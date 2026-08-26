#!/usr/bin/env python3
"""Deterministic v0.15 package identity and upgrade validation lanes."""

from __future__ import annotations

import hashlib
import json
import os
import platform
import re
import shutil
import stat
import subprocess
import sys
import tarfile
import time
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Sequence

import yaml

import ai_context_package as PACKAGE
import ai_context_target_provenance as TARGET


SCHEMA_VERSION = "v015-package-validation-terminal/v1"
AGGREGATE_SCHEMA_VERSION = "v015-package-validation-aggregate/v1"
OUTCOMES = {
    "passed",
    "failed",
    "blocked-by-environment",
    "not-applicable",
    "deferred-with-owner",
}
LANE_BUDGETS = {"fast": 90, "medium": 240, "long": 1200}
EXPECTED_BASE = "ai-collaboration-framework-v0.15.0"
LEGACY_BASE = "ai-context-dotnet-backend-v0.14.0"
SOURCE_VERSION = "0.14.0"
CANDIDATE_VERSION = "0.15.0"
METRICS_PREFIX = "AI context package Git inspection: "


class ValidationError(RuntimeError):
    """A deterministic contract failure with a path-free reason code."""

    def __init__(self, reason_code: str) -> None:
        super().__init__(reason_code)
        self.reason_code = reason_code


@dataclass(frozen=True)
class Candidate:
    result: dict[str, Path | str]
    root: Path
    package: dict[str, object]
    migration: dict[str, object]
    synthetic_release_digest: str


def canonical_json_bytes(value: object) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def atomic_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_bytes(canonical_json_bytes(value) + b"\n")
    os.replace(temporary, path)


def require(condition: bool, reason_code: str) -> None:
    if not condition:
        raise ValidationError(reason_code)


def run(
    argv: Sequence[str],
    *,
    cwd: Path,
    reason_code: str,
) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        list(argv),
        cwd=cwd,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if result.returncode != 0:
        raise ValidationError(reason_code)
    return result


def git(root: Path, *arguments: str, reason_code: str = "git-command-failed") -> subprocess.CompletedProcess[str]:
    return run(("git", *arguments), cwd=root, reason_code=reason_code)


def host_platform() -> str:
    system = platform.system().casefold()
    if system == "windows":
        return "windows"
    if system == "linux":
        return "linux"
    return system or "unknown"


def phase(phases: dict[str, dict[str, object]], name: str, operation: Callable[[], object]) -> object:
    started = time.perf_counter_ns()
    try:
        value = operation()
    except Exception:
        phases[name] = {
            "outcome": "failed",
            "duration_ms": round((time.perf_counter_ns() - started) / 1_000_000, 3),
        }
        raise
    phases[name] = {
        "outcome": "passed",
        "duration_ms": round((time.perf_counter_ns() - started) / 1_000_000, 3),
    }
    return value


def repository_snapshot(root: Path) -> dict[str, str]:
    head = git(root, "rev-parse", "HEAD", reason_code="subject-head-unavailable").stdout.strip()
    status = git(
        root,
        "status",
        "--porcelain=v1",
        "--untracked-files=all",
        reason_code="subject-status-unavailable",
    ).stdout
    tree = git(root, "rev-parse", "HEAD^{tree}", reason_code="subject-tree-unavailable").stdout.strip()
    return {"commit": head, "tree": tree, "status_sha256": sha256_bytes(status.encode("utf-8")), "status": status}


def validate_subject(root: Path, expected_commit: str) -> dict[str, str]:
    snapshot = repository_snapshot(root)
    require(snapshot["commit"] == expected_commit, "subject-commit-drift")
    require(snapshot["status"] == "", "subject-not-clean")
    return {key: value for key, value in snapshot.items() if key != "status"}


def validate_output_root(root: Path, output: Path) -> Path:
    resolved = output.resolve()
    allowed = (root / ".dev/ai-context/local/validation").resolve()
    require(resolved != allowed and resolved.is_relative_to(allowed), "output-outside-ignored-validation-root")
    ignored = subprocess.run(
        ["git", "check-ignore", "--no-index", "--quiet", str(resolved)],
        cwd=root,
        check=False,
        capture_output=True,
    )
    require(ignored.returncode == 0, "output-root-not-ignored")
    if resolved.exists():
        require(not any(resolved.iterdir()), "output-root-not-empty")
    resolved.mkdir(parents=True, exist_ok=True)
    return resolved


