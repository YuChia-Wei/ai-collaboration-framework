#!/usr/bin/env python3
"""Focused GWT coverage for the SAG-003 provider role projection boundary."""

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
    "validate_ai_context_provider_role_projection", VALIDATOR_PATH
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


class ProviderRoleProjectionFixture:
    """Own one isolated, complete SAG-003 role/projection contract fixture."""

    role_ids = (
        "mechanical-evidence-worker",
        "reconciliation-worker",
        "semantic-governance-analyst",
        "evidence-report-synthesizer",
        "fixed-head-independent-auditor",
    )

    def __init__(self) -> None:
        self._temporary = WorkspaceTemporaryDirectory("sag003-role-projection")
        self.root = self._temporary.path
        self._write_contract()

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
        path = self.path(relative)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(yaml.safe_dump(value, sort_keys=False), encoding="utf-8")

    def validate(self) -> tuple[int, list[str]]:
        errors: list[str] = []
        count = VALIDATOR.validate_sag003_provider_role_projection_contract(
            errors, root=self.root
        )
        return count, errors

    def _role_path(self, role_id: str) -> str:
        return f".ai/assets/sub-agent-role-prompts/{role_id}/sub-agent.yaml"

    def _profile_name(self, role_id: str) -> str:
        return (
            "bounded-routine-worker"
            if role_id == "mechanical-evidence-worker"
            else role_id
        )

    def _profile_path(self, role_id: str) -> str:
        return f".codex/agents/{self._profile_name(role_id)}.toml"

    def _write_contract(self) -> None:
        execution_contract = self.path(".ai/assets/shared/ROLE-EXECUTION-CONTRACT.md")
        execution_contract.parent.mkdir(parents=True, exist_ok=True)
        execution_contract.write_text("# fixture\n", encoding="utf-8")
        for schema in (
            ".ai/assets/shared/provider-neutral-capability-registry.schema.yaml",
            ".ai/assets/shared/provider-projection-registry.schema.yaml",
        ):
            self.write_yaml(schema, {"type": "object"})

        role_bindings = []
        capabilities = []
        profiles = []
        for role_id in self.role_ids:
            role_path = self._role_path(role_id)
            self.write_yaml(
                role_path,
                {
                    "asset_id": role_id,
                    "status": "active",
                    "wrapper_targets": [],
                    "adapter_metadata": {},
                },
            )
            role_bindings.append(
                {
                    "role_path": role_path,
                    "role_asset_id": role_id,
                    "expected_role_status": "active",
                    "binding_kind": "conditional",
                    "applicability": f"The upgrader selects {role_id} for its bounded stage.",
                    "load_obligation": "mandatory-when-applicable",
                }
            )
            capabilities.append(
                {
                    "capability_id": role_id,
                    "role_path": role_path,
                    "role_asset_id": role_id,
                    "capability_tags": ["provider-neutral", "bounded"],
                    "default_mutation_boundary": "read-only",
                    "deterministic_authority": {
                        "required": True,
                        "surfaces": ["repository-tracked-evidence"],
                        "agent_boundary": "return control to the named integration owner",
                    },
                    "execution_contract": ".ai/assets/shared/ROLE-EXECUTION-CONTRACT.md",
                }
            )
            profile_path = self._profile_path(role_id)
            agent = self.path(profile_path)
            agent.parent.mkdir(parents=True, exist_ok=True)
            agent.write_text(
                f'name = "{self._profile_name(role_id)}"\n'
                f'description = "Static projection for {role_id}."\n'
                'model = "gpt-5.6-terra"\n'
                'model_reasoning_effort = "high"\n'
                'sandbox_mode = "read-only"\n'
                'developer_instructions = """\n'
                f'Read `{role_path}` before acting.\n'
                '"""\n',
                encoding="utf-8",
            )
            profiles.append(
                {
                    "role_asset_id": role_id,
                    "profile_path": profile_path,
                    "profile_name": self._profile_name(role_id),
                    "model": "gpt-5.6-terra",
                    "model_reasoning_effort": "high",
                    "sandbox_mode": "read-only",
                }
            )

        self.write_yaml(
            ".ai/assets/skills/ai-context-upgrader/skill.yaml",
            {
                "asset_id": "ai-context-upgrader",
                "status": "active",
                "role_bindings": role_bindings,
            },
        )
        self.write_yaml(
            ".ai/assets/shared/provider-neutral-capability-registry.yaml",
            {
                "schema_version": "1.0",
                "registry_id": "provider-neutral-capability-registry",
                "source_of_truth": "canonical",
                "capabilities": capabilities,
            },
        )
        self.write_yaml(
            ".ai/assets/shared/provider-projection-registry.yaml",
            {
                "schema_version": "1.0",
                "registry_id": "provider-projection-registry",
                "source_of_truth": "canonical",
                "canonical_contract": {
                    "availability": "canonical-contract-available",
                    "registry_path": ".ai/assets/shared/provider-neutral-capability-registry.yaml",
                    "role_asset_ids": list(self.role_ids),
                },
                "provider_projections": {
                    "codex": {
                        "configuration_state": "codex-runtime-configured",
                        "profiles": profiles,
                    },
                    "claude": {
                        "configuration_state": "claude-runtime-deferred",
                        "profiles": [],
                        "deferred_reason": "No provider-native projection is selected.",
                    },
                    "copilot": {
                        "configuration_state": "copilot-runtime-deferred",
                        "profiles": [],
                        "deferred_reason": "No provider-native projection is selected.",
                    },
                },
                "current_session": {
                    "availability": "unknown",
                    "invocation_evidence": "not-claimed",
                },
                "package_projection": {
                    "configured_provider": "codex",
                    "profile_paths": [profile["profile_path"] for profile in profiles],
                    "deferred_provider_runtime_paths": [],
                },
            },
        )
        upgrader_bindings = []
        for role_id in self.role_ids:
            guard = ["Select this bounded role only when applicable."]
            if role_id == "fixed-head-independent-auditor":
                guard = [
                    "Use only an explicit terminal/high-risk gate.",
                    "Reject routine tasks and profile presence alone.",
                ]
            upgrader_bindings.append(
                {
                    "role_asset_id": role_id,
                    "role_path": self._role_path(role_id),
                    "recommendation": "recommended",
                    "stage": ["bounded-upgrade-stage"],
                    "inputs": ["bounded input"],
                    "outputs": ["bounded output"],
                    "mutation_boundary": "read-only",
                    "concurrency": {
                        "maximum_parallel_instances": 1,
                        "disjoint_scope_required": True,
                    },
                    "stop_and_escalation": ["return control when scope is unclear"],
                    "direct_sequential_fallback": {
                        "allowed": True,
                        "same_contract_required": True,
                    },
                    "selection_guard": guard,
                }
            )
        self.write_yaml(
            ".ai/assets/skills/ai-context-upgrader/references/role-execution-bindings.yaml",
            {
                "schema_version": "1.0",
                "binding_manifest_id": "ai-context-upgrader-role-execution-bindings",
                "owning_skill": "ai-context-upgrader",
                "role_binding_authority": "skill.yaml.role_bindings",
                "execution_contract": ".ai/assets/shared/ROLE-EXECUTION-CONTRACT.md",
                "role_bindings": upgrader_bindings,
            },
        )


