# AGENTS.md

[Traditional Chinese](AGENTS.zh-TW.md)

This file is the canonical English root collaboration guide. `AGENTS.zh-TW.md` is its Traditional Chinese (Taiwan) translation.

## Temporary Source Redesign Override

For source-repository work explicitly assigned to program #322, read
[the temporary execution override](.dev/standards/FRAMEWORK-REDESIGN-EXECUTION-OVERRIDE.md)
before applying the rules below. Under the owner's 2026-09-24 U001 amendment,
short, clearly bounded work may use coordinator-dispatched sub-agents with the
least expensive capable model/effort; a new conversation or Astra is not required.
Larger or multi-stage implementation Issues retain independent `gpt-6-astra` /
`ultra` conversations. Use the assigned RAM-disk worktree and return local commits
to the coordinator before first push; executors do not create further tasks or
delegate without a coordinator assignment. Unrestored legacy/native/release verification outside the adopted source scope
remains `deferred-by-owner` until its separately selected restoration decision. This exception is
source-only; unrelated security, ownership, credential and publication boundaries
remain in force.

## Source Development Rules

Read [the source development policy](.dev/standards/SOURCE-DEVELOPMENT-POLICY.md)
for the owner-adopted 2026-10-02 cutover and exact ordinary-source scope. Its eight
rules replace conflicting ordinary-source aggregate, receipt, packet, lease and handoff
requirements below; conditional independent review and selected checks remain.
The temporary override and old mechanisms remain only for explicitly retained
legacy/native/release obligations. Release, support, credentials, protection and
downstream adoption retain their owners. No merge or date proves CI success.

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
- Sub-agents inherit the user's runtime model and reasoning effort. Do not automatically escalate model, effort, provider or cost because of a role name. Explain a needed escalation and obtain explicit user authorization for a visible separate task; runtime availability is not spending consent.

## Progressive Context Loading

1. Start with the request, current Git/worktree state, this file, and explicitly named Issues or artifacts.
2. Select one owning skill or policy, then load its canonical entry. A generated runtime entry may serve directly; reload its full source only for metadata, maintenance, or discrepancy resolution.
3. Expand only for an applicable phase, finding, file type, provider, decision, or execution boundary.
4. Do not preload `README.md`, all indexes, all standards, every skill reference, historical workflows, or assessment archives.
5. Do not broad-scan `src/`, `tests/`, `.dev/workflows/`, or `.dev/assessments/` unless scope requires it.
6. Verify material conclusions with Git-tracked evidence, current provider read-back, or repository-owned validators. No search result is not proof of absence.

## Task Routing

Use the original skill IDs in `.agents/skills/<skill-id>/SKILL.md` for Codex and `.claude/skills/<skill-id>/SKILL.md` for Claude. These generated entries and `.ai/core/skills/` are installed projections of editable product sources in `src/skills/`; select them through `.ai/custom/installation.json`. Do not edit generated installed files. The current distribution catalog has 18 skills, including the restored development orchestrator and optional `ai-context-init@0.2.0`. The `project-initialization` preset selects initialization separately; existing presets and this source project's 17-skill installation are unchanged. Installing the package supplies authoring resources, not initialized root documents. `standards-promotion@0.1.1-alpha.1` remains editable in `src/skills/` for independently copied experiments and is excluded from catalogs, presets and release products pending owner-selected validation; it is not an installed source-project route. Generated installation state is updated separately. Removed compatibility roots do not provide current executable routes.

