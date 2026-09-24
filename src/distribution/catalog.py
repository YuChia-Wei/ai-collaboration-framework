"""Immutable catalog, source-free subset, and installed-resource semantic owner."""
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timezone
from hashlib import sha1, sha256
import os
from pathlib import Path
import stat
import sys
import uuid
from .data import json_bytes, require, yaml_object
from .contracts import validate
from .content import (load_content_package, component_shape, descriptor, closure, desired_shape,
                      dependency_key, ordered, portable, resource_bindings, selected_references)
from .git_source import Blob, GitSource
from .package import load_package, check_references
from .codex import project_entry_v2 as codex_entry
from .claude import project_entry_v2 as claude_entry
from . import installation_state as state

PARENT_METADATA=('metadata/catalog.json','metadata/catalog-files.json')
SUBSET_METADATA=(*PARENT_METADATA,'metadata/selection.json','metadata/files.json','metadata/build.json')
TEMPLATES=('src/adapters/claude/skill-entry-v2.md.template','src/adapters/codex/skill-entry-v2.md.template',
           'src/adapters/codex/skill-entry.md.template')
MODULES=('__init__','assembly','catalog','claude','codex','content','contracts','data','git_source',
         'installation','installation_io','installation_plan','installation_state','maintenance_coordination','package','selection')
ENGINE_FILES=tuple(sorted([f'src/distribution/{name}.py' for name in MODULES]+['src/tools/maintain_framework.py','tools/build-catalog.py','tools/derive-subset.py']+list(TEMPLATES)))
GENERATOR_FILES=tuple(sorted([f'src/distribution/{name}.py' for name in MODULES]+['src/tools/maintain_framework.py',
                         'tools/build-catalog.py','tools/derive-subset.py']+list(TEMPLATES)))


def digest(raw): return sha256(raw).hexdigest()


def source_bytes(source, raw):
    validate('Source',source)
    state._relative(source['path']); state._descriptor(source)
    require(len(raw)==source['size'] and digest(raw)==source['sha256'],'source byte identity mismatch')
    oid=(sha1 if len(source['git_blob'])==40 else sha256)(b'blob '+str(len(raw)).encode('ascii')+b'\0'+raw).hexdigest()
    require(oid==source['git_blob'],'source Git blob identity mismatch')


def exact_tree(reader,root,expected):
    portable(sorted(expected))
    dirs={'/'.join(n.split('/')[:i]) for n in expected for i in range(1,len(n.split('/')))}
    pending=[(root,'')]; found=set()
    while pending:
        folder,prefix=pending.pop()
        for entry in reader.listing(folder).values():
            name=prefix+entry; state._relative(name)
            info=(folder/entry).lstat(); state._plain(info,name)
            if stat.S_ISDIR(info.st_mode):
                require(name in dirs,'extra artifact directory')
                pending.append((folder/entry,name+'/'))
            else:
                require(name in expected and stat.S_ISREG(info.st_mode) and info.st_nlink==1,'extra/nonregular artifact member')
                found.add(name)
    require(found==expected,'artifact member closure mismatch')


def read_raw(reader,root,name,limit=None):
    target=reader.locate(root,name)
    require(target is not None,'required artifact member missing: '+name)
    return reader.read(target,name,limit or state.LIMITS['document_bytes'])


def identity(kind,doc,raw):
    inputs={name:digest(value) for name,value in raw.items() if name!='metadata/build.json'}
    prefix='catalog:1' if kind=='catalog' else 'subset:3'
    return f"{prefix}:{doc['release_version']}:{doc['source']['commit']}:{digest(json_bytes(inputs))}",inputs


