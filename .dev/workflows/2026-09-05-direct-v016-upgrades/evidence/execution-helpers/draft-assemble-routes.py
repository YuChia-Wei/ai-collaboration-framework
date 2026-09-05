"""Stage source-only direct-route evidence from one completed real execution.

This preparer does not run validators or mark a release validated. The default
destination must be ignored staging; root owns any later tracked integration.
"""
from pathlib import Path
import argparse,hashlib,json,shutil,zipfile
import yaml

ROOT=Path.cwd()
LOCAL=ROOT/'.dev/ai-context/local/validation/issue-272'
VERSION='v0.16.0'
PACKAGE='ai-collaboration-framework-'+VERSION
ORIGINS={
    'v0.15.1': (ROOT/'.dev/workflows/2026-09-05-published-asset-identity/evidence/published-routes/route-assets/v0.15.1'/ 'ai-collaboration-framework-v0.15.1.zip','f2b5fa7c13550efaeb65ab9fcaeb0403baa2a5af'),
    'v0.9.0': (LOCAL/'origins/v0.9.0/ai-context-dotnet-backend-v0.9.0.zip','c14a3260cba7d0a9e2b67b73df9e221280d2d2ef'),
    'v0.6.0': (LOCAL/'origins/v0.6.0/ai-context-dotnet-backend-v0.6.0.zip','8b98b5f917513f2d143f42a322050a1162bb63f9'),
}
def require(condition,reason):
    if not condition: raise ValueError(reason)
