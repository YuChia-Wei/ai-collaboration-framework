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


def is_noop(observation: state.Observation, candidate: state.Candidate, mode_policy: str, project_inputs=None, project_edits=()) -> bool:
    """Pure no-op classification over a complete, fresh reader observation.

    Build time/run ID and the currently inspecting engine pin do not churn a
    matching installed lock. This helper never authorizes writer admission.
    """
    old = observation.lock
    return bool(old is not None and not observation.markers and not observation.drift
                and old.document["candidate_identity"] == candidate.identity
                and old.document["inventory"] == candidate.inventory
                and old.document["mode_policy"] == mode_policy
                and old.document.get("project_inputs", []) == (project_inputs or []) and not project_edits)


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
        try:
            resolved = current.resolve(strict=True)
        except OSError as exc:
            if os.name != "nt" or getattr(exc, "winerror", None) != 1:
                raise
            # ERROR_INVALID_FUNCTION is the only fallback. Keep the selected
            # node and every ancestor direct and stable around the long-name
            # query; no sibling listing or recursive data scan is needed.
            ancestry = [(current, info), *((parent, parent.lstat()) for parent in current.parents)]
            for ancestor, before in ancestry:
                state._plain(before, name)
                state._check(ancestor == current or stat.S_ISDIR(before.st_mode),
                             "parent-collision", "Protected path parent is occupied.", name, "conflict")
                state._check(bool(before.st_dev and before.st_ino), "path-identity",
                             "Canonical fallback requires usable filesystem identities.", name)
            resolved = state._windows_long_path(current)
            for ancestor, before in ancestry:
                after = ancestor.lstat()
                state._plain(after, name)
                state._check((before.st_dev, before.st_ino, before.st_mode)
                             == (after.st_dev, after.st_ino, after.st_mode),
                             "input-drift", "Protected path ancestry changed during admission.", name)
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
        parent = name.rpartition("/")[0]
        paths.add(("project", (parent + "/" if parent else "") + ".fi-" + "0" * 12))
    for row in candidate.members.values():
        paths.add(("candidate", row["path"]))
    paths.update(("candidate", name) for name in candidate.metadata_bytes)
    paths.update(("engine", row["path"]) for row in engine["files"])
    for role in ("scratch", "staging", "recovery"):
        paths.add((role, operation))
    for name in (*candidate.metadata_bytes, "plan.json", state.LOCK_PATH):
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
               "scratch_root", "staging_root", "recovery_root", "durability", "protected_inputs", "project_data_action", "project_edits"}


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
    state._check(candidate.selection["schema_version"] == 3, "unsupported-write",
                 "Engine 2 writes only explicit catalog subsets; inspect legacy artifacts with their original semantics.", outcome="unsupported")
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
    withdrawn = {row["destination"].rpartition("/")[0] for row in delta if row["action"] == "remove"
                 and row["destination"].startswith(".agents/skills/framework-")}
    for name in observation.unknown or []:
        state._check(not any(name.startswith(prefix + "/") and (name.endswith("/") or name.endswith("/SKILL.md")) for prefix in withdrawn),
                     "legacy-discovery-collision", "Unknown old runtime discovery subtree blocks withdrawal.", name, "conflict")
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
    edits, edit_objects = project_edits(reader, roots, request["project_edits"], names,
                                        [row["path"] for row in protected])
    project_inputs = project_bindings(reader, roots["project"], candidate, protected, edits, edit_objects)
    edited_names = {r["intent"]["path"] for r in edits}
    protected_map = {r["path"]:r for r in protected}
    for row in project_inputs:
        if row["path"] not in edited_names:
            protected_map[row["path"]] = row
    protected = _protected(reader, roots["project"], [protected_map[n] for n in sorted(protected_map)], names | edited_names)
    from .catalog import lock_document
    prospective_lock = lock_document(candidate, request["engine"], old.document["installation_id"] if old else "0" * 32,
                                     request["mode_policy"], project_inputs)
    state._check(len(json_bytes(prospective_lock)) <= state.LIMITS["document_bytes"],
                 "lock-limit", "Resulting lock would exceed its reader byte limit.")
    state._lock_bytes(json_bytes(prospective_lock))
    backend = Backend(roots, durability)
    budget = _path_budget(roots, candidate, old, delta, protected + [{"path":r["intent"]["path"]} for r in edits], request["engine"])
    from .installation_io import budget as actual_budget, sibling
    edit_paths = []
    for row in edits:
        name = row["intent"]["path"]
        edit_paths.extend(("project", roots["project"], n) for n in (name, sibling("0"*32, name)))
        if row["intent"]["after_content_ref"] is not None:
            edit_paths.append(("staging", roots["staging"], row["intent"]["after_content_ref"]))
    actual_budget(edit_paths)
    noop = is_noop(observation, candidate, request["mode_policy"], project_inputs, edits)
    capabilities = {item["id"] for item in candidate.selection["components"]}
    if old:
        capabilities.update(item["id"] for item in old.document["selection"]["components"])
    document = {"api_version": 2, "operation": "plan", "project_root": str(roots["project"]),
                "candidate_identity": candidate.identity, "engine": request["engine"],
                "expected_lock_sha256": request["expected_lock_sha256"], "mode_policy": request["mode_policy"],
                "roots": {role: str(roots[role]) for role in ("engine", "candidate", "scratch", "staging", "recovery")},
                "durability": durability, "project_data_action": "none", "protected_inputs": protected,
                "project_edits": edits, "project_inputs": project_inputs, "noop": noop,
                "maintenance_scope": sorted(capabilities), "delta": delta,
                "preserved_unknown": observation.unknown, "path_budget": budget,
                "prerequisites": _prerequisites(noop, os.name == "nt", any(row["action"] == "mode-only" for row in delta))}
    # Snapshot caller-owned containers; later caller mutations cannot silently
    # change the returned plan without changing its advertised hash.
    raw = json_bytes(document)
    state._check(len(raw) <= state.LIMITS["document_bytes"], "plan-limit", "Plan exceeds serialization byte limit.")
    document = state._document(raw, "plan.json")
    result = {"api_version": 2, "operation": "plan", "outcome": "planned", "plan": document,
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


def project_edits(reader, roots, intents, managed, protected):
    """Resolve closed explicit intents; immutable staging objects are read only."""
    rows = state._array(intents, state.LIMITS["protected_inputs"])
    names = []
    for intent in rows:
        state._shape(intent, {"path", "before_sha256", "after_sha256", "after_content_ref"})
        name = state._relative(intent["path"])
        state._check(not name.startswith((".ai/core/", ".ai/local/", ".git/")) and name not in {".ai/core", ".ai/local", ".git"},
                     "project-edit-boundary", "Project intents cannot own managed, coordination or Git storage.", name)
        names.append(name)
        for key in ("before_sha256", "after_sha256"): state._digest(intent[key], nullable=True)
        state._check(intent["after_content_ref"] == ("objects/" + intent["after_sha256"] if intent["after_sha256"] else None),
                     "project-edit-object", "After content must address its exact staging transaction object.", name)
    state._sorted(rows, lambda r:r["path"])
    state._paths(sorted(managed | {state.LOCK_PATH, state.GUARD_PATH, *state.MARKERS}) + names + protected)
    result = []; objects = {}
    for intent in rows:
        name = intent["path"]; target = reader.locate(roots["project"], name)
        before = reader.read(target, name) if target is not None else None
        state._check((sha256(before).hexdigest() if before is not None else None) == intent["before_sha256"],
                     "project-edit-drift", "Project preimage differs from explicit expected bytes/absence.", name, "conflict")
        mode = "100644"
        if before is not None and os.name == "posix":
            bits = stat.S_IMODE(target.lstat().st_mode)
            state._check(bits in {0o644, 0o755}, "project-edit-mode", "Project edit requires an exactly supported mode.", name, "unsupported")
            mode = "100755" if bits == 0o755 else "100644"
        before_row = None if before is None else {"sha256":sha256(before).hexdigest(), "size":len(before), "mode":mode}
        if before is not None: objects[before_row["sha256"]] = before
        after_row = None
        if intent["after_sha256"] is not None:
            obj = reader.locate(roots["staging"], intent["after_content_ref"])
            state._check(obj is not None, "project-edit-object", "Selected staging object is missing.", name)
            after = reader.read(obj, intent["after_content_ref"])
            state._check(sha256(after).hexdigest() == intent["after_sha256"], "project-edit-object", "Staging object does not match its content address.", name)
            after_row = {"sha256":intent["after_sha256"], "size":len(after), "mode":mode}
            objects[after_row["sha256"]] = after
        result.append({"intent":dict(intent), "before":before_row, "after":after_row})
    return result, objects


def project_bindings(reader, project, candidate, protected, edits, objects):
    """Pin raw after-state inputs; authority meaning stays with the target owner."""
    from .catalog import digest
    desired = candidate.selection["desired"]
    after = {r["intent"]["path"]:r["after"] for r in edits}
    before = {r["path"]:r["sha256"] for r in protected}
    bound = {name:value for name,value in before.items() if value is not None}
    for name,row in after.items():
        if row is not None: bound[name] = row["sha256"]
    for binding in desired["bindings"]:
        for authority in binding["authorities"]:
            name = authority["path"]; state._relative(name)
            if name in after:
                actual = after[name]["sha256"] if after[name] is not None else None
            else:
                target = _protected_path(project, name)
                actual = digest(reader.read(target, name)) if target is not None else None
            state._check(actual == authority["sha256"], "binding-unresolved", "Target authority bytes/after-intent differ from desired binding.", name)
            state._check(name not in bound or bound[name] == actual, "binding-unresolved", "One authority path has conflicting hashes.", name)
            bound[name] = actual
    config = ".ai/custom/framework.json"
    target = _protected_path(project, config)
    if target is not None and config not in after:
        state._check(config in before, "project-input-required", "Explicitly pin the existing framework configuration in protected_inputs.", config)
    selection_path = ".ai/custom/installation.json"
    if selection_path in after and after[selection_path] is not None:
        raw = objects[after[selection_path]["sha256"]]
        saved = state._document(raw, selection_path, canonical=False)
        state._check(saved == desired, "saved-selection-binding", "Explicit saved installation must equal this desired selection.", selection_path)
    elif selection_path in before and before[selection_path] is not None:
        saved = state._document(reader.read(_protected_path(project, selection_path), selection_path), selection_path, canonical=False)
        state._check(saved == desired, "saved-selection-binding", "Selected saved installation differs from desired selection.", selection_path)
    state._check(len(bound) <= state.LIMITS["protected_inputs"], "project-input-limit", "Too many project input bindings.")
    return [{"path":name,"sha256":bound[name]} for name in sorted(bound)]
