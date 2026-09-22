"""Restricted document authoring over existing family validators.

Preview is read-only. Apply re-derives a preview, then writes a recoverable bundle
under an exclusive cooperative lock. Individual replacements are atomic; the
bundle is NOT a filesystem transaction. Recovery only rolls back unchanged
candidate bytes and never accepts caller-supplied output paths as authority.
"""
from __future__ import annotations

import base64
import difflib
import importlib.util
import io
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
import artifact_core as CORE

WORKFLOW_TEMPLATE = ".ai/assets/skills/ai-context-governance/templates/workflow-locator-template.yaml"
PLAN_TEMPLATE = ".ai/assets/skills/ai-context-governance/templates/ai-context-maintenance-workflow-plan-template.md"
TASK_TEMPLATE = ".ai/assets/skills/ai-context-governance/templates/ai-context-remediation-task-template.json"
ASSESSMENT_TEMPLATE = ".dev/assessments/templates/assessment-locator-template.yaml"
REPORT_TEMPLATE = ".ai/assets/skills/ai-context-auditor/templates/ai-context-audit-report-template.md"
REMEDIATION_TEMPLATE = ".ai/assets/skills/ai-context-governance/templates/ai-context-remediation-report-template.md"
LOCAL = ".dev/ai-context/local/artifact-authoring"
OPERATIONS = {
    "workflow.create", "workflow.add-task", "workflow.transition", "workflow.update", "workflow.progress", "workflow.report",
    "assessment.create", "assessment.update", "assessment.finalize",
    "role.update", "role.migrate",
    "catalog.update", "target.technology", "target.work-binding",
    "lifecycle.update",
    "skill.update",
}
ROLE_AUTHORITY = (
    ".ai/assets/CANONICAL-SCHEMA.MD",
    ".ai/assets/templates/sub-agent-role-prompt-template.yaml",
    ".ai/assets/shared/ROLE-EXECUTION-CONTRACT.md",
)
ROLE_RUNTIME = ("validate-ai-context.py", "ai_context_cli_routing.py")
ROLE_EDITABLE = {"title", "purpose", "triggers", "inputs", "outputs", "constraints", "references", "examples"}
CATALOGS = {
    "provider-neutral-capabilities": (".ai/assets/shared/provider-neutral-capability-registry.yaml", "capabilities", "role_asset_id", {"capability_tags"}),
    "provider-projections": (".ai/assets/shared/provider-projection-registry.yaml", "provider_projections", None, {"deferred_reason"}),
    "upgrader-role-bindings": (".ai/assets/skills/ai-context-upgrader/references/role-execution-bindings.yaml", "role_bindings", "role_asset_id", {"stop_and_escalation"}),
    "evaluation-corpus": (".ai/evaluation/corpus-manifest.yaml", "cases", "case_id", {"input", "expected"}),
    "evaluation-mutants": (".ai/evaluation/incident-mutants.yaml", "mutants", "mutant_id", {"follow_up"}),
    "source-dispositions": (".ai/distribution/source-dispositions.yaml", "dispositions", "id", {"patterns", "reason"}),
    "source-identities": (".ai/distribution/identity-registry.yaml", "identity_records", "id", {"display_name"}),
    "identity-consumers": (".ai/distribution/identity-registry.yaml", "consumer_contracts", "id", {"path", "selector"}),
    "governance-terms": (".dev/standards/AI-CONTEXT-OWNERSHIP.yaml", "governance_term_routing.terms", "term_id", {"qualified_term", "owner_anchor", "contextual_shorthand"}),
    "rule-consumers": (".dev/standards/AI-CONTEXT-OWNERSHIP.yaml", "rules", "rule_id", {"derived_consumers"}),
    "validation-gate-groups": (".ai/assets/shared/validation-gate-classification.yaml", "groups", "group_id", {"reason"}),
    "validation-external-gates": (".ai/assets/shared/validation-gate-classification.yaml", "external_fresh_gates", "gate_id", {"reason"}),
    "shell-assets": (".ai/scripts/shell-assets.yaml", "assets", "path", {"lifecycle", "replacement"}),
}
CATALOG_VERSIONS = {key: "1.1" if key in {"source-identities", "identity-consumers"} else "1.0" for key in CATALOGS}
CATALOG_VERSIONS["shell-assets"] = "2.0"
for _classification_catalog in ("validation-gate-groups", "validation-external-gates"):
    CATALOG_VERSIONS[_classification_catalog] = "validation-gate-classification/v1"
CATALOG_RUNTIME = {
    "source-dispositions": ("validate-source-dispositions.py", "ai_context_package.py", "runtime_skill_entries.py", "ai_context_package_identity.py", "ai_context_release_projection.py"),
    "source-identities": ("validate-repository-identity.py", "ai_context_package_identity.py"),
    "identity-consumers": ("validate-repository-identity.py", "ai_context_package_identity.py"),
    "shell-assets": ("validate-shell-assets.py",),
    "validation-gate-groups": ("validation_subject.py", "validation-profile-registry.sh"),
    "validation-external-gates": ("validation_subject.py", "validation-profile-registry.sh"),
}
TARGET_SCHEMAS = tuple(".ai/assets/skills/ai-context-init/templates/" + name + ".schema.yaml" for name in ("technology-selection", "work-item-binding"))


class AuthoringError(ValueError):
    """Actionable input, stale-preview, or recovery refusal."""


def digest(value: bytes) -> str:
    return CORE.sha256(value)


def canonical(value: Any) -> bytes:
    return CORE.canonical_json(value)


class _StrictLoader(yaml.SafeLoader):
    pass


def _mapping(loader: _StrictLoader, node: yaml.MappingNode) -> dict:
    return CORE.construct_unique_mapping(loader, node, flatten=False,
        key_error=lambda key, duplicate: AuthoringError(f"mapping keys must be unique strings; duplicate/invalid key {key!r}"))


_StrictLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _mapping)