| Need | Owning route |
| --- | --- |
| AI-context audit or comparison | `ai-context-auditor` |
| AI-context governance and reusable context maintenance | `ai-context-governance` |
| Architecture, GWT design, code review, diagnosis, or implementation | `ddd-ca-hex-architect` / `bdd-gwt-test-designer` / `code-reviewer` / `diagnostic-analyst` / `slice-implementer` / `local-change-implementer` |
| Requirements, specifications, problem frames, or selected compliance | `requirement-author` / `spec-author` / `problem-frame-author` / `spec-compliance-validator` |
| Decisions, lessons, local backlog, or pull requests | `adr-author` / `lesson-author` / `local-backlog` / `pr-author` |
| Multi-stage software development | `software-development-orchestrator` for stage selection and specialist handoffs; source `.dev/` policy and Issue authority own workflow records and integration |
| Initialization or upgrade of a previously published legacy package format | Retained source compatibility duty with no current portable or executable route; restore a verified source-owned procedure before execution. |
| Historical or exceptional source release closeout | `releases/` and source release policy; no portable installed skill route. |

For source work, `.dev/standards/` continues to own source policy, GitHub work authority, release governance, U001 and the P7 deferrals. Preserve the retained source duties explicitly: source assessment persistence and terminal records; source customization and policy reconciliation; legacy CBF/SWF intake and active records; the target-selected legacy .NET 100% gate and rule resolver, only when maintaining that legacy downstream format or target (not for this framework source or its own installation); and old published-format initialization, upgrade and recovery. Duty retention does not establish tool availability. The removed legacy roots and validators that still depend on them are unavailable until a verified source-owned route is restored; they do not restore removed runtime discovery entries.

- For AI-context placement or language changes, load `.dev/standards/AI-CONTEXT-BOUNDARY.md` and `.dev/standards/AI-CONTEXT-LANGUAGE-POLICY.md` only when applicable.
- For code review, load the installed `code-reviewer` entry and only its applicable route and finding references.
- `test-execution` has no required skill; resolve target-owned commands first.
- Direct execution remains valid. Classify delegation under `.dev/contracts/AGENT-EXECUTION-GUARDRAILS-CONTRACT.md`; load the role contract only when applicable. Static profile presence is not invocation evidence.

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
- Hosted source CI is required only for PRs selected by the source policy's native `src/**` and `tools/**` path filters. Other PRs need no source CI context; absence is not a pass. Separately selected release checks retain their own applicability.
- A content-addressed independent audit reports each gate as `re-executed`, `reused-with-proof`, `blocked`, `deferred`, or `not-applicable`; commit SHAs remain provenance rather than the validity key.

### Agent Execution Guardrails

- For new source development, use bounded delegation and conditional independent review under `.dev/standards/SOURCE-DEVELOPMENT-POLICY.md` and the source applicability override in `.dev/contracts/AGENT-EXECUTION-GUARDRAILS-CONTRACT.md`. Bind the immutable diff, acceptance criteria and governing rules; preserve one tracked writer per worktree and truthful evidence. Do not require legacy classifier, preflight, packet or lease machinery for this adopted source scope.
- For separately selected legacy or release obligations, classify actual risk under the guardrails contract; ordinary analysis and local edits may classify inline, while review preflight uses the validator. A terminal label alone does not require the full tier; short same-runtime independent read-only review of an isolated immutable ordinary change may use the bounded envelope. Authority, evidence-custody, security, release/adoption changes, external or long-running validation, shared mutable review or shared frozen work, and unknown risk require the full validated packet, immutable subject and machine-readable snapshot lease. One tracked writer per worktree remains mandatory in both tiers; a full lease requires explicit terminal release.
- For those separately selected legacy or release obligations, preflight the machine-readable review subject, criteria and authority before behavioral dispatch in either tier. Keep preparation failures, behavioral defects, environment failures and provider reconciliation distinct; retain prior attempts and rerun only affected checks under the existing evidence-reuse and retry rules.
- Keep formal acceptance-to-evidence ledgers where the acceptance contract requires them. Synthetic, mock, fixture, and unit evidence cannot satisfy an acceptance that requires actual execution.
- Retry only after a privacy-safe failure fingerprint and material state change. Attempt three or later requires new owner or workflow authorization.
- Verify code-graph index SHA and coverage before discovery claims. Reindex stale or missing graphs or use an explicit tracked-file fallback; search absence alone is not proof.
- Never assign to PowerShell automatic or reserved variables, case-insensitively; use purpose-specific variable names.

