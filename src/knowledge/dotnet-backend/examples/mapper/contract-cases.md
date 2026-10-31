# Reconstruction and projector contract cases

These original examples illustrate the selected knowledge contracts. They are
not a persistence product, a new target policy or a complete compiled portfolio.
The [Mapper owner](../../standards/coding-standards/mapper-standards.md) defines
required-state versus optional-display failure; the
[projector owner](../../standards/coding-standards/projection-standards.md#event-driven-read-model-projector)
defines the selected recovery examples.

## Behavior cases

| Given / when | Required outcome and responsibility |
|---|---|
| Required DefinitionOfDone is absent, JSON null or malformed on a command-side load | Explicit failure with no usable Aggregate; adapter identifies record/field/schema, data owner repairs. Never catch/continue or save defaults. |
| State schema or historical event version is unsupported | Fail visibly; target owner selects compatibility/upcasting/migration. A known identity does not authorize partial success. |
| A display-only badge is explicitly dispensable, and its JSON is malformed | A DTO with `IsIncomplete` and a reason is valid; no Aggregate or business-state write is produced. |
| The same fallback is unselected or applied to price/permission/required state | Reject degradation. DTOs also fail when their own required contract cannot be met. |
| A formerly valid creation event conflicts with today's command precondition | Replay under the selected historical compatibility rule, without rerunning today's command. Unsupported history still fails; do not silently drop it. |
| Replay encounters an unknown event after partially restoring state | Failure escapes and instance is discarded. No command/save/clear-based recovery of the partial instance. |
| A new command versus replay of an old fact | Only the new command records a new pending fact; replay sends no email, payment or other external effect. |
| Duplicate projector delivery after read commit but failed ack | Deduplicate the committed event and retry acknowledgement under the selected transaction/retention policy. |
| Read write/commit fails | Roll back and leave checkpoint/ack incomplete; retry/park under the selected policy. |
| Separately stored checkpoint/ack fails or is unknown | Reconcile it and replay idempotently; do not advance past an unprocessed sequence gap or claim exactly-once. |
| Query reader writes, or projector changes command state/publishes externally | Reject under those roles; owned read-store projection grants neither capability. |

## Optional published ArchPrecept CT-005 case

The illustrative API baseline is **ArchPrecept.Contracts.Domain.EventSourcing
0.0.3-preview**, with **ArchPrecept.Contracts.Domain 0.0.3-preview**. The product
owner's [release record](https://github.com/YuChia-Wei/ArchPrecept/blob/main/docs/releases/0.0.3-preview.md)
reports public publication and registry verification. Build source is
[`fdc1f9ff3934c769047f797803abc8614290e889`](https://github.com/YuChia-Wei/ArchPrecept/tree/fdc1f9ff3934c769047f797803abc8614290e889);
the fixed [CT-005 contract](https://github.com/YuChia-Wei/ArchPrecept/blob/fdc1f9ff3934c769047f797803abc8614290e889/docs/product/event-sourcing-contract.md)
and [ES API](https://github.com/YuChia-Wei/ArchPrecept/blob/fdc1f9ff3934c769047f797803abc8614290e889/src/Contracts/ArchPrecept.Contracts.Domain.EventSourcing/EsAggregateRoot.cs)
support the conclusions below. Later source that still displays the same build
version is not substituted for these published bytes.

| Exact nupkg | SHA-256 from the release record |
|---|---|
| ArchPrecept.Contracts.Domain.EventSourcing.0.0.3-preview.nupkg | `a0a222ada35ecbc4787b69f9a900640bc4469fe847c7144040799710a710c74d` |
| ArchPrecept.Contracts.Domain.0.0.3-preview.nupkg | `ceb5c5985a0ee61a00572dc6948ab9b187fe2c6d557249f0482626b0f62e3026` |

The [published build artifact](https://github.com/YuChia-Wei/ArchPrecept/actions/runs/39812215279/artifacts/12441085472)
has ZIP digest `d07b031ee633859b604f007abd20ecca682104f4a723bfb1a9e552cf01712c7b`.
Verify the two nupkg hashes, then extract Domain into `domain/` and ES into
`eventsourcing/` under an explicit local directory. No package bytes or credentials
are included here. The product release record is prior registry evidence; local
artifact verification is a distinct observation, not a fresh feed-restore claim.

The bundled support files `contract-cases/Program.cs`,
`contract-cases/ContractCases.csproj` and `contract-cases/NuGet.Config` accompany
this example resource. The runnable cases exercise:

- successful `LoadFromHistory`: state and committed version restored, pending empty;
- prohibited `ClearDomainEvents`, mismatched commit version and retained pending;
- new events remaining pending until a confirmed whole-batch append;
- unknown/failed append represented by no local confirmation, then reconciliation;
- replay failure poisoning: subsequent Apply/replay/commit rejected, discard instance;
- package-free source-include Replay/Apply/commit as an equivalent API vocabulary.
- the actual package-free `Plan` example: valid nested state, absent history,
  missing project/task references and an unsupported event. Failed construction
  returns no usable partial Plan; its event contract reuses inherited timestamp
  metadata without hiding it.

Run with .NET 8 or a compatible installed SDK and explicit verified DLL directory:

```powershell
dotnet run --project <package-root>/examples/mapper/contract-cases/ContractCases.csproj -p:PublishedContractsDir=<verified-extracted-directory>
```

The project clears package sources and references the supplied net8.0 DLLs;
it downloads nothing. The external packages use MIT; obtain them from the owner
and preserve their license. No Analyzer is loaded. The append receipt is a test
double: these cases do not prove real event-store atomicity, transport recovery,
projector transactions or arbitrary side-effect/dataflow analysis.

The package-free reference source include does not enforce CT-005's poisoning
or every replay guard; the caller must discard failed instances. A custom target
may enforce stronger guards or choose another explicit failure API. It must still
preserve required state, separate history from new facts and confirm only durable
success. Normal state-based Aggregates do not acquire an ES requirement.

This fixes portable knowledge and supplies an optional fixed API example.
[Framework #179](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/179)
owns actual external API/version adoption when the owner selects a ready package;
this example does not install ArchPrecept, alter target policy or assign #179 to
a Framework release. Existing target failure policies need explicit conflict and
migration review before adoption; new knowledge pins never silently replace them.
