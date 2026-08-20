#!/usr/bin/env python3
"""GWT contracts for the optional Engineering Guardrails provider binding."""

from __future__ import annotations

from collections.abc import Callable
from copy import deepcopy
import hashlib
import json
import unittest
from pathlib import Path

import yaml


REPO_ROOT = Path(__file__).resolve().parents[3]
RECIPE_ROOT = REPO_ROOT / (
    ".ai/assets/tech-stacks/dotnet-backend/tooling/"
    "on-demand-mechanical-validation"
)
CONTRACT_PATH = RECIPE_ROOT / "provider-contract.yaml"
SCHEMA_PATH = RECIPE_ROOT / "provider-contract.schema.yaml"
SELECTION_TEMPLATE_PATH = RECIPE_ROOT / "templates/provider-selection.template.yaml"
ANALYZER_TEMPLATE_PATH = RECIPE_ROOT / "templates/minimal-diagnostic-analyzer.cs.template"
ANALYZER_TEST_TEMPLATE_PATH = (
    RECIPE_ROOT / "templates/minimal-diagnostic-analyzer-test.cs.template"
)
CODE_FIX_TEMPLATE_PATH = RECIPE_ROOT / "templates/code-fix-decision.md"
README_PATH = RECIPE_ROOT / "README.md"
MANIFEST_PATH = RECIPE_ROOT / "recipe-manifest.yaml"
RECIPE_PATH = RECIPE_ROOT / "recipes/analyzer-project.md"
CHECK_ALL_PATH = REPO_ROOT / ".ai/scripts/check-all.sh"
SHELL_ASSETS_PATH = REPO_ROOT / ".ai/scripts/shell-assets.yaml"


def load_yaml(path: Path) -> dict:
    loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise AssertionError(f"{path.relative_to(REPO_ROOT)} must contain a mapping")
    return loaded


MISSING = object()

# Issue #205 accepted baseline v1. These values deliberately live in executable
# test code rather than in the mutable YAML inputs. A legitimate future baseline
# requires an explicit owner decision plus a new ID/version and every affected
# digest constant and schema declaration updated together.
ISSUE_205_BASELINE_ID = "issue-205-engineering-guardrails-provider-contract-v1"
ISSUE_205_BASELINE_VERSION = 1
ISSUE_205_BASELINE_ISSUE_REFERENCE = {
    "number": 205,
    "url": "https://github.com/YuChia-Wei/ai-collaboration-framework/issues/205",
}
ISSUE_205_BASELINE_CHANGE_CONTROL = (
    "An explicit owner decision must authorize a baseline change. The owner must "
    "assign a new baseline_id and baseline_version and update every affected "
    "Issue #205 accepted digest constant and schema declaration together."
)
ISSUE_205_BASELINE_SCHEMA_DIGEST_CONTROL = (
    "The accepted schema SHA-256 is an Issue #205 test-helper constant rather "
    "than a schema field, so the schema digest cannot self-reference."
)
ISSUE_205_BASELINE_CANONICALIZATION = {
    "input": "YAML-loaded document data",
    "serialization": "JSON",
    "json_options": {
        "sort_keys": True,
        "separators": [",", ":"],
        "ensure_ascii": False,
        "allow_nan": False,
    },
    "array_order": "preserved",
    "encoding": "UTF-8",
    "digest_algorithm": "sha256",
}
ISSUE_205_BASELINE_PROVIDER_CONTRACT_SHA256 = (
    "69c020829aed4371f2b3e81ba41f2c95932623a6467b36cba7aa5fdcf593bee7"
)
ISSUE_205_BASELINE_PROVIDER_SELECTION_TEMPLATE_SHA256 = (
    "9dcf04ee3137c6e2f330e7b4b1138c50a5881c153a9912582f192cbb419d9d29"
)
# This value is not declared in the schema: including it there would make the
# schema's canonical digest self-referential.
ISSUE_205_BASELINE_SCHEMA_SHA256 = (
    "e98afb302ae8194151d5584634ade7fb282fbf31ad0f110bab2b5cedc6ba47db"
)
ISSUE_205_BASELINE_AUTHORITY = {
    "baseline_id": ISSUE_205_BASELINE_ID,
    "baseline_version": ISSUE_205_BASELINE_VERSION,
    "issue_reference": ISSUE_205_BASELINE_ISSUE_REFERENCE,
    "change_control": ISSUE_205_BASELINE_CHANGE_CONTROL,
    "schema_digest_control": ISSUE_205_BASELINE_SCHEMA_DIGEST_CONTROL,
    "canonicalization": ISSUE_205_BASELINE_CANONICALIZATION,
    "artifact_digests": {
        "provider_contract_sha256": ISSUE_205_BASELINE_PROVIDER_CONTRACT_SHA256,
        "provider_selection_template_sha256": (
            ISSUE_205_BASELINE_PROVIDER_SELECTION_TEMPLATE_SHA256
        ),
    },
}

