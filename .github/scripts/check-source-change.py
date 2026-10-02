#!/usr/bin/env python3
"""Source-only affected checks. No provider access, installs, or legacy matrices."""
from __future__ import annotations

import argparse
import ast
from dataclasses import dataclass, field
from datetime import datetime
import json
import math
import os
from pathlib import Path, PurePosixPath
import posixpath
import re
import subprocess
import sys
import threading
import time
from urllib.parse import unquote, urlsplit

MAX_BLOB = 1024 * 1024
MAX_PATHS = 256
MANIFEST = "src/distribution/manifest.yaml"
RUNNER = "tests/run.py"
RUNNER_INTERFACE = "framework-tests/1"
SUITES = ("schemas", "tools", "distribution", "release", "source", "loader", "platform")
TEST_SUITES = {
    **{"tests/framework_next/" + name: "distribution" for name in (
        "test_contracts.py", "test_adapters.py", "test_distribution_contracts.py",
        "test_maintenance_contracts.py", "test_skill_naming.py", "test_distribution_versions.py")},
    "tests/framework_next/test_engine_source.py": "loader",
    "tests/framework_next/test_protected_paths.py": "platform",
    "tests/framework_next/test_windows_paths.py": "platform",
    "tests/test_runner.py": "source",
}
# Only the removed side of a deletion or rename may use these historical names.
RETIRED_TESTS = frozenset({"tests/framework_next/" + name for name in (
    "run.py", "test_knowledge.py", "test_work.py", "test_cbf.py", "test_native_windows.py",
    "test_pr_git_worktree.py", "test_installation_scan_budget.py", "test_breaking_reinstall.py",
    "test_versioned_candidates.py", "test_rc2_adapters.py", "test_rc2_distribution.py",
    "test_rc2_maintenance.py")}) | {".github/tests/test-release-tools.py", ".github/tests/test_source_gates.py"}
LEGACY_WORKFLOWS = frozenset({"governance.yml", "portable-gates.yml", "nightly-full-readiness.yml",
    "package-candidate.yml", "publish-release.yml", "release-provider-preflight.yml",
    "test-fixture-acceleration.yml"})
SOURCE_FILES = frozenset({"AGENTS.md", "AGENTS.zh-TW.md", "CLAUDE.md",
    ".github/pull_request_template.md", ".github/scripts/check-source-change.py",
    ".github/scripts/run-source-native.py", ".github/workflows/source-checks.yml",
    ".github/workflows/source-native.yml"})
DISTRIBUTION_FILES = frozenset({"src/distribution/" + name for name in (
    "__init__.py", "data.py", "git_source.py", "package.py", "selection.py", "assembly.py",
    "catalog.py", "content.py", "contracts.py", "codex.py", "claude.py")})
NATIVE_FILES = frozenset({"src/distribution/" + name for name in (
    "installation.py", "installation_io.py", "installation_plan.py", "installation_state.py",
    "maintenance_coordination.py", "reinstallation.py")}) | {
        "src/tools/maintain_framework.py", "tools/reinstall-framework.py"}
RELEASE_FILES = frozenset({".github/scripts/" + name for name in (
    "build-release.py", "draft-release.py", "release_common.py")})
WORKFLOW_ROOT = ".dev/workflows/"


class GateError(Exception):
    """A bounded failure; never an implicit full-suite fallback."""


def full_sha(value: str) -> str:
    if not re.fullmatch(r"[0-9a-f]{40}", value or "") or value == "0" * 40:
        raise GateError("expected a nonzero full lowercase 40-character commit SHA")
    return value


def safe_path(value: str) -> str:
    if (not isinstance(value, str) or not value or len(value) > 512
            or any(ord(c) < 32 or ord(c) == 127 for c in value)
            or any(c in value for c in "\\:*?[]")
            or value.startswith("/") or any(p in ("", ".", "..") for p in value.split("/"))):
        raise GateError("unsafe repository-relative path")
    return value


def strict_json(data: bytes):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise GateError("duplicate JSON key")
            result[key] = value
        return result
    return json.loads(data.decode("utf-8"), object_pairs_hook=pairs,
                      parse_constant=lambda _: (_ for _ in ()).throw(GateError("nonfinite JSON")))