def parent_documents(raw):
    doc=validate('Catalog',state._document(raw[PARENT_METADATA[0]],PARENT_METADATA[0]))
    files=validate('CatalogFiles',state._document(raw[PARENT_METADATA[1]],PARENT_METADATA[1]))
    require(len(doc['components'])<=128,'catalog component budget')
    closure(doc['components'])
    ordered(doc['adapters'],lambda r:r['id']); ordered(doc['presets'],lambda r:r['id'])
    ordered(doc['build_inputs'],lambda r:r['path']); portable([r['path'] for r in doc['build_inputs']])
    inputs={r['path']:r for r in doc['build_inputs']}
    for row in inputs.values():
        state._descriptor(row); state._relative(row['path'])
        require(len(row['git_blob'])==len(doc['source']['commit'])==len(doc['source']['tree']),'mixed Git object formats')
    require(doc['generator']['id']=='aicf-catalog-assembly','unsupported-generator')
    implementation=doc['generator']['implementation']
    require([r['path'] for r in implementation]==list(GENERATOR_FILES),'generator implementation closure')
    require(all(inputs.get(r['path'])==r for r in implementation),'generator/source binding')
    expected=set(GENERATOR_FILES)|{'src/distribution/manifest.yaml'}
    for preset in doc['presets']:
        for key in ('skills','knowledge','adapters'): ordered(preset[key])
        expected.add(f"src/profiles/{preset['id']}.yaml")
    members={}
    for component in doc['components']:
        for member in component['members']:
            kind,pid=dependency_key(component)
            source=f"src/{'skills' if kind=='skill' else 'knowledge'}/{pid}/{member}"
            expected.add(source)
            members[f'packages/{kind}/{pid}/{member}']=(kind,pid,member,source)
    for adapter in doc['adapters']:
        ordered(adapter['members']); portable(adapter['members'])
        require(adapter['template']=='skill-entry-v2.md.template' and adapter['template'] in adapter['members'],'adapter template branch')
        for member in adapter['members']:
            source=f"src/adapters/{adapter['id']}/{member}"
            expected.add(source)
            members[f"adapters/{adapter['id']}/{member}"]=('adapter',adapter['id'],member,source)
    require(set(inputs)==expected,'build-input-closure')
    ordered(files['files'],lambda r:r['path']); portable([r['path'] for r in files['files']])
    require({r['path'] for r in files['files']}==set(members),'catalog file closure')
    for row in files['files']:
        require((row['kind'],row['owner'],row['member'],row['source']['path'])==members[row['path']]
                and inputs.get(row['source']['path'])==row['source'],'catalog member/source binding')
    require(sum(r['source']['size'] for r in files['files'])+sum(len(b) for b in raw.values())<=state.LIMITS['total_bytes'],'catalog byte budget')
    ident,_=identity('catalog',doc,{n:raw[n] for n in PARENT_METADATA})
    pin={'identity':ident,'catalog_sha256':digest(raw[PARENT_METADATA[0]]),'files_sha256':digest(raw[PARENT_METADATA[1]])}
    return doc,files,pin


def build_document(raw,kind,doc,identity_inputs,ident):
    build=validate('Build',state._document(raw,'metadata/build.json'))
    require(build['artifact_kind']==kind and build['identity']==ident and build['identity_inputs']==identity_inputs,'build identity mismatch')
    require(build['mode_materialization']==('inventory-only' if build['runtime']['os']=='nt' else 'posix-permissions'),'build mode mismatch')
    require([r['source'] for r in build['executing_implementation']]==doc['generator']['implementation'],'build implementation binding')
    require(all(r['source']['sha256']==r['execution_file_sha256'] for r in build['executing_implementation']),'execution/source hash mismatch')
    return build


@dataclass(frozen=True)
class Catalog:
    root: Path | None
    document: dict
    inventory: dict
    pin: dict
    metadata_bytes: dict
    contents: dict
    packages: dict


def packages_from(doc,files,contents,selected=None):
    rows={(r['kind'],r['owner'],r['member']):r for r in files['files']}
    packages={}; payload={}
    for c in doc['components']:
        key=dependency_key(c)
        if selected is not None and key not in selected: continue
        blobs={}
        for member in c['members']:
            row=rows[(*key,member)]; raw=contents[row['path']]
            source_bytes(row['source'],raw)
            src=row['source']; blobs[member]=Blob(src['path'],src['git_blob'],src['mode'],raw)
            payload[(*key,member)]=raw
        metadata=blobs[c['metadata']]
        state._yaml_bound(metadata.data,metadata.path)
        package=load_package(metadata) if c['kind']=='skill' else load_content_package(metadata)
        require(descriptor(c['kind'],package)==c,'metadata/component descriptor mismatch')
        if c['kind']=='skill': check_references(package,blobs)
        packages[key]=package
    selected_references(packages,payload)
    return packages


