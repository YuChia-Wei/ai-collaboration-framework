"""Focused rc.2 adapter examples; execution remains a U001/P7 decision."""

from __future__ import annotations

from pathlib import Path
import unittest

from distribution import claude, codex
from distribution.data import DistributionError


ROOT = Path(__file__).resolve().parents[2]
CODEX_V2 = ROOT / "src/adapters/codex/skill-entry-v2.md.template"
CLAUDE_V2 = ROOT / "src/adapters/claude/skill-entry-v2.md.template"
CODEX_LEGACY = ROOT / "src/adapters/codex/skill-entry.md.template"
MEMBERS = {
    "SKILL.md": ".ai/core/skills/example/SKILL.md",
    "skill-package.yaml": ".ai/core/skills/example/skill-package.yaml",
    "references/guide.md": ".ai/core/skills/example/references/guide.md",
}


class Rc2AdapterCases(unittest.TestCase):
    def render(self, module, template, **overrides):
        values = {
            "template_bytes": template.read_bytes(),
            "package_id": "example",
            "package_version": "0.1.0",
            "description": "A quoted: \"example\"",
            "destinations": MEMBERS,
            "configuration": None,
        }
        values.update(overrides)
        return module.project_entry_v2(**values)

    def test_selected_members_and_runtime_roots(self):
        for module, template, expected in (
            (codex, CODEX_V2, ".agents/skills/aicf-example/SKILL.md"),
            (claude, CLAUDE_V2, ".claude/skills/aicf-example/SKILL.md"),
        ):
            with self.subTest(runtime=module.__name__):
                destination, raw = self.render(module, template)
                text = raw.decode("utf-8")
                self.assertEqual(expected, destination)
                self.assertIn('description: "A quoted: \\"example\\""', text)
                self.assertIn("../../../.ai/core/skills/example/SKILL.md", text)
                self.assertIn("../../../.ai/core/skills/example/skill-package.yaml", text)
                self.assertIn("../../../.ai/core/skills/example/references/guide.md", text)
                self.assertIn("optional missing package or resource", text)
                self.assertNotIn("unselected.md", text)

    def test_wrong_or_modified_template_rejected(self):
        for module, other in ((codex, CLAUDE_V2), (claude, CODEX_V2)):
            with self.subTest(runtime=module.__name__):
                with self.assertRaises(DistributionError):
                    self.render(module, other)
                with self.assertRaises(DistributionError):
                    self.render(module, other, template_bytes=other.read_bytes() + b"\n")

    def test_only_selected_skill_members_are_allowed(self):
        for module, template in ((codex, CODEX_V2), (claude, CLAUDE_V2)):
            with self.subTest(runtime=module.__name__):
                with self.assertRaises(DistributionError):
                    self.render(module, template, destinations={
                        **MEMBERS, "unselected.md": ".ai/core/skills/other/unselected.md"
                    })
                with self.assertRaises(DistributionError):
                    self.render(module, template, destinations={
                        "SKILL.md": MEMBERS["SKILL.md"]
                    })

    def test_legacy_codex_seam_stays_separate(self):
        destination, raw = codex.project_entry(
            CODEX_LEGACY.read_bytes(), "example", "0.1.0", "Example",
            MEMBERS, configuration=None
        )
        self.assertEqual(".agents/skills/framework-example/SKILL.md", destination)
        self.assertIn(b"name: framework-example", raw)
        self.assertNotIn(b"aicf-example", raw)


if __name__ == "__main__":
    unittest.main()