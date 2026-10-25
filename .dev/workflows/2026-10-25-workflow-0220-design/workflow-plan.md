# Workflow 0.22.0 design and SQLite task increment

## Scope and authorization

The owner requested in this chat on 2026-10-25: "由這個對話開始進行 #416 這個 Epic".
This authorizes beginning the Epic and its current design predecessor, #483.
The first delivery is the responsibility, public-operation and migration design;
it does not choose unaccepted provider, ownership, recovery or source-cutover policy.
Push, PR, merge, publication and installation retain their separate authority.
The later owner direction below authorizes beginning implementation and the
required work-item organization; initial no-provider-write status is historical.

The owner subsequently requested that adapters transmit each workflow update to
multiple carriers without repeated AI output, while reads use the user's unique
selected source. The owner asked whether to add a later implementation Story or
integrate this into existing Stories. The follow-up answer explicitly selected
per-carrier results, "synchronization incomplete", durable pending deliveries and
bounded adapter retries when one target fails. These are current user inputs;
the public requirements are being reconciled to them with exact readback.

The owner then clarified that ordinary use pairs with an online Issue system,
asked to reassess removing or merging local-backlog, selected Workflow Board as
the online platform, explicitly requested a new Board development chat if
multi-project support is missing, and authorized proceeding absent blockers.
The selected direction is B with optional local items and compatible retirement
of the standalone skill; workflow creation does not require local-backlog.
The owner accepts clearing/reimporting current online data if necessary, but no
such action has occurred. Complete export, input mapping and restore readiness
must precede any destructive rebuild; clearing is not needed to add project scope.

## Identity and delivery unit

- Repository: `YuChia-Wei/ai-collaboration-framework`.
- Checkout: `C:\Github\YuChia\ai-collaboration-prompts-dotnet-backend`.
- Base and inspected source: `b6de8cdb28404296e41f2b15079675cc96c7b8e4`.
- Local main, origin/main and GitHub live main matched that source at kickoff.
- Branch: `codex/2026-10-25-workflow-0220-design`, created before material writes.
- Initial working tree: clean; no attached worktree was available or needed.
- The bounded delivery now joins #483 design with its first #481 SQLite operation.
  Board development, online adapter, fanout and adoption remain separate increments.
  This record does not claim to execute all Features or complete Epic #416.
- Proposed eventual integration: linear, because this bounded design delivery has
  no migration or external lifecycle execution requiring a merge node. Not executed.

The workflow preserves unique owner decisions, the cross-skill design handoff
and the transition from the current Git record policy to future source adoption.
That is why a durable workflow is appropriate despite the low task count.
Current ARTIFACT policy still requires a Git-trackable root. This is a bootstrap
record before #514 cutover, not evidence that no-Git workflow adoption is complete.

## Work and current result

| Task | Owner | Status | Result / next boundary |
| --- | --- | --- | --- |
| DESIGN | software-architect, coordinated by software-development-orchestrator | completed | [Design](../../design/workflow-0220-2026-10-25/design.md) includes latest owner direction and remaining decisions; Issue closure separate |
| CREATE-TASK | slice-implementer | in_progress | Implementation and focused checks complete; independent review of recovery-history validation pending |

Live native hierarchy was read through GitHub GraphQL, not inferred from body links:
#416 has #481 (child #483), #513 (child #445), and #514 (no child at readback).
All six Issues were open at kickoff. Subsequent work created Framework #520 for
multi-carrier delivery and Board #22 for missing same-owner project scopes.

The draft recommends data integration with separate orchestration (B), explicit
operation/replay semantics, preservation-first migration, and a separate multi-carrier
implementation Story after the selected adapters. #483 should define its interfaces
now; #481/#445 should expose per-provider primitives, and #514 should verify actual use.
The new Story is #520, linked through native sub-issues under #513 and added to
Project #3 as Planned / P1 High / v0.22.0 / Design discussion / Pending owner review /
Not yet published. #416, #481, #483, #513, #445 and #514 body changes were read back
exactly after update. The prior #416 single-writable-store wording is reconciled with a proposed
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
serving-model identity was not independently observable. The parent was the
only tracked writer during design. Their observations support the draft; they are not an
independent review of the resulting design, nor runtime acceptance.

The workflow-records scoped graph reported ready at the input SHA and was useful
for function discovery. Other graph results included a removed `.ai/scripts/`
validator, so current tracked files were used as explicit fallback for absent or
out-of-scope paths. No negative graph result was treated as proof of absence.
The removed validator was not restored or executed.

Primary evidence and operation limitations are linked in design sections 2 and 7.
During design, existing test files were read as coverage locations without execution.
For the SQLite increment, `sqlite_create_task` was the sole tracked writer for six
source/test files while the parent paused repository edits. This registered
`bounded-general-worker` selected `implementation -> gpt-6.1-sol / medium`; no
runtime model pin was present and actual serving identity remains unknown.
It returned writer ownership after implementation and focused checks. No installed
projection, catalog/profile selection or package version was changed; versioning
belongs to the later cohesive #481 release rather than each unpublished increment.

## Validation selection and actual results

The initial design commit changed only the draft, navigation and execution records.
Its selected checks were JSON/YAML parse, locator/task/path relationships, Markdown
links, whitespace and author inspection against #483 AC01-AC07. The later increment
changes SQLite behavior, operation metadata and backup history validation. It needs
direct SQLite and Git compatibility tests, package closure, and independent scoped
read-only review of an immutable diff under SOURCE-DEVELOPMENT-POLICY rule 6.
The full `python -I -B tests/run.py` hosted source gate now applies when a PR is
created; it has not run. No PR, installation or live migration exists for this work.

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
- At the initial design boundary, product tests, hosted checks, installation and
  migration were not executed. That statement does not describe the later increment.

