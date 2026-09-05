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
import re
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
    return {"argv": [str(value) for value in argv], "outcome": "passed" if result.returncode == 0 else "failed", "exit_code": result.returncode,
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


def fixture_customization(identity):
    return {"id": "CUST-UPGRADE-PRESERVATION", "subject": {"kind": "contract", "id": "target-upgrade-preservation"},
            "relationship": "target-only", "reason": "The target owns an additional migration acceptance contract.",
            "paths": ["owner.txt"], "base_framework": {"version": identity["version"], "commit": identity["commit"], "evidence": [EVIDENCE]},
            "dependencies": {"customization_ids": [], "subject_refs": []},
            "owner_reconciliation": {"status": "approved", "owner": "bounded-fixture-owner", "decided_at": stamp(), "evidence": EVIDENCE},
            "decision_evidence": {"requirements": [EVIDENCE], "adrs": [], "workflows": []},
            "active_context_audit": {"assessment_id": "ASM-20260905-271", "status": "verified", "evidence": EVIDENCE},
            "incoming": {"version": identity["version"], "status": "absent", "evidence": EVIDENCE}, "disposition": "retain",
            "post_upgrade_audit": {"assessment_id": "ASM-20260905-271", "status": "verified", "evidence": EVIDENCE},
            "validation": ["python .dev/validation/direct-upgrade-target.py"]}


TARGET_CHECK = '''import hashlib,json
from pathlib import Path
root=Path.cwd()
if (root/'.git/fail-target-validation').exists():
    raise SystemExit(17)
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
    if customized:
        ledger["customizations"] = [fixture_customization(source(old))]
    write_yaml(target / ".dev/ai-context/provenance.yaml", initial)
    write_yaml(target / ".dev/ai-context/customizations.yaml", ledger)
    decision = target / EVIDENCE
    decision.parent.mkdir(parents=True, exist_ok=True)
    decision.write_text("# Bounded fixture owner decision\n\nThis source-owned test fixture accepts unchanged framework replacements and removals, preserves all target-template paths and explicit local content, retains the target-only customization contract, adopts git-commit-subject/v2 at its reachable starting commit without rewriting history, accepts the incoming component and evidence catalog only for the declared review route, and requires actual target validation before provenance advancement. The baseline fixture audit verifies the owner.txt contract and its absence from the incoming manifest. Candidate post-upgrade audit status is an expected terminal state; the runner must execute the target check before publishing that candidate. No production target decision is inferred. Missing baseline effective state is explicitly reconciled to the incoming catalog at finalization.\n", encoding="utf-8")
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
    incoming_paths = {item["path"] for item in inventory}
    removed = [item["path"] for item in old_inventory if item["ownership"] == "framework-managed"
               and item["component_id"] in selected and item["path"] not in incoming_paths and item["path"] not in preserved]
    managed = {item["path"]: item["sha256"] for item in inventory if item["ownership"] == "framework-managed" and item["component_id"] in selected}
    config_path = target / ".dev/project-config.yaml"
    config = yaml.safe_load(config_path.read_bytes()) if config_path.exists() else {}
    config.setdefault("validation", {})["routine"] = {"argv": [sys.executable, ".dev/validation/direct-upgrade-target.py"]}
    write_yaml(config_path, config)
    preserved[".dev/project-config.yaml"] = sha(config_path.read_bytes())
    check = target / ".dev/validation/direct-upgrade-target.py"
    check.parent.mkdir(parents=True, exist_ok=True)
    check.write_text(TARGET_CHECK, encoding="utf-8", newline="\n")
    write_json(target / ".dev/validation/expected-v016.json", {"managed": managed, "preserved": preserved, "removed": removed})
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


def approved_decision(packet, candidate, ledger, provenance):
    proposal = packet["automatic_proposal"]
    return {"schema_version": "upgrade-remediation-decision/v1", "packet_sha256": packet["canonical_digest"],
            "plan_sha256": packet["plan_sha256"], "transaction_id": packet["transaction_id"], "status": "approved",
            "owner": "bounded-direct-upgrade-fixture-owner", "decided_at": stamp(), "evidence": EVIDENCE,
            "reason": "Apply exact direct origin migration; preserve every reconciled target-owned path.",
            "accepted_operation_ids": proposal["apply_operation_ids"], "reconciliation_ids": proposal["reconciliation_ids"],
            "policy_adoptions": candidate.get("policy_adoptions"), "candidate_authority": {"provenance_sha256": provenance.canonical_json_digest(candidate), "customizations_sha256": provenance.canonical_json_digest(ledger)}}


def reject_unchanged(label, operation, exception, pattern, target):
    before = snapshot(target)
    transactions = target / ".git/ai-context-package-apply"
    def transaction_evidence():
        return {key: value for key, value in snapshot(transactions).items() if key != "transaction.lock"} if transactions.exists() else {}
    before_transactions = transaction_evidence()
    try:
        operation()
    except exception as exc:
        require(re.search(pattern, str(exc), re.IGNORECASE), label + ": unexpected rejection reason: " + str(exc))
        require(snapshot(target) == before, label + ": protected target bytes changed")
        require(transaction_evidence() == before_transactions,
                label + ": transaction authority or evidence changed")
        return {"case": label, "outcome": "passed", "observed_rejection": type(exc).__name__,
                "reason_pattern": pattern, "protected_state_sha256": sha(canonical(before))}
    raise RuntimeError(label + ": invalid state was accepted")


def commit_fixture(target, logs, label):
    run(["git", "add", "--all"], target, logs, label + "-stage")
    run(["git", "commit", "-qm", "test(fixture): " + label], target, logs, label + "-commit")


def failing_validator_fixture(incoming):
    """Reseal an explicitly fault-injected envelope, never an admitted artifact."""
    package_root = incoming.parent.parent / "fault-injected-validator"
    if package_root.exists():
        return package_root
    shutil.copytree(incoming, package_root)
    relative = ".ai/scripts/validate-ai-context-payload.py"
    content = b"#!/usr/bin/env python3\nimport sys\nraise SystemExit(0 if '--help' in sys.argv else 17)\n"
    (package_root / "payload" / relative).write_bytes(content)
    metadata = package_root / "metadata"
    inventory = yaml.safe_load((metadata / "files.yaml").read_bytes())
    for record in inventory["files"]:
        if record["path"] == relative:
            record.update(sha256=sha(content), size=len(content))
    write_yaml(metadata / "files.yaml", inventory)
    files_digest = sha((metadata / "files.yaml").read_bytes())
    migration = yaml.safe_load((metadata / "migration.yaml").read_bytes())
    migration["to"]["manifest_sha256"] = files_digest
    write_yaml(metadata / "migration.yaml", migration)
    proof = json.loads((metadata / "selected-inputs.json").read_bytes())
    for record in proof["payload"]:
        if record["path"] == relative:
            record["sha256"] = sha(content)
    (metadata / "selected-inputs.json").write_bytes(canonical(proof).rstrip(b"\n"))
    proof_digest = sha((metadata / "selected-inputs.json").read_bytes())
    validation = json.loads((metadata / "validation.json").read_bytes())
    validation["authority"]["validator"]["sha256"] = sha(content)
    validation["selected_input_proof"]["sha256"] = proof_digest
    (metadata / "validation.json").write_bytes(canonical(validation).rstrip(b"\n"))
    payload_digest = sha("".join(f"{record['sha256']}  {record['path']}\n" for record in sorted(
        inventory["files"], key=lambda record: record["path"].encode())).encode())
    package = yaml.safe_load((metadata / "package.yaml").read_bytes())
    package["identity"].update(selected_input_fingerprint=proof_digest, payload_fingerprint=payload_digest,
                               files_manifest_digest=files_digest, migration_digest=sha((metadata / "migration.yaml").read_bytes()))
    package["payload"]["sha256"] = payload_digest
    package["validation"].update(selected_inputs_sha256=proof_digest, manifest_sha256=sha((metadata / "validation.json").read_bytes()))
    write_yaml(metadata / "package.yaml", package)
    checksums = metadata / "SHA256SUMS.txt"
    entries = sorted((path for path in package_root.rglob("*") if path.is_file() and path != checksums),
                     key=lambda path: path.relative_to(package_root).as_posix().encode())
    checksums.write_bytes("".join(f"{sha(path.read_bytes())}  {path.relative_to(package_root).as_posix()}\n" for path in entries).encode())
    return package_root


def negative_preflight(origin, previous, incoming, target, initial, ledger, logs, apply, provenance):
    results = []
    files = previous / "metadata/files.yaml"
    results.append(reject_unchanged("missing-origin-manifest", lambda: apply.build_plan(incoming, target, logs / "absent-files.yaml", origin), (apply.ApplyError, FileNotFoundError), "previous|cannot read|absent-files", target))
    tampered = logs / "tampered-files.yaml"
    tampered.write_bytes(files.read_bytes() + b"\n")
    results.append(reject_unchanged("tampered-origin-manifest", lambda: apply.build_plan(incoming, target, tampered, origin), apply.ApplyError, "source|manifest|previous", target))
    wrong = "v0.9.0" if origin != "v0.9.0" else "v0.6.0"
    results.append(reject_unchanged("origin-version-disagreement", lambda: apply.build_plan(incoming, target, files, wrong), apply.ApplyError, "source|manifest|previous", target))
    invalid_package = incoming.parent.parent / ("tampered-incoming-" + origin)
    shutil.copytree(incoming, invalid_package)
    validator = invalid_package / "payload/.ai/scripts/validate-ai-context-payload.py"
    validator.write_bytes(validator.read_bytes() + b"# unauthorized bytes\n")
    results.append(reject_unchanged("tampered-incoming-validator", lambda: apply.build_plan(invalid_package, target, files, origin), apply.ApplyError, "checksum|hash|digest|SHA", target))
    fault_package = failing_validator_fixture(incoming)
    apply.validate_package_root(fault_package)
    results.append(reject_unchanged("fault-injected-incoming-validator-disagreement", lambda: apply.build_plan(
        fault_package, target, files, origin), apply.ApplyError, "incoming package validator failed: exit=17", target))
    legacy = target / ".dev/AI-CONTEXT-SOURCE.yaml"
    write_yaml(legacy, {"schema_version": "1.0", "source": initial["source"], "local_overrides": []})
    commit_fixture(target, logs, "duplicate-authority")
    results.append(reject_unchanged("ambiguous-provenance-authority", lambda: apply.build_plan(incoming, target, files, origin), apply.ApplyError, "cannot coexist", target))
    legacy.unlink()
    commit_fixture(target, logs, "restore-one-authority")
    ledger_path = target / ".dev/ai-context/customizations.yaml"
    raw_ledger = ledger_path.read_bytes()
    pending = deepcopy(ledger)
    if not pending["customizations"]:
        pending["customizations"] = [fixture_customization(initial["source"])]
    pending["customizations"][0]["disposition"] = "unresolved"
    pending["customizations"][0]["owner_reconciliation"]["status"] = "pending"
    write_yaml(ledger_path, pending)
    commit_fixture(target, logs, "unresolved-customization")
    plan = apply.build_plan(incoming, target, files, origin)
    packet = apply.build_upgrade_remediation_packet(plan)
    decision = approved_decision(packet, initial, pending, provenance)
    results.append(reject_unchanged("unresolved-customization", lambda: apply.apply_plan(plan, remediation_decision=decision), apply.ApplyError, "unresolved target semantic customizations", target))
    require(not apply.transaction_root(target, plan["plan_sha256"]).exists(), "unresolved customization prepared a write transaction")
    ledger_path.write_bytes(raw_ledger)
    commit_fixture(target, logs, "restore-resolved-customization")
    return results


def record_validation(target, plan, apply, logs, provenance, candidate, ledger):
    transaction = apply.transaction_root(target, plan["plan_sha256"])
    packet = json.loads((transaction / apply.REMEDIATION_PACKET_PATH).read_bytes())
    journal = yaml.safe_load((transaction / "journal.yaml").read_bytes())
    output_path = transaction / apply.TARGET_VALIDATION_OUTPUT_PATH
    def make_receipt(execution, output):
        output_path.write_bytes(output)
        execution["evidence"] = output_path.relative_to(target).as_posix()
        return {"schema_version": "target-validation-receipt/v1", "transaction_id": plan["plan_sha256"], "plan_sha256": plan["plan_sha256"],
                "packet_sha256": packet["canonical_digest"], "decision_sha256": journal["remediation_decision_sha256"],
                "target": {key: packet["target"][key] for key in ("root", "starting_commit", "observed_prestate_sha256")},
                "target_validation_profile": packet["target_validation_profile"], "target_validation_profile_digest": packet["target_validation_profile_digest"],
                "pending_receipt": {"path": apply.PENDING_RECEIPT_PATH, "sha256": sha((target / apply.PENDING_RECEIPT_PATH).read_bytes())}, "execution": execution}
    fault = target / ".git/fail-target-validation"
    fault.write_bytes(b"bounded fault injection\n")
    failed_execution, failed_output = run(packet["target_validation_profile"]["argv"], target, logs, "target-validation-rejected", expected=17)
    failed_receipt = logs / "failed-target-validation.json"
    write_json(failed_receipt, make_receipt(failed_execution, failed_output))
    rejected = reject_unchanged("failed-target-validation-receipt", lambda: apply.record_target_validation_receipt(
        target, plan["plan_sha256"], failed_receipt), apply.ApplyError, "does not record a passed profile execution", target)
    blocked_finalization = reject_unchanged("target-validator-disagreement", lambda: provenance.finalize_context(
        target, candidate, ledger, effective_state_candidate=state_candidate(candidate["source"]), effective_resolver_evidence=[EVIDENCE]),
        provenance.TargetValidationError, "target validation|target-validation", target)
    fault.unlink()
    execution, output = run(packet["target_validation_profile"]["argv"], target, logs, "target-validation")
    receipt = make_receipt(execution, output)
    supplied = logs / "supplied-target-validation.json"
    write_json(supplied, receipt)
    invalid = logs / "tampered-target-validation.json"
    wrong = deepcopy(receipt)
    wrong["execution"]["output_sha256"] = "0" * 64
    write_json(invalid, wrong)
    rejected_receipt = reject_unchanged("tampered-target-validation-receipt", lambda: apply.record_target_validation_receipt(
        target, plan["plan_sha256"], invalid), apply.ApplyError, "output|execution|digest|bytes", target)
    apply.record_target_validation_receipt(target, plan["plan_sha256"], supplied)
    return receipt, [rejected, blocked_finalization, rejected_receipt], failed_execution


def case_artifacts(logs, output):
    return {path.name: {"path": path.relative_to(output).as_posix(), "sha256": sha(path.read_bytes())}
            for path in sorted(logs.iterdir()) if path.is_file()}


def capture_authority(target, logs, phase):
    for name in ("provenance", "customizations", "effective-rules"):
        path = target / f".dev/ai-context/{name}.yaml"
        if path.is_file():
            (logs / f"{name}-{phase}.yaml").write_bytes(path.read_bytes())


def execute_case(origin, previous, incoming, output, customized, recovery, apply, provenance, rules):
    label = origin + ("-customized" if customized else "-pristine") + "-" + recovery
    logs = output / "evidence" / label
    logs.mkdir(parents=True)
    target = output / "work" / label
    initial, ledger, preserved = seed_target(previous, incoming, target, customized, apply, provenance, rules, logs)
    negative = negative_preflight(origin, previous, incoming, target, initial, ledger, logs, apply, provenance) if not customized else []
    before = snapshot(target)
    write_json(logs / "prestate.json", before)
    capture_authority(target, logs, "before")
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
    candidate_ledger = deepcopy(ledger)
    for entry in candidate_ledger["customizations"]:
        entry["incoming"] = {"version": "v0.16.0", "status": "absent", "evidence": EVIDENCE}
        entry["post_upgrade_audit"] = {"assessment_id": "ASM-20260905-272", "status": "verified",
            "evidence": f".git/ai-context-package-apply/{plan['plan_sha256']}/{apply.TARGET_VALIDATION_OUTPUT_PATH}"}
    candidate["policy_adoptions"] = {"commit_subject_grammar": {
        "policy_id": "git-commit-subject/v2", "legacy_history_tip": packet["target"]["starting_commit"],
        "adopted_at": stamp(), "incoming_policy_sha256": sha((incoming / "payload/.dev/standards/GIT-COMMIT-POLICY.yaml").read_bytes()),
        "decision_evidence": EVIDENCE,
    }}
    decision = approved_decision(packet, candidate, candidate_ledger, provenance)
    write_json(logs / "decision.json", decision)
    # An unresolved owner decision must not create a transaction or change bytes.
    negative.append(reject_unchanged("missing-owner-decision", lambda: apply.apply_plan(plan), apply.ApplyError, "explicit approved remediation decision", target))
    invalid_decision = deepcopy(decision)
    invalid_decision["packet_sha256"] = "0" * 64
    negative.append(reject_unchanged("tampered-owner-decision", lambda: apply.apply_plan(plan, remediation_decision=invalid_decision), apply.ApplyError, "packet binding differs", target))
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
        interrupted = snapshot(target)
        write_json(logs / "interrupted.json", interrupted)
        require(interrupted != before, "interruption did not follow real writes")
        require((target / ".dev/ai-context/provenance.yaml").read_bytes() == yaml.safe_dump(initial, sort_keys=False).encode(), "interruption advanced provenance")
        result = apply.recover_transaction(target, plan["plan_sha256"], recovery, incoming if recovery == "resume" else None)
        write_json(logs / "recovery.json", result)
        if recovery == "rollback":
            write_json(logs / "poststate.json", snapshot(target))
            capture_authority(target, logs, "after")
            require(snapshot(target) == before, "rollback did not restore exact prestate")
            write_json(logs / "rollback.json", result)
            return {"origin": origin, "case": label, "outcome": "passed", "transaction_id": plan["plan_sha256"], "recovery": "rolled-back", "prestate_sha256": sha(canonical(before)), "poststate_sha256": sha(canonical(snapshot(target))), "negative_evidence": negative, "artifacts": case_artifacts(logs, output)}
    else:
        apply.apply_plan(plan, remediation_decision=decision)
    negative.append(reject_unchanged("missing-target-validation", lambda: provenance.finalize_context(
        target, candidate, candidate_ledger, effective_state_candidate=state_candidate(candidate["source"]), effective_resolver_evidence=[EVIDENCE]),
        provenance.TargetValidationError, "target validation|target-validation", target))
    receipt, validation_negatives, failed_validation = record_validation(target, plan, apply, logs, provenance, candidate, candidate_ledger)
    negative.extend(validation_negatives)
    wrong_candidate = deepcopy(candidate)
    wrong_candidate["source"]["commit"] = "f" * 40
    negative.append(reject_unchanged("candidate-authority-disagreement", lambda: provenance.finalize_context(
        target, wrong_candidate, candidate_ledger, effective_state_candidate=state_candidate(wrong_candidate["source"]), effective_resolver_evidence=[EVIDENCE]),
        provenance.TargetValidationError, "candidate|source|authority", target))
    finalized = provenance.finalize_context(target, candidate, candidate_ledger, effective_state_candidate=state_candidate(candidate["source"]), effective_resolver_evidence=[EVIDENCE])
    require(finalized["status"] == "finalized" and finalized["effective_rule_readiness"]["action_ready"], "finalization or readiness failed")
    errors = provenance.validate_target(target, require_effective_rules=True)
    require(not errors, "target validation failed: " + "; ".join(errors))
    installed = yaml.safe_load((target / ".dev/ai-context/provenance.yaml").read_bytes())
    installed_ledger = yaml.safe_load((target / ".dev/ai-context/customizations.yaml").read_bytes())
    require(installed["selection"] == initial["selection"], "provider/component selection changed")
    require(installed_ledger == candidate_ledger, "semantic customization reconciliation differs")
    require(installed["policy_adoptions"] == candidate["policy_adoptions"], "Git grammar adoption differs")
    for path, digest in preserved.items():
        require(sha((target / path).read_bytes()) == digest, "target-owned content changed")
    terminal_before = snapshot(target)
    write_json(logs / "poststate.json", terminal_before)
    capture_authority(target, logs, "after")
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
            "negative_evidence": negative, "failed_target_validation": failed_validation,
            "semantic_cutovers": {"provider_component_selection": "preserved", "source_specific_managed_removals": "verified",
                "target_customization_ids": [entry["id"] for entry in installed_ledger["customizations"]],
                "commit_grammar_adoption": "verified", "effective_rule_regeneration": "verified", "skill_retirement": "verified"},
            "prestate_sha256": sha(canonical(before)), "poststate_sha256": sha(canonical(terminal_before)), "artifacts": case_artifacts(logs, output)}


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
    terminal = {"schema_version": "direct-upgrade-execution/v1", "subject_sha": args.subject_sha, "started_at": stamp(), "evidence_kind": "actual-isolated-target-execution", "cases": [], "outcome": "failed",
                "runner": {"path": Path(__file__).relative_to(ROOT).as_posix(), "sha256": sha(Path(__file__).read_bytes())},
                "invocation": [sys.executable, Path(__file__).relative_to(ROOT).as_posix(), *sys.argv[1:]]}
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
        message = str(exc)
        for path, label in ((output, "VALIDATION_OUTPUT"), (ROOT, "SOURCE_ROOT")):
            message = message.replace(str(path).replace("\\", "\\\\"), label).replace(str(path), label)
        terminal["failure"] = {"type": type(exc).__name__, "message": message}
        terminal["failure_fingerprint"] = sha(canonical(terminal["failure"]))
        raise
    finally:
        terminal["completed_at"] = stamp()
        terminal["duration_seconds"] = round(time.monotonic() - started, 3)
        write_json(output / "terminal.json", terminal)
    print(json.dumps({"outcome": terminal["outcome"], "cases": len(terminal["cases"]), "duration_seconds": terminal["duration_seconds"]}))


if __name__ == "__main__":
    main()
