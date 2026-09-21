"""Restricted workflow/assessment authoring over existing family validators.

Preview is read-only. Apply re-derives a preview, then writes a recoverable bundle
under an exclusive cooperative lock. Individual replacements are atomic; the
bundle is NOT a filesystem transaction. Recovery only rolls back unchanged
candidate bytes and never accepts caller-supplied output paths as authority.
"""
from __future__ import annotations

import base64
import difflib
import hashlib
import importlib.util
import json
import os
import re
import stat
import subprocess
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml

WORKFLOW_TEMPLATE = ".ai/assets/skills/ai-context-governance/templates/workflow-locator-template.yaml"
PLAN_TEMPLATE = ".ai/assets/skills/ai-context-governance/templates/ai-context-maintenance-workflow-plan-template.md"
TASK_TEMPLATE = ".ai/assets/skills/ai-context-governance/templates/ai-context-remediation-task-template.json"
ASSESSMENT_TEMPLATE = ".dev/assessments/templates/assessment-locator-template.yaml"
REPORT_TEMPLATE = ".ai/assets/skills/ai-context-auditor/templates/ai-context-audit-report-template.md"
LOCAL = ".dev/ai-context/local/artifact-authoring"
OPERATIONS = {
    "workflow.create", "workflow.add-task", "workflow.transition", "workflow.update",
    "assessment.create", "assessment.update", "assessment.finalize",
}


class AuthoringError(ValueError):
    """Actionable input, stale-preview, or recovery refusal."""


def digest(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def canonical(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")


class _StrictLoader(yaml.SafeLoader):
    pass


def _mapping(loader: _StrictLoader, node: yaml.MappingNode) -> dict:
    result = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node)
        if not isinstance(key, str) or key in result:
            raise AuthoringError(f"mapping keys must be unique strings; duplicate/invalid key {key!r}")
        result[key] = loader.construct_object(value_node)
    return result


_StrictLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _mapping)


def parse(text: str, label: str = "input") -> dict:
    """JSON-compatible YAML only: exact types, no duplicates, aliases or tags."""
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise AuthoringError(f"duplicate key {key!r}")
            result[key] = value
        return result

    try:
        try:
            value = json.loads(text, object_pairs_hook=pairs)
        except json.JSONDecodeError:
            for token in yaml.scan(text):
                if isinstance(token, (yaml.tokens.AliasToken, yaml.tokens.AnchorToken, yaml.tokens.TagToken)):
                    raise AuthoringError("aliases, anchors and explicit tags are unsupported")
            value = yaml.load(text, Loader=_StrictLoader)
        canonical(value)  # rejects timestamps, NaN and other non-JSON values
    except (yaml.YAMLError, TypeError, ValueError, RecursionError) as exc:
        raise AuthoringError(f"{label}: invalid strict JSON/YAML: {exc}") from exc
    if type(value) is not dict:
        raise AuthoringError(f"{label}: expected a mapping")
    return value


def fields(value: dict, required: set[str], optional: set[str], label: str) -> None:
    if type(value) is not dict:
        raise AuthoringError(f"{label}: expected a mapping")
    missing, unknown = required - value.keys(), value.keys() - required - optional
    if missing or unknown:
        raise AuthoringError(f"{label}: missing={sorted(missing)}, unsupported={sorted(unknown)}; use catalog-supported semantic fields")


def string(value: Any, label: str, *, empty: bool = False) -> str:
    if type(value) is not str or (not empty and not value.strip()):
        raise AuthoringError(f"{label}: expected {'a' if empty else 'a non-empty'} string")
    return value


def strings(value: Any, label: str) -> list[str]:
    if type(value) is not list or any(type(item) is not str or not item.strip() for item in value):
        raise AuthoringError(f"{label}: expected a list of non-empty strings")
    if len(value) != len(set(value)):
        raise AuthoringError(f"{label}: duplicate list entries are not supported")
    return value


def instant(value: Any) -> datetime:
    value = string(value, "timestamp")
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})", value):
        raise AuthoringError("timestamp: supply seconds and an explicit UTC offset")
    try:
        return datetime.fromisoformat(value)
    except ValueError as exc:
        raise AuthoringError(f"timestamp: {exc}") from exc


def safe_path(root: Path, relative: str) -> Path:
    """Reject traversal, Windows device names, links and reparse points."""
    if not isinstance(relative, str) or not relative or any(c in relative for c in "\\:\x00"):
        raise AuthoringError(f"unsafe repository path {relative!r}")
    pieces = relative.split("/")
    if any(not part or part in {".", ".."} or part.endswith((".", " ")) or
           re.fullmatch(r"(?i)(con|prn|aux|nul|com[1-9]|lpt[1-9])(?:\..*)?", part) for part in pieces):
        raise AuthoringError(f"unsafe repository path {relative!r}")
    target = root
    for part in pieces:
        target = target / part
        if target.is_symlink():
            raise AuthoringError(f"refusing symbolic link: {relative}")
        if target.exists():
            info = target.lstat()
            if getattr(info, "st_file_attributes", 0) & stat.FILE_ATTRIBUTE_REPARSE_POINT:
                raise AuthoringError(f"refusing junction/reparse point: {relative}")
            if stat.S_ISREG(info.st_mode) and info.st_nlink != 1:
                raise AuthoringError(f"refusing hard-linked file: {relative}")
            if not (stat.S_ISREG(info.st_mode) or stat.S_ISDIR(info.st_mode)):
                raise AuthoringError(f"refusing special file: {relative}")
    if root not in target.resolve().parents:
        raise AuthoringError(f"path escapes repository: {relative}")
    return target


