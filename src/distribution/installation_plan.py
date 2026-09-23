"""Read-only exact plans shared with the coordinated maintenance facade.

Preview checks do not acquire writer exclusion or establish caller quiescence.
"""
from __future__ import annotations

from hashlib import sha256
import os
from pathlib import Path
import stat

from .data import json_bytes
from . import installation_state as state
from .installation_io import Backend

__all__ = ["plan", "member_delta", "is_noop"]


def _descriptor(member: dict | None) -> dict | None:
    if member is None:
        return None
    return {key: member[key] for key in ("sha256", "size", "mode", "owner", "kind")}


def member_delta(old: state.InstalledLock | None, candidate: state.Candidate) -> list[dict]:
    """Pure descriptor delta over reader results, sorted by exact destination.

    This helper confers no filesystem, ownership, drift or mutation admission.
    It accepts reader-created values; public untrusted input enters plan().
    """
    before = old.members if old else {}
    rows = []
    for name in sorted(set(before) | set(candidate.members)):
        left, right = _descriptor(before.get(name)), _descriptor(candidate.members.get(name))
        if left is None:
            action = "add"
        elif right is None:
            action = "remove"
        elif left == right:
            action = "unchanged"
        elif all(left[key] == right[key] for key in ("sha256", "size", "owner", "kind")):
            action = "mode-only"
        else:
            action = "change"
        rows.append({"destination": name, "action": action, "before": left, "after": right})
    return rows


def is_noop(observation: state.Observation, candidate: state.Candidate, mode_policy: str) -> bool:
    """Pure no-op classification over a complete, fresh reader observation.

    Build time/run ID and the currently inspecting engine pin do not churn a
    matching installed lock. This helper never authorizes writer admission.
    """
    old = observation.lock
    return bool(old is not None and not observation.markers and not observation.drift
                and old.document["candidate_identity"] == candidate.identity
                and old.document["inventory"] == candidate.inventory
                and old.document["mode_policy"] == mode_policy)


def _protected_path(root: Path, name: str) -> Path | None:
    """Resolve one caller-selected path without enumerating any data directory."""
    current = root
    parts = name.split("/")
    for index, part in enumerate(parts):
        current = current / part
        try:
            info = current.lstat()
        except FileNotFoundError:
            return None
        state._plain(info, name)
        if index != len(parts) - 1:
            state._check(stat.S_ISDIR(info.st_mode), "parent-collision", "Protected path parent is occupied.", name, "conflict")
        # resolve reads the exact existing path, not sibling names. On Windows
        # the final path spelling also rejects alternate-case/short-name aliases.
        resolved = current.resolve(strict=True)
        state._check(resolved.is_relative_to(root)
                     and resolved.relative_to(root).parts == tuple(parts[:index + 1]),
                     "path-alias", "Protected path is not its exact canonical spelling.", name, "conflict")
    return current


def _protected(reader: state._Reader, root: Path, requested: list, managed: set[str]) -> list[dict]:
    rows = state._array(requested, state.LIMITS["protected_inputs"])
    for row in rows:
        state._shape(row, {"path", "sha256"})
        state._relative(row["path"])
        state._digest(row["sha256"], nullable=True)
    state._sorted(rows, lambda row: row["path"])
    # Also reject prefix/case collisions across protected and managed/control files.
    state._paths(sorted(managed | {state.LOCK_PATH, state.GUARD_PATH, *state.MARKERS}) + [row["path"] for row in rows])
    result = []
    for row in rows:
        target = _protected_path(root, row["path"])
        if row["sha256"] is None:
            state._check(target is None, "protected-input-conflict", "Protected input was expected absent.", row["path"], "conflict")
        else:
            state._check(target is not None, "protected-input-conflict", "Selected protected input is missing.", row["path"], "conflict")
            actual = sha256(reader.read(target, row["path"])).hexdigest()
            state._check(actual == row["sha256"], "protected-input-conflict", "Selected protected input raw bytes differ.", row["path"], "conflict")
        result.append(dict(row))
    return result


