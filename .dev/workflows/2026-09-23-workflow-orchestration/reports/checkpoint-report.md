# Issue #341 local contract checkpoint

Status: design-only; workflow in_progress; source implementation not started.
Baseline: 3a82b3654976fb26da7618a4404f49d7868d813a.
Owning task: P4-CONTRACT; continuation task: P4-SOURCE.
Created: 2026-09-23T09:09:21+08:00. Updated: 2026-09-23T09:12:33+08:00.

## Delivered design

[Contract](../../../design/framework-next/workflow-orchestration/contract.md), closed record/request shapes, Traditional Chinese explanation, synthetic examples and exact interface proposal. One selectable software-development-orchestrator@0.1.0 package; ten expected members; ten public operations; sole software-development-orchestrator.record@1.0.0 read/write family. No source executable/schema/installed runtime changed.

Decisions C341-01..05 require coordinator reconciliation. In particular, actual src/distribution/package.py closes metadata defaults to store/template. Proposed retention/resume defaults remain package-owned operational settings; no silent metadata extension. Knowledge package integration is still based on selected #334 contracts, awaiting actual source reconciliation. PR/backlog metadata and public operations are actual tracked source inputs, with no runtime acceptance claimed.

## Actual observations and checks

- Assigned root, branch, full HEAD, common Git directory and clean initial status matched.
- Issue #341 read OPEN with exact scope. First sandbox request failed with proxy connection refused; scoped read-only network retry succeeded. No unchanged unbounded retry or provider write.
- Missing dispatched governance canonical SKILL.md was resolved using the actual runtime wrapper and skill.yaml; coordinator confirmed the path correction.
- Narrow code graph indexed src/distribution only, without persistence; returned 82 nodes / 441 edges and no index SHA. Direct tracked source read-back and equal Git object hash ffb0d580021d2c8bd33bd4aa0dbb804b5f81b135 bound the metadata-default conclusion to baseline HEAD.
- Direct bounded PowerShell here-string piped to `python -B -`: read only the eleven new files as strict UTF-8, parse JSON via json.loads (duplicate/non-finite rejection), YAML via yaml.safe_load and resolve local Markdown targets. Exit 0: utf8=11, json=5, yaml=1, local_markdown_links=19. No schema library/product import or pycache.
- `git diff --cached --check`: exit 0 after staging only those eleven files. `git diff --cached --stat`, `--name-only` and selected content read-back confirmed only the two authorized roots. Final metadata edits receive the same narrow checks before commit.
- `python -B .ai/scripts/validate-git-commits.py --message-file .dev/workflows/2026-09-23-workflow-orchestration/commit-message.tmp --workflow-id 2026-09-23-workflow-orchestration`: exit 0, "Git commit validation passed for planned message." The .tmp path is already ignored; exact message bytes are used by git commit -F.
- Root/branch/HEAD remained the assigned baseline during checks. No active default pre-commit/prepare-commit-msg/commit-msg/post-commit hook was found; core.hooksPath was unset. No hook or product execution was used for this inspection.

No product CLI/help, schema validator, test, fixture, build/package/install/migration, audit packet, review lease, legacy gate or CI was run. These are deferred-by-owner under U001, owner program #322 coordinator / P7, next action select and execute redesigned checks after implementation. Direct parsing is syntax only. Independent review and behavior/platform/concurrency guarantees remain unverified.

## Handoff and limits

Resolve the exact local commit containing handoff.json; callback supplies its full HEAD. Preserve it once cited. No push/PR/merge, Issue/Project/settings/credentials action, tag/release or adoption. Coordinator owns shared index/mappings and first push.

Resume only when the coordinator supplies reconciled C341-01..05 and the actual #334 dependency subject, in this same task/worktree. #316 remains separate legacy authoring scope; P5/P7 must decide surviving overlap.
