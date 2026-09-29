# Workflow Plan

## Metadata

- `plan_id`: `workflow-plan-2026-04-14-legacy-script-rename`
- `owner_skill`: `ddd-ca-hex-architect`
- `status`: `completed`

## Context

- Problem statement:
  - The repo still contains shell scripts with legacy names such as `spring` and `jpa`.
  - Current `.NET`-friendly script names are only thin wrappers that delegate into those legacy-named files.
  - This keeps historical naming visible in the file system and risks confusing future AI agents and human maintainers.
- Why this workflow now:
  - The repo has already been normalized toward `.NET`-first architecture and documentation.
  - Script naming is the next major historical residue that should be converged.
- Current branch context:
  - work starts from `temp` via `codex/rename-legacy-script-names`

## Goal

Convert script ownership to `.NET`-first names while preserving backward compatibility.

## Target Direction

- Preferred `.NET`-first filenames become the real implementation owners.
- Legacy-named files remain only as thin compatibility wrappers for a transition period.
- All docs and references point to the `.NET`-first names as canonical entry points.
- Wrapper behavior stays functionally equivalent to avoid breaking older prompts, notes, or local habits.

## In Scope

- `.ai/scripts/check-jpa-projection-config.sh`
- `.ai/scripts/check-spring-config.sh`
- `.ai/scripts/check-test-spring-di.sh`
- `.ai/scripts/check-projection-config.sh`
- `src/tools/dotnet/check-dotnet-config.sh`
- `src/tools/dotnet/check-test-di-compliance.sh`
- `.ai/scripts/README.md`
- any repo docs or prompts that still reference the legacy script names

## Out Of Scope

- Renaming every script in `.ai/scripts/`
- Rewriting the internal logic of unrelated validation scripts
- Removing backward compatibility wrappers in the same stage

## Working Mode

- Use direct implementation mode for the actual rename/wrapper work.
- Keep one workflow because the task is multi-step and affects code plus documentation plus compatibility behavior.
- Prefer local execution without sub-agents unless a later verification pass needs parallel checking.

## Phase Plan

### Stage 1: Inventory and dependency map
- Confirm all current references to:
  - `check-jpa-projection-config.sh`
  - `check-spring-config.sh`
  - `check-test-spring-di.sh`
- Confirm which current `.NET`-named scripts are wrappers versus real owners.
- Record whether any other scripts chain into these names.

### Stage 2: Rename ownership
- Make the `.NET`-named files the real implementation owners.
- Convert legacy-named files into thin wrappers that delegate to the `.NET`-named owners.
- Keep the wrapper format minimal and obvious.

### Stage 3: Update docs and references
- Update `.ai/scripts/README.md`
- Update any docs/prompts that still recommend the legacy names
- State clearly that `.NET`-first names are canonical

### Stage 4: Verification
- Re-scan the repo for legacy script references
- Verify wrapper direction is correct:
  - legacy -> canonical
  - not canonical -> legacy
- Confirm worktree consistency and commit

## Canonical Naming Mapping

| Legacy Name | Canonical Name |
| --- | --- |
| `check-jpa-projection-config.sh` | `check-projection-config.sh` |
| `check-spring-config.sh` | `check-dotnet-config.sh` |
| `check-test-spring-di.sh` | `check-test-di-compliance.sh` |

## Compatibility Rule

- During this workflow, old names must keep working.
- The compatibility wrapper should:
  - forward all arguments
  - remain short
  - contain a comment that it is a legacy wrapper

## Risks

- Reversing the wrapper direction by mistake
- Missing indirect references in docs or scripts
- Breaking local habits if an old filename disappears entirely

## Validation Checklist

- [ ] Canonical owner files use `.NET`-first names
- [ ] Legacy files still exist only as wrappers
- [ ] Repo docs prefer canonical names
- [ ] Search results for legacy names are limited to wrappers and explicit compatibility notes

## Expected Deliverables

- renamed script ownership structure
- updated `.ai/scripts/README.md`
- a task artifact recording execution and validation

## Completion Summary

- All workflow task artifacts are marked `done`.
- Canonical .NET-first script names became the active ownership paths.
- Later analyzer-transition work may retire transitional scripts, but that is a separate workflow.