SCHEMA_ROOT_FIELDS = (
    "schema_version",
    "schema_id",
    "applies_to",
    "baseline_authority",
    "contract",
    "capability",
    "recommendation",
    "canonical_provider_package_identity",
    "framework_delivery",
    "fallback",
    "state_semantics",
    "evidence_receipt_contracts",
    "prohibitions",
    "provider_selection_template",
    "template_prohibitions",
)
SCHEMA_SECTION_FIELDS = {
    "contract": ("required_fields", "required_literals"),
    "capability": (
        "required_fields",
        "required_literals",
        "package_identity_independent",
    ),
    "recommendation": ("required_fields", "required_literals"),
    "canonical_provider_package_identity": ("required_fields", "required_literals"),
    "framework_delivery": ("required_fields", "required_literals"),
    "fallback": ("required_fields", "required_literals"),
    "state_semantics": (
        "required_fields",
        "required_literals",
        "required_states",
        "state_requirements",
    ),
    "evidence_receipt_contracts": (
        "required_kinds",
        "required_receipt_fields",
        "digest_required_fields",
        "digest_literals",
        "receipt_requirements",
    ),
    "prohibitions": ("required_exact_values",),
    "provider_selection_template": (
        "required_fields",
        "required_literals",
        "required_null_paths",
        "required_empty_list_paths",
    ),
}
SCHEMA_LITERAL_FIELDS = {
    "contract": (
        "schema_version",
        "contract_id",
        "contract_tier",
        "technology_profile",
    ),
    "capability": (
        "id",
        "provider_binding",
        "stable_identity_requirement",
        "scope",
    ),
    "recommendation": (
        "status",
        "selection_independent",
        "default_selection_state",
        "auto_install",
        "silent_selection",
    ),
    "canonical_provider_package_identity": (
        "status",
        "nuget_id",
        "version",
        "feed",
        "publication_contract",
        "identity_evidence",
    ),
    "framework_delivery": (
        "status",
        "supplied_executable",
        "supplied_readiness_receipt",
        "supplied_compatibility_receipt",
        "supplied_execution_receipt",
        "reason",
    ),
    "fallback": ("status", "ownership", "materials"),
    "state_semantics": ("default_state",),
    "provider_selection_template": (
        "schema_version",
        "record_type",
        "template_status",
        "ownership.source",
        "ownership.after_copy",
        "capability.id",
        "capability.provider_binding",
        "recommendation.status",
        "recommendation.selection_independent",
        "selection.status",
        "provider_package_identity.status",
        "provider_package_identity.publication_contract",
        "capability_gap.status",
        "capability_gap.fallback",
        "readiness.status",
        "compatibility.status",
        "execution.status",
        "execution.required_real_receipt",
        "fallback.status",
        "fallback.analyzer_template",
        "fallback.analyzer_test_template",
        "fallback.code_fix_decision_template",
        "notes",
    ),
}
SCHEMA_APPLIES_TO = (
    "provider-contract.yaml",
    "templates/provider-selection.template.yaml",
)
SCHEMA_TEMPLATE_PROHIBITIONS = (
    ".csproj",
    ".sln",
    ".slnx",
    "global.json",
    "PackageReference",
    "dotnet command",
)


def nested_value(
    document: dict, dotted_path: str, missing: object = MISSING
) -> object:
    current: object = document
    for segment in dotted_path.split("."):
        if not isinstance(current, dict) or segment not in current:
            return missing
        current = current[segment]
    return current


def display_value(value: object) -> str:
    return repr("<missing>") if value is MISSING else repr(value)


def canonical_json_sha256(document: object) -> str:
    """Hash YAML-loaded data as canonical compact UTF-8 JSON for Issue #205."""
    serialized = json.dumps(
        document,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    )
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


def require_issue_205_baseline_digest(
    errors: list[str], artifact: str, document: object, expected: str
) -> None:
    try:
        actual = canonical_json_sha256(document)
    except (TypeError, ValueError) as error:
        errors.append(
            f"{artifact} must be canonicalizable under the Issue #205 baseline: "
            f"{error}"
        )
        return
    if actual != expected:
        errors.append(
            f"{artifact} canonical SHA-256 must equal Issue #205 accepted baseline "
            f"{expected!r}, found {actual!r}"
        )


def require_exact_value(
    errors: list[str], path: str, actual: object, expected: object
) -> None:
    if actual is MISSING:
        matches = False
    elif expected is None:
        matches = actual is None
    elif type(expected) is bool:
        matches = type(actual) is bool and actual is expected
    elif type(expected) is str:
        matches = type(actual) is str and actual == expected
    elif type(expected) is int:
        matches = type(actual) is int and actual == expected
    elif type(expected) is list:
        matches = type(actual) is list and actual == expected
    else:
        matches = actual == expected
    if not matches:
        errors.append(
            f"{path} must be {expected!r}, found {display_value(actual)}"
        )


def require_exact_keys(
    errors: list[str], path: str, actual: object, expected_keys: object
) -> dict | None:
    if not isinstance(actual, dict):
        errors.append(f"{path} must be a mapping, found {display_value(actual)}")
        return None
    if not isinstance(expected_keys, (list, tuple)):
        errors.append(f"{path} schema field list must be a sequence")
        return None
    expected = set(expected_keys)
    actual_keys = set(actual)
    for key in sorted(expected - actual_keys):
        errors.append(f"{path} is missing required field: {key}")
    for key in sorted(actual_keys - expected):
        errors.append(f"{path} has unexpected field: {key}")
    return actual


def require_unique_string_list(
    errors: list[str], path: str, actual: object
) -> list[str] | None:
    if type(actual) is not list:
        errors.append(f"{path} must be a list of strings, found {display_value(actual)}")
        return None
    if any(type(item) is not str for item in actual):
        errors.append(f"{path} must contain only strings")
        return None
    if len(actual) != len(set(actual)):
        errors.append(f"{path} must not contain duplicates")
    return actual


def require_exact_string_list(
    errors: list[str], path: str, actual: object, expected: object
) -> None:
    values = require_unique_string_list(errors, path, actual)
    if values is None:
        return
    if values != expected:
        errors.append(
            f"{path} must exactly equal {expected!r}, found {values!r}"
        )


def require_exact_section(
    errors: list[str], path: str, actual: object, rules: dict
) -> dict | None:
    mapping = require_exact_keys(
        errors, path, actual, rules["required_fields"]
    )
    if mapping is None:
        return None
    for field, expected in rules["required_literals"].items():
        require_exact_value(
            errors, f"{path}.{field}", mapping.get(field, MISSING), expected
        )
    return mapping


def dotted_tree(requirements: dict[str, object]) -> dict[str, object]:
    tree: dict[str, object] = {}
    for dotted_path, expected in requirements.items():
        segments = dotted_path.split(".")
        current = tree
        for segment in segments[:-1]:
            current = current.setdefault(segment, {})
        current[segments[-1]] = expected
    return tree


