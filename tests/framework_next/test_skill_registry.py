"""Project native skill registry contracts; no model calls or activation claims."""
from copy import deepcopy
from hashlib import sha256
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'src'))
from distribution import skill_registry as r, subagent_policy as p, project_layout as layout
from distribution import installation_state as state


def fixture(runtime_id='team-check', base=True):
    entry = '---\nname: ' + runtime_id + '\ndescription: Review bounded evidence\n---\nRead [method](references/method.md).\n'
    files = {'codex.md': entry, 'claude.md': entry, 'references/method.md': 'Preserve unknown evidence.\n',
             'scripts/check.py': 'from support import check\ncheck()\n',
             'scripts/support.py': 'def check():\n    return True\n', 'templates/report.md': '# Report\n'}
    registry = r.empty()
    registry['skills']['team-check'] = {
        'origin': 'project-derived', 'source_ref': 'fixture:original', 'intent': 'Preserve team review.',
        'acceptance': ['Unknown stays unknown.'], 'capabilities': ['review'],
        'members': {n: p.digest(v.encode()) for n, v in files.items()},
        'baseline': {'ref': 'fixture:original', 'files': dict(files)} if base else None,
        'projections': {a: {'runtime_id': runtime_id, 'files': {'SKILL.md': a + '.md',
                         **{n: n for n in files if n not in ('codex.md', 'claude.md')}}}
                        for a in ('codex', 'claude')},
        'integration': {'candidate_ref': None, 'coverage': 'not-assessed', 'status': 'pending',
                        'evidence_ref': None, 'decision_ref': None}}
    registry['routes']['review'] = {a: {'kind': 'project', 'id': 'team-check',
                                      'decision_ref': 'owner', 'expected_sha256': None}
                                   for a in ('codex', 'claude')}
    return registry, {r.PACKAGES + 'team-check/' + n: v for n, v in files.items()}


def apply(root, registry, files, **kwargs):
    planned = r.plan(str(root), registry, files, **kwargs)
    return r.apply(str(root), planned['plan'], planned['plan_sha256'])


def engine():
    return {'id': 'framework-managed-installation', 'version': '2.0.0', 'source_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
            'files': [{'path': n, 'sha256': sha256((ROOT / n).read_bytes()).hexdigest()} for n in state.ENGINE_FILES]}


class SkillRegistryTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name).resolve()
        self.project = str(self.root)

    def test_native_multifile_projection_and_complete_project_route(self):
        registry, files = fixture()
        self.assertEqual(apply(self.root, registry, files)['outcome'], 'applied')
        for adapter, binding in registry['skills']['team-check']['projections'].items():
            selected = r.resolve(self.project, 'review', adapter)
            self.assertEqual(selected['runtime_activation'], 'unknown')
            self.assertEqual(len(selected['resources']), 6)
            for destination, source in binding['files'].items():
                self.assertEqual((self.root / r.native(adapter, binding, destination)).read_text(),
                                 files[r.PACKAGES + 'team-check/' + source])
        self.assertFalse((self.root / '.ai/framework.lock').exists())
        (self.root / r.PACKAGES / 'team-check/scripts/support.py').write_text('drift')
        with self.assertRaisesRegex(ValueError, 'resource drift'):
            r.resolve(self.project, 'review', 'codex')

    def test_projection_resource_drift_blocks_route(self):
        registry, files = fixture()
        apply(self.root, registry, files)
        binding = registry['skills']['team-check']['projections']['claude']
        (self.root / r.native('claude', binding, 'references/method.md')).unlink()
        with self.assertRaisesRegex(ValueError, 'resource drift'):
            r.resolve(self.project, 'review', 'claude')

    def test_same_bytes_unknown_adoption_requires_current_preimage(self):
        registry, files = fixture()
        entry = r.runtime('codex', 'team-check')
        target = self.root / entry
        target.parent.mkdir(parents=True)
        raw = files[r.PACKAGES + 'team-check/codex.md'].encode()
        target.write_bytes(raw)
        with self.assertRaisesRegex(ValueError, 'explicit adoption'):
            r.plan(self.project, registry, files)
        apply(self.root, registry, files, adopt={entry: p.digest(raw)})
        self.assertEqual(r.inspect(self.project)['skills']['team-check']['local_delta'], 'none')

    def test_detach_preserves_authoring_baseline_unknown_siblings_and_replay(self):
        registry, files = fixture()
        apply(self.root, registry, files)
        unknown = self.root / '.agents/skills/team-check/unknown.bin'
        unknown.write_bytes(b'\x00\xff')
        wanted = r.expected(registry)
        detached = [n for n in wanted if not n.startswith(r.PACKAGES)]
        retained = deepcopy(registry)
        retained['skills']['team-check']['projections'] = {}
        retained['routes'] = {}
        prepared = r.plan(self.project, retained, {}, detach=detached)
        self.assertEqual(r.apply(self.project, prepared['plan'], prepared['plan_sha256'])['outcome'], 'applied')
        self.assertEqual(unknown.read_bytes(), b'\x00\xff')
        for name in files:
            self.assertTrue((self.root / name).is_file())
        self.assertEqual(r.inspect(self.project)['registry']['skills']['team-check'], retained['skills']['team-check'])
        self.assertEqual(r.inspect(self.project)['registry']['skills']['team-check']['baseline'], registry['skills']['team-check']['baseline'])
        self.assertEqual(r.apply(self.project, prepared['plan'], prepared['plan_sha256'])['outcome'], 'unchanged')
        entry = self.root / detached[0]
        entry.write_bytes(b'reappeared')
        with self.assertRaisesRegex(ValueError, 'completed registry plan'):
            r.apply(self.project, prepared['plan'], prepared['plan_sha256'])
        self.assertEqual(entry.read_bytes(), b'reappeared')

    def test_completed_same_registry_repair_cannot_reacquire_restored_preimage(self):
        registry, files = fixture()
        apply(self.root, registry, files)
        name = r.runtime('codex', 'team-check')
        entry = self.root / name
        expected = entry.read_bytes()
        entry.write_bytes(b'foreign preimage')
        repaired = r.plan(self.project, registry, {}, adopt={name: p.digest(b'foreign preimage')})
        self.assertEqual(repaired['plan']['writes'][-1]['before_sha256'], repaired['plan']['writes'][-1]['after_sha256'])
        self.assertEqual(r.apply(self.project, repaired['plan'], repaired['plan_sha256'])['outcome'], 'applied')
        marker = self.root / '.ai/local/skill-registry-completed' / (repaired['plan_sha256'] + '.json')
        marker_bytes = p.encode({'completion_version': 1, 'plan_sha256': repaired['plan_sha256']})
        self.assertEqual(marker.read_bytes(), marker_bytes)
        entry.write_bytes(b'foreign preimage')
        with self.assertRaisesRegex(ValueError, 'completed registry plan'):
            r.apply(self.project, repaired['plan'], repaired['plan_sha256'])
        self.assertEqual(entry.read_bytes(), b'foreign preimage')
        entry.write_bytes(expected)
        # Another completed plan must not forget this earlier completion fact.
        later = r.plan(self.project, registry, {})
        self.assertNotEqual(later['plan_sha256'], repaired['plan_sha256'])
        self.assertEqual(r.apply(self.project, later['plan'], later['plan_sha256'])['outcome'], 'applied')
        self.assertEqual(marker.read_bytes(), marker_bytes)
        entry.write_bytes(b'foreign preimage')
        with self.assertRaisesRegex(ValueError, 'completed registry plan'):
            r.apply(self.project, repaired['plan'], repaired['plan_sha256'])
        self.assertEqual(entry.read_bytes(), b'foreign preimage')

    def test_fresh_explicit_repair_is_distinct_from_completed_plan_replay(self):
        registry, files = fixture()
        apply(self.root, registry, files)
        name = r.runtime('codex', 'team-check')
        target = self.root / name
        expected = target.read_bytes()
        target.write_bytes(b'foreign')
        original = r.plan(self.project, registry, {}, adopt={name: p.digest(b'foreign')})
        r.apply(self.project, original['plan'], original['plan_sha256'])
        target.write_bytes(b'foreign')
        with self.assertRaisesRegex(ValueError, 'completed registry plan'):
            r.apply(self.project, original['plan'], original['plan_sha256'])
        fresh = r.plan(self.project, registry, {}, adopt={name: p.digest(b'foreign')})
        self.assertEqual(original['plan']['writes'], fresh['plan']['writes'])
        self.assertNotEqual(original['plan']['operation_id'], fresh['plan']['operation_id'])
        self.assertNotEqual(original['plan_sha256'], fresh['plan_sha256'])
        self.assertEqual(r.apply(self.project, fresh['plan'], fresh['plan_sha256'])['outcome'], 'applied')
        self.assertEqual(target.read_bytes(), expected)
        target.write_bytes(b'foreign')
        with self.assertRaisesRegex(ValueError, 'completed registry plan'):
            r.apply(self.project, original['plan'], original['plan_sha256'])
        self.assertEqual(target.read_bytes(), b'foreign')
        for operation_id in (None, 'not-a-uuid', 'AAAAAAAA-AAAA-4AAA-8AAA-AAAAAAAAAAAA',
                             '00000000-0000-0000-0000-000000000000'):
            forged = deepcopy(fresh['plan'])
            forged['operation_id'] = operation_id
            with self.subTest(operation_id=operation_id), self.assertRaises(ValueError):
                r.apply(self.project, forged, p.digest(p.encode(forged)))
        self.assertEqual(target.read_bytes(), b'foreign')

    def test_malformed_or_mismatched_completion_marker_rejects_before_repair(self):
        registry, files = fixture()
        apply(self.root, registry, files)
        name = r.runtime('codex', 'team-check')
        entry = self.root / name
        entry.write_bytes(b'foreign')
        planned = r.plan(self.project, registry, {}, adopt={name: p.digest(b'foreign')})
        marker = self.root / '.ai/local/skill-registry-completed' / (planned['plan_sha256'] + '.json')
        for raw in (b'invalid', p.encode({'completion_version': 1, 'plan_sha256': '0' * 64})):
            marker.write_bytes(raw)
            with self.subTest(raw=raw), self.assertRaisesRegex(ValueError, 'completion marker'):
                r.apply(self.project, planned['plan'], planned['plan_sha256'])
            self.assertEqual(entry.read_bytes(), b'foreign')
            self.assertEqual(marker.read_bytes(), raw)

    def test_completion_directory_preflight_rejects_file_before_any_plan_write(self):
        registry, files = fixture()
        planned = r.plan(self.project, registry, files)
        directory = self.root / '.ai/local/skill-registry-completed'
        directory.parent.mkdir(parents=True)
        directory.write_bytes(b'preserve unknown file')
        with self.assertRaises(ValueError):
            r.apply(self.project, planned['plan'], planned['plan_sha256'])
        self.assertFalse((self.root / r.REGISTRY).exists())
        self.assertFalse((self.root / r.PACKAGES).exists())
        self.assertEqual(directory.read_bytes(), b'preserve unknown file')

    def test_completion_publication_failure_is_interrupted_and_exact_plan_resumes(self):
        registry, files = fixture()
        apply(self.root, registry, files)
        # A no-op resource plan still needs its own durable completion fact.
        planned = r.plan(self.project, registry, {})
        marker = self.root / '.ai/local/skill-registry-completed' / (planned['plan_sha256'] + '.json')
        original = os.replace
        def fail_completion(source, target):
            if Path(target) == marker:
                raise OSError('fixture completion publication interruption')
            return original(source, target)
        with patch.object(r.os, 'replace', side_effect=fail_completion):
            result = r.apply(self.project, planned['plan'], planned['plan_sha256'])
        self.assertEqual(result['outcome'], 'interrupted')
        self.assertFalse(result['changed'])
        self.assertFalse(marker.exists())
        self.assertFalse(list(marker.parent.glob('.skill-completion-*')))
        self.assertEqual(r.apply(self.project, planned['plan'], planned['plan_sha256'])['outcome'], 'applied')
        self.assertTrue(marker.is_file())
        self.assertEqual(r.apply(self.project, planned['plan'], planned['plan_sha256'])['outcome'], 'unchanged')

    def test_detach_requires_registered_exact_files(self):
        registry, files = fixture()
        apply(self.root, registry, files)
        retained = deepcopy(registry)
        retained['skills']['team-check']['projections'] = {}
        retained['routes'] = {}
        with self.assertRaisesRegex(ValueError, 'explicit detach'):
            r.plan(self.project, retained, {})
        detached = [n for n in r.expected(registry) if not n.startswith(r.PACKAGES)]
        (self.root / detached[0]).write_text('drift')
        with self.assertRaisesRegex(ValueError, 'exact registered'):
            r.plan(self.project, retained, {}, detach=detached)

    def test_record_deletion_and_detach_baseline_erasure_are_rejected(self):
        registry, files = fixture()
        apply(self.root, registry, files)
        with self.assertRaisesRegex(ValueError, 'records must be retained'):
            r.plan(self.project, r.empty(), {})
        retained = deepcopy(registry)
        retained['skills']['team-check']['projections'] = {}
        retained['skills']['team-check']['baseline'] = None
        retained['routes'] = {}
        detached = [n for n in r.expected(registry) if not n.startswith(r.PACKAGES)]
        with self.assertRaisesRegex(ValueError, 'preserve provenance and baseline'):
            r.plan(self.project, retained, {}, detach=detached)
        self.assertEqual(r.inspect(self.project)['registry'], registry)

    def test_managed_collision_even_same_bytes_adoption_is_denied(self):
        registry, files = fixture()
        entry = r.runtime('codex', 'team-check')
        with patch.object(r, 'lock', return_value=('a' * 64, {entry: {}})):
            with self.assertRaisesRegex(ValueError, 'framework-owned'):
                r.plan(self.project, registry, files, adopt={entry: 'b' * 64})

    def test_interrupted_exact_plan_resume_and_stale_input(self):
        registry, files = fixture()
        prepared = r.plan(self.project, registry, files)
        original = os.replace
        count = 0
        def interrupt(*args):
            nonlocal count
            count += 1
            if count == 3:
                raise OSError('fixture interruption')
            return original(*args)
        with patch.object(r.os, 'replace', side_effect=interrupt):
            partial = r.apply(self.project, prepared['plan'], prepared['plan_sha256'])
        self.assertEqual(partial['outcome'], 'interrupted')
        self.assertFalse((self.root / r.REGISTRY).exists())
        self.assertEqual(r.apply(self.project, prepared['plan'], prepared['plan_sha256'])['outcome'], 'applied')

    def test_preimage_drift_and_lock_drift_fail_before_mutation(self):
        registry, files = fixture()
        prepared = r.plan(self.project, registry, files)
        entry = self.root / r.runtime('codex', 'team-check')
        entry.parent.mkdir(parents=True)
        entry.write_text('foreign')
        with self.assertRaisesRegex(ValueError, 'stale'):
            r.apply(self.project, prepared['plan'], prepared['plan_sha256'])
        self.assertFalse((self.root / r.PACKAGES).exists())
        with patch.object(r, 'lock', return_value=('a' * 64, {})):
            with self.assertRaisesRegex(ValueError, 'lock changed'):
                r.apply(self.project, prepared['plan'], prepared['plan_sha256'])

    def test_invalid_identity_case_collision_and_opaque_budget_are_pre_mutation(self):
        for change in ('identity', 'collision', 'opaque', 'oversize'):
            registry, files = fixture()
            skill = registry['skills']['team-check']
            if change == 'identity':
                skill['projections']['codex']['runtime_id'] = 'other'
            elif change == 'collision':
                skill['projections']['codex']['files']['skill.md'] = 'codex.md'
            else:
                name = r.PACKAGES + 'team-check/scripts/support.py'
                files[name] = '\x00' if change == 'opaque' else 'x' * (256 * 1024 + 1)
                skill['members']['scripts/support.py'] = p.digest(files[name].encode())
            with self.subTest(change=change), self.assertRaises(ValueError):
                r.plan(self.project, registry, files)
        self.assertFalse((self.root / r.REGISTRY).exists())

    def test_declared_framework_metadata_uses_real_loader_plain_native_does_not_require_it(self):
        registry, files = fixture()
        files[r.PACKAGES + 'team-check/skill-package.yaml'] = 'invalid: metadata\n'
        registry['skills']['team-check']['members']['skill-package.yaml'] = p.digest(b'invalid: metadata\n')
        with self.assertRaises(ValueError):
            r.plan(self.project, registry, files)
        self.assertFalse((self.root / r.REGISTRY).exists())

    def test_declared_framework_resource_reference_missing_is_rejected(self):
        from framework_next.test_distribution_contracts import skill
        metadata = skill()
        metadata['id'] = 'team-check'
        metadata['knowledge_consumption'] = []
        registry, _ = fixture()
        contents = {'SKILL.md': '---\nname: team-check\ndescription: Review\n---\n[Method](review.md)\n',
                    'review.md': 'Review bounded evidence.\n', 'skill-package.yaml': json.dumps(metadata)}
        selected = registry['skills']['team-check']
        selected['members'] = {n: p.digest(v.encode()) for n, v in contents.items()}
        selected['baseline'] = None
        selected['projections'] = {a: {'runtime_id': 'team-check', 'files': {'SKILL.md': 'SKILL.md', 'review.md': 'review.md'}}
                                   for a in ('codex', 'claude')}
        files = {r.PACKAGES + 'team-check/' + n: v for n, v in contents.items()}
        apply(self.root, registry, files)
        # Hash-consistent registry edits do not excuse a declared missing resource.
        del selected['members']['review.md']
        selected['projections']['codex']['files'].pop('review.md')
        selected['projections']['claude']['files'].pop('review.md')
        files.pop(r.PACKAGES + 'team-check/review.md')
        with self.assertRaises((ValueError, KeyError)):
            r.plan(self.project, registry, files)

    def test_three_way_union_addition_deletion_and_conflict(self):
        registry, files = fixture()
        apply(self.root, registry, files)
        incoming = dict(registry['skills']['team-check']['baseline']['files'])
        incoming.pop('scripts/support.py')
        incoming['new.md'] = 'new'
        incoming['references/method.md'] = 'candidate'
        (self.root / r.PACKAGES / 'team-check/references/method.md').write_text('local')
        result = r.compare(self.project, [{'id': 'team-check', 'ref': 'candidate:v2', 'capabilities': ['review'],
                                          'files': incoming, 'runtime_paths': []}])
        rows = {n['path']: n for n in result['comparisons'][0]['differences']}
        self.assertEqual(rows['new.md']['difference'], 'candidate-only')
        self.assertIsNone(rows['scripts/support.py']['candidate'])
        self.assertEqual(rows['references/method.md']['difference'], 'conflict')
        self.assertFalse(result['comparisons'][0]['route_changed'])

    def test_compare_reports_unknown_and_absent_managed_native_collisions(self):
        unknown = self.root / '.agents/skills/unknown/references/method.md'
        unknown.parent.mkdir(parents=True)
        unknown.write_text('preserve')
        managed_entry = '.claude/skills/aicf-managed/SKILL.md'
        candidate = {'id': 'unrelated', 'ref': 'candidate', 'capabilities': [], 'files': {},
                     'runtime_paths': ['.agents/skills/unknown/references/method.md', managed_entry]}
        with patch.object(r, 'lock', return_value=('a' * 64, {managed_entry: {'sha256': 'b' * 64}})):
            result = r.compare(self.project, [candidate])
        self.assertEqual(result['comparisons'], [])
        self.assertEqual([row['ownership'] for row in result['runtime_collisions']],
                         ['unknown-preserve', 'framework-managed'])
        self.assertEqual(unknown.read_text(), 'preserve')

    def test_compare_accepts_framework_dotted_ids_and_original_prefixed_native_paths(self):
        registry, files = fixture()
        apply(self.root, registry, files)
        native_paths = ['.agents/skills/reviewer.audit/SKILL.md',
                        '.claude/skills/aicf-reviewer.audit/SKILL.md']
        for name in native_paths:
            target = self.root / name
            target.parent.mkdir(parents=True)
            target.write_text('preserve framework candidate collision')
        candidate = {'id': 'reviewer.audit', 'ref': 'candidate:dotted', 'capabilities': ['review'],
                     'files': {}, 'runtime_paths': native_paths}
        result = r.compare(self.project, [candidate])
        self.assertEqual([row['path'] for row in result['runtime_collisions']], native_paths)
        self.assertEqual(result['comparisons'][0]['project_skill'], 'team-check')
        # Framework IDs use their established grammar, rather than project ID limits.
        candidate['id'] = 'reviewer.' + 'audit' * 14
        candidate['runtime_paths'] = []
        self.assertEqual(r.compare(self.project, [candidate])['outcome'], 'compared')
        for name in ('.agents/skills/reviewer..audit/SKILL.md',
                     '.agents/skills/reviewer.audit/../outside.md',
                     '.agents/skills/reviewer.audit/SKILL.md/../../outside.md',
                     '.agents/skills/Reviewer.audit/SKILL.md'):
            candidate['runtime_paths'] = [name]
            with self.subTest(path=name), self.assertRaises(ValueError):
                r.compare(self.project, [candidate])
        # Project-owned authoring identifiers intentionally remain stricter.
        registry['skills']['team.check'] = registry['skills'].pop('team-check')
        with self.assertRaisesRegex(ValueError, 'registry identifier'):
            r.validate(registry)

    def test_missing_baseline_is_unknown_not_unchanged(self):
        registry, files = fixture(base=False)
        apply(self.root, registry, files)
        result = r.compare(self.project, [{'id': 'team-check', 'ref': 'candidate', 'capabilities': [],
                                          'files': {}, 'runtime_paths': []}])
        self.assertTrue(all(n['difference'] == 'baseline-unavailable' for n in result['comparisons'][0]['differences']))
        self.assertEqual(r.inspect(self.project)['skills']['team-check']['local_delta'], 'unknown')

    def test_framework_route_uses_actual_prefixed_binding_and_all_core_files(self):
        registry, files = fixture()
        registry['routes']['review']['codex'] = {'kind': 'framework', 'id': 'reviewer.audit', 'decision_ref': 'owner',
                                                'expected_sha256': p.digest(b'entry')}
        apply(self.root, registry, files)
        entry = '.agents/skills/aicf-reviewer.audit/SKILL.md'
        core = '.ai/core/skills/reviewer.audit/SKILL.md'
        support = '.ai/core/skills/reviewer.audit/references/method.md'
        for name, raw in [(entry, b'entry'), (core, b'core'), (support, b's' * (256 * 1024 + 1))]:
            target = self.root / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(raw)
        managed = {entry: {'owner': 'adapter/codex/skill/reviewer.audit', 'sha256': p.digest(b'entry'),
                          'binding': {'adapter': 'codex', 'skill': 'reviewer.audit', 'entry_name': 'aicf-reviewer.audit', 'core_entrypoint': core}},
                   core: {'owner': 'skill/reviewer.audit', 'sha256': p.digest(b'core')},
                   support: {'owner': 'skill/reviewer.audit', 'sha256': p.digest(b's' * (256 * 1024 + 1))}}
        with patch.object(r, 'lock', return_value=('a' * 64, managed)):
            self.assertEqual(r.resolve(self.project, 'review', 'codex')['entry'], entry)
            (self.root / support).unlink()
            with self.assertRaisesRegex(ValueError, 'resource closure'):
                r.resolve(self.project, 'review', 'codex')

    def test_legacy_only_layout_full_migration_rewrites_registered_projection_hashes(self):
        (self.root / layout.LEGACY).mkdir(parents=True)
        registry, files = fixture()
        files = {n.replace(layout.CANONICAL, layout.LEGACY): v.replace('Preserve unknown', 'Read .ai/custom/skills/team-check/; preserve unknown') for n, v in files.items()}
        for name, value in files.items():
            member = name.split('/team-check/', 1)[1]
            registry['skills']['team-check']['members'][member] = p.digest(value.encode())
        apply(self.root, registry, files)
        self.assertEqual(r.inspect(self.project)['path'], layout.LEGACY + '/skill-registry.json')
        prepared = layout.plan(self.project, engine())
        self.assertEqual(layout.apply(self.project, prepared['plan'], prepared['plan_sha256'], engine())['outcome'], 'applied')
        selected = r.resolve(self.project, 'review', 'codex')
        for name in selected['resources'] + selected['projections']:
            self.assertNotIn('.ai/custom/', (self.root / name).read_text())
        self.assertEqual(r.inspect(self.project)['registry']['skills']['team-check']['baseline'], registry['skills']['team-check']['baseline'])
        self.assertEqual(layout.apply(self.project, prepared['plan'], prepared['plan_sha256'], engine())['outcome'], 'unchanged')
        (self.root / layout.LEGACY).mkdir()
        with self.assertRaisesRegex(ValueError, 'ambiguous'):
            r.inspect(self.project)

    def test_pinned_public_cli_and_historical_closure(self):
        pin = engine()
        request = {'operation': 'registry-inspect', 'project_root': self.project,
                   'engine_root': str(ROOT), 'engine': pin}
        result = subprocess.run([sys.executable, '-I', '-B', str(ROOT / 'src/tools/manage-skills.py')],
                                input=json.dumps(request).encode(), capture_output=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(json.loads(result.stdout)['outcome'], 'inspected')
        self.assertEqual(len(state.LAYOUT_ENGINE_FILES), 27)
        self.assertEqual(len(state.ENGINE_FILES), 29)
        request['engine']['files'][0]['sha256'] = '0' * 64
        result = subprocess.run([sys.executable, '-I', '-B', str(ROOT / 'src/tools/manage-skills.py')],
                                input=json.dumps(request).encode(), capture_output=True)
        self.assertEqual(result.returncode, 1)
        self.assertEqual(json.loads(result.stdout)['outcome'], 'blocked')


if __name__ == '__main__':
    unittest.main()
