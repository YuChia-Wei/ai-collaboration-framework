"""Seven source record contracts, including legacy and unpublished formats.

Calling the actual in-memory validators establishes data behavior only. It does
not publish standards-promotion or claim installation, adoption, or agent quality.
"""
from copy import deepcopy
import json
from types import SimpleNamespace
import unittest

from schemas.schema_support import (
    RECORDS, OID, SHA, cbf, changed, record_examples, record_tool, record_validator,
)


def validate_record(name, record, expected_id=None):
    tool = record_tool(name)
    selected = record_validator(name)
    if name == "cbf":
        return tool.validate_structure(record, json.dumps(record).encode("utf-8"), selected)
    binding = SimpleNamespace(validator=selected, validators={record["schema_version"]: selected})
    return tool.validate_record(binding, record, expected_id=expected_id)


class RecordSchemaTests(unittest.TestCase):
    def test_every_schema_and_owned_validator_accepts_representative_data(self):
        examples = record_examples()
        self.assertEqual(set(examples), set(RECORDS))
        for name, value in examples.items():
            with self.subTest(schema=name):
                record_validator(name).validate(value)
                self.assertIsNotNone(validate_record(name, value))

    def test_required_field_type_version_and_closed_object_for_every_schema(self):
        for name, value in record_examples().items():
            missing = deepcopy(value)
            del missing["schema_version"]
            cases = {"missing": missing, "unknown-field": {**value, "undeclared": True},
                     "version": {**value, "schema_version": "99.0.0"}, "type": {**value, "id": 17}}
            for condition, bad in cases.items():
                with self.subTest(schema=name, condition=condition):
                    self.assertFalse(record_validator(name).is_valid(bad))
                    # Bind the owned schema independently of the invalid version.
                    tool = record_tool(name)
                    with self.assertRaises(tool.Fault):
                        if name == "cbf":
                            validate_record(name, bad)
                        else:
                            binding = SimpleNamespace(validator=record_validator(name),
                                                      validators={value["schema_version"]: record_validator(name)})
                            tool.validate_record(binding, bad)

    def test_each_record_rejects_invalid_enum_and_empty_required_content(self):
        fields = {
            "adr": (("status",), "published", ("content", "title")),
            "lesson": (("content", "confidence"), "certain", ("content", "title")),
            "legacy-lesson": (("status",), "accepted", ("title",)),
            "backlog": (("state",), "merged", ("title",)),
            "pr": (("state",), "merged", ("title",)),
            "cbf": (("sources", 0, "authority"), "accepted", ("title",)),
            "promotion": (("status",), "adopted", ("content", "title")),
        }
        for name, original in record_examples().items():
            enum_path, enum_value, text_path = fields[name]
            for path, value in [(enum_path, enum_value), (text_path, "")]:
                bad = changed(original, path, value)
                with self.subTest(schema=name, path=path):
                    self.assertFalse(record_validator(name).is_valid(bad))
                    with self.assertRaises(record_tool(name).Fault):
                        validate_record(name, bad)

    def test_record_extensions_are_opt_in_namespaced_and_nested_shapes_are_closed(self):
        for name, original in record_examples().items():
            if name == "cbf":
                continue  # CBF deliberately has no extension escape hatch.
            good = {**original, "extensions": {"project.fixture": {"detail": True}}}
            record_validator(name).validate(good)
            validate_record(name, good)
            bad = {**original, "extensions": {"unnamespaced": True}}
            with self.subTest(schema=name):
                self.assertFalse(record_validator(name).is_valid(bad))
        for name, path in [("adr", ("content", "extra")), ("lesson", ("content", "extra")),
                           ("promotion", ("content", "baseline", "extra")),
                           ("pr", ("subject", "extra")), ("cbf", ("sources", 0, "extra"))]:
            with self.subTest(schema=name, path=path):
                self.assertFalse(record_validator(name).is_valid(changed(record_examples()[name], path, 1)))

    def test_timestamps_are_zoned_and_runtime_requires_chronological_order(self):
        for name, value in record_examples().items():
            if name == "cbf":
                continue
            bad = {**value, "updated_at": "2026-10-01T23:59:59+00:00"}
            with self.subTest(schema=name):
                record_validator(name).validate(bad)
                with self.assertRaises(record_tool(name).Fault):
                    validate_record(name, bad)
                # The runtime always checks timezone information, including
                # hosts without jsonschema's optional date-time dependency.
                with self.assertRaises(record_tool(name).Fault):
                    validate_record(name, {**value, "created_at": "2026-10-02T00:00:00"})

    def test_lifecycle_revisions_require_exact_integers_and_retained_history(self):
        for name in ("adr", "lesson", "promotion"):
            value = record_examples()[name]
            for revision in (1.0, 2):
                bad = {**value, "revision": revision}
                with self.subTest(schema=name, revision=revision):
                    record_validator(name).validate(bad)
                    with self.assertRaises(record_tool(name).Fault):
                        validate_record(name, bad)
            for revision in (True, 0):
                self.assertFalse(record_validator(name).is_valid({**value, "revision": revision}))

    def test_legacy_and_current_lesson_evidence_conditions(self):
        examples = record_examples()
        for name in ("legacy-lesson", "lesson"):
            path = () if name == "legacy-lesson" else ("content",)
            unsupported = changed(examples[name], (*path, "confidence"), "supported")
            self.assertFalse(record_validator(name).is_valid(unsupported))
            supported = changed(unsupported, (*path, "evidence"), [{"source": "log.txt", "note": "Observed result"}])
            record_validator(name).validate(supported)
            validate_record(name, supported)
        self.assertFalse(record_validator("lesson").is_valid(examples["legacy-lesson"]))
        self.assertFalse(record_validator("legacy-lesson").is_valid(examples["lesson"]))

    def test_adr_option_identity_and_decision_reference_use_actual_semantics(self):
        good = record_examples()["adr"]
        tool = record_tool("adr")
        tool.check_option(good["content"], "accept", "files")
        tool.check_option(good["content"], "reject", None)
        bad = changed(good, ("content", "options", 1, "id"), "files")
        record_validator("adr").validate(bad)
        with self.assertRaises(tool.Fault):
            validate_record("adr", bad)
        for decision, option in [("accept", "absent"), ("reject", "files")]:
            with self.subTest(decision=decision), self.assertRaises(tool.Fault):
                tool.check_option(good["content"], decision, option)
        self.assertFalse(record_validator("adr").is_valid({**good, "status": "accepted"}))

    def test_completion_and_validation_evidence_cannot_be_claimed_empty(self):
        examples = record_examples()
        completed = {**examples["backlog"], "state": "completed"}
        self.assertFalse(record_validator("backlog").is_valid(completed))
        completed["completion_evidence"] = [{"source": "check.log", "note": "Outcome observed"}]
        validate_record("backlog", completed)
        self.assertFalse(record_validator("backlog").is_valid({**completed, "state": "draft"}))
        check = {"id": "focused", "command": "fixture-only", "disposition": "succeeded", "subject_head": OID,
                 "subject_diff_sha256": SHA, "evidence": [], "reason": "Focused check"}
        pr = {**examples["pr"], "validation": [check]}
        self.assertFalse(record_validator("pr").is_valid(pr))
        check["evidence"] = [{"source": "check.log", "note": "Outcome observed"}]
        validate_record("pr", pr)

    def test_pr_validation_ids_and_subjects_are_bound(self):
        row = {"id": "focused", "command": "fixture-only", "disposition": "planned", "subject_head": OID,
               "subject_diff_sha256": SHA, "evidence": [], "reason": "Awaiting execution"}
        value = {**record_examples()["pr"], "validation": [row]}
        validate_record("pr", value)
        for bad in [changed(value, ("validation",), [row, {**row, "reason": "Same check ID"}]),
                    changed(value, ("validation", 0, "subject_head"), "d" * 40),
                    changed(value, ("validation", 0, "subject_diff_sha256"), "d" * 64)]:
            record_validator("pr").validate(bad)
            with self.assertRaises(record_tool("pr").Fault):
                validate_record("pr", bad)

    def test_work_github_references_stay_reference_only(self):
        for name in ("backlog", "pr"):
            reference = {"kind": "github-issue", "target": "https://github.com/owner/repo/issues/1", "relationship": "reference-only"}
            good = {**record_examples()[name], "references": [reference]}
            validate_record(name, good)
            for field, replacement in [("relationship", "implements"), ("target", "https://example.invalid/issues/1")]:
                with self.subTest(schema=name, field=field):
                    self.assertFalse(record_validator(name).is_valid(changed(good, ("references", 0, field), replacement)))

    def test_pr_object_format_selects_hash_length(self):
        value = record_examples()["pr"]
        for object_format, length in [("sha1", 40), ("sha256", 64)]:
            good = deepcopy(value)
            good["subject"]["object_format"] = object_format
            for field in ("base_commit", "head_commit", "merge_base", "base_tree", "head_tree"):
                good["subject"][field] = "b" * length
            validate_record("pr", good)
            bad = changed(good, ("subject", "head_commit"), "b" * (64 if length == 40 else 40))
            self.assertFalse(record_validator("pr").is_valid(bad))

    def test_unpublished_promotion_binds_content_and_snapshot_bytes(self):
        value = record_examples()["promotion"]
        for path, replacement in [(("content", "replacement"), "changed"),
                                  (("content", "baseline", "utf8"), "drifted"),
                                  (("content", "target_id"), "another-rule")]:
            bad = changed(value, path, replacement)
            record_validator("promotion").validate(bad)
            with self.subTest(path=path), self.assertRaises(record_tool("promotion").Fault):
                validate_record("promotion", bad)
        self.assertFalse(record_validator("promotion").is_valid({**value, "status": "superseded"}))