def require_exact_tree(
    errors: list[str], path: str, actual: object, expected: object
) -> None:
    if isinstance(expected, dict):
        mapping = require_exact_keys(errors, path, actual, list(expected))
        if mapping is None:
            return
        for field, nested_expected in expected.items():
            require_exact_tree(
                errors,
                f"{path}.{field}",
                mapping.get(field, MISSING),
                nested_expected,
            )
        return
    require_exact_value(errors, path, actual, expected)


def schema_errors(schema: dict) -> list[str]:
    """Reject a schema that omits, adds, or weakens a shipped invariant."""
    errors: list[str] = []
    schema_mapping = require_exact_keys(
        errors, "schema", schema, SCHEMA_ROOT_FIELDS
    )
    if schema_mapping is None:
        return errors

    require_exact_value(
        errors, "schema.schema_version", schema.get("schema_version", MISSING), "1.0"
    )
    require_exact_value(
        errors,
        "schema.schema_id",
        schema.get("schema_id", MISSING),
        "dotnet-engineering-guardrails-provider-contract-schema",
    )
    require_exact_string_list(
        errors, "schema.applies_to", schema.get("applies_to", MISSING), list(SCHEMA_APPLIES_TO)
    )
    require_exact_tree(
        errors,
        "schema.baseline_authority",
        schema.get("baseline_authority", MISSING),
        ISSUE_205_BASELINE_AUTHORITY,
    )
    require_issue_205_baseline_digest(
        errors,
        "schema",
        schema,
        ISSUE_205_BASELINE_SCHEMA_SHA256,
    )
    require_exact_string_list(
        errors,
        "schema.template_prohibitions",
        schema.get("template_prohibitions", MISSING),
        list(SCHEMA_TEMPLATE_PROHIBITIONS),
    )

    sections: dict[str, dict] = {}
    for name, expected_fields in SCHEMA_SECTION_FIELDS.items():
        section = require_exact_keys(
            errors, f"schema.{name}", schema.get(name, MISSING), expected_fields
        )
        if section is not None:
            sections[name] = section
    if len(sections) != len(SCHEMA_SECTION_FIELDS):
        return errors

    for name, expected_fields in SCHEMA_LITERAL_FIELDS.items():
        require_exact_keys(
            errors,
            f"schema.{name}.required_literals",
            sections[name].get("required_literals", MISSING),
            expected_fields,
        )

    for name in (
        "contract",
        "capability",
        "recommendation",
        "canonical_provider_package_identity",
        "framework_delivery",
        "fallback",
        "state_semantics",
        "provider_selection_template",
    ):
        require_unique_string_list(
            errors,
            f"schema.{name}.required_fields",
            sections[name].get("required_fields", MISSING),
        )

    state_rules = sections["state_semantics"]
    required_states = require_unique_string_list(
        errors,
        "schema.state_semantics.required_states",
        state_rules.get("required_states", MISSING),
    )
    if required_states is not None:
        require_exact_keys(
            errors,
            "schema.state_semantics.state_requirements",
            state_rules.get("state_requirements", MISSING),
            required_states,
        )

    receipt_rules = sections["evidence_receipt_contracts"]
    required_kinds = require_unique_string_list(
        errors,
        "schema.evidence_receipt_contracts.required_kinds",
        receipt_rules.get("required_kinds", MISSING),
    )
    for field in ("required_receipt_fields", "digest_required_fields"):
        require_unique_string_list(
            errors,
            f"schema.evidence_receipt_contracts.{field}",
            receipt_rules.get(field, MISSING),
        )
    if required_kinds is not None:
        requirements = require_exact_keys(
            errors,
            "schema.evidence_receipt_contracts.receipt_requirements",
            receipt_rules.get("receipt_requirements", MISSING),
            required_kinds,
        )
        if requirements is not None:
            for kind in required_kinds:
                require_exact_keys(
                    errors,
                    f"schema.evidence_receipt_contracts.receipt_requirements.{kind}",
                    requirements.get(kind, MISSING),
                    ("receipt_type", "required_fields"),
                )

    template_rules = sections["provider_selection_template"]
    for field in ("required_null_paths", "required_empty_list_paths"):
        require_unique_string_list(
            errors,
            f"schema.provider_selection_template.{field}",
            template_rules.get(field, MISSING),
        )

    if (
        type(sections["capability"].get("package_identity_independent")) is not bool
        or sections["capability"]["package_identity_independent"] is not True
    ):
        errors.append(
            "schema.capability.package_identity_independent must be strictly True"
        )
    return errors


def selection_template_errors(template: dict, schema: dict) -> list[str]:
    errors: list[str] = []
    require_issue_205_baseline_digest(
        errors,
        "provider_selection_template",
        template,
        ISSUE_205_BASELINE_PROVIDER_SELECTION_TEMPLATE_SHA256,
    )
    rules = schema["provider_selection_template"]
    require_exact_keys(
        errors, "provider_selection_template", template, rules["required_fields"]
    )

    expected_values = dict(rules["required_literals"])
    for path in rules["required_null_paths"]:
        expected_values[path] = None
    for path in rules["required_empty_list_paths"]:
        expected_values[path] = []
    require_exact_tree(
        errors,
        "provider_selection_template",
        template,
        dotted_tree(expected_values),
    )
    return errors


