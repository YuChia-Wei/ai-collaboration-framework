"""Content oracles for delivered templates, independent of production rendering."""
import copy
from types import SimpleNamespace

from .tool_fixtures import FAMILIES, ToolCase, cbf_record, package, record, tool


class RendererTests(ToolCase):
    def rendered(self, family):
        module, binding = self.provision(family)
        value = record(family)
        before = copy.deepcopy(value)
        template = binding["template"] if family == "problem-frame-author" else binding.template
        template_path = package(family) / "templates" / {
            "lesson-author": "lesson.md", "adr-author": "adr.md", "local-backlog": "work-item.md",
            "pr-author": "pr.md", "problem-frame-author": "cbf.md"}[family]
        template_bytes = template_path.read_bytes()
        if family == "problem-frame-author":
            module.validate_structure(value, b"fixed subject", binding["validator"])
            output = module.render_record(value, template)
            repeated = module.render_record(value, template)
        else:
            module.validate_record(binding, value)
            output = module.render(binding, value)
            repeated = module.render(binding, value)
        self.assertEqual(output, repeated)
        self.assertEqual(value, before)
        self.assertEqual(template_path.read_bytes(), template_bytes)
        self.assertEqual(binding["template"] if family == "problem-frame-author" else binding.template, template)
        self.assertNotIn("{{", output)
        return output

    def test_lesson_authored_fields_and_lifecycle_sections(self):
        output = self.rendered("lesson-author")
        expected = [r"# 觀察 \*重試\* &lt;tag&gt;", r"Record: lesson\-" + "1" * 32,
                    r"Schema: 2\.0\.0 | Status: candidate", "First observation\nSecond observation",
                    "## Evidence", "fixture:evidence", "Observed once", "## Conclusion\n\nKeep the original outcome",
                    "## Applies When", "Local caller", "## Does Not Apply When\n\n\\[\\]",
                    "## Confidence\n\nsupported", "## Follow Up", "Repeat with evidence",
                    "## Decision\n\nNone supplied", "## Provenance\n\n\\[\\]", "## History\n\n\\[\\]",
                    "Acceptance is not project rule adoption or implementation verification."]
        for text in expected:
            with self.subTest(text=text):
                self.assertIn(text, output)

    def test_legacy_lesson_v1_preserves_observation_and_original_record(self):
        current = record("lesson-author")
        legacy = {key: current[key] for key in ("kind", "owner", "id", "status", "created_at", "updated_at")}
        legacy.update(schema_version="1.0.0", **current["content"])
        legacy["observation"] = "舊版 observation *retained*\nSecond observation"
        module, binding, value, path = self.persist("lesson-author", legacy)
        original_bytes = path.read_bytes()
        original_data = copy.deepcopy(value)
        original_template = binding.template_path.read_bytes()
        validated = module.validate_record(binding, value, value["id"])
        self.assertTrue(module.is_legacy(validated))
        output = module.render(binding, validated)
        self.assertIn("## Observation\n\n舊版 observation \\*retained\\*\nSecond observation\n", output)
        self.assertIn(r"Schema: 1\.0\.0 | Status: candidate", output)
        self.assertIn(r"Legacy schema: no lifecycle history; preserved read\-only\.", output)
        self.assertIn(r"Legacy schema: no derived provenance; preserved read\-only\.", output)
        self.assertEqual(value, original_data)
        self.assertEqual(path.read_bytes(), original_bytes)
        self.assertEqual(binding.template_path.read_bytes(), original_template)

    def test_adr_renders_alternatives_costs_evidence_and_empty_fields(self):
        output = self.rendered("adr-author")
        for text in [r"# 選擇 \*方案\* &lt;tag&gt;", "Status: draft", "First context\nSecond context",
                     "Keep evidence", "Retain local state", "Use remote state", "Offline access", "Network required",
                     "&quot;benefits&quot;: \\[\\]", "&quot;costs&quot;: \\[\\]", "One source of truth",
                     "fixture:comparison", "Both evaluated", "Single owner", "## Does Not Apply When\n\n\\[\\]",
                     "## Decision\n\nNone supplied", "## Provenance\n\n\\[\\]", "## History\n\n\\[\\]"]:
            with self.subTest(text=text):
                self.assertIn(text, output)

    def test_backlog_markdown_lists_indent_multiline_items(self):
        output = self.rendered("local-backlog")
        self.assertIn(r"# 工作 \*項目\* &lt;tag&gt;", output)
        self.assertIn("First summary\nSecond summary", output)
        self.assertIn("State: draft\n\nReason: Created as candidate work\\.", output)
        self.assertIn("## Acceptance\n\n- Keep state\n  Keep evidence", output)
        self.assertIn("## Completion evidence\n\nNone supplied", output)
        self.assertIn("- kind: text; target: fixture:reference; relationship: related", output)

    def test_pr_includes_entire_selected_subject_and_deferred_evidence(self):
        output = self.rendered("pr-author")
        for text in ["object\\_format: sha1", "base\\_commit: " + "a" * 40, "head\\_commit: " + "b" * 40,
                     "merge\\_base: " + "a" * 40, "base\\_tree: " + "c" * 40, "head\\_tree: " + "d" * 40,
                     "diff\\_sha256: " + "f" * 64, "git\\_version: fixture git", "diff\\_recipe: pr\\.diff/v1",
                     "id: V1; command: python check; disposition: deferred", "evidence: None supplied",
                     "reason: Await caller evidence", "fixture:reference"]:
            with self.subTest(text=text):
                self.assertIn(text, output)

    def test_cbf_recursive_body_includes_all_nested_record_sections(self):
        output = self.rendered("problem-frame-author")
        # Fixed expected lines cover every field of the authored fixture, including
        # nulls, arrays, nested assertions and test anchors. Do not derive this list
        # by walking the input with the same algorithm as render_record.
        expected = [r"# 問題 \*框架\* &lt;tag&gt;", "- Snapshot", "  - family: problem\\-frame\\.cbf",
                    "  - schema\\_version: 1\\.0\\.0", "  - id: cbf\\-" + "1" * 32,
                    "  - frame\\_key: fixture\\-frame", "  - derived\\_from: null", "  - sources",
                    "      - id: SRC1", "      - kind: requirement", "      - reference: fixture:intent",
                    "      - revision: null", "      - locator: Intent section", "      - sha256: null",
                    "      - authority: proposed", "      - authority\\_reference: null", "  - statements",
                    "      - id: ACTOR1", "      - category: actor", "      - text: A caller",
                    "      - id: CMD1", "      - category: command", "      - text: Request a value",
                    "      - id: DOMAIN1", "      - category: controlled\\-domain", "      - text: Local state",
                    "      - basis: stated", "      - source\\_ids\n        - 0: SRC1", "  - scenarios",
                    "      - id: SC1", "      - title: Observe one result", "      - given\n        - 0: First line<br>\nSecond line",
                    "      - when\n        - 0: Caller requests", "      - then", "          - id: THEN1",
                    "          - text: Exact value unresolved", "          - basis: unresolved",
                    "          - source\\_ids: []", "          - statement\\_ids\n            - 0: CMD1",
                    "      - tests\\_anchor", "          - reference: fixture:test", "          - locator: Case one",
                    "  - open\\_questions", "      - id: Q1", "      - text: Which value?",
                    "      - related\\_ids\n        - 0: THEN1"]
        for text in expected:
            with self.subTest(text=text):
                self.assertIn(text, output)

    def test_plain_text_is_escaped_and_never_interpreted_as_template(self):
        raw = '<b> & "quoted" [link](url) `code` | \\ * _ {{title}}\n尾'
        expected = r'&lt;b&gt; &amp; &quot;quoted&quot; \[link\]\(url\) \`code\` \| \\ \* \_ \{\{title\}\}' + "\n尾"
        for family in FAMILIES[:-1]:
            with self.subTest(family=family):
                module, binding = self.provision(family)
                value = record(family)
                (value["content"] if "content" in value else value)["title"] = raw
                self.assertIn("# " + expected + "\n", module.render(binding, value))
        cbf = tool("problem-frame-author")
        self.assertEqual(cbf.escaped("甲\r\n乙 <tag> [x]"), "甲&#13;<br>\n乙 &lt;tag&gt; \\[x\\]")

    def test_required_unknown_and_malformed_template_tokens(self):
        for family in FAMILIES[:-1]:
            module, binding = self.provision(family)
            value = record(family)
            required = ({"id", "schema_version", "status", "history", "provenance", *module.AUTHORED}
                        if family in ("lesson-author", "adr-author") else set(module.VIEW_FIELDS))
            if family == "adr-author":
                required.add("decision")
            invalid = [binding.template.replace("{{" + key + "}}", "") for key in sorted(required)]
            invalid += [binding.template + token for token in ("{{unknown}}", "{{Title}}", "{{ title }}", "{{title", "title}}")]
            for index, template in enumerate(invalid):
                with self.subTest(family=family, invalid=index):
                    operation = (lambda: module.render(SimpleNamespace(template=template), value)) if family in (
                        "lesson-author", "adr-author") else lambda: module.validate_template(template)
                    self.assert_fault(module, operation, code="template-token")
            repeated = binding.template + "\n{{title}}"
            if family in ("local-backlog", "pr-author"):
                module.validate_template(repeated)
            output = module.render(SimpleNamespace(template=repeated), value)
            self.assertEqual(output.count("&lt;tag&gt;"), 2)

    def test_cbf_requires_body_once_and_rejects_invalid_utf8(self):
        module = tool("problem-frame-author")
        for raw in (b"{{title}}", b"{{body}}{{body}}", b"{{body}}{{unknown}}", b"{{body}}{{ title }}",
                    b"{{body}}{{", b"{{body}}}}", b"\xef\xbb\xbf{{body}}", b"\xff{{body}}"):
            with self.subTest(raw=raw):
                self.assert_fault(module, lambda: module.template_text(raw))
        self.assertEqual(module.template_text(b"{{body}}"), "{{body}}")
