#!/usr/bin/env python3
"""Issue #369 tests: synthetic ownership/provider/command inputs plus one tiny Git diff.
No product modules, installation, native cases, legacy validators or provider calls.
"""
from __future__ import annotations
import argparse
from contextlib import redirect_stdout
from copy import deepcopy
from unittest.mock import patch
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

    def test_public_modules_select_their_actual_shared_consumers(self):
        all_families = {'lesson', 'adr', 'standards-promotion', 'pr', 'local-backlog',
                        'software-development-orchestrator', 'problem-frame-author'}
        expected = {'test_knowledge.py': all_families,
                    'test_work.py': {'pr', 'local-backlog', 'software-development-orchestrator'},
                    'test_cbf.py': {'problem-frame-author'}}
        for name, families in expected.items():
            path = 'tests/framework_next/' + name
            tree = SyntheticTree({path: '# synthetic module'})
            with self.subTest(path=path):
                result = self.select(tree, tree, path, path)
                self.assertFalse(result.errors)
                self.assertEqual(result.checks, {'content', 'whitespace'} | {'public:' + f for f in families})
                self.assertEqual(result.owners, families | {'new-public-tests'})
                self.assertFalse(result.requirements)

    def test_versioned_builder_selects_declared_consumers_and_separate_trial(self):
        path = 'tools/build-candidate.py'
        tree = synthetic_package()
        tree.files[path] = b'# synthetic versioned builder'
        result = self.select(tree, tree, path, path)
        self.assertFalse(result.errors)
        self.assertEqual(result.checks, {'content', 'whitespace', 'contracts', 'public:lesson'})
        self.assertEqual(result.owners, {'distribution'})
        self.assertIn('versioned-candidate-trial-required:affected-selections', result.requirements)
        self.assertIn('distribution-trial-required:affected-selections;contracts-build-Lesson-only', result.requirements)

    def test_named_regressions_have_owners_but_no_automatic_dispatch(self):
        expected = {'test_engine_source.py': 'engine-source-regressions:#371',
                    'test_installation_scan_budget.py': 'installation-scan-budget-regressions:#386',
                    'test_pr_git_worktree.py': 'pr-git-worktree-regressions:#335',
                    'test_protected_paths.py': 'protected-path-regressions:#383',
                    'test_versioned_candidates.py': 'versioned-candidate-regressions:#381',
                    'test_windows_paths.py': 'windows-path-regressions:#378'}
        for name, owner in expected.items():
            path = 'tests/framework_next/' + name
            tree = SyntheticTree({path: '# synthetic regression'})
            with self.subTest(path=path):
                result = self.select(tree, tree, path, path)
                self.assertFalse(result.errors)
                self.assertEqual(result.checks, {'content', 'whitespace'})
                self.assertEqual(result.owners, {owner})
                self.assertEqual(result.requirements, {'owner-selected-regression-required:' + path})
                with self.assertRaises(gate.GateError):
                    gate.command_for('regression:' + name)

    def test_native_driver_remains_separate_and_unbound(self):
        path = 'tests/framework_next/test_native_windows.py'
        tree = SyntheticTree({path: '# synthetic native driver'})
        result = self.select(tree, tree, path, path)
        self.assertFalse(result.errors)
        self.assertEqual(result.checks, {'content', 'whitespace'})
        self.assertEqual(result.owners, {'native-test-driver:#382'})
        self.assertEqual(result.requirements, {'native-trial-required:windows:V3-binding-pending',
                                               'independent-scoped-review'})
        with self.assertRaises(gate.GateError):
            gate.command_for('native-windows')

    def test_new_module_rename_and_deletion_keep_both_owners(self):
        old, new = 'tests/framework_next/test_work.py', 'tests/framework_next/test_cbf.py'
        result = self.select(SyntheticTree({old: '# old'}), SyntheticTree({new: '# new'}), old, new)
        self.assertFalse(result.errors)
        self.assertEqual(result.checks, {'content', 'whitespace', 'public:pr', 'public:local-backlog',
                                        'public:software-development-orchestrator', 'public:problem-frame-author'})
        for path, requirement in (
                ('tests/framework_next/test_native_windows.py', 'native-trial-required:windows:V3-binding-pending'),
                ('tests/framework_next/test_pr_git_worktree.py',
                 'owner-selected-regression-required:tests/framework_next/test_pr_git_worktree.py')):
            result = self.select(SyntheticTree({path: '# old'}), SyntheticTree({}), path, None)
            self.assertFalse(result.errors)
            self.assertIn(requirement, result.requirements)
            self.assertEqual(result.checks, {'content', 'whitespace'})

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
                     'unknown.md', 'src/new/unknown.py', 'tests/framework_next/test_future.py',
                     'tests/framework_next/test_native_linux.py', 'tests/framework_next/test_pr_git_worktree_extra.py',
                     'tools/build-candidate-extra.py'):
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
    def test_real_contract_argv_and_reserved_or_unknown_commands(self):
        self.assertEqual(gate.command_for('contracts'),
                         [sys.executable, '-I', '-B', 'tests/framework_next/run.py', '--layer', 'contracts'])
        for check in ('unknown', 'public:unknown', 'native-windows'):
            with self.assertRaises(gate.GateError):
                gate.command_for(check)

    @staticmethod
    def synthetic_contract_output(summary='Ran 2 tests in 0.003s\n\nOK', *, residue=None):
        # Hypothetical success in the *observed interface*, never product execution.
        runtime = {'python': '3.12.0', 'executable': 'synthetic-python', 'PyYAML': '6.0.3',
                   'jsonschema': '4.26.0', 'referencing': '0.37.0'}
        accounting = {'observed_files': 2, 'process_total': 0, 'residue': residue, 'next_action': None,
                      'measurement_phase': 'before-cleanup'}
        return (json.dumps({'runtime': runtime}) + '\n' +
                'test_synthetic (SyntheticTests.test_synthetic) ... ok\n' + summary + '\n' +
                json.dumps({'synthetic_probe': {'meaning': 'command parser test only'}}) + '\n' +
                json.dumps({'fixture_accounting': accounting}) + '\n').encode()

    def test_contract_success_uses_unittest_and_observations(self):
        for output in (self.synthetic_contract_output(), self.synthetic_contract_output().replace(b'\n', b'\r\n')):
            result = gate.command_result('contracts', gate.Outcome('passed', 0, output))
            self.assertEqual((result['tests'], result['skipped']), (2, 0))
            self.assertEqual(result['result_interface'], 'unittest-and-observations')
            self.assertEqual(result['interface_source_commit'], 'e71712b71791170c3f4946e131ce867f82dade8f')
        with self.assertRaises(gate.GateError):
            gate.command_result('contracts', gate.Outcome('passed', 0, b'{"status":"passed","tests":2,"skipped":0}'))

    def test_contract_nonzero_or_error_observation_cannot_pass(self):
        for code in (1, 2, 7):
            with self.assertRaisesRegex(gate.GateError, 'exit=' + str(code)):
                gate.command_result('contracts', gate.Outcome('failed', code, self.synthetic_contract_output()))
        for status in ('skipped', 'cancelled', 'timed-out', 'unavailable', 'output-limit'):
            with self.assertRaises(gate.GateError):
                gate.command_result('contracts', gate.Outcome(status, 0, self.synthetic_contract_output()))
        for output in (self.synthetic_contract_output(residue='synthetic-retained-root'),
                       self.synthetic_contract_output() + b'{"outcome":"cleanup-failed"}\n',
                       self.synthetic_contract_output() + b'{"outcome":"unavailable-or-failed"}\n'):
            with self.assertRaises(gate.GateError):
                gate.command_result('contracts', gate.Outcome('passed', 0, output))

    def test_contract_cleanup_failure_retains_accounting_without_admission(self):
        # Integrated runner emits pre-cleanup accounting even after partial deletion.
        observed = self.synthetic_contract_output(residue='synthetic-partly-deleted-run')
        error = json.dumps({'outcome': 'cleanup-failed', 'residue': 'synthetic-partly-deleted-run',
                            'diagnostic': 'Synthetic cleanup refusal', 'next_action': 'Inspect residue; no retry.'}).encode() + b'\n'
        for status, code, output in [('failed', 2, observed + error),
                                     ('passed', 0, observed + error), ('passed', 0, observed)]:
            with self.subTest(status=status, code=code), self.assertRaises(gate.GateError):
                gate.command_result('contracts', gate.Outcome(status, code, output))

    def test_contract_skipped_missing_or_malformed_output_fails(self):
        for summary in ('', 'Ran 0 tests in 0.001s\n\nOK', 'Ran 2 tests in 0.003s\n\nOK (skipped=1)',
                        'Ran 14 tests in 3.483s\n\nFAILED (errors=7)',
                        'Ran 2 tests in 0.003s\n\nOK\nRan 2 tests in 0.003s\n\nOK'):
            with self.assertRaises(gate.GateError):
                gate.command_result('contracts', gate.Outcome('passed', 0, self.synthetic_contract_output(summary)))
        output = self.synthetic_contract_output()
        malformed = [b'', output.replace(b'"runtime"', b'"wrong"'),
                     output.replace(b'"fixture_accounting"', b'"wrong"'), output + b'{bad json}\n',
                     output + b'{"runtime":{}}\n', output + b'{"fixture_accounting":{}}\n',
                     output.replace(b'"process_total": 0', b'"process_total": true'),
                     output.replace(b'"next_action": null', b'"next_action": "inspect residue"'),
                     output.replace(b'"observed_files": 2', b'"observed_files": -1'),
                     output + b'\xff', output + b'ERROR: synthetic contradictory result\n']
        for value in malformed:
            with self.subTest(output=value[:60]), self.assertRaises(gate.GateError):
                gate.command_result('contracts', gate.Outcome('passed', 0, value))

    def test_contract_missing_pinned_runner_fails_before_launch(self):
        calls = []
        with self.assertRaises(gate.GateError):
            gate.run_selected('contracts', ROOT, SyntheticTree({}), launch=lambda *a, **k: calls.append(a))
        self.assertEqual(calls, [])

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


