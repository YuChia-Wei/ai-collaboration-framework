"""Checked lifecycle routing inventory, never a second artifact validator.

Bindings are inspected as source declarations; this module never imports or
executes them. A present producer is not evidence that it ran or was admitted.
"""
from __future__ import annotations
import ast
import json
from pathlib import Path

REGISTRY = '.ai/assets/shared/artifact-lifecycle-registry.json'
DISPOSITIONS = {'convert','regenerate','re-execute','preserve','unsupported','owner-recovery','owner-reconciliation'}
AUTHORING = {'executable','semantic-owner','manual-gap','external','creation-template'}


def load_registry(root: Path) -> dict:
    def pairs(items):
        result = {}
        for key,value in items:
            if key in result: raise ValueError(f'duplicate lifecycle key: {key}')
            result[key] = value
        return result
    data=json.loads((root/REGISTRY).read_text(encoding='utf-8'),object_pairs_hook=pairs)
    if type(data) is not dict or data.get('schema_version') != '1.0':
        raise ValueError('unsupported lifecycle registry version')
    return data


def _path(root: Path, ref: str) -> Path:
    relative=Path(ref)
    if not isinstance(ref,str) or not ref or '\\' in ref or ':' in ref or relative.is_absolute() or '..' in relative.parts:
        raise ValueError(f'unsafe lifecycle reference: {ref}')
    path=root/relative
    if root.resolve() not in path.resolve().parents: raise ValueError('lifecycle reference escapes root')
    return path


def validate_registry(root: Path, *, source_context: bool) -> list[str]:
    errors=[]
    try:
        data=load_registry(root)
        if set(data) != {'schema_version','purpose','coverage','records'}: raise ValueError('invalid lifecycle registry fields')
        records=data['records']; coverage=data['coverage']
        if type(records) is not list or not records: raise ValueError('lifecycle records must be nonempty')
        required={'kind','baseline_refs','models','owner','authoring','producers','validators','readable','writable','migration','admissible','limits','applicability'}
        seen=set(); refs=set(); declared_models=set(); symbol_cache={}
        for row in records:
            if type(row) is not dict or set(row)!=required: raise ValueError('invalid lifecycle record fields')
            kind=row['kind']
            if type(kind) is not str or not kind or kind in seen: raise ValueError('duplicate/invalid lifecycle kind')
            seen.add(kind)
            for name in ('baseline_refs','models','producers','validators'):
                if type(row[name]) is not list or any(type(value) is not str or not value for value in row[name]): raise ValueError(f'{kind}: invalid {name}')
            if not row['models'] or not row['baseline_refs']: raise ValueError(f'{kind}: model/baseline missing')
            refs.update(row['baseline_refs']); declared_models.update(row['models'])
            if row['authoring'] not in AUTHORING or row['applicability'] not in {'source','portable','dotnet-backend-profile'}: raise ValueError(f'{kind}: invalid route classification')
            if row['authoring']=='executable' and not row['producers']: raise ValueError(f'{kind}: executable route needs a producer')
            if any('::' not in ref or not ref.partition('::')[2] for ref in row['producers']):
                raise ValueError(f'{kind}: producer requires an explicit callable declaration')
            if row['authoring']!='executable' and row['producers']: raise ValueError(f'{kind}: nonexecutable route cannot claim producers')
            if type(row['migration']) is not dict or set(row['migration'])!={'disposition','route'} or row['migration']['disposition'] not in DISPOSITIONS:
                raise ValueError(f'{kind}: invalid migration disposition')
            for value in (row['owner'],row['readable'],row['writable'],row['admissible'],row['limits'],row['migration']['route']):
                if type(value) is not str or not value.strip(): raise ValueError(f'{kind}: missing lifecycle boundary')
            selected=(source_context or row['applicability']=='portable' or
                      (row['applicability']=='dotnet-backend-profile' and (root/'.ai/assets/tech-stacks/dotnet-backend').is_dir()))
            for ref in row['models']+[row['owner']]+row['producers']+row['validators']:
                path_ref, _, symbol=ref.partition('::')
                path=_path(root,path_ref)
                if not selected: continue
                if not path.is_file(): errors.append(f'{kind}: missing route source {path_ref}'); continue
                raw = path.read_bytes()  # Bind model/owner bytes, not only existence.
                if symbol:
                    if path.suffix!='.py': errors.append(f'{kind}: callable binding must name Python source'); continue
                    if path_ref not in symbol_cache:
                        tree=ast.parse(raw.decode('utf-8'))
                        symbol_cache[path_ref]={node.name for node in tree.body if isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef,ast.ClassDef))}
                    if symbol not in symbol_cache[path_ref]: errors.append(f'{kind}: missing callable declaration {ref}')
        expected={f'E{i:02}' for i in range(1,34)}|{f'I{i:02}' for i in range(1,20)}|{'registry'}
        if refs!=expected: errors.append(f'lifecycle baseline coverage differs: missing={sorted(expected-refs)}, extra={sorted(refs-expected)}')
        if type(coverage) is not dict or set(coverage)!={'explicit_schemas','implicit_contracts'}: raise ValueError('invalid lifecycle coverage fields')
        if type(coverage['explicit_schemas']) is not list or len(coverage['explicit_schemas'])!=len(set(coverage['explicit_schemas'])):
            raise ValueError('explicit schema coverage must be unique')
        if coverage['implicit_contracts']!=sorted(f'I{i:02}' for i in range(1,20)): errors.append('implicit contract selector coverage differs')
        if source_context:
            # Active schema-definition roots, not historical workflow/assessment instances.
            roots=['.ai/assets','.ai/distribution','.ai/evaluation','.dev/standards','.dev/backlog/provider-mappings']
            actual={p.relative_to(root).as_posix() for prefix in roots for p in (root/prefix).rglob('*schema.yaml') if p.is_file()}
            recorded=set(coverage['explicit_schemas'])
            if actual!=recorded: errors.append(f'named schema coverage differs: missing={sorted(actual-recorded)}, stale={sorted(recorded-actual)}')
            if not recorded<=declared_models: errors.append('explicit schema lacks a registered artifact kind')
    except (OSError,ValueError,TypeError,KeyError,SyntaxError) as exc:
        errors.append(f'lifecycle registry cannot be checked: {exc}')
    return errors


def routes(root: Path, kind: str | None = None) -> dict:
    data=load_registry(root)
    errors=validate_registry(root,source_context=(root/'.ai/distribution').is_dir())
    if errors: raise ValueError('\n'.join(errors))
    rows=[row for row in data['records'] if kind is None or row['kind']==kind]
    if not rows: raise ValueError(f'unknown lifecycle kind: {kind}')
    return {'schema_version':data['schema_version'],'purpose':data['purpose'],
            'records':[{**row,'sources_available':all(_path(root,ref.split('::')[0]).is_file() for ref in row['models']+[row['owner']]+row['producers']+row['validators'])} for row in rows],
            'admission':'Routing and source-declaration checks only; no artifact validation, execution or approval is asserted.'}
