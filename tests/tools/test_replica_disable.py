"""Explicit replica cutoff, retained-history reconciliation and backup closure."""
import base64
import copy
import json
from contextlib import closing
import sqlite3
import unittest
from unittest.mock import patch

from tools import test_source_store as fixtures
STORE_REF, VERSION = fixtures.STORE_REF, fixtures.VERSION
from workflow_records import WorkflowRecords, source_store as s, source_contract as c, backup
from workflow_records.contracts import RecordError, StoreRef


class ReplicaDisableTests(unittest.TestCase):
    """Reuse real fixture helpers without rediscovering the original test class."""


for _name, _value in fixtures.SourceStoreTests.__dict__.items():
    if not _name.startswith("__") and not _name.startswith("test_"):
        setattr(ReplicaDisableTests, _name, _value)


def _status(self):
    return self.ok(self.run_source("binding-status", binding_id="board"))


def _disable(self, operation_id="disable-board", **changes):
    state = _status(self)
    return self.request("binding-disable", operation_id=operation_id, binding_id="board",
                        expected_binding_digest=changes.get("expected_binding_digest", state["binding_digest"]),
                        expected_snapshot_sequence=changes.get("expected_snapshot_sequence", state["snapshot_sequence"]))


def _revise(self, operation_id):
    current = self.current()
    return self.ok(self.run_native("write-document", operation_id=operation_id, document="plan.md", content=operation_id,
        expected_revision=current["revision"], expected_source_head=current["source_head"]))


def test_cutoff_retains_original_bytes_other_binding_and_lookup(self):
    self.bind(); self.native_create()
    target = {"binding_id":"other", "binding_revision":1, "source_id":"new-other",
              "project_ref":{"store_id":"board","namespace":"personal","project_id":"B"}}
    self.ok(self.run_source("replica-bind", operation_id="bind-other", binding=target, new_source_namespace=True))
    before = self.tables()
    intent = before["replica_intents"][0][1]
    prepared = self.ok(self.run_source("replica-prepare", intent_id=intent))
    request = _disable(self)
    receipt = self.ok(self.source.execute(request))
    self.assertEqual(receipt["request"], request)
    self.assertEqual(receipt["cutoff_sequence"], 1)
    _revise(self,"after-disable")
    after = self.tables()
    for name in ("source_bindings", "replica_steps", "replica_intents"):
        retained = [row for row in after[name] if row in before[name]]
        self.assertEqual(retained, before[name])
    self.assertEqual(len(after["source_snapshots"]), 2)
    self.assertEqual([row[3] for row in after["replica_intents"]], ["board","other","other"])
    exported = self.ok(self.run_native("export-files", destination=str(self.directory / "readable-current"),
                                     expected_revision=self.current()["revision"]))
    self.ok(self.run_native("preflight-files", directory=exported["destination"],
                           manifest_digest=exported["manifest_digest"]))
    self.assertEqual(self.tables(), after)
    self.error(self.run_source("replica-prepare", intent_id=intent), "binding_disabled")
    lookup = self.ok(self.run_source("replica-prepare", intent_id=intent, mode="lookup"))
    self.assertEqual(lookup["command"], prepared["command"])
    self.assertEqual(lookup["request"]["query"], "replica.operation.get")
    self.ok(self.observe(lookup, channel="lookup"))
    self.ok(self.observe(prepared, suffix="-late-direct"))
    self.assertEqual(_status(self)["state"], "disabled")
    replay = self.ok(self.source.execute(request))
    self.assertTrue(replay["replayed"])
    self.assertEqual(replay["cutoff_sequence"], 1)
    changed = {**request,"expected_snapshot_sequence":2}
    self.error(self.source.execute(changed), "operation_id_conflict")
    backup.validate_payload(self.backup_value())


def test_cas_response_loss_zero_cut_and_no_implicit_upgrade(self):
    self.bind()
    request = _disable(self)
    self.assertEqual(request["expected_snapshot_sequence"], 0)
    _status(self)
    with self.native.provider(StoreRef.parse(STORE_REF)).transaction() as (_,meta):
        self.assertEqual(meta["schema_version"], c.SCHEMA)
    self.error(self.source.execute({**request,"expected_binding_digest":"sha256:"+"0"*64}), "revision_conflict")
    original = s.SQLiteStore.transaction
    from contextlib import contextmanager
    @contextmanager
    def lost(store,*args,**kwargs):
        with original(store,*args,**kwargs) as value:
            yield value
        if kwargs.get("write"):
            raise RecordError("storage_error","synthetic committed response loss")
    with patch.object(s.SQLiteStore,"transaction",lost):
        self.error(self.source.execute(request),"storage_error")
    self.assertTrue(self.ok(self.source.execute(request))["replayed"])
    self.native_create()
    self.assertEqual(self.tables()["replica_intents"], [])
    self.assertEqual(self.backup_value()["schema_version"], c.SCHEMA21)
    backup.validate_payload(self.backup_value())
    self.error(self.source.execute(_disable(self,"second-disable")), "binding_disabled")


