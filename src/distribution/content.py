"""Content metadata and exact typed selection semantics (no target rule evaluator)."""
from __future__ import annotations
from dataclasses import dataclass
from hashlib import sha256
import posixpath
import re
from urllib.parse import unquote, urlsplit
from .data import Paths, json_bytes, require, yaml_object
from .contracts import validate
from .package import Package


def ordered(rows, key=lambda x:x):
    keys=[key(x) for x in rows]
    require(keys == sorted(keys) and len(keys)==len(set(keys)), "duplicate identity or unsorted set")


def portable(names):
    from .installation_state import _relative
    paths=Paths()
    for name in names:
        _relative(name)
        paths.add(name,"rc2 member")


def dependency_key(row):
    return row['kind'],row['id']


def dependencies(required, optional, owner=None):
    require(len(required)+len(optional)<=128,"component dependency budget")
    for rows,typ in ((required,'Dependency'),(optional,'OptionalDependency')):
        for row in rows: validate(typ,row)
        ordered(rows,dependency_key)
    left={dependency_key(r) for r in required}
    right={dependency_key(r) for r in optional}
    require(not left & right and owner not in left|right,"self/overlapping dependency")


def load_content_package(blob):
    data=validate('ContentPackage',yaml_object(blob.data,blob.path))
    members=data['members']
    ordered(members,lambda x:x['path'])
    portable([r['path'] for r in members])
    kinds={r['path']:r['kind'] for r in members}
    require(data['entrypoint']=='README.md' and kinds.get('README.md')=='index'
            and kinds.get('content-package.yaml')=='metadata','content entry/metadata binding')
    ordered(data['resources'],lambda x:x['id'])
    for r in data['resources']:
        require(r['path'] in kinds and (kinds[r['path']]==r['kind'] or kinds[r['path']] in {'index','metadata'}),'resource member/kind binding')
        for key in ('rule_ids','capabilities','operations'): ordered(r[key])
        require(not r['rule_ids'] or r['kind'] in {'normative-rule','rule-catalog'},'ordinary resource cannot allocate rules')
    deps=data['dependencies']
    dependencies(deps['required'],deps['optional'],('knowledge',data['id']))
    require(all(r['kind']=='knowledge' for r in deps['required']+deps['optional']),'knowledge dependencies must be knowledge')
    ordered(data['references'],lambda r:(r['from'],r['resource_id'],r['target']['package'],r['target']['path'],r['target']['anchor'] or ''))
    for r in data['references']:
        require(r['from'] in kinds,'reference source member missing')
        portable([r['target']['path']])
        target=r['target']['package']
        if target != data['id']:
            candidates=deps['required'] if r['requirement']=='required' else deps['required']+deps['optional']
            dep=next((d for d in candidates if d['id']==target),None)
            require(dep is not None,'cross-package reference requires matching dependency')
    return Package(data,frozenset(kinds))


def component_root(kind):
    require(kind in {'skill','knowledge','sub-agent'}, 'unsupported component kind')
    return {'skill':'skills','knowledge':'knowledge','sub-agent':'sub-agents'}[kind]


def selected_keys(desired):
    return {(kind, pid) for kind, field in (('skill','skills'),('knowledge','knowledge'),('sub-agent','sub_agents'))
            for pid in desired.get(field, [])}


def load_sub_agent_package(blob):
    data=validate('SubAgentPackage',yaml_object(blob.data,blob.path))
    ordered(data['members']); portable(data['members'])
    require({'sub-agent.yaml','sub-agent-package.yaml'}<=set(data['members']), 'sub-agent entry/metadata closure')
    dependencies(data['dependencies']['required'],data['dependencies']['optional'],('sub-agent',data['id']))
    require(not data['dependencies']['required'] and not data['dependencies']['optional'], 'sub-agent dependencies are caller-owned')
    runtime={m for m in data['members'] if m.startswith('runtime/')}
    require(runtime and runtime<={'runtime/codex.toml','runtime/claude.md'}, 'unsupported sub-agent runtime member')
    return Package(data,frozenset(data['members']))


