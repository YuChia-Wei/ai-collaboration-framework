"""Closed-data and portable-path checks for the distribution boundary."""

from __future__ import annotations

import json
import math
import re
from typing import Any


class DistributionError(ValueError):
    """An actionable selection, input or output failure."""
    def __init__(self, message, code=None):
        super().__init__(message)
        prefix = message.split(":", 1)[0]
        known = {"unsupported-write", "unsupported-version", "unsupported-adapter", "unsupported-engine", "unsupported-generator",
                 "selection-unavailable", "dependency-closure", "dependency-version", "dependency-cycle", "reference-closure",
                 "binding-unresolved", "identity-mismatch"}
        self.code = code or (prefix if prefix in known else "invalid-shape")
        self.outcome = "unsupported" if self.code.startswith("unsupported-") else "blocked"



def require(condition: bool, message: str) -> None:
    if not condition:
        raise DistributionError(message)


def mapping(value: Any, required: set[str], optional: set[str], label: str) -> dict:
    require(type(value) is dict, f"{label}: expected an object")
    require(all(type(key) is str for key in value), f"{label}: keys must be strings")
    missing, extra = required - value.keys(), value.keys() - required - optional
    require(not missing and not extra,
            f"{label}: missing keys {sorted(missing)}, unknown keys {sorted(extra)}")
    return value


def sequence(value: Any, label: str) -> list:
    require(type(value) is list and len(value) <= 4096, f"{label}: expected a bounded array")
    return value


def string(value: Any, label: str) -> str:
    require(type(value) is str and bool(value.strip()), f"{label}: expected non-empty text")
    return value


def identifier(value: Any, label: str) -> str:
    value = string(value, label)
    require(re.fullmatch(r"[a-z][a-z0-9-]*(\.[a-z][a-z0-9-]*)*", value) is not None,
            f"{label}: invalid package identifier {value!r}")
    return value


def version(value: Any, label: str) -> str:
    value = string(value, label)
    require(re.fullmatch(r"(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)", value) is not None,
            f"{label}: expected exact MAJOR.MINOR.PATCH")
    return value


def distribution_version(value: Any, label: str) -> str:
    """An explicit distribution label, separate from component exact versions."""
    value = string(value, label)
    require(re.fullmatch(r"(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)(?:-rc\.[1-9][0-9]*)?", value) is not None,
            f"{label}: expected canonical MAJOR.MINOR.PATCH or MAJOR.MINOR.PATCH-rc.N (N > 0)")
    return value


def _candidate_identity(commit: str, digest: str, release_version: str | None) -> str:
    """Identity over complete metadata; callers validate selection and digests."""
    prefix = "development" if release_version is None else "versioned:" + distribution_version(release_version, "release_version")
    return f"{prefix}:{commit}:{digest}"


def version_one(value: Any, label: str) -> None:
    require(type(value) is int and value == 1, f"{label}: only integer version 1 is supported")


def path(value: Any, label: str) -> str:
    """A conservative portable exact path, never a glob, traversal or OS alias."""
    value = string(value, label)
    require(re.fullmatch(r"[A-Za-z0-9_.\-/]+", value) is not None,
            f"{label}: use an exact portable relative path, without escapes or globs")
    parts = value.split("/")
    require(all(part and part not in {".", ".."} and not part.endswith(".") for part in parts),
            f"{label}: absolute, empty or traversal segments are forbidden")
    for part in parts:
        stem = part.split(".")[0].upper()
        require(stem not in {"CON", "PRN", "AUX", "NUL"}
                and re.fullmatch(r"(?:COM|LPT)[1-9]", stem) is None,
                f"{label}: reserved filesystem name {part!r}")
    return value


class Paths:
    """Detect duplicate files, case aliases (including directories) and prefix conflicts."""

    def __init__(self) -> None:
        self.nodes: dict[str, tuple[str, bool, str]] = {}

    def add(self, value: str, owner: str) -> None:
        path(value, owner)
        parts = value.split("/")
        for index in range(1, len(parts) + 1):
            name = "/".join(parts[:index])
            is_file = index == len(parts)
            prior = self.nodes.get(name.casefold())
            if prior:
                require(prior[0] == name and not prior[1] and not is_file,
                        f"path collision: {name!r} ({owner}) conflicts with {prior[0]!r} ({prior[2]})")
            else:
                self.nodes[name.casefold()] = (name, is_file, owner)


