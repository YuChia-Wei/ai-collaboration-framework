#!/usr/bin/env python3
"""GWT contracts for the source-only release closeout entrypoint."""

from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SCRIPT = ROOT / ".ai/scripts/ai_context_release_closeout.py"
SPEC = importlib.util.spec_from_file_location("release_closeout", SCRIPT)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("Unable to load release closeout entrypoint")
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class ReleaseCloseoutGwtTests(unittest.TestCase):
    def test_gwt_001_given_closeout_command_when_inspected_then_it_only_uses_post_publication_state_phases(self) -> None:
        source = SCRIPT.read_text(encoding="utf-8")
        self.assertIn('"publication"', source)
        self.assertIn('"finalization"', source)
        self.assertNotIn('"candidate"', source)
        self.assertNotIn('prepare-ai-context-release.py', source)

    def test_gwt_002_given_mutating_git_arguments_when_read_only_runner_is_called_then_it_fails_closed(self) -> None:
        with self.assertRaisesRegex(ValueError, "read-only"):
            MODULE.run_read_only(["git", "tag", "-a", "v0.10.0"])

    def test_gwt_003_given_source_only_assets_when_distribution_is_read_then_closeout_assets_are_excluded(self) -> None:
        profile = (ROOT / ".ai/distribution/profiles/dotnet-backend.yaml").read_text(encoding="utf-8")
        for path in (
            ".ai/assets/skills/ai-context-release-closeout/**",
            ".agents/skills/ai-context-release-closeout/**",
            ".claude/skills/ai-context-release-closeout/**",
            ".dev/guides/ai-collaboration-guides/AI-CONTEXT-RELEASE-CLOSEOUT-SKILL-GUIDE.md",
            ".ai/scripts/ai_context_release_closeout.py",
            ".ai/scripts/tests/test_ai_context_release_closeout.py",
        ):
            self.assertIn(path, profile)

    def test_gwt_004_given_primary_worktree_output_when_patch_is_planned_then_it_fails_closed(self) -> None:
        arguments = type(
            "Arguments",
            (),
            {
                "version": "v0.10.0",
                "repository": "YuChia-Wei/ai-collaboration-framework",
                "workflow_run_id": "123",
                "rendered_body": None,
                "recorded_at": None,
                "output": ".dev/releases/v0.10.0/closeout.patch",
            },
        )()
        with self.assertRaisesRegex(ValueError, "outside the primary worktree"):
            MODULE.plan_patch(arguments)

    def test_gwt_005_given_validated_candidate_notes_when_closeout_is_planned_then_only_status_becomes_published(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            worktree = Path(temporary)
            notes = worktree / ".dev/releases/v0.10.0/release-notes.md"
            notes.parent.mkdir(parents=True)
            notes.write_text(
                "# REL-v0.10.0\n\n## Status\n\n"
                "Validated candidate; publication remains pending the immutable tag and hosted release workflow.\n\n"
                "## Publication Completion\n\nComplete this section after publication.\n",
                encoding="utf-8",
            )

            MODULE.update_release_notes(worktree, "v0.10.0")

            rendered = notes.read_text(encoding="utf-8")
            self.assertIn("## Status\n\nPublished.", rendered)
            self.assertIn("## Publication Completion", rendered)

    def test_gwt_006_given_unrecognized_notes_status_when_closeout_is_planned_then_it_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            worktree = Path(temporary)
            notes = worktree / ".dev/releases/v0.10.0/release-notes.md"
            notes.parent.mkdir(parents=True)
            notes.write_text("# REL-v0.10.0\n\n## Status\n\nUnexpected.\n", encoding="utf-8")

            with self.assertRaisesRegex(RuntimeError, "exact validated candidate"):
                MODULE.update_release_notes(worktree, "v0.10.0")


if __name__ == "__main__":
    unittest.main()
