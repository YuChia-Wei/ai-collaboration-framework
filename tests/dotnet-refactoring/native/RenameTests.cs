using System.Text;

namespace RefactorTool.Tests;

public sealed class RenameTests
{
    [Fact]
    public async Task OverloadGroupRequiresOptInAndUpdatesNameof()
    {
        using var workspace = new SemanticWorkspace(GroupConsumer);
        workspace.Add("A/Service.cs", SemanticWorkspace.Service);
        await Refused(workspace, workspace.Rename, "ambiguous_nameof");
        var plan = await workspace.PlanRename(workspace.Rename with { RenameOverloads = true });
        Assert.Contains("int Fetch(string value)", SemanticWorkspace.After(plan, workspace.Source));
        Assert.Contains("nameof(Service.Fetch)", SemanticWorkspace.After(plan, workspace.ConsumerPath));
    }

    [Theory]
    [InlineData("M:Demo.IService.Get(System.Int32)")]
    [InlineData("M:Demo.Derived.Get(System.Int32)")]
    public async Task OptInDoesNotPullInOverloadsFromRelatedTypes(string symbol)
    {
        using var workspace = new SemanticWorkspace(GroupConsumer);
        workspace.Add("A/Service.cs", SemanticWorkspace.Service);
        var failure = await Refused(workspace, workspace.Rename with { Symbol = symbol, RenameOverloads = true }, "ambiguous_nameof");
        Assert.Contains("outside the selected rename scope", failure.Message);
        Assert.DoesNotContain("review renameOverloads=true", failure.Message);
    }

    [Theory]
    [InlineData("T:Demo.Service", "RenamedService", "new RenamedService()", "class RenamedService : IService")]
    [InlineData("T:Demo.IService", "IRenamedService", "IRenamedService service", "class Service : IRenamedService")]
    public async Task TypeRenameUpdatesDeclarationAndConsumer(string symbol, string name, string consumer, string declaration)
    {
        using var workspace = new SemanticWorkspace(SemanticWorkspace.Consumer);
        workspace.Add("A/Service.cs", SemanticWorkspace.Service);
        var plan = await workspace.PlanRename(workspace.Rename with { Symbol = symbol, NewName = name });
        Assert.Contains(consumer, SemanticWorkspace.After(plan, workspace.ConsumerPath));
        Assert.Contains(declaration, SemanticWorkspace.After(plan, workspace.Source));
    }

    [Theory]
    [InlineData("P:Demo.Service.Property", "Value", "int Value { get; set; }")]
    [InlineData("F:Demo.Service.Field", "Data", "return local + Data;")]
    public async Task RenamesSelectedPropertyOrField(string symbol, string name, string expected)
    {
        using var workspace = new SemanticWorkspace();
        workspace.Add("A/Service.cs", SemanticWorkspace.Service);
        var plan = await workspace.PlanRename(workspace.Rename with { Symbol = symbol, NewName = name });
        Assert.Contains(expected, SemanticWorkspace.After(plan, workspace.Source));
    }

    [Theory]
    [InlineData("value", "argument", "int Get(int argument) { int local = argument; return local + Field; }")]
    [InlineData("local", "answer", "int local = value; return local + Field;", "int answer = value; return answer \\+ Field;")]
    [InlineData("local", "record", "int local = value; return local + Field;", "int @?record = value; return @?record \\+ Field;")]
    public async Task PositionRenamesParameterOrLocal(string token, string name, string expected, string? replacement = null)
    {
        using var workspace = new SemanticWorkspace();
        workspace.Add("A/Service.cs", SemanticWorkspace.Service);
        var request = At(workspace.Rename, workspace.Source, SemanticWorkspace.Service, 6, token, name);
        var plan = await workspace.PlanRename(request);
        var after = SemanticWorkspace.After(plan, workspace.Source);
        if (replacement is null) Assert.Contains(expected, after);
        else
        {
            Assert.DoesNotContain(expected, after);
            Assert.Matches(replacement, after);
        }
        Assert.Empty(plan.NewErrors);
    }

