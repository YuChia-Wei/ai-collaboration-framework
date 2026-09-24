#!/usr/bin/env python3
"""Derive an explicitly selected subset from a pinned catalog without Git access."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import sys



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
    parser.add_argument('--engine-pin',type=Path,required=True,help='Explicit independently selected Engine pin JSON; not an artifact self-description')
    parser.add_argument('--output-root',type=Path,required=True)
    parser.add_argument('--scratch-root',type=Path,required=True)
    args=parser.parse_args()
    if not sys.flags.isolated or not sys.flags.dont_write_bytecode: parser.error('Use python -I -B.')
    if bool(args.preset)!=bool(args.preset_version): parser.error('--preset requires an exact --preset-version.')
    try:
        with verified_host(Path(__file__).absolute().parents[1],args.engine_pin):
            from distribution import installation_state as state
            from distribution.catalog import read_catalog,derive_subset,expand_preset
            catalog=read_catalog(args.catalog_root,args.catalog_identity)
            if args.selection:
                parent=state._root(str(args.selection.parent)); name=state._relative(args.selection.name)
                reader=state._Reader(); target=reader.locate(parent,name)
                desired=state._document(reader.read(target,name,state.LIMITS['document_bytes']),name,canonical=False)
            else: desired=expand_preset(catalog,args.preset,args.preset_version)
            result=derive_subset(catalog,desired,args.output_root,args.scratch_root)
            result['desired']=desired
    except (ValueError,OSError,UnicodeError,TypeError,KeyError,ImportError,RecursionError,OverflowError):
        print(json.dumps({'outcome':'blocked','code':'subset-input','reason':'Pinned catalog, explicit selection or bounded output was rejected; preserve any partial output.'}))
        return 1
    print(json.dumps(result,indent=2,ensure_ascii=False))
    return 0


if __name__=='__main__': raise SystemExit(main())