def parse(text: str, label: str = "input", *, refuse_yaml_comments: bool = False) -> dict:
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
            for token in CORE.yaml_tokens(text, refuse_comments=refuse_yaml_comments):
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
    def suffix(self): return self.path.suffix
    @property
    def parent(self): return ViewPath(self.view, self.path.parent)
    @property
    def parents(self): return tuple(ViewPath(self.view, p) for p in self.path.parents)
    def relative_to(self, other): return self.path.relative_to(os.fspath(other))

    def resolve(self):
        self._rel()  # Inspect original components before resolve can hide links.
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
        return self.read_bytes().decode(encoding).replace("\r\n", "\n").replace("\r", "\n")

    def read_bytes(self):
        data = self.view.read(self._rel())
        if data is None: raise FileNotFoundError(str(self.path))
        return data

    def open(self, mode="rb"):
        if mode != "rb": raise AuthoringError("projected streams support only read-only binary access")
        return io.BytesIO(self.read_bytes())

    def is_file(self):
        rel = self._rel()
        actual = self.view.baseline.get(rel) is not None if rel in self.view.baseline else self.path.is_file()
        self.view.observed["is_file:" + rel] = actual
        return rel in self.view.overlay or actual

    def is_dir(self):
        rel = self._rel()
        actual = self.path.is_dir() and rel not in self.view.hidden_directories
        self.view.observed["is_dir:" + rel] = actual
        prefix = "" if rel == "." else rel.rstrip("/") + "/"
        virtual = any(k.startswith(prefix) and v is not None for k, v in {**self.view.baseline, **self.view.overlay}.items())
        return actual or virtual

    def exists(self): return self.is_file() or self.is_dir()

    def iterdir(self):
        rel = self._rel()
        children = {p.name for p in self.path.iterdir()} if self.path.is_dir() else set()
        children = {name for name in children if (rel + "/" + name) not in self.view.hidden_directories
                    and not ((rel + "/" + name) in self.view.baseline and self.view.baseline[rel + "/" + name] is None)}
        self.view.observed["children:" + rel] = sorted(children)
        prefix = "" if rel == "." else rel.rstrip("/") + "/"
        for key, data in {**self.view.baseline, **self.view.overlay}.items():
            if data is not None and key.startswith(prefix):
                children.add(key[len(prefix):].split("/")[0])
        return iter(self / name for name in sorted(children))

    def glob(self, pattern):
        if not pattern or "\\" in pattern or "**" in pattern or any(p in {"", ".", ".."} for p in pattern.split("/")):
            raise AuthoringError("unsupported projected glob pattern")
        first, _, rest = pattern.partition("/")
        if not any(token in first for token in "*?["):
            child = self / first
            children = (child,) if child.exists() else ()
        else:
            children = self.iterdir() if self.is_dir() else ()
        for child in children:
            if child.path.match(first):
                if not rest: yield child
                elif child.is_dir(): yield from child.glob(rest)

    def rglob(self, pattern):
        if "/" in pattern or "\\" in pattern or pattern in {"", ".", ".."} or "**" in pattern:
            raise AuthoringError("unsupported projected recursive pattern")
        for child in self.iterdir() if self.is_dir() else ():
            if child.path.match(pattern): yield child
            if child.is_dir(): yield from child.rglob(pattern)


def load(view: View, path: str, *, writable: bool = False) -> dict:
    raw = view.read(path)
    if raw is None: raise AuthoringError(f"missing {path}")
    text = raw.decode("utf-8")
    return parse(text, path, refuse_yaml_comments=writable and not path.endswith(".json"))


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
    if instant(timestamp) <= instant(locator["updated_at"]):
        raise AuthoringError("timestamp must advance beyond current updated_at; supply a later observation time")
    locator["updated_at"] = timestamp


def automatic_timestamp() -> str:
    """Capture real local time once; preview/apply/recovery retain this instant."""
    return datetime.now().astimezone().isoformat(timespec="microseconds")


def markdown_section(raw: bytes, heading: str) -> tuple[str, int, int]:
    text = raw.decode()
    matches = list(re.finditer(rf"(?m)^## {re.escape(heading)}\r?$", text))
    if len(matches) != 1:
        raise AuthoringError(f"expected exactly one {heading} section")
    match = matches[0]
    following = re.search(r"(?m)^## ", text[match.end():])
    stop = match.end() + following.start() if following else len(text)
    return text, match.end(), stop


def replace_body(raw: bytes, section: str, body: str) -> bytes:
    if re.search(rf"(?m)^## {re.escape(section)}\s*$", body):
        raise AuthoringError(f"body cannot replace machine-owned {section}")
    text, start, stop = markdown_section(raw, section)
    prefix = re.match(r"(?:\r?\n|[ \t]*\r?\n|- `[^`]+`:.*(?:\r?\n|$))*", text[start:stop])
    return (text[:start + prefix.end()] + body.rstrip() + "\n").encode()


def _report_metadata(raw: bytes) -> dict:
    text, start, stop = markdown_section(raw, "Report Metadata")
    rows = re.findall(r"(?m)^- `([^`]+)`: `([^`\r\n]*)`\r?$", text[start:stop])
    if len(rows) != len({key for key, _ in rows}):
        raise AuthoringError("duplicate report metadata")
    result = dict(rows)
    fields(result, {"report_id", "workflow_id", "owner_skill", "status", "created_at", "updated_at",
                    "template_source", "template_version", "baseline_assessment", "verification_assessment"}, set(), "report metadata")
    # Refuse unrecognized metadata prose instead of silently discarding it.
    remainder = re.sub(r"(?m)^- `[^`]+`: `[^`\r\n]*`\r?$", "", text[start:stop])
    if remainder.strip(): raise AuthoringError("unsupported report metadata content")
    return result


