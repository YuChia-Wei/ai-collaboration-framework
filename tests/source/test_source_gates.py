"""Source selector contracts using in-memory source and process-result fixtures.

No Git repositories, package builds, installations or provider calls are created.
"""
from __future__ import annotations

from contextlib import redirect_stdout
from copy import deepcopy
import importlib.util
import io
import json
import os
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).absolute().parents[2]
spec = importlib.util.spec_from_file_location("source_gate", ROOT / ".github/scripts/check-source-change.py")
gate = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = gate
spec.loader.exec_module(gate)
BASE, HEAD = "a" * 40, "b" * 40


class SyntheticTree:
    revision = HEAD

    def __init__(self, files):
        self.files = {path: value if isinstance(value, bytes) else value.encode() for path, value in files.items()}

    def read(self, path):
        if path not in self.files:
            raise gate.GateError("synthetic missing/nonregular blob: " + path)
        return self.files[path]

    def exists(self, path):
        return path in self.files


def skill(owner="lesson-author", *, version=4, tools=True):
    root = "src/skills/" + owner
    resources = {"references": ["references/use.md"], "schemas": [{"path": "schemas/record.json"}],
                 "templates": [{"path": "templates/view.md"}],
                 "tools": [{"entrypoint": "scripts/tool.py"}] if tools else []}
    metadata = {"metadata_version": version, "id": owner, "version": "0.1.0", "entrypoint": "SKILL.md",
                "dependencies": {"required": [], "optional": []}, "resources": resources}
    if version == 4:
        metadata["knowledge_consumption"] = []
    members = ["skill-package.yaml", "SKILL.md", "references/use.md", "schemas/record.json", "templates/view.md"]
    if tools:
        members.append("scripts/tool.py")
    component = {"kind": "skill", "id": owner, "version": "0.1.0", "source": root,
                 "metadata": "skill-package.yaml", "members": [{"source": member} for member in members]}
    return component, metadata


def knowledge(owner="engineering-common"):
    members = [{"path": "README.md", "kind": "index"}, {"path": "content-package.yaml", "kind": "metadata"},
               {"path": "examples/inert.py", "kind": "example"}, {"path": "rules/catalog.yaml", "kind": "rule-catalog"}]
    metadata = {"content_package_version": 1, "id": owner, "version": "0.1.0", "entrypoint": "README.md",
                "members": members, "dependencies": {"required": [], "optional": []}}
    component = {"kind": "knowledge", "id": owner, "version": "0.1.0", "source": "src/knowledge/" + owner,
                 "metadata": "content-package.yaml", "members": [{"source": member["path"]} for member in members]}
    return component, metadata


def tree(*packages):
    files = {"src/profiles/tiny.yaml": "profile_version: 2\n",
             "src/adapters/codex/skill-entry-v2.md.template": "# fixture\n"}
    for component, metadata in packages:
        root = component["source"] + "/"
        files.update({root + member["source"]: "# fixture\n" for member in component["members"]})
        files[root + component["metadata"]] = json.dumps(metadata)
    manifest = {"manifest_version": 2, "components": [component for component, _ in packages],
                "profiles": [{"id": "tiny", "path": "src/profiles/tiny.yaml"}],
                "adapters": [{"id": "codex", "source": "src/adapters/codex", "template": "skill-entry-v2.md.template",
                              "members": ["skill-entry-v2.md.template"]}]}
    files[gate.MANIFEST] = json.dumps(manifest)
    return SyntheticTree(files)


def report(suite="source", **changes):
    row = {"interface": "framework-tests/1", "suites": [suite], "outcome": "passed", "tests": 2,
           "failures": 0, "errors": 0, "skipped": 0, "duration_seconds": 0.003}
    row.update(changes)
    return json.dumps({"framework_tests": row}).encode()


