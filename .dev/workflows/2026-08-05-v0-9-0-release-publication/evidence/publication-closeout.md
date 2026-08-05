# v0.9.0 Publication Closeout Evidence

- `status`: `passed-with-owner-accepted-procedural-deviation`
- `observed_at`: `2026-08-06T07:05:42+08:00`
- `tag`: `v0.9.0`
- `tag_object`: `0c90a4a3c8e7769b4e46db63f80fb43c5e863289`
- `peeled_commit`: `c14a3260cba7d0a9e2b67b73df9e221280d2d2ef`
- `tagged_at`: `2026-08-06T00:51:57+08:00`
- `publication_run`: `31027306074`
- `release_url`: `https://github.com/YuChia-Wei/ai-collaboration-prompts-dotnet-backend/releases/tag/v0.9.0`

## Immutable Publication Read-Back

- The local and remote annotated tag objects are identical and peel to the
  exact candidate merge commit.
- Publication run `31027306074` completed successfully with `headSha` equal to
  the peeled commit.
- The GitHub Release is stable, non-draft, and non-prerelease.
- The Release exposes exactly the governed ZIP, tar.gz, and both adjacent
  checksum sidecars.
- Downloaded ZIP SHA-256:
  `2c98ac02eabd24ca881798caf83657adc2062ababe42fdb09fe26ce499cc98f2`.
- Downloaded tar.gz SHA-256:
  `d2a7c546fa32f27e180883d07e27b3aa560745bdea33e98604abb50dde974634`.
- Both archive hashes matched their sidecars, ZIP/tar payload parity passed,
  and package metadata identifies version `0.9.0` at source commit `c14a326`.
- The sanctioned tag and hosted publication phase validators passed.
- The official published renderer was applied as a body-only closeout update.
  Rendered and live body SHA-256 both equal
  `eaaa2eb3a1aac38adf719888bee1c7818497e1cb63926f7f3de55f46c1c30f47`;
  tag identity, publication timestamp, and all four asset ID/name/size/digest
  tuples remained unchanged. The hosted finalization phase then passed.
- Clean-install and exact-v0.8.0 upgrade fixtures were not repeated during
  closeout; the earlier explicit owner equivalence waiver remains unchanged.

## Project Publication Read-Back

Project #3 reads all eight canonical Included Work items as `Done`, target
`v0.9.0`, and published in `v0.9.0`:

- `GOV-004` / Issue #86
- `CTX-004` / Issue #98
- `PKG-005` / Issue #99
- `GOV-006` / Issue #104
- `CTX-005` / Issue #105
- `PKG-006` / Issue #106
- `VAL-003` / Issue #107
- `SAG-002` / Issue #118

Issue #128 remains online-only and has no local backlog item or provider
mapping.

## Owner-Accepted HIGH Procedural Deviation

The immutable payload and publication are correct, but the current-main
pre-tag sequence did not comply with the publication runbook:

1. The sanctioned pre-tag gate passed at `main@c14a326` at approximately
   `2026-08-06T00:43:00+08:00`.
2. Documentation-only handoff PR #131 merged as `e4965cb` at
   `2026-08-06T00:51:20+08:00`.
3. The tag was created 37 seconds later but still pointed to `c14a326`.

The runbook states that any intervening main commit, including lifecycle
closeout documentation, invalidates the prior tag command. PR #131 changed no
`.ai`, `.agents`, or `tools` payload path, so this does not change package
correctness, but it remains a HIGH procedural deviation.

After this distinction was presented, the owner directed `完成 0.9.0 的發布` on
2026-08-06. Governance therefore records the deviation as accepted for this
immutable release, preserves the tag without movement or recreation, and
closes the workflow. Future releases must merge pre-tag handoff evidence before
the final current-main gate or defer that evidence until after tag creation.

## Terminal Source Gate

Git for Windows Bash executed `.ai/scripts/check-all.sh --quick` outside the
sandbox without WSL. The single completed run took 847.3 seconds and reported
49/49 required selected checks passed, zero failed, zero blocked, zero skipped,
and two not-applicable checks. A preceding compound-command attempt reached its
tool timeout without retained output and is not counted as a pass or a second
completed execution.
