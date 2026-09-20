#!/usr/bin/env python3
"""Contract tests for source-only Python entrypoint prerequisite behavior."""

from __future__ import annotations

import ast
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from source_like_entrypoint_fixture import (
    copy_source_like_entrypoints,
    fixture_tree_snapshot,
)


ROOT = Path(__file__).resolve().parents[3]
REGISTRY_PATH = ROOT / ".ai/scripts/python-entrypoints.json"
STDLIB_COMPARE = ".ai/assets/skills/ai-context-upgrader/scripts/compare-ai-context-versions.py"
STDLIB_FIXTURE_PROFILE = ".ai/scripts/run-test-fixture-profile.py"
STDLIB_PACKAGE_IDENTITY = ".ai/scripts/resolve-ai-context-package-identity.py"
STDLIB_V015_WSL_RUNNER = ".ai/scripts/run-v015-package-validation-wsl.py"
PYYAML_SOURCE_ONLY_SENTINEL = ".ai/scripts/validate-ai-context-package.py"
SOURCE_GOVERNANCE_ENTRYPOINT = ".ai/scripts/validate-source-governance.py"
DIRECT_ENTRYPOINT_TIMEOUT_SECONDS = 15


def imports_nonstdlib_module(statement: ast.AST) -> bool:
    """Inspect imports executable before the guard, including control-flow bodies."""
    if isinstance(statement, ast.Import):
        modules = [alias.name.partition(".")[0] for alias in statement.names]
    elif isinstance(statement, ast.ImportFrom):
        if statement.level:
            return True
        modules = [(statement.module or "").partition(".")[0]]
    elif isinstance(statement, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda)):
        return False  # A function body is not executed merely by defining it.
    else:
        return any(imports_nonstdlib_module(child) for child in ast.iter_child_nodes(statement))
    return any(
        module not in {"__future__", "python_prerequisites"}
        and module not in sys.stdlib_module_names
        for module in modules
    )


def is_direct_guard_call(statement: ast.stmt, entrypoint: str) -> bool:
    """Match the shared prerequisite guard bound to one registry entrypoint."""
    if not isinstance(statement, ast.Expr) or not isinstance(statement.value, ast.Call):
        return False
    call = statement.value
    return (
        isinstance(call.func, ast.Name)
        and call.func.id == "guard_direct_entrypoint"
        and len(call.args) == 1
        and not call.keywords
        and isinstance(call.args[0], ast.Constant)
        and call.args[0].value == entrypoint
    )


class PythonSourceEntrypointTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
        cls.entrypoints = registry["entrypoints"]
        cls.source_only = [item for item in cls.entrypoints if not item["portable"]]
        cls.portable = [item for item in cls.entrypoints if item["portable"]]
        cls.pyyaml_source_only = [item for item in cls.source_only if item["dependency_profile"] == ["PyYAML"]]
        cls.stdlib_source_only = [item for item in cls.source_only if not item["dependency_profile"]]

    def assert_pyyaml_entrypoint_uses_shared_guard(self, item: dict[str, object]) -> None:
        """Prove a registered entrypoint reaches the common guard before domain imports."""
        entrypoint = item["path"]
        self.assertIsInstance(entrypoint, str)
        tree = ast.parse((ROOT / entrypoint).read_text(encoding="utf-8"), filename=entrypoint)
        guard_imports = [
            index
            for index, statement in enumerate(tree.body)
            if isinstance(statement, ast.ImportFrom)
            and statement.module == "python_prerequisites"
            and statement.level == 0
            and any(alias.name == "guard_direct_entrypoint" and alias.asname is None for alias in statement.names)
        ]
        guard_calls = [
            index
            for index, statement in enumerate(tree.body)
            if is_direct_guard_call(statement, entrypoint)
        ]
        with self.subTest(entrypoint=entrypoint):
            self.assertEqual(1, len(guard_imports), "shared guard must be directly imported once")
            self.assertEqual(1, len(guard_calls), "shared guard must be called once with the registry path")
            self.assertLess(guard_imports[0], guard_calls[0], "shared guard must be imported before use")
            self.assertFalse(
                any(imports_nonstdlib_module(statement) for statement in tree.body[:guard_calls[0]]),
                "shared guard must run before domain or third-party imports",
            )

    def test_gwt_001_given_source_only_registry_when_help_is_requested_then_each_direct_cli_remains_callable(self) -> None:
        all_paths = {item["path"] for item in self.entrypoints}
        source_only_paths = {item["path"] for item in self.source_only}
        portable_paths = {item["path"] for item in self.portable}
        pyyaml_source_only_paths = {item["path"] for item in self.pyyaml_source_only}
        stdlib_source_only_paths = {item["path"] for item in self.stdlib_source_only}
        self.assertEqual(
            len(self.entrypoints),
            len(all_paths),
            "source entrypoint registry paths must be unique",
        )
        self.assertTrue(source_only_paths, "source-only entrypoint partition must not be empty")
        self.assertFalse(portable_paths & source_only_paths)
        self.assertEqual(all_paths, portable_paths | source_only_paths)
        self.assertFalse(pyyaml_source_only_paths & stdlib_source_only_paths)
        self.assertEqual(source_only_paths, pyyaml_source_only_paths | stdlib_source_only_paths)
        environment = os.environ.copy()
        environment["PYTHONDONTWRITEBYTECODE"] = "1"
        for item in self.source_only:
            entrypoint = item["path"]
            self.assertIsInstance(entrypoint, str)
            with self.subTest(entrypoint=entrypoint):
                try:
                    result = subprocess.run(
                        [sys.executable, "-B", str(ROOT / entrypoint), "--help"],
                        cwd=ROOT,
                        env=environment,
                        capture_output=True,
                        text=True,
                        encoding="utf-8",
                        errors="replace",
                        check=False,
                        timeout=DIRECT_ENTRYPOINT_TIMEOUT_SECONDS,
                    )
                except subprocess.TimeoutExpired as error:
                    self.fail(
                        f"{entrypoint} did not return from --help within "
                        f"{DIRECT_ENTRYPOINT_TIMEOUT_SECONDS}s: {error}"
                    )
                self.assertEqual(0, result.returncode, result.stdout + result.stderr)
                self.assertIn("usage:", result.stdout)

    def test_gwt_001a_given_source_governance_help_when_invoked_then_it_short_circuits_before_governance_body_or_fixture_mutation(self) -> None:
        environment = os.environ.copy()
        environment["PYTHONDONTWRITEBYTECODE"] = "1"
        environment.pop("PYTHONPATH", None)
        with tempfile.TemporaryDirectory(prefix="source-governance-help-") as temporary:
            fixture_root = Path(temporary)
            copy_source_like_entrypoints(ROOT, fixture_root, (SOURCE_GOVERNANCE_ENTRYPOINT,))
            before = fixture_tree_snapshot(fixture_root)
            try:
                fixture = subprocess.run(
                    [
                        sys.executable,
                        "-B",
                        str(fixture_root / SOURCE_GOVERNANCE_ENTRYPOINT),
                        "--help",
                    ],
                    cwd=fixture_root,
                    env=environment,
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                    check=False,
                    timeout=DIRECT_ENTRYPOINT_TIMEOUT_SECONDS,
                )
            except subprocess.TimeoutExpired as error:
                self.fail(
                    f"fixture {SOURCE_GOVERNANCE_ENTRYPOINT} did not return from --help within "
                    f"{DIRECT_ENTRYPOINT_TIMEOUT_SECONDS}s: {error}"
                )
            self.assertEqual(0, fixture.returncode, fixture.stdout + fixture.stderr)
            self.assertIn("usage:", fixture.stdout)
            self.assertEqual(before, fixture_tree_snapshot(fixture_root))

    def test_gwt_002_given_shadowed_yaml_when_source_only_pyyaml_clis_run_then_each_blocks_before_target_body_or_writes(self) -> None:
        self.assertTrue(self.pyyaml_source_only, "PyYAML source-only entrypoint set must not be empty")
        for item in self.pyyaml_source_only:
            self.assert_pyyaml_entrypoint_uses_shared_guard(item)
        self.assertIn(
            PYYAML_SOURCE_ONLY_SENTINEL,
            {item["path"] for item in self.pyyaml_source_only},
            "the representative source-only PyYAML entrypoint must remain registered",
        )
        entrypoints: list[str] = []
        for item in self.pyyaml_source_only:
            entrypoint = item["path"]
            self.assertIsInstance(entrypoint, str)
            entrypoints.append(entrypoint)
        with tempfile.TemporaryDirectory(prefix="python-source-entrypoints-") as temporary:
            fixture_root = Path(temporary) / "source"
            shadow_root = Path(temporary) / "shadow"
            copy_source_like_entrypoints(ROOT, fixture_root, tuple(entrypoints))
            shadow_root.mkdir()
            shadow = shadow_root / "yaml.py"
            shadow.write_text("raise ImportError('deterministic shadowed yaml')\n", encoding="utf-8")
            environment = os.environ.copy()
            environment["PYTHONPATH"] = str(shadow_root)
            environment["PYTHONDONTWRITEBYTECODE"] = "1"
            environment.pop("AI_CONTEXT_PYTHON", None)
            before = fixture_tree_snapshot(fixture_root)
            for item in self.pyyaml_source_only:
                entrypoint = item["path"]
                self.assertIsInstance(entrypoint, str)
                with self.subTest(entrypoint=entrypoint):
                    try:
                        result = subprocess.run(
                            [
                                sys.executable,
                                "-B",
                                str(fixture_root / entrypoint),
                                "--diagnostic-format=json",
                            ],
                            cwd=fixture_root,
                            env=environment,
                            capture_output=True,
                            text=True,
                            encoding="utf-8",
                            errors="replace",
                            check=False,
                            timeout=DIRECT_ENTRYPOINT_TIMEOUT_SECONDS,
                        )
                    except subprocess.TimeoutExpired as error:
                        self.fail(
                            f"{entrypoint} did not return from its prerequisite guard within "
                            f"{DIRECT_ENTRYPOINT_TIMEOUT_SECONDS}s: {error}"
                        )
                    self.assertEqual(
                        item["prerequisite_exit_code"],
                        result.returncode,
                        result.stdout + result.stderr,
                    )
                    self.assertEqual("", result.stderr)
                    lines = result.stdout.splitlines()
                    self.assertEqual(1, len(lines), result.stdout)
                    diagnostic = json.loads(lines[0])
                    self.assertEqual("blocked-by-environment", diagnostic["outcome"])
                    self.assertEqual("missing-dependency", diagnostic["reason_code"])
                    self.assertEqual(entrypoint, diagnostic["entrypoint"])
                    self.assertEqual(["PyYAML==6.0.3"], diagnostic["missing_requirements"])
                    self.assertFalse(diagnostic["mutation_started"])
                    self.assertEqual(before, fixture_tree_snapshot(fixture_root))

    def test_gwt_002a_given_every_stdlib_source_entrypoint_when_the_guard_exits_then_no_pre_guard_fixture_write_is_allowed(self) -> None:
        source_only_paths = {item["path"] for item in self.source_only}
        pyyaml_source_only_paths = {item["path"] for item in self.pyyaml_source_only}
        stdlib_source_only_paths = {item["path"] for item in self.stdlib_source_only}
        self.assertFalse(pyyaml_source_only_paths & stdlib_source_only_paths)
        self.assertEqual(source_only_paths, pyyaml_source_only_paths | stdlib_source_only_paths)
        self.assertEqual(
            {
                STDLIB_COMPARE,
                STDLIB_FIXTURE_PROFILE,
                STDLIB_PACKAGE_IDENTITY,
                STDLIB_V015_WSL_RUNNER,
            },
            stdlib_source_only_paths,
        )
        entrypoints: list[str] = []
        for item in self.stdlib_source_only:
            entrypoint = item["path"]
            self.assertIsInstance(entrypoint, str)
            entrypoints.append(entrypoint)
        with tempfile.TemporaryDirectory(prefix="python-source-entrypoints-guard-") as temporary:
            fixture_root = Path(temporary)
            copy_source_like_entrypoints(
                ROOT,
                fixture_root,
                tuple(entrypoints),
                support_files=(".ai/scripts/ai_context_package_identity.py",),
            )
            bootstrap = fixture_root / ".ai/scripts/python_prerequisites.py"
            bootstrap.write_text(
                "def guard_direct_entrypoint(entrypoint):\n"
                "    print(f'fixture-direct-guard:{entrypoint}')\n"
                "    raise SystemExit(73)\n",
                encoding="utf-8",
            )
            before = fixture_tree_snapshot(fixture_root)
            environment = os.environ.copy()
            environment["PYTHONDONTWRITEBYTECODE"] = "1"
            environment.pop("PYTHONPATH", None)
            for entrypoint in entrypoints:
                with self.subTest(entrypoint=entrypoint):
                    try:
                        result = subprocess.run(
                            [sys.executable, "-B", str(fixture_root / entrypoint)],
                            cwd=fixture_root,
                            env=environment,
                            capture_output=True,
                            text=True,
                            encoding="utf-8",
                            errors="replace",
                            check=False,
                            timeout=DIRECT_ENTRYPOINT_TIMEOUT_SECONDS,
                        )
                    except subprocess.TimeoutExpired as error:
                        self.fail(
                            f"{entrypoint} did not reach its direct guard within "
                            f"{DIRECT_ENTRYPOINT_TIMEOUT_SECONDS}s: {error}"
                        )
                    self.assertEqual(73, result.returncode, result.stdout + result.stderr)
                    self.assertEqual(
                        [f"fixture-direct-guard:{entrypoint}"],
                        result.stdout.splitlines(),
                    )
                    self.assertEqual("", result.stderr)
                    self.assertEqual(before, fixture_tree_snapshot(fixture_root))

    def test_gwt_003_given_source_only_registry_when_stdlib_entries_are_selected_then_they_have_empty_dependency_profiles(self) -> None:
        stdlib_entries = {item["path"]: item for item in self.stdlib_source_only}
        self.assertEqual(
            {
                STDLIB_COMPARE,
                STDLIB_FIXTURE_PROFILE,
                STDLIB_PACKAGE_IDENTITY,
                STDLIB_V015_WSL_RUNNER,
            },
            set(stdlib_entries),
        )
        for entrypoint in (
            STDLIB_COMPARE,
            STDLIB_FIXTURE_PROFILE,
            STDLIB_PACKAGE_IDENTITY,
            STDLIB_V015_WSL_RUNNER,
        ):
            self.assertEqual([], stdlib_entries[entrypoint]["dependency_profile"])


if __name__ == "__main__":
    unittest.main()
