"""Unpublished standards-promotion source renderer, not a delivered skill test.

Direct source behavior only: no distribution membership, adoption, publication
or runtime enforcement is asserted.
"""
import copy
from types import SimpleNamespace

from .tool_fixtures import ToolCase, digest, package, source_tool


class ExperimentalPromotionRendererTests(ToolCase):
    def proposal(self):
        module = source_tool("standards-promotion", "standards_promotion.py")
        target = self.project / "rule.md"
        target.write_bytes(b"Original rule\n")
        source = self.write_json("evidence/source.json", {"kind": "fixture", "id": "SRC1", "schema_version": "1.0.0"})
        config = self.write_json("project.json", {"config_version": 2, "constraints": {"standards-promotion": {
            "source_read_roots": ["evidence"], "targets": [{"id": "rule", "path": "rule.md", "applicability": "Local fixture",
                "allowed_actors": ["fixture owner"], "adoption_source": None, "effect_source": None}]}}})
        binding = module.Binding({"operation": "render", "project_root": str(self.project),
                                  "package_root": str(package("standards-promotion")), "project_config": str(config)})
        authored = {"title": "提案 *文字*", "target_id": "rule", "expected_target_sha256": digest(target.read_bytes()),
                    "replacement": "New rule\nSecond line", "rationale": "Preserve the bounded evidence", "applicability": "Local fixture",
                    "conflicts": [{"subject": "Old rule", "reason": "Explicit replacement", "disposition": "replace"}],
                    "sources": [{"path": str(source), "expected_sha256": digest(source.read_bytes()), "kind": "fixture",
                                 "id": "SRC1", "schema_version": "1.0.0", "reason": "Synthetic observation"}]}
        value = module.new_record(module.authored_content(binding, authored))
        module.validate_record(binding, value)
        return module, binding, value, target

    def test_complete_proposal_baseline_and_source_snapshots_are_visible(self):
        module, binding, value, target = self.proposal()
        before, target_before, template_before = copy.deepcopy(value), target.read_bytes(), binding.template
        rendered = module.render(binding, value)
        self.assertEqual(rendered, module.render(binding, value))
        self.assertEqual(value, before)
        self.assertEqual(target.read_bytes(), target_before)
        self.assertEqual(binding.template, template_before)
        for expected in (r"# 提案 \*文字\*", "Status: proposed", r"New rule\\nSecond line",
                         "Preserve the bounded evidence", "Local fixture", r"Original rule\\n", "Old rule",
                         "Explicit replacement", "replace", "SRC1", "Synthetic observation", "fixture owner",
                         "## Historical adoption, rule content and declared effect\n\nNone supplied",
                         "## Preserved history\n\n\\[\\]", "does not apply a rule or authenticate an actor"):
            with self.subTest(expected=expected):
                self.assertIn(expected, rendered)

    def test_experimental_template_cannot_omit_proposal_observation_or_history(self):
        module, binding, value, _ = self.proposal()
        invalid = [binding.template.replace("{{" + name + "}}", "") for name in
                   ("id", "schema_version", "status", "proposal", "observation", "history")]
        invalid.extend(binding.template + token for token in ("{{decision}}", "{{body}}", "{{ title }}", "{{"))
        for template in invalid:
            with self.subTest(template=template):
                self.assert_fault(module, lambda: module.render(SimpleNamespace(template=template), value), code="template-token")
