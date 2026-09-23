"""T4-T6 public tools; provider transport simulations are explicitly synthetic."""
from __future__ import annotations

import copy
import importlib.util
import json
from unittest.mock import patch

from test_knowledge import PublicCase, digest, encoded
import support


class PrTests(PublicCase):
    def test_selected(self):
        self.prepare('pr', 'pr.py', ['C4-config', 'C6-binding', 'T4-git-round-trip', 'T4-synthetic-provider'])
        self.phase('C4-config')
        self.config_checks()
        self.phase('C6-binding')
        self.binding_negative()
        self.require_write_roundtrip()
        self.phase('T4-git-round-trip')
        repository = self.project / 'git-fixture'
        repository.mkdir()
        empty_template = self.project / 'empty-git-template'
        empty_template.mkdir()
        support.git('init', '--initial-branch=fixture', '--template=' + str(empty_template), cwd=repository)
        changed = self.write('git-fixture/change.txt', 'before\n'.encode())
        support.git('add', '--', 'change.txt', cwd=repository)
        commit_args = ('-c', 'user.name=Synthetic Fixture', '-c', 'user.email=fixture@example.invalid',
                       '-c', 'commit.gpgsign=false', '-c', 'core.hooksPath=' + str(empty_template), 'commit', '-m')
        support.git(*commit_args, 'base fixture', cwd=repository)
        base = support.git('rev-parse', 'HEAD', cwd=repository).decode().strip()
        self.replace_fixture(changed, 'after: 測試\n'.encode())
        support.git('add', '--', 'change.txt', cwd=repository)
        support.git(*commit_args, 'head fixture', cwd=repository)
        head = support.git('rev-parse', 'HEAD', cwd=repository).decode().strip()
        self.assertEqual(int(support.git('rev-list', '--count', 'HEAD', cwd=repository)), 2)
        self.assertEqual(support.git('ls-files', cwd=repository).decode().splitlines(), ['change.txt'])
        self.run.measure()
        content = {'title': 'selected fixture PR', 'summary': 'One UTF-8 committed change.', 'validation': [], 'references': [],
                   'provider_target': {'provider': 'github', 'host': 'github.com', 'repository': 'synthetic/fixture',
                                       'base_ref': 'main', 'head_ref': 'fixture'}}
        prepared = self.invoke('prepare', repository_root=str(repository), base_commit=base, head_commit=head, content=content)
        ref = prepared['reference']
        inspected = self.invoke('inspect', reference=ref)
        self.assertEqual(inspected['record']['validation'], [])
        subject = inspected['record']['subject']
        content['validation'] = [{'id': 'V1', 'command': 'not executed', 'disposition': 'deferred',
                                  'subject_head': subject['head_commit'], 'subject_diff_sha256': subject['diff_sha256'],
                                  'evidence': [], 'reason': 'Synthetic attribution; owner fixture; next action separate actual check.'}]
        revised = self.invoke('revise', reference=ref, expected_sha256=inspected['sha256'], content=content)
        self.invoke('revise', reference=ref, expected_sha256=inspected['sha256'], content=content, expect='conflict')
        path = self.record_path(ref, '.pr.json')
        before = path.read_bytes()
        rendered = self.invoke('render', reference=ref, repository_root=str(repository))
        self.assertTrue(rendered['subject_verified'])
        self.assertEqual(rendered['sha256'], digest(before))
        self.assertEqual(path.read_bytes(), before)
        inspected = self.invoke('inspect', reference=ref)
        self.assertEqual(inspected['record']['validation'][0]['disposition'], 'deferred')
        stale = copy.deepcopy(content)
        stale['validation'][0]['subject_head'] = base
        self.invoke('revise', reference=ref, expected_sha256=revised['sha256'], content=stale, expect=('invalid-input', 'conflict'))
        self.phase('T4-synthetic-provider')
        self.synthetic_provider(repository, inspected, rendered)
        self.finish()

    def synthetic_provider(self, repository, inspected, rendered):
        """Actual adapter.execute, fake run_bounded transport ONLY; no public/provider pass claim."""
        spec = importlib.util.spec_from_file_location('selected_synthetic_github', self.package / 'scripts/github.py')
        adapter = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(adapter)
        target = inspected['record']['provider_target']
        subject = inspected['record']['subject']
        request = {'operation': 'provider-create', **self.common, 'reference': inspected['reference'],
                   'repository_root': str(repository), 'expected_record_sha256': inspected['sha256'],
                   'expected_template_sha256': rendered['template_sha256'], 'expected_body_sha256': rendered['body_sha256'],
                   'write_mode': 'coordinated-single-writer', 'grant': {
                   'source': 'synthetic-only:no-owner-authorization', 'operation': 'provider-create',
                   'target': target, 'body_sha256': rendered['body_sha256']}}
        observations = []
        for scenario in ('unavailable-gh', 'preflight-conflict', 'post-write-read-failure', 'lost-write-response'):
            transport = []

            def fake_run(argv, env, cwd, input_data=None, timeout=30):
                # Only these finite command shapes exist; unknown calls fail closed.
                if str(argv[0]) == support.PYTHON:
                    local = json.loads(input_data)
                    response = {'explain': {'outcome': 'succeeded'}, 'inspect': inspected, 'render': rendered}[local['operation']]
                    return 0, encoded({**response, 'operation': local['operation'], 'mutation_state': 'none'}), b''
                self.assertEqual(argv[0], 'gh')
                method = argv[argv.index('--method') + 1]
                endpoint = argv[-3] if argv[-2:] == ['--input', '-'] else argv[-1]
                transport.append({'method': method, 'endpoint': endpoint})
                if scenario == 'unavailable-gh':
                    adapter.fail('executable', 'Synthetic missing executable.', 'unavailable')
                if '/git/ref/heads/' in endpoint:
                    name = endpoint.rsplit('/', 1)[-1]
                    oid = subject['base_commit' if name == target['base_ref'] else 'head_commit']
                    value = {'ref': 'refs/heads/' + name, 'object': {'type': 'commit', 'sha': oid}}
                    if scenario == 'preflight-conflict':
                        value['object']['sha'] = '0' * len(oid)
                elif '/compare/' in endpoint:
                    value = {'merge_base_commit': {'sha': subject['merge_base']}}
                elif '/pulls?' in endpoint:
                    value = []
                elif method == 'POST':
                    if scenario == 'lost-write-response':
                        raise TimeoutError('Synthetic lost response; transport never dispatched.')
                    value = {'number': 1}
                elif method == 'GET' and endpoint.endswith('/pulls/1'):
                    return 1, b'', b'synthetic read failure'
                else:
                    raise AssertionError('Unexpected synthetic transport request')
                return 0, encoded(value), b''

            # A second guard rejects any accidental fall-through even if the seam changes.
            with patch.object(adapter, 'run_bounded', fake_run), patch.object(adapter.subprocess, 'Popen', side_effect=AssertionError('Live subprocess forbidden')):
                response = adapter.execute(request)
            expected = {'unavailable-gh': ('unavailable', 'none', 0), 'preflight-conflict': ('conflict', 'none', 0),
                        'post-write-read-failure': ('failed', 'committed', 1), 'lost-write-response': ('failed', 'unknown', 1)}[scenario]
            self.assertEqual((response['outcome'], response['mutation_state'], sum(x['method'] == 'POST' for x in transport)), expected)
            observations.append({'scenario': scenario, 'synthetic_transport_calls': transport, 'response': response})
        self.run.write(self.root / 'synthetic-provider.json', encoded({'basis': 'synthetic transport only; no live gh/provider call',
                                                                     'cases': observations}))


