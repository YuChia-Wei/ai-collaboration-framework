# B4 actual actor output — BDD-only installation

Task: capability test-design; operation design; execution mode direct; technology_profile null; path examples/renewal.md.
Prompt: On this installation, design a Given-When-Then refusal scenario. Agreed R1/AC1: another member reservation prevents renewal and preserves the due date. Loan L7, due 20 October, reserved by Ben, borrower Ada.

## Actual output

Scenario ID: B4-R1-AC1. Name: Renewal refused because another member has reserved the item.
Source: caller prompt, agreed R1/AC1; no source document revision supplied.

Given loan L7 belongs to borrower Ada and has a due date of 20 October
And Ben, a member other than Ada, has reserved the item on loan L7
When Ada requests renewal of loan L7
Then the renewal is refused
And the due date of loan L7 remains 20 October

Assertions: the renewal outcome observable to the caller indicates refusal; the loan due date observable after the request equals 20 October. Both expected outcomes come from agreed R1/AC1, not an algorithm or current implementation.

Proposed test level: application use case, because the scenario observes the renewal result and the resulting loan state. Control the existing-loan and reservation inputs; use the real renewal subject rather than mocking it. The fixture supplies exactly L7/Ada/Ben and 20 October, and starts independently. No date arithmetic or real clock is needed for this rule; no year is invented. The target must select its actual renewal outcome and loan-query interfaces before implementation; this design does not invent an error code or API endpoint.

AC mapping: R1/AC1 -> B4-R1-AC1 -> refusal outcome and unchanged due date.
Open detail: target-owned representation of refusal and interface for observing due date. These do not change the agreed rule. Other renewal eligibility rules and positive/boundary cases are outside this one refusal sample.
Execution status: scenario design only; no test implementation or test execution.

## Coverage and consumed evidence

Unaffected common scenario design: available, grounded in the caller prompt and installed design instructions.
Selected specialist knowledge: unavailable. The supplied verified reader result contains resources=[], bindings=[], authorities=[]. No knowledge bytes were loaded; no adopted normative rule coverage is claimed.

Transient coverage:
- status: unavailable (optional knowledge coverage); common design continues.
- loaded_resources: []
- applicable_rule_ids: []
- conditional_rule_ids: []
- authorities: []
- coverage: {capability: test-design, operation: design, technology_profile: null, status: unavailable}
- missing: engineering-common@0.2.0 resources engineering-rule-catalog, member:references/BDD-METHOD.md, member:references/GHERKIN-SCENARIOS.md, member:references/GWT-TEST-HANDOFF-CONTRACT.md; dotnet-backend@0.1.1 resources engineering-rule-catalog, member:standards/coding-standards/test-standards.md. The .NET coverage is not selected by a null technology profile.
- diagnostics: optional-knowledge-absent; relative_path_or_null: null; reason: BDD-only installed selection exposes no knowledge resources; next_action: retain this unavailable coverage disclosure, and select knowledge separately only if the owner requests its specialist coverage.

Consumed installed paths, relative to C:\b452-74060e5c\absent\p:
- .agents/skills/bdd-gwt-test-designer/SKILL.md — ebca01010328ff9433eb772048181fd88425da32468229e2c6ae24681b3846cc
- .ai/core/skills/bdd-gwt-test-designer/SKILL.md — dae30d2ca24774605aec8fa13d25d1218710f6d5a1d7f52f1e894c4585220630
- .ai/core/skills/bdd-gwt-test-designer/skill-package.yaml — 7cfaad3fa1d5467fcb3b1621c580b2f517f0bd7f9a467590421b51ea9b22d670
- .ai/core/skills/bdd-gwt-test-designer/references/design.md — bd671a3d1b15977a5ade72f401797fae4b2476ae52d4e7b1235c03ff6415d0cb

Lock SHA256 before/after reads: e233116437e3304f9460f7945a6b91774667b8893aacf77c757a90254a4c357a. Each consumed path matched one inventory.files destination and SHA256 before its bounded read and matched again afterward. Initial adapter entry was first displayed before member comparison, then verified and reread in the bounded before/after sequence. An initial member comparison attempt incorrectly treated inventory as rows; it stopped without reading further members. Corrected the observed lock shape to inventory.files/destination and completed the comparisons. This was evidence bookkeeping, not an installed-member drift.

External supplied reader evidence: C:\b452-74060e5c\absent-resources.json; lock identity matches the observed lock. No new reader implementation or parser was created. No source fallback, other consumer access, repository edit, installation, runner selection, test implementation or acceptance judgment was performed.