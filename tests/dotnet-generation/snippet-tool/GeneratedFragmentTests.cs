using static SnippetTool.IntegrationTests.SnippetTestSupport;
using System.Runtime.Loader;
using Microsoft.CodeAnalysis;
using Microsoft.CodeAnalysis.CSharp;
using Microsoft.CodeAnalysis.Emit;
using Generation.TestSupport;
using static SnippetTool.IntegrationTests.SnippetTests;

namespace SnippetTool.IntegrationTests;

public sealed class GeneratedFragmentTests
{
    [Fact]
    public void Should_retain_the_rendered_fragment_contracts_when_compiled_in_a_consumer()
    {
        using var fixture = new GenerationFixture();
        using var image = new MemoryStream();
        var value = new object();
        string source = null!;
        EmitResult emitted = null!;
        string? literal = null;
        (object Value, int Count) holder = default;
        bool? idsEqual = null;
        (int Count, int Version, int Pending) replayed = default, pending = default, rejected = default, committed = default;
        Exception? nullLabel = null, emptyLabel = null, whitespaceLabel = null, nullValue = null;
        Exception? canceled = null, nullConstructorValue = null, wrongCommitVersion = null;

        this.Given(GivenAConsumerWithRenderedFragments, "a consumer with rendered fragments")
            .When(WhenCompilingTheConsumerWithRoslyn, "compiling the consumer with roslyn")
            .Then(ThenEmitTheConsumerWithoutWarnings, "emit the consumer without warnings")
            .When(WhenExercisingTheCompiledConsumerContracts, "exercising the compiled consumer contracts")
            .Then(ThenPreserveTheExpectedConsumerBehavior, "preserve the expected consumer behavior")
            .BDDfy();

        void GivenAConsumerWithRenderedFragments()
        {
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
            source = $$"""
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
                """;
        }

        void WhenCompilingTheConsumerWithRoslyn()
        {
            var references = Directory.EnumerateFiles(Path.Combine(AppContext.BaseDirectory, "refs"), "*.dll")
                .Select(path => MetadataReference.CreateFromFile(path));
            var syntax = CSharpSyntaxTree.ParseText(source, new CSharpParseOptions(LanguageVersion.CSharp14));
            var options = new CSharpCompilationOptions(OutputKind.DynamicallyLinkedLibrary,
                optimizationLevel: OptimizationLevel.Release, nullableContextOptions: NullableContextOptions.Enable,
                generalDiagnosticOption: ReportDiagnostic.Error);
            emitted = CSharpCompilation.Create("SnippetConsumer", [syntax], references, options).Emit(image);
        }

        void ThenEmitTheConsumerWithoutWarnings() =>
            Assert.True(emitted.Success, string.Join(Environment.NewLine, emitted.Diagnostics));

        void WhenExercisingTheCompiledConsumerContracts()
        {
            image.Position = 0;
            var context = new AssemblyLoadContext("SnippetConsumer", isCollectible: true);
            try
            {
                var consumer = context.LoadFromStream(image).GetType("Consumer", throwOnError: true)!;
                T Bind<T>(string method) where T : Delegate => consumer.GetMethod(method)!.CreateDelegate<T>();

                var guard = Bind<Action<string?>>("Guard");
                guard("ok");
                nullLabel = Record.Exception(() => guard(null));
                emptyLabel = Record.Exception(() => guard(""));
                whitespaceLabel = Record.Exception(() => guard(" \t"));
                literal = Bind<Func<string>>("Probe")();

                var nullGuard = Bind<Action<object?>>("NullGuard");
                nullGuard(value);
                nullValue = Record.Exception(() => nullGuard(null));

                var cancel = Bind<Action<CancellationToken>>("Cancel");
                cancel(CancellationToken.None);
                canceled = Record.Exception(() => cancel(new CancellationToken(true)));

                var hold = Bind<Func<object, (object Value, int Count)>>("Hold");
                holder = hold(value);
                nullConstructorValue = Record.Exception(() => { _ = hold(null!); });

                var id = Guid.NewGuid();
                idsEqual = Bind<Func<Guid, Guid, bool>>("IdEquals")(id, id);

                var state = Bind<Func<(int, int, int)>>("State");
                Bind<Action>("Replay")();
                replayed = state();
                Bind<Action>("Add")();
                pending = state();
                var commit = Bind<Action<int>>("Commit");
                wrongCommitVersion = Record.Exception(() => commit(3));
                rejected = state();
                commit(2);
                committed = state();
            }
            finally
            {
                context.Unload();
            }
        }

        void ThenPreserveTheExpectedConsumerBehavior()
        {
            Assert.Equal("label", Assert.IsType<ArgumentNullException>(nullLabel).ParamName);
            Assert.Equal("label", Assert.IsType<ArgumentException>(emptyLabel).ParamName);
            Assert.Equal("label", Assert.IsType<ArgumentException>(whitespaceLabel).ParamName);
            Assert.Equal("${顯示}", literal);
            Assert.Equal("value", Assert.IsType<ArgumentNullException>(nullValue).ParamName);
            Assert.IsType<OperationCanceledException>(canceled);
            Assert.Same(value, holder.Value);
            Assert.Equal(3, holder.Count);
            Assert.Equal("value", Assert.IsType<ArgumentNullException>(nullConstructorValue).ParamName);
            Assert.True(idsEqual);
            Assert.Equal((1, 1, 0), replayed);
            Assert.Equal((2, 1, 1), pending);
            Assert.IsType<InvalidOperationException>(wrongCommitVersion);
            Assert.Equal((2, 1, 1), rejected);
            Assert.Equal((2, 2, 0), committed);
        }
    }
}