class BacklogTests(PublicCase):
    def test_selected(self):
        self.prepare('local-backlog', 'local_backlog.py', ['C4-config', 'C6-binding', 'T5-round-trip'])
        self.phase('C4-config')
        self.config_checks()
        self.phase('C6-binding')
        self.binding_negative()
        self.require_write_roundtrip()
        self.phase('T5-round-trip')
        self.assertEqual(self.invoke('query')['matches'], [])
        content = {'title': 'selected fixture work', 'summary': 'Local scope only.', 'acceptance': ['Retain caller evidence.'],
                   'references': [{'kind': 'github-issue', 'target': 'https://github.com/synthetic/fixture/issues/1', 'relationship': 'reference-only'}]}
        created = self.invoke('create', content=content)
        ref = created['reference']
        inspected = self.invoke('inspect', reference=ref)
        self.assertEqual(inspected['record']['writable_authority'], 'local')
        content['summary'] = 'Revised local scope only.'
        revised = self.invoke('revise', reference=ref, expected_sha256=inspected['sha256'], content=content)
        self.invoke('revise', reference=ref, expected_sha256=inspected['sha256'], content=content, expect='conflict')
        current = revised
        # Actual delivered public states; the selected design's "active" is conceptual.
        for prior, target in [('draft', 'planned'), ('planned', 'in_progress')]:
            current = self.invoke('transition', reference=ref, expected_sha256=current['sha256'], expected_state=prior,
                                  target_state=target, reason='Selected fixture transition.', completion_evidence=[])
        self.invoke('transition', reference=ref, expected_sha256=current['sha256'], expected_state='draft', target_state='completed',
                    reason='Stale state.', completion_evidence=[], expect='conflict')
        self.invoke('transition', reference=ref, expected_sha256=current['sha256'], expected_state='in_progress', target_state='completed',
                    reason='Missing evidence.', completion_evidence=[], expect=('blocked', 'invalid-input'))
        completed = self.invoke('transition', reference=ref, expected_sha256=current['sha256'], expected_state='in_progress', target_state='completed',
                                reason='Caller-attributed fixture completion.', completion_evidence=[{'source': 'synthetic:observation', 'note': 'Attribution only.'}])
        self.invoke('revise', reference=ref, expected_sha256=completed['sha256'], content=content, expect='unsupported')
        self.read_preserves(ref, '.work-item.json', ('inspect', 'render'))
        self.finish()


