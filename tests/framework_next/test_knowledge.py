"""T1-T3 and shared public test assertions; fixtures use unchanged committed resources."""
from __future__ import annotations

import base64
from hashlib import sha256
import json
import unittest
import uuid

import support


def encoded(value):
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + '\n').encode('utf-8')


def digest(raw):
    return sha256(raw).hexdigest()


class PublicCase(unittest.TestCase):
    """Thin assertions over FixtureRun, not a package assembler or installation fixture."""
    complete = False
    blocked_before_write = False

    def prepare(self, family, script, phases):
        self.family, self.phases = family, ['resource-setup', *phases]
        self.finished, self.current, self.calls = [], 'resource-setup', []
        self.nested_bound = 0
        self.complete = False
        self.blocked_before_write = False
        self.run = support.active_run()
        self.root = self.run.case(family)
        self.project, self.package = self.root / 'project', self.root / 'package'
        self.project.mkdir()
        self.package.mkdir()
        self.commit = support.git('rev-parse', 'HEAD').decode().strip()
        prefix = 'src/skills/' + family + '/'
        paths = support.git('ls-tree', '-r', '--name-only', self.commit, '--', prefix).decode().splitlines()
        blobs = support.git_blobs(self.commit, paths)
        self.resources = []
        for name, blob in blobs.items():
            relative = name.removeprefix(prefix)
            destination = self.package / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            # Source resources are exact Git bytes, not newly authored tiny fixtures.
            destination.write_bytes(blob.data)
            self.assertEqual(destination.read_bytes(), blob.data)
            self.resources.append({'path': name, 'relative': relative, 'oid': blob.oid,
                                   'mode': blob.mode, 'sha256': digest(blob.data), 'bytes': len(blob.data)})
            self.run.measure()
        self.script = self.package / 'scripts' / script
        self.common = {'project_root': str(self.project), 'package_root': str(self.package)}
        self.transcript = self.root / 'public-transcript.jsonl'
        self.transcript.touch(exist_ok=False)
        self.run.write(self.root / 'source-binding.json', encoded({
            'fixture_kind': 'direct-committed-package-resources', 'commit': self.commit,
            'not_established': ['candidate assembly', 'installation', 'native acceptance'],
            'members': self.resources}))
        explained = self.invoke('explain')
        self.defaults = (explained['result'] if family == 'problem-frame-author' else explained)['settings']
        self.store = self.project / self.defaults['store']['root']
        self.assertFalse(self.store.exists(), 'explain must not provision a store')
        self.store.mkdir(parents=True)
        self.run.measure()

    def phase(self, name):
        self.assertIn(name, self.phases)
        self.finished.append(self.current)
        self.current = name

    def finish(self):
        for row in self.resources:
            self.assertEqual(digest((self.package / row['relative']).read_bytes()), row['sha256'])
        self.finished.append(self.current)
        self.current = None
        self.assertEqual(self.finished, self.phases)
        self.complete = True

    def observation(self):
        finished = getattr(self, 'finished', [])
        current = getattr(self, 'current', None)
        return {'source_commit': getattr(self, 'commit', None),
                'fixture_kind': 'direct-committed-package-resources',
                'completed_phases': finished, 'failed_phase': current if not self.blocked_before_write else None,
                'blocked_before_write': self.blocked_before_write,
                'unexecuted_phases': [p for p in getattr(self, 'phases', []) if p not in finished and p != current],
                'public_launches': len(getattr(self, 'calls', [])),
                'calls': getattr(self, 'calls', []),
                'nested_child_launches': 'unavailable: unchanged public children are not instrumented',
                'nested_launch_upper_bound': getattr(self, 'nested_bound', 0),
                'boundary_authored_bytes': getattr(self, 'boundary_authored_bytes', 0),
                'transcript': str(getattr(self, 'transcript', 'not-created'))}

    def require_write_roundtrip(self):
        if getattr(self.run, 'public_read_only', False):
            for row in self.resources:
                self.assertEqual(digest((self.package / row['relative']).read_bytes()), row['sha256'])
            self.finished.append(self.current)
            self.current = None
            self.blocked_before_write = True
            self.skipTest('Explicit read-only selection: dependent write round-trip NOT EXECUTED; selection cannot pass.')

    def write(self, name, value):
        path = self.project / name
        path.parent.mkdir(parents=True, exist_ok=True)
        raw = value if isinstance(value, bytes) else encoded(value)
        return self.run.write(path, raw)

    def replace_fixture(self, path, value):
        """Explicit test input mutation, budgeted by the existing helper; never product source."""
        raw = value if isinstance(value, bytes) else encoded(value)
        self.assertTrue(path.is_relative_to(self.project))
        path.unlink()
        return self.run.write(path, raw)

    def invoke(self, operation, *, expect='success', script=None, **values):
        support.check(len(self.calls) < getattr(self.run, 'public_launch_limit', 160), 'public launch cap exceeded')
        request = {'operation': operation, **self.common, **values}
        # Source-bounded reservations, NOT observed process counts. No retries or
        # opaque provider driver is launched here. PR git_subject has <32 calls;
        # local ignored-state checks have <=3. Stop before the combined ceiling.
        reservation = (3 if 'local_config' in request else 0) + (32 if self.family == 'pr' and 'repository_root' in request else 0)
        support.check(getattr(self.run, 'prior_process_bound', 0) + sum(self.run.processes.values()) + self.nested_bound + reservation + 1 <= 256,
                      'helper plus nested launch bound exceeded')
        self.nested_bound += reservation
        request_path = self.root / 'request.json'
        if request_path.exists():
            request_path.unlink()
        self.run.write(request_path, encoded(request))
        argv = [support.PYTHON, '-I', '-B', str(script or self.script), '--request', str(request_path)]
        call = {'operation': operation, 'phase': self.current, 'expected': expect}
        self.calls.append(call)
        try:
            result = support.run_process(argv, cwd=self.project)
        except Exception as exc:
            call.update(exception_type=type(exc).__name__, diagnostic=str(exc))
            with self.transcript.open('ab') as stream:
                stream.write(encoded({'argv': argv, 'request': request, **call}))
            raise
        # One append-only transcript retains EXACT stdout/stderr, including non-JSON failures.
        with self.transcript.open('ab') as stream:
            stream.write(json.dumps({'argv': argv, 'request': request, 'exit': result.returncode,
                                     'stdout_base64': base64.b64encode(result.stdout).decode(),
                                     'stderr_base64': base64.b64encode(result.stderr).decode()}, sort_keys=True).encode() + b'\n')
        call.update(exit=result.returncode, stdout_sha256=digest(result.stdout), stderr_sha256=digest(result.stderr))
        self.run.measure()
        response = json.loads(result.stdout)
        call['outcome'] = response.get('outcome')
        call['diagnostics'] = response.get('diagnostics', [])
        if expect == 'success':
            self.assertEqual(result.returncode, 0, response)
            self.assertEqual(response['outcome'], 'ok' if self.family == 'problem-frame-author' else 'succeeded')
        else:
            expected = {expect} if isinstance(expect, str) else set(expect)
            self.assertIn(response['outcome'], expected, response)
            if self.family == 'problem-frame-author':
                self.assertEqual(result.returncode, 3 if response['outcome'] in {'conflict', 'blocked'} else
                                 4 if response['outcome'] in {'unavailable', 'io-error'} else 2)
            else:
                self.assertEqual(result.returncode, 1)
            self.assertEqual(response['mutation_state'], 'none', response)
        return response

    def config_checks(self):
        """C4: reuse one project, never an exhaustive configuration matrix."""
        absent = 'unavailable' if self.family == 'problem-frame-author' else 'invalid-input'
        self.invoke('explain', project_config='missing.json', expect=absent)
        template = self.defaults['template']
        self.write('view.md', (self.package / template['path']).read_bytes())
        project_config = {'config_version': 2, 'skills': {self.family: {
            'store': {'root': self.defaults['store']['root'], 'tracking': 'ignored'},
            'template': {'origin': 'project', 'path': 'view.md'}}, 'foreign.inert': {'unknown': None}}}
        config = self.write('config.json', project_config)
        local = self.write('local.json', {'config_version': 2, 'skills': {self.family: {
            'store': {'tracking': 'tracked'}, 'template': template}}})
        # This project is deliberately not a Git worktree; local ignored-state Git checks
        # are not claimed. The one PR fixture exercises actual Git separately.
        observed = self.invoke('explain', project_config=str(config), local_config=str(local))
        effective = observed['result'] if self.family == 'problem-frame-author' else observed
        self.assertEqual(effective['settings']['template'], template)
        self.assertEqual(effective['settings']['store']['tracking'], 'tracked')
        observed = self.invoke('explain', project_config=str(config), local_config=str(local),
                               overrides={'store': {'tracking': 'ignored'}, 'template': {'origin': 'project', 'path': 'view.md'}})
        effective = observed['result'] if self.family == 'problem-frame-author' else observed
        self.assertEqual(effective['settings']['template'], {'origin': 'project', 'path': 'view.md'})
        self.assertEqual(effective['settings']['store']['tracking'], 'ignored')
        self.assertNotIn('foreign.inert', effective['settings'])
        version_outcome = 'unsupported-version' if self.family == 'problem-frame-author' else 'unsupported'
        for raw, expected in [(b'{"config_version":2,"config_version":2}', 'invalid-input'),
                              (encoded({'config_version': True}), version_outcome), (encoded({'config_version': 2.0}), version_outcome),
                              (encoded({'config_version': 2, 'skills': {self.family: None}}), 'invalid-input'),
                              (encoded({'config_version': 2, 'skills': {self.family: {'unknown': True}}}), 'invalid-input')]:
            self.replace_fixture(config, raw)
            self.invoke('explain', project_config=str(config), expect=expected)
        self.replace_fixture(local, {'config_version': 2, 'constraints': {'foreign.inert': {}}})
        self.invoke('explain', local_config=str(local), expect='invalid-input')
        self.replace_fixture(config, {'config_version': 2, 'constraints': {self.family: {'locked_fields': ['store.tracking']}}})
        self.invoke('explain', project_config=str(config), overrides={'store': {'tracking': 'ignored'}}, expect='blocked')
        self.invoke('explain', write_roots=[str(self.store / 'narrow')], expect='blocked')
        outside = self.root / 'outside'
        outside.mkdir()
        self.invoke('explain', overrides={'store': {'root': str(outside)}}, write_roots=[str(outside)], expect='blocked')
        self.invoke('explain', overrides={'template': {'origin': 'package', 'path': 'templates/undeclared.md'}}, expect='invalid-input')
        self.invoke('explain', overrides={'store': {'root': '../escape'}}, expect=('invalid-input', 'blocked'))
        if self.family == 'lesson':
            self.replace_fixture(config, {'config_version': 1, 'skills': {'lesson': {}}})
            self.assertEqual(self.invoke('explain', project_config=str(config))['config_version'], 1)
            self.replace_fixture(local, {'config_version': 2})
            self.invoke('explain', project_config=str(config), local_config=str(local), expect='invalid-input')

    def binding_negative(self):
        # Exact executable bytes outside package/scripts must not bind to the selected package.
        wrong = self.root / 'wrong-entry.py'
        wrong.write_bytes(self.script.read_bytes())
        self.run.measure()
        self.invoke('explain', script=wrong, expect=('invalid-input', 'blocked'))

    def input_boundary(self):
        """The single selected 4 MiB+1 exception, transient stdin, no giant file copies."""
        self.assertFalse(getattr(self, 'boundary_authored_bytes', 0))
        support.check(len(self.calls) < getattr(self.run, 'public_launch_limit', 160), 'public launch cap exceeded')
        support.check(getattr(self.run, 'prior_process_bound', 0) + sum(self.run.processes.values()) + self.nested_bound + 1 <= 256,
                      'helper plus nested launch bound exceeded')
        raw = b' ' * (4 * 1024 * 1024 + 1)
        self.boundary_authored_bytes = len(raw)
        argv = [support.PYTHON, '-I', '-B', str(self.script), '--request', '-']
        result = support.run_process(argv, cwd=self.project, input=raw)
        response = json.loads(result.stdout)
        self.calls.append({'operation': 'oversize-request', 'phase': self.current, 'exit': result.returncode,
                           'outcome': response['outcome'], 'stdin_bytes': len(raw), 'stdin_sha256': digest(raw),
                           'stdout_sha256': digest(result.stdout), 'diagnostics': response['diagnostics']})
        with self.transcript.open('ab') as stream:
            stream.write(json.dumps({'argv': argv, 'stdin_bytes': len(raw), 'stdin_sha256': digest(raw),
                'exit': result.returncode, 'stdout_base64': base64.b64encode(result.stdout).decode(),
                'stderr_base64': base64.b64encode(result.stderr).decode()}, sort_keys=True).encode() + b'\n')
        self.run.measure()
        self.assertEqual((result.returncode, response['outcome'], response['mutation_state']), (1, 'unsupported', 'none'))
        self.assertEqual(response['diagnostics'][0]['code'], 'size-limit')

    def new_identity(self, operation, **values):
        query = self.invoke('query', text='selected fixture')
        self.assertFalse(query['partial'])
        return self.invoke(operation, text='selected fixture', decision={
            'action': 'new', 'query_sha256': query['query_sha256'], 'acknowledge_partial': False,
            'reason': 'Synthetic fixture identity after the actual public query.'}, **values)

    def record_path(self, reference, suffix):
        return self.store / (reference['id'] + suffix)

    def read_preserves(self, reference, suffix, operations=('inspect', 'validate', 'render')):
        path = self.record_path(reference, suffix)
        before = path.read_bytes()
        for operation in operations:
            result = self.invoke(operation, reference=reference)
            self.assertEqual(result['sha256'], digest(before))
            self.assertEqual(path.read_bytes(), before)
        return json.loads(before), before


