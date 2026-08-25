#!/usr/bin/env python3
"""Focused Given-When-Then coverage for sealed S2 route checkpoints."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
import zipfile
from copy import deepcopy
from pathlib import Path
from unittest import mock

import yaml


ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / ".ai/scripts"))

import ai_context_multi_hop_upgrade as MULTI  # noqa: E402
import ai_context_package_apply as APPLY  # noqa: E402
import ai_context_package_validation as PACKAGE_VALIDATION  # noqa: E402
import ai_context_target_provenance as TARGET  # noqa: E402
import ai_context_upgrade_routes as ROUTES  # noqa: E402


def git(root: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=root, check=True, capture_output=True, text=True)


class MultiHopFixture:
    def __init__(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="multi-hop-upgrade-")
        self.root = Path(self.temporary.name)
        self.target = self.root / "target"
        self.target.mkdir()
        git(self.target, "init", "-q")
        git(self.target, "config", "user.name", "Fixture")
        git(self.target, "config", "user.email", "fixture@example.invalid")
        (self.target / "README.md").write_text("fixture\n", encoding="utf-8")
        git(self.target, "add", "README.md")
        git(self.target, "commit", "-qm", "fixture baseline")
        self.matrix_path = self.root / "matrix.yaml"
        self.matrix_raw = b"schema_version: '1.0'\n"
        self.matrix_path.write_bytes(self.matrix_raw)
        self.matrix_root = self.root / "matrix-assets"
        self.matrix_root.mkdir()
        self.matrix_id = "fixture"
        self._real_resolve_matrix_file = ROUTES.resolve_matrix_file
        self.e2e: dict | None = None

    def close(self) -> None:
        self.temporary.cleanup()

    def edge(self, edge_id: str, order: int, from_version: str, to_version: str) -> dict:
        return {
            "edge_id": edge_id,
            "order": order,
            "from_version": from_version,
            "to_version": to_version,
            "artifacts": {},
            "semantic_cutovers": [],
            "validation": {},
        }

    def resolution(self, route_kind: str = "orchestrated-multi-hop") -> dict:
        if self.e2e is not None and route_kind == "orchestrated-multi-hop":
            # Existing focused tests may mock MULTI.ROUTES at its public entry,
            # but their e2e fixture still needs the exact normalized S1 edge
            # shape that a real post-begin re-resolution returns.
            return self._real_resolve_matrix_file(
                self.matrix_path, origin="v0.9.0", target="v0.11.0"
            )
        edges = (
            self.e2e["edges"]
            if self.e2e is not None
            else [
                self.edge("v09-to-v010", 1, "v0.9.0", "v0.10.0"),
                self.edge("v010-to-v011", 2, "v0.10.0", "v0.11.0"),
            ]
        )
        return {
            "route_kind": route_kind,
            "origin": "v0.9.0",
            "target": "v0.11.0",
            "matrix": {
                "sha256": APPLY.sha256_bytes(self.matrix_raw),
                "byte_length": len(self.matrix_raw),
                "matrix_id": self.matrix_id,
                "path": self.matrix_path.as_posix(),
            },
            "selected_route": {"route_id": "fixture-two-hop", "edges": edges},
        }

    @staticmethod
    def _record(path: str, content: bytes, component_id: str) -> dict:
        return {
            "path": path,
            "source_path": path,
            "sha256": APPLY.sha256_bytes(content),
            "size": len(content),
            "mode": "0644",
            "ownership": "framework-managed",
            "install_behavior": "managed",
            "entry_id": "multi-hop-fixture",
            "component_id": component_id,
        }

    @staticmethod
    def _yaml_bytes(value: dict) -> bytes:
        return yaml.safe_dump(value, sort_keys=False).encode("utf-8")

    @staticmethod
    def _compact_json_bytes(value: dict) -> bytes:
        return json.dumps(
            value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
        ).encode("utf-8")

    @staticmethod
    def _operation(identifier: str, kind: str, path: str, component_id: str) -> dict:
        return {
            "id": identifier,
            "kind": kind,
            "path": path,
            "ownership": "framework-managed",
            "component_id": component_id,
            "preconditions": {
                "add": ["destination_absent"],
                "replace": ["current_sha256_equals_previous_release"],
            }[kind],
        }

    @staticmethod
    def _reseal(package_root: Path) -> None:
        entries: list[str] = []
        for path in sorted(
            (
                item
                for item in package_root.rglob("*")
                if item.is_file() and item.relative_to(package_root).as_posix() != "metadata/SHA256SUMS.txt"
            ),
            key=lambda item: item.relative_to(package_root).as_posix().encode("utf-8"),
        ):
            relative = path.relative_to(package_root).as_posix()
            entries.append(f"{APPLY.sha256_bytes(path.read_bytes())}  {relative}\n")
        sums = package_root / "metadata/SHA256SUMS.txt"
        sums.write_text("".join(entries), encoding="utf-8", newline="\n")

    def _make_upgrade_package(
        self,
        name: str,
        *,
        from_version: str,
        to_version: str,
        previous_files: bytes,
        example_content: bytes,
        commit: str,
    ) -> tuple[Path, bytes, dict, dict]:
        """Create a small real schema-2.3 envelope for one child transaction."""
        package_root = self.root / f"package-{name}"
        (package_root / "metadata").mkdir(parents=True)
        (package_root / "payload").mkdir()
        selection = deepcopy(APPLY.DEFAULT_COMPONENT_SELECTION)
        validator_path = ".ai/scripts/validate-ai-context-payload.py"
        validator_content = (ROOT / validator_path).read_bytes().replace(
            b"from pathlib import Path\n",
            b"from pathlib import Path\nsys.path.insert(0, str(Path(__file__).resolve().parent))\n",
            1,
        )
        payload = {
            validator_path: validator_content,
            ".ai/scripts/ai_context_package_validation.py": (
                ROOT / ".ai/scripts/ai_context_package_validation.py"
            ).read_bytes(),
            ".ai/scripts/python-entrypoints.json": (
                json.dumps(
                    {
                        "schema_version": "1.0",
                        "python_floor": "3.11",
                        "governed_requirements": {
                            "PyYAML": {
                                "version": "6.0.3",
                                "import_name": "yaml",
                                "requirements_path": "requirements.txt",
                            }
                        },
                        "entrypoints": [
                            {
                                "path": validator_path,
                                "portable": True,
                                "dependency_profile": ["PyYAML"],
                                "prerequisite_exit_code": 1,
                            },
                            {
                                "path": ".ai/scripts/portable.py",
                                "portable": True,
                                "dependency_profile": [],
                                "prerequisite_exit_code": 1,
                            },
                        ],
                    },
                    ensure_ascii=False,
                    sort_keys=True,
                    separators=(",", ":"),
                ).encode("utf-8")
                + b"\n"
            ),
            ".ai/scripts/portable.py": b"#!/usr/bin/env python3\nimport argparse\nargparse.ArgumentParser().parse_args()\n",
            ".ai/assets/shared/example.md": example_content,
        }
        component_ids = {
            validator_path: "ai-context-lifecycle-core",
            ".ai/scripts/ai_context_package_validation.py": "ai-context-lifecycle-core",
            ".ai/scripts/python-entrypoints.json": "ai-context-lifecycle-core",
            ".ai/scripts/portable.py": "ai-context-lifecycle-core",
            ".ai/assets/shared/example.md": "dotnet-backend",
        }
        records = []
        for path, content in sorted(payload.items(), key=lambda item: item[0].encode("utf-8")):
            destination = package_root / "payload" / path
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(content)
            records.append(self._record(path, content, component_ids[path]))
        package_id = f"fixture-ai-context-{to_version.replace('.', '-') }"
        files_document = {
            "schema_version": "2.0.0",
            "package_id": package_id,
            "files": records,
        }
        files_content = self._yaml_bytes(files_document)
        previous_document = yaml.safe_load(previous_files.decode("utf-8"))
        previous_records = {
            item["path"]: item
            for item in previous_document["files"]
        }
        operations = []
        clean_operations = []
        for index, record in enumerate(records, 1):
            operations.append(
                self._operation(
                    f"hop-{name}-{index:04d}",
                    "replace" if record["path"] in previous_records else "add",
                    record["path"],
                    record["component_id"],
                )
            )
            clean_operations.append(
                self._operation(
                    f"clean-{name}-{index:04d}",
                    "add",
                    record["path"],
                    record["component_id"],
                )
            )
        migration = {
            "schema_version": "3.0.0",
            "package_id": package_id,
            "selection": selection,
            "to": {
                "version": to_version,
                "manifest_sha256": APPLY.sha256_bytes(files_content),
            },
            "clean_install": {"operations": clean_operations},
            "sources": [
                {
                    "version": from_version,
                    "manifest_sha256": APPLY.sha256_bytes(previous_files),
                    "operations": operations,
                }
            ],
            "safety": {
                "dry_run_default": True,
                "clean_worktree_required": True,
                "starting_commit_required": True,
                "abort_on_unacknowledged_reconciliation": True,
            },
        }
        migration_content = self._yaml_bytes(migration)
        install_content = (
            b"# Install\n\npython -m pip install -r requirements.txt\n\n"
            b"python payload/.ai/scripts/validate-ai-context-payload.py --package-root .\n"
        )
        proof = {
            "schema_version": "package-selected-input/v1",
            "source_inputs": [
                {"path": ".ai/distribution/profiles/dotnet-backend.yaml", "sha256": APPLY.sha256_bytes(b"profile\n")},
                {"path": ".ai/distribution/templates/INSTALL.md", "sha256": APPLY.sha256_bytes(install_content)},
                {"path": ".ai/distribution/templates/requirements.txt", "sha256": APPLY.sha256_bytes(b"PyYAML==6.0.3\n")},
                {"path": f".dev/releases/v{to_version}/release.yaml", "sha256": APPLY.sha256_bytes(b"release\n")},
            ],
            "payload": [
                {key: record[key] for key in ("path", "sha256", "mode", "ownership", "install_behavior", "component_id")}
                for record in records
            ],
            "migration_sources": [{"version": from_version, "manifest_sha256": APPLY.sha256_bytes(previous_files)}],
        }
        proof_content = self._compact_json_bytes(proof)
        validation = {
            "schema_version": "package-validation/v1",
            "package_id": package_id,
            "authority": {
                "kind": "incoming-candidate",
                "validator": {
                    "path": validator_path,
                    "sha256": APPLY.sha256_bytes(payload[validator_path]),
                    "argv": ["python", "payload/.ai/scripts/validate-ai-context-payload.py", "--package-root", "."],
                },
            },
            "selected_input_proof": {"path": "metadata/selected-inputs.json", "sha256": APPLY.sha256_bytes(proof_content)},
            "source_only_tests": {
                "classification": "source-only",
                "contributes_to_portable_success": False,
                "patterns": [".ai/scripts/tests/**", ".ai/assets/skills/**/scripts/tests/**"],
            },
            "integrity_policy": {
                "path_case": "casefold-unique",
                "payload_text": "all",
                "text": {"encoding": "utf-8", "line_endings": "lf-only", "terminal_lf": "exactly-one"},
                "modes": {"allowed": ["0644", "0755"]},
            },
        }
        validation_content = self._compact_json_bytes(validation)
        payload_fingerprint = APPLY.sha256_bytes(
            "".join(f"{record['sha256']}  {record['path']}\n" for record in records).encode("utf-8")
        )
        source = {
            "repository": "https://example.invalid/framework",
            "release_id": f"REL-v{to_version}",
            "version": f"v{to_version}",
            "tag": f"v{to_version}",
            "commit": commit,
        }
        package = {
            "schema_version": "2.3.0",
            "package_id": package_id,
            "profile_id": "dotnet-backend",
            "version": to_version,
            "release_id": f"REL-v{to_version}",
            "selection": selection,
            "user_view": {
                "schema_version": "1.0.0",
                "classifications": {
                    "markdown_local_links": "required-local-navigation",
                    "markdown_anchors": "required-local-anchor",
                    "component_cross_links": "navigation-only-not-activation",
                    "fenced_code": "non-actionable-example-unless-command",
                    "inline_code": "non-actionable-reference-unless-command",
                    "templates_and_placeholders": "non-actionable-template",
                    "external_urls": "external-not-validated",
                    "actionable_local_commands": "required-local-target",
                },
                "reference_integrity": {
                    "text_extensions": [".md", ".yaml", ".py"],
                    "forbidden_source_lifecycle_patterns": [".dev/releases/v*/**"],
                    "target_owned_reference_patterns": list(
                        PACKAGE_VALIDATION.TARGET_OWNED_REFERENCE_PATTERNS
                    ),
                },
                "components": [
                    {"component_id": "software-development-core", "classification": "mandatory-core", "required": True, "requires": []},
                    {"component_id": "ai-context-lifecycle-core", "classification": "mandatory-core", "required": True, "requires": []},
                    {"component_id": "dotnet-backend", "classification": "technology-profile", "required": False, "requires": ["software-development-core"]},
                    {"component_id": "repo-backlog", "classification": "optional-provider", "required": False, "requires": ["software-development-core"]},
                ],
                "supported_selections": [{"selection_id": "dotnet-backend-default", "components": ["software-development-core", "ai-context-lifecycle-core", "dotnet-backend"]}],
                "capabilities": [],
            },
            "source": {
                "repository": source["repository"],
                "ref": commit,
                "commit": commit,
                "tree": "f" * 40,
            },
            "created_at": "2026-08-20T00:00:00Z",
            "source_date_epoch": 1787184000,
            "identity": {
                "schema_version": "1.0.0",
                "selected_input_fingerprint": APPLY.sha256_bytes(proof_content),
                "payload_fingerprint": payload_fingerprint,
                "files_manifest_digest": APPLY.sha256_bytes(files_content),
                "migration_digest": APPLY.sha256_bytes(migration_content),
            },
            "payload": {"root": "payload", "file_count": len(records), "sha256": payload_fingerprint},
            "compatibility": {"minimum_governed_source": "0.1.0", "breaking_changes": False, "automatic_upgrade_sources": [from_version]},
            "validation": {
                "schema_version": "package-validation/v1",
                "manifest": "metadata/validation.json",
                "manifest_sha256": APPLY.sha256_bytes(validation_content),
                "selected_inputs": "metadata/selected-inputs.json",
                "selected_inputs_sha256": APPLY.sha256_bytes(proof_content),
            },
        }
        (package_root / "INSTALL.md").write_bytes(install_content)
        (package_root / "requirements.txt").write_text("PyYAML==6.0.3\n", encoding="utf-8", newline="\n")
        (package_root / "metadata/package.yaml").write_bytes(self._yaml_bytes(package))
        (package_root / "metadata/files.yaml").write_bytes(files_content)
        (package_root / "metadata/migration.yaml").write_bytes(migration_content)
        (package_root / "metadata/validation.json").write_bytes(validation_content)
        (package_root / "metadata/selected-inputs.json").write_bytes(proof_content)
        self._reseal(package_root)
        return package_root, files_content, selection, source

    def _write_edge_assets(
        self,
        hop_index: int,
        from_version: str,
        to_version: str,
        package_root: Path,
    ) -> dict:
        """Archive one package and retain all S1 edge asset identities."""
        package = yaml.safe_load(
            (package_root / "metadata/package.yaml").read_text(encoding="utf-8")
        )
        validation_raw = (package_root / "metadata/validation.json").read_bytes()
        validation = json.loads(validation_raw.decode("utf-8"))
        package_identity = {
            "package_id": package["package_id"],
            "release_id": package["release_id"],
            "payload_fingerprint": package["identity"]["payload_fingerprint"],
        }
        package_dir = self.matrix_root / "packages"
        manifest_dir = self.matrix_root / "manifests"
        validator_dir = self.matrix_root / "validators"
        output_dir = self.matrix_root / "outputs"
        for path in (package_dir, manifest_dir, validator_dir, output_dir):
            path.mkdir(exist_ok=True)
        archive = package_dir / f"hop-{hop_index}.zip"
        envelope = f"fixture-hop-{hop_index}"
        with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED) as handle:
            for source in sorted(
                (item for item in package_root.rglob("*") if item.is_file()),
                key=lambda item: item.relative_to(package_root).as_posix().encode("utf-8"),
            ):
                info = zipfile.ZipInfo(
                    f"{envelope}/{source.relative_to(package_root).as_posix()}",
                    date_time=(2026, 8, 20, 0, 0, 0),
                )
                info.compress_type = zipfile.ZIP_DEFLATED
                info.external_attr = 0o100644 << 16
                handle.writestr(info, source.read_bytes())
        checksum = package_dir / f"hop-{hop_index}.sha256"
        checksum.write_text(
            f"{APPLY.sha256_bytes(archive.read_bytes())}  {archive.name}\n",
            encoding="utf-8",
            newline="\n",
        )
        manifest = manifest_dir / f"hop-{hop_index}.migration.yaml"
        manifest.write_bytes((package_root / "metadata/migration.yaml").read_bytes())
        expected_output = f"route-validator-{hop_index}\n".encode("utf-8")
        validator = validator_dir / f"hop-{hop_index}.py"
        validator.write_text(
            "import sys\nsys.stdout.buffer.write(" + repr(expected_output) + ")\n",
            encoding="utf-8",
            newline="\n",
        )
        output = output_dir / f"hop-{hop_index}.stdout"
        output.write_bytes(expected_output)

        def asset(asset_id: str, path: Path) -> dict:
            return {
                "asset_id": asset_id,
                "path": path.relative_to(self.matrix_root).as_posix(),
                "sha256": APPLY.sha256_bytes(path.read_bytes()),
            }

        edge = self.edge(
            f"v{from_version.replace('.', '')}-to-v{to_version.replace('.', '')}",
            hop_index + 1,
            f"v{from_version}",
            f"v{to_version}",
        )
        edge["artifacts"] = {
            "archive": asset(f"hop-{hop_index}-archive", archive),
            "checksum": asset(f"hop-{hop_index}-checksum", checksum),
            "manifest": asset(f"hop-{hop_index}-manifest", manifest),
            "validator": asset(f"hop-{hop_index}-validator", validator),
        }
        edge["package_identity"] = package_identity
        edge["semantic_cutovers"] = [{"cutover_id": "fixture-cutover", "state": "passed"}]
        validator_argv = [sys.executable, validator.relative_to(self.matrix_root).as_posix()]
        edge["validation"] = {
            "state": "passed",
            "validator_argv": validator_argv,
            "output": asset(f"hop-{hop_index}-output", output),
        }
        report = {
            "schema_version": ROUTES.EDGE_VALIDATION_RECEIPT_SCHEMA_VERSION,
            "edge_id": edge["edge_id"],
            "from_version": edge["from_version"],
            "to_version": edge["to_version"],
            "artifacts": deepcopy(edge["artifacts"]),
            "validator_argv": validator_argv,
            "semantic_cutovers": [
                {"cutover_id": "fixture-cutover", "required": True, "state": "passed"}
            ],
            "portable_validation": {
                "schema_version": ROUTES.PORTABLE_VALIDATION_SCHEMA_VERSION,
                "authority": {
                    "kind": "incoming-candidate",
                    "manifest": {
                        "path": "metadata/validation.json",
                        "sha256": APPLY.sha256_bytes(validation_raw),
                    },
                    "validator": deepcopy(validation["authority"]["validator"]),
                },
                "package_identity": deepcopy(package_identity),
                "execution": {
                    "outcome": "passed",
                    "exit_code": 0,
                    "output_sha256": APPLY.sha256_bytes(
                        f"incoming-validation-{hop_index}\n".encode("utf-8")
                    ),
                },
            },
            "outcome": "passed",
            "exit_code": 0,
            "output_sha256": edge["validation"]["output"]["sha256"],
        }
        report_path = self.matrix_root / "reports" / f"hop-{hop_index}.json"
        report_path.parent.mkdir(exist_ok=True)
        report_path.write_bytes(ROUTES.canonical_json(report).encode("utf-8"))
        edge["validation"]["report"] = asset(f"hop-{hop_index}-report", report_path)
        return edge

    def _matrix_asset(self, relative: str, content: bytes) -> dict:
        path = self.matrix_root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
        return {
            "asset_id": relative.replace("/", "-"),
            "path": relative,
            "sha256": APPLY.sha256_bytes(content),
        }

    def _write_e2e_matrix(self) -> None:
        assert self.e2e is not None
        self.matrix_id = "fixture-v0.11.0-supported-upgrades"
        matrix = {
            "schema_version": ROUTES.SCHEMA_VERSION,
            "matrix_id": self.matrix_id,
            "target": {
                "version": "v0.11.0",
                "release_id": "REL-v0.11.0",
                "commit": "b" * 40,
                "manifest": self._matrix_asset("route-metadata/target.yaml", b"v0.11 target\n"),
                "package_identity": deepcopy(
                    self.e2e["edges"][-1]["package_identity"]
                ),
            },
            "retained_origins": [
                {
                    "role": "immediate-predecessor",
                    "version": "v0.10.0",
                    "release_id": "REL-v0.10.0",
                    "commit": "a" * 40,
                    "manifest": self._matrix_asset("route-metadata/v0.10.yaml", b"v0.10 origin\n"),
                },
                {
                    "role": "v0.9.0",
                    "version": "v0.9.0",
                    "release_id": "REL-v0.9.0",
                    "commit": "c" * 40,
                    "manifest": self._matrix_asset("route-metadata/v0.9.yaml", b"v0.9 origin\n"),
                },
                {
                    "role": "v0.6.0",
                    "version": "v0.6.0",
                    "release_id": "REL-v0.6.0",
                    "commit": "d" * 40,
                    "manifest": self._matrix_asset("route-metadata/v0.6.yaml", b"v0.6 origin\n"),
                },
            ],
            "semantic_cutovers": [
                {
                    "cutover_id": "fixture-cutover",
                    "required": True,
                    "description": "Fixture route requires the durable cutover.",
                }
            ],
            "routes": [
                {
                    "route_id": "fixture-two-hop",
                    "origin": "v0.9.0",
                    "target": "v0.11.0",
                    "edges": deepcopy(self.e2e["edges"]),
                }
            ],
            "deprecations": [],
        }
        self.matrix_path = self.matrix_root / "route-matrix.yaml"
        self.matrix_raw = yaml.safe_dump(matrix, sort_keys=True).encode("utf-8")
        self.matrix_path.write_bytes(self.matrix_raw)

    def _reseal_e2e_route_evidence(self) -> None:
        """Rebind modified selected assets into their S1 receipts and matrix."""
        assert self.e2e is not None
        for edge in self.e2e["edges"]:
            validation = edge["validation"]
            report_identity = validation["report"]
            report_path = self.matrix_root / report_identity["path"]
            report = json.loads(report_path.read_text(encoding="utf-8"))
            report["artifacts"] = deepcopy(edge["artifacts"])
            report["validator_argv"] = deepcopy(validation["validator_argv"])
            report["output_sha256"] = validation["output"]["sha256"]
            report_raw = ROUTES.canonical_json(report).encode("utf-8")
            report_path.write_bytes(report_raw)
            report_identity["sha256"] = APPLY.sha256_bytes(report_raw)
        self._write_e2e_matrix()

    def prepare_e2e(self) -> dict:
        """Seed an initialized v0.9 target plus two real package route edges."""
        selection = deepcopy(APPLY.DEFAULT_COMPONENT_SELECTION)
        previous_content = b"# fixture v0.9\n"
        (self.target / ".ai/assets/shared").mkdir(parents=True)
        (self.target / ".ai/assets/shared/example.md").write_bytes(previous_content)
        (self.target / ".dev").mkdir(exist_ok=True)
        (self.target / ".dev/project-config.yaml").write_bytes(
            self._yaml_bytes(
                {"validation": {"routine": {"argv": [sys.executable, "-c", "print('target validation')"]}}}
            )
        )
        git(self.target, "add", "-A")
        git(self.target, "commit", "-qm", "fixture initialized target bytes")
        initial_source = {
            "repository": "https://example.invalid/framework",
            "release_id": "REL-v0.9.0",
            "version": "v0.9.0",
            "tag": "v0.9.0",
            "commit": "c" * 40,
        }
        initialized = TARGET.initialize_context(
            self.target, initial_source, selection, "2026-08-20T10:00:00+08:00"
        )
        if initialized.get("status") != "initialized":
            raise AssertionError(f"fixture authority initialization failed: {initialized}")
        git(self.target, "add", ".dev/ai-context")
        git(self.target, "commit", "-qm", "fixture initialized authority")
        previous_document = {
            "schema_version": "2.0.0",
            "package_id": "fixture-ai-context-0.9.0",
            "files": [self._record(".ai/assets/shared/example.md", previous_content, "dotnet-backend")],
        }
        initial_files = self.root / "previous-v0.9-files.yaml"
        initial_files.write_bytes(self._yaml_bytes(previous_document))
        package0, files0, _, source0 = self._make_upgrade_package(
            "0", from_version="0.9.0", to_version="0.10.0",
            previous_files=initial_files.read_bytes(),
            example_content=b"# fixture v0.10\n", commit="a" * 40,
        )
        package1, _files1, _, source1 = self._make_upgrade_package(
            "1", from_version="0.10.0", to_version="0.11.0",
            previous_files=files0,
            example_content=b"# fixture v0.11\n", commit="b" * 40,
        )
        self.e2e = {
            "edges": [
                self._write_edge_assets(0, "0.9.0", "0.10.0", package0),
                self._write_edge_assets(1, "0.10.0", "0.11.0", package1),
            ],
            "initial_files": initial_files,
            "initial_source": initial_source,
            "sources": [source0, source1],
            "selection": selection,
        }
        self._write_e2e_matrix()
        return self.e2e

    @staticmethod
    def candidate_authorities(
        source: dict, previous_source: dict, selection: dict, from_version: str, to_version: str
    ) -> tuple[dict, dict]:
        provenance, ledger = TARGET.build_initialization_documents(
            source, selection, "2026-08-20T12:00:00+08:00"
        )
        provenance["previous_source"] = deepcopy(previous_source)
        provenance["installation"]["last_upgraded_at"] = "2026-08-20T12:00:00+08:00"
        provenance["last_migration"] = {
            "status": "completed",
            "from_version": f"v{from_version}",
            "to_version": f"v{to_version}",
            "completed_at": "2026-08-20T12:00:00+08:00",
            "evidence": "tests/multi-hop-upgrade.md",
        }
        return provenance, ledger

    @staticmethod
    def remediation_decision(plan: dict, provenance: dict, ledger: dict) -> dict:
        packet = APPLY.build_upgrade_remediation_packet(plan)
        proposal = packet["automatic_proposal"]
        if proposal["unresolved_operation_ids"] or proposal["reconciliation_ids"]:
            raise AssertionError(f"fixture package requires unexpected reconciliation: {proposal}")
        return {
            "schema_version": "upgrade-remediation-decision/v1",
            "packet_sha256": packet["canonical_digest"],
            "plan_sha256": plan["plan_sha256"],
            "transaction_id": plan["plan_sha256"],
            "status": "approved",
            "owner": "fixture-owner",
            "decided_at": "2026-08-20T12:00:00+08:00",
            "evidence": "tests/multi-hop-upgrade.md",
            "reason": "exercise exact owner decision binding",
            "accepted_operation_ids": proposal["apply_operation_ids"],
            "reconciliation_ids": proposal["reconciliation_ids"],
            "policy_adoptions": None,
            "candidate_authority": {
                "provenance_sha256": TARGET.canonical_json_digest(provenance),
                "customizations_sha256": TARGET.canonical_json_digest(ledger),
            },
        }

    @staticmethod
    def rejected_remediation_decision(plan: dict) -> dict:
        packet = APPLY.build_upgrade_remediation_packet(plan)
        return {
            "schema_version": "upgrade-remediation-decision/v1",
            "packet_sha256": packet["canonical_digest"],
            "plan_sha256": plan["plan_sha256"],
            "transaction_id": plan["plan_sha256"],
            "status": "rejected",
            "owner": "fixture-owner",
            "decided_at": "2026-08-20T12:00:00+08:00",
            "evidence": "tests/multi-hop-upgrade.md",
            "reason": "exercise explicit owner rejection",
            "accepted_operation_ids": [],
            "reconciliation_ids": [],
            "policy_adoptions": None,
            "candidate_authority": None,
        }

    def supplied_target_validation_receipt(self, plan: dict) -> Path:
        transaction = APPLY.transaction_root(self.target, plan["plan_sha256"])
        packet = json.loads((transaction / APPLY.REMEDIATION_PACKET_PATH).read_text(encoding="utf-8"))
        journal = yaml.safe_load((transaction / "journal.yaml").read_text(encoding="utf-8"))
        profile = packet["target_validation_profile"]
        execution = subprocess.run(
            profile["argv"], cwd=self.target, check=False, capture_output=True
        )
        if execution.returncode != 0 or execution.stderr:
            raise AssertionError(f"fixture target validation failed: {execution.stderr!r}")
        output_path = transaction / APPLY.TARGET_VALIDATION_OUTPUT_PATH
        output_path.write_bytes(execution.stdout)
        pending = self.target / APPLY.PENDING_RECEIPT_PATH
        supplied = {
            "schema_version": "target-validation-receipt/v1",
            "transaction_id": plan["plan_sha256"],
            "plan_sha256": plan["plan_sha256"],
            "packet_sha256": packet["canonical_digest"],
            "decision_sha256": journal["remediation_decision_sha256"],
            "target": {
                "root": packet["target"]["root"],
                "starting_commit": packet["target"]["starting_commit"],
                "observed_prestate_sha256": packet["target"]["observed_prestate_sha256"],
            },
            "target_validation_profile": profile,
            "target_validation_profile_digest": packet["target_validation_profile_digest"],
            "pending_receipt": {"path": APPLY.PENDING_RECEIPT_PATH, "sha256": APPLY.sha256_bytes(pending.read_bytes())},
            "execution": {
                "argv": profile["argv"],
                "outcome": "passed",
                "exit_code": execution.returncode,
                "started_at": "2026-08-20T12:00:00+08:00",
                "completed_at": "2026-08-20T12:00:01+08:00",
                "output_sha256": APPLY.sha256_bytes(execution.stdout),
                "evidence": f".git/ai-context-package-apply/{plan['plan_sha256']}/{APPLY.TARGET_VALIDATION_OUTPUT_PATH}",
            },
        }
        path = self.root / f"target-validation-{plan['plan_sha256']}.json"
        path.write_bytes(APPLY.canonical_json_bytes(supplied))
        return path


class MultiHopUpgradeGwtTests(unittest.TestCase):
    def setUp(self) -> None:
        self.fixture = MultiHopFixture()

    def tearDown(self) -> None:
        self.fixture.close()

    def _begin(self) -> dict:
        with mock.patch.object(
            MULTI.ROUTES,
            "resolve_matrix_file",
            return_value=self.fixture.resolution(),
        ):
            return MULTI.begin_multi_hop_upgrade(
                self.fixture.target,
                self.fixture.matrix_path,
                origin="v0.9.0",
                target_version="v0.11.0",
            )

    def _apply_first_hop_without_mock(
        self,
    ) -> tuple[dict, dict, dict, dict, dict]:
        """Drive one real source-resolver child through its pre-receipt state."""
        e2e = self.fixture.prepare_e2e()
        begun = MULTI.begin_multi_hop_upgrade(
            self.fixture.target,
            self.fixture.matrix_path,
            origin="v0.9.0",
            target_version="v0.11.0",
        )
        first = MULTI.prepare_next_hop(
            self.fixture.target,
            begun["route_transaction_id"],
            matrix_root=self.fixture.matrix_root,
            initial_previous_files_path=e2e["initial_files"],
            initial_previous_version="0.9.0",
        )
        provenance, ledger = self.fixture.candidate_authorities(
            e2e["sources"][0],
            e2e["initial_source"],
            e2e["selection"],
            "0.9.0",
            "0.10.0",
        )
        applied = MULTI.apply_prepared_hop(
            self.fixture.target,
            begun["route_transaction_id"],
            self.fixture.remediation_decision(first["plan"], provenance, ledger),
        )
        return begun, first, applied, provenance, ledger

    def _forge_bound_validator_evidence(self, begun: dict) -> tuple[Path, dict, dict]:
        """Change every mutable promoted binding while leaving it self-consistent."""
        route_root, intent, journal = MULTI._load_route(
            self.fixture.target, begun["route_transaction_id"]
        )
        active = journal["active_hop"]
        assert isinstance(active, dict)
        hop_root = route_root / "hops" / "0000"
        record_path = hop_root / "validator-execution.json"
        stdout_path = hop_root / "validator.stdout.log"
        validator_path = hop_root / "validator.asset"
        evidence_path = hop_root / "evidence.json"
        record = json.loads(record_path.read_text(encoding="utf-8"))
        evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
        forged_validator = b"forged retained validator asset\n"
        forged_stdout = b"forged validator output\n"
        APPLY.atomic_write_bytes(validator_path, forged_validator)
        APPLY.atomic_write_bytes(stdout_path, forged_stdout)
        record["validator_argv"] = ["forged-validator", "--edge", "forged"]
        record["validator_sha256"] = APPLY.sha256_bytes(forged_validator)
        record["expected_output_sha256"] = APPLY.sha256_bytes(forged_stdout)
        record["stdout_sha256"] = APPLY.sha256_bytes(forged_stdout)
        record_raw = APPLY.canonical_json_bytes(record)
        APPLY.atomic_write_bytes(record_path, record_raw)
        execution = deepcopy(active["validator_execution"])
        execution["record_sha256"] = APPLY.sha256_bytes(record_raw)
        execution["stdout_sha256"] = APPLY.sha256_bytes(forged_stdout)
        package = deepcopy(active["package"])
        package["validator_artifact_sha256"] = APPLY.sha256_bytes(forged_validator)
        evidence["package"] = deepcopy(package)
        evidence["validator_execution"] = deepcopy(execution)
        APPLY.atomic_write_bytes(evidence_path, APPLY.canonical_json_bytes(evidence))
        active["package"] = package
        active["validator_execution"] = execution
        journal["active_hop"] = active
        MULTI._persist_route_journal(route_root, intent, journal)
        return route_root, intent, journal

    def _route_mutation_snapshot(self, route_root: Path) -> dict:
        """Capture the boundary that rejected route actions must not advance."""
        checkpoints = route_root / "checkpoints"
        checkpoint_bytes = {
            path.relative_to(route_root).as_posix(): path.read_bytes()
            for path in sorted(checkpoints.rglob("*"))
            if path.is_file()
        }
        authority_bytes: dict[str, bytes | None] = {}
        for relative in (
            ".dev/ai-context/provenance.yaml",
            ".dev/ai-context/customizations.yaml",
        ):
            path = self.fixture.target / relative
            authority_bytes[relative] = path.read_bytes() if path.is_file() else None
        return {
            "journal": (route_root / "journal.yaml").read_bytes(),
            "checkpoints": checkpoint_bytes,
            "authority": authority_bytes,
            "target_surface": APPLY.route_checkpoint_surface(self.fixture.target),
        }

    def _checkpoint_first_hop(self, begun: dict) -> tuple[Path, dict, dict]:
        route_root, intent, journal = MULTI._load_route(
            self.fixture.target, begun["route_transaction_id"]
        )
        (self.fixture.target / ".ai" / "first-hop.md").parent.mkdir(parents=True)
        (self.fixture.target / ".ai" / "first-hop.md").write_text("first\n", encoding="utf-8")
        surface = APPLY.route_checkpoint_surface(self.fixture.target)
        checkpoint_unsigned = {
            "schema_version": APPLY.MULTI_HOP_ROUTE_CHECKPOINT_SCHEMA_VERSION,
            "route_transaction_id": begun["route_transaction_id"],
            "route_intent_sha256": begun["route_intent_sha256"],
            "checkpoint_index": 0,
            "predecessor_checkpoint_sha256": None,
            "edge": intent["route"]["edges"][0],
            "package": {},
            "child_transaction": {},
            "pending_receipt": {},
            "authority": {},
            "target_surface": {
                "starting_commit": intent["target_starting_commit"],
                "paths": surface,
            },
        }
        checkpoint = {
            **checkpoint_unsigned,
            "digest": APPLY.canonical_digest(checkpoint_unsigned),
        }
        checkpoint_path = route_root / "checkpoints" / "0000.json"
        APPLY.atomic_write_bytes(checkpoint_path, APPLY.canonical_json_bytes(checkpoint))
        checkpoint_sha = APPLY.sha256_bytes(checkpoint_path.read_bytes())
        journal.update(
            {
                "state": "checkpointed",
                "next_hop_index": 1,
                "last_checkpoint_index": 0,
                "last_checkpoint_sha256": checkpoint_sha,
                "active_hop": None,
            }
        )
        APPLY.atomic_write_yaml(route_root / "journal.yaml", journal)
        return route_root, intent, journal

    def _finalize_real_first_hop(self) -> tuple[dict, dict, dict, Path, dict, dict]:
        """Produce a genuine sealed checkpoint for targeted retained-evidence probes."""
        e2e = self.fixture.prepare_e2e()
        with mock.patch.object(
            MULTI.ROUTES,
            "resolve_matrix_file",
            side_effect=lambda *_args, **_kwargs: self.fixture.resolution(),
        ):
            begun = MULTI.begin_multi_hop_upgrade(
                self.fixture.target,
                self.fixture.matrix_path,
                origin="v0.9.0",
                target_version="v0.11.0",
            )
            first = MULTI.prepare_next_hop(
                self.fixture.target,
                begun["route_transaction_id"],
                matrix_root=self.fixture.matrix_root,
                initial_previous_files_path=e2e["initial_files"],
                initial_previous_version="0.9.0",
            )
            provenance, ledger = self.fixture.candidate_authorities(
                e2e["sources"][0],
                e2e["initial_source"],
                e2e["selection"],
                "0.9.0",
                "0.10.0",
            )
            applied = MULTI.apply_prepared_hop(
                self.fixture.target,
                begun["route_transaction_id"],
                self.fixture.remediation_decision(first["plan"], provenance, ledger),
            )
            MULTI.record_hop_target_validation(
                self.fixture.target,
                begun["route_transaction_id"],
                self.fixture.supplied_target_validation_receipt(first["plan"]),
            )
            final = MULTI.finalize_hop(
                self.fixture.target,
                begun["route_transaction_id"],
                provenance,
                ledger,
            )
        self.assertEqual(0, final["checkpoint_index"])
        self.assertFalse(final["completed"])
        route_root, intent, journal = MULTI._load_route(
            self.fixture.target, begun["route_transaction_id"]
        )
        self.assertEqual("checkpointed", journal["state"])
        return begun, first, applied, route_root, intent, journal

    def _rejected_unbound_child_crash(self) -> tuple[dict, Path, dict, dict, Path]:
        """Recreate the delete-proposal-before-outer-clear crash boundary."""
        e2e = self.fixture.prepare_e2e()
        with mock.patch.object(
            MULTI.ROUTES,
            "resolve_matrix_file",
            side_effect=lambda *_args, **_kwargs: self.fixture.resolution(),
        ):
            begun = MULTI.begin_multi_hop_upgrade(
                self.fixture.target,
                self.fixture.matrix_path,
                origin="v0.9.0",
                target_version="v0.11.0",
            )
            first = MULTI.prepare_next_hop(
                self.fixture.target,
                begun["route_transaction_id"],
                matrix_root=self.fixture.matrix_root,
                initial_previous_files_path=e2e["initial_files"],
                initial_previous_version="0.9.0",
            )
            route_root, intent, before = MULTI._load_route(
                self.fixture.target, begun["route_transaction_id"]
            )
            active = deepcopy(before["active_hop"])
            assert isinstance(active, dict)
            result = MULTI.apply_prepared_hop(
                self.fixture.target,
                begun["route_transaction_id"],
                self.fixture.rejected_remediation_decision(first["plan"]),
            )
        self.assertEqual("owner-rejected-before-target-mutation", result["outcome"])
        proposal_path = route_root / "hops" / "0000" / "preparation.json"
        self.assertFalse(proposal_path.exists())
        before["state"] = "applying"
        before["active_hop"] = active
        MULTI._persist_route_journal(route_root, intent, before)
        child_root = APPLY.transaction_root(self.fixture.target, first["plan"]["plan_sha256"])
        self.assertTrue(child_root.is_dir())
        return begun, route_root, intent, before, child_root

    def test_gwt_001_given_sealed_initial_context_when_first_hop_is_planned_then_exact_route_context_is_admitted(self) -> None:
        begun = self._begin()
        route_root, intent, journal = MULTI._load_route(
            self.fixture.target, begun["route_transaction_id"]
        )
        initial_context = MULTI._next_context(route_root, intent, journal)
        self.assertEqual(
            APPLY.MULTI_HOP_INITIAL_ROUTE_CONTEXT_SCHEMA_VERSION,
            initial_context["schema_version"],
        )
        self.assertEqual(0, initial_context["next_hop_index"])
        self.assertEqual(
            initial_context,
            APPLY.verify_multi_hop_checkpoint_for_planning(
                self.fixture.target, initial_context
            ),
        )

    def test_gwt_002_given_canonical_but_incomplete_checkpoint_when_later_hop_is_admitted_then_it_fails_closed(self) -> None:
        begun = self._begin()
        route_root, intent, journal = self._checkpoint_first_hop(begun)
        context = MULTI._next_context(route_root, intent, journal)
        assert context is not None

        with self.assertRaisesRegex(APPLY.ApplyError, "finalized checkpoint evidence is invalid"):
            APPLY.verify_multi_hop_checkpoint_for_planning(self.fixture.target, context)

        with self.assertRaisesRegex(APPLY.ApplyError, "finalized checkpoint evidence is invalid"):
            MULTI._previous_files_for_hop(
                self.fixture.target,
                route_root,
                journal,
                initial_previous_files_path=None,
                initial_previous_version=None,
                context=context,
            )

    def test_gwt_003_given_direct_or_ambiguous_result_when_begin_requested_then_no_route_transaction_is_created(self) -> None:
        with mock.patch.object(
            MULTI.ROUTES,
            "resolve_matrix_file",
            return_value=self.fixture.resolution("direct"),
        ):
            with self.assertRaisesRegex(MULTI.MultiHopUpgradeError, "orchestrated-multi-hop"):
                MULTI.begin_multi_hop_upgrade(
                    self.fixture.target,
                    self.fixture.matrix_path,
                    origin="v0.9.0",
                    target_version="v0.11.0",
                )
        route_base = APPLY.git_admin_multi_hop_route_base(self.fixture.target)
        self.assertFalse(route_base.exists())

    def test_gwt_004_given_standard_sha256sum_separators_when_archive_is_bound_then_space_and_binary_forms_are_accepted(self) -> None:
        archive = b"sealed-archive-bytes"
        digest = APPLY.sha256_bytes(archive)
        self.assertTrue(
            MULTI._checksum_binds_archive(
                f"{digest}  package.zip\n".encode("utf-8"), archive, "package.zip"
            )
        )
        self.assertTrue(
            MULTI._checksum_binds_archive(
                f"{digest} *package.zip\n".encode("utf-8"), archive, "package.zip"
            )
        )
        self.assertFalse(
            MULTI._checksum_binds_archive(
                f"{digest} *other.zip\n".encode("utf-8"), archive, "package.zip"
            )
        )

    def test_gwt_005_given_checkpoint_written_and_pending_already_cleared_when_resume_promotes_then_exact_checkpoint_is_reused(self) -> None:
        begun = self._begin()
        route_root, intent, journal = MULTI._load_route(
            self.fixture.target, begun["route_transaction_id"]
        )
        pending = b"sealed pending receipt\n"
        pending_sha = APPLY.sha256_bytes(pending)
        transaction_id = "a" * 64
        active = {
            "hop_index": 0,
            "edge": intent["route"]["edges"][0],
            "package": {},
            "validator_execution": {},
            "plan_sha256": transaction_id,
            "proposal_plan_sha256": transaction_id,
            "child_transaction_id": transaction_id,
            "pending_receipt_sha256": pending_sha,
            "child_evidence_path": f"ai-context-package-apply/{transaction_id}",
        }
        checkpoint_unsigned = {
            "schema_version": APPLY.MULTI_HOP_ROUTE_CHECKPOINT_SCHEMA_VERSION,
            "route_transaction_id": begun["route_transaction_id"],
            "route_intent_sha256": begun["route_intent_sha256"],
            "checkpoint_index": 0,
            "predecessor_checkpoint_sha256": None,
            "edge": intent["route"]["edges"][0],
            "package": {},
            "child_transaction": {"transaction_id": transaction_id},
            "pending_receipt": {
                "path": APPLY.PENDING_RECEIPT_PATH,
                "sha256": pending_sha,
                "archive_path": "checkpoints/0000.pending-receipt.yaml",
            },
            "authority": {},
            "target_surface": {"starting_commit": intent["target_starting_commit"], "paths": {}},
        }
        checkpoint = {**checkpoint_unsigned, "digest": APPLY.canonical_digest(checkpoint_unsigned)}
        checkpoint_path = route_root / "checkpoints" / "0000.json"
        APPLY.atomic_write_bytes(checkpoint_path, APPLY.canonical_json_bytes(checkpoint))
        checkpoint_sha = APPLY.sha256_bytes(checkpoint_path.read_bytes())
        APPLY.atomic_write_bytes(route_root / "checkpoints" / "0000.pending-receipt.yaml", pending)
        journal.update({"state": "checkpointing", "active_hop": active})
        APPLY.atomic_write_yaml(route_root / "journal.yaml", journal)

        with mock.patch.object(APPLY, "clear_checkpointed_pending_receipt_locked") as clear:
            result = MULTI._checkpoint_hop(self.fixture.target, route_root, intent, journal)

        self.assertEqual(0, result["checkpoint_index"])
        self.assertEqual("checkpointed", journal["state"])
        self.assertEqual(1, journal["next_hop_index"])
        self.assertIsNone(journal["active_hop"])
        clear.assert_called_once()
        self.assertEqual(checkpoint_sha, journal["last_checkpoint_sha256"])

    def test_gwt_006_given_active_route_journal_when_validator_reads_it_then_invalid_active_shape_is_reported_not_crashed(self) -> None:
        e2e = self.fixture.prepare_e2e()
        with mock.patch.object(
            MULTI.ROUTES,
            "resolve_matrix_file",
            side_effect=lambda *_args, **_kwargs: self.fixture.resolution(),
        ):
            begun = MULTI.begin_multi_hop_upgrade(
                self.fixture.target,
                self.fixture.matrix_path,
                origin="v0.9.0",
                target_version="v0.11.0",
            )
            MULTI.prepare_next_hop(
                self.fixture.target,
                begun["route_transaction_id"],
                matrix_root=self.fixture.matrix_root,
                initial_previous_files_path=e2e["initial_files"],
                initial_previous_version="0.9.0",
            )
        route_root, _intent, journal = MULTI._load_route(
            self.fixture.target, begun["route_transaction_id"]
        )
        valid_errors: list[str] = []
        TARGET.validate_multi_hop_route_transactions(self.fixture.target, valid_errors)
        self.assertEqual([], valid_errors)

        original_active = deepcopy(journal["active_hop"])
        assert isinstance(original_active, dict)
        journal["active_hop"]["proposal_plan_sha256"] = "d" * 64
        APPLY.atomic_write_yaml(route_root / "journal.yaml", journal)
        digest_errors: list[str] = []
        TARGET.validate_multi_hop_route_transactions(self.fixture.target, digest_errors)
        self.assertTrue(any("active multi-hop proposal plan differs" in error for error in digest_errors))

        journal["active_hop"] = deepcopy(original_active)
        journal["active_hop"]["package"] = {}
        APPLY.atomic_write_yaml(route_root / "journal.yaml", journal)
        empty_package_errors: list[str] = []
        TARGET.validate_multi_hop_route_transactions(self.fixture.target, empty_package_errors)
        self.assertTrue(any("prepared package differs" in error for error in empty_package_errors))

        journal["active_hop"] = deepcopy(original_active)
        APPLY.atomic_write_yaml(route_root / "journal.yaml", journal)
        stderr_path = route_root / "hops" / "0000" / "validator.stderr.log"
        stderr_original = stderr_path.read_bytes()
        try:
            stderr_path.write_bytes(stderr_original + b"tampered\n")
            stderr_errors: list[str] = []
            TARGET.validate_multi_hop_route_transactions(self.fixture.target, stderr_errors)
            self.assertTrue(any("validator execution evidence differs" in error for error in stderr_errors))
        finally:
            stderr_path.write_bytes(stderr_original)

        journal["active_hop"] = {"unexpected": True}
        APPLY.atomic_write_yaml(route_root / "journal.yaml", journal)
        errors: list[str] = []
        TARGET.validate_multi_hop_route_transactions(self.fixture.target, errors)
        self.assertTrue(any("active multi-hop route evidence is invalid" in error for error in errors))

    def test_gwt_007_given_unrelated_single_hop_plan_when_it_is_claimed_as_initial_route_child_then_validator_rejects_it(self) -> None:
        begun = self._begin()
        route_root, intent, journal = MULTI._load_route(
            self.fixture.target, begun["route_transaction_id"]
        )
        ordinary_unsigned = {"schema_version": APPLY.APPLY_PLAN_SCHEMA_VERSION}
        transaction_id = APPLY.canonical_digest(ordinary_unsigned)
        ordinary_plan = {**ordinary_unsigned, "plan_sha256": transaction_id}
        child_root = APPLY.git_admin_transaction_base(self.fixture.target) / transaction_id
        child_root.mkdir(parents=True)
        APPLY.atomic_write_bytes(child_root / "plan.json", APPLY.canonical_json_bytes(ordinary_plan))
        journal.update(
            {
                "state": "awaiting-target-validation",
                "active_hop": {
                    "hop_index": 0,
                    "edge": intent["route"]["edges"][0],
                    "package": {},
                    "validator_execution": {},
                    "plan_sha256": transaction_id,
                    "proposal_plan_sha256": transaction_id,
                    "child_transaction_id": transaction_id,
                    "pending_receipt_sha256": "c" * 64,
                    "child_evidence_path": f"ai-context-package-apply/{transaction_id}",
                },
            }
        )
        APPLY.atomic_write_yaml(route_root / "journal.yaml", journal)

        errors: list[str] = []
        TARGET.validate_multi_hop_route_transactions(self.fixture.target, errors)

        self.assertTrue(any("active multi-hop child route context differs" in error for error in errors))

    def test_gwt_008_given_portable_runtime_when_builder_module_is_unavailable_then_outer_orchestrator_imports(self) -> None:
        probe = (
            "import sys; "
            f"sys.path.insert(0, {str(ROOT / '.ai/scripts')!r}); "
            "sys.modules['ai_context_package'] = None; "
            "import ai_context_multi_hop_upgrade; "
            "print('PORTABLE_CORE_IMPORT_OK')"
        )
        result = subprocess.run(
            [sys.executable, "-B", "-c", probe],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertEqual("PORTABLE_CORE_IMPORT_OK\n", result.stdout)

    def test_gwt_009_given_finalized_child_from_wrong_route_hop_when_checkpoint_evidence_is_collected_then_it_is_rejected(self) -> None:
        begun = self._begin()
        route_root, intent, journal = MULTI._load_route(
            self.fixture.target, begun["route_transaction_id"]
        )
        expected = MULTI._next_context(route_root, intent, journal)
        wrong = {**expected, "edge_id": intent["route"]["edges"][1]["edge_id"]}
        plan = {
            "schema_version": APPLY.APPLY_PLAN_SCHEMA_VERSION,
            APPLY.MULTI_HOP_ROUTE_CONTEXT_KEY: wrong,
        }
        child_journal = {
            "schema_version": APPLY.JOURNAL_SCHEMA_VERSION,
            "state": "finalized",
            "terminal_receipt_path": "terminal-receipt.json",
            APPLY.MULTI_HOP_ROUTE_CONTEXT_KEY: wrong,
        }
        with mock.patch.object(
            APPLY,
            "load_transaction",
            return_value=(self.fixture.target, plan, child_journal),
        ):
            with self.assertRaisesRegex(
                MULTI.MultiHopUpgradeError,
                "route context differs from active route hop",
            ):
                MULTI._child_checkpoint_evidence(
                    self.fixture.target,
                    "a" * 64,
                    {},
                    expected,
                )

    def test_gwt_010_given_two_exact_packages_when_each_child_is_applied_validated_finalized_and_checkpointed_then_route_completes(self) -> None:
        e2e = self.fixture.prepare_e2e()
        self.assertEqual(
            ["REL-v0.10.0", "REL-v0.11.0"],
            [edge["package_identity"]["release_id"] for edge in e2e["edges"]],
        )
        # This is the production admission path: source S1 resolution and
        # supplied source assets must both be real, not mocked resolver output.
        with self.subTest("unmocked-real-s1-two-hop"):
            begun = MULTI.begin_multi_hop_upgrade(
                self.fixture.target,
                self.fixture.matrix_path,
                origin="v0.9.0",
                target_version="v0.11.0",
            )
            first = MULTI.prepare_next_hop(
                self.fixture.target,
                begun["route_transaction_id"],
                matrix_root=self.fixture.matrix_root,
                initial_previous_files_path=e2e["initial_files"],
                initial_previous_version="0.9.0",
            )
            first_provenance, first_ledger = self.fixture.candidate_authorities(
                e2e["sources"][0], e2e["initial_source"], e2e["selection"], "0.9.0", "0.10.0"
            )
            first_apply = MULTI.apply_prepared_hop(
                self.fixture.target,
                begun["route_transaction_id"],
                self.fixture.remediation_decision(first["plan"], first_provenance, first_ledger),
            )
            self.assertEqual(first["plan"]["plan_sha256"], first_apply["transaction_id"])
            MULTI.record_hop_target_validation(
                self.fixture.target,
                begun["route_transaction_id"],
                self.fixture.supplied_target_validation_receipt(first["plan"]),
            )
            first_final = MULTI.finalize_hop(
                self.fixture.target,
                begun["route_transaction_id"],
                first_provenance,
                first_ledger,
            )
            self.assertEqual(0, first_final["checkpoint_index"])
            self.assertFalse(first_final["completed"])
            self.assertFalse((self.fixture.target / APPLY.PENDING_RECEIPT_PATH).exists())

            git_processes: list[tuple[str, ...]] = []
            original_snapshot_git = APPLY._snapshot_git

            def counted_snapshot_git(
                root: Path,
                stats: APPLY.GitInspectionStats,
                *args: str,
                input_bytes: bytes | None = None,
            ) -> object:
                git_processes.append(args)
                return original_snapshot_git(
                    root, stats, *args, input_bytes=input_bytes
                )

            with mock.patch.object(
                TARGET,
                "route_target_surface",
                side_effect=AssertionError(
                    "later-hop validation fell back to per-path Git surface"
                ),
            ), mock.patch.object(
                TARGET,
                "current_target_head",
                side_effect=AssertionError(
                    "later-hop validation fell back to a standalone HEAD process"
                ),
            ), mock.patch.object(
                TARGET,
                "apply_transaction_directory",
                side_effect=AssertionError(
                    "later-hop validation re-resolved the package transaction path"
                ),
            ), mock.patch.object(
                TARGET,
                "multi_hop_route_directory",
                side_effect=AssertionError(
                    "later-hop validation re-resolved the route transaction path"
                ),
            ), mock.patch.object(
                APPLY,
                "_snapshot_git",
                side_effect=counted_snapshot_git,
            ):
                second = MULTI.prepare_next_hop(
                    self.fixture.target,
                    begun["route_transaction_id"],
                    matrix_root=self.fixture.matrix_root,
                )
            self.assertEqual(22, len(git_processes))
            second_provenance, second_ledger = self.fixture.candidate_authorities(
                e2e["sources"][1], e2e["sources"][0], e2e["selection"], "0.10.0", "0.11.0"
            )
            second_apply = MULTI.apply_prepared_hop(
                self.fixture.target,
                begun["route_transaction_id"],
                self.fixture.remediation_decision(second["plan"], second_provenance, second_ledger),
            )
            self.assertEqual(second["plan"]["plan_sha256"], second_apply["transaction_id"])
            MULTI.record_hop_target_validation(
                self.fixture.target,
                begun["route_transaction_id"],
                self.fixture.supplied_target_validation_receipt(second["plan"]),
            )
            second_final = MULTI.finalize_hop(
                self.fixture.target,
                begun["route_transaction_id"],
                second_provenance,
                second_ledger,
            )
        self.assertEqual(1, second_final["checkpoint_index"])
        self.assertTrue(second_final["completed"])
        route_root, _intent, journal = MULTI._load_route(
            self.fixture.target, begun["route_transaction_id"]
        )
        self.assertEqual("completed", journal["state"])
        self.assertTrue((route_root / "checkpoints" / "0000.json").is_file())
        self.assertTrue((route_root / "checkpoints" / "0001.json").is_file())
        errors: list[str] = []
        TARGET.validate_multi_hop_route_transactions(self.fixture.target, errors)
        self.assertEqual([], errors)

        # The final checkpoint can be durable before the terminal journal
        # promotion.  Its exact post-crash state must promote, not strand.
        journal["state"] = "checkpointed"
        APPLY.atomic_write_yaml(route_root / "journal.yaml", journal)
        resumed = MULTI.resume_multi_hop_upgrade(
            self.fixture.target, begun["route_transaction_id"]
        )
        self.assertEqual("completed", resumed["state"])
        self.assertEqual(1, resumed["recovered_final_checkpoint"])
        first_child = APPLY.transaction_root(self.fixture.target, first_apply["transaction_id"])
        for label, path in {
            "packet": first_child / "remediation-packet.json",
            "decision": first_child / "remediation-decision.json",
            "incoming-receipt": first_child / "incoming-validation-receipt.json",
            "target-receipt": first_child / "target-validation-receipt.json",
        }.items():
            with self.subTest(completed_tamper=label):
                original = path.read_bytes()
                try:
                    path.write_bytes(original + b"\nTAMPERED\n")
                    with self.assertRaises(MULTI.MultiHopUpgradeError):
                        MULTI.resume_multi_hop_upgrade(
                            self.fixture.target, begun["route_transaction_id"]
                        )
                finally:
                    path.write_bytes(original)

    def test_gwt_011_given_rejected_owner_decision_when_first_hop_is_applied_then_no_target_mutation_is_retained_as_active(self) -> None:
        e2e = self.fixture.prepare_e2e()
        with mock.patch.object(
            MULTI.ROUTES,
            "resolve_matrix_file",
            side_effect=lambda *_args, **_kwargs: self.fixture.resolution(),
        ):
            begun = MULTI.begin_multi_hop_upgrade(
                self.fixture.target,
                self.fixture.matrix_path,
                origin="v0.9.0",
                target_version="v0.11.0",
            )
            first = MULTI.prepare_next_hop(
                self.fixture.target,
                begun["route_transaction_id"],
                matrix_root=self.fixture.matrix_root,
                initial_previous_files_path=e2e["initial_files"],
                initial_previous_version="0.9.0",
            )
            result = MULTI.apply_prepared_hop(
                self.fixture.target,
                begun["route_transaction_id"],
                self.fixture.rejected_remediation_decision(first["plan"]),
            )
        self.assertEqual("owner-rejected-before-target-mutation", result["outcome"])
        route_root, _intent, journal = MULTI._load_route(
            self.fixture.target, begun["route_transaction_id"]
        )
        self.assertEqual("planned", journal["state"])
        self.assertIsNone(journal["active_hop"])
        child = APPLY.transaction_root(self.fixture.target, first["plan"]["plan_sha256"])
        child_journal = yaml.safe_load((child / "journal.yaml").read_text(encoding="utf-8"))
        self.assertEqual("rejected", child_journal["state"])
        self.assertFalse((self.fixture.target / APPLY.PENDING_RECEIPT_PATH).exists())
        self.assertTrue(route_root.is_dir())

    def test_gwt_012_given_route_marked_rolling_back_when_active_child_recovery_restarts_then_exact_active_hop_rolls_back(self) -> None:
        e2e = self.fixture.prepare_e2e()
        with mock.patch.object(
            MULTI.ROUTES,
            "resolve_matrix_file",
            side_effect=lambda *_args, **_kwargs: self.fixture.resolution(),
        ):
            begun = MULTI.begin_multi_hop_upgrade(
                self.fixture.target,
                self.fixture.matrix_path,
                origin="v0.9.0",
                target_version="v0.11.0",
            )
            first = MULTI.prepare_next_hop(
                self.fixture.target,
                begun["route_transaction_id"],
                matrix_root=self.fixture.matrix_root,
                initial_previous_files_path=e2e["initial_files"],
                initial_previous_version="0.9.0",
            )
            provenance, ledger = self.fixture.candidate_authorities(
                e2e["sources"][0],
                e2e["initial_source"],
                e2e["selection"],
                "0.9.0",
                "0.10.0",
            )
            applied = MULTI.apply_prepared_hop(
                self.fixture.target,
                begun["route_transaction_id"],
                self.fixture.remediation_decision(first["plan"], provenance, ledger),
            )
        route_root, intent, journal = MULTI._load_route(
            self.fixture.target, begun["route_transaction_id"]
        )
        self.assertEqual("awaiting-target-validation", journal["state"])
        journal["state"] = "rolling-back"
        MULTI._persist_route_journal(route_root, intent, journal)
        result = MULTI.rollback_active_hop(
            self.fixture.target, begun["route_transaction_id"]
        )
        self.assertEqual("active-unfinalized-hop-only", result["scope"])
        self.assertEqual("planned", result["state"])
        _route_root, _intent, journal = MULTI._load_route(
            self.fixture.target, begun["route_transaction_id"]
        )
        self.assertEqual("planned", journal["state"])
        self.assertIsNone(journal["active_hop"])
        child = APPLY.transaction_root(self.fixture.target, applied["transaction_id"])
        child_journal = yaml.safe_load((child / "journal.yaml").read_text(encoding="utf-8"))
        self.assertEqual("rolled-back", child_journal["state"])

    def test_gwt_013_given_prepared_hop_evidence_tampering_when_apply_is_requested_then_no_child_mutation_starts(self) -> None:
        e2e = self.fixture.prepare_e2e()
        with mock.patch.object(
            MULTI.ROUTES,
            "resolve_matrix_file",
            side_effect=lambda *_args, **_kwargs: self.fixture.resolution(),
        ):
            begun = MULTI.begin_multi_hop_upgrade(
                self.fixture.target,
                self.fixture.matrix_path,
                origin="v0.9.0",
                target_version="v0.11.0",
            )
            first = MULTI.prepare_next_hop(
                self.fixture.target,
                begun["route_transaction_id"],
                matrix_root=self.fixture.matrix_root,
                initial_previous_files_path=e2e["initial_files"],
                initial_previous_version="0.9.0",
            )
            route_root, _intent, journal = MULTI._load_route(
                self.fixture.target, begun["route_transaction_id"]
            )
            active = journal["active_hop"]
            assert isinstance(active, dict)
            package = active["package"]
            execution = active["validator_execution"]
            hop_root = route_root / "hops" / "0000"
            candidates = {
                "archive": route_root.joinpath(*Path(package["archive_path"]).parts),
                "checksum": hop_root / "checksum.sha256",
                "migration-artifact": hop_root / "migration.yaml",
                "manifest": MULTI._package_root(route_root, package) / "metadata" / "files.yaml",
                "validator-record": route_root.joinpath(*Path(execution["record_path"]).parts),
                "validator-stdout": route_root.joinpath(*Path(execution["stdout_path"]).parts),
                "validator-stderr": hop_root / "validator.stderr.log",
                "proposal": hop_root / "preparation.json",
            }
            for label, path in candidates.items():
                with self.subTest(label=label):
                    original = path.read_bytes()
                    try:
                        path.write_bytes(original + b"\nTAMPERED\n")
                        with mock.patch.object(APPLY, "apply_plan_locked") as child_apply:
                            with self.assertRaises(MULTI.MultiHopUpgradeError):
                                MULTI.apply_prepared_hop(
                                    self.fixture.target,
                                    begun["route_transaction_id"],
                                    {},
                                )
                            child_apply.assert_not_called()
                        self.assertFalse(
                            APPLY.transaction_root(
                                self.fixture.target, first["plan"]["plan_sha256"]
                            ).exists()
                        )
                    finally:
                        path.write_bytes(original)

    def test_gwt_014_given_prepare_validator_failure_when_retrying_then_failed_attempt_is_retained_but_never_blocks_exact_new_preparation(self) -> None:
        e2e = self.fixture.prepare_e2e()
        with mock.patch.object(
            MULTI.ROUTES,
            "resolve_matrix_file",
            side_effect=lambda *_args, **_kwargs: self.fixture.resolution(),
        ):
            begun = MULTI.begin_multi_hop_upgrade(
                self.fixture.target,
                self.fixture.matrix_path,
                origin="v0.9.0",
                target_version="v0.11.0",
            )
            with mock.patch.object(
                MULTI,
                "_execute_edge_validator",
                side_effect=MULTI.MultiHopUpgradeError("synthetic validator failure"),
            ):
                with self.assertRaisesRegex(MULTI.MultiHopUpgradeError, "synthetic validator failure"):
                    MULTI.prepare_next_hop(
                        self.fixture.target,
                        begun["route_transaction_id"],
                        matrix_root=self.fixture.matrix_root,
                        initial_previous_files_path=e2e["initial_files"],
                        initial_previous_version="0.9.0",
                    )
            route_root, _intent, journal = MULTI._load_route(
                self.fixture.target, begun["route_transaction_id"]
            )
            failed = sorted((route_root / "failed-preparations").iterdir())
            self.assertEqual(1, len(failed))
            self.assertTrue((failed[0] / "failure.json").is_file())
            self.assertFalse((route_root / "hops" / "0000").exists())
            self.assertEqual("planned", journal["state"])
            self.assertIsNone(journal["active_hop"])
            retry = MULTI.prepare_next_hop(
                self.fixture.target,
                begun["route_transaction_id"],
                matrix_root=self.fixture.matrix_root,
                initial_previous_files_path=e2e["initial_files"],
                initial_previous_version="0.9.0",
            )
        self.assertEqual(0, retry["hop_index"])
        self.assertTrue((route_root / "hops" / "0000" / "evidence.json").is_file())
        self.assertTrue((failed[0] / "failure.json").is_file())

    def test_gwt_015_given_one_edge_durable_intent_when_route_is_loaded_then_it_is_rejected_before_execution(self) -> None:
        begun = self._begin()
        source_root, intent, journal = MULTI._load_route(
            self.fixture.target, begun["route_transaction_id"]
        )
        bad_intent = deepcopy(intent)
        bad_intent.pop("route_transaction_id")
        bad_intent["route"] = {
            "route_id": intent["route"]["route_id"],
            "edges": [intent["route"]["edges"][0]],
        }
        bad_id = APPLY.canonical_digest(bad_intent)
        bad_intent["route_transaction_id"] = bad_id
        bad_root = APPLY.git_admin_multi_hop_route_base(self.fixture.target) / bad_id
        bad_root.mkdir()
        APPLY.atomic_write_bytes(
            bad_root / "route-intent.json", APPLY.canonical_json_bytes(bad_intent)
        )
        APPLY.atomic_write_bytes(
            bad_root / "route-matrix.yaml", (source_root / "route-matrix.yaml").read_bytes()
        )
        bad_journal = deepcopy(journal)
        bad_journal.update(
            {
                "route_transaction_id": bad_id,
                "route_intent_sha256": APPLY.sha256_bytes(
                    APPLY.canonical_json_bytes(bad_intent)
                ),
                "state": "planned",
                "next_hop_index": 0,
                "last_checkpoint_index": None,
                "last_checkpoint_sha256": None,
                "active_hop": None,
            }
        )
        MULTI._write_journal(bad_root / "journal.yaml", bad_journal)
        with self.assertRaisesRegex(MULTI.MultiHopUpgradeError, "intent edges are invalid"):
            MULTI._load_route(self.fixture.target, bad_id)

    def test_gwt_016_given_private_begin_preparation_residue_when_target_validation_reads_routes_then_only_safe_directory_residue_is_ignored(self) -> None:
        base = APPLY.git_admin_multi_hop_route_base(self.fixture.target)
        base.mkdir(parents=True)
        safe = base / ("." + "a" * 64 + ".preparing-safe")
        safe.mkdir()
        safe_errors: list[str] = []
        TARGET.validate_multi_hop_route_transactions(self.fixture.target, safe_errors)
        self.assertEqual([], safe_errors)
        safe.rmdir()
        unsafe = base / ("." + "b" * 64 + ".preparing-unsafe")
        unsafe.write_text("not a directory\n", encoding="utf-8")
        errors: list[str] = []
        TARGET.validate_multi_hop_route_transactions(self.fixture.target, errors)
        self.assertTrue(any("preparation residue is unsafe" in error for error in errors))

    def test_gwt_017_given_missing_selected_archive_when_prepare_is_requested_then_no_hop_is_promoted(self) -> None:
        e2e = self.fixture.prepare_e2e()
        edge = e2e["edges"][0]
        archive = self.fixture.matrix_root / edge["artifacts"]["archive"]["path"]
        original = archive.read_bytes()
        # Begin seals the source resolver's selected route before a later
        # source-asset disappearance.  Preparation must then reject the
        # missing archive rather than reclassifying the sealed route.
        sealed_result = self.fixture.resolution()
        archive.unlink()
        try:
            with mock.patch.object(
                MULTI.ROUTES,
                "resolve_matrix_file",
                return_value=sealed_result,
            ):
                begun = MULTI.begin_multi_hop_upgrade(
                    self.fixture.target,
                    self.fixture.matrix_path,
                    origin="v0.9.0",
                    target_version="v0.11.0",
                )
                # This models disappearance after the independently sealed
                # S1 result.  The materializer must still reject the exact
                # selected archive and retain the failed attempt.
                with mock.patch.object(
                    MULTI.ROUTES,
                    "resolve_upgrade_route",
                    return_value=sealed_result,
                ):
                    with self.assertRaisesRegex(
                        MULTI.MultiHopUpgradeError, "route edge archive must be a regular file"
                    ):
                        MULTI.prepare_next_hop(
                            self.fixture.target,
                            begun["route_transaction_id"],
                            matrix_root=self.fixture.matrix_root,
                            initial_previous_files_path=e2e["initial_files"],
                            initial_previous_version="0.9.0",
                        )
            route_root, _intent, journal = MULTI._load_route(
                self.fixture.target, begun["route_transaction_id"]
            )
            self.assertEqual("planned", journal["state"])
            self.assertIsNone(journal["active_hop"])
            self.assertFalse((route_root / "hops" / "0000").exists())
            self.assertEqual(1, len(list((route_root / "failed-preparations").iterdir())))
        finally:
            archive.write_bytes(original)

    def test_gwt_018_given_selected_package_with_unsupported_schema_when_prepare_is_requested_then_materialization_rejects_it(self) -> None:
        e2e = self.fixture.prepare_e2e()
        edge = e2e["edges"][0]
        archive = self.fixture.matrix_root / edge["artifacts"]["archive"]["path"]
        checksum = self.fixture.matrix_root / edge["artifacts"]["checksum"]["path"]
        with zipfile.ZipFile(archive, "r") as source:
            members = {info.filename: source.read(info) for info in source.infolist() if not info.is_dir()}
        envelope = next(iter(members)).split("/", 1)[0]
        package_member = f"{envelope}/metadata/package.yaml"
        package = yaml.safe_load(members[package_member].decode("utf-8"))
        package["schema_version"] = "999.0.0"
        members[package_member] = self.fixture._yaml_bytes(package)
        checksum_member = f"{envelope}/metadata/SHA256SUMS.txt"
        members[checksum_member] = "".join(
            f"{APPLY.sha256_bytes(content)}  {name.split('/', 1)[1]}\n"
            for name, content in sorted(members.items(), key=lambda item: item[0].encode("utf-8"))
            if name != checksum_member
        ).encode("utf-8")
        with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED) as destination:
            for name, content in sorted(members.items(), key=lambda item: item[0].encode("utf-8")):
                info = zipfile.ZipInfo(name, date_time=(2026, 8, 20, 0, 0, 0))
                info.compress_type = zipfile.ZIP_DEFLATED
                info.external_attr = 0o100644 << 16
                destination.writestr(info, content)
        archive_sha = APPLY.sha256_bytes(archive.read_bytes())
        checksum.write_text(f"{archive_sha}  {archive.name}\n", encoding="utf-8", newline="\n")
        edge["artifacts"]["archive"]["sha256"] = archive_sha
        edge["artifacts"]["checksum"]["sha256"] = APPLY.sha256_bytes(checksum.read_bytes())
        self.fixture._reseal_e2e_route_evidence()
        begun = MULTI.begin_multi_hop_upgrade(
            self.fixture.target,
            self.fixture.matrix_path,
            origin="v0.9.0",
            target_version="v0.11.0",
        )
        with self.assertRaisesRegex(MULTI.MultiHopUpgradeError, "unsupported package schema"):
            MULTI.prepare_next_hop(
                self.fixture.target,
                begun["route_transaction_id"],
                matrix_root=self.fixture.matrix_root,
                initial_previous_files_path=e2e["initial_files"],
                initial_previous_version="0.9.0",
            )

    def test_gwt_019_given_selected_validator_that_disagrees_with_its_expected_output_when_prepare_is_requested_then_it_is_retained_as_failed(self) -> None:
        e2e = self.fixture.prepare_e2e()
        edge = e2e["edges"][0]
        validator = self.fixture.matrix_root / edge["artifacts"]["validator"]["path"]
        validator.write_text(
            "import sys\nsys.stdout.buffer.write(b'validator disagreement\\n')\n",
            encoding="utf-8",
            newline="\n",
        )
        edge["artifacts"]["validator"]["sha256"] = APPLY.sha256_bytes(validator.read_bytes())
        self.fixture._reseal_e2e_route_evidence()
        begun = MULTI.begin_multi_hop_upgrade(
            self.fixture.target,
            self.fixture.matrix_path,
            origin="v0.9.0",
            target_version="v0.11.0",
        )
        with self.assertRaisesRegex(MULTI.MultiHopUpgradeError, "validator execution did not match"):
            MULTI.prepare_next_hop(
                self.fixture.target,
                begun["route_transaction_id"],
                matrix_root=self.fixture.matrix_root,
                initial_previous_files_path=e2e["initial_files"],
                initial_previous_version="0.9.0",
            )
        route_root, _intent, journal = MULTI._load_route(
            self.fixture.target, begun["route_transaction_id"]
        )
        self.assertEqual("planned", journal["state"])
        self.assertEqual(1, len(list((route_root / "failed-preparations").iterdir())))

    def test_gwt_020_given_missing_or_stale_owner_decision_when_apply_is_requested_then_no_child_transaction_is_created(self) -> None:
        e2e = self.fixture.prepare_e2e()
        with mock.patch.object(
            MULTI.ROUTES,
            "resolve_matrix_file",
            side_effect=lambda *_args, **_kwargs: self.fixture.resolution(),
        ):
            begun = MULTI.begin_multi_hop_upgrade(
                self.fixture.target,
                self.fixture.matrix_path,
                origin="v0.9.0",
                target_version="v0.11.0",
            )
            first = MULTI.prepare_next_hop(
                self.fixture.target,
                begun["route_transaction_id"],
                matrix_root=self.fixture.matrix_root,
                initial_previous_files_path=e2e["initial_files"],
                initial_previous_version="0.9.0",
            )
            provenance, ledger = self.fixture.candidate_authorities(
                e2e["sources"][0],
                e2e["initial_source"],
                e2e["selection"],
                "0.9.0",
                "0.10.0",
            )
            correct = self.fixture.remediation_decision(first["plan"], provenance, ledger)
            stale = deepcopy(correct)
            stale["plan_sha256"] = "e" * 64
            stale["transaction_id"] = "e" * 64
            for label, decision in (("missing", {}), ("stale", stale)):
                with self.subTest(label=label):
                    with self.assertRaises(MULTI.MultiHopUpgradeError):
                        MULTI.apply_prepared_hop(
                            self.fixture.target,
                            begun["route_transaction_id"],
                            decision,
                        )
                    self.assertFalse(
                        APPLY.transaction_root(
                            self.fixture.target, first["plan"]["plan_sha256"]
                        ).exists()
                    )
            route_root, _intent, _journal = MULTI._load_route(
                self.fixture.target, begun["route_transaction_id"]
            )
            stderr_path = route_root / "hops" / "0000" / "validator.stderr.log"
            stderr_original = stderr_path.read_bytes()
            try:
                stderr_path.write_bytes(stderr_original + b"tampered\n")
                with self.assertRaises(MULTI.MultiHopUpgradeError):
                    MULTI.resume_multi_hop_upgrade(
                        self.fixture.target, begun["route_transaction_id"]
                    )
            finally:
                stderr_path.write_bytes(stderr_original)
            resumed = MULTI.resume_multi_hop_upgrade(
                self.fixture.target, begun["route_transaction_id"]
            )
            self.assertEqual("awaiting-owner-decision", resumed["state"])
            self.assertEqual("same-exact-owner-decision", resumed["requires"])
            retried = MULTI.apply_prepared_hop(
                self.fixture.target, begun["route_transaction_id"], correct
            )
        _route_root, _intent, journal = MULTI._load_route(
            self.fixture.target, begun["route_transaction_id"]
        )
        self.assertEqual("awaiting-target-validation", journal["state"])
        self.assertIsInstance(journal["active_hop"], dict)
        self.assertTrue(
            APPLY.transaction_root(self.fixture.target, retried["transaction_id"]).is_dir()
        )

    def test_gwt_025_given_bound_child_proposal_crash_residue_when_read_or_resumed_then_only_exact_crash_state_is_accepted_and_cleaned(self) -> None:
        e2e = self.fixture.prepare_e2e()
        with mock.patch.object(
            MULTI.ROUTES,
            "resolve_matrix_file",
            side_effect=lambda *_args, **_kwargs: self.fixture.resolution(),
        ):
            begun = MULTI.begin_multi_hop_upgrade(
                self.fixture.target,
                self.fixture.matrix_path,
                origin="v0.9.0",
                target_version="v0.11.0",
            )
            first = MULTI.prepare_next_hop(
                self.fixture.target,
                begun["route_transaction_id"],
                matrix_root=self.fixture.matrix_root,
                initial_previous_files_path=e2e["initial_files"],
                initial_previous_version="0.9.0",
            )
            provenance, ledger = self.fixture.candidate_authorities(
                e2e["sources"][0],
                e2e["initial_source"],
                e2e["selection"],
                "0.9.0",
                "0.10.0",
            )
            MULTI.apply_prepared_hop(
                self.fixture.target,
                begun["route_transaction_id"],
                self.fixture.remediation_decision(first["plan"], provenance, ledger),
            )
        route_root, intent, journal = MULTI._load_route(
            self.fixture.target, begun["route_transaction_id"]
        )
        proposal_path = route_root / "hops" / "0000" / "preparation.json"
        proposal_raw = APPLY.canonical_json_bytes(first["plan"])
        APPLY.atomic_write_bytes(proposal_path, proposal_raw)
        exact_errors: list[str] = []
        TARGET.validate_multi_hop_route_transactions(self.fixture.target, exact_errors)
        self.assertEqual([], exact_errors)
        resumed = MULTI.resume_multi_hop_upgrade(
            self.fixture.target, begun["route_transaction_id"]
        )
        self.assertEqual("awaiting-target-validation", resumed["state"])
        self.assertFalse(proposal_path.exists())

        APPLY.atomic_write_bytes(proposal_path, proposal_raw)
        journal["state"] = "validating"
        MULTI._persist_route_journal(route_root, intent, journal)
        stale_errors: list[str] = []
        TARGET.validate_multi_hop_route_transactions(self.fixture.target, stale_errors)
        self.assertTrue(any("stale outside its crash state" in error for error in stale_errors))
        with self.assertRaises(MULTI.MultiHopUpgradeError):
            MULTI.resume_multi_hop_upgrade(self.fixture.target, begun["route_transaction_id"])

        journal["state"] = "awaiting-target-validation"
        MULTI._persist_route_journal(route_root, intent, journal)
        proposal_path.write_bytes(proposal_raw + b"\nTAMPERED\n")
        tampered_errors: list[str] = []
        TARGET.validate_multi_hop_route_transactions(self.fixture.target, tampered_errors)
        self.assertTrue(any("bound multi-hop proposal" in error for error in tampered_errors))
        with self.assertRaises(MULTI.MultiHopUpgradeError):
            MULTI.resume_multi_hop_upgrade(self.fixture.target, begun["route_transaction_id"])
        self.assertTrue(proposal_path.exists())

        proposal_path.write_bytes(proposal_raw)
        MULTI.resume_multi_hop_upgrade(self.fixture.target, begun["route_transaction_id"])
        self.assertFalse(proposal_path.exists())

    def test_gwt_026_given_rejected_child_after_proposal_delete_crash_when_resume_runs_then_outer_route_settles_without_proposal(self) -> None:
        begun, route_root, _intent, _journal, _child_root = self._rejected_unbound_child_crash()
        resumed = MULTI.resume_multi_hop_upgrade(
            self.fixture.target, begun["route_transaction_id"]
        )
        self.assertTrue(resumed["recovered_owner_rejection"])
        self.assertEqual("planned", resumed["state"])
        self.assertFalse((route_root / "hops" / "0000" / "preparation.json").exists())
        _route_root, _intent, journal = MULTI._load_route(
            self.fixture.target, begun["route_transaction_id"]
        )
        self.assertEqual("planned", journal["state"])
        self.assertIsNone(journal["active_hop"])

    def test_gwt_027_given_tampered_rejected_child_after_proposal_delete_crash_when_resume_runs_then_recovery_rejects_it(self) -> None:
        begun, _route_root, _intent, _journal, child_root = self._rejected_unbound_child_crash()
        decision_path = child_root / "remediation-decision.json"
        original = decision_path.read_bytes()
        try:
            decision_path.write_bytes(original + b"\nTAMPERED\n")
            with self.assertRaises(MULTI.MultiHopUpgradeError):
                MULTI.resume_multi_hop_upgrade(
                    self.fixture.target, begun["route_transaction_id"]
                )
        finally:
            decision_path.write_bytes(original)
        resumed = MULTI.resume_multi_hop_upgrade(
            self.fixture.target, begun["route_transaction_id"]
        )
        self.assertTrue(resumed["recovered_owner_rejection"])

    def test_gwt_024_given_sealed_first_checkpoint_when_child_or_route_evidence_is_tampered_then_resume_and_later_planning_fail_closed(self) -> None:
        begun, _first, applied, route_root, _intent, _journal = self._finalize_real_first_hop()
        valid_errors: list[str] = []
        TARGET.validate_multi_hop_route_transactions(self.fixture.target, valid_errors)
        self.assertEqual([], valid_errors)
        resumed = MULTI.resume_multi_hop_upgrade(
            self.fixture.target, begun["route_transaction_id"]
        )
        self.assertEqual("checkpointed", resumed["state"])

        child_root = APPLY.transaction_root(self.fixture.target, applied["transaction_id"])
        for label, path in {
            "packet": child_root / "remediation-packet.json",
            "decision": child_root / "remediation-decision.json",
            "incoming-receipt": child_root / "incoming-validation-receipt.json",
            "target-receipt": child_root / "target-validation-receipt.json",
        }.items():
            with self.subTest(label=label):
                original = path.read_bytes()
                try:
                    path.write_bytes(original + b"\nTAMPERED\n")
                    with self.assertRaises(MULTI.MultiHopUpgradeError):
                        MULTI.resume_multi_hop_upgrade(
                            self.fixture.target, begun["route_transaction_id"]
                        )
                finally:
                    path.write_bytes(original)

        checkpoint = json.loads(
            (route_root / "checkpoints" / "0000.json").read_text(encoding="utf-8")
        )
        archive_path = route_root.joinpath(
            *Path(checkpoint["package"]["archive_path"]).parts
        )
        archive_original = archive_path.read_bytes()
        try:
            archive_path.write_bytes(archive_original + b"\nTAMPERED\n")
            with mock.patch.object(
                MULTI.ROUTES,
                "resolve_matrix_file",
                side_effect=lambda *_args, **_kwargs: self.fixture.resolution(),
            ):
                with self.assertRaisesRegex(
                    APPLY.ApplyError, "finalized checkpoint evidence is invalid"
                ):
                    MULTI.prepare_next_hop(
                        self.fixture.target,
                        begun["route_transaction_id"],
                        matrix_root=self.fixture.matrix_root,
                    )
        finally:
            archive_path.write_bytes(archive_original)

    def test_gwt_023_given_child_created_before_outer_binding_when_resume_runs_then_exact_derived_child_is_restored(self) -> None:
        e2e = self.fixture.prepare_e2e()
        with mock.patch.object(
            MULTI.ROUTES,
            "resolve_matrix_file",
            side_effect=lambda *_args, **_kwargs: self.fixture.resolution(),
        ):
            begun = MULTI.begin_multi_hop_upgrade(
                self.fixture.target,
                self.fixture.matrix_path,
                origin="v0.9.0",
                target_version="v0.11.0",
            )
            first = MULTI.prepare_next_hop(
                self.fixture.target,
                begun["route_transaction_id"],
                matrix_root=self.fixture.matrix_root,
                initial_previous_files_path=e2e["initial_files"],
                initial_previous_version="0.9.0",
            )
            provenance, ledger = self.fixture.candidate_authorities(
                e2e["sources"][0],
                e2e["initial_source"],
                e2e["selection"],
                "0.9.0",
                "0.10.0",
            )
            applied = MULTI.apply_prepared_hop(
                self.fixture.target,
                begun["route_transaction_id"],
                self.fixture.remediation_decision(first["plan"], provenance, ledger),
            )
            route_root, intent, journal = MULTI._load_route(
                self.fixture.target, begun["route_transaction_id"]
            )
            active = journal["active_hop"]
            assert isinstance(active, dict)
            proposal_raw = APPLY.canonical_json_bytes(first["plan"])
            self.assertEqual(active["proposal_plan_sha256"], APPLY.sha256_bytes(proposal_raw))
            proposal_path = route_root / "hops" / "0000" / "preparation.json"
            self.assertFalse(proposal_path.exists())
            APPLY.atomic_write_bytes(proposal_path, proposal_raw)
            active["child_transaction_id"] = None
            active.pop("pending_receipt_sha256")
            active.pop("child_evidence_path")
            journal["state"] = "applying"
            MULTI._persist_route_journal(route_root, intent, journal)

            resumed = MULTI.resume_multi_hop_upgrade(
                self.fixture.target, begun["route_transaction_id"]
            )
        self.assertEqual("awaiting-target-validation", resumed["state"])
        self.assertEqual(applied["transaction_id"], resumed["recovered_child_transaction_id"])
        _route_root, _intent, recovered = MULTI._load_route(
            self.fixture.target, begun["route_transaction_id"]
        )
        active = recovered["active_hop"]
        assert isinstance(active, dict)
        self.assertEqual(applied["transaction_id"], active["child_transaction_id"])
        self.assertFalse(proposal_path.exists())

    def test_gwt_021_given_missing_or_stale_target_validation_receipt_when_recorded_then_child_remains_unfinalized(self) -> None:
        e2e = self.fixture.prepare_e2e()
        with mock.patch.object(
            MULTI.ROUTES,
            "resolve_matrix_file",
            side_effect=lambda *_args, **_kwargs: self.fixture.resolution(),
        ):
            begun = MULTI.begin_multi_hop_upgrade(
                self.fixture.target,
                self.fixture.matrix_path,
                origin="v0.9.0",
                target_version="v0.11.0",
            )
            first = MULTI.prepare_next_hop(
                self.fixture.target,
                begun["route_transaction_id"],
                matrix_root=self.fixture.matrix_root,
                initial_previous_files_path=e2e["initial_files"],
                initial_previous_version="0.9.0",
            )
            provenance, ledger = self.fixture.candidate_authorities(
                e2e["sources"][0],
                e2e["initial_source"],
                e2e["selection"],
                "0.9.0",
                "0.10.0",
            )
            applied = MULTI.apply_prepared_hop(
                self.fixture.target,
                begun["route_transaction_id"],
                self.fixture.remediation_decision(first["plan"], provenance, ledger),
            )
            missing = self.fixture.root / "missing-target-validation-receipt.json"
            with self.assertRaises(MULTI.MultiHopUpgradeError):
                MULTI.record_hop_target_validation(
                    self.fixture.target, begun["route_transaction_id"], missing
                )
            supplied = self.fixture.supplied_target_validation_receipt(first["plan"])
            stale = json.loads(supplied.read_text(encoding="utf-8"))
            stale["transaction_id"] = "f" * 64
            stale_path = self.fixture.root / "stale-target-validation-receipt.json"
            stale_path.write_bytes(APPLY.canonical_json_bytes(stale))
            with self.assertRaises(MULTI.MultiHopUpgradeError):
                MULTI.record_hop_target_validation(
                    self.fixture.target, begun["route_transaction_id"], stale_path
                )
        _route_root, _intent, journal = MULTI._load_route(
            self.fixture.target, begun["route_transaction_id"]
        )
        self.assertEqual("validating", journal["state"])
        self.assertIsInstance(journal["active_hop"], dict)
        child = APPLY.transaction_root(self.fixture.target, applied["transaction_id"])
        child_journal = yaml.safe_load((child / "journal.yaml").read_text(encoding="utf-8"))
        self.assertEqual("awaiting-target-validation", child_journal["state"])
        self.assertTrue((self.fixture.target / APPLY.PENDING_RECEIPT_PATH).is_file())

    def test_gwt_022_given_sealed_matrix_bytes_changed_when_resume_is_requested_then_resume_fails_closed(self) -> None:
        begun = self._begin()
        route_root, _intent, _journal = MULTI._load_route(
            self.fixture.target, begun["route_transaction_id"]
        )
        matrix = route_root / "route-matrix.yaml"
        matrix.write_bytes(matrix.read_bytes() + b"tampered\n")
        with self.assertRaisesRegex(MULTI.MultiHopUpgradeError, "matrix bytes differ"):
            MULTI.resume_multi_hop_upgrade(self.fixture.target, begun["route_transaction_id"])

    def test_gwt_028_given_real_s1_matrix_when_first_hop_is_prepared_then_no_mocked_resolver_is_needed(self) -> None:
        """Exercise the production begin/prepare path against a real asset tree."""
        e2e = self.fixture.prepare_e2e()

        begun = MULTI.begin_multi_hop_upgrade(
            self.fixture.target,
            self.fixture.matrix_path,
            origin="v0.9.0",
            target_version="v0.11.0",
        )
        route_root, intent, _journal = MULTI._load_route(
            self.fixture.target, begun["route_transaction_id"]
        )
        resolver_result = route_root / MULTI.ROUTE_RESOLVER_RESULT_PATH
        self.assertTrue(resolver_result.is_file())
        self.assertEqual(
            APPLY.sha256_bytes(resolver_result.read_bytes()),
            intent["resolver_result"]["sha256"],
        )

        first = MULTI.prepare_next_hop(
            self.fixture.target,
            begun["route_transaction_id"],
            matrix_root=self.fixture.matrix_root,
            initial_previous_files_path=e2e["initial_files"],
            initial_previous_version="0.9.0",
        )

        self.assertEqual(0, first["hop_index"])
        self.assertTrue(
            (route_root / "hops" / "0000" / "validator.asset").is_file()
        )
        errors: list[str] = []
        TARGET.validate_multi_hop_route_transactions(self.fixture.target, errors)
        self.assertEqual([], errors)
        self.assertEqual("v0.10.0", first["edge"]["to_version"])

    def test_gwt_029_given_self_consistent_forged_bound_validator_evidence_when_checked_or_recorded_then_it_is_rejected(self) -> None:
        begun, first, _applied, _provenance, _ledger = self._apply_first_hop_without_mock()
        _route_root, _intent, _journal = self._forge_bound_validator_evidence(begun)

        errors: list[str] = []
        TARGET.validate_multi_hop_route_transactions(self.fixture.target, errors)
        self.assertTrue(
            any(
                "sealed full edge" in error
                or "validator execution evidence differs" in error
                or "package differs from sealed full edge artifacts" in error
                for error in errors
            ),
            errors,
        )
        with self.assertRaisesRegex(
            MULTI.MultiHopUpgradeError, "bound multi-hop promoted evidence is invalid"
        ):
            MULTI.record_hop_target_validation(
                self.fixture.target,
                begun["route_transaction_id"],
                self.fixture.supplied_target_validation_receipt(first["plan"]),
            )
        _route_root, _intent, journal = MULTI._load_route(
            self.fixture.target, begun["route_transaction_id"]
        )
        self.assertEqual("awaiting-target-validation", journal["state"])

    def test_gwt_030_given_self_consistent_forged_bound_validator_evidence_when_finalizing_then_target_authority_is_not_advanced(self) -> None:
        begun, first, _applied, provenance, ledger = self._apply_first_hop_without_mock()
        MULTI.record_hop_target_validation(
            self.fixture.target,
            begun["route_transaction_id"],
            self.fixture.supplied_target_validation_receipt(first["plan"]),
        )
        self._forge_bound_validator_evidence(begun)

        with self.assertRaisesRegex(
            MULTI.MultiHopUpgradeError, "bound multi-hop promoted evidence is invalid"
        ):
            MULTI.finalize_hop(
                self.fixture.target,
                begun["route_transaction_id"],
                provenance,
                ledger,
            )
        _route_root, _intent, journal = MULTI._load_route(
            self.fixture.target, begun["route_transaction_id"]
        )
        self.assertEqual("finalizing", journal["state"])

    def test_gwt_032_given_forged_bound_validator_evidence_when_rollback_or_checkpoint_resume_is_requested_then_no_route_boundary_advances(self) -> None:
        """Mutating recovery paths must reprobe promoted evidence first."""
        original_fixture = self.fixture
        try:
            for action, expected_state in (
                ("rollback", "awaiting-target-validation"),
                ("checkpointing-resume", "checkpointing"),
            ):
                with self.subTest(action=action):
                    scenario_fixture = MultiHopFixture()
                    self.fixture = scenario_fixture
                    try:
                        begun, _first, _applied, _provenance, _ledger = (
                            self._apply_first_hop_without_mock()
                        )
                        if action == "checkpointing-resume":
                            route_root, intent, journal = MULTI._load_route(
                                self.fixture.target, begun["route_transaction_id"]
                            )
                            journal["state"] = "checkpointing"
                            MULTI._persist_route_journal(route_root, intent, journal)
                        route_root, _intent, _journal = self._forge_bound_validator_evidence(
                            begun
                        )
                        before = self._route_mutation_snapshot(route_root)

                        with self.assertRaisesRegex(
                            MULTI.MultiHopUpgradeError,
                            "bound multi-hop promoted evidence is invalid",
                        ):
                            if action == "rollback":
                                MULTI.rollback_active_hop(
                                    self.fixture.target, begun["route_transaction_id"]
                                )
                            else:
                                MULTI.resume_multi_hop_upgrade(
                                    self.fixture.target, begun["route_transaction_id"]
                                )

                        self.assertEqual(before, self._route_mutation_snapshot(route_root))
                        _route_root, _intent, journal = MULTI._load_route(
                            self.fixture.target, begun["route_transaction_id"]
                        )
                        self.assertEqual(expected_state, journal["state"])
                    finally:
                        scenario_fixture.close()
                        self.fixture = original_fixture
        finally:
            self.fixture = original_fixture


if __name__ == "__main__":
    unittest.main()
