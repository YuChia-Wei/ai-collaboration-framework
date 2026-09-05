"""Execute staged edge validators once and retain canonical route evidence."""
from pathlib import Path
import argparse,datetime,hashlib,json,subprocess,sys,time
from copy import deepcopy
import yaml
root=Path.cwd()
sys.path.insert(0,str(root/'.ai/scripts'))
from ai_context_upgrade_routes import canonical_json,load_route_matrix,resolve_upgrade_route

def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def sha(raw):return hashlib.sha256(raw).hexdigest()
def write(path,raw):path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(raw)
def doc(path,value):write(path,canonical_json(value).encode())
def desc(staging,path,identity):return {'asset_id':identity,'path':path,'sha256':sha((staging/path).read_bytes())}
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--staging',type=Path,required=True)
parser.add_argument('--subject-sha',required=True)
parser.add_argument('--actual-dir',type=Path,required=True)
args=parser.parse_args()
staging=args.staging.resolve()
assert staging.is_relative_to((root/'.dev/ai-context/local/validation/issue-272').resolve())
assert subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()==args.subject_sha
assert not subprocess.check_output(['git','status','--porcelain'],text=True).strip()
assert not (staging/'edge-execution-terminal.json').exists()
matrix=yaml.safe_load((staging/'support-matrix.pending.yaml').read_bytes())
begin=time.monotonic();terminal={'schema_version':'staged-edge-execution/v1','subject_sha':args.subject_sha,'started_at':now(),'outcome':'failed','edges':[]}
terminal['invocation']=['python',*sys.argv]
terminal['runner_sha256']=sha(Path(__file__).read_bytes())
try:
    for route in matrix['routes']:
        edge=route['edges'][0];argv=edge['validation']['validator_argv']
        started=now();timer=time.monotonic()
        timed_out=False
        try:
            result=subprocess.run(argv,cwd=staging,capture_output=True,timeout=240)
            output=result.stdout+result.stderr;exit_code=result.returncode
        except subprocess.TimeoutExpired as exc:
            output=(exc.stdout or b'')+(exc.stderr or b'');exit_code=None;timed_out=True
        label=edge['edge_id'];output_path=f'route-assets/edge-validation/{label}.log'
        write(staging/output_path,output)
        observation={'edge_id':label,'command':argv,'started_at':started,'completed_at':now(),'duration_seconds':round(time.monotonic()-timer,3),'exit_code':exit_code,'outcome':'timeout' if timed_out else ('passed' if exit_code==0 else 'failed'),'output':output_path,'output_sha256':sha(output)}
        terminal['edges'].append(observation)
        if timed_out:
            terminal['outcome']='timeout'
            raise RuntimeError(f'{label} execution timed out')
        assert exit_code==0,f'{label} execution failed'
        observed=json.loads(result.stdout)
        assert observed['edge_id']==label and observed['actual_upgrade']['outcome']=='passed'
        for cutover in edge['semantic_cutovers']:cutover['state']='passed'
        receipt={'schema_version':'upgrade-edge-validation/v2','edge_id':label,'from_version':edge['from_version'],'to_version':edge['to_version'],'artifacts':edge['artifacts'],'validator_argv':argv,'semantic_cutovers':[dict(cutover,required=next(row['required'] for row in matrix['semantic_cutovers'] if row['cutover_id']==cutover['cutover_id'])) for cutover in edge['semantic_cutovers']],'portable_validation':observed['portable_validation'],'outcome':'passed','exit_code':0,'output_sha256':sha(output)}
        receipt_path=f'route-assets/edge-validation/{label}.json';doc(staging/receipt_path,receipt)
        edge['validation'].update(state='passed',report=desc(staging,receipt_path,label+'-validation'),output=desc(staging,output_path,label+'-output'))
        print(json.dumps({'edge':label,'outcome':'passed'}),flush=True)
    matrix_path=staging/'support-matrix.yaml'
    matrix_path.write_text(yaml.safe_dump(matrix,sort_keys=False),encoding='utf-8',newline='\n')
    matrix,matrix_bytes=load_route_matrix(matrix_path)
    terminal['matrix_sha256']=sha(matrix_bytes)
    terminal['route_evidence']=[]
    for route in matrix['routes']:
        resolution=resolve_upgrade_route(matrix,origin=route['origin'],target='v0.16.0',matrix_bytes=matrix_bytes,asset_root=staging,matrix_reference='.dev/releases/v0.16.0/support-matrix.yaml')
        assert resolution['route_kind']=='direct' and len(resolution['selected_route']['edges'])==1
        doc(staging/f"route-evidence/{route['origin']}-to-v0.16.0.json",resolution)
        route_path=f"route-evidence/{route['origin']}-to-v0.16.0.json"
        terminal['route_evidence'].append({'path':route_path,'sha256':sha((staging/route_path).read_bytes())})
    negatives=[]
    def protected(target):
        return sha(canonical_json({path.relative_to(target).as_posix():sha(path.read_bytes()) for path in sorted(target.rglob('*')) if path.is_file() and '.git' not in path.relative_to(target).parts}).encode())
    for route in matrix['routes']:
        origin=route['origin'];target=args.actual_dir/'work'/f'{origin}-pristine-resume'
        assert target.is_dir()
        before=protected(target)
        for kind in ('ambiguous-route','missing-route-archive','tampered-route-archive-identity'):
            invalid=deepcopy(matrix)
            selected=next(item for item in invalid['routes'] if item['origin']==origin)
            if kind=='ambiguous-route':
                duplicate=deepcopy(selected);duplicate['route_id']+='-duplicate';invalid['routes'].append(duplicate)
            elif kind=='missing-route-archive':
                selected['edges'][0]['artifacts']['archive']['path']='route-assets/missing-origin-archive.zip'
            else:
                selected['edges'][0]['artifacts']['archive']['sha256']='0'*64
            invalid_bytes=yaml.safe_dump(invalid,sort_keys=False).encode()
            result=resolve_upgrade_route(invalid,origin=origin,target='v0.16.0',matrix_bytes=invalid_bytes,asset_root=staging,matrix_reference='negative-probe-matrix.yaml')
            assert result['route_kind']=='reconciliation-required' and protected(target)==before
            negatives.append({'origin':origin,'case':kind,'outcome':'passed','protected_target_sha256':before,'resolution':result})
    doc(staging/'route-assets/route-negative-execution.json',{'schema_version':'direct-route-negative-execution/v1','subject_sha':args.subject_sha,'outcome':'passed','cases':negatives})
    terminal['route_negative_evidence']={'path':'route-assets/route-negative-execution.json','sha256':sha((staging/'route-assets/route-negative-execution.json').read_bytes())}
    assert subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()==args.subject_sha
    assert not subprocess.check_output(['git','status','--porcelain'],text=True).strip()
    terminal['outcome']='passed'
except Exception as exc:
    terminal['failure']={'type':type(exc).__name__,'message':'Staged edge execution or canonical receipt validation failed; inspect retained edge output.'}
finally:
    terminal.update(completed_at=now(),duration_seconds=round(time.monotonic()-begin,3))
    doc(staging/'edge-execution-terminal.json',terminal)
print(json.dumps({'outcome':terminal['outcome'],'edges':len(terminal['edges'])}))
raise SystemExit(terminal['outcome']!='passed')
