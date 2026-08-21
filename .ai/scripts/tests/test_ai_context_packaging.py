#!/usr/bin/env python3
"""GWT integration tests for deterministic packaging and release workflows."""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import shutil
import stat
import sys
import unittest
import uuid
import warnings
import zipfile
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[3]
SCRIPTS = ROOT / ".ai/scripts"
sys.path.insert(0, str(SCRIPTS))
import ai_context_package as PACKAGE  # noqa: E402
import ai_context_target_provenance as TARGET  # noqa: E402


class RepositoryTemporaryDirectory:
    """Use normal workspace ACLs instead of Windows tempfile 0700 ACLs."""

    def __init__(self, prefix: str) -> None:
        # Keep the deepest portable skill entry below the Win32 MAX_PATH
        # boundary even when Git long-path support is not configured.
        root = ROOT / ".tmp/p"
        root.mkdir(parents=True, exist_ok=True)
        self.path = root / uuid.uuid4().hex[:12]
        self.path.mkdir()
        self.name = str(self.path)

    @staticmethod
    def _remove_readonly(function: object, path: str, _: object) -> None:
        os.chmod(path, stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR)
        function(path)  # type: ignore[operator]

    def cleanup(self) -> None:
        if self.path.exists():
            shutil.rmtree(self.path, onerror=self._remove_readonly)

    def __enter__(self) -> str:
        return self.name

    def __exit__(self, *_: object) -> None:
        self.cleanup()


def repository_temporary_directory(prefix: str) -> RepositoryTemporaryDirectory:
    """Keep large source-only fixtures inside the ignored writable workspace."""
    return RepositoryTemporaryDirectory(prefix)


def git(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        ["git", *args], cwd=root, check=False, capture_output=True, text=True
    )
    if result.returncode != 0:
        raise AssertionError(
            f"git {' '.join(args)} failed with exit {result.returncode}: "
            f"{(result.stdout + result.stderr).strip()}"
        )
    return result