def read_catalog(root,expected_identity):
    reader=state._Reader(); root=state._root(str(root))
    raw={n:read_raw(reader,root,n) for n in (*PARENT_METADATA,'metadata/build.json')}
    doc,files,pin=parent_documents(raw)
    require(expected_identity==pin['identity'] or expected_identity==pin,'identity-mismatch: expected catalog pin')
    ident,inputs=identity('catalog',doc,{n:raw[n] for n in PARENT_METADATA})
    build_document(raw['metadata/build.json'],'catalog',doc,inputs,ident)
    exact_tree(reader,root,set(raw)|{r['path'] for r in files['files']})
    policy='posix-permissions' if os.name=='posix' else 'windows-inventory-only'
    contents={r['path']:reader.member(root,{**r['source'],'path':r['path']},policy) for r in files['files']}
    packages=packages_from(doc,files,contents)
    return Catalog(root,doc,files,pin,raw,contents,packages)


def resolve_selection(catalog,desired):
    if type(desired) is bytes: desired=state._document(desired,'installation.json',canonical=False)
    desired=desired_shape(desired)
    require(desired['catalog']==catalog.pin,'identity-mismatch: desired parent')
    keys={('skill',i) for i in desired['skills']}|{('knowledge',i) for i in desired['knowledge']}
    components=[c for c in catalog.document['components'] if dependency_key(c) in keys]
    require({dependency_key(c) for c in components}==keys,'selection-unavailable')
    adapters=[r for r in catalog.document['adapters'] if r['id'] in desired['adapters']]
    require([r['id'] for r in adapters]==desired['adapters'],'selection-unavailable: adapter')
    closure(components)
    if 'expanded_from' in desired:
        trace=desired['expanded_from']; preset=next((p for p in catalog.document['presets'] if p['id']==trace['id'] and p['version']==trace['version']),None)
        require(preset is not None and trace['catalog_identity']==catalog.pin['identity'] and trace['preset_sha256']==digest(json_bytes(preset)),'preset provenance mismatch')
    packages={k:p for k,p in catalog.packages.items() if k in keys}
    require(set(packages)==keys,'selected metadata unavailable')
    observations=resource_bindings(packages,desired)
    payload={(r['kind'],r['owner'],r['member']):catalog.contents[r['path']] for r in catalog.inventory['files']
             if (r['kind'],r['owner']) in keys}
    unavailable=selected_references(packages,payload)
    return {'desired':desired,'desired_sha256':digest(json_bytes(desired)),'components':components,'adapters':adapters,
            'binding_observations':observations,'unavailable':unavailable}


def expand_preset(catalog,id,version):
    preset=next((p for p in catalog.document['presets'] if p['id']==id and p['version']==version),None)
    require(preset is not None,'selection-unavailable: preset')
    desired={'selection_version':1,'catalog':catalog.pin,**{k:preset[k] for k in ('skills','knowledge','adapters')},'bindings':[],
             'expanded_from':{'id':id,'version':version,'catalog_identity':catalog.pin['identity'],'preset_sha256':digest(json_bytes(preset))}}
    resolve_selection(catalog,desired)
    return desired


def template_bytes(adapter,expected,provided=None):
    name=f"src/adapters/{adapter}/skill-entry-v2.md.template"
    if provided is not None: raw=provided
    else:
        captured=getattr(sys.modules.get('_aicf_verified_bootstrap', sys.modules.get('__main__')),'_framework_engine_bytes',{})
        if name in captured: raw=captured[name]
        else:
            # Explicit executing implementation resource, never cwd/source discovery.
            root=state._root(str(Path(__file__).absolute().parents[2]))
            raw=read_raw(state._Reader(),root,name,state.LIMITS['file_bytes'])
    require(digest(raw)==expected,'unsupported-adapter: template differs from verified implementation')
    return raw


