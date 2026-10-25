"""Authored fixtures for the two project-scoped workflow transport contracts.

These assert schema boundaries, not transport execution or native hash equality.
The replica schema is definitions-only: validate its selected $defs explicitly.
"""
from copy import deepcopy
import unittest

from schemas.schema_support import SHA, WORKFLOW_CONTRACTS, changed, validator


PROJECT = {"store_id": "board", "namespace": "personal", "project_id": "A"}
WORKFLOW = {**PROJECT, "record_kind": "collaboration", "workflow_id": "WF-1"}
DIGEST = "sha256:" + SHA


def contract(name, definition):
    return validator(WORKFLOW_CONTRACTS[name], "#/$defs/" + definition)


def board_start():
    return {"service_contract_version": "workflow-board/collaboration/2", "schema_version": "2.0",
            "workflow_ref": deepcopy(WORKFLOW), "operation_id": "start-1", "expected_revision": 1,
            "command": "workflow.start", "payload": {}}


def replica_commands():
    common = {"service_contract_version": "workflow-board/source-replica/1", "schema_version": "1.0",
              "project_ref": deepcopy(PROJECT), "operation_id": "replica-1", "expected_revision": 0}
    identity = {"source_id": "source-1", "workflow_id": "unit-1", "source_revision": "snapshot-1"}
    manifest = {"source": {"kind": "archive-workflow", "unknown": ["retained"]},
                "workflow": {"id": "unit-1", "title": "歷史工作流程", "status": "closed"},
                "files": [{"path": "plan.md", "mode": "100644", "size": 1, "sha256": DIGEST}]}
    return [
        {**common, "command": "replica.begin", "payload": {**identity, "manifest_hash": DIGEST, "manifest": manifest}},
        {**common, "command": "replica.chunk.put", "payload": {**identity, "chunks": [
            {"path": "plan.md", "index": 0, "content_base64": "YQ==", "chunk_hash": DIGEST}]}},
        {**common, "command": "replica.activate", "payload": {**identity, "manifest_hash": DIGEST}},
    ]


class WorkflowContractSchemaTests(unittest.TestCase):
    def test_board_commands_require_versioned_project_identity_and_closed_payloads(self):
        selected = contract("board-collaboration-v2", "command")
        good = board_start()
        selected.validate(good)
        project = {key: value for key, value in good.items() if key != "workflow_ref"}
        project.update(project_ref=deepcopy(PROJECT), command="project.create",
                       expected_revision=0, payload={"name": "專案"})
        selected.validate(project)
        self.assertFalse(selected.is_valid({**project, "expected_revision": 1}))
        missing = deepcopy(good)
        del missing["workflow_ref"]["project_id"]
        bad = [missing, {**good, "undeclared": True},
               changed(good, ("service_contract_version",), "workflow-board/collaboration/1"),
               changed(good, ("schema_version",), "1.0"),
               changed(good, ("workflow_ref", "namespace"), "team"),
               changed(good, ("workflow_ref", "workflow_id"), "__proto__"),
               changed(good, ("payload",), {"reason": "not accepted by start"})]
        for request in bad:
            with self.subTest(request=request):
                self.assertFalse(selected.is_valid(request))
        for revision in (-1, True, 1.5, 9007199254740992):
            with self.subTest(revision=revision):
                self.assertFalse(selected.is_valid({**good, "expected_revision": revision}))

    def test_board_context_queries_keep_scope_and_bounded_paging(self):
        selected = contract("board-collaboration-v2", "query")
        good = {"service_contract_version": "workflow-board/collaboration/2", "schema_version": "2.0",
                "query": "workflow.context", "payload": {"workflow_ref": deepcopy(WORKFLOW), "limit": 20}}
        selected.validate(good)
        for path, value in [(('payload', 'limit'), 0), (('payload', 'limit'), 21),
                            (('payload', 'workflow_ref'), {key: value for key, value in WORKFLOW.items() if key != 'project_id'}),
                            (('query',), 'workflow.unregistered')]:
            with self.subTest(path=path, value=value):
                self.assertFalse(selected.is_valid(changed(good, path, value)))

    def test_replica_command_variants_accept_archive_metadata_and_reject_missing_identity(self):
        selected = contract("source-replica-v1", "command")
        for good in replica_commands():
            with self.subTest(command=good['command']):
                selected.validate(good)
                for key in ('project_ref', 'operation_id', 'expected_revision'):
                    bad = deepcopy(good)
                    del bad[key]
                    self.assertFalse(selected.is_valid(bad))
                self.assertFalse(selected.is_valid({**good, 'undeclared': True}))
                self.assertFalse(selected.is_valid({**good, 'schema_version': '2.0'}))
                self.assertFalse(selected.is_valid(changed(good, ('project_ref', 'project_id'), 'constructor')))
                self.assertFalse(selected.is_valid(changed(good, ('payload', 'source_id'), '__proto__')))

    def test_replica_manifest_and_chunk_limits_are_enforced_at_the_selected_definition(self):
        selected = contract("source-replica-v1", "command")
        begin, chunk, _ = replica_commands()
        cases = [changed(begin, ('payload', 'manifest', 'files', 0, 'mode'), 'regular'),
                 changed(begin, ('payload', 'manifest', 'files', 0, 'size'), 16777217),
                 changed(begin, ('payload', 'manifest', 'files', 0, 'sha256'), 'a' * 64),
                 changed(chunk, ('payload', 'chunks'), []),
                 changed(chunk, ('payload', 'chunks'), chunk['payload']['chunks'] * 33),
                 changed(chunk, ('payload', 'chunks', 0, 'index'), -1),
                 changed(chunk, ('payload', 'chunks', 0, 'content_base64'), 'A' * 65537),
                 changed(chunk, ('payload', 'chunks', 0, 'chunk_hash'), 'sha256:' + 'A' * 64)]
        for index, bad in enumerate(cases):
            with self.subTest(case=index):
                self.assertFalse(selected.is_valid(bad))
        boundary = changed(chunk, ('payload', 'chunks'), chunk['payload']['chunks'] * 32)
        selected.validate(boundary)

    def test_replica_query_and_receipt_keep_project_and_rejection_semantics(self):
        query = {'service_contract_version': 'workflow-board/source-replica/1', 'schema_version': '1.0',
                 'project_ref': deepcopy(PROJECT), 'query': 'replica.capabilities', 'payload': {}}
        query_schema = contract('source-replica-v1', 'query')
        query_schema.validate(query)
        self.assertFalse(query_schema.is_valid({key: value for key, value in query.items() if key != 'project_ref'}))
        receipt = {'accepted': True, 'project_ref': deepcopy(PROJECT), 'operation_id': 'replica-1',
                   'command': 'replica.activate', 'request_digest': DIGEST, 'expected_revision': 0, 'revision': 1,
                   'source_id': 'source-1', 'workflow_id': 'unit-1', 'source_revision': 'snapshot-1', 'error': None}
        selected = contract('source-replica-v1', 'receipt')
        selected.validate(receipt)
        selected.validate({**receipt, 'accepted': False, 'error': 'revision_conflict', 'revision': 0})
        for bad in ({**receipt, 'accepted': False}, {**receipt, 'error': 'unexpected'},
                    {**receipt, 'extra': True}, {**receipt, 'request_digest': 'unbound'},
                    changed(receipt, ('project_ref',), {'store_id': 'board', 'namespace': 'personal'})):
            with self.subTest(receipt=bad):
                self.assertFalse(selected.is_valid(bad))


if __name__ == '__main__':
    unittest.main()
