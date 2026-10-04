"""Selected GitHub trigger, execution and privilege boundaries; no provider calls."""
from pathlib import Path
import unittest
import yaml

ROOT = Path(__file__).resolve().parents[2]


def workflow(name):
    # BaseLoader keeps GitHub's `on` key a string rather than a YAML 1.1 boolean.
    return yaml.load((ROOT / '.github/workflows' / name).read_text(encoding='utf-8'),
                     Loader=yaml.BaseLoader)


class SourceWorkflowTests(unittest.TestCase):
    def test_only_product_and_build_changes_trigger_automatic_checks(self):
        source = workflow('source-checks.yml')
        self.assertEqual(set(source['on']), {'pull_request'})
        self.assertEqual(source['on']['pull_request']['paths'], ['src/**', 'tools/**'])
        snapshot = workflow('package-candidate.yml')
        self.assertEqual(snapshot['on']['push']['paths'], ['src/**', 'tools/**'])
        self.assertEqual(snapshot['on']['push']['branches'], ['main'])

    def test_pr_job_runs_fixed_local_suites_without_write_credentials(self):
        source = workflow('source-checks.yml')
        self.assertEqual(source['permissions'], {})
        job = source['jobs']['source-change']
        self.assertEqual(job['permissions'], {'contents': 'read'})
        checkout = next(step for step in job['steps'] if step.get('uses', '').startswith('actions/checkout@'))
        self.assertEqual(checkout['with']['persist-credentials'], 'false')
        self.assertEqual(checkout['with']['ref'], '${{ github.event.pull_request.head.sha }}')
        commands = [step['run'] for step in job['steps'] if 'run' in step]
        self.assertIn('python -I -B tests/run.py', commands)
        self.assertFalse(any('check-source-change' in command or '--base' in command for command in commands))


if __name__ == '__main__':
    unittest.main()
