# Use Case and Command Handler Boundary Workflow

## Metadata

- Plan ID: `workflow-plan-2026-07-usecase-command-handler-boundary`
- Workflow ID: `2026-07-usecase-command-handler-boundary`
- Owner skill: `dev-workflow`
- Status: `completed`
- Created: `2026-07-06`
- Branch: `codex/usecase-command-handler-alignment`
- Base: `main` at merge commit `343ab29`
- Issue: not provided

## Problem Statement

Active standards currently define two incompatible synchronous application entry
models:

1. `Controller -> Command/Query -> Handler`, where the Handler normally is the Use
   Case implementation.
2. `Controller -> IUseCase -> UseCase implementation`, where a Handler is a
   separate delivery/dispatch object.

The user-approved target from the repository-pattern workflow is the second model:

- Use Case and Handler are separate objects;
- an API Controller injects a Use Case interface;
- normal synchronous API behavior does not publish a Command through a bus;
- message/event Handler responsibilities remain distinct from Use Case
  orchestration.

The current guidance, examples, prompts, project structure, tests, and analyzers do
not consistently implement that target.

The evidence baseline is recorded in [review-report.md](./review-report.md).

The user's D1-D12 decisions were compared with the attached discussion in
[decision-difference-analysis.md](./decision-difference-analysis.md). The
material differences were re-decided on `2026-07-07` and are recorded below.

## Scope

### In scope

- define `Use Case`, `Input`, `Command`, `Query`, `Handler`, `Application Service`,
  `Controller`, `Consumer`, and `Reactor` responsibilities;
- define the default synchronous API invocation chain;
- define when command/query/message handlers exist and what they may delegate;
- define whether query flows use the same explicit Use Case boundary;
- align DI, naming, project structure, prompts, examples, tests, and analyzers;
- keep Wolverine and other dispatch packages conditional on target-repository
  evidence.

### Non-goals

- no production application implementation;
- no message broker or transport redesign;
- no repository-pattern redesign;
- no broad standards translation;
- no target-specific Wolverine API configuration;
- no sub-agent work unless explicitly requested later.

## Governing Constraints

- DDD + Clean Architecture + CQRS remains the base architecture.
- A Use Case is the application orchestration boundary.
- Presentation adapters do not depend directly on repositories or Domain objects.
- Cross-bounded-context communication remains MQ-only.
- In-process synchronous API behavior does not require message publication.
- Eventual consistency remains the default across Aggregates.
- Exceptional strong consistency is declared by an explicit `IUnitOfWork`
  dependency on the Use Case, not hidden in a Handler.
- Runtime packages such as Wolverine are conditional target-repository choices.

## Approved Target Direction

```text
HTTP Request
  -> Controller
  -> I<CreateOperation>UseCase
  -> <CreateOperation>UseCase
  -> Aggregate / Domain Service / outbound ports
  -> Use Case Output
  -> HTTP Response
```

When a dispatch or message entry is actually required:

```text
Command / Message / Scheduled Trigger
  -> Handler (inbound adapter)
  -> I<CreateOperation>UseCase
  -> Use Case implementation
```

Proposed responsibility split:

- `Use Case interface`: stable inbound Application port;
- `Use Case implementation`: application orchestration, transaction requirement,
  Aggregate/query collaboration, and output contract;
- `Input` / `Output`: transport-neutral Use Case contract;
- `Command`: intent message used only where command dispatch is intentionally
  selected;
- `Handler`: adapter for a selected delivery mechanism; maps its input and invokes
  a Use Case, without becoming the default Use Case implementation;
- `Controller`: HTTP adapter that maps HTTP DTOs to Use Case input and injects only
  Use Case interfaces;
- `Consumer` / event Handler / Reactor: message adapters or eventual-consistency
  workers, kept distinct from synchronous API Use Cases.

## Approved Decisions

### D1 — Use Case interface shape

`ExecuteAsync` is the mandatory operation name. Every asynchronous Use Case must
declare a non-optional `CancellationToken` parameter.

A dedicated, transport-neutral input object is the default:

```csharp
public interface ICreateProductUseCase
{
    Task<CreateProductOutput> ExecuteAsync(
        CreateProductInput input,
        CancellationToken cancellationToken);
}
```

Two exceptions are allowed:

- if the operation has no input other than cancellation, omit the input object;
- if the operation has exactly one input value and that value uses a standard
  platform type, the Use Case may accept that value directly.

