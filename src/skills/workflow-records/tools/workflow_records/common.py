"""Bounded record and path primitives shared by storage adapters."""
from __future__ import annotations
from pathlib import Path, PurePosixPath
import re
import stat
import subprocess
import yaml
from .contracts import MAX_FILE, RecordError, decode_json, require, validate_unicode

class RecordLoader(yaml.SafeLoader):
    def compose_node(self, parent, index):
        require(not self.check_event(yaml.AliasEvent), "malformed_record",
                "YAML aliases are not supported by the selected record format.")
        return super().compose_node(parent, index)

    def construct_mapping(self, node, deep=False):
        result = {}
        for key_node, value_node in node.value:
            key = self.construct_object(key_node, deep=deep)
            require(isinstance(key, str) and key not in result,
                    "malformed_record", "YAML requires unique string keys.")
            result[key] = self.construct_object(value_node, deep=deep)
        return result


def mapping(raw, suffix):
    try:
        value = decode_json(raw) if suffix == ".json" else yaml.load(
            raw.decode("utf-8"), Loader=RecordLoader)
    except (yaml.YAMLError, UnicodeError, RecursionError, TypeError) as exc:
        raise RecordError("malformed_record", "Invalid UTF-8 record mapping.") from exc
    require(isinstance(value, dict), "malformed_record", "Record must be a mapping.")
    validate_unicode(value)
    return value


def relative_path(value):
    require(isinstance(value, str) and value and "\\" not in value and ":" not in value,
            "unsafe_path", "Expected a relative POSIX path.")
    parts = value.split("/")
    require(not value.startswith("/") and all(part not in ("", ".", "..")
            and not part.endswith((".", " ")) and not any(ord(c) < 32 for c in part)
            and part.lower() != ".git" and not any(c in part for c in '*?<>|"')
            and re.fullmatch(r"(CON|PRN|AUX|NUL|COM[1-9¹²³]|LPT[1-9¹²³])(?:\..*)?", part, re.I) is None
            for part in parts), "unsafe_path", "Unsafe relative path.")
    return PurePosixPath(value)


def contained(root, relative):
    path = root
    for part in relative_path(relative).parts:
        path = path / part
        if path.exists() or path.is_symlink():
            info = path.lstat()
            require(not stat.S_ISLNK(info.st_mode) and not getattr(
                info, "st_file_attributes", 0) & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400),
                "unsafe_path", "Symlinks and reparse points are not supported.")
    require(path.resolve().is_relative_to(root.resolve()), "unsafe_path", "Path leaves selected root.")
    return path


def read_bytes(path):
    require(path.is_file(), "not_found", "A required record or document is missing.")
    with path.open("rb") as stream:
        raw = stream.read(MAX_FILE + 1)
    require(len(raw) <= MAX_FILE, "limit_exceeded", "Record exceeds the byte limit.")
    return raw


def text(raw):
    try:
        value = raw.decode("utf-8")
    except UnicodeError as exc:
        raise RecordError("unsupported_format", "Document is not UTF-8 text.") from exc
    require("\x00" not in value, "unsupported_format", "Binary documents are not supported.")
    return value


def required_strings(value, fields):
    for field in fields:
        require(isinstance(value.get(field), str) and value[field].strip(),
                "malformed_record", f"Missing or invalid {field}.")


def clipped(value, size):
    value = str(value)
    return {"text": value[:size], "truncated": len(value) > size}


def validate_checkpoint(value):
    fields = {"summary", "authority", "completed", "pending", "blockers", "evidence", "next_action"}
    require(isinstance(value, dict) and set(value) == fields, "malformed_record", "Checkpoint fields are incomplete or unknown.")
    required_strings(value, ("summary", "authority", "next_action"))
    for key in ("summary", "authority", "next_action"):
        require(len(value[key]) <= 2048, "limit_exceeded", "Checkpoint text is too large.")
    for key in ("completed", "pending", "blockers", "evidence"):
        require(isinstance(value[key], list) and len(value[key]) <= 32 and
                all(isinstance(item, str) and item.strip() and len(item) <= 1024 for item in value[key]),
                "malformed_record", "Checkpoint lists require bounded nonempty strings.")


def source_head(root):
    try:
        result = subprocess.run(["git", "-C", str(root), "rev-parse", "HEAD"], capture_output=True, timeout=10, check=False)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise RecordError("provider_unavailable", "Git source identity is unavailable.") from exc
    head = result.stdout.decode("ascii", errors="replace").strip()
    require(result.returncode == 0 and len(head) in (40, 64) and all(c in "0123456789abcdef" for c in head),
            "provider_unavailable", "A committed Git repository is required.")
    return head
