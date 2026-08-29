# REL-v0.15.1 — Fail-Closed Validation Reuse

v0.15.1 is a non-breaking patch for the v0.15 public framework package. It
prevents validation evidence from being reused when policy or runtime identity
cannot be proved and restores finite execution budgets for every registered
validation check.

## Highlights

- Fails closed when the complete validation-policy fingerprint cannot be
  computed instead of admitting reuse with an incomplete identity.
- Includes the Python implementation, version, cache tag, ABI, SOABI, and the
  managed PyYAML runtime in validation reuse identity.
- Advances the validation cache schema so legacy cache records cannot be
  silently accepted under the stronger runtime contract.
- Assigns positive finite timeout budgets to the three advisory checks that
  previously registered a zero timeout, without changing their advisory
  enforcement class.
- Explains why initialization may report `action_ready: false` with
  `effective-rule-state-missing` and identifies the required governance step.
- Restores the canonical, conditional fixed-head auditor route for terminal or
  high-risk post-remediation AI-context verification while preserving its
  independent read-only boundary.

## Practical Effect

Consumers receive safer validation reuse decisions. A missing or unreadable
policy input, unavailable runtime identity, Python runtime change, or managed
PyYAML change now disables reuse and requires fresh execution. Existing valid
workflows and public commands remain unchanged. Governed AI-context maintenance
can again produce a schema-valid auditor-owned fixed-head execution packet
without assigning the verification conclusion to the remediation owner.

## Compatibility

This patch keeps the `ai-collaboration-framework-v0.15.x` package identity,
the `dotnet-backend` profile, and the v0.15 package/files/migration schema
versions. The automatic package upgrade source is v0.15.0.

Validation cache entries written under the earlier schema are intentionally
invalidated and must be regenerated. This is a safety migration, not a public
CLI or package-layout break.

## Known Limitations

- Validation evidence reuse proves matching declared policy and runtime
  identity; it does not replace exact-head, hosted, or other always-fresh gates.
- `action_ready: false` remains a truthful stop state until the target's
  effective-rule state is created by the appropriate init or upgrade workflow
  and validation is rerun.

<!--
The renderer appends canonical Included Work and release provenance. Keep this
authored content phase-neutral and omit generated automation details.
-->
