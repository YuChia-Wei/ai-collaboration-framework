"""Issue 371 only: actual bootstrap/loader tests and one opt-in public attempt.

python -I -B tests/framework_next/test_engine_source.py --output-root EXPLICIT_F_ROOT
Add --public-entry only for the separately selected one-shot N1 attempt.
Synthetic bootstrap tests replace _direct only; they are not native evidence.
"""
from contextlib import contextmanager
from hashlib import sha256
import argparse
import importlib
import importlib.machinery
import importlib.util
import io
import json
import marshal
import os
from pathlib import Path
import struct
import sys
import unittest
from unittest.mock import patch

HERE = Path(__file__).absolute().parent
sys.dont_write_bytecode = True
sys.path.insert(0, str(HERE))
import support

ENTRY = support.REPOSITORY / 'src/tools/maintain_framework.py'
SPEC = importlib.util.spec_from_file_location('engine_source_bootstrap', ENTRY)
bootstrap = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(bootstrap)
LOCAL_FILES = tuple(p for p in bootstrap.ENGINE_FILES if p.startswith('src/distribution/'))
LOCAL_NAMES = {'distribution' if p.endswith('/__init__.py') else 'distribution.' + Path(p).stem
               for p in LOCAL_FILES}


@contextmanager
def isolated_modules():
    """Restore interpreter state around actual import machinery; no loader mock."""
    saved = {n: m for n, m in sys.modules.items() if n == 'distribution' or n.startswith('distribution.')}
    before_path, before_meta = list(sys.path), list(sys.meta_path)
    for name in saved:
        del sys.modules[name]
    try:
        yield
    finally:
        for name in list(sys.modules):
            if name == 'distribution' or name.startswith('distribution.'):
                del sys.modules[name]
        sys.modules.update(saved)
        sys.path[:] = before_path
        sys.meta_path[:] = before_meta


def fixture(name, *, actual=False, overrides=None):
    run = support.active_run()
    root = run.case(name)
    (root / 'src/distribution').mkdir(parents=True)
    (root / 'src/tools').mkdir()
    sources = {p: b"VALUE = 'source'\n" for p in LOCAL_FILES}
    sources['src/distribution/__init__.py'] += b'from . import data\n'
    sources['src/distribution/data.py'] += b'from . import installation_io\n'
    sources['src/distribution/installation.py'] += (
        b'import sys, json, yaml\n'
        b'from . import git_source, installation_state, installation_plan, maintenance_coordination, package\n'
        b'def execute(raw):\n'
        b"    return {'outcome': 'inspected', 'markers': {n: m.VALUE for n, m in sys.modules.items() "
        b"if n == 'distribution' or n.startswith('distribution.')}}\n")
    sources['src/tools/maintain_framework.py'] = ENTRY.read_bytes()
    if actual:
        sources = {p: (support.REPOSITORY / p).read_bytes() for p in bootstrap.ENGINE_FILES}
    sources.update(overrides or {})
    for name, raw in sources.items():
        target = root / name
        if actual:  # Source-derived copies, measured under the unchanged helper caps.
            with target.open('xb') as stream:
                stream.write(raw)
        else:
            run.write(target, raw)
    run.measure()
    pin = {'id': 'framework-managed-installation', 'version': '1.0.0',
           'source_commit': support.git('rev-parse', 'HEAD').decode().strip(),
           'files': [{'path': p, 'sha256': sha256(sources[p]).hexdigest()} for p in bootstrap.ENGINE_FILES]}
    return root, {'operation': 'inspect', 'engine_root': str(root), 'engine': pin}


