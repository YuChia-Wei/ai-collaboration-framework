"""Real filesystem checks for the separately selected generation installation."""
import hashlib
import json
from pathlib import Path
import runpy
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
        (self.bundle / 'generation.json').write_text(json.dumps({
            'schema': 'aicf-generation/1', 'version': '1.0.0', 'source_commit': 'a' * 40,
            'files': [{'path': 'tool', 'size': len(data), 'sha256': hashlib.sha256(data).hexdigest(), 'mode': 0o755}]
        }), encoding='utf-8')

    def test_install_update_and_project_preservation(self):
        custom = self.project / 'README.md'
        custom.write_text('owned by project')
        API['install'](self.bundle, self.project)
        self.package(b'second')
        API['install'](self.bundle, self.project)
        self.assertEqual((self.target / 'tool').read_bytes(), b'second')
        self.assertEqual(custom.read_text(), 'owned by project')
        self.assertEqual(sorted(p.name for p in self.target.parent.iterdir()), ['dotnet-generation'])

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
