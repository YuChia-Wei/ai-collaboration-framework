#!/usr/bin/env python3
"""Validate one staged v0.18 direct route without admitting it anywhere."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import shutil
import subprocess
import sys
import tempfile
import zipfile

import yaml

sys.dont_write_bytecode = True

ORIGINS = ("v0.6.0", "v0.9.0", "v0.17.0")


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


def expected_cases(terminal: dict) -> None:
    require(terminal.get("schema_version") == "direct-upgrade-execution/v1", "terminal schema mismatch")
    require(terminal.get("evidence_kind") == "actual-isolated-target-execution", "terminal is not actual execution")
    require(terminal.get("outcome") == "passed", "terminal outcome is not passed")
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
            "edge receipts and output must remain inside staged root")
    require(not (root / "execution-set.json").exists(), "v0.17 execution-set exception is forbidden")
    contract = read_json(contract_path)
    expected_keys = {"schema_version", "edge_id", "from_version", "to_version", "artifacts", "package_identity", "semantic_cutovers", "terminal", "runner"}
    require(set(contract) == expected_keys and contract["schema_version"] == "v018-direct-edge-contract/v1",
            "edge contract schema mismatch")
    require(contract["from_version"] in ORIGINS and contract["to_version"] == "v0.18.0", "edge version mismatch")
    artifacts = contract["artifacts"]
    require(isinstance(artifacts, dict) and set(artifacts) == {"archive", "checksum", "manifest", "validator"},
            "edge contract artifacts mismatch")
    validated = {name: asset(root, value)[0] for name, value in artifacts.items()}
    archive_path = under(root, artifacts["archive"]["path"])
    checksum_path = under(root, artifacts["checksum"]["path"])
    require(checksum_path.read_bytes() == f"{artifacts['archive']['sha256']}  {archive_path.name}\n".encode(),
            "checksum is not the exact archive SHA-256 sidecar")
    _, terminal_path = asset(root, contract["terminal"])
    _, runner_path = asset(root, contract["runner"])
    terminal = read_json(terminal_path)
    expected_cases(terminal)
    runner = terminal.get("runner")
    require(isinstance(runner, dict) and runner.get("path") == ".github/scripts/validate-v018-direct-upgrades.py"
            and runner.get("sha256") == digest(runner_path.read_bytes()), "terminal runner binding mismatch")
    require(terminal.get("archive_sha256") == artifacts["archive"]["sha256"], "terminal archive binding mismatch")
    claims = contract["semantic_cutovers"]
    require(isinstance(claims, list) and all(isinstance(item, dict) and set(item) == {"cutover_id", "required", "state"}
                                             and item["state"] == "passed" for item in claims),
            "edge cutover claims must be explicitly passed")
    require(not args.output.exists(), "edge output must be fresh")
    args.output.mkdir(parents=True)
    with tempfile.TemporaryDirectory(dir=args.output, prefix="candidate-") as temporary:
        package_root = extract_zip(archive_path, Path(temporary) / "extract")
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
