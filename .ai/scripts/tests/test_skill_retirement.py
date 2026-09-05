"""Retirement routing and real planner/apply behavior on isolated release fixtures."""

from __future__ import annotations

import copy
import hashlib
from pathlib import Path
import subprocess
import sys
import unittest

import yaml

import test_skill_transition_contract as transition_tests
from test_ai_context_package_apply import PackageApplyFixture, APPLY, apply_fixture_plan
from ai_context_package import migration_operations

ROOT = Path(__file__).resolve().parents[3]
VALIDATOR = transition_tests.VALIDATOR
ALIASES = tuple(VALIDATOR.EXPECTED_TRANSITIONS)
PATHS = tuple(
    f"{prefix}/{alias}/{filename}"
    for alias in ALIASES
    for prefix, filename in ((".ai/assets/skills", "skill.yaml"),
                             (".agents/skills", "SKILL.md"),
                             (".claude/skills", "SKILL.md"))
)


class RetirementContractTests(transition_tests.SkillTransitionContractTests):
    def test_runtime_rejects_but_history_preserves_each_retired_identifier(self):
        for identifier, (replacement, _) in VALIDATOR.EXPECTED_TRANSITIONS.items():
            result = VALIDATOR.resolve_identifier(self.root, identifier)
            self.assertFalse(result['accepted'])
            self.assertEqual('retired', result['status'])
            self.assertIn(replacement, result['message'])
            historical = VALIDATOR.resolve_identifier(self.root, identifier, 'historical')
            self.assertTrue(historical['accepted'])
            self.assertEqual(identifier, historical['identifier'])
            self.assertEqual('historical-evidence', historical['status'])

    def test_active_unknown_and_unsafe_identifiers(self):
        self.assertTrue(VALIDATOR.resolve_identifier(self.root, 'ai-context-init')['accepted'])
        self.assertFalse(VALIDATOR.resolve_identifier(self.root, 'unknown-skill')['accepted'])
        with self.assertRaises(ValueError):
            VALIDATOR.resolve_identifier(self.root, '../ai-context-init')

    def test_missing_tombstone_fails_closed(self):
        (self.root / VALIDATOR.RETIREMENT).unlink()
        self.assertTrue(VALIDATOR.validate(self.root))

    def test_reintroduced_entries_fail_for_every_surface(self):
        for relative in PATHS:
            path = self.root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text('stale entry', encoding='utf-8')
            self.assertTrue(any('retired skill entry must be absent' in e
                                for e in VALIDATOR.validate(self.root)))
            path.unlink()

    def test_release_lifecycle_replacement_and_rewrite_drift_fail(self):
        path = self.root / VALIDATOR.RETIREMENT
        original = yaml.safe_load(path.read_text())
        for field, value in [('removal_target', None), ('lifecycle', 'deprecated'),
                             ('replacement', 'ai-context-upgrader')]:
            with self.subTest(field=field):
                modified = copy.deepcopy(original)
                modified['transitions'][0][field] = value
                path.write_text(yaml.safe_dump(modified), encoding='utf-8')
                self.assertTrue(VALIDATOR.validate(self.root))
        original['historical_identifier_rewrite'] = True
        path.write_text(yaml.safe_dump(original), encoding='utf-8')
        self.assertTrue(VALIDATOR.validate(self.root))

    def test_cli_returns_nonzero_for_new_alias_request(self):
        for context, code in [('runtime', 1), ('historical', 0)]:
            result = subprocess.run(
                [sys.executable, str(ROOT / '.ai/scripts/skill_identifier_lifecycle.py'),
                 'dev-workflow', '--root', str(self.root), '--context', context],
                capture_output=True, text=True, check=False,
            )
            self.assertEqual(code, result.returncode, result.stderr)
            self.assertIn('dev-workflow', result.stdout)


class RetirementUpgradeTests(unittest.TestCase):
    def test_published_alias_bytes_use_guarded_removal_or_owner_reconciliation(self):
        # These are bounded fixtures of the published bytes and actual migration
        # engine, not proof of a published direct edge or a downstream deployment.
        for version in ('0.6.0', '0.9.0'):
            baseline = yaml.safe_load((ROOT / '.ai/scripts/tests/fixtures/skill-retirement.yaml').read_text(encoding='utf-8'))['versions'][version]
            published = {
                path: baseline['files'][path]['content'].encode('utf-8')
                for path in PATHS
            }
            for path, content in published.items():
                self.assertEqual(baseline['files'][path]['sha256'], hashlib.sha256(content).hexdigest())
            for scenario in ('unchanged', 'modified', 'target-owned'):
                with self.subTest(version=version, scenario=scenario):
                    fixture = PackageApplyFixture()
                    try:
                        ownership = 'target-owned' if scenario == 'target-owned' else 'framework-managed'
                        previous = {p: (b, ownership, '0644') for p, b in published.items()}
                        current = {p: b + (b'\n# target customization\n' if scenario == 'modified' else b'')
                                   for p, b in published.items()}
                        for path, content in current.items():
                            fixture.add_target(path, content)
                        history_path = '.dev/workflows/legacy/task.json'
                        history = b'{"owner_skill":"dev-workflow","initialized_by":"repo-structure-sync"}\n'
                        fixture.add_target(history_path, history)
                        fixture.commit_target()
                        records = {p: fixture.record(p, *record) for p, record in previous.items()}
                        operations = migration_operations(records, [])
                        expected = 'remove' if scenario == 'unchanged' else 'reconcile'
                        self.assertEqual({'reconcile'} if scenario == 'target-owned' else {'remove'},
                                         {op['kind'] for op in operations})
                        fixture.make_package({}, operations, previous)
                        migration_path = fixture.package / 'metadata/migration.yaml'
                        migration = yaml.safe_load(migration_path.read_text())
                        migration['from']['version'] = version
                        migration_path.write_text(yaml.safe_dump(migration), encoding='utf-8')
                        fixture.reseal()
                        plan = fixture.plan(version)
                        self.assertEqual({expected}, {op['action'] for op in plan['operations']})
                        if scenario != 'unchanged':
                            with self.assertRaises(APPLY.ApplyError):
                                APPLY.apply_plan(plan)
                            self.assertEqual(current, {p: (fixture.target / p).read_bytes() for p in PATHS})
                        else:
                            apply_fixture_plan(plan)
                            self.assertTrue(all(not (fixture.target / p).exists() for p in PATHS))
                        self.assertEqual(history, (fixture.target / history_path).read_bytes())
                    finally:
                        fixture.close()


if __name__ == "__main__":
    unittest.main()
