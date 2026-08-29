#!/usr/bin/env python3
"""Run the release-only v0.15.1 clean-install and v0.15.0 upgrade gate."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Sequence

import yaml


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / ".ai/scripts"))

import ai_context_v015_validation as COMMON  # noqa: E402


SCHEMA_VERSION = "v0151-actual-upgrade-admission/v1"
CANDIDATE_VERSION = "0.15.1"
PREVIOUS_VERSION = "0.15.0"
CANDIDATE_PACKAGE_ID = "ai-collaboration-framework-v0.15.1"
PREVIOUS_PACKAGE_ID = "ai-collaboration-framework-v0.15.0"
AUDITOR_ROLE_PATH = (
    ".ai/assets/sub-agent-role-prompts/"
    "fixed-head-independent-auditor/sub-agent.yaml"
)


class AdmissionError(RuntimeError):
    """A path-free, deterministic release-admission failure."""


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def require(condition: bool, reason_code: str) -> None:
    if not condition:
        raise AdmissionError(reason_code)


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(COMMON.canonical_json_bytes(value) + b"\n")


def run(
    argv: Sequence[str], *, cwd: Path, evidence_root: Path, label: str
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
    (evidence_root / f"{label}.stdout.log").write_text(
        result.stdout, encoding="utf-8", newline="\n"
    )
    (evidence_root / f"{label}.stderr.log").write_text(
        result.stderr, encoding="utf-8", newline="\n"
    )
    if result.returncode != 0:
        raise AdmissionError(f"{label}-exit-{result.returncode}")
    return result


def extract_envelope(archive: Path, destination: Path, expected_id: str) -> Path:
    COMMON.extract_zip(archive, destination)
    envelope = destination / expected_id
    require(envelope.is_dir(), f"{expected_id}-envelope-missing")
    require(
        sorted(path.name for path in destination.iterdir()) == [expected_id],
        f"{expected_id}-unexpected-top-level-members",
    )
    return envelope


def load_package(envelope: Path, expected_id: str, expected_version: str) -> dict:
    package_path = envelope / "metadata/package.yaml"
    require(package_path.is_file(), f"{expected_id}-package-metadata-missing")
    package = yaml.safe_load(package_path.read_text(encoding="utf-8"))
    require(isinstance(package, dict), f"{expected_id}-package-metadata-invalid")
    require(package.get("package_id") == expected_id, f"{expected_id}-identity-mismatch")
    require(
        package.get("version") == expected_version,
        f"{expected_id}-version-mismatch",
    )
    return package


def assert_auditor_binding(target: Path, reason_prefix: str) -> None:
    skill_path = target / ".ai/assets/skills/ai-context-auditor/skill.yaml"
    require(skill_path.is_file(), f"{reason_prefix}-auditor-skill-missing")
    skill = yaml.safe_load(skill_path.read_text(encoding="utf-8"))
    bindings = skill.get("role_bindings") if isinstance(skill, dict) else None
    require(isinstance(bindings, list), f"{reason_prefix}-auditor-bindings-missing")
    require(
        any(
            isinstance(binding, dict)
            and binding.get("role_path") == AUDITOR_ROLE_PATH
            and binding.get("role_asset_id") == "fixed-head-independent-auditor"
            and binding.get("binding_kind") == "conditional"
            and binding.get("load_obligation") == "mandatory-when-applicable"
            for binding in bindings
        ),
        f"{reason_prefix}-auditor-binding-mismatch",
    )


def read_receipt(
    target: Path, candidate_package: dict, reason_prefix: str
) -> tuple[Path, dict]:
    receipt_path = target / ".dev/AI-CONTEXT-APPLY-PENDING.yaml"
    require(receipt_path.is_file(), f"{reason_prefix}-receipt-missing")
    receipt = yaml.safe_load(receipt_path.read_text(encoding="utf-8"))
    require(isinstance(receipt, dict), f"{reason_prefix}-receipt-invalid")
    require(
        receipt.get("package_id") == CANDIDATE_PACKAGE_ID,
        f"{reason_prefix}-receipt-package-id-mismatch",
    )
    require(
        receipt.get("package_version") == CANDIDATE_VERSION,
        f"{reason_prefix}-receipt-version-mismatch",
    )
    identity = candidate_package["identity"]
    require(
        receipt.get("package_manifest_sha256")
        == identity["files_manifest_digest"],
        f"{reason_prefix}-receipt-manifest-mismatch",
    )
    require(
        receipt.get("migration_sha256") == identity["migration_digest"],
        f"{reason_prefix}-receipt-migration-mismatch",
    )
    require(
        receipt.get("selected_input_proof")
        == {
            "path": "metadata/selected-inputs.json",
            "sha256": candidate_package["validation"]["selected_inputs_sha256"],
        },
        f"{reason_prefix}-receipt-selected-input-mismatch",
    )
    return receipt_path, receipt


def receipt_evidence(receipt_path: Path, receipt: dict, target: Path) -> dict:
    return {
        "package_id": receipt["package_id"],
        "package_version": receipt["package_version"],
        "package_manifest_sha256": receipt["package_manifest_sha256"],
        "migration_sha256": receipt["migration_sha256"],
        "selected_input_proof": receipt["selected_input_proof"],
        "receipt_sha256": COMMON.sha256_file(receipt_path),
        "installed_tree_sha256": COMMON.tree_digest(target),
    }


def write_upgrade_decision(
    packet_path: Path,
    evidence_root: Path,
    *,
    decided_at: str,
) -> Path:
    packet = json.loads(packet_path.read_text(encoding="utf-8"))
    proposal = packet["automatic_proposal"]
    package = packet["package"]
    candidate_provenance, candidate_customizations = (
        COMMON.TARGET.build_initialization_documents(
            {
                "repository": package["source"]["repository"],
                "release_id": f"REL-v{package['version']}",
                "version": f"v{package['version']}",
                "tag": f"v{package['version']}",
                "commit": package["source"]["commit"],
            },
            packet["selection"],
            decided_at,
        )
    )
    candidate_provenance["previous_source"] = packet["provenance"]["source"]
    candidate_provenance["installation"]["last_upgraded_at"] = decided_at
    candidate_provenance["last_migration"] = {
        "status": "completed",
        "from_version": f"v{PREVIOUS_VERSION}",
        "to_version": f"v{CANDIDATE_VERSION}",
        "completed_at": decided_at,
        "evidence": "hosted-v0151-release-admission",
    }
    provenance_bytes = COMMON.canonical_json_bytes(candidate_provenance)
    customizations_bytes = COMMON.canonical_json_bytes(candidate_customizations)
    (evidence_root / "candidate-provenance.json").write_bytes(provenance_bytes)
    (evidence_root / "candidate-customizations.json").write_bytes(
        customizations_bytes
    )
    decision = {
        "schema_version": "upgrade-remediation-decision/v1",
        "packet_sha256": packet["canonical_digest"],
        "plan_sha256": packet["plan_sha256"],
        "transaction_id": packet["transaction_id"],
        "status": "approved",
        "owner": "hosted-release-admission",
        "decided_at": decided_at,
        "evidence": "hosted-v0151-release-admission",
        "reason": "exercise the owner-authorized v0.15.1 actual-upgrade gate",
        "accepted_operation_ids": proposal["apply_operation_ids"],
        "reconciliation_ids": proposal["reconciliation_ids"],
        "policy_adoptions": candidate_provenance.get("policy_adoptions"),
        "candidate_authority": {
            "provenance_sha256": COMMON.sha256_bytes(provenance_bytes),
            "customizations_sha256": COMMON.sha256_bytes(customizations_bytes),
        },
    }
    decision_path = evidence_root / "remediation-decision.json"
    write_json(decision_path, decision)
    return decision_path


def execute(args: argparse.Namespace, evidence_root: Path) -> dict:
    candidate_extract = evidence_root / "work/candidate"
    previous_extract = evidence_root / "work/previous"
    candidate_root = extract_envelope(
        args.candidate_archive, candidate_extract, CANDIDATE_PACKAGE_ID
    )
    previous_root = extract_envelope(
        args.previous_archive, previous_extract, PREVIOUS_PACKAGE_ID
    )
    candidate_package = load_package(
        candidate_root, CANDIDATE_PACKAGE_ID, CANDIDATE_VERSION
    )
    previous_package = load_package(
        previous_root, PREVIOUS_PACKAGE_ID, PREVIOUS_VERSION
    )
    require(
        candidate_package["source"]["commit"] == args.subject_sha,
        "candidate-subject-sha-mismatch",
    )
    assert_auditor_binding(candidate_root / "payload", "candidate")

    planner = candidate_root / "payload/.ai/scripts/plan-ai-context-package-apply.py"
    require(planner.is_file(), "candidate-planner-missing")

    clean_target = evidence_root / "work/clean-install-target"
    clean_target.mkdir(parents=True)
    (clean_target / "target-owned.txt").write_text(
        "target truth\n", encoding="utf-8", newline="\n"
    )
    COMMON.initialize_git_target(clean_target, "v0.15.1 clean-install baseline")
    clean_result = run(
        (
            sys.executable,
            str(planner),
            "--package-root",
            str(candidate_root),
            "--target-root",
            str(clean_target),
            "--git-inspection-metrics",
            "--apply",
        ),
        cwd=ROOT,
        evidence_root=evidence_root,
        label="clean-install",
    )
    require(
        (clean_target / "target-owned.txt").read_text(encoding="utf-8")
        == "target truth\n",
        "clean-install-target-truth-mutated",
    )
    assert_auditor_binding(clean_target, "clean-install")
    clean_receipt_path, clean_receipt = read_receipt(
        clean_target, candidate_package, "clean-install"
    )
    shutil.copy2(clean_receipt_path, evidence_root / "clean-install-receipt.yaml")

    upgrade_target = evidence_root / "work/v0150-upgrade-target"
    shutil.copytree(previous_root / "payload", upgrade_target)
    (upgrade_target / "target-owned.txt").write_text(
        "target truth\n", encoding="utf-8", newline="\n"
    )
    COMMON.seed_upgrade_target_provenance(upgrade_target, previous_root)
    COMMON.initialize_git_target(upgrade_target, "published v0.15.0 target baseline")
    target_before = {
        "commit": COMMON.git(upgrade_target, "rev-parse", "HEAD").stdout.strip(),
        "tree": COMMON.git(
            upgrade_target, "rev-parse", "HEAD^{tree}"
        ).stdout.strip(),
        "payload_tree_sha256": COMMON.tree_digest(upgrade_target),
    }
    plan_path = evidence_root / "upgrade-plan.yaml"
    packet_path = evidence_root / "remediation-packet.json"
    base = (
        sys.executable,
        str(planner),
        "--package-root",
        str(candidate_root),
        "--target-root",
        str(upgrade_target),
        "--previous-files",
        str(previous_root / "metadata/files.yaml"),
        "--previous-version",
        PREVIOUS_VERSION,
        "--git-inspection-metrics",
    )
    plan_result = run(
        (*base, "--plan-output", str(plan_path), "--remediation-packet-output", str(packet_path)),
        cwd=ROOT,
        evidence_root=evidence_root,
        label="upgrade-plan",
    )
    decision_path = write_upgrade_decision(
        packet_path, evidence_root, decided_at=utc_now()
    )
    apply_result = run(
        (*base, "--apply", "--remediation-decision", str(decision_path)),
        cwd=ROOT,
        evidence_root=evidence_root,
        label="upgrade-apply",
    )
    require(
        (upgrade_target / "target-owned.txt").read_text(encoding="utf-8")
        == "target truth\n",
        "upgrade-target-truth-mutated",
    )
    assert_auditor_binding(upgrade_target, "upgrade")
    upgrade_receipt_path, upgrade_receipt = read_receipt(
        upgrade_target, candidate_package, "upgrade"
    )
    shutil.copy2(upgrade_receipt_path, evidence_root / "upgrade-receipt.yaml")

    plan_metrics = COMMON.parse_git_metrics(plan_result.stderr)
    apply_metrics = COMMON.parse_git_metrics(apply_result.stderr)
    clean_metrics = COMMON.parse_git_metrics(clean_result.stderr)
    require(
        len(clean_metrics) == 2
        and [item.get("phase") for item in clean_metrics] == ["plan", "apply"],
        "clean-install-git-metrics-missing",
    )
    require(
        len(plan_metrics) == 1 and plan_metrics[0].get("phase") == "plan",
        "upgrade-plan-git-metrics-missing",
    )
    require(
        len(apply_metrics) == 2
        and [item.get("phase") for item in apply_metrics] == ["plan", "apply"],
        "upgrade-apply-git-metrics-missing",
    )

    return {
        "candidate": {
            "package_id": candidate_package["package_id"],
            "version": candidate_package["version"],
            "subject_sha": candidate_package["source"]["commit"],
            "archive_sha256": COMMON.sha256_file(args.candidate_archive),
            "payload_fingerprint": candidate_package["identity"][
                "payload_fingerprint"
            ],
            "files_manifest_sha256": candidate_package["identity"][
                "files_manifest_digest"
            ],
            "migration_sha256": candidate_package["identity"][
                "migration_digest"
            ],
            "auditor_binding_verified": True,
        },
        "previous": {
            "package_id": previous_package["package_id"],
            "version": previous_package["version"],
            "archive_sha256": COMMON.sha256_file(args.previous_archive),
            "origin": "github-release:v0.15.0",
        },
        "clean_install": {
            "executed": True,
            "synthetic_target": True,
            "actual_package_apply": True,
            "receipt": receipt_evidence(
                clean_receipt_path, clean_receipt, clean_target
            ),
            "git_inspection": clean_metrics,
        },
        "upgrade": {
            "executed": True,
            "synthetic_target": True,
            "actual_package_apply": True,
            "from_version": f"v{PREVIOUS_VERSION}",
            "to_version": f"v{CANDIDATE_VERSION}",
            "target_snapshot_before": target_before,
            "receipt": receipt_evidence(
                upgrade_receipt_path, upgrade_receipt, upgrade_target
            ),
            "git_inspection": {
                "plan": plan_metrics,
                "apply": apply_metrics,
            },
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate-archive", type=Path, required=True)
    parser.add_argument("--previous-archive", type=Path, required=True)
    parser.add_argument("--subject-sha", required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    started_at = utc_now()
    started = time.monotonic()
    evidence_root = args.output.resolve()
    if evidence_root.exists():
        print(
            "v0.15.1 actual-upgrade admission failed: output-already-exists",
            file=sys.stderr,
        )
        return 1
    evidence_root.mkdir(parents=True)
    terminal_path = evidence_root / "terminal.json"
    terminal: dict[str, object] = {
        "schema_version": SCHEMA_VERSION,
        "subject_sha": args.subject_sha,
        "started_at": started_at,
        "completed_at": None,
        "duration_seconds": None,
        "executed": True,
        "outcome": "failed",
        "failure_reason": None,
        "evidence": None,
    }
    try:
        require(len(args.subject_sha) == 40, "subject-sha-invalid")
        require(args.candidate_archive.is_file(), "candidate-archive-missing")
        require(args.previous_archive.is_file(), "previous-archive-missing")
        terminal["evidence"] = execute(args, evidence_root)
        terminal["outcome"] = "passed"
        return_code = 0
    except (AdmissionError, COMMON.ValidationError) as error:
        terminal["failure_reason"] = str(error)
        return_code = 1
    except Exception as error:  # fail closed without leaking path-bearing details
        terminal["failure_reason"] = f"unexpected-{type(error).__name__}"
        return_code = 1
    finally:
        terminal["completed_at"] = utc_now()
        terminal["duration_seconds"] = round(time.monotonic() - started, 6)
        evidence_root.mkdir(parents=True, exist_ok=True)
        write_json(terminal_path, terminal)
    if return_code != 0:
        print(f"v0.15.1 actual-upgrade admission failed: {terminal['failure_reason']}", file=sys.stderr)
    else:
        print(f"v0.15.1 actual-upgrade admission passed: {terminal_path}")
    return return_code


if __name__ == "__main__":
    raise SystemExit(main())
