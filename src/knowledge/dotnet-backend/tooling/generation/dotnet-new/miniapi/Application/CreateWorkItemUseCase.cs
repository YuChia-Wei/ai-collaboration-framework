using AicfMiniApi.Domain;

namespace AicfMiniApi.Application;

public sealed record CreateWorkItemInput(string Title);

public interface ICreateWorkItemUseCase
{
    Task<WorkItemDetails> ExecuteAsync(
        CreateWorkItemInput input,
        CancellationToken cancellationToken);
}

public sealed class CreateWorkItemUseCase(
    IAggregateRepository<WorkItem, Guid> repository) : ICreateWorkItemUseCase
{
    public async Task<WorkItemDetails> ExecuteAsync(
        CreateWorkItemInput input,
        CancellationToken cancellationToken)
    {
        var item = WorkItem.Create(input.Title);
        await repository.SaveAsync(item, cancellationToken);
        return new WorkItemDetails(item.Id, item.Title);
    }
}