    [Theory]
    [InlineData("M:Demo.Service.Get", "Fetch", "ambiguous_symbol")]
    [InlineData(SemanticWorkspace.GetInt, "class", "invalid_name")]
    [InlineData(SemanticWorkspace.GetInt, "bad-name", "invalid_name")]
    [InlineData(SemanticWorkspace.GetInt, "Property", "name_collision")]
    [InlineData(SemanticWorkspace.GetInt, "ToString", "name_collision")]
    public async Task InvalidNamesSelectionsAndCollisionsProduceNoEdits(string symbol, string name, string code)
    {
        using var workspace = new SemanticWorkspace();
        workspace.Add("A/Service.cs", SemanticWorkspace.Service);
        await Refused(workspace, workspace.Rename with { Symbol = symbol, NewName = name }, code);
    }

    [Fact]
    public async Task PositionOutsideIdentifierAndOverloadGroupAreRefused()
    {
        using var workspace = new SemanticWorkspace(GroupConsumer);
        workspace.Add("A/Service.cs", SemanticWorkspace.Service);
        var blank = workspace.Rename with { Project = null, Symbol = null, File = workspace.Source, Line = 6, Column = 1 };
        Assert.Contains((await Refused(workspace, blank)).Code, new[] { "invalid_position", "ambiguous_symbol" });
        var overload = At(workspace.Rename, workspace.ConsumerPath, GroupConsumer, 3, "Service.Get)", "Fetch");
        await Refused(workspace, overload with { Column = overload.Column + "Service.".Length, RenameOverloads = true }, "ambiguous_symbol");
    }

    [Fact]
    public async Task RefusesOverrideOfFrameworkMember()
    {
        using var workspace = new SemanticWorkspace();
        workspace.Add("A/Service.cs", """namespace Demo; public class Service { public override string ToString() => "Service"; }""");
        await Refused(workspace, workspace.Rename with { Symbol = "M:Demo.Service.ToString", NewName = "Describe" }, "uneditable_symbol");
    }

    [Fact]
    public async Task BaselineDiagnosticsRemainVisibleIncludingMappedOffsets()
    {
        using var workspace = new SemanticWorkspace("class Broken { MissingType field; }");
        workspace.Add("A/Service.cs", SemanticWorkspace.Service.Replace("Field = 1;", "Field = 1; MissingType broken;"));
        var plan = await workspace.PlanRename(workspace.Rename with { Symbol = "F:Demo.Service.Field", NewName = "LongerFieldName" });
        Assert.Equal(2, plan.BaselineErrors.Length);
        Assert.All(plan.BaselineErrors, error => Assert.Equal("CS0246", error.Id));
        Assert.Empty(plan.NewErrors);
    }

    [Fact]
    public async Task BaselineErrorDoesNotHideNewLocalCollision()
    {
        using var workspace = new SemanticWorkspace("class Broken { MissingType field; }");
        workspace.Add("A/Service.cs", SemanticWorkspace.Service);
        var failure = await Refused(workspace, At(workspace.Rename, workspace.Source, SemanticWorkspace.Service, 6, "local", "value"));
        Assert.Contains(failure.Code, new[] { "rename_conflict", "new_compilation_errors" });
    }

    [Theory]
    [InlineData("T:Demo.Plain", "Renamed", "nameof(global::Demo.Renamed)", null)]
    [InlineData("T:Demo.Generic`1", "RenamedGeneric", "nameof(RenamedGeneric<T>)", "nameof(RenamedGeneric<>)")]
    public async Task AliasAndGenericNameofPreserveSyntax(string symbol, string name, string expected, string? second)
    {
        using var workspace = new SemanticWorkspace();
        workspace.Add("A/Service.cs", """
            namespace Demo;
            public class Plain { public string Name => nameof(global::Demo.Plain); }
            public class Generic<T> { public string Name => nameof(Generic<T>); public string Open => nameof(Generic<>); }
            """);
        var plan = await workspace.PlanRename(workspace.Rename with { Symbol = symbol, NewName = name });
        var after = SemanticWorkspace.After(plan, workspace.Source);
        Assert.Contains(expected, after);
        if (second is not null) Assert.Contains(second, after);
        Assert.Empty(plan.NewErrors);
    }