class PublicResultTests(unittest.TestCase):
    """Every public response here is synthetic; no public operation is launched."""
    subject = 'a' * 40
    stderr = b'test_selected (SyntheticTests.test_selected) ... ok\n\n----------------------------------------------------------------------\nRan 1 test in 0.123s\n\nOK\n'

    @staticmethod
    def balance(entry):
        count = len(entry['calls'])
        entry['public_launches'] = count
        entry['fixture_accounting']['processes'] = {'git': 4, 'python': count, 'other': 0}
        entry['fixture_accounting']['process_total'] = count + 4

    def synthetic_rows(self, family='adr'):
        # Protocol-shaped hypothetical complete observations, not recorded execution.
        phases = list(gate.PUBLIC_PHASES[family])
        calls = []
        for phase in phases:
            if phase == 'T4-synthetic-provider':  # Actual runner uses in-process fake transport.
                continue
            if phase == 'C6-input-boundary':
                calls.append({'operation': 'oversize-request', 'phase': phase, 'exit': 1, 'outcome': 'unsupported',
                              'stdin_bytes': 4 * 1024 * 1024 + 1, 'stdin_sha256': 'b' * 64,
                              'stdout_sha256': 'c' * 64, 'diagnostics': [{'code': 'size-limit'}]})
            else:
                calls.append({'operation': 'explain', 'phase': phase, 'expected': 'success', 'exit': 0,
                              'stdout_sha256': 'b' * 64, 'stderr_sha256': 'c' * 64,
                              'outcome': 'ok' if family == 'problem-frame-author' else 'succeeded', 'diagnostics': []})
        entry = {'family': family, 'outcome': 'passed', 'exit': 0, 'source_commit': self.subject,
                 'fixture_kind': 'direct-committed-package-resources', 'completed_phases': phases,
                 'failed_phase': None, 'blocked_before_write': False, 'unexecuted_phases': [],
                 'public_launches': len(calls), 'calls': calls,
                 'nested_child_launches': 'unavailable: unchanged public children are not instrumented',
                 'nested_launch_upper_bound': 0, 'boundary_authored_bytes': 4 * 1024 * 1024 + 1 if family == 'lesson' else 0,
                 'transcript': 'synthetic-transcript-never-executed.jsonl',
                 'fixture_accounting': {'observed_files': 8, 'observed_logical_bytes': 1000,
                     'retained_files': 8, 'retained_bytes': 1000, 'authored_bytes': 100,
                     'processes': {}, 'process_total': 0, 'wall_seconds': 0.123, 'residue': None, 'next_action': None}}
        self.balance(entry)
        return [{'runtime': {'python': '3.12.0', 'executable': 'synthetic-python', 'PyYAML': '6.0.3',
                             'jsonschema': '4.26.0', 'referencing': '0.37.0'}},
                {'public_family': entry},
                {'public_selection': [family], 'outcome': 'passed', 'exit': 0, 'unexecuted_families': []}]

    @staticmethod
    def stdout(rows):
        return ('\n'.join(json.dumps(row, sort_keys=True) for row in rows) + '\n').encode()

    def result(self, rows, *, family='adr', subject=None, stderr=None):
        return gate.command_result('public:' + family,
            gate.Outcome('passed', 0, self.stdout(rows), self.stderr if stderr is None else stderr),
            subject=self.subject if subject is None else subject)

    def test_all_seven_exact_commands_and_synthetic_complete_formats(self):
        self.assertEqual(set(gate.PUBLIC_PHASES), gate.FAMILIES)
        for family in sorted(gate.FAMILIES):
            with self.subTest(family=family):
                argv = gate.command_for('public:' + family)
                self.assertEqual(argv, [sys.executable, '-I', '-B', gate.RUNNER, '--layer', 'public', '--family', family])
                self.assertNotIn('--public-read-only', argv)
                self.assertNotIn('--case', argv)
                result = self.result(self.synthetic_rows(family), family=family)
                self.assertEqual((result['family'], result['source_commit'], result['tests'], result['skipped']),
                                 (family, self.subject, 1, 0))
                self.assertEqual(result['interface_source_commit'], 'e71712b71791170c3f4946e131ce867f82dade8f')
                self.result(self.synthetic_rows(family), family=family, stderr=self.stderr.replace(b'\n', b'\r\n'))

    def test_subject_family_selection_and_complete_phases_must_match(self):
        changes = [((2, 'public_selection'), ['lesson']), ((2, 'public_selection'), ['adr', 'lesson']),
                   ((2, 'unexecuted_families'), ['lesson']), ((2, 'outcome'), 'not-passed'), ((2, 'exit'), False),
                   ((1, 'public_family', 'family'), 'lesson'), ((1, 'public_family', 'source_commit'), 'b' * 40),
                   ((1, 'public_family', 'outcome'), 'partial'), ((1, 'public_family', 'outcome'), 'failed'),
                   ((1, 'public_family', 'exit'), 1), ((1, 'public_family', 'exit'), 0.0),
                   ((1, 'public_family', 'failed_phase'), 'T2-round-trip'),
                   ((1, 'public_family', 'blocked_before_write'), True),
                   ((1, 'public_family', 'blocked_before_write'), 0),
                   ((1, 'public_family', 'unexecuted_phases'), ['T2-round-trip']),
                   ((1, 'public_family', 'completed_phases'), ['resource-setup', 'C4-config', 'C6-binding']),
                   ((1, 'public_family', 'completed_phases'), list(reversed(gate.PUBLIC_PHASES['adr']))),
                   ((1, 'public_family', 'completed_phases'), gate.PUBLIC_PHASES['adr'] + ['T2-decision-derive']),
                   ((1, 'public_family', 'current'), 'T2-round-trip')]
        for path, value in changes:
            rows = self.synthetic_rows()
            parent = rows
            for key in path[:-1]: parent = parent[key]
            parent[path[-1]] = value
            with self.subTest(path=path, value=value), self.assertRaises(gate.GateError):
                self.result(rows)
        for subject in ('HEAD', 'b' * 40, '0' * 40):
            with self.assertRaises(gate.GateError): self.result(self.synthetic_rows(), subject=subject)
        with self.assertRaises(gate.GateError):
            gate.command_result('public:adr', gate.Outcome('passed', 0, self.stdout(self.synthetic_rows()), self.stderr))

    def test_missing_duplicate_malformed_or_reordered_observations_fail(self):
        original = self.synthetic_rows()
        outputs = [b'', b'not JSON\n', b'{"status":"passed"}\n', self.stdout(original[:2]),
                   self.stdout(original + [original[1]]), self.stdout([original[0], original[2], original[1]]),
                   self.stdout(original) + b'\xff', self.stdout(original).replace(b'"exit": 0', b'"exit": 0, "exit": 0', 1)]
        for output in outputs:
            with self.subTest(output=output[:50]), self.assertRaises(gate.GateError):
                gate.command_result('public:adr', gate.Outcome('passed', 0, output, self.stderr), subject=self.subject)
        for index, keys in ((0, ['runtime']), (1, ['public_family']), (2, list(original[2]))):
            for key in keys:
                rows = deepcopy(original)
                del rows[index][key]
                with self.assertRaises(gate.GateError): self.result(rows)
        for key in ('family', 'outcome', 'exit', 'source_commit', 'fixture_kind', 'completed_phases',
                    'failed_phase', 'blocked_before_write', 'unexecuted_phases', 'public_launches', 'calls', 'fixture_accounting'):
            rows = deepcopy(original)
            del rows[1]['public_family'][key]
            with self.subTest(missing_family_key=key), self.assertRaises(gate.GateError): self.result(rows)

    def test_nonzero_partial_skip_and_error_stderr_never_pass(self):
        output = self.stdout(self.synthetic_rows())
        for status, code in [('failed', 1), ('failed', 2), ('failed', 7), ('passed', False),
                             ('skipped', 0), ('timed-out', None), ('unavailable', None), ('output-limit', 0)]:
            with self.assertRaises(gate.GateError):
                gate.command_result('public:adr', gate.Outcome(status, code, output, self.stderr), subject=self.subject)
        for detail in (b'', self.stderr.replace(b'Ran 1 test', b'Ran 0 tests'),
                       self.stderr.replace(b'OK\n', b'OK (skipped=1)\n'),
                       self.stderr.replace(b'OK\n', b'FAILED (errors=1)\n'), self.stderr * 2,
                       self.stderr + b'ERROR: contradictory error\n',
                       self.stderr + b'{"outcome":"cleanup-failed"}\n',
                       self.stderr + b'Traceback (most recent call last):\n', self.stderr + b'\xff'):
            with self.assertRaises(gate.GateError): self.result(self.synthetic_rows(), stderr=detail)

    def test_cleanup_and_accounting_must_be_successful_and_consistent(self):
        values = {'residue': 'synthetic-retained-run', 'next_action': 'inspect residue', 'observed_files': False,
                  'retained_files': 99, 'retained_bytes': 1001, 'process_total': 0,
                  'processes': {'git': 4, 'python': True, 'other': 0}, 'wall_seconds': float('inf')}
        for key, value in values.items():
            rows = self.synthetic_rows()
            rows[1]['public_family']['fixture_accounting'][key] = value
            with self.subTest(key=key), self.assertRaises(gate.GateError): self.result(rows)
        for key in set(self.synthetic_rows()[1]['public_family']['fixture_accounting']) - {'authored_bytes'}:
            rows = self.synthetic_rows()
            del rows[1]['public_family']['fixture_accounting'][key]
            with self.assertRaises(gate.GateError): self.result(rows)
        for key, value in {'public_launches': 0, 'calls': None}.items():
            rows = self.synthetic_rows()
            rows[1]['public_family'][key] = value
            with self.assertRaises(gate.GateError): self.result(rows)

    def test_public_cleanup_failure_with_complete_phases_is_not_success(self):
        rows = self.synthetic_rows()
        entry = rows[1]['public_family']
        accounting = entry['fixture_accounting']
        accounting['measurement_phase'] = 'before-cleanup'
        self.result(rows)  # The added observation is also emitted on successful cleanup.
        accounting.update(residue='synthetic-partly-deleted-run', next_action='Inspect residue; no retry.')
        entry.update(outcome='cleanup-failed', exit=2, residue='synthetic-partly-deleted-run',
                     exception_type='FixtureCleanupError', diagnostic='Synthetic cleanup refusal',
                     next_action='Inspect residue; no retry.')
        rows[2].update(outcome='not-passed', exit=2)
        with self.assertRaises(gate.GateError):
            gate.command_result('public:adr', gate.Outcome('failed', 2, self.stdout(rows), self.stderr), subject=self.subject)
        with self.assertRaises(gate.GateError):
            self.result(rows)  # A forged zero process exit cannot overrule cleanup evidence.
        rows[2].update(outcome='passed', exit=0)
        with self.assertRaises(gate.GateError):
            self.result(rows)  # Neither a complete phase list nor final success hides failure.

    def test_call_counts_and_required_observation_shape(self):
        for key, value in {'exit': False, 'outcome': None, 'operation': '', 'phase': 'unknown'}.items():
            rows = self.synthetic_rows()
            rows[1]['public_family']['calls'][0][key] = value
            with self.subTest(key=key), self.assertRaises(gate.GateError): self.result(rows)
        for key in ('operation', 'phase', 'exit', 'outcome'):
            rows = self.synthetic_rows()
            del rows[1]['public_family']['calls'][0][key]
            with self.assertRaises(gate.GateError): self.result(rows)
        rows = self.synthetic_rows()
        rows[1]['public_family']['calls'].pop()
        with self.assertRaises(gate.GateError): self.result(rows)  # Reported launch count no longer matches.
        rows = self.synthetic_rows()
        rows[1]['public_family']['calls'] = []
        self.balance(rows[1]['public_family'])
        with self.assertRaises(gate.GateError): self.result(rows)

    def test_negative_child_exits_are_owned_by_the_actual_runner(self):
        # The caller must not rebuild the public operation/response protocol matrix.
        for family, outcome, code in [('adr', 'conflict', 1), ('problem-frame-author', 'unsupported-version', 2),
                                       ('problem-frame-author', 'conflict', 3), ('problem-frame-author', 'unavailable', 4)]:
            rows = self.synthetic_rows(family)
            entry = rows[1]['public_family']
            negative = {**entry['calls'][-1], 'expected': [outcome, 'invalid-input'], 'outcome': outcome, 'exit': code}
            entry['calls'].append(negative)
            self.balance(entry)
            self.result(rows, family=family)
        self.result(self.synthetic_rows('lesson'), family='lesson')

    def test_pinned_entry_and_head_are_forwarded_without_product_launch(self):
        path = '.github/tests/test_source_gates.py'
        tree = SyntheticTree({path: (ROOT / path).read_bytes()})
        tree.revision = self.subject
        calls = []
        def synthetic_launch(argv, root, **options):
            calls.append((argv, options))
            return gate.Outcome('passed', 0, self.stdout(self.synthetic_rows()), self.stderr)
        # Only route the existence check to our own file; no upstream file is copied/imported.
        with patch.object(gate, 'command_for', return_value=[sys.executable, '-I', '-B', path]):
            result = gate.run_selected('public:adr', ROOT, tree, launch=synthetic_launch)
            self.assertEqual(result['source_commit'], self.subject)
            self.assertTrue(calls[0][1]['separate_streams'])
            tree.revision = 'b' * 40
            with self.assertRaises(gate.GateError): gate.run_selected('public:adr', ROOT, tree, launch=synthetic_launch)
        launches = []
        with self.assertRaises(gate.GateError):
            gate.run_selected('public:adr', ROOT, SyntheticTree({}), launch=lambda *a, **k: launches.append(a))
        self.assertEqual(launches, [])

    def test_actual_capture_separates_streams_under_one_total_bound(self):
        result = gate.bounded_run([sys.executable, '-I', '-B', '-c',
            'import sys; print("synthetic stdout"); print("synthetic stderr", file=sys.stderr)'], ROOT, separate_streams=True)
        self.assertEqual(result.status, 'passed')
        self.assertEqual(result.output.strip(), b'synthetic stdout')
        self.assertEqual(result.stderr.strip(), b'synthetic stderr')
        result = gate.bounded_run([sys.executable, '-I', '-B', '-c',
            'import sys; print("x"*20000); print("y"*20000, file=sys.stderr)'], ROOT, limit=1024, separate_streams=True)
        self.assertEqual(result.status, 'output-limit')
        self.assertEqual(len(result.output) + len(result.stderr), 1024)


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
        dependencies = next(step for step in job['steps'] if step.get('id') == 'dependencies')
        self.assertEqual(dependencies['run'], "python -I -m pip install --disable-pip-version-check 'PyYAML>=6,<7' 'jsonschema>=4.18,<5' referencing")
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
