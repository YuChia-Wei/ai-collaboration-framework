"""Read back this migration's selected preservation and installation criteria."""
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

manifest_path, expected_hash, request_path, inspect_path = sys.argv[1:]
manifest_raw = Path(manifest_path).read_bytes()
assert hashlib.sha256(manifest_raw).hexdigest() == expected_hash
manifest = json.loads(manifest_raw)
request = json.loads(Path(request_path).read_bytes())
response = json.loads(Path(inspect_path).read_bytes())
root = Path(manifest['project_root'])
assert request['project_root'] == str(root)
assert response['details']['managed_state'] == 'managed-bytes-consistent'
assert response['details']['drift'] == []
spec = importlib.util.spec_from_file_location('bridge', Path(__file__).with_name('rc3-migrate.py'))
bridge = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bridge)
current = bridge.inventory(root)
old = manifest['owned']
new = {row['destination']: row['sha256'] for row in response['details']['owned']}
edits = {row['path']: row for row in request['project_edits']}
preserved = {name: value for name, value in manifest['baseline'].items() if name not in old and name not in edits}
assert all(current.get(name) == value for name, value in preserved.items()), 'preserved bytes changed'
assert all(current.get(name) == value for name, value in new.items()), 'new owned bytes differ'
assert all(current.get(name) == row['after_sha256'] for name, row in edits.items()), 'paired edits differ'
allowed = set(old) | set(new) | set(edits) | {bridge.GUARD}
changes = {name for name in set(current) | set(manifest['baseline'])
           if current.get(name) != manifest['baseline'].get(name)}
assert changes <= allowed, 'unexpected mutation'
assert all(name in new or name == bridge.LOCK or name not in current for name in old), 'old-only residue'
untracked = set(subprocess.check_output(['git', '-C', str(root), 'ls-files', '--others', '--exclude-standard']).decode().splitlines())
assert set(manifest['untracked']) <= untracked, 'original untracked paths became tracked or disappeared'
assert all(current[name] == manifest['baseline'][name] for name in manifest['untracked']), 'untracked bytes changed'
lock = json.loads((root / bridge.LOCK).read_bytes())
selection = json.loads((root / '.ai/custom/installation.json').read_bytes())
assert selection['adapters'] == ['claude', 'codex'] and len(selection['skills']) == 17
assert selection['knowledge'] == [] and selection['bindings'] == [] and selection['skill_naming'] == 'original'
assert 'test-designer' in selection['skills'] and 'bdd-gwt-test-designer' not in selection['skills']
assert lock['selection']['desired'] == selection
assert lock['selection']['release_version'] == '0.20.2'
for adapter in ('.agents', '.claude'):
    for skill in selection['skills']:
        assert f'{adapter}/skills/{skill}/SKILL.md' in new
assert lock['candidate_identity'] == request['candidate_identity']
assert lock['engine'] == request['engine']
bridge.no_markers(root)
print(json.dumps(dict(managed_state='managed-bytes-consistent', new_owned=len(new),
                     preserved_files=len(preserved), preserved_untracked=len(manifest['untracked']),
                     changed_paths=len(changes), paired_edits=len(edits),
                     skills=len(selection['skills']), adapters=selection['adapters'],
                     lock_sha256=bridge.raw_hash(root / bridge.LOCK)), sort_keys=True))
