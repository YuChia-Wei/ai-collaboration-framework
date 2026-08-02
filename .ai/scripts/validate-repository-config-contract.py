#!/usr/bin/env python3
"""Validate source configuration and downstream seed ownership boundaries."""

from __future__ import annotations

import sys
from pathlib import Path

SCRIPT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_ROOT))
sys.dont_write_bytecode = True

from python_prerequisites import guard_direct_entrypoint

guard_direct_entrypoint(".ai/scripts/validate-repository-config-contract.py")

import argparse
import hashlib
import yaml


DEFAULT_ROOT = Path(__file__).resolve().parents[2]
PROFILE = Path(".ai/distribution/profiles/dotnet-backend.yaml")
TEMPLATE_ROOT = Path(
    ".ai/assets/skills/ai-context-init/templates/public-root"
)
TEMPLATE_MANIFEST = TEMPLATE_ROOT.parent / "public-template-manifest.yaml"
ASSESSMENT_POLICY = Path(".dev/standards/ASSESSMENT-ARTIFACT-POLICY.md")
ADR = Path(".dev/adr/ADR-001-separate-source-config-from-downstream-templates.md")
ADR_INDEX = Path(".dev/adr/INDEX.md")
LEGACY_EVIDENCE = Path(
    ".dev/assessments/ASM-20260722-005/evidence/workservice/"
    "2026-07-22-dev-workflow-skill-comparison.md"
)
LEGACY_SHA256 = "24a12c4fda19ff8f7aae6902e66c0d95f799bfbf2ef8bdc5cdf1ce710aaab427"
ORIGINAL_RULE = ".dev/assessments/**/evidence/external/original/** binary"
LEGACY_RULE = f"{LEGACY_EVIDENCE.as_posix()} binary"
SOURCE_ONLY_SCRIPTS = {
    ".ai/scripts/validate-repository-config-contract.py",
    ".ai/scripts/validate-skill-transition.py",
    ".ai/scripts/tests/test_repository_config_contract.py",
    ".ai/scripts/tests/test_skill_transition_contract.py",
}


def read_text(root: Path, relative: Path, errors: list[str]) -> str:
    path = root / relative
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        errors.append(f"{relative.as_posix()}: cannot read UTF-8 text: {exc}")
        return ""


def load_yaml(root: Path, relative: Path, errors: list[str]) -> dict:
    text = read_text(root, relative, errors)
    if not text:
        return {}
    try:
        value = yaml.safe_load(text)
    except yaml.YAMLError as exc:
        errors.append(f"{relative.as_posix()}: invalid YAML: {exc}")
        return {}
    if not isinstance(value, dict):
        errors.append(f"{relative.as_posix()}: root must be a mapping")
        return {}
    return value


def active_attribute_lines(text: str) -> set[str]:
    return {
        line.strip()
        for line in text.splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    }


def editor_section(text: str, name: str) -> dict[str, str]:
    current = ""
    values: dict[str, str] = {}
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith(("#", ";")):
            continue
        if line.startswith("[") and line.endswith("]"):
            current = line
            continue
        if current == name and "=" in line:
            key, value = line.split("=", 1)
            values[key.strip()] = value.strip()
    return values


def validate_editorconfig(root: Path, errors: list[str]) -> None:
    source_relative = Path(".editorconfig")
    seed_relative = TEMPLATE_ROOT / ".editorconfig"
    source = read_text(root, source_relative, errors)
    seed = read_text(root, seed_relative, errors)
    for relative, text, header in (
        (source_relative, source, "Source-repository configuration"),
        (seed_relative, seed, "Downstream seed: target-owned after initialization."),
    ):
        if not text:
            continue
        data = (root / relative).read_bytes()
        if not data.endswith(b"\n"):
            errors.append(f"{relative.as_posix()}: must end with a final newline")
        if header not in text:
            errors.append(f"{relative.as_posix()}: missing ownership header")
        defaults = editor_section(text, "[*]")
        if defaults.get("end_of_line") != "lf":
            errors.append(f"{relative.as_posix()}: [*] end_of_line must be lf")
        if defaults.get("insert_final_newline") != "true":
            errors.append(f"{relative.as_posix()}: [*] insert_final_newline must be true")
        commands = editor_section(text, "[*.{bat,cmd}]")
        if commands.get("end_of_line") != "crlf":
            errors.append(f"{relative.as_posix()}: bat/cmd end_of_line must be crlf")
    if source and seed and source == seed:
        errors.append(".editorconfig and downstream seed must be distinct owned files")


