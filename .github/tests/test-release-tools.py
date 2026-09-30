#!/usr/bin/env python3
"""Focused transport fixtures only; no product, native or legacy test suite."""
import copy
import importlib.util
import json
from pathlib import Path
import stat
import sys
import tempfile
import unittest
from unittest.mock import patch
import zipfile

SCRIPTS = Path(__file__).absolute().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))
import release_common as common


def load(name, filename):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / filename)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


draft = load("draft_release", "draft-release.py")
builder = load("build_release", "build-release.py")
SOURCE = {"tag": "v0.19.0-rc.3", "tag_object": "a" * 40, "commit": "b" * 40}


def fixture(directory):
    engine_names = [f"src/module{i:02}.py" for i in range(24)]
    pin = {"id": "framework-managed-installation", "version": "2.0.0", "source_commit": SOURCE["commit"],
           "files": [{"path": n, "sha256": common.sha(b"engine")} for n in engine_names]}
    pin_raw = common.encoded(pin)
    payload = {"engine/" + n: (b"engine", 0o644) for n in engine_names}
    payload["engine/engine.json"] = (common.encoded({"engine": pin, "engine_package_version": 1}), 0o644)
    payload["engine-pin.json"] = (pin_raw, 0o644)
    payload["README.md"] = (b"Generic package\n", 0o644)
    catalog = {"source": {"commit": SOURCE["commit"]}, "release_version": "0.19.0-rc.3"}
    payload["catalog/metadata/catalog.json"] = (common.encoded(catalog), 0o644)
    payload["catalog/metadata/catalog-files.json"] = (common.encoded({"files": []}), 0o644)
    inputs = {n: common.sha(payload["catalog/" + n][0]) for n in ("metadata/catalog.json", "metadata/catalog-files.json")}
    identity_raw = (json.dumps(inputs, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode()
    ident = f"catalog:1:0.19.0-rc.3:{SOURCE['commit']}:{common.sha(identity_raw)}"
    payload["catalog/metadata/build.json"] = (common.encoded({"identity": ident, "identity_inputs": inputs, "artifact_kind": "catalog"}), 0o644)
    payload["content-hashes.json"] = (common.encoded([common.entry(n, b, m) for n, (b, m) in sorted(payload.items())]), 0o644)
    archive = directory / "framework.zip"
    with zipfile.ZipFile(archive, "w") as zipped:
        for name, (raw, mode) in sorted(payload.items()):
            info = zipfile.ZipInfo(name)
            info.create_system = 3
            info.external_attr = (stat.S_IFREG | mode) << 16
            zipped.writestr(info, raw)
    raw = archive.read_bytes()
    manifest = {"schema": common.SCHEMA, "source": copy.deepcopy(SOURCE), "version": "0.19.0-rc.3",
        "catalog_identity": ident, "engine_pin_sha256": common.sha(pin_raw),
        "archive": {"name": archive.name, "size": len(raw), "sha256": common.sha(raw)},
        "entries": [common.entry(n, b, m) for n, (b, m) in sorted(payload.items())],
        "provenance": {"repository": "owner/repo", "workflow": common.WORKFLOW,
            "tooling_commit": "c" * 40, "workflow_commit": "c" * 40, "run_id": "123", "run_attempt": "1"}}
    (directory / "release-manifest.json").write_bytes(common.encoded(manifest))
    (directory / "framework.zip.sha256").write_text(f"{common.sha(raw)}  framework.zip\n", encoding="utf-8", newline="\n")
    return manifest


class FakeGitHub:
    repository = "owner/repo"

    def __init__(self, manifest, raw, existing=True):
        self.source = copy.deepcopy(SOURCE)
        self.release = {"id": 1, "draft": True, "tag_name": SOURCE["tag"],
                        "body": draft.marker(manifest, raw) + "\nHuman edited notes", "name": "Human title",
                        "html_url": "https://example.invalid/draft"} if existing else None
        self.assets = {}
        self.data = {}
        self.writes = []
        self.fail_upload = False
        self.publish_before_write = False

    def pages(self, path):
        return ([copy.deepcopy(self.release)] if self.release else []) if path == "/releases" else list(self.assets.values())

    def request(self, method, path, data=None, binary=False):
        if method == "POST":
            self.writes.append((method, path, data))
            if path == "/releases":
                self.release = dict(data, id=1, html_url="https://example.invalid/draft")
                return copy.deepcopy(self.release)
            if self.fail_upload:
                raise ValueError("HTTP 502; simulated partial upload")
            name = draft.urllib.parse.parse_qs(draft.urllib.parse.urlsplit(path).query)["name"][0]
            index = len(self.assets) + 1
            asset = {"name": name, "id": index, "size": len(data), "state": "uploaded"}
            self.assets[name] = asset
            self.data[index] = data
            return asset
        if path.startswith("/git/ref/tags/"):
            return {"ref": "refs/tags/" + SOURCE["tag"], "object": {"type": "tag", "sha": self.source["tag_object"]}}
        if path.startswith("/git/tags/"):
            return {"sha": self.source["tag_object"], "tag": SOURCE["tag"],
                    "object": {"type": "commit", "sha": self.source["commit"]}}
        if path == "/releases/1":
            if self.publish_before_write:
                self.release["draft"] = False
            return copy.deepcopy(self.release)
        if path.startswith("/releases/assets/"):
            return self.data[int(path.rsplit("/", 1)[1])]
        raise AssertionError(path)


class ReleaseContracts(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.directory = Path(self.temp.name)
        self.manifest = fixture(self.directory)
        self.raw = (self.directory / "release-manifest.json").read_bytes()

    def tearDown(self):
        self.temp.cleanup()

    def api(self, existing=True):
        return FakeGitHub(self.manifest, self.raw, existing)

    def deliver(self, api):
        receipt = {}
        draft.deliver(api, self.directory, self.manifest, receipt)
        return receipt

    def test_actual_zip_raw_inventory(self):
        self.assertEqual(common.verify_bundle(self.directory, SOURCE), self.manifest)

    def test_source_manifest_mismatch(self):
        with self.assertRaisesRegex(ValueError, "source/manifest"):
            common.verify_bundle(self.directory, dict(SOURCE, commit="d" * 40))

    def test_corrupted_archive(self):
        with (self.directory / "framework.zip").open("ab") as stream:
            stream.write(b"corruption")
        with self.assertRaisesRegex(ValueError, "size/hash"):
            common.verify_bundle(self.directory)

    def test_corrupted_catalog_identity(self):
        self.manifest["catalog_identity"] = "wrong"
        (self.directory / "release-manifest.json").write_bytes(common.encoded(self.manifest))
        with self.assertRaisesRegex(ValueError, "catalog identity"):
            common.verify_bundle(self.directory)

    def test_safe_archive_paths(self):
        for path in ("../escape", "/absolute", "engine\\escape", "a//b", "a/CON", "a/."):
            with self.subTest(path=path), self.assertRaises(ValueError):
                common.safe_name(path)

    def test_annotated_tag_exact_identity(self):
        outputs = [b"tag\n", (SOURCE["tag_object"] + "\n").encode(),
                   f"object {SOURCE['commit']}\ntype commit\ntag {SOURCE['tag']}\n\nannotation".encode()]
        with patch.object(common, "git", side_effect=outputs):
            self.assertEqual(common.identity(self.directory, tag=SOURCE["tag"]), SOURCE)

    def test_lightweight_tag_refused(self):
        with patch.object(common, "git", return_value=b"commit\n"), self.assertRaisesRegex(ValueError, "annotated"):
            common.identity(self.directory, tag=SOURCE["tag"])

    def test_tag_source_mismatch(self):
        outputs = [b"tag\n", (SOURCE["tag_object"] + "\n").encode(),
                   f"object {SOURCE['commit']}\ntype commit\ntag {SOURCE['tag']}\n\nannotation".encode()]
        with patch.object(common, "git", side_effect=outputs), self.assertRaisesRegex(ValueError, "source/tag"):
            common.identity(self.directory, source_commit="d" * 40, tag=SOURCE["tag"])

    def test_engine_declarations_must_agree(self):
        first = repr(tuple(f"src/a{i:02}.py" for i in range(24))).encode()
        second = repr(tuple(f"src/b{i:02}.py" for i in range(24))).encode()
        with patch.object(builder, "git", side_effect=[b"ENGINE_FILES = " + first, b"ENGINE_FILES = " + second]):
            with self.assertRaisesRegex(ValueError, "declarations disagree"):
                builder.engine_pin(self.directory, SOURCE["commit"])

    def test_published_release_refused_without_writes(self):
        api = self.api()
        api.release["draft"] = False
        with self.assertRaisesRegex(ValueError, "published"):
            self.deliver(api)
        self.assertFalse(api.writes)

    def test_create_is_draft_without_tag_creation_target(self):
        api = self.api(existing=False)
        result = self.deliver(api)
        create = api.writes[0][2]
        self.assertTrue(create["draft"])
        self.assertNotIn("target_commitish", create)
        self.assertEqual(result["outcome"], "draft-ready")
        self.assertEqual(len(result["assets"]), 3)

    def test_notes_title_preserved_and_idempotent_exact_bytes(self):
        api = self.api()
        initial = copy.deepcopy(api.release)
        self.deliver(api)
        api.writes.clear()
        result = self.deliver(api)
        self.assertEqual(api.release, initial)
        self.assertFalse(api.writes)
        self.assertTrue(result["existing_body_preserved"])

    def test_foreign_draft_refused(self):
        api = self.api()
        api.release["body"] = "unowned"
        with self.assertRaisesRegex(ValueError, "ownership"):
            self.deliver(api)
        self.assertFalse(api.writes)

    def test_mismatching_asset_refused_before_write(self):
        api = self.api()
        api.assets["framework.zip"] = {"id": 1, "name": "framework.zip", "state": "uploaded",
                                       "size": (self.directory / "framework.zip").stat().st_size}
        api.data[1] = b"different bytes"
        with self.assertRaisesRegex(ValueError, "mismatching"):
            self.deliver(api)
        self.assertFalse(api.writes)

    def test_starter_asset_refused(self):
        api = self.api()
        api.assets["framework.zip"] = {"id": 1, "name": "framework.zip", "state": "starter", "size": 0}
        with self.assertRaisesRegex(ValueError, "partial"):
            self.deliver(api)
        self.assertFalse(api.writes)

    def test_tag_drift_refused_without_writes(self):
        api = self.api()
        api.source["commit"] = "d" * 40
        with self.assertRaisesRegex(ValueError, "tag/source drift"):
            self.deliver(api)
        self.assertFalse(api.writes)

    def test_human_publication_race_stops_remaining_writes(self):
        api = self.api()
        api.publish_before_write = True
        with self.assertRaisesRegex(ValueError, "published"):
            self.deliver(api)
        self.assertFalse(api.writes)

    def test_partial_failure_retains_release_identity(self):
        api = self.api(existing=False)
        api.fail_upload = True
        receipt = {}
        with self.assertRaisesRegex(ValueError, "502"):
            draft.deliver(api, self.directory, self.manifest, receipt)
        self.assertEqual(receipt["release_id"], 1)
        self.assertTrue(api.release["draft"])

    def test_publication_during_final_downloads_refuses_ready(self):
        api = self.api(existing=False)
        original = api.request

        def request(method, path, data=None, binary=False):
            value = original(method, path, data, binary)
            if binary:
                api.release["draft"] = False
            return value

        with patch.object(api, "request", side_effect=request), self.assertRaisesRegex(ValueError, "published"):
            self.deliver(api)

    def test_tag_drift_during_final_downloads_refuses_ready(self):
        api = self.api(existing=False)
        original = api.request

        def request(method, path, data=None, binary=False):
            value = original(method, path, data, binary)
            if binary:
                api.source["tag_object"] = "d" * 40
            return value

        with patch.object(api, "request", side_effect=request), self.assertRaisesRegex(ValueError, "tag object drift"):
            self.deliver(api)

    def test_create_timeout_retains_pre_post_unknown_intent(self):
        api = self.api(existing=False)
        receipt, saved = {}, []
        original = api.request

        def request(method, path, data=None, binary=False):
            if method == "POST":
                self.assertEqual(saved[-1]["attempted_operations"][-1]["outcome"], "unknown")
                raise TimeoutError("create response lost")
            return original(method, path, data, binary)

        with patch.object(api, "request", side_effect=request), self.assertRaises(TimeoutError):
            draft.deliver(api, self.directory, self.manifest, receipt,
                          lambda: saved.append(copy.deepcopy(receipt)))
        row = receipt["attempted_operations"][0]
        self.assertEqual((row["operation"], row["outcome"]), ("create-draft", "unknown"))
        self.assertNotIn("provider_id", row)

    def test_upload_failure_journals_asset_intent_before_post(self):
        api = self.api()
        api.fail_upload = True
        receipt, saved = {}, []
        with self.assertRaisesRegex(ValueError, "502"):
            draft.deliver(api, self.directory, self.manifest, receipt,
                          lambda: saved.append(copy.deepcopy(receipt)))
        row = saved[-1]["attempted_operations"][-1]
        self.assertEqual((row["operation"], row["asset_name"], row["outcome"]),
                         ("upload-asset", "release-manifest.json", "unknown"))
        self.assertEqual(row["sha256"], common.sha(self.raw))

    def test_malformed_successful_create_keeps_unknown_outcome(self):
        api = self.api(existing=False)
        original = api.request
        receipt = {}

        def request(method, path, data=None, binary=False):
            value = original(method, path, data, binary)
            return {} if method == "POST" else value

        with patch.object(api, "request", side_effect=request), self.assertRaisesRegex(ValueError, "acknowledgement"):
            draft.deliver(api, self.directory, self.manifest, receipt)
        self.assertTrue(api.release["draft"])
        self.assertEqual(receipt["attempted_operations"][0]["outcome"], "unknown")

    def test_malformed_upload_ack_keeps_unknown_asset_outcome(self):
        api = self.api()
        original = api.request
        receipt = {}

        def request(method, path, data=None, binary=False):
            value = original(method, path, data, binary)
            return dict(value, name="wrong") if method == "POST" else value

        with patch.object(api, "request", side_effect=request), self.assertRaisesRegex(ValueError, "acknowledgement"):
            draft.deliver(api, self.directory, self.manifest, receipt)
        self.assertEqual(receipt["attempted_operations"][0]["outcome"], "unknown")

    def test_success_records_acknowledged_provider_ids(self):
        receipt = self.deliver(self.api(existing=False))
        self.assertEqual(len(receipt["attempted_operations"]), 4)
        self.assertTrue(all(row["outcome"] == "acknowledged" and type(row["provider_id"]) is int
                            for row in receipt["attempted_operations"]))

    def test_paginated_draft_discovery(self):
        api = draft.GitHub("owner/repo", "fixture-not-a-real-token")
        rows = [{"id": i} for i in range(100)]
        with patch.object(api, "request", side_effect=[rows, [{"id": 999}]]) as request:
            self.assertEqual(len(api.pages("/releases")), 101)
            self.assertIn("page=2", request.call_args_list[1].args[1])


if __name__ == "__main__":
    unittest.main()