def sub_agent_entries(component, adapters):
    entries=[]
    for adapter in adapters:
        aid=adapter['id']; suffix='.toml' if aid=='codex' else '.md'
        member='runtime/'+aid+suffix
        require(member in component['members'], 'unsupported sub-agent adapter: '+component['id']+'/'+aid)
        entries.append((aid,member,f'.{aid}/agents/'+component['id']+suffix))
    return entries


def check_sub_agent(package, blobs):
    import tomllib
    role=yaml_object(blobs['sub-agent.yaml'].data,'sub-agent.yaml')
    policy=sub_agent_model_policy(role)
    require(role.get('asset_id')==package.id and role.get('asset_type')=='sub-agent-role-prompt'
            and role.get('status')=='active', 'sub-agent role identity')
    refs=role.get('references'); require(type(refs) is list, 'sub-agent references')
    ordered(refs); portable(refs)
    require(set(refs)<=(package.members-{'sub-agent.yaml','sub-agent-package.yaml'})
            and all(ref.startswith('references/') for ref in refs), 'sub-agent reference closure')
    runtime={m for m in package.members if m.startswith('runtime/')}
    require(package.members==frozenset({'sub-agent.yaml','sub-agent-package.yaml',*refs,*runtime}), 'sub-agent member closure')
    targets=['codex'] if 'runtime/codex.toml' in runtime else []
    if 'runtime/claude.md' in runtime: targets.append('claude')
    require(role.get('wrapper_targets')==targets, 'sub-agent adapter declaration')
    canonical=f'.ai/core/sub-agents/{package.id}/sub-agent.yaml'
    for aid,member,dest in sub_agent_entries({'id':package.id,'members':package.members},[{'id':a} for a in targets]):
        raw=blobs[member].data.decode('utf-8')
        if aid=='codex':
            profile=tomllib.loads(raw)
            require(profile.get('model')==policy[aid]['candidates'][0]
                    and profile.get('model_reasoning_effort')==policy[aid]['reasoning_effort'], 'sub-agent Codex model')
            require(profile.get('name')==package.id and canonical in profile.get('developer_instructions',''), 'sub-agent Codex binding')
            require(type(profile.get('description')) is str and bool(profile['description'].strip()), 'sub-agent Codex description')
            require(package.id=='context-translator' or profile.get('sandbox_mode')=='read-only', 'sub-agent read-only profile')
        else:
            match=re.fullmatch(r'---\n(.*?)\n---\n([\s\S]*)',raw.replace('\r\n','\n'),re.S)
            require(match is not None, 'sub-agent Claude frontmatter')
            profile=yaml_object(match[1].encode(),'Claude frontmatter')
            require(profile.get('name')==package.id and canonical in match[2], 'sub-agent Claude binding')
            require(profile.get('model')==policy[aid]['candidates'][0], 'sub-agent Claude model')
            require(type(profile.get('description')) is str and bool(profile['description'].strip()), 'sub-agent Claude description')
            tools=profile.get('tools')
            if type(tools) is str: tools=[tool.strip() for tool in tools.split(',')]
            require(type(tools) is list and all(type(tool) is str for tool in tools), 'sub-agent Claude tool allowlist')
            allowed={'Read','Write','Edit'} if package.id=='context-translator' else {'Read','Grep','Glob'}
            require(set(tools)==allowed and len(tools)==len(allowed), 'sub-agent Claude bounded tools')
        require('.dev/agents/' not in raw and 'src/sub-agents/' not in raw, 'sub-agent nonportable runtime reference')
        require(role.get('adapter_metadata',{}).get(aid,{}).get('adapter_path')==dest, 'sub-agent runtime destination')


def sub_agent_model_policy(role):
    policy=validate('SubAgentModelPolicy',role.get('model_policy'))
    for aid in ('codex','claude'):
        candidates=policy[aid]['candidates']
        require(len(candidates)==len(set(candidates)), 'duplicate model candidate')
        require(all(m.startswith('gpt-') if aid=='codex' else m.startswith('claude-') for m in candidates), 'model provider boundary')
    return policy


