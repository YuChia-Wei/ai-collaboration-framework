# Mapper Patterns (.NET)

## Overview

Mapper patterns translate objects between layers:
- Domain -> Data (persistence models)
- Data -> Domain (rebuild aggregates)
- Domain -> DTO (API responses)
- Data -> DTO (read models)

In Clean Architecture, mappers keep conversion logic isolated and explicit.

## Mapper Types

### Aggregate Mapper
- May expose `NewMapper()` where the selected outbox/repository adapter needs it;
  this illustrative adapter shape is not a requirement of every Mapper.
- Handles domain events and versioning.
- Converts nested entities.

### Entity Mapper
- No `NewMapper()` method.
- Local conversions only.

## Aggregate Mapper Template (C#)

```csharp
public static class PlanMapper
{
    public static PlanData ToData(Plan plan) { /* ... */ }
    public static Plan ToDomain(PlanData data) { /* ... */ }
    public static PlanDto ToDto(Plan plan) { /* ... */ }

    private static readonly IOutboxMapper<Plan, PlanData> Mapper = new MapperImpl();
    public static IOutboxMapper<Plan, PlanData> NewMapper() => Mapper;
}
```

## Entity Mapper Template (C#)

```csharp
public static class TaskMapper
{
    public static TaskData ToData(Task task) { /* ... */ }
    public static Task ToDomain(TaskData data) { /* ... */ }
    public static TaskDto ToDto(Task task) { /* ... */ }
}
```

## Best Practices

1. Use static methods (no mapper instances).
2. Always check nulls.
3. Provide batch conversion helpers.
4. For event sourcing, set stream name, event data, and timestamps.
5. Return complete required business state and no new publishable events under
   the selected rehydration protocol. Unknown cleanliness stops affected
   reconstruction; do not call `ClearDomainEvents()` as a generic repair.
6. Required-state failure propagates or returns an explicit failed Result with
   no usable Aggregate. Only explicitly selected optional display data may
   degrade, with visible incompleteness.
7. `PlanMapper.ToData` illustrates a pending append batch plus display fields;
   it is not a full-history snapshot. `ToDomain` requires a repository-supplied
   complete-history envelope and verifies its committed count and identity.
   There is no synthetic state-to-history fallback. The placeholder serializer
   must be replaced by a target-selected versioned mapping before execution.

## Common Mistakes

- Entity mappers exposing outbox mapper (only aggregate mappers should).
- Forgetting event sourcing metadata.
- Returning a reconstructed aggregate with historical or constructor-emitted events still pending.
- Swallowing required-state errors or overwriting missing business data with defaults.
- Treating a pending batch as full history, inventing historical events or clearing
  an unknown instance; local acknowledgement does not prove storage success.
- Using raw constructors instead of `ValueOf(...)`.

## Related Resources
- [Failure/lifecycle cases and optional CT-005 example](contract-cases.md)
- `../aggregate/README.md`
- `../dto/README.md`
