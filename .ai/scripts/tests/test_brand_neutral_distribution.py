#!/usr/bin/env python3
"""GWT checks for the source-only historical brand boundary."""

from __future__ import annotations

import re
import sys
import unittest
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[3]
SCRIPTS = ROOT / ".ai/scripts"
sys.path.insert(0, str(SCRIPTS))
import ai_context_package as PACKAGE  # noqa: E402


PROFILE_PATH = ".ai/distribution/profiles/dotnet-backend.yaml"
SELF_PATH = ".ai/scripts/tests/test_brand_neutral_distribution.py"
SOURCE_ONLY_PREFIXES = (
    ".dev/assessments/",
    ".dev/backlog/plans/",
    ".dev/releases/",
    ".dev/workflows/",
)
BRANDED_REFERENCE = re.compile(
    r"ezddd(?:-gateway-api)?|ezspec|ezapp|ucontract|ez[- ]?(?:series|tools?|tooling)",
    re.IGNORECASE,
)


def text_contains_brand(content: bytes) -> bool:
    try:
        text = content.decode("utf-8")
    except UnicodeDecodeError:
        return False
    return BRANDED_REFERENCE.search(text) is not None


class BrandNeutralDistributionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.tree = PACKAGE.git_tree(ROOT, "HEAD")
        profile_blob = PACKAGE.git_blob(ROOT, cls.tree[PROFILE_PATH])
        cls.profile = yaml.safe_load(profile_blob.decode("utf-8"))
        cls.payload = PACKAGE.collect_payload(ROOT, cls.tree, cls.profile)

    def test_gwt_001_given_current_package_when_scanned_then_branded_references_are_absent(
        self,
    ) -> None:
        violations = sorted(
            item.path
            for item in self.payload
            if BRANDED_REFERENCE.search(item.path) or text_contains_brand(item.content)
        )
        self.assertEqual([], violations)

    def test_gwt_002_given_retained_repository_matches_when_classified_then_all_are_source_only(
        self,
    ) -> None:
        payload_sources = {item.source_path for item in self.payload}
        matches: list[str] = []
        violations: list[str] = []

        for path, entry in sorted(self.tree.items()):
            if entry.object_type != "blob":
                continue
            content = PACKAGE.git_blob(ROOT, entry)
            if not BRANDED_REFERENCE.search(path) and not text_contains_brand(content):
                continue

            matches.append(path)
            allowed = path == SELF_PATH or path.startswith(SOURCE_ONLY_PREFIXES)
            if not allowed or path in payload_sources:
                violations.append(path)

        self.assertTrue(matches, "Expected retained source-only provenance matches")
        self.assertEqual([], violations)


if __name__ == "__main__":
    unittest.main()
