"""Project resource/routing behavior, not native model or discovery acceptance."""
from copy import deepcopy
from pathlib import Path
import os
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'src'))
from distribution import subagent_registry as r, subagent_policy as p


def fixture(runtime_id='local-reviewer', base=True):
    profile = 'name = "' + runtime_id + '"\ndescription = "Review bounded evidence"\nsandbox_mode = "read-only"\n'
    files = {'profile.toml': profile, 'references/method.md': 'Preserve unknown evidence.\n'}
    registry = r.empty()
    registry['roles']['team-reviewer'] = {
        'origin': 'project-derived', 'source_ref': 'fixture:original',
        'intent': 'Preserve the team review contract.', 'acceptance': ['Unknown evidence stays unknown.'],
        'capabilities': ['review'], 'members': {n: p.digest(v.encode()) for n, v in files.items()},
        'baseline': {'ref': 'fixture:original', 'files': dict(files)} if base else None,
        'projections': {'codex': {'source': 'profile.toml', 'runtime_id': runtime_id}},
        'integration': {'candidate_ref': None, 'coverage': 'not-assessed', 'status': 'pending',
                        'evidence_ref': None, 'decision_ref': None}}
    registry['routes']['review'] = {'codex': {'kind': 'project', 'id': 'team-reviewer',
                                            'decision_ref': 'owner-task', 'expected_sha256': None}}
    return registry, {r.PACKAGES + 'team-reviewer/' + n: v for n, v in files.items()}


def apply(root, registry, files, **kwargs):
    plan = r.plan(str(root), registry, files, **kwargs)
    return r.apply(str(root), plan['plan'], plan['plan_sha256'])


class RegistryTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        plan = p.plan(str(self.root), p.defaults())
        p.apply(str(self.root), plan['plan'], plan['plan_sha256'])

    def test_explicit_adoption_required_even_for_identical_unowned_entry(self):
        registry, files = fixture()
        target = self.root / r.runtime('codex', 'local-reviewer')
        target.parent.mkdir(parents=True)
        raw = files[r.PACKAGES + 'team-reviewer/profile.toml'].encode()
        target.write_bytes(raw)
        unknown = target.with_name('unknown.toml')
        unknown.write_bytes(b'leave me alone')
        with self.assertRaisesRegex(ValueError, 'explicit adoption'):
            r.plan(str(self.root), registry, files)
        self.assertFalse((self.root / r.REGISTRY).exists())
        result = apply(self.root, registry, files, adopt={r.runtime('codex', 'local-reviewer'): p.digest(raw)})
        self.assertTrue(result['changed'])
        view = r.inspect(str(self.root))
        self.assertEqual(view['roles']['team-reviewer']['local_delta'], 'none')
        self.assertEqual(view['unknown_entries'], ['.codex/agents/unknown.toml'])
        self.assertEqual(unknown.read_bytes(), b'leave me alone')
        self.assertFalse((self.root / '.ai/framework.lock').exists())

    def test_source_free_route_verifies_all_resources_and_model_profile(self):
        registry, files = fixture()
        apply(self.root, registry, files)
        result = r.resolve(str(self.root), 'review', 'codex', 'independent-review')
        self.assertEqual(result['model'], 'gpt-6.1-sol')
        self.assertEqual(result['runtime_id'], 'local-reviewer')
        self.assertFalse(result['invocation_observed'])
        self.assertEqual(result['runtime_activation'], 'unknown')
        (self.root / r.PACKAGES / 'team-reviewer/references/method.md').write_text('changed')
        with self.assertRaisesRegex(ValueError, 'resource drift'):
            r.resolve(str(self.root), 'review', 'codex', 'inventory')

    def test_rebind_preserves_authoring_and_requires_exact_explicit_detachment(self):
        registry, files = fixture()
        apply(self.root, registry, files)
        newer, changed = fixture('team-reviewer-v2')
        old_entry = r.runtime('codex', 'local-reviewer')
        with self.assertRaisesRegex(ValueError, 'explicit detach'):
            r.plan(str(self.root), newer, changed)
        planned = r.plan(str(self.root), newer, changed, detach=[old_entry])
        self.assertTrue((self.root / old_entry).exists())
        result = r.apply(str(self.root), planned['plan'], planned['plan_sha256'])
        self.assertEqual(result['outcome'], 'applied')
        self.assertFalse((self.root / old_entry).exists())
        self.assertTrue((self.root / r.PACKAGES / 'team-reviewer/references/method.md').exists())
        self.assertEqual(r.resolve(str(self.root), 'review', 'codex', 'inventory')['runtime_id'], 'team-reviewer-v2')
        self.assertEqual(r.apply(str(self.root), planned['plan'], planned['plan_sha256'])['outcome'], 'unchanged')

    def test_foreign_destination_drift_and_stale_plan_block_before_changes(self):
        registry, files = fixture()
        prepared = r.plan(str(self.root), registry, files)
        entry = self.root / r.runtime('codex', 'local-reviewer')
        entry.parent.mkdir(parents=True)
        entry.write_text('foreign')
        with self.assertRaisesRegex(ValueError, 'stale'):
            r.apply(str(self.root), prepared['plan'], prepared['plan_sha256'])
        self.assertFalse((self.root / r.PACKAGES).exists())
        self.assertEqual(entry.read_text(), 'foreign')

    def test_managed_ownership_cannot_be_overridden_by_registry_adoption(self):
        registry, files = fixture()
        entry = r.runtime('codex', 'local-reviewer')
        with patch.object(r, 'lock', return_value=('a' * 64, {entry: {}})):
            with self.assertRaisesRegex(ValueError, 'framework-owned'):
                r.plan(str(self.root), registry, files, adopt={entry: 'b' * 64})
        prepared = r.plan(str(self.root), registry, files)
        with patch.object(r, 'lock', return_value=('a' * 64, {entry: {}})):
            with self.assertRaisesRegex(ValueError, 'lock changed'):
                r.apply(str(self.root), prepared['plan'], prepared['plan_sha256'])

    def test_interrupted_projection_reports_partial_state_and_exact_plan_resumes(self):
        registry, files = fixture()
        prepared = r.plan(str(self.root), registry, files)
        replace = os.replace
        def interrupt(source, target):
            if Path(target).suffix == '.toml' and '.codex' in Path(target).parts:
                raise OSError('injected projection interruption')
            return replace(source, target)
        with patch.object(r.os, 'replace', side_effect=interrupt):
            result = r.apply(str(self.root), prepared['plan'], prepared['plan_sha256'])
        self.assertEqual(result['outcome'], 'interrupted')
        self.assertTrue(result['changed'])
        self.assertFalse((self.root / r.REGISTRY).exists())
        with self.assertRaisesRegex(ValueError, 'route missing'):
            r.resolve(str(self.root), 'review', 'codex', 'inventory')
        result = r.apply(str(self.root), prepared['plan'], prepared['plan_sha256'])
        self.assertEqual(result['outcome'], 'applied')
        self.assertEqual(r.resolve(str(self.root), 'review', 'codex', 'inventory')['model'], 'gpt-6-luna')

    def test_coverage_adoption_and_activation_remain_separate(self):
        registry, files = fixture()
        role = registry['roles']['team-reviewer']
        role['integration'] = {'candidate_ref': 'framework:future-reviewer', 'coverage': 'covered',
                               'status': 'proposed', 'evidence_ref': 'review-record', 'decision_ref': None}
        apply(self.root, registry, files)
        view = r.inspect(str(self.root))
        self.assertNotIn('framework-integrated-with-referenced-evidence', view['roles']['team-reviewer']['labels'])
        role['integration'].update(status='adopted', decision_ref='owner-adoption')
        apply(self.root, registry, files)
        view = r.inspect(str(self.root))
        self.assertIn('framework-integrated-with-referenced-evidence', view['roles']['team-reviewer']['labels'])
        self.assertFalse(view['roles']['team-reviewer']['evidence_verified'])
        self.assertEqual(r.resolve(str(self.root), 'review', 'codex', 'inventory')['runtime_id'], 'local-reviewer')
        registry['routes']['review']['codex'] = {'kind': 'framework', 'id': 'future-reviewer',
                                               'decision_ref': 'owner-adoption', 'expected_sha256': 'f' * 64}
        apply(self.root, registry, files)
        with self.assertRaisesRegex(ValueError, 'pending installation'):
            r.resolve(str(self.root), 'review', 'codex', 'inventory')

    def test_compare_preserves_missing_base_partial_coverage_and_missing_members(self):
        registry, files = fixture(base=False)
        apply(self.root, registry, files)
        candidate = {'id': 'future-reviewer', 'ref': 'candidate:fixed', 'capabilities': ['review'],
                     'files': {'profile.toml': 'new', 'extra.md': 'new'},
                     'runtime_paths': ['.codex/agents/local-reviewer.toml']}
        result = r.compare(str(self.root), [candidate])['comparisons'][0]
        self.assertEqual(result['runtime_collisions'], ['.codex/agents/local-reviewer.toml'])
        self.assertEqual({x['difference'] for x in result['differences']}, {'baseline-unavailable'})
        self.assertEqual(len(result['differences']), 3)
        self.assertFalse(result['route_changed'])
        registry, files = fixture()
        apply(self.root, registry, files)
        candidate['files'] = deepcopy(registry['roles']['team-reviewer']['baseline']['files'])
        candidate['files']['references/method.md'] = 'different incoming rule'
        (self.root / r.PACKAGES / 'team-reviewer/references/method.md').write_text('different local rule')
        result = r.compare(str(self.root), [candidate])['comparisons'][0]
        self.assertIn('conflict', {x['difference'] for x in result['differences']})
        self.assertEqual(result['semantic_coverage'], 'not-established-by-comparison')

    def test_resource_path_closure_case_and_native_identity(self):
        registry, files = fixture()
        for name in ('../outside.md', '.ai/core/role.md', 'C:/escape', 'refs/CON.md'):
            invalid = deepcopy(registry)
            invalid['roles']['team-reviewer']['members'][name] = 'a' * 64
            with self.subTest(name=name), self.assertRaises(ValueError):
                r.validate(invalid)
        registry['roles']['team-reviewer']['members']['PROFILE.toml'] = 'b' * 64
        with self.assertRaises(ValueError):
            r.validate(registry)
        registry, files = fixture()
        registry['roles']['team-reviewer']['projections']['codex']['runtime_id'] = 'different'
        with self.assertRaisesRegex(ValueError, 'name and runtime ID'):
            r.plan(str(self.root), registry, files)

    def test_actual_old_lock_and_unknown_protection(self):
        target = self.root / '.ai/framework.lock'
        target.write_bytes((ROOT / '.ai/framework.lock').read_bytes())
        original = target.read_bytes()
        registry, files = fixture()
        apply(self.root, registry, files)
        self.assertEqual(target.read_bytes(), original)
        self.assertEqual(r.resolve(str(self.root), 'review', 'codex', 'inventory')['model'], 'gpt-6-luna')
        # No registry operation grants framework ownership to project resources.
        _, members = r.lock(str(self.root))
        self.assertNotIn(r.runtime('codex', 'local-reviewer'), members)

    def test_framework_route_requires_owned_matching_complete_role_resources(self):
        registry, files = fixture()
        runtime_name = r.runtime('codex', 'future-reviewer')
        raw = b'name = "future-reviewer"\n'
        registry['routes']['review']['codex'] = {'kind': 'framework', 'id': 'future-reviewer',
                                               'decision_ref': 'owner', 'expected_sha256': p.digest(raw)}
        apply(self.root, registry, files)
        (self.root / runtime_name).write_bytes(raw)
        core = '.ai/core/sub-agents/future-reviewer/sub-agent.yaml'
        (self.root / core).parent.mkdir(parents=True)
        (self.root / core).write_bytes(b'role contract')
        managed = {runtime_name: {'owner': 'adapter/codex/sub-agent/future-reviewer', 'sha256': p.digest(raw)},
                   core: {'owner': 'sub-agent/future-reviewer', 'sha256': p.digest(b'role contract')}}
        with patch.object(r, 'lock', return_value=('a' * 64, managed)):
            result = r.resolve(str(self.root), 'review', 'codex', 'inventory')
            self.assertEqual(result['runtime_id'], 'future-reviewer')
            self.assertEqual(result['runtime_activation'], 'unknown')
            (self.root / core).write_bytes(b'modified framework rule')
            self.assertEqual(r.inspect(str(self.root))['managed_resources'][core]['state'], 'managed-drift')
            with self.assertRaisesRegex(ValueError, 'resource closure'):
                r.resolve(str(self.root), 'review', 'codex', 'inventory')

    def test_unknown_collision_is_reported_without_any_registered_semantic_match(self):
        registry, files = fixture()
        apply(self.root, registry, files)
        (self.root / '.codex/agents/unknown.toml').write_text('unknown')
        candidate = {'id': 'unrelated', 'ref': 'candidate:unrelated', 'capabilities': ['unrelated'],
                     'files': {}, 'runtime_paths': ['.codex/agents/unknown.toml']}
        result = r.compare(str(self.root), [candidate])
        self.assertEqual(result['comparisons'], [])
        self.assertEqual(result['runtime_collisions'][0]['ownership'], 'unknown-preserve')

    def test_unregister_preserves_authoring_and_foreign_files(self):
        registry, files = fixture()
        apply(self.root, registry, files)
        before = {n: (self.root / n).read_bytes() for n in files}
        unknown = self.root / r.PACKAGES / 'team-reviewer/unregistered.txt'
        unknown.write_text('custom')
        apply(self.root, r.empty(), {}, detach=[r.runtime('codex', 'local-reviewer')])
        for name, raw in before.items():
            self.assertEqual((self.root / name).read_bytes(), raw)
        self.assertEqual(unknown.read_text(), 'custom')


if __name__ == '__main__':
    unittest.main()
