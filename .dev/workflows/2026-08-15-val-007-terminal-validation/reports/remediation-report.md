# VAL-007 Terminal Validation Remediation Report

## Template Metadata

- `template_id`: `ai-context-governance-remediation-report`
- `template_version`: `2.0.0`
- `created_at`: `2026-07-10T18:22:49+08:00`
- `updated_at`: `2026-07-13T23:11:56+08:00`

## Report Metadata

- `report_id`: `remediation-report-2026-08-15-val-007-terminal-validation`
- `workflow_id`: `2026-08-15-val-007-terminal-validation`
- `owner_skill`: `ai-context-governance`
- `status`: `in_progress`
- `created_at`: `2026-08-15T13:39:00+08:00`
- `updated_at`: `2026-08-15T19:48:37+08:00`
- `template_source`: `.ai/assets/skills/ai-context-governance/templates/ai-context-remediation-report-template.md`
- `template_version`: `2.0.0`
- `baseline_assessment`: `ASM-20260810-005; ASM-20260813-001`
- `verification_assessment`: `transient independent fixed-head review of 59dae454bcfe55fed9873eac834449583750c4a5`

## Remediation Summary

- Authorized scope: Issue #204 complete process-tree supervision, immutable pre/post snapshot, bounded timeout/cancellation/cleanup, sealed evidence, duplicate-coverage measurement, and nightly readiness without a nightly-full run.
- Completed scope: bounded native immutable-history subprocesses; cross-platform process-tree containment; immutable bootstrap and pre/post admission; authenticated preparation, validator, control, and terminal receipts; exact staged-manifest publication; fail-closed cache/receipt reuse; lower-sensitivity semantic fixtures; and a job-level hard-disabled nightly readiness workflow.
- Validation summary: Windows/WSL supervisor fixtures, bounded evidence groups, named runner batches, workflow/registry contracts, syntax/AST/diff checks, iterative independent current-diff reviews, and an exact clean fixed-head review completed. The fixed-head reviewer found no P0/P1. No release, nightly-full, full matrix, or owner-authorized cumulative external validation was run.
- Closure decision: `local-fix-reviewed-awaiting-exact-head-hosted-gates`

## Finding Resolution Matrix

| Assessment Finding | Before Severity | Status | Changed Files | Validation | Commit | Residual Risk |
| --- | --- | --- | --- | --- | --- | --- |
| `ASM-20260810-005#VALSNAP-001` / `ASM-20260813-001#VALRUN-001` | HIGH | `remediated-locally-awaiting-hosted-gate` | runner, supervisor, evidence helper, registry, focused tests | contained bootstrap; pre/post drift, prepare parity, terminal pair, collision, signal, and supervised repo-relative finalize GWTs | `910944f`, `59dae45`, current correction | exact pushed head must pass hosted finalization; read-only selection/authenticator and atomic shell publication TCBs remain explicit |
| `ASM-20260810-005#VALTIME-001` | HIGH | `resolved-locally` | supervisor and process-tree fixtures | Windows module OK with 8 platform skips; WSL module OK with 3 platform skips; independent protocol re-review | `910944f` | non-Linux POSIX fails closed when complete containment is unavailable |
| `ASM-20260810-005#VALTEST-001` / DS-16 | MEDIUM | `resolved-locally` | immutable-history validator/contract/tests, prerequisite fixture, coverage inventory | focused timeout GWT-020/021/022, adjacent regressions, strict cleanup fixture | `254d0d7` | direct immutable-history refresh has per-command bounds; complete descendant proof belongs to the outer runner supervisor |
| `ASM-20260810-005#VALCOST-001` / nightly cluster | MEDIUM | `resolved-readiness-only` | evidence registry split, semantic workflow contracts, disabled readiness workflow | registry 6/6; workflow 10/10; fixed-head readiness GWT 1/1 | `59dae45` | nightly-full remains disabled and unexecuted pending a separately reviewed tracked activation |

## Changes And Evidence

### Complete Process-Tree Supervision And Immutable Admission

