#!/usr/bin/env python3
"""Dormant source-only selector. No provider access, installs, or legacy matrices."""
from __future__ import annotations

import argparse
import ast
from dataclasses import dataclass, field
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
RUNNER = "tests/framework_next/run.py"
RUNNER_INTERFACE_COMMIT = "e71712b71791170c3f4946e131ce867f82dade8f"
PUBLIC_INTERFACE_COMMIT = "e71712b71791170c3f4946e131ce867f82dade8f"
# Exact prepare(..., phases) declarations; PublicCase adds resource-setup.
PUBLIC_PHASES = {family: ["resource-setup", "C4-config", "C6-binding", *phases]
                for family, phases in {
    "lesson": ["T1-round-trip", "C6-query-and-legacy", "T1-decision-successor", "C6-input-boundary"],
    "adr": ["T2-round-trip", "T2-decision-derive"],
    "standards-promotion": ["T3-round-trip", "T3-reconciliation-boundaries"],
    "pr": ["T4-git-round-trip", "T4-synthetic-provider"],
    "local-backlog": ["T5-round-trip"],
    "software-development-orchestrator": ["T6-round-trip", "T6-with-deferrals"],
    "problem-frame-author": ["T7-round-trip", "T7-structural-negatives"],
}.items()}
FAMILIES = frozenset({"lesson", "adr", "standards-promotion", "pr", "local-backlog",
                      "software-development-orchestrator", "problem-frame-author"})
# PublicCase in test_knowledge is shared by all seven families. These are test
# dependencies, not permission to discover or run unrelated regression modules.
PUBLIC_TEST_FAMILIES = {
    "tests/framework_next/test_knowledge.py": FAMILIES,
    "tests/framework_next/test_work.py": frozenset({"pr", "local-backlog", "software-development-orchestrator"}),
    "tests/framework_next/test_cbf.py": frozenset({"problem-frame-author"}),
}
OWNER_SELECTED_TESTS = {
    "tests/framework_next/test_engine_source.py": "engine-source-regressions:#371",
    "tests/framework_next/test_installation_scan_budget.py": "installation-scan-budget-regressions:#386",
    "tests/framework_next/test_pr_git_worktree.py": "pr-git-worktree-regressions:#335",
    "tests/framework_next/test_protected_paths.py": "protected-path-regressions:#383",
    "tests/framework_next/test_versioned_candidates.py": "versioned-candidate-regressions:#381",
    "tests/framework_next/test_windows_paths.py": "windows-path-regressions:#378",
}
LEGACY_WORKFLOWS = frozenset({"governance.yml", "portable-gates.yml", "nightly-full-readiness.yml",
    "package-candidate.yml", "publish-release.yml", "release-provider-preflight.yml",
    "test-fixture-acceleration.yml"})
SOURCE_FILES = frozenset({"AGENTS.md", "AGENTS.zh-TW.md", "CLAUDE.md",
    ".github/pull_request_template.md", ".github/scripts/check-source-change.py",
    ".github/scripts/run-source-native.py", ".github/workflows/source-checks.yml",
    ".github/workflows/source-native.yml"})
DISTRIBUTION_FILES = frozenset({"src/distribution/" + name for name in (
    "__init__.py", "data.py", "git_source.py", "package.py", "selection.py", "assembly.py", "codex.py")})
NATIVE_FILES = frozenset({"src/distribution/" + name for name in (
    "installation.py", "installation_io.py", "installation_plan.py", "installation_state.py",
    "maintenance_coordination.py")}) | {"src/tools/maintain_framework.py"}