def test_disable_capacity_failure_rolls_back_marker_receipt_and_cut(self):
    self.bind(); self.native_create()
    before = self.tables()
    request = _disable(self)
    from workflow_records import source_backup
    with patch.object(source_backup,"MAX_DATA_BYTES",1):
        self.error(self.source.execute(request),"limit_exceeded")
    self.assertEqual(self.tables(),before)
    with self.native.provider(StoreRef.parse(STORE_REF)).transaction() as (_,meta):
        self.assertEqual(meta["schema_version"],c.SCHEMA)
    self.assertEqual(_status(self)["state"],"active")
    self.ok(self.source.execute(request))


def test_stale_cut_rolls_back_and_later_lookup_bypasses_dispatch_predecessor(self):
    self.bind(); self.native_create()
    request = _disable(self)
    _revise(self,"before-disable")
    before = self.tables()
    self.error(self.source.execute(request), "revision_conflict")
    self.assertEqual(self.tables(), before)
    self.ok(self.source.execute(_disable(self)))
    later = self.tables()["replica_intents"][1][1]
    self.ok(self.run_source("replica-prepare", intent_id=later, mode="lookup"))
    self.error(self.run_source("replica-prepare", intent_id=later), "binding_disabled")


def test_backup_export_preflight_inactive_restore_and_corrupt_controls(self):
    self.bind(); self.native_create()
    self.ok(self.source.execute(_disable(self)))
    _revise(self,"post-cut")
    original = self.backup_value()
    backup.validate_payload(original)
    path = self.directory/"disabled-backup.json"
    exported = self.ok(self.native.execute({"contract_version":VERSION,"operation":"export","store_ref":STORE_REF,"destination":str(path)}))
    self.assertEqual(json.loads(path.read_bytes())["format"], "workflow-backup/2.1")
    backup.preflight(str(path),exported["archive_digest"])
    config = copy.deepcopy(self.config)
    config["stores"]["local"]["database"] = str(self.directory/"restored.sqlite")
    restored = WorkflowRecords(self.project,config)
    self.ok(restored.execute({"contract_version":VERSION,"operation":"restore","store_ref":STORE_REF,
        "operation_id":"restore-disabled","archive":str(path),"archive_digest":exported["archive_digest"]}))
    reader = s.SourceStore(self.project,config)
    state = self.ok(reader.execute(self.request("binding-status",binding_id="board")))
    self.assertEqual(state["state"],"disabled")
    self.assertTrue(self.ok(reader.execute(state["disable_receipt"]["request"]))["replayed"])
    self.error(reader.execute(_disable(self,"restore-disable")),"store_inactive")
    with closing(sqlite3.connect(config["stores"]["local"]["database"])) as connection:
        for name in s.TABLES:
            self.assertEqual(connection.execute("SELECT * FROM "+name+" ORDER BY 1,2").fetchall(),self.tables()[name])
    for corruption in ("missing-control","cut-request","request-digest","binding-digest","duplicate-control","precut-gap","postcut-intent","old-marker"):
        with self.subTest(corruption=corruption):
            value=copy.deepcopy(original)
            controls=value["tables"]["source_operations"]
            row=next(row for row in controls if row[0]=="disable-board")
            receipt=json.loads(base64.b64decode(row[2]))
            if corruption=="missing-control":
                controls.remove(row)
            elif corruption=="old-marker":
                value["schema_version"]=c.SCHEMA
            elif corruption=="precut-gap":
                value["tables"]["replica_steps"]=[];value["tables"]["replica_intents"]=[]
            elif corruption=="postcut-intent":
                value["tables"]["source_snapshots"].reverse()
                # A forged zero cut leaves a retained postcut intent.
                receipt["cutoff_sequence"]=0;receipt["request"]["expected_snapshot_sequence"]=0
                from workflow_records.sqlite_store import request_digest
                row[1]=request_digest(receipt["request"])
            elif corruption=="duplicate-control":
                duplicate=copy.deepcopy(row)
                receipt["operation_id"]="duplicate-disable";receipt["request"]["operation_id"]="duplicate-disable"
                from workflow_records.sqlite_store import request_digest
                duplicate[0]="duplicate-disable";duplicate[1]=request_digest(receipt["request"])
                duplicate[2]=base64.b64encode(c.canonical(receipt)).decode("ascii");controls.append(duplicate)
            elif corruption=="cut-request":
                receipt["cutoff_sequence"]=2
            elif corruption=="request-digest":
                row[1]="sha256:"+"0"*64
            elif corruption=="binding-digest":
                receipt["binding_digest"]="sha256:"+"0"*64
            if corruption not in ("missing-control","duplicate-control"):
                row[2]=base64.b64encode(c.canonical(receipt)).decode("ascii")
            with self.assertRaises(RecordError):
                backup.validate_payload(value)


for _test in (test_cutoff_retains_original_bytes_other_binding_and_lookup,
              test_cas_response_loss_zero_cut_and_no_implicit_upgrade,
              test_disable_capacity_failure_rolls_back_marker_receipt_and_cut,
              test_stale_cut_rolls_back_and_later_lookup_bypasses_dispatch_predecessor,
              test_backup_export_preflight_inactive_restore_and_corrupt_controls):
    setattr(ReplicaDisableTests,_test.__name__,_test)
