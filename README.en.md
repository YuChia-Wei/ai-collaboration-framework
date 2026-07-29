# AI Collaboration Knowledge Base and .NET Backend Context Framework

[繁體中文](README.md)

This file is the English translation of the canonical Traditional Chinese (Taiwan) human-facing repository identity in `README.md`.

This repository is the source for a portable AI collaboration framework. It brings together software-development practices, reusable Agent context, skills, sub-agent prompts, and collaboration workflows. It currently retains and develops specialized .NET / C# backend capability while separating cross-stack collaboration rules into reusable shared content.

It is not a product application or a sample system for one product. Its purpose is to help teams bring curated and validated AI collaboration capability into new or existing repositories, while letting each target repository establish its own facts from its code, configuration, and documentation.

> This root README is a human-facing guide to the source repository, not part of a portable release payload. Packages are built from an explicit allowlist that deliberately excludes root README files, so this source-repository introduction is never carried into a target repository.

## What This Repository Is

| This repository is | This repository is not |
| --- | --- |
| A reusable AI collaboration knowledge base and framework source | A complete implementation of one product, microservice, or Web API |
| A collection of shared software-development practices and specialized .NET backend capability | A mechanism for copying this source repository's requirements, specifications, workflows, or decisions into a target project as facts |
| A governed source for portable AI context release packages | A raw source snapshot to install into a target repository |

## Problems It Helps Solve

- Give AI Agents consistent collaboration rules, document locations, and validation expectations before work begins.
- Organize requirements, specifications, architecture, implementation, tests, reviews, and handoffs into routable skills and workflows.
- Separate knowledge that is reusable across repositories from facts that only a target repository can establish, preventing historical-project context from contaminating a new project.
- Retain .NET backend implementation, design, and review experience so discussions of DDD, Clean Architecture, CQRS, and message-driven backends start from a consistent baseline.

## When It Fits

This repository is useful for teams and individuals who want a maintainable AI collaboration practice, especially when they:

- introduce durable AI Agent context into a new or existing repository;
- provide .NET / C# backend architecture and implementation conventions to multiple Agents;
- need clear ownership and handoff boundaries for requirements, specifications, implementation, tests, and code review; or
- want to preserve portable framework rules without overwriting a target repository's business, architecture, or operations facts.

## Quick Navigation

| Goal | Start here |
| --- | --- |
| Understand the source repository's architecture and scope | [`.dev/ARCHITECTURE.md`](.dev/ARCHITECTURE.md) |
| Find available AI skills | [`.ai/assets/skills/README.MD`](.ai/assets/skills/README.MD) |
| Read human-facing collaboration guides | [`.dev/guides/ai-collaboration-guides/INDEX.MD`](.dev/guides/ai-collaboration-guides/INDEX.MD) |
| Help an Agent collaborate correctly in this source repository | [`AGENTS.md`](AGENTS.md) |
| Obtain or upgrade a portable framework release | [`.dev/releases/INDEX.MD`](.dev/releases/INDEX.MD) |

## Core Content

### Shared AI Collaboration Content

The shared content is intended for reuse across languages, frameworks, and product types. It covers:

- AI collaboration workflows, workflow gates, and handoff rules.
- Git commits, validation, requirements, specifications, ADRs, and review practices.
- Skill routing, sub-agent collaboration, and traceable execution boundaries.
- System and software architecture, along with conceptual guidance for DDD, Clean Architecture, and CQRS.

### .NET Backend Capability

The retained technology profile focuses on .NET / C# backend work, including:

- Backend project structures for Web APIs, workers, and consumers.
- Practical DDD, Clean Architecture, CQRS, Hexagonal Architecture, and message-driven backend guidance.
- Common backend combinations involving WolverineFx, Dapper, EF Core, PostgreSQL, RabbitMQ, and Kafka.
- Architecture design, implementation-slice, and code-review guidance for .NET backends.

## Main Directories

| Path | Purpose |
| --- | --- |
| `.ai/` | Agent-facing reusable AI context, canonical assets, scripts, and skill specs. |
| `.ai/assets/shared/` | Cross-stack prompt fragments, rules, and reusable materials. |
| `.ai/assets/tech-stacks/dotnet-backend/` | .NET C# backend Web API-specific context. |
| `.ai/assets/skills/` | Canonical skill specs and the skill registry. |
| `.ai/assets/sub-agent-role-prompts/` | Canonical source for sub-agent role prompts. |
| `.agents/skills/` | Codex and current-runtime skill wrappers. |
| `.claude/skills/` | Claude-compatible skill wrappers. |
| `.dev/` | Human-facing standards, guides, requirements, specifications, releases, and workflow records. |
| `.dev/releases/` | Release identities, compatibility declarations, and migration guidance. |
| `AGENTS.md` | Canonical root collaboration guide for Codex and general Agents. |
| `CLAUDE.md` | Thin Claude Code project-memory entry that imports `AGENTS.md`. |

