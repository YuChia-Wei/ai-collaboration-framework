#!/usr/bin/env python3
"""Independent behavior expectations for catalog and target authoring."""
from __future__ import annotations
import copy
import json
import shutil
import subprocess
import sys
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_artifact_authoring import AUTHOR, AuthoringFixture, NOW, ROOT
from test_provider_role_projection_contract import ProviderRoleProjectionFixture
import artifact_lifecycle as LIFECYCLE


class CatalogAuthoringTests(AuthoringFixture):
    def setUp(self):
        super().setUp()
        for name in AUTHOR.ROLE_RUNTIME:
            self.put('.ai/scripts/' + name, (ROOT / '.ai/scripts' / name).read_bytes())
        fixture = ProviderRoleProjectionFixture()
        self.addCleanup(fixture.close)
        shutil.copytree(fixture.root, self.root, dirs_exist_ok=True)
        for ref, *_ in list(AUTHOR.CATALOGS.values())[:3]:
            schema = ref.removesuffix('.yaml') + '.schema.yaml'
            self.put(schema, (ROOT / schema).read_bytes())
        self.put('.ai/assets/shared/ROLE-EXECUTION-CONTRACT.md', (ROOT / '.ai/assets/shared/ROLE-EXECUTION-CONTRACT.md').read_bytes())

    def request(self, identity='provider-neutral-capabilities', record='mechanical-evidence-worker', **changes):
        return {'version':'1.0','operation':'catalog.update','timestamp':NOW,'id':identity,'record':record,
                'changes':changes or {'capability_tags':['deterministic-evidence','bounded-inventory']}}

    def test_three_catalogs_validate_projected_data_without_invocation_claims(self):
        requests = [self.request(), self.request('provider-projections','claude',deferred_reason='No configured projection; support remains deferred.'),
                    self.request('upgrader-role-bindings', stop_and_escalation=['Return unresolved input references to the owning skill.'])]
        for request in requests:
            with self.subTest(identity=request['id']):
                before = self.snapshot(); first = AUTHOR.plan(self.root,request)
                self.assertEqual(first.digest,AUTHOR.plan(self.root,request).digest)
                self.assertEqual(before,self.snapshot())
                self.assertEqual({AUTHOR.CATALOGS[request['id']][0]},set(first.changes))
                AUTHOR.apply(self.root,request,first.digest)
        data=self.load(AUTHOR.CATALOGS['provider-projections'][0])
        self.assertEqual({'availability':'unknown','invocation_evidence':'not-claimed'},data['current_session'])

    def test_protected_fields_and_unknown_source_keys_refuse_before_writes(self):
        before=self.snapshot()
        for changes in ({'role_path':'elsewhere.yaml'},{'schema_version':'2.0'},{'capability_tags':True}):
            with self.subTest(changes=changes), self.assertRaises(AUTHOR.AuthoringError): AUTHOR.plan(self.root,self.request(**changes))
        self.assertEqual(before,self.snapshot())
        ref=AUTHOR.CATALOGS['provider-neutral-capabilities'][0]; data=self.load(ref); data['owner_extension']={'preserve':True}
        self.put(ref,AUTHOR.dump(data)); before=self.snapshot()
        with self.assertRaises(AUTHOR.AuthoringError): AUTHOR.plan(self.root,self.request())
        self.assertEqual(before,self.snapshot())

    def test_context_authority_and_directory_membership_bind_preview(self):
        for mutation in ('schema','owner','directory'):
            with self.subTest(mutation=mutation):
                request=self.request(); preview=AUTHOR.plan(self.root,request)
                if mutation=='schema': ref=AUTHOR.CATALOGS[request['id']][0].removesuffix('.yaml')+'.schema.yaml'; value=(self.root/ref).read_bytes()+b'\n'
                elif mutation=='owner': ref='.ai/assets/skills/extra-owner/skill.yaml'; value=b'asset_id: extra-owner\nstatus: inactive\n'
                else: ref='.codex/agents/notes.txt'; value=b'directory member'
                old=(self.root/ref).read_bytes() if (self.root/ref).is_file() else None
                self.put(ref,value)
                with self.assertRaises(AUTHOR.AuthoringError): AUTHOR.apply(self.root,request,preview.digest)
                if old is None: (self.root/ref).unlink()
                else: self.put(ref,old)

    def test_recovery_restores_exact_catalog_bytes_and_refuses_external_edits(self):
        request=self.request(); preview=AUTHOR.plan(self.root,request); ref=next(iter(preview.changes)); original=(self.root/ref).read_bytes()
        rename=Path.rename
        def interrupt(path,destination):
            if path.name.endswith('.pending.json'): raise OSError('injected completion interruption')
            return rename(path,destination)
        with mock.patch.object(Path,'rename',interrupt), self.assertRaises(AUTHOR.AuthoringError): AUTHOR.apply(self.root,request,preview.digest)
        journal=next((self.root/AUTHOR.LOCAL).glob('*.pending.json')); candidate=(self.root/ref).read_bytes()
        self.put(ref,candidate+b'\n')
        with self.assertRaises(AUTHOR.AuthoringError): AUTHOR.recover(self.root,journal)
        self.put(ref,candidate); AUTHOR.recover(self.root,journal)
        self.assertEqual(original,(self.root/ref).read_bytes())

    def test_disjoint_catalog_checks_do_not_claim_workflow_admission(self):
        self.put('.dev/workflows/bad/workflow.yaml',b'malformed: retained unrelated data\n')
        preview=AUTHOR.plan(self.root,self.request())
        self.assertEqual({AUTHOR.CATALOGS['provider-neutral-capabilities'][0]},set(preview.changes))
        with self.assertRaises(AUTHOR.AuthoringError): AUTHOR.plan(self.root,self.workflow())


