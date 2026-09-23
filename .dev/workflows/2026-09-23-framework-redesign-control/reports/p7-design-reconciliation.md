# P7 design reconciliation and inspection

Coordinator inspection, not an independent audit or behavioral validation.

| Delivery | Fixed commit | Actual narrow checks |
| --- | --- | --- |
| #364 verification design | `577f3922587ccd8cc8e314f5c558ad6991530886` | Clean assigned worktree; 7 owned UTF-8 files, 1 JSON, 1 YAML, 19 tracked local links; fixed diff whitespace clean |
| #365 pipeline/policy design | `c75582b08f67da17f9548f2eb38fe67c2e6e765e` | Clean assigned worktree; 8 owned UTF-8 files, 2 JSON, 1 YAML, 12 tracked local links; fixed diff whitespace clean |

Both independent Astra Ultra tasks completed and returned their original fixed
commits. Only their assigned design/workflow roots changed. Local integration
preserves those commits and the coordinator dispatch checkpoint `9647feab`.

[Selected implementation sequence](../../../design/framework-next/p7-execution-selection.md)
resolves first source contracts versus later public/configuration cases, dormant
pipeline ownership, actual command binding, Windows-only native entry, explicit
RAM native fixture input with persistent recovery, and separate source adoption/
owner-adopted CI restoration. There is no implementation or execution claim here.

Original request coverage and remaining limits are recorded in
[the coverage table](request-coverage-at-p7-entry.md). The current finding table
in [the delivery ledger](remediation-report.md) now reflects complete source
mapping rather than the historical #359/#361 snapshot. F-01 through F-08 remain
partially resolved; conditional P8 work is not silently added to P7.

Provider evidence from #365 records Actions=false and all seven legacy workflows
disabled at 2026-09-23T14:32:06+08:00, absent main protection/effective rulesets,
and minimal workflow permissions. It does not prove future state or hosted
acceptance. Program #322 body was updated with provider updated_at 2026-09-23T14:41:04+08:00 and separately read back unchanged to reflect source completion and remaining P7/root work;
Issue remains OPEN. #364/#365 stay OPEN until their design PR integrates.

Retained preparation failures in worker reports include Windows command-length
failures before process creation, initial sandbox network refusal, absent guessed
paths and an unavailable official documentation URL. Later bounded discovery and
writes resolved those needs. No automatic-review blocker remains from those
observations. A coordinator thread lookup typo was corrected to the existing #365
ID; no replacement conversation was created.

Coordinator checks passed: 24 changed UTF-8 files, 5 JSON, 3 YAML, 94 local
references (only added index rows), all 15 fixed worker blobs preserved,
`git diff HEAD --check` and the complete planned commit-message validator.
The staged scope and whitespace are checked again before committing these records. Product/runtime/schema/tests/build/
install/migration/native and hosted CI are still `deferred-by-owner`, U001, owner
program #322 coordinator / P7. The next Issues may execute only their explicit
selected cases; this design PR itself has executed none.
