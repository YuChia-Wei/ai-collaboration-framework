"""Bounded Board query bridge contracts; synthetic data, no live transport.

Native field shapes are sourced from Board CollaborationV2/schema.json at
b100c9f9bd09b2a1c125c8b511f06defeb29c556. The frozen UTF-8 digest values below
come from CollaborationV1/vectors.json, inherited unchanged by V2. Tests and
consumer runtime have no dependency on a Board checkout.
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
TOOLS = ROOT / "src/skills/workflow-board-experimental/tools"
spec = importlib.util.spec_from_file_location("board_query_test_runtime", TOOLS / "workflow_records/board_query.py")
api = importlib.util.module_from_spec(spec)
spec.loader.exec_module(api)
PROJECT = {"store_id": "local", "namespace": "personal", "project_id": "A"}
WORKFLOW = {**PROJECT, "record_kind": "collaboration", "workflow_id": "WF"}
BINDING = {"adapter_id": "workflow-board-v2", "binding_id": "selected-plugin",
           "binding_revision": 1, "project_ref": PROJECT}
DOC = {"document_id": "plan", "revision": 1,
       "content_hash": "sha256:3c52599edebec205f035e0ed96ad30f1dacaa9dde259c1f76dc8d52b5652938c"}
PROFILE = {"service_contract_version": api.NATIVE_PROFILE, "schema_version": api.SCHEMA}
DIGEST = "sha256:ed4e5ea09302c1ac581a55a11750fb756eaeaf72bffed3528284fd70a16cb6cf"


def query(name, **payload):
    return {**PROFILE, "query": name, "payload": payload}


def request(name="project.read", **payload):
    return {"contract_version": api.PROFILE, "operation": "board-query-prepare",
            "binding": copy.deepcopy(BINDING), "query": query(name, **(payload or {"project_ref": copy.deepcopy(PROJECT)}))}


def mcp(value, text=False):
    return {"content": [{"type": "text", "text": json.dumps(value, ensure_ascii=False)}]} if text else {"content": [], "structuredContent": value}


def project(scope=PROJECT):
    return {"project_ref": copy.deepcopy(scope), "name": "專案", "revision": 1,
            "workflow_contract": api.NATIVE_PROFILE}


def empty_page():
    return {"items": [], "total": 0, "has_more": False, "cursor": None}


def context():
    return {**PROFILE, "workflow_ref": copy.deepcopy(WORKFLOW), "revision": 3,
            "workflow": {"plan": copy.deepcopy(DOC)}, "tasks": empty_page(),
            "decisions": empty_page(), "handoffs": empty_page(),
            "missing": [{"kind": "input", "ref": "source:unknown", "reason": "not supplied", "future": 7}],
            "extension": {"unknown": [None, "保留"]}}


def receipt(project_target=False, accepted=True):
    common = {"accepted": accepted, "operation_id": "same-operation", "request_digest": DIGEST,
              "extension": {"future": [1, "保留"]}}
    if project_target:
        return {**common, "project_ref": copy.deepcopy(PROJECT), "expected_revision": 0,
                "revision": 1 if accepted else 0, "error": None if accepted else "revision_conflict"}
    common.update({**PROFILE, "workflow_ref": copy.deepcopy(WORKFLOW),
                   "actor": {"subject_id": "agent", "kind": "agent", "binding_id": "selected-plugin"}})
    if accepted:
        return {**common, "before_revision": 0, "revision": 1,
                "accepted_at": "2026-10-25T00:00:00.000Z", "effects": [{"kind": "workflow", "id": "WF", "revision": 1}]}
    return {**common, "expected_revision": 1, "current_revision": None,
            "recorded_at": "2026-10-25T00:00:00.000Z",
            "failure": {"error": "not_found", "category": "not_found", "details": {"retained": True}}}


class BoardQueryTests(unittest.TestCase):
    def ok(self, value):
        self.assertEqual(value["status"], "ok", value)
        self.assertEqual(value["mutation_state"], "none")
        return value["result"]

    def error(self, value, code=None):
        self.assertEqual(value["status"], "error", value)
        self.assertEqual(value["mutation_state"], "none")
        if code:
            self.assertEqual(value["error"]["code"], code, value)

    def accept_request(self, prepared, native, text=False):
        return {"contract_version": api.PROFILE, "operation": "board-query-accept",
                "binding": copy.deepcopy(prepared["binding"]), "prepared": copy.deepcopy(prepared),
                "mcp_result": mcp(copy.deepcopy(native), text)}

    def accept(self, prepared, native, text=False):
        return api.execute(self.accept_request(prepared, native, text))

    def prepared(self, name="project.read", **payload):
        return self.ok(api.execute(request(name, **payload)))

    def test_all_eleven_queries_prepare_exact_native_envelopes_and_symbols(self):
        cases = {
            "project.list": {"store_id": "local", "namespace": "personal", "limit": 100, "cursor": None},
            "project.read": {"project_ref": PROJECT},
            "project.operation.get": {"project_ref": PROJECT, "operation_id": "same-operation"},
            "capabilities": PROJECT,
            "workflow.find": {**PROJECT, "q": "", "limit": 50, "cursor": "opaque/unchanged=="},
            "workflow.context": {"workflow_ref": WORKFLOW, "limit": 20},
            "context.page": {"workflow_ref": WORKFLOW, "section": "tasks", "cursor": "opaque/unchanged=="},
            "task.read": {"workflow_ref": WORKFLOW, "task_id": "T", "definition_revision": 1, "at_revision": 3},
            "decision.read": {"workflow_ref": WORKFLOW, "decision_id": "D", "decision_revision": 1, "at_revision": 3},
            "document.read": {"workflow_ref": WORKFLOW, "document_ref": DOC},
            "operation.get": {"workflow_ref": WORKFLOW, "operation_id": "same-operation"}}
        self.assertEqual(set(cases), set(api.QUERIES))
        for name, payload in cases.items():
            with self.subTest(query=name):
                value = request(name, **payload)
                if name == "context.page":
                    value["expected_snapshot_revision"] = 3
                before = copy.deepcopy(value)
                prepared = self.ok(api.execute(value))
                self.assertEqual(prepared["query"], value["query"])
                self.assertEqual(prepared["tool_name"], "v2_" + name.replace(".", "_"))
                self.assertEqual(value, before)

    def test_writes_legacy_and_other_profiles_are_refused(self):
        for name in ("task.claim", "project.create", "workflow.create", "project.legacy.preview", "read"):
            self.error(api.execute(request(name, project_ref=PROJECT)), "unsupported_capability")
        for key, value in (("service_contract_version", "workflow-board/collaboration/1"), ("schema_version", "1.0")):
            changed = request()
            changed["query"][key] = value
            self.error(api.execute(changed))
        self.error(api.execute(request("workflow.context", workflow_ref={**WORKFLOW, "project_id": "legacy-personal"}, limit=1)))
        changed = request()
        changed["binding"]["project_ref"]["project_id"] = "legacy-personal"
        changed["query"] = query("workflow.context", workflow_ref={**WORKFLOW, "project_id": "legacy-personal"}, limit=1)
        self.error(api.execute(changed), "unsupported_profile")

    def test_unknown_or_missing_envelope_binding_and_query_fields_fail(self):
        value = request()
        for selected in (value, value["binding"], value["query"], value["query"]["payload"]):
            for key in list(selected):
                changed = copy.deepcopy(value)
                target = changed if selected is value else changed["binding"] if selected is value["binding"] else changed["query"] if selected is value["query"] else changed["query"]["payload"]
                del target[key]
                self.error(api.execute(changed))
        for path in ((), ("binding",), ("query",), ("query", "payload")):
            changed = copy.deepcopy(value)
            target = changed
            for key in path:
                target = target[key]
            target["token"] = "not-a-secret-fixture"
            self.error(api.execute(changed))

    def test_native_identifiers_accept_160_and_refuse_reserved_or_unsafe(self):
        for invalid in ("", "x" * 161, "constructor", "prototype", "__proto__", "臺灣", "x/y", " x", 1, True):
            changed = request()
            changed["binding"]["project_ref"]["project_id"] = invalid
            self.error(api.execute(changed))
        changed = request()
        for obj in (changed["binding"]["project_ref"], changed["query"]["payload"]["project_ref"]):
            obj["project_id"] = "x" * 160
        self.ok(api.execute(changed))

    def test_numeric_booleans_and_unsafe_revisions_are_not_integers(self):
        for invalid in (True, False, 0, -1, 1.0, 9007199254740992, "1"):
            changed = request()
            changed["binding"]["binding_revision"] = invalid
            self.error(api.execute(changed))
            self.error(api.execute(request("task.read", workflow_ref=WORKFLOW, task_id="T", definition_revision=invalid, at_revision=1)))
        self.error(api.execute(request("workflow.context", workflow_ref=WORKFLOW, limit=True)))

    def test_request_scope_checks_every_project_and_workflow_component(self):
        for key, value in (("store_id", "other"), ("project_id", "B"), ("namespace", "team")):
            self.error(api.execute(request("workflow.context", workflow_ref={**WORKFLOW, key: value}, limit=1)))
        self.error(api.execute(request("workflow.context", workflow_ref={**WORKFLOW, "record_kind": "legacy"}, limit=1)))
        self.error(api.execute(request("capabilities", **{**PROJECT, "project_id": "B"})), "scope_mismatch")

    def test_prepared_binding_revision_tool_and_native_query_are_revalidated(self):
        prepared = self.prepared()
        original = self.accept_request(prepared, project())
        for key, value in (("binding_revision", 2), ("binding_revision", True), ("binding_id", "another")):
            changed = copy.deepcopy(original)
            changed["prepared"]["binding"][key] = value
            self.error(api.execute(changed))
        changed = copy.deepcopy(original)
        changed["prepared"]["tool_name"] = "v2_project_create"
        self.error(api.execute(changed), "binding_mismatch")
        changed = copy.deepcopy(original)
        changed["prepared"]["query"]["payload"]["project_ref"]["project_id"] = "B"
        self.error(api.execute(changed), "scope_mismatch")
        changed = copy.deepcopy(original)
        changed["unexpected"] = 1
        self.error(api.execute(changed))

    def test_project_results_preserve_extensions_and_reject_same_id_in_another_scope(self):
        prepared = self.prepared()
        native = {**project(), "future": {"status": "unknown", "values": [1, "保留"]}}
        self.assertEqual(self.ok(self.accept(prepared, native)), native)
        for key, value in (("store_id", "other"), ("project_id", "B")):
            changed = copy.deepcopy(native)
            changed["project_ref"][key] = value
            self.error(self.accept(prepared, changed), "scope_mismatch")
        self.error(self.accept(prepared, {**native, "revision": True}))
        self.error(self.accept(prepared, {**native, "workflow_contract": "workflow-board/collaboration/1"}), "unsupported_profile")

    def test_registry_list_is_store_scoped_and_preserves_legacy_project(self):
        prepared = self.prepared("project.list", store_id="local", namespace="personal", limit=3, cursor=None)
        legacy = project({**PROJECT, "project_id": "legacy-personal"})
        legacy["workflow_contract"] = "workflow-board/collaboration/1"
        native = {"items": [legacy, project(), project({**PROJECT, "project_id": "B"})], "has_more": False, "cursor": None}
        self.assertEqual(self.ok(self.accept(prepared, native)), native)
        native["items"][1]["project_ref"]["store_id"] = "other"
        self.error(self.accept(prepared, native), "scope_mismatch")

    def test_all_receipt_families_and_outcomes_preserve_native_data(self):
        for project_target in (True, False):
            name, target = ("project.operation.get", "project_ref") if project_target else ("operation.get", "workflow_ref")
            ref = PROJECT if project_target else WORKFLOW
            prepared = self.prepared(name, **{target: ref, "operation_id": "same-operation"})
            for outcome in ("accepted", "rejected", "unknown"):
                with self.subTest(target=target, outcome=outcome):
                    native = {"outcome": outcome, target: copy.deepcopy(ref), "operation_id": "same-operation"} if outcome == "unknown" else {"outcome": outcome, "receipt": receipt(project_target, outcome == "accepted")}
                    accepted = self.accept(prepared, native)
                    self.assertEqual(self.ok(accepted), native)
                    self.assertEqual(accepted["mutation_state"], "none")
                    changed = copy.deepcopy(native)
                    record = changed if outcome == "unknown" else changed["receipt"]
                    record[target]["project_id"] = "B"
                    self.error(self.accept(prepared, changed), "scope_mismatch")
                    record[target]["project_id"] = "A"
                    record["operation_id"] = "different"
                    self.error(self.accept(prepared, changed), "scope_mismatch")

    def test_receipt_kind_outcome_revision_and_digest_mismatches_fail(self):
        prepared = self.prepared("operation.get", workflow_ref=WORKFLOW, operation_id="same-operation")
        self.error(self.accept(prepared, {"outcome": "accepted", "receipt": receipt(True)}))
        for key, value in (("accepted", False), ("revision", True), ("revision", 3), ("request_digest", "bad"), ("schema_version", "1.0")):
            native = {"outcome": "accepted", "receipt": receipt()}
            native["receipt"][key] = value
            self.error(self.accept(prepared, native))
        self.error(self.accept(prepared, {"outcome": "unknown", "workflow_ref": WORKFLOW, "operation_id": "same-operation", "receipt": receipt()}))

    def test_document_exact_utf8_frozen_vectors_and_revision_checks(self):
        vectors = [("臺灣\n", DOC["content_hash"]),
                   ("臺灣\r\n", "sha256:610946516c6a927adc82f38b54f2d767cfaffd7d2378e180c6910a52d009c7f3"),
                   ("", "sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855")]
        for content, expected_hash in vectors:
            ref = {**DOC, "content_hash": expected_hash}
            prepared = self.prepared("document.read", workflow_ref=WORKFLOW, document_ref=ref)
            native = {"workflow_ref": WORKFLOW, "ref": ref, "content": content, "future": ["保留"]}
            self.assertEqual(self.ok(self.accept(prepared, native, text=True)), native)
            self.error(self.accept(prepared, {**native, "content": content + "x"}), "hash_mismatch")
            self.error(self.accept(prepared, {**native, "ref": {**ref, "revision": 2}}), "revision_mismatch")
            self.error(self.accept(prepared, {**native, "ref": {**ref, "revision": True}}))

    def test_task_and_decision_fixed_snapshot_identity_and_revision(self):
        task = self.prepared("task.read", workflow_ref=WORKFLOW, task_id="T", definition_revision=2, at_revision=3)
        native = {"workflow_ref": WORKFLOW, "snapshot_revision": 3, "summary": {"id": "T", "definition_revision": 2}, "definition": {"id": "T", "future": 1}, "result": None}
        self.assertEqual(self.ok(self.accept(task, native)), native)
        for key, value in (("snapshot_revision", 4), ("snapshot_revision", True), ("workflow_ref", {**WORKFLOW, "workflow_id": "other"})):
            self.error(self.accept(task, {**native, key: value}))
        self.error(self.accept(task, {**native, "summary": {"id": "T", "definition_revision": 1}}), "revision_mismatch")
        decision = self.prepared("decision.read", workflow_ref=WORKFLOW, decision_id="D", decision_revision=2, at_revision=3)
        native = {"workflow_ref": WORKFLOW, "snapshot_revision": 3, "decision": {"id": "D", "revision": 2}, "resolution": None, "options": ["retain"]}
        self.assertEqual(self.ok(self.accept(decision, native)), native)
        self.error(self.accept(decision, {**native, "decision": {"id": "D", "revision": 1}}), "revision_mismatch")

    def test_context_missing_cursor_and_unknown_extensions_preserved(self):
        prepared = self.prepared("workflow.context", workflow_ref=WORKFLOW, limit=2)
        native = context()
        native["tasks"] = {"items": [{"id": "T", "definition_revision": 1, "plan_basis": DOC, "future": [1]}], "total": 2, "has_more": True, "cursor": "opaque/+=="}
        self.assertEqual(self.ok(self.accept(prepared, native)), native)
        for key, value in (("revision", True), ("workflow_ref", {**WORKFLOW, "project_id": "B"}), ("schema_version", "1.0")):
            self.error(self.accept(prepared, {**native, key: value}))
        changed = copy.deepcopy(native)
        changed["tasks"]["cursor"] = None
        self.error(self.accept(prepared, changed))

    def test_context_page_requires_snapshot_and_checks_section(self):
        value = request("context.page", workflow_ref=WORKFLOW, section="tasks", cursor="opaque")
        self.error(api.execute(value))
        value["expected_snapshot_revision"] = 3
        prepared = self.ok(api.execute(value))
        native = {"workflow_ref": WORKFLOW, "revision": 3, "section": "tasks", "page": empty_page()}
        self.assertEqual(self.ok(self.accept(prepared, native)), native)
        self.error(self.accept(prepared, {**native, "revision": 4}), "revision_mismatch")
        self.error(self.accept(prepared, {**native, "section": "decisions"}), "revision_mismatch")
        self.error(api.execute({**request(), "expected_snapshot_revision": 3}))

    def test_find_scope_and_page_limits_and_flags(self):
        prepared = self.prepared("workflow.find", **PROJECT, q="", limit=1, cursor=None)
        native = {"items": [{"workflow_ref": WORKFLOW, "revision": 3, "title": "same ID"}], "has_more": True, "cursor": "opaque"}
        self.assertEqual(self.ok(self.accept(prepared, native)), native)
        self.error(self.accept(prepared, {**native, "items": native["items"] * 2}))
        self.error(self.accept(prepared, {**native, "has_more": 1}))
        self.error(self.accept(prepared, {**native, "has_more": False}))
        native["items"][0]["workflow_ref"] = {**WORKFLOW, "project_id": "B"}
        self.error(self.accept(prepared, native), "scope_mismatch")

    def test_native_capabilities_do_not_enable_adapter_writes(self):
        prepared = self.prepared("capabilities", **PROJECT)
        native = {**PROFILE, **PROJECT, "commands": ["task.claim"], "queries": ["workflow.context"], "limits": {"future": 42}, "contract_status": "implemented"}
        self.assertEqual(self.ok(self.accept(prepared, native)), native)
        self.error(api.execute(request("task.claim", workflow_ref=WORKFLOW)), "unsupported_capability")
        self.error(self.accept(prepared, {**native, "project_id": "B"}), "scope_mismatch")

    def test_mcp_text_structured_and_dual_representation_handling(self):
        prepared = self.prepared()
        self.assertEqual(self.ok(self.accept(prepared, project(), text=True)), project())
        value = self.accept_request(prepared, project())
        value["mcp_result"]["content"] = [{"type": "text", "text": json.dumps(project(), sort_keys=True)}]
        self.ok(api.execute(value))
        value["mcp_result"]["content"][0]["text"] = json.dumps({**project(), "revision": 2})
        self.error(api.execute(value), "invalid_transport")
        for invalid in ({}, {"content": "text"}, {"content": []}, {"content": [], "structuredContent": []},
                        {"content": [{"type": "text", "text": "{}"}], "structuredContent": None},
                        {"content": [{"type": "image", "data": "x"}]},
                        {"content": [{"type": "text", "text": "{}"}, {"type": "text", "text": "{}"}]},
                        {"content": [{"type": "text", "text": "not json"}]},
                        {"content": [], "structuredContent": project(), "isError": 1}):
            with self.subTest(result=invalid):
                value = self.accept_request(prepared, project())
                value["mcp_result"] = invalid
                self.error(api.execute(value))

    def test_mcp_native_fault_stays_error_with_preserved_details(self):
        prepared = self.prepared()
        native = {"error": "storage_unavailable", "category": "unavailable", "details": {"future": [1]}}
        value = self.accept_request(prepared, native)
        value["mcp_result"]["isError"] = True
        result = api.execute(value)
        self.error(result, "remote_error")
        self.assertEqual(result["native_result"], native)
        value["mcp_result"] = {"content": [], "structuredContent": project(), "isError": True}
        self.error(api.execute(value))

    def test_whole_output_budget_refuses_without_clipping_and_explicit_override(self):
        prepared = self.prepared()
        native = {**project(), "future": "x" * 70000}
        value = self.accept_request(prepared, native)
        result = api.execute(value)
        self.error(result, "limit_exceeded")
        self.assertNotIn("result", result)
        value["max_output_bytes"] = 100000
        self.assertEqual(self.ok(api.execute(value)), native)
        for invalid in (True, 2047, api.MAX_BYTES + 1):
            self.error(api.execute({**value, "max_output_bytes": invalid}))
        self.error(api.execute({**value, "mcp_result": mcp({**native, "future": "x" * api.MAX_BYTES})}), "limit_exceeded")

    def test_duplicate_keys_nonfinite_unicode_and_oversized_json_rejected(self):
        for raw in (b'{"x":1,"x":2}', b'{"x":NaN}', b'{"x":1e999}', b'{"x":"\\ud800"}', b'\xff',
                    '{"x":1}'.encode("utf-16"), b'x' * (api.MAX_BYTES + 1)):
            with self.subTest(raw=raw[:30]), self.assertRaises(api.QueryError):
                api.decode(raw)

    def test_prepare_and_accept_are_pure_and_do_not_touch_transport_or_storage(self):
        value = request()
        original = copy.deepcopy(value)
        with patch("builtins.open", side_effect=AssertionError("no filesystem")), \
             patch("subprocess.Popen", side_effect=AssertionError("no process")), \
             patch("socket.socket", side_effect=AssertionError("no network")), \
             patch("os.getenv", side_effect=AssertionError("no ambient credential lookup")):
            prepared = self.ok(api.execute(value))
            self.ok(self.accept(prepared, project()))
        self.assertEqual(value, original)
        prepared["query"]["payload"]["project_ref"]["project_id"] = "changed"
        self.assertEqual(value, original)

    def test_isolated_stdlib_cli_file_and_stdin_closure_and_missing_member(self):
        with tempfile.TemporaryDirectory(prefix="board-query-cli-") as directory:
            target = Path(directory)
            (target / "workflow_records").mkdir()
            for relative in ("board-query.py", "workflow_records/board_query.py"):
                shutil.copyfile(TOOLS / relative, target / relative)
            value = request()
            path = target / "prepare.json"
            path.write_bytes(api.encode(value))
            def launch(source, stdin=None):
                return subprocess.run([sys.executable, "-I", "-S", "-B", str(target / "board-query.py"), "--activate", "--request", source],
                                      input=stdin, cwd=target, capture_output=True, timeout=10)
            process = launch(str(path))
            self.assertEqual((process.returncode, process.stderr), (0, b""))
            prepared = self.ok(json.loads(process.stdout))
            process = launch("-", api.encode(self.accept_request(prepared, project())))
            self.assertEqual((process.returncode, process.stderr), (0, b""))
            self.assertEqual(self.ok(json.loads(process.stdout)), project())
            for raw in (b'{"x":1,"x":2}', b'{"x":"\\ud800"}', b'x' * (api.MAX_BYTES + 1)):
                process = launch("-", raw)
                self.assertEqual((process.returncode, process.stderr), (1, b""))
                self.error(json.loads(process.stdout))
            self.assertFalse(list(target.rglob("__pycache__")))
            (target / "workflow_records/board_query.py").unlink()
            process = launch(str(path))
            self.assertEqual((process.returncode, process.stderr), (1, b""))
            self.assertEqual(json.loads(process.stdout)["status"], "unavailable")


if __name__ == "__main__":
    unittest.main()
