"""Installed core closure without Board execution modules or jsonschema; no network."""
import base64
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

import yaml

from tools import test_workflow_sqlite as fixture
from tools.test_workflow_records import ROOT, CHECKPOINT, git
from workflow_records.contracts import VERSION, encoded


def copy_core(destination):
    """Copy exact manifest members; never reuse a source-checkout import path."""
    manifest = yaml.safe_load((ROOT / 'src/distribution/manifest.yaml').read_text(encoding='utf-8'))
    row = next(r for r in manifest['components'] if r['id'] == 'workflow-records')
    for member in row['members']:
        target = destination / member['source']
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / row['source'] / member['source'], target)
    return row


class OfflinePackageTests(unittest.TestCase):
    setUpClass = classmethod(fixture.SQLiteRecordTests.setUpClass.__func__)
    tearDownClass = classmethod(fixture.SQLiteRecordTests.tearDownClass.__func__)

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='workflow-offline-')
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name)
        self.project = self.directory / 'project'
        shutil.copytree(self.base, self.project)
        self.package = self.directory / 'installed/.ai/core/skills/workflow-records'
        copy_core(self.package)
        self.config = {'contract_version': VERSION, 'default_provider': 'local', 'stores': {'local': {
            'kind': 'local', 'store_id': 'local-records', 'repository_id': 'fixture-repository',
            'database': str(self.directory / 'records.sqlite')}}}
        # -I retains system PyYAML, but this process must not import any Board or
        # optional validator module even when installed in the ambient environment.
        self.runner = self.directory / 'run-isolated.py'
        self.runner.write_text('''import importlib.abc, runpy, socket, sys
class BlockOptional(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname.split('.')[0] in ('jsonschema', 'referencing') or 'board_command' in fullname or 'board_query' in fullname:
            raise ImportError('optional runtime deliberately unavailable')
sys.meta_path.insert(0, BlockOptional())
def no_network(*args, **kwargs):
    raise AssertionError('network forbidden')
socket.socket = no_network
sys.argv = sys.argv[1:]
runpy.run_path(sys.argv[0], run_name='__main__')
''', encoding='utf-8')

    def launch(self, request, source=False, config=None):
        config_path = self.directory / 'config.json'
        request_path = self.directory / 'request.json'
        config_path.write_bytes(encoded(config or self.config))
        request_path.write_bytes(encoded(request))
        cli = self.package / 'tools' / ('source-store.py' if source else 'workflow-records.py')
        process = subprocess.run([sys.executable, '-I', '-B', str(self.runner), str(cli), '--root', str(self.project),
                                  '--config', str(config_path), '--request', str(request_path)],
                                 cwd=self.directory, capture_output=True, timeout=20)
        self.assertEqual(process.stderr, b'')
        result = json.loads(process.stdout)
        self.assertEqual(process.returncode, 0 if result['status'] == 'ok' else 1, result)
        return result

    def native(self, operation, store=False, **values):
        return self.launch({'contract_version': VERSION, 'operation': operation,
                            'store_ref' if store else 'workflow_ref': fixture.STORE_REF if store else fixture.REF, **values})

    def source(self, operation, **values):
        profile = 'workflow-records/source-store/2' if operation == 'source-init' else 'workflow-records/source-store/1'
        return self.launch({'contract_version': profile, 'operation': operation,
                            'store_ref': fixture.STORE_REF, **values}, source=True)

    def ok(self, response):
        self.assertEqual(response['status'], 'ok', response)
        return response['result']

    def test_core_only_real_cli_local_lifecycle_snapshot_and_inactive_restore_without_optional_runtime(self):
        self.assertFalse(list(self.package.rglob('*board*')))
        # A local-only read/write/backup does not need even the inert replica schema.
        (self.package / 'schemas/source-replica-v1.schema.json').unlink()
        self.ok(self.source('source-init', operation_id='init-offline', schema_version='workflow-sqlite/3'))
        self.ok(self.native('create', operation_id='create-offline', record=fixture.record()))
        current = self.ok(self.native('context'))
        self.ok(self.native('checkpoint', operation_id='checkpoint-offline', checkpoint=CHECKPOINT,
                            expected_revision=current['revision'], expected_source_head=current['source_head']))
        resumed = self.ok(self.native('resume'))
        self.assertEqual(resumed['plan']['content'], '# 原始計畫\n')
        latest = self.ok(self.source('source-list'))
        snapshot_id = latest['items'][0]['snapshot_id']
        manifest = self.ok(self.source('source-read', snapshot_id=snapshot_id))['manifest']
        entry = next(f for f in manifest['files'] if f['path'] == '_native/state.json')
        chunk = self.ok(self.source('source-chunk', snapshot_id=snapshot_id, path=entry['path'], index=0))
        self.assertTrue(base64.b64decode(chunk['content_base64']))
        archive = self.directory / 'backup.json'
        exported = self.ok(self.native('export', store=True, destination=str(archive)))
        self.ok(self.native('preflight', store=True, archive=str(archive), archive_digest=exported['archive_digest']))
        restored = json.loads(json.dumps(self.config))
        restored['stores']['local']['database'] = str(self.directory / 'restored.sqlite')
        result = self.ok(self.launch({'contract_version': VERSION, 'operation': 'restore', 'store_ref': fixture.STORE_REF,
                                    'operation_id': 'restore-offline', 'archive': str(archive),
                                    'archive_digest': exported['archive_digest']}, config=restored))
        self.assertEqual(result['store_state'], 'inactive')
        readback = self.ok(self.launch({'contract_version': VERSION, 'operation': 'resume', 'workflow_ref': fixture.REF}, config=restored))
        self.assertEqual(readback['revision'], resumed['revision'])
        self.assertEqual(git(self.project, 'status', '--porcelain'), '')

    def test_core_refuses_board_operation_without_implicit_package_lookup(self):
        result = self.launch({'contract_version': 'workflow-records/board-query/1', 'operation': 'board-query-prepare'}, source=True)
        self.assertEqual(result['error']['code'], 'provider_unavailable')
        self.assertFalse(Path(self.config['stores']['local']['database']).exists())

    def test_experimental_installation_does_not_activate_or_read_request(self):
        target = self.directory / 'installed/.ai/core/skills/workflow-board-experimental'
        shutil.copytree(ROOT / 'src/skills/workflow-board-experimental', target)
        for name in ('board-query.py', 'board-command.py'):
            process = subprocess.run([sys.executable, '-I', '-S', '-B', str(target / 'tools' / name),
                                      '--request', str(self.directory / 'does-not-exist.json')],
                                     cwd=self.directory, capture_output=True, timeout=10)
            self.assertEqual((process.returncode, process.stderr), (1, b''))
            self.assertEqual(json.loads(process.stdout)['error']['code'], 'experimental_not_activated')


if __name__ == '__main__':
    unittest.main()
