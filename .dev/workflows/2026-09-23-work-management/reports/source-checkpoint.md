# Local source checkpoint

Report/workflow: 2026-09-23-work-management; owner ai-context-governance. Created/updated 2026-09-23T00:41:35+00:00. Adapted from .ai/assets/skills/ai-context-governance/templates/ai-context-remediation-report-template.md version 2.0.1 under U001. This is source/content inspection, not an independent audit or execution receipt.

## Delivered source

The coordinator's explicit continuation granted two package roots after shared contract 0d0556d4c60105a28eb39cfb06efab9b069728cb. The assigned clean F: branch was fast-forwarded from original checkpoint 446a579d; no rebase/amend changed that handoff. The original design report and source owner's other files are preserved.

- pr@0.1.0: 10 exact members. Public filesystem operations explain,prepare,inspect,query,revise,render; package-owned pr.github operations provider-read,provider-create,provider-update.
- local-backlog@0.1.0: 8 exact members. Public operations explain,create,inspect,query,revise,transition,render.
- Both packages: metadata v2 with one read_schemas identity equal to writable schema; config v2 with isolated selected namespace; empty required/optional skill dependencies; portable instructions, default template, schema and owned scripts.
- PR source binds a selected real immutable Git comparison, validation dispositions, candidate bytes and expected provider state. GitHub operations use existing gh runtime authentication, explicit modes/grant references and actual post-read, without treating declarations as approval/exclusion proof.
- Backlog source preserves local writable authority, stable IDs, selected filesystem/tracking intent, expected digest/state updates, references and truthful lifecycle. Online links are reference-only; historical source backlog stays inactive.

[Exact member/operation inventory](../../../design/framework-next/work-management/integration-proposal.json) is ready for coordinator/#337 mapping. No manifest/profile/shared parser/runtime activation change is included. Local filesystem/parsing primitives were adapted from inspected P2 source into each owner; no package imports Lesson or another skill's private code. pr.github invokes its own package's public JSON tool.

## Actual observations and narrow checks

Live Issue #335 was refreshed read-only at source continuation: OPEN, updatedAt 2026-09-22T18:11:35Z. Assigned Git identity/common dir/status were read before and after the authorized fast-forward. A fresh non-persisted graph at the selected worktree still excluded Lesson scripts; the previously identified tracked source was read narrowly. Graph was navigation only, not a revision/coverage attestation.

Direct source/data inspection parsed all 18 package files as UTF-8, three Python ASTs without imports/pycache, two metadata YAML documents and two record-schema JSON documents. The declared package member lists were compared directly with the 10/8 actual file inventories; 15 local package Markdown links resolved. This is inventory/syntax evidence, not schema validation or a product trial.

Manual source inspection covered request dispatch/closed fields, v2 namespace isolation, metadata/read_schemas binding, record mutation/cleanup, transition and evidence binding, Git child arguments/environment, PR grant/preflight/post-read and failure/uncertainty paths. Static refinements bounded query result accumulation and schema-reference traversal, removed unreachable PR function references from backlog, retained raw newline detection for closing directives, used exact integer provider identities, and prevented nested submodule status work. No executed failure reproduction or measured performance result is claimed.

A final direct YAML parse initially failed with ScannerError at workflow.yaml line 29: completion_scope had been appended to a preceding no-newline EOF value. The missing line break was repaired before rerunning direct parsing. This was a workflow syntax failure, not a product test. After repair, direct parsing/reference inspection completed: 31 UTF-8 files, 3 Python ASTs, 7 JSON documents, 4 YAML documents and 36 local links. Package inventories remain exactly 10/8. A final source-only metadata refinement restricted jsonschema requirements to the operations that consume it; the affected two ASTs/YAML documents were parsed again. Staged git diff --check and the exact planned source commit-message format check passed. No product/schema/behavior execution is implied. No product module, product CLI (including --help), test, schema validator, package/build/install/migration or provider operation was invoked.

## Limits and deferred verification

All behavioral/schema/provider/package/build/install/migration/benchmark/CI/audit verification remains **deferred-by-owner**, authority U001, owner program #322 coordinator / P7. Next action: select proportionate checks against final integrated code and record actual results at P7. Metadata implemented means code exists, not that any such check passed.

