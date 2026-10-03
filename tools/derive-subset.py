#!/usr/bin/env python3
"""Derive an explicitly selected subset from a pinned catalog without Git access."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import sys


def discover_codex_models():
    """Read the current CLI catalog without starting a thread or a model turn."""
    import queue
    import shutil
    import subprocess
    import threading
    import time
    from datetime import datetime, timezone
    executable=shutil.which('codex')
    if not executable: raise ValueError('Codex CLI unavailable')
    process=subprocess.Popen([executable,'app-server'],stdin=subprocess.PIPE,stdout=subprocess.PIPE,
                             stderr=subprocess.DEVNULL)
    messages=queue.Queue(maxsize=128)
    deadline=time.monotonic()+45
    def receive():
        try:
            while True:
                raw=process.stdout.readline(1024*1024+1)
                if not raw: break
                messages.put(raw,timeout=1)
        except (OSError,ValueError,queue.Full): pass
        finally:
            try: messages.put(None,timeout=1)
            except queue.Full: pass
    reader=threading.Thread(target=receive,daemon=True); reader.start()
    def send(value):
        process.stdin.write(json.dumps(value).encode()+b'\n'); process.stdin.flush()
    def request(ident,method,params):
        send({'id':ident,'method':method,'params':params})
        for _ in range(128):
            remaining=deadline-time.monotonic()
            if remaining<=0: raise ValueError('Model discovery deadline')
            try: raw=messages.get(timeout=remaining)
            except queue.Empty: raise ValueError('Model discovery timeout') from None
            if raw is None: raise ValueError('Model discovery process ended')
            if len(raw)>1024*1024: raise ValueError('Model discovery budget')
            value=json.loads(raw)
            if value.get('id')!=ident: continue
            if 'error' in value: raise ValueError('Model discovery refused')
            return value['result']
        raise ValueError('Model discovery protocol budget')
    try:
        request(0,'initialize',{'clientInfo':{'name':'aicf_model_selection','version':'0.1.0'}})
        send({'method':'initialized','params':{}})
        models=[]; cursor=None; seen=set()
        for page in range(16):
            params={'limit':100,'includeHidden':False}
            if cursor is not None: params['cursor']=cursor
            result=request(page+1,'model/list',params)
            for row in result['data']:
                if type(row) is not dict: raise ValueError('Model discovery row shape')
                if row.get('hidden',False): continue
                model=row['model'] if 'model' in row else row.get('id')
                if type(model) is not str or not model.strip(): raise ValueError('Model discovery identifier')
                if not model.startswith('gpt-'): continue
                efforts=row.get('supportedReasoningEfforts')
                if type(efforts) is not list or not all(type(r) is dict and type(r.get('reasoningEffort')) is str
                        and bool(r['reasoningEffort'].strip()) for r in efforts): raise ValueError('Model discovery effort shape')
                models.append({'id':model,'reasoning_efforts':sorted(r['reasoningEffort'] for r in efforts)})
            if len(models)>128: raise ValueError('Model discovery model budget')
            cursor=result['nextCursor']
            if cursor is None: break
            if cursor in seen: raise ValueError('Model discovery cursor cycle')
            seen.add(cursor)
        else: raise ValueError('Model discovery page budget')
        return {'adapter':'codex','source':'codex-app-server','observed_at':datetime.now(timezone.utc).isoformat(),
                'models':sorted(models,key=lambda r:r['id'])}
    finally:
        if process.poll() is None: process.terminate()
        try: process.wait(timeout=5)
        except subprocess.TimeoutExpired: process.kill(); process.wait(timeout=5)
        process.stdin.close(); process.stdout.close(); reader.join(timeout=1)


def discover_claude_api_models():
    """Explicit direct-Anthropic API discovery; never reuse Claude subscription auth."""
    import os
    import time
    from datetime import datetime, timezone
    from urllib.request import Request, build_opener, HTTPRedirectHandler
    from urllib.parse import urlencode
    key=os.environ.get('ANTHROPIC_API_KEY')
    if not key: raise ValueError('Explicit Anthropic API key unavailable')
    if os.environ.get('ANTHROPIC_BASE_URL') or any(os.environ.get(n) for n in
            ('CLAUDE_CODE_USE_BEDROCK','CLAUDE_CODE_USE_VERTEX','CLAUDE_CODE_USE_FOUNDRY')):
        raise ValueError('Direct Anthropic API discovery cannot describe this provider')
    class NoRedirect(HTTPRedirectHandler):
        def redirect_request(self,*args,**kwargs): raise ValueError('Model discovery redirect refused')
    opener=build_opener(NoRedirect()); models=[]; cursor=None; seen=set(); deadline=time.monotonic()+45
    for _ in range(16):
        params={'limit':100}
        if cursor is not None: params['after_id']=cursor
        remaining=deadline-time.monotonic()
        if remaining<=0: raise ValueError('Model discovery deadline')
        request=Request('https://api.anthropic.com/v1/models?'+urlencode(params),
                        headers={'x-api-key':key,'anthropic-version':'2023-06-01'})
        with opener.open(request,timeout=min(15,remaining)) as response:
            raw=response.read(1024*1024+1)
        if len(raw)>1024*1024: raise ValueError('Model discovery budget')
        result=json.loads(raw)
        for row in result['data']:
            if row['id'].startswith('claude-'): models.append({'id':row['id'],'reasoning_efforts':[]})
        if len(models)>128: raise ValueError('Model discovery model budget')
        if result['has_more'] is False: break
        if result['has_more'] is not True: raise ValueError('Model discovery pagination shape')
        cursor=result['last_id']
        if not cursor or cursor in seen: raise ValueError('Model discovery cursor cycle')
        seen.add(cursor)
    else: raise ValueError('Model discovery page budget')
    return {'adapter':'claude','source':'anthropic-api','observed_at':datetime.now(timezone.utc).isoformat(),
            'models':sorted(models,key=lambda r:r['id'])}



def verified_host(engine_root, pin_file):
    """Authenticate the bootstrap as data before executing any distribution code."""
    import hashlib
    import os
    import stat
    import types
    def read_direct(target, limit):
        if not target.is_absolute() or ".." in target.parts: raise ValueError("absolute direct input required")
        for item in (target, *target.parents):
            info=item.lstat()
            if stat.S_ISLNK(info.st_mode) or getattr(info,"st_file_attributes",0)&0x400: raise ValueError("linked host input")
        before=target.lstat()
        if not stat.S_ISREG(before.st_mode) or before.st_nlink!=1 or before.st_size>limit: raise ValueError("host input budget/type")
        with target.open('rb') as stream:
            opened=os.fstat(stream.fileno()); raw=stream.read(limit+1); after=os.fstat(stream.fileno())
        final=target.lstat()
        signature=lambda row:(row.st_dev,row.st_ino,row.st_size,row.st_mtime_ns,row.st_mode)
        if len(raw)>limit or not signature(before)==signature(opened)==signature(after)==signature(final): raise ValueError("host input drift")
        return raw
    def pairs(rows):
        result={}
        for key,value in rows:
            if key in result: raise ValueError("duplicate pin key")
            result[key]=value
        return result
    def invalid(value): raise ValueError("invalid pin scalar")
    pin=json.loads(read_direct(pin_file,4*1024*1024).decode('utf-8'),object_pairs_hook=pairs,parse_constant=invalid,parse_float=invalid)
    name='src/tools/maintain_framework.py'
    rows=[r for r in pin['files'] if r['path']==name]
    if len(rows)!=1: raise ValueError("bootstrap pin")
    launch=engine_root/name; raw=read_direct(launch,16*1024*1024)
    if hashlib.sha256(raw).hexdigest()!=rows[0]['sha256']: raise ValueError("bootstrap hash")
    module=types.ModuleType('aicf_consumer_bootstrap'); module.__file__=str(launch)
    exec(compile(raw,str(launch),'exec',dont_inherit=True),module.__dict__)
    return module.verified_engine(str(engine_root),pin)


def main():
    parser=argparse.ArgumentParser(description='Derive an RC2 subset; no config saving or installation.')
    parser.add_argument('--catalog-root',type=Path,required=True)
    parser.add_argument('--catalog-identity',required=True)
    source=parser.add_mutually_exclusive_group(required=True)
    source.add_argument('--selection',type=Path)
    source.add_argument('--preset')
    parser.add_argument('--preset-version')
    parser.add_argument('--skill-naming',choices=('original','prefixed'),
                        help='With --preset: original (default) or aicf-prefixed runtime skill names')
    parser.add_argument('--engine-pin',type=Path,required=True,help='Explicit independently selected Engine pin JSON; not an artifact self-description')
    parser.add_argument('--output-root',type=Path,required=True)
    parser.add_argument('--scratch-root',type=Path,required=True)
    parser.add_argument('--model-availability',type=Path,help='Explicit normalized model/list observations; resolve selected role models')
    parser.add_argument('--discover-codex-models',action='store_true',help='Read current Codex CLI model/list; no inference')
    parser.add_argument('--discover-claude-api-models',action='store_true',help='Read direct Anthropic API models with existing ANTHROPIC_API_KEY; not Claude subscription discovery')
    args=parser.parse_args()
    if not sys.flags.isolated or not sys.flags.dont_write_bytecode: parser.error('Use python -I -B.')
    if bool(args.preset)!=bool(args.preset_version): parser.error('--preset requires an exact --preset-version.')
    if args.selection and args.skill_naming is not None: parser.error('--skill-naming requires --preset; saved selections retain their naming mode.')
    if args.model_availability and (args.discover_codex_models or args.discover_claude_api_models): parser.error('Choose saved observations or live discovery.')
    try:
        with verified_host(Path(__file__).absolute().parents[1],args.engine_pin):
            from distribution import installation_state as state
            from distribution.catalog import read_catalog,derive_subset,expand_preset,resolve_sub_agent_model_selection
            catalog=read_catalog(args.catalog_root,args.catalog_identity)
            if args.selection:
                parent=state._root(str(args.selection.parent)); name=state._relative(args.selection.name)
                reader=state._Reader(); target=reader.locate(parent,name)
                state._check(target is not None,'selection-unavailable','Explicit selection file is missing.',name)
                desired=state._document(reader.read(target,name,state.LIMITS['document_bytes']),name,canonical=False)
            else: desired=expand_preset(catalog,args.preset,args.preset_version,skill_naming=args.skill_naming or 'original')
            if args.model_availability or args.discover_codex_models or args.discover_claude_api_models:
                requested=sorted((['codex'] if args.discover_codex_models else [])+(['claude'] if args.discover_claude_api_models else []))
                if not args.model_availability and requested!=desired['adapters']: raise ValueError('Discovery adapter scope mismatch')
                if args.model_availability:
                    parent=state._root(str(args.model_availability.parent)); name=state._relative(args.model_availability.name)
                    reader=state._Reader(); target=reader.locate(parent,name)
                    if target is None: raise ValueError('Model availability missing')
                    document=state._document(reader.read(target,name,state.LIMITS['document_bytes']),name,canonical=False)
                    if set(document)!={'observations'}: raise ValueError('Model availability document closure')
                    observations=document['observations']
                else:
                    observations=[]
                    if args.discover_claude_api_models: observations.append(discover_claude_api_models())
                    if args.discover_codex_models: observations.append(discover_codex_models())
                desired=resolve_sub_agent_model_selection(catalog,desired,observations)
            result=derive_subset(catalog,desired,args.output_root,args.scratch_root)
            result['desired']=desired
    except (ValueError,OSError,UnicodeError,TypeError,KeyError,ImportError,RecursionError,OverflowError) as exc:
        reason=str(exc) if getattr(exc,'code',None)=='model-unavailable' else 'Pinned catalog, explicit selection, model observation or bounded output was rejected; preserve any partial output.'
        print(json.dumps({'outcome':getattr(exc,'outcome','blocked'),'code':getattr(exc,'code',getattr(exc,'diagnostic',{}).get('code','subset-input')),'reason':reason}))
        return 1
    print(json.dumps(result,indent=2,ensure_ascii=False))
    return 0


if __name__=='__main__': raise SystemExit(main())
