#!/usr/bin/env python3
"""GWT tests for immutable source-history validation receipts."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[3]
HELPER = ROOT / ".ai/scripts/validate-immutable-history.py"
REUSABLE_IDS = [
    "workflow-artifacts",
    "assessment-artifacts",
    "source-ai-context-version",
]
ROUTINE_ALLOWLIST = [
    ".ai/distribution/validation/immutable-history-receipt.yaml",
    ".ai/assets/**",
    ".ai/scripts/README.md",
    ".ai/scripts/tests/**",
    ".dev/guides/**",
    "docs/**",
    "src/**",
    "tests/**",
    "tools/**",
    "README.md",
    "README.en.md",
    "AGENTS.md",
    "AGENTS.zh-TW.md",
    "CLAUDE.md",
]


class ImmutableHistoryValidationGwtTests(unittest.TestCase):
    def setUp(self) -> None:
        self.initialize_repository(failing_validator=False)

    def initialize_repository(self, *, failing_validator: bool) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="immutable-history-")
        self.repo = Path(self.temporary.name) / "repo"
        self.repo.mkdir()
        self.git("init", "-q")
        self.git("config", "user.email", "fixture@example.test")
        self.git("config", "user.name", "Fixture")
        self.branch = self.git("branch", "--show-current").stdout.strip()
        self.contract_path = self.repo / ".ai/distribution/validation/immutable-history-validation.yaml"
        self.receipt_path = self.repo / ".ai/distribution/validation/immutable-history-receipt.yaml"
        self.create_fixture(failing_validator=failing_validator)
        self.commit_all("source baseline")
        published_commit = self.git("rev-parse", "HEAD").stdout.strip()
        self.git("tag", "-a", "v0.0.1", published_commit, "-m", "fixture release tag")
        self.write(
            ".dev/releases/v0.0.1/release.yaml",
            'tag: "v0.0.1"\ncommit: "%s"\n' % published_commit,
        )
        self.commit_all("bind fixture release declaration")
        self.source_revision = self.git("rev-parse", "HEAD").stdout.strip()

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def git(self, *arguments: str) -> subprocess.CompletedProcess[str]:
        result = subprocess.run(
            ["git", *arguments],
            cwd=self.repo,
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        return result

    def write(self, relative: str, content: str) -> Path:
        path = self.repo / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8", newline="\n")
        return path

    def create_fixture(self, *, failing_validator: bool) -> None:
        self.write(".dev/workflows/INDEX.MD", "# workflows\n")
        self.write(".dev/workflows/2026-01-01-fixture/workflow.yaml", "workflow: fixture\n")
        self.write(".dev/assessments/INDEX.MD", "# assessments\n")
        self.write(".dev/assessments/ASM-20260101-001/assessment.yaml", "assessment: fixture\n")
        self.write(".dev/releases/INDEX.MD", "# releases\n")
        self.write(".dev/releases/v0.0.1/release.yaml", 'tag: "v0.0.1"\ncommit: "0000000000000000000000000000000000000000"\n')
        self.write(".dev/releases/v0.0.2/release.yaml", "status: planned\ntag: null\ncommit: null\n")
        self.write(".ai/scripts/fixture-validator.py", "raise SystemExit(%d)\n" % (7 if failing_validator else 0))
        self.write(".ai/distribution/IMMUTABLE-HISTORY-VALIDATION-CONTRACT.md", "fixture contract\n")
        payload = {
            "schema_version": "1.0",
            "contract_id": "immutable-history-validation",
            "source": {
                "history_roots": [".dev/workflows", ".dev/assessments", ".dev/releases"],
                "history_indexes": [
                    ".dev/workflows/INDEX.MD",
                    ".dev/assessments/INDEX.MD",
                    ".dev/releases/INDEX.MD",
                ],
                "protected_paths": [
                    ".dev/backlog/**",
                    ".dev/ai-context/**",
                    ".dev/AI-CONTEXT-SOURCE.yaml",
                ],
                "fingerprint_paths": {
                    "validators": [".ai/scripts/fixture-validator.py"],
                    "schema": [
                        ".ai/distribution/validation/immutable-history-validation.yaml",
                        ".ai/distribution/IMMUTABLE-HISTORY-VALIDATION-CONTRACT.md",
                    ],
                },
                "receipt": {
                    "path": ".ai/distribution/validation/immutable-history-receipt.yaml",
                    "schema_version": "1.0",
                    "allowed_diff_paths": ROUTINE_ALLOWLIST,
                },
                "profiles": {
                    "routine": ["fast", "pr"],
                    "full": ["release", "nightly-full"],
                    "full_gates": [
                        "release-candidate",
                        "scheduled-governance",
                        "validator-schema-change",
                        "immutable-history-change",
                    ],
                },
                "native_full_validators": [
                    {"check_id": check_id, "command": ["python", ".ai/scripts/fixture-validator.py"]}
                    for check_id in REUSABLE_IDS
                ],
            },
            "downstream": {
                "mode": "target-local-ai-context-only",
                "source_history_receipt": "forbidden",
                "target_local_validation": [sys.executable, ".ai/scripts/validate-ai-context-target.py"],
            },
        }
        self.contract_path.parent.mkdir(parents=True, exist_ok=True)
        self.contract_path.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8", newline="\n")

    def commit_all(self, message: str) -> None:
        self.git("add", ".")
        self.git("commit", "-q", "-m", message)

    def current_commit(self) -> str:
        return self.git("rev-parse", "HEAD").stdout.strip()

    def invoke(
        self,
        command: str,
        *extra: str,
        output_format: str = "json",
        contract_path: Path | None = None,
    ) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                sys.executable,
                str(HELPER),
                command,
                "--repo",
                str(self.repo),
                "--contract",
                str(contract_path or self.contract_path),
                "--receipt",
                str(self.receipt_path),
                "--head",
                "HEAD",
                "--output-format",
                output_format,
                *extra,
            ],
            cwd=self.repo,
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )

    def parse(self, result: subprocess.CompletedProcess[str], expected_code: int) -> dict[str, object]:
        self.assertEqual(expected_code, result.returncode, result.stdout + result.stderr)
        self.assertEqual("", result.stderr)
        self.assertEqual(1, len(result.stdout.splitlines()), result.stdout)
        return json.loads(result.stdout)

    def refresh_and_commit_receipt(self) -> dict[str, object]:
        payload = self.parse(self.invoke("refresh", "--head", self.current_commit()), 0)
        self.assertEqual("full-refreshed", payload["outcome"])
        self.assertEqual(REUSABLE_IDS, payload["executed_check_ids"])
        self.assertTrue(all(command[0] == sys.executable for command in payload["executed_commands"]))
        self.assertTrue(self.receipt_path.is_file())
        self.git("add", self.receipt_path.relative_to(self.repo).as_posix())
        self.git("commit", "-q", "-m", "record immutable history receipt")
        return payload

    def assert_full_required(self, result: subprocess.CompletedProcess[str], reason: str) -> dict[str, object]:
        payload = self.parse(result, 10)
        self.assertEqual("full-required", payload["outcome"])
        self.assertEqual(reason, payload["reason"])
        self.assertEqual([], payload["reusable_check_ids"])
        return payload

    def test_gwt_001_given_receipt_only_first_parent_continuation_when_verified_then_routine_checks_are_reusable(self) -> None:
        self.refresh_and_commit_receipt()
        self.write("tools/ordinary.py", "print('ordinary code')\n")
        self.write(".dev/guides/ordinary.md", "# Ordinary documentation\n")
        self.commit_all("change allowlisted ordinary code and documentation")

        payload = self.parse(self.invoke("verify"), 0)

        self.assertEqual("routine-reusable", payload["outcome"])
        self.assertEqual("receipt-valid", payload["reason"])
        self.assertEqual(self.source_revision, payload["source_revision"])
        self.assertEqual(REUSABLE_IDS, payload["reusable_check_ids"])
        self.assertRegex(str(payload["source_tree"]), r"^[0-9a-f]{40}$")
        self.assertRegex(str(payload["receipt_commit"]), r"^[0-9a-f]{40}$")

        tsv = self.invoke("verify", output_format="tsv")
        self.assertEqual(0, tsv.returncode, tsv.stdout + tsv.stderr)
        fields = tsv.stdout.rstrip("\r\n").split("\t")
        self.assertEqual(6, len(fields))
        self.assertEqual("routine-reusable", fields[0])
        self.assertEqual("receipt-valid", fields[1])
        self.assertEqual(self.source_revision, fields[2])
        self.assertEqual(",".join(REUSABLE_IDS), fields[5])

    def test_gwt_002_given_added_modified_or_deleted_history_when_verified_then_full_validation_is_required(self) -> None:
        cases = (
            ("add", ".dev/workflows/2026-01-02-new/workflow.yaml", "workflow: new\n"),
            ("modify", ".dev/assessments/ASM-20260101-001/assessment.yaml", "assessment: changed\n"),
            ("delete", ".dev/releases/v0.0.1/release.yaml", None),
        )
        for operation, relative, content in cases:
            with self.subTest(operation=operation):
                self.tearDown()
                self.setUp()
                self.refresh_and_commit_receipt()
                path = self.repo / relative
                if content is None:
                    path.unlink()
                else:
                    self.write(relative, content)
                self.commit_all(f"{operation} immutable history")
                self.assert_full_required(self.invoke("verify"), "immutable-history-change")

    def test_gwt_003_given_unindexed_history_addition_when_verified_then_full_validation_is_required(self) -> None:
        self.refresh_and_commit_receipt()
        self.write(".dev/workflows/unindexed-evidence/receipt.yaml", "unindexed: true\n")
        self.commit_all("add unindexed immutable history")

        self.assert_full_required(self.invoke("verify"), "immutable-history-change")

    def test_gwt_004_given_stale_receipt_digest_when_verified_then_full_validation_is_required(self) -> None:
        self.parse(self.invoke("refresh"), 0)
        receipt = yaml.safe_load(self.receipt_path.read_text(encoding="utf-8"))
        receipt["source"]["history_digest"] = "0" * 64
        self.receipt_path.write_text(yaml.safe_dump(receipt, sort_keys=False), encoding="utf-8", newline="\n")
        self.git("add", self.receipt_path.relative_to(self.repo).as_posix())
        self.git("commit", "-q", "-m", "record receipt with stale digest")

        self.assert_full_required(self.invoke("verify"), "receipt-history-digest-mismatch")

    def test_gwt_005_given_validator_or_schema_change_when_verified_then_full_validation_is_required(self) -> None:
        for relative, reason in (
            (".ai/scripts/fixture-validator.py", "validator-change"),
            (".ai/distribution/IMMUTABLE-HISTORY-VALIDATION-CONTRACT.md", "schema-change"),
        ):
            with self.subTest(path=relative):
                self.tearDown()
                self.setUp()
                self.refresh_and_commit_receipt()
                self.write(relative, "changed\n" if relative.endswith(".md") else "raise SystemExit(0)\n# changed\n")
                self.commit_all("change fingerprint")
                self.assert_full_required(self.invoke("verify"), reason)

    def test_gwt_006_given_receipt_source_not_on_head_first_parent_when_verified_then_full_validation_is_required(self) -> None:
        self.git("checkout", "-q", "-b", "side")
        self.write("side-only.txt", "side\n")
        self.commit_all("side source")
        self.parse(self.invoke("refresh"), 0)
        saved_receipt = self.receipt_path.read_text(encoding="utf-8")
        self.receipt_path.unlink()
        self.git("checkout", "-q", self.branch)
        self.receipt_path.parent.mkdir(parents=True, exist_ok=True)
        self.receipt_path.write_text(saved_receipt, encoding="utf-8", newline="\n")
        self.git("add", self.receipt_path.relative_to(self.repo).as_posix())
        self.git("commit", "-q", "-m", "record side receipt")
        self.git("merge", "--no-ff", "side", "-m", "merge side")

        self.assert_full_required(self.invoke("verify"), "receipt-source-not-first-parent")

    def test_gwt_007_given_unknown_continuation_path_when_verified_then_closed_allowlist_requires_full_validation(self) -> None:
        self.refresh_and_commit_receipt()
        self.write("unknown-routine-input.txt", "unlisted continuation\n")
        self.commit_all("change unknown path")

        self.assert_full_required(self.invoke("verify"), "closed-allowlist-mismatch")

    def test_gwt_008_given_clean_committed_source_when_refreshed_then_all_native_full_validators_execute_before_receipt_write(self) -> None:
        payload = self.parse(self.invoke("refresh"), 0)

        self.assertEqual("full-refreshed", payload["outcome"])
        self.assertEqual("native-full-validation-passed", payload["reason"])
        self.assertEqual(REUSABLE_IDS, payload["executed_check_ids"])
        self.assertTrue(all(command[0] == sys.executable for command in payload["executed_commands"]))
        self.assertEqual(".ai/distribution/validation/immutable-history-receipt.yaml", payload["receipt_path"])
        self.assertTrue(self.receipt_path.is_file())

    def test_gwt_009_given_allowlisted_path_deletion_when_verified_then_full_validation_is_required(self) -> None:
        self.refresh_and_commit_receipt()
        guide = self.write(".dev/guides/ordinary.md", "# ordinary\n")
        self.commit_all("add ordinary guide")
        self.parse(self.invoke("verify"), 0)
        guide.unlink()
        self.commit_all("delete ordinary guide")

        self.assert_full_required(self.invoke("verify"), "deleted-continuation-path")

    def test_gwt_010_given_declared_release_tag_is_moved_when_verified_then_full_validation_is_required(self) -> None:
        self.refresh_and_commit_receipt()
        self.git("tag", "-f", "v0.0.1", "HEAD")

        self.assert_full_required(self.invoke("verify"), "release-reference-drift")

    def test_gwt_011_given_head_does_not_equal_checked_out_head_when_verified_then_invocation_is_rejected(self) -> None:
        self.refresh_and_commit_receipt()
        result = subprocess.run(
            [
                sys.executable,
                str(HELPER),
                "verify",
                "--repo",
                str(self.repo),
                "--contract",
                str(self.contract_path),
                "--receipt",
                str(self.receipt_path),
                "--head",
                self.source_revision,
            ],
            cwd=self.repo,
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        payload = self.parse(result, 2)
        self.assertEqual("error", payload["outcome"])
        self.assertEqual("--head must resolve to the checked-out HEAD", payload["reason"])

    def test_gwt_012_given_noncanonical_contract_path_when_verified_then_invocation_is_rejected(self) -> None:
        alternate = self.repo / "alternate-contract.yaml"
        alternate.write_text(self.contract_path.read_text(encoding="utf-8"), encoding="utf-8", newline="\n")

        payload = self.parse(self.invoke("verify", contract_path=alternate), 2)

        self.assertEqual("error", payload["outcome"])
        self.assertEqual("--contract must resolve to the canonical immutable-history validation contract", payload["reason"])

    def test_gwt_013_given_failed_native_validator_when_refreshed_then_no_receipt_is_written(self) -> None:
        self.tearDown()
        self.initialize_repository(failing_validator=True)

        payload = self.parse(self.invoke("refresh"), 2)

        self.assertEqual("error", payload["outcome"])
        self.assertIn("native validator workflow-artifacts failed", str(payload["reason"]))
        self.assertFalse(self.receipt_path.exists())

    def test_gwt_014_given_downstream_mode_when_checked_then_source_receipt_is_explicitly_forbidden(self) -> None:
        payload = self.parse(self.invoke("verify", "--mode", "downstream"), 0)
        self.assertEqual("downstream-target-local", payload["outcome"])
        self.assertEqual("source-history-receipt-forbidden", payload["reason"])
        self.assertEqual([], payload["reusable_check_ids"])
        self.assertEqual([sys.executable, ".ai/scripts/validate-ai-context-target.py"], payload["target_local_validation"])

        refresh = self.parse(self.invoke("refresh", "--mode", "downstream"), 2)
        self.assertEqual("error", refresh["outcome"])
        self.assertIn("forbids source-history receipt refresh", str(refresh["reason"]))

    def test_gwt_016_given_misnamed_release_record_when_refreshed_then_no_invalid_receipt_is_written(self) -> None:
        self.refresh_and_commit_receipt()
        receipt_before = self.receipt_path.read_bytes()
        release = (self.repo / ".dev/releases/v0.0.1/release.yaml").read_text(
            encoding="utf-8"
        )
        self.write(".dev/releases/legacy/release.yaml", release)
        self.commit_all("add misnamed release record")

        payload = self.parse(self.invoke("refresh"), 2)

        self.assertEqual("error", payload["outcome"])
        self.assertEqual("release-reference-malformed", payload["reason"])
        self.assertEqual(receipt_before, self.receipt_path.read_bytes())

    def test_gwt_017_given_receipt_omits_published_release_when_verified_then_full_validation_is_required(self) -> None:
        self.parse(self.invoke("refresh"), 0)
        receipt = yaml.safe_load(self.receipt_path.read_text(encoding="utf-8"))
        receipt["source"]["release_refs"] = []
        digest_payload = {
            "digest_schema_version": "1.0",
            "kind": "release-tag-refs",
            "objects": [],
        }
        receipt["source"]["release_ref_digest"] = hashlib.sha256(
            (
                json.dumps(
                    digest_payload,
                    ensure_ascii=False,
                    separators=(",", ":"),
                    sort_keys=True,
                )
                + "\n"
            ).encode("utf-8")
        ).hexdigest()
        self.receipt_path.write_text(
            yaml.safe_dump(receipt, sort_keys=False),
            encoding="utf-8",
            newline="\n",
        )
        self.git("add", self.receipt_path.relative_to(self.repo).as_posix())
        self.git("commit", "-q", "-m", "record incomplete receipt")

        self.assert_full_required(
            self.invoke("verify"), "receipt-release-ref-set-mismatch"
        )

    def test_gwt_018_given_side_branch_delete_and_recreate_when_merged_then_full_validation_is_required(self) -> None:
        self.refresh_and_commit_receipt()
        main_branch = self.branch
        self.write("docs/guide.md", "baseline\n")
        self.commit_all("add allowlisted guide")
        self.git("switch", "-q", "-c", "fixture-side")
        (self.repo / "docs/guide.md").unlink()
        self.commit_all("delete allowlisted guide")
        self.write("docs/guide.md", "replacement\n")
        self.commit_all("recreate allowlisted guide")
        self.git("switch", "-q", main_branch)
        self.git("merge", "--no-ff", "-q", "fixture-side", "-m", "merge fixture side branch")

        self.assert_full_required(
            self.invoke("verify"), "merge-continuation-requires-full"
        )

    def test_gwt_019_given_canonical_contract_is_symlink_when_resolved_target_is_supplied_then_invocation_is_rejected(self) -> None:
        target = self.repo / "real-contract.yaml"
        target.write_text(
            self.contract_path.read_text(encoding="utf-8"),
            encoding="utf-8",
            newline="\n",
        )
        self.contract_path.unlink()
        try:
            self.contract_path.symlink_to(target)
        except OSError as exc:
            self.skipTest(f"symlink creation is unavailable: {exc}")

        payload = self.parse(
            self.invoke("verify", contract_path=target),
            2,
        )

        self.assertEqual("error", payload["outcome"])
        self.assertEqual(
            "--contract and canonical contract must not be symlinks",
            payload["reason"],
        )


class SourceImmutableHistoryContractTests(unittest.TestCase):
    def test_gwt_015_given_source_contract_when_loaded_then_runtime_validator_inputs_are_protected_without_a_broad_ai_allowance(self) -> None:
        contract = yaml.safe_load(
            (ROOT / ".ai/distribution/validation/immutable-history-validation.yaml").read_text(encoding="utf-8")
        )
        source = contract["source"]
        validators = source["fingerprint_paths"]["validators"]
        self.assertTrue(
            {
                ".ai/scripts/validate-immutable-history.py",
                ".ai/scripts/validate-workflow-artifacts.py",
                ".ai/scripts/validate-assessment-artifacts.py",
                ".ai/scripts/validate-ai-context-versions.py",
                ".ai/scripts/python_prerequisites.py",
                ".ai/scripts/ai_context_target_provenance.py",
                ".ai/scripts/ai_context_effective_rules.py",
                ".ai/scripts/python-entrypoints.json",
                "requirements.txt",
            }.issubset(validators)
        )
        allowlist = source["receipt"]["allowed_diff_paths"]
        self.assertEqual(ROUTINE_ALLOWLIST, allowlist)
        self.assertNotIn(".ai/**", allowlist)
        self.assertEqual(
            [".dev/backlog/**", ".dev/ai-context/**", ".dev/AI-CONTEXT-SOURCE.yaml"],
            source["protected_paths"],
        )
        self.assertEqual(
            [
                {
                    "check_id": "workflow-artifacts",
                    "command": ["python", ".ai/scripts/validate-workflow-artifacts.py"],
                },
                {
                    "check_id": "assessment-artifacts",
                    "command": ["python", ".ai/scripts/validate-assessment-artifacts.py"],
                },
                {
                    "check_id": "source-ai-context-version",
                    "command": ["python", ".ai/scripts/validate-ai-context-versions.py"],
                },
            ],
            source["native_full_validators"],
        )
        helper_source = HELPER.read_text(encoding="utf-8")
        self.assertNotIn('["rev-list", "--first-parent", head]', helper_source)
        verify_body = helper_source.split("def verify_source", 1)[1].split("def refresh_source", 1)[0]
        self.assertIn("include_release_refs=False", verify_body)
        self.assertIn("release_ref_records(repo, source_revision)", verify_body)

if __name__ == "__main__":
    unittest.main()