def valid_cache(target, *, timestamp=False, fail_on_import=False):
    """A deliberately different CPython cache, proven acceptable by its real loader."""
    source = target.read_bytes()
    payload = "VALUE = 'cache'\n"
    if fail_on_import:
        payload += "raise RuntimeError('UNPINNED_CACHE_EXECUTED')\n"
    code = compile(payload, str(target), 'exec', dont_inherit=True)
    if timestamp:
        info = target.stat()
        header = struct.pack('<III', 0, int(info.st_mtime) & 0xffffffff, len(source) & 0xffffffff)
    else:
        header = struct.pack('<I', 1) + importlib.util.source_hash(source)
    cache = Path(importlib.util.cache_from_source(str(target)))
    cache.parent.mkdir(exist_ok=True)
    raw = importlib.util.MAGIC_NUMBER + header + marshal.dumps(code)
    support.active_run().write(cache, raw)
    admitted = importlib.machinery.SourceFileLoader('cache_control', str(target)).get_code('cache_control')
    namespace = {}
    try:
        exec(admitted, namespace)
    except RuntimeError as exc:
        support.check(fail_on_import and str(exc) == 'UNPINNED_CACHE_EXECUTED', 'unexpected cache control error')
    else:
        support.check(not fail_on_import, 'public cache control did not execute sentinel')
    support.check(namespace['VALUE'] == 'cache', 'control loader did not admit the deliberately different valid cache')
    support.check(target.read_bytes() == source, 'cache setup changed the source')
    return cache, raw


def invoke(root, request, *, direct=None):
    stdin, stdout, stderr = io.BytesIO(json.dumps(request).encode()), io.BytesIO(), io.StringIO()
    with patch.object(bootstrap, '__file__', str(root / 'src/tools/maintain_framework.py')), \
            patch.object(bootstrap, '_direct', side_effect=direct), \
            patch.object(sys, 'argv', [str(ENTRY)]), \
            patch.object(sys, 'stdin', type('Input', (), {'buffer': stdin})()), \
            patch.object(sys, 'stdout', type('Output', (), {'buffer': stdout})()), \
            patch.object(sys, 'stderr', stderr):
        code = bootstrap.main()
    return code, json.loads(stdout.getvalue()) if stdout.getvalue() else None, stderr.getvalue()


