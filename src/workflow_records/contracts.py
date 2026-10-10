"""Provider-independent request, reference and error vocabulary."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import hashlib
import json
import re
from typing import Protocol

VERSION = "workflow-records/1"
MAX_FILE = 262144
MAX_OUTPUT = 65536
MAX_TASKS = 128
MAX_OPERATIONS = 128
ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,127}\Z")


class RecordError(Exception):
    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code
        self.message = message


def require(condition, code, message):
    if not condition:
        raise RecordError(code, message)


def identifier(value):
    require(isinstance(value, str) and ID.fullmatch(value) is not None,
            "invalid_input", "Expected a path-safe identifier.")
    return value


def integer(value, minimum, maximum):
    require(type(value) is int and minimum <= value <= maximum,
            "invalid_input", f"Expected an integer from {minimum} to {maximum}.")
    return value


def encoded(value):
    return (json.dumps(value, ensure_ascii=False, sort_keys=True,
                       separators=(",", ":"), allow_nan=False) + "\n").encode("utf-8")


def digest(raw):
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def unique_object(pairs):
    value = {}
    for key, item in pairs:
        require(key not in value, "malformed_record", "Duplicate object key.")
        value[key] = item
    return value


def decode_json(raw):
    require(len(raw) <= MAX_FILE, "limit_exceeded", "JSON input exceeds the byte limit.")
    try:
        def reject_constant(_):
            raise ValueError("Non-finite numbers are not JSON records.")
        return json.loads(raw.decode("utf-8"), object_pairs_hook=unique_object,
                          parse_constant=reject_constant)
    except (ValueError, UnicodeError, RecursionError) as exc:
        raise RecordError("malformed_record", "Invalid UTF-8 JSON.") from exc


def timestamp(value):
    require(isinstance(value, str) and re.fullmatch(
        r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})", value),
        "malformed_record", "Timestamp requires seconds and an explicit UTC offset.")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        require(parsed.tzinfo is not None and "T" in value,
                "malformed_record", "Timestamp requires an explicit UTC offset.")
    except ValueError as exc:
        raise RecordError("malformed_record", "Invalid timestamp.") from exc


@dataclass(frozen=True)
class WorkflowRef:
    provider_id: str
    store_id: str
    workflow_id: str

    @classmethod
    def parse(cls, value):
        require(isinstance(value, dict) and set(value) ==
                {"provider_id", "store_id", "workflow_id"},
                "invalid_input", "A complete explicit workflow_ref is required.")
        return cls(*(identifier(value[key]) for key in
                     ("provider_id", "store_id", "workflow_id")))

    def as_dict(self):
        return dict(provider_id=self.provider_id, store_id=self.store_id,
                    workflow_id=self.workflow_id)


class RecordPort(Protocol):
    """Application-facing capability; provider DTOs do not expose board models."""
    def find(self, offset: int, limit: int) -> dict: ...
    def context(self, ref: WorkflowRef, task_limit: int) -> dict: ...
    def read(self, ref: WorkflowRef, document: str, revision: str | None,
             offset: int, limit: int) -> dict: ...
    def checkpoint(self, ref: WorkflowRef, request: dict) -> dict: ...
    def operation(self, ref: WorkflowRef, operation_id: str) -> dict: ...
