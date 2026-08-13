#!/usr/bin/env python3
"""Synthetic extracted-envelope tests for PKG-012 portable package validation."""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[3]
SCRIPTS = ROOT / ".ai/scripts"
sys.path.insert(0, str(SCRIPTS))
from ai_context_package_validation import (  # noqa: E402
    PackageValidationError,
    canonical_json_bytes,
    validate_extracted_package,
)


PACKAGE_ID = "ai-context-dotnet-backend-0.13.0"
VALIDATOR_PATH = ".ai/scripts/validate-ai-context-payload.py"


def sha256(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def yaml_bytes(document: dict) -> bytes:
    return yaml.safe_dump(
        document, sort_keys=False, allow_unicode=True, default_flow_style=False
    ).encode("utf-8")


def payload_fingerprint(records: list[dict]) -> str:
    return sha256(
        "".join(f"{record['sha256']}  {record['path']}\n" for record in records).encode(
            "utf-8"
        )
    )


def write_file(root: Path, relative: str, content: bytes) -> Path:
    path = root.joinpath(*relative.split("/"))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)
    return path


def rewrite_checksums(package_root: Path) -> None:
    members: list[tuple[str, bytes]] = []
    for path in package_root.rglob("*"):
        if not path.is_file() or path.is_symlink():
            continue
        relative = path.relative_to(package_root).as_posix()
        if relative == "metadata/SHA256SUMS.txt":
            continue
        members.append((relative, path.read_bytes()))
    lines = "".join(
        f"{sha256(content)}  {relative}\n"
        for relative, content in sorted(members, key=lambda item: item[0].encode("utf-8"))
    )
    write_file(package_root, "metadata/SHA256SUMS.txt", lines.encode("utf-8"))


