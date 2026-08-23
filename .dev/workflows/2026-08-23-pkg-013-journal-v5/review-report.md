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

## Candidate `679bc0bea9c08176c3495946fb0c228ef4f4e6a2`

- Subject and parent matched; tracked worktree and index were clean at audit start and end.
- Full suite result: 87 passed, 0 failed, 1 skipped in 503.146 seconds, with a schema-valid completion envelope.
- Independent result: `failed`; P1=1, P2=0, P3=0. The test pass cannot override the failed review.
- P1: replacing the complete `<transaction-id>/` directory with a symlink or junction left its plan, journal, and progress leaves looking regular and allowed recovery to follow the ancestor outside Git-admin.
- Prior leaf-link and all earlier semantic, state, v4, and progress findings were confirmed resolved.

## Transaction-Root Boundary Remediation

- The resolved Git-admin transaction base and each transaction root must be real directories, not symlinks or reparse points, before locking, preparation, load, snapshot persistence, progress load/append/truncation, or legacy scanning.
- Target admission records a SHA-named unsafe transaction child as an error rather than silently skipping it.
- GWT-070 redirects or simulates redirecting the transaction root and proves recovery, append, and target admission fail before the next target operation or external progress bytes change.

## Accepted Candidate `c3ffc2f4d2b576943595f2b0b99692f39d7895e5`

- Subject and parent matched; tracked worktree and index were clean at audit start and end.
- Full suite result: 88 passed, 0 failed, 1 skipped in 533.226 seconds; the schema 1.1 completion record validated against its exact dispatch.
- Independent result: accepted for local implementation handoff with P1=0, P2=0, P3=0.
- The audit confirmed Git-admin base/root and leaf link safety, v4 mutation blocking without v4 recovery, target/recovery semantic and state parity, per-operation durability, linear deterministic logical I/O, torn-tail recovery, idempotency, and stderr-only progress.
- The prior failed audits of `c196c558`, `ed48ec99`, `34753883`, and `679bc0be` remain retained and are not replaced by the accepted result.
- Residual coverage: native Windows junction creation was not independently exercised when the host required mocked reparse classification; concurrent path replacement between validation and open is outside deterministic fixture coverage.

## Review Disposition

- Accepted implementation subject: `c3ffc2f4d2b576943595f2b0b99692f39d7895e5`.
- The later workflow closeout and PR declaration commits initially changed evidence only, but the required fresh PR-head audit exposed two additional P1 path-safety defects at `6502c29603cb46c52b200c20d00ff3098e71ca5a`.
- PR #240 remains draft and blocked from merge until the repaired exact head passes full validation, hosted checks, and a fresh independent audit.
- Issue closure, Project mutation, release allocation, tag, Release, and publication remain outside this review.

## Candidate `6502c29603cb46c52b200c20d00ff3098e71ca5a`

- Subject and base matched; tracked worktree and index were clean at audit start and end.
- Independent result: `failed`; P1=2, P2=0, P3=0. The five passing hosted checks cannot override the failed review.
- P1: `transaction.lock` opened an unchecked leaf with `Path.open("a+b")`, so a symlink or reparse point could redirect the initial durable lock byte outside Git-admin.
- P1: missing, unsafe, unreadable, or malformed SHA-root `journal.yaml` evidence was skipped by the v4 mutation guard, so an unfinished legacy transaction hidden behind that leaf was not proven terminal before new mutation.
- Prior semantic, write-amplification, durability, v5 replay, progress-log, and transaction-root findings remained resolved.

## PR-Head Path-Safety Remediation

- The lock leaf is rejected when it is a symlink, reparse point, or non-regular file; opening uses `O_NOFOLLOW` when available, validates the opened descriptor as regular before any write, and maps open failure to the stable apply safety boundary.
- A SHA-root transaction with missing, unsafe, unreadable, malformed, or unsupported journal evidence now blocks mutation because it cannot be proven terminal; recognized v5 evidence is not reclassified as v4, and only proven terminal v4 remains nonblocking.
- GWT-071 proves a lock link cannot create or alter an external file or mutate the target.
- GWT-072 covers missing, unsafe, unreadable, and malformed legacy journal leaves with stable unsupported-version guidance and no target mutation.
- The repaired exact head requires a new full-suite receipt and independent audit; no prior pass is promoted to that future head.
