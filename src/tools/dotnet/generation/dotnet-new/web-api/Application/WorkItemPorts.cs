using AicfWebApi.Domain;

namespace AicfWebApi.Application;

public interface IAggregateRepository<TAggregate, TId>
    where TAggregate : IAggregateRoot<TId>
    where TId : notnull
{
    Task<TAggregate?> FindByIdAsync(TId id, CancellationToken cancellationToken);
    Task SaveAsync(TAggregate aggregate, CancellationToken cancellationToken);
}

public interface IWorkItemQueries
{
    Task<WorkItemDetails?> FindAsync(Guid id, CancellationToken cancellationToken);
}

public sealed record WorkItemDetails(Guid Id, string Title);