class SelectionTests(unittest.TestCase):
    def selected(self, snapshot, path):
        return gate.select([gate.Change(path, path)], snapshot, snapshot)

    def test_project_readme_selects_source_checks_and_independent_review(self):
        path = ".dev/README.MD"
        before = SyntheticTree({path: "# Previous project boundary\n"})
        after = SyntheticTree({path: "# Updated project boundary\n"})
        result = gate.select([gate.Change(path, path)], before, after)
        self.assertFalse(result.errors)
        self.assertEqual(result.checks, {"content", "whitespace", "source"})
        self.assertEqual(result.owners, {"source-governance"})
        self.assertIn("independent-scoped-review", result.requirements)

    def test_sub_agent_metadata_runtime_and_moved_source_select_exact_checks(self):
        root='src/sub-agents/reviewer'
        members=['sub-agent-package.yaml','sub-agent.yaml','references/review.md','runtime/codex.toml']
        component={'kind':'sub-agent','id':'reviewer','version':'0.1.0','source':root,
                   'metadata':'sub-agent-package.yaml','members':[{'source':m} for m in members]}
        metadata={'sub_agent_package_version':1,'id':'reviewer','version':'0.1.0',
                  'entrypoint':'sub-agent.yaml','members':members,'dependencies':{'required':[],'optional':[]}}
        snapshot=tree((component,metadata))
        for member in members:
            result=self.selected(snapshot,root+'/'+member)
            self.assertFalse(result.errors)
            self.assertEqual(result.checks,{'content','whitespace'} | (
                {'schemas','distribution'} if member!='references/review.md' else set()))
        before=SyntheticTree({'.dev/agents/reviewer/sub-agent.yaml':'asset_id: reviewer\n'})
        moved=gate.select([gate.Change('.dev/agents/reviewer/sub-agent.yaml',root+'/sub-agent.yaml')],before,snapshot)
        self.assertFalse(moved.errors)
        self.assertIn('distribution',moved.checks)

    def test_source_sub_agent_profiles_keep_conditional_independent_review(self):
        name='.codex/agents/context-translator.toml'
        result=self.selected(SyntheticTree({name:'name = "context-translator"\n'}),name)
        self.assertFalse(result.errors)
        self.assertEqual(result.checks,{'content','whitespace','source','distribution'})
        self.assertIn('independent-scoped-review',result.requirements)
        other='.codex/agents/unselected.toml'
        self.assertTrue(self.selected(SyntheticTree({other:'name = "other"\n'}),other).errors)

    def test_current_skill_names_and_metadata_versions_keep_prose_lightweight(self):
        for owner in ("lesson-author", "adr-author", "pr-author", "software-development-orchestrator"):
            for version in (1, 2, 3, 4):
                snapshot = tree(skill(owner, version=version))
                with self.subTest(owner=owner, version=version):
                    result = self.selected(snapshot, "src/skills/" + owner + "/SKILL.md")
                    self.assertFalse(result.errors)
                    self.assertEqual(result.checks, {"content", "whitespace"})
                    self.assertEqual(result.owners, {owner})

    def test_skill_behavior_and_metadata_select_current_suites(self):
        snapshot = tree(skill())
        for relative in ("scripts/tool.py", "schemas/record.json", "templates/view.md", "skill-package.yaml"):
            with self.subTest(relative=relative):
                result = self.selected(snapshot, "src/skills/lesson-author/" + relative)
                expected = {"content", "whitespace", "schemas", "tools"}
                if relative == "skill-package.yaml":
                    expected.add("distribution")
                self.assertFalse(result.errors)
                self.assertEqual(result.checks, expected)

    def test_knowledge_content_is_inert_and_metadata_selects_contracts(self):
        snapshot = tree(knowledge())
        for relative in ("README.md", "examples/inert.py", "rules/catalog.yaml", "content-package.yaml"):
            with self.subTest(relative=relative):
                result = self.selected(snapshot, "src/knowledge/engineering-common/" + relative)
                expected = {"content", "whitespace"}
                if relative == "content-package.yaml":
                    expected.update({"schemas", "distribution"})
                self.assertFalse(result.errors)
                self.assertEqual(result.checks, expected)

    def test_rename_and_delete_preserve_old_behavior_selection(self):
        before, after = tree(skill()), tree(skill("adr-author"))
        old, new = "src/skills/lesson-author/scripts/tool.py", "src/skills/adr-author/scripts/tool.py"
        renamed = gate.select([gate.Change(old, new)], before, after)
        self.assertFalse(renamed.errors)
        self.assertEqual(renamed.owners, {"lesson-author", "adr-author"})
        deleted = gate.select([gate.Change(old, None)], before, SyntheticTree({}))
        self.assertFalse(deleted.errors)
        self.assertEqual(deleted.checks, {"content", "whitespace", "schemas", "tools"})
        prose = SyntheticTree({"README.md": "# moved"})
        self.assertIn("tools", gate.select([gate.Change(old, "README.md")], before, prose).checks)

    def test_manifest_versions_duplicates_and_undeclared_members_fail(self):
        path = "src/skills/lesson-author/SKILL.md"
        for version in (1, True, 2.0, "2", 3):
            snapshot = tree(skill())
            manifest = json.loads(snapshot.read(gate.MANIFEST))
            manifest["manifest_version"] = version
            snapshot.files[gate.MANIFEST] = json.dumps(manifest).encode()
            with self.subTest(version=version):
                self.assertTrue(self.selected(snapshot, path).errors)
        self.assertTrue(self.selected(tree(skill(), skill()), path).errors)
        snapshot = tree(skill())
        snapshot.files["src/skills/lesson-author/undeclared.py"] = b"# not owned"
        self.assertTrue(self.selected(snapshot, "src/skills/lesson-author/undeclared.py").errors)
        self.assertTrue(self.selected(SyntheticTree({path: "# missing manifest"}), path).errors)

    def test_metadata_identity_versions_roles_and_shapes_fail_closed(self):
        for kind in (skill, knowledge):
            component, metadata = kind()
            path = component["source"] + "/" + component["metadata"]
            version_key = "metadata_version" if component["kind"] == "skill" else "content_package_version"
            for changes in ({"id": "wrong"}, {"version": "9.0.0"}, {version_key: True}, {version_key: 99}):
                with self.subTest(kind=component["kind"], changes=changes):
                    self.assertTrue(self.selected(tree((component, {**metadata, **changes})), path).errors)
            malformed = deepcopy(metadata)
            if component["kind"] == "skill":
                malformed["resources"]["tools"] = ["not a tool declaration"]
            else:
                malformed["members"] = ["not a member declaration"]
            self.assertTrue(self.selected(tree((component, malformed)), path).errors)
            altered = deepcopy(component)
            altered["members"].append({"source": "extra.md"})
            self.assertTrue(self.selected(tree((altered, metadata)), path).errors)

    def test_declared_knowledge_dependencies_and_v4_consumption_are_resolved(self):
        common = knowledge()
        dotnet_component, dotnet = knowledge("dotnet-backend")
        dotnet["dependencies"]["required"] = [{"kind": "knowledge", "id": "engineering-common", "version": "0.1.0"}]
        consumer_component, consumer = skill("local-change-implementer", tools=False)
        consumer["knowledge_consumption"] = [{"id": "dotnet", "package": "dotnet-backend", "version": "0.1.0",
            "operations": ["implement"], "resources": ["index"], "requirement": "optional", "on_missing": "unavailable"}]
        snapshot = tree(common, (dotnet_component, dotnet), (consumer_component, consumer))
        path = consumer_component["source"] + "/skill-package.yaml"
        self.assertFalse(self.selected(snapshot, path).errors)
        self.assertFalse(self.selected(tree((consumer_component, consumer)), path).errors)  # Optional absence is explicit.
        consumer["knowledge_consumption"][0]["requirement"] = "required"
        self.assertTrue(self.selected(tree((consumer_component, consumer)), path).errors)
        consumer["knowledge_consumption"][0]["version"] = "9.0.0"
        self.assertTrue(self.selected(tree(common, (dotnet_component, dotnet), (consumer_component, consumer)), path).errors)

    def test_unknown_required_dependency_and_cycle_do_not_fall_back(self):
        first_component, first = knowledge()
        second_component, second = knowledge("dotnet-backend")
        first["dependencies"]["required"] = [{"kind": "knowledge", "id": "dotnet-backend", "version": "0.1.0"}]
        path = first_component["source"] + "/content-package.yaml"
        self.assertTrue(self.selected(tree((first_component, first)), path).errors)
        second["dependencies"]["required"] = [{"kind": "knowledge", "id": "engineering-common", "version": "0.1.0"}]
        self.assertTrue(any("cyclic" in error for error in self.selected(tree((first_component, first), (second_component, second)), path).errors))

    def test_distribution_adapters_and_manifest_select_no_build_or_native_driver(self):
        snapshot = tree(skill(), knowledge())
        for path in (gate.MANIFEST, "src/distribution/catalog.py", "tools/build-candidate.py",
                     "src/profiles/tiny.yaml", "src/adapters/codex/skill-entry-v2.md.template"):
            snapshot.files.setdefault(path, b"# fixture")
            with self.subTest(path=path):
                result = self.selected(snapshot, path)
                self.assertFalse(result.errors)
                self.assertIn("distribution", result.checks)
                self.assertFalse(result.requirements)
        snapshot.files["src/adapters/codex/undeclared.md"] = b"# undeclared"
        self.assertTrue(self.selected(snapshot, "src/adapters/codex/undeclared.md").errors)

    def test_native_source_keeps_separate_unavailable_acceptance(self):
        for path in gate.NATIVE_FILES:
            result = self.selected(SyntheticTree({path: "# native owner"}), path)
            self.assertFalse(result.errors)
            self.assertTrue({"content", "whitespace", "distribution"} <= result.checks)
            self.assertEqual(result.requirements, {"native-acceptance-unavailable:owner-selection-required", "independent-scoped-review"})

    def test_loader_and_platform_regressions_follow_their_source_owners(self):
        expected = {
            "src/tools/maintain_framework.py": {"loader", "platform"},
            "src/distribution/installation_state.py": {"platform"},
            "src/distribution/installation_io.py": {"platform"},
            "src/distribution/installation_plan.py": {"platform"},
            "src/distribution/installation.py": set(),
        }
        for path, regressions in expected.items():
            with self.subTest(path=path):
                result = self.selected(SyntheticTree({path: "# source owner"}), path)
                self.assertFalse(result.errors)
                self.assertEqual(result.checks, {"content", "whitespace", "distribution"} | regressions)
                self.assertIn("native-acceptance-unavailable:owner-selection-required", result.requirements)

    def test_owned_test_files_map_to_explicit_suites(self):
        paths = {**gate.TEST_SUITES, "tests/schemas/test_contract.py": "schemas", "tests/tools/test_lesson.py": "tools",
                 "tests/release/test_release_tools.py": "release", "tests/source/test_source_gates.py": "source"}
        for path, suite in paths.items():
            with self.subTest(path=path):
                result = self.selected(SyntheticTree({path: "# test"}), path)
                self.assertFalse(result.errors)
                self.assertEqual(result.checks, {"content", "whitespace", suite})
        path = "tests/framework_next/support.py"
        self.assertEqual(self.selected(SyntheticTree({path: "# support"}), path).checks,
                         {"content", "whitespace", "distribution", "loader", "platform"})

    def test_runner_and_source_governance_keep_scoped_review_requirement(self):
        for path in (".gitignore", ".github/workflows/source-checks.yml", ".dev/standards/SOURCE-DEVELOPMENT-POLICY.md",
                     ".dev/contracts/AGENT-EXECUTION-GUARDRAILS-CONTRACT.md",
                     ".dev/INDEX.md", ".dev/workflows/INDEX.MD"):
            with self.subTest(path=path):
                result = self.selected(SyntheticTree({path: "# source"}), path)
                self.assertFalse(result.errors)
                self.assertEqual(result.checks, {"content", "whitespace", "source"})
                self.assertEqual(result.requirements, {"independent-scoped-review"})

    def test_shared_runner_and_dependencies_select_all_supported_suites(self):
        for path in (gate.RUNNER, "requirements.txt", "tests/requirements.txt"):
            result = self.selected(SyntheticTree({path: "# runtime"}), path)
            self.assertFalse(result.errors)
            self.assertEqual(result.checks, {"content", "whitespace", *gate.SUITES})
        result = self.selected(SyntheticTree({gate.RUNNER: "# runtime"}), gate.RUNNER)
        self.assertEqual(result.requirements, {"independent-scoped-review"})

    def test_release_tools_select_only_offline_release_tests(self):
        for path in gate.RELEASE_FILES:
            result = self.selected(SyntheticTree({path: "# release"}), path)
            self.assertFalse(result.errors)
            self.assertEqual(result.checks, {"content", "whitespace", "release"})
            self.assertEqual(result.requirements, {"independent-scoped-review"})

    def test_retired_names_are_accepted_only_when_removed(self):
        for path in gate.RETIRED_TESTS:
            with self.subTest(path=path):
                before = SyntheticTree({path: "# retired"})
                result = gate.select([gate.Change(path, None)], before, SyntheticTree({}))
                self.assertFalse(result.errors)
                self.assertEqual(result.checks, {"content", "whitespace"})
                self.assertEqual(result.owners, {"retired-tests"})
                self.assertFalse(result.requirements)
                self.assertTrue(self.selected(before, path).errors)
                self.assertTrue(gate.select([gate.Change(None, path)], SyntheticTree({}), before).errors)
        old, new = "tests/framework_next/test_rc2_adapters.py", "tests/framework_next/test_adapters.py"
        result = gate.select([gate.Change(old, new)], SyntheticTree({old: "# old"}), SyntheticTree({new: "# new"}))
        self.assertFalse(result.errors)
        self.assertEqual(result.checks, {"content", "whitespace", "distribution"})

    def test_prose_stays_content_only_and_unknown_ownership_fails(self):
        for path in ("README.md", "tests/readme.md", "tests/framework_next/README.md",
                     ".dev/guides/implementation-guides/FRAMEWORK-RELEASE-DRAFT-GUIDE.md"):
            result = self.selected(SyntheticTree({path: "# prose"}), path)
            self.assertFalse(result.errors)
            self.assertEqual(result.checks, {"content", "whitespace"})
        for path in ("unknown.md", "src/new/unknown.py", "tests/framework_next/test_future.py",
                     ".github/workflows/governance.yml", ".ai/scripts/old.py", ".dev/backlog/frozen.md",
                     ".dev/workflows/2026-10-02-framework-tests/tasks.json", ".dev/contracts/unknown.py",
                     ".dev/unknown.md", ".dev/workflows/unknown.md"):
            result = self.selected(SyntheticTree({path: "# unknown"}), path)
            self.assertTrue(result.errors)
            self.assertEqual(result.checks, {"content", "whitespace"})

    def test_user_manuals_preserve_installation_review_and_reject_nonprose(self):
        for path in ("docs/README.md", "docs/skills/code-reviewer.md",
                     "docs/installation.md", "docs/knowledge-packages.md"):
            snapshot = SyntheticTree({path: "# manual"})
            for change in (gate.Change(None, path), gate.Change(path, None)):
                with self.subTest(path=path, change=change):
                    result = gate.select([change], snapshot, snapshot)
                    self.assertFalse(result.errors)
                    self.assertEqual(result.checks, {"content", "whitespace"})
                    self.assertEqual(result.owners, {"user-documentation"})
                    expected = {"independent-scoped-review"} if path in {
                        "docs/installation.md", "docs/knowledge-packages.md"} else set()
                    self.assertEqual(result.requirements, expected)
        # Moving an installation guide cannot lose the old side's review requirement.
        before = SyntheticTree({"docs/installation.md": "# install"})
        after = SyntheticTree({"docs/archive/install.md": "# install"})
        result = gate.select([gate.Change("docs/installation.md", "docs/archive/install.md")], before, after)
        self.assertFalse(result.errors)
        self.assertIn("independent-scoped-review", result.requirements)
        for path in ("docs/tool.py", "docs/selection.json", "docs-policy.md"):
            self.assertTrue(self.selected(SyntheticTree({path: "# unknown"}), path).errors)

    def test_current_declared_metadata_is_read_without_git_build_or_install(self):
        manifest = gate.strict_yaml((ROOT / gate.MANIFEST).read_bytes())
        files = {gate.MANIFEST: (ROOT / gate.MANIFEST).read_bytes()}
        for component in manifest["components"]:
            path = component["source"] + "/" + component["metadata"]
            files[path] = (ROOT / path).read_bytes()
        ownership = gate.Ownership(SyntheticTree(files))
        ownership.prove_dependencies()
        self.assertEqual(ownership.manifest()["manifest_version"], 2)
        self.assertTrue(any(component["kind"] == "knowledge" for component in manifest["components"]))