def project_members(doc,files,selection,contents,templates=None):
    selected={dependency_key(c) for c in selection['components']}
    rows=[]; output={}; indexed={(r['kind'],r['owner'],r['member']):r for r in files['files']}
    for c in selection['components']:
        kind,pid=dependency_key(c); destinations={m:f".ai/core/{'skills' if kind=='skill' else 'knowledge'}/{pid}/{m}" for m in c['members']}
        for member,dest in destinations.items():
            src=indexed[(kind,pid,member)]['source']; raw=contents[dest]
            source_bytes(src,raw)
            row={'path':'payload/'+dest,'destination':dest,'owner':kind+'/'+pid,'kind':'payload',
                 **{k:src[k] for k in ('mode','size','sha256')},'source':src,'binding':None}
            rows.append(row); output[dest]=raw
        if kind!='skill': continue
        blobs={m:Blob(indexed[(kind,pid,m)]['source']['path'],indexed[(kind,pid,m)]['source']['git_blob'],indexed[(kind,pid,m)]['source']['mode'],contents[d]) for m,d in destinations.items()}
        package=load_package(blobs['skill-package.yaml']); front=check_references(package,blobs)
        for adapter in selection['adapters']:
            aid=adapter['id']; src=indexed[('adapter',aid,adapter['template'])]['source']
            raw_template=template_bytes(aid,src['sha256'],None if templates is None else templates[aid])
            renderer=codex_entry if aid=='codex' else claude_entry
            dest,raw=renderer(raw_template,pid,c['version'],front['description'],destinations,configuration=package.metadata['configuration'])
            rows.append({'path':'runtime/'+dest,'destination':dest,'owner':f'adapter/{aid}/skill/{pid}','kind':'runtime','mode':'100644',
                         'size':len(raw),'sha256':digest(raw),'source':None,
                         'binding':{'adapter':aid,'skill':pid,'entry_name':'aicf-'+pid,'core_entrypoint':destinations['SKILL.md'],'template_sha256':src['sha256']}})
            output[dest]=raw
    rows.sort(key=lambda r:r['path']); portable([r['destination'] for r in rows]); portable([r['path'] for r in rows])
    require(len(rows)<=4096 and sum(r['size'] for r in rows)<=state.LIMITS['total_bytes'],'subset materialization budget')
    return {'schema_version':2,'files':rows},output


def subset_documents(raw, *, completed=True):
    require(set(raw)==(set(SUBSET_METADATA) if completed else set(SUBSET_METADATA)-{'metadata/build.json'}),'subset metadata closure')
    doc,files,pin=parent_documents(raw)
    selection=validate('Subset',state._document(raw['metadata/selection.json'],'selection.json'))
    inventory=validate('Files',state._document(raw['metadata/files.json'],'files.json'))
    desired_shape(selection['desired'])
    require(selection['catalog']==selection['desired']['catalog']==pin and selection['source']==doc['source']
            and selection['release_version']==doc['release_version'],'subset parent binding')
    require(selection['desired_sha256']==digest(json_bytes(selection['desired'])),'desired identity mismatch')
    desired=selection['desired']; keys={('skill',i) for i in desired['skills']}|{('knowledge',i) for i in desired['knowledge']}
    require(selection['components']==[c for c in doc['components'] if dependency_key(c) in keys]
            and {dependency_key(c) for c in selection['components']}==keys,'subset component selection mismatch')
    require(selection['adapters']==[a for a in doc['adapters'] if a['id'] in desired['adapters']]
            and [a['id'] for a in selection['adapters']]==desired['adapters'],'subset adapter mismatch')
    closure(selection['components'])
    require(selection['generator']=={**doc['generator'],'id':'aicf-subset-derivation'},'derivation implementation closure')
    ordered(inventory['files'],lambda r:r['path']); portable([r['path'] for r in inventory['files']]); portable([r['destination'] for r in inventory['files']])
    require(sum(r['size'] for r in inventory['files'])+sum(len(b) for b in raw.values())<=state.LIMITS['total_bytes'],'subset byte budget')
    subset_inventory(doc,files,selection,inventory)
    for row in inventory['files']: state._descriptor(row)
    ident,inputs=identity('subset',selection,{n:b for n,b in raw.items() if n!='metadata/build.json'})
    build=build_document(raw['metadata/build.json'],'subset',selection,inputs,ident) if completed else None
    return selection,inventory,build,{r['destination']:r for r in inventory['files']},ident


