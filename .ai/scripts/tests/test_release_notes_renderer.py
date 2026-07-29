#!/usr/bin/env python3
"""Focused GWT tests for governed release-body rendering."""

from __future__ import annotations

import importlib.util
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


if __name__ == "__main__":
    unittest.main()
