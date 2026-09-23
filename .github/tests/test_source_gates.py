#!/usr/bin/env python3
"""Issue #369 tests: synthetic ownership/provider/command inputs plus one tiny Git diff.
No product modules, installation, native cases, legacy validators or provider calls.
"""
from __future__ import annotations
import argparse
from contextlib import redirect_stdout
import importlib.util
import io
import json
import os
from pathlib import Path
import shutil
import stat
import sys
import tempfile
import time
import unittest
import uuid

ROOT = Path(__file__).resolve().parents[2]


def load(name, relative):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


gate = load('source_gate', '.github/scripts/check-source-change.py')
native = load('source_native', '.github/scripts/run-source-native.py')
OUTPUT_ROOT = None


class SyntheticTree:
    def __init__(self, files):
        self.files = {p: value if isinstance(value, bytes) else value.encode() for p, value in files.items()}
    def read(self, path):
        if path not in self.files:
            raise gate.GateError('synthetic missing/nonregular blob: ' + path)
        return self.files[path]
    def exists(self, path):
        return path in self.files


def synthetic_package(owner='lesson', *, tools=True):
    root = 'src/skills/' + owner
    metadata = {'metadata_version': 3, 'id': owner, 'entrypoint': 'SKILL.md',
        'dependencies': {'required': [], 'optional': []},
        'resources': {'references': ['references/use.md'], 'schemas': [{'path': 'schemas/record.json'}],
                      'templates': [{'path': 'templates/view.md'}],
                      'tools': [{'entrypoint': 'scripts/tool.py'}] if tools else []}}
    members = ['skill-package.yaml', 'SKILL.md', 'references/use.md', 'schemas/record.json', 'templates/view.md']
    if tools:
        members.append('scripts/tool.py')
    manifest = {'manifest_version': 1, 'components': [{'id': owner, 'source': root,
        'metadata': 'skill-package.yaml', 'members': [{'source': p} for p in members]}],
        'profiles': [{'id': 'tiny', 'path': 'src/profiles/tiny.yaml'}],
        'adapters': [{'id': 'codex', 'template': 'src/adapters/codex/skill-entry.md.template'}]}
    files = {root + '/' + p: '{}' if p.endswith('.json') else '# synthetic\n' for p in members}
    files[root + '/skill-package.yaml'] = json.dumps(metadata)
    files[gate.MANIFEST] = json.dumps(manifest)
    files['src/profiles/tiny.yaml'] = 'profile_version: 1\n'
    return SyntheticTree(files)


