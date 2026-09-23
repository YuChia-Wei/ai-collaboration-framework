# Local maintenance-design revision handoff for #345

Current deliverable is the coordinator-selected quiescent maintenance v1 revision. Design only; no implementation, product invocation, installation, conversion or activation. Owning skill ai-context-governance; U001/P7 deferral remains. [Design entry](../../../design/framework-next/installation-update/README.md).

## Identity and history

Worktree F:/framework-next/345, branch codex/2026-09-23-installation-update-design, persistent common Git directory C:/Github/YuChia/ai-collaboration-prompts-dotnet-backend/.git. Original base 758a7f51c745ee61625cc089b593367fd1a45533 is unchanged. First design checkpoint 51229b63565ce6e836d57a4b107cf6df5554bf7c stays in history; no rebase. This additive revision follows an explicit coordinator instruction in the same conversation/task.

P5 selected input remains 842b73ca09d701d1561109255193d80439dc996b, read by Git without merge. M01 design selection is not execution. Required/user-declared gpt-6-astra / ultra is not independent runtime attestation. No subagents/new conversations/tasks. Sole existing task INSTALL-DESIGN-001 tracks revision. Exact final HEAD is read back after commit; resolve this report's checkpoint as containing commit, avoiding self-reference.

## Current contract

- Four public package operations: inspect, plan, apply, recover. No ordinary instruction/tool invocation API, mandatory common launcher or shared skill runtime. Adapter need not add a launcher for maintenance.
- Caller explicitly disables affected capabilities and declares sessions/tools/external writers stopped. Engine can verify declaration fields/scope, not truth. Nonparticipating concurrent writers unsupported; hash rechecks do not resolve TOCTOU.
- OS-held lock coordinates participating maintenance writers for their entire operation. File existence is not lock ownership. Markers disclose incomplete/no-owner-activation state; they do not stop arbitrary readers or control already-loaded text.
- External development source checkout plus full commit/required-file raw hashes pins engine; no load from changed core or invented release. Same complete pin is required for recovery. Bootstrap/file closure/backend remain bounded implementation choices.
- Exact owned digest/mode delta, no unchanged rewrites, preserved unknown/project data, complete durable managed before/after set and conditional recovery remain. Package completion is managed-bytes-consistent with project_readiness=not-assessed.
- Full RAM project loss recovers only managed set. Missing source/config/records require project-owned recovery. Managed success is never whole-project ready. Project selects actual public reader(s) and activation decision separately; no installer compatibility plugin/scan/pass inference.
- M01 only for real required closed P2 JSON pair 1->2, with all other values/absence/authority unchanged. Separate assigned owner and durable pair record. Completion proves its conversion invariants only, not general readiness. No unnecessary conversion for defaults/already-v2/null-config skills.

Six design files and four existing workflow files are aligned. No shared source/loader/manifest/profile/adapter/index/root/test/CI changes. Ignored revision message remains within this workflow. F:/ai-context-tests and other worktrees preserved.

## Evidence boundaries

Previous checkpoint retains original source/AST/YAML/Issue observations and initial network/authoring/read-command failures. They remain historical; no new product validation is inferred. This revision starts with matching root/branch/HEAD/common-dir and empty porcelain at 51229b63565ce6e836d57a4b107cf6df5554bf7c.

Actual revision read-back: 10 UTF-8 files, 2 JSON, 1 YAML and 32 local Markdown references, zero syntax/reference errors. Direct API/example fields and targeted content inspection found no remaining abandoned invocation API/compatibility-selection contract. git diff --check reported no errors. Complete planned message .revision-message.tmp was confirmed ignored and passed `python -B .ai/scripts/validate-git-commits.py --message-file F:/framework-next/345/.dev/workflows/2026-09-23-installation-update-design/.revision-message.tmp --workflow-id 2026-09-23-installation-update-design`. Final staged scope/syntax and committed-message byte equality are read back in final response after execution; none is schema/behavior evidence. All product CLI/help, schema validation, tests/fixtures/build/package/install/migration/compatibility/I/O trials, audit/lease/effective-rule/receipt/native handoff tooling and CI remain deferred-by-owner; authority U001; owner program #322 coordinator / P7; next action P7 selects redesigned checks after implementation.

## Successor ownership and remaining choices

I345-A candidate/state/read-only plan. I345-B maintenance writer coordination and external pinned engine bootstrap (no skill invocation changes). I345-C durable apply/recover. I345-D separately needed M01. I345-E coordinator root cutover and project-selected activation checks. P7 selects/runs mechanical cases and CI restoration separately.

Still select exact engine entry/bootstrap/dependency closure, native writer-lock/flush backend, durable paths/failure model, initial profile and project activation checks; assign M01 only upon actual need. Instruction skills need no new execution runtime. Unknown project compatibility remains unresolved outside installer success. #43/#305/#149/#168 are not fulfilled/closed by this design.

Coordinator requested final-only read-back collection. Do not send/retry a cross-task callback or ask user about it. Final response supplies exact HEAD, clean state, changed scope and actual/deferred checks; then stop. No push/PR/merge/provider/settings/credentials/tag/release/publication/downstream actions.