def strict_yaml(data: bytes):
    try:
        import yaml
    except ImportError as exc:
        raise GateError("missing selected parser: PyYAML >=6,<7; install nothing implicitly") from exc
    class Loader(yaml.SafeLoader):
        pass
    def mapping(loader, node):
        result = {}
        for key_node, value_node in node.value:
            key = loader.construct_object(key_node)
            if not isinstance(key, (str, int, bool)) or key in result:
                raise GateError("duplicate or unsupported YAML key")
            result[key] = loader.construct_object(value_node)
        return result
    Loader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, mapping)
    try:
        depth = count = aliases = 0
        for event in yaml.parse(data):
            count += 1
            aliases += isinstance(event, yaml.events.AliasEvent)
            depth += isinstance(event, (yaml.events.MappingStartEvent, yaml.events.SequenceStartEvent))
            depth -= isinstance(event, (yaml.events.MappingEndEvent, yaml.events.SequenceEndEvent))
            if count > 20000 or depth > 64 or aliases > 64:
                raise GateError("YAML exceeds bounded parser limits")
        return yaml.load(data.decode("utf-8"), Loader=Loader)
    except yaml.YAMLError as exc:
        raise GateError("invalid YAML syntax") from exc


@dataclass(frozen=True)
class Outcome:
    status: str
    code: int | None
    output: bytes = b""
    stderr: bytes = b""


def bounded_run(argv, cwd, *, timeout=60, limit=65536, separate_streams=False) -> Outcome:
    """Bound total capture; callers can separate JSON stdout from test diagnostics."""
    try:
        child = subprocess.Popen(argv, cwd=cwd, stdin=subprocess.DEVNULL,
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE if separate_streams else subprocess.STDOUT,
                                 shell=False)
    except OSError:
        return Outcome("unavailable", None)
    captured, errors = bytearray(), bytearray()
    overflow = threading.Event()
    lock = threading.Lock()
    def reader(stream, destination):
        while chunk := stream.read(4096):
            with lock:
                remaining = limit - len(captured) - len(errors)
                destination.extend(chunk[:remaining])
                if len(chunk) > remaining:
                    overflow.set()
            if overflow.is_set():
                try:
                    child.kill()
                except OSError:
                    pass
                break
    streams = [(child.stdout, captured)]
    if separate_streams:
        streams.append((child.stderr, errors))
    threads = [threading.Thread(target=reader, args=pair, daemon=True) for pair in streams]
    for thread in threads:
        thread.start()
    try:
        code = child.wait(timeout=timeout)
        status = "passed" if code == 0 else "failed"
    except subprocess.TimeoutExpired:
        child.kill()
        child.wait(timeout=5)
        code, status = None, "timed-out"
    for thread in threads:
        thread.join(timeout=5)
    if any(thread.is_alive() for thread in threads):
        status = "output-stream-not-closed"
    elif overflow.is_set():
        status = "output-limit"
    for thread, (stream, _) in zip(threads, streams):
        if not thread.is_alive():
            stream.close()
    return Outcome(status, code, bytes(captured), bytes(errors))


class GitTree:
    def __init__(self, root: Path, revision: str):
        self.root, self.revision = root, full_sha(revision)
        actual = self.git("rev-parse", "--verify", revision + "^{commit}").decode().strip()
        if actual != revision:
            raise GateError("commit identity mismatch")

    def git(self, *args, limit=MAX_BLOB):
        result = bounded_run(["git", "--no-pager", *args], self.root, limit=limit)
        if result.status != "passed":
            raise GateError("Git read failed or exceeded bounds: " + args[0])
        return result.output

    def entry(self, path):
        path = safe_path(path)
        records = self.git("ls-tree", "-z", self.revision, "--", path).split(b"\0")
        entries = []
        for raw in filter(None, records):
            info, name = raw.split(b"\t", 1)
            if name.decode("utf-8") == path:
                entries.append(info.decode().split())
        if len(entries) > 1:
            raise GateError("ambiguous tree entry")
        return entries[0] if entries else None

    def exists(self, path):
        return self.entry(path) is not None

    def read(self, path):
        entry = self.entry(path)
        if not entry or entry[0] not in ("100644", "100755") or entry[1] != "blob":
            raise GateError("missing or nonregular blob: " + path)
        size = int(self.git("cat-file", "-s", entry[2]))
        if size > MAX_BLOB:
            raise GateError("blob exceeds 1 MiB source-check bound: " + path)
        return self.git("cat-file", "blob", entry[2])