class View:
    """Read-only filesystem overlay; no files are copied and Git sees real cwd."""
    def __init__(self, root: Path, baseline: dict[str, bytes | None] | None = None):
        self.root = root.resolve()
        self.baseline = baseline or {}
        self.hidden_directories: set[str] = set()
        for rel, data in self.baseline.items():
            if data is None:
                parts = rel.split("/")
                # A create operation owns only a new artifact directory, never
                # the family root. Recovery checks its physical contents first.
                for length in range(3, len(parts)):
                    self.hidden_directories.add("/".join(parts[:length]))
        self.overlay: dict[str, bytes] = {}
        self.observed: dict[str, Any] = {}

    def read(self, rel: str) -> bytes | None:
        target = safe_path(self.root, rel)
        data = self.baseline[rel] if rel in self.baseline else target.read_bytes() if target.is_file() else None
        self.observed["file:" + rel] = None if data is None else digest(data)
        return self.overlay.get(rel, data)

    def put(self, rel: str, data: bytes, *, create: bool = False) -> None:
        old = self.read(rel)
        if create and (old is not None or self.path(rel).exists()):
            raise AuthoringError(f"collision at {rel}; select a new ID, do not overwrite")
        self.overlay[rel] = data

    def path(self, rel: str = "") -> ViewPath:
        return ViewPath(self, self.root / rel)


class ViewPath:
    """The narrow pathlib protocol consumed by the two existing validators."""
    def __init__(self, view: View, path: Path):
        self.view, self.path = view, path

    def __fspath__(self): return str(self.path)
    def __str__(self): return str(self.path)
    def __hash__(self): return hash(self.path)
    def __eq__(self, other): return self.path == (other.path if isinstance(other, ViewPath) else other)
    def __lt__(self, other): return str(self) < str(other)
    def __truediv__(self, other): return ViewPath(self.view, self.path / other)
    @property
    def name(self): return self.path.name
    @property
    def parent(self): return ViewPath(self.view, self.path.parent)
    @property
    def parents(self): return tuple(ViewPath(self.view, p) for p in self.path.parents)
    def relative_to(self, other): return self.path.relative_to(os.fspath(other))

    def resolve(self):
        result = self.path.resolve()
        if result != self.view.root:
            safe_path(self.view.root, result.relative_to(self.view.root).as_posix())
        return ViewPath(self.view, result)

    def _rel(self):
        try:
            rel = self.path.relative_to(self.view.root).as_posix()
        except ValueError as exc:
            raise AuthoringError("validator reference escapes repository") from exc
        if rel != ".": safe_path(self.view.root, rel)
        return rel

    def read_text(self, encoding="utf-8"):
        data = self.view.read(self._rel())
        if data is None: raise FileNotFoundError(str(self.path))
        return data.decode(encoding)

    def is_file(self):
        rel = self._rel()
        actual = self.view.baseline.get(rel) is not None if rel in self.view.baseline else self.path.is_file()
        self.view.observed["is_file:" + rel] = actual
        return rel in self.view.overlay or actual

    def is_dir(self):
        rel = self._rel()
        actual = self.path.is_dir() and rel not in self.view.hidden_directories
        self.view.observed["is_dir:" + rel] = actual
        prefix = rel.rstrip("/") + "/"
        virtual = any(k.startswith(prefix) and v is not None for k, v in {**self.view.baseline, **self.view.overlay}.items())
        return actual or virtual

    def exists(self): return self.is_file() or self.is_dir()

    def iterdir(self):
        rel = self._rel()
        children = {p.name for p in self.path.iterdir()} if self.path.is_dir() else set()
        children = {name for name in children if (rel + "/" + name) not in self.view.hidden_directories
                    and not ((rel + "/" + name) in self.view.baseline and self.view.baseline[rel + "/" + name] is None)}
        self.view.observed["children:" + rel] = sorted(children)
        prefix = rel.rstrip("/") + "/"
        for key, data in {**self.view.baseline, **self.view.overlay}.items():
            if data is not None and key.startswith(prefix):
                children.add(key[len(prefix):].split("/")[0])
        return iter(self / name for name in sorted(children))

    def glob(self, pattern):
        if "/" in pattern or "**" in pattern:
            raise AuthoringError("validator requested an unsupported recursive projection; update the view adapter")
        return (p for p in self.iterdir() if p.path.match(pattern))


def load(view: View, path: str, *, writable: bool = False) -> dict:
    raw = view.read(path)
    if raw is None: raise AuthoringError(f"missing {path}")
    text = raw.decode("utf-8")
    if writable and not path.endswith(".json") and re.search(r"(^|\s)#", text):
        raise AuthoringError(f"{path}: comment-like YAML cannot be rewritten losslessly; move comments to prose or use a reviewed manual edit")
    return parse(text, path)


