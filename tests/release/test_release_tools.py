#!/usr/bin/env python3
"""Offline release transport fixtures using synthetic bundles and provider replies."""
import copy
import importlib.util
import hashlib
import json
from pathlib import Path
import stat
import sys
import tempfile
import unittest
from unittest.mock import patch
import zipfile

SCRIPTS = Path(__file__).absolute().parents[2] / ".github/scripts"
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
README_TEMPLATE = "# ${label}\nSource: ${source_commit}\nCatalog: ${catalog_identity}\nVersion: ${release_version}\n"


def readme_source(template=README_TEMPLATE):
    raw = template.encode("utf-8")
    return {"path": common.README_SOURCE_PATH, "commit": SOURCE["commit"],
            "git_blob": hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest(),
            "sha256": common.sha(raw), "size": len(raw), "template_utf8": template}


def fixture(directory, *, schema=common.SCHEMA, readme_override=None, catalog_source=None):
    engine_names = [f"src/module{i:02}.py" for i in range(23)]
    pin = {"id": "framework-managed-installation", "version": "2.0.0", "source_commit": SOURCE["commit"],
           "files": [{"path": n, "sha256": common.sha(b"engine")} for n in engine_names]}
    pin_raw = common.encoded(pin)
    payload = {"engine/" + n: (b"engine", 0o644) for n in engine_names}
    payload["engine/engine.json"] = (common.encoded({"engine": pin, "engine_package_version": 1}), 0o644)
    payload["engine-pin.json"] = (pin_raw, 0o644)
    catalog = {"source": {"commit": SOURCE["commit"]}, "release_version": "0.19.0-rc.3"}
    payload["catalog/metadata/catalog.json"] = (common.encoded(catalog), 0o644)
    catalog_files = []
    if catalog_source is not None:
        name, raw = "packages/skill/reviewer/README.md", b"Selected resource\n"
        payload["catalog/" + name] = (raw, 0o644)
        catalog_files.append({"path": name, "source": {"path": catalog_source, "size": len(raw), "sha256": common.sha(raw)}})
    payload["catalog/metadata/catalog-files.json"] = (common.encoded({"files": catalog_files}), 0o644)
    inputs = {n: common.sha(payload["catalog/" + n][0]) for n in ("metadata/catalog.json", "metadata/catalog-files.json")}
    identity_raw = (json.dumps(inputs, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode()
    ident = f"catalog:1:0.19.0-rc.3:{SOURCE['commit']}:{common.sha(identity_raw)}"
    payload["catalog/metadata/build.json"] = (common.encoded({"identity": ident, "identity_inputs": inputs, "artifact_kind": "catalog"}), 0o644)
    readme = (common.render_readme(README_TEMPLATE, SOURCE, ident, "0.19.0-rc.3")
              if schema == common.SCHEMA else b"Generic legacy package\n")
    payload["README.md"] = (readme if readme_override is None else readme_override, 0o644)
    payload["content-hashes.json"] = (common.encoded([common.entry(n, b, m) for n, (b, m) in sorted(payload.items())]), 0o644)
    archive = directory / "framework.zip"
    with zipfile.ZipFile(archive, "w") as zipped:
        for name, (raw, mode) in sorted(payload.items()):
            info = zipfile.ZipInfo(name)
            info.create_system = 3
            info.external_attr = (stat.S_IFREG | mode) << 16
            zipped.writestr(info, raw)
    raw = archive.read_bytes()
    manifest = {"schema": schema, "source": copy.deepcopy(SOURCE), "version": "0.19.0-rc.3",
        "catalog_identity": ident, "engine_pin_sha256": common.sha(pin_raw),
        "archive": {"name": archive.name, "size": len(raw), "sha256": common.sha(raw)},
        "entries": [common.entry(n, b, m) for n, (b, m) in sorted(payload.items())],
        "provenance": {"repository": "owner/repo", "workflow": common.WORKFLOW,
            "tooling_commit": "c" * 40, "workflow_commit": "c" * 40, "run_id": "123", "run_attempt": "1"}}
    if schema == common.SCHEMA:
        manifest["provenance"]["readme_source"] = readme_source()
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
        offline = patch.object(draft.urllib.request.OpenerDirector, "open",
                               side_effect=AssertionError("release-tool tests must stay offline"))
        offline.start()
        self.addCleanup(offline.stop)
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
        first = repr(tuple(f"src/a{i:02}.py" for i in range(23))).encode()
        second = repr(tuple(f"src/b{i:02}.py" for i in range(23))).encode()
        with patch.object(builder, "git", side_effect=[b"ENGINE_FILES = " + first, b"ENGINE_FILES = " + second]):
            with self.assertRaisesRegex(ValueError, "declarations disagree"):
                builder.engine_pin(self.directory, SOURCE["commit"])

    def test_engine_rejects_root_build_tools_before_reading_payload(self):
        members=tuple(sorted([f"src/a{i:02}.py" for i in range(22)]+['tools/build-catalog.py']))
        with patch.object(builder, 'git', return_value=('ENGINE_FILES = '+repr(members)).encode()) as git_read:
            with self.assertRaisesRegex(ValueError, 'product-only'):
                builder.engine_pin(self.directory,SOURCE['commit'])
            self.assertEqual(git_read.call_count,1)

    def test_current_engine_has_relocated_consumer_entries_and_no_build_cli(self):
        import ast
        root=SCRIPTS.parents[1]
        declarations=[]
        for name in ('src/tools/maintain_framework.py','src/distribution/installation_state.py'):
            tree=ast.parse((root/name).read_text(encoding='utf-8'))
            node=next(n for n in tree.body if isinstance(n,ast.Assign)
                      and any(isinstance(t,ast.Name) and t.id=='ENGINE_FILES' for t in n.targets))
            declarations.append(ast.literal_eval(node.value))
        self.assertEqual(declarations[0],declarations[1])
        self.assertTrue(all(n.startswith('src/') and not Path(n).name.startswith('build-') for n in declarations[0]))
        self.assertTrue({'src/tools/derive-subset.py','src/tools/reinstall-framework.py',
                         'src/tools/maintain_framework.py'}<=set(declarations[0]))

    def test_v2_requires_readme_source_and_rejects_unknown_envelope(self):
        for defect in ('missing', 'schema'):
            manifest = copy.deepcopy(self.manifest)
            if defect == 'missing':
                manifest['provenance'].pop('readme_source')
            else:
                manifest['schema'] = 'framework-release-assets/3'
            (self.directory / 'release-manifest.json').write_bytes(common.encoded(manifest))
            with self.subTest(defect=defect), self.assertRaises(ValueError):
                common.verify_bundle(self.directory)

    def test_readme_source_identity_and_raw_bytes_are_verified(self):
        defects = {'path': 'tools/release-readme.md', 'commit': 'd' * 40,
                   'git_blob': 'e' * 40, 'sha256': 'f' * 64,
                   'size': True, 'template_utf8': README_TEMPLATE + 'changed'}
        for field, value in defects.items():
            manifest = copy.deepcopy(self.manifest)
            manifest['provenance']['readme_source'][field] = value
            (self.directory / 'release-manifest.json').write_bytes(common.encoded(manifest))
            with self.subTest(field=field), self.assertRaisesRegex(ValueError, 'README source'):
                common.verify_bundle(self.directory)
        manifest = copy.deepcopy(self.manifest)
        manifest['provenance']['readme_source']['extra'] = 'not allowed'
        (self.directory / 'release-manifest.json').write_bytes(common.encoded(manifest))
        with self.assertRaisesRegex(ValueError, 'README source fields'):
            common.verify_bundle(self.directory)

    def test_self_consistent_archive_cannot_replace_rendered_readme(self):
        fixture(self.directory, readme_override=b'Changed README with matching ZIP and content hashes.\n')
        with self.assertRaisesRegex(ValueError, 'README rendered bytes'):
            common.verify_bundle(self.directory)

    def test_template_renderer_rejects_unknown_missing_and_invalid_fields(self):
        for template in (README_TEMPLATE.replace('${label}', '${unknown}'),
                         README_TEMPLATE.replace('${label}', 'missing'),
                         README_TEMPLATE + '$', README_TEMPLATE + '${source_commit.__class__}'):
            with self.subTest(template=template), self.assertRaisesRegex(ValueError, 'README template'):
                common.render_readme(template, SOURCE, 'catalog-id', '0.19.0-rc.3')
        snapshot = dict(SOURCE, tag=None, tag_object=None)
        rendered = common.render_readme(README_TEMPLATE, snapshot, 'catalog-id', '0.19.0-rc.3')
        self.assertEqual(rendered, ('# snapshot\nSource: ' + SOURCE['commit'] +
                                  '\nCatalog: catalog-id\nVersion: 0.19.0-rc.3\n').encode())

    def test_template_is_read_from_selected_commit_not_tooling_checkout(self):
        record = readme_source()
        listing = ('100644 blob ' + record['git_blob'] + '\t' + common.README_SOURCE_PATH + '\n').encode()
        with patch.object(builder, 'git', side_effect=[listing, README_TEMPLATE.encode()]) as git_read:
            self.assertEqual(builder.load_readme_source(self.directory, SOURCE['commit']), record)
        self.assertEqual(git_read.call_args_list, [
            unittest.mock.call(self.directory, 'ls-tree', SOURCE['commit'], '--', common.README_SOURCE_PATH),
            unittest.mock.call(self.directory, 'show', SOURCE['commit'] + ':' + common.README_SOURCE_PATH)])
        self.assertNotEqual(SOURCE['commit'], self.manifest['provenance']['tooling_commit'])

    def test_missing_selected_template_never_falls_back_to_working_tree(self):
        target = self.directory / common.README_SOURCE_PATH
        target.parent.mkdir(parents=True)
        target.write_text(README_TEMPLATE, encoding='utf-8')
        with patch.object(builder, 'git', return_value=b'') as git_read, \
                self.assertRaisesRegex(ValueError, 'regular src README template; no fallback'):
            builder.load_readme_source(self.directory, SOURCE['commit'])
        git_read.assert_called_once_with(self.directory, 'ls-tree', SOURCE['commit'], '--', common.README_SOURCE_PATH)

    def test_template_source_rejects_links_wrong_blob_and_invalid_utf8(self):
        record = readme_source()
        for mode in ('120000', '040000'):
            listing = (mode + ' blob ' + record['git_blob'] + '\t' + common.README_SOURCE_PATH + '\n').encode()
            with self.subTest(mode=mode), patch.object(builder, 'git', return_value=listing) as git_read, \
                    self.assertRaisesRegex(ValueError, 'regular src README template'):
                builder.load_readme_source(self.directory, SOURCE['commit'])
            self.assertEqual(git_read.call_count, 1)
        listing = ('100644 blob ' + record['git_blob'] + '\t' + common.README_SOURCE_PATH + '\n').encode()
        with patch.object(builder, 'git', side_effect=[listing, b'different']), self.assertRaisesRegex(ValueError, 'Git blob mismatch'):
            builder.load_readme_source(self.directory, SOURCE['commit'])
        raw = b'\xff'
        blob = hashlib.sha1(b'blob 1\0' + raw).hexdigest()
        listing = ('100644 blob ' + blob + '\t' + common.README_SOURCE_PATH + '\n').encode()
        with patch.object(builder, 'git', side_effect=[listing, raw]), self.assertRaises(UnicodeDecodeError):
            builder.load_readme_source(self.directory, SOURCE['commit'])

    def test_legacy_envelope_retains_absent_source_evidence_without_rewrite(self):
        legacy = fixture(self.directory, schema=common.LEGACY_SCHEMA)
        before = (self.directory / 'release-manifest.json').read_bytes()
        result = common.verify_bundle(self.directory, SOURCE)
        self.assertEqual(result, legacy)
        self.assertEqual(result['schema'], 'framework-release-assets/1')
        self.assertNotIn('readme_source', result['provenance'])
        self.assertEqual((self.directory / 'release-manifest.json').read_bytes(), before)

    def test_v2_catalog_product_sources_must_be_safe_src_paths(self):
        for name in ('tools/resource.md', '.dev/resource.md', 'src/../tools/resource.md',
                     'srcx/resource.md', 'src\\resource.md'):
            fixture(self.directory, catalog_source=name)
            with self.subTest(name=name), self.assertRaises(ValueError):
                common.verify_bundle(self.directory)
        good = fixture(self.directory, catalog_source='src/skills/reviewer/README.md')
        self.assertEqual(common.verify_bundle(self.directory), good)

    def test_current_product_template_has_exact_fixed_fields(self):
        template = (SCRIPTS.parents[1] / common.README_SOURCE_PATH).read_text(encoding='utf-8')
        rendered = common.render_readme(template, SOURCE, 'catalog-id', '0.19.0-rc.3')
        self.assertIn(('Source commit: ' + SOURCE['commit']).encode(), rendered)
        self.assertIn(b'Catalog identity: catalog-id', rendered)

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
