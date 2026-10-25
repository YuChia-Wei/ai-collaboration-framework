"""Section 16: atomic native progress revisions, using real SQLite stores."""
import copy
from contextlib import closing, contextmanager
import sqlite3
import unittest
from unittest.mock import patch

from tools import test_source_store as fixture
from workflow_records import WorkflowRecords, backup, source_backup, source_store
from workflow_records import sqlite_store
from workflow_records.contracts import MAX_FILE, VERSION, RecordError, StoreRef, decode_json, encoded


class WorkflowRevisionTests(unittest.TestCase):
    setUpClass = classmethod(fixture.SourceStoreTests.setUpClass.__func__)
    tearDownClass = classmethod(fixture.SourceStoreTests.tearDownClass.__func__)
    setUp = fixture.SourceStoreTests.setUp
    request = fixture.SourceStoreTests.request
    ok = fixture.SourceStoreTests.ok
    error = fixture.SourceStoreTests.error
    run_source = fixture.SourceStoreTests.run_source
    run_native = fixture.SourceStoreTests.run_native
    current = fixture.SourceStoreTests.current
    tables = fixture.SourceStoreTests.tables
    bind = fixture.SourceStoreTests.bind
    backup_value = fixture.SourceStoreTests.backup_value

    def prepare(self):
        self.bind()
        value = fixture.record()
        value['metadata']['phase'] = 'implement'
        value['tasks'].append({'task_id': 'T2', 'title': 'Review', 'status': 'pending', 'future': [1, 2]})
        self.ok(self.run_native('create', operation_id='create', record=value))
        current = self.current()
        return {'contract_version': VERSION, 'operation': 'revise-workflow', 'workflow_ref': fixture.REF,
                'operation_id': 'progress', 'expected_revision': current['revision'],
                'expected_source_head': current['source_head'],
                'metadata_patch': {'phase': 'review', 'custom': {'new': True}},
                'task_patches': [{'task_id': 'T1', 'status': 'completed'}, {'task_id': 'T2', 'status': 'in_progress'}],
                'documents': {'reports/result.md': '# 驗證完成\r\n', 'plan.md': '# Updated plan\n'}}

    def state(self):
        with closing(sqlite3.connect(self.database)) as connection:
            row = connection.execute('SELECT state FROM revisions JOIN workflows ON revisions.workflow_id=workflows.id AND revisions.revision=workflows.revision').fetchone()
            return decode_json(bytes(row[0]))

    def test_atomic_progress_preserves_extensions_and_enqueues_each_saved_target_once(self):
        request = self.prepare()
        binding = {'binding_id': 'second', 'binding_revision': 1, 'source_id': 'new-second-fixture',
                   'project_ref': {'store_id': 'board', 'namespace': 'personal', 'project_id': 'B'}}
        self.ok(self.run_source('replica-bind', operation_id='bind-second', new_source_namespace=True, binding=binding))
        original = self.state()
        before = self.tables()
        receipt = self.ok(self.native.execute(request))
        state = self.state()
        self.assertEqual(state['metadata'], {**original['metadata'], 'phase': 'review', 'custom': {'new': True}})
        self.assertEqual(state['tasks'], [{**original['tasks'][0], 'status': 'completed'},
                                          {**original['tasks'][1], 'status': 'in_progress'}])
        for key in ('entrypoint', 'attachments', 'checkpoint'):
            self.assertEqual(state[key], original[key])
        self.assertEqual(self.ok(self.run_native('read', document='reports/result.md'))['content'], '# 驗證完成\r\n')
        after = self.tables()
        for table in ('revisions', 'operations', 'source_snapshots'):
            self.assertEqual(len(after[table]), len(before[table]) + 1)
        self.assertEqual(len(after['replica_intents']), len(before['replica_intents']) + 2)
        self.assertEqual(after['replica_observations'], before['replica_observations'])
        replay = self.ok(self.native.execute(request))
        self.assertEqual(replay, {**receipt, 'replayed': True})
        self.assertEqual(after, self.tables())
        backup.validate_payload(self.backup_value())

    def test_invalid_selectors_shapes_paths_and_protected_fields_roll_back(self):
        original = self.prepare()
        cases = [({}, 'invalid_input'),
                 ({'task_patches': [{}]}, 'invalid_input'),
                 ({'task_patches': [{'task_id': 'T1'}]}, 'invalid_input'),
                 ({'task_patches': [{'task_id': 'unknown', 'status': 'done'}]}, 'invalid_input'),
                 ({'task_patches': [{'task_id': 'T1', 'status': 'done'}] * 2}, 'invalid_input'),
                 ({'task_patches': [{'task_id': 'T1', 'title': ''}]}, 'malformed_record'),
                 ({'metadata_patch': {'authority': ''}}, 'malformed_record'),
                 ({'documents': {'PLAN.md': 'collision'}}, 'invalid_input'),
                 ({'documents': {'images/pixel.bin': 'attachment'}}, 'invalid_input'),
                 ({'documents': {'.WORKFLOW-records/hidden': 'reserved'}}, 'invalid_input'),
                 ({'documents': {'../escape': 'unsafe'}}, 'unsafe_path'),
                 ({'documents': {'new': '\x00'}}, 'unsupported_format'),
                 ({'documents': {'new': 5}}, 'invalid_input'),
                 ({'metadata_patch': []}, 'invalid_input'),
                 ({'task_patches': {}}, 'invalid_input'),
                 ({'entrypoint': 'another.md'}, 'invalid_input'),
                 ({'attachments': {}}, 'invalid_input')]
        base = {key: value for key, value in original.items() if key not in ('metadata_patch', 'task_patches', 'documents')}
        before = self.tables()
        for change, code in cases:
            with self.subTest(change=change):
                self.error(self.native.execute({**base, **change}), code)
                self.assertEqual(before, self.tables())

    def test_whole_record_document_blob_and_state_limits(self):
        request = self.prepare()
        before = self.tables()
        for change in ({'documents': {'big': '文' * (MAX_FILE // 3 + 1)}},
                       {'documents': {f'new/{i}': '' for i in range(127)}},
                       {'metadata_patch': {'large': 'a' * MAX_FILE}}):
            with self.subTest(change=next(iter(change))):
                self.error(self.native.execute({**request, **change}), 'limit_exceeded')
                self.assertEqual(before, self.tables())

    def test_replay_conflict_and_both_optimistic_inputs(self):
        request = self.prepare()
        before = self.tables()
        for key, code in (('expected_revision', 'revision_conflict'), ('expected_source_head', 'source_conflict')):
            self.error(self.native.execute({**request, key: 'stale'}), code)
            self.assertEqual(before, self.tables())
        self.ok(self.native.execute(request))
        committed = self.tables()
        self.error(self.native.execute({**request, 'documents': {'changed': 'payload'}}), 'operation_id_conflict')
        self.error(self.native.execute({**request, 'operation_id': 'new-stale'}), 'revision_conflict')
        self.assertEqual(committed, self.tables())

    def test_snapshot_capacity_failure_rolls_back_every_native_and_source_table(self):
        request = self.prepare()
        before = self.tables()
        with patch.object(source_backup, 'MAX_DATA_BYTES', 1):
            self.error(self.native.execute(request), 'limit_exceeded')
        self.assertEqual(before, self.tables())
        with patch.object(sqlite_store, 'source_head', side_effect=[request['expected_source_head'], 'changed-before-commit']):
            self.error(self.native.execute(request), 'source_conflict')
        self.assertEqual(before, self.tables())
        self.ok(self.native.execute(request))

    def test_lost_response_replays_original_receipt_without_new_delivery(self):
        request = self.prepare()
        original = source_store.SQLiteStore.transaction
        @contextmanager
        def lost(store, *args, **kwargs):
            with original(store, *args, **kwargs) as transaction:
                yield transaction
            if kwargs.get('write'):
                raise RecordError('storage_error', 'Synthetic response loss after commit')
        with patch.object(source_store.SQLiteStore, 'transaction', lost):
            response = self.native.execute(request)
        self.error(response, 'storage_error')
        self.assertEqual(response['mutation_state'], 'unknown')
        committed = self.tables()
        receipt = self.ok(self.run_native('operation', operation_id=request['operation_id']))
        self.assertEqual(self.ok(self.native.execute(request)), {**receipt, 'replayed': True})
        self.assertEqual(committed, self.tables())

    def test_v2_backup_restore_preserves_revision_snapshot_intents_and_safe_replay(self):
        request = self.prepare()
        receipt = self.ok(self.native.execute(request))
        before = self.tables()
        archive = self.directory / 'revision-backup.json'
        exported = self.ok(self.native.execute({'contract_version': VERSION, 'operation': 'export',
                           'store_ref': fixture.STORE_REF, 'destination': str(archive)}))
        config = copy.deepcopy(self.config)
        target = self.directory / 'restored.sqlite'
        config['stores']['local']['database'] = str(target)
        restored = WorkflowRecords(self.project, config)
        self.ok(restored.execute({'contract_version': VERSION, 'operation': 'restore', 'store_ref': fixture.STORE_REF,
                                 'operation_id': 'restore', 'archive': str(archive), 'archive_digest': exported['archive_digest']}))
        self.assertEqual(self.ok(restored.execute(request)), {**receipt, 'replayed': True})
        with closing(sqlite3.connect(target)) as connection:
            for name in (*source_store.TABLES, 'revisions', 'blobs', 'workflows'):
                self.assertEqual(connection.execute('SELECT * FROM ' + name + ' ORDER BY 1,2').fetchall(), before[name])

    def test_v1_recovery_keeps_strict_old_mutation_rules_and_accepts_revision(self):
        config = copy.deepcopy(self.config)
        config['stores']['local']['database'] = str(self.directory / 'v1.sqlite')
        native = WorkflowRecords(self.project, config)
        def call(operation, **values):
            return native.execute({'contract_version': VERSION, 'operation': operation,
                                   'store_ref' if operation == 'init' else 'workflow_ref': fixture.STORE_REF if operation == 'init' else fixture.REF, **values})
        self.ok(call('init', operation_id='init'))
        self.ok(call('create', operation_id='create', record=fixture.record()))
        current = self.ok(call('context'))
        self.ok(call('revise-workflow', operation_id='revise', metadata_patch={'phase': 'done'},
                     expected_revision=current['revision'], expected_source_head=current['source_head']))
        store = native.provider(StoreRef.parse(fixture.STORE_REF))
        with store.transaction() as (connection, meta):
            backup.validate_payload(backup.payload(connection, meta))
        # A rehashed revision that mislabels this metadata edit as write-document
        # must still fail the original recovery transition rules.
        from workflow_records.contracts import RecordError, digest
        with store.transaction() as (connection, meta):
            value = backup.payload(connection, meta)
        import base64
        tables = value['tables']
        row = next(row for row in tables['revisions'] if row[2] is not None)
        state = decode_json(base64.b64decode(row[3])); state['event']['operation'] = 'write-document'
        raw = encoded(state); row[1] = digest(raw); row[3] = base64.b64encode(raw).decode()
        tables['workflows'][0][1] = row[1]
        operation_row = next(item for item in tables['operations'] if item[1] == 'revise')
        receipt = decode_json(base64.b64decode(operation_row[3]))
        receipt['revision'] = receipt['checkpoint_revision'] = row[1]
        operation_row[3] = base64.b64encode(encoded(receipt)).decode()
        event = decode_json(base64.b64decode(operation_row[4]))
        event['operation'] = 'write-document'
        operation_row[4] = base64.b64encode(encoded(event)).decode()
        with self.assertRaises(RecordError) as rejected:
            backup.validate_payload(value)
        self.assertEqual(rejected.exception.code, 'malformed_record')
        self.assertEqual(rejected.exception.message, 'Mutation changed fields outside its supported contract.')


if __name__ == '__main__':
    unittest.main()
