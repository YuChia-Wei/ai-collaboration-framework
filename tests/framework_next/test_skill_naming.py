"""Selection naming and entry projection in memory; no subset or installed target."""
from copy import deepcopy
from hashlib import sha1
from pathlib import Path
import sys
import unittest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path[:0] = [str(HERE), str(ROOT / "src")]
from distribution import catalog
from distribution.content import descriptor, desired_shape, selection_skill_naming
from distribution.data import json_bytes
from distribution.git_source import Blob
from distribution.package import load_package
from test_distribution_contracts import skill

def source_blob(name, raw):
    return Blob(name, sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest(), '100644', raw)

def tiny_catalog():
    """Fictional catalog identity; current execution bytes, one tiny instruction."""
    blobs = {name: source_blob(name, (ROOT / name).read_bytes()) for name in catalog.GENERATOR_FILES}
    metadata = skill()
    metadata['knowledge_consumption'] = []
    contents = {}
    files = []
    for name, raw in {
        'skill-package.yaml': json_bytes(metadata),
        'SKILL.md': b'---\nname: reviewer\ndescription: Synthetic naming fixture\n---\n[Review](review.md)\n',
        'review.md': b'Review the supplied text.\n',
    }.items():
        source = source_blob('src/skills/reviewer/' + name, raw)
        blobs[source.path] = source
        artifact = 'packages/skill/reviewer/' + name
        files.append({'path': artifact, 'kind': 'skill', 'owner': 'reviewer', 'member': name, 'source': source.identity()})
        contents[artifact] = raw
    package = load_package(blobs['src/skills/reviewer/skill-package.yaml'])
    adapters = []
    for runtime in ('claude', 'codex'):
        member = 'skill-entry-v2.md.template'
        source = blobs[f'src/adapters/{runtime}/{member}']
        artifact = f'adapters/{runtime}/{member}'
        files.append({'path': artifact, 'kind': 'adapter', 'owner': runtime, 'member': member, 'source': source.identity()})
        contents[artifact] = source.data
        adapters.append({'id': runtime, 'version': '2.0.0', 'prefix': 'aicf-', 'template': member, 'members': [member]})
    preset = {'preset_version': 1, 'id': 'tiny', 'version': '1.0.0', 'skills': ['reviewer'], 'knowledge': [], 'adapters': ['claude', 'codex']}
    for name, raw in {'src/profiles/tiny.yaml': json_bytes(preset), 'src/distribution/manifest.yaml': b'# Synthetic source fixture.\n'}.items():
        blobs[name] = source_blob(name, raw)
    doc = {'catalog_version': 1, 'release_version': '1.0.0', 'source': {'commit': '1' * 40, 'tree': '2' * 40},
           'components': [descriptor('skill', package)], 'adapters': adapters, 'presets': [preset],
           'build_inputs': [blobs[name].identity() for name in sorted(blobs)],
           'generator': {'id': 'aicf-catalog-assembly', 'implementation': [blobs[name].identity() for name in catalog.GENERATOR_FILES]}}
    inventory = {'catalog_files_version': 1, 'files': sorted(files, key=lambda row: row['path'])}
    raw = {catalog.PARENT_METADATA[0]: json_bytes(doc), catalog.PARENT_METADATA[1]: json_bytes(inventory)}
    doc, inventory, pin = catalog.parent_documents(raw)
    packages = catalog.packages_from(doc, inventory, contents)
    return catalog.Catalog(None, doc, inventory, pin, raw, contents, packages)

class SkillNamingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = tiny_catalog()
        cls.desired = {mode: catalog.expand_preset(cls.catalog, "tiny", "1.0.0", skill_naming=mode) for mode in ("original", "prefixed")}
        cls.desired["legacy"] = {key: value for key, value in cls.desired["prefixed"].items() if key != "skill_naming"}
        cls.desired["legacy"]["selection_version"] = 1

    def projected(self, desired):
        selection = catalog.resolve_selection(self.catalog, desired)
        payload = {}
        templates = {}
        for row in self.catalog.inventory["files"]:
            raw = self.catalog.contents[row["path"]]
            if row["kind"] == "skill":
                payload[f".ai/core/skills/{row['owner']}/{row['member']}"] = raw
            elif row["kind"] == "adapter":
                templates[row["owner"]] = raw
        return catalog.project_members(self.catalog.document, self.catalog.inventory, selection, payload, templates)

    def test_default_mode_and_legacy_selection_bytes(self):
        self.assertEqual(catalog.expand_preset(self.catalog, "tiny", "1.0.0"), self.desired["original"])
        legacy = deepcopy(self.desired["legacy"])
        before = json_bytes(legacy)
        self.assertIs(desired_shape(legacy), legacy)
        self.assertEqual(selection_skill_naming(legacy), "prefixed")
        self.assertEqual(json_bytes(legacy), before)
        self.assertEqual(self.projected(legacy), self.projected(self.desired["prefixed"]))

    def test_modes_change_only_runtime_entry_names_and_content(self):
        original_rows, original = self.projected(self.desired["original"])
        prefixed_rows, prefixed = self.projected(self.desired["prefixed"])
        for runtime in ("agents", "claude"):
            original_path = f".{runtime}/skills/reviewer/SKILL.md"
            prefixed_path = f".{runtime}/skills/aicf-reviewer/SKILL.md"
            self.assertIn(original_path, original)
            self.assertIn(prefixed_path, prefixed)
            self.assertNotIn(prefixed_path, original)
            self.assertNotIn(original_path, prefixed)
            self.assertIn(b"name: reviewer\n", original[original_path])
            self.assertIn(b"name: aicf-reviewer\n", prefixed[prefixed_path])
        for name in original:
            if name.startswith(".ai/"):
                self.assertEqual(original[name], prefixed[name])
        self.assertEqual([r for r in original_rows["files"] if r["kind"] == "payload"],
                         [r for r in prefixed_rows["files"] if r["kind"] == "payload"])

    def test_selection_is_closed_and_uses_exact_versions(self):
        for version in (True, False, 1.0, 2.0, "2", None, 0, 3):
            with self.subTest(version=version), self.assertRaises(ValueError):
                desired_shape({**self.desired["original"], "selection_version": version})
        for naming in (True, 1, None, [], "", "unknown"):
            with self.subTest(naming=naming), self.assertRaises(ValueError):
                desired_shape({**self.desired["original"], "skill_naming": naming})
        missing = {k: v for k, v in self.desired["original"].items() if k != "skill_naming"}
        for value in (missing, {**self.desired["legacy"], "skill_naming": "original"}, {**self.desired["original"], "unknown": 1}):
            with self.assertRaises(ValueError):
                desired_shape(value)

    def test_unknown_components_and_preset_provenance_are_rejected(self):
        for field, value in (("skills", ["missing"]), ("knowledge", ["missing"]), ("adapters", ["missing"])):
            with self.subTest(field=field), self.assertRaises(ValueError):
                catalog.resolve_selection(self.catalog, {**self.desired["original"], field: value})
        bad = deepcopy(self.desired["original"])
        bad["expanded_from"]["preset_sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "preset provenance"):
            catalog.resolve_selection(self.catalog, bad)


if __name__ == "__main__":
    unittest.main()
