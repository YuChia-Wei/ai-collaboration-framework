#!/usr/bin/env python3
"""GWT tests for deterministic, privacy-preserving validation evidence."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from pathlib import Path
from typing import Any, Callable


ROOT = Path(__file__).resolve().parents[3]
HELPER = ROOT / ".ai/scripts/validation-evidence.py"
INVOCATION_ID = "fixture-invocation"


class ValidationEvidenceFixture(unittest.TestCase):
    """Shared isolated repository fixture; no test methods live here."""
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="validation-evidence-")
        self.repo = Path(self.temporary.name) / "repo"
        self.repo.mkdir()
        self.inputs = self.repo / "inputs"
        self.inputs.mkdir()
        (self.inputs / "rule.md").write_text("governed bytes\n", encoding="utf-8")
        self.logs = self.repo / "artifacts/validation/run"
        self.logs.mkdir(parents=True)
        self.log = self.logs / "check.log"
        self.log.write_text("private-token=must-not-appear\n", encoding="utf-8")
        self.cache = self.repo / "artifacts/validation/evidence-cache.json"
        self.evidence = self.logs / "evidence.jsonl"
        self.git_initialized = False

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def helper(self, *arguments: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(HELPER), *arguments],
            check=False,
            capture_output=True,
            text=True,
            timeout=30,
        )

    def load_helper_module(self, suffix: str) -> Any:
        spec = importlib.util.spec_from_file_location(
            f"validation_evidence_{suffix}", HELPER
        )
        self.assertIsNotNone(spec)
        self.assertIsNotNone(spec.loader)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def git(self, *arguments: str) -> None:
        result = subprocess.run(
            ["git", *arguments],
            cwd=self.repo,
            check=False,
            capture_output=True,
            text=True,
            timeout=30,
        )
        self.assertEqual(0, result.returncode, result.stderr)

    def initialize_git(self) -> None:
        if self.git_initialized:
            return
        self.git("init")
        self.git("config", "user.email", "validator@example.test")
        self.git("config", "user.name", "Validator Fixture")
        (self.repo / ".gitignore").write_text("artifacts/\n", encoding="utf-8")
        self.git("add", "inputs/rule.md", ".gitignore")
        self.git("commit", "-m", "fixture")
        self.git_initialized = True

    def install_tracked_helper(self, message: str = "tracked bootstrap helper fixture") -> None:
        self.initialize_git()
        fixture_helper = self.repo / ".ai/scripts/validation-evidence.py"
        fixture_helper.parent.mkdir(parents=True, exist_ok=True)
        fixture_helper.write_bytes(HELPER.read_bytes())
        self.git("add", fixture_helper.relative_to(self.repo).as_posix())
        self.git("commit", "-m", message)

    def supervise(
        self,
        snapshot: Path,
        *argv: str,
        timeout_seconds: float = 5,
        accepted_child_exit_codes: tuple[int, ...] = (),
        name: str = "supervised",
    ) -> tuple[subprocess.CompletedProcess[str], Path, Path]:
        log = self.logs / f"{name}.log"
        result_path = self.logs / f"{name}-result.json"
        arguments = [
            "supervise",
            "--repo", str(self.repo),
            "--snapshot", str(snapshot),
            "--log-path", str(log),
            "--result-path", str(result_path),
            "--timeout-seconds", str(timeout_seconds),
            "--cwd-ref", ".",
        ]
        for code in accepted_child_exit_codes:
            arguments.extend(("--accepted-child-exit-code", str(code)))
        arguments.extend((
            "--",
            *argv,
        ))
        result = self.helper(*arguments)
        return result, log, result_path

    def supervise_bootstrap(
        self,
        snapshot: Path,
        *argv: str,
        profile: str = "fast",
        require_clean: bool = False,
        timeout_seconds: float = 10,
        name: str = "bootstrap-snapshot-control",
    ) -> tuple[subprocess.CompletedProcess[str], Path, Path]:
        log = self.logs / f"{name}.log"
        result_path = self.logs / f"{name}.json"
        arguments = [
            "supervise", "--repo", str(self.repo),
            "--bootstrap-snapshot-output", str(snapshot),
            "--bootstrap-profile", profile,
            "--bootstrap-python", sys.executable,
            "--log-path", str(log),
            "--result-path", str(result_path),
            "--timeout-seconds", str(timeout_seconds),
            "--cwd-ref", ".",
        ]
        if require_clean:
            arguments.append("--bootstrap-require-clean")
        arguments.extend(("--", *argv))
        return self.helper(*arguments), log, result_path

    def capture_snapshot(
        self,
        *,
        profile: str = "release",
        require_clean: bool = True,
        name: str = "snapshot-pre.json",
    ) -> Path:
        snapshot = self.logs / name
        arguments = [
            "snapshot", "--repo", str(self.repo), "--output", str(snapshot),
            "--profile", profile,
        ]
        if require_clean:
            arguments.append("--require-clean")
        result = self.helper(*arguments)
        self.assertEqual(0, result.returncode, result.stderr)
        return snapshot

    @staticmethod
    def json_bytes(value: object) -> bytes:
        return (
            json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
        ).encode("utf-8")

    @staticmethod
    def canonical_digest(value: object) -> str:
        return hashlib.sha256(
            json.dumps(
                value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
            ).encode("utf-8")
        ).hexdigest()

    @staticmethod
    def line_count(content: bytes) -> int:
        return 0 if not content else content.count(b"\n") + (
            0 if content.endswith(b"\n") else 1
        )

    def lookup(
        self,
        *,
        validator_id: str = "fixture-check",
        version: str = "validator-v1",
        profile: str = "fast",
        environment: str = "windows-native",
    ) -> tuple[str, bool]:
        result = self.helper(
            "lookup", "--repo", str(self.repo), "--cache", str(self.cache),
            "--validator-id", validator_id, "--validator-version", version,
            "--profile", profile, "--environment-class", environment,
            "--input-paths", "inputs", "--cache-policy", "reuse-by-input",
        )
        self.assertEqual(0, result.returncode, result.stderr)
        fingerprint, reusable, _ = result.stdout.rstrip("\r\n").split("\t")
        return fingerprint, reusable == "true"

    def record_current(
        self,
        fingerprint: str,
        *,
        validator_id: str = "fixture-check",
        version: str = "validator-v1",
        outcome: str = "passed",
        disposition: str = "executed",
        result_path: Path | None = None,
        snapshot: Path | None = None,
        profile: str = "fast",
        enforcement: str | None = "required",
        log_path: Path | None = None,
        evidence: Path | None = None,
        cache_hit: bool = False,
        selection_reason: str = "fixture",
    ) -> subprocess.CompletedProcess[str]:
        log_path = log_path or self.log
        evidence = evidence or self.evidence
        arguments = [
            "record", "--repo", str(self.repo), "--cache", str(self.cache),
            "--evidence", str(evidence), "--invocation-id", INVOCATION_ID,
            "--validator-id", validator_id, "--validator-version", version,
            "--profile", profile, "--environment-class", "windows-native",
            "--input-fingerprint", fingerprint, "--outcome", outcome,
            "--disposition", disposition, "--started-ms", "1000",
            "--completed-ms", "1010", "--duration-ms", "10",
            "--suppressed-output-bytes", "-1", "--subprocess-count", "1",
            "--log-path", str(log_path), "--selection-reason", selection_reason,
            "--changed-paths-digest", "fixture-changed-paths",
        ]
        if cache_hit:
            arguments.append("--cache-hit")
        if enforcement is not None:
            arguments.extend(("--enforcement", enforcement))
        if result_path is not None:
            arguments.extend(("--result-path", str(result_path)))
        if snapshot is not None:
            arguments.extend(("--snapshot", str(snapshot)))
        return self.helper(*arguments)

    def write_receipt(
        self,
        snapshot: Path,
        *,
        log_path: Path | None = None,
        name: str = "execution",
        raw_status: str = "completed",
        child_exit_code: int | None = 0,
        wrapper_status: str | None = None,
        post_verified: bool = True,
        directory: Path | None = None,
        safe_argv: list[str] | None = None,
        effective_argv: list[str] | None = None,
        accepted_child_exit_codes: list[int] | None = None,
        bootstrap_target_argv: list[str] | None = None,
        bootstrap_profile: str = "fast",
    ) -> Path:
        log_path = log_path or self.log
        snapshot_value = json.loads(snapshot.read_text(encoding="utf-8"))
        argv = safe_argv or ["python", "-c", "pass"]
        effective = effective_argv or argv
        content = log_path.read_bytes()
        trigger = {
            "completed": None,
            "timed-out": "timeout",
            "cancelled": "cancelled",
            "cleanup-failed": "orphan-descendant",
            "launch-failed": "launch-failure",
        }[raw_status]
        tree_empty = raw_status != "cleanup-failed"
        sealed = tree_empty
        termination = {
            "trigger": trigger,
            "soft_signal_sent": trigger in {"timeout", "cancelled", "orphan-descendant"},
            "hard_kill_sent": trigger in {"timeout", "cancelled", "orphan-descendant"},
            "root_reaped": raw_status != "launch-failed",
            "tree_empty": tree_empty,
            "active_processes": 0 if tree_empty else 1,
            "verification": "fixture-proof",
            "errors": [] if tree_empty else ["tree-not-empty"],
        }
        raw_log = {
            "sealed": sealed,
            "sha256": hashlib.sha256(content).hexdigest() if sealed else None,
            "bytes": len(content) if sealed else None,
            "lines": self.line_count(content) if sealed else None,
        }
        result_path = (directory or self.logs) / f"{name}.json"
        result_path.parent.mkdir(parents=True, exist_ok=True)
        raw = {
            "schema": "validation-supervision/v1",
            "status": raw_status,
            "child_exit_code": child_exit_code,
            "argv": argv,
            "argv_sha256": self.canonical_digest(argv),
            "effective_argv_sha256": self.canonical_digest(effective),
            "cwd_ref": ".",
            "timeout_seconds": 10.0,
            "termination_grace_seconds": 1.0,
            "started_at": "1970-01-01T00:00:01.000Z",
            "finished_at": "1970-01-01T00:00:01.010Z",
            "duration_seconds": 0.01,
            "platform": {"family": "windows", "mechanism": "fixture-job"},
            "termination": termination,
            "log": raw_log,
            "error": None,
        }
        raw_path = Path(str(result_path) + ".process.json")
        raw_content = self.json_bytes(raw)
        raw_path.write_bytes(raw_content)
        status = wrapper_status or raw_status
        cleanup_state = (
            "failed" if raw_status == "cleanup-failed" or not tree_empty
            else "completed" if trigger is not None else "not-required"
        )
        receipt = {
            "schema_version": "validation-supervision-result/v1",
            "status": status,
            "command": {
                "argv": argv,
                "argv_digest": self.canonical_digest(argv),
                "effective_argv_digest": self.canonical_digest(effective),
                "cwd_ref": ".",
            },
            "timeout_seconds": 10.0,
            "accepted_child_exit_codes": accepted_child_exit_codes or [0],
            "termination_grace_seconds": 1.0,
            "timing": {"started_ms": 1000, "completed_ms": 1010, "duration_ms": 10},
            "exit_code": child_exit_code,
            "cleanup": {"state": cleanup_state, "tree_empty": tree_empty},
            "execution": {"launched": raw_status != "launch-failed"},
            "log": {
                "ref": log_path.relative_to(self.repo).as_posix(),
                "sha256": hashlib.sha256(content).hexdigest(),
                "bytes": len(content),
                "lines": self.line_count(content),
                "sealed": sealed,
            },
            "snapshot": {
                "identity_digest": snapshot_value["identity_digest"],
                "pre_verified": True,
                "post_verified": post_verified,
                "observed_identity_digest": (
                    snapshot_value["identity_digest"] if post_verified else "f" * 64
                ),
            },
            "supervisor_receipt": {
                "ref": raw_path.relative_to(self.repo).as_posix(),
                "sha256": hashlib.sha256(raw_content).hexdigest(),
                "bytes": len(raw_content),
                "schema": "validation-supervision/v1",
                "status": raw_status,
            },
            "supervisor": {
                "status": raw_status,
                "platform": raw["platform"],
                "termination": termination,
                "error": None,
            },
        }
        if bootstrap_target_argv is not None:
            safe_python = (
                f"<absolute-path>/{Path(sys.executable).name}"
                if Path(sys.executable).is_absolute()
                else sys.executable
            )
            safe_target = [
                safe_python if value == sys.executable else value
                for value in bootstrap_target_argv
            ]
            sidecar = {
                "schema_version": "validation-supervision-bootstrap/v1",
                "profile": bootstrap_profile,
                "status": "completed",
                "reason_code": None,
                "snapshot_ref": snapshot.relative_to(self.repo).as_posix(),
                "snapshot_identity_digest": snapshot_value["identity_digest"],
                "snapshot_clean": snapshot_value["identity"]["clean"],
                "post_verified": True,
                "target_argv": safe_target,
                "target_argv_digest": self.canonical_digest(safe_target),
                "target_effective_argv_digest": self.canonical_digest(bootstrap_target_argv),
                "target_cwd_ref": ".",
                "target_launched": True,
                "target_exit_code": 0,
            }
            sidecar_path = Path(str(result_path) + ".bootstrap.json")
            sidecar_content = self.json_bytes(sidecar)
            sidecar_path.write_bytes(sidecar_content)
            receipt["bootstrap"] = {
                **sidecar,
                "sidecar": {
                    "ref": sidecar_path.relative_to(self.repo).as_posix(),
                    "sha256": hashlib.sha256(sidecar_content).hexdigest(),
                    "bytes": len(sidecar_content),
                },
            }
        result_path.write_bytes(self.json_bytes(receipt))
        return result_path

    def seed_cache_source(
        self,
        snapshot: Path,
        *,
        validator_id: str,
        version: str,
        profile: str,
        fingerprint: str,
    ) -> None:
        source_dir = self.repo / f"artifacts/validation/cache-source-{validator_id}"
        source_dir.mkdir(parents=True, exist_ok=True)
        source_log = source_dir / "source.log"
        source_log.write_text(f"sealed source for {validator_id}\n", encoding="utf-8")
        receipt = self.write_receipt(
            snapshot,
            log_path=source_log,
            name="source-result",
            directory=source_dir,
        )
        source_evidence = source_dir / "evidence.jsonl"
        recorded = self.record_current(
            fingerprint,
            validator_id=validator_id,
            version=version,
            profile=profile,
            result_path=receipt,
            snapshot=snapshot,
            log_path=source_log,
            evidence=source_evidence,
        )
        self.assertEqual(0, recorded.returncode, recorded.stderr)
        source_record = json.loads(source_evidence.read_text(encoding="utf-8"))

        def artifact(path: Path) -> dict[str, object]:
            content = path.read_bytes()
            return {
                "ref": path.relative_to(self.repo).as_posix(),
                "sha256": hashlib.sha256(content).hexdigest(),
                "bytes": len(content),
            }

        raw_receipt = Path(str(receipt) + ".process.json")
        control_plane: list[dict[str, object]] = []
        control_artifact_paths: list[Path] = []
        for role in sorted((
            "bootstrap-snapshot", "prepare", "post-snapshot", "finalize",
            "summarize", "workflow-summary",
        )):
            control_log = source_dir / f"control-{role}.log"
            control_log.write_bytes(b"")
            control_result = self.write_receipt(
                snapshot,
                log_path=control_log,
                name=f"control-{role}",
                directory=source_dir,
                safe_argv=["python", role],
                effective_argv=["python", role],
                accepted_child_exit_codes=[0],
                bootstrap_target_argv=["python", "bootstrap-target"]
                if role == "bootstrap-snapshot" else None,
                bootstrap_profile=profile,
            )
            control_raw = Path(str(control_result) + ".process.json")
            control_receipt = json.loads(control_result.read_text(encoding="utf-8"))
            control_plane.append({
                "role": role,
                "result": {
                    **artifact(control_result),
                    "status": "completed",
                    "exit_code": 0,
                },
                "log": artifact(control_log),
                "raw_supervisor_receipt": artifact(control_raw),
                "command": control_receipt["command"],
                "timing": control_receipt["timing"],
            })
            control_artifact_paths.extend((control_result, control_log, control_raw))
            if role == "bootstrap-snapshot":
                control_artifact_paths.append(Path(str(control_result) + ".bootstrap.json"))
        artifact_values = sorted(
            [
                artifact(snapshot),
                artifact(source_evidence),
                artifact(source_log),
                artifact(receipt),
                artifact(raw_receipt),
                *(artifact(path) for path in control_artifact_paths),
            ],
            key=lambda item: str(item["ref"]).encode("utf-8"),
        )
        snapshot_value = json.loads(snapshot.read_text(encoding="utf-8"))
        core = {
            "schema_version": "validation-invocation/v1",
            "invocation_id": INVOCATION_ID,
            "profile": profile,
            "outcome": "passed",
            "sealed_at": "1970-01-01T00:00:02Z",
            "repository": {
                "pre_identity_digest": snapshot_value["identity_digest"],
                "post_identity_digest": snapshot_value["identity_digest"],
                "verified_identity_digest": snapshot_value["identity_digest"],
                "commit": snapshot_value["identity"]["commit"],
                "tree": snapshot_value["identity"]["tree"],
                "clean": snapshot_value["identity"]["clean"],
            },
            "cardinality": {"events": 1, "evidence_records": 1},
            "control_plane": control_plane,
            "terminal_supervision": {"mode": "direct"},
            "artifacts": artifact_values,
        }
        manifest = {**core, "manifest_digest": self.canonical_digest(core)}
        source_manifest = source_dir / "sealed-manifest.json"
        source_manifest.write_bytes(self.json_bytes(manifest))
        manifest_artifact = artifact(source_manifest)
        evidence_artifact = artifact(source_evidence)
        evidence_artifact["record_sha256"] = self.canonical_digest(source_record)
        reuse_source = {
            "kind": "cache",
            "source_manifest": manifest_artifact,
            "source_evidence": evidence_artifact,
            "source_snapshot": artifact(snapshot),
            "source_log": artifact(source_log),
        }
        cache_value = (
            json.loads(self.cache.read_text(encoding="utf-8"))
            if self.cache.is_file()
            else {"schema_version": "1.0.0", "entries": {}}
        )
        key = f"{validator_id}|{version}|{profile}|{fingerprint}|windows-native"
        cache_value["entries"][key] = {
            "eligible": True,
            "outcome": "passed",
            "log_ref": source_log.relative_to(self.repo).as_posix(),
            "reuse_source": reuse_source,
        }
        self.cache.parent.mkdir(parents=True, exist_ok=True)
        self.cache.write_bytes(self.json_bytes(cache_value))

    def write_immutable_preparation(
        self,
        snapshot: Path,
        *,
        profile: str,
        reusable_ids: list[str],
        routine_reusable: bool = True,
        name: str = "immutable-preparation",
    ) -> tuple[Path, str]:
        source_revision = "1" * 40
        source_tree = "2" * 40
        receipt_commit = "3" * 40
        if routine_reusable:
            fields = [
                "routine-reusable",
                "receipt-valid",
                source_revision,
                source_tree,
                receipt_commit,
                ",".join(reusable_ids),
            ]
            child_exit_code = 0
        else:
            fields = ["full-required", "receipt-missing", "", "", "", ""]
            child_exit_code = 10
        preparation_log = self.logs / f"{name}.log"
        preparation_log.write_text("\t".join(fields) + "\n", encoding="utf-8")
        effective_argv = [
            sys.executable,
            ".ai/scripts/validate-immutable-history.py",
            "verify",
            "--repo",
            ".",
            "--profile",
            profile,
            "--output-format",
            "tsv",
        ]
        safe_python = (
            f"<absolute-path>/{Path(sys.executable).name}"
            if Path(sys.executable).is_absolute()
            else sys.executable
        )
        result = self.write_receipt(
            snapshot,
            log_path=preparation_log,
            name=name,
            child_exit_code=child_exit_code,
            accepted_child_exit_codes=[0, 10],
            safe_argv=[safe_python, *effective_argv[1:]],
            effective_argv=effective_argv,
        )
        fingerprint = hashlib.sha256(
            f"{source_revision}\n{source_tree}\n{receipt_commit}\n".encode("utf-8")
        ).hexdigest()
        return result, fingerprint

    def control_argv(
        self,
        role: str,
        paths: dict[str, Path],
        *,
        profile: str,
        preparation_python: str | None,
        bootstrap_result: Path | None = None,
    ) -> list[str]:
        prefix = [sys.executable, ".ai/scripts/validation-evidence.py"]
        reference = lambda path: path.relative_to(self.repo).as_posix()
        if role == "bootstrap-snapshot":
            result_path = bootstrap_result or self.logs / "control-bootstrap-snapshot.json"
            target = [
                *prefix, "verify-snapshot", "--repo", ".",
                "--snapshot", reference(paths["snapshot"]),
            ]
            argv = [
                *prefix, "bootstrap-run", "--repo", ".",
                "--snapshot-output", reference(paths["snapshot"]),
                "--profile", profile,
                "--sidecar-output", f"{reference(result_path)}.bootstrap.json",
                "--cwd-ref", ".",
            ]
            if profile in {"release", "nightly-full"}:
                argv.append("--require-clean")
            return [*argv, "--", *target]
        if role == "prepare":
            return [
                *prefix, "prepare", "--repo", ".", "--cache", reference(self.cache),
                "--profile", profile, "--environment-class", "windows-native",
                "--selection", reference(paths["preparation_selection"]),
            ]
        if role == "post-snapshot":
            return [
                *prefix, "verify-snapshot", "--repo", ".",
                "--snapshot", reference(paths["snapshot"]),
                "--output", reference(paths["post"]),
            ]
        if role == "finalize":
            argv = [
                *prefix, "finalize", "--repo", ".", "--cache", reference(self.cache),
                "--evidence", reference(paths["evidence"]),
                "--events", reference(paths["events"]),
                "--invocation-id", INVOCATION_ID, "--profile", profile,
                "--environment-class", "windows-native",
                "--snapshot", reference(paths["snapshot"]),
            ]
            if preparation_python:
                argv.extend(("--preparation-python", preparation_python))
            return argv
        if role == "summarize":
            return [
                *prefix, "summarize", "--evidence", reference(paths["evidence"]),
                "--output", reference(paths["summary"]),
                "--invocation-id", INVOCATION_ID, "--profile", profile,
            ]
        if role == "workflow-summary":
            return [
                *prefix, "workflow-summary",
                "--evidence", reference(paths["evidence"]),
                "--output", reference(paths["workflow_summary"]),
                "--invocation-id", INVOCATION_ID, "--profile", profile,
                "--wall-span-ms", "1000",
            ]
        raise AssertionError(f"unknown fixture control role: {role}")

    def write_control_results(
        self,
        paths: dict[str, Path],
        *,
        profile: str,
        preparation_python: str | None,
    ) -> dict[str, Path]:
        results: dict[str, Path] = {}
        safe_python = (
            f"<absolute-path>/{Path(sys.executable).name}"
            if Path(sys.executable).is_absolute()
            else sys.executable
        )
        for role in (
            "bootstrap-snapshot", "prepare", "post-snapshot", "finalize",
            "summarize", "workflow-summary",
        ):
            control_result_path = self.logs / f"control-{role}.json"
            effective_argv = self.control_argv(
                role,
                paths,
                profile=profile,
                preparation_python=preparation_python,
                bootstrap_result=control_result_path if role == "bootstrap-snapshot" else None,
            )
            log_path = self.logs / f"control-{role}.log"
            if role == "prepare":
                prepared = self.helper(
                    "prepare", "--repo", str(self.repo), "--cache", str(self.cache),
                    "--profile", profile, "--environment-class", "windows-native",
                    "--selection", str(paths["preparation_selection"]),
                )
                self.assertEqual(0, prepared.returncode, prepared.stderr)
                log_path.write_text(prepared.stdout, encoding="utf-8")
            else:
                log_path.write_bytes(b"")
            results[role] = self.write_receipt(
                paths["snapshot"],
                log_path=log_path,
                name=f"control-{role}",
                safe_argv=[
                    safe_python if value == sys.executable else value
                    for value in effective_argv
                ],
                effective_argv=effective_argv,
                accepted_child_exit_codes=[0],
                bootstrap_target_argv=(
                    effective_argv[effective_argv.index("--") + 1 :]
                    if role == "bootstrap-snapshot" else None
                ),
                bootstrap_profile=profile,
            )
        return results

    def prepare_invocation(
        self,
        specs: list[dict[str, Any]] | None = None,
        *,
        profile: str = "release",
        snapshot: Path | None = None,
        preparation_python: str | None = None,
    ) -> dict[str, Path]:
        self.initialize_git()
        snapshot = snapshot or self.capture_snapshot(
            profile=profile, name=f"{profile}-snapshot-pre.json"
        )
        specs = specs or [{
            "id": "fixture-check", "outcome": "passed",
            "disposition": "executed", "enforcement": "required",
        }]
        changed_paths_content = b"inputs/rule.md\n"
        changed_paths_digest = hashlib.sha256(changed_paths_content).hexdigest()
        events: list[str] = []
        selected: list[str] = []
        contracts: list[str] = []
        preparation_contracts: list[str] = []
        preparation_results: list[Path] = []
        for index, spec in enumerate(specs):
            validator_id = spec["id"]
            version = spec.get("version", "validator-v1")
            if "fingerprint" in spec:
                fingerprint = str(spec["fingerprint"])
                reusable = False
            else:
                fingerprint, reusable = self.lookup(
                    validator_id=validator_id, version=version, profile=profile
                )
            log_path = spec.get("log_path", self.logs / f"{validator_id}.log")
            if "log_path" not in spec:
                content = spec.get("content", f"retained {validator_id}\n".encode())
                log_path.write_bytes(content.encode() if isinstance(content, str) else content)
            disposition = spec["disposition"]
            outcome = spec["outcome"]
            cache_hit = spec.get("cache_hit", disposition == "reused")
            if disposition == "reused" and cache_hit and not reusable:
                self.seed_cache_source(
                    snapshot,
                    validator_id=validator_id,
                    version=version,
                    profile=profile,
                    fingerprint=fingerprint,
                )
                same_fingerprint, reusable = self.lookup(
                    validator_id=validator_id, version=version, profile=profile
                )
                self.assertEqual(fingerprint, same_fingerprint)
                self.assertTrue(reusable)
            result_path: Path | None = spec.get("result_path")
            if disposition == "reused" and not cache_hit and result_path is not None:
                preparation_results.append(result_path)
            if result_path is None and disposition in {"executed", "timed-out", "cancelled"}:
                raw_status = spec.get("raw_status", {
                    "executed": "completed", "timed-out": "timed-out",
                    "cancelled": "cancelled",
                }[disposition])
                child_exit = spec.get(
                    "exit_code", 0 if outcome == "passed" and raw_status == "completed" else 1
                )
                if raw_status in {"timed-out", "cancelled"}:
                    child_exit = None
                result_path = self.write_receipt(
                    snapshot, log_path=log_path, name=f"{validator_id}-result",
                    raw_status=raw_status, child_exit_code=child_exit,
                )
            elif disposition == "snapshot-drift" and spec.get("post_launch"):
                result_path = self.write_receipt(
                    snapshot, log_path=log_path, name=f"{validator_id}-result",
                    raw_status="completed", child_exit_code=0,
                    wrapper_status="snapshot-drift", post_verified=False,
                )
            reason = spec.get("selection_reason", f"selected-{validator_id}")
            if disposition != "not-selected":
                selected.append(f"{validator_id}\t{reason}")
            if spec.get("fingerprint_contract", True):
                contracts.append(f"{validator_id}\t{version}\tinputs\treuse-by-input")
            preparation_contracts.append(
                f"{validator_id}\t{version}\tinputs\treuse-by-input"
            )
            fields = [
                validator_id, version, fingerprint, outcome, disposition,
                str(1000 + index * 100), str(1010 + index * 100),
                "true" if cache_hit else "false",
                log_path.name, "-1", reason, changed_paths_digest,
                result_path.name if result_path else "",
                spec.get("enforcement", "required"),
            ]
            events.append("\t".join(fields))
        paths = {
            "snapshot": snapshot,
            "post": self.logs / f"{profile}-snapshot-post.json",
            "events": self.logs / "events.tsv",
            "evidence": self.evidence,
            "summary": self.logs / "summary.json",
            "workflow_summary": self.logs / "workflow-summary.json",
            "selection": self.logs / "selected-checks.tsv",
            "selection_comparison": self.logs / "selection-comparison.tsv",
            "fingerprint_selection": self.logs / "fingerprint-selection.tsv",
            "preparation_selection": self.logs / "evidence-preparation-selection.tsv",
            "changed_paths": self.logs / "changed-paths.txt",
        }
        paths["preparation_results"] = preparation_results  # type: ignore[assignment]
        paths["preparation_python"] = preparation_python  # type: ignore[assignment]
        paths["events"].write_text("\n".join(events) + "\n", encoding="utf-8")
        paths["selection"].write_text(
            "\n".join(selected) + ("\n" if selected else ""), encoding="utf-8"
        )
        paths["fingerprint_selection"].write_text(
            "\n".join(contracts) + "\n", encoding="utf-8"
        )
        paths["preparation_selection"].write_text(
            "\n".join(preparation_contracts) + "\n", encoding="utf-8"
        )
        paths["changed_paths"].write_bytes(changed_paths_content)
        snapshot_value = json.loads(snapshot.read_text(encoding="utf-8"))
        snapshot_commit = snapshot_value["identity"]["commit"]
        paths["selection_comparison"].write_text(
            "\t".join((
                "validation-selection-comparison/v1",
                "changed-path",
                snapshot_commit,
                snapshot_commit,
                changed_paths_digest,
                "",
            )) + "\n",
            encoding="utf-8",
        )
        finalize_arguments = [
            "finalize", "--repo", str(self.repo), "--cache", str(self.cache),
            "--evidence", str(paths["evidence"]), "--events", str(paths["events"]),
            "--invocation-id", INVOCATION_ID, "--profile", profile,
            "--environment-class", "windows-native", "--snapshot", str(snapshot),
        ]
        if preparation_python:
            finalize_arguments.extend(("--preparation-python", preparation_python))
        finalized = self.helper(*finalize_arguments)
        self.assertEqual(0, finalized.returncode, finalized.stderr)
        self.write_summaries(paths, profile=profile)
        verified = self.helper(
            "verify-snapshot", "--repo", str(self.repo), "--snapshot", str(snapshot),
            "--output", str(paths["post"]),
        )
        self.assertEqual(0, verified.returncode, verified.stderr)
        paths["control_python"] = sys.executable  # type: ignore[assignment]
        paths["control_results"] = self.write_control_results(  # type: ignore[assignment]
            paths,
            profile=profile,
            preparation_python=preparation_python,
        )
        return paths

    def write_summaries(self, paths: dict[str, Path], *, profile: str) -> None:
        summarized = self.helper(
            "summarize", "--evidence", str(paths["evidence"]),
            "--output", str(paths["summary"]), "--invocation-id", INVOCATION_ID,
            "--profile", profile,
        )
        self.assertEqual(0, summarized.returncode, summarized.stderr)
        workflow = self.helper(
            "workflow-summary", "--evidence", str(paths["evidence"]),
            "--output", str(paths["workflow_summary"]),
            "--invocation-id", INVOCATION_ID, "--profile", profile,
            "--wall-span-ms", "1000",
        )
        self.assertEqual(0, workflow.returncode, workflow.stderr)

    def seal_prepared(
        self,
        paths: dict[str, Path],
        *,
        outcome: str = "passed",
        output_name: str = "sealed-manifest.json",
        publication_name: str | None = None,
    ) -> tuple[subprocess.CompletedProcess[str], Path]:
        output = self.logs / output_name
        publication_output = self.logs / publication_name if publication_name else None
        result = self.helper(*self.seal_arguments(
            paths,
            outcome=outcome,
            output=output,
            publication_output=publication_output,
        ))
        return result, output

    def seal_arguments(
        self,
        paths: dict[str, Path],
        *,
        outcome: str,
        output: Path,
        publication_output: Path | None = None,
        terminal_result: Path | None = None,
        terminal_log: Path | None = None,
    ) -> list[str]:
        return [
            "seal-invocation", "--repo", str(self.repo),
            "--snapshot", str(paths["snapshot"]), "--post-snapshot", str(paths["post"]),
            "--evidence", str(paths["evidence"]), "--summary", str(paths["summary"]),
            "--workflow-summary", str(paths["workflow_summary"]),
            "--selection", str(paths["selection"]),
            "--selection-comparison", str(paths["selection_comparison"]),
            "--fingerprint-selection", str(paths["fingerprint_selection"]),
            "--preparation-selection", str(paths["preparation_selection"]),
            "--events", str(paths["events"]), "--changed-paths", str(paths["changed_paths"]),
            "--output", str(output), "--cache", str(self.cache),
            *(
                ["--publication-output", str(publication_output)]
                if publication_output is not None
                else []
            ),
            "--invocation-id", INVOCATION_ID, "--outcome", outcome,
            "--control-python", str(paths.get("control_python", sys.executable)),
            *sum(
                (
                    ["--control-result", role, str(result_path)]
                    for role, result_path in sorted(
                        paths.get("control_results", {}).items()  # type: ignore[union-attr]
                    )
                ),
                [],
            ),
            *(
                [
                    "--terminal-result", str(terminal_result),
                    "--terminal-log", str(terminal_log),
                ]
                if terminal_result is not None and terminal_log is not None
                else []
            ),
            *(
                ["--preparation-python", str(paths["preparation_python"])]
                if paths.get("preparation_python")
                else []
            ),
            *sum(
                (
                    ["--preparation-result", str(item)]
                    for item in paths.get("preparation_results", [])
                ),
                [],
            ),
        ]

class ValidationEvidenceCoreGwtTests(ValidationEvidenceFixture):
    """Original five evidence contracts retained as focused compatibility coverage."""

    def test_gwt_001_given_executed_evidence_when_finalized_and_then_sealed_then_only_the_seal_promotes_reuse(self) -> None:
        paths = self.prepare_invocation(profile="fast")
        fingerprint, reusable = self.lookup(profile="fast")
        self.assertFalse(reusable, "finalize must not promote an unsealed invocation")
        sealed, _ = self.seal_prepared(paths)
        self.assertEqual(0, sealed.returncode, sealed.stderr)
        same_fingerprint, reusable = self.lookup(profile="fast")
        self.assertEqual(fingerprint, same_fingerprint)
        self.assertTrue(reusable)
        record = json.loads(self.evidence.read_text(encoding="utf-8"))
        self.assertEqual(("passed", "executed"), (
            record["outcome"], record["execution_disposition"]
        ))

    def test_gwt_002_given_changed_input_or_incompatible_identity_when_checked_then_reuse_is_invalidated(self) -> None:
        paths = self.prepare_invocation(profile="fast")
        sealed, _ = self.seal_prepared(paths)
        self.assertEqual(0, sealed.returncode, sealed.stderr)
        fingerprint, reusable = self.lookup(profile="fast")
        self.assertTrue(reusable)
        (self.inputs / "rule.md").write_text("changed bytes\n", encoding="utf-8")
        changed, changed_reusable = self.lookup(profile="fast")
        _, version_reusable = self.lookup(version="validator-v2", profile="fast")
        _, profile_reusable = self.lookup(profile="pr")
        _, environment_reusable = self.lookup(
            profile="fast", environment="ubuntu-hosted"
        )
        self.assertNotEqual(fingerprint, changed)
        self.assertFalse(changed_reusable)
        self.assertFalse(version_reusable)
        self.assertFalse(profile_reusable)
        self.assertFalse(environment_reusable)

    def test_gwt_003_given_retained_output_when_recorded_then_evidence_contains_counts_not_output_or_host_identity(self) -> None:
        paths = self.prepare_invocation(profile="fast")
        serialized = paths["evidence"].read_text(encoding="utf-8")
        record = json.loads(serialized)
        self.assertNotIn("private-token", serialized)
        self.assertNotIn(str(self.temporary.name), serialized)
        self.assertEqual(
            "artifacts/validation/run/fixture-check.log", record["log_ref"]
        )
        fixture_log = self.logs / "fixture-check.log"
        self.assertEqual(len(fixture_log.read_bytes()), record["output_bytes"])
        self.assertEqual(1, record["output_lines"])

    def test_gwt_004_given_profile_selection_dispositions_when_serialized_then_timeout_cancellation_and_nonselection_remain_distinct(self) -> None:
        specs = [
            {"id": "executed", "outcome": "passed", "disposition": "executed"},
            {"id": "reused", "outcome": "passed", "disposition": "reused"},
            {"id": "not-selected", "outcome": "not-applicable", "disposition": "not-selected"},
            {"id": "timed-out", "outcome": "failed", "disposition": "timed-out"},
            {"id": "cancelled", "outcome": "failed", "disposition": "cancelled"},
        ]
        paths = self.prepare_invocation(specs, profile="fast")
        records = [
            json.loads(line)
            for line in paths["evidence"].read_text(encoding="utf-8").splitlines()
        ]
        summary = json.loads(paths["summary"].read_text(encoding="utf-8"))
        self.assertEqual(
            {(spec["disposition"], spec["outcome"]) for spec in specs},
            {(record["execution_disposition"], record["outcome"]) for record in records},
        )
        self.assertEqual(1, summary["dispositions"]["timed-out"])
        self.assertEqual(1, summary["dispositions"]["cancelled"])
        self.assertEqual(1, summary["dispositions"]["not-selected"])

    def test_gwt_005_given_tracked_input_when_unmodified_then_git_content_identity_is_stable_but_dirty_content_invalidates_it(self) -> None:
        self.initialize_git()
        fingerprint, reusable = self.lookup()
        same_fingerprint, same_reusable = self.lookup()
        (self.inputs / "rule.md").write_text("dirty content\n", encoding="utf-8")
        dirty_fingerprint, dirty_reusable = self.lookup()
        self.assertFalse(reusable)
        self.assertEqual(fingerprint, same_fingerprint)
        self.assertFalse(same_reusable)
        self.assertNotEqual(fingerprint, dirty_fingerprint)
        self.assertFalse(dirty_reusable)

class ValidationEvidenceReadinessGwtTests(ValidationEvidenceFixture):
    """Exhaustive durability, recovery, and tamper coverage for external readiness."""

    def test_gwt_006_given_clean_dirty_or_uncapturable_repository_when_snapshotted_then_admission_artifact_is_durable_and_private(self) -> None:
        self.initialize_git()
        clean = self.capture_snapshot()
        clean_value = json.loads(clean.read_text(encoding="utf-8"))
        self.assertTrue(clean_value["identity"]["clean"])
        self.assertNotIn(str(self.temporary.name), clean.read_text(encoding="utf-8"))
        (self.inputs / "rule.md").write_text("dirty bytes\n", encoding="utf-8")
        dirty = self.logs / "dirty-rejected.json"
        rejected = self.helper(
            "snapshot", "--repo", str(self.repo), "--output", str(dirty),
            "--profile", "release", "--require-clean",
        )
        self.assertNotEqual(0, rejected.returncode)
        self.assertFalse(
            json.loads(dirty.read_text(encoding="utf-8"))["identity"]["clean"]
        )
        non_repo = Path(self.temporary.name) / "not-a-repo"
        non_repo.mkdir()
        failure = non_repo / "admission.json"
        failed = self.helper(
            "snapshot", "--repo", str(non_repo), "--output", str(failure),
            "--profile", "release", "--require-clean",
        )
        self.assertNotEqual(0, failed.returncode)
        failure_text = failure.read_text(encoding="utf-8")
        self.assertNotIn(str(self.temporary.name), failure_text)
        self.assertEqual(
            "validation-repository-admission-failure/v1",
            json.loads(failure_text)["schema_version"],
        )

    def test_gwt_007_given_snapshot_when_head_status_content_or_operation_changes_then_verification_fails_closed(self) -> None:
        self.initialize_git()
        clean = self.capture_snapshot()
        head = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=self.repo, check=True,
            capture_output=True, text=True, timeout=30,
        ).stdout.strip()
        (self.repo / ".git" / "MERGE_HEAD").write_text(head + "\n", encoding="ascii")
        self.assertNotEqual(0, self.helper(
            "verify-snapshot", "--repo", str(self.repo), "--snapshot", str(clean)
        ).returncode)
        (self.repo / ".git" / "MERGE_HEAD").unlink()
        (self.inputs / "rule.md").write_text("dirty-one\n", encoding="utf-8")
        dirty = self.capture_snapshot(require_clean=False, name="dirty.json")
        (self.inputs / "rule.md").write_text("dirty-two\n", encoding="utf-8")
        self.assertNotEqual(0, self.helper(
            "verify-snapshot", "--repo", str(self.repo), "--snapshot", str(dirty)
        ).returncode)
        self.git("add", "inputs/rule.md")
        self.git("commit", "-m", "head drift")
        self.assertNotEqual(0, self.helper(
            "verify-snapshot", "--repo", str(self.repo), "--snapshot", str(clean)
        ).returncode)

    def test_gwt_008_given_ignored_validation_artifacts_when_their_bytes_change_then_snapshot_identity_is_stable(self) -> None:
        self.initialize_git()
        snapshot = self.capture_snapshot()
        self.log.write_text("new ignored output\n", encoding="utf-8")
        post = self.logs / "snapshot-post.json"
        result = self.helper(
            "verify-snapshot", "--repo", str(self.repo), "--snapshot", str(snapshot),
            "--output", str(post),
        )
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertEqual(
            json.loads(snapshot.read_text(encoding="utf-8"))["identity_digest"],
            json.loads(post.read_text(encoding="utf-8"))["identity_digest"],
        )

    def test_gwt_009_given_supervisor_receipt_when_recorded_then_full_execution_and_snapshot_are_bound(self) -> None:
        self.initialize_git()
        snapshot = self.capture_snapshot(profile="fast")
        receipt = self.write_receipt(snapshot)
        fingerprint, _ = self.lookup()
        result = self.record_current(
            fingerprint, result_path=receipt, snapshot=snapshot
        )
        self.assertEqual(0, result.returncode, result.stderr)
        record = json.loads(self.evidence.read_text(encoding="utf-8"))
        self.assertEqual(
            hashlib.sha256(self.log.read_bytes()).hexdigest(), record["log_sha256"]
        )
        self.assertEqual("completed", record["execution"]["status"])
        self.assertEqual(
            ["python", "-c", "pass"], record["execution"]["command"]["argv"]
        )
        self.assertTrue(record["execution"]["snapshot"]["post_verified"])
        self.assertNotIn(str(self.temporary.name), json.dumps(record))

    def test_gwt_010_given_missing_receipt_or_tampered_log_when_recorded_then_executed_evidence_is_rejected(self) -> None:
        self.initialize_git()
        snapshot = self.capture_snapshot(profile="fast")
        fingerprint, _ = self.lookup()
        missing = self.record_current(
            fingerprint, result_path=self.logs / "missing.json", snapshot=snapshot
        )
        self.assertNotEqual(0, missing.returncode)
        receipt = self.write_receipt(snapshot)
        self.log.write_text("tampered after receipt\n", encoding="utf-8")
        tampered = self.record_current(
            fingerprint, result_path=receipt, snapshot=snapshot
        )
        self.assertNotEqual(0, tampered.returncode)
        self.assertFalse(self.evidence.exists())

    def test_gwt_011_given_complete_retained_artifacts_when_sealed_then_cardinality_and_canonical_digests_are_persisted(self) -> None:
        paths = self.prepare_invocation([{
            "id": "fixture-check", "outcome": "passed", "disposition": "executed"
        }], profile="fast")
        result, seal = self.seal_prepared(paths)
        self.assertEqual(0, result.returncode, result.stderr)
        manifest = json.loads(seal.read_text(encoding="utf-8"))
        refs = [artifact["ref"] for artifact in manifest["artifacts"]]
        self.assertEqual(sorted(refs, key=lambda item: item.encode("utf-8")), refs)
        self.assertEqual({"events": 1, "evidence_records": 1}, manifest["cardinality"])
        evidence_artifact = next(
            item
            for item in manifest["artifacts"]
            if item["ref"] == self.evidence.relative_to(self.repo).as_posix()
        )
        self.assertEqual(
            hashlib.sha256(self.evidence.read_bytes()).hexdigest(),
            evidence_artifact["sha256"],
        )

    def test_gwt_012_given_cardinality_mismatch_or_post_snapshot_drift_when_sealed_then_no_passing_manifest_is_created(self) -> None:
        paths = self.prepare_invocation([{
            "id": "fixture-check", "outcome": "passed", "disposition": "executed"
        }], profile="fast")
        comparison_fields = paths["selection_comparison"].read_text(
            encoding="utf-8"
        ).rstrip("\n").split("\t")
        forged_head = list(comparison_fields)
        forged_head[3] = "f" * 40
        paths["selection_comparison"].write_text(
            "\t".join(forged_head) + "\n", encoding="utf-8"
        )
        rejected, rejected_output = self.seal_prepared(
            paths, output_name="forged-selection-head.json"
        )
        self.assertNotEqual(0, rejected.returncode)
        self.assertFalse(rejected_output.exists())
        forged_digest = list(comparison_fields)
        forged_digest[4] = "0" * 64
        paths["selection_comparison"].write_text(
            "\t".join(forged_digest) + "\n", encoding="utf-8"
        )
        rejected, rejected_output = self.seal_prepared(
            paths, output_name="forged-selection-digest.json"
        )
        self.assertNotEqual(0, rejected.returncode)
        self.assertFalse(rejected_output.exists())
        paths["selection_comparison"].write_text(
            "\t".join(comparison_fields) + "\n", encoding="utf-8"
        )
        original_events = paths["events"].read_text(encoding="utf-8")
        paths["events"].write_text("", encoding="utf-8")
        mismatch, mismatch_seal = self.seal_prepared(
            paths, output_name="mismatch.json"
        )
        self.assertNotEqual(0, mismatch.returncode)
        self.assertFalse(mismatch_seal.exists())
        paths["events"].write_text(original_events, encoding="utf-8")
        (self.inputs / "rule.md").write_text("post drift\n", encoding="utf-8")
        drift, drift_seal = self.seal_prepared(paths, output_name="drift.json")
        self.assertNotEqual(0, drift.returncode)
        self.assertFalse(drift_seal.exists())

    def test_gwt_013_given_terminal_cache_is_preseeded_when_prepare_finalize_and_seal_run_then_cache_is_neither_read_nor_written(self) -> None:
        self.initialize_git()
        fingerprint, _ = self.lookup(profile="release")
        original = b"{malformed terminal cache that must not be read\n"
        self.cache.write_bytes(original)
        self.assertFalse(self.lookup(profile="release")[1])
        selection = self.logs / "terminal-selection.tsv"
        selection.write_text(
            "fixture-check\tvalidator-v1\tinputs\treuse-by-input\n", encoding="utf-8"
        )
        prepared = self.helper(
            "prepare", "--repo", str(self.repo), "--cache", str(self.cache),
            "--profile", "release", "--environment-class", "windows-native",
            "--selection", str(selection),
        )
        self.assertEqual(0, prepared.returncode, prepared.stderr)
        self.assertIn("\tfalse\t", prepared.stdout)
        paths = self.prepare_invocation(profile="release")
        sealed, _ = self.seal_prepared(paths)
        self.assertEqual(0, sealed.returncode, sealed.stderr)
        self.assertEqual(original, self.cache.read_bytes())

    def test_gwt_014_given_pre_execution_snapshot_drift_when_supervision_is_requested_then_command_is_not_launched(self) -> None:
        self.initialize_git()
        snapshot = self.capture_snapshot()
        (self.inputs / "rule.md").write_text("drift before launch\n", encoding="utf-8")
        marker = self.logs / "should-not-exist.txt"
        result, log, result_path = self.supervise(
            snapshot,
            Path(sys.executable).name,
            "-c",
            "from pathlib import Path; Path('artifacts/validation/run/should-not-exist.txt').write_text('launched')",
        )
        self.assertEqual(128, result.returncode, result.stderr)
        self.assertFalse(marker.exists())
        receipt = json.loads(result_path.read_text(encoding="utf-8"))
        self.assertEqual({"launched": False}, receipt["execution"])
        self.assertFalse(receipt["snapshot"]["pre_verified"])
        self.assertEqual(
            receipt["log"]["sha256"], hashlib.sha256(log.read_bytes()).hexdigest()
        )
        self.assertFalse(Path(str(result_path) + ".process.json").exists())
        fingerprint, _ = self.lookup(profile="release")
        recorded = self.record_current(
            fingerprint,
            outcome="failed",
            disposition="snapshot-drift",
            result_path=result_path,
            snapshot=snapshot,
            profile="release",
            log_path=log,
        )
        self.assertEqual(0, recorded.returncode, recorded.stderr)
        record = json.loads(self.evidence.read_text(encoding="utf-8"))
        self.assertEqual(False, record["execution"]["launched"])
        launch_log = self.logs / "launch-failed.log"
        launch_log.write_text("launch failed\n", encoding="utf-8")
        launch_receipt = self.write_receipt(
            snapshot,
            log_path=launch_log,
            name="launch-failed",
            raw_status="launch-failed",
            child_exit_code=None,
        )
        launch_recorded = self.record_current(
            fingerprint,
            outcome="failed",
            disposition="not-executed",
            result_path=launch_receipt,
            snapshot=snapshot,
            profile="release",
            log_path=launch_log,
            evidence=self.logs / "launch-failed-evidence.jsonl",
        )
        self.assertEqual(0, launch_recorded.returncode, launch_recorded.stderr)
        (self.inputs / "rule.md").write_text("governed bytes\n", encoding="utf-8")
        module = self.load_helper_module("launch_failure")
        import_failure_log = self.logs / "import-failure.log"
        import_failure_result = self.logs / "import-failure-result.json"
        parsed = module.parser().parse_args([
            "supervise", "--repo", str(self.repo), "--snapshot", str(snapshot),
            "--log-path", str(import_failure_log),
            "--result-path", str(import_failure_result),
            "--timeout-seconds", "5", "--accepted-child-exit-code", "10",
            "--", Path(sys.executable).name, "-c", "pass",
        ])
        original_import = module.importlib.import_module

        def unavailable_supervisor(_name: str) -> None:
            raise ImportError("injected unavailable supervisor")

        module.importlib.import_module = unavailable_supervisor
        try:
            self.assertEqual(127, module.supervise(parsed))
        finally:
            module.importlib.import_module = original_import
        import_failure_receipt = json.loads(
            import_failure_result.read_text(encoding="utf-8")
        )
        self.assertEqual("launch-failed", import_failure_receipt["status"])
        self.assertEqual([0, 10], import_failure_receipt["accepted_child_exit_codes"])
        self.assertEqual({"launched": False}, import_failure_receipt["execution"])
        self.assertFalse(Path(str(import_failure_result) + ".process.json").exists())
        verified_import_failure = self.helper(
            "verify-supervision-result", "--repo", str(self.repo),
            "--snapshot", str(snapshot), "--result-path", str(import_failure_result),
        )
        self.assertEqual(0, verified_import_failure.returncode, verified_import_failure.stderr)
        self.assertEqual("launch-failed\tfalse\t", verified_import_failure.stdout.rstrip("\r\n"))

    def test_gwt_015_given_stable_snapshot_when_command_completes_then_adapter_preserves_raw_receipt_and_seals_wrapper(self) -> None:
        self.initialize_git()
        snapshot = self.capture_snapshot()
        result, log, result_path = self.supervise(
            snapshot, Path(sys.executable).name, "-c", "pass"
        )
        self.assertEqual(0, result.returncode, result.stderr)
        receipt = json.loads(result_path.read_text(encoding="utf-8"))
        raw_path = Path(str(result_path) + ".process.json")
        raw = json.loads(raw_path.read_text(encoding="utf-8"))
        self.assertEqual("completed", receipt["status"])
        self.assertEqual(raw["argv"], receipt["command"]["argv"])
        self.assertEqual(
            raw["effective_argv_sha256"], receipt["command"]["effective_argv_digest"]
        )
        self.assertEqual(
            hashlib.sha256(raw_path.read_bytes()).hexdigest(),
            receipt["supervisor_receipt"]["sha256"],
        )
        self.assertEqual(
            hashlib.sha256(log.read_bytes()).hexdigest(), receipt["log"]["sha256"]
        )
        self.assertEqual(b"", log.read_bytes())
        paths = self.prepare_invocation([{
            "id": "silent", "outcome": "passed", "disposition": "executed",
            "log_path": log, "result_path": result_path,
        }], snapshot=snapshot)
        sealed, _ = self.seal_prepared(paths, output_name="silent-command-seal.json")
        self.assertEqual(0, sealed.returncode, sealed.stderr)
        accepted, accepted_log, accepted_result = self.supervise(
            snapshot,
            Path(sys.executable).name,
            "-c",
            "raise SystemExit(10)",
            accepted_child_exit_codes=(10,),
        )
        self.assertEqual(0, accepted.returncode, accepted.stderr)
        accepted_receipt = json.loads(accepted_result.read_text(encoding="utf-8"))
        self.assertEqual([0, 10], accepted_receipt["accepted_child_exit_codes"])
        self.assertEqual(10, accepted_receipt["exit_code"])
        accepted_paths = self.prepare_invocation([{
            "id": "accepted-ten", "outcome": "passed", "disposition": "executed",
            "log_path": accepted_log, "result_path": accepted_result,
        }], snapshot=snapshot)
        accepted_sealed, _ = self.seal_prepared(
            accepted_paths, output_name="accepted-ten-seal.json"
        )
        self.assertEqual(0, accepted_sealed.returncode, accepted_sealed.stderr)
        unaccepted, _unaccepted_log, unaccepted_result = self.supervise(
            snapshot, Path(sys.executable).name, "-c", "raise SystemExit(1)"
        )
        self.assertEqual(1, unaccepted.returncode, unaccepted.stderr)
        unaccepted_receipt = json.loads(unaccepted_result.read_text(encoding="utf-8"))
        self.assertEqual(
            ("completed", 1, [0]),
            (
                unaccepted_receipt["status"],
                unaccepted_receipt["exit_code"],
                unaccepted_receipt["accepted_child_exit_codes"],
            ),
        )
        verified = self.helper(
            "verify-supervision-result",
            "--repo", str(self.repo),
            "--snapshot", str(snapshot),
            "--result-path", str(unaccepted_result),
        )
        self.assertEqual(0, verified.returncode, verified.stderr)
        self.assertEqual("completed\ttrue\t1", verified.stdout.strip())
        unaccepted_receipt["command"]["argv_digest"] = "0" * 64
        unaccepted_result.write_bytes(self.json_bytes(unaccepted_receipt))
        rejected = self.helper(
            "verify-supervision-result",
            "--repo", str(self.repo),
            "--snapshot", str(snapshot),
            "--result-path", str(unaccepted_result),
        )
        self.assertNotEqual(0, rejected.returncode)
        self.assertEqual("", rejected.stdout)

    def test_gwt_016_given_target_mutates_repository_when_command_exits_then_post_drift_overrides_completed_without_appending_log(self) -> None:
        self.initialize_git()
        snapshot = self.capture_snapshot()
        result, log, result_path = self.supervise(
            snapshot,
            Path(sys.executable).name,
            "-c",
            "from pathlib import Path; Path('inputs/rule.md').write_text('post drift\\n'); print('child-final-line')",
        )
        self.assertEqual(125, result.returncode, result.stderr)
        receipt = json.loads(result_path.read_text(encoding="utf-8"))
        raw = json.loads(
            Path(str(result_path) + ".process.json").read_text(encoding="utf-8")
        )
        self.assertEqual("completed", raw["status"])
        self.assertEqual("snapshot-drift", receipt["status"])
        self.assertEqual({"launched": True}, receipt["execution"])
        self.assertFalse(receipt["snapshot"]["post_verified"])
        self.assertEqual(
            raw["log"]["sha256"], hashlib.sha256(log.read_bytes()).hexdigest()
        )

    def test_gwt_017_given_bounded_command_exceeds_timeout_when_supervised_then_adapter_returns_timeout_contract(self) -> None:
        self.initialize_git()
        snapshot = self.capture_snapshot()
        result, _, result_path = self.supervise(
            snapshot,
            Path(sys.executable).name,
            "-c",
            "import time; time.sleep(5)",
            timeout_seconds=0.2,
        )
        self.assertEqual(124, result.returncode, result.stderr)
        receipt = json.loads(result_path.read_text(encoding="utf-8"))
        self.assertEqual("timed-out", receipt["status"])
        self.assertTrue(receipt["cleanup"]["tree_empty"])
        self.assertTrue(receipt["log"]["sealed"])

    def test_gwt_018_given_executed_evidence_when_sealed_then_wrapper_raw_receipt_and_log_are_required(self) -> None:
        paths = self.prepare_invocation()
        sealed, seal = self.seal_prepared(paths)
        self.assertEqual(0, sealed.returncode, sealed.stderr)
        record = json.loads(self.evidence.read_text(encoding="utf-8"))
        raw_ref = record["execution"]["artifacts"]["raw_supervisor_receipt"]["ref"]
        raw_path = self.repo / raw_ref
        refs = {
            item["ref"]
            for item in json.loads(seal.read_text(encoding="utf-8"))["artifacts"]
        }
        self.assertIn(record["log_ref"], refs)
        self.assertIn(record["execution"]["receipt_ref"], refs)
        self.assertIn(raw_ref, refs)
        raw_path.write_text("{}\n", encoding="utf-8")
        rejected, output = self.seal_prepared(
            paths, output_name="tampered-raw.json"
        )
        self.assertNotEqual(0, rejected.returncode)
        self.assertFalse(output.exists())

    def test_gwt_019_given_later_finalize_failure_when_an_earlier_event_is_valid_then_evidence_and_cache_are_unchanged(self) -> None:
        self.initialize_git()
        snapshot = self.capture_snapshot(profile="fast")
        fingerprint, _ = self.lookup()
        good_log = self.logs / "good.log"
        good_log.write_text("good\n", encoding="utf-8")
        receipt = self.write_receipt(snapshot, log_path=good_log, name="good-result")
        events = self.logs / "atomic-events.tsv"
        valid = "\t".join([
            "good", "validator-v1", fingerprint, "passed", "executed",
            "1000", "1010", "false", good_log.name, "-1", "good",
            "changed", receipt.name, "required",
        ])
        invalid = "\t".join([
            "bad", "validator-v1", fingerprint, "failed", "not-executed",
            "1020", "1030", "false", "missing.log", "-1", "bad",
            "changed", "", "required",
        ])
        events.write_text(valid + "\n" + invalid + "\n", encoding="utf-8")
        evidence_before = b"sentinel-evidence\n"
        cache_before = self.json_bytes({"schema_version": "1.0.0", "entries": {}})
        self.evidence.write_bytes(evidence_before)
        self.cache.write_bytes(cache_before)
        result = self.helper(
            "finalize", "--repo", str(self.repo), "--cache", str(self.cache),
            "--evidence", str(self.evidence), "--events", str(events),
            "--invocation-id", INVOCATION_ID, "--profile", "fast",
            "--environment-class", "windows-native", "--snapshot", str(snapshot),
        )
        self.assertNotEqual(0, result.returncode)
        self.assertEqual(evidence_before, self.evidence.read_bytes())
        self.assertEqual(cache_before, self.cache.read_bytes())

    def test_gwt_020_given_legacy_unbound_or_forged_minimal_evidence_when_passing_seal_is_requested_then_it_fails_closed(self) -> None:
        self.initialize_git()
        snapshot = self.capture_snapshot()
        fingerprint, _ = self.lookup(profile="release")
        legacy_log = self.logs / "legacy.log"
        legacy_log.write_bytes(b"")
        legacy_events = self.logs / "legacy-events.tsv"
        legacy_events.write_text(
            "\t".join([
                "legacy", "validator-v1", fingerprint, "not-applicable", "not-executed",
                "1000", "1010", "false", legacy_log.name, "-1", "legacy", "changed",
            ]) + "\n",
            encoding="utf-8",
        )
        legacy = self.helper(
            "finalize", "--repo", str(self.repo), "--cache", str(self.cache),
            "--evidence", str(self.evidence), "--events", str(legacy_events),
            "--invocation-id", INVOCATION_ID, "--profile", "release",
            "--environment-class", "windows-native", "--snapshot", str(snapshot),
        )
        self.assertEqual(0, legacy.returncode, legacy.stderr)
        legacy_paths = {
            "snapshot": snapshot,
            "post": self.logs / "legacy-post.json",
            "events": legacy_events,
            "evidence": self.evidence,
            "summary": self.logs / "legacy-summary.json",
            "workflow_summary": self.logs / "legacy-workflow-summary.json",
            "selection": self.logs / "legacy-selected.tsv",
            "selection_comparison": self.logs / "legacy-selection-comparison.tsv",
            "fingerprint_selection": self.logs / "legacy-fingerprint.tsv",
            "preparation_selection": self.logs / "legacy-preparation.tsv",
            "changed_paths": self.logs / "legacy-changed.txt",
        }
        legacy_paths["selection"].write_text("legacy\tlegacy\n", encoding="utf-8")
        legacy_paths["fingerprint_selection"].write_text(
            "legacy\tvalidator-v1\tinputs\treuse-by-input\n", encoding="utf-8"
        )
        legacy_paths["preparation_selection"].write_text(
            "legacy\tvalidator-v1\tinputs\treuse-by-input\n", encoding="utf-8"
        )
        legacy_paths["changed_paths"].write_text("inputs/rule.md\n", encoding="utf-8")
        legacy_snapshot = json.loads(snapshot.read_text(encoding="utf-8"))
        legacy_changed_digest = hashlib.sha256(
            legacy_paths["changed_paths"].read_bytes()
        ).hexdigest()
        legacy_paths["selection_comparison"].write_text(
            "\t".join((
                "validation-selection-comparison/v1",
                "changed-path",
                legacy_snapshot["identity"]["commit"],
                legacy_snapshot["identity"]["commit"],
                legacy_changed_digest,
                "",
            )) + "\n",
            encoding="utf-8",
        )
        self.write_summaries(legacy_paths, profile="release")
        verified = self.helper(
            "verify-snapshot", "--repo", str(self.repo), "--snapshot", str(snapshot),
            "--output", str(legacy_paths["post"]),
        )
        self.assertEqual(0, verified.returncode, verified.stderr)
        unbound, unbound_output = self.seal_prepared(
            legacy_paths, output_name="legacy-unbound.json"
        )
        self.assertNotEqual(0, unbound.returncode)
        self.assertFalse(unbound_output.exists())
        paths = self.prepare_invocation([{
            "id": "fixture-check", "outcome": "passed", "disposition": "executed"
        }], snapshot=snapshot)
        paths["evidence"].write_text(
            '{"validator_id":"fixture-check"}\n', encoding="utf-8"
        )
        rejected, output = self.seal_prepared(
            paths, output_name="forged-minimal.json"
        )
        self.assertNotEqual(0, rejected.returncode)
        self.assertFalse(output.exists())

    def test_gwt_021_given_zero_byte_executed_reused_and_nonexecuted_logs_when_sealed_then_all_are_retained_and_tamper_detected(self) -> None:
        specs = [
            {"id": "silent", "outcome": "passed", "disposition": "executed", "content": b""},
            {"id": "reused", "outcome": "passed", "disposition": "reused", "content": b""},
            {"id": "notapp", "outcome": "not-applicable", "disposition": "not-executed", "content": b""},
            {"id": "notselected", "outcome": "not-applicable", "disposition": "not-selected", "content": b""},
        ]
        paths = self.prepare_invocation(specs, profile="fast")
        sealed, seal = self.seal_prepared(paths)
        self.assertEqual(0, sealed.returncode, sealed.stderr)
        manifest = json.loads(seal.read_text(encoding="utf-8"))
        by_ref = {item["ref"]: item for item in manifest["artifacts"]}
        for validator_id in ("silent", "reused", "notapp", "notselected"):
            ref = f"artifacts/validation/run/{validator_id}.log"
            self.assertEqual(0, by_ref[ref]["bytes"])
        (self.logs / "reused.log").write_text("tampered\n", encoding="utf-8")
        rejected, output = self.seal_prepared(
            paths, output_name="tampered-retained-log.json"
        )
        self.assertNotEqual(0, rejected.returncode)
        self.assertFalse(output.exists())
        (self.logs / "reused.log").write_bytes(b"")
        (self.logs / "notapp.log").write_text("tampered\n", encoding="utf-8")
        rejected, output = self.seal_prepared(
            paths, output_name="tampered-nonexecuted-log.json"
        )
        self.assertNotEqual(0, rejected.returncode)
        self.assertFalse(output.exists())
        (self.logs / "notapp.log").write_bytes(b"")
        records = [
            json.loads(line)
            for line in paths["evidence"].read_text(encoding="utf-8").splitlines()
        ]
        reused_record = next(
            record for record in records if record["validator_id"] == "reused"
        )
        source_evidence = self.repo / reused_record["reuse_source"]["source_evidence"]["ref"]
        source_evidence.write_text("{\"forged\":true}\n", encoding="utf-8")
        rejected, output = self.seal_prepared(
            paths, output_name="tampered-cache-source.json"
        )
        self.assertNotEqual(0, rejected.returncode)
        self.assertFalse(output.exists())

    def test_gwt_022_given_concurrent_tracked_mutation_between_snapshot_bookends_then_capture_fails_closed(self) -> None:
        self.initialize_git()
        module = self.load_helper_module("concurrent_snapshot")
        original: Callable[[Path], dict[str, object]] = (
            module.capture_repository_identity_once
        )
        first_complete = threading.Event()
        mutation_complete = threading.Event()
        calls = 0

        def wrapped(repo: Path) -> dict[str, object]:
            nonlocal calls
            value = original(repo)
            calls += 1
            if calls == 1:
                first_complete.set()
                self.assertTrue(mutation_complete.wait(2))
            return value

        def mutate() -> None:
            self.assertTrue(first_complete.wait(2))
            (self.inputs / "rule.md").write_text(
                "concurrent mutation\n", encoding="utf-8"
            )
            mutation_complete.set()

        module.capture_repository_identity_once = wrapped
        thread = threading.Thread(target=mutate, daemon=True)
        thread.start()
        with self.assertRaises(module.EvidenceError):
            module.capture_repository_snapshot(self.repo, "release")
        thread.join(2)
        self.assertFalse(thread.is_alive())
        original_run = module.subprocess.run

        def timeout_run(*_args: object, **_kwargs: object) -> None:
            raise subprocess.TimeoutExpired(cmd=["git"], timeout=30)

        module.subprocess.run = timeout_run
        try:
            with self.assertRaisesRegex(module.EvidenceError, "exceeded 30 seconds") as raised:
                module.run_git(self.repo, "status")
            self.assertNotIn(str(self.repo), str(raised.exception))
        finally:
            module.subprocess.run = original_run

    def test_gwt_023_given_symlinked_retained_log_when_recorded_then_input_symlink_is_rejected(self) -> None:
        self.initialize_git()
        fingerprint, _ = self.lookup()
        target = self.logs / "real.log"
        target.write_text("real\n", encoding="utf-8")
        link = self.logs / "linked.log"
        try:
            link.symlink_to(target)
        except OSError as exc:
            self.skipTest(f"symlink creation is unavailable: {type(exc).__name__}")
        result = self.record_current(
            fingerprint,
            outcome="passed",
            disposition="reused",
            log_path=link,
            cache_hit=True,
        )
        self.assertNotEqual(0, result.returncode)
        self.assertFalse(self.evidence.exists())
        link.unlink()
        snapshot = self.capture_snapshot(profile="fast")
        raw_target = self.logs / "raw-receipt-target.json"
        raw_target.write_bytes(b"must remain unchanged\n")
        raw_result = self.logs / "supervised-result.json"
        raw_link = Path(str(raw_result) + ".process.json")
        raw_link.symlink_to(raw_target)
        launch_marker = self.logs / "symlink-launch-marker.txt"
        supervised, _log, result_path = self.supervise(
            snapshot,
            Path(sys.executable).name,
            "-c",
            "from pathlib import Path; Path('artifacts/validation/run/symlink-launch-marker.txt').write_text('launched')",
        )
        self.assertNotEqual(0, supervised.returncode)
        self.assertFalse(launch_marker.exists())
        self.assertFalse(result_path.exists())
        self.assertEqual(b"must remain unchanged\n", raw_target.read_bytes())

    def test_gwt_024_given_required_advisory_and_blocked_nonexecution_when_passing_seal_is_requested_then_enforcement_policy_is_exact(self) -> None:
        required = self.prepare_invocation([{
            "id": "deferred", "outcome": "deferred-with-owner",
            "disposition": "not-executed", "enforcement": "required",
        }])
        rejected, output = self.seal_prepared(
            required, output_name="required-deferred.json"
        )
        self.assertNotEqual(0, rejected.returncode)
        self.assertFalse(output.exists())
        advisory = self.prepare_invocation([{
            "id": "deferred", "outcome": "deferred-with-owner",
            "disposition": "not-executed", "enforcement": "advisory",
        }], snapshot=required["snapshot"])
        accepted, _ = self.seal_prepared(
            advisory, output_name="advisory-deferred.json"
        )
        self.assertEqual(0, accepted.returncode, accepted.stderr)
        blocked = self.prepare_invocation([{
            "id": "blocked", "outcome": "blocked-by-environment",
            "disposition": "not-executed", "enforcement": "advisory",
        }], snapshot=required["snapshot"])
        rejected, output = self.seal_prepared(blocked, output_name="blocked.json")
        self.assertNotEqual(0, rejected.returncode)
        self.assertFalse(output.exists())

    def test_gwt_025_given_failed_seal_when_cache_was_empty_then_no_promotion_occurs_until_a_successful_fast_seal(self) -> None:
        paths = self.prepare_invocation(profile="fast")
        summary = json.loads(paths["summary"].read_text(encoding="utf-8"))
        summary["profile"] = "forged"
        paths["summary"].write_bytes(self.json_bytes(summary))
        failed, output = self.seal_prepared(
            paths, output_name="failed-before-cache.json"
        )
        self.assertNotEqual(0, failed.returncode)
        self.assertFalse(output.exists())
        self.assertFalse(self.cache.exists())
        self.assertFalse(self.lookup(profile="fast")[1])
        self.write_summaries(paths, profile="fast")
        module = self.load_helper_module("cache_rollback")
        injected_output = self.logs / "manifest-publication-failed.json"
        parsed = module.parser().parse_args(
            self.seal_arguments(paths, outcome="passed", output=injected_output)
        )
        original_atomic_write = module.atomic_write_bytes

        def fail_manifest_publication(path: Path, content: bytes) -> None:
            if Path(path) == injected_output:
                raise OSError("injected manifest publication failure")
            original_atomic_write(path, content)

        module.atomic_write_bytes = fail_manifest_publication
        try:
            with self.assertRaisesRegex(OSError, "injected manifest publication failure"):
                module.seal_invocation(parsed)
        finally:
            module.atomic_write_bytes = original_atomic_write
        self.assertFalse(injected_output.exists())
        self.assertFalse(self.cache.exists())
        self.assertFalse(self.lookup(profile="fast")[1])
        self.cache.write_text("{malformed\n", encoding="utf-8")
        cache_failed, cache_failed_output = self.seal_prepared(
            paths, output_name="cache-promotion-failed.json"
        )
        self.assertNotEqual(0, cache_failed.returncode)
        self.assertFalse(cache_failed_output.exists())
        self.cache.unlink()
        passed, _ = self.seal_prepared(
            paths, output_name="passed-before-cache.json"
        )
        self.assertEqual(0, passed.returncode, passed.stderr)
        self.assertTrue(self.lookup(profile="fast")[1])

    def test_gwt_026_given_raw_or_wrapper_dimension_is_forged_when_recorded_then_full_authentication_rejects_each_mismatch(self) -> None:
        self.initialize_git()
        snapshot = self.capture_snapshot(profile="fast")
        fingerprint, _ = self.lookup()

        def raw_argv(raw: dict[str, Any], _: dict[str, Any]) -> None:
            raw["argv"] = ["python", "-c", "different"]
            raw["argv_sha256"] = self.canonical_digest(raw["argv"])

        def raw_timing(raw: dict[str, Any], _: dict[str, Any]) -> None:
            raw["finished_at"] = "1970-01-01T00:00:01.020Z"
            raw["duration_seconds"] = 0.02

        mutations: dict[
            str, Callable[[dict[str, Any], dict[str, Any]], None]
        ] = {
            "safe-argv": raw_argv,
            "safe-digest": lambda raw, wrapper: raw.__setitem__("argv_sha256", "0" * 64),
            "effective-digest": lambda raw, wrapper: raw.__setitem__("effective_argv_sha256", "1" * 64),
            "cwd": lambda raw, wrapper: raw.__setitem__("cwd_ref", "subdir"),
            "timeout": lambda raw, wrapper: raw.__setitem__("timeout_seconds", 11.0),
            "grace": lambda raw, wrapper: raw.__setitem__("termination_grace_seconds", 2.0),
            "timing": raw_timing,
            "exit": lambda raw, wrapper: raw.__setitem__("child_exit_code", 1),
            "log": lambda raw, wrapper: raw["log"].__setitem__("bytes", raw["log"]["bytes"] + 1),
            "status": lambda raw, wrapper: raw.__setitem__("status", "timed-out"),
            "platform": lambda raw, wrapper: raw["platform"].__setitem__("mechanism", "forged"),
            "termination": lambda raw, wrapper: raw["termination"].__setitem__("verification", "forged"),
            "error": lambda raw, wrapper: raw.__setitem__("error", {"stage": "forged", "type": "Error"}),
        }
        for name, mutation in mutations.items():
            with self.subTest(name=name):
                receipt_path = self.write_receipt(snapshot, name=f"forged-{name}")
                raw_path = Path(str(receipt_path) + ".process.json")
                raw = json.loads(raw_path.read_text(encoding="utf-8"))
                wrapper = json.loads(receipt_path.read_text(encoding="utf-8"))
                mutation(raw, wrapper)
                raw_content = self.json_bytes(raw)
                raw_path.write_bytes(raw_content)
                wrapper["supervisor_receipt"]["sha256"] = hashlib.sha256(
                    raw_content
                ).hexdigest()
                wrapper["supervisor_receipt"]["bytes"] = len(raw_content)
                wrapper["supervisor_receipt"]["status"] = raw["status"]
                receipt_path.write_bytes(self.json_bytes(wrapper))
                result = self.record_current(
                    fingerprint,
                    result_path=receipt_path,
                    snapshot=snapshot,
                    evidence=self.logs / f"forged-{name}.jsonl",
                )
                self.assertNotEqual(0, result.returncode)

    def test_gwt_027_given_malformed_evidence_when_summaries_fail_then_existing_outputs_are_not_partially_replaced(self) -> None:
        self.evidence.write_text("{malformed\n", encoding="utf-8")
        summary = self.logs / "atomic-summary.json"
        workflow = self.logs / "atomic-workflow-summary.json"
        sentinel = b"sentinel-summary\n"
        summary.write_bytes(sentinel)
        workflow.write_bytes(sentinel)
        summarized = self.helper(
            "summarize", "--evidence", str(self.evidence), "--output", str(summary),
            "--invocation-id", INVOCATION_ID, "--profile", "fast",
        )
        workflow_summarized = self.helper(
            "workflow-summary", "--evidence", str(self.evidence),
            "--output", str(workflow), "--invocation-id", INVOCATION_ID,
            "--profile", "fast", "--wall-span-ms", "10",
        )
        self.assertNotEqual(0, summarized.returncode)
        self.assertNotEqual(0, workflow_summarized.returncode)
        self.assertEqual(sentinel, summary.read_bytes())
        self.assertEqual(sentinel, workflow.read_bytes())

    def test_gwt_028_given_supervised_immutable_receipt_decision_when_reused_then_exact_identity_and_tracked_receipt_are_sealed(self) -> None:
        self.initialize_git()
        tracked_receipt = self.repo / ".ai/distribution/validation/immutable-history-receipt.yaml"
        tracked_receipt.parent.mkdir(parents=True)
        tracked_receipt.write_text("schema_version: '1.0'\n", encoding="utf-8")
        self.git("add", tracked_receipt.relative_to(self.repo).as_posix())
        self.git("commit", "-m", "tracked immutable receipt fixture")
        snapshot = self.capture_snapshot(profile="fast")
        preparation, fingerprint = self.write_immutable_preparation(
            snapshot,
            profile="fast",
            reusable_ids=["immutable-check"],
        )
        paths = self.prepare_invocation(
            [{
                "id": "immutable-check",
                "outcome": "passed",
                "disposition": "reused",
                "cache_hit": False,
                "result_path": preparation,
                "fingerprint": fingerprint,
                "fingerprint_contract": False,
            }],
            profile="fast",
            snapshot=snapshot,
            preparation_python=sys.executable,
        )
        sealed, output = self.seal_prepared(
            paths, output_name="immutable-reuse-seal.json"
        )
        self.assertEqual(0, sealed.returncode, sealed.stderr)
        record = json.loads(paths["evidence"].read_text(encoding="utf-8"))
        self.assertEqual("immutable-history", record["reuse_source"]["kind"])
        self.assertEqual(fingerprint, record["input_fingerprint"])
        refs = {
            item["ref"]
            for item in json.loads(output.read_text(encoding="utf-8"))["artifacts"]
        }
        self.assertIn(
            ".ai/distribution/validation/immutable-history-receipt.yaml", refs
        )
        self.assertIn(preparation.relative_to(self.repo).as_posix(), refs)
        self.assertIn(Path(str(preparation) + ".process.json").relative_to(self.repo).as_posix(), refs)

    def test_gwt_029_given_full_required_preparation_without_reuse_when_sealed_then_child_exit_ten_evidence_is_retained(self) -> None:
        self.initialize_git()
        snapshot = self.capture_snapshot(profile="fast")
        preparation, _fingerprint = self.write_immutable_preparation(
            snapshot,
            profile="fast",
            reusable_ids=[],
            routine_reusable=False,
            name="immutable-full-required",
        )
        paths = self.prepare_invocation(
            profile="fast",
            snapshot=snapshot,
            preparation_python=sys.executable,
        )
        paths["preparation_results"] = [preparation]  # type: ignore[assignment]
        sealed, output = self.seal_prepared(
            paths, output_name="full-required-preparation-seal.json"
        )
        self.assertEqual(0, sealed.returncode, sealed.stderr)
        refs = {
            item["ref"]
            for item in json.loads(output.read_text(encoding="utf-8"))["artifacts"]
        }
        self.assertIn(preparation.relative_to(self.repo).as_posix(), refs)
        receipt = json.loads(preparation.read_text(encoding="utf-8"))
        self.assertEqual(10, receipt["exit_code"])
        paths["preparation_python"] = "different-python"  # type: ignore[assignment]
        rejected, rejected_output = self.seal_prepared(
            paths, output_name="wrong-preparation-python.json"
        )
        self.assertNotEqual(0, rejected.returncode)
        self.assertFalse(rejected_output.exists())


class ValidationEvidenceBootstrapReadinessGwtTests(ValidationEvidenceFixture):
    """Focused bootstrap admission and containment proofs; not a routine profile target."""

    def test_gwt_031_given_dirty_clean_required_bootstrap_when_admitted_then_snapshot_is_retained_and_target_is_not_launched(self) -> None:
        self.install_tracked_helper()
        (self.inputs / "rule.md").write_text("dirty governed bytes\n", encoding="utf-8")
        snapshot = self.logs / "dirty-bootstrap-snapshot.json"
        marker = self.repo / "artifacts/validation/dirty-bootstrap-target.txt"
        target = [
            sys.executable,
            "-c",
            "from pathlib import Path; Path('artifacts/validation/dirty-bootstrap-target.txt').write_text('launched')",
        ]
        result, _log, result_path = self.supervise_bootstrap(
            snapshot,
            *target,
            profile="release",
            require_clean=True,
            name="dirty-bootstrap",
        )
        self.assertEqual(128, result.returncode, result.stderr)
        self.assertFalse(marker.exists())
        snapshot_value = json.loads(snapshot.read_text(encoding="utf-8"))
        self.assertFalse(snapshot_value["identity"]["clean"])
        receipt = json.loads(result_path.read_text(encoding="utf-8"))
        self.assertEqual("snapshot-drift", receipt["status"])
        self.assertTrue(receipt["execution"]["launched"], "contained driver was launched")
        self.assertFalse(receipt["bootstrap"]["target_launched"])
        self.assertEqual("repository-not-clean", receipt["bootstrap"]["reason_code"])
        verified = self.helper(
            "verify-supervision-result", "--repo", str(self.repo),
            "--snapshot", str(snapshot), "--result-path", str(result_path),
        )
        self.assertEqual(0, verified.returncode, verified.stderr)
        self.assertEqual("snapshot-drift\tfalse\t", verified.stdout.rstrip("\r\n"))

    def test_gwt_032_given_bootstrap_target_with_descendant_when_timed_out_then_the_owned_tree_is_empty(self) -> None:
        self.install_tracked_helper()
        snapshot = self.logs / "timeout-bootstrap-snapshot.json"
        marker = self.repo / "artifacts/validation/bootstrap-descendant-survived.txt"
        descendant = (
            "import time; from pathlib import Path; time.sleep(3); "
            "Path('artifacts/validation/bootstrap-descendant-survived.txt').write_text('survived')"
        )
        target = [
            sys.executable,
            "-c",
            "import subprocess,sys,time; "
            f"subprocess.Popen([sys.executable,'-c',{descendant!r}]); time.sleep(10)",
        ]
        result, _log, result_path = self.supervise_bootstrap(
            snapshot,
            *target,
            profile="fast",
            timeout_seconds=2.0,
            name="timeout-bootstrap",
        )
        self.assertEqual(124, result.returncode, result.stderr)
        receipt = json.loads(result_path.read_text(encoding="utf-8"))
        self.assertEqual("timed-out", receipt["status"])
        self.assertTrue(receipt["bootstrap"]["target_launched"])
        self.assertTrue(receipt["cleanup"]["tree_empty"])
        time.sleep(3.5)
        self.assertFalse(marker.exists())

    def test_gwt_033_given_forged_prepare_output_when_sealed_then_standard_fingerprint_parity_fails_closed(self) -> None:
        paths = self.prepare_invocation(profile="fast")
        expected_argv = self.control_argv(
            "prepare", paths, profile="fast", preparation_python=None
        )
        forged_log = self.logs / "forged-prepare.log"
        forged_log.write_text(
            f"fixture-check\t{'0' * 64}\tfalse\t\n", encoding="utf-8"
        )
        safe_python = (
            f"<absolute-path>/{Path(sys.executable).name}"
            if Path(sys.executable).is_absolute()
            else sys.executable
        )
        forged_result = self.write_receipt(
            paths["snapshot"],
            log_path=forged_log,
            name="forged-prepare",
            safe_argv=[safe_python, *expected_argv[1:]],
            effective_argv=expected_argv,
            accepted_child_exit_codes=[0],
        )
        forged_paths = dict(paths)
        controls = dict(paths["control_results"])  # type: ignore[arg-type]
        controls["prepare"] = forged_result
        forged_paths["control_results"] = controls  # type: ignore[assignment]
        sealed, output = self.seal_prepared(
            forged_paths, output_name="forged-prepare-seal.json"
        )
        self.assertNotEqual(0, sealed.returncode)
        self.assertFalse(output.exists())
        self.assertFalse(self.cache.exists())

    def test_gwt_034_given_uncapturable_bootstrap_repository_when_admitted_then_failure_receipt_is_retained_without_target_launch(self) -> None:
        fixture_helper = self.repo / ".ai/scripts/validation-evidence.py"
        fixture_helper.parent.mkdir(parents=True)
        fixture_helper.write_bytes(HELPER.read_bytes())
        snapshot = self.logs / "uncapturable-bootstrap-snapshot.json"
        marker = self.repo / "artifacts/validation/uncapturable-target.txt"
        target = [
            sys.executable,
            "-c",
            "from pathlib import Path; Path('artifacts/validation/uncapturable-target.txt').write_text('launched')",
        ]
        result, _log, result_path = self.supervise_bootstrap(
            snapshot,
            *target,
            profile="fast",
            name="uncapturable-bootstrap",
        )
        self.assertEqual(128, result.returncode, result.stderr)
        self.assertFalse(marker.exists())
        admission = json.loads(snapshot.read_text(encoding="utf-8"))
        self.assertEqual("validation-repository-admission-failure/v1", admission["schema_version"])
        self.assertEqual("snapshot-capture-failed", admission["reason_code"])
        receipt = json.loads(result_path.read_text(encoding="utf-8"))
        self.assertEqual("snapshot-drift", receipt["status"])
        self.assertFalse(receipt["bootstrap"]["target_launched"])
        self.assertEqual("snapshot-capture-failed", receipt["bootstrap"]["reason_code"])


class ValidationEvidenceRoutineContractGwtTests(ValidationEvidenceFixture):
    """Routine proof for supervised control roles and staged terminal publication."""

    def test_gwt_030_given_exact_supervised_controls_and_staged_manifest_when_published_then_terminal_pair_is_reusable(self) -> None:
        self.install_tracked_helper("tracked control helper fixture")
        bootstrap_snapshot = self.logs / "fast-snapshot-pre.json"
        bootstrap_target = [
            sys.executable,
            ".ai/scripts/validation-evidence.py",
            "verify-snapshot",
            "--repo", ".",
            "--snapshot", bootstrap_snapshot.relative_to(self.repo).as_posix(),
        ]
        bootstrapped, bootstrap_log, bootstrap_result = self.supervise_bootstrap(
            bootstrap_snapshot,
            *bootstrap_target,
            profile="fast",
            name="bootstrap-snapshot-control",
        )
        self.assertEqual(0, bootstrapped.returncode, bootstrapped.stderr)
        bootstrap_receipt = json.loads(bootstrap_result.read_text(encoding="utf-8"))
        self.assertTrue(bootstrap_receipt["bootstrap"]["target_launched"])
        self.assertEqual(0, bootstrap_receipt["bootstrap"]["target_exit_code"])
        bootstrap_verified = self.helper(
            "verify-supervision-result", "--repo", str(self.repo),
            "--snapshot", str(bootstrap_snapshot),
            "--result-path", str(bootstrap_result),
        )
        self.assertEqual(0, bootstrap_verified.returncode, bootstrap_verified.stderr)
        self.assertEqual("completed\ttrue\t0", bootstrap_verified.stdout.strip())
        paths = self.prepare_invocation(profile="fast", snapshot=bootstrap_snapshot)
        controls = dict(paths["control_results"])  # type: ignore[arg-type]
        controls["bootstrap-snapshot"] = bootstrap_result
        paths["control_results"] = controls  # type: ignore[assignment]
        unbound, unbound_stage = self.seal_prepared(
            paths,
            output_name="unbound-staged-manifest.json",
            publication_name="unbound-published-manifest.json",
        )
        self.assertNotEqual(0, unbound.returncode)
        self.assertFalse(unbound_stage.exists())
        self.assertFalse(self.cache.exists())
        preexisting_stage = self.logs / "preexisting-stage.json"
        preexisting_final = self.logs / "preexisting-final.json"
        preexisting_terminal_result = self.logs / "preexisting-terminal-result.json"
        preexisting_terminal_log = self.logs / "preexisting-terminal.log"
        preexisting_final.write_bytes(b"must not be overwritten\n")
        preexisting = self.helper(*self.seal_arguments(
            paths,
            outcome="passed",
            output=preexisting_stage,
            publication_output=preexisting_final,
            terminal_result=preexisting_terminal_result,
            terminal_log=preexisting_terminal_log,
        ))
        self.assertNotEqual(0, preexisting.returncode)
        self.assertFalse(preexisting_stage.exists())
        self.assertEqual(b"must not be overwritten\n", preexisting_final.read_bytes())
        self.assertFalse(self.cache.exists())
        preexisting_final.unlink()
        staged_name = "staged-terminal-manifest.json"
        published_name = "published-terminal-manifest.json"
        staged = self.logs / staged_name
        published = self.logs / published_name
        terminal_log = self.logs / "terminal-seal.log"
        terminal_result = self.logs / "terminal-seal-result.json"
        seal_arguments = self.seal_arguments(
            paths,
            outcome="passed",
            output=staged,
            publication_output=published,
            terminal_result=terminal_result,
            terminal_log=terminal_log,
        )
        terminal_command = [
            sys.executable,
            ".ai/scripts/validation-evidence.py",
            *seal_arguments,
        ]
        sealed, observed_terminal_log, observed_terminal_result = self.supervise(
            paths["snapshot"],
            *terminal_command,
            name="terminal-seal",
        )
        self.assertEqual(
            0,
            sealed.returncode,
            sealed.stderr
            + (
                observed_terminal_log.read_text(encoding="utf-8", errors="replace")
                if observed_terminal_log.is_file()
                else "missing terminal log"
            ),
        )
        self.assertEqual(terminal_log, observed_terminal_log)
        self.assertEqual(terminal_result, observed_terminal_result)
        self.assertTrue(staged.is_file())
        self.assertFalse(published.exists())
        self.assertFalse(self.lookup(profile="fast")[1])
        manifest = json.loads(staged.read_text(encoding="utf-8"))
        self.assertEqual(
            [
                "bootstrap-snapshot", "finalize", "post-snapshot", "prepare",
                "summarize", "workflow-summary",
            ],
            [item["role"] for item in manifest["control_plane"]],
        )
        terminal_declaration = manifest["terminal_supervision"]
        terminal_receipt = json.loads(terminal_result.read_text(encoding="utf-8"))
        self.assertEqual("supervised", terminal_declaration["mode"])
        self.assertEqual(
            terminal_result.relative_to(self.repo).as_posix(),
            terminal_declaration["result_ref"],
        )
        self.assertEqual(
            terminal_log.relative_to(self.repo).as_posix(),
            terminal_declaration["log_ref"],
        )
        self.assertEqual(
            terminal_receipt["command"]["effective_argv_digest"],
            terminal_declaration["expected_effective_argv_digest"],
        )
        artifact_refs = {item["ref"] for item in manifest["artifacts"]}
        for path in (
            bootstrap_result,
            bootstrap_log,
            Path(str(bootstrap_result) + ".process.json"),
            Path(str(bootstrap_result) + ".bootstrap.json"),
        ):
            self.assertIn(path.relative_to(self.repo).as_posix(), artifact_refs)
        cache_value = json.loads(self.cache.read_text(encoding="utf-8"))
        source_manifest_refs = {
            entry["reuse_source"]["source_manifest"]["ref"]
            for entry in cache_value["entries"].values()
        }
        self.assertEqual({published.relative_to(self.repo).as_posix()}, source_manifest_refs)
        held_before_publication = self.logs / "terminal-seal-result.before-publication"
        terminal_result.rename(held_before_publication)
        self.assertFalse(published.exists())
        self.assertFalse(self.lookup(profile="fast")[1])
        held_before_publication.rename(terminal_result)
        terminal_raw = Path(str(terminal_result) + ".process.json")
        terminal_raw_content = terminal_raw.read_bytes()
        terminal_raw.write_text("{}\n", encoding="utf-8")
        self.assertFalse(published.exists())
        self.assertFalse(self.lookup(profile="fast")[1])
        tampered_terminal = self.helper(
            "verify-terminal-invocation", "--repo", str(self.repo),
            "--snapshot", str(paths["snapshot"]), "--manifest", str(staged),
            "--result-path", str(terminal_result), "--", *terminal_command,
        )
        self.assertNotEqual(0, tampered_terminal.returncode)
        terminal_raw.write_bytes(terminal_raw_content)
        verified_terminal = self.helper(
            "verify-supervision-result", "--repo", str(self.repo),
            "--snapshot", str(paths["snapshot"]),
            "--result-path", str(terminal_result),
        )
        self.assertEqual(0, verified_terminal.returncode, verified_terminal.stderr)
        staged_content = staged.read_bytes()
        verified_invocation = self.helper(
            "verify-terminal-invocation", "--repo", str(self.repo),
            "--snapshot", str(paths["snapshot"]), "--manifest", str(staged),
            "--result-path", str(terminal_result), "--", *terminal_command,
        )
        self.assertEqual(0, verified_invocation.returncode, verified_invocation.stderr)
        self.assertEqual(
            hashlib.sha256(staged_content).hexdigest(),
            verified_invocation.stdout.strip(),
        )
        wrong_terminal_argv = self.helper(
            "verify-terminal-invocation", "--repo", str(self.repo),
            "--snapshot", str(paths["snapshot"]), "--manifest", str(staged),
            "--result-path", str(terminal_result), "--", *terminal_command,
            "--unexpected",
        )
        self.assertNotEqual(0, wrong_terminal_argv.returncode)
        forged_manifest = json.loads(staged_content)
        forged_manifest["terminal_supervision"][
            "expected_effective_argv_digest"
        ] = "0" * 64
        forged_core = {
            key: value
            for key, value in forged_manifest.items()
            if key != "manifest_digest"
        }
        forged_manifest["manifest_digest"] = self.canonical_digest(forged_core)
        staged.write_bytes(self.json_bytes(forged_manifest))
        forged_terminal = self.helper(
            "verify-terminal-invocation", "--repo", str(self.repo),
            "--snapshot", str(paths["snapshot"]), "--manifest", str(staged),
            "--result-path", str(terminal_result), "--", *terminal_command,
        )
        self.assertNotEqual(0, forged_terminal.returncode)
        staged.write_bytes(staged_content)
        published.write_bytes(b"racing publication must survive\n")
        with self.assertRaises(FileExistsError):
            os.link(staged, published)
        self.assertEqual(b"racing publication must survive\n", published.read_bytes())
        self.assertEqual(staged_content, staged.read_bytes())
        staged.unlink()
        published.unlink()
        self.assertFalse(staged.exists())
        self.assertFalse(published.exists())
        self.assertFalse(self.lookup(profile="fast")[1])
        staged.write_bytes(staged_content)
        os.link(staged, published)
        staged.unlink()
        self.assertTrue(self.lookup(profile="fast")[1])
        held_terminal_result = self.logs / "terminal-seal-result.held"
        terminal_result.rename(held_terminal_result)
        self.assertFalse(self.lookup(profile="fast")[1])
        held_terminal_result.rename(terminal_result)
        self.assertTrue(self.lookup(profile="fast")[1])
        terminal_raw.write_text("{}\n", encoding="utf-8")
        self.assertFalse(self.lookup(profile="fast")[1])
        terminal_raw.write_bytes(terminal_raw_content)
        self.assertTrue(self.lookup(profile="fast")[1])
        published.write_text("tampered publication\n", encoding="utf-8")
        self.assertFalse(self.lookup(profile="fast")[1])
        published.unlink()

        missing_paths = dict(paths)
        missing_controls = dict(controls)
        missing_controls.pop("summarize")
        missing_paths["control_results"] = missing_controls  # type: ignore[assignment]
        missing, missing_output = self.seal_prepared(
            missing_paths, output_name="missing-control.json"
        )
        self.assertNotEqual(0, missing.returncode)
        self.assertFalse(missing_output.exists())

        duplicate_output = self.logs / "duplicate-control.json"
        duplicate_arguments = self.seal_arguments(
            paths, outcome="passed", output=duplicate_output
        )
        duplicate_arguments.extend((
            "--control-result", "finalize", str(controls["finalize"]),
        ))
        duplicate = self.helper(*duplicate_arguments)
        self.assertNotEqual(0, duplicate.returncode)
        self.assertFalse(duplicate_output.exists())

        unknown_output = self.logs / "unknown-control.json"
        unknown_arguments = self.seal_arguments(
            paths, outcome="passed", output=unknown_output
        )
        unknown_arguments.extend((
            "--control-result", "unknown-role", str(controls["finalize"]),
        ))
        unknown = self.helper(*unknown_arguments)
        self.assertNotEqual(0, unknown.returncode)
        self.assertFalse(unknown_output.exists())

        wrong_argv = self.control_argv(
            "summarize", paths, profile="fast", preparation_python=None
        )
        wrong_argv[-1] = "wrong-profile"
        safe_python = (
            f"<absolute-path>/{Path(sys.executable).name}"
            if Path(sys.executable).is_absolute()
            else sys.executable
        )
        wrong_log = self.logs / "wrong-control.log"
        wrong_log.write_bytes(b"")
        wrong_result = self.write_receipt(
            paths["snapshot"],
            log_path=wrong_log,
            name="wrong-control",
            safe_argv=[safe_python, *wrong_argv[1:]],
            effective_argv=wrong_argv,
            accepted_child_exit_codes=[0],
        )
        wrong_paths = dict(paths)
        wrong_controls = dict(controls)
        wrong_controls["summarize"] = wrong_result
        wrong_paths["control_results"] = wrong_controls  # type: ignore[assignment]
        wrong, wrong_output = self.seal_prepared(
            wrong_paths, output_name="wrong-control-argv.json"
        )
        self.assertNotEqual(0, wrong.returncode)
        self.assertFalse(wrong_output.exists())

    def test_gwt_035_given_repository_relative_finalize_refs_when_supervised_then_snapshot_resolves_from_repository_root(self) -> None:
        self.install_tracked_helper("tracked repository-relative finalize fixture")
        snapshot = self.capture_snapshot(
            profile="fast", name="fast-snapshot-pre.json"
        )
        fingerprint, _reusable = self.lookup(profile="fast")
        execution_receipt = self.write_receipt(
            snapshot, name="fixture-check-result"
        )
        changed_paths_digest = hashlib.sha256(b"inputs/rule.md\n").hexdigest()
        events = self.logs / "events.tsv"
        events.write_text(
            "\t".join((
                "fixture-check",
                "validator-v1",
                fingerprint,
                "passed",
                "executed",
                "1000",
                "1010",
                "false",
                self.log.name,
                "-1",
                "fixture",
                changed_paths_digest,
                execution_receipt.name,
                "required",
            )) + "\n",
            encoding="utf-8",
        )
        paths = {
            "snapshot": snapshot,
            "events": events,
            "evidence": self.evidence,
        }
        command = self.control_argv(
            "finalize",
            paths,
            profile="fast",
            preparation_python=None,
        )
        self.assertEqual(
            self.evidence.relative_to(self.repo).as_posix(),
            command[command.index("--evidence") + 1],
        )
        self.assertEqual(
            snapshot.relative_to(self.repo).as_posix(),
            command[command.index("--snapshot") + 1],
        )

        finalized, control_log, control_result = self.supervise(
            snapshot,
            *command,
            name="control-finalize-repository-relative",
        )
        diagnostic = (
            control_log.read_text(encoding="utf-8", errors="replace")
            if control_log.is_file()
            else "missing retained control log"
        )
        self.assertEqual(0, finalized.returncode, finalized.stderr + diagnostic)
        verified = self.helper(
            "verify-supervision-result",
            "--repo", str(self.repo),
            "--snapshot", str(snapshot),
            "--result-path", str(control_result),
        )
        self.assertEqual(0, verified.returncode, verified.stderr)
        self.assertEqual("completed\ttrue\t0", verified.stdout.strip())

        records = [
            json.loads(line)
            for line in self.evidence.read_text(encoding="utf-8").splitlines()
            if line
        ]
        self.assertEqual(1, len(records))
        record = records[0]
        self.assertEqual("fixture-check", record["validator_id"])
        self.assertEqual(
            self.log.relative_to(self.repo).as_posix(),
            record["log_ref"],
        )
        self.assertEqual(
            execution_receipt.relative_to(self.repo).as_posix(),
            record["execution"]["receipt_ref"],
        )
        expected_snapshot = json.loads(snapshot.read_text(encoding="utf-8"))
        self.assertEqual(
            expected_snapshot["identity_digest"],
            record["execution"]["snapshot"]["identity_digest"],
        )

if __name__ == "__main__":
    unittest.main()