class TargetSelectionAuthoringTests(AuthoringFixture):
    ref='.dev/project-config.yaml'
    def setUp(self):
        super().setUp()
        for ref in (*AUTHOR.TARGET_SCHEMAS, *('.ai/scripts/'+name for name in AUTHOR.ROLE_RUNTIME)):
            self.put(ref,(ROOT/ref).read_bytes())
        template='.ai/assets/skills/ai-context-init/templates/project-config.template.yaml'
        self.put(template,(ROOT/template).read_bytes())
        data=json.loads((ROOT/'.ai/assets/skills/ai-context-init/templates/project-config.template.yaml').read_text())
        data['owner_extension']={'nested':[True,1,{'untouched':'yes'}]}
        self.put(self.ref,AUTHOR.dump(data,json_format=True)); self.put('decision.md',b'Fixture explicit decision; not a real owner approval.')

    def request(self):
        return {'version':'1.0','operation':'target.technology','timestamp':NOW,'id':'project-config',
                'selection':{'slot':'persistence.orm','value':{'Inventory':'EF Core','Orders':'Dapper'},'status':'selected',
                             'source':'explicit-target-decision','evidence':['decision.md'],'reason':'Preserve target bounded contexts.'}}

    def test_selection_upsert_and_binding_preserve_extensions_and_unrelated_choices(self):
        before=self.load(self.ref); request=self.request(); self.execute(request)
        data=self.load(self.ref); self.assertEqual(before['owner_extension'],data['owner_extension']); self.assertEqual(request['selection'],data['technologySelections'][0])
        data['technologySelections'][0]['target_extension']={'keep':42}; self.put(self.ref,AUTHOR.dump(data,json_format=True))
        request['selection']['reason']='Retain independent persistence decisions.'; self.execute(request)
        self.assertEqual({'keep':42},self.load(self.ref)['technologySelections'][0]['target_extension'])
        binding={'version':'1.0','operation':'target.work-binding','timestamp':NOW,'id':'project-config','mode':'required','merge_gate':'optional','decision_ref':'decision.md'}
        self.execute(binding); final=self.load(self.ref)
        self.assertEqual(['traceability','work-authorization'],final['workManagement']['workItemBinding']['purposes'])
        self.assertEqual('optional',final['workManagement']['workItemBinding']['mergeGate'])
        self.assertEqual(before['owner_extension'],final['owner_extension'])

    def test_invalid_selection_exact_version_and_stale_decision_fail_closed(self):
        for field,value in [('slot','no-dot'),('status','approved'),('source','inferred')]:
            request=self.request(); request['selection'][field]=value
            with self.subTest(field=field), self.assertRaises(AUTHOR.AuthoringError): AUTHOR.plan(self.root,request)
        data=self.load(self.ref); data['schemaVersion']=True; self.put(self.ref,AUTHOR.dump(data,json_format=True))
        with self.assertRaises(AUTHOR.AuthoringError): AUTHOR.plan(self.root,self.request())
        data['schemaVersion']=1; self.put(self.ref,AUTHOR.dump(data,json_format=True))
        request={'version':'1.0','operation':'target.work-binding','timestamp':NOW,'id':'project-config','mode':'required','merge_gate':'optional','decision_ref':'decision.md'}
        preview=AUTHOR.plan(self.root,request); self.put('decision.md',b'changed decision')
        with self.assertRaises(AUTHOR.AuthoringError): AUTHOR.apply(self.root,request,preview.digest)


