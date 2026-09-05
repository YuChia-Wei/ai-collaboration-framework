# Issue 271 local implementation evidence

- Selected removal release: v0.16.0. Project allocation and release publication remain separate.
- AC1: v0.16 tombstone manifest records both removals and post-removal policy. v0.6 activation bytes remain historical.
- AC2: Six deprecated canonical/runtime entries removed; active replacement specs and wrappers unchanged. Runtime and product identity registries declare retirement.
- AC3: Existing workflow/task/assessment/release/provenance/evaluation files were not edited. New evidence is confined to this workflow, the workflow index, and new test fixtures.
- AC4: Deterministic resolver defaults to runtime rejection; explicit historical context accepts the original retired identifier as evidence only.
- AC5: Six isolated upgrade scenarios use exact v0.6.0/v0.9.0 alias bytes. Existing migration generator and planner remove unchanged framework files, preserve modified/target-owned files pending owner reconciliation, and preserve historical task bytes. This is fixture execution, not a published upgrade route or actual downstream deployment.
- AC6: Both old names produce explicit retired/replacement diagnostics, including nonzero CLI status for new requests.

## Focused validation

- Retirement suite: 14 tests passed in 16.479 seconds with self-contained published-byte fixtures.
- Repository identity suite: 13 tests passed in 5.826 seconds after adding the new manifest to its synthetic repository.
- AI context, skill transition, workflow artifacts, source dispositions, and repository identity validators passed.
- Historical activation evaluation evidence is retained unchanged; no current model-in-loop behavior evaluation is claimed.

## Failure evidence

- Default sandbox denied test-file writes and temporary directory access. Protected writes and isolated tests succeeded through authorized escalation; no environment override or TEMP redirection was used.
- First retirement upgrade fixture lacked the mandatory approved remediation decision (two unchanged-version cases failed). Adding the existing fixture authorization helper made the suite pass; production gates were not weakened.
- Workflow validator initially rejected two active tasks; metadata was corrected to one active task.
- Repository identity suite initially lacked the retirement manifest in its synthetic repository (six failures); supplying the current manifest made all 13 pass.

## Pending gates

Freeze the coherent commit, inspect the portable payload, and perform an independent read-only post-remediation audit. No push, PR, merge, Issue/Project mutation, tag, release, or publication has occurred.
