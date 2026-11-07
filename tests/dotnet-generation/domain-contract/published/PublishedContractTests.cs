using Published = ArchPrecept.Contracts.Domain;
using PublishedEs = ArchPrecept.Contracts.Domain.EventSourcing;

namespace Generation.Tests;

public sealed class PublishedContractTests
{
    [Fact]
    public void LoadingHistoryRestoresStateWithoutPendingEventsAndCannotRepeat()
    {
        var counter = LoadedCounter();
        Assert.Equal(5, counter.Total);
        Assert.Equal(2, counter.Version);
        Assert.Empty(counter.DomainEvents);
        Assert.Throws<NotSupportedException>(counter.ClearDomainEvents);
        Assert.Throws<InvalidOperationException>(() => counter.Load([]));
    }

    [Fact]
    public void PendingBatchSurvivesRejectedOrUnconfirmedAppendAndClearsOnConfirmation()
    {
        var counter = LoadedCounter();
        counter.Change(4);
        Assert.Equal(9, counter.Total);
        Assert.Equal(2, counter.Version);
        var fact = Assert.IsType<Fact>(Assert.Single(counter.DomainEvents));
        Assert.Equal(4, fact.Delta);

        Assert.Throws<InvalidOperationException>(() => counter.MarkChangesAsCommitted(99));
        Assert.Equal(2, counter.Version);
        Assert.Same(fact, Assert.Single(counter.DomainEvents));

        // The caller captures this exact batch and waits to reconcile unknown append outcomes.
        var pending = counter.DomainEvents.ToArray();
        var expectedRevision = counter.Version;
        Assert.Equal(2, expectedRevision);
        Assert.Same(fact, Assert.Single(pending));
        Assert.Same(fact, Assert.Single(counter.DomainEvents));
        counter.MarkChangesAsCommitted(3); // Simulated durable whole-batch success.
        Assert.Equal(3, counter.Version);
        Assert.Empty(counter.DomainEvents);
    }

    [Fact]
    public void FailedReplayRejectsFurtherOperationsOnTheSameInstance()
    {
        var counter = new Counter();
        Assert.Throws<NotSupportedException>(() => counter.Load([new Fact(2), new UnknownFact()]));
        Assert.Throws<InvalidOperationException>(() => counter.Change(1));
        Assert.Throws<InvalidOperationException>(() => counter.MarkChangesAsCommitted(counter.Version));
        Assert.Throws<InvalidOperationException>(() => counter.Load([]));
    }

    private static Counter LoadedCounter()
    {
        var counter = new Counter();
        counter.Load([new Fact(2), new Fact(3)]);
        return counter;
    }

    private sealed record Fact(int Delta) : Published.IDomainEvent
    {
        public Guid EventId { get; } = Guid.NewGuid();
        public DateTime OccurredOn => DateTime.UnixEpoch;
    }

    private sealed record UnknownFact : Published.IDomainEvent
    {
        public Guid EventId { get; } = Guid.NewGuid();
        public DateTime OccurredOn => DateTime.UnixEpoch;
    }

    private sealed class Counter() : PublishedEs.EsAggregateRoot<string>("counter")
    {
        public int Total { get; private set; }
        public void Load(IEnumerable<Published.IDomainEvent> history) => LoadFromHistory(history);
        public void Change(int delta) => Apply(new Fact(delta));
        protected override void When(Published.IDomainEvent fact)
        {
            if (fact is not Fact known)
                throw new NotSupportedException("Unsupported event.");
            Total += known.Delta;
        }
    }
}
