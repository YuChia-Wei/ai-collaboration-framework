# AI Execution Provenance And Git Attribution Policy Correction

## Template Metadata

- `template_id`: `ai-context-governance-maintenance-workflow-plan`
- `template_version`: `1.2.0`
- `created_at`: `2026-07-10T18:22:49+08:00`
- `updated_at`: `2026-07-13T23:11:56+08:00`

## Workflow Metadata

- `workflow_id`: `2026-07-27-ai-execution-provenance-policy`
- `workflow_kind`: `ai-context-maintenance`
- `owner_skill`: `ai-context-governance`
- `branch`: `codex/2026-07-27-ai-execution-provenance-policy`
- `base_branch`: `main`
- `branch_segment`: `1`
- `status`: `in_progress`
- `current_phase`: `remediation-planning`
- `artifact_root`: `.dev/workflows/2026-07-27-ai-execution-provenance-policy`
- `created_at`: `2026-07-27T08:39:34+08:00`
- `updated_at`: `2026-07-27T08:39:34+08:00`
- `template_source`: `.ai/assets/skills/ai-context-governance/templates/ai-context-maintenance-workflow-plan-template.md`
- `template_version`: `1.2.0`
- `release_target`: `unassigned`

## Objective And Scope

- Problem statement: recent Codex-assisted commits used the fixed trailer
  `OpenAI Codex (GPT-5)` even though the recorded authoring session resolved to
  `gpt-5.6-sol` with `high` reasoning effort in Default mode. The repository
  tells agents to use active runtime identity but provides fixed-model examples,
  validates only generic trailer syntax, and does not connect resolved session
  provenance to commit construction.
- Authorized planning scope: preserve the diagnosis and define an executable
  correction plan covering provider-native attribution, stable Git identity,
  resolved execution provenance, surface and mode, tool evidence, validation,
  provider fixtures, and independent verification.
- Current authorization boundary: this turn authorizes workflow and planning
  artifacts only. It does not authorize canonical policy, template, wrapper, or
  validator remediation.
- Exclusions: do not rewrite historical commits; do not claim configured model
  defaults are runtime evidence; do not invent unavailable model, reasoning, or
  tool metadata; do not normalize Claude, Copilot, Codex, or other provider
  attribution without real provider fixtures; do not create a new cross-tool
  settings file unless an owner-approved enforcement requirement justifies it.
- Completion criteria: fixed-model examples are removed; provider-native
  attribution is preserved; Codex fallback attribution uses a stable runtime
  identity; exact model, reasoning effort, surface, mode, and tool evidence have
  an explicit source and unavailable behavior; configuration intent is distinct
  from resolved execution evidence; validators cover the contract; real or
  explicitly blocked provider fixtures are recorded; an independent
  post-remediation assessment verifies the result.

## Evidence Snapshot

| Evidence | Observation | Planning consequence |
| --- | --- | --- |
| Recent Codex session record | The authoring session resolved to `gpt-5.6-sol`, `high`, and Default mode. | Runtime/session evidence must be the preferred source for exact execution metadata. |
| Recent commit command | The command explicitly inserted `Co-Authored-By: OpenAI Codex (GPT-5)`. | The observed trailer was repository-generated, not evidence of an OpenAI-native attribution hook. |
| `.dev/standards/GIT-COMMIT-POLICY.md` | Fixed `GPT-5` examples coexist with a rule requiring active-environment identity. | Replace fixed model examples and separate attribution from provenance. |
| `.dev/standards/GIT-COMMIT-POLICY.yaml` | The trailer validator checks only a generic name and noreply-address shape. | Add semantic provenance validation instead of accepting any syntactically valid model label. |
| `.dev/standards/WORKFLOW-HANDOFF-POLICY.md` | Existing `runtime`, `model`, `reasoning_effort`, and `model_source` fields already define a partial provenance contract. | Extend and reuse the existing contract rather than creating a duplicate settings authority. |
| Provider documentation | Claude Code and Copilot CLI expose native attribution controls; current public Codex documentation exposes model/reasoning configuration but no equivalent documented commit-attribution control. | Keep provider adapters distinct and preserve provider-native behavior when available. |

## Policy Direction

1. Treat `Co-Authored-By` as contributor attribution, not complete execution
   provenance.
2. Preserve provider-native attribution. For a local Codex commit without a
   native trailer, prefer the stable identity
   `OpenAI Codex <noreply@openai.com>` and store exact execution details outside
   the identity string.
3. Record configured intent separately from resolved execution state. A config
   file, model alias, UI tier, or prior commit is not proof of the active model.
4. Extend the existing provenance contract with `surface`, `mode`,
   `tools_available`, `tools_used`, evidence timestamp/reference, and
   sub-agent provenance when applicable.
5. Accept exact model and reasoning values only from a declared evidence source
   such as `runtime-reported` or `provider-reported`. Use `unavailable` without
   invention when the client cannot expose them.
6. Keep detailed provenance in workflow/checkpoint evidence. Define a compact
   direct-mode representation only if commits without workflow artifacts need
   the same assurance level.
7. Do not add a repository-wide cross-tool settings file by default. Reconsider
   one only for an approved model allowlist, minimum reasoning requirement, or
   mechanically enforced unavailable behavior.

## Owner Decision Register