def validate_retry(
    *,
    lane: str,
    subject_commit: str,
    attempt: int,
    prior_terminal: Path | None,
    material_state_change: str | None,
    authorization_ref: str | None,
) -> dict[str, object]:
    require(attempt >= 1, "invalid-attempt")
    if attempt == 1:
        require(prior_terminal is None, "first-attempt-must-not-have-prior-terminal")
        require(material_state_change is None, "first-attempt-must-not-claim-state-change")
        return {"retry": False}
    require(prior_terminal is not None and prior_terminal.is_file(), "retry-prior-terminal-required")
    prior = json.loads(prior_terminal.read_text(encoding="utf-8"))
    require(prior.get("schema_version") == SCHEMA_VERSION, "retry-prior-schema-invalid")
    require(prior.get("lane") == lane, "retry-prior-lane-mismatch")
    require(prior.get("subject", {}).get("commit") == subject_commit, "retry-subject-mismatch")
    require(prior.get("outcome") != "passed", "passed-terminal-cannot-be-retried")
    fingerprint = prior.get("failure_fingerprint")
    require(isinstance(fingerprint, str) and len(fingerprint) == 64, "retry-failure-fingerprint-required")
    require(bool(material_state_change), "retry-material-state-change-required")
    if attempt >= 3:
        require(bool(authorization_ref), "attempt-three-authorization-required")
        prior_authorization = prior.get("execution", {}).get("authorization_ref")
        require(authorization_ref != prior_authorization, "attempt-three-authorization-must-be-new")
    return {
        "retry": True,
        "prior_failure_fingerprint": fingerprint,
        "material_state_change_sha256": sha256_bytes(material_state_change.encode("utf-8")),
    }


def legacy_paths(root: Path) -> tuple[Path, Path]:
    published = root / ".dev/releases/v0.14.0/route-assets/published-v0.14.0"
    return published / f"{LEGACY_BASE}.zip", published / "metadata/files.yaml"


def legacy_snapshot(root: Path) -> dict[str, str]:
    archive, files = legacy_paths(root)
    require(archive.is_file() and files.is_file(), "published-v014-evidence-missing")
    return {
        "archive_sha256": sha256_file(archive),
        "files_manifest_sha256": sha256_file(files),
    }


def safe_extract_tar(archive: Path, destination: Path) -> None:
    destination.mkdir(parents=True, exist_ok=True)
    with tarfile.open(archive) as opened:
        for member in opened.getmembers():
            target = (destination / member.name).resolve()
            require(target.is_relative_to(destination.resolve()), "source-archive-path-escape")
        opened.extractall(destination)


def create_synthetic_source(root: Path, expected_commit: str, work: Path) -> tuple[Path, str]:
    archive = work / "source.tar"
    source = work / "synthetic-source"
    run(
        ("git", "archive", "--format=tar", "--output", str(archive), expected_commit),
        cwd=root,
        reason_code="synthetic-source-archive-failed",
    )
    safe_extract_tar(archive, source)
    git(source, "init", "-q", reason_code="synthetic-source-git-init-failed")
    git(source, "config", "user.name", "Validation Fixture")
    git(source, "config", "user.email", "validation-fixture@example.invalid")
    git(source, "config", "core.longpaths", "true")
    git(source, "add", ".", reason_code="synthetic-source-git-add-failed")
    git(source, "commit", "-qm", "exact subject snapshot", reason_code="synthetic-source-baseline-commit-failed")
    release_path = source / ".dev/releases/v0.15.0/release.yaml"
    release_path.parent.mkdir(parents=True, exist_ok=True)
    release_document = {
        "version": "v0.15.0",
        "compatibility": {
            "breaking_changes": True,
            "minimum_source_version": "v0.14.0",
            "reconciliation_sources": ["v0.14.0"],
            "automatic_upgrade_sources": ["v0.14.0"],
        },
        "distribution": {
            "profile_id": "dotnet-backend",
            "package_id": EXPECTED_BASE,
        },
    }
    release_bytes = yaml.safe_dump(release_document, sort_keys=False).encode("utf-8")
    release_path.write_bytes(release_bytes)
    git(source, "add", "--", ".dev/releases/v0.15.0/release.yaml")
    git(source, "commit", "-qm", "synthetic v0.15 validation candidate")
    return source, sha256_bytes(release_bytes)


def extract_zip(archive: Path, destination: Path) -> None:
    destination.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(archive) as opened:
        for member in opened.infolist():
            target = (destination / member.filename).resolve()
            require(target.is_relative_to(destination.resolve()), "package-archive-path-escape")
        opened.extractall(destination)