For this exception, a standard platform type means one scalar built-in or BCL
value such as `string`, a numeric type, `bool`, `Guid`, or a date/time type. A
collection, tuple, custom record/class, or multiple values requires a dedicated
input object.

```csharp
Task ExecuteAsync(CancellationToken cancellationToken);

Task<FindProductOutput> ExecuteAsync(
    Guid productId,
    CancellationToken cancellationToken);
```

### D2 — Input versus Command

A Use Case never accepts an HTTP request, broker contract, Wolverine Command, or
other delivery contract as its Application input. It accepts its own
transport-neutral input object, subject only to the no-input and single-standard-
type exceptions in D1.

A Controller maps its HTTP request to the Use Case input. When an actual dispatch
entry exists, its Handler maps the message Command to the same Use Case input.

### D3 — Command Handler existence and role

A Command Handler exists only when an actual command/message dispatch entry is
configured. It is not mandatory for every command-style Use Case and is not added
solely to wrap a Controller call.

### D4 — Controller dependency rule

By default, a Controller depends on one or more explicit Use Case interfaces. It
must not inject:

- concrete Handlers;
- `IMessageBus`;
- mediator/dispatcher abstractions;
- write repositories;
- Domain services.

An explicitly selected pure-query endpoint may inject an `IQueryRepository` or
query service directly. This is an allowed but discouraged exception, not an
alternative default. Without an explicit decision for that endpoint, the
Controller must use a query Use Case.

### D5 — Query-side symmetry

The default synchronous query flow is:

```text
Controller -> I<GetProduct>UseCase -> GetProductUseCase -> IProductQueryRepository
```

For a pure query only, an explicitly approved endpoint may call an
`IQueryRepository` or query service directly. The developer must document why the
extra coupling and loss of inbound-port symmetry are justified. Direct
query-handler dispatch is not the approved exception.

### D6 — Handler placement

Package-neutral convention Handlers may remain in Application. Wolverine-,
MediatR-, MQ-, or other framework/transport-specific Handlers belong to the
inbound adapter or composition boundary. In every placement, the Handler maps its
delivery input and invokes one Use Case; it does not own the business workflow.

### D7 — Result and error ownership

A Use Case returns only a transport-neutral output produced by completing the
operation. If the operation produces no output object, it returns `Task` rather
than an artificial empty result. A Controller maps the outcome to HTTP, and a
message Handler maps failure behavior to retry/dead-letter semantics. A Use Case
never returns `IActionResult`, broker acknowledgements, or framework-specific
envelopes.

### D8 — Transaction and event lifecycle ownership

Repository coordination, an exceptional explicit `IUnitOfWork`, outbox
coordination, and pending Domain Event acknowledgement dependencies belong to the
Use Case implementation. A Handler never introduces hidden strong consistency and
does not independently commit after invoking a Use Case.

### D9 — Concrete implementation naming

Use `CreateProductUseCase` and the `*UseCase` suffix for the concrete
implementation. This workflow does not introduce, expand, or redefine
`Application Service`; that concept remains outside this decision set.

### D10 — Compatibility and migration

Compatibility and concrete migration steps are deferred. They must be planned
against the target product during an actual refactor, where the developer must be
reminded to classify callers, registrations, and real dispatch entries before
changing them. This workflow will not publish a generic migration recipe.

### D11 — Analyzer enforcement

Deterministic boundary violations are analyzer errors, including:

- Controller dependencies on Handler, dispatcher, or message bus;
- Use Case interface and implementation shape;
- Handler-to-UseCase dependency direction;
- transport/package dependencies in Use Cases;
- legacy classes that implement both Use Case and Handler entry points.

The explicit pure-query exception from D4/D5 must not be reported as an error when
the target project provides reliable evidence that the endpoint selected that
profile. Naming-only or migration advisories remain warnings where deterministic
target evidence is unavailable.

### D12 — Wolverine and dispatcher policy

Use Cases depend on project-owned outbound event publisher ports, not directly on
Wolverine `IMessageBus`. Infrastructure adapts those ports to Wolverine when the
target repository selects Wolverine.

Wolverine remains valid conditional guidance for messaging, outbox, consumers,
and intentionally selected dispatch. It is not a portable requirement for normal
synchronous API Use Cases and is not automatically introduced by command/query
implementation prompts. A Use Case must not publish Commands or inject another
Use Case.

## Skill Routing

