#!/usr/bin/env python3
"""Independent behavior expectations for artifact preparation, custody and migration."""
from __future__ import annotations

import copy
import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / ".ai/scripts"))
import execution_artifact_contract as CONTRACT

ROLE = ".ai/assets/sub-agent-role-prompts/mechanical-evidence-worker/sub-agent.yaml"
REVIEW_ROLE = ".ai/assets/sub-agent-role-prompts/fixed-head-independent-auditor/sub-agent.yaml"
SKILL = ".ai/assets/skills/ai-context-upgrader/skill.yaml"


class StructureTests(unittest.TestCase):
    def test_exact_types_batch_unknown_fields_and_unknown_schema_keywords(self) -> None:
        model = {"type": "object", "properties": {"count": {"type": "integer"}, "ready": {"type": "boolean"}}, "required": ["count", "ready"], "additionalProperties": False}
        errors = CONTRACT.validate_model({"count": True, "ready": 1, "extra": "x"}, model, "sample")
        self.assertEqual(3, len(errors))
        self.assertTrue(any("count must be integer" in error for error in errors))
        self.assertTrue(any("ready must be boolean" in error for error in errors))
        model["properties"]["count"]["minimun"] = 1
        self.assertTrue(any("unsupported schema keyword minimun" in error for error in CONTRACT.schema_errors(model)))

    def test_numeric_extremes_and_inapplicable_constraints(self) -> None:
        self.assertEqual([], CONTRACT.validate_model(10 ** 1000, {"type": "number"}, "number"))
        for value in (float("nan"), float("inf"), True):
            self.assertTrue(CONTRACT.validate_model(value, {"type": "number"}, "number"))
        for model in ({"type": "string", "minimum": 1}, {"type": "number", "minItems": 1}):
            self.assertTrue(any("does not apply" in error for error in CONTRACT.schema_errors(model)))
        self.assertEqual(["model.type is invalid"], CONTRACT.schema_errors({"type": [{"bad": "type"}]}))

    def test_authority_follows_source_or_fixed_package_envelope_requirements(self) -> None:
        with tempfile.TemporaryDirectory(prefix="artifact-package-authority-") as temporary:
            envelope = Path(temporary).resolve(); payload = envelope / "payload"; payload.mkdir()
            for ref in (*CONTRACT.AUTHORITY_REFS, ROLE, SKILL):
                destination = payload / ref; destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / ref, destination)
            packet = {"role": {"path": ROLE}, "owning_skill": "ai-context-upgrader"}
            source = CONTRACT.authority_manifest(payload, packet)
            self.assertIn("requirements.txt", [item["path"] for item in source])
            requirements = (payload / "requirements.txt").read_bytes()
            (payload / "requirements.txt").unlink(); (envelope / "requirements.txt").write_bytes(requirements)
            packaged = CONTRACT.authority_manifest(payload, packet)
            self.assertIn({"path": "package-envelope:requirements.txt", "sha256": CONTRACT.sha256(requirements)}, packaged)
            (envelope / "requirements.txt").unlink()
            with self.assertRaisesRegex(ValueError, "source or package-envelope"):
                CONTRACT.authority_manifest(payload, packet)

    def test_compatible_optional_field_and_incompatible_required_change(self) -> None:
        schema = CONTRACT.load_mapping(ROOT / CONTRACT.EXTERNAL_SCHEMA)
        model = copy.deepcopy(CONTRACT.record_model(schema, "completion", "1.3"))
        # A hand-authored minimal family proves compatibility without a generator oracle.
        old = {"type": "object", "properties": {"name": {"type": "string"}}, "required": ["name"], "additionalProperties": False}
        changed = copy.deepcopy(old)
        changed["properties"]["note"] = {"type": "string"}
        self.assertEqual([], CONTRACT.validate_model({"name": "kept"}, changed, "sample"))
        changed["required"].append("note")
        self.assertEqual(["sample.note is required"], CONTRACT.validate_model({"name": "kept"}, changed, "sample"))
        skeleton = CONTRACT.template_value(model)
        self.assertEqual("<required string>", skeleton["result"]["outcome"])
        self.assertEqual("<required integer or null>", skeleton["result"]["exit_code"])
        self.assertEqual("<required boolean>", skeleton["preflight"]["clean_worktree"])


class ArtifactBehaviorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temp = tempfile.TemporaryDirectory(prefix="execution-artifacts-")
        cls.root = Path(cls.temp.name).resolve()
        for ref in (*CONTRACT.AUTHORITY_REFS, ROLE, REVIEW_ROLE, SKILL):
            target = cls.root / ref
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / ref, target)
        (cls.root / ".gitignore").write_text(".dev/ai-context/local/\n__pycache__/\n", encoding="utf-8")
        (cls.root / ".dev/ai-context/local").mkdir(parents=True)
        for argv in (["init", "-q"], ["config", "user.email", "fixture@example.invalid"], ["config", "user.name", "Fixture"], ["add", "."], ["commit", "-qm", "fixture"]):
            subprocess.run(["git", "-C", str(cls.root), *argv], check=True, capture_output=True)
        cls.head = subprocess.check_output(["git", "-C", str(cls.root), "rev-parse", "HEAD"], text=True).strip()
        cls.tree = subprocess.check_output(["git", "-C", str(cls.root), "rev-parse", "HEAD^{tree}"], text=True).strip()
        cls.cli = CONTRACT.load_module(cls.root / ".ai/scripts/execution-artifacts.py", "artifact_cli_test")

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temp.cleanup()

    def setUp(self) -> None:
        self.ref = f".dev/ai-context/local/{self._testMethodName}"

    def request(self) -> dict:
        return {
            "schema_version": "1.0", "record_type": "execution-prepare-request",
            "delegation_id": "independent-test", "task_kind": "validation", "expected_commit_sha": self.head,
            "owning_skill": "ai-context-upgrader", "role": {"path": ROLE, "applicability": "applies", "reason": "Collect bounded test evidence."},
            "source": {"task_id_source": "explicit", "task_id": "parent-test", "final_integration_owner": "parent-test"},
            "objective": {"goal": "Run one bounded fixture command.", "non_goals": ["repair", "provider changes"]},
            "execution": {"working_directory": ".", "argv": ["python", "-c", "print('fixture')"], "timeout_seconds": 30},
            "network": "deny", "delivery": {"primary": "parent-event-wait", "fallback": "none"},
            "stop_conditions": ["terminal outcome", "subject drift"], "retry": {"attempt": 1, "budget": 2, "authorization_refs": []},
        }

    def observations(self, outcome: str = "failed") -> dict:
        return {
            "schema_version": "1.0", "record_type": "execution-observations", "source_task_id": "parent-test", "delegated_task_id": "child-test",
            "observed_commit_sha": self.head, "preflight": {"commit_matches": True, "clean_worktree": True},
            "execution": {"working_directory": ".", "argv": self.request()["execution"]["argv"]},
            "timing": {"started_at": "2026-09-20T00:00:00+00:00", "completed_at": "2026-09-20T00:00:02+00:00", "duration_seconds": 2},
            "result": {"outcome": outcome, "exit_code": 0 if outcome == "passed" else 1, "counts": None},
            "evidence": {"refs": ["fixture:independent-observation"], "bounded_output": "Explicit synthetic test observation, not production execution."},
            "final_state": {"clean_worktree": True, "tracked_changes": []}, "delivery_mode": "parent-event-wait",
        }

    def save(self, ref: str, record: dict) -> bytes:
        content = CONTRACT.encoded(record)
        (self.root / ref).write_bytes(content)
        return content

    def test_prepare_observes_git_and_binds_shared_request_once(self) -> None:
        result = self.cli.prepare(self.request(), self.ref)
        self.assertFalse(result["execution_observed"])
        packet = CONTRACT.load_mapping(self.root / result["packet_ref"])
        dispatch = CONTRACT.load_mapping(self.root / result["dispatch_ref"])
        self.assertEqual(self.head, dispatch["subject"]["commit_sha"])
        self.assertEqual(packet["subject"]["exact_sha"], dispatch["subject"]["commit_sha"])
        self.assertEqual(packet["invocation"]["argv"], dispatch["execution"]["argv"])
        self.assertIsNone(packet["review_input"])
        self.assertEqual("1.3", dispatch["schema_version"])
        _, external, _, schema = self.cli.validators()
        message = (self.root / result["dispatch_message_ref"]).read_text(encoding="utf-8")
        self.assertEqual(dispatch, external.extract_dispatch_from_prompt(message))
        self.assertEqual([], external.validate_dispatch(external.extract_dispatch_from_prompt(message), schema))
        self.assertEqual((self.root / result["dispatch_ref"]).read_bytes(), external.extract_exact_envelope_bytes(message, external.BEGIN_MARKER, external.END_MARKER, "dispatch"))
        with self.assertRaisesRegex(ValueError, "new output directory"):
            self.cli.prepare(self.request(), self.ref)

    def test_wrong_head_and_unknown_fields_batch_before_output(self) -> None:
        request = self.request(); request["expected_commit_sha"] = "0" * 40
        with self.assertRaisesRegex(ValueError, "observed HEAD"):
            self.cli.prepare(request, self.ref)
        self.assertFalse((self.root / self.ref).exists())
        request["execution"]["timeout_seconds"] = True; request["extra"] = "rejected"
        with self.assertRaises(ValueError) as failure:
            self.cli.prepare(request, self.ref)
        self.assertIn("unsupported fields: extra", str(failure.exception))
        self.assertIn("timeout_seconds must be integer", str(failure.exception))

    def test_late_packet_failure_rolls_back_exclusive_bundle(self) -> None:
        request = self.request(); request["network"] = "maybe"
        with self.assertRaisesRegex(ValueError, "permissions"):
            self.cli.prepare(request, self.ref)
        self.assertFalse((self.root / self.ref).exists())

    def test_output_escape_tracked_and_collision_refused(self) -> None:
        for ref in ("../escape", ".gitignore", ".dev/ai-context/local/../unsafe"):
            with self.subTest(ref=ref), self.assertRaises(ValueError):
                self.cli.prepare(self.request(), ref)

    def test_review_role_cannot_bypass_explicit_criteria_with_task_kind(self) -> None:
        request = self.request(); request["role"]["path"] = REVIEW_ROLE
        with self.assertRaisesRegex(ValueError, "explicit review_input"):
            self.cli.prepare(request, self.ref)
        self.assertFalse((self.root / self.ref).exists())

    def test_low_level_dispatch_cannot_downgrade_review_role_to_legacy_packet(self) -> None:
        result = self.cli.prepare(self.request(), self.ref)
        packet_path = self.root / result["packet_ref"]
        packet = CONTRACT.load_mapping(packet_path)
        packet["schema_version"] = "1.0"; del packet["review_input"]
        packet["role"]["path"] = REVIEW_ROLE
        packet["packet_sha256"] = CONTRACT.digest({key: value for key, value in packet.items() if key != "packet_sha256"})
        packet_bytes = self.save(result["packet_ref"], packet)
        dispatch = CONTRACT.load_mapping(self.root / result["dispatch_ref"])
        dispatch["execution_packet"]["packet_sha256"] = CONTRACT.sha256(packet_bytes)
        dispatch["authority_manifest"] = CONTRACT.authority_manifest(self.root, packet)
        _, external, _, schema = self.cli.validators()
        errors = external.validate_dispatch(dispatch, schema)
        self.assertTrue(any("current review dispatch requires packet 1.1" in error for error in errors))

    def test_cleanup_preserves_changed_bytes_and_reports_failure(self) -> None:
        directory = self.root / self.ref; directory.mkdir()
        path = directory / "owned.txt"; owned = []
        self.cli.exclusive_file(path, b"created", owned)
        path.write_bytes(b"changed-by-another-writer")
        with self.assertRaisesRegex(ValueError, "identity or bytes changed"):
            self.cli.rollback(owned, directory)
        self.assertEqual(b"changed-by-another-writer", path.read_bytes())

    def review_input(self) -> dict:
        classification = {"schema_version": "1.0", "record_type": "agent-execution-classification", "operation": "review", "execution_boundary": "external", "duration_class": "short", "change_domains": ["ordinary"], "snapshot": "isolated-immutable", "tracked_write": False, "provider_mutation": False, "credential_access": False, "terminal_gate": True}
        content = {"schema_version": "independent-review-subject/v1", "repository_id": "fixture", "base_tree": self.tree, "head_tree": self.tree}
        return {"schema_version": "1.0", "record_type": "independent-review-input", "classification": classification, "subject": {"repository": "fixture", "base_sha": self.head, "head_sha": self.head, "base_tree": self.tree, "head_tree": self.tree, "subject_digest": CONTRACT.digest(content)}, "criteria": ["Reject unsupported outcome promotion."], "authority": [{"path": ref, "sha256": CONTRACT.sha256((self.root / ref).read_bytes())} for ref in (CONTRACT.GUARD_SCHEMA, CONTRACT.GUARD_VALIDATOR)]}

    def test_terminal_expectation_uses_canonical_current_review_input(self) -> None:
        terminal = CONTRACT.load_module(ROOT / ".ai/scripts/validate-terminal-issue-closure.py", "artifact_terminal_test")
        terminal.ROOT = self.root
        review = self.review_input()
        input_ref = ".dev/ai-context/local/terminal-review-input.yaml"
        self.save(input_ref, review)
        path = self.root / input_ref
        expected = terminal.current_review_expectation(path, "fixture", self.head, self.head)
        self.assertEqual(CONTRACT.digest(review["criteria"]), expected["criteria_sha256"])
        self.assertEqual(CONTRACT.digest(sorted(review["authority"], key=lambda item: item["path"])), expected["authority_sha256"])
        review["authority"].reverse()
        self.save(input_ref, review)
        self.assertEqual(expected, terminal.current_review_expectation(path, "fixture", self.head, self.head))
        for repository, base, head in (("other", self.head, self.head), ("fixture", "0" * 40, self.head), ("fixture", self.head, "0" * 40)):
            with self.subTest(repository=repository, base=base, head=head):
                with self.assertRaisesRegex(ValueError, "bind the live repository, base and head"):
                    terminal.current_review_expectation(path, repository, base, head)
        review["authority"][0]["sha256"] = "0" * 64
        self.save(input_ref, review)
        with self.assertRaisesRegex(ValueError, "authority byte digest"):
            terminal.current_review_expectation(path, "fixture", self.head, self.head)
        with self.assertRaisesRegex(ValueError, "requires --review-input"):
            terminal.current_review_expectation(None, "fixture", self.head, self.head)

    def test_review_input_bytes_are_bound_and_mutation_rejected(self) -> None:
        review = self.review_input()
        input_ref = ".dev/ai-context/local/review-input.yaml"; self.save(input_ref, review)
        request = self.request(); request["role"]["path"] = REVIEW_ROLE; request["review_input"] = input_ref
        result = self.cli.prepare(request, self.ref)
        review["criteria"].append("Changed after preparation")
        self.save(f"{self.ref}/review-input.yaml", review)
        with self.assertRaisesRegex(ValueError, "byte digest"):
            self.cli.check(result["packet_ref"], None)
        with self.assertRaisesRegex(ValueError, "byte digest"):
            self.cli.check(result["dispatch_ref"], None)

    def test_failed_and_blocked_observations_remain_nonpassing_after_receipt(self) -> None:
        for outcome in ("failed", "blocked-by-environment", "timed-out", "interrupted"):
            ref = self.ref + "-" + outcome
            result = self.cli.prepare(self.request(), ref)
            finished = self.cli.finalize(self.observations(outcome), result["dispatch_ref"])
            self.assertEqual(outcome, finished["execution_outcome"])
            self.assertEqual("passed", finished["validator_outcome"])
            self.assertFalse(finished["execution_run_by_tool"])
            self.assertEqual("validated", self.cli.check(finished["receipt_ref"], result["dispatch_ref"])["state"])
            _, external, _, schema = self.cli.validators()
            dispatch_path = self.root / result["dispatch_ref"]
            message = (self.root / finished["terminal_message_ref"]).read_text(encoding="utf-8")
            self.assertEqual([], external.validate_terminal_delivery_message(message, schema, CONTRACT.load_mapping(dispatch_path), dispatch_path.read_bytes()))
            with self.assertRaisesRegex(ValueError, "existing candidate or receipt"):
                self.cli.finalize(self.observations(outcome), result["dispatch_ref"])

    def test_missing_observation_and_falsely_passed_result_do_not_create_receipt(self) -> None:
        result = self.cli.prepare(self.request(), self.ref)
        observation = self.observations(); del observation["timing"]["duration_seconds"]; del observation["result"]["exit_code"]
        with self.assertRaises(ValueError) as failure:
            self.cli.finalize(observation, result["dispatch_ref"])
        self.assertIn("duration_seconds is required", str(failure.exception)); self.assertIn("exit_code is required", str(failure.exception))
        observation = self.observations("passed"); observation["result"]["exit_code"] = 2
        with self.assertRaisesRegex(ValueError, "exit_code zero"):
            self.cli.finalize(observation, result["dispatch_ref"])
        observation = self.observations("passed")
        observation["timing"]["completed_at"] = "2026-09-19T23:59:59+00:00"
        with self.assertRaisesRegex(ValueError, "completed_at must not precede"):
            self.cli.finalize(observation, result["dispatch_ref"])
        self.assertFalse((self.root / self.ref / "candidate.yaml").exists())
        self.assertFalse((self.root / self.ref / "receipt.yaml").exists())

    def test_manifest_rejects_removed_dependency_and_helper_drift(self) -> None:
        result = self.cli.prepare(self.request(), self.ref)
        path = self.root / result["dispatch_ref"]; original = path.read_bytes()
        dispatch = CONTRACT.load_mapping(path); dispatch["authority_manifest"] = dispatch["authority_manifest"][:-1]
        self.save(result["dispatch_ref"], dispatch)
        with self.assertRaisesRegex(ValueError, "dependency set"):
            self.cli.check(result["dispatch_ref"], None)
        path.write_bytes(original)
        helper = self.root / ".ai/scripts/execution_artifact_contract.py"; old = helper.read_bytes()
        try:
            helper.write_bytes(old + b"\n# authority drift\n")
            with self.assertRaisesRegex(ValueError, "changed dependency"):
                self.cli.check(result["dispatch_ref"], None)
        finally:
            helper.write_bytes(old)

    def test_migration_is_explicit_preserves_failed_history_and_never_issues_receipt(self) -> None:
        prepared = self.cli.prepare(self.request(), self.ref)
        finished = self.cli.finalize(self.observations(), prepared["dispatch_ref"])
        candidate = CONTRACT.load_mapping(self.root / finished["candidate_ref"]); candidate["schema_version"] = "1.2"
        source_ref = f"{self.ref}/historical.yaml"; source_bytes = self.save(source_ref, candidate)
        preview = self.cli.migrate(source_ref, "1.3", None, prepared["dispatch_ref"])
        self.assertEqual("failed", preview["preview"]["result"]["outcome"])
        self.assertFalse(preview["receipt_created"])
        output_ref = self.ref + "-migrated"
        converted = self.cli.migrate(source_ref, "1.3", output_ref, prepared["dispatch_ref"])
        self.assertEqual(source_bytes, (self.root / source_ref).read_bytes())
        self.assertEqual(candidate["timing"], converted["preview"]["timing"])
        self.assertFalse((self.root / output_ref / "receipt.yaml").exists())
        with self.assertRaisesRegex(ValueError, "unsupported migration"):
            self.cli.migrate(finished["receipt_ref"], "1.3", None)

    def test_legacy_reader_is_not_a_fresh_writer_or_admission_downgrade(self) -> None:
        prepared = self.cli.prepare(self.request(), self.ref)
        dispatch = CONTRACT.load_mapping(self.root / prepared["dispatch_ref"])
        dispatch["schema_version"] = "1.2"; del dispatch["authority_manifest"]
        self.save(prepared["dispatch_ref"], dispatch)
        self.assertFalse(self.cli.check(prepared["dispatch_ref"], None, True)["admission"])
        with self.assertRaisesRegex(ValueError, "current 1.3"):
            self.cli.finalize(self.observations(), prepared["dispatch_ref"])
        _, external, _, _ = self.cli.validators()
        with self.assertRaisesRegex(ValueError, "current receipt writer"):
            external.build_validation_receipt({"schema_version": "1.2"}, dispatch, "", b"", "", b"", "")

    def test_cli_reports_batch_diagnostics_as_one_failed_preflight(self) -> None:
        ref = ".dev/ai-context/local/invalid-request.yaml"
        self.save(ref, {"schema_version": "1.0", "record_type": "execution-prepare-request"})
        result = subprocess.run([sys.executable, str(self.root / ".ai/scripts/execution-artifacts.py"), "prepare", "--request", ref, "--output", self.ref], cwd=self.root, capture_output=True, text=True)
        self.assertEqual(1, result.returncode)
        report = json.loads(result.stderr)
        # Review input is conditional on a review role; these fields are always required.
        for field in ("expected_commit_sha", "role", "execution", "retry"):
            self.assertTrue(any(field in error for error in report["errors"]), report["errors"])
        self.assertEqual("not-executed-by-this-tool", report["behavioral_outcome"])
        self.assertFalse((self.root / self.ref).exists())

    def test_generation_is_idempotent_and_contract_changes_affect_template_and_checker(self) -> None:
        schema_path = self.root / CONTRACT.EXTERNAL_SCHEMA
        original = schema_path.read_bytes()
        try:
            self.cli.templates(False)
            first = {ref: (self.root / ref).read_bytes() for ref in self.cli.TEMPLATES.values()}
            self.cli.templates(False)
            self.assertEqual(first, {ref: (self.root / ref).read_bytes() for ref in self.cli.TEMPLATES.values()})
            self.cli.templates(True)
            schema = CONTRACT.load_mapping(schema_path)
            model = schema["record_models"]["completion"]["1.3"]
            model["properties"]["explanation"] = {"type": "string"}
            schema_path.write_bytes(CONTRACT.encoded(schema))
            with self.assertRaisesRegex(ValueError, "template drift"):
                self.cli.templates(True)
            self.cli.templates(False)
            generated = CONTRACT.load_mapping(self.root / self.cli.TEMPLATES["completion"])
            self.assertIn("explanation", generated)
            # Compatible optional addition does not require old records to supply it.
            observation = self.observations()
            sample = {"schema_version": "1.3", "record_type": "external-task-completion", "delegation_id": "sample", "source_task_id": "parent-test", "delegated_task_id": "child-test", "subject": {"expected_commit_sha": self.head, "observed_commit_sha": self.head}, **{key: observation[key] for key in ("preflight", "execution", "timing", "result", "evidence", "final_state")}, "delivery": {"mode": "parent-event-wait", "destination": "source-task", "terminal_report_number": 1}}
            self.assertEqual([], CONTRACT.structure_errors(sample, schema, "completion"))
            model["required"].append("explanation")
            self.assertEqual(["completion.explanation is required"], CONTRACT.structure_errors(sample, schema, "completion"))
            schema_path.write_bytes(CONTRACT.encoded(schema))
            self.cli.templates(False)
            self.assertIn("explanation", CONTRACT.load_mapping(self.root / self.cli.TEMPLATES["completion"]))
        finally:
            schema_path.write_bytes(original)


if __name__ == "__main__":
    unittest.main()
