"""Source configuration consistency; does not establish owner adoption or CI state."""
from pathlib import Path
import unittest
import yaml

ROOT = Path(__file__).resolve().parents[2]


class SourcePolicyTests(unittest.TestCase):
    def test_source_v2_uses_one_context_and_conditional_review_without_legacy_receipt(self):
        path = ROOT / ".dev/standards/GITHUB-WORK-MANAGEMENT-POLICY.yaml"
        policy = yaml.safe_load(path.read_text(encoding="utf-8"))
        self.assertEqual(policy["schema_version"], "2.0")
        self.assertIn(policy["status"], {"pending-adoption", "active"})
        gate = policy["work_item_binding"]["merge_gate"]
        self.assertEqual(gate["required_check_contexts"], ["Source change gate"])
        self.assertEqual(gate["required_check_paths"], ["src/**", "tools/**"])
        self.assertEqual(gate["outside_check_paths"], "not-applicable")
        review = gate["review_gate"]
        self.assertEqual(review["mode"], "maintainer-acceptance-with-conditional-independent-review")
        self.assertEqual(set(review["independent_for"]),
                         {"authority", "security", "credentials", "publication", "installation", "recovery"})
        self.assertNotIn("receipt_contract", review)
        self.assertEqual(review["downstream_policy"], "target-owned")
        self.assertFalse(policy["authority"]["provider_state_alone_authorizes"])
        self.assertFalse(policy["current_provider_state"]["credentials_for_ordinary_validation"])

    def test_named_source_authorities_exist_without_removed_resolver_roots(self):
        policy = yaml.safe_load((ROOT / ".dev/standards/AI-CONTEXT-SOURCE-EFFECTIVE-RULES.yaml").read_text(encoding="utf-8"))
        self.assertEqual(policy["schema_version"], "2.0")
        self.assertEqual(policy["selection"]["method"], "read-explicit-owning-policies")
        paths = [policy["policy_owner"], policy["adoption_record"], *policy["selection"]["paths"],
                 *policy["selection"]["conditional_paths"].values()]
        for relative in paths:
            with self.subTest(path=relative):
                self.assertTrue((ROOT / relative).is_file())
                self.assertFalse(relative.startswith((".ai/scripts/", ".ai/assets/")))
        self.assertFalse(policy["legacy"]["ordinary_source_invocation"])
        self.assertEqual(policy["boundaries"]["downstream_adoption"], "target-owned")


if __name__ == "__main__":
    unittest.main()
