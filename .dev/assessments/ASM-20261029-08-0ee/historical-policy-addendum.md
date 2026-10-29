# Historical decision evidence addendum

Assessment: `ASM-20261029-08-0ee`. Added 2026-10-29 after the owner requested a
bounded search of prior discussions and ADR/design/workflow evidence. This
addendum supplements the final [baseline report](report.md); it does not rewrite
the assessed source or turn the later #518 repair into #516 evidence.

The historical directories were unchanged from the assessed Framework commit
`0ee07d8314c55a95c99428fa8d4fd12c4673c04c`. Two read-only evidence workers used
the project inventory selection, `gpt-6-luna`, medium. The requested selection
is known; independent runtime model/billing identity was not exposed. The parent
owns the following interpretation and authored summary.

| Finding | Recovered evidence | Effect on the baseline conclusion |
|---|---|---|
| K01 Repository | `.dev/workflows/2026-07-repository-pattern-standards-alignment/workflow-plan.md:138-151` (D2); `review-report.md:18-29` | Explicit user-resolved identity-load/save decision, root persistence and read-model separation. Preserve it and explain its cost. It is not a universal two-method data-access rule. |
| K02 Input/Handler | `.dev/workflows/2026-07-usecase-command-handler-boundary/decision-difference-analysis.md:73-91,122-143` | The 2026-07-07 gate records dedicated Input with the scalar exception and Handler only for a real delivery entry; adapter placement separates transport/framework dependency. Earlier mixed examples do not override that selected policy. |
| K03 Mapper | `.dev/workflows/2026-07-dotnet-validator-phase-3/workflow-plan.md:58-67` | Static-only and alternative dependency-bearing roles are recorded as resolved. Full original motivation was not recovered. Current #518 also explicitly supplies the hidden-dependency rationale, so the rule is not unsupported merely because the original discussion is incomplete. |
| K05 Factory | Scoped ADR/design/lessons and keyword-matched historical workflow inventory | No original justification was located in that bounded search. This is an evidence limit, not proof that no decision exists. The existing restriction and #518's unresolved comparison remain distinct. |
| K06 MQ-only | `.dev/workflows/2026-07-usecase-command-handler-boundary/workflow-plan.md:57-68`; Repository alignment `workflow-plan.md:52-59` | These preserve MQ-only as a baseline. They do not recover its original rationale or reconcile the playbook's narrower broker restriction. |
| Preserved consistency | Repository alignment `workflow-plan.md:309-334` (D6) | Explicit user-resolved eventual-consistency default and visible `IUnitOfWork` dependency for synchronous strong consistency, atomic Aggregate/outbox storage and post-success event acknowledgement. |

Accessible conversation evidence was also inspected:

- `評估 Skill 職責與 SDLC 調整`, thread `01a15f79-f0de-7263-8abd-a4fc746f3d7d`,
  turn `01a163c8-fef5-7082-8b7b-5f7246e1d56f` (2026-10-22), explains domain versus
  software-architecture decisions and outputs. It is analysis, not acceptance of
  every .NET form rule.
- `盤點歷史 Issue 與整理優先序`, thread `01a16957-21f3-7472-9be9-a1b4353a3246`,
  turn `01a160c8-68bd-72c0-a4d6-dde565cede6a` (2026-10-22), records the user's
  selected skill names and retirement without alias. That does not adopt all
  unrelated repository/mapper/factory policies.
- `ArchPrecept 規則修正、套件文件驗收與低成本發布審查`, thread
  `01a18356-569f-7ed2-be57-693106249bac`, supplied continuation context and closeout
  turn `01a18356-59bd-79d2-a9fd-eb7a3cfc7762` (2026-10-28), summarize the selected
  minimal Repository, static pure Mapper, canonical UseCase/thin entry and
  query/projector boundaries. The continuation is user-supplied context, not an
  independently verified Issue decision. It explicitly leaves static-factory
  prohibition and MQ-only rationale/applicability unresolved.

The new evidence strengthens decision provenance for K01–K03 and preserved
consistency. It does not change the fixed-source findings, complete #515/#519,
authorize target adoption or close the unresolved factory/MQ questions. Product
guidance may link fixed historical Git records; it must not depend on private
conversation access or load `.dev` resources as installed execution dependencies.
