"""Deterministic policy/portable CLI evidence; no paid model invocations."""
from copy import deepcopy
from hashlib import sha256
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'src'))
from distribution import subagent_policy as policy
from distribution import catalog, installation_state as state


class PolicyTests(unittest.TestCase):
    def test_task_choice_is_independent_of_parent_and_premium_needs_authority(self):
        for adapter, routine, reasoning in [('codex', 'gpt-6-luna', 'gpt-6.1-sol'),
                                             ('claude', 'haiku', 'sonnet')]:
            self.assertEqual(policy.resolve(policy.defaults(), adapter, 'inventory')['model'], routine)
            self.assertEqual(policy.resolve(policy.defaults(), adapter, 'implementation')['model'], reasoning)
            with self.assertRaisesRegex(ValueError, 'authorization'):
                policy.resolve(policy.defaults(), adapter, 'inventory', tier='premium')
            selected = policy.resolve(policy.defaults(), adapter, 'inventory', tier='premium', authority_ref='owner-task-1')
            self.assertFalse(selected['authority_verified'])
            self.assertFalse(selected['invocation_observed'])
        with self.assertRaisesRegex(ValueError, 'unknown'):
            policy.resolve(policy.defaults(), 'codex', 'unspecified')

    def test_provider_overrides_availability_and_effort(self):
        for profile in [{'model': 'gpt-6-astra'}, {'effort': 'ultra'}]:
            with self.assertRaisesRegex(ValueError, 'profile overrides'):
                policy.resolve(policy.defaults(), 'codex', 'inventory', profile=profile)
        observed = {'adapter': 'claude', 'runtime_version': '2.1.292', 'forced_model': None,
                    'forced_effort': None, 'models': [{'model': 'sonnet', 'efforts': ['medium']}]}
        result = policy.resolve(policy.defaults(), 'claude', 'implementation', observations=observed,
                                profile={'model': 'haiku'})
        self.assertEqual(result['outcome'], 'selected')
        self.assertFalse(result['invocation_observed'])
        for patch in [{'runtime_version': '2.1.250'}, {'runtime_version': '2.1.251'},
                      {'forced_model': 'opus'}, {'forced_effort': 'max'}, {'models': []},
                      {'models': [{'model': 'sonnet', 'efforts': ['low']}]}, {'adapter': 'codex'}]:
            with self.subTest(patch=patch), self.assertRaises(ValueError):
                policy.resolve(policy.defaults(), 'claude', 'implementation', observations={**observed, **patch})

    def test_custom_choices_validation_and_extensions(self):
        custom = policy.defaults()
        custom['adapters']['codex']['routine'] = {'model': 'gpt-future-small', 'effort': 'high'}
        custom['extensions']['rationale'] = {'team': 'approved task plan'}
        self.assertEqual(policy.resolve(custom, 'codex', 'translation')['model'], 'gpt-future-small')
        for change in [{'schema_version': 99}, {'on_unavailable': 'inherit'}, {'unknown': True}]:
            with self.assertRaises(ValueError):
                policy.validate({**custom, **change})
        custom['adapters']['codex']['routine']['model'] = 'gpt-6-astra'
        with self.assertRaisesRegex(ValueError, 'premium'):
            policy.validate(custom)
        with self.assertRaisesRegex(ValueError, 'duplicate'):
            policy.decode(b'{"schema_version":1,"schema_version":2}')
        for scalar in (1.5, float('nan'), float('inf')):
            proposed = policy.defaults()
            proposed['extensions']['value'] = scalar
            with self.assertRaises(ValueError):
                policy.validate(proposed)

    def test_read_only_plan_atomic_apply_stale_replay_and_unknown_preservation(self):
        with tempfile.TemporaryDirectory() as name:
            root = Path(name).resolve()
            unknown = root / 'my-agent.md'
            unknown.write_bytes(b'project custom instructions')
            before = sorted(root.rglob('*'))
            proposed = policy.defaults()
            proposed['extensions'] = {'owner': 'team', 'custom': [1, 2]}
            prepared = policy.plan(str(root), proposed)
            self.assertEqual(sorted(root.rglob('*')), before)
            self.assertEqual(policy.apply(str(root), prepared['plan'], prepared['plan_sha256'])['outcome'], 'applied')
            self.assertEqual(policy.apply(str(root), prepared['plan'], prepared['plan_sha256'])['outcome'], 'unchanged')
            actual = (root / policy.POLICY_PATH).read_bytes()
            self.assertEqual(policy.inspect(str(root))['policy'], proposed)
            replacement = policy.defaults()
            replacement['tasks']['translation'] = 'reasoning'
            next_plan = policy.plan(str(root), replacement)
            (root / policy.POLICY_PATH).write_bytes(actual + b' ')
            with self.assertRaisesRegex(ValueError, 'stale'):
                policy.apply(str(root), next_plan['plan'], next_plan['plan_sha256'])
            self.assertEqual((root / policy.POLICY_PATH).read_bytes(), actual + b' ')
            self.assertEqual(unknown.read_bytes(), b'project custom instructions')
            self.assertFalse((root / '.ai/framework.lock').exists())
            self.assertFalse((root / '.codex/config.toml').exists())
            self.assertFalse(list((root / '.ai/project').glob('*.writer')))

    def test_missing_policy_invalid_paths_and_writer_conflict(self):
        with tempfile.TemporaryDirectory() as name:
            root = Path(name).resolve()
            with self.assertRaisesRegex(ValueError, 'policy missing'):
                policy.execute({'operation': 'resolve', 'project_root': str(root), 'adapter': 'codex', 'task': 'inventory'})
            prepared = policy.plan(str(root), policy.defaults())
            (root / '.ai/project').mkdir(parents=True)
            guard = root / '.ai/project/sub-agent-policy.json.writer'
            guard.write_text('another writer')
            with self.assertRaisesRegex(ValueError, 'writer active'):
                policy.apply(str(root), prepared['plan'], prepared['plan_sha256'])
            self.assertEqual(guard.read_text(), 'another writer')
            guard.unlink()
            target = root / policy.POLICY_PATH
            target.mkdir()
            with self.assertRaises(ValueError):
                policy.inspect(str(root))
            target.rmdir()
            source = root / 'hardlink-source'
            source.write_bytes(policy.encode(policy.defaults()))
            os.link(source, target)
            with self.assertRaises(ValueError):
                policy.inspect(str(root))
            with self.assertRaises(ValueError):
                policy.inspect(str(root / '..' / root.name))

    def test_policy_initialization_rejects_case_alias_before_creating_paths(self):
        with tempfile.TemporaryDirectory() as name:
            root = Path(name).resolve()
            (root / '.AI').mkdir()
            with self.assertRaisesRegex(ValueError, 'case collision'):
                policy.plan(str(root), policy.defaults())
            self.assertEqual([p.name for p in root.iterdir()], ['.AI'])

    def test_three_way_comparison_does_not_adopt_or_erase_customization(self):
        base = policy.defaults()
        local, candidate = deepcopy(base), deepcopy(base)
        local['adapters']['codex']['routine']['effort'] = 'high'
        candidate['adapters']['codex']['routine']['effort'] = 'low'
        local['extensions']['team'] = 'intent'
        result = policy.compare(base, local, candidate)
        self.assertEqual({r['difference'] for r in result['differences']}, {'conflict', 'local-only'})
        self.assertEqual(result['adoption'], 'unknown')
        self.assertEqual(result['activation'], 'unknown')
        self.assertFalse(result['changed'])
        self.assertEqual(policy.compare(None, local, candidate)['outcome'], 'baseline-unavailable')


