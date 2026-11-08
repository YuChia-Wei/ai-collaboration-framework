using System.Reflection;
using Generation.TestSupport;
using static SnippetTool.IntegrationTests.SnippetTests;

namespace SnippetTool.IntegrationTests;

[Collection("Generation SDK")]
public sealed class GeneratedFragmentTests
{
    [SnippetSdkFact]
    [Trait("Boundary", "Sdk")]
    public void RenderedFragmentsCompileAndRetainTheirBehaviorInAConsumer()
    {
        using var fixture = new GenerationFixture();
        string project = null!;

        this.Given(GivenAConsumerWithRenderedFragments, "a consumer with rendered fragments")
            .When(WhenBuildingTheConsumerWithTheSdk, "building the consumer with the sdk")
            .Then(ThenLoadAndExerciseTheCompiledContracts, "load and exercise the compiled contracts")
            .BDDfy();

        void GivenAConsumerWithRenderedFragments()
        {
            project = fixture.Write("Consumer.csproj", """
                <Project Sdk="Microsoft.NET.Sdk">
                  <PropertyGroup>
                    <TargetFramework>net10.0</TargetFramework>
                    <Nullable>enable</Nullable>
                    <TreatWarningsAsErrors>true</TreatWarningsAsErrors>
                  </PropertyGroup>
                </Project>
                """);
            var declaration = Render(fixture, "interface-method", new { methodName = "ReadAsync", returnType = "Task<string>" });
            var guard = Render(fixture, "string-guard", new { parameterName = "label" });
            var custom = Text(RenderCustom(fixture), "text");
            var nullGuard = Render(fixture, "null-guard", new { parameterName = "value" });
            var cancellation = Render(fixture, "cancellation-guard", new { tokenName = "token" });
            var assignment = Render(fixture, "constructor-assignment", new { fieldName = "_value", parameterName = "value" });
            var identifier = Render(fixture, "guid-id", new { typeName = "OrderId" });
            var property = Render(fixture, "readonly-property", new { propertyName = "Count", propertyType = "int" });
            var contracts = Render(fixture, "domain-contracts");
            var aggregate = Render(fixture, "es-aggregate");
            fixture.Write("Consumer.cs", $$"""
                using System;
                using System.Collections.Generic;
                using System.Threading;
                using System.Threading.Tasks;

                {{identifier}}
                {{contracts}}
                {{aggregate}}
                interface IReader
                {
                    {{declaration}}
                }
                sealed class Holder
                {
                    private readonly object _value;
                    {{property}}
                    public Holder(object value) { {{assignment}} Count = 3; }
                    public object Value => _value;
                }
                sealed record Changed(Guid EventId, DateTimeOffset OccurredOn) : IDomainEvent;
                sealed class Counter : EsAggregateRoot<Guid>
                {
                    public override Guid Id => Guid.Empty;
                    public int Count { get; private set; }
                    public Counter(IEnumerable<IDomainEvent> history) { Replay(history); }
                    public void Add() => Apply(new Changed(Guid.NewGuid(), DateTimeOffset.UnixEpoch));
                    protected override void When(IDomainEvent e)
                    {
                        if (e is not Changed) throw new ArgumentException("unsupported");
                        Count++;
                    }
                }
                public static class Consumer
                {
                    private static Counter? _counter;

                    public static void Guard(string? label) { {{guard}} }
                    public static void NullGuard(object? value) { {{nullGuard}} }
                    public static void Cancel(CancellationToken token) { {{cancellation}} }
                    public static (object, int) Hold(object value)
                    {
                        var holder = new Holder(value);
                        return (holder.Value, holder.Count);
                    }
                    public static bool IdEquals(Guid left, Guid right) => new OrderId(left) == new OrderId(right);
                    public static string Probe()
                    {
                        {{custom}}
                    }
                    public static void Replay() => _counter = new Counter(new[] { new Changed(Guid.NewGuid(), DateTimeOffset.UnixEpoch) });
                    public static void Add() => _counter!.Add();
                    public static void Commit(int version) => _counter!.MarkChangesAsCommitted(version);
                    public static (int, int, int) State() => (_counter!.Count, _counter.Version, _counter.DomainEvents.Count);
                }
                """);
        }

        async Task WhenBuildingTheConsumerWithTheSdk() => await fixture.Build(project, "Release");

        void ThenLoadAndExerciseTheCompiledContracts()
        {
            var compiled = Assembly.Load(File.ReadAllBytes(Path.Combine(fixture.Root, "bin", "Release", "net10.0", "Consumer.dll")));
            var consumer = compiled.GetType("Consumer", throwOnError: true)!;
            T Bind<T>(string method) where T : Delegate => consumer.GetMethod(method)!.CreateDelegate<T>();

            var runGuard = Bind<Action<string?>>("Guard");
            runGuard("ok");
            Assert.Throws<ArgumentNullException>("label", () => runGuard(null));
            Assert.Throws<ArgumentException>("label", () => runGuard(""));
            Assert.Throws<ArgumentException>("label", () => runGuard(" \t"));
            Assert.Equal("${顯示}", Bind<Func<string>>("Probe")());

            var value = new object();
            var runNullGuard = Bind<Action<object?>>("NullGuard");
            runNullGuard(value);
            Assert.Throws<ArgumentNullException>("value", () => runNullGuard(null));

            var cancel = Bind<Action<CancellationToken>>("Cancel");
            cancel(CancellationToken.None);
            Assert.Throws<OperationCanceledException>(() => cancel(new CancellationToken(true)));

            var hold = Bind<Func<object, (object Value, int Count)>>("Hold");
            var holder = hold(value);
            Assert.Same(value, holder.Value);
            Assert.Equal(3, holder.Count);
            Assert.Throws<ArgumentNullException>("value", () => hold(null!));

            var id = Guid.NewGuid();
            Assert.True(Bind<Func<Guid, Guid, bool>>("IdEquals")(id, id));

            var state = Bind<Func<(int, int, int)>>("State");
            Bind<Action>("Replay")();
            Assert.Equal((1, 1, 0), state());
            Bind<Action>("Add")();
            Assert.Equal((2, 1, 1), state());
            var commit = Bind<Action<int>>("Commit");
            Assert.Throws<InvalidOperationException>(() => commit(3));
            Assert.Equal((2, 1, 1), state());
            commit(2);
            Assert.Equal((2, 2, 0), state());
        }
    }
}
