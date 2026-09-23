# Issue #386 installation scan budget

Status: implementation and focused checks complete; committed-clean public trial pending.
The coordinator owns review, integration, first push, provider state and target retry.
This is not target readiness or full-framework acceptance.

## Binding and scope

- Issue: https://github.com/YuChia-Wei/ai-collaboration-framework/issues/386
- Program #322 / U001; owner confirmation: call_LXr4GzoSMC5N6rgh7xWkXO3c.
- Assigned worktree: F:/framework-next/386.
- Branch: codex/2026-09-23-installation-scan-budget.
- Starting clean HEAD: b746cff2fc803c0c0f1473605ce2f02fbec1eec6.
- Declared independent runtime: OpenAI Codex, gpt-6-astra, ultra.
  This is dispatch provenance, not independent runtime attestation.
- One writer; no subagents or executor-created tasks. Project membership remains coordinator-owned.
- Owning route: local-change-implementer, framework-source. U001 suspends effective-rule
  packet, formal review/lease/ledger, legacy/full/hosted validation. This Issue explicitly
  selects focused tests and one actual complete-candidate trial.

Changed product scope is only IO path lookup and its directly necessary private reader
helpers. Engine/bootstrap/installation call sites, closure membership, package/profile/policy
and public request/result schemas are unchanged.

## Cause and repair

The original IO.locate cleared every cached listing on every path lookup. The Reader
entry counter intentionally accumulates all enumerated rows across one operation.
Creating each object therefore enumerated unchanged parents and growing objects directories
again during parent, absence and exact read-back work.

An isolated unmodified IO.create loop created 131 one-byte objects, performed 655
listings and counted 17,553 entries of the unchanged 20,000 limit. This loop alone passed;
it omits actual plan/preparation overhead and must not be called the original target failure.

The controlled follow-up asks both implementations to read the same existing 131-object
directory 200 times. LegacyIO reinstates the original unconditional clear; the repaired
reader and all counters/limits are otherwise identical. LegacyIO completes 151 reads,
then refuses at 20,001 entries after 304 listing calls. The repaired IO completes 200
reads after two listings / 132 entries. This isolates repeated enumeration as sufficient
to exhaust the budget. The fixed complete-candidate public trial separately tests the
actual selected workload.

Reader listings now compare a fresh direct directory observation (device/inode, type,
attributes, size and modification/change timestamps) before reuse. New listings are
bracketed by equal observations and are cached only after complete bounded alias-free
enumeration. IO invalidates the directly changed parent before mkdir, exclusive file
create, publication move and unlink, even if timestamps do not advance. No entry/byte
counter or limit is raised, reset or bypassed.

Root/ancestry/volume checks and child lstat still run at each IO lookup. Exact case
spelling, duplicate case aliases, link/reparse and hardlink checks, O_EXCL, exact reads,
raw hash checks and refusal ordering remain active. No file bytes are cached by this repair.

This remains the existing quiescent-maintenance contract
([contract](../../design/framework-next/installation-update/contract.md), paragraphs 7–11):
nonparticipating concurrent writers are unsupported; observations are not a filesystem
lease. Metadata revalidation cannot prove absence of malicious concurrent writers that
restore all observed metadata. No new concurrency guarantee or resource contract is adopted.

## Focused evidence

Raw observations are under the explicit durable ignored root:
C:/Github/YuChia/ai-collaboration-prompts-dotnet-backend/.dev/ai-context/local/p7/n386/observations/

- baseline.json: original clean-source 131-object loop, retained 131 files / 131 bytes.
- focused-result.json: first harness attempt, 10 tests, 8 errors. The test driver used
  nonexistent InstallationError.code instead of diagnostic["code"]. Two tests passed.
  This is driver failure, not eight product defects or a passing run.
- focused-continuation.json: one materially changed continuation after correcting the
  driver field access; 10/10 passed, zero skips. All failed fixture roots remain.
- Focused backend flush/move and injected alias/reparse rows are test observations;
  actual hardlink refusal uses a real link. These do not establish native/public acceptance.
- Covered: repeated-listing limit, own invalidation with a held signature, exclusive create,
  case spelling/aliases, changed absence, enumeration drift, ancestor replacement,
  link/reparse cache refusal, hardlink, exact write/read expectation and original limits.

