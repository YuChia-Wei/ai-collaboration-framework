#!/usr/bin/env python3
"""GWT integration tests for deterministic packaging and release workflows."""

from __future__ import annotations

import os
import subprocess
import shutil
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[3]
SCRIPTS = ROOT / ".ai/scripts"
sys.path.insert(0, str(SCRIPTS))
import ai_context_package as PACKAGE  # noqa: E402


def git(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", *args], cwd=root, check=True, capture_output=True, text=True)


class SyntheticPackageRepo:
    """Own a minimal Git-backed package source and isolated output roots."""

    def __init__(self) -> None:
        self._temporary = tempfile.TemporaryDirectory(prefix="ai-context-packaging-")
        self.root = Path(self._temporary.name) / "source"
        self.root.mkdir()
        git(self.root, "init", "-q")
        git(self.root, "config", "user.name", "Fixture")
        git(self.root, "config", "user.email", "fixture@example.invalid")
        (self.root / ".ai/distribution/templates").mkdir(parents=True)
        (self.root / ".ai/distribution/profiles").mkdir(parents=True)
        (self.root / ".ai/scripts").mkdir(parents=True)
        (self.root / ".dev").mkdir()
        (self.root / "docs").mkdir()
        (self.root / ".ai/distribution/templates/INSTALL.md").write_text(
            "# Install fixture\n", encoding="utf-8", newline="\n"
        )
        (self.root / ".ai/distribution/templates/requirements.txt").write_text(
            "PyYAML==6.0.3\n", encoding="utf-8", newline="\n"
        )
        (self.root / "docs/rule.md").write_text("committed rule\n", encoding="utf-8", newline="\n")
        (self.root / "docs/remove.md").write_text("remove me\n", encoding="utf-8", newline="\n")
        (self.root / "docs/old-name.md").write_text("renamed bytes\n", encoding="utf-8", newline="\n")
        (self.root / ".dev/validation.local.conf").write_text(
            "validation.routine.local=required\n", encoding="utf-8", newline="\n"
        )
        (self.root / ".dev/portable.md").write_text(
            "portable project guidance\n", encoding="utf-8", newline="\n"
        )
        for script in (
            "ai_context_package_apply.py",
            "ai_context_effective_rules.py",
            "ai_context_target_provenance.py",
            "plan-ai-context-package-apply.py",
            "resolve-effective-rule-packet.py",
            "python-entrypoints.json",
            "python_prerequisites.py",
        ):
            (self.root / ".ai/scripts" / script).write_bytes((SCRIPTS / script).read_bytes())
        (self.root / ".ai/scripts/render-ai-context-release-notes.py").write_text(
            "raise SystemExit('source-only renderer')\n",
            encoding="utf-8",
            newline="\n",
        )
        profile = {
            "schema_version": "2.0.0",
            "profile": {
                "id": "fixture",
                "component_id": "dotnet-backend",
                "requires": ["software-development-core"],
            },
            "release_model": "single-versioned-componentized-release",
            "components": [
                {
                    "component_id": "software-development-core",
                    "classification": "mandatory-core",
                    "required": True,
                    "requires": [],
                },
                {
                    "component_id": "ai-context-lifecycle-core",
                    "classification": "mandatory-core",
                    "required": True,
                    "requires": [],
                },
                {
                    "component_id": "dotnet-backend",
                    "classification": "technology-profile",
                    "required": False,
                    "requires": ["software-development-core"],
                },
                {
                    "component_id": "repo-backlog",
                    "classification": "optional-provider",
                    "required": False,
                    "default_enabled": False,
                    "requires": ["software-development-core"],
                },
            ],
            "selection_defaults": {
                "release_model": "single-versioned-componentized-release",
                "mandatory_components": [
                    "software-development-core",
                    "ai-context-lifecycle-core",
                ],
                "profiles": ["dotnet-backend"],
                "providers": {
                    "repo-backlog": {
                        "enabled": False,
                        "preservation": "preserve-existing-if-recorded",
                    }
                },
            },
            "package": {
                "source_repository": "fixture/repository",
                "name_template": "fixture-v{version}",
            },
            "payload_user_view": {
                "schema_version": "1.0.0",
                "classifications": PACKAGE.PAYLOAD_USER_VIEW_CLASSIFICATIONS,
                "supported_selections": [
                    {
                        "selection_id": "core-only",
                        "components": [
                            "software-development-core",
                            "ai-context-lifecycle-core",
                        ],
                    },
                    {
                        "selection_id": "dotnet-selected",
                        "components": [
                            "software-development-core",
                            "ai-context-lifecycle-core",
                            "dotnet-backend",
                        ],
                    },
                ],
                "capabilities": [],
            },
            "reference_integrity": {
                "text_extensions": [".md", ".yaml", ".py"],
                "forbidden_source_lifecycle_patterns": [
                    ".dev/workflows/20*/**",
                    ".dev/assessments/ASM-*/**",
                    ".dev/releases/v*/**",
                    ".dev/backlog/items/**",
                ],
            },
            "entries": [
                {
                    "id": "fixture-docs",
                    "component_id": "software-development-core",
                    "source": "docs/**",
                    "target": "preserve-relative-path",
                    "ownership": "framework-managed",
                    "install_behavior": "managed",
                },
                {
                    "id": "fixture-apply-scripts",
                    "component_id": "software-development-core",
                    "source": ".ai/scripts/**",
                    "target": "preserve-relative-path",
                    "ownership": "framework-managed",
                    "install_behavior": "managed",
                },
                {
                    "id": "fixture-local-policy",
                    "component_id": "software-development-core",
                    "source": ".dev/**",
                    "target": "preserve-relative-path",
                    "ownership": "framework-managed",
                    "install_behavior": "managed",
                }
            ],
            "exclusions": [
                {
                    "id": "local-validation-opt-in",
                    "classification": "source-only",
                    "patterns": [".dev/validation.local.conf"],
                    "reason": "Machine-local validation selection is never portable framework truth.",
                },
                {
                    "id": "source-release-renderer",
                    "classification": "source-only",
                    "patterns": [
                        ".ai/scripts/render-ai-context-release-notes.py"
                    ],
                    "reason": "Release publication rendering is source-only.",
                }
            ],
        }
        (self.root / ".ai/distribution/profiles/fixture.yaml").write_text(
            yaml.safe_dump(profile, sort_keys=False), encoding="utf-8", newline="\n"
        )
        git(self.root, "add", ".")
        git(self.root, "commit", "-qm", "fixture package source")
        self.profile = ".ai/distribution/profiles/fixture.yaml"

    def close(self) -> None:
        self._temporary.cleanup()

    def output(self, name: str) -> Path:
        return Path(self._temporary.name) / name


    def ensure_release(
        self,
        version: str,
        automatic_sources: list[str] | None = None,
    ) -> None:
        normalized = PACKAGE.normalize_version(version)
        sources = automatic_sources or []
        release_path = self.root / f".dev/releases/v{normalized}/release.yaml"
        release_path.parent.mkdir(parents=True, exist_ok=True)
        document = {
            "version": f"v{normalized}",
            "compatibility": {
                "breaking_changes": True,
                "minimum_source_version": sources[0] if sources else "v0.1.0",
                "reconciliation_sources": sources,
                "automatic_upgrade_sources": sources,
            },
            "distribution": {
                "profile_id": "fixture",
                "package_id": f"fixture-v{normalized}",
            },
        }
        content = yaml.safe_dump(document, sort_keys=False)
        if not release_path.exists() or release_path.read_text(encoding="utf-8") != content:
            release_path.write_text(content, encoding="utf-8", newline="\n")
            git(self.root, "add", "--", release_path.relative_to(self.root).as_posix())
            git(self.root, "commit", "-qm", f"release v{normalized} fixture")

    def build(
        self,
        name: str,
        version: str = "1.0.0",
        previous_files: Path | None = None,
        previous_version: str | None = None,
    ) -> dict[str, Path | str]:
        automatic_sources = (
            [f"v{PACKAGE.normalize_version(previous_version)}"]
            if previous_version is not None
            else []
        )
        self.ensure_release(version, automatic_sources)
        return PACKAGE.build_package(
            self.root,
            "HEAD",
            version,
            self.output(name),
            self.profile,
            previous_files,
            previous_version,
        )

    def extract(self, result: dict[str, Path | str], name: str) -> Path:
        destination = self.output(name)
        with zipfile.ZipFile(Path(result["zip"])) as archive:
            archive.extractall(destination)
        return destination / str(result["package_id"])


class GitObjectReaderGwtTests(unittest.TestCase):
    def test_gwt_000_given_shared_snapshot_when_multiple_payload_blobs_are_read_then_one_batch_process_is_reused(self) -> None:
        fixture = SyntheticPackageRepo()
        try:
            large_content = ("large package fixture\n" * 32768).encode("utf-8")
            large_path = fixture.root / "docs/large.md"
            large_path.write_bytes(large_content)
            git(fixture.root, "add", "docs/large.md")
            git(fixture.root, "commit", "-qm", "large batch fixture")

            # Given one immutable snapshot, when two blobs are retrieved,
            # then they share the one preloaded Git batch reader.
            snapshot = PACKAGE.PackageRepositorySnapshot.from_ref(fixture.root, "HEAD")
            rule = snapshot.tree["docs/rule.md"]
            large = snapshot.tree["docs/large.md"]
            self.assertEqual(b"committed rule\n", snapshot.blob_reader.read_blob(rule))
            self.assertEqual(large_content, snapshot.blob_reader.read_blob(large))
            self.assertEqual(1, snapshot.blob_reader.batch_process_count)
        finally:
            fixture.close()

    def test_gwt_001_given_missing_object_when_batch_read_then_the_error_is_fail_closed(self) -> None:
        fixture = SyntheticPackageRepo()
        try:
            reader = PACKAGE.GitObjectReader(fixture.root)
            missing = PACKAGE.GitEntry("missing.md", "100644", "blob", "0" * 40)

            with self.assertRaises(PACKAGE.PackageError) as raised:
                reader.read_blobs_batch((missing,))

            self.assertIn("Git batch response", str(raised.exception))
            self.assertEqual(1, reader.batch_process_count)
        finally:
            fixture.close()


def rewrite_zip_member(source: Path, target: Path, suffix: str, replacement: bytes) -> None:
    with zipfile.ZipFile(source) as archive:
        records = [(info, archive.read(info)) for info in archive.infolist()]
    with zipfile.ZipFile(target, "w") as archive:
        for info, content in records:
            if info.filename.endswith(suffix):
                content = replacement
            copied = zipfile.ZipInfo(info.filename, info.date_time)
            copied.create_system = info.create_system
            copied.external_attr = info.external_attr
            copied.compress_type = info.compress_type
            archive.writestr(copied, content)


class DeterministicPackageGwtTests(unittest.TestCase):
    def test_gwt_000a_given_tracked_local_validation_opt_in_when_payload_is_projected_then_it_is_excluded(self) -> None:
        fixture = SyntheticPackageRepo()
        try:
            tree = PACKAGE.git_tree(fixture.root, "HEAD")
            profile = PACKAGE.load_yaml_blob(fixture.root, tree, fixture.profile)
            targets = {
                item.path
                for item in PACKAGE.collect_payload(fixture.root, tree, profile)
            }
            self.assertIn(".dev/portable.md", targets)
            self.assertNotIn(".dev/validation.local.conf", targets)
        finally:
            fixture.close()

    def test_gwt_000_given_source_release_body_tooling_when_payload_is_projected_then_downstream_excludes_it(self) -> None:
        fixture = SyntheticPackageRepo()
        try:
            tree = PACKAGE.git_tree(fixture.root, "HEAD")
            profile = PACKAGE.load_yaml_blob(fixture.root, tree, fixture.profile)
            targets = {
                item.path
                for item in PACKAGE.collect_payload(fixture.root, tree, profile)
            }
            self.assertNotIn(
                ".ai/scripts/render-ai-context-release-notes.py", targets
            )
            self.assertNotIn(
                ".ai/scripts/validate-ai-context-release-state.py", targets
            )
            self.assertFalse(
                any("ai-context-release-closeout" in path for path in targets)
            )
            self.assertFalse(
                any(path.startswith(".ai/scripts/tests/") for path in targets)
            )
            self.assertFalse(
                any(path.startswith(".dev/workflows/") for path in targets)
            )
            self.assertIn(
                ".ai/scripts/plan-ai-context-package-apply.py", targets
            )
        finally:
            fixture.close()

    def test_gwt_000c_given_repository_identity_gate_when_profile_is_read_then_all_control_files_are_source_only(self) -> None:
        profile = yaml.safe_load(
            (ROOT / ".ai/distribution/profiles/dotnet-backend.yaml").read_text(
                encoding="utf-8"
            )
        )
        exclusions = {item["id"]: item for item in profile["exclusions"]}
        runtime_patterns = set(
            exclusions["repository-and-local-runtime-state"]["patterns"]
        )

        self.assertTrue(
            {
                ".ai/scripts/validate-repository-identity.py",
                ".ai/scripts/tests/test_repository_identity.py",
            }
            <= runtime_patterns
        )
        self.assertIn(
            ".ai/distribution/**",
            exclusions["source-distribution-control"]["patterns"],
        )

    def test_gwt_0000_given_source_local_policy_and_portable_mapping_when_projected_then_target_gets_only_portable_bytes(self) -> None:
        fixture = SyntheticPackageRepo()
        try:
            source_policy = fixture.root / ".dev/standards/POLICY.md"
            portable_root = fixture.root / ".ai/assets/shared/governance"
            source_policy.parent.mkdir(parents=True)
            portable_root.mkdir(parents=True)
            source_policy.write_text(
                "source-only hosted provider and main rule\n", encoding="utf-8"
            )
            (portable_root / "POLICY.md").write_text(
                "provider-neutral workflow truth\n", encoding="utf-8"
            )
            manifest_path = portable_root / "manifest.yaml"
            manifest_path.write_text(
                yaml.safe_dump(
                    {
                        "schema_version": "1.0",
                        "source_root": ".",
                        "mappings": [
                            {
                                "source": "POLICY.md",
                                "target": ".dev/standards/POLICY.md",
                                "component_id": "software-development-core",
                            }
                        ],
                    },
                    sort_keys=False,
                ),
                encoding="utf-8",
            )
            profile_path = fixture.root / fixture.profile
            profile = yaml.safe_load(profile_path.read_text(encoding="utf-8"))
            profile["entries"].append(
                {
                    "id": "portable-policy",
                    "component_id": "software-development-core",
                    "source": ".ai/assets/shared/governance/**",
                    "target": "mapping-declared-by-template-manifest",
                    "template_manifest": ".ai/assets/shared/governance/manifest.yaml",
                    "ownership": "framework-managed",
                    "install_behavior": "managed",
                }
            )
            profile["exclusions"].append(
                {
                    "id": "source-policy",
                    "classification": "source-only",
                    "patterns": [".dev/standards/POLICY.md"],
                    "reason": "Source policy must not become target truth.",
                }
            )
            profile_path.write_text(
                yaml.safe_dump(profile, sort_keys=False), encoding="utf-8"
            )
            git(fixture.root, "add", ".")
            git(fixture.root, "commit", "-qm", "portable policy fixture")

            tree = PACKAGE.git_tree(fixture.root, "HEAD")
            committed_profile = PACKAGE.load_yaml_blob(
                fixture.root, tree, fixture.profile
            )
            payload = {
                item.path: item
                for item in PACKAGE.collect_payload(
                    fixture.root, tree, committed_profile
                )
            }

            projected = payload[".dev/standards/POLICY.md"]
            self.assertEqual(
                ".ai/assets/shared/governance/POLICY.md", projected.source_path
            )
            self.assertEqual(b"provider-neutral workflow truth\n", projected.content)
            self.assertNotIn(b"hosted provider", projected.content)
        finally:
            fixture.close()

    def test_gwt_000a_given_real_component_matrix_when_payload_is_projected_then_both_mandatory_cores_keep_their_capabilities(self) -> None:
        tree = PACKAGE.git_tree(ROOT, "HEAD")
        profile = yaml.safe_load(
            (
                ROOT / ".ai/distribution/profiles/dotnet-backend.yaml"
            ).read_text(encoding="utf-8")
        )
        payload = {
            item.path: item.component_id
            for item in PACKAGE.collect_payload(ROOT, tree, profile)
        }
        lifecycle_paths = [
            ".ai/assets/skills/ai-context-auditor/skill.yaml",
            ".ai/assets/skills/ai-context-governance/skill.yaml",
            ".ai/assets/skills/ai-context-upgrader/skill.yaml",
            ".ai/assets/skills/ai-context-init/skill.yaml",
            ".agents/skills/ai-context-auditor/SKILL.md",
            ".agents/skills/ai-context-governance/SKILL.md",
            ".agents/skills/ai-context-upgrader/SKILL.md",
            ".agents/skills/ai-context-init/SKILL.md",
            ".ai/scripts/ai_context_target_provenance.py",
            ".ai/scripts/ai_context_effective_rules.py",
            ".ai/scripts/resolve-effective-rule-packet.py",
            ".ai/scripts/validate-ai-context-target.py",
        ]
        self.assertTrue(
            all(
                payload[path] == "ai-context-lifecycle-core"
                for path in lifecycle_paths
            )
        )
        self.assertEqual(
            "software-development-core",
            payload[".ai/assets/skills/software-development-orchestrator/skill.yaml"],
        )
        self.assertEqual(
            "software-development-core",
            payload[".dev/workflows/README.MD"],
        )
        self.assertEqual(
            "repo-backlog",
            payload[".dev/backlog/README.MD"],
        )
        self.assertEqual(
            "dotnet-backend",
            payload[
                ".ai/assets/tech-stacks/dotnet-backend/tooling/"
                "on-demand-mechanical-validation/recipe-manifest.yaml"
            ],
        )
        self.assertFalse(
            any(
                path.lower().endswith((".csproj", ".sln", ".slnx"))
                for path in payload
            ),
            "the default framework payload must not contain compilable .NET projects",
        )
        self.assertNotIn("global.json", payload)
        self.assertFalse(
            any("bundled-mechanical-validation" in path for path in payload),
            "the retired bundled provider must not remain in the payload",
        )
        self.assertFalse(
            any(
                path.startswith("tools/") and path.split("/", 2)[1].endswith(".Tests")
                for path in payload
            ),
            "the SDK-free source framework must not project root tools projects",
        )

    def test_gwt_000aa_given_repository_configuration_when_payload_is_projected_then_dedicated_target_seeds_replace_source_truth(self) -> None:
        tree = PACKAGE.git_tree(ROOT, "HEAD")
        profile = PACKAGE.load_yaml_blob(
            ROOT,
            tree,
            ".ai/distribution/profiles/dotnet-backend.yaml",
        )
        payload = {
            item.path: item
            for item in PACKAGE.collect_payload(ROOT, tree, profile)
        }

        expected_sources = {
            ".editorconfig": (
                ".ai/assets/skills/ai-context-init/templates/"
                "public-root/.editorconfig"
            ),
            ".gitattributes": (
                ".ai/assets/skills/ai-context-init/templates/"
                "public-root/.gitattributes"
            ),
        }
        for target, source in expected_sources.items():
            item = payload[target]
            self.assertEqual(source, item.source_path)
            self.assertEqual("target-template", item.ownership)
            self.assertEqual("seed", item.install_behavior)
            self.assertEqual("software-development-core", item.component_id)
            self.assertNotIn(b".dev/assessments", item.content)
            self.assertNotIn(b"evidence/external/original", item.content)

        source_only = next(
            item
            for item in profile["exclusions"]
            if item["id"] == "source-root-truth"
        )
        self.assertTrue(
            {".editorconfig", ".gitattributes"}
            <= set(source_only["patterns"])
        )

    def test_gwt_000b_given_overlapping_component_overrides_when_one_path_matches_both_then_projection_fails_closed(self) -> None:
        entry = {
            "id": "ambiguous-component-fixture",
            "component_overrides": [
                {
                    "component_id": "software-development-core",
                    "patterns": [".ai/assets/**"],
                },
                {
                    "component_id": "ai-context-lifecycle-core",
                    "patterns": [".ai/assets/skills/**"],
                },
            ],
        }
        with self.assertRaisesRegex(
            PACKAGE.PackageError, "ambiguous component overrides"
        ):
            PACKAGE.resolve_entry_component(
                entry,
                ".ai/assets/skills/ai-context-governance/skill.yaml",
                "software-development-core",
                {"software-development-core", "ai-context-lifecycle-core"},
            )

    def test_gwt_000c_given_unknown_component_override_when_profile_is_resolved_then_projection_fails_closed(self) -> None:
        entry = {
            "id": "unknown-component-fixture",
            "component_overrides": [
                {
                    "component_id": "unknown-core",
                    "patterns": [".ai/assets/**"],
                }
            ],
        }
        with self.assertRaisesRegex(PACKAGE.PackageError, "unknown component_id"):
            PACKAGE.resolve_entry_component(
                entry,
                ".ai/assets/skills/software-development-orchestrator/skill.yaml",
                "software-development-core",
                {"software-development-core", "ai-context-lifecycle-core"},
            )

    def test_gwt_001_given_one_immutable_commit_when_built_twice_then_archives_are_byte_identical(self) -> None:
        fixture = SyntheticPackageRepo()
        try:
            # Given one immutable package source commit.
            # When independent output directories build the same version.
            first = fixture.build("first")
            second = fixture.build("second")
            # Then each archive format and its sidecar are byte-identical.
            for key in ("zip", "tar_gz"):
                first_path, second_path = Path(first[key]), Path(second[key])
                self.assertEqual(first_path.read_bytes(), second_path.read_bytes())
                self.assertEqual(Path(f"{first_path}.sha256").read_bytes(), Path(f"{second_path}.sha256").read_bytes())
        finally:
            fixture.close()

    def test_gwt_001a_given_message_only_rewrite_when_built_then_tree_identity_and_eligible_inputs_match(self) -> None:
        fixture = SyntheticPackageRepo()
        try:
            fixture.ensure_release("1.0.0")
            first_commit = git(fixture.root, "rev-parse", "HEAD").stdout.strip()
            git(fixture.root, "commit", "--allow-empty", "-qm", "message-only rewrite")
            second_commit = git(fixture.root, "rev-parse", "HEAD").stdout.strip()

            first = PACKAGE.build_package(
                fixture.root, first_commit, "1.0.0", fixture.output("message-first"), fixture.profile
            )
            second = PACKAGE.build_package(
                fixture.root, second_commit, "1.0.0", fixture.output("message-second"), fixture.profile
            )

            self.assertNotEqual(first["commit"], second["commit"])
            self.assertEqual(first["tree"], second["tree"])
            for key in (
                "selected_input_fingerprint",
                "payload_fingerprint",
                "files_manifest_digest",
                "migration_digest",
            ):
                self.assertEqual(first[key], second[key])
        finally:
            fixture.close()

    def test_gwt_001b_given_unselected_documentation_change_when_built_then_selected_input_identity_is_reused(self) -> None:
        fixture = SyntheticPackageRepo()
        try:
            fixture.ensure_release("1.0.0")
            first = PACKAGE.build_package(
                fixture.root, "HEAD", "1.0.0", fixture.output("docs-first"), fixture.profile
            )
            (fixture.root / "README.md").write_text(
                "unselected documentation\n", encoding="utf-8", newline="\n"
            )
            git(fixture.root, "add", "README.md")
            git(fixture.root, "commit", "-qm", "documentation outside package inputs")
            second = PACKAGE.build_package(
                fixture.root, "HEAD", "1.0.0", fixture.output("docs-second"), fixture.profile
            )

            self.assertNotEqual(first["tree"], second["tree"])
            self.assertEqual(
                first["selected_input_fingerprint"], second["selected_input_fingerprint"]
            )
            self.assertEqual(first["payload_fingerprint"], second["payload_fingerprint"])
        finally:
            fixture.close()

    def test_gwt_001c_given_relevant_payload_change_when_built_then_content_identity_is_invalidated(self) -> None:
        fixture = SyntheticPackageRepo()
        try:
            fixture.ensure_release("1.0.0")
            first = PACKAGE.build_package(
                fixture.root, "HEAD", "1.0.0", fixture.output("payload-first"), fixture.profile
            )
            (fixture.root / "docs/rule.md").write_text(
                "changed package rule\n", encoding="utf-8", newline="\n"
            )
            git(fixture.root, "add", "docs/rule.md")
            git(fixture.root, "commit", "-qm", "relevant package input")
            second = PACKAGE.build_package(
                fixture.root, "HEAD", "1.0.0", fixture.output("payload-second"), fixture.profile
            )

            self.assertNotEqual(
                first["selected_input_fingerprint"], second["selected_input_fingerprint"]
            )
            self.assertNotEqual(first["payload_fingerprint"], second["payload_fingerprint"])
        finally:
            fixture.close()

    def test_gwt_001d_given_profile_configuration_change_when_built_then_selected_input_identity_is_invalidated(self) -> None:
        fixture = SyntheticPackageRepo()
        try:
            fixture.ensure_release("1.0.0")
            first = PACKAGE.build_package(
                fixture.root, "HEAD", "1.0.0", fixture.output("profile-first"), fixture.profile
            )
            profile_path = fixture.root / fixture.profile
            profile = yaml.safe_load(profile_path.read_text(encoding="utf-8"))
            profile["package"]["source_repository"] = "fixture/repository-v2"
            profile_path.write_text(
                yaml.safe_dump(profile, sort_keys=False), encoding="utf-8", newline="\n"
            )
            git(fixture.root, "add", fixture.profile)
            git(fixture.root, "commit", "-qm", "relevant profile configuration")
            second = PACKAGE.build_package(
                fixture.root, "HEAD", "1.0.0", fixture.output("profile-second"), fixture.profile
            )

            self.assertNotEqual(
                first["selected_input_fingerprint"], second["selected_input_fingerprint"]
            )
            self.assertEqual(first["payload_fingerprint"], second["payload_fingerprint"])
        finally:
            fixture.close()

    def test_gwt_002_given_dirty_checkout_bytes_when_head_is_built_then_git_blob_truth_wins(self) -> None:
        fixture = SyntheticPackageRepo()
        try:
            # Given a tracked checkout file differs from its committed Git blob.
            (fixture.root / "docs/rule.md").write_text("dirty checkout\n", encoding="utf-8", newline="\n")
            # When the package is built from HEAD.
            result = fixture.build("dirty")
            members = PACKAGE.validate_archive(Path(result["zip"]))
            # Then the payload contains committed bytes and the checkout stays dirty.
            self.assertEqual(
                b"committed rule\n",
                members["fixture-v1.0.0/payload/docs/rule.md"][0],
            )
            self.assertIn("docs/rule.md", git(fixture.root, "status", "--short").stdout)
        finally:
            fixture.close()

    def test_gwt_003_given_existing_outputs_when_build_repeats_then_overwrite_is_refused(self) -> None:
        fixture = SyntheticPackageRepo()
        try:
            # Given the governed archive names already exist after one build.
            fixture.build("existing")
            # When another build targets the same directory, then it fails closed.
            with self.assertRaisesRegex(PACKAGE.PackageError, "refusing to overwrite"):
                fixture.build("existing")
        finally:
            fixture.close()

    def test_gwt_004_given_zip_member_tampering_when_validated_then_checksum_contract_fails(self) -> None:
        fixture = SyntheticPackageRepo()
        try:
            # Given a valid package whose payload member is changed without metadata updates.
            result = fixture.build("valid")
            tampered = fixture.output("tampered.zip")
            rewrite_zip_member(Path(result["zip"]), tampered, "payload/docs/rule.md", b"tampered\n")
            # When archive validation recomputes envelope checksums, then it rejects the package.
            with self.assertRaisesRegex(PACKAGE.PackageError, "SHA256SUMS"):
                PACKAGE.validate_archive(tampered)
        finally:
            fixture.close()

    def test_gwt_005_given_zip_and_tar_from_one_build_when_validated_then_payload_and_modes_match(self) -> None:
        fixture = SyntheticPackageRepo()
        try:
            # Given both governed archive formats from one build.
            result = fixture.build("parity")
            # When sidecars and archives are validated.
            PACKAGE.validate_sidecar(Path(result["zip"]))
            PACKAGE.validate_sidecar(Path(result["tar_gz"]))
            zip_members = PACKAGE.validate_archive(Path(result["zip"]))
            tar_members = PACKAGE.validate_archive(Path(result["tar_gz"]))
            # Then every member byte and normalized mode is identical by path.
            self.assertEqual(zip_members, tar_members)
        finally:
            fixture.close()

    def test_gwt_005a_given_component_profile_when_built_then_metadata_carries_one_selection_and_component_identity(self) -> None:
        fixture = SyntheticPackageRepo()
        try:
            result = fixture.build("component-metadata")
            root = fixture.extract(result, "component-metadata-extracted")
            package = yaml.safe_load(
                (root / "metadata/package.yaml").read_text(encoding="utf-8")
            )
            inventory = yaml.safe_load(
                (root / "metadata/files.yaml").read_text(encoding="utf-8")
            )
            migration = yaml.safe_load(
                (root / "metadata/migration.yaml").read_text(encoding="utf-8")
            )

            self.assertEqual("2.2.0", package["schema_version"])
            self.assertEqual("2.0.0", inventory["schema_version"])
            self.assertEqual("3.0.0", migration["schema_version"])
            self.assertEqual(package["selection"], migration["selection"])
            self.assertEqual("1.0.0", package["user_view"]["schema_version"])
            self.assertEqual(result["tree"], package["source"]["tree"])
            self.assertEqual(result["commit"], package["source"]["commit"])
            self.assertEqual(
                result["selected_input_fingerprint"],
                package["identity"]["selected_input_fingerprint"],
            )
            self.assertEqual(
                result["payload_fingerprint"],
                package["identity"]["payload_fingerprint"],
            )
            self.assertEqual(
                result["files_manifest_digest"],
                package["identity"]["files_manifest_digest"],
            )
            self.assertEqual(
                result["migration_digest"],
                package["identity"]["migration_digest"],
            )
            self.assertEqual(
                {
                    "minimum_governed_source": "v0.1.0",
                    "breaking_changes": True,
                    "automatic_upgrade_sources": [],
                },
                package["compatibility"],
            )
            self.assertTrue(
                all(
                    record["component_id"] == "software-development-core"
                    for record in inventory["files"]
                )
            )
            self.assertTrue(
                all(
                    operation["component_id"] == "software-development-core"
                    for operation in migration["clean_install"]["operations"]
                )
            )
        finally:
            fixture.close()

    def test_gwt_005aa_given_archive_sidecar_digest_drift_when_validated_then_it_fails_closed(self) -> None:
        fixture = SyntheticPackageRepo()
        try:
            result = fixture.build("sidecar-drift")
            sidecar = Path(f"{result['zip']}.sha256")
            sidecar.write_text(
                f"{'0' * 64}  {Path(result['zip']).name}\n",
                encoding="utf-8",
                newline="\n",
            )
            with self.assertRaisesRegex(PACKAGE.PackageError, "sidecar mismatch"):
                PACKAGE.validate_sidecar(Path(result["zip"]))
        finally:
            fixture.close()

    def test_gwt_005b_given_release_and_migration_sources_disagree_when_built_then_it_fails_closed(self) -> None:
        fixture = SyntheticPackageRepo()
        try:
            # Given the governed release advertises an automatic source that the
            # package build did not receive.
            fixture.ensure_release("1.0.0", ["v0.9.0"])
            # When the package is built, then metadata cannot silently claim a
            # broader upgrade contract than migration.yaml implements.
            with self.assertRaisesRegex(
                PACKAGE.PackageError, "do not match package migration sources"
            ):
                PACKAGE.build_package(
                    fixture.root,
                    "HEAD",
                    "1.0.0",
                    fixture.output("mismatched-release"),
                    fixture.profile,
                )
        finally:
            fixture.close()

    def test_gwt_006_given_extracted_envelope_when_packaged_planner_runs_then_bytecode_does_not_break_checksums(self) -> None:
        fixture = SyntheticPackageRepo()
        try:
            # Given a validated archive extracted beside a clean committed target.
            result = fixture.build("packaged-cli")
            extracted = fixture.output("extracted")
            target = fixture.output("target")
            with zipfile.ZipFile(Path(result["zip"])) as archive:
                archive.extractall(extracted)
            target.mkdir()
            git(target, "init", "-q")
            git(target, "config", "user.name", "Fixture")
            git(target, "config", "user.email", "fixture@example.invalid")
            (target / "baseline.txt").write_text("baseline\n", encoding="utf-8", newline="\n")
            git(target, "add", "baseline.txt")
            git(target, "commit", "-qm", "target baseline")
            package_root = extracted / "fixture-v1.0.0"
            planner = package_root / "payload/.ai/scripts/plan-ai-context-package-apply.py"
            # And the envelope declares the exact target-side dependency.
            self.assertEqual("PyYAML==6.0.3\n", (package_root / "requirements.txt").read_text(encoding="utf-8"))
            missing_dependency = subprocess.run(
                [sys.executable, "-S", str(planner), "--help"],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(2, missing_dependency.returncode)
            self.assertIn("-m pip install -r", missing_dependency.stderr)
            self.assertIn(str(package_root / "requirements.txt"), missing_dependency.stderr)
            # When the planner imports its packaged helper before checksum validation.
            completed = subprocess.run(
                [sys.executable, str(planner), "--package-root", str(package_root), "--target-root", str(target)],
                check=False,
                capture_output=True,
                text=True,
            )
            # Then dry-run succeeds and does not add ungoverned bytecode to the envelope.
            self.assertEqual(0, completed.returncode, completed.stderr)
            self.assertIn("Dry run only", completed.stdout)
            self.assertFalse(any(package_root.rglob("*.pyc")))
            self.assertFalse(any(package_root.rglob("__pycache__")))
        finally:
            fixture.close()


class ReleaseWorkflowContractGwtTests(unittest.TestCase):
    @staticmethod
    def load(name: str) -> tuple[dict, str]:
        path = ROOT / ".github/workflows" / name
        text = path.read_text(encoding="utf-8")
        document = yaml.load(text, Loader=yaml.BaseLoader)
        if not isinstance(document, dict):
            raise AssertionError(f"workflow root must be a mapping: {name}")
        return document, text

    def test_gwt_007_given_candidate_workflow_when_inspected_then_it_only_builds_read_only_artifacts(self) -> None:
        # Given the candidate packaging workflow.
        workflow, text = self.load("package-candidate.yml")
        # When its triggers, permissions, and commands are inspected.
        triggers = workflow["on"]
        jobs = workflow["jobs"]
        # Then PR/manual execution is read-only and cannot publish or mutate tags.
        self.assertEqual({"pull_request", "workflow_dispatch"}, set(triggers))
        self.assertEqual({}, workflow["permissions"])
        self.assertEqual(
            {"contents": "read", "issues": "read"},
            jobs["package"]["permissions"],
        )
        self.assertIn("actions/upload-artifact@v7", text)
        self.assertNotIn("actions/upload-artifact@v4", text)
        self.assertIn("--migration-source", text)
        self.assertIn("steps.release.outputs.migration_sources", text)
        self.assertIn("validate-ai-context-release-state.py", text)
        self.assertIn("--phase candidate", text)
        self.assertIn("available=false", text)
        self.assertIn("available=true", text)
        self.assertIn("candidate discovery requires exactly one governed planned or validated release; found none", text)
        self.assertGreaterEqual(text.count("if: steps.release.outputs.available == 'true'"), 5)
        self.assertIn('--output "${RUNNER_TEMP}/release-body.md"', text)
        self.assertIn("${{ runner.temp }}/release-body.md", text)
        self.assertNotIn("--output dist/release-body.md", text)
        self.assertIn('gh release download "${migration_source}"', text)
        self.assertIn('ai-context-dotnet-backend-v${previous_version}.zip.sha256', text)
        self.assertNotIn('--ref "refs/tags/${migration_source}"', text)
        self.assertNotIn("gh release create", text)
        self.assertNotIn("gh release upload", text)
        self.assertNotRegex(text, r"(?m)^\s*(?:git\s+(?:tag|push|update-ref)|gh\s+api\s+.*git/refs)\b")

    def test_gwt_008_given_publish_workflow_when_inspected_then_only_user_tags_authorize_release_writes(self) -> None:
        # Given the release publication workflow.
        workflow, text = self.load("publish-release.yml")
        # When its tag trigger and job permissions are inspected.
        jobs = workflow["jobs"]
        # Then only pushed v-tags trigger it and contents:write is isolated to publish.
        self.assertEqual(["v*"], workflow["on"]["push"]["tags"])
        self.assertEqual({}, workflow["permissions"])
        self.assertEqual(
            {"contents": "read", "issues": "read"},
            jobs["build"]["permissions"],
        )
        self.assertEqual({"contents": "write"}, jobs["publish"]["permissions"])
        self.assertEqual("ai-context-release", jobs["publish"]["environment"])
        self.assertIn(r"^v[0-9]+\.[0-9]+\.[0-9]+$", text)
        self.assertIn('--ref "refs/tags/${GITHUB_REF_NAME}"', text)
        self.assertIn("--migration-source", text)
        self.assertIn("steps.release.outputs.migration_sources", text)
        self.assertIn('gh release download "${migration_source}"', text)
        self.assertIn('ai-context-dotnet-backend-v${previous_version}.zip.sha256', text)
        self.assertNotIn('--ref "refs/tags/${migration_source}"', text)
        self.assertIn("validate-ai-context-release-state.py", text)
        self.assertIn("--phase tag", text)
        self.assertIn("actions/upload-artifact@v7", text)
        self.assertIn("actions/download-artifact@v8", text)
        self.assertNotIn("actions/upload-artifact@v4", text)
        self.assertNotIn("actions/download-artifact@v5", text)

    def test_gwt_009_given_publish_commands_when_inspected_then_draft_precedes_publish_and_tags_never_mutate(self) -> None:
        # Given the commands used to create, verify, and publish a release.
        _, text = self.load("publish-release.yml")
        # When mutation boundaries and ordering are inspected.
        draft_position = text.find("gh release create")
        publish_position = text.find("--draft=false")
        # Then an owned draft is created/resumed before publication, while Git refs remain read-only.
        self.assertGreaterEqual(draft_position, 0)
        self.assertGreater(publish_position, draft_position)
        self.assertIn("gh release view", text)
        self.assertIn("ai-context-release-automation:", text)
        self.assertNotRegex(text, r"(?m)^\s*(?:git\s+(?:tag|push|update-ref)|gh\s+api\s+.*git/refs)\b")


class PayloadReferenceIntegrityGwtTests(unittest.TestCase):
    def test_gwt_010_given_packaged_text_links_excluded_source_workflow_when_built_then_it_fails_closed(self) -> None:
        fixture = SyntheticPackageRepo()
        try:
            # Given an allowlisted Markdown file links to a concrete excluded source workflow instance.
            (fixture.root / "docs/rule.md").write_text(
                "See `.dev/workflows/2026-05-source-only/report.md`.\n",
                encoding="utf-8",
                newline="\n",
            )
            git(fixture.root, "add", "docs/rule.md")
            git(fixture.root, "commit", "-qm", "add forbidden source backlink")
            # When the deterministic builder validates payload references.
            # Then it rejects the backlink even though the referring file itself is allowlisted.
            with self.assertRaisesRegex(PACKAGE.PackageError, "excluded source lifecycle"):
                fixture.build("forbidden-reference")
        finally:
            fixture.close()

    def test_gwt_011_given_generic_lifecycle_placeholders_when_built_then_they_remain_portable(self) -> None:
        fixture = SyntheticPackageRepo()
        try:
            # Given portable documentation uses placeholders and globs rather than a source instance.
            (fixture.root / "docs/rule.md").write_text(
                "Use `.dev/workflows/<workflow-id>/report.md` and `.dev/backlog/items/*.yaml`.\n",
                encoding="utf-8",
                newline="\n",
            )
            git(fixture.root, "add", "docs/rule.md")
            git(fixture.root, "commit", "-qm", "add portable lifecycle placeholders")
            # When the package is built, then generic target-side contracts remain valid.
            result = fixture.build("portable-placeholders")
            self.assertTrue(Path(result["zip"]).is_file())
        finally:
            fixture.close()

    def test_gwt_011a_given_missing_local_navigation_when_built_then_it_fails_closed(self) -> None:
        fixture = SyntheticPackageRepo()
        try:
            (fixture.root / "docs/rule.md").write_text(
                "[missing portable target](missing.md)\n",
                encoding="utf-8",
                newline="\n",
            )
            git(fixture.root, "add", "docs/rule.md")
            git(fixture.root, "commit", "-qm", "add missing payload navigation")
            with self.assertRaisesRegex(PACKAGE.PackageError, "navigation targets are missing"):
                fixture.build("missing-navigation")
        finally:
            fixture.close()

    def test_gwt_011b_given_missing_actionable_command_target_when_built_then_it_fails_closed(self) -> None:
        fixture = SyntheticPackageRepo()
        try:
            (fixture.root / "docs/rule.md").write_text(
                "```powershell\npython .ai/scripts/missing.py\n```\n",
                encoding="utf-8",
                newline="\n",
            )
            git(fixture.root, "add", "docs/rule.md")
            git(fixture.root, "commit", "-qm", "add missing payload command")
            with self.assertRaisesRegex(PACKAGE.PackageError, "actionable command targets are missing"):
                fixture.build("missing-command")
        finally:
            fixture.close()


class VersionedMigrationPackagingGwtTests(unittest.TestCase):
    def test_gwt_012_given_no_prior_release_when_schema_v2_candidate_is_built_then_clean_install_is_independent(self) -> None:
        fixture = SyntheticPackageRepo()
        try:
            # Given an incoming package with no upgrade source.
            # When schema v2 is built for a clean installation.
            result = fixture.build("clean-install-v2", "1.0.0")
            root = fixture.extract(result, "clean-install-v2-extracted")
            migration = yaml.safe_load((root / "metadata/migration.yaml").read_text(encoding="utf-8"))
            # Then clean-install operations are first-class and no synthetic previous version is needed.
            self.assertEqual("3.0.0", migration["schema_version"])
            self.assertEqual(
                "single-versioned-componentized-release",
                migration["selection"]["release_model"],
            )
            self.assertTrue(
                all(
                    operation["component_id"] == "software-development-core"
                    for operation in migration["clean_install"]["operations"]
                )
            )
            self.assertIn("clean_install", migration)
            self.assertIsInstance(migration["clean_install"]["operations"], list)
            self.assertEqual([], migration["sources"])
        finally:
            fixture.close()

    def test_gwt_013_given_multiple_exact_prior_inventories_when_schema_v2_candidate_is_built_then_sources_are_ordered_and_bound(self) -> None:
        fixture = SyntheticPackageRepo()
        try:
            # Given immutable inventories for two supported prior releases.
            v080 = fixture.build("v080", "0.8.0")
            v080_files = fixture.extract(v080, "v080-extracted") / "metadata/files.yaml"
            (fixture.root / "docs/rule.md").write_text("v090 rule\n", encoding="utf-8", newline="\n")
            git(fixture.root, "add", "docs/rule.md")
            git(fixture.root, "commit", "-qm", "v0.9.0 source")
            v090 = fixture.build("v090", "0.9.0")
            v090_files = fixture.extract(v090, "v090-extracted") / "metadata/files.yaml"
            (fixture.root / "docs/rule.md").write_text("v100 rule\n", encoding="utf-8", newline="\n")
            git(fixture.root, "add", "docs/rule.md")
            git(fixture.root, "commit", "-qm", "v1.0.0 source")
            fixture.ensure_release("1.0.0", ["v0.8.0", "v0.9.0"])

            # When the builder receives the exact version-and-inventory pairs out of order.
            result = PACKAGE.build_package(
                fixture.root,
                "HEAD",
                "1.0.0",
                fixture.output("v2-candidate"),
                fixture.profile,
                previous_sources=[(v090_files, "0.9.0"), (v080_files, "0.8.0")],
            )
            migration = yaml.safe_load(
                (fixture.extract(result, "v2-candidate-extracted") / "metadata/migration.yaml").read_text(encoding="utf-8")
            )
            # Then source selection identity is retained and serialized in ascending version order.
            self.assertEqual(["0.8.0", "0.9.0"], [source["version"] for source in migration["sources"]])
            self.assertEqual(
                [PACKAGE.sha256_bytes(v080_files.read_bytes()), PACKAGE.sha256_bytes(v090_files.read_bytes())],
                [source["manifest_sha256"] for source in migration["sources"]],
            )
            self.assertTrue(all(isinstance(source["operations"], list) for source in migration["sources"]))
        finally:
            fixture.close()

    def test_gwt_014_given_governed_previous_inventory_when_built_then_versioned_operations_apply(self) -> None:
        fixture = SyntheticPackageRepo()
        try:
            # Given an extracted governed previous package and an immutable incoming commit.
            previous_result = fixture.build("previous", "0.9.0")
            previous_root = fixture.extract(previous_result, "previous-extracted")
            previous_files = previous_root / "metadata/files.yaml"
            (fixture.root / "docs/rule.md").write_text(
                "incoming rule\n", encoding="utf-8", newline="\n"
            )
            (fixture.root / "docs/remove.md").unlink()
            (fixture.root / "docs/old-name.md").rename(fixture.root / "docs/new-name.md")
            (fixture.root / "docs/add.md").write_text(
                "added\n", encoding="utf-8", newline="\n"
            )
            git(fixture.root, "add", "-A")
            git(fixture.root, "commit", "-qm", "incoming package source")

            # When the candidate is built with the exact previous files manifest.
            candidate_result = fixture.build(
                "candidate", "1.0.0", previous_files, "0.9.0"
            )
            candidate_root = fixture.extract(candidate_result, "candidate-extracted")
            migration = yaml.safe_load(
                (candidate_root / "metadata/migration.yaml").read_text(encoding="utf-8")
            )

            # Then migration identity and every existing operation kind are deterministic.
            self.assertEqual("3.0.0", migration["schema_version"])
            self.assertEqual("0.9.0", migration["sources"][0]["version"])
            self.assertEqual(
                PACKAGE.sha256_bytes(previous_files.read_bytes()),
                migration["sources"][0]["manifest_sha256"],
            )
            self.assertEqual(
                {"add", "replace", "remove", "rename"},
                {item["kind"] for item in migration["sources"][0]["operations"]},
            )
            self.assertEqual(
                sorted(item["id"] for item in migration["sources"][0]["operations"]),
                [item["id"] for item in migration["sources"][0]["operations"]],
            )

            # And the planner from the extracted candidate upgrades the extracted base.
            target = fixture.output("upgrade-target")
            shutil.copytree(previous_root / "payload", target)
            provenance = target / ".dev/ai-context/provenance.yaml"
            provenance.parent.mkdir(parents=True, exist_ok=True)
            provenance.write_text(
                yaml.safe_dump(
                    {
                        "selection": {
                            "release_model": "single-versioned-componentized-release",
                            "mandatory_components": [
                                "software-development-core",
                                "ai-context-lifecycle-core",
                            ],
                            "profiles": ["dotnet-backend"],
                            "providers": {
                                "repo-backlog": {
                                    "enabled": False,
                                    "preservation": "preserve-existing-if-recorded",
                                }
                            },
                        }
                    },
                    sort_keys=False,
                ),
                encoding="utf-8",
                newline="\n",
            )
            git(target, "init", "-q")
            git(target, "config", "user.name", "Fixture")
            git(target, "config", "user.email", "fixture@example.invalid")
            git(target, "add", ".")
            git(target, "commit", "-qm", "governed previous package")
            planner = candidate_root / "payload/.ai/scripts/plan-ai-context-package-apply.py"
            applied = subprocess.run(
                [
                    sys.executable,
                    str(planner),
                    "--package-root",
                    str(candidate_root),
                    "--target-root",
                    str(target),
                    "--previous-files",
                    str(previous_files),
                    "--previous-version",
                    "0.9.0",
                    "--apply",
                ],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(0, applied.returncode, applied.stdout + applied.stderr)
            self.assertEqual(b"incoming rule\n", (target / "docs/rule.md").read_bytes())
            self.assertFalse((target / "docs/remove.md").exists())
            self.assertFalse((target / "docs/old-name.md").exists())
            self.assertEqual(b"renamed bytes\n", (target / "docs/new-name.md").read_bytes())
            self.assertEqual(b"added\n", (target / "docs/add.md").read_bytes())
        finally:
            fixture.close()

    def test_gwt_015_given_partial_previous_identity_when_built_then_it_fails_closed(self) -> None:
        fixture = SyntheticPackageRepo()
        try:
            # Given only one half of the previous-release identity.
            previous_result = fixture.build("previous", "0.9.0")
            previous_root = fixture.extract(previous_result, "previous-extracted")
            previous_files = previous_root / "metadata/files.yaml"

            # When either the version or manifest is omitted, then building fails closed.
            with self.assertRaisesRegex(PACKAGE.PackageError, "supplied together"):
                fixture.build("missing-version", previous_files=previous_files)
            with self.assertRaisesRegex(PACKAGE.PackageError, "supplied together"):
                fixture.build("missing-manifest", previous_version="0.9.0")
        finally:
            fixture.close()

    # Historical pre-v0.6 end-to-end fixtures remain readable evidence, but are
    # intentionally outside unittest discovery. Active upgrade gates begin at
    # v0.6.0 and exercise one immediate-predecessor route per candidate.
    def historical_gwt_016_given_real_v030_package_when_candidate_is_extracted_then_upgrade_applies(self) -> None:
        with tempfile.TemporaryDirectory(prefix="ai-context-real-upgrade-") as temp_value:
            temp = Path(temp_value)

            # Given the immutable published v0.3.0 tree is built and extracted.
            previous_result = PACKAGE.build_package(
                ROOT, "v0.3.0", "0.3.0", temp / "previous"
            )
            previous_extract = temp / "previous-extracted"
            with zipfile.ZipFile(Path(previous_result["zip"])) as archive:
                archive.extractall(previous_extract)
            previous_root = previous_extract / "ai-context-dotnet-backend-v0.3.0"
            previous_files = previous_root / "metadata/files.yaml"

            # When the current immutable candidate is built against that exact inventory.
            candidate_result = PACKAGE.build_package(
                ROOT,
                "HEAD",
                "0.4.1",
                temp / "candidate",
                previous_files_path=previous_files,
                previous_version_value="0.3.0",
            )
            PACKAGE.validate_sidecar(Path(candidate_result["zip"]))
            PACKAGE.validate_sidecar(Path(candidate_result["tar_gz"]))
            self.assertEqual(
                PACKAGE.validate_archive(Path(candidate_result["zip"])),
                PACKAGE.validate_archive(Path(candidate_result["tar_gz"])),
            )
            candidate_extract = temp / "candidate-extracted"
            with zipfile.ZipFile(Path(candidate_result["zip"])) as archive:
                archive.extractall(candidate_extract)
            candidate_root = candidate_extract / "ai-context-dotnet-backend-v0.4.1"
            migration = yaml.safe_load(
                (candidate_root / "metadata/migration.yaml").read_text(encoding="utf-8")
            )
            candidate_payload = candidate_root / "payload"
            self.assertFalse(
                (candidate_payload / ".ai/scripts/tests/test_ai_context_version_governance.py").exists()
            )
            self.assertFalse(
                (candidate_payload / ".ai/scripts/tests/test_ai_context_packaging.py").exists()
            )
            self.assertFalse(
                (candidate_payload / ".ai/scripts/ai_context_package.py").exists()
            )
            self.assertTrue(
                (candidate_payload / ".ai/scripts/tests/test_ai_context_package_apply.py").is_file()
            )
            self.assertEqual("0.3.0", migration["sources"][0]["version"])
            self.assertEqual(
                PACKAGE.sha256_bytes(previous_files.read_bytes()),
                migration["sources"][0]["manifest_sha256"],
            )
            self.assertGreater(len(migration["sources"][0]["operations"]), 100)

            # Then the extracted candidate planner dry-runs and applies to a real v0.3.0 payload.
            target = temp / "target"
            shutil.copytree(previous_root / "payload", target)
            git(target, "init", "-q")
            git(target, "config", "user.name", "Fixture")
            git(target, "config", "user.email", "fixture@example.invalid")
            git(target, "add", ".")
            git(target, "commit", "-qm", "published v0.3.0 package baseline")
            planner = candidate_root / "payload/.ai/scripts/plan-ai-context-package-apply.py"
            plan_path = temp / "plan.yaml"
            dry_run = subprocess.run(
                [
                    sys.executable,
                    str(planner),
                    "--package-root",
                    str(candidate_root),
                    "--target-root",
                    str(target),
                    "--previous-files",
                    str(previous_files),
                    "--previous-version",
                    "0.3.0",
                    "--plan-output",
                    str(plan_path),
                ],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(0, dry_run.returncode, dry_run.stdout + dry_run.stderr)
            plan = yaml.safe_load(plan_path.read_text(encoding="utf-8"))
            acknowledgements = [
                item["id"] for item in plan["operations"] if item["action"] == "reconcile"
            ]
            apply_arguments = [
                sys.executable,
                str(planner),
                "--package-root",
                str(candidate_root),
                "--target-root",
                str(target),
                "--previous-files",
                str(previous_files),
                "--previous-version",
                "0.3.0",
                "--apply",
            ]
            for operation_id in acknowledgements:
                apply_arguments.extend(["--acknowledge", operation_id])
            applied = subprocess.run(
                apply_arguments,
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(0, applied.returncode, applied.stdout + applied.stderr)
            receipt = yaml.safe_load(
                (target / ".dev/AI-CONTEXT-APPLY-PENDING.yaml").read_text(
                    encoding="utf-8"
                )
            )
            self.assertEqual("0.4.1", receipt["package_version"])
            self.assertEqual(sorted(acknowledgements), receipt["skipped_reconciliation_ids"])

    def historical_gwt_017_given_four_real_supported_sources_when_one_v050_candidate_is_built_then_each_upgrades_without_overwriting_target_truth(self) -> None:
        with tempfile.TemporaryDirectory(prefix="ai-context-real-multi-source-") as temp_value:
            temp = Path(temp_value)
            previous_roots: dict[str, Path] = {}
            source_inputs: list[tuple[Path, str]] = []
            v030_files: Path | None = None

            # Given real extracted packages for every supported v0.5.0 source.
            for version in ("0.3.0", "0.4.0", "0.4.1", "0.4.2"):
                result = PACKAGE.build_package(
                    ROOT,
                    f"v{version}",
                    version,
                    temp / f"previous-{version}",
                    previous_files_path=(
                        v030_files if version in {"0.4.1", "0.4.2"} else None
                    ),
                    previous_version_value=(
                        "0.3.0" if version in {"0.4.1", "0.4.2"} else None
                    ),
                )
                extract = temp / f"previous-{version}-extracted"
                with zipfile.ZipFile(Path(result["zip"])) as archive:
                    archive.extractall(extract)
                package_root = extract / f"ai-context-dotnet-backend-v{version}"
                previous_roots[version] = package_root
                if version == "0.3.0":
                    v030_files = package_root / "metadata/files.yaml"
                source_inputs.append(
                    (package_root / "metadata/files.yaml", version)
                )

            # When one immutable v0.5.0 candidate binds all four inventories.
            candidate_result = PACKAGE.build_package(
                ROOT,
                "HEAD",
                "0.5.0",
                temp / "candidate",
                previous_sources=source_inputs,
            )
            PACKAGE.validate_sidecar(Path(candidate_result["zip"]))
            PACKAGE.validate_sidecar(Path(candidate_result["tar_gz"]))
            self.assertEqual(
                PACKAGE.validate_archive(Path(candidate_result["zip"])),
                PACKAGE.validate_archive(Path(candidate_result["tar_gz"])),
            )
            candidate_extract = temp / "candidate-extracted"
            with zipfile.ZipFile(Path(candidate_result["zip"])) as archive:
                archive.extractall(candidate_extract)
            candidate_root = candidate_extract / "ai-context-dotnet-backend-v0.5.0"
            migration = yaml.safe_load(
                (candidate_root / "metadata/migration.yaml").read_text(
                    encoding="utf-8"
                )
            )
            self.assertEqual(
                ["0.3.0", "0.4.0", "0.4.1", "0.4.2"],
                [source["version"] for source in migration["sources"]],
            )

            # Then every exact source upgrades while target templates and local
            # managed overrides remain byte-identical after acknowledgement.
            planner = (
                candidate_root
                / "payload/.ai/scripts/plan-ai-context-package-apply.py"
            )
            for version, previous_root in previous_roots.items():
                target = temp / f"target-{version}"
                shutil.copytree(previous_root / "payload", target)
                managed_override = (
                    target / ".ai/scripts/plan-ai-context-package-apply.py"
                )
                target_template = target / "AGENTS.md"
                self.assertTrue(managed_override.is_file())
                self.assertTrue(target_template.is_file())
                managed_bytes = f"local managed override from {version}\n".encode()
                target_bytes = f"target-owned AGENTS from {version}\n".encode()
                managed_override.write_bytes(managed_bytes)
                target_template.write_bytes(target_bytes)
                git(target, "init", "-q")
                git(target, "config", "user.name", "Fixture")
                git(target, "config", "user.email", "fixture@example.invalid")
                git(target, "add", ".")
                git(target, "commit", "-qm", f"target v{version} with local truth")
                plan_path = temp / f"plan-{version}.yaml"
                previous_files = previous_root / "metadata/files.yaml"
                dry_run = subprocess.run(
                    [
                        sys.executable,
                        str(planner),
                        "--package-root",
                        str(candidate_root),
                        "--target-root",
                        str(target),
                        "--previous-version",
                        version,
                        "--previous-files",
                        str(previous_files),
                        "--plan-output",
                        str(plan_path),
                    ],
                    check=False,
                    capture_output=True,
                    text=True,
                )
                self.assertEqual(
                    0, dry_run.returncode, dry_run.stdout + dry_run.stderr
                )
                plan = yaml.safe_load(plan_path.read_text(encoding="utf-8"))
                managed_plan = next(
                    item
                    for item in plan["operations"]
                    if item["path"]
                    == ".ai/scripts/plan-ai-context-package-apply.py"
                )
                self.assertEqual("reconcile", managed_plan["action"])
                acknowledgements = [
                    item["id"]
                    for item in plan["operations"]
                    if item["action"] == "reconcile"
                ]
                apply_arguments = [
                    sys.executable,
                    str(planner),
                    "--package-root",
                    str(candidate_root),
                    "--target-root",
                    str(target),
                    "--previous-version",
                    version,
                    "--previous-files",
                    str(previous_files),
                    "--apply",
                ]
                for operation_id in acknowledgements:
                    apply_arguments.extend(["--acknowledge", operation_id])
                applied = subprocess.run(
                    apply_arguments,
                    check=False,
                    capture_output=True,
                    text=True,
                )
                self.assertEqual(
                    0, applied.returncode, applied.stdout + applied.stderr
                )
                self.assertEqual(managed_bytes, managed_override.read_bytes())
                self.assertEqual(target_bytes, target_template.read_bytes())
                receipt = yaml.safe_load(
                    (target / ".dev/AI-CONTEXT-APPLY-PENDING.yaml").read_text(
                        encoding="utf-8"
                    )
                )
                self.assertEqual("0.5.0", receipt["package_version"])
                self.assertEqual(
                    sorted(acknowledgements),
                    receipt["skipped_reconciliation_ids"],
                )

    @unittest.skipUnless(
        os.environ.get("AI_CONTEXT_DOWNSTREAM_REPO"),
        "set AI_CONTEXT_DOWNSTREAM_REPO for the retained downstream integration gate",
    )
    def historical_gwt_018_given_retained_v040_downstream_when_v050_candidate_applies_then_declared_local_overrides_are_preserved(self) -> None:
        downstream = Path(os.environ["AI_CONTEXT_DOWNSTREAM_REPO"]).resolve()
        source_manifest = yaml.safe_load(
            (downstream / ".dev/AI-CONTEXT-SOURCE.yaml").read_text(encoding="utf-8")
        )
        self.assertEqual("v0.4.0", source_manifest["source"]["version"])
        self.assertEqual(
            "",
            subprocess.run(
                [
                    "git",
                    "-C",
                    str(downstream),
                    "status",
                    "--porcelain",
                    "--untracked-files=all",
                ],
                check=True,
                capture_output=True,
                text=True,
            ).stdout,
        )

        with tempfile.TemporaryDirectory(prefix="ai-context-downstream-v050-") as temp_value:
            temp = Path(temp_value)
            source_inputs: list[tuple[Path, str]] = []
            previous_roots: dict[str, Path] = {}
            v030_files: Path | None = None
            for version in ("0.3.0", "0.4.0", "0.4.1", "0.4.2"):
                result = PACKAGE.build_package(
                    ROOT,
                    f"v{version}",
                    version,
                    temp / f"previous-{version}",
                    previous_files_path=(
                        v030_files if version in {"0.4.1", "0.4.2"} else None
                    ),
                    previous_version_value=(
                        "0.3.0" if version in {"0.4.1", "0.4.2"} else None
                    ),
                )
                extract = temp / f"previous-{version}-extracted"
                with zipfile.ZipFile(Path(result["zip"])) as archive:
                    archive.extractall(extract)
                package_root = extract / f"ai-context-dotnet-backend-v{version}"
                previous_roots[version] = package_root
                if version == "0.3.0":
                    v030_files = package_root / "metadata/files.yaml"
                source_inputs.append(
                    (package_root / "metadata/files.yaml", version)
                )
            candidate_result = PACKAGE.build_package(
                ROOT,
                "HEAD",
                "0.5.0",
                temp / "candidate",
                previous_sources=source_inputs,
            )
            candidate_extract = temp / "candidate-extracted"
            with zipfile.ZipFile(Path(candidate_result["zip"])) as archive:
                archive.extractall(candidate_extract)
            candidate_root = candidate_extract / "ai-context-dotnet-backend-v0.5.0"
            target = temp / "target"
            subprocess.run(
                ["git", "clone", "--local", "--quiet", str(downstream), str(target)],
                check=True,
                capture_output=True,
                text=True,
            )

            declared_paths = {
                path
                for override in source_manifest["local_overrides"]
                for path in override["paths"]
            }
            preserved = {
                path: (target / path).read_bytes()
                for path in declared_paths
                if (target / path).is_file()
            }
            self.assertGreater(len(preserved), 20)
            planner = (
                candidate_root
                / "payload/.ai/scripts/plan-ai-context-package-apply.py"
            )
            plan_path = temp / "downstream-plan.yaml"
            previous_files = (
                previous_roots["0.4.0"] / "metadata/files.yaml"
            )
            dry_run = subprocess.run(
                [
                    sys.executable,
                    str(planner),
                    "--package-root",
                    str(candidate_root),
                    "--target-root",
                    str(target),
                    "--previous-version",
                    "0.4.0",
                    "--previous-files",
                    str(previous_files),
                    "--plan-output",
                    str(plan_path),
                ],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(0, dry_run.returncode, dry_run.stdout + dry_run.stderr)
            plan = yaml.safe_load(plan_path.read_text(encoding="utf-8"))
            acknowledgements = [
                item["id"]
                for item in plan["operations"]
                if item["action"] == "reconcile"
            ]
            apply_arguments = [
                sys.executable,
                str(planner),
                "--package-root",
                str(candidate_root),
                "--target-root",
                str(target),
                "--previous-version",
                "0.4.0",
                "--previous-files",
                str(previous_files),
                "--apply",
            ]
            for operation_id in acknowledgements:
                apply_arguments.extend(["--acknowledge", operation_id])
            applied = subprocess.run(
                apply_arguments,
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(0, applied.returncode, applied.stdout + applied.stderr)
            self.assertEqual(
                [],
                [
                    path
                    for path, before in preserved.items()
                    if not (target / path).is_file()
                    or (target / path).read_bytes() != before
                ],
            )
            receipt = yaml.safe_load(
                (target / ".dev/AI-CONTEXT-APPLY-PENDING.yaml").read_text(
                    encoding="utf-8"
                )
            )
            self.assertEqual("0.5.0", receipt["package_version"])
            self.assertEqual(
                sorted(acknowledgements),
                receipt["skipped_reconciliation_ids"],
            )

    def test_gwt_019_given_current_profile_when_payload_is_collected_then_all_native_agent_adapters_are_included(self) -> None:
        # Given the immutable current source tree and public package profile.
        tree = PACKAGE.git_tree(ROOT, "HEAD")
        profile = PACKAGE.load_yaml_blob(
            ROOT,
            tree,
            ".ai/distribution/profiles/dotnet-backend.yaml",
        )

        # When the authoritative package engine resolves the payload.
        payload = PACKAGE.collect_payload(ROOT, tree, profile)
        targets = {item.path for item in payload}

        # Then every promoted runtime-native adapter retains its exact path.
        self.assertTrue(
            {
                ".codex/agents/context-translator.toml",
                ".claude/agents/context-translator.md",
                ".github/agents/context-translator.agent.md",
            }
            <= targets
        )

    def test_gwt_020_given_v070_payload_when_candidate_projects_shared_prerequisites_then_clean_install_and_upgrade_keep_portable_commands(self) -> None:
        """CP-2 synthetic proof; it does not mutate source release artifacts."""
        release_root = ROOT / ".dev/releases"
        release_artifacts_before = {
            path.relative_to(ROOT).as_posix(): path.read_bytes()
            for path in release_root.rglob("*")
            if path.is_file()
        }
        try:
            fixture = SyntheticPackageRepo()
        except PermissionError as error:
            self.skipTest(f"temporary synthetic package fixture is blocked by Windows ACL: {error}")
        shared_assets = (
            ".ai/scripts/python_prerequisites.py",
            ".ai/scripts/python-entrypoints.json",
            ".ai/scripts/run-python-entrypoint.sh",
            ".ai/scripts/run-python-entrypoint.ps1",
        )
        portable_paths = (
            ".ai/assets/skills/software-development-orchestrator/scripts/validate-software-development-orchestrator-acceptance.py",
            ".ai/scripts/ai_context_effective_rules.py", ".ai/scripts/ai_context_target_provenance.py",
            ".ai/scripts/plan-ai-context-package-apply.py", ".ai/scripts/resolve-effective-rule-packet.py",
            ".ai/scripts/validate-ai-context-target.py",
            ".ai/scripts/validate-ai-context.py", ".ai/scripts/validate-assessment-artifacts.py",
            ".ai/scripts/validate-dependency-versions.py", ".ai/scripts/validate-file-disposition-manifest.py",
            ".ai/scripts/validate-git-commits.py", ".ai/scripts/validate-shell-assets.py",
            ".ai/scripts/validate-software-development-orchestrator-acceptance.py",
            ".ai/scripts/validate-workflow-artifacts.py", ".ai/scripts/validate-workflow-handoff.py",
        )
        try:
            # Given v0.7.0 already carries every direct portable command path.
            for path in portable_paths:
                target = fixture.root / path
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes((ROOT / path).read_bytes())
            profile_path = fixture.root / fixture.profile
            profile = yaml.safe_load(profile_path.read_text(encoding="utf-8"))
            profile["entries"].append({"id": "portable-skill-cli", "component_id": "software-development-core", "source": ".ai/assets/skills/**", "target": "preserve-relative-path", "ownership": "framework-managed", "install_behavior": "managed"})
            profile_path.write_text(yaml.safe_dump(profile, sort_keys=False), encoding="utf-8", newline="\n")
            git(fixture.root, "add", ".")
            git(fixture.root, "commit", "-qm", "v070 portable command fixture")
            previous = fixture.build("v070", version="0.7.0")
            previous_root = fixture.extract(previous, "v070-extract")
            previous_files = previous_root / "metadata/files.yaml"
            previous_payload = previous_root / "payload"
            direct_bytes = {path: (previous_payload / path).read_bytes() for path in portable_paths}

            # When the candidate adds the shared runtime bytes without renaming direct commands.
            for path in shared_assets:
                target = fixture.root / path
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes((ROOT / path).read_bytes())
            git(fixture.root, "add", ".")
            git(fixture.root, "commit", "-qm", "candidate shared prerequisite fixture")
            candidate = fixture.build("candidate", version="0.8.0", previous_files=previous_files, previous_version="0.7.0")
            candidate_root = fixture.extract(candidate, "candidate-extract")
            candidate_payload = candidate_root / "payload"

            # Then clean install projects the four shared assets and every portable CLI unchanged.
            self.assertTrue(all((candidate_payload / path).is_file() for path in shared_assets))
            self.assertTrue(all((candidate_payload / path).is_file() for path in portable_paths))
            self.assertEqual({path: (candidate_payload / path).read_bytes() for path in portable_paths}, direct_bytes)
            self.assertFalse((candidate_payload / ".dev/validation.local.conf").exists())

            # And the candidate planner upgrades a v0.7 payload while retaining those same paths.
            target = fixture.output("v070-target")
            shutil.copytree(previous_payload, target)
            provenance = target / ".dev/ai-context/provenance.yaml"
            provenance.parent.mkdir(parents=True, exist_ok=True)
            provenance.write_text(
                yaml.safe_dump(
                    {
                        "selection": {
                            "release_model": "single-versioned-componentized-release",
                            "mandatory_components": [
                                "software-development-core",
                                "ai-context-lifecycle-core",
                            ],
                            "profiles": ["dotnet-backend"],
                            "providers": {
                                "repo-backlog": {
                                    "enabled": False,
                                    "preservation": "preserve-existing-if-recorded",
                                }
                            },
                        }
                    },
                    sort_keys=False,
                ),
                encoding="utf-8",
                newline="\n",
            )
            git(target, "init", "-q")
            git(target, "config", "user.name", "Fixture")
            git(target, "config", "user.email", "fixture@example.invalid")
            git(target, "add", ".")
            git(target, "commit", "-qm", "v070 payload")
            planner = candidate_payload / ".ai/scripts/plan-ai-context-package-apply.py"
            applied = subprocess.run([sys.executable, str(planner), "--package-root", str(candidate_root), "--target-root", str(target), "--previous-files", str(previous_files), "--previous-version", "0.7.0", "--apply"], capture_output=True, text=True, check=False)
            self.assertEqual(0, applied.returncode, applied.stdout + applied.stderr)
            self.assertTrue(all((target / path).is_file() for path in shared_assets + portable_paths))
            self.assertEqual(direct_bytes, {path: (target / path).read_bytes() for path in portable_paths})
            self.assertFalse((target / ".dev/validation.local.conf").exists())
            release_artifacts_after = {
                path.relative_to(ROOT).as_posix(): path.read_bytes()
                for path in release_root.rglob("*")
                if path.is_file()
            }
            self.assertEqual(release_artifacts_before, release_artifacts_after)
        finally:
            fixture.close()


if __name__ == "__main__":
    unittest.main()
