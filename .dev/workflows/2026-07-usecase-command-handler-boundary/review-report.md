# Use Case and Command Handler Boundary Baseline Review

## Review Metadata

- Review ID: `usecase-command-handler-boundary-baseline-review`
- Workflow: `2026-07-usecase-command-handler-boundary`
- Review type: architecture and AI-context consistency pre-analysis
- Review date: `2026-07-06`
- Branch: `codex/usecase-command-handler-alignment`
- Base: merged `main` at `343ab29`
- Skills:
  - `dev-workflow`;
  - `ddd-ca-hex-architect`.
- Product source review: not applicable; this repository is a reusable context
  framework.

## Executive Assessment

The repository already contains a viable explicit Use Case model in its controller
and testing examples, but the canonical standards and generation prompts still
prefer Handler-as-Use-Case. This creates two competing dependency graphs and makes
`Handler`, `Command`, and `Wolverine` carry multiple meanings.

The required change is architectural, not a naming-only refactor. The workflow must
first decide the inbound-port and adapter model, then update standards, generation
context, examples, and analyzers in that order.

## Evidence Used

- `.dev/standards/USECASE-COMMAND-HANDLER-RELATIONSHIP.MD`
- `.dev/standards/coding-standards/usecase-standards.md`
- `.dev/standards/coding-standards/controller-standards.md`
- `.dev/standards/coding-standards/test-standards.md`
- `.dev/standards/project-structure.md`
- `.dev/standards/examples/controller/`
- `.dev/standards/examples/usecase/`
- `.dev/guides/implementation-guides/DOTNET-DI-TEST-GUIDE.md`
- `.dev/guides/implementation-guides/PROFILE-CONFIGURATION-COMPLEXITY-SOLUTION.md`
- `.dev/agents/command-sub-agent/`
- `.dev/agents/query-sub-agent/`
- `.dev/agents/controller-sub-agent/`
- `.ai/assets/skills/slice-implementer/references/modes/`
- `.ai/assets/tech-stacks/dotnet-backend/references/CODE-TEMPLATES.MD`
- `tools/DotnetBackendAnalyzers/ControllerComplianceAnalyzer.cs`
- `tools/DotnetBackendAnalyzers/UseCaseServiceProviderInjectionAnalyzer.cs`
- matching analyzer tests.

## Inventory Snapshot

- 24 active files directly match Handler-as-Use-Case, Controller-to-Handler,
  `IUseCase -> Handler` registration, mandatory Wolverine command/query Handler,
  or combined `ICommand`/`IQuery` Use Case patterns.
- The broader dependency radius also includes command/controller sub-agent
  constraints, DI and test setup guides, technology templates, and Handler naming
  shared by message consumers and Reactors.
- The direct-match count is a lower bound. Each occurrence must be classified by
  trigger and delivery role before migration; a global rename is unsafe.

## Findings

### F1 — Canonical relationship contradicts the approved target

Severity: critical

The relationship standard explicitly says a Handler normally is the Use Case
implementation and recommends `Controller -> Command/Query -> Handler`. The
approved target requires Use Case and Handler to be separate objects, with
Controller depending on a Use Case interface.

Impact:

- future generated code will continue the rejected model;
- later analyzer rules cannot determine whether Handler injection is valid;
- changing examples alone would not fix the source of truth.

### F2 — Controller standard and controller examples disagree

Severity: critical

- controller standard examples inject `CreateResourceHandler`;
- controller examples inject `ICreateTaskUseCase`;
- controller guidance says controllers map DTOs to Use Cases;
- current analyzer tests explicitly accept an injected concrete Handler.

Impact:

- reviews can approve opposite dependency graphs;
- DI registrations vary between concrete Handler and Use Case interface;
- Presentation is not guaranteed to target a stable Application port.

### F3 — Use Case, command marker, and Handler entry are combined

Severity: high

The active Use Case example:

- defines `ICreateTaskUseCase : ICommand<CreateTaskInput, CqrsOutput>`;
- implements it with `CreateTaskService`;
- exposes both `Execute` and a forwarding `Handle` method described as a Wolverine
  entry point.

Impact:

- Use Case interfaces become coupled to dispatch semantics;
- one object has both orchestration and adapter entry responsibilities;
- a package choice can leak into the portable Application boundary.

