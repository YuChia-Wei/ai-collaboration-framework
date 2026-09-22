#!/usr/bin/env python3
"""Independent behavior expectations for artifact preparation, custody and migration."""
from __future__ import annotations

import copy
import datetime
import hashlib
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
import artifact_authoring as AUTHOR
import artifact_core as CORE

ROLE = ".ai/assets/sub-agent-role-prompts/mechanical-evidence-worker/sub-agent.yaml"
REVIEW_ROLE = ".ai/assets/sub-agent-role-prompts/fixed-head-independent-auditor/sub-agent.yaml"
SKILL = ".ai/assets/skills/ai-context-upgrader/skill.yaml"


class CoreCompatibilityTests(unittest.TestCase):
    def test_canonical_bytes_and_public_digest_facades_match_independent_oracle(self):
        value = {'z': [True, None, -1, 1.25], 'a': '臺灣'}
        expected = '{"a":"臺灣","z":[true,null,-1,1.25]}'.encode('utf-8')
        self.assertEqual(expected, CORE.canonical_json(value))
        self.assertEqual(expected, AUTHOR.canonical(value))
        self.assertEqual(hashlib.sha256(expected).hexdigest(), CONTRACT.digest(value))
        self.assertEqual(hashlib.sha256(expected).hexdigest(), AUTHOR.digest(expected))
        for invalid in (float('nan'), float('inf'), datetime.date(2026, 9, 21)):
            with self.subTest(invalid=invalid), self.assertRaises((ValueError, TypeError)):
                CORE.canonical_json({'value': invalid})

    def test_family_dialects_remain_distinct(self):
        self.assertEqual(1e-5, AUTHOR.parse('{"value":1e-5}')['value'])
        self.assertEqual('1e-5', yaml.load('{"value":1e-5}', Loader=CONTRACT.StrictLoader)['value'])
        cases = [('value: 2026-09-21', datetime.date(2026, 9, 21)),
                 ('value: !!str 42', '42'), ('value: &name text\ncopy: *name', 'text')]
        for text, expected in cases:
            with self.subTest(text=text):
                self.assertEqual(expected, yaml.load(text, Loader=CONTRACT.StrictLoader)['value'])
                with self.assertRaises(AUTHOR.AuthoringError): AUTHOR.parse(text)
        merged = 'base: &base {name: kept}\nvalue: {<<: *base, count: 2}'
        self.assertEqual({'name': 'kept', 'count': 2}, yaml.load(merged, Loader=CONTRACT.StrictLoader)['value'])
        with self.assertRaises(AUTHOR.AuthoringError): AUTHOR.parse(merged)
        self.assertTrue(str(yaml.load('value: .nan', Loader=CONTRACT.StrictLoader)['value']) == 'nan')
        with self.assertRaises(AUTHOR.AuthoringError): AUTHOR.parse('value: .nan')
        self.assertEqual({'x': 2}, yaml.safe_load('x: 1\nx: 2'))  # Global loader unchanged.

    def test_mapping_failures_preserve_adapter_diagnostics(self):
        for text in ('x: 1\nx: 2', 'nested: {x: 1, x: 2}'):
            with self.subTest(text=text):
                with self.assertRaisesRegex(yaml.YAMLError, 'duplicate mapping key'):
                    yaml.load(text, Loader=CONTRACT.StrictLoader)
                with self.assertRaisesRegex(AUTHOR.AuthoringError, 'duplicate/invalid key'):
                    AUTHOR.parse(text)
        with self.assertRaisesRegex(yaml.YAMLError, 'mapping keys must be strings'):
            yaml.load('1: value', Loader=CONTRACT.StrictLoader)
        with self.assertRaisesRegex(AUTHOR.AuthoringError, 'unique strings'):
            AUTHOR.parse('1: value')
        with self.assertRaisesRegex(AUTHOR.AuthoringError, 'duplicate key'):
            AUTHOR.parse('{"x":1,"x":2}')
        for text in ('value: [unfinished', 'value: "unfinished', '- list'):
            with self.subTest(text=text), self.assertRaises(AUTHOR.AuthoringError): AUTHOR.parse(text)

    def test_scalar_hashes_are_data_in_lf_and_crlf_yaml(self):
        cases = [('value: "Discuss #42"', 'Discuss #42'), ("value: 'it''s #42'", "it's #42"),
                 ('value: "quoted \\"#42\\""', 'quoted "#42"'),
                 ('value: https://example.invalid/a#fragment', 'https://example.invalid/a#fragment'),
                 ('value: C#', 'C#'), ('value: |\n  # 臺灣😀\n', '# 臺灣😀\n'),
                 ('value: >-\n  # first\n  second\n', '# first second'),
                 ('value: |2-\n  # literal\n', '# literal')]
        for text, expected in cases:
            for ending in ('\n', '\r\n'):
                with self.subTest(text=text, ending=ending):
                    self.assertEqual(expected, AUTHOR.parse(text.replace('\n', ending), refuse_yaml_comments=True)['value'])
        for text in ('value: ["# literal", C#]', '"# key": {value: "# literal"}',
                     'value: "line one\n  # line two"', 'value: first\n  abc#fragment'):
            with self.subTest(text=text):
                self.assertEqual(yaml.safe_load(text), AUTHOR.parse(text, refuse_yaml_comments=True))

    def test_actual_comments_and_malformed_yaml_are_refused(self):
        cases = ['# leading\nvalue: kept', 'value: kept\n# trailing', 'value: kept # inline',
                 'value: "# data"# comment', 'value: [one, # comment\n two]',
                 'value: | # header\n  # data\n', 'value: >- # header',
                 'value: |\n  # data\n# outside\n', '%YAML 1.1 # directive\n---\nvalue: kept',
                 'value: kept\n... # end']
        for text in cases:
            for ending in ('\n', '\r\n'):
                with self.subTest(text=text, ending=ending), self.assertRaisesRegex(AUTHOR.AuthoringError, 'YAML comments'):
                    AUTHOR.parse(text.replace('\n', ending), refuse_yaml_comments=True)
        for text in ('value: ["# literal"', 'value: "# literal', 'value: |\n # data\ninvalid: ['):
            with self.subTest(text=text), self.assertRaises(AUTHOR.AuthoringError):
                AUTHOR.parse(text, refuse_yaml_comments=True)


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

    def test_execution_cli_isolated_package_imports_and_template_bytes(self):
        with tempfile.TemporaryDirectory(prefix='execution-package-') as temporary:
            envelope = Path(temporary).resolve(); payload = envelope / 'payload'
            templates = ['.ai/assets/skills/software-development-orchestrator/templates/' + name
                         for name in ('external-task-dispatch.template.yaml', 'external-task-completion.template.yaml',
                                      'execution-prepare-request.template.yaml', 'execution-observations.template.yaml')]
            for ref in (*CONTRACT.AUTHORITY_REFS, *templates):
                target = payload / ref; target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / ref, target)
            (payload / 'requirements.txt').replace(envelope / 'requirements.txt')
            command = [sys.executable, '-I', '-B', str(payload / '.ai/scripts/execution-artifacts.py'), 'templates', '--check']
            result = subprocess.run(command, cwd=envelope, capture_output=True, text=True)
            self.assertEqual(0, result.returncode, result.stderr)
            self.assertEqual({'operation': 'templates', 'state': 'current'}, json.loads(result.stdout))
            (payload / '.ai/scripts/artifact_core.py').unlink()
            missing = subprocess.run(command, cwd=envelope, capture_output=True, text=True)
            self.assertNotEqual(0, missing.returncode)
            self.assertIn('artifact_core', missing.stderr)


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
        for name in ('execution_artifact_contract.py', 'artifact_core.py'):
            helper = self.root / '.ai/scripts' / name; old = helper.read_bytes()
            try:
                helper.write_bytes(old + b"\n# authority drift\n")
                with self.subTest(helper=name), self.assertRaisesRegex(ValueError, "changed dependency"):
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


