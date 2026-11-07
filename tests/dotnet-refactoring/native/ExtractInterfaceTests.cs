using Microsoft.CodeAnalysis.CSharp;
using Microsoft.CodeAnalysis.CSharp.Syntax;

namespace RefactorTool.Tests;

public sealed class ExtractInterfaceTests
{
    [Fact]
    public async Task NullableGenericContractPreservesRefOutAndPrivateSetterBehavior()
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
        workspace.Add("A/Service.cs", source);
        var plan = await workspace.PlanExtraction(workspace.Extract with
        {
            Symbol = "T:Demo.Service`1", Members = ["P:Demo.Service`1.Value", "M:Demo.Service`1.Read``1(`0@,System.Int32@)"]
        });
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
        Assert.Equal("True|0|abc|3|abc", await workspace.RunConsumer(plan, """
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
            """));
        Assert.Equal(source, File.ReadAllText(workspace.Source));
        Assert.False(File.Exists(workspace.Output));
    }

    [Theory]
    [InlineData("F:Demo.Service.Field", "unsupported_member")]
    [InlineData("M:Demo.Other.Get(System.Int32)", "invalid_members")]
    [InlineData("M:Demo.Service.Get", "invalid_members")]
    public async Task ExactDeclaredMethodOrPropertyIsRequired(string member, string code)
    {
        using var workspace = new SemanticWorkspace();
        workspace.Add("A/Service.cs", SemanticWorkspace.Service);
        await Refused(workspace, workspace.Extract with { Members = [member] }, code);
    }

    [Fact]
    public async Task DuplicateMemberIdsAreRefused()
    {
        using var workspace = new SemanticWorkspace();
        workspace.Add("A/Service.cs", SemanticWorkspace.Service);
        await Refused(workspace, workspace.Extract with { Members = [SemanticWorkspace.Property, SemanticWorkspace.Property] }, "invalid_members");
    }

    [Theory]
    [InlineData("class", "Contracts")]
    [InlineData("ISelected", "bad-name")]
    public async Task InvalidInterfaceOrNamespaceIdentifierIsRefused(string name, string @namespace)
    {
        using var workspace = new SemanticWorkspace();
        workspace.Add("A/Service.cs", SemanticWorkspace.Service);
        await Refused(workspace, workspace.Extract with { NewName = name, Namespace = @namespace }, "invalid_name");
    }

    [Theory]
    [InlineData("Service.cs")]
    [InlineData("../Outside.cs")]
    [InlineData("payload.cs:stream.cs")]
    [InlineData("CON.cs")]
    [InlineData("COM¹.cs")]
    [InlineData("obj/ISelected.cs")]
    public async Task InvalidOutputPathIsRefused(string relative)
    {
        using var workspace = new SemanticWorkspace();
        workspace.Add("A/Service.cs", SemanticWorkspace.Service);
        var path = Path.GetFullPath(relative, Path.GetDirectoryName(workspace.Source)!);
        await Refused(workspace, workspace.Extract with { OutputFile = path }, "invalid_output");
        if (relative != "Service.cs") Assert.False(File.Exists(path));
    }

    [Theory]
    [InlineData("public static int Get(int x) => x;", SemanticWorkspace.GetInt)]
    [InlineData("public int Get(int x = 1) => x;", SemanticWorkspace.GetInt)]
    [InlineData("[System.Obsolete] public int Get(int x) => x;", SemanticWorkspace.GetInt)]
    [InlineData("public int this[int x] => x;", "P:Demo.Service.Item(System.Int32)")]
    [InlineData("public int Value { get; init; }", "P:Demo.Service.Value")]
    [InlineData("""public string Value { get => ""; [param: System.Diagnostics.CodeAnalysis.AllowNull] set {} }""", "P:Demo.Service.Value")]
    public async Task UnsupportedMemberShapesAreRefused(string declaration, string member)
    {
        using var workspace = new SemanticWorkspace();
        workspace.Add("A/Service.cs", "namespace Demo; public class Service { " + declaration + " }");
        await Refused(workspace, workspace.Extract with { Members = [member] }, "unsupported_member");
    }

    [Fact]
    public async Task DuplicateTypeWouldIntroduceCompilationErrors()
    {
        using var workspace = new SemanticWorkspace();
        workspace.Add("A/Service.cs", SemanticWorkspace.Service);
        await Refused(workspace, workspace.Extract with { NewName = "Service", Namespace = "Demo" }, "new_compilation_errors");
    }

    [Theory]
    [InlineData("ISelected", "namespace Contracts; using External; public class Use { public System.Type Type => typeof(ISelected); }")]
    [InlineData("Token", "using External; public class Use { public System.Type Type => typeof(Contracts.Token); }")]
    public async Task ExistingTypeAndNamespaceBindingsCannotChange(string name, string consumer)
    {
        using var workspace = new SemanticWorkspace(consumer);
        workspace.Add("A/Service.cs", SemanticWorkspace.Service);
        workspace.Add("A/External.cs", "namespace External { public interface ISelected {} public class Contracts { public class Token {} } }");
        await Refused(workspace, workspace.Extract with { NewName = name }, "name_collision");
        Assert.Equal(consumer, File.ReadAllText(workspace.ConsumerPath));
    }

    [Fact]
    public async Task PrimaryConstructorAndMethodBodyArePreserved()
    {
        const string source = "namespace Demo; public class Service(int n) { public int Get(int value) => n + value; }";
        using var workspace = new SemanticWorkspace();
        workspace.Add("A/Service.cs", source);
        var plan = await workspace.PlanExtraction(workspace.Extract with { Members = [SemanticWorkspace.GetInt] });
        Assert.Equal("namespace Demo; public class Service(int n) : global::Contracts.ISelected { public int Get(int value) => n + value; }",
            SemanticWorkspace.After(plan, workspace.Source));
        Assert.Equal("7", await workspace.RunConsumer(plan, """
            public static class Probe
            {
                public static string Run()
                {
                    Contracts.ISelected service = new Demo.Service(3);
                    return service.Get(4).ToString(System.Globalization.CultureInfo.InvariantCulture);
                }
            }
            """));
        Assert.Equal(source, File.ReadAllText(workspace.Source));
        Assert.False(File.Exists(workspace.Output));
    }

    private static async Task Refused(SemanticWorkspace workspace, Request request, string code)
    {
        var before = File.ReadAllBytes(workspace.Source);
        var failure = await Assert.ThrowsAsync<RefactorFailure>(() => workspace.PlanExtraction(request));
        Assert.Equal(code, failure.Code);
        Assert.Equal(before, File.ReadAllBytes(workspace.Source));
        Assert.False(File.Exists(workspace.Output));
    }
}