def _assessment_reference(view: View, identity: str, workflow_id: str, *, verification: bool, baseline: str = "") -> None:
    _identity(identity, "assessment")
    root = f".dev/assessments/{identity}"
    record = load(view, root + "/assessment.yaml")
    if (record.get("assessment_id") != identity or record.get("owner_skill") != "ai-context-auditor"
            or record.get("assessment_type") not in {"ai-context-audit", "ai-context-verification"}
            or record.get("status") != "final" or record.get("report") != "report.md"
            or view.read(root + "/report.md") is None):
        raise AuthoringError("report reference must identify an existing final independent assessment")
    if verification and (record.get("assessment_type") != "ai-context-verification"
                         or workflow_id not in record.get("relations", {}).get("workflow_refs", [])
                         or baseline not in record.get("relations", {}).get("related_assessments", [])):
        raise AuthoringError("verification assessment must be a verification linked to this workflow and baseline")


def _state_projection(view: View, locator: dict) -> str:
    """Project current recorded facts, never infer a test/review/provider outcome."""
    def cell(value):
        return str(value).replace("&", "&amp;").replace("<", "&lt;").replace("|", "&#124;").replace("`", "&#96;").replace("\r", "").replace("\n", "<br>")
    rows = ["## Current Workflow State\n\n",
            "<!-- artifact-authoring: workflow-state/v1; generated from workflow.yaml and tasks -->\n",
            f"- Workflow status: `{locator['status']}`\n- Current phase: {cell(locator['current_phase'])}\n\n",
            "| Task | Status | Last completed step | Next action |\n| --- | --- | --- | --- |\n"]
    for path in sorted(view.path(locator["artifact_root"] + "/tasks").glob("*.json")):
        task = load(view, path.relative_to(view.root).as_posix())
        if task.get("workflow_id") != locator["workflow_id"]:
            raise AuthoringError("current-state task belongs to another workflow")
        execution = task["execution"]
        for key in ("last_completed_step", "next_action"): string(execution[key], f"task.execution.{key}", empty=True)
        rows.append("| " + " | ".join(cell(value) for value in (task["task_id"], task["status"],
                    execution["last_completed_step"], execution["next_action"])) + " |\n")
    rows.append("\nRecorded workflow state is not independent verification, current-head CI admission, or provider closure.\n")
    return "".join(rows)


def _replace_state(raw: bytes, projection: str) -> bytes:
    text = raw.decode()
    if re.search(r"(?m)^## Current Workflow State\r?$", text):
        text, _, stop = markdown_section(raw, "Current Workflow State")
        start = re.search(r"(?m)^## Current Workflow State\r?$", text).start()
        block = text[start:stop]
        if "<!-- artifact-authoring: workflow-state/v1; generated from workflow.yaml and tasks -->" not in block:
            raise AuthoringError("unmanaged Current Workflow State section; move author prose before adopting projection")
        return ((text[:start] + projection.rstrip() + "\n\n" + text[stop:]).rstrip() + "\n").encode()
    return (text.rstrip() + "\n\n" + projection).encode()


def remediation_report(view: View, locator: dict, request: dict) -> None:
    """Create/adopt/update only the governance-owned remediation report."""
    root = locator["artifact_root"]
    path = root + "/reports/remediation-report.md"
    raw = view.read(path)
    timestamp = request["timestamp"]
    if raw is None:
        if "baseline_assessment" not in request: raise AuthoringError("new report requires baseline_assessment")
        metadata = dict(report_id="remediation-report-" + locator["workflow_id"], workflow_id=locator["workflow_id"],
                        owner_skill="ai-context-governance", status="draft", created_at=timestamp, updated_at=timestamp,
                        template_source=REMEDIATION_TEMPLATE, template_version=md_version(view, REMEDIATION_TEMPLATE),
                        baseline_assessment=request["baseline_assessment"], verification_assessment="pending")
        body = _body(view, request)
        if re.search(r"(?m)^## Current Workflow State\s*$", body):
            raise AuthoringError("body cannot replace generated Current Workflow State")
        title = string(request.get("title", locator["title"]), "title")
        if any(c in title for c in "\r\n`"): raise AuthoringError("report title must be a single line without backticks")
        raw = metadata_document(title, "Report Metadata", metadata, body)
    else:
        metadata = _report_metadata(raw)
        expected = {"report_id": "remediation-report-" + locator["workflow_id"], "workflow_id": locator["workflow_id"],
                    "owner_skill": "ai-context-governance", "template_source": REMEDIATION_TEMPLATE,
                    "template_version": md_version(view, REMEDIATION_TEMPLATE)}
        if any(metadata[key] != value for key, value in expected.items()) or metadata["status"] != "draft":
            raise AuthoringError("unsupported report identity/version or immutable final report")
        if instant(metadata["created_at"]) > instant(metadata["updated_at"]): raise AuthoringError("invalid report chronology")
        _advance(metadata, timestamp)
        if "baseline_assessment" in request and request["baseline_assessment"] != metadata["baseline_assessment"]:
            raise AuthoringError("baseline assessment is immutable; create a successor for a new baseline")
        if "title" in request: raise AuthoringError("existing report title is preserved")
        if "body" in request or "body_file" in request:
            body = _body(view, request)
            if re.search(r"(?m)^## Current Workflow State\s*$", body):
                raise AuthoringError("body cannot replace generated Current Workflow State")
            raw = replace_body(raw, "Report Metadata", body)
    if "verification_assessment" in request:
        metadata["verification_assessment"] = string(request["verification_assessment"], "verification_assessment")
    _assessment_reference(view, metadata["baseline_assessment"], locator["workflow_id"], verification=False)
    if metadata["verification_assessment"] != "pending":
        _assessment_reference(view, metadata["verification_assessment"], locator["workflow_id"], verification=True, baseline=metadata["baseline_assessment"])
    if locator["status"] == "completed":
        if metadata["verification_assessment"] == "pending":
            raise AuthoringError("completed workflow report requires an existing final verification assessment")
        metadata["status"] = "final"
    raw = update_markdown(raw, "Report Metadata", metadata)
    view.put(path, _replace_state(raw, _state_projection(view, locator)))


