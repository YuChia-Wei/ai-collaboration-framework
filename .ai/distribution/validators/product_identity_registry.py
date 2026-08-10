"""Load and validate the source-only product identity registry."""

from __future__ import annotations

import re
from pathlib import Path, PurePosixPath
from typing import Any

import yaml


SCHEMA_VERSION = "1.0"
REGISTRY_KEYS = {
    "schema_version",
    "schema",
    "registry_id",
    "issue",
    "status",
    "owner_skill",
    "identity_records",
    "bindings",
    "future_namespaces",
    "consumer_contracts",
}
RECORD_KEYS = {
    "id",
    "kind",
    "canonical_value",
    "display_name",
    "owner",
    "scope",
    "version_authority",
    "status",
    "forms",
    "aliases",
    "deprecation_policy",
}
ALIAS_KEYS = {"id", "value", "status", "scope", "deprecation_policy"}
DEPRECATION_KEYS = {
    "mode",
    "replacement",
    "removal_target",
    "historical_rewrite",
    "notes",
}
BINDING_KEYS = {"id", "source", "target", "relationship", "rationale"}
FUTURE_KEYS = {
    "id",
    "scope",
    "status",
    "naming_rule",
    "authority",
    "prohibited_assumptions",
}
COMMON_CONSUMER_KEYS = {"id", "kind"}
CONSUMER_KEYS = {
    "yaml-value": COMMON_CONSUMER_KEYS
    | {"path", "selector", "identity_id", "identity_field"},
    "text-contains": COMMON_CONSUMER_KEYS
    | {"path", "identity_id", "identity_field"},
    "release-family": COMMON_CONSUMER_KEYS
    | {"path_glob", "release_identity_id", "package_identity_id"},
    "skill-transition": COMMON_CONSUMER_KEYS
    | {"path", "canonical_skill_ids"},
}
IDENTITY_KINDS = {
    "repository",
    "public-product",
    "framework-release",
    "technology-profile",
    "archive-package",
    "canonical-skill",
}
REQUIRED_KINDS = {
    "repository",
    "public-product",
    "framework-release",
    "technology-profile",
    "archive-package",
}
RECORD_STATUSES = {"active"}
ALIAS_STATUSES = {
    "redirect-compatible",
    "immutable-published-instance",
    "deprecated-compatible",
}
DEPRECATION_MODES = {"none", "compatibility", "immutable"}
RELATIONSHIPS = {
    "must-remain-distinct",
    "derives-name-from",
    "shares-version-with",
}
ID_RE = re.compile(r"^[a-z][a-z0-9.-]*$")


class IdentityRegistryError(RuntimeError):
    """Raised when identity data or a declared consumer cannot be trusted."""


