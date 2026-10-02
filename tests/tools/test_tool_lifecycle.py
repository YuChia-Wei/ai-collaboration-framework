"""Actual in-process operations with tiny local records and native publication.

Unsupported filesystems are reported as skips, never emulated successes. No Git
or provider integration is exercised by these record lifecycle tests.
"""
import copy

from .tool_fixtures import FAMILIES, ToolCase, cbf_record, content, digest, encoded, record, tool


class ReadOnlyTests(ToolCase):
    def test_inspect_validate_render_preserve_record_and_template_bytes(self):
        for family in FAMILIES[:-1]:
            with self.subTest(family=family):
                module, binding, value, path = self.persist(family)
                before, template = path.read_bytes(), binding.template_path.read_bytes()
                operations = ("inspect", "validate", "render") if family in ("lesson-author", "adr-author") else ("inspect", "render")
                for operation in operations:
                    result = module.execute(self.request(family, operation, reference=module.reference(value)))
                    self.assertEqual(result["outcome"], "succeeded", result)
                    self.assertEqual(result["sha256"], digest(before))
                    self.assertEqual(path.read_bytes(), before)
                    self.assertEqual(binding.template_path.read_bytes(), template)
                    if operation == "render":
                        self.assertIn("&lt;tag&gt;", result["view"]["markdown"])
                        if family == "pr-author":
                            self.assertFalse(result["subject_verified"])
                self.assertEqual([p.name for p in binding.store.iterdir()], [path.name])

    def test_cbf_read_checks_raw_digest_and_preserves_legacy_bytes(self):
        family = "problem-frame-author"
        module, binding, value, path = self.persist(family)
        before = path.read_bytes()
        inputs = module.Inputs()
        actual, raw, structure = module.read_record(inputs, path, binding["validator"], digest(before))
        self.assertEqual(actual, value)
        self.assertEqual(raw, before)
        self.assertEqual(structure["status"], "valid")
        inputs.recheck()
        self.assert_fault(module, lambda: module.read_record(module.Inputs(), path, binding["validator"], "0" * 64), "conflict", "digest")
        legacy = binding["store"] / "legacy.yaml"
        legacy.write_bytes(b"family: legacy\n")
        response = {}
        self.assert_fault(module, lambda: module.read_record(module.Inputs(), legacy, binding["validator"], response=response), "unsupported-format", "legacy")
        self.assertEqual(response["subject_sha256"], digest(b"family: legacy\n"))
        self.assertEqual(legacy.read_bytes(), b"family: legacy\n")
        self.assertEqual(path.read_bytes(), before)

    def test_queries_keep_malformed_records_as_partial_evidence(self):
        for family in ("lesson-author", "adr-author", "local-backlog", "pr-author"):
            with self.subTest(family=family):
                module, binding, value, path = self.persist(family)
                result = module.query(binding, "")
                self.assertFalse(result["partial"])
                self.assertEqual(len(result["matches"]), 1)
                bad = path.with_name(path.name.replace("1" * 32, "2" * 32))
                bad.write_bytes(b'{"schema_version":"99.0.0"}\n')
                result = module.query(binding, "")
                self.assertTrue(result["partial"])
                self.assertEqual(len(result["matches"]), 1)
                self.assertEqual(bad.read_bytes(), b'{"schema_version":"99.0.0"}\n')


