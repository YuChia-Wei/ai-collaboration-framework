"""Shared, deliberately limited structure and authority contract for execution artifacts.

This is not a general JSON Schema implementation. Unknown keywords fail closed.
Semantic validation remains with the canonical guardrail/delegation validators.
"""
from __future__ import annotations

import copy
import importlib.util
import math
import sys
from pathlib import Path
from typing import Any

import yaml
import artifact_core as CORE

GUARD_SCHEMA = ".ai/assets/shared/agent-execution-guardrails.schema.yaml"
EXTERNAL_SCHEMA = ".ai/assets/skills/software-development-orchestrator/templates/external-task-delegation.schema.yaml"
GUARD_VALIDATOR = ".ai/scripts/validate-agent-execution-guardrails.py"
EXTERNAL_VALIDATOR = ".ai/assets/skills/software-development-orchestrator/scripts/validate-external-task-delegation.py"
# Mandatory dependencies, not a caller-selected list. Role and skill are added
# from the validated packet. These bind current validation, not past execution.
AUTHORITY_REFS = (
    GUARD_SCHEMA, EXTERNAL_SCHEMA, GUARD_VALIDATOR, EXTERNAL_VALIDATOR,
    ".ai/scripts/execution_artifact_contract.py", ".ai/scripts/execution-artifacts.py",
    ".ai/scripts/artifact_core.py",
    ".ai/scripts/python_prerequisites.py", ".ai/scripts/python-entrypoints.json",
    "requirements.txt",
    ".ai/assets/shared/AGENT-EXECUTION-GUARDRAILS-CONTRACT.md",
    ".ai/assets/shared/ROLE-EXECUTION-CONTRACT.md",
)
KEYWORDS = {"type", "properties", "required", "additionalProperties", "items", "enum", "const", "minimum", "minItems", "minLength", "description"}
TYPES = {"object", "array", "string", "integer", "number", "boolean", "null"}


class ContractError(ValueError):
    pass


class StrictLoader(yaml.SafeLoader):
    pass


def unique_mapping(loader: StrictLoader, node: Any, deep: bool = False) -> dict:
    return CORE.construct_unique_mapping(loader, node, flatten=True, deep=deep,
        key_error=lambda key, duplicate: yaml.YAMLError(f"duplicate mapping key: {key!r}" if duplicate else "mapping keys must be strings"))


StrictLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, unique_mapping)


def load_mapping(path: Path) -> dict:
    value = yaml.load(path.read_text(encoding="utf-8"), Loader=StrictLoader)
    if not isinstance(value, dict):
        raise ContractError("artifact must be a mapping")
    return value


def encoded(value: Any) -> bytes:
    return yaml.safe_dump(value, sort_keys=False, allow_unicode=True).encode("utf-8")


def sha256(value: bytes) -> str:
    return CORE.sha256(value)


def digest(value: Any) -> str:
    return sha256(CORE.canonical_json(value))


