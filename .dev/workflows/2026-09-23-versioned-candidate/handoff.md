# Issue 381 local handoff

Completed the bounded implementation and selected evidence under U001. First push, fixed-source coordinator review/integration, target pilot and release remain separate. No unresolved product ownership decision was discovered.

- Worktree: `F:/framework-next/381`; branch: `codex/2026-09-23-versioned-candidate`.
- Baseline: `031233202f21e0793c9667cac872375d65e52be0`.
- Clean implementation / actual engine commit: `3755b217421a4f1238f740a09de7e034ccf56038`.
- Delivery commit is the containing commit of this report (resolve `git log -1 --format=%H -- .dev/workflows/2026-09-23-versioned-candidate/handoff.md`); it changes own records only after the implementation checkpoint.
- Observed: 2026-09-23T22:39:20+08:00. Primary task declared Astra/ultra; no subagents/tasks/callbacks. Direct user confirmation resolved both historical approval refusals.

## Delivered scope

The [contract](../../design/framework-next/versioned-candidate/contract.md) describes explicit versioned assembly, schema 2, strict distribution labels separate from unchanged component versions, and version/commit/full metadata identity. Development API/CLI and schema 1 remain supported. Candidate, installed lock and retained-object readers share the same selection/identity logic in existing pinned modules. `complete` explicitly selects all 18 actual components with Codex. Existing profiles and component/member bytes are unchanged. No new engine module or bootstrap/loader/apply/recover/native IO/planner changes.

Product/test paths are assembly.py, data.py, installation_state.py, exact manifest profile registration, complete.yaml, the new build-candidate.py CLI and test_versioned_candidates.py, plus the directly affected profile inventory in test_contracts.py. Own documentation/records are the only other edits.

## Actual and fixture evidence

| Selected acceptance | Observation | Evidence |
| --- | --- | --- |
| Strict versions, legacy development, closed selection/identity/refusal, lock and same-schema plan semantics | Six focused tests passed, 0.304 s; 34 retained files / 39,430 bytes. Inputs are tiny synthetic fixtures. | [regressions](evidence/regressions-01.txt) |
| Complete rc.1 public CLI from one clean commit and actual installation reader | Passed; all 18 identities, 113 source payload members, 18 generated runtime entries and exact member bytes equal committed selection. | [CLI argv/stdout/stderr](evidence/complete-cli.json), [actual result](evidence/complete-result.json) |
| Actual-run caps | 269 files / 2,334,138 bytes including receipt, below 512 / 16 MiB. Measured assembly/read after selection preflight 19.642 s. All output retained. | [observations](evidence/observations.json) |
| Future stable update planning | Manual rc lock and fictional stable metadata entered actual pinned public API. Correct request planned with unchanged member delta but pending lock transition; wrong lock/candidate rejected as conflict, wrong engine as blocked. No writes by planner. | [fixture transcript](evidence/fixture-plan-transcript.json) |
| Syntax/readability/reference/scope/diff checks | Passed; unchanged legacy CLI/payloads and unaffected engine definitions inspected. Exact planned implementation message validated before commit. | Workflow plan and observations |

Actual candidate identity:

`versioned:0.19.0-rc.1:3755b217421a4f1238f740a09de7e034ccf56038:691ef5f2202c02772e0af76c3789e0af829501d8dea5bc24837763fe1caf8a28`

Candidate path: `F:\framework-next\p7-runs\versioned-candidate\complete-ae3645163ae84569a1ccbacdb8fb4ad5\candidate-3755b217421a-880decbc11734dae8fbc24939280fcbb`. Full retained run: `F:\framework-next\p7-runs\versioned-candidate\complete-ae3645163ae84569a1ccbacdb8fb4ad5`. The build reports installation, behavioral_validation and publication as not-performed; selected reader verification is recorded separately here. Future stable fixture output is never an actual release or successful target upgrade.

Retained recovery evidence covers the exact shared metadata/lock parsers. Inspection confirms the unchanged recovery reader calls `_candidate_documents` and `_lock_bytes`; no apply/recover or interrupted operation is executed. Existing data, configuration, .NET rules, legacy routes, migration and activation remain target-owned.

## Failures, deferrals and continuation

No selected regression, actual build/read or positive fixture-plan acceptance failed. Negative fixture responses are expected refusal evidence. Two initial automatic approval rejections made no writes; the user directly confirmed this task's exact scope, then ordinary scoped execution succeeded. A later restricted evidence read hit PermissionError and reported an incomplete glob view; discard that partial count. A normally approved read with explicit fail-on-error traversal established the retained totals above. Original runtime run outputs were not edited or rerun.

Unselected legacy/full/history/profile matrices, formal packets/native handoff validators, independent audit and hosted/CI checks remain `deferred-by-owner`, authority #322 U001, owner program #322 coordinator / P7; next action is explicit P7 selection/restoration adoption. No push/PR/provider/Issue/Project mutation, publication/tag/release, downstream install or CI/credential change.

Coordinator next: review the fixed local implementation and evidence, resolve the containing delivery commit, then arrange any already authorized transport/integration. Candidate provenance remains the implementation commit above. Any later maintenance invocation must pin its actual immutable engine checkout/HEAD and raw files afresh; the observed pin is evidence for the tested checkpoint, not permission to reuse an old HEAD pin on a newer checkout. Final record-only commit does not change tested source, profile, payload or test bytes.
