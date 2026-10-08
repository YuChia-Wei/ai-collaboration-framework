"""Explicit breaking reinstall of Git-backed framework resources.

Cleanup is deliberately destructive, not a legacy migration or atomic upgrade.
Git is the recovery source for committed cleanup files. The ordinary paired
installer still owns publication of the selected new subset and project edits.
"""
from __future__ import annotations

from hashlib import sha256
from pathlib import Path
import os
import re
import stat
import subprocess

from . import installation_state as state
from . import installation
from .data import json_bytes
from .installation_io import platform_diagnostics

SCOPES = (".ai", ".dev", ".agents/skills", ".claude/skills")
FIELDS = {"reinstall_version", "operation", "project_root", "expected_head",
          "cleanup", "preserved_inputs", "preview_root", "installation", "maintenance",
          "all_framework_activity_stopped"}


def _git(root, *args, input_bytes=None):
    result = subprocess.run(["git", "-C", str(root), *args], stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, input=input_bytes, check=False)
    state._check(result.returncode == 0, "reinstall-git", "Selected Git baseline is unavailable.")
    return result.stdout


def _scope(name):
    return any(name == prefix or name.startswith(prefix + "/") for prefix in SCOPES)


def _native_relative(name):
    """Exact target preservation names; package/cleanup paths stay portable."""
    state._text(name)
    parts = name.split("/")
    state._check(len(parts) <= state.LIMITS["depth"] and len(name.encode("utf-16-le")) // 2 <= state.LIMITS["path_utf16"]
                 and all(part not in {"", ".", ".."} and not part.endswith((".", " "))
                         and not re.search(r'[\\<>:"|?*\x00-\x1f\x7f]', part)
                         and re.fullmatch(r'(?i)(CON|PRN|AUX|NUL|COM[0-9¹²³]|LPT[0-9¹²³])(?:\..*)?', part) is None
                         for part in parts),
                 "reinstall-preservation-path", "Preservation requires a bounded exact native relative path.")
    return name


def _native_paths(names):
    rows = sorted((_native_relative(n).casefold() for n in names))
    present = set(rows)
    state._check(len(rows) == len(present) and not any('/'.join(row.split('/')[:i]) in present
                 for row in rows for i in range(1, len(row.split('/')))),
                 "reinstall-path-alias", "Preservation paths contain duplicate, case or prefix aliases.")


def _locate_native(reader, root, name):
    parts = _native_relative(name).split("/")
    current = root
    for index, part in enumerate(parts):
        actual = reader.listing(current).get(part.casefold())
        if actual is None:
            return None
        state._check(actual == part, "path-alias", "Existing preservation spelling differs.", name)
        current = current / part
        info = current.lstat()
        state._plain(info, name)
        state._check(index == len(parts) - 1 or stat.S_ISDIR(info.st_mode),
                     "parent-collision", "Preservation parent is occupied by a file.", name)
    return current


