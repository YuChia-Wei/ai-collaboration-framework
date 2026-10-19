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
Implementation and 76 distribution regression cases passed. The first sandbox run failed with 29 temporary-directory PermissionError errors (0 assertions failed); the same suite passed outside that restricted environment. Exact commands: python -I -B tests/run.py --suite distribution. Original reproduction remains retained. Independent review and packaged snapshot upgrade/reinstall acceptance passed; exact formal Draft acceptance remains pending. Windows trials do not claim native macOS acceptance. Existing macOS contract remains unchanged.


## Review and build checkpoint
Independent read-only review by assess_443 of 867cd57a..39fe2c96 found no actionable P0-P3 defects; see independent-review.json. PR #468 Source change gate run 39253955780 passed at 39fe2c96.
Initial snapshot build refused the main workspace because retained untracked release records made tooling unclean; no package was produced. A managed clean worktree at F:/git-worktree/v0201-validation/ai-collaboration-prompts-dotnet-backend built snapshot 39fe2c96 successfully, ZIP SHA-256 95270d72c01d3b9c37661e78492cadb619132ca22d141dda93d4c992bac4bca2. Build roots F:/u201sb2 and F:/u201so2. Exact formal Draft bytes still require their own acceptance.

## Snapshot acceptance
Command: `python -I -B F:/u201-trials.py F:/u201so2/p F:/u201t`. Four real public-origin upgrades passed: v0.19.1 Codex-only, Claude-only, complete skills/knowledge/roles with both adapters, and v0.20.0 all skills/knowledge/roles with both adapters. All final managed bytes matched; README, runtime settings and custom agents were preserved. See snapshot-upgrade-results.json. Full request/response/process evidence remains at F:/u201t, not a portable evidence location.

Command: `python -I -B F:/u201-reinstall.py F:/u201so2/p F:/u201t`. Real Git-backed reinstall removed all 12 managed role entries and preserved both custom profiles; final inspect was managed-bytes-consistent. Unclassified and untracked agent cleanup were rejected before mutation. See snapshot-reinstall-results.json. Nested failure response fidelity is covered by focused unit tests, not a forced destructive native failure.

After immutable review, only documentation version/example corrections and these evidence records changed. Product implementation, direct tests and governing rules remain the reviewed 39fe2c96 content. Required current-head PR CI is still refreshed after the record commit; product trials are not repeated solely for that commit.
