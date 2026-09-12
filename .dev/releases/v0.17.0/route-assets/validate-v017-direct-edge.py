#!/usr/bin/env python3
"""Verify one retained direct route against admitted v0.17 bytes and actual cases."""
import argparse
import hashlib
import importlib
import importlib.util
import os
import json
import sys
import tempfile
import zipfile
from pathlib import Path, PurePosixPath

sys.dont_write_bytecode = True
EXPECTED_ARCHIVE = 'b9e6b38515e8ac82731734b99bacb97b40ca0c7ad543d2b6f84390b4cdb94a22'
EXPECTED_ACTUAL = '21fa2f3d67f194994fc8ee1fcb314bd59727e4fc775ef1a88057f68155738e62'
ORIGINS = {'v0.16.0': '41fc410bde7a2745bed1663eb28d89ce5a5e6672b15fa95db82e7089c2972ab4', 'v0.9.0': 'c293247612eb2f01ef42e4d7c55be4ff36201cdf034157c518de871ec2acb5c7', 'v0.6.0': '20ca69ef4e1b4085476a2b15eeba93da7a75ea580fd2ab9f6c8815938b0af3be'}

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def require(condition, reason):
    if not condition:
        raise ValueError(reason)

def asset(value):
    pure = PurePosixPath(value)
    require(not pure.is_absolute() and '..' not in pure.parts and ':' not in value and '\\' not in value, 'unsafe asset path')
    path = Path(value)
    require(path.is_file() and not path.is_symlink() and path.resolve().is_relative_to(Path.cwd().resolve()), 'asset unavailable or escapes release directory')
    return path

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('edge-id', 'origin-version', 'archive', 'checksum', 'target-manifest', 'origin-manifest', 'migration', 'actual-evidence', 'cutover-id'):
        parser.add_argument('--' + name, required=True)
    args = parser.parse_args()
    require(args.origin_version in ORIGINS and args.edge_id == args.origin_version + '-to-v0.17.0', 'unknown direct edge')
    require(args.cutover_id == 'retained-direct-upgrade-v1', 'unknown cutover')
    archive = asset(args.archive)
    require(sha(archive.read_bytes()) == EXPECTED_ARCHIVE, 'archive identity differs')
    require(asset(args.checksum).read_bytes() == (EXPECTED_ARCHIVE + '  ' + archive.name + '\n').encode(), 'checksum identity differs')
    actual = asset(args.actual_evidence)
    require(sha(actual.read_bytes()) == EXPECTED_ACTUAL, 'actual execution identity differs')
    source_root = Path.cwd().resolve().parents[2]
    sys.path.insert(0, str(source_root / '.ai/scripts'))
    import yaml
    from test_fixture_runtime import preflight_fixture_root
    spec = importlib.util.spec_from_file_location('source_release_gate', source_root / '.ai/scripts/validate-ai-context-release-state.py')
    gate = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(gate)
    matrix = yaml.safe_load(asset('support-matrix.yaml').read_bytes())
    gate.validate_direct_upgrade_execution(source_root, 'v0.17.0', list(ORIGINS), matrix)
    all_cases, _, package_source, archive_digest = gate.load_v017_execution_set(source_root, actual.parent)
    require(archive_digest == EXPECTED_ARCHIVE, 'execution-set archive differs')
    cases = [case for case in all_cases if case['origin'] == args.origin_version]
    cache = preflight_fixture_root(os.environ.get('AI_CONTEXT_TEST_TMP_ROOT')).root
    require(sha(asset(args.origin_manifest).read_bytes()) == ORIGINS[args.origin_version], 'original public manifest differs')
    # The caller supplies an isolated writable release workspace. Extraction
    # stays inside that workspace and the owned temporary child is removed.
    with tempfile.TemporaryDirectory(prefix='v017-edge-', dir=cache) as temporary:
        extracted = Path(temporary)
        with zipfile.ZipFile(archive) as opened:
            seen = set()
            for member in opened.infolist():
                pure = PurePosixPath(member.filename)
                require(not pure.is_absolute() and '..' not in pure.parts and ':' not in member.filename and '\\' not in member.filename and member.filename not in seen, 'unsafe archive member')
                seen.add(member.filename)
                require(((member.external_attr >> 16) & 0o170000) != 0o120000, 'archive symlink')
                target = extracted / member.filename
                if member.is_dir():
                    target.mkdir(parents=True, exist_ok=True)
                else:
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_bytes(opened.read(member))
                    target.chmod((member.external_attr >> 16) & 0o777)
        incoming = extracted / 'ai-collaboration-framework-v0.17.0'
        sys.path.insert(0, str(incoming / 'payload/.ai/scripts'))
        apply = importlib.import_module('ai_context_package_apply')
        package, _, migration, manifest_sha = apply.validate_package_root(incoming)
        require(package['version'] == '0.17.0' and package['source'] == package_source, 'incoming source identity differs')
        require(asset(args.target_manifest).read_bytes() == (incoming / 'metadata/files.yaml').read_bytes(), 'target manifest differs')
        require(asset(args.migration).read_bytes() == (incoming / 'metadata/migration.yaml').read_bytes(), 'migration metadata differs')
        require([item['manifest_sha256'] for item in migration['sources'] if item['version'] == args.origin_version[1:]] == [ORIGINS[args.origin_version]], 'direct migration is missing')
        observed = apply.incoming_package_validation(incoming, package)
    portable = {'schema_version': 'incoming-package-validation/v1', 'authority': {'kind': observed['authority'], 'manifest': {'path': observed['manifest_path'], 'sha256': observed['manifest_sha256']}, 'validator': {'path': observed['path'], 'sha256': observed['sha256'], 'argv': observed['argv']}}, 'package_identity': {'package_id': package['package_id'], 'release_id': package['release_id'], 'payload_fingerprint': package['identity']['payload_fingerprint']}, 'execution': observed['execution']}
    print(json.dumps({'edge_id': args.edge_id, 'from_version': args.origin_version, 'to_version': 'v0.17.0', 'portable_validation': portable, 'actual_upgrade': {'kind': 'retained-execution-set-validation', 'evidence_path': args.actual_evidence, 'sha256': EXPECTED_ACTUAL, 'cases': [case['case'] for case in cases], 'outcome': 'passed'}}, sort_keys=True, separators=(',', ':')))

if __name__ == '__main__':
    try:
        main()
    except Exception as exc:
        print(json.dumps({'outcome': 'failed', 'error_type': type(exc).__name__}), file=sys.stderr)
        raise SystemExit(1)
