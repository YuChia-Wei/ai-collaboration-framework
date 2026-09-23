# P4 selected workflow contract

Selected for source implementation of [#341](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/341) under #322/U001. This records coordinator decisions, not runtime acceptance or project adoption. The original design at `7f821ee866e7e54e551036785e19dffaa3d7ac39` remains a retained proposal; this addendum resolves its open choices.

## Selected choices

| Choice | Selection and implementation boundary |
| --- | --- |
| C341-01 | Adopt `software-development-orchestrator@0.1.0`, one project-owned aggregate JSON record, the exact ten proposed members and ten public operations. Metadata/config v2; sole `software-development-orchestrator.record@1.0.0` read/write schema. |
| C341-02 | Adopt semantic handoff candidates only, with empty required/optional skill dependencies. Reconcile against the actual P3 source below. No foreign tool invocation, private import, automatic knowledge artifact or rule adoption. |
| C341-03 | Adopt explicit read-only retention previews. Null disables an age threshold. Compact may return a useful summary with originals retained; archive describes required evidence; purge never returns safe-to-delete. No automatic schedule or cleanup writer. |
| C341-04 | Adopt truthful completed-with-deferrals when all documented terminal conditions hold. A deferred item requires owner, reason, trigger, next action and attributed authority reference. Recorded completion is not verification, provider completion or approval. |
| C341-05 | Retain closed metadata-v2 store/template defaults. The owned executable is the single operational authority for retention/resume defaults; configuration documentation describes the same values. Explain exposes effective values and their sources. No shared metadata/loader extension in #341. |

The [contract](workflow-orchestration/contract.md), [record shapes](workflow-orchestration/record-shapes.md) and [interface inventory](workflow-orchestration/interface-proposal.json) define the selected surface except where clarified here. The package must carry its complete own contract; installed use must not require these source design files or U001.

## Actual P3 public handoffs

Use integrated subject `ac4175948045590d1a1942022435ab438ad30ac3`: knowledge source `552e218d039245482ed422be7d4fb642d5463ff0`, corrected work-management source `5409641f19244bc44467af7fba3fc496d7f5195c`, and final mappings `b38ef4a8dce57c2cb78fda6ae9c100d689605245`. PR #343 is merged; #334/#337 are CLOSED/Done. This is source/provider evidence, not executed tool acceptance.

| Destination | Actual source boundary to preserve in candidate instructions |
| --- | --- |
| `lesson@0.2.0 / create` | Public create requires content, text and a caller decision bound to the actual related-query digest; optional statuses/extensions. Content includes title, observation, evidence, conclusion, applies_when, does_not_apply_when, confidence and follow_up. A new record is a candidate; acceptance is separate. |
| `adr@0.1.0 / create` | Same actual query/decision binding. Content includes context, decision_drivers, at least two distinct options with consequences, evidence and applicability. Create yields a draft; decide requires separately configured actual decision evidence and selection of an existing option. |
| `standards-promotion@0.1.0 / propose` | Same query/decision binding plus title, target_id, expected_target_sha256, complete replacement text, rationale, applicability, conflicts and exact source descriptors/digests. Configured target/read roots and actual bytes must exist. No apply operation; proposal/adoption/content/effect are distinct. |
| `local-backlog@0.1.0 / create` | Own public contract remains authoritative for title, summary and observable acceptance. Workflow link is reference-only; no Issue synchronization or authority to execute follows. |
| `pr@0.1.0 / prepare` | Own tool measures the selected actual Git subject. Title/summary, repository/base/head and real validation dispositions remain required inputs. No GitHub create/update is implied by a workflow candidate. |

Candidate documents are semantic handoffs, not executable requests with invented hashes or missing required inputs. Caller selects the installed package/version, reads its public contract, obtains actual query/subject/configuration evidence and performs an already-authorized operation. Missing capabilities preserve the candidate. Only actual returned references may be recorded as handed-off; that label does not imply acceptance or adoption.

## Clarifications for the owned implementation

1. Keep ordinary workflow use proportionate: minimal authored creation input expands mechanically to one coherent record. No mandatory foreign skill, global registry, multi-file locator, audit packet, fixed phase sequence or `.dev` location.
2. Preserve task/acceptance identities, failed observations, dependency checks, immutable evidence and useful next actions as designed. A reported success remains caller-attributed. Content changes invalidate the current retrospective; terminal transitions normalize next_action consistently with retrospective binding.
3. The default retention/resume values are 30/90/null days and 12000 characters. Documentation mirrors executable defaults rather than becoming a second parser. Unknown selected configuration fields fail; other skill namespaces remain inert. P5 may separately propose metadata evolution, but #341 remains on v2.
4. A terminal record is immutable even if open knowledge candidates remain. Later candidate disposition or follow-up uses a new linked workflow or specialist record. Such a link is not automatically sufficient to release retention protection; an actual cleanup owner must reconcile it. Explain this consequence in composition/retention references.
5. Retention is an on-demand preview, not scheduled compression. Unknown external references remain disclosed. A bounded summary must preserve required meaning or report its limit; it cannot silently erase failure, deferral or decision reversal. This slice does not claim the user's future automatic compaction/provider-archive direction is implemented.
6. Only own selected store/config/template paths may be read or written as documented. No implicit storage probing, Git changes, fixture creation, foreign artifact edits or historical workflow conversion.

## Ownership and continuation

Continue in the same independent Astra Ultra task `01a0cbc8-448d-7270-b27b-295295914afb`, F:/framework-next/341, branch `codex/2026-09-23-workflow-orchestration`. Fast-forward the clean worktree to the coordinator handoff commit containing this decision and the retained design. Do not recreate the task or worktree.

Exclusive writes: `src/skills/software-development-orchestrator/`, `.dev/design/framework-next/workflow-orchestration/`, `.dev/workflows/2026-09-23-workflow-orchestration/`. Update the proposal's pending-source and C341-choice wording with links to this selection, retaining provenance. The coordinator owns this file, shared indexes, metadata loader, manifest/profiles, root activation, first push and online integration. Package mapping follows the actual source return; no speculative mapping now.

Return a coherent local source checkpoint, exact full HEAD, clean status, exact members/operations, source/schema/config compatibility limits, actual checks and remaining P7 work. No sub-agents or executor-created conversations. Preserve F:/ai-context-tests and all other worktrees. Product CLI/help, schema validation, tests, fixtures, build/package/install/migration, audit/lease machinery and CI remain deferred-by-owner under U001, owner program #322 coordinator / P7, next action select redesigned checks after implementation.