def dump(value: dict, *, json_format: bool = False) -> bytes:
    if json_format:
        return (json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n").encode()
    return yaml.safe_dump(value, allow_unicode=True, sort_keys=False, width=1000).encode()


def template(view: View, path: str) -> dict:
    value = load(view, path)
    value.pop("template_metadata", None)
    if "schema_version" in value and value["schema_version"] != "1.0":
        raise AuthoringError(f"{path}: unsupported artifact schema version; update the family adapter before writing")
    return value


def no_placeholders(value: Any, label: str) -> None:
    if isinstance(value, dict):
        for key, item in value.items(): no_placeholders(item, f"{label}.{key}")
    elif isinstance(value, list):
        for item in value: no_placeholders(item, label)
    elif isinstance(value, str) and re.search(r"<[^>\n]+>", value):
        raise AuthoringError(f"{label}: unresolved template field; this template evolution requires an updated writer")


def md_version(view: View, path: str) -> str:
    text = view.read(path).decode().replace("\r\n", "\n")
    section = text.split("## Template Metadata\n", 1)[-1].split("\n## ", 1)[0]
    matches = re.findall(r"^- `template_version`: `([^`]+)`\s*$", section.replace("\r\n", "\n"), re.M)
    if len(matches) != 1: raise AuthoringError(f"{path}: cannot derive one template version")
    return matches[0]


def metadata_document(title: str, section: str, metadata: dict, body: str) -> bytes:
    for key, value in metadata.items():
        if any(char in str(value) for char in "\r\n`"):
            raise AuthoringError(f"metadata {key}: newlines/backticks are unsupported")
    if re.search(rf"^## {re.escape(section)}\s*$", body, re.M):
        raise AuthoringError(f"body must not contain machine-owned {section} section")
    return (f"# {title}\n\n## {section}\n\n" + "".join(f"- `{key}`: `{value}`\n" for key, value in metadata.items()) + "\n" + body.rstrip() + "\n").encode()


def update_markdown(raw: bytes, section: str, changes: dict) -> bytes:
    text = raw.decode()
    newline = "\r\n" if "\r\n" in text else "\n"
    match = re.search(rf"(?m)^## {re.escape(section)}\r?$", text)
    if not match: raise AuthoringError(f"missing controlled {section} section; reconcile manually before authoring")
    end = re.search(r"(?m)^## ", text[match.end():])
    stop = match.end() + end.start() if end else len(text)
    block = text[match.end():stop]
    for key, value in changes.items():
        if any(char in str(value) for char in "\r\n`"):
            raise AuthoringError(f"metadata {key}: newlines/backticks are unsupported")
        pattern = rf"(?m)^- `{re.escape(key)}`:.*?(\r?\n|$)"
        matches = list(re.finditer(pattern, block))
        if len(matches) != 1: raise AuthoringError(f"metadata {key}: expected exactly one controlled row")
        block = re.sub(pattern, lambda m: f"- `{key}`: `{value}`" + (newline if m.group(1) else ""), block)
    return (text[:match.end()] + block + text[stop:]).encode()


def update_index(view: View, family: str, locator: dict, *, create: bool) -> None:
    rel = f".dev/{family}s/INDEX.MD"
    data = view.read(rel)
    if data is None: raise AuthoringError(f"missing {rel}; initialize repository artifact indexes first")
    text = data.decode()
    newline = "\r\n" if "\r\n" in text else "\n"
    identity = locator[f"{family}_id"]
    title = string(locator["title"], "title")
    if any(c in title for c in "|\r\n`"):
        raise AuthoringError("title cannot contain table separators, backticks or newlines")
    lines = text.splitlines(keepends=True)
    targets = [i for i, line in enumerate(lines) if re.match(rf"^\| \[`{re.escape(identity)}`\]", line)]
    if len(targets) != (0 if create else 1):
        raise AuthoringError(f"{rel}: expected {'no' if create else 'one'} row for {identity}; resolve duplicate/missing row first")
    if family == "workflow":
        row = f"| [`{identity}`]({identity}/workflow.yaml) | {title} | `{locator['owner_skill']}` | `{locator['status']}` | `{locator['updated_at']}` | [plan]({identity}/workflow-plan.md) |" + newline
        section = "Active Post-Adoption Workflows"
    else:
        row = f"| [`{identity}`]({identity}/assessment.yaml) | {title} | `{locator['assessment_type']}` | `{locator['owner_skill']}` | `{locator['status']}` | `{locator['subject_ref']['commit']}` | `{locator['updated_at']}` | [report]({identity}/report.md) |" + newline
        section = {"draft": "Draft Assessments", "final": "Final Assessments"}[locator["status"]]
    current_section = ""
    if targets:
        current_section = next((line[3:].strip() for line in reversed(lines[:targets[0]]) if line.startswith("## ")), "")
    if targets and (family == "workflow" or current_section == section):
        lines[targets[0]] = row
    else:
        if targets: del lines[targets[0]]
        sections = [i for i, line in enumerate(lines) if line.rstrip("\r\n") == f"## {section}"]
        if family == "workflow" and not sections:
            # Workflow policy owns the row, but does not prescribe section titles.
            headers = [i for i, line in enumerate(lines) if line.startswith("| Workflow |")]
            if len(headers) == 1 and headers[0] + 1 < len(lines) and lines[headers[0] + 1].startswith("| ---"):
                lines.insert(headers[0] + 2, row)
                view.put(rel, "".join(lines).encode())
                return
        if len(sections) != 1: raise AuthoringError(f"{rel}: missing/duplicate lifecycle section {section}")
        start = sections[0] + 1
        stop = next((i for i in range(start, len(lines)) if lines[i].startswith("## ")), len(lines))
        separator = next((i for i in range(start, stop) if lines[i].startswith("| ---")), None)
        if separator is None: raise AuthoringError(f"{rel}: missing lifecycle table header")
        lines.insert(separator + 1, row)
    view.put(rel, "".join(lines).encode())


def _identity(value: Any, family: str) -> str:
    value = string(value, "id")
    pattern = r"\d{4}-\d{2}-\d{2}-[a-z0-9][a-z0-9-]*" if family == "workflow" else r"ASM-\d{8}-(?:[0-2][0-9]-[a-z0-9]{3}|\d{3})"
    if not re.fullmatch(pattern, value): raise AuthoringError(f"invalid {family} id")
    return value


def _body(view: View, request: dict) -> str:
    if ("body" in request) == ("body_file" in request):
        raise AuthoringError("supply exactly one body or repository-relative body_file")
    if "body_file" in request:
        raw = view.read(string(request["body_file"], "body_file"))
        if raw is None: raise AuthoringError("body_file does not exist")
        return string(raw.decode(), "body_file contents")
    return string(request["body"], "body")


def _advance(locator: dict, timestamp: str) -> None:
    if instant(timestamp) < instant(locator["updated_at"]):
        raise AuthoringError("timestamp precedes current updated_at; supply a current observation time")
    locator["updated_at"] = timestamp


def _supported(view: View, record: dict, source: str) -> None:
    expected = template(view, source)
    for key in ("template_source", "template_version"):
        if record.get(key) != expected.get(key):
            raise AuthoringError(f"unsupported {key} {record.get(key)!r}; keep original and use its owning reader or explicit future migration")
    if "schema_version" in expected and record.get("schema_version") != expected["schema_version"]:
        raise AuthoringError("unsupported schema_version; migration is not available in P1")
    if source == WORKFLOW_TEMPLATE and record.get("lifecycle_contract") != expected.get("lifecycle_contract"):
        raise AuthoringError("unsupported lifecycle_contract; reconcile through the owning workflow policy")


def _task(view: View, spec: dict, workflow_id: str, timestamp: str, status: str) -> dict:
    fields(spec, {"id", "target", "model", "reasoning_effort"}, {"steps", "validation", "files", "constraints", "non_goals", "finding_ids", "next_action"}, "task")
    task_id = string(spec["id"], "task.id")
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", task_id): raise AuthoringError("unsafe task ID")
    result = template(view, TASK_TEMPLATE)
    result.update(task_id=task_id, workflow_id=workflow_id, status=status, created_at=timestamp, updated_at=timestamp,
                  model=string(spec["model"], "task.model"), reasoning_effort=string(spec["reasoning_effort"], "task.reasoning_effort"))
    result["scope"]["target"] = string(spec["target"], "task.target")
    for key in ("files", "constraints", "non_goals"):
        result["scope"][key] = strings(spec.get(key, []), f"task.{key}")
    result["finding_ids"] = strings(spec.get("finding_ids", []), "task.finding_ids")
    for key in ("steps", "validation"):
        result["execution"][key] = strings(spec.get(key, []), f"task.{key}")
    result["execution"]["next_action"] = string(spec.get("next_action", spec["target"]), "task.next_action")
    no_placeholders(result, "task")
    return result


def _observations(value: Any) -> dict:
    fields(value, {"summary", "finding_status", "tests_run", "files_changed", "residual_risk", "follow_up_needed"}, set(), "observations")
    for key in ("summary", "finding_status"): string(value[key], f"observations.{key}")
    string(value["residual_risk"], "observations.residual_risk", empty=True)
    for key in ("tests_run", "files_changed"): strings(value[key], f"observations.{key}")
    if type(value["follow_up_needed"]) is not bool: raise AuthoringError("observations.follow_up_needed must be boolean")
    return value


def workflow(view: View, request: dict) -> None:
    action = request["operation"].split(".")[1]
    common = {"version", "operation", "id", "timestamp"}
    required, optional = {
        "create": ({"title", "branch", "task"}, {"base_branch", "body", "body_file"}),
        "add-task": ({"task"}, set()),
        "transition": ({"task_id", "status"}, {"observations", "next_action", "next_task_id", "workflow_status", "current_phase"}),
        "update": (set(), {"title", "current_phase"}),
    }[action]
    fields(request, common | required, optional, request["operation"])
    identity = _identity(request["id"], "workflow")
    root = f".dev/workflows/{identity}"
    timestamp = request["timestamp"]
    locator_path, plan_path = f"{root}/workflow.yaml", f"{root}/workflow-plan.md"
    if action == "create":
        if view.path(root).exists(): raise AuthoringError(f"workflow ID collision: {identity}")
        locator = template(view, WORKFLOW_TEMPLATE)
        locator.update(workflow_id=identity, title=string(request["title"], "title"), branch=string(request["branch"], "branch"),
                       base_branch=string(request.get("base_branch", "main"), "base_branch"), artifact_root=root,
                       created_at=timestamp, updated_at=timestamp)
        task = _task(view, request["task"], identity, timestamp, "in_progress")
        view.put(f"{root}/tasks/{task['task_id']}.json", dump(task, json_format=True), create=True)
        metadata = {k: locator[k] for k in ("workflow_id", "workflow_kind", "owner_skill", "branch", "base_branch", "status", "current_phase", "artifact_root", "created_at", "updated_at")}
        metadata.update(branch_segment="1", template_source=PLAN_TEMPLATE, template_version=md_version(view, PLAN_TEMPLATE))
        view.put(plan_path, metadata_document(locator["title"], "Workflow Metadata", metadata, _body(view, request)), create=True)
        no_placeholders(locator, "workflow")
    else:
        locator = load(view, locator_path, writable=True)
        _supported(view, locator, WORKFLOW_TEMPLATE)
        if locator.get("owner_skill") != "ai-context-governance" or locator.get("workflow_kind") != "ai-context-maintenance":
            raise AuthoringError("unsupported workflow owner/profile; use its owning authoring route")
        if locator.get("workflow_id") != identity or locator.get("artifact_root") != root or locator.get("entrypoint") != "workflow-plan.md":
            raise AuthoringError("workflow identity/path differs from supported layout; reconcile manually")
        if locator.get("status") in {"completed", "cancelled"}:
            raise AuthoringError("terminal workflow is immutable in P1; create a successor workflow")
        _advance(locator, timestamp)
        if action == "add-task":
            task = _task(view, request["task"], identity, timestamp, "pending")
            view.put(f"{root}/tasks/{task['task_id']}.json", dump(task, json_format=True), create=True)
        elif action == "transition":
            task_id = string(request["task_id"], "task_id")
            if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", task_id): raise AuthoringError("unsafe task_id")
            task_path = f"{root}/tasks/{task_id}.json"
            task = load(view, task_path)
            _supported(view, task, TASK_TEMPLATE)
            if task.get("task_id") != task_id or task.get("workflow_id") != identity: raise AuthoringError("task identity mismatch")
            status = string(request["status"], "status")
            allowed = {"pending": {"in_progress", "blocked", "deferred", "cancelled"}, "in_progress": {"completed", "blocked", "deferred", "cancelled"}, "blocked": {"in_progress", "deferred", "cancelled"}}
            if status not in allowed.get(task.get("status"), set()): raise AuthoringError(f"unsupported task transition {task.get('status')} -> {status}")
            if status != "in_progress":
                if "observations" not in request: raise AuthoringError("this transition requires caller-supplied observations; no result is inferred")
                task["results"].update(_observations(request["observations"]))
            elif "observations" in request:
                raise AuthoringError("resuming task does not rewrite prior observations")
            _advance(task, timestamp)
            task["status"] = status
            if "next_action" in request: task["execution"]["next_action"] = string(request["next_action"], "next_action", empty=True)
            view.put(task_path, dump(task, json_format=True))
            if "next_task_id" in request:
                next_id = string(request["next_task_id"], "next_task_id")
                if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", next_id) or next_id == task_id: raise AuthoringError("invalid handoff task ID")
                next_path = f"{root}/tasks/{next_id}.json"
                next_task = load(view, next_path)
                _supported(view, next_task, TASK_TEMPLATE)
                if next_task.get("task_id") != next_id or next_task.get("workflow_id") != identity or next_task.get("status") not in {"pending", "blocked"}:
                    raise AuthoringError("handoff target must be a pending/blocked task in this workflow")
                _advance(next_task, timestamp)
                next_task["status"] = "in_progress"
                view.put(next_path, dump(next_task, json_format=True))
            if "workflow_status" in request:
                workflow_status = string(request["workflow_status"], "workflow_status")
                if workflow_status not in {"in_progress", "blocked", "completed"}:
                    raise AuthoringError("workflow.transition supports in_progress, blocked or observed completed; other lifecycle changes need the owning policy")
                locator["status"] = workflow_status
            if "current_phase" in request: locator["current_phase"] = string(request["current_phase"], "current_phase")
        else:
            for key in ("title", "current_phase"):
                if key in request: locator[key] = string(request[key], key)
        if locator["status"] == "completed" and action != "transition":
            raise AuthoringError("complete workflow through an observed task transition with workflow_status and current_phase")
        raw = view.read(plan_path)
        if raw is None: raise AuthoringError("missing workflow-plan.md")
        view.put(plan_path, update_markdown(raw, "Workflow Metadata", {k: locator[k] for k in ("status", "current_phase", "updated_at")}))
    view.put(locator_path, dump(locator), create=action == "create")
    update_index(view, "workflow", locator, create=action == "create")


def assessment(view: View, request: dict) -> None:
    action = request["operation"].split(".")[1]
    common = {"version", "operation", "id", "timestamp"}
    required, optional = {
        "create": ({"title", "type", "artifact_branch", "subject", "included", "next_action"}, {"base_branch", "excluded", "workflow_refs", "related_assessments", "body", "body_file"}),
        "update": (set(), {"title", "next_action", "blockers", "body", "body_file"}),
        "finalize": ({"last_completed_action"}, {"body", "body_file"}),
    }[action]
    fields(request, common | required, optional, request["operation"])
    identity = _identity(request["id"], "assessment")
    root = f".dev/assessments/{identity}"
    locator_path, report_path = f"{root}/assessment.yaml", f"{root}/report.md"
    timestamp = request["timestamp"]
    if action == "create":
        if view.path(root).exists(): raise AuthoringError(f"assessment ID collision: {identity}")
        if string(request["type"], "type") not in {"audit", "verification"}: raise AuthoringError("type must be audit or verification")
        subject = request["subject"]
        fields(subject, {"repository", "branch", "commit"}, set(), "subject")
        for key, val in subject.items(): string(val, f"subject.{key}")
        locator = template(view, ASSESSMENT_TEMPLATE)
        locator.update(assessment_id=identity, commit_search_id=identity, assessment_type="ai-context-" + request["type"],
                       title=string(request["title"], "title"), owner_skill="ai-context-auditor", artifact_branch=string(request["artifact_branch"], "artifact_branch"),
                       base_branch=string(request.get("base_branch", "main"), "base_branch"), created_at=timestamp, updated_at=timestamp,
                       report_template_source=REPORT_TEMPLATE, report_template_version=md_version(view, REPORT_TEMPLATE), subject_ref=subject)
        locator["scope"].update(included=strings(request["included"], "included"), excluded=strings(request.get("excluded", []), "excluded"))
        for key in ("workflow_refs", "related_assessments"): locator["relations"][key] = strings(request.get(key, []), key)
        locator["resume"]["next_action"] = string(request["next_action"], "next_action")
        no_placeholders(locator, "assessment")
        metadata = {k: locator[k] for k in ("assessment_id", "assessment_type", "owner_skill", "status", "created_at", "updated_at")}
        metadata.update(template_source=REPORT_TEMPLATE, template_version=locator["report_template_version"],
                        repository=subject["repository"], subject_branch=subject["branch"], subject_commit=subject["commit"])
        view.put(report_path, metadata_document(locator["title"], "Metadata", metadata, _body(view, request)), create=True)
    else:
        locator = load(view, locator_path, writable=True)
        _supported(view, locator, ASSESSMENT_TEMPLATE)
        if locator.get("assessment_id") != identity or locator.get("commit_search_id") != identity or locator.get("report") != "report.md": raise AuthoringError("assessment identity mismatch")
        if locator.get("owner_skill") != "ai-context-auditor" or locator.get("assessment_type") not in {"ai-context-audit", "ai-context-verification"}:
            raise AuthoringError("unsupported assessment owner/profile")
        if locator.get("report_template_source") != REPORT_TEMPLATE or locator.get("report_template_version") != md_version(view, REPORT_TEMPLATE):
            raise AuthoringError("unsupported report template version; preserve original and use its owning reader")
        if locator.get("status") != "draft": raise AuthoringError("final conclusions are immutable; create a successor or reviewed addendum")
        _advance(locator, timestamp)
        if "title" in request: locator["title"] = string(request["title"], "title")
        for key in ("next_action", "blockers"):
            if key in request: locator["resume"][key] = strings(request[key], key) if key == "blockers" else string(request[key], key)
        raw = view.read(report_path)
        if raw is None: raise AuthoringError("missing report.md")
        if action == "finalize":
            body = _body(view, request)
            if re.search(r"<[^>\n]+>|\b(?:TODO|TBD)\b|draft\s*\|\s*final|healthy\s*\|", body, re.I):
                raise AuthoringError("final report contains template placeholders; supply actual observations and conclusions")
            for heading in ("Executive Summary", "Scope", "Validation"):
                section = re.search(rf"(?ms)^## {heading}\r?\n(.+?)(?=^## |\Z)", body)
                if not section or not re.sub(r"[\s|:*/`-]", "", section.group(1)):
                    raise AuthoringError(f"final report requires caller-authored {heading} content; formatting cannot establish execution")
            locator["status"] = "final"
            locator["resume"].update(last_completed_action=string(request["last_completed_action"], "last_completed_action"), next_action="", blockers=[])
        if "body" in request or "body_file" in request:
            body = _body(view, request)
            if re.search(r"^## Metadata\s*$", body, re.M): raise AuthoringError("body cannot replace machine-owned Metadata")
            match = re.search(r"(?m)^## Metadata\r?$", raw.decode())
            if not match: raise AuthoringError("missing report Metadata section")
            next_section = re.search(r"(?m)^## ", raw.decode()[match.end():])
            if next_section:
                cutoff = match.end() + next_section.start()
            else:
                # A draft may contain plain prose rather than Markdown headings.
                tail = raw.decode()[match.end():]
                metadata_prefix = re.match(r"(?:\r?\n|[ \t]*\r?\n|- `[^`]+`:.*(?:\r?\n|$))*", tail)
                cutoff = match.end() + metadata_prefix.end()
                if cutoff == match.end(): raise AuthoringError("cannot locate existing report metadata/body boundary")
            raw = (raw.decode()[:cutoff] + body.rstrip() + "\n").encode()
        view.put(report_path, update_markdown(raw, "Metadata", {k: locator[k] for k in ("status", "updated_at")}))
    view.put(locator_path, dump(locator), create=action == "create")
    update_index(view, "assessment", locator, create=action == "create")


def _module(name: str):
    path = Path(__file__).with_name(name + ".py")
    spec = importlib.util.spec_from_file_location(name.replace("-", "_"), path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def git(root: Path, *args: str, allowed: tuple[int, ...] = (0,)) -> str:
    result = subprocess.run(["git", *args], cwd=root, capture_output=True, text=True, check=False)
    if result.returncode not in allowed:
        raise AuthoringError(f"Git {' '.join(args[:2])} failed; use a valid repository and resolve Git configuration")
    return f"{result.returncode}:{result.stdout.strip()}"


@dataclass(frozen=True)
class Plan:
    request: dict
    changes: dict[str, tuple[bytes | None, bytes]]
    digest: str

    def diff(self) -> str:
        return "".join("".join(difflib.unified_diff((before or b"").decode().splitlines(keepends=True), after.decode().splitlines(keepends=True), fromfile=("a/" + path if before is not None else "/dev/null"), tofile="b/" + path)) for path, (before, after) in sorted(self.changes.items()))


def plan(root: Path, request: dict, *, _baseline: dict[str, bytes | None] | None = None) -> Plan:
    if root.is_symlink() or (root.exists() and getattr(root.lstat(), "st_file_attributes", 0) & stat.FILE_ATTRIBUTE_REPARSE_POINT):
        raise AuthoringError("repository root must not be a link or junction")
    root = root.resolve()
    if not root.is_dir(): raise AuthoringError("repository root does not exist")
    request = parse(canonical(request).decode(), "request")
    if request.get("version") != "1.0": raise AuthoringError("unsupported request version; catalog describes current writer, no migration is available")
    if string(request.get("operation"), "operation") not in OPERATIONS: raise AuthoringError("unsupported operation; use catalog")
    instant(request.get("timestamp"))
    view = View(root, _baseline)
    family = request["operation"].split(".")[0]
    (workflow if family == "workflow" else assessment)(view, request)
    # Validate the complete projected repository using the unchanged domain rules.
    try:
        errors = _module("validate-workflow-artifacts").validate_workflows(view.path())[0]
        errors += _module("validate-assessment-artifacts").validate_assessments(view.path())[0]
    except (KeyError, TypeError, AttributeError, OSError, ValueError) as exc:
        raise AuthoringError(f"projected validation could not complete: {exc}; reconcile malformed records before authoring") from exc
    if errors: raise AuthoringError("projected validation failed before writes:\n- " + "\n- ".join(errors))
    for rel in (WORKFLOW_TEMPLATE, PLAN_TEMPLATE, TASK_TEMPLATE, ASSESSMENT_TEMPLATE, REPORT_TEMPLATE,
                ".dev/standards/WORKFLOW-ARTIFACT-POLICY.md", ".dev/standards/ASSESSMENT-ARTIFACT-POLICY.md",
                ".ai/scripts/validate-workflow-artifacts.py", ".ai/scripts/validate-assessment-artifacts.py",
                ".ai/scripts/artifact_authoring.py", ".gitignore"):
        view.read(rel)
    changes = {}
    for rel, after in view.overlay.items():
        target = safe_path(root, rel)
        before = _baseline[rel] if _baseline and rel in _baseline else target.read_bytes() if target.is_file() else None
        if before != after: changes[rel] = (before, after)
    if not changes: raise AuthoringError("request has no changes; choose new content or timestamp")
    context = {"head": git(root, "rev-parse", "HEAD"), "branch": git(root, "symbolic-ref", "--quiet", "HEAD", allowed=(0, 1)),
               "ignored": git(root, "check-ignore", "--no-index", "--", *sorted(changes), allowed=(0, 1))}
    if context["ignored"].startswith("0:"): raise AuthoringError("artifact output is ignored; correct the repository policy first")
    binding = {"request": request, "inputs": view.observed, "git": context,
               "runtime": {name: digest(Path(__file__).with_name(name).read_bytes()) for name in
                           ("artifact_authoring.py", "validate-workflow-artifacts.py", "validate-assessment-artifacts.py", "python_prerequisites.py")},
               "changes": {p: [None if before is None else digest(before), digest(after)] for p, (before, after) in changes.items()}}
    return Plan(request, changes, digest(canonical(binding)))


def catalog(root: Path) -> dict:
    view = View(root)
    return {"request_version": "1.0", "operations": sorted(OPERATIONS), "families": {
        "workflow": {"profile": "ai-context-maintenance", "readable": "current templates only", "writable": template(view, WORKFLOW_TEMPLATE)["template_version"], "template_source": WORKFLOW_TEMPLATE},
        "assessment": {"profile": ["ai-context-audit", "ai-context-verification"], "readable": "current templates only", "writable": template(view, ASSESSMENT_TEMPLATE)["template_version"], "template_source": ASSESSMENT_TEMPLATE}},
        "migration": "unsupported: preserve originals and use the owning reader; P1 does not convert evidence",
        "final_assessments": "readable, immutable; create successor or reviewed addendum",
        "yaml_comments": "comment-like YAML is refused before rewriting; Markdown prose and JSON/YAML extension fields are retained",
        "recovery": "explicit rollback of unchanged candidate bytes; no multi-file atomicity"}


def _local(root: Path) -> Path:
    directory = safe_path(root, LOCAL)
    if not git(root, "check-ignore", "-q", "--", LOCAL + "/journal.json", allowed=(0, 1)).startswith("0:"):
        raise AuthoringError(f"recovery directory {LOCAL} must be ignored by Git; configure it explicitly before apply")
    if git(root, "ls-files", "--", LOCAL) != "0:": raise AuthoringError("recovery directory contains tracked files")
    directory.mkdir(parents=True, exist_ok=True)
    return directory


def _exclusive(path: Path, data: bytes) -> None:
    with path.open("xb") as handle:
        handle.write(data)
        handle.flush()
        os.fsync(handle.fileno())


def _write(root: Path, rel: str, expected: bytes | None, data: bytes | None) -> None:
    target = safe_path(root, rel)
    actual = target.read_bytes() if target.is_file() else None
    if actual != expected: raise AuthoringError(f"external modification at {rel}; keep files and inspect recovery journal")
    if data is None:
        target.unlink()
    elif expected is None:
        target.parent.mkdir(parents=True, exist_ok=True)
        safe_path(root, rel)
        _exclusive(target, data)
    else:
        temporary = target.with_name(target.name + ".authoring-tmp")
        safe_path(root, temporary.relative_to(root).as_posix())
        _exclusive(temporary, data)
        try:
            safe_path(root, rel)
            if target.read_bytes() != expected: raise AuthoringError(f"external modification at {rel}; refuse replacement")
            os.replace(temporary, target)
        finally:
            if temporary.exists(): temporary.unlink()


def apply(root: Path, request: dict, expected_digest: str) -> Path:
    """Re-preview under lock. On interruption retain the journal for rollback."""
    if root.is_symlink() or (root.exists() and getattr(root.lstat(), "st_file_attributes", 0) & stat.FILE_ATTRIBUTE_REPARSE_POINT):
        raise AuthoringError("repository root must not be a link or junction")
    root = root.resolve()
    directory = _local(root)
    lock = directory / "writer.lock"
    try: _exclusive(lock, b"artifact-authoring cooperative writer lock\n")
    except FileExistsError as exc: raise AuthoringError("authoring lock exists; verify no writer is running, then recover its journal") from exc
    journal_path = None
    try:
        pending = sorted(directory.glob("*.pending.json"))
        if pending: raise AuthoringError(f"unfinished bundle; recover {pending[0].relative_to(root).as_posix()} before another apply")
        candidate = plan(root, request)
        if candidate.digest != expected_digest: raise AuthoringError("stale preview: repository, request or inputs changed; run preview again")
        journal_path = directory / f"{candidate.digest}.pending.json"
        before = {p: None if old is None else base64.b64encode(old).decode() for p, (old, _) in candidate.changes.items()}
        journal = {"version": "1.0", "request": candidate.request, "preview_digest": candidate.digest, "before": before,
                   "after": {p: digest(new) for p, (_, new) in candidate.changes.items()}}
        journal["journal_sha256"] = digest(canonical(journal))
        _exclusive(journal_path, canonical(journal))
        for rel, (old, new) in sorted(candidate.changes.items()): _write(root, rel, old, new)
        destination = journal_path.with_name(journal_path.name.replace(".pending.json", ".applied.json"))
        if destination.exists(): raise AuthoringError("journal completion collision; retain pending journal")
        journal_path.rename(destination)
        return destination
    except (OSError, AuthoringError) as exc:
        suffix = f"; bundle may be partial: recover --journal {journal_path.relative_to(root).as_posix()}" if journal_path and journal_path.exists() else "; no bundle was started"
        raise AuthoringError(str(exc) + suffix) from exc
    finally:
        lock.unlink()


def recover(root: Path, journal_path: Path) -> None:
    """Rollback a pending bundle after re-deriving every candidate output."""
    if root.is_symlink() or (root.exists() and getattr(root.lstat(), "st_file_attributes", 0) & stat.FILE_ATTRIBUTE_REPARSE_POINT):
        raise AuthoringError("repository root must not be a link or junction")
    root = root.resolve()
    directory = _local(root)
    if not journal_path.is_absolute(): journal_path = root / journal_path
    if journal_path.parent != directory or not re.fullmatch(r"[a-f0-9]{64}\.pending\.json", journal_path.name):
        raise AuthoringError("recovery accepts only a pending journal in the known ignored authoring directory")
    safe_path(root, journal_path.relative_to(root).as_posix())
    # A crash can leave a lock. Never silently remove it; ownership must be checked.
    lock = directory / "writer.lock"
    if lock.exists(): raise AuthoringError("writer lock remains; verify its process has stopped, then remove only writer.lock and retry recovery")
    _exclusive(lock, b"artifact-authoring recovery lock\n")
    try:
        journal = parse(journal_path.read_text(encoding="utf-8"), "journal")
        fields(journal, {"version", "request", "preview_digest", "before", "after", "journal_sha256"}, set(), "journal")
        journal_digest = journal.pop("journal_sha256")
        if journal_digest != digest(canonical(journal)):
            raise AuthoringError("journal content digest mismatch; preserve files and investigate")
        if journal["version"] != "1.0" or journal["preview_digest"] + ".pending.json" != journal_path.name: raise AuthoringError("journal identity/version mismatch")
        if type(journal["before"]) is not dict or type(journal["after"]) is not dict: raise AuthoringError("invalid journal change maps")
        before = {}
        for rel, encoded in journal["before"].items():
            safe_path(root, rel)
            try: before[rel] = None if encoded is None else base64.b64decode(encoded, validate=True)
            except (ValueError, TypeError) as exc: raise AuthoringError("invalid journal before bytes") from exc
        if journal["request"].get("operation", "").endswith(".create"):
            family = journal["request"]["operation"].split(".")[0]
            identity = _identity(journal["request"].get("id"), family)
            artifact_root = safe_path(root, f".dev/{family}s/{identity}")
            for existing in artifact_root.rglob("*") if artifact_root.exists() else []:
                rel = existing.relative_to(root).as_posix()
                safe_path(root, rel)
                if existing.is_file() and (rel not in before or before[rel] is not None):
                    raise AuthoringError(f"external file in partially created bundle: {rel}; recovery refuses directory removal")
        # Candidate paths and bytes come from the restricted operation, not journal outputs.
        candidate = plan(root, journal["request"], _baseline=before)
        if set(candidate.changes) != set(before) or journal["after"] != {p: digest(new) for p, (_, new) in candidate.changes.items()}:
            raise AuthoringError("journal does not match the re-derived restricted operation; preserve files and investigate")
        for rel, (old, new) in candidate.changes.items():
            target = safe_path(root, rel)
            actual = target.read_bytes() if target.is_file() else None
            if actual not in (old, new): raise AuthoringError(f"external modification at {rel}; recovery refuses to overwrite it")
        for rel, (old, new) in reversed(sorted(candidate.changes.items())):
            target = safe_path(root, rel)
            if (target.read_bytes() if target.is_file() else None) == new: _write(root, rel, new, old)
        # Remove only empty directories created by this bundle, never existing trees.
        for rel, (old, _) in reversed(sorted(candidate.changes.items())):
            if old is None:
                target = safe_path(root, rel).parent
                while target != root and target.name not in {"workflows", "assessments"}:
                    try: target.rmdir()
                    except OSError: break
                    target = target.parent
        journal_path.rename(journal_path.with_name(journal_path.name.replace(".pending.json", ".recovered.json")))
    finally:
        lock.unlink()
