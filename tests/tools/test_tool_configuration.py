"""Configuration precedence, declared package binding and read-only explanation."""
import copy

from .tool_fixtures import FAMILIES, ToolCase, encoded, package, tool


class ConfigurationTests(ToolCase):
    def explanation(self, family, **options):
        binding = self.binding(family, "explain", **options)
        return binding["explanation"] if family == "problem-frame-author" else binding.explain()

    def test_defaults_do_not_create_store_or_claim_runtime_capability(self):
        roots = {"lesson-author": "notes/lessons", "adr-author": "notes/adrs",
                 "local-backlog": "notes/work-items", "pr-author": "notes/pull-requests",
                 "problem-frame-author": "specs/problem-frames"}
        for family in FAMILIES:
            with self.subTest(family=family):
                explained = self.explanation(family)
                self.assertEqual(explained["settings"]["store"]["root"], roots[family])
                self.assertEqual(explained["settings"]["store"]["tracking"], "tracked")
                self.assertEqual(explained["runtime_capability"], "not-probed")
                self.assertEqual(explained["tracking"], "intent-only")
                self.assertFalse((self.project / roots[family]).exists())
        self.assertEqual(list(self.project.iterdir()), [])

    def test_project_local_invocation_precedence_without_saving(self):
        for family in FAMILIES:
            with self.subTest(family=family):
                defaults = self.explanation(family)["settings"]
                original = copy.deepcopy(defaults)
                view = self.project / "view.md"
                view.write_bytes((package(family) / defaults["template"]["path"]).read_bytes())
                selected = {"store": {"tracking": "ignored"}, "template": {"origin": "project", "path": "view.md"}}
                project = self.write_json("project.json", {"config_version": 2, "skills": {
                    family: selected, "foreign.inert": {"unknown": None}}})
                local = self.write_json("local.json", {"config_version": 2, "skills": {
                    family: {"store": {"tracking": "tracked"}, "template": defaults["template"]}}})
                before = {path: path.read_bytes() for path in (project, local, view)}
                explained = self.explanation(family, project_config=str(project), local_config=str(local))
                self.assertEqual(explained["settings"], defaults)
                explained = self.explanation(family, project_config=str(project), local_config=str(local), overrides=selected)
                self.assertEqual(explained["settings"]["template"], {"origin": "project", "path": "view.md"})
                self.assertEqual(explained["settings"]["store"]["tracking"], "ignored")
                self.assertNotIn("foreign.inert", explained["settings"])
                self.assertEqual(defaults, original)
                self.assertEqual({path: path.read_bytes() for path in before}, before)
                self.assertFalse((self.project / defaults["store"]["root"]).exists())

    def test_locked_fields_and_write_roots_reject_broader_overrides(self):
        for family in FAMILIES:
            module = tool(family)
            with self.subTest(family=family):
                config = self.write_json("project.json", {"config_version": 2,
                    "constraints": {family: {"locked_fields": ["store.tracking"]}}})
                self.assert_fault(module, lambda: self.explanation(family, project_config=str(config),
                    overrides={"store": {"tracking": "ignored"}}), "blocked", "locked-field")
                root = self.explanation(family)["settings"]["store"]["root"]
                self.assert_fault(module, lambda: self.explanation(family,
                    write_roots=[str(self.project / root / "narrow")]), "blocked")
                self.assert_fault(module, lambda: self.explanation(family,
                    overrides={"store": {"root": str(self.project.parent / "outside")}}), "blocked")

    def test_invalid_selected_configuration_is_not_ignored(self):
        for family in FAMILIES:
            module = tool(family)
            for raw, outcome in [
                (b'{"config_version":2,"config_version":2}', "invalid-input"),
                (encoded({"config_version": True}), "unsupported-version" if family == "problem-frame-author" else "unsupported"),
                (encoded({"config_version": 2.0}), "unsupported-version" if family == "problem-frame-author" else "unsupported"),
                (encoded({"config_version": 2, "skills": {family: None}}), "invalid-input"),
                (encoded({"config_version": 2, "skills": {family: {"unknown": True}}}), "invalid-input"),
            ]:
                with self.subTest(family=family, raw=raw):
                    path = self.project / "invalid.json"
                    path.write_bytes(raw)
                    self.assert_fault(module, lambda: self.explanation(family, project_config=str(path)), outcome)
                    self.assertEqual(path.read_bytes(), raw)

    def test_template_must_be_declared_or_explicitly_selected_from_project(self):
        for family in FAMILIES:
            with self.subTest(family=family):
                self.assert_fault(tool(family), lambda: self.explanation(family,
                    overrides={"template": {"origin": "package", "path": "templates/undeclared.md"}}))

    def test_lesson_legacy_config_is_explicit_and_versions_cannot_mix(self):
        project = self.write_json("legacy.json", {"config_version": 1, "skills": {"lesson-author": {}}})
        local = self.write_json("local.json", {"config_version": 2})
        self.assertEqual(self.explanation("lesson-author", project_config=str(project))["config_version"], 1)
        self.assert_fault(tool("lesson-author"), lambda: self.explanation("lesson-author",
            project_config=str(project), local_config=str(local)), code="config-version")