class SelectionTests(unittest.TestCase):
    def select(self, before, after, old, new):
        return gate.select([gate.Change(old, new)], before, after)

    def test_instruction_member_is_lightweight(self):
        tree = synthetic_package('code-reviewer', tools=False)
        path = 'src/skills/code-reviewer/SKILL.md'
        result = self.select(tree, tree, path, path)
        self.assertFalse(result.errors)
        self.assertEqual(result.checks, {'content', 'whitespace'})

    def test_behavior_and_template_select_exact_family(self):
        tree = synthetic_package()
        for relative in ('scripts/tool.py', 'templates/view.md', 'schemas/record.json', 'skill-package.yaml'):
            with self.subTest(relative=relative):
                path = 'src/skills/lesson/' + relative
                result = self.select(tree, tree, path, path)
                self.assertFalse(result.errors)
                self.assertEqual(result.checks, {'content', 'whitespace', 'contracts', 'public:lesson'})

    def test_rename_unions_old_and_new_families(self):
        before, after = synthetic_package(), synthetic_package('adr')
        result = self.select(before, after, 'src/skills/lesson/scripts/tool.py', 'src/skills/adr/scripts/tool.py')
        self.assertFalse(result.errors)
        self.assertEqual(result.owners, {'lesson', 'adr'})
        self.assertTrue({'public:lesson', 'public:adr'} <= result.checks)

    def test_deletion_retains_old_owner_and_command(self):
        before, after = synthetic_package(), SyntheticTree({})
        result = self.select(before, after, 'src/skills/lesson/scripts/tool.py', None)
        self.assertFalse(result.errors)
        self.assertIn('public:lesson', result.checks)

    def test_rename_to_prose_does_not_drop_behavior(self):
        result = self.select(synthetic_package(), SyntheticTree({'README.md': 'text'}),
                             'src/skills/lesson/scripts/tool.py', 'README.md')
        self.assertIn('public:lesson', result.checks)

    def test_undeclared_member_or_unknown_family_fails(self):
        for owner, path in [('lesson', 'secret.py'), ('new-family', 'scripts/tool.py')]:
            tree = synthetic_package(owner)
            full = 'src/skills/' + owner + '/' + path
            tree.files[full] = b'x'
            result = self.select(tree, tree, full, full)
            self.assertTrue(result.errors)

    def test_transitive_uncertainty_fails(self):
        tree = synthetic_package()
        meta_path = 'src/skills/lesson/skill-package.yaml'
        metadata = json.loads(tree.read(meta_path))
        metadata['dependencies']['required'] = [{'id': 'foreign', 'version': '1'}]
        tree.files[meta_path] = json.dumps(metadata).encode()
        result = self.select(tree, tree, meta_path, meta_path)
        self.assertTrue(any('transitive' in error for error in result.errors))

    def test_duplicate_or_missing_ownership_fails(self):
        tree = synthetic_package()
        manifest = json.loads(tree.read(gate.MANIFEST))
        manifest['components'] *= 2
        tree.files[gate.MANIFEST] = json.dumps(manifest).encode()
        path = 'src/skills/lesson/SKILL.md'
        self.assertTrue(self.select(tree, tree, path, path).errors)
        self.assertTrue(self.select(SyntheticTree({path: '# x'}), tree, path, path).errors)

    def test_distribution_expands_declared_consumers(self):
        tree = synthetic_package()
        result = self.select(tree, tree, gate.MANIFEST, gate.MANIFEST)
        self.assertFalse(result.errors)
        self.assertIn('public:lesson', result.checks)
        self.assertTrue(any('Lesson-only' in p for p in result.requirements))

    def test_source_policy_and_native_requirements_remain_separate(self):
        policy = '.dev/standards/SOURCE-DEVELOPMENT-POLICY.md'
        tree = SyntheticTree({policy: '# rules', 'src/distribution/installation.py': '# native'})
        result = gate.select([gate.Change(policy, policy), gate.Change(None, 'src/distribution/installation.py')], tree, tree)
        self.assertFalse(result.errors)
        self.assertIn('source-tests', result.checks)
        self.assertIn('independent-scoped-review', result.requirements)
        self.assertTrue(any(p.startswith('native-trial-required:windows') for p in result.requirements))

    def test_legacy_and_unknown_never_default_to_green_or_full_matrix(self):
        for path in ('.ai/scripts/old.py', '.dev/backlog/frozen.md', '.github/workflows/governance.yml',
                     'unknown.md', 'src/new/unknown.py'):
            with self.subTest(path=path):
                tree = SyntheticTree({path: 'x'})
                result = self.select(tree, tree, path, path)
                self.assertTrue(result.errors)
                self.assertEqual(result.checks, {'content', 'whitespace'})

    def test_parse_real_diff_shape_and_reject_incomplete(self):
        changes = gate.parse_diff(b'R100\0old.md\0new.md\0D\0gone.md\0A\0added.md\0')
        self.assertEqual(changes, [gate.Change('old.md', 'new.md'), gate.Change('gone.md', None), gate.Change(None, 'added.md')])
        for bad in (b'M\0x', b'R100\0x\0', b'U\0x\0', b'M\0../x\0', b'M\0x\nname\0'):
            with self.assertRaises(gate.GateError):
                gate.parse_diff(bad)

    def test_unsafe_full_sha_and_paths(self):
        for value in ('HEAD', 'a' * 39, 'A' * 40, '0' * 40, 'a' * 40 + ';echo x'):
            with self.assertRaises(gate.GateError):
                gate.full_sha(value)
        for value in ('../x', '/tmp/x', 'C:/x', 'x\\y', 'a//b', 'a/./b', 'x\0y', ':(glob)*'):
            with self.assertRaises(gate.GateError):
                gate.safe_path(value)


