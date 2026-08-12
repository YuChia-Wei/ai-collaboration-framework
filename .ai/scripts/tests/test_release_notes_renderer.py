#!/usr/bin/env python3
"""Focused GWT tests for governed release-body rendering."""

from __future__ import annotations

import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import yaml


REPO_ROOT = Path(__file__).resolve().parents[3]
RENDERER_PATH = REPO_ROOT / ".ai/scripts/render-ai-context-release-notes.py"
SPEC = importlib.util.spec_from_file_location("release_notes_renderer", RENDERER_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"Unable to load renderer: {RENDERER_PATH}")
RENDERER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(RENDERER)
COMMIT = "a" * 40


def git(root: Path, *args: str) -> str:
    completed = subprocess.run(
        ["git", *args],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


def release_record(migration_schema: str, sources: list[str]) -> dict:
    return {
        "schema_version": "1.0",
        "release_id": "REL-v0.5.0",
        "version": "v0.5.0",
        "status": "validated",
        "record_origin": "governed",
        "tag": None,
        "commit": None,
        "compatibility": {"breaking_changes": True, "automatic_upgrade_sources": sources},
        "artifacts": {"release_notes": "release-notes.md", "migration_guide": "migration-guide.md"},
        "distribution": {"schema_versions": {"migration": migration_schema}},
    }


def published_release_record() -> dict:
    data = release_record("1.0.0", ["v0.3.0"])
    data.update({"status": "published", "tag": "v0.5.0", "commit": COMMIT})
    data["validation"] = {
        "published_run": "42",
        "public_release_url": "https://github.com/owner/repo/releases/tag/v0.5.0",
    }
    return data


class ReleaseNotesRendererTests(unittest.TestCase):
    def write_release(self, root: Path, data: dict) -> None:
        release = root / ".dev/releases/v0.5.0"
        release.mkdir(parents=True)
        (release / "release.yaml").write_text(yaml.safe_dump(data), encoding="utf-8")
        (release / "release-notes.md").write_text("# Authored notes\n", encoding="utf-8")
        (release / "migration-guide.md").write_text("# Migration\n", encoding="utf-8")

    def write_discovery_release(
        self,
        root: Path,
        version: str,
        *,
        status: str = "validated",
        record_origin: str = "governed",
    ) -> None:
        release = root / ".dev" / "releases" / version
        release.mkdir(parents=True, exist_ok=True)
        data = {
            "schema_version": "1.0",
            "release_id": f"REL-{version}",
            "version": version,
            "status": status,
            "record_origin": record_origin,
        }
        (release / "release.yaml").write_text(
            yaml.safe_dump(data, sort_keys=False),
            encoding="utf-8",
        )

    def initialize_git_repository(self, root: Path) -> None:
        git(root, "init", "-q")
        git(root, "config", "user.name", "Release fixture")
        git(root, "config", "user.email", "release-fixture@example.invalid")

    def commit_all(self, root: Path, message: str) -> str:
        git(root, "add", ".")
        git(root, "commit", "-qm", message)
        return git(root, "rev-parse", "HEAD")

    def test_gwt_001_given_schema_2_multi_source_candidate_when_validated_then_renders(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.write_release(
                root,
                release_record(
                    "2.0.0", ["v0.3.0", "v0.4.0", "v0.4.1", "v0.4.2"]
                ),
            )
            data, notes, migration = RENDERER.validate_release(root, "v0.5.0", COMMIT, "candidate")
            self.assertIn("v0.4.1", data["compatibility"]["automatic_upgrade_sources"])
            self.assertIn("v0.4.2", data["compatibility"]["automatic_upgrade_sources"])
            self.assertEqual("# Authored notes", notes.read_text(encoding="utf-8").strip())
            self.assertEqual("# Migration", migration.read_text(encoding="utf-8").strip())

    def test_gwt_002_given_schema_1_multi_source_candidate_when_validated_then_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.write_release(root, release_record("1.0.0", ["v0.3.0", "v0.4.0"]))
            with self.assertRaisesRegex(RENDERER.ReleaseNotesError, "schema 2.0.0"):
                RENDERER.validate_release(root, "v0.5.0", COMMIT, "candidate")

    def test_gwt_003_given_schema_1_single_source_when_validated_then_remains_compatible(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.write_release(root, release_record("1.0.0", ["v0.3.0"]))
            data, _, _ = RENDERER.validate_release(root, "v0.5.0", COMMIT, "candidate")
            self.assertEqual(["v0.3.0"], data["compatibility"]["automatic_upgrade_sources"])

    def test_gwt_004_given_v070_backlog_refs_when_rendered_then_authored_notes_and_exact_included_work_are_preserved(self) -> None:
        data = release_record("2.0.0", ["v0.6.0"])
        data.update({"release_id": "REL-v0.7.0", "version": "v0.7.0"})
        data["planning"] = {
            "backlog_refs": [
                ".dev/backlog/items/GOV-002.yaml",
                ".dev/backlog/items/GOV-003.yaml",
                ".dev/backlog/items/PKG-004.yaml",
            ]
        }
        authored = "# Human-authored release notes\n\nKeep this paragraph byte-for-byte."
        rendered = RENDERER.render_body_text(data, authored, "# Migration", COMMIT)
        self.assertIn(authored, rendered)
        included = rendered.split("## Included Work", 1)[1].split(
            "## Release provenance", 1
        )[0]
        for work_id in ("GOV-002", "GOV-003", "PKG-004"):
            self.assertEqual(1, included.count(f"`{work_id}`"))

    def test_gwt_005_given_v070_missing_or_duplicate_backlog_refs_when_rendered_then_it_fails_closed(self) -> None:
        data = release_record("2.0.0", ["v0.6.0"])
        data.update({"release_id": "REL-v0.7.0", "version": "v0.7.0"})
        data["planning"] = {}
        with self.assertRaisesRegex(RENDERER.ReleaseNotesError, "non-empty"):
            RENDERER.render_body_text(data, "# Notes", "# Migration", COMMIT)
        data["planning"] = {
            "backlog_refs": [
                ".dev/backlog/items/GOV-002.yaml",
                ".dev/backlog/items/GOV-002.yaml",
            ]
        }
        with self.assertRaisesRegex(RENDERER.ReleaseNotesError, "duplicates"):
            RENDERER.render_body_text(data, "# Notes", "# Migration", COMMIT)

    def test_gwt_005a_given_v010_online_issue_refs_when_rendered_then_they_are_the_exact_included_work(self) -> None:
        data = release_record("3.0.0", ["v0.9.0"])
        data.update({"release_id": "REL-v0.10.0", "version": "v0.10.0"})
        data["planning"] = {"github_issue_refs": ["#96", "#135", "#57"]}
        rendered = RENDERER.render_body_text(data, "# Notes", "# Migration", COMMIT)
        included = rendered.split("## Included Work", 1)[1].split(
            "## Release provenance", 1
        )[0]
        for issue_ref in ("#96", "#135", "#57"):
            self.assertEqual(1, included.count(f"`{issue_ref}`"))

    def test_gwt_006_given_pre_v070_release_when_rendered_then_historical_shape_remains_compatible(self) -> None:
        data = release_record("1.0.0", ["v0.4.2"])
        rendered = RENDERER.render_body_text(data, "# Notes", "# Migration", COMMIT)
        self.assertNotIn("## Included Work", rendered)

    def test_gwt_007_given_published_record_when_rendered_then_phase_truth_is_preserved(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.write_release(root, published_release_record())
            notes_path = root / ".dev/releases/v0.5.0/release-notes.md"
            notes_path.write_text(
                "# REL-v0.5.0 - Published\n\n"
                "## Status\n\n"
                "Published.\n\n"
                "## Release Validation\n\n"
                "The published release validation passed.\n\n"
                "## Publication Completion\n\n"
                "Published from immutable annotated tag `v0.5.0`.\n",
                encoding="utf-8",
            )

            data, notes, migration = RENDERER.validate_release(
                root, "v0.5.0", COMMIT, "published"
            )
            rendered = RENDERER.render_body(data, notes, migration, COMMIT)

            self.assertIn("## Status\n\nPublished.", rendered)
            self.assertIn("## Release provenance", rendered)

    def test_gwt_008_given_published_record_with_candidate_claim_when_rendered_then_it_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.write_release(root, published_release_record())
            notes_path = root / ".dev/releases/v0.5.0/release-notes.md"
            notes_path.write_text(
                "# REL-v0.5.0 - Published\n\n"
                "## Status\n\n"
                "Published.\n\n"
                "## Release Validation\n\n"
                "Tag and publication remain unperformed.\n\n"
                "## Publication Completion\n\n"
                "Not published.\n",
                encoding="utf-8",
            )

            with self.assertRaisesRegex(RENDERER.ReleaseNotesError, "candidate-only"):
                RENDERER.validate_release(root, "v0.5.0", COMMIT, "published")

    def test_gwt_009_given_validated_history_when_pr_adds_one_candidate_then_changed_candidate_is_selected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.initialize_git_repository(root)
            self.write_discovery_release(root, "v0.12.0")
            base = self.commit_all(root, "validated historical release")

            self.write_discovery_release(root, "v0.13.0")
            head = self.commit_all(root, "add current candidate")

            self.assertEqual(
                "v0.13.0",
                RENDERER.discover_candidate(root, base, head),
            )

    def test_gwt_010_given_validated_history_when_pr_changes_no_release_record_then_packaging_is_not_applicable(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.initialize_git_repository(root)
            self.write_discovery_release(root, "v0.12.0")
            base = self.commit_all(root, "validated historical release")

            (root / "README.md").write_text("tooling-only change\n", encoding="utf-8")
            head = self.commit_all(root, "change tooling only")

            with self.assertRaises(RENDERER.CandidateNotApplicable):
                RENDERER.discover_candidate(root, base, head)
            completed = subprocess.run(
                [
                    sys.executable,
                    str(RENDERER_PATH),
                    "--root",
                    str(root),
                    "--base-commit",
                    base,
                    "--head-commit",
                    head,
                    "--commit",
                    head,
                    "--output",
                    str(root / "release-body.md"),
                ],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(
                RENDERER.CANDIDATE_NOT_APPLICABLE_EXIT_CODE,
                completed.returncode,
                completed.stdout + completed.stderr,
            )
            self.assertIn("not applicable", completed.stderr)

    def test_gwt_011_given_pr_changes_multiple_candidates_when_selected_then_it_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.initialize_git_repository(root)
            self.write_discovery_release(root, "v0.12.0")
            base = self.commit_all(root, "validated historical release")

            self.write_discovery_release(root, "v0.13.0")
            self.write_discovery_release(root, "v0.14.0", status="planned")
            head = self.commit_all(root, "add two candidates")

            with self.assertRaisesRegex(
                RENDERER.ReleaseNotesError,
                "found v0.13.0, v0.14.0",
            ):
                RENDERER.discover_candidate(root, base, head)

    def test_gwt_012_given_pr_deletes_a_release_record_when_selected_then_it_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.initialize_git_repository(root)
            self.write_discovery_release(root, "v0.12.0")
            base = self.commit_all(root, "validated historical release")

            (root / ".dev/releases/v0.12.0/release.yaml").unlink()
            head = self.commit_all(root, "delete release record")

            with self.assertRaisesRegex(
                RENDERER.ReleaseNotesError,
                "must not be deleted",
            ):
                RENDERER.discover_candidate(root, base, head)


if __name__ == "__main__":
    unittest.main()
