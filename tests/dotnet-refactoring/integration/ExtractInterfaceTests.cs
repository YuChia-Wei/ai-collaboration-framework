using Microsoft.CodeAnalysis.CSharp;
using Microsoft.CodeAnalysis.CSharp.Syntax;

namespace RefactorTool.IntegrationTests;

public sealed class ExtractInterfaceTests
{
    /// <summary>Preserves generic constraints, nullability, ref and out parameters, and consumer dispatch.</summary>
    [Fact]
    public void NullableGenericContractPreservesRefOutAndPrivateSetterBehavior()
    {
        const string source = """
            #nullable enable
            namespace Demo;
            public class Service<T> where T : class {
             public T? Value { get; private set; }
             public T? Read<U>(ref T? value, out int length) where U : unmanaged { length=value?.ToString()?.Length ?? 0; Value=value; return value; }
            }
            """;
        using var workspace = new SemanticWorkspace();
        Plan plan = null!;
        string runningTheConsumerAgainstThePlannedEditsResult = null!;

        this.Given(GivenANullableGenericClassWithRefOutAndPrivateSetter, "a nullable generic class with ref out and private setter")
            .When(WhenPlanningExtraction, "planning extraction")
            .Then(ThenPreserveTheSelectedGenericSignature, "preserve the selected generic signature")
            .When(WhenRunningTheConsumerAgainstThePlannedEdits, "running the consumer against the planned edits")
            .Then(ThenPreserveRuntimeBehaviorAndAuthoredFiles, "preserve runtime behavior and authored files")
            .BDDfy();

        void GivenANullableGenericClassWithRefOutAndPrivateSetter() => workspace.Add("A/Service.cs", source);

        async Task WhenPlanningExtraction()
        {
            plan = await workspace.PlanExtraction(workspace.Extract with
            {
                Symbol = "T:Demo.Service`1",
                Members = ["P:Demo.Service`1.Value", "M:Demo.Service`1.Read``1(`0@,System.Int32@)"]
            });
        }

        void ThenPreserveTheSelectedGenericSignature()
        {
            var contract = SemanticWorkspace.After(plan, workspace.Output);
            var declaration = Assert.Single(CSharpSyntaxTree.ParseText(contract).GetRoot().DescendantNodes().OfType<InterfaceDeclarationSyntax>());
            Assert.Equal("T", Assert.Single(declaration.TypeParameterList!.Parameters).Identifier.ValueText);
            Assert.Equal("where T : class", Assert.Single(declaration.ConstraintClauses).ToString());
            var property = Assert.Single(declaration.Members.OfType<PropertyDeclarationSyntax>());
            Assert.Equal("T?", property.Type.ToString());
            Assert.Equal("get", Assert.Single(property.AccessorList!.Accessors).Keyword.ValueText);
            var method = Assert.Single(declaration.Members.OfType<MethodDeclarationSyntax>());
            Assert.Equal("T?", method.ReturnType.ToString());
            Assert.Equal("where U : unmanaged", Assert.Single(method.ConstraintClauses).ToString());
            Assert.Equal("ref", Assert.Single(method.ParameterList.Parameters[0].Modifiers).ValueText);
            Assert.Equal("out", Assert.Single(method.ParameterList.Parameters[1].Modifiers).ValueText);
        }

        async Task WhenRunningTheConsumerAgainstThePlannedEdits() => runningTheConsumerAgainstThePlannedEditsResult = await workspace.RunConsumer(plan, """
            using Demo;
            using Contracts;
            public static class Probe
            {
                public static string Run()
                {
                    ISelected<string> s = new Service<string>();
                    string? value = null;
                    var first = s.Read<int>(ref value, out var a);
                    value = "abc";
                    var second = s.Read<int>(ref value, out var b);
                    return $"{first is null}|{a}|{second}|{b}|{s.Value}";
                }
            }
            """);

        void ThenPreserveRuntimeBehaviorAndAuthoredFiles()
        {
            Assert.Equal("True|0|abc|3|abc", runningTheConsumerAgainstThePlannedEditsResult);
            Assert.Equal(source, File.ReadAllText(workspace.Source));
            Assert.False(File.Exists(workspace.Output));
        }
    }

