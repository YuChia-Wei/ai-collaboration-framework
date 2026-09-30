# Migrate To v0.4.0

This is the published migration contract for `REL-v0.4.0`. Annotated tag
`v0.4.0` resolves to
`5af1db672928f9d51f55fee04183ad27b79fb9f8`. Validate the downloaded archive
against its adjacent `.sha256` asset before planning an upgrade.

## Supported Source

The governed source is `REL-v0.3.0` at
`1e782909b7753b2889014516595d72f703a260f3`. Older, unversioned, or forked
copies must first enter unresolved-provenance reconciliation or adopt the
intermediate `v0.3.0` contracts. Do not infer a safe base from similar paths or
historical repository ancestry.

## Safety Sequence

1. Require a clean target worktree and preserve a rollback commit.
2. Confirm `.dev/AI-CONTEXT-SOURCE.yaml` identifies the actual installed base,
   local overrides, and unresolved items.
3. Validate the eventual v0.4.0 archive and supply the governed v0.3.0
   `files.yaml` to the package planner.
4. Run the package planner in dry-run mode. A file disposition describes
   incoming release intent; it does not replace base/incoming/target
   comparison.
5. Reconcile target-owned truth, locally modified framework files, moves,
   merges, retirements, and source-included BuildingBlocks.
6. Apply only explicitly accepted operations from a clean worktree.
7. Run `ai-context-upgrader`, repository-specific context synchronization, and
   the target's required validation.
8. Update target provenance to v0.4.0 only after accepted changes validate.

## Required Contract Reconciliation

### Technology Selection

Create or reconcile the target-owned generic technology-selection record.
`testing.mocking` defaults to NSubstitute only when the target has not selected
another supported implementation. Apply the same override shape for ORM,
broker, and future technology slots; do not create a mocking-only exception.

### Deletion Policy

Treat soft delete as the default Aggregate Repository profile, not an
invariant. A target may explicitly opt out. Hard delete remains an explicit
purge capability with a purpose-specific command and repository port; do not
silently turn normal repository deletion into physical deletion.

### BuildingBlocks And Aggregates

Normal Aggregates use the interface-first contracts. Do not force a shared base
class. `EsAggregateRoot<TId>` is an optional, executable-tested source include
for replay, pending-event tracking, state transition dispatch, and committed
version mechanics.

When copied into a target, source-included code becomes target-owned. Upgrade it
through three-way comparison or reimplement the documented behavior contract;
never overwrite a locally evolved copy from path identity alone.

### Solution Grammar

Review the logical `<workload>/DomainCore` and
`<workload>/Presentation` mapping. Use bounded context as workload for a
micro-system mono repo and system as workload for a mono-system repo. This is a
logical navigation grammar, not an instruction to rename physical projects or
solution folders.

### Example Evidence

Consume evidence tiers from `evidence-manifest.yaml`. Existing legacy examples
default downward to illustrative or historical unless a validator and
verification route prove a stronger tier. Do not restore retired fixtures just
to preserve a previous folder shape.

### Shell Asset Registry

Reconcile `shell-assets.yaml` from schema `1.0` to `2.0`. Every tracked shell
asset now declares role, lifecycle, distribution, authority, and replacement
direction. `packaged` means the asset remains available for execution or
compatibility; it does not make grep-based C# checks semantic authorities.
Preserve target-owned shell customizations as local overrides and do not
silently promote transitional helpers to required gates.

`check-test-compliance.sh` is a packaged `retirement-candidate` and is no
longer selected by `check-all.sh`. Remove downstream automatic invocations or
replace them with target-owned testing selections, analyzers, and executable
test architecture checks. The packaged file exists only for the v0.4.0
migration window.

## Move, Merge, And Retirement Projection

The following operations may be proposed automatically only when the target
source bytes match the v0.3.0 base, the destination has no conflicting
target-owned change, no local override applies, and the eventual package
planner proves the operation. Otherwise they require reconciliation.

