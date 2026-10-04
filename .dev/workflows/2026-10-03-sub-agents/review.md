# Independent scoped review

Created: `2026-10-03T08:39:51+08:00`; updated: `2026-10-03T08:56:55+08:00`.
Owner: `software-development-orchestrator`; source-policy rule 6 applies.

The human explicitly authorized one read-only sub-agent for #434. Actual
reviewer `/root/sub_agents_review` used `bounded-general-worker`, whose tool
profile declares `gpt-5.6-terra` / `xhigh`, and the owning `code-reviewer` skill.
It was restricted to reads, no delegation, repair, provider mutation or release.
Root remained the only tracked writer. There is no canonical auditor role
binding; this is an ordinary scoped review under the adopted source policy.

Immutable base: `37a588c8c0b6f5e760079c563e71d742af8f962d`.
Implementation head: `89815900f7d0aa05a53eb9902f8883fdc87649de`.
Tracked state was clean at dispatch and remained unchanged during review.

Reviewed scope: distribution contracts/schema, catalog/subset/projection,
installation ownership, six role packages and preset, moved active source
profiles/references, source ownership selector, focused tests and user guide.
Criteria are the accepted bounded outcome in `workflow-plan.md`; governing
authority is the adopted `SOURCE-DEVELOPMENT-POLICY.md` and applicable root guide.
The reviewer read supplied exact-head check and physical assembly evidence;
those parent-executed checks are not represented as reviewer-executed tests.

Result: **no supported actionable defects within the bounded immutable diff**.
The reviewer found v3 selection, six package closures, source-free subset,
unsupported adapter refusal, v1/v2 compatibility, managed ownership/collision/
drift and moved active references consistent with the acceptance scope.
Reviewer reported no changed files. Parent disposition: accept; no repair.

Limits: this common review is not a specialized security audit. Static and
physical configuration evidence does not prove model availability, runtime
discovery/invocation, role behavior, downstream adoption or publication. The
focused installation result was separately supplied as parent evidence.

Initial pre-Claude workflow bookkeeping was outside the product patch. The same authorized
reviewer receives the final immutable record commit for a fresh current-head
binding and review of that administrative delta. No full-tree equivalence is
claimed across a commit that changes these records. The deterministic binding
verifies all 50 reviewed non-workflow changed files and seven deletions, while
the reviewer checks the record delta and unchanged criteria/authority. Any
content discrepancy or actionable finding blocks handoff.

First administrative follow-up on
`cf407f6b22293559fdcf99e816107b1b46370339` blocked binding: the reviewer
identified the failed source gate's two completed-task record defects, requiring
the actual `result_summary` and accepted finding disposition. Parent accepts
that finding and repairs only workflow metadata; this does not invalidate the
unchanged implementation review. A subsequent fresh immutable binding must
confirm the correction and gate outcome before handoff.

The owner subsequently extended acceptance to all six Claude projections.
Affected review on `fcaf7aa76d0a958b894f0176d7116193f9f3b636` failed with one
actionable model-enforcement finding: `check_sub_agent` accepted arbitrary
values instead of requiring analyzer `inherit` and translator `haiku`. Parent
accepts the finding and implements exact checks and refusal regression cases.
The same reviewer remains read-only; prior no-defect review does not cover the
new Claude acceptance. Corrected immutable scope needs affected re-review.

## Corrected Claude review

Updated: `2026-10-03T08:56:55+08:00`. Reviewer `/root/sub_agents_review` completed affected
read-only review on `51a939c5b1de1ca32b7c46a130f29532a4424ff6` using the same authorized profile/skill.
The exact inherit/haiku checks and wrong/missing/cross-role regression cases
addressed the model-enforcement finding; no remaining supported actionable
defects were reported in the bounded cumulative scope. Files changed: none.
Parent disposition: accept. Actual reviewer result is retained locally at
`artifacts/claude-sub-agents-review-final.json`. Independent review of the
record-only final delta and fresh current-head binding remain required for
handoff. Configuration/install evidence remains separate from model availability,
actual invocation, downstream adoption and publication.

The configured-path targeted model-refusal test was independently executed:
one test passed in 0.266 seconds. A direct standalone test-file invocation hit
an existing import-path mismatch; that is retained as a command-preparation
limitation, not a passing execution or a supported product regression. Parent
executed the full configured Source suites; the reviewer inspected their
evidence rather than claiming its own full-suite run. The current cumulative
product binding covers 56 changed non-workflow files and seven deletions.

## Model resolution review and accepted repair

The existing authorized `/root/sub_agents_review` read-only reviewer, executing
the bounded-general-worker profile under code-reviewer, reviewed
`afa04b19a1905c4a614a8242b98e5146b862ad69..b220256921736b17c86217ccfee8b2d4434b5bfe`.
Its failed review found one P2 eager id lookup / malformed discovery scalar
issue; no additional actionable defect was reported. Parent retained and repaired
that finding. This review does not recharacterize prior fixture passes as parser
coverage or discard the failed mocked reproductions.

Affected re-review accepted `d980df4cec53a884267cc6b323bf427d74a12b02`:
model-only/id-only pagination and invalid identifier/effort cases pass two
independently executed targeted tests (0.115 seconds). Reviewer preflight checked
36 file/authority rows, committed hashes and Git-normalized working blob identity;
raw CRLF bytes are separately recorded, never declared identical to LF Git bytes.
The reviewer inspected the 171-test fresh source gate and 42-file isolated
installation evidence. Parent accepts; no remaining actionable defect reported.
See model-validation.md for immutable identities, preserved attempts and limits.
The complete earlier scope plus accepted model extension is bound to that fixed
product. The final metadata-only commit needs administrative hash rebind and
fresh local source gate before handoff; hosted/native admission stays separate.
