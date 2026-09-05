# Direct Upgrades to v0.16.0

## Workflow Metadata

- `workflow_id`: `2026-09-05-direct-v016-upgrades`
- `workflow_kind`: `ai-context-maintenance`
- `owner_skill`: `ai-context-governance`
- `branch`: `codex/2026-09-05-direct-v016-upgrades`
- `base_branch`: `main`
- `branch_segment`: `1`
- `status`: `completed`
- `current_phase`: `completed`
- `artifact_root`: `.dev/workflows/2026-09-05-direct-v016-upgrades`
- `created_at`: `2026-09-05T18:00:49+08:00`
- `updated_at`: `2026-09-05T20:47:33+08:00`
- `template_source`: `.ai/assets/skills/ai-context-governance/templates/ai-context-maintenance-workflow-plan-template.md`
- `template_version`: `1.2.0`

## Objective And Authorization

Issue [272](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/272) requires actual v0.6.0, v0.9.0 and v0.15.1 direct upgrades to one v0.16.0 archive. The owner authorized continuation on 2026-09-05 after Issues 269 and 280 implementation was integrated. Source-specific semantic cutovers, target-owned reconciliation and recovery are in scope. The owner explicitly retained Issue 280 open in Verification until public v0.16.0 archive acceptance. Publication, tags and target-specific production customization decisions remain separate.

Baseline: clean main and origin/main at `013f39116962611c3dbd2825fecd9efca3ec8e3a`. The dedicated branch was created before material edits. Root owns integration, with a sole tracked-writer lease for each mutation phase. The code graph excludes the relevant script trees; bounded tracked-file discovery is recorded under the ignored Issue 272 validation root.

## Acceptance And Evidence

| ID | Observable acceptance | Required evidence |
| --- | --- | --- |
| UPG006-AC1 | Each origin resolves exactly one direct edge | Canonical matrix and three resolver receipts |
| UPG006-AC2 | Exact public origins upgrade to the same admitted archive | Actual isolated target plan/apply/validation/finalization records |
| UPG006-AC3 | Required semantic cutovers and customized ownership are reconciled | Origin-specific cutover assertions and bounded fixture decisions |
| UPG006-AC4 | Missing or tampered identity, ambiguity, validator disagreement and unresolved customization fail closed | Mutation/provenance boundary comparisons |
| UPG006-AC5 | Interruption resumes or rolls back without mixed provenance | Actual durable transaction execution and restored prestate proof |
| UPG006-AC6 | Retained support remains explicit and consumer entry is clear | Versioned source policy, migration guide and regression gates |
| UPG006-AC7 | Publication readiness preserves exact admitted bytes | Asset admission and independent review; fresh publication receipt remains pending |

Baseline audit UPG006-B1 found that historical edge validation executes portable archive checks but does not establish target upgrade completion. UPG006-B2 requires actual direct target apply, finalization and recovery for every origin. The baseline is retained in `evidence/baseline-audit.json`; it is analysis, not acceptance.

## Tasks And Validation

1. UPG006-contract: version the three-origin support horizon and direct release gate.
2. UPG006-direct-evidence: implement and execute the bounded actual upgrade matrix.
3. UPG006-release-readiness: bind immutable assets, independently verify and evaluate release readiness.

Focused checks precede immutable long-running execution. Long-running validation uses a read-only external agent with an exact command, validated packet and terminal report. Failed attempts remain visible and retries require material state change. Real fixture execution is labeled as isolated target evidence; it is not a production deployment.

## Branch Lifecycle And Resume

Use merge-commit topology for the coupled migration contracts, exact archive admission and retained execution evidence, preserving preparation commits as provenance. The local workflow is completed. Provider delivery and current source-candidate admission are the next external gates. The first actual attempt failed before target execution because source-only release identity tools were included in the payload; that archive was not admitted. Independent runner review found three blocking gaps. Repair 1 addressed them and retained the original findings and failure. Attempt 2 was authorized after focused validation of those material repairs, on a new immutable commit and fresh candidate archive. Later attempts and their outcomes are retained below.

