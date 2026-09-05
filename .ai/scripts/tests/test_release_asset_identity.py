"""REL-018 synthetic failure fixtures; not evidence of actual publication."""
from __future__ import annotations

import copy
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from release_asset_identity import (
    PackageError, SCHEMA, asset_names, canonical_json_bytes, check_admission, contained,
    governed, sha256_bytes, stage, strict_json, verify_provider, verify_route_binding,
    verify_transported, verify_source, selected_input_document, load_admission, PROFILE,
)


def fixture():
    version = "v0.16.0"
    assets = [{"name": name, "path": "admitted/" + name, "size": len(name),
               "sha256": sha256_bytes(name.encode())} for name in asset_names(version)]
    admission = {"schema_version": SCHEMA, "state": "admitted-candidate", "version": version,
                 "package_id": "ai-collaboration-framework-v0.16.0", "release_id": "REL-v0.16.0",
                 "build_commit": "1" * 40, "payload_fingerprint": "2" * 64,
                 "selected_input_fingerprint": "3" * 64, "assets": assets}
    admission["artifact_set_id"] = "sha256:" + sha256_bytes(canonical_json_bytes([
        {key: item[key] for key in ("name", "size", "sha256")} for item in assets]))
    repository = "owner/framework"
    provider = {"id": 42, "tag_name": version, "draft": False, "prerelease": False,
                "published_at": "2026-09-05T00:00:00Z",
                "html_url": f"https://github.com/{repository}/releases/tag/{version}",
                "assets": [{"id": n + 10, "state": "uploaded", "name": a["name"],
                            "size": a["size"], "digest": "sha256:" + a["sha256"],
                            "browser_download_url": f"https://github.com/{repository}/releases/download/{version}/{a['name']}"}
                           for n, a in enumerate(assets)]}
    return admission, provider, repository