def lesson_content():
    return {'title': 'selected fixture lesson', 'observation': 'One bounded observation.', 'evidence': [],
            'conclusion': 'Tentative fixture conclusion.', 'applies_when': ['Synthetic fixture only.'],
            'does_not_apply_when': [], 'confidence': 'tentative', 'follow_up': []}


class LessonTests(PublicCase):
    def test_selected(self):
        self.prepare('lesson', 'lesson.py', ['C4-config', 'C6-binding', 'T1-round-trip', 'C6-query-and-legacy', 'T1-decision-successor', 'C6-input-boundary'])
        self.phase('C4-config')
        self.config_checks()
        self.phase('C6-binding')
        self.binding_negative()
        self.require_write_roundtrip()
        self.phase('T1-round-trip')
        content = lesson_content()
        created = self.new_identity('create', content=content)
        ref = created['reference']
        record, original = self.read_preserves(ref, '.lesson.json')
        content['conclusion'] = 'Revised fixture conclusion.'
        revised = self.invoke('revise', reference=ref, expected_sha256=digest(original), content=content, reason='One revision.')
        self.invoke('revise', reference=ref, expected_sha256=digest(original), content=content, reason='Stale digest.', expect='conflict')
        unchanged = self.invoke('revise', reference=ref, expected_sha256=revised['sha256'], content=content, reason='Identical content.')
        self.assertFalse(unchanged['changed'])
        self.assertEqual(unchanged['sha256'], revised['sha256'])
        self.phase('C6-query-and-legacy')
        query = self.invoke('query', text='selected fixture')
        legacy_id = 'lesson-' + uuid.uuid4().hex
        legacy_path = self.store / (legacy_id + '.lesson.json')
        self.run.write(legacy_path, b'{"schema_version":"99.0.0"}\n')
        conflict = self.invoke('create', content=content, text='selected fixture', decision={
            'action': 'new', 'query_sha256': query['query_sha256'], 'acknowledge_partial': False,
            'reason': 'Changed inventory must conflict.'}, expect='conflict')
        partial = self.invoke('query', text='selected fixture')
        self.assertTrue(partial['partial'])
        self.assertEqual(conflict['related_query']['query_sha256'], partial['query_sha256'])
        self.invoke('create', content=content, text='selected fixture', decision={
            'action': 'new', 'query_sha256': partial['query_sha256'], 'acknowledge_partial': False,
            'reason': 'No partial acknowledgement.'}, expect='blocked')
        self.assertEqual(legacy_path.read_bytes(), b'{"schema_version":"99.0.0"}\n')
        self.replace_fixture(legacy_path, b'{malformed\n')
        malformed = self.invoke('query', text='selected fixture')
        self.assertTrue(malformed['partial'])
        self.assertEqual(legacy_path.read_bytes(), b'{malformed\n')
        legacy = {'schema_version': '1.0.0', 'kind': 'lesson', 'owner': 'project', 'id': legacy_id,
                  'status': 'candidate', 'created_at': record['created_at'], 'updated_at': record['created_at'], **lesson_content()}
        self.replace_fixture(legacy_path, legacy)
        legacy_ref = {'role': 'lesson.record', 'id': legacy_id}
        _, legacy_raw = self.read_preserves(legacy_ref, '.lesson.json')
        self.invoke('revise', reference=legacy_ref, expected_sha256=digest(legacy_raw), content=content,
                    reason='Legacy is read-only.', expect='unsupported')
        derived = self.new_identity('derive', reference=legacy_ref, expected_sha256=digest(legacy_raw), reason='Explicit v1 derivation.')
        self.assertEqual(legacy_path.read_bytes(), legacy_raw)
        self.assertNotEqual(derived['reference'], legacy_ref)
        self.assertEqual(self.invoke('inspect', reference=derived['reference'])['record']['schema_version'], '2.0.0')
        self.phase('T1-decision-successor')
        selection = {'binding_id': 'synthetic', 'path': 'decision/accept.json', 'expected_sha256': digest(b'no adapter')}
        self.invoke('accept', reference=ref, expected_sha256=revised['sha256'], reason='Adapter absent.', decision_source=selection, expect='blocked')
        accepted = decision(self, ref, revised['sha256'], 'accept')
        self.invoke('supersede', reference=ref, expected_sha256=accepted['sha256'], reason='Self-cycle refused.',
                    successor={'reference': ref, 'expected_sha256': accepted['sha256']}, expect=('invalid-input', 'conflict'))
        self.common.pop('project_config')
        self.phase('C6-input-boundary')
        self.input_boundary()
        self.finish()


