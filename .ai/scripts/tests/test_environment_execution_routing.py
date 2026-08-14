#!/usr/bin/env python3
"""GWT tests for portable environment execution routing and ignored local state."""

from __future__ import annotations

import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[3]
SCRIPTS = ROOT / ".ai/scripts"

import sys

sys.path.insert(0, str(SCRIPTS))

import ai_context_environment_routing as ROUTING


def git(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args], cwd=root, check=False, capture_output=True, text=True
    )


class RoutingFixture:
    def __init__(self, *, ignored: bool = True) -> None:
        self._temporary = tempfile.TemporaryDirectory(prefix="environment-routing-")
        self.root = Path(self._temporary.name) / "target"
        self.root.mkdir()
        self.local = self.root / ROUTING.LOCAL_PATH
        (self.root / ROUTING.CONTRACT_PATH).parent.mkdir(parents=True)
        shutil.copy2(ROOT / ROUTING.CONTRACT_PATH, self.root / ROUTING.CONTRACT_PATH)
        shutil.copy2(ROOT / ROUTING.SCHEMA_PATH, self.root / ROUTING.SCHEMA_PATH)
        (self.root / ".gitignore").write_text(
            f"{ROUTING.IGNORE_RULE}\n" if ignored else "*.tmp\n",
            encoding="utf-8",
            newline="\n",
        )
        self.assert_git("init", "-q")
        self.assert_git("config", "user.name", "Fixture")
        self.assert_git("config", "user.email", "fixture@example.invalid")
        self.assert_git("add", ".gitignore", ROUTING.CONTRACT_PATH.as_posix(), ROUTING.SCHEMA_PATH.as_posix())
        self.assert_git("commit", "-qm", "fixture baseline")

    def assert_git(self, *args: str) -> None:
        result = git(self.root, *args)
        if result.returncode != 0:
            raise AssertionError(result.stdout + result.stderr)

    def write(self, document: dict) -> None:
        self.local.parent.mkdir(parents=True, exist_ok=True)
        self.local.write_text(
            yaml.safe_dump(document, sort_keys=False),
            encoding="utf-8",
            newline="\n",
        )

    def close(self) -> None:
        self._temporary.cleanup()


