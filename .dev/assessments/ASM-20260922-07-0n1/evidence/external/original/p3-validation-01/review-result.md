# P3 dynamic role metadata independent audit

## Executive Summary

Outcome: `passed`. Parent action: `accept` this bounded audit result for the integration owner's separate decision.

The independent review found no material defect in the 17-file P3 subject. The result is bound to content subject `43d4aadbeee5f2179cb26d53fa22b5dde32b64c4da87909ad84c3dd68ece6ee0`, criteria digest `df26108723bb4c8711027ccf88be3855af0e0fa3a6533a9242c8cef54ac71045`, authority digest `590b3149ebeb44cb69fee3afaaf1d0ca4ea77908afa393a70c1ec5faf3486d67`, canonical review-input digest `8e818cf4725b42da6656081d3723e7c15d3469578a88bb9efa041dea5ad88ae5`, and execution commit `fb1c310b6629eece95d9d0bb51da8ef23a1f1e20` / tree `59be49052a8b20387269a83c65850b669716a063`.

The exact dispatched package-smoke command ran once at the authorized elevated Windows fixture boundary. It completed 1 of 1 test with no failure, error, or skip, exit code 0. No repair, tracked mutation, provider action, credential use, network action, or additional test execution occurred.

This audit does not grant final integration acceptance and does not claim workflow, Issue, Project, release, publication, hosted CI, or downstream-adoption completion. Root remains the sole integration owner.

## Scope

Included:

- The Git diff from base `228bf4576610a4a07b8ca5d13d2b429edd0bf1af` / tree `0b54883a51aecf830b11db2870b8e24e4075aefb` to head `fb1c310b6629eece95d9d0bb51da8ef23a1f1e20` / tree `59be49052a8b20387269a83c65850b669716a063`.
- `role.update` and explicit dynamic-role `role.migrate` behavior, canonical candidate validation, stale-preview binding, recovery custody, validation-profile/package dependency closure, tests, fixtures, and operator documentation.
- The retained focused records under `.dev/ai-context/local/p3-checks/` and the Traditional Chinese remediation report and active workflow records for truthfulness and scope limits.
- Issue 318 AC1 through AC6 as supplied by the validated machine review input.

Excluded:

- Product source and product tests. The selected `.ai/scripts` context-tooling source and tests are within this audit's explicit scope.
- Role creation, promoted runtime-adapter authoring, owner-binding changes, other metadata families, P4 gate removal, remote/provider activity, release, publication, and downstream adoption.
- Any repair, checkout, tracked write, or second behavioral execution.

The refreshed graph excludes `.ai/scripts` and `.ai/assets`; this audit used the explicit Git diff and Git-tracked file reads. No absence conclusion relies on graph search.

## Independent Baseline Pass

The general engineering pass found a narrow family adapter over the existing authoring transaction and recovery machinery:

- Requests resolve an existing canonical role by `asset_id` across the shared and owning-skill-private layouts. They cannot supply an output path, owner binding, status, workflow, schema, wrapper target, or adapter disposition.
- `role.update` allows only the eight catalogued descriptive fields. Unknown top-level and nested owner extensions stay in the candidate mapping; actual YAML comments, duplicate keys, aliases, anchors, explicit tags, unsupported scalar types, and invalid candidate shapes fail before writing.
- `role.migrate` accepts only explicit `1.0 -> 1.1` dynamic roles with empty `wrapper_targets` and absent or empty `adapter_metadata`, then changes only `schema_version` and the empty adapter mapping. Other versions and promoted adapters fail closed.
- Candidate validation consumes the in-memory projected mapping, all canonical skill/role manifests, owner relations, the derived role projection, reference existence, directory membership, the three role authorities, and the validator/runtime files. Apply re-derives the plan; generic journal recovery retains exact prior bytes and refuses external candidate drift or hostile paths.
- The extracted canonical-manifest and role-relationship functions preserve the existing repository validator flow. The two deliberate hardenings enforce canonical `source_of_truth` under `.ai/assets` and reject YAML booleans as workflow-step integers.

Baseline findings: none.

