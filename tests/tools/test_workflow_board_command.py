"""Command bridge fixtures from Board V1 examples inherited by V2.

Source Board b100c9f9bd09b2a1c125c8b511f06defeb29c556
src/Contracts/CollaborationV1/examples.json, with only versions/project added.
No consumer or test runtime dependency on that checkout. No live transport.
"""
from __future__ import annotations
import copy
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = ROOT / 'src/skills/workflow-board-experimental'
spec = importlib.util.spec_from_file_location('board_command_test_runtime', PACKAGE / 'tools/workflow_records/board_command.py')
api = importlib.util.module_from_spec(spec)
spec.loader.exec_module(api)

COMMAND_FIXTURES = {'workflow.create': {'service_contract_version': 'workflow-board/collaboration/2',
                     'schema_version': '2.0',
                     'workflow_ref': {'store_id': 'board-local',
                                      'namespace': 'personal',
                                      'record_kind': 'collaboration',
                                      'workflow_id': 'WF-1',
                                      'project_id': 'A'},
                     'operation_id': 'OP-1',
                     'expected_revision': 0,
                     'command': 'workflow.create',
                     'payload': {'title': 'Workflow',
                                 'goal': '完成分析',
                                 'scope': {'included': '本次工作', 'excluded': '部署'},
                                 'skill': {'id': 'analysis', 'version': None},
                                 'external_work_refs': []}},
 'workflow.start': {'service_contract_version': 'workflow-board/collaboration/2',
                    'schema_version': '2.0',
                    'workflow_ref': {'store_id': 'board-local',
                                     'namespace': 'personal',
                                     'record_kind': 'collaboration',
                                     'workflow_id': 'WF-1',
                                     'project_id': 'A'},
                    'operation_id': 'OP-2',
                    'expected_revision': 1,
                    'command': 'workflow.start',
                    'payload': {}},
 'workflow.pause': {'service_contract_version': 'workflow-board/collaboration/2',
                    'schema_version': '2.0',
                    'workflow_ref': {'store_id': 'board-local',
                                     'namespace': 'personal',
                                     'record_kind': 'collaboration',
                                     'workflow_id': 'WF-1',
                                     'project_id': 'A'},
                    'operation_id': 'OP-3',
                    'expected_revision': 1,
                    'command': 'workflow.pause',
                    'payload': {'reason': '稍後接續'}},
 'workflow.resume': {'service_contract_version': 'workflow-board/collaboration/2',
                     'schema_version': '2.0',
                     'workflow_ref': {'store_id': 'board-local',
                                      'namespace': 'personal',
                                      'record_kind': 'collaboration',
                                      'workflow_id': 'WF-1',
                                      'project_id': 'A'},
                     'operation_id': 'OP-4',
                     'expected_revision': 1,
                     'command': 'workflow.resume',
                     'payload': {}},
 'workflow.cancel': {'service_contract_version': 'workflow-board/collaboration/2',
                     'schema_version': '2.0',
                     'workflow_ref': {'store_id': 'board-local',
                                      'namespace': 'personal',
                                      'record_kind': 'collaboration',
                                      'workflow_id': 'WF-1',
                                      'project_id': 'A'},
                     'operation_id': 'OP-5',
                     'expected_revision': 1,
                     'command': 'workflow.cancel',
                     'payload': {'reason': '範圍變更', 'remaining': '未完成驗證'}},
 'workflow.complete': {'service_contract_version': 'workflow-board/collaboration/2',
                       'schema_version': '2.0',
                       'workflow_ref': {'store_id': 'board-local',
                                        'namespace': 'personal',
                                        'record_kind': 'collaboration',
                                        'workflow_id': 'WF-1',
                                        'project_id': 'A'},
                       'operation_id': 'OP-6',
                       'expected_revision': 1,
                       'command': 'workflow.complete',
                       'payload': {'summary': '必要工作已交付',
                                   'document_refs': [{'document_id': 'plan',
                                                      'revision': 1,
                                                      'content_hash': 'sha256:ddba9bf9f8afcbc5a8271ff38d21fe3ec34114e00bfd1f249bb6f99d902deee2'}]}},
 'plan.revise': {'service_contract_version': 'workflow-board/collaboration/2',
                 'schema_version': '2.0',
                 'workflow_ref': {'store_id': 'board-local',
                                  'namespace': 'personal',
                                  'record_kind': 'collaboration',
                                  'workflow_id': 'WF-1',
                                  'project_id': 'A'},
                 'operation_id': 'OP-7',
                 'expected_revision': 1,
                 'command': 'plan.revise',
                 'payload': {'plan': {'document_id': 'plan',
                                      'expected_document_revision': 0,
                                      'content': '# 工作計畫\n'},
                             'execution_impact': 'declared',
                             'task_changes': [{'kind': 'add',
                                               'definition': {'id': 'T1',
                                                              'title': '分析',
                                                              'description': '整理規則',
                                                              'scope': {'included': '本次工作', 'excluded': '部署'},
                                                              'completion_criteria': ['提供分析文件'],
                                                              'dependencies': [],
                                                              'plan_basis': {'document_id': 'plan',
                                                                             'revision': 1,
                                                                             'content_hash': 'sha256:ddba9bf9f8afcbc5a8271ff38d21fe3ec34114e00bfd1f249bb6f99d902deee2'},
                                                              'inputs': [],
                                                              'expected_artifacts': ['分析文件'],
                                                              'decision_ids': [],
                                                              'workstream': None}}],
                             'unaffected_task_ids': [],
                             'decision_dispositions': [],
                             'completion_requirements': [{'id': 'REQ-1',
                                                          'description': '交付分析',
                                                          'task_ids': ['T1'],
                                                          'document_refs': []}],
                             'requirement_dispositions': []}},
 'document.append': {'service_contract_version': 'workflow-board/collaboration/2',
                     'schema_version': '2.0',
                     'workflow_ref': {'store_id': 'board-local',
                                      'namespace': 'personal',
                                      'record_kind': 'collaboration',
                                      'workflow_id': 'WF-1',
                                      'project_id': 'A'},
                     'operation_id': 'OP-8',
                     'expected_revision': 1,
                     'command': 'document.append',
                     'payload': {'document': {'document_id': 'result',
                                              'expected_document_revision': 0,
                                              'content': '分析結果\n'},
                                 'purpose': 'result'}},
 'task.claim': {'service_contract_version': 'workflow-board/collaboration/2',
                'schema_version': '2.0',
                'workflow_ref': {'store_id': 'board-local',
                                 'namespace': 'personal',
                                 'record_kind': 'collaboration',
                                 'workflow_id': 'WF-1',
                                 'project_id': 'A'},
                'operation_id': 'OP-9',
                'expected_revision': 1,
                'command': 'task.claim',
                'payload': {'task_id': 'T1', 'expected_definition_revision': 1, 'session': None}},
 'task.progress': {'service_contract_version': 'workflow-board/collaboration/2',
                   'schema_version': '2.0',
                   'workflow_ref': {'store_id': 'board-local',
                                    'namespace': 'personal',
                                    'record_kind': 'collaboration',
                                    'workflow_id': 'WF-1',
                                    'project_id': 'A'},
                   'operation_id': 'OP-10',
                   'expected_revision': 1,
                   'command': 'task.progress',
                   'payload': {'task_id': 'T1',
                               'assignment': {'assignment_id': 'ASG-1',
                                              'generation': 1,
                                              'definition_revision': 1},
                               'summary': '已完成初稿',
                               'evidence': []}},
 'task.release': {'service_contract_version': 'workflow-board/collaboration/2',
                  'schema_version': '2.0',
                  'workflow_ref': {'store_id': 'board-local',
                                   'namespace': 'personal',
                                   'record_kind': 'collaboration',
                                   'workflow_id': 'WF-1',
                                   'project_id': 'A'},
                  'operation_id': 'OP-11',
                  'expected_revision': 1,
                  'command': 'task.release',
                  'payload': {'task_id': 'T1',
                              'assignment': {'assignment_id': 'ASG-1',
                                             'generation': 1,
                                             'definition_revision': 1},
                              'handoff': {'completed': '分析已完成',
                                          'remaining': '補充驗證',
                                          'next_step': '檢查既有結果',
                                          'artifact_refs': [{'kind': 'document',
                                                             'ref': {'document_id': 'plan',
                                                                     'revision': 1,
                                                                     'content_hash': 'sha256:ddba9bf9f8afcbc5a8271ff38d21fe3ec34114e00bfd1f249bb6f99d902deee2'}}],
                                          'blockers': [],
                                          'limitations': [],
                                          'next_actor_hint': None}}},
 'task.block': {'service_contract_version': 'workflow-board/collaboration/2',
                'schema_version': '2.0',
                'workflow_ref': {'store_id': 'board-local',
                                 'namespace': 'personal',
                                 'record_kind': 'collaboration',
                                 'workflow_id': 'WF-1',
                                 'project_id': 'A'},
                'operation_id': 'OP-12',
                'expected_revision': 1,
                'command': 'task.block',
                'payload': {'task_id': 'T1',
                            'assignment': {'assignment_id': 'ASG-1',
                                           'generation': 1,
                                           'definition_revision': 1},
                            'reason': '缺少輸入',
                            'handoff': {'completed': '分析已完成',
                                        'remaining': '補充驗證',
                                        'next_step': '檢查既有結果',
                                        'artifact_refs': [{'kind': 'document',
                                                           'ref': {'document_id': 'plan',
                                                                   'revision': 1,
                                                                   'content_hash': 'sha256:ddba9bf9f8afcbc5a8271ff38d21fe3ec34114e00bfd1f249bb6f99d902deee2'}}],
                                        'blockers': [],
                                        'limitations': [],
                                        'next_actor_hint': None}}},
 'task.unblock': {'service_contract_version': 'workflow-board/collaboration/2',
                  'schema_version': '2.0',
                  'workflow_ref': {'store_id': 'board-local',
                                   'namespace': 'personal',
                                   'record_kind': 'collaboration',
                                   'workflow_id': 'WF-1',
                                   'project_id': 'A'},
                  'operation_id': 'OP-13',
                  'expected_revision': 1,
                  'command': 'task.unblock',
                  'payload': {'task_id': 'T1', 'resolution': '已補齊輸入'}},
 'task.complete': {'service_contract_version': 'workflow-board/collaboration/2',
                   'schema_version': '2.0',
                   'workflow_ref': {'store_id': 'board-local',
                                    'namespace': 'personal',
                                    'record_kind': 'collaboration',
                                    'workflow_id': 'WF-1',
                                    'project_id': 'A'},
                   'operation_id': 'OP-14',
                   'expected_revision': 1,
                   'command': 'task.complete',
                   'payload': {'task_id': 'T1',
                               'assignment': {'assignment_id': 'ASG-1',
                                              'generation': 1,
                                              'definition_revision': 1},
                               'result': {'summary': '分析完成',
                                          'criterion_results': [{'criterion_index': 0,
                                                                 'outcome': 'satisfied',
                                                                 'explanation': '結果文件可讀',
                                                                 'evidence_ids': []}],
                                          'artifacts': [{'kind': 'document',
                                                         'ref': {'document_id': 'result',
                                                                 'revision': 1,
                                                                 'content_hash': 'sha256:0f33ae5f3694c08f7e75bda9711782603bebd4310ea8114e6e2224e4287d18e7'}}],
                                          'evidence': [],
                                          'limitations': []}}},
 'task.cancel': {'service_contract_version': 'workflow-board/collaboration/2',
                 'schema_version': '2.0',
                 'workflow_ref': {'store_id': 'board-local',
                                  'namespace': 'personal',
                                  'record_kind': 'collaboration',
                                  'workflow_id': 'WF-1',
                                  'project_id': 'A'},
                 'operation_id': 'OP-15',
                 'expected_revision': 1,
                 'command': 'task.cancel',
                 'payload': {'task_id': 'T1', 'assignment': None, 'reason': '不再交付此任務', 'handoff': None}},
 'decision.open': {'service_contract_version': 'workflow-board/collaboration/2',
                   'schema_version': '2.0',
                   'workflow_ref': {'store_id': 'board-local',
                                    'namespace': 'personal',
                                    'record_kind': 'collaboration',
                                    'workflow_id': 'WF-1',
                                    'project_id': 'A'},
                   'operation_id': 'OP-16',
                   'expected_revision': 1,
                   'command': 'decision.open',
                   'payload': {'decision_id': 'Q1',
                               'question': '採用哪個方案',
                               'options': ['A', 'B'],
                               'required_decider': {'kind': 'human'},
                               'blocks': {'task_ids': ['T1'], 'workflow_closure': False},
                               'basis': [{'document_id': 'plan',
                                          'revision': 1,
                                          'content_hash': 'sha256:ddba9bf9f8afcbc5a8271ff38d21fe3ec34114e00bfd1f249bb6f99d902deee2'}]}},
 'handoff.record': {'service_contract_version': 'workflow-board/collaboration/2',
                    'schema_version': '2.0',
                    'workflow_ref': {'store_id': 'board-local',
                                     'namespace': 'personal',
                                     'record_kind': 'collaboration',
                                     'workflow_id': 'WF-1',
                                     'project_id': 'A'},
                    'operation_id': 'OP-18',
                    'expected_revision': 1,
                    'command': 'handoff.record',
                    'payload': {'task_id': None,
                                'handoff': {'completed': '分析已完成',
                                            'remaining': '補充驗證',
                                            'next_step': '檢查既有結果',
                                            'artifact_refs': [{'kind': 'document',
                                                               'ref': {'document_id': 'plan',
                                                                       'revision': 1,
                                                                       'content_hash': 'sha256:ddba9bf9f8afcbc5a8271ff38d21fe3ec34114e00bfd1f249bb6f99d902deee2'}}],
                                            'blockers': [],
                                            'limitations': [],
                                            'next_actor_hint': None}}},
 'checkpoint.append': {'service_contract_version': 'workflow-board/collaboration/2',
                       'schema_version': '2.0',
                       'workflow_ref': {'store_id': 'board-local',
                                        'namespace': 'personal',
                                        'record_kind': 'collaboration',
                                        'workflow_id': 'WF-1',
                                        'project_id': 'A'},
                       'operation_id': 'OP-19',
                       'expected_revision': 1,
                       'command': 'checkpoint.append',
                       'payload': {'observation': '確認目前計畫與限制',
                                   'next_step': '接手任務',
                                   'document_refs': [{'document_id': 'plan',
                                                      'revision': 1,
                                                      'content_hash': 'sha256:ddba9bf9f8afcbc5a8271ff38d21fe3ec34114e00bfd1f249bb6f99d902deee2'}]}}}


