"""REL-018 synthetic failure fixtures; not evidence of actual publication."""
from __future__ import annotations

import copy
import importlib.util
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
from contextlib import redirect_stderr, redirect_stdout
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from release_asset_identity import (
    PackageError, SCHEMA, asset_names, canonical_json_bytes, check_admission, contained,
    governed, sha256_bytes, stage, strict_json, verify_provider, verify_route_binding,
    verify_transported, verify_source, selected_input_document, load_admission, PROFILE, validate_archive,
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
    def test_realistic_draft_downloads_bind_to_the_owned_page_then_public_tag(self):
        admission, provider, repository = fixture()
        provider.update(draft=True, published_at=None,
                        html_url=f"https://github.com/{repository}/releases/tag/untagged-167422cded865a8923c2")
        for asset in provider["assets"]:
            asset["browser_download_url"] = f"https://github.com/{repository}/releases/download/untagged-167422cded865a8923c2/{asset['name']}"
        with self.assertRaises(PackageError):
            verify_provider(admission, provider, repository)
        draft = verify_provider(admission, provider, repository, allow_draft=True)
        self.assertEqual("uploaded-draft", draft["state"])
        self.assertIsNone(draft["published_at"])
        provider.update(draft=False, published_at="2026-09-05T00:00:00Z",
                        html_url=f"https://github.com/{repository}/releases/tag/v0.16.0")
        with self.assertRaisesRegex(PackageError, "browser_download_url"):
            verify_provider(admission, provider, repository, allow_draft=True)
        for asset in provider["assets"]:
            asset["browser_download_url"] = f"https://github.com/{repository}/releases/download/v0.16.0/{asset['name']}"
        published = verify_provider(admission, provider, repository)
        self.assertEqual("published", published["state"])
        self.assertEqual(draft["artifact_set_id"], published["artifact_set_id"])
        self.assertEqual([a["id"] for a in draft["assets"]], [a["id"] for a in published["assets"]])

    def test_draft_url_exception_rejects_other_tokens_hosts_repositories_and_malformed_values(self):
        admission, provider, repository = fixture()
        provider.update(draft=True, published_at=None,
                        html_url=f"https://github.com/{repository}/releases/tag/untagged-abc123")
        valid = f"https://github.com/{repository}/releases/download/untagged-abc123/{provider['assets'][0]['name']}"
        invalid = [valid.replace("abc123", "def456"), valid.replace("github.com", "example.invalid"),
                   valid.replace(repository, "other/framework"), valid + "?download=1", valid + "/suffix",
                   valid.replace("untagged-abc123", "v0.15.1"), valid.replace("untagged-abc123", "%75ntagged-abc123"),
                   valid.replace("untagged-abc123", "untagged-abc123/.."), None, [valid]]
        for value in invalid:
            with self.subTest(value=value):
                provider["assets"][0]["browser_download_url"] = value
                with self.assertRaisesRegex(PackageError, "browser_download_url"):
                    verify_provider(admission, provider, repository, allow_draft=True)
        provider["assets"][0]["browser_download_url"] = valid
        provider["html_url"] = f"https://github.com/{repository}/releases/tag/v0.16.0"
        with self.assertRaisesRegex(PackageError, "browser_download_url"):
            verify_provider(admission, provider, repository, allow_draft=True)

    def test_valid_draft_url_does_not_weaken_asset_identity_checks(self):
        for field, value in (("id", True), ("size", 1), ("state", "new"), ("digest", "sha256:" + "0" * 64)):
            with self.subTest(field=field):
                admission, provider, repository = fixture()
                provider.update(draft=True, published_at=None,
                                html_url=f"https://github.com/{repository}/releases/tag/untagged-abc123")
                for asset in provider["assets"]:
                    asset["browser_download_url"] = f"https://github.com/{repository}/releases/download/untagged-abc123/{asset['name']}"
                provider["assets"][0][field] = value
                with self.assertRaisesRegex(PackageError, field):
                    verify_provider(admission, provider, repository, allow_draft=True)

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
        source[".dev/releases/v0.16.0/release.yaml"] = yaml.safe_dump({
            "schema_version": "1.0", "version": "v0.16.0", "release_id": "REL-v0.16.0",
            "compatibility": {}, "distribution": {}, "status": "planned",
        }).encode()
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

    def test_retained_backfill_binds_provider_archive_payload_and_route_bytes(self):
        base = Path(__file__).resolve().parents[3] / ".dev/workflows/2026-09-05-published-asset-identity/evidence/published-routes"
        catalog = json.loads((base / "asset-lifecycle.json").read_bytes())
        matrix = yaml.safe_load((base / "support-matrix.yaml").read_bytes())
        for entry in catalog["assets"]:
            published = entry["published"]
            raw = (base / published["provider_readback"]["path"]).read_bytes()
            self.assertEqual(published["provider_readback"]["sha256"], sha256_bytes(raw))
            provider = json.loads(raw)
            self.assertFalse(provider["draft"])
            self.assertEqual(entry["version"], provider["tag_name"])
            archive = base / published["path"]
            digest = sha256_bytes(archive.read_bytes())
            self.assertEqual("sha256:" + digest, published["archive_id"])
            self.assertNotEqual(entry["candidate"]["archive_id"], published["archive_id"])
            asset = next(a for a in provider["assets"] if a["id"] == published["provider_asset_id"])
            self.assertEqual("sha256:" + digest, asset["digest"])
            self.assertEqual(archive.stat().st_size, asset["size"])
            self.assertEqual(archive.name, asset["name"])
            members = validate_archive(archive)
            metadata = yaml.safe_load(members[entry["package_id"] + "/metadata/package.yaml"][0])
            self.assertEqual(entry["payload_fingerprint"], metadata["identity"]["payload_fingerprint"])
            self.assertEqual(published["build_commit"], metadata["source"]["commit"])
            edges = [edge for route in matrix["routes"] for edge in route["edges"] if edge["to_version"] == entry["version"]]
            self.assertTrue(edges)
            for edge in edges:
                self.assertEqual(digest, edge["artifacts"]["archive"]["sha256"])


class ProviderEvidenceCliTests(unittest.TestCase):
    """Synthetic CLI responses test evidence retention, never actual publication."""

    def setUp(self):
        path = Path(__file__).resolve().parents[1] / "manage-release-asset-identity.py"
        spec = importlib.util.spec_from_file_location("release_asset_cli_under_test", path)
        self.cli = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.cli)

    def invoke(self, admission, provider, repository, directory, extra=None):
        raw = (json.dumps(provider, indent=2) + "\n").encode()
        responses = [SimpleNamespace(stdout=json.dumps({"databaseId": provider["id"], "tagName": admission["version"]}).encode()),
                     SimpleNamespace(stdout=raw)]
        argv = ["manage-release-asset-identity.py", "provider", "--version", admission["version"],
                "--repository", repository, "--assets-dir", str(directory),
                "--output", str(directory / "receipt.json"), "--raw-provider-output", str(directory / "provider.json")]
        with patch.object(sys, "argv", argv + (extra or [])), \
             patch.object(self.cli, "load_admission", return_value=admission), \
             patch.object(self.cli, "verify_transported"), \
             patch.object(self.cli.subprocess, "run", side_effect=responses) as provider_call, \
             redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()) as errors:
            result = self.cli.main()
        return result, raw, errors.getvalue(), provider_call.call_count

    def test_rejected_provider_retains_exact_response_without_success_receipt(self):
        admission, provider, repository = fixture()
        provider["assets"][0]["digest"] = "sha256:" + "f" * 64
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            result, raw, error, calls = self.invoke(admission, provider, repository, directory)
            self.assertEqual(1, result)
            self.assertEqual(2, calls)
            self.assertIn("digest", error)
            self.assertEqual(raw, (directory / "provider.json").read_bytes())
            self.assertFalse((directory / "receipt.json").exists())

    def test_success_receipt_binds_the_preserved_response(self):
        admission, provider, repository = fixture()
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            result, raw, _, _ = self.invoke(admission, provider, repository, directory)
            self.assertEqual(0, result)
            self.assertEqual(raw, (directory / "provider.json").read_bytes())
            receipt = json.loads((directory / "receipt.json").read_bytes())
            self.assertEqual(sha256_bytes(raw), receipt["raw_provider_sha256"])

    def test_existing_raw_evidence_fails_before_provider_access_and_is_not_overwritten(self):
        admission, provider, repository = fixture()
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            (directory / "provider.json").write_bytes(b"prior-failure")
            result, _, error, calls = self.invoke(admission, provider, repository, directory)
            self.assertEqual(1, result)
            self.assertEqual(0, calls)
            self.assertIn("refusing to overwrite", error)
            self.assertEqual(b"prior-failure", (directory / "provider.json").read_bytes())


if __name__ == "__main__":
    unittest.main()
