#!/usr/bin/env python3
"""GWT tests for source work-management authority and compatibility."""

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
MODULE_PATH = ROOT / ".ai/scripts/validate-source-work-management.py"
SPEC = importlib.util.spec_from_file_location("source_work_management", MODULE_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"Unable to load validator: {MODULE_PATH}")
VALIDATOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VALIDATOR)


class SourceWorkManagementGwtTests(unittest.TestCase):
    def releases(self) -> dict:
        return {
            "v0.9.0": {
                "planning": {"backlog_refs": [".dev/backlog/items/GOV-004.yaml"]}
            },
            "v0.10.0": {"planning": {"github_issue_refs": ["#133"]}},
        }

    def test_gwt_001_given_frozen_paths_and_bytes_when_digested_then_order_is_deterministic(self) -> None:
        content = {".dev/backlog/a": b"a", ".dev/backlog/b": b"b"}
        first = VALIDATOR.aggregate_digest(content, content.__getitem__)
        second = VALIDATOR.aggregate_digest(reversed(content), content.__getitem__)
        self.assertEqual(first, second)

    def test_gwt_002_given_frozen_path_or_byte_drift_when_digested_then_identity_changes(self) -> None:
        original = {".dev/backlog/a": b"a"}
        byte_drift = {".dev/backlog/a": b"b"}
        path_drift = {".dev/backlog/other": b"a"}
        digest = VALIDATOR.aggregate_digest(original, original.__getitem__)
        self.assertNotEqual(digest, VALIDATOR.aggregate_digest(byte_drift, byte_drift.__getitem__))
        self.assertNotEqual(digest, VALIDATOR.aggregate_digest(path_drift, path_drift.__getitem__))

    def test_gwt_003_given_legacy_and_online_release_scope_when_validated_then_it_passes(self) -> None:
        self.assertEqual(
            [],
            VALIDATOR.release_scope_errors(
                self.releases(),
                legacy_versions={"v0.9.0"},
                frozen_paths={".dev/backlog/items/GOV-004.yaml"},
                online_from=(0, 10, 0),
            ),
        )

    def test_gwt_004_given_v010_backlog_refs_when_validated_then_it_fails_closed(self) -> None:
        releases = self.releases()
        releases["v0.10.0"]["planning"]["backlog_refs"] = [
            ".dev/backlog/items/GOV-004.yaml"
        ]
        errors = VALIDATOR.release_scope_errors(
            releases,
            legacy_versions={"v0.9.0"},
            frozen_paths={".dev/backlog/items/GOV-004.yaml"},
            online_from=(0, 10, 0),
        )
        self.assertTrue(any("forbidden from v0.10.0" in error for error in errors))

    def test_gwt_005_given_unresolved_legacy_ref_when_validated_then_it_fails_closed(self) -> None:
        errors = VALIDATOR.release_scope_errors(
            self.releases(),
            legacy_versions={"v0.9.0"},
            frozen_paths=set(),
            online_from=(0, 10, 0),
        )
        self.assertTrue(any("unresolved frozen backlog ref" in error for error in errors))

    def test_gwt_006_given_prospective_backlog_binding_when_checked_then_it_fails_closed(self) -> None:
        task = {
            "backlog_refs": [".dev/backlog/items/NEW-001.yaml"],
            "scope": {"planning": ".dev/backlog/ROADMAP.md"},
        }
        errors = VALIDATOR.forbidden_structured_references(
            task,
            forbidden_keys={"backlog_refs"},
            forbidden_paths=(".dev/backlog/items/", ".dev/backlog/ROADMAP.md"),
        )
        self.assertEqual(3, len(errors))

    def test_gwt_007_given_online_issue_binding_when_checked_then_it_passes(self) -> None:
        task = {
            "work_item_binding": {
                "provider": "github",
                "issue": 245,
                "authorization": "explicit owner authorization",
            }
        }
        self.assertEqual(
            [],
            VALIDATOR.forbidden_structured_references(
                task,
                forbidden_keys={"backlog_refs"},
                forbidden_paths=(".dev/backlog/items/", ".dev/backlog/ROADMAP.md"),
            ),
        )


if __name__ == "__main__":
    unittest.main()
