#!/usr/bin/env python3
"""Validate one v0.16 direct edge and bind retained actual target execution."""
from pathlib import Path, PurePosixPath
import argparse, hashlib, importlib, json, os, sys, tempfile, zipfile
import yaml
sys.dont_write_bytecode = True
EXPECTED_ARCHIVE = 'd136b69e4153e7c85f892871fb0d3e6c5d8f88c7fd89d43fdb1b03ca88c5c85d'
EXPECTED_ACTUAL = '14a981794188b728c5b659050cf9f2a950cfcb113b5fe97ad0aff9ad1823619f'
ORIGINS = {
    'v0.6.0': '20ca69ef4e1b4085476a2b15eeba93da7a75ea580fd2ab9f6c8815938b0af3be',
    'v0.9.0': 'c293247612eb2f01ef42e4d7c55be4ff36201cdf034157c518de871ec2acb5c7',
    'v0.15.1': '8edcb120fe00b16e803f161ec31861ff45a30d8697a5a3e5c58931f7f2b5d1ad',
}
def sha(raw): return hashlib.sha256(raw).hexdigest()
def require(condition, message):
    if not condition: raise ValueError(message)
def asset(value):
    pure=PurePosixPath(value)
    require(not pure.is_absolute() and '..' not in pure.parts and ':' not in value and '\\' not in value, 'unsafe asset path')
    path=Path(value)
    require(path.is_file() and not path.is_symlink() and path.resolve().is_relative_to(Path.cwd().resolve()), 'unavailable contained asset')
    return path

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    for flag in ('edge-id','origin-version','archive','checksum','target-manifest','origin-manifest','migration','actual-evidence','cutover-id'):
        parser.add_argument('--'+flag, required=True)
    args=parser.parse_args()
    require(args.origin_version in ORIGINS and args.edge_id==args.origin_version+'-to-v0.16.0', 'wrong direct origin edge')
    require(args.cutover_id=='retained-direct-upgrade-v1', 'wrong semantic cutover')
    archive=asset(args.archive); actual=asset(args.actual_evidence)
    require(sha(archive.read_bytes())==EXPECTED_ARCHIVE, 'archive differs from admitted bytes')
    require(asset(args.checksum).read_text().split()==[EXPECTED_ARCHIVE,archive.name], 'checksum differs')
    require(sha(actual.read_bytes())==EXPECTED_ACTUAL, 'actual execution terminal differs')
    terminal=json.loads(actual.read_bytes())
    require(terminal['outcome']=='passed' and terminal['evidence_kind']=='actual-isolated-target-execution' and terminal['archive_sha256']==EXPECTED_ARCHIVE, 'actual execution not admitted or passed')
    cases=[case for case in terminal['cases'] if case['origin']==args.origin_version]
    require({case['case'] for case in cases}=={args.origin_version+s for s in ('-pristine-resume','-customized-none','-customized-rollback')}, 'actual origin cases incomplete')
    require(all(case['outcome']=='passed' for case in cases), 'actual origin case failed')
    for case in cases:
        if case['recovery']=='rolled-back':
            require(case['prestate_sha256']==case['poststate_sha256'], 'rollback differs')
        else:
            require(case['finalization']['status']=='finalized' and case['finalization']['effective_rule_readiness']['action_ready'] and case['target_validation']['exit_code']==0, 'target upgrade incomplete')
    origin_raw=asset(args.origin_manifest).read_bytes()
    require(sha(origin_raw)==ORIGINS[args.origin_version], 'origin manifest differs from exact public asset')
    with tempfile.TemporaryDirectory(prefix='v016-edge-') as directory:
        root=Path(directory)
        with zipfile.ZipFile(archive) as opened:
            seen=set()
            for member in opened.infolist():
                pure=PurePosixPath(member.filename)
                require(not pure.is_absolute() and '..' not in pure.parts and ':' not in member.filename and '\\' not in member.filename and member.filename not in seen, 'unsafe archive member')
                seen.add(member.filename)
                require(((member.external_attr>>16)&0o170000)!=0o120000, 'archive symlink')
                destination=root/member.filename
                if member.is_dir(): destination.mkdir(parents=True,exist_ok=True)
                else:
                    destination.parent.mkdir(parents=True,exist_ok=True);destination.write_bytes(opened.read(member));destination.chmod((member.external_attr>>16)&0o777)
        incoming=root/'ai-collaboration-framework-v0.16.0'
        sys.path.insert(0,str(incoming/'payload/.ai/scripts'))
        apply=importlib.import_module('ai_context_package_apply')
        package,_,migration,manifest_sha=apply.validate_package_root(incoming)
        require(package['version']=='0.16.0' and package['source']==terminal['package_source'], 'package source disagrees with actual execution')
        require(asset(args.target_manifest).read_bytes()==(incoming/'metadata/files.yaml').read_bytes(), 'copied target manifest differs')
        require(asset(args.migration).read_bytes()==(incoming/'metadata/migration.yaml').read_bytes(), 'copied migration differs')
        require([item['manifest_sha256'] for item in migration['sources'] if item['version']==args.origin_version[1:]] == [ORIGINS[args.origin_version]], 'direct origin migration missing')
        observed=apply.incoming_package_validation(incoming,package)
    portable={'schema_version':'incoming-package-validation/v1','authority':{'kind':observed['authority'],'manifest':{'path':observed['manifest_path'],'sha256':observed['manifest_sha256']},'validator':{'path':observed['path'],'sha256':observed['sha256'],'argv':observed['argv']}},'package_identity':{'package_id':package['package_id'],'release_id':package['release_id'],'payload_fingerprint':package['identity']['payload_fingerprint']},'execution':observed['execution']}
    reason='Retained owner-policy baseline' if args.origin_version=='v0.6.0' else ('Retained owner-policy origin' if args.origin_version=='v0.9.0' else 'Immediate previous governed package')
    result={'edge_id':args.edge_id,'from_version':args.origin_version,'to_version':'v0.16.0','archive_sha256':EXPECTED_ARCHIVE,'origin_manifest_sha256':ORIGINS[args.origin_version],'target_manifest_sha256':manifest_sha,'reason':reason+'; one direct migration with actual pristine resume, customized finalization and exact rollback evidence.','portable_validation':portable,'actual_upgrade':{'evidence_path':args.actual_evidence,'sha256':EXPECTED_ACTUAL,'outcome':'passed','cases':[case['case'] for case in cases]}}
    print(json.dumps(result,sort_keys=True,separators=(',',':')))

if __name__=='__main__':
    try: main()
    except Exception as exc:
        print(json.dumps({'error_type':type(exc).__name__,'outcome':'failed'}),file=sys.stderr)
        raise SystemExit(1)