def build_candidate(root: Path, expected_commit: str, output: Path) -> Candidate:
    work = output / "work"
    work.mkdir(parents=True, exist_ok=True)
    source, release_digest = create_synthetic_source(root, expected_commit, work)
    candidate_output = output / "artifacts/candidate"
    _, previous_files = legacy_paths(root)
    result = PACKAGE.build_package(
        source,
        "HEAD",
        CANDIDATE_VERSION,
        candidate_output,
        ".ai/distribution/profiles/dotnet-backend.yaml",
        previous_files,
        SOURCE_VERSION,
    )
    extracted = work / "candidate-extracted"
    extract_zip(Path(result["zip"]), extracted)
    candidate_root = extracted / EXPECTED_BASE
    package = yaml.safe_load((candidate_root / "metadata/package.yaml").read_text(encoding="utf-8"))
    migration = yaml.safe_load((candidate_root / "metadata/migration.yaml").read_text(encoding="utf-8"))
    return Candidate(result, candidate_root, package, migration, release_digest)


def candidate_evidence(candidate: Candidate, output: Path) -> dict[str, object]:
    candidate_dir = output / "artifacts/candidate"
    names = sorted(path.name for path in candidate_dir.iterdir())
    expected_names = sorted(
        [
            f"{EXPECTED_BASE}.zip",
            f"{EXPECTED_BASE}.zip.sha256",
            f"{EXPECTED_BASE}.tar.gz",
            f"{EXPECTED_BASE}.tar.gz.sha256",
        ]
    )
    require(names == expected_names, "candidate-public-forms-mismatch")
    for archive_key in ("zip", "tar_gz"):
        PACKAGE.validate_sidecar(Path(candidate.result[archive_key]))
    zip_members = PACKAGE.validate_archive(Path(candidate.result["zip"]))
    tar_members = PACKAGE.validate_archive(Path(candidate.result["tar_gz"]))
    require(zip_members == tar_members, "candidate-archive-parity-failed")
    package = candidate.package
    identity = package["identity"]
    require(candidate.result["package_id"] == EXPECTED_BASE, "candidate-result-identity-mismatch")
    require(package["schema_version"] == "2.4.0", "candidate-package-schema-mismatch")
    require(package["package_id"] == EXPECTED_BASE, "candidate-envelope-identity-mismatch")
    require(identity["public_artifact_base"] == EXPECTED_BASE, "candidate-public-base-mismatch")
    require(candidate.migration["package_id"] == EXPECTED_BASE, "candidate-migration-identity-mismatch")
    require(candidate.migration["sources"][0]["version"] == SOURCE_VERSION, "candidate-upgrade-source-mismatch")
    require(candidate.result["payload_fingerprint"] == identity["payload_fingerprint"], "candidate-payload-fingerprint-mismatch")
    member_map = [
        {"path": path, "sha256": sha256_bytes(content), "mode": mode}
        for path, (content, mode) in sorted(
            zip_members.items(), key=lambda item: item[0].encode("utf-8")
        )
    ]
    return {
        "public_forms": names,
        "zip_sha256": sha256_file(Path(candidate.result["zip"])),
        "tar_gz_sha256": sha256_file(Path(candidate.result["tar_gz"])),
        "archive_member_map_sha256": sha256_bytes(canonical_json_bytes(member_map)),
        "archive_member_count": len(zip_members),
        "package_manifest_sha256": identity["files_manifest_digest"],
        "migration_sha256": identity["migration_digest"],
        "payload_fingerprint": identity["payload_fingerprint"],
        "synthetic_release_sha256": candidate.synthetic_release_digest,
    }


def initialize_git_target(target: Path, message: str) -> None:
    git(target, "init", "-q", reason_code="target-git-init-failed")
    git(target, "config", "core.longpaths", "true")
    git(target, "config", "user.name", "Validation Fixture")
    git(target, "config", "user.email", "validation-fixture@example.invalid")
    git(target, "add", ".", reason_code="target-git-add-failed")
    git(target, "commit", "-qm", message, reason_code="target-baseline-commit-failed")


def parse_git_metrics(stderr: str) -> list[dict[str, object]]:
    events = []
    for line in stderr.splitlines():
        if line.startswith(METRICS_PREFIX):
            events.append(json.loads(line[len(METRICS_PREFIX) :]))
    return events


def tree_digest(root: Path) -> str:
    records: list[dict[str, object]] = []
    for path in sorted(root.rglob("*"), key=lambda item: item.as_posix().encode("utf-8")):
        relative = path.relative_to(root).as_posix()
        if relative == ".git" or relative.startswith(".git/"):
            continue
        if path.is_file():
            records.append({"path": relative, "sha256": sha256_file(path), "mode": path.stat().st_mode & 0o777})
    return sha256_bytes(canonical_json_bytes(records))


def remove_tree(root: Path) -> None:
    def clear_readonly_and_retry(function: Callable[[str], object], path: str, _: object) -> None:
        os.chmod(path, stat.S_IWRITE)
        function(path)

    shutil.rmtree(root, onerror=clear_readonly_and_retry)


