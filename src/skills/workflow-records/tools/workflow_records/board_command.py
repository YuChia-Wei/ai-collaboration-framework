"""Single-carrier Board command bridge. No dispatch, retry, credentials or journal.

Native DTO validation uses the frozen V2 schema and jsonschema, without network
resolution. Local fingerprints are deliberately separate from Board digests.
"""
from __future__ import annotations

import copy
from datetime import datetime
import hashlib
import importlib.util
import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker
from referencing import Registry
from referencing.exceptions import NoSuchResource

PROFILE = "workflow-records/board-command/1"
MAX_BYTES = 2 * 1024 * 1024
DEFAULT_OUTPUT = 65536
SCHEMA_SHA256 = "f9c40d058019a408097ddbf3fd414f5d638fc7a0678853cd2a0d75df55c5c1a4"
COMMANDS = (
    "workflow.create", "workflow.start", "workflow.pause", "workflow.resume",
    "workflow.cancel", "workflow.complete", "plan.revise", "document.append",
    "task.claim", "task.progress", "task.release", "task.block", "task.unblock",
    "task.complete", "task.cancel", "decision.open", "handoff.record", "checkpoint.append")
OPERATIONS = ("board-command-prepare", "board-command-accept", "board-command-reconcile")


def load_query_runtime():
    member = Path(__file__).resolve().with_name("board_query.py")
    if not member.is_file() or member.is_symlink():
        raise ImportError("Declared local query primitives are missing")
    spec = importlib.util.spec_from_file_location("board_command_query_primitives", member)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


q = load_query_runtime()
CommandError = q.QueryError
check = q.check
encode = q.encode


def canonical(value):
    return encode(value)[:-1]


def strict_values(value):
    q.unicode_values(value)
    def visit(item):
        if type(item) is int:
            check(abs(item) <= q.MAX_REVISION, "JSON integers must be safe integers.")
        elif isinstance(item, float):
            raise CommandError("invalid_input", "Only integer JSON number syntax is supported.")
        elif isinstance(item, dict):
            for child in item.values():
                visit(child)
        elif isinstance(item, list):
            for child in item:
                visit(child)
    visit(value)


def decode(raw):
    check(len(raw) <= MAX_BYTES, "Input exceeds whole-object byte limit.", "limit_exceeded")
    def pairs(items):
        result = {}
        for key, value in items:
            check(key not in result, "Duplicate JSON key.")
            result[key] = value
        return result
    def integer(raw_number):
        check(raw_number != "-0", "Negative zero is forbidden.")
        value = int(raw_number)
        check(abs(value) <= q.MAX_REVISION, "JSON integers must be safe integers.")
        return value
    def other_number(_):
        raise CommandError("invalid_input", "Floats, exponents and non-finite numbers are forbidden.")
    try:
        value = json.loads(raw.decode("utf-8"), object_pairs_hook=pairs,
                           parse_int=integer, parse_float=other_number, parse_constant=other_number)
        strict_values(value)
        return value
    except (ValueError, TypeError, UnicodeError, RecursionError) as exc:
        raise CommandError("invalid_input", "Invalid strict UTF-8 JSON.") from exc


def no_resource(uri):
    raise NoSuchResource(ref=uri)


def load_validators():
    member = Path(__file__).resolve().parents[2] / "schemas/board-collaboration-v2.schema.json"
    if not member.is_file() or member.is_symlink():
        raise ImportError("Frozen local schema is missing")
    raw = member.read_bytes()
    if hashlib.sha256(raw).hexdigest() != SCHEMA_SHA256:
        raise ImportError("Frozen local schema drift")
    schema = json.loads(raw.decode("utf-8"))
    Draft202012Validator.check_schema(schema)
    registry = Registry(retrieve=no_resource)
    checker = FormatChecker()
    # jsonschema's date-time checker is optional when its format extra is not
    # installed. Native timestamps are UTC Gregorian dates; use stdlib calendar
    # validation rather than silently treating format as annotation.
    @checker.checks("date-time", raises=(ValueError, OverflowError))
    def calendar_date_time(value):
        if not isinstance(value, str):
            return True
        datetime.fromisoformat(value.replace("Z", "+00:00"))
        return True
    return {name: Draft202012Validator({"$schema": schema["$schema"], "$ref": "#/$defs/" + name,
                                       "$defs": schema["$defs"]},
                                      registry=registry, format_checker=checker)
            for name in ("command", "capabilities", "receipt", "operation_result", "error")}


