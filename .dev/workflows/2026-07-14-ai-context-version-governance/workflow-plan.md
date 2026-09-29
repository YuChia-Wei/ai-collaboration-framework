# AI Context Version Governance And Upgrade Capability

## Template Metadata

- `template_id`: `ai-context-governance-maintenance-workflow-plan`
- `template_version`: `1.2.0`
- `created_at`: `2026-07-10T18:22:49+08:00`
- `updated_at`: `2026-07-13T23:11:56+08:00`

## Workflow Metadata

- `workflow_id`: `2026-07-14-ai-context-version-governance`
- `workflow_kind`: `ai-context-maintenance`
- `owner_skill`: `ai-context-governance`
- `branch`: `codex/2026-07-14-ai-context-version-governance`
- `base_branch`: `main`
- `branch_segment`: `1`
- `status`: `completed`
- `current_phase`: `closed`
- `artifact_root`: `.dev/workflows/2026-07-14-ai-context-version-governance`
- `created_at`: `2026-07-14T21:46:14+08:00`
- `updated_at`: `2026-07-14T22:07:36+08:00`
- `template_source`: `.ai/assets/skills/ai-context-governance/templates/ai-context-maintenance-workflow-plan-template.md`
- `template_version`: `1.2.0`

## Objective And Scope

- Problem statement: repository tags identify two framework snapshots, but no canonical policy defines version meaning, release records, target-repository provenance, or a safe upgrade process. Commit SHA alone is fragile as a human discovery key, while copying a newer framework over a target can overwrite target truth or import runtime history.
- Authorized remediation scope: define immutable SemVer tags and release artifacts; introduce a target provenance manifest; create an `ai-context-upgrader` skill and thin Codex/Claude wrappers; add a read-only Git-backed comparison tool; document three-way reconciliation; add fail-closed structural validation and GWT tests.
- Exclusions: moving `v0.1.0` or `v0.2.0`; tagging or publishing `v0.3.0`; upgrading an external target repository; scanning product `src/` or `tests/`; copying completed workflows or assessments into a target; depending on codebase-memory-mcp or another external index as evidence.
- Completion criteria: current and target versions are discoverable without relying on a mutable SHA; releases state compatibility and migration impact; a target can record source version and local overrides; the upgrade skill preserves target-owned truth and excludes history; comparison output is reproducible from Git; wrappers, indexes, validators, tests, and repository gates pass.

## Design Decisions

1. Existing annotated tags are immutable historical anchors: `v0.1.0` at `69c285077708dfb96ee49bb39258aec83eb7f1a9` and `v0.2.0` at `9abc75b543ae201865c1e119d29fac2bcd2f4542`.
2. The first fully governed release will be a future `v0.3.0`; this workflow may prepare its release record but cannot create the tag before merge and explicit authorization.
3. `repo-structure-sync` owns first-copy initialization. `ai-context-upgrader` owns upgrades of an already initialized target with recorded provenance.
4. Upgrade analysis is a three-input reconciliation: previous framework version, new framework version, and current target state. Target-specific truth is never silently replaced.
5. Git objects and repository files are evidence. Knowledge graphs and code indexes may accelerate discovery but cannot establish completeness or truth.
6. The canonical skill package follows this repository's `skill.yaml` architecture. The generic skill-creator initializer is intentionally not used because it would generate a competing standalone `SKILL.md` package; its validation and forward-test requirements still apply.

## Proposed Artifact Contract

- Version policy: `.dev/standards/AI-CONTEXT-VERSION-POLICY.md`
- Release discovery: `releases/INDEX.MD`
- Per-release record: `releases/<version>/release.yaml`, `release-notes.md`, and `migration-guide.md`
- Target provenance template: `.ai/assets/skills/ai-context-upgrader/templates/ai-context-source-template.yaml`
- Installed target provenance: `.dev/AI-CONTEXT-SOURCE.yaml` in an initialized target repository; this framework source stores only the canonical template.
- Upgrade skill: `.ai/assets/skills/ai-context-upgrader/`
- Runtime wrappers: `.agents/skills/ai-context-upgrader/` and `.claude/skills/ai-context-upgrader/`
- Comparison tool: `.ai/scripts/compare-ai-context-versions.py`
- Tasks: `.dev/workflows/2026-07-14-ai-context-version-governance/tasks/`

## Finding Triage

