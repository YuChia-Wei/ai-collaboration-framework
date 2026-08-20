#!/usr/bin/env python3
"""Deterministic, read-only resolution of evidence-bound AI-context upgrade routes."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from hashlib import sha256
import json
from pathlib import Path, PurePosixPath
import re
from typing import Any

import yaml


SCHEMA_VERSION = "1.0"
ROUTE_KINDS = frozenset(
    {
        "direct",
        "orchestrated-multi-hop",
        "reconciliation-required",
        "unsupported",
    }
)
RETAINED_ORIGIN_ROLES = frozenset({"immediate-predecessor", "v0.9.0", "v0.6.0"})
EDGE_ARTIFACT_NAMES = ("archive", "checksum", "manifest", "validator")
DEPRECATION_EVIDENCE_NAMES = ("deprecation_notice", "owner_decision", "validator")
SHA256_RE = re.compile(r"[0-9a-f]{64}\Z")
SHA1_RE = re.compile(r"[0-9a-f]{40}\Z")
VERSION_RE = re.compile(r"v[0-9]+\.[0-9]+\.[0-9]+(?:[-+][0-9A-Za-z.-]+)?\Z")
VALIDATION_STATES = frozenset({"passed", "failed", "blocked", "not-run", "deferred-with-owner"})


class UpgradeRouteError(ValueError):
    """Base error for a route matrix that cannot produce governed evidence."""


class MatrixValidationError(UpgradeRouteError):
    """The matrix contract is incomplete, contradictory, or unsafe."""


def canonical_json(value: Any) -> str:
    """Return the sole JSON encoding used for resolver evidence."""

    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"


def sha256_bytes(value: bytes) -> str:
    """Return a lowercase SHA-256 digest for raw evidence bytes."""

    return sha256(value).hexdigest()


def load_route_matrix(matrix_path: Path) -> tuple[dict[str, Any], bytes]:
    """Read exactly one explicit matrix file without directory discovery."""

    try:
        raw = matrix_path.read_bytes()
    except OSError as exc:
        raise MatrixValidationError(f"cannot read matrix {matrix_path}: {exc}") from exc
    try:
        value = yaml.safe_load(raw)
    except yaml.YAMLError as exc:
        raise MatrixValidationError(f"cannot parse matrix {matrix_path}: {exc}") from exc
    if not isinstance(value, dict):
        raise MatrixValidationError("matrix must be a YAML mapping")
    return value, raw


def _mapping(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise MatrixValidationError(f"{label} must be a mapping")
    return value


def _list(value: Any, label: str) -> list[Any]:
    if not isinstance(value, list):
        raise MatrixValidationError(f"{label} must be a list")
    return value


def _string(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise MatrixValidationError(f"{label} must be a non-empty string")
    return value


def _exact_keys(value: Mapping[str, Any], expected: set[str], label: str) -> None:
    actual = set(value)
    missing = sorted(expected - actual)
    unexpected = sorted(actual - expected)
    if missing or unexpected:
        details: list[str] = []
        if missing:
            details.append(f"missing {', '.join(missing)}")
        if unexpected:
            details.append(f"unexpected {', '.join(unexpected)}")
        raise MatrixValidationError(f"{label} has {'; '.join(details)}")


def _version(value: Any, label: str) -> str:
    value = _string(value, label)
    if not VERSION_RE.fullmatch(value):
        raise MatrixValidationError(f"{label} must be a v-prefixed semantic version")
    return value


def _sha256(value: Any, label: str) -> str:
    value = _string(value, label)
    if not SHA256_RE.fullmatch(value):
        raise MatrixValidationError(f"{label} must be a lowercase SHA-256")
    return value


def _commit(value: Any, label: str) -> str:
    value = _string(value, label)
    if not SHA1_RE.fullmatch(value):
        raise MatrixValidationError(f"{label} must be a full lowercase Git SHA")
    return value


def _safe_relative_path(value: Any, label: str) -> str:
    value = _string(value, label)
    if "\\" in value:
        raise MatrixValidationError(f"{label} must use POSIX separators")
    path = PurePosixPath(value)
    if (
        path.is_absolute()
        or not path.parts
        or any(part in {"", ".", ".."} or ":" in part for part in path.parts)
    ):
        raise MatrixValidationError(f"{label} must be a safe matrix-relative path")
    return value


def _asset_identity(value: Any, label: str) -> dict[str, str]:
    data = _mapping(value, label)
    _exact_keys(data, {"asset_id", "path", "sha256"}, label)
    return {
        "asset_id": _string(data["asset_id"], f"{label}.asset_id"),
        "path": _safe_relative_path(data["path"], f"{label}.path"),
        "sha256": _sha256(data["sha256"], f"{label}.sha256"),
    }


def _validate_target(value: Any) -> dict[str, Any]:
    data = _mapping(value, "target")
    _exact_keys(data, {"version", "release_id", "commit", "manifest"}, "target")
    version = _version(data["version"], "target.version")
    if data["release_id"] != f"REL-{version}":
        raise MatrixValidationError("target.release_id must equal REL-target.version")
    return {
        "version": version,
        "release_id": data["release_id"],
        "commit": _commit(data["commit"], "target.commit"),
        "manifest": _asset_identity(data["manifest"], "target.manifest"),
    }


def _validate_retained_origins(value: Any) -> list[dict[str, Any]]:
    origins = _list(value, "retained_origins")
    roles: set[str] = set()
    versions: set[str] = set()
    result: list[dict[str, Any]] = []
    for index, item in enumerate(origins):
        label = f"retained_origins[{index}]"
        data = _mapping(item, label)
        _exact_keys(data, {"role", "version", "release_id", "commit", "manifest"}, label)
        role = _string(data["role"], f"{label}.role")
        if role not in RETAINED_ORIGIN_ROLES:
            raise MatrixValidationError(f"{label}.role is not a retained-origin role")
        version = _version(data["version"], f"{label}.version")
        if role in {"v0.9.0", "v0.6.0"} and version != role:
            raise MatrixValidationError(f"{label}.version must equal role {role}")
        if data["release_id"] != f"REL-{version}":
            raise MatrixValidationError(f"{label}.release_id must equal REL-version")
        if role in roles or version in versions:
            raise MatrixValidationError("retained origins must have unique roles and versions")
        roles.add(role)
        versions.add(version)
        result.append(
            {
                "role": role,
                "version": version,
                "release_id": data["release_id"],
                "commit": _commit(data["commit"], f"{label}.commit"),
                "manifest": _asset_identity(data["manifest"], f"{label}.manifest"),
            }
        )
    return result


def _validate_cutovers(value: Any) -> list[dict[str, Any]]:
    cutovers = _list(value, "semantic_cutovers")
    ids: set[str] = set()
    result: list[dict[str, Any]] = []
    for index, item in enumerate(cutovers):
        label = f"semantic_cutovers[{index}]"
        data = _mapping(item, label)
        _exact_keys(data, {"cutover_id", "required", "description"}, label)
        cutover_id = _string(data["cutover_id"], f"{label}.cutover_id")
        if cutover_id in ids:
            raise MatrixValidationError("semantic_cutovers.cutover_id values must be unique")
        if not isinstance(data["required"], bool):
            raise MatrixValidationError(f"{label}.required must be boolean")
        ids.add(cutover_id)
        result.append(
            {
                "cutover_id": cutover_id,
                "required": data["required"],
                "description": _string(data["description"], f"{label}.description"),
            }
        )
    return result


def _validate_edge(
    value: Any,
    label: str,
    expected_order: int,
    cutover_ids: set[str],
) -> dict[str, Any]:
    data = _mapping(value, label)
    _exact_keys(
        data,
        {
            "edge_id",
            "order",
            "from_version",
            "to_version",
            "artifacts",
            "semantic_cutovers",
            "validation",
        },
        label,
    )
    if data["order"] != expected_order:
        raise MatrixValidationError(f"{label}.order must be {expected_order} in list order")
    artifacts = _mapping(data["artifacts"], f"{label}.artifacts")
    _exact_keys(artifacts, set(EDGE_ARTIFACT_NAMES), f"{label}.artifacts")
    validation = _mapping(data["validation"], f"{label}.validation")
    _exact_keys(validation, {"state", "report"}, f"{label}.validation")
    validation_state = _string(validation["state"], f"{label}.validation.state")
    if validation_state not in VALIDATION_STATES:
        raise MatrixValidationError(f"{label}.validation.state is not supported")
    seen_cutovers: set[str] = set()
    edge_cutovers: list[dict[str, str]] = []
    for cutover_index, cutover in enumerate(_list(data["semantic_cutovers"], f"{label}.semantic_cutovers")):
        cutover_label = f"{label}.semantic_cutovers[{cutover_index}]"
        cutover_data = _mapping(cutover, cutover_label)
        _exact_keys(cutover_data, {"cutover_id", "state"}, cutover_label)
        cutover_id = _string(cutover_data["cutover_id"], f"{cutover_label}.cutover_id")
        state = _string(cutover_data["state"], f"{cutover_label}.state")
        if cutover_id not in cutover_ids:
            raise MatrixValidationError(f"{cutover_label}.cutover_id is not declared")
        if cutover_id in seen_cutovers:
            raise MatrixValidationError(f"{label}.semantic_cutovers must not duplicate cutover IDs")
        if state not in VALIDATION_STATES:
            raise MatrixValidationError(f"{cutover_label}.state is not supported")
        seen_cutovers.add(cutover_id)
        edge_cutovers.append({"cutover_id": cutover_id, "state": state})
    return {
        "edge_id": _string(data["edge_id"], f"{label}.edge_id"),
        "order": expected_order,
        "from_version": _version(data["from_version"], f"{label}.from_version"),
        "to_version": _version(data["to_version"], f"{label}.to_version"),
        "artifacts": {
            name: _asset_identity(artifacts[name], f"{label}.artifacts.{name}")
            for name in EDGE_ARTIFACT_NAMES
        },
        "semantic_cutovers": edge_cutovers,
        "validation": {
            "state": validation_state,
            "report": _asset_identity(validation["report"], f"{label}.validation.report"),
        },
    }


def _validate_routes(
    value: Any,
    retained_versions: set[str],
    target_version: str,
    cutover_ids: set[str],
) -> list[dict[str, Any]]:
    routes = _list(value, "routes")
    route_ids: set[str] = set()
    result: list[dict[str, Any]] = []
    for index, item in enumerate(routes):
        label = f"routes[{index}]"
        data = _mapping(item, label)
        _exact_keys(data, {"route_id", "origin", "target", "edges"}, label)
        route_id = _string(data["route_id"], f"{label}.route_id")
        if route_id in route_ids:
            raise MatrixValidationError("routes.route_id values must be unique")
        route_ids.add(route_id)
        origin = _version(data["origin"], f"{label}.origin")
        target = _version(data["target"], f"{label}.target")
        if origin not in retained_versions:
            raise MatrixValidationError(f"{label}.origin must be a retained origin")
        if target != target_version:
            raise MatrixValidationError(f"{label}.target must equal target.version")
        edge_values = _list(data["edges"], f"{label}.edges")
        if not edge_values:
            raise MatrixValidationError(f"{label}.edges must not be empty")
        edges = [
            _validate_edge(edge, f"{label}.edges[{edge_index}]", edge_index + 1, cutover_ids)
            for edge_index, edge in enumerate(edge_values)
        ]
        if edges[0]["from_version"] != origin:
            raise MatrixValidationError(f"{label}.edges[0].from_version must equal route origin")
        if edges[-1]["to_version"] != target:
            raise MatrixValidationError(f"{label}.edges[-1].to_version must equal route target")
        for previous, current in zip(edges, edges[1:]):
            if previous["to_version"] != current["from_version"]:
                raise MatrixValidationError(f"{label}.edges are not an exact continuous chain")
        result.append({"route_id": route_id, "origin": origin, "target": target, "edges": edges})
    return result


def _validate_deprecations(
    value: Any, retained_roles: set[str], retained_versions: set[str], target_version: str
) -> list[dict[str, Any]]:
    deprecations = _list(value, "deprecations")
    ids: set[str] = set()
    origins: set[str] = set()
    result: list[dict[str, Any]] = []
    for index, item in enumerate(deprecations):
        label = f"deprecations[{index}]"
        data = _mapping(item, label)
        _exact_keys(
            data,
            {
                "deprecation_id",
                "role",
                "origin",
                "target",
                "disposition",
                "complete",
                "reason",
                "evidence",
            },
            label,
        )
        deprecation_id = _string(data["deprecation_id"], f"{label}.deprecation_id")
        role = _string(data["role"], f"{label}.role")
        if role not in RETAINED_ORIGIN_ROLES:
            raise MatrixValidationError(f"{label}.role is not a retained-origin role")
        if role in retained_roles:
            raise MatrixValidationError("a retained-origin role cannot also be deprecated")
        origin = _version(data["origin"], f"{label}.origin")
        if role in {"v0.9.0", "v0.6.0"} and origin != role:
            raise MatrixValidationError(f"{label}.origin must equal role {role}")
        target = _version(data["target"], f"{label}.target")
        if deprecation_id in ids or origin in origins:
            raise MatrixValidationError("deprecations must have unique IDs and origins")
        if origin in retained_versions:
            raise MatrixValidationError("a retained origin cannot also be deprecated")
        if target != target_version:
            raise MatrixValidationError(f"{label}.target must equal target.version")
        if data["disposition"] != "unsupported":
            raise MatrixValidationError(f"{label}.disposition must be unsupported")
        if data["complete"] is not True:
            raise MatrixValidationError(f"{label}.complete must be true")
        evidence = _mapping(data["evidence"], f"{label}.evidence")
        _exact_keys(evidence, set(DEPRECATION_EVIDENCE_NAMES), f"{label}.evidence")
        ids.add(deprecation_id)
        origins.add(origin)
        result.append(
            {
                "deprecation_id": deprecation_id,
                "role": role,
                "origin": origin,
                "target": target,
                "disposition": "unsupported",
                "complete": True,
                "reason": _string(data["reason"], f"{label}.reason"),
                "evidence": {
                    name: _asset_identity(evidence[name], f"{label}.evidence.{name}")
                    for name in DEPRECATION_EVIDENCE_NAMES
                },
            }
        )
    return result


def validate_matrix(matrix: Mapping[str, Any]) -> dict[str, Any]:
    """Validate a matrix without discovering files or executing any asset."""

    data = _mapping(matrix, "matrix")
    required_keys = {
        "schema_version",
        "matrix_id",
        "target",
        "retained_origins",
        "semantic_cutovers",
        "routes",
        "deprecations",
    }
    _exact_keys(
        {key: value for key, value in data.items() if key != "template_metadata"},
        required_keys,
        "matrix",
    )
    if "template_metadata" in data:
        metadata = _mapping(data["template_metadata"], "template_metadata")
        _exact_keys(
            metadata,
            {"template_id", "template_version", "created_at", "updated_at"},
            "template_metadata",
        )
        for key in ("template_id", "template_version", "created_at", "updated_at"):
            _string(metadata[key], f"template_metadata.{key}")
    if data["schema_version"] != SCHEMA_VERSION:
        raise MatrixValidationError(f"matrix.schema_version must be {SCHEMA_VERSION}")
    target = _validate_target(data["target"])
    origins = _validate_retained_origins(data["retained_origins"])
    cutovers = _validate_cutovers(data["semantic_cutovers"])
    retained_versions = {item["version"] for item in origins}
    routes = _validate_routes(
        data["routes"],
        retained_versions,
        target["version"],
        {item["cutover_id"] for item in cutovers},
    )
    retained_roles = {item["role"] for item in origins}
    deprecations = _validate_deprecations(
        data["deprecations"], retained_roles, retained_versions, target["version"]
    )
    deprecated_roles = {item["role"] for item in deprecations}
    if retained_roles | deprecated_roles != RETAINED_ORIGIN_ROLES:
        raise MatrixValidationError(
            "retained_origins and deprecations must account for exactly "
            "immediate-predecessor, v0.9.0, and v0.6.0"
        )
    if len(deprecated_roles) != len(deprecations):
        raise MatrixValidationError("deprecations must have unique retained-origin roles")
    return {
        "schema_version": SCHEMA_VERSION,
        "matrix_id": _string(data["matrix_id"], "matrix.matrix_id"),
        "target": target,
        "retained_origins": origins,
        "semantic_cutovers": cutovers,
        "routes": routes,
        "deprecations": deprecations,
    }


def _asset_path(asset_root: Path, identity: Mapping[str, str]) -> Path:
    root = asset_root.resolve()
    candidate = (root / PurePosixPath(identity["path"])).resolve()
    try:
        candidate.relative_to(root)
    except ValueError as exc:
        raise MatrixValidationError(
            f"asset {identity['asset_id']} escapes the matrix directory"
        ) from exc
    return candidate


def _asset_diagnostic(
    asset_root: Path, identity: Mapping[str, str], context: Mapping[str, str]
) -> dict[str, str] | None:
    path = _asset_path(asset_root, identity)
    try:
        actual = sha256_bytes(path.read_bytes())
    except OSError:
        return {
            **context,
            "asset_id": identity["asset_id"],
            "code": "missing-asset",
            "path": identity["path"],
        }
    if actual != identity["sha256"]:
        return {
            **context,
            "actual_sha256": actual,
            "asset_id": identity["asset_id"],
            "code": "tampered-asset",
            "expected_sha256": identity["sha256"],
            "path": identity["path"],
        }
    return None


def _deprecation_evidence_errors(matrix: Mapping[str, Any], asset_root: Path) -> None:
    errors: list[str] = []
    for deprecation in matrix["deprecations"]:
        for name in DEPRECATION_EVIDENCE_NAMES:
            diagnostic = _asset_diagnostic(
                asset_root,
                deprecation["evidence"][name],
                {"deprecation_id": deprecation["deprecation_id"], "evidence": name},
            )
            if diagnostic is not None:
                errors.append(
                    f"{diagnostic['deprecation_id']}.{diagnostic['evidence']}: {diagnostic['code']}"
                )
    if errors:
        raise MatrixValidationError(
            "incomplete deprecation evidence invalidates matrix: " + ", ".join(sorted(errors))
        )


def _route_diagnostics(
    route: Mapping[str, Any], required_cutovers: set[str], asset_root: Path
) -> list[dict[str, str]]:
    diagnostics: list[dict[str, str]] = []
    covered_cutovers: set[str] = set()
    for edge in route["edges"]:
        edge_context = {"edge_id": edge["edge_id"], "route_id": route["route_id"]}
        for name in EDGE_ARTIFACT_NAMES:
            diagnostic = _asset_diagnostic(
                asset_root,
                edge["artifacts"][name],
                {**edge_context, "artifact": name},
            )
            if diagnostic is not None:
                diagnostics.append(diagnostic)
        validation_diagnostic = _asset_diagnostic(
            asset_root,
            edge["validation"]["report"],
            {**edge_context, "artifact": "validation-report"},
        )
        if validation_diagnostic is not None:
            diagnostics.append(validation_diagnostic)
        if edge["validation"]["state"] != "passed":
            diagnostics.append(
                {
                    **edge_context,
                    "code": "edge-validation-not-passed",
                    "state": edge["validation"]["state"],
                }
            )
        for cutover in edge["semantic_cutovers"]:
            if cutover["state"] == "passed":
                covered_cutovers.add(cutover["cutover_id"])
            else:
                diagnostics.append(
                    {
                        **edge_context,
                        "code": "cutover-validation-not-passed",
                        "cutover_id": cutover["cutover_id"],
                        "state": cutover["state"],
                    }
                )
    missing_cutovers = sorted(required_cutovers - covered_cutovers)
    if missing_cutovers:
        diagnostics.append(
            {
                "code": (
                    "direct-route-bypasses-required-cutover"
                    if len(route["edges"]) == 1
                    else "required-cutover-missing"
                ),
                "cutover_ids": ",".join(missing_cutovers),
                "route_id": route["route_id"],
            }
        )
    return diagnostics


def _sort_diagnostics(diagnostics: Sequence[Mapping[str, str]]) -> list[dict[str, str]]:
    return [
        dict(item)
        for item in sorted(
            diagnostics,
            key=lambda item: canonical_json(dict(item)),
        )
    ]


def _selected_route(route: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "edge_count": len(route["edges"]),
        "edges": [dict(edge) for edge in route["edges"]],
        "route_id": route["route_id"],
    }


def _result(
    *,
    route_kind: str,
    origin: str,
    target: str,
    matrix_id: str,
    matrix_bytes: bytes,
    matrix_reference: str,
    diagnostics: Sequence[Mapping[str, str]],
    selected_route: Mapping[str, Any] | None,
) -> dict[str, Any]:
    if route_kind not in ROUTE_KINDS:
        raise AssertionError(f"unsupported internal route kind: {route_kind}")
    return {
        "diagnostics": _sort_diagnostics(diagnostics),
        "matrix": {
            "byte_length": len(matrix_bytes),
            "matrix_id": matrix_id,
            "path": matrix_reference,
            "sha256": sha256_bytes(matrix_bytes),
        },
        "origin": origin,
        "read_only": True,
        "route_kind": route_kind,
        "selected_route": dict(selected_route) if selected_route is not None else None,
        "target": target,
    }


def resolve_upgrade_route(
    matrix: Mapping[str, Any],
    *,
    origin: str,
    target: str,
    matrix_bytes: bytes,
    asset_root: Path,
    matrix_reference: str,
) -> dict[str, Any]:
    """Resolve one explicit request from a validated matrix without side effects."""

    if not isinstance(matrix_bytes, bytes):
        raise MatrixValidationError("matrix_bytes must be raw bytes")
    origin = _version(origin, "origin")
    target = _version(target, "target")
    normalized = validate_matrix(matrix)
    _deprecation_evidence_errors(normalized, asset_root)

    common = {
        "origin": origin,
        "target": target,
        "matrix_id": normalized["matrix_id"],
        "matrix_bytes": matrix_bytes,
        "matrix_reference": matrix_reference,
    }
    if target != normalized["target"]["version"]:
        return _result(
            route_kind="unsupported",
            diagnostics=[{"code": "target-outside-matrix", "matrix_target": normalized["target"]["version"]}],
            selected_route=None,
            **common,
        )

    deprecations = {item["origin"]: item for item in normalized["deprecations"]}
    if origin in deprecations:
        deprecation = deprecations[origin]
        return _result(
            route_kind="unsupported",
            diagnostics=[
                {
                    "code": "fully-explicitly-deprecated",
                    "deprecation_id": deprecation["deprecation_id"],
                    "reason": deprecation["reason"],
                }
            ],
            selected_route=None,
            **common,
        )

    retained = {item["version"]: item for item in normalized["retained_origins"]}
    if origin not in retained:
        return _result(
            route_kind="unsupported",
            diagnostics=[{"code": "origin-outside-matrix"}],
            selected_route=None,
            **common,
        )

    target_diagnostic = _asset_diagnostic(
        asset_root,
        normalized["target"]["manifest"],
        {"artifact": "target-manifest"},
    )
    origin_diagnostic = _asset_diagnostic(
        asset_root,
        retained[origin]["manifest"],
        {"artifact": "origin-manifest", "origin_role": retained[origin]["role"]},
    )
    matching = [
        route
        for route in normalized["routes"]
        if route["origin"] == origin and route["target"] == target
    ]
    if not matching:
        diagnostics: list[dict[str, str]] = [{"code": "missing-route"}]
        if target_diagnostic is not None:
            diagnostics.append(target_diagnostic)
        if origin_diagnostic is not None:
            diagnostics.append(origin_diagnostic)
        return _result(
            route_kind="reconciliation-required",
            diagnostics=diagnostics,
            selected_route=None,
            **common,
        )

    required_cutovers = {
        cutover["cutover_id"] for cutover in normalized["semantic_cutovers"] if cutover["required"]
    }
    route_diagnostics: dict[str, list[dict[str, str]]] = {
        route["route_id"]: _route_diagnostics(route, required_cutovers, asset_root)
        for route in matching
    }
    if target_diagnostic is not None or origin_diagnostic is not None:
        for diagnostics in route_diagnostics.values():
            if target_diagnostic is not None:
                diagnostics.append(target_diagnostic)
            if origin_diagnostic is not None:
                diagnostics.append(origin_diagnostic)

    safe_direct = [
        route
        for route in matching
        if len(route["edges"]) == 1 and not route_diagnostics[route["route_id"]]
    ]
    if len(safe_direct) == 1:
        rejected = [
            diagnostic
            for route in matching
            if route is not safe_direct[0]
            for diagnostic in route_diagnostics[route["route_id"]]
        ]
        return _result(
            route_kind="direct",
            diagnostics=rejected,
            selected_route=_selected_route(safe_direct[0]),
            **common,
        )
    if len(safe_direct) > 1:
        return _result(
            route_kind="reconciliation-required",
            diagnostics=[
                {
                    "candidate_route_ids": ",".join(sorted(route["route_id"] for route in safe_direct)),
                    "code": "ambiguous-safe-chain",
                }
            ],
            selected_route=None,
            **common,
        )

    safe_multi_hop = [
        route
        for route in matching
        if len(route["edges"]) > 1 and not route_diagnostics[route["route_id"]]
    ]
    if len(safe_multi_hop) == 1:
        rejected = [
            diagnostic
            for route in matching
            if route is not safe_multi_hop[0]
            for diagnostic in route_diagnostics[route["route_id"]]
        ]
        return _result(
            route_kind="orchestrated-multi-hop",
            diagnostics=rejected,
            selected_route=_selected_route(safe_multi_hop[0]),
            **common,
        )
    if len(safe_multi_hop) > 1:
        return _result(
            route_kind="reconciliation-required",
            diagnostics=[
                {
                    "candidate_route_ids": ",".join(
                        sorted(route["route_id"] for route in safe_multi_hop)
                    ),
                    "code": "ambiguous-safe-chain",
                }
            ],
            selected_route=None,
            **common,
        )

    diagnostics = [
        diagnostic for route in matching for diagnostic in route_diagnostics[route["route_id"]]
    ]
    return _result(
        route_kind="reconciliation-required",
        diagnostics=diagnostics,
        selected_route=None,
        **common,
    )


def resolve_matrix_file(matrix_path: Path, *, origin: str, target: str) -> dict[str, Any]:
    """Load and resolve one explicit matrix file; no other route source is consulted."""

    matrix_path = Path(matrix_path)
    matrix, raw = load_route_matrix(matrix_path)
    return resolve_upgrade_route(
        matrix,
        origin=origin,
        target=target,
        matrix_bytes=raw,
        asset_root=matrix_path.parent,
        matrix_reference=matrix_path.as_posix(),
    )
