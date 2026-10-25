# Workflow 0.22.0 records and Board V2 adapter

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
- The bounded delivery joins #483 design, its first #481 SQLite operation, and
  the first #445 Board V2 query/receipt adapter. Board writes, fanout and adoption
  remain separate increments.
  This record does not claim to execute all Features or complete Epic #416.
- The owner subsequently selected `--no-ff` integration because the branch now
  contains multiple durable commits. Preserve a distinct merge commit; do not use
  fast-forward, squash or rebase merge. This replaces the earlier linear proposal.
  Integration itself remains unexecuted.

The workflow preserves unique owner decisions, the cross-skill design handoff
and the transition from the current Git record policy to future source adoption.
That is why a durable workflow is appropriate despite the low task count.
Current ARTIFACT policy still requires a Git-trackable root. This is a bootstrap
record before #514 cutover, not evidence that no-Git workflow adoption is complete.

## Work and current result

| Task | Owner | Status | Result / next boundary |
| --- | --- | --- | --- |
| DESIGN | software-architect, coordinated by software-development-orchestrator | completed | [Design](../../design/workflow-0220-2026-10-25/design.md) includes latest owner direction and remaining decisions; Issue closure separate |
| CREATE-TASK | slice-implementer | completed | Implementation, focused checks and independent recovery review complete; R1 corrected and read back |
| BOARD-V2-QUERY | slice-implementer | completed | Additive Board V2 query/receipt profile, 15 actual selected-plugin queries and independent fixed-commit review complete; see design section 11 |
| BOARD-V2-COMMAND | slice-implementer | completed | Implementation, selected-plugin validation and independent fixed-head review complete |
| HISTORY-COPY | software-development-orchestrator | pending | Exact Git inventory retained; Board #24 source-replica implementation is under repair after independent review; real import not run |
| MULTI-CARRIER | slice-implementer | in_progress | SQLite schema-2 snapshot, transactional outbox and recovery implementation |
| SOURCE-MIGRATION | software-development-orchestrator | pending | Persistent store, migration, installation and source-policy cutover not performed |

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
initial review failure and red reproduction remain evidence. The same independent
reviewer read corrective clean commit `5d8efd8ef663a09e8b3f1551798419432e819240`
against `ee5a2021b8038ab16dd33c0d91e584a789b06a98`, confirmed R1 addressed and
reported no supported new regression in the affected delta. It performed no tests.
Unchanged source, criteria and governing rules retain the prior scoped review;
this closeout changes only execution records and navigation, with source/test equivalence checked.

At commit `8c5c879251cd52f3c77268615af7c724ae60945a`, both original tasks were terminal.
That completed the bounded design and
SQLite create-task increment, not Epic #416, full #481/#483 acceptance, integration,
release or adoption. All related Issues remain open. Later implementation still
includes task editing/transitions, the remaining local operation contract, optional
local work-item parity/migration, Board adapter #445, fanout #520 and source adoption
#514. Their completion is not inferred from this local checkpoint.

## Resume without private conversation

### 2026-10-25 continuation after Board deployment

The user explicitly asked the Board chat to hand deployment/acceptance back here,
verify V2 availability in this conversation, and continue the original integration.
The handoff reported merged Board PR #23, main `b100c9f9bd09b2a1c125c8b511f06defeb29c556`,
CI run 40170618704 and private Site version 15. Those are handoff observations;
this conversation independently called the selected plugin's V2 queries.
The original branch and clean HEAD `8c5c879251cd52f3c77268615af7c724ae60945a` were
read back. The existing dedicated branch continues the same Epic; completed tasks
remain terminal, and the new implementation task supplies the unique current state.

The [prerequisite evidence](board-v2-prerequisite-evidence.json) records 58 visible
tools (32 V2), project discovery, A/B contexts, exact documents and receipts. Initial
context requests used limit 100 and were rejected by connector schema before
execution; the corrected limit 20 calls succeeded. Formal project ID
`ai-collaboration-framework` was explicitly selected by the user, created using
operation `framework-project-create-20261025`, and read back with its accepted
receipt at revision 1. No synthetic A/B data became formal project data.

