#!/usr/bin/env python3
"""Focused execution tests for the direct target-validation receipt runner."""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[3]
RUNNER = (
    ROOT
    / ".ai/assets/skills/ai-context-upgrader/scripts/run-target-validation.py"
)
SUPPORT_PATH = Path(__file__).resolve().with_name("test_ai_context_package_apply.py")
SUPPORT_SPEC = importlib.util.spec_from_file_location(
    "target_validation_apply_support", SUPPORT_PATH
)
if SUPPORT_SPEC is None or SUPPORT_SPEC.loader is None:
    raise RuntimeError("cannot load package-apply test support")
SUPPORT = importlib.util.module_from_spec(SUPPORT_SPEC)
sys.modules[SUPPORT_SPEC.name] = SUPPORT
SUPPORT_SPEC.loader.exec_module(SUPPORT)
RUNNER_SPEC = importlib.util.spec_from_file_location("target_validation_runner", RUNNER)
if RUNNER_SPEC is None or RUNNER_SPEC.loader is None:
    raise RuntimeError("cannot load target validation runner")
RUNNER_MODULE = importlib.util.module_from_spec(RUNNER_SPEC)
sys.modules[RUNNER_SPEC.name] = RUNNER_MODULE
RUNNER_SPEC.loader.exec_module(RUNNER_MODULE)


