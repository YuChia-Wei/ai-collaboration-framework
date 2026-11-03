# .NET Backend Knowledge

Optional references for DDD, Clean Architecture, CQRS and ASP.NET Core backends.
Installation supplies knowledge; target-owned decisions select rules, technology
and execution. UI frameworks and full-stack generation are outside this profile.

Load only task-relevant resource IDs from the installed selection. Required
inputs must be available; do not fall back to a framework source checkout.
`target-authority:<name>` denotes an explicit target-owned input, not a path.
Member links are relative to their containing document; rule-owner paths are
relative to the catalog. Embedded rule text uses its semantic owner's link base.

Requires `engineering-common@0.4.1`. Preserve per-domain persistence choices,
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
