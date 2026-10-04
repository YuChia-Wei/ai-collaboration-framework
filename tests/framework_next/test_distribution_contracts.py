"""Distribution metadata, dependency and identity contract fixtures.

Run: python -I -B tests/framework_next/test_distribution_contracts.py
These in-memory fixtures neither install a target nor prove native/runtime behavior.
"""
from copy import deepcopy
from hashlib import sha1
from pathlib import Path
import sys
import unittest

sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).absolute().parents[2]/'src'))
from distribution.content import load_content_package, descriptor, closure, desired_shape, selected_references
from distribution.contracts import validate
from distribution.data import DistributionError,json_bytes,json_object,yaml_object
from distribution.git_source import Blob
from distribution.package import load_package
from distribution import catalog


def blob(name,value):
    raw=json_bytes(value)
    oid=sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
    return Blob(name,oid,'100644',raw)


def knowledge():
    return {'content_package_version':1,'id':'common','version':'0.1.0','entrypoint':'README.md',
            'members':[{'path':'README.md','kind':'index'},{'path':'content-package.yaml','kind':'metadata'}],
            'resources':[{'id':'index','path':'README.md','kind':'knowledge','rule_ids':[],
                          'capabilities':['review'],'operations':['review'],'technology_profile':None}],
            'dependencies':{'required':[],'optional':[]},'references':[]}


def skill():
    return {'metadata_version':4,'id':'reviewer','version':'0.2.0','delivery_status':'implemented','entrypoint':'SKILL.md',
            'dependencies':{'required':[],'optional':[]},'runtime':[], 'configuration':None,'artifact_roles':[],
            'resources':{'references':['review.md'],'schemas':[],'templates':[],'tools':[]},
            'operations':[{'id':'review','execution':'instruction','inputs':['text'],'outputs':['review'],
                           'implementation_status':'implemented','instructions':'review.md'}],
            'knowledge_consumption':[{'id':'common','package':'common','version':'0.1.0','operations':['review'],
                                      'resources':['index'],'requirement':'optional','on_missing':'unavailable'}]}