- Changes: the new supervisor uses Windows Job Objects and a Linux dedicated subreaper/helper protocol. It admits exact caller cwd and privacy-safe argv projections, tracks PID start-time identity, contains detached-session descendants, withholds launch on cancellation, proves tree-empty before return, and atomically preserves or writes its raw receipt. The runner captures the initial repository snapshot inside the supervised tree, re-admits selection against that snapshot before any reuse or target launch, and rejects pre/post drift.
- Evidence: deterministic Windows and Linux child/grandchild, detached-writer, unrelated-child, protocol-fault, cancellation, timeout, relative-cwd, PID-reuse, and atomic-replacement GWTs. Independent supervisor re-review ended with no P0/P1.
- Remaining boundary: pre-target-launch Git selection admission is a read-only no-launch/no-pass TCB. The runner does not claim that every retained-artifact mutation is supervisor-owned.

### Authenticated Evidence And Terminal Publication

- Changes: immutable-history preparation, cache preparation, selected validators, post-snapshot, finalize, summarize, workflow-summary, and seal execution are supervised. Evidence authenticates wrapper/raw/log/snapshot identity, exact effective argv, accepted exits, selection comparison, preparation parity, artifacts, reuse source, and invocation outcome. Seal builds a staged manifest, declares the future terminal supervisor pair, and cache reuse remains undiscoverable until the published manifest and terminal pair both validate.
- Changes: before the hard-link commit point, the runner verifies the staged manifest against the actual terminal wrapper/raw/log/snapshot and the shell-intended seal argv. After linking, it compares the published bytes with the authenticated staged digest. A collision preserves the foreign final path; signal cleanup removes only an owned publication.
- Evidence: focused evidence GWT groups, runner GWT-019/020/023/027-038, exact terminal tamper and cache-source cases, plus iterative independent current-diff reviews. The final integrated review found P0=0 and P1=0.
- Remaining boundary: supervision-result authentication is a read-only TCB, and artifact assembly/hard-link publication is an atomic shell TCB. A unique invocation directory assumes no untrusted concurrent writer.

### Bounded Nested Validation And Test-Cost Disposition

- Changes: native immutable-history validators require strict positive per-command timeouts, Git helpers are bounded, timeout stops later validators and receipt publication, and the prerequisite shadow fixture uses strict OS-temporary cleanup. The fast/PR evidence contract selects one semantic routine class; exhaustive evidence coverage is release/nightly-only.
- Evidence: focused nested timeout/cleanup tests passed. `reports/coverage-inventory.md` retains the pre-remediation duplication measurements and the post-remediation selection decisions.
- Test-history disclosure: one interim whole-file evidence command unexpectedly took 121.283 seconds. It was immediately treated as long-running, never rerun, and replaced by bounded groups. A seven-method runner batch passed in 115.683 seconds but must be split before future expansion. Sandbox `WinError 5`, Git Bash signal-pipe access denial, WSL `E_ACCESSDENIED`, and concurrent-worktree immutability-guard attempts remain blocked evidence, not passing results.
- Current seal-order disclosure: the first GWT-036/037 sandbox attempt stopped during OS Temp fixture setup with two `WinError 5` errors in 0.004 seconds and was not counted as test evidence; the exact host rerun passed 2/2. A `py_compile` diagnostic was separately blocked by an existing repo-local `__pycache__` ACL and was not counted; read-only AST parsing is used for the final syntax proof.

### Nightly-Full Readiness

- Changes: `.github/workflows/nightly-full-readiness.yml` declares schedule/manual triggers, `contents: read`, stable single-run concurrency with `cancel-in-progress: false`, the exact aggregate nightly command, and deterministic strict artifact upload.
- Admission: the sole job has job-level `if: ${{ false }}`. Checkout, setup, command execution, and upload are unreachable until a tracked reviewed change alters that gate.
- Evidence: workflow contract 10/10 passed in 0.322 seconds; the fixed-head reviewer independently passed the dedicated readiness GWT and confirmed the hard-disable.

### PR #216 Hosted CI Startup Portability Remediation

