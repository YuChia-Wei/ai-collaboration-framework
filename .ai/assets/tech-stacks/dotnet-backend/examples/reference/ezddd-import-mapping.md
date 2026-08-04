# Historical ezDDD Import Mapping (Reference)

This guide preserves source-stack terminology as historical provenance. It does
not define expected .NET namespaces, promise a future package, or authorize
copying the placeholder imports into target code. Current contracts come from
the linked canonical standards.

## Core Concepts (Historical Labels)

| Concept | Expected Type Name | Notes |
| --- | --- | --- |
| Entity | `IEntity<TId>` | Entities have identity. |
| Value Object | `IValueObject` | Prefer immutable records. |
| Domain Event | `IDomainEvent` | Public events. |
| Internal Domain Event | `IInternalDomainEvent` | Internal events for aggregate. |
| Aggregate Root | Java EzDDD `AggregateRoot<TId, TEvent>` | Historical source shape; current .NET normal Aggregates implement `IAggregateRoot<TId>` directly. |
| ES Aggregate Root | Java EzDDD `EsAggregateRoot<TId, TEvent>` | Historical source shape; current optional .NET abstraction is `EsAggregateRoot<TId>`. |
| Domain Event Mapper | `DomainEventMapper` | Map to/from `DomainEventData`. |
| Domain Event Type Mapper | `DomainEventTypeMapper` | Maps event type names. |

This file is historical provenance, not an active .NET import plan. Current
BuildingBlocks truth is the
[BuildingBlocks Reconstruction Contract](../../standards/BUILDING-BLOCKS-RECONSTRUCTION-CONTRACT.md).

## CQRS Concepts

| Concept | Expected Type Name |
| --- | --- |
| Command | `ICommand<TInput, TOutput>` |
| Query | `IQuery<TInput, TOutput>` |
| CQRS Output | `CqrsOutput` |
| Projection | `IProjection<TInput, TResult>` |
| Projection Input | `ProjectionInput` |

## Use Case Layer

| Concept | Expected Type Name |
| --- | --- |
| Input | `IInput` |
| Exit Code | `ExitCode` |
| Use Case Failure | `UseCaseFailureException` |

## Repository and Messaging

| Concept | Expected Type Name |
| --- | --- |
| Aggregate Repository | `IAggregateRepository<TAggregate, TId>` |
| Message Bus | `IMessageBus<TMessage>` |
| Domain Event Data | `DomainEventData` |

## Common Mistakes to Avoid

1. Do not mix `DomainEvent` with `DomainEventData`.  
   `DomainEventData` is the serialized transport shape.
2. Do not guess namespaces; select target-owned contracts and packages from
   repository evidence.
3. Always keep domain events immutable (record types recommended).
4. Use `DomainEventTypeMapper` for serialization stability.

## Historical Import Shape (Do Not Copy)

```csharp
// Historical placeholder namespaces retained only as provenance.
using EzDdd.Entity;
using EzDdd.Cqrs;
using EzDdd.UseCase;

public sealed record PlanCreated(/* ... */) : IDomainEvent
{
    public IDictionary<string, object> Metadata { get; init; } = new Dictionary<string, object>();
}
```

## Contract Utilities

Design by Contract semantics are defined by
[Design By Contract Semantics](../../standards/DESIGN-BY-CONTRACT.md). Helper names and
package selection remain target-owned; this historical mapping does not require
`uContract`.
