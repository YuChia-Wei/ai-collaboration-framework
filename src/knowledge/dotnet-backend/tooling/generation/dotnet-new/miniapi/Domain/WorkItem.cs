namespace AicfMiniApi.Domain;

public sealed class WorkItem : IAggregateRoot<Guid>
{
    private WorkItem(Guid id, string title)
    {
        Id = id;
        Title = title;
    }

    public Guid Id { get; }
    public string Title { get; }

    public static WorkItem Create(string title)
    {
        ArgumentException.ThrowIfNullOrWhiteSpace(title);
        return new WorkItem(Guid.NewGuid(), title.Trim());
    }
}