Expected-state local/provider checks require cooperating writers; neither filesystem compare/replace nor GitHub pre/post reads provide arbitrary concurrent-writer CAS. GitHub writes can remain unknown after timeout, or committed with failed post-read. No automatic retry/rollback or credentials engine exists. Provider writes are GitHub.com, same-repository, draft create and title/body update only. Root status intentionally ignores nested submodule dirtiness. Unsupported Git config/attributes/version/encoding or filesystem cases fail rather than silently switching execution/storage.

PR content/evidence and grant references are caller-supplied claims whose binding is checked; their truth/authorship is not independently authenticated. Default store-parent provisioning remains constrained as in P2. Package selection/installation and runtime acceptance remain downstream steps.

Model/effort provenance is explicit dispatch-declared gpt-6-astra / ultra; no independent runtime attestation is claimed. No sub-agents, new tasks/worktrees, first push, provider write, credential change, release or memory write occurred. Historical first-checkpoint network/orchestration failures remain in the earlier report; no new product execution took place to overwrite them with a pass.

## Handoff

WM-001 and WM-002 are completed for their bounded local scopes. Workflow completion covers source delivery only; Issue/Project/provider closure remains coordinator-owned. Return containing commit with clean Git read-back, branch/worktree and this inventory to coordinator task 01a0c9d9-3b00-7b70-ad85-daff590e7ecd. Coordinator/#337 maps actual members, then program P7 owns execution verification.

The ignored source message file is .dev/ai-context/local/commit-messages/issue-335-source.txt. Exact command: python -B .ai/scripts/validate-git-commits.py --message-file F:/framework-next/335/.dev/ai-context/local/commit-messages/issue-335-source.txt --workflow-id 2026-09-23-work-management; exit 0. core.hooksPath was unset (query exit 1); default hooks were sample files only. The staged checkpoint contains 27 paths in the four authorized roots.

## CR335-001 source correction

Correction updated: 2026-09-23T00:51:28+00:00. The coordinator identified this gap by source reasoning against immutable source checkpoint 5e632ed50242f13b44bec1884de24c496f5a93ea: the original `--local` read excludes `config.worktree`, while the subsequent Git diff can consume worktree settings when `extensions.worktreeConfig` is enabled. A worktree `diff.orderFile` or include directive could therefore bypass that source preflight. No failure reproduction was executed.

The correction reads both `--local` and `--worktree` through the existing bounded Git helper and applies the same diff/include/promisor rejection to both. Explicit `--no-includes` inspects include/includeIf directives themselves without following them during this preflight. The sanitized environment, process-local pinned options, output/time limits and subsequent diff recipe remain unchanged. [Git configuration documentation](https://git-scm.com/docs/git-config) defines these scopes and the fallback from `--worktree` to `--local` when the extension is disabled. No Git setting is modified.

Only `src/skills/pr/scripts/pr.py`, its operations reference, the owned design contract and this workflow's records change. Package member lists, public operations, the backlog package and shared distribution/profile files remain unchanged. Existing design checkpoint 446a579d03a25edf1b6e64b5e5c13016740025c0 and source checkpoint 5e632ed50242f13b44bec1884de24c496f5a93ea are preserved; this correction is a new commit, not an amendment.

Actual initial correction checks: `python -B -` read the five initially changed files as UTF-8 and parsed one Python AST without importing target code, one JSON document and one YAML document. Direct source/diff inspection and `git diff --check` completed without errors. These results are syntax/content observations only. Final record/message observations follow.

CR335-001 is completed for local source correction. Behavioral reproduction, product CLI invocation (including help), fixtures, tests, schema verification, package/build/install/migration, CI and independent audit remain **deferred-by-owner**, authority U001, owner program #322 coordinator / P7. Next action: coordinator inspects the affected diff; P7 selects and executes actual verification against the integrated subject before final finding resolution. No sub-agent, new task/worktree, settings change, provider mutation or push occurred.

Final direct correction inspection used `python -B -`: 8 UTF-8 files, 1 Python AST without target imports, 1 JSON document, 2 YAML documents and 9 resolved local Markdown links. Parsed next-action values retain their complete Issue 337/P7 instructions. Changed/untracked paths matched the eight authorized correction paths; `git diff --check` exited 0. Exact planned message command: `python -B .ai/scripts/validate-git-commits.py --message-file F:/framework-next/335/.dev/ai-context/local/commit-messages/issue-335-cr335-001.txt --workflow-id 2026-09-23-work-management`; exit 0. The message file is ignored. No behavioral or schema verification is implied.
