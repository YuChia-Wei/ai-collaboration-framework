# Provider Reconciliation Read-Back

## Canonical Integration

- Pull request: [#68](https://github.com/YuChia-Wei/ai-collaboration-prompts-dotnet-backend/pull/68)
- Merge commit: `cdff0f36e4cb2963231ac004606d340659bf3f0c`
- Merged at: `2026-07-30T14:54:18Z`
- Read-back recorded at: `2026-07-30T23:01:33+08:00`
- Projection source: merged `main`, not a feature branch.

## Formal Issue Projection

| Backlog | Issue | Source SHA-256 | Title | Body | Labels / State | Project read-back |
| --- | --- | --- | --- | --- | --- | --- |
| `OBS-001` | [#45](https://github.com/YuChia-Wei/ai-collaboration-prompts-dotnet-backend/issues/45) | `1f16485bdc4866804488a4e7e3bbf7b7cc164ab1de3f8045ab5387d7585d7795` | exact | exact | exact / open | `Inbox`, `P2 Normal`, `Pending`, `Unassigned`, `Not yet published` |
| `STD-001` | [#61](https://github.com/YuChia-Wei/ai-collaboration-prompts-dotnet-backend/issues/61) | `519e12c5dc945dd58de30b1858088a064edb03d25df4bac5f460c274290110fc` | exact | exact | exact / open | `Planned`, `P1 High`, `Approved`, `Unassigned`, `Not yet published` |

Both Issue bodies resolve their canonical permalink to `main@cdff0f3`, retain
the canonical attribution and migration markers, and project the reciprocal
Related Work references without creating a sub-issue relationship.

## Proposal Intake

- Proposal: [#69](https://github.com/YuChia-Wei/ai-collaboration-prompts-dotnet-backend/issues/69)
- Title: `[Proposal] Standardize Python Prerequisite Diagnostics Across Validator Entrypoints`
- State: `open`
- Labels: `kind:proposal`, `scope:mixed`, `triage:needed`
- Project item: `PVTI_lAHOAwvEG84Bez7wzg0r2gQ`
- Project status: `Inbox`
- Created at: `2026-07-30T14:59:13Z`

The Proposal records `ASM-20260730-001#AIC-004` as evidence. It was not
accepted, rejected, promoted, assigned a formal backlog ID, or treated as
implementation authorization.

## Read-Back Method

- Rebuilt the deterministic GitHub provider projection from merged `main`.
- Updated #45 and #61 through the GitHub provider, then compared their complete
  returned titles and bodies with the deterministic projection.
- Read Project #3 through `gh project item-list` and selected only #45, #61,
  and #69 for exact field verification.
- Confirmed that Project automation added #69 to Inbox and did not initialize
  formal-backlog fields that do not apply to a Proposal.
