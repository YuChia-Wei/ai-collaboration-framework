# Repository Pattern Standards Alignment Workflow

## Metadata

- Plan ID: `workflow-plan-2026-07-repository-pattern-standards-alignment`
- Workflow ID: `2026-07-repository-pattern-standards-alignment`
- Owner skill: `dev-workflow`
- Status: `completed`
- Created: `2026-07-05`
- Branch: `codex/repository-pattern-standards-alignment`
- Rebased onto: local `main` at `2d4130c`
- Bootstrap commit after rebase: `32f6227`
- Original analysis baseline: `417cc5c`
- Issue: not provided

## Problem Statement

The repository pattern guidance does not currently provide one reliable execution contract. Active standards, architecture references, prompts, examples, and generated checks disagree on:

- repository abstraction name;
- allowed operation set;
- command-side persistence technology;
- query-side layering;
- custom repository interface policy;
- soft-delete behavior;
- transaction and domain-event lifecycle;
- automated enforcement.

These conflicts can cause generated code, reviews, tests, and future context synchronization to enforce incompatible designs.

The baseline findings are retained in [review-report.md](./review-report.md).

## Scope

### In scope

- Establish the canonical command-side repository contract.
- Establish query-side port and adapter placement.
- Align Dapper, Npgsql, EF Core, Unit of Work, and outbox responsibilities.
- Resolve aggregate deletion and domain-event lifecycle rules.
- Update canonical `.dev` standards and architecture references.
- Synchronize dependent `.ai` context, prompts, guides, examples, and checks.
- Replace or constrain checks that cannot safely validate semantic architecture rules.

### Non-goals

- No product application implementation.
- No target-repository migration.
- No unrelated standards cleanup.
- No broad documentation translation unless explicitly approved.
- No runtime wrapper redesign unless a canonical skill contract is affected.
- No cross-bounded-context communication redesign.

## Governing Constraints

- DDD + Clean Architecture + CQRS remains the base architecture.
- Hexagonal Architecture defines application ports and infrastructure adapters.
- Cross-bounded-context communication remains MQ-only.
- Domain objects remain independent of ORM, broker, and transport concerns.
- Persistence and query technology are target-repository decisions.
- Technology-specific guidance applies only when the target selects that adapter.
- Runtime wrappers must remain thin.
- `.dev/standards/**` is agent-facing execution context; new normative text should follow the language policy.
- User decisions must be recorded before canonical standards are rewritten.

## Target Direction

The following approved direction governs this workflow:

1. Separate aggregate persistence, pure query access, and technical/operational writes into distinct semantic ports.
2. Permit aggregate repositories to load and persist Aggregate Roots only; child entities are persisted through their owning Aggregate Root.
3. Do not expose a general-purpose writable repository or CRUD abstraction to Application code.
4. Keep the aggregate repository contract limited to approved aggregate lifecycle operations.
5. Exclude bulk operations from the shared aggregate repository contract.
6. Model soft deletion as aggregate behavior followed by persistence; reserve physical purge for a separate maintenance capability.
7. Keep the normative repository contract database-, ORM-, and package-neutral.
8. Put EF Core, Dapper, Npgsql, event-store, and other adapter-specific rules in conditional implementation guidance.
9. Let the transaction boundary own commit, rollback, and atomic outbox persistence; repositories participate without independently committing.
10. Clear or acknowledge recorded domain events only after successful atomic persistence.
11. Use direct query ports for simple reads; introduce an application query service only for composition or query-side policy.
12. Use capability-specific write ports such as outbox, projection, import, or purge writers when data is not aggregate state.
13. Align the existing `DBA1001` Roslyn analyzer with the approved semantic contract, add positive/negative/false-positive tests, and retire the non-gating repository grep script.

## Repository Role Model

### Aggregate persistence port

- Purpose: rehydrate and persist one Aggregate Root consistency boundary.
- Allowed domain result: Aggregate Root only.
- Disallowed: returning or persisting a child entity independently.
- Disallowed: UI search, reporting, filtering, paging, and arbitrary DTO queries.
- Implementation: an outbound adapter using the target system's selected database and package.

