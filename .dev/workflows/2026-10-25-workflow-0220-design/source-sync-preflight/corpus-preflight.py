"""Disposable full-corpus preflight; first verify F: is the ready RAMDRIVE.

Never use this synthetic store for production or dispatch its prepared requests.
The retained procedure corrects the initial harness's restore-state field.
"""
import hashlib,json,sqlite3,subprocess,sys,tempfile,time
from pathlib import Path
root=Path(r'C:\Github\YuChia\ai-collaboration-prompts-dotnet-backend')
sys.path.insert(0,str(root/'src/skills/workflow-records/tools'))
from workflow_records.source_store import SourceStore,TABLES
from workflow_records import WorkflowRecords
from workflow_records import source_contract as c
scratch=Path(r'F:\tmp\aicf-416-source-sync\corpus-preflight');scratch.mkdir(exist_ok=True)
run=Path(tempfile.mkdtemp(prefix='run-',dir=scratch))
commit='f701105059bfc180dc5c212122e2fed939fdf664'
started=time.monotonic()
def git(*args,data=None):
 return subprocess.run(['git','-C',str(root),*args],input=data,stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=True,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0)).stdout
code_head=git('rev-parse','HEAD').decode().strip()
entries=[]
for row in git('ls-tree','-r','-l','-z',commit,'--','.dev/workflows').split(b'\0'):
 if not row:continue
 h,p=row.split(b'\t',1);mode,kind,oid,size=h.split();assert kind==b'blob'
 entries.append((p.decode(),mode.decode(),oid.decode(),int(size)))
raw=git('cat-file','--batch',data=('\n'.join(row[2] for row in entries)+'\n').encode())
offset=0;expected={}
for path,mode,oid,size in entries:
 end=raw.index(b'\n',offset);header=raw[offset:end].decode().split();assert header==[oid,'blob',str(size)]
 offset=end+1;blob=raw[offset:offset+size];offset+=size;assert raw[offset:offset+1]==b'\n';offset+=1
 expected[path]={'path':path,'mode':mode,'size':size,'sha256':c.digest(blob)}
assert offset==len(raw);del raw
units=sorted({p.split('/')[2] for p in expected if len(p.split('/'))>3})
assert len(units)==219 and len(expected)==1931 and sum(v['size'] for v in expected.values())==19427197
ref={'provider_id':'local','store_id':'corpus-proof'}
config={'contract_version':'workflow-records/1','default_provider':'local','stores':{'local':{'kind':'local','store_id':ref['store_id'],'repository_id':'framework-corpus-proof','database':str(run/'source.sqlite'),'busy_timeout_ms':1000}}}
source=SourceStore(root,config);native=WorkflowRecords(root,config)
def ok(response):
 if response.get('status')!='ok':raise RuntimeError(json.dumps(response,ensure_ascii=False))
 return response['result']
def call(op,**fields):return ok(source.execute({'contract_version':c.PROFILE,'operation':op,'store_ref':ref,**fields}))
def nc(op,**fields):return ok(native.execute({'contract_version':'workflow-records/1','operation':op,'store_ref':ref,**fields}))
call('source-init',operation_id='corpus-init',schema_version=c.SCHEMA)
call('replica-bind',operation_id='corpus-bind',new_source_namespace=True,binding={'binding_id':'corpus-board','binding_revision':1,'source_id':'synthetic-corpus-no-dispatch','project_ref':{'store_id':'synthetic','namespace':'personal','project_id':'synthetic'}})
print(json.dumps({'stage':'start','run':str(run),'source_commit':commit,'expected_files':len(expected),'expected_bytes':19427197}),flush=True)
seen={};snapshots=[]
for i,unit in enumerate(units+['workflow-index']):
 kind='archive-workflow' if i<len(units) else 'archive-root-index';prefix='.dev/workflows/'+unit if kind=='archive-workflow' else '.dev/workflows'
 result=call('source-import-git',operation_id='corpus-'+hashlib.sha256((kind+'\0'+unit).encode()).hexdigest(),kind=kind,workflow_id=unit,source_commit=commit,source_root=prefix)
 view=call('source-read',snapshot_id=result['snapshot_id']);assert view['workflow_id']==unit and view['kind']==kind and view['synchronization']['state']=='incomplete'
 assert len(view['synchronization']['targets'])==1 and view['synchronization']['targets'][0]['state']=='pending'
 for f in view['manifest']['files']:
  path=prefix+'/'+f['path'];assert path not in seen and expected[path]=={**f,'path':path},path
  seen[path]=f
 snapshots.append(result['snapshot_id'])
 if (i+1)%25==0 or i+1==220:print(json.dumps({'stage':'import','units':i+1,'files':len(seen),'elapsed_seconds':round(time.monotonic()-started,3)}),flush=True)
assert set(seen)==set(expected)
exported=nc('export',destination=str(run/'full.backup.json'))
print(json.dumps({'stage':'export','result':exported,'elapsed_seconds':round(time.monotonic()-started,3)}),flush=True)
preflight=nc('preflight',archive=str(run/'full.backup.json'),archive_digest=exported['archive_digest'])
restored_config=json.loads(json.dumps(config));restored_config['stores']['local']['database']=str(run/'restored.sqlite')
restored_native=WorkflowRecords(root,restored_config)
restore=ok(restored_native.execute({'contract_version':'workflow-records/1','operation':'restore','store_ref':ref,'operation_id':'corpus-restore','archive':str(run/'full.backup.json'),'archive_digest':exported['archive_digest']}))
assert restore['state']=='applied' and restore['store_state']=='inactive',restore
with sqlite3.connect(run/'source.sqlite') as a,sqlite3.connect(run/'restored.sqlite') as b:
 counts={}
 for name in TABLES:
  aa=a.execute('SELECT * FROM '+name+' ORDER BY 1,2').fetchall();bb=b.execute('SELECT * FROM '+name+' ORDER BY 1,2').fetchall();assert aa==bb,name;counts[name]=len(aa)
 first_intent=a.execute('SELECT id FROM replica_intents ORDER BY sequence LIMIT 1').fetchone()[0]
 refuse=SourceStore(root,restored_config).execute({'contract_version':c.PROFILE,'operation':'replica-prepare','store_ref':ref,'intent_id':first_intent})
 assert refuse['status']=='error' and refuse['error']['code']=='store_inactive',refuse
 assert a.execute('SELECT count(*) FROM replica_observations').fetchone()[0]==0
summary={'status':'passed','code_head':code_head,'source_commit':commit,'archive_units':220,'workflow_units':219,'files':len(seen),'raw_bytes':sum(v['size'] for v in seen.values()),'source_tables':counts,'archive_bytes':(run/'full.backup.json').stat().st_size,'archive_digest':exported['archive_digest'],'restored_state':'inactive','exact_source_table_restore':True,'remote_dispatches':0,'run_directory':str(run),'elapsed_seconds':round(time.monotonic()-started,3)}
(run/'summary.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8');print(json.dumps(summary),flush=True)
