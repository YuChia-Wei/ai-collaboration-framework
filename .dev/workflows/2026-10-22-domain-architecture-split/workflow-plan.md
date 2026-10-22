# Domain modeling and software architecture split

## Authority and coherent delivery

Owner's 2026-10-22 instruction authorizes complete design, another agent's review before
source edits, Chinese Feature/User Story creation, then local implementation and necessary
validation. Accepted names: domain-model-designer and software-architect. Retire the old
combined skill without alias. Preserve unrelated untracked 2026-10-19/20 workflow folders.

One coherent delivery contains [Feature #476](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/476)
and Stories [#477](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/477),
[#478](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/478),
[#479](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/479), and
[#480](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/480).
Domain work comes first; distribute the complete coordinated result together.

Local-workflow [Feature #481](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/481)
and design [Story #483](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/483),
customization [Feature #482](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/482)
and design [Story #484](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/484)
are separate future work. They were created and read back open with Chinese scope/ACs;
no implementation or provider/data migration is included here. Issue parentage is explicit
bidirectional body links; native GitHub sub-issue fields were not set by the connector.

## Design and baseline

- Source baseline: f96fffe0af6e9e4f79d5f2f4be05bb3665553123.
- [Complete design](../../design/skill-evolution-2026-10-22/README.md).
- Initial immutable design: 4ade82bcc2eb4f8bc1230dbe9905c4db58293cbf.
- Review: /root/split_design_review, separate author, fresh context, read-only fixed commit.
- Current phase: completed for the authorized implementation and review follow-up. The received reviewer identifies as macOS / Claude Fable 5.1, not the originally intended Opus. R1-R3 design corrections at 3a3e3098 were independently verified resolved before source edits. PR/integration and proposed product follow-ups retain separate authority.
- [Implementation and validation](implementation-results.md); [independent source review](source-review.md) covers 51865868 and the verified F1 correction at 589abfcd.
- Parent is the only tracked writer. Read-only delegates assist discovery/review only.
- Configured fallback model/effort: gpt-6-astra/low; actual provider execution identity is
  not exposed. Delegates inherit session settings; no model/effort override was requested.

## Work and acceptance

DESIGN owns self-contained documentation, immutable review, finding disposition and Issues.
IMPLEMENT owns the five principal skill boundaries, two new packages, knowledge/preset/version
closure, old-ID removal and human/source navigation. VERIFY owns the directly affected
checks, fixed-source review and honest delivery limitations. See each task JSON for state.

Acceptance is A-AC-01 through A-AC-13 in skill-contracts.md and F-AC/Story criteria in Issues.
Existing distribution/schema suites and narrow selection/binding tests are selected because
public operation/selection/dependency contracts change. Full installation/native/E2E/AI model
matrices are not selected. Document-only stage used local-link validation (110 links in 11
changed Markdown files) and git diff --check; no product test pass is claimed for that stage.

## Delivery boundary and next action

The original design, implementation and source review are complete. On 2026-10-22,
the owner separately authorized updating the existing Windows Preview and an
Antigravity / Gemini 4 Argon review, then correcting its two optional wording
suggestions and pushing this branch for macOS / Claude Opus review. Continue
Feature #476 and Stories #479/#480; do not create replacement Issues.

The two source wording corrections and the external review evidence/limitations
are recorded in [implementation results](implementation-results.md). They do not
change package versions, operation contracts, bindings or installation behavior.
The Windows Preview remains at 438b15eb; these subsequent wording corrections are
source-only. The original source-project 17-skill installation is also unchanged.

### Historical macOS / Claude Opus handoff (completed transport)

- Repository: `https://github.com/YuChia-Wei/ai-collaboration-framework.git`.
- Transport: owner-authorized push-only checkpoint on
  `codex/plan/skill-evolution-20261022`; integration base is `main`.
- Fetch and check out that remote branch, not `main`. Record the exact fetched
  `git rev-parse HEAD` as the immutable review subject; this document's containing
  commit is the handoff checkpoint. Verify remote HEAD before starting.
- Read this entry, the linked complete design and A-AC-01 through A-AC-13,
  implementation results, source-review.md and Issues #476–#480.
- Review the complete implementation against source baseline
  `f96fffe0af6e9e4f79d5f2f4be05bb3665553123`; use `438b15eb` as the narrower
  baseline for these final wording corrections. Preserve the four walkthroughs
  and responsibility/knowledge boundaries. Report concrete findings and actual
  coverage; do not reuse the Gemini report's unchecked line references as proof.
- The owner's intended next actor is Claude Opus on macOS. The exact model,
  effort and execution are not observed here; the receiving session must record
  its actual selection. No macOS review has run in this session.
- Next action is read-only analysis/review. Source fixes, another installation,
  native runtime acceptance, PR creation, merge, Issue closure, Project changes
  and release/publication are not implied by this handoff. Required hosted PR
  checks remain pending; local results are not hosted acceptance.
- Preserve unrelated local workflow folders dated 2026-10-19 and 2026-10-20;
  they are untracked and excluded from the pushed checkpoint.

Transport read-back at 2026-10-22T08:26:22+08:00: checkpoint
`1e397036bb3cf50ad99f08149529476964943844` was pushed to the branch above;
`git ls-remote --heads origin refs/heads/codex/plan/skill-evolution-20261022`
matched local HEAD. The final record-only follow-up retains that source subject.
At that checkpoint, O1/O2 source wording correction and handoff preparation were
complete. The intended next actor was the user's macOS / Claude Opus reviewer.
The follow-up below records the actual received review. No PR or merge was performed.

## 2026-10-22 external review follow-up

The owner authorized reading the latest Slack analysis, arranging corrections,
and updating design and existing online User Stories. Continue the same branch
and Issues. [Review dispositions and follow-up design](../../design/skill-evolution-2026-10-22/review-follow-up.md)
bind reports 26/27 to subject `6694b8b099c8fcc3063f498f008df698756e0a92`.
The reported 130 tests and macOS trials remain attributed external evidence;
the original raw receipts were not independently executed here.

FOLLOWUP owns migration/installed-route clarification, historical navigation,
knowledge/role documentation, precise C/D design boundaries and existing Issue
reconciliation. Product-engine changes, compatible-version pins, behavior fixture
execution, source self-installation and milestone selection remain unperformed.

Validation selection: inspect changed explanatory text, bilingual route parity,
relative links, workflow JSON/YAML, Git diff, and actual Issue read-back. This
diff does not alter product behavior, authority, installation or recovery; the
root entry clarifies an already installed route. No product suite or additional
model review is selected merely for this documentation update. The branch's
eventual PR still retains applicable hosted and independent-review requirements.

At that checkpoint, the next product action, if selected, was the bounded R26-3 derive-result diagnostics
change in #480. #483/#484 remain design proposals. Push continues the existing
owner-authorized review branch; PR/merge/closure/release are separate.

### Follow-up result

Documentation/design correction commit:
`b2eec8b1d2d6708ec1b6f01838c8b388b7967ba3`.
Checked 99 local links across 14 changed/added files with no missing targets;
changed JSON/YAML parsed successfully, bilingual installed-route meaning agrees,
and `git diff --check` passed. Product tests were not rerun for this explanatory
diff. The original source implementation and external results retain their
fixed subjects and limitations.

Updated bodies of existing Issues #43, #149, #153, #168, #416, #443, #460 and
#476–#484. Each body was fetched immediately before writing and matched the
intake snapshot. A separate fetch after writing confirmed every intended body
and unchanged title/state/labels/assignees/milestone; all sixteen remain open.
No Issue was created or closed, and no Project mutation was made. #179 and #445
already retain the relevant optional/deferred boundaries and were not rewritten.

R26-1/R26-2 and explanatory S4/S5/F4 corrections are complete. R26-3 remains a
concrete unimplemented follow-up in #480; optional behavior evaluation in #479,
pin policy alternatives and C/D product decisions remain separately selectable.
The incorrect D-P3-04 attribution was corrected in design and #481/#483 without
declaring any unaccepted supersession. #43 remains initial-intake work.

At that checkpoint, all workflow-owned authorized tasks were complete. That lifecycle completion
does not close provider Issues, claim hosted CI, authorize integration, select
a release, or update either installed target. The containing record commit is
to be pushed on the already authorized branch; final transport read-back belongs
to the delivery response rather than another evidence-only commit.

## 2026-10-22 remaining-defect repair and merge preparation

The owner subsequently authorized repairing all three confirmed remaining
defects, continuing the existing branch and work items, and preparing for
their review before arranging integration. The intended integration closes
only delivered work items; the owner plans further changes before a later
release. No merge, closure, version allocation, tag or publication is performed
by this repair task. Gemini may be used as a bounded delegate; the owner also
authorized communication through the existing ROBO Agents Slack DM when useful.

REPAIR uses slice-implementer generic mode with the remediation overlay. The
parent is the only tracked writer. Fixed input: `329571b583cc6290f4c0950a232675bd3edbb45f`.
The fresh reviewer and Gemini evidence is retained in the external Preview
Notes; these findings are pre-existing, not regressions introduced by the split.

- #480 R26-3: expose the existing resolver `unavailable` list in the successful
  library/CLI result, including an empty list; preserve required-dependency
  failures, selection/lock/artifact identity and no implicit installation.
- #480 portable-role follow-up: replace fixed auditor's unavailable source
  preflight/classifier/packet-tier/digest admission with explicit bounded
  parent inputs. Preserve independent read-only review, fixed clean subject,
  drift stops, actual authority, failure history and no integration acceptance.
- #480 portable-role follow-up: replace undefined `role_bindings` authority in
  four roles' eight projections with the real owning skill/operation, canonical
  role, bounded assignment and target rules. Do not introduce a new schema.

Validate public diagnostic behavior with focused regression cases and the
existing distribution/schema suites; exercise real pinned CLI output at the
fixed repaired source because the public result changed. Validate role metadata,
runtime projection parity and unchanged tool/model permissions. The authority
changes require independent scoped read-only review of the committed diff.
Do not add lexical role tests, a preflight platform, ledgers or a model matrix.
Retain the actual hosted PR gate separately from local results. Update existing
Issue acceptance and the proposed closure set; #481–#484 remain deferred product
design work and are excluded from this delivery's closure set.

### REPAIR implementation checks

The successful focused run was `python -I -B tests/run.py --suite distribution
--suite schemas`: 133 tests, zero failures/errors/skips. Three new in-memory
cases exercise real resolution, projection and metadata/identity, replacing
only execution-source admission and disk emission; they do not claim a native
installation. A real pinned CLI check remains pending at the committed source.
Four role pairs have equivalent shared Codex/Claude instructions and unchanged
model/tool permissions; metadata parses and 26 local documentation links pass.

Retained initial failures: the first run had three new fixture errors (skill
knowledge dependencies were incorrectly written as skill dependencies) and four
source-byte assertions caused by Windows CRLF introduced during editing. The
fixture now uses the existing knowledge_consumption contract and the changed
sources retain LF. A targeted retry found the fixture's unsupported on_missing
value; it was corrected to the existing schema before the successful suite run.
No product validation was weakened. Independent committed-diff review and public
CLI evidence are still pending; this task remains in progress.

### REPAIR result

The three selected defects are repaired at `01eabd7f4399ff1fe31edd30e49119372f7484b7`.
[Repair review and integration handoff](repair-review.md) records 133 passing
checks, authentic pinned CLI cases, independent review, Gemini interruption/retry
and candidate disposition, Preview read-back, Slack handoff and five live Issue
body updates. Remaining provider integration and publication boundaries are
explicit; they do not keep the completed local repair active. No product content
changed after the independently reviewed commit. Final record-only transport
will remain on the existing branch.
