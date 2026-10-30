"""Selected-layout diagnostics and refusal boundaries; no native acceptance claim."""
from contextlib import nullcontext, redirect_stdout
import importlib.util
import io
import json
from pathlib import Path, PureWindowsPath
import sys
from types import SimpleNamespace
import unittest
from unittest.mock import patch

ROOT = Path(__file__).absolute().parents[2]
sys.dont_write_bytecode = True
sys.path.insert(0, str(ROOT / 'src'))
from distribution import catalog, installation_plan as planning, installation_state as state
from distribution.installation_io import budget


def windows_root(units, unicode=False):
    # C:\ = 3 units; the optional non-BMP character occupies two, not one.
    prefix = '\U0001f331' if unicode else ''
    return PureWindowsPath('C:/' + prefix + 'a' * (units - 3 - (2 if unicode else 0)))


class PathBudgetTests(unittest.TestCase):
    def test_actual_ascii_and_non_bmp_239_240_241(self):
        for unicode in (False, True):
            for length in (239, 240, 241):
                with self.subTest(unicode=unicode, length=length):
                    root = windows_root(length - 9, unicode)  # separator + leaf.txt
                    if length <= 240:
                        budget([('project', root, 'leaf.txt')], stage='apply')
                    else:
                        with self.assertRaises(state.InstallationError) as caught:
                            budget([('project', root, 'leaf.txt')], stage='apply')
                        error = caught.exception
                        self.assertEqual(error.outcome, 'unsupported')
                        self.assertEqual(error.diagnostic['code'], 'path-budget')
                        self.assertEqual(error.diagnostic['path'], 'leaf.txt')
                        self.assertIn('apply stage, project root', error.diagnostic['reason'])
                        self.assertIn('root uses 232 UTF-16', error.diagnostic['reason'])
                        self.assertIn('241 full-path', error.diagnostic['reason'])
                        self.assertIn('240 / 255', error.diagnostic['reason'])
                        self.assertIn('shorter explicit project root', error.diagnostic['next_action'])
                        self.assertIn('new plan', error.diagnostic['next_action'])
                        self.assertNotIn(str(root), json.dumps(error.diagnostic, ensure_ascii=False))

    def test_plan_budgets_each_root_and_intermediate_layout(self):
        destination = '.ai/core/sample/member.md'
        metadata = 'metadata/catalog-files.json'
        engine_file = 'src/distribution/installation_state.py'
        operation = 'i-' + '0' * 32
        candidate = SimpleNamespace(members={destination: {'path': 'payload/' + destination}},
                                    metadata_bytes={metadata: b'{}'})
        tails = {'project': '.ai/core/sample/' + '.fi-' + '0' * 12,
                 'candidate': 'payload/' + destination, 'engine': engine_file,
                 'scratch': operation + '/' + metadata,
                 'staging': operation + '/' + destination,
                 'recovery': operation + '/objects/' + '0' * 64}
        for role, tail in tails.items():
            for length in (240, 241):
                with self.subTest(role=role, length=length):
                    roots = {key: PureWindowsPath('C:/' + key) for key in tails}
                    roots[role] = windows_root(length - len(tail) - 1, unicode=True)
                    args = (roots, candidate, None, [{'action': 'add', 'destination': destination}],
                            [{'path': 'README.md'}], {'files': [{'path': engine_file}]})
                    if length == 240:
                        result = planning._path_budget(*args)
                        self.assertEqual(result['maximum_full_path_utf16'], 240)
                    else:
                        with self.assertRaises(state.InstallationError) as caught:
                            planning._path_budget(*args)
                        self.assertIn('plan stage, ' + role + ' root', caught.exception.diagnostic['reason'])
                        self.assertIn('241 full-path', caught.exception.diagnostic['reason'])
                        self.assertNotIn(str(roots[role]), json.dumps(caught.exception.diagnostic, ensure_ascii=False))

    def test_catalog_and_subset_refuse_before_directory_allocation_with_stable_roles(self):
        for kind in ('catalog', 'subset'):
            for role in ('output', 'scratch'):
                with self.subTest(kind=kind, role=role):
                    label_length = len(kind if role == 'output' else 'scratch') + 1 + 32
                    roots = {'output': PureWindowsPath('C:/output'), 'scratch': PureWindowsPath('C:/scratch')}
                    roots[role] = windows_root(241 - 1 - label_length - 1 - len('metadata/build.json'))
                    with patch.object(state, '_root', side_effect=PureWindowsPath), \
                         patch.object(state, '_roots_disjoint'), \
                         patch('distribution.assembly.OwnedDirectory') as allocate:
                        with self.assertRaises(state.InstallationError) as caught:
                            catalog.emit_artifact({'metadata/build.json': b'{}'}, {},
                                                  roots['output'], roots['scratch'], kind, 'selected')
                        allocate.assert_not_called()
                    self.assertIn(kind + ' stage, ' + role + ' root', caught.exception.diagnostic['reason'])
                    self.assertIn('241 full-path', caught.exception.diagnostic['reason'])
                    self.assertNotIn(str(roots[role]), json.dumps(caught.exception.diagnostic, ensure_ascii=False))

    def test_relative_limits_and_impossible_layout_do_not_suggest_root_shortening(self):
        with self.assertRaises(state.InstallationError) as caught:
            budget([('project', PureWindowsPath('C:/private'), 'a' * 240)], stage='plan')
        self.assertIn('root alone cannot fit', caught.exception.diagnostic['next_action'])
        for name in ('a' * 241, '/'.join(['a'] * 49)):
            with self.subTest(name_length=len(name)), self.assertRaises(state.InstallationError) as caught:
                budget([('project', PureWindowsPath('C:/private'), name)], stage='apply')
            self.assertEqual(caught.exception.diagnostic['code'], 'path-limit')
            self.assertIsNone(caught.exception.diagnostic['path'])
            self.assertIn('Shortening a root cannot resolve', caught.exception.diagnostic['next_action'])
        with self.assertRaises(state.InstallationError) as caught:
            budget([('project', PureWindowsPath('C:/private'), '../escape')], stage='apply')
        self.assertEqual(caught.exception.diagnostic['code'], 'invalid-path')

    def test_recovery_refusal_preserves_original_identity_guidance(self):
        with self.assertRaises(state.InstallationError) as caught:
            budget([('recovery', windows_root(232), 'leaf.txt')], stage='recover')
        diagnostic = caught.exception.diagnostic
        self.assertIn('recover stage, recovery root', diagnostic['reason'])
        self.assertIn('original operation record', diagnostic['next_action'])
        self.assertIn('Do not move or rename', diagnostic['next_action'])
        self.assertNotIn('shorter explicit', diagnostic['next_action'])

    def test_public_generation_clis_keep_shape_and_safe_path_diagnostics(self):
        for relative, call_name, arguments in (
                ('tools/build-catalog.py', 'build_catalog', ['--repository', str(ROOT), '--commit', '1' * 40,
                 '--release-version', '0.0.0', '--engine-pin', 'pin', '--output-root', 'out', '--scratch-root', 'tmp']),
                ('src/tools/derive-subset.py', 'read_catalog', ['--catalog-root', 'catalog', '--catalog-identity', 'selected',
                 '--preset', 'selected', '--preset-version', '0.1.0', '--engine-pin', 'pin', '--output-root', 'out', '--scratch-root', 'tmp'])):
            spec = importlib.util.spec_from_file_location('path_budget_cli', ROOT / relative)
            cli = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(cli)
            for error in (state.InstallationError('path-budget', 'subset stage, output root: 241 full-path; limits 240 / 255.',
                                                 'payload/member.md', 'unsupported', 'Select a shorter explicit output root.'),
                          OSError('permission denied at C:/private-host/unselected')):
                with self.subTest(cli=relative, error=type(error).__name__), \
                     patch.object(sys, 'argv', [relative, *arguments]), \
                     patch.object(cli, 'verified_host', return_value=nullcontext()), \
                     patch.object(catalog, call_name, side_effect=error), redirect_stdout(io.StringIO()) as output:
                    self.assertEqual(cli.main(), 1)
                result = json.loads(output.getvalue())
                self.assertEqual(set(result), {'outcome', 'code', 'reason'})
                self.assertNotIn('private-host', result['reason'])
                if isinstance(error, state.InstallationError):
                    self.assertEqual(result['code'], 'path-budget')
                    self.assertEqual(result['outcome'], 'unsupported')
                    self.assertIn('241 full-path', result['reason'])
                    self.assertIn('payload/member.md', result['reason'])
                    self.assertIn('shorter explicit output root', result['reason'])
                else:
                    self.assertNotEqual(result['code'], 'path-budget')


if __name__ == '__main__':
    unittest.main()
