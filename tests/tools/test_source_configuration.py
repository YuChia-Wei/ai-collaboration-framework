"""Schema-3 workflow configuration and exact selected-replica fixture proofs."""
import base64
import copy
from contextlib import closing
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
import shutil
import sqlite3
import tempfile
import threading
import unittest
from unittest.mock import patch

from tools import test_workflow_sqlite as fixture
from tools import test_source_store as source_fixture
from workflow_records import WorkflowRecords
from workflow_records import source_contract as c, source_store as s, backup
from workflow_records.contracts import VERSION, encoded, RecordError, StoreRef


class SourceConfigurationTests(unittest.TestCase):
    setUpClass = classmethod(fixture.SQLiteRecordTests.setUpClass.__func__)
    tearDownClass = classmethod(fixture.SQLiteRecordTests.tearDownClass.__func__)
    ok = source_fixture.SourceStoreTests.ok
    error = source_fixture.SourceStoreTests.error
    observe = source_fixture.SourceStoreTests.observe

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="source-configuration-")
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name)
        self.project = self.directory / "project"
        shutil.copytree(self.base, self.project)
        self.database = self.directory / "records.sqlite"
        self.config = {"contract_version": VERSION, "default_provider": "local", "stores": {"local": {
            "kind": "local", "store_id": fixture.STORE_REF["store_id"], "repository_id": "fixture-repository", "database": str(self.database)}}}
        self.source = s.SourceStore(self.project, self.config)
        self.native = WorkflowRecords(self.project, self.config)
        self.ok(self.call("source-init", operation_id="init3", schema_version=c.SCHEMA3))
        self.ok(self.run_native("create", operation_id="create", record=fixture.record()))

    def request(self, operation, **values):
        return {"contract_version": c.PROFILE2, "operation": operation, "store_ref": copy.deepcopy(fixture.STORE_REF), **values}

    def call(self, operation, **values):
        return self.source.execute(self.request(operation, **values))

    def run_source(self, operation, **values):
        return self.source.execute({"contract_version": c.PROFILE, "operation": operation, "store_ref": fixture.STORE_REF, **values})

    def run_native(self, operation, workflow_id="example", **values):
        return self.native.execute({"contract_version": VERSION, "operation": operation,
                                    "workflow_ref": {**fixture.REF, "workflow_id": workflow_id}, **values})

    def configuration(self, workflow_id="example"):
        return self.ok(self.call("source-configuration", workflow_id=workflow_id))

    def change(self, operation, operation_id=None, workflow_id="example", **values):
        return self.call(operation, operation_id=operation_id or operation + str(self.configuration(workflow_id)["configuration_revision"]),
                         workflow_id=workflow_id, expected_configuration_revision=self.configuration(workflow_id)["configuration_revision"], **values)

    def add(self, binding_id="board", source_id="fresh", workflow_id="example"):
        return self.ok(self.change("replica-add", workflow_id=workflow_id, binding={"binding_id": binding_id,
            "project_ref": {"store_id": "board", "namespace": "personal", "project_id": "A"}, "source_id": source_id}, new_source_namespace=True))

    def checkpoint(self, operation_id="checkpoint"):
        current = self.ok(self.run_native("context"))
        return self.run_native("checkpoint", operation_id=operation_id, checkpoint=copy.deepcopy(fixture.CHECKPOINT),
                               expected_revision=current["revision"], expected_source_head=current["source_head"])

    def prepare(self, operation_id="read", binding_id=None):
        values = {"binding_id": binding_id} if binding_id is not None else {}
        return self.ok(self.change("read-prepare", operation_id=operation_id, **values))

    def response(self, prepared):
        query = prepared["request"]
        payload = query["payload"]
        with closing(sqlite3.connect(self.database)) as connection:
            row = connection.execute("SELECT id,manifest FROM source_snapshots WHERE revision=?", (payload["source_revision"],)).fetchone()
            manifest = c.parse(bytes(row[1]))
            value = {"project_ref": query["project_ref"], **{key: payload[key] for key in ("source_id", "workflow_id", "source_revision")},
                     "revision": 7, "manifest_hash": c.digest(c.canonical(manifest)), "complete": True}
            if query["query"] == "replica.read":
                value.update(metadata={"source": manifest["source"], "workflow": manifest["workflow"]},
                             file_count=len(manifest["files"]), total_bytes=sum(file["size"] for file in manifest["files"]))
            elif query["query"] == "replica.manifest":
                offset = payload["offset"]
                value.update(offset=offset, total=len(manifest["files"]), files=manifest["files"][offset:offset + 50], has_more=offset + 50 < len(manifest["files"]))
            else:
                chunk = connection.execute("SELECT b.hash,b.data FROM source_chunks sc JOIN source_blobs b ON b.hash=sc.hash WHERE sc.snapshot_id=? AND sc.path=? AND sc.chunk_index=?", (row[0], payload["path"], payload["index"])).fetchone()
                value.update(path=payload["path"], index=payload["index"], chunk_hash=chunk[0], content_base64=base64.b64encode(bytes(chunk[1])).decode("ascii"))
        return {"content": [], "structuredContent": copy.deepcopy(value)}

    def finish(self, prepared):
        proof_id = prepared["proof_id"]
        while prepared["read_state"] != "complete":
            prepared = self.ok(self.call("read-accept", operation_id=proof_id + "-" + str(prepared["step_index"]),
                              proof_id=proof_id, step_index=prepared["step_index"], mcp_result=self.response(prepared)))
        return proof_id

    def select(self, proof_id):
        binding = self.configuration()["bindings"]["board"]
        return self.change("select-read-source", read_source={"kind": "replica", "binding_id": "board", "generation_id": binding["generation_id"]}, proof_id=proof_id)

    def deliver(self):
        with closing(sqlite3.connect(self.database)) as connection:
            intents = [row[0] for row in connection.execute("SELECT id FROM replica_intents ORDER BY sequence")]
        for intent in intents:
            while True:
                prepared = self.ok(self.run_source("replica-prepare", intent_id=intent))
                if prepared.get("state") == "complete":
                    break
                self.ok(self.observe(prepared))

    def test_offline_default_scoped_config_and_native_revision_mapping(self):
        self.assertEqual(self.configuration()["read_source"], {"kind": "sqlite"})
        with patch.object(c, "validate", side_effect=AssertionError("offline must not need remote schema")):
            prepared = self.prepare()
            result = self.ok(self.call("read-result", proof_id=prepared["proof_id"]))
            self.assertEqual(result["freshness"], "current")
            self.assertEqual(result["provider_revision"], None)
            self.assertEqual(result["logical_revision"], "native-" + result["native_state_revision"][7:])
            self.assertEqual(result["native_state"]["metadata"]["title"], fixture.record()["metadata"]["title"])
            archive = self.directory / "offline.json"
            self.ok(self.native.execute({"contract_version": VERSION, "operation": "export", "store_ref": fixture.STORE_REF, "destination": str(archive)}))
        self.assertEqual(json.loads(archive.read_bytes())["format"], "workflow-backup/3")

    def test_configuration_cas_replay_collision_and_workflow_isolation(self):
        self.ok(self.run_native("create", workflow_id="other", operation_id="create-other", record=fixture.record()))
        request = self.request("replica-add", workflow_id="example", operation_id="add", expected_configuration_revision=0,
                               binding={"binding_id": "board", "project_ref": {"store_id": "board", "namespace": "personal", "project_id": "A"}, "source_id": "fresh"}, new_source_namespace=True)
        first = self.ok(self.source.execute(request))
        self.assertTrue(self.ok(self.source.execute(request))["replayed"])
        changed = copy.deepcopy(request)
        changed["binding"]["source_id"] = "changed"
        self.error(self.source.execute(changed), "operation_id_conflict")
        stale = copy.deepcopy(request)
        stale["operation_id"] = "stale"
        self.error(self.source.execute(stale), "configuration_conflict")
        self.assertEqual(self.configuration("other")["configuration_revision"], 0)
        with closing(sqlite3.connect(self.database)) as connection:
            self.assertEqual(connection.execute("SELECT count(*) FROM replica_intents").fetchone()[0], 1)
        self.assertEqual(first["configuration_revision"], 1)

    def test_update_remove_preserve_original_payload_and_future_membership(self):
        self.add()
        old = self.configuration()["bindings"]["board"]["generation_id"]
        with closing(sqlite3.connect(self.database)) as connection:
            original = connection.execute("SELECT * FROM replica_steps ORDER BY 1,2").fetchall()
        self.ok(self.change("replica-update", binding={"binding_id": "board", "project_ref": {"store_id": "board", "namespace": "personal", "project_id": "B"}, "source_id": "fresh2"}, expected_binding_generation=old, new_source_namespace=True))
        new = self.configuration()["bindings"]["board"]["generation_id"]
        self.ok(self.checkpoint())
        self.ok(self.change("replica-remove", binding_id="board", expected_binding_generation=new))
        self.ok(self.checkpoint("after-remove"))
        with closing(sqlite3.connect(self.database)) as connection:
            self.assertEqual(connection.execute("SELECT * FROM replica_steps WHERE intent_id IN (SELECT id FROM replica_intents WHERE binding_id=?) ORDER BY 1,2", (old,)).fetchall(), original)
            memberships = connection.execute("SELECT binding_id,count(*) FROM replica_intents GROUP BY binding_id").fetchall()
            self.assertEqual(dict(memberships), {old: 1, new: 2})
        self.export_and_restore()

    def export_and_restore(self):
        archive = self.directory / "backup.json"
        result = self.ok(self.native.execute({"contract_version": VERSION, "operation": "export", "store_ref": fixture.STORE_REF, "destination": str(archive)}))
        restored_config = copy.deepcopy(self.config)
        restored_config["stores"]["local"]["database"] = str(self.directory / "restored.sqlite")
        restored = WorkflowRecords(self.project, restored_config)
        self.ok(restored.execute({"contract_version": VERSION, "operation": "restore", "operation_id": "restore", "store_ref": fixture.STORE_REF,
                                 "archive": str(archive), "archive_digest": result["archive_digest"]}))
        selected = s.SourceStore(self.project, restored_config)
        self.assertEqual(self.ok(selected.execute(self.request("source-configuration", workflow_id="example"))), self.configuration())
        self.error(selected.execute(self.request("read-prepare", operation_id="inactive", workflow_id="example", expected_configuration_revision=self.configuration()["configuration_revision"])), "store_inactive")
        return archive

    def test_complete_replica_selection_proof_and_no_local_fallback(self):
        self.add()
        proof = self.prepare(binding_id="board")
        self.error(self.select(proof["proof_id"]), "source_incomplete")
        proof_id = self.finish(proof)
        self.ok(self.select(proof_id))
        # Verified remote bytes make a version readable without forging command
        # activation receipts; synchronization remains separately incomplete.
        self.ok(self.change("read-prepare", operation_id="unconfirmed"))
        with closing(sqlite3.connect(self.database)) as connection:
            self.assertEqual(connection.execute("SELECT count(*) FROM replica_observations").fetchone()[0], 0)
        self.deliver()
        prepared = self.prepare("selected")
        self.error(self.call("read-accept", operation_id="offline", proof_id=prepared["proof_id"], step_index=0,
                             mcp_result={"content": [], "isError": True}), "source_unavailable")
        selected = self.finish(prepared)
        result = self.ok(self.call("read-result", proof_id=selected))
        self.assertEqual((result["provider_revision"], result["freshness"]), (7, "current"))
        self.ok(self.checkpoint())
        result = self.ok(self.call("read-result", proof_id=selected))
        self.assertEqual(result["freshness"], "behind")
        self.assertNotEqual(result["native_state_revision"], self.ok(self.run_native("context"))["revision"])
        self.export_and_restore()

    def test_wrong_scope_corrupt_dual_transport_missing_page_and_stale_cut_rejected(self):
        self.add()
        prepared = self.prepare(binding_id="board")
        wrong = self.response(prepared)
        wrong["structuredContent"]["project_ref"]["project_id"] = "wrong"
        self.error(self.call("read-accept", operation_id="wrong", proof_id=prepared["proof_id"], step_index=0, mcp_result=wrong), "source_mismatch")
        inconsistent = self.response(prepared)
        inconsistent["content"] = [{"type": "text", "text": "{}"}]
        self.error(self.call("read-accept", operation_id="dual", proof_id=prepared["proof_id"], step_index=0, mcp_result=inconsistent), "invalid_transport")
        proof_id = self.finish(prepared)
        self.ok(self.checkpoint())
        self.error(self.select(proof_id), "source_cut_conflict")
        self.assertEqual(self.configuration()["read_source"], {"kind": "sqlite"})

    def test_reconfiguration_invalidates_read_token_and_selected_binding_is_protected(self):
        self.add()
        proof_id = self.finish(self.prepare(binding_id="board"))
        self.ok(self.select(proof_id))
        binding = self.configuration()["bindings"]["board"]
        self.error(self.change("replica-remove", binding_id="board", expected_binding_generation=binding["generation_id"]), "read_source_in_use")
        self.ok(self.change("select-read-source", operation_id="back-local", read_source={"kind": "sqlite"}))
        self.error(self.call("read-result", proof_id=proof_id), "configuration_conflict")

    def test_atomic_baseline_capacity_rollback_leaves_no_configuration_or_binding(self):
        with patch.object(s, "receipt", side_effect=RecordError("limit_exceeded", "fixture capacity")):
            self.error(self.change("replica-add", binding={"binding_id": "board", "project_ref": {"store_id": "board", "namespace": "personal", "project_id": "A"}, "source_id": "fresh"}, new_source_namespace=True), "limit_exceeded")
        self.assertEqual(self.configuration()["configuration_revision"], 0)
        with closing(sqlite3.connect(self.database)) as connection:
            for table in ("source_configurations", "source_bindings", "replica_intents", "replica_steps"):
                self.assertEqual(connection.execute("SELECT count(*) FROM " + table).fetchone()[0], 0)

    def test_legacy_profile_on_schema2_keeps_behavior_and_refuses_new_capability(self):
        other = self.directory / "legacy.sqlite"
        config = copy.deepcopy(self.config)
        config["stores"]["local"]["database"] = str(other)
        legacy = s.SourceStore(self.project, config)
        self.ok(legacy.execute({"contract_version": c.PROFILE, "operation": "source-init", "store_ref": fixture.STORE_REF, "operation_id": "legacy", "schema_version": c.SCHEMA}))
        self.error(legacy.execute(self.request("source-configuration", workflow_id="example")), "explicit_upgrade_required")
        self.error(legacy.execute(self.request("source-init", operation_id="implicit", schema_version=c.SCHEMA3)), "explicit_upgrade_required")
        self.ok(legacy.execute({"contract_version": c.PROFILE, "operation": "source-list", "store_ref": fixture.STORE_REF}))

    def test_concurrent_configuration_writers_have_one_winner_and_no_lost_membership(self):
        barrier = threading.Barrier(2)
        def writer(name):
            barrier.wait(timeout=10)
            return self.call("replica-add", operation_id="concurrent-" + name, workflow_id="example", expected_configuration_revision=0,
                             binding={"binding_id": name, "project_ref": {"store_id": "board", "namespace": "personal", "project_id": "A"}, "source_id": name}, new_source_namespace=True)
        with ThreadPoolExecutor(max_workers=2) as executor:
            results = list(executor.map(writer, ("first", "second")))
        self.assertEqual(sum(value["status"] == "ok" for value in results), 1)
        self.assertEqual([value["error"]["code"] for value in results if value["status"] != "ok"], ["configuration_conflict"])
        self.assertEqual(len(self.configuration()["bindings"]), 1)
        self.ok(self.checkpoint())
        self.export_and_restore()

    def test_native_capture_failure_rolls_back_state_and_configured_intent(self):
        self.add()
        original = self.ok(self.run_native("context"))
        with closing(sqlite3.connect(self.database)) as connection:
            before = {name: connection.execute("SELECT count(*) FROM " + name).fetchone()[0]
                      for name in ("source_snapshots", "replica_intents", "operations", "revisions", "source_snapshot_configurations")}
        with patch.object(s, "enqueue", side_effect=RecordError("limit_exceeded", "fixture pending capacity")):
            self.error(self.checkpoint(), "limit_exceeded")
        self.assertEqual(self.ok(self.run_native("context"))["revision"], original["revision"])
        with closing(sqlite3.connect(self.database)) as connection:
            after = {name: connection.execute("SELECT count(*) FROM " + name).fetchone()[0] for name in before}
        self.assertEqual(after, before)

    def test_missing_manifest_corrupt_chunk_and_changed_provider_revision_are_rejected(self):
        self.add()
        prepared = self.prepare(binding_id="board")
        first_request = self.request("read-accept", operation_id="header", proof_id=prepared["proof_id"], step_index=0, mcp_result=self.response(prepared))
        prepared = self.ok(self.source.execute(first_request))
        self.assertTrue(self.ok(self.source.execute(first_request))["replayed"])
        missing = self.response(prepared)
        missing["structuredContent"]["files"] = missing["structuredContent"]["files"][:-1]
        self.error(self.call("read-accept", operation_id="missing", proof_id=prepared["proof_id"], step_index=1, mcp_result=missing), "integrity_error")
        changed = self.response(prepared)
        changed["structuredContent"]["revision"] += 1
        self.error(self.call("read-accept", operation_id="provider-drift", proof_id=prepared["proof_id"], step_index=1, mcp_result=changed), "source_mismatch")
        prepared = self.ok(self.call("read-accept", operation_id="manifest", proof_id=prepared["proof_id"], step_index=1, mcp_result=self.response(prepared)))
        corrupt = self.response(prepared)
        corrupt["structuredContent"]["content_base64"] = base64.b64encode(b"wrong").decode("ascii")
        self.error(self.call("read-accept", operation_id="corrupt", proof_id=prepared["proof_id"], step_index=2, mcp_result=corrupt), "integrity_error")
        self.error(self.call("read-result", proof_id=prepared["proof_id"]), "source_incomplete")

    def test_backup_rejects_missing_membership_proof_and_rewritten_generation(self):
        self.add()
        proof_id = self.finish(self.prepare(binding_id="board"))
        self.ok(self.select(proof_id))
        with self.source.service.provider(StoreRef.parse(fixture.STORE_REF)).transaction() as (connection, meta):
            value = backup.payload(connection, meta)
        backup.validate_payload(value)
        missing = copy.deepcopy(value)
        missing["tables"]["source_read_evidence"].pop()
        with self.assertRaises(RecordError):
            backup.validate_payload(missing)
        missing = copy.deepcopy(value)
        missing["tables"]["replica_intents"] = []
        missing["tables"]["replica_steps"] = []
        with self.assertRaises(RecordError):
            backup.validate_payload(missing)
        rewritten = copy.deepcopy(value)
        config = c.parse(base64.b64decode(rewritten["tables"]["source_configurations"][0][2]))
        config["bindings"]["board"]["target"]["source_id"] = "changed"
        rewritten["tables"]["source_configurations"][0][2] = base64.b64encode(c.canonical(config)).decode("ascii")
        with self.assertRaises(RecordError):
            backup.validate_payload(rewritten)

    def test_full_manifest_requires_multiple_pages_and_preserves_empty_files(self):
        record = fixture.record()
        record["documents"].update({"empty-" + str(index) + ".txt": "" for index in range(55)})
        self.ok(self.run_native("create", workflow_id="paged", operation_id="create-paged", record=record))
        self.add(workflow_id="paged", source_id="paged-fresh")
        prepared = self.ok(self.call("read-prepare", operation_id="paged-proof", workflow_id="paged", expected_configuration_revision=1, binding_id="board"))
        proof_id = self.finish(prepared)
        result = self.ok(self.call("read-result", proof_id=proof_id))
        self.assertGreater(len(result["manifest"]["files"]), 50)
        self.assertEqual(sum(file["size"] == 0 for file in result["manifest"]["files"]), 55)
        with closing(sqlite3.connect(self.database)) as connection:
            pages = [c.parse(bytes(row[0])) for row in connection.execute("SELECT value FROM source_read_evidence WHERE proof_id=?", (proof_id,))]
        self.assertEqual(sorted(page["offset"] for page in pages if "offset" in page), [0, 50])


if __name__ == "__main__":
    unittest.main()
