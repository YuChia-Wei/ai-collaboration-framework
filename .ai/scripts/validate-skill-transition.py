#!/usr/bin/env python3
"""Validate historical v0.6 activation and the current v0.16 retirement lifecycle."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

SCRIPT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_ROOT))
sys.dont_write_bytecode = True

from python_prerequisites import guard_direct_entrypoint

guard_direct_entrypoint(".ai/scripts/validate-skill-transition.py")

import argparse
import hashlib
import yaml

from skill_identifier_lifecycle import RETIREMENT, load_retirement, resolve_identifier


ROOT = Path(__file__).resolve().parents[2]
MANIFEST = Path(".ai/assets/skills/transitions/v0.6.0.yaml")
FIXTURE = Path(".ai/evaluation/fixtures/identifier-compatibility.yaml")
CANONICAL_REGISTRY = Path(".ai/assets/skills/README.MD")
AGENTS_REGISTRY = Path(".agents/skills/README.md")
CLAUDE_REGISTRY = Path(".claude/skills/README.md")

EXPECTED_TRANSITIONS = {
    "repo-structure-sync": ("ai-context-init", "ai-context-lifecycle"),
    "dev-workflow": (
        "software-development-orchestrator",
        "software-development",
    ),
}
RUNTIME_ROOTS = (".agents/skills", ".claude/skills")
MODEL_REPORT = Path(
    ".dev/workflows/2026-07-24-v0-6-model-evaluation/"
    "reports/model-evaluation-report.md"
)
MODEL_EVIDENCE = {
    "terra-candidate-a.yaml": Path(
        ".dev/workflows/2026-07-24-v0-6-model-evaluation/"
        "evidence/terra-candidate-a.yaml"
    ),
    "terra-candidate-b.yaml": Path(
        ".dev/workflows/2026-07-24-v0-6-model-evaluation/"
        "evidence/terra-candidate-b.yaml"
    ),
    "terra-judge.yaml": Path(
        ".dev/workflows/2026-07-24-v0-6-model-evaluation/"
        "evidence/terra-judge.yaml"
    ),
}


def mapping(value: Any, label: str, errors: list[str]) -> dict[str, Any]:
    if not isinstance(value, dict):
        errors.append(f"{label}: must be a mapping")
        return {}
    return value


def string_list(value: Any, label: str, errors: list[str]) -> list[str]:
    if not isinstance(value, list) or not all(
        isinstance(item, str) and item for item in value
    ):
        errors.append(f"{label}: must be a list of non-empty strings")
        return []
    if len(value) != len(set(value)):
        errors.append(f"{label}: contains duplicates")
    return value


def load_yaml(root: Path, path: Path, errors: list[str]) -> dict[str, Any]:
    try:
        value = yaml.safe_load((root / path).read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, yaml.YAMLError) as exc:
        errors.append(f"{path.as_posix()}: cannot read YAML: {exc}")
        return {}
    return mapping(value, path.as_posix(), errors)


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate_registry(
    root: Path,
    path: Path,
    active: set[str],
    compatibility: set[str],
    errors: list[str],
) -> None:
    try:
        text = (root / path).read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        errors.append(f"{path.as_posix()}: cannot read registry: {exc}")
        return
    for identifier in sorted(active):
        if f"- `{identifier}`" not in text:
            errors.append(
                f"{path.as_posix()}: active identifier is missing: {identifier}"
            )
    for identifier in sorted(compatibility):
        if f"`{identifier}`" not in text:
            errors.append(
                f"{path.as_posix()}: deprecated compatibility identifier is missing: "
                f"{identifier}"
            )
        if f"- `{identifier}`" in text:
            errors.append(
                f"{path.as_posix()}: deprecated compatibility identifier is "
                f"listed as active: {identifier}"
            )


def validate(root: Path) -> list[str]:
    errors: list[str] = []
    manifest = load_yaml(root, MANIFEST, errors)
    if not manifest:
        return errors
    if manifest.get("schema_version") != "1.0":
        errors.append(f"{MANIFEST}: schema_version must be 1.0")
    if manifest.get("transition_id") != "SKILL-001-v0.6.0":
        errors.append(f"{MANIFEST}: transition_id must be SKILL-001-v0.6.0")
    if manifest.get("state") != "activated":
        errors.append(f"{MANIFEST}: state must be activated")
    if manifest.get("activation_mode") != "atomic":
        errors.append(f"{MANIFEST}: activation_mode must be atomic")

    transitions = manifest.get("transitions")
    if not isinstance(transitions, list):
        errors.append(f"{MANIFEST}: transitions must be a list")
        transitions = []
    actual: dict[str, tuple[str, str]] = {}
    for index, raw in enumerate(transitions):
        item = mapping(raw, f"{MANIFEST}: transitions[{index}]", errors)
        current = item.get("current_identifier")
        candidate = item.get("candidate_identifier")
        family = item.get("family")
        if not all(isinstance(value, str) and value for value in (current, candidate, family)):
            errors.append(
                f"{MANIFEST}: transitions[{index}] requires current, candidate, and family"
            )
            continue
        if current in actual:
            errors.append(f"{MANIFEST}: duplicate current identifier: {current}")
        actual[current] = (candidate, family)
        if item.get("current_lifecycle") != "deprecated":
            errors.append(f"{MANIFEST}: {current} must be deprecated after activation")
        if item.get("candidate_lifecycle") != "active":
            errors.append(f"{MANIFEST}: {candidate} must be active after activation")
        if item.get("compatibility_lifecycle_after_activation") != "deprecated":
            errors.append(
                f"{MANIFEST}: {current} must become deprecated after activation"
            )
        if item.get("removal_target") is not None:
            errors.append(f"{MANIFEST}: {current} must not have a removal target")
        if item.get("historical_identifier_rewrite") is not False:
            errors.append(
                f"{MANIFEST}: {current} must not authorize historical rewrites"
            )
    if actual != EXPECTED_TRANSITIONS:
        errors.append(
            f"{MANIFEST}: transition mapping drifted: expected "
            f"{EXPECTED_TRANSITIONS}, found {actual}"
        )

    taxonomy = mapping(manifest.get("taxonomy"), f"{MANIFEST}: taxonomy", errors)
    for family in ("ai-context-lifecycle", "software-development"):
        record = mapping(taxonomy.get(family), f"{MANIFEST}: taxonomy.{family}", errors)
        target = string_list(
            record.get("target_members"),
            f"{MANIFEST}: taxonomy.{family}.target_members",
            errors,
        )
        compatibility = string_list(
            record.get("compatibility_members"),
            f"{MANIFEST}: taxonomy.{family}.compatibility_members",
            errors,
        )
        expected_candidates = {
            candidate
            for candidate, candidate_family in EXPECTED_TRANSITIONS.values()
            if candidate_family == family
        }
        expected_current = {
            current
            for current, (_, current_family) in EXPECTED_TRANSITIONS.items()
            if current_family == family
        }
        if not expected_candidates <= set(target):
            errors.append(f"{MANIFEST}: taxonomy.{family} misses candidate identifiers")
        if set(compatibility) != expected_current:
            errors.append(
                f"{MANIFEST}: taxonomy.{family}.compatibility_members drifted"
            )

    gate = mapping(
        manifest.get("activation_gate"), f"{MANIFEST}: activation_gate", errors
    )
    deterministic = mapping(
        gate.get("deterministic_evaluation"),
        f"{MANIFEST}: activation_gate.deterministic_evaluation",
        errors,
    )
    if deterministic.get("status") != "passed":
        errors.append(f"{MANIFEST}: deterministic evaluation must be passed")
    for field in ("corpus", "baseline", "compatibility_fixture"):
        value = deterministic.get(field)
        if not isinstance(value, str) or not (root / value).is_file():
            errors.append(
                f"{MANIFEST}: deterministic_evaluation.{field} must resolve"
            )
    model = mapping(
        gate.get("model_in_loop_evaluation"),
        f"{MANIFEST}: activation_gate.model_in_loop_evaluation",
        errors,
    )
    if model.get("status") != "passed":
        errors.append(f"{MANIFEST}: model evaluation must be passed")
    if model.get("candidate_model") != "gpt-5.6-terra":
        errors.append(f"{MANIFEST}: candidate model must be gpt-5.6-terra")
    if model.get("judge_model") != "gpt-5.6-terra":
        errors.append(f"{MANIFEST}: judge model must be gpt-5.6-terra")
    if model.get("critical_safety_result") != "8/8":
        errors.append(f"{MANIFEST}: critical safety result must be 8/8")
    if model.get("full_rubric_result") != "8/8":
        errors.append(f"{MANIFEST}: full rubric result must be 8/8")
    report = root / MODEL_REPORT
    if not report.is_file():
        errors.append(f"{MANIFEST}: model evaluation report must resolve")
    elif model.get("report_sha256") != sha256_file(report):
        errors.append(f"{MANIFEST}: model evaluation report SHA-256 drifted")
    retained = mapping(
        model.get("retained_evidence_sha256"),
        f"{MANIFEST}: model_in_loop_evaluation.retained_evidence_sha256",
        errors,
    )
    if set(retained) != set(MODEL_EVIDENCE):
        errors.append(f"{MANIFEST}: retained evidence identity set drifted")
    for name, path in MODEL_EVIDENCE.items():
        resolved = root / path
        if not resolved.is_file():
            errors.append(f"{MANIFEST}: retained evidence must resolve: {path}")
        elif retained.get(name) != sha256_file(resolved):
            errors.append(f"{MANIFEST}: retained evidence SHA-256 drifted: {name}")

    current = set(EXPECTED_TRANSITIONS)
    candidates = {candidate for candidate, _ in EXPECTED_TRANSITIONS.values()}
    try:
        load_retirement(root)
    except (OSError, ValueError, yaml.YAMLError) as exc:
        errors.append(f"{RETIREMENT}: {exc}")
    for identifier in EXPECTED_TRANSITIONS:
        for entry_root in (".ai/assets/skills", *RUNTIME_ROOTS):
            directory = root / entry_root / identifier
            if directory.exists() and any(path.is_file() for path in directory.rglob("*")):
                errors.append(f"retired skill entry must be absent: {entry_root}/{identifier}")
    for identifier in candidates:
        active_spec = root / ".ai/assets/skills" / identifier / "skill.yaml"
        if not active_spec.is_file():
            errors.append(f"active canonical skill is missing: {identifier}")
        else:
            active = load_yaml(
                root,
                Path(".ai/assets/skills") / identifier / "skill.yaml",
                errors,
            )
            if active.get("status") != "active":
                errors.append(f"active canonical skill has wrong status: {identifier}")
        for runtime_root in RUNTIME_ROOTS:
            if not (root / runtime_root / identifier / "SKILL.md").is_file():
                errors.append(
                    f"active runtime wrapper is missing: "
                    f"{runtime_root}/{identifier}"
                )

    fixture = load_yaml(root, FIXTURE, errors)
    expected_aliases = {
        current_identifier: candidate
        for current_identifier, (candidate, _) in EXPECTED_TRANSITIONS.items()
    }
    if set(fixture.get("active_identifiers", [])) != candidates:
        errors.append(f"{FIXTURE}: active identifier candidate set drifted")
    if fixture.get("compatibility_entries") != expected_aliases:
        errors.append(f"{FIXTURE}: compatibility entry mapping drifted")
    if set(fixture.get("historical_identifiers", [])) != current:
        errors.append(f"{FIXTURE}: historical identifier set drifted")

    for registry in (CANONICAL_REGISTRY, AGENTS_REGISTRY, CLAUDE_REGISTRY):
        validate_registry(root, registry, candidates, current, errors)
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--identifier", help="Validate one explicit skill request")
    parser.add_argument("--context", choices=("runtime", "historical"), default="runtime")
    args = parser.parse_args()
    errors = validate(args.root.resolve())
    if errors:
        print("Skill transition validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    if args.identifier:
        try:
            result = resolve_identifier(args.root.resolve(), args.identifier, args.context)
        except (OSError, ValueError, yaml.YAMLError) as exc:
            print(f"Skill identifier validation failed: {exc}")
            return 1
        print(result["message"])
        return 0 if result["accepted"] else 1
    print(
        "Skill transition validation passed: two active identifiers, two "
        "retired tombstones, historical atomic activation, and retained "
        "Terra model evidence."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