class ContentTests(unittest.TestCase):
    def test_changed_links_resolve_and_missing_links_fail(self):
        before = SyntheticTree({'README.md': '[old](historically-missing.md)'})
        after = SyntheticTree({'README.md': '[old](historically-missing.md) [new](new.md)', 'new.md': '# file'})
        gate.content_checks([gate.Change('README.md', 'README.md')], before, after)
        del after.files['new.md']
        with self.assertRaises(gate.GateError):
            gate.content_checks([gate.Change('README.md', 'README.md')], before, after)

    def test_rename_rechecks_relative_links(self):
        before = SyntheticTree({'old.md': '[doc](target.md)', 'target.md': '# target'})
        after = SyntheticTree({'dir/new.md': '[doc](target.md)', 'target.md': '# target'})
        with self.assertRaises(gate.GateError):
            gate.content_checks([gate.Change('old.md', 'dir/new.md')], before, after)

    def test_duplicates_alias_depth_and_syntax(self):
        for text in (b'a: 1\na: 2', b'a: [', ('a: ' + '[' * 65 + '0' + ']' * 65).encode()):
            with self.assertRaises(gate.GateError):
                gate.strict_yaml(text)
        self.assertEqual(gate.strict_yaml(b'a: &item [x]\nb: *item')['b'], ['x'])
        with self.assertRaises(gate.GateError):
            gate.strict_json(b'{"x":1,"x":2}')
        for path, text in [('x.py', 'def !'), ('x.json', '{'), ('x.md', '<<<<<<< conflict\n')]:
            with self.assertRaises((gate.GateError, ValueError, SyntaxError)):
                gate.content_checks([gate.Change(None, path)], SyntheticTree({}), SyntheticTree({path: text}))


class CommandTests(unittest.TestCase):
    def test_unknown_and_unbound_selected_commands_fail(self):
        for check in ('unknown', 'contracts', 'public:lesson'):
            with self.assertRaises(gate.GateError):
                gate.command_for(check)

    def test_synthetic_subprocess_outcomes_never_fake_hosted_success(self):
        path = '.github/tests/test_source_gates.py'
        tree = SyntheticTree({path: (ROOT / path).read_bytes()})
        for status in ('failed', 'skipped', 'cancelled', 'timed-out', 'unavailable', 'output-limit'):
            with self.subTest(status=status), self.assertRaises(gate.GateError):
                gate.run_selected('source-tests', ROOT, tree, launch=lambda *a, **k: gate.Outcome(status, 0))
        for receipt in ({'status': 'passed', 'tests': 0, 'skipped': 0},
                        {'status': 'passed', 'tests': 1, 'skipped': 1},
                        {'status': 'deferred', 'tests': 1, 'skipped': 0},
                        {'status': 'passed', 'tests': True, 'skipped': 0}, {}):
            with self.assertRaises(gate.GateError):
                gate.run_selected('source-tests', ROOT, tree,
                    launch=lambda *a, **k: gate.Outcome('passed', 0, json.dumps(receipt).encode()))
        receipt = gate.run_selected('source-tests', ROOT, tree,
            launch=lambda *a, **k: gate.Outcome('passed', 0, b'{"status":"passed","tests":2,"skipped":0}'))
        self.assertEqual(receipt['tests'], 2)  # Synthetic command response, not a GitHub result.

    def test_missing_or_drifted_selected_command_fails_before_launch(self):
        calls = []
        with self.assertRaises(gate.GateError):
            gate.run_selected('source-tests', ROOT, SyntheticTree({}), launch=lambda *a, **k: calls.append(a))
        with self.assertRaises(gate.GateError):
            gate.run_selected('source-tests', ROOT, SyntheticTree({'.github/tests/test_source_gates.py': '# changed'}),
                              launch=lambda *a, **k: calls.append(a))
        self.assertEqual(calls, [])

    def test_actual_bounded_child_output_and_failure(self):
        noisy = gate.bounded_run([sys.executable, '-I', '-B', '-c', 'print("x" * 20000)'], ROOT, limit=1024)
        self.assertEqual(noisy.status, 'output-limit')
        self.assertEqual(len(noisy.output), 1024)
        failed = gate.bounded_run([sys.executable, '-I', '-B', '-c', 'raise SystemExit(7)'], ROOT)
        self.assertEqual((failed.status, failed.code), ('failed', 7))