def seed_upgrade_target_provenance(target: Path, previous_root: Path) -> None:
    package = yaml.safe_load((previous_root / "metadata/package.yaml").read_text(encoding="utf-8"))
    source = package["source"]
    provenance = target / ".dev/ai-context/provenance.yaml"
    provenance.parent.mkdir(parents=True, exist_ok=True)
    selection = {
        "release_model": "single-versioned-componentized-release",
        "mandatory_components": ["software-development-core", "ai-context-lifecycle-core"],
        "profiles": ["dotnet-backend"],
        "providers": {"repo-backlog": {"enabled": False, "preservation": "preserve-existing-if-recorded"}},
    }
    provenance.write_text(
        yaml.safe_dump(
            {
                "source": {
                    "repository": source["repository"],
                    "release_id": package["release_id"],
                    "version": f"v{package['version']}",
                    "tag": f"v{package['version']}",
                    "commit": source["commit"],
                },
                "selection": selection,
            },
            sort_keys=False,
        ),
        encoding="utf-8",
        newline="\n",
    )


def write_upgrade_decision(packet_path: Path, evidence: Path) -> Path:
    packet = json.loads(packet_path.read_text(encoding="utf-8"))
    proposal = packet["automatic_proposal"]
    package = packet["package"]
    candidate_provenance, candidate_customizations = TARGET.build_initialization_documents(
        {
            "repository": package["source"]["repository"],
            "release_id": f"REL-v{package['version']}",
            "version": f"v{package['version']}",
            "tag": f"v{package['version']}",
            "commit": package["source"]["commit"],
        },
        packet["selection"],
        "2026-08-26T00:00:00+08:00",
    )
    candidate_provenance["previous_source"] = packet["provenance"]["source"]
    candidate_provenance["installation"]["last_upgraded_at"] = "2026-08-26T00:00:00+08:00"
    candidate_provenance["last_migration"] = {
        "status": "completed",
        "from_version": "v0.14.0",
        "to_version": "v0.15.0",
        "completed_at": "2026-08-26T00:00:00+08:00",
        "evidence": "ignored-validation-terminal",
    }
    provenance_bytes = canonical_json_bytes(candidate_provenance)
    customizations_bytes = canonical_json_bytes(candidate_customizations)
    evidence.mkdir(parents=True, exist_ok=True)
    (evidence / "candidate-provenance.json").write_bytes(provenance_bytes)
    (evidence / "candidate-customizations.json").write_bytes(customizations_bytes)
    decision = {
        "schema_version": "upgrade-remediation-decision/v1",
        "packet_sha256": packet["canonical_digest"],
        "plan_sha256": packet["plan_sha256"],
        "transaction_id": packet["transaction_id"],
        "status": "approved",
        "owner": "validation-fixture-owner",
        "decided_at": "2026-08-26T00:00:00+08:00",
        "evidence": "ignored-validation-terminal",
        "reason": "exercise the authorized synthetic v0.15 durability upgrade route",
        "accepted_operation_ids": proposal["apply_operation_ids"],
        "reconciliation_ids": proposal["reconciliation_ids"],
        "policy_adoptions": candidate_provenance.get("policy_adoptions"),
        "candidate_authority": {
            "provenance_sha256": sha256_bytes(provenance_bytes),
            "customizations_sha256": sha256_bytes(customizations_bytes),
        },
    }
    path = evidence / "remediation-decision.json"
    atomic_json(path, decision)
    return path


def fast_lane(root: Path, expected_commit: str, output: Path, phases: dict[str, dict[str, object]]) -> dict[str, object]:
    legacy_before = legacy_snapshot(root)
    candidate = phase(phases, "build", lambda: build_candidate(root, expected_commit, output))
    assert isinstance(candidate, Candidate)
    evidence = phase(phases, "archive-parity", lambda: candidate_evidence(candidate, output))
    assert isinstance(evidence, dict)
    legacy_after = legacy_snapshot(root)
    require(legacy_before == legacy_after, "legacy-evidence-mutated")
    evidence.update(
        {
            "legacy": legacy_after,
            "legacy_immutable": True,
            "material_target_mutation": False,
            "actual_upgrade": False,
            "synthetic_candidate": True,
        }
    )
    return evidence