def resolved_sub_agent_models(packages, desired, observations):
    """Select only role-approved candidates; catalog presence is not access proof."""
    validate('ModelAvailability', observations)
    ordered(observations,lambda r:r['adapter'])
    require([r['adapter'] for r in observations]==desired['adapters'], 'model observation adapter closure')
    available={}
    for row in observations:
        require(row['source'] in ({'codex-app-server'} if row['adapter']=='codex' else {'anthropic-api','caller-claude-code'}), 'model observation provider boundary')
        ordered(row['models'],lambda r:r['id'])
        for model in row['models']: ordered(model['reasoning_efforts'])
        available[row['adapter']]={m['id']:m for m in row['models']}
    bindings=[]
    for aid in desired['adapters']:
        for pid in desired.get('sub_agents',[]):
            policy=sub_agent_model_policy(packages[pid])[aid]
            effort=policy.get('reasoning_effort')
            model=next((m for m in policy['candidates'] if m in available[aid]
                        and (effort is None or effort in available[aid][m]['reasoning_efforts'])),None)
            require(model is not None, 'model-unavailable: '+aid+'/'+pid)
            bindings.append({'adapter':aid,'sub_agent':pid,'model':model,'reasoning_effort':effort})
    return bindings


def sub_agent_model_binding(desired, aid, pid):
    return next((r for r in desired.get('model_resolution',{}).get('bindings',[])
                 if r['adapter']==aid and r['sub_agent']==pid),None)


def render_sub_agent_model(raw, aid, binding):
    """Change one top-level model scalar only; preserve every other byte."""
    if binding is None: return raw
    text=raw.decode('utf-8')
    pattern=r'(?m)^model = "[^"\r\n]+"(?=\r?$)' if aid=='codex' else r'(?m)^model: [^\r\n]+(?=\r?$)'
    replacement='model = "'+binding['model']+'"' if aid=='codex' else 'model: '+binding['model']
    text,count=re.subn(pattern,lambda _:replacement,text)
    require(count==1, 'sub-agent model rendering ambiguity')
    return text.encode('utf-8')


def descriptor(kind, package):
    data=package.metadata
    if kind=='sub-agent':
        return {'kind':kind,'id':package.id,'version':package.version,'metadata_version':1,
                'metadata':'sub-agent-package.yaml','members':sorted(package.members),
                'required_dependencies':[],'optional_dependencies':[]}
    required=[]; optional=[]
    for requirement,rows in (('required',required),('optional',optional)):
        for dep in data['dependencies'][requirement]:
            row={'kind':dep['kind'] if kind=='knowledge' else 'skill','id':dep['id'],'version':dep['version']}
            if requirement=='optional': row['on_missing']='unavailable'
            rows.append(row)
    if kind=='skill':
        for use in data.get('knowledge_consumption',[]):
            row={'kind':'knowledge','id':use['package'],'version':use['version']}
            if use['requirement']=='optional': row['on_missing']='unavailable'
            rows=required if use['requirement']=='required' else optional
            previous=next((r for r in rows if dependency_key(r)==dependency_key(row)),None)
            require(previous is None or previous==row,'consumption version disagreement')
            if previous is None: rows.append(row)
    required.sort(key=dependency_key); optional.sort(key=dependency_key)
    dependencies(required,optional,(kind,package.id))
    return {'kind':kind,'id':package.id,'version':package.version,
            'metadata_version':data['content_package_version'] if kind=='knowledge' else data['metadata_version'],
            'metadata':'content-package.yaml' if kind=='knowledge' else 'skill-package.yaml',
            'members':sorted(package.members),'required_dependencies':required,'optional_dependencies':optional}


def component_shape(component):
    validate('Component',component)
    require(len(component['members'])<=4096,'member budget')
    ordered(component['members']); portable(component['members'])
    expected={'skill':'skill-package.yaml','knowledge':'content-package.yaml','sub-agent':'sub-agent-package.yaml'}[component['kind']]
    entry={'skill':'SKILL.md','knowledge':'README.md','sub-agent':'sub-agent.yaml'}[component['kind']]
    require(component['kind']!='sub-agent' or component['metadata_version']==1,'unsupported sub-agent metadata')
    require(component['metadata']==expected and {entry,expected}<=set(component['members']),'metadata/entry closure')
    require(component['kind']!='knowledge' or component['metadata_version']==1,'unsupported content metadata')
    dependencies(component['required_dependencies'],component['optional_dependencies'],dependency_key(component))