class EventTests(unittest.TestCase):
    def test_draft_and_every_selected_action_run_on_fixed_pair(self):
        for action in ('opened', 'synchronize', 'reopened', 'edited', 'ready_for_review'):
            event = {'action': action, 'pull_request': {'draft': True, 'base': {'ref': 'main', 'sha': 'a' * 40},
                                                       'head': {'sha': 'b' * 40}}}
            gate.validate_event(event, 'pull_request', 'a' * 40, 'b' * 40)
            with self.assertRaises(gate.GateError):
                gate.validate_event(event, 'pull_request', 'c' * 40, 'b' * 40)
        for event_name in ('pull_request_target', 'push', 'merge_group', 'workflow_dispatch'):
            with self.assertRaises(gate.GateError):
                gate.validate_event(event, event_name, 'a' * 40, 'b' * 40)

    def test_workflow_context_is_unconditional_and_credential_free(self):
        document = gate.strict_yaml((ROOT / '.github/workflows/source-checks.yml').read_bytes())
        events = document.get('on', document.get(True))  # GitHub uses YAML 1.2; SafeLoader recognizes YAML 1.1 on.
        self.assertEqual(set(events), {'pull_request'})
        self.assertEqual(events['pull_request']['branches'], ['main'])
        self.assertEqual(set(events['pull_request']['types']), {'opened', 'synchronize', 'reopened', 'edited', 'ready_for_review'})
        self.assertFalse({'paths', 'paths-ignore'} & events['pull_request'].keys())
        self.assertEqual(document['permissions'], {})
        self.assertEqual(set(document['jobs']), {'source-change'})
        job = document['jobs']['source-change']
        self.assertEqual(job['name'], 'Source change gate')
        self.assertEqual(job['permissions'], {'contents': 'read'})
        self.assertNotIn('if', job)
        self.assertNotIn('environment', job)
        self.assertNotIn('strategy', job)
        self.assertEqual(job['timeout-minutes'], 10)
        self.assertTrue(document['concurrency']['cancel-in-progress'])
        self.assertEqual(job['env']['SOURCE_BASE'], '${{ github.event.pull_request.base.sha }}')
        self.assertEqual(job['env']['SOURCE_HEAD'], '${{ github.event.pull_request.head.sha }}')
        self.assertEqual(job['steps'][-1]['if'], 'always()')
        for step in job['steps']:
            self.assertNotIn('continue-on-error', step)
            if 'uses' in step:
                self.assertRegex(step['uses'], r'^actions/(checkout|setup-python)@[0-9a-f]{40}$')
            if step.get('uses', '').startswith('actions/checkout@'):
                self.assertIs(step['with']['persist-credentials'], False)
                self.assertEqual(step['with']['fetch-depth'], 1)
                self.assertEqual(step['with']['ref'], '${{ github.event.pull_request.head.sha }}')
            if 'run' in step:
                self.assertNotIn('${{', step['run'])
                self.assertNotIn('|| true', step['run'])
                self.assertNotIn('secrets.', step['run'])

    def test_native_is_manual_windows_main_and_unbound(self):
        document = gate.strict_yaml((ROOT / '.github/workflows/source-native.yml').read_bytes())
        self.assertEqual(set(document.get('on', document.get(True))), {'workflow_dispatch'})
        job = document['jobs']['native']
        self.assertEqual(job['name'], 'Source native trial')
        self.assertEqual(job['runs-on'], 'windows-latest')
        self.assertEqual(job['permissions'], {'contents': 'read'})
        self.assertFalse(document['concurrency']['cancel-in-progress'])
        self.assertNotIn('if', job)
        self.assertIn('refs/heads/main', job['steps'][0]['run'])
        self.assertEqual(job['steps'][-1]['if'], 'always()')
        self.assertTrue(native.decision('a' * 40, 'Windows', 'workflow_dispatch', 'refs/heads/main').startswith('native-binding-pending'))
        self.assertEqual(native.decision('HEAD', 'Windows'), 'invalid-subject')
        self.assertEqual(native.decision('a' * 40, 'Linux'), 'unsupported-platform:Windows-only')
        self.assertEqual(native.decision('a' * 40, 'Windows', 'workflow_dispatch', 'refs/heads/topic'), 'requires-manual-main-workflow')
        stream = io.StringIO()
        with redirect_stdout(stream):
            code = native.main(['--subject', 'a' * 40])
        self.assertEqual(code, 1)
        result = json.loads(stream.getvalue())
        self.assertEqual(result['status'], 'blocked')
        self.assertIs(result['native_executed'], False)


def fresh_fixture():
    parent = Path(OUTPUT_ROOT or tempfile.gettempdir()).absolute()
    if not parent.is_dir():
        raise gate.GateError('explicit source-test output parent must already exist')
    for part in [parent, *parent.parents]:
        if part.is_symlink() or (hasattr(part, 'is_junction') and part.is_junction()):
            raise gate.GateError('linked source-test output parent')
    # The assigned RAM disk rejects Windows final-path resolution (WinError 1).
    # For disposable source-test fixtures, validate the lexical absolute path
    # by lstat of every existing ancestor; do not resolve or reroute elsewhere.
    for part in [parent, *parent.parents]:
        info = part.lstat()
        if not stat.S_ISDIR(info.st_mode) or getattr(info, "st_file_attributes", 0) & 0x400:
            raise gate.GateError("non-directory/reparse source-test ancestor")
    run = parent / ('source-gates-' + uuid.uuid4().hex)
    run.mkdir()
    return parent, run


