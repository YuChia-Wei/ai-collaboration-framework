"""Selected C1-C3/C5 contracts. Synthetic inputs are named explicitly."""
from __future__ import annotations

from contextlib import contextmanager, redirect_stderr
from copy import deepcopy
from functools import lru_cache
from hashlib import sha256
import io
import json
import os
from pathlib import Path
import posixpath
import re
import stat
import tempfile
import time
import unittest
from types import SimpleNamespace
from urllib.parse import unquote, urlsplit

from distribution import assembly, installation_state
from distribution.data import DistributionError, json_bytes, yaml_object
from distribution.git_source import Blob, GitSource, direct_directory
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
            'context-maintenance': (MAINTENANCE, 6),
            'complete': (KNOWLEDGE | WORK | ENGINEERING | MAINTENANCE, 113)}


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
                                'profiles': 8, 'physical_assembly_scope': 'separate C5; this observation is declarations only'}}))

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
        nested = repository / 'nested'
        nested.mkdir()
        with self.assertRaisesRegex(DistributionError, 'worktree root'):
            GitSource(nested, commit)
        with self.assertRaisesRegex(DistributionError, 'traversal'):
            GitSource(repository / '..' / repository.name, commit)
        self.assertEqual((source.read('src/regular').mode, source.read('src/regular').data), ('100755', b'tiny\n'))
        with self.assertRaisesRegex(DistributionError, 'missing exact Git member'):
            source.read('src/missing')
        with self.assertRaisesRegex(DistributionError, 'only regular Git blobs'):
            source.read('src/link')
        # Actual Git tree/link modes; no native OS symlink or installation probe.
        run.measure()


