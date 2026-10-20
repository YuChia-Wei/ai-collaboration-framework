"""Disposable-fixture public CLI exercise, including process termination."""
from pathlib import Path
import subprocess,json,sys,time,hashlib
out=Path(sys.argv[1]); action=sys.argv[2]; req=json.loads((out/'plan-request.json').read_bytes())
assert Path(req['project_root']).resolve().is_relative_to(Path('C:/tmp/mig202').resolve()), 'fixture roots only'
cli=Path(req['engine_root'])/'src/tools/maintain_framework.py'
def write(path,value): path.write_bytes((json.dumps(value,ensure_ascii=False,sort_keys=True,indent=2)+'\n').encode())
def call(label,request):
 write(out/(label+'-request.json'),request)
 r=subprocess.run([sys.executable,'-I','-B',str(cli)],input=json.dumps(request).encode(),capture_output=True,timeout=180)
 (out/(label+'-response.json')).write_bytes(r.stdout);(out/(label+'-stderr.txt')).write_bytes(r.stderr)
 assert r.returncode==0,(r.returncode,r.stdout.decode(),r.stderr.decode())
 return json.loads(r.stdout)
if action=='plan':
 r=call('plan',req); print(json.dumps({k:v for k,v in r.items() if k!='plan'})); print('scope',r['plan']['maintenance_scope'])
elif action in ('apply','interrupt'):
 plan=json.loads((out/'plan-response.json').read_bytes())
 req.update(operation='apply',expected_plan_sha256=plan['plan_sha256'],maintenance=dict(declared_by='project-owner',declaration_reference='2026-10-21 authorized isolated migration rehearsal; sole fixture writer',affected_capabilities=plan['plan']['maintenance_scope'],sessions_stopped=True,tools_stopped=True,external_writers_stopped=True))
 if action=='apply': print(json.dumps(call('apply',req)))
 else:
  write(out/'apply-request.json',req)
  with (out/'apply-response.json').open('wb') as stdout,(out/'apply-stderr.txt').open('wb') as stderr:
   proc=subprocess.Popen([sys.executable,'-I','-B',str(cli)],stdin=subprocess.PIPE,stdout=stdout,stderr=stderr)
   proc.stdin.write(json.dumps(req).encode());proc.stdin.close()
   watch=Path(req['project_root'])/'.agents/skills/adr-author/SKILL.md'
   started=time.monotonic(); killed=False
   while proc.poll() is None and time.monotonic()-started<120:
    if watch.exists(): proc.terminate();killed=True;break
    time.sleep(.001)
   if proc.poll() is None and not killed: proc.terminate()
   code=proc.wait(timeout=15)
  evidence=dict(killed_after_payload=killed,exit_code=code,observed_path=str(watch),payload_exists=watch.exists())
  write(out/'termination.json',evidence);print(json.dumps(evidence));assert killed
elif action=='recover':
 operations=list((out/'recovery').glob('*/operation.json'));assert len(operations)==1
 op=operations[0];project=Path(req['project_root']); sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest() if p.exists() else None
 apply=json.loads((out/'apply-request.json').read_bytes())
 recover=dict(api_version=2,operation='recover',project_root=str(project),engine_root=req['engine_root'],engine=req['engine'],operation_root=str(op.parent),operation_sha256=sha(op),direction='restore',expected_lock_sha256=sha(project/'.ai/framework.lock'),expected_marker_sha256=sha(project/'.ai/framework.operation'),maintenance=apply['maintenance'])
 print(json.dumps(call('recover',recover)))
elif action=='inspect':
 inspect={k:req[k] for k in ['api_version','project_root','engine_root','engine','candidate_root']};inspect['operation']='inspect'
 print(json.dumps(call('inspect',inspect)))