def load_module(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ContractError("canonical validator cannot be loaded")
    module = importlib.util.module_from_spec(spec)
    previous = sys.modules.get(name)
    sys.modules[name] = module
    try:
        spec.loader.exec_module(module)
    except BaseException:
        if previous is None:
            sys.modules.pop(name, None)
        else:
            sys.modules[name] = previous
        raise
    return module


def schema_errors(model: Any, label: str = "model") -> list[str]:
    if not isinstance(model, dict):
        return [f"{label} must be a schema mapping"]
    errors = [f"{label}: unsupported schema keyword {key}" for key in model if key not in KEYWORDS]
    kinds = model.get("type")
    kinds = kinds if isinstance(kinds, list) else [kinds]
    if not kinds or any(not isinstance(kind, str) or kind not in TYPES for kind in kinds) or len(set(str(k) for k in kinds)) != len(kinds):
        return errors + [f"{label}.type is invalid"]
    for key in ("minimum", "minItems", "minLength"):
        if key in model and (type(model[key]) is not int or model[key] < 0):
            errors.append(f"{label}.{key} must be a non-negative integer")
    if "enum" in model and (not isinstance(model["enum"], list) or not model["enum"]):
        errors.append(f"{label}.enum must be non-empty")
    for keyword, applicable in (("minimum", {"integer", "number"}), ("minItems", {"array"}), ("minLength", {"string"})):
        if keyword in model and not applicable.intersection(kinds):
            errors.append(f"{label}: {keyword} does not apply to its type")
    if "object" in kinds:
        props, required = model.get("properties"), model.get("required")
        if not isinstance(props, dict) or not isinstance(required, list) or any(not isinstance(k, str) for k in required):
            return errors + [f"{label} requires properties and required"]
        if len(required) != len(set(required)) or not set(required) <= set(props):
            errors.append(f"{label}.required must uniquely select declared properties")
        extra = model.get("additionalProperties")
        if extra is not False and not isinstance(extra, dict):
            errors.append(f"{label}.additionalProperties must be false or a schema")
        elif isinstance(extra, dict):
            errors.extend(schema_errors(extra, f"{label}.additionalProperties"))
        for key, child in props.items():
            errors.extend(schema_errors(child, f"{label}.{key}"))
    elif any(key in model for key in ("properties", "required", "additionalProperties")):
        errors.append(f"{label}: object keywords require object type")
    if "array" in kinds:
        errors.extend(schema_errors(model.get("items"), f"{label}.items"))
    elif "items" in model:
        errors.append(f"{label}: items requires array type")
    return errors


def validate_model(value: Any, model: dict, label: str) -> list[str]:
    errors = schema_errors(model)
    if errors:
        return errors

    def walk(item: Any, node: dict, path: str) -> None:
        kinds = node["type"] if isinstance(node["type"], list) else [node["type"]]
        valid = {"object": type(item) is dict, "array": type(item) is list, "string": type(item) is str, "integer": type(item) is int, "number": type(item) is int or (type(item) is float and math.isfinite(item)), "boolean": type(item) is bool, "null": item is None}
        if not any(valid[kind] for kind in kinds):
            errors.append(f"{path.rsplit('.', 1)[0]} is invalid: {path} must be {' or '.join(kinds)}")
            return
        if "const" in node and (type(item) is not type(node["const"]) or item != node["const"]):
            errors.append(f"{path} must equal its contract constant")
        if "enum" in node and not any(type(item) is type(v) and item == v for v in node["enum"]):
            errors.append(f"{path} is outside its allowed values")
        if item is None:
            return
        if isinstance(item, dict):
            props = node["properties"]
            for key in node["required"]:
                if key not in item:
                    errors.append(f"{path}.{key} is required")
            extra = set(item) - set(props)
            if extra and node["additionalProperties"] is False:
                errors.append(f"{path} contains unsupported fields: {', '.join(sorted(str(k) for k in extra))}")
            for key, nested in item.items():
                if not isinstance(key, str):
                    errors.append(f"{path} keys must be strings")
                elif key in props:
                    walk(nested, props[key], f"{path}.{key}")
                elif isinstance(node["additionalProperties"], dict):
                    walk(nested, node["additionalProperties"], f"{path}.{key}")
        elif isinstance(item, list):
            if len(item) < node.get("minItems", 0):
                errors.append(f"{path} has too few items")
            for index, nested in enumerate(item):
                walk(nested, node["items"], f"{path}[{index}]")
        elif isinstance(item, str) and len(item.strip()) < node.get("minLength", 0):
            errors.append(f"{path} must be non-empty")
        elif type(item) in (int, float) and item < node.get("minimum", -math.inf):
            errors.append(f"{path} is below its minimum")

    walk(value, model, label)
    return errors


def record_model(schema: dict, family: str, version: str) -> dict:
    model = schema.get("record_models", {}).get(family, {}).get(version)
    if not isinstance(model, dict):
        raise ContractError(f"{family}.schema_version {version!r} is unsupported; select an explicit supported migration")
    return model


def structure_errors(record: Any, schema: dict, family: str) -> list[str]:
    if not isinstance(record, dict):
        return [f"{family} must be a mapping"]
    try:
        return validate_model(record, record_model(schema, family, record.get("schema_version")), family)
    except (ContractError, TypeError) as exc:
        return [str(exc)]


def models_errors(schema: dict) -> list[str]:
    families = schema.get("record_models")
    if not isinstance(families, dict) or not families:
        return ["schema.record_models must be non-empty"]
    errors = []
    for family, versions in families.items():
        if not isinstance(versions, dict) or not versions:
            errors.append(f"record_models.{family} must contain versions")
            continue
        for version, model in versions.items():
            errors.extend(schema_errors(model, f"record_models.{family}.{version}"))
    return errors


def template_value(model: dict) -> Any:
    """Generate a visibly incomplete skeleton, never successful observations."""
    if "const" in model:
        return copy.deepcopy(model["const"])
    kinds = model["type"] if isinstance(model["type"], list) else [model["type"]]
    if "object" in kinds:
        return {key: template_value(child) for key, child in model["properties"].items()}
    if "array" in kinds:
        return [template_value(model["items"])]
    return "<required " + " or ".join(kinds) + ">"


def authority_manifest(root: Path, packet: dict) -> list[dict[str, str]]:
    role = packet["role"]["path"]
    skill = f".ai/assets/skills/{packet['owning_skill']}/skill.yaml"
    refs = sorted(set((*AUTHORITY_REFS, role, skill)))
    result = []
    for ref in refs:
        # The prerequisite guard supports an extracted payload whose governed
        # requirements live in its immediate package envelope. This fixed
        # logical key cannot be selected or redirected by an artifact caller.
        if ref == "requirements.txt" and not (root / ref).is_file():
            envelope = root.parent / ref
            if not envelope.is_file() or envelope.resolve() != envelope:
                raise ContractError("authority requires source or package-envelope requirements")
            result.append({"path": "package-envelope:requirements.txt", "sha256": sha256(envelope.read_bytes())})
            continue
        path = (root / ref).resolve()
        if path == root or root not in path.parents or path.relative_to(root).as_posix() != ref or not path.is_file():
            raise ContractError("authority requires existing canonical contained dependencies")
        result.append({"path": ref, "sha256": sha256(path.read_bytes())})
    return result


def manifest_errors(actual: Any, expected: list[dict]) -> list[str]:
    if not isinstance(actual, list) or any(not isinstance(item, dict) for item in actual):
        return ["authority_manifest must contain the exact current validation dependencies"]
    if [item.get("path") for item in actual] != [item["path"] for item in expected]:
        return ["authority_manifest dependency set or canonical ordering differs; a self-selected authority list is not admitted"]
    return [f"authority_manifest changed dependency: {item['path']}" for item, observed in zip(expected, actual) if observed != item]
