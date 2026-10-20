"""Project-intent and paired-record contracts using small disposable fixtures.

Run: python -I -B tests/framework_next/test_maintenance_contracts.py
"""
from hashlib import sha256
from contextlib import contextmanager
from copy import deepcopy
from pathlib import Path
from types import SimpleNamespace
import os
import sys
import unittest
from unittest.mock import patch

HERE=Path(__file__).absolute().parent
sys.dont_write_bytecode=True
sys.path[:0]=[str(HERE),str(HERE.parents[1]/'src')]
import support
from distribution import installation_plan as planning,installation_state as state,installation,reinstallation
from distribution.installation_io import Backend,sibling
from distribution.data import json_bytes


class UnsupportedPlatformTests(unittest.TestCase):
    def test_unsupported_hosts_stop_before_native_io_and_report_an_actionable_route(self):
        durability={'declared_by':'test-owner','declaration_reference':'unit fixture',
                    'failure_domain':'process-termination'}
        for platform,pointer_size in (('darwin',4),('linux',4),('freebsd',8)):
            with self.subTest(platform=platform,pointer_size=pointer_size), \
                 patch('distribution.installation_io.os',SimpleNamespace(name='posix')), \
                 patch('distribution.installation_io.sys',SimpleNamespace(platform=platform)), \
                 patch('distribution.installation_io.ctypes.sizeof',return_value=pointer_size), \
                 patch('distribution.installation_io.ctypes.CDLL') as native, \
                 patch.object(Backend,'_volume') as volume:
                with self.assertRaises(state.InstallationError) as caught:
                    Backend({},durability)
                result=state._failure('plan',caught.exception)
                self.assertEqual(result['outcome'],'unsupported')
                self.assertFalse(result['changed'])
                diagnostic=result['diagnostics'][0]
                self.assertEqual(diagnostic['code'],'native-platform')
                self.assertIn('Windows or 64-bit Linux',diagnostic['next_action'])
                self.assertIn('inspect',diagnostic['next_action'])
                self.assertNotIn('retry',diagnostic['next_action'].lower())
                native.assert_not_called()
                volume.assert_not_called()


class MacOSFallbackTests(support.FixtureTestCase):
    @contextmanager
    def macos_host(self):
        # Execute standard-library file operations on this host, not a Darwin trial.
        portable_os=SimpleNamespace(name='posix',path=os.path,replace=os.replace,rename=os.rename)
        with patch('distribution.installation_io.os',portable_os), \
             patch('distribution.installation_io.sys',SimpleNamespace(platform='darwin')), \
             patch('distribution.installation_io.ctypes.sizeof',return_value=8):
            yield

    def backend(self,root,domain='process-termination'):
        return Backend({'project':root},{'declared_by':'fixture-owner',
            'declaration_reference':'host-simulated fixture','failure_domain':domain})

    def test_macos_needs_no_linux_native_loader_or_filesystem_query(self):
        root=support.active_run().case('mac-backend')
        with self.macos_host(),patch('distribution.installation_io.ctypes.CDLL') as native:
            backend=self.backend(root)
            self.assertTrue(backend.macos)
            self.assertFalse(backend.windows)
            self.assertEqual(backend._volume(root),(root.stat().st_dev,None))
            backend.flush_directory(root)
            native.assert_not_called()

    def test_volume_loss_and_power_loss_are_rejected_before_volume_observation(self):
        root=support.active_run().case('mac-domain')
        for domain in ('project-volume-loss','power-loss'):
            with self.subTest(domain=domain),self.macos_host(),patch.object(Backend,'_volume') as volume:
                with self.assertRaises(state.InstallationError) as caught:
                    self.backend(root,domain)
                self.assertEqual(caught.exception.outcome,'unsupported')
                volume.assert_not_called()

    def test_existing_target_is_preserved_until_replacement_is_explicit(self):
        root=support.active_run().case('mac-move')
        source=support.active_run().write(root/'source',b'new')
        target=support.active_run().write(root/'target',b'project-owned')
        with self.macos_host():
            backend=self.backend(root)
            with self.assertRaises(FileExistsError): backend.move(source,target,False)
            self.assertEqual(target.read_bytes(),b'project-owned')
            self.assertEqual(source.read_bytes(),b'new')
            backend.move(source,target,True)
            self.assertEqual(target.read_bytes(),b'new')
            self.assertFalse(source.exists())
            added=support.active_run().write(root/'added',b'added')
            backend.move(added,root/'destination',False)
            self.assertEqual((root/'destination').read_bytes(),b'added')
            with self.assertRaises(state.InstallationError):
                backend.move(target,root/'elsewhere'/'target',True)
            self.assertEqual(target.read_bytes(),b'new')

    def test_failures_and_matching_results_disclose_weaker_guarantees(self):
        with self.macos_host():
            # Invalid input never writes; disclosure must not look like success.
            for call in (installation.plan,installation.apply,installation.recover,reinstallation.execute):
                result=call({})
                self.assertFalse(result.get('changed',False))
                notes=[r for r in result['diagnostics'] if r['code']=='macos-reduced-guarantees']
                self.assertEqual(len(notes),1)
                self.assertIn('best effort',notes[0]['reason'])
                self.assertIn('external writers',notes[0]['next_action'])
            for operation,outcome in (('apply','unchanged'),('recover','already-matching')):
                result=installation._result(operation,outcome,installation.Changes(),'managed-bytes-consistent')
                self.assertEqual(result['diagnostics'][0]['code'],'macos-reduced-guarantees')
                self.assertFalse(result['changed'])

    def test_plan_prerequisites_bind_the_reduced_contract(self):
        notes={r['id']:r for r in planning._prerequisites(False,False,False,reduced_macos=True)}
        self.assertIn('best effort',notes['durability-declaration']['next_action'])
        self.assertIn('no atomic create-if-absent',notes['native-writer-backend']['next_action'])
        self.assertEqual(notes['writer-guard']['status'],'pending')
        self.assertEqual(notes['maintenance-quiescence']['status'],'pending')
        native={r['id']:r for r in planning._prerequisites(False,False,False)}
        self.assertIn('Native filesystem/domain',native['durability-declaration']['next_action'])