@dataclass(frozen=True)
class Change:
    before: str | None
    after: str | None


def parse_diff(data: bytes) -> list[Change]:
    if data and not data.endswith(b"\0"):
        raise GateError("incomplete NUL-delimited diff")
    fields = data[:-1].decode("utf-8").split("\0") if data else []
    changes = []
    i = 0
    while i < len(fields):
        status = fields[i]
        count = 2 if re.fullmatch(r"R(?:100|0[0-9]{2}|[0-9]{1,2})", status) else 1
        if status not in ("A", "M", "D", "T") and count != 2:
            raise GateError("unsupported diff status: " + status[:12])
        if i + count >= len(fields):
            raise GateError("incomplete diff record")
        names = [safe_path(p) for p in fields[i + 1:i + count + 1]]
        changes.append(Change(None if status == "A" else names[0],
                              None if status == "D" else names[-1]))
        i += count + 1
        if len(changes) > MAX_PATHS:
            raise GateError("diff exceeds 256 changed entries; select a bounded review")
    return changes


class Ownership:
    """Read declared members/roles, without importing any product code."""
    def __init__(self, tree):
        self.tree, self._manifest, self._packages = tree, None, {}
        self._components, self._members = {}, {}

    @staticmethod
    def identifier(value):
        if not isinstance(value, str) or not re.fullmatch(r"[a-z][a-z0-9-]{0,63}", value):
            raise GateError("unsafe package identifier")
        return value

    @staticmethod
    def rows(value, name, limit=512, *, mappings=False):
        if (not isinstance(value, list) or len(value) > limit
                or (mappings and any(not isinstance(row, dict) for row in value))):
            raise GateError("missing or oversized " + name)
        return value

    def manifest(self):
        if self._manifest is None:
            value = strict_yaml(self.tree.read(MANIFEST))
            if not isinstance(value, dict) or type(value.get("manifest_version")) is not int or value["manifest_version"] != 2:
                raise GateError("unknown manifest ownership version")
            components = self.rows(value.get("components"), "component ownership", 64, mappings=True)
            self.rows(value.get("profiles"), "profile ownership", 64, mappings=True)
            self.rows(value.get("adapters"), "adapter ownership", 16, mappings=True)
            seen_paths = set()
            for component in components:
                kind, owner = component["kind"], self.identifier(component["id"])
                if kind not in ("skill", "knowledge"):
                    raise GateError("unknown component kind")
                key = kind, owner
                if key in self._components:
                    raise GateError("duplicate component ownership")
                root = safe_path(component["source"])
                expected_root = ("src/skills/" if kind == "skill" else "src/knowledge/") + owner
                if root != expected_root or not isinstance(component.get("version"), str) or not component["version"]:
                    raise GateError("unknown component source or version")
                safe_path(component["metadata"])
                for member in self.rows(component.get("members"), "member ownership", mappings=True):
                    relative = safe_path(member["source"])
                    full = safe_path(root + "/" + relative)
                    if full.casefold() in seen_paths:
                        raise GateError("ambiguous declared member: " + full)
                    seen_paths.add(full.casefold())
                    self._members[full] = component, relative
                if root + "/" + component["metadata"] not in self._members:
                    raise GateError("metadata is not a declared member")
                self._components[key] = component
            self._manifest = value
        return self._manifest

    def metadata(self, component):
        key = component["kind"], component["id"]
        if key in self._packages:
            return self._packages[key]
        path = component["source"] + "/" + component["metadata"]
        metadata = strict_yaml(self.tree.read(path))
        if (not isinstance(metadata, dict) or metadata.get("id") != component["id"]
                or metadata.get("version") != component["version"]):
            raise GateError("package identity differs from declared ownership: " + path)
        roles = {}
        def role(member, kind):
            member = safe_path(member)
            if member in roles:
                raise GateError("ambiguous metadata member role: " + path)
            roles[member] = kind
        if component["kind"] == "skill":
            version = metadata.get("metadata_version")
            if type(version) is not int or version not in (1, 2, 3, 4):
                raise GateError("unknown skill metadata ownership version")
            role(component["metadata"], "metadata")
            role(metadata["entrypoint"], "prose")
            resources = metadata.get("resources")
            if not isinstance(resources, dict):
                raise GateError("missing skill resource ownership")
            for member in self.rows(resources.get("references"), "reference ownership"):
                role(member, "prose")
            for kind in ("schemas", "templates", "tools"):
                for resource in self.rows(resources.get(kind), kind + " ownership", mappings=True):
                    role(resource["entrypoint" if kind == "tools" else "path"], kind)
        else:
            if type(metadata.get("content_package_version")) is not int or metadata["content_package_version"] != 1:
                raise GateError("unknown knowledge metadata ownership version")
            kinds = {"index", "knowledge", "metadata", "normative-rule", "rule-catalog", "example", "source-include", "template"}
            for member in self.rows(metadata.get("members"), "knowledge member ownership", mappings=True):
                if member.get("kind") not in kinds:
                    raise GateError("unknown knowledge member kind")
                # Knowledge examples and source includes are inert content, not tools.
                role(member["path"], "metadata" if member["kind"] == "metadata" else "prose")
            if roles.get(component["metadata"]) != "metadata" or metadata.get("entrypoint") not in roles:
                raise GateError("missing knowledge metadata/entrypoint ownership")
        if set(roles) != {member["source"] for member in component["members"]}:
            raise GateError("manifest and metadata member ownership differ: " + path)
        result = metadata, roles
        self._packages[key] = result
        return result

    def package(self, path):
        self.manifest()
        if path not in self._members:
            raise GateError("unknown declared member: " + path)
        component, relative = self._members[path]
        _, roles = self.metadata(component)
        return component["kind"], component["id"], roles[relative], "tools" in roles.values()

    def prove_dependencies(self):
        """Bind declared dependency edges to this tree; do not assume empty closure."""
        edges = {}
        for component in self.manifest()["components"]:
            key = component["kind"], component["id"]
            metadata, _ = self.metadata(component)
            dependencies = metadata.get("dependencies")
            if not isinstance(dependencies, dict) or set(dependencies) != {"required", "optional"}:
                raise GateError("missing dependency ownership")
            rows = []
            for requirement in ("required", "optional"):
                for dependency in self.rows(dependencies[requirement], "dependencies", 64, mappings=True):
                    rows.append((dependency.get("kind", "skill"), dependency["id"],
                                 dependency["version"], requirement, dependency.get("on_missing")))
            if component["kind"] == "skill" and metadata["metadata_version"] == 4:
                consumption_ids = set()
                for dependency in self.rows(metadata.get("knowledge_consumption"), "knowledge consumption", 64, mappings=True):
                    identifier = self.identifier(dependency["id"])
                    if identifier in consumption_ids:
                        raise GateError("duplicate knowledge consumption")
                    consumption_ids.add(identifier)
                    for field in ("operations", "resources"):
                        values = self.rows(dependency.get(field), "knowledge " + field)
                        if (not values or any(not isinstance(value, str) or not value for value in values)
                                or len(values) != len(set(values))):
                            raise GateError("unknown knowledge consumption binding")
                    rows.append(("knowledge", dependency["package"], dependency["version"],
                                 dependency["requirement"], dependency.get("on_missing")))
            edges[key] = set()
            for kind, owner, version, requirement, missing in rows:
                target = kind, self.identifier(owner)
                if (kind not in ("skill", "knowledge") or requirement not in ("required", "optional")
                        or not isinstance(version, str) or not version
                        or (requirement == "optional" and missing != "unavailable")):
                    raise GateError("unknown dependency binding")
                declared = self._components.get(target)
                if declared is None:
                    if requirement == "required":
                        raise GateError("missing required dependency: " + owner)
                    continue
                if declared["version"] != version:
                    raise GateError("dependency version differs from declared ownership: " + owner)
                edges[key].add(target)
        complete, active = set(), set()
        def visit(key):
            if key in active:
                raise GateError("cyclic dependency ownership")
            if key not in complete:
                active.add(key)
                for target in edges[key]:
                    visit(target)
                active.remove(key)
                complete.add(key)
        for key in edges:
            visit(key)

    def declared_distribution(self, path):
        manifest = self.manifest()
        paths = {safe_path(p["path"]) for p in manifest["profiles"]}
        for adapter in manifest["adapters"]:
            root = safe_path(adapter["source"])
            if root != "src/adapters/" + self.identifier(adapter["id"]):
                raise GateError("unknown adapter source")
            members = self.rows(adapter.get("members"), "adapter members")
            if adapter["template"] not in members:
                raise GateError("undeclared adapter template")
            paths.update(safe_path(root + "/" + safe_path(member)) for member in members)
        return path in paths

    def workflow(self, path):
        """Validate only the changed record and its pinned source-owned locator."""
        parts = path.split("/")
        if len(parts) < 4 or not re.fullmatch(r"\d{4}-\d{2}-\d{2}-[a-z0-9][a-z0-9-]*", parts[2]):
            raise GateError("unknown workflow identity: " + path)
        workflow_id = parts[2]
        root = WORKFLOW_ROOT + workflow_id
        locator_path = root + "/workflow.yaml"
        locator = strict_yaml(self.tree.read(locator_path))
        if not isinstance(locator, dict):
            raise GateError("workflow locator must be a mapping")
        required = ("workflow_id", "workflow_kind", "title", "owner_skill", "status",
                    "artifact_root", "entrypoint", "created_at", "updated_at",
                    "template_source", "template_version", "branch", "base_branch")
        if (locator.get("schema_version") != "1.0"
                or any(not isinstance(locator.get(key), str) or not locator[key].strip() for key in required)
                or locator["workflow_id"] != workflow_id or locator["artifact_root"] != root
                or locator["branch"] == locator["base_branch"] or locator["branch"] == "main"):
            raise GateError("invalid workflow locator identity or fields: " + locator_path)
        if locator["status"] not in {"pending", "in_progress", "completed", "deferred", "cancelled"}:
            raise GateError("unknown source workflow state")
        for key in ("created_at", "updated_at"):
            if datetime.fromisoformat(locator[key]).utcoffset() is None:
                raise GateError("workflow timestamp lacks offset")
        self.tree.read(safe_path(root + "/" + safe_path(locator["entrypoint"])))
        owner = self.identifier(locator["owner_skill"])
        self.tree.read("src/skills/" + owner + "/skill-package.yaml")
        # Both retained locator spellings name online Issues; neither grants authority.
        issues = locator.get("work_items", locator.get("issue_refs"))
        if not isinstance(issues, list) or not issues or len(issues) > 32:
            raise GateError("workflow needs bounded online Issue binding")
        for issue in issues:
            if isinstance(issue, str) and re.fullmatch(r"#[1-9][0-9]*", issue):
                continue
            if (not isinstance(issue, dict) or issue.get("provider") != "github"
                    or type(issue.get("issue")) is not int or issue["issue"] <= 0
                    or issue.get("url") != "https://github.com/YuChia-Wei/ai-collaboration-framework/issues/" + str(issue["issue"])):
                raise GateError("workflow has invalid online Issue binding")
        relative = path[len(root) + 1:]
        if relative == "workflow.yaml" or relative.lower().endswith(".md"):
            return workflow_id
        if re.fullmatch(r"tasks/[A-Za-z0-9][A-Za-z0-9_-]*\.json", relative):
            record = strict_json(self.tree.read(path))
            fields = ("task_id", "workflow_id", "owner_skill", "status", "created_at", "updated_at",
                      "template_source", "template_version", "model", "reasoning_effort")
            if (not isinstance(record, dict)
                    or any(not isinstance(record.get(key), str) or not record[key].strip() for key in fields)
                    or record["workflow_id"] != workflow_id
                    or record["task_id"] != PurePosixPath(relative).stem
                    or record["status"] not in {"pending", "in_progress", "completed", "deferred", "cancelled"}):
                raise GateError("invalid workflow task relationship: " + path)
            for key in ("created_at", "updated_at"):
                if datetime.fromisoformat(record[key]).utcoffset() is None:
                    raise GateError("task timestamp lacks offset")
            self.tree.read("src/skills/" + self.identifier(record["owner_skill"]) + "/skill-package.yaml")
            if record["status"] == "completed" and (
                    not isinstance(record.get("result_summary"), str) or not record["result_summary"].strip()
                    or record.get("finding_status") != "addressed"):
                raise GateError("completed task lacks result or finding disposition")
            return workflow_id
        raise GateError("unknown workflow record format: " + path)


