"""Distribution file schemas, pinned runtime shapes, and in-memory references."""
from copy import deepcopy
from hashlib import sha1
import unittest

from jsonschema import Draft202012Validator
from referencing.exceptions import Unresolvable

from schemas.schema_support import (
    DISTRIBUTION, JSON_PATHS, PROVIDER_SCHEMA, RECORDS, ROOT, SHA, changed,
    distribution_examples, distribution_validator, document, knowledge,
    registry, selection, source, validator,
)
from distribution import contracts
from distribution.content import closure, descriptor, desired_shape, load_content_package
from distribution.data import DistributionError, json_bytes
from distribution.git_source import Blob
from distribution.installation_state import InstallationError


def content_package(data):
    raw = json_bytes(data)
    oid = sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
    return load_content_package(Blob("content-package.yaml", oid, "100644", raw))


class SourceSchemaInventoryTests(unittest.TestCase):
    def test_scope_matrix_covers_every_source_schema(self):
        paths = set((ROOT / "src/distribution/schemas").glob("*.schema.json"))
        paths.update((ROOT / "src/skills").glob("*/schemas/*.schema.json"))
        paths.update((ROOT / "src/knowledge").rglob("*.schema.yaml"))
        self.assertEqual({p.relative_to(ROOT).as_posix() for p in paths}, set(JSON_PATHS) | {PROVIDER_SCHEMA})
        self.assertEqual((len(DISTRIBUTION), len(RECORDS)), (12, 7))

    def test_all_json_schemas_are_well_formed(self):
        for path in JSON_PATHS:
            with self.subTest(path=path):
                Draft202012Validator.check_schema(document(path))

    def test_all_references_stay_inside_the_declared_local_bundle(self):
        def references(node):
            if isinstance(node, dict):
                if "$ref" in node:
                    yield node["$ref"]
                for child in node.values():
                    yield from references(child)
            elif isinstance(node, list):
                for child in node:
                    yield from references(child)

        for path in JSON_PATHS:
            for ref in references(document(path)):
                with self.subTest(path=path, ref=ref):
                    self.assertTrue(ref.startswith("#/$defs/") or ref.startswith("contracts.schema.json#/$defs/"))
                    registry().resolver((ROOT / path).as_uri()).lookup(ref)
        with self.assertRaises(Unresolvable):
            registry().resolver().lookup("https://example.invalid/unregistered.schema.json")