class SyntheticPackageRepo:
    """Own a minimal Git-backed package source and isolated output roots."""

    def __init__(self) -> None:
        self._temporary = repository_temporary_directory("ai-context-packaging-")
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
            "# Install fixture\n\n"
            "python -m pip install -r requirements.txt\n\n"
            "python payload/.ai/scripts/validate-ai-context-payload.py --package-root .\n",
            encoding="utf-8",
            newline="\n",
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
            "ai_context_package_validation.py",
            "ai_context_package_apply.py",
            "ai_context_cli_routing.py",
            "ai_context_effective_rules.py",
            "ai_context_target_provenance.py",
            "plan-ai-context-package-apply.py",
            "resolve-effective-rule-packet.py",
            "validate-ai-context-payload.py",
            "python-entrypoints.json",
            "python_prerequisites.py",
        ):
            (self.root / ".ai/scripts" / script).write_bytes((SCRIPTS / script).read_bytes())
        registry = json.loads((SCRIPTS / "python-entrypoints.json").read_text(encoding="utf-8"))
        for entrypoint in registry["entrypoints"]:
            if entrypoint.get("portable") is not True:
                continue
            relative = entrypoint["path"]
            target = self.root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes((ROOT / relative).read_bytes())
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
                "target_owned_reference_patterns": list(
                    PACKAGE.TARGET_OWNED_REFERENCE_PATTERNS
                ),
            },
            "package_validation": {
                "schema_version": "package-validation/v1",
                "authority": {
                    "kind": "incoming-candidate",
                    "validator": {
                        "path": ".ai/scripts/validate-ai-context-payload.py",
                        "argv": [
                            "python",
                            "payload/.ai/scripts/validate-ai-context-payload.py",
                            "--package-root",
                            ".",
                        ],
                    },
                },
                "source_only_tests": {
                    "classification": "source-only",
                    "patterns": [
                        ".ai/scripts/tests/**",
                        ".ai/assets/skills/**/scripts/tests/**",
                    ],
                    "contributes_to_portable_success": False,
                },
                "integrity_policy": {
                    "path_case": "casefold-unique",
                    "payload_text": "all",
                    "text": {
                        "encoding": "utf-8",
                        "line_endings": "lf-only",
                        "terminal_lf": "exactly-one",
                    },
                    "modes": {"allowed": ["0644", "0755"]},
                },
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
                    "id": "fixture-portable-skill-scripts",
                    "component_id": "software-development-core",
                    "source": ".ai/assets/skills/**",
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


def seed_upgrade_target_provenance(
    target: Path, previous_package_root: Path, selection: dict
) -> None:
    """Seed only the exact predecessor authority that an upgrade planner reads."""
    package = yaml.safe_load(
        (previous_package_root / "metadata/package.yaml").read_text(encoding="utf-8")
    )
    source = package["source"]
    provenance = target / ".dev/ai-context/provenance.yaml"
    provenance.parent.mkdir(parents=True, exist_ok=True)
    provenance.write_text(
        yaml.safe_dump(
            {
                "source": {
                    "repository": source["repository"],
                    "release_id": package["release_id"],
                    "version": f"v{package['version']}",
                    "tag": f"v{package['version']}",
                    "commit": source["commit"],
                },
                "selection": selection,
            },
            sort_keys=False,
        ),
        encoding="utf-8",
        newline="\n",
    )


def apply_extracted_upgrade_with_explicit_decision(
    *,
    planner: Path,
    package_root: Path,
    target_root: Path,
    previous_files: Path,
    previous_version: str,
    evidence_root: Path,
) -> subprocess.CompletedProcess[str]:
    """Exercise the public packet-before-mutation upgrade contract in isolation."""
    packet_path = evidence_root / "remediation-packet.json"
    decision_path = evidence_root / "remediation-decision.json"
    evidence_root.mkdir(parents=True, exist_ok=True)
    base_arguments = [
        sys.executable,
        str(planner),
        "--package-root",
        str(package_root),
        "--target-root",
        str(target_root),
        "--previous-files",
        str(previous_files),
        "--previous-version",
        previous_version,
    ]
    prepared = subprocess.run(
        [*base_arguments, "--remediation-packet-output", str(packet_path)],
        check=False,
        capture_output=True,
        text=True,
    )
    if prepared.returncode != 0:
        raise AssertionError(prepared.stdout + prepared.stderr)
    packet = json.loads(packet_path.read_text(encoding="utf-8"))
    proposal = packet["automatic_proposal"]
    package = packet["package"]
    previous_source = packet["provenance"]["source"]
    candidate_provenance, candidate_customizations = TARGET.build_initialization_documents(
        {
            "repository": package["source"]["repository"],
            "release_id": f"REL-v{package['version']}",
            "version": f"v{package['version']}",
            "tag": f"v{package['version']}",
            "commit": package["source"]["commit"],
        },
        packet["selection"],
        "2026-08-20T12:00:00+08:00",
    )
    candidate_provenance["previous_source"] = previous_source
    candidate_provenance["installation"]["last_upgraded_at"] = "2026-08-20T12:00:00+08:00"
    candidate_provenance["last_migration"] = {
        "status": "completed",
        "from_version": f"v{previous_version}",
        "to_version": f"v{package['version']}",
        "completed_at": "2026-08-20T12:00:00+08:00",
        "evidence": "tests/upgrade-finalization.md",
    }

    def canonical_candidate_bytes(document: object) -> bytes:
        return json.dumps(
            document,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        ).encode("utf-8")

    candidate_provenance_bytes = canonical_candidate_bytes(candidate_provenance)
    candidate_customizations_bytes = canonical_candidate_bytes(candidate_customizations)
    (evidence_root / "candidate-provenance.json").write_bytes(candidate_provenance_bytes)
    (evidence_root / "candidate-customizations.json").write_bytes(candidate_customizations_bytes)
    candidate_authority = {
        "provenance_sha256": hashlib.sha256(candidate_provenance_bytes).hexdigest(),
        "customizations_sha256": hashlib.sha256(candidate_customizations_bytes).hexdigest(),
    }
    if candidate_authority != {
        "provenance_sha256": TARGET.canonical_json_digest(candidate_provenance),
        "customizations_sha256": TARGET.canonical_json_digest(candidate_customizations),
    }:
        raise AssertionError("fixture candidate authority must bind retained canonical documents")
    decision = {
        "schema_version": "upgrade-remediation-decision/v1",
        "packet_sha256": packet["canonical_digest"],
        "plan_sha256": packet["plan_sha256"],
        "transaction_id": packet["transaction_id"],
        "status": "approved",
        "owner": "fixture-owner",
        "decided_at": "2026-08-20T12:00:00+08:00",
        "evidence": "fixture-remediation-decision",
        "reason": "exercise explicit package upgrade authorization",
        "accepted_operation_ids": proposal["apply_operation_ids"],
        "reconciliation_ids": proposal["reconciliation_ids"],
        "policy_adoptions": candidate_provenance.get("policy_adoptions"),
        "candidate_authority": candidate_authority,
    }
    decision_path.write_text(
        json.dumps(decision, sort_keys=True, separators=(",", ":")) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return subprocess.run(
        [*base_arguments, "--apply", "--remediation-decision", str(decision_path)],
        check=False,
        capture_output=True,
        text=True,
    )


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

    def test_gwt_000b_given_source_effective_rule_policy_schema_and_evidence_when_built_then_downstream_excludes_them_and_retains_resolver(self) -> None:
        canonical_profile = yaml.safe_load(
            (ROOT / ".ai/distribution/profiles/dotnet-backend.yaml").read_text(
                encoding="utf-8"
            )
        )
        portable_projection = canonical_profile["portable_projection"]
        self.assertEqual(
            {
                "skill_effective_rule_consumption": {
                    "source_pattern": ".ai/assets/skills/*/skill.yaml",
                    "applicability_mode": "initialized-target",
                    "excluded_mode": "framework-source",
                }
            },
            portable_projection,
        )
        self.assertEqual(
            {
                "default": "git-blob-bytes",
                "portable_projection": (
                    "deterministic-yaml-serialization-of-selected-git-blob"
                ),
            },
            canonical_profile["package"]["deterministic"]["content_bytes"],
        )
        target_owned_reference_patterns = canonical_profile["reference_integrity"][
            "target_owned_reference_patterns"
        ]
        self.assertEqual(
            list(PACKAGE.TARGET_OWNED_REFERENCE_PATTERNS),
            target_owned_reference_patterns,
        )
        fixture = SyntheticPackageRepo()
        source_only_paths = (
            ".dev/standards/AI-CONTEXT-SOURCE-EFFECTIVE-RULES.yaml",
            ".dev/standards/AI-CONTEXT-SOURCE-EFFECTIVE-RULE-EVIDENCE.schema.yaml",
            ".dev/workflows/2026-08-20-source-effective-rule/evidence/source-execution.yaml",
        )
        resolver_path = ".ai/scripts/resolve-effective-rule-packet.py"
        skill_path = ".ai/assets/skills/fixture/skill.yaml"
        try:
            for path in source_only_paths:
                target = fixture.root / path
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(
                    "source-only effective-rule execution bytes\n",
                    encoding="utf-8",
                    newline="\n",
                )
            skill = fixture.root / skill_path
            skill.parent.mkdir(parents=True, exist_ok=True)
            skill.write_text(
                yaml.safe_dump(
                    {
                        "name": "fixture",
                        "effective_rule_consumption": {
                            "applicability": {
                                "selector": "applicability_mode",
                                "modes": {
                                    "framework-source": {
                                        "authority": source_only_paths[0],
                                        "evidence": source_only_paths[2],
                                    },
                                    "initialized-target": {
                                        "authority": ".dev/ai-context/provenance.yaml"
                                    },
                                },
                            },
                            "evidence": {
                                "required_by_mode": {
                                    "framework-source": ["source_repository.id"],
                                    "initialized-target": ["target_state.digest"],
                                }
                            },
                            "semantic_consistency": {
                                "stricter_policy_owner": (
                                    "source-governance-owned in framework-source mode; "
                                    "target-owned in initialized-target mode"
                                )
                            },
                            "prohibitions": [
                                (
                                    "Do not require, fabricate, or persist downstream "
                                    "provenance in framework-source mode."
                                )
                            ],
                        },
                    },
                    sort_keys=False,
                ),
                encoding="utf-8",
                newline="\n",
            )
            profile_path = fixture.root / fixture.profile
            profile = yaml.safe_load(profile_path.read_text(encoding="utf-8"))
            profile["portable_projection"] = portable_projection
            profile["reference_integrity"]["target_owned_reference_patterns"] = (
                target_owned_reference_patterns
            )
            profile["payload_user_view"]["capabilities"].append(
                {
                    "capability_id": "fixture-effective-rule-skill",
                    "owner_component": "software-development-core",
                    "path_patterns": [skill_path],
                    "availability": {
                        "core-only": "available",
                        "dotnet-selected": "available",
                    },
                }
            )
            profile["exclusions"].extend(
                [
                    {
                        "id": "source-effective-rule-execution",
                        "classification": "source-only",
                        "patterns": list(source_only_paths[:2]),
                        "reason": "Source applicability policy and schema are not portable.",
                    },
                    {
                        "id": "source-effective-rule-workflow-evidence",
                        "classification": "source-only",
                        "patterns": [".dev/workflows/*/**"],
                        "reason": "Source execution evidence is not portable.",
                    },
                ]
            )
            profile_path.write_text(
                yaml.safe_dump(profile, sort_keys=False), encoding="utf-8", newline="\n"
            )
            git(fixture.root, "add", ".")
            git(fixture.root, "commit", "-qm", "source effective rule packaging fixture")

            result = fixture.build("source-effective-rule-exclusion")
            package_id = str(result["package_id"])
            source_members = {
                f"{package_id}/payload/{path}" for path in source_only_paths
            }
            resolver_member = f"{package_id}/payload/{resolver_path}"
            for archive_name in ("zip", "tar_gz"):
                with self.subTest(archive=archive_name):
                    members = PACKAGE.validate_archive(Path(result[archive_name]))
                    self.assertTrue(source_members.isdisjoint(members))
                    self.assertIn(resolver_member, members)

            payload = fixture.extract(result, "source-effective-rule-extracted") / "payload"
            self.assertTrue((payload / resolver_path).is_file())
            self.assertTrue(
                all(not (payload / path).exists() for path in source_only_paths)
            )
            projected_skill = yaml.safe_load(
                (payload / skill_path).read_text(encoding="utf-8")
            )
            self.assertEqual(
                {"initialized-target"},
                set(
                    projected_skill["effective_rule_consumption"]["applicability"][
                        "modes"
                    ]
                ),
            )
            self.assertNotIn(
                "framework-source",
                (payload / skill_path).read_text(encoding="utf-8"),
            )
            source_skill = yaml.safe_load(skill.read_text(encoding="utf-8"))
            self.assertEqual(
                {"framework-source", "initialized-target"},
                set(
                    source_skill["effective_rule_consumption"]["applicability"][
                        "modes"
                    ]
                ),
            )

            source_skill["effective_rule_consumption"]["applicability"]["modes"][
                "initialized-target"
            ]["authority"] = ".dev/ai-context/unknown.yaml"
            skill.write_text(
                yaml.safe_dump(source_skill, sort_keys=False),
                encoding="utf-8",
                newline="\n",
            )
            git(fixture.root, "add", skill_path)
            git(
                fixture.root,
                "commit",
                "-qm",
                "unlisted target-owned reference fixture",
            )
            with self.assertRaisesRegex(
                PACKAGE.PackageError, r"\.dev/ai-context/unknown\.yaml"
            ):
                fixture.build("source-effective-rule-unlisted-target")
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
        self.assertEqual(
            {
                ".dev/standards/AI-CONTEXT-SOURCE-EFFECTIVE-RULES.yaml",
                ".dev/standards/AI-CONTEXT-SOURCE-EFFECTIVE-RULE-EVIDENCE.schema.yaml",
            },
            set(exclusions["source-effective-rule-execution"]["patterns"]),
        )
        self.assertEqual(
            "source-only",
            exclusions["source-effective-rule-execution"]["classification"],
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

    def test_gwt_0000a_given_template_mapping_claims_component_when_projected_then_profile_authority_fails_closed(self) -> None:
        fixture = SyntheticPackageRepo()
        try:
            portable_root = fixture.root / ".ai/assets/shared/governance"
            portable_root.mkdir(parents=True)
            (portable_root / "POLICY.md").write_text(
                "provider-neutral workflow truth\n", encoding="utf-8", newline="\n"
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
                newline="\n",
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
            profile_path.write_text(
                yaml.safe_dump(profile, sort_keys=False), encoding="utf-8", newline="\n"
            )
            git(fixture.root, "add", ".")
            git(fixture.root, "commit", "-qm", "conflicting component fixture")
            tree = PACKAGE.git_tree(fixture.root, "HEAD")
            committed_profile = PACKAGE.load_yaml_blob(
                fixture.root, tree, fixture.profile
            )
            with self.assertRaisesRegex(
                PACKAGE.PackageError,
                "mapping component_id is forbidden",
            ):
                PACKAGE.collect_payload(fixture.root, tree, committed_profile)
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
            ".ai/scripts/ai_context_cli_routing.py",
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
        provider_contract_assets = (
            ".ai/assets/tech-stacks/dotnet-backend/tooling/"
            "on-demand-mechanical-validation/recipe-manifest.yaml",
            ".ai/assets/tech-stacks/dotnet-backend/tooling/"
            "on-demand-mechanical-validation/provider-contract.yaml",
            ".ai/assets/tech-stacks/dotnet-backend/tooling/"
            "on-demand-mechanical-validation/provider-contract.schema.yaml",
            ".ai/assets/tech-stacks/dotnet-backend/tooling/"
            "on-demand-mechanical-validation/templates/provider-selection.template.yaml",
            ".ai/assets/tech-stacks/dotnet-backend/tooling/"
            "on-demand-mechanical-validation/templates/minimal-diagnostic-analyzer.cs.template",
            ".ai/assets/tech-stacks/dotnet-backend/tooling/"
            "on-demand-mechanical-validation/templates/minimal-diagnostic-analyzer-test.cs.template",
            ".ai/assets/tech-stacks/dotnet-backend/tooling/"
            "on-demand-mechanical-validation/templates/code-fix-decision.md",
        )
        self.assertTrue(
            all(payload[path] == "dotnet-backend" for path in provider_contract_assets)
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

    def test_gwt_004a_given_duplicate_or_casefold_archive_members_when_read_then_it_fails_closed(self) -> None:
        fixture = SyntheticPackageRepo()
        try:
            cases = {
                "duplicate": (
                    ("fixture-v1.0.0/payload/docs/rule.md", b"one\n"),
                    ("fixture-v1.0.0/payload/docs/rule.md", b"two\n"),
                    "duplicate archive member",
                ),
                "casefold": (
                    ("fixture-v1.0.0/payload/docs/Rule.md", b"one\n"),
                    ("fixture-v1.0.0/payload/docs/rule.md", b"two\n"),
                    "case-insensitive archive member collision",
                ),
            }
            for name, (first, second, expected) in cases.items():
                with self.subTest(name=name):
                    path = fixture.output(f"{name}.zip")
                    with warnings.catch_warnings():
                        warnings.simplefilter("ignore", UserWarning)
                        with zipfile.ZipFile(path, "w") as archive:
                            archive.writestr(*first)
                            archive.writestr(*second)
                    with self.assertRaisesRegex(PACKAGE.PackageError, expected):
                        PACKAGE.archive_files(path)
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

            self.assertEqual("2.3.0", package["schema_version"])
            self.assertEqual("2.0.0", inventory["schema_version"])
            self.assertEqual("3.0.0", migration["schema_version"])
            self.assertEqual(package["selection"], migration["selection"])
            self.assertEqual("1.0.0", package["user_view"]["schema_version"])
            self.assertEqual(result["tree"], package["source"]["tree"])
            self.assertEqual(result["commit"], package["source"]["commit"])
            self.assertEqual(
                "package-validation/v1", package["validation"]["schema_version"]
            )
            self.assertTrue((root / "metadata/validation.json").is_file())
            self.assertTrue((root / "metadata/selected-inputs.json").is_file())
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
        self.assertIn("github.event.pull_request.base.sha", text)
        self.assertIn("github.event.pull_request.head.sha", text)
        self.assertIn('--base-commit "${PR_BASE_SHA}"', text)
        self.assertIn('--head-commit "${PR_HEAD_SHA}"', text)
        self.assertIn("${render_status} -eq 3", text)
        self.assertNotIn("candidate discovery requires exactly one governed planned or validated release; found none", text)
        self.assertGreaterEqual(text.count("if: steps.release.outputs.available == 'true'"), 5)
        self.assertIn('--output "${RUNNER_TEMP}/release-body.md"', text)
        self.assertIn("${{ runner.temp }}/release-body.md", text)
        self.assertNotIn("--output dist/release-body.md", text)
        self.assertIn('gh release download "${migration_source}"', text)
        self.assertIn('ai-context-dotnet-backend-v${previous_version}.zip.sha256', text)
        self.assertIn("Validate freshly extracted incoming candidate", text)
        self.assertIn("validate-ai-context-payload.py", text)
        self.assertIn("--package-root .", text)
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

    def test_gwt_011c_given_source_only_terminal_policy_when_index_is_projected_then_it_is_not_a_portable_link(self) -> None:
        # Given the GitHub terminal-close policy is explicitly source-only.
        profile = yaml.safe_load(
            (ROOT / ".ai/distribution/profiles/dotnet-backend.yaml").read_text(
                encoding="utf-8"
            )
        )
        excluded = {
            pattern
            for entry in profile["exclusions"]
            for pattern in entry["patterns"]
        }
        self.assertIn(
            ".dev/standards/GITHUB-TERMINAL-ISSUE-CLOSURE-POLICY.md",
            excluded,
        )

        # When the portable standards index is inspected, then it identifies
        # that policy without creating a local Markdown target the package omits.
        index_text = (ROOT / ".dev/standards/INDEX.MD").read_text(encoding="utf-8")
        self.assertIn("`GITHUB-TERMINAL-ISSUE-CLOSURE-POLICY.md`", index_text)
        self.assertNotIn(
            "](GITHUB-TERMINAL-ISSUE-CLOSURE-POLICY.md)", index_text
        )


class UpgradeRoutePackageProjectionGwtTests(unittest.TestCase):
    """Exercise route planning only through an extracted mandatory-core payload."""

    ROUTE_SCRIPTS = (
        ".ai/scripts/ai_context_upgrade_routes.py",
        ".ai/scripts/plan-ai-context-upgrade.py",
    )
    MULTI_HOP_RUNTIME_SCRIPTS = (
        ".ai/scripts/ai_context_multi_hop_upgrade.py",
    )
    MULTI_HOP_CONTRACT_PATHS = (
        ".ai/assets/skills/ai-context-upgrader/references/"
        "multi-hop-upgrade-transaction-contract.md",
        ".ai/assets/skills/ai-context-upgrader/templates/"
        "multi-hop-upgrade-transaction.template.yaml",
        ".ai/assets/skills/ai-context-upgrader/templates/"
        "multi-hop-upgrade-transaction.schema.yaml",
    )
    MULTI_HOP_CONTRACT_MARKERS = {
        MULTI_HOP_CONTRACT_PATHS[0]: (
            "resolver-result.json",
            "result-to-intent-to-hop-to-checkpoint-to-target",
            "validator.asset",
        ),
        MULTI_HOP_CONTRACT_PATHS[1]: (
            "resolver_result:",
            "validator_path: \"hops/0000/validator.asset\"",
            "supplied matrix_root",
        ),
        MULTI_HOP_CONTRACT_PATHS[2]: (
            "resolver_result:",
            "materialized_validator_pattern",
            "resolver-result -> route-intent -> promoted hop -> checkpoint -> target validation",
        ),
    }
    CORE_COMPONENTS = {
        "software-development-core",
        "ai-context-lifecycle-core",
    }
    PORTABLE_VERSION_POLICY = (
        ".ai/assets/shared/governance/AI-CONTEXT-VERSION-POLICY.md"
    )
    TARGET_VERSION_POLICY = ".dev/standards/AI-CONTEXT-VERSION-POLICY.md"
    PORTABLE_SHARED_REFERENCE_PATHS = (
        ".ai/assets/shared/CLI-EXECUTION-ROUTING-CONTRACT.md",
        ".ai/assets/shared/cli-execution-routing.schema.yaml",
        ".ai/assets/shared/ROLE-EXECUTION-CONTRACT.md",
        ".ai/assets/shared/provider-neutral-capability-registry.yaml",
        ".ai/assets/shared/provider-projection-registry.yaml",
    )

    def test_gwt_021_given_route_assets_when_core_only_payload_is_extracted_then_planner_isolated_and_asset_failures_stay_closed(self) -> None:
        source_profile = yaml.safe_load(
            (ROOT / ".ai/distribution/profiles/dotnet-backend.yaml").read_text(
                encoding="utf-8"
            )
        )
        source_entries = {entry["id"]: entry for entry in source_profile["entries"]}
        runtime_override = next(
            override
            for override in source_entries["ai-runtime-scripts"][
                "component_overrides"
            ]
            if override["component_id"] == "ai-context-lifecycle-core"
        )
        asset_override = next(
            override
            for override in source_entries["canonical-ai-assets"]["component_overrides"]
            if override["component_id"] == "ai-context-lifecycle-core"
        )
        self.assertTrue(
            set(self.ROUTE_SCRIPTS)
            | set(self.MULTI_HOP_RUNTIME_SCRIPTS)
            <= set(runtime_override["patterns"])
        )
        self.assertIn(
            ".ai/assets/skills/ai-context-upgrader/**", asset_override["patterns"]
        )

        skill_spec_path = ROOT / ".ai/assets/skills/ai-context-upgrader/skill.yaml"
        skill_spec = yaml.safe_load(skill_spec_path.read_text(encoding="utf-8"))
        reference_paths = [
            path
            for path in skill_spec["references"]
            if Path(path).suffix.lower() in {".md", ".yaml"}
        ]
        self.assertTrue(reference_paths)
        self.assertTrue(set(self.MULTI_HOP_CONTRACT_PATHS) <= set(reference_paths))

        fixture = SyntheticPackageRepo()
        try:
            fixture_assets = fixture.root / ".ai/assets/skills"
            shutil.copytree(
                ROOT / ".ai/assets/skills/ai-context-upgrader",
                fixture_assets / "ai-context-upgrader",
                ignore=shutil.ignore_patterns("__pycache__"),
            )
            shutil.copytree(
                ROOT / ".ai/assets/skills/ai-context-governance",
                fixture_assets / "ai-context-governance",
                ignore=shutil.ignore_patterns("__pycache__"),
            )
            for path in self.PORTABLE_SHARED_REFERENCE_PATHS:
                target = fixture.root / path
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes((ROOT / path).read_bytes())
            version_policy_target = fixture.root / self.TARGET_VERSION_POLICY
            version_policy_target.parent.mkdir(parents=True, exist_ok=True)
            version_policy_target.write_bytes(
                (ROOT / self.PORTABLE_VERSION_POLICY).read_bytes()
            )
            for path in (
                *self.ROUTE_SCRIPTS,
                *self.MULTI_HOP_RUNTIME_SCRIPTS,
            ):
                target = fixture.root / path
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes((ROOT / path).read_bytes())

            profile_path = fixture.root / fixture.profile
            profile = yaml.safe_load(profile_path.read_text(encoding="utf-8"))
            fixture_entries = {entry["id"]: entry for entry in profile["entries"]}
            fixture_entries["fixture-apply-scripts"]["component_overrides"] = [
                {
                    "component_id": "ai-context-lifecycle-core",
                    "patterns": [
                        *self.ROUTE_SCRIPTS,
                        *self.MULTI_HOP_RUNTIME_SCRIPTS,
                    ],
                }
            ]
            fixture_entries["fixture-portable-skill-scripts"][
                "component_overrides"
            ] = [
                {
                    "component_id": "ai-context-lifecycle-core",
                    "patterns": [
                        ".ai/assets/skills/ai-context-upgrader/**",
                        ".ai/assets/skills/ai-context-governance/**",
                    ],
                }
            ]
            profile["entries"].append(
                {
                    "id": "fixture-shared-upgrade-assets",
                    "component_id": "software-development-core",
                    "source": list(self.PORTABLE_SHARED_REFERENCE_PATHS),
                    "target": "preserve-relative-path",
                    "ownership": "framework-managed",
                    "install_behavior": "managed",
                }
            )
            profile["exclusions"].append(
                {
                    "id": "fixture-source-only-upgrader-compare",
                    "classification": "source-only",
                    "patterns": [
                        ".ai/assets/skills/ai-context-upgrader/scripts/"
                        "compare-ai-context-versions.py"
                    ],
                    "reason": "Source comparison tooling is not portable package truth.",
                }
            )
            profile_path.write_text(
                yaml.safe_dump(profile, sort_keys=False), encoding="utf-8", newline="\n"
            )
            git(fixture.root, "add", ".")
            git(fixture.root, "commit", "-qm", "route package projection fixture")

            package_result = fixture.build("upgrade-route-package")
            package_root = fixture.extract(
                package_result, "upgrade-route-package-extracted"
            )
            inventory = yaml.safe_load(
                (package_root / "metadata/files.yaml").read_text(encoding="utf-8")
            )
            records = {record["path"]: record for record in inventory["files"]}
            self.assertTrue(
                all(
                    records[path]["component_id"] == "ai-context-lifecycle-core"
                    for path in (
                        *self.ROUTE_SCRIPTS,
                        *self.MULTI_HOP_RUNTIME_SCRIPTS,
                    )
                )
            )
            self.assertTrue(
                all(
                    path in records
                    and records[path]["component_id"] in self.CORE_COMPONENTS
                    for path in reference_paths
                )
            )

            core_only = fixture.output("upgrade-route-core-only")
            for path, record in records.items():
                if record["component_id"] not in self.CORE_COMPONENTS:
                    continue
                target = core_only / path
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes((package_root / "payload" / path).read_bytes())
            self.assertTrue(all((core_only / path).is_file() for path in reference_paths))
            self.assertTrue(all((core_only / path).is_file() for path in self.ROUTE_SCRIPTS))
            self.assertTrue(
                all(
                    (core_only / path).is_file()
                    for path in (
                        *self.MULTI_HOP_RUNTIME_SCRIPTS,
                        *self.MULTI_HOP_CONTRACT_PATHS,
                    )
                )
            )
            for path, markers in self.MULTI_HOP_CONTRACT_MARKERS.items():
                projected = (core_only / path).read_text(encoding="utf-8")
                self.assertTrue(
                    all(marker in projected for marker in markers),
                    f"core-only projection lost required multi-hop contract markers: {path}",
                )

            execution_root = fixture.output("upgrade-route-execution")
            target_root = execution_root / "target"
            target_root.mkdir(parents=True)
            target_marker = target_root / "target-owned.txt"
            target_marker.write_bytes(b"retain target bytes\n")
            target_before = {
                path.relative_to(target_root).as_posix(): path.read_bytes()
                for path in target_root.rglob("*")
                if path.is_file()
            }
            matrix_root = execution_root / "matrix"
            matrix_root.mkdir()

            environment = os.environ.copy()
            environment["PYTHONPATH"] = str(core_only / ".ai/scripts")
            resolver_probe = subprocess.run(
                [
                    sys.executable,
                    "-c",
                    "import ai_context_upgrade_routes as route; print(route.__file__)",
                ],
                cwd=execution_root,
                env=environment,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(
                0, resolver_probe.returncode, resolver_probe.stdout + resolver_probe.stderr
            )
            self.assertEqual(
                (core_only / self.ROUTE_SCRIPTS[0]).resolve(),
                Path(resolver_probe.stdout.strip()).resolve(),
            )

            multi_hop_probe = subprocess.run(
                [
                    sys.executable,
                    "-c",
                    (
                        "from pathlib import Path\n"
                        "import ai_context_multi_hop_upgrade as multi_hop\n"
                        "try:\n"
                        "    multi_hop.run_multi_hop_upgrade('unsupported', Path('.'))\n"
                        "except multi_hop.MultiHopUpgradeError as exc:\n"
                        "    print(multi_hop.__file__)\n"
                        "    print(exc)\n"
                        "else:\n"
                        "    raise SystemExit('unsupported action was accepted')\n"
                    ),
                ],
                cwd=execution_root,
                env=environment,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(
                0,
                multi_hop_probe.returncode,
                multi_hop_probe.stdout + multi_hop_probe.stderr,
            )
            multi_hop_lines = multi_hop_probe.stdout.splitlines()
            self.assertEqual(2, len(multi_hop_lines))
            self.assertEqual(
                (core_only / self.MULTI_HOP_RUNTIME_SCRIPTS[0]).resolve(),
                Path(multi_hop_lines[0]).resolve(),
            )
            self.assertEqual("multi-hop operation action is unsupported", multi_hop_lines[1])

            def asset(asset_id: str, path: str, content: bytes) -> dict[str, str]:
                asset_path = matrix_root / path
                asset_path.parent.mkdir(parents=True, exist_ok=True)
                asset_path.write_bytes(content)
                return {
                    "asset_id": asset_id,
                    "path": path,
                    "sha256": hashlib.sha256(content).hexdigest(),
                }

            def canonical_json_asset(asset_id: str, path: str, value: dict) -> dict[str, str]:
                return asset(
                    asset_id,
                    path,
                    (
                        json.dumps(
                            value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
                        )
                        + "\n"
                    ).encode("utf-8"),
                )

            target_manifest = asset(
                "target-manifest", "artifacts/target/manifest.yaml", b"target manifest\n"
            )
            immediate_manifest = asset(
                "immediate-manifest",
                "artifacts/v1.0.0/manifest.yaml",
                b"immediate manifest\n",
            )
            v090_manifest = asset(
                "v090-manifest", "artifacts/v0.9.0/manifest.yaml", b"v090 manifest\n"
            )
            edge_archive = asset("edge-archive", "artifacts/edge/package.tar.gz", b"archive\n")
            edge_artifacts = {
                "archive": edge_archive,
                "checksum": asset(
                    "edge-checksum",
                    "artifacts/edge/SHA256SUMS",
                    f"{edge_archive['sha256']}  package.tar.gz\n".encode("utf-8"),
                ),
                "manifest": asset("edge-manifest", "artifacts/edge/migration.yaml", b"migration\n"),
                "validator": asset("edge-validator", "artifacts/edge/validator.py", b"validator\n"),
            }
            validator_argv = [
                "python",
                edge_artifacts["validator"]["path"],
                "--edge-id",
                "v100-to-v120",
            ]
            validation_output = asset(
                "edge-validation-output",
                "artifacts/edge/validation-output.log",
                b"edge validation output\n",
            )
            validation_report = canonical_json_asset(
                "edge-validation-report",
                "artifacts/edge/validation-report.json",
                {
                    "schema_version": "upgrade-edge-validation/v1",
                    "edge_id": "v100-to-v120",
                    "from_version": "v1.0.0",
                    "to_version": "v1.2.0",
                    "artifacts": edge_artifacts,
                    "validator_argv": validator_argv,
                    "semantic_cutovers": [
                        {
                            "cutover_id": "route-evidence",
                            "required": True,
                            "state": "passed",
                        }
                    ],
                    "outcome": "passed",
                    "exit_code": 0,
                    "output_sha256": validation_output["sha256"],
                },
            )
            deprecation_id = "v060-unsupported"
            deprecation_reason = "fixture deprecation is complete"
            deprecation_notice = canonical_json_asset(
                "v060-notice",
                "deprecations/v060/notice.json",
                {
                    "schema_version": "upgrade-deprecation-notice/v1",
                    "deprecation_id": deprecation_id,
                    "role": "v0.6.0",
                    "origin": "v0.6.0",
                    "target": "v1.2.0",
                    "disposition": "unsupported",
                    "reason": deprecation_reason,
                },
            )
            deprecation_decision = canonical_json_asset(
                "v060-decision",
                "deprecations/v060/owner-decision.json",
                {
                    "schema_version": "upgrade-deprecation-owner-decision/v1",
                    "deprecation_id": deprecation_id,
                    "role": "v0.6.0",
                    "origin": "v0.6.0",
                    "target": "v1.2.0",
                    "status": "approved",
                    "approved": True,
                    "owner": "fixture-governance-owner",
                    "decided_at": "2026-08-20T00:00:00+08:00",
                },
            )
            deprecation_output = asset(
                "v060-validation-output",
                "deprecations/v060/validation-output.log",
                b"deprecation validation output\n",
            )
            deprecation_evidence = {
                "deprecation_notice": deprecation_notice,
                "owner_decision": deprecation_decision,
                "validator": canonical_json_asset(
                    "v060-validator",
                    "deprecations/v060/validation.json",
                    {
                        "schema_version": "upgrade-deprecation-validation/v1",
                        "deprecation_id": deprecation_id,
                        "role": "v0.6.0",
                        "origin": "v0.6.0",
                        "target": "v1.2.0",
                        "deprecation_notice": deprecation_notice,
                        "owner_decision": deprecation_decision,
                        "outcome": "passed",
                        "exit_code": 0,
                        "output_sha256": deprecation_output["sha256"],
                    },
                ),
                "output": deprecation_output,
            }
            matrix = {
                "schema_version": "1.0",
                "matrix_id": "fixture-upgrade-routes",
                "target": {
                    "version": "v1.2.0",
                    "release_id": "REL-v1.2.0",
                    "commit": "a" * 40,
                    "manifest": target_manifest,
                },
                "retained_origins": [
                    {
                        "role": "immediate-predecessor",
                        "version": "v1.0.0",
                        "release_id": "REL-v1.0.0",
                        "commit": "b" * 40,
                        "manifest": immediate_manifest,
                    },
                    {
                        "role": "v0.9.0",
                        "version": "v0.9.0",
                        "release_id": "REL-v0.9.0",
                        "commit": "c" * 40,
                        "manifest": v090_manifest,
                    },
                ],
                "semantic_cutovers": [
                    {
                        "cutover_id": "route-evidence",
                        "required": True,
                        "description": "fixture route evidence is complete",
                    }
                ],
                "routes": [
                    {
                        "route_id": "v100-to-v120",
                        "origin": "v1.0.0",
                        "target": "v1.2.0",
                        "edges": [
                            {
                                "edge_id": "v100-to-v120",
                                "order": 1,
                                "from_version": "v1.0.0",
                                "to_version": "v1.2.0",
                                "artifacts": edge_artifacts,
                                "semantic_cutovers": [
                                    {"cutover_id": "route-evidence", "state": "passed"}
                                ],
                                "validation": {
                                    "state": "passed",
                                    "validator_argv": validator_argv,
                                    "report": validation_report,
                                    "output": validation_output,
                                },
                            }
                        ],
                    }
                ],
                "deprecations": [
                    {
                        "deprecation_id": deprecation_id,
                        "role": "v0.6.0",
                        "origin": "v0.6.0",
                        "target": "v1.2.0",
                        "disposition": "unsupported",
                        "complete": True,
                        "reason": deprecation_reason,
                        "evidence": deprecation_evidence,
                    }
                ],
            }
            matrix_path = matrix_root / "upgrade-route-matrix.yaml"
            matrix_path.write_text(
                yaml.safe_dump(matrix, sort_keys=False), encoding="utf-8", newline="\n"
            )

            def resolve() -> subprocess.CompletedProcess[str]:
                return subprocess.run(
                    [
                        sys.executable,
                        str(core_only / self.ROUTE_SCRIPTS[1]),
                        "--matrix",
                        str(matrix_path),
                        "--origin",
                        "v1.0.0",
                        "--target",
                        "v1.2.0",
                    ],
                    cwd=execution_root,
                    env=environment,
                    capture_output=True,
                    text=True,
                    check=False,
                )

            direct = resolve()
            self.assertEqual(0, direct.returncode, direct.stdout + direct.stderr)
            direct_result = json.loads(direct.stdout)
            self.assertEqual("direct", direct_result["route_kind"])
            self.assertTrue(direct_result["read_only"])
            self.assertEqual("v100-to-v120", direct_result["selected_route"]["route_id"])

            validator_path = matrix_root / edge_artifacts["validator"]["path"]
            validator_path.unlink()
            missing = resolve()
            self.assertEqual(0, missing.returncode, missing.stdout + missing.stderr)
            missing_result = json.loads(missing.stdout)
            self.assertEqual("reconciliation-required", missing_result["route_kind"])
            self.assertIn(
                "missing-asset",
                {diagnostic["code"] for diagnostic in missing_result["diagnostics"]},
            )

            validator_path.write_bytes(b"tampered validator\n")
            tampered = resolve()
            self.assertEqual(0, tampered.returncode, tampered.stdout + tampered.stderr)
            tampered_result = json.loads(tampered.stdout)
            self.assertEqual("reconciliation-required", tampered_result["route_kind"])
            self.assertIn(
                "tampered-asset",
                {diagnostic["code"] for diagnostic in tampered_result["diagnostics"]},
            )
            self.assertEqual(
                target_before,
                {
                    path.relative_to(target_root).as_posix(): path.read_bytes()
                    for path in target_root.rglob("*")
                    if path.is_file()
                },
            )
        finally:
            fixture.close()


class ProviderRolePackageProjectionGwtTests(unittest.TestCase):
    """Project SAG-003 candidates without inventing provider runtime parity."""

    ROLE_ASSET_IDS = (
        "mechanical-evidence-worker",
        "reconciliation-worker",
        "semantic-governance-analyst",
        "evidence-report-synthesizer",
        "fixed-head-independent-auditor",
    )
    ROLE_ASSET_PATHS = (
        ".ai/assets/sub-agent-role-prompts/mechanical-evidence-worker/sub-agent.yaml",
        ".ai/assets/sub-agent-role-prompts/mechanical-evidence-worker/references/"
        "mechanical-evidence-playbook.md",
        ".ai/assets/sub-agent-role-prompts/reconciliation-worker/sub-agent.yaml",
        ".ai/assets/sub-agent-role-prompts/reconciliation-worker/references/"
        "reconciliation-playbook.md",
        ".ai/assets/sub-agent-role-prompts/semantic-governance-analyst/sub-agent.yaml",
        ".ai/assets/sub-agent-role-prompts/semantic-governance-analyst/references/"
        "semantic-governance-analysis-playbook.md",
        ".ai/assets/sub-agent-role-prompts/evidence-report-synthesizer/sub-agent.yaml",
        ".ai/assets/sub-agent-role-prompts/evidence-report-synthesizer/references/"
        "evidence-report-synthesis-playbook.md",
        ".ai/assets/sub-agent-role-prompts/fixed-head-independent-auditor/sub-agent.yaml",
        ".ai/assets/sub-agent-role-prompts/fixed-head-independent-auditor/references/"
        "fixed-head-independent-audit-playbook.md",
    )
    REGISTRY_PATHS = (
        ".ai/assets/shared/provider-neutral-capability-registry.yaml",
        ".ai/assets/shared/provider-neutral-capability-registry.schema.yaml",
        ".ai/assets/shared/provider-projection-registry.yaml",
        ".ai/assets/shared/provider-projection-registry.schema.yaml",
    )
    BINDING_PATHS = (
        ".ai/assets/skills/ai-context-upgrader/references/role-execution-bindings.yaml",
        ".ai/assets/skills/ai-context-upgrader/references/"
        "role-execution-bindings.schema.yaml",
    )
    DELEGATION_RUN_PATHS = (
        ".ai/assets/skills/ai-context-upgrader/references/delegation-run-contract.md",
        ".ai/assets/skills/ai-context-upgrader/references/"
        "delegation-run-contract.schema.yaml",
        ".ai/assets/skills/ai-context-upgrader/templates/"
        "delegation-run-record.template.yaml",
    )
    CODEX_PROFILE_PATHS = (
        ".codex/agents/bounded-routine-worker.toml",
        ".codex/agents/reconciliation-worker.toml",
        ".codex/agents/semantic-governance-analyst.toml",
        ".codex/agents/evidence-report-synthesizer.toml",
        ".codex/agents/fixed-head-independent-auditor.toml",
    )
    TRANSLATOR_PATHS = (
        ".ai/assets/sub-agent-role-prompts/context-translator/sub-agent.yaml",
        ".ai/assets/sub-agent-role-prompts/context-translator/references/"
        "translation-playbook.md",
        ".codex/agents/context-translator.toml",
        ".claude/agents/context-translator.md",
        ".github/agents/context-translator.agent.md",
    )

    def test_gwt_022_given_provider_role_candidates_when_packaged_then_contracts_and_static_projection_stay_separate(self) -> None:
        source_profile = yaml.safe_load(
            (ROOT / ".ai/distribution/profiles/dotnet-backend.yaml").read_text(
                encoding="utf-8"
            )
        )
        source_entries = {entry["id"]: entry for entry in source_profile["entries"]}
        self.assertEqual(
            {"software-development-core", "ai-context-lifecycle-core", "dotnet-backend"},
            {
                source_entries["canonical-ai-assets"]["component_id"],
                *(
                    override["component_id"]
                    for override in source_entries["canonical-ai-assets"][
                        "component_overrides"
                    ]
                ),
            },
        )
        self.assertEqual(
            {".codex/agents/context-translator.toml", *self.CODEX_PROFILE_PATHS},
            set(source_entries["codex-agent-adapters"]["source"]),
        )

        fixture = SyntheticPackageRepo()
        try:
            projected_paths = (
                *self.ROLE_ASSET_PATHS,
                *self.REGISTRY_PATHS,
                *self.BINDING_PATHS,
                *self.DELEGATION_RUN_PATHS,
                *self.CODEX_PROFILE_PATHS,
                *self.TRANSLATOR_PATHS,
            )
            for path in projected_paths:
                target = fixture.root / path
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes((ROOT / path).read_bytes())

            profile_path = fixture.root / fixture.profile
            profile = yaml.safe_load(profile_path.read_text(encoding="utf-8"))
            profile["entries"].extend(
                [
                    {
                        "id": "fixture-provider-role-assets",
                        "component_id": "software-development-core",
                        "source": [
                            *self.ROLE_ASSET_PATHS,
                            *self.REGISTRY_PATHS,
                            *self.TRANSLATOR_PATHS[:2],
                        ],
                        "target": "preserve-relative-path",
                        "ownership": "framework-managed",
                        "install_behavior": "managed",
                    },
                    {
                        "id": "fixture-codex-role-profiles",
                        "component_id": "software-development-core",
                        "source": [
                            *self.CODEX_PROFILE_PATHS,
                            self.TRANSLATOR_PATHS[2],
                        ],
                        "target": "preserve-relative-path",
                        "ownership": "framework-managed",
                        "install_behavior": "managed",
                    },
                    {
                        "id": "fixture-translator-provider-adapters",
                        "component_id": "software-development-core",
                        "source": list(self.TRANSLATOR_PATHS[3:]),
                        "target": "preserve-relative-path",
                        "ownership": "framework-managed",
                        "install_behavior": "managed",
                    },
                ]
            )
            profile_path.write_text(
                yaml.safe_dump(profile, sort_keys=False), encoding="utf-8", newline="\n"
            )
            git(fixture.root, "add", ".")
            git(fixture.root, "commit", "-qm", "provider role package projection fixture")

            package_result = fixture.build("provider-role-package")
            package_root = fixture.extract(
                package_result, "provider-role-package-extracted"
            )
            inventory = yaml.safe_load(
                (package_root / "metadata/files.yaml").read_text(encoding="utf-8")
            )
            records = {record["path"]: record for record in inventory["files"]}
            self.assertTrue(set(projected_paths) <= set(records))
            self.assertTrue(
                all(
                    records[path]["component_id"] == "software-development-core"
                    for path in projected_paths
                )
            )

            payload_root = package_root / "payload"
            capability_registry = yaml.safe_load(
                (payload_root / self.REGISTRY_PATHS[0]).read_text(encoding="utf-8")
            )
            self.assertEqual(
                set(self.ROLE_ASSET_IDS),
                {
                    capability["role_asset_id"]
                    for capability in capability_registry["capabilities"]
                },
            )
            projection_registry = yaml.safe_load(
                (payload_root / self.REGISTRY_PATHS[2]).read_text(encoding="utf-8")
            )
            self.assertEqual(
                {
                    "root_capability": "frontier",
                    "delegated_capability": "balanced",
                    "quality_posture": "quality-first",
                    "delegation": "optional",
                    "quota_sensitivity": "quota-sensitive",
                    "fallback": "disclosed",
                },
                projection_registry["canonical_contract"]["delegation_intent"],
            )
            self.assertEqual(
                "codex-runtime-configured",
                projection_registry["provider_projections"]["codex"][
                    "configuration_state"
                ],
            )
            self.assertEqual(
                {
                    "schema_version": "1.0",
                    "configuration_scope": "static-provider-projection",
                    "max_concurrent_workers": 2,
                    "fast_priority": "disabled",
                    "model_mismatch_disposition": "advisory-one-prompt",
                    "mismatch_prompt_limit": 1,
                    "mismatch_choice_boundary": "current-vs-recommended/continue-or-switch",
                    "root_preflight": {
                        "recommended_root": {
                            "model": "gpt-5.6-sol",
                            "model_reasoning_effort": "xhigh",
                            "service_tier": "priority",
                        },
                        "observed_current_state": {
                            "active_model": "unknown",
                            "active_reasoning_effort": "unknown",
                            "active_speed_service_tier": "unknown",
                            "configuration_default_inference": "forbidden",
                        },
                        "quota_cost_disclosure": "required-before-switch",
                        "verified_switch_action": {
                            "verification_state": "not-verified",
                            "shortest_verified_ui_or_command": None,
                            "evidence_refs": [],
                        },
                        "unavailable_fallback": {
                            "prompt_required": True,
                            "options": [
                                "gpt-5.6-terra/xhigh",
                                "current-model",
                            ],
                        },
                        "owner_run_fast_priority": {
                            "status": "disabled",
                            "activation": "explicit-owner-choice-required",
                        },
                    },
                    "worker_preference": {
                        "model": "gpt-5.6-terra",
                        "model_reasoning_effort": "max",
                        "unavailable_fallback": "root-sequential",
                    },
                    "terminal_auditor_preference": {
                        "model": "gpt-5.6-sol",
                        "model_reasoning_effort": "max",
                        "unavailable_fallback": "fresh-sol-high-independent-context",
                    },
                },
                projection_registry["provider_projections"]["codex"][
                    "delegation_advisory"
                ],
            )
            self.assertNotIn(
                "delegation_advisory",
                projection_registry["provider_projections"]["claude"],
            )
            self.assertNotIn(
                "delegation_advisory",
                projection_registry["provider_projections"]["copilot"],
            )
            self.assertEqual(
                "claude-runtime-deferred",
                projection_registry["provider_projections"]["claude"][
                    "configuration_state"
                ],
            )
            self.assertEqual(
                "copilot-runtime-deferred",
                projection_registry["provider_projections"]["copilot"][
                    "configuration_state"
                ],
            )
            self.assertEqual(
                {"availability": "unknown", "invocation_evidence": "not-claimed"},
                projection_registry["current_session"],
            )
            self.assertEqual(
                list(self.CODEX_PROFILE_PATHS),
                projection_registry["package_projection"]["profile_paths"],
            )
            delegation_record = yaml.safe_load(
                (payload_root / self.DELEGATION_RUN_PATHS[2]).read_text(encoding="utf-8")
            )
            self.assertEqual("full-recommended", delegation_record["selection"]["mode"])
            self.assertEqual(2, delegation_record["selection"]["max_concurrent_workers"])
            self.assertEqual(0, delegation_record["selection"]["prompt"]["count"])
            self.assertFalse(delegation_record["selection"]["resume"]["repeat_prompt"])

            for role_id in self.ROLE_ASSET_IDS:
                self.assertNotIn(f".claude/agents/{role_id}.md", records)
                self.assertNotIn(f".github/agents/{role_id}.agent.md", records)
            self.assertTrue(set(self.TRANSLATOR_PATHS[2:]) <= set(records))
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
            v090 = fixture.build("v090", "0.9.0")
            v090_files = fixture.extract(v090, "v090-extracted") / "metadata/files.yaml"
            (fixture.root / "docs/rule.md").write_text("v0130 rule\n", encoding="utf-8", newline="\n")
            git(fixture.root, "add", "docs/rule.md")
            git(fixture.root, "commit", "-qm", "v0.13.0 source")
            v0130 = fixture.build("v0130", "0.13.0")
            v0130_files = fixture.extract(v0130, "v0130-extracted") / "metadata/files.yaml"
            (fixture.root / "docs/rule.md").write_text("v100 rule\n", encoding="utf-8", newline="\n")
            git(fixture.root, "add", "docs/rule.md")
            git(fixture.root, "commit", "-qm", "v1.0.0 source")
            fixture.ensure_release("1.0.0", ["v0.9.0", "v0.13.0"])

            # When the builder receives the exact version-and-inventory pairs out of order.
            result = PACKAGE.build_package(
                fixture.root,
                "HEAD",
                "1.0.0",
                fixture.output("v2-candidate"),
                fixture.profile,
                previous_sources=[(v0130_files, "0.13.0"), (v090_files, "0.9.0")],
            )
            migration = yaml.safe_load(
                (fixture.extract(result, "v2-candidate-extracted") / "metadata/migration.yaml").read_text(encoding="utf-8")
            )
            selected_inputs = json.loads(
                (
                    fixture.extract(result, "v2-selected-inputs-extracted")
                    / "metadata/selected-inputs.json"
                ).read_text(encoding="utf-8")
            )
            # Then source selection identity is retained and serialized in ascending version order.
            self.assertEqual(["0.9.0", "0.13.0"], [source["version"] for source in migration["sources"]])
            self.assertEqual(
                ["0.9.0", "0.13.0"],
                [source["version"] for source in selected_inputs["migration_sources"]],
            )
            self.assertEqual(
                [PACKAGE.sha256_bytes(v090_files.read_bytes()), PACKAGE.sha256_bytes(v0130_files.read_bytes())],
                [source["manifest_sha256"] for source in migration["sources"]],
            )
            self.assertTrue(all(isinstance(source["operations"], list) for source in migration["sources"]))
            self.assertEqual(
                PACKAGE.validate_archive(Path(result["zip"])),
                PACKAGE.validate_archive(Path(result["tar_gz"])),
            )
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
            seed_upgrade_target_provenance(
                target,
                previous_root,
                {
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
            )
            git(target, "init", "-q")
            git(target, "config", "user.name", "Fixture")
            git(target, "config", "user.email", "fixture@example.invalid")
            git(target, "add", ".")
            git(target, "commit", "-qm", "governed previous package")
            planner = candidate_root / "payload/.ai/scripts/plan-ai-context-package-apply.py"
            applied = apply_extracted_upgrade_with_explicit_decision(
                planner=planner,
                package_root=candidate_root,
                target_root=target,
                previous_files=previous_files,
                previous_version="0.9.0",
                evidence_root=fixture.output("gwt014-remediation-evidence"),
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
        with repository_temporary_directory("ai-context-real-upgrade-") as temp_value:
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
        with repository_temporary_directory("ai-context-real-multi-source-") as temp_value:
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

        with repository_temporary_directory("ai-context-downstream-v050-") as temp_value:
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
            ".ai/scripts/ai_context_cli_routing.py",
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
            # Given v0.7.0 already carries every registry-declared portable path.
            self.assertTrue(all((fixture.root / path).is_file() for path in portable_paths))
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
            seed_upgrade_target_provenance(
                target,
                previous_root,
                {
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
            )
            git(target, "init", "-q")
            git(target, "config", "user.name", "Fixture")
            git(target, "config", "user.email", "fixture@example.invalid")
            git(target, "add", ".")
            git(target, "commit", "-qm", "v070 payload")
            planner = candidate_payload / ".ai/scripts/plan-ai-context-package-apply.py"
            applied = apply_extracted_upgrade_with_explicit_decision(
                planner=planner,
                package_root=candidate_root,
                target_root=target,
                previous_files=previous_files,
                previous_version="0.7.0",
                evidence_root=fixture.output("gwt020-remediation-evidence"),
            )
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
