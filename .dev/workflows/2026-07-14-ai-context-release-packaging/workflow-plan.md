# AI Context Deterministic Packaging And Automated Release

## Template Metadata

- `template_id`: `ai-context-governance-maintenance-workflow-plan`
- `template_version`: `1.2.0`
- `created_at`: `2026-07-10T18:22:49+08:00`
- `updated_at`: `2026-07-13T23:11:56+08:00`

## Workflow Metadata

- `workflow_id`: `2026-07-14-ai-context-release-packaging`
- `workflow_kind`: `ai-context-maintenance`
- `owner_skill`: `ai-context-governance`
- `branch`: `codex/2026-07-14-ai-context-release-packaging`
- `base_branch`: `main`
- `branch_segment`: `1`
- `status`: `completed`
- `current_phase`: `closed`
- `artifact_root`: `.dev/workflows/2026-07-14-ai-context-release-packaging`
- `created_at`: `2026-07-14T23:39:38+08:00`
- `updated_at`: `2026-07-15T07:53:30+08:00`
- `template_source`: `.ai/assets/skills/ai-context-governance/templates/ai-context-maintenance-workflow-plan-template.md`
- `template_version`: `1.2.0`

## Objective And Scope

- Problem statement: previous installation copied whole framework directories after manually deleting target context, committed the deletion as a rollback point, and relied on `repo-structure-sync` to discover source backlog/history and rewrite target truth. That process was auditable but packaging boundaries, removals, renames, file ownership, checksums, and release publication were not machine-readable or automated.
- Authorized remediation scope: create one full `dotnet-backend` distributable profile; deterministic ZIP and tar.gz archives; package/file/migration manifests; dry-run-first safe application; public root templates; derived Traditional Chinese translation; runtime-specific low-cost translator agents; candidate and tag-triggered GitHub Actions; release-note assembly; historical baseline extensibility; validation and installation fixtures.
- Exclusions: creating or pushing a tag; publishing a GitHub Release during this workflow; splitting universal core from the .NET profile; copying source workflow, assessment, backlog, or release instances into targets; product source review; destructive replacement of target-modified files; hard-coding ignored local `.codex/config.toml` settings into a package.
- Completion criteria: a candidate `v0.3.0` package can be built reproducibly from a Git commit; ZIP and tar.gz contain identical payloads; every file has ownership and SHA-256 metadata; add/replace/remove/rename decisions fail safe; public root entries do not leak source-repository truth; three runtime translator adapters route to one canonical prompt; candidate and tag-triggered workflows validate; a disposable target install and upgrade pass.

## Confirmed User Decisions

1. Release cadence and version remain user-controlled: the user creates the immutable tag; a tag-triggered GitHub Action packages and publishes the Release automatically.
2. The initial release remains one complete `dotnet-backend` profile. Profile splitting is deferred until context boundaries are mature enough.
3. Packaging must enable safe automation. A raw whole-tree overwrite is not an acceptable primary installer because the user can already perform it manually.
4. Translation work must use a low-cost sub-agent and must not consume the main high-cost context when a bounded translator is sufficient.

## Design Decisions

### Package Envelope

Produce both `ai-context-dotnet-backend-v<version>.zip` and `.tar.gz` from one normalized staging tree:

```text
ai-context-dotnet-backend-v<version>/
  INSTALL.md
  requirements.txt
  metadata/
    package.yaml
    files.yaml
    migration.yaml
    SHA256SUMS.txt
  payload/
    ... distributable framework files ...
```

- Use a canonical allowlist, not a whole-tree archive with ad hoc exclusions.
- Normalize file order, timestamps, permissions, path separators, and archive metadata for deterministic output.
- Package metadata belongs to the envelope; it is not copied as target project truth.
- `.dev/AI-CONTEXT-SOURCE.yaml` is written only after target validation succeeds.

### Public Root Entries And Translation