def _exact_mapping(value: object, keys: set[str], location: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise IdentityRegistryError(f"{location} must be a mapping")
    missing = sorted(keys - set(value))
    unknown = sorted(set(value) - keys)
    if missing:
        raise IdentityRegistryError(
            f"{location} is missing required keys: {', '.join(missing)}"
        )
    if unknown:
        raise IdentityRegistryError(
            f"{location} has unknown keys: {', '.join(unknown)}"
        )
    return value


def _non_empty_string(value: object, location: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise IdentityRegistryError(f"{location} must be a non-empty string")
    return value


def _stable_id(value: object, location: str) -> str:
    value = _non_empty_string(value, location)
    if not ID_RE.fullmatch(value):
        raise IdentityRegistryError(
            f"{location} must use lowercase letters, digits, dots, and hyphens"
        )
    return value


def _string_list(value: object, location: str) -> list[str]:
    if not isinstance(value, list) or not value:
        raise IdentityRegistryError(f"{location} must be a non-empty list")
    if any(not isinstance(item, str) or not item for item in value):
        raise IdentityRegistryError(f"{location} entries must be non-empty strings")
    if len(value) != len(set(value)):
        raise IdentityRegistryError(f"{location} must not contain duplicates")
    return list(value)


def _repo_file(root: Path, value: object, location: str) -> Path:
    relative = _non_empty_string(value, location)
    if (
        chr(92) in relative
        or relative.startswith(("/", "./"))
        or relative.endswith("/")
        or ".." in PurePosixPath(relative).parts
        or any(token in relative for token in ("*", "?", "[", "]", "{", "}"))
    ):
        raise IdentityRegistryError(
            f"{location} must be an exact repository-relative file"
        )
    root = root.resolve()
    path = (root / relative).resolve()
    if root not in path.parents or not path.is_file():
        raise IdentityRegistryError(f"{location} does not exist: {relative}")
    return path


def _load_yaml(path: Path, location: str) -> dict[str, Any]:
    try:
        value = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, yaml.YAMLError) as exc:
        raise IdentityRegistryError(f"cannot load {location}: {exc}") from exc
    if not isinstance(value, dict):
        raise IdentityRegistryError(f"{location} root must be a mapping")
    return value


def _deprecation_policy(
    value: object,
    location: str,
    *,
    allowed_replacements: set[str] | None = None,
) -> dict[str, Any]:
    policy = _exact_mapping(value, DEPRECATION_KEYS, location)
    mode = policy["mode"]
    if mode not in DEPRECATION_MODES:
        raise IdentityRegistryError(
            f"{location}.mode must be one of {sorted(DEPRECATION_MODES)}"
        )
    replacement = policy["replacement"]
    if replacement is not None and (
        not isinstance(replacement, str)
        or (
            allowed_replacements is not None
            and replacement not in allowed_replacements
        )
    ):
        raise IdentityRegistryError(
            f"{location}.replacement must be null or a registered identity id"
        )
    removal_target = policy["removal_target"]
    if removal_target is not None and (
        not isinstance(removal_target, str) or not removal_target
    ):
        raise IdentityRegistryError(
            f"{location}.removal_target must be null or a non-empty string"
        )
    if policy["historical_rewrite"] is not False:
        raise IdentityRegistryError(f"{location}.historical_rewrite must be false")
    _non_empty_string(policy["notes"], f"{location}.notes")
    if mode == "none" and replacement is not None:
        raise IdentityRegistryError(
            f"{location}.replacement must be null when mode is none"
        )
    return policy


def _identity_field(record: dict[str, Any], field: str, location: str) -> str:
    parts = field.split(".")
    value: object = record
    for part in parts:
        if not isinstance(value, dict) or part not in value:
            raise IdentityRegistryError(
                f"{location} references missing identity field {field}"
            )
        value = value[part]
    return _non_empty_string(value, f"{location}.{field}")


def _yaml_selector(value: dict[str, Any], selector: str, location: str) -> object:
    current: object = value
    for part in selector.split("."):
        if not isinstance(current, dict) or part not in current:
            raise IdentityRegistryError(
                f"{location} selector does not exist: {selector}"
            )
        current = current[part]
    return current


def records_by_id(registry: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {record["id"]: record for record in registry["identity_records"]}


def alias_by_id(record: dict[str, Any], alias_id: str) -> dict[str, Any] | None:
    return next(
        (alias for alias in record["aliases"] if alias["id"] == alias_id),
        None,
    )


def _validate_consumers(
    root: Path,
    consumers: list[dict[str, Any]],
    records: dict[str, dict[str, Any]],
) -> None:
    consumer_ids: set[str] = set()
    covered_records: set[str] = set()
    for index, raw in enumerate(consumers):
        location = f"registry.consumer_contracts[{index}]"
        if not isinstance(raw, dict):
            raise IdentityRegistryError(f"{location} must be a mapping")
        kind = raw.get("kind")
        if kind not in CONSUMER_KEYS:
            raise IdentityRegistryError(
                f"{location}.kind must be one of {sorted(CONSUMER_KEYS)}"
            )
        consumer = _exact_mapping(raw, CONSUMER_KEYS[kind], location)
        consumer_id = _stable_id(consumer["id"], f"{location}.id")
        if consumer_id in consumer_ids:
            raise IdentityRegistryError(f"duplicate consumer id: {consumer_id}")
        consumer_ids.add(consumer_id)

        if kind in {"yaml-value", "text-contains"}:
            identity_id = consumer["identity_id"]
            if identity_id not in records:
                raise IdentityRegistryError(
                    f"{location}.identity_id is unknown: {identity_id}"
                )
            covered_records.add(identity_id)
            expected = _identity_field(
                records[identity_id],
                _non_empty_string(
                    consumer["identity_field"], f"{location}.identity_field"
                ),
                location,
            )
            path = _repo_file(root, consumer["path"], f"{location}.path")
            if kind == "yaml-value":
                actual = _yaml_selector(
                    _load_yaml(path, str(consumer["path"])),
                    _non_empty_string(
                        consumer["selector"], f"{location}.selector"
                    ),
                    location,
                )
                if actual != expected:
                    raise IdentityRegistryError(
                        f"{consumer_id} consumer drift: expected {expected!r}, "
                        f"found {actual!r}"
                    )
            else:
                try:
                    text = path.read_text(encoding="utf-8")
                except (OSError, UnicodeDecodeError) as exc:
                    raise IdentityRegistryError(
                        f"cannot read {consumer['path']}: {exc}"
                    ) from exc
                if expected not in text:
                    raise IdentityRegistryError(
                        f"{consumer_id} consumer drift: {expected!r} is absent"
                    )
            continue

        if kind == "release-family":
            release_id = consumer["release_identity_id"]
            package_id = consumer["package_identity_id"]
            if release_id not in records or package_id not in records:
                raise IdentityRegistryError(
                    f"{location} references an unknown release or package identity"
                )
            covered_records.update({release_id, package_id})
            pattern = _non_empty_string(
                consumer["path_glob"], f"{location}.path_glob"
            )
            if (
                chr(92) in pattern
                or pattern.startswith(("/", "./"))
                or ".." in PurePosixPath(pattern).parts
            ):
                raise IdentityRegistryError(
                    f"{location}.path_glob must be repository-relative"
                )
            paths = sorted(root.glob(pattern))
            if not paths:
                raise IdentityRegistryError(f"{consumer_id} matched no release records")
            release_template = records[release_id]["canonical_value"]
            package_template = records[package_id]["canonical_value"]
            for path in paths:
                data = _load_yaml(path, path.relative_to(root).as_posix())
                version_value = data.get("version")
                if (
                    not isinstance(version_value, str)
                    or not re.fullmatch(r"v\d+\.\d+\.\d+", version_value)
                ):
                    raise IdentityRegistryError(
                        f"{path.relative_to(root).as_posix()}: invalid release version"
                    )
                version = version_value[1:]
                if data.get("release_id") != release_template.format(version=version):
                    raise IdentityRegistryError(
                        f"{path.relative_to(root).as_posix()}: release identity drift"
                    )
                distribution = data.get("distribution")
                if isinstance(distribution, dict) and distribution.get("package_id") is not None:
                    expected_package = package_template.format(version=version)
                    if distribution.get("package_id") != expected_package:
                        raise IdentityRegistryError(
                            f"{path.relative_to(root).as_posix()}: package identity drift"
                        )
            continue

        canonical_ids = _string_list(
            consumer["canonical_skill_ids"],
            f"{location}.canonical_skill_ids",
        )
        if any(item not in records for item in canonical_ids):
            raise IdentityRegistryError(
                f"{location}.canonical_skill_ids contains an unknown identity"
            )
        covered_records.update(canonical_ids)
        transition = _load_yaml(
            _repo_file(root, consumer["path"], f"{location}.path"),
            str(consumer["path"]),
        )
        transitions = transition.get("transitions")
        if not isinstance(transitions, list):
            raise IdentityRegistryError(
                f"{consumer_id} transitions must be a list"
            )
        actual = {
            (item.get("current_identifier"), item.get("candidate_identifier"))
            for item in transitions
            if isinstance(item, dict)
        }
        expected_pairs: set[tuple[str, str]] = set()
        for identity_id in canonical_ids:
            record = records[identity_id]
            for alias in record["aliases"]:
                if alias["status"] == "deprecated-compatible":
                    expected_pairs.add((alias["value"], record["canonical_value"]))
        if actual != expected_pairs:
            raise IdentityRegistryError(
                f"{consumer_id} skill transition drift: "
                f"expected={sorted(expected_pairs)}, actual={sorted(actual)}"
            )

    uncovered = sorted(set(records) - covered_records)
    if uncovered:
        raise IdentityRegistryError(
            "identity records must have at least one declared consumer: "
            + ", ".join(uncovered)
        )


def load_identity_registry(
    root: Path,
    relative_path: str,
    *,
    validate_consumers: bool = True,
) -> dict[str, Any]:
    """Load one registry and fail closed on identity or consumer ambiguity."""
    registry_path = _repo_file(root, relative_path, "identity registry path")
    registry = _exact_mapping(
        _load_yaml(registry_path, relative_path),
        REGISTRY_KEYS,
        "registry",
    )
    if registry["schema_version"] != SCHEMA_VERSION:
        raise IdentityRegistryError(
            f"registry.schema_version must be {SCHEMA_VERSION}"
        )
    expected_schema = ".ai/distribution/schemas/identity-registry.schema.yaml"
    if registry["schema"] != expected_schema:
        raise IdentityRegistryError(f"registry.schema must be {expected_schema}")
    _repo_file(root, registry["schema"], "registry.schema")
    _stable_id(registry["registry_id"], "registry.registry_id")
    if registry["issue"] != 166:
        raise IdentityRegistryError("registry.issue must be 166")
    if registry["status"] != "active":
        raise IdentityRegistryError("registry.status must be active")
    if registry["owner_skill"] != "ai-context-governance":
        raise IdentityRegistryError(
            "registry.owner_skill must be ai-context-governance"
        )

    raw_records = registry["identity_records"]
    if not isinstance(raw_records, list) or not raw_records:
        raise IdentityRegistryError(
            "registry.identity_records must be a non-empty list"
        )
    record_ids: set[str] = set()
    canonical_values: set[str] = set()
    record_surfaces: dict[str, set[str]] = {}
    alias_ids: set[str] = set()
    alias_values: set[str] = set()
    kinds: set[str] = set()
    normalized_records: list[dict[str, Any]] = []
    for index, raw in enumerate(raw_records):
        location = f"registry.identity_records[{index}]"
        record = _exact_mapping(raw, RECORD_KEYS, location)
        identity_id = _stable_id(record["id"], f"{location}.id")
        if identity_id in record_ids:
            raise IdentityRegistryError(f"duplicate canonical identity id: {identity_id}")
        record_ids.add(identity_id)
        kind = record["kind"]
        if kind not in IDENTITY_KINDS:
            raise IdentityRegistryError(
                f"{location}.kind must be one of {sorted(IDENTITY_KINDS)}"
            )
        kinds.add(kind)
        canonical = _non_empty_string(
            record["canonical_value"], f"{location}.canonical_value"
        )
        if canonical.casefold() in canonical_values:
            raise IdentityRegistryError(
                f"duplicate canonical identity value: {canonical}"
            )
        canonical_values.add(canonical.casefold())
        for field in ("display_name", "owner", "scope", "version_authority"):
            _non_empty_string(record[field], f"{location}.{field}")
        if record["status"] not in RECORD_STATUSES:
            raise IdentityRegistryError(
                f"{location}.status must be one of {sorted(RECORD_STATUSES)}"
            )
        forms = record["forms"]
        if not isinstance(forms, dict) or not forms:
            raise IdentityRegistryError(f"{location}.forms must be a non-empty mapping")
        surface = {canonical.casefold()}
        for key, value in forms.items():
            if not isinstance(key, str) or not re.fullmatch(
                r"^[a-z][a-z0-9_]*$", key
            ):
                raise IdentityRegistryError(
                    f"{location}.forms keys must use lowercase snake_case"
                )
            surface.add(_non_empty_string(value, f"{location}.forms.{key}").casefold())
        aliases = record["aliases"]
        if not isinstance(aliases, list):
            raise IdentityRegistryError(f"{location}.aliases must be a list")
        normalized_aliases: list[dict[str, Any]] = []
        for alias_index, raw_alias in enumerate(aliases):
            alias_location = f"{location}.aliases[{alias_index}]"
            alias = _exact_mapping(raw_alias, ALIAS_KEYS, alias_location)
            alias_id = _stable_id(alias["id"], f"{alias_location}.id")
            if alias_id in alias_ids:
                raise IdentityRegistryError(f"duplicate alias id: {alias_id}")
            alias_ids.add(alias_id)
            alias_value = _non_empty_string(
                alias["value"], f"{alias_location}.value"
            )
            if alias_value.casefold() in alias_values:
                raise IdentityRegistryError(
                    f"ambiguous alias value: {alias_value}"
                )
            alias_values.add(alias_value.casefold())
            surface.add(alias_value.casefold())
            if alias["status"] not in ALIAS_STATUSES:
                raise IdentityRegistryError(
                    f"{alias_location}.status must be one of {sorted(ALIAS_STATUSES)}"
                )
            _non_empty_string(alias["scope"], f"{alias_location}.scope")
            normalized_aliases.append(dict(alias))
        _deprecation_policy(record["deprecation_policy"], f"{location}.deprecation_policy")
        normalized = dict(record)
        normalized["aliases"] = normalized_aliases
        normalized_records.append(normalized)
        record_surfaces[identity_id] = surface

    if not REQUIRED_KINDS <= kinds:
        raise IdentityRegistryError(
            "registry is missing required identity kinds: "
            + ", ".join(sorted(REQUIRED_KINDS - kinds))
        )
    if record_ids & alias_ids:
        raise IdentityRegistryError(
            "alias ids must not equal canonical identity ids: "
            + ", ".join(sorted(record_ids & alias_ids))
        )
    seen_surfaces: dict[str, str] = {}
    for identity_id, surfaces in record_surfaces.items():
        for value in surfaces:
            previous = seen_surfaces.get(value)
            if previous is not None and previous != identity_id:
                raise IdentityRegistryError(
                    f"identity value {value!r} is coupled to both "
                    f"{previous} and {identity_id}"
                )
            seen_surfaces[value] = identity_id
    if canonical_values & alias_values:
        overlap = sorted(canonical_values & alias_values)
        raise IdentityRegistryError(
            f"alias values must not equal canonical values: {overlap}"
        )

    records = {record["id"]: record for record in normalized_records}
    for index, record in enumerate(normalized_records):
        _deprecation_policy(
            record["deprecation_policy"],
            f"registry.identity_records[{index}].deprecation_policy",
            allowed_replacements=set(records),
        )
        for alias_index, alias in enumerate(record["aliases"]):
            _deprecation_policy(
                alias["deprecation_policy"],
                f"registry.identity_records[{index}].aliases[{alias_index}].deprecation_policy",
                allowed_replacements=set(records),
            )

    raw_bindings = registry["bindings"]
    if not isinstance(raw_bindings, list) or not raw_bindings:
        raise IdentityRegistryError("registry.bindings must be a non-empty list")
    binding_ids: set[str] = set()
    separation_found = False
    for index, raw in enumerate(raw_bindings):
        location = f"registry.bindings[{index}]"
        binding = _exact_mapping(raw, BINDING_KEYS, location)
        binding_id = _stable_id(binding["id"], f"{location}.id")
        if binding_id in binding_ids:
            raise IdentityRegistryError(f"duplicate binding id: {binding_id}")
        binding_ids.add(binding_id)
        if binding["source"] not in records or binding["target"] not in records:
            raise IdentityRegistryError(f"{location} references an unknown identity")
        if binding["source"] == binding["target"]:
            raise IdentityRegistryError(f"{location} cannot self-bind")
        if binding["relationship"] not in RELATIONSHIPS:
            raise IdentityRegistryError(
                f"{location}.relationship must be one of {sorted(RELATIONSHIPS)}"
            )
        _non_empty_string(binding["rationale"], f"{location}.rationale")
        source_kind = records[binding["source"]]["kind"]
        target_kind = records[binding["target"]]["kind"]
        if (
            binding["relationship"] == "must-remain-distinct"
            and {source_kind, target_kind} == {"repository", "public-product"}
        ):
            separation_found = True
    if not separation_found:
        raise IdentityRegistryError(
            "registry must bind repository and public product as must-remain-distinct"
        )

    raw_future = registry["future_namespaces"]
    if not isinstance(raw_future, list) or not raw_future:
        raise IdentityRegistryError(
            "registry.future_namespaces must be a non-empty list"
        )
    future_ids: set[str] = set()
    for index, raw in enumerate(raw_future):
        location = f"registry.future_namespaces[{index}]"
        future = _exact_mapping(raw, FUTURE_KEYS, location)
        future_id = _stable_id(future["id"], f"{location}.id")
        if future_id in future_ids:
            raise IdentityRegistryError(f"duplicate future namespace id: {future_id}")
        future_ids.add(future_id)
        if future["status"] != "reserved-rule-only":
            raise IdentityRegistryError(
                f"{location}.status must be reserved-rule-only"
            )
        for field in ("scope", "naming_rule", "authority"):
            _non_empty_string(future[field], f"{location}.{field}")
        _string_list(
            future["prohibited_assumptions"],
            f"{location}.prohibited_assumptions",
        )

    registry["identity_records"] = normalized_records
    consumers = registry["consumer_contracts"]
    if not isinstance(consumers, list) or not consumers:
        raise IdentityRegistryError(
            "registry.consumer_contracts must be a non-empty list"
        )
    if validate_consumers:
        _validate_consumers(root.resolve(), consumers, records)
    return registry
