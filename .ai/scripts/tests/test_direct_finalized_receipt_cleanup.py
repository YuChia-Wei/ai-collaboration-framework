#!/usr/bin/env python3
"""Focused coverage for opt-in direct finalized receipt cleanup."""

from __future__ import annotations

import importlib.util
import shutil
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
PLANNER = ROOT / ".ai/scripts/plan-ai-context-package-apply.py"
SUPPORT_PATH = Path(__file__).resolve().with_name("test_ai_context_package_apply.py")
SUPPORT_SPEC = importlib.util.spec_from_file_location(
    "direct_terminal_cleanup_apply_support", SUPPORT_PATH
)
if SUPPORT_SPEC is None or SUPPORT_SPEC.loader is None:
    raise RuntimeError("cannot load package-apply test support")
SUPPORT = importlib.util.module_from_spec(SUPPORT_SPEC)
sys.modules[SUPPORT_SPEC.name] = SUPPORT
SUPPORT_SPEC.loader.exec_module(SUPPORT)


class DirectFinalizedReceiptCleanupTests(unittest.TestCase):
    def prepare_finalized_upgrade(self) -> tuple[object, dict]:
        fixture = SUPPORT.PackageApplyFixture()
        self.addCleanup(fixture.close)
        package = SUPPORT.make_schema_23_upgrade_package(fixture)
        candidate_provenance, candidate_ledger = SUPPORT.fixture_upgrade_authorities(
            fixture, package["selection"], package["previous_content"]
        )
        plan = fixture.plan("0.9.0")
        SUPPORT.APPLY.apply_plan(
            plan,
            remediation_decision=SUPPORT.fixture_remediation_decision(
                plan,
                candidate_provenance=candidate_provenance,
                candidate_ledger=candidate_ledger,
            ),
        )
        SUPPORT.record_passed_target_validation(fixture, plan)
        SUPPORT.TARGET.finalize_context(
            fixture.target, candidate_provenance, candidate_ledger
        )
        return fixture, plan

    def test_incomplete_or_tampered_finalization_preserves_pending_receipt(self) -> None:
        fixture = SUPPORT.PackageApplyFixture()
        self.addCleanup(fixture.close)
        package = SUPPORT.make_schema_23_upgrade_package(fixture)
        candidate_provenance, candidate_ledger = SUPPORT.fixture_upgrade_authorities(
            fixture, package["selection"], package["previous_content"]
        )
        plan = fixture.plan("0.9.0")
        SUPPORT.APPLY.apply_plan(
            plan,
            remediation_decision=SUPPORT.fixture_remediation_decision(
                plan,
                candidate_provenance=candidate_provenance,
                candidate_ledger=candidate_ledger,
            ),
        )
        SUPPORT.record_passed_target_validation(fixture, plan)
        pending = fixture.target / SUPPORT.APPLY.PENDING_RECEIPT_PATH
        pending_before = pending.read_bytes()

        with self.assertRaises(SUPPORT.APPLY.ApplyError):
            SUPPORT.APPLY.archive_finalized_receipt(
                fixture.target, plan["plan_sha256"]
            )

        transaction = SUPPORT.APPLY.transaction_root(
            fixture.target, plan["plan_sha256"]
        )
        self.assertEqual(pending_before, pending.read_bytes())
        self.assertFalse(
            (
                transaction
                / SUPPORT.APPLY.FINALIZED_PENDING_RECEIPT_ARCHIVE_PATH
            ).exists()
        )

        SUPPORT.TARGET.finalize_context(
            fixture.target, candidate_provenance, candidate_ledger
        )
        terminal = transaction / SUPPORT.TARGET.TERMINAL_RECEIPT_PATH
        terminal.write_bytes(b"{}\n")

        with self.assertRaises(SUPPORT.APPLY.ApplyError):
            SUPPORT.APPLY.archive_finalized_receipt(
                fixture.target, plan["plan_sha256"]
            )

        self.assertEqual(pending_before, pending.read_bytes())
        self.assertFalse(
            (
                transaction
                / SUPPORT.APPLY.FINALIZED_PENDING_RECEIPT_ARCHIVE_PATH
            ).exists()
        )

    def test_cli_archives_finalized_receipt_and_clone_has_no_pending_dependency(self) -> None:
        fixture, plan = self.prepare_finalized_upgrade()
        pending = fixture.target / SUPPORT.APPLY.PENDING_RECEIPT_PATH
        pending_before = pending.read_bytes()
        transaction = SUPPORT.APPLY.transaction_root(
            fixture.target, plan["plan_sha256"]
        )

        result = subprocess.run(
            [
                sys.executable,
                str(PLANNER),
                "--target-root",
                str(fixture.target),
                "--archive-finalized-receipt",
                plan["plan_sha256"],
            ],
            cwd=fixture.target,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("archived-and-cleared", result.stdout)
        archive = (
            transaction / SUPPORT.APPLY.FINALIZED_PENDING_RECEIPT_ARCHIVE_PATH
        )
        self.assertEqual(pending_before, archive.read_bytes())
        self.assertFalse(pending.exists())
        self.assertEqual([], SUPPORT.TARGET.validate_target(fixture.target))
        repeated = SUPPORT.APPLY.archive_finalized_receipt(
            fixture.target, plan["plan_sha256"]
        )
        self.assertEqual("already-archived-and-cleared", repeated["status"])

        SUPPORT.git(fixture.target, "add", "-A")
        fixture.commit_target("fixture direct receipt cleanup")
        clone = fixture.root / "portable-clone"
        subprocess.run(
            ["git", "clone", "-q", str(fixture.target), str(clone)],
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertFalse((clone / SUPPORT.APPLY.PENDING_RECEIPT_PATH).exists())
        self.assertEqual([], SUPPORT.TARGET.validate_target(clone))

    def test_finalize_commit_then_archive_uses_historical_terminal_evidence(self) -> None:
        fixture, plan = self.prepare_finalized_upgrade()
        pending = fixture.target / SUPPORT.APPLY.PENDING_RECEIPT_PATH
        pending_before = pending.read_bytes()
        transaction = SUPPORT.APPLY.transaction_root(
            fixture.target, plan["plan_sha256"]
        )
        SUPPORT.git(fixture.target, "add", "-A")
        fixture.commit_target("fixture finalized upgrade before receipt cleanup")

        pre_cleanup_errors = SUPPORT.TARGET.validate_target(fixture.target)
        self.assertTrue(
            any(
                "sealed target starting commit differs from current HEAD" in error
                for error in pre_cleanup_errors
            ),
            pre_cleanup_errors,
        )

        result = SUPPORT.APPLY.archive_finalized_receipt(
            fixture.target, plan["plan_sha256"]
        )

        archive = (
            transaction / SUPPORT.APPLY.FINALIZED_PENDING_RECEIPT_ARCHIVE_PATH
        )
        self.assertEqual("archived-and-cleared", result["status"])
        self.assertEqual(pending_before, archive.read_bytes())
        self.assertFalse(pending.exists())
        self.assertEqual([], SUPPORT.TARGET.validate_target(fixture.target))

    def test_interruption_after_archive_retains_recoverable_evidence(self) -> None:
        fixture, plan = self.prepare_finalized_upgrade()
        pending = fixture.target / SUPPORT.APPLY.PENDING_RECEIPT_PATH
        pending_before = pending.read_bytes()
        transaction = SUPPORT.APPLY.transaction_root(
            fixture.target, plan["plan_sha256"]
        )

        def interrupt_after_archive(event: str, _details: dict) -> None:
            if event == "after_finalized_receipt_archive":
                raise SUPPORT.APPLY.InjectedInterruption("archive retained before clear")

        with self.assertRaises(SUPPORT.APPLY.InjectedInterruption):
            SUPPORT.APPLY.archive_finalized_receipt(
                fixture.target,
                plan["plan_sha256"],
                boundary_hook=interrupt_after_archive,
            )

        archive = (
            transaction / SUPPORT.APPLY.FINALIZED_PENDING_RECEIPT_ARCHIVE_PATH
        )
        self.assertEqual(pending_before, archive.read_bytes())
        self.assertEqual(pending_before, pending.read_bytes())
        self.assertEqual([], SUPPORT.TARGET.validate_target(fixture.target))
        resumed = SUPPORT.APPLY.archive_finalized_receipt(
            fixture.target, plan["plan_sha256"]
        )
        self.assertEqual("archived-and-cleared", resumed["status"])
        self.assertFalse(pending.exists())


if __name__ == "__main__":
    unittest.main()
