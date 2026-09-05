"""Release-input projection boundary tests; no publication or actual upgrade claims."""
import copy
import json
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from ai_context_package import PackageError, canonical_json_bytes, selected_input_document, sha256_bytes
from ai_context_release_projection import validate_selected_release_projection
from release_asset_identity import PROFILE, verify_source

VERSION='v0.16.0'
RELEASE_PATH=f'.dev/releases/{VERSION}/release.yaml'
def record():
    return {'schema_version':'1.0','release_id':'REL-'+VERSION,'version':VERSION,'status':'planned',
        'compatibility':{'minimum_source_version':'v0.6.0','breaking_changes':True,'automatic_upgrade_sources':['v0.6.0','v0.9.0','v0.15.1']},
        'distribution':{'profile_id':'dotnet-backend','package_id':'ai-collaboration-framework-'+VERSION},
        'planning':{'github_issue_refs':['#272']},'provider_reconciliation':{'included_work':{'prepublication':{'issue_state':'closed'}}},
        'validation':{'package_status':'planned','evidence':'pending'}}
def raw(value): return yaml.safe_dump(value,sort_keys=False).encode()

class ReleaseInputProjectionTests(unittest.TestCase):
    def test_built_archive_rebinds_after_source_acceptance_without_rebuilding(self):
        from test_ai_context_packaging import SyntheticPackageRepo, PACKAGE, git
        fixture = SyntheticPackageRepo()
        try:
            fixture.adopt_public_identity_policy()
            profile_path = fixture.root / fixture.profile
            profile = yaml.safe_load(profile_path.read_bytes())
            profile['exclusions'].append({'id':'release-lifecycle','classification':'source-only',
                'patterns':['.dev/releases/**'],'reason':'Match the governed source-only release boundary.'})
            profile_path.write_bytes(raw(profile))
            git(fixture.root, 'add', fixture.profile)
            git(fixture.root, 'commit', '-qm', 'source release boundary fixture')
            fixture.ensure_release('0.16.0')
            built = PACKAGE.build_package(fixture.root, 'HEAD', '0.16.0', fixture.output('projection-archive'), fixture.profile)
            archive = Path(built['zip'])
            archive_sha = sha256_bytes(archive.read_bytes())
            members = PACKAGE.validate_archive(archive)
            proof = json.loads(members[built['package_id'] + '/metadata/selected-inputs.json'][0])
            admission = {'selected_input_fingerprint': built['selected_input_fingerprint']}
            release_path = fixture.root / RELEASE_PATH
            accepted = yaml.safe_load(release_path.read_bytes())
            accepted.update(status='validated', validation={'package_status':'validated','evidence':'bounded source test acceptance'})
            release_path.write_bytes(raw(accepted))
            git(fixture.root, 'add', RELEASE_PATH)
            git(fixture.root, 'commit', '-qm', 'source acceptance fixture')
            verify_source(fixture.root, VERSION, 'HEAD', admission, proof)
            self.assertEqual(archive_sha, sha256_bytes(archive.read_bytes()))
            accepted['compatibility']['breaking_changes'] = False
            release_path.write_bytes(raw(accepted))
            git(fixture.root, 'add', RELEASE_PATH)
            git(fixture.root, 'commit', '-qm', 'changed compatibility fixture')
            with self.assertRaisesRegex(PackageError, 'selected inputs'):
                verify_source(fixture.root, VERSION, 'HEAD', admission, proof)
        finally:
            fixture.close()

    def test_progress_only_change_rebinds_same_admitted_input_subject(self):
        paths={PROFILE,RELEASE_PATH,'.ai/distribution/templates/INSTALL.md','.ai/distribution/templates/requirements.txt','.ai/distribution/identity-registry.yaml'}
        inputs={path:path.encode() for path in paths}
        original=record();inputs[RELEASE_PATH]=raw(original)
        selected=selected_input_document(inputs,[],[])
        self.assertEqual('package-selected-input/v2',selected['schema_version'])
        admission={'selected_input_fingerprint':sha256_bytes(canonical_json_bytes(selected))}
        final=copy.deepcopy(original)
        final.update(status='validated',updated_at='2026-09-05T12:00:00Z')
        final['validation']={'package_status':'validated','evidence':'retained actual execution'}
        inputs[RELEASE_PATH]=raw(final)
        snapshot=SimpleNamespace(tree={path:path for path in paths},blob_reader=None)
        with patch('release_asset_identity.PackageRepositorySnapshot.from_ref',return_value=snapshot), \
             patch('release_asset_identity.load_yaml_blob',return_value={'package':{'identity_registry':'.ai/distribution/identity-registry.yaml'}}), \
             patch('release_asset_identity.collect_payload',return_value=[]), \
             patch('release_asset_identity.git_blob',side_effect=lambda root,entry,reader:inputs[entry]):
            verify_source(Path('.'),VERSION,'b'*40,admission,selected)
            for key in ('compatibility','distribution','planning','provider_reconciliation','future_package_rule'):
                changed=copy.deepcopy(final)
                changed[key]=dict(changed.get(key,{}),changed_contract=True)
                inputs[RELEASE_PATH]=raw(changed)
                with self.subTest(key=key),self.assertRaisesRegex(PackageError,'selected inputs'):
                    verify_source(Path('.'),VERSION,'b'*40,admission,selected)

    def test_historical_release_input_remains_raw_byte_identity(self):
        path='.dev/releases/v0.15.1/release.yaml'
        first=selected_input_document({path:b'status: planned\n'},[],[])
        second=selected_input_document({path:b'status: validated\n'},[],[])
        self.assertEqual('package-selected-input/v1',first['schema_version'])
        self.assertNotEqual(first,second)
        self.assertEqual(sha256_bytes(b'status: planned\n'),first['source_inputs'][0]['sha256'])

    def test_unknown_projection_schema_missing_projection_and_digest_tamper_fail(self):
        proof=selected_input_document({RELEASE_PATH:raw(record())},[],[])
        validate_selected_release_projection(proof,VERSION)
        for change in ('missing','downgrade','unknown','digest','progress'):
            altered=copy.deepcopy(proof)
            if change=='missing': altered.pop('release_projection')
            elif change=='downgrade': altered['schema_version']='package-selected-input/v1'
            elif change=='unknown': altered['release_projection']['schema_version']='release-package-input/v99'
            elif change=='digest': altered['source_inputs'][0]['sha256']='a'*64
            else: altered['release_projection']['fields']['status']='validated'
            with self.subTest(change=change),self.assertRaises(ValueError):
                validate_selected_release_projection(altered,VERSION)

    def test_package_contract_disagreement_and_duplicate_authority_fail(self):
        release=record();proof=selected_input_document({RELEASE_PATH:raw(release)},[],[])
        package={'version':'0.16.0','profile_id':'dotnet-backend','package_id':release['distribution']['package_id'],
            'compatibility':{'minimum_governed_source':'v0.6.0','breaking_changes':True,'automatic_upgrade_sources':['v0.6.0','v0.9.0','v0.15.1']}}
        validate_selected_release_projection(proof,VERSION,package)
        package['compatibility']['automatic_upgrade_sources']=['v0.15.1']
        with self.assertRaisesRegex(ValueError,'incoming package contract'):
            validate_selected_release_projection(proof,VERSION,package)
        with self.assertRaisesRegex(PackageError,'duplicate'):
            selected_input_document({RELEASE_PATH:raw(release)+b'status: validated\n'},[],[])

if __name__=='__main__': unittest.main()