def verify_subset_contents(doc,files,selection,inventory,contents):
    selected={dependency_key(c) for c in selection['components']}
    parent_contents={}
    for c in selection['components']:
        kind,pid=dependency_key(c)
        for member in c['members']:
            dest=f".ai/core/{'skills' if kind=='skill' else 'knowledge'}/{pid}/{member}"
            require(dest in contents,'missing selected payload')
            parent_contents[f'packages/{kind}/{pid}/{member}']=contents[dest]
    packages=packages_from(doc,files,parent_contents,selected)
    fake=Catalog(None,doc,files,selection['catalog'],{},parent_contents,packages)
    resolve_selection(fake,selection['desired'])
    expected,projected=project_members(doc,files,selection,contents)
    require(expected==inventory and projected==contents,'subset projection/inventory/content mismatch')
    return packages


def read_subset(root,reader=None):
    reader=reader or state._Reader(); root=state._root(str(root))
    raw={n:read_raw(reader,root,n) for n in SUBSET_METADATA}
    selection,inventory,build,members,ident=subset_documents(raw)
    exact_tree(reader,root,set(raw)|{r['path'] for r in members.values()})
    policy='posix-permissions' if os.name=='posix' else 'windows-inventory-only'
    contents={n:reader.member(root,row,policy) for n,row in members.items()}
    doc,files,_=parent_documents(raw)
    verify_subset_contents(doc,files,selection,inventory,contents)
    return state.Candidate(root,ident,selection,inventory,build,raw,members,contents)


def lock_document(candidate,engine,installation_id,mode_policy,project_inputs):
    raw=candidate.metadata_bytes
    return {'lock_version':2,'installation_id':installation_id,'engine':engine,'mode_policy':mode_policy,
            'candidate_identity':candidate.identity,'catalog_document':state._document(raw[PARENT_METADATA[0]],PARENT_METADATA[0]),
            'catalog_inventory':state._document(raw[PARENT_METADATA[1]],PARENT_METADATA[1]),'selection':candidate.selection,
            'inventory':candidate.inventory,'project_inputs':project_inputs}


def lock_bytes(raw):
    doc=validate('Lock',state._document(raw,state.LOCK_PATH))
    # Locks omit completion receipts. Reuse identity/shape checks explicitly
    # without fabricating completion time or execution evidence.
    metadata={PARENT_METADATA[0]:json_bytes(doc['catalog_document']),PARENT_METADATA[1]:json_bytes(doc['catalog_inventory']),
              'metadata/selection.json':json_bytes(doc['selection']),'metadata/files.json':json_bytes(doc['inventory'])}
    ident,inputs=identity('subset',doc['selection'],metadata)
    _,_,_,members,_=subset_documents(metadata,completed=False)
    require(ident==doc['candidate_identity'],'lock identity mismatch')
    state._engine_shape(doc['engine']); require(tuple(r['path'] for r in doc['engine']['files'])==ENGINE_FILES,'lock engine closure')
    ordered(doc['project_inputs'],lambda r:r['path']); require(len(doc['project_inputs'])<=128,'project input budget')
    portable(list(members)+[state.LOCK_PATH,state.GUARD_PATH,*state.MARKERS]+[r['path'] for r in doc['project_inputs']])
    return state.InstalledLock(doc,raw,digest(raw),members)


def completion(kind,doc,ident,inputs):
    import yaml
    return {'schema_version':2,'artifact_kind':kind,'identity':ident,'identity_inputs':inputs,
            'completed_at':datetime.now(timezone.utc).isoformat(),
            'executing_implementation':[{'source':r,'execution_file_sha256':r['sha256']} for r in doc['generator']['implementation']],
            'runtime':{'python':sys.version.split()[0],'pyyaml':yaml.__version__,'os':os.name},
            'mode_materialization':'inventory-only' if os.name=='nt' else 'posix-permissions',
            'installation':'not-performed','behavioral_validation':'not-performed','publication':'not-performed'}


