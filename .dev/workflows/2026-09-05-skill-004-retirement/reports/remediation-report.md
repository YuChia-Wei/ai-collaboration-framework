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

## Local completion

The implementation, bounded payload membership inspection, and independent post-remediation audit are complete. The separate full release-packaging gate remains blocked by the baseline issue described below. No push, PR, merge, Issue/Project mutation, tag, release, or publication has occurred.

## Independent review and bounded package inspection

- Review 1 on `63b3b51ee5d53f97ae73f09e4f43f870feda17fe` / tree `f681290df086cfc025601bc8b8128d5992333924`: failed with MEDIUM SKILL004-R1, stale active guidance in two upgrader references and two compatibility guides. No actionable code defect found; all 12 fixture byte/hash records independently matched the recorded release commits. The four current guides were corrected; follow-up review passed on `a6563a23b0beb4b2e6ee34de14ede5380f0921ad` (tree `046a656b13d57de493d6553ab1251687b49d924e`), resolving SKILL004-R1 with no new actionable findings.
- Portable payload inventory: 640 entries, new resolver and tombstone present, all six retired entries absent. Historical and active-replacement Git bytes unchanged.
- Full payload reference integrity is blocked by the same preexisting error on baseline `f06e8e3a882e375e31e315569741541ac6e1659d` and the reviewed commit: validation-profile-registry.sh references excluded v0.14.0 output.json, receipt.json, and support-matrix.yaml. This is not a full package pass and is outside this Issue's retirement scope. Release packaging remains a separate gate.

- Final affected AI context validation passed after the four guidance corrections. Tests were not repeated for the documentation-only change.
- AC1–AC6 are satisfied for local source implementation and isolated fixtures. Publication, hosted checks, and real downstream application are outside this result.
- Terminal workflow validation rejected current_phase closure for a completed workflow; changed it to completed and the validator passed.
