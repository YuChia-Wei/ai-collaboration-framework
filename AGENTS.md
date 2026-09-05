# AGENTS.md

[Traditional Chinese](AGENTS.zh-TW.md)

This file is the canonical English root collaboration guide. `AGENTS.zh-TW.md` is its Traditional Chinese (Taiwan) translation.

## Scope And Authority

- This is the source repository for a reusable AI collaboration framework, not a product application.
- A deeper `AGENTS.*` file overrides this file in its subtree.
- Precedence is: user and explicit approval, deeper `AGENTS.*`, this file, then other general documents.
- Use current Git-tracked files, validated records, and live provider read-back. Historical workflows, assessments, releases, examples, and migrated records are evidence, not current state.
- Keep source-framework, downstream target, provider, and runtime session truth separate.
- Do not invent facts, authorization, availability, execution, validation, Issue state, or release state. Stop for unresolved owner-sensitive decisions.

## Execution Rules

- Make the smallest coherent change that satisfies accepted scope and observable completion criteria.
- Touch only required files; preserve unrelated user changes.
- Treat implementation, push, pull request, merge, Issue or Project mutation, tag, release, publication, and credential use as separate actions unless authorized together.
- Prefer deterministic tools for inventories, paths, hashes, schemas, Git identity, build, test, and receipts.
- `failed`, `blocked-by-environment`, `not-applicable`, and `deferred-with-owner` are not `passed`.
- Prefer an applicable and permitted IDE MCP refactoring operation.

## Progressive Context Loading

1. Start with the request, current Git/worktree state, this file, and explicitly named Issues or artifacts.
2. Select one owning skill or policy, then load its canonical entry.
3. Expand only for an applicable phase, finding, file type, provider, decision, or execution boundary.
4. Do not preload `README.md`, all indexes, all standards, every skill reference, historical workflows, or assessment archives.
5. Do not broad-scan `src/`, `tests/`, `.dev/workflows/`, or `.dev/assessments/` unless scope requires it.
6. Verify material conclusions with Git-tracked evidence, current provider read-back, or repository-owned validators. No search result is not proof of absence.

## Task Routing

Use `.ai/assets/skills/README.MD` as the canonical skill registry. Runtime wrappers remain thin and are never a second authority.

| Need | Owning route |
| --- | --- |
| AI-context audit | `ai-context-auditor` |
| AI-context governance, routing, translation, remediation, or source-release governance | `ai-context-governance` |
| First target adoption or initialized-target upgrade | `ai-context-init` / `ai-context-upgrader` |
| Historical or exceptional release verification | `ai-context-release-closeout` |
| Multi-stage software development | `software-development-orchestrator` |
| Architecture, GWT design, review, or implementation | `ddd-ca-hex-architect` / `bdd-gwt-test-designer` / `code-reviewer` / `slice-implementer` / `local-change-implementer` |
| Observed failure, performance symptom, or root-cause diagnosis | `diagnostic-analyst` |
| Requirements, specifications, problem frames, or selected compliance | `requirement-author` / `spec-author` / `problem-frame-author` / `spec-compliance-validator` |

- For AI-context placement or language changes, load `.dev/standards/AI-CONTEXT-BOUNDARY.md` and `.dev/standards/AI-CONTEXT-LANGUAGE-POLICY.md` only when applicable.
- For code review, load `.ai/assets/skills/code-reviewer/references/review-routing.yaml` first and only selected route and finding references.
- `test-execution` has no required skill; resolve target-owned commands first.
- Direct execution remains valid. For delegation, load `.ai/assets/shared/ROLE-EXECUTION-CONTRACT.md`; static profile presence is not invocation evidence.

## Workflow And Change Control

- Small, local, single-pass work may remain direct mode.
- For source-of-truth, AI-context, routing, wrapper, multi-stage, or durable cross-session work, load `.dev/standards/WORKFLOW-GATE-POLICY.md`.
- In workflow mode, follow `.dev/standards/WORKFLOW-ARTIFACT-POLICY.md` and `.dev/TEAM-GIT-FLOW-RULES.MD`; switch to the dedicated branch before material edits.
- A retained read-only report uses `.dev/standards/ASSESSMENT-ARTIFACT-POLICY.md`; it does not require a workflow by itself.
- For cross-session transfer, follow `.dev/standards/WORKFLOW-HANDOFF-POLICY.md`; the checkpoint must not depend on hidden conversation state.
- Before committing, follow `.dev/standards/GIT-COMMIT-POLICY.md` and validate the complete planned message from a message file before invoking `git commit`.
- Merge, workflow completion, Issue closure, Project status, release allocation, publication, and target upgrade are distinct states.

## Validation And Review

- Define observable acceptance criteria and run the narrowest meaningful validation first.
- Do not weaken fail-closed behavior merely to pass a test.
- Independent review runs against one immutable commit, binds to an exact content subject, stays read-only, and cannot count its own repair as verification.
- Content, criteria, or authority drift after review invalidates that review. Commit-SHA drift alone requires a deterministic current-subject rebind, not repeated independent review.
- Preserve failure, timeout, interruption, and blocked evidence; a later pass does not erase it.

### Validation Freeze And Evidence Reuse