PROJECT = {'store_id': 'board-local', 'namespace': 'personal', 'project_id': 'A'}
BINDING = {'adapter_id': 'workflow-board-v2', 'binding_id': 'selected-plugin',
           'binding_revision': 1, 'project_ref': PROJECT}
CAPABILITIES = {
    'service_contract_version': api.q.NATIVE_PROFILE, 'schema_version': api.q.SCHEMA,
    **PROJECT, 'commands': list(api.COMMANDS), 'queries': ['operation.get'],
    'limits': {'request_utf8_bytes': 300000, 'document_utf8_bytes': 256000,
               'record_utf8_bytes': 64000, 'context_utf8_bytes': 64000,
               'tasks_per_workflow': 100, 'decisions_per_workflow': 100,
               'context_page_items': 20, 'header_utf8_bytes': 16000},
    'contract_status': 'implemented'}
DIGEST = 'sha256:ed4e5ea09302c1ac581a55a11750fb756eaeaf72bffed3528284fd70a16cb6cf'
ACTOR = {'subject_id': 'agent', 'kind': 'agent', 'binding_id': 'server-binding'}


def prepare_request(name='workflow.create'):
    return {'contract_version': api.PROFILE, 'operation': 'board-command-prepare',
            'binding': copy.deepcopy(BINDING), 'capabilities': copy.deepcopy(CAPABILITIES),
            'command': copy.deepcopy(COMMAND_FIXTURES[name])}


