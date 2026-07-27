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
- `current_phase`: `remediation`
- `artifact_root`: `.dev/workflows/2026-07-27-ai-execution-provenance-policy`
- `created_at`: `2026-07-27T08:39:34+08:00`
- `updated_at`: `2026-07-27T09:56:54+08:00`
- `template_source`: `.ai/assets/skills/ai-context-governance/templates/ai-context-maintenance-workflow-plan-template.md`
- `template_version`: `1.2.0`
- `release_target`: `v0.7.0`

## Objective And Scope

- Problem statement: recent Codex-assisted commits used the fixed trailer
  `OpenAI Codex (GPT-5)` even though the recorded authoring session resolved to
  `gpt-5.6-sol` with `high` reasoning effort in Default mode. The repository
  tells agents to use active runtime identity but provides fixed-model examples,
  validates only generic trailer syntax, and does not connect resolved session
  provenance to commit construction.
- Authorized remediation scope: apply the owner-approved common commit
  signature containing runtime, model, and reasoning effort; add only `model`
  and `reasoning_effort` to task execution provenance; define default fallback
  behavior; update validators, templates, provider fixtures, and guidance; and
  complete independent verification for the v0.7.0 workstream.
- Exclusions: do not rewrite historical commits; do not add surface, mode,
  available-tool, or used-tool fields; do not add a direct-mode-specific
  provenance contract; do not create a cross-tool settings file; do not alter
  provider account configuration.
- Completion criteria: fixed-model examples are removed; AI commit signatures
  consistently use `<runtime> (<model>, <reasoning_effort>)`; runtime values are
  preferred and missing values use the effective configured or documented
  client default without blocking the commit; tasks contain only the approved
  `model` and `reasoning_effort` additions; validators cover the contract; real
  or explicitly blocked provider fixtures are recorded; an independent
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

## Approved Policy Direction

1. Use one repository commit-signature shape across Codex, Claude, Copilot, and
   other supported runtimes:

   ```text
   Co-Authored-By: <runtime> (<model>, <reasoning_effort>) <noreply@provider-domain>
   ```

   Preserve the provider/runtime name and provider noreply domain while making
   model and reasoning effort visible in the same parenthesized format.
2. Resolve signature and task values from the active session when available.
   When either value is unavailable, fill it from the effective configured
   default after applying the client's documented precedence; if no explicit
   configuration exists, use the client's documented built-in default. Missing
   runtime metadata does not globally block a commit.
3. Add only `model` and `reasoning_effort` to task artifacts. Do not add source,
   surface, mode, tool, or evidence-reference fields as part of this workflow.
4. Do not add direct-mode-specific provenance rules. Direct operations continue
   to rely on the common commit signature.
5. Do not add tool inventory or tool-use recording in this workflow.
6. Do not create a cross-tool custom settings file. Provider-native settings
   remain the configuration authorities.
7. Assign the workflow to v0.7.0.

## Owner Decision Register

| Decision | Owner-approved decision | Evidence | Status |
| --- | --- | --- | --- |
| `AEP-DEC-001` Git identity | Include the actual model and reasoning effort in a common Claude/Copilot/Codex-style message signature: `<runtime> (<model>, <reasoning_effort>)`. | Owner response on 2026-07-27. | `approved` |
| `AEP-DEC-002` Missing evidence | Fill missing model or reasoning values from the applicable default and do not impose a global commit block. | Owner response on 2026-07-27. | `approved` |
| `AEP-DEC-003` Task storage | Add only `model` and `reasoning_effort` to tasks; rely on the commit signature for direct operations and add no direct-mode-specific contract. | Owner response on 2026-07-27. | `approved` |
| `AEP-DEC-004` Tool evidence | Do not add tool availability or tool-use fields in this workflow. | Owner response on 2026-07-27. | `approved` |
| `AEP-DEC-005` Cross-tool policy file | Do not create a cross-tool custom settings file. | Owner response on 2026-07-27. | `approved` |
| `AEP-DEC-006` Release assignment | Assign this workflow to v0.7.0. | Owner response on 2026-07-27. | `approved` |
| `AEP-DEC-007` Task migration | Require the two fields on new tasks; add them to unfinished historical tasks when next updated; do not backfill completed historical tasks. | Owner accepted the recommended boundary on 2026-07-27. | `approved` |
| `AEP-DEC-008` Sub-agent attribution | Add another co-author only when a sub-agent materially produced committed content, and mark its runtime as `Sub-Agent`; do not credit read-only discovery, review, or advice. | Owner response on 2026-07-27. | `approved` |
| `AEP-DEC-009` Reasoning labels | Preserve the provider/runtime value without cross-provider replacement or arbitrary normalization. | Owner response on 2026-07-27. | `approved` |

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
| Git commit policy and examples | Require `<runtime> (<model>, <reasoning_effort>)` and document active-session then default fallback resolution. |
| Commit policy schema and validator | Validate the common signature shape and required values rather than accepting a generic name. |
| Workflow tasks | Add only `model` and `reasoning_effort`; do not add surface, mode, tools, or source fields. |
| Codex CLI and Desktop | Document how active-session values and effective defaults are obtained for the common signature. |
| Claude Code and Desktop | Verify how native attribution can coexist with or produce the approved common signature before enforcement. |
| GitHub Copilot | Verify CLI, IDE, and cloud-agent attribution behavior before enforcing the common signature. |
| Fixtures | Use real provider outputs where available and record unsupported native formatting explicitly. |