class DistributionSchemaTests(unittest.TestCase):
    def test_sub_agent_package_and_selection_v3_schema_runtime_parity(self):
        package={'sub_agent_package_version':1,'id':'reviewer','version':'0.1.0',
                 'entrypoint':'sub-agent.yaml','members':['runtime/codex.toml','sub-agent-package.yaml','sub-agent.yaml'],
                 'dependencies':{'required':[],'optional':[]}}
        schema=validator('src/distribution/schemas/contracts.schema.json','#/$defs/SubAgentPackage')
        schema.validate(package); contracts.validate('SubAgentPackage',package)
        for path,value in ((('sub_agent_package_version',),True),(('entrypoint',),'SKILL.md'),(('members',),['../escape'])):
            bad=changed(package,path,value)
            if path!=('members',): self.assertFalse(schema.is_valid(bad))
            with self.assertRaises(ValueError):
                from distribution.content import load_sub_agent_package
                load_sub_agent_package(Blob('sub-agent-package.yaml','0'*40,'100644',json_bytes(bad)))
        desired=selection(); desired.update(selection_version=3,sub_agents=['reviewer'])
        distribution_validator('selection').validate(desired); desired_shape(desired)
        for field,value in (('sub_agents',['reviewer','reviewer']),('selection_version',2)):
            bad=changed(desired,(field,),value)
            self.assertFalse(distribution_validator('selection').is_valid(bad))
            with self.assertRaises(ValueError): desired_shape(bad)

    def test_runtime_definition_literal_matches_source_schema(self):
        self.assertEqual(contracts.DEFINITIONS, document("src/distribution/schemas/contracts.schema.json")["$defs"])

    def test_every_wrapper_accepts_a_representative_document_in_both_validators(self):
        examples = distribution_examples()
        self.assertEqual(set(examples), set(DISTRIBUTION) - {"contracts"})
        for name, value in examples.items():
            with self.subTest(schema=name):
                distribution_validator(name).validate(value)
                self.assertIs(contracts.validate(DISTRIBUTION[name], value), value)

    def test_required_fields_and_closed_top_level_objects(self):
        for name, value in distribution_examples().items():
            for operation in ("missing", "unknown"):
                bad = deepcopy(value)
                if operation == "missing":
                    del bad[next(iter(bad))]
                else:
                    bad["undeclared"] = True
                with self.subTest(schema=name, operation=operation):
                    self.assertFalse(distribution_validator(name).is_valid(bad))
                    with self.assertRaises(DistributionError):
                        contracts.validate(DISTRIBUTION[name], bad)

    def test_each_wrapper_rejects_nested_or_scalar_contract_violations(self):
        cases = {
            "build": (("publication",), "published"),
            "catalog-files": (("files", 0, "kind"), "unknown"),
            "catalog": (("release_version",), "01.0.0"),
            "content-package": (("resources", 0, "capabilities"), []),
            "engine-bundle": (("engine", "version"), "3.0.0"),
            "files": (("files", 0, "size"), -1),
            "lock": (("installation_id",), "not-a-hex-id"),
            "manifest": (("components",), "not-an-array"),
            "preset": (("id",), "x" * 81),
            "selection": (("skill_naming",), "automatic"),
            "subset": (("desired_sha256",), "a" * 63),
        }
        examples = distribution_examples()
        self.assertEqual(set(cases), set(examples))
        for name, (path, replacement) in cases.items():
            bad = changed(examples[name], path, replacement)
            with self.subTest(schema=name, field=path):
                self.assertFalse(distribution_validator(name).is_valid(bad))
                with self.assertRaises(DistributionError):
                    contracts.validate(DISTRIBUTION[name], bad)

    def test_version_discriminators_reject_unknown_string_and_boolean(self):
        for name, value in distribution_examples().items():
            field = next(iter(value))
            for version in (999, str(value[field]), True):
                bad = changed(value, (field,), version)
                with self.subTest(schema=name, version=version):
                    self.assertFalse(distribution_validator(name).is_valid(bad))
                    with self.assertRaises(DistributionError):
                        contracts.validate(DISTRIBUTION[name], bad)

    def test_integral_float_schema_runtime_divergence_is_intentional(self):
        # JSON Schema compares mathematical integers; runtime accepts exact int
        # discriminators and rejects all floats in its bounded input parser.
        for name, value in distribution_examples().items():
            field = next(iter(value))
            bad = changed(value, (field,), float(value[field]))
            with self.subTest(schema=name):
                distribution_validator(name).validate(bad)
                with self.assertRaises(InstallationError):
                    contracts.validate(DISTRIBUTION[name], bad)

    def test_contract_definitions_enforce_lengths_types_and_field_closure(self):
        source_validator = validator("src/distribution/schemas/contracts.schema.json", "#/$defs/Source")
        for path in ("x", "x" * 240):
            value = {**source(), "path": path}
            source_validator.validate(value)
            contracts.validate("Source", value)
        for field, value in [("path", ""), ("path", "x" * 241), ("path", "C:/unsafe"),
                             ("mode", "100600"), ("git_blob", "z" * 40), ("size", True), ("unknown", 1)]:
            bad = {**source(), field: value}
            with self.subTest(field=field, value=value):
                self.assertFalse(source_validator.is_valid(bad))
                with self.assertRaises(DistributionError):
                    contracts.validate("Source", bad)

    def test_arrays_and_nested_objects_are_closed(self):
        examples = distribution_examples()
        for name, path, value in [
            ("catalog", ("source", "extra"), 1),
            ("content-package", ("resources", 0, "extra"), 1),
            ("files", ("files",), examples["files"]["files"] * 2),
            ("selection", ("adapters",), ["codex", "codex"]),
        ]:
            bad = changed(examples[name], path, value)
            with self.subTest(schema=name, path=path):
                self.assertFalse(distribution_validator(name).is_valid(bad))
                with self.assertRaises((DistributionError, ValueError)):
                    contracts.validate(DISTRIBUTION[name], bad)

    def test_runtime_requires_timezone_and_rejects_container_aliases(self):
        # JSON Schema format checking depends on optional host dependencies;
        # the owned runtime enforces its timestamp rule on every host.
        build = distribution_examples()["build"]
        with self.assertRaisesRegex(DistributionError, "timestamp offset"):
            contracts.validate("Build", {**build, "completed_at": "2026-10-02T00:00:00"})
        rows = knowledge()
        rows["resources"].append(rows["resources"][0])
        with self.assertRaises(InstallationError) as raised:
            contracts.validate("ContentPackage", rows)
        self.assertEqual(raised.exception.diagnostic["code"], "aliased-input")

    def test_selection_versions_preserve_distinct_naming_shapes(self):
        modern = selection()
        legacy = {key: value for key, value in modern.items() if key != "skill_naming"}
        legacy["selection_version"] = 1
        for value in [legacy, modern, {**modern, "skill_naming": "prefixed"}]:
            distribution_validator("selection").validate(value)
            desired_shape(value)
        for bad in [{**legacy, "skill_naming": "original"},
                    {key: value for key, value in modern.items() if key != "skill_naming"}]:
            self.assertFalse(distribution_validator("selection").is_valid(bad))
            with self.assertRaises(DistributionError):
                desired_shape(bad)


