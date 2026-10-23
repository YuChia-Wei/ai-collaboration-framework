# v0.21.0 publication

## Authority and scope

On 2026-10-24 (Asia/Taipei), the owner explicitly authorized filling version fields, aligning documentation with the new rules, fast-forward integration into main, creation of the 0.21.0 tag and completion of publication. The owner explicitly waived Issue binding for these actions and declined a new release Issue. The earlier automatic approval rejection of Issue creation is retained here; no Issue was created. Public explanatory text must remain valid after publication or omit version references.

Input main: `bef09eedeab07e670449cc7dad8262058e05e17e`; prior public tag: `v0.20.2`. Use a PR and `git merge --ff-only`, with no merge commit. Source release policy owns this workflow directly; no installed release skill is claimed. The workflow preserves publication/partial-failure recovery state and the explicit Issue-binding exception.

## Delivery

Product Issues: #476–#480, #482, #484, #487, #490, #491, #496, #498, #500–#502, #504. The latter eleven had no Version and were assigned v0.21.0. #492 (source packaging), #497 (source policy), #505 (test fixture) are supporting source maintenance, not packaged product allocations. Unimplemented work and already published v0.20.2 Issues are excluded.

Documentation corrects obsolete version baselines, initialization version pins, model-inheritance wording, fixed engine-member counts, old architect migration/empty-directory statements, and obsolete unpublished/candidate phrasing. Preserve historical RC4 and v0.19/v0.20 compatibility evidence, project-specific installation state, platform guarantees and the unpublished standards-promotion experiment.

## Validation selection

This change is explanatory documentation and lifecycle records only. Inspect the diff, relative links and commit message; product tests and src/tools hosted path gate are not applicable to this diff. Reuse PR #503 Source change gate 39961997497 (338 tests) for its actual product subject; the later #505 change is tests-only. Compare product/tooling trees to that integrated baseline before tag creation. No new installation or model behavior acceptance is claimed. Build the exact annotated tag through the existing hosted draft workflow; verify the manifest, ZIP checksum/content, tag/source and unchanged Draft-to-public bytes. Do not rebuild admitted assets or mutate existing public tags/releases.

## Completed outcome

PR #510 was inspected and fast-forward merged into main at `221695622dde248a2dc84ffb9fc675d7c45d0768`; GitHub reports MERGED with the same commit, and no merge commit was created. Documentation validation covered 9 changed documents and 87 resolving relative references; workflow structure, planned and actual commit validation, and git diff --check passed. Product src/tools/.github trees matched the integrated PR #503 baseline. This explanatory diff changed no installation/recovery/publication behavior or policy, so no new independent implementation review or product test run was triggered.

Annotated tag `v0.21.0` object `e1b7e2d92e6994ea254b69661135f12a54b0d63d` peels to the same source. Hosted run [39987360640](https://github.com/YuChia-Wei/ai-collaboration-framework/actions/runs/39987360640), attempt 1, completed build and draft successfully. Release ID 422073042 became stable Latest at 2026-10-24T00:34:42+08:00. The public [Release](https://github.com/YuChia-Wei/ai-collaboration-framework/releases/tag/v0.21.0) retains the ownership marker, source and assets.

The existing repository verifier checked all 497 ZIP entries, catalog identity, raw hashes, Engine closure/pin, README provenance and checksum. All three files from the original Actions artifact, authenticated Draft, and unauthenticated public download are byte-identical. See [publication-verification.json](publication-verification.json) for identities and hashes. No new native installation or runtime behavior test was performed or claimed.

Provider read-back confirms Version and Published `v0.21.0`, Status `Done` for all 16 product Issues. Eleven Version fields were filled; five already had the selected version. The new Published option preserved every prior option ID/name/color/description. Source-only and unimplemented items were not allocated. The owner explicitly declined Issue #496/#498 body edits after automatic approval review treated those as outside field/document authority; both bodies remain unchanged by request.

## Retained diagnostics and disposition

- Sandbox could not access the supplied worktree; authorized elevated calls read and operated on the exact path.
- Get-Volume did not enumerate F:, while Win32_LogicalDisk confirmed RAMDRIVE with approximately 16 GiB free. Disposable downloads stayed under F:/tmp/aicf-v0210-20261024; durable verification is retained here.
- Draft REST tag lookup returned 404; authenticated paginated release listing selected the unique owned Draft. No unknown write was retried.
- The initial exact notes comparison failed because GitHub normalized LF to CRLF. Read-back proved only newline normalization; content matched before publication and after public read-back.
- New release Issue creation was rejected by automatic approval review. The owner subsequently explicitly waived Issue binding; no new Issue was created. Issue-body edits were independently rejected and then declined by the owner; no alternate write path was used.

## Closeout

All requested release operations and verification are complete. This records-only continuation starts from integrated main and retains the fixed release tag/assets. Integrate its PR using the same owner-selected fast-forward path. Its integration does not move the release tag or rebuild assets. No product or hosted source-check rerun is required for this records-only diff.