def decision(case, reference, sha, operation, option=None, negative=None):
    """Explicit synthetic project-local authority; never actual owner adoption."""
    fields = ['subject_sha256', 'actor', 'decision', 'decided_at'] + (['option_id'] if option else [])
    config = {'config_version': 2, 'constraints': {case.family: {'decision_sources': [{
        'id': 'synthetic', 'root': 'decision', 'allowed_actors': ['synthetic-actor'],
        'pointers': {field: '/' + field for field in fields}}]}}}
    case.write('authority.json', config)
    case.common['project_config'] = str(case.project / 'authority.json')
    current = case.invoke('inspect', reference=reference)['record']
    evidence = {'subject_sha256': sha, 'actor': 'synthetic-actor', 'decision': 'accept', 'decided_at': current['updated_at']}
    if option:
        evidence['option_id'] = option
    path = case.write('decision/accept.json', evidence)
    for invalid in negative or []:
        bad = {**evidence, **invalid}
        case.replace_fixture(path, bad)
        case.invoke(operation, reference=reference, expected_sha256=sha, reason='Synthetic invalid decision.',
                    decision_source={'binding_id': 'synthetic', 'path': 'decision/accept.json', 'expected_sha256': digest(encoded(bad))},
                    expect=('blocked', 'invalid-input'))
        case.replace_fixture(path, evidence)
    return case.invoke(operation, reference=reference, expected_sha256=sha, reason='Synthetic mapped decision only.',
                       decision_source={'binding_id': 'synthetic', 'path': 'decision/accept.json', 'expected_sha256': digest(encoded(evidence))})


