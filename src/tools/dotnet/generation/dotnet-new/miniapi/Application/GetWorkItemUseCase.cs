namespace AicfMiniApi.Application;

public interface IGetWorkItemUseCase
{
    Task<WorkItemDetails?> ExecuteAsync(Guid id, CancellationToken cancellationToken);
}

public sealed class GetWorkItemUseCase(IWorkItemQueries queries) : IGetWorkItemUseCase
{
    public Task<WorkItemDetails?> ExecuteAsync(Guid id, CancellationToken cancellationToken)
        => queries.FindAsync(id, cancellationToken);
}