def mcp(value, text=False):
    return {'content': [{'type': 'text', 'text': api.canonical(value).decode('utf-8')}]} if text else {'content': [], 'structuredContent': copy.deepcopy(value)}


def receipt(command, accepted=True):
    common = {'accepted': accepted, 'service_contract_version': api.q.NATIVE_PROFILE,
              'schema_version': api.q.SCHEMA, 'workflow_ref': copy.deepcopy(command['workflow_ref']),
              'operation_id': command['operation_id'], 'request_digest': DIGEST,
              'actor': copy.deepcopy(ACTOR)}
    if accepted:
        before = command['expected_revision']
        effects = [{'kind': 'workflow', 'id': command['workflow_ref']['workflow_id'], 'revision': before+1}]
        if command['command'] in ('plan.revise', 'document.append'):
            doc = command['payload']['plan' if command['command']=='plan.revise' else 'document']
            effects.insert(0, {'kind': 'document', 'id': doc['document_id'], 'revision': doc['expected_document_revision']+1})
        return {**common, 'before_revision': before, 'revision': before+1,
                'accepted_at': '2026-10-25T00:00:00.000Z', 'effects': effects}
    return {**common, 'expected_revision': command['expected_revision'], 'current_revision': 9,
            'recorded_at': '2026-10-25T00:00:00.000Z',
            'failure': {'error': 'revision_conflict', 'category': 'conflict',
                        'details': {'future': {'preserved': [1, '保留']}}}}


