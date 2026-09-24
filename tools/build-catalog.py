#!/usr/bin/env python3
"""Explicit RC2 catalog assembly, independent of legacy --profile invocations."""
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
    parser=argparse.ArgumentParser(description='Build an immutable RC2 catalog from an exact local commit; no installation.')
    parser.add_argument('--repository',type=Path,required=True)
    parser.add_argument('--commit',required=True)
    parser.add_argument('--release-version',required=True)
    parser.add_argument('--engine-pin',type=Path,required=True,help='Explicit independently selected Engine pin JSON; not an artifact self-description')
    parser.add_argument('--output-root',type=Path,required=True)
    parser.add_argument('--scratch-root',type=Path,required=True)
    parser.add_argument('--engine-output-root',type=Path)
    args=parser.parse_args()
    if not sys.flags.isolated or not sys.flags.dont_write_bytecode: parser.error('Use python -I -B.')
    root=Path(__file__).absolute().parents[1]
    if args.repository!=root: parser.error('Select the executing repository explicitly.')
    try:
        with verified_host(root,args.engine_pin):
            from distribution.catalog import build_catalog,package_engine
            result=build_catalog(args.repository,args.commit,args.release_version,args.output_root,args.scratch_root)
            if args.engine_output_root is not None: result['engine_bundle']=package_engine(args.repository,args.commit,args.engine_output_root)
    except (ValueError,OSError,UnicodeError,TypeError,KeyError,ImportError,RecursionError,OverflowError) as exc:
        print(json.dumps({'outcome':getattr(exc,'outcome','blocked'),'code':getattr(exc,'code',getattr(exc,'diagnostic',{}).get('code','catalog-input')),'reason':'Exact committed inputs, roots or bounded catalog closure were rejected; preserve any partial output.'}))
        return 1
    print(json.dumps(result,indent=2,ensure_ascii=False))
    return 0


if __name__=='__main__': raise SystemExit(main())