class ProblemFrameReferenceTests(unittest.TestCase):
    def test_valid_inventory_preserves_typed_criteria(self):
        result = validate_record("cbf", cbf())
        self.assertEqual(result["counts"], {"statement": 3, "scenario": 1, "assertion": 1})
        self.assertEqual(result["source_ids"], ["requirement"])

    def test_unique_ids_across_sources_and_criterion_kinds(self):
        value = cbf()
        for bad in [changed(value, ("sources",), value["sources"] * 2),
                    changed(value, ("scenarios", 0, "id"), "actor"),
                    changed(value, ("scenarios", 0, "then", 0, "id"), "command"),
                    changed(value, ("open_questions",), [{"id": "domain", "text": "Question", "related_ids": []}])]:
            record_validator("cbf").validate(bad)
            with self.assertRaises(record_tool("cbf").Fault):
                validate_record("cbf", bad)

    def test_cross_references_require_the_correct_local_target_kind(self):
        value = cbf()
        for path, replacement in [(("statements", 0, "source_ids"), ["missing"]),
                                  (("scenarios", 0, "source_ids"), ["actor"]),
                                  (("scenarios", 0, "then", 0, "statement_ids"), ["requirement"]),
                                  (("derived_from",), "missing"),
                                  (("open_questions",), [{"id": "question", "text": "Clarify", "related_ids": ["requirement"]}])]:
            bad = changed(value, path, replacement)
            record_validator("cbf").validate(bad)
            with self.subTest(path=path), self.assertRaises(record_tool("cbf").Fault):
                validate_record("cbf", bad)

    def test_unresolved_claim_needs_a_question_and_required_domain_categories(self):
        bad = changed(cbf(), ("statements", 0, "basis"), "unresolved")
        record_validator("cbf").validate(bad)
        with self.assertRaises(record_tool("cbf").Fault):
            validate_record("cbf", bad)
        good = {**bad, "open_questions": [{"id": "question", "text": "Confirm actor", "related_ids": ["actor"]}]}
        self.assertEqual(validate_record("cbf", good)["unresolved_ids"], ["actor"])
        bad = changed(cbf(), ("statements", 2, "category"), "fact")
        record_validator("cbf").validate(bad)
        with self.assertRaises(record_tool("cbf").Fault):
            validate_record("cbf", bad)

    def test_text_and_array_budgets_and_normative_authority(self):
        value = cbf()
        record_validator("cbf").validate({**value, "title": "x" * 16384})
        for path, replacement in [(("title",), "x" * 16385), (("title",), "  "),
                                  (("scenarios", 0, "given"), ["step"] * 1025),
                                  (("sources", 0, "authority"), "normative"),
                                  (("statements", 0, "source_ids"), []),
                                  (("statements", 0, "source_ids"), ["requirement", "requirement"])]:
            with self.subTest(path=path):
                self.assertFalse(record_validator("cbf").is_valid(changed(value, path, replacement)))


if __name__ == "__main__":
    unittest.main()