class CompatibilityTests(unittest.TestCase):
    def test_real_previous_installed_lock_remains_readable_but_arbitrary_closure_is_rejected(self):
        raw = (ROOT / '.ai/framework.lock').read_bytes()
        old = json.loads(raw)
        self.assertIn(tuple(r['path'] for r in old['engine']['files']),
                      (state.LEGACY_ENGINE_FILES, state.POLICY_ENGINE_FILES,
                       state.REGISTRY_ENGINE_FILES, state.ENGINE_FILES))
        catalog.lock_bytes(raw)
        for changed in [old['engine']['files'][:-1], old['engine']['files'] +
                        [{'path': 'src/tools/unowned.py', 'sha256': '0' * 64}]]:
            value = deepcopy(old)
            value['engine']['files'] = changed
            with self.assertRaises(ValueError):
                catalog.lock_bytes(policy.encode(value))

    def test_portable_pinned_cli_without_source_checkout_imports_and_tamper_rejection(self):
        with tempfile.TemporaryDirectory() as name:
            root = Path(name).resolve()
            engine = root / 'engine'
            engine.mkdir()
            rows = []
            for member in state.ENGINE_FILES:
                raw = (ROOT / member).read_bytes()
                dest = engine / member
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_bytes(raw)
                rows.append({'path': member, 'sha256': sha256(raw).hexdigest()})
            pin = {'id': 'framework-managed-installation', 'version': '2.0.0',
                   'source_commit': '1' * 40, 'files': rows}
            (engine / 'engine.json').write_bytes(policy.encode({'engine_package_version': 1, 'engine': pin}))
            request = {'operation': 'defaults', 'engine_root': str(engine), 'engine': pin}
            def invoke(value):
                return subprocess.run([sys.executable, '-I', '-B', str(engine / 'src/tools/manage-sub-agents.py')],
                                      input=policy.encode(value), stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                      cwd=root, timeout=45)
            result = invoke(request)
            self.assertEqual(result.returncode, 0, (result.stdout, result.stderr))
            self.assertEqual(json.loads(result.stdout)['policy']['adapters']['claude']['routine']['model'], 'haiku')
            project = root / 'consumer'
            project.mkdir()
            request.update(operation='plan', project_root=str(project), proposed=policy.defaults())
            prepared = json.loads(invoke(request).stdout)
            request.pop('proposed')
            request.update(operation='apply', plan=prepared['plan'], plan_sha256=prepared['plan_sha256'])
            result = invoke(request)
            self.assertEqual(result.returncode, 0, (result.stdout, result.stderr))
            self.assertEqual(policy.inspect(str(project))['policy'], policy.defaults())
            from distribution import subagent_registry as registry
            raw = 'name = "team-worker"\n'
            custom = registry.empty()
            custom['roles']['team-worker'] = {
                'origin': 'project-authored', 'source_ref': 'owner-task', 'intent': 'Bounded team work',
                'acceptance': ['Return bounded output'], 'capabilities': ['inventory'],
                'members': {'codex.toml': policy.digest(raw.encode())}, 'baseline': None,
                'projections': {'codex': {'source': 'codex.toml', 'runtime_id': 'team-worker'}},
                'integration': {'candidate_ref': None, 'coverage': 'not-assessed', 'status': 'pending',
                                'evidence_ref': None, 'decision_ref': None}}
            request = {'engine_root': str(engine), 'engine': pin, 'operation': 'registry-plan',
                       'project_root': str(project), 'proposed': custom,
                       'files': {registry.PACKAGES + 'team-worker/codex.toml': raw}}
            prepared_result = invoke(request)
            self.assertEqual(prepared_result.returncode, 0, prepared_result.stdout)
            prepared = json.loads(prepared_result.stdout)
            request = {k: v for k, v in request.items() if k not in {'proposed', 'files'}}
            request.update(operation='registry-apply', plan=prepared['plan'], plan_sha256=prepared['plan_sha256'])
            result = invoke(request)
            self.assertEqual(result.returncode, 0, result.stdout)
            self.assertEqual(registry.inspect(str(project))['registry'], custom)
            (engine / 'src/distribution/subagent_policy.py').write_bytes(b'raise RuntimeError("untrusted")')
            result = invoke(request)
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(json.loads(result.stdout)['outcome'], 'blocked')


if __name__ == '__main__':
    unittest.main()
