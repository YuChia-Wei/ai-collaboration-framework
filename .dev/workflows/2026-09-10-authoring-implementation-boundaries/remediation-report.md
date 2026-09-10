# Authoring And Implementation Boundary Delivery

## Report Metadata

- report_id: `remediation-report-2026-09-10-authoring-implementation-boundaries`
- workflow_id: `2026-09-10-authoring-implementation-boundaries`
- owner_skill: `ai-context-governance`; status: `final`
- template_source: `.ai/assets/skills/ai-context-governance/templates/ai-context-remediation-report-template.md`
- template_version: `2.0.0`
- created_at: `2026-09-10T20:15:21+08:00`; updated_at: `2026-09-10T20:15:21+08:00`
- Baseline: `7ad859fd3724cfd7d9a3f8165c003fb812c5c2e9`.
- Initial source and paired model execution: `6655b3510e0e536e5e5216b4989ff282241e0a57`.
- Corrected source and bounded rechecks: `80311afd2672ff8bea7858a144248257aa00c561`.
- Baseline assessment: direct Issue #276/#279 source comparison in this workflow.
- Verification: Terra xhigh source audit, two Luna max paired routing exercises and root acceptance.

## Decision And Scope

Retain all five skill identities. The three authoring skills own different
document contracts; local and slice implementation own different units and
decision radii. Shared inputs do not make their outputs interchangeable.
Two shared references now define artifact selection, source binding, accepted
scope and necessary handoffs. Consolidation has no demonstrated benefit here
and is not selected. No migration, new mandatory stage or language router is
introduced. Local closure decision: `ready` after the evidence below.

The owner authorized evaluation and local implementation on 2026-09-10. The
earlier merge/closure authorization was completed for PR #291 and Issues
#289/#290. It does not extend to provider delivery of this new workflow.
This report covers #276/#279 local source changes and controlled model routing;
it does not close either online Issue or establish release or production use.

## Responsibility, Inputs And Contract Preservation

The [capability matrix](capability-matrix.md) maps unique/shared responsibility
and stop conditions. The following comparison completes the input, trigger and
document-contract dimensions. Trigger phrases guide selection, not deterministic
natural-language processing; ambiguous output or scope requires clarification.

| Skill | Trigger and representative input | Preserved output, template/schema and validation authority |
| --- | --- | --- |
| requirement-author | Draft/normalize requirements from notes, existing requirements, bounded code context or ADRs | Requirement Markdown under `.dev/requirement/`, `REQUIREMENT-GUIDE.MD`, skill output contract and source-truth rules; no spec/compliance claim |
| spec-author | Draft/normalize a selected spec from requirements, existing specs or code references | Production/entity/adapter JSON or formal test-spec Markdown under `.dev/specs/`; `SPEC-GUIDE.MD`, `SPEC-ORGANIZATION-GUIDE.MD`, selected schema and type-selection contract |
| problem-frame-author | Draft/recover selected CBF/SWF from requirements/specs/ADRs or scoped code/test observations | Extraction sheet and selected frame file set, source-mapping/output contracts and existing frame templates/schema; drafting is separate from compliance validation |
| local-change-implementer | One existing technical target/operation with accepted behavior, direct sites and immediate tests | Bounded local edit, compatibility/validation evidence and scope handoff; existing allowed-operations/radius and effective-rule contract |
| slice-implementer | One accepted behavior or refactoring goal with settled design, source/finding bindings and explicit authority | Exactly one command/query/reactor/generic mode, implementation/validation evidence and role records; existing mode/test/target contracts |

All five asset IDs, capability slots, role bindings and exact
`effective_rule_consumption` objects match the baseline. Machine capability
mappings and existing document templates/schemas are unchanged. Ten Codex/Claude
wrappers and five human guides reflect the canonical boundaries. No historical
workflow, assessment, skill identity or evidence was rewritten. Actual downstream
adoption must still resolve its own effective rules, schema and customizations.

