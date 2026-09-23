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
    parser.add_argument('--public-read-only', action='store_true',
                        help='Public C4/C6 only; omit dependent round-trips and always return nonzero partial status')
    args = parser.parse_args(argv)
    if args.layer != 'public' and args.family:
        parser.error('--family requires --layer public')
    if args.layer != 'native-windows' and args.native_root:
        parser.error('--native-root requires --layer native-windows')
    if args.layer == 'native-windows' and args.native_root is None:
        parser.error('--layer native-windows requires its separate explicit --native-root')
    if args.layer == 'public' and args.case:
        parser.error('--case is contracts only; select a complete public family')
    if args.layer != 'public' and args.public_read_only:
        parser.error('--public-read-only requires --layer public')
    if args.layer == 'native-windows' and (args.case or args.output_root is not None):
        parser.error('native-windows uses only its explicit --native-root; --case/--output-root are not native selections')
    return args


def main(argv=None):
    args = arguments(argv)  # Reject unsupported selections before allocating/importing product.
    if args.layer == 'native-windows':
        import test_native_windows
        return test_native_windows.main(args.native_root)
    if args.layer == 'public':
        return public_main(args)
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


def public_main(args):
    """Public-only dispatch; contracts and reserved native behavior stay separate."""
    selected = (args.family,) if args.family else FAMILIES
    modules = {'lesson': ('test_knowledge', 'LessonTests'),
               'adr': ('test_knowledge', 'AdrTests'),
               'standards-promotion': ('test_knowledge', 'PromotionTests'),
               'pr': ('test_work', 'PrTests'),
               'local-backlog': ('test_work', 'BacklogTests'),
               'software-development-orchestrator': ('test_work', 'WorkflowTests'),
               'problem-frame-author': ('test_cbf', 'CbfTests')}
    outcomes = []
    public_used = process_bound_used = 0
    try:
        print(json.dumps({'runtime': support.runtime_versions()}, sort_keys=True), flush=True)
        # Each family has its own verified bounded child, including aggregate mode.
        for family in selected:
            run = None
            entry = {'family': family, 'outcome': 'unavailable-or-failed', 'exit': 2}
            success = False
            try:
                support.check(public_used < 160 and process_bound_used + 5 <= 256,
                              'aggregate public/helper launch budget exhausted; remaining families not executed')
                run = support.FixtureRun(args.output_root)
                run.public_read_only = args.public_read_only
                run.public_launch_limit = 160 - public_used
                run.prior_process_bound = process_bound_used
                with support.use_run(run):
                    name, classname = modules[family]
                    if name not in sys.modules:
                        spec = importlib.util.spec_from_file_location(name, HERE / (name + '.py'))
                        module = importlib.util.module_from_spec(spec)
                        sys.modules[name] = module
                        spec.loader.exec_module(module)
                    case = getattr(sys.modules[name], classname)('test_selected')
                    result = unittest.TextTestRunner(verbosity=2).run(unittest.TestSuite([case]))
                    success = (result.testsRun == 1 and result.wasSuccessful() and not result.skipped
                               and case.complete)
                    entry.update(case.observation())
                    entry.update(outcome='passed' if success else 'partial' if case.blocked_before_write else 'failed',
                                 exit=0 if success else 1)
            except Exception as exc:
                entry.update(exception_type=type(exc).__name__, diagnostic=str(exc))
            finally:
                if run is not None:
                    try:
                        entry['fixture_accounting'] = run.close(success)
                    except Exception as exc:
                        entry.update(outcome='cleanup-failed', exit=2, residue=str(run.root),
                                     exception_type=type(exc).__name__, diagnostic=str(exc),
                                     next_action='Inspect residue; do not retry cleanup blindly.')
            outcomes.append(entry)
            print(json.dumps({'public_family': entry}, sort_keys=True), flush=True)
            public_used += entry.get('public_launches', 0)
            process_bound_used += (entry.get('fixture_accounting', {}).get('process_total', 0)
                                   + entry.get('nested_launch_upper_bound', 0))
            if entry['exit']:
                # Stop the aggregate at its first failure/partial setup. Callers can
                # explicitly select an independent family after inspecting evidence.
                break
    except (support.FixtureError, OSError, ImportError) as exc:
        print(json.dumps({'outcome': 'unavailable-or-failed', 'diagnostic': str(exc),
                          'unexecuted_families': list(selected[len(outcomes):])}), file=sys.stderr)
        return 2
    code = max(item['exit'] for item in outcomes) if outcomes else 2
    if len(outcomes) != len(selected):
        code = max(code, 1)
    print(json.dumps({'public_selection': list(selected), 'exit': code,
                      'unexecuted_families': list(selected[len(outcomes):]),
                      'outcome': 'passed' if code == 0 else 'not-passed'}, sort_keys=True), flush=True)
    return code


if __name__ == '__main__':
    raise SystemExit(main())
