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


class AuthoringTests(unittest.TestCase):
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
                    GOV + 'ai-context-remediation-task-template.json', AUDIT, LOCATOR,
                    '.ai/scripts/validate-workflow-artifacts.py', '.ai/scripts/validate-assessment-artifacts.py',
                    '.ai/scripts/python_prerequisites.py', '.ai/scripts/python-entrypoints.json', 'requirements.txt'):
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
        return AUTHOR.apply(self.root, request, preview.digest)

    def snapshot(self):
        return {str(path.relative_to(self.root)): path.read_bytes()
                for path in self.root.rglob('*') if path.is_file()
                and '.git' not in path.relative_to(self.root).parts
                and '.dev/ai-context/local/' not in path.relative_to(self.root).as_posix()}

    def load(self, ref):
        return yaml.safe_load((self.root / ref).read_text(encoding='utf-8'))

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

    def test_backward_update_time_is_rejected(self):
        self.execute(self.assessment())
        before = self.snapshot()
        with self.assertRaises(ValueError):
            AUTHOR.plan(self.root, {'version': '1.0', 'operation': 'assessment.update',
                                   'timestamp': '2026-09-20T21:00:00+08:00', 'id': ASM, 'title': 'Earlier'})
        self.assertEqual(before, self.snapshot())

    def observations(self):
        return {'summary': 'Fixture inspection completed; no command execution claimed.',
                'finding_status': 'deferred', 'tests_run': ['not run: this is a synthetic observation'],
                'files_changed': [], 'residual_risk': 'Fixture evidence only', 'follow_up_needed': True}

    def transition(self, **extra):
        return {'version': '1.0', 'operation': 'workflow.transition', 'timestamp': LATER,
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
        refs += ['.ai/scripts/' + name for name in ('artifact-authoring.py', 'artifact_authoring.py',
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


if __name__ == '__main__':
    unittest.main()
