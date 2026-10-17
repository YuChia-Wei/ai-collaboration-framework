# Common BDD knowledge delivery

Formal work: [#452](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/452),
promoted from #451 after the owner instructed `開始進行修改` on 2026-10-14.
Base: `d334805b60b51574a94ce1634fbdf8158bbed406`.
Local implementation, necessary validation and policy-required commits are in scope;
push, PR, merge, closure, release and real-project installation are not selected.

## Design and ownership

| Topic | Source resource | Consumer / boundary |
| --- | --- | --- |
| Discovery, formulation, automation; rules/examples/questions; source status | engineering-common `references/BDD-METHOD.md` | First skill consumer: bdd-gwt-test-designer design/review when the task needs this method. No new Story or general exploration operation. |
| Gherkin syntax versus design advice; observations and independence; examples | engineering-common `references/GHERKIN-SCENARIOS.md` | Read for requested Gherkin output/review, not every BDD task. |
| Scenario-to-test handoff | Existing GWT-TEST-HANDOFF-CONTRACT | Preserve bytes and contract; no duplicate implementation rules. |
| Runner, language, paths and target adoption | Existing dotnet-backend or target owner | Preserve normative content; common knowledge supplies no technical defaults. |

The existing engineering-common package already supports optional resource selection.
A separate BDD package would create an additional lifecycle and dependency surface
without an independently requested delivery need. Two short resources permit focused
reads. No generic author package is made a consumer just because it concerns requirements.

Version choice: engineering-common 0.1.0 -> 0.2.0 for additive knowledge;
bdd-gwt-test-designer 0.2.0 -> 0.3.0 for the new optional method consumption.
dotnet-backend 0.1.0 -> 0.1.1 and code-reviewer, architect, local-change and slice
skills 0.2.0 -> 0.2.1 only rebind exact dependency versions. Their rule/operation
bytes remain unchanged. Source manifest and current-version manuals follow those
identities; installed selections, locks, adapters and released files remain intact.

The orchestrator owns this source-package change directly under source policy.
The installed local-change operation's symbol-level radius and context-governance
operation's project-context radius do not own product package administration.
No unavailable generic implementation tool is inferred from those skill names.

## Execution stages

| Task | Outcome | State |
| --- | --- | --- |
| T1 | Scope, topic ownership and version consequences | completed |
| T2 | Knowledge, consumer instructions, metadata and manuals | completed |
| T3 | Source checks, isolated package/install and fixed behavioral cases | completed |
| T4 | Immutable review, supported repairs and local delivery | completed |

Parent is the sole tracked writer and integration owner. Three gpt-6.1-sol/low
workers supplied read-only inventory; no discovered text is implementation approval.
Current primary model/effort was read from the active turn context as gpt-6-astra/high.

## Validation plan and expected judgments

Run focused `python -I -B tests/run.py --suite distribution --suite schemas`,
then the fixed default source suite. Existing tests own member/reference/version
closure; do not add string-presence tests that mirror the new prose. Historical
comparable default runs took about 41-57 seconds; this is not a full history/native
matrix. Preserve failed attempts and rerun only after a relevant change.

After local commit, assemble that exact source into an unpublished catalog and
derive explicit BDD+common and BDD-only selections. Use fresh isolated consumers,
the existing inspect/plan/apply/inspect API and pinned installed-resource reader.
These synthetic targets have no product data, sessions or competing writers.
Select only process-termination durability and Windows inventory mode; do not claim
native recovery, crash durability or downstream adoption from this evidence.

Fix these four behavioral judgments before execution; the actor receives task
prompts and installed inputs, not this expected-answer table:

| Case | Prompt | Expected judgment |
| --- | --- | --- |
| B1 discovery only | Explore whether overdue library loans may be renewed; no policy is supplied. Do not write scenarios yet. | Rules/examples/questions, overdue policy unresolved, no .feature, no coverage or authority claim; BDD method selected, Gherkin unnecessary. |
| B2 scenarios only | Agreed R1/AC1: another member's reservation prevents renewal and preserves due date. Design requested Gherkin for L7, due 20 October, reserved by Ben, borrower Ada. | Concrete independent setup, request event, refusal and unchanged due-date observations, source mapping, no runner installation or execution claim; Gherkin guidance relevant. |
| B3 combined | Explore renewal and formulate supported examples; R1 is agreed, overdue policy is unknown; scenario notes are enough. | Reuse R1/AC1, mark overdue unknown/provisional, preserve both outcomes, no invented approval and no compulsory author sequence; Gherkin unnecessary. |
| B4 no knowledge | On a BDD-only installation, design the same agreed refusal scenario from caller inputs. | Report common package coverage unavailable, continue bounded GWT design, no source fallback or installation; actual installed reader lists no common resources. |

Package/install/binding changes require independent read-only review under source
rule 6. Bind the immutable diff, Issue AC01-07 and governing policies; author
inspection and agent behavior samples do not substitute for independent review.

## Evidence and pending operations

Results and retained attempt limitations are in [validation.md](validation.md);
task records report actual outcomes. Implementation commit is
`c9439c1d29c21fe27f0415b62c910e9aabffe790`. The local delivery scope is complete:
117 focused and 243 default source tests, two actual isolated installations,
verified installed resources, B1-B4 agent samples and independent scoped review.
The initial shared-context sample could not prove per-case resource isolation;
separate fresh B1/B3 samples supplied that evidence without source changes.
Raw actor reports are retained in `evidence/`. No statistical or token claim follows.
The repository-wide graph advertised this HEAD but returned retired tests and no
known current catalog functions. Treat that coverage as stale: tracked-file fallback
was used for exact current test/tool paths, and distribution was reindexed separately.
No absence conclusion was drawn from graph search.

Issue #452 remains open until separately authorized integration and terminal gates.
No release allocation or source-project self-installation follows this workflow.