Read-only analysis established that local `/1` cannot losslessly encode Board V2.
The parent selected the additive profile and deterministic prepare/plugin/accept
bridge described in design section 11. This is the current #445 increment; a
title-only SQLite revise-task can follow independently, while lifecycle policy
remains unresolved. Source adoption, fanout and full recovery are still separate.
No Framework push, PR, merge, installation or publication authority is inferred
from Board's separate deployment authorization. Existing online data is retained.

### Board adapter implementation and validation

`sqlite_create_task` implemented the new query-mode slice as sole tracked writer
under the registered bounded-general-worker profile, selecting gpt-6.1-sol/medium
from the project implementation policy. Actual serving identity is unknown. It
returned writer ownership after eight source/test/manifest changes; existing `/1`
runtime and installed projections were not changed. The CLI and one declared
runtime module are standard-library-only, with no Board-checkout dependency.

Its `python -I -B -` unittest runner inserted `tests` and `tests/framework_next`
in sys.path, set process-local tempfile.tempdir to `F:\tmp\aicf-416-board-v2`, and
loaded `tools.test_workflow_board_query` plus
`framework_next.test_distribution_contracts.Metadata5DistributionTests.test_workflow_records_is_optional_and_manifest_matches_metadata`.
All 24 methods passed in 0.979 seconds (23 new plus package closure). After adding
explicit-null structuredContent rejection, the affected MCP representation method
passed again in 0.003 seconds. No global TEMP/TMP was changed.

Parent inspection found that json.loads(bytes) also accepts UTF-16 despite the
declared UTF-8 input contract. An added UTF-16 case reproduced the gap (one method
failed in 0.003 seconds). Decoding strict UTF-8 before JSON parsing corrected it;
the malformed-input and isolated file/stdin CLI methods passed in 0.694 seconds.
The failure remains recorded. This does not affect earlier valid UTF-8 inputs.

The [live adapter evidence](board-v2-adapter-evidence.json) records 15 successful
prepare -> actual selected-plugin tool -> accept calls across 10 query families.
The host serialized both hops as code, without model copying native documents.
Formal project/read/capability/find and project receipt checks passed; A/B context,
fixed snapshot pages, exact UTF-8 document hashes, task detail and accepted/unknown
workflow receipts passed. decision.read has fixture evidence only. A successful
lookup retains mutation_state none and does not claim a write or migration.

This increment adds a provider-boundary validator and distribution members, so
independent scoped review was selected under source policy rule 6.
`create_task_audit`, using the registered fixed-head-independent-auditor role and
`independent-review -> gpt-6.1-sol / medium`, reviewed clean implementation commit
`bd8d219337b3250c3228f023cb87e9c9b4ca8814` against
`8c5c879251cd52f3c77268615af7c724ae60945a`. Runtime source/projection hashes matched;
there was no model pin, and actual serving identity remains unknown. The reviewer
inspected the eight source/test/manifest files, accepted section 11 criteria and
recorded evidence, without tests, provider calls or edits. It reported no supported
actionable findings and an advisory accept disposition. Parent author inspection
and the independent review remain separate evidence.

A possible document character/byte-limit mismatch was investigated and dismissed:
Board's `src/Core/Workflows/Domain/collaboration-workflow.mjs:100` separately enforces
256000 UTF-8 bytes, matching the adapter. The bounded expansion used graph/source
readback at Board commit `b100c9f9bd09b2a1c125c8b511f06defeb29c556`; parent Git readback
confirmed that exact head and clean tree. The reviewer's earlier denied Board Git
probe is not a pass. Framework graph coverage predated the new modules, so they
were reviewed through an explicit tracked-file fallback.

All three workflow tasks are terminal. This completes only the bounded design,
SQLite create-task and Board query increments. The closeout changes records and
navigation; source/test/manifest and governing-policy equivalence with the reviewed
head is checked directly. Hosted PR gate, installation, cross-session adoption,
formal workflow migration, writes/fanout and complete recovery remain unexecuted.

The following Board development snapshot is historical evidence from the first
increment, superseded for availability by the continuation above:

Board #22 is assigned to the explicitly requested chat
`01a171b0-1260-7990-a8fe-23cd6614efb0` (local host), titled
"實作 Board 多專案 workflow 隔離與選擇". It owns Board changes only. Baseline main
`ea161dcbbe045eb9b22468348da94fcae4bba567` was clean; private Site version 14 and
live collaboration/1 capabilities were read. The chat remains active and reports
A/B same-ID isolation, old-row migration comparison and CLI/MCP continuation tests
passing; packaging and browser checks are still in progress. These are that chat's
development observations, not live deployment or feature-completion acceptance.
Read its current status through wait_threads.
The former multi-project gap is superseded by the V2 availability proof above.
Board #6 recovery limits still prevent declaring full migration readiness.

Read this record, the design, live Issues and current working tree first. Keep
the parent's draft separate from accepted product policy. The next source increment
is the remaining #481 task editing/transition contract and #445 native command
adapter; the project-aware query path now exists. Before fanout #520, resolve the
command authority and replication contract in design section 5. Preserve the owner's
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

## 2026-10-25 Board command, copies and synchronization continuation

The owner explicitly requested continuation of #416: implement the Board write
adapter, validate and independently review it, then advance multi-carrier sync and
formal migration. The owner also explicitly requested historical repository
workflow copies on Board using low-cost sub-agents. This authorizes additive
copy writes and selected synthetic command verification; it does not require
clearing online data or inventing historical execution. Push/PR/merge/publication
remain separate. Prior tasks remain completed; BOARD-V2-COMMAND is the unique
current task, followed by HISTORY-COPY, MULTI-CARRIER and SOURCE-MIGRATION.

Input Framework HEAD is f701105059bfc180dc5c212122e2fed939fdf664, clean; Board HEAD
b100c9f9bd09b2a1c125c8b511f06defeb29c556 was read back clean. The selected plugin
still advertises 18 workflow commands under the formal project. The scoped
Framework tools graph was reindexed as framework-records-f7011050 (200 nodes,
1272 edges); an insufficient symbol search uses explicit source fallback.

Low-cost inventory selected the registered bounded-routine-worker with
inventory -> gpt-6-luna/medium, source/runtime hash matched, no pin; actual serving
identity unknown. At the fixed source it found 1931 Git blobs, 19427197 bytes,
219 first-segment workflow units, 199 root locators and 20 legacy units without
root locators, plus three root-level index/control files. The earlier 654 count
was all parent directories, corrected before use as workflow count. Located
statuses are 186 completed and 13 in_progress; status is preserved as historical
source data. Seven files exceed 262144 bytes, including three binary ZIPs; no symlinks.
Legacy missing fields do not retroactively invalidate their historical records.

Historical copies must preserve exact Git-blob bytes, original paths/IDs/status,
source commit and hashes, including unknown fields and binary bytes. A Board draft
archive container is not an imported completed workflow. Do not replay historical
claim/complete actions to manufacture lifecycle equivalence. Source Git records
remain intact. True lifecycle migration needs a supported import/mapping and
recovery boundary; Board #6 remains an external dependency.

