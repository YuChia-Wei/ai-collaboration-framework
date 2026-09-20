# Proportionate Terminal Review And Execution Artifacts

## Metadata

- `status`: `draft`
- `created_at`: `2026-09-20T20:00:32+08:00`
- `updated_at`: `2026-09-20T21:17:10+08:00`

- Owner: `ai-context-governance`
- Workflow: `2026-09-20-proportionate-terminal-artifact-tooling`
- Status: implementation complete; lifecycle validation reported passed by owner; immutable independent verification pending
- Template source: `.ai/assets/skills/ai-context-governance/templates/ai-context-remediation-report-template.md`
- Template version: `2.0.1`
- Baseline: conversation-only assessment and Issues #312/#313; no historical assessment was rewritten or invented.
- Source baseline: `93447c6fc1b19bc8fc3fa1df98a24a8bbdf87e41`
- Contract checkpoint: `018091e551f9fb7d30b26c8044b076737a1fe887`

The user directly authorized implementation, focused checks and local commits.
Push, PR, merge, Issue/Project changes, release and publication remain outside
this work. Issues #307/#308 retain their release-reuse and resolver scope;
#309 is deferred and is not a prerequisite.

## Changes And Gate Disposition

| Selected gate | Disposition | Risk and consumer |
| --- | --- | --- |
| Terminal label forces full packet/lease | Simplify | Parent/reviewer classify actual operation risk; authority, custody, external, privileged and unknown-risk review remain full. |
| Immutable content, criteria and authority | Retain/combine | One material review input is validated before dispatch and bound by packet 1.1; prose cannot replace missing criteria. |
| Receipt must occupy the entire review body | Remove | Merge consumer can retain explanatory prose while extracting exactly one valid receipt. |
| Duplicate, malformed or unsupported receipts | Retain | Admission must not choose a convenient receipt from conflicting evidence. |
| Repeat review after SHA-only history changes | Remove | Existing content-addressed reuse remains; current provider bindings still require fresh admission. |
| Preparation, behavior, environment and provider failures share one retry path | Simplify | Repair affected input/checks, preserve failure history and retry limits, and do not relabel formatting repair as behavioral verification. |
| Declaration, admission and reconciliation | Retain | Intent, pre-merge state and actual integrated/provider state are different facts. |
| Actual execution evidence | Retain | Unit and synthetic fixture evidence cannot satisfy an acceptance requiring real deployment, adoption or provider execution. |

Packet and external-task schemas now own their selected structural models.
The shared walker replaces duplicated field inventories in the validators.
Generated templates replace manually synchronized packet/dispatch/completion
representation instructions; they contain placeholders, not successful execution
defaults. `prepare` and `finalize` own canonical seals, byte hashes, references,
receipt writer calls and both dispatch/terminal envelopes. Existing low-level
validators remain the behavioral and custody implementation.

New writes use packet 1.1 and external 1.3. Packet 1.0 and external 1.2 retain
declared historical reading; old receipts are not fresh admission. Explicit
dispatch/completion migration supports 1.2 to 1.3, preserves original bytes and
outcomes, and never creates or migrates a receipt. Lease/retry/ledger migrations
are excluded from this slice.

## Separate Acceptance Checkpoint

These rows identify implementation evidence, not completed independent acceptance.
The final machine-readable ledger must bind the committed implementation and
independent review before workflow completion.

| Acceptance | Implementation evidence | Remaining boundary |
| --- | --- | --- |
| 312-AC1 Compatible/incompatible changes and deterministic generation | Actual selected schema/template change tests, independent input expectations, repeated generation equality | Independent review pending |
| 312-AC2 No handwritten hashes or envelopes | Prepare/finalize tests and real CLI fixture smoke, including dispatch/terminal envelopes | Fixture is not downstream adoption |
| 312-AC3 Actual outcomes, no success defaults | Explicit observation requirements; failed/blocked/timed-out/interrupted preservation tests | Builders do not attest caller honesty or execute the delegated command |
| 312-AC4 Historical semantics and explicit migration | Legacy reader, no fresh downgrade, supported migration, source-byte preservation tests | No receipt migration or guessed semantic input |
| 312-AC5 PR #311 preparation mismatch | Missing criteria rejected before output; canonical review role cannot evade binding through task_kind | Preparation readiness is not review execution |
| 312-AC6 Independent behavioral expectations | Outcome, content/authority drift, paths, cleanup and version tests | No generated-checker-only acceptance |
| 312-AC7 Bounded cost observation | Shared receipt process exercise below | No aggregate timing/token savings |
| 312-AC8 Retired duplication | Field sets removed; templates generated; manual sealing/envelope steps delegated to common CLI | Legacy low-level APIs intentionally retained |
| 313-AC1 Gate disposition | Matrix above | Independent review pending |
| 313-AC2 Pre-dispatch material input | Review preflight and packet byte-binding tests | Formatting repair does not prove behavioral correctness |
| 313-AC3 Content/criteria reuse | Existing tree/SHA tests plus changed criteria byte-binding rejection | No new provider receipt protocol or live merge tested |
| 313-AC4 Truthful outcomes and artifact identity | Existing execution-truth checks and new preservation tests | No release selected or verified by this work |
| 313-AC5 Proportionate examples | Ordinary terminal review remains bounded; authority/custody/external/unknown cases require full | Classification consumes declared operation facts |
| 313-AC6 Bounded before/after | Shared exercise below | Synthetic parser exercise only |
| 313-AC7 Ownership exclusions | Selected diff and explicit #307/#308/#309 exclusions | No release-reuse/resolver implementation claimed |

