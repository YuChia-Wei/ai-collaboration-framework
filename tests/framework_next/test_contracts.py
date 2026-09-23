"""Selected C1-C3/C5 contracts. Synthetic inputs are named explicitly."""
from __future__ import annotations

from contextlib import contextmanager, redirect_stderr
from copy import deepcopy
from functools import lru_cache
from hashlib import sha256
import io
import json
from pathlib import Path
import posixpath
import re
import tempfile
import time
import unittest
from urllib.parse import unquote, urlsplit

from distribution import assembly, installation_state
from distribution.data import DistributionError, json_bytes, yaml_object
from distribution.git_source import Blob, GitSource
from distribution.package import check_references, load_package
from distribution.selection import select
import support

KNOWLEDGE = {'lesson', 'adr', 'standards-promotion'}
WORK = {'pr', 'local-backlog', 'software-development-orchestrator'}
ENGINEERING = {'code-reviewer', 'requirement-author', 'spec-author', 'diagnostic-analyst',
               'ddd-ca-hex-architect', 'bdd-gwt-test-designer', 'local-change-implementer',
               'slice-implementer', 'problem-frame-author', 'spec-compliance-validator'}
MAINTENANCE = {'ai-context-auditor', 'ai-context-governance'}
PROFILES = {'lesson-minimal': ({'lesson'}, 9), 'knowledge': (KNOWLEDGE, 26),
            'work-management': (WORK, 28), 'engineering': (ENGINEERING, 53),
            'collaboration': (KNOWLEDGE | WORK | ENGINEERING, 107),
            'source-repository': ((KNOWLEDGE | WORK | ENGINEERING) - {'local-backlog'}, 99),
            'context-maintenance': (MAINTENANCE, 6)}


def blob(name, value):
    raw = value if type(value) is bytes else json_bytes(value)
    return Blob(name, '0' * 40, '100644', raw)  # explicitly synthetic identity


class BlobInputs:
    """In-memory transport only. Production readers own every format's semantics."""
    def __init__(self, blobs):
        self.blobs = blobs

    def read(self, name):
        if name not in self.blobs:
            raise DistributionError('missing selected input: ' + name)
        return self.blobs[name]


@lru_cache(maxsize=1)
def actual_source():
    commit = support.git('rev-parse', 'HEAD').decode().strip()
    manifest_name = 'src/distribution/manifest.yaml'
    blobs = support.git_blobs(commit, [manifest_name])
    manifest = yaml_object(blobs[manifest_name].data, manifest_name)
    names = [row['path'] for row in manifest['profiles']]
    names += [row['template'] for row in manifest['adapters']]
    names += [f"{component['source']}/{row['source']}" for component in manifest['components']
              for row in component['members']]
    blobs.update(support.git_blobs(commit, names))
    return commit, manifest, BlobInputs(blobs)


def metadata(owner):
    return yaml_object(actual_source()[2].read(f'src/skills/{owner}/skill-package.yaml').data, owner)


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


def synthetic_selection(documents, selected):
    components, inputs = [], {}
    for document in documents:
        owner = document['id']
        source = f'src/skills/{owner}'
        members = ['SKILL.md', 'skill-package.yaml', 'review.md']
        components.append({'id': owner, 'source': source, 'metadata': 'skill-package.yaml',
                           'members': [{'source': name, 'destination': f'.ai/core/skills/{owner}/{name}'}
                                       for name in members]})
        inputs[source + '/skill-package.yaml'] = blob(source + '/skill-package.yaml', document)
        inputs[source + '/SKILL.md'] = blob(source + '/SKILL.md',
            f'---\nname: {owner}\ndescription: Tiny synthetic instruction\n---\n[Review](review.md)\n'.encode())
        inputs[source + '/review.md'] = blob(source + '/review.md', b'Read the selected text.\n')
    inputs['src/distribution/manifest.yaml'] = blob('src/distribution/manifest.yaml',
        {'manifest_version': 1, 'profiles': [{'id': 'tiny', 'path': 'src/profiles/tiny.yaml'}],
         'components': components, 'adapters': []})
    inputs['src/profiles/tiny.yaml'] = blob('src/profiles/tiny.yaml',
        {'profile_version': 1, 'id': 'tiny', 'skills': [{'id': name, 'version': '0.1.0'} for name in selected],
         'adapters': []})
    return BlobInputs(inputs)


