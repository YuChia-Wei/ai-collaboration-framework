"""Pure, bounded Board V2 query preparation and MCP result acceptance.

No transport, credentials, filesystem, provider selection or domain mutations.
Critical invariants are validated; this is not a complete native schema validator.
"""
from __future__ import annotations

import copy
import hashlib
import json
import re

PROFILE = "workflow-records/board-query/1"
NATIVE_PROFILE = "workflow-board/collaboration/2"
SCHEMA = "2.0"
MAX_BYTES = 2 * 1024 * 1024
DEFAULT_OUTPUT = 65536
MAX_REVISION = 9007199254740991
QUERIES = ("project.list", "project.read", "project.operation.get", "capabilities",
           "workflow.find", "workflow.context", "context.page", "task.read",
           "decision.read", "document.read", "operation.get")
PROJECT_KEYS = {"store_id", "namespace", "project_id"}
WORKFLOW_KEYS = PROJECT_KEYS | {"record_kind", "workflow_id"}


class QueryError(Exception):
    def __init__(self, code, message):
        self.code, self.message = code, message
        super().__init__(message)


def check(condition, message, code="invalid_input"):
    if not condition:
        raise QueryError(code, message)


def encode(value):
    return (json.dumps(value, ensure_ascii=False, allow_nan=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def unicode_values(value):
    if isinstance(value, str):
        value.encode("utf-8")
    elif isinstance(value, dict):
        for key, item in value.items():
            check(isinstance(key, str), "Object keys must be strings.")
            unicode_values(key)
            unicode_values(item)
    elif isinstance(value, list):
        for item in value:
            unicode_values(item)


def decode(raw):
    check(len(raw) <= MAX_BYTES, "Input exceeds the whole-object byte limit.", "limit_exceeded")
    def pairs(items):
        result = {}
        for key, value in items:
            check(key not in result, "Duplicate JSON key.")
            result[key] = value
        return result
    def constant(_):
        raise QueryError("invalid_input", "Non-finite JSON number.")
    try:
        value = json.loads(raw.decode("utf-8"), object_pairs_hook=pairs, parse_constant=constant)
        unicode_values(value)
        encode(value)
        return value
    except (ValueError, TypeError, UnicodeError, RecursionError) as exc:
        raise QueryError("invalid_input", "Invalid UTF-8 JSON object.") from exc


def fields(value, required, optional=()):
    check(isinstance(value, dict) and set(required) <= set(value)
          and set(value) <= set(required) | set(optional), "Missing or unknown object fields.")


def object_fields(value, required):
    check(isinstance(value, dict) and set(required) <= set(value), "Required native result fields are missing.", "invalid_result")


def identifier(value):
    check(isinstance(value, str) and re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,159}", value) is not None
          and value not in ("constructor", "prototype", "__proto__"), "Invalid native identifier.")


def number(value, minimum=0, maximum=MAX_REVISION):
    check(type(value) is int and minimum <= value <= maximum, "Expected a safe integer in range.")


def string(value, maximum, minimum=1):
    check(isinstance(value, str) and minimum <= len(value) <= maximum, "Invalid bounded string.")


def hash_value(value):
    check(isinstance(value, str) and re.fullmatch(r"sha256:[0-9a-f]{64}", value) is not None, "Invalid content digest.")


def project_ref(value, expected=None, workflow=False):
    fields(value, WORKFLOW_KEYS if workflow else PROJECT_KEYS)
    for key in ("store_id", "project_id"):
        identifier(value[key])
    check(value["namespace"] == "personal", "Unsupported namespace.")
    if workflow:
        check(value["record_kind"] == "collaboration", "Unsupported record kind.")
        check(value["project_id"] != "legacy-personal", "Legacy workflow queries require a separately selected V1 route.", "unsupported_profile")
        identifier(value["workflow_id"])
    if expected is not None:
        check(all(value[key] == expected[key] for key in PROJECT_KEYS), "Returned or requested project scope differs from binding.", "scope_mismatch")


def document_ref(value):
    fields(value, {"document_id", "revision", "content_hash"})
    identifier(value["document_id"])
    number(value["revision"], 1)
    hash_value(value["content_hash"])


def binding(value):
    fields(value, {"adapter_id", "binding_id", "binding_revision", "project_ref"})
    check(value["adapter_id"] == "workflow-board-v2", "Unsupported adapter binding.", "unsupported_profile")
    identifier(value["binding_id"])
    number(value["binding_revision"], 1)
    project_ref(value["project_ref"])


def versions(value):
    check(value.get("service_contract_version") == NATIVE_PROFILE, "Native profile mismatch.", "unsupported_profile")
    check(value.get("schema_version") == SCHEMA, "Native schema mismatch.", "unsupported_schema")


def prepare(selected, query, snapshot=None):
    binding(selected)
    fields(query, {"service_contract_version", "schema_version", "query", "payload"})
    versions(query)
    name, payload = query["query"], query["payload"]
    check(isinstance(name, str) and name in QUERIES, "Query is outside the read-only allowlist.", "unsupported_capability")
    keys = {
        "project.list": {"store_id", "namespace", "limit", "cursor"},
        "project.read": {"project_ref"}, "project.operation.get": {"project_ref", "operation_id"},
        "capabilities": PROJECT_KEYS, "workflow.find": PROJECT_KEYS | {"q", "limit", "cursor"},
        "workflow.context": {"workflow_ref", "limit"}, "context.page": {"workflow_ref", "section", "cursor"},
        "task.read": {"workflow_ref", "task_id", "definition_revision", "at_revision"},
        "decision.read": {"workflow_ref", "decision_id", "decision_revision", "at_revision"},
        "document.read": {"workflow_ref", "document_ref"}, "operation.get": {"workflow_ref", "operation_id"}}
    fields(payload, keys[name])
    scope = selected["project_ref"]
    if "workflow_ref" in payload:
        project_ref(payload["workflow_ref"], scope, workflow=True)
    elif "project_ref" in payload:
        project_ref(payload["project_ref"], scope)
    elif name == "project.list":
        check(payload["store_id"] == scope["store_id"] and payload["namespace"] == scope["namespace"], "Registry scope differs from binding.", "scope_mismatch")
    else:
        project_ref({key: payload[key] for key in PROJECT_KEYS}, scope)
        check(scope["project_id"] != "legacy-personal", "Legacy workflow queries require V1.", "unsupported_profile")
    if "limit" in payload:
        number(payload["limit"], 1, 100 if name == "project.list" else 50 if name == "workflow.find" else 20)
    if "cursor" in payload and payload["cursor"] is not None:
        string(payload["cursor"], 2048)
    if name == "context.page":
        check(payload["section"] in ("tasks", "decisions", "handoffs") and payload["cursor"] is not None, "Page requires a section and opaque cursor.")
        number(snapshot, 1)
    else:
        check(snapshot is None, "Snapshot expectation is only accepted for context.page.")
    if "q" in payload:
        string(payload["q"], 200, 0)
    for key in ("task_id", "decision_id", "operation_id"):
        if key in payload:
            identifier(payload[key])
    for key in ("definition_revision", "decision_revision", "at_revision"):
        if key in payload:
            number(payload[key], 1)
    if "document_ref" in payload:
        document_ref(payload["document_ref"])
    return copy.deepcopy({"contract_version": PROFILE, "binding": selected, "query": query,
                          "tool_name": "v2_" + name.replace(".", "_"), "expected_snapshot_revision": snapshot})


def page(value, limit, section=None):
    object_fields(value, {"items", "has_more", "cursor"})
    check(isinstance(value["items"], list) and len(value["items"]) <= limit, "Invalid page size.", "invalid_result")
    check(type(value["has_more"]) is bool, "Invalid paging flag.", "invalid_result")
    if value["has_more"]:
        string(value["cursor"], 2048)
    else:
        check(value["cursor"] is None, "Completed page must not carry another cursor.", "invalid_result")
    if section:
        object_fields(value, {"total"})
        number(value["total"])
        check(value["total"] >= len(value["items"]), "Page exceeds section total.", "invalid_result")
        for item in value["items"]:
            object_fields(item, {"id"})
            identifier(item["id"])
            if section == "tasks":
                object_fields(item, {"definition_revision", "plan_basis"})
                number(item["definition_revision"], 1)
                document_ref(item["plan_basis"])
            elif section == "decisions":
                object_fields(item, {"revision", "basis"})
                number(item["revision"], 1)
                check(isinstance(item["basis"], list), "Invalid decision basis.", "invalid_result")
                for ref in item["basis"]:
                    document_ref(ref)
            else:
                object_fields(item, {"workflow_revision", "task_id"})
                number(item["workflow_revision"], 1)
                if item["task_id"] is not None:
                    identifier(item["task_id"])


def same_workflow(value, expected):
    project_ref(value, expected, workflow=True)
    check(value == expected, "Workflow identity differs from the prepared query.", "scope_mismatch")


def receipt_result(value, name, payload):
    object_fields(value, {"outcome"})
    outcome = value["outcome"]
    check(outcome in ("accepted", "rejected", "unknown"), "Invalid operation outcome.", "invalid_result")
    target = "project_ref" if name == "project.operation.get" else "workflow_ref"
    def target_matches(record):
        object_fields(record, {target, "operation_id"})
        check(("workflow_ref" if target == "project_ref" else "project_ref") not in record,
              "Receipt belongs to a different target kind.", "scope_mismatch")
        if target == "project_ref":
            project_ref(record[target], payload[target])
        else:
            same_workflow(record[target], payload[target])
        check(record["operation_id"] == payload["operation_id"], "Receipt operation identity mismatch.", "scope_mismatch")
    if outcome == "unknown":
        check("receipt" not in value, "Unknown outcome cannot contain a receipt.", "invalid_result")
        target_matches(value)
        return
    object_fields(value, {"receipt"})
    receipt = value["receipt"]
    target_matches(receipt)
    object_fields(receipt, {"accepted", "request_digest"})
    check(type(receipt["accepted"]) is bool and receipt["accepted"] == (outcome == "accepted"), "Receipt outcome disagrees with acceptance.", "invalid_result")
    hash_value(receipt["request_digest"])
    if target == "project_ref":
        object_fields(receipt, {"expected_revision", "revision", "error"})
        number(receipt["expected_revision"])
        number(receipt["revision"])
        if outcome == "accepted":
            check(receipt["revision"] == receipt["expected_revision"] + 1 and receipt["error"] is None, "Invalid accepted project receipt.", "invalid_result")
        else:
            string(receipt["error"], 160)
    else:
        versions(receipt)
        if outcome == "accepted":
            object_fields(receipt, {"before_revision", "revision", "effects"})
            number(receipt["before_revision"])
            number(receipt["revision"], 1)
            check(receipt["revision"] == receipt["before_revision"] + 1, "Receipt revision did not advance exactly once.", "invalid_result")
            check(isinstance(receipt["effects"], list), "Invalid receipt effects.", "invalid_result")
            for effect in receipt["effects"]:
                object_fields(effect, {"kind", "id", "revision"})
                identifier(effect["id"])
                number(effect["revision"], 1)
        else:
            object_fields(receipt, {"expected_revision", "current_revision", "failure"})
            number(receipt["expected_revision"])
            if receipt["current_revision"] is not None:
                number(receipt["current_revision"])
            fault(receipt["failure"])


def fault(value):
    object_fields(value, {"error", "category", "details"})
    string(value["error"], 160)
    check(value["category"] in ("invalid", "not_found", "conflict", "forbidden", "unauthenticated", "limit_exceeded", "unsupported", "unavailable")
          and isinstance(value["details"], dict), "Invalid native fault.", "invalid_result")


def native_result(value, prepared):
    check(isinstance(value, dict), "Native result must be an object.", "invalid_result")
    name, payload = prepared["query"]["query"], prepared["query"]["payload"]
    scope = prepared["binding"]["project_ref"]
    # Versions are mandatory only where the native DTO carries them.
    if "service_contract_version" in value or "schema_version" in value:
        versions(value)
    if name in ("project.operation.get", "operation.get"):
        receipt_result(value, name, payload)
    elif name == "project.list":
        page(value, payload["limit"])
        for item in value["items"]:
            validate_project(item, scope, registry=True)
    elif name == "project.read":
        validate_project(value, scope)
    elif name == "capabilities":
        object_fields(value, PROJECT_KEYS | {"commands", "queries", "limits", "contract_status"})
        versions(value)
        project_ref({key: value[key] for key in PROJECT_KEYS}, scope)
        check(isinstance(value["commands"], list) and isinstance(value["queries"], list)
              and isinstance(value["limits"], dict) and value["contract_status"] == "implemented", "Invalid native capabilities.", "invalid_result")
    elif name == "workflow.find":
        page(value, payload["limit"])
        for item in value["items"]:
            object_fields(item, {"workflow_ref", "revision"})
            project_ref(item["workflow_ref"], scope, workflow=True)
            number(item["revision"], 1)
    else:
        object_fields(value, {"workflow_ref"})
        same_workflow(value["workflow_ref"], payload["workflow_ref"])
        if name == "workflow.context":
            versions(value)
            object_fields(value, {"revision", "workflow", "tasks", "decisions", "handoffs", "missing"})
            number(value["revision"], 1)
            object_fields(value["workflow"], {"plan"})
            if value["workflow"]["plan"] is not None:
                document_ref(value["workflow"]["plan"])
            for section in ("tasks", "decisions", "handoffs"):
                page(value[section], payload["limit"], section)
            check(isinstance(value["missing"], list) and len(value["missing"]) <= 100, "Invalid missing-input list.", "invalid_result")
            for missing in value["missing"]:
                object_fields(missing, {"kind", "ref", "reason"})
                for key, maximum in (("kind", 160), ("ref", 2000), ("reason", 1000)):
                    string(missing[key], maximum)
        elif name == "context.page":
            object_fields(value, {"revision", "section", "page"})
            number(value["revision"], 1)
            check(value["revision"] == prepared["expected_snapshot_revision"] and value["section"] == payload["section"], "Page snapshot or section mismatch.", "revision_mismatch")
            page(value["page"], 20, payload["section"])
        elif name == "document.read":
            object_fields(value, {"ref", "content"})
            document_ref(value["ref"])
            check(value["ref"] == payload["document_ref"], "Document reference differs from the requested revision.", "revision_mismatch")
            check(isinstance(value["content"], str), "Document content must be text.", "invalid_result")
            raw = value["content"].encode("utf-8")
            check(len(raw) <= 256000, "Native document byte limit exceeded.", "limit_exceeded")
            check("sha256:" + hashlib.sha256(raw).hexdigest() == value["ref"]["content_hash"], "Exact UTF-8 document hash mismatch.", "hash_mismatch")
        else:
            object_fields(value, {"snapshot_revision"})
            number(value["snapshot_revision"], 1)
            check(value["snapshot_revision"] == payload["at_revision"], "Detail snapshot revision mismatch.", "revision_mismatch")
            if name == "task.read":
                object_fields(value, {"summary", "definition", "result"})
                object_fields(value["summary"], {"id", "definition_revision"})
                object_fields(value["definition"], {"id"})
                number(value["summary"]["definition_revision"], 1)
                check(value["summary"]["id"] == payload["task_id"] == value["definition"]["id"]
                      and value["summary"]["definition_revision"] == payload["definition_revision"], "Task identity or definition revision mismatch.", "revision_mismatch")
            else:
                object_fields(value, {"decision", "resolution", "options"})
                object_fields(value["decision"], {"id", "revision"})
                number(value["decision"]["revision"], 1)
                check(value["decision"]["id"] == payload["decision_id"] and value["decision"]["revision"] == payload["decision_revision"], "Decision identity or revision mismatch.", "revision_mismatch")


def validate_project(value, scope, registry=False):
    object_fields(value, {"project_ref", "name", "revision", "workflow_contract"})
    project_ref(value["project_ref"])
    expected = {**scope, "project_id": value["project_ref"]["project_id"]} if registry else scope
    project_ref(value["project_ref"], expected)
    string(value["name"], 160)
    number(value["revision"], 1)
    expected_contract = "workflow-board/collaboration/1" if value["project_ref"]["project_id"] == "legacy-personal" else NATIVE_PROFILE
    check(value["workflow_contract"] == expected_contract, "Project workflow contract mismatch.", "unsupported_profile")


def mcp_value(result):
    object_fields(result, {"content"})
    check(isinstance(result["content"], list) and type(result.get("isError", False)) is bool, "Malformed MCP result.", "invalid_transport")
    structured = result.get("structuredContent")
    text_value = None
    content = result["content"]
    if content:
        check(len(content) == 1 and isinstance(content[0], dict) and content[0].get("type") == "text"
              and isinstance(content[0].get("text"), str), "MCP content must be exactly one JSON text block.", "invalid_transport")
        text_value = decode(content[0]["text"].encode("utf-8"))
    check(isinstance(structured, dict) or isinstance(text_value, dict), "No native object in MCP result.", "invalid_transport")
    if "structuredContent" in result:
        check(isinstance(structured, dict), "MCP structuredContent must be an object.", "invalid_transport")
        check(text_value is None or encode(structured) == encode(text_value), "Contradictory MCP result representations.", "invalid_transport")
        return structured
    return text_value


def failure(operation, error):
    return {"contract_version": PROFILE, "operation": operation if operation in ("board-query-prepare", "board-query-accept") else None,
            "status": "error", "mutation_state": "none", "error": {"code": error.code, "message": error.message}}


def execute(request):
    operation = request.get("operation") if isinstance(request, dict) else None
    try:
        unicode_values(request)
        check(len(encode(request)) <= MAX_BYTES, "Input exceeds the whole-object byte limit.", "limit_exceeded")
        check(isinstance(request, dict) and request.get("contract_version") == PROFILE, "Unsupported adapter profile.", "unsupported_profile")
        check(operation in ("board-query-prepare", "board-query-accept"), "Unsupported adapter operation.", "unsupported_capability")
        required = {"contract_version", "operation", "binding"}
        optional = {"max_output_bytes"}
        if operation == "board-query-prepare":
            fields(request, required | {"query"}, optional | {"expected_snapshot_revision"})
        else:
            fields(request, required | {"prepared", "mcp_result"}, optional)
        maximum = request.get("max_output_bytes", DEFAULT_OUTPUT)
        number(maximum, 2048, MAX_BYTES)
        if operation == "board-query-prepare":
            result = prepare(request["binding"], request["query"], request.get("expected_snapshot_revision"))
        else:
            value = request["prepared"]
            fields(value, {"contract_version", "binding", "query", "tool_name", "expected_snapshot_revision"})
            binding(value["binding"])
            check(value["contract_version"] == PROFILE and encode(value["binding"]) == encode(request["binding"]), "Prepared binding or profile changed.", "binding_mismatch")
            result = prepare(request["binding"], value["query"], value["expected_snapshot_revision"])
            check(encode(result) == encode(value), "Prepared request no longer matches its query and binding.", "binding_mismatch")
            result = mcp_value(request["mcp_result"])
            if request["mcp_result"].get("isError", False):
                fault(result)
                response = failure(operation, QueryError("remote_error", "Selected MCP tool reported a native fault."))
                response["native_result"] = result
                check(len(encode(response)) <= maximum, "Whole response exceeds output budget.", "limit_exceeded")
                return response
            native_result(result, value)
        response = {"contract_version": PROFILE, "operation": operation, "status": "ok", "mutation_state": "none", "result": result}
        check(len(encode(response)) <= maximum, "Whole response exceeds output budget; request a larger explicit budget.", "limit_exceeded")
        return copy.deepcopy(response)
    except QueryError as exc:
        return failure(operation, exc)
    except (ValueError, TypeError, UnicodeError, RecursionError, KeyError):
        return failure(operation, QueryError("invalid_input", "Malformed adapter request or native result."))