## Repository-Aware Policy Pass

The repository-aware pass confirmed the baseline and policy boundaries:

- The owning `ai-context-auditor` skill explicitly selects the active fixed-head auditor for this authority-sensitive terminal gate. Full packet, external dispatch, active shared-frozen lease, exact review input, and all 14 dispatch-authority hashes matched before execution.
- The review-input copy is byte-identical to the authoritative input at SHA-256 `af418fba9a215c71eed6f1b4ae7876e9e226c1e3460f3b13520ab50614ad3815`; the packet raw SHA-256 is `83d3bb69ab5d7ce49bd8ad7e789be451afbcc7597860e4157b3a5671195adf90`.
- Historical fixture bytes exactly match Git blobs `6de419d67bdcb11807e2db5622af9f729efdf400` and `5076e189c4e80c0ece4f38e856840706164b70ad` at commits `a87bddf98dd3a254e1f84b16625ef53ef644ae53` and `6aed5786033d404fdfe9eaa8961f51a071321b5f`. Their parsed mapping delta contains only `schema_version: 1.0 -> 1.1` and addition of `adapter_metadata: {}`.
- Final-source `role-03`, `adapters-registry-02`, and `canonical-02` records have output hashes that match their retained logs, and their recorded changed-path input hashes match the current clean working bytes. Because those records were captured before the final commit while HEAD still named the base commit, they remain focused source-byte evidence rather than exact-head executions.
- Early `authoring-02`, `canonical-01`, `adapters-01`, and `registry-01` records retain their earlier input identities and outputs. `authoring-02` is supporting evidence only because later canonical hardening changed recorded inputs. The failed adapter and registry assertions remain failed evidence and are not relabeled.
- `role-01-summary.json` is explicitly a parent-observed summary without a complete raw stream. It supports history only and is not treated as independently preserved command output.
- `p3-run.py` records its own SHA-256 after command completion. The early runner file was edited during those early runs only to reduce printed JSON fields; therefore its early `runner_sha256` is not used as a pinned start-time runner identity. The retained command, output bytes, output hash, and input manifest remain the evidence actually claimed. Final role/adapters/canonical records ran after that edit.
- The remediation report correctly describes the family as the first P3 batch, keeps creation/promoted adapters/other families/P4 deferred, leaves independent verification pending at the audited commit, and does not invent hosted, provider, release, or runtime-invocation completion.

Repository-aware findings: none.

## Two-Pass Comparison

| Comparison | Result |
| --- | --- |
| Confirmed | Bounded descriptive updates, one explicit dynamic-role migration edge, protected identity/disposition, extension preservation, candidate validation, stale-preview and recovery behavior, canonical hardening, and package dependency closure. |
| Added by repository policy | Exact content/criteria/authority binding, full lease/dispatch custody, current fixed-head package smoke, historical-failure retention, and integration-owner separation. |
| Downgraded or deferred | The full 35-case authoring run is prior supporting evidence, not whole-suite final-head proof. The parent-only role-01 summary is not raw execution evidence. Other P3 families and P4 remain deferred. |
| Overturned | None. |
| Residual uncertainty | The exact fixed-head behavioral execution covers package smoke only. Focused final-source records support the role/adapter/canonical conclusions by input identity, but this audit does not call those commands exact-head reruns. |

## Criteria Disposition