### Pure query port

- Working name: `IQueryRepository`.
- Purpose: execute read-model queries without aggregate mutation.
- Return types: DTOs, read models, scalar values, identifiers, or pages.
- Disallowed: aggregate/domain mutation and persistence writes.
- A query port may be use-case-specific rather than a generic query CRUD interface.

### Technical or operational write port

- Examples: `IOutboxStore`, `IProjectionWriter`, `IInboxStore`, `IIdempotencyStore`, `IBulkImportWriter`, or `IDataPurgePort`.
- Purpose: write data that is not the state of an Aggregate Root, or perform an explicitly approved operational capability.
- Naming rule: name the business/technical capability; do not call it a general repository.
- Implementation: an Infrastructure adapter.
- A persistence helper used only inside an adapter does not need to become an Application port.

### Port and adapter relationship

- Repository/query/writer interfaces express Application-required semantics and are outbound ports.
- EF Core, Dapper, SQL, event-store, file, cache, and broker implementations are outbound adapters.
- Choosing Adapter Pattern does not remove the need for a semantic port when Application code has a dependency.
- If a write is an internal implementation detail of an adapter, keep it internal instead of creating another public port.

## Open Decisions

### D1 — Aggregate repository name and compatibility shape

Status: resolved by user.

Decision:

- `IAggregateRepository<TAggregate, TId>` is the canonical contract for new code.
- `IDomainRepository<TAggregate, TId>` remains as a compatibility contract and must inherit `IAggregateRepository<TAggregate, TId>`.
- Both contracts require `TAggregate` to be an Aggregate Root.
- New code should prefer `IAggregateRepository`.
- Compatibility must not suppress violations: analyzers must inspect `IDomainRepository`, its generic argument, and every derived aggregate-specific interface.
- A legacy `IDomainRepository<ChildEntity, TId>` remains a violation and must be reported.

Migration consequence:

- Existing products can adopt the context without renaming every valid aggregate repository first.
- The compatibility contract creates a semantic bridge, not a second repository model.
- Empty aggregate-specific wrappers remain discouraged; they are allowed only for compatibility or approved aggregate-specific lifecycle semantics.

### D2 — Aggregate repository operation contract

Status: resolved by user.

Decision:

- The shared aggregate repository exposes:
- `FindByIdAsync`
- `SaveAsync`
- `SaveAsync` persists a new or changed Aggregate according to adapter rules.
- Soft delete is an Aggregate behavior followed by `SaveAsync`.
- Physical deletion is required but is not part of the shared aggregate repository.
- Physical deletion uses a separately named restricted capability such as `IAggregatePurgePort<TAggregate, TId>` or a target-specific retention/deletion port.
- A hard-delete use case must still apply authorization, retention, legal, and aggregate eligibility rules before invoking the purge port.

### D3 — Multiple instances of the same Aggregate type

Status: resolved by user after final traceability audit.

Clarified scenario:

- a query port identifies multiple `ProductAggregate` identifiers;
- the application loads `List<ProductAggregate>`;
- each Aggregate executes its own domain behavior;
- the application persists all changed Product Aggregates.

This is not the same as coordinating different Aggregate types such as Product and Order.

Architectural interpretation:

- loading by a collection of identities remains Aggregate access, not read-model querying;
- applying behavior to each Aggregate remains valid domain behavior;
- batch IO is a legitimate performance capability;
- batch IO does not mean the Aggregates form one consistency boundary;
- Unit of Work controls transaction/commit semantics and does not replace batch IO optimization.

Options:

#### Option A — Put batch methods on every aggregate repository

```text
IAggregateRepository<TAggregate, TId>
  FindByIdAsync
  SaveAsync
  FindByIdsAsync
  SaveAllAsync
```

Advantages:

- simple consumer API;
- direct support for the described workflow.

Risks:

