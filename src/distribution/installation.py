"""Closed development maintenance API 1; project readiness is never inferred.

The source entry establishes the fixed engine bootstrap. Apply and recover hold
native participating-writer exclusion and demand a fresh caller declaration.
No fetch, dependency installation, migration, activation or cleanup service.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import os
from pathlib import Path
import re
import secrets
import stat

from .data import json_bytes
from . import installation_state as state
from . import installation_plan as planning
from .installation_io import Backend, Changes, IO, budget, sibling
from .maintenance_coordination import WriterLock, declaration

__all__ = ["inspect", "plan", "apply", "recover", "execute"]
inspect = state.inspect
plan = planning.plan
ERRORS = (state.InstallationError, OSError, UnicodeError, ValueError, TypeError, RecursionError, OverflowError)


@dataclass(frozen=True)
class Operation:
    document: dict
    raw: bytes
    before: state.InstalledLock | None
    after: state.InstalledLock
    objects: dict[str, bytes]

    @property
    def names(self) -> set[str]:
        return set(self.after.members) | (set(self.before.members) if self.before else set()) | {r["intent"]["path"] for r in self.document["project_edits"]}

    def descriptors(self, target):
        rows = dict(target.members) if target else {}
        side = "after" if target is not None and target.sha256 == self.after.sha256 else "before"
        for edit in self.document["project_edits"]:
            if edit[side] is not None:
                name = edit["intent"]["path"]
                rows[name] = {**edit[side], "owner":"project/"+name, "kind":"project"}
        return rows

    @property
    def scope(self) -> list[str]:
        names = {row["id"] for row in self.after.document["selection"]["components"]}
        if self.before:
            names.update(row["id"] for row in self.before.document["selection"]["components"])
        return sorted(names)


def _hash(raw: bytes | None) -> str | None:
    return None if raw is None else sha256(raw).hexdigest()


def _details(changes: Changes, managed: str) -> dict:
    return {"managed_state": managed, "project_readiness": "not-assessed", "lock_sha256": changes.lock_sha256,
            "operation_root": changes.operation_root, "counts": dict(changes.counts), "protected_input_state": changes.protected}


def _result(operation: str, outcome: str, changes: Changes, managed: str, diagnostics: list | None = None) -> dict:
    return {"api_version": 2, "operation": operation, "outcome": outcome, "changed": changes.changed,
            "details": _details(changes, managed), "diagnostics": diagnostics or []}


def _failed(operation: str, exc: Exception, changes: Changes) -> dict:
    failure = state._failure(operation, exc)
    if changes.protected == "matches":
        changes.protected = "unresolved"
    diagnostics = getattr(exc, "diagnostics", failure["diagnostics"])
    if changes.changed:
        changes.lock_sha256 = None  # An earlier hash is not current read-back.
        diagnostics = list(diagnostics) + [{"code": "partial-maintenance", "path": None,
            "reason": "Preparation or managed writes occurred; counts describe completed member syscalls only. Durable/run directories and empty parents are retained.",
            "next_action": "Keep capabilities inactive; use the exact complete operation for recovery, or reconcile pre-marker residue under its owner."}]
        diagnostics.extend({"code": "retained-preparation-path", "path": row["path"],
                            "reason": "A write occurred at this relative " + row["role"] + " path; presence after failure is not assumed.",
                            "next_action": "Preserve and inspect this bounded residue; no recursive cleanup is authorized."} for row in changes.residues)
    outcome = "recovery-needed" if changes.marker_admitted else failure["outcome"]
    managed = "recovery-needed" if changes.marker_admitted else outcome
    if any(row["code"] == "maintenance-marker" for row in diagnostics):
        managed = "recovery-needed"
    if managed == "conflict":
        managed = "drift"
    return _result(operation, outcome, changes, managed, diagnostics)


def _mode_note(rows: list[dict]) -> list[dict]:
    if os.name == "nt" and any(row["action"] == "mode-only" for row in rows):
        return [{"code": "mode-not-materialized", "path": None,
                 "reason": "Windows mode-only members changed declared inventory only; their bytes and executable permissions were not rewritten.",
                 "next_action": "Project owns any separate ACL or executable policy."}]
    return []


def _bundle(request: dict, prepared: tuple, operation_id: str, reader: state._Reader) -> Operation:
    result, candidate, observation, roots, _ = prepared
    before = observation.lock
    installation_id = before.document["installation_id"] if before else operation_id
    from .catalog import lock_document
    after_raw = json_bytes(lock_document(candidate, request["engine"], installation_id,
                                        request["mode_policy"], result["plan"]["project_inputs"]))
    after = state._lock_bytes(after_raw)
    objects = {}

    def retain(raw: bytes) -> None:
        digest = sha256(raw).hexdigest()
        state._check(digest not in objects or objects[digest] == raw, "object-collision", "Different bytes share an object identity.")
        objects[digest] = raw

    retain(after.raw)
    if before:
        retain(before.raw)
        for name, row in sorted(before.members.items()):
            retain(reader.member(roots["project"], {**row, "path": name}, request["mode_policy"]))
    for raw in (*candidate.contents.values(), *candidate.metadata_bytes.values()):
        retain(raw)
    edits, edit_objects = planning.project_edits(reader, roots, request["project_edits"],
                                                set(candidate.members) | (set(before.members) if before else set()),
                                                [r["path"] for r in result["plan"]["protected_inputs"]])
    state._check(edits == result["plan"]["project_edits"], "project-edit-drift", "Project intent preimages changed since planning.")
    for raw in edit_objects.values(): retain(raw)
    retain(json_bytes(result["plan"]))
    for row in request["engine"]["files"]:
        raw = reader.read(reader.locate(roots["engine"], row["path"]), row["path"])
        state._check(_hash(raw) == row["sha256"], "engine-drift", "Engine changed during recovery capture.", row["path"])
        retain(raw)
    document = {"operation_version": 2, "journal_version": 2, "project_edits": edits,
                "engine_objects": request["engine"]["files"], "operation_id": operation_id, "engine": request["engine"],
                "installation_id": installation_id, "project_root": str(roots["project"]),
                "operation_root": str(roots["recovery"] / ("i-" + operation_id)), "durability": request["durability"],
                "maintenance": request["maintenance"], "plan_sha256": result["plan_sha256"],
                "before_lock_sha256": before.sha256 if before else None, "after_lock_sha256": after.sha256,
                "candidate_metadata": {name: sha256(raw).hexdigest() for name, raw in candidate.metadata_bytes.items()},
                "protected_inputs": result["plan"]["protected_inputs"], "project_data_action": "none"}
    raw = json_bytes(document)
    state._document(raw, "operation.json")
    return Operation(document, raw, before, after, objects)


def _object(reader: state._Reader, root: Path, digest: str, objects: dict) -> bytes:
    if digest not in objects:
        name = "objects/" + state._digest(digest)
        target = reader.locate(root, name)
        state._check(target is not None, "missing-object", "Durable recovery object is missing.", name)
        raw = reader.read(target, name)
        state._check(_hash(raw) == digest, "object-drift", "Durable object bytes do not match their name.", name)
        objects[digest] = raw
    return objects[digest]


def _read_operation(reader: state._Reader, root: Path, expected_hash: str, engine: dict, project: Path) -> Operation:
    reader.listings.clear()
    target = reader.locate(root, "operation.json")
    state._check(target is not None, "incomplete-operation", "Complete immutable operation is required.", "operation.json")
    raw = reader.read(target, "operation.json", state.LIMITS["document_bytes"])
    state._check(_hash(raw) == expected_hash, "operation-binding", "Operation differs from the explicit raw hash.", "operation.json", "conflict")
    doc = state._document(raw, "operation.json")
    state._shape(doc, {"operation_version", "operation_id", "engine", "installation_id", "project_root", "operation_root",
                       "durability", "maintenance", "plan_sha256", "before_lock_sha256", "after_lock_sha256",
                       "candidate_metadata", "protected_inputs", "project_data_action", "journal_version", "project_edits", "engine_objects"})
    state._check(type(doc["operation_version"]) is int and doc["operation_version"] == 2
                 and type(doc["journal_version"]) is int and doc["journal_version"] == 2,
                 "unsupported-version", "Recover operation/journal 1 with its original pinned engine.", outcome="unsupported")
    for key in ("operation_id", "installation_id"):
        state._check(type(doc[key]) is str and re.fullmatch(r"[0-9a-f]{32}", doc[key]) is not None,
                     "operation-identity", "Operation/installation identity must be 32 lowercase hex characters.")
    state._check(root.name == "i-" + doc["operation_id"] and str(root) == doc["operation_root"]
                 and str(project) == doc["project_root"], "operation-root-binding", "Recovery requires the original exact project and operation roots.", outcome="conflict")
    state._engine_shape(doc["engine"])
    state._check(doc["engine"] == engine, "recovery-engine", "Recovery requires the complete original engine pin.", outcome="unsupported")
    state._digest(doc["plan_sha256"])
    state._digest(doc["before_lock_sha256"], nullable=True)
    state._digest(doc["after_lock_sha256"])
    state._shape(doc["durability"], {"declared_by", "declaration_reference", "failure_domain"})
    for value in doc["durability"].values():
        state._text(value)
    state._check(doc["project_data_action"] == "none", "project-data-action", "Operation must preserve project data.", outcome="unsupported")
    objects = {}
    after = state._lock_bytes(_object(reader, root, doc["after_lock_sha256"], objects))
    before = state._lock_bytes(_object(reader, root, doc["before_lock_sha256"], objects)) if doc["before_lock_sha256"] else None
    state._check(after.document["installation_id"] == doc["installation_id"] and after.document["engine"] == engine
                 and (before is None or (before.document["installation_id"] == doc["installation_id"]
                                         and before.document["mode_policy"] == after.document["mode_policy"])),
                 "operation-lock-binding", "Durable locks differ from operation identity, engine or mode policy.")
    state._check((os.name, after.document["mode_policy"]) in {("nt", "windows-inventory-only"), ("posix", "posix-permissions")},
                 "recovery-mode-platform", "Original mode policy is unsupported on this platform.", outcome="unsupported")
    from .catalog import SUBSET_METADATA
    metadata = state._shape(doc["candidate_metadata"], set(SUBSET_METADATA))
    raw_metadata = {name: _object(reader, root, state._digest(metadata[name]), objects) for name in SUBSET_METADATA}
    selection, inventory, _, _, identity = state._candidate_documents(raw_metadata)
    state._check(selection == after.document["selection"] and inventory == after.document["inventory"]
                 and identity == after.document["candidate_identity"], "operation-candidate-binding", "Captured candidate metadata differs from the after lock.")
    for lock in (before, after):
        if lock:
            contents = {}
            for name, row in lock.members.items():
                content = _object(reader, root, row["sha256"], objects)
                state._check(len(content) == row["size"], "object-size", "Object size differs from managed inventory.", name)
                contents[name] = content
            state.verify_lock_contents(lock, contents)
    state._check(doc["engine_objects"] == engine["files"], "recovery-engine", "Retained engine closure differs.")
    for row in doc["engine_objects"]:
        _object(reader, root, row["sha256"], objects)
    plan_raw = _object(reader, root, doc["plan_sha256"], objects)
    retained_plan = state._document(plan_raw, "plan.json")
    state._shape(retained_plan, {"api_version", "operation", "project_root", "candidate_identity", "engine", "expected_lock_sha256", "mode_policy",
                                 "roots", "durability", "project_data_action", "protected_inputs", "project_edits", "project_inputs", "noop",
                                 "maintenance_scope", "delta", "preserved_unknown", "path_budget", "prerequisites"})
    state._check(type(retained_plan["api_version"]) is int and retained_plan["api_version"] == 2
                 and retained_plan["operation"] == "plan" and retained_plan["engine"] == engine
                 and retained_plan["project_root"] == doc["project_root"]
                 and retained_plan["candidate_identity"] == after.document["candidate_identity"]
                 and retained_plan["expected_lock_sha256"] == doc["before_lock_sha256"]
                 and retained_plan["project_edits"] == doc["project_edits"]
                 and retained_plan["project_inputs"] == after.document["project_inputs"]
                 and retained_plan["protected_inputs"] == doc["protected_inputs"]
                 and retained_plan["durability"] == doc["durability"] and retained_plan["project_data_action"] == "none",
                 "operation-plan-binding", "Retained plan and operation disagree.")
    _edit_record(doc["project_edits"], reader, root, objects,
                 set(after.members) | (set(before.members) if before else set()), doc["protected_inputs"])
    operation = Operation(doc, raw, before, after, objects)
    state._check(retained_plan["maintenance_scope"] == operation.scope, "operation-plan-binding", "Retained maintenance scope differs.")
    declaration(doc["maintenance"], operation.scope)
    _protected_shape(doc["protected_inputs"], operation.names)
    return operation


def _protected_shape(rows: list, managed: set[str]) -> None:
    state._array(rows, state.LIMITS["protected_inputs"])
    for row in rows:
        state._shape(row, {"path", "sha256"})
        state._relative(row["path"])
        state._digest(row["sha256"], nullable=True)
    state._sorted(rows, lambda row: row["path"])
    state._paths(sorted(managed | {state.LOCK_PATH, state.GUARD_PATH, *state.MARKERS}) + [row["path"] for row in rows])


def _protected(io: IO, project: Path, rows: list, managed: set[str], *, reconstruct: bool = False) -> str:
    io.changes.protected = "unresolved"
    _protected_shape(rows, managed)
    unresolved = False
    for row in rows:
        # Exact ancestor stat only; never list a protected data directory.
        target = planning._protected_path(project, row["path"])
        raw = io.reader.read(target, row["path"]) if target is not None else None
        if _hash(raw) != row["sha256"]:
            if reconstruct and raw is None and row["sha256"] is not None:
                unresolved = True
            else:
                io.changes.protected = "conflict"
                raise state.InstallationError("protected-input-conflict", "Selected protected input differs from its byte/absence binding.", row["path"], "conflict")
    return "unresolved" if unresolved else "matches" if rows else "not-selected"


def _siblings(operation: Operation) -> dict[str, str]:
    names = operation.names | {state.LOCK_PATH, *state.MARKERS}
    siblings = {name: sibling(operation.document["operation_id"], name) for name in sorted(names)}
    state._check(len(set(siblings.values())) == len(siblings), "sibling-name-collision", "Deterministic sibling names collide.")
    state._paths(sorted(operation.names | {state.LOCK_PATH, state.GUARD_PATH, *state.MARKERS})
                 + list(siblings.values()) + [row["path"] for row in operation.document["protected_inputs"]])
    return siblings


def _layout(io: IO, roots: dict[str, Path], operation: Operation, rows: list[dict] | None = None) -> dict[str, str]:
    siblings = _siblings(operation)
    paths = [("project", roots["project"], name) for name in operation.names | {state.LOCK_PATH, state.GUARD_PATH, *state.MARKERS}
             | set(siblings.values()) | {row["path"] for row in operation.document["protected_inputs"]}]
    run = "i-" + operation.document["operation_id"]
    for digest in operation.objects:
        paths.append(("recovery", roots["recovery"], run + "/objects/" + digest))
    paths.append(("recovery", roots["recovery"], run + "/operation.json"))
    if rows is not None:
        for role in ("scratch", "staging", "recovery"):
            paths.append((role, roots[role], run))
            state._check(io.locate(roots[role], run) is None, "operation-collision", "Selected real operation path must be exclusively absent.", run, "conflict")
        paths.extend(("scratch", roots["scratch"], run + "/" + name) for name in (*operation.document["candidate_metadata"], "plan.json", state.LOCK_PATH))
        paths.extend(("staging", roots["staging"], run + "/" + row["destination"]) for row in rows if row["action"] in {"add", "change"})
        paths.append(("staging", roots["staging"], run + "/" + state.LOCK_PATH))
        for name in siblings.values():
            state._check(io.locate(roots["project"], name) is None, "sibling-collision", "Derived sibling path already exists.", name, "conflict")
    paths.extend(("engine", roots["engine"], row["path"]) for row in operation.document["engine"]["files"])
    budget(paths)
    for _, root, name in paths:
        io.contained_volume(root, name)
    return siblings


def _admit(document: dict, discharged: set[str]) -> None:
    unresolved = [row["id"] for row in document["prerequisites"] if row["status"] == "pending" and row["id"] not in discharged]
    state._check(not unresolved, "pending-prerequisite", "Mechanical prerequisites remain unresolved: " + ", ".join(unresolved))


def _capture(io: IO, roots: dict, prepared: tuple, operation: Operation) -> None:
    run = "i-" + operation.document["operation_id"]
    io.changes.operation_root = str(roots["recovery"] / run)
    allocated = {}
    for role in ("recovery", "scratch", "staging"):
        parent = roots[role]
        if parent not in allocated:
            allocated[parent] = io.directory(parent, run, role)
    recovery = allocated[roots["recovery"]]
    for digest, raw in sorted(operation.objects.items()):
        io.create(recovery, "objects/" + digest, raw, "recovery")
    result, candidate, _, _, _ = prepared
    scratch, staging = allocated[roots["scratch"]], allocated[roots["staging"]]
    for name, raw in candidate.metadata_bytes.items():
        io.create(scratch, name, raw, "scratch")
    io.create(scratch, "plan.json", json_bytes(result["plan"]), "scratch")
    # Scratch/staging may coincide; do not create the same control twice.
    io.create(staging, state.LOCK_PATH, operation.after.raw, "staging")
    if scratch != staging:
        io.create(scratch, state.LOCK_PATH, operation.after.raw, "scratch")
    for row in result["plan"]["delta"]:
        if row["action"] in {"add", "change"} and (row["before"] is None or row["before"]["sha256"] != row["after"]["sha256"]):
            io.create(staging, row["destination"], candidate.contents[row["destination"]], "staging", row["after"]["mode"])
    # A partial capture has no marker and cannot authorize managed mutation.
    io.create(recovery, "operation.json", operation.raw, "recovery")
    verified = _read_operation(io.reader, recovery, sha256(operation.raw).hexdigest(), operation.document["engine"], roots["project"])
    state._check(verified.raw == operation.raw and verified.objects == operation.objects,
                 "capture-closure", "Complete durable before/after closure did not read back exactly.")


def _current(io: IO, project: Path, operation: Operation, *, reconstruct: bool = False) -> dict:
    current = {}
    before_members = operation.descriptors(operation.before)
    for name in sorted(operation.names):
        raw = io.raw(project, name)
        mode = None if raw is None or io.backend.windows else ("100755" if stat.S_IMODE((project / name).lstat().st_mode) == 0o755 else
                                                               "100644" if stat.S_IMODE((project / name).lstat().st_mode) == 0o644 else "unsupported")
        options = (before_members.get(name), operation.descriptors(operation.after).get(name))
        matched = any((row is None and raw is None) or
                      (row is not None and raw is not None and len(raw) == row["size"] and _hash(raw) == row["sha256"]
                       and (io.backend.windows or mode == row["mode"])) for row in options)
        state._check(matched or (reconstruct and raw is None), "recovery-member-conflict",
                     "Member matches neither before nor after; unknown edits and partial unexpected loss cannot be overwritten.", name, "conflict")
        current[name] = (raw, mode)
    if reconstruct:
        state._check(all(raw is None for raw, _ in current.values()), "partial-loss", "Whole-loss reconstruction requires the entire managed union to be absent.", outcome="conflict")
    return current


def _verify_target(io: IO, project: Path, operation: Operation, target: state.InstalledLock | None) -> None:
    members = operation.descriptors(target)
    for name in sorted(operation.names):
        row = members.get(name)
        io.expect(project, name, operation.objects[row["sha256"]] if row else None, row["mode"] if row else None)


def _matches(operation: Operation, current: dict, target: state.InstalledLock | None, lock_raw: bytes | None, windows: bool) -> bool:
    if lock_raw != (target.raw if target else None):
        return False
    members = operation.descriptors(target)
    for name, (raw, mode) in current.items():
        row = members.get(name)
        if raw != (operation.objects[row["sha256"]] if row else None) or (row and not windows and mode != row["mode"]):
            return False
    return True


def _transition(io: IO, guard: WriterLock, project: Path, operation: Operation, current: dict,
                target: state.InstalledLock | None) -> None:
    members = operation.descriptors(target)
    for name in sorted(operation.names):
        guard.verify()
        before, before_mode = current[name]
        row = members.get(name)
        after = operation.objects[row["sha256"]] if row else None
        if before == after:
            if row and not io.backend.windows and before_mode != row["mode"]:
                io.mode(project, name, after, before_mode, row["mode"])
            else:
                io.expect(project, name, before, before_mode)
                io.changes.counts["unchanged"] += 1
        elif after is None:
            io.remove(project, name, before, before_mode, "removed")
        else:
            io.publish(project, name, after, before, operation.document["operation_id"], row["mode"], before_mode,
                       "added" if before is None else "changed")


def _finish(io: IO, guard: WriterLock, project: Path, operation: Operation, target: state.InstalledLock | None,
            current_lock: bytes | None, *, reconstruct: bool = False) -> None:
    _verify_target(io, project, operation, target)
    io.changes.protected = _protected(io, project, operation.document["protected_inputs"], operation.names, reconstruct=reconstruct)
    guard.verify()
    io.expect(project, state.MARKERS[0], operation.raw)
    io.expect(project, state.MARKERS[1], operation.raw)
    desired_lock = target.raw if target else None
    if desired_lock != current_lock:
        if desired_lock is None:
            io.remove(project, state.LOCK_PATH, current_lock)
        else:
            io.publish(project, state.LOCK_PATH, desired_lock, current_lock, operation.document["operation_id"])
    io.expect(project, state.LOCK_PATH, desired_lock)
    if target and target.document["lock_version"] == 2:
        for row in target.document["project_inputs"]:
            state._check(_hash(io.raw(project, row["path"])) == row["sha256"], "project-input-drift", "Paired project input differs after transition.", row["path"], "conflict")
    io.changes.lock_sha256 = _hash(desired_lock)
    _verify_target(io, project, operation, target)
    # The marker is the final namespace removal. Failed read-back remains an
    # incomplete result even if a subsequent inspection finds matching bytes.
    io.remove(project, state.MARKERS[1], operation.raw)
    io.remove(project, state.MARKERS[0], operation.raw)
    io.expect(project, state.LOCK_PATH, desired_lock)
    _verify_target(io, project, operation, target)
    io.expect(project, state.MARKERS[0], None)
    io.changes.protected = _protected(io, project, operation.document["protected_inputs"], operation.names, reconstruct=reconstruct)
    guard.verify()


def apply(request: dict | bytes) -> dict:
    """Recompute accepted plan under native exclusion, capture, then exact publish."""
    changes = Changes()
    try:
        request = state._request(request, "apply", planning.PLAN_FIELDS | {"expected_plan_sha256", "maintenance"})
        state._digest(request["expected_plan_sha256"])
        reader = state._Reader()
        prepared = planning._prepare(request, reader)
        preview, candidate, observation, roots, backend = prepared
        state._check(preview["plan_sha256"] == request["expected_plan_sha256"], "plan-conflict", "Recomputed preview differs from the accepted plan hash.", outcome="conflict")
        declaration(request["maintenance"], preview["plan"]["maintenance_scope"])
        changes.protected = "matches" if request["protected_inputs"] else "not-selected"
        changes.lock_sha256 = observation.lock.sha256 if observation.lock else None
        noop = preview["plan"]["noop"]
        io = IO(backend, reader, changes)
        # Actual layout preflight precedes even first-install guard/parent writes.
        # No-op allocates neither ID nor directory nor content.
        operation_id = None if noop else secrets.token_hex(16)
        if not noop:
            operation = _bundle(request, prepared, operation_id, reader)
            _layout(io, roots, operation, preview["plan"]["delta"])
        with WriterLock(io, roots["project"], allow_create=not noop) as guard:
            prepared = planning._prepare(request, reader, own_guard=guard.created)
            result, candidate, observation, roots, _ = prepared
            state._check(result["plan_sha256"] == request["expected_plan_sha256"], "plan-conflict", "Locked recomputation differs from accepted plan.", outcome="conflict")
            declaration(request["maintenance"], result["plan"]["maintenance_scope"])
            guard.verify()
            discharged = {"writer-guard", "fresh-input-observation", "maintenance-quiescence"}
            if noop:
                state._check(result["plan"]["noop"], "noop-drift", "No-op state changed before coordination.", outcome="conflict")
                _admit(result["plan"], discharged)
                changes.counts["unchanged"] = len(candidate.members)
                answer = _result("apply", "unchanged", changes, "managed-bytes-consistent")
            else:
                operation = _bundle(request, prepared, operation_id, reader)
                _layout(io, roots, operation, result["plan"]["delta"])
                _capture(io, roots, prepared, operation)
                discharged.add("exclusive-operation-allocation")
                _admit(result["plan"], discharged)
                state._engine(reader, roots["engine"], request["engine"])
                # All-old observation again before marker; current() alone permits
                # after states and cannot confer apply ownership.
                current = _current(io, roots["project"], operation)
                state._check(_matches(operation, current, operation.before, io.raw(roots["project"], state.LOCK_PATH), backend.windows),
                             "pre-marker-drift", "All old members and lock must still match before marker admission.", outcome="conflict")
                changes.protected = _protected(io, roots["project"], operation.document["protected_inputs"], operation.names)
                io.expect(roots["project"], state.MARKERS[1], None)
                guard.verify()
                io.publish(roots["project"], state.MARKERS[0], operation.raw, None, operation_id)
                changes.marker_admitted = True
                io.publish(roots["project"], state.MARKERS[1], operation.raw, None, operation_id)
                _transition(io, guard, roots["project"], operation, current, operation.after)
                _finish(io, guard, roots["project"], operation, operation.after, operation.before.raw if operation.before else None)
                answer = _result("apply", "applied", changes, "managed-bytes-consistent", _mode_note(result["plan"]["delta"]))
        return answer
    except ERRORS as exc:
        return _failed("apply", exc, changes)


def _recovery_controls(io: IO, project: Path, operation: Operation, request: dict) -> tuple:
    paired_marker = io.raw(project, state.MARKERS[1], state.LIMITS["document_bytes"])
    state._check(paired_marker in (None, operation.raw), "unrelated-marker", "Project marker differs from retained operation.", state.MARKERS[1], "conflict")
    lock = io.raw(project, state.LOCK_PATH, state.LIMITS["document_bytes"])
    marker = io.raw(project, state.MARKERS[0], state.LIMITS["document_bytes"])
    state._check(_hash(lock) == request["expected_lock_sha256"] and _hash(marker) == request["expected_marker_sha256"],
                 "recovery-control-binding", "Current lock/marker differs from explicitly expected raw hash/absence.", outcome="conflict")
    state._check(paired_marker is None or marker == operation.raw, "recovery-incomplete", "A project marker without its managed marker is not a known phase.")
    state._check(marker in (None, operation.raw), "unrelated-marker", "Marker is not this exact immutable operation; malformed/newer state is preserved.", state.MARKERS[0], "conflict")
    state._check(lock == operation.after.raw or lock == (operation.before.raw if operation.before else None)
                 or (request.get("reconstruct_missing_managed", False) and lock is None),
                 "unrelated-lock", "Lock is not an exact before/after binding; unknown/torn/newer state is preserved.", state.LOCK_PATH, "conflict")
    return lock, marker


def _sibling_residue(io: IO, project: Path, operation: Operation, siblings: dict) -> dict:
    residue = {}
    before_members = operation.descriptors(operation.before)
    for destination, temporary in siblings.items():
        raw = io.raw(project, temporary)
        if raw is None:
            continue
        if destination in state.MARKERS:
            options = [(operation.raw, "100644")]
        elif destination == state.LOCK_PATH:
            options = [(lock.raw, "100644") for lock in (operation.before, operation.after) if lock]
        else:
            options = [(operation.objects[row["sha256"]], row["mode"])
                       for row in (before_members.get(destination), operation.descriptors(operation.after).get(destination)) if row]
        state._check(any(raw == content and (io.backend.windows or stat.S_IMODE((project / temporary).lstat().st_mode)
                         == (0o755 if mode == "100755" else 0o644)) for content, mode in options),
                     "unknown-sibling", "Sibling is not a complete exact captured file; preserve partial/unknown residue for owner reconciliation.", temporary, "conflict")
        residue[temporary] = raw
    return residue


def recover(request: dict | bytes) -> dict:
    """Exact-record finish/restore; retained completed operations confer no rollback."""
    changes = Changes()
    try:
        request = state._request(request, "recover", {"operation_root", "operation_sha256", "direction",
                                 "expected_lock_sha256", "expected_marker_sha256", "maintenance"}, {"reconstruct_missing_managed"})
        for key in ("operation_sha256", "expected_lock_sha256", "expected_marker_sha256"):
            state._digest(request[key], nullable=key != "operation_sha256")
        state._check(request["direction"] in {"finish", "restore"}, "recovery-direction", "Direction must be finish or restore.")
        reconstruct = request.get("reconstruct_missing_managed", False)
        state._check(reconstruct is False, "unsupported-reconstruction", "Paired project edits require exact retained before/after state; whole-project reconstruction is not selected.", outcome="unsupported")
        state._check(type(reconstruct) is bool, "reconstruction-flag", "Reconstruction must be an exact boolean.")
        reader = state._Reader()
        project, engine, operation_root = (state._root(request[key]) for key in ("project_root", "engine_root", "operation_root"))
        roots = {"project": project, "engine": engine, "recovery": state._root(str(operation_root.parent))}
        state._roots_disjoint(roots)
        state._engine(reader, engine, request["engine"])
        operation = _read_operation(reader, operation_root, request["operation_sha256"], request["engine"], project)
        declaration(request["maintenance"], operation.scope)
        backend = Backend(roots, operation.document["durability"])
        io = IO(backend, reader, changes)
        changes.operation_root = str(operation_root)
        siblings = _layout(io, roots, operation)
        lock, marker = _recovery_controls(io, project, operation, request)
        current = _current(io, project, operation, reconstruct=reconstruct)
        _sibling_residue(io, project, operation, siblings)
        changes.protected = _protected(io, project, operation.document["protected_inputs"], operation.names, reconstruct=reconstruct)
        if reconstruct:
            state._check(lock is None and marker is None, "whole-loss-controls", "Whole-loss reconstruction needs absent lock and markers.", outcome="conflict")
        target = operation.after if request["direction"] == "finish" else operation.before
        # A matching target is a read-only recovery observation, even when the
        # caller supplied a reconstruction flag; it cannot create missing guard.
        needs_reconstruction = reconstruct and not _matches(operation, current, target, lock, backend.windows)
        with WriterLock(io, project, allow_create=needs_reconstruction) as guard:
            state._engine(reader, engine, request["engine"])
            operation = _read_operation(reader, operation_root, request["operation_sha256"], request["engine"], project)
            declaration(request["maintenance"], operation.scope)
            lock, marker = _recovery_controls(io, project, operation, request)
            current = _current(io, project, operation, reconstruct=reconstruct)
            residue = _sibling_residue(io, project, operation, siblings)
            changes.protected = _protected(io, project, operation.document["protected_inputs"], operation.names, reconstruct=reconstruct)
            changes.lock_sha256 = _hash(lock)
            if marker is None and not needs_reconstruction:
                state._check(_matches(operation, current, target, lock, backend.windows), "completed-operation-replay",
                             "Without its marker a retained operation is read-only evidence; a fresh package plan is required for another state.", outcome="conflict")
                changes.counts["unchanged"] = len(operation.names)
                answer = _result("recover", "already-matching", changes, "managed-bytes-consistent" if target else "uninstalled")
            else:
                changes.marker_admitted = marker is not None
                marker_sibling = siblings[state.MARKERS[0]]
                if marker_sibling in residue:
                    io.remove(project, marker_sibling, residue.pop(marker_sibling))
                if marker is None:
                    io.publish(project, state.MARKERS[0], operation.raw, None, operation.document["operation_id"])
                changes.marker_admitted = True
                guard.verify()
                for control in state.MARKERS:
                    temporary = siblings[control]
                    if temporary in residue:
                        io.remove(project, temporary, residue.pop(temporary))
                paired_marker = io.raw(project, state.MARKERS[1], state.LIMITS["document_bytes"])
                if paired_marker is None:
                    io.publish(project, state.MARKERS[1], operation.raw, None, operation.document["operation_id"])
                for name, raw in residue.items():
                    io.remove(project, name, raw)
                _transition(io, guard, project, operation, current, target)
                _finish(io, guard, project, operation, target, lock, reconstruct=reconstruct)
                before_members = operation.descriptors(operation.before)
                mode_rows = [{"action": "mode-only"} for name, row in operation.after.members.items()
                             if name in before_members and row["sha256"] == before_members[name]["sha256"]
                             and row["mode"] != before_members[name]["mode"]]
                diagnostics = _mode_note(mode_rows)
                if changes.protected == "unresolved":
                    diagnostics.append({"code": "project-inputs-missing", "path": None,
                                        "reason": "Selected protected inputs are absent after whole-loss reconstruction; only managed bytes were restored.",
                                        "next_action": "Project owner must recover source/config/data and select activation checks separately."})
                answer = _result("recover", "recovered", changes, "managed-bytes-consistent" if target else "uninstalled", diagnostics)
        return answer
    except ERRORS as exc:
        return _failed("recover", exc, changes)


def execute(request: dict | bytes) -> dict:
    """Dispatch exactly inspect/plan/apply/recover; no general command surface."""
    try:
        if type(request) is bytes:
            request = state._document(request, "request.json", canonical=False)
        state._check(type(request) is dict and type(request.get("operation")) is str, "invalid-request", "A closed operation request is required.")
        operation = request["operation"]
        state._check(operation in {"inspect", "plan", "apply", "recover"}, "unsupported-operation", "Only inspect, plan, apply and recover are supported.", outcome="unsupported")
        return {"inspect": inspect, "plan": plan, "apply": apply, "recover": recover}[operation](request)
    except ERRORS as exc:
        result = state._failure("inspect", exc)
        result["details"] = {"managed_state": result["outcome"], "project_readiness": "not-assessed",
                             "owned": None, "unknown": None, "drift": None, "mode_policy": None}
        return result


def _edit_record(rows, reader, root, objects, managed, protected):
    state._array(rows, state.LIMITS["protected_inputs"])
    names = []
    for row in rows:
        state._shape(row, {"intent", "before", "after"})
        intent = state._shape(row["intent"], {"path", "before_sha256", "after_sha256", "after_content_ref"})
        name = state._relative(intent["path"]); names.append(name)
        state._check(not name.startswith((".ai/core/", ".ai/local/", ".git/")) and name not in {".ai/core", ".ai/local", ".git"},
                     "project-edit-boundary", "Retained project edit crosses storage ownership.", name)
        for side in ("before", "after"):
            state._digest(intent[side + "_sha256"], nullable=True)
            value = row[side]
            if value is None:
                state._check(intent[side + "_sha256"] is None, "project-edit-binding", "Absent descriptor needs explicit absent intent.", name)
            else:
                state._shape(value, {"sha256", "size", "mode"}); state._descriptor(value)
                state._check(value["sha256"] == intent[side + "_sha256"], "project-edit-binding", "Intent and retained descriptor differ.", name)
                raw = _object(reader, root, value["sha256"], objects)
                state._check(len(raw) == value["size"], "project-edit-binding", "Retained project content size differs.", name)
        state._check(intent["after_content_ref"] == ("objects/" + intent["after_sha256"] if intent["after_sha256"] else None),
                     "project-edit-object", "Invalid retained after-content address.", name)
        if row["before"] is not None and row["after"] is not None:
            state._check(row["before"]["mode"] == row["after"]["mode"], "project-edit-mode", "An intent cannot change project mode.", name)
    state._sorted(rows, lambda r:r["intent"]["path"])
    state._paths(sorted(managed | {state.LOCK_PATH, state.GUARD_PATH, *state.MARKERS}) + names + [r["path"] for r in protected])