class AdrTests(PublicCase):
    def test_selected(self):
        self.prepare('adr', 'adr.py', ['C4-config', 'C6-binding', 'T2-round-trip', 'T2-decision-derive'])
        self.phase('C4-config')
        self.config_checks()
        self.phase('C6-binding')
        self.binding_negative()
        self.require_write_roundtrip()
        self.phase('T2-round-trip')
        content = {'title': 'selected fixture ADR', 'context': 'Fixture decision.', 'decision_drivers': ['Bounded scope'],
                   'options': [{'id': name, 'summary': name, 'benefits': ['Small'], 'costs': ['Limited']} for name in ('a', 'b')],
                   'consequences': [], 'evidence': [], 'applies_when': ['Synthetic only'], 'does_not_apply_when': []}
        created = self.new_identity('create', content=content)
        ref = created['reference']
        _, original = self.read_preserves(ref, '.adr.json', ('inspect',))
        content['context'] = 'Revised fixture decision.'
        revised = self.invoke('revise', reference=ref, expected_sha256=digest(original), content=content, reason='One revision.')
        self.invoke('revise', reference=ref, expected_sha256=digest(original), content=content, reason='Stale.', expect='conflict')
        self.read_preserves(ref, '.adr.json', ('render',))
        self.phase('T2-decision-derive')
        accepted = decision(self, ref, revised['sha256'], 'decide', option='a',
                            negative=[{'subject_sha256': digest(original)}, {'option_id': 'unknown'}])
        self.invoke('revise', reference=ref, expected_sha256=accepted['sha256'], content=content, reason='Accepted immutable.', expect='invalid-input')
        self.invoke('supersede', reference=ref, expected_sha256=accepted['sha256'], reason='Self cycle.',
                    successor={'reference': ref, 'expected_sha256': accepted['sha256']}, expect=('invalid-input', 'conflict'))
        derived = self.new_identity('derive', reference=ref, expected_sha256=accepted['sha256'], reason='New draft.')
        draft = self.invoke('inspect', reference=derived['reference'])['record']
        self.assertEqual(draft['status'], 'draft')
        self.assertIsNone(draft['decision'])
        self.assertTrue(draft['provenance'])
        self.assertEqual(digest(self.record_path(ref, '.adr.json').read_bytes()), accepted['sha256'])
        self.common.pop('project_config')
        self.finish()


