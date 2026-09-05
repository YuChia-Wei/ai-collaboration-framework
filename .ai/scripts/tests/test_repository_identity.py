#!/usr/bin/env python3
"""GWT tests for the fail-closed retired repository identity policy."""

from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from collections.abc import Callable
from pathlib import Path

import yaml


REPO_ROOT = Path(__file__).resolve().parents[3]
VALIDATOR = REPO_ROOT / ".ai/scripts/validate-repository-identity.py"
POLICY_PATH = ".ai/distribution/repository-identity-policy.yaml"
REGISTRY_PATH = ".ai/distribution/identity-registry.yaml"
REGISTRY_SCHEMA_PATH = ".ai/distribution/schemas/identity-registry.schema.yaml"
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

    def write_registry(
        self,
        mutate: Callable[[dict[str, object]], None] | None = None,
    ) -> None:
        registry = yaml.safe_load(
            (REPO_ROOT / REGISTRY_PATH).read_text(encoding="utf-8")
        )
        if mutate is not None:
            mutate(registry)
        self.write(REGISTRY_SCHEMA_PATH, 'schema_version: "1.1"\n')
        self.write(
            ".ai/distribution/profiles/dotnet-backend.yaml",
            yaml.safe_dump(
                {
                    "profile": {"id": "dotnet-backend"},
                    "release_model": "single-versioned-componentized-release",
                    "package": {
                        "source_repository": "https://github.com/YuChia-Wei/ai-collaboration-framework",
                        "identity_registry": REGISTRY_PATH,
                        "identity_policy": "public-package-identity-v1",
                    },
                },
                sort_keys=False,
            ),
        )
        self.write("README.md", "# AI Collaboration Framework\n")
        self.write("README.en.md", "# AI Collaboration Framework\n")
        self.write(
            ".dev/releases/v0.3.0/release.yaml",
            yaml.safe_dump(
                {
                    "version": "v0.3.0",
                    "release_id": "REL-v0.3.0",
                    "distribution": {
                        "package_id": "ai-context-dotnet-backend-v0.3.0"
                    },
                },
                sort_keys=False,
            ),
        )
        self.write(
            ".ai/assets/skills/transitions/v0.6.0.yaml",
            yaml.safe_dump(
                {
                    "transitions": [
                        {
                            "current_identifier": "repo-structure-sync",
                            "candidate_identifier": "ai-context-init",
                        },
                        {
                            "current_identifier": "dev-workflow",
                            "candidate_identifier": "software-development-orchestrator",
                        },
                    ]
                },
                sort_keys=False,
            ),
        )
        self.write(
            ".ai/assets/skills/transitions/v0.16.0.yaml",
            (REPO_ROOT / ".ai/assets/skills/transitions/v0.16.0.yaml").read_text(encoding="utf-8"),
        )
        self.write(REGISTRY_PATH, yaml.safe_dump(registry, sort_keys=False))

    def write_policy(
        self,
        rules: list[dict[str, object]],
        *,
        registry_mutator: Callable[[dict[str, object]], None] | None = None,
    ) -> None:
        self.write_registry(registry_mutator)
        policy = {
            "schema_version": "1.0",
            "policy_id": "fixture-retired-identity",
            "issue": 150,
            "status": "active",
            "identity_registry": {
                "path": REGISTRY_PATH,
                "current_repository_id": "repository.framework-source",
                "retired_alias_refs": [
                    {
                        "identity_id": "repository.framework-source",
                        "alias_id": "pre-v0.12-repository-slug",
                    }
                ],
            },
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
                    "paths": [REGISTRY_PATH],
                    "minimum_occurrence_lines": 1,
                    "minimum_files": 1,
                    "rationale": "The registry declares its retired aliases.",
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
            self.assertIn("4 retired-name line(s)", result.stdout)
            self.assertIn("HISTORY: 1 line(s), 1 file(s)", result.stdout)
        finally:
            fixture.close()

    def test_gwt_003_given_unclassified_current_path_when_validated_then_it_fails(self) -> None:
        fixture = SyntheticIdentityRepository()
        try:
            fixture.write_policy([])
            fixture.write(
                "README.md",
                f"# AI Collaboration Framework\nClone {RETIRED}.\n",
            )

            result = fixture.validate()

            self.assertEqual(1, result.returncode)
            self.assertIn("unclassified retired identity at README.md:2", result.stderr)
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

    def test_gwt_008_given_duplicate_canonical_id_when_registry_is_loaded_then_it_fails(self) -> None:
        fixture = SyntheticIdentityRepository()
        try:
            def duplicate_id(registry: dict[str, object]) -> None:
                records = registry["identity_records"]
                records[1]["id"] = records[0]["id"]

            fixture.write_policy([], registry_mutator=duplicate_id)

            result = fixture.validate()

            self.assertEqual(1, result.returncode)
            self.assertIn("duplicate canonical identity id", result.stderr)
        finally:
            fixture.close()

    def test_gwt_009_given_ambiguous_alias_value_when_registry_is_loaded_then_it_fails(self) -> None:
        fixture = SyntheticIdentityRepository()
        try:
            def duplicate_alias(registry: dict[str, object]) -> None:
                aliases = registry["identity_records"][0]["aliases"]
                aliases[1]["value"] = aliases[0]["value"]

            fixture.write_policy([], registry_mutator=duplicate_alias)

            result = fixture.validate()

            self.assertEqual(1, result.returncode)
            self.assertIn("ambiguous alias value", result.stderr)
        finally:
            fixture.close()

    def test_gwt_010_given_repository_product_value_coupling_when_loaded_then_it_fails(self) -> None:
        fixture = SyntheticIdentityRepository()
        try:
            def couple_product(registry: dict[str, object]) -> None:
                records = registry["identity_records"]
                records[1]["canonical_value"] = records[0]["canonical_value"]

            fixture.write_policy([], registry_mutator=couple_product)

            result = fixture.validate()

            self.assertEqual(1, result.returncode)
            self.assertIn("duplicate canonical identity value", result.stderr)
        finally:
            fixture.close()

    def test_gwt_011_given_declared_consumer_drift_when_validated_then_it_fails(self) -> None:
        fixture = SyntheticIdentityRepository()
        try:
            fixture.write_policy([])
            fixture.write(
                ".ai/distribution/profiles/dotnet-backend.yaml",
                yaml.safe_dump(
                    {
                        "profile": {"id": "dotnet-backend"},
                        "release_model": "single-versioned-componentized-release",
                        "package": {
                            "source_repository": "https://example.invalid/wrong",
                            "identity_registry": REGISTRY_PATH,
                            "identity_policy": "public-package-identity-v1",
                        },
                    },
                    sort_keys=False,
                ),
            )

            result = fixture.validate()

            self.assertEqual(1, result.returncode)
            self.assertIn("distribution-profile-repository consumer drift", result.stderr)
        finally:
            fixture.close()

    def test_gwt_012_given_v015_current_identity_is_duplicated_when_loaded_then_it_fails_closed(self) -> None:
        fixture = SyntheticIdentityRepository()
        try:
            def activate_legacy(registry: dict[str, object]) -> None:
                records = registry["identity_records"]
                legacy = next(item for item in records if item["id"] == "package.ai-context-dotnet-backend-legacy")
                legacy["status"] = "active"

            fixture.write_policy([], registry_mutator=activate_legacy)
            result = fixture.validate()
            self.assertEqual(1, result.returncode)
            self.assertIn("must be legacy-compatible", result.stderr)
        finally:
            fixture.close()

    def test_gwt_013_given_identity_policy_range_drifts_when_loaded_then_it_fails_closed(self) -> None:
        fixture = SyntheticIdentityRepository()
        try:
            def overlap_ranges(registry: dict[str, object]) -> None:
                registry["package_identity_policy"]["rules"][0][
                    "maximum_version_exclusive"
                ] = "v0.16.0"

            fixture.write_policy([], registry_mutator=overlap_ranges)
            result = fixture.validate()
            self.assertEqual(1, result.returncode)
            self.assertIn(
                "maximum_version_exclusive must be 'v0.15.0'", result.stderr
            )
        finally:
            fixture.close()


if __name__ == "__main__":
    unittest.main()