class WorkflowOwnershipTests(unittest.TestCase):
    def fixture(self, workflow_id="2026-10-02-example"):
        root = ".dev/workflows/" + workflow_id
        locator = {"schema_version": "1.0", "workflow_id": workflow_id, "workflow_kind": "software-development",
                   "title": "Fixture workflow", "owner_skill": "software-development-orchestrator",
                   "status": "in_progress", "artifact_root": root, "entrypoint": "workflow-plan.md",
                   "created_at": "2026-10-02T13:00:00+08:00", "updated_at": "2026-10-02T13:00:00+08:00",
                   "template_source": ".dev/standards/WORKFLOW-ARTIFACT-POLICY.md", "template_version": "policy-direct-1.0",
                   "branch": "codex/" + workflow_id, "base_branch": "main", "work_items": [{"provider": "github",
                    "issue": 369, "url": "https://github.com/YuChia-Wei/ai-collaboration-framework/issues/369"}]}
        task = {key: locator[key] for key in ("workflow_id", "owner_skill", "status", "created_at", "updated_at", "template_source", "template_version")}
        task.update(task_id="T1", model="fixture-model", reasoning_effort="fixture-effort")
        files = {root + "/workflow.yaml": json.dumps(locator), root + "/workflow-plan.md": "# bounded plan",
                 root + "/tasks/T1.json": json.dumps(task),
                 "src/skills/software-development-orchestrator/skill-package.yaml": "id: software-development-orchestrator\n"}
        return root, locator, task, SyntheticTree(files)

    def test_add_modify_delete_and_cross_workflow_rename_use_each_pinned_locator(self):
        root, _, _, before = self.fixture()
        other, _, _, after = self.fixture("2026-10-02-other")
        for relative in ("workflow.yaml", "workflow-plan.md", "tasks/T1.json"):
            old, new = root + "/" + relative, other + "/" + relative
            for change, left, right in ((gate.Change(old, old), before, before),
                    (gate.Change(None, new), SyntheticTree({}), after),
                    (gate.Change(old, None), before, SyntheticTree({})),
                    (gate.Change(old, new), before, after)):
                with self.subTest(change=change):
                    result = gate.select([change], left, right)
                    self.assertFalse(result.errors)
                    self.assertEqual(result.checks, {"content", "whitespace"})
                    self.assertTrue(all(owner.startswith("source-workflow:") for owner in result.owners))

    def test_missing_mismatched_unsafe_or_unbound_locator_fails_closed(self):
        for changes in ({"workflow_id": "wrong"}, {"artifact_root": "elsewhere"}, {"entrypoint": "../outside.md"},
                        {"schema_version": 1}, {"branch": "main"}, {"work_items": []}, {"owner_skill": "../other"},
                        {"created_at": "2026-10-02T13:00:00"}, {"work_items": [{"provider": "github", "issue": True}]}):
            root, locator, _, snapshot = self.fixture()
            snapshot.files[root + "/workflow.yaml"] = json.dumps({**locator, **changes}).encode()
            with self.subTest(changes=changes):
                self.assertTrue(gate.select([gate.Change(None, root + "/tasks/T1.json")], SyntheticTree({}), snapshot).errors)
        root, _, _, snapshot = self.fixture()
        del snapshot.files[root + "/workflow.yaml"]
        self.assertTrue(gate.select([gate.Change(None, root + "/workflow-plan.md")], SyntheticTree({}), snapshot).errors)

    def test_task_identity_terminal_result_and_unknown_formats_fail_closed(self):
        for changes in ({"workflow_id": "wrong"}, {"task_id": "T2"}, {"model": ""}, {"status": "completed"},
                        {"updated_at": False}, {"owner_skill": "missing-skill"}):
            root, _, task, snapshot = self.fixture()
            path = root + "/tasks/T1.json"
            snapshot.files[path] = json.dumps({**task, **changes}).encode()
            with self.subTest(changes=changes):
                self.assertTrue(gate.select([gate.Change(None, path)], SyntheticTree({}), snapshot).errors)
        root, _, task, snapshot = self.fixture()
        for relative in ("tasks.json", "run.py", "other.yaml", "tasks/T1.yaml"):
            path = root + "/" + relative
            snapshot.files[path] = b"{}"
            self.assertTrue(gate.select([gate.Change(None, path)], SyntheticTree({}), snapshot).errors)
        path = root + "/tasks/T1.json"
        task.update(status="completed", result_summary="Bounded outcome recorded", finding_status="addressed")
        snapshot.files[path] = json.dumps(task).encode()
        self.assertFalse(gate.select([gate.Change(None, path)], SyntheticTree({}), snapshot).errors)

    def test_retained_issue_refs_spelling_does_not_require_historical_issue_whitelist(self):
        root, locator, _, snapshot = self.fixture()
        del locator["work_items"]
        locator["issue_refs"] = ["#427"]
        path = root + "/workflow.yaml"
        snapshot.files[path] = json.dumps(locator).encode()
        self.assertFalse(gate.select([gate.Change(path, path)], snapshot, snapshot).errors)