def medium_lane(root: Path, expected_commit: str, output: Path, phases: dict[str, dict[str, object]]) -> dict[str, object]:
    legacy_before = legacy_snapshot(root)
    candidate = phase(phases, "build", lambda: build_candidate(root, expected_commit, output))
    assert isinstance(candidate, Candidate)
    evidence = candidate_evidence(candidate, output)
    target = output / "work/clean-install-target"

    def prepare_target() -> None:
        target.mkdir(parents=True)
        (target / "target-owned.txt").write_text("target truth\n", encoding="utf-8", newline="\n")
        initialize_git_target(target, "synthetic clean-install baseline")

    phase(phases, "prepare-target", prepare_target)
    planner = candidate.root / "payload/.ai/scripts/plan-ai-context-package-apply.py"

    def apply_clean_install() -> subprocess.CompletedProcess[str]:
        return run(
            (
                sys.executable,
                str(planner),
                "--package-root",
                str(candidate.root),
                "--target-root",
                str(target),
                "--git-inspection-metrics",
                "--apply",
            ),
            cwd=root,
            reason_code="medium-clean-install-failed",
        )

    applied = phase(phases, "apply", apply_clean_install)
    assert isinstance(applied, subprocess.CompletedProcess)

    def read_receipt() -> dict[str, object]:
        receipt = yaml.safe_load((target / ".dev/AI-CONTEXT-APPLY-PENDING.yaml").read_text(encoding="utf-8"))
        require(receipt["package_id"] == EXPECTED_BASE, "medium-receipt-package-id-mismatch")
        require(receipt["package_version"] == CANDIDATE_VERSION, "medium-receipt-version-mismatch")
        require((target / "target-owned.txt").read_text(encoding="utf-8") == "target truth\n", "medium-target-truth-mutated")
        return receipt

    receipt = phase(phases, "receipt", read_receipt)
    assert isinstance(receipt, dict)
    legacy_after = legacy_snapshot(root)
    require(legacy_before == legacy_after, "legacy-evidence-mutated")
    evidence.update(
        {
            "legacy": legacy_after,
            "legacy_immutable": True,
            "synthetic_candidate": True,
            "synthetic_clean_install": True,
            "actual_upgrade": False,
            "receipt_package_id": receipt["package_id"],
            "receipt_package_version": receipt["package_version"],
            "receipt_sha256": sha256_file(target / ".dev/AI-CONTEXT-APPLY-PENDING.yaml"),
            "git_inspection_metrics": parse_git_metrics(applied.stderr),
        }
    )
    return evidence


