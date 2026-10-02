"""Current source declarations and metadata behavior, without assembly or installation.

Source files are read in place. Synthetic metadata cases do not copy a checkout,
spawn Git, create candidates or assert a frozen catalog member count.
"""
from copy import deepcopy
from functools import lru_cache
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from distribution.content import closure, descriptor, load_content_package, selected_references
from distribution.contracts import validate
from distribution.data import DistributionError, json_bytes, yaml_object
from distribution.git_source import Blob
from distribution.package import check_references, load_package


@lru_cache(maxsize=1)
def source_inventory():
    manifest = validate("Manifest", yaml_object((ROOT / "src/distribution/manifest.yaml").read_bytes(), "manifest"))
    packages, contents = {}, {}
    for row in manifest["components"]:
        name = row["source"] + "/" + row["metadata"]
        raw = (ROOT / name).read_bytes()
        parser = load_package if row["kind"] == "skill" else load_content_package
        package = parser(Blob(name, "0" * 40, "100644", raw))
        key = (row["kind"], row["id"])
        if key in packages:
            raise AssertionError("duplicate component: " + repr(key))
        packages[key] = package
        for member in row["members"]:
            source = row["source"] + "/" + member["source"]
            contents[(*key, member["source"])] = (ROOT / source).read_bytes()
    return manifest, packages, contents


def metadata(owner):
    # Return a fresh mapping because rejection cases intentionally mutate it.
    path = ROOT / "src/skills" / owner / "skill-package.yaml"
    return yaml_object(path.read_bytes(), str(path))


class SourceDeclarationTests(unittest.TestCase):
    def test_declared_members_and_metadata_agree(self):
        manifest, packages, contents = source_inventory()
        destinations = []
        for row in manifest["components"]:
            key = (row["kind"], row["id"])
            package = packages[key]
            with self.subTest(component=key):
                self.assertEqual((package.id, package.version), (row["id"], row["version"]))
                names = [m["source"] for m in row["members"]]
                self.assertEqual(len(names), len(set(names)))
                self.assertEqual(set(names), package.members)
                for member in row["members"]:
                    destinations.append(member["destination"].casefold())
                    self.assertTrue(contents[(*key, member["source"])])
                if row["kind"] == "skill":
                    blobs = {name: Blob(name, "0" * 40, "100644", contents[(*key, name)]) for name in names}
                    self.assertEqual(check_references(package, blobs)["name"], row["id"])
        self.assertEqual(len(destinations), len(set(destinations)))
        closure(sorted((descriptor(kind, p) for (kind, _), p in packages.items()), key=lambda row: (row["kind"], row["id"])))
        self.assertEqual(selected_references(packages, contents), [])

    def test_presets_select_declared_components_and_adapters(self):
        manifest, packages, _ = source_inventory()
        profiles = [row["id"] for row in manifest["profiles"]]
        self.assertEqual(len(profiles), len(set(profiles)))
        adapters = {row["id"] for row in manifest["adapters"]}
        for row in manifest["profiles"]:
            preset = validate("Preset", yaml_object((ROOT / row["path"]).read_bytes(), row["path"]))
            with self.subTest(preset=row["id"]):
                self.assertEqual(preset["id"], row["id"])
                self.assertLessEqual(set(preset["adapters"]), adapters)
                selected = {(kind, name) for kind, field in (("skill", "skills"), ("knowledge", "knowledge")) for name in preset[field]}
                self.assertLessEqual(selected, packages.keys())
                closure(sorted((descriptor(kind, packages[(kind, name)]) for kind, name in selected), key=lambda row: (row["kind"], row["id"])))

    def test_declared_instruction_and_tool_members_are_readable(self):
        _, packages, contents = source_inventory()
        for (kind, owner), package in packages.items():
            if kind != "skill":
                continue
            data = package.metadata
            with self.subTest(skill=owner):
                self.assertIn(data["entrypoint"], package.members)
                for name in package.members:
                    contents[(kind, owner, name)].decode("utf-8")
                for operation in data["operations"]:
                    if operation.get("execution") == "instruction":
                        self.assertIn(operation["instructions"], package.members)
                if data["configuration"] is None:
                    self.assertEqual(data["artifact_roles"], [])

def blob(name, value):
    raw = value if type(value) is bytes else json_bytes(value)
    return Blob(name, '0' * 40, '100644', raw)

def load_synthetic(document):
    return load_package(blob('synthetic/skill-package.yaml', document))

def instruction(owner):
    return {'metadata_version': 3, 'id': owner, 'version': '0.1.0',
            'delivery_status': 'implemented', 'entrypoint': 'SKILL.md',
            'dependencies': {'required': [], 'optional': []},
            'runtime': [{'id': 'skill-instruction-reader', 'requirement': 'Read text',
                         'for_operations': ['review'], 'on_missing': 'unavailable'}],
            'configuration': None, 'artifact_roles': [],
            'resources': {'references': ['review.md'], 'schemas': [], 'templates': [], 'tools': []},
            'operations': [{'id': 'review', 'execution': 'instruction', 'inputs': ['text'],
                            'outputs': ['prose'], 'instructions': 'review.md',
                            'implementation_status': 'implemented'}]}