class ReleaseAssetIdentityTests(unittest.TestCase):
    def test_v016_mismatched_upload_and_provider_digest_fails(self):
        admission, provider, repository = fixture()
        provider["assets"][0]["digest"] = "sha256:" + "f" * 64
        with self.assertRaisesRegex(PackageError, "disagrees"):
            verify_provider(admission, provider, repository)

    def test_missing_digest_wrong_size_name_url_state_and_id_fail_closed(self):
        for key, value in (("digest", None), ("size", 1), ("name", "other.zip"),
                           ("browser_download_url", "https://example.invalid/a"),
                           ("state", "new"), ("id", True)):
            with self.subTest(key=key):
                admission, provider, repository = fixture()
                provider["assets"][0][key] = value
                with self.assertRaises(PackageError):
                    verify_provider(admission, provider, repository)

    def test_provider_duplicate_asset_id_or_name_fails(self):
        for key in ("id", "name"):
            admission, provider, repository = fixture()
            provider["assets"][1][key] = provider["assets"][0][key]
            with self.assertRaises(PackageError):
                verify_provider(admission, provider, repository)

    def test_draft_requires_explicit_permission_and_never_becomes_published(self):
        admission, provider, repository = fixture()
        provider.update(draft=True, published_at=None)
        with self.assertRaises(PackageError):
            verify_provider(admission, provider, repository)
        receipt = verify_provider(admission, provider, repository, allow_draft=True)
        self.assertEqual("uploaded-draft", receipt["state"])
        provider["html_url"] = f"https://github.com/{repository}/releases/tag/untagged-abc123"
        self.assertEqual("uploaded-draft", verify_provider(admission, provider, repository, allow_draft=True)["state"])
        provider.update(draft=False, published_at="2026-09-05T00:00:00Z")
        with self.assertRaises(PackageError):
            verify_provider(admission, provider, repository)
        provider["html_url"] = f"https://github.com/{repository}/releases/tag/v0.16.0"
        published = verify_provider(admission, provider, repository)
        self.assertEqual("published", published["state"])
        self.assertEqual(receipt["artifact_set_id"], published["artifact_set_id"])
        self.assertEqual("admitted-candidate", admission["state"])

    def test_publication_without_timestamp_or_wrong_tag_fails(self):
        for key, value in (("published_at", None), ("tag_name", "v0.15.1"), ("draft", None)):
            admission, provider, repository = fixture()
            provider[key] = value
            with self.assertRaises(PackageError):
                verify_provider(admission, provider, repository)

    def test_artifact_set_detects_same_logical_identity_with_changed_archive(self):
        admission, _, _ = fixture()
        admission["assets"][0]["sha256"] = "f" * 64
        with self.assertRaisesRegex(PackageError, "artifact set"):
            check_admission(admission, admission["version"])

    def test_stage_copies_exact_bytes_and_rejects_overwrite_or_later_drift(self):
        admission, _, _ = fixture()
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "admitted").mkdir()
            for asset in admission["assets"]:
                (root / asset["path"]).write_bytes(asset["name"].encode())
            output = root / "transport"
            stage(root, admission, output)
            verify_transported(root, admission, output)
            with self.assertRaisesRegex(PackageError, "overwrite"):
                stage(root, admission, output)
            (output / admission["assets"][0]["name"]).write_bytes(b"changed")
            with self.assertRaisesRegex(PackageError, "transported"):
                verify_transported(root, admission, output)

    def test_route_identity_requires_same_payload_and_exact_admitted_archive(self):
        admission, _, _ = fixture()
        identity = {k: admission[k] for k in ("package_id", "release_id", "payload_fingerprint")}
        edge = {"to_version": "v0.16.0", "package_identity": identity,
                "artifacts": {"archive": {"sha256": admission["assets"][0]["sha256"]}}}
        matrix = {"target": {"package_identity": identity},
                  "routes": [{"target": "v0.16.0", "edges": [edge]}]}
        verify_route_binding(matrix, admission)
        for key in ("package_identity", "artifacts"):
            changed = copy.deepcopy(matrix)
            changed["routes"][0]["edges"][0][key] = {}
            with self.assertRaises(PackageError):
                verify_route_binding(changed, admission)

    def test_missing_route_fails(self):
        admission, _, _ = fixture()
        with self.assertRaises(PackageError):
            verify_route_binding({}, admission)

    def test_unsafe_path_and_duplicate_json_fail(self):
        with tempfile.TemporaryDirectory() as temporary:
            for path in ("../outside", "a/../b", "/root", "C:/root", "a\\b"):
                with self.assertRaises(PackageError):
                    contained(Path(temporary), path)
        with self.assertRaises(PackageError):
            strict_json(b'{"state":1,"state":2}')

    def test_version_boundary_keeps_historical_records_readable(self):
        self.assertFalse(governed("v0.15.1"))
        self.assertTrue(governed("v0.16.0"))
        self.assertTrue(governed("v1.0.0"))
        with self.assertRaises(PackageError):
            governed("v0.16.0/../a")

    def test_history_only_rebind_passes_but_changed_or_omitted_selected_input_fails(self):
        admission, _, _ = fixture()
        paths = {PROFILE, ".dev/releases/v0.16.0/release.yaml", ".ai/distribution/templates/INSTALL.md",
                 ".ai/distribution/templates/requirements.txt", ".ai/distribution/identity-registry.yaml"}
        source = {path: path.encode() for path in paths}
        selected = selected_input_document(source, [], [])
        admission["selected_input_fingerprint"] = sha256_bytes(canonical_json_bytes(selected))
        snapshot = SimpleNamespace(tree={path: path for path in paths}, blob_reader=None, commit="b" * 40)
        with patch("release_asset_identity.PackageRepositorySnapshot.from_ref", return_value=snapshot), \
             patch("release_asset_identity.load_yaml_blob", return_value={"package": {"identity_registry": ".ai/distribution/identity-registry.yaml"}}), \
             patch("release_asset_identity.collect_payload", return_value=[]), \
             patch("release_asset_identity.git_blob", side_effect=lambda root, entry, reader: source[entry]):
            verify_source(Path("."), "v0.16.0", "b" * 40, admission, selected)
            omitted = copy.deepcopy(selected)
            omitted["source_inputs"].pop()
            with self.assertRaisesRegex(PackageError, "selected inputs"):
                verify_source(Path("."), "v0.16.0", "b" * 40, admission, omitted)
            source[PROFILE] += b"changed"
            with self.assertRaisesRegex(PackageError, "selected inputs"):
                verify_source(Path("."), "v0.16.0", "b" * 40, admission, selected)

    def test_candidate_without_tracked_admission_fails(self):
        with patch("release_asset_identity.PackageRepositorySnapshot.from_ref", return_value=SimpleNamespace(tree={})):
            with self.assertRaisesRegex(PackageError, "admission is missing"):
                load_admission(Path("."), "v0.16.0")


if __name__ == "__main__":
    unittest.main()