class SourceClosureTests(unittest.TestCase):
    def test_c1_exact_packages_members_profiles_and_projection(self):
        commit, manifest, source = actual_source()
        owners = KNOWLEDGE | WORK | ENGINEERING | MAINTENANCE
        self.assertEqual({c['id'] for c in manifest['components']}, owners)
        self.assertEqual(len(manifest['components']), 18)
        self.assertEqual({p['id'] for p in manifest['profiles']}, set(PROFILES))
        self.assertEqual(sum(len(c['members']) for c in manifest['components']), 113)
        components = {c['id']: c for c in manifest['components']}
        expected = {}
        for owner, component in components.items():
            with self.subTest(package=owner):
                package = load_package(source.read(f"{component['source']}/{component['metadata']}"))
                self.assertEqual(package.id, owner)
                self.assertEqual(package.version, '0.2.0' if owner == 'lesson' else '0.1.0')
                mapping = {m['source']: m['destination'] for m in component['members']}
                self.assertEqual(set(mapping), package.members)
                self.assertEqual(len(mapping), len(component['members']))
                contents = {name: source.read(component['source'] + '/' + name) for name in package.members}
                self.assertEqual(check_references(package, contents)['name'], owner)
                for name, member in contents.items():
                    destination = f'.ai/core/skills/{owner}/{name}'
                    self.assertEqual(mapping[name], destination)
                    self.assertIn(member.mode, {'100644', '100755'})
                    expected[destination] = (owner, member)
        for profile, (selected, count) in PROFILES.items():
            with self.subTest(profile=profile):
                result = select(source, profile)
                self.assertEqual({p.id for p in result.packages}, selected)
                payload = {m.destination: m for m in result.members if m.envelope == 'payload'}
                wanted = {name: row for name, row in expected.items() if row[0] in selected}
                self.assertEqual(set(payload), set(wanted))
                self.assertEqual(len(payload), count)
                for destination, member in payload.items():
                    owner, original = wanted[destination]
                    self.assertEqual((member.owner, member.mode, member.data, member.source),
                                     (owner, original.mode, original.data, original))
                entries = [m for m in result.members if m.envelope == 'runtime']
                self.assertEqual({m.destination for m in entries},
                                 {f'.agents/skills/framework-{p}/SKILL.md' for p in selected})
                self.assertEqual(len(result.members), count + len(selected))
                for entry in entries:
                    self.assertEqual(entry.mode, '100644')
                    text = entry.data.decode('utf-8')
                    targets = []
                    for match in re.finditer(r'\[[^\]\n]*\]\(([^)]+)\)', text):
                        target = urlsplit(unquote(match.group(1)))
                        self.assertFalse(target.scheme or target.netloc or target.query)
                        targets.append(posixpath.normpath(posixpath.join(posixpath.dirname(entry.destination), target.path)))
                    owner = entry.owner.removeprefix('codex/')
                    self.assertEqual(set(targets), {d for d, (p, _) in wanted.items() if p == owner})
                    self.assertNotRegex(text, r'src/|\.ai/assets/|\.dev/|[A-Za-z]:[\\/]')
        print(json.dumps({'C1': {'source_commit': commit, 'packages': 18, 'payload_members': 113,
                                'profiles': 7, 'physical_assembly_scope': 'separate C5; this observation is declarations only'}}))

    def test_c2_actual_v2_v3_union_and_null_config_projection(self):
        _, _, source = actual_source()
        lesson = load_package(source.read('src/skills/lesson/skill-package.yaml'))
        record = next(r for r in lesson.metadata['artifact_roles'] if r['owner'] == 'project')
        self.assertEqual(lesson.metadata['metadata_version'], 2)
        self.assertEqual(record['read_schemas'], ['lesson.record@1.0.0', 'lesson.record@2.0.0'])
        self.assertEqual(record['schema'], 'lesson.record@2.0.0')
        cbf = load_package(source.read('src/skills/problem-frame-author/skill-package.yaml'))
        self.assertEqual(cbf.metadata['metadata_version'], 3)
        self.assertEqual({o['execution'] for o in cbf.metadata['operations']}, {'instruction', 'tool'})
        null_owners = (ENGINEERING - {'problem-frame-author'}) | MAINTENANCE
        self.assertEqual(len(null_owners), 11)
        for owner in sorted(null_owners):
            with self.subTest(owner=owner):
                package = load_package(source.read(f'src/skills/{owner}/skill-package.yaml'))
                data = package.metadata
                self.assertEqual(data['metadata_version'], 3)
                self.assertIsNone(data['configuration'])
                self.assertEqual(data['artifact_roles'], [])
                self.assertEqual({o['execution'] for o in data['operations']}, {'instruction'})
                expected_runtime = ['skill-instruction-reader']
                if owner in {'local-change-implementer', 'slice-implementer'}:
                    expected_runtime.append('authorized-target-editor')
                self.assertEqual([r['id'] for r in data['runtime']], expected_runtime)
                for field in ['schemas', 'templates', 'tools']:
                    self.assertEqual(data['resources'][field], [])
                profile = 'context-maintenance' if owner in MAINTENANCE else 'engineering'
                entry = next(m for m in select(source, profile).members if m.owner == 'codex/' + owner)
                text = entry.data.decode()
                self.assertIn('configuration: null', text)
                self.assertIn('Do not resolve or create either', text)
                self.assertNotIn('.ai/custom/framework.json', text)
                self.assertNotIn('explicit `project_root`', text)