def build_fixture(
    root: Path,
    *,
    portable_source: bytes | None = None,
    extra_payload: dict[str, bytes] | None = None,
    modes: dict[str, str] | None = None,
) -> Path:
    """Build a complete synthetic extracted package without calling the builder."""

    package_root = root / PACKAGE_ID
    package_root.mkdir()
    payload: dict[str, bytes] = {
        VALIDATOR_PATH: (SCRIPTS / "validate-ai-context-payload.py").read_bytes(),
        ".ai/scripts/ai_context_package_validation.py": (
            SCRIPTS / "ai_context_package_validation.py"
        ).read_bytes(),
        ".ai/scripts/python-entrypoints.json": json.dumps(
            {
                "schema_version": "1.0",
                "entrypoints": [
                    {"path": VALIDATOR_PATH, "portable": True},
                    {"path": ".ai/scripts/portable.py", "portable": True},
                    {"path": ".ai/scripts/source-only.py", "portable": False},
                ],
            },
            separators=(",", ":"),
            sort_keys=True,
        ).encode("utf-8")
        + b"\n",
        ".ai/scripts/portable.py": portable_source
        if portable_source is not None
        else b"#!/usr/bin/env python3\nimport argparse\nargparse.ArgumentParser().parse_args()\n",
        ".ai/assets/shared/example.md": b"# Portable fixture\n",
    }
    payload.update(extra_payload or {})
    for relative, content in payload.items():
        write_file(package_root, f"payload/{relative}", content)

    modes = modes or {}
    records = [
        {
            "path": relative,
            "sha256": sha256(content),
            "size": len(content),
            "mode": modes.get(relative, "0644"),
            "ownership": "framework-managed",
            "install_behavior": "managed",
            "component_id": "software-development-core",
        }
        for relative, content in sorted(payload.items(), key=lambda item: item[0].encode("utf-8"))
    ]
    files_document = {
        "schema_version": "2.0.0",
        "package_id": PACKAGE_ID,
        "files": records,
    }
    files_content = yaml_bytes(files_document)
    migration_document = {
        "schema_version": "3.0.0",
        "package_id": PACKAGE_ID,
        "to": {"version": "0.13.0", "manifest_sha256": sha256(files_content)},
        "sources": [],
    }
    migration_content = yaml_bytes(migration_document)
    proof = {
        "schema_version": "package-selected-input/v1",
        "source_inputs": [
            {"path": ".ai/distribution/profiles/demo.yaml", "sha256": sha256(b"profile\n")}
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
        "migration_sources": [],
    }
    proof_content = canonical_json_bytes(proof)
    validator_content = payload[VALIDATOR_PATH]
    validation = {
        "schema_version": "package-validation/v1",
        "package_id": PACKAGE_ID,
        "authority": {
            "kind": "incoming-candidate",
            "validator": {
                "path": VALIDATOR_PATH,
                "sha256": sha256(validator_content),
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
            "sha256": sha256(proof_content),
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
    validation_content = json.dumps(
        validation, ensure_ascii=False, separators=(",", ":"), sort_keys=True
    ).encode("utf-8")
    package = {
        "schema_version": "2.3.0",
        "package_id": PACKAGE_ID,
        "identity": {
            "schema_version": "1.0.0",
            "selected_input_fingerprint": sha256(proof_content),
            "payload_fingerprint": payload_fingerprint(records),
            "files_manifest_digest": sha256(files_content),
            "migration_digest": sha256(migration_content),
        },
        "payload": {
            "root": "payload",
            "file_count": len(records),
            "sha256": payload_fingerprint(records),
        },
        "validation": {
            "manifest": "metadata/validation.json",
            "manifest_sha256": sha256(validation_content),
            "selected_inputs": "metadata/selected-inputs.json",
            "selected_inputs_sha256": sha256(proof_content),
        },
    }
    write_file(package_root, "INSTALL.md", b"# Install\n")
    write_file(package_root, "requirements.txt", b"PyYAML==6.0.3\n")
    write_file(package_root, "metadata/package.yaml", yaml_bytes(package))
    write_file(package_root, "metadata/files.yaml", files_content)
    write_file(package_root, "metadata/migration.yaml", migration_content)
    write_file(package_root, "metadata/validation.json", validation_content)
    write_file(package_root, "metadata/selected-inputs.json", proof_content)
    rewrite_checksums(package_root)
    return package_root


class PackageValidationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory(
            dir=ROOT / ".ai/scripts/tests"
        )
        self.root = Path(self.temporary_directory.name)

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    def test_given_complete_synthetic_envelope_when_validated_then_it_is_portable(self) -> None:
        package_root = build_fixture(self.root)

        result = validate_extracted_package(package_root)

        self.assertEqual(PACKAGE_ID, result["package_id"])
        self.assertEqual(2, result["portable_entrypoints_verified"])
        self.assertEqual("excluded-from-portable-validation", result["source_only_tests"])

    def test_given_apply_reader_mode_when_portable_command_would_fail_then_execution_is_skipped_only(self) -> None:
        package_root = build_fixture(
            self.root,
            portable_source=b"import missing_portable_fixture_dependency\n",
        )

        result = validate_extracted_package(package_root, run_portable_entrypoints=False)

        self.assertEqual(0, result["portable_entrypoints_verified"])
        self.assertEqual("skipped", result["portable_entrypoints_execution"])

    def test_given_missing_portable_import_when_isolated_help_runs_then_it_fails_closed(self) -> None:
        package_root = build_fixture(
            self.root,
            portable_source=b"import missing_portable_fixture_dependency\n",
        )

        with self.assertRaisesRegex(PackageValidationError, "portable entrypoint --help failed"):
            validate_extracted_package(package_root)

    def test_given_validator_identity_mismatch_when_validated_then_it_fails_closed(self) -> None:
        package_root = build_fixture(self.root)
        package_path = package_root / "metadata/package.yaml"
        package = yaml.safe_load(package_path.read_text(encoding="utf-8"))
        package["validation"]["manifest_sha256"] = "0" * 64
        package_path.write_bytes(yaml_bytes(package))
        rewrite_checksums(package_root)

        with self.assertRaisesRegex(PackageValidationError, "manifest_sha256"):
            validate_extracted_package(package_root, run_portable_entrypoints=False)

    def test_given_noncanonical_selected_proof_when_validated_then_it_fails_closed(self) -> None:
        package_root = build_fixture(self.root)
        proof_path = package_root / "metadata/selected-inputs.json"
        proof = json.loads(proof_path.read_text(encoding="utf-8"))
        proof_path.write_text(json.dumps(proof, indent=2), encoding="utf-8", newline="\n")
        proof_bytes = proof_path.read_bytes()
        validation_path = package_root / "metadata/validation.json"
        validation = json.loads(validation_path.read_text(encoding="utf-8"))
        validation["selected_input_proof"]["sha256"] = sha256(proof_bytes)
        validation_path.write_text(
            json.dumps(validation, separators=(",", ":"), sort_keys=True),
            encoding="utf-8",
            newline="",
        )
        package_path = package_root / "metadata/package.yaml"
        package = yaml.safe_load(package_path.read_text(encoding="utf-8"))
        package["validation"]["selected_inputs_sha256"] = sha256(proof_bytes)
        package["validation"]["manifest_sha256"] = sha256(validation_path.read_bytes())
        package["identity"]["selected_input_fingerprint"] = sha256(proof_bytes)
        package_path.write_bytes(yaml_bytes(package))
        rewrite_checksums(package_root)

        with self.assertRaisesRegex(PackageValidationError, "canonical compact sorted JSON"):
            validate_extracted_package(package_root, run_portable_entrypoints=False)

    def test_given_source_only_test_in_payload_when_validated_then_it_fails_closed(self) -> None:
        package_root = build_fixture(
            self.root,
            extra_payload={".ai/scripts/tests/test_leak.py": b"# source only\n"},
        )

        with self.assertRaisesRegex(PackageValidationError, "source-only test is present"):
            validate_extracted_package(package_root, run_portable_entrypoints=False)

    def test_given_invalid_text_or_mode_when_validated_then_it_fails_closed(self) -> None:
        cases = {
            "eof": ({"docs/bad.md": b"bad\n\n"}, {}, "exactly one terminal LF"),
            "crlf": ({"docs/bad.md": b"bad\r\n"}, {}, "not LF-only"),
            "utf8": ({"docs/bad.md": b"\xff\n"}, {}, "not UTF-8"),
            "mode": ({}, {".ai/scripts/portable.py": "0640"}, "invalid mode"),
        }
        for name, (extra, modes, expected) in cases.items():
            with self.subTest(name=name):
                with tempfile.TemporaryDirectory(dir=ROOT / ".ai/scripts/tests") as temporary:
                    package_root = build_fixture(
                        Path(temporary), extra_payload=extra, modes=modes
                    )
                    with self.assertRaisesRegex(PackageValidationError, expected):
                        validate_extracted_package(package_root, run_portable_entrypoints=False)

    @unittest.skipIf(os.name == "nt", "Windows filesystems cannot construct case-fold collisions")
    def test_given_casefold_collision_when_validated_then_it_fails_closed(self) -> None:
        package_root = build_fixture(
            self.root,
            extra_payload={"docs/Foo.md": b"A\n", "docs/foo.md": b"B\n"},
        )

        with self.assertRaisesRegex(PackageValidationError, "case-fold collision"):
            validate_extracted_package(package_root, run_portable_entrypoints=False)

    def test_given_cli_when_complete_envelope_is_given_then_summary_excludes_source_only_tests(self) -> None:
        package_root = build_fixture(self.root)
        cli = package_root / "payload" / ".ai/scripts/validate-ai-context-payload.py"

        result = subprocess.run(
            [sys.executable, str(cli), "--package-root", "."],
            cwd=package_root,
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("source_only_tests=excluded-from-portable-validation", result.stdout)


if __name__ == "__main__":
    unittest.main()