class TargetValidationRunnerTests(unittest.TestCase):
    def prepare_transaction(self, argv: list[str]) -> tuple[object, dict]:
        fixture = SUPPORT.PackageApplyFixture()
        self.addCleanup(fixture.close)
        package = SUPPORT.make_schema_23_upgrade_package(fixture)
        candidate_provenance, candidate_ledger = SUPPORT.fixture_upgrade_authorities(
            fixture, package["selection"], package["previous_content"]
        )
        fixture.add_target(
            ".dev/project-config.yaml",
            SUPPORT.yaml.safe_dump(
                {"validation": {"routine": {"argv": argv}}}, sort_keys=False
            ).encode("utf-8"),
        )
        fixture.commit_target("target validation runner profile")
        plan = fixture.plan("0.9.0")
        decision = SUPPORT.fixture_remediation_decision(
            plan,
            candidate_provenance=candidate_provenance,
            candidate_ledger=candidate_ledger,
        )
        SUPPORT.RAW_APPLY_PLAN(plan, remediation_decision=decision)
        return fixture, plan

    def run_runner(self, fixture: object, transaction_id: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                sys.executable,
                str(RUNNER),
                "--target-root",
                str(fixture.target),
                "--transaction-id",
                transaction_id,
            ],
            cwd=fixture.target,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )

    def test_wrong_transaction_fails_before_profile_execution(self) -> None:
        marker = "runner-profile-executed.txt"
        fixture, plan = self.prepare_transaction(
            [
                sys.executable,
                "-c",
                f"from pathlib import Path; Path({marker!r}).write_text('ran')",
            ]
        )

        result = self.run_runner(fixture, "0" * 64)

        self.assertEqual(2, result.returncode, result.stdout + result.stderr)
        self.assertFalse((fixture.target / marker).exists())
        transaction = SUPPORT.APPLY.transaction_root(
            fixture.target, plan["plan_sha256"]
        )
        self.assertFalse(
            (transaction / SUPPORT.APPLY.TARGET_VALIDATION_OUTPUT_PATH).exists()
        )

    def test_failing_profile_retains_raw_output_without_passing_receipt(self) -> None:
        fixture, plan = self.prepare_transaction(
            [
                sys.executable,
                "-c",
                "import sys; print('expected failing profile'); raise SystemExit(7)",
            ]
        )

        result = self.run_runner(fixture, plan["plan_sha256"])

        self.assertEqual(7, result.returncode, result.stdout + result.stderr)
        transaction = SUPPORT.APPLY.transaction_root(
            fixture.target, plan["plan_sha256"]
        )
        output = (transaction / SUPPORT.APPLY.TARGET_VALIDATION_OUTPUT_PATH).read_bytes()
        self.assertIn(b"expected failing profile", output)
        self.assertFalse(
            (transaction / SUPPORT.APPLY.TARGET_VALIDATION_RECEIPT_PATH).exists()
        )
        attempts = list(transaction.glob("target-validation-attempt-*.json"))
        self.assertEqual(1, len(attempts))
        attempt = json.loads(attempts[0].read_text(encoding="utf-8"))
        self.assertEqual("failed", attempt["execution"]["outcome"])
        self.assertEqual(7, attempt["execution"]["exit_code"])
        self.assertEqual(
            SUPPORT.APPLY.sha256_bytes(output), attempt["execution"]["output_sha256"]
        )

    def test_unit_interrupted_runner_retains_streamed_partial_output_without_receipt(
        self,
    ) -> None:
        """Unit-only interruption seam; subprocess.run owns child cleanup."""
        fixture, plan = self.prepare_transaction(
            [sys.executable, "-c", "print('unused because this is mocked')"]
        )
        real_subprocess_run = subprocess.run

        def interrupting_run(_argv: list[str], **kwargs: object) -> object:
            if "stdout" not in kwargs:
                return real_subprocess_run(_argv, **kwargs)
            output_stream = kwargs["stdout"]
            assert hasattr(output_stream, "write")
            output_stream.write(b"partial target validation output\n")
            output_stream.flush()
            raise KeyboardInterrupt()

        with mock.patch.object(
            RUNNER_MODULE.subprocess, "run", side_effect=interrupting_run
        ):
            receipt, exit_code, _message = RUNNER_MODULE.run_target_validation(
                fixture.target, plan["plan_sha256"]
            )

        self.assertIsNone(receipt)
        self.assertEqual(130, exit_code)
        transaction = SUPPORT.APPLY.transaction_root(
            fixture.target, plan["plan_sha256"]
        )
        output = (transaction / SUPPORT.APPLY.TARGET_VALIDATION_OUTPUT_PATH).read_bytes()
        self.assertEqual(b"partial target validation output\n", output)
        self.assertFalse(
            (transaction / SUPPORT.APPLY.TARGET_VALIDATION_RECEIPT_PATH).exists()
        )
        attempts = list(transaction.glob("target-validation-attempt-*.json"))
        self.assertEqual(1, len(attempts))
        attempt = json.loads(attempts[0].read_text(encoding="utf-8"))
        self.assertEqual("interrupted", attempt["execution"]["outcome"])
        self.assertEqual(130, attempt["execution"]["exit_code"])
        self.assertEqual("target-validation-interrupted", attempt["reason"])
        self.assertEqual(
            SUPPORT.APPLY.sha256_bytes(output), attempt["execution"]["output_sha256"]
        )

    def test_passing_profile_writes_canonical_unbound_receipt_accepted_by_recorder(self) -> None:
        fixture, plan = self.prepare_transaction(
            [sys.executable, "-c", "print('expected successful profile')"]
        )

        result = self.run_runner(fixture, plan["plan_sha256"])

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("--record-target-validation-receipt", result.stdout)
        transaction, sealed_plan, journal = SUPPORT.APPLY.load_transaction(
            fixture.target,
            plan["plan_sha256"],
            allow_unbound_target_validation_receipt=True,
        )
        self.assertEqual("awaiting-target-validation", journal["state"])
        self.assertIsNone(journal["target_validation_receipt_sha256"])
        remediation = SUPPORT.APPLY.validate_upgrade_remediation_artifacts(
            transaction,
            sealed_plan,
            journal,
            allow_unbound_target_validation_receipt=True,
        )
        self.assertIsNotNone(remediation)
        packet, decision = remediation
        receipt_path = transaction / SUPPORT.APPLY.TARGET_VALIDATION_RECEIPT_PATH
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
        self.assertEqual(
            receipt,
            SUPPORT.APPLY.validate_target_validation_receipt(
                receipt, sealed_plan, journal, packet, decision
            ),
        )
        self.assertEqual(
            receipt,
            SUPPORT.APPLY.record_target_validation_receipt(
                fixture.target, plan["plan_sha256"], receipt_path
            ),
        )


if __name__ == "__main__":
    unittest.main()