def closure(components):
    require(len(components)<=128,'component budget')
    ordered(components,dependency_key)
    by_key={dependency_key(c):c for c in components}
    for c in components:
        component_shape(c)
        for requirement in ('required','optional'):
            for dep in c[requirement+'_dependencies']:
                key=dependency_key(dep)
                require(key in by_key or requirement=='optional','dependency-closure: required omission')
                if key in by_key: require(by_key[key]['version']==dep['version'],'dependency-version')
    remaining=set(by_key)
    while remaining:
        ready={k for k in remaining if not {dependency_key(r) for r in by_key[k]['required_dependencies']} & remaining}
        require(bool(ready),'dependency-cycle')
        remaining-=ready


def desired_shape(data):
    validate('Selection',data)
    for key in ('skills','knowledge','adapters','sub_agents'): ordered(data.get(key,[]))
    require(len(selected_keys(data))<=128 and len(data['bindings'])<=128,'selection budget')
    ordered(data['bindings'],lambda r:r['id'])
    if 'model_resolution' in data:
        resolution=data['model_resolution']
        ordered(resolution['bindings'],lambda r:(r['adapter'],r['sub_agent']))
        require([(r['adapter'],r['sub_agent']) for r in resolution['bindings']]
                ==[(aid,pid) for aid in data['adapters'] for pid in data['sub_agents']], 'model binding selection closure')
    authority_hashes={}
    for row in data['bindings']:
        for key in ('resources','required_rule_ids'): ordered(row[key])
        selector=row['selector']
        for key in ('capabilities','operations','execution_modes','path_prefixes','file_types'): ordered(selector[key])
        for name in selector['path_prefixes']:
            if name!='.': portable([name])
        ordered(row['authorities'],lambda r:(r['path'],r['selector']))
        for authority in row['authorities']:
            portable([authority['path']])
            previous=authority_hashes.setdefault(authority['path'],authority['sha256'])
            require(previous==authority['sha256'],'binding-unresolved: conflicting authority hashes')
        require((row['use_as']=='normative-rule' and bool(row['required_rule_ids']) and bool(row['authorities']))
                or (row['use_as']!='normative-rule' and not row['required_rule_ids']), 'binding-unresolved: normative authority/rules')
    return data


def selection_skill_naming(desired):
    """Keep historical v1 bytes intact while resolving their implicit mode."""
    validate('Selection', desired)
    return 'prefixed' if desired['selection_version'] == 1 else desired['skill_naming']


def resource_bindings(packages, desired):
    observations=[]
    for binding in desired['bindings']:
        package=packages.get(('knowledge',binding['package']))
        require(package is not None,'binding-unresolved: bound package is not selected')
        resources={r['id']:r for r in package.metadata['resources']}
        require(set(binding['resources'])<=resources.keys(),'binding-unresolved: absent resource')
        rules=set()
        for rid in binding['resources']:
            resource=resources[rid]
            rules.update(resource['rule_ids'])
            if binding['use_as']=='normative-rule':
                require(resource['kind'] in {'rule-catalog','normative-rule'},'binding-unresolved: resource is not normative')
            selector=binding['selector']
            require(set(selector['capabilities'])<=set(resource['capabilities']) and set(selector['operations'])<=set(resource['operations']), 'binding-unresolved: resource capability/operation')
            require(resource['technology_profile'] is None or selector['technology_profile']==resource['technology_profile'], 'binding-unresolved: technology profile')
        require(set(binding['required_rule_ids'])<=rules,'binding-unresolved: required rule absent')
        observations.append({'binding':binding,'status':'requires-authority-observation' if binding['authorities'] else 'available',
                             'semantic_applicability':'target-owned'})
    return observations


def markdown_prose(text):
    """Exclude fenced examples/comments; they do not allocate active references."""
    rows=[]; fence=None; width=0
    for line in text.splitlines(keepends=True):
        marker=re.match(r'^ {0,3}(`{3,}|~{3,})(.*)$',line.rstrip('\r\n'))
        if fence is not None:
            if marker and marker[1][0]==fence and len(marker[1])>=width and not marker[2].strip(): fence=None
            rows.append('\n'); continue
        if marker and (marker[1][0]=='~' or '`' not in marker[2]):
            fence=marker[1][0]; width=len(marker[1]); rows.append('\n'); continue
        rows.append(line)
    return re.sub(r'<!--[\s\S]*?-->', '', ''.join(rows))