| Decision | Recommended default | Why it requires owner confirmation | Status |
| --- | --- | --- | --- |
| `AEP-DEC-001` Git identity | Stable runtime identity for Codex; preserve native Claude/Copilot trailers. | This changes the canonical meaning and presentation of AI co-authorship. | `pending` |
| `AEP-DEC-002` Missing evidence | Record `unavailable`; fail only where a workflow explicitly requires exact provenance. | A global fail-closed rule could block clients that do not expose model or effort. | `pending` |
| `AEP-DEC-003` Direct-mode storage | Use compact commit trailers only when no workflow/checkpoint artifact exists. | This controls commit verbosity and evidence availability for small changes. | `pending` |
| `AEP-DEC-004` Tool evidence | Require `tools_used`; keep `tools_available` optional unless needed for a handoff or audit. | Full availability lists are dynamic and may be noisy, while actual use is materially relevant. | `pending` |
| `AEP-DEC-005` Cross-tool policy file | Do not create one in this workflow unless enforcement requirements are approved. | A second settings authority can drift from provider-native configuration. | `pending` |
| `AEP-DEC-006` Release assignment | Keep `release_target: unassigned` until the owner explicitly assigns this work to `v0.7.0` or another release. | Workflow authorization does not itself authorize roadmap or release scope. | `pending` |

## Artifact Contract

- Baseline evidence: this plan's evidence snapshot and repository/session records
  referenced during `AEP-001`; no standalone baseline assessment is created by
  the planning-only authorization.
- Remediation report: `.dev/workflows/2026-07-27-ai-execution-provenance-policy/reports/remediation-report.md`
- Verification assessment: to be assigned and created by `ai-context-auditor`
  after remediation.
- Tasks: `.dev/workflows/2026-07-27-ai-execution-provenance-policy/tasks/`

## Planned Contract Surface

| Surface | Planned treatment |
| --- | --- |
| Git commit policy and examples | Remove fixed-model examples; distinguish provider-native attribution, stable runtime identity, and exact provenance. |
| Commit policy schema and validator | Validate required semantic fields and evidence sources, not only trailer syntax. |
| Workflow handoff provenance | Extend the existing contract for surface, mode, available/used tools, and sub-agent execution. |
| Codex CLI and Desktop | Document configuration intent, session overrides, resolved runtime checks, mode, and the absence of a documented native trailer control. |
| Claude Code and Desktop | Preserve Claude Code attribution; distinguish Claude Desktop chat from the client or MCP tool that actually performs Git operations. |
| GitHub Copilot | Preserve CLI-native `includeCoAuthoredBy`; keep CLI, IDE, and cloud-agent execution surfaces distinct. |
| Fixtures | Use real provider outputs where available; mark unavailable fixtures as blocked instead of synthesizing identities. |

## Stages And Checkpoints

1. Confirm owner decisions and freeze the exact policy boundary.
2. Update the smallest coherent attribution and execution-provenance contract.
3. Add provider fixtures, validator coverage, and target-facing guidance.
4. Run repository validation and request an independent post-remediation audit.
5. Reconcile findings, publish the remediation report, commit, and close.

## Task Plan

| Task | Purpose | Status |
| --- | --- | --- |
| `AEP-001` | Preserve evidence and obtain owner decisions for attribution, unavailable behavior, storage, tools, custom settings, and release assignment. | `in_progress` |
| `AEP-002` | Apply the approved policy and provenance contract changes without introducing a duplicate settings authority. | `pending` |
| `AEP-003` | Add provider fixtures, validator coverage, and runtime-specific guidance. | `pending` |
| `AEP-004` | Validate, obtain independent verification, reconcile results, and close the workflow. | `pending` |

## Validation Plan

- Parse every JSON and YAML artifact changed by the workflow.
- Run `.ai/scripts/validate-workflow-artifacts.py` after every workflow-state
  change.
- Run focused commit-policy and handoff validator tests introduced or affected
  by remediation.
- Run `.ai/scripts/validate-git-commits.py` against the workflow commit range.
- Run `git diff --check`.
- Require an independent `ai-context-auditor` post-remediation assessment before
  closure.

## Resume Checkpoint

- Last completed action: created the dedicated branch and durable correction
  plan without changing canonical policy.
- Current task: `AEP-001`.
- Exact next action: obtain owner decisions `AEP-DEC-001` through
  `AEP-DEC-006`; do not begin `AEP-002` before those decisions are recorded.
- Validation already completed: planning evidence was cross-checked against
  recent session records, current policy text, schema validation behavior, and
  current provider documentation. Artifact validation remains to be run after
  creation.
- Git state: branch `codex/2026-07-27-ai-execution-provenance-policy` from
  `main`; the validated planning checkpoint is local and has not been
  transported.
- Branch history and checkpoint handoffs: none.
- Blockers or unresolved decisions: `AEP-DEC-001` through `AEP-DEC-006`.

## Branch Lifecycle

| Segment | Branch | Base | Checkpoint Type | Commit | Remote / Target | Recorded At | Reason | Resume Branch / Action |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `codex/2026-07-27-ai-execution-provenance-policy` | `main` | local planning | resolved from branch history | local | `2026-07-27T08:39:34+08:00` | Preserve the owner-requested policy correction plan before remediation. | Resolve `AEP-DEC-001` through `AEP-DEC-006`. |