def contract_errors(
    contract: dict, schema: dict, selection_template: dict | None = None
) -> list[str]:
    """Validate all shipped provider claims without simulating a provider."""
    errors = schema_errors(schema)
    if errors:
        return errors
    if not isinstance(contract, dict):
        return [f"contract must be a mapping, found {display_value(contract)}"]
    require_issue_205_baseline_digest(
        errors,
        "contract",
        contract,
        ISSUE_205_BASELINE_PROVIDER_CONTRACT_SHA256,
    )

    contract_rules = schema["contract"]
    require_exact_keys(errors, "contract", contract, contract_rules["required_fields"])
    for field, expected in contract_rules["required_literals"].items():
        require_exact_value(
            errors, f"contract.{field}", contract.get(field, MISSING), expected
        )

    capability_rules = schema["capability"]
    capability = require_exact_section(
        errors, "capability", contract.get("capability", MISSING), capability_rules
    )
    if capability is not None and capability_rules["package_identity_independent"]:
        if any(
            term in str(capability.get("id", "")).lower()
            for term in ("nuget", "package", "version", "feed")
        ):
            errors.append("capability.id must not depend on provider package identity")

    require_exact_section(
        errors,
        "recommendation",
        contract.get("recommendation", MISSING),
        schema["recommendation"],
    )
    require_exact_section(
        errors,
        "provider_package_identity",
        contract.get("provider_package_identity", MISSING),
        schema["canonical_provider_package_identity"],
    )
    require_exact_section(
        errors,
        "framework_delivery",
        contract.get("framework_delivery", MISSING),
        schema["framework_delivery"],
    )
    require_exact_section(
        errors,
        "fallback",
        contract.get("fallback", MISSING),
        schema["fallback"],
    )

    state_rules = schema["state_semantics"]
    state_semantics = require_exact_section(
        errors,
        "state_semantics",
        contract.get("state_semantics", MISSING),
        state_rules,
    )
    if state_semantics is not None:
        states = require_exact_keys(
            errors,
            "state_semantics.states",
            state_semantics.get("states", MISSING),
            state_rules["required_states"],
        )
        if states is not None:
            for state in state_rules["required_states"]:
                require_exact_tree(
                    errors,
                    state,
                    states.get(state, MISSING),
                    dotted_tree(state_rules["state_requirements"][state]),
                )

    receipt_rules = schema["evidence_receipt_contracts"]
    receipt_contracts = require_exact_keys(
        errors,
        "evidence_receipt_contracts",
        contract.get("evidence_receipt_contracts", MISSING),
        receipt_rules["required_kinds"],
    )
    receipt_types: list[str] = []
    if receipt_contracts is not None:
        for kind in receipt_rules["required_kinds"]:
            record = require_exact_keys(
                errors,
                kind,
                receipt_contracts.get(kind, MISSING),
                receipt_rules["required_receipt_fields"],
            )
            if record is None:
                continue
            requirements = receipt_rules["receipt_requirements"][kind]
            receipt_type = record.get("receipt_type", MISSING)
            require_exact_value(
                errors,
                f"{kind}.receipt_type",
                receipt_type,
                requirements["receipt_type"],
            )
            if type(receipt_type) is str:
                receipt_types.append(receipt_type)
            require_exact_string_list(
                errors,
                f"{kind}.required_fields",
                record.get("required_fields", MISSING),
                requirements["required_fields"],
            )
            digest = require_exact_keys(
                errors,
                f"{kind}.digest",
                record.get("digest", MISSING),
                receipt_rules["digest_required_fields"],
            )
            if digest is not None:
                for field, expected in receipt_rules["digest_literals"].items():
                    require_exact_value(
                        errors,
                        f"{kind}.digest.{field}",
                        digest.get(field, MISSING),
                        expected,
                    )
    if len(receipt_types) != len(set(receipt_types)):
        errors.append("readiness, compatibility, and execution receipt types must differ")

    require_exact_string_list(
        errors,
        "prohibitions",
        contract.get("prohibitions", MISSING),
        schema["prohibitions"]["required_exact_values"],
    )

    if selection_template is not None:
        errors.extend(selection_template_errors(selection_template, schema))
    return errors


CoordinatedMutation = Callable[[dict, dict, dict], None]


def rewrite_mutable_authority_digests_for_attack(
    schema: dict, contract: dict, template: dict
) -> None:
    """Simulate an attacker keeping mutable schema digest declarations in sync."""
    schema["baseline_authority"]["artifact_digests"] = {
        "provider_contract_sha256": canonical_json_sha256(contract),
        "provider_selection_template_sha256": canonical_json_sha256(template),
    }


def mutate_coordinated_capability_id(
    schema: dict, contract: dict, template: dict
) -> None:
    value = "dotnet.provider-specific-validation"
    schema["capability"]["required_literals"]["id"] = value
    schema["provider_selection_template"]["required_literals"]["capability.id"] = value
    contract["capability"]["id"] = value
    template["capability"]["id"] = value


def mutate_coordinated_capability_binding(
    schema: dict, contract: dict, template: dict
) -> None:
    value = "provider-package-specific"
    schema["capability"]["required_literals"]["provider_binding"] = value
    schema["provider_selection_template"]["required_literals"][
        "capability.provider_binding"
    ] = value
    contract["capability"]["provider_binding"] = value
    template["capability"]["provider_binding"] = value


def mutate_coordinated_boolean(
    schema: dict, contract: dict, template: dict
) -> None:
    schema["recommendation"]["required_literals"]["selection_independent"] = False
    schema["provider_selection_template"]["required_literals"][
        "recommendation.selection_independent"
    ] = False
    contract["recommendation"]["selection_independent"] = False
    template["recommendation"]["selection_independent"] = False


def mutate_coordinated_unavailable_flag(
    schema: dict, contract: dict, template: dict
) -> None:
    del template  # The unavailable delivery claim exists only in the contract.
    schema["framework_delivery"]["required_literals"]["supplied_executable"] = True
    contract["framework_delivery"]["supplied_executable"] = True


def mutate_coordinated_receipt_field(
    schema: dict, contract: dict, template: dict
) -> None:
    del template
    schema["evidence_receipt_contracts"]["receipt_requirements"]["execution"][
        "required_fields"
    ].remove("command")
    contract["evidence_receipt_contracts"]["execution"]["required_fields"].remove(
        "command"
    )