def read_installed_resources(project_root,expected_lock_sha256,authorities):
    """Read-only S5 seam; explicit authority allowlist, no applicability evaluator.

    Returns index rows with verified member bytes, declared resource selectors,
    exact saved bindings and observed raw authorities. Throws on marker/drift,
    stale lock/authority or undeclared authority access. It never saves config.
    """
    reader=state._Reader(); root=state._root(str(project_root))
    observation=state.observe_installation(str(root),_reader=reader)
    require(not observation.markers and not observation.drift and observation.lock is not None,'installed resources unavailable: marker/drift/absence')
    lock=observation.lock
    require(lock.sha256==state._digest(expected_lock_sha256) and lock.document['lock_version']==2,'installed resource lock pin mismatch')
    state._bounded(authorities)
    state._array(authorities,state.LIMITS["protected_inputs"])
    supplied={}
    for row in authorities:
        validate('Authority',row); portable([row['path']])
        key=(row['path'],row['selector']); require(key not in supplied,'duplicate authority')
        supplied[key]=row
    selected=lock.document['selection']; observed=[]
    required={ (r['path'],r['selector']):r for b in selected['desired']['bindings'] for r in b['authorities'] }
    require(supplied==required,'binding authority allowlist mismatch')
    for row in required.values():
        raw=read_raw(reader,root,row['path'])
        require(digest(raw)==row['sha256'],'binding authority drift')
        observed.append({**row,'status':'raw-hash-matched','semantic_applicability':'target-owned'})
    resources=[]
    for component in selected['components']:
        if component['kind']!='knowledge': continue
        prefix=f".ai/core/knowledge/{component['id']}/"
        name=prefix+component['metadata']; row=lock.members[name]
        raw=reader.member(root,{**row,'path':name},lock.document['mode_policy'])
        package=load_content_package(Blob(row['source']['path'],row['source']['git_blob'],row['mode'],raw))
        for resource in package.metadata['resources']:
            member=prefix+resource['path']; bound=lock.members[member]
            resources.append({'package':component['id'],'version':component['version'],'resource_id':resource['id'],
                              'member':member,'sha256':bound['sha256'],'resource':resource})
    return {'lock_sha256':lock.sha256,'candidate_identity':lock.document['candidate_identity'],
            'desired_sha256':selected['desired_sha256'],'resources':resources,'bindings':selected['desired']['bindings'],
            'authorities':observed,'semantic_applicability':'target-owned'}


def execution_sources(source=None, catalog=None):
    """Bind the entire declared generator closure to observed executing raw bytes."""
    root=state._root(str(Path(__file__).absolute().parents[2])); reader=state._Reader()
    expected={r['path']:r for r in catalog.document['generator']['implementation']} if catalog else None
    rows=[]
    for name in GENERATOR_FILES:
        raw=read_raw(reader,root,name,state.LIMITS['file_bytes'])
        row=source.read(name).identity() if source else expected[name]
        source_bytes(row,raw)
        rows.append(row)
    return rows


def emit_artifact(metadata,payload,output_root,scratch_root,kind,ident,source_root=None,parent_root=None):
    from .assembly import OwnedDirectory
    output=state._root(str(output_root)); scratch=state._root(str(scratch_root))
    roots={'output':output,'scratch':scratch}
    if output==scratch: roots.pop('scratch')
    if source_root is not None: roots['source']=source_root
    if parent_root is not None: roots['parent']=parent_root
    state._roots_disjoint(roots)
    run=uuid.uuid4().hex
    all_files={**{n:(b,'100644') for n,b in metadata.items()},**payload}
    require(len(all_files)<=4096 and sum(len(b) for b,_ in all_files.values())<=state.LIMITS['total_bytes'],'artifact output budget')
    from .installation_io import budget
    for root,label in ((output,kind+'-'+run),(scratch,'scratch-'+run)):
        budget([(label,root,label+'/'+name) for name in all_files])
    staged=OwnedDirectory(scratch,'scratch-'+run)
    published=OwnedDirectory(output,kind+'-'+run)
    for name in sorted(set(all_files)-{'metadata/build.json'}):
        raw,mode=all_files[name]; staged.write(name,raw,mode); published.write(name,staged.read(name,raw,mode),mode)
    raw,mode=all_files['metadata/build.json']; staged.write('metadata/build.json',raw,mode); published.write('metadata/build.json',raw,mode)
    if kind=='catalog': read_catalog(published.root,ident)
    else: read_subset(published.root)
    return {'outcome':'assembled','identity':ident,'artifact_root':str(published.root),'scratch_root':str(staged.root),
            'installation':'not-performed','behavioral_validation':'not-performed','publication':'not-performed'}


