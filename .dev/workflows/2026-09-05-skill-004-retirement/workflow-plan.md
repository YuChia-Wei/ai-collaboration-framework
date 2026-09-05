# Retire deprecated skill entries

## Workflow metadata

- Workflow: `2026-09-05-skill-004-retirement`; owner: `ai-context-governance`; status: `in_progress`.
- Branch: `codex/2026-09-05-skill-004-retirement`; base: `main` at `f06e8e3a882e375e31e315569741541ac6e1659d` (live GitHub read-back matched).
- Created / updated: `2026-09-05T14:29:47+08:00`.
- Template: `.ai/assets/skills/ai-context-governance/templates/ai-context-maintenance-workflow-plan-template.md`, version `1.2.0`.

## Objective and authority

Implement [Issue 271](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/271). The owner's 2026-09-05 conversation request to process this Issue authorizes local implementation. Select the Issue's proposed v0.16.0 as the removal release; this is a source lifecycle decision, not a Project allocation or publication.

One cohesive delivery covers tombstones, runtime routing, historical validation, and downstream removal fixtures. Workflow mode retains the cross-surface lifecycle and acceptance evidence. No push, PR, merge, Issue/Project mutation, tag, release, or publication is authorized. Prefer linear integration after separately authorized PR gates.

## Baseline and preservation

The current transition validator requires deprecated specs and wrappers indefinitely. Existing package migration already computes guarded framework-managed removals and target-owned reconciliation. Preserve all existing workflows, tasks, assessments, releases, provenance, commits, and evaluation records byte-for-byte. Keep the v0.6 activation manifest as historical evidence and add the v0.16 retirement manifest. Active replacement specs/wrappers remain unchanged.

Graph discovery returned stale source ranges and no verifiable index SHA; use explicit tracked-file and direct-source fallback for the selected transition, workflow, package and test surfaces. Git CLI remote read failed at the sandbox proxy; GitHub connector live read-back confirmed the clean baseline.

## Tasks and acceptance

- SKILL-004-lifecycle: retirement manifest; remove canonical aliases and wrappers; explicit retired/replacement routing diagnostic; distinguish new requests from historical evidence.
- SKILL-004-upgrade: v0.6.0 and v0.9.0 fixtures prove unchanged framework aliases are removed, modified aliases block, target-owned aliases reconcile; historical bytes stay unchanged.

Acceptance IDs AC1 through AC6 follow the Issue's six criteria, respectively. Focused tests and validators precede an immutable review. Existing historical evaluation is retained, not rerun as evidence of current model behavior.

## Resume checkpoint

- Current task: SKILL-004-lifecycle.
- Next: implement retirement manifest and validator; exercise focused upgrade fixtures; record evidence and commit; perform read-only post-remediation review.
- Validation: pending.
- Source release/publication and real downstream deployment: not executed.