## Observed Validation

- #313: guardrails 47, terminal closure 61 and language 10 tests passed on the host.
- #312: new artifact tests 18 passed; external-task tests 35 passed; guardrails 47 passed. Subsequent authority changes had 6 affected checks and dispatch-envelope changes had 2 affected checks, all passing, with before/after input hashes retained.
- Portable entrypoints: 7 tests passed. AI-context validation passed for 27 indexes, 16 skills, 2 runtime roots and 477 language-policy files. Bilingual structural parity passed; semantic parity still belongs to review.
- Runtime generation check, generated-template check, guardrail static check, external schema check, shell inventory and workflow validation passed.
- Lifecycle validation was subsequently run directly by the owner, who supplied `Validation lifecycle contract passed.` for the exact command. This is retained as user-reported passing evidence, not an agent-captured process receipt.
- Actual CLI smoke passed in the retained disposable Git fixture at `.dev/ai-context/local/issue-312-313/smoke-runs/20260920T115818Z-e6f85a4dbc/report.json`. A harmless child actually ran; the overall evidence remains synthetic fixture evidence, not independent review/adoption.

Logs and input hashes remain under `.dev/ai-context/local/issue312-validation/`
and `.dev/ai-context/local/issue-312-313/`. No full release, nightly, package or
history matrix was selected.

## Bounded Comparative Exercise

The same synthetic receipt with surrounding explanatory prose was sent to the
baseline parser and current parser in separate validator processes. The baseline
rejected the original, then accepted after one controlled representation edit;
the current parser accepted the original.

| Observed operation | Before | After |
| --- | ---: | ---: |
| Representation corrections modeling a manual edit | 1 | 0 |
| Validator process invocations | 2 | 1 |
| Format-only rejections | 1 | 0 |

Evidence: `.dev/ai-context/local/issue-312-313/receipt-process-exercise.json`.
The common harness and Git lookup processes are excluded. This parser-only
exercise supports neither aggregate time/token savings nor provider admission.

## Preserved Failures And Pending Work

- Initial #313 sandbox fixture ACL failures remain environment failures; later host passes do not erase them.
- Initial #312 external tests had five diagnostic-text assertion failures; updated assertions retained the same behavioral rejection and then passed.
- Shell validation initially found three commands missing from the aggregate runner; declarations were added and inventory then passed.
- One external static invocation omitted `--schema-only`; the corrected preparation command passed.
- Lifecycle attempt one could not load the registry in the sandbox; its generic diagnostic does not prove the operating-system cause. Host attempt two rejected unsorted new gate IDs. The later scenario review removed this order-only restriction while retaining membership checks. Automatic approval review rejected attempt three because it required new trusted user authorization. The owner's subsequent request authorized scenario cleanup, not that retry; no alternate execution is used.
- First CLI fixture smoke failed at Git add because of Windows path length. Only the disposable fixture's `core.longpaths` setting was corrected; the second smoke passed and both attempts remain retained.
- The owner subsequently ran the lifecycle command directly and supplied its passing output. Evidence is retained at `.dev/ai-context/local/issue-312-313/user-lifecycle-result.json`; the record distinguishes observed current input hashes from unrecorded execution-time identity. No agent retry occurred.
- Required next steps: tooling commit, full independent review on a clean immutable subject, final per-Issue ledger and workflow reconciliation. No lifecycle closure is claimed.

## Owner-Requested Scenario And Failure Review

The owner requested removal of narrow, useless and duplicate tests and diagnosis
of repeated validation failures. This pass covers the four #312/#313 functional
test files and their immediate registry, runner and documentation dependencies;
it is not a repository-wide test-suite assessment. Two read-only analyses informed
the changes. They are advisory review, with independence not established, and do
not replace immutable independent acceptance. The parent retained sole tracked
write ownership.

### Scenario Dispositions