@dataclass
class Selection:
    checks: set[str] = field(default_factory=lambda: {"content", "whitespace"})
    owners: set[str] = field(default_factory=set)
    requirements: set[str] = field(default_factory=set)
    errors: list[str] = field(default_factory=list)

    def document(self):
        return {"checks": sorted(self.checks), "owners": sorted(self.owners),
                "admission_requirements": sorted(self.requirements), "errors": self.errors[:20],
                "error_count": len(self.errors)}


def classify(path: str, ownership: Ownership, selection: Selection, *, removed=False):
    safe_path(path)
    ownership.tree.read(path)  # Includes deleted side mode/size safety.
    if path in RETIRED_TESTS:
        if not removed:
            raise GateError("retired test path is not an executable route: " + path)
        selection.owners.add("retired-tests")
        return
    if path.startswith((".dev/backlog/", ".ai/", ".agents/", ".claude/", ".codex/", ".dev/ai-context/")):
        raise GateError("legacy/support owner must select exact checks: " + path)
    if path.startswith(("src/skills/", "src/knowledge/")):
        kind, owner, role, tool = ownership.package(path)
        selection.owners.add(owner)
        if role != "prose":
            ownership.prove_dependencies()
            selection.checks.add("schemas")
            if tool:
                selection.checks.add("tools")
            if role == "metadata":
                selection.checks.add("distribution")
        return
    if path in NATIVE_FILES:
        selection.checks.add("distribution")
        if path == "src/tools/maintain_framework.py":
            selection.checks.update({"loader", "platform"})
        elif path in {"src/distribution/installation_state.py", "src/distribution/installation_io.py",
                      "src/distribution/installation_plan.py"}:
            selection.checks.add("platform")
        selection.requirements.update({"native-acceptance-unavailable:owner-selection-required", "independent-scoped-review"})
        selection.owners.add("installation")
        return
    if (path == MANIFEST or path in DISTRIBUTION_FILES
            or path.startswith("src/distribution/schemas/")
            or path in {"tools/build-development.py", "tools/build-candidate.py", "tools/build-catalog.py", "tools/derive-subset.py"}
            or path.startswith(("src/profiles/", "src/adapters/"))):
        if path.startswith(("src/profiles/", "src/adapters/")) and not ownership.declared_distribution(path):
            raise GateError("undeclared profile/adapter: " + path)
        ownership.prove_dependencies()
        selection.checks.add("distribution")
        if path == MANIFEST or path.startswith("src/distribution/schemas/"):
            selection.checks.add("schemas")
        selection.owners.add("distribution")
        return
    if path in RELEASE_FILES:
        selection.checks.add("release")
        selection.requirements.add("independent-scoped-review")
        selection.owners.add("release-tooling")
        return
    if path in TEST_SUITES:
        selection.checks.add(TEST_SUITES[path])
        selection.owners.add("source-tests")
        return
    for suite in ("schemas", "tools", "release", "source"):
        if path.startswith("tests/" + suite + "/") and path.endswith(".py"):
            selection.checks.add(suite)
            selection.owners.add("source-tests")
            return
    if path in {"tests/framework_next/support.py", "tests/framework_next/__init__.py"}:
        selection.checks.update({"distribution", "loader", "platform"})
        selection.owners.add("source-test-support")
        return
    if path in {RUNNER, "requirements.txt", "tests/requirements.txt"}:
        selection.checks.update(SUITES)
        if path == RUNNER:
            selection.requirements.add("independent-scoped-review")
        selection.owners.add("source-test-runtime")
        return
    if (path in SOURCE_FILES or path in {"tests/__init__.py", ".gitignore", ".gitattributes"}
            or (path.startswith((".dev/standards/", ".dev/contracts/"))
                and PurePosixPath(path).suffix.lower() in {".md", ".yaml", ".yml", ".json"})):
        selection.checks.add("source")
        selection.requirements.add("independent-scoped-review")
        selection.owners.add("source-governance")
        return
    if path.startswith(".github/"):
        raise GateError("unselected source/legacy pipeline owner: " + path)
    if path.startswith(WORKFLOW_ROOT):
        workflow_id = ownership.workflow(path)
        selection.owners.add("source-workflow:" + workflow_id)
        return
    if path == ".dev/TEAM-GIT-FLOW-RULES.MD":
        selection.checks.add("source")
        selection.requirements.add("independent-scoped-review")
        selection.owners.add("source-governance")
        return
    if (path in {"README.md", "README.en.md", "LICENSE", "tests/readme.md", "tests/framework_next/README.md"}
            or (path.startswith((".dev/design/", ".dev/guides/")) and path.lower().endswith(".md"))):
        selection.owners.add("source-prose")
        return
    raise GateError("unknown ownership; coordinator must select checks: " + path)