class EvaluationCatalogAuthoringTests(AuthoringFixture):
    def setUp(self):
        super().setUp()
        manifest=AUTHOR.parse((ROOT/'.ai/evaluation/incident-mutants.yaml').read_text())
        refs={'.ai/scripts/validate-ai-behavior-evaluation.py'}
        for path in (ROOT/'.ai/evaluation').rglob('*.yaml'): refs.add(path.relative_to(ROOT).as_posix())
        refs.update(item['path'] for item in manifest['candidate_inputs'])
        for ref in refs: self.put(ref,(ROOT/ref).read_bytes())
        for item in manifest['candidate_inputs']: item['sha256']=AUTHOR.digest((self.root/item['path']).read_bytes())
        self.put('.ai/evaluation/incident-mutants.yaml',AUTHOR.dump(manifest))

    def request(self,identity,record,changes):
        return {'version':'1.0','operation':'catalog.update','timestamp':NOW,'id':identity,'record':record,'changes':changes}

    def test_corpus_reference_update_binds_independent_inputs_without_running_evaluation(self):
        self.put('.ai/evaluation/fixtures/alternate.yaml',(ROOT/'.ai/evaluation/fixtures/empty-repository.yaml').read_bytes())
        request=self.request('evaluation-corpus','empty-repository',{'input':'.ai/evaluation/fixtures/alternate.yaml'})
        before=self.snapshot(); preview=AUTHOR.plan(self.root,request)
        self.assertEqual(before,self.snapshot()); self.assertEqual({'.ai/evaluation/corpus-manifest.yaml'},set(preview.changes))
        self.put('.ai/evaluation/fixtures/alternate.yaml',b'changed: true\n')
        with self.assertRaises(AUTHOR.AuthoringError): AUTHOR.apply(self.root,request,preview.digest)
        request['changes']['input']='../outside.yaml'
        with self.assertRaises(AUTHOR.AuthoringError): AUTHOR.plan(self.root,request)

    def test_mutant_followup_preserves_detectors_and_rejects_digest_drift(self):
        ref='.ai/evaluation/incident-mutants.yaml'; original=self.load(ref)
        selected=next(row for row in original['mutants'] if row['criticality']=='exploratory')
        request=self.request('evaluation-mutants',selected['mutant_id'],{'follow_up':'Review structured extension handling separately.'})
        self.execute(request); expected=copy.deepcopy(original)
        next(row for row in expected['mutants'] if row['mutant_id']==selected['mutant_id'])['follow_up']=request['changes']['follow_up']
        self.assertEqual(expected,self.load(ref))
        request['changes']={'expected_detector':'fabricated'}
        with self.assertRaises(AUTHOR.AuthoringError): AUTHOR.plan(self.root,request)
        request['changes']={'follow_up':'Another explicit follow-up.'}
        self.put(original['candidate_inputs'][0]['path'],b'changed validator')
        with self.assertRaises(AUTHOR.AuthoringError): AUTHOR.plan(self.root,request)