def validate_workflow_report(root, locator: dict) -> list[str]:
    """Read-only opt-in consistency check shared with the workflow validator."""
    if "remediation_report" not in locator: return []
    try:
        if (locator.get("owner_skill") != "ai-context-governance" or locator.get("workflow_kind") != "ai-context-maintenance"
                or locator.get("artifact_root") != ".dev/workflows/" + _identity(locator.get("workflow_id"), "workflow")):
            raise AuthoringError("unsupported remediation workflow owner/layout")
        if locator["remediation_report"] != {"contract": "1.0", "path": "reports/remediation-report.md"}:
            raise AuthoringError("unsupported remediation report binding")
        view = root.view if isinstance(root, ViewPath) else View(Path(root))
        raw = view.read(locator["artifact_root"] + "/reports/remediation-report.md")
        if raw is None: raise AuthoringError("missing bound remediation report")
        metadata = _report_metadata(raw)
        expected = {"report_id": "remediation-report-" + locator["workflow_id"], "workflow_id": locator["workflow_id"],
                    "owner_skill": "ai-context-governance", "template_source": REMEDIATION_TEMPLATE,
                    "template_version": md_version(view, REMEDIATION_TEMPLATE), "updated_at": locator["updated_at"],
                    "status": "final" if locator["status"] == "completed" else "draft"}
        if any(metadata[key] != value for key, value in expected.items()):
            raise AuthoringError("report metadata differs from workflow projection")
        if instant(metadata["created_at"]) > instant(metadata["updated_at"]): raise AuthoringError("invalid report chronology")
        _assessment_reference(view, metadata["baseline_assessment"], locator["workflow_id"], verification=False)
        verification = metadata["verification_assessment"]
        if verification != "pending":
            _assessment_reference(view, verification, locator["workflow_id"], verification=True, baseline=metadata["baseline_assessment"])
        elif metadata["status"] == "final": raise AuthoringError("final report lacks verification reference")
        projection = _state_projection(view, locator)
        for path in (locator["artifact_root"] + "/reports/remediation-report.md", locator["artifact_root"] + "/workflow-plan.md"):
            document = view.read(path)
            text, start, stop = markdown_section(document, "Current Workflow State")
            if text[start:stop].strip() != projection.split("\n", 1)[1].strip():
                raise AuthoringError(f"stale generated current state in {path}")
    except (ValueError, TypeError, KeyError, AttributeError, OSError) as exc:
        return [f"{locator.get('workflow_id', 'workflow')}: {exc}"]
    return []


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
        "update": (set(), {"title", "current_phase", "body", "body_file"}),
        "progress": ({"task_id", "last_completed_step", "next_action"}, {"observations", "current_phase"}),
        "report": (set(), {"title", "body", "body_file", "baseline_assessment", "verification_assessment"}),
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
        elif action == "progress":
            task_id = string(request["task_id"], "task_id")
            if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", task_id): raise AuthoringError("unsafe task_id")
            task_path = f"{root}/tasks/{task_id}.json"
            task = load(view, task_path)
            _supported(view, task, TASK_TEMPLATE)
            if (task.get("task_id") != task_id or task.get("workflow_id") != identity
                    or task.get("status") not in {"in_progress", "blocked"}):
                raise AuthoringError("progress requires an active or blocked task in this workflow")
            _advance(task, timestamp)
            for key in ("last_completed_step", "next_action"):
                task["execution"][key] = string(request[key], key, empty=True)
            if "observations" in request: task["results"].update(_observations(request["observations"]))
            if "current_phase" in request: locator["current_phase"] = string(request["current_phase"], "current_phase")
            view.put(task_path, dump(task, json_format=True))
        elif action == "report":
            if "remediation_report" in locator and locator["remediation_report"] != {"contract": "1.0", "path": "reports/remediation-report.md"}:
                raise AuthoringError("unsupported remediation report binding")
            locator["remediation_report"] = {"contract": "1.0", "path": "reports/remediation-report.md"}
        else:
            for key in ("title", "current_phase"):
                if key in request: locator[key] = string(request[key], key)
        if locator["status"] == "completed" and action != "transition":
            raise AuthoringError("complete workflow through an observed task transition with workflow_status and current_phase")
        raw = view.read(plan_path)
        if raw is None: raise AuthoringError("missing workflow-plan.md")
        if action == "update" and ("body" in request or "body_file" in request):
            body = _body(view, request)
            if re.search(r"(?m)^## Current Workflow State\s*$", body): raise AuthoringError("body cannot replace generated Current Workflow State")
            raw = replace_body(raw, "Workflow Metadata", body)
        view.put(plan_path, update_markdown(raw, "Workflow Metadata", {k: locator[k] for k in ("status", "current_phase", "updated_at")}))
    if "remediation_report" in locator:
        if locator["remediation_report"] != {"contract": "1.0", "path": "reports/remediation-report.md"}:
            raise AuthoringError("unsupported remediation report binding")
        remediation_report(view, locator, request if action == "report" else {"timestamp": timestamp})
        view.put(plan_path, _replace_state(view.read(plan_path), _state_projection(view, locator)))
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