| Functional boundary | Before | After | Retained behavior |
| --- | ---: | ---: | --- |
| Artifact schema, authority packaging and templates | 5 | 5 | Exact types, schema compatibility, placeholders and deterministic generation |
| Artifact prepare/finalize/custody/migration | 14 | 14 | Observed Git identity, cleanup, paths, outcome truth, authority drift and version boundaries |
| External schema | 3 | 3 | Schema identity, transport semantics and exact numeric types |
| External runtime transport and custody | 32 | 31 | Parse, argv/path/byte binding, all terminal outcomes and receipts |
| Guardrail classification and review preflight | 11 | 11 | Risk, criteria, authority, immutable subject and permissions |
| Packets, leases, retries, graph and execution evidence | 36 | 35 | Security, retry authorization, evidence truth and fixed-subject checks |
| Terminal parser | 2 | 1 | Malformed, duplicate, conflicting and unsupported receipts rejected |
| Terminal disposition and CLI admission | 31 | 31 | Declaration, authorization, provider requirements and identity |
| Provider projection and review reuse | 28 | 28 | Pagination, current receipt identity and content-based review reuse |
| Total methods in the four selected files | 162 | 159 | No distinct behavioral contract removed |

- Removed guardrail `010ae`, an exact duplicate of `010`; the surviving name
  explicitly identifies legacy retry records without `retry_subject_sha`.
- Removed external `002`, whose fixture assertion and valid-completion check
  add no boundary beyond `003` receipt validation. `002e` still rejects
  self-asserted validator success.
- Removed the standalone terminal prose parser self-comparison, which could pass
  with two `None` results. `050` still exercises surrounding prose through the
  provider projection and checks accepted status, reviewer and subject identity.
- Split external `002c` and terminal `051` into named, independent defect rows;
  a different invalid field or another review can no longer mask a missing guard.
- External `002l` now verifies that rejected CLI combinations do not load records.
  Terminal `025`/`026`/`027`/`032` assert their actual rejection boundary; `032`
  also proves that live verification is not called without the required flag.
- External type/byte-binding tests assert the affected field or binding instead
  of complete diagnostic sentences or a second semantic error after structural
  rejection. Artifact batch validation checks independently selected required
  fields rather than an arbitrary minimum error count. Terminal `038` checks
  the parsed snapshot and exit status, with a name matching those observations.

### Confirmed Causes And Corrections

| Cause | Correction or retained requirement |
| --- | --- |
| Earlier external assertions expected old prose and later-stage errors after the new structural walker rejected input | Test the field/binding and outcome; structural rejection need not run later semantic checks |
| Classification test fixed the registry size at 76 | Compare the actual registry and classification key sets |
| Gate ID authoring order was mandatory despite ID-based lookup | Accept any order; retain nonempty valid IDs, uniqueness across/within groups and exact registry coverage |
| New checks were missing in both earlier executable declarations and the absent-context branch | Existing executable declarations retained; absent-context handling now derives selected source-governance IDs from the registry |
| README documented only `run_check`, omitting `run_command_check` and the full registration route | Document both literal-call contracts and separate registry, shell parity, sensitivity and CLI responsibilities |
| Review input text still described packet 1.0 separately bound inputs | Document current packet 1.1 preparation and legacy reading versus fresh review admission |
| Registry subprocess failures all appeared as unavailable | Distinguish launch errno, timeout and nonzero exit code without exposing raw output or paths |
| Stale workflow index timestamp | Keep projection consistency validation; update locator and index together |
| External static invocation omitted `--schema-only` | Preserve empty-input rejection; correct the invocation, not the validator |
| Smoke fixture Git path length and sandbox fixture access | Retain environment failures and use confirmed fixture-local/host corrections; do not call them product failures |
| Third lifecycle attempt denied before execution | Preserve approval rejection separately from behavioral failures; no retry-rule weakening or execution workaround |

Gate order changes preserve per-gate semantic digests; the full authority byte
digest may still change. This does not grant evidence reuse across changed
authority bytes. Classification authority remains separate from runner selection
because sensitivity and reuse eligibility are distinct decisions.

### Focused Verification And Limits

Logs and input snapshots: `.dev/ai-context/local/issue-312-313/scenario-review/`.

- Guardrails: 46 passed; external delegation: 34 passed; terminal closure: 60
  passed, followed by 4 passing affected CLI cases after assertion strengthening.
- Artifact suite: 18 passed and 1 new assertion failed because the test incorrectly
  required conditional `review_input` for every request. The assertion now uses
  only universally required fields; that one affected case passed on rerun.
  Dedicated review-role tests retain conditional criteria enforcement.
- Three isolated membership/diagnostic tests passed. These mock the registry
  subprocess or registry input and are not execution of the denied lifecycle gate.
- The selected absent-context runner case passed after correcting the test's
  fixture-local log configuration. The first run returned runner exit 0 but the
  new assertion looked in an unconfigured directory; both results are retained.
  The case proves selected checks receive `not-applicable` and do not launch.
- No release/full-package/history matrix, live provider admission, new immutable
  audit or complete workflow acceptance is claimed. The later owner-reported
  lifecycle pass is separate from these focused runs. Method removal is not a measured
  timing or token improvement. Existing failure logs remain intact.
