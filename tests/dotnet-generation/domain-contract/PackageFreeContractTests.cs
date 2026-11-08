using Custom = BuildingBlocks.Domain;
using Sample = Example.Plans.Domain;

namespace DomainContract.UnitTests;

public sealed class PackageFreeContractTests
{
    private static readonly IReadOnlyDictionary<string, string> EmptyMetadata = new Dictionary<string, string>();

    [Fact]
    public void ReplayRestoresCommittedStateAndOnlyNewFactsRemainPendingUntilConfirmation()
    {
        CustomCounter counter = null!;
        Custom.IDomainEvent[] history = null!;

        this.Given(GivenTwoCommittedCounterFacts, "two committed counter facts")
            .When(WhenReplayingCounterHistory, "replaying counter history")
            .Then(ThenRestoreTheCommittedStateWithoutPendingEvents, "restore the committed state without pending events")
            .When(WhenChangingTheReplayedCounter, "changing the replayed counter")
            .Then(ThenLeaveTheNewFactPending, "leave the new fact pending")
            .When(WhenConfirmingThePendingFact, "confirming the pending fact")
            .Then(ThenAdvanceTheCommittedVersionAndClearPendingEvents, "advance the committed version and clear pending events")
            .BDDfy();

        void GivenTwoCommittedCounterFacts() => history = [new Fact(2), new Fact(3)];

        void WhenReplayingCounterHistory() => counter = new CustomCounter(history);

        void ThenRestoreTheCommittedStateWithoutPendingEvents()
        {
            Assert.Equal((5, 2), (counter.Total, counter.Version));
            Assert.Empty(counter.DomainEvents);
        }

        void WhenChangingTheReplayedCounter() => counter.Change(4);

        void ThenLeaveTheNewFactPending()
        {
            Assert.Equal(2, counter.Version);
            Assert.Single(counter.DomainEvents);
        }

        void WhenConfirmingThePendingFact() => counter.MarkChangesAsCommitted(3);

        void ThenAdvanceTheCommittedVersionAndClearPendingEvents()
        {
            Assert.Equal(3, counter.Version);
            Assert.Empty(counter.DomainEvents);
        }
    }

    [Fact]
    public void CompletePlanHistoryRestoresRequiredNestedState()
    {
        PlanHistory history = null!;
        Example.Plans.Domain.Plan plan = null!;

        this.Given(GivenThePlanProjectAndTaskFacts, "the plan project and task facts")
            .When(WhenReplayingThePlanHistory, "replaying the plan history")
            .Then(ThenRestoreTheNestedTaskWithoutPendingEvents, "restore the nested task without pending events")
            .BDDfy();

        void GivenThePlanProjectAndTaskFacts()
        {
            history = new PlanHistory();
        }

        void WhenReplayingThePlanHistory()
        {
            plan = new Sample.Plan([history.Created, history.ProjectCreated, history.TaskCreated]);
        }

        void ThenRestoreTheNestedTaskWithoutPendingEvents()
        {
            Assert.True(plan.GetProject(history.ProjectId)?.HasTask(history.TaskId) == true);
            Assert.Equal(3, plan.Version);
            Assert.Empty(plan.DomainEvents);
        }
    }

    [Fact]
    public void EmptyPlanHistoryCannotReturnAnAggregate() =>
        Assert.Throws<InvalidOperationException>(() => new Sample.Plan([]));

    [Fact]
    public void TaskCreationWithoutItsProjectCannotReturnAnAggregate()
    {
        var history = new PlanHistory();
        Assert.Throws<InvalidOperationException>(() => new Sample.Plan([history.Created, history.TaskCreated]));
    }

    [Fact]
    public void TaskUpdateWithoutItsTaskCannotReturnAnAggregate()
    {
        var history = new PlanHistory();
        Assert.Throws<InvalidOperationException>(() => new Sample.Plan([history.Created, history.ProjectCreated, history.TaskChecked]));
    }

    [Fact]
    public void UnsupportedPlanFactCannotBeSilentlyIgnored()
    {
        var history = new PlanHistory();
        Assert.Throws<NotSupportedException>(() => new Sample.Plan([history.Created, new UnsupportedPlanFact(history.PlanId)]));
    }

    private sealed class PlanHistory
    {
        private readonly Sample.ProjectName _projectName = Sample.ProjectName.ValueOf("Project");
        public Sample.PlanId PlanId { get; } = Sample.PlanId.ValueOf("plan");
        public Sample.ProjectId ProjectId { get; } = Sample.ProjectId.ValueOf("project");
        public Sample.TaskId TaskId { get; } = Sample.TaskId.ValueOf("1");

        public Sample.PlanEvents.PlanCreated Created => new(PlanId, "Plan", "user", EmptyMetadata, Guid.NewGuid(), DateTimeOffset.UnixEpoch);
        public Sample.PlanEvents.ProjectCreated ProjectCreated =>
            new(PlanId, ProjectId, _projectName, EmptyMetadata, Guid.NewGuid(), DateTimeOffset.UnixEpoch);
        public Sample.PlanEvents.TaskCreated TaskCreated =>
            new(PlanId, ProjectId, _projectName, TaskId, "Task", EmptyMetadata, Guid.NewGuid(), DateTimeOffset.UnixEpoch);
        public Sample.PlanEvents.TaskChecked TaskChecked =>
            new(PlanId, ProjectId, TaskId, EmptyMetadata, Guid.NewGuid(), DateTimeOffset.UnixEpoch);
    }

    private sealed record UnsupportedPlanFact(Sample.PlanId PlanIdentity) : Sample.PlanEvents.PlanEvent(
        PlanIdentity, EmptyMetadata, Guid.NewGuid(), DateTimeOffset.UnixEpoch);

    private sealed record Fact(int Delta) : Custom.IDomainEvent
    {
        public Guid EventId { get; } = Guid.NewGuid();
        public DateTimeOffset OccurredOn => DateTimeOffset.UnixEpoch;
    }

    private sealed class CustomCounter : Custom.EsAggregateRoot<string>
    {
        public CustomCounter(IEnumerable<Custom.IDomainEvent> history) => Replay(history);
        public override string Id => "counter";
        public int Total { get; private set; }
        public void Change(int delta) => Apply(new Fact(delta));
        protected override void When(Custom.IDomainEvent fact)
        {
            if (fact is not Fact known)
                throw new NotSupportedException("Unsupported event.");
            Total += known.Delta;
        }
    }
}