def _git_filter_boundary(root, tracked):
    # Query keys only: configured command text may contain credentials. Git's
    # attribute sentinels also happen to be valid string driver names.
    configured = subprocess.run(["git", "-C", str(root), "config", "--name-only", "--get-regexp",
                                 "^filter[.](unset|unspecified)[.]"],
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    state._check(configured.returncode in {0, 1} and not configured.stdout,
                 "reinstall-git-filter", "Ambiguous custom Git filter drivers are unsupported.")
    if tracked:
        attributes = _git(root, "check-attr", "-z", "--stdin", "filter",
                          input_bytes=("\0".join(sorted(tracked)) + "\0").encode("utf-8")).decode("utf-8").split("\0")
        state._check(all(attributes[i + 2] in {"unspecified", "unset"} for i in range(0, len(attributes) - 1, 3)),
                     "reinstall-git-filter", "Custom Git content filters are unsupported for breaking reinstall.")


def _scan(reader, root):
    """Complete bounded inventory, refusing links, hard links and aliases."""
    result = {}
    def visit(name):
        target = _locate_native(reader, root, name)
        if target is None:
            return
        info = target.lstat()
        state._plain(info, name)
        state._check(info.st_dev == root.stat().st_dev and not os.path.ismount(target),
                     "reinstall-volume", "Scoped resources cannot cross a mount or volume boundary.", name)
        if stat.S_ISDIR(info.st_mode):
            for child in sorted(target.iterdir(), key=lambda p: p.name):
                visit(name + "/" + child.name)
        else:
            state._check(stat.S_ISREG(info.st_mode) and info.st_nlink == 1,
                         "reinstall-file-type", "Framework scope contains a non-direct file.", name)
            raw = reader.read(target, name)
            result[name] = {"path": name, "sha256": sha256(raw).hexdigest(),
                            "size": len(raw), "mode": "100755" if os.name != "nt" and
                            stat.S_IMODE(info.st_mode) == 0o755 else "100644"}
            state._check(len(result) <= state.LIMITS["members"], "reinstall-budget", "Scoped inventory exceeds its bound.")
    for prefix in SCOPES:
        visit(prefix)
    return result


def _pins(rows, root, reader, *, preservation=False):
    state._array(rows)
    for row in rows:
        state._shape(row, {"path", "sha256"})
        (_native_relative if preservation else state._relative)(row["path"])
        state._digest(row["sha256"])
    state._sorted(rows, lambda r: r["path"])
    (_native_paths if preservation else state._paths)([r["path"] for r in rows])
    for row in rows:
        target = _locate_native(reader, root, row["path"]) if preservation else reader.locate(root, row["path"])
        state._check(target is not None and sha256(reader.read(target, row["path"])).hexdigest() == row["sha256"],
                     "reinstall-preimage", "Explicit file preimage differs or is missing.", row["path"], "conflict")


def _prepare(request):
    state._shape(request, FIELDS, {"expected_plan_sha256"})
    state._check(type(request["reinstall_version"]) is int and request["reinstall_version"] == 1,
                 "reinstall-version", "Unsupported breaking reinstall version.")
    state._check(request["operation"] in {"plan", "apply"}, "reinstall-operation", "Choose plan or apply.")
    state._check(request["all_framework_activity_stopped"] is True, "reinstall-quiescence",
                 "Explicitly stop all old and new framework activity for the complete non-atomic reset.")
    reader = state._Reader()
    project = state._root(request["project_root"])
    preview = state._root(request["preview_root"])
    install = dict(request["installation"])
    install["operation"] = "plan"
    install["project_root"] = str(project)
    state._request(install, "plan", installation.planning.PLAN_FIELDS)
    state._check(install["expected_lock_sha256"] is None, "reinstall-lock", "New installation starts without the retired lock.")
    roots = {"project": project, "preview": preview, **{
        role: state._root(install[role + "_root"]) for role in ("engine", "candidate", "scratch", "staging", "recovery")}}
    state._roots_disjoint(roots)
    state._engine(reader, roots["engine"], install["engine"])
    candidate = state.read_candidate(install["candidate_root"], _reader=reader)
    state._check(candidate.identity == install["candidate_identity"], "reinstall-candidate", "Selected candidate identity differs.")
    state._oid(request["expected_head"])
    state._check(_git(project, "rev-parse", "--show-toplevel").decode().strip().replace("\\", "/").casefold() == str(project).replace("\\", "/").casefold(),
                 "reinstall-git-root", "Project root must be the exact Git worktree root.")
    state._check(_git(project, "rev-parse", "HEAD").decode().strip() == request["expected_head"],
                 "reinstall-head", "Git HEAD differs from the selected recovery baseline.", outcome="conflict")
    tracked = set(_git(project, "ls-files", "-z").decode("utf-8").split("\0")) - {""}
    _git_filter_boundary(project, tracked)  # Before any command that may run a filter.
    state._check(not _git(project, "diff", "--no-ext-diff", "--no-textconv", "--name-only", "HEAD", "--"),
                 "reinstall-dirty", "Commit or separately reconcile tracked edits before destructive reinstall.", outcome="conflict")
    inventory = _scan(reader, project)
    state._check(not any(reader.locate(project, name) is not None for name in state.MARKERS),
                 "maintenance-marker", "An incomplete operation must be recovered before breaking reinstall.")
    _pins(request["cleanup"], project, reader)
    _pins(request["preserved_inputs"], project, reader, preservation=True)
    clean = {r["path"] for r in request["cleanup"]}
    keep = {r["path"] for r in request["preserved_inputs"]}
    edit = {r["path"] for r in install["project_edits"]}
    _native_paths(sorted(clean | keep | edit))
    state._check(not (clean & keep or clean & edit or keep & edit), "reinstall-overlap", "Cleanup, preserved files and project edits must be disjoint.")
    for name in clean:
        state._check(_scope(name) and name not in state.MARKERS and not name.startswith(".ai/local/"),
                     "reinstall-boundary", "Cleanup must select framework resource files, excluding coordination storage.", name)
        state._check(not name.startswith((".dev/workflows/", ".dev/workflows-v2/")), "reinstall-workflow",
                     "Source and project workflow records cannot be cleanup resources.", name)
        state._check(name in tracked, "reinstall-untracked", "Untracked or ignored files cannot be destructively removed.", name)
    flags = {row[2:]: row[:1] for row in _git(project, "ls-files", "-v", "-z").decode("utf-8").split("\0") if row}
    tree = {}
    for row in _git(project, "ls-tree", "-r", "-z", "HEAD").decode("utf-8").split("\0"):
        if row:
            descriptor, name = row.split("\t", 1)
            mode, kind, oid = descriptor.split(" ")
            tree[name] = (mode, kind, oid)
    ordered = sorted(clean)
    for name in ordered:
        state._check(flags.get(name) == "H" and name in tree and tree[name][0] in state.MODES and tree[name][1] == "blob",
                     "reinstall-git-flags", "Cleanup needs an ordinary tracked regular file without hidden index flags.", name)
    if ordered:
        actual = _git(project, "hash-object", "--stdin-paths", input_bytes=("\n".join(ordered) + "\n").encode("utf-8")).decode("ascii").splitlines()
        state._check(actual == [tree[n][2] for n in ordered], "reinstall-git-preimage",
                     "Cleanup content is not represented by the selected Git baseline.", outcome="conflict")
        _pins(request["cleanup"], project, reader)
    state._check(state.LOCK_PATH not in inventory or state.LOCK_PATH in clean,
                 "reinstall-old-lock", "The exact old framework lock must be selected for retirement.")
    state._check(set(inventory) <= clean | keep | edit,
                 "reinstall-unclassified", "Every scoped file needs cleanup, preservation or an explicit project edit.")
    state._check(not any(name in candidate.members for name in keep),
                 "reinstall-preserved-collision", "Candidate cannot overwrite a preserved file.")
    state._check(all(name not in inventory or name in clean for name in candidate.members),
                 "reinstall-collision", "Existing candidate destinations must be explicitly selected for cleanup.")
    guard = reader.locate(project, state.GUARD_PATH)
    if guard is not None:
        # Guard is coordination-owned, never user data. Its inert shape is
        # verified and native writer exclusion is probed before reset below.
        info = guard.lstat()
        state._check(stat.S_ISREG(info.st_mode) and info.st_size == 0 and info.st_nlink == 1,
                     "guard-conflict", "Existing writer guard is not the inert coordination file.", state.GUARD_PATH)
        state._check(state.GUARD_PATH in keep, "reinstall-guard", "Inventory must explicitly acknowledge the existing guard.")
    scope = sorted(r["id"] for r in candidate.selection["components"])
    from .maintenance_coordination import declaration
    declaration(request["maintenance"], scope)
    document = {"reinstall_version": 1, "project_root": str(project), "expected_head": request["expected_head"],
                "candidate_identity": candidate.identity, "cleanup": request["cleanup"],
                "preserved_inputs": request["preserved_inputs"], "scoped_inventory": [inventory[n] for n in sorted(inventory)],
                "coordination_reset": state.GUARD_PATH if guard else None,
                "all_framework_activity_stopped": True,
                "installation": install, "maintenance": request["maintenance"], "preview_root": str(preview),
                "atomic": False, "recovery": "Git baseline for committed cleanup; pinned API 2 journal for new installation."}
    return document, roots, reader, candidate


def _preview(document, roots, reader):
    """Stage only retained inputs in a caller-selected external preview root."""
    clean = {r["path"] for r in document["cleanup"]}
    names = {r["path"] for r in document["scoped_inventory"]} - clean - {state.GUARD_PATH}
    names.update(r["path"] for r in document["installation"]["protected_inputs"] if r["sha256"] is not None)
    names.update(r["path"] for r in document["installation"]["project_edits"] if r["before_sha256"] is not None)
    def preview_files(directory):
        found = set()
        for spelling in reader.listing(directory).values():
            item = directory / spelling
            name = item.relative_to(roots["preview"]).as_posix()
            _native_relative(name)
            info = item.lstat()
            state._plain(info, name)
            state._check(info.st_dev == roots["preview"].stat().st_dev and not os.path.ismount(item),
                         "reinstall-preview-volume", "Preview cannot cross a mount or volume boundary.", name)
            if stat.S_ISDIR(info.st_mode):
                found.update(preview_files(item))
            else:
                state._check(stat.S_ISREG(info.st_mode) and info.st_nlink == 1,
                             "reinstall-preview-type", "Preview must contain direct files only.", name)
                found.add(name)
        return found
    state._check(preview_files(roots["preview"]) <= names, "reinstall-preview-collision", "Preview root contains unrelated files.")
    retained = {}
    missing = []
    # Observe the complete stable destination before our namespace mutations.
    # Re-listing a growing sibling directory for every write is quadratic and
    # would consume the unchanged entry bound for ordinary historical data.
    for name in sorted(names):
        source = _locate_native(reader, roots["project"], name)
        state._check(source is not None, "reinstall-preview-input", "Retained preview input is unavailable.", name)
        raw = reader.read(source, name)
        retained[name] = raw
        target = _locate_native(reader, roots["preview"], name)
        if target is None:
            missing.append(name)
        else:
            state._check(reader.read(target, name) == raw, "reinstall-preview-drift", "Retained preview differs; choose another empty preview root.", name)
    for name in missing:
        destination = roots["preview"] / name
        # Existing spellings were checked above under declared quiescence.
        destination.parent.mkdir(parents=True, exist_ok=True)
        state._no_links(destination.parent)
        with destination.open("xb") as stream:
            stream.write(retained[name])
        if os.name != "nt":
            os.chmod(destination, stat.S_IMODE((roots["project"] / name).lstat().st_mode))
    # Own writes invalidate the old observations. A fresh, independently bounded
    # complete snapshot verifies exact closure, paths and bytes before cleanup.
    reader = state._Reader()
    state._check(preview_files(roots["preview"]) == names, "reinstall-preview-collision", "Preview closure changed during materialization.")
    for name, raw in retained.items():
        target = _locate_native(reader, roots["preview"], name)
        state._check(target is not None and reader.read(target, name) == raw,
                     "reinstall-preview-drift", "Retained preview changed during materialization.", name)
    request = {**document["installation"], "project_root": str(roots["preview"])}
    result = installation.plan(request)
    state._check(result["outcome"] == "planned", "reinstall-install-preflight", "New installation preview was rejected; target cleanup has not started.")
    return result


def execute(request):
    removed = []
    answer = {"reinstall_version": 1, "operation": request.get("operation"), "changed": False}
    if notes := platform_diagnostics():
        answer["diagnostics"] = notes
    try:
        document, roots, reader, candidate = _prepare(request)
        preview = _preview(document, roots, reader)
        document["installation_preview"] = preview["plan"]
        digest = sha256(json_bytes(document)).hexdigest()
        answer.update(plan=document, plan_sha256=digest)
        if request["operation"] == "plan":
            return {**answer, "outcome": "planned", "preview_allocated": True}
        state._digest(request.get("expected_plan_sha256"))
        state._check(digest == request["expected_plan_sha256"], "reinstall-plan-drift", "Fresh breaking plan differs from the selected plan.", outcome="conflict")
        # Verify the entire snapshot again before the first destructive syscall.
        repeated, _, _, _ = _prepare(request)
        state._check(repeated == {k: v for k, v in document.items() if k != "installation_preview"},
                     "reinstall-input-drift", "Breaking reinstall inputs changed before cleanup.")
        reader = state._Reader()  # Cleanup has its own complete bounded read budget.
        if document["coordination_reset"]:
            from .installation_io import Backend, IO, Changes
            from .maintenance_coordination import WriterLock
            backend = Backend({k: v for k, v in roots.items() if k != "preview"}, document["installation"]["durability"])
            io = IO(backend, reader, Changes())
            with WriterLock(io, roots["project"], allow_create=False) as held:
                held.verify()
            # Caller declares complete quiescence across the non-atomic reset.
            (roots["project"] / state.GUARD_PATH).unlink()
            answer["changed"] = True
        for row in document["cleanup"]:
            _pins([row], roots["project"], reader)
            (roots["project"] / row["path"]).unlink()
            removed.append(row["path"])
            answer["changed"] = True
        reader = state._Reader()
        _pins([r for r in document["preserved_inputs"] if r["path"] != state.GUARD_PATH], roots["project"], reader, preservation=True)
        actual = installation.plan(document["installation"])
        state._check(actual["outcome"] == "planned", "reinstall-after-cleanup", "New installation planning failed after destructive cleanup; retain evidence and use Git recovery.")
        for field in ("candidate_identity", "engine", "expected_lock_sha256", "mode_policy", "delta",
                      "project_edits", "project_inputs", "protected_inputs", "maintenance_scope", "noop"):
            state._check(actual["plan"][field] == preview["plan"][field], "reinstall-after-drift", "New installation intent changed after cleanup.")
        result = installation.apply({**document["installation"], "operation": "apply",
                                     "expected_plan_sha256": actual["plan_sha256"], "maintenance": document["maintenance"]})
        answer["installation_result"] = result
        state._check(result["outcome"] == "applied", "reinstall-install-failed", "Destructive cleanup completed, but new installation did not complete; use its exact recovery evidence.")
        reader = state._Reader()
        _pins([r for r in document["preserved_inputs"] if r["path"] != state.GUARD_PATH], roots["project"], reader, preservation=True)
        state._check(all(reader.locate(roots["project"], r["path"]) is None for r in document["cleanup"]
                         if r["path"] not in candidate.members and r["path"] != state.LOCK_PATH),
                     "reinstall-remnant", "A selected obsolete file remains after installation.")
        return {**answer, "outcome": "reinstalled", "removed": removed, "preserved": "hashes-match",
                "project_readiness": "not-assessed"}
    except (state.InstallationError, OSError, ValueError, TypeError, KeyError, UnicodeError) as exc:
        return {**answer, "outcome": "cleanup-incomplete" if answer["changed"] else getattr(exc, "outcome", "blocked"),
                "removed": removed, "diagnostics": [getattr(exc, "diagnostic", {
                    "code": "reinstall-input", "path": None, "reason": "Breaking reinstall was rejected or interrupted.",
                    "next_action": "Preserve the result; Git baseline owns cleanup recovery, API 2 owns any new operation recovery."})] + platform_diagnostics()}