## Stages And Checkpoints

1. Confirm owner decisions and freeze the exact policy boundary.
2. Update the smallest coherent attribution and execution-provenance contract.
3. Add provider fixtures, validator coverage, and target-facing guidance.
4. Run repository validation and request an independent post-remediation audit.
5. Reconcile findings, publish the remediation report, commit, and close.

## Task Plan

| Task | Purpose | Status |
| --- | --- | --- |
| `AEP-001` | Preserve evidence and obtain owner decisions for attribution, unavailable behavior, storage, tools, custom settings, and release assignment. | `completed` |
| `AEP-002` | Apply the approved policy and provenance contract changes without introducing a duplicate settings authority. | `completed` |
| `AEP-003` | Add provider fixtures, validator coverage, and runtime-specific guidance. | `in_progress` |
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

- Last completed action: recorded owner approval for `AEP-DEC-007` through
  `AEP-DEC-009`, implemented the repository-created local commit signature,
  added the prospective two-field task contract, and completed focused tests.
- Current task: `AEP-003`.
- Exact next action: capture or classify real Codex, Claude, and Copilot
  attribution fixtures and document how each client produces or preserves the
  approved signature without rewriting provider-native commits.
- Validation already completed: planning evidence was cross-checked against
  recent session records, current policy text, schema validation behavior, and
  current provider documentation; workflow artifact validation, four-task JSON
  parsing, the six backlog release-contract tests, and `git diff --check` pass.
- Git state: branch `codex/2026-07-27-ai-execution-provenance-policy` from
  `main`; the validated planning checkpoint is local and has not been
  transported.
- Branch history and checkpoint handoffs: none.
- Blockers or unresolved decisions: no policy-direction decision remains.
  Claude and Copilot native fixture availability may constrain client-specific
  enforcement and must be reported rather than fabricated.

## Branch Lifecycle

| Segment | Branch | Base | Checkpoint Type | Commit | Remote / Target | Recorded At | Reason | Resume Branch / Action |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `codex/2026-07-27-ai-execution-provenance-policy` | `main` | local planning | resolved from branch history | local | `2026-07-27T08:39:34+08:00` | Preserve the owner-requested policy correction plan before remediation. | Resolve `AEP-DEC-001` through `AEP-DEC-006`. |
| 1 | `codex/2026-07-27-ai-execution-provenance-policy` | `main` | local owner-decision checkpoint | resolved from branch history | local | `2026-07-27T09:24:09+08:00` | Preserve the approved policy boundary and v0.7.0 assignment before canonical remediation. | Inventory task templates and provider fixtures, then execute `AEP-002`. |
| 1 | `codex/2026-07-27-ai-execution-provenance-policy` | `main` | local policy-remediation checkpoint | resolved from branch history | local | `2026-07-27T09:56:54+08:00` | Apply AEP-DEC-001 through AEP-DEC-009 to local commit and task contracts. | Capture provider fixtures and guidance under `AEP-003`. |