def long_lane(root: Path, expected_commit: str, output: Path, phases: dict[str, dict[str, object]]) -> dict[str, object]:
    legacy_before = legacy_snapshot(root)
    archive, previous_files = legacy_paths(root)
    candidate = phase(phases, "build", lambda: build_candidate(root, expected_commit, output))
    assert isinstance(candidate, Candidate)
    evidence = candidate_evidence(candidate, output)
    previous_extract = output / "work/v014-extracted"

    def extract_origin() -> Path:
        extract_zip(archive, previous_extract)
        previous_root = previous_extract / LEGACY_BASE
        require(previous_root.is_dir(), "published-v014-envelope-missing")
        return previous_root

    previous_root = phase(phases, "extract", extract_origin)
    assert isinstance(previous_root, Path)
    target = output / "work/v014-upgrade-target"

    def prepare_target() -> dict[str, str]:
        shutil.copytree(previous_root / "payload", target)
        seed_upgrade_target_provenance(target, previous_root)
        initialize_git_target(target, "published v0.14 target baseline")
        snapshot = repository_snapshot(target)
        return {
            "commit": snapshot["commit"],
            "tree": snapshot["tree"],
            "status_sha256": snapshot["status_sha256"],
            "payload_tree_sha256": tree_digest(target),
        }

    target_before = phase(phases, "snapshot", prepare_target)
    assert isinstance(target_before, dict)
    planner = candidate.root / "payload/.ai/scripts/plan-ai-context-package-apply.py"
    evidence_root = output / "artifacts/upgrade-evidence"
    packet_path = evidence_root / "remediation-packet.json"
    plan_path = evidence_root / "plan.yaml"
    base = (
        sys.executable,
        str(planner),
        "--package-root",
        str(candidate.root),
        "--target-root",
        str(target),
        "--previous-files",
        str(previous_files),
        "--previous-version",
        SOURCE_VERSION,
        "--git-inspection-metrics",
    )

    def prepare_plan() -> subprocess.CompletedProcess[str]:
        evidence_root.mkdir(parents=True, exist_ok=True)
        return run(
            (*base, "--plan-output", str(plan_path), "--remediation-packet-output", str(packet_path)),
            cwd=root,
            reason_code="long-upgrade-plan-failed",
        )

    prepared = phase(phases, "plan", prepare_plan)
    assert isinstance(prepared, subprocess.CompletedProcess)
    decision = phase(phases, "decision", lambda: write_upgrade_decision(packet_path, evidence_root))
    assert isinstance(decision, Path)

    def apply_upgrade() -> subprocess.CompletedProcess[str]:
        return run(
            (*base, "--apply", "--remediation-decision", str(decision)),
            cwd=root,
            reason_code="long-upgrade-apply-failed",
        )

    applied = phase(phases, "apply", apply_upgrade)
    assert isinstance(applied, subprocess.CompletedProcess)

    def read_receipt() -> dict[str, object]:
        receipt_path = target / ".dev/AI-CONTEXT-APPLY-PENDING.yaml"
        receipt = yaml.safe_load(receipt_path.read_text(encoding="utf-8"))
        require(receipt["package_id"] == EXPECTED_BASE, "long-receipt-package-id-mismatch")
        require(receipt["package_version"] == CANDIDATE_VERSION, "long-receipt-version-mismatch")
        require(receipt["package_manifest_sha256"] == candidate.package["identity"]["files_manifest_digest"], "long-receipt-manifest-mismatch")
        require(receipt["migration_sha256"] == candidate.package["identity"]["migration_digest"], "long-receipt-migration-mismatch")
        require(
            receipt["selected_input_proof"]
            == {
                "path": "metadata/selected-inputs.json",
                "sha256": candidate.package["validation"]["selected_inputs_sha256"],
            },
            "long-receipt-selected-input-proof-mismatch",
        )
        return receipt

    receipt = phase(phases, "receipt", read_receipt)
    assert isinstance(receipt, dict)
    plan_metrics = parse_git_metrics(prepared.stderr)
    apply_metrics = parse_git_metrics(applied.stderr)
    require(len(plan_metrics) == 1 and plan_metrics[0].get("phase") == "plan", "long-plan-metrics-missing")
    require(
        [item.get("phase") for item in apply_metrics] == ["plan", "apply"],
        "long-apply-metrics-missing",
    )
    target_after = {
        "payload_tree_sha256": tree_digest(target),
        "receipt_sha256": sha256_file(target / ".dev/AI-CONTEXT-APPLY-PENDING.yaml"),
    }
    legacy_after = legacy_snapshot(root)
    require(legacy_before == legacy_after, "legacy-evidence-mutated")
    evidence.update(
        {
            "source": {
                "subject_commit": expected_commit,
                "subject_tree": git(root, "rev-parse", f"{expected_commit}^{{tree}}").stdout.strip(),
                "legacy": legacy_after,
            },
            "candidate": {
                "zip_sha256": evidence["zip_sha256"],
                "tar_gz_sha256": evidence["tar_gz_sha256"],
                "package_manifest_sha256": evidence["package_manifest_sha256"],
                "migration_sha256": evidence["migration_sha256"],
                "payload_fingerprint": evidence["payload_fingerprint"],
            },
            "target_snapshot_before": target_before,
            "target_snapshot_after": target_after,
            "git_inspection": {
                "plan": plan_metrics[0],
                "apply_invocation": apply_metrics,
                "process_count": {
                    "plan": plan_metrics[0]["git_process_count"],
                    "apply_plan": apply_metrics[0]["git_process_count"],
                    "apply": apply_metrics[1]["git_process_count"],
                },
            },
            "receipt": {
                "package_id": receipt["package_id"],
                "package_version": receipt["package_version"],
                "package_manifest_sha256": receipt["package_manifest_sha256"],
                "migration_sha256": receipt["migration_sha256"],
                "selected_input_proof": receipt["selected_input_proof"],
            },
            "legacy_immutable": True,
            "synthetic_candidate": True,
            "actual_published_v014_origin": True,
            "actual_upgrade": True,
            "consumed_ai_context_test_tmp_root": False,
        }
    )
    return evidence


def failure_details(lane: str, subject_commit: str, error: Exception) -> tuple[str, str, str]:
    if isinstance(error, ValidationError):
        outcome = "failed"
        reason = error.reason_code
        failure_class = "contract"
    elif isinstance(error, PACKAGE.PackageError):
        outcome = "failed"
        reason = "package-build-contract-failed"
        failure_class = "contract"
    elif isinstance(error, (PermissionError, OSError)):
        outcome = "blocked-by-environment"
        code = getattr(error, "winerror", None) or getattr(error, "errno", None) or "unknown"
        reason = f"os-error-{code}"
        failure_class = "environment"
    else:
        outcome = "failed"
        reason = "unexpected-validation-error"
        failure_class = "implementation"
    fingerprint = sha256_bytes(
        canonical_json_bytes(
            {
                "failure_class": failure_class,
                "lane": lane,
                "reason_code": reason,
                "subject_commit": subject_commit,
                "platform": host_platform(),
            }
        )
    )
    return outcome, reason, fingerprint