| Criterion | Disposition | Evidence |
| --- | --- | --- |
| AC1 | `passed` | Static diff plus final-source 12-case role subset confirm bounded editable fields, protected identity/disposition, deterministic preview, projected-candidate validation, and preservation of nested extensions and unrelated files. |
| AC2 | `passed` | Both fixture files are byte-identical to the named historical Git blobs; mapping comparison confirms only the documented two-field transformation. Migration requires explicit versions and retains original bytes in the recovery journal. |
| AC3 | `passed` | Static fail-closed paths and final-source role cases cover unsupported versions, promoted adapters, malformed/duplicate identities, noncanonical authority, boolean steps, missing references, owner/projection mismatch, and stale preview. |
| AC4 | `passed` | Generic recovery remains unchanged; final-source role cases demonstrate exact prior-byte restoration and refusal after external candidate modification. Safe-path, link/reparse, hard-link, and journal-output authority remain inherited from the existing writer. |
| AC5 | `passed` | Canonical and adapter/registry final-source records pass with matching inputs; registry/runtime dependencies include the new validator and router. The exact fixed-head package smoke passed 1/1 and confirmed both helpers are present in the archives. |
| AC6 | `passed-by-review` | Retained output hashes and changed-input identities were checked. The report distinguishes 35 full prior cases from the overlapping final 12-role subset, 42 adapter/registry cases, the final canonical validator, early setup/assertion failures, and the parent-only role-01 summary. |
| Report/workflow truthfulness | `passed-by-review` | The Chinese report and workflow bound only this first P3 family, preserve deferred work and local-only integration authority, and leave Issue/Project/provider/release actions separate. |

## Findings

None.

## Risks And Limits

- The historical full authoring run was not repeated at the fixed commit. Its later-changed inputs prevent whole-suite final-head reuse; only the final 12-case role subset is treated as final-source focused evidence.
- Prior focused records name the pre-commit base HEAD and record raw working-file hashes. Their clean current working-byte matches establish source identity on this host, while the clean fixed commit supplies current provenance; they are not relabeled as exact-head command runs.
- Exact native worker invocation timestamps are unavailable. Direct worker clock observations and exact command start/end/monotonic duration are retained without inference from filesystem metadata.
- No hosted, provider, release, publication, complete-P3, or P4 validation was performed or inferred.

## Validation

Preparation:

- Guardrails review-input preflight: `ready`, full tier.
- Subject digest: `43d4aadbeee5f2179cb26d53fa22b5dde32b64c4da87909ad84c3dd68ece6ee0`.
- Criteria digest: `df26108723bb4c8711027ccf88be3855af0e0fa3a6533a9242c8cef54ac71045`.
- Authority digest: `590b3149ebeb44cb69fee3afaaf1d0ca4ea77908afa393a70c1ec5faf3486d67`.
- HEAD/tree, clean tracked state, packet digest, active lease lock, dispatch-message bytes, review-input copy, and authority manifest all matched before execution.

Exact argv:

```text
python -B .ai/scripts/tests/test_ai_context_package_smoke.py -v
```

Measured result:

- Boundary: `require_escalated` for authorized default-temp fixture I/O; `TEMP` and `TMP` were unchanged.
- Started: `2026-09-22T07:36:52.145383+08:00`.
- Completed: `2026-09-22T07:36:53.936133+08:00`.
- Monotonic duration: `1.7906910000601783` seconds.
- Unit-test runner duration: `1.490` seconds.
- Exit code: `0`.
- Tests: 1 run, 1 successful, 0 failures, 0 errors, 0 skipped.
- Execution log SHA-256: `71b2fc317456299317db3efb6499d33910dad19296b5fef4de9e5e1f5ee3e15c`.
- HEAD/tree and tracked status matched before and after the command.

Prior evidence checked:

- Authoring full record: 35 passed, log SHA-256 `e8aab4e87553ad95c6c227d4835cff596d5ce442734c7e816c7541ff0bdbdb13`; prior supporting evidence only.
- Final affected role subset: 12 passed, log SHA-256 `8a48a518482944237226fd832f70c1f90f08125a139d836f89c1e9053eedf562`.
- Final adapters plus registry: 42 passed, log SHA-256 `d46746b1e4650d7daee3af2e18e83fc9d10cafa271ae1294aeec2f862a293385`.
- Final canonical validator: passed for 39 canonical manifests, log SHA-256 `064fbbf30fbcd1ab71420810a294d744309d544202a03c0b28d3e586d0a51eb0`.
- Retained failures: adapter assertion log `3987de66086ad867d4f4f5903bfafa58f07167e8ca140a81c999b12475bf3667`; registry assertion log `171b203627ec390d953500a266b6b50285bd69dc752042d630aa42745da9206e`.

No other command matrix, behavioral retry, repair, tracked mutation, provider action, or credential operation was performed by this auditor.