def yaml_object(raw: bytes, label: str) -> dict:
    """JSON-model YAML only: no duplicate keys, aliases, explicit tags or merges."""
    try:
        import yaml
    except ImportError as exc:
        raise DistributionError("PyYAML >=6,<7 is required; provision it explicitly before building") from exc
    require(yaml.__version__.split(".")[0] == "6", "Only PyYAML >=6,<7 is supported")
    try:
        require(len(raw) <= 256 * 1024 and not raw.startswith(b"\xef\xbb\xbf"), f"{label}: YAML byte budget/BOM")
        text = raw.decode("utf-8", errors="strict")
        depth = count = 0
        for event in yaml.parse(text, Loader=yaml.SafeLoader):
            count += 1
            if isinstance(event, (yaml.events.MappingStartEvent, yaml.events.SequenceStartEvent)): depth += 1
            if isinstance(event, (yaml.events.MappingEndEvent, yaml.events.SequenceEndEvent)): depth -= 1
            require(count <= 100000 and depth <= 48, f"{label}: YAML structural budget")
            require(not isinstance(event, yaml.events.AliasEvent), f"{label}: YAML aliases are forbidden")
            require(getattr(event, "anchor", None) is None, f"{label}: YAML anchors are forbidden")
            require(getattr(event, "tag", None) is None, f"{label}: explicit YAML tags are forbidden")
        node = yaml.compose(text, Loader=yaml.SafeLoader)

        def convert(item):
            tag = item.tag.removeprefix("tag:yaml.org,2002:")
            if isinstance(item, yaml.nodes.MappingNode):
                require(tag == "map", f"{label}: unsupported mapping tag")
                result = {}
                for key_node, value_node in item.value:
                    require(key_node.tag == "tag:yaml.org,2002:str", f"{label}: keys must be strings")
                    key = key_node.value
                    require(key not in result and key != "<<", f"{label}: duplicate or merge key {key!r}")
                    result[key] = convert(value_node)
                return result
            if isinstance(item, yaml.nodes.SequenceNode):
                require(tag == "seq", f"{label}: unsupported sequence tag")
                return [convert(child) for child in item.value]
            require(tag in {"str", "null", "bool", "int", "float"}, f"{label}: non-JSON scalar {tag}")
            if tag == "str":
                return item.value
            value = yaml.safe_load(item.value)
            require(type(value) in {type(None), bool, int, float}, f"{label}: invalid scalar")
            require(type(value) is not float or math.isfinite(value), f"{label}: non-finite number")
            return value

        require(node is not None, f"{label}: empty YAML document")
        result = convert(node)
        require(type(result) is dict, f"{label}: expected an object")
        from .installation_state import _bounded
        _bounded(result, allow_floats=True)
        return result
    except (UnicodeError, yaml.YAMLError, RecursionError) as exc:
        raise DistributionError(f"{label}: invalid UTF-8 or restricted YAML") from exc


def json_bytes(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2,
                       allow_nan=False) + "\n").encode("utf-8")


def json_object(raw: bytes, label: str) -> dict:
    require(len(raw) <= 4 * 1024 * 1024 and not raw.startswith(b"\xef\xbb\xbf"), f"{label}: JSON byte budget/BOM")
    def pairs(items):
        result = {}
        for key, value in items:
            require(key not in result, f"{label}: duplicate JSON key {key!r}")
            result[key] = value
        return result

    def invalid_constant(value):
        raise DistributionError(f"{label}: non-finite JSON value {value}")

    def finite_float(value):
        number = float(value)
        require(math.isfinite(number), f"{label}: non-finite JSON number")
        return number

    try:
        result = json.loads(raw.decode("utf-8"), object_pairs_hook=pairs,
                            parse_constant=invalid_constant, parse_float=finite_float)
    except (UnicodeError, json.JSONDecodeError, RecursionError) as exc:
        raise DistributionError(f"{label}: invalid UTF-8 JSON") from exc
    require(type(result) is dict, f"{label}: expected an object")
    from .installation_state import _bounded
    _bounded(result, allow_floats=True)
    return result
