#!/usr/bin/env python3
"""Independent behavior expectations for bounded document authoring."""
from __future__ import annotations

import copy
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import yaml

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / '.ai/scripts'))
import artifact_authoring as AUTHOR

NOW = '2026-09-21T21:00:00+08:00'
LATER = '2026-09-21T21:05:00+08:00'
WF = '2026-09-21-authoring-fixture'
ASM = 'ASM-20260921-21-a7b'
GOV = '.ai/assets/skills/ai-context-governance/templates/'
AUDIT = '.ai/assets/skills/ai-context-auditor/templates/ai-context-audit-report-template.md'
LOCATOR = '.dev/assessments/templates/assessment-locator-template.yaml'


class AuthoringFixture(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.seed = tempfile.TemporaryDirectory(prefix='document-authoring-seed-')
        cls.addClassCleanup(cls.seed.cleanup)
        cls.seed_ready = False

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='document-authoring-')
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name).resolve()
        if self.seed_ready:
            shutil.copytree(self.seed.name, self.root, dirs_exist_ok=True)
            self.head = self.seed_head
            return
        for ref in (GOV + 'workflow-locator-template.yaml', GOV + 'ai-context-maintenance-workflow-plan-template.md',
                    GOV + 'ai-context-remediation-task-template.json', GOV + 'ai-context-remediation-report-template.md', AUDIT, LOCATOR,
                    '.ai/scripts/validate-workflow-artifacts.py', '.ai/scripts/validate-assessment-artifacts.py',
                    '.ai/scripts/python_prerequisites.py', '.ai/scripts/python-entrypoints.json',
                    '.ai/scripts/artifact_core.py', 'requirements.txt'):
            self.put(ref, (ROOT / ref).read_bytes())
        self.put('.gitignore', b'.dev/ai-context/local/\n__pycache__/\n')
        self.put('.dev/workflows/README.MD', b'# Workflows\n')
        self.put('.dev/workflows/INDEX.MD', b'# Workflow Index\n\n## Workflows\n\n| Workflow | Title | Owner | Status | Updated | Entry |\n| --- | --- | --- | --- | --- | --- |\n\n<!-- unrelated prose: preserve byte for byte -->\n')
        self.put('.dev/assessments/README.MD', b'# Assessments\n')
        text = '# Assessment Index\n\n'
        for section in ('Draft Assessments', 'Final Assessments', 'Superseded Or Withdrawn Assessments'):
            text += f'## {section}\n\n| Assessment | Title | Type | Owner | Status | Subject Commit | Updated | Report |\n| --- | --- | --- | --- | --- | --- | --- | --- |\n\n'
        self.put('.dev/assessments/INDEX.MD', text.encode())
        for args in (('init', '-q'), ('config', 'user.email', 'fixture@example.invalid'),
                     ('config', 'user.name', 'Fixture'), ('add', '.'), ('commit', '-qm', 'fixture'),
                     ('switch', '-qc', f'codex/{WF}')):
            subprocess.run(['git', '-C', str(self.root), *args], check=True, capture_output=True)
        self.head = subprocess.check_output(['git', '-C', str(self.root), 'rev-parse', 'HEAD'], text=True).strip()
        shutil.copytree(self.root, self.seed.name, dirs_exist_ok=True)
        type(self).seed_head = self.head
        type(self).seed_ready = True

    def put(self, ref, content):
        path = self.root / ref
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)

    def workflow(self):
        return {'version': '1.0', 'operation': 'workflow.create', 'timestamp': NOW, 'id': WF,
                'title': 'Independent fixture workflow', 'branch': f'codex/{WF}', 'base_branch': 'main',
                'body': 'Owner-authorized fixture scope. No actual execution claimed.',
                'task': {'id': 'TASK-001', 'target': 'Inspect the fixture', 'model': 'fixture-model',
                         'reasoning_effort': 'fixture-effort', 'steps': ['Inspect'], 'validation': [], 'files': []}}

    def assessment(self):
        return {'version': '1.0', 'operation': 'assessment.create', 'timestamp': NOW, 'id': ASM,
                'title': 'Independent fixture assessment', 'type': 'audit',
                'artifact_branch': f'codex/{WF}', 'base_branch': 'main',
                'subject': {'repository': 'example/fixture', 'branch': 'main', 'commit': self.head},
                'included': ['.ai/scripts'], 'excluded': ['src'], 'next_action': 'Collect observations',
                'body': 'Independent fixture observations, with no execution claim.'}

    def execute(self, request):
        preview = AUTHOR.plan(self.root, request)
        return AUTHOR.apply(self.root, preview.request, preview.digest)

    def snapshot(self):
        return {str(path.relative_to(self.root)): path.read_bytes()
                for path in self.root.rglob('*') if path.is_file()
                and '.git' not in path.relative_to(self.root).parts
                and '.dev/ai-context/local/' not in path.relative_to(self.root).as_posix()}

    def load(self, ref):
        return yaml.safe_load((self.root / ref).read_text(encoding='utf-8'))