class MetadataTests(unittest.TestCase):
    def test_minimal_synthetic_v1(self):
        data = instruction('tiny')
        data['metadata_version'] = 1
        data['runtime'] = []
        data['configuration'] = {'namespace': 'tiny', 'defaults': {
            'store': {'kind': 'filesystem', 'root': 'records', 'tracking': 'tracked'},
            'template': {'origin': 'package', 'path': 'view.md'}}}
        data['artifact_roles'] = [
            {'role': 'tiny.record', 'owner': 'project', 'schema': 'tiny.record@1.0.0',
             'store_binding': 'tiny.store', 'identity': 'tiny-id', 'filename': '<id>.json',
             'read_operations': ['read'], 'write_operations': []},
            {'role': 'tiny.view', 'owner': 'derived', 'source_role': 'tiny.record',
             'output': 'text', 'persistence': 'caller-owned', 'produce_operations': ['read']}]
        data['resources'].update(
            schemas=[{'id': 'tiny.record', 'version': '1.0.0', 'path': 'record.json', 'owner': 'tiny', 'migration': 'unsupported'}],
            templates=[{'id': 'tiny.template', 'path': 'view.md', 'input_role': 'tiny.record', 'output_role': 'tiny.view', 'owner': 'tiny'}],
            tools=[{'id': 'tiny.tool', 'owner': 'tiny', 'implementation_status': 'implemented',
                    'entrypoint': 'read.py', 'operation_contract': 'review.md', 'operations': ['read']}])
        data['operations'] = [{'id': 'read', 'tool': 'tiny.tool', 'inputs': ['record'],
                               'outputs': ['view'], 'implementation_status': 'implemented'}]
        result = load_synthetic(data)
        self.assertEqual(result.members, {'SKILL.md', 'skill-package.yaml', 'review.md', 'record.json', 'view.md', 'read.py'})
        self.assertNotIn('read_schemas', result.metadata['artifact_roles'][0])

    def test_reject_version_types_and_duplicate_schema(self):
        for version in (True, 1.0, 2.0, 3.0, 4.0, 0, 99):
            with self.subTest(version=repr(version)):
                data = metadata('lesson-author')
                data['metadata_version'] = version
                with self.assertRaisesRegex(DistributionError, 'integer metadata versions|unsupported-version'):
                    load_synthetic(data)
        data = metadata('lesson-author')
        data['resources']['schemas'].append(deepcopy(data['resources']['schemas'][0]))
        with self.assertRaisesRegex(DistributionError, 'duplicate schema identity'):
            load_synthetic(data)

    def test_reject_owner_and_undeclared_tool_or_reference(self):
        for defect in ('owner', 'tool', 'reference'):
            with self.subTest(defect=defect):
                data = metadata('lesson-author')
                if defect == 'owner':
                    data['resources']['schemas'][0]['owner'] = 'foreign'
                    pattern = 'resource owner mismatch'
                elif defect == 'tool':
                    data['operations'][0]['tool'] = 'unknown'
                    pattern = 'tool mapping is inconsistent'
                else:
                    data['resources']['tools'][0]['operation_contract'] = 'missing.md'
                    pattern = 'declared reference'
                with self.assertRaisesRegex(DistributionError, pattern):
                    load_synthetic(data)
        data = instruction('tiny')
        data['operations'][0]['instructions'] = 'undeclared.md'
        with self.assertRaisesRegex(DistributionError, 'declared reference'):
            load_synthetic(data)

    def test_restricted_yaml_rejects_anchors_and_duplicate_keys(self):
        for raw, reason in [(b'value: &alias [tiny]\ncopy: *alias\n', 'anchors are forbidden'),
                            (b'value: one\nvalue: two\n', 'duplicate or merge key')]:
            with self.subTest(reason=reason), self.assertRaisesRegex(DistributionError, reason):
                yaml_object(raw, 'synthetic restricted YAML')

    def test_reject_mixed_union_and_null_config_artifact(self):
        data = metadata('problem-frame-author')
        for arm in ('instruction', 'tool'):
            broken = deepcopy(data)
            operation = next(o for o in broken['operations'] if o['execution'] == arm)
            operation['tool' if arm == 'instruction' else 'instructions'] = 'extra'
            with self.subTest(arm=arm), self.assertRaisesRegex(DistributionError, 'unknown keys'):
                load_synthetic(broken)
        data['configuration'] = None
        with self.assertRaisesRegex(DistributionError, 'null configuration requires empty'):
            load_synthetic(data)


if __name__ == "__main__":
    unittest.main()