class DistributionContractTests(unittest.TestCase):
    def test_content_and_metadata4_have_distinct_closed_shapes(self):
        package=load_content_package(blob('content-package.yaml',knowledge()))
        self.assertEqual(package.members,frozenset({'README.md','content-package.yaml'}))
        package=load_package(blob('skill-package.yaml',skill()))
        self.assertEqual(descriptor('skill',package)['optional_dependencies'],
                         [{'kind':'knowledge','id':'common','version':'0.1.0','on_missing':'unavailable'}])
        mixed=skill(); mixed['metadata_version']=3
        with self.assertRaises(ValueError): load_package(blob('skill-package.yaml',mixed))
        legacy=skill(); legacy['metadata_version']=3; del legacy['knowledge_consumption']
        self.assertEqual(load_package(blob('skill-package.yaml',legacy)).metadata['metadata_version'],3)

    def test_exact_discriminators_and_duplicate_keys(self):
        for bad in (True,1.0,'1',2):
            doc=knowledge(); doc['content_package_version']=bad
            with self.subTest(bad=bad),self.assertRaises(ValueError): load_content_package(blob('content-package.yaml',doc))
        for raw in (b'{"a":1,"a":2}',b'\xef\xbb\xbf{}',b'{"x":"\\ud800"}'):
            with self.subTest(raw=raw),self.assertRaises(ValueError): json_object(raw,'fixture')
        for raw in (b'a: 1\na: 2\n',b'a: &x [1]\nb: *x\n',b'a: !thing x\n',b'a: 1\n---\na: 2\n'):
            with self.subTest(raw=raw),self.assertRaises(ValueError): yaml_object(raw,'fixture')

    def test_required_omission_optional_absence_and_cycle(self):
        common=descriptor('knowledge',load_content_package(blob('content-package.yaml',knowledge())))
        consumer=descriptor('skill',load_package(blob('skill-package.yaml',skill())))
        closure([consumer])
        mandatory=deepcopy(consumer); mandatory['required_dependencies']=[{'kind':'knowledge','id':'common','version':'0.1.0'}]; mandatory['optional_dependencies']=[]
        with self.assertRaisesRegex(ValueError,'dependency-closure'): closure([mandatory])
        closure([common,mandatory])
        other=deepcopy(common); other['id']='other'
        common['required_dependencies']=[{'kind':'knowledge','id':'other','version':'0.1.0'}]
        other['required_dependencies']=[{'kind':'knowledge','id':'common','version':'0.1.0'}]
        with self.assertRaisesRegex(ValueError,'dependency-cycle'): closure([common,other])

    def test_empty_and_reference_only_selection_are_explicit(self):
        pin={'identity':'catalog:1:0.19.0-rc.2:'+'1'*40+':'+'2'*64,'catalog_sha256':'3'*64,'files_sha256':'4'*64}
        empty={'selection_version':1,'catalog':pin,'skills':[],'knowledge':[],'adapters':[],'bindings':[]}
        desired_shape(empty)
        reference=deepcopy(empty); reference['knowledge']=['common']; desired_shape(reference)
        duplicate=deepcopy(reference); duplicate['knowledge']*=2
        with self.assertRaises(ValueError): desired_shape(duplicate)
        alias=knowledge(); alias['members'].append({'path':'readme.md','kind':'knowledge'})
        alias['members'].sort(key=lambda r:r['path'])
        with self.assertRaises(ValueError): load_content_package(blob('content-package.yaml',alias))

    def test_parent_and_subset_identity_boundaries_are_independent(self):
        doc={'release_version':'0.19.0-rc.2','source':{'commit':'1'*40}}
        parent={'metadata/catalog.json':b'catalog\n','metadata/catalog-files.json':b'files\n'}
        first,_=catalog.identity('catalog',doc,parent)
        a,_=catalog.identity('subset',doc,{**parent,'metadata/selection.json':b'A','metadata/files.json':b'[]'})
        b,_=catalog.identity('subset',doc,{**parent,'metadata/selection.json':b'B','metadata/files.json':b'[]'})
        self.assertNotEqual(a,b)
        self.assertEqual(catalog.identity('catalog',doc,parent)[0],first)

    def test_optional_reference_is_unavailable_but_unconditional_link_blocks(self):
        doc=knowledge()
        doc['dependencies']['optional']=[{'kind':'knowledge','id':'other','version':'0.1.0','on_missing':'unavailable'}]
        doc['references']=[{'from':'README.md','resource_id':'index','target':{'package':'other','path':'README.md','anchor':None},
                            'requirement':'optional','on_missing':'unavailable'}]
        package=load_content_package(blob('content-package.yaml',doc))
        packages={('knowledge','common'):package}
        contents={('knowledge','common','README.md'):b'Guarded optional resource lookup.\n'}
        self.assertEqual(selected_references(packages,contents)[0]['status'],'unavailable')
        contents[('knowledge','common','README.md')]=b'[unconditional](../other/README.md)\n'
        with self.assertRaisesRegex(ValueError,'reference-closure'): selected_references(packages,contents)

    def test_example_code_is_inert_and_active_undeclared_links_are_not(self):
        package=load_content_package(blob('content-package.yaml',knowledge()))
        packages={('knowledge','common'):package}
        contents={('knowledge','common','README.md'):b'# Index\n\n```csharp\nWhen[Event](typed, ct);\n```\n`[label](missing.md)`\n'}
        self.assertEqual(selected_references(packages,contents),[])
        contents[('knowledge','common','README.md')]+=b'[active](missing.md)\n'
        with self.assertRaisesRegex(ValueError,'reference-closure'): selected_references(packages,contents)

    def test_empty_subset_metadata_is_complete_and_unknown_selection_blocks(self):
        # Synthetic descriptors exercise metadata semantics only, never artifact admission.
        sources=[{'path':name,'git_blob':'1'*40,'mode':'100644','size':0,'sha256':'2'*64}
                 for name in sorted(set(catalog.GENERATOR_FILES)|{'src/distribution/manifest.yaml'})]
        implementation=[row for row in sources if row['path'] in catalog.GENERATOR_FILES]
        parent={'catalog_version':1,'release_version':'0.19.0-rc.2','source':{'commit':'1'*40,'tree':'3'*40},
                'components':[],'adapters':[],'presets':[],'build_inputs':sources,
                'generator':{'id':'aicf-catalog-assembly','implementation':implementation}}
        # The catalog itself requires a member; the selected subset may be empty.
        member='skill-entry-v2.md.template'
        parent['adapters']=[{'id':'codex','version':'2.0.0','prefix':'aicf-','template':member,'members':[member]}]
        source=next(row for row in sources if row['path']=='src/adapters/codex/'+member)
        files=[{'path':'adapters/codex/'+member,'kind':'adapter','owner':'codex','member':member,'source':source}]
        raw={'metadata/catalog.json':json_bytes(parent),'metadata/catalog-files.json':json_bytes({'catalog_files_version':1,'files':files})}
        _,_,pin=catalog.parent_documents(raw)
        desired={'selection_version':1,'catalog':pin,'skills':[],'knowledge':[],'adapters':[],'bindings':[]}
        selection={'schema_version':3,'mode':'catalog-subset','release_version':parent['release_version'],'source':parent['source'],
                   'catalog':pin,'desired':desired,'desired_sha256':catalog.digest(json_bytes(desired)),'components':[],'adapters':[],
                   'generator':{**parent['generator'],'id':'aicf-subset-derivation'}}
        raw.update({'metadata/selection.json':json_bytes(selection),'metadata/files.json':json_bytes({'schema_version':2,'files':[]})})
        identity,inputs=catalog.identity('subset',selection,raw)
        receipt={'schema_version':2,'artifact_kind':'subset','identity':identity,'identity_inputs':inputs,
                 'completed_at':'2000-01-01T00:00:00+00:00',
                 'executing_implementation':[{'source':row,'execution_file_sha256':row['sha256']} for row in implementation],
                 'runtime':{'python':'fixture','pyyaml':'fixture','os':'nt'},'mode_materialization':'inventory-only',
                 'installation':'not-performed','behavioral_validation':'not-performed','publication':'not-performed'}
        raw['metadata/build.json']=json_bytes(receipt)
        parsed=catalog.subset_documents(raw)
        self.assertEqual(parsed[3],{}); self.assertEqual(parsed[4],identity)
        selection['desired']['skills']=['unavailable']
        selection['desired_sha256']=catalog.digest(json_bytes(selection['desired']))
        raw['metadata/selection.json']=json_bytes(selection)
        with self.assertRaisesRegex(ValueError,'component selection'): catalog.subset_documents(raw)

    def test_generated_unknown_fields_and_lexical_sizes_are_rejected(self):
        for bad in ({'schema_version':2,'files':[],'extra':1},{'schema_version':True,'files':[]}):
            with self.assertRaises(ValueError): validate('Files',bad)
        source={'path':'src/x','git_blob':'1'*40,'mode':'100644','size':1.0,'sha256':'2'*64}
        with self.assertRaises(ValueError): validate('Source',source)