def build_catalog(repository,commit,release_version,output_root,scratch_root):
    from .data import distribution_version
    source=GitSource(Path(repository),commit)
    require(source.repository==state._root(str(Path(__file__).absolute().parents[2])),'executing/source root mismatch')
    manifest=validate('Manifest',yaml_object(source.read('src/distribution/manifest.yaml').data,'manifest.yaml'))
    ordered(manifest['components'],dependency_key); ordered(manifest['adapters'],lambda r:r['id']); ordered(manifest['profiles'],lambda r:r['id'])
    implementation=execution_sources(source=source)
    components=[]; adapters=[]; presets=[]; files=[]; contents={}; paths=[]
    for row in manifest['components']:
        kind,pid=dependency_key(row); prefix=f"src/{'skills' if kind=='skill' else 'knowledge'}/{pid}"
        require(row['source']==prefix and row['metadata']==('content-package.yaml' if kind=='knowledge' else 'skill-package.yaml'),'manifest component root')
        metadata=source.read(prefix+'/'+row['metadata'])
        package=load_content_package(metadata) if kind=='knowledge' else load_package(metadata)
        require(package.id==pid and package.version==row['version'],'manifest package identity')
        component=descriptor(kind,package); components.append(component)
        ordered(row['members'],lambda r:r['source'])
        require({m['source'] for m in row['members']}==package.members,'manifest metadata member closure')
        for member in row['members']:
            name=member['source']; dest=f".ai/core/{'skills' if kind=='skill' else 'knowledge'}/{pid}/{name}"
            require(member['destination']==dest,'manifest destination ownership')
            paths.append(dest); blob=source.read(prefix+'/'+name)
            artifact=f'packages/{kind}/{pid}/{name}'
            files.append({'path':artifact,'kind':kind,'owner':pid,'member':name,'source':blob.identity()}); contents[artifact]=blob.data
    portable(paths)
    for row in manifest['adapters']:
        aid=row['id']; require(row['source']==f'src/adapters/{aid}','adapter source root')
        adapter={k:row[k] for k in ('id','version','template','members')}; adapter['prefix']='aicf-'; adapters.append(adapter)
        for name in row['members']:
            blob=source.read(row['source']+'/'+name); artifact=f'adapters/{aid}/{name}'
            files.append({'path':artifact,'kind':'adapter','owner':aid,'member':name,'source':blob.identity()}); contents[artifact]=blob.data
    for row in manifest['profiles']:
        require(row['path']==f"src/profiles/{row['id']}.yaml",'preset source root')
        preset=validate('Preset',yaml_object(source.read(row['path']).data,row['path']))
        require(preset['id']==row['id'],'preset identity'); presets.append(preset)
    doc={'catalog_version':1,'release_version':distribution_version(release_version,'release_version'),
         'source':{'commit':source.commit,'tree':source.tree},'components':components,'adapters':adapters,'presets':presets,
         'build_inputs':[source.blobs[n].identity() for n in sorted(source.blobs)],
         'generator':{'id':'aicf-catalog-assembly','implementation':implementation}}
    inventory={'catalog_files_version':1,'files':sorted(files,key=lambda r:r['path'])}
    metadata={PARENT_METADATA[0]:json_bytes(doc),PARENT_METADATA[1]:json_bytes(inventory)}
    doc,inventory,pin=parent_documents(metadata)
    packages=packages_from(doc,inventory,contents)
    catalog=Catalog(None,doc,inventory,pin,metadata,contents,packages)
    for preset in presets: expand_preset(catalog,preset['id'],preset['version'])
    ident,inputs=identity('catalog',doc,metadata)
    metadata['metadata/build.json']=json_bytes(completion('catalog',doc,ident,inputs))
    payload={r['path']:(contents[r['path']],r['source']['mode']) for r in files}
    return emit_artifact(metadata,payload,output_root,scratch_root,'catalog',ident,source_root=source.repository)


