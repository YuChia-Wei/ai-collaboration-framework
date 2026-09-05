"""Project completed local executions into the guarded acceptance ledger.

This file creates ignored runtime evidence only. Root separately owns release
record integration, provider admission and any public acceptance disposition.
"""
from pathlib import Path
import argparse,hashlib,json,subprocess
import yaml
root=Path.cwd();local=root/'.dev/ai-context/local/validation/issue-272'
def sha(raw):return hashlib.sha256(raw).hexdigest()
def digest(value):return sha(json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode())
def save(path,value):path.write_text(yaml.safe_dump(value,sort_keys=False),encoding='utf-8',newline='\n')
def ref(path):return 'ignored:'+path.relative_to(root).as_posix()
parser=argparse.ArgumentParser();parser.add_argument('--actual-dir',type=Path,required=True);parser.add_argument('--staging',type=Path,required=True)
args=parser.parse_args();actual=args.actual_dir.resolve();staging=args.staging.resolve()
actual_terminal=json.loads((actual/'terminal.json').read_bytes());edges_terminal=json.loads((staging/'edge-execution-terminal.json').read_bytes())
head=actual_terminal['subject_sha']
assert actual_terminal['outcome']=='passed' and len(actual_terminal['cases'])==9
assert edges_terminal['outcome']=='passed' and edges_terminal['subject_sha']==head
assert subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()==head
edge_command=edges_terminal.get('invocation')
assert isinstance(edge_command,list) and len(edge_command)==8 and all(isinstance(value,str) and value for value in edge_command),'edge invocation is missing or malformed'
assert edge_command[0]=='python' and Path(edge_command[1]).resolve()==local/'execute-staged-edges.py','edge invocation names another runner'
for flag,expected in (('--staging',staging),('--actual-dir',actual),('--subject-sha',head)):
    assert edge_command.count(flag)==1 and edge_command.index(flag)<len(edge_command)-1,'edge invocation flag is missing or ambiguous'
    value=edge_command[edge_command.index(flag)+1]
    assert (value if flag=='--subject-sha' else Path(value).resolve())==expected,'edge invocation input differs'
assert edges_terminal.get('runner_sha256')==sha((local/'execute-staged-edges.py').read_bytes()),'edge runner content differs'
assert actual_terminal.get('schema_version')=='direct-upgrade-execution/v1' and actual_terminal.get('evidence_kind')=='actual-isolated-target-execution','actual terminal authority differs'
assert edges_terminal.get('schema_version')=='staged-edge-execution/v1','edge terminal authority differs'
assert actual_terminal.get('runner',{}).get('sha256')==sha((root/'.github/scripts/validate-v016-direct-upgrades.py').read_bytes()),'actual runner content differs'
admission_path=local/'preparation-package-4-admission.json'
admission=json.loads(admission_path.read_bytes())
assert actual_terminal['archive_sha256']==next(asset['sha256'] for asset in admission['assets'] if asset['name'].endswith('.zip')),'actual archive is not admitted'
entries=[]
def executed(ids,terminal,path,command,profile):
    output_sha=sha(path.read_bytes())
    receipt={'schema_version':'1.0','record_type':'terminal-command-execution','producer':'external-task-completion','subject_sha':head,'command':command,'profile':profile,'started_at':terminal['started_at'],'completed_at':terminal['completed_at'],'duration_seconds':terminal['duration_seconds'],'executed':True,'synthetic':False,'outcome':'passed','exit_code':0,'evidence_refs':[ref(path)],'evidence_sha256':output_sha}
    receipt['receipt_sha256']=digest(receipt);receipt_path=local/(profile+'-execution-receipt.yaml');save(receipt_path,receipt)
    for identifier in ids:
        entries.append({'acceptance_id':identifier,'issue':272,'requires_actual_execution':True,'evidence_kind':'actual-execution','command':command,'profile':profile,'subject_sha':head,'outcome':'passed','evidence_refs':[ref(path)],'evidence_sha256':output_sha,'execution_receipt_ref':ref(receipt_path),'execution_receipt_file_sha256':sha(receipt_path.read_bytes()),'execution_receipt':receipt})
executed(['UPG006-AC2','UPG006-AC3','UPG006-AC4-target','UPG006-AC5'],actual_terminal,actual/'terminal.json',json.dumps(actual_terminal['invocation'],ensure_ascii=False),'retained-direct-upgrades')
executed(['UPG006-AC1','UPG006-AC4-route'],edges_terminal,staging/'edge-execution-terminal.json',json.dumps(edge_command,ensure_ascii=False),'retained-direct-edges')
def document(identifier,paths,outcome,command):
    hashes={path.as_posix():sha((root/path).read_bytes()) for path in paths}
    entries.append({'acceptance_id':identifier,'issue':272,'requires_actual_execution':False,'evidence_kind':'document','command':command,'profile':'source-evidence-review','subject_sha':head,'outcome':outcome,'evidence_refs':['tracked:'+path.as_posix() for path in paths],'evidence_sha256':digest(hashes),'execution_receipt_ref':None,'execution_receipt_file_sha256':None,'execution_receipt':None})
document('UPG006-AC6',[Path('.dev/releases/v0.16.0/migration-guide.md'),Path('.dev/standards/AI-CONTEXT-SOURCE-RELEASE-POLICY.md')],'passed','Read source-specific migration entrypoint and prospective retained-support policy')
entries.append({'acceptance_id':'UPG006-AC7','issue':272,'requires_actual_execution':False,'evidence_kind':'document','command':'Evaluate exact local asset admission; final current-source/provider admission and public acceptance remain pending','profile':'release-readiness','subject_sha':head,'outcome':'deferred','evidence_refs':[ref(admission_path)],'evidence_sha256':sha(admission_path.read_bytes()),'execution_receipt_ref':None,'execution_receipt_file_sha256':None,'execution_receipt':None})
projection=[{key:entry[key] for key in ('acceptance_id','outcome','evidence_sha256')} for entry in entries]
ledger={'schema_version':'1.0','record_type':'acceptance-evidence-ledger','subject_sha':head,'entries':entries,'human_report':{'entries':projection,'report_sha256':digest(projection)}}
ledger['ledger_sha256']=digest(ledger);save(local/'acceptance-ledger.yaml',ledger)
print(json.dumps({'ledger_sha256':ledger['ledger_sha256'],'entries':len(entries),'release_readiness':'deferred'}))
