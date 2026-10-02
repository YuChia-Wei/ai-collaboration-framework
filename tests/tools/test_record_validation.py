"""Real schema and semantic validators over small independent record fixtures."""
import copy

from .tool_fixtures import FAMILIES, ToolCase, cbf_record, digest, encoded, record, tool


def changed(value, path, replacement):
    result = copy.deepcopy(value)
    node = result
    for key in path[:-1]:
        node = node[key]
    node[path[-1]] = replacement
    return result


class RecordValidationTests(ToolCase):
    def test_closed_records_reject_missing_fields_unknown_fields_and_versions(self):
        for family in FAMILIES[:-1]:
            module, binding = self.provision(family)
            value = record(family)
            module.validate_record(binding, value, value["id"])
            without_title = copy.deepcopy(value)
            del (without_title["content"] if "content" in without_title else without_title)["title"]
            cases = [(without_title, "invalid-input"), ({**value, "unknown": 1}, "invalid-input"),
                     ({**value, "schema_version": "99.0.0"}, "unsupported"),
                     ({**value, "updated_at": "2025-01-01T00:00:00+00:00"}, "invalid-input"),
                     ({**value, "created_at": "yesterday"}, "invalid-input"),
                     ({**value, "extensions": {"undotted": True}}, "invalid-input")]
            for invalid, outcome in cases:
                with self.subTest(family=family, invalid=invalid):
                    before = copy.deepcopy(invalid)
                    self.assert_fault(module, lambda: module.validate_record(binding, invalid), outcome)
                    self.assertEqual(invalid, before)
            with self.subTest(family=family, case="filename mismatch"):
                self.assert_fault(module, lambda: module.validate_record(binding, value, "other"), code="record-identity")

    def test_lesson_requires_evidence_for_supported_confidence(self):
        module, binding = self.provision("lesson-author")
        value = record("lesson-author")
        invalid = changed(value, ["content", "evidence"], [])
        self.assert_fault(module, lambda: module.validate_record(binding, invalid))
        invalid["content"]["confidence"] = "tentative"
        self.assertEqual(module.validate_record(binding, invalid), invalid)

    def test_adr_requires_distinct_real_alternatives(self):
        module, binding = self.provision("adr-author")
        value = record("adr-author")
        for path, replacement in [(["content", "options"], [value["content"]["options"][0]]),
                                  (["content", "options", 1, "id"], "A"),
                                  (["content", "decision_drivers"], [])]:
            invalid = changed(value, path, replacement)
            with self.subTest(path=path):
                self.assert_fault(module, lambda: module.validate_record(binding, invalid))

    def test_lifecycle_revision_and_history_are_semantically_bound(self):
        for family in ("lesson-author", "adr-author"):
            module, binding = self.provision(family)
            initial = record(family)
            value = copy.deepcopy(initial)
            value.update(status="retired", revision=2, updated_at="2026-01-02T00:00:00+00:00")
            value["history"] = [{"from_revision": 1, "operation": "retire", "recorded_at": value["updated_at"],
                                 "reason": "Historical observation", "previous_sha256": digest(encoded(initial)),
                                 "previous_status": initial["status"], "previous_state": {
                                     "content": initial["content"], "successor": None, "decision": None}}]
            module.validate_record(binding, value)
            for path, replacement in [(["revision"], True), (["revision"], 3),
                                      (["history", 0, "from_revision"], 2),
                                      (["history", 0, "recorded_at"], initial["created_at"]),
                                      (["history", 0, "operation"], "revise"),
                                      (["history", 0, "previous_state", "content", "title"], "Changed during retirement")]:
                invalid = changed(value, path, replacement)
                with self.subTest(family=family, path=path):
                    self.assert_fault(module, lambda: module.validate_record(binding, invalid))
            output = module.render(binding, value)
            for expected in ("Status: retired", "Historical observation", "&quot;operation&quot;: &quot;retire&quot;",
                             "&quot;previous\\_status&quot;:", digest(encoded(initial))):
                self.assertIn(expected, output)

    def test_pr_validation_must_bind_selected_subject_and_actual_result_evidence(self):
        module, binding = self.provision("pr-author")
        value = record("pr-author")
        cases = [(["validation", 0, "subject_head"], "a" * 40, "conflict", "validation-subject"),
                 (["validation", 0, "subject_diff_sha256"], "e" * 64, "conflict", "validation-subject"),
                 (["validation"], value["validation"] * 2, "invalid-input", "validation-id"),
                 (["validation", 0, "disposition"], "succeeded", "invalid-input", "record-schema"),
                 (["subject", "object_format"], "sha256", "invalid-input", "record-schema")]
        for path, replacement, outcome, code in cases:
            invalid = changed(value, path, replacement)
            with self.subTest(path=path):
                self.assert_fault(module, lambda: module.validate_record(binding, invalid), outcome, code)

    def test_cbf_inventory_contains_assertion_pointers_and_unresolved_links(self):
        module, binding = self.provision("problem-frame-author")
        value = cbf_record()
        raw = encoded(value)
        result = module.validate_structure(value, raw, binding["validator"])
        self.assertEqual(result["counts"], {"statement": 3, "scenario": 1, "assertion": 1})
        self.assertEqual(result["unresolved_ids"], ["THEN1"])
        self.assertEqual(result["source_ids"], ["SRC1"])
        self.assertEqual(result["question_ids"], ["Q1"])
        self.assertEqual(result["subject_sha256"], digest(raw))
        self.assertEqual(result["criterion_inventory"], [
            {"id": "ACTOR1", "kind": "statement", "pointer": "/statements/0", "scenario_id": None},
            {"id": "CMD1", "kind": "statement", "pointer": "/statements/1", "scenario_id": None},
            {"id": "DOMAIN1", "kind": "statement", "pointer": "/statements/2", "scenario_id": None},
            {"id": "SC1", "kind": "scenario", "pointer": "/scenarios/0", "scenario_id": "SC1"},
            {"id": "THEN1", "kind": "assertion", "pointer": "/scenarios/0/then/0", "scenario_id": "SC1"}])

    def test_cbf_rejects_dangling_duplicate_unresolved_and_untyped_references(self):
        module, binding = self.provision("problem-frame-author")
        value = cbf_record()
        cases = [(["family"], "unknown", "unsupported-family"),
                 (["schema_version"], "9.0.0", "unsupported-version"),
                 (["sources"], value["sources"] * 2, "invalid-input"),
                 (["statements", 1, "id"], "ACTOR1", "invalid-input"),
                 (["statements", 0, "category"], "fact", "invalid-input"),
                 (["statements", 0, "source_ids"], ["MISSING"], "invalid-input"),
                 (["scenarios", 0, "then", 0, "statement_ids"], ["SRC1"], "invalid-input"),
                 (["open_questions"], [], "invalid-input"),
                 (["open_questions", 0, "related_ids"], ["SRC1"], "invalid-input"),
                 (["derived_from"], "MISSING", "invalid-input"),
                 (["sources", 0, "authority"], "normative", "invalid-input")]
        for path, replacement, outcome in cases:
            invalid = changed(value, path, replacement)
            with self.subTest(path=path, replacement=replacement):
                self.assert_fault(module, lambda: module.validate_structure(invalid, encoded(invalid), binding["validator"]), outcome)

    def test_json_duplicate_keys_and_nonfinite_numbers_are_refused(self):
        for family in FAMILIES:
            module = tool(family)
            for raw in (b'{"id":1,"id":2}', b'{"value":NaN}', b'{"value":Infinity}'):
                with self.subTest(family=family, raw=raw):
                    action = (lambda: module.decode(raw, "fixture")) if family == "problem-frame-author" else lambda: module.parse_json(raw)
                    self.assert_fault(module, action)
