# S4 bounded content review and integration decision

Issue #404, program #322. Reviewed source commit `6d5c0df13ef93c55c7d2c95beaeb420e32954c40`, base `9247f444eb14a86849c66078cd7fa366dc098379`; accepted corrected delivery `ece36743624e9031cf47686e5ecdca9d4f3a2f4b`.

## Decision and coverage

Accept the bounded S4 renderer/template and handoff implementation for coordinator integration. A separate read-only sub-agent applied the common code-review route to the two renderer modules, two templates, immediate test assertions and necessary helper/contract context. No actionable code findings were returned. Aggregate/controller/reactor and .NET specialist routes did not apply. This is static content reasoning, not a formal independent audit, behavioral acceptance or runtime observation.

| Acceptance | Evidence and remaining boundary |
| --- | --- |
| S4-A1 | Parent compared exact old Codex function text and original template bytes with the assigned base; unchanged. |
| S4-A2 | Separate v2 seams, fixed runtime roots and exact seven template keys; source review and direct AST/template inspection only. |
| S4-A3 | Thin selected-core entries and template discrimination implemented. Explicit caller/format dispatch, migration admission and old-name removal stay with S3. |
| S4-A4 | Parent recomputed actual template/renderer hashes, sizes, modes and legacy source identities from Git blobs; exact inventory expectations are in the S3 handoff. |
| S4-A5 | Immediate cases are authored but unexecuted. Three Python files parse; nine changed paths are owned; UTF-8/JSON/YAML, diff and exact-message checks were performed. |
| S4-A6 | Independent actual Codex/Claude discovery observations are defined for S6; neither was executed. |

## Correction and evidence reuse

The first local delivery assigned A4/A5 evidence to the wrong Issue identifiers. The executor corrected only task.json and workflow-plan.md. All six reviewed renderer/template/test/handoff blobs remain identical, so the code review applies to the corrected delivery without another code review. The parent read the corrected mapping and parsed JSON. The executor retained an initial JSON formatting failure before its repair. A parent comparison helper initially expected an invented literal status label; after inspecting the actual correct free-text label, that helper assertion was corrected and the remaining unchanged-blob comparison completed. Neither preparation failure was a behavioral product failure or a test pass.

## Limits and next owner

Legacy/formal/critical/behavioral/installation/runtime/hosted/CI verification remains `deferred-by-owner` under U001, owner program #322 coordinator/P7 with selected S6 work. S3 consumes the exact handoff and owns manifest, selection, caller dispatch, generator/engine closure and safe ownership transitions. Online PR integration, Issue closure and Project Done remain separately pending here. S2 and the full rc.2 program are not complete.