| Incoming intent | Source | Destination |
| --- | --- | --- |
| merged | `.dev/standards/examples/TEMPLATE-INDEX.md` | `.dev/standards/examples/INDEX.md` |
| merged | `.dev/standards/examples/bdd-gherkin-example/OUTBOX-TEST-CONFIGURATION.md` | `.dev/standards/examples/outbox/OUTBOX-TEST-CONFIGURATION.md` |
| moved | `.dev/standards/examples/bdd-given-when-then-example/OUTBOX-TEST-CONFIGURATION.md` | `.dev/standards/examples/outbox/OUTBOX-TEST-CONFIGURATION.md` |
| moved | `.dev/standards/examples/bdd-gherkin-test/CreateTaskUseCase.feature` | `.dev/standards/examples/bdd-gherkin-example/create-task-usecase.feature` |
| merged | `.dev/standards/examples/bdd-gherkin-test/README.md` | `.dev/standards/examples/bdd-gherkin-example/README.md` |
| merged | `.dev/standards/examples/testing-guide.md` | `.dev/standards/coding-standards/test-standards.md` |
| merged | `.dev/standards/examples/test-example.md` | `.dev/standards/examples/bdd-given-when-then-example/` |
| merged | `.dev/standards/examples/use-case-test-example.md` | `.dev/standards/coding-standards/test-standards.md` |
| merged | `.dev/standards/examples/projection-example.md` | `.dev/standards/examples/projection/` |
| moved | `.dev/standards/guides/DATABASE-MIGRATION-GUIDE.md` | `src/knowledge/dotnet-backend/guides/DATABASE-MIGRATION-GUIDE.md` |
| moved | `.dev/standards/guides/DEVELOPMENT-TOOLS-GUIDE.md` | `src/knowledge/dotnet-backend/guides/DEVELOPMENT-TOOLS-GUIDE.md` |
| merged | `.dev/standards/guides/EF-CORE-CONFIGURATION-GUIDE.md` | `src/knowledge/dotnet-backend/guides/PERSISTENCE-CONFIGURATION-GUIDE.md` |
| merged | `.dev/standards/guides/README.md` | `.dev/guides/implementation-guides/README.MD` |
| merged | `.dev/standards/prompts/README.md` | `.dev/guides/ai-collaboration-guides/README.MD` |

Automatic removal may be proposed under the same byte-identical/no-override
conditions for these retired sources:

- `.dev/standards/examples/.versions.json`;
- `.dev/standards/examples/bdd-gherkin-example/AggregateOutboxRepositorySteps.cs`;
- `.dev/standards/examples/bdd-gherkin-example/CompleteUseCaseSteps.cs`;
- `.dev/standards/examples/bdd-gherkin-test/CreateTaskUseCaseSteps.cs`;
- `.dev/standards/examples/bdd-gherkin-test/TestHostFixture.cs`;
- `.dev/standards/examples/bdd-gherkin-test/UseCaseTestFixture.cs`;
- `.dev/standards/examples/test/` and its hollow fixtures/product tests.
- `.dev/standards/prompts/add-feature-prompt.md`;
- `.dev/standards/prompts/create-use-case-prompt.md`.

If a target changed any retired source, preserve it until the user chooses
whether to keep target-owned content, migrate useful material, or remove it.

## Mandatory Manual Reconciliation

- `AGENTS.md`, `CLAUDE.md`, translations, and root repository identity;
- target requirements, specs, ADRs, architecture, operations, domain language,
  and project configuration;
- target workflow, assessment, backlog, and release catalogs;
- technology selections and architecture capability selections;
- copied BuildingBlocks/source includes and any locally modified skill,
  runtime wrapper, script, standard, or validator.

Source workflow instances, assessment instances, backlog items, release
registry history, and this source repository's root truth remain excluded from
target packages.

## Deferred Or Separate Work

- Full Observability/AOP architecture remains `OBS-001` and is not introduced
  by this migration.
- NuGet publication for analyzers or BuildingBlocks remains a future delivery
  decision.
- Physical downstream solution-folder migrations are not part of v0.4.0.