- The source repository's active `AGENTS.md`, translation, and README are not public templates.
- `repo-structure-sync` owns minimal public `AGENTS.md`, `CLAUDE.md`, and README templates.
- The package installs the English template. After target-specific English `AGENTS.md` is finalized, a bounded translator produces `AGENTS.zh-TW.md` as a derived human review artifact.
- Do not package a stale pretranslated `AGENTS.zh-TW.md` template. Add the reciprocal translation link only when the derived file exists.
- Rename the source repository translation from `agents.zh-tw.md` to `AGENTS.zh-TW.md` and update exact-case references.

### Translator Agent Portability

Keep one runtime-neutral canonical role under `.dev/agents/`; runtime adapters remain thin:

| Runtime | Project agent location | Format | Model policy |
| --- | --- | --- | --- |
| Codex | `.codex/agents/<name>.toml` | TOML with `name`, `description`, `developer_instructions` | pin or select the current documented lower-cost model and validate availability; never distribute local approval/sandbox defaults |
| Claude Code | `.claude/agents/<name>.md` | Markdown with YAML frontmatter | use the lower-cost `haiku` alias unless the target explicitly overrides it |
| GitHub Copilot | `.github/agents/<name>.agent.md` | Markdown with YAML frontmatter | model is configurable but account availability varies; require an explicit low-cost selection or fail the translation handoff closed |

The canonical prompt limits writes to the requested translation, preserves Markdown structure, links, code, paths, IDs, normative strength, and Taiwan Traditional Chinese terminology, and returns a parity summary. The main agent validates output; the translator does not declare governance completion.

Official format evidence:

- Codex custom agents: <https://learn.chatgpt.com/docs/agent-configuration/subagents.md>
- Claude Code project subagents: <https://code.claude.com/docs/en/sub-agents>
- GitHub Copilot custom agents: <https://docs.github.com/en/copilot/reference/custom-agents-configuration>
- GitHub Copilot instruction support: <https://docs.github.com/en/copilot/reference/custom-instructions-support>

### Safe Migration Operations

`files.yaml` records path, SHA-256, ownership (`framework-managed`, `target-template`, or `target-owned`), and installation behavior. `migration.yaml` records explicit rename and compatibility operations.

- Add only when the target path is absent; otherwise reconcile.
- Replace only when target SHA-256 equals the previous framework SHA-256.
- Remove only framework-managed paths whose target SHA-256 equals the previous framework SHA-256.
- Rename only when the old hash matches and the destination is absent.
- Never automatically overwrite or delete target templates or target-owned truth.
- Default to dry-run. Require a clean Git worktree and record the starting commit before apply.
- Run `repo-structure-sync` after initial application; run `ai-context-upgrader` for versioned upgrades.

### GitHub Actions Publication Boundary

- Candidate workflow: manual/PR execution, build and validate archives, upload Actions artifacts only.
- Publish workflow: trigger only from a user-created `v*` tag, validate the governed release record, build from the tag, create a draft Release, upload archives/checksums, assemble full notes, then publish.
- Use minimum `contents: write` only for the publish job and a protected release environment where available.
- Never move or recreate a tag. Make reruns idempotent against an existing draft/release.

## Historical Baseline Decision

- Commit `ac2e2937b5209ece93e104c4a389a15e164c0d1b` exists, was authored at `2026-05-23T22:59:45+08:00`, and predates `ai-context-governance`; it is a credible early installed baseline candidate.
- Do not create a tag or release record until the user confirms the installed commit.
- The packaging schema must allow a retrospective baseline to be added later and must be able to generate old-file SHA-256 data directly from an immutable tag.
- Current version validation accepts `vMAJOR.MINOR.PATCH` but not prerelease suffixes. Prefer future retrospective `v0.0.1`; supporting `v0.0.1-preview[.N]` requires a deliberate SemVer schema/validator change and is not assumed here.
- `REL-v0.3.0` must not claim `v0.0.1` compatibility until that tag and baseline manifest exist. Existing `v0.1.0` remains the minimum governed source version for now.