VALIDATORS = load_validators()


def validate(name, value):
    # Never return validator messages: they may include document bodies or other
    # private input. The selected schema and stable adapter code identify the gap.
    check(VALIDATORS[name].is_valid(value), "Native " + name + " violates the frozen V2 schema.", "invalid_native_schema")


def prepare(selected, capabilities, command):
    q.binding(selected)
    validate("capabilities", capabilities)
    q.project_ref({key: capabilities[key] for key in q.PROJECT_KEYS}, selected["project_ref"])
    validate("command", command)
    name = command["command"]
    check(name in COMMANDS, "Command is outside the selected workflow writer allowlist.", "unsupported_capability")
    check(name in capabilities["commands"] and "operation.get" in capabilities["queries"],
          "Selected connection does not advertise the required command and recovery query.", "provider_unavailable")
    q.project_ref(command["workflow_ref"], selected["project_ref"], workflow=True)
    if name == "workflow.create":
        check(command["expected_revision"] == 0, "Workflow creation requires expected revision zero.")
    else:
        q.number(command["expected_revision"], 1)
    check(len(canonical(command)) <= capabilities["limits"]["request_utf8_bytes"],
          "Native command exceeds its UTF-8 byte limit.", "limit_exceeded")
    payload = command["payload"]
    document = payload.get("plan") if name == "plan.revise" else payload.get("document") if name == "document.append" else None
    if document is not None:
        check(len(document["content"].encode("utf-8")) <= capabilities["limits"]["document_utf8_bytes"],
              "Native document exceeds its exact UTF-8 byte limit.", "limit_exceeded")
    recovery = {"service_contract_version": q.NATIVE_PROFILE, "schema_version": q.SCHEMA,
                "query": "operation.get", "payload": {"workflow_ref": command["workflow_ref"], "operation_id": command["operation_id"]}}
    return copy.deepcopy({"contract_version": PROFILE, "binding": selected, "capabilities": capabilities,
                          "command": command, "tool_name": "v2_" + name.replace(".", "_"),
                          "local_command_fingerprint": "sha256:" + hashlib.sha256(canonical(command)).hexdigest(),
                          "recovery_query": recovery})


def revalidate(selected, prepared):
    q.fields(prepared, {"contract_version", "binding", "capabilities", "command", "tool_name", "local_command_fingerprint", "recovery_query"})
    q.binding(prepared["binding"])
    check(prepared["contract_version"] == PROFILE and canonical(selected) == canonical(prepared["binding"]),
          "Prepared profile or binding changed.", "binding_mismatch")
    actual = prepare(selected, prepared["capabilities"], prepared["command"])
    check(canonical(actual) == canonical(prepared), "Prepared command, fingerprint, tool or recovery query changed.", "binding_mismatch")


def mcp_value(result):
    q.object_fields(result, {"content"})
    check("error_code" not in result, "Host error annotation is outside the observed structured location.", "invalid_transport")
    check(isinstance(result["content"], list) and type(result.get("isError", False)) is bool,
          "Malformed MCP result.", "invalid_transport")
    value = None
    if result["content"]:
        content = result["content"]
        check(len(content) == 1 and isinstance(content[0], dict) and content[0].get("type") == "text"
              and isinstance(content[0].get("text"), str), "MCP content must be one JSON text block.", "invalid_transport")
        value = decode(content[0]["text"].encode("utf-8"))
    if "structuredContent" in result:
        structured = result["structuredContent"]
        check(isinstance(structured, dict), "MCP structured content must be an object.", "invalid_transport")
        strict_values(structured)
        if "error_code" in structured:
            # The selected host annotates error results here, while the text
            # block contains the untouched native DTO. Recognize only that
            # observed annotation and require the remaining dual data to agree.
            check(result.get("isError") is True and type(structured["error_code"]) is str
                  and structured["error_code"] == "INVALID_ARGUMENT"
                  and isinstance(value, dict) and "error_code" not in value,
                  "Unrecognized or uncorroborated host error annotation.", "invalid_transport")
            structured = {key: item for key, item in structured.items() if key != "error_code"}
        check(value is None or canonical(structured) == canonical(value), "MCP representations disagree.", "invalid_transport")
        value = structured
    check(isinstance(value, dict), "MCP result contains no native object.", "invalid_transport")
    return value


