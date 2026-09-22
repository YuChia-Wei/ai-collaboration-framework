# Issue 319 F-001 repair independent audit

## Executive Summary

Outcome: `failed`. Parent action: `reroute` the bounded workflow-entrypoint finding; F-001 itself is resolved on this subject.

The one-line authority repair is correct. `artifact-catalog-tests` now occurs exactly once in the validation registry and once in the canonical classification authority, inside the existing `input-environment-candidates` group. It inherits `[input, environment]` sensitivity, `candidate-disabled` reuse eligibility, no reusable profiles, and `baseline-runtime-platform/v1`. The sole `pilot-approved` gate remains `multi-hop-upgrade-transaction`.

One medium finding remains in the tracked workflow delta. The workflow locator still points to `workflow-plan.md`, but that entrypoint's latest checkpoint directs the next executor to freeze the original implementation, prepare the first review, and execute another package smoke. The first audit, F-001 repair, repair commit, and no-rerun repair review have superseded those instructions. The task record and remediation report carry the newer state, but the canonical entrypoint does not lead to it as required by workflow policy.

This result is bound to content subject `33719853550928b4314dc852dcb751b3df427db1cf0f4dbba3750e41c4132e03`, head `aa91d68479346f1c931920e4735ce84996b6b9d5`, and tree `51dc70953264b00f2c037d83710c5411155cc7d6`. The validated review-input digests are canonical input `80dc6fd3b26ea927f43fe0e55f073b78e9a6dc6ea5ac949c61dcadf3c720080e`, criteria `6a1802e9668e5d10dc576a40da5de019739903ab1ae6dea14671b64a3b8f0828`, and authority `727cdfa2ecc900cb3663c5537c580ed3bdf51dd3c6194bf78e193f6898683c5e`.

The reviewer executed no behavioral test, package, or provider command. Review-input, packet, and active lease preflights passed; all other activity was read-only inspection. No repair, tracked mutation, provider action, credential use, external mutation, or parent-lease release occurred.

## Scope

Included:

- The delta from failed-audit head `b29f3ae9c079b05ab144ba0eddd10294e452988a` to repaired head `aa91d68479346f1c931920e4735ce84996b6b9d5`.
- The single classification-authority line and the five workflow/progress/report files changed in that delta.
- Original `lifecycle-repair-01`, `lifecycle-repair-02`, `classification-01`, and clean-subject `lifecycle-fixed-01` receipts and logs.
- Exact dependency proof for rebinding unaffected conclusions from the first audit, including the earlier package-smoke result.
- The requested correction to the first review's lifecycle-update prose.

Excluded:

- Any new behavioral test, package smoke, profile matrix, provider operation, repair, final integration acceptance, Issue/Project mutation, release, publication, or downstream adoption.
- Unrelated repository matrices and any universal producer audit.

## Finding

### F-002 — Medium — Canonical workflow entrypoint exposes stale next work

`.dev/workflows/2026-09-22-artifact-lifecycle-completion/workflow.yaml` names `workflow-plan.md` as the workflow entrypoint. `.dev/standards/WORKFLOW-ARTIFACT-POLICY.md:70` requires that entrypoint to lead to current progress, next work, blockers, and deferred items.

The latest checkpoint in `workflow-plan.md:52-54` still says the next actions are to freeze the original implementation, prepare the first independent review packet/lease, execute one package smoke, and then integrate. At this fixed head:

- the original implementation was frozen at `b29f3ae9c079b05ab144ba0eddd10294e452988a`;
- the first independent audit completed with F-001 while its exact package smoke passed 1/1;
- F-001 was repaired and committed at `aa91d68479346f1c931920e4735ce84996b6b9d5`;
- the current task explicitly prohibits another package-smoke execution and instead reuses that result through unchanged command-specific dependencies; and
- `tasks/LIFE-003-verification.json:45-59` correctly records the repair and pending repair audit.

Impact: a receiver following the declared entrypoint can repeat a completed terminal command, miss the retained failed-audit boundary, or bypass the actual repair-review state. This is a durable continuation defect, not a formatting issue.

Required repair: update or append the workflow-plan checkpoint so the entrypoint identifies the failed first audit, preserved passing smoke, F-001 repair commit, inspected current evidence, present blocker, and exact next root-owned action. It should not instruct another package-smoke run. Keep the original sealed reviewer artifacts unchanged.

No other material findings were identified within the four repair-review criteria.

## F-001 Repair Disposition

F-001 is resolved for the repaired content bytes:

- The diff adds only `artifact-catalog-tests` to the existing `input-environment-candidates` gate list. No other `.ai` implementation, schema, registry, test, group policy, or pilot membership changes between the failed and repaired heads.
- The classification now contains one `artifact-catalog-tests` membership, the validation registry contains one registration, and the only `multi-hop-upgrade-transaction` membership remains in the `pilot-approved` group.
- `lifecycle-fixed-01` records the exact repaired head, exit code 0, `input_drift: []`, and the expected `Validation lifecycle contract passed.` output.
- All 751 recorded input hashes in each of `lifecycle-repair-01`, `lifecycle-repair-02`, `classification-01`, and `lifecycle-fixed-01` match the current files; none is missing.
- The relevant authority and implementation remain unchanged apart from the classification line: `validation-profile-registry.sh`, `validation_subject.py`, `validate-validation-lifecycle.py`, `test_validation_subject_digest.py`, the lifecycle contract/schema, and provider policy retain their prior bytes.

The clean fixed-subject pass was executed by root and inspected by this reviewer. It is not relabeled as a reviewer execution.

## Retained Execution Evidence