class PathAdmissionTests(unittest.TestCase):
    def test_existing_direct_directory_and_invalid_roots(self):
        run = support.active_run()
        case = run.case('path-admission')
        self.assertEqual(direct_directory(case, 'fixture'), case)
        for value in [Path('relative'), case / '..' / 'escape']:
            with self.subTest(value=str(value)), self.assertRaises(DistributionError):
                direct_directory(value, 'fixture')
        with self.assertRaises(FileNotFoundError):
            direct_directory(case / 'missing', 'fixture')
        ordinary = run.write(case / 'ordinary-file', b'not a directory')
        with self.assertRaisesRegex(DistributionError, 'direct directory'):
            direct_directory(ordinary, 'fixture')
        if os.name == 'nt':
            for name in ['alias~1', 'trailing.', 'trailing ', 'NUL.txt', 'stream:ads']:
                with self.subTest(name=name), self.assertRaisesRegex(DistributionError, 'ambiguous'):
                    direct_directory(case / name, 'fixture')

    def test_synthetic_link_identity_and_error_refusals(self):
        # Local path doubles exercise admission branches, not native links/syscalls.
        # No global Path/OS monkeypatch; actual filesystem evidence is separate.
        case = support.active_run().case('synthetic-path-errors')

        class View:
            def __init__(self, *, mode=stat.S_IFDIR, attributes=0, inode=17,
                         winerror=1, drift=False, parents=None):
                self.parts = case.parts
                self.parents = case.parents if parents is None else parents
                self.mode, self.attributes, self.inode = mode, attributes, inode
                self.winerror, self.drift, self.calls = winerror, drift, 0

            def __str__(self):
                return str(case)

            def __fspath__(self):
                return str(case)

            def is_absolute(self):
                return True

            def lstat(self):
                self.calls += 1
                return SimpleNamespace(st_mode=self.mode, st_file_attributes=self.attributes,
                                       st_dev=9, st_ino=self.inode + (self.calls if self.drift else 0))

            def resolve(self, *, strict):
                error = OSError('synthetic final-path failure')
                error.winerror = self.winerror
                raise error

        for view in [View(mode=stat.S_IFLNK), View(attributes=stat.FILE_ATTRIBUTE_REPARSE_POINT),
                     View(parents=(View(attributes=stat.FILE_ATTRIBUTE_REPARSE_POINT),))]:
            with self.subTest(kind=(view.mode, view.attributes)), self.assertRaisesRegex(DistributionError, 'links/reparse'):
                direct_directory(view, 'synthetic')
        for code in [2, 5, 50]:
            with self.subTest(error=code), self.assertRaises(OSError) as caught:
                direct_directory(View(winerror=code), 'synthetic')
            self.assertEqual(caught.exception.winerror, code)
        if os.name == 'nt':
            self.assertEqual(direct_directory(View(), 'synthetic'), case)
            with self.assertRaisesRegex(DistributionError, 'usable filesystem identities'):
                direct_directory(View(inode=0), 'synthetic')
            with self.assertRaisesRegex(DistributionError, 'identity changed'):
                direct_directory(View(drift=True), 'synthetic')
        else:
            with self.assertRaises(OSError):
                direct_directory(View(), 'synthetic')

    def test_output_containment_and_synthetic_source_alias_identity(self):
        case = support.active_run().case('output-containment')
        info = support.REPOSITORY.lstat()
        source = SimpleNamespace(repository=support.REPOSITORY,
                                 repository_identity=(info.st_dev, info.st_ino))
        with self.assertRaisesRegex(DistributionError, 'outside the source worktree'):
            assembly.output_parent(support.REPOSITORY / 'src', source, 'output-root')
        self.assertEqual(assembly.output_parent(case, source, 'output-root'), case)
        # Synthetic source identity simulates a second spelling for an ancestor.
        info = case.parent.lstat()
        source.repository_identity = (info.st_dev, info.st_ino)
        with self.assertRaisesRegex(DistributionError, 'source worktree aliases'):
            assembly.output_parent(case, source, 'output-root')


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
        expected = select(source, 'lesson-minimal')
        emitted = {}
        for candidate in (a, b):
            names = {p.relative_to(candidate).as_posix() for p in candidate.rglob('*') if p.is_file()}
            self.assertEqual(names, set(installation_state.METADATA) | {m.candidate_path for m in expected.members})
            self.assertEqual(len(names), 13)
            for member in expected.members:
                self.assertEqual((candidate / member.candidate_path).read_bytes(), member.data)
            emitted[candidate] = {name: (candidate / name).read_bytes() for name in installation_state.METADATA}
            files = json.loads(emitted[candidate]['metadata/files.json'])
            self.assertEqual(files['files'], [m.identity() for m in expected.members])
        for name in ['metadata/selection.json', 'metadata/files.json']:
            self.assertEqual(emitted[a][name], emitted[b][name])
        builds = [json.loads(emitted[p]['metadata/build.json']) for p in (a, b)]
        identity_inputs = {name: sha256(emitted[a][name]).hexdigest()
                           for name in ['metadata/selection.json', 'metadata/files.json']}
        expected_identity = f'development:{commit}:' + sha256(json_bytes(identity_inputs)).hexdigest()
        for build in builds:
            self.assertEqual(build['candidate_identity'], expected_identity)
            self.assertEqual(build['identity_inputs'], identity_inputs)
        self.assertNotEqual(builds[0]['run_id'], builds[1]['run_id'])
        self.assertNotEqual(builds[0]['completed_at'], builds[1]['completed_at'])
        print(json.dumps({'C5_assembly': {'source_commit': commit, 'actual_builds': 2,
                                        'files_per_candidate': 13, 'candidate_identity': expected_identity,
                                        'candidate_roots': [str(a), str(b)],
                                        'reader_status': 'next; not yet accepted'}}), flush=True)
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
    def test_readonly_git_object_cleanup(self):
        case = support.active_run().case('readonly-git-cleanup')
        child = support.FixtureRun(case, environment={})
        with support.use_run(child):
            repo = child.case('tiny-git')
            support.git('init', '--bare', '--template=', str(repo))
            oid = support.git('hash-object', '-w', '--stdin', cwd=repo,
                              input=b'tiny readonly Git fixture\n').decode().strip()
            loose = repo / 'objects' / oid[:2] / oid[2:]
            info = loose.lstat()
            self.assertTrue(stat.S_ISREG(info.st_mode))
            self.assertEqual(info.st_nlink, 1)
            if os.name == 'nt':
                self.assertTrue(info.st_file_attributes & stat.FILE_ATTRIBUTE_READONLY)
            measured = child.measure()
            observed = child.close(True)
        self.assertTrue(child.closed)
        self.assertFalse(child.root.exists())
        self.assertTrue(case.is_dir())
        for key in ('processes', 'process_total', 'retained_files', 'retained_bytes'):
            self.assertEqual(observed[key], measured[key])
        self.assertEqual(observed['processes'], {'git': 2, 'python': 0, 'other': 0})
        print(json.dumps({'actual_readonly_git_cleanup': observed}, sort_keys=True))

    def test_readonly_cleanup_refusals_preserve_accounting(self):
        from unittest.mock import patch
        case = support.active_run().case('readonly-refusals')
        child = support.FixtureRun(case, environment={})
        nested = child.case('nested')
        target = child.write(nested / 'tiny.txt', b'owned readonly refusal fixture\n')
        outside = support.active_run().write(case / 'outside.txt', b'outside child; preserve\n')
        os.chmod(target, target.lstat().st_mode & ~stat.S_IWRITE)
        real_lstat = Path.lstat
        actual = real_lstat(target)
        original_identity = child.identity
        modes = ('outside', 'traversal', 'unknown', 'file-identity', 'ancestor-identity',
                 'root-identity', 'symlink', 'reparse', 'ancestor-reparse', 'nonregular',
                 'hardlink', 'writable', 'attribute-drift', 'unknown-error', 'unknown-operation',
                 'post-chmod-drift', 'retry-failure')
        for mode in modes:
            with self.subTest(synthetic_guard=mode):
                prior = child.measure()
                error = PermissionError('synthetic Windows unlink access denial')
                error.winerror = 5
                chmod_calls = []
                unlink_calls = []

                def baseline_lstat(path, *args, **kwargs):
                    info = real_lstat(path, *args, **kwargs)
                    if path != target or hasattr(info, 'st_file_attributes'):
                        return info
                    # Windows attribute semantics are synthetic on other hosts.
                    return SimpleNamespace(**{name: getattr(info, name) for name in
                        ('st_dev', 'st_ino', 'st_mode', 'st_nlink', 'st_size', 'st_mtime_ns')},
                        st_file_attributes=stat.FILE_ATTRIBUTE_READONLY)

                def simulated_lstat(path, *args, **kwargs):
                    info = baseline_lstat(path, *args, **kwargs)
                    fields = {name: getattr(info, name) for name in
                              ('st_dev', 'st_ino', 'st_mode', 'st_nlink', 'st_size', 'st_mtime_ns')}
                    fields['st_file_attributes'] = getattr(info, 'st_file_attributes', 0)
                    if path == target:
                        fields['st_file_attributes'] |= stat.FILE_ATTRIBUTE_READONLY
                        if mode == 'file-identity' or (mode == 'post-chmod-drift' and chmod_calls):
                            fields['st_ino'] = -1
                        elif mode == 'symlink':
                            fields['st_mode'] = stat.S_IFLNK | stat.S_IREAD
                        elif mode == 'reparse':
                            fields['st_file_attributes'] |= stat.FILE_ATTRIBUTE_REPARSE_POINT
                        elif mode == 'nonregular':
                            fields['st_mode'] = stat.S_IFDIR | stat.S_IREAD
                        elif mode == 'hardlink':
                            fields['st_nlink'] = 2
                        elif mode == 'writable':
                            fields['st_file_attributes'] &= ~stat.FILE_ATTRIBUTE_READONLY
                        elif mode == 'attribute-drift':
                            fields['st_file_attributes'] ^= stat.FILE_ATTRIBUTE_HIDDEN
                        elif mode == 'retry-failure' and chmod_calls:
                            fields['st_file_attributes'] = (fields['st_file_attributes'] &
                                ~stat.FILE_ATTRIBUTE_READONLY) or stat.FILE_ATTRIBUTE_NORMAL
                    if path == nested and mode == 'ancestor-identity':
                        fields['st_ino'] = -1
                    if path == nested and mode == 'ancestor-reparse':
                        fields['st_file_attributes'] |= stat.FILE_ATTRIBUTE_REPARSE_POINT
                    return SimpleNamespace(**fields)

                def failed_unlink(*args):
                    unlink_calls.append(args)
                    raise PermissionError('synthetic one-retry failure')

                def synthetic_rmtree(root, *, onerror):
                    self.assertEqual(root, child.root)
                    path = outside if mode == 'outside' else target
                    if mode == 'traversal':
                        path = nested / '..' / 'nested' / target.name
                    if mode == 'unknown':
                        path = child.write(child.root / 'late.txt', b'not in cleanup snapshot')
                    if mode == 'root-identity':
                        child.identity = (-1, -1)
                    if mode == 'unknown-error':
                        error.winerror = 32
                    with patch.object(Path, 'lstat', simulated_lstat), \
                         patch.object(support.os, 'chmod', side_effect=lambda *a: chmod_calls.append(a)), \
                         patch.object(support.os, 'unlink', side_effect=failed_unlink):
                        operation = os.rmdir if mode == 'unknown-operation' else os.unlink
                        onerror(operation, str(path), (type(error), error, None))

                try:
                    with patch.object(Path, 'lstat', baseline_lstat), \
                         patch.object(support.shutil, 'rmtree', synthetic_rmtree), \
                         self.assertRaises(support.FixtureCleanupError) as caught:
                        child.close(True)
                finally:
                    child.identity = original_identity
                observed = caught.exception.accounting
                for key in ('observed_files', 'observed_logical_bytes', 'retained_files',
                            'retained_bytes', 'authored_bytes', 'processes', 'process_total'):
                    self.assertEqual(observed[key], prior[key])
                self.assertEqual(observed['measurement_phase'], 'before-cleanup')
                self.assertEqual(observed['residue'], str(child.root))
                self.assertGreaterEqual(observed['wall_seconds'], prior['wall_seconds'])
                self.assertFalse(child.closed)
                self.assertEqual(len(chmod_calls), 1 if mode in ('post-chmod-drift', 'retry-failure') else 0)
                self.assertEqual(len(unlink_calls), 1 if mode == 'retry-failure' else 0)
                self.assertEqual(target.read_bytes(), b'owned readonly refusal fixture\n')
                self.assertEqual(outside.read_bytes(), b'outside child; preserve\n')
                self.assertEqual(real_lstat(target).st_mode, actual.st_mode)
        print(json.dumps({'synthetic_readonly_refusal_modes': list(modes),
                          'fixture_accounting': child.close(True)}, sort_keys=True))

    def test_cleanup_failure_accounting_in_contracts_and_public_reports(self):
        from contextlib import redirect_stdout
        from unittest.mock import patch
        import run as runner
        case = support.active_run().case('cleanup-reporting')

        class SyntheticPublicCase(unittest.TestCase):
            complete = True
            blocked_before_write = False

            def test_selected(self):
                pass

            def observation(self):
                return {'synthetic_reporting_only': True, 'public_launches': 0,
                        'nested_launch_upper_bound': 0}

        result = SimpleNamespace(testsRun=1, wasSuccessful=lambda: True, skipped=[])
        for layer in ('contracts', 'public'):
            child = support.FixtureRun(case, environment={})
            child.write(child.root / 'tiny.txt', b'preserve accounting\n')
            deleted = child.write(child.root / 'deleted.txt', b'measured before deletion\n')
            before = child.measure()

            def partial_cleanup(root, **kwargs):
                child.verify()
                self.assertEqual(root, child.root)
                support.direct_directory(deleted.parent)
                deleted.unlink()
                raise PermissionError('synthetic failure after one deletion')

            stdout, stderr = io.StringIO(), io.StringIO()
            argv = ['--layer', layer, '--output-root', str(case)]
            argv += (['--case', 'FixtureSupportTests.test_readonly_git_object_cleanup'] if layer == 'contracts'
                     else ['--family', 'pr', '--public-read-only'])
            # Both dispatch branches are synthetic report plumbing only: no suite,
            # public entry, Git fixture, provider or product operation runs here.
            with patch.object(support, 'FixtureRun', return_value=child), \
                 patch.object(support.shutil, 'rmtree', side_effect=partial_cleanup), \
                 patch.object(runner.unittest.TextTestRunner, 'run', return_value=result), \
                 patch.dict(runner.sys.modules, {'test_work': SimpleNamespace(PrTests=SyntheticPublicCase)}), \
                 redirect_stdout(stdout), redirect_stderr(stderr):
                if layer == 'contracts':
                    with self.assertRaises(SystemExit) as caught:
                        runner.main(argv)
                    self.assertEqual(caught.exception.code, 2)
                else:
                    self.assertEqual(runner.main(argv), 2)
            records = [json.loads(line) for line in stdout.getvalue().splitlines()]
            if layer == 'contracts':
                accounting = next(row['fixture_accounting'] for row in records if 'fixture_accounting' in row)
                self.assertEqual(json.loads(stderr.getvalue())['outcome'], 'cleanup-failed')
            else:
                family = next(row['public_family'] for row in records if 'public_family' in row)
                self.assertEqual((family['outcome'], family['exit']), ('cleanup-failed', 2))
                accounting = family['fixture_accounting']
                self.assertEqual(records[-1]['outcome'], 'not-passed')
            for key in ('observed_files', 'observed_logical_bytes', 'retained_files', 'retained_bytes',
                        'authored_bytes', 'processes', 'process_total'):
                self.assertEqual(accounting[key], before[key])
            self.assertEqual(accounting['residue'], str(child.root))
            self.assertEqual(accounting['measurement_phase'], 'before-cleanup')
            self.assertGreaterEqual(accounting['wall_seconds'], before['wall_seconds'])
            self.assertTrue(child.root.exists())
            self.assertFalse(deleted.exists())
            self.assertEqual(accounting['retained_files'], 2)
            self.assertEqual(child.measure()['retained_files'], 1)
            print(json.dumps({'synthetic_cleanup_report': layer, 'exit': 2,
                              'fixture_accounting': accounting}, sort_keys=True))
            child.close(True)

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
