#!/usr/bin/env python3
"""Given-When-Then tests for fail-closed AI context package application."""

from __future__ import annotations

import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from contextlib import nullcontext
from pathlib import Path
from unittest import mock

import yaml


ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / ".ai/scripts"))
MODULE_PATH = ROOT / ".ai/scripts/ai_context_package_apply.py"
SPEC = importlib.util.spec_from_file_location("ai_context_package_apply", MODULE_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"Unable to load package apply module: {MODULE_PATH}")
APPLY = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = APPLY
SPEC.loader.exec_module(APPLY)
RAW_APPLY_PLAN = APPLY.apply_plan

import ai_context_target_provenance as TARGET  # noqa: E402
import ai_context_package_validation as PACKAGE_VALIDATION  # noqa: E402


def git(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", *args], cwd=root, check=True, capture_output=True, text=True)


class PackageApplyFixture:
    def __init__(self) -> None:
        self._temporary = tempfile.TemporaryDirectory(prefix="ai-context-package-apply-")
        self.root = Path(self._temporary.name)
        self.target = self.root / "target"
        self.package = self.root / "package"
        self.target.mkdir()
        (self.package / "metadata").mkdir(parents=True)
        (self.package / "payload").mkdir()
        git(self.target, "init", "-q")
        git(self.target, "config", "user.name", "Fixture")
        git(self.target, "config", "user.email", "fixture@example.invalid")
        (self.target / "README.md").write_text("fixture\n", encoding="utf-8")
        git(self.target, "add", "README.md")
        git(self.target, "commit", "-qm", "fixture baseline")
        self.previous_path: Path | None = None

    def close(self) -> None:
        self._temporary.cleanup()

    def add_target(self, path: str, content: bytes, executable: bool = False) -> None:
        target = self.target / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(content)
        if executable:
            os.chmod(target, 0o755)
        git(self.target, "add", "--", path)
        if executable:
            git(self.target, "update-index", "--chmod=+x", "--", path)

    def commit_target(self, message: str = "target files") -> None:
        git(self.target, "commit", "-qm", message)

    @staticmethod
    def record(
        path: str,
        content: bytes,
        ownership: str = "framework-managed",
        mode: str = "0644",
        component_id: str | None = None,
    ) -> dict:
        record = {
            "path": path,
            "source_path": path,
            "sha256": APPLY.sha256_bytes(content),
            "size": len(content),
            "mode": mode,
            "ownership": ownership,
            "install_behavior": "seed" if ownership == "target-template" else "managed",
            "entry_id": "fixture",
        }
        if component_id is not None:
            record["component_id"] = component_id
        return record

    def reseal(self) -> None:
        checksum_lines = []
        for path in sorted(
            (
                item
                for item in self.package.rglob("*")
                if item.is_file() and item.name != "SHA256SUMS.txt"
            ),
            key=lambda item: item.relative_to(self.package).as_posix().encode("utf-8"),
        ):
            relative = path.relative_to(self.package).as_posix()
            checksum_lines.append(
                f"{APPLY.sha256_bytes(path.read_bytes())}  {relative}\n"
            )
        (self.package / "metadata/SHA256SUMS.txt").write_text(
            "".join(checksum_lines), encoding="utf-8", newline="\n"
        )

    def make_package(
        self,
        incoming: dict[str, tuple[bytes, str, str]],
        operations: list[dict],
        previous: dict[str, tuple[bytes, str, str]] | None = None,
    ) -> None:
        incoming_records = []
        for path in sorted(incoming, key=lambda item: item.encode("utf-8")):
            content, ownership, mode = incoming[path]
            payload = self.package / "payload" / path
            payload.parent.mkdir(parents=True, exist_ok=True)
            payload.write_bytes(content)
            incoming_records.append(self.record(path, content, ownership, mode))
        files = {"schema_version": "1.0.0", "package_id": "fixture-v1.0.0", "files": incoming_records}
        files_path = self.package / "metadata/files.yaml"
        files_path.write_text(yaml.safe_dump(files, sort_keys=False), encoding="utf-8", newline="\n")
        previous_sha = None
        previous_version = None
        if previous is not None:
            previous_records = [
                self.record(path, *previous[path])
                for path in sorted(previous, key=lambda item: item.encode("utf-8"))
            ]
            previous_document = {
                "schema_version": "1.0.0",
                "package_id": "fixture-v0.9.0",
                "files": previous_records,
            }
            self.previous_path = self.root / "previous-files.yaml"
            self.previous_path.write_text(
                yaml.safe_dump(previous_document, sort_keys=False), encoding="utf-8", newline="\n"
            )
            previous_sha = APPLY.sha256_bytes(self.previous_path.read_bytes())
            previous_version = "0.9.0"
        package = {"schema_version": "1.0.0", "package_id": "fixture-v1.0.0", "version": "1.0.0"}
        migration = {
            "schema_version": "1.0.0",
            "package_id": "fixture-v1.0.0",
            "from": {"version": previous_version, "manifest_sha256": previous_sha},
            "to": {"version": "1.0.0", "manifest_sha256": APPLY.sha256_bytes(files_path.read_bytes())},
            "operations": operations,
            "safety": {
                "dry_run_default": True,
                "clean_worktree_required": True,
                "starting_commit_required": True,
                "abort_on_unacknowledged_reconciliation": True,
            },
        }
        (self.package / "metadata/package.yaml").write_text(
            yaml.safe_dump(package, sort_keys=False), encoding="utf-8", newline="\n"
        )
        (self.package / "metadata/migration.yaml").write_text(
            yaml.safe_dump(migration, sort_keys=False), encoding="utf-8", newline="\n"
        )
        self.reseal()

    def plan(self, previous_version: str | None = None) -> dict:
        return APPLY.build_plan(self.package, self.target, self.previous_path, previous_version)

    def make_schema_v2_migration(
        self,
        clean_install_operations: list[dict],
        sources: list[dict],
    ) -> None:
        """Replace the fixture migration with schema v2 and re-seal its envelope."""
        files_path = self.package / "metadata/files.yaml"
        migration = {
            "schema_version": "2.0.0",
            "package_id": "fixture-v1.0.0",
            "to": {"version": "1.0.0", "manifest_sha256": APPLY.sha256_bytes(files_path.read_bytes())},
            "clean_install": {"operations": clean_install_operations},
            "sources": sources,
            "safety": {
                "dry_run_default": True,
                "clean_worktree_required": True,
                "starting_commit_required": True,
                "abort_on_unacknowledged_reconciliation": True,
            },
        }
        (self.package / "metadata/migration.yaml").write_text(
            yaml.safe_dump(migration, sort_keys=False), encoding="utf-8", newline="\n"
        )
        self.reseal()

    def make_component_package(
        self,
        incoming: dict[str, tuple[bytes, str, str, str]],
        clean_operations: list[dict],
        sources: list[dict] | None = None,
    ) -> None:
        records = []
        for path in sorted(incoming, key=lambda item: item.encode("utf-8")):
            content, ownership, mode, component_id = incoming[path]
            payload = self.package / "payload" / path
            payload.parent.mkdir(parents=True, exist_ok=True)
            payload.write_bytes(content)
            records.append(
                self.record(path, content, ownership, mode, component_id)
            )
        files = {
            "schema_version": "2.0.0",
            "package_id": "fixture-v1.0.0",
            "files": records,
        }
        files_path = self.package / "metadata/files.yaml"
        files_path.write_text(
            yaml.safe_dump(files, sort_keys=False), encoding="utf-8", newline="\n"
        )
        selection = yaml.safe_load(yaml.safe_dump(APPLY.DEFAULT_COMPONENT_SELECTION))
        package = {
            "schema_version": "2.0.0",
            "package_id": "fixture-v1.0.0",
            "version": "1.0.0",
            "selection": selection,
        }
        migration = {
            "schema_version": "3.0.0",
            "package_id": "fixture-v1.0.0",
            "selection": selection,
            "to": {
                "version": "1.0.0",
                "manifest_sha256": APPLY.sha256_bytes(files_path.read_bytes()),
            },
            "clean_install": {"operations": clean_operations},
            "sources": sources or [],
            "safety": {
                "dry_run_default": True,
                "clean_worktree_required": True,
                "starting_commit_required": True,
                "abort_on_unacknowledged_reconciliation": True,
            },
        }
        (self.package / "metadata/package.yaml").write_text(
            yaml.safe_dump(package, sort_keys=False), encoding="utf-8", newline="\n"
        )
        (self.package / "metadata/migration.yaml").write_text(
            yaml.safe_dump(migration, sort_keys=False), encoding="utf-8", newline="\n"
        )
        self.reseal()

    def write_provenance(self, enabled: bool) -> None:
        path = self.target / ".dev/ai-context/provenance.yaml"
        path.parent.mkdir(parents=True, exist_ok=True)
        selection = yaml.safe_load(yaml.safe_dump(APPLY.DEFAULT_COMPONENT_SELECTION))
        selection["providers"]["repo-backlog"]["enabled"] = enabled
        provenance, _ledger = TARGET.build_initialization_documents(
            {
                "repository": "https://example.invalid/framework",
                "release_id": "REL-v0.9.0",
                "version": "v0.9.0",
                "tag": "v0.9.0",
                "commit": "a" * 40,
            },
            selection,
            "2026-08-20T12:00:00+08:00",
        )
        path.write_text(
            yaml.safe_dump(provenance, sort_keys=False),
            encoding="utf-8",
            newline="\n",
        )
        git(self.target, "add", "--", ".dev/ai-context/provenance.yaml")


def seed_executable_target_validation_profile(fixture: PackageApplyFixture) -> None:
    fixture.add_target(
        ".dev/project-config.yaml",
        yaml.safe_dump(
            {
                "validation": {
                    "routine": {
                        "argv": ["python", "-c", "print('target validation')"]
                    }
                }
            },
            sort_keys=False,
        ).encode("utf-8"),
    )


def operation(
    identifier: str,
    kind: str,
    path: str,
    ownership: str = "framework-managed",
    from_path: str | None = None,
    component_id: str | None = None,
) -> dict:
    preconditions = {
        "add": ["destination_absent"],
        "replace": ["current_sha256_equals_previous_release"],
        "remove": ["current_sha256_equals_previous_release"],
        "rename": ["source_sha256_equals_previous_release", "destination_absent"],
        "reconcile": ["human_acknowledgement"],
    }[kind]
    value = {"id": identifier, "kind": kind, "path": path, "ownership": ownership, "preconditions": preconditions}
    if from_path is not None:
        value["from_path"] = from_path
    if component_id is not None:
        value["component_id"] = component_id
    return value


def fixture_remediation_decision(
    plan: dict,
    status: str = "approved",
    candidate_provenance: dict | None = None,
    candidate_ledger: dict | None = None,
) -> dict:
    packet = APPLY.build_upgrade_remediation_packet(plan)
    proposal = packet["automatic_proposal"]
    return {
        "schema_version": "upgrade-remediation-decision/v1",
        "packet_sha256": packet["canonical_digest"],
        "plan_sha256": plan["plan_sha256"],
        "transaction_id": plan["plan_sha256"],
        "status": status,
        "owner": "fixture-owner",
        "decided_at": "2026-08-20T12:00:00+08:00",
        "evidence": "fixture-decision",
        "reason": "exercise explicit upgrade authorization binding",
        "accepted_operation_ids": (
            proposal["apply_operation_ids"] if status == "approved" else []
        ),
        "reconciliation_ids": (
            proposal["reconciliation_ids"] if status == "approved" else []
        ),
        "policy_adoptions": None,
        "candidate_authority": (
            {
                "provenance_sha256": TARGET.canonical_json_digest(
                    candidate_provenance
                )
                if candidate_provenance is not None
                else "a" * 64,
                "customizations_sha256": TARGET.canonical_json_digest(candidate_ledger)
                if candidate_ledger is not None
                else "b" * 64,
            }
            if status == "approved"
            else None
        ),
    }


def apply_fixture_plan(
    plan: dict,
    acknowledgements: set[str] | None = None,
    boundary_hook=None,
    remediation_decision: dict | None = None,
) -> dict:
    """Give historical automatic fixtures explicit authority without hiding conflicts."""
    acknowledgements = acknowledgements or set()
    if not plan.get("upgrade_remediation_required"):
        return RAW_APPLY_PLAN(plan, acknowledgements, boundary_hook)
    packet = APPLY.build_upgrade_remediation_packet(plan)
    proposal = packet["automatic_proposal"]
    if remediation_decision is None:
        if (
            proposal["unresolved_operation_ids"]
            or proposal["ignored_framework_paths"]
            or proposal["managed_state_conflicts"]
        ):
            return RAW_APPLY_PLAN(plan, acknowledgements, boundary_hook)
        if proposal["reconciliation_ids"]:
            if acknowledgements != set(proposal["reconciliation_ids"]):
                return RAW_APPLY_PLAN(plan, acknowledgements, boundary_hook)
            remediation_decision = fixture_remediation_decision(plan)
            acknowledgements = set()
        else:
            remediation_decision = fixture_remediation_decision(plan)
    return RAW_APPLY_PLAN(
        plan,
        acknowledgements,
        boundary_hook,
        remediation_decision=remediation_decision,
    )


def make_schema_23_upgrade_package(
    fixture: PackageApplyFixture, *, validator_content: bytes | None = None
) -> dict:
    """Build a small portable v2.3 envelope with an executable incoming validator."""
    package_id = "fixture-ai-context-dotnet-backend-1.0.0"
    version = "1.0.0"
    selection = yaml.safe_load(yaml.safe_dump(APPLY.DEFAULT_COMPONENT_SELECTION))
    validator_path = ".ai/scripts/validate-ai-context-payload.py"
    install_content = (
        b"# Install\n\n"
        b"python -m pip install -r requirements.txt\n\n"
        b"python payload/.ai/scripts/validate-ai-context-payload.py --package-root .\n"
    )
    payload = {
        validator_path: validator_content
        or (ROOT / ".ai/scripts/validate-ai-context-payload.py").read_bytes(),
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
        ".ai/assets/shared/example.md": b"# Incoming schema-2.3 fixture\n",
    }
    component_by_path = {
        validator_path: "ai-context-lifecycle-core",
        ".ai/scripts/ai_context_package_validation.py": "ai-context-lifecycle-core",
        ".ai/assets/shared/example.md": "dotnet-backend",
    }
    records: list[dict] = []
    for relative, content in sorted(payload.items(), key=lambda item: item[0].encode("utf-8")):
        destination = fixture.package / "payload" / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(content)
        records.append(
            fixture.record(
                relative,
                content,
                component_id=component_by_path.get(
                    relative, "software-development-core"
                ),
            )
        )

    previous_content = b"# Previous schema-2.3 fixture\n"
    previous_document = {
        "schema_version": "2.0.0",
        "package_id": "fixture-ai-context-dotnet-backend-0.9.0",
        "files": [
            fixture.record(
                ".ai/assets/shared/example.md",
                previous_content,
                component_id="dotnet-backend",
            )
        ],
    }
    fixture.previous_path = fixture.root / "previous-files.yaml"
    fixture.previous_path.write_text(
        yaml.safe_dump(previous_document, sort_keys=False),
        encoding="utf-8",
        newline="\n",
    )
    previous_sha = APPLY.sha256_bytes(fixture.previous_path.read_bytes())
    files_document = {
        "schema_version": "2.0.0",
        "package_id": package_id,
        "files": records,
    }
    files_content = yaml.safe_dump(files_document, sort_keys=False).encode("utf-8")
    source_operations = []
    clean_operations = []
    for index, record in enumerate(records, 1):
        component_id = record["component_id"]
        source_operations.append(
            operation(
                f"upgrade-{index:04d}",
                "replace" if record["path"] == ".ai/assets/shared/example.md" else "add",
                record["path"],
                component_id=component_id,
            )
        )
        clean_operations.append(
            operation(
                f"clean-install-{index:04d}",
                "add",
                record["path"],
                component_id=component_id,
            )
        )
    migration = {
        "schema_version": "3.0.0",
        "package_id": package_id,
        "selection": selection,
        "to": {"version": version, "manifest_sha256": APPLY.sha256_bytes(files_content)},
        "clean_install": {"operations": clean_operations},
        "sources": [
            {
                "version": "0.9.0",
                "manifest_sha256": previous_sha,
                "operations": source_operations,
            }
        ],
        "safety": {
            "dry_run_default": True,
            "clean_worktree_required": True,
            "starting_commit_required": True,
            "abort_on_unacknowledged_reconciliation": True,
        },
    }
    migration_content = yaml.safe_dump(migration, sort_keys=False).encode("utf-8")
    proof = {
        "schema_version": "package-selected-input/v1",
        "source_inputs": [
            {
                "path": ".ai/distribution/profiles/dotnet-backend.yaml",
                "sha256": APPLY.sha256_bytes(b"dotnet-profile\n"),
            },
            {
                "path": ".ai/distribution/templates/INSTALL.md",
                "sha256": APPLY.sha256_bytes(install_content),
            },
            {
                "path": ".ai/distribution/templates/requirements.txt",
                "sha256": APPLY.sha256_bytes(b"PyYAML==6.0.3\n"),
            },
            {
                "path": ".dev/releases/v1.0.0/release.yaml",
                "sha256": APPLY.sha256_bytes(b"release\n"),
            },
        ],
        "payload": [
            {
                key: record[key]
                for key in (
                    "path",
                    "sha256",
                    "mode",
                    "ownership",
                    "install_behavior",
                    "component_id",
                )
            }
            for record in records
        ],
        "migration_sources": [
            {"version": "0.9.0", "manifest_sha256": previous_sha}
        ],
    }
    package_canonical_json = lambda document: json.dumps(
        document, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    proof_content = package_canonical_json(proof)
    validation = {
        "schema_version": "package-validation/v1",
        "package_id": package_id,
        "authority": {
            "kind": "incoming-candidate",
            "validator": {
                "path": validator_path,
                "sha256": APPLY.sha256_bytes(payload[validator_path]),
                "argv": [
                    "python",
                    "payload/.ai/scripts/validate-ai-context-payload.py",
                    "--package-root",
                    ".",
                ],
            },
        },
        "selected_input_proof": {
            "path": "metadata/selected-inputs.json",
            "sha256": APPLY.sha256_bytes(proof_content),
        },
        "source_only_tests": {
            "classification": "source-only",
            "contributes_to_portable_success": False,
            "patterns": [
                ".ai/scripts/tests/**",
                ".ai/assets/skills/**/scripts/tests/**",
            ],
        },
        "integrity_policy": {
            "path_case": "casefold-unique",
            "payload_text": "all",
            "text": {
                "encoding": "utf-8",
                "line_endings": "lf-only",
                "terminal_lf": "exactly-one",
            },
            "modes": {"allowed": ["0644", "0755"]},
        },
    }
    validation_content = package_canonical_json(validation)
    payload_fingerprint = APPLY.sha256_bytes(
        "".join(
            f"{record['sha256']}  {record['path']}\n" for record in records
        ).encode("utf-8")
    )
    package = {
        "schema_version": "2.3.0",
        "package_id": package_id,
        "profile_id": "dotnet-backend",
        "version": version,
        "release_id": "REL-v1.0.0",
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
                {
                    "component_id": "software-development-core",
                    "classification": "mandatory-core",
                    "required": True,
                    "requires": [],
                },
                {
                    "component_id": "ai-context-lifecycle-core",
                    "classification": "mandatory-core",
                    "required": True,
                    "requires": [],
                },
                {
                    "component_id": "dotnet-backend",
                    "classification": "technology-profile",
                    "required": False,
                    "requires": ["software-development-core"],
                },
                {
                    "component_id": "repo-backlog",
                    "classification": "optional-provider",
                    "required": False,
                    "requires": ["software-development-core"],
                },
            ],
            "supported_selections": [
                {
                    "selection_id": "dotnet-backend-default",
                    "components": [
                        "software-development-core",
                        "ai-context-lifecycle-core",
                        "dotnet-backend",
                    ],
                }
            ],
            "capabilities": [],
        },
        "source": {
            "repository": "https://example.invalid/framework",
            "ref": "a" * 40,
            "commit": "a" * 40,
            "tree": "b" * 40,
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
        "payload": {
            "root": "payload",
            "file_count": len(records),
            "sha256": payload_fingerprint,
        },
        "compatibility": {
            "minimum_governed_source": "0.1.0",
            "breaking_changes": False,
            "automatic_upgrade_sources": ["0.9.0"],
        },
        "validation": {
            "schema_version": "package-validation/v1",
            "manifest": "metadata/validation.json",
            "manifest_sha256": APPLY.sha256_bytes(validation_content),
            "selected_inputs": "metadata/selected-inputs.json",
            "selected_inputs_sha256": APPLY.sha256_bytes(proof_content),
        },
    }
    (fixture.package / "INSTALL.md").write_bytes(install_content)
    (fixture.package / "requirements.txt").write_text(
        "PyYAML==6.0.3\n", encoding="utf-8", newline="\n"
    )
    (fixture.package / "metadata/package.yaml").write_text(
        yaml.safe_dump(package, sort_keys=False), encoding="utf-8", newline="\n"
    )
    (fixture.package / "metadata/files.yaml").write_bytes(files_content)
    (fixture.package / "metadata/migration.yaml").write_bytes(migration_content)
    (fixture.package / "metadata/validation.json").write_bytes(validation_content)
    (fixture.package / "metadata/selected-inputs.json").write_bytes(proof_content)
    fixture.reseal()
    return {"previous_content": previous_content, "selection": selection}


def fixture_upgrade_authorities(
    fixture: PackageApplyFixture, selection: dict, previous_content: bytes
) -> tuple[dict, dict]:
    """Install credible prior authority and return a valid successor candidate pair."""
    fixture.add_target(".ai/assets/shared/example.md", previous_content)
    fixture.add_target(
        ".dev/project-config.yaml",
        yaml.safe_dump(
            {
                "validation": {
                    "routine": {
                        "argv": ["python", "-c", "print('target validation')"]
                    }
                }
            },
            sort_keys=False,
        ).encode("utf-8"),
    )
    fixture.commit_target("fixture target before initialized authority")
    previous_source = {
        "repository": "https://example.invalid/framework",
        "release_id": "REL-v0.9.0",
        "version": "v0.9.0",
        "tag": "v0.9.0",
        "commit": "c" * 40,
    }
    initialized = TARGET.initialize_context(
        fixture.target,
        previous_source,
        selection,
        "2026-08-20T10:00:00+08:00",
    )
    if initialized.get("status") != "initialized":
        raise AssertionError(f"fixture authority initialization failed: {initialized}")
    git(fixture.target, "add", ".dev/ai-context")
    fixture.commit_target("fixture initialized authority")
    candidate_source = {
        "repository": "https://example.invalid/framework",
        "release_id": "REL-v1.0.0",
        "version": "v1.0.0",
        "tag": "v1.0.0",
        "commit": "a" * 40,
    }
    candidate_provenance, candidate_ledger = TARGET.build_initialization_documents(
        candidate_source,
        selection,
        "2026-08-20T12:00:00+08:00",
    )
    candidate_provenance["previous_source"] = previous_source
    candidate_provenance["installation"]["last_upgraded_at"] = (
        "2026-08-20T12:00:00+08:00"
    )
    candidate_provenance["last_migration"] = {
        "status": "completed",
        "from_version": "v0.9.0",
        "to_version": "v1.0.0",
        "completed_at": "2026-08-20T12:00:00+08:00",
        "evidence": "tests/upgrade-finalization.md",
    }
    return candidate_provenance, candidate_ledger


def record_passed_target_validation(
    fixture: PackageApplyFixture, plan: dict
) -> dict:
    """Seal a supplied passed target validation record through the public recorder."""
    transaction = APPLY.transaction_root(fixture.target, plan["plan_sha256"])
    packet = json.loads(
        (transaction / APPLY.REMEDIATION_PACKET_PATH).read_text(encoding="utf-8")
    )
    journal = yaml.safe_load((transaction / "journal.yaml").read_text(encoding="utf-8"))
    pending_path = fixture.target / APPLY.PENDING_RECEIPT_PATH
    profile = packet["target_validation_profile"]
    validation_output = b"target validation passed\n"
    transaction_id = plan["plan_sha256"]
    evidence_path = (
        APPLY.transaction_root(fixture.target, transaction_id)
        / APPLY.TARGET_VALIDATION_OUTPUT_PATH
    )
    evidence_path.write_bytes(validation_output)
    supplied = {
        "schema_version": "target-validation-receipt/v1",
        "transaction_id": plan["plan_sha256"],
        "plan_sha256": plan["plan_sha256"],
        "packet_sha256": packet["canonical_digest"],
        "decision_sha256": journal["remediation_decision_sha256"],
        "target": {
            "root": packet["target"]["root"],
            "starting_commit": packet["target"]["starting_commit"],
            "observed_prestate_sha256": packet["target"][
                "observed_prestate_sha256"
            ],
        },
        "target_validation_profile": profile,
        "target_validation_profile_digest": packet[
            "target_validation_profile_digest"
        ],
        "pending_receipt": {
            "path": APPLY.PENDING_RECEIPT_PATH,
            "sha256": APPLY.sha256_bytes(pending_path.read_bytes()),
        },
        "execution": {
            "argv": profile["argv"],
            "outcome": "passed",
            "exit_code": 0,
            "started_at": "2026-08-20T12:00:00+08:00",
            "completed_at": "2026-08-20T12:00:01+08:00",
            "output_sha256": APPLY.sha256_bytes(validation_output),
            "evidence": (
                f".git/ai-context-package-apply/{transaction_id}/"
                f"{APPLY.TARGET_VALIDATION_OUTPUT_PATH}"
            ),
        },
    }
    supplied_path = fixture.root / "supplied-target-validation-receipt.json"
    supplied_path.write_bytes(APPLY.canonical_json_bytes(supplied))
    return APPLY.record_target_validation_receipt(
        fixture.target, plan["plan_sha256"], supplied_path
    )


def reseal_applied_transaction(
    fixture: PackageApplyFixture,
    original_plan: dict,
    mutate,
) -> tuple[Path, dict]:
    original_root = APPLY.transaction_root(fixture.target, original_plan["plan_sha256"])
    plan_path = original_root / "plan.json"
    journal_path = original_root / "journal.yaml"
    receipt_path = fixture.target / APPLY.PENDING_RECEIPT_PATH
    sealed_plan = json.loads(plan_path.read_text(encoding="utf-8"))
    journal = yaml.safe_load(journal_path.read_text(encoding="utf-8"))
    receipt = yaml.safe_load(receipt_path.read_text(encoding="utf-8"))
    sealed_plan.pop("plan_sha256")
    mutate(sealed_plan)
    transaction_id = APPLY.canonical_digest(sealed_plan)
    sealed_plan["plan_sha256"] = transaction_id
    journal["transaction_id"] = transaction_id
    journal["plan_sha256"] = transaction_id
    receipt["transaction_id"] = transaction_id
    receipt["plan_sha256"] = transaction_id
    receipt_bytes = APPLY.deterministic_yaml_bytes(receipt)
    journal["final_receipt_sha256"] = APPLY.sha256_bytes(receipt_bytes)
    plan_path.write_text(
        json.dumps(
            sealed_plan,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
        + "\n",
        encoding="utf-8",
        newline="\n",
    )
    journal_path.write_text(
        yaml.safe_dump(journal, sort_keys=True),
        encoding="utf-8",
        newline="\n",
    )
    receipt_path.write_bytes(receipt_bytes)
    new_root = original_root.with_name(transaction_id)
    original_root.replace(new_root)
    return new_root, sealed_plan


class AiContextPackageApplyGwtTests(unittest.TestCase):
    def setUp(self) -> None:
        self._prior_apply_plan = APPLY.apply_plan
        APPLY.apply_plan = apply_fixture_plan
        self.addCleanup(setattr, APPLY, "apply_plan", self._prior_apply_plan)

    def test_gwt_000_given_portable_prerequisite_runtime_when_clean_installed_then_all_shared_and_registered_assets_are_selected(self) -> None:
        fixture = PackageApplyFixture()
        try:
            registry = json.loads((ROOT / ".ai/scripts/python-entrypoints.json").read_text(encoding="utf-8"))
            paths = {
                ".ai/scripts/python-entrypoints.json",
                ".ai/scripts/python_prerequisites.py",
                ".ai/scripts/run-python-entrypoint.sh",
                ".ai/scripts/run-python-entrypoint.ps1",
                *(item["path"] for item in registry["entrypoints"] if item["portable"]),
            }
            incoming = {
                path: (path.encode("utf-8"), "framework-managed", "0644", "software-development-core")
                for path in paths
            }
            fixture.make_component_package(
                incoming,
                [operation(f"{index:03d}-add", "add", path, component_id="software-development-core") for index, path in enumerate(sorted(paths), 1)],
            )
            plan = fixture.plan()
            self.assertEqual(sorted(paths), [item["path"] for item in plan["operations"]])
            self.assertEqual({"software-development-core": 20}, plan["component_operation_counts"]["would_apply"])
        finally:
            fixture.close()
    def test_gwt_000a_given_component_archive_when_clean_installed_then_default_skips_backlog_and_cli_can_enable_it(self) -> None:
        fixture = PackageApplyFixture()
        try:
            core = operation(
                "001-core",
                "add",
                ".ai/rule.md",
                component_id="software-development-core",
            )
            backlog = operation(
                "002-backlog",
                "add",
                ".dev/backlog/README.MD",
                component_id="repo-backlog",
            )
            fixture.make_component_package(
                {
                    ".ai/rule.md": (
                        b"core\n",
                        "framework-managed",
                        "0644",
                        "software-development-core",
                    ),
                    ".dev/backlog/README.MD": (
                        b"provider\n",
                        "framework-managed",
                        "0644",
                        "repo-backlog",
                    ),
                },
                [core, backlog],
            )

            default_plan = fixture.plan()
            self.assertFalse(
                default_plan["selection"]["providers"]["repo-backlog"]["enabled"]
            )
            self.assertEqual([".ai/rule.md"], [
                item["path"] for item in default_plan["operations"]
            ])
            self.assertEqual(
                {"repo-backlog": 1},
                default_plan["component_operation_counts"]["would_skip"],
            )

            enabled_plan = APPLY.build_plan(
                fixture.package,
                fixture.target,
                enable_providers=["repo-backlog"],
            )
            self.assertEqual(
                [".ai/rule.md", ".dev/backlog/README.MD"],
                [item["path"] for item in enabled_plan["operations"]],
            )
            receipt = APPLY.apply_plan(enabled_plan)
            self.assertEqual(
                "explicit-cli-provider",
                receipt["selection_resolution"]["source"],
            )
            self.assertEqual(
                {"repo-backlog": 1, "software-development-core": 1},
                receipt["component_operation_counts"]["applied"],
            )
        finally:
            fixture.close()

    def test_gwt_000b_given_component_upgrade_without_provenance_when_planned_then_it_fails_closed(self) -> None:
        fixture = PackageApplyFixture()
        try:
            old = b"old\n"
            previous = {
                "schema_version": "2.0.0",
                "package_id": "fixture-v0.9.0",
                "files": [
                    fixture.record(
                        ".ai/rule.md",
                        old,
                        component_id="software-development-core",
                    )
                ],
            }
            fixture.previous_path = fixture.root / "previous-files.yaml"
            fixture.previous_path.write_text(
                yaml.safe_dump(previous, sort_keys=False),
                encoding="utf-8",
                newline="\n",
            )
            source = {
                "version": "0.9.0",
                "manifest_sha256": APPLY.sha256_bytes(
                    fixture.previous_path.read_bytes()
                ),
                "operations": [
                    operation(
                        "001-replace",
                        "replace",
                        ".ai/rule.md",
                        component_id="software-development-core",
                    )
                ],
            }
            fixture.make_component_package(
                {
                    ".ai/rule.md": (
                        b"new\n",
                        "framework-managed",
                        "0644",
                        "software-development-core",
                    )
                },
                [],
                [source],
            )
            fixture.add_target(".ai/rule.md", old)
            fixture.commit_target()
            with self.assertRaisesRegex(
                APPLY.ApplyError, "component-aware upgrade requires"
            ):
                fixture.plan("0.9.0")
        finally:
            fixture.close()

    def test_gwt_000c_given_provenance_disables_provider_when_upgraded_then_all_provider_operations_are_filtered(self) -> None:
        fixture = PackageApplyFixture()
        try:
            previous_records = [
                fixture.record(
                    ".ai/rule.md",
                    b"old\n",
                    component_id="software-development-core",
                ),
                fixture.record(
                    ".dev/backlog/README.MD",
                    b"old provider\n",
                    component_id="repo-backlog",
                ),
            ]
            previous = {
                "schema_version": "2.0.0",
                "package_id": "fixture-v0.9.0",
                "files": sorted(
                    previous_records, key=lambda item: item["path"].encode("utf-8")
                ),
            }
            fixture.previous_path = fixture.root / "previous-files.yaml"
            fixture.previous_path.write_text(
                yaml.safe_dump(previous, sort_keys=False),
                encoding="utf-8",
                newline="\n",
            )
            source = {
                "version": "0.9.0",
                "manifest_sha256": APPLY.sha256_bytes(
                    fixture.previous_path.read_bytes()
                ),
                "operations": [
                    operation(
                        "001-core",
                        "replace",
                        ".ai/rule.md",
                        component_id="software-development-core",
                    ),
                    operation(
                        "002-provider",
                        "replace",
                        ".dev/backlog/README.MD",
                        component_id="repo-backlog",
                    ),
                ],
            }
            fixture.make_component_package(
                {
                    ".ai/rule.md": (
                        b"new\n",
                        "framework-managed",
                        "0644",
                        "software-development-core",
                    ),
                    ".dev/backlog/README.MD": (
                        b"new provider\n",
                        "framework-managed",
                        "0644",
                        "repo-backlog",
                    ),
                },
                [],
                [source],
            )
            fixture.add_target(".ai/rule.md", b"old\n")
            fixture.add_target(".dev/backlog/README.MD", b"old provider\n")
            fixture.write_provenance(False)
            fixture.commit_target()
            plan = fixture.plan("0.9.0")
            self.assertEqual([".ai/rule.md"], [
                item["path"] for item in plan["operations"]
            ])
            self.assertEqual(
                {"repo-backlog": 1},
                plan["component_operation_counts"]["would_skip"],
            )
            APPLY.apply_plan(plan)
            self.assertEqual(
                b"old provider\n",
                (fixture.target / ".dev/backlog/README.MD").read_bytes(),
            )
        finally:
            fixture.close()

    def test_gwt_000d_given_legacy_inventory_contains_backlog_when_upgraded_then_provider_is_preserved(self) -> None:
        fixture = PackageApplyFixture()
        try:
            fixture.add_target(".dev/backlog/README.MD", b"old\n")
            fixture.commit_target()
            fixture.make_package(
                {
                    ".dev/backlog/README.MD": (
                        b"new\n",
                        "framework-managed",
                        "0644",
                    )
                },
                [
                    operation(
                        "001-provider",
                        "replace",
                        ".dev/backlog/README.MD",
                    )
                ],
                {
                    ".dev/backlog/README.MD": (
                        b"old\n",
                        "framework-managed",
                        "0644",
                    )
                },
            )
            plan = fixture.plan()
            self.assertTrue(
                plan["selection"]["providers"]["repo-backlog"]["enabled"]
            )
            self.assertEqual(
                "legacy-schema1-inventory", plan["selection_resolution"]["source"]
            )
        finally:
            fixture.close()

    def test_gwt_000e_given_dual_provenance_when_planned_then_selection_fails_closed(self) -> None:
        fixture = PackageApplyFixture()
        try:
            fixture.make_component_package({}, [])
            fixture.write_provenance(False)
            legacy = fixture.target / ".dev/AI-CONTEXT-SOURCE.yaml"
            legacy.write_text('schema_version: "1.0"\n', encoding="utf-8")
            git(fixture.target, "add", "--", ".dev/AI-CONTEXT-SOURCE.yaml")
            fixture.commit_target()
            with self.assertRaisesRegex(APPLY.ApplyError, "cannot coexist"):
                fixture.plan()
        finally:
            fixture.close()

    def test_gwt_000_given_schema_v1_upgrade_envelope_when_exact_previous_manifest_is_supplied_then_reader_compatibility_remains(self) -> None:
        fixture = PackageApplyFixture()
        try:
            # Given a legacy schema v1 package and its governed previous inventory.
            fixture.add_target(".ai/rule.md", b"old\n")
            fixture.commit_target()
            fixture.make_package(
                {".ai/rule.md": (b"new\n", "framework-managed", "0644")},
                [operation("001-replace", "replace", ".ai/rule.md")],
                {".ai/rule.md": (b"old\n", "framework-managed", "0644")},
            )
            # When the schema v1 reader plans without a schema v2 version argument.
            plan = fixture.plan()
            # Then the legacy source identity and operation remain usable.
            self.assertEqual(["replace"], [item["action"] for item in plan["operations"]])
        finally:
            fixture.close()

    def test_gwt_001_given_schema_v2_clean_install_when_planned_without_previous_identity_then_it_uses_clean_operations(self) -> None:
        fixture = PackageApplyFixture()
        try:
            # Given a v2 envelope with an independent clean-install route.
            fixture.make_package(
                {".ai/rule.md": (b"incoming\n", "framework-managed", "0644")},
                [],
            )
            fixture.make_schema_v2_migration([operation("001-clean", "add", ".ai/rule.md")], [])
            # When no previous inventory or version is supplied.
            plan = fixture.plan()
            # Then the planner selects only the clean-install operation.
            self.assertEqual(["add"], [item["action"] for item in plan["operations"]])
            self.assertFalse((fixture.target / ".ai/rule.md").exists())
        finally:
            fixture.close()

    def test_gwt_002_given_schema_v2_source_when_exact_version_and_sha_match_then_that_source_is_selected(self) -> None:
        fixture = PackageApplyFixture()
        try:
            # Given a v2 migration source bound to the governed prior manifest.
            previous = {".ai/rule.md": (b"old\n", "framework-managed", "0644")}
            fixture.add_target(".ai/rule.md", b"old\n")
            fixture.commit_target()
            fixture.make_package({".ai/rule.md": (b"new\n", "framework-managed", "0644")}, [], previous)
            assert fixture.previous_path is not None
            fixture.make_schema_v2_migration(
                [],
                [{
                    "version": "0.9.0",
                    "manifest_sha256": APPLY.sha256_bytes(fixture.previous_path.read_bytes()),
                    "operations": [operation("001-replace", "replace", ".ai/rule.md")],
                }],
            )
            # When the exact source version and manifest are supplied.
            plan = fixture.plan("0.9.0")
            # Then only the matched source is used.
            self.assertEqual(["replace"], [item["action"] for item in plan["operations"]])
        finally:
            fixture.close()

    def test_gwt_003_given_schema_v2_unknown_mismatched_or_duplicate_source_when_planned_then_it_fails_closed(self) -> None:
        fixture = PackageApplyFixture()
        try:
            # Given a v2 package with a governed prior inventory.
            previous = {".ai/rule.md": (b"old\n", "framework-managed", "0644")}
            fixture.make_package({".ai/rule.md": (b"new\n", "framework-managed", "0644")}, [], previous)
            assert fixture.previous_path is not None
            source = {
                "version": "0.9.0",
                "manifest_sha256": APPLY.sha256_bytes(fixture.previous_path.read_bytes()),
                "operations": [operation("001-replace", "replace", ".ai/rule.md")],
            }
            fixture.make_schema_v2_migration([], [source, dict(source)])
            # When the sources are ambiguous, then selection fails before target mutation.
            with self.assertRaisesRegex(APPLY.ApplyError, "duplicate|ambiguous"):
                fixture.plan("0.9.0")

            # Given one source with a different declared identity.
            fixture.make_schema_v2_migration([], [source])
            # When the caller provides an unknown version or a manifest paired with the wrong version.
            with self.assertRaisesRegex(APPLY.ApplyError, "unknown|source"):
                fixture.plan("0.8.0")
            with self.assertRaisesRegex(APPLY.ApplyError, "SHA|source|manifest"):
                wrong_manifest = fixture.root / "not-the-source.yaml"
                wrong_manifest.write_text("files: []\n", encoding="utf-8")
                APPLY.build_plan(fixture.package, fixture.target, wrong_manifest, "0.9.0")
        finally:
            fixture.close()

    def test_gwt_001_given_absent_paths_when_clean_install_is_planned_then_dry_run_binds_without_writes(self) -> None:
        fixture = PackageApplyFixture()
        try:
            # Given a clean committed target and an absent managed path.
            fixture.make_package(
                {".ai/rule.md": (b"incoming\n", "framework-managed", "0644")},
                [operation("001-add", "add", ".ai/rule.md")],
            )
            # When a dry-run plan is built.
            plan = fixture.plan()
            # Then it binds package, HEAD, and observations without writing target bytes.
            self.assertEqual("add", plan["operations"][0]["action"])
            self.assertEqual(git(fixture.target, "rev-parse", "HEAD").stdout.strip(), plan["target_starting_commit"])
            self.assertFalse((fixture.target / ".ai/rule.md").exists())
            self.assertFalse((fixture.target / ".dev/AI-CONTEXT-APPLY-PENDING.yaml").exists())
        finally:
            fixture.close()

    def test_gwt_001a_given_selected_codex_adapter_ignored_by_target_gitignore_when_planned_then_evidence_is_unresolved_and_apply_preserves_target_rule(self) -> None:
        fixture = PackageApplyFixture()
        try:
            # Given an exact selected framework-managed adapter below a target-owned ignore rule.
            ignore_path = fixture.target / ".gitignore"
            ignore_bytes = b"/.codex/**\n"
            fixture.add_target(".gitignore", ignore_bytes)
            fixture.commit_target("target ignores Codex adapters")
            path = ".codex/agents/context-translator.toml"
            fixture.make_component_package(
                {
                    path: (
                        b'name = "context-translator"\n',
                        "framework-managed",
                        "0644",
                        "software-development-core",
                    )
                },
                [
                    operation(
                        "001-add-translator",
                        "add",
                        path,
                        component_id="software-development-core",
                    )
                ],
            )

            # When dry-run preflight observes the target rule.
            plan = fixture.plan()

            # Then the plan preserves exact path/component/ownership/rule evidence and no owner choice is inferred.
            self.assertEqual("unresolved", plan["operations"][0]["action"])
            self.assertEqual(path, plan["ignored_framework_paths"][0]["path"])
            self.assertEqual(
                "software-development-core",
                plan["ignored_framework_paths"][0]["component_id"],
            )
            self.assertEqual(
                "framework-managed",
                plan["ignored_framework_paths"][0]["ownership"],
            )
            self.assertEqual(
                {"source": ".gitignore", "line": 1, "pattern": "/.codex/**"},
                plan["ignored_framework_paths"][0]["ignore_rule"],
            )
            self.assertEqual(
                [
                    "preserve-target-rule",
                    "add-narrow-exception",
                    "disable-component",
                    "pending-owner-decision",
                ],
                plan["ignored_framework_paths"][0]["owner_dispositions"],
            )
            with self.assertRaisesRegex(APPLY.ApplyError, "unresolved target Git ignore rules"):
                APPLY.apply_plan(plan)
            self.assertFalse((fixture.target / path).exists())
            self.assertFalse(
                (fixture.target / ".dev/AI-CONTEXT-APPLY-PENDING.yaml").exists()
            )
            self.assertEqual(ignore_bytes, ignore_path.read_bytes())
        finally:
            fixture.close()

    def test_gwt_001b_given_ignore_rule_with_different_case_when_planned_then_exact_path_is_not_false_positive_on_windows_or_posix(self) -> None:
        fixture = PackageApplyFixture()
        try:
            # Given a rule whose casing differs from the exact package path.
            fixture.add_target(".gitignore", b"/.CODEX/**\n")
            fixture.commit_target("target ignore casing fixture")
            git(fixture.target, "config", "core.ignorecase", "false")
            path = ".codex/agents/context-translator.toml"
            fixture.make_component_package(
                {
                    path: (
                        b'name = "context-translator"\n',
                        "framework-managed",
                        "0644",
                        "software-development-core",
                    )
                },
                [
                    operation(
                        "001-add-translator",
                        "add",
                        path,
                        component_id="software-development-core",
                    )
                ],
            )

            # When the planner evaluates the exact POSIX package identity.
            plan = fixture.plan()
            receipt = APPLY.apply_plan(plan)

            # Then an exact-case mismatch does not suppress the selected adapter on Windows or POSIX.
            self.assertEqual([], plan["ignored_framework_paths"])
            self.assertEqual("add", plan["operations"][0]["action"])
            self.assertEqual("2.0.0", receipt["schema_version"])
            self.assertEqual(path, receipt["required_framework_paths"][0]["path"])
            self.assertIsNone(TARGET.git_ignore_rule(fixture.target, path))
        finally:
            fixture.close()

    def test_gwt_001c_given_legacy_ignored_selected_path_receipt_when_target_validation_or_finalization_runs_then_both_fail_closed_and_provenance_is_preserved(self) -> None:
        fixture = PackageApplyFixture()
        try:
            # Given an initialized target with existing provenance bytes.
            path = ".codex/agents/context-translator.toml"
            source = {
                "repository": "owner/framework",
                "release_id": "REL-v1.0.0",
                "version": "v1.0.0",
                "tag": "v1.0.0",
                "commit": "a" * 40,
            }
            selection = yaml.safe_load(yaml.safe_dump(APPLY.DEFAULT_COMPONENT_SELECTION))
            TARGET.initialize_context(
                fixture.target, source, selection, "2026-08-04T21:49:30+08:00"
            )
            provenance_path = fixture.target / ".dev/ai-context/provenance.yaml"
            provenance_before = provenance_path.read_bytes()
            provenance = TARGET.load_mapping(provenance_path, [])
            ledger = TARGET.load_mapping(
                fixture.target / ".dev/ai-context/customizations.yaml", []
            )
            assert provenance is not None
            assert ledger is not None

            # And a later pending receipt identifies the same path below .git/info/exclude.
            exclude = fixture.target / ".git/info/exclude"
            exclude.write_text("/.codex/**\n", encoding="utf-8")
            managed = fixture.target / path
            managed.parent.mkdir(parents=True, exist_ok=True)
            managed_bytes = b'name = "context-translator"\n'
            managed.write_bytes(managed_bytes)
            receipt_path = fixture.target / ".dev/AI-CONTEXT-APPLY-PENDING.yaml"
            receipt_path.parent.mkdir(parents=True, exist_ok=True)
            receipt_path.write_text(
                yaml.safe_dump(
                    {
                        "schema_version": "1.1.0",
                        "status": "pending-validation",
                        "required_framework_paths": [
                            {
                                "path": path,
                                "component_id": "software-development-core",
                                "ownership": "framework-managed",
                                "sha256": APPLY.sha256_bytes(managed_bytes),
                            }
                        ],
                    },
                    sort_keys=False,
                ),
                encoding="utf-8",
                newline="\n",
            )

            # When standalone validation and provenance finalization inspect the receipt identity.
            errors = TARGET.validate_target(fixture.target)

            # Then both use the same Git ignore finding and finalization leaves prior provenance bytes intact.
            self.assertTrue(
                any(
                    "target Git ignore rule excludes framework-managed path " + path
                    in error
                    for error in errors
                ),
                errors,
            )
            with self.assertRaisesRegex(
                TARGET.TargetValidationError,
                "target Git ignore rule excludes framework-managed path",
            ):
                TARGET.finalize_context(fixture.target, provenance, ledger)
            self.assertEqual(provenance_before, provenance_path.read_bytes())
        finally:
            fixture.close()

    def test_gwt_001d_given_ignored_required_path_receipt_when_initialization_runs_then_it_stays_unresolved_without_writing_provenance(self) -> None:
        fixture = PackageApplyFixture()
        try:
            # Given a selected managed adapter whose pending receipt is hidden by the target.
            path = ".codex/agents/context-translator.toml"
            (fixture.target / ".git/info/exclude").write_text(
                "/.codex/**\n", encoding="utf-8"
            )
            managed = fixture.target / path
            managed.parent.mkdir(parents=True, exist_ok=True)
            managed_bytes = b'name = "context-translator"\n'
            managed.write_bytes(managed_bytes)
            receipt_path = fixture.target / ".dev/AI-CONTEXT-APPLY-PENDING.yaml"
            receipt_path.parent.mkdir(parents=True, exist_ok=True)
            receipt_path.write_text(
                yaml.safe_dump(
                    {
                        "schema_version": "1.1.0",
                        "status": "pending-validation",
                        "required_framework_paths": [
                            {
                                "path": path,
                                "component_id": "software-development-core",
                                "ownership": "framework-managed",
                                "sha256": APPLY.sha256_bytes(managed_bytes),
                            }
                        ],
                    },
                    sort_keys=False,
                ),
                encoding="utf-8",
                newline="\n",
            )

            # When initialization checks the pending package identity.
            result = TARGET.initialize_context(
                fixture.target,
                {
                    "repository": "owner/framework",
                    "release_id": "REL-v1.0.0",
                    "version": "v1.0.0",
                    "tag": "v1.0.0",
                    "commit": "a" * 40,
                },
                yaml.safe_load(yaml.safe_dump(APPLY.DEFAULT_COMPONENT_SELECTION)),
                "2026-08-04T21:49:30+08:00",
            )

            # Then initialization records no false completion or new provenance authority.
            self.assertEqual("unresolved", result["status"])
            self.assertEqual(
                "required-framework-managed-path-validation-failed", result["reason"]
            )
            self.assertEqual([], result["written"])
            self.assertFalse(
                (fixture.target / ".dev/ai-context/provenance.yaml").exists()
            )
        finally:
            fixture.close()

    def test_gwt_002_given_existing_seed_when_acknowledged_then_it_is_preserved_and_safe_add_applies(self) -> None:
        fixture = PackageApplyFixture()
        try:
            # Given an existing target-template plus one absent managed path.
            fixture.add_target("AGENTS.md", b"target truth\n")
            fixture.commit_target()
            fixture.make_package(
                {
                    ".ai/rule.md": (b"managed\n", "framework-managed", "0644"),
                    "AGENTS.md": (b"seed\n", "target-template", "0644"),
                },
                [
                    operation("001-managed", "add", ".ai/rule.md"),
                    operation("002-seed", "add", "AGENTS.md", "target-template"),
                ],
            )
            # When the reconcile is acknowledged and the plan is applied.
            plan = fixture.plan()
            with self.assertRaisesRegex(
                APPLY.ApplyError, "unacknowledged reconciliation items: \\['002-seed'\\]"
            ):
                APPLY.apply_plan(plan)
            receipt = APPLY.apply_plan(plan, {"002-seed"})
            # Then acknowledgement skips the seed rather than authorizing overwrite.
            self.assertEqual(b"target truth\n", (fixture.target / "AGENTS.md").read_bytes())
            self.assertEqual(b"managed\n", (fixture.target / ".ai/rule.md").read_bytes())
            self.assertEqual(["002-seed"], receipt["skipped_reconciliation_ids"])
            self.assertFalse((fixture.target / ".dev/AI-CONTEXT-SOURCE.yaml").exists())
            self.assertTrue((fixture.target / ".dev/AI-CONTEXT-APPLY-PENDING.yaml").is_file())
        finally:
            fixture.close()

    def test_gwt_003_given_unchanged_managed_base_when_upgraded_then_replace_remove_and_rename_apply(self) -> None:
        fixture = PackageApplyFixture()
        try:
            # Given managed target files match the previous hashes and modes.
            fixture.add_target(".ai/replace.md", b"old replace\n")
            fixture.add_target(".ai/remove.md", b"old remove\n")
            fixture.add_target(".ai/old-name.md", b"old name\n")
            fixture.commit_target()
            previous = {
                ".ai/old-name.md": (b"old name\n", "framework-managed", "0644"),
                ".ai/remove.md": (b"old remove\n", "framework-managed", "0644"),
                ".ai/replace.md": (b"old replace\n", "framework-managed", "0644"),
            }
            fixture.make_package(
                {
                    ".ai/new-name.md": (b"renamed incoming\n", "framework-managed", "0644"),
                    ".ai/replace.md": (b"new replace\n", "framework-managed", "0644"),
                },
                [
                    operation("001-rename", "rename", ".ai/new-name.md", from_path=".ai/old-name.md"),
                    operation("002-remove", "remove", ".ai/remove.md"),
                    operation("003-replace", "replace", ".ai/replace.md"),
                ],
                previous,
            )
            # When the upgrade is planned and applied.
            plan = fixture.plan()
            APPLY.apply_plan(plan)
            # Then only explicitly gated operations mutate the managed paths.
            self.assertEqual(["rename", "remove", "replace"], [item["action"] for item in plan["operations"]])
            self.assertFalse((fixture.target / ".ai/old-name.md").exists())
            self.assertFalse((fixture.target / ".ai/remove.md").exists())
            self.assertEqual(b"renamed incoming\n", (fixture.target / ".ai/new-name.md").read_bytes())
            self.assertEqual(b"new replace\n", (fixture.target / ".ai/replace.md").read_bytes())
        finally:
            fixture.close()

    def test_gwt_004_given_local_managed_change_when_replace_or_remove_is_planned_then_reconcile_preserves_it(self) -> None:
        fixture = PackageApplyFixture()
        try:
            # Given committed target content differs from the previous release bytes.
            fixture.add_target(".ai/remove.md", b"local remove override\n")
            fixture.add_target(".ai/replace.md", b"local replace override\n")
            fixture.commit_target()
            previous = {
                ".ai/remove.md": (b"base remove\n", "framework-managed", "0644"),
                ".ai/replace.md": (b"base replace\n", "framework-managed", "0644"),
            }
            fixture.make_package(
                {".ai/replace.md": (b"incoming\n", "framework-managed", "0644")},
                [
                    operation("001-remove", "remove", ".ai/remove.md"),
                    operation("002-replace", "replace", ".ai/replace.md"),
                ],
                previous,
            )
            # When the plan compares current hash and mode to the previous inventory.
            plan = fixture.plan()
            # Then both changes require reconciliation and remain byte-identical after acknowledgement.
            self.assertEqual(["reconcile", "reconcile"], [item["action"] for item in plan["operations"]])
            APPLY.apply_plan(plan, {"001-remove", "002-replace"})
            self.assertEqual(b"local remove override\n", (fixture.target / ".ai/remove.md").read_bytes())
            self.assertEqual(b"local replace override\n", (fixture.target / ".ai/replace.md").read_bytes())
        finally:
            fixture.close()

    def test_gwt_005_given_dirty_or_unborn_target_when_planning_then_git_gate_fails(self) -> None:
        fixture = PackageApplyFixture()
        try:
            # Given a target has an untracked change.
            fixture.make_package({}, [])
            (fixture.target / "dirty.txt").write_text("dirty", encoding="utf-8")
            # When planning starts, then it fails before classification.
            with self.assertRaisesRegex(APPLY.ApplyError, "worktree must be clean"):
                fixture.plan()
            # Given a separate repository has no committed HEAD, when planning starts, then it fails closed.
            unborn = fixture.root / "unborn"
            unborn.mkdir()
            git(unborn, "init", "-q")
            with self.assertRaisesRegex(APPLY.ApplyError, "committed HEAD"):
                APPLY.build_plan(fixture.package, unborn)
        finally:
            fixture.close()

    def test_gwt_006_given_target_changes_after_plan_when_apply_runs_then_stale_plan_is_rejected(self) -> None:
        fixture = PackageApplyFixture()
        try:
            # Given a valid plan was created against one clean target state.
            fixture.make_package(
                {".ai/rule.md": (b"incoming\n", "framework-managed", "0644")},
                [operation("001-add", "add", ".ai/rule.md")],
            )
            plan = fixture.plan()
            (fixture.target / "later.txt").write_text("changed", encoding="utf-8")
            # When apply rechecks the target, then it rejects the stale plan without writes.
            with self.assertRaisesRegex(APPLY.ApplyError, "worktree must be clean"):
                APPLY.apply_plan(plan)
            self.assertFalse((fixture.target / ".ai/rule.md").exists())
        finally:
            fixture.close()

    def test_gwt_007_given_casefold_collision_when_planning_then_portable_path_safety_fails(self) -> None:
        fixture = PackageApplyFixture()
        try:
            # Given the target owns a differently cased path.
            fixture.add_target("Rules/Policy.md", b"target\n")
            fixture.commit_target()
            fixture.make_package(
                {"rules/policy.md": (b"incoming\n", "framework-managed", "0644")},
                [operation("001-add", "add", "rules/policy.md")],
            )
            # When portable path validation runs, then the case-fold collision is rejected.
            with self.assertRaisesRegex(APPLY.ApplyError, "case-fold collision"):
                fixture.plan()
        finally:
            fixture.close()

    def test_gwt_008_given_symlink_parent_when_planning_then_escape_is_rejected(self) -> None:
        fixture = PackageApplyFixture()
        try:
            # Given a package destination is below a target symlink.
            outside = fixture.root / "outside"
            outside.mkdir()
            try:
                (fixture.target / "linked").symlink_to(outside, target_is_directory=True)
            except OSError as exc:
                self.skipTest(f"symlink creation unavailable: {exc}")
            git(fixture.target, "add", "linked")
            git(fixture.target, "commit", "-qm", "symlink fixture")
            fixture.make_package(
                {"linked/rule.md": (b"incoming\n", "framework-managed", "0644")},
                [operation("001-add", "add", "linked/rule.md")],
            )
            # When planning resolves the path boundary, then it refuses the escape.
            with self.assertRaisesRegex(APPLY.ApplyError, "symlink boundary"):
                fixture.plan()
        finally:
            fixture.close()

    def test_gwt_009_given_mid_apply_failure_when_transaction_aborts_then_all_paths_are_restored(self) -> None:
        fixture = PackageApplyFixture()
        try:
            # Given two safe additions and a simulated failure on the second write.
            fixture.make_package(
                {
                    ".ai/first.md": (b"first\n", "framework-managed", "0644"),
                    ".ai/second.md": (b"second\n", "framework-managed", "0644"),
                },
                [operation("001-first", "add", ".ai/first.md"), operation("002-second", "add", ".ai/second.md")],
            )
            plan = fixture.plan()
            original = APPLY.write_payload
            calls = 0

            def failing_write(*args, **kwargs):
                nonlocal calls
                calls += 1
                if calls == 2:
                    raise OSError("simulated write failure")
                return original(*args, **kwargs)

            APPLY.write_payload = failing_write
            # When apply fails midway, then every file and created parent is rolled back.
            try:
                with self.assertRaisesRegex(APPLY.ApplyError, "rolled back"):
                    APPLY.apply_plan(plan)
            finally:
                APPLY.write_payload = original
            self.assertFalse((fixture.target / ".ai").exists())
            self.assertFalse((fixture.target / ".dev").exists())
            self.assertEqual("", git(fixture.target, "status", "--porcelain", "--untracked-files=all").stdout)
        finally:
            fixture.close()

    def test_gwt_010_given_wrong_previous_manifest_when_upgrade_plans_then_identity_fails_closed(self) -> None:
        fixture = PackageApplyFixture()
        try:
            # Given an upgrade package whose supplied previous manifest changed after migration creation.
            fixture.make_package(
                {".ai/rule.md": (b"new\n", "framework-managed", "0644")},
                [operation("001-replace", "replace", ".ai/rule.md")],
                {".ai/rule.md": (b"old\n", "framework-managed", "0644")},
            )
            fixture.previous_path.write_text("files: []\n", encoding="utf-8")
            # When planning verifies the previous identity, then it fails before target mutation.
            with self.assertRaisesRegex(APPLY.ApplyError, "previous files manifest SHA"):
                fixture.plan()
        finally:
            fixture.close()

    def test_gwt_011_given_migration_targets_provenance_when_planning_then_reserved_path_fails_closed(self) -> None:
        fixture = PackageApplyFixture()
        try:
            # Given a malicious package attempts to install validated provenance directly.
            path = ".dev/AI-CONTEXT-SOURCE.yaml"
            fixture.make_package(
                {path: (b"source: forged\n", "framework-managed", "0644")},
                [operation("001-forged", "add", path)],
            )
            # When planning validates reserved ownership, then provenance mutation is rejected.
            with self.assertRaisesRegex(APPLY.ApplyError, "cannot manage provenance"):
                fixture.plan()
        finally:
            fixture.close()

    def test_gwt_011a_given_migration_targets_schema_2_context_state_when_planning_then_reserved_paths_fail_closed(self) -> None:
        for path in (
            ".dev/ai-context/provenance.yaml",
            ".dev/ai-context/customizations.yaml",
            ".dev/ai-context/effective-rules.yaml",
            ".dev/ai-context/effective-rule-packets/ROUTE-EXAMPLE.yaml",
        ):
            with self.subTest(path=path):
                fixture = PackageApplyFixture()
                try:
                    fixture.make_package(
                        {path: (b"target-owned: true\n", "framework-managed", "0644")},
                        [operation("001-forged", "add", path)],
                    )
                    with self.assertRaisesRegex(APPLY.ApplyError, "cannot manage provenance"):
                        fixture.plan()
                finally:
                    fixture.close()

    def test_gwt_012_given_previous_bytes_match_but_git_mode_differs_when_planned_then_it_reconciles(self) -> None:
        fixture = PackageApplyFixture()
        try:
            # Given target bytes match the base but the tracked executable mode differs.
            fixture.add_target(".ai/tool.sh", b"same bytes\n", executable=True)
            fixture.commit_target()
            fixture.make_package(
                {".ai/tool.sh": (b"incoming\n", "framework-managed", "0644")},
                [operation("001-replace", "replace", ".ai/tool.sh")],
                {".ai/tool.sh": (b"same bytes\n", "framework-managed", "0644")},
            )
            # When planning compares the governed previous state, then mode drift blocks replacement.
            plan = fixture.plan()
            self.assertEqual("reconcile", plan["operations"][0]["action"])
            self.assertIn("hash or mode", plan["operations"][0]["reason"])
        finally:
            fixture.close()

    def test_gwt_012a_given_filemode_disabled_target_with_unrepresentable_executable_bit_when_planned_then_safe_replace_applies(self) -> None:
        fixture = PackageApplyFixture()
        try:
            # Given target bytes match the executable base, but Git explicitly cannot
            # represent the executable bit on this worktree.
            git(fixture.target, "config", "core.filemode", "false")
            seed_executable_target_validation_profile(fixture)
            fixture.add_target(".ai/tool.sh", b"same bytes\n")
            fixture.commit_target()
            fixture.make_package(
                {".ai/tool.sh": (b"incoming\n", "framework-managed", "0755")},
                [operation("001-replace", "replace", ".ai/tool.sh")],
                {".ai/tool.sh": (b"same bytes\n", "framework-managed", "0755")},
            )

            # When planning and applying the governed replacement.
            plan = fixture.plan()
            receipt = APPLY.apply_plan(plan)

            # Then platform-only mode loss does not masquerade as target-owned
            # content drift, and the receipt binds the incoming bytes.
            self.assertEqual("replace", plan["operations"][0]["action"])
            self.assertEqual([], receipt["skipped_reconciliation_ids"])
            self.assertEqual(b"incoming\n", (fixture.target / ".ai/tool.sh").read_bytes())
            self.assertEqual(
                APPLY.sha256_bytes(b"incoming\n"),
                receipt["applied_artifacts"][0]["raw_sha256"],
            )
            self.assertEqual("0755", receipt["applied_artifacts"][0]["git_mode"])
            self.assertEqual("awaiting-target-validation", receipt["transaction_state"])
        finally:
            fixture.close()

    def test_gwt_013_given_unchanged_selected_managed_path_drift_when_planned_then_apply_fails_closed(self) -> None:
        fixture = PackageApplyFixture()
        try:
            path = ".ai/stable.md"
            fixture.add_target(path, b"committed target drift\n")
            fixture.commit_target()
            fixture.make_package(
                {path: (b"release bytes\n", "framework-managed", "0644")},
                [],
                {path: (b"release bytes\n", "framework-managed", "0644")},
            )

            plan = fixture.plan()
            decision = fixture_remediation_decision(plan)

            self.assertEqual([path], [item["path"] for item in plan["managed_state_conflicts"]])
            with self.assertRaisesRegex(
                APPLY.ApplyError, "approved decision cannot override unresolved package conflicts"
            ):
                APPLY.apply_plan(plan, remediation_decision=decision)
            self.assertEqual(b"committed target drift\n", (fixture.target / path).read_bytes())
        finally:
            fixture.close()

    def test_gwt_014_given_clean_autocrlf_projection_when_planned_then_git_identity_avoids_false_drift(self) -> None:
        fixture = PackageApplyFixture()
        try:
            path = ".ai/eol.md"
            git(fixture.target, "config", "core.autocrlf", "true")
            seed_executable_target_validation_profile(fixture)
            fixture.add_target(path, b"release bytes\r\n")
            fixture.commit_target()
            fixture.make_package(
                {path: (b"release bytes\n", "framework-managed", "0644")},
                [],
                {path: (b"release bytes\n", "framework-managed", "0644")},
            )

            plan = fixture.plan()
            receipt = APPLY.apply_plan(plan)

            observed = plan["observed"][path]
            self.assertNotEqual(APPLY.sha256_bytes(b"release bytes\n"), observed["sha256"])
            self.assertEqual(APPLY.sha256_bytes(b"release bytes\n"), observed["git_sha256"])
            self.assertTrue(observed["git_eol_only"])
            self.assertEqual([], plan["managed_state_conflicts"])
            self.assertEqual(
                "git-eol-canonical",
                receipt["selected_managed_path_results"][0]["match_basis"],
            )
            self.assertEqual("awaiting-target-validation", receipt["transaction_state"])
        finally:
            fixture.close()

    def test_gwt_015_given_process_death_between_operations_when_resumed_then_transaction_finalizes_once(self) -> None:
        fixture = PackageApplyFixture()
        try:
            fixture.make_package(
                {
                    ".ai/first.md": (b"first\n", "framework-managed", "0644"),
                    ".ai/second.md": (b"second\n", "framework-managed", "0644"),
                },
                [
                    operation("001-first", "add", ".ai/first.md"),
                    operation("002-second", "add", ".ai/second.md"),
                ],
            )
            plan = fixture.plan()

            def crash(boundary: str, details: dict) -> None:
                if boundary == "after_operation" and details.get("index") == 0:
                    raise APPLY.InjectedInterruption("simulated process death")

            with self.assertRaises(APPLY.InjectedInterruption):
                APPLY.apply_plan(plan, boundary_hook=crash)
            transaction_id = plan["plan_sha256"]
            _root, _saved_plan, interrupted = APPLY.load_transaction(
                fixture.target, transaction_id
            )
            self.assertEqual("applying", interrupted["state"])
            self.assertEqual(0, interrupted["next_apply_index"])
            interrupted_errors: list[str] = []
            TARGET.validate_pending_apply_receipt(fixture.target, interrupted_errors)
            self.assertTrue(
                any("package apply transaction is applying" in error for error in interrupted_errors),
                interrupted_errors,
            )

            receipt = APPLY.recover_transaction(
                fixture.target, transaction_id, "resume", fixture.package
            )
            repeated = APPLY.recover_transaction(
                fixture.target, transaction_id, "resume", fixture.package
            )

            self.assertEqual(receipt, repeated)
            self.assertEqual("finalized", receipt["transaction_state"])
            self.assertEqual(b"first\n", (fixture.target / ".ai/first.md").read_bytes())
            self.assertEqual(b"second\n", (fixture.target / ".ai/second.md").read_bytes())
            _root, _saved_plan, finalized = APPLY.load_transaction(
                fixture.target, transaction_id
            )
            self.assertEqual("finalized", finalized["state"])
            finalized_errors: list[str] = []
            TARGET.validate_pending_apply_receipt(fixture.target, finalized_errors)
            self.assertEqual([], finalized_errors)
            receipt_path = fixture.target / APPLY.PENDING_RECEIPT_PATH
            tampered = yaml.safe_load(receipt_path.read_text(encoding="utf-8"))
            tampered["package_id"] = "tampered-package"
            receipt_path.write_text(
                yaml.safe_dump(tampered, sort_keys=False),
                encoding="utf-8",
                newline="\n",
            )
            tamper_errors: list[str] = []
            TARGET.validate_pending_apply_receipt(fixture.target, tamper_errors)
            self.assertTrue(
                any("finalized receipt SHA-256 differs" in error for error in tamper_errors),
                tamper_errors,
            )
        finally:
            fixture.close()

    def test_gwt_016_given_partial_rename_when_rolled_back_then_exact_prestate_and_terminal_idempotence_hold(self) -> None:
        fixture = PackageApplyFixture()
        try:
            source = ".ai/old.md"
            destination = ".ai/new.md"
            fixture.add_target(source, b"old bytes\n")
            fixture.commit_target()
            fixture.make_package(
                {destination: (b"new bytes\n", "framework-managed", "0644")},
                [operation("001-rename", "rename", destination, from_path=source)],
                {source: (b"old bytes\n", "framework-managed", "0644")},
            )
            plan = fixture.plan()

            def crash(boundary: str, _details: dict) -> None:
                if boundary == "after_destination_replace":
                    raise APPLY.InjectedInterruption("simulated partial rename")

            with self.assertRaises(APPLY.InjectedInterruption):
                APPLY.apply_plan(plan, boundary_hook=crash)
            self.assertTrue((fixture.target / source).is_file())
            self.assertTrue((fixture.target / destination).is_file())

            transaction_id = plan["plan_sha256"]
            journal = APPLY.recover_transaction(
                fixture.target, transaction_id, "rollback"
            )
            repeated = APPLY.recover_transaction(
                fixture.target, transaction_id, "rollback"
            )

            self.assertEqual("rolled-back", journal["state"])
            self.assertEqual(journal, repeated)
            self.assertEqual(b"old bytes\n", (fixture.target / source).read_bytes())
            self.assertFalse((fixture.target / destination).exists())
            self.assertEqual(
                "", git(fixture.target, "status", "--porcelain", "--untracked-files=all").stdout
            )
        finally:
            fixture.close()

    def test_gwt_017_given_readonly_destination_when_apply_starts_then_it_fails_before_transaction_mutation(self) -> None:
        fixture = PackageApplyFixture()
        readonly = fixture.target / ".ai/readonly.md"
        try:
            fixture.add_target(".ai/readonly.md", b"old bytes\n")
            fixture.commit_target()
            fixture.make_package(
                {".ai/readonly.md": (b"new bytes\n", "framework-managed", "0644")},
                [operation("001-replace", "replace", ".ai/readonly.md")],
                {".ai/readonly.md": (b"old bytes\n", "framework-managed", "0644")},
            )
            plan = fixture.plan()
            os.chmod(readonly, 0o444)
            if readonly.stat().st_mode & 0o200:
                self.skipTest("host filesystem does not expose a readonly mode")

            with self.assertRaisesRegex(APPLY.ApplyError, "read-only"):
                APPLY.apply_plan(plan)

            self.assertEqual(b"old bytes\n", readonly.read_bytes())
            self.assertFalse(
                APPLY.transaction_root(fixture.target, plan["plan_sha256"]).exists()
            )
        finally:
            if readonly.exists():
                os.chmod(readonly, 0o644)
            fixture.close()

    def test_gwt_018_given_cli_without_apply_when_executed_then_it_remains_dry_run(self) -> None:
        fixture = PackageApplyFixture()
        try:
            # Given a package with one safe addition and the target CLI entrypoint.
            fixture.make_package(
                {".ai/rule.md": (b"incoming\n", "framework-managed", "0644")},
                [operation("001-add", "add", ".ai/rule.md")],
            )
            # When the CLI runs without the explicit --apply flag.
            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / ".ai/scripts/plan-ai-context-package-apply.py"),
                    "--package-root",
                    str(fixture.package),
                    "--target-root",
                    str(fixture.target),
                ],
                check=False,
                capture_output=True,
                text=True,
            )
            # Then it prints a dry-run plan and leaves the target untouched.
            self.assertEqual(0, result.returncode, result.stdout + result.stderr)
            self.assertIn("Dry run only", result.stdout)
            self.assertFalse((fixture.target / ".ai/rule.md").exists())
            self.assertEqual("", git(fixture.target, "status", "--porcelain", "--untracked-files=all").stdout)
        finally:
            fixture.close()

    def test_gwt_019_given_plan_output_inside_package_or_target_when_cli_runs_then_it_fails_before_writing(self) -> None:
        fixture = PackageApplyFixture()
        try:
            # Given a valid package and output paths that would invalidate the envelope or clean target.
            fixture.make_package(
                {".ai/rule.md": (b"incoming\n", "framework-managed", "0644")},
                [operation("001-add", "add", ".ai/rule.md")],
            )
            for output in (fixture.package / "plan.yaml", fixture.target / "plan.yaml"):
                # When the CLI is asked to write a plan inside either protected root.
                result = subprocess.run(
                    [
                        sys.executable,
                        str(ROOT / ".ai/scripts/plan-ai-context-package-apply.py"),
                        "--package-root",
                        str(fixture.package),
                        "--target-root",
                        str(fixture.target),
                        "--plan-output",
                        str(output),
                    ],
                    check=False,
                    capture_output=True,
                    text=True,
                )
                # Then it fails closed before creating the ungoverned file.
                self.assertEqual(1, result.returncode, result.stdout + result.stderr)
                self.assertIn("--plan-output must be outside", result.stderr)
                self.assertFalse(output.exists())
        finally:
            fixture.close()

    def test_gwt_020_given_transaction_evidence_copied_to_another_target_when_recovered_then_plan_target_mismatch_fails_before_mutation(self) -> None:
        fixture = PackageApplyFixture()
        other_target = fixture.root / "other-target"
        try:
            fixture.make_package(
                {".ai/rule.md": (b"incoming\n", "framework-managed", "0644")},
                [operation("001-add", "add", ".ai/rule.md")],
            )
            plan = fixture.plan()

            def crash(boundary: str, _details: dict) -> None:
                if boundary == "after_planned_journal":
                    raise APPLY.InjectedInterruption("retain planned transaction")

            with self.assertRaises(APPLY.InjectedInterruption):
                APPLY.apply_plan(plan, boundary_hook=crash)
            subprocess.run(
                ["git", "clone", "-q", str(fixture.target), str(other_target)],
                check=True,
                capture_output=True,
                text=True,
            )
            transaction_id = plan["plan_sha256"]
            copied_root = APPLY.transaction_root(other_target, transaction_id)
            copied_root.parent.mkdir(parents=True, exist_ok=True)
            shutil.copytree(
                APPLY.transaction_root(fixture.target, transaction_id), copied_root
            )

            for action in ("resume", "rollback"):
                with self.subTest(action=action):
                    with self.assertRaisesRegex(
                        APPLY.ApplyError,
                        "transaction target root does not match recovery target",
                    ):
                        APPLY.recover_transaction(
                            other_target,
                            transaction_id,
                            action,
                            fixture.package if action == "resume" else None,
                        )
            self.assertFalse((fixture.target / ".ai/rule.md").exists())
            self.assertFalse((other_target / ".ai/rule.md").exists())
        finally:
            fixture.close()

    def test_gwt_021_given_process_death_during_transaction_preparation_when_retried_then_complete_journal_publishes_without_a_wedge(self) -> None:
        for failed_boundary in (
            "after_preparation_root",
            "after_preparation_plan",
            "after_preparation_backup",
            "after_preparation_journal",
        ):
            with self.subTest(boundary=failed_boundary):
                fixture = PackageApplyFixture()
                try:
                    seed_executable_target_validation_profile(fixture)
                    fixture.add_target(".ai/rule.md", b"previous\n")
                    fixture.commit_target()
                    fixture.make_package(
                        {
                            ".ai/rule.md": (
                                b"incoming\n",
                                "framework-managed",
                                "0644",
                            )
                        },
                        [operation("001-replace", "replace", ".ai/rule.md")],
                        {
                            ".ai/rule.md": (
                                b"previous\n",
                                "framework-managed",
                                "0644",
                            )
                        },
                    )
                    plan = fixture.plan()

                    def crash(boundary: str, _details: dict) -> None:
                        if boundary == failed_boundary:
                            raise APPLY.InjectedInterruption(
                                f"process died at {failed_boundary}"
                            )

                    with self.assertRaises(APPLY.InjectedInterruption):
                        APPLY.apply_plan(plan, boundary_hook=crash)
                    transaction_id = plan["plan_sha256"]
                    final_root = APPLY.transaction_root(
                        fixture.target, transaction_id
                    )
                    self.assertFalse(final_root.exists())
                    self.assertEqual(b"previous\n", (fixture.target / ".ai/rule.md").read_bytes())
                    self.assertTrue(
                        list(
                            final_root.parent.glob(
                                f".{transaction_id}.preparing-*"
                            )
                        )
                    )

                    receipt = APPLY.apply_plan(plan)

                    self.assertEqual(
                        "awaiting-target-validation", receipt["transaction_state"]
                    )
                    self.assertTrue((final_root / "journal.yaml").is_file())
                    self.assertEqual(
                        b"incoming\n", (fixture.target / ".ai/rule.md").read_bytes()
                    )
                finally:
                    fixture.close()

    def test_gwt_022_given_windows_source_removal_when_journal_can_advance_then_write_through_move_precedes_unlink(self) -> None:
        fixture = PackageApplyFixture()
        try:
            source = fixture.root / "delete-me.txt"
            source.write_bytes(b"content\n")
            transaction_root = fixture.root / "transaction"
            transaction_root.mkdir()
            calls: list[tuple[Path, Path, int]] = []

            def move(source_path: Path, destination_path: Path, flags: int) -> None:
                calls.append((source_path, destination_path, flags))
                os.replace(source_path, destination_path)

            with mock.patch.object(APPLY.os, "name", "nt"), mock.patch.object(
                APPLY, "windows_move_path", side_effect=move
            ):
                APPLY.durable_unlink(source, transaction_root)

            self.assertFalse(source.exists())
            self.assertEqual(1, len(calls))
            self.assertEqual(APPLY.WINDOWS_MOVEFILE_WRITE_THROUGH, calls[0][2])
            self.assertEqual(transaction_root / "deleted", calls[0][1].parent)
        finally:
            fixture.close()

    def test_gwt_023_given_process_death_at_each_apply_boundary_when_resumed_then_transaction_finalizes_exactly_once(self) -> None:
        boundaries = (
            "after_planned_journal",
            "after_applying_journal",
            "after_destination_replace",
            "after_operation",
            "after_progress_journal",
            "after_source_remove",
            "after_receipt",
            "after_finalized_journal",
        )
        for failed_boundary in boundaries:
            with self.subTest(boundary=failed_boundary):
                fixture = PackageApplyFixture()
                try:
                    is_remove = failed_boundary == "after_source_remove"
                    expected_transaction_state = (
                        "awaiting-target-validation" if is_remove else "finalized"
                    )
                    if is_remove:
                        seed_executable_target_validation_profile(fixture)
                        fixture.add_target(".ai/rule.md", b"previous\n")
                        fixture.commit_target()
                        fixture.make_package(
                            {},
                            [operation("001-remove", "remove", ".ai/rule.md")],
                            {
                                ".ai/rule.md": (
                                    b"previous\n",
                                    "framework-managed",
                                    "0644",
                                )
                            },
                        )
                    else:
                        fixture.make_package(
                            {
                                ".ai/rule.md": (
                                    b"incoming\n",
                                    "framework-managed",
                                    "0644",
                                )
                            },
                            [operation("001-add", "add", ".ai/rule.md")],
                        )
                    plan = fixture.plan()

                    def crash(boundary: str, _details: dict) -> None:
                        if boundary == failed_boundary:
                            raise APPLY.InjectedInterruption(
                                f"process died at {failed_boundary}"
                            )

                    with self.assertRaises(APPLY.InjectedInterruption):
                        APPLY.apply_plan(plan, boundary_hook=crash)
                    transaction_id = plan["plan_sha256"]

                    receipt = APPLY.recover_transaction(
                        fixture.target, transaction_id, "resume", fixture.package
                    )
                    repeated = APPLY.recover_transaction(
                        fixture.target, transaction_id, "resume", fixture.package
                    )

                    self.assertEqual(receipt, repeated)
                    self.assertEqual(
                        expected_transaction_state, receipt["transaction_state"]
                    )
                    if is_remove:
                        self.assertFalse((fixture.target / ".ai/rule.md").exists())
                    else:
                        self.assertEqual(
                            b"incoming\n",
                            (fixture.target / ".ai/rule.md").read_bytes(),
                        )
                finally:
                    fixture.close()

    def test_gwt_024_given_process_death_at_each_rollback_boundary_when_retried_then_exact_prestate_is_terminal(self) -> None:
        for failed_boundary in (
            "after_rollback_start_journal",
            "after_rollback_restore",
            "after_rollback_progress_journal",
            "after_rollback_journal",
        ):
            with self.subTest(boundary=failed_boundary):
                fixture = PackageApplyFixture()
                try:
                    fixture.make_package(
                        {
                            ".ai/rule.md": (
                                b"incoming\n",
                                "framework-managed",
                                "0644",
                            )
                        },
                        [operation("001-add", "add", ".ai/rule.md")],
                    )
                    plan = fixture.plan()

                    def interrupt_apply(boundary: str, _details: dict) -> None:
                        if boundary == "after_destination_replace":
                            raise APPLY.InjectedInterruption("partial add")

                    with self.assertRaises(APPLY.InjectedInterruption):
                        APPLY.apply_plan(plan, boundary_hook=interrupt_apply)
                    transaction_id = plan["plan_sha256"]

                    def interrupt_rollback(boundary: str, _details: dict) -> None:
                        if boundary == failed_boundary:
                            raise APPLY.InjectedInterruption(
                                f"process died at {failed_boundary}"
                            )

                    with self.assertRaises(APPLY.InjectedInterruption):
                        APPLY.recover_transaction(
                            fixture.target,
                            transaction_id,
                            "rollback",
                            boundary_hook=interrupt_rollback,
                        )
                    journal = APPLY.recover_transaction(
                        fixture.target, transaction_id, "rollback"
                    )
                    repeated = APPLY.recover_transaction(
                        fixture.target, transaction_id, "rollback"
                    )

                    self.assertEqual("rolled-back", journal["state"])
                    self.assertEqual(journal, repeated)
                    self.assertFalse((fixture.target / ".ai/rule.md").exists())
                    self.assertEqual(
                        "",
                        git(
                            fixture.target,
                            "status",
                            "--porcelain",
                            "--untracked-files=all",
                        ).stdout,
                    )
                finally:
                    fixture.close()

    def test_gwt_025_given_mixed_key_pending_receipt_when_resumed_then_ambiguity_fails_closed(self) -> None:
        fixture = PackageApplyFixture()
        try:
            fixture.make_package(
                {
                    ".ai/rule.md": (
                        b"incoming\n",
                        "framework-managed",
                        "0644",
                    )
                },
                [operation("001-add", "add", ".ai/rule.md")],
            )
            plan = fixture.plan()

            def crash(boundary: str, _details: dict) -> None:
                if boundary == "after_receipt":
                    raise APPLY.InjectedInterruption("receipt persisted")

            with self.assertRaises(APPLY.InjectedInterruption):
                APPLY.apply_plan(plan, boundary_hook=crash)
            receipt_path = fixture.target / APPLY.PENDING_RECEIPT_PATH
            receipt_path.write_text(
                "1: attacker\nschema_version: apply-receipt/v2\n",
                encoding="utf-8",
            )

            with self.assertRaisesRegex(
                APPLY.ApplyError,
                "pending receipt is ambiguous after interruption",
            ):
                APPLY.recover_transaction(
                    fixture.target,
                    plan["plan_sha256"],
                    "resume",
                    fixture.package,
                )

            self.assertEqual(
                "1: attacker\nschema_version: apply-receipt/v2\n",
                receipt_path.read_text(encoding="utf-8"),
            )
            journal = yaml.safe_load(
                (
                    APPLY.transaction_root(fixture.target, plan["plan_sha256"])
                    / "journal.yaml"
                ).read_text(encoding="utf-8")
            )
            self.assertEqual("applying", journal["state"])
            self.assertIsNone(journal["final_receipt_sha256"])
        finally:
            fixture.close()

    def test_gwt_026_given_windows_cross_volume_tombstone_when_removed_then_it_fails_before_move(self) -> None:
        fixture = PackageApplyFixture()
        try:
            source = fixture.root / "delete-me.txt"
            source.write_bytes(b"content\n")
            transaction_root = fixture.root / "transaction"
            transaction_root.mkdir()
            tombstone_root = transaction_root / "deleted"
            original_stat = Path.stat

            def different_volume(path: Path, *args: object, **kwargs: object) -> object:
                if path == source:
                    return mock.Mock(st_dev=1)
                if path == tombstone_root:
                    return mock.Mock(st_dev=2)
                return original_stat(path, *args, **kwargs)

            with mock.patch.object(APPLY.os, "name", "nt"), mock.patch.object(
                Path, "stat", autospec=True, side_effect=different_volume
            ), mock.patch.object(APPLY, "windows_move_path") as move:
                with self.assertRaisesRegex(
                    APPLY.ApplyError,
                    "cannot durably remove a target path across Windows volumes",
                ):
                    APPLY.durable_unlink(source, transaction_root)

            move.assert_not_called()
            self.assertEqual(b"content\n", source.read_bytes())
        finally:
            fixture.close()

    def test_gwt_027_given_windows_tombstone_cleanup_failure_when_recovered_then_resume_and_rollback_are_idempotent(self) -> None:
        for recovery_action in ("resume", "rollback"):
            with self.subTest(action=recovery_action):
                fixture = PackageApplyFixture()
                try:
                    seed_executable_target_validation_profile(fixture)
                    fixture.add_target(".ai/rule.md", b"previous\n")
                    fixture.commit_target()
                    fixture.make_package(
                        {},
                        [operation("001-remove", "remove", ".ai/rule.md")],
                        {
                            ".ai/rule.md": (
                                b"previous\n",
                                "framework-managed",
                                "0644",
                            )
                        },
                    )
                    plan = fixture.plan()
                    original_durable_unlink = APPLY.durable_unlink
                    original_unlink = Path.unlink

                    def move(source_path: Path, destination_path: Path, _flags: int) -> None:
                        os.replace(source_path, destination_path)

                    def retain_tombstone(path: Path, *args: object, **kwargs: object) -> None:
                        if path.suffix == ".deleted":
                            raise PermissionError("retained for recovery")
                        original_unlink(path, *args, **kwargs)

                    def crash(boundary: str, _details: dict) -> None:
                        if boundary == "after_source_remove":
                            raise APPLY.InjectedInterruption("source removal persisted")

                    def windows_durable_unlink(
                        path: Path, transaction_root_path: Path
                    ) -> None:
                        with mock.patch.object(
                            APPLY.os, "name", "nt"
                        ), mock.patch.object(
                            APPLY, "windows_move_path", side_effect=move
                        ), mock.patch.object(
                            Path,
                            "unlink",
                            autospec=True,
                            side_effect=retain_tombstone,
                        ):
                            original_durable_unlink(path, transaction_root_path)

                    with mock.patch.object(
                        APPLY,
                        "durable_unlink",
                        side_effect=windows_durable_unlink,
                    ):
                        with self.assertRaises(APPLY.InjectedInterruption):
                            APPLY.apply_plan(plan, boundary_hook=crash)

                    root = APPLY.transaction_root(fixture.target, plan["plan_sha256"])
                    tombstones = list((root / "deleted").glob("*.deleted"))
                    self.assertEqual(1, len(tombstones))
                    self.assertFalse((fixture.target / ".ai/rule.md").exists())

                    recovered = APPLY.recover_transaction(
                        fixture.target,
                        plan["plan_sha256"],
                        recovery_action,
                        fixture.package if recovery_action == "resume" else None,
                    )
                    repeated = APPLY.recover_transaction(
                        fixture.target,
                        plan["plan_sha256"],
                        recovery_action,
                        fixture.package if recovery_action == "resume" else None,
                    )

                    self.assertEqual(recovered, repeated)
                    if recovery_action == "resume":
                        self.assertEqual(
                            "awaiting-target-validation",
                            recovered["transaction_state"],
                        )
                        self.assertFalse((fixture.target / ".ai/rule.md").exists())
                    else:
                        self.assertEqual("rolled-back", recovered["state"])
                        self.assertEqual(
                            b"previous\n",
                            (fixture.target / ".ai/rule.md").read_bytes(),
                        )
                    self.assertTrue(tombstones[0].is_file())
                finally:
                    fixture.close()

    def test_gwt_028_given_target_template_add_when_fresh_process_rolls_back_then_package_independent_prestate_is_restored(self) -> None:
        for failed_boundary in ("after_destination_replace", "after_progress_journal"):
            with self.subTest(boundary=failed_boundary):
                fixture = PackageApplyFixture()
                try:
                    fixture.make_package(
                        {
                            "AGENTS.md": (
                                b"target template\n",
                                "target-template",
                                "0644",
                            )
                        },
                        [
                            operation(
                                "001-add",
                                "add",
                                "AGENTS.md",
                                ownership="target-template",
                            )
                        ],
                    )
                    plan = fixture.plan()
                    self.assertEqual(
                        {
                            "exists": True,
                            "sha256": APPLY.sha256_bytes(b"target template\n"),
                            "mode": "0644",
                        },
                        plan["operation_post_states"][0]["paths"][0]["state"],
                    )

                    def crash(boundary: str, _details: dict) -> None:
                        if boundary == failed_boundary:
                            raise APPLY.InjectedInterruption(
                                f"process died at {failed_boundary}"
                            )

                    with self.assertRaises(APPLY.InjectedInterruption):
                        APPLY.apply_plan(plan, boundary_hook=crash)
                    transaction_id = plan["plan_sha256"]
                    command = [
                        sys.executable,
                        str(ROOT / ".ai/scripts/plan-ai-context-package-apply.py"),
                        "--target-root",
                        str(fixture.target),
                        "--rollback",
                        transaction_id,
                    ]

                    rolled_back = subprocess.run(
                        command,
                        check=False,
                        capture_output=True,
                        text=True,
                    )
                    repeated = subprocess.run(
                        command,
                        check=False,
                        capture_output=True,
                        text=True,
                    )

                    self.assertEqual(
                        0, rolled_back.returncode, rolled_back.stdout + rolled_back.stderr
                    )
                    self.assertEqual(
                        0, repeated.returncode, repeated.stdout + repeated.stderr
                    )
                    self.assertFalse((fixture.target / "AGENTS.md").exists())
                    _root, _plan, journal = APPLY.load_transaction(
                        fixture.target, transaction_id
                    )
                    self.assertEqual("rolled-back", journal["state"])
                    self.assertEqual(
                        "",
                        git(
                            fixture.target,
                            "status",
                            "--porcelain",
                            "--untracked-files=all",
                        ).stdout,
                    )
                finally:
                    fixture.close()

    def test_gwt_029_given_corrupt_journal_progress_when_recovered_then_it_fails_before_mutation(self) -> None:
        corruptions = (
            {"next_apply_index": -1},
            {"next_apply_index": True},
            {"next_apply_index": "1"},
            {"next_apply_index": 3},
            {"next_apply_index": 1, "completed_operation_ids": []},
            {"next_apply_index": 1, "completed_operation_ids": ["002-add"]},
            {
                "state": "planned",
                "next_apply_index": 1,
                "completed_operation_ids": ["001-add"],
            },
            {
                "state": "finalized",
                "next_apply_index": 2,
                "completed_operation_ids": ["001-add", "002-add"],
                "final_receipt_sha256": None,
            },
            {"state": "interrupted", "final_receipt_sha256": "0" * 64},
        )
        for corruption in corruptions:
            with self.subTest(corruption=corruption):
                fixture = PackageApplyFixture()
                try:
                    fixture.make_package(
                        {
                            ".ai/one.md": (b"one\n", "framework-managed", "0644"),
                            ".ai/two.md": (b"two\n", "framework-managed", "0644"),
                        },
                        [
                            operation("001-add", "add", ".ai/one.md"),
                            operation("002-add", "add", ".ai/two.md"),
                        ],
                    )
                    plan = fixture.plan()

                    def crash(boundary: str, _details: dict) -> None:
                        if boundary == "after_planned_journal":
                            raise APPLY.InjectedInterruption("planned transaction")

                    with self.assertRaises(APPLY.InjectedInterruption):
                        APPLY.apply_plan(plan, boundary_hook=crash)
                    root = APPLY.transaction_root(fixture.target, plan["plan_sha256"])
                    journal_path = root / "journal.yaml"
                    journal = yaml.safe_load(journal_path.read_text(encoding="utf-8"))
                    journal.update(corruption)
                    journal_path.write_text(
                        yaml.safe_dump(journal, sort_keys=True),
                        encoding="utf-8",
                    )
                    before = journal_path.read_bytes()

                    with self.assertRaises(APPLY.ApplyError):
                        APPLY.recover_transaction(
                            fixture.target,
                            plan["plan_sha256"],
                            "rollback",
                        )

                    self.assertEqual(before, journal_path.read_bytes())
                    self.assertFalse((fixture.target / ".ai/one.md").exists())
                    self.assertFalse((fixture.target / ".ai/two.md").exists())
                finally:
                    fixture.close()

    def test_gwt_030_given_completed_remove_or_rename_prefix_with_restored_source_when_resumed_then_false_finalization_is_rejected(self) -> None:
        for action in ("remove", "rename"):
            with self.subTest(action=action):
                fixture = PackageApplyFixture()
                try:
                    fixture.add_target(".ai/source.md", b"previous\n")
                    fixture.commit_target()
                    incoming = (
                        {}
                        if action == "remove"
                        else {
                            ".ai/destination.md": (
                                b"incoming\n",
                                "framework-managed",
                                "0644",
                            )
                        }
                    )
                    operation_record = (
                        operation("001-remove", "remove", ".ai/source.md")
                        if action == "remove"
                        else operation(
                            "001-rename",
                            "rename",
                            ".ai/destination.md",
                            from_path=".ai/source.md",
                        )
                    )
                    fixture.make_package(
                        incoming,
                        [operation_record],
                        {
                            ".ai/source.md": (
                                b"previous\n",
                                "framework-managed",
                                "0644",
                            )
                        },
                    )
                    plan = fixture.plan()

                    def crash(boundary: str, details: dict) -> None:
                        if boundary == "after_progress_journal" and details["index"] == 0:
                            raise APPLY.InjectedInterruption("durable prefix persisted")

                    with self.assertRaises(APPLY.InjectedInterruption):
                        APPLY.apply_plan(plan, boundary_hook=crash)
                    (fixture.target / ".ai/source.md").write_bytes(b"previous\n")
                    transaction_id = plan["plan_sha256"]

                    for recovery_action in ("resume", "rollback"):
                        with self.assertRaisesRegex(
                            APPLY.ApplyError,
                            "target state does not match transaction progress",
                        ):
                            APPLY.recover_transaction(
                                fixture.target,
                                transaction_id,
                                recovery_action,
                                fixture.package if recovery_action == "resume" else None,
                            )

                    _root, _plan, journal = APPLY.load_transaction(
                        fixture.target, transaction_id
                    )
                    self.assertEqual("applying", journal["state"])
                    self.assertIsNone(journal["final_receipt_sha256"])
                    self.assertFalse(
                        (fixture.target / APPLY.PENDING_RECEIPT_PATH).exists()
                    )
                finally:
                    fixture.close()

    def test_gwt_031_given_persisted_operation_prefix_when_recovered_then_resume_and_rollback_are_idempotent(self) -> None:
        for recovery_action in ("resume", "rollback"):
            with self.subTest(action=recovery_action):
                fixture = PackageApplyFixture()
                try:
                    fixture.make_package(
                        {
                            ".ai/one.md": (b"one\n", "framework-managed", "0644"),
                            ".ai/two.md": (b"two\n", "framework-managed", "0644"),
                        },
                        [
                            operation("001-add", "add", ".ai/one.md"),
                            operation("002-add", "add", ".ai/two.md"),
                        ],
                    )
                    plan = fixture.plan()

                    def crash(boundary: str, details: dict) -> None:
                        if boundary == "after_progress_journal" and details["index"] == 0:
                            raise APPLY.InjectedInterruption("durable prefix persisted")

                    with self.assertRaises(APPLY.InjectedInterruption):
                        APPLY.apply_plan(plan, boundary_hook=crash)
                    transaction_id = plan["plan_sha256"]
                    _root, _plan, journal = APPLY.load_transaction(
                        fixture.target, transaction_id
                    )
                    self.assertEqual(1, journal["next_apply_index"])
                    self.assertEqual(["001-add"], journal["completed_operation_ids"])

                    recovered = APPLY.recover_transaction(
                        fixture.target,
                        transaction_id,
                        recovery_action,
                        fixture.package if recovery_action == "resume" else None,
                    )
                    repeated = APPLY.recover_transaction(
                        fixture.target,
                        transaction_id,
                        recovery_action,
                        fixture.package if recovery_action == "resume" else None,
                    )

                    self.assertEqual(recovered, repeated)
                    if recovery_action == "resume":
                        self.assertEqual("finalized", recovered["transaction_state"])
                        self.assertEqual(b"one\n", (fixture.target / ".ai/one.md").read_bytes())
                        self.assertEqual(b"two\n", (fixture.target / ".ai/two.md").read_bytes())
                    else:
                        self.assertEqual("rolled-back", recovered["state"])
                        self.assertFalse((fixture.target / ".ai/one.md").exists())
                        self.assertFalse((fixture.target / ".ai/two.md").exists())
                finally:
                    fixture.close()

    def test_gwt_032_given_persisted_apply_prefix_when_rollback_dies_after_restore_then_fresh_process_continues_exactly(self) -> None:
        for failed_boundary in (
            "after_rollback_restore",
            "after_rollback_progress_journal",
        ):
            with self.subTest(boundary=failed_boundary):
                fixture = PackageApplyFixture()
                try:
                    fixture.make_package(
                        {
                            ".ai/one.md": (b"one\n", "framework-managed", "0644"),
                            ".ai/two.md": (b"two\n", "framework-managed", "0644"),
                        },
                        [
                            operation("001-add", "add", ".ai/one.md"),
                            operation("002-add", "add", ".ai/two.md"),
                        ],
                    )
                    plan = fixture.plan()

                    def crash_apply(boundary: str, details: dict) -> None:
                        if boundary == "after_progress_journal" and details["index"] == 0:
                            raise APPLY.InjectedInterruption(
                                "durable apply prefix persisted"
                            )

                    with self.assertRaises(APPLY.InjectedInterruption):
                        APPLY.apply_plan(plan, boundary_hook=crash_apply)
                    transaction_id = plan["plan_sha256"]

                    def crash_rollback(boundary: str, details: dict) -> None:
                        if (
                            boundary == failed_boundary
                            and details.get("path") == ".ai/one.md"
                        ):
                            raise APPLY.InjectedInterruption(
                                f"rollback died at {failed_boundary}"
                            )

                    with self.assertRaises(APPLY.InjectedInterruption):
                        APPLY.recover_transaction(
                            fixture.target,
                            transaction_id,
                            "rollback",
                            boundary_hook=crash_rollback,
                        )
                    _root, _plan, interrupted = APPLY.load_transaction(
                        fixture.target, transaction_id
                    )
                    self.assertEqual("rolling-back", interrupted["state"])
                    self.assertEqual(
                        (
                            [".ai/two.md"]
                            if failed_boundary == "after_rollback_restore"
                            else [".ai/two.md", ".ai/one.md"]
                        ),
                        interrupted["rollback_completed_paths"],
                    )

                    command = [
                        sys.executable,
                        str(ROOT / ".ai/scripts/plan-ai-context-package-apply.py"),
                        "--target-root",
                        str(fixture.target),
                        "--rollback",
                        transaction_id,
                    ]
                    recovered = subprocess.run(
                        command, check=False, capture_output=True, text=True
                    )
                    repeated = subprocess.run(
                        command, check=False, capture_output=True, text=True
                    )

                    self.assertEqual(
                        0, recovered.returncode, recovered.stdout + recovered.stderr
                    )
                    self.assertEqual(
                        0, repeated.returncode, repeated.stdout + repeated.stderr
                    )
                    self.assertFalse((fixture.target / ".ai/one.md").exists())
                    self.assertFalse((fixture.target / ".ai/two.md").exists())
                    finalized = yaml.safe_load(
                        (_root / "journal.yaml").read_text(encoding="utf-8")
                    )
                    self.assertEqual("rolled-back", finalized["state"])
                    self.assertEqual(
                        [".ai/two.md", ".ai/one.md"],
                        finalized["rollback_completed_paths"],
                    )
                finally:
                    fixture.close()

    def test_gwt_033_given_finalized_journal_progress_corruption_when_target_validates_then_provenance_gate_fails_closed(self) -> None:
        corruptions = (
            {"next_apply_index": 0},
            {"next_apply_index": 2.0},
            {"completed_operation_ids": []},
            {"operation_order_sha256": "0" * 64},
            {"transition_sequence": 3},
            {"transition_sequence": 5},
            {"rollback_next_index": 1},
            {"rollback_next_index": False},
        )
        for corruption in corruptions:
            with self.subTest(corruption=corruption):
                fixture = PackageApplyFixture()
                try:
                    fixture.make_package(
                        {
                            ".ai/one.md": (b"one\n", "framework-managed", "0644"),
                            ".ai/two.md": (b"two\n", "framework-managed", "0644"),
                        },
                        [
                            operation("001-add", "add", ".ai/one.md"),
                            operation("002-add", "add", ".ai/two.md"),
                        ],
                    )
                    plan = fixture.plan()
                    APPLY.apply_plan(plan)
                    root = APPLY.transaction_root(
                        fixture.target, plan["plan_sha256"]
                    )
                    journal_path = root / "journal.yaml"
                    journal = yaml.safe_load(
                        journal_path.read_text(encoding="utf-8")
                    )
                    journal.update(corruption)
                    journal_path.write_text(
                        yaml.safe_dump(journal, sort_keys=True),
                        encoding="utf-8",
                        newline="\n",
                    )

                    errors: list[str] = []
                    TARGET.validate_pending_apply_receipt(fixture.target, errors)

                    self.assertTrue(
                        any(
                            "finalized transaction progress is invalid" in error
                            for error in errors
                        ),
                        errors,
                    )
                    if "transition_sequence" in corruption:
                        with self.assertRaisesRegex(
                            APPLY.ApplyError,
                            "transaction journal transition sequence is impossible",
                        ):
                            APPLY.recover_transaction(
                                fixture.target,
                                plan["plan_sha256"],
                                "resume",
                                fixture.package,
                            )
                finally:
                    fixture.close()

    def test_gwt_033a_given_exact_v5_finalized_or_validated_sequences_when_recovered_and_target_validates_then_both_pass(self) -> None:
        for scenario in ("clean-finalized", "upgrade-validated"):
            with self.subTest(scenario=scenario):
                fixture = PackageApplyFixture()
                try:
                    if scenario == "clean-finalized":
                        fixture.make_package(
                            {".ai/rule.md": (b"incoming\n", "framework-managed", "0644")},
                            [operation("001-add", "add", ".ai/rule.md")],
                        )
                        plan = fixture.plan()
                        receipt = APPLY.apply_plan(plan)
                        expected_state = "finalized"
                        expected_sequence = len(APPLY.active_operations(plan)) + 2
                    else:
                        package = make_schema_23_upgrade_package(fixture)
                        candidate_provenance, candidate_ledger = fixture_upgrade_authorities(
                            fixture, package["selection"], package["previous_content"]
                        )
                        plan = fixture.plan("0.9.0")
                        receipt = APPLY.apply_plan(
                            plan,
                            remediation_decision=fixture_remediation_decision(
                                plan,
                                candidate_provenance=candidate_provenance,
                                candidate_ledger=candidate_ledger,
                            ),
                        )
                        record_passed_target_validation(fixture, plan)
                        expected_state = "validated"
                        expected_sequence = len(APPLY.active_operations(plan)) + 3

                    root = APPLY.transaction_root(fixture.target, plan["plan_sha256"])
                    journal = yaml.safe_load((root / "journal.yaml").read_text(encoding="utf-8"))
                    self.assertEqual(expected_state, journal["state"])
                    self.assertEqual(expected_sequence, journal["transition_sequence"])
                    self.assertEqual(
                        receipt,
                        APPLY.recover_transaction(
                            fixture.target,
                            plan["plan_sha256"],
                            "resume",
                            fixture.package,
                        ),
                    )
                    errors: list[str] = []
                    TARGET.validate_pending_apply_receipt(
                        fixture.target,
                        errors,
                        enforce_terminal_invariants=scenario == "clean-finalized",
                    )
                    self.assertEqual([], errors)
                    if scenario == "upgrade-validated":
                        finalization = TARGET.finalize_context(
                            fixture.target, candidate_provenance, candidate_ledger
                        )
                        finalized = yaml.safe_load(
                            (root / "journal.yaml").read_text(encoding="utf-8")
                        )
                        self.assertEqual("finalized", finalization["status"])
                        self.assertEqual("finalized", finalized["state"])
                        self.assertEqual(
                            len(APPLY.active_operations(plan)) + 4,
                            finalized["transition_sequence"],
                        )
                        errors = []
                        TARGET.validate_pending_apply_receipt(fixture.target, errors)
                        self.assertEqual([], errors)
                finally:
                    fixture.close()

    def test_gwt_034_given_resealed_unsupported_plan_or_post_state_when_target_validates_then_provenance_gate_fails_closed(self) -> None:
        variants = (
            "unsupported-schema",
            "operations-not-list",
            "add-declared-absent",
            "remove-exists-integer-zero",
            "rename-source-exists-integer-zero",
        )
        for variant in variants:
            with self.subTest(variant=variant):
                fixture = PackageApplyFixture()
                try:
                    if variant == "remove-exists-integer-zero":
                        fixture.add_target(".ai/one.md", b"one\n")
                        fixture.commit_target()
                        fixture.make_package(
                            {},
                            [operation("001-remove", "remove", ".ai/one.md")],
                            {
                                ".ai/one.md": (
                                    b"one\n",
                                    "framework-managed",
                                    "0644",
                                )
                            },
                        )
                    elif variant == "rename-source-exists-integer-zero":
                        fixture.add_target(".ai/old.md", b"old\n")
                        fixture.commit_target()
                        fixture.make_package(
                            {
                                ".ai/new.md": (
                                    b"new\n",
                                    "framework-managed",
                                    "0644",
                                )
                            },
                            [
                                operation(
                                    "001-rename",
                                    "rename",
                                    ".ai/new.md",
                                    from_path=".ai/old.md",
                                )
                            ],
                            {
                                ".ai/old.md": (
                                    b"old\n",
                                    "framework-managed",
                                    "0644",
                                )
                            },
                        )
                    else:
                        fixture.make_package(
                            {
                                ".ai/one.md": (
                                    b"one\n",
                                    "framework-managed",
                                    "0644",
                                )
                            },
                            [operation("001-add", "add", ".ai/one.md")],
                        )
                    original_plan = fixture.plan()
                    APPLY.apply_plan(original_plan)
                    original_id = original_plan["plan_sha256"]
                    original_root = APPLY.transaction_root(
                        fixture.target, original_id
                    )
                    plan_path = original_root / "plan.json"
                    journal_path = original_root / "journal.yaml"
                    receipt_path = fixture.target / APPLY.PENDING_RECEIPT_PATH
                    sealed_plan = json.loads(plan_path.read_text(encoding="utf-8"))
                    journal = yaml.safe_load(journal_path.read_text(encoding="utf-8"))
                    receipt = yaml.safe_load(receipt_path.read_text(encoding="utf-8"))
                    sealed_plan.pop("plan_sha256")
                    if variant == "unsupported-schema":
                        sealed_plan["schema_version"] = "2.0.0"
                    elif variant == "operations-not-list":
                        sealed_plan["operations"] = None
                    elif variant == "remove-exists-integer-zero":
                        sealed_plan["operation_post_states"][0]["paths"][0][
                            "state"
                        ] = {"exists": 0, "sha256": None, "mode": None}
                    elif variant == "rename-source-exists-integer-zero":
                        sealed_plan["operation_post_states"][0]["paths"][1][
                            "state"
                        ] = {"exists": 0, "sha256": None, "mode": None}
                    else:
                        sealed_plan["operation_post_states"][0]["paths"][0][
                            "state"
                        ] = {"exists": False, "sha256": None, "mode": None}
                    if variant in {
                        "remove-exists-integer-zero",
                        "rename-source-exists-integer-zero",
                    }:
                        with self.assertRaisesRegex(
                            APPLY.ApplyError,
                            "absent post-state identity is invalid",
                        ):
                            APPLY.operation_post_state_map(sealed_plan)
                    transaction_id = APPLY.canonical_digest(sealed_plan)
                    sealed_plan["plan_sha256"] = transaction_id
                    journal["transaction_id"] = transaction_id
                    journal["plan_sha256"] = transaction_id
                    receipt["transaction_id"] = transaction_id
                    receipt["plan_sha256"] = transaction_id
                    receipt_bytes = APPLY.deterministic_yaml_bytes(receipt)
                    journal["final_receipt_sha256"] = APPLY.sha256_bytes(
                        receipt_bytes
                    )
                    plan_path.write_text(
                        json.dumps(
                            sealed_plan,
                            ensure_ascii=False,
                            sort_keys=True,
                            separators=(",", ":"),
                        )
                        + "\n",
                        encoding="utf-8",
                        newline="\n",
                    )
                    journal_path.write_text(
                        yaml.safe_dump(journal, sort_keys=True),
                        encoding="utf-8",
                        newline="\n",
                    )
                    receipt_path.write_bytes(receipt_bytes)
                    new_root = original_root.with_name(transaction_id)
                    original_root.replace(new_root)

                    errors: list[str] = []
                    TARGET.validate_pending_apply_receipt(fixture.target, errors)

                    self.assertTrue(
                        any(
                            "sealed transaction post-state evidence is invalid"
                            in error
                            for error in errors
                        ),
                        errors,
                    )
                finally:
                    fixture.close()

    def test_gwt_035_given_windows_existing_destination_when_atomically_replaced_then_supported_write_through_move_is_used(self) -> None:
        with tempfile.TemporaryDirectory(prefix="ai-context-atomic-replace-") as temporary:
            root = Path(temporary)
            staged = root / "staged.tmp"
            destination = root / "journal.yaml"
            staged.write_bytes(b"new\n")
            destination.write_bytes(b"old\n")
            observed: list[tuple[Path, Path, int]] = []

            def move(source: Path, target: Path, flags: int) -> None:
                observed.append((source, target, flags))
                os.replace(source, target)

            with mock.patch.object(APPLY.os, "name", "nt"), mock.patch.object(
                APPLY, "windows_move_path", side_effect=move
            ):
                APPLY.atomic_replace(staged, destination)

            self.assertEqual(b"new\n", destination.read_bytes())
            self.assertEqual(
                [(staged, destination, 0x9)],
                observed,
            )
            self.assertEqual(0x9, APPLY.WINDOWS_ATOMIC_REPLACE_FLAGS)

    def test_gwt_036_given_resealed_malformed_operations_when_target_validates_then_exact_schema_fails_closed(self) -> None:
        variants = (
            "missing-kind",
            "kind-action-mismatch",
            "unknown-component",
            "extra-field",
            "unsorted-identifiers",
            "forbidden-ownership",
            "forbidden-from-path",
            "reserved-effective-path",
            "reserved-effective-packet-root",
            "duplicate-touched-path",
        )
        for variant in variants:
            with self.subTest(variant=variant):
                fixture = PackageApplyFixture()
                try:
                    fixture.make_package(
                        {
                            ".ai/one.md": (b"one\n", "framework-managed", "0644"),
                            ".ai/two.md": (b"two\n", "framework-managed", "0644"),
                        },
                        [
                            operation("001-add", "add", ".ai/one.md"),
                            operation("002-add", "add", ".ai/two.md"),
                        ],
                    )
                    plan = fixture.plan()
                    APPLY.apply_plan(plan)

                    def mutate(sealed: dict) -> None:
                        operations = sealed["operations"]
                        if variant == "missing-kind":
                            operations[0].pop("kind")
                        elif variant == "kind-action-mismatch":
                            operations[0]["kind"] = "remove"
                        elif variant == "unknown-component":
                            operations[0]["component_id"] = "not-selected"
                        elif variant == "extra-field":
                            operations[0]["unexpected"] = True
                        elif variant == "unsorted-identifiers":
                            operations.reverse()
                        elif variant == "forbidden-ownership":
                            operations[0]["ownership"] = "target-owned"
                        elif variant == "forbidden-from-path":
                            operations[0]["from_path"] = ".ai/source.md"
                        elif variant == "reserved-effective-path":
                            operations[0]["path"] = TARGET.EFFECTIVE_STATE_PATH
                        elif variant == "reserved-effective-packet-root":
                            operations[0]["path"] = TARGET.EFFECTIVE_PACKET_DIRECTORY
                        else:
                            operations[1]["path"] = operations[0]["path"]

                    reseal_applied_transaction(fixture, plan, mutate)
                    errors: list[str] = []
                    TARGET.validate_pending_apply_receipt(fixture.target, errors)

                    self.assertTrue(
                        any(
                            "sealed transaction operation evidence is invalid" in error
                            for error in errors
                        ),
                        errors,
                    )
                finally:
                    fixture.close()

    def test_gwt_037_given_copied_target_or_changed_head_when_finalized_then_target_binding_fails_before_provenance_write(self) -> None:
        for variant in ("different-root", "changed-head"):
            with self.subTest(variant=variant):
                fixture = PackageApplyFixture()
                try:
                    fixture.make_package(
                        {".ai/one.md": (b"one\n", "framework-managed", "0644")},
                        [operation("001-add", "add", ".ai/one.md")],
                    )
                    plan = fixture.plan()
                    APPLY.apply_plan(plan)
                    if variant == "different-root":
                        reseal_applied_transaction(
                            fixture,
                            plan,
                            lambda sealed: sealed.__setitem__(
                                "target_root", str(fixture.root / "different-target")
                            ),
                        )
                        expected = "sealed target root differs from current target"
                    else:
                        (fixture.target / "HEAD-DRIFT.md").write_text(
                            "drift\n", encoding="utf-8"
                        )
                        git(fixture.target, "add", "HEAD-DRIFT.md")
                        git(fixture.target, "commit", "-qm", "head drift")
                        expected = "sealed target starting commit differs from current HEAD"

                    errors: list[str] = []
                    TARGET.validate_pending_apply_receipt(fixture.target, errors)
                    self.assertTrue(any(expected in error for error in errors), errors)
                    provenance_path = fixture.target / ".dev/ai-context/provenance.yaml"
                    with self.assertRaisesRegex(TARGET.TargetValidationError, expected):
                        TARGET.finalize_context(fixture.target, {}, {})
                    self.assertFalse(provenance_path.exists())
                finally:
                    fixture.close()

    def test_gwt_038_given_managed_path_reparse_parent_when_target_validates_then_external_bytes_are_not_authoritative(self) -> None:
        fixture = PackageApplyFixture()
        try:
            fixture.make_package(
                {
                    ".ai/linked/managed.md": (
                        b"managed\n",
                        "framework-managed",
                        "0644",
                    )
                },
                [operation("001-add", "add", ".ai/linked/managed.md")],
            )
            plan = fixture.plan()
            APPLY.apply_plan(plan)
            blocked_parent = fixture.target / ".ai/linked"
            original = TARGET.is_reparse_point

            def simulated_reparse(path: Path) -> bool:
                return Path(path) == blocked_parent or original(path)

            errors: list[str] = []
            with mock.patch.object(
                TARGET, "is_reparse_point", side_effect=simulated_reparse
            ):
                TARGET.validate_pending_apply_receipt(fixture.target, errors)

            self.assertTrue(
                any("crosses a symlink or reparse boundary" in error for error in errors),
                errors,
            )
            outside = fixture.root / "outside-linked"
            try:
                blocked_parent.replace(outside)
                blocked_parent.symlink_to(outside, target_is_directory=True)
            except OSError:
                if outside.exists() and not blocked_parent.exists():
                    outside.replace(blocked_parent)
            else:
                actual_errors: list[str] = []
                TARGET.validate_pending_apply_receipt(
                    fixture.target, actual_errors
                )
                self.assertTrue(
                    any(
                        "crosses a symlink or reparse boundary" in error
                        for error in actual_errors
                    ),
                    actual_errors,
                )
        finally:
            fixture.close()

    def test_gwt_039_given_dangling_pending_receipt_boundary_when_rollback_runs_then_terminal_state_is_refused(self) -> None:
        fixture = PackageApplyFixture()
        try:
            fixture.make_package(
                {".ai/one.md": (b"one\n", "framework-managed", "0644")},
                [operation("001-add", "add", ".ai/one.md")],
            )
            plan = fixture.plan()

            def crash(boundary: str, details: dict) -> None:
                if boundary == "after_progress_journal":
                    raise APPLY.InjectedInterruption("preserve apply prefix")

            with self.assertRaises(APPLY.InjectedInterruption):
                APPLY.apply_plan(plan, boundary_hook=crash)
            receipt_path = fixture.target / APPLY.PENDING_RECEIPT_PATH
            transaction_id = plan["plan_sha256"]

            receipt_path.parent.mkdir(parents=True, exist_ok=True)
            receipt_path.write_bytes(b"unbound: receipt\n")
            journal_path = (
                APPLY.transaction_root(fixture.target, transaction_id)
                / "journal.yaml"
            )
            journal_before = journal_path.read_bytes()
            with self.assertRaisesRegex(
                APPLY.ApplyError, "pending receipt does not match rollback transaction"
            ):
                APPLY.recover_transaction(fixture.target, transaction_id, "rollback")
            self.assertEqual(b"unbound: receipt\n", receipt_path.read_bytes())
            self.assertEqual(journal_before, journal_path.read_bytes())
            self.assertTrue((fixture.target / ".ai/one.md").is_file())
            receipt_path.unlink()

            receipt_parent = fixture.target / ".dev"
            with mock.patch.object(
                APPLY,
                "is_reparse_point",
                side_effect=lambda path: Path(path) == receipt_parent,
            ):
                with self.assertRaisesRegex(
                    APPLY.ApplyError,
                    "symlink boundary or reparse-point boundary is not allowed",
                ):
                    APPLY.recover_transaction(
                        fixture.target, transaction_id, "rollback"
                    )
            self.assertEqual(journal_before, journal_path.read_bytes())
            self.assertTrue((fixture.target / ".ai/one.md").is_file())

            with mock.patch.object(
                APPLY,
                "is_reparse_point",
                side_effect=lambda path: Path(path) == receipt_path,
            ):
                with self.assertRaisesRegex(
                    APPLY.ApplyError,
                    "symlink boundary or reparse-point boundary is not allowed",
                ):
                    APPLY.recover_transaction(
                        fixture.target, transaction_id, "rollback"
                    )
            self.assertTrue((fixture.target / ".ai/one.md").is_file())

            recovered = APPLY.recover_transaction(
                fixture.target, transaction_id, "rollback"
            )
            self.assertEqual("rolled-back", recovered["state"])
            with mock.patch.object(
                APPLY,
                "is_reparse_point",
                side_effect=lambda path: Path(path) == receipt_path,
            ):
                with self.assertRaisesRegex(
                    APPLY.ApplyError,
                    "symlink boundary or reparse-point boundary is not allowed",
                ):
                    APPLY.recover_transaction(
                        fixture.target, transaction_id, "rollback"
                    )
        finally:
            fixture.close()

    def test_gwt_040_given_exact_receipt_published_before_final_journal_when_rollback_runs_then_only_bound_receipt_is_removed(self) -> None:
        fixture = PackageApplyFixture()
        try:
            fixture.make_package(
                {".ai/one.md": (b"one\n", "framework-managed", "0644")},
                [operation("001-add", "add", ".ai/one.md")],
            )
            plan = fixture.plan()

            def crash(boundary: str, details: dict) -> None:
                if boundary == "after_receipt":
                    raise APPLY.InjectedInterruption(
                        "receipt published before finalized journal"
                    )

            with self.assertRaises(APPLY.InjectedInterruption):
                APPLY.apply_plan(plan, boundary_hook=crash)
            receipt_path = fixture.target / APPLY.PENDING_RECEIPT_PATH
            self.assertTrue(receipt_path.is_file())

            recovered = APPLY.recover_transaction(
                fixture.target, plan["plan_sha256"], "rollback"
            )

            self.assertEqual("rolled-back", recovered["state"])
            self.assertFalse(receipt_path.exists())
            self.assertFalse((fixture.target / ".ai/one.md").exists())
        finally:
            fixture.close()

    def test_gwt_041_given_target_changes_during_preparation_when_transaction_is_admitted_then_new_state_is_never_adopted(self) -> None:
        for boundary in ("after_preparation_backup", "after_planned_journal"):
            for variant in ("dirty-edit", "head-drift", "exact-post"):
                with self.subTest(boundary=boundary, variant=variant):
                    fixture = PackageApplyFixture()
                    try:
                        seed_executable_target_validation_profile(fixture)
                        fixture.add_target(".ai/one.md", b"old\n")
                        fixture.commit_target()
                        fixture.make_package(
                            {".ai/one.md": (b"new\n", "framework-managed", "0644")},
                            [operation("001-replace", "replace", ".ai/one.md")],
                            previous={
                                ".ai/one.md": (b"old\n", "framework-managed", "0644")
                            },
                        )
                        plan = fixture.plan("0.9.0")

                        def mutate(observed_boundary: str, _details: dict) -> None:
                            if observed_boundary != boundary:
                                return
                            path = fixture.target / ".ai/one.md"
                            path.write_bytes(
                                b"new\n" if variant == "exact-post" else b"concurrent\n"
                            )
                            if variant == "head-drift":
                                git(fixture.target, "add", ".ai/one.md")
                                git(fixture.target, "commit", "-qm", "concurrent head drift")

                        with self.assertRaises(APPLY.ApplyError):
                            APPLY.apply_plan(plan, boundary_hook=mutate)

                        self.assertEqual(
                            b"new\n" if variant == "exact-post" else b"concurrent\n",
                            (fixture.target / ".ai/one.md").read_bytes(),
                        )
                        transaction_root = APPLY.transaction_root(
                            fixture.target, plan["plan_sha256"]
                        )
                        self.assertEqual(
                            boundary == "after_planned_journal",
                            transaction_root.exists(),
                        )
                        if transaction_root.exists():
                            journal = yaml.safe_load(
                                (transaction_root / "journal.yaml").read_text(
                                    encoding="utf-8"
                                )
                            )
                            self.assertEqual("planned", journal["state"])
                            self.assertEqual(0, journal["next_apply_index"])
                            self.assertEqual(0, journal["transition_sequence"])
                            self.assertIsNone(journal["last_error"])
                        self.assertFalse(
                            (fixture.target / APPLY.PENDING_RECEIPT_PATH).exists()
                        )
                        if (
                            boundary == "after_planned_journal"
                            and variant == "exact-post"
                        ):
                            (fixture.target / ".ai/one.md").write_bytes(b"old\n")
                            receipt = APPLY.recover_transaction(
                                fixture.target,
                                plan["plan_sha256"],
                                "resume",
                                package_root=fixture.package,
                            )
                            self.assertEqual(
                                "awaiting-target-validation",
                                receipt["transaction_state"],
                            )
                    finally:
                        fixture.close()

    def test_gwt_042_given_process_death_after_target_staging_fsync_when_resumed_then_only_journal_bound_staging_is_collected(self) -> None:
        fixture = PackageApplyFixture()
        try:
            fixture.make_package(
                {".ai/one.md": (b"one\n", "framework-managed", "0644")},
                [operation("001-add", "add", ".ai/one.md")],
            )
            plan = fixture.plan()
            staging_record = next(
                item
                for item in APPLY.target_staging_records(plan)
                if item["destination"] == ".ai/one.md"
            )
            staging_path = fixture.target / staging_record["path"]

            def crash(boundary: str, details: dict) -> None:
                if (
                    boundary == "after_target_staging_fsync"
                    and details.get("destination") == ".ai/one.md"
                    and details.get("purpose") == "apply"
                ):
                    raise APPLY.InjectedInterruption("simulated hard process death")

            with self.assertRaises(APPLY.InjectedInterruption):
                APPLY.apply_plan(plan, boundary_hook=crash)

            self.assertTrue(staging_path.is_file())
            self.assertEqual(b"one\n", staging_path.read_bytes())
            self.assertFalse((fixture.target / ".ai/one.md").exists())
            journal_path = (
                APPLY.transaction_root(fixture.target, plan["plan_sha256"])
                / "journal.yaml"
            )
            journal_before_rejected_resume = journal_path.read_bytes()

            with self.assertRaises(APPLY.ApplyError):
                APPLY.recover_transaction(
                    fixture.target,
                    plan["plan_sha256"],
                    "resume",
                    package_root=fixture.root / "wrong-package",
                )

            self.assertTrue(staging_path.is_file())
            self.assertEqual(b"one\n", staging_path.read_bytes())
            self.assertEqual(
                journal_before_rejected_resume, journal_path.read_bytes()
            )
            self.assertFalse((fixture.target / ".ai/one.md").exists())

            verify_package_binding = APPLY.verify_package_binding

            def mutate_after_package_binding(
                sealed_plan: dict, package_root: Path
            ) -> tuple[dict, dict[str, dict], dict, str]:
                binding = verify_package_binding(sealed_plan, package_root)
                destination = fixture.target / ".ai/one.md"
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_bytes(b"concurrent\n")
                return binding

            with mock.patch.object(
                APPLY,
                "verify_package_binding",
                side_effect=mutate_after_package_binding,
            ), self.assertRaisesRegex(
                APPLY.ApplyError, "target state does not match transaction progress"
            ):
                APPLY.recover_transaction(
                    fixture.target,
                    plan["plan_sha256"],
                    "resume",
                    package_root=fixture.package,
                )

            self.assertTrue(staging_path.is_file())
            self.assertEqual(b"one\n", staging_path.read_bytes())
            self.assertEqual(
                journal_before_rejected_resume, journal_path.read_bytes()
            )
            self.assertEqual(
                b"concurrent\n", (fixture.target / ".ai/one.md").read_bytes()
            )
            (fixture.target / ".ai/one.md").unlink()

            receipt = APPLY.recover_transaction(
                fixture.target,
                plan["plan_sha256"],
                "resume",
                package_root=fixture.package,
            )

            self.assertEqual("finalized", receipt["transaction_state"])
            self.assertFalse(staging_path.exists())
            self.assertEqual(
                b"one\n", (fixture.target / ".ai/one.md").read_bytes()
            )
        finally:
            fixture.close()

    def test_gwt_043_given_finalized_transaction_with_retained_staging_when_target_validates_then_finalization_fails_closed(self) -> None:
        fixture = PackageApplyFixture()
        try:
            fixture.make_package(
                {".ai/one.md": (b"one\n", "framework-managed", "0644")},
                [operation("001-add", "add", ".ai/one.md")],
            )
            plan = fixture.plan()
            APPLY.apply_plan(plan)
            staging_record = next(
                item
                for item in APPLY.target_staging_records(plan)
                if item["destination"] == ".ai/one.md"
            )
            staging_path = fixture.target / staging_record["path"]
            staging_path.write_bytes(b"retained\n")

            errors: list[str] = []
            TARGET.validate_pending_apply_receipt(fixture.target, errors)

            self.assertTrue(
                any("transaction staging path remains" in error for error in errors),
                errors,
            )
            with self.assertRaisesRegex(
                TARGET.TargetValidationError, "transaction staging path remains"
            ):
                TARGET.finalize_context(fixture.target, {}, {})
        finally:
            fixture.close()

    def test_gwt_044_given_process_death_during_receipt_staging_when_resumed_then_receipt_is_rebuilt_from_sealed_state(self) -> None:
        fixture = PackageApplyFixture()
        try:
            fixture.make_package(
                {".ai/one.md": (b"one\n", "framework-managed", "0644")},
                [operation("001-add", "add", ".ai/one.md")],
            )
            plan = fixture.plan()
            staging_record = next(
                item
                for item in APPLY.target_staging_records(plan)
                if item["destination"] == APPLY.PENDING_RECEIPT_PATH
            )
            staging_path = fixture.target / staging_record["path"]

            def crash(boundary: str, details: dict) -> None:
                if (
                    boundary == "after_target_staging_fsync"
                    and details.get("purpose") == "receipt"
                ):
                    raise APPLY.InjectedInterruption("receipt staging interrupted")

            with self.assertRaises(APPLY.InjectedInterruption):
                APPLY.apply_plan(plan, boundary_hook=crash)

            self.assertTrue(staging_path.is_file())
            receipt_path = fixture.target / APPLY.PENDING_RECEIPT_PATH
            self.assertFalse(receipt_path.exists())
            journal_path = (
                APPLY.transaction_root(fixture.target, plan["plan_sha256"])
                / "journal.yaml"
            )
            journal_before_rejected_resume = journal_path.read_bytes()
            receipt_path.write_bytes(b"unbound receipt\n")

            with self.assertRaisesRegex(
                APPLY.ApplyError, "pending receipt is ambiguous after interruption"
            ):
                APPLY.recover_transaction(
                    fixture.target,
                    plan["plan_sha256"],
                    "resume",
                    package_root=fixture.package,
                )

            self.assertTrue(staging_path.is_file())
            self.assertEqual(b"unbound receipt\n", receipt_path.read_bytes())
            self.assertEqual(
                journal_before_rejected_resume, journal_path.read_bytes()
            )
            receipt_path.unlink()

            receipt = APPLY.recover_transaction(
                fixture.target,
                plan["plan_sha256"],
                "resume",
                package_root=fixture.package,
            )

            self.assertEqual("finalized", receipt["transaction_state"])
            self.assertFalse(staging_path.exists())
            self.assertTrue(
                (fixture.target / APPLY.PENDING_RECEIPT_PATH).is_file()
            )
        finally:
            fixture.close()

    def test_gwt_045_given_process_death_during_rollback_staging_when_rollback_retries_then_prestate_is_restored(self) -> None:
        fixture = PackageApplyFixture()
        try:
            fixture.add_target(".ai/one.md", b"old\n")
            fixture.commit_target()
            fixture.make_package(
                {".ai/one.md": (b"new\n", "framework-managed", "0644")},
                [operation("001-replace", "replace", ".ai/one.md")],
                previous={
                    ".ai/one.md": (b"old\n", "framework-managed", "0644")
                },
            )
            plan = fixture.plan("0.9.0")

            def stop_after_apply(boundary: str, details: dict) -> None:
                if boundary == "after_progress_journal":
                    raise APPLY.InjectedInterruption("retain applied prefix")

            with self.assertRaises(APPLY.InjectedInterruption):
                APPLY.apply_plan(plan, boundary_hook=stop_after_apply)

            staging_record = next(
                item
                for item in APPLY.target_staging_records(plan)
                if item["destination"] == ".ai/one.md"
            )
            staging_path = fixture.target / staging_record["path"]

            def crash_rollback(boundary: str, details: dict) -> None:
                if (
                    boundary == "after_target_staging_fsync"
                    and details.get("purpose") == "rollback"
                ):
                    raise APPLY.InjectedInterruption("rollback staging interrupted")

            with self.assertRaises(APPLY.InjectedInterruption):
                APPLY.recover_transaction(
                    fixture.target,
                    plan["plan_sha256"],
                    "rollback",
                    boundary_hook=crash_rollback,
                )

            self.assertTrue(staging_path.is_file())
            self.assertEqual(
                b"new\n", (fixture.target / ".ai/one.md").read_bytes()
            )
            receipt_path = fixture.target / APPLY.PENDING_RECEIPT_PATH
            receipt_path.parent.mkdir(parents=True, exist_ok=True)
            receipt_path.write_bytes(b"unbound receipt\n")
            journal_path = (
                APPLY.transaction_root(fixture.target, plan["plan_sha256"])
                / "journal.yaml"
            )
            journal_before_rejected_rollback = journal_path.read_bytes()

            with self.assertRaisesRegex(
                APPLY.ApplyError,
                "rolling-back transaction still has a pending receipt",
            ):
                APPLY.recover_transaction(
                    fixture.target, plan["plan_sha256"], "rollback"
                )

            self.assertTrue(staging_path.is_file())
            self.assertEqual(
                b"new\n", (fixture.target / ".ai/one.md").read_bytes()
            )
            self.assertEqual(
                b"unbound receipt\n", receipt_path.read_bytes()
            )
            self.assertEqual(
                journal_before_rejected_rollback, journal_path.read_bytes()
            )
            receipt_path.unlink()

            recovered = APPLY.recover_transaction(
                fixture.target, plan["plan_sha256"], "rollback"
            )

            self.assertEqual("rolled-back", recovered["state"])
            self.assertFalse(staging_path.exists())
            self.assertEqual(
                b"old\n", (fixture.target / ".ai/one.md").read_bytes()
            )
        finally:
            fixture.close()

    def test_gwt_046_given_upgrade_without_owner_decision_when_apply_then_no_target_mutation_is_authorized(self) -> None:
        fixture = PackageApplyFixture()
        try:
            fixture.add_target(".ai/managed.md", b"old\n")
            fixture.commit_target()
            fixture.make_package(
                {".ai/managed.md": (b"new\n", "framework-managed", "0644")},
                [operation("001-replace", "replace", ".ai/managed.md")],
                previous={
                    ".ai/managed.md": (b"old\n", "framework-managed", "0644")
                },
            )
            plan = fixture.plan("0.9.0")

            with self.assertRaisesRegex(
                APPLY.ApplyError, "requires an explicit approved remediation decision"
            ):
                RAW_APPLY_PLAN(plan)

            self.assertEqual(b"old\n", (fixture.target / ".ai/managed.md").read_bytes())
            self.assertFalse(
                APPLY.transaction_root(fixture.target, plan["plan_sha256"]).exists()
            )
        finally:
            fixture.close()

    def test_gwt_047_given_rejected_upgrade_decision_when_apply_then_packet_report_and_decision_are_retained(self) -> None:
        fixture = PackageApplyFixture()
        try:
            fixture.add_target(".ai/managed.md", b"local owner change\n")
            fixture.commit_target()
            fixture.make_package(
                {".ai/managed.md": (b"new\n", "framework-managed", "0644")},
                [operation("001-replace", "replace", ".ai/managed.md")],
                previous={
                    ".ai/managed.md": (b"old\n", "framework-managed", "0644")
                },
            )
            plan = fixture.plan("0.9.0")
            decision = fixture_remediation_decision(plan, "rejected")

            with self.assertRaisesRegex(APPLY.ApplyError, "rejected by owner decision"):
                APPLY.apply_plan(plan, remediation_decision=decision)

            root = APPLY.transaction_root(fixture.target, plan["plan_sha256"])
            journal = yaml.safe_load((root / "journal.yaml").read_text(encoding="utf-8"))
            self.assertEqual("rejected", journal["state"])
            self.assertTrue((root / APPLY.REMEDIATION_PACKET_PATH).is_file())
            self.assertTrue((root / APPLY.REMEDIATION_DECISION_PATH).is_file())
            report = (root / APPLY.REMEDIATION_REPORT_PATH).read_text(encoding="utf-8")
            self.assertEqual(
                f"derived_from_packet_digest: {decision['packet_sha256']}",
                report.splitlines()[0],
            )
            _root, loaded_plan, loaded_journal = APPLY.load_transaction(
                fixture.target, plan["plan_sha256"]
            )
            self.assertEqual(plan, loaded_plan)
            self.assertEqual("rejected", loaded_journal["state"])
            self.assertEqual(
                b"local owner change\n",
                (fixture.target / ".ai/managed.md").read_bytes(),
            )
            self.assertFalse(
                (fixture.target / APPLY.PENDING_RECEIPT_PATH).exists()
            )
        finally:
            fixture.close()

    def test_gwt_048_given_approved_upgrade_decision_when_apply_then_artifacts_precede_target_mutation_and_are_bound(self) -> None:
        fixture = PackageApplyFixture()
        try:
            fixture.add_target(".ai/managed.md", b"old\n")
            fixture.commit_target()
            fixture.make_package(
                {".ai/managed.md": (b"new\n", "framework-managed", "0644")},
                [operation("001-replace", "replace", ".ai/managed.md")],
                previous={
                    ".ai/managed.md": (b"old\n", "framework-managed", "0644")
                },
            )
            plan = fixture.plan("0.9.0")
            decision = fixture_remediation_decision(plan)
            observed_before_write: list[bool] = []

            def assert_prewrite_artifacts(boundary: str, _details: dict) -> None:
                if boundary != "after_planned_journal":
                    return
                root = APPLY.transaction_root(fixture.target, plan["plan_sha256"])
                observed_before_write.append(
                    all(
                        (root / relative).is_file()
                        for relative in (
                            APPLY.REMEDIATION_PACKET_PATH,
                            APPLY.REMEDIATION_REPORT_PATH,
                            APPLY.REMEDIATION_DECISION_PATH,
                            APPLY.INCOMING_VALIDATION_RECEIPT_PATH,
                        )
                    )
                    and (fixture.target / ".ai/managed.md").read_bytes() == b"old\n"
                )

            receipt = APPLY.apply_plan(
                plan,
                boundary_hook=assert_prewrite_artifacts,
                remediation_decision=decision,
            )

            root = APPLY.transaction_root(fixture.target, plan["plan_sha256"])
            journal = yaml.safe_load((root / "journal.yaml").read_text(encoding="utf-8"))
            self.assertEqual([True], observed_before_write)
            self.assertEqual(
                "awaiting-target-validation", receipt["transaction_state"]
            )
            self.assertEqual("awaiting-target-validation", journal["state"])
            self.assertEqual(plan["target_observed_prestate_sha256"], journal["target_observed_prestate_sha256"])
            self.assertTrue(
                isinstance(journal["incoming_validation_receipt_sha256"], str)
            )
            self.assertEqual(b"new\n", (fixture.target / ".ai/managed.md").read_bytes())
        finally:
            fixture.close()

    def test_gwt_049_given_schema_23_upgrade_and_passed_target_validation_when_finalized_then_terminal_receipt_is_idempotent(self) -> None:
        fixture = PackageApplyFixture()
        try:
            package = make_schema_23_upgrade_package(fixture)
            candidate_provenance, candidate_ledger = fixture_upgrade_authorities(
                fixture, package["selection"], package["previous_content"]
            )
            plan = fixture.plan("0.9.0")
            self.assertTrue(plan["upgrade_remediation_required"])
            self.assertEqual("passed", plan["incoming_package_validation"]["execution"]["outcome"])
            decision = fixture_remediation_decision(
                plan,
                candidate_provenance=candidate_provenance,
                candidate_ledger=candidate_ledger,
            )

            APPLY.apply_plan(plan, remediation_decision=decision)
            record_passed_target_validation(fixture, plan)
            transaction_id = plan["plan_sha256"]
            supplied_receipt = fixture.root / "supplied-target-validation-receipt.json"
            managed_path = fixture.target / ".ai/assets/shared/example.md"
            managed_before_cli = managed_path.read_bytes()
            record_cli = [
                sys.executable,
                str(ROOT / ".ai/scripts/plan-ai-context-package-apply.py"),
                "--target-root",
                str(fixture.target),
                "--record-target-validation-receipt",
                transaction_id,
                "--target-validation-receipt",
                str(supplied_receipt),
            ]
            cli_result = subprocess.run(record_cli, capture_output=True, text=True)
            self.assertEqual(0, cli_result.returncode, cli_result.stderr)
            self.assertEqual(managed_before_cli, managed_path.read_bytes())
            invalid_cli = subprocess.run(
                [*record_cli, "--package-root", str(fixture.package)],
                capture_output=True,
                text=True,
            )
            self.assertNotEqual(0, invalid_cli.returncode)
            self.assertIn("does not accept --package-root", invalid_cli.stderr)
            first = TARGET.finalize_context(
                fixture.target, candidate_provenance, candidate_ledger
            )
            transaction = APPLY.transaction_root(fixture.target, plan["plan_sha256"])
            terminal = transaction / TARGET.TERMINAL_RECEIPT_PATH
            terminal_bytes = terminal.read_bytes()

            second = TARGET.finalize_context(
                fixture.target, candidate_provenance, candidate_ledger
            )

            self.assertEqual("finalized", first["status"])
            self.assertEqual(first["terminal_receipt"], second["terminal_receipt"])
            self.assertEqual(terminal_bytes, terminal.read_bytes())
            _root, _plan, finalized_journal = APPLY.load_transaction(
                fixture.target, transaction_id
            )
            self.assertEqual("finalized", finalized_journal["state"])
            self.assertEqual([], TARGET.validate_target(fixture.target))
        finally:
            fixture.close()

    def test_gwt_049a_given_self_consistent_envelope_with_failing_incoming_validator_when_planned_then_target_is_unchanged(self) -> None:
        fixture = PackageApplyFixture()
        try:
            fixture.add_target("owner.txt", b"owner state\n")
            fixture.commit_target()
            target_before = {
                path.relative_to(fixture.target).as_posix(): path.read_bytes()
                for path in fixture.target.rglob("*")
                if path.is_file() and ".git" not in path.parts
            }
            make_schema_23_upgrade_package(
                fixture,
                validator_content=(
                    b"#!/usr/bin/env python3\n"
                    b"raise SystemExit('fixture incoming validation rejection')\n"
                ),
            )

            with self.assertRaisesRegex(
                APPLY.ApplyError, "incoming package validator failed"
            ):
                fixture.plan("0.9.0")

            self.assertEqual(
                target_before,
                {
                    path.relative_to(fixture.target).as_posix(): path.read_bytes()
                    for path in fixture.target.rglob("*")
                    if path.is_file() and ".git" not in path.parts
                },
            )
            self.assertFalse(APPLY.git_admin_transaction_base(fixture.target).exists())
        finally:
            fixture.close()

    def test_gwt_050_given_candidate_authority_mismatch_when_finalized_then_prior_authority_is_preserved(self) -> None:
        fixture = PackageApplyFixture()
        try:
            package = make_schema_23_upgrade_package(fixture)
            candidate_provenance, candidate_ledger = fixture_upgrade_authorities(
                fixture, package["selection"], package["previous_content"]
            )
            plan = fixture.plan("0.9.0")
            decision = fixture_remediation_decision(
                plan,
                candidate_provenance=candidate_provenance,
                candidate_ledger=candidate_ledger,
            )
            APPLY.apply_plan(plan, remediation_decision=decision)
            record_passed_target_validation(fixture, plan)
            provenance_path = fixture.target / ".dev/ai-context/provenance.yaml"
            ledger_path = fixture.target / ".dev/ai-context/customizations.yaml"
            prior = (provenance_path.read_bytes(), ledger_path.read_bytes())
            candidate_provenance["installation"]["last_upgraded_at"] = "2026-08-20T13:00:00+08:00"

            with self.assertRaisesRegex(
                TARGET.TargetValidationError, "candidate authority differs"
            ):
                TARGET.finalize_context(
                    fixture.target, candidate_provenance, candidate_ledger
                )

            self.assertEqual(prior, (provenance_path.read_bytes(), ledger_path.read_bytes()))
            self.assertFalse(
                (APPLY.transaction_root(fixture.target, plan["plan_sha256"])
                 / TARGET.TERMINAL_RECEIPT_PATH).exists()
            )
        finally:
            fixture.close()

    def test_gwt_051_given_missing_or_tampered_target_validation_when_finalized_then_authority_does_not_advance(self) -> None:
        fixture = PackageApplyFixture()
        try:
            package = make_schema_23_upgrade_package(fixture)
            candidate_provenance, candidate_ledger = fixture_upgrade_authorities(
                fixture, package["selection"], package["previous_content"]
            )
            plan = fixture.plan("0.9.0")
            decision = fixture_remediation_decision(
                plan,
                candidate_provenance=candidate_provenance,
                candidate_ledger=candidate_ledger,
            )
            APPLY.apply_plan(plan, remediation_decision=decision)
            provenance_path = fixture.target / ".dev/ai-context/provenance.yaml"
            prior = provenance_path.read_bytes()

            with self.assertRaisesRegex(
                TARGET.TargetValidationError, "target validation receipt"
            ):
                TARGET.finalize_context(
                    fixture.target, candidate_provenance, candidate_ledger
                )
            self.assertEqual(prior, provenance_path.read_bytes())
            record_passed_target_validation(fixture, plan)
            transaction = APPLY.transaction_root(fixture.target, plan["plan_sha256"])
            validation_evidence = transaction / APPLY.TARGET_VALIDATION_OUTPUT_PATH
            validation_evidence.unlink()

            with self.assertRaisesRegex(
                TARGET.TargetValidationError, "execution evidence bytes"
            ):
                TARGET.finalize_context(
                    fixture.target, candidate_provenance, candidate_ledger
                )
            self.assertEqual(prior, provenance_path.read_bytes())
            validation_evidence.write_bytes(b"target validation passed\n")
            (transaction / TARGET.TARGET_VALIDATION_RECEIPT_PATH).write_bytes(b"{}\n")

            with self.assertRaisesRegex(
                TARGET.TargetValidationError, "target validation receipt"
            ):
                TARGET.finalize_context(
                    fixture.target, candidate_provenance, candidate_ledger
                )
            self.assertEqual(prior, provenance_path.read_bytes())
        finally:
            fixture.close()

    def test_gwt_052_given_authority_advanced_before_terminal_binding_when_retried_then_exact_terminal_is_rebound(self) -> None:
        fixture = PackageApplyFixture()
        try:
            package = make_schema_23_upgrade_package(fixture)
            candidate_provenance, candidate_ledger = fixture_upgrade_authorities(
                fixture, package["selection"], package["previous_content"]
            )
            plan = fixture.plan("0.9.0")
            decision = fixture_remediation_decision(
                plan,
                candidate_provenance=candidate_provenance,
                candidate_ledger=candidate_ledger,
            )
            APPLY.apply_plan(plan, remediation_decision=decision)
            record_passed_target_validation(fixture, plan)
            provenance_path = fixture.target / ".dev/ai-context/provenance.yaml"
            ledger_path = fixture.target / ".dev/ai-context/customizations.yaml"
            provenance_path.write_text(
                yaml.safe_dump(candidate_provenance, sort_keys=False),
                encoding="utf-8",
                newline="\n",
            )
            ledger_path.write_text(
                yaml.safe_dump(candidate_ledger, sort_keys=False),
                encoding="utf-8",
                newline="\n",
            )

            errors = TARGET.validate_target(fixture.target)
            self.assertTrue(any("terminal receipt" in error for error in errors), errors)
            recovered = TARGET.finalize_context(
                fixture.target, candidate_provenance, candidate_ledger
            )
            transaction = APPLY.transaction_root(fixture.target, plan["plan_sha256"])
            terminal = transaction / TARGET.TERMINAL_RECEIPT_PATH
            self.assertEqual("finalized", recovered["status"])
            self.assertTrue(terminal.is_file())
            self.assertEqual([], TARGET.validate_target(fixture.target))
            journal_path = transaction / "journal.yaml"
            journal_bytes = journal_path.read_bytes()
            journal = yaml.safe_load(journal_bytes)
            journal["state"] = "awaiting-target-validation"
            journal_path.write_text(
                yaml.safe_dump(journal, sort_keys=False),
                encoding="utf-8",
                newline="\n",
            )
            self.assertTrue(
                any(
                    "terminal receipt journal state is not finalized" in error
                    for error in TARGET.validate_target(fixture.target)
                )
            )
            journal_path.write_bytes(journal_bytes)
            terminal.write_bytes(b"{}\n")
            self.assertTrue(
                any("terminal receipt" in error for error in TARGET.validate_target(fixture.target))
            )
        finally:
            fixture.close()

    def test_gwt_053_given_rejected_schema_23_upgrade_when_target_validated_then_rejection_is_retained_without_pending_receipt(self) -> None:
        fixture = PackageApplyFixture()
        try:
            package = make_schema_23_upgrade_package(fixture)
            fixture_upgrade_authorities(
                fixture, package["selection"], package["previous_content"]
            )
            plan = fixture.plan("0.9.0")
            decision = fixture_remediation_decision(plan, status="rejected")

            with self.assertRaisesRegex(APPLY.ApplyError, "rejected by owner decision"):
                APPLY.apply_plan(plan, remediation_decision=decision)

            transaction = APPLY.transaction_root(fixture.target, plan["plan_sha256"])
            journal = yaml.safe_load((transaction / "journal.yaml").read_text(encoding="utf-8"))
            self.assertEqual("rejected", journal["state"])
            self.assertIsNone(journal["target_validation_receipt_path"])
            self.assertIsNone(journal["target_validation_receipt_sha256"])
            self.assertFalse((fixture.target / APPLY.PENDING_RECEIPT_PATH).exists())
            self.assertEqual([], TARGET.validate_target(fixture.target))
        finally:
            fixture.close()

    def test_gwt_054_given_historical_v3_plan_21_when_pending_receipt_validated_then_compatibility_is_preserved(self) -> None:
        fixture = PackageApplyFixture()
        try:
            fixture.make_package(
                {".ai/managed.md": (b"new\n", "framework-managed", "0644")},
                [operation("001-add", "add", ".ai/managed.md")],
            )
            plan = fixture.plan()
            RAW_APPLY_PLAN(plan)
            transaction, sealed = reseal_applied_transaction(
                fixture,
                plan,
                lambda sealed: sealed.__setitem__("schema_version", "2.1.0"),
            )
            journal_path = transaction / "journal.yaml"
            journal = yaml.safe_load(journal_path.read_text(encoding="utf-8"))
            journal["schema_version"] = "ai-context-package-apply-journal/v3"
            journal["target_staging_paths"] = TARGET.transaction_staging_records(
                sealed["plan_sha256"],
                [
                    item
                    for item in sealed["operations"]
                    if item["action"] in {"add", "replace", "remove", "rename"}
                ],
            )
            journal_path.write_text(
                yaml.safe_dump(journal, sort_keys=False), encoding="utf-8", newline="\n"
            )

            errors: list[str] = []
            TARGET.validate_pending_apply_receipt(fixture.target, errors)

            self.assertEqual([], errors)
        finally:
            fixture.close()

    def test_gwt_055_given_retained_rejection_and_later_pending_apply_when_target_validated_then_the_unrelated_receipt_is_allowed(self) -> None:
        fixture = PackageApplyFixture()
        try:
            package = make_schema_23_upgrade_package(fixture)
            fixture_upgrade_authorities(
                fixture, package["selection"], package["previous_content"]
            )
            rejected_plan = fixture.plan("0.9.0")
            with self.assertRaisesRegex(APPLY.ApplyError, "rejected by owner decision"):
                APPLY.apply_plan(
                    rejected_plan,
                    remediation_decision=fixture_remediation_decision(
                        rejected_plan, status="rejected"
                    ),
                )
            shutil.rmtree(fixture.package)
            (fixture.package / "metadata").mkdir(parents=True)
            (fixture.package / "payload").mkdir()
            fixture.previous_path = None
            fixture.make_package(
                {".ai/later-clean-install.md": (b"later\n", "framework-managed", "0644")},
                [operation("001-add", "add", ".ai/later-clean-install.md")],
            )
            later_plan = fixture.plan()
            RAW_APPLY_PLAN(later_plan)

            pending = yaml.safe_load(
                (fixture.target / APPLY.PENDING_RECEIPT_PATH).read_text(encoding="utf-8")
            )
            self.assertNotEqual(rejected_plan["plan_sha256"], pending["transaction_id"])
            self.assertEqual([], TARGET.validate_target(fixture.target))
        finally:
            fixture.close()

    def test_gwt_056_given_historical_terminal_upgrade_and_later_apply_when_target_validated_then_the_old_authority_is_not_rechecked(self) -> None:
        fixture = PackageApplyFixture()
        try:
            package = make_schema_23_upgrade_package(fixture)
            candidate_provenance, candidate_ledger = fixture_upgrade_authorities(
                fixture, package["selection"], package["previous_content"]
            )
            upgrade_plan = fixture.plan("0.9.0")
            APPLY.apply_plan(
                upgrade_plan,
                remediation_decision=fixture_remediation_decision(
                    upgrade_plan,
                    candidate_provenance=candidate_provenance,
                    candidate_ledger=candidate_ledger,
                ),
            )
            record_passed_target_validation(fixture, upgrade_plan)
            TARGET.finalize_context(fixture.target, candidate_provenance, candidate_ledger)
            (fixture.target / APPLY.PENDING_RECEIPT_PATH).unlink()
            git(fixture.target, "add", "-A")
            fixture.commit_target("fixture finalized upgrade checkpoint")
            shutil.rmtree(fixture.package)
            (fixture.package / "metadata").mkdir(parents=True)
            (fixture.package / "payload").mkdir()
            fixture.previous_path = None
            fixture.make_package(
                {".ai/later-history.md": (b"later\n", "framework-managed", "0644")},
                [operation("001-add", "add", ".ai/later-history.md")],
            )
            later_plan = fixture.plan()
            RAW_APPLY_PLAN(later_plan)

            self.assertEqual([], TARGET.validate_target(fixture.target))
            current_provenance = TARGET.load_mapping(
                fixture.target / ".dev/ai-context/provenance.yaml", []
            )
            current_ledger = TARGET.load_mapping(
                fixture.target / ".dev/ai-context/customizations.yaml", []
            )
            assert current_provenance is not None
            assert current_ledger is not None
            self.assertEqual(
                "finalized",
                TARGET.finalize_context(
                    fixture.target, current_provenance, current_ledger
                )["status"],
            )
        finally:
            fixture.close()

    def test_gwt_057_given_owner_bound_candidate_with_wrong_package_source_when_finalized_then_sealed_identity_wins(self) -> None:
        fixture = PackageApplyFixture()
        try:
            package = make_schema_23_upgrade_package(fixture)
            candidate_provenance, candidate_ledger = fixture_upgrade_authorities(
                fixture, package["selection"], package["previous_content"]
            )
            candidate_provenance["source"]["commit"] = "d" * 40
            plan = fixture.plan("0.9.0")
            decision = fixture_remediation_decision(
                plan,
                candidate_provenance=candidate_provenance,
                candidate_ledger=candidate_ledger,
            )
            APPLY.apply_plan(plan, remediation_decision=decision)
            record_passed_target_validation(fixture, plan)
            provenance_path = fixture.target / ".dev/ai-context/provenance.yaml"
            prior = provenance_path.read_bytes()

            with self.assertRaisesRegex(
                TARGET.TargetValidationError,
                "candidate source differs from sealed package identity",
            ):
                TARGET.finalize_context(
                    fixture.target, candidate_provenance, candidate_ledger
                )

            self.assertEqual(prior, provenance_path.read_bytes())
        finally:
            fixture.close()

    def test_gwt_058_given_package_applied_without_target_validation_when_rolled_back_then_prior_target_is_restored(self) -> None:
        fixture = PackageApplyFixture()
        try:
            package = make_schema_23_upgrade_package(fixture)
            fixture_upgrade_authorities(
                fixture, package["selection"], package["previous_content"]
            )
            plan = fixture.plan("0.9.0")
            decision = fixture_remediation_decision(plan)

            receipt = APPLY.apply_plan(plan, remediation_decision=decision)
            transaction = APPLY.transaction_root(fixture.target, plan["plan_sha256"])
            journal = yaml.safe_load(
                (transaction / "journal.yaml").read_text(encoding="utf-8")
            )
            self.assertEqual(
                "awaiting-target-validation", receipt["transaction_state"]
            )
            self.assertEqual("awaiting-target-validation", journal["state"])

            rolled_back = APPLY.recover_transaction(
                fixture.target, plan["plan_sha256"], "rollback"
            )

            self.assertEqual("rolled-back", rolled_back["state"])
            self.assertEqual(
                package["previous_content"],
                (fixture.target / ".ai/assets/shared/example.md").read_bytes(),
            )
            self.assertFalse((fixture.target / APPLY.PENDING_RECEIPT_PATH).exists())
            self.assertEqual([], TARGET.validate_target(fixture.target))
        finally:
            fixture.close()

    def test_gwt_059_given_target_validation_passed_before_provenance_when_rolled_back_then_validation_evidence_is_retained(self) -> None:
        fixture = PackageApplyFixture()
        try:
            package = make_schema_23_upgrade_package(fixture)
            fixture_upgrade_authorities(
                fixture, package["selection"], package["previous_content"]
            )
            plan = fixture.plan("0.9.0")
            decision = fixture_remediation_decision(plan)
            APPLY.apply_plan(plan, remediation_decision=decision)
            record_passed_target_validation(fixture, plan)
            transaction = APPLY.transaction_root(fixture.target, plan["plan_sha256"])

            rolled_back = APPLY.recover_transaction(
                fixture.target, plan["plan_sha256"], "rollback"
            )

            self.assertEqual("rolled-back", rolled_back["state"])
            self.assertTrue(
                (transaction / APPLY.TARGET_VALIDATION_RECEIPT_PATH).is_file()
            )
            self.assertTrue(
                (transaction / APPLY.TARGET_VALIDATION_OUTPUT_PATH).is_file()
            )
            self.assertFalse((fixture.target / APPLY.PENDING_RECEIPT_PATH).exists())
            self.assertEqual([], TARGET.validate_target(fixture.target))
        finally:
            fixture.close()

    def test_gwt_060_given_upgrade_without_an_executable_target_validation_profile_when_recorded_or_finalized_then_it_fails_closed(self) -> None:
        fixture = PackageApplyFixture()
        try:
            # Given an initialized upgrade target whose committed validation profile is absent.
            package = make_schema_23_upgrade_package(fixture)
            candidate_provenance, candidate_ledger = fixture_upgrade_authorities(
                fixture, package["selection"], package["previous_content"]
            )
            git(fixture.target, "rm", "-q", "--", ".dev/project-config.yaml")
            fixture.commit_target("fixture removes target validation profile")
            plan = fixture.plan("0.9.0")
            decision = fixture_remediation_decision(
                plan,
                candidate_provenance=candidate_provenance,
                candidate_ledger=candidate_ledger,
            )
            APPLY.apply_plan(plan, remediation_decision=decision)
            transaction = APPLY.transaction_root(fixture.target, plan["plan_sha256"])
            provenance_path = fixture.target / ".dev/ai-context/provenance.yaml"
            ledger_path = fixture.target / ".dev/ai-context/customizations.yaml"
            prior_authority = (provenance_path.read_bytes(), ledger_path.read_bytes())

            # When a passed receipt is supplied without an executable target routine.
            with self.assertRaisesRegex(
                APPLY.ApplyError,
                "requires a present executable target validation profile",
            ):
                record_passed_target_validation(fixture, plan)

            # Then no receipt is bound and finalization preserves the prior authority.
            journal = yaml.safe_load((transaction / "journal.yaml").read_text(encoding="utf-8"))
            self.assertEqual("awaiting-target-validation", journal["state"])
            self.assertIsNone(journal["target_validation_receipt_sha256"])
            self.assertFalse((transaction / APPLY.TARGET_VALIDATION_RECEIPT_PATH).exists())
            with self.assertRaisesRegex(
                TARGET.TargetValidationError,
                "present executable target validation profile",
            ):
                TARGET.finalize_context(
                    fixture.target, candidate_provenance, candidate_ledger
                )
            self.assertEqual(
                prior_authority,
                (provenance_path.read_bytes(), ledger_path.read_bytes()),
            )
        finally:
            fixture.close()

    def test_gwt_061_given_n_v5_operations_when_applied_then_journal_write_work_is_linear_and_each_prefix_is_durable(self) -> None:
        def execute(count: int) -> tuple[APPLY.JournalWriteStats, list[int]]:
            fixture = PackageApplyFixture()
            try:
                incoming = {
                    f".ai/generated/file-{index:03d}.md":
                    (f"payload-{index}\n".encode("utf-8"), "framework-managed", "0644")
                    for index in range(count)
                }
                operations = [
                    operation(
                        f"{index:03d}-add",
                        "add",
                        f".ai/generated/file-{index:03d}.md",
                    )
                    for index in range(count)
                ]
                fixture.make_package(incoming, operations)
                plan = fixture.plan()
                durable_prefixes: list[int] = []

                def observe_boundary(event: str, details: dict) -> None:
                    if event != "after_progress_journal":
                        return
                    _root, _plan, recovered = APPLY.load_transaction(
                        fixture.target, plan["plan_sha256"]
                    )
                    durable_prefixes.append(recovered["next_apply_index"])
                    self.assertEqual(
                        details["next_apply_index"], recovered["next_apply_index"]
                    )

                stats = APPLY.JournalWriteStats()

                # When N operations are applied through journal v5.
                RAW_APPLY_PLAN(
                    plan,
                    boundary_hook=observe_boundary,
                    journal_io_hook=stats.observe,
                )

                # Then every prefix is durable and logical journal writes are N + O(1).
                self.assertEqual(list(range(1, count + 1)), durable_prefixes)
                self.assertEqual(count, stats.append_write_calls)
                self.assertEqual(3, stats.snapshot_write_calls)
                self.assertEqual(count + 3, stats.write_calls)
                return stats, durable_prefixes
            finally:
                fixture.close()

        small, _ = execute(4)
        large, _ = execute(8)
        self.assertLess(large.bytes_written, small.bytes_written * 3)

    def test_gwt_062_given_crash_after_v5_progress_append_when_resumed_then_the_operation_prefix_replays_exactly_once(self) -> None:
        fixture = PackageApplyFixture()
        try:
            incoming = {
                ".ai/one.md": (b"one\n", "framework-managed", "0644"),
                ".ai/two.md": (b"two\n", "framework-managed", "0644"),
            }
            fixture.make_package(
                incoming,
                [
                    operation("001-add", "add", ".ai/one.md"),
                    operation("002-add", "add", ".ai/two.md"),
                ],
            )
            plan = fixture.plan()

            def interrupt_after_first_durable_prefix(event: str, details: dict) -> None:
                if event == "after_progress_journal" and details["next_apply_index"] == 1:
                    raise APPLY.InjectedInterruption("fixture crash after durable append")

            # When the process dies after the first append is fsynced but before a snapshot.
            with self.assertRaises(APPLY.InjectedInterruption):
                RAW_APPLY_PLAN(plan, boundary_hook=interrupt_after_first_durable_prefix)
            transaction = APPLY.transaction_root(fixture.target, plan["plan_sha256"])
            snapshot = yaml.safe_load(
                (transaction / "journal.yaml").read_text(encoding="utf-8")
            )
            self.assertEqual(0, snapshot["next_apply_index"])
            self.assertEqual(1, len((transaction / APPLY.JOURNAL_PROGRESS_PATH).read_text(encoding="utf-8").splitlines()))
            with (transaction / APPLY.JOURNAL_PROGRESS_PATH).open("ab") as progress:
                progress.write(b'{"schema_version":"torn')

            receipt = APPLY.recover_transaction(
                fixture.target, plan["plan_sha256"], "resume", fixture.package
            )

            # Then replay advances the durable prefix and the second operation runs once.
            self.assertEqual(["001-add", "002-add"], receipt["applied_operation_ids"])
            _root, _plan, journal = APPLY.load_transaction(
                fixture.target, plan["plan_sha256"]
            )
            self.assertEqual("finalized", journal["state"])
            self.assertEqual(["001-add", "002-add"], journal["completed_operation_ids"])
            self.assertEqual(
                2,
                len(
                    (transaction / APPLY.JOURNAL_PROGRESS_PATH)
                    .read_text(encoding="utf-8")
                    .splitlines()
                ),
            )
            self.assertEqual(b"one\n", (fixture.target / ".ai/one.md").read_bytes())
            self.assertEqual(b"two\n", (fixture.target / ".ai/two.md").read_bytes())
        finally:
            fixture.close()

    def test_gwt_063_given_unfinished_or_terminal_v4_when_new_v5_apply_starts_then_only_unfinished_evidence_blocks(self) -> None:
        fixture = PackageApplyFixture()
        try:
            fixture.make_package(
                {".ai/new.md": (b"new\n", "framework-managed", "0644")},
                [operation("001-add", "add", ".ai/new.md")],
            )
            plan = fixture.plan()
            legacy_id = "b" * 64
            legacy_root = APPLY.transaction_root(fixture.target, legacy_id)
            legacy_root.mkdir(parents=True)
            legacy_journal_path = legacy_root / "journal.yaml"
            legacy = {
                "schema_version": APPLY.LEGACY_JOURNAL_SCHEMA_VERSION,
                "transaction_id": legacy_id,
                "plan_sha256": legacy_id,
                "state": "applying",
            }
            legacy_journal_path.write_text(
                yaml.safe_dump(legacy, sort_keys=False), encoding="utf-8", newline="\n"
            )

            # When an unfinished v4 transaction exists, new mutation is rejected safely.
            with self.assertRaisesRegex(
                APPLY.ApplyError,
                "unsupported-transaction-journal-version.*prior tooling.*owner-directed manual recovery",
            ):
                RAW_APPLY_PLAN(plan)
            self.assertFalse((fixture.target / ".ai/new.md").exists())
            self.assertFalse(APPLY.transaction_root(fixture.target, plan["plan_sha256"]).exists())

            # When the same v4 record is terminal archival evidence, it is left unchanged.
            legacy["state"] = "finalized"
            legacy_journal_path.write_text(
                yaml.safe_dump(legacy, sort_keys=False), encoding="utf-8", newline="\n"
            )
            archival_bytes = legacy_journal_path.read_bytes()
            receipt = RAW_APPLY_PLAN(plan)

            # Then a new v5 transaction succeeds without recovering or converting v4.
            self.assertEqual(["001-add"], receipt["applied_operation_ids"])
            self.assertEqual(archival_bytes, legacy_journal_path.read_bytes())
            self.assertEqual(
                APPLY.JOURNAL_SCHEMA_VERSION,
                yaml.safe_load(
                    (
                        APPLY.transaction_root(fixture.target, plan["plan_sha256"])
                        / "journal.yaml"
                    ).read_text(encoding="utf-8")
                )["schema_version"],
            )
            v5_root = APPLY.transaction_root(fixture.target, plan["plan_sha256"])
            v5_journal_path = v5_root / "journal.yaml"
            unsupported = yaml.safe_load(v5_journal_path.read_text(encoding="utf-8"))
            unsupported["schema_version"] = APPLY.LEGACY_JOURNAL_SCHEMA_VERSION
            v5_journal_path.write_text(
                yaml.safe_dump(unsupported, sort_keys=False),
                encoding="utf-8",
                newline="\n",
            )
            with self.assertRaisesRegex(
                APPLY.ApplyError,
                "unsupported-transaction-journal-version.*journal v4 recovery is not supported",
            ):
                APPLY.recover_transaction(
                    fixture.target,
                    plan["plan_sha256"],
                    "resume",
                    fixture.package,
                )
        finally:
            fixture.close()

    def test_gwt_064_given_progress_opt_in_when_cli_applies_then_only_stderr_receives_progress(self) -> None:
        fixture = PackageApplyFixture()
        try:
            fixture.make_package(
                {".ai/progress.md": (b"progress\n", "framework-managed", "0644")},
                [operation("001-add", "add", ".ai/progress.md")],
            )

            # When the CLI applies with explicit progress reporting.
            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / ".ai/scripts/plan-ai-context-package-apply.py"),
                    "--package-root",
                    str(fixture.package),
                    "--target-root",
                    str(fixture.target),
                    "--apply",
                    "--progress",
                ],
                capture_output=True,
                text=True,
            )

            # Then stdout keeps its prior contract and progress appears only on stderr.
            self.assertEqual(0, result.returncode, result.stderr)
            self.assertIn("apply_receipt:", result.stdout)
            self.assertNotIn("AI context package apply progress:", result.stdout)
            self.assertIn("AI context package apply progress:", result.stderr)
            self.assertIn("apply operation durably completed", result.stderr)
        finally:
            fixture.close()

    def test_gwt_065_given_unfinished_v4_when_v5_recovery_would_mutate_then_resume_and_rollback_are_blocked(self) -> None:
        fixture = PackageApplyFixture()
        try:
            fixture.make_package(
                {
                    ".ai/one.md": (b"one\n", "framework-managed", "0644"),
                    ".ai/two.md": (b"two\n", "framework-managed", "0644"),
                },
                [
                    operation("001-add", "add", ".ai/one.md"),
                    operation("002-add", "add", ".ai/two.md"),
                ],
            )
            plan = fixture.plan()

            def interrupt_after_first_durable_prefix(event: str, details: dict) -> None:
                if event == "after_progress_journal" and details["next_apply_index"] == 1:
                    raise APPLY.InjectedInterruption("fixture crash after durable append")

            with self.assertRaises(APPLY.InjectedInterruption):
                RAW_APPLY_PLAN(plan, boundary_hook=interrupt_after_first_durable_prefix)
            legacy_id = "c" * 64
            legacy_root = APPLY.transaction_root(fixture.target, legacy_id)
            legacy_root.mkdir(parents=True)
            (legacy_root / "journal.yaml").write_text(
                yaml.safe_dump(
                    {
                        "schema_version": APPLY.LEGACY_JOURNAL_SCHEMA_VERSION,
                        "transaction_id": legacy_id,
                        "plan_sha256": legacy_id,
                        "state": "applying",
                    },
                    sort_keys=False,
                ),
                encoding="utf-8",
                newline="\n",
            )

            for action, package_root in (("resume", fixture.package), ("rollback", None)):
                with self.assertRaisesRegex(
                    APPLY.ApplyError,
                    "unsupported-transaction-journal-version.*prior tooling.*owner-directed manual recovery",
                ):
                    APPLY.recover_transaction(
                        fixture.target,
                        plan["plan_sha256"],
                        action,
                        package_root,
                    )

            self.assertEqual(b"one\n", (fixture.target / ".ai/one.md").read_bytes())
            self.assertFalse((fixture.target / ".ai/two.md").exists())
        finally:
            fixture.close()

    def test_gwt_066_given_digest_valid_v5_progress_that_differs_from_sealed_plan_when_target_validates_then_it_fails_closed(self) -> None:
        fixture = PackageApplyFixture()
        try:
            fixture.make_package(
                {
                    ".ai/one.md": (b"one\n", "framework-managed", "0644"),
                    ".ai/two.md": (b"two\n", "framework-managed", "0644"),
                },
                [
                    operation("001-add", "add", ".ai/one.md"),
                    operation("002-add", "add", ".ai/two.md"),
                ],
            )
            plan = fixture.plan()
            RAW_APPLY_PLAN(plan)
            transaction = APPLY.transaction_root(fixture.target, plan["plan_sha256"])
            progress_path = transaction / APPLY.JOURNAL_PROGRESS_PATH
            records = [
                json.loads(line)
                for line in progress_path.read_text(encoding="utf-8").splitlines()
            ]
            records[0]["operation_id"] = "digest-valid-but-not-in-sealed-plan"
            previous = None
            for record in records:
                record["previous_record_sha256"] = previous
                record.pop("record_sha256", None)
                record["record_sha256"] = APPLY.canonical_digest(record)
                previous = record["record_sha256"]
            progress_path.write_bytes(b"".join(APPLY.canonical_json_bytes(item) for item in records))
            journal_path = transaction / "journal.yaml"
            journal = yaml.safe_load(journal_path.read_text(encoding="utf-8"))
            journal["progress_tail_sha256"] = previous
            journal_path.write_text(
                yaml.safe_dump(journal, sort_keys=True),
                encoding="utf-8",
                newline="\n",
            )

            errors: list[str] = []
            TARGET.validate_pending_apply_receipt(fixture.target, errors)
            self.assertTrue(
                any("v5 progress semantics differ from sealed plan" in item for item in errors),
                errors,
            )
            with self.assertRaisesRegex(
                APPLY.ApplyError, "transaction journal apply progress is invalid"
            ):
                APPLY.load_transaction(fixture.target, plan["plan_sha256"])
        finally:
            fixture.close()

    def test_gwt_067_given_finalized_v5_snapshot_with_missing_progress_log_when_target_validates_then_recovery_parity_fails_closed(self) -> None:
        fixture = PackageApplyFixture()
        try:
            fixture.make_package(
                {".ai/one.md": (b"one\n", "framework-managed", "0644")},
                [operation("001-add", "add", ".ai/one.md")],
            )
            plan = fixture.plan()
            RAW_APPLY_PLAN(plan)
            transaction = APPLY.transaction_root(fixture.target, plan["plan_sha256"])
            (transaction / APPLY.JOURNAL_PROGRESS_PATH).unlink()
            journal_path = transaction / "journal.yaml"
            journal = yaml.safe_load(journal_path.read_text(encoding="utf-8"))
            journal["progress_record_count"] = 0
            journal["progress_tail_sha256"] = None
            journal_path.write_text(
                yaml.safe_dump(journal, sort_keys=True),
                encoding="utf-8",
                newline="\n",
            )

            errors: list[str] = []
            TARGET.validate_pending_apply_receipt(fixture.target, errors)
            self.assertTrue(
                any("v5 progress semantics differ from sealed plan" in item for item in errors),
                errors,
            )
            with self.assertRaisesRegex(
                APPLY.ApplyError, "transaction journal snapshot progress differs from its log"
            ):
                APPLY.load_transaction(fixture.target, plan["plan_sha256"])
        finally:
            fixture.close()

    def test_gwt_068_given_finalized_v5_with_compacted_rollback_progress_when_target_validates_then_recovery_state_invariants_fail_closed(self) -> None:
        fixture = PackageApplyFixture()
        try:
            fixture.make_package(
                {".ai/one.md": (b"one\n", "framework-managed", "0644")},
                [operation("001-add", "add", ".ai/one.md")],
            )
            plan = fixture.plan()
            RAW_APPLY_PLAN(plan)
            transaction = APPLY.transaction_root(fixture.target, plan["plan_sha256"])
            journal_path = transaction / "journal.yaml"
            journal = yaml.safe_load(journal_path.read_text(encoding="utf-8"))
            rollback_path = journal["pre_state"][-1]["path"]
            rollback_record = {
                "schema_version": APPLY.JOURNAL_PROGRESS_SCHEMA_VERSION,
                "sequence": 1,
                "phase": "rollback",
                "previous_record_sha256": None,
                "transition_sequence": 1,
                "rollback_index": 0,
                "path": rollback_path,
            }
            rollback_record["record_sha256"] = APPLY.canonical_digest(
                rollback_record
            )
            (transaction / APPLY.JOURNAL_PROGRESS_PATH).write_bytes(
                APPLY.canonical_json_bytes(rollback_record)
            )
            journal["completed_operation_ids"] = []
            journal["next_apply_index"] = 0
            journal["rollback_completed_paths"] = [rollback_path]
            journal["rollback_next_index"] = 1
            journal["progress_record_count"] = 1
            journal["progress_tail_sha256"] = rollback_record["record_sha256"]
            journal_path.write_text(
                yaml.safe_dump(journal, sort_keys=True),
                encoding="utf-8",
                newline="\n",
            )

            errors: list[str] = []
            TARGET.validate_pending_apply_receipt(fixture.target, errors)
            self.assertTrue(
                any("non-rollback journal contains rollback progress" in item for item in errors),
                errors,
            )
            with self.assertRaisesRegex(
                APPLY.ApplyError, "non-rollback journal contains rollback progress"
            ):
                APPLY.load_transaction(fixture.target, plan["plan_sha256"])
        finally:
            fixture.close()

    def test_gwt_069_given_broken_progress_link_when_v5_resumes_or_writes_then_no_target_or_external_mutation_occurs(self) -> None:
        fixture = PackageApplyFixture()
        try:
            fixture.make_package(
                {
                    ".ai/one.md": (b"one\n", "framework-managed", "0644"),
                    ".ai/two.md": (b"two\n", "framework-managed", "0644"),
                },
                [
                    operation("001-add", "add", ".ai/one.md"),
                    operation("002-add", "add", ".ai/two.md"),
                ],
            )
            plan = fixture.plan()

            def interrupt_after_first_durable_prefix(event: str, details: dict) -> None:
                if event == "after_progress_journal" and details["next_apply_index"] == 1:
                    raise APPLY.InjectedInterruption("fixture crash after durable append")

            with self.assertRaises(APPLY.InjectedInterruption):
                RAW_APPLY_PLAN(plan, boundary_hook=interrupt_after_first_durable_prefix)
            transaction = APPLY.transaction_root(fixture.target, plan["plan_sha256"])
            progress_path = transaction / APPLY.JOURNAL_PROGRESS_PATH
            progress_path.unlink()
            outside = fixture.root / "outside-progress.jsonl"
            try:
                progress_path.symlink_to(outside)
            except OSError:
                link_context = mock.patch.object(
                    APPLY,
                    "is_reparse_point",
                    side_effect=lambda path: Path(path) == progress_path,
                )
            else:
                link_context = mock.patch.object(
                    APPLY,
                    "is_reparse_point",
                    wraps=APPLY.is_reparse_point,
                )

            with link_context:
                with self.assertRaisesRegex(
                    APPLY.ApplyError, "transaction journal progress log is unsafe"
                ):
                    APPLY.recover_transaction(
                        fixture.target,
                        plan["plan_sha256"],
                        "resume",
                        fixture.package,
                    )
                with self.assertRaisesRegex(
                    APPLY.ApplyError, "transaction journal progress log is unsafe"
                ):
                    APPLY.durable_append_bytes(progress_path, b"{}\n")
                journal = yaml.safe_load(
                    (transaction / "journal.yaml").read_text(encoding="utf-8")
                )
                with self.assertRaisesRegex(
                    APPLY.ApplyError, "transaction journal progress log is unsafe"
                ):
                    APPLY.truncate_incomplete_progress_tail(transaction, journal)

            self.assertEqual(b"one\n", (fixture.target / ".ai/one.md").read_bytes())
            self.assertFalse((fixture.target / ".ai/two.md").exists())
            self.assertFalse(outside.exists())
        finally:
            fixture.close()

    def test_gwt_070_given_transaction_root_link_when_v5_resumes_or_validates_then_no_external_journal_or_target_mutation_occurs(self) -> None:
        fixture = PackageApplyFixture()
        try:
            fixture.make_package(
                {
                    ".ai/one.md": (b"one\n", "framework-managed", "0644"),
                    ".ai/two.md": (b"two\n", "framework-managed", "0644"),
                },
                [
                    operation("001-add", "add", ".ai/one.md"),
                    operation("002-add", "add", ".ai/two.md"),
                ],
            )
            plan = fixture.plan()

            def interrupt_after_first_durable_prefix(event: str, details: dict) -> None:
                if event == "after_progress_journal" and details["next_apply_index"] == 1:
                    raise APPLY.InjectedInterruption("fixture crash after durable append")

            with self.assertRaises(APPLY.InjectedInterruption):
                RAW_APPLY_PLAN(plan, boundary_hook=interrupt_after_first_durable_prefix)
            transaction = APPLY.transaction_root(fixture.target, plan["plan_sha256"])
            outside = fixture.root / "outside-transaction"
            shutil.copytree(transaction, outside)
            outside_progress = outside / APPLY.JOURNAL_PROGRESS_PATH
            outside_progress_before = outside_progress.read_bytes()
            shutil.rmtree(transaction)
            try:
                transaction.symlink_to(outside, target_is_directory=True)
            except OSError:
                transaction.mkdir()
                apply_link_context = mock.patch.object(
                    APPLY,
                    "is_reparse_point",
                    side_effect=lambda path: Path(path) == transaction,
                )
                target_link_context = mock.patch.object(
                    TARGET,
                    "is_reparse_point",
                    side_effect=lambda path: Path(path) == transaction,
                )
            else:
                apply_link_context = mock.patch.object(
                    APPLY,
                    "is_reparse_point",
                    wraps=APPLY.is_reparse_point,
                )
                target_link_context = mock.patch.object(
                    TARGET,
                    "is_reparse_point",
                    wraps=TARGET.is_reparse_point,
                )

            with apply_link_context, target_link_context:
                with self.assertRaisesRegex(
                    APPLY.ApplyError, "transaction root is unsafe"
                ):
                    APPLY.recover_transaction(
                        fixture.target,
                        plan["plan_sha256"],
                        "resume",
                        fixture.package,
                    )
                with self.assertRaisesRegex(
                    APPLY.ApplyError, "transaction root is unsafe"
                ):
                    APPLY.durable_append_bytes(
                        transaction / APPLY.JOURNAL_PROGRESS_PATH, b"{}\n"
                    )
                errors: list[str] = []
                TARGET.validate_apply_transaction_journals(
                    fixture.target, None, errors
                )
                self.assertTrue(
                    any("transaction root is unsafe" in item for item in errors),
                    errors,
                )

            self.assertEqual(outside_progress_before, outside_progress.read_bytes())
            self.assertEqual(b"one\n", (fixture.target / ".ai/one.md").read_bytes())
            self.assertFalse((fixture.target / ".ai/two.md").exists())
        finally:
            fixture.close()

    def test_gwt_071_given_transaction_lock_link_when_apply_starts_then_no_external_or_target_mutation_occurs(self) -> None:
        fixture = PackageApplyFixture()
        try:
            fixture.make_package(
                {".ai/one.md": (b"one\n", "framework-managed", "0644")},
                [operation("001-add", "add", ".ai/one.md")],
            )
            plan = fixture.plan()
            base = APPLY.git_admin_transaction_base(fixture.target)
            base.mkdir(parents=True)
            lock_path = base / "transaction.lock"
            outside = fixture.root / "outside-lock"
            try:
                lock_path.symlink_to(outside)
            except OSError:
                lock_path.write_bytes(b"sentinel")
                link_context = mock.patch.object(
                    APPLY,
                    "is_reparse_point",
                    side_effect=lambda path: Path(path) == lock_path,
                )
            else:
                link_context = mock.patch.object(
                    APPLY,
                    "is_reparse_point",
                    wraps=APPLY.is_reparse_point,
                )

            with link_context, self.assertRaisesRegex(
                APPLY.ApplyError, "transaction lock is unsafe"
            ):
                RAW_APPLY_PLAN(plan)

            self.assertFalse((fixture.target / ".ai/one.md").exists())
            self.assertFalse(
                APPLY.transaction_root(fixture.target, plan["plan_sha256"]).exists()
            )
            self.assertFalse(outside.exists())
            if not lock_path.is_symlink():
                self.assertEqual(b"sentinel", lock_path.read_bytes())
        finally:
            fixture.close()

    def test_gwt_072_given_untrusted_legacy_journal_leaf_when_new_v5_apply_starts_then_mutation_fails_closed(self) -> None:
        for variant in ("missing", "unsafe", "unreadable", "malformed"):
            with self.subTest(variant=variant):
                fixture = PackageApplyFixture()
                try:
                    fixture.make_package(
                        {".ai/new.md": (b"new\n", "framework-managed", "0644")},
                        [operation("001-add", "add", ".ai/new.md")],
                    )
                    plan = fixture.plan()
                    legacy_id = "d" * 64
                    legacy_root = APPLY.transaction_root(fixture.target, legacy_id)
                    legacy_root.mkdir(parents=True)
                    journal_path = legacy_root / "journal.yaml"
                    legacy = {
                        "schema_version": APPLY.LEGACY_JOURNAL_SCHEMA_VERSION,
                        "transaction_id": legacy_id,
                        "plan_sha256": legacy_id,
                        "state": "applying",
                    }
                    leaf_context = nullcontext()
                    read_context = nullcontext()
                    if variant != "missing":
                        journal_path.write_text(
                            (
                                "not: [valid"
                                if variant == "malformed"
                                else yaml.safe_dump(legacy, sort_keys=False)
                            ),
                            encoding="utf-8",
                            newline="\n",
                        )
                    if variant == "unsafe":
                        leaf_context = mock.patch.object(
                            APPLY,
                            "is_reparse_point",
                            side_effect=lambda path: Path(path) == journal_path,
                        )
                    elif variant == "unreadable":
                        original_read_text = Path.read_text

                        def reject_legacy_read(path: Path, *args: object, **kwargs: object) -> str:
                            if Path(path) == journal_path:
                                raise PermissionError("fixture denies legacy journal read")
                            return original_read_text(path, *args, **kwargs)

                        read_context = mock.patch.object(
                            Path,
                            "read_text",
                            autospec=True,
                            side_effect=reject_legacy_read,
                        )

                    with leaf_context, read_context, self.assertRaisesRegex(
                        APPLY.ApplyError,
                        "unsupported-transaction-journal-version.*cannot be proven terminal.*prior tooling.*owner-directed manual recovery",
                    ):
                        RAW_APPLY_PLAN(plan)

                    self.assertFalse((fixture.target / ".ai/new.md").exists())
                    self.assertFalse(
                        APPLY.transaction_root(
                            fixture.target, plan["plan_sha256"]
                        ).exists()
                    )
                finally:
                    fixture.close()

    def test_gwt_073_given_small_v014_scale_and_expanded_payloads_when_planned_then_git_process_count_is_constant(self) -> None:
        observations: list[tuple[int, int, dict]] = []
        for payload_count in (3, 631, 947):
            with self.subTest(payload_count=payload_count):
                fixture = PackageApplyFixture()
                try:
                    incoming = {
                        f".ai/generated/item-{index:04d}.txt": (
                            f"payload-{index}\n".encode("utf-8"),
                            "framework-managed",
                            "0644",
                        )
                        for index in range(payload_count)
                    }
                    operations = [
                        operation(
                            f"{index:04d}-add",
                            "add",
                            f".ai/generated/item-{index:04d}.txt",
                        )
                        for index in range(payload_count)
                    ]
                    fixture.make_package(incoming, operations)
                    events: list[dict] = []
                    git_processes = 0
                    original_run = subprocess.run

                    def counted_run(*args: object, **kwargs: object):
                        nonlocal git_processes
                        argv = args[0] if args else kwargs.get("args")
                        if isinstance(argv, (list, tuple)) and argv and argv[0] == "git":
                            git_processes += 1
                        return original_run(*args, **kwargs)

                    with mock.patch.object(
                        APPLY.subprocess, "run", side_effect=counted_run
                    ):
                        plan = APPLY.build_plan(
                            fixture.package,
                            fixture.target,
                            git_inspection_hook=events.append,
                        )
                    self.assertEqual(payload_count, len(plan["required_framework_paths"]))
                    self.assertEqual(1, len(events))
                    self.assertEqual("plan", events[0]["phase"])
                    self.assertEqual("passed", events[0]["outcome"])
                    self.assertEqual(payload_count, events[0]["path_count"])
                    self.assertGreater(events[0]["git_bytes_read"], 0)
                    self.assertGreater(events[0]["phase_duration_ns"], 0)
                    observations.append(
                        (git_processes, events[0]["git_process_count"], events[0])
                    )
                finally:
                    fixture.close()

        self.assertEqual({item[0] for item in observations}, {24})
        self.assertEqual({item[1] for item in observations}, {24})

    def test_gwt_074_given_growing_apply_operation_counts_when_applied_then_git_process_count_is_constant(self) -> None:
        observations: list[tuple[int, int, int, int, int]] = []
        for payload_count in (1, 8, 32):
            with self.subTest(payload_count=payload_count):
                fixture = PackageApplyFixture()
                try:
                    incoming = {
                        f".ai/apply/item-{index:03d}.txt": (
                            f"apply-{index}\n".encode("utf-8"),
                            "framework-managed",
                            "0644",
                        )
                        for index in range(payload_count)
                    }
                    operations = [
                        operation(
                            f"{index:03d}-add",
                            "add",
                            f".ai/apply/item-{index:03d}.txt",
                        )
                        for index in range(payload_count)
                    ]
                    fixture.make_package(incoming, operations)
                    plan = fixture.plan()
                    events: list[dict] = []
                    git_processes = 0
                    full_worktree_scans = 0
                    entry_reads = 0
                    original_run = subprocess.run
                    original_inventory = APPLY.worktree_inventory
                    original_entry = APPLY.worktree_inventory_entry

                    def counted_run(*args: object, **kwargs: object):
                        nonlocal git_processes
                        argv = args[0] if args else kwargs.get("args")
                        if isinstance(argv, (list, tuple)) and argv and argv[0] == "git":
                            git_processes += 1
                        return original_run(*args, **kwargs)

                    def counted_inventory(*args: object, **kwargs: object):
                        nonlocal full_worktree_scans
                        full_worktree_scans += 1
                        return original_inventory(*args, **kwargs)

                    def counted_entry(*args: object, **kwargs: object):
                        nonlocal entry_reads
                        entry_reads += 1
                        return original_entry(*args, **kwargs)

                    with mock.patch.object(
                        APPLY.subprocess, "run", side_effect=counted_run
                    ), mock.patch.object(
                        APPLY, "worktree_inventory", side_effect=counted_inventory
                    ), mock.patch.object(
                        APPLY, "worktree_inventory_entry", side_effect=counted_entry
                    ):
                        receipt = RAW_APPLY_PLAN(
                            plan, git_inspection_hook=events.append
                        )
                    self.assertEqual(payload_count, len(receipt["applied_operation_ids"]))
                    self.assertEqual(1, len(events))
                    self.assertEqual("apply", events[0]["phase"])
                    self.assertEqual("passed", events[0]["outcome"])
                    observations.append(
                        (
                            payload_count,
                            git_processes,
                            events[0]["git_process_count"],
                            full_worktree_scans,
                            entry_reads,
                        )
                    )
                finally:
                    fixture.close()

        self.assertEqual({item[1] for item in observations}, {12})
        self.assertEqual({item[2] for item in observations}, {12})
        self.assertEqual({item[3] for item in observations}, {4})
        for payload_count, _processes, _snapshot_processes, _scans, reads in observations:
            self.assertLessEqual(
                reads,
                54 * payload_count + 220,
                "apply filesystem entry reads must remain O(payload paths)",
            )

    def test_gwt_075_given_ignored_lfs_attributes_and_unknown_index_state_when_snapshotted_then_semantics_fail_closed(self) -> None:
        fixture = PackageApplyFixture()
        try:
            fixture.add_target(
                ".gitattributes",
                b".ai/lfs.bin filter=lfs\n.ai/ident.txt ident\n",
            )
            fixture.add_target(".gitignore", b".ai/ignored.txt\n")
            fixture.commit_target("attribute and ignore policy")
            snapshot = APPLY.capture_target_git_snapshot(
                fixture.target,
                [".ai/lfs.bin", ".ai/ident.txt", ".ai/ignored.txt"],
                phase="negative-fixture",
                require_clean=True,
            )
            self.assertFalse(snapshot.no_content_transform(".ai/lfs.bin"))
            self.assertFalse(snapshot.no_content_transform(".ai/ident.txt"))
            self.assertIsNotNone(snapshot.ignore_rule(".ai/ignored.txt"))
            self.assertIsNone(snapshot.ignore_rule(".ai/lfs.bin"))
            with self.assertRaisesRegex(
                APPLY.ApplyError, "unresolved stages"
            ):
                APPLY._parse_index_entries(
                    b"100644 " + b"a" * 40 + b" 1\t.ai/conflict.txt\0"
                )
        finally:
            fixture.close()

    def test_gwt_076_given_metrics_opt_in_when_cli_plans_and_applies_then_machine_records_are_stderr_only(self) -> None:
        fixture = PackageApplyFixture()
        try:
            fixture.make_package(
                {".ai/metrics.md": (b"metrics\n", "framework-managed", "0644")},
                [operation("001-add", "add", ".ai/metrics.md")],
            )
            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / ".ai/scripts/plan-ai-context-package-apply.py"),
                    "--package-root",
                    str(fixture.package),
                    "--target-root",
                    str(fixture.target),
                    "--apply",
                    "--git-inspection-metrics",
                ],
                capture_output=True,
                text=True,
            )
            self.assertEqual(0, result.returncode, result.stderr)
            prefix = "AI context package Git inspection: "
            records = [
                json.loads(line.removeprefix(prefix))
                for line in result.stderr.splitlines()
                if line.startswith(prefix)
            ]
            self.assertEqual(["plan", "apply"], [item["phase"] for item in records])
            self.assertEqual(
                {"plan": 24, "apply": 12},
                {item["phase"]: item["git_process_count"] for item in records},
            )
            self.assertTrue(all(item["outcome"] == "passed" for item in records))
            self.assertNotIn(prefix, result.stdout)
            self.assertIn("apply_receipt:", result.stdout)
        finally:
            fixture.close()

    def test_gwt_077_given_head_or_unrelated_worktree_drift_after_snapshot_when_verified_then_it_fails_closed(self) -> None:
        fixture = PackageApplyFixture()
        try:
            snapshot = APPLY.capture_target_git_snapshot(
                fixture.target,
                ["README.md"],
                phase="drift-fixture",
                require_clean=True,
            )
            (fixture.target / "unrelated.txt").write_text(
                "drift\n", encoding="utf-8", newline="\n"
            )
            self.assertIn("unrelated.txt", snapshot.changed_paths())
            git(fixture.target, "add", "unrelated.txt")
            git(fixture.target, "commit", "-qm", "external drift")
            with APPLY.target_git_snapshot_scope(snapshot), self.assertRaisesRegex(
                APPLY.ApplyError, "administrative identity changed"
            ):
                APPLY.target_git_head(fixture.target)
        finally:
            fixture.close()

    def test_gwt_078_given_tracked_replace_paths_when_planned_then_index_blobs_are_read_by_one_batch_process(self) -> None:
        fixture = PackageApplyFixture()
        try:
            previous = {
                f".ai/tracked/item-{index}.txt": (
                    f"old-{index}\n".encode("utf-8"),
                    "framework-managed",
                    "0644",
                )
                for index in range(3)
            }
            incoming = {
                path: (
                    content.replace(b"old-", b"new-"),
                    ownership,
                    mode,
                )
                for path, (content, ownership, mode) in previous.items()
            }
            for path, (content, _ownership, _mode) in previous.items():
                fixture.add_target(path, content)
            fixture.commit_target("tracked replacement baseline")
            fixture.make_package(
                incoming,
                [
                    operation(
                        f"{index:03d}-replace",
                        "replace",
                        f".ai/tracked/item-{index}.txt",
                    )
                    for index in range(3)
                ],
                previous,
            )
            events: list[dict] = []
            git_processes = 0
            original_run = subprocess.run

            def counted_run(*args: object, **kwargs: object):
                nonlocal git_processes
                argv = args[0] if args else kwargs.get("args")
                if isinstance(argv, (list, tuple)) and argv and argv[0] == "git":
                    git_processes += 1
                return original_run(*args, **kwargs)

            with mock.patch.object(
                APPLY.subprocess, "run", side_effect=counted_run
            ):
                plan = APPLY.build_plan(
                    fixture.package,
                    fixture.target,
                    fixture.previous_path,
                    "0.9.0",
                    git_inspection_hook=events.append,
                )
            self.assertEqual({"replace"}, {item["action"] for item in plan["operations"]})
            self.assertEqual(24, git_processes)
            self.assertEqual(24, events[0]["git_process_count"])
            self.assertEqual(3, events[0]["git_blob_read_count"])
        finally:
            fixture.close()

    def test_gwt_079_given_modified_or_deleted_tracked_path_when_snapshotted_then_clean_gate_fails_closed(self) -> None:
        for mutation in ("modified", "deleted"):
            with self.subTest(mutation=mutation):
                fixture = PackageApplyFixture()
                try:
                    fixture.make_package({}, [])
                    readme = fixture.target / "README.md"
                    if mutation == "modified":
                        readme.write_text("modified\n", encoding="utf-8", newline="\n")
                    else:
                        readme.unlink()
                    with self.assertRaisesRegex(
                        APPLY.ApplyError, "worktree must be clean"
                    ):
                        APPLY.capture_target_git_snapshot(
                            fixture.target,
                            ["README.md"],
                            phase="dirty-fixture",
                            require_clean=True,
                        )
                finally:
                    fixture.close()

    def test_gwt_080_given_target_commit_between_plan_admission_and_full_snapshot_when_compared_then_mixed_head_facts_fail_closed(self) -> None:
        fixture = PackageApplyFixture()
        try:
            fixture.make_package(
                {".ai/race.txt": (b"race\n", "framework-managed", "0644")},
                [operation("001-add", "add", ".ai/race.txt")],
            )
            original_capture = APPLY.capture_target_git_snapshot
            captures = 0

            def raced_capture(*args: object, **kwargs: object):
                nonlocal captures
                snapshot = original_capture(*args, **kwargs)
                captures += 1
                if captures == 1:
                    fixture.add_target("concurrent.txt", b"concurrent\n")
                    fixture.commit_target("concurrent target commit")
                return snapshot

            with mock.patch.object(
                APPLY,
                "capture_target_git_snapshot",
                side_effect=raced_capture,
            ), self.assertRaisesRegex(
                APPLY.ApplyError, "identity changed during planning"
            ):
                fixture.plan()
            self.assertEqual(2, captures)
            self.assertFalse((fixture.target / ".ai/race.txt").exists())
        finally:
            fixture.close()

    def test_gwt_081_given_git_attributes_or_filemode_change_after_plan_when_apply_admits_then_semantic_drift_fails_closed(self) -> None:
        for mutation in ("attributes", "filemode"):
            with self.subTest(mutation=mutation):
                fixture = PackageApplyFixture()
                try:
                    relative = ".ai/semantic.txt"
                    fixture.make_package(
                        {relative: (b"semantic\n", "framework-managed", "0644")},
                        [operation("001-add", "add", relative)],
                    )
                    plan = fixture.plan()
                    if mutation == "attributes":
                        info_attributes = fixture.target / ".git/info/attributes"
                        info_attributes.write_text(
                            f"{relative} ident\n",
                            encoding="utf-8",
                            newline="\n",
                        )
                    else:
                        current = git(
                            fixture.target, "config", "--bool", "core.filemode"
                        ).stdout.strip()
                        git(
                            fixture.target,
                            "config",
                            "core.filemode",
                            "false" if current == "true" else "true",
                        )
                    with self.assertRaisesRegex(
                        APPLY.ApplyError,
                        "attributes, ignore rules, or core.filemode changed",
                    ):
                        RAW_APPLY_PLAN(plan)
                    self.assertFalse((fixture.target / relative).exists())
                finally:
                    fixture.close()

    def test_gwt_082_given_git_semantics_change_after_crash_when_resume_or_rollback_admits_then_recovery_does_not_mutate(self) -> None:
        for action in ("resume", "rollback"):
            with self.subTest(action=action):
                fixture = PackageApplyFixture()
                try:
                    fixture.make_package(
                        {
                            ".ai/first.md": (b"first\n", "framework-managed", "0644"),
                            ".ai/second.md": (b"second\n", "framework-managed", "0644"),
                        },
                        [
                            operation("001-first", "add", ".ai/first.md"),
                            operation("002-second", "add", ".ai/second.md"),
                        ],
                    )
                    plan = fixture.plan()

                    def crash(boundary: str, details: dict) -> None:
                        if boundary == "after_operation" and details.get("index") == 0:
                            raise APPLY.InjectedInterruption("recovery semantic fixture")

                    with self.assertRaises(APPLY.InjectedInterruption):
                        RAW_APPLY_PLAN(plan, boundary_hook=crash)
                    current = git(
                        fixture.target, "config", "--bool", "core.filemode"
                    ).stdout.strip()
                    git(
                        fixture.target,
                        "config",
                        "core.filemode",
                        "false" if current == "true" else "true",
                    )
                    with self.assertRaisesRegex(
                        APPLY.ApplyError,
                        "attributes, ignore rules, or core.filemode changed",
                    ):
                        APPLY.recover_transaction(
                            fixture.target,
                            plan["plan_sha256"],
                            action,
                            fixture.package if action == "resume" else None,
                        )
                    self.assertEqual(
                        b"first\n", (fixture.target / ".ai/first.md").read_bytes()
                    )
                    self.assertFalse((fixture.target / ".ai/second.md").exists())
                finally:
                    fixture.close()

    def test_gwt_083_given_unrelated_drift_is_found_at_terminal_scan_when_automatic_rollback_admits_then_no_rollback_mutation_starts(self) -> None:
        fixture = PackageApplyFixture()
        try:
            fixture.make_package(
                {
                    ".ai/first.md": (b"first\n", "framework-managed", "0644"),
                    ".ai/second.md": (b"second\n", "framework-managed", "0644"),
                },
                [
                    operation("001-first", "add", ".ai/first.md"),
                    operation("002-second", "add", ".ai/second.md"),
                ],
            )
            plan = fixture.plan()

            def drift(boundary: str, details: dict) -> None:
                if boundary == "after_progress_journal" and details.get("index") == 0:
                    (fixture.target / "unrelated.txt").write_text(
                        "external\n", encoding="utf-8", newline="\n"
                    )

            with self.assertRaisesRegex(
                APPLY.ApplyError, "rollback failed"
            ):
                RAW_APPLY_PLAN(plan, boundary_hook=drift)
            self.assertEqual(
                b"first\n", (fixture.target / ".ai/first.md").read_bytes()
            )
            self.assertEqual(
                b"second\n", (fixture.target / ".ai/second.md").read_bytes()
            )
            self.assertEqual(
                "external\n",
                (fixture.target / "unrelated.txt").read_text(encoding="utf-8"),
            )
            _root, _saved, journal = APPLY.load_transaction(
                fixture.target, plan["plan_sha256"]
            )
            self.assertEqual("interrupted", journal["state"])
            self.assertEqual([], journal["rollback_completed_paths"])
        finally:
            fixture.close()

    def test_gwt_084_given_unrelated_drift_after_recovery_snapshot_before_lock_admission_when_resume_starts_then_no_recovery_mutation_occurs(self) -> None:
        fixture = PackageApplyFixture()
        try:
            fixture.make_package(
                {
                    ".ai/first.md": (b"first\n", "framework-managed", "0644"),
                    ".ai/second.md": (b"second\n", "framework-managed", "0644"),
                },
                [
                    operation("001-first", "add", ".ai/first.md"),
                    operation("002-second", "add", ".ai/second.md"),
                ],
            )
            plan = fixture.plan()

            def crash(boundary: str, details: dict) -> None:
                if boundary == "after_operation" and details.get("index") == 0:
                    raise APPLY.InjectedInterruption("recovery lock-race fixture")

            with self.assertRaises(APPLY.InjectedInterruption):
                RAW_APPLY_PLAN(plan, boundary_hook=crash)
            original_capture = APPLY.capture_target_git_snapshot

            def drift_after_snapshot(*args: object, **kwargs: object):
                snapshot = original_capture(*args, **kwargs)
                (fixture.target / "lock-wait-drift.txt").write_text(
                    "external\n", encoding="utf-8", newline="\n"
                )
                return snapshot

            with mock.patch.object(
                APPLY,
                "capture_target_git_snapshot",
                side_effect=drift_after_snapshot,
            ), self.assertRaisesRegex(
                APPLY.ApplyError, "unrelated target changes block recovery"
            ):
                APPLY.recover_transaction(
                    fixture.target,
                    plan["plan_sha256"],
                    "resume",
                    fixture.package,
                )
            self.assertEqual(
                b"first\n", (fixture.target / ".ai/first.md").read_bytes()
            )
            self.assertFalse((fixture.target / ".ai/second.md").exists())
        finally:
            fixture.close()

    def test_gwt_085_given_ignore_rule_changes_after_crash_when_resume_or_rollback_admits_then_recovery_does_not_mutate(self) -> None:
        for action in ("resume", "rollback"):
            with self.subTest(action=action):
                fixture = PackageApplyFixture()
                try:
                    fixture.make_package(
                        {
                            ".ai/first.md": (
                                b"first\n",
                                "framework-managed",
                                "0644",
                            ),
                            ".ai/second.md": (
                                b"second\n",
                                "framework-managed",
                                "0644",
                            ),
                        },
                        [
                            operation("001-first", "add", ".ai/first.md"),
                            operation("002-second", "add", ".ai/second.md"),
                        ],
                    )
                    plan = fixture.plan()

                    def crash(boundary: str, details: dict) -> None:
                        if boundary == "after_operation" and details.get("index") == 0:
                            raise APPLY.InjectedInterruption(
                                "recovery ignore-semantic fixture"
                            )

                    with self.assertRaises(APPLY.InjectedInterruption):
                        RAW_APPLY_PLAN(plan, boundary_hook=crash)
                    (fixture.target / ".git/info/exclude").write_text(
                        ".ai/second.md\n", encoding="utf-8", newline="\n"
                    )
                    with self.assertRaisesRegex(
                        APPLY.ApplyError,
                        "attributes, ignore rules, or core.filemode changed",
                    ):
                        APPLY.recover_transaction(
                            fixture.target,
                            plan["plan_sha256"],
                            action,
                            fixture.package if action == "resume" else None,
                        )
                    self.assertEqual(
                        b"first\n", (fixture.target / ".ai/first.md").read_bytes()
                    )
                    self.assertFalse((fixture.target / ".ai/second.md").exists())
                finally:
                    fixture.close()

    def test_gwt_086_given_growing_multi_hop_checkpoint_surfaces_when_planned_then_git_process_count_remains_constant(self) -> None:
        observations: list[tuple[int, int, int]] = []
        for changed_count in (3, 631):
            with self.subTest(changed_count=changed_count):
                fixture = PackageApplyFixture()
                try:
                    relative = ".ai/next-hop.txt"
                    fixture.make_package(
                        {
                            relative: (
                                b"next\n",
                                "framework-managed",
                                "0644",
                            )
                        },
                        [operation("001-next", "add", relative)],
                    )
                    for index in range(changed_count):
                        path = (
                            fixture.target
                            / "checkpoint-surface"
                            / f"path-{index:04d}.txt"
                        )
                        path.parent.mkdir(parents=True, exist_ok=True)
                        path.write_text(
                            f"{index}\n", encoding="utf-8", newline="\n"
                        )
                    metrics: list[dict] = []

                    def verify_from_active_snapshot(
                        target: Path, context: object
                    ) -> dict:
                        self.assertIsNotNone(APPLY.active_target_git_snapshot(target))
                        APPLY._require_complete_multi_hop_checkpoint_evidence(target)
                        self.assertEqual(
                            changed_count,
                            len(APPLY.route_checkpoint_surface(target)),
                        )
                        return {"fixture": context}

                    with mock.patch.object(
                        APPLY,
                        "verify_multi_hop_checkpoint_for_planning",
                        side_effect=verify_from_active_snapshot,
                    ), mock.patch.object(
                        APPLY,
                        "run_git",
                        side_effect=AssertionError(
                            "multi-hop planning fell back to per-path Git"
                        ),
                    ):
                        plan = APPLY.build_plan(
                            fixture.package,
                            fixture.target,
                            multi_hop_checkpoint_context={
                                "changed_count": changed_count
                            },
                            git_inspection_hook=metrics.append,
                        )
                    self.assertEqual("fixture-v1.0.0", plan["package_id"])
                    self.assertEqual(1, len(metrics))
                    observations.append(
                        (
                            changed_count,
                            metrics[0]["path_count"],
                            metrics[0]["git_process_count"],
                        )
                    )
                finally:
                    fixture.close()
        self.assertEqual({item[2] for item in observations}, {24})
        self.assertEqual(
            [item[0] + 1 for item in observations],
            [item[1] for item in observations],
        )

    def test_gwt_087_given_ignore_policy_changes_after_apply_snapshot_when_admitted_then_target_is_not_mutated(self) -> None:
        for source in ("info-exclude", "core-excludes-file"):
            with self.subTest(source=source):
                fixture = PackageApplyFixture()
                try:
                    relative = ".ai/ignored-after-snapshot.md"
                    fixture.make_package(
                        {
                            relative: (
                                b"must remain absent\n",
                                "framework-managed",
                                "0644",
                            )
                        },
                        [operation("001-add", "add", relative)],
                    )
                    policy_path = fixture.target / ".git/info/exclude"
                    if source == "core-excludes-file":
                        policy_path = fixture.target / ".git/custom-ignore"
                        git(
                            fixture.target,
                            "config",
                            "core.excludesFile",
                            str(policy_path),
                        )
                    plan = fixture.plan()
                    original_capture = APPLY.capture_target_git_snapshot

                    def drift_after_snapshot(*args: object, **kwargs: object):
                        snapshot = original_capture(*args, **kwargs)
                        policy_path.write_text(
                            f"{relative}\n", encoding="utf-8", newline="\n"
                        )
                        return snapshot

                    with mock.patch.object(
                        APPLY,
                        "capture_target_git_snapshot",
                        side_effect=drift_after_snapshot,
                    ), self.assertRaisesRegex(
                        APPLY.ApplyError, "administrative identity changed"
                    ):
                        RAW_APPLY_PLAN(plan)
                    self.assertFalse((fixture.target / relative).exists())
                    ignored = subprocess.run(
                        ["git", "check-ignore", "--quiet", relative],
                        cwd=fixture.target,
                        check=False,
                        capture_output=True,
                        text=True,
                    )
                    self.assertEqual(0, ignored.returncode)
                finally:
                    fixture.close()

    def test_gwt_088_given_attribute_policy_changes_after_apply_snapshot_when_admitted_then_target_is_not_mutated(self) -> None:
        for source in ("info-attributes", "core-attributes-file"):
            with self.subTest(source=source):
                fixture = PackageApplyFixture()
                try:
                    relative = ".ai/attributed-after-snapshot.md"
                    fixture.make_package(
                        {
                            relative: (
                                b"must remain absent\n",
                                "framework-managed",
                                "0644",
                            )
                        },
                        [operation("001-add", "add", relative)],
                    )
                    policy_path = fixture.target / ".git/info/attributes"
                    if source == "core-attributes-file":
                        policy_path = fixture.target / ".git/custom-attributes"
                        git(
                            fixture.target,
                            "config",
                            "core.attributesFile",
                            str(policy_path),
                        )
                    plan = fixture.plan()
                    original_capture = APPLY.capture_target_git_snapshot

                    def drift_after_snapshot(*args: object, **kwargs: object):
                        snapshot = original_capture(*args, **kwargs)
                        policy_path.write_text(
                            f"{relative} filter=lfs\n",
                            encoding="utf-8",
                            newline="\n",
                        )
                        return snapshot

                    with mock.patch.object(
                        APPLY,
                        "capture_target_git_snapshot",
                        side_effect=drift_after_snapshot,
                    ), self.assertRaisesRegex(
                        APPLY.ApplyError, "administrative identity changed"
                    ):
                        RAW_APPLY_PLAN(plan)
                    self.assertFalse((fixture.target / relative).exists())
                    observed = git(
                        fixture.target,
                        "check-attr",
                        "filter",
                        "--",
                        relative,
                    )
                    self.assertIn("filter: lfs", observed.stdout)
                finally:
                    fixture.close()

    def test_gwt_089_given_preexisting_global_config_adds_ignore_policy_after_snapshot_when_admitted_then_target_is_not_mutated(self) -> None:
        fixture = PackageApplyFixture()
        try:
            relative = ".ai/global-ignore-after-snapshot.md"
            fixture.make_package(
                {
                    relative: (
                        b"must remain absent\n",
                        "framework-managed",
                        "0644",
                    )
                },
                [operation("001-add", "add", relative)],
            )
            global_config = fixture.root / "global.gitconfig"
            global_config.write_text(
                "[user]\n\tname = Existing Global Fixture\n",
                encoding="utf-8",
                newline="\n",
            )
            policy_path = fixture.root / "late-global-ignore"
            with mock.patch.dict(
                os.environ,
                {"GIT_CONFIG_GLOBAL": str(global_config)},
            ):
                plan = fixture.plan()
                original_capture = APPLY.capture_target_git_snapshot

                def drift_after_snapshot(*args: object, **kwargs: object):
                    snapshot = original_capture(*args, **kwargs)
                    global_config.write_text(
                        "[user]\n"
                        "\tname = Existing Global Fixture\n"
                        "[core]\n"
                        f"\texcludesFile = {policy_path.as_posix()}\n",
                        encoding="utf-8",
                        newline="\n",
                    )
                    policy_path.write_text(
                        f"{relative}\n", encoding="utf-8", newline="\n"
                    )
                    return snapshot

                with mock.patch.object(
                    APPLY,
                    "capture_target_git_snapshot",
                    side_effect=drift_after_snapshot,
                ), self.assertRaisesRegex(
                    APPLY.ApplyError, "administrative identity changed"
                ):
                    RAW_APPLY_PLAN(plan)
                self.assertFalse((fixture.target / relative).exists())
                ignored = subprocess.run(
                    ["git", "check-ignore", "--quiet", relative],
                    cwd=fixture.target,
                    check=False,
                    capture_output=True,
                    text=True,
                )
                self.assertEqual(0, ignored.returncode)
        finally:
            fixture.close()

    def test_gwt_090_given_preexisting_empty_include_adds_policy_after_snapshot_when_admitted_then_target_is_not_mutated(self) -> None:
        for policy in ("ignore", "attributes"):
            with self.subTest(policy=policy):
                fixture = PackageApplyFixture()
                try:
                    relative = f".ai/include-{policy}-after-snapshot.md"
                    fixture.make_package(
                        {
                            relative: (
                                b"must remain absent\n",
                                "framework-managed",
                                "0644",
                            )
                        },
                        [operation("001-add", "add", relative)],
                    )
                    global_config = fixture.root / "global.gitconfig"
                    included_config = fixture.root / "included.gitconfig"
                    global_config.write_text(
                        "[include]\n\tpath = included.gitconfig\n",
                        encoding="utf-8",
                        newline="\n",
                    )
                    included_config.write_text(
                        "# intentionally empty at snapshot\n",
                        encoding="utf-8",
                        newline="\n",
                    )
                    policy_path = fixture.root / f"late-include-{policy}"
                    with mock.patch.dict(
                        os.environ,
                        {"GIT_CONFIG_GLOBAL": str(global_config)},
                    ):
                        plan = fixture.plan()
                        original_capture = APPLY.capture_target_git_snapshot

                        def drift_after_snapshot(*args: object, **kwargs: object):
                            snapshot = original_capture(*args, **kwargs)
                            key = (
                                "excludesFile"
                                if policy == "ignore"
                                else "attributesFile"
                            )
                            included_config.write_text(
                                f"[core]\n\t{key} = {policy_path.as_posix()}\n",
                                encoding="utf-8",
                                newline="\n",
                            )
                            policy_line = (
                                f"{relative}\n"
                                if policy == "ignore"
                                else f"{relative} filter=lfs\n"
                            )
                            policy_path.write_text(
                                policy_line, encoding="utf-8", newline="\n"
                            )
                            return snapshot

                        with mock.patch.object(
                            APPLY,
                            "capture_target_git_snapshot",
                            side_effect=drift_after_snapshot,
                        ), self.assertRaisesRegex(
                            APPLY.ApplyError, "administrative identity changed"
                        ):
                            RAW_APPLY_PLAN(plan)
                        self.assertFalse((fixture.target / relative).exists())
                finally:
                    fixture.close()

    def test_gwt_091_given_absent_global_config_appears_after_snapshot_when_admitted_then_target_is_not_mutated(self) -> None:
        fixture = PackageApplyFixture()
        try:
            relative = ".ai/absent-global-after-snapshot.md"
            fixture.make_package(
                {
                    relative: (
                        b"must remain absent\n",
                        "framework-managed",
                        "0644",
                    )
                },
                [operation("001-add", "add", relative)],
            )
            global_config = fixture.root / "absent-at-snapshot.gitconfig"
            policy_path = fixture.root / "late-global-ignore"
            with mock.patch.dict(
                os.environ,
                {"GIT_CONFIG_GLOBAL": str(global_config)},
            ):
                plan = fixture.plan()
                original_capture = APPLY.capture_target_git_snapshot

                def drift_after_snapshot(*args: object, **kwargs: object):
                    snapshot = original_capture(*args, **kwargs)
                    global_config.write_text(
                        f"[core]\n\texcludesFile = {policy_path.as_posix()}\n",
                        encoding="utf-8",
                        newline="\n",
                    )
                    policy_path.write_text(
                        f"{relative}\n", encoding="utf-8", newline="\n"
                    )
                    return snapshot

                with mock.patch.object(
                    APPLY,
                    "capture_target_git_snapshot",
                    side_effect=drift_after_snapshot,
                ), self.assertRaisesRegex(
                    APPLY.ApplyError, "administrative identity changed"
                ):
                    RAW_APPLY_PLAN(plan)
                self.assertFalse((fixture.target / relative).exists())
        finally:
            fixture.close()

    def test_gwt_092_given_local_config_has_relative_dormant_include_when_policy_appears_after_snapshot_then_target_is_not_mutated(self) -> None:
        for policy in ("ignore", "attributes"):
            with self.subTest(policy=policy):
                fixture = PackageApplyFixture()
                try:
                    relative = f".ai/local-include-{policy}-after-snapshot.md"
                    fixture.make_package(
                        {
                            relative: (
                                b"must remain absent\n",
                                "framework-managed",
                                "0644",
                            )
                        },
                        [operation("001-add", "add", relative)],
                    )
                    included_config = fixture.target / ".git" / f"dormant-{policy}.gitconfig"
                    git(
                        fixture.target,
                        "config",
                        "include.path",
                        included_config.name,
                    )
                    policy_path = fixture.root / f"late-local-{policy}"
                    plan = fixture.plan()
                    original_capture = APPLY.capture_target_git_snapshot

                    def drift_after_snapshot(*args: object, **kwargs: object):
                        snapshot = original_capture(*args, **kwargs)
                        key = (
                            "excludesFile"
                            if policy == "ignore"
                            else "attributesFile"
                        )
                        included_config.write_text(
                            f"[core]\n\t{key} = {policy_path.as_posix()}\n",
                            encoding="utf-8",
                            newline="\n",
                        )
                        policy_line = (
                            f"{relative}\n"
                            if policy == "ignore"
                            else f"{relative} filter=lfs\n"
                        )
                        policy_path.write_text(
                            policy_line, encoding="utf-8", newline="\n"
                        )
                        return snapshot

                    with mock.patch.object(
                        APPLY,
                        "capture_target_git_snapshot",
                        side_effect=drift_after_snapshot,
                    ), self.assertRaisesRegex(
                        APPLY.ApplyError, "administrative identity changed"
                    ):
                        RAW_APPLY_PLAN(plan)
                    self.assertFalse((fixture.target / relative).exists())
                finally:
                    fixture.close()

    def test_gwt_093_given_config_changes_during_snapshot_when_semantics_were_already_read_then_capture_fails_closed(self) -> None:
        for policy in ("ignore", "attributes"):
            with self.subTest(policy=policy):
                fixture = PackageApplyFixture()
                try:
                    relative = f".ai/in-capture-{policy}.md"
                    fixture.make_package(
                        {
                            relative: (
                                b"must remain absent\n",
                                "framework-managed",
                                "0644",
                            )
                        },
                        [operation("001-add", "add", relative)],
                    )
                    global_config = fixture.root / "global.gitconfig"
                    global_config.write_text(
                        "[user]\n\tname = Existing Global Fixture\n",
                        encoding="utf-8",
                        newline="\n",
                    )
                    policy_path = fixture.root / f"in-capture-{policy}"
                    with mock.patch.dict(
                        os.environ,
                        {"GIT_CONFIG_GLOBAL": str(global_config)},
                    ):
                        plan = fixture.plan()
                        original_snapshot_git = APPLY._snapshot_git
                        changed = False

                        def drift_during_snapshot(
                            root: Path,
                            stats: object,
                            *args: str,
                            **kwargs: object,
                        ):
                            nonlocal changed
                            result = original_snapshot_git(
                                root,
                                stats,
                                *args,
                                **kwargs,
                            )
                            if args and args[0] == "check-ignore" and not changed:
                                changed = True
                                key = (
                                    "excludesFile"
                                    if policy == "ignore"
                                    else "attributesFile"
                                )
                                global_config.write_text(
                                    "[user]\n"
                                    "\tname = Existing Global Fixture\n"
                                    "[core]\n"
                                    f"\t{key} = {policy_path.as_posix()}\n",
                                    encoding="utf-8",
                                    newline="\n",
                                )
                                policy_line = (
                                    f"{relative}\n"
                                    if policy == "ignore"
                                    else f"{relative} filter=lfs\n"
                                )
                                policy_path.write_text(
                                    policy_line,
                                    encoding="utf-8",
                                    newline="\n",
                                )
                            return result

                        with mock.patch.object(
                            APPLY,
                            "_snapshot_git",
                            side_effect=drift_during_snapshot,
                        ), self.assertRaisesRegex(
                            APPLY.ApplyError,
                            "configuration changed while snapshot was captured",
                        ):
                            RAW_APPLY_PLAN(plan)
                    self.assertTrue(changed)
                    self.assertFalse((fixture.target / relative).exists())
                finally:
                    fixture.close()

    def test_gwt_094_given_windows_git_home_differs_from_userprofile_when_default_policy_changes_then_apply_fails_closed(self) -> None:
        for policy in ("ignore", "attributes"):
            for source in ("default-global", "default-policy"):
                with self.subTest(policy=policy, source=source):
                    fixture = PackageApplyFixture()
                    try:
                        relative = f".ai/home-{source}-{policy}.md"
                        fixture.make_package(
                            {
                                relative: (
                                    b"must remain absent\n",
                                    "framework-managed",
                                    "0644",
                                )
                            },
                            [operation("001-add", "add", relative)],
                        )
                        git_home = fixture.root / "git-home"
                        git_home.mkdir()
                        global_config = git_home / ".gitconfig"
                        if source == "default-global":
                            policy_path = git_home / f"late-{policy}"
                        else:
                            policy_path = git_home / ".config" / "git" / policy
                        with mock.patch.dict(
                            os.environ,
                            {"HOME": str(git_home)},
                        ):
                            os.environ.pop("GIT_CONFIG_GLOBAL", None)
                            os.environ.pop("XDG_CONFIG_HOME", None)
                            plan = fixture.plan()
                            original_capture = APPLY.capture_target_git_snapshot

                            def drift_after_snapshot(*args: object, **kwargs: object):
                                snapshot = original_capture(*args, **kwargs)
                                policy_path.parent.mkdir(parents=True, exist_ok=True)
                                if source == "default-global":
                                    key = (
                                        "excludesFile"
                                        if policy == "ignore"
                                        else "attributesFile"
                                    )
                                    global_config.write_text(
                                        f"[core]\n\t{key} = ~/{policy_path.name}\n",
                                        encoding="utf-8",
                                        newline="\n",
                                    )
                                policy_line = (
                                    f"{relative}\n"
                                    if policy == "ignore"
                                    else f"{relative} filter=lfs\n"
                                )
                                policy_path.write_text(
                                    policy_line,
                                    encoding="utf-8",
                                    newline="\n",
                                )
                                return snapshot

                            with mock.patch.object(
                                APPLY,
                                "capture_target_git_snapshot",
                                side_effect=drift_after_snapshot,
                            ), self.assertRaisesRegex(
                                APPLY.ApplyError,
                                "administrative identity changed",
                            ):
                                RAW_APPLY_PLAN(plan)
                            self.assertFalse((fixture.target / relative).exists())
                            if policy == "ignore":
                                self.assertEqual(
                                    0,
                                    subprocess.run(
                                        ["git", "check-ignore", "--quiet", relative],
                                        cwd=fixture.target,
                                        check=False,
                                    ).returncode,
                                )
                            else:
                                self.assertIn(
                                    "filter: lfs",
                                    git(
                                        fixture.target,
                                        "check-attr",
                                        "filter",
                                        "--",
                                        relative,
                                    ).stdout,
                                )
                    finally:
                        fixture.close()

    def test_gwt_095_given_raw_global_selector_uses_platform_path_resolution_when_git_admin_config_changes_then_apply_fails_closed(self) -> None:
        for policy in ("ignore", "attributes"):
            with self.subTest(policy=policy):
                fixture = PackageApplyFixture()
                try:
                    relative = f".ai/literal-selector-{policy}.md"
                    fixture.make_package(
                        {
                            relative: (
                                b"must remain absent\n",
                                "framework-managed",
                                "0644",
                            )
                        },
                        [operation("001-add", "add", relative)],
                    )
                    git_home = fixture.root / "git-home"
                    git_home.mkdir()
                    selector = "~/../.git/audit-global"
                    actual_config = fixture.target / ".git" / "audit-global"
                    policy_path = fixture.target / ".git" / f"audit-{policy}"
                    with mock.patch.dict(
                        os.environ,
                        {
                            "HOME": str(git_home),
                            "GIT_CONFIG_GLOBAL": selector,
                        },
                    ):
                        plan = fixture.plan()
                        original_capture = APPLY.capture_target_git_snapshot

                        def drift_after_snapshot(*args: object, **kwargs: object):
                            snapshot = original_capture(*args, **kwargs)
                            if os.name != "nt":
                                # POSIX must traverse the literal '~' component
                                # before '..'; creating it makes the raw selector
                                # resolve to the same config Windows can reach
                                # through lexical normalization.
                                (fixture.target / "~").mkdir()
                            key = (
                                "excludesFile"
                                if policy == "ignore"
                                else "attributesFile"
                            )
                            actual_config.write_text(
                                f"[core]\n\t{key} = {policy_path.as_posix()}\n",
                                encoding="utf-8",
                                newline="\n",
                            )
                            policy_line = (
                                f"{relative}\n"
                                if policy == "ignore"
                                else f"{relative} filter=lfs\n"
                            )
                            policy_path.write_text(
                                policy_line,
                                encoding="utf-8",
                                newline="\n",
                            )
                            return snapshot

                        with mock.patch.object(
                            APPLY,
                            "capture_target_git_snapshot",
                            side_effect=drift_after_snapshot,
                        ), self.assertRaisesRegex(
                            APPLY.ApplyError,
                            "administrative identity changed",
                        ):
                            RAW_APPLY_PLAN(plan)
                        self.assertFalse((fixture.target / relative).exists())
                        if policy == "ignore":
                            self.assertEqual(
                                0,
                                subprocess.run(
                                    ["git", "check-ignore", "--quiet", relative],
                                    cwd=fixture.target,
                                    check=False,
                                ).returncode,
                            )
                        else:
                            self.assertIn(
                                "filter: lfs",
                                git(
                                    fixture.target,
                                    "check-attr",
                                    "filter",
                                    "--",
                                    relative,
                                ).stdout,
                            )
                finally:
                    fixture.close()


if __name__ == "__main__":
    unittest.main()
