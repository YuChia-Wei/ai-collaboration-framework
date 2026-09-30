# Migrate From v0.1.0 To v0.2.0

`v0.2.0` is also a retrospective source snapshot and provenance anchor, not an installable distribution package. Do not copy either tag tree into a new or existing target. Use these commits only as comparison bases for allowlisted reconciliation; new installations must use a published governed package.

## Before Changing Files

1. Confirm the target's existing framework source is tag `v0.1.0` at commit `69c285077708dfb96ee49bb39258aec83eb7f1a9`; otherwise record the source as unresolved.
2. Commit or otherwise preserve target-local changes.
3. Inventory target-owned root collaboration instructions, requirements, specs, ADRs, operations documents, and runtime customizations.
4. Exclude source requirements, backlog instances, completed workflows, assessments, release history, and source root truth before proposing reusable framework paths.

## Required Reconciliation

- Adopt uppercase `AGENTS.md` as the canonical English entry and use `CLAUDE.md` as a thin Claude adapter without overwriting target-specific collaboration truth.
- Reconcile skill canonical packages and both runtime wrapper trees; do not copy source-repository completed workflows or assessments.
- Adopt standalone assessment storage only for new durable audits; do not retroactively relabel unrelated reports without review.
- Apply the current workflow branch, commit trailer, and `--no-ff` merge policies to future work.
- Update development task producers to use task intent plus one execution mode and optional remediation overlay.

## Validation

Run repository AI-context and workflow validators, then inspect every target-owned conflict manually. Because `v0.2.0` predates the provenance contract, its own tagged tree cannot create the manifest. When a `v0.3.0` or newer upgrader performs this migration retrospectively, it may record `v0.2.0` as the validated resulting source version immediately after these checks pass; it need not falsely defer provenance until a later target version.