## Bounded Actual Execution Retry 3

Attempt 2 rejected a missing source manifest via FileNotFoundError; the runner expected only ApplyError and stopped before target writes. Its terminal fingerprint is retained in evidence/actual-attempt-2.json. Correction accepts this exact missing-file boundary, preserves target comparison, and redacts escaped host paths in terminal diagnostics. The second independent audit closed R1 and R2; its remaining R3 finding now submits the real exit-17 receipt to the receipt validator before asserting finalization remains blocked. This authorized implementation workflow permits one third immutable actual attempt after these material repairs. The package-selected files did not change, so reuse the exact preparation-package-3 archive with a deterministic selected-input proof rather than rebuild it.

## Bounded Actual Execution Retry 4

Attempt 3 was blocked by the execution sandbox while creating transaction prestate and cleaning its preparation directory. A same-path empty-directory differential probe failed under the default sandbox and passed under require_escalated. The OS attributes were normal; no global setting or permission was changed. The workflow authorizes one fourth isolated matrix attempt with the exact command under require_escalated and the same declared ignored output boundary. Additional harness corrections match the actual failed-receipt rejection, compare transaction evidence as well as target files, and record the runner digest plus restored rollback digest. Required actual release evidence and the candidate CI hook now enforce all three origins. No actual upgrade acceptance is claimed until the matrix passes.

## Owner Decision: Versioned Release Input Projection

Independent audit UPG006-CYCLE-R1 established that hashing all release.yaml bytes
creates a cycle between completed validation and the validated source status.
On 2026-09-05 the owner explicitly chose the versioned package input projection.
The implementation preserves validated as completed acceptance and introduces
package-selected-input/v2 with release-package-input/v1 from v0.16.0. It excludes
only the eight documented top-level source lifecycle and validation fields;
every other field and payload byte remains bound. Full current source and
provider gates still own phase acceptance and publication authority. Historical
proofs remain unchanged. Evidence is retained in evidence/cycle-audit.json.

The actual release gate audit found three missing evidence bindings. Its
correction fixes the runner authority and requires retained command, packet,
decision, output, provenance, customization and recovery artifacts. Original
findings remain in evidence/actual-gate-audit.json. Root integrates these changes
in temporary branch codex/2026-09-05-v016-projection at an isolated worktree while
attempt 4 retains its original immutable checkout. The new selected input
contract requires a fresh preparation archive and actual execution; the prior
archive cannot satisfy this changed subject. No new execution retry is implied
before focused validation, a clean commit and its bounded authorization.

## Bounded Actual Execution Retry 5

Attempt 4 was interrupted by the executor sending Ctrl-C during quiet output.
Five completed cases remain in partial progress; no runner terminal or exact
duration exists. No timeout or pre-interruption hang was established. The
parent observation and its fingerprint are retained in
evidence/actual-attempt-4-interrupted.json; this is not completed acceptance.

The workflow authorizes one fifth immutable matrix on the new projection
archive after focused validation and a clean commit. The runner now emits
case and stage progress. The external executor must not interrupt for quiet
output and must allow up to 120 minutes for all nine cases, based on five
completed cases taking approximately 39 minutes in the prior attempt. Actual
subject drift, permission expansion, an explicit owner stop, or that deadline
must return truthful interruption or timeout evidence. Use require_escalated
only for the previously established local fixture boundary; do not repair or
retry within the executor. Retain the exact package bytes through source-only
repairs by current selected-input admission proof.

The projection correction audit left one P2 requiring failed target receipt
and output hashes, execution identity and protected-state evidence. Those
checks and focused missing/tampered evidence regressions are now implemented.
The original audit remains in evidence/projection-audit.json. The first
projection suite stopped at 47 tests with four fixture dependency failures;
evidence/projection-suites-1.json preserves that failure. Adding the existing
validation_subject.py helper to the synthetic package fixture authorizes one
second immutable run of the same three suites. No production dependency or
acceptance rule is weakened and the prior unexecuted suites remain unexecuted.