    /// <summary>Requires the exact declaration ID of a supported member on the selected class.</summary>
    [Theory]
    [InlineData("F:Demo.Service.Field", "unsupported_member")]
    [InlineData("M:Demo.Other.Get(System.Int32)", "invalid_members")]
    [InlineData("M:Demo.Service.Get", "invalid_members")]
    public void ExactDeclaredMethodOrPropertyIsRequired(string member, string code)
    {
        using var workspace = new SemanticWorkspace();
        byte[] before = null!;
        Exception? error = null;

        this.Given(GivenAClassAndAnIneligibleMemberId, "a class and an ineligible member ID")
            .When(WhenPlanningTheRequestedChange, "planning the requested change")
            .Then(ThenRefuseAndKeepAuthoredFiles, "refuse and keep authored files unchanged")
            .BDDfy();

        void GivenAClassAndAnIneligibleMemberId()
        {
            workspace.Add("A/Service.cs", SemanticWorkspace.Service);
            before = File.ReadAllBytes(workspace.Source);
        }

        async Task WhenPlanningTheRequestedChange() =>
            error = await Record.ExceptionAsync(() => workspace.PlanExtraction(workspace.Extract with { Members = [member] }));

        void ThenRefuseAndKeepAuthoredFiles()
        {
            var failure = Assert.IsType<RefactorFailure>(error);
            Assert.Equal(code, failure.Code);
            Assert.Equal(before, File.ReadAllBytes(workspace.Source));
            Assert.False(File.Exists(workspace.Output));
        }
    }

    /// <summary>Rejects repeated IDs in the explicit interface member selection.</summary>
    [Fact]
    public void DuplicateMemberIdsAreRefused()
    {
        using var workspace = new SemanticWorkspace();
        byte[] before = null!;
        Exception? error = null;

        this.Given(GivenAClassAndRepeatedPropertyIds, "a class and repeated property IDs")
            .When(WhenPlanningTheRequestedChange, "planning the requested change")
            .Then(ThenRefuseAndKeepAuthoredFiles, "refuse and keep authored files unchanged")
            .BDDfy();

        void GivenAClassAndRepeatedPropertyIds()
        {
            workspace.Add("A/Service.cs", SemanticWorkspace.Service);
            before = File.ReadAllBytes(workspace.Source);
        }

        async Task WhenPlanningTheRequestedChange() =>
            error = await Record.ExceptionAsync(() => workspace.PlanExtraction(workspace.Extract with { Members = [SemanticWorkspace.Property, SemanticWorkspace.Property] }));

        void ThenRefuseAndKeepAuthoredFiles()
        {
            var failure = Assert.IsType<RefactorFailure>(error);
            Assert.Equal("invalid_members", failure.Code);
            Assert.Equal(before, File.ReadAllBytes(workspace.Source));
            Assert.False(File.Exists(workspace.Output));
        }
    }

    /// <summary>Rejects invalid identifiers for the interface name or namespace.</summary>
    [Theory]
    [InlineData("class", "Contracts")]
    [InlineData("ISelected", "bad-name")]
    public void InvalidInterfaceOrNamespaceIdentifierIsRefused(string name, string @namespace)
    {
        using var workspace = new SemanticWorkspace();
        byte[] before = null!;
        Exception? error = null;

        this.Given(GivenAClassAndAnInvalidContractIdentifier, "a class and an invalid contract identifier")
            .When(WhenPlanningTheRequestedChange, "planning the requested change")
            .Then(ThenRefuseAndKeepAuthoredFiles, "refuse and keep authored files unchanged")
            .BDDfy();

        void GivenAClassAndAnInvalidContractIdentifier()
        {
            workspace.Add("A/Service.cs", SemanticWorkspace.Service);
            before = File.ReadAllBytes(workspace.Source);
        }

        async Task WhenPlanningTheRequestedChange() =>
            error = await Record.ExceptionAsync(() => workspace.PlanExtraction(workspace.Extract with { NewName = name, Namespace = @namespace }));

        void ThenRefuseAndKeepAuthoredFiles()
        {
            var failure = Assert.IsType<RefactorFailure>(error);
            Assert.Equal("invalid_name", failure.Code);
            Assert.Equal(before, File.ReadAllBytes(workspace.Source));
            Assert.False(File.Exists(workspace.Output));
        }
    }

    /// <summary>Rejects existing, outside, reserved, or generated interface output paths.</summary>
    [Theory]
    [InlineData("Service.cs")]
    [InlineData("../Outside.cs")]
    [InlineData("CON.cs")]
    [InlineData("COM¹.cs")]
    [InlineData("obj/ISelected.cs")]
    public void InvalidOutputPathIsRefused(string relative) => AssertInvalidOutputPath(relative);

