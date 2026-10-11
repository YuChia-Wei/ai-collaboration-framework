"""One bounded real-CLI walkthrough; writes only a disposable native-temp fixture and this evidence directory."""
import copy
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time

root = Path.cwd().resolve()
evidence = root / '.dev/ai-context/local/workflow-records-continuation'
workflow_id = '2026-10-02-skill-routing'
cli = root / 'tools/workflow-records.py'
source = root / '.dev/workflows' / workflow_id
version = 'workflow-records/1'
started = time.monotonic()

def command(argv, cwd=None):
    return subprocess.run(argv, cwd=cwd, capture_output=True, timeout=20)

def git(repository, *args):
    result = command(['git', '-C', str(repository), *args])
    assert result.returncode == 0, result.stderr.decode(errors='replace')
    return result.stdout.decode('utf-8').strip()

def digest(raw):
    return 'sha256:' + hashlib.sha256(raw).hexdigest()

def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

source_head = git(root, 'rev-parse', 'HEAD')
source_manifest = {p.relative_to(source).as_posix(): digest(p.read_bytes())
                   for p in source.rglob('*') if p.is_file()}
cases = []
with tempfile.TemporaryDirectory(prefix='workflow-record-walkthrough-') as temporary:
    fixture_root = Path(temporary).resolve()
    assert fixture_root.is_relative_to(Path(tempfile.gettempdir()).resolve())
    assert fixture_root.name.startswith('workflow-record-walkthrough-')
    assert not fixture_root.is_symlink()
    project = fixture_root / 'project'
    artifact = project / '.dev/workflows' / workflow_id
    shutil.copytree(source, artifact)
    git(project, 'init', '--initial-branch=example')
    git(project, 'add', '.')
    git(project, '-c', 'user.name=Workflow Example', '-c', 'user.email=example@example.invalid',
        '-c', 'commit.gpgsign=false', '-c', 'core.hooksPath=empty-hooks', 'commit', '-m', 'Example fixture')
    fixture_commit = git(project, 'rev-parse', 'HEAD')

    def invoke(case_id, operation, config=None, **fields):
        request = {'contract_version': version, 'operation': operation, **fields}
        request_file = fixture_root / f'{case_id}.json'
        save(request_file, request)
        argv = [sys.executable, '-I', '-B', str(cli), '--root', str(project), '--request', str(request_file)]
        if config is not None:
            config_file = fixture_root / f'{case_id}-config.json'
            save(config_file, config)
            argv += ['--config', str(config_file)]
        result = command(argv)
        assert not result.stderr, result.stderr.decode(errors='replace')
        response = json.loads(result.stdout)
        assert result.returncode == (0 if response['status'] == 'ok' else 1)
        cases.append({'id': case_id, 'request': request, 'configuration': config,
                      'exit_code': result.returncode, 'stderr_empty': True, 'response': response})
        return response

    capabilities = invoke('01-capabilities', 'capabilities')
    assert not capabilities['result']['providers']['git']['create']
    create = invoke('02-create-unsupported', 'create')
    assert create['error']['code'] == 'unsupported_capability'
    found = invoke('03-find', 'find', provider_id='git', limit=10)
    ref = found['result']['items'][0]['workflow_ref']
    context = invoke('04-context', 'context', workflow_ref=ref)['result']
    payload = {'summary': '完成來源盤點，準備審核設計', 'authority': '隔離 fixture 示範，不代表正式採用',
               'completed': ['盤點目前讀取與寫入路徑'], 'pending': ['審核設計'], 'blockers': [],
               'evidence': ['inventory.md'], 'next_action': '核對設計與驗收案例'}
    checkpoint_fields = {'workflow_ref': ref, 'expected_revision': context['revision'],
                         'expected_source_head': context['source_head'],
                         'operation_id': 'checkpoint-001', 'checkpoint': payload}
    written = invoke('05-checkpoint', 'checkpoint', **checkpoint_fields)
    assert written['result']['state'] == 'applied' and not written['result']['replayed']
    journal = artifact / '.workflow-records/checkpoint.json'
    journal_raw = journal.read_bytes()
    replayed = invoke('06-replay', 'checkpoint', **checkpoint_fields)
    assert replayed['result']['replayed'] and journal.read_bytes() == journal_raw
    stale_fields = copy.deepcopy(checkpoint_fields)
    stale_fields['operation_id'] = 'checkpoint-002'
    stale = invoke('07-stale-checkpoint', 'checkpoint', **stale_fields)
    assert stale['error']['code'] == 'revision_conflict' and stale['mutation_state'] == 'none'
    fresh = invoke('08-fresh-context', 'context', workflow_ref=ref)['result']
    assert fresh['revision'] != context['revision'] and fresh['entrypoint'] == context['entrypoint']
    document = invoke('09-read-document', 'read', workflow_ref=ref, **fresh['entrypoint'], limit=256)
    assert document['result']['content'] == (artifact / 'workflow-plan.md').read_text(encoding='utf-8')[:256]
    receipt = invoke('10-operation', 'operation', workflow_ref=ref, operation_id='checkpoint-001')
    assert receipt['result']['checkpoint_revision'] == written['result']['checkpoint_revision']
    missing = invoke('11-unknown-operation', 'operation', workflow_ref=ref, operation_id='not-recorded')
    assert missing['result']['state'] == 'unknown'
    resumed = invoke('12-resume', 'resume', workflow_ref=ref, limit=256)
    assert resumed['result']['checkpoint']['next_action']['text'] == payload['next_action']
    config = {'contract_version': version, 'default_provider': 'board', 'stores': {
        'git': {'kind': 'git', 'store_id': 'project-workflows', 'root': '.dev/workflows'},
        'board': {'kind': 'remote', 'store_id': 'board-records'}}}
    unavailable = invoke('13-unqualified-unavailable', 'find', config=config)
    assert unavailable['status'] == 'unavailable' and unavailable['mutation_state'] == 'none'
    unchanged_binding = invoke('14-explicit-git-binding', 'context', config=config, workflow_ref=ref)
    assert unchanged_binding['result']['workflow_ref'] == ref
    remote_fields = copy.deepcopy(checkpoint_fields)
    remote_fields['workflow_ref'] = {'provider_id': 'board', 'store_id': 'board-records', 'workflow_id': workflow_id}
    remote = invoke('15-remote-write-unavailable', 'checkpoint', config=config, **remote_fields)
    assert remote['status'] == 'unavailable' and remote['error']['code'] == 'provider_unavailable'
    assert remote['mutation_state'] == 'none' and journal.read_bytes() == journal_raw
    assert git(project, 'diff', '--name-only') == ''
    for relative, expected in source_manifest.items():
        assert digest((artifact / relative).read_bytes()) == expected
        assert digest((source / relative).read_bytes()) == expected
    assert git(root, 'rev-parse', 'HEAD') == source_head
    result = {'observed_at': datetime.now(timezone.utc).isoformat(timespec='seconds'),
              'implementation_head': source_head, 'fixture_source': '.dev/workflows/' + workflow_id,
              'fixture_commit': fixture_commit, 'source_manifest': source_manifest, 'cases': cases,
              'checks': {'original_fixture_bytes_preserved': True, 'source_record_bytes_preserved': True,
                         'replay_bytes_unchanged': True, 'no_fallback_write': True,
                         'fixture_tracked_diff_empty': True}, 'duration_seconds': round(time.monotonic() - started, 3)}
assert not fixture_root.exists(), 'Fixture cleanup did not finish'
result['checks']['owned_fixture_cleanup_complete'] = True
save(evidence / 'walkthrough-transcript.json', result)
summary = {key: value for key, value in result.items() if key not in ('cases', 'source_manifest')}
summary['cases'] = [{'id': case['id'], 'exit_code': case['exit_code'],
                     'status': case['response']['status'], 'mutation_state': case['response']['mutation_state'],
                     'error_code': case['response'].get('error', {}).get('code'),
                     'operation_state': case['response'].get('result', {}).get('state')}
                    for case in cases]
summary['transcript_sha256'] = digest((evidence / 'walkthrough-transcript.json').read_bytes())
save(evidence / 'walkthrough-summary.json', summary)
print(json.dumps(summary, ensure_ascii=False))
