"""Distribution version grammar and rejection before any source/output access."""
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from distribution import assembly
from distribution.data import DistributionError, distribution_version, version


class DistributionVersionTests(unittest.TestCase):
    def test_strict_distribution_grammar_and_unchanged_component_grammar(self):
        for value in ('0.0.0', '0.19.0', '12.34.56', '0.19.0-rc.1', '12.34.56-rc.12'):
            self.assertEqual(distribution_version(value, 'fixture'), value)
        for value in (None, True, False, 1, 1.0, [], {}, '', ' ', '0.19', 'v0.19.0',
                      '00.19.0', '0.019.0', '0.19.00', '0.19.0-rc.0', '0.19.0-rc.01',
                      '0.19.0-rc.-1', '0.19.0-rc.1.0', '0.19.0-RC.1', '0.19.0-beta.1',
                      '0.19.0+build', '0.19.0-rc.1+build', ' 0.19.0', '0.19.0\n', '１.19.0'):
            with self.subTest(value=value), self.assertRaises(DistributionError):
                distribution_version(value, 'fixture')
        with self.assertRaises(DistributionError):
            version('0.19.0-rc.1', 'component')
        self.assertEqual(version('0.2.0', 'component'), '0.2.0')

    def test_versioned_api_requires_version_before_source_or_output(self):
        with patch.object(assembly, 'GitSource', side_effect=AssertionError('premature source')):
            for value in (None, '', True, 0.19, '0.19.0-rc.0'):
                with self.subTest(value=value), self.assertRaises(DistributionError):
                    assembly.assemble_versioned(Path('unused'), 'unused', 'tiny', Path('unused'), Path('unused'), release_version=value)
            with self.assertRaises(TypeError):
                assembly.assemble_versioned(Path('unused'), 'unused', 'tiny', Path('unused'), Path('unused'))

if __name__ == "__main__":
    unittest.main()
