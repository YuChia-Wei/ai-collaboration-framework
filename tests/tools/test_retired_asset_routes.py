"""Issue #534: current source resources and explicit legacy refusal."""
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
# Prefer Git Bash over Windows' WSL launcher.
BASH = (str(Path(os.environ.get("ProgramFiles", "C:/Program Files")) / "Git/bin/bash.exe")
        if os.name == "nt" else shutil.which("bash"))


class LegacyRouteTests(unittest.TestCase):
    def test_retired_validators_refuse_without_loading_removed_dependencies(self):
        for name in ("execution_artifact_contract.py", "validate-agent-execution-guardrails.py",
                     "validate-terminal-issue-closure.py"):
            with self.subTest(name=name):
                result = subprocess.run([sys.executable, "-I", "-B", str(ROOT / "tools/maintenance" / name)],
                                        capture_output=True, text=True, timeout=20)
                self.assertEqual(result.returncode, 1)
                self.assertIn("unavailable_legacy_route", result.stderr)
                self.assertIn("No validation was performed", result.stderr)
                self.assertNotIn("Traceback", result.stderr)

    def test_historical_entrypoints_are_not_executable_selections(self):
        # Exercise the actual consumer, not just registry field spelling.
        sys.path.insert(0, str(ROOT / "tools/maintenance"))
        try:
            from python_prerequisites import entrypoint_contract, load_registry
            registry = load_registry()
            history = registry["historical_entrypoints"]
            self.assertEqual(history["availability"], "unavailable-legacy")
            self.assertEqual(len(history["records"]), 4)
            for row in history["records"]:
                with self.assertRaisesRegex(ValueError, "Unsupported Python entrypoint"):
                    entrypoint_contract(row["path"], registry)
        finally:
            sys.path.pop(0)

class SourceCheckerTests(unittest.TestCase):
    def run_checker(self, checker, cwd):
        self.assertTrue(BASH and Path(BASH).is_file(), "Bash is required for this selected shell regression")
        return subprocess.run([BASH, str(checker)], cwd=cwd, input="y\n", capture_output=True,
                              text=True, encoding="utf-8", timeout=30)

    def test_source_resources_resolve_from_unrelated_working_directory(self):
        with tempfile.TemporaryDirectory() as elsewhere:
            result = self.run_checker(ROOT / "src/tools/dotnet/check-coding-standards.sh", elsewhere)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("Self-check passed", result.stdout)
        self.assertRegex(result.stdout, r"Total scripts: [1-9][0-9]*")
        self.assertNotIn("Missing exact catalog route", result.stdout)

    def test_missing_resources_stop_before_checks_even_with_yes_input(self):
        with tempfile.TemporaryDirectory() as directory:
            checker = Path(directory) / "src/tools/dotnet/check-coding-standards.sh"
            checker.parent.mkdir(parents=True)
            shutil.copyfile(ROOT / "src/tools/dotnet/check-coding-standards.sh", checker)
            result = self.run_checker(checker, directory)
        self.assertEqual(result.returncode, 1)
        self.assertIn("Self-check failed", result.stdout)
        self.assertNotIn("1. Checking Main File", result.stdout)

    def test_inexact_catalog_link_is_still_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            fixture = Path(directory)
            checker = fixture / "src/tools/dotnet/check-coding-standards.sh"
            checker.parent.mkdir(parents=True)
            shutil.copyfile(ROOT / "src/tools/dotnet/check-coding-standards.sh", checker)
            standards = fixture / "src/knowledge/dotnet-backend/standards"
            shutil.copytree(ROOT / "src/knowledge/dotnet-backend/standards", standards)
            catalog = standards / "coding-standards.md"
            content = catalog.read_text(encoding="utf-8")
            content = content.replace("](coding-standards/aggregate-standards.md)",
                                      "](coding-standards/aggregate-standards.md.bak)")
            catalog.write_text(content, encoding="utf-8")
            result = self.run_checker(checker, directory)
        self.assertEqual(result.returncode, 1)
        self.assertIn("Missing exact catalog route", result.stdout)


if __name__ == "__main__":
    unittest.main()