### F4 — Wolverine is treated as mandatory in generation context

Severity: high

Command/query sub-agent prompts and slice modes say to use Wolverine handlers, even
though the technology profile now says Wolverine is conditional target-repository
guidance.

Impact:

- copied context may invent a package dependency;
- normal synchronous API behavior can be routed through a bus/dispatcher despite
  no target evidence;
- command and message handling remain conflated.

### F5 — Project structure encodes Handler-as-Use-Case

Severity: high

The Application structure contains `Commands` and `Queries` as “Command + Handler”
folders, states Handler can directly be the Use Case implementation, and does not
define a canonical explicit Use Case interface/implementation placement.

Impact:

- standards changes would be contradicted by generated folder guidance;
- target repos cannot consistently locate inbound ports versus adapters.

### F6 — DI and test guidance contains both models

Severity: high

Examples variously:

- register `ICreateProductUseCase` to `CreateProductHandler`;
- instantiate a Handler and call it the Use Case;
- resolve `ICreateProductUseCase` from DI;
- unit-test concrete Handlers as the orchestration object.

Impact:

- migration cannot be a simple rename;
- tests protect the current ambiguity;
- composition roots may retain unused Handler registrations.

### F7 — Analyzer ownership is incomplete

Severity: high

Current analyzers:

- prohibit direct Handler/UseCase construction in Controllers;
- do not prohibit injecting concrete Handlers into Controllers;
- classify Use Cases and Handlers together by suffix/namespace;
- enforce mixed command/query markers only on `Handle` methods;
- do not detect one object exposing both Use Case and Handler entry points.

Impact:

- approved architecture would remain advisory;
- naming heuristics may create false positives during staged migration;
- analyzer tests currently codify the old model.

### F8 — Handler taxonomy is overloaded

Severity: high

`Handler` currently refers to:

- synchronous command/query orchestration;
- Wolverine dispatch;
- MQ Consumer handling;
- Domain Event handling;
- Reactor/eventual-consistency work.

Impact:

- placement, retry, transaction, and output rules cannot be inferred from the
  suffix;
- “Handler must do X” rules unintentionally apply to unrelated delivery roles.

### F9 — Input/Command/Query contracts are unresolved

Severity: medium

Controller examples map HTTP DTOs to `Input`, while standards require
`ICommand<T>`/`IQuery<T>` records. The repository has not decided whether Command
is:

- the transport-neutral Use Case input;
- an in-process dispatcher request;
- a broker message;
- or a generic CQRS classification marker.

Impact:

- Use Case interfaces and Handler signatures cannot be finalized;
- serialization/metadata requirements may leak into HTTP-only flows.

### F10 — Query-side scope needs an explicit decision

Severity: medium

The user clarification explicitly covered normal Controller-to-Use-Case behavior,
but active standards apply Handler-as-Use-Case to commands and queries together.

Impact:

- fixing command flow alone may leave two API entry models;
- enforcing symmetry without approval could over-broaden the requested change.

## Preliminary Architecture Interpretation

Under Clean Architecture and Hexagonal Architecture:

- a Use Case interface is an inbound Application port;
- a Controller is an inbound HTTP adapter;
- a message/dispatcher Handler is another inbound adapter when that delivery
  mechanism is selected;
- both adapters may invoke the same Use Case;
- the Use Case owns orchestration and outbound-port dependencies;
- the Command/message contract belongs to its delivery boundary unless explicitly
  approved as the transport-neutral Use Case input.

This interpretation matches the user target and avoids making Wolverine a
portable architecture dependency. It remains a proposal until D1-D12 are resolved.

## Recommended Remediation Sequence

1. Resolve D1-D12.
2. Rewrite canonical relationship, Use Case, Controller, test, and project
   structure standards.
3. Update conditional technology and DI guidance.
4. Synchronize command/query/controller prompts and slice modes.
5. Migrate examples and test guidance.
6. Align analyzers and regression tests.
7. Run repository-wide role/invocation consistency validation.

## Initial Risk Boundary

Do not mechanically replace `Handler` with `UseCase`.

Some Handlers are legitimate message or event adapters and must remain. The safe
migration depends on classifying each occurrence by trigger, delivery mechanism,
transaction ownership, and caller before changing names or dependencies.
