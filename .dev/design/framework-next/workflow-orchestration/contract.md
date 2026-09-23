# Portable workflow orchestration contract checkpoint

Current status: C341-01..05 selected by the coordinator in [p4-selected-contract.md](../p4-selected-contract.md); source implementation is delivered under src/skills/software-development-orchestrator/, with verification deferred-by-owner under U001. Selection subject: 9aa93ff4b9df396d28d0a9ae1bd2dd24715e05c0. The original design checkpoint 7f821ee866e7e54e551036785e19dffaa3d7ac39 is preserved. The text below retains that proposal; current executable/public references are package-owned. P3 knowledge source has been reconciled against the integrated actual public contracts, including query/decision/target/source requirements.

Historical checkpoint status: proposed-for-coordinator-reconciliation for [Issue #341](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/341), P4 of #322. Design only; no product executable, schema acceptance, installation or runtime result is delivered here. Starting subject: `3a82b3654976fb26da7618a4404f49d7868d813a`.

Source authority: [U001](../../../assessments/ASM-20260923-00-6oq/execution-plan.md), [P4 scope](../../../workflows/2026-09-23-framework-redesign-control/reports/p4-orchestration-scope.md), [P1 portable contract](../portable-contracts/contract.md), [source layout](../source-layout/design.md) and the selected [P3 contract](../p3-shared-contract.md). These links explain this source proposal; the eventual package carries complete owned references and never requires these source files.

## 1. One owner and one record

Propose `software-development-orchestrator@0.1.0`, source root `src/skills/software-development-orchestrator/`, configuration namespace `software-development-orchestrator`, metadata_version 2, config_version 2 and tool `software-development-orchestrator.fs`.

The organizational skill owns intent/scope, task dependencies, recorded progress, resume, retrospective and retention previews. Specialists remain directly usable and own their artifacts. Neither workflow presence nor a task status grants implementation, provider, rule-adoption or credential authority. The project/runtime resolves real authorization separately. No mandatory phase sequence, technology, repository, tracker, approval engine, scheduler, global artifact registry or source policy is bundled.

One project-owned JSON file holds the workflow and its tasks. No mandatory locator, per-task files, discovery index, audit receipt or knowledge artifact. Query scans only the selected flat store. Default root `notes/workflows` is replaceable. IDs and references are scoped to the selected store, not globally unique authority.

The [record shapes](record-shapes.md), [interface proposal](interface-proposal.json) and [synthetic examples](examples.json) are the implementable surface. Proposed exact payload is ten members, all owned by this package. No package source is written at this checkpoint. interface-proposal.json is a coordinator inventory, not loadable skill-package metadata; its proposal-only fields must not be copied into the closed metadata envelope.

## 2. Minimum semantic input and lifecycle

Create accepts title, intent, included/excluded scope, nonempty acceptance and a first action with an observable completion condition. It generates a workflow ID and initial task `T001`; the first action becomes the explicit next action. The tool does not invent a decomposition, actor, dependency, success or owner decision. The initial workflow is planned, T001 is pending, evidence/decisions/references are empty and retrospective is null. More tasks are explicit caller input at checkpoint.

| Workflow state | Allowed next | Conditions |
| --- | --- | --- |
| planned | active, cancelled | Reason; active requires a concrete next action and satisfied dependencies for any active task. |
| active | blocked, completed, cancelled | Blocked records blocker/owner/next action. Completed meets the completion rule below. |
| blocked | active, cancelled | Active requires explicit resolution and a concrete next action recorded in content. |
| completed, cancelled | none | Immutable; later work uses a new workflow and an explicit reference. |

Task states are pending, active, blocked, failed, completed, deferred and cancelled. Only completed satisfies a dependency. Deferred/failed/blocked never imply success. IDs persist; removed work becomes cancelled with a reason. Dependency edges are within this workflow, must resolve, cannot target self and must be acyclic. A pending dependency blocks active/completed transitions. A change to completed task meaning or acceptance requires a new task ID; prior completion remains historical evidence. Multiple independent tasks may be active in the record, but one cooperating writer serializes record changes. This is not agent dispatch.

Completion requires every task completed, deferred or cancelled; every completed task has a result summary and evidence IDs; deferred tasks retain reason, responsible owner and follow-up trigger/action; all required acceptance items have explicit dispositions; no open decision or unresolved blocking reference remains. A retrospective (including no-new-knowledge) must bind the latest content. If any acceptance/task is deferred, result says `with-deferrals`, never an overall pass. Required failed/blocked/not-executed acceptance cannot close the workflow; an actual owner can explicitly defer it with attribution and follow-up, preserving the old observation. Cancellation records unfinished work and reason without acceptance claims. Terminal records have no active next action.

Task status and acceptance disposition are caller-attributed records. This tool executes no task, test or approval. Even caller-supplied successful output remains an attributed report, not independently verified evidence. Raw workflow digests prove only the bytes read.

## 3. Public operations

Future executable interface: one strict JSON request via `python <selected-package>/scripts/workflow.py --request <absolute-file-or->`. This is a proposed interface, not an invocation performed here.

Common required fields: operation, project_root and package_root. Optional common fields: project_config, local_config, overrides and write_roots. Unknown fields fail. Mutations additionally require existing user/runtime authority; a request field is not that authority.

| Operation | Additional input | Output / mutation |
| --- | --- | --- |
| explain | none | Effective selected settings/provenance/locks; availability not-probed; no write. |
| create | content: minimal input above; optional namespaced extensions | New record/ID, reference and actual raw digest. Exclusive creation only. |
| inspect | reference: {role, id} | Full supported record, historical labels and raw digest. |
| query | optional literal text, default empty | Filename-sorted ID/title/state/digest rows; per-file diagnostics and explicit partial. |
| checkpoint | reference, expected_sha256, content, reason | Replace the current authored content, enforce task/evidence invariants, append former state to history; workflow state unchanged. |
| transition | reference, expected_sha256, expected_state, target_state, reason | Change workflow state/reason and clear next_action for terminal states; enforce current-content conditions; append history. |
| resume | reference | Complete mandatory continuation view, source revision/digest, blockers, dependencies and exact next action; no execution. |
| retrospect | reference, expected_sha256, retrospective | Persist authored outcome/reflection/candidates against current content; append history; no foreign calls. |
| render | reference | Inert-template Markdown and actual record/template/body hashes, result only. |
| retention-preview | mode: compact/archive/purge; selection: 1-100 unique workflow IDs | Read-only assessment per record with input digests, protections, summary and missing evidence; no cleanup executor. |

Exactly ten public operations. No update of a foreign record, dispatch, delete, archive-write, compact-write, import, migration, provider action or implicit export. Full record/request/result bounds are 4 MiB. Query/retention scans at most 10,000 direct matching filenames. Exceeding a bound is explicit unsupported/partial, never silent successful truncation. The resume_budget_chars setting also bounds each retention summary. Resume mandatory content exceeding its configured budget returns unsupported with diagnostic; inspect can still supply the bounded full record.

Outcome vocabulary: succeeded, invalid-input, unsupported, unavailable, blocked, conflict, failed. Results include operation, outcome, mutation_state (none/committed/unknown), selected reference/digest when available and bounded diagnostics. Read-only preview can succeed while its per-record dispositions are protected/needs-reconciliation. No invocation means not-executed in the surrounding conversation; never a fabricated result. Directory creation and cleanup failures remain separately visible. A failed write with uncertain publication has mutation_state=unknown and requires inspection, not automatic retry.

## 4. Configuration, paths and templates

Apply the selected P3 config-v2 envelope unchanged: project JSON has exact integer config_version=2 and optional skills/constraints; local JSON permits config_version and skills only. Reject duplicate keys, invalid Unicode, non-finite values, bool/float versions and malformed namespace objects. Deeply validate only this namespace. Other object namespaces remain inert; explain lists names only. Selected v1/unknown config is unsupported, preserved without conversion. Explicitly missing selected files are errors; omission uses defaults.

Invocation > local > project > package defaults. Merge store and retention leaves; replace template atomically. Null is invalid except the explicitly nullable retention age thresholds. Selected settings are closed:

| Setting | Default / closed values |
| --- | --- |
| store | {kind: filesystem, root: notes/workflows, tracking: tracked}; tracking is tracked or ignored |
| template | {origin: package, path: templates/workflow.md}; origin package or project |
| retention | {compact_after_days: 30, archive_after_days: 90, purge_after_days: null}; each threshold null (disabled) or exact integer 1..36500 |
| resume_budget_chars | 12000; exact integer 2000..64000 |

Metadata v2 configuration.defaults remains exactly store/template. The current distribution reader closes those keys (src/distribution/package.py:179), so retention/resume defaults above are proposed package-owned operational defaults in references/configuration.md and scripts/workflow.py, not added metadata fields. C341-05 asks the coordinator to adopt this explicit default authority; if complete machine-declared defaults are required instead, a separately owned metadata-version decision is needed before implementation. No shared loader change is included here.

Project constraints permit only nonempty write_roots and locked_fields chosen from store.root, store.tracking, template, retention and resume_budget_chars. Locks bind the project-effective value; caller roots only narrow. Default write permission is the project/default store before local/invocation overrides. Other namespaces cannot grant permission. An external absolute root needs explicit project write roots and caller authority. No upward search, environment interpolation, settings edits, disk discovery or fallback.

Tracking is intent only. Explain/resume say actual Git tracking, backup and cross-person durability are unverified. Tools do not stage, ignore, commit or relocate records. A Git project selecting local config must establish ignored/untracked config before invocation; only that read-only Git check is conditional. A successful local write is not power-loss durability or cross-machine availability.

Freeze accepted config/package/template/path bytes at operation start. Safe canonical paths reject traversal, links/reparse points, drive-relative/device/UNC paths, ambiguous Windows names, volume roots and overlap with installed package/config/template. Only contained permitted missing store parents may be created; a parent outside the bound must be provisioned separately or explicitly allowed. No store move on a setting change.

Templates are inert UTF-8 with single-pass escaped literal tokens: id, title, intent, scope, state, acceptance, tasks, evidence, decisions, references, next_action, retrospective, history, storage_notice. Require all tokens; reject unknown/malformed tokens, expressions/includes and recursive substitution. A view is derived, not an import source. Export requires separate destination authority.

## 5. Filesystem and version limits

One cooperating writer per selected store: token-owned `.workflow-write.lock`, expected raw SHA-256 checked under lock, same-directory temporary file and exclusive create/atomic single-file replacement. Re-read frozen config/record before publication. Preserve exact bytes/time on equal-content no-op. Clean only invocation-owned verified temporary files/lock. Stale locks require separately authorized recovery.

A digest check plus lock is not OS-level compare-and-swap against uncoordinated editors. No multi-file/provider transaction, distributed lock, automatic rollback, network store or power-loss guarantee. Proposed supported write hosts match P3's limited local filesystem set: Windows fixed/RAM NTFS, Linux local ext2/ext3/ext4/xfs/btrfs/tmpfs/ramfs after actual mount inspection. Other cases return unsupported. None is certified by this design.

| Artifact | Producer / reader | Write and compatibility disposition |
| --- | --- | --- |
| metadata v2 | Package author / selected loader | Closed P3 keys; exact identities/resources; reject unsupported version. |
| config v2 | Project owner / own resolver | Read only; no conversion or config edits. |
| software-development-orchestrator.record@1.0.0 | create/checkpoint/transition/retrospect; all record readers | Sole read/write family; unknown versions preserve bytes and report unsupported. |
| template | Package or project / render | Read only, owned token contract. |
| resume/preview/render result | Tool / caller | Derived result only; no persisted registry, receipt or schema role. |
| foreign records/evidence | Specialist/project / their public readers | Opaque references here; no rewriting, fetching or foreign schema acceptance. |

Metadata role has schema and read_schemas=[same exact identity]. Package and schema versions are independent. No released legacy workflow importer or conversion edge exists. History retains former states within the 4 MiB limit; overflow fails before write. Preview cannot silently compact history to make room. A new linked workflow can continue explicitly with necessary evidence retained.

## 6. Retrospective and specialist handoff

Retrospective outcome is no-new-knowledge or candidates. Both need a useful reflection: actual outcome, useful observations, remaining limits and why a candidate is or is not warranted. No-new-knowledge requires an empty candidate array and nonblank rationale. Candidates require at least one specific item, source evidence IDs, intended owner/package/public operation, applicability, missing inputs and exact next action. Retrospective is a workflow artifact only.

Initial dependencies.required=[] and dependencies.optional=[]. The tool never loads/imports/calls another skill. A candidate allows the user/agent to invoke an independently selected specialist through its public contract, with fresh package/config/permission checks. Missing/unavailable capabilities preserve the workflow and candidate; candidates are never marked written without actual returned evidence recorded later.

| Destination | Candidate content and handoff | Truth boundary |
| --- | --- | --- |
| lesson@0.2.0 / create | Observation, conclusion, evidence and applicability; query related work first | #334 selected contract only at this base; actual source must be reconciled. Acceptance is a separate operation. |
| adr@0.1.0 / create | Context, drivers, at least two real options/consequences and decision needing an owner | #334 dependency; writing a draft does not decide it. |
| standards-promotion@0.1.0 / propose | Selected source, target ID, rationale, proposed change and unresolved conflicts | #334 dependency; target/config/digests/authority must be supplied there. No adoption/application. |
| local-backlog@0.1.0 / create | Title, summary, observable acceptance and reference-only workflow link | Actual source references inspected at this base. No Issue sync or authorization to execute. |
| pr@0.1.0 / prepare | Title/summary, explicit repository/base/head selection and actual validation dispositions | Actual source references inspected. PR tool must measure actual Git subject; no provider-create/update handoff by implication. |

These are concrete semantic handoffs, not ready-to-execute foreign JSON when required inputs are missing. Inspect the installed version's contract before execution. Record foreign outcomes/references as new caller-attributed evidence; do not deduce completion from a request. No private imports, forced Lesson/ADR, generated owner approval, automatic standard promotion, retry or provider mutation.

## 7. Retention previews and useful summaries

Retention never runs automatically. Explicit selection and mode produce no file mutation, command script or reusable deletion authorization. Age uses the actual observation time and terminal transition time; malformed/future chronology is blocked. A null threshold disables that mode. Age eligibility alone proves no safe disposal.

For every selected record, preserve a useful summary: identity/store/schema/revision/raw digest; intent/scope/acceptance; task outcomes/dependencies; failed/blocked/deferred observations; unresolved decisions/references; evidence locators/digests and uniqueness; retrospective/candidates; exact next action or terminal reason; tracking/durability uncertainty. History is represented without erasing failure or decision reversals. The bounded summary must explicitly list omitted nonessential history; if mandatory meaning cannot fit, block the proposal rather than silently omit it.

Scan only same-store workflow references in supported direct records. Report actual scanned scope/count, unreadable/unknown records and partial state. Opaque links and external inbound references are unresolved by this scan. Never call a single-store scan proof of global absence, and never follow arbitrary references.

| Protection or missing evidence | Preview consequence |
| --- | --- |
| planned/active/blocked work; pending/active/blocked/failed tasks | Protected from all three modes. |
| Deferred work, open decision/candidate, unresolved or blocking reference | Protected until resolved or an explicit continuation is documented and reconciled; no proof inferred from a link. |
| Irreplaceable evidence or evidence uniqueness unknown | Protected; a hash/URL is not a preserved copy. |
| Referenced same-store target or incomplete reference scan | Protect source removal; no archive/purge readiness; retain diagnostic. |
| Unknown external inbound references | Always reported; source-removing actions need external owner reconciliation. A user assertion cannot become tool-proven absence. |
| Summary lacks required meaning or source version unreadable | Protected; do not summarize unsupported bytes as understood. |
| No durable recovery/copy and destination-reader evidence | Archive/purge needs reconciliation; no automatic storage selection. |

Compact preview proposes a result-only summary alongside retained originals, never replacement of the authoritative record/history. For closed, sufficiently old, fully understood records it may return summary-available-original-retained; this is no cleanup permission. Archive preview describes required exact-byte copy, digest/read-back, reader compatibility, reference/resume continuity and explicit durable destination evidence; no archive backend is implemented. Purge preview inventories what would be lost and required owner/reference/retention/recovery evidence; this slice always returns protected or needs-owner-reconciliation, never safe-to-delete. Retention cannot override evidence protection.

No automatic deletion, history rewriting, tombstone service, external archive implementation or cross-store registry. The future implementation supplies useful bounded previews; actual cleanup remains a separately scoped decision/tool.

## 8. Coordinator choices and resumption

- C341-01: adopt the proposed long-form identity, single aggregate record, ten members and ten operations.
- C341-02: adopt candidate-only specialist composition with empty dependencies; reconcile #334 public fields/operations against actual delivered source before implementation. Changes remain within this same task after an explicit source scope handoff.
- C341-03: adopt preview-only retention, nullable age thresholds, conservative external-reference/evidence protection and no executable compact/archive/purge.
- C341-04: accept completed-with-deferrals as a truthful workflow result when explicit conditions above hold; no global pass or provider completion. If the project needs a stricter terminal policy, select it explicitly without encoding source U001 as product behavior.
- C341-05: retain metadata-v2 store/template-only defaults and adopt skill-owned retention/resume operational defaults as described in section 4; do not silently widen the current closed metadata envelope.

The coordinator owns shared manifest/profile/index updates and first push. [Source workflow](../../../workflows/2026-09-23-workflow-orchestration/workflow-plan.md) stays in progress. #316 remains a separate open legacy bundle-authoring Issue; this work does not meet its acceptance or close it. P5/P7 must decide surviving overlap.

U001 limits actual checks here to direct reads/JSON-YAML syntax/reference/Git inspection, diff whitespace and the exact planned commit-message check. Product CLI/help, schema validation, tests, fixtures, build/package/install/migration, audit/lease machinery and CI remain deferred-by-owner to program #322 coordinator / P7. Design inspection is not runtime acceptance.
