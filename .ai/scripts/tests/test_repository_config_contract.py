#!/usr/bin/env python3
"""Fail-closed GWT tests for repository configuration ownership."""

from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
VALIDATOR = REPO_ROOT / ".ai/scripts/validate-repository-config-contract.py"
FIXTURE_PATHS = (
    ".editorconfig",
    ".gitattributes",
    ".ai/assets/skills/ai-context-init/templates/public-root/.editorconfig",
    ".ai/assets/skills/ai-context-init/templates/public-root/.gitattributes",
    ".ai/assets/skills/ai-context-init/templates/public-template-manifest.yaml",
    ".ai/distribution/profiles/dotnet-backend.yaml",
    ".dev/standards/ASSESSMENT-ARTIFACT-POLICY.md",
    ".dev/adr/ADR-001-separate-source-config-from-downstream-templates.md",
    ".dev/adr/INDEX.md",
    ".dev/assessments/ASM-20260722-005/evidence/workservice/"
    "2026-07-22-dev-workflow-skill-comparison.md",
)


class RepositoryConfigContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="repository-config-contract-")
        self.root = Path(self.temporary.name)
        for relative in FIXTURE_PATHS:
            source = REPO_ROOT / relative
            target = self.root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, target)

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def run_validator(self) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(VALIDATOR), "--root", str(self.root)],
            capture_output=True,
            text=True,
            check=False,
        )

    def assert_failure(self, expected: str) -> None:
        result = self.run_validator()
        output = result.stdout + result.stderr
        self.assertNotEqual(0, result.returncode, output)
        self.assertIn("Repository configuration contract validation failed:", output)
        self.assertIn(expected, output)

    def replace(self, relative: str, old: str, new: str) -> None:
        path = self.root / relative
        text = path.read_text(encoding="utf-8")
        self.assertIn(old, text)
        path.write_text(text.replace(old, new, 1), encoding="utf-8", newline="\n")

    def test_gwt_001_given_complete_contract_when_validated_then_it_passes(self) -> None:
        result = self.run_validator()
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_gwt_002_given_source_editor_default_drift_when_validated_then_it_fails(self) -> None:
        self.replace(".editorconfig", "end_of_line = lf", "end_of_line = crlf")
        self.assert_failure("[*] end_of_line must be lf")

    def test_gwt_003_given_missing_final_newline_when_validated_then_it_fails(self) -> None:
        path = self.root / ".editorconfig"
        path.write_bytes(path.read_bytes().rstrip(b"\r\n"))
        self.assert_failure("must end with a final newline")

    def test_gwt_004_given_central_original_rule_removed_when_validated_then_it_fails(self) -> None:
        self.replace(
            ".gitattributes",
            ".dev/assessments/**/evidence/external/original/** binary",
            "# removed",
        )
        self.assert_failure("missing centralized immutable-original rule")

    def test_gwt_005_given_arbitrary_evidence_exception_when_validated_then_it_fails(self) -> None:
        path = self.root / ".gitattributes"
        path.write_text(
            path.read_text(encoding="utf-8")
            + ".dev/assessments/ASM-20990101-001/evidence/report.md binary\n",
            encoding="utf-8",
            newline="\n",
        )
        self.assert_failure("immutable evidence rules must be")

    def test_gwt_006_given_source_path_leaks_into_downstream_seed_when_validated_then_it_fails(self) -> None:
        path = (
            self.root
            / ".ai/assets/skills/ai-context-init/templates/public-root/.gitattributes"
        )
        path.write_text(
            path.read_text(encoding="utf-8")
            + ".dev/assessments/**/evidence/external/original/** binary\n",
            encoding="utf-8",
            newline="\n",
        )
        self.assert_failure("source-only token leaked")

    def test_gwt_007_given_template_mapping_removed_when_validated_then_it_fails(self) -> None:
        self.replace(
            ".ai/assets/skills/ai-context-init/templates/public-template-manifest.yaml",
            "  - source: public-root/.editorconfig\n"
            "    target: .editorconfig\n"
            "    component_id: software-development-core\n",
            "",
        )
        self.assert_failure("public-root/.editorconfig -> .editorconfig")

    def test_gwt_008_given_source_root_config_is_packaged_directly_when_validated_then_it_fails(self) -> None:
        self.replace(
            ".ai/distribution/profiles/dotnet-backend.yaml",
            "    source:\n      - .github/pull_request_template.md",
            "    source:\n      - .editorconfig\n      - .github/pull_request_template.md",
        )
        self.assert_failure("source root .editorconfig must not be a target-template entry")

    def test_gwt_009_given_validator_is_not_source_only_when_validated_then_it_fails(self) -> None:
        self.replace(
            ".ai/distribution/profiles/dotnet-backend.yaml",
            "      - .ai/scripts/validate-repository-config-contract.py\n",
            "",
        )
        self.assert_failure("source-only CFG/SKILL validators missing")

    def test_gwt_010_given_policy_loses_ordinary_text_boundary_when_validated_then_it_fails(self) -> None:
        self.replace(
            ".dev/standards/ASSESSMENT-ARTIFACT-POLICY.md",
            "Ordinary assessment evidence is repository text",
            "Assessment evidence may be binary",
        )
        self.assert_failure("Ordinary assessment evidence is repository text")

    def test_gwt_011_given_adr_is_not_accepted_when_validated_then_it_fails(self) -> None:
        self.replace(
            ".dev/adr/ADR-001-separate-source-config-from-downstream-templates.md",
            "## Status\n\nAccepted",
            "## Status\n\nProposed",
        )
        self.assert_failure("ADR-001 must be Accepted")

    def test_gwt_012_given_tactical_evidence_attributes_when_validated_then_it_fails(self) -> None:
        path = self.root / ".dev/assessments/ASM-20990101-001/evidence/source/.gitattributes"
        path.parent.mkdir(parents=True)
        path.write_text("report.md binary\n", encoding="utf-8", newline="\n")
        self.assert_failure("per-assessment .gitattributes files are forbidden")

    def test_gwt_013_given_legacy_original_bytes_change_when_validated_then_it_fails(self) -> None:
        path = self.root / (
            ".dev/assessments/ASM-20260722-005/evidence/workservice/"
            "2026-07-22-dev-workflow-skill-comparison.md"
        )
        path.write_bytes(path.read_bytes() + b"tampered")
        self.assert_failure("SHA-256 changed")


if __name__ == "__main__":
    unittest.main()
