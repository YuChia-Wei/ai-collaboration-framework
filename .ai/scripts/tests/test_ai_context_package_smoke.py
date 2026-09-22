#!/usr/bin/env python3
"""Fast package smoke coverage kept separate from the release migration matrix."""

from __future__ import annotations

import unittest
import yaml

from test_ai_context_packaging import PACKAGE, ROOT, SyntheticPackageRepo, git


class AiContextPackageSmokeGwtTests(unittest.TestCase):
    def test_gwt_001_given_one_candidate_when_smoke_runs_then_archives_and_metadata_are_valid(self) -> None:
        fixture = SyntheticPackageRepo()
        try:
            # Scope routing-catalog inclusion to this smoke fixture. Other
            # synthetic package identities do not depend on the full registry.
            relative = ".ai/assets/shared/artifact-lifecycle-registry.json"
            path = fixture.root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes((ROOT / relative).read_bytes())
            profile_path = fixture.root / fixture.profile
            profile = yaml.safe_load(profile_path.read_text(encoding="utf-8"))
            profile["entries"].append({"id":"lifecycle-routing", "component_id":"software-development-core",
                "source":relative, "target":"preserve-relative-path", "ownership":"framework-managed", "install_behavior":"managed"})
            profile_path.write_text(yaml.safe_dump(profile,sort_keys=False),encoding="utf-8",newline="\n")
            git(fixture.root,"add","."); git(fixture.root,"commit","-qm","smoke routing inventory")
            result = fixture.build("smoke")

            # One build is sufficient for PR smoke: validate both archive
            # formats, their embedded checksums, and package metadata.
            zip_members = PACKAGE.validate_archive(result["zip"])
            tar_members = PACKAGE.validate_archive(result["tar_gz"])
            self.assertEqual(zip_members, tar_members)
            self.assertIn(f"{result['package_id']}/metadata/package.yaml", zip_members)
            self.assertIn(f"{result['package_id']}/metadata/migration.yaml", zip_members)
            for helper in ('execution_artifact_contract.py', 'artifact_authoring.py', 'artifact_core.py',
                           'validate-ai-context.py', 'ai_context_cli_routing.py', 'artifact_lifecycle.py'):
                self.assertIn(f"{result['package_id']}/payload/.ai/scripts/{helper}", zip_members)
            self.assertIn(f"{result['package_id']}/payload/.ai/assets/shared/artifact-lifecycle-registry.json", zip_members)
        finally:
            fixture.close()


if __name__ == "__main__":
    unittest.main()