class MetadataTests(unittest.TestCase):
    def test_c2_minimal_synthetic_v1(self):
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

    def test_c2_reject_version_types_and_duplicate_schema(self):
        for version in (True, 1.0, 2.0, 3.0, 4):
            with self.subTest(version=repr(version)):
                data = metadata('lesson')
                data['metadata_version'] = version
                with self.assertRaisesRegex(DistributionError, 'integer metadata versions'):
                    load_synthetic(data)
        data = metadata('lesson')
        data['resources']['schemas'].append(deepcopy(data['resources']['schemas'][0]))
        with self.assertRaisesRegex(DistributionError, 'duplicate schema identity'):
            load_synthetic(data)

    def test_c2_reject_owner_and_undeclared_tool_or_reference(self):
        for defect in ('owner', 'tool', 'reference'):
            with self.subTest(defect=defect):
                data = metadata('lesson')
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

    def test_c2_restricted_yaml_rejects_anchors_and_duplicate_keys(self):
        for raw, reason in [(b'value: &alias [tiny]\ncopy: *alias\n', 'anchors are forbidden'),
                            (b'value: one\nvalue: two\n', 'duplicate or merge key')]:
            with self.subTest(reason=reason), self.assertRaisesRegex(DistributionError, reason):
                yaml_object(raw, 'synthetic restricted YAML')

    def test_c2_reject_mixed_union_and_null_config_artifact(self):
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


class SelectionTests(unittest.TestCase):
    def test_c3_required_optional_version_and_cycle(self):
        alpha, beta = instruction('alpha'), instruction('beta')
        alpha['dependencies']['required'] = [{'id': 'beta', 'version': '0.1.0'}]
        with self.assertRaisesRegex(DistributionError, 'requires unselected beta'):
            select(synthetic_selection([alpha, beta], ['alpha']), 'tiny')
        alpha['dependencies'] = {'required': [], 'optional': [
            {'id': 'beta', 'version': '0.1.0', 'operations': ['review'], 'on_missing': 'unsupported'}]}
        absent = select(synthetic_selection([alpha, beta], ['alpha']), 'tiny')
        self.assertEqual([p.id for p in absent.packages], ['alpha'])
        self.assertEqual({m.owner for m in absent.members}, {'alpha'})
        alpha['dependencies'] = {'required': [{'id': 'beta', 'version': '0.2.0'}], 'optional': []}
        with self.assertRaisesRegex(DistributionError, 'incompatible required version'):
            select(synthetic_selection([alpha, beta], ['alpha', 'beta']), 'tiny')
        alpha['dependencies']['required'][0]['version'] = '0.1.0'
        beta['dependencies']['required'] = [{'id': 'alpha', 'version': '0.1.0'}]
        with self.assertRaisesRegex(DistributionError, 'dependency cycle'):
            select(synthetic_selection([alpha, beta], ['alpha', 'beta']), 'tiny')

    def test_c3_selected_version_and_manifest_collisions(self):
        source = synthetic_selection([instruction('alpha')], ['alpha'])
        profile = yaml_object(source.read('src/profiles/tiny.yaml').data, 'tiny')
        profile['skills'][0]['version'] = '0.2.0'
        source.blobs['src/profiles/tiny.yaml'] = blob('src/profiles/tiny.yaml', profile)
        with self.assertRaisesRegex(DistributionError, 'metadata identity disagrees'):
            select(source, 'tiny')
        for extra in ('skill.md', 'review.md/child', '../outside'):
            with self.subTest(path=extra):
                source = synthetic_selection([instruction('alpha')], ['alpha'])
                manifest = yaml_object(source.read('src/distribution/manifest.yaml').data, 'tiny')
                manifest['components'][0]['members'].append(
                    {'source': extra, 'destination': '.ai/core/skills/alpha/' + extra})
                source.blobs['src/distribution/manifest.yaml'] = blob('src/distribution/manifest.yaml', manifest)
                with self.assertRaisesRegex(DistributionError, 'collision|traversal'):
                    select(source, 'tiny')

    def test_c3_real_git_regular_missing_nonregular_members(self):
        run = support.active_run()
        case = run.case('git-members')
        repository = case / 'repository'
        empty = case / 'empty-template'
        empty.mkdir()
        support.git('-c', 'init.defaultBranch=fixture', 'init', '--template=' + str(empty), str(repository))
        oid = support.git('hash-object', '-w', '--stdin', cwd=repository, input=b'tiny\n').decode().strip()
        tree = support.git('mktree', cwd=repository, input=(
            f'100755 blob {oid}\tregular\n120000 blob {oid}\tlink\n').encode()).decode().strip()
        root_tree = support.git('mktree', cwd=repository, input=f'040000 tree {tree}\tsrc\n'.encode()).decode().strip()
        commit = support.git('-c', 'user.name=Fixture', '-c', 'user.email=fixture@example.invalid',
                             'commit-tree', root_tree, cwd=repository, input=b'Synthetic member fixture\n').decode().strip()
        source = GitSource(repository, commit)
        self.assertEqual((source.read('src/regular').mode, source.read('src/regular').data), ('100755', b'tiny\n'))
        with self.assertRaisesRegex(DistributionError, 'missing exact Git member'):
            source.read('src/missing')
        with self.assertRaisesRegex(DistributionError, 'only regular Git blobs'):
            source.read('src/link')
        # Actual Git tree/link modes; no native OS symlink or installation probe.
        run.measure()