class SafetyTests(unittest.TestCase):
    def test_git_padded_rename_scores_preserve_before_after_and_next_record(self):
        expected = [gate.Change("old.md", "new.md"), gate.Change("another.md", "another.md")]
        for score in (b"000", b"001", b"095", b"099", b"100", b"0", b"95"):
            with self.subTest(score=score):
                self.assertEqual(gate.parse_diff(b"R" + score + b"\0old.md\0new.md\0M\0another.md\0"), expected)
        for score in (b"101", b"999", b"0100", b"0000", b"-01", b"9a5"):
            with self.subTest(score=score), self.assertRaisesRegex(gate.GateError, "unsupported diff status"):
                gate.parse_diff(b"R" + score + b"\0old.md\0new.md\0")

    def test_diff_parse_bounds_and_path_rejection(self):
        self.assertEqual(gate.parse_diff(b"R100\0old.md\0new.md\0D\0gone.md\0A\0added.md\0"),
                         [gate.Change("old.md", "new.md"), gate.Change("gone.md", None), gate.Change(None, "added.md")])
        for data in (b"M\0x", b"R100\0x\0", b"U\0x\0", b"M\0../x\0", b"M\0x\nname\0",
                     b"M\0x\0" * (gate.MAX_PATHS + 1)):
            with self.subTest(data=data[:20]), self.assertRaises(gate.GateError):
                gate.parse_diff(data)
        for path in ("../x", "/tmp/x", "C:/x", "x\\y", "a//b", "a/./b", "x\0y", ":(glob)*"):
            with self.assertRaises(gate.GateError):
                gate.safe_path(path)
        for value in ("HEAD", "a" * 39, "A" * 40, "0" * 40, "a" * 40 + ";echo x"):
            with self.assertRaises(gate.GateError):
                gate.full_sha(value)

    def test_git_tree_requires_exact_commit_identity(self):
        with patch.object(gate, "bounded_run", return_value=gate.Outcome("passed", 0, (BASE + "\n").encode())) as launch:
            self.assertEqual(gate.GitTree(ROOT, BASE).revision, BASE)
            self.assertEqual(launch.call_args.args[0][:3], ["git", "--no-pager", "rev-parse"])
            with self.assertRaises(gate.GateError):
                gate.GitTree(ROOT, HEAD)

    def test_git_tree_mode_size_and_entry_ambiguity_fail_before_blob_read(self):
        snapshot = object.__new__(gate.GitTree)
        snapshot.root, snapshot.revision = ROOT, HEAD
        for entry in (None, ["120000", "blob", BASE], ["160000", "commit", BASE], ["040000", "tree", BASE]):
            with patch.object(snapshot, "entry", return_value=entry), patch.object(snapshot, "git") as git:
                with self.assertRaises(gate.GateError):
                    snapshot.read("x")
                git.assert_not_called()
        with patch.object(snapshot, "entry", return_value=["100644", "blob", BASE]), patch.object(snapshot, "git", return_value=str(gate.MAX_BLOB + 1).encode()) as git:
            with self.assertRaises(gate.GateError):
                snapshot.read("x")
            self.assertEqual(git.call_count, 1)
        record = ("100644 blob " + BASE + "\tx\0").encode()
        with patch.object(snapshot, "git", return_value=record * 2), self.assertRaises(gate.GateError):
            snapshot.entry("x")

    def test_content_links_rename_and_syntax_are_checked(self):
        before = SyntheticTree({"README.md": "[old](historically-missing.md)"})
        after = SyntheticTree({"README.md": "[old](historically-missing.md) [new](new.md)", "new.md": "# file"})
        gate.content_checks([gate.Change("README.md", "README.md")], before, after)
        del after.files["new.md"]
        with self.assertRaises(gate.GateError):
            gate.content_checks([gate.Change("README.md", "README.md")], before, after)
        with self.assertRaises(gate.GateError):
            gate.content_checks([gate.Change("old.md", "dir/new.md")], SyntheticTree({"old.md": "[doc](target.md)"}),
                                SyntheticTree({"dir/new.md": "[doc](target.md)", "target.md": "# outside"}))
        for path, value in (("x.py", "def !"), ("x.json", "{"), ("x.md", "<<<<<<< conflict\n")):
            with self.assertRaises((gate.GateError, ValueError, SyntaxError)):
                gate.content_checks([gate.Change(None, path)], SyntheticTree({}), SyntheticTree({path: value}))

    def test_strict_json_yaml_and_bounded_depth(self):
        for data in (b'{"x":1,"x":2}', b'{"x":NaN}'):
            with self.assertRaises(gate.GateError):
                gate.strict_json(data)
        for data in (b"a: 1\na: 2", b"a: [", ("a: " + "[" * 65 + "0" + "]" * 65).encode()):
            with self.assertRaises(gate.GateError):
                gate.strict_yaml(data)
        self.assertEqual(gate.strict_yaml(b"a: &item [x]\nb: *item")["b"], ["x"])

    def test_bounded_child_capture_failure_and_timeout(self):
        result = gate.bounded_run([sys.executable, "-I", "-B", "-c",
                                  'import sys; print("stdout"); print("stderr", file=sys.stderr)'], ROOT, separate_streams=True)
        self.assertEqual((result.status, result.output.strip(), result.stderr.strip()), ("passed", b"stdout", b"stderr"))
        result = gate.bounded_run([sys.executable, "-I", "-B", "-c", 'print("x" * 20000)'], ROOT, limit=1024)
        self.assertEqual((result.status, len(result.output)), ("output-limit", 1024))
        result = gate.bounded_run([sys.executable, "-I", "-B", "-c", "raise SystemExit(7)"], ROOT)
        self.assertEqual((result.status, result.code), ("failed", 7))
        result = gate.bounded_run([sys.executable, "-I", "-B", "-c", "import time; time.sleep(10)"], ROOT, timeout=0.05)
        self.assertEqual((result.status, result.code), ("timed-out", None))