class AuthoringTests(AuthoringFixture):
    def test_preview_is_deterministic_read_only_and_create_derives_index(self):
        before = self.snapshot()
        first = AUTHOR.plan(self.root, self.workflow())
        second = AUTHOR.plan(self.root, self.workflow())
        self.assertEqual(first.digest, second.digest)
        self.assertEqual(first.changes, second.changes)
        self.assertEqual(before, self.snapshot())
        self.execute(self.workflow())
        locator = self.load(f'.dev/workflows/{WF}/workflow.yaml')
        self.assertEqual(WF, locator['workflow_id'])
        self.assertEqual(NOW, locator['created_at'])
        self.assertEqual('in_progress', locator['status'])
        self.assertEqual('1.2.0', locator['template_version'])
        index = (self.root / '.dev/workflows/INDEX.MD').read_text()
        self.assertIn('| Independent fixture workflow |', index)
        self.assertIn('<!-- unrelated prose: preserve byte for byte -->', index)
        task = self.load(f'.dev/workflows/{WF}/tasks/TASK-001.json')
        self.assertEqual('in_progress', task['status'])
        self.assertNotIn('passed', json.dumps(task['results']))

    def test_collision_and_unknown_version_leave_all_documents_unchanged(self):
        self.execute(self.workflow())
        before = self.snapshot()
        with self.assertRaises(ValueError):
            AUTHOR.plan(self.root, self.workflow())
        bad = self.workflow(); bad['version'] = '9000.0'
        with self.assertRaises(ValueError):
            AUTHOR.plan(self.root, bad)
        self.assertEqual(before, self.snapshot())

    def test_preview_digest_rejects_changed_index_before_any_document_write(self):
        request = self.workflow()
        preview = AUTHOR.plan(self.root, request)
        path = self.root / '.dev/workflows/INDEX.MD'
        path.write_bytes(path.read_bytes() + b'External edit\n')
        before = self.snapshot()
        with self.assertRaises(ValueError):
            AUTHOR.apply(self.root, request, preview.digest)
        self.assertEqual(before, self.snapshot())

    def test_unsupported_mutations_do_not_change_identity_or_subject(self):
        self.execute(self.assessment())
        before = self.snapshot()
        for field, value in [('created_at', LATER), ('subject', {'commit': 'b' * 40}),
                             ('assessment_id', 'ASM-20260921-21-zzz')]:
            request = {'version': '1.0', 'operation': 'assessment.update', 'timestamp': LATER,
                       'id': ASM, field: value}
            with self.subTest(field=field), self.assertRaises(ValueError):
                AUTHOR.plan(self.root, request)
        self.assertEqual(before, self.snapshot())

    def test_title_update_preserves_body_extensions_and_created_timestamp(self):
        self.execute(self.workflow())
        ref = f'.dev/workflows/{WF}/workflow.yaml'
        locator = self.load(ref); locator['custom_extension'] = {'nested': ['kept', 4]}
        self.put(ref, yaml.safe_dump(locator, sort_keys=False).encode())
        plan_path = self.root / f'.dev/workflows/{WF}/workflow-plan.md'
        prose = b'\nCustom prose, including punctuation: # | []\n'
        plan_path.write_bytes(plan_path.read_bytes() + prose)
        self.execute({'version': '1.0', 'operation': 'workflow.update', 'timestamp': LATER,
                      'id': WF, 'title': 'Changed title'})
        changed = self.load(ref)
        self.assertEqual(NOW, changed['created_at'])
        self.assertEqual({'nested': ['kept', 4]}, changed['custom_extension'])
        self.assertTrue(plan_path.read_bytes().endswith(prose))
        self.assertIn('| Changed title |', (self.root / '.dev/workflows/INDEX.MD').read_text())

    def test_comments_are_preserved_or_update_refuses_before_any_write(self):
        self.execute(self.workflow())
        ref = f'.dev/workflows/{WF}/workflow.yaml'
        path = self.root / ref
        path.write_bytes(b'# Meaningful caller comment\n' + path.read_bytes())
        before = self.snapshot()
        request = {'version': '1.0', 'operation': 'workflow.update', 'timestamp': LATER,
                   'id': WF, 'title': 'Comment preserving title'}
        try:
            self.execute(request)
        except ValueError:
            self.assertEqual(before, self.snapshot())
        else:
            self.assertIn(b'# Meaningful caller comment\n', path.read_bytes())

    def test_path_escape_and_table_injection_fail_without_output(self):
        for field, value in [('id', '../escaped'), ('title', 'bad | injected'), ('title', 'bad\nrow')]:
            request = self.workflow(); request[field] = value
            before = self.snapshot()
            with self.subTest(field=field, value=value), self.assertRaises(ValueError):
                AUTHOR.plan(self.root, request)
            self.assertEqual(before, self.snapshot())

    def test_generated_quoted_hash_values_remain_editable_in_both_families(self):
        workflow = self.workflow(); workflow['title'] = 'Discuss #316'
        assessment = self.assessment(); assessment['included'] = ['Discuss #316']
        self.execute(workflow); self.execute(assessment)
        self.execute({'version': '1.0', 'operation': 'workflow.update', 'timestamp': LATER,
                      'id': WF, 'title': 'Follow up #316'})
        self.execute({'version': '1.0', 'operation': 'assessment.finalize', 'timestamp': LATER,
                      'id': ASM, 'last_completed_action': 'Fixture observations recorded',
                      'body': '## Executive Summary\nFixture only.\n## Scope\nDiscuss #316.\n## Validation\nNo execution claimed.'})
        self.assertEqual('Follow up #316', self.load(f'.dev/workflows/{WF}/workflow.yaml')['title'])
        record = self.load(f'.dev/assessments/{ASM}/assessment.yaml')
        self.assertEqual(['Discuss #316'], record['scope']['included'])
        self.assertEqual('final', record['status'])

    def test_real_yaml_comments_refuse_updates_before_any_write(self):
        self.execute(self.workflow())
        ref = f'.dev/workflows/{WF}/workflow.yaml'
        original = (self.root / ref).read_bytes()
        for extension in ('note: value # comment\n', 'note: | # header comment\n  # literal\n',
                          'note: "# literal"# comment\n', '# last comment\n'):
            self.put(ref, original + extension.replace('\n', '\r\n').encode())
            before = self.snapshot()
            with self.subTest(extension=extension), self.assertRaisesRegex(ValueError, 'YAML comments'):
                self.execute({'version': '1.0', 'operation': 'workflow.update', 'timestamp': LATER,
                              'id': WF, 'title': 'Changed'})
            self.assertEqual(before, self.snapshot())

    def test_shared_core_drift_invalidates_preview(self):
        request = self.workflow(); preview = AUTHOR.plan(self.root, request)
        path = self.root / '.ai/scripts/artifact_core.py'
        path.write_bytes(path.read_bytes() + b'\n# changed dependency\n')
        before = self.snapshot()
        with self.assertRaisesRegex(ValueError, 'stale'):
            AUTHOR.apply(self.root, request, preview.digest)
        self.assertEqual(before, self.snapshot())

    def test_backward_update_time_is_rejected(self):
        self.execute(self.assessment())
        before = self.snapshot()
        with self.assertRaises(ValueError):
            AUTHOR.plan(self.root, {'version': '1.0', 'operation': 'assessment.update',
                                   'timestamp': '2026-09-20T21:00:00+08:00', 'id': ASM, 'title': 'Earlier'})
        self.assertEqual(before, self.snapshot())

    def test_material_update_requires_later_timestamp_for_both_families(self):
        self.execute(self.workflow())
        self.execute(self.assessment())
        before = self.snapshot()
        for kind, identifier in [('workflow', WF), ('assessment', ASM)]:
            # The same instant written with a different offset must also fail.
            for timestamp in (NOW, '2026-09-21T13:00:00+00:00'):
                request = {'version': '1.0', 'operation': kind + '.update',
                           'timestamp': timestamp, 'id': identifier, 'title': 'Changed title'}
                with self.subTest(kind=kind, timestamp=timestamp), self.assertRaisesRegex(ValueError, 'advance'):
                    self.execute(request)
                self.assertEqual(before, self.snapshot())

    def observations(self):
        return {'summary': 'Fixture inspection completed; no command execution claimed.',
                'finding_status': 'deferred', 'tests_run': ['not run: this is a synthetic observation'],
                'files_changed': [], 'residual_risk': 'Fixture evidence only', 'follow_up_needed': True}

    def transition(self, **extra):
        return {'version': '1.0', 'operation': 'workflow.transition', 'timestamp': '2026-09-21T21:10:00+08:00',
                'id': WF, 'task_id': 'TASK-001', 'status': 'completed', **extra}

    def test_task_handoff_is_coherent_and_cannot_infer_completion(self):
        self.execute(self.workflow())
        task = self.workflow()['task']; task['id'] = 'TASK-002'
        self.execute({'version': '1.0', 'operation': 'workflow.add-task', 'timestamp': LATER, 'id': WF, 'task': task})
        before = self.snapshot()
        for request in (self.transition(), self.transition(observations=self.observations())):
            with self.assertRaises(ValueError):
                AUTHOR.plan(self.root, request)
        self.assertEqual(before, self.snapshot())
        self.execute(self.transition(observations=self.observations(), next_task_id='TASK-002'))
        old = self.load(f'.dev/workflows/{WF}/tasks/TASK-001.json')
        next_task = self.load(f'.dev/workflows/{WF}/tasks/TASK-002.json')
        self.assertEqual('completed', old['status'])
        self.assertEqual(self.observations(), old['results'])
        self.assertEqual('in_progress', next_task['status'])

    def test_final_task_can_complete_workflow_but_cannot_reopen_history(self):
        self.execute(self.workflow())
        request = self.transition(observations=self.observations(), workflow_status='completed', current_phase='completed')
        self.execute(request)
        self.assertEqual('completed', self.load(f'.dev/workflows/{WF}/workflow.yaml')['status'])
        with self.assertRaises(ValueError):
            AUTHOR.plan(self.root, {'version': '1.0', 'operation': 'workflow.update', 'timestamp': LATER,
                                   'id': WF, 'current_phase': 'remediation'})

    def test_assessment_finalization_preserves_subject_and_freezes_report(self):
        self.execute(self.assessment())
        before = self.load(f'.dev/assessments/{ASM}/assessment.yaml')
        report = '## Executive Summary\nBounded fixture review.\n\n## Scope\nFixture documents.\n\n## Validation\nNot executed; synthetic test content.\n'
        self.execute({'version': '1.0', 'operation': 'assessment.finalize', 'timestamp': LATER,
                      'id': ASM, 'body': report, 'last_completed_action': 'Recorded fixture conclusions'})
        after = self.load(f'.dev/assessments/{ASM}/assessment.yaml')
        self.assertEqual(before['subject_ref'], after['subject_ref'])
        self.assertEqual(before['created_at'], after['created_at'])
        self.assertEqual('final', after['status'])
        content = (self.root / f'.dev/assessments/{ASM}/report.md').read_text()
        self.assertIn('Not executed; synthetic test content.', content)
        self.assertNotIn('passed', content)
        index = (self.root / '.dev/assessments/INDEX.MD').read_text()
        self.assertNotIn(ASM, index.split('## Final Assessments')[0])
        self.assertIn(ASM, index.split('## Final Assessments')[1])
        snapshot = self.snapshot()
        with self.assertRaises(ValueError):
            AUTHOR.plan(self.root, {'version': '1.0', 'operation': 'assessment.update', 'timestamp': LATER,
                                   'id': ASM, 'body': 'rewritten'})
        self.assertEqual(snapshot, self.snapshot())

    def test_missing_relations_are_reported_together_before_writing(self):
        request = self.assessment()
        request['workflow_refs'] = ['2026-09-21-missing-one', '2026-09-21-missing-two']
        before = self.snapshot()
        with self.assertRaises(ValueError) as raised:
            AUTHOR.plan(self.root, request)
        for name in request['workflow_refs']:
            self.assertIn(name, str(raised.exception))
        self.assertEqual(before, self.snapshot())

    def partial_apply(self):
        request = self.workflow(); preview = AUTHOR.plan(self.root, request)
        original = AUTHOR._write
        calls = []
        def fail_second(*args):
            calls.append(args)
            if len(calls) == 2:
                raise OSError('injected write interruption')
            return original(*args)
        with mock.patch.object(AUTHOR, '_write', side_effect=fail_second), self.assertRaises(ValueError):
            AUTHOR.apply(self.root, request, preview.digest)
        pending = list((self.root / AUTHOR.LOCAL).glob('*.pending.json'))
        self.assertEqual(1, len(pending))
        return pending[0], calls[0][1]

    def test_partial_write_recovery_restores_exact_before_bytes(self):
        before = self.snapshot()
        pending, _ = self.partial_apply()
        self.assertNotEqual(before, self.snapshot())
        AUTHOR.recover(self.root, pending)
        self.assertEqual(before, self.snapshot())
        self.assertFalse(pending.exists())
        self.assertEqual(1, len(list((self.root / AUTHOR.LOCAL).glob('*.recovered.json'))))

    def test_recovery_preserves_external_changes_and_rejects_extra_paths(self):
        pending, changed = self.partial_apply()
        path = self.root / changed
        path.write_bytes(path.read_bytes() + b'External modification\n')
        before = self.snapshot()
        with self.assertRaises(ValueError): AUTHOR.recover(self.root, pending)
        self.assertEqual(before, self.snapshot())
        journal = json.loads(pending.read_text()); journal['before']['.git/config'] = None
        pending.write_text(json.dumps(journal))
        with self.assertRaises(ValueError): AUTHOR.recover(self.root, pending)
        self.assertEqual(before, self.snapshot())

    def test_hardlinked_index_is_rejected_before_writing(self):
        source = self.root / '.dev/workflows/INDEX.MD'
        os.link(source, self.root / 'index-hardlink.md')
        before = self.snapshot()
        with self.assertRaises(ValueError): AUTHOR.plan(self.root, self.workflow())
        self.assertEqual(before, self.snapshot())

    def test_linked_artifact_root_is_rejected_before_writing(self):
        real = self.root / 'actual-workflows'; real.mkdir()
        link = self.root / f'.dev/workflows/{WF}'
        try:
            link.symlink_to(real, target_is_directory=True)
        except OSError as exc:
            if os.name != 'nt':
                raise
            junction = subprocess.run(['cmd', '/c', 'mklink', '/J', str(link), str(real)], capture_output=True)
            self.assertEqual(0, junction.returncode, junction.stderr.decode(errors='replace'))
        with self.assertRaises(ValueError): AUTHOR.plan(self.root, self.workflow())
        self.assertEqual([], list(real.iterdir()))

    def test_parser_preserves_json_numbers_and_rejects_duplicates_and_aliases(self):
        self.assertEqual(1e-5, AUTHOR.parse('{"value":1e-5}')['value'])
        for content in ('{"value":1,"value":2}', 'value: 1\nvalue: 2\n',
                        'value: &a [1]\nother: *a\n', '{"value":NaN}'):
            with self.subTest(content=content), self.assertRaises(ValueError): AUTHOR.parse(content)

    def test_optional_template_extension_survives_required_evolution_fails_closed(self):
        path = self.root / GOV / 'workflow-locator-template.yaml'
        original = path.read_text()
        path.write_text(original + '\noptional_extension: retained\n')
        preview = AUTHOR.plan(self.root, self.workflow())
        output = preview.changes[f'.dev/workflows/{WF}/workflow.yaml'][1]
        self.assertEqual('retained', yaml.safe_load(output)['optional_extension'])
        path.write_text(original + '\nnew_required_semantics: "<owner decision required>"\n')
        before = self.snapshot()
        with self.assertRaises(ValueError): AUTHOR.plan(self.root, self.workflow())
        self.assertEqual(before, self.snapshot())

    def test_abrupt_process_exit_retains_lock_and_can_be_recovered_after_process_stops(self):
        before = self.snapshot()
        request = self.workflow(); preview = AUTHOR.plan(self.root, request)
        program = '''import json, os, sys
from pathlib import Path
sys.path.insert(0, sys.argv[1])
import artifact_authoring as author
original = author._write
def crash_after_first_write(*args):
    original(*args)
    os._exit(73)
author._write = crash_after_first_write
author.apply(Path(sys.argv[2]), json.loads(sys.argv[3]), sys.argv[4])
'''
        result = subprocess.run([sys.executable, '-B', '-c', program, str(ROOT / '.ai/scripts'),
                                 str(self.root), json.dumps(request), preview.digest], capture_output=True)
        self.assertEqual(73, result.returncode, result.stderr.decode(errors='replace'))
        directory = self.root / AUTHOR.LOCAL
        pending = next(directory.glob('*.pending.json'))
        self.assertTrue((directory / 'writer.lock').exists())
        with self.assertRaises(ValueError): AUTHOR.recover(self.root, pending)
        # subprocess.run has confirmed this fixture's writer stopped.
        (directory / 'writer.lock').unlink()
        AUTHOR.recover(self.root, pending)
        self.assertEqual(before, self.snapshot())

    def test_portable_cli_runs_without_source_only_modules(self):
        envelope = self.root / 'package'
        payload = envelope / 'payload'
        refs = [GOV + 'workflow-locator-template.yaml', GOV + 'ai-context-maintenance-workflow-plan-template.md',
                GOV + 'ai-context-remediation-task-template.json', AUDIT, LOCATOR]
        refs += ['.ai/scripts/' + name for name in ('artifact-authoring.py', 'artifact_authoring.py', 'artifact_core.py',
                 'validate-workflow-artifacts.py', 'validate-assessment-artifacts.py',
                 'python_prerequisites.py', 'python-entrypoints.json')]
        for ref in refs:
            destination = payload / ref
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / ref, destination)
        shutil.copyfile(ROOT / 'requirements.txt', envelope / 'requirements.txt')
        cli = payload / '.ai/scripts/artifact-authoring.py'
        result = subprocess.run([sys.executable, '-B', str(cli), 'catalog'], cwd=envelope,
                                capture_output=True, text=True)
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn('workflow.create', json.loads(result.stdout)['operations'])
        request = self.root / '.dev/ai-context/local/package-request.json'
        request.parent.mkdir(parents=True, exist_ok=True)
        request.write_text(json.dumps(self.workflow()))
        result = subprocess.run([sys.executable, '-B', str(cli), '--root', str(self.root),
                                 'preview', '--request', str(request)], cwd=envelope,
                                capture_output=True, text=True)
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn('Preview digest:', result.stdout)
        self.assertFalse((self.root / f'.dev/workflows/{WF}').exists())