class SourceCatalogAuthoringTests(AuthoringFixture):
    def setUp(self):
        super().setUp()
        for names in AUTHOR.CATALOG_RUNTIME.values():
            for name in names: self.put('.ai/scripts/'+name,(ROOT/'.ai/scripts'/name).read_bytes())
        ref='.ai/distribution/validators/product_identity_registry.py'
        self.put(ref,(ROOT/ref).read_bytes())

    def request(self,identity,record,changes):
        return {'version':'1.0','operation':'catalog.update','timestamp':NOW,'id':identity,'record':record,'changes':changes}

    def identity_fixture(self):
        from test_repository_identity import SyntheticIdentityRepository
        fixture=SyntheticIdentityRepository(); self.addCleanup(fixture.close); fixture.write_registry()
        for path in fixture.root.rglob('*'):
            if path.is_file() and '.git' not in path.relative_to(fixture.root).parts:
                self.put(path.relative_to(fixture.root).as_posix(),path.read_bytes())

    def test_identity_metadata_and_consumer_moves_validate_actual_content(self):
        self.identity_fixture()
        request=self.request('source-identities','technology-profile.dotnet-backend',{'display_name':'.NET/C# backend technology profile'})
        self.execute(request)
        registry=self.load(AUTHOR.CATALOGS['source-identities'][0])
        row=next(row for row in registry['consumer_contracts'] if row['kind']=='text-contains' and row['path']=='README.en.md')
        self.put('docs/product.md',b'# AI Collaboration Framework\n')
        request=self.request('identity-consumers',row['id'],{'path':'docs/product.md'})
        preview=AUTHOR.plan(self.root,request)
        self.put('docs/product.md',b'incorrect identity\n')
        with self.assertRaises(AUTHOR.AuthoringError): AUTHOR.apply(self.root,request,preview.digest)
        self.put('docs/product.md',b'# AI Collaboration Framework\n')
        self.execute(request)
        request['changes']={'selector':'forbidden'}
        with self.assertRaises(AUTHOR.AuthoringError): AUTHOR.plan(self.root,request)

    def test_identity_preview_binds_release_inventory_and_refuses_internal_links(self):
        self.identity_fixture()
        request=self.request('source-identities','technology-profile.dotnet-backend',{'display_name':'Backend profile'})
        preview=AUTHOR.plan(self.root,request)
        self.put('.dev/releases/v0.3.1/release.yaml',b'version: v0.3.1\nrelease_id: REL-v0.3.1\ndistribution:\n  package_id: ai-context-dotnet-backend-v0.3.1\n')
        with self.assertRaises(AUTHOR.AuthoringError): AUTHOR.apply(self.root,request,preview.digest)
        # Exercise resolve's safety ordering independently of Windows link privileges.
        unsafe=self.root/'consumer-link'; target=self.root/'README.md'
        real_resolve=Path.resolve
        def resolve(path,*args,**kwargs):
            return target if path==unsafe else real_resolve(path,*args,**kwargs)
        real_link=Path.is_symlink
        with mock.patch.object(Path,'resolve',resolve), mock.patch.object(Path,'is_symlink',lambda p:p==unsafe or real_link(p)):
            with self.assertRaises(AUTHOR.AuthoringError): AUTHOR.View(self.root).path('consumer-link').resolve()

    def test_dispositions_validate_pinned_committed_partition_and_refuse_head_drift(self):
        from test_source_dispositions import contract
        ref=AUTHOR.CATALOGS['source-dispositions'][0]
        self.put(ref,AUTHOR.dump(contract()))
        schema='.ai/distribution/schemas/source-dispositions.schema.yaml'; self.put(schema,(ROOT/schema).read_bytes())
        profile={'profile':{'id':'dotnet-backend'},'exclusions':[{'patterns':['.dev/**'],'except':['.dev/packaged.md','.dev/omitted.md']}],
                 'entries':[{'id':'fixture','component_id':'software-development-core','source':'.dev/packaged.md','target':'preserve-relative-path','ownership':'framework-managed','install_behavior':'managed'}]}
        self.put('.ai/distribution/profiles/dotnet-backend.yaml',AUTHOR.dump(profile))
        for name in ('packaged','omitted'): self.put('.dev/'+name+'.md',b'fixture\n')
        subprocess.run(['git','-C',str(self.root),'add','.'],check=True,capture_output=True)
        subprocess.run(['git','-C',str(self.root),'commit','-qm','committed disposition fixture'],check=True,capture_output=True)
        request=self.request('source-dispositions','fixture-omission',{'patterns':['.dev/omitted.*']})
        before=self.snapshot(); preview=AUTHOR.plan(self.root,request); self.assertEqual(before,self.snapshot())
        self.execute(request)
        request['changes']={'patterns':['.dev/packaged.md']}
        with self.assertRaises(AUTHOR.AuthoringError): AUTHOR.plan(self.root,request)
        request['changes']={'reason':'Still source-only.'}
        real_git=AUTHOR.git; calls=0
        def changed_head(root,*args,**kwargs):
            nonlocal calls
            result=real_git(root,*args,**kwargs)
            if args==('rev-parse','HEAD'):
                calls+=1
                if calls>1: return '0:'+'0'*40
            return result
        with mock.patch.object(AUTHOR,'git',changed_head), self.assertRaises(AUTHOR.AuthoringError): AUTHOR.plan(self.root,request)