- Classify validation evidence as identity-, input-, environment-, or provider-sensitive before reuse. Reuse requires matching tracked bytes, transitive dependencies, command, profile, environment, runner, manifest, resolver, policy, and configuration authority.
- Freeze only after tracked mutation and focused validation are complete. After freeze, tracked content or governing-authority drift invalidates the subject; history-only identity drift requires rebind. Terminal metadata writes only to declared ignored artifacts and does not invalidate the frozen snapshot.
- Unknown dependency or authority state fails closed. Current-head review-subject binding, required hosted contexts, and live admission gates are always fresh; an equal content digest may reuse the independent review without repeating it.
- Required hosted contexts remain present for every admitted head. Internal execution or proven reuse may vary, but path filtering must not make a required context disappear.
- A content-addressed independent audit reports each gate as `re-executed`, `reused-with-proof`, `blocked`, `deferred`, or `not-applicable`; commit SHAs remain provenance rather than the validity key.

### Agent Execution Guardrails

- Before delegated, external, or fixed-head execution, validate an agent execution packet with owning skill, canonical role path and applicability, exact SHA/argv/cwd, permissions, ignored artifact roots, terminal schema and callback, integration owner, stop conditions, and retry budget. The SHA pins the execution checkout; evidence validity follows the applicable content-subject contract.
- Hold a machine-readable worktree snapshot lease. One active tracked-writer holder excludes every other tracked writer; read-only work and declared ignored validation output remain permitted, and terminal release must be explicit.
- Keep an acceptance-to-evidence ledger and validate its human-report projection. Synthetic, mock, fixture, and unit evidence cannot satisfy an acceptance that requires actual execution.
- Retry only after a privacy-safe failure fingerprint and material state change. Attempt three or later requires new owner or workflow authorization.
- Verify code-graph index SHA and coverage before discovery claims. Reindex stale or missing graphs or use an explicit tracked-file fallback; search absence alone is not proof.
- Never assign to PowerShell automatic or reserved variables, case-insensitively; use purpose-specific variable names.

### Long-Running Validation Gate

- Treat `release`, `nightly-full`, a full matrix, or at least 120 seconds expected or observed wall time as long-running.
- Finish tracked mutations and focused validation, then bind the exact command to a clean immutable commit.
- Dispatch one read-only external task using the least expensive capable profile; write only ignored validation artifacts and do not repair the subject.
- Use a callback or one parent event wait. Do not poll.
- Require one schema-valid terminal report bound to the exact task, commit provenance, content subject, command, duration, outcome, and evidence.
- Timeout, interruption, drift, missing evidence, cleanup failure, or blocked execution never becomes `passed`.

### Portable Test Fixture Acceleration

- The portable baseline is zero configuration. Only tests explicitly classified in `.ai/scripts/test-fixture-classifications.json` as disposable fixture I/O may consume `AI_CONTEXT_TEST_TMP_ROOT`.
- The setting is one explicit opt-in fixture root. Do not discover storage, change global `TEMP` or `TMP`, or route durability-storage or platform-filesystem semantics through it.
- Re-run preflight at execution time, create one unique contained run directory, and clean up only that verified directory. Invalid, unsafe, or unwritable roots fail before material fixtures.
- Keep diagnostics path-free. A WSL `/mnt/*` performance warning is advisory; it never changes test outcomes or silently selects another root.
- Compare default and accelerated modes with the same tracked test profile on one commit and host. Use at least three runs for a median and label cold or warm conditions explicitly.
- See `.dev/guides/implementation-guides/PORTABLE-TEST-FIXTURE-ACCELERATION-GUIDE.md` for local and manual CI usage.

## CLI And Runtime Boundaries

- After higher-priority policy selects cross-boundary CLI execution, load `.ai/assets/shared/CLI-EXECUTION-ROUTING-CONTRACT.md`.
- The optional binding may exist only at `.dev/ai-context/local/cli-execution-routing.yaml`; it must remain ignored, untracked, unstaged, secret-free, and outside package or provenance truth.
- Never create or update it implicitly. Verify recovery first, then disclose the exact path, fields, `create/merge/replace` action, and secret exclusion; decline or no answer writes nothing.
- Do not silently substitute a model, provider, execution surface, credential boundary, or permission. Static configuration does not prove current-session execution.

## Stop Conditions

Stop before mutation when authorization is missing or contradictory, authority cannot be resolved, the write exceeds scope, target-owned truth lacks reconciliation, required evidence cannot be proven, the fixed subject drifted, or a new owner-sensitive decision is required.

Repairable implementation, test, or CI failures inside authorized scope are not owner checkpoints by themselves.

## Navigation And Language

Use indexes only when needed:

- `.ai/INDEX.MD`: reusable agent-facing assets.
- `.dev/INDEX.md`: project knowledge and current records.
- `.dev/standards/INDEX.MD`: standards navigation.
- `.dev/guides/ai-collaboration-guides/INDEX.MD`: human-facing explanations, not default execution context.
- `.agents/skills/README.md` and `.claude/skills/README.md`: wrapper inventories.

### Root Entry Files

| Path | Responsibility |
| --- | --- |
| `README.md` | Human-facing Traditional Chinese repository entry |
| `README.en.md` | English repository entry |
| `AGENTS.md` | Canonical English root collaboration guide |
| `AGENTS.zh-TW.md` | Traditional Chinese translation |
| `CLAUDE.md` | Thin Claude project-memory adapter |

- Agent-facing execution contracts should prefer English.
- Human-facing guides may use Traditional Chinese (Taiwan) or English.
- Keep `AGENTS.zh-TW.md` structurally and normatively aligned; it must not add or remove rules.
