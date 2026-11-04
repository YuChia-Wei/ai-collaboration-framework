"""Real filesystem checks for the separately selected generation installation."""
import hashlib
import json
import os
from pathlib import Path
import runpy
import shutil
import subprocess
import sys
import tempfile
import unittest

API = runpy.run_path(str(Path(__file__).resolve().parents[2] / 'src/tools/install-generation.py'))


class GenerationInstallation(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.bundle = self.root / 'bundle'
        self.bundle.mkdir()
        self.project = self.root / 'project'
        self.project.mkdir()
        self.target = self.project / '.ai/tools/dotnet-generation'
        self.package(b'first')

    def package(self, data):
        (self.bundle / 'tool').write_bytes(data)
        shutil.copyfile(API['__file__'], self.bundle / 'install-generation.py')
        rows = []
        for name, mode in [('tool', 0o755), ('install-generation.py', 0o644)]:
            raw = (self.bundle / name).read_bytes()
            rows.append({'path': name, 'size': len(raw), 'sha256': hashlib.sha256(raw).hexdigest(), 'mode': mode})
        (self.bundle / 'generation.json').write_text(json.dumps({
            'schema': 'aicf-generation/1', 'version': '1.0.0', 'source_commit': 'a' * 40,
            'files': rows
        }), encoding='utf-8')

    def cli(self, *args):
        return subprocess.run([sys.executable, '-I', '-B', str(self.bundle / 'install-generation.py'), *args],
                              capture_output=True, text=True, encoding='utf-8')

    def assert_blocked(self, result, code):
        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stdout, '')
        self.assertEqual(len(result.stderr.splitlines()), 1)
        doc = json.loads(result.stderr)
        self.assertEqual(doc['outcome'], 'blocked')
        self.assertEqual(doc['code'], code)
        self.assertTrue(doc['reason'])
        return doc

    def test_cli_refusals_preserve_local_content_and_pending_state(self):
        result = self.cli('--project', str(self.project))
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stderr, '')
        self.assertEqual(json.loads(result.stdout)['outcome'], 'installed')
        (self.target / 'tool').write_bytes(b'custom')
        self.assert_blocked(self.cli('--project', str(self.project)), 'bundle-changed')
        self.assertEqual((self.target / 'tool').read_bytes(), b'custom')
        (self.target / 'tool').write_bytes(b'first')
        unknown = self.target / 'team.txt'
        unknown.write_text('team-owned')
        self.assert_blocked(self.cli('--project', str(self.project)), 'invalid-bundle')
        self.assertEqual(unknown.read_text(), 'team-owned')
        unknown.unlink()
        stage = self.target.parent / '.dotnet-generation-pending'
        stage.mkdir()
        blocked = self.assert_blocked(self.cli('--project', str(self.project)), 'pending-installation')
        self.assertIn('--recover', blocked['reason'])
        self.assertTrue(stage.exists())
        result = self.cli('--project', str(self.project), '--recover')
        self.assertEqual(result.returncode, 0)
        self.assertEqual(json.loads(result.stdout)['outcome'], 'removed-empty-stage')
        self.assertEqual((self.target / 'tool').read_bytes(), b'first')

    def test_cli_input_and_io_errors_are_structured(self):
        self.assert_blocked(self.cli(), 'invalid-arguments')
        self.assert_blocked(self.cli('--project', str(self.root / 'missing')), 'project-not-found')
        manifest = self.bundle / 'generation.json'
        manifest.write_text('{broken')
        self.assert_blocked(self.cli('--project', str(self.project)), 'invalid-data')
        manifest.unlink()
        self.assert_blocked(self.cli('--project', str(self.project)), 'filesystem-error')
        self.assertFalse(self.target.exists())

    def test_cli_missing_identity_does_not_replace_existing_installation(self):
        API['install'](self.bundle, self.project)
        installed_manifest = (self.target / 'generation.json').read_bytes()
        self.package(b'second')
        manifest = self.bundle / 'generation.json'
        valid = json.loads(manifest.read_text())
        for field in ('version', 'source_commit'):
            with self.subTest(field=field):
                malformed = {key: value for key, value in valid.items() if key != field}
                manifest.write_text(json.dumps(malformed))
                self.assert_blocked(self.cli('--project', str(self.project)), 'invalid-bundle')
                self.assertEqual((self.target / 'tool').read_bytes(), b'first')
                self.assertEqual((self.target / 'generation.json').read_bytes(), installed_manifest)
                self.assertFalse((self.target.parent / '.dotnet-generation-pending').exists())

    @unittest.skipIf(os.name == 'nt', 'POSIX symlink scenario; Windows reparse checks use the same refusal')
    def test_cli_linked_project_requires_explicit_physical_path(self):
        link = self.root / 'linked-project'
        link.symlink_to(self.project, target_is_directory=True)
        doc = self.assert_blocked(self.cli('--project', str(link)), 'linked-path')
        self.assertIn('physical path', doc['reason'])
        self.assertIn('realpath', doc['reason'])
        self.assertFalse(self.target.exists())
        result = self.cli('--project', str(link.resolve()))
        self.assertEqual(result.returncode, 0)
        self.assertEqual(json.loads(result.stdout)['outcome'], 'installed')

    def test_install_update_and_project_preservation(self):
        custom = self.project / 'README.md'
        custom.write_text('owned by project')
        API['install'](self.bundle, self.project)
        self.package(b'second')
        API['install'](self.bundle, self.project)
        self.assertEqual((self.target / 'tool').read_bytes(), b'second')
        self.assertEqual(custom.read_text(), 'owned by project')
        self.assertEqual(sorted(p.name for p in self.target.parent.iterdir()),
                         ['.dotnet-generation-install.lock', 'dotnet-generation'])

    @unittest.skipIf(os.name == 'nt', 'Requires case-sensitive POSIX filesystem')
    def test_case_alias_and_fifo_are_preserved(self):
        API['install'](self.bundle, self.project)
        alias = self.target / 'TOOL'
        alias.write_bytes(b'custom')
        with self.assertRaises(ValueError):
            API['install'](self.bundle, self.project)
        self.assertEqual(alias.read_bytes(), b'custom')
        alias.unlink()
        fifo = self.target / 'team-pipe'
        os.mkfifo(fifo)
        with self.assertRaises(ValueError):
            API['install'](self.bundle, self.project)
        self.assertTrue(fifo.exists())

    def test_process_death_releases_lock_and_restores_previous_installation(self):
        API['install'](self.bundle, self.project)
        self.package(b'second')
        script = '''import os, runpy, sys
from pathlib import Path
api = runpy.run_path(sys.argv[1])
rename = Path.rename
def crash(path, target):
    if path.name == 'payload':
        os._exit(23)
    return rename(path, target)
Path.rename = crash
api['install'](Path(sys.argv[2]), Path(sys.argv[3]))
'''
        result = subprocess.run([sys.executable, '-I', '-B', '-c', script,
                                 str(Path(API['__file__'])), str(self.bundle), str(self.project)])
        self.assertEqual(result.returncode, 23)
        self.assertFalse(self.target.exists())
        self.assertEqual(API['recover'](self.project)['outcome'], 'restored-previous-installation')
        self.assertEqual((self.target / 'tool').read_bytes(), b'first')
        API['install'](self.bundle, self.project)
        self.assertEqual((self.target / 'tool').read_bytes(), b'second')

    def test_changed_previous_installation_blocks_recovery(self):
        API['install'](self.bundle, self.project)
        stage = self.target.parent / '.dotnet-generation-pending'
        stage.mkdir()
        before = API['manifest_hash'](self.target)
        (stage / 'transaction.json').write_text(json.dumps({'before': before, 'after': 'unused', 'before_files': []}))
        self.target.rename(stage / 'previous')
        (stage / 'previous/tool').write_bytes(b'custom')
        with self.assertRaises(ValueError):
            API['recover'](self.project)
        self.assertEqual((stage / 'previous/tool').read_bytes(), b'custom')

    def test_recovery_finishes_interrupted_cleanup(self):
        API['install'](self.bundle, self.project)
        stage = self.target.parent / '.dotnet-generation-pending'
        stage.mkdir()
        after = API['manifest_hash'](self.target)
        old_manifest = self.target / 'generation.json'
        before_files = json.loads(old_manifest.read_text())['files'] + [
            {'path': 'generation.json', 'size': old_manifest.stat().st_size, 'sha256': after}]
        (stage / 'transaction.json').write_text(json.dumps(
            {'before': 'old', 'after': after, 'before_files': before_files}))
        shutil.copytree(self.target, stage / 'previous')
        (stage / 'previous/tool').unlink()
        custom = stage / 'previous/custom.txt'
        custom.write_text('custom')
        with self.assertRaises(ValueError):
            API['recover'](self.project)
        self.assertEqual(custom.read_text(), 'custom')
        custom.unlink()
        old_tool = stage / 'previous/tool'
        old_tool.write_bytes(b'changed')
        with self.assertRaises(ValueError):
            API['recover'](self.project)
        self.assertEqual(old_tool.read_bytes(), b'changed')
        old_tool.unlink()
        self.assertEqual(API['recover'](self.project)['outcome'], 'completed-installation')
        self.assertFalse(stage.exists())
        self.assertEqual((self.target / 'tool').read_bytes(), b'first')

    def test_modified_installation_is_not_overwritten(self):
        API['install'](self.bundle, self.project)
        (self.target / 'tool').write_bytes(b'custom')
        with self.assertRaises(ValueError):
            API['install'](self.bundle, self.project)
        self.assertEqual((self.target / 'tool').read_bytes(), b'custom')

    def test_unknown_file_and_directory_are_preserved(self):
        API['install'](self.bundle, self.project)
        for name, directory in [('team.txt', False), ('team', True)]:
            path = self.target / name
            path.mkdir() if directory else path.write_text('custom')
            with self.assertRaises(ValueError):
                API['install'](self.bundle, self.project)
            self.assertTrue(path.exists())
            path.rmdir() if directory else path.unlink()

    def test_corrupt_source_and_traversal_do_not_install(self):
        (self.bundle / 'tool').write_bytes(b'corrupt')
        with self.assertRaises(ValueError):
            API['install'](self.bundle, self.project)
        self.assertFalse(self.target.exists())
        self.package(b'first')
        manifest = self.bundle / 'generation.json'
        doc = json.loads(manifest.read_text())
        doc['files'][0]['path'] = '../tool'
        manifest.write_text(json.dumps(doc))
        with self.assertRaises(ValueError):
            API['install'](self.bundle, self.project)
        self.assertFalse(self.target.exists())