## Installation and Upgrade

Obtain the appropriate portable AI context package from a published release instead of copying this entire source repository. A package is a versioned framework payload, not an overwrite snapshot of the whole repository.

| Target state | Correct flow |
| --- | --- |
| First framework adoption in an empty or existing repository | Use the package planner described in **Clean installation**, then run `ai-context-init`. |
| Initialized target with credible provenance and a release-supported migration route | Use the package planner described in **Version upgrade**, then run `ai-context-upgrader`. |
| Unknown source version, incomplete provenance, or an unsupported version gap | Stop automatic upgrade; use manual baseline reconciliation or a clean-install-style adoption. Never guess the previous version. |

### Clean installation

#### 0. Prepare the correct directories and evidence

Extract the downloaded ZIP or tar.gz **outside the target repository**. `PACKAGE_ROOT` means the extracted envelope root that contains `requirements.txt`, `metadata/`, and `payload/`; it is not the directory that contains the archive file.

```text
~/gitproj/
├── ai-context-package-0.7.0/
│   └── ai-context-dotnet-backend-v0.7.0/  # PACKAGE_ROOT
└── my-project/                            # TARGET_ROOT
```

Do not extract the package directly into `my-project`, and do not copy the `payload/` files one by one. Either action bypasses checksums, package selection, reconciliation, and the application receipt, and may place envelope metadata in the target repository.

Before starting, confirm that:

1. The target is a Git repository with a clean worktree, and its current commit has been recorded for rollback.
2. You downloaded both the release archive and its adjacent `.sha256` sidecar; compare the archive's SHA-256 with the sidecar value.
3. Python 3.11 or newer is available.
4. You have read the selected version's `migration-guide.md`. Even for a clean installation, confirm the default profile and optional-provider choices.

In PowerShell, set the paths and inspect the checksum as follows. The two values must match:

```powershell
$Archive = 'C:\Downloads\ai-context-dotnet-backend-v0.7.0.zip'
$Checksum = 'C:\Downloads\ai-context-dotnet-backend-v0.7.0.zip.sha256'
$PackageRoot = 'C:\gitproj\ai-context-package-0.7.0\ai-context-dotnet-backend-v0.7.0'
$TargetRoot = 'C:\gitproj\my-project'

Get-Content $Checksum
(Get-FileHash $Archive -Algorithm SHA256).Hash
```

On macOS or Linux, replace the paths and compare `shasum -a 256 <archive>` with the first field in the sidecar.

#### 1. Run a dry-run first; never overwrite directly

Run this from `PACKAGE_ROOT`. `--plan-output` is optional but recommended for review; it must be outside both the package and target directories.

```powershell
Set-Location $PackageRoot
python --version
python -m pip install -r requirements.txt

python .\payload\.ai\scripts\plan-ai-context-package-apply.py `
  --package-root . `
  --target-root $TargetRoot `
  --plan-output "$env:TEMP\ai-context-v0.7.0-clean-install-plan.yaml"
```

In Bash or zsh, use the equivalent commands:

```bash
PACKAGE_ROOT="$HOME/gitproj/ai-context-package-0.7.0/ai-context-dotnet-backend-v0.7.0"
TARGET_ROOT="$HOME/gitproj/my-project"
PLAN_OUTPUT="/tmp/ai-context-v0.7.0-clean-install-plan.yaml"

cd "$PACKAGE_ROOT"
python3.11 --version
python3.11 -m pip install -r requirements.txt
python3.11 payload/.ai/scripts/plan-ai-context-package-apply.py \
  --package-root . \
  --target-root "$TARGET_ROOT" \
  --plan-output "$PLAN_OUTPUT"
```

The default selection includes the `dotnet-backend` profile. `repo-backlog` is an optional provider and is disabled by default. Add `--enable-provider repo-backlog` to both dry-run and apply **only** when the target owner explicitly wants it for a clean installation. Never enable it merely to work around an upgrade problem.

Review the plan's selection and every `add`, `replace`, `remove`, `rename`, and `reconcile` item. This step creates a plan only; it does not write to the target repository.

#### 2. Apply only after the plan is accepted

Run apply only when the dry-run has been accepted and the target worktree remains at the same clean starting point. Repeat `--acknowledge` for every reconciliation item. Acknowledging an ID skips that item; it **does not** authorize replacing or deleting target-owned files.

```powershell
Set-Location $PackageRoot

