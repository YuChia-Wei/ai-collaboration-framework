using System;
using System.Collections.Generic;
using System.Linq;
using Example.Plans.Domain;

namespace Example.Plans.UseCases.Port;

public static class PlanMapper
{
    public static PlanData ToData(Plan plan)
    {
        ArgumentNullException.ThrowIfNull(plan);

        var planData = new PlanData(plan.Version);
        planData.PlanId = plan.Id.Value;
        planData.Name = plan.Name;
        planData.UserId = plan.UserId;
        planData.IsDeleted = plan.IsDeleted;

        planData.StreamName = plan.StreamName;
        // Pending append batch, not the complete history expected by ToDomain.
        planData.DomainEventDatas = plan.DomainEvents
            .Select(DomainEventMapper.ToData)
            .ToList();

        // Sync projects
        planData.ProjectDatas.RemoveAll(projectData =>
            !plan.GetProjects().ContainsKey(ProjectId.ValueOf(projectData.ProjectId)));

        foreach (var project in plan.GetProjects().Values)
        {
            var existing = planData.ProjectDatas
                .FirstOrDefault(pd => pd.ProjectId == project.Id.Value);

            if (existing == null)
            {
                planData.ProjectDatas.Add(ProjectMapper.ToData(project));
                continue;
            }

            existing.TaskDatas.RemoveAll(taskData =>
                !project.GetTasks().ContainsKey(TaskId.ValueOf(taskData.TaskId)));

            foreach (var task in project.GetTasks().Values)
            {
                var existingTask = existing.TaskDatas
                    .FirstOrDefault(td => td.TaskId == task.Id.Value);

                if (existingTask == null)
                {
                    existing.TaskDatas.Add(TaskMapper.ToData(task, project.Id.Value));
                    continue;
                }

                existingTask.Name = task.Name;
                existingTask.IsDone = task.IsDone;
                existingTask.TagIds = task.Tags.Select(tag => tag.Value).ToHashSet();
            }
        }

        return planData;
    }

    public static List<PlanData> ToData(IEnumerable<Plan> plans) =>
        plans.Select(ToData).ToList();

    public static PlanDto ToDto(Plan plan)
    {
        ArgumentNullException.ThrowIfNull(plan);

        var dto = new PlanDto()
            .SetId(plan.Id.Value)
            .SetName(plan.Name)
            .SetUserId(plan.UserId);

        dto.SetProjects(plan.GetProjects().Values.Select(ProjectMapper.ToDto));
        return dto;
    }

    public static Plan ToDomain(PlanData planData)
    {
        ArgumentNullException.ThrowIfNull(planData);

        // Repository input must be a complete committed history, never ToData's
        // pending append batch. This example has no selected snapshot protocol.
        if (!planData.ContainsCompleteHistory || planData.DomainEventDatas is not { Count: > 0 })
            throw new InvalidOperationException("A complete Plan history is required.");

        var history = planData.DomainEventDatas
            .Select(DomainEventMapper.ToDomain)
            .Cast<PlanEvents.IPlanEvent>()
            .ToList(); // Unsupported payload/version failures escape.
        if (history.Count != planData.Version || history[0] is not PlanEvents.PlanCreated
            || history.Skip(1).Any(e => e is PlanEvents.PlanCreated)
            || history.Any(e => e.PlanId.Value != planData.PlanId))
            throw new InvalidOperationException("History count, creation or stream identity mismatch.");

        var plan = new Plan(history); // Replay failure exposes no usable instance.
        plan.EnsureInvariant();
        if (plan.DomainEvents.Count != 0)
            throw new InvalidOperationException("Replay contract produced new pending events.");
        return plan; // No Version setter, manufactured history or generic Clear.
    }

    public static List<Plan> ToDomain(IEnumerable<PlanData> planDatas) =>
        planDatas.Select(ToDomain).ToList();

    public static PlanDto ToDto(PlanData planData)
    {
        ArgumentNullException.ThrowIfNull(planData);

        var dto = new PlanDto()
            .SetId(planData.PlanId)
            .SetName(planData.Name)
            .SetUserId(planData.UserId);

        dto.SetProjects(planData.ProjectDatas.Select(ProjectMapper.ToDto));
        return dto;
    }

    public static List<PlanDto> ToDto(IEnumerable<PlanData> planDatas) =>
        planDatas.Select(ToDto).ToList();

    // Aggregate mappers expose an Outbox mapper.
    private static readonly IOutboxMapper<Plan, PlanData> Mapper = new MapperImpl();

    public static IOutboxMapper<Plan, PlanData> NewMapper() => Mapper;

    private sealed class MapperImpl : IOutboxMapper<Plan, PlanData>
    {
        public Plan ToDomain(PlanData data) => PlanMapper.ToDomain(data);
        public PlanData ToData(Plan aggregateRoot) => PlanMapper.ToData(aggregateRoot);
    }
}

// TODO: Replace placeholders below with target-selected mapping, persistence, and messaging adapters.
public interface IOutboxMapper<TAggregate, TData>
{
    TAggregate ToDomain(TData data);
    TData ToData(TAggregate aggregateRoot);
}

public static class DomainEventMapper
{
    public static DomainEventData ToData(object domainEvent) =>
        throw new NotSupportedException("Select a versioned event serializer before use.");
    public static object ToDomain(DomainEventData data) =>
        throw new NotSupportedException("Select a versioned event deserializer before use.");
}

public sealed class DomainEventData { }

public sealed class PlanData
{
    public PlanData(int version) => Version = version;

    // Only the repository may set this after loading full committed history.
    public bool ContainsCompleteHistory { get; set; }
    public int Version { get; set; }
    public string PlanId { get; set; } = string.Empty;
    public string Name { get; set; } = string.Empty;
    public string UserId { get; set; } = string.Empty;
    public bool IsDeleted { get; set; }
    public string StreamName { get; set; } = string.Empty;
    public List<DomainEventData> DomainEventDatas { get; set; } = new();
    public List<ProjectData> ProjectDatas { get; set; } = new();
}

public sealed class ProjectData
{
    public string ProjectId { get; set; } = string.Empty;
    public string Name { get; set; } = string.Empty;
    public List<TaskData> TaskDatas { get; set; } = new();
}

public sealed class TaskData
{
    public string TaskId { get; set; } = string.Empty;
    public string Name { get; set; } = string.Empty;
    public bool IsDone { get; set; }
    public string? Deadline { get; set; }
    public HashSet<string> TagIds { get; set; } = new();
}