def _path_budget(roots: dict[str, Path], candidate: state.Candidate,
                 old: state.InstalledLock | None, delta: list[dict], protected: list[dict], engine: dict) -> dict:
    """Budget the selected writer layout without allocating IDs or directories.

    Fixed-width placeholders are length calculations only. Apply selects a real
    ID, checks exclusive absence and budgets every actual backend path.
    """
    operation = "i-" + "0" * 32
    paths: set[tuple[str, str]] = {(role, "") for role in roots}
    names = set(candidate.members) | (set(old.members) if old else set())
    controls = {state.LOCK_PATH, state.GUARD_PATH, *state.MARKERS}
    for name in names | controls | {row["path"] for row in protected}:
        paths.add(("project", name))
    for name in names | {state.LOCK_PATH, *state.MARKERS}:
        parent = name.rsplit("/", 1)[0]
        paths.add(("project", parent + "/.fi-" + "0" * 12))
    for row in candidate.members.values():
        paths.add(("candidate", row["path"]))
    paths.update(("candidate", name) for name in state.METADATA)
    paths.update(("engine", row["path"]) for row in engine["files"])
    for role in ("scratch", "staging", "recovery"):
        paths.add((role, operation))
    for name in (*state.METADATA, "plan.json", state.LOCK_PATH):
        paths.add(("scratch", operation + "/" + name))
    for row in delta:
        if row["action"] in {"add", "change"}:
            paths.add(("staging", operation + "/" + row["destination"]))
    paths.add(("staging", operation + "/" + state.LOCK_PATH))
    paths.add(("recovery", operation + "/operation.json"))
    paths.add(("recovery", operation + "/objects/" + "0" * 64))
    maximum, longest_segment = 0, 0
    for role, name in sorted(paths):
        target = roots[role].joinpath(*name.split("/")) if name else roots[role]
        full_length = len(str(target).encode("utf-16-le", errors="strict")) // 2
        segment_length = max(len(part.encode("utf-16-le", errors="strict")) // 2 for part in target.parts)
        maximum, longest_segment = max(maximum, full_length), max(longest_segment, segment_length)
        state._check(full_length <= state.LIMITS["path_utf16"] and segment_length <= state.LIMITS["segment_utf16"],
                     "path-budget", f"{role} path uses {full_length} full-path / {segment_length} segment UTF-16 units; limits are 240 / 255.", name or None, "unsupported")
    return {"policy": "conservative-windows-v1", "full_path_utf16_limit": state.LIMITS["path_utf16"],
            "segment_utf16_limit": state.LIMITS["segment_utf16"], "maximum_full_path_utf16": maximum,
            "maximum_segment_utf16": longest_segment, "checked_paths": len(paths),
            "backend_certification": "not-assessed"}


PLAN_FIELDS = {"candidate_root", "candidate_identity", "expected_lock_sha256", "mode_policy",
               "scratch_root", "staging_root", "recovery_root", "durability", "protected_inputs", "project_data_action"}


class PlanConflict(state.InstallationError):
    def __init__(self, drift: list[dict]):
        super().__init__("owned-drift", "Every old member must match before maintenance.", outcome="conflict")
        self.diagnostics = [{"code": "owned-drift", "path": row["path"], "reason": row["reason"],
                             "next_action": "Reconcile owned state without overwriting drift, then plan again."} for row in drift]


def _prerequisites(noop: bool, windows: bool, mode_only: bool) -> list[dict]:
    # Stable across acquisition/first-install guard creation. Runtime observations
    # are discharged privately by apply, never smuggled into a reusable plan hash.
    rows = [
        ("candidate-provenance", "satisfied", "caller", "Available bytes/bindings match; provenance approval and source authenticity remain with caller."),
        ("durability-declaration", "satisfied", "caller", "Native filesystem/domain combination is supported; recovery survival is a caller assertion, not measured durability."),
        ("exclusive-operation-allocation", "not-required" if noop else "pending", "maintenance-writer", "Preflight actual unique paths and exclusively allocate the selected operation before managed mutation."),
        ("fresh-input-observation", "pending", "maintenance-writer", "Recompute this exact plan under a held native writer lock."),
        ("lock-publication", "not-required" if noop else "satisfied", "maintenance-writer", "Next lock fits the closed reader and selected backend; publication remains a postcondition after full member read-back."),
        ("maintenance-quiescence", "pending", "caller", "Supply a fresh exact-scope declaration; the engine cannot attest stopped activity."),
        ("mode-materialization", "not-applicable" if windows else "satisfied", "maintenance-writer",
         "mode-not-materialized: Windows inventory-only; mode-only changes do not rewrite bytes." if windows and mode_only else
         "Windows inventory-only; no ACL/executable enforcement." if windows else "Native exact 0644/0755 support; mode-only changes avoid byte replacement."),
        ("native-writer-backend", "satisfied", "maintenance-writer", "Selected native primitives and filesystem/domain checks are available; this is not platform certification."),
        ("writer-engine-closure", "satisfied", "maintenance-writer", "Fixed bootstrap, executing origins, exact source closure and observed checkout HEAD match the caller pin."),
        ("writer-guard", "pending", "maintenance-writer", "Acquire the inert guard with a native OS lock; no-op cannot create a missing guard."),
    ]
    return [{"id": name, "status": status, "owner": owner, "next_action": action}
            for name, status, owner, action in sorted(rows)]


def _prepare(request: dict, reader: state._Reader, *, own_guard: bool = False) -> tuple:
    """Recompute from raw inputs. own_guard is internal held-handle provenance."""
    state._text(request["candidate_identity"])
    state._digest(request["expected_lock_sha256"], nullable=True)
    state._text(request["mode_policy"])
    state._check((os.name, request["mode_policy"]) in {("posix", "posix-permissions"), ("nt", "windows-inventory-only")},
                 "mode-platform", "Explicit mode policy is unsupported on this platform.", outcome="unsupported")
    state._check(request["project_data_action"] == "none", "project-data-action", "Only project_data_action=none is supported.", outcome="unsupported")
    durability = state._shape(request["durability"], {"declared_by", "declaration_reference", "failure_domain"})
    for value in durability.values():
        state._text(value)
    reader.listings.clear()
    roots = {role: state._root(request[role + "_root"]) for role in ("project", "engine", "candidate", "scratch", "staging", "recovery")}
    state._roots_disjoint(roots)
    state._engine(reader, roots["engine"], request["engine"])
    candidate = state.read_candidate(request["candidate_root"], _reader=reader)
    state._check(candidate.identity == request["candidate_identity"], "candidate-selection", "Candidate differs from caller-selected identity.", outcome="conflict")
    observation = state.observe_installation(request["project_root"], candidate, _reader=reader)
    state._check(not observation.markers, "maintenance-marker", "An incomplete/inaccessible maintenance marker blocks planning.", outcome="blocked")
    old = observation.lock
    state._check((old.sha256 if old else None) == request["expected_lock_sha256"],
                 "lock-conflict", "Observed raw lock identity differs from expected hash/absence.", state.LOCK_PATH, "conflict")
    if observation.drift:
        raise PlanConflict(observation.drift)
    if old:
        state._check(old.document["mode_policy"] == request["mode_policy"], "mode-policy-transition",
                     "Changing an installed mode policy needs a separately supported transition.", outcome="unsupported")
    names = set(candidate.members) | (set(old.members) if old else set())
    state._paths(sorted(names))
    delta = member_delta(old, candidate)
    for row in delta:
        if row["action"] == "add":
            target = reader.locate(roots["project"], row["destination"])
            state._check(target is None, "unowned-collision", "Destination exists without old inventory ownership, even if bytes match.", row["destination"], "conflict")
    # Reserved controls may have absent ancestors; locating checks aliases,
    # linked ancestors and parent occupation without creating anything.
    guard = reader.locate(roots["project"], state.GUARD_PATH)
    if guard is not None:
        info = guard.lstat()
        state._check(stat.S_ISREG(info.st_mode) and info.st_nlink == 1 and info.st_size == 0,
                     "guard-conflict", "Reserved coordination path is not a direct regular file.", state.GUARD_PATH, "conflict")
        state._check(old is not None or own_guard, "unowned-control", "Clean install cannot adopt a preexisting coordination file.", state.GUARD_PATH, "conflict")
    protected = _protected(reader, roots["project"], request["protected_inputs"], names)
    # Exact fixed-width lock shape budget, without publishing a lock or ID.
    prospective_lock = {"lock_version": 1, "installation_id": old.document["installation_id"] if old else "0" * 32,
                        "engine": request["engine"], "mode_policy": request["mode_policy"],
                        "candidate_identity": candidate.identity, "selection": candidate.selection,
                        "inventory": candidate.inventory}
    state._check(len(json_bytes(prospective_lock)) <= state.LIMITS["document_bytes"],
                 "lock-limit", "Resulting lock would exceed its reader byte limit.")
    backend = Backend(roots, durability)
    budget = _path_budget(roots, candidate, old, delta, protected, request["engine"])
    noop = is_noop(observation, candidate, request["mode_policy"])
    capabilities = {item["id"] for item in candidate.selection["components"]}
    if old:
        capabilities.update(item["id"] for item in old.document["selection"]["components"])
    document = {"api_version": 1, "operation": "plan", "project_root": str(roots["project"]),
                "candidate_identity": candidate.identity, "engine": request["engine"],
                "expected_lock_sha256": request["expected_lock_sha256"], "mode_policy": request["mode_policy"],
                "roots": {role: str(roots[role]) for role in ("engine", "candidate", "scratch", "staging", "recovery")},
                "durability": durability, "project_data_action": "none", "protected_inputs": protected,
                "maintenance_scope": sorted(capabilities), "delta": delta,
                "preserved_unknown": observation.unknown, "path_budget": budget,
                "prerequisites": _prerequisites(noop, os.name == "nt", any(row["action"] == "mode-only" for row in delta))}
    # Snapshot caller-owned containers; later caller mutations cannot silently
    # change the returned plan without changing its advertised hash.
    raw = json_bytes(document)
    state._check(len(raw) <= state.LIMITS["document_bytes"], "plan-limit", "Plan exceeds serialization byte limit.")
    document = state._document(raw, "plan.json")
    result = {"api_version": 1, "operation": "plan", "outcome": "planned", "plan": document,
              "plan_sha256": sha256(raw).hexdigest()}
    return result, candidate, observation, roots, backend


def plan(request: dict | bytes) -> dict:
    """Closed API 1 preview with no allocation, lock acquisition or writes."""
    try:
        request = state._request(request, "plan", PLAN_FIELDS)
        return _prepare(request, state._Reader())[0]
    except (state.InstallationError, OSError, UnicodeError, ValueError, TypeError, RecursionError, OverflowError) as exc:
        result = state._failure("plan", exc)
        if isinstance(exc, PlanConflict):
            result["diagnostics"] = exc.diagnostics
        return result
