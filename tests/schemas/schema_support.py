"""Explicit source scope, cached local schemas, and small authored fixtures."""
from functools import lru_cache
import importlib.util
import json
from pathlib import Path
import sys

from jsonschema import Draft202012Validator, FormatChecker
from referencing import Registry, Resource
import yaml

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

# Deliberate scope matrix: 12 distribution JSON schemas, seven record JSON
# schemas (including legacy lesson and unpublished standards-promotion), and
# one custom declarative knowledge baseline. New source schemas require a
# conscious fixture/coverage decision, not just automatic meta-validation.
DISTRIBUTION = {
    "build": "Build", "catalog-files": "CatalogFiles", "catalog": "Catalog",
    "content-package": "ContentPackage", "contracts": None,
    "engine-bundle": "EngineBundle", "files": "Files", "lock": "Lock",
    "manifest": "Manifest", "preset": "Preset", "selection": "Selection",
    "subset": "Subset",
}
RECORDS = {
    "adr": ("adr-author", "adr-record", "adr.py"),
    "lesson": ("lesson-author", "lesson-record-v2", "lesson.py"),
    "legacy-lesson": ("lesson-author", "lesson-record", "lesson.py"),
    "backlog": ("local-backlog", "local-backlog-record", "local_backlog.py"),
    "pr": ("pr-author", "pr-record", "pr.py"),
    "cbf": ("problem-frame-author", "cbf-record-v1", "problem_frame.py"),
    "promotion": ("standards-promotion", "promotion-record", "standards_promotion.py"),
}
PROVIDER_ROOT = "src/knowledge/dotnet-backend/tooling/on-demand-mechanical-validation"
PROVIDER_SCHEMA = PROVIDER_ROOT + "/provider-contract.schema.yaml"
JSON_PATHS = tuple(
    [f"src/distribution/schemas/{name}.schema.json" for name in DISTRIBUTION]
    + [f"src/skills/{family}/schemas/{name}.schema.json" for family, name, _ in RECORDS.values()]
)
STAMP = "2026-10-02T00:00:00+00:00"
SHA = "a" * 64
OID = "b" * 40


@lru_cache(maxsize=None)
def document(path):
    text = (ROOT / path).read_text(encoding="utf-8")
    return json.loads(text) if path.endswith(".json") else yaml.safe_load(text)


@lru_cache(maxsize=1)
def registry():
    # No retrieval callback: an undeclared or remote $ref fails locally.
    return Registry().with_resources(
        ((ROOT / path).as_uri(), Resource.from_contents(document(path)))
        for path in JSON_PATHS
    )


@lru_cache(maxsize=None)
def validator(path, fragment=""):
    return Draft202012Validator(
        {"$ref": (ROOT / path).as_uri() + fragment},
        registry=registry(), format_checker=FormatChecker(),
    )


def distribution_validator(name):
    return validator(f"src/distribution/schemas/{name}.schema.json")


def record_validator(name):
    family, schema, _ = RECORDS[name]
    return validator(f"src/skills/{family}/schemas/{schema}.schema.json")