class SubAgentDistributionTests(unittest.TestCase):
    """Actual small role sources in a synthetic in-memory catalog; no installation."""

    def role_catalog(self, role='context-translator', *, legacy=False):
        from test_skill_naming import tiny_catalog, source_blob, ROOT
        from distribution.content import load_sub_agent_package
        base=tiny_catalog()
        doc=deepcopy(base.document); inventory=deepcopy(base.inventory); contents=dict(base.contents)
        prefix='src/sub-agents/'+role
        package=load_sub_agent_package(source_blob(prefix+'/sub-agent-package.yaml',
                                                   (ROOT/prefix/'sub-agent-package.yaml').read_bytes()))
        for member in sorted(package.members):
            raw=(ROOT/prefix/member).read_bytes()
            if legacy:
                # Synthetic policy-1 compatibility fixture; current published
                # role sources no longer prescribe these model generations.
                translator=role=='context-translator'
                models=['gpt-6-luna'] if translator else ['gpt-6.1-sol','gpt-6-sol']
                effort='max' if translator else 'medium'
                claude='claude-haiku-4-5-20251001' if translator else 'claude-opus-5-5'
                if member=='sub-agent.yaml':
                    data=yaml_object(raw,member)
                    data['model_policy']={'policy_version':1,'codex':{'candidates':models,'reasoning_effort':effort},
                                          'claude':{'candidates':[claude]}}
                    raw=json_bytes(data)
                elif member=='runtime/codex.toml':
                    raw=(f'model = "{models[0]}"\nmodel_reasoning_effort = "{effort}"\n'.encode()+raw)
                elif member=='runtime/claude.md':
                    raw=raw.replace(b'model: inherit',('model: '+claude).encode())
            src=source_blob(prefix+'/'+member,raw)
            artifact=f'packages/sub-agent/{role}/{member}'
            inventory['files'].append({'path':artifact,'kind':'sub-agent','owner':role,'member':member,'source':src.identity()})
            contents[artifact]=src.data; doc['build_inputs'].append(src.identity())
        doc['build_inputs'].sort(key=lambda r:r['path'])
        doc['components'].append(descriptor('sub-agent',package))
        doc['components'].sort(key=lambda r:(r['kind'],r['id']))
        doc['presets'][0]['skills']=[]; doc['presets'][0]['sub_agents']=[role]
        # Each real role supplies both runtime projections; the default preset is Codex.
        doc['presets'][0]['adapters']=['codex']
        inventory['files'].sort(key=lambda r:r['path'])
        raw={catalog.PARENT_METADATA[0]:json_bytes(doc),catalog.PARENT_METADATA[1]:json_bytes(inventory)}
        doc,inventory,pin=catalog.parent_documents(raw)
        packages=catalog.packages_from(doc,inventory,contents)
        return catalog.Catalog(None,doc,inventory,pin,raw,contents,packages)

    def availability(self, models, adapter='codex', source=None):
        return [{'adapter':adapter,'source':source or ('codex-app-server' if adapter=='codex' else 'caller-claude-code'),
                 'observed_at':'2026-10-03T00:00:00+00:00',
                 'models':[{'id':model,'reasoning_efforts':efforts} for model,efforts in sorted(models)]}]

    def test_model_priority_fallback_effort_and_exact_projection(self):
        parent=self.role_catalog('mechanical-evidence-worker',legacy=True)
        desired=catalog.expand_preset(parent,'tiny','1.0.0')
        original=json_bytes(desired)
        observations=self.availability([('gpt-6-sol',['medium']),('gpt-6.1-sol',['medium'])])
        selected=catalog.resolve_sub_agent_model_selection(parent,desired,observations)
        self.assertEqual(selected['model_resolution']['bindings'][0]['model'],'gpt-6.1-sol')
        self.assertEqual(json_bytes(desired),original)
        observations[0]['models'][1]['reasoning_efforts']=['low']
        selected=catalog.resolve_sub_agent_model_selection(parent,desired,observations)
        self.assertEqual(selected['model_resolution']['bindings'][0]['model'],'gpt-6-sol')
        _,inventory,contents=self.projection(parent,selected)
        dest='.codex/agents/mechanical-evidence-worker.toml'
        raw=contents['.ai/core/sub-agents/mechanical-evidence-worker/runtime/codex.toml']
        self.assertEqual(contents[dest],raw.replace(b'gpt-6.1-sol',b'gpt-6-sol'))
        row=next(r for r in inventory['files'] if r['destination']==dest)
        self.assertIsNone(row['source']); self.assertEqual(row['binding']['model'],'gpt-6-sol')
        altered=deepcopy(selected); altered['model_resolution']['bindings'][0]['reasoning_effort']='low'
        with self.assertRaisesRegex(ValueError,'model resolution mismatch'): catalog.resolve_selection(parent,altered)
        observations[0]['models']=[]
        with self.assertRaisesRegex(ValueError,'model-unavailable'): catalog.resolve_sub_agent_model_selection(parent,desired,observations)

    def test_model_provider_and_candidate_boundaries_fail_closed(self):
        parent=self.role_catalog(legacy=True)
        desired=catalog.expand_preset(parent,'tiny','1.0.0')
        for observations in (self.availability([('gpt-5.6-luna',['max'])]),
                             self.availability([('gpt-6-luna',['high'])]),
                             self.availability([('gpt-6-luna',['max'])],source='anthropic-api'),
                             self.availability([('gpt-6-luna',['max']),('gpt-6-luna',['max'])]),
                             self.availability([('claude-sonnet-5-5',[])],adapter='claude')):
            with self.subTest(observations=observations),self.assertRaises(ValueError):
                catalog.resolve_sub_agent_model_selection(parent,desired,observations)
        desired['adapters']=['claude']
        observations=self.availability([('claude-haiku-4-5-20251001',[])],adapter='claude')
        selected=catalog.resolve_sub_agent_model_selection(parent,desired,observations)
        self.projection(parent,selected)
        selected['model_resolution']['bindings'][0]['model']='claude-sonnet-5-5'
        with self.assertRaises(ValueError): catalog.resolve_selection(parent,selected)

    def test_model_selection_and_inventory_drift_are_rejected(self):
        parent=self.role_catalog('mechanical-evidence-worker',legacy=True); desired=catalog.expand_preset(parent,'tiny','1.0.0')
        selected=catalog.resolve_sub_agent_model_selection(parent,desired,self.availability([('gpt-6-sol',['medium'])]))
        selection,inventory,contents=self.projection(parent,selected)
        mutated=deepcopy(inventory)
        next(r for r in mutated['files'] if r['kind']=='runtime')['binding']['template_sha256']='0'*64
        with self.assertRaises(ValueError): catalog.subset_inventory(parent.document,parent.inventory,selection,mutated)
        dest='.codex/agents/mechanical-evidence-worker.toml'; contents[dest]=contents[dest].replace(b'gpt-6-sol',b'gpt-6-astra')
        with self.assertRaises(ValueError): catalog.verify_subset_contents(parent.document,parent.inventory,selection,inventory,contents)
        selected['model_resolution']['bindings']=[]
        with self.assertRaises(ValueError): catalog.resolve_selection(parent,selected)

    def test_renderer_preserves_crlf_and_refuses_ambiguous_model_field(self):
        from distribution.content import render_sub_agent_model
        binding={'model':'gpt-6-sol'}
        raw=b'name = "example"\r\nmodel = "gpt-6.1-sol"\r\nmodel_reasoning_effort = "high"\r\n'
        self.assertEqual(render_sub_agent_model(raw,'codex',binding),raw.replace(b'gpt-6.1-sol',b'gpt-6-sol'))
        with self.assertRaises(ValueError): render_sub_agent_model(raw+raw,'codex',binding)

    def discovery_module(self):
        import importlib.util
        path=Path(__file__).absolute().parents[2]/'src/tools/derive-subset.py'
        spec=importlib.util.spec_from_file_location('model_discovery_fixture',path)
        module=importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
        return module

    def test_codex_discovery_paginates_without_thread_or_inference(self):
        import io,json
        from unittest.mock import patch
        module=self.discovery_module()
        class Pipe(io.BytesIO):
            def close(self): self.saved=self.getvalue(); super().close()
        class Process:
            stdin=Pipe()
            stdout=io.BytesIO(b'\n'.join(json.dumps(v).encode() for v in (
                {'id':0,'result':{}},
                {'id':1,'result':{'data':[{'model':'gpt-6.1-sol','supportedReasoningEfforts':[{'reasoningEffort':'medium'}]}],'nextCursor':'page2'}},
                {'id':2,'result':{'data':[{'id':'gpt-6-luna','supportedReasoningEfforts':[{'reasoningEffort':'max'}]}],'nextCursor':None}}))+b'\n')
            def poll(self): return 0
            def wait(self,timeout): return 0
        proc=Process()
        with patch('shutil.which',return_value='codex'),patch('subprocess.Popen',return_value=proc) as launch:
            observation=module.discover_codex_models()
        self.assertEqual(observation['source'],'codex-app-server')
        self.assertEqual([r['id'] for r in observation['models']],['gpt-6-luna','gpt-6.1-sol'])
        messages=[json.loads(row) for row in proc.stdin.saved.splitlines()]
        self.assertEqual([m['method'] for m in messages],['initialize','initialized','model/list','model/list'])
        self.assertEqual(messages[-1]['params']['cursor'],'page2')
        self.assertEqual(launch.call_args.args[0],['codex','app-server'])

    def test_codex_discovery_refuses_malformed_identifiers_and_efforts(self):
        import io,json
        from unittest.mock import patch
        module=self.discovery_module()
        for row in (None,1,{}, {'model':None},{'model':1},{'model':''},
                    {'id':'gpt-6-sol','model':None},{'id':'gpt-6-sol','model':1},
                    {'model':'gpt-6-sol','supportedReasoningEfforts':None},
                    {'model':'gpt-6-sol','supportedReasoningEfforts':[{'reasoningEffort':1}]}):
            class Process:
                stdin=io.BytesIO()
                stdout=io.BytesIO(b'\n'.join(json.dumps(v).encode() for v in (
                    {'id':0,'result':{}},{'id':1,'result':{'data':[row],'nextCursor':None}}))+b'\n')
                def poll(self): return 0
                def wait(self,timeout): return 0
            with self.subTest(row=row),patch('shutil.which',return_value='codex'),patch('subprocess.Popen',return_value=Process()),self.assertRaises(ValueError):
                module.discover_codex_models()

    def test_claude_api_discovery_is_explicit_paged_and_secret_free(self):
        import io,json
        from unittest.mock import patch,Mock
        module=self.discovery_module(); requests=[]
        opener=Mock()
        def request(req,timeout):
            requests.append(req)
            return io.BytesIO(json.dumps({'data':[{'id':'claude-opus-5-5' if len(requests)==1 else 'claude-fable-5-1'}],
                                          'has_more':len(requests)==1,'last_id':'claude-opus-5-5'}).encode())
        opener.open.side_effect=request
        with patch.dict('os.environ',{'ANTHROPIC_API_KEY':'fixture-secret'},clear=True),patch('urllib.request.build_opener',return_value=opener):
            observation=module.discover_claude_api_models()
        self.assertEqual(observation['source'],'anthropic-api')
        self.assertNotIn('fixture-secret',json.dumps(observation))
        self.assertTrue(all(r.full_url.startswith('https://api.anthropic.com/v1/models?') for r in requests))
        self.assertIn('after_id=claude-opus-5-5',requests[1].full_url)
        self.assertEqual(requests[0].get_header('X-api-key'),'fixture-secret')
        with patch.dict('os.environ',{},clear=True),self.assertRaises(ValueError): module.discover_claude_api_models()
        with patch.dict('os.environ',{'ANTHROPIC_API_KEY':'fixture-secret','ANTHROPIC_BASE_URL':'https://example.invalid'},clear=True),self.assertRaises(ValueError): module.discover_claude_api_models()

    def projection(self, parent, desired):
        from distribution.content import component_root
        resolved=catalog.resolve_selection(parent,desired)
        selection={'schema_version':3,'mode':'catalog-subset',
                   'release_version':parent.document['release_version'],'source':parent.document['source'],
                   'catalog':parent.pin,'desired':resolved['desired'],'desired_sha256':resolved['desired_sha256'],
                   'components':resolved['components'],'adapters':resolved['adapters'],
                   'generator':{**parent.document['generator'],'id':'aicf-subset-derivation'}}
        selection=json_object(json_bytes(selection),'fixture subset')
        validate('Subset',selection)
        selected={(c['kind'],c['id']) for c in selection['components']}
        contents={f".ai/core/{component_root(r['kind'])}/{r['owner']}/{r['member']}":parent.contents[r['path']]
                  for r in parent.inventory['files'] if (r['kind'],r['owner']) in selected}
        templates={a['id']:parent.contents[f"adapters/{a['id']}/{a['template']}"] for a in selection['adapters']}
        inventory,projected=catalog.project_members(parent.document,parent.inventory,selection,contents,templates)
        catalog.subset_inventory(parent.document,parent.inventory,selection,inventory)
        catalog.verify_subset_contents(parent.document,parent.inventory,selection,inventory,projected)
        return selection,inventory,projected

    def test_preset_projects_canonical_role_and_exact_codex_profile(self):
        parent=self.role_catalog()
        desired=catalog.expand_preset(parent,'tiny','1.0.0')
        self.assertEqual((desired['selection_version'],desired['sub_agents']),(3,['context-translator']))
        _,inventory,contents=self.projection(parent,desired)
        role='.ai/core/sub-agents/context-translator/'
        self.assertEqual(contents['.codex/agents/context-translator.toml'],contents[role+'runtime/codex.toml'])
        self.assertNotIn('.codex/config.toml',contents)
        self.assertNotIn('.claude/agents/context-translator.md',contents)
        self.assertEqual(len(contents),len(inventory['files']))
        self.assertTrue(all('skill/' not in r['owner'] for r in inventory['files']))

    def test_translator_claude_and_mixed_skill_selection(self):
        parent=self.role_catalog()
        desired=catalog.expand_preset(parent,'tiny','1.0.0')
        del desired['expanded_from']
        desired['adapters']=['claude','codex']; desired['skills']=['reviewer']
        _,_,contents=self.projection(parent,desired)
        self.assertIn('.claude/agents/context-translator.md',contents)
        self.assertIn('.agents/skills/reviewer/SKILL.md',contents)
        self.assertIn('.claude/skills/reviewer/SKILL.md',contents)

    def test_legacy_selection_does_not_implicitly_install_roles(self):
        parent=self.role_catalog()
        for version in (1,2):
            desired={'selection_version':version,'catalog':parent.pin,'skills':['reviewer'],
                     'knowledge':[],'adapters':['codex'],'bindings':[]}
            if version==2: desired['skill_naming']='original'
            before=json_bytes(desired)
            _,_,contents=self.projection(parent,desired)
            self.assertFalse(any('sub-agents/' in path or '/agents/' in path for path in contents))
            self.assertEqual(json_bytes(desired),before)
            desired['sub_agents']=[]
            with self.assertRaises(ValueError): catalog.resolve_selection(parent,desired)

    def test_unknown_duplicate_and_unsupported_role_adapter_fail_closed(self):
        parent=self.role_catalog('mechanical-evidence-worker')
        desired=catalog.expand_preset(parent,'tiny','1.0.0')
        for field,value in (('sub_agents',['missing']),('sub_agents',['mechanical-evidence-worker']*2),('adapters',['missing'])):
            bad=deepcopy(desired); del bad['expanded_from']; bad[field]=value
            with self.subTest(field=field,value=value),self.assertRaises(ValueError): catalog.resolve_selection(parent,bad)

    def test_each_role_projects_exact_claude_and_dual_adapter_bytes(self):
        from test_skill_naming import ROOT
        roles=sorted(path.name for path in (ROOT/'src/sub-agents').iterdir() if (path/'sub-agent-package.yaml').is_file())
        self.assertEqual(len(roles),6)
        for role in roles:
            for adapters in (['claude'],['claude','codex']):
                with self.subTest(role=role,adapters=adapters):
                    parent=self.role_catalog(role)
                    desired=catalog.expand_preset(parent,'tiny','1.0.0')
                    del desired['expanded_from']; desired['adapters']=adapters
                    _,_,contents=self.projection(parent,desired)
                    self.assertEqual(contents[f'.claude/agents/{role}.md'],contents[f'.ai/core/sub-agents/{role}/runtime/claude.md'])
                    self.assertNotIn('.claude/settings.json',contents)
                    if 'codex' not in adapters: self.assertNotIn(f'.codex/agents/{role}.toml',contents)

    def test_claude_model_and_writable_or_unbounded_profiles_are_refused(self):
        from distribution.content import check_sub_agent, sub_agent_entries
        from test_skill_naming import source_blob
        parent=self.role_catalog('mechanical-evidence-worker')
        package=parent.packages[('sub-agent','mechanical-evidence-worker')]
        blobs={m:source_blob(m,parent.contents['packages/sub-agent/mechanical-evidence-worker/'+m]) for m in package.members}
        original=blobs['runtime/claude.md'].data.decode()
        check_sub_agent(package,blobs)
        crlf=dict(blobs)
        crlf['runtime/claude.md']=source_blob('runtime/claude.md',original.replace('\r\n','\n').replace('\n','\r\n').encode())
        check_sub_agent(package,crlf)
        original=original.replace('\r\n','\n')
        for altered in (original.replace('Read, Grep, Glob','Read, Write, Glob'),
                        original.replace('tools: Read, Grep, Glob\n',''),
                        '\n'.join('description: ""' if line.startswith('description:') else line for line in original.splitlines())+'\n'):
            with self.subTest(profile=altered),self.assertRaises(ValueError):
                changed=dict(blobs); changed['runtime/claude.md']=source_blob('runtime/claude.md',altered.encode())
                check_sub_agent(package,changed)
        with self.assertRaisesRegex(ValueError,'unsupported sub-agent adapter'):
            sub_agent_entries({'id':'test','members':['runtime/codex.toml']},[{'id':'claude'}])
        for role in ('mechanical-evidence-worker','context-translator'):
            parent=self.role_catalog(role); package=parent.packages[('sub-agent',role)]
            blobs={m:source_blob(m,parent.contents[f'packages/sub-agent/{role}/'+m]) for m in package.members}
            raw=blobs['runtime/claude.md'].data.decode().replace('\r\n','\n')
            for altered in (raw.replace('model: inherit','model: claude-fable-5-1'),
                            raw.replace('model: inherit\n',''),
                            raw.replace('model: inherit','model: inherit\neffort: max')):
                with self.subTest(role=role),self.assertRaisesRegex(ValueError,'Claude model'):
                    changed=dict(blobs); changed['runtime/claude.md']=source_blob('runtime/claude.md',altered.encode())
                    check_sub_agent(package,changed)

    def test_current_roles_inherit_models_without_observation_or_generation_pins(self):
        import tomllib
        from test_skill_naming import ROOT
        roles=sorted(p.name for p in (ROOT/'src/sub-agents').iterdir() if (p/'sub-agent-package.yaml').is_file())
        for role in roles:
            with self.subTest(role=role):
                parent=self.role_catalog(role); desired=catalog.expand_preset(parent,'tiny','1.0.0')
                desired['adapters']=['claude','codex']; desired.pop('expanded_from')
                _,_,contents=self.projection(parent,desired)
                profile=tomllib.loads(contents[f'.codex/agents/{role}.toml'].decode())
                self.assertFalse({'model','model_reasoning_effort','model_provider'} & profile.keys())
                self.assertIn(b'\nmodel: inherit\n',contents[f'.claude/agents/{role}.md'])
                self.assertNotIn('model_resolution',desired)

    def test_discovery_does_not_pin_or_escalate_inherited_roles(self):
        parent=self.role_catalog('fixed-head-independent-auditor')
        desired=catalog.expand_preset(parent,'tiny','1.0.0')
        for models in ([], [('gpt-6-astra',['max'])], [('gpt-99-future',['ultra'])]):
            with self.subTest(models=models):
                selected=catalog.resolve_sub_agent_model_selection(parent,desired,self.availability(models))
                self.assertEqual(selected,desired)
                _,_,contents=self.projection(parent,selected)
                self.assertNotIn(b'model =',contents['.codex/agents/fixed-head-independent-auditor.toml'])
        for observations in (self.availability([],source='anthropic-api'),self.availability([],adapter='claude'),
                             self.availability([('claude-fable-5-1',[])])):
            with self.assertRaises(ValueError): catalog.resolve_sub_agent_model_selection(parent,desired,observations)

    def test_inherited_role_rejects_fixed_model_binding_and_profile(self):
        from distribution.content import check_sub_agent
        from test_skill_naming import source_blob
        parent=self.role_catalog(); desired=catalog.expand_preset(parent,'tiny','1.0.0')
        desired['model_resolution']={'policy_version':1,'observations':self.availability([('gpt-6-astra',['max'])]),
            'bindings':[{'adapter':'codex','sub_agent':'context-translator','model':'gpt-6-astra','reasoning_effort':'max'}]}
        with self.assertRaisesRegex(ValueError,'inherited model policy'):
            catalog.resolve_selection(parent,desired)
        with self.assertRaisesRegex(ValueError,'explicit removal'):
            catalog.resolve_sub_agent_model_selection(parent,desired,desired['model_resolution']['observations'])
        package=parent.packages[('sub-agent','context-translator')]
        blobs={m:source_blob(m,parent.contents['packages/sub-agent/context-translator/'+m]) for m in package.members}
        for line in ('model = "gpt-6-astra"','model_reasoning_effort = "max"','model_provider = "another"'):
            changed=dict(blobs)
            changed['runtime/codex.toml']=source_blob('runtime/codex.toml',line.encode()+b'\n'+blobs['runtime/codex.toml'].data)
            with self.assertRaisesRegex(ValueError,'inherited Codex'):
                check_sub_agent(package,changed)

    def test_runtime_tamper_and_destination_escape_are_rejected(self):
        parent=self.role_catalog()
        desired=catalog.expand_preset(parent,'tiny','1.0.0')
        selection,inventory,contents=self.projection(parent,desired)
        bad=deepcopy(inventory)
        row=next(r for r in bad['files'] if r['kind']=='runtime')
        row['destination']='.codex/config.toml'
        with self.assertRaises(ValueError): catalog.subset_inventory(parent.document,parent.inventory,selection,bad)
        contents['.codex/agents/context-translator.toml']+=b'\n# changed\n'
        with self.assertRaises(ValueError): catalog.verify_subset_contents(parent.document,parent.inventory,selection,inventory,contents)

    def test_metadata_and_reference_closure_reject_missing_or_escaped_members(self):
        from distribution.content import load_sub_agent_package, check_sub_agent
        from test_skill_naming import source_blob
        parent=self.role_catalog()
        package=parent.packages[('sub-agent','context-translator')]
        for bad in (True,1.0,'1',2):
            metadata=deepcopy(package.metadata); metadata['sub_agent_package_version']=bad
            with self.subTest(version=bad),self.assertRaises(ValueError):
                load_sub_agent_package(source_blob('sub-agent-package.yaml',json_bytes(metadata)))
        blobs={m:source_blob(m,parent.contents['packages/sub-agent/context-translator/'+m]) for m in package.members}
        role=yaml_object(blobs['sub-agent.yaml'].data,'role')
        role['references']=['../../AGENTS.md']
        blobs['sub-agent.yaml']=source_blob('sub-agent.yaml',json_bytes(role))
        with self.assertRaises(ValueError): check_sub_agent(package,blobs)


if __name__=='__main__':
    if not sys.flags.isolated or not sys.flags.dont_write_bytecode: raise SystemExit('Use -I -B.')
    unittest.main()
