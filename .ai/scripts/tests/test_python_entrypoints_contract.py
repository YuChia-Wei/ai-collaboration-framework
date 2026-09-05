#!/usr/bin/env python3
"""Contract tests for the portable Python entrypoint registry and package projection."""

from __future__ import annotations

from collections import Counter
import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[3]
REGISTRY_PATH = ROOT / ".ai/scripts/python-entrypoints.json"
PROFILE_PATH = ROOT / ".ai/distribution/profiles/dotnet-backend.yaml"

SHARED_RUNTIME_ASSETS = {
    ".ai/scripts/python-entrypoints.json",
    ".ai/scripts/python_prerequisites.py",
    ".ai/scripts/run-python-entrypoint.sh",
    ".ai/scripts/run-python-entrypoint.ps1",
}

EXPECTED_PORTABLE_PATHS = {
    ".ai/assets/skills/diagnostic-analyst/scripts/validate-diagnostic-record.py",
    ".ai/assets/skills/software-development-orchestrator/scripts/validate-software-development-orchestrator-acceptance.py",
    ".ai/scripts/observe-validation-dependencies.py",
    ".ai/scripts/plan-ai-context-package-apply.py",
    ".ai/scripts/resolve-effective-rule-packet.py",
    ".ai/scripts/validate-ai-context-payload.py",
    ".ai/scripts/validate-ai-context-target.py",
    ".ai/scripts/validate-ai-context.py",
    ".ai/scripts/validate-assessment-artifacts.py",
    ".ai/scripts/validate-dependency-versions.py",
    ".ai/scripts/validate-file-disposition-manifest.py",
    ".ai/scripts/validate-git-commits.py",
    ".ai/scripts/validate-agent-execution-guardrails.py",
    ".ai/scripts/validate-validation-lifecycle.py",
    ".ai/scripts/validate-shell-assets.py",
    ".ai/scripts/validate-software-development-orchestrator-acceptance.py",
    ".ai/scripts/validate-workflow-artifacts.py",
    ".ai/scripts/validate-workflow-handoff.py",
}

EXPECTED_STDLIB_ONLY_PATHS = {
    ".ai/assets/skills/diagnostic-analyst/scripts/validate-diagnostic-record.py",
    ".ai/scripts/resolve-ai-context-package-identity.py",
    ".ai/assets/skills/ai-context-upgrader/scripts/compare-ai-context-versions.py",
    ".ai/scripts/run-test-fixture-profile.py",
    ".ai/scripts/run-v015-package-validation-wsl.py",
    ".ai/scripts/validate-dependency-versions.py",
}

ENTRYPOINT_FIELDS = {
    "path",
    "portable",
    "dependency_profile",
    "prerequisite_exit_code",
}
EXPECTED_EXIT_CODE_TWO_PATHS = {
    ".ai/scripts/plan-ai-context-package-apply.py",
    ".ai/scripts/validate-immutable-history.py",
}
EXPECTED_EXIT_CODE_THREE_PATHS = {
    ".ai/scripts/ai_context_release_closeout.py",
}


class PythonEntrypointContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
        cls.entrypoints = cls.registry["entrypoints"]

    @staticmethod
    def write_fixture_entrypoints(root: Path, registry: dict[str, object]) -> None:
        for entrypoint in registry["entrypoints"]:  # type: ignore[index]
            path = root / entrypoint["path"]  # type: ignore[index]
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("# fixture entrypoint\n", encoding="utf-8")

    def assert_entrypoint_contract(self, registry: dict[str, object], root: Path) -> None:
        self.assertEqual("1.0", registry.get("schema_version"))
        self.assertEqual("3.11", registry.get("python_floor"))

        governed_requirements = registry.get("governed_requirements")
        self.assertIsInstance(governed_requirements, dict)
        self.assertEqual({"PyYAML"}, set(governed_requirements))
        self.assertEqual(
            {
                "version": "6.0.3",
                "import_name": "yaml",
                "requirements_path": "requirements.txt",
            },
            governed_requirements["PyYAML"],
        )

        entrypoints = registry.get("entrypoints")
        self.assertIsInstance(entrypoints, list)
        self.assertTrue(entrypoints, "entrypoint registry must not be empty")

        paths: list[str] = []
        portable_paths: set[str] = set()
        source_only_paths: set[str] = set()
        stdlib_only_paths: set[str] = set()
        exit_code_paths = {1: set(), 2: set(), 3: set()}
        for index, entrypoint in enumerate(entrypoints):
            label = f"entrypoints[{index}]"
            self.assertIsInstance(entrypoint, dict, label)
            self.assertEqual(
                ENTRYPOINT_FIELDS,
                set(entrypoint),
                f"{label}: required fields are path, portable, dependency_profile, and prerequisite_exit_code",
            )

            path = entrypoint["path"]
            portable = entrypoint["portable"]
            dependency_profile = entrypoint["dependency_profile"]
            exit_code = entrypoint["prerequisite_exit_code"]
            self.assertIsInstance(path, str, label)
            self.assertTrue(
                path.endswith(".py") and not path.startswith("/") and "\\" not in path,
                f"{label}: path must be a repository-relative .py path",
            )
            self.assertTrue((root / path).is_file(), f"{label}: referenced file is missing: {path}")
            self.assertIs(type(portable), bool, f"{label}: portable must be boolean")
            self.assertIn(
                dependency_profile,
                ([], ["PyYAML"]),
                f"{label}: dependency_profile must be [] or ['PyYAML']",
            )
            self.assertIs(type(exit_code), int, f"{label}: prerequisite_exit_code must be an integer")
            self.assertIn(exit_code, exit_code_paths, f"{label}: unsupported prerequisite_exit_code")

            paths.append(path)
            if portable:
                portable_paths.add(path)
            else:
                source_only_paths.add(path)
            if not dependency_profile:
                stdlib_only_paths.add(path)
            exit_code_paths[exit_code].add(path)

        duplicate_paths = sorted(
            path for path, occurrences in Counter(paths).items() if occurrences > 1
        )
        self.assertEqual([], duplicate_paths, f"duplicate entrypoint paths: {duplicate_paths}")
        all_paths = set(paths)
        self.assertFalse(
            portable_paths & source_only_paths,
            "portable and source-only path partitions must be mutually exclusive",
        )
        self.assertEqual(
            all_paths,
            portable_paths | source_only_paths,
            "every entrypoint must belong to exactly one portable/source-only partition",
        )
        self.assertEqual(
            EXPECTED_PORTABLE_PATHS,
            portable_paths,
            "portable approval boundary drift: "
            f"missing={sorted(EXPECTED_PORTABLE_PATHS - portable_paths)} "
            f"unexpected={sorted(portable_paths - EXPECTED_PORTABLE_PATHS)}",
        )
        self.assertEqual(
            EXPECTED_STDLIB_ONLY_PATHS,
            stdlib_only_paths,
            "stdlib-only entrypoint boundary drift: "
            f"missing={sorted(EXPECTED_STDLIB_ONLY_PATHS - stdlib_only_paths)} "
            f"unexpected={sorted(stdlib_only_paths - EXPECTED_STDLIB_ONLY_PATHS)}",
        )
        self.assertEqual(EXPECTED_EXIT_CODE_TWO_PATHS, exit_code_paths[2])
        self.assertEqual(EXPECTED_EXIT_CODE_THREE_PATHS, exit_code_paths[3])
        self.assertEqual(
            all_paths - EXPECTED_EXIT_CODE_TWO_PATHS - EXPECTED_EXIT_CODE_THREE_PATHS,
            exit_code_paths[1],
            "only the governed special paths may use a non-default prerequisite exit code",
        )

    def test_gwt_001_given_governed_registry_when_validated_then_contract_is_complete(self) -> None:
        self.assert_entrypoint_contract(self.registry, ROOT)

    def test_gwt_002_given_dotnet_profile_when_resolved_then_shared_runtime_and_portable_cli_assets_are_projected(self) -> None:
        profile = yaml.safe_load(PROFILE_PATH.read_text(encoding="utf-8"))
        runtime_entry = next(item for item in profile["entries"] if item["id"] == "ai-runtime-scripts")
        self.assertEqual(".ai/scripts/**", runtime_entry["source"])
        self.assertEqual("software-development-core", runtime_entry["component_id"])
        projected = {item["path"] for item in self.entrypoints if item["portable"]}
        self.assertEqual(EXPECTED_PORTABLE_PATHS, projected)
        for path in SHARED_RUNTIME_ASSETS | projected:
            self.assertTrue(path.startswith(".ai/scripts/") or path.startswith(".ai/assets/skills/"), path)
        self.assertIn(
            ".ai/assets/skills/software-development-orchestrator/scripts/validate-software-development-orchestrator-acceptance.py",
            projected,
        )

    def test_gwt_003_given_portable_direct_commands_when_help_is_requested_then_each_remains_callable(self) -> None:
        for item in self.entrypoints:
            if not item["portable"]:
                continue
            with self.subTest(entrypoint=item["path"]):
                result = subprocess.run(
                    [sys.executable, str(ROOT / item["path"]), "--help"],
                    cwd=ROOT,
                    capture_output=True,
                    text=True,
                    check=False,
                )
                output = result.stdout + result.stderr
                self.assertEqual(0, result.returncode, output)
                self.assertIn("usage:", output.lower(), item["path"])
                self.assertNotIn("validation passed", output.lower(), item["path"])

    def test_gwt_004_given_machine_local_validation_opt_in_when_profile_is_read_then_it_is_source_only(self) -> None:
        profile = yaml.safe_load(PROFILE_PATH.read_text(encoding="utf-8"))
        local_state = next(
            item
            for item in profile["exclusions"]
            if item["id"] == "repository-and-local-runtime-state"
        )
        self.assertEqual("source-only", local_state["classification"])
        self.assertIn(".dev/validation.local.conf", local_state["patterns"])

    def test_gwt_005_given_a_new_legal_source_only_entrypoint_when_validated_then_no_inventory_count_update_is_required(self) -> None:
        registry = copy.deepcopy(self.registry)
        registry["entrypoints"].append(
            {
                "path": ".ai/scripts/source-only-regression-fixture.py",
                "portable": False,
                "dependency_profile": ["PyYAML"],
                "prerequisite_exit_code": 1,
            }
        )

        with tempfile.TemporaryDirectory(prefix="python-entrypoint-contract-") as temporary:
            root = Path(temporary)
            self.write_fixture_entrypoints(root, registry)
            self.assert_entrypoint_contract(registry, root)

    def test_gwt_006_given_a_new_portable_entrypoint_when_validated_then_explicit_approval_boundary_update_is_required(self) -> None:
        registry = copy.deepcopy(self.registry)
        registry["entrypoints"].append(
            {
                "path": ".ai/scripts/portable-regression-fixture.py",
                "portable": True,
                "dependency_profile": ["PyYAML"],
                "prerequisite_exit_code": 1,
            }
        )

        with tempfile.TemporaryDirectory(prefix="python-entrypoint-contract-") as temporary:
            root = Path(temporary)
            self.write_fixture_entrypoints(root, registry)
            with self.assertRaisesRegex(AssertionError, "portable approval boundary drift.*portable-regression-fixture"):
                self.assert_entrypoint_contract(registry, root)

    def test_gwt_007_given_a_malformed_entrypoint_record_when_validated_then_it_fails_closed(self) -> None:
        registry = copy.deepcopy(self.registry)
        del registry["entrypoints"][0]["dependency_profile"]

        with tempfile.TemporaryDirectory(prefix="python-entrypoint-contract-") as temporary:
            root = Path(temporary)
            self.write_fixture_entrypoints(root, registry)
            with self.assertRaisesRegex(AssertionError, r"entrypoints\[0\]: required fields"):
                self.assert_entrypoint_contract(registry, root)


if __name__ == "__main__":
    unittest.main()
