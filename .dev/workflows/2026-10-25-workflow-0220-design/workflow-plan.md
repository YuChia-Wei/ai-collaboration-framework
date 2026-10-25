# Workflow 0.22.0 design checkpoint

## Scope and authorization

The owner requested in this chat on 2026-10-25: "由這個對話開始進行 #416 這個 Epic".
This authorizes beginning the Epic and its current design predecessor, #483.
The first delivery is the responsibility, public-operation and migration design;
it does not choose unaccepted provider, ownership, recovery or source-cutover policy.
Push, PR, merge, public Issue/Project changes, publication and installation retain
their separate authority. No such external write has occurred in this checkpoint.

The owner subsequently requested that adapters transmit each workflow update to
multiple carriers without repeated AI output, while reads use the user's unique
selected source. The owner asked whether to add a later implementation Story or
integrate this into existing Stories. The follow-up answer explicitly selected
per-carrier results, "synchronization incomplete", durable pending deliveries and
bounded adapter retries when one target fails. These are current user inputs;
the live Issue bodies have not yet been revised to incorporate them.

## Identity and delivery unit

- Repository: `YuChia-Wei/ai-collaboration-framework`.
- Checkout: `C:\Github\YuChia\ai-collaboration-prompts-dotnet-backend`.
- Base and inspected source: `b6de8cdb28404296e41f2b15079675cc96c7b8e4`.
- Local main, origin/main and GitHub live main matched that source at kickoff.
- Branch: `codex/2026-10-25-workflow-0220-design`, created before material writes.
- Initial working tree: clean; no attached worktree was available or needed.
- One source design delivery under #483; #481, #445/#513 and #514 remain distinct
  implementation/adoption boundaries. This record does not claim to execute all
  Features in one branch or to complete Epic #416.
- Proposed eventual integration: linear, because this bounded design delivery has
  no migration or external lifecycle execution requiring a merge node. Not executed.

The single task preserves unique owner decisions, the cross-skill design handoff
and the transition from the current Git record policy to future source adoption.
That is why a durable workflow is appropriate despite the low task count.
Current ARTIFACT policy still requires a Git-trackable root. This is a bootstrap
record before #514 cutover, not evidence that no-Git workflow adoption is complete.

## Work and current result

| Task | Owner | Status | Result / next boundary |
| --- | --- | --- | --- |
| DESIGN | software-architect, coordinated by software-development-orchestrator | in_progress | [Design draft](../../design/workflow-0220-2026-10-25/design.md) is ready for review; owner choices and requirement-change disposition remain open |

Live native hierarchy was read through GitHub GraphQL, not inferred from body links:
#416 has #481 (child #483), #513 (child #445), and #514 (no child at readback).
All six Issues were open. No Issue or Project state was changed.

The draft recommends data integration with separate orchestration (B), explicit
operation/replay semantics, preservation-first migration, and a separate multi-carrier
implementation Story after the selected adapters. #483 should define its interfaces
now; #481/#445 should expose per-provider primitives, and #514 should verify actual use.
The new Story is proposed, has no assigned Issue number and has not been published.
The prior #416 single-writable-store wording needs reconciliation with a proposed
single logical command authority and multiple physical carriers; that mechanism is
not owner-adopted merely because the new product goal was requested.

## Evidence and delegation

Owning skills read: installed `software-development-orchestrator` orchestrate,
`software-architect` design, and `requirement-author` explore/authoring for the
new requirement split. No additional optional knowledge package was presumed installed.

Two read-only semantic-governance-analyst assignments inspected the fixed source:
`local_record_contract` and `source_adoption`. The registered project package and
runtime entry were checked; neither has a model pin. Both selected
`semantic-review -> gpt-6.1-sol / medium` from the project model policy. Their actual
serving-model identity was not independently observable. The parent remains the
only tracked writer. Their observations support the draft; they are not an
independent review of the resulting design, nor runtime acceptance.

The workflow-records scoped graph reported ready at the input SHA and was useful
for function discovery. Other graph results included a removed `.ai/scripts/`
validator, so current tracked files were used as explicit fallback for absent or
out-of-scope paths. No negative graph result was treated as proof of absence.
The removed validator was not restored or executed.

Primary evidence and operation limitations are linked in design sections 2 and 7.
Existing test files were read as coverage locations, not executed or treated as passes.

## Validation selection and actual results

This increment changes a design draft, navigation and execution records only.
It does not change product behavior, schemas, installed entries or effective policy.
Required local checks: changed JSON/YAML parse, locator/task/path relationships,
changed Markdown links, whitespace and author inspection against #483 AC01-AC07.
No product tests or installation matrix are selected for this draft. Hosted source
gate is not applicable to a diff without src/** or tools/** changes; no PR exists.

- `git status --short --branch`, `git remote -v`, `git rev-parse HEAD`: inspected kickoff identity.
- GitHub connector fetched #416/#481/#483/#513/#445/#514 and live main; read-only
  `gh api graphql` confirmed native child counts and identities.
- Sandboxed `git ls-remote origin refs/heads/main` failed DNS resolution; connector
  main readback supplied the required identity instead. No failed command is a pass.
- Scratch probe could not establish usable F: inside the sandbox. A subsequent
  approved read-only probe confirmed ready RAMDRIVE with approximately 16.7 GB free.
  Commit-message scratch is bounded to `F:\tmp\aicf-416-design`; no global TEMP/TMP
  or alternate scratch location is selected. Durable artifacts remain in this repo.
- Inline Python/PyYAML check parsed the changed JSON/YAML, verified locator/task
  identity, timestamps, template/artifact paths and status relationships, and checked
  29 local Markdown links. Whitespace check and `git diff --check` passed.
- Read-only architecture review by `source_adoption` of design SHA-256
  `BB01746BD359DD294A0D1A08ACC97328DDDB12821701102F1B8803596EADB465` found one
  material issue: command acceptance and durable fanout intent needed an explicit
  atomic boundary. The parent corrected section 5 and added crash-window scenario
  S13. Affected readback of revised design SHA-256
  `060AAB63888A4E38DECCD1B4C98008AD41D4E9244B4DA3595F82EE33A2FE7F54` accepted the
  correction with no material residual omission in that finding's scope. This is
  artifact review, not independent fixed-commit implementation review or runtime acceptance.
- Product tests, hosted checks, installation and migration were not executed.

## Resume without private conversation

Read this record, the design, live Issues and current working tree first. Keep
the parent's draft separate from accepted product policy. The next action is to
review the design and finalize the proposed Story placement, preserving the owner's
multi-carrier and partial-failure decision. Do not ask the owner again whether
partial synchronization should be visible and durably retried; that is selected.

Outstanding decisions are D01-D08 in the design: combined data owner, Git writer
retirement, persistent DB/source identity, online provider/client/account, exact
command authority/replication parameters, disaster activation/retention, optional
multi-executor claim and new Story/version scope. Resolve only the choice required
for the next increment. Do not block independent design work on platform selection.

Public requirements may describe the new product behavior and dependencies; they
must not contain this authorization history, agent assignments or resume checkpoint.
After a selected requirement update, read back actual Issue text/hierarchy. Carry
unchanged completed design analysis forward rather than repeating repository discovery.