def role(view: View, request: dict) -> None:
    """Update dynamic roles or convert the explicitly supported historical edge.

    Paths are discovered from canonical layouts. Neither a request nor a journal
    can select an arbitrary output, owner binding or runtime disposition.
    """
    action = request["operation"].split(".")[1]
    fields(request, {"version", "operation", "timestamp", "id"} | ({"changes"} if action == "update" else {"from_version", "to_version"}),
           set(), "role request")
    identity = string(request["id"], "id")
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", identity):
        raise AuthoringError("role id must be canonical kebab-case")
    for ref in ROLE_AUTHORITY:
        if view.read(ref) is None: raise AuthoringError(f"missing role authority: {ref}")
    validator = _module("validate-ai-context")
    if validator.ASSET_SCHEMA_VERSIONS["sub-agent.yaml"] != "1.1":
        raise AuthoringError("canonical role version changed; update the family adapter")

    def manifests(directory: str, filename: str):
        base = view.path(directory)
        if base.is_dir():
            for child in base.iterdir():
                if child.is_dir() and (child / filename).is_file():
                    yield (child / filename).relative_to(view.root).as_posix()

    skill_paths = list(manifests(".ai/assets/skills", "skill.yaml"))
    role_paths = list(manifests(".ai/assets/sub-agent-role-prompts", "sub-agent.yaml"))
    # Private role discovery does not depend on the owning skill being valid.
    skill_root = view.path(".ai/assets/skills")
    if skill_root.is_dir():
        for child in skill_root.iterdir():
            if child.is_dir():
                role_paths.extend(manifests(child.relative_to(view.root).as_posix() + "/roles", "sub-agent.yaml"))
    records = {ref: load(view, ref) for ref in skill_paths + role_paths}
    matches = [ref for ref in role_paths if records[ref].get("asset_id") == identity]
    if len(matches) != 1: raise AuthoringError("role identity must resolve to exactly one canonical manifest")
    target = matches[0]
    data = load(view, target, writable=True)
    if data.get("wrapper_targets") != [] or data.get("adapter_metadata", {}) != {}:
        raise AuthoringError("runtime adapter reconciliation required; this writer only supports dynamic roles")
    if action == "update":
        if data.get("schema_version") != "1.1":
            raise AuthoringError("role.update requires current 1.1; use the declared migration edge for legacy input")
        changes = request["changes"]
        fields(changes, set(), ROLE_EDITABLE, "role changes")
        if not changes: raise AuthoringError("role changes must not be empty")
        for key, value in changes.items():
            data[key] = string(value, key) if key in {"title", "purpose"} else strings(value, key)
    else:
        if request["from_version"] != "1.0" or request.get("to_version") != "1.1" or data.get("schema_version") != "1.0":
            raise AuthoringError("only explicit role migration 1.0 -> 1.1 is supported; preserve original and reconcile other versions")
        data["schema_version"] = "1.1"
        data["adapter_metadata"] = {}
    view.put(target, dump(data))
    records[target] = data
    errors: list[str] = []
    seen: set[str] = set()
    # Reuse canonical shape/identity/reference checks and owner relationships.
    # Runtime wrappers of unmodified contextual manifests are outside this gate.
    for ref, record in records.items():
        validator.validate_canonical_manifest(Path(ref), record, errors, root=view.path(), seen=seen)
    validator.validate_sub_agent_adapter_metadata(Path(target), data, errors, root=view.path())
    validator.validate_role_relationships(
        [(Path(ref), records[ref]) for ref in skill_paths],
        {ref: records[ref] for ref in role_paths},
        view.path(".ai/SUB-AGENT-SYSTEM.MD"), errors,
    )
    if errors: raise AuthoringError("projected role validation failed before writes:\n- " + "\n- ".join(errors))


def skill_update(view: View, request: dict) -> None:
    fields(request, {"version", "operation", "timestamp", "id", "changes"}, set(), "skill request")
    identity = string(request["id"], "id")
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", identity): raise AuthoringError("skill id must be canonical kebab-case")
    ref = f".ai/assets/skills/{identity}/skill.yaml"
    data = load(view, ref, writable=True)
    if data.get("schema_version") != "1.0" or data.get("asset_id") != identity or data.get("asset_type") != "skill-spec":
        raise AuthoringError("skill.update requires existing current canonical skill identity")
    projection = _module("runtime_skill_entries")
    generated = identity in projection.SELECTED_SKILLS
    editable = {"inputs", "outputs", "constraints", "triggers", "handoff_rules", "runtime_notes"}
    if generated: editable |= {"title", "purpose"}
    fields(request["changes"], set(), editable, "skill changes")
    if not request["changes"]: raise AuthoringError("skill changes must not be empty")
    for name, value in request["changes"].items():
        data[name] = string(value, name) if name in {"title", "purpose"} else strings(value, name)
    for authority in (ROLE_AUTHORITY[0], ".ai/assets/templates/skill-template.yaml", ".ai/assets/skills/README.MD"):
        if view.read(authority) is None: raise AuthoringError(f"missing skill authority {authority}")
    validator = _module("validate-ai-context")
    errors: list[str] = []
    # Validate existing projections before regeneration so an update never hides
    # an unrelated pre-existing wrapper defect.
    original = load(view, ref)
    validator.validate_wrapper_metadata(Path(ref), original, errors, root=view.path())
    validator.validate_skill_wrapper_semantics(Path(ref), original, errors, root=view.path())
    if generated:
        original_raw = view.read(ref)
        expected = projection.render_entry(original, original_raw)
        for target in ("codex", "claude"):
            wrapper = projection.wrapper_path(identity, target).as_posix()
            if projection.normalize_git_text_bytes(view.read(wrapper)) != expected.encode(): errors.append(f"existing generated wrapper differs: {wrapper}")
    if errors: raise AuthoringError("existing skill projection invalid:\n- " + "\n- ".join(errors))
    view.put(ref, dump(data))
    if generated:
        selected, raw = projection.load_skill(view.path(), identity)
        rendered = projection.render_entry(selected, raw).encode()
        for target in ("codex", "claude"):
            view.put(projection.wrapper_path(identity, target).as_posix(), rendered)
    validator.validate_canonical_manifest(Path(ref), data, errors, root=view.path())
    validator.validate_wrapper_metadata(Path(ref), data, errors, root=view.path())
    validator.validate_skill_wrapper_semantics(Path(ref), data, errors, root=view.path())
    if errors: raise AuthoringError("projected skill validation failed before writes:\n- " + "\n- ".join(errors))


