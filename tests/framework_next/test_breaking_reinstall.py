"""Focused destructive-boundary tests; full installer execution is a separate trial."""
from hashlib import sha256
from pathlib import Path
import json
import os
import subprocess
import sys
import tempfile
import types
import unittest
from unittest.mock import patch

sys.dont_write_bytecode = True
ROOT = Path(__file__).absolute().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from distribution import reinstallation as owner


class BreakingReinstallTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.base = Path(self.temp.name).resolve()
        self.project = self.base / "project"
        self.project.mkdir()
        subprocess.run(["git", "init", "-q", str(self.project)], check=True)
        self.old = ".ai/obsolete.md"
        self.keep = ".dev/workflows/current/workflow.yaml"
        for name, raw in ((self.old, b"old framework\n"), (self.keep, b"actual target work\n")):
            path = self.project / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(raw)
        subprocess.run(["git", "-C", str(self.project), "add", "."], check=True)
        subprocess.run(["git", "-C", str(self.project), "-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid", "commit", "-qm", "fixture"], check=True)
        head = subprocess.check_output(["git", "-C", str(self.project), "rev-parse", "HEAD"]).decode().strip()
        for name in ("preview", "engine", "candidate", "scratch", "staging", "recovery"):
            (self.base / name).mkdir()
        maintenance = dict(declared_by="fixture", declaration_reference="isolated fixture",
                           affected_capabilities=[], sessions_stopped=True, tools_stopped=True,
                           external_writers_stopped=True)
        install = dict(api_version=2, operation="plan", project_root=str(self.project),
                       engine={}, candidate_root=str(self.base / "candidate"), candidate_identity="fixture",
                       expected_lock_sha256=None, mode_policy="windows-inventory-only" if os.name == "nt" else "posix-permissions",
                       durability=dict(declared_by="fixture", declaration_reference="fixture", failure_domain="process-termination"),
                       protected_inputs=[], project_data_action="none", project_edits=[])
        install.update({role + "_root": str(self.base / role) for role in ("engine", "scratch", "staging", "recovery")})
        self.request = dict(reinstall_version=1, operation="plan", project_root=str(self.project), expected_head=head,
                            cleanup=[self.pin(self.old)], preserved_inputs=[self.pin(self.keep)],
                            preview_root=str(self.base / "preview"), installation=install, maintenance=maintenance)
        self.candidate = types.SimpleNamespace(identity="fixture", members={}, selection={"components": []})
        self.patches = [patch.object(owner.state, "_engine"), patch.object(owner.state, "read_candidate", return_value=self.candidate),
                        patch.object(owner.installation, "plan", side_effect=self.install_plan)]
        for item in self.patches:
            item.start()

    def tearDown(self):
        for item in reversed(self.patches):
            item.stop()
        self.temp.cleanup()

    def pin(self, name):
        return dict(path=name, sha256=sha256((self.project / name).read_bytes()).hexdigest())

    def install_plan(self, request):
        plan = {name: request[name] for name in ("candidate_identity", "engine", "expected_lock_sha256", "mode_policy", "protected_inputs", "project_edits")}
        plan.update(delta=[], project_inputs=[], maintenance_scope=[], noop=False)
        return dict(outcome="planned", plan=plan, plan_sha256="a" * 64)

    def apply_request(self):
        result = owner.execute(self.request)
        self.assertEqual("planned", result["outcome"], result)
        return {**self.request, "operation": "apply", "expected_plan_sha256": result["plan_sha256"]}

    def test_exact_cleanup_preserves_workflow(self):
        request = self.apply_request()
        with patch.object(owner.installation, "apply", return_value={"outcome": "applied"}):
            result = owner.execute(request)
        self.assertEqual("reinstalled", result["outcome"], result)
        self.assertFalse((self.project / self.old).exists())
        self.assertEqual(b"actual target work\n", (self.project / self.keep).read_bytes())

    def test_drift_between_plan_and_apply_removes_nothing(self):
        request = self.apply_request()
        (self.project / self.old).write_bytes(b"uncommitted user edit")
        result = owner.execute(request)
        self.assertFalse(result["changed"])
        self.assertEqual("reinstall-dirty", result["diagnostics"][0]["code"])
        self.assertTrue((self.project / self.old).exists())

    def test_untracked_cleanup_rejected(self):
        name = ".ai/untracked.md"
        (self.project / name).write_bytes(b"user data")
        self.request["cleanup"].append(self.pin(name))
        result = owner.execute(self.request)
        self.assertEqual("reinstall-untracked", result["diagnostics"][0]["code"])
        self.assertFalse(result["changed"])

    def test_workflow_cleanup_rejected(self):
        self.request["cleanup"] = sorted([self.pin(self.old), self.pin(self.keep)], key=lambda r:r["path"])
        self.request["preserved_inputs"] = []
        result = owner.execute(self.request)
        self.assertEqual("reinstall-workflow", result["diagnostics"][0]["code"])

    def test_unclassified_file_rejected(self):
        self.request["preserved_inputs"] = []
        result = owner.execute(self.request)
        self.assertEqual("reinstall-unclassified", result["diagnostics"][0]["code"])

    def test_failed_install_reports_destructive_partial_state(self):
        request = self.apply_request()
        with patch.object(owner.installation, "apply", return_value={"outcome": "blocked", "changed": False}):
            result = owner.execute(request)
        self.assertEqual("cleanup-incomplete", result["outcome"], result)
        self.assertTrue(result["changed"])
        self.assertEqual([self.old], result["removed"])
        self.assertEqual("blocked", result["installation_result"]["outcome"])
        self.assertTrue((self.project / self.keep).exists())

    def test_linked_cleanup_rejected(self):
        name = ".ai/linked.md"
        try:
            os.symlink(self.project / self.old, self.project / name)
        except OSError:
            self.skipTest("Host cannot create a symlink fixture.")
        result = owner.execute(self.request)
        self.assertNotEqual("planned", result["outcome"])
        self.assertFalse(result["changed"])


if __name__ == "__main__":
    unittest.main()