def sha(raw): return hashlib.sha256(raw).hexdigest()
def canonical(value): return json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()
def write_yaml(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(yaml.safe_dump(value,sort_keys=False),encoding='utf-8',newline='\n')
def write_bytes(path,raw):
    path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(raw)
def descriptor(destination,path,asset_id):
    return {'asset_id':asset_id,'path':path,'sha256':sha((destination/path).read_bytes())}
def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--package-dir',type=Path,required=True)
    parser.add_argument('--actual-dir',type=Path,required=True)
    parser.add_argument('--destination',type=Path,required=True)
    args=parser.parse_args()
    destination=args.destination.resolve();actual=args.actual_dir.resolve()
    require(destination.is_relative_to(LOCAL.resolve()) and not destination.exists(),'fresh ignored staging destination required')
    terminal=json.loads((actual/'terminal.json').read_bytes())
    require(terminal.get('outcome')=='passed' and len(terminal.get('cases',[]))==9,'actual matrix has not passed all cases')
    archive=args.package_dir/(PACKAGE+'.zip')
    require(sha(archive.read_bytes())==terminal['archive_sha256'],'candidate and actual subject differ')
    destination.mkdir(parents=True)
    for extension in ('.zip','.zip.sha256','.tar.gz','.tar.gz.sha256'):
        source=args.package_dir/(PACKAGE+extension)
        write_bytes(destination/'route-assets/admitted'/source.name,source.read_bytes())
    with zipfile.ZipFile(archive) as opened:
        package=yaml.safe_load(opened.read(PACKAGE+'/metadata/package.yaml'))
        for name in ('files.yaml','migration.yaml','package.yaml','validation.json','selected-inputs.json'):
            write_bytes(destination/'route-assets/incoming/metadata'/name,opened.read(PACKAGE+'/metadata/'+name))
    require(package['source']==terminal['package_source'],'package source and actual terminal differ')
    actual_destination=destination/'route-assets/actual'
    write_bytes(actual_destination/'terminal.json',(actual/'terminal.json').read_bytes())
    for case in terminal['cases']:
        require(case.get('outcome')=='passed' and case.get('artifacts'),'case retained evidence missing')
        for name,record in case['artifacts'].items():
            relative=f"evidence/{case['case']}/{name}"
            require(record['path']==relative and Path(name).name==name,'invalid retained case path')
            raw=(actual/relative).read_bytes();require(sha(raw)==record['sha256'],'actual artifact digest differs')
            write_bytes(actual_destination/relative,raw)
    validator=(LOCAL/'draft-direct-edge.py').read_text(encoding='utf-8')
    validator=validator.replace('REPLACE_ARCHIVE_DIGEST',terminal['archive_sha256']).replace('REPLACE_ACTUAL_DIGEST',sha((actual/'terminal.json').read_bytes()))
    write_bytes(destination/'route-assets/validate-v016-direct-edge.py',validator.encode())
    identity={'package_id':package['package_id'],'release_id':package['release_id'],'payload_fingerprint':package['identity']['payload_fingerprint']}
    matrix={'schema_version':'1.1','matrix_id':'upgrade-route-matrix-'+VERSION,
        'target':{'version':VERSION,'release_id':'REL-'+VERSION,'commit':package['source']['commit'],
            'manifest':descriptor(destination,'route-assets/incoming/metadata/files.yaml',VERSION+'-admitted-files-manifest'),'package_identity':identity},
        'retained_origins':[],
        'semantic_cutovers':[{'cutover_id':'retained-direct-upgrade-v1','required':True,
            'description':'Direct component and provider selection preservation, package naming transition, target-owned semantic customization reconciliation, source-specific managed removals and retired skills, commit grammar adoption, effective rule regeneration, approved remediation packet, target validation before provenance, and durable resume or rollback.'}],
        'routes':[],'deprecations':[]}
    for origin,(origin_archive,commit) in ORIGINS.items():
        with zipfile.ZipFile(origin_archive) as opened:
            names=[name for name in opened.namelist() if name.endswith('/metadata/files.yaml')]
            require(len(names)==1,'origin manifest is ambiguous')
            manifest_raw=opened.read(names[0])
        origin_manifest=f'route-assets/origins/{origin}/metadata/files.yaml'
        write_bytes(destination/origin_manifest,manifest_raw)
        matrix['retained_origins'].append({'role':'immediate-predecessor' if origin=='v0.15.1' else origin,'version':origin,'release_id':'REL-'+origin,'commit':commit,'manifest':descriptor(destination,origin_manifest,origin+'-published-files-manifest')})
        edge_id=origin+'-to-'+VERSION
        argv=['python','route-assets/validate-v016-direct-edge.py','--edge-id',edge_id,'--origin-version',origin,
            '--archive','route-assets/admitted/'+PACKAGE+'.zip','--checksum','route-assets/admitted/'+PACKAGE+'.zip.sha256',
            '--target-manifest','route-assets/incoming/metadata/files.yaml','--origin-manifest',origin_manifest,
            '--migration','route-assets/incoming/metadata/migration.yaml','--actual-evidence','route-assets/actual/terminal.json','--cutover-id','retained-direct-upgrade-v1']
        artifacts={key:descriptor(destination,path,VERSION+'-admitted-'+key) for key,path in {
            'archive':'route-assets/admitted/'+PACKAGE+'.zip','checksum':'route-assets/admitted/'+PACKAGE+'.zip.sha256',
            'manifest':'route-assets/incoming/metadata/migration.yaml','validator':'route-assets/validate-v016-direct-edge.py'}.items()}
        matrix['routes'].append({'route_id':edge_id+'-direct','origin':origin,'target':VERSION,
            'edges':[{'edge_id':edge_id,'order':1,'from_version':origin,'to_version':VERSION,'package_identity':identity,
                'artifacts':artifacts,'semantic_cutovers':[{'cutover_id':'retained-direct-upgrade-v1','state':'pending'}],
                'validation':{'state':'pending','validator_argv':argv}}]})
    write_yaml(destination/'support-matrix.pending.yaml',matrix)
    print(json.dumps({'outcome':'staged-only','destination':str(destination),'actual_sha256':sha((actual/'terminal.json').read_bytes())}))
if __name__=='__main__': main()
