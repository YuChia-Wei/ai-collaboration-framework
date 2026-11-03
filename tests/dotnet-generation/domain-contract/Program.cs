using Published = ArchPrecept.Contracts.Domain;
using PublishedEs = ArchPrecept.Contracts.Domain.EventSourcing;
using Custom = BuildingBlocks.Domain;
using Sample = Example.Plans.Domain;

var cases = 0;
void Check(bool result, string scenario)
{
    if (!result) throw new InvalidOperationException(scenario);
    Console.WriteLine("PASS " + scenario);
    cases++;
}
void Throws<T>(Action action, string scenario) where T : Exception
{
    try { action(); }
    catch (T) { Check(true, scenario); return; }
    throw new InvalidOperationException("Expected " + typeof(T).Name + ": " + scenario);
}

var counter = new Counter();
counter.Load([new Fact(2), new Fact(3)]);
Check(counter.Total == 5 && counter.Version == 2 && counter.DomainEvents.Count == 0,
    "Given full history, when LoadFromHistory succeeds, then state/version restored and pending empty");
Throws<NotSupportedException>(counter.ClearDomainEvents,
    "Given CT-005, when generic Clear is called, then it is rejected");
counter.Change(4);
Check(counter.Total == 9 && counter.Version == 2 && counter.DomainEvents.Count == 1,
    "Given rehydrated state, when a new command applies, then only the new fact is pending");
Throws<InvalidOperationException>(() => counter.MarkChangesAsCommitted(99),
    "Given pending data, when commit version mismatches, then confirmation fails");
Check(counter.Version == 2 && counter.DomainEvents.Count == 1,
    "Given rejected confirmation, then committed version and pending remain intact");

// A caller/store test double, not an event-store implementation or atomicity proof.
// Failed or unknown append never invokes local confirmation. Reconcile unknown
// outcome before any retry. The verified success receipt confirms this exact batch.
var pending = counter.DomainEvents.ToArray();
var expectedRevision = counter.Version;
Check(expectedRevision == 2 && pending.Length == 1 && counter.DomainEvents.Count == 1,
    "Given failed/unknown append, when awaiting reconciliation, then pending is retained");
var confirmedStoredVersion = 3; // Simulated successful append of the captured batch.
counter.MarkChangesAsCommitted(confirmedStoredVersion);
Check(counter.Version == 3 && counter.DomainEvents.Count == 0,
    "Given confirmed whole-batch append, when acknowledged, then pending clears and version advances");
Throws<InvalidOperationException>(() => counter.Load([]),
    "Given an already started instance, when history reloads, then replay is rejected");

var poisoned = new Counter();
Throws<NotSupportedException>(() => poisoned.Load([new Fact(2), new UnknownFact()]),
    "Given unknown history after a valid fact, when replay fails, then failure escapes");
Throws<InvalidOperationException>(() => poisoned.Change(1),
    "Given poisoned replay state, when a new command applies, then it is rejected");
Throws<InvalidOperationException>(() => poisoned.MarkChangesAsCommitted(poisoned.Version),
    "Given poisoned replay state, when commit is requested, then it is rejected");
Throws<InvalidOperationException>(() => poisoned.Load([]),
    "Given poisoned replay state, when replay retries on the same instance, then it is rejected");
// Discard poisoned; a fresh instance is the only subsequent reconstruction target.

var custom = new CustomCounter([new Fact(2), new Fact(3)]);
Check(custom.Total == 5 && custom.Version == 2 && custom.DomainEvents.Count == 0,
    "Given package-free Replay, when full history loads, then no new pending facts exist");
custom.Change(4);
Check(custom.Version == 2 && custom.DomainEvents.Count == 1,
    "Given package-free new behavior, then pending stays separate from committed version");
custom.MarkChangesAsCommitted(3); // Same simulated durable-success prerequisite.
Check(custom.Version == 3 && custom.DomainEvents.Count == 0,
    "Given package-free verified append, when confirmed, then the equivalent protocol completes");
var planId = Sample.PlanId.ValueOf("plan");
var projectId = Sample.ProjectId.ValueOf("project");
var projectName = Sample.ProjectName.ValueOf("Project");
var taskId = Sample.TaskId.ValueOf("1");
var metadata = new Dictionary<string, string>();
var occurred = DateTimeOffset.UnixEpoch;
var created = new Sample.PlanEvents.PlanCreated(planId, "Plan", "user", metadata, Guid.NewGuid(), occurred);
var projectCreated = new Sample.PlanEvents.ProjectCreated(planId, projectId, projectName, metadata, Guid.NewGuid(), occurred);
var taskCreated = new Sample.PlanEvents.TaskCreated(planId, projectId, projectName, taskId, "Task", metadata, Guid.NewGuid(), occurred);
var plan = new Sample.Plan([created, projectCreated, taskCreated]);
Check(plan.GetProject(projectId)?.HasTask(taskId) == true && plan.Version == 3 && plan.DomainEvents.Count == 0,
    "Given complete nested Plan history, when reconstructed, then required child state is restored");
Throws<InvalidOperationException>(() => new Sample.Plan([]),
    "Given absent Plan history, when reconstructed, then no unset Aggregate is returned");
Throws<InvalidOperationException>(() => new Sample.Plan([created, taskCreated]),
    "Given a task fact without its project, when reconstructed, then partial success is rejected");
var checkedTask = new Sample.PlanEvents.TaskChecked(planId, projectId, taskId, metadata, Guid.NewGuid(), occurred);
Throws<InvalidOperationException>(() => new Sample.Plan([created, projectCreated, checkedTask]),
    "Given a task update without its task, when reconstructed, then partial success is rejected");
Throws<NotSupportedException>(() => new Sample.Plan([created, new UnsupportedPlanFact(planId)]),
    "Given an unsupported Plan event, when reconstructed, then it cannot be silently ignored");
Console.WriteLine($"{cases} bounded contract cases passed; no real event store/broker tested.");

sealed record Fact(int Delta) : Published.IDomainEvent, Custom.IDomainEvent
{
    public Guid EventId { get; } = Guid.NewGuid();
    public DateTime OccurredOn { get; } = DateTime.UnixEpoch;
    DateTimeOffset Custom.IDomainEvent.OccurredOn => new(OccurredOn);
}
sealed record UnknownFact : Published.IDomainEvent
{
    public Guid EventId { get; } = Guid.NewGuid();
    public DateTime OccurredOn => DateTime.UnixEpoch;
}
sealed record UnsupportedPlanFact(Sample.PlanId PlanIdentity) : Sample.PlanEvents.PlanEvent(
    PlanIdentity, new Dictionary<string, string>(), Guid.NewGuid(), DateTimeOffset.UnixEpoch);
sealed class Counter : PublishedEs.EsAggregateRoot<string>
{
    public Counter() : base("counter") { }
    public int Total { get; private set; }
    public void Load(IEnumerable<Published.IDomainEvent> history) => LoadFromHistory(history);
    public void Change(int delta) => Apply(new Fact(delta));
    protected override void When(Published.IDomainEvent fact)
    {
        if (fact is not Fact known) throw new NotSupportedException("Unsupported event.");
        Total += known.Delta;
    }
}
sealed class CustomCounter : Custom.EsAggregateRoot<string>
{
    public override string Id => "counter";
    public int Total { get; private set; }
    public CustomCounter(IEnumerable<Custom.IDomainEvent> history) => Replay(history);
    public void Change(int delta) => Apply(new Fact(delta));
    protected override void When(Custom.IDomainEvent fact)
    {
        if (fact is not Fact known) throw new NotSupportedException("Unsupported event.");
        Total += known.Delta;
    }
}
