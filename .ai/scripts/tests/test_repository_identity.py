#!/usr/bin/env python3
"""GWT tests for the fail-closed retired repository identity policy."""

from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import yaml


REPO_ROOT = Path(__file__).resolve().parents[3]
VALIDATOR = REPO_ROOT / ".ai/scripts/validate-repository-identity.py"
POLICY_PATH = ".ai/distribution/repository-identity-policy.yaml"
RETIRED = "ai-collaboration-prompts-dotnet-backend"


class SyntheticIdentityRepository:
    def __init__(self) -> None:
        self._temporary = tempfile.TemporaryDirectory(prefix="repository-identity-")
        self.root = Path(self._temporary.name)
        result = subprocess.run(
            ["git", "init", "--quiet"],
            cwd=self.root,
            check=False,
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            self.close()
            raise RuntimeError(result.stderr)

    def close(self) -> None:
        self._temporary.cleanup()

    def write(self, relative: str, content: str) -> None:
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8", newline="\n")

    def write_policy(self, rules: list[dict[str, object]]) -> None:
        policy = {
            "schema_version": "1.0",
            "policy_id": "fixture-retired-identity",
            "issue": 150,
            "status": "active",
            "current_identity": {
                "repository_slug": "ai-collaboration-framework",
                "repository": "YuChia-Wei/ai-collaboration-framework",
            },
            "retired_identities": [
                {"id": "retired-repository", "literal": RETIRED},
            ],
            "scan": {
                "source": "git-index-and-untracked-nonignored",
                "case_sensitive": True,
                "match_unit": "line",
            },
            "allowed_classifications": [
                "public-compatibility",
                "historical-immutable-evidence",
                "generated-projection",
                "product-or-package-identity",
                "fixture",
                "unrelated-text",
            ],
            "forbidden_classifications": ["current-operational"],
            "rules": [
                {
                    "id": "SELF",
                    "classification": "public-compatibility",
                    "disposition": "validator-input",
                    "paths": [POLICY_PATH],
                    "minimum_occurrence_lines": 1,
                    "minimum_files": 1,
                    "rationale": "The policy declares its rejected literal.",
                },
                *rules,
            ],
        }
        self.write(POLICY_PATH, yaml.safe_dump(policy, sort_keys=False))

    def validate(self) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                sys.executable,
                str(VALIDATOR),
                "--root",
                str(self.root),
                "--policy",
                POLICY_PATH,
            ],
            cwd=REPO_ROOT,
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )


def allowed_rule(
    rule_id: str,
    path: str,
    *,
    classification: str = "historical-immutable-evidence",
) -> dict[str, object]:
    return {
        "id": rule_id,
        "classification": classification,
        "disposition": "retain",
        "paths": [path],
        "minimum_occurrence_lines": 1,
        "minimum_files": 1,
        "rationale": "Synthetic classified evidence.",
    }


class RepositoryIdentityGwtTests(unittest.TestCase):
    def test_gwt_001_given_real_source_when_validated_then_every_retired_line_is_classified(self) -> None:
        result = subprocess.run(
            [sys.executable, str(VALIDATOR)],
            cwd=REPO_ROOT,
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("Repository identity validation passed", result.stdout)
        self.assertIn("GOV007-ALLOW-009", result.stdout)

    def test_gwt_002_given_classified_untracked_evidence_when_validated_then_it_passes(self) -> None:
        fixture = SyntheticIdentityRepository()
        try:
            fixture.write("history/receipt.md", f"Observed {RETIRED} before rename.\n")
            fixture.write_policy([allowed_rule("HISTORY", "history/receipt.md")])

            result = fixture.validate()

            self.assertEqual(0, result.returncode, result.stdout + result.stderr)
            self.assertIn("2 retired-name line(s)", result.stdout)
            self.assertIn("HISTORY: 1 line(s), 1 file(s)", result.stdout)
        finally:
            fixture.close()

    def test_gwt_003_given_unclassified_current_path_when_validated_then_it_fails(self) -> None:
        fixture = SyntheticIdentityRepository()
        try:
            fixture.write("README.md", f"Clone {RETIRED}.\n")
            fixture.write_policy([])

            result = fixture.validate()

            self.assertEqual(1, result.returncode)
            self.assertIn("unclassified retired identity at README.md:1", result.stderr)
        finally:
            fixture.close()

    def test_gwt_004_given_stale_exception_rule_when_validated_then_it_fails(self) -> None:
        fixture = SyntheticIdentityRepository()
        try:
            fixture.write("history/receipt.md", "Only the current repository remains.\n")
            fixture.write_policy([allowed_rule("STALE", "history/receipt.md")])

            result = fixture.validate()

            self.assertEqual(1, result.returncode)
            self.assertIn("stale rule STALE", result.stderr)
        finally:
            fixture.close()

    def test_gwt_005_given_overlapping_rules_when_validated_then_it_fails(self) -> None:
        fixture = SyntheticIdentityRepository()
        try:
            fixture.write("history/receipt.md", f"Observed {RETIRED}.\n")
            fixture.write_policy(
                [
                    allowed_rule("HISTORY-A", "history/receipt.md"),
                    allowed_rule("HISTORY-B", "history/receipt.md"),
                ]
            )

            result = fixture.validate()

            self.assertEqual(1, result.returncode)
            self.assertIn("overlapping rules for history/receipt.md", result.stderr)
        finally:
            fixture.close()

    def test_gwt_006_given_excluded_path_when_it_contains_retired_name_then_it_is_unclassified(self) -> None:
        fixture = SyntheticIdentityRepository()
        try:
            fixture.write("history/current.md", f"Current default: {RETIRED}.\n")
            fixture.write_policy(
                [
                    {
                        "id": "HISTORY-GLOB",
                        "classification": "historical-immutable-evidence",
                        "disposition": "retain",
                        "path_globs": ["history/**"],
                        "excluded_patterns": ["history/current.md"],
                        "minimum_occurrence_lines": 1,
                        "minimum_files": 1,
                        "rationale": "Synthetic historical scope with an operational exclusion.",
                    }
                ]
            )

            result = fixture.validate()

            self.assertEqual(1, result.returncode)
            self.assertIn("unclassified retired identity at history/current.md:1", result.stderr)
            self.assertIn("stale rule HISTORY-GLOB", result.stderr)
        finally:
            fixture.close()

    def test_gwt_007_given_current_operational_exception_when_loaded_then_policy_fails(self) -> None:
        fixture = SyntheticIdentityRepository()
        try:
            fixture.write("README.md", f"Clone {RETIRED}.\n")
            fixture.write_policy(
                [allowed_rule("FORBIDDEN", "README.md", classification="current-operational")]
            )

            result = fixture.validate()

            self.assertEqual(1, result.returncode)
            self.assertIn("uses forbidden classification: current-operational", result.stderr)
        finally:
            fixture.close()


if __name__ == "__main__":
    unittest.main()
