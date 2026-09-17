#!/usr/bin/env python3
"""GWT tests for deterministic generated runtime skill entries."""

from __future__ import annotations

import hashlib
import importlib.util
import unittest
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[3]
GENERATOR_PATH = REPO_ROOT / ".ai/scripts/generate-runtime-skill-entries.py"
SPEC = importlib.util.spec_from_file_location("runtime_skill_entries", GENERATOR_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"Unable to load generator: {GENERATOR_PATH}")
GENERATOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(GENERATOR)

import ai_context_package as PACKAGE  # noqa: E402


class RuntimeSkillEntryTests(unittest.TestCase):
    def test_gwt_001_given_selected_canonical_entries_when_checked_then_exact_wrappers_pass(self) -> None:
        # Given the selected pilot's canonical execution entries and generated wrappers.
        # When exact parity checks run, then no manual wrapper drift is accepted.
        self.assertEqual([], GENERATOR.check_entries(REPO_ROOT))

    def test_gwt_002_given_selected_entries_when_rendered_then_codex_and_claude_are_byte_identical(self) -> None:
        # Given each selected canonical skill source.
        # When it projects to both declared runtimes, then execution behavior is identical.
        entries = GENERATOR.generated_entries(REPO_ROOT)
        for skill_id in GENERATOR.SELECTED_SKILLS:
            with self.subTest(skill_id=skill_id):
                self.assertEqual(
                    entries[GENERATOR.wrapper_path(skill_id, "codex")],
                    entries[GENERATOR.wrapper_path(skill_id, "claude")],
                )

    def test_gwt_003_given_generated_entry_when_inspected_then_it_binds_canonical_source_digest(self) -> None:
        # Given a selected source skill.
        # When its entry is rendered, then provenance names the exact source bytes.
        for skill_id in GENERATOR.SELECTED_SKILLS:
            with self.subTest(skill_id=skill_id):
                source = REPO_ROOT / GENERATOR.source_path(skill_id)
                expected_digest = GENERATOR.source_digest(source.read_bytes())
                entry = (REPO_ROOT / GENERATOR.wrapper_path(skill_id, "codex")).read_text(encoding="utf-8")
                self.assertIn(f"canonical source SHA-256: `{expected_digest}`", entry)
                self.assertIn("This entry does not promise zero additional reads.", entry)

    def test_gwt_004_given_manual_wrapper_drift_when_checked_then_parity_fails(self) -> None:
        # Given a materialized projection with one edited runtime output.
        expected = GENERATOR.generated_entries(REPO_ROOT)
        actual = dict(expected)
        claude_entry = GENERATOR.wrapper_path("code-reviewer", "claude")
        actual[claude_entry] = actual[claude_entry] + "\nManual drift.\n"

        # When parity checks run, then the edited runtime output fails closed.
        errors = GENERATOR.parity_errors(expected, actual)

        self.assertTrue(any("code-reviewer/SKILL.md: differs" in error for error in errors))

    def test_gwt_005_given_missing_runtime_entry_field_when_rendered_then_generation_fails(self) -> None:
        # Given a canonical skill without its execution source.
        data, _ = GENERATOR.load_skill(REPO_ROOT, "local-change-implementer")
        data.pop("runtime_entry")

        # When rendering is requested, then generation rejects the missing authority.
        with self.assertRaisesRegex(ValueError, "runtime_entry must be a mapping"):
            GENERATOR.render_entry(data, b"fixture")

    def test_gwt_006_given_crlf_worktree_text_when_rendered_then_git_text_provenance_is_stable(self) -> None:
        # Given the same canonical YAML bytes with Windows or Git LF line endings.
        source = REPO_ROOT / GENERATOR.source_path("local-change-implementer")
        git_text = source.read_bytes()
        worktree_text = git_text.decode("utf-8").replace("\n", "\r\n").encode("utf-8")

        # When the entry is rendered, then its source digest and bytes match Git-text input.
        data_lf, normalized_lf = PACKAGE.RUNTIME_SKILL_ENTRIES.load_skill_document(
            git_text, GENERATOR.source_path("local-change-implementer")
        )
        data_crlf, normalized_crlf = PACKAGE.RUNTIME_SKILL_ENTRIES.load_skill_document(
            worktree_text, GENERATOR.source_path("local-change-implementer")
        )

        self.assertEqual(normalized_lf, normalized_crlf)
        self.assertEqual(GENERATOR.source_digest(git_text), GENERATOR.source_digest(worktree_text))
        self.assertEqual(
            GENERATOR.render_entry(data_lf, normalized_lf),
            GENERATOR.render_entry(data_crlf, normalized_crlf),
        )

    def test_gwt_007_given_portable_projected_skills_when_payload_is_built_then_wrappers_bind_projected_bytes(self) -> None:
        # Given a portable payload after its canonical skill manifests are projected.
        profile = yaml.safe_load(
            (REPO_ROOT / ".ai/distribution/profiles/dotnet-backend.yaml").read_text(encoding="utf-8")
        )
        contents: dict[str, bytes] = {}
        for skill_id in GENERATOR.SELECTED_SKILLS:
            source = GENERATOR.source_path(skill_id).as_posix()
            projected = PACKAGE.project_portable_payload_content(
                source,
                (REPO_ROOT / source).read_bytes(),
                profile,
            )
            self.assertNotIn(b"framework-source", projected)
            contents[source] = projected
            for target in ("codex", "claude"):
                contents[GENERATOR.wrapper_path(skill_id, target).as_posix()] = b"stale source wrapper\n"
        expected = PACKAGE.RUNTIME_SKILL_ENTRIES.render_payload_entries(contents)
        payload = {
            path: PACKAGE.PayloadFile(
                path=path,
                source_path=path,
                content=content,
                mode=0o644,
                ownership="framework-owned",
                install_behavior="merge",
                entry_id="runtime-skill-entry-fixture",
                component_id="software-development-core",
            )
            for path, content in contents.items()
        }

        # When package assembly regenerates derived wrappers, then each is exactly
        # the projection of final payload authority, without a source-only mode.
        PACKAGE.regenerate_generated_runtime_entries(payload, profile)

        for path, entry in expected.items():
            with self.subTest(wrapper=path):
                self.assertEqual(entry, payload[path].content)
                self.assertNotIn(b"framework-source", payload[path].content)
                source = path.replace(".agents/skills", ".ai/assets/skills").replace(".claude/skills", ".ai/assets/skills").replace("/SKILL.md", "/skill.yaml")
                self.assertIn(
                    f"canonical source SHA-256: `{hashlib.sha256(contents[source]).hexdigest()}`".encode("utf-8"),
                    payload[path].content,
                )

    def test_gwt_008_given_final_projected_role_subset_when_rendered_then_only_projected_binding_metadata_is_emitted(self) -> None:
        # Given final package skill bytes with a modified and reduced role-binding set.
        profile = yaml.safe_load(
            (REPO_ROOT / ".ai/distribution/profiles/dotnet-backend.yaml").read_text(encoding="utf-8")
        )
        source = GENERATOR.source_path("code-reviewer")
        projected = PACKAGE.project_portable_payload_content(
            source.as_posix(),
            (REPO_ROOT / source).read_bytes(),
            profile,
        )
        data, _ = PACKAGE.RUNTIME_SKILL_ENTRIES.load_skill_document(projected, source)
        selected = dict(data["role_bindings"][0])
        selected["applicability"] = "Projected primary review scope only."
        data["role_bindings"] = [selected]
        final_projected = yaml.safe_dump(data, sort_keys=False, allow_unicode=True).encode("utf-8")
        contents = {source.as_posix(): final_projected}
        for target in ("codex", "claude"):
            contents[GENERATOR.wrapper_path("code-reviewer", target).as_posix()] = b"stale wrapper\n"

        # When package assembly renders from those final bytes, then it exposes
        # the selected role identity and condition without leaking omitted roles.
        entries = PACKAGE.RUNTIME_SKILL_ENTRIES.render_payload_entries(contents)
        entry = entries[GENERATOR.wrapper_path("code-reviewer", "codex").as_posix()].decode("utf-8")

        self.assertIn("## Canonical role bindings", entry)
        self.assertIn("`code-review-sub-agent`", entry)
        self.assertIn("Projected primary review scope only.", entry)
        self.assertIn("`primary`", entry)
        self.assertIn("`mandatory-when-applicable`", entry)
        self.assertNotIn("aggregate-code-review-sub-agent", entry)
        self.assertNotIn("Aggregate or event-sourcing", entry)

        local_data, local_raw = GENERATOR.load_skill(REPO_ROOT, "local-change-implementer")
        local_entry = GENERATOR.render_entry(local_data, local_raw)
        self.assertNotIn("## Canonical role bindings", local_entry)


if __name__ == "__main__":
    unittest.main()
