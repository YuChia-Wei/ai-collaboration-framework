"""Narrow RC2 contract fixtures for S6. Authoring is not execution evidence.

Run only after owner selection: python -I -B tests/framework_next/test_rc2_distribution.py
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


class Rc2DistributionTests(unittest.TestCase):
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
        raw={'metadata/catalog.json':json_bytes(parent),'metadata/catalog-files.json':json_bytes({'catalog_files_version':1,'files':[]})}
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


if __name__=='__main__':
    if not sys.flags.isolated or not sys.flags.dont_write_bytecode: raise SystemExit('Use -I -B.')
    unittest.main()