def catalog_update(view: View, request: dict) -> None:
    """Update an existing semantic record, never an arbitrary caller path."""
    fields(request, {"version", "operation", "timestamp", "id", "record", "changes"}, set(), "catalog request")
    identity = string(request["id"], "id")
    if identity not in CATALOGS: raise AuthoringError("unsupported catalog; use catalog to inspect bounded operations")
    ref, collection, key, editable = CATALOGS[identity]
    record_id = string(request["record"], "record")
    changes = request["changes"]
    fields(changes, set(), editable, "catalog changes")
    if not changes: raise AuthoringError("catalog changes must not be empty")
    data = load(view, ref, writable=True)
    expected_version = CATALOG_VERSIONS[identity]
    if data.get("schema_version") != expected_version: raise AuthoringError(f"catalog requires current {expected_version}; no historical conversion is supported")
    records = data
    for part in collection.split("."):
        records = records.get(part) if type(records) is dict else None
    if key is None:
        if type(records) is not dict or record_id not in records: raise AuthoringError("catalog record does not exist")
        selected = records[record_id]
    else:
        if type(records) is not list: raise AuthoringError("catalog collection must be a list")
        matches = [row for row in records if type(row) is dict and row.get(key) == record_id]
        if len(matches) != 1: raise AuthoringError("catalog record must resolve exactly once")
        selected = matches[0]
    if type(selected) is not dict: raise AuthoringError("catalog record must be a mapping")
    if identity == "identity-consumers":
        if selected.get("kind") not in {"yaml-value", "text-contains"} or ("selector" in changes and selected.get("kind") != "yaml-value"):
            raise AuthoringError("only existing yaml-value/text-contains consumer references are writable")
    for name, value in changes.items():
        if identity == "governance-terms" and name == "owner_anchor":
            selected["canonical_owner"]["anchor"] = string(value, name)
        elif identity == "governance-terms" and name == "contextual_shorthand":
            fields(value, {"aliases", "allowed_scope", "forbidden_authority_claims"}, set(), name)
            for field in ("aliases", "forbidden_authority_claims"): strings(value[field], field)
            string(value["allowed_scope"], "allowed_scope")
            selected[name].update(value)
        elif identity == "shell-assets" and name == "replacement" and value is None:
            selected[name] = None
        else:
            selected[name] = strings(value, name) if name in {"capability_tags", "stop_and_escalation", "patterns", "derived_consumers"} else string(value, name)
    if identity == "rule-consumers":
        _advance(data, request["timestamp"])
        resolved_consumers: set[str] = set()
        for consumer in selected["derived_consumers"]:
            path = safe_path(view.root, consumer)
            canonical_path = os.path.normcase(str(path.resolve()))
            if canonical_path in resolved_consumers:
                raise AuthoringError("derived consumers must resolve to unique files")
            resolved_consumers.add(canonical_path)
            content = view.read(consumer)
            if content is None:
                raise AuthoringError(f"missing derived consumer: {consumer}")
            if not re.search(r"(?<![A-Za-z0-9_-])" + re.escape(record_id) + r"(?![A-Za-z0-9_-])", content.decode("utf-8")):
                raise AuthoringError(f"derived consumer {consumer} must cite the exact rule id {record_id}")
    view.put(ref, dump(data))
    errors: list[str] = []
    if identity == "governance-terms":
        _module("validate-ai-context").validate_governance_term_routing_data(data, errors, root=view.path())
    elif identity == "rule-consumers":
        owner = ".dev/standards/AI-CONTEXT-OWNERSHIP.md"
        if view.read(owner) is None: raise AuthoringError(f"missing rule ownership authority {owner}")
        validator = _module("validate-ai-context")
        validator.ROOT = view.path()
        validator.validate_rule_ownership(errors)
    elif identity in {"validation-gate-groups", "validation-external-gates"}:
        validator = _module("validation_subject")
        for authority in (validator.SCHEMA_REF, validator.CONTRACT_REF, validator.REGISTRY_REF, validator.SUBJECT_IMPLEMENTATION_REF):
            if view.read(authority) is None: raise AuthoringError(f"missing classification authority {authority}")
        # Target bytes are observed, never executed. The fixed running source
        # registry supplies metadata only; its gate commands are not dispatched.
        checks = validator.registry_snapshot(Path(__file__).resolve().parents[2])
        validator.validate_classification_authority(data, checks)
    elif identity == "shell-assets":
        # Git index modes are authority distinct from HEAD and working bytes.
        view.observed["git:shell-index"] = git(view.root, "ls-files", "--stage", "*.sh")
        _module("validate-shell-assets").validate_repository_manifest(data, errors, root=view.path())
    elif identity in CATALOG_RUNTIME:
        schema_ref = ref.removesuffix(".yaml").replace(".ai/distribution/", ".ai/distribution/schemas/") + ".schema.yaml"
        if view.read(schema_ref) is None: raise AuthoringError(f"missing source catalog authority {schema_ref}")
        if identity == "source-dispositions":
            pinned = git(view.root, "rev-parse", "HEAD").removeprefix("0:")
            report = _module("validate-source-dispositions").validate_repository(view.path(), source_ref=pinned)
            if report["source_commit"] != pinned: raise AuthoringError("source disposition commit drift")
            view.observed["git:disposition-source"] = {"commit": report["source_commit"], "tree": report["source_tree"]}
        else:
            _module("validate-repository-identity").load_identity_registry(view.path(), ref, validate_consumers=True)
    elif identity.startswith("evaluation-"):
        for name in ("manifest_schema", "result_schema"):
            schema_ref = string(data.get(name), name)
            if view.read(schema_ref) is None: raise AuthoringError(f"missing catalog authority {schema_ref}")
        validator = _module("validate-ai-behavior-evaluation")
        if identity == "evaluation-corpus":
            validator.validate_manifest(data, root=view.path())
            # Observing references grants no behavioral or expected-result acceptance.
            refs = [string(data.get("baseline"), "baseline")]
            refs += [string(row[name], name) for row in data["cases"] for name in ("input", "expected")]
            for path in refs:
                if view.read(path) is None: raise AuthoringError(f"missing evaluation input {path}")
        else:
            validator.validate_fault_manifest(data, root=view.path())
    else:
        for path, *_ in list(CATALOGS.values())[:3]:
            schema_ref = path.removesuffix(".yaml") + ".schema.yaml"
            if view.read(schema_ref) is None: raise AuthoringError(f"missing catalog authority {schema_ref}")
            load(view, path)  # strict parse all contextual catalogs before owner reader
        if view.read(".ai/assets/shared/ROLE-EXECUTION-CONTRACT.md") is None:
            raise AuthoringError("missing role execution authority")
        _module("validate-ai-context").validate_sag003_provider_role_projection_contract(errors, root=view.path())
    if errors: raise AuthoringError("projected catalog validation failed before writes:\n- " + "\n- ".join(errors))


