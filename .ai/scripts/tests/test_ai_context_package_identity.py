#!/usr/bin/env python3
"""GWT tests for the v0.15 public package identity boundary."""

from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[3]
SCRIPTS = ROOT / ".ai/scripts"
sys.path.insert(0, str(SCRIPTS))

import ai_context_package_identity as IDENTITY  # noqa: E402


class PackageIdentityBoundaryGwtTests(unittest.TestCase):
    def test_gwt_001_given_versions_around_cutover_when_resolved_then_each_has_one_exact_base(self) -> None:
        self.assertEqual(
            "ai-context-dotnet-backend-v0.14.0",
            IDENTITY.expected_package_id("v0.14.0"),
        )
        self.assertEqual(
            "ai-context-dotnet-backend-v0.14.99",
            IDENTITY.expected_package_id("v0.14.99"),
        )
        self.assertEqual(
            "ai-collaboration-framework-v0.15.0",
            IDENTITY.expected_package_id("v0.15.0"),
        )
        self.assertEqual(
            "ai-collaboration-framework-v1.0.0",
            IDENTITY.expected_package_id("1.0.0"),
        )

    def test_gwt_002_given_v015_when_assets_are_resolved_then_exactly_four_names_share_one_base(self) -> None:
        artifacts = IDENTITY.expected_artifacts("v0.15.0")
        base = "ai-collaboration-framework-v0.15.0"
        self.assertEqual(
            {
                "zip": f"{base}.zip",
                "zip_checksum": f"{base}.zip.sha256",
                "tar_gz": f"{base}.tar.gz",
                "tar_gz_checksum": f"{base}.tar.gz.sha256",
            },
            artifacts,
        )

    def test_gwt_003_given_unknown_version_when_resolved_then_it_fails_before_guessing(self) -> None:
        for value in ("latest", "0.15", "v0.15.0.zip", ""):
            with self.subTest(value=value):
                with self.assertRaises(IDENTITY.PackageIdentityError):
                    IDENTITY.expected_package_id(value)

    def test_gwt_004_given_tracked_registry_when_resolved_then_policy_matches_both_ranges(self) -> None:
        registry = yaml.safe_load(
            (ROOT / ".ai/distribution/identity-registry.yaml").read_text(encoding="utf-8")
        )
        legacy = IDENTITY.resolve_registry_identity(registry, "v0.14.0")
        current = IDENTITY.resolve_registry_identity(registry, "v0.15.0")
        self.assertEqual(IDENTITY.LEGACY_RULE_ID, legacy["rule_id"])
        self.assertEqual(IDENTITY.CURRENT_RULE_ID, current["rule_id"])
        self.assertNotEqual(legacy["identity_id"], current["identity_id"])
        self.assertEqual(IDENTITY.POLICY_ID, current["policy_id"])

    def test_gwt_005_given_cli_resolution_when_invoked_then_output_is_one_unambiguous_base(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                str(SCRIPTS / "resolve-ai-context-package-identity.py"),
                "--version",
                "v0.15.0",
            ],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertEqual("ai-collaboration-framework-v0.15.0", result.stdout.strip())


if __name__ == "__main__":
    unittest.main()
