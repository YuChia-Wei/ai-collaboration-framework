# .NET Backend Knowledge

Optional references for DDD, Clean Architecture, CQRS and ASP.NET Core backends.
Installation supplies knowledge; target-owned decisions select rules, technology
and execution. UI frameworks and full-stack generation are outside this profile.

Load only task-relevant resource IDs from the installed selection. Required
inputs must be available; do not fall back to a framework source checkout.
`target-authority:<name>` denotes an explicit target-owned input, not a path.
Member links are relative to their containing document; rule-owner paths are
relative to the catalog. Embedded rule text uses its semantic owner's link base.

Requires `engineering-common@0.4.2`. Preserve per-domain persistence choices,
conditional Event Sourcing, BDDfy opt-out and target-selected mocking. New pins
do not replace accepted target policy or imply runtime validation.

| Task | Entry |
| --- | --- |
| Generate projects, files or fragments | [Generation guide](tooling/generation/README.md) |
| Design dependencies and boundaries | [Architecture playbook](design/architecture-playbook.md) |
| Select applicable rules | [Rule catalog](engineering-rule-catalog.yaml) |
| Implement and review behavior | [Coding standards](standards/coding-standards.md) |
| Choose project layout | [Project structure](standards/project-structure.md) |
| Design tests | [Testing strategy](shared/testing-strategy.md) |
| Resolve policy meaning | [Policy rationale](standards/POLICY-RATIONALE.md) |
| Select mechanical validation | [Validation recipes](tooling/on-demand-mechanical-validation/README.md) |

`content-package.yaml` lists available members and resource IDs. Legacy role
projections are references, not active skill routes. Generated code and optional
validation recipes require target-selected compilation and behavior checks.

## Migrating from 0.1.9 examples

The 0.2 line removes the old `examples/` and `source-includes/` trees from the
installed knowledge package. Runnable starter code now has one template source;
small insertion fragments use SnippetTool. Tutorial placeholders and optional
integration examples are not advertised as complete generated capabilities.
Update project-owned links to the old paths explicitly; installation cannot
rewrite links in your own documents or upgrade previously copied code.

| Previous content | Current entry or disposition |
| --- | --- |
| `examples/usecase`, `examples/use-case-injection` | `aicf-usecase` plus Use Case guidance; dependency registration remains target-owned |
| `examples/aspnet-core`, `examples/controller`, `examples/dto` | `aicf-miniapi` or `aicf-webapi` reference feature; adapt HTTP contracts to the target |
| `examples/generation-templates`, `examples/reference`, `examples/profile-configs` | Generation guide above lists the native API starters, C# items and contract examples |
| `source-includes/domain`, `examples/aggregate` | `domain-contracts` and optional `es-aggregate` snippets; select ES only when required |
| `examples/contract`, `examples/mapper` | Existing DbC/mapper standards; the mapper contract-case summary is now `standards/contract-cases.md` |
| `examples/bdd-gherkin-example`, `examples/bdd-given-when-then-example` | Generic Gherkin examples in `engineering-common/bdd`; no generated business bindings |
| `examples/bdd-step-methods` | BDD/GWT knowledge remains guidance; target-specific bindings must be implemented and tested locally |
| `examples/outbox`, `examples/projection`, `examples/inquiry-archive`, `examples/nuget` | Persistence/messaging and package-selection guidance remains; no equivalent complete relay, projector, archive or NuGet integration is promised |

The separate generation bundle provides the native starters, snippets and
[domain contract test templates](templates/domain-contracts/README.md).
Copy and adapt generated code under target ownership.
