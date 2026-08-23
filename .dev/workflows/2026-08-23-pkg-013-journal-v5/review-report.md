# PKG-013 Journal v5 Independent Review

## Review Scope

- Workflow: `2026-08-23-pkg-013-journal-v5`
- Owner skill: `ai-context-governance`
- Role-binding owner: `ai-context-upgrader`
- Canonical role: `.ai/assets/sub-agent-role-prompts/fixed-head-independent-auditor/sub-agent.yaml`
- Gate selection: explicit high-risk fixed-head gate because journal recovery controls durable downstream target mutation after crashes.
- Integration owner: source-task primary agent; the auditor cannot accept integration or close the workflow.

## Candidate `c196c5589f228b791f46dace8c4e8e9dca5d8cce`

- Subject and parent matched; tracked worktree and index were clean at audit start and end.
- Result: `failed`; P1=2, P2=0, P3=0.
- P1: unfinished v4 detection guarded new apply but not v5 resume or rollback, so recovery could still mutate a target while unsupported unfinished v4 evidence existed.
- P1: target provenance validated v5 progress framing and digests without binding operation IDs, indexes, rollback paths, transitions, and snapshot prefixes to the sealed plan; a digest-resealed log could pass target validation while recovery rejected it.
- The failed review remains retained evidence and cannot be replaced by the preceding 82-test pass.
- Auditor residual coverage notes: rollback write-byte scaling and high-N replay/read cost were not independently concluded after the two P1 findings failed the gate.

## Remediation

- The recovery lock now runs the same unfinished-v4 mutation guard before loading or mutating a v5 transaction.
- Target provenance now reuses the package recovery semantic replay against the identity-verified sealed plan, preventing the admission and recovery contracts from diverging.
- GWT-065 covers both resume and rollback blocking with target bytes unchanged.
- GWT-066 reseals a semantically false operation ID and digest chain and requires target validation and recovery to fail closed consistently.

## Candidate `ed48ec9954ccce926fceae22bb23b498ea402d23`

- Subject and parent matched; tracked worktree and index were clean at audit start and end.
- Full suite result: 84 passed, 0 failed, 1 skipped in 481.154 seconds, with a schema-valid completion envelope.
- Independent result: `failed`; P1=1, P2=1, P3=0. The test pass cannot override the failed review.
- P1: when `progress.jsonl` was absent and snapshot count/tail were reset to zero/null, target admission returned before sealed-plan replay and accepted a finalized snapshot that recovery rejected.
- P2: target admission reused semantic replay but omitted recovery's subsequent `validate_journal_progress` state invariants, allowing a finalized journal to retain fully compacted rollback progress.
- Prior finding disposition: unfinished-v4 resume/rollback blocking and digest-valid wrong-operation binding were confirmed resolved.

## Complete Recovery-Parity Remediation

- A missing zero-count log no longer returns before semantic validation; replay must prove the snapshot is truly a zero-operation prefix.
- Target admission now executes both `replay_journal_progress` and `validate_journal_progress` from the recovery implementation against the identity-verified sealed plan.
- GWT-067 covers the missing-log/snapshot-prefix bypass.
- GWT-068 covers fully compacted rollback progress in a non-rollback terminal journal.

## Candidate `34753883e38501175c0c7f0a91dd26894cab33bd`

- Subject and parent matched; tracked worktree and index were clean at audit start and end.
- Full suite result: 86 passed, 0 failed, 1 skipped in 496.087 seconds, with a schema-valid completion envelope.
- Independent result: `failed`; P1=1, P2=0, P3=0. The test pass cannot override the failed review.
- P1: a broken `progress.jsonl` symlink or reparse point reported `exists() == false`, so load treated it as missing and append/truncation could later follow it outside the transaction boundary.
- Prior findings for v4 mutation safety and target/recovery semantic/state parity were confirmed resolved.

## Broken-Link Boundary Remediation

- Load, target admission, append, and torn-tail truncation reject symlink/reparse progress paths before testing existence.
- Append and truncation also request `O_NOFOLLOW` on platforms that expose it and convert unsafe open failures to the stable apply safety boundary.
- GWT-069 covers a broken-link resume, direct append, and torn-tail truncation while proving neither the next target operation nor the external link target is created.

## Required Re-review

- The broken-link repair requires a new immutable commit, full fixed-head validation, and a fresh independent audit of that new SHA.
- No acceptance conclusion is recorded for the repaired working tree yet.