class SkillAuthoringTests(AuthoringFixture):
    def setUp(self):
        super().setUp()
        refs={'.ai/assets/CANONICAL-SCHEMA.MD','.ai/assets/templates/skill-template.yaml','.ai/assets/skills/README.MD'}
        refs.update('.ai/scripts/'+name for name in (*AUTHOR.ROLE_RUNTIME,'runtime_skill_entries.py'))
        validator=AUTHOR._module('validate-ai-context')
        for identity in ('requirement-author','local-change-implementer'):
            ref=f'.ai/assets/skills/{identity}/skill.yaml'; data=AUTHOR.parse((ROOT/ref).read_text())
            refs.update(validator.canonical_wrapper_references(Path(ref),data))
            refs.update(meta['wrapper_path']+'SKILL.md' for meta in data['wrapper_metadata'].values())
        for ref in refs: self.put(ref,(ROOT/ref).read_bytes())

    def request(self,identity='requirement-author',**changes):
        return {'version':'1.0','operation':'skill.update','timestamp':NOW,'id':identity,'changes':changes or {'inputs':['Explicit retained fixture input.']}}

    def test_thin_skill_preserves_wrappers_extensions_and_rejects_protected_fields(self):
        ref='.ai/assets/skills/requirement-author/skill.yaml'; data=self.load(ref); data['owner_extension']={'preserve':[True,1]}; self.put(ref,AUTHOR.dump(data))
        request=self.request(); preview=AUTHOR.plan(self.root,request)
        self.assertEqual({ref},set(preview.changes)); self.execute(request)
        self.assertEqual(data['owner_extension'],self.load(ref)['owner_extension'])
        for changes in ({'asset_id':'other'},{'role_bindings':[]},{'triggers':[]},{'inputs':True}):
            with self.subTest(changes=changes), self.assertRaises(AUTHOR.AuthoringError): AUTHOR.plan(self.root,self.request(**changes))
        wrapper='.agents/skills/requirement-author/SKILL.md'; self.put(wrapper,(self.root/wrapper).read_bytes()+b'\nUnpaired drift.\n')
        with self.assertRaises(AUTHOR.AuthoringError): AUTHOR.plan(self.root,self.request(inputs=['Another input.']))

    def test_generated_bundle_uses_final_source_and_exact_recovery(self):
        request=self.request('local-change-implementer',purpose='Execute the explicitly bounded local fixture change.')
        projection=AUTHOR._module('runtime_skill_entries')
        for target in ('codex','claude'):
            ref=projection.wrapper_path(request['id'],target).as_posix(); self.put(ref,(self.root/ref).read_bytes().replace(b'\r\n',b'\n').replace(b'\n',b'\r\n'))
        before=self.snapshot(); preview=AUTHOR.plan(self.root,request); self.assertEqual(3,len(preview.changes))
        canonical=f'.ai/assets/skills/{request["id"]}/skill.yaml'; source=preview.changes[canonical][1]
        for target in ('codex','claude'):
            projected=preview.changes[projection.wrapper_path(request['id'],target).as_posix()][1]
            self.assertIn(projection.source_digest(source).encode(),projected)
            self.assertIn(request['changes']['purpose'].encode(),projected)
        rename=Path.rename
        def interrupt(path,destination):
            if path.name.endswith('.pending.json'): raise OSError('injected bundle completion failure')
            return rename(path,destination)
        with mock.patch.object(Path,'rename',interrupt), self.assertRaises(AUTHOR.AuthoringError): AUTHOR.apply(self.root,request,preview.digest)
        journal=next((self.root/AUTHOR.LOCAL).glob('*.pending.json')); AUTHOR.recover(self.root,journal)
        self.assertEqual(before,self.snapshot())

    def test_renderer_dependency_drift_and_isolated_portable_preview(self):
        request=self.request('local-change-implementer'); preview=AUTHOR.plan(self.root,request)
        ref='.ai/scripts/runtime_skill_entries.py'; original=(self.root/ref).read_bytes(); self.put(ref,original+b'\n')
        with self.assertRaises(AUTHOR.AuthoringError): AUTHOR.apply(self.root,request,preview.digest)
        self.put(ref,original)
        # Invoke copied runtime with no source-only distribution or evaluation modules.
        for name in ('artifact-authoring.py','artifact_authoring.py','artifact_core.py'):
            self.put('.ai/scripts/'+name,(ROOT/'.ai/scripts'/name).read_bytes())
        self.put('request.json',AUTHOR.canonical(request))
        result=subprocess.run([sys.executable,'-B',str(self.root/'.ai/scripts/artifact-authoring.py'),'--root',str(self.root),'preview','--request',str(self.root/'request.json')],cwd=self.root,capture_output=True,text=True)
        self.assertEqual(0,result.returncode,result.stderr)