class RunnerContractTests(unittest.TestCase):
    def test_exact_suite_argv_has_real_isolation_flags(self):
        for suite in gate.SUITES:
            self.assertEqual(gate.command_for(suite), [sys.executable, "-I", "-B", "tests/run.py", "--suite", suite])
        for name in ("unknown", "contracts", "public:lesson", "native-windows"):
            with self.assertRaises(gate.GateError):
                gate.command_for(name)

    def test_complete_report_for_exact_suite_passes(self):
        for suite in gate.SUITES:
            result = gate.command_result(suite, gate.Outcome("passed", 0, report(suite), b"unittest diagnostics"))
            self.assertEqual((result["check"], result["tests"], result["result_interface"]), (suite, 2, "framework-tests/1"))

    def test_nonzero_timeout_unavailable_and_noninteger_exits_cannot_pass(self):
        for status, code in (("failed", 1), ("passed", 2), ("passed", False), ("passed", 0.0),
                             ("timed-out", None), ("output-limit", 0), ("skipped", 0), ("cancelled", 0),
                             ("unavailable", None), ("output-stream-not-closed", 0)):
            with self.subTest(status=status, code=code), self.assertRaises(gate.GateError):
                gate.command_result("source", gate.Outcome(status, code, report()))

    def test_missing_extra_duplicate_or_malformed_report_cannot_pass(self):
        invalid = [b"", b"{}", b"[]", b"null", b"{", b"\xff", report() + report(), b"noise\n" + report(),
                   b'{"framework_tests":{},"framework_tests":{}}', b'{"framework_tests":null}',
                   json.dumps({"framework_tests": json.loads(report())["framework_tests"], "extra": True}).encode()]
        for field in json.loads(report())["framework_tests"]:
            data = json.loads(report())
            del data["framework_tests"][field]
            invalid.append(json.dumps(data).encode())
        data = json.loads(report())
        data["framework_tests"]["extra"] = True
        invalid.append(json.dumps(data).encode())
        for data in invalid:
            with self.subTest(data=data[:80]), self.assertRaises(gate.GateError):
                gate.command_result("source", gate.Outcome("passed", 0, data))

    def test_wrong_selection_counts_duration_and_false_success_are_rejected(self):
        values = {"interface": ("framework-tests/0", None), "suites": ([], ["tools"], ["source", "tools"], "source"),
                  "outcome": ("failed", "skipped", True), "tests": (0, -1, True, 2.0, "2"),
                  "failures": (1, -1, True, None), "errors": (1, -1, False, "0"), "skipped": (1, -1, False, 0.0),
                  "duration_seconds": (-1, True, None, "0", float("inf"), float("nan"), 10 ** 1000)}
        for field, choices in values.items():
            for value in choices:
                with self.subTest(field=field, value=str(value)[:30]), self.assertRaises(gate.GateError):
                    gate.command_result("source", gate.Outcome("passed", 0, report(**{field: value})))

    def test_selected_entry_is_pinned_and_launch_uses_separate_streams(self):
        path = "tests/source/test_source_gates.py"
        snapshot = SyntheticTree({path: (ROOT / path).read_bytes()})
        with patch.object(gate, "RUNNER", path), patch.object(gate, "bounded_run"):
            calls = []
            def launch(argv, root, **options):
                calls.append((argv, root, options))
                return gate.Outcome("passed", 0, report())
            result = gate.run_selected("source", ROOT, snapshot, launch=launch)
            self.assertEqual(result["source_commit"], HEAD)
            self.assertTrue(calls[0][2]["separate_streams"])
            snapshot.files[path] += b"# drift"
            with self.assertRaises(gate.GateError):
                gate.run_selected("source", ROOT, snapshot, launch=launch)
            self.assertEqual(len(calls), 1)

    def test_missing_or_linked_entry_and_invalid_subject_fail_before_launch(self):
        path = "tests/source/test_source_gates.py"
        snapshot = SyntheticTree({path: (ROOT / path).read_bytes()})
        with patch.object(gate, "RUNNER", path), patch.object(gate, "bounded_run") as launch:
            with self.assertRaises(gate.GateError):
                gate.run_selected("source", ROOT, SyntheticTree({}), launch=launch)
            with patch.object(Path, "is_symlink", return_value=True), self.assertRaises(gate.GateError):
                gate.run_selected("source", ROOT, snapshot, launch=launch)
            snapshot.revision = "HEAD"
            with self.assertRaises(gate.GateError):
                gate.run_selected("source", ROOT, snapshot, launch=launch)
            launch.assert_not_called()