def select(changes, before, after):
    result = Selection()
    owners = Ownership(before), Ownership(after)
    for change in changes:
        for index, (path, ownership) in enumerate(zip((change.before, change.after), owners)):
            if path:
                try:
                    removed = index == 0 and change.before != change.after and not after.exists(path)
                    classify(path, ownership, result, removed=removed)
                except (GateError, KeyError, TypeError, ValueError) as exc:
                    result.errors.append(str(exc)[:600])
    return result


def local_links(text):
    # File targets only; heading semantics and reference meaning remain review work.
    text = re.sub(r"(?ms)^\s*(```|~~~).*?^\s*\1\s*$", "", text)
    inline = re.findall(r"!?\[[^\]\n]*\]\(<?([^\s)>]+)>?(?:\s+[^)]+)?\)", text)
    definitions = re.findall(r"(?m)^\s*\[[^\]\n]+\]:\s*<?([^\s>]+)>?", text)
    return set(inline + definitions)


def content_checks(changes, before, after):
    for change in changes:
        if not change.after:
            continue
        path = change.after
        raw = after.read(path)
        text = raw.decode("utf-8")
        if re.search(r"(?m)^(?:<{7} |={7}$|>{7} )", text):
            raise GateError("conflict marker: " + path)
        suffix = PurePosixPath(path).suffix.lower()
        if suffix == ".py":
            ast.parse(text, filename=path)
        elif suffix == ".json":
            strict_json(raw)
        elif suffix in (".yaml", ".yml"):
            strict_yaml(raw)
        elif suffix == ".md":
            previous = before.read(change.before).decode("utf-8") if change.before else ""
            # A rename changes resolution even for an unchanged relative link.
            old_links = local_links(previous) if change.before == change.after else set()
            for link in sorted(local_links(text) - old_links):
                parsed = urlsplit(link)
                if parsed.scheme or parsed.netloc or not parsed.path:
                    continue
                decoded = unquote(parsed.path)
                target = posixpath.normpath(posixpath.join(posixpath.dirname(path), decoded))
                if not after.exists(safe_path(target)):
                    raise GateError("changed local reference missing: " + path + " -> " + target)