class EnvironmentExecutionRoutingGwtTests(unittest.TestCase):
    @staticmethod
    def valid_document() -> dict:
        requirements = {
            "network": "required",
            "credential_boundary": "runtime-managed",
            "filesystem_write": "none",
            "privilege": "standard",
            "approval": "not-required",
        }
        return {
            "schema_version": "1.0",
            "record_type": "environment-execution-routing-local",
            "routes": [
                {
                    "operation_id": "remote.metadata",
                    "capability_id": "remote-api",
                    "candidates": [
                        {
                            "route_id": "primary-connector",
                            "surface": "connector",
                            "sandbox": "not-applicable",
                            "selectors": {"connector": "preferred-provider"},
                            "working_directory": "repository-root",
                            "requirements": requirements,
                            "fallback": {
                                "on": ["connector-gap"],
                                "to": ["host-cli"],
                                "retry": "material-change-only",
                                "max_attempts": 1,
                            },
                        },
                        {
                            "route_id": "host-cli",
                            "surface": "host-shell",
                            "sandbox": "outside",
                            "selectors": {"executable": "provider-cli"},
                            "working_directory": "repository-root",
                            "requirements": {
                                **requirements,
                                "credential_boundary": "host-managed",
                                "approval": "required-before-execution",
                            },
                            "fallback": {
                                "on": [],
                                "to": [],
                                "retry": "material-change-only",
                                "max_attempts": 1,
                            },
                        },
                    ],
                    "persistence": {
                        "consent": "explicit",
                        "reason": "post-recovery-success",
                        "recorded_at": "2026-08-14T21:40:34+08:00",
                        "change": "create",
                    },
                }
            ],
        }

    def test_gwt_001_given_portable_contract_without_local_binding_when_validated_then_unconfigured_passes(self) -> None:
        errors: list[str] = []

        count = ROUTING.validate_environment_execution_routing(errors, root=ROOT)

        self.assertEqual(0, count)
        self.assertEqual([], errors)

    def test_gwt_002_given_explicitly_consented_ignored_binding_when_validated_then_passes(self) -> None:
        fixture = RoutingFixture()
        try:
            fixture.write(self.valid_document())
            errors: list[str] = []

            count = ROUTING.validate_environment_execution_routing(errors, root=fixture.root)

            self.assertEqual(1, count)
            self.assertEqual([], errors)
            self.assertEqual(1, git(fixture.root, "ls-files", "--error-unmatch", "--", ROUTING.LOCAL_PATH.as_posix()).returncode)
        finally:
            fixture.close()

    def test_gwt_003_given_local_binding_without_ignore_rule_when_validated_then_fails_closed(self) -> None:
        fixture = RoutingFixture(ignored=False)
        try:
            fixture.write(self.valid_document())
            errors: list[str] = []

            ROUTING.validate_environment_execution_routing(errors, root=fixture.root)

            self.assertTrue(any("missing exact" in error for error in errors))
            self.assertTrue(any("is not Git-ignored" in error for error in errors))
        finally:
            fixture.close()

    def test_gwt_004_given_ignored_but_tracked_personal_binding_when_validated_then_fails_closed(self) -> None:
        fixture = RoutingFixture()
        try:
            fixture.write(self.valid_document())
            fixture.assert_git("add", "-f", ROUTING.LOCAL_PATH.as_posix())
            fixture.assert_git("commit", "-qm", "incorrectly track personal route")
            errors: list[str] = []

            ROUTING.validate_environment_execution_routing(errors, root=fixture.root)

            self.assertTrue(any("must not be Git-tracked" in error for error in errors))
        finally:
            fixture.close()

    def test_gwt_005_given_missing_consent_and_sensitive_field_when_validated_then_both_are_rejected(self) -> None:
        fixture = RoutingFixture()
        try:
            document = self.valid_document()
            document["routes"][0]["persistence"]["consent"] = "implicit"
            document["routes"][0]["token"] = "not-a-real-secret"
            fixture.write(document)
            errors: list[str] = []

            ROUTING.validate_environment_execution_routing(errors, root=fixture.root)

            self.assertTrue(any("forbidden field" in error and "token" in error for error in errors))
            self.assertTrue(any("persistence.consent must be explicit" in error for error in errors))
        finally:
            fixture.close()

    def test_gwt_006_given_disallowed_fallback_or_repeated_attempt_when_validated_then_fails_closed(self) -> None:
        fixture = RoutingFixture()
        try:
            document = self.valid_document()
            fallback = document["routes"][0]["candidates"][0]["fallback"]
            fallback["on"] = ["disallowed"]
            fallback["max_attempts"] = 2
            fixture.write(document)
            errors: list[str] = []

            ROUTING.validate_environment_execution_routing(errors, root=fixture.root)

            self.assertTrue(any("fallback.on is invalid" in error for error in errors))
            self.assertTrue(any("max_attempts must equal 1" in error for error in errors))
        finally:
            fixture.close()

    def test_gwt_007_given_portable_assets_when_inspected_then_no_source_host_route_is_a_default(self) -> None:
        portable = "\n".join(
            [
                (ROOT / ROUTING.CONTRACT_PATH).read_text(encoding="utf-8"),
                (ROOT / ROUTING.SCHEMA_PATH).read_text(encoding="utf-8"),
            ]
        )
        profile = yaml.safe_load(
            (ROOT / ".ai/distribution/profiles/dotnet-backend.yaml").read_text(encoding="utf-8")
        )
        local_state = next(
            item
            for item in profile["exclusions"]
            if item["id"] == "repository-and-local-runtime-state"
        )

        self.assertNotIn("Ubuntu-24.04", portable)
        self.assertNotIn(".dev/ai-context/local/environment-execution-routing.yaml", {
            path.as_posix() for path in ROOT.glob(".dev/ai-context/local/*")
        })
        self.assertIn(".dev/ai-context/local/**", local_state["patterns"])
        target_validator = (
            ROOT / ".ai/scripts/validate-ai-context-target.py"
        ).read_text(encoding="utf-8")
        self.assertIn(
            "validate_environment_execution_routing",
            target_validator,
        )

    def test_gwt_008_given_agent_guidance_when_recovery_succeeds_then_consent_prompt_precedes_write(self) -> None:
        for path in (
            ROOT / "AGENTS.md",
            ROOT / "AGENTS.zh-TW.md",
            ROOT / ".ai/assets/skills/ai-context-init/templates/public-root/AGENTS.md",
        ):
            with self.subTest(path=path):
                text = path.read_text(encoding="utf-8")
                self.assertIn("environment-execution-routing.yaml", text)
                self.assertIn("create/merge/replace", text)
                self.assertTrue("decline or no answer" in text or "拒絕或未回覆" in text)


if __name__ == "__main__":
    unittest.main()
