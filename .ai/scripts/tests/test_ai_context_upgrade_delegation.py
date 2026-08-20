#!/usr/bin/env python3
"""Focused GWT coverage for the UPG-004 per-run delegation contract."""

from __future__ import annotations

import importlib.util
import os
import shutil
import stat
import unittest
import uuid
from pathlib import Path

import yaml


REPO_ROOT = Path(__file__).resolve().parents[3]
VALIDATOR_PATH = REPO_ROOT / ".ai/scripts/validate-ai-context.py"
SPEC = importlib.util.spec_from_file_location(
    "validate_ai_context_upgrade_delegation", VALIDATOR_PATH
)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"Unable to load validator: {VALIDATOR_PATH}")
VALIDATOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VALIDATOR)


class WorkspaceTemporaryDirectory:
    """Use repository-inherited ACLs instead of Windows tempfile 0700 ACLs."""

    def __init__(self, prefix: str) -> None:
        root = REPO_ROOT / ".tmp" / prefix
        root.mkdir(parents=True, exist_ok=True)
        self.path = root / uuid.uuid4().hex[:12]
        self.path.mkdir()

    @staticmethod
    def _remove_readonly(function: object, path: str, _: object) -> None:
        os.chmod(path, stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR)
        function(path)  # type: ignore[operator]

    def cleanup(self) -> None:
        if self.path.exists():
            shutil.rmtree(self.path, onerror=self._remove_readonly)


class DelegationRunContractFixture:
    """Own one isolated copy of the portable UPG-004 contract surface."""

    paths = (
        ".ai/assets/skills/ai-context-upgrader/references/delegation-run-contract.md",
        ".ai/assets/skills/ai-context-upgrader/references/"
        "delegation-run-contract.schema.yaml",
        ".ai/assets/skills/ai-context-upgrader/templates/"
        "delegation-run-record.template.yaml",
        ".ai/assets/skills/ai-context-upgrader/skill.yaml",
        ".agents/skills/ai-context-upgrader/SKILL.md",
        ".claude/skills/ai-context-upgrader/SKILL.md",
    )

    def __init__(self) -> None:
        self._temporary = WorkspaceTemporaryDirectory("upg004-delegation-")
        self.root = self._temporary.path
        for relative in self.paths:
            destination = self.root / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes((REPO_ROOT / relative).read_bytes())

    def close(self) -> None:
        self._temporary.cleanup()

    def path(self, relative: str) -> Path:
        return self.root / relative

    def read_yaml(self, relative: str) -> dict:
        value = yaml.safe_load(self.path(relative).read_text(encoding="utf-8"))
        if not isinstance(value, dict):
            raise AssertionError(f"Fixture mapping expected: {relative}")
        return value

    def write_yaml(self, relative: str, value: dict) -> None:
        self.path(relative).write_text(
            yaml.safe_dump(value, sort_keys=False), encoding="utf-8", newline="\n"
        )

    def validate(self) -> tuple[int, list[str]]:
        errors: list[str] = []
        count = VALIDATOR.validate_upg004_delegation_run_contract(
            errors, root=self.root
        )
        return count, errors