## Task Plan

| Task | Purpose | Status | Primary validation |
| --- | --- | --- | --- |
| `AIPKG-001` | Define distributable profile, ownership classes, envelope, deterministic rules, and source-history exclusions. | `completed` | Every included/excluded category has one canonical disposition. |
| `AIPKG-002` | Add public root templates, rename the source translation, and add canonical/runtime translator agents. | `completed` | Exact-case links pass; translation adapters load and preserve one source of truth. |
| `AIPKG-003` | Implement deterministic package builder and package/file/checksum manifests. | `completed` | Repeated builds have identical digests and ZIP/tar payload parity. |
| `AIPKG-004` | Implement dry-run-first installation/upgrade planning for add, replace, remove, rename, and reconcile. | `completed` | Modified target files are never silently overwritten or deleted. |
| `AIPKG-005` | Add candidate and user-tag-triggered GitHub Actions with draft-to-published release behavior. | `completed` | Workflow lint/schema checks and local command parity pass. |
| `AIPKG-006` | Add GWT fixtures for clean install, legacy baseline, normal upgrade, local modification, removal, rename, and failures. | `completed` | All scenario matrices pass in disposable Git repositories. |
| `AIPKG-007` | Prepare `REL-v0.3.0` packaging notes and future retrospective-baseline extension without creating tags. | `completed` | Release data remains planned/validated and makes no false publication claim. |
| `AIPKG-008` | Build and inspect a candidate package, run full gates, reconcile artifacts, and close. | `completed` | Candidate install/upgrade, quick gate, workflow, commit, and archive checks pass. |

## Validation Strategy

- PyYAML parsing and dedicated package/migration validators.
- GWT-named Python tests in disposable Git repositories; no product `src/` or `tests/` scan.
- Exact-case root entry checks for `AGENTS.md`, `AGENTS.zh-TW.md`, and `CLAUDE.md`.
- Runtime adapter schema checks for Codex TOML, Claude YAML frontmatter, and Copilot YAML frontmatter.
- Two builds from the same commit with byte-identical archives or documented container-format limits plus identical extracted payload digests.
- ZIP/tar extracted file list, content hashes, and normalized modes must match.
- Candidate install into an empty repo and upgrade from synthetic `v0.1.0`-based target with modified target truth.
- `check-all.sh --quick`, workflow/AI-context/version/package validation, and `git diff --check` before closure.

## Resume Checkpoint

- Last completed action: built `ai-context-dotnet-backend-v0.3.0` twice from Git commit `1a25eb023e69d85c32a7459e7a9dc749e30e5d26`, validated ZIP/tar parity and pinned runtime requirements, executed the packaged planner against a disposable clean target, and passed the complete required quick gate.
- Current task: none; workflow completed.
- Exact next action: merge with `--no-ff` only when authorized, rerun post-merge validation, then let the user create the version tag when ready.
- Validation already completed: two independent output directories produced identical per-format SHA-256; archive envelopes and sidecars passed; clean install and synthetic upgrade/preservation scenarios passed; required quick gate passed 12/12 with 47 analyzer and 2 configuration tests.
- Git state: `codex/2026-07-14-ai-context-release-packaging`; final workflow closeout commit pending.
- Branch history and checkpoint handoffs: segment 1 began locally on 2026-07-14.
- Blockers or unresolved decisions: none for workflow closure. Historical `v0.0.1` selection, merge, push, user-created `v0.3.0` tag, and hosted GitHub Release publication remain explicit external follow-up actions.

## Branch Lifecycle

| Segment | Branch | Base | Checkpoint Type | Commit | Remote / Target | Recorded At | Reason | Resume Branch / Action |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `codex/2026-07-14-ai-context-release-packaging` | `main` | started | `67b540c` | local | `2026-07-14T23:39:38+08:00` | Build safe deterministic packaging and automated tag-triggered publication. | Continue `AIPKG-001`. |
