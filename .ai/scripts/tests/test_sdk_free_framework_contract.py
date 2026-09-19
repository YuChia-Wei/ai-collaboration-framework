#!/usr/bin/env python3
"""GWT contracts for the framework-owned SDK-free baseline."""

from __future__ import annotations

import os
import subprocess
import tempfile
import unittest
from pathlib import Path

import yaml


REPO_ROOT = Path(__file__).resolve().parents[3]
OLD_PROVIDER = Path(
    ".ai/assets/tech-stacks/dotnet-backend/tooling/bundled-mechanical-validation"
)
RECIPE_ROOT = Path(
    ".ai/assets/tech-stacks/dotnet-backend/tooling/on-demand-mechanical-validation"
)
PROJECT_SUFFIXES = {".csproj", ".sln", ".slnx"}
DISCOVERY_SKIP_PARTS = {".git", ".tmp", "artifacts", "bin", "obj", "__pycache__"}
LOCAL_ARTIFACT_ROOTS = {(".codex", "release"), (".dev", "ai-context", "local")}
# Optional teaching projects are not framework SDK prerequisites. Keep this
# exception scoped to the owner-classified example, not every examples folder.
OPTIONAL_EXAMPLE_ROOT = Path(
    ".ai/assets/tech-stacks/dotnet-backend/examples/bdd-step-methods"
)


def supplied_core_projects(root: Path, tracked: set[str]) -> tuple[list[str], list[str]]:
    physical: list[str] = []
    for directory, child_directories, filenames in os.walk(root, topdown=True):
        relative = Path(directory).relative_to(root)
        child_directories[:] = [
            name for name in child_directories
            if name not in DISCOVERY_SKIP_PARTS
            and (*relative.parts, name) not in LOCAL_ARTIFACT_ROOTS
            and not (relative / name).is_relative_to(OPTIONAL_EXAMPLE_ROOT)
        ]
        for filename in filenames:
            path = Path(directory, filename)
            if path.suffix.lower() in PROJECT_SUFFIXES:
                physical.append(path.relative_to(root).as_posix())
    candidate_tracked = [
        path for path in tracked
        if Path(path).suffix.lower() in PROJECT_SUFFIXES
        and not Path(path).is_relative_to(OPTIONAL_EXAMPLE_ROOT)
        and (root / path).is_file()
    ]
    return sorted(physical), sorted(candidate_tracked)


def tracked_paths() -> set[str]:
    result = subprocess.run(
        ["git", "ls-files", "-z"],
        cwd=REPO_ROOT,
        capture_output=True,
        check=False,
    )
    if result.returncode:
        raise AssertionError(result.stderr.decode("utf-8", errors="replace"))
    return {
        value.decode("utf-8")
        for value in result.stdout.split(b"\0")
        if value
    }


