#!/usr/bin/env python3
"""Validate one Candidate11 v0.18 direct edge without source admission.

This template deliberately proves a narrow C10-to-C11 archive rebind.  It
retains the C10 actual target execution evidence as an immutable baseline and
performs only the archive-declared portable validation for C11.  It never reads
the source checkout, a support matrix admission result, or a current payload
file.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import subprocess
import sys
import tempfile
import zipfile

import yaml

sys.dont_write_bytecode = True

ORIGINS = ("v0.6.0", "v0.9.0", "v0.17.0")
C10_ARCHIVE_SHA256 = "90e403bde5e1e84767a4c00b67923780ebea76222b7956e598c814241c0f7db0"
C10_SUBJECT_SHA = "f566a6014f0942a15b28a39f0b2f5df3303e6014"
C10_RUNNER_PATH = ".github/scripts/validate-v018-direct-upgrades.py"
C10_RUNNER_SHA256 = "60df0a1c2fc0217c104467d23a23b65245d3360fbc04291ff26387470b4e199b"
C10_TERMINAL_SHA256 = "04885cbbb8c3dc6823867f7ed73be102c2c427b3b34602080204b0f12782a3ca"
C10_CASE_INDEX_SHA256 = "3e4f5dab025e408f6588959f9bb8c328835721c9b2b5f6886dcee575c127978a"
C10_BASELINE_MATRIX_SHA256 = "d95c5ee82b97013f46f9a52a54ec54e698f94706cb0c29280f44c93b84417c30"
C10_PAYLOAD_FINGERPRINT = "3af97c3d986f13aeec45dfd1efc123700cbf4d3d4378af178cfcedc34a85e64d"
PAYLOAD_MODE = "0644"
PAYLOAD_DELTAS = (
    (
        ".ai/scripts/shell-assets.yaml",
        b"  - python .ai/scripts/tests/test_code_reviewer_routing_contract.py -v\n",
        b"  - python .ai/scripts/tests/test_runtime_skill_entries.py -v\n",
    ),
    (
        ".ai/scripts/validate-dependency-versions.py",
        b"    expected_exit_two = {\n",
        b"        \".ai/assets/skills/ai-context-upgrader/scripts/run-target-validation.py\",\n",
    ),
)
CASES = (
    "v0.6.0-pristine-resume", "v0.6.0-customized-none", "v0.6.0-customized-rollback",
    "v0.9.0-pristine-resume", "v0.9.0-customized-none", "v0.9.0-customized-rollback",
    "v0.17.0-pristine-resume", "v0.17.0-customized-none", "v0.17.0-customized-rollback",
)


def canonical(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True,
                       separators=(",", ":"), allow_nan=False) + "\n").encode("utf-8")


def digest(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def fail(message: str) -> None:
    raise RuntimeError(message)


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def read_json(path: Path) -> dict:
    try:
        value = json.loads(path.read_bytes())
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"invalid JSON: {path.name}") from exc
    require(isinstance(value, dict), f"JSON object required: {path.name}")
    return value


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(canonical(value))


def safe_relative(value: str) -> PurePosixPath:
    require(isinstance(value, str) and value, "nonempty relative path required")
    item = PurePosixPath(value)
    require(not item.is_absolute() and ".." not in item.parts and "\\" not in value and ":" not in value,
            "unsafe relative path")
    return item


def under(root: Path, relative: str) -> Path:
    item = root / safe_relative(relative)
    require(item.resolve().is_relative_to(root.resolve()), "asset path escapes staged root")
    require(item.is_file() and not item.is_symlink(), "asset is absent or a symlink")
    return item


def asset(root: Path, identity: dict) -> tuple[dict, Path]:
    require(isinstance(identity, dict) and set(identity) == {"asset_id", "path", "sha256"},
            "invalid asset identity")
    require(all(isinstance(identity[key], str) and identity[key] for key in identity), "empty asset identity")
    require(len(identity["sha256"]) == 64 and all(ch in "0123456789abcdef" for ch in identity["sha256"]),
            "invalid asset digest")
    path = under(root, identity["path"])
    require(digest(path.read_bytes()) == identity["sha256"], "staged asset digest mismatch")
    return identity, path


def extract_zip(archive: Path, destination: Path) -> Path:
    with zipfile.ZipFile(archive) as opened:
        names: set[str] = set()
        for member in opened.infolist():
            name = member.filename
            member_path = PurePosixPath(name)
            require(name not in names, "duplicate ZIP member")
            names.add(name)
            require(not member_path.is_absolute() and ".." not in member_path.parts and "\\" not in name and ":" not in name,
                    "unsafe ZIP member")
            require((member.external_attr >> 16) & 0o170000 != 0o120000, "ZIP symlink not allowed")
            candidate = destination / member_path
            require(candidate.resolve().is_relative_to(destination.resolve()), "ZIP member escapes extraction root")
        opened.extractall(destination)
    children = [child for child in destination.iterdir() if not child.name.startswith("__MACOSX")]
    require(len(children) == 1 and children[0].is_dir(), "package archive must have one envelope directory")
    return children[0]


def c10_execution_set() -> dict:
    return {
        "schema_version": "v018-direct-upgrade-rebind/v1",
        "release": "v0.18.0",
        "authority": "user-authorized-excessive-validation-rebind",
        "original": {
            "archive_sha256": C10_ARCHIVE_SHA256,
            "subject_sha": C10_SUBJECT_SHA,
            "runner": {"path": C10_RUNNER_PATH, "sha256": C10_RUNNER_SHA256},
            "terminal": {"path": "terminal.json", "sha256": C10_TERMINAL_SHA256},
            "case_evidence_index": {
                "path": "case-evidence-index.json", "sha256": C10_CASE_INDEX_SHA256,
                "evidence_count": 236,
            },
            "baseline_support_matrix": {
                "path": "baseline-support-matrix.yaml", "sha256": C10_BASELINE_MATRIX_SHA256,
            },
            "baseline_archive": {"path": "baseline.zip", "sha256": C10_ARCHIVE_SHA256},
        },
        "cases": list(CASES),
        "allowed_payload_deltas": [
            {
                "path": path,
                "mode": PAYLOAD_MODE,
                "anchor": anchor.decode("ascii"),
                "addition": addition.decode("ascii"),
            }
            for path, anchor, addition in PAYLOAD_DELTAS
        ],
    }


def c10_assets() -> dict:
    return {
        "execution_set": {
            "asset_id": "actual-direct-v018-execution-set",
            "path": "route-assets/actual/execution-set.json",
            "sha256": digest(canonical(c10_execution_set())),
        },
        "baseline_archive": {
            "asset_id": "actual-direct-v018-baseline-archive",
            "path": "route-assets/actual/baseline.zip", "sha256": C10_ARCHIVE_SHA256,
        },
        "baseline_support_matrix": {
            "asset_id": "actual-direct-v018-baseline-support-matrix",
            "path": "route-assets/actual/baseline-support-matrix.yaml", "sha256": C10_BASELINE_MATRIX_SHA256,
        },
        "terminal": {
            "asset_id": "actual-direct-v018-terminal",
            "path": "route-assets/actual/terminal.json", "sha256": C10_TERMINAL_SHA256,
        },
        "runner": {
            "asset_id": "v018-direct-runner",
            "path": "route-assets/actual/validate-v018-direct-upgrades.py", "sha256": C10_RUNNER_SHA256,
        },
        "case_evidence_index": {
            "asset_id": "actual-direct-v018-case-evidence-index",
            "path": "route-assets/actual/case-evidence-index.json", "sha256": C10_CASE_INDEX_SHA256,
        },
    }


def expected_cases(terminal: dict) -> None:
    require(terminal.get("schema_version") == "direct-upgrade-execution/v1", "terminal schema mismatch")
    require(terminal.get("evidence_kind") == "actual-isolated-target-execution", "terminal is not actual execution")
    require(terminal.get("outcome") == "passed", "terminal outcome is not passed")
    require(terminal.get("archive_sha256") == C10_ARCHIVE_SHA256, "terminal archive is not Candidate10")
    require(terminal.get("subject_sha") == C10_SUBJECT_SHA, "terminal subject is not Candidate10")
    require(terminal.get("package_source", {}).get("commit") == C10_SUBJECT_SHA,
            "terminal package source is not Candidate10")
    require(terminal.get("runner") == {"path": C10_RUNNER_PATH, "sha256": C10_RUNNER_SHA256},
            "terminal runner binding mismatch")
    cases = terminal.get("cases")
    require(isinstance(cases, list) and len(cases) == 9, "terminal must contain exactly nine cases")
    expected = {
        (origin, f"{origin}-pristine-resume", "resume") for origin in ORIGINS
    } | {
        (origin, f"{origin}-customized-none", "none") for origin in ORIGINS
    } | {
        (origin, f"{origin}-customized-rollback", "rolled-back") for origin in ORIGINS
    }
    observed = set()
    for case in cases:
        require(isinstance(case, dict), "terminal case must be an object")
        observed.add((case.get("origin"), case.get("case"), case.get("recovery")))
        require(case.get("outcome") == "passed", "terminal contains a nonpassing case")
        require(isinstance(case.get("prestate_sha256"), str) and isinstance(case.get("poststate_sha256"), str),
                "terminal case lacks exact state identities")
        artifacts = case.get("artifacts")
        require(isinstance(artifacts, dict) and artifacts, "terminal case lacks retained artifacts")
        if case.get("recovery") != "rolled-back":
            target = case.get("target_validation")
            require(isinstance(target, dict) and target.get("outcome") == "passed" and target.get("exit_code") == 0,
                    "completed case lacks passing target validation")
    require(observed == expected, "terminal does not represent the exact direct v0.18 case set")


def validate_case_evidence_index(root: Path, path: Path) -> None:
    index = read_json(path)
    expected_terminal = {
        "asset_id": "actual-direct-v018-terminal",
        "path": "actual/terminal.json",
        "sha256": C10_TERMINAL_SHA256,
    }
    entries = index.get("evidence") if isinstance(index, dict) else None
    require(set(index) == {"schema_version", "terminal", "evidence"}
            and index.get("schema_version") == "v018-direct-case-evidence-index/v1"
            and index.get("terminal") == expected_terminal
            and isinstance(entries, list) and len(entries) == 236,
            "Candidate10 case evidence index differs")
    paths, asset_ids = set(), set()
    for entry in entries:
        require(isinstance(entry, dict) and set(entry) == {"staged", "terminal_path"},
                "Candidate10 case evidence entry is invalid")
        staged, terminal_path = entry["staged"], entry["terminal_path"]
        require(isinstance(staged, dict) and set(staged) == {"asset_id", "path", "sha256"}
                and isinstance(terminal_path, str) and terminal_path
                and staged.get("path") == f"actual/{terminal_path}"
                and isinstance(staged.get("asset_id"), str) and staged["asset_id"]
                and isinstance(staged.get("sha256"), str) and len(staged["sha256"]) == 64
                and all(ch in "0123456789abcdef" for ch in staged["sha256"])
                and terminal_path not in paths and staged["asset_id"] not in asset_ids,
                "Candidate10 case evidence entry differs")
        observed = under(root, f"route-assets/{staged['path']}").read_bytes()
        require(digest(observed) == staged["sha256"], "Candidate10 case evidence bytes changed")
        paths.add(terminal_path)
        asset_ids.add(staged["asset_id"])


def payload_entries(content: bytes) -> dict[str, tuple[int, bytes]]:
    try:
        entries: dict[str, tuple[int, bytes]] = {}
        with zipfile.ZipFile(io.BytesIO(content)) as archive:
            for item in archive.infolist():
                if item.is_dir():
                    continue
                name = item.filename
                marker = "/payload/"
                if marker not in name:
                    continue
                prefix, relative = name.split(marker, 1)
                pure = PurePosixPath(relative)
                require(prefix and relative and name.count(marker) == 1 and "\\" not in name
                        and not pure.is_absolute() and str(pure) == relative
                        and all(part not in {"", ".", ".."} for part in pure.parts),
                        "rebound payload path is invalid")
                key = pure.as_posix()
                require(key not in entries, "rebound payload has duplicate paths")
                entries[key] = (item.external_attr, archive.read(item))
        require(entries, "rebound payload is empty")
        return entries
    except (OSError, ValueError, zipfile.BadZipFile) as exc:
        raise RuntimeError("rebound payload cannot be read") from exc


def validate_rebound_payload_delta(baseline_archive: bytes, replacement_archive: bytes) -> None:
    before = payload_entries(baseline_archive)
    after = payload_entries(replacement_archive)
    changed = {name for name in before.keys() | after.keys() if before.get(name) != after.get(name)}
    expected_paths = {path for path, _anchor, _addition in PAYLOAD_DELTAS}
    require(changed == expected_paths, "Candidate11 payload delta differs")
    for path, anchor, addition in PAYLOAD_DELTAS:
        require(path in before and path in after and before[path][0] == after[path][0],
                "Candidate11 payload mode differs")
        expected = before[path][1]
        require(expected.count(anchor) == 1, "Candidate10 payload anchor differs")
        expected = expected.replace(anchor, anchor + addition)
        require(after[path][1] == expected, "Candidate11 payload bytes differ")


def route_identity(package: dict) -> dict:
    identity = package.get("identity")
    require(isinstance(identity, dict), "candidate package identity is absent")
    value = {
        "package_id": package.get("package_id"),
        "release_id": package.get("release_id"),
        "payload_fingerprint": identity.get("payload_fingerprint"),
    }
    require(all(isinstance(item, str) and item for item in value.values()), "candidate route identity is incomplete")
    return value


def portable_validation(package_root: Path, expected_identity: dict) -> tuple[dict, bytes]:
    metadata = package_root / "metadata"
    validation_path = metadata / "validation.json"
    package_path = metadata / "package.yaml"
    require(validation_path.is_file() and package_path.is_file(), "candidate package metadata is incomplete")
    validation_bytes = validation_path.read_bytes()
    validation = read_json(validation_path)
    authority = validation.get("authority")
    require(isinstance(authority, dict) and authority.get("kind") == "incoming-candidate",
            "candidate does not declare incoming-candidate validation authority")
    declared = authority.get("validator")
    require(isinstance(declared, dict) and set(declared) == {"path", "sha256", "argv"},
            "candidate validator authority has an invalid shape")
    validator_path = declared["path"]
    require(isinstance(validator_path, str), "candidate validator path is invalid")
    safe_relative(validator_path)
    expected_argv = ["python", f"payload/{validator_path}", "--package-root", "."]
    require(declared["argv"] == expected_argv, "candidate validator argv does not bind the declared validator")
    validator = under(package_root / "payload", validator_path)
    require(digest(validator.read_bytes()) == declared["sha256"], "candidate validator digest mismatch")
    package = yaml.safe_load(package_path.read_bytes())
    require(isinstance(package, dict) and route_identity(package) == expected_identity,
            "candidate package identity disagrees with staged candidate")
    require(expected_identity["payload_fingerprint"] != C10_PAYLOAD_FINGERPRINT,
            "Candidate11 package identity still names Candidate10 payload")
    completed = subprocess.run([sys.executable, str(validator), "--package-root", "."],
                               cwd=package_root, capture_output=True, check=False)
    output = completed.stdout + completed.stderr
    require(completed.returncode == 0, f"archive-declared portable validator failed: exit={completed.returncode}")
    return {
        "schema_version": "incoming-package-validation/v1",
        "authority": {
            "kind": "incoming-candidate",
            "manifest": {"path": "metadata/validation.json", "sha256": digest(validation_bytes)},
            "validator": {"path": validator_path, "sha256": declared["sha256"], "argv": expected_argv},
        },
        "package_identity": expected_identity,
        "execution": {"outcome": "passed", "exit_code": 0, "output_sha256": digest(output)},
    }, output


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--asset-root", type=Path, required=True)
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    root = args.asset_root.resolve()
    contract_path = args.contract.resolve()
    require(root.is_dir() and contract_path.is_file(), "staged root and contract are required")
    require(contract_path.is_relative_to(root), "contract must remain inside staged root")
    require(args.receipt.resolve().is_relative_to(root) and args.output.resolve().is_relative_to(root),
            "edge receipt and output must remain inside staged root")
    contract = read_json(contract_path)
    expected_keys = {
        "schema_version", "edge_id", "from_version", "to_version", "artifacts", "package_identity",
        "semantic_cutovers", "terminal", "runner",
    }
    require(set(contract) == expected_keys and contract["schema_version"] == "v018-direct-edge-contract/v1",
            "edge contract schema mismatch")
    require(contract["from_version"] in ORIGINS and contract["to_version"] == "v0.18.0",
            "edge version mismatch")
    require(contract["terminal"] == c10_assets()["terminal"]
            and contract["runner"] == c10_assets()["runner"],
            "retained Candidate10 terminal or runner binding differs")
    artifacts = contract["artifacts"]
    require(isinstance(artifacts, dict) and set(artifacts) == {"archive", "checksum", "manifest", "validator"},
            "Candidate11 contract artifacts mismatch")
    validated = {name: asset(root, value)[0] for name, value in artifacts.items()}
    self_path = Path(__file__).resolve()
    require(self_path.is_relative_to(root)
            and artifacts["validator"]["path"] == self_path.relative_to(root).as_posix()
            and digest(self_path.read_bytes()) == artifacts["validator"]["sha256"],
            "Candidate11 contract does not bind this validator")
    archive_path = under(root, artifacts["archive"]["path"])
    require(artifacts["archive"]["sha256"] != C10_ARCHIVE_SHA256,
            "Candidate11 archive cannot be Candidate10 archive")
    checksum_path = under(root, artifacts["checksum"]["path"])
    require(checksum_path.read_bytes() == f"{artifacts['archive']['sha256']}  {archive_path.name}\n".encode(),
            "checksum is not the exact Candidate11 archive SHA-256 sidecar")
    c10_paths = {name: asset(root, identity)[1] for name, identity in c10_assets().items()}
    require(read_json(c10_paths["execution_set"]) == c10_execution_set(), "Candidate10 execution set differs")
    terminal = read_json(c10_paths["terminal"])
    expected_cases(terminal)
    validate_case_evidence_index(root, c10_paths["case_evidence_index"])
    require(terminal["runner"]["sha256"] == digest(c10_paths["runner"].read_bytes()),
            "Candidate10 retained runner bytes differ")
    validate_rebound_payload_delta(c10_paths["baseline_archive"].read_bytes(), archive_path.read_bytes())
    claims = contract["semantic_cutovers"]
    require(isinstance(claims, list) and all(isinstance(item, dict) and set(item) == {"cutover_id", "required", "state"}
                                             and item["state"] == "passed" for item in claims),
            "edge cutover claims must be explicitly passed")
    require(not args.output.exists() and not args.receipt.exists(), "edge receipt and output must be fresh")
    args.output.mkdir(parents=True)
    with tempfile.TemporaryDirectory(prefix="ai-c11-") as temporary:
        package_root = extract_zip(archive_path, Path(temporary) / "extract")
        manifest = under(package_root, "metadata/migration.yaml")
        require(manifest.read_bytes() == under(root, artifacts["manifest"]["path"]).read_bytes(),
                "Candidate11 external manifest disagrees with package metadata")
        portable, output = portable_validation(package_root, contract["package_identity"])
    output_path = args.output / "validation-output.log"
    output_path.write_bytes(output)
    receipt = {
        "schema_version": "upgrade-edge-validation/v2",
        "edge_id": contract["edge_id"],
        "from_version": contract["from_version"],
        "to_version": contract["to_version"],
        "artifacts": validated,
        "validator_argv": ["python", artifacts["validator"]["path"], "--edge-id", contract["edge_id"]],
        "semantic_cutovers": claims,
        "portable_validation": portable,
        "outcome": "passed",
        "exit_code": 0,
        "output_sha256": digest(output),
    }
    write_json(args.receipt, receipt)
    print(json.dumps({"edge_id": contract["edge_id"], "outcome": "passed", "output_sha256": digest(output)}))


if __name__ == "__main__":
    main()
