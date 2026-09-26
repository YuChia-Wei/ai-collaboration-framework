"""Issue 409: bounded synthetic naming/reader/planner fixtures, never target adoption.

Uses real projection, artifact/lock readers and planning. Planner engine admission
and native backend setup are mocked; manual fixture realization is not apply,
recovery, provenance validation or Codex/Claude UI discovery evidence.
"""
from contextlib import nullcontext, redirect_stderr, redirect_stdout
from copy import deepcopy
from hashlib import sha1
import argparse
import io
import json
import os
from pathlib import Path
import sys
from types import ModuleType
import unittest
from unittest.mock import patch

HERE = Path(__file__).absolute().parent
sys.dont_write_bytecode = True
sys.path[:0] = [str(HERE), str(HERE.parents[1] / 'src')]
import support
from distribution import catalog, contracts, installation_plan as planning, installation_state as state
from distribution.content import descriptor, desired_shape, selection_skill_naming
from distribution.data import json_bytes
from distribution.git_source import Blob
from distribution.package import load_package
from test_rc2_distribution import skill

ROOT = HERE.parents[1]
MODE = 'windows-inventory-only' if os.name == 'nt' else 'posix-permissions'


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
    doc = {'catalog_version': 1, 'release_version': '0.19.0-rc.2', 'source': {'commit': '1' * 40, 'tree': '2' * 40},
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
        cls.engine = {'id': 'framework-managed-installation', 'version': '2.0.0', 'source_commit': '1' * 40,
                      'files': [{'path': row['path'], 'sha256': row['sha256']} for row in cls.catalog.document['generator']['implementation']]}
        cls.desired = {mode: catalog.expand_preset(cls.catalog, 'tiny', '1.0.0', skill_naming=mode) for mode in ('original', 'prefixed')}
        cls.desired['legacy'] = {key: value for key, value in cls.desired['prefixed'].items() if key != 'skill_naming'}
        cls.desired['legacy']['selection_version'] = 1
        output = support.active_run().case('candidates')
        cls.candidates = {}
        for mode, desired in cls.desired.items():
            result = catalog.derive_subset(cls.catalog, desired, output, output)
            cls.candidates[mode] = state.read_candidate(result['artifact_root'])
        support.active_run().measure()

    def roots(self, name):
        base = support.active_run().case(name)
        roots = {}
        for role in ('project', 'engine', 'scratch', 'staging', 'recovery'):
            roots[role] = base / role
            roots[role].mkdir()
        return roots

    def write(self, path, raw):
        path.parent.mkdir(parents=True, exist_ok=True)
        # Large metadata is generated from the tiny fixture, not authored input.
        with path.open('wb') as stream:
            stream.write(raw)
        if os.name == 'posix':
            path.chmod(0o644)
        support.active_run().measure()

    def realize(self, roots, candidate, previous=None):
        """Manual fixture state, explicitly not production apply or recovery."""
        if previous:
            for name in set(previous.members) - set(candidate.members):
                target = roots['project'] / name
                self.assertTrue(target.is_relative_to(support.active_run().root))
                target.unlink()
        for name, raw in candidate.contents.items():
            self.write(roots['project'] / name, raw)
        raw = json_bytes(catalog.lock_document(candidate, self.engine, '3' * 32, MODE, []))
        self.write(roots['project'] / state.LOCK_PATH, raw)
        return state.read_lock(str(roots['project']))

    def plan(self, roots, candidate):
        lock = state.read_lock(str(roots['project']))
        request = {'api_version': 2, 'operation': 'plan', 'project_root': str(roots['project']),
                   'engine_root': str(roots['engine']), 'engine': self.engine, 'candidate_root': str(candidate.root),
                   'candidate_identity': candidate.identity, 'expected_lock_sha256': lock.sha256 if lock else None,
                   'mode_policy': MODE, 'project_data_action': 'none', 'protected_inputs': [], 'project_edits': [],
                   'durability': {'declared_by': 'fixture', 'declaration_reference': 'synthetic-only', 'failure_domain': 'process-termination'},
                   **{role + '_root': str(roots[role]) for role in ('scratch', 'staging', 'recovery')}}
        with patch.object(state, '_engine'), patch.object(planning, 'Backend'):
            return planning.plan(request)

    def test_default_explicit_modes_and_unchanged_v1_bytes(self):
        self.assertEqual(catalog.expand_preset(self.catalog, 'tiny', '1.0.0'), self.desired['original'])
        self.assertEqual(self.desired['original']['selection_version'], 2)
        legacy = deepcopy(self.desired['legacy'])
        before = json_bytes(legacy)
        self.assertIs(desired_shape(legacy), legacy)
        self.assertEqual(selection_skill_naming(legacy), 'prefixed')
        self.assertEqual(json_bytes(legacy), before)
        self.assertEqual(self.candidates['legacy'].contents, self.candidates['prefixed'].contents)
        self.assertEqual(self.candidates['legacy'].inventory, self.candidates['prefixed'].inventory)
        self.assertEqual(len({candidate.identity for candidate in self.candidates.values()}), 3)

    def test_closed_selection_versions_and_schema_mirror(self):
        schema = json.loads((ROOT / '.dev/design/framework-next/rc2-contracts/schemas/contracts.schema.json').read_text())
        self.assertEqual(contracts.DEFINITIONS, schema['$defs'])
        for version in (True, False, 1.0, 2.0, '2', None, 0, 3):
            invalid = {**self.desired['original'], 'selection_version': version}
            with self.subTest(version=version), self.assertRaises(ValueError):
                desired_shape(invalid)
        for naming in (True, 1, None, [], {}, '', 'Original', 'aicf', 'framework'):
            invalid = {**self.desired['original'], 'skill_naming': naming}
            with self.subTest(naming=naming), self.assertRaises(ValueError):
                desired_shape(invalid)
        missing = {key: value for key, value in self.desired['original'].items() if key != 'skill_naming'}
        for invalid in (missing, {**self.desired['legacy'], 'skill_naming': 'original'}, {**self.desired['original'], 'unknown': 1}):
            with self.assertRaises(ValueError):
                desired_shape(invalid)

    def test_nonempty_reader_inventory_lock_binding_and_tamper(self):
        for mode, candidate in self.candidates.items():
            expected_name = 'reviewer' if mode == 'original' else 'aicf-reviewer'
            runtime = [row for row in candidate.inventory['files'] if row['kind'] == 'runtime']
            self.assertEqual({row['destination'] for row in runtime}, {f'{root}/skills/{expected_name}/SKILL.md' for root in ('.agents', '.claude')})
            self.assertTrue(all(row['binding']['entry_name'] == expected_name for row in runtime))
            self.assertTrue(all(row['binding']['skill'] == 'reviewer' and row['owner'].endswith('/skill/reviewer') for row in runtime))
            document = catalog.lock_document(candidate, self.engine, '3' * 32, MODE, [])
            lock = state._lock_bytes(json_bytes(document))
            self.assertEqual(lock.document['selection']['desired'], self.desired[mode])
            self.assertEqual(lock.document['selection']['desired_sha256'], catalog.digest(json_bytes(self.desired[mode])))
            state.verify_lock_contents(lock, candidate.contents)
            tampered = deepcopy(candidate.inventory)
            next(row for row in tampered['files'] if row['kind'] == 'runtime')['binding']['entry_name'] = 'wrong'
            with self.assertRaises(ValueError):
                catalog.subset_inventory(self.catalog.document, self.catalog.inventory, candidate.selection, tampered)

    def test_repeated_rename_plans_both_runtimes_and_directions(self):
        roots = self.roots('rename-plans')
        previous = None
        for mode in ('legacy', 'original', 'prefixed', 'original'):
            candidate = self.candidates[mode]
            result = self.plan(roots, candidate)
            self.assertEqual(result['outcome'], 'planned', result)
            if previous:
                rows = [row for row in result['plan']['delta'] if row['destination'].startswith(('.agents/', '.claude/'))]
                self.assertEqual([row['action'] for row in rows].count('add'), 2)
                self.assertEqual([row['action'] for row in rows].count('remove'), 2)
            self.realize(roots, candidate, previous)
            observation = state.observe_installation(str(roots['project']), candidate)
            self.assertEqual(observation.drift, [])
            self.assertEqual(self.plan(roots, candidate)['plan']['noop'], True)
            previous = candidate

    def test_unowned_destination_and_owned_drift_block_without_writes(self):
        old, new = self.candidates['prefixed'], self.candidates['original']
        for runtime in ('.agents', '.claude'):
            roots = self.roots('collision-' + runtime[1:])
            self.realize(roots, old)
            destination = roots['project'] / f'{runtime}/skills/reviewer/SKILL.md'
            self.write(destination, new.contents[destination.relative_to(roots['project']).as_posix()])
            result = self.plan(roots, new)
            self.assertEqual(result['diagnostics'][0]['code'], 'unowned-collision', result)
            self.assertTrue((roots['project'] / f'{runtime}/skills/aicf-reviewer/SKILL.md').exists())
        roots = self.roots('owned-drift')
        self.realize(roots, old)
        self.write(roots['project'] / '.agents/skills/aicf-reviewer/SKILL.md', b'owner edit\n')
        result = self.plan(roots, new)
        self.assertEqual(result['diagnostics'][0]['code'], 'owned-drift', result)
        self.assertFalse((roots['project'] / '.agents/skills/reviewer/SKILL.md').exists())

    def test_discoverable_withdrawal_remnants_block_for_both_names_and_runtimes(self):
        for mode, other in (('original', 'prefixed'), ('prefixed', 'original')):
            for runtime in ('.agents', '.claude'):
                roots = self.roots('remnant-' + mode + '-' + runtime[1:])
                old, new = self.candidates[mode], self.candidates[other]
                self.realize(roots, old)
                name = 'reviewer' if mode == 'original' else 'aicf-reviewer'
                remnant = roots['project'] / f'{runtime}/skills/{name}/extra/SKILL.md'
                self.write(remnant, b'unknown discoverable skill\n')
                result = self.plan(roots, new)
                self.assertEqual(result['diagnostics'][0]['code'], 'legacy-discovery-collision', result)
                self.assertTrue(remnant.exists())

    def test_rc1_framework_entry_can_be_withdrawn_and_extra_discovery_blocks(self):
        from distribution import assembly
        from test_versioned_candidates import SyntheticSource, fixture_lock
        source = SyntheticSource()
        manifest = json.loads(source.blobs['src/distribution/manifest.yaml'].data)
        profile = json.loads(source.blobs['src/profiles/tiny.yaml'].data)
        template_name = 'src/adapters/codex/skill-entry.md.template'
        manifest['adapters'] = [{'id': 'codex', 'template': template_name}]
        profile['adapters'] = ['codex']
        for name, raw in {'src/distribution/manifest.yaml': json_bytes(manifest),
                          'src/profiles/tiny.yaml': json_bytes(profile),
                          template_name: (ROOT / template_name).read_bytes()}.items():
            source.blobs[name] = source_blob(name, raw)
        implementation = [{'source': source.read('src/distribution/data.py').identity(), 'execution_file_sha256': '3' * 64}]
        output = support.active_run().case('rc1-candidate')
        with patch.object(assembly, 'GitSource', return_value=source), patch.object(assembly, 'implementation_identity', return_value=implementation):
            built = assembly.assemble_versioned(source.repository, source.commit, 'tiny', output, output, release_version='0.19.0-rc.1')
        old = state.read_candidate(built['candidate_root'])
        old_entry = '.agents/skills/framework-tiny/SKILL.md'
        self.assertIn(old_entry, old.members)
        for extra in (False, True):
            roots = self.roots('rc1-' + ('remnant' if extra else 'withdraw'))
            for name, raw in old.contents.items():
                self.write(roots['project'] / name, raw)
            self.write(roots['project'] / state.LOCK_PATH, json_bytes(fixture_lock(old)))
            if extra:
                self.write(roots['project'] / '.agents/skills/framework-tiny/extra/SKILL.md', b'unknown discovery\n')
            result = self.plan(roots, self.candidates['original'])
            if extra:
                self.assertEqual(result['diagnostics'][0]['code'], 'legacy-discovery-collision', result)
            else:
                self.assertEqual(result['outcome'], 'planned', result)
                self.assertEqual(next(row['action'] for row in result['plan']['delta'] if row['destination'] == old_entry), 'remove')
                for runtime in ('.agents', '.claude'):
                    self.assertEqual(next(row['action'] for row in result['plan']['delta'] if row['destination'] == f'{runtime}/skills/reviewer/SKILL.md'), 'add')
            self.assertTrue((roots['project'] / old_entry).exists())

    def test_saved_selection_requires_exact_selected_mode(self):
        roots = self.roots('saved-mode')
        name = '.ai/custom/installation.json'
        raw = json_bytes(self.desired['original'])
        self.write(roots['project'] / name, raw)
        protected = [{'path': name, 'sha256': catalog.digest(raw)}]
        self.assertEqual(planning.project_bindings(state._Reader(), roots['project'], self.candidates['original'], protected, [], {}), protected)
        with self.assertRaises(ValueError):
            planning.project_bindings(state._Reader(), roots['project'], self.candidates['prefixed'], protected, [], {})

    def test_cli_default_opt_in_saved_selection_and_override_rejection(self):
        module = ModuleType('naming_cli_fixture')
        module.__file__ = str(ROOT / 'tools/derive-subset.py')
        exec(compile(Path(module.__file__).read_bytes(), module.__file__, 'exec'), module.__dict__)
        roots = self.roots('cli')
        saved = roots['project'] / 'selection.json'
        self.write(saved, json_bytes(self.desired['prefixed']))
        common = ['derive-subset', '--catalog-root', str(roots['project']), '--catalog-identity', self.catalog.pin['identity'],
                  '--engine-pin', str(roots['engine'] / 'pin.json'), '--output-root', str(roots['staging']), '--scratch-root', str(roots['scratch'])]
        for options, expected in ((['--preset', 'tiny', '--preset-version', '1.0.0'], 'original'),
                                  (['--preset', 'tiny', '--preset-version', '1.0.0', '--skill-naming', 'prefixed'], 'prefixed'),
                                  (['--selection', str(saved)], 'prefixed')):
            with patch.object(sys, 'argv', common + options), patch.object(module, 'verified_host', return_value=nullcontext()), \
                    patch.object(catalog, 'read_catalog', return_value=self.catalog), patch.object(catalog, 'derive_subset', return_value={'outcome': 'fixture'}) as derive, \
                    redirect_stdout(io.StringIO()):
                self.assertEqual(module.main(), 0)
                self.assertEqual(derive.call_args.args[1]['skill_naming'], expected)
        for options in (['--selection', str(saved), '--skill-naming', 'original'],
                        ['--selection', str(saved), '--skill-naming', 'prefixed'],
                        ['--preset', 'tiny', '--preset-version', '1.0.0', '--skill-naming', 'invalid']):
            with patch.object(sys, 'argv', common + options), patch.object(module, 'verified_host') as host, redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
                module.main()
            host.assert_not_called()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-root', type=Path, required=True)
    args = parser.parse_args()
    support.check(sys.flags.isolated and sys.flags.dont_write_bytecode, 'Use -I -B.')
    run = support.FixtureRun(args.output_root)
    success = False
    try:
        with support.use_run(run):
            result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(SkillNamingTests))
            success = result.wasSuccessful() and not result.skipped
            return 0 if success else 1
    finally:
        print(json.dumps({'fixture_accounting': run.close(success)}, sort_keys=True))


if __name__ == '__main__':
    raise SystemExit(main())