class EngineSourceTests(unittest.TestCase):
    def setUp(self):
        self.addCleanup(patch.stopall)
        self.scope = isolated_modules()
        self.scope.__enter__()
        self.addCleanup(self.scope.__exit__, None, None, None)

    def assert_sources(self, root, request):
        before_path, before_meta = list(sys.path), list(sys.meta_path)
        code, result, stderr = invoke(root, request)
        self.assertEqual((code, stderr), (0, ''))
        self.assertEqual(result['markers'], {n: 'source' for n in LOCAL_NAMES})
        self.assertEqual(sys.path, before_path)
        self.assertEqual(sys.meta_path, before_meta)
        for name in LOCAL_NAMES:
            module = sys.modules[name]
            expected = root / ('src/distribution/__init__.py' if name == 'distribution' else
                               'src/distribution/' + name.split('.')[1] + '.py')
            self.assertEqual(Path(module.__file__), expected)
            self.assertEqual(module.__spec__.origin, str(expected))
        self.assertEqual(sys.modules['distribution'].__path__, [str(root / 'src/distribution')])

    def test_all_local_modules_ignore_valid_unchecked_hash_caches(self):
        root, request = fixture('hash-caches')
        pin_before = json.dumps(request['engine'], sort_keys=True)
        caches = [valid_cache(root / name) for name in LOCAL_FILES]
        self.assert_sources(root, request)
        self.assertEqual(json.dumps(request['engine'], sort_keys=True), pin_before)
        for cache, raw in caches:
            self.assertEqual(cache.read_bytes(), raw)

    def test_transitive_module_ignores_valid_timestamp_cache(self):
        root, request = fixture('timestamp-cache')
        cache, raw = valid_cache(root / 'src/distribution/installation_io.py', timestamp=True)
        self.assert_sources(root, request)
        self.assertEqual(cache.read_bytes(), raw)

    def test_compiles_retained_verified_bytes_after_disk_change(self):
        root, request = fixture('retained-bytes')
        real_finder = bootstrap._VerifiedSourceFinder
        def after_verification(sources):
            (root / 'src/distribution/data.py').write_bytes(b"VALUE = 'changed-after-verification'\n")
            return real_finder(sources)
        with patch.object(bootstrap, '_VerifiedSourceFinder', side_effect=after_verification):
            self.assert_sources(root, request)

    def test_unlisted_transitive_module_is_refused_before_execution(self):
        root, request = fixture('unlisted-import', overrides={
            'src/distribution/__init__.py': b'from . import unlisted\n'})
        support.active_run().write(root / 'src/distribution/unlisted.py', b"raise RuntimeError('unlisted executed')\n")
        before_meta = list(sys.meta_path)
        code, result, stderr = invoke(root, request)
        self.assertEqual((code, stderr), (1, ''))
        self.assertEqual(result['diagnostics'][0]['code'], 'source-bootstrap')
        self.assertNotIn('distribution.unlisted', sys.modules)
        self.assertEqual(sys.meta_path, before_meta)

    def test_hash_type_closure_and_preloaded_refusals_are_preserved(self):
        root, request = fixture('admission-refusals')
        for defect in ('hash', 'type', 'closure', 'preloaded'):
            with self.subTest(defect=defect):
                bad = json.loads(json.dumps(request))
                if defect == 'hash':
                    bad['engine']['files'][0]['sha256'] = '0' * 64
                elif defect == 'type':
                    bad['engine']['files'][0]['sha256'] = 3
                elif defect == 'closure':
                    bad['engine']['files'][0]['path'] = 'src/distribution/unlisted.py'
                else:
                    sys.modules['distribution'] = object()
                with patch.object(bootstrap, '_VerifiedSourceFinder', side_effect=AssertionError('premature loader')):
                    code, result, stderr = invoke(root, bad)
                self.assertEqual((code, stderr), (1, ''))
                self.assertEqual(result['diagnostics'][0]['code'], 'source-bootstrap')
                sys.modules.pop('distribution', None)

    def test_path_refusal_stops_before_loader(self):
        root, request = fixture('path-refusal')
        with patch.object(bootstrap, '_VerifiedSourceFinder', side_effect=AssertionError('premature loader')):
            code, result, stderr = invoke(root, request, direct=OSError('synthetic path refusal'))
        self.assertEqual((code, stderr), (1, ''))
        self.assertFalse(result['changed'])
        self.assertEqual(result['diagnostics'][0]['code'], 'source-bootstrap')

    def test_host_modules_are_not_shadowed(self):
        root, request = fixture('host-boundary')
        for name in ('src/json.py', 'src/yaml.py', 'src/distribution/json.py', 'src/distribution/yaml.py'):
            support.active_run().write(root / name, b"raise RuntimeError('host shadow executed')\n")
        import yaml
        self.assert_sources(root, request)
        self.assertIs(sys.modules['distribution.installation'].json, json)
        self.assertIs(sys.modules['distribution.installation'].yaml, yaml)

    def test_finder_remains_active_during_dispatch_and_is_removed_on_failure(self):
        root, request = fixture('lazy-import', overrides={'src/distribution/installation.py':
            b'def execute(raw):\n    from . import unlisted\n'})
        support.active_run().write(root / 'src/distribution/unlisted.py', b"raise RuntimeError('unlisted executed')\n")
        before_meta = list(sys.meta_path)
        code, result, stderr = invoke(root, request)
        self.assertEqual((code, result), (2, None))
        self.assertIn('interrupted', stderr)
        self.assertNotIn('distribution.unlisted', sys.modules)
        self.assertEqual(sys.meta_path, before_meta)

    def test_actual_product_sources_import_complete_allowed_closure(self):
        sources = {('distribution' if name.endswith('/__init__.py') else 'distribution.' + Path(name).stem):
                   (support.REPOSITORY / name, (support.REPOSITORY / name).read_bytes()) for name in LOCAL_FILES}
        finder = bootstrap._VerifiedSourceFinder(sources)
        sys.meta_path.insert(0, finder)
        installation = importlib.import_module('distribution.installation')
        loaded = {n for n in sys.modules if n == 'distribution' or n.startswith('distribution.')}
        self.assertEqual(loaded, LOCAL_NAMES)
        self.assertTrue(callable(installation.execute))
        for name, (path, _) in sources.items():
            self.assertIs(sys.modules[name].__loader__, finder)
            self.assertEqual(Path(sys.modules[name].__file__), path)