def validate_terminal_record(terminal: dict[str, object]) -> None:
    required = {
        "schema_version",
        "lane",
        "outcome",
        "subject",
        "command",
        "execution",
        "evidence",
        "phases",
        "cleanup",
        "failure_fingerprint",
    }
    require(set(terminal) == required, "terminal-fields-invalid")
    require(terminal["schema_version"] == SCHEMA_VERSION, "terminal-schema-invalid")
    lane = terminal["lane"]
    outcome = terminal["outcome"]
    require(lane in LANE_BUDGETS, "terminal-lane-invalid")
    require(outcome in OUTCOMES, "terminal-outcome-invalid")
    fingerprint = terminal["failure_fingerprint"]
    if outcome == "passed":
        require(fingerprint is None, "passed-terminal-has-failure-fingerprint")
    else:
        require(isinstance(fingerprint, str) and len(fingerprint) == 64, "nonpassing-terminal-missing-fingerprint")
    cleanup = terminal["cleanup"]
    require(isinstance(cleanup, dict) and cleanup.get("outcome") in {"passed", "failed"}, "terminal-cleanup-invalid")
    if outcome != "passed":
        return
    evidence = terminal["evidence"]
    phases = terminal["phases"]
    require(isinstance(evidence, dict) and isinstance(phases, dict), "terminal-evidence-invalid")
    if lane == "fast":
        require(evidence.get("material_target_mutation") is False, "fast-terminal-target-mutation-invalid")
        require(evidence.get("actual_upgrade") is False, "fast-terminal-actual-upgrade-invalid")
    elif lane == "medium":
        require(evidence.get("synthetic_clean_install") is True, "medium-terminal-clean-install-missing")
        require(evidence.get("actual_upgrade") is False, "medium-terminal-actual-upgrade-invalid")
    else:
        require(evidence.get("actual_upgrade") is True, "long-terminal-actual-upgrade-missing")
        require(evidence.get("consumed_ai_context_test_tmp_root") is False, "long-terminal-tmp-root-consumed")
        required_phases = {"build", "extract", "snapshot", "plan", "decision", "apply", "receipt", "cleanup"}
        require(required_phases.issubset(phases), "long-terminal-phase-missing")
        require(
            all(phases[name].get("outcome") == "passed" for name in required_phases),
            "long-terminal-phase-not-passed",
        )
        require(evidence.get("legacy_immutable") is True, "long-terminal-legacy-immutability-missing")
        require(isinstance(evidence.get("git_inspection", {}).get("process_count"), dict), "long-terminal-process-count-missing")


def execute_lane(
    *,
    root: Path,
    lane: str,
    expected_commit: str,
    output_dir: Path,
    attempt: int = 1,
    prior_terminal: Path | None = None,
    material_state_change: str | None = None,
    authorization_ref: str | None = None,
    trusted_reference: bool = False,
) -> tuple[int, dict[str, object]]:
    require(lane in LANE_BUDGETS, "unsupported-lane")
    started = time.perf_counter_ns()
    output = validate_output_root(root, output_dir)
    subject = validate_subject(root, expected_commit)
    retry = validate_retry(
        lane=lane,
        subject_commit=expected_commit,
        attempt=attempt,
        prior_terminal=prior_terminal,
        material_state_change=material_state_change,
        authorization_ref=authorization_ref,
    )
    require(not trusted_reference or lane == "long", "trusted-reference-only-valid-for-long-lane")
    phases: dict[str, dict[str, object]] = {}
    outcome = "passed"
    reason_code: str | None = None
    fingerprint: str | None = None
    evidence: dict[str, object] = {}
    cleanup = {"outcome": "passed", "work_root_removed": False, "duration_ms": 0.0}
    try:
        implementations = {"fast": fast_lane, "medium": medium_lane, "long": long_lane}
        evidence = implementations[lane](root, expected_commit, output, phases)
    except Exception as error:  # terminal reporting must cover every admitted execution
        outcome, reason_code, fingerprint = failure_details(lane, expected_commit, error)
    finally:
        cleanup_started = time.perf_counter_ns()
        try:
            work = output / "work"
            if work.exists():
                remove_tree(work)
            cleanup["work_root_removed"] = not work.exists()
            if not cleanup["work_root_removed"]:
                raise OSError("cleanup did not remove work root")
        except OSError as error:
            cleanup["outcome"] = "failed"
            cleanup["work_root_removed"] = False
            if outcome == "passed":
                outcome, reason_code, fingerprint = failure_details(
                    lane, expected_commit, ValidationError("cleanup-failed")
                )
        cleanup["duration_ms"] = round((time.perf_counter_ns() - cleanup_started) / 1_000_000, 3)
        phases["cleanup"] = {
            "outcome": cleanup["outcome"],
            "duration_ms": cleanup["duration_ms"],
        }
    duration_ms = round((time.perf_counter_ns() - started) / 1_000_000, 3)
    command_identity = {
        "lane": lane,
        "subject_commit": expected_commit,
        "attempt": attempt,
        "trusted_reference": trusted_reference,
    }
    terminal: dict[str, object] = {
        "schema_version": SCHEMA_VERSION,
        "lane": lane,
        "outcome": outcome,
        "subject": {
            **subject,
            "source_version": SOURCE_VERSION,
            "candidate_version": CANDIDATE_VERSION,
        },
        "command": {
            "id": f"v015-package-validation-{lane}",
            "digest": sha256_bytes(canonical_json_bytes(command_identity)),
            "budget_seconds": LANE_BUDGETS[lane],
        },
        "execution": {
            "platform": host_platform(),
            "attempt": attempt,
            "trusted_reference": trusted_reference,
            "authorization_ref": authorization_ref,
            "duration_ms": duration_ms,
            "retry": retry,
            "ai_context_test_tmp_root_present": "AI_CONTEXT_TEST_TMP_ROOT" in os.environ,
        },
        "evidence": evidence,
        "phases": phases,
        "cleanup": cleanup,
        "failure_fingerprint": fingerprint,
    }
    if reason_code is not None:
        terminal["evidence"] = {**evidence, "reason_code": reason_code}
    validate_terminal_record(terminal)
    atomic_json(output / "terminal.json", terminal)
    return (0 if outcome == "passed" else 1), terminal