def selected_references(packages, contents):
    unavailable=[]
    rule_owners={}
    for (kind,pid),package in packages.items():
        if kind=='sub-agent': continue
        if kind=='skill':
            for dep in package.metadata['dependencies']['optional']:
                other=packages.get(('skill',dep['id']))
                if other is not None:
                    require(set(dep['operations'])<={r['id'] for r in other.metadata['operations']},'reference-closure: optional skill operation missing')
            for row in package.metadata.get('knowledge_consumption',[]):
                target=packages.get(('knowledge',row['package']))
                available={r['id'] for r in target.metadata['resources']} if target else set()
                missing=sorted(set(row['resources'])-available)
                require(not missing or row['requirement']=='optional','reference-closure: required knowledge consumption')
                if missing: unavailable.append({'package':pid,'consumption':row['id'],'missing':missing,'status':'unavailable'})
            continue
        members={m['path']:m for m in package.metadata['members']}
        for resource in package.metadata['resources']:
            for rule in resource['rule_ids']:
                require(rule not in rule_owners or rule_owners[rule]==pid,'duplicate normative rule owner')
                rule_owners[rule]=pid
        declared=set()
        for ref in package.metadata['references']:
            target=ref['target']; other=packages.get(('knowledge',target['package']))
            resource=next((r for r in other.metadata['resources'] if r['id']==ref['resource_id']),None) if other else None
            if other is None or target['path'] not in other.members or resource is None:
                require(ref['requirement']=='optional','reference-closure: required resource missing')
                unavailable.append({'package':pid,'resource_id':ref['resource_id'],'status':'unavailable'})
                continue
            require(resource['path']==target['path'],'reference-closure: resource target mismatch')
            if target['anchor'] is not None:
                text=markdown_prose(contents[('knowledge',target['package'],target['path'])].decode('utf-8'))
                anchors=set(re.findall(r'<a\s+(?:id|name)=["\']([^"\']+)',text))
                seen={}
                for heading in re.findall(r'^ {0,3}#{1,6}\s+(.+?)\s*#*$',text,re.M):
                    anchor=re.sub(r'[^\w\- ]','',heading.lower()).replace(' ','-')
                    count=seen.get(anchor,0); seen[anchor]=count+1
                    anchors.add(anchor if not count else anchor+'-'+str(count))
                require(target['anchor'] in anchors,'reference-closure: heading anchor missing')
            declared.add((ref['from'],target['package'],target['path'],target['anchor']))
        for member in package.members:
            if not member.lower().endswith('.md'): continue
            text=markdown_prose(contents[(kind,pid,member)].decode('utf-8'))
            text=re.sub(r'(?<!`)(`+)(?!`)[\s\S]*?(?<!`)\1(?!`)', '', text)
            links=re.findall(r'!?\[[^\]\n]*\]\(\s*(<[^>]+>|[^\s)]+)(?:\s+[^)]*)?\)',text)
            links+=re.findall(r'^\s{0,3}\[[^\]\n]+\]:\s*(<[^>]+>|\S+)',text,re.M)
            for link in links:
                parsed=urlsplit(unquote(link.strip('<>')))
                if parsed.scheme in {'https','http','mailto'}: continue
                require(not parsed.scheme and not parsed.netloc and not parsed.query and not parsed.path.startswith(('/', '\\')) and '\\' not in parsed.path,'reference-closure: nonportable local link')
                resolved=posixpath.normpath(posixpath.join(pid,posixpath.dirname(member),parsed.path)) if parsed.path else pid+'/'+member
                target_id,sep,target_member=resolved.partition('/')
                require(sep and ('knowledge',target_id) in packages and target_member in packages[('knowledge',target_id)].members,'reference-closure: local link missing')
                require((member,target_id,target_member,parsed.fragment or None) in declared,'reference-closure: undeclared link')
    return unavailable