def derive_subset(catalog,desired,output_root,scratch_root):
    resolved=resolve_selection(catalog,desired)
    execution_sources(catalog=catalog)
    selection={'schema_version':3,'mode':'catalog-subset','release_version':catalog.document['release_version'],
               'source':catalog.document['source'],'catalog':catalog.pin,'desired':resolved['desired'],
               'desired_sha256':resolved['desired_sha256'],'components':resolved['components'],'adapters':resolved['adapters'],
               'generator':{**catalog.document['generator'],'id':'aicf-subset-derivation'}}
    keys={dependency_key(c) for c in selection['components']}
    contents={f".ai/core/{'skills' if r['kind']=='skill' else 'knowledge'}/{r['owner']}/{r['member']}":catalog.contents[r['path']]
              for r in catalog.inventory['files'] if (r['kind'],r['owner']) in keys}
    templates={r['id']:catalog.contents[f"adapters/{r['id']}/{r['template']}"] for r in selection['adapters']}
    inventory,contents=project_members(catalog.document,catalog.inventory,selection,contents,templates)
    metadata={n:catalog.metadata_bytes[n] for n in PARENT_METADATA}
    metadata.update({'metadata/selection.json':json_bytes(selection),'metadata/files.json':json_bytes(inventory)})
    ident,inputs=identity('subset',selection,metadata)
    metadata['metadata/build.json']=json_bytes(completion('subset',selection,ident,inputs))
    subset_documents(metadata)
    payload={r['path']:(contents[r['destination']],r['mode']) for r in inventory['files']}
    return emit_artifact(metadata,payload,output_root,scratch_root,'subset',ident,parent_root=catalog.root,
                         source_root=state._root(str(Path(__file__).absolute().parents[2])))


def package_engine(repository,commit,output_root):
    """Explicit standalone bundle; descriptor is not a substitute for caller trust."""
    from .assembly import OwnedDirectory
    source=GitSource(Path(repository),commit)
    execution_sources(source=source)
    output=state._root(str(output_root)); state._roots_disjoint({'source':source.repository,'output':output})
    blobs={n:source.read(n) for n in ENGINE_FILES}
    pin={'id':'framework-managed-installation','version':'2.0.0','source_commit':commit,
         'files':[{'path':n,'sha256':digest(blobs[n].data)} for n in ENGINE_FILES]}
    from .installation_io import budget
    name='engine-'+uuid.uuid4().hex
    budget([('engine',output,name+'/'+n) for n in (*ENGINE_FILES,'engine.json')])
    bundle=OwnedDirectory(output,name)
    for n,blob in blobs.items(): bundle.write(n,blob.data,blob.mode)
    bundle.write('engine.json',json_bytes({'engine_package_version':1,'engine':pin}))
    exact_tree(state._Reader(),bundle.root,set(ENGINE_FILES)|{'engine.json'})
    return {'engine_root':str(bundle.root),'engine':pin,'execution':'not-performed'}


def subset_inventory(doc,files,selection,inventory):
    """Admit exact destinations/ownership before any installed-file read."""
    indexed={(r['kind'],r['owner'],r['member']):r['source'] for r in files['files']}
    expected={}
    for component in selection['components']:
        kind,pid=dependency_key(component)
        for member in component['members']:
            dest=f".ai/core/{'skills' if kind=='skill' else 'knowledge'}/{pid}/{member}"
            source=indexed[(kind,pid,member)]
            expected[dest]={'path':'payload/'+dest,'destination':dest,'owner':kind+'/'+pid,'kind':'payload',
                            **{k:source[k] for k in ('sha256','size','mode')},'source':source,'binding':None}
        if kind=='skill':
            for adapter in selection['adapters']:
                aid=adapter['id']; runtime='.agents' if aid=='codex' else '.claude'
                dest=f'{runtime}/skills/aicf-{pid}/SKILL.md'
                expected[dest]={'path':'runtime/'+dest,'destination':dest,'owner':f'adapter/{aid}/skill/{pid}','kind':'runtime',
                                'mode':'100644','source':None,
                                'binding':{'adapter':aid,'skill':pid,'entry_name':'aicf-'+pid,'core_entrypoint':f'.ai/core/skills/{pid}/SKILL.md',
                                           'template_sha256':indexed[('adapter',aid,adapter['template'])]['sha256']}}
    require({r['destination'] for r in inventory['files']}==set(expected),'subset inventory closure')
    for row in inventory['files']:
        require(all(row[k]==v for k,v in expected[row['destination']].items()),'subset inventory ownership/source binding')