    /// <summary>Rejects a Windows alternate data stream as an interface output.</summary>
    [WindowsFact]
    public void AlternateDataStreamOutputIsRefused() => AssertInvalidOutputPath("payload.cs:stream.cs");

    private void AssertInvalidOutputPath(string relative)
    {
        using var workspace = new SemanticWorkspace();
        string path = null!;
        byte[] before = null!;
        Exception? error = null;

        this.Given(GivenAClassAndAnInvalidOutputPath, "a class and an invalid output path")
            .When(WhenPlanningTheRequestedChange, "planning the requested change")
            .Then(ThenRefuseAndKeepAuthoredFiles, "refuse and keep authored files unchanged")
            .BDDfy();

        void GivenAClassAndAnInvalidOutputPath()
        {
            workspace.Add("A/Service.cs", SemanticWorkspace.Service);
            path = Path.GetFullPath(relative, Path.GetDirectoryName(workspace.Source)!);
            before = File.ReadAllBytes(workspace.Source);
        }

        async Task WhenPlanningTheRequestedChange() =>
            error = await Record.ExceptionAsync(() => workspace.PlanExtraction(workspace.Extract with { OutputFile = path }));

        void ThenRefuseAndKeepAuthoredFiles()
        {
            var failure = Assert.IsType<RefactorFailure>(error);
            Assert.Equal("invalid_output", failure.Code);
            Assert.Equal(before, File.ReadAllBytes(workspace.Source));
            Assert.False(File.Exists(workspace.Output));
            if (relative != "Service.cs") Assert.False(File.Exists(path));
        }
    }

    /// <summary>Rejects selected members whose signatures or accessors are outside the extraction subset.</summary>
    [Theory]
    [InlineData("public static int Get(int x) => x;", SemanticWorkspace.GetInt)]
    [InlineData("public int Get(int x = 1) => x;", SemanticWorkspace.GetInt)]
    [InlineData("[System.Obsolete] public int Get(int x) => x;", SemanticWorkspace.GetInt)]
    [InlineData("public int this[int x] => x;", "P:Demo.Service.Item(System.Int32)")]
    [InlineData("public int Value { get; init; }", "P:Demo.Service.Value")]
    [InlineData("""public string Value { get => ""; [param: System.Diagnostics.CodeAnalysis.AllowNull] set {} }""", "P:Demo.Service.Value")]
    public void UnsupportedMemberShapesAreRefused(string declaration, string member)
    {
        using var workspace = new SemanticWorkspace();
        byte[] before = null!;
        Exception? error = null;

        this.Given(GivenAClassWithAnUnsupportedMemberShape, "a class with an unsupported member shape")
            .When(WhenPlanningTheRequestedChange, "planning the requested change")
            .Then(ThenRefuseAndKeepAuthoredFiles, "refuse and keep authored files unchanged")
            .BDDfy();

        void GivenAClassWithAnUnsupportedMemberShape()
        {
            workspace.Add("A/Service.cs", "namespace Demo; public class Service { " + declaration + " }");
            before = File.ReadAllBytes(workspace.Source);
        }

        async Task WhenPlanningTheRequestedChange() =>
            error = await Record.ExceptionAsync(() => workspace.PlanExtraction(workspace.Extract with { Members = [member] }));

        void ThenRefuseAndKeepAuthoredFiles()
        {
            var failure = Assert.IsType<RefactorFailure>(error);
            Assert.Equal("unsupported_member", failure.Code);
            Assert.Equal(before, File.ReadAllBytes(workspace.Source));
            Assert.False(File.Exists(workspace.Output));
        }
    }

    /// <summary>Rejects extraction that would introduce a duplicate type in the compilation.</summary>
    [Fact]
    public void DuplicateTypeWouldIntroduceCompilationErrors()
    {
        using var workspace = new SemanticWorkspace();
        byte[] before = null!;
        Exception? error = null;

        this.Given(GivenAClassWithTheProposedContractName, "a class with the proposed contract name")
            .When(WhenPlanningTheRequestedChange, "planning the requested change")
            .Then(ThenRefuseAndKeepAuthoredFiles, "refuse and keep authored files unchanged")
            .BDDfy();

        void GivenAClassWithTheProposedContractName()
        {
            workspace.Add("A/Service.cs", SemanticWorkspace.Service);
            before = File.ReadAllBytes(workspace.Source);
        }

        async Task WhenPlanningTheRequestedChange() =>
            error = await Record.ExceptionAsync(() => workspace.PlanExtraction(workspace.Extract with { NewName = "Service", Namespace = "Demo" }));

        void ThenRefuseAndKeepAuthoredFiles()
        {
            var failure = Assert.IsType<RefactorFailure>(error);
            Assert.Equal("new_compilation_errors", failure.Code);
            Assert.Equal(before, File.ReadAllBytes(workspace.Source));
            Assert.False(File.Exists(workspace.Output));
        }
    }

