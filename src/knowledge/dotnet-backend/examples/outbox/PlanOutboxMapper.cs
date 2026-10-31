using System;
using System.Collections.Generic;
using System.Linq;
using Example.Plans.Domain;
using Example.Plans.UseCases.Port;
using Example.Shared.Outbox;

namespace Example.Plans.Outbox;

public static class PlanOutboxMapper
{
    public static PlanData ToData(Plan plan)
    {
        ArgumentNullException.ThrowIfNull(plan);

        // This portfolio does not supply a complete current-state persistence
        // contract (including next-task ID and persisted metadata). Never write
        // default values or invent creation timestamps to pretend it does.
        throw new NotSupportedException(
            "Implement the target-selected complete state/metadata mapping before persistence.");
    }

    public static PlanDto ToDto(Plan plan)
    {
        ArgumentNullException.ThrowIfNull(plan);

        var dto = new PlanDto()
            .SetId(plan.Id.Value)
            .SetName(plan.Name)
            .SetUserId(plan.UserId);

        dto.SetProjects(plan.GetProjects().Values.Select(ProjectOutboxMapper.ToDto));
        return dto;
    }

    public static Plan ToDomain(PlanData planData)
    {
        ArgumentNullException.ThrowIfNull(planData);

        // DomainEventDatas is a non-mapped pending outbox batch, not committed
        // full history. Neither creation+Clear nor a partial replay restores this
        // state-based record. This adapter remains unavailable until the target
        // implements its complete versioned state-rehydration contract.
        throw new NotSupportedException(
            "Implement the target-selected complete state rehydration before command-side loads.");
    }

    private static readonly IOutboxMapper<Plan, PlanData> Mapper = new MapperImpl();

    public static IOutboxMapper<Plan, PlanData> NewMapper() => Mapper;

    private sealed class MapperImpl : IOutboxMapper<Plan, PlanData>
    {
        public Plan ToDomain(PlanData data) => PlanOutboxMapper.ToDomain(data);
        public PlanData ToData(Plan aggregateRoot) => PlanOutboxMapper.ToData(aggregateRoot);
    }
}

// Example placeholders; replace them with target-owned outbox contracts.
public interface IOutboxMapper<TAggregate, TData>
{
    TAggregate ToDomain(TData data);
    TData ToData(TAggregate aggregateRoot);
}

public static class DateProvider
{
    public static DateTimeOffset Now() => DateTimeOffset.UtcNow;
}
