using Published = ArchPrecept.Contracts.Domain;
using PublishedEs = ArchPrecept.Contracts.Domain.EventSourcing;

namespace PublishedDomainContract.IntegrationTests;

public sealed class PublishedContractTests
{
    /// <summary>Restores committed state with no pending events and rejects a second history load.</summary>
    [Fact]
    public void LoadingHistoryRestoresStateWithoutPendingEventsAndCannotRepeat()
    {
        Published.IDomainEvent[] history = null!;
        var counter = new Counter();
        Exception? clearing = null, reloading = null;

        this.Given(GivenTwoCommittedFacts, "two committed facts")
            .When(WhenLoadingHistory, "loading history")
            .Then(ThenRestoreCommittedStateWithoutPendingEvents, "restore committed state without pending events")
            .When(WhenClearingEventsOrReloading, "attempting to clear events or reload history")
            .Then(ThenRejectBothLifecycleOperations, "reject both lifecycle operations")
            .BDDfy();

        void GivenTwoCommittedFacts() => history = [new Fact(2), new Fact(3)];
        void WhenLoadingHistory() => counter.Load(history);

        void ThenRestoreCommittedStateWithoutPendingEvents()
        {
            Assert.Equal(5, counter.Total);
            Assert.Equal(2, counter.Version);
            Assert.Empty(counter.DomainEvents);
        }

        void WhenClearingEventsOrReloading()
        {
            clearing = Record.Exception(counter.ClearDomainEvents);
            reloading = Record.Exception(() => counter.Load([]));
        }

        void ThenRejectBothLifecycleOperations()
        {
            Assert.IsType<NotSupportedException>(clearing);
            Assert.IsType<InvalidOperationException>(reloading);
        }
    }

    /// <summary>Keeps pending facts through unconfirmed append and clears the batch only after confirmation.</summary>
    [Fact]
    public void PendingBatchSurvivesRejectedOrUnconfirmedAppendAndClearsOnConfirmation()
    {
        Counter counter = null!;
        Fact fact = null!;
        Exception? badVersion = null, reloading = null;

        this.Given(GivenACounterAtRevisionTwo, "a counter at revision two")
            .When(WhenChangingTheCounter, "changing the counter")
            .Then(ThenKeepTheNewFactPending, "keep the new fact pending")
            .When(WhenConfirmingTheWrongVersion, "confirming the wrong version")
            .Then(ThenRejectTheVersionAndKeepTheExactBatchPending, "reject the version and keep the exact batch pending")
            .When(WhenConfirmingTheCapturedBatch, "confirming the captured batch")
            .Then(ThenAdvanceTheVersionAndClearPendingEvents, "advance the version and clear pending events")
            .When(WhenLoadingHistoryAgain, "loading history again")
            .Then(ThenRejectRepeatedLoading, "reject repeated loading")
            .BDDfy();

        void GivenACounterAtRevisionTwo() => counter = LoadedCounter();
        void WhenChangingTheCounter() => counter.Change(4);

        void ThenKeepTheNewFactPending()
        {
            Assert.Equal(9, counter.Total);
            Assert.Equal(2, counter.Version);
            fact = Assert.IsType<Fact>(Assert.Single(counter.DomainEvents));
            Assert.Equal(4, fact.Delta);
        }

        void WhenConfirmingTheWrongVersion() =>
            badVersion = Record.Exception(() => counter.MarkChangesAsCommitted(99));

        void ThenRejectTheVersionAndKeepTheExactBatchPending()
        {
            Assert.IsType<InvalidOperationException>(badVersion);
            Assert.Equal(2, counter.Version);
            Assert.Same(fact, Assert.Single(counter.DomainEvents));
            // The caller captures this exact batch and waits to reconcile unknown append outcomes.
            var pending = counter.DomainEvents.ToArray();
            var expectedRevision = counter.Version;
            Assert.Equal(2, expectedRevision);
            Assert.Same(fact, Assert.Single(pending));
            Assert.Same(fact, Assert.Single(counter.DomainEvents));
        }

        void WhenConfirmingTheCapturedBatch() => counter.MarkChangesAsCommitted(3);

        void ThenAdvanceTheVersionAndClearPendingEvents()
        {
            Assert.Equal(3, counter.Version);
            Assert.Empty(counter.DomainEvents);
        }

        void WhenLoadingHistoryAgain() => reloading = Record.Exception(() => counter.Load([]));
        void ThenRejectRepeatedLoading() => Assert.IsType<InvalidOperationException>(reloading);
    }

    /// <summary>Rejects subsequent operations on an instance whose history replay failed.</summary>
    [Fact]
    public void FailedReplayRejectsFurtherOperationsOnTheSameInstance()
    {
        var counter = new Counter();
        Published.IDomainEvent[] history = null!;
        Exception? replay = null, change = null, commit = null, reload = null;

        this.Given(GivenHistoryContainingAnUnknownFact, "history containing an unknown fact")
            .When(WhenLoadingHistory, "loading history")
            .Then(ThenRefuseTheUnsupportedFact, "refuse the unsupported fact")
            .When(WhenReusingTheFailedCounter, "reusing the failed counter")
            .Then(ThenRejectAllFurtherLifecycleOperations, "reject all further lifecycle operations")
            .BDDfy();

        void GivenHistoryContainingAnUnknownFact() => history = [new Fact(2), new UnknownFact()];
        void WhenLoadingHistory() => replay = Record.Exception(() => counter.Load(history));
        void ThenRefuseTheUnsupportedFact() => Assert.IsType<NotSupportedException>(replay);

        void WhenReusingTheFailedCounter()
        {
            change = Record.Exception(() => counter.Change(1));
            commit = Record.Exception(() => counter.MarkChangesAsCommitted(counter.Version));
            reload = Record.Exception(() => counter.Load([]));
        }

        void ThenRejectAllFurtherLifecycleOperations()
        {
            Assert.IsType<InvalidOperationException>(change);
            Assert.IsType<InvalidOperationException>(commit);
            Assert.IsType<InvalidOperationException>(reload);
        }
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