class ProviderRoleProjectionContractTests(unittest.TestCase):
    def assert_error(self, errors: list[str], fragment: str) -> None:
        self.assertTrue(any(fragment in error for error in errors), errors)

    def test_gwt_001_given_complete_provider_neutral_contract_when_validated_then_passes(self) -> None:
        fixture = ProviderRoleProjectionFixture()
        try:
            count, errors = fixture.validate()
            self.assertEqual([], errors)
            self.assertEqual(5, count)
        finally:
            fixture.close()

    def test_gwt_002_given_provider_field_in_canonical_registry_when_validated_then_fails_closed(self) -> None:
        fixture = ProviderRoleProjectionFixture()
        try:
            registry = fixture.read_yaml(".ai/assets/shared/provider-neutral-capability-registry.yaml")
            registry["capabilities"][0]["model"] = "gpt-5.6-terra"
            fixture.write_yaml(".ai/assets/shared/provider-neutral-capability-registry.yaml", registry)
            _, errors = fixture.validate()
            self.assert_error(errors, "provider/runtime field leaks")
        finally:
            fixture.close()

    def test_gwt_003_given_duplicate_upgrader_role_binding_when_validated_then_fails_closed(self) -> None:
        fixture = ProviderRoleProjectionFixture()
        try:
            skill = fixture.read_yaml(".ai/assets/skills/ai-context-upgrader/skill.yaml")
            skill["role_bindings"].append(skill["role_bindings"][0].copy())
            fixture.write_yaml(".ai/assets/skills/ai-context-upgrader/skill.yaml", skill)
            _, errors = fixture.validate()
            self.assert_error(errors, "ai-context-upgrader must have exactly one active canonical role_binding")
        finally:
            fixture.close()

    def test_gwt_004_given_static_runtime_or_invocation_claims_when_validated_then_fails_closed(self) -> None:
        fixture = ProviderRoleProjectionFixture()
        try:
            registry = fixture.read_yaml(".ai/assets/shared/provider-projection-registry.yaml")
            registry["provider_projections"]["codex"]["configuration_state"] = "runtime-enabled"
            registry["provider_projections"]["claude"]["configuration_state"] = "claude-runtime-unsupported"
            registry["current_session"] = {
                "availability": "available",
                "invocation_evidence": "invoked",
            }
            fixture.write_yaml(".ai/assets/shared/provider-projection-registry.yaml", registry)
            _, errors = fixture.validate()
            self.assert_error(errors, "statically configured")
            self.assert_error(errors, "runtime-deferred")
            self.assert_error(errors, "current_session must remain unknown")
            self.assert_error(errors, "static configuration cannot claim")
        finally:
            fixture.close()

    def test_gwt_005_given_unknown_codex_toml_field_when_validated_then_repository_contract_fails(self) -> None:
        fixture = ProviderRoleProjectionFixture()
        try:
            role_id = fixture.role_ids[0]
            profile = fixture.path(fixture._profile_path(role_id))
            profile.write_text(
                profile.read_text(encoding="utf-8") + "runtime_enabled = true\n",
                encoding="utf-8",
            )
            _, errors = fixture.validate()
            self.assert_error(errors, "unsupported Codex profile fields")
        finally:
            fixture.close()

    def test_gwt_006_given_terminal_auditor_selected_by_routine_profile_presence_when_validated_then_fails(self) -> None:
        fixture = ProviderRoleProjectionFixture()
        try:
            bindings = fixture.read_yaml(
                ".ai/assets/skills/ai-context-upgrader/references/role-execution-bindings.yaml"
            )
            auditor = next(
                item
                for item in bindings["role_bindings"]
                if item["role_asset_id"] == "fixed-head-independent-auditor"
            )
            auditor["selection_guard"] = ["Select for routine task profile presence."]
            fixture.write_yaml(
                ".ai/assets/skills/ai-context-upgrader/references/role-execution-bindings.yaml",
                bindings,
            )
            _, errors = fixture.validate()
            self.assert_error(errors, "terminal/high-risk gates")
        finally:
            fixture.close()

    def test_gwt_007_given_write_capable_projection_or_optional_deterministic_authority_when_validated_then_fails(self) -> None:
        fixture = ProviderRoleProjectionFixture()
        try:
            registry = fixture.read_yaml(
                ".ai/assets/shared/provider-projection-registry.yaml"
            )
            registry["provider_projections"]["codex"]["profiles"][0][
                "sandbox_mode"
            ] = "workspace-write"
            fixture.write_yaml(
                ".ai/assets/shared/provider-projection-registry.yaml", registry
            )
            profile = fixture.path(fixture._profile_path(fixture.role_ids[0]))
            profile.write_text(
                profile.read_text(encoding="utf-8").replace(
                    'sandbox_mode = "read-only"',
                    'sandbox_mode = "workspace-write"',
                ),
                encoding="utf-8",
            )
            capabilities = fixture.read_yaml(
                ".ai/assets/shared/provider-neutral-capability-registry.yaml"
            )
            capabilities["capabilities"][0]["deterministic_authority"][
                "required"
            ] = False
            fixture.write_yaml(
                ".ai/assets/shared/provider-neutral-capability-registry.yaml",
                capabilities,
            )
            _, errors = fixture.validate()
            self.assert_error(errors, "sandbox_mode must remain read-only")
            self.assert_error(errors, "deterministic_authority.required must be true")
        finally:
            fixture.close()

    def test_gwt_008_given_provider_model_field_in_role_manifest_when_validated_then_fails(self) -> None:
        fixture = ProviderRoleProjectionFixture()
        try:
            role_path = fixture._role_path(fixture.role_ids[0])
            role = fixture.read_yaml(role_path)
            role["model"] = "gpt-5.6-terra"
            role["model_slug"] = "unverified-model"
            role["current_session_availability"] = "available"
            role["invocation_evidence"] = "claimed"
            fixture.write_yaml(role_path, role)
            _, errors = fixture.validate()
            self.assert_error(errors, "provider/runtime field leaks")
        finally:
            fixture.close()


if __name__ == "__main__":
    unittest.main()