class RoleAuthoringTests(AuthoringFixture):
    role_path = '.ai/assets/sub-agent-role-prompts/example-role/sub-agent.yaml'
    owner_path = '.ai/assets/skills/example-owner/skill.yaml'

    def setUp(self):
        super().setUp()
        for ref in (*AUTHOR.ROLE_AUTHORITY, *('.ai/scripts/' + name for name in AUTHOR.ROLE_RUNTIME)):
            self.put(ref, (ROOT / ref).read_bytes())
        data = {'asset_id': 'example-role', 'schema_version': '1.1', 'asset_type': 'sub-agent-role-prompt',
                'title': 'Example role', 'purpose': 'Read supplied evidence', 'portability': 'repo-portable',
                'audience': 'agent-facing', 'wrapper_targets': [], 'adapter_metadata': {}, 'source_of_truth': 'canonical',
                'role_kind': 'fixture', 'triggers': ['Inspect'], 'inputs': [], 'outputs': [], 'constraints': [],
                'workflow': [{'step': 1, 'description': 'Inspect', 'owner_extension': {'keep': [2, False]}}],
                'references': [], 'examples': [], 'status': 'active', 'owner_extension': {'nested': ['keep', 42]}}
        self.save(data)
        owner = {**data, 'asset_id': 'example-owner', 'asset_type': 'skill-spec', 'schema_version': '1.0', 'wrapper_metadata': {},
                 'role_bindings': [{'role_path': self.role_path, 'role_asset_id': 'example-role', 'expected_role_status': 'active',
                                    'binding_kind': 'primary', 'applicability': 'Inspect selected evidence.', 'load_obligation': 'mandatory-when-applicable'}]}
        self.put(self.owner_path, AUTHOR.dump(owner))
        self.put('.ai/SUB-AGENT-SYSTEM.MD', b'## SAG-001 Derived Role-Binding Projection\n\n| Role Asset ID | Derived Owning Skill | Binding Kind | Canonical Applicability (Projection) |\n| --- | --- | --- | --- |\n| `example-role` | `example-owner` | `primary` | Inspect selected evidence. |\n')

    def save(self, data):
        self.put(self.role_path, AUTHOR.dump(data))

    def request(self, **changes):
        return {'version': '1.0', 'operation': 'role.update', 'id': 'example-role', 'timestamp': NOW,
                'changes': changes or {'title': 'Updated role'}}

    def migration(self):
        return {'version': '1.0', 'operation': 'role.migrate', 'id': 'example-role', 'timestamp': NOW,
                'from_version': '1.0', 'to_version': '1.1'}

    def legacy(self):
        data = self.load(self.role_path); data['schema_version'] = '1.0'; data.pop('adapter_metadata')
        self.save(data)
        return data

    def test_preview_and_update_preserve_owned_extensions_and_other_bytes(self):
        before = self.snapshot(); data = self.load(self.role_path)
        first = AUTHOR.plan(self.root, self.request())
        self.assertEqual(first.digest, AUTHOR.plan(self.root, self.request()).digest)
        self.assertEqual(before, self.snapshot())
        self.assertEqual({self.role_path}, set(first.changes))
        self.execute(self.request())
        data['title'] = 'Updated role'
        self.assertEqual(data, self.load(self.role_path))
        self.assertEqual(before[self.owner_path.replace('/', os.sep)], (self.root / self.owner_path).read_bytes())

    def test_migration_changes_only_two_fields_and_retains_exact_original(self):
        import base64
        data = self.legacy(); original = (self.root / self.role_path).read_bytes()
        errors = []
        AUTHOR._module('validate-ai-context').validate_canonical_manifest(Path(self.role_path), data, errors, root=AUTHOR.View(self.root).path())
        self.assertTrue(any('schema_version must be 1.1' in error for error in errors))
        with self.assertRaises(AUTHOR.AuthoringError): AUTHOR.plan(self.root, self.request())
        journal = self.execute(self.migration())
        expected = {**data, 'schema_version': '1.1', 'adapter_metadata': {}}
        self.assertEqual(expected, self.load(self.role_path))
        self.assertEqual(original, base64.b64decode(json.loads(journal.read_text())['before'][self.role_path]))
        with self.assertRaises(AUTHOR.AuthoringError): AUTHOR.plan(self.root, self.migration())

    def test_historical_git_pair_is_independent_mapping_oracle(self):
        # Exact blobs from a87bddf9 -> 6aed5786; fixtures do not require Git history at test time.
        fixtures = ROOT / '.ai/scripts/tests/fixtures/role-migration'
        old = yaml.safe_load((fixtures / 'dynamic-1.0.yaml').read_text())
        expected = yaml.safe_load((fixtures / 'dynamic-1.1.yaml').read_text())
        old.update(asset_id='example-role', references=[], examples=[])
        expected.update(asset_id='example-role', references=[], examples=[])
        old['owner_extension'] = expected['owner_extension'] = {'nested': [1, {'opaque': True}]}
        self.save(old)
        self.execute(self.migration())
        self.assertEqual(expected, self.load(self.role_path))

    def test_legacy_targets_versions_and_conflicting_metadata_are_not_guessed(self):
        original = self.legacy()
        for change in ({'wrapper_targets': ['codex']}, {'adapter_metadata': {'codex': {}}},
                       {'schema_version': '0.9'}, {'schema_version': '2.0'}, {'wrapper_targets': None}):
            with self.subTest(change=change):
                self.save({**original, **change}); before = self.snapshot()
                with self.assertRaises(AUTHOR.AuthoringError): AUTHOR.plan(self.root, self.migration())
                self.assertEqual(before, self.snapshot())

    def test_protected_changes_and_invalid_shape_are_refused(self):
        for change in ({'asset_id': 'other'}, {'workflow': []}, {'status': 'active'}, {'wrapper_targets': []},
                       {'schema_version': '1.1'}, {'owner_extension': {}}, {'triggers': []}, {'title': ''},
                       {'inputs': [False]}, {'references': ['.ai/missing.md']}):
            with self.subTest(change=change), self.assertRaises(AUTHOR.AuthoringError):
                AUTHOR.plan(self.root, self.request(**change))
        self.assertEqual('Example role', self.load(self.role_path)['title'])

    def test_noncanonical_authority_and_boolean_steps_block_both_operations(self):
        original = self.load(self.role_path)
        for version, request in [('1.1', self.request()), ('1.0', self.migration())]:
            for change in ({'source_of_truth': 'generated'}, {'source_of_truth': 'wrapper'},
                           {'workflow': [{'step': True, 'description': 'Invalid boolean step'}]}):
                with self.subTest(version=version, change=change):
                    self.save({**original, 'schema_version': version, **change})
                    before = (self.root / self.role_path).read_bytes()
                    with self.assertRaises(AUTHOR.AuthoringError): AUTHOR.plan(self.root, request)
                    self.assertEqual(before, (self.root / self.role_path).read_bytes())

    def test_owner_projection_and_duplicate_identity_block_writes(self):
        original = (self.root / self.owner_path).read_bytes()
        owner = self.load(self.owner_path); owner['role_bindings'] = []
        self.put(self.owner_path, AUTHOR.dump(owner))
        with self.assertRaises(AUTHOR.AuthoringError): AUTHOR.plan(self.root, self.request())
        self.put(self.owner_path, original)
        self.put('.ai/SUB-AGENT-SYSTEM.MD', b'# Missing projection\n')
        with self.assertRaises(AUTHOR.AuthoringError): AUTHOR.plan(self.root, self.request())
        self.put('.ai/assets/skills/example-owner/roles/example-role/sub-agent.yaml', (self.root / self.role_path).read_bytes())
        with self.assertRaisesRegex(AUTHOR.AuthoringError, 'exactly one'): AUTHOR.plan(self.root, self.request())

    def test_private_role_path_is_discovered_without_relocation(self):
        old = self.role_path; new = '.ai/assets/skills/example-owner/roles/example-role/sub-agent.yaml'
        self.put(new, (self.root / old).read_bytes()); (self.root / old).unlink()
        owner = self.load(self.owner_path); owner['role_bindings'][0]['role_path'] = new
        self.put(self.owner_path, AUTHOR.dump(owner))
        plan = AUTHOR.plan(self.root, self.request())
        self.assertEqual({new}, set(plan.changes))

    def test_authority_context_and_reference_drift_invalidate_preview(self):
        self.put('.ai/reference.md', b'# Reference\n')
        request = self.request(references=['.ai/reference.md'])
        for ref in (AUTHOR.ROLE_AUTHORITY[0], '.ai/scripts/ai_context_cli_routing.py', self.owner_path):
            with self.subTest(ref=ref):
                original = (self.root / ref).read_bytes(); plan = AUTHOR.plan(self.root, request)
                self.put(ref, original + b'\n')
                with self.assertRaisesRegex(AUTHOR.AuthoringError, 'stale preview'):
                    AUTHOR.apply(self.root, request, plan.digest)
                self.put(ref, original)
        plan = AUTHOR.plan(self.root, request); (self.root / '.ai/reference.md').unlink()
        with self.assertRaises(AUTHOR.AuthoringError): AUTHOR.apply(self.root, request, plan.digest)

    def test_duplicate_keys_and_comments_refuse_without_loss(self):
        original = (self.root / self.role_path).read_bytes()
        for raw in (original + b'title: duplicate\n', b'# owned explanation\n' + original):
            self.put(self.role_path, raw)
            with self.assertRaises(AUTHOR.AuthoringError): AUTHOR.plan(self.root, self.request())
            self.assertEqual(raw, (self.root / self.role_path).read_bytes())

    def test_migration_recovery_restores_original_and_refuses_external_edits(self):
        self.legacy(); original = (self.root / self.role_path).read_bytes()
        request = self.migration(); plan = AUTHOR.plan(self.root, request)
        with mock.patch.object(Path, 'rename', side_effect=OSError('simulated journal completion failure')):
            with self.assertRaises(AUTHOR.AuthoringError): AUTHOR.apply(self.root, request, plan.digest)
        journal = next((self.root / AUTHOR.LOCAL).glob('*.pending.json'))
        candidate = (self.root / self.role_path).read_bytes()
        self.put(self.role_path, candidate + b'\n')
        with self.assertRaises(AUTHOR.AuthoringError): AUTHOR.recover(self.root, journal)
        self.put(self.role_path, candidate); AUTHOR.recover(self.root, journal)
        self.assertEqual(original, (self.root / self.role_path).read_bytes())

    def test_portable_role_preview_and_catalog_import_closure(self):
        envelope = self.root / 'package'; payload = envelope / 'payload'
        refs = [GOV + 'workflow-locator-template.yaml', GOV + 'ai-context-maintenance-workflow-plan-template.md',
                GOV + 'ai-context-remediation-task-template.json', AUDIT, LOCATOR, *AUTHOR.ROLE_AUTHORITY]
        refs += ['.ai/scripts/' + name for name in ('artifact-authoring.py', 'artifact_authoring.py', 'artifact_core.py',
                 'validate-workflow-artifacts.py', 'validate-assessment-artifacts.py', 'python_prerequisites.py',
                 'python-entrypoints.json', *AUTHOR.ROLE_RUNTIME)]
        for ref in refs:
            path = payload / ref; path.parent.mkdir(parents=True, exist_ok=True); shutil.copyfile(ROOT / ref, path)
        shutil.copyfile(ROOT / 'requirements.txt', envelope / 'requirements.txt')
        cli = payload / '.ai/scripts/artifact-authoring.py'
        result = subprocess.run([sys.executable, '-B', str(cli), 'catalog'], cwd=envelope, capture_output=True, text=True)
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertEqual('convert', json.loads(result.stdout)['families']['role']['migration']['disposition'])
        request = envelope / 'request.json'; request.write_text(json.dumps(self.request()))
        result = subprocess.run([sys.executable, '-B', str(cli), '--root', str(self.root), 'preview', '--request', str(request)],
                                cwd=envelope, capture_output=True, text=True)
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn('Updated role', result.stdout)


