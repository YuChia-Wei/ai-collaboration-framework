"""One owner-authorized two-case replay using the unchanged tracked executor."""
import argparse, importlib, importlib.util, json, subprocess, sys, time
from pathlib import Path
import yaml

sys.dont_write_bytecode = True
ROOT = Path.cwd().resolve()
SHA = 'a7b171df383ba416815275e81ed06f13e77b13ca'
CORE = '.github/scripts/validate-v017-direct-upgrades.py'
CORE_HASH = '7b83294b491465486070dcf0796e7485e229b37bfc417772b4d4f7f39590feba'
CANDIDATE_HASH = 'b9e6b38515e8ac82731734b99bacb97b40ca0c7ad543d2b6f84390b4cdb94a22'
EXPECTED = ['v0.16.0-customized-none', 'v0.16.0-customized-rollback']

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--candidate-archive', type=Path, required=True)
    parser.add_argument('--origin-archive', type=Path, required=True)
    parser.add_argument('--subject-sha', required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    import hashlib
    if hashlib.sha256((ROOT / CORE).read_bytes()).hexdigest() != CORE_HASH:
        raise RuntimeError('tracked executor hash mismatch')
    spec = importlib.util.spec_from_file_location('v017_core', ROOT / CORE)
    core = importlib.util.module_from_spec(spec); spec.loader.exec_module(core)
    output = args.output.resolve()
    core.require(output.is_relative_to(ROOT / '.dev/ai-context/local/validation'), 'output outside declared root')
    core.require(not output.exists(), 'fresh output required')
    output.mkdir(parents=True)
    terminal = {'schema_version': 'direct-upgrade-execution/v1', 'subject_sha': args.subject_sha,
        'started_at': core.stamp(), 'evidence_kind': 'actual-isolated-target-execution', 'cases': [], 'outcome': 'failed',
        'runner': {'path': CORE, 'sha256': CORE_HASH},
        'selection_runner': {'path': Path(__file__).resolve().relative_to(ROOT).as_posix(), 'sha256': core.sha(Path(__file__).read_bytes())},
        'selection': {'mode': 'owner-selected-two-case-retest', 'required_cases': EXPECTED, 'full_matrix': False},
        'invocation': [sys.executable, str(Path(__file__).resolve().relative_to(ROOT)), *sys.argv[1:]]}
    started = time.monotonic()
    try:
        core.require(args.subject_sha == SHA == subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip(), 'source commit drift')
        core.require(not subprocess.check_output(['git', 'status', '--porcelain=v1'], text=True).strip(), 'unclean source')
        candidate = args.candidate_archive.resolve(); origin_archive = args.origin_archive.resolve()
        for archive, expected in [(candidate, CANDIDATE_HASH), (origin_archive, core.ORIGINS['v0.16.0'][0])]:
            core.require(core.sha(archive.read_bytes()) == expected, 'archive identity mismatch')
            core.require(archive.with_suffix(archive.suffix + '.sha256').read_text().split()[0] == expected, 'archive sidecar mismatch')
        incoming = core.extract(candidate, output / 'incoming')
        package = yaml.safe_load((incoming / 'metadata/package.yaml').read_bytes())
        core.require(package['version'] == '0.17.0', 'wrong incoming version')
        terminal['archive_sha256'] = CANDIDATE_HASH; terminal['package_source'] = package['source']
        sys.path.insert(0, str(incoming / 'payload/.ai/scripts'))
        apply = importlib.import_module('ai_context_package_apply')
        provenance = importlib.import_module('ai_context_target_provenance')
        rules = importlib.import_module('ai_context_effective_rules')
        apply.validate_package_root(incoming)
        previous = core.extract(origin_archive, output / 'origin-v0.16.0')
        core.require(core.sha((previous / 'metadata/files.yaml').read_bytes()) == core.ORIGINS['v0.16.0'][1], 'origin manifest mismatch')
        for recovery in ('none', 'rollback'):
            terminal['active_case'] = 'v0.16.0-customized-' + recovery
            result = core.execute_case('v0.16.0', previous, incoming, output, True, recovery, apply, provenance, rules)
            core.require(result['case'] == terminal['active_case'] and result['outcome'] == 'passed', 'case result mismatch')
            terminal['cases'].append(result); terminal.pop('active_case')
            core.write_json(output / 'progress.json', terminal)
            print(json.dumps({'event': 'case-passed', 'case': result['case'], 'completed_cases': len(terminal['cases'])}), flush=True)
        core.require([case['case'] for case in terminal['cases']] == EXPECTED, 'selected cases incomplete')
        terminal['outcome'] = 'passed'
    except Exception as exc:
        message = str(exc)
        for path, label in [(output, 'VALIDATION_OUTPUT'), (ROOT, 'SOURCE_ROOT')]:
            message = message.replace(str(path), label)
        terminal['failure'] = {'type': type(exc).__name__, 'message': message}
        terminal['failure_fingerprint'] = core.sha(core.canonical(terminal['failure']))
        raise
    finally:
        terminal['completed_at'] = core.stamp()
        terminal['duration_seconds'] = round(time.monotonic() - started, 3)
        core.write_json(output / 'terminal.json', terminal)
    print(json.dumps({'outcome': terminal['outcome'], 'selected_cases': len(terminal['cases']), 'full_matrix': False}))

if __name__ == '__main__':
    main()