class RealGitTests(unittest.TestCase):
    def test_two_commit_fixture_rename_delete_and_cli_event_pair(self):
        parent, run = fresh_fixture()
        def git(*args):
            result = gate.bounded_run(['git', '-c', 'core.autocrlf=false', '-c', 'core.hooksPath=/dev/null', *args], run)
            if result.status != 'passed':
                self.fail('tiny Git fixture command failed: ' + args[0])
            return result.output.decode().strip()
        try:
            git('init', '--quiet')
            (run / 'README.md').write_text('# same\n', encoding='utf-8')
            (run / 'README.en.md').write_text('# remove\n', encoding='utf-8')
            git('add', '--', 'README.md', 'README.en.md')
            git('-c', 'user.name=Source gate fixture', '-c', 'user.email=fixture@example.invalid',
                '-c', 'commit.gpgsign=false', 'commit', '--quiet', '-m', 'synthetic base')
            base = git('rev-parse', 'HEAD')
            target = run / '.dev/design/framework-next/renamed.md'
            target.parent.mkdir(parents=True)
            (run / 'README.md').rename(target)
            (run / 'README.en.md').unlink()
            git('add', '-A')
            git('-c', 'user.name=Source gate fixture', '-c', 'user.email=fixture@example.invalid',
                '-c', 'commit.gpgsign=false', 'commit', '--quiet', '-m', 'synthetic head')
            head = git('rev-parse', 'HEAD')
            before, after = gate.GitTree(run, base), gate.GitTree(run, head)
            changes = gate.parse_diff(after.git('diff', '--name-status', '-z', '-M', base, head, '--'))
            self.assertEqual(len(changes), 2)
            self.assertTrue(any(c.before == 'README.md' and c.after == '.dev/design/framework-next/renamed.md' for c in changes))
            selection = gate.select(changes, before, after)
            self.assertFalse(selection.errors)
            self.assertEqual(selection.checks, {'content', 'whitespace'})
            gate.content_checks(changes, before, after)
            after.git('diff', '--check', base, head, '--')
            with self.assertRaises(gate.GateError):
                gate.GitTree(run, 'e' * 40)
        finally:
            # Only this freshly created exact child; never delete a supplied parent.
            if run.parent != parent or not run.name.startswith('source-gates-') or run.is_symlink():
                raise gate.GateError('fixture cleanup containment failure')
            def clear_readonly(function, path, error):
                selected = Path(path).absolute()
                if not selected.is_relative_to(run) or selected.is_symlink():
                    raise gate.GateError("cleanup path escaped fixture")
                selected.chmod(stat.S_IWRITE | stat.S_IREAD)
                function(path)
            shutil.rmtree(run, onerror=clear_readonly)


def main():
    global OUTPUT_ROOT
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-root')
    parser.add_argument('--json', action='store_true')
    args = parser.parse_args()
    OUTPUT_ROOT = args.output_root or os.environ.get('FRAMEWORK_TEST_OUTPUT_ROOT')
    started = time.monotonic()
    suite = unittest.defaultTestLoader.loadTestsFromModule(sys.modules[__name__])
    diagnostics = io.StringIO()
    result = unittest.TextTestRunner(stream=diagnostics, verbosity=2).run(suite)
    passed = result.wasSuccessful() and result.testsRun > 0 and not result.skipped
    receipt = {'status': 'passed' if passed else 'failed', 'tests': result.testsRun, 'skipped': len(result.skipped),
               'failures': len(result.failures), 'errors': len(result.errors),
               'duration_seconds': round(time.monotonic() - started, 3),
               'evidence': 'local selector/event contracts; synthetic ownership/command/provider inputs; tiny real Git diff; no hosted/product/native result'}
    if args.json:
        print(json.dumps(receipt, sort_keys=True))
        if not passed:
            print(diagnostics.getvalue()[-32768:], file=sys.stderr)
    else:
        print(diagnostics.getvalue()[-32768:])
        print(json.dumps(receipt, sort_keys=True))
    return 0 if passed else 1


if __name__ == '__main__':
    raise SystemExit(main())
