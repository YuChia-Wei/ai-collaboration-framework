"""Frozen source-replica contract and exact chunk/canonical JSON primitives."""
import base64
import hashlib
import json
from pathlib import Path

from .contracts import RecordError, require, validate_unicode

PROFILE = "workflow-records/source-store/1"
PROFILE2 = "workflow-records/source-store/2"
NATIVE_PROFILE = "workflow-board/source-replica/1"
SCHEMA = "workflow-sqlite/2"
SCHEMA21 = "workflow-sqlite/2.1"
SCHEMA3 = "workflow-sqlite/3"
CHUNK = 49152
MAX_FILE = 16777216
MAX_UNIT = 33554432
MAX_INPUT = 2 * 1024 * 1024
SCHEMA_HASH = "02ac880c1969e43c0094e88bd5817e2e205fb8552cbaf7b8f30ae2e45f331ab9"
MAPPING = "source-store-mapping/1"


def canonical(value):
    validate_unicode(value, "invalid_input")
    def ordered(item):
        if isinstance(item, dict):
            require(all(isinstance(key, str) for key in item), "invalid_input", "JSON keys must be strings.")
            return {key: ordered(item[key]) for key in sorted(item, key=lambda key: key.encode("utf-16-be"))}
        if isinstance(item, list):
            return [ordered(child) for child in item]
        require(not isinstance(item, float) and (type(item) is not int or abs(item) <= 9007199254740991),
                "invalid_input", "Source replica numbers must be safe integers.")
        return item
    return json.dumps(ordered(value), ensure_ascii=False, separators=(",", ":"), allow_nan=False).encode("utf-8")


def digest(raw):
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def parse(raw):
    from .contracts import unique_object
    def integer(value):
        require(value != "-0", "invalid_input", "Negative zero is forbidden.")
        return int(value)
    def other(_):
        raise RecordError("invalid_input", "Only safe integer JSON numbers are supported.")
    try:
        value = json.loads(raw.decode("utf-8"), object_pairs_hook=unique_object,
                           parse_int=integer, parse_float=other, parse_constant=other)
        canonical(value)
        return value
    except (ValueError, UnicodeError, RecursionError, TypeError) as exc:
        raise RecordError("malformed_record", "Invalid source-store JSON.") from exc


def fields(value, required, optional=()):
    require(isinstance(value, dict) and set(required) <= set(value) <= set(required) | set(optional),
            "invalid_input", "Missing or unknown source-store fields.")


def native_id(value):
    import re
    require(isinstance(value, str) and re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,159}", value) is not None
            and value not in ("constructor", "prototype", "__proto__"), "invalid_input", "Invalid source identifier.")


def path(value):
    require(isinstance(value, str) and 0 < len(value) <= 1024 and not value.startswith("/")
            and not any(char in value for char in ("\\", ":")) and not any(ord(char) < 32 or ord(char) == 127 for char in value)
            and all(part not in ("", ".", "..") for part in value.split("/")), "unsafe_path", "Invalid archived relative path.")


def integer(value, minimum=0, maximum=9007199254740990):
    require(type(value) is int and minimum <= value <= maximum, "invalid_input", "Expected a bounded integer.")
    return value


def unit_id(kind, workflow_id):
    return "unit-" + hashlib.sha256((kind + "\0" + workflow_id).encode("utf-8")).hexdigest()


def binding(value):
    fields(value, {"binding_id", "binding_revision", "project_ref", "source_id"})
    native_id(value["binding_id"])
    integer(value["binding_revision"], 1)
    native_id(value["source_id"])
    fields(value["project_ref"], {"store_id", "namespace", "project_id"})
    for key in ("store_id", "project_id"):
        native_id(value["project_ref"][key])
    require(value["project_ref"]["namespace"] == "personal" and value["project_ref"]["project_id"] != "legacy-personal",
            "invalid_input", "Replica requires a non-legacy personal project.")


_validators = None


def validate(selector, value):
    global _validators
    if _validators is None:
        try:
            from jsonschema import Draft202012Validator
            from referencing import Registry
            member = Path(__file__).resolve().parents[2] / "schemas/source-replica-v1.schema.json"
            require(member.is_file() and not member.is_symlink(), "provider_unavailable", "Frozen source replica schema is missing.")
            raw = member.read_bytes()
            require(hashlib.sha256(raw).hexdigest() == SCHEMA_HASH, "provider_unavailable", "Frozen source replica schema changed.")
            schema = parse(raw)
            Draft202012Validator.check_schema(schema)
            _validators = {name: Draft202012Validator({"$schema": schema["$schema"], "$defs": schema["$defs"],
                                                      "$ref": "#/$defs/" + name}, registry=Registry())
                           for name in ("command", "query", "receipt", "result_replica_operation_get",
                                        "result_replica_read", "result_replica_manifest", "result_replica_file_chunk")}
        except ImportError as exc:
            raise RecordError("provider_unavailable", "Source replication requires the declared jsonschema runtime; nothing was installed.") from exc
    require(selector in _validators and _validators[selector].is_valid(value), "malformed_record", "Source replica DTO violates its frozen schema.")


def mcp_value(transport):
    """Decode retained host data without loading an optional execution adapter."""
    require(isinstance(transport, dict) and "error_code" not in transport
            and isinstance(transport.get("content"), list) and type(transport.get("isError", False)) is bool,
            "invalid_transport", "Expected an MCP result with content.")
    value = None
    if transport["content"]:
        content = transport["content"]
        require(len(content) == 1 and isinstance(content[0], dict) and content[0].get("type") == "text"
                and isinstance(content[0].get("text"), str), "invalid_transport", "Expected one JSON text block.")
        value = parse(content[0]["text"].encode("utf-8"))
    if "structuredContent" in transport:
        structured = transport["structuredContent"]
        require(isinstance(structured, dict), "invalid_transport", "Structured result must be an object.")
        canonical(structured)
        if "error_code" in structured:
            require(transport.get("isError") is True and structured["error_code"] == "INVALID_ARGUMENT"
                    and isinstance(value, dict) and "error_code" not in value,
                    "invalid_transport", "Uncorroborated host error annotation.")
            structured = {key: item for key, item in structured.items() if key != "error_code"}
        require(value is None or canonical(structured) == canonical(value), "invalid_transport", "MCP representations disagree.")
        value = structured
    require(isinstance(value, dict), "invalid_transport", "Native result must be an object.")
    return value


def decode_chunk(value):
    require(isinstance(value, str), "invalid_input", "Chunk must be canonical base64.")
    try:
        raw = base64.b64decode(value, validate=True)
    except ValueError as exc:
        raise RecordError("invalid_input", "Chunk must be canonical base64.") from exc
    require(len(raw) <= CHUNK and base64.b64encode(raw).decode("ascii") == value,
            "malformed_record", "Chunk size or base64 representation is invalid.")
    return raw