def validate_gitattributes(root: Path, errors: list[str]) -> None:
    source_relative = Path(".gitattributes")
    seed_relative = TEMPLATE_ROOT / ".gitattributes"
    source = read_text(root, source_relative, errors)
    seed = read_text(root, seed_relative, errors)
    required_portable = {
        "* text=auto eol=lf",
        "*.bat text eol=crlf",
        "*.cmd text eol=crlf",
    }
    source_lines = active_attribute_lines(source)
    seed_lines = active_attribute_lines(seed)
    for relative, lines in ((source_relative, source_lines), (seed_relative, seed_lines)):
        missing = sorted(required_portable - lines)
        if missing:
            errors.append(f"{relative.as_posix()}: missing text rules {missing}")
    if ORIGINAL_RULE not in source_lines:
        errors.append(f".gitattributes: missing centralized immutable-original rule: {ORIGINAL_RULE}")
    if LEGACY_RULE not in source_lines:
        errors.append(f".gitattributes: missing exact retained legacy rule: {LEGACY_RULE}")
    evidence_binary_rules = {
        line
        for line in source_lines
        if "evidence/" in line and (line.endswith(" binary") or " -text" in line)
    }
    allowed = {ORIGINAL_RULE, LEGACY_RULE}
    if evidence_binary_rules != allowed:
        errors.append(
            ".gitattributes: immutable evidence rules must be the centralized "
            f"convention plus exact legacy exception; found {sorted(evidence_binary_rules)}"
        )
    forbidden_seed_tokens = (".dev/assessments", "evidence/external/original", "ASM-")
    for token in forbidden_seed_tokens:
        if token in seed:
            errors.append(f"{seed_relative.as_posix()}: source-only token leaked: {token}")
    tactical = sorted(
        path.relative_to(root).as_posix()
        for path in (root / ".dev/assessments").glob("*/evidence/**/.gitattributes")
    )
    if tactical:
        errors.append(f"per-assessment .gitattributes files are forbidden: {tactical}")
    legacy_path = root / LEGACY_EVIDENCE
    try:
        actual = hashlib.sha256(legacy_path.read_bytes()).hexdigest()
    except OSError as exc:
        errors.append(f"{LEGACY_EVIDENCE.as_posix()}: cannot read legacy evidence: {exc}")
    else:
        if actual != LEGACY_SHA256:
            errors.append(
                f"{LEGACY_EVIDENCE.as_posix()}: SHA-256 changed: "
                f"expected {LEGACY_SHA256}, got {actual}"
            )


def validate_template_manifest(root: Path, errors: list[str]) -> None:
    manifest = load_yaml(root, TEMPLATE_MANIFEST, errors)
    if not manifest:
        return
    if manifest.get("ownership") != "target-template":
        errors.append(f"{TEMPLATE_MANIFEST.as_posix()}: ownership must be target-template")
    if manifest.get("install_behavior") != "seed":
        errors.append(f"{TEMPLATE_MANIFEST.as_posix()}: install_behavior must be seed")
    mappings = manifest.get("mappings")
    if not isinstance(mappings, list):
        errors.append(f"{TEMPLATE_MANIFEST.as_posix()}: mappings must be a list")
        return
    for name in (".editorconfig", ".gitattributes"):
        matches = [
            item
            for item in mappings
            if isinstance(item, dict)
            and item.get("source") == f"public-root/{name}"
            and item.get("target") == name
        ]
        if len(matches) != 1:
            errors.append(
                f"{TEMPLATE_MANIFEST.as_posix()}: require exactly one public-root/{name} -> {name} mapping"
            )
        elif matches[0].get("component_id") != "software-development-core":
            errors.append(
                f"{TEMPLATE_MANIFEST.as_posix()}: {name} mapping must use software-development-core"
            )


