# Framework Redesign Execution Override

Prospective applicability (dormant): the [source development policy](SOURCE-DEVELOPMENT-POLICY.md)
and its root/template pointers may be written under the owner's #369 approval.
That approval does not adopt the rules, narrow U001 or restore CI. A later recorded
owner decision must name the effective scope/date, evidence and remaining deferrals.

## Authority And Applicability

This temporary **source-repository-only** rule implements the owner's U001 in
[execution-plan.md](../assessments/ASM-20260923-00-6oq/execution-plan.md) for
[program #322](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/322).
It is delivered by [Issue #324](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/324).
Read it before applying conflicting legacy validation, review or handoff gates
to a work item explicitly assigned to #322 by the
[coordinator workflow](../workflows/2026-09-23-framework-redesign-control/workflow.yaml).
U001 and later explicit owner decisions remain the authority; this document
makes that bounded exception discoverable without conversation history.

The exception applies to this source repository's authorized redesign through
the P7 restoration decision. It does not apply to unrelated work, released
framework semantics, target-owned rules, downstream adoption or product/runtime
security controls. Do not copy it into portable contracts, package contents,
initialization templates or downstream wrappers. A root entry link does not
make this policy portable.

## Execution And Ownership

- Keep the owning skill, online Issue binding, dedicated branch, issue-owned
  workflow/task artifacts, smallest coherent scope and truthful evidence.
- Each implementation Issue uses one independent conversation explicitly
  selected as `model=gpt-6-astra`, `reasoning_effort=ultra`. Do not silently use a
  default or substitute another model/effort. Record declared provenance
  honestly; a dispatch requirement is not independent runtime attestation.
- No sub-agents, nested agents or executor-created tasks/conversations. The
  coordinator owns task creation, dependencies, shared files and integration.
  Return substantive cross-contract decisions to that coordinator.
- Use only the assigned `F:/framework-next/<issue-or-bounded-task>/` worktree and
  branch, with an explicit working directory for each repository command and
  absolute edit paths. One writer per worktree. A saved-project bootstrap does
  not authorize edits in the main checkout or creation of another worktree.
- Preserve `F:/ai-context-tests`, other worktrees and uncommitted work. Request
  the normal scoped sandbox permission when needed; do not silently move work
  to another drive. RAM-disk contents are volatile: commit coherent checkpoints
  into the existing persistent Git object database and refs.
- Keep security, privacy, credential, external-write, publication and ownership
  boundaries. This override grants no new credential use or settings changes,
  destructive cleanup, release, tag, publication or downstream adoption.

## Verification During The Transition

| Work | Required treatment under U001 |
| --- | --- |
| UTF-8/file readability, direct syntax or JSON/YAML parsing, changed-link checks and inspection of actual content | Perform the narrow checks needed by the change; record actual commands and outcomes. |
| Git root/branch/HEAD/status, changed-path scope, diff inspection and `git diff --check` | Preserve local identity, scope and reviewable changes. |
| Existing commit-message format check | Validate the complete planned message with `.ai/scripts/validate-git-commits.py --message-file <ignored-message-file> --workflow-id <workflow-id>` before committing those exact bytes. |
| Other legacy framework validators, `check-all`, critical/full gates and test suites | `deferred-by-owner`; do not run or redesign during P0-P6. |
| Package, upgrade, compatibility, migration, benchmark and high-I/O trials | `deferred-by-owner`; do not run to admit development checkpoints. |
| Validation-only independent audits, audit/receipt packets, review-subject validation, snapshot leases, effective-rule validation packets, acceptance-ledger tooling and native handoff validation | `deferred-by-owner`; do not manufacture tooling records merely to satisfy suspended gates. Preserve meaningful authority, findings and resumable evidence in bounded records. |
| Hosted required contexts and legacy admission-validation machinery | `deferred-by-owner`; absence of checks is never a CI pass. |

The commit-message exception does not enable history matrices or a full
validation runner. Direct parsing is syntax evidence, not schema compliance,
behavioral coverage or independent review. No test or framework validation is
implied by document readability, a clean diff, a local commit or PR integration.
Retain failures and environment limitations beside later successful checks.
Use the exact disposition `deferred-by-owner`, with U001, responsible owner
(program #322 coordinator / P7) and next action. Do not relabel deferrals as
`passed`, `not-applicable`, waived success or validated implementation.

Use the owning skill's workflow/task/report templates proportionally. Preserve
stable IDs, timestamps, source links, actual state and next actions; explicitly
note U001 adaptations instead of claiming legacy validator compliance. A local
P0-P6 task may be `completed` when its bounded implementation is complete and
its verification deferral is assigned to P7. Full-framework verification,
assessment-finding resolution, provider integration and Issue closure remain
separate states. Do not create empty audit tasks to simulate those outcomes.

## CI Suspension And Integration

The coordinator already disabled repository Actions and all seven workflows.
The original [CI evidence](../workflows/2026-09-23-framework-redesign-control/evidence/ci-suspension.json)
and [branch-cleanup evidence](../workflows/2026-09-23-framework-redesign-control/evidence/branch-cleanup.json)
remain coordinator-owned historical observations. The
[restoration inventory](../workflows/2026-09-23-redesign-transition/evidence/ci-restoration-inventory.yaml)
retains their source commit/blob identities, observation times, workflow IDs,
paths, settings and P7 review obligations. It is not a fresh provider read-back.
Do not repeat cleanup/disablement, trigger workflows or restore CI in an
implementation Issue. Repository-wide Actions suspension does not extend this
work-item exception to unrelated security or ownership decisions.

Before first push, each executor returns coherent local commits, exact HEAD,
branch/worktree, changed paths, actual/deferred checks, unresolved decisions and
any shared index row to the coordinator. Do not edit coordinator-owned indexes
or records without a handoff. Coordinator task:
`01a0ce78-db26-74e1-a615-2bd0599f7d0c`.
Predecessor: `01a0c9d9-3b00-7b70-ad85-daff590e7ecd`; retained
[handoff](../workflows/2026-09-23-framework-redesign-control/handoffs/coordinator-transfer.md).

The coordinator arranges commit organization and the authorized remote branch
-> GitHub PR -> online merge sequence. Preserve referenced analysis checkpoints,
shared commits and explicit handoff identities; unshared implementation commits
may be organized under U001. Review scope, actual content, Git identity and
necessary file read-back before integration. The PR must identify U001, the
work-item disposition, limited checks and deferred verification. Read back the
remote SHA after push and the merged PR/main plus Issue/Project state after
merge; do not infer one state from another. No direct main push or local merge
substitutes for this program's online PR integration.

## P7 Restoration Review And Exit

CI stays disabled until the separately assigned P7 work and owner adoption.
P7 must:

1. Re-read live provider state and compare it with the retained before/after
   inventory. Review all seven workflow IDs/paths and their current successors,
   `.github/workflows`, source GitHub gate policies, Actions permissions,
   required contexts, branch protection and rulesets as one consistent set.
2. Record a reasoned disposition for every old pipeline and gate: retain with
   the new contract, replace with an identified successor, or retire. Select
   checks for implemented new contracts, focused tests/tiny fixtures and only
   necessary I/O paths. Do not restore all seven legacy workflows by default.
3. Run only the P7-selected redesigned checks/trials and record real outcomes,
   limits and remaining deferrals. Reconcile the deferred F-06 work and any
   retained acceptance criteria; no synthetic evidence replaces required actual
   execution. #324 supplies the inventory, not this redesign or its pass result.
4. Present the exact proposed workflow/context/settings set and observations
   for owner adoption. Preserve secrets, tokens, credentials, permission scopes
   and unrelated protections. New credential or protection changes require
   their own authority; restoration does not authorize a release or publication.
5. Restore only the adopted subset under that authority, capture live read-back
   and observe the selected execution results. Record failures and remaining
   disabled/deferred items; a settings change is not evidence that CI passed.
6. Record the owner-approved effective replacement rules and scope/date of this
   override's retirement or narrowed remainder. Update both root entries and
   source policy pointers coherently, retaining U001 and historical evidence.

P7 exit requires explicit dispositions, adopted replacement gates, truthful
execution/provider evidence and a recorded policy transition. A date, merged
implementation PR or completion of P0 does not automatically enable CI, expire
the override or claim full verification. If restoration is not adopted or is
blocked, keep CI disabled and record the owner and next action.
