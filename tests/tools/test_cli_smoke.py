"""Ten real isolated CLI launches: one success and one rejection per family."""
import json
import subprocess
import sys

from .tool_fixtures import FAMILIES, SCRIPTS, ToolCase, package


class CliSmokeTests(ToolCase):
    def test_explain_returns_json_success_without_creating_records(self):
        for family in FAMILIES:
            with self.subTest(family=family):
                request = self.write_json("request.json", self.request(family, "explain"))
                result = subprocess.run([sys.executable, "-I", "-B", str(package(family) / "scripts" / SCRIPTS[family]),
                                         "--request", str(request)], cwd=self.project, capture_output=True, timeout=20)
                self.assertEqual(result.returncode, 0, result.stderr.decode(errors="replace"))
                response = json.loads(result.stdout)
                self.assertEqual(response["outcome"], "ok" if family == "problem-frame-author" else "succeeded")
                self.assertEqual(response["mutation_state"], "none")
                self.assertEqual(result.stderr, b"")
                self.assertEqual([p.name for p in self.project.iterdir()], ["request.json"])

    def test_unknown_operation_returns_structured_failure_and_documented_exit(self):
        for family in FAMILIES:
            with self.subTest(family=family):
                request = self.write_json("request.json", self.request(family, "not-an-operation"))
                result = subprocess.run([sys.executable, "-I", "-B", str(package(family) / "scripts" / SCRIPTS[family]),
                                         "--request", str(request)], cwd=self.project, capture_output=True, timeout=20)
                response = json.loads(result.stdout)
                self.assertEqual(result.returncode, 2 if family == "problem-frame-author" else 1)
                self.assertEqual(response["outcome"], "invalid-input" if family == "problem-frame-author" else "unsupported")
                self.assertEqual(response["mutation_state"], "none")
                self.assertTrue(response["diagnostics"])
                self.assertEqual(result.stderr, b"")
                self.assertEqual([p.name for p in self.project.iterdir()], ["request.json"])