    /// <summary>Rejects extraction if an existing type or namespace reference would bind differently.</summary>
    [Theory]
    [InlineData("ISelected", "namespace Contracts; using External; public class Use { public System.Type Type => typeof(ISelected); }")]
    [InlineData("Token", "using External; public class Use { public System.Type Type => typeof(Contracts.Token); }")]
    public void ExistingTypeAndNamespaceBindingsCannotChange(string name, string consumer)
    {
        using var workspace = new SemanticWorkspace(consumer);
        byte[] before = null!;
        Exception? error = null;

        this.Given(GivenAConsumerOfAnExistingNamespaceOrType, "a consumer of an existing namespace or type")
            .When(WhenPlanningTheRequestedChange, "planning the requested change")
            .Then(ThenRefuseAndKeepAuthoredFiles, "refuse and keep authored files unchanged")
            .BDDfy();

        void GivenAConsumerOfAnExistingNamespaceOrType()
        {
            workspace.Add("A/Service.cs", SemanticWorkspace.Service);
            workspace.Add("A/External.cs", "namespace External { public interface ISelected {} public class Contracts { public class Token {} } }");
            before = File.ReadAllBytes(workspace.Source);
        }

        async Task WhenPlanningTheRequestedChange() =>
            error = await Record.ExceptionAsync(() => workspace.PlanExtraction(workspace.Extract with { NewName = name }));

        void ThenRefuseAndKeepAuthoredFiles()
        {
            var failure = Assert.IsType<RefactorFailure>(error);
            Assert.Equal("name_collision", failure.Code);
            Assert.Equal(before, File.ReadAllBytes(workspace.Source));
            Assert.False(File.Exists(workspace.Output));
            Assert.Equal(consumer, File.ReadAllText(workspace.ConsumerPath));
        }
    }

    /// <summary>Preserves the primary constructor and method body while adding the interface.</summary>
    [Fact]
    public void PrimaryConstructorAndMethodBodyArePreserved()
    {
        const string source = "namespace Demo; public class Service(int n) { public int Get(int value) => n + value; }";
        using var workspace = new SemanticWorkspace();
        Plan plan = null!;
        string runningTheConsumerAgainstThePlannedEditsResult = null!;

        this.Given(GivenAClassWithAPrimaryConstructor, "a class with a primary constructor")
            .When(WhenPlanningExtraction, "planning extraction")
            .Then(ThenPreserveTheConstructorAndMethodBody, "preserve the constructor and method body")
            .When(WhenRunningTheConsumerAgainstThePlannedEdits, "running the consumer against the planned edits")
            .Then(ThenPreserveRuntimeBehaviorAndAuthoredFiles, "preserve runtime behavior and authored files")
            .BDDfy();

        void GivenAClassWithAPrimaryConstructor() => workspace.Add("A/Service.cs", source);

        async Task WhenPlanningExtraction()
        {
            plan = await workspace.PlanExtraction(workspace.Extract with { Members = [SemanticWorkspace.GetInt] });
        }

        void ThenPreserveTheConstructorAndMethodBody() => Assert.Equal("namespace Demo; public class Service(int n) : global::Contracts.ISelected { public int Get(int value) => n + value; }",
            SemanticWorkspace.After(plan, workspace.Source));

        async Task WhenRunningTheConsumerAgainstThePlannedEdits() => runningTheConsumerAgainstThePlannedEditsResult = await workspace.RunConsumer(plan, """
            public static class Probe
            {
                public static string Run()
                {
                    Contracts.ISelected service = new Demo.Service(3);
                    return service.Get(4).ToString(System.Globalization.CultureInfo.InvariantCulture);
                }
            }
            """);

        void ThenPreserveRuntimeBehaviorAndAuthoredFiles()
        {
            Assert.Equal("7", runningTheConsumerAgainstThePlannedEditsResult);
            Assert.Equal(source, File.ReadAllText(workspace.Source));
            Assert.False(File.Exists(workspace.Output));
        }
    }
}
