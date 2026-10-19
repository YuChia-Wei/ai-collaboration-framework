# v0.20.1 upgrade repair and publication

Issue: [#467](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/467).
Owner authorized three repairs, publication and upgrades from official v0.19.1 and v0.20.0 on 2026-10-19; separately authorized Issue creation. Source base: 867cd57a99d3e5a05bba898054328410c622f36c.

## Scope and decisions
- Preserve historical template bytes inside the existing source engine closure; choose only exact known digests, never rewrite installed hashes or trust arbitrary templates.
- Extend breaking reinstall only to .codex/agents and .claude/agents. Explicit classification, Git baseline and preservation remain required.
- Retain nested preview/post-cleanup plan failures without changing partial-cleanup or recovery ownership.
- Carry the already authorized four documentation corrections. Do not edit installed projections, published old assets, existing untracked v0.20.0 release records or real consumer projects.
- One writer (parent); read-only advice from assess_444. Required independent review uses an immutable commit. Use a merge commit to retain the source-fix/validation checkpoint as the integration boundary for the subsequent release lifecycle. Issue closure remains deferred until publication.

## Stages and validation
1. Implement repairs and direct regression cases; run distribution suite for changed adapter/planning contracts. No additional product tests solely for documentation wording.
2. Commit a fixed review subject, build isolated snapshot, perform real official-origin upgrades and sub-agent reinstall in new F: roots. Preserve failed attempts and positive controls.
3. Independent read-only review and required current-head hosted Source change gate; integrate through PR.
4. Create annotated v0.20.1 tag; obtain pipeline Draft and exact assets. Validate those exact bytes with both official-origin upgrade routes before publishing the same draft.
5. Download public assets/read back tag, release, Issue and Project separately. No branch cleanup or downstream adoption.

## Baseline evidence
F:/aicf-u191-20261019/results.json retains four failed official v0.19.1 -> v0.20.0 upgrade cases and successful v0.20.0 fresh-install control. Old files and lock were unchanged. Other hosts can reproduce from public tags; this local path is not portable evidence access.

## Current state
Implementation and 76 distribution regression cases passed. The first sandbox run failed with 29 temporary-directory PermissionError errors (0 assertions failed); the same suite passed outside that restricted environment. Exact commands: python -I -B tests/run.py --suite distribution. Original reproduction remains retained. Independent review, packaged snapshot acceptance and exact formal Draft upgrade/reinstall acceptance passed. v0.20.1 is publicly released and verified; the owner subsequently authorized Issue/Project closeout, now read back as CLOSED/COMPLETED, Done and Version v0.20.1. Windows trials do not claim native macOS acceptance. Existing macOS contract remains unchanged.


## Review and build checkpoint
Independent read-only review by assess_443 of 867cd57a..39fe2c96 found no actionable P0-P3 defects; see independent-review.json. PR #468 Source change gate run 39253955780 passed at 39fe2c96.
Initial snapshot build refused the main workspace because retained untracked release records made tooling unclean; no package was produced. A managed clean worktree at F:/git-worktree/v0201-validation/ai-collaboration-prompts-dotnet-backend built snapshot 39fe2c96 successfully, ZIP SHA-256 95270d72c01d3b9c37661e78492cadb619132ca22d141dda93d4c992bac4bca2. Build roots F:/u201sb2 and F:/u201so2. Exact formal Draft bytes still require their own acceptance.

## Snapshot acceptance
Command: `python -I -B F:/u201-trials.py F:/u201so2/p F:/u201t`. Four real public-origin upgrades passed: v0.19.1 Codex-only, Claude-only, complete skills/knowledge/roles with both adapters, and v0.20.0 all skills/knowledge/roles with both adapters. All final managed bytes matched; README, runtime settings and custom agents were preserved. See snapshot-upgrade-results.json. Full request/response/process evidence remains at F:/u201t, not a portable evidence location.

Command: `python -I -B F:/u201-reinstall.py F:/u201so2/p F:/u201t`. Real Git-backed reinstall removed all 12 managed role entries and preserved both custom profiles; final inspect was managed-bytes-consistent. Unclassified and untracked agent cleanup were rejected before mutation. See snapshot-reinstall-results.json. Nested failure response fidelity is covered by focused unit tests, not a forced destructive native failure.

After immutable review, only documentation version/example corrections and these evidence records changed. Product implementation, direct tests and governing rules remain the reviewed 39fe2c96 content. Required current-head PR CI is still refreshed after the record commit; product trials are not repeated solely for that commit.

## Formal release completion
PR #468 head 2006d56eb31440e2fb57939b6f869db12b002159 passed Source change gate run 39254819912 (246 tests, no errors/failures/skips). The ready-for-review event cancelled earlier run 39254784232; that cancelled run is not a pass. PR merged as fba2f031f1c969cd5788af924e307ffebf553422 with the same tree. Exact main snapshot run 39255268520 and formal Draft run 39255304812 passed; these builds do not claim source-test execution at the merge commit.

Annotated tag v0.20.1 object 62559e0196db7275067755fc07e4a4b85c75f3eb identifies that source. Actions and Draft assets, extracted bytes, 452 catalog source files, 23 engine files and README source matched raw Git. Formal ZIP SHA-256: e60b53e83e89ee3742e5ff4b20b5a28037ffef3cf8b12817dcb40c869b89be80.

Commands `python -I -B F:/u201-trials.py F:/u201release/p F:/u201d` and `python -I -B F:/u201-reinstall.py F:/u201release/p F:/u201d` passed against that exact Draft. All four upgrades reached release version 0.20.1 with managed bytes consistent. Reinstall removed 12 managed role profiles, preserved custom profiles and outside-scope README/runtime settings, and rejected unclassified/untracked cleanup before mutation. See formal-upgrade-results.json and formal-reinstall-results.json. Raw request/response/process evidence remains under F:/u201d.

Release ID 417287964 was published 2026-10-19T12:59:58Z, stable and Latest. Public ZIP/checksum/manifest equal the accepted Actions and Draft bytes; asset IDs unchanged. See public-release-verification.json and release-notes.md. Provider raw read-backs/downloads remain F:/u201release. At publication, Issue #467 remained OPEN and Project status Inbox pending separate owner authority. These records do not change the published tag or package.

## Authorized administrative closeout
On 2026-10-19 the owner explicitly authorized committing post-publication acceptance records, closing Issue #467, setting Project Status Done and assigning the version, and correcting the title and bug classification. The issue title is now `修復公開版本升級與 sub-agent 重裝缺陷`, with labels `bug` and preserved `created-by:codex`. Live read-back confirms CLOSED/COMPLETED at 2026-10-19T13:06:08Z, Project #3 Status Done and Version v0.20.1. See administrative-closeout.json.

The missing Version option v0.20.1 was added as 47dc6af5; all 20 existing options retained their IDs, names, colors and descriptions. Current PR integration, successful PR-head CI, exact integrated-source package build and public stable release were re-read before closure. This records-only commit requires content/JSON and diff checks, not another product test or installation run. The commit preserves the original v0.20.0 records, published assets and real consumer projects; branch/worktree cleanup remains outside scope.