RECORD_ROOT = ".dev/workflows/2026-09-23-source-gates-implementation/"


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
    """Bound total capture; public JSONL/stdout stays separate from unittest/stderr."""
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
        count = 2 if re.fullmatch(r"R(?:100|[0-9]{1,2})", status) else 1
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

    def manifest(self):
        if self._manifest is None:
            value = strict_yaml(self.tree.read(MANIFEST))
            if not isinstance(value, dict) or type(value.get("manifest_version")) is not int or value["manifest_version"] != 1:
                raise GateError("unknown manifest ownership version")
            if not isinstance(value.get("components"), list) or not isinstance(value.get("profiles"), list):
                raise GateError("missing component/profile ownership")
            if len(value["components"]) > 64 or len(value["profiles"]) > 64:
                raise GateError("ownership table exceeds selected bounds")
            self._manifest = value
        return self._manifest

    def package(self, path):
        owners = []
        for component in self.manifest()["components"]:
            root = safe_path(component["source"])
            for member in component["members"]:
                full = safe_path(root + "/" + safe_path(member["source"]))
                if full == path:
                    owners.append((component, member["source"]))
        if len(owners) != 1:
            raise GateError("unknown or ambiguous declared member: " + path)
        component, relative = owners[0]
        owner = component["id"]
        if not isinstance(owner, str) or not re.fullmatch(r"[a-z][a-z0-9-]{0,63}", owner):
            raise GateError("unsafe package identifier")
        if owner not in self._packages:
            metadata = strict_yaml(self.tree.read(component["source"] + "/" + safe_path(component["metadata"])))
            if (not isinstance(metadata, dict) or metadata.get("id") != owner
                    or type(metadata.get("metadata_version")) is not int
                    or metadata["metadata_version"] not in (1, 2, 3)):
                raise GateError("unknown package metadata ownership: " + path)
            self._packages[owner] = metadata
        metadata = self._packages[owner]
        resources = metadata.get("resources", {})
        if not isinstance(resources, dict) or not isinstance(resources.get("tools"), list):
            raise GateError("missing tool ownership: " + owner)
        prose = {metadata.get("entrypoint"), *resources.get("references", [])}
        declared = {component["metadata"], *prose}
        declared.update(item["path"] for kind in ("schemas", "templates") for item in resources.get(kind, []))
        declared.update(item["entrypoint"] for item in resources["tools"])
        if relative not in declared:
            raise GateError("member has no metadata role: " + path)
        return owner, relative in prose, bool(resources["tools"])

    def prove_dependencies(self):
        for component in self.manifest()["components"]:
            owner, _, _ = self.package(component["source"] + "/" + component["metadata"])
            dependencies = self._packages[owner].get("dependencies")
            if (not isinstance(dependencies, dict) or set(dependencies) != {"required", "optional"}
                    or dependencies["required"] != [] or dependencies["optional"] != []):
                raise GateError("transitive dependency impact requires coordinator binding: " + owner)

    def families(self):
        self.prove_dependencies()
        result = set()
        for component in self.manifest()["components"]:
            path = component["source"] + "/" + component["metadata"]
            owner, _, tool = self.package(path)
            if tool:
                if owner not in FAMILIES:
                    raise GateError("unknown public family: " + owner)
                result.add(owner)
        return result

    def declared_distribution(self, path):
        manifest = self.manifest()
        paths = {safe_path(p["path"]) for p in manifest["profiles"]}
        paths.update(safe_path(a["template"]) for a in manifest.get("adapters", []))
        return path in paths


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


