using System.Collections.Concurrent;
using AicfWebApi.Application;
using AicfWebApi.Domain;

namespace AicfWebApi.Infrastructure;

public sealed class InMemoryWorkItems : IAggregateRepository<WorkItem, Guid>, IWorkItemQueries
{
    private readonly ConcurrentDictionary<Guid, WorkItem> items = new();

    public Task<WorkItem?> FindByIdAsync(Guid id, CancellationToken cancellationToken)
    {
        cancellationToken.ThrowIfCancellationRequested();
        return Task.FromResult(items.GetValueOrDefault(id));
    }

    public Task SaveAsync(WorkItem aggregate, CancellationToken cancellationToken)
    {
        cancellationToken.ThrowIfCancellationRequested();
        items[aggregate.Id] = aggregate;
        return Task.CompletedTask;
    }

    public async Task<WorkItemDetails?> FindAsync(Guid id, CancellationToken cancellationToken)
    {
        var item = await FindByIdAsync(id, cancellationToken);
        return item is null ? null : new WorkItemDetails(item.Id, item.Title);
    }
}