class NativeLifecycleTests(ToolCase):
    def invoke(self, family, operation, expected="succeeded", **options):
        result = tool(family).execute(self.request(family, operation, **options))
        self.assertEqual(result["outcome"], expected, result)
        if expected != "succeeded":
            self.assertEqual(result["mutation_state"], "none", result)
        return result

    def create_knowledge(self, family):
        module, binding = self.provision(family)
        self.require_native(module, binding.store)
        query = self.invoke(family, "query", text="bounded fixture")
        created = self.invoke(family, "create", text="bounded fixture", content=content(family), decision={
            "action": "new", "query_sha256": query["query_sha256"], "acknowledge_partial": False,
            "reason": "A bounded fixture after the actual query"})
        path = binding.record_path(created["reference"])
        self.assertEqual(created["sha256"], digest(path.read_bytes()))
        return module, binding, created, path

    def knowledge_revision(self, family):
        module, binding, created, path = self.create_knowledge(family)
        original = path.read_bytes()
        revised_content = content(family)
        revised_content["title"] = "Revised fixture"
        lock = binding.store / ("." + module.FAMILY + "-write.lock")
        lock.write_bytes(b"existing writer\n")
        self.invoke(family, "revise", expected="conflict", reference=created["reference"],
                    expected_sha256=created["sha256"], content=revised_content, reason="Existing writer")
        self.assertEqual(path.read_bytes(), original)
        self.assertEqual(lock.read_bytes(), b"existing writer\n")
        lock.unlink()
        revised = self.invoke(family, "revise", reference=created["reference"], expected_sha256=created["sha256"],
                              content=revised_content, reason="New title")
        updated = path.read_bytes()
        inspected = self.invoke(family, "inspect", reference=created["reference"])["record"]
        self.assertEqual(inspected["revision"], 2)
        self.assertEqual(inspected["history"][0]["previous_state"]["content"], content(family))
        self.assertEqual(inspected["history"][0]["previous_sha256"], digest(original))
        self.invoke(family, "revise", expected="conflict", reference=created["reference"],
                    expected_sha256=created["sha256"], content=revised_content, reason="Stale subject")
        self.assertEqual(path.read_bytes(), updated)
        same = self.invoke(family, "revise", reference=created["reference"], expected_sha256=revised["sha256"],
                           content=revised_content, reason="No content change")
        self.assertFalse(same["changed"])
        self.assertEqual(path.read_bytes(), updated)
        retired = self.invoke(family, "retire", reference=created["reference"], expected_sha256=revised["sha256"], reason="Retained history")
        terminal = path.read_bytes()
        self.invoke(family, "revise", expected="invalid-input", reference=created["reference"],
                    expected_sha256=retired["sha256"], content=revised_content, reason="Refused after retirement")
        self.assertEqual(path.read_bytes(), terminal)
        self.assertEqual([p.name for p in binding.store.iterdir()], [path.name])

    def test_lesson_create_revise_conflict_noop_and_retire(self):
        self.knowledge_revision("lesson-author")

    def test_adr_create_revise_conflict_noop_and_retire(self):
        self.knowledge_revision("adr-author")

    def mapped_decision(self, family):
        module, binding, created, path = self.create_knowledge(family)
        original = path.read_bytes()
        current = self.invoke(family, "inspect", reference=created["reference"])["record"]
        pointers = {name: "/" + name for name in module.DECISION_POINTERS}
        config = self.write_json("project.json", {"config_version": 2, "constraints": {family: {
            "decision_sources": [{"id": "owner", "root": "decisions", "allowed_actors": ["fixture owner"], "pointers": pointers}]}}})
        evidence = {"subject_sha256": digest(original), "actor": "fixture owner", "decision": "accept", "decided_at": module.now_text()}
        if family == "adr-author":
            evidence["option_id"] = "A"
        decision_path = self.write_json("decisions/accept.json", evidence)
        selection = {"binding_id": "owner", "path": "decisions/accept.json", "expected_sha256": digest(decision_path.read_bytes())}
        operation = "accept" if family == "lesson-author" else "decide"
        self.invoke(family, operation, expected="blocked", reference=created["reference"],
                    expected_sha256=created["sha256"], reason="No selected authority", decision_source=selection)
        self.assertEqual(path.read_bytes(), original)
        accepted = self.invoke(family, operation, project_config=str(config), reference=created["reference"],
                               expected_sha256=created["sha256"], reason="Mapped fixture owner decision", decision_source=selection)
        observed = self.invoke(family, "inspect", reference=created["reference"])["record"]
        self.assertEqual(observed["status"], "accepted")
        self.assertEqual(observed["content"], current["content"])
        self.assertEqual(observed["decision"]["actor"], "fixture owner")
        self.assertEqual(observed["decision"]["subject_sha256"], digest(original))
        self.assertEqual(observed["decision"]["evidence"]["utf8"].encode(), decision_path.read_bytes())
        rendered = self.invoke(family, "render", reference=created["reference"])["view"]["markdown"]
        for expected in ("Status: accepted", "fixture owner", "Mapped fixture owner decision", "&quot;decision&quot;: &quot;accept&quot;"):
            self.assertIn(expected, rendered)
        query = self.invoke(family, "query", text="derive fixture")
        derived = self.invoke(family, "derive", reference=created["reference"], expected_sha256=accepted["sha256"],
                              reason="New independent candidate", text="derive fixture", decision={
                                  "action": "new", "query_sha256": query["query_sha256"], "acknowledge_partial": False,
                                  "reason": "Preserve accepted source as provenance"})
        child = self.invoke(family, "inspect", reference=derived["reference"])["record"]
        self.assertNotEqual(child["id"], current["id"])
        self.assertEqual(child["status"], module.INITIAL)
        self.assertIsNone(child["decision"])
        self.assertEqual(child["history"], [])
        self.assertEqual(child["provenance"][0]["snapshot"]["sha256"], accepted["sha256"])
        derived_view = self.invoke(family, "render", reference=derived["reference"])["view"]["markdown"]
        self.assertIn("derived\\-from", derived_view)
        self.assertIn(accepted["sha256"], derived_view)

    def test_lesson_mapped_acceptance_and_derivation_keep_decision_provenance(self):
        self.mapped_decision("lesson-author")

    def test_adr_mapped_acceptance_and_derivation_keep_decision_provenance(self):
        self.mapped_decision("adr-author")

    def test_backlog_transitions_require_current_state_and_completion_evidence(self):
        family = "local-backlog"
        module, binding = self.provision(family)
        self.require_native(module, binding.store)
        created = self.invoke(family, "create", content=content(family))
        reference = created["reference"]
        revised_content = content(family)
        revised_content["summary"] = "Revised local scope"
        revised = self.invoke(family, "revise", reference=reference, expected_sha256=created["sha256"], content=revised_content)
        path = binding.record_path(reference)
        before = path.read_bytes()
        self.invoke(family, "revise", expected="conflict", reference=reference, expected_sha256=created["sha256"], content=revised_content)
        self.assertEqual(path.read_bytes(), before)
        current = revised
        for prior, target in (("draft", "planned"), ("planned", "in_progress")):
            current = self.invoke(family, "transition", reference=reference, expected_sha256=current["sha256"],
                                  expected_state=prior, target_state=target, reason="Explicit fixture progression", completion_evidence=[])
            self.assertEqual(self.invoke(family, "inspect", reference=reference)["record"]["state"], target)
        before = path.read_bytes()
        for expected_state, expected in (("draft", "conflict"), ("in_progress", "invalid-input")):
            self.invoke(family, "transition", expected=expected, reference=reference, expected_sha256=current["sha256"],
                        expected_state=expected_state, target_state="completed", reason="No evidence", completion_evidence=[])
            self.assertEqual(path.read_bytes(), before)
        completed = self.invoke(family, "transition", reference=reference, expected_sha256=current["sha256"],
                                expected_state="in_progress", target_state="completed", reason="Caller supplied completion",
                                completion_evidence=[{"source": "fixture:observation", "note": "Retained attribution"}])
        terminal = path.read_bytes()
        self.invoke(family, "revise", expected="unsupported", reference=reference, expected_sha256=completed["sha256"], content=revised_content)
        self.assertEqual(path.read_bytes(), terminal)
        view = self.invoke(family, "render", reference=reference)["view"]["markdown"]
        self.assertIn("State: completed", view)
        self.assertIn("note: Retained attribution; source: fixture:observation", view)

    def test_pr_revision_preserves_explicit_subject_without_git(self):
        family = "pr-author"
        module, binding, value, path = self.persist(family)
        self.require_native(module, binding.store)
        original = path.read_bytes()
        revised_content = content(family)
        revised_content["summary"] = "Updated proposal prose"
        revised = self.invoke(family, "revise", reference=module.reference(value), expected_sha256=digest(original), content=revised_content)
        updated = path.read_bytes()
        self.invoke(family, "revise", expected="conflict", reference=module.reference(value), expected_sha256=digest(original), content=revised_content)
        self.assertEqual(path.read_bytes(), updated)
        inspected = self.invoke(family, "inspect", reference=module.reference(value))["record"]
        self.assertEqual(inspected["subject"], value["subject"])
        rendered = self.invoke(family, "render", reference=module.reference(value))
        self.assertFalse(rendered["subject_verified"])
        self.assertIn("Updated proposal prose", rendered["view"]["markdown"])
        self.assertEqual(rendered["sha256"], revised["sha256"])

    def test_cbf_publication_is_no_clobber_and_structural_failure_writes_nothing(self):
        family = "problem-frame-author"
        module, binding = self.provision(family)
        self.require_native(module, binding["store"])
        value = cbf_record()
        request = self.request(family, "create", reference=value["id"] + ".cbf.json", record=value)
        inputs = module.Inputs()
        context = module.configure(inputs, request)
        response = {"changed": False, "mutation_state": "none", "residue": [], "diagnostics": []}
        module.create_record(inputs, context, request, response)
        self.assertTrue(response["changed"])
        self.assertEqual(response["mutation_state"], "published")
        self.assertEqual(response["residue"], [])
        path = context["store"] / request["reference"]
        original = path.read_bytes()
        self.assertEqual(response["result"]["record"], value)
        self.assertEqual(response["subject_sha256"], digest(original))
        self.assert_fault(module, lambda: module.create_record(module.Inputs(), context, request, response), "conflict", "collision")
        invalid = copy.deepcopy(value)
        invalid["id"] = "cbf-" + "2" * 32
        invalid["open_questions"] = []
        invalid_request = self.request(family, "create", reference=invalid["id"] + ".cbf.json", record=invalid)
        self.assert_fault(module, lambda: module.create_record(module.Inputs(), context, invalid_request, response))
        self.assertEqual(path.read_bytes(), original)
        self.assertEqual([p.name for p in context["store"].iterdir()], [path.name])