class MaintenanceContractTests(support.FixtureTestCase):
    def test_reinstall_preview_copies_only_selected_preservation_inputs(self):
        base=support.active_run().case('reinstall-agent-scope')
        roots={role:base/role for role in ('project','preview')}
        for root in roots.values(): root.mkdir()
        retained=[]; cleanup=[]
        for prefix,suffix in (('.codex/agents','.toml'),('.claude/agents','.md')):
            folder=roots['project']/prefix; folder.mkdir(parents=True)
            for name in ('managed','custom'):
                path=f'{prefix}/{name}{suffix}'; raw=name.encode()
                support.active_run().write(roots['project']/path,raw)
                row={'path':path,'sha256':sha256(raw).hexdigest()}
                (cleanup if name=='managed' else retained).append(row)
        inventory=reinstallation._scan(state._Reader(),roots['project'],{r['path'] for r in retained+cleanup})
        self.assertEqual(set(inventory),{r['path'] for r in retained+cleanup})
        document={'cleanup':cleanup,'scoped_inventory':list(inventory.values()),
                  'installation':{'protected_inputs':[],'project_edits':[]}}
        with patch.object(installation,'plan',return_value={'outcome':'planned','plan':{}}):
            reinstallation._preview(document,roots,state._Reader())
        for row in retained:
            self.assertEqual((roots['preview']/row['path']).read_bytes(),b'custom')
        for row in cleanup:
            self.assertFalse((roots['preview']/row['path']).exists())
            self.assertEqual((roots['project']/row['path']).read_bytes(),b'managed')

    def test_unrelated_history_and_custom_resources_need_no_inventory_or_preview(self):
        base=support.active_run().case('bounded-reinstall')
        roots={role:base/role for role in ('project','preview')}
        for root in roots.values(): root.mkdir()
        history=roots['project']/'.dev'/'lessons'; history.mkdir(parents=True)
        for index in range(4097):
            support.active_run().write(history/f'{index}.md',b'project history')
        custom=roots['project']/'.ai'/'custom'/'team-skill'
        custom.mkdir(parents=True)
        support.active_run().write(custom/'SKILL.md',b'team owned')
        managed='.ai/core/skills/example/SKILL.md'
        target=roots['project']/managed; target.parent.mkdir(parents=True)
        support.active_run().write(target,b'old managed')
        reader=state._Reader()
        with patch.object(reader,'read',wraps=reader.read) as reads:
            inventory=reinstallation._scan(reader,roots['project'],{managed})
        self.assertEqual(set(inventory),{managed})
        self.assertEqual(reads.call_count,1)
        document={'cleanup':[{'path':managed}],'scoped_inventory':list(inventory.values()),
                  'installation':{'protected_inputs':[],'project_edits':[]}}
        with patch.object(installation,'plan',return_value={'outcome':'planned','plan':{}}):
            reinstallation._preview(document,roots,state._Reader())
        self.assertEqual(list(roots['preview'].iterdir()),[])
        self.assertEqual((custom/'SKILL.md').read_bytes(),b'team owned')
        self.assertEqual((history/'4096.md').read_bytes(),b'project history')

    def test_cleanup_requires_installed_ownership_not_a_tracked_path(self):
        root=support.active_run().case('cleanup-ownership')
        member='.ai/core/skills/example/SKILL.md'
        lock=state.InstalledLock({},b'{}','1'*64,{member:{}})
        observation=state.Observation(root,lock,[],[],[])
        with patch.object(state,'observe_installation',return_value=observation):
            self.assertEqual(reinstallation._owned_cleanup(state._Reader(),root,None,{member,state.LOCK_PATH}),
                             {member,state.LOCK_PATH})
            for name in ('.dev/spec/example.md','.dev/requirement/example.md',
                         '.dev/lessons/example.md','.dev/adr/example.md',
                         '.dev/workflows/example.md','.dev/design/example.md',
                         '.dev/assessments/example.md','.ai/custom/team/SKILL.md',
                         '.ai/core/skills/team/SKILL.md','.agents/skills/team/SKILL.md',
                         '.claude/skills/team/SKILL.md','.codex/agents/team.toml'):
                with self.subTest(path=name),self.assertRaises(state.InstallationError) as caught:
                    reinstallation._owned_cleanup(state._Reader(),root,None,{name})
                self.assertEqual(caught.exception.diagnostic['code'],'reinstall-ownership')
                self.assertEqual(caught.exception.diagnostic['path'],name)
        with patch.object(state,'observe_installation',return_value=state.Observation(root,None,[],[],[])):
            with self.assertRaises(state.InstallationError):
                reinstallation._owned_cleanup(state._Reader(),root,None,{member})

    def test_reinstall_retains_precise_managed_drift_and_marker_conflicts(self):
        root=support.active_run().case('cleanup-drift')
        member='.ai/core/skills/example/SKILL.md'
        observation=state.Observation(root,None,[{'path':member,'reason':'member-drift'}],None,[])
        with patch.object(state,'observe_installation',return_value=observation):
            with self.assertRaises(planning.PlanConflict) as caught:
                reinstallation._owned_cleanup(state._Reader(),root,None,{member})
        with patch.object(reinstallation,'_prepare',side_effect=caught.exception):
            result=reinstallation.execute({'operation':'apply'})
        self.assertEqual(result['outcome'],'conflict')
        self.assertFalse(result['changed'])
        self.assertEqual(result['removed'],[])
        self.assertEqual(result['diagnostics'][0]['path'],member)
        observation=state.Observation(root,None,[],None,[state.MARKERS[0]])
        with patch.object(state,'observe_installation',return_value=observation):
            with self.assertRaises(state.InstallationError) as caught:
                reinstallation._owned_cleanup(state._Reader(),root,None,set())
        self.assertEqual(caught.exception.diagnostic['code'],'maintenance-marker')

    def test_reinstall_retains_plan_failure_before_and_after_cleanup(self):
        failure={'outcome':'conflict','changed':False,'diagnostics':[{
            'code':'unowned-collision','path':'.codex/agents/custom.toml',
            'reason':'Explicit collision','next_action':'Preserve project-owned file.'}]}
        for phase in ('preview','after-cleanup'):
            with self.subTest(phase=phase):
                root=support.active_run().case('reinstall-failure-'+phase)
                file=support.active_run().write(root/'retired',b'old')
                document={'cleanup':[{'path':'retired','sha256':sha256(b'old').hexdigest()}],
                          'coordination_reset':None,'preserved_inputs':[], 'installation':{}}
                preview={'outcome':'planned','plan':{}}
                request={'operation':'apply','expected_plan_sha256':sha256(json_bytes({
                    **document,'installation_preview':preview['plan']})).hexdigest()}
                def prepare(_):
                    return deepcopy(document),{'project':root},state._Reader(),SimpleNamespace(members={})
                with patch.object(reinstallation,'_prepare',side_effect=prepare), \
                     patch.object(reinstallation,'_preview',return_value=failure if phase=='preview' else preview), \
                     patch.object(installation,'plan',return_value=failure), \
                     patch.object(installation,'apply') as apply:
                    result=reinstallation.execute(request)
                key='installation_preview_result' if phase=='preview' else 'installation_plan_result'
                self.assertEqual(result[key],failure)
                self.assertEqual(result['changed'],phase=='after-cleanup')
                self.assertEqual(result['removed'],[] if phase=='preview' else ['retired'])
                self.assertEqual(file.exists(),phase=='preview')
                self.assertEqual(result['outcome'],'blocked' if phase=='preview' else 'cleanup-incomplete')
                apply.assert_not_called()

    def roots(self,name):
        base=support.active_run().case(name)
        result={}
        for role in ('project','staging'):
            target=base/role; target.mkdir(); result[role]=target
        (result['staging']/'objects').mkdir()
        return result

    def intent(self,roots,name,before,after):
        if before is not None:
            target=roots['project']/name; target.parent.mkdir(parents=True,exist_ok=True)
            support.active_run().write(target,before)
            if os.name=='posix': target.chmod(0o644)
        digest=sha256(after).hexdigest() if after is not None else None
        if after is not None: support.active_run().write(roots['staging']/'objects'/digest,after)
        return {'path':name,'before_sha256':sha256(before).hexdigest() if before is not None else None,
                'after_sha256':digest,'after_content_ref':'objects/'+digest if digest else None}

    def test_exact_root_preimage_and_after_object_are_retained_without_write(self):
        roots=self.roots('root-edit')
        intent=self.intent(roots,'AGENTS.md',b'old root\r\n',b'new root\n')
        rows,objects=planning.project_edits(state._Reader(),roots,[intent],set(),[])
        self.assertEqual(objects[rows[0]['before']['sha256']],b'old root\r\n')
        self.assertEqual(objects[rows[0]['after']['sha256']],b'new root\n')
        self.assertEqual((roots['project']/'AGENTS.md').read_bytes(),b'old root\r\n')
        self.assertTrue(sibling('1'*32,'AGENTS.md').startswith('.fi-'))
        self.assertNotIn('/',sibling('1'*32,'AGENTS.md'))

    def test_unowned_present_file_and_managed_protected_overlap_block(self):
        roots=self.roots('intent-overlap')
        intent=self.intent(roots,'AGENTS.md',b'owned by project',b'after')
        for managed,protected in (({'AGENTS.md'},[]),(set(),['AGENTS.md'])):
            with self.assertRaises(ValueError): planning.project_edits(state._Reader(),roots,[intent],managed,protected)
        intent['before_sha256']=None
        with self.assertRaises(ValueError): planning.project_edits(state._Reader(),roots,[intent],set(),[])

    def test_content_address_and_delete_shape_fail_closed(self):
        roots=self.roots('object-drift')
        intent=self.intent(roots,'AGENTS.md',None,b'candidate')
        (roots['staging']/intent['after_content_ref']).write_bytes(b'changed')
        with self.assertRaises(ValueError): planning.project_edits(state._Reader(),roots,[intent],set(),[])
        intent['after_sha256']=None
        with self.assertRaises(ValueError): planning.project_edits(state._Reader(),roots,[intent],set(),[])

    def test_recovery_records_reject_unknown_fields_and_wrong_side(self):
        roots=self.roots('record-shape')
        intent=self.intent(roots,'AGENTS.md',b'old',None)
        rows,objects=planning.project_edits(state._Reader(),roots,[intent],set(),[])
        # _edit_record consumes already verified object bytes from the same object owner.
        installation._edit_record(rows,state._Reader(),roots['staging'],dict(objects),set(),[])
        rows[0]['after']={'sha256':'1'*64,'size':1,'mode':'100644'}
        with self.assertRaises(ValueError): installation._edit_record(rows,state._Reader(),roots['staging'],dict(objects),set(),[])

    def test_equal_lock_hashes_do_not_collapse_project_before_and_after(self):
        before=state.InstalledLock({},b'{}','1'*64,{})
        after=state.InstalledLock({},b'{}','1'*64,{})
        old={'sha256':'2'*64,'size':3,'mode':'100644'}
        new={'sha256':'3'*64,'size':3,'mode':'100644'}
        operation=installation.Operation({'project_edits':[{'intent':{'path':'ROOT.md'},'before':old,'after':new}]},b'',before,after,{})
        self.assertEqual(operation.descriptors(before)['ROOT.md']['sha256'],old['sha256'])
        self.assertEqual(operation.descriptors(after)['ROOT.md']['sha256'],new['sha256'])
        foreign=state.InstalledLock({},b'{}','1'*64,{})
        with self.assertRaises(ValueError): operation.descriptors(foreign)

    def test_project_edits_and_retained_records_cannot_modify_custom_resources(self):
        roots=self.roots('edit-ownership')
        for name in ('.dev/spec/example.md','.dev/requirement/example.md',
                     '.dev/lessons/example.md','.dev/adr/example.md',
                     '.dev/workflows/example.md','.dev/design/example.md',
                     '.dev/assessments/example.md','docs/requirements/example.md',
                     '.ai/custom/team/SKILL.md','.ai/custom/framework.json',
                     '.agents/skills/team/SKILL.md','.claude/skills/team/SKILL.md',
                     '.codex/agents/team.toml','.ai/core/skills/example/SKILL.md'):
            with self.subTest(path=name):
                intent={'path':name,'before_sha256':None,'after_sha256':None,'after_content_ref':None}
                with self.assertRaises(state.InstallationError) as caught:
                    planning.project_edits(state._Reader(),roots,[intent],set(),[])
                self.assertEqual(caught.exception.diagnostic['code'],'project-edit-boundary')
                with self.assertRaises(state.InstallationError) as caught:
                    installation._edit_record([{'intent':intent,'before':None,'after':None}],
                                              state._Reader(),roots['staging'],{},set(),[])
                self.assertEqual(caught.exception.diagnostic['code'],'project-edit-boundary')
        for name in ('AGENTS.md','.ai/custom/installation.json','.codex/config.toml',
                     '.claude/settings.json','.ai/INDEX.MD','.agents/skills/README.md'):
            self.assertEqual(planning.project_edit_path(name),name)

    def test_saved_selection_uses_exact_types_before_semantic_comparison(self):
        roots=self.roots('saved-selection-types')
        desired={'selection_version':1,'catalog':{'identity':'catalog:1:0.19.0-rc.2:'+'1'*40+':'+'2'*64,
                  'catalog_sha256':'3'*64,'files_sha256':'4'*64},'skills':[],'knowledge':[],'adapters':[],'bindings':[]}
        saved={**desired,'selection_version':True}
        intent=self.intent(roots,'.ai/custom/installation.json',None,json_bytes(saved))
        rows,objects=planning.project_edits(state._Reader(),roots,[intent],set(),[])
        candidate=SimpleNamespace(selection={'desired':desired})
        with self.assertRaises(ValueError): planning.project_bindings(state._Reader(),roots['project'],candidate,[],rows,objects)

    def test_api1_cannot_acquire_new_writer_semantics(self):
        request={'api_version':1,'operation':'inspect','project_root':'unused','engine_root':'unused','engine':{}}
        result=installation.execute(request)
        self.assertEqual(result['outcome'],'unsupported')
        self.assertEqual(result['diagnostics'][0]['code'],'unsupported-write')
        self.assertFalse(result['changed'])

    def test_flat_agent_profiles_do_not_claim_unrelated_runtime_entries(self):
        roots=self.roots('flat-agent-profiles')
        folder=roots['project']/'.codex/agents'; folder.mkdir(parents=True)
        managed='.codex/agents/reviewer.toml'
        support.active_run().write(folder/'reviewer.toml',b'managed')
        support.active_run().write(folder/'custom.toml',b'project-owned')
        self.assertEqual(state._unknown(state._Reader(),roots['project'],{managed},{managed}),[])
        self.assertEqual((folder/'custom.toml').read_bytes(),b'project-owned')

    def test_sub_agent_managed_bytes_report_drift(self):
        roots=self.roots('agent-drift')
        name='.codex/agents/reviewer.toml'; path=roots['project']/name
        path.parent.mkdir(parents=True)
        support.active_run().write(path,b'changed')
        row={'path':name,'destination':name,'mode':'100644','size':8,'sha256':sha256(b'original').hexdigest()}
        with self.assertRaises(ValueError): state._Reader().member(roots['project'],row,
            'windows-inventory-only' if os.name=='nt' else 'posix-permissions')


if __name__ == "__main__":
    unittest.main()
