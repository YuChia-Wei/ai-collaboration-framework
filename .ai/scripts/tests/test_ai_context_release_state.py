#!/usr/bin/env python3
"""Given-When-Then tests for read-only release phase validation."""

from __future__ import annotations

import importlib.util
import json
import subprocess
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[3]
SCRIPT = ROOT / ".ai" / "scripts" / "validate-ai-context-release-state.py"
SPEC = importlib.util.spec_from_file_location("release_state", SCRIPT)
assert SPEC and SPEC.loader
STATE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(STATE)

SHA = "a" * 40
VERSION = "v0.5.0"
BRANCH = "codex/release"
PACKAGE_ID = "ai-context-dotnet-backend-v0.5.0"
BACKLOG_REF = ".dev/backlog/items/REL-001.yaml"


def release_data(status: str = "validated") -> dict:
    published = status == "published"
    return {
        "schema_version": "1.0",
        "release_id": f"REL-{VERSION}",
        "version": VERSION,
        "status": status,
        "record_origin": "governed",
        "distribution_kind": "governed-package",
        "installable": True,
        "tag": VERSION if published else None,
        "commit": SHA if published else None,
        "tagged_at": "2026-07-20T02:00:00+00:00" if published else None,
        "recorded_at": "2026-07-20T02:10:00+00:00" if published else None,
        "created_at": "2026-07-20T01:00:00+00:00",
        "updated_at": "2026-07-20T02:20:00+00:00",
        "planning": {"backlog_refs": [BACKLOG_REF]},
        "compatibility": {
            "breaking_changes": True,
            "minimum_source_version": "v0.3.0",
            "reconciliation_sources": ["v0.3.0", "v0.4.0", "v0.4.1", "v0.4.2"],
            "automatic_upgrade_sources": ["v0.3.0", "v0.4.0", "v0.4.1", "v0.4.2"],
            "affected_contracts": ["migration metadata"],
        },
        "artifacts": {
            "release_notes": "release-notes.md",
            "migration_guide": "migration-guide.md",
        },
        "distribution": {
            "profile_id": "dotnet-backend",
            "package_id": PACKAGE_ID,
            "schema_versions": {
                "package": "1.0.0",
                "files": "1.0.0",
                "migration": "2.0.0",
            },
            "artifacts": {
                "zip": f"{PACKAGE_ID}.zip",
                "zip_checksum": f"{PACKAGE_ID}.zip.sha256",
                "tar_gz": f"{PACKAGE_ID}.tar.gz",
                "tar_gz_checksum": f"{PACKAGE_ID}.tar.gz.sha256",
            },
        },
        "validation": {
            "package_status": "validated",
            "published_run": "42" if published else None,
            "public_release_url": (
                f"https://github.com/owner/repo/releases/tag/{VERSION}"
                if published
                else None
            ),
        },
    }