def mutate_coordinated_receipt_type(
    schema: dict, contract: dict, template: dict
) -> None:
    del template
    value = "engineering-guardrails-provider-runtime-receipt"
    schema["evidence_receipt_contracts"]["receipt_requirements"]["execution"][
        "receipt_type"
    ] = value
    contract["evidence_receipt_contracts"]["execution"]["receipt_type"] = value


def mutate_coordinated_receipt_kind(
    schema: dict, contract: dict, template: dict
) -> None:
    del template
    kind = "runtime"
    receipt_type = "engineering-guardrails-provider-runtime-receipt"
    required_fields = list(
        contract["evidence_receipt_contracts"]["execution"]["required_fields"]
    )
    schema["evidence_receipt_contracts"]["required_kinds"].append(kind)
    schema["evidence_receipt_contracts"]["receipt_requirements"][kind] = {
        "receipt_type": receipt_type,
        "required_fields": required_fields,
    }
    contract["evidence_receipt_contracts"][kind] = {
        "receipt_type": receipt_type,
        "digest": deepcopy(contract["evidence_receipt_contracts"]["execution"]["digest"]),
        "required_fields": required_fields,
    }


def mutate_coordinated_state_set(
    schema: dict, contract: dict, template: dict
) -> None:
    del template
    state = "selected-ready"
    schema["state_semantics"]["required_states"].append(state)
    schema["state_semantics"]["state_requirements"][state] = {
        "readiness.status": "proven"
    }
    contract["state_semantics"]["states"][state] = {
        "readiness": {"status": "proven"}
    }


def mutate_coordinated_state_requirement(
    schema: dict, contract: dict, template: dict
) -> None:
    del template
    schema["state_semantics"]["state_requirements"]["not-selected"][
        "selection.auto_install"
    ] = "allowed"
    contract["state_semantics"]["states"]["not-selected"]["selection"][
        "auto_install"
    ] = "allowed"


def mutate_coordinated_prohibition(
    schema: dict, contract: dict, template: dict
) -> None:
    del template
    schema["prohibitions"]["required_exact_values"].pop()
    contract["prohibitions"].pop()


def mutate_coordinated_fallback(
    schema: dict, contract: dict, template: dict
) -> None:
    del template
    value = "framework-owned"
    schema["fallback"]["required_literals"]["ownership"] = value
    contract["fallback"]["ownership"] = value


def mutate_coordinated_template_selection(
    schema: dict, contract: dict, template: dict
) -> None:
    del contract
    schema["provider_selection_template"]["required_literals"]["selection.status"] = (
        "selected"
    )
    template["selection"]["status"] = "selected"


def mutate_coordinated_template_null_receipt(
    schema: dict, contract: dict, template: dict
) -> None:
    del contract
    schema["provider_selection_template"]["required_null_paths"].remove(
        "readiness.receipt"
    )
    del template["readiness"]["receipt"]


def mutate_coordinated_added_contract_claim(
    schema: dict, contract: dict, template: dict
) -> None:
    del template
    claim = "unproven_execution_claim"
    schema["contract"]["required_fields"].append(claim)
    contract[claim] = "provider-evidence-not-required"


class EngineeringGuardrailsProviderContractGwtTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = load_yaml(CONTRACT_PATH)
        cls.schema = load_yaml(SCHEMA_PATH)
        cls.selection_template = load_yaml(SELECTION_TEMPLATE_PATH)

    def errors_for(
        self,
        contract: dict | None = None,
        template: dict | None = None,
        schema: dict | None = None,
    ) -> list[str]:
        return contract_errors(
            self.contract if contract is None else contract,
            self.schema if schema is None else schema,
            self.selection_template if template is None else template,
        )

    def assert_validation_error(
        self,
        expected_fragment: str,
        contract: dict | None = None,
        template: dict | None = None,
        schema: dict | None = None,
    ) -> None:
        errors = self.errors_for(contract=contract, template=template, schema=schema)
        self.assertTrue(
            any(expected_fragment in error for error in errors),
            f"Expected {expected_fragment!r}; errors were: {errors}",
        )

    def assert_coordinated_mutation_rejected(
        self, category: str, mutation: CoordinatedMutation
    ) -> None:
        """Show an attacker cannot make schema plus artifacts drift together."""
        schema = deepcopy(self.schema)
        contract = deepcopy(self.contract)
        template = deepcopy(self.selection_template)
        mutation(schema, contract, template)
        rewrite_mutable_authority_digests_for_attack(schema, contract, template)

        errors = self.errors_for(
            schema=schema,
            contract=contract,
            template=template,
        )
        self.assertTrue(
            any(
                "schema canonical SHA-256 must equal Issue #205 accepted baseline"
                in error
                for error in errors
            ),
            f"{category} coordinated mutation escaped the immutable baseline: {errors}",
        )

    def test_gwt_001_given_the_shipped_contract_when_checked_then_the_unavailable_provider_states_are_complete(self) -> None:
        self.assertEqual([], self.errors_for())

    def test_gwt_002_given_a_mutated_unavailable_contract_when_checked_then_it_fails_closed(self) -> None:
        with self.subTest("invented provider package identity"):
            candidate = deepcopy(self.contract)
            candidate["provider_package_identity"]["nuget_id"] = "Invented.Provider"
            self.assert_validation_error(
                "provider_package_identity.nuget_id must be None",
                contract=candidate,
            )

        with self.subTest("framework delivery cannot claim a real provider"):
            candidate = deepcopy(self.contract)
            candidate["framework_delivery"]["status"] = "real-provider-ready"
            self.assert_validation_error(
                "framework_delivery.status must be 'real-provider-unavailable'",
                contract=candidate,
            )

        for field in (
            "supplied_executable",
            "supplied_readiness_receipt",
            "supplied_compatibility_receipt",
            "supplied_execution_receipt",
        ):
            with self.subTest(f"framework delivery cannot mark {field} supplied"):
                candidate = deepcopy(self.contract)
                candidate["framework_delivery"][field] = True
                self.assert_validation_error(
                    f"framework_delivery.{field} must be False, found True",
                    contract=candidate,
                )

        with self.subTest("framework delivery values must be booleans"):
            candidate = deepcopy(self.contract)
            candidate["framework_delivery"]["supplied_executable"] = 0
            self.assert_validation_error(
                "framework_delivery.supplied_executable must be False, found 0",
                contract=candidate,
            )

        for state in (
            "declined",
            "not-selected",
            "selected-unavailable",
            "synthetic-readiness-proven",
        ):
            with self.subTest(f"{state} cannot carry an execution receipt"):
                candidate = deepcopy(self.contract)
                candidate["state_semantics"]["states"][state]["execution"][
                    "receipt"
                ] = {"receipt_type": "invented"}
                self.assert_validation_error(
                    f"{state}.execution.receipt must be None",
                    contract=candidate,
                )

            with self.subTest(f"{state} must explicitly record a null receipt"):
                candidate = deepcopy(self.contract)
                del candidate["state_semantics"]["states"][state]["execution"][
                    "receipt"
                ]
                self.assert_validation_error(
                    f"{state}.execution.receipt must be None, found '<missing>'",
                    contract=candidate,
                )

        with self.subTest("canonical prohibitions cannot be removed"):
            candidate = deepcopy(self.contract)
            candidate["prohibitions"] = []
            self.assert_validation_error(
                "prohibitions must exactly equal",
                contract=candidate,
            )

        with self.subTest("synthetic readiness cannot become real execution"):
            candidate = deepcopy(self.contract)
            candidate["state_semantics"]["states"]["synthetic-readiness-proven"][
                "execution"
            ]["status"] = "proven"
            self.assert_validation_error(
                "synthetic-readiness-proven.execution.status",
                contract=candidate,
            )

    def test_gwt_003_given_the_selection_template_when_checked_then_it_starts_target_owned_and_not_selected(self) -> None:
        with self.subTest("stable capability identity and binding"):
            candidate = deepcopy(self.selection_template)
            candidate["capability"]["id"] = "dotnet.provider-specific-validation"
            self.assert_validation_error(
                "provider_selection_template.capability.id must be "
                "'dotnet.mechanical-validation'",
                template=candidate,
            )

            candidate = deepcopy(self.selection_template)
            candidate["capability"]["provider_binding"] = "other-provider"
            self.assert_validation_error(
                "provider_selection_template.capability.provider_binding must be "
                "'engineering-guardrails'",
                template=candidate,
            )

        with self.subTest("selection booleans are strictly typed"):
            candidate = deepcopy(self.selection_template)
            candidate["recommendation"]["selection_independent"] = 1
            self.assert_validation_error(
                "provider_selection_template.recommendation.selection_independent "
                "must be True, found 1",
                template=candidate,
            )

            candidate = deepcopy(self.selection_template)
            candidate["execution"]["required_real_receipt"] = 1
            self.assert_validation_error(
                "provider_selection_template.execution.required_real_receipt "
                "must be True, found 1",
                template=candidate,
            )

        with self.subTest("the template cannot make a selection or provider claim"):
            candidate = deepcopy(self.selection_template)
            candidate["selection"]["status"] = "selected"
            self.assert_validation_error(
                "provider_selection_template.selection.status must be "
                "'not-selected'",
                template=candidate,
            )

            candidate = deepcopy(self.selection_template)
            candidate["selection"]["target_decision"] = "selected-by-default"
            self.assert_validation_error(
                "provider_selection_template.selection.target_decision must be None",
                template=candidate,
            )

            candidate = deepcopy(self.selection_template)
            candidate["provider_package_identity"]["nuget_id"] = "Invented.Provider"
            self.assert_validation_error(
                "provider_selection_template.provider_package_identity.nuget_id "
                "must be None",
                template=candidate,
            )

        for claim_path in (
            "readiness.receipt",
            "compatibility.receipt",
            "execution.receipt",
            "evidence_receipts.readiness",
        ):
            with self.subTest(f"the template cannot claim {claim_path}"):
                candidate = deepcopy(self.selection_template)
                parent_path, field = claim_path.rsplit(".", 1)
                nested_value(candidate, parent_path)[field] = {
                    "receipt_type": "invented"
                }
                self.assert_validation_error(
                    f"provider_selection_template.{claim_path} must be None",
                    template=candidate,
                )

        with self.subTest("fallback material paths are exact"):
            candidate = deepcopy(self.selection_template)
            candidate["fallback"]["analyzer_template"] = "selected-analyzer.cs"
            self.assert_validation_error(
                "provider_selection_template.fallback.analyzer_template must be "
                "'minimal-diagnostic-analyzer.cs.template'",
                template=candidate,
            )

    def test_gwt_004_given_identity_delivery_and_fallback_claim_mutations_when_checked_then_they_fail_closed(self) -> None:
        for field in (
            "schema_version",
            "contract_id",
            "contract_tier",
            "technology_profile",
        ):
            with self.subTest(f"contract {field} is stable"):
                candidate = deepcopy(self.contract)
                candidate[field] = "mutated"
                self.assert_validation_error(
                    f"contract.{field} must be",
                    contract=candidate,
                )

        for field in ("id", "provider_binding"):
            with self.subTest(f"capability {field} is stable"):
                candidate = deepcopy(self.contract)
                candidate["capability"][field] = "provider-package-specific"
                self.assert_validation_error(
                    f"capability.{field} must be",
                    contract=candidate,
                )

        with self.subTest("the stable identity contract cannot become package-specific"):
            candidate = deepcopy(self.contract)
            candidate["capability"][
                "stable_identity_requirement"
            ] = "Use the NuGet package identity as the capability identity."
            self.assert_validation_error(
                "capability.stable_identity_requirement must be",
                contract=candidate,
            )

        with self.subTest("recommendation selection independence is a strict boolean"):
            candidate = deepcopy(self.contract)
            candidate["recommendation"]["selection_independent"] = 1
            self.assert_validation_error(
                "recommendation.selection_independent must be True, found 1",
                contract=candidate,
            )

        for field in (
            "supplied_executable",
            "supplied_readiness_receipt",
            "supplied_compatibility_receipt",
            "supplied_execution_receipt",
        ):
            with self.subTest(f"framework delivery {field} rejects integer booleans"):
                candidate = deepcopy(self.contract)
                candidate["framework_delivery"][field] = 0
                self.assert_validation_error(
                    f"framework_delivery.{field} must be False, found 0",
                    contract=candidate,
                )

        with self.subTest("package identity remains unknown and unsupported"):
            candidate = deepcopy(self.contract)
            candidate["provider_package_identity"]["publication_contract"] = "known"
            self.assert_validation_error(
                "provider_package_identity.publication_contract must be 'unknown'",
                contract=candidate,
            )

        with self.subTest("fallback ownership and material paths are exact"):
            candidate = deepcopy(self.contract)
            candidate["fallback"]["ownership"] = "framework-owned"
            self.assert_validation_error(
                "fallback.ownership must be 'target-owned-after-copy'",
                contract=candidate,
            )

            candidate = deepcopy(self.contract)
            candidate["fallback"]["materials"].append("templates/provider.cs")
            self.assert_validation_error(
                "fallback.materials must be",
                contract=candidate,
            )

        with self.subTest("the prohibition list has exact content and order"):
            candidate = deepcopy(self.contract)
            candidate["prohibitions"].reverse()
            self.assert_validation_error(
                "prohibitions must exactly equal",
                contract=candidate,
            )

        with self.subTest("the schema cannot omit the stable capability binding"):
            candidate_schema = deepcopy(self.schema)
            del candidate_schema["capability"]["required_literals"]["id"]
            self.assert_validation_error(
                "schema.capability.required_literals is missing required field: id",
                schema=candidate_schema,
            )

    def test_gwt_005_given_receipt_contract_mutations_when_checked_then_exact_types_and_fields_are_required(self) -> None:
        with self.subTest("readiness requires complete identity freshness and outcome fields"):
            candidate = deepcopy(self.contract)
            candidate["evidence_receipt_contracts"]["readiness"][
                "required_fields"
            ] = ["receipt_sha256"]
            self.assert_validation_error(
                "readiness.required_fields must exactly equal",
                contract=candidate,
            )

        for field in ("target_commit", "command"):
            with self.subTest(f"execution requires {field}"):
                candidate = deepcopy(self.contract)
                candidate["evidence_receipt_contracts"]["execution"][
                    "required_fields"
                ].remove(field)
                self.assert_validation_error(
                    "execution.required_fields must exactly equal",
                    contract=candidate,
                )

        with self.subTest("receipt kinds cannot swap receipt types"):
            candidate = deepcopy(self.contract)
            candidate["evidence_receipt_contracts"]["execution"]["receipt_type"] = (
                candidate["evidence_receipt_contracts"]["readiness"]["receipt_type"]
            )
            self.assert_validation_error(
                "execution.receipt_type must be "
                "'engineering-guardrails-provider-execution-receipt'",
                contract=candidate,
            )

        with self.subTest("required fields cannot duplicate or gain semantics"):
            candidate = deepcopy(self.contract)
            candidate["evidence_receipt_contracts"]["execution"][
                "required_fields"
            ].append("command")
            self.assert_validation_error(
                "execution.required_fields must not contain duplicates",
                contract=candidate,
            )

            candidate = deepcopy(self.contract)
            candidate["evidence_receipt_contracts"]["compatibility"][
                "required_fields"
            ].append("provider_exit_code")
            self.assert_validation_error(
                "compatibility.required_fields must exactly equal",
                contract=candidate,
            )

        with self.subTest("receipt contracts require ordered string lists and booleans"):
            candidate = deepcopy(self.contract)
            candidate["evidence_receipt_contracts"]["compatibility"][
                "required_fields"
            ] = "receipt_sha256"
            self.assert_validation_error(
                "compatibility.required_fields must be a list of strings",
                contract=candidate,
            )

            candidate = deepcopy(self.contract)
            candidate["evidence_receipt_contracts"]["readiness"]["digest"][
                "required"
            ] = 1
            self.assert_validation_error(
                "readiness.digest.required must be True, found 1",
                contract=candidate,
            )

    def test_gwt_006_given_state_claim_mutations_when_checked_then_all_states_remain_unavailable_or_synthetic_only(self) -> None:
        with self.subTest("the state set cannot gain readiness or execution states"):
            candidate = deepcopy(self.contract)
            candidate["state_semantics"]["states"]["selected-ready"] = {}
            self.assert_validation_error(
                "state_semantics.states has unexpected field: selected-ready",
                contract=candidate,
            )

        for state in self.schema["state_semantics"]["required_states"]:
            for area in ("readiness", "compatibility"):
                with self.subTest(f"{state} cannot carry a {area} receipt"):
                    candidate = deepcopy(self.contract)
                    candidate["state_semantics"]["states"][state][area][
                        "receipt"
                    ] = {"receipt_type": "invented"}
                    self.assert_validation_error(
                        f"{state}.{area}.receipt must be None",
                        contract=candidate,
                    )

        with self.subTest("not-selected cannot bypass auto and silent selection"):
            candidate = deepcopy(self.contract)
            candidate["state_semantics"]["states"]["not-selected"]["selection"][
                "auto_install"
            ] = "allowed"
            self.assert_validation_error(
                "not-selected.selection.auto_install must be 'forbidden'",
                contract=candidate,
            )

        with self.subTest("selected-unavailable retains all missing evidence"):
            candidate = deepcopy(self.contract)
            candidate["state_semantics"]["states"]["selected-unavailable"][
                "required_missing_evidence"
            ].pop()
            self.assert_validation_error(
                "selected-unavailable.required_missing_evidence must be",
                contract=candidate,
            )

        with self.subTest("synthetic readiness booleans reject integers"):
            candidate = deepcopy(self.contract)
            candidate["state_semantics"]["states"]["synthetic-readiness-proven"][
                "readiness"
            ]["receipt_digest_required"] = 1
            self.assert_validation_error(
                "synthetic-readiness-proven.readiness.receipt_digest_required "
                "must be True, found 1",
                contract=candidate,
            )

            candidate = deepcopy(self.contract)
            candidate["state_semantics"]["states"]["synthetic-readiness-proven"][
                "execution"
            ]["required_real_receipt"] = 1
            self.assert_validation_error(
                "synthetic-readiness-proven.execution.required_real_receipt "
                "must be True, found 1",
                contract=candidate,
            )

    def test_gwt_007_given_the_starting_templates_when_read_then_they_remain_reference_only_and_target_owned(self) -> None:
        source_templates = (
            ANALYZER_TEMPLATE_PATH,
            ANALYZER_TEST_TEMPLATE_PATH,
            CODE_FIX_TEMPLATE_PATH,
        )
        forbidden = (
            ".csproj",
            ".sln",
            ".slnx",
            "global.json",
            "packagereference",
            "dotnet ",
        )
        for path in source_templates:
            with self.subTest(path=path.name):
                content = path.read_text(encoding="utf-8")
                self.assertIn("reference-only", content.lower())
                self.assertIn("target-owned after copy", content.lower())
                self.assertFalse(
                    any(fragment in content.lower() for fragment in forbidden), path
                )

        analyzer = ANALYZER_TEMPLATE_PATH.read_text(encoding="utf-8")
        analyzer_test = ANALYZER_TEST_TEMPLATE_PATH.read_text(encoding="utf-8")
        self.assertIn("DiagnosticAnalyzer", analyzer)
        self.assertIn("DiagnosticDescriptor", analyzer)
        self.assertIn("GivenTargetSource", analyzer_test)
        self.assertIn("WhenAnalyzerRuns", analyzer_test)
        self.assertIn("ThenExpectedDiagnosticIsObserved", analyzer_test)

    def test_gwt_008_given_recipe_material_when_read_then_contract_fallback_and_documentation_agree(self) -> None:
        manifest = load_yaml(MANIFEST_PATH)
        expected_paths = {
            "provider_contract": "provider-contract.yaml",
            "provider_contract_schema": "provider-contract.schema.yaml",
            "provider_selection_template": "templates/provider-selection.template.yaml",
            "minimal_diagnostic_analyzer_template": "templates/minimal-diagnostic-analyzer.cs.template",
            "minimal_diagnostic_analyzer_test_template": "templates/minimal-diagnostic-analyzer-test.cs.template",
            "code_fix_decision_template": "templates/code-fix-decision.md",
        }
        self.assertEqual("reference-only", manifest["delivery_state"])
        self.assertEqual("not-selected", manifest["default_selection_state"])
        self.assertEqual("official-recommended", manifest["provider_contract"]["recommendation_status"])
        self.assertEqual("unknown", manifest["provider_contract"]["canonical_provider_package_identity"])
        self.assertEqual("real-provider-unavailable", manifest["provider_contract"]["framework_delivery"])
        for material, path in expected_paths.items():
            self.assertEqual(path, manifest["materials"][material]["path"])
            self.assertEqual("reference-only", manifest["materials"][material]["evidence_tier"])

        readme = README_PATH.read_text(encoding="utf-8")
        recipe = RECIPE_PATH.read_text(encoding="utf-8")
        for state in self.schema["state_semantics"]["required_states"]:
            self.assertIn(f"`{state}`", readme)
            self.assertIn(f"`{state}`", recipe)
        self.assertIn("separate types and", readme)
        self.assertIn("separately typed and digested", recipe)

    def test_gwt_009_given_coordinated_schema_and_artifact_drift_when_checked_then_issue_205_baseline_rejects_every_category(self) -> None:
        mutations: tuple[tuple[str, CoordinatedMutation], ...] = (
            ("capability id", mutate_coordinated_capability_id),
            ("capability binding", mutate_coordinated_capability_binding),
            ("boolean", mutate_coordinated_boolean),
            ("unavailable flag", mutate_coordinated_unavailable_flag),
            ("receipt field", mutate_coordinated_receipt_field),
            ("receipt type", mutate_coordinated_receipt_type),
            ("receipt kind", mutate_coordinated_receipt_kind),
            ("state set", mutate_coordinated_state_set),
            ("state requirement", mutate_coordinated_state_requirement),
            ("prohibition", mutate_coordinated_prohibition),
            ("fallback", mutate_coordinated_fallback),
            ("template selection", mutate_coordinated_template_selection),
            ("template null receipt", mutate_coordinated_template_null_receipt),
            ("added contract claim", mutate_coordinated_added_contract_claim),
        )
        for category, mutation in mutations:
            with self.subTest(category=category):
                self.assert_coordinated_mutation_rejected(category, mutation)

    def test_gwt_010_given_the_provider_check_is_selected_when_the_aggregate_runner_executes_then_evidence_is_emitted(self) -> None:
        check_all = CHECK_ALL_PATH.read_text(encoding="utf-8")
        shell_assets = load_yaml(SHELL_ASSETS_PATH)
        runner = "run_source_repository_engineering_guardrails_provider_contract"
        command = "python .ai/scripts/tests/test_engineering_guardrails_provider_contract.py -v"
        self.assertEqual(2, check_all.count(runner))
        self.assertIn(f'run_command_check "{command}"', check_all)
        self.assertIn('"Engineering Guardrails Provider Contract"', check_all)
        self.assertIn(command, shell_assets["check_all_required_commands"])


if __name__ == "__main__":
    unittest.main()
