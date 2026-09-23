"""Issue-local command capture, not a fixture helper or acceptance runner."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

parser = argparse.ArgumentParser()
parser.add_argument('family')
parser.add_argument('label')
parser.add_argument('--read-only', action='store_true')
args = parser.parse_args()
root = Path(__file__).absolute().parents[3]
evidence = Path(__file__).absolute().parent / 'evidence'
outputs = [evidence / (args.label + extension) for extension in ('.stdout', '.stderr', '.json')]
if any(path.exists() for path in outputs):
    raise SystemExit('Capture label already exists; preserve prior evidence.')
argv = [sys.executable, '-I', '-B', str(root / 'tests/framework_next/run.py'), '--layer', 'public',
        '--family', args.family, '--output-root', 'F:/framework-next/p7-runs/373-public']
if args.read_only:
    argv.append('--public-read-only')
names = ['run.py', 'support.py', 'test_knowledge.py', 'test_work.py', 'test_cbf.py']
hashes = {name: hashlib.sha256((root / 'tests/framework_next' / name).read_bytes()).hexdigest() for name in names}
result = subprocess.run(argv, cwd=root, capture_output=True, timeout=110)
outputs[0].write_bytes(result.stdout)
outputs[1].write_bytes(result.stderr)
metadata = {'argv': argv, 'cwd': str(root), 'runner_exit': result.returncode, 'test_file_sha256': hashes,
            'capture_driver_subprocesses': 1, 'stdout_sha256': hashlib.sha256(result.stdout).hexdigest(),
            'stderr_sha256': hashlib.sha256(result.stderr).hexdigest()}
outputs[2].write_text(json.dumps(metadata, indent=2) + '\n', encoding='utf-8')
for line in result.stdout.splitlines():
    value = json.loads(line)
    if 'public_family' in value:
        item = value['public_family']
        calls = item.pop('calls', [])
        item['last_call'] = calls[-1] if calls else None
    print(json.dumps(value, sort_keys=True))
print('ACTUAL_RUNNER_EXIT=' + str(result.returncode))
if result.returncode:
    sys.stderr.buffer.write(result.stderr)
raise SystemExit(result.returncode)