D03/D05 owner response selected SQLite for unified daily reads/writes and Board
as synchronized replica. The earlier Board-only read proposal is superseded.
The proposed persistent directory remains
C:\Users\h4227\AppData\Local\AI-Collaboration\ai-collaboration-framework\; no directory,
database or active binding has been created. Design section 13 records the current
decision and the separately selected project-scoped historical importer (Board #24).

Validation plan: native request schema and strict integer/UTF-8 parsing; explicit
capabilities and binding; direct command receipt correlation; same-ID same-payload
replay, altered payload conflict, stale revision durable rejection, lost-response
lookup/replay, exact document content, scoped target refusal and malformed MCP.
Run focused tests plus package closure, then actual selected-plugin calls on an
explicit synthetic workflow, commit and independent immutable-diff review before
bulk copies. Keep fixture, actual plugin, cross-session and adoption results distinct.

### Command adapter implementation and actual host evidence

The registered bounded-general-worker used implementation -> gpt-6.1-sol/medium,
with source/runtime hash matched and no model pin; actual serving identity is
unknown. Parent inspected the implementation, package closure and actual host
results. The change adds nine source/test/metadata files or modifications; the
existing query and local/Git runtime are unchanged.

Focused evidence covers 25 distinct methods: 24 command methods plus the existing
optional-package closure method. Initial command/closure run passed 21 methods in
3.105 seconds; the additional decision/claim effect method passed in 0.053 seconds.
The observed host-format repair then passed nine new/affected methods in 2.416
seconds, including three new regressions and isolated CLI closure. Disposable
fixtures used only verified F:\tmp\aicf-416-board-command with process-local
`tempfile.tempdir`; global TEMP/TMP were unchanged. Suite selection used
`tools.test_workflow_board_command` and
`framework_next.test_distribution_contracts.Metadata5DistributionTests.test_workflow_records_is_optional_and_manifest_matches_metadata`
through `python -I -B -` and unittest's loader from explicit tests paths.

Retained initial failures: date-time validation lacked jsonschema's optional format
extra, corrected with a standard-library Gregorian checker; package metadata first
duplicated a member and then declared an artifact schema under null configuration,
corrected by declaring the frozen schema as tool support. An initial drive guard
expected a Ram driver type; actual readback showed a ready Fixed-type RAMDRIVE.
Later real MCP calls exposed a host-only `INVALID_ARGUMENT` annotation and
`isError: true` on durable rejected receipts. A narrow normalization/correlation
repair passed the affected tests and re-accepted the saved real responses without
repeating their mutations. Original failed adapter outputs remain retained.

The durable [live evidence directory](board-command-live/summary.json) preserves
complete prepared requests written before dispatch, actual selected-plugin replies
and adapter results. Fifteen actual command calls exercise ten families: twelve
accepted replies (including two exact replays), two durable rejections and one
native payload conflict. Eight other supported families retain fixture coverage.
Four queries after capability readback cover accepted operation lookup, exact
Unicode document/hash, final workflow context at revision 10, and rejected
operation lookup. The query bridge also validates the latter three responses.

Response loss was explicitly simulated with null after a real document acceptance;
lookup observed accepted but kept unknown/requires-original-replay until the same
request was resent. A retained prior fingerprint/digest pair later established the
known rejected receipt. One plan attempt reused a supporting document ID and was
durably rejected with document_role_conflict; a distinct plan ID and new operation
then succeeded. The stale expected-revision case was durably rejected. Exact
UTF-8 content including Traditional Chinese and emoji matched its SHA-256. The
synthetic workflow is completed, one task completed and one cancelled; these are
validation records, not historical migration or source adoption.

Independent review is next on an immutable clean commit. No push, PR, hosted gate,
installation, SQLite synchronization, production source-replica deployment or
actual historical copy is established by this command increment. Board importer
commit 89f6dd35b3484822ca035baac50d2dcd67007b82 had two independent P2 findings
(HTTP profile binding and CLI result identity); repair and affected review are
being performed in the separate Board checkout.

### Command review and SQLite synchronization handoff

The independent fixed-head auditor reviewed clean
5c0abfe7ea064fdaadab8e64b8b00d9656705bbf against f701105059bfc180dc5c212122e2fed939fdf664
under code-reviewer/review and the project fixed-head role, selected Sol/medium
(actual serving identity unknown). It returned no supported actionable findings.
Current loader evidence resolved the shared query helper: tool support members
are combined into one complete skill package, so a single declaration supplies
both CLIs. Review was read-only and did not rerun tests or provider calls.

Board independent review of 89f6dd35b3484822ca035baac50d2dcd67007b82 found two P2
issues. The affected review of clean 5bf075abb64b797f039e7484aa96485f814835e2 verified
both repairs and the bounded activation reader, with no new actionable finding.
On 2026-10-25 the owner explicitly authorized Board branch push, PR creation,
merge after CI, deployment to the existing owner-private Site and additive
migration, followed by the already authorized historical copy. The current Site
readback is version 15, access policy revision 1 with owner only. No audience
change is selected. Framework push/PR/merge remain separate from that Board grant;
the owner's later no-ff instruction selects merge method, not unexecuted CI success.

The next implementation uses design section 14: a versioned snapshot and outbox
layer inside the same SQLite database, lossless historical import, native writer
hooks and complete backup/restore closure. The parent selects manual bounded
dispatch with exact retained requests and no pruning. Pending delivery cannot be
created in a second transaction or second database. Permanent path selection is
still pending; implementation/testing do not initialize the production store.

### SQLite snapshot implementation and Board deployment evidence

The source increment adds `workflow-records/source-store/1` and explicitly fresh
`workflow-sqlite/2`. Native create/create-task/checkpoint/write-document preserve
their public request meanings; snapshot capture and fixed-target delivery intents
commit with their state/receipt. Git snapshot import preserves complete raw files
as archive-workflow or archive-root-index, without manufacturing native tasks.
Exact Board begin/chunk/activate requests are retained before dispatch, with
predecessor ordering, original-request recovery and monotonic receipt evidence.
Schema-2 backup/restore includes all source/delivery tables and remains inactive
after restore. Initial bindings cannot be replaced or silently adopted.

The bounded implementation worker used the registered general profile with
implementation -> gpt-6.1-sol/medium; actual serving identity is unavailable.
Forty distinct methods have passing evidence across the selected runs: 26 existing
SQLite v1 methods, 13 new source-store methods and package closure. The final
14-method source/closure run passed in 9.658 seconds; three affected checks then
passed in 2.673 seconds. An extended existing isolated-CLI method additionally
passed in 1.008 seconds after adding exact local module/schema closure checks.
The CLI refuses a missing initializer rather than resolving an ambient package.
Tests include an actually killed local writer, committed-response loss, rollback,
binary/empty/oversized Git blobs, exact raw-byte reconstruction, ordering,
misrouted lookup refusal, delayed unknown evidence and inactive restore/transfer.
These are local fixture/process checks, not physical-device or hosted acceptance.
The runner used `python -I -B -`, explicit `tests` and `tests/framework_next`
module paths, and process-local `tempfile.tempdir=F:\tmp\aicf-416-sync` after a
ready-RAMDRIVE check. Its selected names were
`tools.test_source_store.SourceStoreTests` and
`framework_next.test_distribution_contracts.Metadata5DistributionTests.test_workflow_records_is_optional_and_manifest_matches_metadata`.
The final closure repair selected only
`tools.test_source_store.SourceStoreTests.test_isolated_source_cli_has_declared_source_only_runtime`.

Retained initial failures: the first 36-method run passed all 26 pre-existing
SQLite methods but had three new failures. Schema-2 initialization required its
new administrative event alias only in v2 native-backup validation, and lookup
fixtures omitted the actual outer project/operation fields. Those were corrected.
Parent inspection additionally required known lookup outer identity/outcome
correlation and structured malformed-backup failure. The worker applied them and
returned sole writer ownership before this record update. No broad rerun was
needed after the focused repairs. Disposable tests stayed on verified F: RAMDRIVE;
no production store or credential was created by these tests.

Board #24 is now implemented through
[PR #25](https://github.com/YuChia-Wei/ai-collaboration-workflow-board/pull/25).
The four checks in run 40207589373 passed for reviewed source
5bf075abb64b797f039e7484aa96485f814835e2. The authorized merge commit is
8417d869d07ab52887124222aa4f1e0e37517164, with two parents and tree
4d26f2f646338e7c6d4ed2bd02de1813352e8077. Its equivalent Site source commit
570e77f2371db3b905e26c77ceba3a2d1d2c322b has that same tree. Site version 16
deployment appgdep_6ade22cd28a08191bb86865753995315 succeeded, including the
additive migration. Existing access policy revision 1 remains owner only; no
sharing change or credential rotation was made. Board Issue #24 remains open.
The initial artifact check found CRLF migration bytes differing from canonical
Git LF bytes; packaging was corrected and the artifact check passed before deploy.

Actual post-deployment CLI queries used the existing `workflow-records-private`
Windows Credential Manager profile, without outputting or saving tokens. Source
capabilities and `replica.list` succeeded in project `ai-collaboration-framework`;
the latter returned an empty complete list. The browser likewise displayed that
project and no published copies. New source MCP tools are not exposed in this
session; the existing supported CLI is the selected transport for the copy pilot.
This does not claim source-plugin acceptance or actual historical import.

The user-requested low-cost general worker selected Luna/medium and prepared a
bounded host runner in scratch. Its fixed Git inventory agrees: 220 archive units
(219 workflows plus one root-index), 1931 files and 19427197 raw bytes. The small
pilot is `2026-08-08-v0-10-release-publication`, two files and 4400 bytes. The root
index has three files and 57560 bytes. The first runner inspection found a stale
undefined argument and missing delivery/readback phases; repair is in progress.
No local import or Board copy has been executed. Do not use a plan-only success
as apply-path or delivery evidence.

The exact permanent database path remains an unanswered owner selection. Before
initializing a production store or dispatching copies, resolve that pending choice,
finish immutable source review, and validate the bounded runner against actual
CLI response shapes. Store credentials stay in the existing host credential path;
prepared commands and raw transport evidence must survive RAM-disk loss.

Formal source adoption is still pending. Current daily writer gaps include full
task/workflow status editing. Artifact/Gate policies, Git checkpoint rules,
source policy and commit policy still require Git daily records, and consumers
still resolve Git locators. The bounded read-only policy analysis found no current
portable machine-readable store-discovery resolver; explicit caller-owned
`--config` is supported. A future secret-free binding may use the already ignored
`.dev/ai-context/local/` with explicit navigation, but has not been created.
Retain existing Git records and their historical meanings until supported daily
operations, policy/consumer alignment, real cross-session use and full backup
readback justify a selected cutover. Board #6 recovery remains a separate gap.

This increment deliberately leaves dynamic target changes, read-source switching,
full local status editing and formal migration open. It does not complete #416,
#481, #514 or #520. The owner requires the next Framework integration to preserve
the accumulated commits with a merge commit (`--no-ff` semantics); no squash,
rebase or fast-forward integration is selected. Framework push/PR/merge permission
is still separate from the completed Board delivery grant.

### Independent recovery findings and complete corpus preflight

The fixed-head reviewer inspected clean 4ff9014027df51a360108bf764ed0e8a55495339
against 21d96f4b575ba00a22b620e0eeb66cd10b648b51 and returned two P2 findings:

- R1: native source backup validation checked four sidecars but did not compare
  the complete document/attachment/header projection against retained native
  history. A rehashed but incomplete source snapshot could pass preflight.
- R2: a source-operation receipt containing JSON `[]` reached `.get` without an
  object guard, escaping the public structured-error boundary.

The implementation worker reproduced six incorrectly accepted projection
corruptions and the uncaught AttributeError before repairing them. Capture and
backup now share a pure deterministic native projection; validation requires the
complete header/file list and exact paths, modes, sizes, hashes and raw bytes.
Receipt object/field validation now precedes access. Nine focused methods passed
in 6.590 seconds, including two new independent regression methods; the distinct
method total with passing evidence is now 42. The new cases recalculate inner and
outer hashes, so rejection proves equivalence checking rather than only a stale
hash. Public preflight/restore and the real CLI reject the non-object receipt with
empty stderr and without creating the restore target. V1 default validation was
not changed. Repair re-review is next on a new immutable commit.

Separately, the parent imported the entire selected Git corpus into a synthetic
schema-2 store on verified F: RAMDRIVE. Independent `git ls-tree` and one binary
`git cat-file --batch` read supplied expected paths, modes, sizes and SHA-256;
every imported manifest matched. All 220 archive units, 1931 files and 19427197
bytes imported in 209.024 seconds. No production store or remote dispatch occurred.
The retained tables contain 220 snapshots, 2118 unique raw chunks, 2125 chunk
references, one synthetic binding, 220 intents, 714 exact prepared steps, zero
observations and 221 source-operation receipts.

Complete export produced 63308807 bytes with archive digest
`sha256:ccab5385248ab2c372c465e6c06f9f7a1e7cf8442c95e1ed164b1073d2c4b5bc` and
logical snapshot digest
`sha256:2a83255393a45824c20373dadc91bd811457809b3a2fd2d37947bd601d57d127`.
Preflight and restore succeeded. The first harness then incorrectly compared
`restore.state` with `inactive`; the actual successful receipt has
`state: applied` and `store_state: inactive`. The corrected continuation replayed
that same restore request and received `replayed: true`, compared every source
table byte-for-byte, and confirmed inactive dispatch returns `store_inactive`.
It also revalidated the same full archive with the repaired source validator,
without reimporting the corpus. The repaired module hashes are
source_backup.py `73bb2593ab4332b0a15f284ff4742ed7ed61f64f31d7bdab85c43f1d0bb37d25`
and source_store.py `46648d80a2d4473c123cac242b873fcbacf911687bf2651c32ad5e0047a05072`.
The [bounded preflight script](source-sync-preflight/corpus-preflight.py) retains
the reproducible procedure with the harness assertion corrected. Scratch data
is disposable; this evidence does not select F: as a durable workflow store.