@lru_cache(maxsize=None)
def record_tool(name):
    family, _, script = RECORDS[name]
    path = ROOT / "src/skills" / family / "scripts" / script
    module_name = "schema_test_" + family.replace("-", "_")
    if module_name not in sys.modules:
        spec = importlib.util.spec_from_file_location(module_name, path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
    return sys.modules[module_name]


def changed(value, path, replacement):
    """Copy fixture data and replace one field without mutating cached source."""
    from copy import deepcopy
    value = deepcopy(value)
    parent = value
    for part in path[:-1]:
        parent = parent[part]
    parent[path[-1]] = replacement
    # Actual parsed JSON has no shared mutable containers. deepcopy alone
    # preserves aliases introduced by composing nested fixture dictionaries.
    return json.loads(json.dumps(value))


def source():
    return {"path": "src/example.py", "git_blob": OID, "mode": "100644", "size": 0, "sha256": SHA}


def knowledge():
    return {
        "content_package_version": 1, "id": "common", "version": "0.1.0", "entrypoint": "README.md",
        "members": [{"path": "README.md", "kind": "index"}, {"path": "content-package.yaml", "kind": "metadata"}],
        "resources": [{"id": "index", "path": "README.md", "kind": "knowledge", "rule_ids": [],
                       "capabilities": ["review"], "operations": ["review"], "technology_profile": None}],
        "dependencies": {"required": [], "optional": []}, "references": [],
    }


def selection():
    return {"selection_version": 2,
            "catalog": {"identity": "catalog:1:0.1.0:" + SHA, "catalog_sha256": SHA, "files_sha256": SHA},
            "skills": [], "knowledge": [], "adapters": [], "bindings": [], "skill_naming": "original"}


def distribution_examples():
    origin = {"commit": OID, "tree": OID}
    generator = {"id": "schema-fixture", "implementation": [source()]}
    catalog = {"catalog_version": 1, "release_version": "0.1.0-rc.1", "source": origin,
               "components": [], "adapters": [], "presets": [], "build_inputs": [source()], "generator": generator}
    files = {"schema_version": 2, "files": [{"path": "skills/example/SKILL.md", "destination": ".ai/core/skills/example/SKILL.md",
             "owner": "example", "kind": "payload", "mode": "100644", "size": 0, "sha256": SHA,
             "source": source(), "binding": None}]}
    inventory = {"catalog_files_version": 1, "files": [{"path": "skills/example/SKILL.md", "kind": "skill",
                 "owner": "example", "member": "SKILL.md", "source": source()}]}
    engine = {"id": "framework-managed-installation", "version": "2.0.0", "source_commit": OID,
              "files": [{"path": "distribution/contracts.py", "sha256": SHA}]}
    desired = selection()
    subset = {"schema_version": 3, "mode": "catalog-subset", "release_version": "0.1.0-rc.1", "source": origin,
              "catalog": desired["catalog"], "desired": desired, "desired_sha256": SHA,
              "components": [], "adapters": [], "generator": generator}
    examples = {
        "catalog": catalog, "catalog-files": inventory, "content-package": knowledge(), "files": files,
        "engine-bundle": {"engine_package_version": 1, "engine": engine},
        "manifest": {"manifest_version": 2, "profiles": [], "components": [], "adapters": []},
        "preset": {"preset_version": 1, "id": "minimal", "version": "0.1.0", "skills": [], "knowledge": [], "adapters": []},
        "selection": desired, "subset": subset,
        "lock": {"lock_version": 2, "installation_id": "c" * 32, "engine": engine, "mode_policy": "windows-inventory-only",
                 "candidate_identity": "fixture-only", "catalog_document": catalog, "catalog_inventory": inventory,
                 "selection": subset, "inventory": files, "project_inputs": []},
        "build": {"schema_version": 2, "artifact_kind": "catalog", "identity": "fixture-only",
                  "identity_inputs": {"metadata/catalog.json": SHA, "metadata/catalog-files.json": SHA}, "completed_at": STAMP,
                  "executing_implementation": [{"source": source(), "execution_file_sha256": SHA}],
                  "runtime": {"python": "3", "pyyaml": "6", "os": "nt"}, "mode_materialization": "inventory-only",
                  "installation": "not-performed", "behavioral_validation": "not-performed", "publication": "not-performed"},
    }
    return json.loads(json.dumps(examples))


def lesson_content():
    return {"title": "Observe retry behavior", "observation": "A bounded fixture failed once.", "evidence": [],
            "conclusion": "Investigate before retry.", "applies_when": ["A fixture fails."],
            "does_not_apply_when": [], "confidence": "tentative", "follow_up": []}


def cbf():
    return {
        "family": "problem-frame.cbf", "schema_version": "1.0.0", "id": "cbf-" + "c" * 32,
        "frame_key": "checkout", "title": "Checkout command", "derived_from": None,
        "sources": [{"id": "requirement", "kind": "requirement", "reference": "requirements.md", "revision": None,
                     "locator": "checkout", "sha256": None, "authority": "proposed", "authority_reference": None}],
        "statements": [{"id": key, "category": category, "text": text, "basis": "stated", "source_ids": ["requirement"]}
                       for key, category, text in [("actor", "actor", "Buyer"), ("command", "command", "Check out"),
                                                   ("domain", "controlled-domain", "Cart")]],
        "scenarios": [{"id": "checkout", "title": "Submit cart", "source_ids": ["requirement"],
                       "given": ["A valid cart"], "when": ["Buyer checks out"],
                       "then": [{"id": "accepted", "text": "Checkout is accepted", "basis": "stated",
                                 "source_ids": ["requirement"], "statement_ids": ["command"]}], "tests_anchor": []}],
        "open_questions": [],
    }


def record_examples():
    base = {"schema_version": "1.0.0", "owner": "project", "created_at": STAMP, "updated_at": STAMP}
    lifecycle = {"revision": 1, "successor": None, "provenance": [], "history": []}
    adr_content = {"title": "Choose storage", "context": "A local store is needed", "decision_drivers": ["Portability"],
                   "options": [{"id": key, "summary": key, "benefits": [], "costs": []} for key in ["files", "database"]],
                   "consequences": [], "evidence": [], "applies_when": ["Local use"], "does_not_apply_when": []}
    pr_subject = {"object_format": "sha1", **{key: OID for key in ["base_commit", "head_commit", "merge_base", "base_tree", "head_tree"]},
                  "diff_sha256": SHA, "git_version": "fixture", "diff_recipe": "pr.diff/v1"}
    promotion_tool = record_tool("promotion")
    snapshot = {"path": "rule.md", "sha256": promotion_tool.digest(b"before"), "utf8": "before", "observed_at": STAMP}
    promotion_content = {"title": "Propose a rule", "target_id": "rule", "baseline": snapshot, "replacement": "after",
                         "rationale": "Observed need", "applicability": "Local work", "conflicts": [],
                         "sources": [{"kind": "lesson", "id": "lesson-fixture", "schema_version": "2.0.0",
                                      "reason": "Supporting observation", "snapshot": snapshot}],
                         "target_binding": {"binding_id": "rule", "config_path": "config.yaml", "config_sha256": SHA,
                                            "binding": {"id": "rule", "path": "rule.md", "applicability": "Local work",
                                                        "allowed_actors": ["owner"], "adoption_source": None, "effect_source": None}}}
    promotion_content["after_sha256"] = promotion_tool.digest(b"after")
    promotion_content["subject_sha256"] = promotion_tool.digest(promotion_tool.encode(promotion_tool.proposal_subject(promotion_content)))
    return {
        "adr": {**base, **lifecycle, "kind": "adr", "id": "adr-" + "c" * 32, "status": "draft", "decision": None, "content": adr_content},
        "lesson": {**base, **lifecycle, "schema_version": "2.0.0", "kind": "lesson", "id": "lesson-" + "c" * 32,
                   "status": "candidate", "decision": None, "content": lesson_content()},
        "legacy-lesson": {**base, "kind": "lesson", "id": "lesson-" + "c" * 32, "status": "candidate", **lesson_content()},
        "backlog": {**base, "kind": "local-backlog", "id": "work-" + "c" * 32, "title": "Work item", "summary": "Bounded work",
                    "references": [], "writable_authority": "local", "state": "draft", "state_reason": "Proposed", "acceptance": ["Observable result"], "completion_evidence": []},
        "pr": {**base, "kind": "pr", "id": "pr-" + "c" * 32, "state": "prepared", "title": "Proposed change",
               "summary": "Review a bounded change", "references": [], "subject": pr_subject, "validation": []},
        "cbf": cbf(),
        "promotion": {**base, **lifecycle, "kind": "standards-promotion", "id": "promotion-" + "c" * 32,
                      "status": "proposed", "observation": None, "content": promotion_content},
    }
