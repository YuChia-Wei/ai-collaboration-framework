#!/usr/bin/env python3
"""Explicit P7 selections; unavailable layers never succeed as placeholders."""
from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
import sys
import unittest

HERE = Path(__file__).resolve().parent
sys.dont_write_bytecode = True
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[1] / 'src'))
import support

FAMILIES = ('lesson', 'adr', 'standards-promotion', 'pr', 'local-backlog',
            'software-development-orchestrator', 'problem-frame-author')


def arguments(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--layer', required=True, choices=('contracts', 'public', 'native-windows'))
    parser.add_argument('--family', choices=FAMILIES)
    parser.add_argument('--output-root', type=Path)
    parser.add_argument('--native-root', type=Path)
    parser.add_argument('--case', action='append', help='Exact unittest Class.method, repeatable; contracts only')
    args = parser.parse_args(argv)
    if args.layer != 'public' and args.family:
        parser.error('--family requires --layer public')
    if args.layer != 'native-windows' and args.native_root:
        parser.error('--native-root requires --layer native-windows')
    if args.layer == 'native-windows' and args.native_root is None:
        parser.error('--layer native-windows requires its separate explicit --native-root')
    if args.layer != 'contracts':
        parser.error(f'layer {args.layer!r} is reserved but not implemented; no tests executed')
    return args


def main(argv=None):
    args = arguments(argv)  # Reject unsupported selections before allocating/importing product.
    run = None
    success = False
    try:
        print(json.dumps({'runtime': support.runtime_versions()}, sort_keys=True), flush=True)
        run = support.FixtureRun(args.output_root)
        with support.use_run(run):
            spec = importlib.util.spec_from_file_location('test_contracts', HERE / 'test_contracts.py')
            module = importlib.util.module_from_spec(spec)
            sys.modules[spec.name] = module
            spec.loader.exec_module(module)
            loader = unittest.TestLoader()
            suite = (loader.loadTestsFromNames(args.case, module) if args.case else loader.loadTestsFromModule(module))
            if loader.errors or suite.countTestCases() == 0:
                raise support.FixtureError('unknown or empty test selection: ' + '; '.join(loader.errors))
            result = unittest.TextTestRunner(verbosity=2).run(suite)
            success = result.wasSuccessful() and not result.skipped
        return 0 if success else 1
    except (support.FixtureError, OSError, ImportError) as exc:
        print(json.dumps({'outcome': 'unavailable-or-failed', 'diagnostic': str(exc)}), file=sys.stderr)
        return 2
    finally:
        if run is not None:
            try:
                print(json.dumps({'fixture_accounting': run.close(success)}, sort_keys=True), flush=True)
            except (support.FixtureError, OSError) as exc:
                print(json.dumps({'outcome': 'cleanup-failed', 'residue': str(run.root),
                                  'diagnostic': str(exc), 'next_action': 'Inspect residue; do not retry cleanup blindly.'}), file=sys.stderr)
                # Cleanup failure must never inherit the success return above.
                raise SystemExit(2)


if __name__ == '__main__':
    raise SystemExit(main())
