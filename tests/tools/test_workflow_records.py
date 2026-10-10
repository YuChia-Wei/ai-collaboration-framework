"""Real Git/filesystem and CLI evidence for the selected current workflow slice."""
from __future__ import annotations

import copy
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import yaml

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from workflow_records import WorkflowRecords
from workflow_records import git_store
from workflow_records.contracts import MAX_FILE, VERSION, RecordError, decode_json, encoded
from workflow_records.service import DEFAULT_CONFIG

WORKFLOW = "2026-10-02-skill-routing"
REF = {"provider_id": "git", "store_id": "project-workflows", "workflow_id": WORKFLOW}
CLI = ROOT / "tools/workflow-records.py"
ASSESSMENT_CLI = ROOT / "tools/maintenance/validate-assessment-artifacts.py"
CHECKPOINT = {"summary": "已完成來源盤點", "authority": "Selected fixture owner",
              "completed": ["Read the current plan"], "pending": ["Review findings"],
              "blockers": [], "evidence": ["fixture:observed"], "next_action": "Review findings with the owner"}


def git(root, *args):
    result = subprocess.run(["git", "-C", str(root), *args], capture_output=True, timeout=15)
    if result.returncode:
        raise AssertionError(result.stderr.decode(errors="replace"))
    return result.stdout.decode().strip()


class WorkflowRecordTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.baseline_temp = tempfile.TemporaryDirectory(prefix="workflow-record-baseline-")
        cls.baseline = Path(cls.baseline_temp.name)
        target = cls.baseline / ".dev/workflows" / WORKFLOW
        shutil.copytree(ROOT / ".dev/workflows" / WORKFLOW, target)
        git(cls.baseline, "init", "--initial-branch=fixture")
        git(cls.baseline, "add", ".")
        git(cls.baseline, "-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
            "-c", "commit.gpgsign=false", "-c", "core.hooksPath=empty-hooks",
            "commit", "-m", "fixture")

    @classmethod
    def tearDownClass(cls):
        cls.baseline_temp.cleanup()

    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="workflow-record-case-")
        self.addCleanup(self.temporary.cleanup)
        self.project = Path(self.temporary.name) / "project"
        shutil.copytree(self.baseline, self.project)
        self.artifact = self.project / ".dev/workflows" / WORKFLOW
        self.service = WorkflowRecords(self.project)
        self.original = {p.relative_to(self.artifact): p.read_bytes()
                         for p in self.artifact.rglob("*") if p.is_file()}

    def request(self, operation, **extra):
        result = {"contract_version": VERSION, "operation": operation}
        if operation not in ("find", "capabilities"):
            result["workflow_ref"] = REF.copy()
        result.update(extra)
        return result

    def run_operation(self, operation, **extra):
        return self.service.execute(self.request(operation, **extra))

    def checkpoint_request(self, operation_id="cp-1"):
        context = self.run_operation("context")
        self.assertEqual(context["status"], "ok", context)
        return self.request("checkpoint", checkpoint=copy.deepcopy(CHECKPOINT), operation_id=operation_id,
                            expected_revision=context["result"]["revision"],
                            expected_source_head=context["result"]["source_head"])

    def assert_original_preserved(self):
        for relative, raw in self.original.items():
            self.assertEqual((self.artifact / relative).read_bytes(), raw, str(relative))

    def assert_error(self, response, code):
        self.assertNotEqual(response["status"], "ok", response)
        self.assertEqual(response["error"]["code"], code, response)

    def launch(self, request, name="request.json"):
        path = Path(self.temporary.name) / name
        path.write_bytes(request if isinstance(request, bytes) else encoded(request))
        completed = subprocess.run([sys.executable, "-I", "-B", str(CLI), "--root", str(self.project),
                                    "--request", str(path)], capture_output=True, timeout=20)
        self.assertEqual(completed.stderr, b"")
        return completed.returncode, json.loads(completed.stdout)

    def test_real_cli_find_read_checkpoint_receipt_and_resume_preserve_existing_bytes(self):
        code, response = self.launch(self.request("find"))
        self.assertEqual(code, 0)
        self.assertEqual(response["result"]["items"][0]["workflow_ref"], REF)
        code, context = self.launch(self.request("context"))
        self.assertEqual(code, 0)
        entrypoint = context["result"]["entrypoint"]
        code, document = self.launch(self.request("read", **entrypoint, limit=32768))
        self.assertEqual(code, 0)
        self.assertEqual(document["result"]["content"], self.original[Path("workflow-plan.md")].decode("utf-8"))
        request = self.checkpoint_request()
        code, written = self.launch(request)
        self.assertEqual(code, 0)
        self.assertEqual(written["result"]["state"], "applied")
        code, receipt = self.launch(self.request("operation", operation_id="cp-1"))
        self.assertEqual(receipt["result"]["checkpoint_revision"], written["result"]["checkpoint_revision"])
        code, resumed = self.launch(self.request("resume"))
        self.assertEqual(code, 0)
        self.assertEqual(resumed["result"]["checkpoint"]["next_action"]["text"], CHECKPOINT["next_action"])
        self.assertIn("Skill responsibility routing", resumed["result"]["plan"]["content"])
        self.assertNotEqual(resumed["result"]["revision"], request["expected_revision"])
        self.assert_original_preserved()
        self.assertEqual(git(self.project, "diff", "--name-only"), "")

    def test_revision_includes_tasks_plan_locator_and_checkpoint_not_unrelated_documents(self):
        request = self.checkpoint_request()
        (self.artifact / "workflow-plan.md").write_text("changed plan", encoding="utf-8")
        self.assert_error(self.service.execute(request), "revision_conflict")
        self.assertFalse((self.artifact / ".workflow-records/checkpoint.json").exists())
        request = self.checkpoint_request()
        task = self.artifact / "tasks/T1.json"
        task.write_bytes(task.read_bytes() + b"\n")
        self.assert_error(self.service.execute(request), "revision_conflict")
        request = self.checkpoint_request()
        (self.artifact / "unrelated-evidence.md").write_text("new evidence", encoding="utf-8")
        self.assertEqual(self.service.execute(request)["status"], "ok")

    def test_document_revision_and_truncation_are_explicit(self):
        response = self.run_operation("read", document="workflow-plan.md", limit=5)
        self.assertEqual(response["result"]["content"], "# Ski")
        self.assertTrue(response["result"]["truncated"])
        self.assertEqual(response["result"]["next_offset"], 5)
        self.assert_error(self.run_operation("read", document="workflow-plan.md", revision="sha256:stale"), "revision_conflict")
        context = self.run_operation("context", task_limit=1)
        self.assertTrue(context["result"]["tasks_truncated"])
        self.assertFalse(context["result"]["documents_loaded"])

    def test_retry_recovers_same_operation_and_rejects_reused_id(self):
        request = self.checkpoint_request()
        first = self.service.execute(request)
        replay = self.service.execute(request)
        self.assertEqual(first["status"], "ok")
        self.assertTrue(replay["result"]["replayed"])
        self.assertEqual(first["result"]["checkpoint_revision"], replay["result"]["checkpoint_revision"])
        request["checkpoint"]["summary"] = "different request"
        self.assert_error(self.service.execute(request), "operation_id_conflict")
        self.assertEqual(self.run_operation("operation", operation_id="unknown")["result"]["state"], "unknown")

    def test_history_preserves_older_receipts_and_refuses_compaction_at_capacity(self):
        first = self.service.execute(self.checkpoint_request("first"))
        self.assertEqual(self.service.execute(self.checkpoint_request("second"))["status"], "ok")
        self.assertEqual(self.run_operation("operation", operation_id="first")["result"]["checkpoint_revision"],
                         first["result"]["checkpoint_revision"])
        before = (self.artifact / ".workflow-records/checkpoint.json").read_bytes()
        with patch.object(git_store, "MAX_OPERATIONS", 2):
            self.assert_error(self.service.execute(self.checkpoint_request("third")), "limit_exceeded")
        self.assertEqual((self.artifact / ".workflow-records/checkpoint.json").read_bytes(), before)

    def test_git_source_change_refuses_write_even_if_record_bytes_match(self):
        request = self.checkpoint_request()
        request["expected_source_head"] = "0" * 40
        self.assert_error(self.service.execute(request), "source_conflict")
        self.assert_original_preserved()

    def test_two_real_cli_writers_apply_at_most_one_checkpoint(self):
        request = self.checkpoint_request()
        request_path = Path(self.temporary.name) / "concurrent.json"
        request_path.write_bytes(encoded(request))
        other_path = Path(self.temporary.name) / "concurrent-other.json"
        request["operation_id"] = "other"
        other_path.write_bytes(encoded(request))
        processes = [subprocess.Popen([sys.executable, "-I", "-B", str(CLI), "--root", str(self.project),
                                      "--request", str(path)], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                     for path in (request_path, other_path)]
        responses = []
        for process in processes:
            output, error = process.communicate(timeout=20)
            self.assertEqual(error, b"")
            responses.append(json.loads(output))
        self.assertEqual(sum(r["status"] == "ok" for r in responses), 1)
        failed = next(r for r in responses if r["status"] != "ok")
        self.assertIn(failed["error"]["code"], ("writer_busy", "revision_conflict"))
        self.assert_original_preserved()

    def test_external_lock_is_not_stolen(self):
        request = self.checkpoint_request()
        folder = self.artifact / ".workflow-records"
        folder.mkdir()
        (folder / "writer.lock").write_bytes(b"existing owner")
        self.assert_error(self.service.execute(request), "writer_busy")
        self.assertEqual((folder / "writer.lock").read_bytes(), b"existing owner")
        self.assert_original_preserved()

    def test_replace_failure_preserves_prior_checkpoint_and_cleans_own_temporary_files(self):
        self.service.execute(self.checkpoint_request())
        path = self.artifact / ".workflow-records/checkpoint.json"
        before = path.read_bytes()
        request = self.checkpoint_request("next")
        with patch.object(git_store.os, "replace", side_effect=OSError("injected before replace")):
            response = self.service.execute(request)
        self.assert_error(response, "io_error")
        self.assertEqual(path.read_bytes(), before)
        self.assertEqual(sorted(p.name for p in path.parent.iterdir()), ["checkpoint.json"])

    def test_lost_ack_after_real_replace_has_recoverable_receipt(self):
        request = self.checkpoint_request()
        real_replace = git_store.os.replace

        def replace_then_lose_ack(source, target):
            real_replace(source, target)
            raise OSError("injected acknowledgement loss")

        with patch.object(git_store.os, "replace", side_effect=replace_then_lose_ack):
            response = self.service.execute(request)
        self.assert_error(response, "io_error")
        self.assertEqual(response["mutation_state"], "unknown")
        self.assertEqual(self.run_operation("operation", operation_id="cp-1")["result"]["state"], "applied")
        self.assertTrue(self.service.execute(request)["result"]["replayed"])

    def test_missing_and_malformed_records_never_become_empty_success(self):
        locator = self.artifact / "workflow.yaml"
        original = locator.read_bytes()
        for content, expected in ((b"schema_version: [", "malformed_record"),
                                  (b"schema_version: '999'\n", "unsupported_version"),
                                  (b"schema_version: '1.0'\nschema_version: '1.0'\n", "malformed_record")):
            with self.subTest(expected=expected, content=content):
                locator.write_bytes(content)
                self.assert_error(self.run_operation("context"), expected)
                listing = self.run_operation("find")
                self.assertFalse(listing["result"]["complete"])
                self.assertEqual(listing["result"]["items"][0]["error"]["code"], expected)
        locator.write_bytes(original)
        (self.artifact / "workflow-plan.md").unlink()
        self.assert_error(self.run_operation("context"), "not_found")

    def test_task_identity_malformed_json_and_duplicate_keys_are_rejected(self):
        path = self.artifact / "tasks/T1.json"
        value = json.loads(path.read_bytes())
        value["workflow_id"] = "another-workflow"
        path.write_bytes(encoded(value))
        self.assert_error(self.run_operation("validate"), "malformed_record")
        path.write_bytes(b'{"task_id": "T1", "task_id":"T2"}')
        self.assert_error(self.run_operation("validate"), "malformed_record")

    def test_missing_tasks_are_marked_and_cannot_be_checkpointed(self):
        request = self.checkpoint_request()
        for path in (self.artifact / "tasks").iterdir():
            path.unlink()
        response = self.run_operation("context")
        self.assertEqual(response["result"]["missing"], ["tasks"])
        self.assert_error(self.run_operation("validate"), "not_found")
        request["expected_revision"] = response["result"]["revision"]
        self.assert_error(self.service.execute(request), "not_found")

    def test_unsafe_document_and_artifact_paths_are_rejected(self):
        for path in ("../outside", "/absolute", "C:/secret", "a:stream", "\\\\host\\share", "a/../b", "CON", "a./x", ".git/config"):
            with self.subTest(path=path):
                self.assert_error(self.run_operation("read", document=path), "unsafe_path")
        locator_path = self.artifact / "workflow.yaml"
        locator = yaml.safe_load(locator_path.read_text(encoding="utf-8"))
        locator["artifact_root"] = "../outside"
        locator_path.write_text(yaml.safe_dump(locator), encoding="utf-8")
        self.assert_error(self.run_operation("context"), "unsafe_path")

    def test_reparse_detection_is_applied_to_each_existing_path_component(self):
        original_stat = Path.lstat
        target = self.artifact / "workflow-plan.md"

        class ReparseStat:
            st_mode = 0o100644
            st_file_attributes = 0x400

        def observed_stat(path, *args, **kwargs):
            return ReparseStat() if path == target else original_stat(path, *args, **kwargs)

        # This is controlled metadata evidence, not an OS symlink/junction acceptance claim.
        with patch.object(Path, "lstat", observed_stat):
            self.assert_error(self.run_operation("context"), "unsafe_path")

    def test_default_change_keeps_explicit_git_ref_and_remote_never_falls_back(self):
        config = copy.deepcopy(DEFAULT_CONFIG)
        config["stores"]["board"] = {"kind": "remote", "store_id": "board-records"}
        config["default_provider"] = "board"
        selected = WorkflowRecords(self.project, config)
        self.assertEqual(selected.execute(self.request("context"))["status"], "ok")
        self.assertEqual(selected.reference(WORKFLOW), REF)
        self.assert_error(selected.execute(self.request("find")), "provider_unavailable")
        request = self.checkpoint_request()
        request["workflow_ref"] = {"provider_id": "board", "store_id": "board-records", "workflow_id": WORKFLOW}
        self.assert_error(selected.execute(request), "provider_unavailable")
        self.assertFalse((self.artifact / ".workflow-records").exists())
        self.assert_original_preserved()

    def test_checkpoint_binding_cannot_be_reinterpreted_as_another_store(self):
        self.assertEqual(self.service.execute(self.checkpoint_request())["status"], "ok")
        config = copy.deepcopy(DEFAULT_CONFIG)
        config["stores"]["git"]["store_id"] = "different"
        service = WorkflowRecords(self.project, config)
        request = self.request("context", workflow_ref=service.reference(WORKFLOW))
        self.assert_error(service.execute(request), "binding_mismatch")
        self.assert_error(service.execute(self.request("context")), "binding_mismatch")

    def test_limits_versions_unknown_fields_and_capabilities(self):
        self.assert_error(self.run_operation("context", contract_version="other"), "unsupported_version")
        self.assert_error(self.run_operation("create"), "unsupported_capability")
        self.assert_error(self.run_operation("context", surprise=True), "invalid_input")
        self.assert_error(self.run_operation("read", document="workflow-plan.md", limit=True), "invalid_input")
        response = self.run_operation("capabilities")
        self.assertFalse(response["result"]["providers"]["git"]["create"])
        self.assert_error(self.run_operation("resume", limit=32768, max_output_bytes=2048), "limit_exceeded")
        (self.artifact / "large.md").write_bytes(b"x" * (MAX_FILE + 1))
        self.assert_error(self.run_operation("read", document="large.md"), "limit_exceeded")

    def test_malformed_operation_and_timestamp_keep_errors_bounded_and_writes_absent(self):
        for operation in ([], "x" * 70000):
            result = self.service.execute({"contract_version": VERSION, "operation": operation})
            self.assert_error(result, "invalid_input")
            self.assertLess(len(encoded(result)), 2048)
        task = self.artifact / "tasks/T1.json"
        value = json.loads(task.read_bytes())
        value["created_at"] = "2026-10-10T11:46+08:00"
        task.write_bytes(encoded(value))
        self.assert_error(self.run_operation("validate"), "malformed_record")
        self.assertFalse((self.artifact / ".workflow-records").exists())

    def test_real_cli_rejects_escaped_surrogates_without_tracebacks_or_writes(self):
        requests = [self.request("\ud800"), self.request("\udfff")]
        checkpoint = self.checkpoint_request()
        checkpoint["checkpoint"]["summary"] = "invalid \ud800 text"
        requests.append(checkpoint)
        requests.append({"contract_version": VERSION, "operation": "capabilities", "\ud800": []})
        for request in requests:
            with self.subTest(request=request):
                raw = json.dumps(request, ensure_ascii=True).encode("ascii")
                code, response = self.launch(raw)
                self.assertEqual(code, 1)
                self.assert_error(response, "malformed_record")
                self.assertEqual(response["mutation_state"], "none")
                self.assertLess(len(encoded(response)), 2048)
                direct = self.service.execute(request)
                self.assert_error(direct, "invalid_input")
                self.assertEqual(direct["mutation_state"], "none")
                self.assertLess(len(encoded(direct)), 2048)
        self.assertFalse((self.artifact / ".workflow-records").exists())
        self.assert_original_preserved()
        valid = self.checkpoint_request()
        valid["checkpoint"]["summary"] = "Valid Unicode \U0001f600"
        code, response = self.launch(json.dumps(valid, ensure_ascii=True).encode("ascii"))
        self.assertEqual(code, 0, response)
        self.assertEqual(self.run_operation("resume")["result"]["checkpoint"]["summary"]["text"],
                         valid["checkpoint"]["summary"])

    def test_escaped_surrogate_in_yaml_record_is_malformed(self):
        locator = self.artifact / "workflow.yaml"
        value = yaml.safe_load(locator.read_bytes())
        value["title"] = "\ud800"
        locator.write_text(yaml.safe_dump(value, allow_unicode=False), encoding="utf-8")
        self.assert_error(self.run_operation("context"), "malformed_record")
        self.assertFalse((self.artifact / ".workflow-records").exists())

    def test_configuration_rejects_ambiguous_roots(self):
        config = copy.deepcopy(DEFAULT_CONFIG)
        config["stores"]["other"] = {"kind": "git", "store_id": "other", "root": ".dev/workflows/subdir"}
        with self.assertRaises(RecordError) as result:
            WorkflowRecords(self.project, config)
        self.assertEqual(result.exception.code, "binding_mismatch")

    def test_real_assessment_validator_opt_in_uses_common_store_and_legacy_default_is_preserved(self):
        root = self.project / ".dev/assessments"
        assessment_id = "ASM-20261010-11-abc"
        folder = root / assessment_id
        folder.mkdir(parents=True)
        (root / "README.MD").write_text("Fixture assessments", encoding="utf-8")
        (folder / "report.md").write_text("Fixture report", encoding="utf-8")
        template = ".dev/assessments/README.MD"
        stamp = "2026-10-10T11:00:00+08:00"
        head = git(self.project, "rev-parse", "HEAD")
        locator = {"schema_version": "1.0", "assessment_id": assessment_id, "commit_search_id": assessment_id,
                   "assessment_type": "inventory", "title": "Fixture", "owner_skill": "ai-context-auditor",
                   "status": "draft", "report": "report.md", "artifact_branch": "fixture", "base_branch": "main",
                   "created_at": stamp, "updated_at": stamp, "template_source": template, "template_version": "1",
                   "report_template_source": template, "report_template_version": "1",
                   "subject_ref": {"repository": "fixture", "branch": "fixture", "commit": head},
                   "scope": {"included": ["workflow reference"], "excluded": []}, "relations": {key: [] for key in
                    ("supersedes", "superseded_by", "related_assessments", "workflow_refs", "backlog_refs", "adr_refs")},
                   "resume": {"current_step": "inspect", "last_completed_action": "fixture setup", "next_action": "review", "blockers": []}}
        locator["relations"]["workflow_refs"] = [WORKFLOW]
        (folder / "assessment.yaml").write_text(yaml.safe_dump(locator), encoding="utf-8")
        (root / "INDEX.MD").write_text(f"## Draft Assessments\n\n| [`{assessment_id}`]({assessment_id}/assessment.yaml) | Fixture | `inventory` | `ai-context-auditor` | `draft` | `{head}` | `{stamp}` | [report]({assessment_id}/report.md) |\n", encoding="utf-8")
        config = Path(self.temporary.name) / "config.json"
        config.write_bytes(encoded(DEFAULT_CONFIG))

        def validate(selected):
            argv = [sys.executable, "-I", "-B", str(ASSESSMENT_CLI), "--root", str(self.project)]
            if selected:
                argv += ["--workflow-store-config", str(config)]
            return subprocess.run(argv, capture_output=True, timeout=20)

        for selected in (False, True):
            result = validate(selected)
            self.assertEqual(result.returncode, 0, result.stdout.decode(errors="replace") + result.stderr.decode(errors="replace"))
        (self.artifact / "workflow.yaml").write_bytes(b"broken: [")
        self.assertEqual(validate(False).returncode, 0)
        failed = validate(True)
        self.assertEqual(failed.returncode, 1)
        self.assertIn(b"malformed_record", failed.stdout)
        (self.artifact / "workflow.yaml").unlink()
        self.assertIn(b"not_found", validate(True).stdout)


if __name__ == "__main__":
    unittest.main()
