#!/usr/bin/env python3
"""Given-When-Then tests for read-only release phase validation."""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

import yaml


ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / ".ai/scripts"))
# Tracked as ephemeral-fixture-io in test-fixture-classifications.json.
import test_fixture_runtime as tempfile  # noqa: E402
tempfile.bind_classified_test(__file__, ROOT)

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
    tagged_data: dict | None = None,
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
                tagged = tagged_data or release_data("validated")
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

    def test_gwt_025_given_v010_candidate_when_tag_policy_is_checked_then_only_the_bounded_agent_exception_passes(self):
        data = release_data()
        data["version"] = "v0.10.0"
        data["release_id"] = "REL-v0.10.0"
        data["distribution"]["package_id"] = "ai-context-dotnet-backend-v0.10.0"
        data["distribution"]["artifacts"] = {
            "zip": "ai-context-dotnet-backend-v0.10.0.zip",
            "zip_checksum": "ai-context-dotnet-backend-v0.10.0.zip.sha256",
            "tar_gz": "ai-context-dotnet-backend-v0.10.0.tar.gz",
            "tar_gz_checksum": "ai-context-dotnet-backend-v0.10.0.tar.gz.sha256",
        }
        data["distribution"]["publication"] = dict(
            STATE.V010_AGENT_PUBLICATION_AUTHORITY
        )
        STATE.validate_publication_authority("v0.10.0", data["distribution"])
        data["distribution"]["publication"]["tag_owner"] = "user"
        with self.assertRaisesRegex(STATE.ReleaseStateError, "bounded owner-authorized Terra"):
            STATE.validate_publication_authority("v0.10.0", data["distribution"])

    def test_gwt_025a_given_v011_tag_when_checked_then_only_the_exact_sol_exception_passes(self):
        data = release_data()
        data["distribution"]["publication"] = dict(
            STATE.V011_AGENT_PUBLICATION_AUTHORITY
        )
        STATE.validate_publication_authority("v0.11.0", data["distribution"])
        data["distribution"]["publication"]["automation"] = "github-actions"
        with self.assertRaisesRegex(STATE.ReleaseStateError, "bounded owner-authorized Sol"):
            STATE.validate_publication_authority("v0.11.0", data["distribution"])

    def test_gwt_025b_given_immutable_v011_tagged_candidate_when_read_then_only_the_exact_historical_skeleton_passes(self):
        tagged = release_data()
        tagged.update(
            {
                "release_id": "REL-v0.11.0",
                "version": "v0.11.0",
                "status": "candidate",
                "tag": "v0.11.0",
                "commit": "pending-exact-candidate",
            }
        )
        tagged["distribution"]["publication"] = dict(
            STATE.V011_TAGGED_PUBLICATION_AUTHORITY
        )
        tagged["validation"]["package_status"] = "deferred-with-owner"
        self.assertEqual(
            tagged,
            STATE.tagged_release_record(
                Path("."), "v0.11.0", fake_runner(tagged_data=tagged)
            ),
        )
        tagged["commit"] = "different"
        with self.assertRaisesRegex(STATE.ReleaseStateError, "validated registry skeleton"):
            STATE.tagged_release_record(
                Path("."), "v0.11.0", fake_runner(tagged_data=tagged)
            )

    def test_gwt_025c_given_exact_failed_v011_publication_run_when_checked_then_the_bounded_deviation_passes(self):
        failed = {
            "conclusion": "failure",
            "head_sha": STATE.V011_TAGGED_COMMIT,
            "event": "push",
            "path": STATE.PUBLISH_WORKFLOW_PATH,
        }
        STATE.assert_hosted_workflow(
            Path("."),
            "owner/repo",
            "v0.11.0",
            STATE.V011_FAILED_PUBLICATION_RUN,
            STATE.V011_TAGGED_COMMIT,
            fake_runner(workflow=failed),
        )
        with self.assertRaisesRegex(STATE.ReleaseStateError, "must have succeeded"):
            STATE.assert_hosted_workflow(
                Path("."),
                "owner/repo",
                "v0.11.0",
                "1",
                STATE.V011_TAGGED_COMMIT,
                fake_runner(workflow=failed),
            )
        with self.assertRaisesRegex(STATE.ReleaseStateError, "must have succeeded"):
            STATE.assert_hosted_workflow(
                Path("."),
                "owner/repo",
                "v0.12.0",
                STATE.V011_FAILED_PUBLICATION_RUN,
                STATE.V011_TAGGED_COMMIT,
                fake_runner(workflow=failed),
            )

    def test_gwt_026_given_v010_online_issue_scope_when_candidate_checked_then_live_open_targeted_issues_are_required(self):
        data = release_data()
        data["version"] = "v0.10.0"
        data["release_id"] = "REL-v0.10.0"
        data["distribution"]["package_id"] = "ai-context-dotnet-backend-v0.10.0"
        data["distribution"]["artifacts"] = {
            "zip": "ai-context-dotnet-backend-v0.10.0.zip",
            "zip_checksum": "ai-context-dotnet-backend-v0.10.0.zip.sha256",
            "tar_gz": "ai-context-dotnet-backend-v0.10.0.tar.gz",
            "tar_gz_checksum": "ai-context-dotnet-backend-v0.10.0.tar.gz.sha256",
        }
        data["distribution"]["publication"] = dict(
            STATE.V010_AGENT_PUBLICATION_AUTHORITY
        )
        data["planning"] = {"github_issue_refs": ["#96", "#135"]}
        baseline = fake_runner()

        def online_runner(args, cwd, capture_output, text, check):
            if args[:4] == ["gh", "api", "--method", "GET"] and "/issues/" in args[-1]:
                number = int(args[-1].rsplit("/", 1)[1])
                return subprocess.CompletedProcess(
                    args,
                    0,
                    json.dumps(
                        {
                            "number": number,
                            "state": "open",
                            "body": "## Target Release\n\nv0.10.0\n",
                        }
                    )
                    + "\n",
                    "",
                )
            return baseline(args, cwd, capture_output, text, check)

        with tempfile.TemporaryDirectory() as temp:
            STATE.validate_candidate_record(Path(temp), "v0.10.0", data, online_runner)

        def closed_runner(args, cwd, capture_output, text, check):
            result = online_runner(args, cwd, capture_output, text, check)
            if args[:4] == ["gh", "api", "--method", "GET"] and "/issues/" in args[-1]:
                payload = json.loads(result.stdout)
                payload["state"] = "closed"
                return subprocess.CompletedProcess(args, 0, json.dumps(payload) + "\n", "")
            return result

        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaisesRegex(STATE.ReleaseStateError, "must remain open"):
                STATE.validate_candidate_record(Path(temp), "v0.10.0", data, closed_runner)

    def test_gwt_027_given_v012_online_issue_scope_when_candidate_checked_then_closed_completed_issues_are_required(self):
        version = "v0.12.0"
        package_id = f"ai-context-dotnet-backend-{version}"
        data = release_data()
        data["version"] = version
        data["release_id"] = f"REL-{version}"
        data["planning"] = {"github_issue_refs": ["#167", "#184"]}
        data["distribution"]["package_id"] = package_id
        data["distribution"]["artifacts"] = {
            "zip": f"{package_id}.zip",
            "zip_checksum": f"{package_id}.zip.sha256",
            "tar_gz": f"{package_id}.tar.gz",
            "tar_gz_checksum": f"{package_id}.tar.gz.sha256",
        }
        baseline = fake_runner()

        def completed_runner(args, cwd, capture_output, text, check):
            if args[:4] == ["gh", "api", "--method", "GET"] and "/issues/" in args[-1]:
                number = int(args[-1].rsplit("/", 1)[1])
                return subprocess.CompletedProcess(
                    args,
                    0,
                    json.dumps(
                        {
                            "number": number,
                            "state": "closed",
                            "state_reason": "completed",
                            "body": f"Target release: {version}",
                        }
                    )
                    + "\n",
                    "",
                )
            return baseline(args, cwd, capture_output, text, check)

        with tempfile.TemporaryDirectory() as temp:
            STATE.validate_candidate_record(Path(temp), version, data, completed_runner)

        def open_runner(args, cwd, capture_output, text, check):
            result = completed_runner(args, cwd, capture_output, text, check)
            if args[:4] == ["gh", "api", "--method", "GET"] and "/issues/" in args[-1]:
                payload = json.loads(result.stdout)
                payload["state"] = "open"
                payload["state_reason"] = None
                return subprocess.CompletedProcess(args, 0, json.dumps(payload) + "\n", "")
            return result

        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaisesRegex(STATE.ReleaseStateError, "closed with completed"):
                STATE.validate_candidate_record(Path(temp), version, data, open_runner)

    def test_gwt_028_given_terminal_validated_source_when_hosted_finalization_runs_then_no_published_source_rewrite_is_required(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            write_fixture(root, status="validated")
            runner = fake_runner()
            expected = STATE.render_governed_body(root, VERSION, SHA, runner)
            body = root / "body.md"
            body.write_text(expected, encoding="utf-8")
            STATE.validate(
                root,
                "finalization",
                VERSION,
                repository="owner/repo",
                rendered_body=body,
                workflow_run_id="42",
                hosted=True,
                runner=fake_runner(
                    release=hosted_release(expected),
                    workflow=hosted_workflow(),
                ),
            )

    def test_gwt_029_given_the_executing_actions_run_when_finalization_runs_then_in_progress_is_accepted_only_explicitly(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            write_fixture(root, status="validated")
            runner = fake_runner()
            expected = STATE.render_governed_body(root, VERSION, SHA, runner)
            body = root / "body.md"
            body.write_text(expected, encoding="utf-8")
            workflow = hosted_workflow()
            workflow["status"] = "in_progress"
            workflow["conclusion"] = None
            with patch.dict(
                STATE.os.environ,
                {"GITHUB_ACTIONS": "true", "GITHUB_RUN_ID": "42"},
                clear=False,
            ):
                STATE.validate(
                    root,
                    "finalization",
                    VERSION,
                    repository="owner/repo",
                    rendered_body=body,
                    workflow_run_id="42",
                    hosted=True,
                    allow_current_workflow_run=True,
                    runner=fake_runner(
                        release=hosted_release(expected),
                        workflow=workflow,
                    ),
                )

    def test_gwt_030_given_a_nonexecuting_run_when_current_run_override_is_requested_then_it_fails_closed(self):
        with patch.dict(
            STATE.os.environ,
            {"GITHUB_ACTIONS": "true", "GITHUB_RUN_ID": "99"},
            clear=False,
        ):
            with self.assertRaisesRegex(STATE.ReleaseStateError, "executing GITHUB_RUN_ID"):
                STATE.require_current_workflow_context(
                    "finalization",
                    True,
                    "42",
                    True,
                )

    def test_gwt_031_given_v014_retained_origins_when_route_evidence_matches_then_all_routes_pass(self):
        version = "v0.14.0"
        origins = ("v0.13.0", "v0.9.0", "v0.6.0")
        artifacts = {
            "release_notes": "release-notes.md",
            "migration_guide": "migration-guide.md",
            "support_matrix": "support-matrix.yaml",
            "route_evidence": [
                f"route-evidence/{origin}-to-{version}.json" for origin in origins
            ],
        }
        matrix = {
            "matrix_id": "upgrade-route-matrix-v0.14.0",
            "target": {"version": version, "release_id": "REL-v0.14.0"},
        }

        def resolved(_matrix, *, origin, target, **_kwargs):
            return {
                "diagnostics": [],
                "matrix": {"matrix_id": matrix["matrix_id"]},
                "origin": origin,
                "read_only": True,
                "route_kind": "direct",
                "selected_route": {"route_id": f"{origin}-to-{target}-direct"},
                "target": target,
            }

        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            evidence_root = root / ".dev" / "releases" / version / "route-evidence"
            evidence_root.mkdir(parents=True)
            for origin in origins:
                result = resolved(matrix, origin=origin, target=version)
                (evidence_root / f"{origin}-to-{version}.json").write_bytes(
                    STATE.canonical_route_json(result).encode("utf-8"),
                )
            with patch.object(STATE, "load_route_matrix", return_value=(matrix, b"matrix")):
                with patch.object(STATE, "resolve_upgrade_route", side_effect=resolved):
                    STATE.validate_retained_origin_route_evidence(root, version, artifacts, ["v0.13.0"])

    def test_gwt_031b_given_v016_retained_routes_when_multihop_or_wrong_predecessor_then_rejected(self):
        version = "v0.16.0"
        origins = ("v0.15.1", "v0.9.0", "v0.6.0")
        artifacts = {"release_notes": "release-notes.md", "migration_guide": "migration-guide.md",
                     "support_matrix": "support-matrix.yaml", "route_evidence": [
                         f"route-evidence/{origin}-to-{version}.json" for origin in origins]}
        matrix = {"matrix_id": "upgrade-route-matrix-v0.16.0", "target": {"version": version, "release_id": "REL-v0.16.0"}}
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            previous = root / ".dev/releases/v0.15.1/release.yaml"
            previous.parent.mkdir(parents=True)
            previous.write_text(yaml.safe_dump({"version": "v0.15.1", "distribution_kind": "governed-package"}), encoding="utf-8")
            evidence = root / ".dev/releases/v0.16.0/route-evidence"
            evidence.mkdir(parents=True)
            for origin in origins:
                (evidence / f"{origin}-to-{version}.json").write_bytes(STATE.canonical_route_json({"route_kind": "direct"}).encode("utf-8"))
            sources = ["v0.6.0", "v0.9.0", "v0.15.1"]
            with patch.object(STATE, "load_route_matrix", return_value=(matrix, b"matrix")), patch.object(STATE, "resolve_upgrade_route", return_value={"route_kind": "direct"}), patch.object(STATE, "validate_direct_upgrade_execution") as actual_gate:
                STATE.validate_retained_origin_route_evidence(root, version, artifacts, sources)
                actual_gate.assert_called_once_with(root, version, sources, matrix)
                with self.assertRaisesRegex(STATE.ReleaseStateError, "automatic sources"):
                    STATE.validate_retained_origin_route_evidence(root, version, artifacts, ["v0.6.0", "v0.9.0", "v0.15.0"])
            with patch.object(STATE, "load_route_matrix", return_value=(matrix, b"matrix")), patch.object(STATE, "resolve_upgrade_route", return_value={"route_kind": "orchestrated-multi-hop"}):
                with self.assertRaisesRegex(STATE.ReleaseStateError, "one direct edge"):
                    STATE.validate_retained_origin_route_evidence(root, version, artifacts, sources)

    def test_gwt_031c_given_direct_execution_claims_when_identity_or_completion_disagrees_then_rejected(self):
        sources = ["v0.6.0", "v0.9.0", "v0.15.1"]
        version = "v0.16.0"
        digest = "b" * 64
        matrix = {"target": {"commit": SHA}, "routes": [{"edges": [{"to_version": version,
            "artifacts": {"archive": {"sha256": digest}}}]}]}
        negatives = ["missing-origin-manifest", "tampered-origin-manifest", "origin-version-disagreement",
            "tampered-incoming-validator", "fault-injected-incoming-validator-disagreement", "ambiguous-provenance-authority",
            "unresolved-customization", "missing-owner-decision", "tampered-owner-decision", "missing-target-validation",
            "failed-target-validation-receipt", "target-validator-disagreement", "tampered-target-validation-receipt", "candidate-authority-disagreement"]
        matrix["retained_origins"] = [{"version": origin, "commit": SHA, "manifest": {"sha256": digest}} for origin in sources]
        with tempfile.TemporaryDirectory() as temp, patch.object(STATE, "validate_direct_case_artifacts"):
            root = Path(temp)
            runner = root / ".github/scripts/validate-v016-direct-upgrades.py"
            runner.parent.mkdir(parents=True)
            runner.write_bytes(b"# source-gate unit fixture only\n")
            runner.with_name("alternate.py").write_bytes(runner.read_bytes())
            path = root / ".dev/releases/v0.16.0/route-assets/actual/terminal.json"
            path.parent.mkdir(parents=True)
            evidence = {"schema_version": "direct-upgrade-execution/v1", "evidence_kind": "actual-isolated-target-execution",
                "outcome": "passed", "archive_sha256": digest, "package_source": {"commit": SHA},
                "runner": {"path": runner.relative_to(root).as_posix(), "sha256": STATE.hashlib.sha256(runner.read_bytes()).hexdigest()}, "cases": []}
            evidence.update(subject_sha=SHA, started_at="2026-09-05T10:00:00+00:00", completed_at="2026-09-05T10:00:01+00:00", duration_seconds=1.0, invocation=["python", ".github/scripts/validate-v016-direct-upgrades.py", "--subject-sha", SHA])
            for origin in sources:
                for suffix in ("-pristine-resume", "-customized-none", "-customized-rollback"):
                    evidence["cases"].append({"origin": origin, "case": origin + suffix, "outcome": "passed",
                        "recovery": "rolled-back" if suffix.endswith("rollback") else "resume" if suffix.endswith("resume") else "none",
                        "prestate_sha256": digest, "poststate_sha256": digest,
                        "finalization": {"status": "finalized", "effective_rule_readiness": {"action_ready": True}},
                        "target_validation": {"outcome": "passed", "exit_code": 0},
                        "semantic_cutovers": {"provider_component_selection": "preserved", "source_specific_managed_removals": "verified",
                            "commit_grammar_adoption": "verified", "effective_rule_regeneration": "verified", "skill_retirement": "verified",
                            "target_customization_ids": ["fixture-contract"]},
                        "negative_evidence": [{"case": name, "outcome": "passed"} for name in negatives]})
            with self.assertRaisesRegex(STATE.ReleaseStateError, "missing or invalid"):
                STATE.validate_direct_upgrade_execution(root, version, sources, matrix)
            path.write_text(json.dumps(evidence), encoding="utf-8")
            STATE.validate_direct_upgrade_execution(root, version, sources, matrix)
            changes = [
                ("synthetic", lambda item: item.update(evidence_kind="synthetic-test")),
                ("failed", lambda item: item.update(outcome="failed")),
                ("archive", lambda item: item.update(archive_sha256="c" * 64)),
                ("source", lambda item: item["package_source"].update(commit="c" * 40)),
                ("runner", lambda item: item["runner"].update(sha256="c" * 64)),
                ("alternate runner", lambda item: item["runner"].update(path=".github/scripts/alternate.py")),
                ("missing rollback hashes", lambda item: (item["cases"][2].pop("prestate_sha256"), item["cases"][2].pop("poststate_sha256"))),
                ("wrong resume", lambda item: item["cases"][0].update(recovery="never-resumed")),
                ("missing invocation", lambda item: item.pop("invocation")),
                ("missing time", lambda item: item.pop("started_at")),
                ("missing case", lambda item: item["cases"].pop()),
                ("rollback", lambda item: item["cases"][2].update(poststate_sha256="c" * 64)),
                ("target failed", lambda item: item["cases"][0]["target_validation"].update(exit_code=17)),
                ("not ready", lambda item: item["cases"][0]["finalization"]["effective_rule_readiness"].update(action_ready=False)),
                ("no customization", lambda item: item["cases"][1]["semantic_cutovers"].update(target_customization_ids=[])),
                ("missing negative", lambda item: item["cases"][0].update(negative_evidence=[])),
            ]
            for label, change in changes:
                with self.subTest(label=label):
                    altered = json.loads(json.dumps(evidence))
                    change(altered)
                    path.write_text(json.dumps(altered), encoding="utf-8")
                    with self.assertRaises(STATE.ReleaseStateError):
                        STATE.validate_direct_upgrade_execution(root, version, sources, matrix)

    def test_gwt_031d_given_retained_case_files_when_receipt_output_or_recovery_is_missing_then_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            actual = Path(temp)
            label = 'v0.6.0-customized-none'
            transaction = 'b' * 64
            case = {'origin': 'v0.6.0', 'case': label, 'transaction_id': transaction, 'recovery': 'none', 'artifacts': {}}
            origin_identity = {'commit': SHA, 'manifest': {'sha256': 'c' * 64}}
            target_identity = {'commit': 'd' * 40, 'manifest': {'sha256': 'e' * 64}}
            def verify(value):
                STATE.validate_direct_case_artifacts(actual, value, origin_identity, target_identity)
            def raw(value):
                return (json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False) + '\n').encode()
            def bind(name, value, *, binary=False):
                data = value if binary else raw(value)
                path = actual / 'evidence' / label / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(data)
                case['artifacts'][name] = {'path': path.relative_to(actual).as_posix(), 'sha256': STATE.hashlib.sha256(data).hexdigest()}
                return case['artifacts'][name]['sha256']
            def digest(value):
                return STATE.hashlib.sha256(raw(value).rstrip(b'\n')).hexdigest()
            case['prestate_sha256'] = bind('prestate.json', {'old': 'bytes'})
            case['poststate_sha256'] = bind('poststate.json', {'new': 'bytes'})
            before_authority = {'source': {'version': 'v0.6.0', 'commit': SHA}}
            before_authority_digest = bind('provenance-before.yaml', before_authority)
            bind('provenance-after.yaml', {'source': {'commit': 'd' * 40}, 'previous_source': {'commit': SHA}})
            bind('customizations-before.yaml', {'customizations': [{'id': 'fixture-contract'}]})
            bind('customizations-after.yaml', {'customizations': [{'id': 'fixture-contract'}]})
            profile = {'argv': ['python', '.dev/validation/direct-upgrade-target.py']}
            packet = {'transaction_id': transaction, 'plan_sha256': transaction, 'target_validation_profile': profile, 'target_validation_profile_digest': digest(profile)}
            packet.update(schema_version='upgrade-remediation-packet/v1', provenance={'source': {'version': 'v0.6.0', 'commit': SHA}}, migration={'selected_input': {'previous_version': '0.6.0', 'previous_files_sha256': 'c' * 64}}, package={'source': {'commit': 'd' * 40}, 'manifest_sha256': 'e' * 64})
            packet['provenance']['sha256'] = before_authority_digest
            packet['canonical_digest'] = digest(packet)
            bind('packet.json', packet)
            decision = {'transaction_id': transaction, 'status': 'approved', 'packet_sha256': packet['canonical_digest']}
            decision_digest = bind('decision.json', decision)
            output_digest = bind('target-validation.log', b'actual test fixture output\n', binary=True)
            execution = {'argv': profile['argv'], 'outcome': 'passed', 'exit_code': 0, 'started_at': '2026-09-05T10:00:00+00:00', 'completed_at': '2026-09-05T10:00:01+00:00', 'output_sha256': output_digest, 'evidence': f'.git/ai-context-package-apply/{transaction}/target-validation-output.txt'}
            case['target_validation'] = execution
            case['finalization'] = {'status': 'finalized'}
            bind('finalization.json', case['finalization'])
            receipt = {'schema_version': 'target-validation-receipt/v1', 'transaction_id': transaction, 'plan_sha256': transaction, 'packet_sha256': packet['canonical_digest'], 'decision_sha256': decision_digest, 'target_validation_profile': profile, 'target_validation_profile_digest': digest(profile), 'execution': execution}
            bind('supplied-target-validation.json', receipt)
            verify(case)
            path = actual / 'evidence' / label / 'target-validation.log'
            original = path.read_bytes()
            path.unlink()
            with self.assertRaisesRegex(STATE.ReleaseStateError, 'unavailable'):
                verify(case)
            path.write_bytes(original + b'tampered')
            with self.assertRaisesRegex(STATE.ReleaseStateError, 'digest'):
                verify(case)
            path.write_bytes(original)
            for key in ('argv', 'output_sha256', 'started_at', 'completed_at', 'evidence'):
                with self.subTest(missing=key):
                    incomplete = json.loads(json.dumps(case))
                    incomplete['target_validation'].pop(key)
                    with self.assertRaises(STATE.ReleaseStateError):
                        verify(incomplete)
            resumed = json.loads(json.dumps(case))
            resumed['recovery'] = 'resume'
            with self.assertRaisesRegex(STATE.ReleaseStateError, 'artifact binding'):
                verify(resumed)

    def test_gwt_031a_given_repository_v014_route_evidence_when_validated_then_published_routes_pass(self):
        version = "v0.14.0"
        release = yaml.safe_load(
            (ROOT / ".dev" / "releases" / version / "release.yaml").read_text(
                encoding="utf-8",
            )
        )

        STATE.validate_retained_origin_route_evidence(
            ROOT, version, release["artifacts"], ["v0.13.0"]
        )
        # Retained historical evidence remains readable. The historical broader
        # declaration is not silently admitted as a new source candidate.
        with self.assertRaisesRegex(STATE.ReleaseStateError, "exactly"):
            STATE.validate_retained_origin_route_evidence(
                ROOT, version, release["artifacts"], release["compatibility"]["automatic_upgrade_sources"]
            )

    def test_gwt_032_given_v014_tampered_or_unproven_route_when_validated_then_it_fails_closed(self):
        version = "v0.14.0"
        origins = ("v0.13.0", "v0.9.0", "v0.6.0")
        artifacts = {
            "release_notes": "release-notes.md",
            "migration_guide": "migration-guide.md",
            "support_matrix": "support-matrix.yaml",
            "route_evidence": [
                f"route-evidence/{origin}-to-{version}.json" for origin in origins
            ],
        }
        matrix = {
            "matrix_id": "upgrade-route-matrix-v0.14.0",
            "target": {"version": version, "release_id": "REL-v0.14.0"},
        }

        def resolved(_matrix, *, origin, target, **_kwargs):
            return {
                "diagnostics": [],
                "matrix": {"matrix_id": matrix["matrix_id"]},
                "origin": origin,
                "read_only": True,
                "route_kind": "direct",
                "selected_route": {"route_id": f"{origin}-to-{target}-direct"},
                "target": target,
            }

        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            evidence_root = root / ".dev" / "releases" / version / "route-evidence"
            evidence_root.mkdir(parents=True)
            for origin in origins:
                result = resolved(matrix, origin=origin, target=version)
                (evidence_root / f"{origin}-to-{version}.json").write_bytes(
                    STATE.canonical_route_json(result).encode("utf-8"),
                )
            (evidence_root / f"v0.9.0-to-{version}.json").write_text(
                '{"tampered":true}\n',
                encoding="utf-8",
            )
            with patch.object(STATE, "load_route_matrix", return_value=(matrix, b"matrix")):
                with patch.object(STATE, "resolve_upgrade_route", side_effect=resolved):
                    with self.assertRaisesRegex(
                        STATE.ReleaseStateError,
                        "differs from canonical resolver output",
                    ):
                        STATE.validate_retained_origin_route_evidence(root, version, artifacts, ["v0.13.0"])

            def unresolved(_matrix, *, origin, target, **_kwargs):
                result = resolved(_matrix, origin=origin, target=target)
                result["route_kind"] = "reconciliation-required"
                return result

            with patch.object(STATE, "load_route_matrix", return_value=(matrix, b"matrix")):
                with patch.object(STATE, "resolve_upgrade_route", side_effect=unresolved):
                    with self.assertRaisesRegex(
                        STATE.ReleaseStateError,
                        "must resolve direct or orchestrated-multi-hop",
                    ):
                        STATE.validate_retained_origin_route_evidence(root, version, artifacts, ["v0.13.0"])

    def test_gwt_033_given_open_terminal_issue_bound_to_current_pr_when_candidate_checked_then_only_exact_head_passes(self):
        issue_number = 206
        repository = "owner/repo"
        body = "## Disposition\n\nCloses #206"
        declaration = {
            "schema_version": "1.0",
            "contract_id": "github-terminal-issue-closure",
            "repository": repository,
            "validation_stage": "declaration",
            "pull_request": {
                "number": 231,
                "head_sha": None,
                "body": body,
                "integration": {
                    "status": "pending",
                    "topology": None,
                    "admitted_head_sha": None,
                    "integration_commit_sha": None,
                    "provider_read_back": False,
                },
                "review": {"status": "pending"},
                "required_check_contexts": [],
                "hosted_checks": [],
            },
            "issues": [
                {
                    "number": issue_number,
                    "mode": "terminal-close",
                    "work_authorization": {
                        "online_issue_bound": True,
                        "explicit_owner_approval": True,
                    },
                    "final_accepted_delivery": True,
                    "workflow": {
                        "scope_complete": True,
                        "tasks_complete": True,
                        "applicable_verification_complete": True,
                    },
                    "closing_keyword": "Closes",
                    "closure_deferred_reason": None,
                    "next_terminal_gate_or_owner": None,
                    "read_back": {
                        "performed": False,
                        "integration_commit_sha": None,
                        "issue_state": None,
                        "issue_state_reason": None,
                        "project_status": None,
                    },
                }
            ],
        }

        def runner_for(head_sha):
            def execute(args, cwd, capture_output, text, check):
                if args == ["git", "rev-parse", "HEAD"]:
                    output = SHA + "\n"
                elif args == ["gh", "api", "--method", "GET", "repos/owner/repo/pulls/231"]:
                    output = json.dumps(
                        {
                            "number": 231,
                            "state": "open",
                            "merged_at": None,
                            "body": body,
                            "head": {"sha": head_sha},
                            "base": {"repo": {"full_name": repository}},
                        }
                    )
                else:
                    raise AssertionError(args)
                return subprocess.CompletedProcess(args, 0, output, "")

            return execute

        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            declaration_path = (
                root
                / ".dev/workflows/s3/evidence/terminal-issue-closure-s3-pr-231.yaml"
            )
            declaration_path.parent.mkdir(parents=True)
            declaration_path.write_text(
                yaml.safe_dump(declaration, sort_keys=False),
                encoding="utf-8",
            )
            deferred = json.loads(json.dumps(declaration))
            deferred["pull_request"]["number"] = 227
            deferred["pull_request"]["body"] = (
                "## Disposition\n\n"
                "Refs #206\n\n"
                "Closure deferred reason for #206: later release proof remains.\n\n"
                "Next terminal gate for #206: complete the later release proof."
            )
            deferred_issue = deferred["issues"][0]
            deferred_issue.update(
                {
                    "mode": "deferred",
                    "final_accepted_delivery": False,
                    "workflow": {
                        "scope_complete": False,
                        "tasks_complete": False,
                        "applicable_verification_complete": False,
                    },
                    "closing_keyword": None,
                    "closure_deferred_reason": "later release proof remains",
                    "next_terminal_gate_or_owner": "complete the later release proof",
                }
            )
            historical_path = (
                declaration_path.parent / "terminal-issue-closure-declaration.yaml"
            )
            historical_path.write_text(
                yaml.safe_dump(deferred, sort_keys=False),
                encoding="utf-8",
            )
            self.assertTrue(
                STATE.pending_terminal_issue_delivery(
                    root,
                    repository,
                    issue_number,
                    runner_for(SHA),
                )
            )
            self.assertFalse(
                STATE.pending_terminal_issue_delivery(
                    root,
                    repository,
                    issue_number,
                    runner_for("b" * 40),
                )
            )
            duplicate_path = (
                declaration_path.parent / "terminal-issue-closure-duplicate.yaml"
            )
            duplicate_path.write_text(
                yaml.safe_dump(declaration, sort_keys=False),
                encoding="utf-8",
            )
            self.assertFalse(
                STATE.pending_terminal_issue_delivery(
                    root,
                    repository,
                    issue_number,
                    runner_for(SHA),
                )
            )
            duplicate_path.unlink()
            malformed_path = (
                declaration_path.parent / "terminal-issue-closure-malformed.yaml"
            )
            malformed_path.write_text("unrelated: true\n", encoding="utf-8")
            wrong_contract = json.loads(json.dumps(declaration))
            wrong_contract["contract_id"] = "unrelated-contract"
            wrong_contract_path = (
                declaration_path.parent / "terminal-issue-closure-wrong-contract.yaml"
            )
            wrong_contract_path.write_text(
                yaml.safe_dump(wrong_contract, sort_keys=False),
                encoding="utf-8",
            )
            self.assertTrue(
                STATE.pending_terminal_issue_delivery(
                    root,
                    repository,
                    issue_number,
                    runner_for(SHA),
                )
            )
            declaration_path.unlink()
            self.assertFalse(
                STATE.pending_terminal_issue_delivery(
                    root,
                    repository,
                    issue_number,
                    runner_for(SHA),
                )
            )


if __name__ == "__main__":
    tempfile.run_unittest_main()