The implementation checks ran from this checkout with Python 3.13 using isolated
`python -I -B -` stdin runners and process-local `tempfile.tempdir` set to
`F:\tmp\aicf-416-create-task`. Global TEMP/TMP were not changed.

- First runner loaded `tools.test_workflow_sqlite` and `tools.test_workflow_records`
  through `unittest.defaultTestLoader.loadTestsFromNames`, with `tests` on sys.path.
  It also parsed metadata and asserted `create-task` in the tool and runtime operation
  lists. Result: 49 test methods in 52.109 seconds; 47 passed and two failed with
  three assertions. The new tests incorrectly selected a revision by SQL hash order
  and expected `invalid_input` where existing task validation returns `malformed_record`.
- After correcting those test expectations, the second runner loaded the two affected
  methods (`SQLiteRecordTests.test_create_task_cli_fifty_additions_preserve_history_and_export_closure`
  and `SQLiteRecordTests.test_create_task_malformed_envelopes_and_tasks_do_not_write`)
  plus `Metadata5DistributionTests.test_workflow_records_is_optional_and_manifest_matches_metadata`.
  Module names were `tools.test_workflow_sqlite` and
  `framework_next.test_distribution_contracts`, with `tests` and `tests/framework_next`
  on sys.path. All 3 passed in 16.672 seconds. The unchanged 47 results remain applicable.
- Combined final evidence covers 50 distinct methods (52 executions), including
  seven new tests. This is not a single green 50-test run. It covers public CLI
  readback, 50 task additions, state/history/blob preservation, replay and ID collision,
  stale inputs, concurrent clients, capacity and rollback, unsupported Git writer,
  export/restore and rejection of forged history. It proves logical/process behavior,
  not physical power-loss durability or actual downstream adoption.
- Author inspection and `git diff --check` passed. Recovery-related independent
  review and its correction are recorded below; no integration acceptance is inferred.

### Independent review and correction

`create_task_audit`, the registered fixed-head-independent-auditor, performed the
explicitly selected recovery review under `code-reviewer` on clean commit
`ee5a2021b8038ab16dd33c0d91e584a789b06a98`, base
`9d8ac6c909befdaa1dd44bc9e15fd2e78712f41d`. Selection was
`independent-review -> gpt-6.1-sol / medium`; runtime source and projection hashes
matched, with no model pin. Actual serving identity remains unknown. Review stayed
read-only with no test execution and covered the six changed implementation/test/
metadata/documentation files plus necessary direct dependencies and accepted criteria.

Finding R1 (P2): the new backup transition check used Python equality for retained
JSON fields. That admits `true -> 1` in an existing task extension after a forged
child revision and receipt are rehashed. Static review identified a concrete
preservation violation; the parent reproduced it before repair. The expanded
`test_create_task_backup_rejects_rehashed_changes_to_prior_task` failed for integer
1 in one method (0.677 seconds), while the existing false-value case was rejected.

The correction compares canonical encoded JSON for all retained fields and the
prior task prefix in the new `create-task` branch. Existing operation behavior is
unchanged. A focused `python -I -B -` unittest runner then passed these four methods
from `tools.test_workflow_sqlite.SQLiteRecordTests` in 19.232 seconds:

- `test_create_task_backup_rejects_rehashed_changes_to_prior_task`
- `test_create_task_cli_fifty_additions_preserve_history_and_export_closure`
- `test_complete_export_restore_preserves_history_extensions_blobs_and_receipts`
- `test_corrupt_backup_preflight_and_existing_target_refuse_before_restore`

The runner used `tests` on sys.path and the same process-local F: scratch. Both the
initial review failure and red reproduction remain evidence. Affected independent
readback is pending the corrective fixed commit; no clean-review conclusion yet.

## Resume without private conversation

Board #22 is assigned to the explicitly requested chat
`01a171b0-1260-7990-a8fe-23cd6614efb0` (local host), titled
"實作 Board 多專案 workflow 隔離與選擇". It owns Board changes only. Baseline main
`ea161dcbbe045eb9b22468348da94fcae4bba567` was clean; private Site version 14 and
live collaboration/1 capabilities were read. The chat is actively implementing;
that dispatch is not evidence of feature completion. Read status through wait_threads.
Current multi-project gap and Board #6 recovery limits prohibit premature full migration.

Read this record, the design, live Issues and current working tree first. Keep
the parent's draft separate from accepted product policy. The next action is the
affected fixed-commit review of the R1 correction, preserving the owner's
multi-carrier and partial-failure decision. Do not ask the owner again whether
partial synchronization should be visible and durably retried; that is selected.

Outstanding decisions are the unresolved rows D02-D07 in the design: Git writer
retirement cutover, exact persistent DB path, command authority/replication parameters,
disaster activation/retention and optional multi-executor claim. B, Board and #520
are now selected. Resolve only the choice required
for the next increment. Do not block independent design work on platform selection.

Public requirements may describe the new product behavior and dependencies; they
must not contain this authorization history, agent assignments or resume checkpoint.
After a selected requirement update, read back actual Issue text/hierarchy. Carry
unchanged completed design analysis forward rather than repeating repository discovery.
