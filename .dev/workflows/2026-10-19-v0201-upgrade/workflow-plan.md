# v0.20.1 upgrade repair and publication

Issue: [#467](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/467).
Owner authorized three repairs, publication and upgrades from official v0.19.1 and v0.20.0 on 2026-10-19; separately authorized Issue creation. Source base: 867cd57a99d3e5a05bba898054328410c622f36c.

## Scope and decisions
- Preserve historical template bytes inside the existing source engine closure; choose only exact known digests, never rewrite installed hashes or trust arbitrary templates.
- Extend breaking reinstall only to .codex/agents and .claude/agents. Explicit classification, Git baseline and preservation remain required.
- Retain nested preview/post-cleanup plan failures without changing partial-cleanup or recovery ownership.
- Carry the already authorized four documentation corrections. Do not edit installed projections, published old assets, existing untracked v0.20.0 release records or real consumer projects.
- One writer (parent); read-only advice from assess_444. Required independent review uses an immutable commit. Linear PR integration is suitable for this cohesive patch release.

## Stages and validation
1. Implement repairs and direct regression cases; run distribution suite for changed adapter/planning contracts. No additional product tests solely for documentation wording.
2. Commit a fixed review subject, build isolated snapshot, perform real official-origin upgrades and sub-agent reinstall in new F: roots. Preserve failed attempts and positive controls.
3. Independent read-only review and required current-head hosted Source change gate; integrate through PR.
4. Create annotated v0.20.1 tag; obtain pipeline Draft and exact assets. Validate those exact bytes with both official-origin upgrade routes before publishing the same draft.
5. Download public assets/read back tag, release, Issue and Project separately. No branch cleanup or downstream adoption.

## Baseline evidence
F:/aicf-u191-20261019/results.json retains four failed official v0.19.1 -> v0.20.0 upgrade cases and successful v0.20.0 fresh-install control. Old files and lock were unchanged. Other hosts can reproduce from public tags; this local path is not portable evidence access.

## Current state
Implementation and 76 distribution regression cases passed. The first sandbox run failed with 29 temporary-directory PermissionError errors (0 assertions failed); the same suite passed outside that restricted environment. Exact commands: python -I -B tests/run.py --suite distribution. Original reproduction remains retained. Independent review and real packaged upgrade/reinstall tests are next; Issue acceptance remains open until evidence is complete. Windows trials do not claim native macOS acceptance. Existing macOS contract remains unchanged.