- every adapter must implement batch behavior even when it cannot optimize it;
- normal Use Cases can casually expand into large batch transactions;
- `SaveAllAsync` atomicity and partial-failure behavior are easy to leave undefined;
- event-store, document, relational, and remote adapters may have materially different capabilities.

#### Option B — Optional aggregate batch capability

```text
IAggregateRepository<TAggregate, TId>
  FindByIdAsync
  SaveAsync

IAggregateBatchRepository<TAggregate, TId>
  FindByIdsAsync
  SaveAllAsync
```

Conditionally recommended, but the portable core should define the capability pattern rather than ship a mandatory concrete interface.

Rules:

- the portable context documents an opt-in Aggregate batch persistence capability but does not require a concrete `IAggregateBatchRepository` type;
- a target repository may define `IAggregateBatchRepository`, `IProductAggregateBatchPort`, or an equivalent semantic port after the opt-in conditions are satisfied;
- a target batch port must not inherit `IAggregateRepository<TAggregate, TId>`;
- it is not registered by default and does not appear in normal Use Case templates;
- a target repository introduces it only after recording expected cardinality, measured IO pressure, batch limits, and failure semantics;
- both generic arguments remain constrained to Aggregate Root and its identifier;
- only batch-oriented Use Cases inject the batch capability;
- `FindByIdsAsync` is identity-based loading only, not status/filter querying;
- query repository obtains the candidate IDs;
- each Aggregate must execute its own domain behavior before persistence;
- batch persistence must preserve concurrency checks and pending events for each Aggregate;
- large input sets must be chunked;
- missing IDs, duplicate IDs, ordering, maximum batch size, concurrency failures, and partial failures must be specified;
- aggregate-specific adapters may implement both interfaces;
- adapters without real batch support are not forced to expose the capability.
- common code-review guidance must challenge batch dependencies used only to wrap one ID in a collection.
- framework-level analyzer rules must not depend on `IBatchUseCase` until the deferred Use Case/Handler workflow defines that taxonomy.

#### Option C — Loop over the single-aggregate contract

```text
foreach id:
  aggregate = FindByIdAsync(id)
  aggregate.DoBehavior()
  SaveAsync(aggregate)
```

Advantages:

- clearest per-Aggregate semantics;
- works with every adapter.

Risks:

- may produce N+1 IO;
- performance can be unacceptable for large sets;
- adapters cannot reliably optimize across calls without additional infrastructure.

Transaction semantics:

- `FindByIdsAsync` / `SaveAllAsync` optimize IO; they do not by themselves request strong business consistency.
- `IUnitOfWork` is injected only when all changed Aggregates must commit or roll back atomically.
- Without an atomic business requirement, process bounded chunks and expose per-item/chunk failure handling rather than opening one large transaction.
- An all-or-nothing transaction over an unbounded list is prohibited.
- For imports, migrations, rebuilds, and purges that do not execute normal Aggregate behavior, use a separate capability-specific writer instead of `IAggregateBatchRepository`.

Decision:

- portable core uses Option C and exposes only the single-Aggregate contract;
- portable standards document, but do not publish, the Option B target-specific batch capability pattern;
- no canonical batch interface appears in portable building blocks, default templates, or default DI;
- target repositories may introduce a batch port only after measured need and complete semantics are recorded;
- target-repository architecture tests or analyzers may enforce local batch markers after the Use Case taxonomy is resolved;
- code review remains responsible for whether batch justification is genuine;
- `IUnitOfWork` is required only when business semantics demand all-or-nothing commit, not merely for batch IO;
- non-atomic bulk processing uses bounded chunks, retry, and resumable progress.

Final audit:

- original cause: the active standards disagreed between a three-method and five-method default repository contract;
- actual requirement: some target systems may need efficient identity-based loading and persistence of multiple instances of the same Aggregate type;
- non-requirement: every target system does not need batch persistence;
- mismatch found: making `IAggregateBatchRepository` and `IBatchUseCase` canonical would turn an optional optimization into portable architecture law;
- corrected solution: keep the portable Aggregate repository minimal and document a target-specific batch extension pattern with explicit opt-in evidence and semantics.