class ReportAutomationTests(AuthoringFixture):
    report_path = f'.dev/workflows/{WF}/reports/remediation-report.md'
    history = '## Historical Evidence\nFailed review on an earlier commit; retain these exact words.\n'

    def prepare(self):
        self.execute(self.workflow())
        self.execute(self.assessment())
        self.execute({'version': '1.0', 'operation': 'assessment.finalize', 'timestamp': LATER,
                      'id': ASM, 'last_completed_action': 'Fixture baseline retained',
                      'body': '## Executive Summary\nFixture.\n## Scope\nFixture.\n## Validation\nNot executed.'})
        self.execute({'version': '1.0', 'operation': 'workflow.report', 'id': WF,
                      'baseline_assessment': ASM, 'body': self.history})

    def progress(self):
        return {'version': '1.0', 'operation': 'workflow.progress', 'id': WF, 'task_id': 'TASK-001',
                'last_completed_step': 'Observed fixture output', 'next_action': 'Review remaining evidence'}

    def test_automatic_preview_keeps_one_instant_and_refuses_unresolved_apply(self):
        request = self.workflow(); request.pop('timestamp')
        before = self.snapshot()
        with mock.patch.object(AUTHOR, 'automatic_timestamp', return_value=NOW):
            preview = AUTHOR.plan(self.root, request)
        self.assertEqual(NOW, preview.request['timestamp'])
        self.assertNotIn('timestamp', request)
        self.assertEqual(before, self.snapshot())
        with self.assertRaisesRegex(ValueError, 'resolved preview'):
            AUTHOR.apply(self.root, request, preview.digest)
        with mock.patch.object(AUTHOR, 'automatic_timestamp', side_effect=AssertionError('clock must not run again')):
            AUTHOR.apply(self.root, preview.request, preview.digest)
        self.assertEqual(NOW, self.load(f'.dev/workflows/{WF}/workflow.yaml')['updated_at'])

    def test_progress_and_body_updates_sync_report_plan_task_and_index(self):
        self.prepare()
        created = AUTHOR._report_metadata((self.root / self.report_path).read_bytes())['created_at']
        self.execute(self.progress())
        locator = self.load(f'.dev/workflows/{WF}/workflow.yaml')
        report = (self.root / self.report_path).read_text()
        metadata = AUTHOR._report_metadata(report.encode())
        self.assertEqual(created, metadata['created_at'])
        self.assertGreater(AUTHOR.instant(metadata['updated_at']), AUTHOR.instant(created))
        self.assertEqual(locator['updated_at'], metadata['updated_at'])
        self.assertEqual(locator['updated_at'], self.load(f'.dev/workflows/{WF}/tasks/TASK-001.json')['updated_at'])
        self.assertIn(locator['updated_at'], (self.root / '.dev/workflows/INDEX.MD').read_text())
        for path in (self.report_path, f'.dev/workflows/{WF}/workflow-plan.md'):
            self.assertIn('| TASK-001 | in_progress | Observed fixture output | Review remaining evidence |', (self.root / path).read_text())
        self.assertIn(self.history, report)
        self.execute({'version': '1.0', 'operation': 'workflow.report', 'id': WF, 'body': self.history + '\nAdditional actual observation.\n'})
        updated = AUTHOR._report_metadata((self.root / self.report_path).read_bytes())
        self.assertGreater(AUTHOR.instant(updated['updated_at']), AUTHOR.instant(metadata['updated_at']))
        self.assertEqual('draft', updated['status'])
        self.execute({'version': '1.0', 'operation': 'workflow.update', 'id': WF, 'body': '## Scope\nUpdated plan body.\n'})
        plan = (self.root / f'.dev/workflows/{WF}/workflow-plan.md').read_text()
        self.assertIn('Updated plan body.', plan)
        self.assertNotIn('Owner-authorized fixture scope.', plan)
        self.assertIn('Review remaining evidence', plan)

    def test_existing_report_adoption_preserves_identity_and_timestamp_origin(self):
        self.prepare()
        locator_ref = f'.dev/workflows/{WF}/workflow.yaml'
        locator = self.load(locator_ref); locator.pop('remediation_report')
        self.put(locator_ref, AUTHOR.dump(locator))
        before = AUTHOR._report_metadata((self.root / self.report_path).read_bytes())
        self.execute({'version': '1.0', 'operation': 'workflow.report', 'id': WF})
        after = AUTHOR._report_metadata((self.root / self.report_path).read_bytes())
        for key in ('report_id', 'created_at', 'baseline_assessment', 'template_source', 'template_version'):
            self.assertEqual(before[key], after[key])
        self.assertGreater(AUTHOR.instant(after['updated_at']), AUTHOR.instant(before['updated_at']))
        self.assertIn(self.history, (self.root / self.report_path).read_text())

    def test_drift_and_controlled_section_injection_refuse_all_writes(self):
        self.prepare()
        request = self.progress(); preview = AUTHOR.plan(self.root, request)
        report = self.root / self.report_path
        report.write_bytes(report.read_bytes() + b'\nExternal authored edit.\n')
        before = self.snapshot()
        with self.assertRaisesRegex(ValueError, 'stale'):
            AUTHOR.apply(self.root, preview.request, preview.digest)
        for body in ('## Report Metadata\n- `status`: `final`\n', '## Current Workflow State\nEverything passed.\n'):
            with self.subTest(body=body), self.assertRaises(ValueError):
                AUTHOR.plan(self.root, {'version': '1.0', 'operation': 'workflow.report', 'id': WF, 'body': body})
        with self.assertRaises(ValueError):
            AUTHOR.plan(self.root, {'version': '1.0', 'operation': 'workflow.report', 'id': WF, 'status': 'final'})
        self.assertEqual(before, self.snapshot())

    def test_validator_detects_stale_state_duplicate_metadata_and_missing_reference(self):
        self.prepare()
        original = (self.root / self.report_path).read_bytes()
        validator = AUTHOR._module('validate-workflow-artifacts')
        mutations = [original.replace(b'| TASK-001 | in_progress |', b'| TASK-001 | completed |'),
                     original.replace(b'- `status`: `draft`', b'- `status`: `draft`\n- `status`: `final`'),
                     original.replace(ASM.encode(), b'ASM-20260921-21-zzz'),
                     original + b'\n## Current Workflow State\nDuplicate\n']
        for data in mutations:
            self.put(self.report_path, data)
            with self.subTest(data=data[-60:]):
                self.assertTrue(validator.validate_workflows(self.root)[0])
        self.put(self.report_path, original)
        self.assertEqual([], validator.validate_workflows(self.root)[0])

    def test_completion_needs_linked_verification_and_final_report_is_immutable(self):
        self.prepare()
        observations = {'summary': 'Fixture work done; no real acceptance claimed', 'finding_status': 'deferred',
                        'tests_run': ['Synthetic fixture only'], 'files_changed': [], 'residual_risk': '', 'follow_up_needed': False}
        complete = {'version': '1.0', 'operation': 'workflow.transition', 'id': WF, 'task_id': 'TASK-001',
                    'status': 'completed', 'workflow_status': 'completed', 'current_phase': 'completed', 'observations': observations}
        before = self.snapshot()
        with self.assertRaisesRegex(ValueError, 'verification'): AUTHOR.plan(self.root, complete)
        with self.assertRaisesRegex(ValueError, 'verification'):
            AUTHOR.plan(self.root, {'version': '1.0', 'operation': 'workflow.report', 'id': WF, 'verification_assessment': ASM})
        self.assertEqual(before, self.snapshot())
        verification = self.assessment()
        verification.update(id='ASM-20260921-21-ver', type='verification', workflow_refs=[WF], related_assessments=[ASM])
        self.execute(verification)
        self.execute({'version': '1.0', 'operation': 'assessment.finalize', 'id': verification['id'],
                      'last_completed_action': 'Retained fixture result', 'body': '## Executive Summary\nFailed.\n## Scope\nFixture.\n## Validation\nSynthetic failed observation.'})
        # A final assessment records conclusions; it is deliberately not a fabricated pass.
        self.execute({'version': '1.0', 'operation': 'workflow.report', 'id': WF, 'verification_assessment': verification['id']})
        self.execute(complete)
        report = (self.root / self.report_path).read_text()
        self.assertEqual('final', AUTHOR._report_metadata(report.encode())['status'])
        self.assertNotIn('passed', report)
        before = self.snapshot()
        with self.assertRaisesRegex(ValueError, 'terminal workflow'):
            AUTHOR.plan(self.root, {'version': '1.0', 'operation': 'workflow.report', 'id': WF, 'body': 'Rewrite'})
        self.assertEqual(before, self.snapshot())

    def test_report_bundle_recovery_restores_every_previous_byte(self):
        self.prepare()
        before = self.snapshot(); candidate = AUTHOR.plan(self.root, self.progress())
        original = AUTHOR._write; calls = []
        def interrupt(*args):
            calls.append(args[1])
            if len(calls) == len(candidate.changes): raise OSError('injected final-write interruption')
            return original(*args)
        with mock.patch.object(AUTHOR, '_write', side_effect=interrupt), self.assertRaises(ValueError):
            AUTHOR.apply(self.root, candidate.request, candidate.digest)
        pending = next((self.root / AUTHOR.LOCAL).glob('*.pending.json'))
        AUTHOR.recover(self.root, pending)
        self.assertEqual(before, self.snapshot())

    def test_cli_json_preview_and_apply_never_require_manual_timestamp(self):
        request = self.workflow(); request.pop('timestamp')
        request_path = self.root / '.dev/ai-context/local/request.json'
        self.put(request_path.relative_to(self.root).as_posix(), json.dumps(request).encode())
        cli = ROOT / '.ai/scripts/artifact-authoring.py'
        run = subprocess.run([sys.executable, '-B', str(cli), '--root', str(self.root), 'preview', '--request', str(request_path), '--json'], capture_output=True, text=True)
        self.assertEqual(0, run.returncode, run.stderr)
        preview = json.loads(run.stdout)
        preview_path = request_path.with_name('preview.json'); preview_path.write_text(run.stdout, encoding='utf-8')
        apply = subprocess.run([sys.executable, '-B', str(cli), '--root', str(self.root), 'apply', '--preview', str(preview_path), '--expect', preview['digest']], capture_output=True, text=True)
        self.assertEqual(0, apply.returncode, apply.stderr)
        self.assertEqual(preview['request']['timestamp'], self.load(f'.dev/workflows/{WF}/workflow.yaml')['created_at'])

    def test_repeated_projection_preserves_following_prose_without_trailing_blank_lines(self):
        projection = '## Current Workflow State\n\n<!-- artifact-authoring: workflow-state/v1; generated from workflow.yaml and tasks -->\nRecorded state.\n'
        original = b'# Report\n\nHistorical evidence.\n'
        first = AUTHOR._replace_state(original, projection)
        self.assertEqual(first, AUTHOR._replace_state(first, projection))
        self.assertFalse(first.endswith(b'\n\n'))
        tail = b'\n## Additional Evidence\nPreserve this author-owned paragraph.\n'
        updated = AUTHOR._replace_state(first + tail, projection.replace('Recorded state.', 'New state.'))
        self.assertTrue(updated.endswith(tail))
        self.assertIn(b'Historical evidence.', updated)


if __name__ == '__main__':
    unittest.main()