class EventAndCheckoutTests(unittest.TestCase):
    def test_event_base_head_and_allowed_actions_remain_exact(self):
        for action in ("opened", "synchronize", "reopened", "edited", "ready_for_review"):
            event = {"action": action, "pull_request": {"draft": True, "base": {"ref": "main", "sha": BASE}, "head": {"sha": HEAD}}}
            gate.validate_event(event, "pull_request", BASE, HEAD)
            with self.assertRaises(gate.GateError):
                gate.validate_event(event, "pull_request", HEAD, HEAD)
        for event_name in ("pull_request_target", "push", "merge_group", "workflow_dispatch"):
            with self.assertRaises(gate.GateError):
                gate.validate_event(event, event_name, BASE, HEAD)

    def test_wrong_or_dirty_checkout_stops_before_selected_execution(self):
        for actual_head, dirty in ((BASE, b""), (HEAD, b"changed.py\n")):
            def git(*args, **kwargs):
                return (actual_head + "\n").encode() if args[0] == "rev-parse" else dirty
            snapshot = SyntheticTree({})
            snapshot.git = git
            output = io.StringIO()
            with patch.object(gate, "GitTree", return_value=snapshot), patch.object(gate, "run_selected") as launch, \
                    patch.dict(os.environ, {"GITHUB_ACTIONS": "false"}), redirect_stdout(output):
                self.assertEqual(gate.main(["--base", BASE, "--head", HEAD]), 1)
            launch.assert_not_called()
            self.assertEqual(json.loads(output.getvalue())["status"], "failed")

    def test_workflow_has_selected_windows_environment_and_stays_credential_free(self):
        raw = (ROOT / ".github/workflows/source-checks.yml").read_bytes()
        document = gate.strict_yaml(raw)
        events = document.get("on", document.get(True))
        self.assertEqual(set(events), {"pull_request"})
        self.assertFalse({"paths", "paths-ignore"} & events["pull_request"].keys())
        self.assertEqual(document["permissions"], {})
        job = document["jobs"]["source-change"]
        self.assertEqual(job["runs-on"], "windows-latest")
        self.assertEqual(job["permissions"], {"contents": "read"})
        self.assertNotIn("if", job)
        self.assertEqual(job["steps"][-1]["if"], "always()")
        for step in job["steps"]:
            self.assertNotIn("continue-on-error", step)
            if step.get("uses", "").startswith("actions/checkout@"):
                self.assertIs(step["with"]["persist-credentials"], False)
            if "run" in step:
                self.assertNotIn("secrets.", step["run"])
        self.assertTrue(job["steps"][0]["uses"].startswith("actions/setup-python@"))
        self.assertEqual(job["steps"][0]["with"]["python-version"], "3.13")
        self.assertIn(b"tests/requirements.txt", raw)

    def test_source_check_report_never_claims_merge_admission(self):
        snapshot = SyntheticTree({})
        snapshot.git = lambda *args, **kwargs: (HEAD + "\n").encode() if args[0] == "rev-parse" else b""
        output = io.StringIO()
        selected = gate.Selection(requirements={"independent-scoped-review"})
        with patch.object(gate, "GitTree", return_value=snapshot), patch.object(gate, "select", return_value=selected), \
                patch.dict(os.environ, {"GITHUB_ACTIONS": "false"}), redirect_stdout(output):
            self.assertEqual(gate.main(["--base", BASE, "--head", HEAD]), 0)
        document = json.loads(output.getvalue())
        self.assertEqual(document["status"], "passed")
        self.assertEqual(document["admission_status"], "not-evaluated")
        self.assertEqual(document["admission_requirements"], ["independent-scoped-review"])


if __name__ == "__main__":
    unittest.main()
