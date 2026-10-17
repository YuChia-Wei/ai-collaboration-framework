# B3 isolated installed-skill actor report

Task: Explore library-loan renewal and formulate supported examples. Selectors: capability test-design; operation design; execution mode direct; technology_profile null; selected path examples/renewal.md. Output is scenario notes, with no .feature request.

## Discovery

Source is the exact caller prompt in this sample, with R1/AC1 explicitly agreed: another member reservation prevents renewal and preserves the due date. Concrete facts: loan L7; borrower Ada; due date 20 October; reserved by Ben. Ben is another member relative to Ada. No source revision, year, timezone, implementation, or further renewal policy was supplied.

| ID | Type | Content and status |
| --- | --- | --- |
| R1/AC1 | Agreed rule | Another member reservation prevents renewal and preserves the due date. |
| B3-E1 | Supported example | Ada requests renewal of L7 reserved by Ben: renewal is refused; due date remains 20 October. |
| B3-E2 | Provisional example | A loan without another member reservation may be eligible, but absence of reservation alone does not establish approval; other rules are unknown. No success oracle is supplied. |
| B3-Q1 | Open question | Can an overdue loan be renewed, and who owns that decision? Overdue policy remains unknown. |

No illustrative statement in the installed BDD guidance is promoted into product authority. In particular, no-reservation success and overdue rejection/approval remain undecided.

## Formulation

Scenario B3-S1 — Another member reservation prevents renewal.
Source/status: caller prompt, agreed R1/AC1; local scenario ID B3-S1, based on B3-E1.

Given loan L7 is borrowed by Ada and its due date is 20 October
And the loaned item has a reservation by Ben, a member other than Ada
When Ada requests renewal of loan L7
Then renewal is refused
And the due date of loan L7 remains 20 October

Both expected results come directly from agreed R1/AC1. Refusal means an observable unsuccessful renewal result; no exact wording, HTTP status, exception, or transport contract is asserted. The due-date observation must read the resulting loan state rather than calculate an expected date from the subject algorithm.

Recommended smallest credible test level: domain behavior if the loan domain owns the reservation invariant and exposes refusal plus resulting due date; otherwise the renewal application use case that owns those outcomes. Actual ownership is unknown, so this level selection is conditional. The real subject must be the renewal decision/state transition. Control the initial loan state and reservation state; do not mock the subject. If reservation information crosses a dependency boundary, a controlled response can establish orchestration only, with actual dependency integration evidence required separately if that boundary is accepted scope.

Setup and isolation: create one isolated L7 state with Ada, Ben, and the supplied due date; restore/reset it independently for each eventual test. The prompt does not establish request date or overdue status. Keep that uncertainty visible and ask the owner for a controlled request date if executable setup needs it; do not choose an overdue oracle. If an eventual date type needs a year or timezone, obtain those values before implementation rather than silently adding product meaning.

## Coverage and limits

| Source | Formulation mapping | Limits |
| --- | --- | --- |
| R1/AC1 refusal | B3-S1 Then renewal is refused | Designed observation; no execution or exact response contract. |
| R1/AC1 due-date preservation | B3-S1 And due date remains 20 October | Designed state assertion; persistence mechanism unknown. |
| Overdue policy | B3-Q1 | Unresolved; no approved scenario oracle. |
| No-reservation renewal | B3-E2 | Provisional; no claim that renewal succeeds. |

This combined discovery/formulation request reuses R1/AC1 and preserves two related observations in one scenario. Automation is a separate authorized task and was not performed. Positive, date boundary, duplicate, timeout, recovery, and cancellation scenarios are not invented without supporting rules. No runner, test parser, package installation, source fallback, delegation, repository write, or product execution occurred.

## Installed resource selection

The raw framework.lock SHA256 matched the supplied expected value before reading it as data: 4f8224d6d037f9edb331e545bae50452365c36dac8b8b23ed6cea9bcc903e426. The first tool output unnecessarily displayed the full data lock and was truncated; selection consumed only relevant inventory/selection data and subsequent bounded installed-member reads. No lock-embedded source member was opened as source fallback.

Verified supplied reader inventory: C:/b452-74060e5c/common-resources.json. Its lock identity matches the expected lock. Saved binding bdd-guidance matches test-design/design/direct, examples prefix, md file type, and null technology profile. Authority allowlist is empty. Semantic applicability remains target-owned; no normative engineering rule is adopted.

Resources below were individually verified against lock.inventory.files by destination before decoding/displaying the same bytes.

| Read member | Raw SHA256 | Selection reason |
| --- | --- | --- |
| .agents/skills/bdd-gwt-test-designer/SKILL.md | ebca01010328ff9433eb772048181fd88425da32468229e2c6ae24681b3846cc | Explicitly requested Codex entry. |
| .ai/core/skills/bdd-gwt-test-designer/SKILL.md | dae30d2ca24774605aec8fa13d25d1218710f6d5a1d7f52f1e894c4585220630 | Entry-declared installed instructions and operation routing. |
| .ai/core/skills/bdd-gwt-test-designer/skill-package.yaml | 7cfaad3fa1d5467fcb3b1621c580b2f517f0bd7f9a467590421b51ea9b22d670 | Entry-declared metadata; design instructions and optional knowledge allowlist. |
| .ai/core/skills/bdd-gwt-test-designer/references/design.md | bd671a3d1b15977a5ade72f401797fae4b2476ae52d4e7b1235c03ff6415d0cb | Selected design operation instructions. |
| .ai/core/knowledge/engineering-common/references/BDD-METHOD.md | 65dd5669a4b06f6b00abcec5a3c273b4cc4d2920b767201da5f4cbf82ae4f4d4 | Needed rule/example/question distinctions for combined exploration and formulation; also matched supplied resource index hash. |

Knowledge result: status available; loaded_resources contains engineering-common@0.2.0 resource member:references/BDD-METHOD.md, installed member/hash as above, use_as knowledge. applicable_rule_ids [], conditional_rule_ids [], authorities []. Coverage: capability test-design, operation design, technology_profile null, status available for selected BDD method, missing []. Diagnostics: none for resource availability. Implementation-specific boundary, overdue policy, date precision and response representation remain target-input gaps, not installed-resource gaps.

GHERKIN-SCENARIOS.md was not read: scenario notes are sufficient and no Gherkin artifact/expression was requested. GWT-TEST-HANDOFF-CONTRACT.md was not read: no implementation handoff was requested. No .NET specialist package, rule catalog, review instructions, other consumer output, or repository workflow/expected judgment was read.

Post-output verification: exact lock and all five chosen installed members re-observed with matching raw SHA256; no drift detected.