| Record | Observed result | Independent disposition |
| --- | --- | --- |
| `lifecycle-repair-01` | Root command `python -B .ai/scripts/validate-validation-lifecycle.py`; exit 1. The retained log records fail-closed registry subprocess exit `3221225794`. | `blocked-by-environment`. Preserved as the sandbox Git Bash launch failure; it supplies no behavioral pass. Log hash matches, all 751 input hashes match current bytes, and the receipt records the runner unchanged. |
| `lifecycle-repair-02` | Same root command at the authorized elevated Windows boundary; exit 0; 0.8145946 s; lifecycle contract passed. | `reused-with-proof` for the repaired bytes and successful environment. Head provenance still names b29 because the repair was uncommitted, so it is not exact-head evidence by itself. |
| `classification-01` | Root ran the two `ValidationSubjectClassificationGwtTests`; 2 passed, exit 0; 0.5588472 s overall and 0.230 s test-reported. | `reused-with-proof`. It covers exact registry/classification parity and the change-decision matrix on input bytes identical to the repaired head. |
| `lifecycle-fixed-01` | Root ran the lifecycle validator on head `aa91d68479346f1c931920e4735ce84996b6b9d5`; exit 0; 0.3196565 s; lifecycle contract passed. | `reused-with-proof` as the direct clean-subject observation. It remains root execution, not reviewer execution. |

Each JSON record's `log_sha256` equals the corresponding retained log hash. All four records report `input_drift: []`, `runner_unchanged: true`, and runner SHA-256 `58cea3ac6e27f46dd5a62602103423aebd26db592229b3e15a17c2116e89bb54`.

Evidence limit: no runner file is present in the bounded p34 evidence directories, so this review can verify consistency of the recorded runner hash and the per-run unchanged flag but cannot recompute that runner hash from retained runner bytes. This limit does not convert the failed sandbox attempt into a pass and does not change the exact input/log identity checks above.

## Prior Audit and Package-Smoke Rebinding

The original audit body remains byte-for-byte preserved at SHA-256 `395f4d7e04932e32f965ec19e922cbcb30d1f6e5d3d94ecf0e59839ba1aad945`. Its candidate, receipt, and terminal message remain at their sealed hashes, and the original lease is explicitly released with a reason that preserves the failed audit separately from the passing smoke.

The first audit outcome remains `failed`; its command outcome remains `passed` with 1/1 test and exit code 0. The timing disclosure also remains unchanged: native process event timestamps were unavailable, and the command observation used bounded cleanup-derived wall-clock proxies plus the directly observed elapsed duration.

The earlier package-smoke result is `reused-with-proof`, not re-executed:

- Every path in the registered package-smoke dependency closure is unchanged between b29 and aa91: the packaging scripts/tests, `.ai/distribution`, artifact helpers, lifecycle helper, and lifecycle registry.
- The specific smoke fixture copies the lifecycle registry and named script helpers into a synthetic repository. It does not copy or consume `validation-gate-classification.yaml`.
- The only `.ai` delta is the classification membership line, outside that command-specific closure. The five other changes are workflow/progress/report files outside the smoke fixture.

This proof rebinds the prior package-smoke conclusion to the repaired content subject without pretending the command ran on aa91. It does not supply a blanket whole-subject pass.

## Clarification to the First Review

The first report stated: “Lifecycle changes protect kind, baseline, coverage, model, and owner identity.” That sentence was imprecise.

The verified behavior is:

- `lifecycle.update` permits edits to `models`, `owner`, `authoring`, `producers`, `validators`, `readable`, `writable`, `migration`, `admissible`, `limits`, and `applicability`.
- The protected selectors are `kind`, each record's `baseline_refs`, and the registry-level `coverage` inventory.
- Candidate validation reads and binds the bytes referenced by `models` and `owner`, so drift in those referenced sources invalidates the projection. That dependency binding does not make the `models` or `owner` routing fields immutable.

The original reviewer body is preserved rather than rewritten; this successor report records the correction.

## Report and Workflow Truth

The Traditional Chinese remediation report and `LIFE-003-verification.json` truthfully distinguish:

- the first audit's failed outcome from its passing package-smoke command;
- the sandbox environment failure from the later elevated pass;
- the two classification cases and current clean-subject lifecycle pass from reviewer execution;
- `candidate-disabled` policy from an approved reuse pilot; and
- pending independent repair admission from final integration acceptance.

The report remains draft and correctly excludes remote/provider, release, performance, token, and adoption claims. F-002 is localized to the stale workflow entrypoint checkpoint.

## Criteria Disposition

| Criterion | Disposition | Evidence |
| --- | --- | --- |
| Repair classification | `passed-by-review` | One exact membership in the existing input/environment candidate-disabled group; no reusable profile or pilot expansion; current lifecycle and classification evidence passes. |
| Original evidence inspection | `passed-by-review` | Original logs and receipts retain the sandbox failure, elevated pass, two classification cases, exact log hashes, unchanged runner hash fields, and complete current input identity. Root executions are not relabeled. |
| Unaffected conclusion rebind | `passed-by-review` | Other implementation and relevant authority bytes are unchanged. Package-smoke dependencies are unchanged and the changed classification file is not consumed by its specific fixture. No command was rerun. |
| Clarification and whole-subject truth | `failed` | The lifecycle-update clarification is recorded and the report/task state is truthful, but F-002 leaves the canonical workflow entrypoint stale and capable of directing a prohibited duplicate smoke run. |

## Parent Action

`reroute`: correct F-002 in the workflow entrypoint under the integration owner's tracked-write authority. Preserve the original failed audit, command observations, and this repair-review attempt. Any later content-subject admission must honor the attempt budget and the existing evidence-reuse rules; this reviewer does not authorize a third attempt, integration, or lease release.
