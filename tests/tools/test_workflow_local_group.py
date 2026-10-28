"""Actual local CLI/file/SQLite evidence; provider observations are fixtures only."""
from __future__ import annotations

import base64
import copy
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
import yaml

ROOT = Path(__file__).resolve().parents[2]
TOOLS = ROOT / "src/skills/workflow-records/tools"
sys.path.insert(0, str(TOOLS))
from workflow_records.group_service import LocalGroup, CONFIG
from workflow_records import group_model as m
from workflow_records import group_storage as storage
from workflow_records import group_service

SCRATCH = Path(os.environ.get("WORKFLOW_GROUP_TEST_ROOT", tempfile.gettempdir()))


class LocalGroupTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="local-group-", dir=SCRATCH)
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name)
        self.project = self.directory / "project"
        self.project.mkdir()
        self.ref = {"group_id": "fixture-group", "project_id": "fixture-project", "workflow_id": "fixture-workflow"}
        self.config = self.configuration("first")
        self.group = LocalGroup(self.project, self.config)
        self.counter = 0
        self.ok(self.request("group-init", operation_id="initialize"))

    def configuration(self, name):
        control = self.directory / (name + "-control")
        control.mkdir()
        files = self.directory / (name + "-files")
        files.mkdir()
        return {"contract_version": CONFIG, "group_ref": self.ref, "control_directory": str(control), "file_path": str(files / "workflow.json")}

    def request(self, operation, **fields):
        self.counter += 1
        request = {"contract_version": m.PROVIDERS if operation.startswith("provider-") else m.PROFILE, "group_ref": self.ref, "operation": operation}
        if operation not in group_service.READS | {"group-export", "group-preflight"}:
            request["operation_id"] = "operation-" + str(self.counter)
            if operation not in ("group-init", "group-restore"):
                config = self.group.execute({"contract_version": m.PROFILE, "group_ref": self.ref, "operation": "group-configuration"})
                self.assertEqual(config["status"], "ok", config)
                request.update({"expected_configuration_revision": config["result"]["configuration_revision"], "expected_authority_epoch": config["result"]["authority_epoch"], "expected_revision": config["result"]["revision"]})
                if operation in ("provider-register", "provider-update", "provider-enable", "provider-disable"):
                    request["expected_provider_configuration_revision"] = config["result"]["provider_configuration_revision"]
        request.update(fields)
        return request

    def ok(self, request, group=None):
        result = (group or self.group).execute(request)
        self.assertEqual(result["status"], "ok", result)
        return result["result"]

    def error(self, request, code):
        result = self.group.execute(request)
        self.assertEqual(result["status"], "error", result)
        self.assertEqual(result["error"]["code"], code, result)
        return result

    def create(self):
        return self.ok(self.request("group-create", record={"metadata": {"title": "測試", "status": "active", "extension": {"future": [1, True]}}, "tasks": [{"task_id": "T1", "extra": "keep"}],
                                                           "entrypoint": "plan.md", "documents": {"plan.md": {"encoding": "utf-8", "content": "line1\r\nline2\r\n"}},
                                                           "attachments": {"empty.bin": {"encoding": "base64", "content": ""}, "data.bin": {"encoding": "base64", "content": "AP9BQkM="}}}))

    def add_sqlite(self):
        self.ok(self.request("member-add", member_id="sqlite", kind="sqlite", path=str(self.directory / "member.db")))

    def sync(self):
        statuses = self.ok(self.request("group-sync-status"))["targets"]
        for row in statuses:
            if row["target"]["kind"] == "local" and row["delivery"]["state"] != "accepted":
                self.assertEqual(self.ok(self.request("group-sync", intent_id=row["intent_id"]))["state"], "applied")

    def switch(self, member):
        config = self.ok(self.request("group-configuration"))
        return self.ok(self.request("select-authority", member_id=member, expected_generation=config["members"][member]["generation"]))

    def cli(self, request):
        config = self.directory / "config.json"
        config.write_text(json.dumps(self.config), encoding="utf-8")
        result = subprocess.run([sys.executable, "-I", "-B", str(TOOLS / "local-group.py"), "--root", str(self.project), "--config", str(config), "--request", "-"], input=json.dumps(request).encode(), capture_output=True, timeout=20)
        self.assertEqual(result.stderr, b"")
        return result.returncode, json.loads(result.stdout)

    def test_repeated_completion_reopen_on_sqlite_authority_preserves_atomic_cuts(self):
        # The caller coordinates its source lifecycle fields in one generic revision.
        self.create()
        self.add_sqlite()
        self.sync()
        self.switch("sqlite")
        member = self.ok(self.request("group-configuration"))["members"]["sqlite"]
        initial = storage.load_member(member)
        retained = copy.deepcopy(initial["events"])
        created_at = "2026-10-29T09:00:00+08:00"
        requests = []
        for step, status in enumerate(("completed", "in_progress", "completed", "in_progress", "completed"), 1):
            with self.subTest(step=step, status=status):
                timestamp = "2026-10-29T10:00:0" + str(step) + "+08:00"
                phase = "completed" if status == "completed" else "implementation"
                result = {"summary": "Caller transition " + str(step),
                          "finding_status": "addressed" if status == "completed" else "pending"}
                document = "# Cycle " + str(step) + "\n" + status + "\n"
                request = self.request("group-revise-workflow", operation_id="lifecycle-" + str(step),
                                       metadata_patch={"lifecycle_contract": "1.0", "status": status, "current_phase": phase,
                                                       "created_at": created_at, "updated_at": timestamp},
                                       task_patches={"T1": {"status": status, "created_at": created_at, "updated_at": timestamp, "result": result}},
                                       documents={"plan.md": {"encoding": "utf-8", "content": document}}, attachments={})
                receipt = self.ok(request)
                current = self.ok(self.request("group-context"))
                after = storage.load_member(member)
                state = current["record"]
                self.assertEqual(current["authority"], "sqlite")
                self.assertEqual(current["revision"], receipt["revision"])
                self.assertEqual(len(after["events"]), len(initial["events"]) + step)
                self.assertEqual(after["events"][:-1], retained)
                self.assertEqual(after["events"][-1]["body"]["parent"], request["expected_revision"])
                self.assertEqual(after["events"][-1]["body"]["operation_id"], request["operation_id"])
                for field in ("status", "current_phase", "created_at", "updated_at", "lifecycle_contract"):
                    self.assertEqual(state["metadata"][field], request["metadata_patch"][field])
                for field in ("status", "created_at", "updated_at", "result"):
                    self.assertEqual(state["tasks"][0][field], request["task_patches"]["T1"][field])
                self.assertEqual(state["metadata"]["extension"], {"future": [1, True]})
                self.assertEqual(state["tasks"][0]["extra"], "keep")
                read = self.ok(self.request("group-read", collection="documents", document="plan.md"))
                self.assertEqual(read["revision"], receipt["revision"])
                self.assertEqual(base64.b64decode(read["content"]), document.encode("utf-8"))
                self.assertEqual({**self.ok(request), "replayed": False}, receipt)
                stale = copy.deepcopy(request)
                stale["operation_id"] += "-stale"
                stale["metadata_patch"]["updated_at"] = "2026-10-29T23:59:59+08:00"
                stale["task_patches"]["T1"]["result"] = {"summary": "must not persist", "finding_status": "pending"}
                stale["documents"]["plan.md"]["content"] = "must not persist"
                self.error(stale, "revision_conflict")
                self.assertEqual(storage.load_member(member), after)
                retained = copy.deepcopy(after["events"])
                requests.append((request, receipt))
        terminal = storage.load_member(member)
        for request, receipt in requests:
            self.assertEqual({**self.ok(request), "replayed": False}, receipt)
        self.assertEqual(storage.load_member(member), terminal)
        self.assertEqual(self.ok(self.request("group-context"))["record"]["metadata"]["status"], "completed")

    def test_file_only_public_cli_and_byte_preservation(self):
        request = self.request("group-create", record={"metadata": {"title": "offline", "status": "active"}, "tasks": [], "entrypoint": "plan.md", "documents": {"plan.md": {"encoding": "utf-8", "content": "a\r\nb"}}, "attachments": {}})
        code, result = self.cli(request)
        self.assertEqual(code, 0, result)
        code, read = self.cli(self.request("group-read", collection="documents", document="plan.md"))
        self.assertEqual(code, 0, read)
        self.assertEqual(base64.b64decode(read["result"]["content"]), b"a\r\nb")
        self.assertFalse(list(self.directory.glob("*.db")))

    def test_manifest_copied_standalone_package_cli_without_source_fallback(self):
        manifest = yaml.safe_load((ROOT / "src/distribution/manifest.yaml").read_text(encoding="utf-8"))
        component = next(item for item in manifest["components"] if item["id"] == "workflow-records")
        package = self.directory / "installed/.ai/core/skills/workflow-records"
        for member in component["members"]:
            target = package / member["source"]
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / component["source"] / member["source"], target)
        config = self.configuration("standalone")
        config_path = self.directory / "standalone-config.json"
        config_path.write_text(json.dumps(config), encoding="utf-8")
        runner = self.directory / "no-sqlite.py"
        runner.write_text("import importlib.abc,runpy,sys\nclass Block(importlib.abc.MetaPathFinder):\n def find_spec(self,fullname,path=None,target=None):\n  if fullname.split('.')[0] in ('sqlite3','_sqlite3','jsonschema','referencing'):\n   raise ImportError('optional runtime unavailable')\nsys.meta_path.insert(0,Block())\nsys.argv=sys.argv[1:]\nrunpy.run_path(sys.argv[0],run_name='__main__')\n", encoding="utf-8")
        requests = [self.request("group-init", operation_id="standalone-init"),
                    {"contract_version": m.PROFILE, "group_ref": self.ref, "operation": "group-create", "operation_id": "standalone-create",
                     "expected_configuration_revision": 0, "expected_authority_epoch": 1, "expected_revision": None,
                     "record": {"metadata": {"title": "standalone", "status": "active"}, "tasks": [], "entrypoint": "plan.md",
                                "documents": {"plan.md": {"encoding": "utf-8", "content": "copied package"}}, "attachments": {}}}]
        for request in requests:
            process = subprocess.run([sys.executable, "-I", "-B", str(runner), str(package / "tools/local-group.py"), "--root", str(self.project), "--config", str(config_path), "--request", "-"],
                                     input=json.dumps(request).encode(), cwd=self.directory, capture_output=True, timeout=20)
            self.assertEqual(process.stderr, b"")
            self.assertEqual(process.returncode, 0, process.stdout)
            self.assertEqual(json.loads(process.stdout)["status"], "ok")
        self.assertTrue(Path(config["file_path"]).is_file())

    def test_both_authorities_sync_and_stale_epoch(self):
        self.create()
        self.add_sqlite()
        self.error(self.request("select-authority", member_id="sqlite", expected_generation=self.ok(self.request("group-configuration"))["members"]["sqlite"]["generation"]), "source_cut_conflict")
        self.ok(self.request("group-write-document", document="plan.md", content={"encoding": "utf-8", "content": "changed\r\n"}))
        stale = self.request("group-create-task", task={"task_id": "stale"})
        self.sync()
        self.switch("sqlite")
        self.error(stale, "configuration_conflict")
        self.ok(self.request("group-create-task", task={"task_id": "T2", "nested": {"preserve": True}}))
        self.sync()
        self.switch("file")
        state = self.ok(self.request("group-resume"))["record"]
        self.assertEqual(state["metadata"]["extension"], {"future": [1, True]})
        self.assertEqual(state["attachments"]["data.bin"]["content"], "AP9BQkM=")
        self.assertEqual(len(state["tasks"]), 2)

    def test_replay_before_cas_and_no_fallback(self):
        self.create()
        request = self.request("group-create-task", task={"task_id": "T2"})
        first = self.ok(request)
        self.assertTrue(self.ok(request)["replayed"])
        changed = copy.deepcopy(request)
        changed["task"]["task_id"] = "T3"
        self.error(changed, "operation_id_conflict")
        self.assertEqual(self.ok(self.request("group-operation", lookup_operation_id=request["operation_id"]))["revision"], first["revision"])
        self.add_sqlite()
        self.sync()
        self.switch("sqlite")
        (self.directory / "member.db").rename(self.directory / "hidden.db")
        self.error({"contract_version": m.PROFILE, "group_ref": self.ref, "operation": "group-context"}, "provider_unavailable")

    def test_native_store_cannot_open_group_schema(self):
        self.create()
        self.add_sqlite()
        connection = sqlite3.connect(self.directory / "member.db")
        self.addCleanup(connection.close)
        self.assertEqual(connection.execute("SELECT schema_version FROM group_envelope").fetchone()[0], storage.SCHEMA)
        from workflow_records.sqlite_store import SQLiteStore
        # A native reader expects store_meta, never dispatches this envelope as native data.
        with self.assertRaises(sqlite3.OperationalError):
            SQLiteStore.meta(object(), connection)

    def test_target_outage_is_retained_without_fallback(self):
        self.create()
        self.add_sqlite()
        row = self.ok(self.request("group-sync-status"))["targets"][0]
        database = self.directory / "member.db"
        database.rename(self.directory / "away.db")
        request = self.request("group-sync", intent_id=row["intent_id"])
        observed = self.ok(request)
        self.assertEqual(observed["state"], "unknown")
        self.assertEqual(observed["error"]["code"], "provider_unavailable")
        self.assertTrue(self.ok(request)["replayed"])
        self.assertEqual(self.ok(self.request("group-sync-status"))["targets"][0]["delivery"]["attempts"], 1)
        (self.directory / "away.db").rename(database)
        self.sync()

    def test_replica_parent_outage_does_not_block_authority(self):
        self.create()
        carrier = self.directory / "replica-parent"
        carrier.mkdir()
        self.ok(self.request("member-add", member_id="sqlite", kind="sqlite", path=str(carrier / "member.db")))
        self.sync()
        carrier.rename(self.directory / "replica-away")
        self.ok(self.request("group-create-task", task={"task_id": "T2"}))
        self.assertEqual(self.ok(self.request("group-context"))["authority"], "file")
        sync_failure = self.ok(self.request("group-sync", intent_id=self.ok(self.request("group-sync-status"))["targets"][-1]["intent_id"]))
        self.assertEqual(sync_failure["state"], "unknown")
        (self.directory / "replica-away").rename(carrier)
        self.sync()
        self.switch("sqlite")
        files = Path(self.config["file_path"]).parent
        files.rename(self.directory / "file-away")
        reopened = LocalGroup(self.project, self.config)
        self.ok({"contract_version": m.PROFILE, "group_ref": self.ref, "operation": "group-context"}, reopened)
        self.ok(self.request("group-create-task", task={"task_id": "T3"}))
        (self.directory / "file-away").rename(files)
        self.sync()

    def test_real_os_lock_and_exit_release(self):
        source = "import sys,time;sys.path.insert(0,sys.argv[1]);from workflow_records.group_storage import group_lock;from pathlib import Path\nwith group_lock(Path(sys.argv[2])):\n print('locked',flush=True)\n time.sleep(30)\n"
        process = subprocess.Popen([sys.executable, "-I", "-B", "-c", source, str(TOOLS), self.config["control_directory"]], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        try:
            self.assertEqual(process.stdout.readline().strip(), b"locked")
            self.error({"contract_version": m.PROFILE, "group_ref": self.ref, "operation": "group-configuration"}, "writer_busy")
        finally:
            process.kill()
            process.communicate(timeout=10)
        self.ok(self.request("group-configuration"))

    def test_lost_replica_response_and_transition_recovery(self):
        self.create()
        self.add_sqlite()
        row = self.ok(self.request("group-sync-status"))["targets"][0]
        request = self.request("group-sync", intent_id=row["intent_id"])
        original = self.group.commit
        with patch.object(self.group, "commit", side_effect=OSError("simulated response loss after replica write")):
            self.error(request, "storage_error")
        self.group.commit = original
        self.ok(request)
        self.sync()
        selection = self.request("select-authority", member_id="sqlite", expected_generation=self.ok(self.request("group-configuration"))["members"]["sqlite"]["generation"])
        original_write = group_service.atomic_json
        with patch.object(group_service, "atomic_json", wraps=original_write) as write:
            def interrupt(path, value, **kwargs):
                if path == self.group.control_path:
                    raise OSError("stop before control replacement")
                return original_write(path, value, **kwargs)
            write.side_effect = interrupt
            self.error(selection, "storage_error")
        self.assertEqual(self.ok(self.request("group-configuration"))["authority"], "sqlite")
        self.assertTrue(self.ok(selection)["replayed"])

    def test_backup_restore_inactive_and_single_successor(self):
        self.create()
        self.add_sqlite()
        self.sync()
        archive = self.ok(self.request("group-export", destination=str(self.directory / "backup.json")))
        self.ok(self.request("group-preflight", archive=archive["destination"], archive_digest=archive["archive_digest"]))
        restored = []
        for index in range(2):
            config = self.configuration("restore" + str(index))
            root = self.project
            if index == 0:
                root = self.directory / "relocated-project"
                root.mkdir()
            group = LocalGroup(root, config)
            request = {"contract_version": m.PROFILE, "group_ref": self.ref, "operation": "group-restore", "operation_id": "restore-" + str(index),
                       "archive": archive["destination"], "archive_digest": archive["archive_digest"], "member_paths": {"file": config["file_path"], "sqlite": str(self.directory / ("restore" + str(index) + ".db"))}}
            self.ok(request, group)
            configuration = self.ok({"contract_version": m.PROFILE, "group_ref": self.ref, "operation": "group-configuration"}, group)
            self.assertEqual(configuration["state"], "inactive")
            restored.append((group, configuration))
        retired = self.ok(self.request("group-deactivate", snapshot_digest=archive["snapshot_digest"]))
        for index, (group, config) in enumerate(restored):
            request = {"contract_version": m.PROFILE, "group_ref": self.ref, "operation": "group-activate", "operation_id": "activate-" + str(index),
                       "expected_configuration_revision": config["configuration_revision"], "expected_authority_epoch": config["authority_epoch"], "expected_revision": config["revision"],
                       "original_control_directory": self.config["control_directory"], "retirement_seal": retired["retirement_seal"]}
            result = group.execute(request)
            self.assertEqual(result["status"], "ok" if index == 0 else "error", result)
            if index:
                self.assertEqual(result["error"]["code"], "successor_conflict")

    def test_recomputed_backup_with_invalid_control_is_refused_before_restore(self):
        self.create()
        exported = self.ok(self.request("group-export", destination=str(self.directory / "backup.json")))
        archive = storage.read_json(Path(exported["destination"]))
        archive["payload"]["control"]["members"]["file"]["kind"] = "unsupported"
        from workflow_records import source_contract as c
        archive["snapshot_digest"] = c.digest(storage.bounded(archive["payload"]))
        corrupt = self.directory / "corrupt.json"
        storage.atomic_json(corrupt, archive, fresh=True)
        archive_digest = c.digest(storage.bounded(archive))
        self.error(self.request("group-preflight", archive=str(corrupt), archive_digest=archive_digest), "integrity_error")
        config = self.configuration("invalid-restore")
        group = LocalGroup(self.project, config)
        result = group.execute({"contract_version": m.PROFILE, "group_ref": self.ref, "operation": "group-restore", "operation_id": "invalid-restore",
                                "archive": str(corrupt), "archive_digest": archive_digest, "member_paths": {"file": config["file_path"]}})
        self.assertEqual(result["status"], "error", result)
        self.assertFalse(Path(config["file_path"]).exists())
        self.assertFalse((Path(config["control_directory"]) / "transition.json").exists())

    def registration(self, key, settings_file=False):
        result = {"provider_id": key, "implementation_ref": "adapters/" + key + ".py", "implementation_version": "1.0", "protocol_version": m.HANDOFF,
                  "project_id": self.ref["project_id"], "scope": "fixture", "capabilities": ["replicate"], "settings_non_secret": True}
        result["settings_file" if settings_file else "settings"] = "settings.json" if settings_file else {"endpoint_label": key}
        return result

    def test_two_provider_controls_and_pinned_fixture_handoff(self):
        self.create()
        (self.project / "settings.json").write_text('{"label":"original"}')
        self.ok(self.request("provider-register", registration=self.registration("alpha", True)))
        self.ok(self.request("provider-register", registration=self.registration("beta")))
        providers = self.ok(self.request("provider-list"))["providers"]
        for key, registered in providers.items():
            self.ok(self.request("provider-enable", provider_id=key, expected_generation=registered["current_generation"]))
        (self.project / "settings.json").write_text('{"label":"changed"}')
        self.ok(self.request("group-write-document", document="plan.md", content={"encoding": "utf-8", "content": "remote copy"}))
        intents = [row for row in self.ok(self.request("group-sync-status"))["targets"] if row["target"]["kind"] == "remote"]
        self.assertEqual(len(intents), 2)
        prepared = self.ok(self.request("provider-prepare", intent_id=intents[0]["intent_id"], mode="command"))
        command = prepared["request"]
        self.assertEqual(command["registration"]["settings_snapshot"], {"label": "original"})
        observation = {key: command[key] for key in ("contract_version", "group_ref", "provider_id", "generation", "operation_id", "request_digest", "logical_revision")}
        observation.update(outcome="accepted", provider_revision="opaque-provider-etag-v17")
        wrong = {**observation, "provider_id": "beta"}
        self.error(self.request("provider-observe", handoff_id=prepared["handoff_id"], observation=wrong), "binding_mismatch")
        observed = self.ok(self.request("provider-observe", handoff_id=prepared["handoff_id"], observation=observation))
        self.assertEqual(observed["evidence_kind"], "host-correlated-assertion")
        self.ok(self.request("group-write-document", document="plan.md", content={"encoding": "utf-8", "content": "second remote copy"}))
        next_intent = [row for row in self.ok(self.request("group-sync-status"))["targets"] if row["target"].get("provider_id") == "alpha"][-1]
        next_command = self.ok(self.request("provider-prepare", intent_id=next_intent["intent_id"], mode="command"))["request"]
        self.assertEqual(next_command["expected_provider_revision"], "opaque-provider-etag-v17")
        self.assertNotEqual(next_command["logical_revision"], next_command["expected_provider_revision"])
        self.assertEqual(self.ok(self.request("provider-prepare", intent_id=next_intent["intent_id"], mode="command"))["request"], next_command)
        generation = providers["alpha"]["current_generation"]
        self.ok(self.request("provider-disable", provider_id="alpha", expected_generation=generation))
        self.error(self.request("provider-prepare", intent_id=intents[0]["intent_id"], mode="command"), "provider_disabled")
        self.ok(self.request("provider-prepare", intent_id=intents[0]["intent_id"], mode="lookup"))

    def test_dispatch_bound_lookup_and_explicit_resume(self):
        self.create()
        self.ok(self.request("provider-register", registration=self.registration("alpha")))
        provider = self.ok(self.request("provider-list"))["providers"]["alpha"]
        self.ok(self.request("provider-enable", provider_id="alpha", expected_generation=provider["current_generation"]))
        self.ok(self.request("group-write-document", document="plan.md", content={"encoding": "utf-8", "content": "bounded"}))
        intent = self.ok(self.request("group-sync-status"))["targets"][0]["intent_id"]
        first = None
        for _ in range(32):
            prepared = self.ok(self.request("provider-prepare", intent_id=intent, mode="command"))
            first = first or prepared["request"]
            self.assertEqual(prepared["request"], first)
        self.error(self.request("provider-prepare", intent_id=intent, mode="command"), "limit_exceeded")
        self.ok(self.request("provider-prepare", intent_id=intent, mode="lookup"))
        self.ok(self.request("group-resume-intent", intent_id=intent, additional_attempts=1))
        self.assertEqual(self.ok(self.request("provider-prepare", intent_id=intent, mode="command"))["request"], first)

    def accepted_remote_backup(self):
        """Framework-only host assertions; no downstream provider is executed."""
        self.create()
        self.ok(self.request("provider-register", registration=self.registration("alpha")))
        provider = self.ok(self.request("provider-list"))["providers"]["alpha"]
        self.ok(self.request("provider-enable", provider_id="alpha", expected_generation=provider["current_generation"]))
        self.ok(self.request("group-write-document", document="plan.md", content={"encoding": "utf-8", "content": "closure fixture"}))
        intent = self.ok(self.request("group-sync-status"))["targets"][0]["intent_id"]
        prepared = self.ok(self.request("provider-prepare", intent_id=intent, mode="command"))
        command = prepared["request"]
        observation = {key: command[key] for key in ("contract_version", "group_ref", "provider_id", "generation", "operation_id", "request_digest", "logical_revision")}
        observation.update(outcome="accepted", provider_revision="opaque-provider-etag-42")
        self.ok(self.request("provider-observe", handoff_id=prepared["handoff_id"], observation=observation))
        unknown = {**observation, "outcome": "unknown", "provider_revision": None}
        result = self.ok(self.request("provider-observe", handoff_id=prepared["handoff_id"], observation=unknown))
        self.assertEqual(result["outcome"], "accepted")
        exported = self.ok(self.request("group-export", destination=str(self.directory / "remote-backup.json")))
        return storage.read_json(Path(exported["destination"])), exported, intent

    def test_remote_assertion_closure_rejects_rehashed_archives_before_restore_writes(self):
        original, _, intent = self.accepted_remote_backup()
        from workflow_records import source_contract as c
        variants = {
            "contract": ("contract_version", "foreign/1"),
            "group": ("group_ref", {**self.ref, "project_id": "foreign-project"}),
            "provider": ("provider_id", "foreign-provider"),
            "generation": ("generation", "generation-foreign"),
            "operation": ("operation_id", "foreign-operation"),
            "digest": ("request_digest", "sha256:" + "f" * 64),
            "logical-cut": ("logical_revision", "sha256:" + "e" * 64),
            "missing-handoff": None,
            "later-unknown-provider": ("provider_id", "foreign-provider"),
        }
        for name, mutation in variants.items():
            with self.subTest(variant=name):
                archive = copy.deepcopy(original)
                envelope = archive["payload"]["members"]["file"]
                if mutation is None:
                    envelope["handoffs"].clear()
                else:
                    position = -1 if name == "later-unknown-provider" else 0
                    envelope["deliveries"][intent]["observations"][position][mutation[0]] = mutation[1]
                m.seal(envelope)
                archive["snapshot_digest"] = c.digest(storage.bounded(archive["payload"]))
                path = self.directory / (name + "-backup.json")
                storage.atomic_json(path, archive, fresh=True)
                digest = c.digest(storage.bounded(archive))
                self.error(self.request("group-preflight", archive=str(path), archive_digest=digest), "integrity_error")
                config = self.configuration(name + "-restore")
                group = LocalGroup(self.project, config)
                response = group.execute({"contract_version": m.PROFILE, "group_ref": self.ref, "operation": "group-restore", "operation_id": name + "-restore",
                                          "archive": str(path), "archive_digest": digest, "member_paths": {"file": config["file_path"]}})
                self.assertEqual(response["status"], "error", response)
                self.assertEqual(response["error"]["code"], "integrity_error", response)
                self.assertFalse(Path(config["file_path"]).exists())
                control_directory = Path(config["control_directory"])
                self.assertFalse((control_directory / "control.json").exists())
                self.assertFalse((control_directory / "transition.json").exists())

    def reject_rehashed_group_archive(self, original, name):
        from workflow_records import source_contract as c
        archive = copy.deepcopy(original)
        for envelope in archive["payload"]["members"].values():
            m.seal(envelope)
        archive["snapshot_digest"] = c.digest(storage.bounded(archive["payload"]))
        path = self.directory / (name + "-forged.json")
        storage.atomic_json(path, archive, fresh=True)
        archive_digest = c.digest(storage.bounded(archive))
        self.error(self.request("group-preflight", archive=str(path), archive_digest=archive_digest), "integrity_error")
        config = self.configuration(name + "-restore")
        restored = LocalGroup(self.project, config)
        response = restored.execute({"contract_version": m.PROFILE, "group_ref": self.ref, "operation": "group-restore", "operation_id": name + "-restore",
                                     "archive": str(path), "archive_digest": archive_digest, "member_paths": {"file": config["file_path"]}})
        self.assertEqual(response["status"], "error", response)
        self.assertEqual(response["error"]["code"], "integrity_error", response)
        self.assertFalse(Path(config["file_path"]).exists())
        self.assertFalse((Path(config["control_directory"]) / "control.json").exists())
        self.assertFalse((Path(config["control_directory"]) / "transition.json").exists())

    @staticmethod
    def rehash_remote_command(envelope, intent, mutate):
        """Forge consistent hashes/receipts so only semantic correlation can reject."""
        from workflow_records import source_contract as c
        old_id, saved = next((key, value) for key, value in envelope["handoffs"].items() if value["intent_id"] == intent)
        command = saved["command"]
        mutate(command)
        command["request_digest"] = c.digest(c.canonical({key: value for key, value in command.items() if key != "request_digest"}))
        new_id = "handoff-" + command["request_digest"][7:]
        del envelope["handoffs"][old_id]
        envelope["handoffs"][new_id] = saved
        for observed in envelope["deliveries"].get(intent, {}).get("observations", []):
            observed["request_digest"] = command["request_digest"]
        for value in envelope["aux_operations"].values():
            request, receipt = value["request"], value["receipt"]
            if request.get("operation") == "provider-prepare" and request.get("intent_id") == intent:
                receipt["handoff_id"] = new_id
                receipt["request"] = copy.deepcopy(command) if request["mode"] == "command" else {key: command[key] for key in
                                     ("contract_version", "group_ref", "provider_id", "generation", "operation_id", "request_digest", "logical_revision")}
            elif request.get("operation") == "provider-observe" and request.get("handoff_id") == old_id:
                request["handoff_id"] = new_id
                request["observation"]["request_digest"] = command["request_digest"]
                value["request_digest"] = m.fingerprint(request)

    def test_recovery_binds_fresh_and_pending_expected_provider_revision(self):
        original, _, first = self.accepted_remote_backup()
        self.rehash_remote_command(original["payload"]["members"]["file"], first,
                                   lambda command: command.update(expected_provider_revision="forged-first-revision"))
        self.reject_rehashed_group_archive(original, "fresh-provider-revision")
        self.ok(self.request("group-write-document", document="plan.md", content={"encoding": "utf-8", "content": "successor"}))
        successor = [row for row in self.ok(self.request("group-sync-status"))["targets"] if row["target"].get("provider_id") == "alpha"][-1]["intent_id"]
        self.ok(self.request("provider-prepare", intent_id=successor, mode="command"))
        exported = self.ok(self.request("group-export", destination=str(self.directory / "successor.json")))
        valid = storage.read_json(Path(exported["destination"]))
        self.ok(self.request("group-preflight", archive=exported["destination"], archive_digest=exported["archive_digest"]))
        for name, revision in (("pending-null", None), ("pending-wrong", "forged-predecessor-revision")):
            with self.subTest(variant=name):
                archive = copy.deepcopy(valid)
                self.rehash_remote_command(archive["payload"]["members"]["file"], successor,
                                           lambda command: command.update(expected_provider_revision=revision))
                self.reject_rehashed_group_archive(archive, name)

    def test_recovery_requires_exact_accepted_predecessor(self):
        self.accepted_remote_backup()
        self.ok(self.request("group-write-document", document="plan.md", content={"encoding": "utf-8", "content": "successor"}))
        successor = [row for row in self.ok(self.request("group-sync-status"))["targets"] if row["target"].get("provider_id") == "alpha"][-1]["intent_id"]
        self.ok(self.request("provider-prepare", intent_id=successor, mode="command"))
        exported = self.ok(self.request("group-export", destination=str(self.directory / "predecessors.json")))
        valid = storage.read_json(Path(exported["destination"]))
        from workflow_records import source_contract as c, group_providers as providers
        for name, predecessor in (("skipped-predecessor", None), ("foreign-predecessor", "intent-foreign")):
            with self.subTest(variant=name):
                archive = copy.deepcopy(valid)
                envelope = archive["payload"]["members"]["file"]
                event = envelope["events"][-1]
                target = event["body"]["targets"][0]
                target["predecessor_intent_id"] = predecessor
                event["cut"] = c.digest(c.canonical(event["body"]))
                replacement = providers.intent_id(event["cut"], target)
                envelope["deliveries"][replacement] = envelope["deliveries"].pop(successor)
                handoff = next(value for value in envelope["handoffs"].values() if value["intent_id"] == successor)
                handoff["intent_id"] = replacement
                for value in envelope["aux_operations"].values():
                    if value["request"].get("intent_id") == successor:
                        value["request"]["intent_id"] = replacement
                        value["request_digest"] = m.fingerprint(value["request"])
                self.rehash_remote_command(envelope, replacement, lambda command: command.update(operation_id=replacement, logical_revision=event["cut"]))
                self.reject_rehashed_group_archive(archive, name)
        archive = copy.deepcopy(valid)
        envelope = archive["payload"]["members"]["file"]
        predecessor = envelope["events"][-1]["body"]["targets"][0]["predecessor_intent_id"]
        envelope["deliveries"][predecessor]["state"] = "unknown"
        self.reject_rehashed_group_archive(archive, "unaccepted-predecessor")

    def test_recovery_correlates_prepare_receipt_to_original_command_and_lookup(self):
        original, _, intent = self.accepted_remote_backup()
        self.ok(self.request("provider-prepare", intent_id=intent, mode="lookup"))
        exported = self.ok(self.request("group-export", destination=str(self.directory / "lookup.json")))
        original = storage.read_json(Path(exported["destination"]))
        variants = (("command-body", "command", "body"), ("lookup-body", "lookup", "body"),
                    ("handoff", "command", "handoff"), ("mode", "lookup", "mode"), ("state", "command", "state"))
        for name, mode, field in variants:
            with self.subTest(variant=name):
                archive = copy.deepcopy(original)
                envelope = archive["payload"]["members"]["file"]
                value = next(value for value in envelope["aux_operations"].values()
                             if value["request"].get("operation") == "provider-prepare" and value["request"]["mode"] == mode)
                receipt = value["receipt"]
                if field == "body":
                    receipt["request"]["provider_id"] = "foreign-provider"
                elif field == "handoff":
                    receipt["handoff_id"] = "handoff-" + "f" * 64
                elif field == "mode":
                    receipt["mode"] = "command"
                else:
                    receipt["state"] = "applied"
                self.reject_rehashed_group_archive(archive, name)

    def test_older_local_prefix_omits_later_remote_auxiliary_receipts(self):
        self.create()
        self.add_sqlite()
        self.ok(self.request("provider-register", registration=self.registration("alpha")))
        provider = self.ok(self.request("provider-list"))["providers"]["alpha"]
        self.ok(self.request("provider-enable", provider_id="alpha", expected_generation=provider["current_generation"]))
        self.ok(self.request("group-write-document", document="plan.md", content={"encoding": "utf-8", "content": "later remote cut"}))
        statuses = self.ok(self.request("group-sync-status"))["targets"]
        remote = next(row["intent_id"] for row in statuses if row["target"]["kind"] == "remote")
        prepared = self.ok(self.request("provider-prepare", intent_id=remote, mode="command"))
        observation = {key: prepared["request"][key] for key in
                       ("contract_version", "group_ref", "provider_id", "generation", "operation_id", "request_digest", "logical_revision")}
        observation.update(outcome="unknown", provider_revision=None)
        self.ok(self.request("provider-observe", handoff_id=prepared["handoff_id"], observation=observation))
        self.ok(self.request("group-resume-intent", intent_id=remote, additional_attempts=1))
        baseline = next(row["intent_id"] for row in statuses if row["target"]["kind"] == "local")
        self.assertEqual(self.ok(self.request("group-sync", intent_id=baseline))["state"], "applied")
        replica = storage.load_member(self.ok(self.request("group-configuration"))["members"]["sqlite"])
        m.validate(replica, self.ref)
        self.assertFalse(replica["handoffs"])
        self.assertFalse(any(value["request"].get("intent_id") == remote or value["request"].get("handoff_id") == prepared["handoff_id"]
                             for value in replica["aux_operations"].values()))
        exported = self.ok(self.request("group-export", destination=str(self.directory / "older-prefix.json")))
        self.ok(self.request("group-preflight", archive=exported["destination"], archive_digest=exported["archive_digest"]))
        # Catch-up and authority transfer retain the full valid reconciliation state.
        self.sync()
        self.switch("sqlite")
        self.assertEqual(self.ok(self.request("provider-prepare", intent_id=remote, mode="lookup"))["request"]["request_digest"], prepared["request"]["request_digest"])

    def test_valid_remote_assertions_restore_inactive_and_preserve_accepted_after_unknown(self):
        _, exported, intent = self.accepted_remote_backup()
        self.ok(self.request("group-preflight", archive=exported["destination"], archive_digest=exported["archive_digest"]))
        config = self.configuration("valid-remote-restore")
        group = LocalGroup(self.project, config)
        result = self.ok({"contract_version": m.PROFILE, "group_ref": self.ref, "operation": "group-restore", "operation_id": "valid-remote-restore",
                          "archive": exported["destination"], "archive_digest": exported["archive_digest"], "member_paths": {"file": config["file_path"]}}, group)
        self.assertEqual(result["store_state"], "inactive")
        status = self.ok({"contract_version": m.PROFILE, "group_ref": self.ref, "operation": "group-sync-status"}, group)
        delivery = next(row["delivery"] for row in status["targets"] if row["intent_id"] == intent)
        self.assertEqual(delivery["state"], "accepted")
        self.assertEqual(delivery["provider_revision"], "opaque-provider-etag-42")
        self.assertNotEqual(delivery["provider_revision"], delivery["logical_revision"])
        self.assertEqual([observation["outcome"] for observation in delivery["observations"]], ["accepted", "unknown"])


if __name__ == "__main__":
    unittest.main()
