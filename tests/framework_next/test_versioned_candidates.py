"""Issue 381: bounded versioned selection tests and an explicit complete CLI run.

regressions: tiny synthetic source/locks/future stable metadata; actual readers.
fixture-plan: those fixtures through the real pinned public read-only planner.
complete: one real complete 0.19.0-rc.1 CLI assembly/read from clean committed source.
All modes retain their unique evidence directory; never install/apply/recover.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
from datetime import datetime, timezone
from hashlib import sha1, sha256
import json
import os
from pathlib import Path
import stat
import sys
import time
import unittest
from unittest.mock import patch
import uuid

HERE = Path(__file__).absolute().parent
sys.dont_write_bytecode = True
sys.path[:0] = [str(HERE), str(HERE.parents[1] / 'src')]
import support
from distribution import assembly, installation_plan as planning, installation_state as state
from distribution.data import DistributionError, distribution_version, json_bytes, version, yaml_object
from distribution.git_source import Blob, GitSource
from distribution.selection import select

COMPONENTS = {
    'lesson': '0.2.0', 'adr': '0.1.0', 'standards-promotion': '0.1.0',
    'pr': '0.1.0', 'local-backlog': '0.1.0', 'software-development-orchestrator': '0.1.0',
    'code-reviewer': '0.1.0', 'requirement-author': '0.1.0', 'spec-author': '0.1.0',
    'diagnostic-analyst': '0.1.0', 'ddd-ca-hex-architect': '0.1.0',
    'bdd-gwt-test-designer': '0.1.0', 'local-change-implementer': '0.1.0',
    'slice-implementer': '0.1.0', 'problem-frame-author': '0.1.0',
    'spec-compliance-validator': '0.1.0', 'ai-context-auditor': '0.1.0',
    'ai-context-governance': '0.1.0',
}
RUN = None


class SyntheticSource:
    """Tiny fictional Git transport. It is never source provenance evidence."""
    def __init__(self):
        self.commit, self.tree = '1' * 40, '2' * 40
        self.repository = support.REPOSITORY
        info = self.repository.stat()
        self.repository_identity = info.st_dev, info.st_ino
        metadata = {'metadata_version': 3, 'id': 'tiny', 'version': '0.1.0',
                    'delivery_status': 'implemented', 'entrypoint': 'SKILL.md',
                    'dependencies': {'required': [], 'optional': []},
                    'runtime': [{'id': 'skill-instruction-reader', 'requirement': 'Read text',
                                 'for_operations': ['review'], 'on_missing': 'unavailable'}],
                    'configuration': None, 'artifact_roles': [],
                    'resources': {'references': ['review.md'], 'schemas': [], 'templates': [], 'tools': []},
                    'operations': [{'id': 'review', 'execution': 'instruction', 'inputs': ['text'],
                                    'outputs': ['prose'], 'instructions': 'review.md',
                                    'implementation_status': 'implemented'}]}
        members = ['SKILL.md', 'skill-package.yaml', 'review.md']
        documents = {
            'src/distribution/data.py': b'# Synthetic generator fixture.\n',
            'src/distribution/manifest.yaml': {'manifest_version': 1,
                'profiles': [{'id': 'tiny', 'path': 'src/profiles/tiny.yaml'}], 'adapters': [],
                'components': [{'id': 'tiny', 'source': 'src/skills/tiny', 'metadata': 'skill-package.yaml',
                                'members': [{'source': name, 'destination': '.ai/core/skills/tiny/' + name} for name in members]}]},
            'src/profiles/tiny.yaml': {'profile_version': 1, 'id': 'tiny', 'skills': [{'id': 'tiny', 'version': '0.1.0'}], 'adapters': []},
            'src/skills/tiny/skill-package.yaml': metadata,
            'src/skills/tiny/SKILL.md': b'---\nname: tiny\ndescription: Synthetic instruction fixture\n---\n[Review](review.md)\n',
            'src/skills/tiny/review.md': b'Synthetic instruction fixture.\n',
        }
        self.blobs = {}
        for name, value in documents.items():
            raw = value if type(value) is bytes else json_bytes(value)
            digest = sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
            self.blobs[name] = Blob(name, digest, '100644', raw)

    def read(self, name):
        return self.blobs[name]


def fixture_candidate(parent, release=None):
    source = SyntheticSource()
    implementation = [{'source': source.read('src/distribution/data.py').identity(),
                       'execution_file_sha256': '3' * 64}]
    with patch.object(assembly, 'GitSource', return_value=source), \
            patch.object(assembly, 'implementation_identity', return_value=implementation):
        if release is None:
            built = assembly.assemble(source.repository, source.commit, 'tiny', parent, parent)
        else:
            built = assembly.assemble_versioned(source.repository, source.commit, 'tiny', parent, parent,
                                               release_version=release)
    return state.read_candidate(built['candidate_root'])


def fixture_engine():
    return {'id': 'framework-managed-installation', 'version': '1.0.0',
            'source_commit': '4' * 40, 'files': [{'path': 'src/distribution/data.py', 'sha256': '5' * 64}]}


def fixture_lock(candidate, engine=None):
    """Manually constructed fixture: never evidence of apply or a target install."""
    return {'lock_version': 1, 'installation_id': '6' * 32, 'engine': engine or fixture_engine(),
            'mode_policy': 'windows-inventory-only' if os.name == 'nt' else 'posix-permissions',
            'candidate_identity': candidate.identity, 'selection': deepcopy(candidate.selection),
            'inventory': deepcopy(candidate.inventory)}


def rebind(documents):
    """Fixture metadata with an independently calculated expected identity."""
    selection, inventory = documents[state.METADATA[0]], documents[state.METADATA[1]]
    hashes = {state.METADATA[0]: sha256(json_bytes(selection)).hexdigest(),
              state.METADATA[1]: sha256(json_bytes(inventory)).hexdigest()}
    digest = sha256(json_bytes(hashes)).hexdigest()
    prefix = 'development' if selection['mode'] == 'development' else 'versioned:' + str(selection['release_version'])
    build = documents[state.METADATA[2]]
    build.update(candidate_identity=prefix + ':' + selection['source']['commit'] + ':' + digest,
                 candidate_sha256=digest, identity_inputs=hashes, source_commit=selection['source']['commit'])
    return {name: json_bytes(value) for name, value in documents.items()}


class VersionedTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        parent = RUN.case('tiny-candidates')
        cls.development = fixture_candidate(parent)
        cls.rc = fixture_candidate(parent, '0.19.0-rc.1')
        cls.stable = fixture_candidate(parent, '0.19.0')  # fictional future stable, unpublished

    def test_strict_distribution_grammar_and_unchanged_component_grammar(self):
        for value in ('0.0.0', '0.19.0', '12.34.56', '0.19.0-rc.1', '12.34.56-rc.12'):
            self.assertEqual(distribution_version(value, 'fixture'), value)
        for value in (None, True, False, 1, 1.0, [], {}, '', ' ', '0.19', 'v0.19.0',
                      '00.19.0', '0.019.0', '0.19.00', '0.19.0-rc.0', '0.19.0-rc.01',
                      '0.19.0-rc.-1', '0.19.0-rc.1.0', '0.19.0-RC.1', '0.19.0-beta.1',
                      '0.19.0+build', '0.19.0-rc.1+build', ' 0.19.0', '0.19.0\n', '１.19.0'):
            with self.subTest(value=value), self.assertRaises(DistributionError):
                distribution_version(value, 'fixture')
        with self.assertRaises(DistributionError):
            version('0.19.0-rc.1', 'component')
        self.assertEqual(version('0.2.0', 'component'), '0.2.0')

    def test_versioned_api_requires_version_before_source_or_output(self):
        with patch.object(assembly, 'GitSource', side_effect=AssertionError('premature source')):
            for value in (None, '', True, 0.19, '0.19.0-rc.0'):
                with self.subTest(value=value), self.assertRaises(DistributionError):
                    assembly.assemble_versioned(Path('unused'), 'unused', 'tiny', Path('unused'), Path('unused'), release_version=value)
            with self.assertRaises(TypeError):
                assembly.assemble_versioned(Path('unused'), 'unused', 'tiny', Path('unused'), Path('unused'))

    def test_legacy_and_versioned_identity_exact_metadata_binding(self):
        for candidate, schema, mode, release, generator in (
                (self.development, 1, 'development', None, 'framework-development-assembly'),
                (self.rc, 2, 'versioned', '0.19.0-rc.1', 'framework-versioned-assembly'),
                (self.stable, 2, 'versioned', '0.19.0', 'framework-versioned-assembly')):
            with self.subTest(mode=mode, release=release):
                selection = candidate.selection
                self.assertEqual((selection['schema_version'], selection['mode'], selection['release_version'], selection['generator']['id']),
                                 (schema, mode, release, generator))
                self.assertEqual(selection['components'][0]['version'], '0.1.0')
                documents = {name: json.loads(raw) for name, raw in candidate.metadata_bytes.items()}
                self.assertEqual(rebind(documents)[state.METADATA[2]], candidate.metadata_bytes[state.METADATA[2]])
                self.assertEqual(candidate.build['publication'], 'not-performed')
                # Recovery imports this exact parser; this is retained-object reader evidence only.
                self.assertEqual(state._candidate_documents(candidate.metadata_bytes)[-1], candidate.identity)
        self.assertNotEqual(self.rc.identity, self.stable.identity)
        self.assertNotEqual(self.development.identity, self.rc.identity)

    def test_closed_schema_mode_version_generator_rules_shared_with_lock(self):
        cases = [('schema_version', value) for value in (0, 3, True, 2.0, '2', None)]
        cases += [('release_version', value) for value in (None, '', True, 0.19, '0.19.0-rc.0', '0.19.0+build')]
        cases += [('mode', 'development'), ('mode', 'release'), ('unknown', 'field')]
        for key, value in cases:
            documents = {name: json.loads(raw) for name, raw in self.rc.metadata_bytes.items()}
            documents[state.METADATA[0]][key] = value
            with self.subTest(key=key, value=value), self.assertRaises(state.InstallationError):
                state._candidate_documents({name: json_bytes(value) for name, value in documents.items()})
            lock = fixture_lock(self.rc)
            lock['selection'][key] = value
            with self.subTest(lock_key=key, value=value), self.assertRaises(state.InstallationError):
                state._lock_bytes(json_bytes(lock))
        for candidate, generator in ((self.rc, 'framework-development-assembly'), (self.development, 'framework-versioned-assembly')):
            documents = {name: json.loads(raw) for name, raw in candidate.metadata_bytes.items()}
            documents[state.METADATA[0]]['generator']['id'] = generator
            with self.assertRaises(state.InstallationError) as caught:
                state._candidate_documents(rebind(documents))
            self.assertEqual(caught.exception.outcome, 'unsupported')
            self.assertEqual(caught.exception.diagnostic['code'], 'unsupported-generator')
        for key, value in (('schema_version', 2), ('mode', 'versioned'), ('release_version', '0.19.0')):
            lock = fixture_lock(self.development)
            lock['selection'][key] = value
            with self.assertRaises(state.InstallationError):
                state._lock_bytes(json_bytes(lock))

    def test_mismatched_identity_version_commit_digest_and_noncanonical_bytes(self):
        for key, value in (('release_version', '0.19.0'), ('source', {'commit': '9' * 40, 'tree': '2' * 40}), ('profile', 'other')):
            documents = {name: json.loads(raw) for name, raw in self.rc.metadata_bytes.items()}
            documents[state.METADATA[0]][key] = value
            with self.subTest(key=key), self.assertRaises(state.InstallationError):
                state._candidate_documents({name: json_bytes(value) for name, value in documents.items()})
            lock = fixture_lock(self.rc)
            lock['selection'][key] = value
            with self.assertRaises(state.InstallationError):
                state._lock_bytes(json_bytes(lock))
        for key, value in (('candidate_identity', self.stable.identity), ('candidate_sha256', '0' * 64),
                           ('identity_inputs', {}), ('source_commit', '9' * 40), ('publication', 'published')):
            documents = {name: json.loads(raw) for name, raw in self.rc.metadata_bytes.items()}
            documents[state.METADATA[2]][key] = value
            with self.subTest(key=key), self.assertRaises(state.InstallationError):
                state._candidate_documents({name: json_bytes(value) for name, value in documents.items()})
        raw = dict(self.rc.metadata_bytes)
        raw[state.METADATA[0]] = json.dumps(self.rc.selection).encode()
        with self.assertRaises(state.InstallationError) as caught:
            state._candidate_documents(raw)
        self.assertEqual(caught.exception.diagnostic['code'], 'noncanonical-document')

    def test_fixture_lock_readback_and_same_schema_stable_plan_semantics(self):
        root = RUN.case('manual-lock-fixture')
        (root / '.ai').mkdir()
        document = fixture_lock(self.rc)
        raw = json_bytes(document)
        (root / state.LOCK_PATH).write_bytes(raw)
        lock = state.read_lock(str(root))
        self.assertEqual(lock.raw, raw)
        self.assertEqual(lock.sha256, sha256(raw).hexdigest())
        self.assertEqual(lock.document['candidate_identity'], self.rc.identity)
        observation = state.Observation(root, lock, [], [], [])
        self.assertTrue(planning.is_noop(observation, self.rc, document['mode_policy']))
        self.assertFalse(planning.is_noop(observation, self.stable, document['mode_policy']))
        self.assertEqual({row['action'] for row in planning.member_delta(lock, self.stable)}, {'unchanged'})
        document['candidate_identity'] = self.stable.identity
        (root / state.LOCK_PATH).write_bytes(json_bytes(document))
        with self.assertRaises(state.InstallationError) as caught:
            state.read_lock(str(root))
        self.assertEqual(caught.exception.diagnostic['code'], 'lock-identity')


def pinned_fixture_plan(run):
    """Actual read-only public API against fictional installed/stable fixtures."""
    support.check(not support.git('status', '--porcelain').strip(), 'fixture plan requires clean committed engine')
    rc = fixture_candidate(run.case('rc-fixture'), '0.19.0-rc.1')
    stable = fixture_candidate(run.case('future-stable-fixture'), '0.19.0')
    roots = {role: run.case(role) for role in ('project-fixture', 'scratch', 'recovery')}
    project = roots['project-fixture']
    commit = support.git('rev-parse', 'HEAD').decode().strip()
    pin = {'id': 'framework-managed-installation', 'version': '1.0.0', 'source_commit': commit,
           'files': [{'path': name, 'sha256': sha256((support.REPOSITORY / name).read_bytes()).hexdigest()} for name in state.ENGINE_FILES]}
    for name, raw in rc.contents.items():
        target = project / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(raw)
        if os.name == 'posix':
            target.chmod(0o755 if rc.members[name]['mode'] == '100755' else 0o644)
    lock_raw = json_bytes(fixture_lock(rc, pin))
    (project / state.LOCK_PATH).write_bytes(lock_raw)
    request = {'api_version': 1, 'operation': 'plan', 'project_root': str(project),
               'engine_root': str(support.REPOSITORY), 'engine': pin,
               'candidate_root': str(stable.root), 'candidate_identity': stable.identity,
               'expected_lock_sha256': sha256(lock_raw).hexdigest(),
               'scratch_root': str(roots['scratch']), 'staging_root': str(roots['scratch']),
               'recovery_root': str(roots['recovery']), 'mode_policy': 'windows-inventory-only' if os.name == 'nt' else 'posix-permissions',
               'protected_inputs': [], 'project_data_action': 'none',
               'durability': {'declared_by': 'Issue 381 synthetic fixture', 'declaration_reference': 'synthetic:381', 'failure_domain': 'process-termination'}}
    before = {p.relative_to(project).as_posix(): p.read_bytes() for p in project.rglob('*') if p.is_file()}
    observations = []
    # These are different inputs testing distinct rules, never an unchanged retry.
    for label, override, outcome, code in (
            ('same-schema-stable-fixture', {}, 'planned', None),
            ('wrong-lock-fixture', {'expected_lock_sha256': '0' * 64}, 'conflict', 'lock-conflict'),
            ('wrong-candidate-fixture', {'candidate_identity': rc.identity}, 'conflict', 'candidate-selection'),
            ('wrong-engine-fixture', {'engine': {**pin, 'source_commit': '0' * 40}}, 'blocked', 'engine-head')):
        selected = {**request, **override}
        process = support.run_process([support.PYTHON, '-I', '-B', support.REPOSITORY / 'src/tools/maintain_framework.py'],
                                      cwd=support.REPOSITORY, input=json_bytes(selected))
        response = json.loads(process.stdout)
        (run.root / (label + '.json')).write_bytes(json_bytes({'evidence_kind': 'fictional rc lock and future stable fixture; actual read-only public planner',
            'request': selected, 'response': response, 'exit': process.returncode, 'stderr': process.stderr.decode()}))
        support.check(response['outcome'] == outcome, str(response))
        support.check(process.returncode == (0 if outcome == 'planned' else 1), 'unexpected public exit')
        if code:
            support.check(response['diagnostics'][0]['code'] == code, str(response))
        else:
            plan = response['plan']
            support.check(plan['engine'] == pin and plan['candidate_identity'] == stable.identity, 'plan pin mismatch')
            support.check(plan['expected_lock_sha256'] == sha256(lock_raw).hexdigest(), 'expected lock mismatch')
            support.check(sha256(json_bytes(plan)).hexdigest() == response['plan_sha256'], 'plan digest mismatch')
            support.check({row['action'] for row in plan['delta']} == {'unchanged'}, 'fixture should change selection identity only')
            status = {r['id']: r['status'] for r in plan['prerequisites']}
            support.check(status['lock-publication'] == 'satisfied' and status['writer-guard'] == 'pending', 'planning was treated as no-op/apply')
        observations.append({'case': label, 'outcome': outcome, 'expected_refusal': code})
    support.check(before == {p.relative_to(project).as_posix(): p.read_bytes() for p in project.rglob('*') if p.is_file()}, 'planner mutated fixture')
    support.check(all(not list(roots[role].iterdir()) for role in ('scratch', 'recovery')), 'planner allocated operation output')
    return {'evidence_kind': 'synthetic future stable and manually constructed rc lock; actual public read-only planner',
            'engine_source_commit': commit, 'observations': observations, 'installation_apply_recover': 'not-performed', 'publication': 'not-performed'}


def complete_cli(parent):
    """One selected complete build, capped at 512 files / 16 MiB incl. evidence."""
    parent = support.output_parent(parent)
    support.check(not support.git('status', '--porcelain').strip(), 'complete assembly requires clean committed source')
    commit = support.git('rev-parse', 'HEAD').decode().strip()
    source = GitSource(support.REPOSITORY, commit)
    expected = select(source, 'complete')
    support.check({p.id: p.version for p in expected.packages} == COMPONENTS, 'exact 18-component selection changed')
    payload = [m for m in expected.members if m.envelope == 'payload']
    runtime = [m for m in expected.members if m.envelope == 'runtime']
    support.check(len(payload) == 113 and len(runtime) == 18 and len(expected.members) == 131, 'exact member inventory changed')
    support.check(sum(len(m.data) for m in expected.members) * 2 < 4 * 1024 * 1024, 'payload preflight budget exceeded')
    run_root = parent / ('complete-' + uuid.uuid4().hex)
    run_root.mkdir()
    started = time.monotonic()
    success = False
    result = {'source_commit': commit, 'evidence_kind': 'actual complete public CLI assembly and installation reader',
              'started_at': datetime.now(timezone.utc).isoformat(), 'root': str(run_root)}
    try:
        argv = [support.PYTHON, '-I', '-B', support.REPOSITORY / 'tools/build-candidate.py',
                '--repository', support.REPOSITORY, '--commit', commit, '--profile', 'complete',
                '--release-version', '0.19.0-rc.1', '--output-root', run_root, '--scratch-root', run_root]
        process = support.run_process(argv, cwd=support.REPOSITORY, timeout=110)
        (run_root / 'cli.json').write_bytes(json_bytes({'argv': [str(a) for a in argv], 'exit': process.returncode,
            'stdout': process.stdout.decode(), 'stderr': process.stderr.decode()}))
        support.check(process.returncode == 0, process.stderr.decode())
        built = json.loads(process.stdout)
        candidate = state.read_candidate(built['candidate_root'])
        support.check(candidate.selection['schema_version'] == 2 and candidate.selection['mode'] == 'versioned'
                      and candidate.selection['release_version'] == '0.19.0-rc.1', 'wrong candidate selection')
        support.check(candidate.selection['source'] == {'commit': commit, 'tree': source.tree}, 'source identity mismatch')
        support.check({p['id']: p['version'] for p in candidate.selection['components']} == COMPONENTS, 'component identity mismatch')
        support.check(candidate.inventory == {'schema_version': 1, 'files': [m.identity() for m in expected.members]}, 'exact committed inventory differs')
        support.check(candidate.contents == {m.destination: m.data for m in expected.members}, 'actual reader bytes differ from committed selection')
        support.check(candidate.identity == built['candidate_identity'], 'CLI/reader identities differ')
        support.check(candidate.identity == 'versioned:0.19.0-rc.1:' + commit + ':' + candidate.build['candidate_sha256'], 'identity prefix differs')
        support.check(candidate.selection['generator']['id'] == 'framework-versioned-assembly', 'wrong generator')
        support.check(all(candidate.build[k] == 'not-performed' for k in ('installation', 'behavioral_validation', 'publication')), 'unexpected build claim')
        support.check(not support.git('status', '--porcelain').strip() and support.git('rev-parse', 'HEAD').decode().strip() == commit, 'source drift')
        result.update(candidate_identity=candidate.identity, candidate_root=str(candidate.root), scratch_root=built['scratch_root'],
                      component_versions=COMPONENTS, payload_members=113, runtime_entries=18,
                      metadata_sha256={name: sha256(raw).hexdigest() for name, raw in candidate.metadata_bytes.items()},
                      installation='not-performed', publication='not-performed')
        success = True
    except Exception as exc:
        result.update(failure_type=type(exc).__name__, failure_fingerprint=sha256(str(exc).encode()).hexdigest(), diagnostic=str(exc))
        raise
    finally:
        count = total = 0
        for item in run_root.rglob('*'):
            info = item.lstat()
            support.check(not stat.S_ISLNK(info.st_mode) and not getattr(info, 'st_file_attributes', 0) & 0x400, 'linked actual run residue')
            if stat.S_ISREG(info.st_mode):
                count += 1
                total += info.st_size
        result.update(outcome='passed' if success else 'failed', wall_seconds=round(time.monotonic() - started, 3),
                      finished_at=datetime.now(timezone.utc).isoformat(), retained_files_before_receipt=count,
                      retained_bytes_before_receipt=total, file_cap=512, retained_byte_cap=16 * 1024 * 1024)
        raw = json_bytes(result)
        support.check(count + 1 <= 512 and total + len(raw) <= 16 * 1024 * 1024, 'actual build/read cap exceeded; residue retained')
        (run_root / 'result.json').write_bytes(raw)
        print(json.dumps(result), flush=True)
    return 0


def main():
    global RUN
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--mode', required=True, choices=('regressions', 'fixture-plan', 'complete'))
    parser.add_argument('--output-root', type=Path, required=True)
    args = parser.parse_args()
    support.check(sys.flags.isolated and sys.dont_write_bytecode, 'invoke with -I -B')
    if args.mode == 'complete':
        return complete_cli(args.output_root)
    RUN = support.FixtureRun(args.output_root)
    success = False
    try:
        with support.use_run(RUN):
            print(json.dumps({'mode': args.mode, 'evidence_kind': 'tiny synthetic fixtures; no actual release or target upgrade',
                              'run_root': str(RUN.root), 'runtime': support.runtime_versions()}), flush=True)
            if args.mode == 'regressions':
                result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(VersionedTests))
                success = result.wasSuccessful() and not result.skipped
            else:
                result = pinned_fixture_plan(RUN)
                (RUN.root / 'result.json').write_bytes(json_bytes(result))
                print(json.dumps(result), flush=True)
                success = True
    finally:
        accounting = RUN.close(False)
        accounting.update(selected_checks_passed=success, retention='Issue 381 evidence, including failures')
        print(json.dumps({'accounting': accounting}), flush=True)
    return 0 if success else 1


if __name__ == '__main__':
    raise SystemExit(main())
