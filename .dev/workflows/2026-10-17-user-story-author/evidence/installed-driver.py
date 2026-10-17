"""Task-owned #459 standalone/combined Story installed acceptance; execute only on approved frozen source.

Invoke with isolated Python and one clean immutable --commit. No retries or cleanup.
Source export is the sole source-product import; consumers use packaged engines.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import runpy
import subprocess
import sys
import tempfile
import time

REPO = Path('C:/Github/YuChia/ai-collaboration-prompts-dotnet-backend')
BRANCH = 'codex/2026-10-17-method-knowledge-skills'
SCRIPT = Path(__file__).absolute()

def require(value, reason):
    if not value:
        raise RuntimeError(reason)

def git(*args):
    return subprocess.check_output(['git', '-C', str(REPO), *args])

def guard(commit):
    require(git('rev-parse', 'HEAD').decode().strip() == commit, 'HEAD drift')
    require(git('branch', '--show-current').decode().strip() == BRANCH, 'branch drift')
    require(not git('status', '--porcelain', '--untracked-files=all').strip(), 'source working tree not clean')

def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def load(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))

def save(path, value):
    Path(path).write_text(json.dumps(value, indent=2, ensure_ascii=False)+'\n', encoding='utf-8')

def internal(stage, request, commit):
    guard(commit)
    if stage == 'export':
        sys.path.insert(0, str(REPO/'src'))
        from distribution.catalog import package_engine
        guard(commit)
        result = package_engine(REPO, commit, Path(request['output']))
    else:
        host = runpy.run_path(str(REPO/'tools/build-catalog.py'))['verified_host']
        with host(Path(request['engine']), Path(request['pin'])):
            from distribution.catalog import read_installed_resources
            result = read_installed_resources(Path(request['project']), request['lock'], [])
        for row in result['resources']:
            require(digest(Path(request['project'])/row['member']) == row['sha256'], 'resource hash mismatch')
        require(digest(Path(request['project'])/'.ai/framework.lock') == request['lock'], 'read lock drift')
    guard(commit)
    return result

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--commit', required=True)
    parser.add_argument('--trial-root', type=Path)
    parser.add_argument('--internal', choices=['export', 'read'])
    args = parser.parse_args()
    require(re.fullmatch('[0-9a-f]{40}', args.commit), 'full lowercase SHA required')
    require(sys.flags.isolated and sys.flags.dont_write_bytecode, 'use python -I -B')
    require(os.name == 'nt', 'selected Windows inventory trial requires Windows')
    guard(args.commit)
    if args.internal:
        print(json.dumps(internal(args.internal, json.load(sys.stdin), args.commit)))
        return

    if args.trial_root is None:
        trial = Path(tempfile.mkdtemp(prefix='s459-'))
    else:
        trial = args.trial_root.absolute()
        require(trial.parent == Path('C:/') and re.fullmatch(r's459-[0-9a-f]{8}',trial.name),
                'explicit short trial root must be a new C:/s459-<8hex> directory')
        require(not trial.exists(), 'explicit trial root already exists')
        trial.mkdir()
    summary = {'source_commit': args.commit, 'branch': BRANCH, 'trial': str(trial),
               'actual_argv': sys.argv, 'cases': {}, 'steps': [],
               'synthetic_version': '0.0.0', 'mode_policy': 'windows-inventory-only',
               'durability': 'process-termination', 'agent_behavior': 'not-assessed',
               'publication': 'not-performed'}
    started = time.monotonic()
    save(trial/'invocation.json', summary)

    def stage_log(name, event, **extra):
        with (trial/'stages.jsonl').open('a',encoding='utf-8') as stream:
            stream.write(json.dumps({'stage':name,'event':event,'time':time.time(),**extra})+'\n')

    def mkdir(path):
        guard(args.commit)
        path.mkdir()
        return path

    def run(name, argv, request=None, negative=False):
        guard(args.commit)  # Before every product invocation, including mutating ones.
        if request is not None:
            save(trial/(name+'-request.json'), request)
        save(trial/(name+'-argv.json'), argv)
        tick = time.monotonic()
        stage_log(name,'started',argv=argv,timeout_seconds=300)
        process = subprocess.Popen(argv, stdin=subprocess.PIPE,stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE,text=True,cwd=trial,
                                   creationflags=subprocess.CREATE_NEW_PROCESS_GROUP)
        timed_out = False
        try:
            stdout,stderr = process.communicate(json.dumps(request) if request is not None else None,timeout=300)
        except subprocess.TimeoutExpired as timeout:
            timed_out = True
            partial_stdout = timeout.stdout or ''
            partial_stderr = timeout.stderr or ''
            if isinstance(partial_stdout,bytes): partial_stdout=partial_stdout.decode(errors='replace')
            if isinstance(partial_stderr,bytes): partial_stderr=partial_stderr.decode(errors='replace')
            (trial/(name+'-timeout-partial-stdout.txt')).write_text(partial_stdout,encoding='utf-8')
            (trial/(name+'-timeout-partial-stderr.txt')).write_text(partial_stderr,encoding='utf-8')
            # This exact PID is owned by the invocation above. Terminate its tree;
            # never leave a timed-out product operation running or retry it.
            killed = subprocess.run(['taskkill','/PID',str(process.pid),'/T','/F'],
                                    capture_output=True,text=True,timeout=30)
            (trial/(name+'-termination.txt')).write_text(killed.stdout+killed.stderr,encoding='utf-8')
            if process.poll() is None:
                process.kill()
            stdout,stderr = process.communicate(timeout=30)
        (trial/(name+'-response.json')).write_text(stdout, encoding='utf-8')
        (trial/(name+'-stderr.txt')).write_text(stderr, encoding='utf-8')
        step = {'name':name,'argv':argv,'exit':process.returncode,'timed_out':timed_out,
                'duration_seconds':round(time.monotonic()-tick,6)}
        summary['steps'].append(step)
        stage_log(name,'finished',**{k:v for k,v in step.items() if k!='name'})
        require(not timed_out,name+' timed out; retained evidence, no retry')
        guard(args.commit)
        data = json.loads(stdout)
        require((process.returncode != 0) if negative else (process.returncode == 0), name+' unexpected exit')
        return data

    def child(stage, request, name):
        return run(name, [sys.executable,'-I','-B',str(SCRIPT),'--commit',args.commit,'--internal',stage], request)

    def selection(catalog, skills, knowledge, naming):
        root = Path(catalog['artifact_root'])
        return {'selection_version':3, 'catalog':{'identity':catalog['identity'],
                'catalog_sha256':digest(root/'metadata/catalog.json'), 'files_sha256':digest(root/'metadata/catalog-files.json')},
                'skills':sorted(skills), 'knowledge':sorted(knowledge), 'sub_agents':[],
                'adapters':['claude','codex'], 'bindings':[], 'skill_naming':naming}

    def derive(name, bundle, catalog, desired, negative=False):
        box = mkdir(trial/name)
        for p in ['out','scratch','staging','recovery']:
            mkdir(box/p)
        save(box/'selection.json', desired)
        save(box/'engine-pin.json', bundle['engine'])
        engine = Path(bundle['engine_root'])
        result = run(name+'-derive', [sys.executable,'-I','-B',str(engine/'src/tools/derive-subset.py'),
            '--catalog-root',catalog['artifact_root'],'--catalog-identity',catalog['identity'],
            '--selection',str(box/'selection.json'),'--engine-pin',str(box/'engine-pin.json'),
            '--output-root',str(box/'out'),'--scratch-root',str(box/'scratch')], negative=negative)
        return box, result

    def inspect_request(bundle, candidate, project):
        return {'api_version':2,'operation':'inspect','project_root':str(project),
                'engine_root':bundle['engine_root'],'engine':bundle['engine'],'candidate_root':candidate['artifact_root']}

    def maintenance(name, bundle, request, negative=False):
        return run(name,[sys.executable,'-I','-B',str(Path(bundle['engine_root'])/'src/tools/maintain_framework.py')],request,negative)

    def request_plan(bundle, candidate, project, box, lock):
        return {**inspect_request(bundle,candidate,project), 'operation':'plan',
            'candidate_identity':candidate['identity'],'expected_lock_sha256':lock,
            'mode_policy':'windows-inventory-only','scratch_root':str(box/'scratch'),
            'staging_root':str(box/'staging'),'recovery_root':str(box/'recovery'),
            'durability':{'declared_by':'story-validation-owner',
             'declaration_reference':'Owner-selected isolated Story acceptance #459','failure_domain':'process-termination'},
            'protected_inputs':[],'project_data_action':'none','project_edits':[]}

    def members(candidate):
        return {r['destination']:r for r in load(Path(candidate['artifact_root'])/'metadata/files.json')['files']}

    def install(name,bundle,candidate,project,box):
        inspection = maintenance(name+'-before',bundle,inspect_request(bundle,candidate,project))
        require(inspection['details']['managed_state'] == 'uninstalled', 'unexpected pre-state')
        old_rows = {}
        req = request_plan(bundle,candidate,project,box,None)
        plan = maintenance(name+'-plan',bundle,req)
        require(plan['outcome']=='planned','plan not produced')
        target_rows = members(candidate)
        expected = {}
        for path,row in target_rows.items():
            previous = old_rows.get(path)
            if previous is None:
                expected[path] = 'add'
            elif any(previous[k] != row[k] for k in ['sha256','size','owner','kind']):
                expected[path] = 'change'
            elif previous['mode'] != row['mode']:
                expected[path] = 'mode-only'
            else:
                expected[path] = 'unchanged'
        expected.update({p:'remove' for p in old_rows if p not in target_rows})
        actual = {r['destination']:r['action'] for r in plan['plan']['delta']}
        require(actual == expected, 'exact delta mismatch; inspect retained plan, no apply')
        unknown = plan['plan']['preserved_unknown']
        require(not unknown, 'fresh consumer has unexpected unowned managed-path content')
        apply = {**req,'operation':'apply','expected_plan_sha256':plan['plan_sha256'],
          'maintenance':{'declared_by':'story-validation-owner',
           'declaration_reference':'Exact delta reviewed in disposable project; no other session/tool/writer uses it',
           'affected_capabilities':plan['plan']['maintenance_scope'],
           'sessions_stopped':True,'tools_stopped':True,'external_writers_stopped':True}}
        applied = maintenance(name+'-apply',bundle,apply)
        require(applied['outcome']=='applied','apply did not complete')
        after = maintenance(name+'-after',bundle,inspect_request(bundle,candidate,project))
        require(after['details']['managed_state']=='managed-bytes-consistent' and not after['details']['drift'],'post inspect inconsistent')
        (trial/(name+'-raw-lock.json')).write_bytes((project/'.ai/framework.lock').read_bytes())
        return after

    def read_case(name,bundle,project,inspection,source):
        lock = digest(project/'.ai/framework.lock')
        pinfile = trial/(name+'-reader-engine-pin.json')
        save(pinfile,bundle['engine'])
        result = child('read',{'engine':bundle['engine_root'],'pin':str(pinfile),'project':str(project),'lock':lock},name+'-read')
        payloads = 0
        for row in inspection['details']['owned']:
            require(digest(project/row['destination'])==row['sha256'],'owned mismatch')
            if row['source'] is not None:
                require(hashlib.sha256(git('show',source+':'+row['source']['path'])).hexdigest()==row['sha256'],'payload differs from immutable source')
                payloads += 1
        save(trial/(name+'-actor-input.json'),{'project_root':str(project),'engine_root':bundle['engine_root'],
             'engine_pin':str(pinfile),'expected_lock_sha256':lock,'verified_resources':result})
        return {'project_root':str(project),'lock_sha256':lock,'resource_count':len(result['resources']),
                'source_identical_payloads':payloads,'actor_input':str(trial/(name+'-actor-input.json'))}

    try:
        for part in ['engine-output','catalog-output','catalog-scratch']:
            mkdir(trial/part)
        bundle = child('export',{'output':str(trial/'engine-output')},'export-engine')
        save(trial/'bundle.json',bundle)
        save(trial/'engine-pin.json',bundle['engine'])
        catalog = run('catalog',[sys.executable,'-I','-B',str(REPO/'tools/build-catalog.py'),
          '--repository',str(REPO),'--commit',args.commit,'--release-version','0.0.0',
          '--engine-pin',str(trial/'engine-pin.json'),'--output-root',str(trial/'catalog-output'),
          '--scratch-root',str(trial/'catalog-scratch')])
        for name,skills,knowledge,naming in [('A',['user-story-author'],[],'original'),('B',['user-story-author','test-designer'],[],'prefixed')]:
            desired = selection(catalog,skills,knowledge,naming)
            box,candidate = derive(name,bundle,catalog,desired)
            project = mkdir(box/'project')
            inspection = install(name,bundle,candidate,project,box)
            summary['cases'][name] = read_case(name,bundle,project,inspection,args.commit)
            require((summary['cases'][name]['resource_count']>0)==bool(knowledge),'knowledge inventory mismatch')
            for adapter in ['.agents','.claude']:
                for skill in skills:
                    entry = ('aicf-' if naming=='prefixed' else '')+skill
                    require((project/adapter/'skills'/entry/'SKILL.md').is_file(),'runtime entry missing')
        guard(args.commit)
        summary['outcome']='completed-selected-installed-checks'
    except BaseException as exc:
        summary['outcome']='failed'
        summary['error']={'type':type(exc).__name__,'message':str(exc)}
        raise
    finally:
        summary['duration_seconds']=round(time.monotonic()-started,6)
        save(trial/'summary.json',summary)
        print(json.dumps({'trial':str(trial),'summary':str(trial/'summary.json'),'outcome':summary.get('outcome')}),flush=True)

if __name__ == '__main__':
    main()