def write_fixture(
    root: Path,
    *,
    status: str = "validated",
    authored_notes: str | None = None,
    migration: str | None = None,
) -> Path:
    release = root / ".dev" / "releases" / VERSION
    release.mkdir(parents=True)
    contract = {
        "schema_version": "1.0",
        "release": VERSION,
        "phases": {
            phase: {"command": command}
            for phase, command in STATE.sanctioned_commands(VERSION).items()
        },
    }
    (release / "release-phase-checks.yaml").write_text(
        yaml.safe_dump(contract, sort_keys=False),
        encoding="utf-8",
    )
    backlog_path = root / BACKLOG_REF
    backlog_path.parent.mkdir(parents=True)
    backlog_path.write_text(
        yaml.safe_dump(
            {
                "backlog_id": "REL-001",
                "status": "resolved",
                "release": {
                    "target": VERSION,
                    "completed_in": VERSION,
                    "published_in": None,
                },
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )
    (release / "release.yaml").write_text(
        yaml.safe_dump(release_data(status), sort_keys=False),
        encoding="utf-8",
    )
    (release / "release-notes.md").write_text(
        authored_notes
        or (
            "# REL-v0.5.0 - Published\n\n"
            "## Status\n\n"
            "Published.\n\n"
            "## Release Validation\n\n"
            "The published release validation passed.\n\n"
            "## Publication Completion\n\n"
            "Published from immutable annotated tag `v0.5.0`.\n"
            if status == "published"
            else "# REL-v0.5.0 - Candidate\n\n"
            "Supports governed upgrades from v0.3.0, v0.4.0, v0.4.1, and v0.4.2.\n"
        ),
        encoding="utf-8",
    )
    (release / "migration-guide.md").write_text(
        migration
        or (
            "# Migrate To v0.5.0\n\n"
            "Choose the exact v0.3.0, v0.4.0, v0.4.1, or v0.4.2 inventory.\n"
        ),
        encoding="utf-8",
    )
    renderer = root / STATE.RENDERER_PATH
    renderer.parent.mkdir(parents=True, exist_ok=True)
    renderer.write_text(
        (ROOT / STATE.RENDERER_PATH).read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    return release


def fake_runner(
    *,
    dirty: bool = False,
    tag: bool = True,
    release: dict | None = None,
    workflow: dict | None = None,
):
    def execute(args, cwd, capture_output, text, check):
        if args == ["git", "status", "--porcelain=v1", "--untracked-files=all"]:
            output = " M .dev/releases/v0.5.0/release-notes.md\n" if dirty else ""
        elif args[:3] == ["git", "cat-file", "-t"]:
            output = "tag\n" if tag else "commit\n"
        elif args == ["git", "rev-parse", "HEAD"]:
            output = SHA + "\n"
        elif args[:2] == ["git", "rev-parse"]:
            output = SHA + "\n"
        elif args == ["git", "branch", "--show-current"]:
            output = BRANCH + "\n"
        elif args[:2] == ["git", "show"]:
            if args[-1].endswith("/release.yaml"):
                tagged = release_data("validated")
                output = yaml.safe_dump(tagged, sort_keys=False)
            elif args[-1].endswith("/release-notes.md"):
                output = "# REL-v0.5.0 - Candidate\n\nGoverned notes.\n"
            else:
                output = "# Migrate To v0.5.0\n\nGoverned migration.\n"
        elif args == ["git", "config", "--get", "remote.origin.url"]:
            output = "https://github.com/owner/repo.git\n"
        elif args[:4] == ["gh", "api", "--method", "GET"]:
            endpoint = args[-1]
            if "/actions/workflows/" in endpoint:
                value = {
                    "workflow_runs": [
                        {
                            "id": 42,
                            "conclusion": "success",
                            "head_sha": SHA,
                            "event": "push",
                            "path": STATE.PUBLISH_WORKFLOW_PATH,
                        }
                    ]
                }
            elif "/actions/runs/" in endpoint:
                value = workflow
            else:
                value = release
            output = json.dumps(value) + "\n"
        else:
            raise AssertionError(f"unexpected read-only command: {args}")
        return subprocess.CompletedProcess(args, 0, output, "")

    return execute


def hosted_release(body: str = "rendered body\n") -> dict:
    return {
        "draft": False,
        "prerelease": False,
        "tag_name": VERSION,
        "name": f"REL-{VERSION}",
        "published_at": "2026-07-21T01:05:00Z",
        "body": body,
        "assets": [
            {"name": name}
            for name in (
                f"{PACKAGE_ID}.zip",
                f"{PACKAGE_ID}.zip.sha256",
                f"{PACKAGE_ID}.tar.gz",
                f"{PACKAGE_ID}.tar.gz.sha256",
            )
        ],
    }


def hosted_workflow() -> dict:
    return {
        "conclusion": "success",
        "head_sha": SHA,
        "event": "push",
        "path": STATE.PUBLISH_WORKFLOW_PATH,
    }


class AiContextReleaseStateGwtTests(unittest.TestCase):
    def test_gwt_001_given_validated_clean_candidate_when_checked_then_prior_source_versions_are_allowed(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            write_fixture(root)
            STATE.validate(root, "candidate", VERSION, runner=fake_runner())

    def test_gwt_002_given_candidate_with_dirty_worktree_when_checked_then_it_fails_closed(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            write_fixture(root)
            with self.assertRaisesRegex(STATE.ReleaseStateError, "clean source worktree"):
                STATE.validate(
                    root,
                    "candidate",
                    VERSION,
                    runner=fake_runner(dirty=True),
                )

    def test_gwt_003_given_candidate_identity_drift_when_checked_then_it_fails_closed(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            write_fixture(root)
            with self.assertRaisesRegex(STATE.ReleaseStateError, "--branch"):
                STATE.validate(
                    root,
                    "candidate",
                    VERSION,
                    SHA,
                    "main",
                    runner=fake_runner(),
                )

    def test_gwt_004_given_rendered_provenance_in_authored_notes_when_checked_then_it_fails_closed(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            write_fixture(
                root,
                authored_notes=(
                    "# REL-v0.5.0 - Candidate\n"
                    "<!-- ai-context-release-automation: REL-v0.5.0 -->\n"
                ),
            )
            with self.assertRaisesRegex(
                STATE.ReleaseStateError, "rendered release provenance"
            ):
                STATE.validate(root, "candidate", VERSION, runner=fake_runner())

    def test_gwt_005_given_copied_release_heading_when_checked_then_it_fails_closed(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            write_fixture(root, authored_notes="# REL-v0.4.2 - Copied\n")
            with self.assertRaisesRegex(STATE.ReleaseStateError, "first heading"):
                STATE.validate(root, "candidate", VERSION, runner=fake_runner())

    def test_gwt_006_given_stale_publication_fields_when_candidate_checked_then_it_fails_closed(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            release = write_fixture(root)
            data = yaml.safe_load((release / "release.yaml").read_text(encoding="utf-8"))
            data["validation"]["published_run"] = "29679273269"
            (release / "release.yaml").write_text(
                yaml.safe_dump(data, sort_keys=False),
                encoding="utf-8",
            )
            with self.assertRaisesRegex(STATE.ReleaseStateError, "published_run"):
                STATE.validate(root, "candidate", VERSION, runner=fake_runner())

    def test_gwt_007_given_unrelated_backlog_ref_when_candidate_checked_then_it_fails_closed(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            write_fixture(root)
            backlog = root / BACKLOG_REF
            data = yaml.safe_load(backlog.read_text(encoding="utf-8"))
            data["release"]["target"] = "v0.6.0"
            backlog.write_text(
                yaml.safe_dump(data, sort_keys=False),
                encoding="utf-8",
            )
            with self.assertRaisesRegex(STATE.ReleaseStateError, "unrelated"):
                STATE.validate(root, "candidate", VERSION, runner=fake_runner())

    def test_gwt_008_given_future_timestamp_when_candidate_checked_then_it_fails_closed(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            release = write_fixture(root)
            data = yaml.safe_load((release / "release.yaml").read_text(encoding="utf-8"))
            data["updated_at"] = (
                datetime.now(timezone.utc) + timedelta(days=1)
            ).isoformat()
            (release / "release.yaml").write_text(
                yaml.safe_dump(data, sort_keys=False),
                encoding="utf-8",
            )
            with self.assertRaisesRegex(STATE.ReleaseStateError, "future"):
                STATE.validate(root, "candidate", VERSION, runner=fake_runner())

    def test_gwt_009_given_existing_lightweight_tag_when_tag_checked_then_it_fails_closed(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            write_fixture(root)
            with self.assertRaisesRegex(STATE.ReleaseStateError, "annotated"):
                STATE.validate(root, "tag", VERSION, runner=fake_runner(tag=False))

    def test_gwt_010_given_unowned_phase_command_when_checked_then_it_fails_closed(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            write_fixture(root)
            contract_path = (
                root / f".dev/releases/{VERSION}/release-phase-checks.yaml"
            )
            contract = yaml.safe_load(contract_path.read_text(encoding="utf-8"))
            contract["phases"]["candidate"]["command"] = "bash -c arbitrary"
            contract_path.write_text(
                yaml.safe_dump(contract, sort_keys=False),
                encoding="utf-8",
            )
            with self.assertRaisesRegex(STATE.ReleaseStateError, "not the sanctioned"):
                STATE.validate(root, "candidate", VERSION, runner=fake_runner())

    def test_gwt_011_given_validated_tag_and_exact_hosted_release_when_publication_checked_then_it_passes(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            write_fixture(root)
            body = root / "body.md"
            body.write_text("rendered body\n", encoding="utf-8")
            STATE.validate(
                root,
                "publication",
                VERSION,
                repository="owner/repo",
                rendered_body=body,
                workflow_run_id="42",
                hosted=True,
                runner=fake_runner(
                    release=hosted_release(),
                    workflow=hosted_workflow(),
                ),
            )

    def test_gwt_012_given_published_record_and_exact_hosted_release_when_finalized_then_it_passes(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            write_fixture(root, status="published")
            body = root / "body.md"
            expected = STATE.render_published_body(root, VERSION, SHA)
            body.write_text(expected, encoding="utf-8")
            STATE.validate(
                root,
                "finalization",
                VERSION,
                repository="owner/repo",
                rendered_body=body,
                hosted=True,
                runner=fake_runner(
                    release=hosted_release(expected),
                    workflow=hosted_workflow(),
                ),
            )

    def test_gwt_013_given_hosted_body_that_drifts_when_checked_then_it_fails_closed(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            write_fixture(root)
            body = root / "body.md"
            body.write_text("expected", encoding="utf-8")
            with self.assertRaisesRegex(STATE.ReleaseStateError, "body differs"):
                STATE.validate(
                    root,
                    "publication",
                    VERSION,
                    repository="owner/repo",
                    rendered_body=body,
                    workflow_run_id="42",
                    hosted=True,
                    runner=fake_runner(
                        release=hosted_release("wrong"),
                        workflow=hosted_workflow(),
                    ),
                )

    def test_gwt_024_given_published_record_with_hosted_candidate_body_when_finalized_then_it_fails_closed(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            write_fixture(root, status="published")
            stale_candidate_body = (
                "## Status\n\n"
                "Validated governed candidate. v0.5.0 is not tagged or published.\n\n"
                "## Publication Completion\n\n"
                "Not published.\n"
            )
            with self.assertRaisesRegex(STATE.ReleaseStateError, "body differs"):
                STATE.validate(
                    root,
                    "finalization",
                    VERSION,
                    repository="owner/repo",
                    workflow_run_id="42",
                    hosted=True,
                    runner=fake_runner(
                        release=hosted_release(stale_candidate_body),
                        workflow=hosted_workflow(),
                    ),
                )

    def test_gwt_014_given_missing_phase_contract_when_checked_then_it_fails_closed(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            write_fixture(root)
            (root / f".dev/releases/{VERSION}/release-phase-checks.yaml").unlink()
            with self.assertRaisesRegex(STATE.ReleaseStateError, "cannot read"):
                STATE.validate(root, "candidate", VERSION, runner=fake_runner())

    def test_gwt_015_given_git_write_command_when_read_only_runner_called_then_it_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaisesRegex(STATE.ReleaseStateError, "read-only allowlist"):
                STATE.run_read_only(
                    Path(temp),
                    ["git", "tag", "-a", VERSION],
                    fake_runner(),
                )

    def test_gwt_016_given_v060_contract_when_required_then_versioned_commands_pass(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            version = "v0.6.0"
            release = root / ".dev" / "releases" / version
            release.mkdir(parents=True)
            contract = {
                "schema_version": "1.0",
                "release": version,
                "phases": {
                    phase: {"command": command}
                    for phase, command in STATE.sanctioned_commands(version).items()
                },
            }
            (release / "release-phase-checks.yaml").write_text(
                yaml.safe_dump(contract, sort_keys=False),
                encoding="utf-8",
            )

            entry = STATE.require_phase_contract(root, "publication", version)

            self.assertIn("--version v0.6.0 --hosted", entry["command"])

    def test_gwt_017_given_only_legacy_singleton_when_required_then_it_is_not_accepted(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            singleton = root / ".dev" / "releases" / "release-phase-checks.yaml"
            singleton.parent.mkdir(parents=True)
            singleton.write_text(
                yaml.safe_dump(
                    {
                        "schema_version": "1.0",
                        "release": VERSION,
                        "phases": {
                            phase: {"command": command}
                            for phase, command in STATE.sanctioned_commands(
                                VERSION
                            ).items()
                        },
                    },
                    sort_keys=False,
                ),
                encoding="utf-8",
            )

            with self.assertRaisesRegex(STATE.ReleaseStateError, VERSION):
                STATE.require_phase_contract(root, "candidate", VERSION)

    def test_gwt_018_given_unsafe_version_when_required_then_it_fails_before_path_lookup(self):
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaisesRegex(
                STATE.ReleaseStateError,
                "stable vMAJOR.MINOR.PATCH",
            ):
                STATE.require_phase_contract(
                    Path(temp),
                    "candidate",
                    "../v0.6.0",
                )

    def write_backlog(
        self,
        root: Path,
        backlog_id: str,
        *,
        status: str = "resolved",
        target: str = "v0.7.0",
        completed_in: str | None = "v0.7.0",
        published_in: str | None = None,
    ) -> str:
        ref = f".dev/backlog/items/{backlog_id}.yaml"
        path = root / ref
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            yaml.safe_dump(
                {
                    "backlog_id": backlog_id,
                    "status": status,
                    "release": {
                        "target": target,
                        "completed_in": completed_in,
                        "published_in": published_in,
                    },
                },
                sort_keys=False,
            ),
            encoding="utf-8",
        )
        return ref

    def test_gwt_019_given_exact_canonical_backlog_set_when_validated_then_it_passes(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            refs = [
                self.write_backlog(root, "GOV-002"),
                self.write_backlog(root, "GOV-003"),
                self.write_backlog(root, "PKG-004"),
            ]
            STATE.validate_backlog_refs(
                root, "v0.7.0", {"planning": {"backlog_refs": refs}}
            )

    def test_gwt_020_given_canonical_backlog_item_missing_when_validated_then_it_fails_closed(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            included = self.write_backlog(root, "GOV-002")
            self.write_backlog(root, "GOV-003")
            with self.assertRaisesRegex(STATE.ReleaseStateError, "exactly equal"):
                STATE.validate_backlog_refs(
                    root,
                    "v0.7.0",
                    {"planning": {"backlog_refs": [included]}},
                )

    def test_gwt_021_given_duplicate_backlog_ref_when_validated_then_it_fails_closed(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            ref = self.write_backlog(root, "GOV-002")
            with self.assertRaisesRegex(STATE.ReleaseStateError, "duplicates"):
                STATE.validate_backlog_refs(
                    root,
                    "v0.7.0",
                    {"planning": {"backlog_refs": [ref, ref]}},
                )

    def test_gwt_022_given_unrelated_or_unresolved_backlog_when_validated_then_it_fails_closed(self):
        cases = [
            {"target": "v0.6.0"},
            {"status": "planned", "completed_in": None},
        ]
        for case in cases:
            with self.subTest(case=case), tempfile.TemporaryDirectory() as temp:
                root = Path(temp)
                ref = self.write_backlog(root, "GOV-002", **case)
                with self.assertRaises(STATE.ReleaseStateError):
                    STATE.validate_backlog_refs(
                        root,
                        "v0.7.0",
                        {"planning": {"backlog_refs": [ref]}},
                    )

    def test_gwt_023_given_completion_or_publication_mismatch_when_validated_then_it_fails_closed(self):
        cases = [
            {"completed_in": "v0.6.0"},
            {"published_in": "v0.7.0"},
        ]
        for case in cases:
            with self.subTest(case=case), tempfile.TemporaryDirectory() as temp:
                root = Path(temp)
                ref = self.write_backlog(root, "GOV-002", **case)
                with self.assertRaises(STATE.ReleaseStateError):
                    STATE.validate_backlog_refs(
                        root,
                        "v0.7.0",
                        {"planning": {"backlog_refs": [ref]}},
                    )


if __name__ == "__main__":
    unittest.main()