def correlate_receipt(receipt, command, verified_digest=None):
    validate("receipt", receipt)
    check(receipt["workflow_ref"] == command["workflow_ref"] and receipt["operation_id"] == command["operation_id"],
          "Receipt scope or operation does not match the original command.", "receipt_mismatch")
    if verified_digest is not None:
        q.hash_value(verified_digest)
        check(receipt["request_digest"] == verified_digest, "Receipt differs from the supplied previously verified server digest.", "digest_mismatch")
    if receipt["accepted"]:
        check(receipt["before_revision"] == command["expected_revision"]
              and receipt["revision"] == receipt["before_revision"] + 1,
              "Receipt does not advance the original expected revision exactly once.", "receipt_mismatch")
        workflow_effects = [effect for effect in receipt["effects"] if effect["kind"] == "workflow"]
        check(len(workflow_effects) == 1 and workflow_effects[0]["id"] == command["workflow_ref"]["workflow_id"]
              and workflow_effects[0]["revision"] == receipt["revision"], "Receipt workflow effect does not match its revision.", "receipt_mismatch")
        for effect in receipt["effects"]:
            if effect["kind"] == "document" and command["command"] in ("document.append", "plan.revise"):
                document = command["payload"]["document" if command["command"] == "document.append" else "plan"]
                check(effect["id"] == document["document_id"] and effect["revision"] == document["expected_document_revision"] + 1,
                      "Document effect does not match the submitted document revision.", "receipt_mismatch")
        if command["command"] in ("document.append", "plan.revise"):
            check(sum(effect["kind"] == "document" for effect in receipt["effects"]) == 1,
                  "Document command requires its retained document effect.", "receipt_mismatch")
        name, payload = command["command"], command["payload"]
        def require_effect(kind, identity, revision=None):
            effects = [effect for effect in receipt["effects"] if effect["kind"] == kind and effect["id"] == identity]
            check(len(effects) == 1 and (revision is None or effects[0]["revision"] == revision),
                  "Receipt effect does not match the submitted identity/revision.", "receipt_mismatch")
        if name.startswith("task."):
            assignment = payload.get("assignment")
            definition_revision = payload.get("expected_definition_revision") if name == "task.claim" else assignment["definition_revision"] if assignment else None
            require_effect("task", payload["task_id"], definition_revision)
            if name == "task.claim":
                check(any(effect["kind"] == "assignment" for effect in receipt["effects"]),
                      "Claim receipt must include an assignment effect.", "receipt_mismatch")
            if assignment and name in ("task.release", "task.block", "task.complete", "task.cancel"):
                require_effect("assignment", assignment["assignment_id"], assignment["generation"])
        elif name == "plan.revise":
            for change in payload["task_changes"]:
                require_effect("task", change["definition"]["id"], 1 if change["kind"] == "add" else change["expected_definition_revision"] + 1)
        elif name == "decision.open":
            require_effect("decision", payload["decision_id"], 1)
        elif name in ("handoff.record", "checkpoint.append"):
            kind = "handoff" if name == "handoff.record" else "checkpoint"
            effects = [effect for effect in receipt["effects"] if effect["kind"] == kind]
            check(len(effects) == 1 and effects[0]["revision"] == 1,
                  "Receipt is missing its generated record effect.", "receipt_mismatch")
    else:
        check(receipt["expected_revision"] == command["expected_revision"], "Rejected receipt names another original revision.", "receipt_mismatch")


def lookup(prepared):
    return {"tool_name": "v2_operation_get", "query": copy.deepcopy(prepared["recovery_query"])}


def unresolved(prepared, native=None, observed=None):
    result = {"server_digest_verification": "not_recomputed", "requires_original_replay": observed in ("accepted", "rejected"),
              "next_action": "replay_exact_original_command" if observed in ("accepted", "rejected") else "query_original_operation",
              "recovery": lookup(prepared)}
    if native is not None:
        result["native_result"] = native
    if observed is not None:
        result["observed_outcome"] = observed
    if result["requires_original_replay"]:
        result["replay"] = {"tool_name": prepared["tool_name"], "command": copy.deepcopy(prepared["command"])}
    return result


def accepted_result(prepared, receipt, correlation):
    return {"native_result": receipt, "correlation": correlation,
            "server_digest_verification": "host_correlated_not_recomputed",
            "prior_confirmation": {"local_command_fingerprint": prepared["local_command_fingerprint"],
                                   "request_digest": receipt["request_digest"]}, "requires_original_replay": False,
            "next_action": "retain_receipt_and_original_prepared_command"}