def aggregate_terminals(paths: Sequence[Path], output: Path) -> tuple[int, dict[str, object]]:
    terminals = [json.loads(path.read_text(encoding="utf-8")) for path in paths]
    require(terminals, "aggregate-terminals-required")
    for terminal in terminals:
        validate_terminal_record(terminal)
    commits = {terminal["subject"]["commit"] for terminal in terminals}
    require(len(commits) == 1, "aggregate-subject-mismatch")
    simple: dict[str, dict[str, object]] = {}
    long_by_platform: dict[str, dict[str, object]] = {}
    for terminal in terminals:
        lane = terminal["lane"]
        if lane in {"fast", "medium"}:
            require(lane not in simple, "aggregate-duplicate-lane")
            simple[lane] = terminal
        else:
            platform_id = terminal["execution"]["platform"]
            require(platform_id not in long_by_platform, "aggregate-duplicate-long-platform")
            long_by_platform[platform_id] = terminal
    lane_outcomes = {
        lane: simple.get(lane, {}).get("outcome", "not-applicable")
        for lane in ("fast", "medium")
    }
    trusted_platforms: dict[str, dict[str, object]] = {}
    for platform_id in ("windows", "linux"):
        terminal = long_by_platform.get(platform_id)
        if terminal is None:
            trusted_platforms[platform_id] = {
                "outcome": "blocked-by-environment",
                "reason_code": "trusted-reference-terminal-missing",
            }
        elif terminal["outcome"] != "passed":
            trusted_platforms[platform_id] = {"outcome": terminal["outcome"]}
        elif terminal["execution"].get("trusted_reference") is not True:
            trusted_platforms[platform_id] = {
                "outcome": "failed",
                "reason_code": "long-terminal-not-trusted-reference",
            }
        elif terminal.get("evidence", {}).get("actual_upgrade") is not True:
            trusted_platforms[platform_id] = {
                "outcome": "failed",
                "reason_code": "long-terminal-does-not-prove-actual-upgrade",
            }
        else:
            trusted_platforms[platform_id] = {
                "outcome": "passed",
                "terminal_digest": sha256_bytes(canonical_json_bytes(terminal)),
            }
    actual_upgrade_outcome = (
        "passed"
        if all(item["outcome"] == "passed" for item in trusted_platforms.values())
        else next(
            (
                item["outcome"]
                for item in trusted_platforms.values()
                if item["outcome"] != "passed"
            ),
            "failed",
        )
    )
    aggregate_outcome = (
        "passed"
        if lane_outcomes == {"fast": "passed", "medium": "passed"}
        and actual_upgrade_outcome == "passed"
        else actual_upgrade_outcome
        if actual_upgrade_outcome != "passed"
        else "failed"
    )
    aggregate = {
        "schema_version": AGGREGATE_SCHEMA_VERSION,
        "outcome": aggregate_outcome,
        "subject_commit": next(iter(commits)),
        "lanes": lane_outcomes,
        "trusted_actual_upgrade": trusted_platforms,
        "actual_upgrade_outcome": actual_upgrade_outcome,
        "projection": {
            "fast_or_medium_can_prove_actual_upgrade": False,
            "release_readiness_owner": "issue-254-integrated-main-gate",
        },
    }
    atomic_json(output, aggregate)
    return (0 if aggregate_outcome == "passed" else 1), aggregate
