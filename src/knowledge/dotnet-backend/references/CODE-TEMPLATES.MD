# Code generation and behavior

Use the [generation guide](../tooling/generation/README.md) for executable
project, class, interface and Use Case templates, or fragments in existing files.
Generated code is editable target source and does not depend on Framework tools.

| Responsibility | Semantic owner |
| --- | --- |
| Command orchestration and query separation | [Use Case standards](../standards/coding-standards/usecase-standards.md) |
| Invariants and event transitions | [Aggregate standards](../standards/coding-standards/aggregate-standards.md) |
| Required-state reconstruction | [Mapper standards](../standards/coding-standards/mapper-standards.md) |
| Read models and projector recovery | [Projection standards](../standards/coding-standards/projection-standards.md) |
| Transport input/output mapping | [Controller standards](../standards/coding-standards/controller-standards.md) |
| Observable scenarios | [Test standards](../standards/coding-standards/test-standards.md) |

Choose input/output contracts, persistence and failure behavior from accepted
requirements. A generator supplies syntax and structure; it does not make these
design decisions or replace the selected validation.