Command (continuation):
python -I -B tests/framework_next/test_installation_scan_budget.py --root F:/framework-next/p7-runs/scan-budget-386/focused-0f205a74/safety-continuation --baseline F:/framework-next/p7-runs/scan-budget-386/focused-0f205a74/before --result C:/Github/YuChia/ai-collaboration-prompts-dotnet-backend/.dev/ai-context/local/p7/n386/observations/focused-continuation.json

## One actual public trial

After committing all source/driver/records clean, execute:
python -I -B .dev/workflows/2026-09-23-installation-scan-budget/public-trial.py

The driver uses the fixed read-only candidate:
F:/framework-next/p7-runs/versioned-candidate/complete-ae3645163ae84569a1ccbacdb8fb4ad5/candidate-3755b217421a-880decbc11734dae8fbc24939280fcbb

Identity:
versioned:0.19.0-rc.1:3755b217421a4f1238f740a09de7e034ccf56038:691ef5f2202c02772e0af76c3789e0af829501d8dea5bc24837763fe1caf8a28

It creates one exclusive tiny project below F:/framework-next/p7-runs/scan-budget-386,
uses fresh raw hashes for all ten EnginePin members and the exact clean source commit,
and invokes the real isolated public entry once for plan and once for apply.
Durable recovery/observations use only C: .dev/ai-context/local/p7/n386/{recovery,observations}.
The driver verifies those roots ignored/untracked before public execution.

Caps are eight trial launches including the driver, five read-only Git helpers and two
public children; one simultaneous directly owned child; two operation roots; 700
retained files and 16 MiB logical output. Retained accounting also includes the earlier
focused fixtures and observations. Nested/transient product process counts are unavailable.
No performance claim. No candidate rebuild, real target mutation, interruption injection
or alternate root. Stop on public failure and retain outputs.

Success requires all 131 raw managed members, exact lock bytes against the durable object
and public hash, both markers absent, protected/unknown sentinels exact, unchanged candidate
and engine bytes, and clean source. Project readiness remains not-assessed.

## Original target failure retained

Read-only source evidence:
C:/Github/YuChia/dotnet-mq-arch-lab/.dev/ai-context/local/rc1-pilot/pilot-9ceb050fed8f/observations/
(plan-request.json, plan.stdout.json, apply-request.json, apply.stdout.json, apply-execution.json)

Retained target summary:
C:/Github/YuChia/dotnet-mq-arch-lab-rc1-pilot/.dev/workflows/2026-09-23-framework-rc1-pilot/evidence/installation-first-failure.json

The summary reports blocked/scan-limit, no managed members/lock/marker, all 19 protected
inputs exact, and 102 durable objects / 1,152,958 bytes. This task does not mutate any
of those paths. The prior failure is retained, not relabeled by later success.

## Static checks and events

- Assigned root/branch/clean starting HEAD and live Issue #386 OPEN verified.
- Code graph indexed at the starting HEAD without persisted repo artifact. A first
  overly restrictive file-pattern query had no matches; the unfiltered symbol query
  found _capture/listing, confirmed against tracked source. Absence was not treated as proof.
- Initial sandbox provider read failed due unavailable proxy; scoped read succeeded.
- Initial candidate metadata read was filesystem-blocked; scoped read succeeded.
- Direct AST/UTF-8 readability and git diff --check performed; final exact-message
  validation precedes each local commit.
- Initial staged diff check refused trailing blank lines in newly written files; normalized final newlines before commit. No behavioral source changed.
- A guessed task-template filename was absent; tracked inventory located
  development-workflow-task-template.json. No replacement policy was invented.

## Remaining ownership

Coordinator 01a0ce78-db26-74e1-a615-2bd0599f7d0c receives exact local clean HEAD, actual
public evidence and changed scope, independently reviews/integrates and decides target retry.
First push, PR/merge, Issue/Project state and target execution remain separate.

Unselected legacy/full/formal/hosted gates: deferred-by-owner, U001, program #322
coordinator / P7. Next action: select/restored gates only under recorded P7 owner adoption.
No CI restoration, release/tag/publication or credential action occurs here.