### Long-Running Validation Gate

- Before dispatch, classify a command as long-running when its profile is `release` or `nightly-full`, it selects a full package, compatibility, or history matrix, repository evidence predicts at least 120 seconds, or a prior comparable execution took at least 120 seconds. Use `.dev/standards/WORKFLOW-GATE-POLICY.md` for the execution contract.
- Finish tracked mutations and focused validation, then bind the exact command to a clean immutable commit.
- Dispatch one read-only external task using the least expensive capable profile; write only ignored validation artifacts and do not repair the subject.
- Use a callback or one parent event wait. Do not poll.
- Require one schema-valid terminal report bound to the exact task, commit provenance, content subject, command, duration, outcome, and evidence.
- Timeout, interruption, drift, missing evidence, cleanup failure, or blocked execution never becomes `passed`.

### Portable Test Fixture Acceleration

- The portable baseline is zero configuration. The legacy `AI_CONTEXT_TEST_TMP_ROOT` acceleration route is unavailable in this source layout because its classifier and tooling were removed; do not activate it from historical instructions.
- The setting is one explicit opt-in fixture root. Do not discover storage, change global `TEMP` or `TMP`, or route durability-storage or platform-filesystem semantics through it.
- Re-run preflight at execution time, create one unique contained run directory, and clean up only that verified directory. Invalid, unsafe, or unwritable roots fail before material fixtures.
- Keep diagnostics path-free. A WSL `/mnt/*` performance warning is advisory; it never changes test outcomes or silently selects another root.
- Compare default and accelerated modes with the same tracked test profile on one commit and host. Use at least three runs for a median and label cold or warm conditions explicitly.
- Current source tests follow `.dev/standards/SOURCE-DEVELOPMENT-POLICY.md`; the retired acceleration route requires a separately selected compatible revision.

## CLI And Runtime Boundaries

- After higher-priority policy selects cross-boundary CLI execution, load `.dev/contracts/CLI-EXECUTION-ROUTING-CONTRACT.md`.
- The optional binding may exist only at `.dev/ai-context/local/cli-execution-routing.yaml`; it must remain ignored, untracked, unstaged, secret-free, and outside package or provenance truth.
- Never create or update it implicitly. Verify recovery first, then disclose the exact path, fields, `create/merge/replace` action, and secret exclusion; decline or no answer writes nothing.
- Do not silently substitute a model, provider, execution surface, credential boundary, or permission. Static configuration does not prove current-session execution.

## Stop Conditions

Stop before mutation when authorization is missing or contradictory, authority cannot be resolved, the write exceeds scope, target-owned truth lacks reconciliation, required evidence cannot be proven, the fixed subject drifted, or a new owner-sensitive decision is required.

Repairable implementation, test, or CI failures inside authorized scope are not owner checkpoints by themselves.

## Documentation Ownership

- Editable reusable resources belong in `src`; resources required by a framework capability must be included there or declared as knowledge dependencies.
- `.dev` owns this project's records, policies and collaboration; `docs` owns product documentation. Source and installed copies may coexist because this repository develops and uses the framework.
- Prepare reusable resources in source before separately selected self-installation/upgrade. Remove obsolete documents without experience-transfer value; preserve existing `.dev/design`, `.dev/assessments`, `.dev/requirement`, `.dev/adr` and `.dev/workflows` history in this cleanup.

## Navigation And Language

Use indexes only when needed:

- `.ai/INDEX.MD`: generated installed content and source-tooling data.
- `.dev/INDEX.md`: project knowledge and current records.
- `.dev/standards/INDEX.MD`: standards navigation.
- `docs/`: human-facing product manuals; `.dev/guides/` explains source-project work and experience.
- `.agents/skills/README.md` and `.claude/skills/README.md`: installed skill inventories.

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
