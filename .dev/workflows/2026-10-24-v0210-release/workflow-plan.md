# v0.21.0 publication

## Authority and scope

On 2026-10-24 (Asia/Taipei), the owner explicitly authorized filling version fields, aligning documentation with the new rules, fast-forward integration into main, creation of the 0.21.0 tag and completion of publication. The owner explicitly waived Issue binding for these actions and declined a new release Issue. The earlier automatic approval rejection of Issue creation is retained here; no Issue was created. Public explanatory text must remain valid after publication or omit version references.

Input main: `bef09eedeab07e670449cc7dad8262058e05e17e`; prior public tag: `v0.20.2`. Use a PR and `git merge --ff-only`, with no merge commit. Source release policy owns this workflow directly; no installed release skill is claimed. The workflow preserves publication/partial-failure recovery state and the explicit Issue-binding exception.

## Delivery

Product Issues: #476–#480, #482, #484, #487, #490, #491, #496, #498, #500–#502, #504. The latter eleven had no Version and were assigned v0.21.0. #492 (source packaging), #497 (source policy), #505 (test fixture) are supporting source maintenance, not packaged product allocations. Unimplemented work and already published v0.20.2 Issues are excluded.

Documentation corrects obsolete version baselines, initialization version pins, model-inheritance wording, fixed engine-member counts, old architect migration/empty-directory statements, and obsolete unpublished/candidate phrasing. Preserve historical RC4 and v0.19/v0.20 compatibility evidence, project-specific installation state, platform guarantees and the unpublished standards-promotion experiment.

## Validation selection

This change is explanatory documentation and lifecycle records only. Inspect the diff, relative links and commit message; product tests and src/tools hosted path gate are not applicable to this diff. Reuse PR #503 Source change gate 39961997497 (338 tests) for its actual product subject; the later #505 change is tests-only. Compare product/tooling trees to that integrated baseline before tag creation. No new installation or model behavior acceptance is claimed. Build the exact annotated tag through the existing hosted draft workflow; verify the manifest, ZIP checksum/content, tag/source and unchanged Draft-to-public bytes. Do not rebuild admitted assets or mutate existing public tags/releases.

## Progress and next action

Version writes and provider read-back confirm all eleven selected Issues now have v0.21.0; all sixteen product Issues retain Done status. Published is unchanged pending public verification. Documentation edits are prepared for validation and PR review. Next: commit, push, PR, fast-forward main, annotated tag, owned Draft verification, release notes, public publication and final provider read-back. Keep Published unchanged until actual public verification.

Documentation validation: 9 changed explanatory documents inspected; 87 relative path references resolve; git diff --check passed. Product src/tools/.github trees match fca7ca3e, the integrated PR #503 baseline. The selected documentation diff does not change installation, recovery, security or publication behavior/policy; independent implementation review is not newly triggered. Existing implementation reviews retain their own evidence.
