from pathlib import Path
from hashlib import sha256
from datetime import datetime, timezone
import argparse, base64, importlib.metadata, json, os, platform, re, stat, subprocess, sys, time, uuid

REPO = Path('F:/framework-next/368')
WF = REPO / '.dev/workflows/2026-09-23-source-contract-checks'
PARENT = Path('F:/framework-next/p7-runs/368-contracts')
parser = argparse.ArgumentParser()
parser.add_argument('--expected-head', required=True)
args = parser.parse_args()
assert re.fullmatch(r'[0-9a-f]{40}', args.expected_head)
output = REPO / '.dev/ai-context/local' / ('cr002-368-' + uuid.uuid4().hex)
output.mkdir()
record = {'started_at': datetime.now(timezone.utc).isoformat(), 'expected_head': args.expected_head,
          'workdir': str(REPO), 'capture_directory': str(output), 'timeout_seconds': 90,
          'tests_dispatched': False, 'outcome': 'preflight-pending', 'wrapper_git_calls': 0}
stdout = stderr = b''

def git(*argv):
    record['wrapper_git_calls'] += 1
    return subprocess.check_output(['git', *argv], cwd=REPO)

def snapshot(root):
    entries = []; pending = [root]
    while pending:
        current = pending.pop()
        info = current.lstat()
        assert not stat.S_ISLNK(info.st_mode) and not getattr(info, 'st_file_attributes', 0) & stat.FILE_ATTRIBUTE_REPARSE_POINT
        row = {'path': current.relative_to(root).as_posix(), 'device': info.st_dev, 'inode': info.st_ino,
               'mode': info.st_mode, 'attributes': getattr(info, 'st_file_attributes', 0), 'nlink': info.st_nlink,
               'size': info.st_size, 'mtime_ns': info.st_mtime_ns}
        if stat.S_ISDIR(info.st_mode): pending.extend(current.iterdir())
        else:
            assert stat.S_ISREG(info.st_mode)
            row['sha256'] = sha256(current.read_bytes()).hexdigest()
        entries.append(row)
        assert len(entries) <= 2048, 'historical read-only inventory exceeded its bounded expectation'
    return sorted(entries, key=lambda item: item['path'])

try:
    assert git('rev-parse', 'HEAD').decode().strip() == args.expected_head
    assert not git('status', '--porcelain=v1').strip()
    assert git('branch', '--show-current').decode().strip() == 'codex/2026-09-23-source-contract-checks'
    plan = json.loads((WF / 'cr002-checks.json').read_text(encoding='utf-8'))
    record['source_tree_oid'] = git('rev-parse', 'HEAD:src').decode().strip()
    record['selected_source_commit'] = plan['selected_source_commit']
    record['runtime'] = {'python': sys.version.split()[0], 'executable': sys.executable, 'platform': platform.platform(),
                         'isolated': sys.flags.isolated, 'dont_write_bytecode': sys.dont_write_bytecode,
                         'packages': {name: importlib.metadata.version(name) for name in ('PyYAML', 'jsonschema', 'referencing')},
                         'git': git('--version').decode().strip()}
    record['capture_script_sha256'] = sha256(Path(__file__).read_bytes()).hexdigest()
    paths = ['tests/framework_next/run.py', 'tests/framework_next/support.py', 'tests/framework_next/test_contracts.py',
             'src/distribution/assembly.py', 'src/distribution/installation_state.py', 'src/distribution/data.py',
             'src/distribution/git_source.py', 'src/distribution/package.py', 'src/distribution/selection.py',
             'src/distribution/codex.py', 'src/distribution/manifest.yaml']
    record['execution_file_sha256'] = {name: sha256((REPO / name).read_bytes()).hexdigest() for name in paths}
    assert record['execution_file_sha256'] == plan['planned_code_sha256']
    old_roots = [p for p in sorted(PARENT.iterdir()) if p.is_dir()]
    assert all(re.fullmatch(r'fn-[0-9a-f]{32}', p.name) for p in old_roots)
    old_roots.append(Path('F:/framework-next/p7-runs/373-public/fn-c21e6bb478f64c759aed8dfdbba5ea6d'))
    record['historical_before'] = {str(p): snapshot(p) for p in old_roots}
    record['argv'] = [sys.executable, *plan['argv_after_python']]
    record['tests_dispatched'] = True
    started = time.monotonic()
    try:
        result = subprocess.run(record['argv'], cwd=REPO, capture_output=True, timeout=90)
        stdout, stderr = result.stdout, result.stderr
        record['exit_code'] = result.returncode
        record['outcome'] = 'runner-passed' if result.returncode == 0 else 'runner-failed'
    except subprocess.TimeoutExpired as exc:
        stdout, stderr = exc.stdout or b'', exc.stderr or b''
        record.update(outcome='timeout', exit_code=None)
    finally:
        record['execution_wall_seconds'] = round(time.monotonic() - started, 3)
    record['historical_after'] = {str(p): snapshot(p) for p in old_roots}
    record['historical_unchanged'] = record['historical_before'] == record['historical_after']
    record['remaining_new_runs'] = [str(p) for p in sorted(PARENT.iterdir()) if p not in old_roots]
    rows = [json.loads(line) for line in stdout.decode('utf-8').splitlines() if line.strip()]
    record['observations'] = rows
    outer = []
    for row in rows:
        if 'C5_assembly' in row:
            for value in row['C5_assembly']['candidate_roots']:
                candidate = Path(value)
                relative = candidate.relative_to(PARENT)
                assert re.fullmatch(r'fn-[0-9a-f]{32}', relative.parts[0])
                outer.append(PARENT / relative.parts[0])
    record['candidate_owned_run_readback'] = [{'path': str(p), 'exists': p.exists()} for p in sorted(set(outer))]
    record['head_after'] = git('rev-parse', 'HEAD').decode().strip()
    record['status_after'] = git('status', '--porcelain=v1').decode()
    record['evidence_complete'] = (len(stdout)+len(stderr) <= 8*1024*1024 and record['historical_unchanged']
        and record['head_after'] == args.expected_head and not record['status_after']
        and bool(rows) and 'fixture_accounting' in rows[-1])
    if not record['evidence_complete']: record['outcome'] = 'evidence-failed'
except Exception as exc:
    record.update(outcome='capture-or-preflight-failed', exception_type=type(exc).__name__, diagnostic=str(exc))
finally:
    for name, value in [('stdout', stdout), ('stderr', stderr)]:
        (output / (name + '.bin')).write_bytes(value)
        record[name+'_sha256'] = sha256(value).hexdigest()
        record[name+'_base64'] = base64.b64encode(value).decode('ascii')
    record['finished_at'] = datetime.now(timezone.utc).isoformat()
    record['accounting_boundary'] = 'Fixture child/parent observations are separate. Wrapper Python, runner Python and wrapper Git reads are outside fixture audit counters.'
    (output / 'execution.json').write_text(json.dumps(record, indent=2)+'\n', encoding='utf-8', newline='\n')
    print(stdout.decode('utf-8', errors='replace'))
    print(stderr.decode('utf-8', errors='replace'))
    print(json.dumps({key: record.get(key) for key in ('outcome', 'exit_code', 'tests_dispatched', 'execution_wall_seconds', 'historical_unchanged', 'evidence_complete', 'capture_directory', 'diagnostic')}))
raise SystemExit(0 if record['outcome'] == 'runner-passed' and record['evidence_complete'] else 2)