    [Fact]
    public async Task PreservesBomAndNoFinalNewline()
    {
        using var workspace = new SemanticWorkspace();
        workspace.Add("A/Service.cs", SemanticWorkspace.Service, bom: true);
        var plan = await workspace.PlanRename(workspace.Rename);
        var after = Convert.FromBase64String(Assert.Single(plan.Edits).After);
        Assert.True(after.AsSpan().StartsWith(new byte[] { 0xef, 0xbb, 0xbf }));
        Assert.NotEqual((byte)'\n', after[^1]);
        Assert.Contains("\\ No newline at end of file", plan.Patch);
    }

    [Fact]
    public async Task CompactPatchOmitsDistantUnchangedContext()
    {
        using var workspace = new SemanticWorkspace();
        var padding = string.Concat(Enumerable.Range(0, 100).Select(i => $"// unchanged {i}\n"));
        var source = $"namespace Demo;\nclass Service {{ int field;\n{padding}int Use() => field;\n}}\n";
        workspace.Add("A/Service.cs", source);
        var plan = await workspace.PlanRename(workspace.Rename with { Symbol = "F:Demo.Service.field", NewName = "data" });
        Assert.Equal(2, plan.Patch.Split("\n@@ -").Length - 1);
        Assert.Contains("-class Service { int field;\n+class Service { int data;\n", plan.Patch);
        Assert.Contains("-int Use() => field;\n+int Use() => data;\n", plan.Patch);
        Assert.DoesNotContain("// unchanged 50", plan.Patch);
        Assert.Equal(Encoding.UTF8.GetBytes(source), Convert.FromBase64String(Assert.Single(plan.Edits).Before));
    }

    [Fact]
    public async Task CrOnlySourceAndPatchAreByteExact()
    {
        using var workspace = new SemanticWorkspace();
        const string before = "namespace Demo;\rclass Service {\r int value;\r int Use() => value;\r}\r";
        const string after = "namespace Demo;\rclass Service {\r int data;\r int Use() => data;\r}\r";
        const string marker = "\n\\ No newline at end of file\n";
        workspace.Add("A/Service.cs", before);
        var plan = await workspace.PlanRename(workspace.Rename with { Symbol = "F:Demo.Service.value", NewName = "data" });
        var edit = Assert.Single(plan.Edits);
        Assert.Equal(before, File.ReadAllText(workspace.Source));
        Assert.Equal(Encoding.UTF8.GetBytes(before), Convert.FromBase64String(edit.Before));
        Assert.Equal(Encoding.UTF8.GetBytes(after), Convert.FromBase64String(edit.After));
        Assert.Equal($"--- a/A/Service.cs\n+++ b/A/Service.cs\n@@ -1,1 +1,1 @@\n-{before}{marker}+{after}{marker}", plan.Patch);
    }

    [Fact]
    public async Task MalformedSourceEncodingIsRefusedWithoutWrites()
    {
        using var workspace = new SemanticWorkspace();
        byte[] bytes = [0xef, 0xbb, 0xbf, .. Encoding.UTF8.GetBytes(SemanticWorkspace.Service + "\n// malformed "), 0xff, 0x0a];
        workspace.Add("A/Service.cs", bytes);
        await Refused(workspace, workspace.Rename, "lossy_encoding");
        Assert.Equal(bytes, File.ReadAllBytes(workspace.Source));
    }

    private static string GroupConsumer => SemanticWorkspace.Consumer.Replace("nameof(IService.Get)", "nameof(Service.Get)");

    private static Request At(Request request, string path, string source, int line, string token, string name) => request with
    {
        Symbol = null, Project = null, File = path, Line = line, NewName = name,
        Column = source.Split('\n')[line - 1].IndexOf(token, StringComparison.Ordinal) + 1
    };

    private static async Task<RefactorFailure> Refused(SemanticWorkspace workspace, Request request, string? code = null)
    {
        var before = File.ReadAllBytes(workspace.Source);
        var consumer = File.Exists(workspace.ConsumerPath) ? File.ReadAllBytes(workspace.ConsumerPath) : null;
        var failure = await Assert.ThrowsAsync<RefactorFailure>(() => workspace.PlanRename(request));
        if (code is not null) Assert.Equal(code, failure.Code);
        Assert.Equal(before, File.ReadAllBytes(workspace.Source));
        if (consumer is not null) Assert.Equal(consumer, File.ReadAllBytes(workspace.ConsumerPath));
        return failure;
    }
}
