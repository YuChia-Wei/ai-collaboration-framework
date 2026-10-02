"""Tiny authored records and imports bound to actual source packages.

No copied packages, Git repositories, provider calls or renderer-derived oracles.
"""
from __future__ import annotations

from functools import lru_cache
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = {
    "lesson-author": "lesson.py", "adr-author": "adr.py",
    "local-backlog": "local_backlog.py", "pr-author": "pr.py",
    "problem-frame-author": "problem_frame.py",
}
FAMILIES = tuple(SCRIPTS)
STAMP = "2026-01-01T00:00:00+00:00"


def encoded(value):
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8")


def digest(raw):
    return sha256(raw).hexdigest()


def package(family):
    return ROOT / "src" / "skills" / family


@lru_cache(maxsize=None)
def source_tool(family, script):
    spec = importlib.util.spec_from_file_location(
        "tools_test_" + family.replace("-", "_") + "_" + script.replace(".", "_"),
        package(family) / "scripts" / script)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def tool(family):
    return source_tool(family, SCRIPTS[family])


def content(family):
    if family == "lesson-author":
        return {"title": "觀察 *重試* <tag>", "observation": "First observation\nSecond observation",
                "evidence": [{"source": "fixture:evidence", "note": "Observed once"}],
                "conclusion": "Keep the original outcome", "applies_when": ["Local caller"],
                "does_not_apply_when": [], "confidence": "supported", "follow_up": ["Repeat with evidence"]}
    if family == "adr-author":
        return {"title": "選擇 *方案* <tag>", "context": "First context\nSecond context",
                "decision_drivers": ["Keep evidence"], "options": [
                    {"id": "A", "summary": "Retain local state", "benefits": ["Offline access"], "costs": []},
                    {"id": "B", "summary": "Use remote state", "benefits": [], "costs": ["Network required"]}],
                "consequences": ["One source of truth"], "evidence": [{"source": "fixture:comparison", "note": "Both evaluated"}],
                "applies_when": ["Single owner"], "does_not_apply_when": []}
    value = {"title": "工作 *項目* <tag>", "summary": "First summary\nSecond summary",
             "references": [{"kind": "text", "target": "fixture:reference", "relationship": "related"}]}
    if family == "local-backlog":
        value["acceptance"] = ["Keep state\nKeep evidence"]
    else:
        value["validation"] = [{"id": "V1", "command": "python check", "disposition": "deferred",
                                "subject_head": "b" * 40, "subject_diff_sha256": "f" * 64,
                                "evidence": [], "reason": "Await caller evidence"}]
        value["provider_target"] = {"provider": "github", "host": "github.com", "repository": "fixture/example",
                                    "base_ref": "main", "head_ref": "fixture"}
    return value


def record(family):
    """Fixed records authored independently of production constructors."""
    if family == "problem-frame-author":
        return cbf_record()
    prefix = {"lesson-author": "lesson", "adr-author": "adr", "local-backlog": "work", "pr-author": "pr"}[family]
    value = {"schema_version": "2.0.0" if family == "lesson-author" else "1.0.0",
             "kind": "local-backlog" if family == "local-backlog" else prefix,
             "owner": "project", "id": prefix + "-" + "1" * 32, "created_at": STAMP, "updated_at": STAMP}
    if family in ("lesson-author", "adr-author"):
        value.update(content=content(family), status="candidate" if family == "lesson-author" else "draft",
                     revision=1, successor=None, decision=None, history=[], provenance=[])
    else:
        value.update(content(family))
        if family == "local-backlog":
            value.update(state="draft", writable_authority="local", state_reason="Created as candidate work.", completion_evidence=[])
        else:
            value.update(state="prepared", subject={"object_format": "sha1", "base_commit": "a" * 40,
                         "head_commit": "b" * 40, "merge_base": "a" * 40, "base_tree": "c" * 40,
                         "head_tree": "d" * 40, "diff_sha256": "f" * 64, "git_version": "fixture git",
                         "diff_recipe": "pr.diff/v1"})
    return value


def cbf_record():
    return {"family": "problem-frame.cbf", "schema_version": "1.0.0", "id": "cbf-" + "1" * 32,
            "frame_key": "fixture-frame", "title": "問題 *框架* <tag>", "derived_from": None,
            "sources": [{"id": "SRC1", "kind": "requirement", "reference": "fixture:intent", "revision": None,
                         "locator": "Intent section", "sha256": None, "authority": "proposed", "authority_reference": None}],
            "statements": [
                {"id": "ACTOR1", "category": "actor", "text": "A caller", "basis": "stated", "source_ids": ["SRC1"]},
                {"id": "CMD1", "category": "command", "text": "Request a value", "basis": "stated", "source_ids": ["SRC1"]},
                {"id": "DOMAIN1", "category": "controlled-domain", "text": "Local state", "basis": "stated", "source_ids": ["SRC1"]}],
            "scenarios": [{"id": "SC1", "title": "Observe one result", "source_ids": ["SRC1"],
                           "given": ["First line\nSecond line"], "when": ["Caller requests"],
                           "then": [{"id": "THEN1", "text": "Exact value unresolved", "basis": "unresolved",
                                     "source_ids": [], "statement_ids": ["CMD1"]}],
                           "tests_anchor": [{"reference": "fixture:test", "locator": "Case one"}]}],
            "open_questions": [{"id": "Q1", "text": "Which value?", "related_ids": ["THEN1"]}]}


class ToolCase(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="framework-tools-")
        self.addCleanup(temporary.cleanup)
        self.project = Path(temporary.name).resolve()

    def request(self, family, operation="inspect", **extra):
        return {"operation": operation, "project_root": str(self.project), "package_root": str(package(family)), **extra}

    def binding(self, family, operation="inspect", **extra):
        module = tool(family)
        request = self.request(family, operation, **extra)
        if family == "problem-frame-author":
            return module.configure(module.Inputs(), request)
        return module.Binding(request)

    def provision(self, family):
        module = tool(family)
        explained = self.binding(family, "explain")
        store = explained["store"] if family == "problem-frame-author" else explained.store
        store.mkdir(parents=True, exist_ok=True)
        return module, self.binding(family)

    def persist(self, family, value=None):
        module, binding = self.provision(family)
        value = record(family) if value is None else value
        if family == "problem-frame-author":
            path = binding["store"] / (value["id"] + ".cbf.json")
        else:
            path = binding.record_path(module.reference(value))
        path.write_bytes(encoded(value))
        return module, binding, value, path

    def write_json(self, name, value):
        path = self.project / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(encoded(value))
        return path

    def require_native(self, module, store):
        """Probe the actual backend; never replace native publication with a fake."""
        try:
            probe = getattr(module, "local_write_backend", None) or module.local_backend
            probe(store)
        except module.Fault as error:
            diagnostic = error.diagnostic() if callable(error.diagnostic) else error.diagnostic
            if error.outcome in ("unsupported", "unavailable") and diagnostic["code"] == "filesystem":
                self.skipTest("Native publication unavailable on actual temporary filesystem: " + diagnostic["message"])
            raise

    def assert_fault(self, module, action, outcome="invalid-input", code=None):
        with self.assertRaises(module.Fault) as caught:
            action()
        self.assertEqual(caught.exception.outcome, outcome)
        if code is not None:
            diagnostic = caught.exception.diagnostic() if callable(caught.exception.diagnostic) else caught.exception.diagnostic
            self.assertEqual(diagnostic["code"], code)