def failure(operation, error):
    return {"contract_version": PROFILE, "operation": operation if operation in OPERATIONS else None,
            "status": "unavailable" if error.code in ("provider_unavailable", "runtime_unavailable") else "error", "bridge_effect": "none",
            "command_outcome": "not_dispatched" if operation == "board-command-prepare" else "unknown",
            "error": {"code": error.code, "message": error.message},
            "next_action": "correct_prepare_inputs" if operation == "board-command-prepare" else "retain_original_prepared_command_and_query_or_replay_same_operation"}


def execute(request):
    operation = request.get("operation") if isinstance(request, dict) else None
    try:
        strict_values(request)
        check(len(encode(request)) <= MAX_BYTES, "Input exceeds the whole-object limit.", "limit_exceeded")
        check(isinstance(request, dict) and request.get("contract_version") == PROFILE, "Unsupported command bridge profile.", "unsupported_profile")
        check(operation in OPERATIONS, "Unsupported command bridge operation.", "unsupported_capability")
        required = {"contract_version", "operation", "binding"}
        optional = {"max_output_bytes"}
        if operation == "board-command-prepare":
            q.fields(request, required | {"command", "capabilities"}, optional)
        elif operation == "board-command-accept":
            q.fields(request, required | {"prepared", "mcp_result"}, optional | {"prior_confirmation"})
        else:
            q.fields(request, required | {"prepared"}, optional | {"prior_confirmation", "lookup_result"})
        maximum = request.get("max_output_bytes", DEFAULT_OUTPUT)
        q.number(maximum, 2048, MAX_BYTES)
        outcome = "unknown"
        if operation == "board-command-prepare":
            result = prepare(request["binding"], request["capabilities"], request["command"])
            outcome = "not_dispatched"
        else:
            prepared = request["prepared"]
            revalidate(request["binding"], prepared)
            digest = None
            if "prior_confirmation" in request:
                confirmation = request["prior_confirmation"]
                q.fields(confirmation, {"local_command_fingerprint", "request_digest"})
                q.hash_value(confirmation["local_command_fingerprint"])
                q.hash_value(confirmation["request_digest"])
                check(confirmation["local_command_fingerprint"] == prepared["local_command_fingerprint"],
                      "Prior confirmation belongs to another original command.", "fingerprint_mismatch")
                digest = confirmation["request_digest"]
            key = "mcp_result" if operation == "board-command-accept" else "lookup_result"
            transport = request.get(key)
            if transport is None:
                result = unresolved(prepared)
            else:
                native = mcp_value(transport)
                if transport.get("isError", False) and not (operation == "board-command-accept" and native.get("accepted") is False):
                    check(native.get("accepted") is not True,
                          "MCP error flag contradicts an accepted receipt.", "invalid_transport")
                    validate("error", native)
                    response = failure(operation, CommandError("remote_error", "MCP reported a native fault; this is not a durable rejected receipt."))
                    response["result"] = unresolved(prepared, native)
                    check(len(encode(response)) <= maximum, "Whole response exceeds output budget; original command remains unresolved.", "limit_exceeded")
                    return response
                if operation == "board-command-accept":
                    correlate_receipt(native, prepared["command"], digest)
                    result = accepted_result(prepared, native, "direct_host_request_response")
                    outcome = "applied" if native["accepted"] else "rejected"
                else:
                    validate("operation_result", native)
                    if native["outcome"] == "unknown":
                        command = prepared["command"]
                        check(native["workflow_ref"] == command["workflow_ref"] and native["operation_id"] == command["operation_id"],
                              "Unknown lookup names another operation or workflow.", "receipt_mismatch")
                        result = unresolved(prepared, native, "unknown")
                    else:
                        correlate_receipt(native["receipt"], prepared["command"], digest)
                        if digest is None:
                            result = unresolved(prepared, native, native["outcome"])
                        else:
                            result = accepted_result(prepared, native["receipt"], "previously_verified_server_digest")
                            outcome = "applied" if native["receipt"]["accepted"] else "rejected"
        response = {"contract_version": PROFILE, "operation": operation, "status": "ok", "bridge_effect": "none",
                    "command_outcome": outcome, "result": result}
        check(len(encode(response)) <= maximum, "Whole response exceeds output budget; retain the original command and reconcile after dispatch.", "limit_exceeded")
        return copy.deepcopy(response)
    except CommandError as exc:
        return failure(operation, exc)
    except (ValueError, TypeError, UnicodeError, RecursionError, KeyError):
        return failure(operation, CommandError("invalid_input", "Malformed command bridge request or result; no automatic retry was made."))