def find_by_id(items: object, item_id: str) -> dict:
    if not isinstance(items, list):
        return {}
    return next(
        (
            item
            for item in items
            if isinstance(item, dict) and item.get("id") == item_id
        ),
        {},
    )


def validate_profile(root: Path, errors: list[str]) -> None:
    profile = load_yaml(root, PROFILE, errors)
    if not profile:
        return
    entries = profile.get("entries")
    integration = find_by_id(entries, "repository-integration-seeds")
    integration_sources = integration.get("source", [])
    if not isinstance(integration_sources, list):
        errors.append(f"{PROFILE.as_posix()}: repository-integration-seeds source must be a list")
        integration_sources = []
    for name in (".editorconfig", ".gitattributes"):
        if name in integration_sources:
            errors.append(f"{PROFILE.as_posix()}: source root {name} must not be a target-template entry")
    public = find_by_id(entries, "public-root-and-catalog-seeds")
    public_sources = public.get("source", [])
    if not isinstance(public_sources, list) or (
        ".ai/assets/skills/ai-context-init/templates/public-root/**"
        not in public_sources
    ):
        errors.append(f"{PROFILE.as_posix()}: public-root seed allowlist is missing")
    if public.get("ownership") != "target-template" or public.get("install_behavior") != "seed":
        errors.append(f"{PROFILE.as_posix()}: public-root seeds must remain target-template/seed")
    source_root = find_by_id(profile.get("exclusions"), "source-root-truth")
    root_patterns = set(source_root.get("patterns", []))
    for name in (".editorconfig", ".gitattributes"):
        if name not in root_patterns:
            errors.append(f"{PROFILE.as_posix()}: source-root-truth must exclude {name}")
    runtime = find_by_id(profile.get("exclusions"), "repository-and-local-runtime-state")
    runtime_patterns = set(runtime.get("patterns", []))
    missing = sorted(SOURCE_ONLY_SCRIPTS - runtime_patterns)
    if missing:
        errors.append(f"{PROFILE.as_posix()}: source-only CFG/SKILL validators missing: {missing}")


def validate_policy_and_adr(root: Path, errors: list[str]) -> None:
    policy = read_text(root, ASSESSMENT_POLICY, errors)
    required_policy = (
        "evidence/external/original/<source-id>/<file>",
        "Ordinary assessment evidence is repository text",
        "Do not add per-assessment `.gitattributes` files",
        "new immutable originals must use the convention",
    )
    for phrase in required_policy:
        if phrase not in policy:
            errors.append(f"{ASSESSMENT_POLICY.as_posix()}: missing contract phrase: {phrase}")
    adr = read_text(root, ADR, errors)
    if "## Status\n\nAccepted" not in adr:
        errors.append(f"{ADR.as_posix()}: ADR-001 must be Accepted")
    adr_index = read_text(root, ADR_INDEX, errors)
    if "| Accepted |" not in adr_index:
        errors.append(f"{ADR_INDEX.as_posix()}: ADR-001 index status must be Accepted")


def validate(root: Path) -> list[str]:
    errors: list[str] = []
    validate_editorconfig(root, errors)
    validate_gitattributes(root, errors)
    validate_template_manifest(root, errors)
    validate_profile(root, errors)
    validate_policy_and_adr(root, errors)
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    args = parser.parse_args()
    root = args.root.resolve()
    errors = validate(root)
    if errors:
        print("Repository configuration contract validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print("Repository configuration contract validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
