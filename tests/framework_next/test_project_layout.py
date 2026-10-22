"""Project namespace compatibility and explicit relocation; no runtime model calls."""
from copy import deepcopy
from hashlib import sha256
import json
import os
from pathlib import Path
import sys
import subprocess
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'src'))
from distribution import project_layout as layout, subagent_policy as p, subagent_registry as r
from distribution import installation_state as state, catalog, contracts
from distribution.data import json_bytes
from distribution.installation_plan import project_bindings
sys.path.insert(0, str(ROOT / 'tests'))
from framework_next.test_subagent_registry import fixture


def engine():
    return {'id': 'framework-managed-installation', 'version': '2.0.0', 'source_commit': '1' * 40,
            'files': [{'path': n, 'sha256': sha256((ROOT / n).read_bytes()).hexdigest()} for n in state.ENGINE_FILES]}


class LayoutTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.project = str(self.root)

    def seed(self, legacy=True):
        base = layout.LEGACY if legacy else layout.CANONICAL
        (self.root / base).mkdir(parents=True)
        proposed = p.plan(self.project, p.defaults())
        p.apply(self.project, proposed['plan'], proposed['plan_sha256'])
        registry, files = fixture()
        files = {n.replace(layout.CANONICAL, base): v for n, v in files.items()}
        name = base + '/sub-agents/team-reviewer/profile.toml'
        files[name] += '# Read .ai/custom/sub-agents/team-reviewer/references/method.md\n'
        registry['roles']['team-reviewer']['members']['profile.toml'] = p.digest(files[name].encode())
        registry['extensions']['team'] = {'opaque': True}
        proposed = r.plan(self.project, registry, files)
        r.apply(self.project, proposed['plan'], proposed['plan_sha256'])
        return registry

    def test_fresh_canonical_and_legacy_coherent_routes(self):
        self.assertEqual(p.inspect(self.project)['path'], p.POLICY_PATH)
        self.seed()
        self.assertEqual(p.inspect(self.project)['path'], layout.LEGACY + '/sub-agent-policy.json')
        self.assertEqual(r.inspect(self.project)['path'], layout.LEGACY + '/sub-agent-registry.json')
        self.assertTrue(all(n.startswith(layout.LEGACY) for n in
                            r.resolve(self.project, 'review', 'codex', 'inventory')['resources']))
        self.assertFalse((self.root / layout.CANONICAL).exists())

    def test_ambiguous_roots_and_changed_layout_reject_policy_plan(self):
        planned = p.plan(self.project, p.defaults())
        (self.root / layout.LEGACY).mkdir(parents=True)
        with self.assertRaisesRegex(ValueError, 'plan target'):
            p.apply(self.project, planned['plan'], planned['plan_sha256'])
        (self.root / layout.CANONICAL).mkdir()
        for operation in (p.inspect, r.inspect, layout.inspect):
            with self.assertRaisesRegex(ValueError, 'ambiguous'):
                operation(self.project)

    def test_migration_preserves_unknown_binary_empty_dirs_history_and_routes(self):
        before = self.seed()
        base = self.root / layout.LEGACY
        (base / 'unknown.bin').write_bytes(b'\x00\xff\xfe.ai/custom/\x00')
        (base / 'empty').mkdir()
        native = self.root / '.codex/agents/unregistered.toml'
        native.write_bytes(b'unknown .ai/custom/reference')
        policy_before = p.location(self.project).read_bytes()
        planned = layout.plan(self.project, engine())
        self.assertTrue((base / 'unknown.bin').exists())
        result = layout.apply(self.project, planned['plan'], planned['plan_sha256'], engine())
        self.assertEqual(result['outcome'], 'applied')
        self.assertEqual(layout.inventory(self.project, layout.CANONICAL), planned['plan']['after'])
        self.assertEqual((self.root / layout.CANONICAL / 'unknown.bin').read_bytes(), b'\x00\xff\xfe.ai/custom/\x00')
        self.assertTrue((self.root / layout.CANONICAL / 'empty').is_dir())
        self.assertEqual(native.read_bytes(), b'unknown .ai/custom/reference')
        after = r.inspect(self.project)['registry']
        for key in ('routes', 'extensions'):
            self.assertEqual(after[key], before[key])
        for key in ('origin', 'source_ref', 'baseline', 'integration'):
            self.assertEqual(after['roles']['team-reviewer'][key], before['roles']['team-reviewer'][key])
        self.assertEqual(p.location(self.project).read_bytes(), policy_before)
        self.assertIn('.ai/project/', (self.root / '.codex/agents/local-reviewer.toml').read_text())
        self.assertEqual(r.resolve(self.project, 'review', 'codex', 'inventory')['model'], 'gpt-6-luna')
        self.assertEqual(layout.apply(self.project, planned['plan'], planned['plan_sha256'], engine())['outcome'], 'unchanged')
        base.mkdir()
        (base / 'foreign').write_text('recreated')
        with self.assertRaisesRegex(ValueError, 'ambiguous'):
            layout.apply(self.project, planned['plan'], planned['plan_sha256'], engine())
        self.assertEqual((base / 'foreign').read_text(), 'recreated')

    def test_drift_and_linked_unknown_fail_before_rename(self):
        self.seed()
        planned = layout.plan(self.project, engine())
        unknown = self.root / layout.LEGACY / 'unknown'
        unknown.write_bytes(b'new')
        with self.assertRaisesRegex(ValueError, 'stale'):
            layout.apply(self.project, planned['plan'], planned['plan_sha256'], engine())
        self.assertFalse((self.root / layout.CANONICAL).exists())
        external = self.root / 'external'
        external.write_bytes(b'linked')
        unknown.unlink()
        os.link(external, unknown)
        with self.assertRaisesRegex(ValueError, 'file type'):
            layout.plan(self.project, engine())

    def test_native_drift_and_managed_collision_preserved(self):
        self.seed()
        target = self.root / '.codex/agents/local-reviewer.toml'
        original = target.read_bytes()
        target.write_bytes(b'foreign')
        with self.assertRaisesRegex(ValueError, 'native drift'):
            layout.plan(self.project, engine())
        target.write_bytes(original)
        with patch.object(r, 'lock', return_value=('a' * 64, {'.codex/agents/local-reviewer.toml': {}})):
            with self.assertRaisesRegex(ValueError, 'managed native'):
                layout.plan(self.project, engine())
        self.assertFalse((self.root / layout.CANONICAL).exists())

    def test_interruption_resumes_only_exact_accepted_plan(self):
        self.seed()
        planned = layout.plan(self.project, engine())
        with patch.object(layout, '_replace', side_effect=OSError('injected interruption')):
            result = layout.apply(self.project, planned['plan'], planned['plan_sha256'], engine())
        self.assertEqual(result['outcome'], 'interrupted')
        self.assertTrue((self.root / layout.CANONICAL).exists())
        forged = deepcopy(planned['plan'])
        forged['writes'][0]['content'] = 'unaccepted'
        forged['writes'][0]['after_sha256'] = p.digest(b'unaccepted')
        with self.assertRaisesRegex(ValueError, 'accepted migration'):
            layout.apply(self.project, forged, p.digest(p.encode(forged)), engine())
        result = layout.apply(self.project, planned['plan'], planned['plan_sha256'], engine())
        self.assertEqual(result['outcome'], 'applied')
        self.assertEqual(layout.inventory(self.project, layout.CANONICAL), planned['plan']['after'])

    def test_completed_lockless_replay_rejects_restored_preimage(self):
        self.seed()
        before = (self.root / '.codex/agents/local-reviewer.toml').read_bytes()
        planned = layout.plan(self.project, engine())
        layout.apply(self.project, planned['plan'], planned['plan_sha256'], engine())
        target = self.root / '.codex/agents/local-reviewer.toml'
        target.write_bytes(before)
        with self.assertRaisesRegex(ValueError, 'resource drift'):
            layout.apply(self.project, planned['plan'], planned['plan_sha256'], engine())
        self.assertEqual(target.read_bytes(), before)

    def test_legacy_writer_guards_and_shared_exclusion(self):
        self.seed()
        guard = self.root / layout.LEGACY / 'sub-agent-policy.json.writer'
        guard.write_bytes(b'owner')
        with self.assertRaisesRegex(ValueError, 'writer active'):
            layout.plan(self.project, engine())
        guard.unlink()
        planned = p.plan(self.project, p.defaults())
        registry, files = fixture()
        files = {n.replace(layout.CANONICAL, layout.LEGACY): v for n, v in files.items()}
        with layout.writer(self.project):
            with self.assertRaises(state.InstallationError):
                p.apply(self.project, planned['plan'], planned['plan_sha256'])
            with self.assertRaises(state.InstallationError):
                r.apply(self.project, {}, '0' * 64)
        self.assertTrue((self.root / layout.LEGACY).exists())

    def test_actual_old_lock_relocation_keeps_candidate_owned_assets_and_other_inputs(self):
        self.seed()
        original = state.read_lock(str(ROOT))
        self.assertIsNotNone(original)
        (self.root / state.LOCK_PATH).write_bytes(original.raw)
        for row in original.document['project_inputs']:
            if row['path'].startswith(layout.LEGACY + '/'):
                source = ROOT / row['path']
                self.assertEqual(p.digest(source.read_bytes()), row['sha256'])
                target = self.root / row['path']
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(source.read_bytes())
        planned = layout.plan(self.project, engine())
        result = layout.apply(self.project, planned['plan'], planned['plan_sha256'], engine())
        self.assertEqual(result['outcome'], 'applied')
        after = state.read_lock(self.project)
        for key in ('candidate_identity', 'selection', 'inventory', 'catalog_document', 'catalog_inventory',
                    'installation_id', 'mode_policy'):
            self.assertEqual(after.document[key], original.document[key])
        self.assertEqual(after.members, original.members)
        for old in original.document['project_inputs']:
            # Sorted order may change across relocation; select by translated path.
            new = next(row for row in after.document['project_inputs'] if row['path'] == layout.relocated(old['path']))
            self.assertEqual(old['sha256'], new['sha256'])
            if old['path'].startswith(layout.LEGACY + '/'):
                self.assertEqual(p.digest((self.root / new['path']).read_bytes()), new['sha256'])
        self.assertEqual(layout.apply(self.project, planned['plan'], planned['plan_sha256'], engine())['outcome'], 'unchanged')

    def test_moved_lock_input_drift_rejected_without_mutation(self):
        self.seed()
        original = deepcopy(state.read_lock(str(ROOT)).document)
        original['project_inputs'] = [{'path': layout.LEGACY + '/unavailable.json', 'sha256': '0' * 64}]
        (self.root / state.LOCK_PATH).write_bytes(json_bytes(original))
        with self.assertRaises((ValueError, OSError)):
            layout.plan(self.project, engine())
        self.assertFalse((self.root / layout.CANONICAL).exists())

    def test_old_metadata_paths_and_exact_historical_closures_remain_readable(self):
        self.assertEqual([len(x) for x in (state.LEGACY_ENGINE_FILES, state.POLICY_ENGINE_FILES,
                                          state.REGISTRY_ENGINE_FILES, state.ENGINE_FILES)], [23, 25, 26, 27])
        value = {'policy_version': 3, 'codex': {'selection': 'task'}, 'claude': {'selection': 'task'},
                 'escalation': 'explicit-user-authorized-visible-task', 'default_task': 'inventory',
                 'on_unavailable': 'stop', 'policy_path': p.POLICY_PATH}
        for name in (p.POLICY_PATH, layout.LEGACY + '/sub-agent-policy.json'):
            contracts.validate('SubAgentModelPolicyV3', {**value, 'policy_path': name})

    def test_saved_selection_and_config_protection_follow_resolved_layout(self):
        desired = state.read_lock(str(ROOT)).document['selection']['desired']
        for base in (layout.LEGACY, layout.CANONICAL):
            with self.subTest(layout=base), tempfile.TemporaryDirectory() as project:
                root = Path(project)
                (root / base).mkdir(parents=True)
                config = base + '/framework.json'
                selection = base + '/installation.json'
                (root / config).write_bytes(b'{}\n')
                (root / selection).write_bytes(json_bytes(desired))
                candidate = SimpleNamespace(selection={'desired': desired})
                protected = [{'path': selection, 'sha256': p.digest(json_bytes(desired))}]
                with self.assertRaises(state.InstallationError):
                    project_bindings(state._Reader(), root, candidate, protected, [], {})
                protected.append({'path': config, 'sha256': p.digest(b'{}\n')})
                rows = project_bindings(state._Reader(), root, candidate, protected, [], {})
                self.assertEqual({row['path'] for row in rows}, {selection, config})
                mismatch = deepcopy(desired)
                mismatch['skills'] = []
                (root / selection).write_bytes(json_bytes(mismatch))
                with self.assertRaises(state.InstallationError):
                    project_bindings(state._Reader(), root, candidate, protected, [], {})
                wrong = (layout.CANONICAL if base == layout.LEGACY else layout.LEGACY) + '/installation.json'
                with self.assertRaises(state.InstallationError):
                    project_bindings(state._Reader(), root, candidate, protected,
                                     [{'intent': {'path': wrong}, 'after': None}], {})

    def test_portable_pinned_layout_cli_plan_apply_and_replay(self):
        self.seed()
        host = self.root / 'engine'
        pin = engine()
        for name in state.ENGINE_FILES:
            target = host / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes((ROOT / name).read_bytes())
        (host / 'engine.json').write_bytes(p.encode({'engine_package_version': 1, 'engine': pin}))
        common = {'project_root': self.project, 'engine_root': str(host), 'engine': pin}
        def invoke(operation, **values):
            process = subprocess.run([sys.executable, '-I', '-B', str(host / 'src/tools/manage-sub-agents.py')],
                input=p.encode({**common, 'operation': operation, **values}), capture_output=True, check=False)
            self.assertEqual(process.returncode, 0, process.stdout.decode() + process.stderr.decode())
            return json.loads(process.stdout)
        planned = invoke('layout-plan')
        result = invoke('layout-apply', plan=planned['plan'], plan_sha256=planned['plan_sha256'])
        self.assertEqual(result['outcome'], 'applied')
        self.assertEqual(invoke('layout-inspect')['layout'], layout.CANONICAL)
        self.assertEqual(invoke('layout-apply', plan=planned['plan'], plan_sha256=planned['plan_sha256'])['outcome'], 'unchanged')


if __name__ == '__main__':
    unittest.main()