class InputAuthoringTests(unittest.TestCase):
    setUpClass = classmethod(ArtifactBehaviorTests.setUpClass.__func__)
    tearDownClass = classmethod(ArtifactBehaviorTests.tearDownClass.__func__)
    setUp = ArtifactBehaviorTests.setUp

    def review_request(self):
        return {"version": "1.0", "expected_head": self.head, "repository": "fixture-repository", "base_sha": self.head,
                "classification": {"schema_version": "1.0", "record_type": "agent-execution-classification", "operation": "review",
                    "execution_boundary": "same-runtime", "duration_class": "short", "change_domains": ["ordinary"],
                    "snapshot": "isolated-immutable", "tracked_write": False, "provider_mutation": False,
                    "credential_access": False, "terminal_gate": False},
                "criteria": ["Preserve the accepted behavior."], "authority_paths": [CONTRACT.GUARD_SCHEMA]}

    def test_review_input_derives_current_subject_and_authority_without_admission(self):
        request = self.review_request()
        preview = self.cli.author_input("review-input", request)
        record = preview["record"]
        content = {"schema_version": "independent-review-subject/v1", "repository_id": "fixture-repository", "base_tree": self.tree, "head_tree": self.tree}
        expected = hashlib.sha256(json.dumps(content, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
        self.assertEqual(expected, record["subject"]["subject_digest"])
        self.assertEqual(hashlib.sha256((self.root / CONTRACT.GUARD_SCHEMA).read_bytes()).hexdigest(), record["authority"][0]["sha256"])
        self.assertFalse(preview["admission_granted"])
        self.assertFalse((self.root / self.ref).exists())
        result = self.cli.author_input("review-input", request, self.ref, preview["preview_digest"])
        self.assertEqual("authored", result["state"])
        self.assertEqual(record, CONTRACT.load_mapping(self.root / self.ref))
        with self.assertRaisesRegex(ValueError, "new file"):
            self.cli.author_input("review-input", request, self.ref, preview["preview_digest"])

    def test_refuses_wrong_subject_unknown_fields_and_protected_observations(self):
        for key, value in (("expected_head", "0" * 40), ("version", "2.0"), ("execution_passed", True)):
            request = self.review_request(); request[key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                self.cli.author_input("review-input", request)
        request = self.review_request(); request["classification"]["tracked_write"] = True
        with self.assertRaisesRegex(ValueError, "read-only"):
            self.cli.author_input("review-input", request)
        request = self.review_request(); request["authority_paths"] *= 2
        with self.assertRaisesRegex(ValueError, "unique"):
            self.cli.author_input("review-input", request)

    def test_review_rejects_tree_as_commit_and_runtime_drift(self):
        request = self.review_request(); request["base_sha"] = self.tree
        with self.assertRaisesRegex(ValueError, "must name commits"):
            self.cli.author_input("review-input", request)
        request = self.review_request(); preview = self.cli.author_input("review-input", request)
        path = self.root / ".ai/scripts/execution_artifact_contract.py"
        original = path.read_bytes()
        try:
            path.write_bytes(original + b"\n")
            with self.assertRaisesRegex(ValueError, "clean tracked HEAD"):
                self.cli.author_input("review-input", request, self.ref, preview["preview_digest"])
        finally:
            path.write_bytes(original)

    def test_current_input_cli_preview_then_explicit_create(self):
        source = self.root / (self.ref + "-request.yaml")
        source.write_bytes(CONTRACT.encoded(self.review_request()))
        command = [sys.executable, "-B", str(self.root / ".ai/scripts/execution-artifacts.py"), "input", "--kind", "review-input", "--request", str(source)]
        first = subprocess.run(command, capture_output=True, text=True)
        self.assertEqual(0, first.returncode, first.stderr)
        preview = json.loads(first.stdout)
        missing = subprocess.run(command + ["--output", self.ref], capture_output=True, text=True)
        self.assertNotEqual(0, missing.returncode)
        self.assertFalse((self.root / self.ref).exists())
        created = subprocess.run(command + ["--output", self.ref, "--expect", preview["preview_digest"]], capture_output=True, text=True)
        self.assertEqual(0, created.returncode, created.stderr)
        self.assertFalse(json.loads(created.stdout)["admission_granted"])

    def test_preview_binds_criteria_and_refuses_unsafe_or_tracked_outputs(self):
        request = self.review_request()
        preview = self.cli.author_input("review-input", request)
        changed = copy.deepcopy(request); changed["criteria"] = ["Changed acceptance criteria."]
        with self.assertRaisesRegex(ValueError, "preview changed"):
            self.cli.author_input("review-input", changed, self.ref, preview["preview_digest"])
        for ref in ("../outside.yaml", CONTRACT.GUARD_SCHEMA, self.ref + "/../escape.yaml"):
            with self.subTest(ref=ref), self.assertRaises(ValueError):
                self.cli.author_input("review-input", request, ref, preview["preview_digest"])
        self.assertFalse((self.root / self.ref).exists())

    def test_dependency_request_never_runs_callable_and_binds_dependency_bytes(self):
        refs = (".ai/scripts/observe-validation-dependencies.py", ".ai/assets/shared/validation-dependency-observation.schema.yaml")
        for ref in refs:
            target = self.root / ref; target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / ref, target)
        dependency = ".dev/ai-context/local/observed.py"
        (self.root / dependency).write_text("def check():\n    raise RuntimeError('must not execute')\n")
        request = {"version": "1.0", "expected_head": self.head, "validator_id": "bounded-input",
                   "harness": "in-process-python-callable/v1", "entrypoint": dependency, "callable": "check", "argv": [],
                   "declared_dependencies": {"file": [dependency], "subprocess": [], "git": [], "environment": [], "runtime": ["python"]}}
        preview = self.cli.author_input("dependency-request", request)
        self.assertEqual(self.head, preview["record"]["subject"])
        (self.root / dependency).write_text("def check():\n    return False\n")
        with self.assertRaisesRegex(ValueError, "preview changed"):
            self.cli.author_input("dependency-request", request, self.ref, preview["preview_digest"])

    def test_prepare_request_preserves_explicit_inputs_and_does_not_create_dispatch(self):
        original = ArtifactBehaviorTests.request(self)
        request = {key: value for key, value in original.items() if key not in {"schema_version", "record_type", "expected_commit_sha"}}
        request.update(version="1.0", expected_head=self.head)
        preview = self.cli.author_input("prepare-request", request)
        self.assertEqual(original, preview["record"])
        self.assertFalse((self.root / self.ref).exists())
        request["role"] = False
        with self.assertRaises(ValueError):
            self.cli.author_input("prepare-request", request)

    def test_ledger_binds_document_bytes_and_never_promotes_synthetic_evidence(self):
        document = ".dev/ai-context/local/ledger-source.txt"
        (self.root / document).write_bytes(b"Observed limitation; no execution result.\n")
        entry = {"acceptance_id": "AC-1", "issue": 320, "requires_actual_execution": False, "evidence_kind": "document",
                 "command": "read retained report", "profile": "document", "outcome": "blocked", "evidence_ref": "ignored:" + document}
        request = {"version": "1.0", "expected_head": self.head, "entries": [entry]}
        preview = self.cli.author_input("evidence-ledger", request)
        record = preview["record"]
        self.assertEqual("blocked", record["human_report"]["entries"][0]["outcome"])
        self.assertEqual(hashlib.sha256((self.root / document).read_bytes()).hexdigest(), record["entries"][0]["evidence_sha256"])
        self.assertIsNone(record["entries"][0]["execution_receipt"])
        entry["requires_actual_execution"] = True
        with self.assertRaisesRegex(ValueError, "cannot satisfy"):
            self.cli.author_input("evidence-ledger", request)
        entry["requires_actual_execution"] = False; entry["issue"] = True
        with self.assertRaisesRegex(ValueError, "integer"):
            self.cli.author_input("evidence-ledger", request)

    def test_publication_drift_cleans_only_own_unchanged_output(self):
        from unittest.mock import patch
        request = self.review_request(); preview = self.cli.author_input("review-input", request)
        observed = self.cli.observed_git()
        with patch.object(self.cli, "observed_git", side_effect=[observed, observed, {**observed, "tracked_status": " M changed"}]):
            with self.assertRaisesRegex(ValueError, "drifted during input publication"):
                self.cli.author_input("review-input", request, self.ref, preview["preview_digest"])
        self.assertFalse((self.root / self.ref).exists())

    def test_ledger_reads_existing_failed_receipt_without_reissuing_or_promoting_it(self):
        output = self.ref + "-output.txt"; receipt_ref = self.ref + "-receipt.yaml"
        (self.root / output).write_bytes(b"Synthetic fixture for a failed execution receipt.\n")
        output_sha = hashlib.sha256((self.root / output).read_bytes()).hexdigest()
        receipt = {"schema_version": "1.0", "record_type": "terminal-command-execution", "producer": "local-command-runner",
                   "subject_sha": self.head, "command": "fixture-command", "profile": "fixture-profile",
                   "started_at": "2026-09-22T00:00:00+00:00", "completed_at": "2026-09-22T00:00:01+00:00",
                   "duration_seconds": 1, "executed": True, "synthetic": False, "outcome": "failed", "exit_code": 1,
                   "evidence_refs": ["ignored:" + output], "evidence_sha256": output_sha}
        receipt["receipt_sha256"] = hashlib.sha256(json.dumps(receipt, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
        raw_receipt = CONTRACT.encoded(receipt); (self.root / receipt_ref).write_bytes(raw_receipt)
        entry = {"acceptance_id": "AC-fixture", "issue": 320, "requires_actual_execution": True, "evidence_kind": "actual-execution",
                 "command": "fixture-command", "profile": "fixture-profile", "outcome": "failed", "evidence_ref": "ignored:" + output,
                 "execution_receipt_ref": "ignored:" + receipt_ref}
        request = {"version": "1.0", "expected_head": self.head, "entries": [entry]}
        preview = self.cli.author_input("evidence-ledger", request)
        self.assertEqual(receipt, preview["record"]["entries"][0]["execution_receipt"])
        self.assertEqual(raw_receipt, (self.root / receipt_ref).read_bytes())
        entry["outcome"] = "passed"
        with self.assertRaisesRegex(ValueError, "does not bind"):
            self.cli.author_input("evidence-ledger", request)
        entry["outcome"] = "failed"; (self.root / output).write_bytes(b"Changed fixture bytes.\n")
        with self.assertRaises(ValueError): self.cli.author_input("evidence-ledger", request, self.ref, preview["preview_digest"])
        self.assertFalse((self.root / self.ref).exists())

    def test_fixed_package_envelope_requirements_cannot_be_selected_as_user_input(self):
        from unittest.mock import patch
        with tempfile.TemporaryDirectory(prefix="input-envelope-") as directory:
            envelope = Path(directory).resolve(); payload = envelope / "payload"; payload.mkdir()
            (envelope / "requirements.txt").write_bytes(b"PyYAML==6.0.2\n")
            _, external, _, _ = self.cli.validators()
            with patch.object(self.cli, "ROOT", payload):
                self.assertEqual(b"PyYAML==6.0.2\n", self.cli.input_authority_bytes("package-envelope:requirements.txt", external))
                with self.assertRaises(ValueError): self.cli.input_file("package-envelope:requirements.txt", {}, external)
                (payload / "requirements.txt").write_bytes(b"different\n")
                with self.assertRaisesRegex(ValueError, "authority changed"):
                    self.cli.input_authority_bytes("package-envelope:requirements.txt", external)


if __name__ == "__main__":
    unittest.main()