### D4 — Preventing the writable-repository broken-window effect

Status: resolved by user.

Decision:

- prohibit `IRepository<TEntity, TId>`-style CRUD ports available to general Application code;
- aggregate persistence ports accept Aggregate Roots only;
- query ports cannot write;
- technical writes use capability-specific names and do not return Aggregates;
- Infrastructure may use private DAO/table-gateway helpers inside adapters;
- Application code cannot inject those private helpers.
- explicitly ban public general-purpose `IGenericRepository`, `IWritableRepository`, and `ICrudRepository` contracts.

### D5 — Persistence technology policy

Status: resolved by user.

Decision:

- The normative contract must not require a database, ORM, or persistence package.
- Each target system selects its own persistence technology.
- Technology-specific content is conditional guidance, not a universal repository requirement.

Guidance consequence:

- EF Core guidance should explain tracking policy by use case, projection behavior, concurrency, model registration, and asynchronous terminal operators.
- A query does not always require `ToListAsync`; use the terminal operator matching cardinality, such as `ToListAsync`, `SingleOrDefaultAsync`, `FirstOrDefaultAsync`, `AnyAsync`, or `CountAsync`.
- Dapper, Npgsql, event-store, and other guidance should document their own transaction, mapping, concurrency, and materialization concerns.

### D6 — Transaction boundary, Unit of Work visibility, and domain-event acknowledgement

Status: resolved by user.

Decision:

- Eventual consistency remains the default for coordination across Aggregates.
- A Use Case requiring synchronous strong consistency explicitly injects `IUnitOfWork`.
- Explicit injection is exceptional and communicates the stronger consistency requirement in the dependency graph.
- A normal single-Aggregate Use Case does not automatically require `IUnitOfWork`.
- Repository adapters do not independently commit when participating in the explicit Unit of Work.
- Transaction middleware/decorators may implement infrastructure mechanics, but must not hide whether the Use Case declares the strong-consistency dependency.
- Repository-owned independent commits are prohibited when an operation has multiple atomic participants.

Required lifecycle contract:

1. execute Use Case orchestration and Aggregate behavior;
2. capture pending domain events;
3. persist aggregate changes and required outbox records atomically;
4. commit;
5. acknowledge/clear recorded events only after successful commit;
6. preserve retry/concurrency behavior on failure.

Boundary note:

- This decision uses `Use Case` as the application orchestration object.
- Current repository documents do not consistently separate Use Case from Handler; that terminology and invocation model is deferred to a follow-up workflow.

### D7 — Query-side layering

Status: resolved by user.

Decision:

- A simple query handler may depend directly on an Application query port implemented by Infrastructure.
- Add an Application Query Service only for multi-source composition, reusable query policy, or non-trivial calculation.
- Do not require a pass-through Query Repository + Query Service pair for every query.

### D8 — Remediation breadth

Status: resolved by user.

Decision:

- update canonical standards first;
- synchronize active context and examples second;
- align validator/tooling third;
- validate and close last.

### D9 — Language migration

Status: resolved by user.

Decision:

- defer broad standards translation to a separate workflow;
- do not use sub-agents for translation in this workflow;
- keep this workflow focused on architecture semantics and consistency.

### D10 — Semantic validation contract

Status: resolved by user.

Decision:

- `IAggregateRepository<,>` and `IQueryRepository` semantic contracts are mandatory for analyzer classification;
- compatibility `IDomainRepository<,>` and all aggregate-specific interfaces derived from either aggregate contract are covered;
- aggregate repository generic argument must be an Aggregate Root;
- child domain entities cannot be exposed as independently persisted repository roots;
- only the approved D2 lifecycle methods are allowed on the shared aggregate repository;
- query repository ports cannot expose persistence write operations;
- query repositories do not return mutable Aggregate Roots or child domain entities;
- capability-specific writers are not misclassified as aggregate repositories;
- ORM/package-specific behavior is excluded from the generic analyzer.

Enforcement ownership:

- Roslyn analyzer: type relationships, method surface, return/parameter types, forbidden dependencies.
- Architecture/configuration tests: cross-assembly placement and runtime model registration.
- Unit/integration tests and AI review: transaction atomicity, event acknowledgement, query efficiency, mapping completeness.

- semantic marker/base contracts replace naming heuristics;
- analyzer severity is `error`;
- aggregate-specific repository interfaces derived from the canonical or compatibility aggregate contracts are included;
- repository grep scripts are retired after equivalent analyzer tests pass.

## Follow-up Workflow Candidate: Use Case and Handler Boundary

The current repository is not aligned with the user's intended model.

User target:

- Use Case and Handler are separate application objects.
- API Controller injects a Use Case interface.
- API Controller does not publish a Command to invoke normal synchronous application behavior.
- Handler is not the default Use Case implementation.

Current conflicting rules:

- `USECASE-COMMAND-HANDLER-RELATIONSHIP.MD` says Handler is normally the Use Case implementation.
- `controller-standards.md` injects concrete Handler objects.
- controller examples inject `IUseCase`.
- command/query skill references prefer Wolverine handlers.

Recommended follow-up:

- open a separate workflow after Repository Pattern alignment;
- redefine Use Case, Command, Handler, Controller, synchronous invocation, and message-handler roles;
- update controller/use-case standards, project structure, prompts, examples, analyzers, and tests together;
- keep event/MQ handlers distinct from synchronous API Use Case invocation.

Tracking:

- retained as deferred task `follow-up-usecase-handler-boundary`;
- must be promoted into a new workflow after Repository Pattern alignment closes;
- intentionally excluded from the current canonical standards implementation stage.

## Skill Routing

| Stage | Capability | Skill | Confidence | Evidence |
| --- | --- | --- | --- | --- |
| S0 | workflow orchestration | `dev-workflow` | High | Repository capability profile |
| S0-S2 | architecture | `ddd-ca-hex-architect` | High | Repository capability profile |
| S0, S3-S5 | context governance | `ai-context-governance` | High | Repository capability profile |
| S4 | bounded validator implementation | `slice-implementer` | High | Repository capability profile and completed Validator Phase 3 direction |

No sub-agent work is planned. Specialist skills are applied sequentially in the current thread.

## Stages

### S0 — Baseline analysis and decision frame

- Status: completed
- Goal: retain evidence-backed findings and create the decision boundary.
- Outputs:
  - `review-report.md`
  - `tasks/repository-pattern-analysis-and-decision-frame.json`
- Validation:
  - workflow Markdown exists;
  - task JSON parses;
  - findings include source evidence and do not claim user approval.

### S1 — Resolve architecture decisions

- Status: completed
- Owner: `ddd-ca-hex-architect`
- Goal: D1-D10 decision resolution completed.
- Output:
  - updated decision section in this plan;
  - `tasks/resolve-repository-pattern-decisions.json`
- Validation:
  - every decision is approved, rejected, or explicitly deferred;
  - no unresolved decision is silently inferred.

### S2 — Align canonical standards

- Status: completed
- Owner: `ddd-ca-hex-architect`
- Goal: rewrite the normative repository, query, transaction, deletion, and persistence rules.
- Primary targets:
  - `.dev/ARCHITECTURE.MD`
  - `src/knowledge/dotnet-backend/requirements/TECH-STACK-REQUIREMENTS.MD`
  - `.dev/standards/coding-standards.md`
  - `.dev/standards/coding-standards/repository-standards.md`
  - `.dev/standards/coding-standards/projection-standards.md`
  - `.dev/standards/coding-standards/usecase-standards.md`
  - `.dev/standards/project-structure.md`
  - matching rationale documents
- Validation:
  - one abstraction name;
  - one operation set;
  - one command-side persistence policy;
  - one query-layer placement model;
  - explicit transaction, event, concurrency, and deletion semantics.

### S3 — Synchronize dependent context