def command_for(check):
    if check not in SUITES:
        raise GateError("unknown selected suite: " + str(check))
    return [sys.executable, "-I", "-B", RUNNER, "--suite", check]


def run_selected(check, root, head, launch=bounded_run):
    argv = command_for(check)
    path = safe_path(argv[3])
    expected = head.read(path)
    entry = root / path
    for parent in [entry, *entry.parents]:
        if parent == root.parent:
            break
        if parent.is_symlink() or (hasattr(parent, "is_junction") and parent.is_junction()):
            raise GateError("selected entry is linked")
    if not entry.is_file() or entry.read_bytes() != expected:
        raise GateError("selected command missing or differs from pinned head: " + path)
    subject = full_sha(head.revision)
    result = launch(argv, root, timeout=120, limit=65536, separate_streams=True)
    return {**command_result(check, result), "source_commit": subject}


def command_result(check, result):
    """Accept only one complete report for the exact selected suite."""
    if check not in SUITES:
        raise GateError("unknown selected suite: " + str(check))
    if result.status != "passed" or type(result.code) is not int or result.code != 0:
        raise GateError("selected command non-passing: " + check + ":" + result.status + ":exit=" + str(result.code))
    try:
        report = strict_json(result.output)
    except (ValueError, RecursionError) as exc:
        raise GateError("missing or invalid framework test report") from exc
    fields = {"interface", "suites", "outcome", "tests", "failures", "errors", "skipped", "duration_seconds"}
    if not isinstance(report, dict) or set(report) != {"framework_tests"}:
        raise GateError("missing framework test report")
    row = report["framework_tests"]
    if not isinstance(row, dict) or set(row) != fields:
        raise GateError("incomplete framework test report")
    if row["interface"] != RUNNER_INTERFACE or row["suites"] != [check] or row["outcome"] != "passed":
        raise GateError("framework test interface, selection or outcome mismatch")
    if type(row["tests"]) is not int or row["tests"] <= 0:
        raise GateError("framework test report has no executed tests")
    if any(type(row[field]) is not int or row[field] != 0 for field in ("failures", "errors", "skipped")):
        raise GateError("framework test report contains failures, errors or skips")
    duration = row["duration_seconds"]
    try:
        valid_duration = type(duration) in (int, float) and math.isfinite(duration) and duration >= 0
    except OverflowError:
        valid_duration = False
    if not valid_duration:
        raise GateError("invalid framework test duration")
    return {"check": check, "status": "passed", "tests": row["tests"], "skipped": 0,
            "duration_seconds": duration, "result_interface": RUNNER_INTERFACE}