class CandidateTests(unittest.TestCase):
    def test_c5_two_real_lesson_builds_and_reader_refusals(self):
        run = support.active_run()
        root = run.case('lesson-candidates')
        commit, _, source = actual_source()
        first = assembly.assemble(support.REPOSITORY, commit, 'lesson-minimal', root, root)
        run.measure()
        time.sleep(1.05)  # Completion timestamps have second precision; one bounded difference.
        second = assembly.assemble(support.REPOSITORY, commit, 'lesson-minimal', root, root)
        run.measure()
        a, b = Path(first['candidate_root']), Path(second['candidate_root'])
        left, right = installation_state.read_candidate(str(a)), installation_state.read_candidate(str(b))
        self.assertEqual(left.identity, right.identity)
        self.assertEqual(left.selection, right.selection)
        self.assertEqual(left.inventory, right.inventory)
        self.assertNotEqual(left.build['run_id'], right.build['run_id'])
        self.assertNotEqual(left.build['completed_at'], right.build['completed_at'])
        self.assertEqual(sum(p.is_file() for p in a.rglob('*')), 13)
        self.assertEqual({p.relative_to(a).as_posix() for p in a.rglob('*') if p.is_file()},
                         set(installation_state.METADATA) | {m.candidate_path for m in select(source, 'lesson-minimal').members})
        expected = select(source, 'lesson-minimal')
        for member in expected.members:
            with self.subTest(member=member.destination):
                self.assertEqual(left.contents[member.destination], member.data)
                descriptor = left.members[member.destination]
                self.assertEqual(descriptor['mode'], member.mode)
                self.assertEqual(descriptor['size'], len(member.data))
                self.assertEqual(descriptor['sha256'], sha256(member.data).hexdigest())
        payload = a / 'payload/.ai/core/skills/lesson/SKILL.md'
        completion = a / 'metadata/build.json'
        inventory = a / 'metadata/files.json'

        @contextmanager
        def replaced(target, raw):
            original = target.read_bytes()
            try:
                target.write_bytes(raw)
                yield
            finally:
                target.write_bytes(original)

        original = completion.read_bytes()
        completion.unlink()
        try:
            with self.assertRaises(installation_state.InstallationError) as caught:
                installation_state.read_candidate(str(a))
            self.assertEqual(caught.exception.diagnostic['code'], 'incomplete-candidate')
        finally:
            completion.write_bytes(original)
        with replaced(payload, b'X' + payload.read_bytes()[1:]):
            with self.assertRaises(installation_state.InstallationError) as caught:
                installation_state.read_candidate(str(a))
            self.assertEqual(caught.exception.diagnostic['code'], 'member-drift')
        document = json.loads(inventory.read_bytes())
        document['files'][0]['sha256'] = '0' * 64
        with replaced(inventory, json_bytes(document)):
            with self.assertRaises(installation_state.InstallationError):
                installation_state.read_candidate(str(a))
        extra = run.write(a / 'payload/unexpected.txt', b'undeclared\n')
        try:
            with self.assertRaises(installation_state.InstallationError) as caught:
                installation_state.read_candidate(str(a))
            self.assertEqual(caught.exception.diagnostic['code'], 'extra-candidate-file')
        finally:
            extra.unlink()
        original = payload.read_bytes()
        mode = payload.stat().st_mode
        payload.unlink()
        try:
            with self.assertRaises(installation_state.InstallationError) as caught:
                installation_state.read_candidate(str(a))
            self.assertEqual(caught.exception.diagnostic['code'], 'candidate-closure')
        finally:
            payload.write_bytes(original)
            payload.chmod(mode)
        self.assertEqual(installation_state.read_candidate(str(a)).identity, left.identity)
        print(json.dumps({'C5': {'assemblies': 2, 'files_per_candidate': 13, 'payload': 9,
                                'entries': 1, 'metadata': 3, 'synthetic_refusals': 5,
                                'candidate_identity': left.identity, 'native_apply': 'not-executed'}}))
        run.measure()