- Status: completed
- Owner: `ai-context-governance`
- Goal: propagate approved rules without duplicating canonical ownership.
- Scope:
  - `.ai/assets/tech-stacks/dotnet-backend/`
  - relevant skill and sub-agent references;
  - active prompts;
  - human-facing guides;
  - examples and checklists.
- Validation:
  - canonical rules remain in standards or canonical AI assets;
  - runtime wrappers remain thin;
  - reference searches find no active contradictory contract;
  - deferred historical examples are explicitly labeled.

### S4 — Align validation tooling

- Status: completed
- Owner: `slice-implementer`
- Goal: align `DBA1001` with the approved contract and retire the repository grep validation path.
- Scope:
  - `tools/DotnetBackendAnalyzers/RepositoryQueryMethodAnalyzer.cs`
  - `tools/DotnetBackendAnalyzers.Tests/RepositoryQueryMethodAnalyzerTests.cs`
  - `tools/DotnetBackendAnalyzers/README.md`
  - `tools/DotnetBackendAnalyzers/templates/analyzer-severity.editorconfig`
  - `.ai/scripts/check-repository-compliance.sh`
  - `.ai/scripts/generated/check-repository.sh`
  - `.ai/scripts/check-all.sh`
  - `.ai/scripts/README.md`
  - validator ownership and mapping documents
- Validation:
  - analyzer recognizes only the approved domain repository contract;
  - allowed lifecycle methods pass;
  - forbidden query-style methods fail;
  - query/read repositories and unrelated interfaces do not produce false positives;
  - analyzer positive, negative, and false-positive regression tests pass;
  - the repository grep script and its generated artifact are removed only after replacement evidence passes;
  - `check-all.sh`, README, and validator ownership documents agree.

### S5 — Final consistency validation and closure

- Status: completed
- Owner: `dev-workflow`
- Goal: verify the complete rule family and close the workflow.
- Validation:
  - parse all changed JSON;
  - `git diff --check`;
  - targeted reference searches;
  - Markdown link validation for changed documents;
  - shell syntax checks for changed scripts;
  - relevant repository validation commands;
  - residual risks and deferred work documented.

### Deferred follow-up — Use Case and Handler boundary

- Status: deferred
- Owner: `dev-workflow`
- Artifact:
  - `tasks/follow-up-usecase-handler-boundary.json`
- Trigger:
  - open a dedicated workflow after this Repository Pattern workflow closes.

## Commit Checkpoints

The workflow bootstrap was committed as `32f6227` after rebasing onto `main`.

Use these remaining coherent boundaries:

1. `workflow(workflow): record repository pattern decisions`
2. `docs(architecture): align repository pattern standards`
3. `docs(ai-context): synchronize repository guidance`
4. `feat(dotnet-backend): align repository validation`
5. `workflow(workflow): close repository pattern alignment`

Each workflow-stage commit must include `Why`, `What`, `Validation`, and `Workflow` sections.

## Completion Criteria

- D1-D10 are resolved or explicitly deferred.
- Canonical standards contain no internal contradiction for the repository rule family.
- Active prompts, guides, examples, and checks do not override the canonical contract.
- Transaction/outbox examples state their adapter assumptions and preserve the
  approved commit/event lifecycle.
- Semantic analyzer validation agrees with the canonical standards.
- Final validation evidence is recorded.

## Completion Summary

- D1-D10 are resolved and implemented.
- Portable aggregate persistence uses
  `IAggregateRepository<TAggregate, TId>` with `FindByIdAsync` and `SaveAsync`.
- `IDomainRepository<TAggregate, TId>` remains a compatibility contract derived
  from the canonical interface and receives the same Aggregate Root enforcement.
- Pure reads use `IQueryRepository` ports; QueryService remains conditional.
- Target-specific batch capability guidance is documented without publishing a
  mandatory portable batch interface.
- DBA1001 now performs inheritance-based semantic validation with error severity;
  all 36 analyzer tests pass.
- Legacy repository grep scripts were removed and cannot be regenerated from the
  Markdown parser.
- The separate Use Case/Handler boundary remains intentionally deferred in
  `tasks/follow-up-usecase-handler-boundary.json`.