| Stage | Capability | Skill | Confidence | Evidence |
| --- | --- | --- | --- | --- |
| S0 | workflow orchestration | `dev-workflow` | High | Mandatory workflow gate and existing deferred task |
| S0-S2 | architecture | `ddd-ca-hex-architect` | High | Use Case/Handler/Controller/adapter boundary design |
| S3 | context governance | `ai-context-governance` | High | Prompts, reusable AI assets, guides, and examples |
| S4 | implementation | `slice-implementer` | High | Bounded analyzer and validation changes |
| S5 | workflow validation | `dev-workflow` | High | Cross-file consistency and closure |

## Stages

### S0 — Workflow bootstrap and pre-analysis

- Status: completed
- Outputs:
  - `workflow-plan.md`;
  - `review-report.md`;
  - `tasks/bootstrap-usecase-command-handler-workflow.json`.
- Validation:
  - branch starts from merged `main`;
  - workflow artifacts parse and links resolve;
  - findings cite active repository evidence.

### S1 — Resolve architecture decisions

- Status: completed
- Owner: `ddd-ca-hex-architect`
- Output:
  - approved D1-D12 decisions;
  - `decision-difference-analysis.md`;
  - `tasks/resolve-usecase-command-handler-decisions.json`.
- Gate:
  - passed: R1-R4 were re-decided and D1-D12 are recorded.

### S2 — Align canonical standards

- Status: completed
- Owner: `ddd-ca-hex-architect`
- Primary scope:
  - `src/knowledge/dotnet-backend/design/architecture-overview.md`;
  - `.dev/standards/USECASE-COMMAND-HANDLER-RELATIONSHIP.MD`;
  - usecase/controller/test/project-structure standards;
  - DI and technology-profile rules.

### S3 — Synchronize context, prompts, guides, and examples

- Status: completed
- Owner: `ai-context-governance`
- Primary scope:
  - command/query/controller sub-agent prompts;
  - slice-implementer modes;
  - .NET backend templates and checklists;
  - controller/usecase/testing/DI examples and guides.

### S4 — Align analyzers and executable validation

- Status: completed
- Owner: `slice-implementer`
- Primary scope:
  - Controller and Use Case analyzer rules;
  - positive, negative, migration, and false-positive tests;
  - analyzer documentation and severity template.

### S5 — Final validation and closure

- Status: completed
- Owner: `dev-workflow`
- Validation:
  - all task JSON parses;
  - analyzer tests pass;
  - changed Markdown links resolve;
  - targeted role and invocation searches match approved decisions;
  - `git diff --check`;
  - deferred migration risks are recorded.

## Commit Checkpoints

1. `workflow(workflow): bootstrap use case handler alignment`
2. `workflow(workflow): record use case handler decisions`
3. `docs(architecture): align use case handler boundaries`
4. `docs(ai-context): synchronize use case handler guidance`
5. `feat(dotnet-backend): enforce use case handler boundaries`
6. `workflow(workflow): close use case handler alignment`

Each workflow-stage commit includes `Why`, `What`, `Validation`, and `Workflow`
sections.

## Completion Criteria

- Controller, Use Case, Input/Output, Command/Query, and Handler each have one
  canonical role.
- Synchronous API invocation has one default dependency chain.
- Framework-specific dispatch is conditional and cannot silently replace the
  Application port.
- Transaction and event lifecycle ownership is explicit.
- Prompts, examples, tests, DI guidance, and analyzers agree with the approved
  model.
- Migration guidance distinguishes legacy compatibility from the new default.

## Completion Summary

- D1-D12 are approved and implemented across canonical standards and active
  reusable guidance.
- Synchronous Controllers default to explicit Use Case interfaces; the only
  direct data-access exception is an explicitly selected pure query using a
  read-only Query Repository/Service.
- Use Cases use `ExecuteAsync`, transport-neutral contracts, required
  `CancellationToken`, project-owned outbound event publisher ports, and no
  direct Wolverine or Use Case-to-Use Case dependency.
- Command/Query Handlers exist only for real dispatch entries and adapt to one
  Use Case; legitimate Reactor and Consumer handlers remain distinct.
- Analyzer diagnostics `DBA1014` through `DBA1017` enforce the deterministic
  boundaries, and 47 analyzer tests pass.
- Product-specific migration sequencing remains deferred under D10.
- Target repositories must provide evidence that a pure-query endpoint explicitly
  selected the direct Query Repository/Service exception.