def public_entry_attempt():
    """One unpatched CLI, no project/installed root or operation dispatch requested."""
    root, request = fixture('public-entry', actual=True)
    # An isolated tiny source checkout; no project or installed root exists here.
    support.git('-c', 'init.templateDir=', 'init', '--quiet', cwd=root)
    support.git('-c', 'core.autocrlf=false', 'add', '--', 'src', cwd=root)
    support.git('-c', 'user.name=Engine Source Fixture', '-c', 'user.email=fixture@example.invalid',
                '-c', 'commit.gpgsign=false', '-c', 'core.hooksPath=' + str(root / '.git/no-hooks'),
                'commit', '--quiet', '-m', 'fixture: exact source pin', cwd=root)
    request['engine']['source_commit'] = support.git('rev-parse', 'HEAD', cwd=root).decode().strip()
    support.active_run().measure()
    source_before = {name: (root / name).read_bytes() for name in bootstrap.ENGINE_FILES}
    pin_before = json.dumps(request['engine'], sort_keys=True)
    cache, cache_raw = valid_cache(root / 'src/distribution/installation_io.py', fail_on_import=True)
    raw = json.dumps(request).encode()
    child = support.run_process([support.PYTHON, '-I', '-B', root / 'src/tools/maintain_framework.py'],
                                cwd=root, input=raw, timeout=30)
    support.check({name: (root / name).read_bytes() for name in bootstrap.ENGINE_FILES} == source_before,
                  'public source bytes changed')
    support.check(json.dumps(request['engine'], sort_keys=True) == pin_before, 'public pin changed')
    support.check(cache.read_bytes() == cache_raw, 'public cache changed')
    for name, value in [('request.json', raw), ('stdout.json', child.stdout), ('stderr.txt', child.stderr)]:
        support.active_run().write(root / name, value)
    response = json.loads(child.stdout)
    refused = (child.returncode == 1 and response.get('outcome') == 'unsupported'
               and response.get('changed') is False
               and any(d.get('code') == 'source-bootstrap' for d in response.get('diagnostics', [])))
    print(json.dumps({'public_entry': {'exit_code': child.returncode, 'response': response,
          'source_and_pin_unchanged': True, 'cache_control_admitted': True, 'cache_unchanged': True,
          'status': 'blocked-before-dispatch' if refused else 'requires-owner-review',
          'native_acceptance': 'not-established', 'retry': 'none'}}, sort_keys=True))
    return False  # A tiny incomplete request/refusal is never native installation acceptance.


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-root', required=True, type=Path)
    parser.add_argument('--public-entry', action='store_true')
    args = parser.parse_args()
    run, success = None, False
    try:
        print(json.dumps({'python': sys.version.split()[0], 'isolated': sys.flags.isolated,
                          'dont_write_bytecode': sys.flags.dont_write_bytecode}), flush=True)
        support.check(sys.flags.isolated and sys.flags.dont_write_bytecode, 'use isolated Python -I -B')
        run = support.FixtureRun(args.output_root)
        with support.use_run(run):
            if args.public_entry:
                success = public_entry_attempt()
                return 0 if success else 2
            result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(EngineSourceTests))
            success = result.wasSuccessful() and not result.skipped
            return 0 if success else 1
    finally:
        if run is not None:
            print(json.dumps({'fixture_accounting': run.close(success)}, sort_keys=True), flush=True)


if __name__ == '__main__':
    raise SystemExit(main())
