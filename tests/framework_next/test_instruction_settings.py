"""Closed instruction settings metadata, schema defaults and optional wrappers."""
from copy import deepcopy
from pathlib import Path
import json
import sys
import unittest

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "tests/framework_next")]
from distribution import codex, claude
from distribution.data import DistributionError, json_bytes, yaml_object
from distribution.git_source import Blob
from distribution.package import load_package, check_references
from framework_next.test_contracts import source_inventory, metadata

OWNER = "software-development-orchestrator"
SCHEMA = "schemas/issue-control-settings.schema.json"


class InstructionSettingsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.document = metadata(OWNER)
        cls.schema = json.loads((ROOT / "src/skills" / OWNER / SCHEMA).read_text(encoding="utf-8"))
        cls.validator = Draft202012Validator(cls.schema)

    def closure(self, document=None, schema=None):
        document = deepcopy(self.document if document is None else document)
        package = load_package(Blob("skill-package.yaml", "0" * 40, "100644", json_bytes(document)))
        blobs = {name: Blob(name, "0" * 40, "100644", (ROOT / "src/skills" / OWNER / name).read_bytes()) for name in package.members}
        if schema is not None:
            blobs[SCHEMA] = Blob(SCHEMA, "0" * 40, "100644", json_bytes(schema))
        return package, check_references(package, blobs)

    def test_source_instruction_settings_load_defaults_and_declared_closure(self):
        package, _ = self.closure()
        self.assertEqual(package.version, "0.5.0")
        self.assertEqual(package.metadata["configuration"]["defaults"], {"issue_control": ""})
        self.assertEqual(package.metadata["artifact_roles"], [])
        self.assertEqual(package.metadata["resources"]["tools"], [])
        self.assertIn(("skill", OWNER), source_inventory()[1])
        for owner in ("lesson-author", "adr-author", "pr-author", "problem-frame-author"):
            with self.subTest(owner=owner):
                document = metadata(owner)
                self.assertNotIn("kind", document["configuration"])
                load_package(Blob("skill-package.yaml", "0" * 40, "100644", json_bytes(document)))

    def test_all_three_settings_modes_have_schema_and_closure_parity(self):
        cases = ({}, {"issue_control": ""},
                 {"issue_control": {"mode": "experimental", "route": "issue-control"}},
                 {"issue_control": {"mode": "project", "route": ".agents/skills/team-ado/SKILL.md"}},
                 {"issue_control": {"mode": "project", "route": "mcp://team/tracker.operations"}})
        for settings in cases:
            with self.subTest(settings=settings):
                self.validator.validate(settings)
                document = deepcopy(self.document)
                document["configuration"]["defaults"] = settings
                self.closure(document)

    def test_invalid_modes_unknown_fields_and_inexact_routes_fail_closed(self):
        values = (None, False, [], " ", "issue-control", {},
                  {"mode": "default", "route": ""}, {"mode": "experimental", "route": "other"},
                  {"mode": "experimental"}, {"mode": "project", "route": ""},
                  {"mode": "project", "route": " leading"}, {"mode": "project", "route": "trailing "},
                  {"mode": "project", "route": "team\n"}, {"mode": "project", "route": "team\r\n"},
                  {"mode": "project", "route": "a\nb"}, {"mode": "project", "route": "a" * 4097},
                  {"mode": "project", "route": "team", "fallback": "local"})
        for value in values:
            with self.subTest(value=value):
                settings = {"issue_control": value}
                self.assertFalse(self.validator.is_valid(settings))
                document = deepcopy(self.document)
                document["configuration"]["defaults"] = settings
                with self.assertRaises(DistributionError):
                    self.closure(document)
        self.assertFalse(self.validator.is_valid({"unknown": ""}))

    def test_metadata_discriminator_schema_identity_and_default_shape_are_closed(self):
        for key, value in (("kind", "unknown"), ("namespace", "other"), ("schema", "settings"),
                           ("schema", {"id": "absent", "version": "1.0.0", "path": SCHEMA}),
                           ("schema", {"id": OWNER + ".settings", "version": "2.0.0", "path": SCHEMA}),
                           ("schema", {"id": OWNER + ".settings", "version": "1.0.0", "path": "other.json"}),
                           ("defaults", None), ("defaults", []), ("unknown", True)):
            with self.subTest(key=key, value=value):
                document = deepcopy(self.document)
                document["configuration"][key] = value
                with self.assertRaises(DistributionError):
                    self.closure(document)
        document = deepcopy(self.document)
        del document["configuration"]["kind"]
        with self.assertRaises(DistributionError):
            self.closure(document)
        document = metadata("pr-author")
        document["configuration"] = {**deepcopy(self.document["configuration"]), "namespace": "pr-author"}
        with self.assertRaises(DistributionError):
            load_package(Blob("skill-package.yaml", "0" * 40, "100644", json_bytes(document)))

    def test_unsupported_assertions_and_bad_patterns_fail_even_in_unused_union_arm(self):
        for assertion, value in (("enum", [""]), ("$ref", "https://example.invalid/schema"),
                                 ("not", {}), ("minimum", 0), ("additionalProperties", True)):
            schema = deepcopy(self.schema)
            schema["properties"]["issue_control"]["anyOf"][1][assertion] = value
            with self.subTest(assertion=assertion), self.assertRaises(DistributionError):
                self.closure(schema=schema)
        schema = deepcopy(self.schema)
        schema["properties"]["issue_control"]["anyOf"][2]["properties"]["route"]["pattern"] = "["
        with self.assertRaises(DistributionError):
            self.closure(schema=schema)

    def test_wrappers_describe_optional_settings_without_record_requirements(self):
        package, _ = self.closure()
        destinations = {name: ".ai/core/skills/" + OWNER + "/" + name for name in package.members}
        for aid, module in (("codex", codex), ("claude", claude)):
            with self.subTest(adapter=aid):
                _, raw = module.project_entry_v2((ROOT / "src/adapters" / aid / "skill-entry-v2.md.template").read_bytes(),
                    OWNER, "0.5.0", "Coordinate stages", destinations, configuration=self.document["configuration"])
                text = raw.decode("utf-8")
                self.assertIn("optional project-owned instruction settings", text)
                self.assertIn("an empty issue route is fully unspecified", text)
                self.assertIn("Do not create a configuration file or record store implicitly", text)
                self.assertNotIn("store.root", text)
                with self.assertRaises(DistributionError):
                    module.project_entry_v2((ROOT / "src/adapters" / aid / "skill-entry-v2.md.template").read_bytes(),
                        OWNER, "0.5.0", "Coordinate stages", destinations, configuration={"kind": "unknown"})


if __name__ == "__main__":
    unittest.main()