def lifecycle_update(view: View, request: dict) -> None:
    fields(request, {"version", "operation", "timestamp", "id", "changes"}, set(), "lifecycle request")
    validator = _module("artifact_lifecycle")
    ref = validator.REGISTRY
    data = load(view, ref, writable=True)
    changes = request["changes"]
    fields(changes, set(), {"models", "owner", "authoring", "producers", "validators", "readable", "writable", "migration", "admissible", "limits", "applicability"}, "lifecycle changes")
    if not changes: raise AuthoringError("lifecycle changes must not be empty")
    matches = [row for row in data["records"] if row["kind"] == request["id"]]
    if len(matches) != 1: raise AuthoringError("lifecycle kind must resolve exactly once; kind and baseline identity are immutable")
    matches[0].update(changes)
    view.put(ref, dump(data, json_format=True))
    errors = validator.validate_registry(view.path(), source_context=view.path(".ai/distribution").is_dir())
    if errors: raise AuthoringError("projected lifecycle validation failed before writes:\n- " + "\n- ".join(errors))


def target_selection(view: View, request: dict) -> None:
    action = request["operation"].split(".")[1]
    fields(request, {"version", "operation", "timestamp", "id"} | ({"selection"} if action == "technology" else {"mode", "merge_gate", "decision_ref"}), set(), "target request")
    if request["id"] != "project-config": raise AuthoringError("only existing project-config is supported; target initialization is a separate operation")
    ref = ".dev/project-config.yaml"
    data = load(view, ref, writable=True)
    for path in TARGET_SCHEMAS:
        if view.read(path) is None: raise AuthoringError(f"missing target selection authority {path}")
    validator = _module("validate-ai-context")
    errors: list[str] = []
    validator.validate_technology_selection_contract(errors, root=view.path())
    validator.validate_work_item_binding_contract(errors, root=view.path())
    validator.validate_target_selection_records(data, errors, root=view.path())
    if errors: raise AuthoringError("existing target selection invalid:\n- " + "\n- ".join(errors))
    if action == "technology":
        selection = request["selection"]
        if type(selection) is not dict: raise AuthoringError("selection must be a mapping")
        slot = string(selection.get("slot"), "selection.slot")
        matches = [item for item in data["technologySelections"] if item["slot"] == slot]
        if matches: matches[0].update(selection)
        else: data["technologySelections"].append(selection)
    else:
        decision = string(request["decision_ref"], "decision_ref")
        if view.read(decision) is None: raise AuthoringError("decision_ref must name retained owner input; authoring does not verify approval")
        for key in ("mode", "merge_gate"): string(request[key], key)
        data["workManagement"]["workItemBinding"].update(mode=request["mode"], mergeGate=request["merge_gate"])
    validator.validate_target_selection_records(data, errors, root=view.path())
    if errors: raise AuthoringError("projected target selection invalid:\n- " + "\n- ".join(errors))
    view.put(ref, dump(data, json_format=True))


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
    if "timestamp" not in request: request["timestamp"] = automatic_timestamp()
    instant(request["timestamp"])
    view = View(root, _baseline)
    family = request["operation"].split(".")[0]
    # Validate the complete projected repository using the unchanged domain rules.
    try:
        {"workflow": workflow, "assessment": assessment, "role": role, "catalog": catalog_update, "target": target_selection, "lifecycle": lifecycle_update, "skill": skill_update}[family](view, request)
        # These families own linked locator/index bundles. Other adapters own
        # fixed disjoint paths and run their contextual owner checks above.
        # Their preview is not repository-wide workflow/assessment admission.
        errors = []
        if family in {"workflow", "assessment"}:
            errors = _module("validate-workflow-artifacts").validate_workflows(view.path())[0]
            errors += _module("validate-assessment-artifacts").validate_assessments(view.path())[0]
    except (KeyError, TypeError, AttributeError, OSError, ValueError, RuntimeError) as exc:
        raise AuthoringError(f"projected validation could not complete: {exc}; reconcile malformed records before authoring") from exc
    if errors: raise AuthoringError("projected validation failed before writes:\n- " + "\n- ".join(errors))
    for rel in (WORKFLOW_TEMPLATE, PLAN_TEMPLATE, TASK_TEMPLATE, ASSESSMENT_TEMPLATE, REPORT_TEMPLATE, REMEDIATION_TEMPLATE,
                ".dev/standards/WORKFLOW-ARTIFACT-POLICY.md", ".dev/standards/ASSESSMENT-ARTIFACT-POLICY.md",
                ".ai/scripts/validate-workflow-artifacts.py", ".ai/scripts/validate-assessment-artifacts.py",
                ".ai/scripts/artifact_authoring.py", ".ai/scripts/artifact_core.py", "requirements.txt", ".gitignore"):
        view.read(rel)
    selected_runtime = (("artifact_lifecycle.py",) if family == "lifecycle" else
                        (*ROLE_RUNTIME, "runtime_skill_entries.py") if family == "skill" else
                        CATALOG_RUNTIME[request["id"]] if family == "catalog" and request["id"] in CATALOG_RUNTIME else
                        ROLE_RUNTIME if family in {"role", "target"} or (family == "catalog" and not request["id"].startswith("evaluation-")) else
                        ("validate-ai-behavior-evaluation.py",) if family == "catalog" else ())
    if selected_runtime:
        for name in (*selected_runtime, "python-entrypoints.json", "python_prerequisites.py"):
            view.read(".ai/scripts/" + name)
    extra_runtime = (".ai/distribution/validators/product_identity_registry.py",) if family == "catalog" and request["id"] in {"source-identities", "identity-consumers"} else ()
    for ref in extra_runtime: view.read(ref)
    changes = {}
    for rel, after in view.overlay.items():
        target = safe_path(root, rel)
        before = _baseline[rel] if _baseline and rel in _baseline else target.read_bytes() if target.is_file() else None
        if before != after: changes[rel] = (before, after)
    if not changes: raise AuthoringError("request has no changes; choose new content or timestamp")
    context = {"head": git(root, "rev-parse", "HEAD"), "branch": git(root, "symbolic-ref", "--quiet", "HEAD", allowed=(0, 1)),
               "ignored": git(root, "check-ignore", "--no-index", "--", *sorted(changes), allowed=(0, 1))}
    source = view.observed.get("git:disposition-source")
    if source and context["head"] != "0:" + source["commit"]:
        raise AuthoringError("source disposition validation subject changed during preview")
    if context["ignored"].startswith("0:"): raise AuthoringError("artifact output is ignored; correct the repository policy first")
    binding = {"request": request, "inputs": view.observed, "git": context,
               "runtime": {ref: digest((Path(__file__).resolve().parents[2] / ref).read_bytes()) for ref in
                           tuple(".ai/scripts/" + name for name in (("artifact_authoring.py", "artifact_core.py", "validate-workflow-artifacts.py", "validate-assessment-artifacts.py", "python_prerequisites.py", "python-entrypoints.json") + selected_runtime)) + extra_runtime},
               "changes": {p: [None if before is None else digest(before), digest(after)] for p, (before, after) in changes.items()}}
    return Plan(request, changes, digest(canonical(binding)))