python .\payload\.ai\scripts\plan-ai-context-package-apply.py `
  --package-root . `
  --target-root $TargetRoot `
  --apply `
  --acknowledge 'OP-001' `
  --acknowledge 'OP-002'
```

In Bash or zsh:

```bash
cd "$PACKAGE_ROOT"
python3.11 payload/.ai/scripts/plan-ai-context-package-apply.py \
  --package-root . \
  --target-root "$TARGET_ROOT" \
  --apply \
  --acknowledge 'OP-001' \
  --acknowledge 'OP-002'
```

Replace `OP-001` and `OP-002` with operation IDs from the reviewed plan, or remove those lines when no acknowledgement is required. After applying, read:

```powershell
Get-Content "$TargetRoot\.dev\AI-CONTEXT-APPLY-PENDING.yaml"
```

This receipt records applied components, skipped reconciliation items, and source evidence. It does not finalize target provenance.

#### 3. Run `ai-context-init` in the target repository

Now open your preferred AI Agent with `TARGET_ROOT` as its working directory and ask it to use the installed `ai-context-init` skill. The skill must derive target-specific truth from real repository files, solutions, packages, configuration, and existing documents. It must not treat framework-source facts as target facts or invent a product architecture for an empty repository.

Use this prompt for the first, read-only phase. Requiring an inventory and plan before writes is safer and easier to review than asking the Agent to handle everything autonomously.

```text
Complete clean-install initialization of AI context in the current target repository.

Package envelope root: <PACKAGE_ROOT>
Target repository: <TARGET_ROOT>
Requested release: <VERSION>

In the first phase, perform read-only checks only:
1. Confirm that the target Git worktree is clean and report its current commit.
2. Confirm that the package root contains requirements.txt, metadata/, and payload/, and verify the archive-checksum evidence.
3. Run the package planner in dry-run mode; place its plan output outside both package and target.
4. Report component/profile/provider selection, every add/replace/remove/rename/reconcile item, and its operation ID.
5. Do not extract or copy payload files directly into the target, apply changes, or create or finalize provenance.

Wait for my approval of the plan before continuing.
```

After approving the plan, send this follow-up prompt:

```text
I approve the application plan. Apply only the reviewed package plan from the same clean target commit.
Only acknowledge operation IDs that I explicitly name; acknowledgement is not authorization to replace or delete files.

After application, read .dev/AI-CONTEXT-APPLY-PENDING.yaml and use ai-context-init to:
- establish target-specific truth from target repository files, solutions, projects, packages, configuration, and existing documents;
- preserve reusable framework rules;
- update the necessary README, AGENTS, architecture entry points, and project config;
- avoid inventing product, endpoint, database, broker, queue, or deployment facts in an empty repository; and
- atomically create .dev/ai-context/provenance.yaml and .dev/ai-context/customizations.yaml only when repository, release, tag, full commit, component selection, and import-time evidence are credible.

Report changed files, unconfirmed facts, validation results, and the recommended next step.
```

In practice, commit framework-package application separately from target-specific documentation synchronization when that keeps review and rollback boundaries clearer.

### Version upgrade

`ai-context-upgrader` is neither a one-click overwrite tool nor the entry point for a first installation. Use it only for an initialized target, after the new package's planner has performed a version-aware application.

Before starting, you need all of the following:

1. A clean target worktree and a recorded rollback commit.
2. Valid `.dev/ai-context/provenance.yaml` and `.dev/ai-context/customizations.yaml`; legacy `.dev/AI-CONTEXT-SOURCE.yaml` is read-compatible only and must not coexist as a new authority.
3. The prior release package's matching `metadata/files.yaml`, plus the complete new release package and its checksum.
4. A migration guide that explicitly supports the source version and route.

For example, v0.7.0 directly supports the exact published v0.6.0 inventory as its automatic or reviewed upgrade source. A target on v0.5.0 or older must first follow the published migration guides to v0.6.0. Merely having the `ai-context-upgrader` skill installed is not sufficient.

#### 1. Build an upgrade dry-run with the new package

The following example upgrades an initialized target from v0.6.0 to v0.7.0. Run it from the **new** package root and pass the matching **previous** package inventory:

```powershell
$PackageRoot = 'C:\gitproj\ai-context-package-0.7.0\ai-context-dotnet-backend-v0.7.0'
$TargetRoot = 'C:\gitproj\my-project'
$PreviousFiles = 'C:\gitproj\ai-context-package-0.6.0\ai-context-dotnet-backend-v0.6.0\metadata\files.yaml'

Set-Location $PackageRoot
python -m pip install -r requirements.txt

python .\payload\.ai\scripts\plan-ai-context-package-apply.py `
  --package-root . `
  --target-root $TargetRoot `
  --previous-version 'v0.6.0' `
  --previous-files $PreviousFiles `
  --plan-output "$env:TEMP\ai-context-v0.6.0-to-v0.7.0-plan.yaml"
