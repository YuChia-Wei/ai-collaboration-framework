"""Narrow project-intent and paired-record fixtures for S6; never a native trial.

Owner-selected invocation:
python -I -B tests/framework_next/test_rc2_maintenance.py --output-root EXPLICIT_ROOT
"""
from hashlib import sha256
from pathlib import Path
import argparse
import json
import os
import sys
import unittest

HERE=Path(__file__).absolute().parent
sys.dont_write_bytecode=True
sys.path[:0]=[str(HERE),str(HERE.parents[1]/'src')]
import support
from distribution import installation_plan as planning,installation_state as state,installation
from distribution.installation_io import sibling
from distribution.data import json_bytes


class Rc2MaintenanceTests(unittest.TestCase):
    def roots(self,name):
        base=support.active_run().case(name)
        result={}
        for role in ('project','staging'):
            target=base/role; target.mkdir(); result[role]=target
        (result['staging']/'objects').mkdir()
        return result

    def intent(self,roots,name,before,after):
        if before is not None:
            target=roots['project']/name; target.parent.mkdir(parents=True,exist_ok=True)
            support.active_run().write(target,before)
            if os.name=='posix': target.chmod(0o644)
        digest=sha256(after).hexdigest() if after is not None else None
        if after is not None: support.active_run().write(roots['staging']/'objects'/digest,after)
        return {'path':name,'before_sha256':sha256(before).hexdigest() if before is not None else None,
                'after_sha256':digest,'after_content_ref':'objects/'+digest if digest else None}

    def test_exact_root_preimage_and_after_object_are_retained_without_write(self):
        roots=self.roots('root-edit')
        intent=self.intent(roots,'AGENTS.md',b'old root\r\n',b'new root\n')
        rows,objects=planning.project_edits(state._Reader(),roots,[intent],set(),[])
        self.assertEqual(objects[rows[0]['before']['sha256']],b'old root\r\n')
        self.assertEqual(objects[rows[0]['after']['sha256']],b'new root\n')
        self.assertEqual((roots['project']/'AGENTS.md').read_bytes(),b'old root\r\n')
        self.assertTrue(sibling('1'*32,'AGENTS.md').startswith('.fi-'))
        self.assertNotIn('/',sibling('1'*32,'AGENTS.md'))

    def test_unowned_present_file_and_managed_protected_overlap_block(self):
        roots=self.roots('intent-overlap')
        intent=self.intent(roots,'AGENTS.md',b'owned by project',b'after')
        for managed,protected in (({'AGENTS.md'},[]),(set(),['AGENTS.md'])):
            with self.assertRaises(ValueError): planning.project_edits(state._Reader(),roots,[intent],managed,protected)
        intent['before_sha256']=None
        with self.assertRaises(ValueError): planning.project_edits(state._Reader(),roots,[intent],set(),[])

    def test_content_address_and_delete_shape_fail_closed(self):
        roots=self.roots('object-drift')
        intent=self.intent(roots,'ROOT.md',None,b'candidate')
        (roots['staging']/intent['after_content_ref']).write_bytes(b'changed')
        with self.assertRaises(ValueError): planning.project_edits(state._Reader(),roots,[intent],set(),[])
        intent['after_sha256']=None
        with self.assertRaises(ValueError): planning.project_edits(state._Reader(),roots,[intent],set(),[])

    def test_recovery_records_reject_unknown_fields_and_wrong_side(self):
        roots=self.roots('record-shape')
        intent=self.intent(roots,'ROOT.md',b'old',None)
        rows,objects=planning.project_edits(state._Reader(),roots,[intent],set(),[])
        # _edit_record consumes already verified object bytes from the same object owner.
        installation._edit_record(rows,state._Reader(),roots['staging'],dict(objects),set(),[])
        rows[0]['after']={'sha256':'1'*64,'size':1,'mode':'100644'}
        with self.assertRaises(ValueError): installation._edit_record(rows,state._Reader(),roots['staging'],dict(objects),set(),[])

    def test_api1_cannot_acquire_new_writer_semantics(self):
        request={'api_version':1,'operation':'inspect','project_root':'unused','engine_root':'unused','engine':{}}
        result=installation.execute(request)
        self.assertEqual(result['outcome'],'unsupported')
        self.assertEqual(result['diagnostics'][0]['code'],'unsupported-write')
        self.assertFalse(result['changed'])


def main():
    parser=argparse.ArgumentParser(description=__doc__); parser.add_argument('--output-root',type=Path,required=True)
    args=parser.parse_args()
    support.check(sys.flags.isolated and sys.flags.dont_write_bytecode,'Use -I -B.')
    run=support.FixtureRun(args.output_root); success=False
    try:
        with support.use_run(run):
            result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Rc2MaintenanceTests))
            success=result.wasSuccessful() and not result.skipped
            return 0 if success else 1
    finally: print(json.dumps({'fixture_accounting':run.close(success)},sort_keys=True))


if __name__=='__main__': raise SystemExit(main())
