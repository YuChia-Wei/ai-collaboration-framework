import hashlib,json,subprocess,sys,time
from datetime import datetime
from pathlib import Path
root=Path.cwd(); local=root/'.dev/ai-context/local/p34-checks'; local.mkdir(parents=True,exist_ok=True)
name=sys.argv[1]; command=sys.argv[2:]; destination=local/(name+'.json')
if destination.exists(): raise SystemExit('Refusing to overwrite retained attempt')
runner=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
refs=subprocess.check_output(['git','ls-files','--cached','--others','--exclude-standard','--','.ai','.dev/standards','requirements.txt'],text=True).splitlines()
inputs={ref:hashlib.sha256((root/ref).read_bytes()).hexdigest() for ref in sorted(set(refs)) if (root/ref).is_file()}
head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(); start=datetime.now().astimezone().isoformat(); tick=time.perf_counter()
result=subprocess.run(command,capture_output=True,text=True)
elapsed=time.perf_counter()-tick
log=local/(name+'.log'); log.write_text(result.stdout+result.stderr,encoding='utf-8',newline='\n')
after={ref:hashlib.sha256((root/ref).read_bytes()).hexdigest() if (root/ref).is_file() else None for ref in inputs}
record={'command':command,'head_provenance':head,'started_at':start,'completed_at':datetime.now().astimezone().isoformat(),
 'duration_seconds':elapsed,'exit_code':result.returncode,'runner_sha256_before':runner,'runner_unchanged':runner==hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
 'input_sha256':inputs,'input_drift':[ref for ref in inputs if inputs[ref]!=after[ref]],'log_sha256':hashlib.sha256(log.read_bytes()).hexdigest(),
 'execution_context':'working tree; HEAD alone is not validation identity'}
destination.write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
print(json.dumps({key:record[key] for key in ('command','exit_code','duration_seconds','input_drift')}),flush=True)
print((result.stdout+result.stderr)[-5500:],flush=True)
raise SystemExit(result.returncode)