- Initial evidence: `Read-only governance contract` run `31878447436` / job `94997476877` and `Ubuntu PR profile gate` run `31878447393` / job `94997476608` both failed before validator launch with `realpath: '': No such file or directory` followed by the repository evidence-boundary rejection. The other three hosted checks passed.
- Root cause: `repo_relative_artifact` declared `input_path=$1` and `normalized_path=$input_path` in one Bash `local` command. Bash expanded both right-hand sides before executing `local`, so Ubuntu retained an empty normalized path. Git Bash masked the defect because its subsequent `cygpath` branch overwrote the value.
- Disposition: commit `7b4be71e00ef09289b2d17b77c00b23ddcbc3c9c` separates declaration and ordered assignment without changing Windows conversion or boundary semantics. Exact GWT-019 passed on Windows in 1.322 seconds and Ubuntu-24.04 in 25.334 seconds; Ubuntu Bash syntax and scoped diff checks passed. Independent read-only review found no P0/P1.
- Required next evidence: one exact-head hosted-check watch after the remediation and closeout-sync commits are pushed. The first failed runs remain retained and are not relabeled.

### PR #216 Hosted CI Finalization Regression

- Hosted evidence: `Read-only governance contract` run `31878944344` / job `94998686109` completed 35 selected executions, and `Ubuntu PR profile gate` run `31878944451` / job `94998686454` completed 41 selected executions. Both then failed closed in supervised finalization with `validation evidence failed closed: cannot read repository snapshot`.
- Root cause: `check-all.sh` correctly passes a repository-relative snapshot ref, while `build_record` treats every relative snapshot as evidence-directory-relative and prefixes the full invocation directory a second time. The retained snapshot and pre/post identity are valid; seal was not launched because finalization failed first.
- Remediation: `build_record` now resolves `arguments.snapshot` immediately through the repository-root artifact boundary while preserving evidence-directory-relative event log/result values. GWT-035 executes the exact repo-relative finalize argv under the process supervisor and authenticates the resulting receipt, log ref, and snapshot identity.
- Focused evidence: the final routine contract class passed 2/2 in 24.484 seconds; final Windows GWT-035/009/019 passed 3/3 in 6.942 seconds; Ubuntu-24.04 GWT-035 passed 1/1 in 1.228 seconds. Independent current-diff review reported P0=0/P1=0 and confirmed that the GWT deterministically fails the old duplicated-prefix behavior without relying on global inventory counts.
- Boundary: the hosted failures remain failed evidence and are not relabeled. No release, nightly-full, full matrix, Issue closure, merge, tag, or publication is authorized by this remediation.

### PR #216 Hosted CI Seal-Order Contract Review

- Hosted evidence: at exact branch head `eff73dfa6db3f6713098ac8b3f4416e792d931ce`, build plus both prerequisite lanes passed. `Read-only governance contract` run `31880798815` / job `95002974622` and `Ubuntu PR profile gate` run `31880798749` / job `95002974208` reached supervised seal and failed closed with `preparation-selection validators do not match evidence order`.
- Artifact read-back: artifacts `9245967617` and `9245973619` each contain exactly 63 unique preparation, event, and evidence validator IDs with identical sets and no duplicates. Preparation selection matches the supervised prepare log in canonical registry order. Events match finalized evidence in not-selected-first plus actual runner-call order. The two domains intentionally differ in order.
- Scenario decision: retain and test preparation-to-prepare-log order, event-to-evidence order, duplicate rejection, exact preparation/evidence ID-set parity, and every per-ID version/fingerprint/reuse check. Reject the cross-domain preparation-to-evidence list-order requirement. Skipping seal would remove necessary integrity coverage; reordering execution evidence would add mutation and obscure execution history solely to satisfy an unsupported assertion.
- Remediation: replaced only the two cross-domain list comparisons with exact set comparisons and changed the diagnostic to validator-set membership. GWT-036 proves the same unique IDs can seal in different valid domain orders. GWT-037 proves same-cardinality set replacement, duplicate preparation IDs, prepare-log reorder with a newly authenticated receipt, and event/evidence reorder remain non-passing and produce no manifest.
- Focused evidence: the Windows exact routine class passed 4/4 in 39.941 seconds under its 60-second registry timeout; Ubuntu-24.04 GWT-036/037 passed 2/2 in 5.421 seconds; adjacent fingerprint-parity GWT-033 passed 1/1 in 4.403 seconds. Independent safety and test-quality reviews found P0=0/P1=0 and confirmed the positive case fails the old implementation for the intended list-equality reason.
- Classification: P1 merge blocker, not P0. Both jobs failed closed, published no terminal manifest, and retained useful diagnosis. The failed runs remain failed evidence and are not relabeled.