class WorkflowTests(PublicCase):
    def test_selected(self):
        self.prepare('software-development-orchestrator', 'workflow.py', ['C4-config', 'C6-binding', 'T6-round-trip', 'T6-with-deferrals'])
        self.phase('C4-config')
        self.config_checks()
        self.phase('C6-binding')
        self.binding_negative()
        self.require_write_roundtrip()
        self.phase('T6-round-trip')
        minimal = {'title': 'selected fixture workflow', 'intent': 'Retain truthful outcomes.',
                   'scope': {'included': ['fixture'], 'excluded': ['real work']}, 'acceptance': [{'id': 'A1', 'criterion': 'Fixture observation.'}],
                   'first_action': {'action': 'Inspect fixture', 'completion_condition': 'Record observation', 'owner': 'synthetic-owner'}}
        created = self.invoke('create', content=minimal)
        ref = created['reference']
        inspected = self.invoke('inspect', reference=ref)
        current = self.invoke('transition', reference=ref, expected_sha256=inspected['sha256'], expected_state='planned',
                              target_state='active', reason='Fixture active; no permission inferred.')
        content = self.invoke('inspect', reference=ref)['record']['content']
        content['tasks'][0]['state'] = 'active'
        current = self.invoke('checkpoint', reference=ref, expected_sha256=current['sha256'], content=content, reason='Start fixture task.')
        content['references'] = [{'id': 'R1', 'kind': 'opaque', 'target': 'synthetic:failure', 'schema': None, 'sha256': None,
                                  'resolution': 'unverified', 'blocking': False, 'evidence_value': 'unknown', 'note': 'Synthetic attribution.'}]
        content['evidence'] = [{'id': 'E1', 'task_id': 'T001', 'summary': 'Synthetic failed observation.', 'disposition': 'failed',
                                'subject': 'fixture only', 'source_refs': ['R1'], 'reported_by': 'synthetic-owner',
                                'observed_at': inspected['record']['created_at'], 'basis': 'caller-supplied'}]
        content['tasks'][0].update(state='failed', reason='Fixture failure.', result='Not passed.', evidence_ids=['E1'])
        content['acceptance'][0].update(disposition='failed', evidence_ids=['E1'], reason='Fixture failure.')
        content['decisions'] = [{'id': 'D1', 'question': 'Who handles the fixture failure?', 'state': 'open', 'owner': 'synthetic-owner',
                                 'resolution': None, 'source_refs': [], 'next_action': 'Owner disposition.'}]
        current = self.invoke('checkpoint', reference=ref, expected_sha256=current['sha256'], content=content, reason='Retain fixture failure.')
        self.invoke('transition', reference=ref, expected_sha256=current['sha256'], expected_state='active', target_state='completed',
                    reason='Unresolved decision and failed acceptance.', expect='blocked')
        resumed = self.invoke('resume', reference=ref)
        self.assertIn('Synthetic failed observation.', json.dumps(resumed['continuation']))
        self.invoke('resume', reference=ref, overrides={'resume_budget_chars': 2000}, expect='unsupported')
        retrospective = {'outcome': 'no-new-knowledge', 'reflection': {'actual_outcome': 'Failed fixture.',
                         'observations': 'Caller-attributed failure remains.', 'limitations': 'No actual project execution.'},
                         'rationale': 'No general knowledge from synthetic input.', 'candidates': []}
        current = self.invoke('retrospect', reference=ref, expected_sha256=current['sha256'], retrospective=retrospective)
        record = self.invoke('inspect', reference=ref)['record']
        basis = copy.deepcopy(record['content'])
        basis['next_action'] = None
        self.assertEqual(record['retrospective']['content_sha256'], digest(encoded(basis)))
        content['intent'] = 'Retain failure and clear stale retrospective.'
        current = self.invoke('checkpoint', reference=ref, expected_sha256=current['sha256'], content=content, reason='Changed content.')
        record = self.invoke('inspect', reference=ref)['record']
        self.assertIsNone(record['retrospective'])
        self.assertTrue(any(row['previous_state']['retrospective'] for row in record['history']))
        before = self.record_path(ref, '.workflow.json').read_bytes()
        self.invoke('retention-preview', mode='purge', selection=[ref['id']])
        self.assertEqual(self.record_path(ref, '.workflow.json').read_bytes(), before)
        self.phase('T6-with-deferrals')
        deferred = self.invoke('create', content={**minimal, 'title': 'Separate with-deferrals fixture'})
        ref = deferred['reference']
        current = self.invoke('transition', reference=ref, expected_sha256=deferred['sha256'], expected_state='planned',
                              target_state='active', reason='Prepare explicit deferral.')
        content = self.invoke('inspect', reference=ref)['record']['content']
        deferral = {'reason': 'Synthetic owner deferral.', 'owner': 'synthetic-owner', 'trigger': 'Separate actual work',
                    'next_action': 'Owner decides later.', 'authority_ref': 'synthetic:authority-only'}
        content['tasks'][0].update(state='deferred', reason=deferral['reason'], deferral=deferral)
        content['acceptance'][0].update(disposition='deferred', reason=deferral['reason'], deferral=deferral)
        current = self.invoke('checkpoint', reference=ref, expected_sha256=current['sha256'], content=content, reason='Attributed deferral.')
        current = self.invoke('retrospect', reference=ref, expected_sha256=current['sha256'], retrospective=retrospective)
        self.invoke('transition', reference=ref, expected_sha256=current['sha256'], expected_state='active', target_state='completed', reason='With deferrals, not aggregate pass.')
        resumed = self.invoke('resume', reference=ref)
        self.assertEqual(resumed['continuation']['completion_disposition'], 'with-deferrals')
        self.assertIn('synthetic:authority-only', json.dumps(resumed['continuation']))
        self.finish()
