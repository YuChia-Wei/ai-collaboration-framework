#!/usr/bin/env python3
"""Synthetic inference fixtures; these are not actual incident diagnoses."""
from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

sys.dont_write_bytecode = True
SKILL = Path(__file__).resolve().parents[2]
ROOT = SKILL.parents[3]
SCRIPT = SKILL / "scripts/validate-diagnostic-record.py"
spec = importlib.util.spec_from_file_location("diagnostic_validator", SCRIPT)
validator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validator)


class DiagnosticContractTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="diagnostic-fixture-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.data = json.loads((SKILL / "fixtures/insufficient-sampling.json").read_text())
        payload = b"SYNTHETIC fixture: baseline 3 calls; intervention 1 call\n"
        (self.root / "observation.txt").write_bytes(payload)
        self.data["evidence"] = [{"id": "E1", "path": "observation.txt", "sha256": hashlib.sha256(payload).hexdigest()}]

    def supported(self):
        data = copy.deepcopy(self.data)
        hypothesis = data["hypotheses"][0]
        hypothesis.update(method="interception", falsification_strength="deterministic-bounded")
        hypothesis["coverage"] = {"expected_opportunities": 3, "observed_opportunities": 3, "complete": True}
        return data

    def rejected(self, data, pattern):
        with self.assertRaisesRegex(validator.DiagnosticError, pattern):
            validator.validate(data, self.root)

    def test_sampling_cannot_confirm_root_cause(self):
        self.rejected(self.data, "deterministic support")

    def test_bounded_interception_with_reproduction_and_isolation_is_admissible(self):
        validator.validate(self.supported(), self.root)

    def test_sampling_absence_cannot_falsify(self):
        self.data["hypotheses"][0]["result"] = "falsified"
        self.rejected(self.data, "cannot falsify")

    def test_sampling_cannot_be_renamed_deterministic(self):
        self.data["hypotheses"][0]["falsification_strength"] = "deterministic-bounded"
        self.rejected(self.data, "deterministic observation")

    def test_incomplete_counts_cannot_claim_complete_coverage(self):
        data = self.supported()
        data["hypotheses"][0]["coverage"]["observed_opportunities"] = 2
        self.rejected(data, "all deterministic")

    def test_missing_reproduction_blocks_confirmation(self):
        data = self.supported()
        data["minimal_reproduction"]["status"] = "not-run"
        self.rejected(data, "minimal reproduction")

    def test_no_controlled_intervention_blocks_confirmation(self):
        data = self.supported()
        data["causal_isolation"]["status"] = "not-isolated"
        self.rejected(data, "causal isolation")

    def test_unresolved_competing_hypothesis_blocks_confirmation(self):
        data = self.supported()
        other = copy.deepcopy(data["hypotheses"][0])
        other.update(id="H2", result="inconclusive")
        data["hypotheses"].append(other)
        self.rejected(data, "unresolved alternative")

    def test_tampered_or_unknown_evidence_is_rejected(self):
        data = self.supported()
        data["evidence"][0]["sha256"] = "0" * 64
        self.rejected(data, "digest mismatch")
        data = self.supported()
        data["root_cause"]["evidence_refs"] = ["unknown"]
        self.rejected(data, "unknown reference")

    def test_evidence_cannot_escape_root(self):
        for path in ("../observation.txt", "C:/observation.txt", "/observation.txt", "x\\observation.txt"):
            with self.subTest(path=path):
                data = self.supported()
                data["evidence"][0]["path"] = path
                self.rejected(data, "unsafe relative")

    def test_bool_count_and_unknown_fields_fail_closed(self):
        data = self.supported()
        data["hypotheses"][0]["coverage"]["expected_opportunities"] = True
        self.rejected(data, "integer required")
        data = self.supported()
        data["repair_handoff"]["authorized"] = True
        self.rejected(data, "unknown fields")

    def test_unconfirmed_sampling_is_preserved_without_repair_authority(self):
        self.data["root_cause"]["status"] = "unconfirmed"
        self.data["repair_handoff"]["authorization_ref"] = None
        validator.validate(self.data, self.root)

    def test_cli_rejects_duplicate_keys_and_retains_receipt_bytes(self):
        path = self.root / "record.json"
        path.write_text('{"schema_version":"1.0","schema_version":"1.0"}')
        before = (self.root / "observation.txt").read_bytes()
        result = subprocess.run([sys.executable, str(SCRIPT), "--record", str(path), "--evidence-root", str(self.root)], capture_output=True, text=True)
        self.assertEqual(1, result.returncode)
        self.assertIn("duplicate JSON key", result.stderr)
        self.assertEqual(before, (self.root / "observation.txt").read_bytes())

    def test_routing_wrappers_and_runtime_identifier_agree(self):
        import yaml
        profile = yaml.safe_load((ROOT / ".ai/assets/skills/software-development-orchestrator/references/capability-profile.yaml").read_text())
        self.assertEqual("diagnostic-analyst", profile["mappings"]["diagnosis"])
        self.assertIn("diagnosis", profile["required_slots"])
        for runtime in (".agents", ".claude"):
            self.assertIn("diagnostic-analyst/skill.yaml", (ROOT / runtime / "skills/diagnostic-analyst/SKILL.md").read_text())
        result = subprocess.run([sys.executable, str(ROOT / ".ai/scripts/skill_identifier_lifecycle.py"), "diagnostic-analyst"], capture_output=True, text=True)
        self.assertEqual(0, result.returncode, result.stderr)


if __name__ == "__main__":
    unittest.main()
