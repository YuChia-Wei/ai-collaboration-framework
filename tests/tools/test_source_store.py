"""Real schema-2 transactions, Git blobs and complete pending-delivery restore."""
import base64
import copy
from contextlib import closing, contextmanager
import json
from pathlib import Path
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from tools import test_workflow_sqlite as sqlite_fixture
from tools.test_workflow_records import git, CHECKPOINT, ROOT
from workflow_records import WorkflowRecords
from workflow_records import backup, source_backup, source_store as s, source_contract as c
from workflow_records.contracts import VERSION, StoreRef, encoded, RecordError

record, REF, STORE_REF = sqlite_fixture.record, sqlite_fixture.REF, sqlite_fixture.STORE_REF


class SourceStoreTests(unittest.TestCase):
    setUpClass = classmethod(sqlite_fixture.SQLiteRecordTests.setUpClass.__func__)
    tearDownClass = classmethod(sqlite_fixture.SQLiteRecordTests.tearDownClass.__func__)

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="source-store-case-")
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name)
        self.project = self.directory / "project"
        shutil.copytree(self.base, self.project)
        self.database = self.directory / "source.sqlite"
        self.config = {"contract_version": VERSION, "default_provider": "local", "stores": {"local": {
            "kind": "local", "store_id": STORE_REF["store_id"], "repository_id": "fixture-repository", "database": str(self.database)}}}
        self.source = s.SourceStore(self.project, self.config)
        self.native = WorkflowRecords(self.project, self.config)
        self.ok(self.source.execute(self.request("source-init", operation_id="initialize-v2", schema_version=c.SCHEMA)))

    def request(self, operation, **values):
        return {"contract_version": c.PROFILE, "operation": operation, "store_ref": copy.deepcopy(STORE_REF), **values}

    def ok(self, response):
        self.assertEqual(response["status"], "ok", response)
        return response["result"]

    def error(self, response, code):
        self.assertEqual(response["status"], "error", response)
        self.assertEqual(response["error"]["code"], code, response)

    def run_source(self, operation, **values):
        return self.source.execute(self.request(operation, **values))

    def run_native(self, operation, **values):
        return self.native.execute({"contract_version": VERSION, "operation": operation, "workflow_ref": copy.deepcopy(REF), **values})

    def bind(self):
        return self.ok(self.run_source("replica-bind", operation_id="bind", new_source_namespace=True,
                       binding={"binding_id": "board", "binding_revision": 1, "source_id": "explicitly-new-fixture-namespace",
                                "project_ref": {"store_id": "board", "namespace": "personal", "project_id": "A"}}))

    def native_create(self):
        value = record()
        value["metadata"]["unknown-float"] = 1.5
        return self.ok(self.run_native("create", operation_id="create-native", record=value))

    def tables(self):
        with closing(sqlite3.connect(self.database)) as connection:
            return {name: connection.execute("SELECT * FROM " + name + " ORDER BY 1,2").fetchall()
                    for name in (*backup.TABLES, *s.TABLES)}

    def current(self):
        return self.ok(self.run_native("context"))

    def observe(self, prepared, accepted=True, channel="direct", suffix=""):
        command = prepared["command"]
        native = {"accepted": accepted, "project_ref": command["project_ref"], "operation_id": command["operation_id"],
                  "command": command["command"], "request_digest": "sha256:" + "1" * 64,
                  "expected_revision": command["expected_revision"],
                  "revision": command["expected_revision"] + (accepted and command["command"] == "replica.activate"),
                  **{key: command["payload"][key] for key in ("source_id", "workflow_id", "source_revision")},
                  "error": None if accepted else "revision_conflict"}
        if channel == "lookup":
            native = {"project_ref": command["project_ref"], "operation_id": command["operation_id"],
                      "outcome": "accepted" if accepted else "rejected", "receipt": native}
        response = {"content": [], "structuredContent": native}
        return self.run_source("replica-observe", operation_id="observe-" + command["operation_id"] + suffix,
                               intent_id=prepared["intent_id"], step_index=prepared["step_index"], channel=channel, mcp_result=response)

    def git_unit(self):
        directory = self.project / "history/unit"
        directory.mkdir(parents=True)
        files = {"workflow.yaml": b"title: Legacy title\nstatus: closed\nfuture: [retain, unknown]\n",
                 "empty": b"", "binary.zip": bytes(range(256)) * 1300, "raw-crlf.txt": b"unchanged\r\nbytes\r\n"}
        for name, value in files.items():
            (directory / name).write_bytes(value)
        (self.project / "history/INDEX.md").write_bytes(b"root control\r\n")
        git(self.project, "-c", "core.autocrlf=false", "add", "history")
        git(self.project, "-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid", "-c", "commit.gpgsign=false", "-c", "core.hooksPath=empty-hooks", "commit", "-m", "raw source fixture")
        return git(self.project, "rev-parse", "HEAD"), files

    def test_native_all_writers_capture_atomic_state_receipts_and_persisted_binding(self):
        self.bind()
        first = self.native_create()
        before = self.tables()
        replay = self.ok(self.run_native("create", operation_id="create-native", record={**record(), "metadata": {**record()["metadata"], "unknown-float": 1.5}}))
        self.assertTrue(replay["replayed"])
        self.assertEqual(before, self.tables())
        for operation, values in (("create-task", {"task": {"task_id": "T2", "title": "Additional", "status": "pending"}}),
                                  ("checkpoint", {"checkpoint": CHECKPOINT}),
                                  ("write-document", {"document": "plan.md", "content": "new raw plan\r\n"})):
            current = self.current()
            self.ok(self.run_native(operation, operation_id=operation, expected_revision=current["revision"], expected_source_head=current["source_head"], **values))
        state = self.tables()
        self.assertEqual(len(state["revisions"]), 4)
        self.assertEqual(len(state["source_snapshots"]), 4)
        self.assertEqual(len(state["replica_intents"]), 4)
        self.assertEqual([row[4] for row in state["replica_intents"]], [0, 1, 2, 3])
        for row in state["revisions"]:
            self.assertEqual(c.digest(bytes(row[3])), row[1])
        read = self.ok(self.run_source("source-list"))["items"][0]
        self.assertEqual((read["kind"], read["workflow_id"]), ("native-workflow", "example"))
        self.assertEqual(read["synchronization"]["state"], "incomplete")
        self.assertEqual(first["revision"], before["revisions"][0][1])

    def test_capacity_failure_rolls_back_native_revision_snapshot_and_intent_together(self):
        self.bind()
        self.native_create()
        before = self.tables()
        current = self.current()
        with patch.object(source_backup, "MAX_DATA_BYTES", 1):
            self.error(self.run_native("checkpoint", operation_id="rolled-back", checkpoint=CHECKPOINT,
                                      expected_revision=current["revision"], expected_source_head=current["source_head"]), "limit_exceeded")
        self.assertEqual(self.tables(), before)

    def test_committed_response_loss_replay_keeps_single_snapshot_and_intent(self):
        self.bind()
        original = s.SQLiteStore.transaction
        @contextmanager
        def lost(store, *args, **kwargs):
            with original(store, *args, **kwargs) as value:
                yield value
            if kwargs.get('write'):
                raise RecordError('storage_error','Synthetic response lost after commit')
        with patch.object(s.SQLiteStore,'transaction',lost):
            response = self.run_native('create',operation_id='create-lost',record=record())
        self.error(response,'storage_error')
        before = self.tables()
        self.assertEqual((len(before['source_snapshots']),len(before['replica_intents'])),(1,1))
        result = self.ok(self.run_native('create',operation_id='create-lost',record=record()))
        self.assertTrue(result['replayed'])
        self.assertEqual(self.tables(),before)

    def test_killed_real_writer_rolls_back_native_snapshot_outbox_and_receipt(self):
        self.bind()
        self.native_create()
        current=self.current()
        request={'contract_version':VERSION,'operation':'checkpoint','workflow_ref':REF,'operation_id':'killed-v2',
                 'checkpoint':CHECKPOINT,'expected_revision':current['revision'],'expected_source_head':current['source_head']}
        request_path=self.directory/'kill-request.json';request_path.write_bytes(encoded(request))
        config_path=self.directory/'kill-config.json';config_path.write_bytes(encoded(self.config))
        before=self.tables()
        code="""import sys,json
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
WorkflowRecords(sys.argv[2],json.loads(Path(sys.argv[3]).read_bytes())).execute(json.loads(Path(sys.argv[4]).read_bytes()))
"""
        process=subprocess.Popen([sys.executable,'-I','-B','-c',code,str(ROOT/'src/skills/workflow-records/tools'),
                                  str(self.project),str(config_path),str(request_path)],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        try:
            self.assertEqual(process.stdout.readline().strip(),b'UNCOMMITTED')
            process.kill();process.communicate(timeout=10)
        finally:
            if process.poll() is None:
                process.kill();process.communicate(timeout=5)
        self.assertEqual(self.tables(),before)

    def test_git_raw_binary_empty_large_legacy_and_root_index_are_distinct_and_exact(self):
        commit, files = self.git_unit()
        self.bind()
        request = self.request("source-import-git", operation_id="import-legacy", kind="archive-workflow", workflow_id="original-unit",
                               source_commit=commit, source_root="history/unit")
        result = self.ok(self.source.execute(request))
        (self.project / "history/unit/raw-crlf.txt").write_bytes(b"changed checkout")
        read = self.ok(self.run_source("source-read", snapshot_id=result["snapshot_id"]))
        self.assertEqual((read["title"], read["original_status"], read["workflow_id"]), ("Legacy title", "closed", "original-unit"))
        self.assertEqual(read["manifest"]["source"]["source_commit"], commit)
        self.assertEqual(read["manifest"]["workflow"]["original_id"], "original-unit")
        for file in read["manifest"]["files"]:
            value = b""
            for index in range((file["size"] + c.CHUNK - 1) // c.CHUNK):
                chunk = self.ok(self.run_source("source-chunk", snapshot_id=result["snapshot_id"], path=file["path"], index=index))
                raw = c.decode_chunk(chunk["content_base64"])
                self.assertEqual(c.digest(raw), chunk["chunk_hash"])
                value += raw
            self.assertEqual(value, files[file["path"]])
        with patch.object(s, "import_git", side_effect=AssertionError("replay must not reread Git")):
            self.assertTrue(self.ok(self.source.execute(request))["replayed"])
        root = self.ok(self.run_source("source-import-git", operation_id="root-index", kind="archive-root-index", workflow_id="root-index", source_commit=commit, source_root="history"))
        view = self.ok(self.run_source("source-read", snapshot_id=root["snapshot_id"]))
        self.assertEqual([file["path"] for file in view["manifest"]["files"]], ["INDEX.md"])
        self.assertEqual((view["kind"], view["title"], view["original_status"]), ("archive-root-index", "unknown", "unknown"))
        self.assertEqual(self.tables()["workflows"], [])

    def test_bad_or_missing_chunks_are_not_accepted_or_exported(self):
        self.native_create()
        row = self.tables()["source_snapshots"][0]
        original = self.tables()["source_blobs"]
        with closing(sqlite3.connect(self.database)) as connection:
            connection.execute("UPDATE source_blobs SET data=? WHERE hash=(SELECT hash FROM source_chunks WHERE snapshot_id=? LIMIT 1)", (b"corrupt", row[1]))
            connection.commit()
        self.error(self.run_source("source-read", snapshot_id=row[1]), "integrity_error")
        self.error(self.native.execute({"contract_version": VERSION, "operation": "export", "store_ref": STORE_REF, "destination": str(self.directory / "bad.json")}), "integrity_error")
        with closing(sqlite3.connect(self.database)) as connection:
            for key, data in original:
                connection.execute('UPDATE source_blobs SET data=? WHERE hash=?',(data,key))
            connection.execute('DELETE FROM source_chunks WHERE rowid=(SELECT rowid FROM source_chunks WHERE snapshot_id=? LIMIT 1)',(row[1],))
            connection.commit()
        self.error(self.run_source('source-read',snapshot_id=row[1]),'integrity_error')

    def test_ordering_unknown_lookup_exact_replay_late_unknown_and_binding_immutability(self):
        self.native_create()
        self.bind()
        current = self.current()
        self.ok(self.run_native("checkpoint", operation_id="second-version", checkpoint=CHECKPOINT,
                                expected_revision=current["revision"], expected_source_head=current["source_head"]))
        intents = self.tables()["replica_intents"]
        self.error(self.run_source("replica-prepare", intent_id=intents[1][1]), "predecessor_pending")
        first = self.ok(self.run_source("replica-prepare", intent_id=intents[0][1]))
        observed = self.ok(self.observe(first, channel="lookup", suffix="lookup"))
        self.assertEqual(observed["evaluation"]["outcome"], "observed_accepted")
        self.assertEqual(self.ok(self.run_source("replica-prepare", intent_id=intents[0][1]))["command"], first["command"])
        self.ok(self.observe(first))
        late = self.ok(self.run_source("replica-observe", operation_id="late-unknown", intent_id=first["intent_id"], step_index=first["step_index"], channel="direct", mcp_result=None))
        self.assertEqual(late["evaluation"]["outcome"], "unknown")
        next_step = self.ok(self.run_source("replica-prepare", intent_id=intents[0][1]))
        self.assertGreater(next_step["step_index"], first["step_index"])
        while "command" in next_step:
            self.ok(self.observe(next_step))
            next_step = self.ok(self.run_source("replica-prepare", intent_id=intents[0][1]))
        self.assertEqual(next_step["state"], "complete")
        second = self.ok(self.run_source("replica-prepare", intent_id=intents[1][1]))
        self.assertEqual(second["command"]["expected_revision"], 1)
        changed = {"binding_id": "replacement", "binding_revision": 2, "source_id": "explicitly-new-fixture-namespace", "project_ref": {"store_id": "board", "namespace": "personal", "project_id": "A"}}
        self.error(self.run_source("replica-bind", operation_id="replace-binding", binding=changed, new_source_namespace=True), "already_exists")

    def test_malformed_receipt_scope_conflict_and_unknown_never_advance(self):
        self.bind()
        self.native_create()
        intent = self.tables()["replica_intents"][0][1]
        prepared = self.ok(self.run_source("replica-prepare", intent_id=intent))
        result = self.ok(self.run_source("replica-observe", operation_id="bad-receipt", intent_id=intent, step_index=0, channel="direct",
                                        mcp_result={"content": [], "structuredContent": {"accepted": True}}))
        self.assertEqual(result["evaluation"]["outcome"], "unknown")
        self.assertEqual(self.ok(self.run_source("replica-prepare", intent_id=intent))["command"], prepared["command"])
        self.ok(self.observe(prepared, accepted=False))
        self.error(self.run_source("replica-prepare", intent_id=intent), "replica_conflict")

    def test_known_lookup_outer_scope_and_outcome_cannot_override_valid_receipt(self):
        self.bind();self.native_create()
        intent=self.tables()['replica_intents'][0][1]
        prepared=self.ok(self.run_source('replica-prepare',intent_id=intent))
        self.ok(self.observe(prepared,channel='lookup',suffix='base'))
        with closing(sqlite3.connect(self.database)) as connection:
            raw=connection.execute('SELECT value FROM replica_observations ORDER BY sequence LIMIT 1').fetchone()[0]
        original=c.parse(bytes(raw))['transport']
        for index,change in enumerate(('project','operation','outcome')):
            transport=copy.deepcopy(original)
            if change=='project':
                transport['structuredContent']['project_ref']={**transport['structuredContent']['project_ref'],'project_id':'B'}
            elif change=='operation':
                transport['structuredContent']['operation_id']='other'
            else:
                transport['structuredContent']['outcome']='rejected'
            result=self.ok(self.run_source('replica-observe',operation_id='bad-outer-'+str(index),intent_id=intent,step_index=0,channel='lookup',mcp_result=transport))
            self.assertEqual(result['evaluation']['outcome'],'unknown')
        self.assertEqual(self.ok(self.run_source('replica-prepare',intent_id=intent))['command'],prepared['command'])

    def test_backup_v2_pending_prepared_commands_restore_inactive_and_transfer_authority(self):
        self.native_create()
        self.bind()
        intent = self.tables()["replica_intents"][0][1]
        prepared = self.ok(self.run_source("replica-prepare", intent_id=intent))
        self.ok(self.observe(prepared, channel="lookup", suffix="lookup"))
        before = self.tables()
        archive = self.directory / "complete.json"
        exported = self.ok(self.native.execute({"contract_version": VERSION, "operation": "export", "store_ref": STORE_REF, "destination": str(archive)}))
        self.assertEqual(json.loads(archive.read_bytes())["format"], "workflow-backup/2")
        config = copy.deepcopy(self.config)
        config["stores"]["local"]["database"] = str(self.directory / "restored.sqlite")
        restored = WorkflowRecords(self.project, config)
        self.ok(restored.execute({"contract_version": VERSION, "operation": "restore", "store_ref": STORE_REF,
                                 "operation_id": "restore-v2", "archive": str(archive), "archive_digest": exported["archive_digest"]}))
        source = s.SourceStore(self.project, config)
        self.error(source.execute(self.request("replica-prepare", intent_id=intent)), "store_inactive")
        with closing(sqlite3.connect(config["stores"]["local"]["database"])) as connection:
            for table in s.TABLES:
                self.assertEqual(connection.execute("SELECT * FROM " + table + " ORDER BY 1,2").fetchall(), before[table])
        retirement = self.ok(self.native.execute({"contract_version": VERSION, "operation": "deactivate", "store_ref": STORE_REF,
                                                "operation_id": "retire-v2", "snapshot_digest": exported["snapshot_digest"]}))
        self.error(self.run_source("replica-prepare", intent_id=intent), "store_inactive")
        self.ok(restored.execute({"contract_version": VERSION, "operation": "activate", "store_ref": STORE_REF, "operation_id": "activate-v2",
                                 "retired_database": str(self.database), "retirement_seal": retirement["retirement_seal"]}))
        self.assertEqual(self.ok(source.execute(self.request("replica-prepare", intent_id=intent)))["command"], prepared["command"])

    def test_v1_is_not_implicitly_upgraded_and_v1_backup_still_validates(self):
        config = copy.deepcopy(self.config)
        config["stores"]["local"]["database"] = str(self.directory / "old.sqlite")
        old = WorkflowRecords(self.project, config)
        self.ok(old.execute({"contract_version": VERSION, "operation": "init", "store_ref": STORE_REF, "operation_id": "old-init"}))
        self.ok(old.execute({"contract_version": VERSION, "operation": "create", "workflow_ref": REF, "operation_id": "old-create", "record": record()}))
        source = s.SourceStore(self.project, config)
        self.error(source.execute(self.request("source-list")), "explicit_upgrade_required")
        self.error(source.execute(self.request("source-init", operation_id="implicit", schema_version=c.SCHEMA)), "explicit_upgrade_required")
        archive = self.directory / "old-backup.json"
        self.ok(old.execute({"contract_version": VERSION, "operation": "export", "store_ref": STORE_REF, "destination": str(archive)}))
        value = json.loads(archive.read_bytes())
        self.assertEqual(value["format"], "workflow-backup/1")
        backup.validate_payload(value["payload"])

    def test_v2_backup_rejects_malformed_base64_and_missing_intent_closure(self):
        self.native_create();self.bind()
        with self.native.provider(StoreRef.parse(STORE_REF)).transaction() as (connection,meta):
            value=backup.payload(connection,meta)
        corrupt=copy.deepcopy(value)
        corrupt['tables']['source_blobs'][0][1]='@@bad@@'
        with self.assertRaises(RecordError):
            backup.validate_payload(corrupt)
        corrupt=copy.deepcopy(value)
        corrupt['tables']['replica_steps']=[]
        corrupt['tables']['replica_intents']=[]
        with self.assertRaises(RecordError):
            backup.validate_payload(corrupt)

    def backup_value(self):
        with self.native.provider(StoreRef.parse(STORE_REF)).transaction() as (connection,meta):
            return backup.payload(connection,meta)

    def write_rehashed_archive(self, value, suffix):
        archive={'format':'workflow-backup/2','snapshot_digest':c.digest(encoded(value)),'payload':value}
        raw=encoded(archive)
        path=self.directory/(suffix+'.json')
        path.write_bytes(raw)
        return path,c.digest(raw)

    def test_rehashed_native_projection_corruption_is_refused(self):
        self.native_create()
        original=self.backup_value()
        for corruption in ('missing-document','attachment-bytes','header','source-header','extra-file','mode'):
            with self.subTest(corruption=corruption):
                value=copy.deepcopy(original)
                row=value['tables']['source_snapshots'][0]
                old_id=row[1]
                manifest=json.loads(base64.b64decode(row[5]))
                path='documents/plan.md' if corruption=='missing-document' else 'attachments/images/pixel.bin'
                if corruption=='missing-document':
                    manifest['files']=[file for file in manifest['files'] if file['path']!=path]
                    value['tables']['source_chunks']=[chunk for chunk in value['tables']['source_chunks'] if chunk[1]!=path]
                elif corruption in ('attachment-bytes','extra-file'):
                    path='documents/rogue.txt' if corruption=='extra-file' else path
                    data=b'independently rehashed extra or changed bytes'
                    file={'path':path,'mode':'100644','size':len(data),'sha256':c.digest(data)}
                    manifest['files']=[item for item in manifest['files'] if item['path']!=path]+[file]
                    value['tables']['source_chunks']=[chunk for chunk in value['tables']['source_chunks'] if chunk[1]!=path]
                    value['tables']['source_blobs'].append([c.digest(data),base64.b64encode(data).decode('ascii')])
                    value['tables']['source_chunks'].append([old_id,path,0,c.digest(data)])
                elif corruption=='header':
                    manifest['workflow']['title']='Not the retained native title'
                    manifest['workflow']['status']='cancelled'
                elif corruption=='source-header':
                    manifest['source']['native_operation_id']='another-native-operation'
                else:
                    next(file for file in manifest['files'] if file['path']=='documents/plan.md')['mode']='100755'
                new_id='snapshot-'+c.digest(c.canonical(manifest))[7:]
                row[1],row[5]=new_id,base64.b64encode(c.canonical(manifest)).decode('ascii')
                for chunk in value['tables']['source_chunks']:
                    if chunk[0]==old_id:
                        chunk[0]=new_id
                used={chunk[3] for chunk in value['tables']['source_chunks']}
                value['tables']['source_blobs']=[blob for blob in value['tables']['source_blobs'] if blob[0] in used]
                archive,digest=self.write_rehashed_archive(value,corruption)
                response=self.native.execute({'contract_version':VERSION,'operation':'preflight','store_ref':STORE_REF,
                                              'archive':str(archive),'archive_digest':digest})
                self.error(response,'integrity_error')
                if corruption=='missing-document':
                    config=copy.deepcopy(self.config)
                    target=self.directory/'refused-incomplete-native.sqlite'
                    config['stores']['local']['database']=str(target)
                    restored=WorkflowRecords(self.project,config)
                    self.error(restored.execute({'contract_version':VERSION,'operation':'restore','store_ref':STORE_REF,
                                                'operation_id':'refuse-incomplete-native','archive':str(archive),'archive_digest':digest}),'integrity_error')
                    self.assertFalse(target.exists())

    def test_nonobject_source_receipt_public_preflight_restore_are_structured_and_create_nothing(self):
        self.native_create();self.bind()
        value=self.backup_value()
        value['tables']['source_operations'][0][2]=base64.b64encode(c.canonical([])).decode('ascii')
        archive,digest=self.write_rehashed_archive(value,'nonobject-source-receipt')
        self.error(self.native.execute({'contract_version':VERSION,'operation':'preflight','store_ref':STORE_REF,
                                       'archive':str(archive),'archive_digest':digest}),'malformed_record')
        config=copy.deepcopy(self.config)
        target=self.directory/'refused-nonobject-restore.sqlite'
        config['stores']['local']['database']=str(target)
        restored=WorkflowRecords(self.project,config)
        self.error(restored.execute({'contract_version':VERSION,'operation':'restore','store_ref':STORE_REF,
                                    'operation_id':'refuse-nonobject','archive':str(archive),'archive_digest':digest}),'malformed_record')
        self.assertFalse(target.exists())
        config_path=self.directory/'refused-config.json';config_path.write_bytes(encoded(config))
        request_path=self.directory/'refused-restore.json'
        request_path.write_bytes(encoded({'contract_version':VERSION,'operation':'restore','store_ref':STORE_REF,
                                         'operation_id':'refuse-nonobject-cli','archive':str(archive),'archive_digest':digest}))
        process=subprocess.run([sys.executable,'-I','-B',str(ROOT/'src/skills/workflow-records/tools/workflow-records.py'),
                                '--root',str(self.project),'--config',str(config_path),'--request',str(request_path)],
                               cwd=self.directory,capture_output=True,timeout=15)
        self.assertEqual((process.returncode,process.stderr),(1,b''))
        self.error(json.loads(process.stdout),'malformed_record')
        self.assertFalse(target.exists())

    def test_isolated_source_cli_has_declared_source_only_runtime(self):
        package = self.directory / "package"
        shutil.copytree(ROOT / "src/skills/workflow-records", package)
        request = self.directory / "request.json"
        config = self.directory / "config.json"
        request.write_bytes(encoded(self.request("source-list")))
        config.write_bytes(encoded(self.config))
        process = subprocess.run([sys.executable, "-I", "-B", str(package / "tools/source-store.py"), "--root", str(self.project),
                                  "--config", str(config), "--request", str(request)], cwd=self.directory, capture_output=True, timeout=15)
        self.assertEqual((process.returncode, process.stderr), (0, b""))
        self.assertEqual(json.loads(process.stdout)["status"], "ok")
        (package / 'tools/workflow_records/__init__.py').unlink()
        process = subprocess.run([sys.executable, "-I", "-B", str(package / "tools/source-store.py"), "--root", str(self.project),
                                  "--config", str(config), "--request", str(request)], cwd=self.directory, capture_output=True, timeout=15)
        self.assertEqual((process.returncode, process.stderr), (1, b""))
        self.assertEqual(json.loads(process.stdout)['status'], 'unavailable')


if __name__ == "__main__":
    unittest.main()