class GovernanceCatalogAuthoringTests(AuthoringFixture):
    def request(self,identity,record,changes):
        return {'version':'1.0','operation':'catalog.update','timestamp':NOW,'id':identity,'record':record,'changes':changes}

    def test_lifecycle_update_binds_plain_owner_authority_and_protects_identity(self):
        registry=LIFECYCLE.load_registry(ROOT); self.put(LIFECYCLE.REGISTRY,AUTHOR.dump(registry,json_format=True))
        refs={'.ai/scripts/artifact_lifecycle.py'}
        for row in registry['records']:
            refs.update(ref.split('::')[0] for ref in row['models']+[row['owner']]+row['producers']+row['validators'])
        for ref in refs: self.put(ref,(ROOT/ref).read_bytes())
        request={'version':'1.0','operation':'lifecycle.update','timestamp':NOW,'id':'canonical-skill-metadata','changes':{'limits':'Existing metadata only; no creation or implicit adoption.'}}
        preview=AUTHOR.plan(self.root,request)
        self.assertEqual({LIFECYCLE.REGISTRY},set(preview.changes))
        ref='.ai/assets/CANONICAL-SCHEMA.MD'; self.put(ref,(self.root/ref).read_bytes()+b'\n')
        with self.assertRaises(AUTHOR.AuthoringError): AUTHOR.apply(self.root,request,preview.digest)
        request['changes']={'kind':'other'}
        with self.assertRaises(AUTHOR.AuthoringError): AUTHOR.plan(self.root,request)

    def test_portable_routes_check_mandatory_closure_and_optional_profile_presence(self):
        registry=LIFECYCLE.load_registry(ROOT); self.put(LIFECYCLE.REGISTRY,AUTHOR.dump(registry,json_format=True))
        for row in registry['records']:
            if row['applicability']!='portable': continue
            for ref in row['models']+[row['owner']]+row['producers']+row['validators']:
                ref=ref.split('::')[0]; self.put(ref,(ROOT/ref).read_bytes())
        self.assertEqual([],LIFECYCLE.validate_registry(self.root,source_context=False))
        route=LIFECYCLE.routes(self.root,'example-evidence-manifest')['records'][0]
        self.assertFalse(route['sources_available'])
        self.put('.ai/assets/tech-stacks/dotnet-backend/README.md',b'Selected profile fixture\n')
        self.assertTrue(any('example-evidence-manifest: missing' in e for e in LIFECYCLE.validate_registry(self.root,source_context=False)))
        ref=route['models'][0]; self.put(ref,(ROOT/ref).read_bytes())
        self.assertEqual([],LIFECYCLE.validate_registry(self.root,source_context=False))

    def test_governance_term_edit_binds_owner_text_and_preserves_machine_literals(self):
        ref=AUTHOR.CATALOGS['governance-terms'][0]; data=AUTHOR.parse((ROOT/ref).read_text()); self.put(ref,AUTHOR.dump(data))
        for row in data['governance_term_routing']['terms']:
            path=row['canonical_owner']['path']; self.put(path,(ROOT/path).read_bytes())
        for name in AUTHOR.ROLE_RUNTIME: self.put('.ai/scripts/'+name,(ROOT/'.ai/scripts'/name).read_bytes())
        selected=data['governance_term_routing']['terms'][0]
        request=self.request('governance-terms',selected['term_id'],{'qualified_term':selected['qualified_term']+' (explicit scope)'})
        preview=AUTHOR.plan(self.root,request); candidate=AUTHOR.parse(preview.changes[ref][1].decode())
        self.assertEqual(selected['machine_bindings'],candidate['governance_term_routing']['terms'][0]['machine_bindings'])
        owner=selected['canonical_owner']['path']; self.put(owner,(self.root/owner).read_bytes()+b'\n')
        with self.assertRaises(AUTHOR.AuthoringError): AUTHOR.apply(self.root,request,preview.digest)
        request['changes']={'owner_anchor':'not a real anchor'}
        with self.assertRaises(AUTHOR.AuthoringError): AUTHOR.plan(self.root,request)

    def test_shell_lifecycle_retains_runner_requirements_and_binds_index_modes(self):
        ref=AUTHOR.CATALOGS['shell-assets'][0]; script='.ai/scripts/fixture.sh'
        data={'schema_version':'2.0','contract':{'distribution_rule':'fixture','authority_rule':'fixture'},'assets':[{'path':script,'role':'manual-advisory','lifecycle':'active','distribution':'packaged','authority':'advisory','replacement':None}],
              'required_entrypoints':[],'check_all_required_scripts':[],'check_all_required_commands':[]}
        self.put(ref,AUTHOR.dump(data)); self.put(script,b'#!/bin/sh\nexit 0\n')
        self.put('.ai/scripts/validate-shell-assets.py',(ROOT/'.ai/scripts/validate-shell-assets.py').read_bytes())
        subprocess.run(['git','-C',str(self.root),'add','--chmod=+x',script],check=True,capture_output=True)
        request=self.request('shell-assets',script,{'lifecycle':'deprecated','replacement':'Use the documented current command.'})
        preview=AUTHOR.plan(self.root,request)
        subprocess.run(['git','-C',str(self.root),'update-index','--chmod=-x',script],check=True,capture_output=True)
        with self.assertRaises(AUTHOR.AuthoringError): AUTHOR.apply(self.root,request,preview.digest)
        subprocess.run(['git','-C',str(self.root),'update-index','--chmod=+x',script],check=True,capture_output=True)
        data['required_entrypoints']=[script]; self.put(ref,AUTHOR.dump(data))
        with self.assertRaises(AUTHOR.AuthoringError): AUTHOR.plan(self.root,request)