def classify(path: str, ownership: Ownership, selection: Selection):
    safe_path(path)
    ownership.tree.read(path)  # Includes deleted side mode/size safety.
    if path.startswith((".dev/backlog/", ".ai/", ".agents/", ".claude/", ".codex/", ".dev/ai-context/")):
        raise GateError("legacy/support owner must select exact checks: " + path)
    if path.startswith("src/skills/"):
        owner, prose, tool = ownership.package(path)
        selection.owners.add(owner)
        if not prose:
            ownership.prove_dependencies()
            selection.checks.add("contracts")
            if tool:
                if owner not in FAMILIES:
                    raise GateError("unknown public family: " + owner)
                selection.checks.add("public:" + owner)
        return
    if path in NATIVE_FILES:
        selection.checks.add("contracts")
        selection.requirements.update({"native-trial-required:windows:V3-binding-pending", "independent-scoped-review"})
        selection.owners.add("installation")
        return
    if (path == MANIFEST or path in DISTRIBUTION_FILES
            or path in {"tools/build-development.py", "tools/build-candidate.py"}
            or path.startswith(("src/profiles/", "src/adapters/"))):
        if path.startswith(("src/profiles/", "src/adapters/")) and not ownership.declared_distribution(path):
            raise GateError("undeclared profile/adapter: " + path)
        selection.checks.add("contracts")
        selection.checks.update("public:" + family for family in ownership.families())
        selection.requirements.add("distribution-trial-required:affected-selections;contracts-build-Lesson-only")
        if path == "tools/build-candidate.py":
            selection.requirements.add("versioned-candidate-trial-required:affected-selections")
        selection.owners.add("distribution")
        return
    if path in PUBLIC_TEST_FAMILIES:
        families = PUBLIC_TEST_FAMILIES[path]
        selection.checks.update("public:" + family for family in families)
        selection.owners.update(families)
        selection.owners.add("new-public-tests")
        return
    if path == "tests/framework_next/test_native_windows.py":
        selection.owners.add("native-test-driver:#382")
        selection.requirements.update({"native-trial-required:windows:V3-binding-pending", "independent-scoped-review"})
        return
    if path in OWNER_SELECTED_TESTS:
        selection.owners.add(OWNER_SELECTED_TESTS[path])
        selection.requirements.add("owner-selected-regression-required:" + path)
        return
    if path in {"tests/framework_next/run.py", "tests/framework_next/support.py"}:
        selection.checks.add("contracts")
        selection.checks.update("public:" + family for family in ownership.families())
        selection.owners.add("new-test-runner")
        return
    if path == "tests/framework_next/test_contracts.py" or path == "tests/framework_next/README.md":
        selection.checks.add("contracts" if path.endswith(".py") else "content")
        selection.owners.add("new-test-contracts")
        return
    if path in SOURCE_FILES or path.startswith(".github/tests/") or path.startswith(".dev/standards/"):
        selection.checks.add("source-tests")
        selection.requirements.add("independent-scoped-review")
        selection.owners.add("source-governance")
        return
    if path.startswith(".github/"):
        raise GateError("unselected source/legacy pipeline owner: " + path)
    if path.startswith(RECORD_ROOT) and PurePosixPath(path).suffix in {".md", ".json", ".yaml"}:
        selection.owners.add("issue-369-record")
        return
    if path == ".dev/TEAM-GIT-FLOW-RULES.MD":
        selection.checks.add("source-tests")
        selection.requirements.add("independent-scoped-review")
        selection.owners.add("source-governance")
        return
    if (path in {"README.md", "README.en.md", "LICENSE"}
            or (path.startswith((".dev/design/", ".dev/guides/", ".dev/workflows/")) and path.lower().endswith(".md"))):
        selection.owners.add("source-prose")
        return
    raise GateError("unknown ownership; coordinator must select checks: " + path)


def select(changes, before, after):
    result = Selection()
    owners = Ownership(before), Ownership(after)
    for change in changes:
        for path, ownership in zip((change.before, change.after), owners):
            if path:
                try:
                    classify(path, ownership, result)
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
    if check == "source-tests":
        return [sys.executable, "-I", "-B", ".github/tests/test_source_gates.py", "--json"]
    if check == "contracts":
        return [sys.executable, "-I", "-B", RUNNER, "--layer", "contracts"]
    if check.startswith("public:") and check.removeprefix("public:") in FAMILIES:
        return [sys.executable, "-I", "-B", RUNNER, "--layer", "public", "--family", check.removeprefix("public:")]
    raise GateError("unknown selected command: " + check)


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
    if check.startswith("public:"):
        subject = full_sha(head.revision)
        result = launch(argv, root, timeout=120, limit=65536, separate_streams=True)
        return command_result(check, result, subject=subject)
    result = launch(argv, root, timeout=120, limit=65536)
    return command_result(check, result)


