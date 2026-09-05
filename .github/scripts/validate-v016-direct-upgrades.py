#!/usr/bin/env python3
"""Execute real, isolated retained-origin targets against one incoming archive.

Fixture owner decisions authorize only the targets created below output/work.
The runner never applies a package to its source checkout or a user repository.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import importlib
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import subprocess
import sys
import time
import zipfile

sys.dont_write_bytecode = True
import yaml

ROOT = Path(__file__).resolve().parents[2]
ORIGINS = {
    "v0.6.0": ("46f906ed67b04dc35b4d28475e092cf336f230660f6f1180f10082fbdf9e8371", "20ca69ef4e1b4085476a2b15eeba93da7a75ea580fd2ab9f6c8815938b0af3be"),
    "v0.9.0": ("2c98ac02eabd24ca881798caf83657adc2062ababe42fdb09fe26ce499cc98f2", "c293247612eb2f01ef42e4d7c55be4ff36201cdf034157c518de871ec2acb5c7"),
    "v0.15.1": ("cbabde70a921eba8c59255fc2f414961c9aaab0151b08d27956071f8f1c066ca", "8edcb120fe00b16e803f161ec31861ff45a30d8697a5a3e5c58931f7f2b5d1ad"),
}
EVIDENCE = ".dev/decisions/direct-v016-fixture.md"


def stamp():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def canonical(value):
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False) + "\n").encode()


def sha(value):
    return hashlib.sha256(value).hexdigest()


def require(condition, reason):
    if not condition:
        raise RuntimeError(reason)


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(canonical(value))


def write_yaml(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(value, sort_keys=False), encoding="utf-8", newline="\n")


def run(argv, cwd, logs, label, expected=0):
    started = stamp()
    result = subprocess.run([str(value) for value in argv], cwd=cwd, capture_output=True)
    logs.mkdir(parents=True, exist_ok=True)
    output = result.stdout + result.stderr
    (logs / (label + ".log")).write_bytes(output)
    require(result.returncode == expected, f"{label}: exit {result.returncode}; see retained log")
    return {"argv": [str(value) for value in argv], "outcome": "passed", "exit_code": result.returncode,
            "started_at": started, "completed_at": stamp(), "output_sha256": sha(output)}, output


def extract(archive, destination):
    destination.mkdir(parents=True, exist_ok=False)
    with zipfile.ZipFile(archive) as opened:
        seen = set()
        for member in opened.infolist():
            path = PurePosixPath(member.filename)
            require(not path.is_absolute() and ".." not in path.parts and "\\" not in member.filename and ":" not in member.filename, "unsafe archive path")
            require(member.filename not in seen, "duplicate archive member")
            seen.add(member.filename)
            require(((member.external_attr >> 16) & 0o170000) != 0o120000, "archive symlink")
            require((destination / member.filename).resolve().is_relative_to(destination.resolve()), "archive escape")
        opened.extractall(destination)
        for member in opened.infolist():
            if not member.is_dir():
                mode = (member.external_attr >> 16) & 0o777
                require(mode in {0o644, 0o755}, "invalid package file mode")
                (destination / member.filename).chmod(mode)
    children = list(destination.iterdir())
    require(len(children) == 1 and children[0].is_dir(), "noncanonical envelope root")
    return children[0]


def snapshot(target):
    return {path.relative_to(target).as_posix(): {"sha256": sha(path.read_bytes()), "mode": path.stat().st_mode & 0o777}
            for path in sorted(target.rglob("*")) if path.is_file() and ".git" not in path.relative_to(target).parts}


def source(package):
    version = "v" + package["version"]
    return {"repository": package["source"]["repository"], "release_id": package["release_id"],
            "version": version, "tag": version, "commit": package["source"]["commit"]}


def state_candidate(identity):
    return {"schema_version": "1.0", "framework": {"version": identity["version"], "commit": identity["commit"], "selected_technology_profile": "dotnet-backend"},
            "rule_dispositions": [{"rule_id": "AICTX-EVIDENCE-001", "effective_disposition": "baseline-effective",
                "applicability": "This isolated upgrade validation target uses repository evidence for migration verification.",
                "evidence": [EVIDENCE], "baseline_acceptance": {"explicit": True, "verification": {"status": "verified", "evidence": [EVIDENCE]}}}],
            "routing": [{"selector": {"capability": "review", "execution_mode": "direct", "technology_profile": "dotnet-backend", "file_type": "python"},
                         "required_rule_ids": ["AICTX-EVIDENCE-001"], "reported_not_applicable_rule_ids": []}]}


TARGET_CHECK = '''import hashlib,json
from pathlib import Path
root=Path.cwd()
expected=json.loads((root/'.dev/validation/expected-v016.json').read_bytes())
for path,digest in expected['managed'].items():
    assert hashlib.sha256((root/path).read_bytes()).hexdigest()==digest,path
for path,digest in expected['preserved'].items():
    assert hashlib.sha256((root/path).read_bytes()).hexdigest()==digest,path
for path in expected['removed']:
    assert not (root/path).exists(),path
print('All selected incoming managed bytes, target-owned content and retired removals verified.')
'''


def seed_target(previous, incoming, target, customized, apply, provenance, rules, logs):
    shutil.copytree(previous / "payload", target)
    old = yaml.safe_load((previous / "metadata/package.yaml").read_bytes())
    new = yaml.safe_load((incoming / "metadata/package.yaml").read_bytes())
    inventory = yaml.safe_load((incoming / "metadata/files.yaml").read_bytes())["files"]
    old_inventory = yaml.safe_load((previous / "metadata/files.yaml").read_bytes())["files"]
    selection = deepcopy(old["selection"])
    initial, ledger = provenance.build_initialization_documents(source(old), selection, stamp())
    write_yaml(target / ".dev/ai-context/provenance.yaml", initial)
    write_yaml(target / ".dev/ai-context/customizations.yaml", ledger)
    decision = target / EVIDENCE
    decision.parent.mkdir(parents=True, exist_ok=True)
    decision.write_text("# Bounded fixture owner decision\n\nThis source-owned test fixture accepts unchanged framework replacements and removals, preserves all target-template paths and explicit local content, adopts the incoming component and evidence catalog only for the declared review route, and requires actual target validation before provenance advancement. No production target decision is inferred. Missing baseline effective state is explicitly reconciled to the incoming catalog at finalization.\n", encoding="utf-8")
    owner = target / "owner.txt"
    owner.write_bytes(b"target-owned content must survive\n")
    preserved = {"owner.txt": sha(owner.read_bytes()), EVIDENCE: sha(decision.read_bytes())}
    retired = [record["path"] for record in old_inventory if record["ownership"] == "framework-managed" and
               record["path"] not in {item["path"] for item in inventory} and
               ("/dev-workflow/" in record["path"] or "/repo-structure-sync/" in record["path"])]
    require(retired, "origin lacks expected retained skill retirement paths")
    if customized:
        path = retired[0]
        local = target / path
        local.write_bytes(local.read_bytes() + b"\nFixture target-owned historical customization.\n")
        preserved[path] = sha(local.read_bytes())
        retired.remove(path)
    selected = apply.enabled_components(selection)
    managed = {item["path"]: item["sha256"] for item in inventory if item["ownership"] == "framework-managed" and item["component_id"] in selected}
    config_path = target / ".dev/project-config.yaml"
    config = yaml.safe_load(config_path.read_bytes()) if config_path.exists() else {}
    config.setdefault("validation", {})["routine"] = {"argv": [sys.executable, ".dev/validation/direct-upgrade-target.py"]}
    write_yaml(config_path, config)
    preserved[".dev/project-config.yaml"] = sha(config_path.read_bytes())
    check = target / ".dev/validation/direct-upgrade-target.py"
    check.parent.mkdir(parents=True, exist_ok=True)
    check.write_text(TARGET_CHECK, encoding="utf-8", newline="\n")
    write_json(target / ".dev/validation/expected-v016.json", {"managed": managed, "preserved": preserved, "removed": retired})
    # Older sources predate effective catalogs. Their absence remains visible;
    # the explicit fixture decision above supplies incoming adoption at finalization.
    catalog = target / rules.SHARED_CATALOG_PATH
    if catalog.is_file():
        state, packets = rules.build_effective_state_and_packets(target, state_candidate(source(old)), resolver_evidence=[EVIDENCE])
        rules.write_effective_state_and_packets(target, state, packets)
    for argv in (["git", "init", "-q"], ["git", "config", "core.autocrlf", "false"], ["git", "config", "core.longpaths", "true"],
                 ["git", "config", "user.name", "Direct Upgrade Fixture"], ["git", "config", "user.email", "fixture@example.invalid"],
                 ["git", "add", "--all"], ["git", "commit", "-qm", "test(fixture): record exact origin and bounded target decisions"]):
        run(argv, target, logs, "seed-" + argv[1] + (argv[2] if len(argv) > 2 else ""))
    return initial, ledger, preserved


def approved_decision(packet, candidate, ledger):
    proposal = packet["automatic_proposal"]
    return {"schema_version": "upgrade-remediation-decision/v1", "packet_sha256": packet["canonical_digest"],
            "plan_sha256": packet["plan_sha256"], "transaction_id": packet["transaction_id"], "status": "approved",
            "owner": "bounded-direct-upgrade-fixture-owner", "decided_at": stamp(), "evidence": EVIDENCE,
            "reason": "Apply exact direct origin migration; preserve every reconciled target-owned path.",
            "accepted_operation_ids": proposal["apply_operation_ids"], "reconciliation_ids": proposal["reconciliation_ids"],
            "policy_adoptions": candidate.get("policy_adoptions"), "candidate_authority": {"provenance_sha256": sha(canonical(candidate)), "customizations_sha256": sha(canonical(ledger))}}


def record_validation(target, plan, apply, logs):
    transaction = apply.transaction_root(target, plan["plan_sha256"])
    packet = json.loads((transaction / apply.REMEDIATION_PACKET_PATH).read_bytes())
    journal = yaml.safe_load((transaction / "journal.yaml").read_bytes())
    execution, output = run(packet["target_validation_profile"]["argv"], target, logs, "target-validation")
    output_path = transaction / apply.TARGET_VALIDATION_OUTPUT_PATH
    output_path.write_bytes(output)
    execution["evidence"] = output_path.relative_to(target).as_posix()
    receipt = {"schema_version": "target-validation-receipt/v1", "transaction_id": plan["plan_sha256"], "plan_sha256": plan["plan_sha256"],
               "packet_sha256": packet["canonical_digest"], "decision_sha256": journal["remediation_decision_sha256"],
               "target": {key: packet["target"][key] for key in ("root", "starting_commit", "observed_prestate_sha256")},
               "target_validation_profile": packet["target_validation_profile"], "target_validation_profile_digest": packet["target_validation_profile_digest"],
               "pending_receipt": {"path": apply.PENDING_RECEIPT_PATH, "sha256": sha((target / apply.PENDING_RECEIPT_PATH).read_bytes())}, "execution": execution}
    supplied = logs / "supplied-target-validation.json"
    write_json(supplied, receipt)
    apply.record_target_validation_receipt(target, plan["plan_sha256"], supplied)
    return receipt


def execute_case(origin, previous, incoming, output, customized, recovery, apply, provenance, rules):
    label = origin + ("-customized" if customized else "-pristine") + "-" + recovery
    logs = output / "evidence" / label
    logs.mkdir(parents=True)
    target = output / "work" / label
    initial, ledger, preserved = seed_target(previous, incoming, target, customized, apply, provenance, rules, logs)
    before = snapshot(target)
    plan = apply.build_plan(incoming, target, previous / "metadata/files.yaml", origin)
    require(plan["previous_version"].lstrip("v") == origin.lstrip("v"), "wrong selected origin")
    require(not plan.get("multi_hop_route_context"), "intermediate route context forbidden")
    packet = apply.build_upgrade_remediation_packet(plan)
    write_json(logs / "packet.json", packet)
    require(snapshot(target) == before, "planner changed target")
    candidate, _ = provenance.build_initialization_documents(source(yaml.safe_load((incoming / "metadata/package.yaml").read_bytes())), packet["selection"], stamp())
    candidate["previous_source"] = initial["source"]
    candidate["installation"]["last_upgraded_at"] = stamp()
    candidate["last_migration"] = {"status": "completed", "from_version": origin, "to_version": "v0.16.0", "completed_at": stamp(), "evidence": EVIDENCE}
    decision = approved_decision(packet, candidate, ledger)
    write_json(logs / "decision.json", decision)
    # An unresolved owner decision must not create a transaction or change bytes.
    try:
        apply.apply_plan(plan)
    except apply.ApplyError:
        require(snapshot(target) == before, "missing decision changed target")
    else:
        raise RuntimeError("missing owner decision accepted")
    if recovery in {"resume", "rollback"}:
        def crash(event, details):
            if event == "after_progress_journal":
                raise apply.InjectedInterruption("bounded actual durable-operation interruption")
        try:
            apply.apply_plan(plan, boundary_hook=crash, remediation_decision=decision)
        except apply.InjectedInterruption:
            pass
        else:
            raise RuntimeError("interruption boundary was not executed")
        require(snapshot(target) != before, "interruption did not follow real writes")
        require((target / ".dev/ai-context/provenance.yaml").read_bytes() == yaml.safe_dump(initial, sort_keys=False).encode(), "interruption advanced provenance")
        result = apply.recover_transaction(target, plan["plan_sha256"], recovery, incoming if recovery == "resume" else None)
        if recovery == "rollback":
            require(snapshot(target) == before, "rollback did not restore exact prestate")
            write_json(logs / "rollback.json", result)
            return {"origin": origin, "case": label, "outcome": "passed", "transaction_id": plan["plan_sha256"], "recovery": "rolled-back", "prestate_sha256": sha(canonical(before))}
    else:
        apply.apply_plan(plan, remediation_decision=decision)
    try:
        provenance.finalize_context(target, candidate, ledger)
    except provenance.TargetValidationError:
        require(yaml.safe_load((target / ".dev/ai-context/provenance.yaml").read_bytes())["source"] == initial["source"], "premature finalization advanced provenance")
    else:
        raise RuntimeError("finalization accepted missing target validation")
    receipt = record_validation(target, plan, apply, logs)
    finalized = provenance.finalize_context(target, candidate, ledger, effective_state_candidate=state_candidate(candidate["source"]), effective_resolver_evidence=[EVIDENCE])
    require(finalized["status"] == "finalized" and finalized["effective_rule_readiness"]["action_ready"], "finalization or readiness failed")
    errors = provenance.validate_target(target, require_effective_rules=True)
    require(not errors, "target validation failed: " + "; ".join(errors))
    for path, digest in preserved.items():
        require(sha((target / path).read_bytes()) == digest, "target-owned content changed")
    terminal_before = snapshot(target)
    try:
        apply.recover_transaction(target, plan["plan_sha256"], "rollback")
    except apply.ApplyError:
        require(snapshot(target) == terminal_before, "finalized rollback changed target")
    else:
        raise RuntimeError("finalized rollback accepted")
    write_json(logs / "finalization.json", finalized)
    return {"origin": origin, "case": label, "outcome": "passed", "transaction_id": plan["plan_sha256"], "recovery": recovery,
            "incoming_validation": packet["package"]["validation"], "target_validation": receipt["execution"], "finalization": finalized,
            "reconciliation_count": len(packet["automatic_proposal"]["reconciliation_ids"]), "preserved_paths": sorted(preserved),
            "prestate_sha256": sha(canonical(before)), "poststate_sha256": sha(canonical(terminal_before))}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate-archive", type=Path, required=True)
    parser.add_argument("--origin-archive", type=Path, action="append", required=True)
    parser.add_argument("--subject-sha", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--preflight-only", action="store_true")
    args = parser.parse_args()
    output = args.output.resolve()
    require(output.is_relative_to(ROOT / ".dev/ai-context/local/validation") or os.environ.get("RUNNER_TEMP") and output.is_relative_to(Path(os.environ["RUNNER_TEMP"]).resolve()), "output must be declared ignored validation storage")
    require(not output.exists(), "fresh output directory required")
    output.mkdir(parents=True)
    terminal = {"schema_version": "direct-upgrade-execution/v1", "subject_sha": args.subject_sha, "started_at": stamp(), "evidence_kind": "actual-isolated-target-execution", "cases": [], "outcome": "failed"}
    started = time.monotonic()
    try:
        require(subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip() == args.subject_sha, "source commit drift")
        require(not subprocess.check_output(["git", "status", "--porcelain", "--untracked-files=normal"], cwd=ROOT, text=True).strip(), "source checkout must be clean")
        candidate = args.candidate_archive.resolve()
        require(candidate.with_suffix(candidate.suffix + ".sha256").read_text().split()[0] == sha(candidate.read_bytes()), "candidate sidecar mismatch")
        incoming = extract(candidate, output / "incoming")
        package = yaml.safe_load((incoming / "metadata/package.yaml").read_bytes())
        require(package["version"] == "0.16.0", "wrong incoming version")
        terminal["archive_sha256"] = sha(candidate.read_bytes())
        terminal["package_source"] = package["source"]
        sys.path.insert(0, str(incoming / "payload/.ai/scripts"))
        apply = importlib.import_module("ai_context_package_apply")
        provenance = importlib.import_module("ai_context_target_provenance")
        rules = importlib.import_module("ai_context_effective_rules")
        apply.validate_package_root(incoming)
        origins = {}
        for archive in args.origin_archive:
            actual = sha(archive.read_bytes())
            versions = [version for version, hashes in ORIGINS.items() if hashes[0] == actual]
            require(len(versions) == 1 and versions[0] not in origins, "unrecognized or duplicate published origin")
            origin = versions[0]
            previous = extract(archive, output / ("origin-" + origin))
            require(sha((previous / "metadata/files.yaml").read_bytes()) == ORIGINS[origin][1], "origin manifest differs")
            origins[origin] = previous
        require(set(origins) == set(ORIGINS), "all three public origins are required")
        for origin in ORIGINS:
            for customized, recovery in ((False, "resume"), (True, "none"), (True, "rollback")):
                if args.preflight_only:
                    logs = output / "evidence" / origin
                    target = output / "work" / origin
                    seed_target(origins[origin], incoming, target, customized, apply, provenance, rules, logs)
                    plan = apply.build_plan(incoming, target, origins[origin] / "metadata/files.yaml", origin)
                    write_json(logs / "packet.json", apply.build_upgrade_remediation_packet(plan))
                    terminal["cases"].append({"origin": origin, "outcome": "planned-only", "summary": plan.get("component_operation_counts")})
                    break
                terminal["cases"].append(execute_case(origin, origins[origin], incoming, output, customized, recovery, apply, provenance, rules))
                write_json(output / "progress.json", terminal)
        terminal["outcome"] = "planned-only" if args.preflight_only else "passed"
    except Exception as exc:
        terminal["failure"] = {"type": type(exc).__name__, "message": str(exc).replace(str(output), "VALIDATION_OUTPUT").replace(str(ROOT), "SOURCE_ROOT")}
        terminal["failure_fingerprint"] = sha(canonical(terminal["failure"]))
        raise
    finally:
        terminal["completed_at"] = stamp()
        terminal["duration_seconds"] = round(time.monotonic() - started, 3)
        write_json(output / "terminal.json", terminal)
    print(json.dumps({"outcome": terminal["outcome"], "cases": len(terminal["cases"]), "duration_seconds": terminal["duration_seconds"]}))


if __name__ == "__main__":
    main()