class AiContextUpgradeDelegationGwtTests(unittest.TestCase):
    template_path = (
        ".ai/assets/skills/ai-context-upgrader/templates/"
        "delegation-run-record.template.yaml"
    )
    schema_path = (
        ".ai/assets/skills/ai-context-upgrader/references/"
        "delegation-run-contract.schema.yaml"
    )

    def assert_error(self, errors: list[str], fragment: str) -> None:
        self.assertTrue(any(fragment in error for error in errors), errors)

    def test_gwt_001_given_owner_selected_full_recommended_when_validated_then_passes(self) -> None:
        fixture = DelegationRunContractFixture()
        try:
            count, errors = fixture.validate()
            self.assertEqual([], errors)
            self.assertEqual(1, count)
        finally:
            fixture.close()

    def test_gwt_002_given_provider_field_in_portable_record_when_validated_then_fails_closed(self) -> None:
        fixture = DelegationRunContractFixture()
        try:
            record = fixture.read_yaml(self.template_path)
            record["selection"]["model"] = "gpt-5.6-terra"
            fixture.write_yaml(self.template_path, record)
            _, errors = fixture.validate()
            self.assert_error(errors, "provider/runtime field leaks")
        finally:
            fixture.close()

    def test_gwt_003_given_explicit_choice_when_prompt_is_not_suppressed_then_fails_closed(self) -> None:
        fixture = DelegationRunContractFixture()
        try:
            record = fixture.read_yaml(self.template_path)
            record["selection"]["prompt"] = {
                "count": 1,
                "disposition": "recorded-owner-choice",
            }
            fixture.write_yaml(self.template_path, record)
            _, errors = fixture.validate()
            self.assert_error(errors, "must suppress an explicit choice")
        finally:
            fixture.close()

    def test_gwt_004_given_resume_repeats_prompt_when_validated_then_fails_closed(self) -> None:
        fixture = DelegationRunContractFixture()
        try:
            record = fixture.read_yaml(self.template_path)
            record["selection"]["resume"]["repeat_prompt"] = True
            fixture.write_yaml(self.template_path, record)
            _, errors = fixture.validate()
            self.assert_error(errors, "must reuse without a repeat prompt")
        finally:
            fixture.close()

    def test_gwt_005_given_root_sequential_after_selection_without_receipt_then_fails_closed(self) -> None:
        fixture = DelegationRunContractFixture()
        try:
            record = fixture.read_yaml(self.template_path)
            record["execution_path"]["kind"] = "root-sequential"
            fixture.write_yaml(self.template_path, record)
            _, errors = fixture.validate()
            self.assert_error(errors, "root-sequential fallback requires exact evidence")
        finally:
            fixture.close()

    def test_gwt_006_given_fallback_without_exact_evidence_when_validated_then_fails_closed(self) -> None:
        fixture = DelegationRunContractFixture()
        try:
            record = fixture.read_yaml(self.template_path)
            record["execution_path"]["kind"] = "root-sequential"
            record["fallbacks"] = [
                {
                    "scope": "recommended-role-execution",
                    "disposition": "root-sequential",
                    "trigger": "verified worker support is unavailable",
                    "authorization_evidence": [],
                    "evidence_refs": [],
                    "canonical_stage_ids": record["canonical_stage_ids"],
                }
            ]
            fixture.write_yaml(self.template_path, record)
            _, errors = fixture.validate()
            self.assert_error(errors, "authorization_evidence must be a non-empty string list")
            self.assert_error(errors, "evidence_refs must be a non-empty string list")
        finally:
            fixture.close()

    def test_gwt_007_given_routine_terminal_audit_selection_when_validated_then_fails_closed(self) -> None:
        fixture = DelegationRunContractFixture()
        try:
            record = fixture.read_yaml(self.template_path)
            record["terminal_independent_audit"]["selection_basis"] = "routine-profile"
            fixture.write_yaml(self.template_path, record)
            _, errors = fixture.validate()
            self.assert_error(errors, "must use an explicit terminal-or-high-risk basis")
        finally:
            fixture.close()

    def test_gwt_008_given_schema_omits_mode_when_validated_then_fails_closed(self) -> None:
        fixture = DelegationRunContractFixture()
        try:
            schema = fixture.read_yaml(self.schema_path)
            schema["properties"]["selection"]["supported_modes"] = [
                "none",
                "analysis-only",
            ]
            fixture.write_yaml(self.schema_path, schema)
            _, errors = fixture.validate()
            self.assert_error(errors, "must retain none, analysis-only, and full-recommended")
        finally:
            fixture.close()

    def test_gwt_009_given_wrapper_omits_record_reference_when_validated_then_fails_closed(self) -> None:
        fixture = DelegationRunContractFixture()
        try:
            wrapper = fixture.path(".agents/skills/ai-context-upgrader/SKILL.md")
            wrapper.write_text(
                wrapper.read_text(encoding="utf-8").replace(
                    "  - `.ai/assets/skills/ai-context-upgrader/templates/"
                    "delegation-run-record.template.yaml`\n",
                    "",
                ),
                encoding="utf-8",
                newline="\n",
            )
            _, errors = fixture.validate()
            self.assert_error(errors, "missing UPG-004 delegation reference")
        finally:
            fixture.close()

    def test_gwt_010_given_none_mode_when_root_sequential_stages_match_then_passes(self) -> None:
        fixture = DelegationRunContractFixture()
        try:
            record = fixture.read_yaml(self.template_path)
            record["selection"]["mode"] = "none"
            record["execution_path"]["kind"] = "root-sequential"
            fixture.write_yaml(self.template_path, record)
            count, errors = fixture.validate()
            self.assertEqual([], errors)
            self.assertEqual(1, count)
        finally:
            fixture.close()

    def test_gwt_011_given_analysis_only_mode_when_stage_order_matches_then_passes(self) -> None:
        fixture = DelegationRunContractFixture()
        try:
            record = fixture.read_yaml(self.template_path)
            record["selection"]["mode"] = "analysis-only"
            fixture.write_yaml(self.template_path, record)
            count, errors = fixture.validate()
            self.assertEqual([], errors)
            self.assertEqual(1, count)
        finally:
            fixture.close()

    def test_gwt_012_given_exact_root_sequential_fallback_when_validated_then_passes(self) -> None:
        fixture = DelegationRunContractFixture()
        try:
            record = fixture.read_yaml(self.template_path)
            record["execution_path"]["kind"] = "root-sequential"
            record["fallbacks"] = [
                {
                    "scope": "recommended-role-execution",
                    "disposition": "root-sequential",
                    "trigger": "verified worker support is unavailable",
                    "authorization_evidence": ["owner-selected fallback"],
                    "evidence_refs": ["workflow-task#worker-unavailable"],
                    "canonical_stage_ids": record["canonical_stage_ids"],
                }
            ]
            fixture.write_yaml(self.template_path, record)
            count, errors = fixture.validate()
            self.assertEqual([], errors)
            self.assertEqual(1, count)
        finally:
            fixture.close()


if __name__ == "__main__":
    unittest.main()