class LifecycleRegistryTests(unittest.TestCase):
    def test_all_current_named_schemas_and_baseline_groups_have_checked_routes(self):
        self.assertEqual([],LIFECYCLE.validate_registry(ROOT,source_context=True))
        data=LIFECYCLE.routes(ROOT)
        self.assertTrue(any(row['authoring']=='manual-gap' for row in data['records']))
        self.assertTrue(any(row['authoring']=='external' for row in data['records']))
        kinds={row['kind'] for row in data['records']}
        self.assertTrue({'external-task-dispatch','external-task-completion','external-task-validation-receipt','worktree-snapshot-lease','agent-execution-packet'}<=kinds)

    def test_missing_binding_duplicate_kind_and_claim_without_producer_fail(self):
        original=LIFECYCLE.load_registry(ROOT)
        for mutation in ('binding','duplicate','producer','plain-file','version'):
            data=copy.deepcopy(original)
            if mutation=='binding': data['records'][0]['validators']=['.ai/scripts/artifact_authoring.py::no_such_function']
            elif mutation=='duplicate': data['records'].append(copy.deepcopy(data['records'][0]))
            elif mutation=='producer': data['records'][0].update(authoring='executable',producers=[])
            elif mutation=='plain-file': data['records'][0].update(authoring='executable',producers=['AGENTS.md'])
            else: data['records'][0]['migration']['disposition']='automatic-every-version'
            with self.subTest(mutation=mutation), mock.patch.object(LIFECYCLE,'load_registry',return_value=data):
                self.assertTrue(LIFECYCLE.validate_registry(ROOT,source_context=True))

    def test_unregistered_schema_and_unavailable_source_routes_are_explicit(self):
        data=LIFECYCLE.load_registry(ROOT)
        data['coverage']['explicit_schemas'].pop()
        with mock.patch.object(LIFECYCLE,'load_registry',return_value=data):
            self.assertTrue(any('named schema coverage differs' in e for e in LIFECYCLE.validate_registry(ROOT,source_context=True)))
        with self.assertRaises(ValueError): LIFECYCLE.routes(ROOT,'not-registered')
        selected=LIFECYCLE.routes(ROOT,'github-backlog-migration-receipt')['records'][0]
        self.assertEqual([],selected['producers'])
        self.assertEqual('preserve',selected['migration']['disposition'])


if __name__=='__main__': unittest.main()