def contract_test_count(output):
    """Read #368's real unittest + JSON observations; this is not a receipt schema.

    The caller also requires exit 0, which the upstream runner guarantees only
    after zero skips and successful cleanup. Missing/contradictory output fails
    closed. Extra observation names are allowed; product assertions remain owned
    by the actual runner, not reimplemented here.
    """
    try:
        text = output.decode("utf-8").replace("\r\n", "\n")
        summaries = re.findall(r"(?m)^Ran ([1-9][0-9]*) tests? in [0-9]+(?:\.[0-9]+)?s\n\nOK$", text)
        if len(summaries) != 1 or re.search(
                r"(?m)^(?:FAILED\b|OK \(|ERROR:|FAIL:|Traceback |usage:)| \.\.\. skipped\b", text):
            raise GateError("contracts result missing, failed, skipped or ambiguous unittest summary")
        observations = [strict_json(line.encode("utf-8")) for line in text.splitlines() if line.startswith("{")]
        if any(not isinstance(item, dict) or "outcome" in item for item in observations):
            raise GateError("contracts result contains an error or malformed observation")
        runtimes = [item["runtime"] for item in observations if "runtime" in item]
        accounting = [item["fixture_accounting"] for item in observations if "fixture_accounting" in item]
        if len(runtimes) != 1 or len(accounting) != 1:
            raise GateError("contracts result missing or duplicate runtime/cleanup observation")
        runtime, fixture = runtimes[0], accounting[0]
        if (not isinstance(runtime, dict) or not all(isinstance(runtime.get(key), str) and runtime[key]
                for key in ("python", "executable", "PyYAML", "jsonschema", "referencing"))
                or not isinstance(fixture, dict)
                or not {"residue", "next_action", "observed_files", "process_total"} <= fixture.keys()
                or fixture["residue"] is not None or fixture["next_action"] is not None
                or any(type(fixture[key]) is not int or fixture[key] < 0
                       for key in ("observed_files", "process_total"))):
            raise GateError("contracts result malformed or cleanup incomplete")
        return int(summaries[0])
    except (UnicodeError, ValueError, TypeError) as exc:
        raise GateError("contracts result has malformed observation bytes") from exc