Handoffs carry artifact location, source ID/reference/revision/status, accepted
decisions, open questions, requested next output and existing authorization.
Source bindings belong outside schema fields that do not permit them. There is
no mandatory frame-to-requirement-to-spec sequence: A10 deliberately requests
two linked provisional drafts, while A06 permits observed code-only framing
without inventing normative documents or compliance.

## Observed Routing And Limits

The first paired comparison selected the expected immediate owner in 19/20
cases for both baseline and current guidance. Both had four cases with an
unnecessary required-handoff declaration (A01, A06, I06, I10), no actual scope
expansion and no authority bypass. This does not demonstrate an improvement.
Root rejected those facets despite the workers' successful operation receipts.

The two shared contracts were then corrected. The feedback-informed recheck
covered A01/A06 and I05/I06/I09/I10: 6/6 immediate owners matched, with no
unnecessary required handoffs, actual expansion or authority bypass. I06 now
selects the concrete architecture decision owner; future authoring/repair work
remains optional or conditional. I05/I09 protect architecture-first and unknown-
scope behavior. The other fourteen cases were not rerun; their first results
retain their original commit and are not relabeled as a final full-corpus pass.
The recheck also used clearer response fields, so its improvement cannot be
attributed exclusively to the source wording rather than feedback or protocol.


The fixed [request corpus](routing-cases.yaml) and separate
[parent oracle](routing-oracle.yaml) existed before dispatch. Each Luna worker
recorded baseline decisions before reading the current context bundle; root
graded the returned decisions against the oracle. These are actual model
judgments in a retrospective paired exercise. They are not historical usage
telemetry, independent fresh model sessions, a blind trial, human usability
research or execution of the selected downstream skills. Exposure/learning and
case-selection bias limit any comparison. No production confusion rate, token
cost, latency improvement or universal future routing reliability is established.

The ambiguous requests exercise needed clarification, not a measured human
confusion rate. Parent grading checks requested output, mode, handoffs, scope
and unresolved authority, rather than exact wording or a child self-score.
Full case decisions, child receipts/digests, parent grades and limits are
retained in [observed results](observed-results.json); raw outputs remain in
the declared ignored local evidence roots.

A05's adjacent BDD owner is supported by the capability mapping and authoring
boundary; the routing worker did not inspect the BDD skill's complete canonical
contract. No detailed BDD execution is inferred. A06 names supplied handler/tests
in the request but does not embed those code contents; it measures the chosen
route and missing-authority boundary, not an actually produced frame.

## Context And Maintenance Tradeoff

| Skill | Baseline bytes | Corrected bytes | Increase |
| --- | ---: | ---: | ---: |
| requirement-author | 7,599 | 12,217 | +4,618 |
| spec-author | 7,270 | 12,361 | +5,091 |
| problem-frame-author | 13,773 | 18,782 | +5,009 |
| local-change-implementer | 9,149 | 14,229 | +5,080 |
| slice-implementer | 31,872 | 36,863 | +4,991 |

These numbers count each skill entry, Codex wrapper and unique declared direct
reference once. They are an upper-bound source-byte envelope, not actual
per-request reads, transitive closure or model tokens; the slice envelope
includes unselected modes. Each skill adds one direct shared reference. The
worker context-read observations describe this controlled exercise only.

A reproducible lexical proxy across 22 per-skill reference Markdown files
counts exactly equal trimmed non-heading prose lines of at least 45 characters.
The baseline has 8 repeated lines / 11 occurrences beyond the first; the current
source has 9 / 12. The additional repeated source-binding output line is
intentional. Existing role-execution and mode-contract repetitions remain.
This limited metric does not measure semantic duplication or prove maintenance
savings. The benefit is clear ownership of two cross-skill contracts, with a
real increase in text and one more reference per skill. Broad deduplication or
skill consolidation would need separate evidence and, for consolidation, a safe
migration plan. Required effective-rule declarations are not removed as noise.

