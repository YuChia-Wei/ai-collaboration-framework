#!/usr/bin/env python3
"""Focused regression tests for rollback snapshot restoration."""

from __future__ import annotations

import unittest
from unittest import mock

from test_ai_context_package_apply import (
    APPLY,
    PackageApplyFixture,
    fixture_remediation_decision,
    git,
    operation,
    seed_executable_target_validation_profile,
)


class RollbackSnapshotRecoveryTests(unittest.TestCase):
    path = ".ai/tool.sh"
    before = b"before rollback\n"
    after = b"after apply\n"

    def _interrupted_executable_replacement(
        self,
    ) -> tuple[PackageApplyFixture, dict]:
        fixture = PackageApplyFixture()
        git(fixture.target, "config", "core.filemode", "false")
        seed_executable_target_validation_profile(fixture)
        fixture.add_target(self.path, self.before, executable=True)
        fixture.commit_target()
        fixture.make_package(
            {self.path: (self.after, "framework-managed", "0755")},
            [operation("001-replace", "replace", self.path)],
            {self.path: (self.before, "framework-managed", "0755")},
        )
        plan = fixture.plan()
        decision = fixture_remediation_decision(plan)

        def interrupt_after_replace(boundary: str, _details: dict) -> None:
            if boundary == "after_destination_replace":
                raise APPLY.InjectedInterruption("preserve applied state for recovery")

        with self.assertRaises(APPLY.InjectedInterruption):
            APPLY.apply_plan(
                plan,
                boundary_hook=interrupt_after_replace,
                remediation_decision=decision,
            )
        self.assertEqual(self.after, (fixture.target / self.path).read_bytes())
        return fixture, plan

    def test_given_windows_filemode_disabled_recovery_when_rollback_restores_executable_then_same_snapshot_completes(self) -> None:
        fixture, plan = self._interrupted_executable_replacement()
        try:
            # Simulate a Windows worktree that cannot expose Git's executable bit.
            with mock.patch.object(APPLY, "filesystem_mode", return_value="0644"):
                journal = APPLY.recover_transaction(
                    fixture.target, plan["plan_sha256"], "rollback"
                )

            self.assertEqual("rolled-back", journal["state"])
            self.assertEqual(self.before, (fixture.target / self.path).read_bytes())
            self.assertEqual(
                "",
                git(
                    fixture.target,
                    "status",
                    "--porcelain",
                    "--untracked-files=all",
                ).stdout,
            )
        finally:
            fixture.close()

    def test_given_verified_restoration_when_target_mutates_after_progress_then_rollback_rejects_it(self) -> None:
        fixture, plan = self._interrupted_executable_replacement()
        try:
            def mutate_after_progress(boundary: str, details: dict) -> None:
                if (
                    boundary == "after_rollback_progress_journal"
                    and details.get("path") == self.path
                ):
                    (fixture.target / self.path).write_bytes(b"unexpected mutation\n")

            with mock.patch.object(APPLY, "filesystem_mode", return_value="0644"):
                with self.assertRaisesRegex(
                    APPLY.ApplyError,
                    "target state does not match rollback progress",
                ):
                    APPLY.recover_transaction(
                        fixture.target,
                        plan["plan_sha256"],
                        "rollback",
                        boundary_hook=mutate_after_progress,
                    )
            self.assertEqual(
                b"unexpected mutation\n", (fixture.target / self.path).read_bytes()
            )
        finally:
            fixture.close()

    def test_given_initially_dirty_path_when_restoration_is_considered_then_snapshot_does_not_accept_it_as_clean(self) -> None:
        fixture = PackageApplyFixture()
        try:
            fixture.add_target(self.path, self.before, executable=True)
            fixture.commit_target()
            target_path = fixture.target / self.path
            target_path.write_bytes(b"initial target-owned drift\n")
            snapshot = APPLY.capture_target_git_snapshot(
                fixture.target,
                [self.path],
                phase="recovery-rollback",
                require_clean=False,
            )
            with APPLY.target_git_snapshot_scope(snapshot):
                state = APPLY.observation([self.path], fixture.target)[self.path]
                self.assertTrue(state["dirty"])
                self.assertFalse(
                    snapshot.accept_verified_prestate_restoration(self.path, state)
                )
            self.assertIn(self.path, snapshot.dirty_paths)
        finally:
            fixture.close()


if __name__ == "__main__":
    unittest.main()
