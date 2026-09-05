"""Validate staged actual route artifacts before any tracked integration."""
from pathlib import Path
import argparse,hashlib,importlib.util,json,shutil,sys
import yaml
root=Path.cwd();sys.path.insert(0,str(root/'.ai/scripts'))
spec=importlib.util.spec_from_file_location('release_state',root/'.ai/scripts/validate-ai-context-release-state.py')
gate=importlib.util.module_from_spec(spec);spec.loader.exec_module(gate)
parser=argparse.ArgumentParser();parser.add_argument('--staging',type=Path,required=True);parser.add_argument('--view',type=Path,required=True)
args=parser.parse_args();staging=args.staging.resolve();view=args.view.resolve()
local=(root/'.dev/ai-context/local/validation/issue-272').resolve()
assert staging.is_relative_to(local) and view.is_relative_to(local) and not view.exists()
release_dir=view/'.dev/releases/v0.16.0'
release_dir.mkdir(parents=True)
for name in ('support-matrix.yaml','route-assets','route-evidence'):
    source=staging/name;destination=release_dir/name
    if source.is_dir():shutil.copytree(source,destination)
    else:shutil.copyfile(source,destination)
for source in (root/'.dev/releases').glob('v*/release.yaml'):
    destination=view/source.relative_to(root);destination.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,destination)
runner=Path('.github/scripts/validate-v016-direct-upgrades.py')
(view/runner).parent.mkdir(parents=True);shutil.copyfile(root/runner,view/runner)
release=yaml.safe_load((root/'.dev/releases/v0.16.0/release.yaml').read_bytes())
gate.validate_retained_origin_route_evidence(view,'v0.16.0',release['artifacts'],release['compatibility']['automatic_upgrade_sources'])
print(json.dumps({'gate':'retained-origin-route-evidence','outcome':'passed','matrix_sha256':hashlib.sha256((staging/'support-matrix.yaml').read_bytes()).hexdigest(),'candidate_provider_phase':'not-executed'}))