class PromotionTests(PublicCase):
    def test_selected(self):
        self.prepare('standards-promotion', 'standards_promotion.py', ['C4-config', 'C6-binding', 'T3-round-trip', 'T3-reconciliation-boundaries'])
        self.phase('C4-config')
        self.config_checks()
        self.phase('C6-binding')
        self.binding_negative()
        self.require_write_roundtrip()
        self.phase('T3-round-trip')
        target = self.write('rule.md', b'Original fixture rule.\n')
        source = self.write('evidence/source.txt', b'Synthetic source evidence.\n')
        config = self.write('promotion-config.json', {'config_version': 2, 'constraints': {self.family: {
            'source_read_roots': ['evidence'], 'targets': [{'id': 'rule', 'path': 'rule.md', 'applicability': 'fixture',
            'allowed_actors': ['synthetic-actor'], 'adoption_source': None, 'effect_source': None}]}}})
        self.common['project_config'] = str(config)
        before = target.read_bytes()
        content = {'title': 'selected fixture promotion', 'target_id': 'rule', 'expected_target_sha256': digest(before),
                   'replacement': 'Proposed fixture rule.\n', 'rationale': 'Synthetic proposal only.', 'applicability': 'fixture',
                   'conflicts': [], 'sources': [{'path': str(source), 'expected_sha256': digest(source.read_bytes()),
                   'kind': 'fixture', 'id': 'source-1', 'schema_version': '1.0.0', 'reason': 'Synthetic attribution.'}]}
        created = self.new_identity('propose', content=content)
        ref = created['reference']
        self.read_preserves(ref, '.promotion.json')
        reconciled = self.invoke('reconcile', reference=ref, expected_sha256=created['sha256'])
        self.assertEqual(reconciled['observation']['adoption'], 'unresolved')
        self.assertEqual(reconciled['observation']['effect'], 'unresolved')
        self.assertEqual(reconciled['observation']['rule_content'], 'drifted')
        self.assertEqual(target.read_bytes(), before)
        self.phase('T3-reconciliation-boundaries')
        self.invoke('revise', reference=ref, expected_sha256=created['sha256'], content=content, reason='Stale.', expect='conflict')
        self.invoke('supersede', reference=ref, expected_sha256=reconciled['sha256'], reason='Self cycle.',
                    successor={'reference': ref, 'expected_sha256': reconciled['sha256']}, expect=('invalid-input', 'conflict'))
        self.replace_fixture(target, b'External fixture edit.\n')
        self.invoke('revise', reference=ref, expected_sha256=reconciled['sha256'], content=content, reason='Changed target.', expect='conflict')
        self.assertEqual(target.read_bytes(), b'External fixture edit.\n')
        self.replace_fixture(target, before)
        self.replace_fixture(config, config.read_bytes() + b'\n')
        self.invoke('reconcile', reference=ref, expected_sha256=reconciled['sha256'], expect='conflict')
        self.common.pop('project_config')
        self.finish()