| Finding | Severity | Owner | Disposition | Task | Validation |
| --- | --- | --- | --- | --- | --- |
| `AIVG-POLICY-001` | high | `ai-context-governance` | define version semantics, immutable tags, release lifecycle, and compatibility declarations | `AIVG-001` | policy and schema validation |
| `AIVG-PROVENANCE-001` | high | `ai-context-governance` | define target source and local-override manifest | `AIVG-002` | valid and invalid manifest GWT cases |
| `AIVG-UPGRADE-001` | high | `skill-creator` | create safe three-way upgrade skill and runtime routes | `AIVG-003` | wrapper validation and independent forward-test |
| `AIVG-TOOL-001` | medium | `ai-context-governance` | create deterministic read-only Git comparison | `AIVG-004` | classifier and CLI GWT tests plus real tag comparison |
| `AIVG-CLOSE-001` | low | `ai-context-governance` | reconcile indexes, gates, release readiness, and commits | `AIVG-005` | quick gate and Git-policy checks |

## Task Plan

| Task | Purpose | Status | Primary validation |
| --- | --- | --- | --- |
| `AIVG-001` | Establish SemVer, tag immutability, release records, and compatibility policy. | `completed` | Historical anchors and next-release lifecycle are unambiguous. |
| `AIVG-002` | Establish target provenance and local-override contracts. | `completed` | Schema rejects missing or ambiguous source identity. |
| `AIVG-003` | Create and route the `ai-context-upgrader` skill. | `completed` | Both wrappers validate and a fresh agent produces a safe plan. |
| `AIVG-004` | Implement and test deterministic version comparison and governance validation. | `completed` | GWT suites and real `v0.1.0..v0.2.0` comparison pass. |
| `AIVG-005` | Complete release bootstrap, documentation/index synchronization, and closeout. | `completed` | Full quick gate, workflow validator, diff and commit checks pass. |

## Validation Strategy

- Parse all YAML with PyYAML and validate release/provenance invariants.
- Use Given-When-Then test naming and scenario structure; do not use 3A terminology.
- Quick-validate both runtime wrappers.
- Run a bounded independent forward-test using a target with local collaboration and requirement overrides.
- Compare the real `v0.1.0` and `v0.2.0` Git trees without modifying the worktree.
- Run workflow and AI-context validators, `check-all.sh --quick`, and `git diff --check`.
- Verify every workflow commit has `Why`, `What`, `Validation`, `Workflow`, and the final OpenAI Codex co-author trailer.

## Release And Authorization Boundary

- `v0.1.0` and `v0.2.0` must not be moved, recreated, or deleted.
- `v0.3.0` is a candidate identifier only until the workflow is merged to `main`, all release metadata matches the merged commit, and the user explicitly authorizes tag creation.
- Push, merge, and tag publication remain outside current authorization.

## Resume Checkpoint

- Last completed action: completed the 11-check quick gate, reconciled release/workflow evidence, and closed every task.
- Current task: none; workflow completed.
- Exact next action: await explicit `--no-ff` merge authorization, then re-run post-merge validation before any explicit `v0.3.0` tag authorization.
- Validation already completed: 11/11 required quick checks; 10/10 version-governance GWT tests; 9/9 assessment GWT tests; 7/7 workflow implementation GWT tests; 47 analyzer tests; 2 configuration tests; both wrapper quick validations; AI-context, workflow, release, shell, YAML/JSON, and whitespace checks; real read-only tag comparison; independent forward-test pass after five contract corrections.
- Git state: workflow bootstrap `8656cf5`, AIVG-001 `5864017`, and AIVG-002 through AIVG-004 `1dd3c45` committed; final closure metadata is ready to commit.
- Branch history and checkpoint handoffs: segment 1 began locally on 2026-07-14.
- Blockers or unresolved decisions: none. Future `v0.3.0` tag creation requires a later explicit authorization after merge.

## Branch Lifecycle

| Segment | Branch | Base | Checkpoint Type | Commit | Remote / Target | Recorded At | Reason | Resume Branch / Action |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `codex/2026-07-14-ai-context-version-governance` | `main` | started | `9abc75b` | local | `2026-07-14T21:46:14+08:00` | Establish version governance and safe upgrade capability. | Continue `AIVG-001`. |
| 1 | `codex/2026-07-14-ai-context-version-governance` | `main` | completed | `pending closure commit` | local | `2026-07-14T22:07:36+08:00` | All planned governance, skill, tooling, release, and validation work passed. | Await explicit merge authorization. |