class SdkFreeFrameworkContractTests(unittest.TestCase):
    def test_gwt_001_given_framework_tree_when_projects_are_discovered_then_no_core_projects_are_supplied(self) -> None:
        physical_projects, candidate_tracked_projects = supplied_core_projects(
            REPO_ROOT, tracked_paths()
        )

        self.assertEqual([], physical_projects)
        self.assertEqual([], candidate_tracked_projects)
        self.assertFalse((REPO_ROOT / "global.json").exists())

    def test_gwt_006_given_optional_examples_and_core_projects_when_discovered_then_only_examples_are_excluded(self) -> None:
        examples = {
            (OPTIONAL_EXAMPLE_ROOT / "DefaultBddfy/DefaultBddfy.csproj").as_posix(),
            (OPTIONAL_EXAMPLE_ROOT / "PlainXunit/PlainXunit.csproj").as_posix(),
        }
        core = {
            "Core.csproj", "Framework.sln", "src/Core/Core.slnx",
            ".ai/assets/tech-stacks/dotnet-backend/examples/other/Other.csproj",
            OPTIONAL_EXAMPLE_ROOT.as_posix() + "-extra/Unexpected.csproj",
            ".dev/ai-context/local-extra/Unexpected.csproj",
        }
        local_artifacts = {
            ".dev/ai-context/local/validation-fixture/Fixture.csproj",
            ".codex/release/extracted/Fixture.slnx",
        }
        tracked_local_artifact = ".dev/ai-context/local/AccidentallyTracked.csproj"
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for name in examples | core | local_artifacts | {"src/Untracked.csproj", tracked_local_artifact}:
                path = root / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("<Project />", encoding="utf-8")
            physical, tracked = supplied_core_projects(root, examples | core | {tracked_local_artifact})
            self.assertEqual(sorted(core | {"src/Untracked.csproj"}), physical)
            self.assertEqual(sorted(core | {tracked_local_artifact}), tracked)

    def test_gwt_002_given_mechanical_guidance_when_inspected_then_it_is_recipe_only(self) -> None:
        paths = tracked_paths()
        self.assertFalse(any(path.startswith(OLD_PROVIDER.as_posix() + "/") for path in paths))
        expected = {
            (RECIPE_ROOT / "README.md").as_posix(),
            (RECIPE_ROOT / "recipe-manifest.yaml").as_posix(),
            (RECIPE_ROOT / "diagnostic-mapping.yaml").as_posix(),
            (RECIPE_ROOT / "provider-contract.yaml").as_posix(),
            (RECIPE_ROOT / "provider-contract.schema.yaml").as_posix(),
            (RECIPE_ROOT / "templates/provider-selection.template.yaml").as_posix(),
            (RECIPE_ROOT / "templates/minimal-diagnostic-analyzer.cs.template").as_posix(),
            (RECIPE_ROOT / "templates/minimal-diagnostic-analyzer-test.cs.template").as_posix(),
            (RECIPE_ROOT / "templates/code-fix-decision.md").as_posix(),
            (RECIPE_ROOT / "recipes/analyzer-project.md").as_posix(),
            (RECIPE_ROOT / "recipes/analyzer-severity.editorconfig.snippet").as_posix(),
            (RECIPE_ROOT / "recipes/projection-registration-test.md").as_posix(),
        }
        self.assertTrue(expected.issubset(paths), expected - paths)

        manifest = yaml.safe_load(
            (REPO_ROOT / RECIPE_ROOT / "recipe-manifest.yaml").read_text(encoding="utf-8")
        )
        self.assertEqual("reference-only", manifest["delivery_state"])
        self.assertEqual("not-selected", manifest["default_selection_state"])
        self.assertFalse(manifest["compilable_payload"])
        self.assertEqual("none", manifest["framework_sdk_requirement"])
        self.assertEqual("none", manifest["activation_contract"])
        self.assertEqual(
            "official-recommended",
            manifest["provider_contract"]["recommendation_status"],
        )
        self.assertEqual(
            "unknown",
            manifest["provider_contract"]["canonical_provider_package_identity"],
        )
        self.assertEqual(
            "real-provider-unavailable",
            manifest["provider_contract"]["framework_delivery"],
        )

        mapping = yaml.safe_load(
            (REPO_ROOT / RECIPE_ROOT / "diagnostic-mapping.yaml").read_text(encoding="utf-8")
        )
        self.assertEqual(
            {f"DBA{value}" for value in range(1001, 1018)},
            {entry["diagnostic_id"] for entry in mapping["diagnostics"]},
        )
        self.assertTrue(
            all(entry["semantic_sources"] for entry in mapping["diagnostics"])
        )

    def test_gwt_003_given_required_runner_contract_when_read_then_no_dotnet_command_is_selected(self) -> None:
        runner = (REPO_ROOT / ".ai/scripts/check-all.sh").read_text(encoding="utf-8")
        registry = (REPO_ROOT / ".ai/scripts/validation-profile-registry.sh").read_text(
            encoding="utf-8"
        )
        shell_assets = yaml.safe_load(
            (REPO_ROOT / ".ai/scripts/shell-assets.yaml").read_text(encoding="utf-8")
        )

        self.assertNotIn('run_command_check "dotnet ', runner)
        self.assertNotIn('"dotnet test ', registry)
        self.assertNotIn('"dotnet" 180 dotnet', registry)
        self.assertFalse(
            any(
                command.lstrip().startswith("dotnet ")
                for command in shell_assets["check_all_required_commands"]
            )
        )
        command = "python .ai/scripts/tests/test_sdk_free_framework_contract.py -v"
        self.assertIn(command, runner)
        self.assertIn(command, shell_assets["check_all_required_commands"])

    def test_gwt_004_given_portable_workflow_when_read_then_no_sdk_setup_or_trigger_remains(self) -> None:
        workflow_path = REPO_ROOT / ".github/workflows/portable-gates.yml"
        workflow_text = workflow_path.read_text(encoding="utf-8")
        workflow = yaml.load(workflow_text, Loader=yaml.BaseLoader)

        self.assertNotIn("actions/setup-dotnet", workflow_text)
        self.assertNotIn("global-json-file", workflow_text)
        self.assertNotIn("global.json", workflow["on"]["pull_request"]["paths"])
        self.assertNotIn("tools/**", workflow["on"]["pull_request"]["paths"])

    def test_gwt_005_given_distribution_profile_when_read_then_no_sdk_seed_is_projected(self) -> None:
        profile = yaml.safe_load(
            (REPO_ROOT / ".ai/distribution/profiles/dotnet-backend.yaml").read_text(
                encoding="utf-8"
            )
        )
        self.assertNotIn(
            "repository-integration-seeds",
            {entry["id"] for entry in profile["entries"]},
        )


if __name__ == "__main__":
    unittest.main()
