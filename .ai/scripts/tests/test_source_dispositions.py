#!/usr/bin/env python3
"""Given-When-Then tests for the source-disposition coverage contract."""

from __future__ import annotations

import copy
import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
MODULE_PATH = ROOT / ".ai/scripts/validate-source-dispositions.py"
SPEC = importlib.util.spec_from_file_location("validate_source_dispositions", MODULE_PATH)
assert SPEC and SPEC.loader
SOURCE_DISPOSITIONS = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(SOURCE_DISPOSITIONS)


def contract() -> dict:
    return {
        "schema_version": "1.0",
        "schema": ".ai/distribution/schemas/source-dispositions.schema.yaml",
        "contract_id": "fixture-source-dispositions",
        "issue": 184,
        "status": "active",
        "owner_skill": "ai-context-governance",
        "profile": {
            "id": "dotnet-backend",
            "path": ".ai/distribution/profiles/dotnet-backend.yaml",
        },
        "coverage": {
            "source_patterns": [".dev/**"],
            "baseline_assessment": "ASM-20260810-003#PKG-001",
            "derivation": "tracked-minus-packaged-minus-explicit-exclusion",
        },
        "dispositions": [
            {
                "id": "fixture-omission",
                "patterns": [".dev/omitted.md"],
                "classification": "source-only",
                "owner": "fixture-owner",
                "reason": "The fixture path is intentionally source-only.",
                "retention": "retain-active",
                "package_behavior": "exclude",
            }
        ],
    }


class SourceDispositionContractTests(unittest.TestCase):
    def validate(
        self,
        data: dict,
        *,
        tracked: set[str] | None = None,
        packaged: set[str] | None = None,
        excluded: set[str] | None = None,
    ) -> dict:
        return SOURCE_DISPOSITIONS.validate_contract_data(
            data,
            tracked_paths=tracked or {".dev/packaged.md", ".dev/excluded.md", ".dev/omitted.md"},
            packaged_paths=packaged or {".dev/packaged.md"},
            excluded_paths=excluded or {".dev/excluded.md"},
            source_ref="fixture",
            source_commit="a" * 40,
            source_tree="b" * 40,
        )

    def test_gwt_001_given_exact_disposition_coverage_when_validated_then_no_implicit_omission_remains(self) -> None:
        report = self.validate(contract())
        paths = [entry["path"] for entry in report["paths"]]
        self.assertEqual(0, report["coverage"]["implicit_omissions"])
        self.assertEqual(report["coverage"]["disposition_paths"], len(paths))
        self.assertEqual(len(paths), len(set(paths)), f"duplicate disposition paths: {paths}")
        self.assertEqual({".dev/omitted.md"}, set(paths))

    def test_gwt_002_given_a_new_implicit_omission_when_validated_then_it_fails_closed(self) -> None:
        with self.assertRaisesRegex(SOURCE_DISPOSITIONS.SourceDispositionError, "missing=.*new.md"):
            self.validate(
                contract(),
                tracked={
                    ".dev/packaged.md",
                    ".dev/excluded.md",
                    ".dev/omitted.md",
                    ".dev/new.md",
                },
            )

    def test_gwt_003_given_overlapping_patterns_when_validated_then_it_fails_closed(self) -> None:
        data = contract()
        duplicate = copy.deepcopy(data["dispositions"][0])
        duplicate["id"] = "overlapping-omission"
        data["dispositions"].append(duplicate)
        with self.assertRaisesRegex(SOURCE_DISPOSITIONS.SourceDispositionError, "duplicate disposition pattern"):
            self.validate(data)

    def test_gwt_004_given_a_stale_pattern_when_validated_then_it_fails_closed(self) -> None:
        data = contract()
        data["dispositions"][0]["patterns"] = [".dev/missing.md"]
        with self.assertRaisesRegex(SOURCE_DISPOSITIONS.SourceDispositionError, "stale disposition pattern"):
            self.validate(data)

    def test_gwt_005_given_a_payload_overlap_when_validated_then_it_fails_closed(self) -> None:
        data = contract()
        data["dispositions"][0]["patterns"] = [".dev/packaged.md"]
        with self.assertRaisesRegex(SOURCE_DISPOSITIONS.SourceDispositionError, "overlap packaged"):
            self.validate(data)

    def test_gwt_006_given_an_explicit_exclusion_overlap_when_validated_then_it_fails_closed(self) -> None:
        data = contract()
        data["dispositions"][0]["patterns"] = [".dev/excluded.md"]
        with self.assertRaisesRegex(SOURCE_DISPOSITIONS.SourceDispositionError, "overlap explicit"):
            self.validate(data)

    def test_gwt_007_given_an_unknown_classification_when_validated_then_it_fails_closed(self) -> None:
        data = contract()
        data["dispositions"][0]["classification"] = "mystery"
        with self.assertRaisesRegex(SOURCE_DISPOSITIONS.SourceDispositionError, "classification must be one of"):
            self.validate(data)

    def test_gwt_008_given_the_current_repository_when_validated_then_all_current_omissions_are_governed(self) -> None:
        report = SOURCE_DISPOSITIONS.validate_repository(ROOT)
        paths = [entry["path"] for entry in report["paths"]]
        self.assertEqual(0, report["coverage"]["implicit_omissions"])
        self.assertTrue(paths, "current source-disposition coverage must not be empty")
        self.assertEqual(report["coverage"]["disposition_paths"], len(paths))
        self.assertEqual(len(paths), len(set(paths)), f"duplicate disposition paths: {paths}")


if __name__ == "__main__":
    unittest.main()