def validate_event(event, event_name, base, head):
    if event_name != "pull_request" or not isinstance(event, dict):
        raise GateError("only pull_request is supported")
    if event.get("action") not in {"opened", "synchronize", "reopened", "edited", "ready_for_review"}:
        raise GateError("unselected pull_request action")
    pr = event.get("pull_request", {})
    if (pr.get("base", {}).get("ref") != "main" or pr.get("base", {}).get("sha") != base
            or pr.get("head", {}).get("sha") != head):
        raise GateError("event base/head/ref mismatch")
    # Draft status intentionally has no branch: the context always runs.


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", required=True)
    parser.add_argument("--head", required=True)
    args = parser.parse_args(argv)
    report = {"context": "Source change gate", "status": "failed", "results": [],
              "admission_status": "not-evaluated"}
    started = time.monotonic()
    try:
        base, head = full_sha(args.base), full_sha(args.head)
        report.update(base=base, head=head)
        if os.environ.get("GITHUB_ACTIONS") == "true":
            event_file = Path(os.environ["GITHUB_EVENT_PATH"])
            if event_file.stat().st_size > MAX_BLOB:
                raise GateError("event input exceeds bound")
            validate_event(strict_json(event_file.read_bytes()), os.environ.get("GITHUB_EVENT_NAME"), base, head)
        root = Path.cwd().resolve()
        before, after = GitTree(root, base), GitTree(root, head)
        if after.git("rev-parse", "HEAD").decode().strip() != head:
            raise GateError("checkout HEAD differs from event head")
        if after.git("diff", "--name-only", "HEAD", "--"):
            raise GateError("tracked working tree differs from head")
        changes = parse_diff(after.git("diff", "--no-ext-diff", "--no-textconv", "--name-status", "-z", "-M", base, head, "--"))
        selection = select(changes, before, after)
        report.update(selection.document())
        if selection.errors:
            raise GateError("unresolved ownership; see errors")
        content_checks(changes, before, after)
        report["results"].append({"check": "content", "status": "passed"})
        after.git("diff", "--no-ext-diff", "--no-textconv", "--check", base, head, "--")
        report["results"].append({"check": "whitespace", "status": "passed"})
        for check in sorted(selection.checks - {"content", "whitespace"}, key=SUITES.index):
            report["results"].append(run_selected(check, root, after))
        report["status"] = "passed"
    except (GateError, OSError, ValueError, KeyError, TypeError, SyntaxError, RecursionError) as exc:
        report["error"] = str(exc)[:1500]
    report["duration_seconds"] = round(time.monotonic() - started, 3)
    encoded = json.dumps(report, ensure_ascii=True, sort_keys=True)
    # CI workflow writes its bounded always-run summary; this JSON is diagnostic output.
    print(encoded[:32768])
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