## Verification Assessment Reconciliation

- Independent auditors: separate supervisor, evidence, runner-integration, terminal-publication, and fixed-head reviewers examined the changing diff. Their P1 findings covered argv privacy, detached descendants, PID reuse, launch-handshake races, incomplete seal semantics, cache/preparation parity, selection binding, signal windows, publication ownership, and terminal-pair authentication; each was remediated and re-reviewed.
- Confirmed resolved: the final current-diff review reported P0=0/P1=0. The clean fixed-head reviewer verified exact subject `59dae454bcfe55fed9873eac834449583750c4a5`, clean index/worktree, base ancestry, diff integrity, and hard-disabled readiness, and found no P0/P1.
- Recurring findings: none at fixed head.
- New or regressed findings: hosted CI confirmed the snapshot remediation and then exposed an unsupported cross-domain ordering assertion in sealing. The invariant is locally narrowed to exact validator-set parity while retaining both same-domain order contracts; independent review found no P0/P1. Evidence/event duplicate coverage and the shared parser's preparation duplicate label remain non-blocking P2s. Exact governed-workflow job maps remain a separate semantic-maintenance sensitivity assigned to Issue #215.

## Deferred Work

| Finding | Reason | Owner | Next Action |
| --- | --- | --- | --- |
| Issue #215 registry and exact job-map sensitivity | independently scoped improvement PR; #204 removed raw workflow-count and fixture-count coupling but does not redesign all topology contracts | future #215 workflow | assess semantic registry/job ownership without count or source-text surgery |
| cumulative long-running validation | owner sequencing prohibits long/full validation until all planned #200-#208 mutations, focused tests, reviews, and commits complete | cumulative release-readiness workflow | bind exact clean cumulative HEAD and dispatch one low-cost external task with exact callback or one event wait |
| nightly-full activation and execution | readiness is intentionally hard-disabled | later release-readiness owner | make a separate tracked activation change only after cumulative gates pass |

## Closure Evidence

- Required local validations: focused supervisor/snapshot/evidence/cleanup/workflow contracts and independent fixed-head review are complete. Later cumulative external-task validation is deliberately deferred, not passed or waived.
- Commit status: workflow bootstrap `0965a2c`; bounded nested cleanup `254d0d7`; process-tree supervisor `910944f`; integrated evidence, runner, tests, and disabled readiness `59dae454bcfe55fed9873eac834449583750c4a5`; initial closeout `94f7d9e`; Ubuntu hosted-startup portability fix `7b4be71e00ef09289b2d17b77c00b23ddcbc3c9c`. These durable boundaries are intentionally retained; squashing would discard reviewed safety checkpoints without materially reducing the final diff.
- Workflow/task status: all three VAL-007 tasks are completed. PR #216 admitted head `9a7432cd656b84392847c966b5044af7e82161c1` passed all five required hosted checks and integrated as merge commit `c032090a5d07ba5163e6b83735f68dc0ea4545e6`.
- Provider separation: Issue #204 remained open after readiness delivery because its terminal closure was deliberately separated from PR #216. GOV-008 segment 2 now owns that terminal provider reconciliation without reopening VAL-007.
- Final next action: none in VAL-007. Nightly-full activation/execution and cumulative validation remain separate owner-authorized work; no post-merge source repair commit is required for this workflow.