class BoardCommandTests(unittest.TestCase):
    def ok(self, response, outcome=None):
        self.assertEqual(response['status'], 'ok', response)
        self.assertEqual(response['bridge_effect'], 'none')
        if outcome is not None:
            self.assertEqual(response['command_outcome'], outcome, response)
        return response['result']

    def error(self, response, code=None, outcome='unknown'):
        self.assertNotEqual(response['status'], 'ok', response)
        self.assertEqual(response['bridge_effect'], 'none')
        self.assertEqual(response['command_outcome'], outcome, response)
        if code:
            self.assertEqual(response['error']['code'], code, response)

    def prepared(self, name='workflow.create'):
        return self.ok(api.execute(prepare_request(name)), 'not_dispatched')

    def after(self, prepared, native=None, operation='board-command-accept'):
        request = {'contract_version': api.PROFILE, 'operation': operation,
                   'binding': copy.deepcopy(prepared['binding']), 'prepared': copy.deepcopy(prepared)}
        request['mcp_result' if operation=='board-command-accept' else 'lookup_result'] = None if native is None else mcp(native)
        return request

    def test_all_eighteen_native_examples_prepare_exact_commands_and_recovery(self):
        self.assertEqual(set(COMMAND_FIXTURES), set(api.COMMANDS))
        for name in api.COMMANDS:
            with self.subTest(command=name):
                request = prepare_request(name)
                original = copy.deepcopy(request)
                prepared = self.ok(api.execute(request), 'not_dispatched')
                self.assertEqual(prepared['command'], request['command'])
                self.assertEqual(prepared['tool_name'], 'v2_'+name.replace('.', '_'))
                self.assertEqual(prepared['recovery_query']['payload'], {
                    'workflow_ref': request['command']['workflow_ref'], 'operation_id': request['command']['operation_id']})
                self.assertEqual(request, original)
                self.assertNotIn('request_digest', prepared)

    def test_capability_version_scope_limits_and_missing_command_fail_closed(self):
        for key, value in (('commands', []), ('queries', []), ('schema_version', '1.0'),
                           ('project_id', 'B'), ('store_id', 'other'), ('namespace', 'team'),
                           ('limits', {**CAPABILITIES['limits'], 'request_utf8_bytes': 999999})):
            request = prepare_request()
            request['capabilities'][key] = value
            self.error(api.execute(request), outcome='not_dispatched')
        request = prepare_request()
        del request['capabilities']['contract_status']
        self.error(api.execute(request), outcome='not_dispatched')

    def test_excluded_native_commands_and_legacy_scope_are_never_writers(self):
        for name in ('decision.resolve', 'project.create', 'project.rename', 'arbitrary.command'):
            request = prepare_request()
            request['command']['command'] = name
            self.error(api.execute(request), outcome='not_dispatched')
        request = prepare_request()
        request['binding']['project_ref']['project_id'] = 'legacy-personal'
        request['capabilities']['project_id'] = 'legacy-personal'
        request['command']['workflow_ref']['project_id'] = 'legacy-personal'
        self.error(api.execute(request), 'unsupported_profile', 'not_dispatched')

    def test_schema_valid_but_excluded_decision_and_project_commands_are_refused(self):
        request = prepare_request('workflow.start')
        command = request['command']
        command['command'] = 'decision.resolve'
        command['payload'] = {'decision_id':'D','expected_decision_revision':1,'basis':[],
                              'outcome':'waived','value':None,'reason':'Synthetic exclusion check'}
        api.validate('command',command)
        request['capabilities']['commands'].append('decision.resolve')
        self.error(api.execute(request),'unsupported_capability','not_dispatched')
        command = {**command, 'command':'project.create', 'project_ref':PROJECT,
                   'expected_revision':0,'payload':{'name':'Synthetic'}}
        del command['workflow_ref']
        api.validate('command',command)
        request['command'] = command
        self.error(api.execute(request),'unsupported_capability','not_dispatched')

    def test_native_schema_rejects_actor_owner_injection_and_nested_unknown_fields(self):
        for path in ((), ('payload',), ('payload','scope'), ('workflow_ref',)):
            request = prepare_request()
            obj = request['command']
            for key in path:
                obj = obj[key]
            obj['actor'] = ACTOR
            self.error(api.execute(request), 'invalid_native_schema', 'not_dispatched')
        request = prepare_request('task.claim')
        request['command']['payload']['session'] = {'session_id': 'session', 'actor': ACTOR}
        self.error(api.execute(request), 'invalid_native_schema', 'not_dispatched')
        request = prepare_request()
        request['command']['owner_id'] = 'fake-owner'
        self.error(api.execute(request), 'invalid_native_schema', 'not_dispatched')

    def test_unknown_missing_adapter_fields_and_binding_drift_are_rejected(self):
        for key in ('binding', 'capabilities', 'command'):
            request = prepare_request()
            del request[key]
            self.error(api.execute(request), outcome='not_dispatched')
        request = prepare_request()
        request['unexpected'] = True
        self.error(api.execute(request), outcome='not_dispatched')
        prepared = self.prepared()
        for key in ('tool_name', 'local_command_fingerprint', 'recovery_query', 'command'):
            request = self.after(prepared)
            del request['prepared'][key]
            self.error(api.execute(request))
        request = self.after(prepared)
        request['binding']['binding_revision'] = 2
        self.error(api.execute(request), 'binding_mismatch')
        request = self.after(prepared)
        request['prepared']['command']['payload']['title'] = 'changed without reprepare'
        self.error(api.execute(request), 'binding_mismatch')

    def test_strict_json_wire_numbers_unicode_duplicates_and_native_integer_types(self):
        for raw in (b'{"n":-0}', b'{"n":1.0}', b'{"n":1e0}', b'{"n":1E2}', b'{"n":NaN}',
                    b'{"n":9007199254740992}', b'{"n":1,"n":2}', b'{"n":"\\ud800"}', b'\xff'):
            with self.subTest(raw=raw), self.assertRaises(api.CommandError):
                api.decode(raw)
        for value in (True, 1.0, -1, 9007199254740992):
            request = prepare_request()
            request['command']['expected_revision'] = value
            self.error(api.execute(request), outcome='not_dispatched')
        self.assertEqual(api.decode(b'{"n":0}'), {'n': 0})

    def test_exact_utf8_document_and_native_request_byte_limits(self):
        request = prepare_request('document.append')
        request['command']['payload']['document']['content'] = '臺' * 85334
        self.error(api.execute(request), 'limit_exceeded', 'not_dispatched')
        request['command']['payload']['document']['content'] = 'x' * 256000
        self.ok(api.execute({**request, 'max_output_bytes': 400000}), 'not_dispatched')
        request = prepare_request('plan.revise')
        request['command']['payload']['plan']['content'] = 'x' * 256000
        request['command']['payload']['task_changes'] *= 4
        self.error(api.execute(request), outcome='not_dispatched')

    def test_direct_accepted_rejected_and_frozen_digest_confirmation(self):
        prepared = self.prepared()
        for accepted in (True, False):
            native = receipt(prepared['command'], accepted)
            result = self.ok(api.execute(self.after(prepared,native)), 'applied' if accepted else 'rejected')
            self.assertEqual(result['native_result'], native)
            self.assertEqual(result['prior_confirmation'], {
                'local_command_fingerprint': prepared['local_command_fingerprint'], 'request_digest': DIGEST})
            self.assertEqual(result['server_digest_verification'], 'host_correlated_not_recomputed')

    def test_direct_receipt_scope_operation_expected_revision_actor_digest_and_effects(self):
        prepared = self.prepared()
        native = receipt(prepared['command'])
        for key, value in (('workflow_ref', {**native['workflow_ref'], 'project_id': 'B'}),
                           ('operation_id', 'other'), ('before_revision', 1), ('revision', 3),
                           ('actor', {**ACTOR, 'owner_id': 'injected'}), ('request_digest', 'bad'),
                           ('effects', []), ('accepted_at', '2026-02-30T00:00:00.000Z')):
            self.error(api.execute(self.after(prepared, {**native, key:value})))
        rejected = receipt(prepared['command'], False)
        self.error(api.execute(self.after(prepared, {**rejected, 'expected_revision': 1})), 'receipt_mismatch')

    def test_document_effect_must_match_original_identity_and_revision(self):
        prepared = self.prepared('document.append')
        native = receipt(prepared['command'])
        self.ok(api.execute(self.after(prepared,native)), 'applied')
        for key, value in (('id','another'), ('revision', 99)):
            changed = copy.deepcopy(native)
            changed['effects'][0][key] = value
            self.error(api.execute(self.after(prepared,changed)), 'receipt_mismatch')
        native['effects'] = native['effects'][1:]
        self.error(api.execute(self.after(prepared,native)), 'receipt_mismatch')

    def test_task_effect_must_match_task_and_definition_from_command(self):
        prepared = self.prepared('task.progress')
        native = receipt(prepared['command'])
        payload = prepared['command']['payload']
        effect = {'kind':'task','id':payload['task_id'],'revision':payload['assignment']['definition_revision']}
        native['effects'].insert(0,effect)
        self.ok(api.execute(self.after(prepared,native)),'applied')
        for key,value in (('id','another-task'),('revision',99)):
            changed = copy.deepcopy(native)
            changed['effects'][0][key] = value
            self.error(api.execute(self.after(prepared,changed)),'receipt_mismatch')

    def test_decision_and_claim_effects_match_inputs_without_inventing_generated_ids(self):
        prepared = self.prepared('decision.open')
        native = receipt(prepared['command'])
        effect = {'kind':'decision','id':prepared['command']['payload']['decision_id'],'revision':1}
        native['effects'].insert(0,effect)
        self.ok(api.execute(self.after(prepared,native)),'applied')
        for key,value in (('id','other-decision'),('revision',2)):
            changed = copy.deepcopy(native)
            changed['effects'][0][key] = value
            self.error(api.execute(self.after(prepared,changed)),'receipt_mismatch')
        prepared = self.prepared('task.claim')
        native = receipt(prepared['command'])
        payload = prepared['command']['payload']
        native['effects'].insert(0,{'kind':'task','id':payload['task_id'],
                                    'revision':payload['expected_definition_revision']})
        self.error(api.execute(self.after(prepared,native)),'receipt_mismatch')
        native['effects'].insert(0,{'kind':'assignment','id':'server-generated-id','revision':7})
        self.ok(api.execute(self.after(prepared,native)),'applied')

    def test_lookup_without_prior_confirmation_only_observes_and_requires_original_replay(self):
        prepared = self.prepared()
        command = prepared['command']
        for accepted in (True,False):
            native = {'outcome':'accepted' if accepted else 'rejected','receipt':receipt(command,accepted)}
            result = self.ok(api.execute(self.after(prepared,native,'board-command-reconcile')), 'unknown')
            self.assertEqual(result['observed_outcome'], native['outcome'])
            self.assertTrue(result['requires_original_replay'])
            self.assertEqual(result['replay'], {'tool_name':prepared['tool_name'],'command':command})
            replay = self.ok(api.execute(self.after(prepared,native['receipt'])), 'applied' if accepted else 'rejected')
            self.assertFalse(replay['requires_original_replay'])

    def test_verified_same_fingerprint_digest_lookup_can_finalize_and_cross_payload_cannot(self):
        prepared = self.prepared()
        native = receipt(prepared['command'])
        confirmation = self.ok(api.execute(self.after(prepared,native)))['prior_confirmation']
        request = self.after(prepared, {'outcome':'accepted','receipt':native}, 'board-command-reconcile')
        request['prior_confirmation'] = confirmation
        self.ok(api.execute(request), 'applied')
        request['prior_confirmation'] = {**confirmation, 'request_digest':'sha256:'+'0'*64}
        self.error(api.execute(request), 'digest_mismatch')
        changed = prepare_request()
        changed['command']['payload']['title'] = 'another payload with same IDs'
        changed_prepared = self.ok(api.execute(changed))
        request = self.after(changed_prepared, {'outcome':'accepted','receipt':native}, 'board-command-reconcile')
        request['prior_confirmation'] = confirmation
        self.error(api.execute(request), 'fingerprint_mismatch')
        request.pop('prior_confirmation')
        self.ok(api.execute(request), 'unknown')

    def test_reconcile_builds_original_query_and_unknown_results_remain_unknown(self):
        prepared = self.prepared()
        request = self.after(prepared,operation='board-command-reconcile')
        del request['lookup_result']
        result = self.ok(api.execute(request),'unknown')
        self.assertEqual(result['recovery'], {'tool_name':'v2_operation_get','query':prepared['recovery_query']})
        command = prepared['command']
        unknown = {'outcome':'unknown','workflow_ref':command['workflow_ref'],'operation_id':command['operation_id']}
        result = self.ok(api.execute(self.after(prepared,unknown,'board-command-reconcile')),'unknown')
        self.assertEqual(result['native_result'],unknown)
        unknown['workflow_ref'] = {**unknown['workflow_ref'],'workflow_id':'different'}
        self.error(api.execute(self.after(prepared,unknown,'board-command-reconcile')),'receipt_mismatch')

    def test_payload_conflict_auth_and_storage_faults_are_not_durable_rejection(self):
        prepared = self.prepared()
        for code,category in (('operation_payload_conflict','conflict'),('forbidden','forbidden'),
                              ('signin_required','unauthenticated'),('storage_unavailable','unavailable')):
            native = {'error':code,'category':category,'details':{'future':[1,'保留']}}
            request = self.after(prepared,native)
            request['mcp_result']['isError'] = True
            response = api.execute(request)
            self.error(response,'remote_error')
            self.assertEqual(response['result']['native_result'],native)
        self.ok(api.execute(self.after(prepared)), 'unknown')

    def test_observed_host_annotation_preserves_native_fault_and_durable_rejection(self):
        prepared = self.prepared()
        fault = {'error':'operation_payload_conflict','category':'conflict','details':{}}
        request = self.after(prepared,fault)
        request['mcp_result'] = mcp(fault,True)
        request['mcp_result'].update({'structuredContent':{**fault,'error_code':'INVALID_ARGUMENT'},'isError':True})
        original = copy.deepcopy(request)
        response = api.execute(request)
        self.error(response,'remote_error')
        self.assertEqual(response['result']['native_result'],fault)
        self.assertEqual(request,original)
        prepared = self.prepared('plan.revise')
        native = receipt(prepared['command'],False)
        native['current_revision'] = native['expected_revision']
        native['failure'] = {'error':'document_role_conflict','category':'conflict','details':{}}
        request = self.after(prepared,native)
        request['mcp_result'] = mcp(native,True)
        request['mcp_result'].update({'structuredContent':{**native,'error_code':'INVALID_ARGUMENT'},'isError':True})
        original = copy.deepcopy(request)
        result = self.ok(api.execute(request),'rejected')
        self.assertEqual(result['native_result'],native)
        self.assertEqual(request,original)
        del request['mcp_result']['structuredContent']['error_code']
        self.ok(api.execute(request),'rejected')

    def test_host_annotation_is_exact_and_never_masks_native_disagreement(self):
        prepared = self.prepared()
        native = receipt(prepared['command'],False)
        request = self.after(prepared,native)
        request['mcp_result'] = mcp(native,True)
        request['mcp_result'].update({'structuredContent':{**native,'error_code':'INVALID_ARGUMENT'},'isError':True})
        for value in ('OTHER',1,True,None):
            changed = copy.deepcopy(request)
            changed['mcp_result']['structuredContent']['error_code'] = value
            self.error(api.execute(changed),'invalid_transport')
        for change in ('success-flag','extra-field','native-mismatch','text-annotation','no-text','wrong-location'):
            changed = copy.deepcopy(request)
            transport = changed['mcp_result']
            if change=='success-flag':
                transport['isError'] = False
            elif change=='extra-field':
                transport['structuredContent']['host_extra'] = 'must not strip'
            elif change=='native-mismatch':
                transport['structuredContent']['current_revision'] = 8
            elif change=='text-annotation':
                transport['content'] = mcp({**native,'error_code':'INVALID_ARGUMENT'},True)['content']
            elif change=='wrong-location':
                transport['error_code'] = transport['structuredContent'].pop('error_code')
            else:
                transport['content'] = []
            self.error(api.execute(changed),'invalid_transport')

    def test_error_flag_accepted_receipt_and_wrong_rejected_receipt_remain_unknown(self):
        prepared = self.prepared()
        for accepted in (True,False):
            native = receipt(prepared['command'],accepted)
            if not accepted:
                native['operation_id'] = 'another-operation'
            request = self.after(prepared,native)
            request['mcp_result'] = mcp(native,True)
            request['mcp_result'].update({'structuredContent':{**native,'error_code':'INVALID_ARGUMENT'},'isError':True})
            self.error(api.execute(request),'invalid_transport' if accepted else 'receipt_mismatch')

    def test_malformed_mcp_dual_representations_and_wire_numbers_remain_unresolved(self):
        prepared = self.prepared()
        native = receipt(prepared['command'])
        for malformed in ({}, {'content': []}, {'content': [],'structuredContent':None},
                          {'content': [],'structuredContent':native,'isError':1},
                          {'content':[{'type':'text','text':'{}'},{'type':'text','text':'{}'}]},
                          {'content':[{'type':'text','text':'{"n":-0}'}]},
                          {'content':[{'type':'image','data':'bad'}]}):
            request = self.after(prepared)
            request['mcp_result'] = malformed
            self.error(api.execute(request))
        request = self.after(prepared,native)
        request['mcp_result']['content'] = mcp(native,True)['content']
        self.ok(api.execute(request),'applied')
        changed = copy.deepcopy(native)
        changed['request_digest']='sha256:'+'1'*64
        request['mcp_result']['content']=mcp(changed,True)['content']
        self.error(api.execute(request),'invalid_transport')

    def test_postdispatch_output_overflow_and_invalid_input_never_claim_failed_write(self):
        prepared = self.prepared()
        native = receipt(prepared['command'],False)
        native['failure']['details']['large'] = 'x'*70000
        request = self.after(prepared,native)
        response = api.execute(request)
        self.error(response,'limit_exceeded')
        self.assertNotIn('result',response)
        request['max_output_bytes'] = 100000
        self.assertEqual(self.ok(api.execute(request),'rejected')['native_result'],native)
        request['max_output_bytes'] = True
        self.error(api.execute(request))
        self.error(api.execute({'contract_version':api.PROFILE,'operation':'board-command-accept'}))

    def test_prepare_accept_reconcile_never_dispatch_or_lookup_credentials(self):
        prepared = self.prepared()
        native = receipt(prepared['command'])
        original = copy.deepcopy(prepared)
        with patch('socket.socket',side_effect=AssertionError('no network')), \
             patch('subprocess.Popen',side_effect=AssertionError('no process')), \
             patch('builtins.open',side_effect=AssertionError('no journal')), \
             patch('os.getenv',side_effect=AssertionError('no ambient credential')):
            self.ok(api.execute(prepare_request()))
            self.ok(api.execute(self.after(prepared,native)))
            self.ok(api.execute(self.after(prepared,operation='board-command-reconcile')))
        self.assertEqual(prepared,original)

    def test_isolated_cli_declared_closure_missing_runtime_dependency_and_schema_drift(self):
        members = ('tools/board-command.py','tools/workflow_records/board_command.py',
                   'tools/workflow_records/board_query.py','schemas/board-collaboration-v2.schema.json')
        with tempfile.TemporaryDirectory(prefix='board-command-cli-') as directory:
            target=Path(directory)
            for member in members:
                path=target/member
                path.parent.mkdir(parents=True,exist_ok=True)
                shutil.copyfile(PACKAGE/member,path)
            def launch(value,site=True):
                args=[sys.executable,'-I','-B']
                if not site:
                    args.append('-S')
                return subprocess.run([*args,str(target/'tools/board-command.py'),'--activate','--request','-'],
                                      input=api.encode(value),capture_output=True,cwd=target,timeout=20)
            process=launch(prepare_request())
            self.assertEqual((process.returncode,process.stderr),(0,b''))
            prepared=self.ok(json.loads(process.stdout))
            process=launch(self.after(prepared,receipt(prepared['command'])))
            self.assertEqual((process.returncode,process.stderr),(0,b''))
            self.ok(json.loads(process.stdout),'applied')
            process=launch(prepare_request(),False)
            self.assertEqual((process.returncode,process.stderr),(1,b''))
            self.assertEqual(json.loads(process.stdout)['status'],'unavailable')
            schema=target/'schemas/board-collaboration-v2.schema.json'
            schema.write_bytes(schema.read_bytes()+b' ')
            process=launch(prepare_request())
            self.assertEqual((process.returncode,process.stderr),(1,b''))
            self.assertEqual(json.loads(process.stdout)['status'],'unavailable')
            self.assertFalse(list(target.rglob('__pycache__')))


if __name__ == '__main__':
    unittest.main()