class DistributionReferenceTests(unittest.TestCase):
    def test_resource_ids_must_be_unique_even_when_rows_differ(self):
        good = knowledge()
        content_package(good)
        bad = deepcopy(good)
        bad["resources"].append({**bad["resources"][0], "capabilities": ["implement"]})
        distribution_validator("content-package").validate(bad)
        with self.assertRaisesRegex(DistributionError, "duplicate identity"):
            content_package(bad)

    def test_reference_source_and_dependency_must_exist(self):
        good = knowledge()
        good["dependencies"]["required"] = [{"kind": "knowledge", "id": "other", "version": "0.1.0"}]
        good["references"] = [{"from": "README.md", "resource_id": "index",
                               "target": {"package": "other", "path": "README.md", "anchor": None},
                               "requirement": "required", "on_missing": "unavailable"}]
        content_package(good)
        for path, replacement, diagnostic in [
            (("references", 0, "from"), "missing.md", "source member missing"),
            (("dependencies", "required"), [], "matching dependency"),
            (("resources", 0, "path"), "missing.md", "resource member/kind binding"),
        ]:
            bad = changed(good, path, replacement)
            distribution_validator("content-package").validate(bad)
            with self.subTest(path=path), self.assertRaisesRegex(DistributionError, diagnostic):
                content_package(bad)

    def test_dependency_closure_rejects_absence_version_mismatch_and_cycle(self):
        common = descriptor("knowledge", content_package(knowledge()))
        other = deepcopy(common)
        other["id"] = "other"
        common["required_dependencies"] = [{"kind": "knowledge", "id": "other", "version": "0.1.0"}]
        closure([common, other])
        with self.assertRaisesRegex(DistributionError, "dependency-closure"):
            closure([common])
        with self.assertRaisesRegex(DistributionError, "dependency-version"):
            closure([common, {**other, "version": "0.2.0"}])
        other["required_dependencies"] = [{"kind": "knowledge", "id": "common", "version": "0.1.0"}]
        with self.assertRaisesRegex(DistributionError, "dependency-cycle"):
            closure([common, other])

    def test_selection_binding_ids_are_unique_and_authority_is_explicit(self):
        binding = {"id": "rules", "package": "common", "resources": ["index"], "use_as": "normative-rule",
                   "selector": {"capabilities": ["review"], "operations": ["review"], "path_prefixes": ["."],
                                "technology_profile": None, "file_types": ["python"], "execution_modes": ["local"]},
                   "authorities": [{"path": "AGENTS.md", "sha256": SHA, "selector": "rules"}],
                   "required_rule_ids": ["RULE-1"], "required_for_coverage": True}
        good = {**selection(), "bindings": [binding]}
        desired_shape(good)
        for bad, diagnostic in [
            (changed(good, ("bindings",), [binding, {**binding, "required_for_coverage": False}]), "duplicate identity"),
            (changed(good, ("bindings", 0, "authorities"), []), "normative authority/rules"),
        ]:
            distribution_validator("selection").validate(bad)
            with self.assertRaisesRegex(DistributionError, diagnostic):
                desired_shape(bad)


if __name__ == "__main__":
    unittest.main()