```

In Bash or zsh:

```bash
PACKAGE_ROOT="$HOME/gitproj/ai-context-package-0.7.0/ai-context-dotnet-backend-v0.7.0"
TARGET_ROOT="$HOME/gitproj/my-project"
PREVIOUS_FILES="$HOME/gitproj/ai-context-package-0.6.0/ai-context-dotnet-backend-v0.6.0/metadata/files.yaml"
PLAN_OUTPUT="/tmp/ai-context-v0.6.0-to-v0.7.0-plan.yaml"

cd "$PACKAGE_ROOT"
python3.11 -m pip install -r requirements.txt
python3.11 payload/.ai/scripts/plan-ai-context-package-apply.py \
  --package-root . \
  --target-root "$TARGET_ROOT" \
  --previous-version 'v0.6.0' \
  --previous-files "$PREVIOUS_FILES" \
  --plan-output "$PLAN_OUTPUT"
```

Review every `automatic-candidate`, `reconcile`, and `exclude` result. Content the planner cannot establish must remain an owner decision; never continue with a guessed version or an arbitrary `files.yaml`.

#### 2. Apply the planner, then use `ai-context-upgrader`

After accepting the plan, rerun the command with `--apply`, the same `--previous-version` and `--previous-files`, and only approved acknowledgement IDs. Read `.dev/AI-CONTEXT-APPLY-PENDING.yaml`, then run read-only planning with `ai-context-upgrader` in the target repository.

```powershell
Set-Location $PackageRoot

python .\payload\.ai\scripts\plan-ai-context-package-apply.py `
  --package-root . `
  --target-root $TargetRoot `
  --previous-version 'v0.6.0' `
  --previous-files $PreviousFiles `
  --apply `
  --acknowledge 'OP-001' `
  --acknowledge 'OP-002'
```

```bash
cd "$PACKAGE_ROOT"
python3.11 payload/.ai/scripts/plan-ai-context-package-apply.py \
  --package-root . \
  --target-root "$TARGET_ROOT" \
  --previous-version 'v0.6.0' \
  --previous-files "$PREVIOUS_FILES" \
  --apply \
  --acknowledge 'OP-001' \
  --acknowledge 'OP-002'
```

Replace the example operation IDs with reviewed, approved plan items. Remove every `--acknowledge` line when no reconciliation is present.

```text
Use ai-context-upgrader to plan, read-only, the upgrade of this target repository from <FROM_VERSION>
to <TO_VERSION>. The new package has been applied by the package planner; its receipt is at
.dev/AI-CONTEXT-APPLY-PENDING.yaml.

First:
1. Validate .dev/ai-context/provenance.yaml, the customizations ledger, release version, tag, full commit,
   package metadata, and the migration guide.
2. Compare base, incoming, and target state.
3. List automatic-candidate, reconcile, and exclude paths with reasons.
4. Produce a semantic reconciliation table grouped by customization ID, together with validation and rollback boundaries.

Do not modify target files, overwrite target-owned truth, or finalize provenance or the customizations ledger until I explicitly approve.
```

Authorize application only after the owner has decided every reconciliation item, required validation has succeeded, and an independent post-upgrade audit has no blocking finding. If the target lacks a credible baseline, require the Agent to stop with an unresolved-provenance inventory and propose manual reconciliation or a clean-install-style baseline. Do not force an automatic upgrade.

For detailed target-truth boundaries, see [`migration-boundaries.md`](.ai/assets/skills/ai-context-init/references/migration-boundaries.md). The support matrix for each version is defined by its [release migration guide](.dev/releases/INDEX.MD).

## Release Boundary

This repository is both the maintenance source and the build source for framework packages, but those scopes intentionally contain different files:

- Root README files, source-repository Agent entry files, historical workflows, assessments, release records, and product placeholders are source-only information and are never included in a downstream package.
- A portable package contains only reusable content named by the distribution profile's allowlist, with explicit exclusions providing a second protection boundary.
- As a result, editing this README improves the readability of the source repository only. It neither changes a published release nor makes the README eligible for inclusion in future packages.

## Language

- `README.md` is the Traditional Chinese (Taiwan) human-facing guide.
- `README.en.md` is the corresponding English version.
- Agent-facing context prefers English; human-facing guides may use Traditional Chinese (Taiwan). See [`.dev/standards/AI-CONTEXT-LANGUAGE-POLICY.md`](.dev/standards/AI-CONTEXT-LANGUAGE-POLICY.md) for the full policy.