## Finding Resolution And Validation

| Source finding | Resolution | Evidence |
| --- | --- | --- |
| A276-01: overlapping inputs obscure artifact owner | Select by requested artifact; clarify unknown output or explicit skill/artifact conflicts | Shared authoring contract, A01-A10 and independent source audit |
| A276-02: formal-test-spec GWT and code-only framing conflict | Keep formal test spec with spec-author; allow explicitly observed/inferred frame recovery without fabricated normative sources | A04/A06/A07, preserved schemas and source bindings |
| A279-01: multi-file handoff wording contradicts local direct sites | File count alone does not expand one target/radius | I01-I03 and local scope references |
| A279-02: accepted design and internal local edits can repeat handoffs | New types stay outside local; settled design uses a slice, internal local delegation is optional | I04/I07/I08 and shared implementation contract |
| A279-03: slice handoff describes reviewer as .NET-only | Use common reviewer core and target-selected technology coverage | Source audit and real package reference validation |

- Terra source audit: passed at the initial source commit, no static blocking
  finding; subsequent parent behavioral findings are preserved and separately
  reconciled. The final admission reviews the corrective source delta.
- Real package payload-reference integrity test: 1 passed, 36.120 seconds at
  the initial source; 1 passed, 41.866 seconds after corrective source changes.
- AI-context validation: passed, 20.834 seconds initially and 22.979 seconds
  after correction; 16 skills and 472 language files.
- Focused effective-rule consumer contract selection: 3 passed, 0.228 seconds.
- Contract-preservation/corpus checks and whitespace check: passed.
- Workflow validation initially failed on an empty completed R01 summary;
  the factual matrix/corpus summary was added and the validator passed.
  That first failure remains recorded, rather than counted as a pass.
- Source package/profile and document contracts are unchanged during closeout;
  rerun the affected workflow and commit checks, not a full release/history matrix.

## Per-Issue Acceptance

| Acceptance | Observable criterion | Local result |
| --- | --- | --- |
| 276-AC1 | Capability matrix distinguishes unique and overlapping responsibilities | passed |
| 276-AC2 | Representative and ambiguous routing cases evaluated | passed |
| 276-AC3 | Document-type contracts and source binding preserved | passed |
| 276-AC4 | No consolidation without demonstrated benefit | passed |
| 276-AC5 | Retained skills have clearer boundaries and handoff rules | passed |
| 279-AC1 | Matrix maps responsibility, input, output and stop conditions | passed |
| 279-AC2 | Fixed corpus covers local, slice and ambiguous requests | passed |
| 279-AC3 | Misroutes, handoffs, scope, context and maintenance metrics reported | passed |
| 279-AC4 | No consolidation without benefit and a safe migration plan | passed |
| 279-AC5 | Retention includes necessary wording/routing/shared-reference improvements | passed |
| 279-AC6 | Historical skill references and evidence remain unchanged | passed |

Each row follows the online Issue acceptance order. The
[acceptance index](acceptance-index.json) maps the rows to separate Issue ledgers
with schema-validated human projections. Actual-execution rows retain the model
receipt's original commit; source/document evidence is separately classified.
Successful tool execution alone does not satisfy semantic acceptance.

## Closure Evidence And Remaining Boundaries

R01, R02, R03, V01 and A01 are complete for this local scope. No acceptance is
deferred within that scope. Production usage, human usability measurement,
actual downstream artifact authoring or test implementation, hosted CI,
provider merge/closure, target upgrade and publication are not claimed.

Only workflow closeout artifacts change after the source/behavior checks.
The final clean commit receives a fresh bounded independent admission review
of the closeout and the preserved source/evidence. Its future result is not
asserted by this tracked report. The declared terminal evidence root is
`ignored:.dev/ai-context/local/2026-09-10-authoring-implementation-boundaries/final_admission/`.
Root must validate that receipt, current content binding, clean checkout and
full acceptance projection before declaring the local delivery complete.
