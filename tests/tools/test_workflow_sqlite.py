"""Real native SQLite transactions, CLI processes and complete logical restore."""
from __future__ import annotations

import base64
import copy
from contextlib import closing
import json
import os
from pathlib import Path
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from tools.test_workflow_records import git, CHECKPOINT, ROOT

sys.path.insert(0, str(ROOT / "src"))
from workflow_records import WorkflowRecords
from workflow_records.contracts import VERSION, digest, encoded

CLI = ROOT / "src/skills/workflow-records/tools/workflow-records.py"
REF = {"provider_id": "local", "store_id": "local-records", "workflow_id": "example"}
STORE_REF = {key: REF[key] for key in ("provider_id", "store_id")}


def record():
    return {"metadata": {"title": "保留 Unicode 與未知欄位", "status": "in_progress", "owner_skill": "fixture",
                         "authority": "Synthetic fixture owner", "extensions": {"future": ["保留", 1]}},
            "tasks": [{"task_id": "T1", "title": "Verify provider", "status": "in_progress", "unknown": {"x": True}}],
            "entrypoint": "plan.md", "documents": {"plan.md": "# 原始計畫\n", "evidence.txt": "observed evidence\n"},
            "attachments": {"images/pixel.bin": base64.b64encode(b"\x00\xff\x10attachment").decode("ascii")}}


class SQLiteRecordTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base_temp = tempfile.TemporaryDirectory(prefix="workflow-sqlite-base-")
        cls.base = Path(cls.base_temp.name).resolve()
        (cls.base / "sentinel.txt").write_text("caller data", encoding="utf-8")
        git(cls.base, "init", "--initial-branch=fixture")
        git(cls.base, "add", ".")
        git(cls.base, "-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid", "-c", "commit.gpgsign=false",
            "-c", "core.hooksPath=empty-hooks", "commit", "-m", "fixture")

    @classmethod
    def tearDownClass(cls):
        cls.base_temp.cleanup()

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="workflow-sqlite-case-")
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name).resolve()
        self.project = self.directory / "project"
        shutil.copytree(self.base, self.project)
        self.database = self.directory / "store.sqlite"
        self.config = {"contract_version": VERSION, "default_provider": "local", "stores": {"local": {
            "kind": "local", "store_id": REF["store_id"], "repository_id": "fixture-repository", "database": str(self.database), "busy_timeout_ms": 500}}}
        self.service = WorkflowRecords(self.project, self.config)
        self.ok(self.run("init", store=True, operation_id="initialize"))
        self.ok(self.run("create", operation_id="create-example", record=record()))

    def request(self, operation, store=False, **extra):
        value = {"contract_version": VERSION, "operation": operation}
        if operation not in ("find", "capabilities"):
            value["store_ref" if store else "workflow_ref"] = copy.deepcopy(STORE_REF if store else REF)
        value.update(extra)
        return value

    def run(self, operation=None, store=False, **extra):
        # unittest calls run(result); preserve its runner protocol.
        if not isinstance(operation, str):
            return super().run(operation)
        return self.service.execute(self.request(operation, store, **extra))

    def ok(self, result):
        self.assertEqual(result["status"], "ok", result)
        return result["result"]

    def error(self, result, code):
        self.assertNotEqual(result["status"], "ok", result)
        self.assertEqual(result["error"]["code"], code, result)

    def checkpoint(self, operation_id="checkpoint-1"):
        current = self.ok(self.run("context"))
        return self.request("checkpoint", operation_id=operation_id, checkpoint=copy.deepcopy(CHECKPOINT),
                            expected_revision=current["revision"], expected_source_head=current["source_head"])

    def create_task(self, task_id="T2", operation_id="add-task"):
        current = self.ok(self.run("context"))
        return self.request("create-task", operation_id=operation_id,
                            expected_revision=current["revision"], expected_source_head=current["source_head"],
                            task={"task_id": task_id, "title": "Additional task", "status": "pending",
                                  "owner_skill": "fixture", "extensions": {"future": ["保留", 2]}})

    def launch(self, request, config=None, suffix="cli"):
        request_path = self.directory / (suffix + "-request.json")
        config_path = self.directory / (suffix + "-config.json")
        request_path.write_bytes(encoded(request))
        config_path.write_bytes(encoded(config or self.config))
        completed = subprocess.run([sys.executable, "-I", "-B", str(CLI), "--root", str(self.project),
                                    "--config", str(config_path), "--request", str(request_path)],
                                   cwd=self.directory, capture_output=True, timeout=20)
        self.assertEqual(completed.stderr, b"", completed.stderr)
        response = json.loads(completed.stdout)
        self.assertEqual(completed.returncode, 0 if response["status"] == "ok" else 1)
        return response

    def tables(self, database=None):
        with closing(sqlite3.connect(database or self.database)) as connection:
            return {name: connection.execute(f"SELECT * FROM {name} ORDER BY 1,2").fetchall()
                    for name in ("workflows", "revisions", "operations", "blobs")}

    def export(self, name="backup.json"):
        path = self.directory / name
        result = self.ok(self.run("export", store=True, destination=str(path)))
        return path, result

    def restored(self, archive, receipt, name="restored.sqlite"):
        config = copy.deepcopy(self.config)
        config["stores"]["local"]["database"] = str(self.directory / name)
        service = WorkflowRecords(self.project, config)
        request = self.request("restore", store=True, archive=str(archive), archive_digest=receipt["archive_digest"], operation_id="restore-" + name)
        result = self.ok(service.execute(request))
        self.assertEqual(result["store_state"], "inactive")
        return service, config

    def test_create_task_cli_fifty_additions_preserve_history_and_export_closure(self):
        self.ok(self.service.execute(self.checkpoint()))
        before = self.tables()
        first_request = self.create_task()
        first = self.ok(self.launch(first_request))
        for index in range(3, 52):
            self.ok(self.service.execute(self.create_task("T" + str(index), "add-" + str(index))))
        resumed = self.ok(self.launch(self.request("resume", task_limit=128)))
        self.assertEqual([task["task_id"] for task in resumed["tasks"]], ["T" + str(i) for i in range(1, 52)])
        self.assertEqual(resumed["plan"]["content"], record()["documents"]["plan.md"])
        self.assertEqual(git(self.project, "status", "--porcelain"), "")
        self.assertFalse((self.project / ".dev/local-backlog").exists())
        after = self.tables()
        self.assertEqual(after["blobs"], before["blobs"])
        self.assertTrue(all(row in after["revisions"] for row in before["revisions"]))
        states = {row[1]: json.loads(row[3]) for row in after["revisions"]}
        original = states[first_request["expected_revision"]]
        latest = states[resumed["revision"]]
        for key in ("metadata", "documents", "attachments", "entrypoint", "checkpoint"):
            self.assertEqual(latest[key], original[key])
        self.assertEqual(latest["tasks"][0], record()["tasks"][0])
        self.assertEqual(latest["tasks"][1], first_request["task"])
        self.assertEqual(len(after["revisions"]), len(before["revisions"]) + 50)
        archive, exported = self.export()
        restored, config = self.restored(archive, exported)
        recovered = self.tables(Path(config["stores"]["local"]["database"]))
        for key in ("workflows", "revisions", "blobs"):
            self.assertEqual(recovered[key], after[key])
        replay = self.ok(self.launch(first_request, config))
        self.assertEqual({**replay, "replayed": False}, first)
        fresh = self.create_task("T52", "inactive-add")
        self.error(restored.execute(fresh), "store_inactive")
        self.assertEqual(self.ok(self.launch(self.request("resume", task_limit=128), config))["tasks"], resumed["tasks"])

    def test_create_task_replay_collision_duplicate_and_stale_inputs(self):
        request = self.create_task()
        first = self.ok(self.launch(request))
        self.ok(self.service.execute(self.create_task("T3", "add-next")))
        before = self.tables()
        self.assertEqual({**self.ok(self.launch(request)), "replayed": False}, first)
        changed = copy.deepcopy(request)
        changed["task"]["title"] = "different"
        self.error(self.launch(changed), "operation_id_conflict")
        changed = copy.deepcopy(request)
        changed["operation_id"] = "stale-add"
        self.error(self.launch(changed), "revision_conflict")
        self.error(self.service.execute(self.create_task("T2", "duplicate")), "already_exists")
        fresh = self.create_task("T4", "stale-source")
        git(self.project, "-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid", "-c", "commit.gpgsign=false",
            "-c", "core.hooksPath=empty-hooks", "commit", "--allow-empty", "-m", "advance")
        self.error(self.launch(fresh), "source_conflict")
        self.assertEqual(self.tables(), before)

    def test_create_task_malformed_envelopes_and_tasks_do_not_write(self):
        request = self.create_task()
        before = self.tables()
        for key in ("workflow_ref", "operation_id", "expected_revision", "expected_source_head", "task"):
            with self.subTest(missing=key):
                changed = copy.deepcopy(request)
                del changed[key]
                self.error(self.service.execute(changed), "invalid_input")
        for task, code in ((None, "invalid_input"), ([], "invalid_input"), ({}, "invalid_input"),
                           ({"task_id": "bad/path", "title": "title", "status": "pending"}, "invalid_input"),
                           ({"task_id": "T2", "status": "pending"}, "malformed_record"),
                           ({"task_id": "T2", "title": "title", "status": 1}, "malformed_record")):
            with self.subTest(task=task):
                self.error(self.service.execute({**request, "task": task}), code)
        self.error(self.service.execute({**request, "unexpected": True}), "invalid_input")
        self.error(self.service.execute({**request, "expected_revision": None}), "invalid_input")
        self.assertEqual(self.tables(), before)

    def test_create_task_two_clients_and_same_request_have_atomic_results(self):
        first = self.create_task("T2", "parallel-task-1")
        second = copy.deepcopy(first)
        second["operation_id"] = "parallel-task-2"
        second["task"]["task_id"] = "T3"
        responses = self.simultaneous([first, second])
        self.assertEqual(sum(r["status"] == "ok" for r in responses), 1, responses)
        self.assertEqual([r["error"]["code"] for r in responses if r["status"] != "ok"], ["revision_conflict"])
        request = self.create_task("T4", "parallel-task-same")
        results = [self.ok(response) for response in self.simultaneous([request, request])]
        self.assertEqual(sorted(r["replayed"] for r in results), [False, True])
        self.assertEqual(len(self.tables()["revisions"]), 3)
        self.assertEqual(len(self.tables()["operations"]), 4)

    def test_create_task_capacity_and_source_change_before_commit_roll_back(self):
        from workflow_records import sqlite_store
        request = self.create_task()
        before = self.tables()
        with patch.object(sqlite_store, "MAX_TASKS", 1):
            self.error(self.service.execute(request), "limit_exceeded")
        with patch.object(sqlite_store, "source_head", side_effect=[request["expected_source_head"], "changed"]):
            self.error(self.service.execute(request), "source_conflict")
        self.assertEqual(self.tables(), before)
        self.assertEqual(self.ok(self.run("operation", operation_id=request["operation_id"]))["state"], "unknown")

    def test_create_task_not_advertised_or_dispatched_on_git(self):
        service = WorkflowRecords(self.project)
        capabilities = self.ok(service.execute({"contract_version": VERSION, "operation": "capabilities"}))
        self.assertNotIn("create-task", capabilities["providers"]["git"]["operations"])
        local = self.ok(self.run("capabilities"))
        self.assertIn("create-task", local["providers"]["local"]["operations"])
        request = self.create_task()
        request["workflow_ref"] = service.reference("example")
        self.error(service.execute(request), "unsupported_capability")

    def test_create_task_backup_rejects_rehashed_changes_to_prior_task(self):
        from workflow_records import backup
        from workflow_records.contracts import RecordError
        receipt = self.ok(self.service.execute(self.create_task()))
        archive, _ = self.export()
        original = json.loads(archive.read_bytes())["payload"]
        for replacement in (False, 1):
            with self.subTest(replacement=replacement):
                value = copy.deepcopy(original)
                row = next(row for row in value["tables"]["revisions"] if row[1] == receipt["revision"])
                state = json.loads(base64.b64decode(row[3]))
                state["tasks"][0]["unknown"] = {"x": replacement}
                raw = encoded(state)
                row[1], row[3] = digest(raw), base64.b64encode(raw).decode("ascii")
                value["tables"]["workflows"][0][1] = row[1]
                operation = next(item for item in value["tables"]["operations"] if item[1] == receipt["operation_id"])
                changed_receipt = json.loads(base64.b64decode(operation[3]))
                changed_receipt["revision"] = row[1]
                operation[3] = base64.b64encode(encoded(changed_receipt)).decode("ascii")
                with self.assertRaises(RecordError) as error:
                    backup.validate_payload(value)
                self.assertEqual(error.exception.code, "malformed_record")

    def test_real_cli_checkpoint_new_process_resume_replay_and_no_tracked_diff(self):
        found = self.ok(self.launch(self.request("find")))
        self.assertEqual(found["items"][0]["workflow_ref"], REF)
        context = self.ok(self.launch(self.request("context")))
        document = self.ok(self.launch(self.request("read", **context["entrypoint"])))
        self.assertEqual(document["content"], record()["documents"]["plan.md"])
        request = self.checkpoint()
        first = self.ok(self.launch(request))
        before = self.tables()
        lookup = self.ok(self.launch(self.request("operation", operation_id=request["operation_id"])))
        self.assertEqual(lookup, first)
        replay = self.ok(self.launch(request))
        self.assertEqual({**replay, "replayed": False}, first)
        self.assertEqual(self.tables(), before)
        resumed = self.ok(self.launch(self.request("resume")))
        self.assertEqual(resumed["checkpoint"]["next_action"]["text"], CHECKPOINT["next_action"])
        self.assertEqual(resumed["plan"]["content"], document["content"])
        self.assertEqual(git(self.project, "diff", "--name-only"), "")
        self.assertEqual(git(self.project, "status", "--porcelain"), "")

    def test_stale_revision_reused_id_and_source_head_conflicts_preserve_state(self):
        request = self.checkpoint()
        self.ok(self.service.execute(request))
        before = self.tables()
        changed = copy.deepcopy(request)
        changed["checkpoint"]["summary"] = "changed"
        self.error(self.launch(changed), "operation_id_conflict")
        changed = copy.deepcopy(request)
        changed["operation_id"] = "stale"
        self.error(self.launch(changed), "revision_conflict")
        fresh = self.checkpoint("source-conflict")
        git(self.project, "-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid", "-c", "commit.gpgsign=false",
            "-c", "core.hooksPath=empty-hooks", "commit", "--allow-empty", "-m", "advance")
        self.error(self.launch(fresh), "source_conflict")
        self.assertEqual(before, self.tables())

    def simultaneous(self, requests):
        config_path = self.directory / "concurrent-config.json"
        config_path.write_bytes(encoded(self.config))
        child = "import sys,runpy; print('READY',flush=True); sys.stdin.readline(); sys.argv=sys.argv[1:]; runpy.run_path(sys.argv[0],run_name='__main__')"
        children = []
        for index, request in enumerate(requests):
            path = self.directory / f"concurrent-{index}.json"
            path.write_bytes(encoded(request))
            process = subprocess.Popen([sys.executable, "-I", "-B", "-c", child, str(CLI), "--root", str(self.project),
                                        "--config", str(config_path), "--request", str(path)],
                                       stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            children.append(process)
        try:
            for process in children:
                self.assertEqual(process.stdout.readline().rstrip(b"\r\n"), b"READY")
            for process in children:
                process.stdin.write(b"go\n")
                process.stdin.flush()
            responses = []
            for process in children:
                out, err = process.communicate(timeout=20)
                self.assertEqual(err, b"")
                responses.append(json.loads(out))
            return responses
        finally:
            for process in children:
                if process.poll() is None:
                    process.kill()
                    process.communicate(timeout=5)

    def test_two_real_clients_same_revision_have_one_winner(self):
        first = self.checkpoint("parallel-1")
        second = copy.deepcopy(first)
        second["operation_id"] = "parallel-2"
        responses = self.simultaneous([first, second])
        self.assertEqual(sum(r["status"] == "ok" for r in responses), 1, responses)
        self.assertEqual([r["error"]["code"] for r in responses if r["status"] != "ok"], ["revision_conflict"])
        state = self.tables()
        self.assertEqual(len(state["revisions"]), 2)
        self.assertEqual(len(state["operations"]), 3)

    def test_two_real_clients_same_request_apply_once_and_id_conflict_is_not_overwritten(self):
        request = self.checkpoint("parallel-same")
        responses = self.simultaneous([request, request])
        results = [self.ok(response) for response in responses]
        self.assertEqual(sorted(r["replayed"] for r in results), [False, True])
        self.assertEqual(results[0]["revision"], results[1]["revision"])
        first = self.checkpoint("parallel-different")
        second = copy.deepcopy(first)
        second["checkpoint"]["summary"] = "different request"
        responses = self.simultaneous([first, second])
        self.assertEqual(sum(r["status"] == "ok" for r in responses), 1)
        self.assertEqual([r["error"]["code"] for r in responses if r["status"] != "ok"], ["operation_id_conflict"])

    def test_real_busy_timeout_does_not_fallback_or_partially_write(self):
        request = self.checkpoint()
        before = self.tables()
        config = copy.deepcopy(self.config)
        config["stores"]["local"]["busy_timeout_ms"] = 50
        with closing(sqlite3.connect(self.database, isolation_level=None)) as writer:
            writer.execute("BEGIN IMMEDIATE")
            self.error(self.launch(request, config), "writer_busy")
            writer.rollback()
        self.assertEqual(self.tables(), before)
        self.assertEqual(git(self.project, "status", "--porcelain"), "")

    def test_complete_export_restore_preserves_history_extensions_blobs_and_receipts(self):
        checkpoint = self.checkpoint()
        first = self.ok(self.service.execute(checkpoint))
        old_context = self.ok(self.run("context"))
        request = self.request("write-document", document="plan.md", content="# 新版計畫\n", operation_id="edit-plan",
                               expected_revision=old_context["revision"], expected_source_head=old_context["source_head"])
        self.ok(self.launch(request))
        self.ok(self.run("create", operation_id="create-other", record=record(), workflow_ref={**REF, "workflow_id": "another"}))
        archive, exported = self.export()
        self.ok(self.launch(self.request("preflight", store=True, archive=str(archive), archive_digest=exported["archive_digest"])))
        service, config = self.restored(archive, exported)
        original = self.tables()
        recovered = self.tables(Path(config["stores"]["local"]["database"]))
        for name in ("workflows", "revisions", "blobs"):
            self.assertEqual(recovered[name], original[name])
        self.assertTrue(all(row in recovered["operations"] for row in original["operations"]))
        receipt = self.ok(self.launch(self.request("operation", operation_id=checkpoint["operation_id"]), config))
        self.assertEqual(receipt, first)
        replay = self.ok(self.launch(checkpoint, config))
        self.assertEqual({**replay, "replayed": False}, first)
        old = self.ok(self.launch(self.request("read", **old_context["entrypoint"]), config))
        self.assertEqual(old["content"], "# 原始計畫\n")
        resumed = self.ok(self.launch(self.request("resume"), config))
        self.assertEqual(resumed["plan"]["content"], "# 新版計畫\n")
        self.assertEqual(resumed["store_state"], "inactive")
        new_request = self.request("checkpoint", operation_id="blocked-write", checkpoint=CHECKPOINT,
                                  expected_revision=resumed["revision"], expected_source_head=resumed["source_head"])
        self.error(service.execute(new_request), "store_inactive")

    def test_corrupt_backup_preflight_and_existing_target_refuse_before_restore(self):
        archive, exported = self.export()
        document = json.loads(archive.read_bytes())
        # Recompute the outer hashes to exercise the internal relationship oracle.
        document["payload"]["tables"]["blobs"][0][1] = base64.b64encode(b"corrupt").decode("ascii")
        document["snapshot_digest"] = digest(encoded(document["payload"]))
        corrupt = self.directory / "corrupt.json"
        corrupt.write_bytes(encoded(document))
        config = copy.deepcopy(self.config)
        target = self.directory / "refused.sqlite"
        config["stores"]["local"]["database"] = str(target)
        service = WorkflowRecords(self.project, config)
        request = self.request("restore", store=True, archive=str(corrupt), archive_digest=digest(corrupt.read_bytes()), operation_id="restore-corrupt")
        self.error(service.execute(request), "malformed_record")
        self.assertFalse(target.exists())
        before = self.database.read_bytes()
        self.error(self.run("restore", store=True, archive=str(archive), archive_digest=exported["archive_digest"], operation_id="refuse-existing"), "already_exists")
        self.assertEqual(self.database.read_bytes(), before)

    def test_retirement_proof_allows_exactly_one_successor_and_safe_activation_retry(self):
        archive, exported = self.export()
        restored, restored_config = self.restored(archive, exported)
        second, _ = self.restored(archive, exported, "second.sqlite")
        activate = self.request("activate", store=True, operation_id="activate-restored", retired_database=str(self.database), retirement_seal="missing")
        self.error(restored.execute(activate), "binding_mismatch")
        retirement = self.ok(self.run("deactivate", store=True, operation_id="retire", snapshot_digest=exported["snapshot_digest"]))
        activate["retirement_seal"] = retirement["retirement_seal"]
        result = self.ok(restored.execute(activate))
        self.assertEqual(result["store_state"], "active")
        self.assertTrue(self.ok(restored.execute(activate))["replayed"])
        self.error(second.execute(activate), "binding_mismatch")
        old = self.checkpoint("old-writer")
        self.error(self.service.execute(old), "store_inactive")
        context = self.ok(restored.execute(self.request("context")))
        request = self.request("checkpoint", operation_id="new-writer", checkpoint=CHECKPOINT,
                               expected_revision=context["revision"], expected_source_head=context["source_head"])
        self.ok(self.launch(request, restored_config))

    def test_stale_export_cannot_retire_the_newer_writer(self):
        _, exported = self.export()
        self.ok(self.service.execute(self.checkpoint()))
        self.error(self.run("deactivate", store=True, operation_id="stale-retire", snapshot_digest=exported["snapshot_digest"]), "revision_conflict")
        self.assertEqual(self.ok(self.run("context"))["store_state"], "active")

    def test_full_normal_operation_pool_keeps_lifecycle_capacity_and_late_transfer_refuses_early(self):
        from workflow_records import backup, sqlite_store
        # Lower limits exercise the same real transactions without 4096 writes.
        with patch.object(sqlite_store, "MAX_WORKFLOW_OPERATIONS", 2), patch.object(backup, "MAX_WORKFLOW_OPERATIONS", 2), \
             patch.object(sqlite_store, "MAX_ADMIN_OPERATIONS", 3), patch.object(backup, "MAX_ADMIN_OPERATIONS", 3):
            self.ok(self.service.execute(self.checkpoint()))
            before = self.tables()
            self.error(self.service.execute(self.checkpoint("full-normal")), "limit_exceeded")
            self.assertEqual(self.tables(), before)
            archive, exported = self.export()
            restored, config = self.restored(archive, exported)
            retirement = self.ok(self.run("deactivate", store=True, operation_id="retire", snapshot_digest=exported["snapshot_digest"]))
            activation = self.request("activate", store=True, operation_id="activate", retired_database=str(self.database), retirement_seal=retirement["retirement_seal"])
            self.assertEqual(self.ok(restored.execute(activation))["store_state"], "active")
            next_archive = self.directory / "next.json"
            next_export = self.ok(restored.execute(self.request("export", store=True, destination=str(next_archive))))
            self.error(restored.execute(self.request("deactivate", store=True, operation_id="retire-next", snapshot_digest=next_export["snapshot_digest"])), "limit_exceeded")
            self.assertEqual(self.ok(restored.execute(self.request("context")))["store_state"], "active")
            next_config = copy.deepcopy(config)
            target = self.directory / "next.sqlite"
            next_config["stores"]["local"]["database"] = str(target)
            self.error(WorkflowRecords(self.project, next_config).execute(self.request("restore", store=True,
                       archive=str(next_archive), archive_digest=next_export["archive_digest"], operation_id="restore-next")), "limit_exceeded")
            self.assertFalse(target.exists())

    def test_portable_size_budget_rolls_back_new_history_and_keeps_prior_export_restorable(self):
        from workflow_records import backup
        large = record()
        large["metadata"]["extension"] = "Z" * 20000
        ref = {**REF, "workflow_id": "large"}
        self.ok(self.run("create", workflow_ref=ref, operation_id="create-large", record=large))
        archive, _ = self.export("before-size.json")
        value = json.loads(archive.read_bytes())["payload"]
        normal = {**value, "tables": {**value["tables"], "operations": [row for row in value["tables"]["operations"] if row[0]]}}
        before = self.tables()
        context = self.ok(self.run("context", workflow_ref=ref))
        request = self.request("checkpoint", workflow_ref=ref, operation_id="too-large", checkpoint=CHECKPOINT,
                               expected_revision=context["revision"], expected_source_head=context["source_head"])
        with patch.object(backup, "MAX_DATA_BYTES", len(encoded(normal)) + 2048):
            self.error(self.service.execute(request), "limit_exceeded")
            self.assertEqual(self.tables(), before)
            retained, exported = self.export("retained.json")
            restored, _ = self.restored(retained, exported)
            self.assertEqual(self.ok(restored.execute(self.request("context", workflow_ref=ref)))["revision"], context["revision"])

    def test_forged_checkpoint_history_is_rejected_even_with_recomputed_hashes(self):
        from workflow_records import backup
        from workflow_records.contracts import RecordError
        archive, _ = self.export()
        value = json.loads(archive.read_bytes())["payload"]
        row = value["tables"]["revisions"][0]
        state = json.loads(base64.b64decode(row[3]))
        state["checkpoint"] = {"operation_id": "nonexistent", "recorded_at": state["event"]["recorded_at"], "value": CHECKPOINT}
        raw = encoded(state)
        row[1], row[3] = digest(raw), base64.b64encode(raw).decode("ascii")
        value["tables"]["workflows"][0][1] = row[1]
        operation = next(item for item in value["tables"]["operations"] if item[0])
        receipt = json.loads(base64.b64decode(operation[3]))
        receipt["revision"] = row[1]
        operation[3] = base64.b64encode(encoded(receipt)).decode("ascii")
        with self.assertRaises(RecordError) as error:
            backup.validate_payload(value)
        self.assertEqual(error.exception.code, "malformed_record")

    def test_killed_real_process_rolls_back_checkpoint_revision_and_receipt_together(self):
        request = self.checkpoint("interrupted")
        request_path = self.directory / "interrupted-request.json"
        config_path = self.directory / "interrupted-config.json"
        request_path.write_bytes(encoded(request))
        config_path.write_bytes(encoded(self.config))
        before = self.tables()
        code = """import sys,json
from pathlib import Path
sys.path.insert(0,sys.argv[1])
from workflow_records import WorkflowRecords
from workflow_records.sqlite_store import SQLiteStore
original=SQLiteStore.save_operation
def pause(connection,scope,request,receipt):
    original(connection,scope,request,receipt)
    print('UNCOMMITTED',flush=True)
    sys.stdin.readline()
SQLiteStore.save_operation=staticmethod(pause)
response=WorkflowRecords(sys.argv[2],json.loads(Path(sys.argv[3]).read_bytes())).execute(json.loads(Path(sys.argv[4]).read_bytes()))
print(json.dumps(response),flush=True)
"""
        process = subprocess.Popen([sys.executable, "-I", "-B", "-c", code, str(CLI.parent), str(self.project), str(config_path), str(request_path)],
                                   stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        try:
            self.assertEqual(process.stdout.readline().strip(), b"UNCOMMITTED")
            process.kill()
            process.communicate(timeout=10)
        finally:
            if process.poll() is None:
                process.kill()
                process.communicate(timeout=5)
        self.assertEqual(self.tables(), before)
        self.assertEqual(self.ok(self.launch(self.request("operation", operation_id="interrupted")))["state"], "unknown")
        self.ok(self.launch(request))

    def test_export_read_snapshot_excludes_competing_transaction_without_partial_history(self):
        # Hold a real read transaction while a separate process attempts a write.
        # The write lock must be observed before releasing the export barrier.
        config = copy.deepcopy(self.config)
        config["stores"]["local"]["busy_timeout_ms"] = 10000
        config_path = self.directory / "concurrent-config.json"
        config_path.write_bytes(encoded(config))
        archive = self.directory / "concurrent-export.json"
        export_request = self.directory / "export-request.json"
        export_request.write_bytes(encoded(self.request("export", store=True, destination=str(archive))))
        write_request = self.directory / "write-request.json"
        write_request.write_bytes(encoded(self.checkpoint("during-export")))
        code = """import sys,json
from pathlib import Path
sys.path.insert(0,sys.argv[1])
from workflow_records import WorkflowRecords,backup
from workflow_records.sqlite_store import SQLiteStore
if sys.argv[5]=='export':
    original=backup.payload
    def barrier(connection,meta):
        connection.execute('SELECT count(*) FROM workflows').fetchone()
        print('SNAPSHOT',flush=True)
        sys.stdin.readline()
        return original(connection,meta)
    backup.payload=barrier
else:
    original=SQLiteStore.save_operation
    def barrier(connection,scope,request,receipt):
        original(connection,scope,request,receipt)
        print('UNCOMMITTED',flush=True)
    SQLiteStore.save_operation=staticmethod(barrier)
response=WorkflowRecords(sys.argv[2],json.loads(Path(sys.argv[3]).read_bytes())).execute(json.loads(Path(sys.argv[4]).read_bytes()))
print(json.dumps(response),flush=True)
"""
        common = [sys.executable, "-I", "-B", "-c", code, str(CLI.parent), str(self.project), str(config_path)]
        exporter = subprocess.Popen([*common, str(export_request), "export"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        writer = None
        before = self.tables()
        try:
            self.assertEqual(exporter.stdout.readline().strip(), b"SNAPSHOT")
            writer = subprocess.Popen([*common, str(write_request), "write"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            self.assertEqual(writer.stdout.readline().strip(), b"UNCOMMITTED")
            output, error = exporter.communicate(b"continue\n", timeout=15)
            self.assertEqual(error, b"")
            exported = self.ok(json.loads(output))
            output, error = writer.communicate(timeout=15)
            self.assertEqual(error, b"")
            self.ok(json.loads(output))
        finally:
            for process in (exporter, writer):
                if process is not None and process.poll() is None:
                    process.kill()
                    process.communicate(timeout=5)
        restored, config = self.restored(archive, exported)
        recovered = self.tables(Path(config["stores"]["local"]["database"]))
        for table in ("workflows", "revisions", "blobs"):
            self.assertEqual(recovered[table], before[table])
        self.assertTrue(all(row in recovered["operations"] for row in before["operations"]))
        self.assertEqual(self.ok(restored.execute(self.request("operation", operation_id="during-export")))["state"], "unknown")
        self.assertEqual(self.ok(self.run("operation", operation_id="during-export"))["state"], "applied")

    def test_activation_phase_two_failure_reserves_only_same_successor_and_can_retry(self):
        from workflow_records import backup
        from workflow_records.contracts import RecordError
        archive, exported = self.export()
        restored, _ = self.restored(archive, exported)
        second, _ = self.restored(archive, exported, "second.sqlite")
        retirement = self.ok(self.run("deactivate", store=True, operation_id="retire", snapshot_digest=exported["snapshot_digest"]))
        request = self.request("activate", store=True, operation_id="activate", retired_database=str(self.database), retirement_seal=retirement["retirement_seal"])
        original = backup.SQLiteStore.save_operation
        def reject_activation(connection, scope, value, receipt):
            if value["operation"] == "activate":
                raise RecordError("writer_busy", "selected failure after successor claim")
            return original(connection, scope, value, receipt)
        with patch.object(backup.SQLiteStore, "save_operation", staticmethod(reject_activation)):
            failed = restored.execute(request)
        self.error(failed, "activation_pending")
        self.assertEqual(failed["mutation_state"], "unknown")
        self.assertEqual(self.ok(restored.execute(self.request("context")))["store_state"], "inactive")
        self.error(second.execute(request), "binding_mismatch")
        self.assertEqual(self.ok(restored.execute(request))["store_state"], "active")

    def test_explicit_linked_worktree_shares_common_repository_but_clone_does_not(self):
        linked = self.directory / "linked"
        git(self.project, "-c", "core.hooksPath=empty-hooks", "worktree", "add", "--detach", str(linked), "HEAD")
        self.addCleanup(lambda: git(self.project, "worktree", "remove", "--force", str(linked)))
        same = WorkflowRecords(linked, self.config)
        self.assertEqual(self.ok(same.execute(self.request("context")))["workflow_ref"], REF)
        other = self.directory / "other"
        shutil.copytree(self.base, other)
        self.error(WorkflowRecords(other, self.config).execute(self.request("context")), "binding_mismatch")

    def test_database_in_repository_and_network_path_are_rejected_without_creation(self):
        config = copy.deepcopy(self.config)
        config["stores"]["local"]["database"] = str(self.project / "bad.sqlite")
        self.error(WorkflowRecords(self.project, config).execute(self.request("init", store=True, operation_id="bad-init")), "unsafe_path")
        self.assertFalse((self.project / "bad.sqlite").exists())
        config["stores"]["local"]["database"] = "//server/share/bad.sqlite"
        self.error(WorkflowRecords(self.project, config).execute(self.request("init", store=True, operation_id="network-init")), "unsupported_topology")

    def test_missing_local_store_is_unavailable_and_read_never_creates_it(self):
        config = copy.deepcopy(self.config)
        missing = self.directory / "missing.sqlite"
        config["stores"]["local"]["database"] = str(missing)
        self.error(WorkflowRecords(self.project, config).execute(self.request("context")), "provider_unavailable")
        self.assertFalse(missing.exists())

    def test_cli_missing_local_member_fails_without_source_fallback(self):
        package = self.directory / "runtime"
        shutil.copytree(CLI.parent, package)
        (package / "workflow_records/backup.py").unlink()
        completed = subprocess.run([sys.executable, "-I", "-B", str(package / CLI.name), "--help"], capture_output=True, timeout=10)
        self.assertEqual(completed.returncode, 1)
        response = json.loads(completed.stdout)
        self.assertEqual(response["status"], "unavailable")
        self.assertEqual(completed.stderr, b"")


if __name__ == "__main__":
    unittest.main()