class FixtureSupportTests(unittest.TestCase):
    def test_output_root_precedence_default_and_rejection(self):
        run = support.active_run()
        case = run.case('root-precedence')
        explicit, env_root = case / 'explicit', case / 'environment'
        self.assertEqual(support.output_parent(explicit, {'FRAMEWORK_TEST_OUTPUT_ROOT': str(env_root)}), explicit)
        self.assertFalse(env_root.exists())
        self.assertEqual(support.output_parent(environment={'FRAMEWORK_TEST_OUTPUT_ROOT': str(env_root)}), env_root)
        # One tiny genuine OS-temp allocation; no drive detection or legacy reinterpretation.
        default = support.FixtureRun(environment={'AI_CONTEXT_TEST_TMP_ROOT': 'ignored-invalid'})
        try:
            self.assertEqual(default.parent, Path(tempfile.gettempdir()).resolve())
            default.write(default.root / 'tiny.txt', b'tiny\n')
        finally:
            print(json.dumps({'zero_config_probe': default.close(True)}))
        for invalid in ('', 'relative', str(case / '..' / 'escape'), str(support.REPOSITORY), str(case.anchor)):
            with self.subTest(root=invalid), self.assertRaises((support.FixtureError, OSError)):
                support.output_parent(invalid, {})
        occupied = run.write(case / 'file-root', b'not a directory')
        with self.assertRaises((support.FixtureError, OSError)):
            support.output_parent(occupied, {})

    def test_failed_run_preserves_owned_residue_and_rejects_identity_drift(self):
        case = support.active_run().case('cleanup-contract')
        child = support.FixtureRun(case, environment={})
        child.write(child.root / 'failure.txt', b'synthetic failure residue\n')
        observation = child.close(False)
        self.assertEqual(observation['residue'], str(child.root))
        self.assertTrue((child.root / 'failure.txt').exists())
        identity = child.identity
        child.identity = (-1, -1)  # labelled synthetic identity mismatch, no native rename probe
        try:
            with self.assertRaisesRegex(support.FixtureError, 'identity changed'):
                child.close(True)
        finally:
            child.identity = identity
        self.assertTrue(child.root.exists())
        print(json.dumps({'synthetic_cleanup_probe': child.close(True)}))
        self.assertTrue(case.exists())

    def test_reserved_and_unknown_runner_selections_fail_before_allocation(self):
        import run as runner
        examples = [[], ['--layer', 'unknown'], ['--layer', 'public'],
                    ['--layer', 'public', '--family', 'lesson'],
                    ['--layer', 'public', '--family', 'unknown'], ['--layer', 'native-windows'],
                    ['--layer', 'native-windows', '--native-root', str(support.active_run().root)],
                    ['--layer', 'contracts', '--family', 'lesson'],
                    ['--layer', 'contracts', '--native-root', str(support.active_run().root)]]
        for argv in examples:
            with self.subTest(argv=argv), redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as caught:
                runner.arguments(argv)
            self.assertEqual(caught.exception.code, 2)
        args = runner.arguments(['--layer', 'contracts', '--case', 'MetadataTests.test_c2_minimal_synthetic_v1'])
        self.assertEqual(args.case, ['MetadataTests.test_c2_minimal_synthetic_v1'])