## Accepted Actual Execution And Local Readiness

Attempt 5 passed all nine cases on immutable source 5ca4fcfe9d00d556dab21db9a90bd575cc01c25a in 3277.546 seconds. The exact admitted ZIP remains d136b69e4153e7c85f892871fb0d3e6c5d8f88c7fd89d43fdb1b03ca88c5c85d, built at 4d1a5c7d039618f007784679d9968c357347272b. No intermediate package was applied. All target records are retained beneath `.dev/releases/v0.16.0/route-assets/actual/`.

The three standalone edge validators and nine ambiguity/missing/tampered route probes passed in 57.757 seconds. Canonical resolver receipts and the complete retained actual-artifact source gate passed before tracked integration. `evidence/runtime-acceptance-ledger.yaml` preserves the validated runtime ledger as historical evidence; its original ignored references identify the execution locations. The retained source copies and their hashes are projected in `evidence/acceptance-evidence.json` for portable inspection.

The release's route-assets directory retains captured logs in Git and disables text normalization for those logs only. Their raw Windows line endings remain part of the recorded output hashes. The ordinary source text policy is unchanged.

Regression retry 2 passed 179 tests with two platform skips out of 181 total. The skips cover Windows casefold-fixture construction and symlink privilege; neither counts as passed. A raw-log recount corrected the executor's initial package-validation overcount. All earlier failed, blocked and interrupted attempts remain retained. The owner supplied an explicit faster fixture root; the classified release-state suite passed 40 tests there in 1.144 seconds. No speedup comparison or redirection of storage-semantic tests is claimed.

Local direct-upgrade implementation acceptance is established. Independent integration review at `940afee97cc318af15f698b0321011aadc49c7ef` passed with zero blocking findings. At local completion release source status was planned and Issue 272 remained open; and Issue 280 remains open in Verification pending public archive acceptance. No tag, publication or provider terminal mutation is claimed.

## Local Workflow Completion And Provider Handoff

All three workflow-owned tasks are completed. Independent integration review passed at `940afee97cc318af15f698b0321011aadc49c7ef`; its report is retained in `evidence/integration-audit-1.json`. The content subject is `e254c2c1023fa2879dc01efac288e763c45507f0ed74caa7ddbe82330398094e`. Earlier expensive execution is reused only with identical runner, archive and retained evidence bytes. The final metadata commit requires a fresh review-subject binding; it does not claim that the earlier audit ran on a later commit.

AC7 remains deferred at the provider boundary. A PR must declare its Issue disposition and obtain fresh required hosted contexts, review binding and terminal admission. The release was planned at local completion; its current source phase is owned by release.yaml. Candidate validation may accept the final Included Work issue through an exact live open-PR terminal declaration; after merge it requires the Issue to be closed/completed. Evaluate and set validated source state only after the applicable acceptance and live provider prerequisites are satisfied. Issue 280 remains open in Verification until the exact public archive is accepted. User-owned tag creation and publication remain separate decisions.

This completion records local implementation and readiness evaluation. It does not claim push, PR creation, merge, Issue closure, validated source phase, tag creation or publication. No post-merge source evidence-sync commit is required merely to record later provider state.

## PR 286 Source-Candidate Declaration

The earlier owner instruction to create and merge a PR and close the completed issue continues through this delivery. PR 286 carries the final Issue 272 disposition. All actual archive/target acceptance and local independent reviews completed before the source transition from planned to validated. The versioned projection preserves the already accepted archive. Its fresh current-head candidate and provider gates must pass before integration; this source transition alone is not their result. No tag or public release is authorized or claimed. The completed local workflow remains distinct from these external delivery gates.