def public_family_result(family, subject, stdout, stderr):
    """Validate the fixed #373 single-family completion evidence, never an RO gate."""
    try:
        subject = full_sha(subject)
        if family not in PUBLIC_PHASES:
            raise GateError("unknown public result family")
        detail = stderr.decode("utf-8").replace("\r\n", "\n")
        if (len(re.findall(r"(?m)^Ran 1 test in [0-9]+(?:\.[0-9]+)?s\n\nOK$", detail)) != 1
                or re.search(r"(?m)^(?:FAILED\b|OK \(|ERROR:|FAIL:|Traceback |usage:|\{)| \.\.\. skipped\b", detail)
                or len(re.findall(r"(?m)^Ran ", detail)) != 1):
            raise GateError("public unittest result missing, failed, skipped or ambiguous")
        # The actual single-family arm emits exactly runtime, public_family, selection.
        lines = stdout.decode("utf-8").splitlines()
        rows = [strict_json(line.encode("utf-8")) for line in lines]
        if (len(rows) != 3 or any(not isinstance(row, dict) for row in rows)
                or set(rows[0]) != {"runtime"} or set(rows[1]) != {"public_family"}
                or set(rows[2]) != {"public_selection", "outcome", "exit", "unexecuted_families"}):
            raise GateError("public JSONL missing, duplicated, reordered or malformed")
        runtime, entry, final = rows[0]["runtime"], rows[1]["public_family"], rows[2]
        if (not isinstance(runtime, dict) or not all(isinstance(runtime.get(key), str) and runtime[key]
                for key in ("python", "executable", "PyYAML", "jsonschema", "referencing"))):
            raise GateError("public runtime observation malformed")
        if (final["public_selection"] != [family] or final["outcome"] != "passed"
                or type(final["exit"]) is not int or final["exit"] != 0
                or final["unexecuted_families"] != []):
            raise GateError("public selection mismatched or incomplete")
        fields = {"family", "outcome", "exit", "source_commit", "fixture_kind", "completed_phases",
                  "failed_phase", "blocked_before_write", "unexecuted_phases", "public_launches", "calls",
                  "fixture_accounting"}
        phases = PUBLIC_PHASES[family]
        if (not isinstance(entry, dict) or not fields <= entry.keys()
                or {"exception_type", "diagnostic", "residue", "next_action"} & entry.keys()
                or entry.get("current") is not None or entry["family"] != family
                or entry["source_commit"] != subject or entry["outcome"] != "passed"
                or type(entry["exit"]) is not int or entry["exit"] != 0
                or entry["fixture_kind"] != "direct-committed-package-resources"
                or entry["completed_phases"] != phases or entry["failed_phase"] is not None
                or entry["blocked_before_write"] is not False or entry["unexecuted_phases"] != []):
            raise GateError("public family/subject/phase completion missing or contradictory")
        calls = entry["calls"]
        if (not isinstance(calls, list) or type(entry["public_launches"]) is not int
                or not 0 < entry["public_launches"] == len(calls) <= 160):
            raise GateError("public launch count missing or inconsistent")
        # Calls are diagnostics from the pinned test runner. Check shape/count only;
        # expected negative operations may legitimately return nonzero child exits.
        # PublicCase owns request/response assertions and operation/phase coverage.
        for call in calls:
            if (not isinstance(call, dict) or call.get("phase") not in phases
                    or not isinstance(call.get("operation"), str) or not call["operation"]
                    or type(call.get("exit")) is not int
                    or not isinstance(call.get("outcome"), str) or not call["outcome"]):
                raise GateError("public call observation incomplete or malformed")
        fixture = entry["fixture_accounting"]
        counters = {"observed_files", "observed_logical_bytes", "retained_files", "retained_bytes", "process_total"}
        if (not isinstance(fixture, dict) or not counters | {"processes", "wall_seconds", "residue", "next_action"} <= fixture.keys()
                or fixture["residue"] is not None or fixture["next_action"] is not None
                or any(type(fixture[key]) is not int or fixture[key] < 0 for key in counters)
                or type(fixture["wall_seconds"]) not in (int, float) or not math.isfinite(fixture["wall_seconds"])
                or fixture["wall_seconds"] < 0 or not isinstance(fixture["processes"], dict)
                or set(fixture["processes"]) != {"git", "python", "other"}
                or any(type(value) is not int or value < 0 for value in fixture["processes"].values())
                or sum(fixture["processes"].values()) != fixture["process_total"]
                or fixture["process_total"] < len(calls)
                or fixture["retained_files"] > fixture["observed_files"]
                or fixture["retained_bytes"] > fixture["observed_logical_bytes"]):
            raise GateError("public cleanup/accounting incomplete or inconsistent")
        return {"check": "public:" + family, "status": "passed", "tests": 1, "skipped": 0,
                "family": family, "source_commit": subject, "completed_phases": phases,
                "public_launches": len(calls), "result_interface": "public-jsonl-and-unittest",
                "interface_source_commit": PUBLIC_INTERFACE_COMMIT}
    except (UnicodeError, ValueError, TypeError, KeyError, RecursionError) as exc:
        raise GateError("public result malformed") from exc


def command_result(check, result, *, subject=None):
    if result.status != "passed" or result.code != 0:
        raise GateError("selected command non-passing: " + check + ":" + result.status + ":exit=" + str(result.code))
    if check.startswith("public:"):
        if type(result.code) is not int:
            raise GateError("public process exit is not an integer")
        return public_family_result(check.removeprefix("public:"), subject, result.output, result.stderr)
    if check == "contracts":
        return {"check": check, "status": "passed", "tests": contract_test_count(result.output),
                "skipped": 0, "result_interface": "unittest-and-observations",
                "interface_source_commit": RUNNER_INTERFACE_COMMIT}
    if check != "source-tests":
        raise GateError("unknown or reserved selected result: " + check)
    receipt = strict_json(result.output)
    if (not isinstance(receipt, dict) or receipt.get("status") != "passed"
            or type(receipt.get("tests")) is not int or receipt["tests"] <= 0
            or type(receipt.get("skipped")) is not int or receipt["skipped"] != 0):
        raise GateError("selected command missing/failed/skipped result: " + check)
    return {"check": check, "status": "passed", "tests": receipt["tests"], "skipped": 0}


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
    report = {"context": "Source change gate", "status": "failed", "results": []}
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
        for check in sorted(selection.checks - {"content", "whitespace"}):
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