def catalog(root: Path) -> dict:
    view = View(root)
    return {"request_version": "1.0", "operations": sorted(OPERATIONS), "families": {
        "workflow": {"profile": "ai-context-maintenance", "readable": "current templates only", "writable": template(view, WORKFLOW_TEMPLATE)["template_version"], "template_source": WORKFLOW_TEMPLATE,
                     "remediation_report": {"operation": "workflow.report", "template_source": REMEDIATION_TEMPLATE,
                                            "state": "opt-in projection from locator/tasks; no independent or provider outcome inferred"}},
        "assessment": {"profile": ["ai-context-audit", "ai-context-verification"], "readable": "current templates only", "writable": template(view, ASSESSMENT_TEMPLATE)["template_version"], "template_source": ASSESSMENT_TEMPLATE},
        "role": {"profile": "existing dynamic sub-agent-role-prompt", "readable": ["1.1"],
                 "migration_input": ["1.0 dynamic roles only; not current admission"], "writable": "1.1", "admissible": "1.1 plus canonical owner/reference validation",
                 "editable_fields": sorted(ROLE_EDITABLE), "template_source": ROLE_AUTHORITY[1],
                 "migration": {"disposition": "convert", "from": "1.0", "to": "1.1",
                               "preconditions": "empty wrapper_targets; absent or empty adapter_metadata; valid current relationships",
                               "preserve_original": "exact bytes in ignored recovery journal; retain it for historical custody"},
                 "unsupported": "creation, promoted adapters, owner/status/identity changes and all other version edges; preserve originals for owner reconciliation"}},
        "catalogs": {key: {"path": value[0], "record_selector": value[2] or "provider key", "editable_fields": sorted(value[3]), "readable": [CATALOG_VERSIONS[key]], "writable": CATALOG_VERSIONS[key], "migration": "unsupported; preserve original and reconcile with owner", "available": view.path(value[0]).is_file(), "admissible": "owning contextual validation; no runtime or evaluation execution asserted"} for key, value in CATALOGS.items()},
        "skills": {"operation": "skill.update", "version": "1.0", "editable_fields": ["inputs", "outputs", "constraints", "triggers", "handoff_rules", "runtime_notes"], "generated_pilot_extra_fields": ["title", "purpose"], "generated_pilots": ["code-reviewer", "local-change-implementer"], "migration": "unsupported", "wrapper_policy": "preserve thin wrappers; regenerate both declared pilot wrappers from final canonical bytes"},
        "target_selections": {"path": ".dev/project-config.yaml", "operations": ["target.technology", "target.work-binding"], "enclosing_version": 1, "model_version": "1.0", "migration": "unsupported", "available": view.path(".dev/project-config.yaml").is_file(), "authority": "caller supplies target facts and decisions; no implicit initialization or adoption"},
        "lifecycle_registry": {"operation": "lifecycle.update", "record_selector": "kind", "version": "1.0", "migration": "unsupported", "protected": ["kind", "baseline_refs", "coverage"], "admission": "source declarations only; semantics require owner review"},
        "migration": "role.migrate supports only the catalogued dynamic edge; other families preserve originals and use their owning route",
        "timestamp": "optional; preview captures real local time once; apply the resolved preview request without changing its timestamp",
        "final_assessments": "readable, immutable; create successor or reviewed addendum",
        "yaml_comments": "YAML comments are refused before rewriting; scalar hash content, Markdown prose and JSON/YAML extension fields are retained",
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
    if "timestamp" not in request:
        raise AuthoringError("apply requires the resolved preview request; use preview --json and apply --preview, without hand-editing timestamps")
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
