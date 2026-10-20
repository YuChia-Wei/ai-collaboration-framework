"""Prepare this project migration request; no target writes or extra backups."""
import importlib.util
import json
from pathlib import Path
import sys

spec = importlib.util.spec_from_file_location('bridge', Path(__file__).with_name('rc3-migrate.py'))
bridge = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bridge)
root = bridge.plain(Path(sys.argv[1])).resolve()
out = bridge.plain(Path(sys.argv[2])).resolve()
assert root == bridge.TARGET.resolve() or root.is_relative_to(Path('C:/tmp/mig202').resolve())
assert not out.is_relative_to(root) and not root.is_relative_to(out)
assert not out.exists()
package = bridge.plain(Path('C:/tmp/v0202-release/package'))
candidate = bridge.plain(Path('C:/tmp/si202/out/subset-d13513d5782d4c2b969f326b452168ff'))
engine = json.loads((package / 'engine-pin.json').read_bytes())
assert bridge.digest(json.dumps(engine, sort_keys=True, separators=(',', ':')).encode()) == bridge.NEW_PIN
for row in engine['files']:
    assert bridge.raw_hash(bridge.member(package / 'engine', row['path'])) == row['sha256']
selection_bytes = Path('C:/tmp/si202/selection.json').read_bytes()
selection = json.loads(selection_bytes)
assert selection == json.loads((candidate / 'metadata/selection.json').read_bytes())['desired']
assert len(selection['skills']) == 17 and selection['knowledge'] == [] and selection['bindings'] == []
assert selection['adapters'] == ['claude', 'codex'] and selection['skill_naming'] == 'original'
out.mkdir()
for name in ('scratch', 'staging', 'recovery'):
    (out / name).mkdir()
(out / 'staging/objects').mkdir()
edits = []
for name in ('.agents/skills/README.md', '.ai/INDEX.MD', '.ai/custom/installation.json',
             '.claude/skills/README.md', 'AGENTS.md', 'AGENTS.zh-TW.md'):
    before = bridge.member(root, name).read_bytes()
    if name == '.ai/custom/installation.json':
        after = selection_bytes
    elif name == '.ai/INDEX.MD':
        assert before.count(b'`tools/reinstall-framework.py`') == 1
        after = before.replace(b'`tools/reinstall-framework.py`', b'`src/tools/reinstall-framework.py`')
    else:
        assert before.count(b'bdd-gwt-test-designer') == (2 if name.endswith('/README.md') else 1)
        after = before.replace(b'bdd-gwt-test-designer', b'test-designer')
    after_hash = bridge.digest(after)
    (out / 'staging/objects' / after_hash).write_bytes(after)
    edits.append(dict(path=name, before_sha256=bridge.digest(before), after_sha256=after_hash,
                      after_content_ref='objects/' + after_hash))
request = dict(
    api_version=2, operation='plan', project_root=str(root),
    engine_root=str(package / 'engine'), engine=engine, candidate_root=str(candidate),
    candidate_identity=json.loads((candidate / 'metadata/build.json').read_bytes())['identity'],
    expected_lock_sha256=None, mode_policy='windows-inventory-only',
    scratch_root=str(out / 'scratch'), staging_root=str(out / 'staging'), recovery_root=str(out / 'recovery'),
    durability=dict(declared_by='target-owner', failure_domain='process-termination',
                    declaration_reference='Owner approved project-specific RC3 migration on 2026-10-21; workflow 2026-10-20-installation-ownership'),
    protected_inputs=[dict(path='.ai/custom/framework.json',
                           sha256=bridge.raw_hash(bridge.member(root, '.ai/custom/framework.json')))],
    project_data_action='none', project_edits=edits)
bridge.save(out / 'plan-request.json', request)
print(json.dumps(dict(prepared=str(out), project_edits=len(edits))))
