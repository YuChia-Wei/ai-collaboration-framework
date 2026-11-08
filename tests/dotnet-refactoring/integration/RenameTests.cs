using Microsoft.CodeAnalysis.CSharp;
using System.Text;

namespace RefactorTool.IntegrationTests;

public sealed class RenameTests
{
    [Fact]
    public void OverloadGroupRequiresOptInAndUpdatesNameof()
    {
        using var workspace = new SemanticWorkspace(GroupConsumer);
        Plan plan = null!;
        byte[] before = null!, consumerBefore = null!;
        Exception? error = null;

        this.Given(GivenAnOverloadGroupReferencedByNameof, "an overload group referenced by nameof")
            .When(WhenPreviewingWithoutOptIn, "previewing without opt-in")
            .Then(ThenRequireOptInWithoutChangingSource, "require opt-in without changing source")
            .When(WhenPreviewingWithOptIn, "previewing with opt in")
            .Then(ThenUpdateBothOverloadsAndTheNameofExpression, "update both overloads and the nameof expression")
            .BDDfy();

        void GivenAnOverloadGroupReferencedByNameof()
        {
            workspace.Add("A/Service.cs", SemanticWorkspace.Service);
            before = File.ReadAllBytes(workspace.Source);
            consumerBefore = File.ReadAllBytes(workspace.ConsumerPath);
        }

        async Task WhenPreviewingWithoutOptIn() =>
            error = await Record.ExceptionAsync(() => workspace.PlanRename(workspace.Rename));

        void ThenRequireOptInWithoutChangingSource()
        {
            Assert.Equal("ambiguous_nameof", Assert.IsType<RefactorFailure>(error).Code);
            Assert.Equal(before, File.ReadAllBytes(workspace.Source));
            Assert.Equal(consumerBefore, File.ReadAllBytes(workspace.ConsumerPath));
        }

        async Task WhenPreviewingWithOptIn()
        {
            plan = await workspace.PlanRename(workspace.Rename with { RenameOverloads = true });
        }

        void ThenUpdateBothOverloadsAndTheNameofExpression()
        {
            Assert.Contains("int Fetch(string value)", SemanticWorkspace.After(plan, workspace.Source));
            Assert.Contains("nameof(Service.Fetch)", SemanticWorkspace.After(plan, workspace.ConsumerPath));
        }
    }

    [Theory]
    [InlineData("M:Demo.IService.Get(System.Int32)")]
    [InlineData("M:Demo.Derived.Get(System.Int32)")]
    public void OptInDoesNotPullInOverloadsFromRelatedTypes(string symbol)
    {
        using var workspace = new SemanticWorkspace(GroupConsumer);
        byte[] before = null!;
        byte[] consumerBefore = null!;
        Exception? error = null;

        this.Given(GivenAnOverloadGroupOutsideTheSelectedType, "an overload group outside the selected type")
            .When(WhenPlanningTheRequestedChange, "planning the requested change")
            .Then(ThenRefuseAndKeepAuthoredFiles, "refuse and keep authored files unchanged")
            .BDDfy();

        void GivenAnOverloadGroupOutsideTheSelectedType()
        {
            workspace.Add("A/Service.cs", SemanticWorkspace.Service);
            before = File.ReadAllBytes(workspace.Source);
            consumerBefore = File.ReadAllBytes(workspace.ConsumerPath);
        }

        async Task WhenPlanningTheRequestedChange() =>
            error = await Record.ExceptionAsync(() => workspace.PlanRename(workspace.Rename with { Symbol = symbol, RenameOverloads = true }));

        void ThenRefuseAndKeepAuthoredFiles()
        {
            var failure = Assert.IsType<RefactorFailure>(error);
            Assert.Equal("ambiguous_nameof", failure.Code);
            Assert.Equal(before, File.ReadAllBytes(workspace.Source));
            Assert.Equal(consumerBefore, File.ReadAllBytes(workspace.ConsumerPath));
            Assert.Contains(workspace.ConsumerPath, failure.Message);
            Assert.DoesNotContain("renameOverloads=true", failure.Message);
        }
    }

    [Theory]
    [InlineData("T:Demo.Service", "RenamedService", "new RenamedService()", "class RenamedService : IService")]
    [InlineData("T:Demo.IService", "IRenamedService", "IRenamedService service", "class Service : IRenamedService")]
    public void TypeRenameUpdatesDeclarationAndConsumer(string symbol, string name, string consumer, string declaration)
    {
        using var workspace = new SemanticWorkspace(SemanticWorkspace.Consumer);
        Plan plan = null!;

        this.Given(GivenATypeUsedAcrossProjects, "a type used across projects")
            .When(WhenPlanningTheTypeRename, "planning the type rename")
            .Then(ThenUpdateDeclarationAndConsumer, "update declaration and consumer")
            .BDDfy();

        void GivenATypeUsedAcrossProjects() => workspace.Add("A/Service.cs", SemanticWorkspace.Service);

        async Task WhenPlanningTheTypeRename()
        {
            plan = await workspace.PlanRename(workspace.Rename with { Symbol = symbol, NewName = name });
        }

        void ThenUpdateDeclarationAndConsumer()
        {
            AssertSourceTokens(consumer, SemanticWorkspace.After(plan, workspace.ConsumerPath));
            AssertSourceTokens(declaration, SemanticWorkspace.After(plan, workspace.Source));
        }
    }

    [Theory]
    [InlineData("P:Demo.Service.Property", "Value", "int Value { get; set; }")]
    [InlineData("F:Demo.Service.Field", "Data", "return local + Data;")]
    public void RenamesSelectedPropertyOrField(string symbol, string name, string expected)
    {
        using var workspace = new SemanticWorkspace();
        Plan plan = null!;

        this.Given(GivenAClassWithAFieldAndProperty, "a class with a field and property")
            .When(WhenRenamingTheSelectedMember, "renaming the selected member")
            .Then(ThenUpdateItsDeclaration, "update its declaration")
            .BDDfy();

        void GivenAClassWithAFieldAndProperty() => workspace.Add("A/Service.cs", SemanticWorkspace.Service);

        async Task WhenRenamingTheSelectedMember()
        {
            plan = await workspace.PlanRename(workspace.Rename with { Symbol = symbol, NewName = name });
        }

        void ThenUpdateItsDeclaration() => AssertSourceTokens(expected, SemanticWorkspace.After(plan, workspace.Source));
    }

    [Theory]
    [InlineData("value", "argument", "int Get(int argument) { int local = argument; return local + Field; }")]
    [InlineData("local", "answer", "int local = value; return local + Field;", "int answer = value; return answer \\+ Field;")]
    [InlineData("local", "record", "int local = value; return local + Field;", "int @?record = value; return @?record \\+ Field;")]
    public void PositionRenamesParameterOrLocal(string token, string name, string expected, string? replacement = null)
    {
        using var workspace = new SemanticWorkspace();
        Request request = null!;
        Plan plan = null!;

        this.Given(GivenThePositionOfALocalOrParameter, "the position of a local or parameter")
            .When(WhenPlanningRenameAtThePosition, "planning rename at the position")
            .Then(ThenPreserveTheExpectedSyntaxWithoutNewErrors, "preserve the expected syntax without new errors")
            .BDDfy();

        void GivenThePositionOfALocalOrParameter()
        {
            workspace.Add("A/Service.cs", SemanticWorkspace.Service);
            request = At(workspace.Rename, workspace.Source, SemanticWorkspace.Service, 6, token, name);
        }

        async Task WhenPlanningRenameAtThePosition()
        {
            plan = await workspace.PlanRename(request);
        }

        void ThenPreserveTheExpectedSyntaxWithoutNewErrors()
        {
            var after = SemanticWorkspace.After(plan, workspace.Source);
            if (replacement is null) Assert.Contains(expected, after);
            else
            {
                Assert.DoesNotContain(expected, after);
                Assert.Matches(replacement, after);
            }
            Assert.Empty(plan.NewErrors);
        }
    }

    [Theory]
    [InlineData("M:Demo.Service.Get", "Fetch", "ambiguous_symbol")]
    [InlineData(SemanticWorkspace.GetInt, "class", "invalid_name")]
    [InlineData(SemanticWorkspace.GetInt, "bad-name", "invalid_name")]
    [InlineData(SemanticWorkspace.GetInt, "Property", "name_collision")]
    [InlineData(SemanticWorkspace.GetInt, "ToString", "name_collision")]
    public void InvalidNamesSelectionsAndCollisionsProduceNoEdits(string symbol, string name, string code)
    {
        using var workspace = new SemanticWorkspace();
        byte[] before = null!;
        Exception? error = null;

        this.Given(GivenASymbolSelectionWithANameOrCollisionProblem, "a symbol selection with a name or collision problem")
            .When(WhenPlanningTheRequestedChange, "planning the requested change")
            .Then(ThenRefuseAndKeepAuthoredFiles, "refuse and keep authored files unchanged")
            .BDDfy();

        void GivenASymbolSelectionWithANameOrCollisionProblem()
        {
            workspace.Add("A/Service.cs", SemanticWorkspace.Service);
            before = File.ReadAllBytes(workspace.Source);
        }

        async Task WhenPlanningTheRequestedChange() =>
            error = await Record.ExceptionAsync(() => workspace.PlanRename(workspace.Rename with { Symbol = symbol, NewName = name }));

        void ThenRefuseAndKeepAuthoredFiles()
        {
            var failure = Assert.IsType<RefactorFailure>(error);
            Assert.Equal(code, failure.Code);
            Assert.Equal(before, File.ReadAllBytes(workspace.Source));
        }
    }

    [Fact]
    public void PositionOutsideIdentifierAndOverloadGroupAreRefused()
    {
        using var workspace = new SemanticWorkspace(GroupConsumer);
        Request blank = null!;
        Exception? blankFailure = null, overloadFailure = null;
        byte[] before = null!, consumerBefore = null!;
        Request overload = null!;

        this.Given(GivenAnAuthoredWorkspaceAndAPositionOutsideAnIdentifier, "an authored workspace and a position outside an identifier")
            .When(WhenPlanningRenameOutsideAnIdentifier, "planning rename outside an identifier")
            .Then(ThenRefuseTheAmbiguousOrInvalidPosition, "refuse the ambiguous or invalid position")
            .Given(GivenAPositionOnTheOverloadGroup, "a position on the overload group")
            .When(WhenPlanningAnOverloadGroupRenameFromPosition, "planning an overload group rename from position")
            .Then(ThenRefuseTheAmbiguousSymbol, "refuse the ambiguous symbol")
            .BDDfy();

        void GivenAnAuthoredWorkspaceAndAPositionOutsideAnIdentifier()
        {
            workspace.Add("A/Service.cs", SemanticWorkspace.Service);
            before = File.ReadAllBytes(workspace.Source);
            consumerBefore = File.ReadAllBytes(workspace.ConsumerPath);
            blank = workspace.Rename with { Project = null, Symbol = null, File = workspace.Source, Line = 6, Column = 1 };
        }

        async Task WhenPlanningRenameOutsideAnIdentifier()
        {
            blankFailure = await Record.ExceptionAsync(() => workspace.PlanRename(blank));
        }

        void ThenRefuseTheAmbiguousOrInvalidPosition()
        {
            Assert.Contains(Assert.IsType<RefactorFailure>(blankFailure).Code, new[] { "invalid_position", "ambiguous_symbol" });
            Assert.Equal(before, File.ReadAllBytes(workspace.Source));
            Assert.Equal(consumerBefore, File.ReadAllBytes(workspace.ConsumerPath));
        }

        void GivenAPositionOnTheOverloadGroup()
        {
            overload = At(workspace.Rename, workspace.ConsumerPath, GroupConsumer, 3, "Service.Get)", "Fetch");
        }

        async Task WhenPlanningAnOverloadGroupRenameFromPosition() =>
            overloadFailure = await Record.ExceptionAsync(() =>
                workspace.PlanRename(overload with { Column = overload.Column + "Service.".Length, RenameOverloads = true }));

        void ThenRefuseTheAmbiguousSymbol()
        {
            Assert.Equal("ambiguous_symbol", Assert.IsType<RefactorFailure>(overloadFailure).Code);
            Assert.Equal(before, File.ReadAllBytes(workspace.Source));
            Assert.Equal(consumerBefore, File.ReadAllBytes(workspace.ConsumerPath));
        }
    }

    [Fact]
    public void RefusesOverrideOfFrameworkMember()
    {
        using var workspace = new SemanticWorkspace();
        byte[] before = null!;
        Exception? error = null;

        this.Given(GivenAnOverrideOfAFrameworkMember, "an override of a framework member")
            .When(WhenPlanningTheRequestedChange, "planning the requested change")
            .Then(ThenRefuseAndKeepAuthoredFiles, "refuse and keep authored files unchanged")
            .BDDfy();

        void GivenAnOverrideOfAFrameworkMember()
        {
            workspace.Add("A/Service.cs", """namespace Demo; public class Service { public override string ToString() => "Service"; }""");
            before = File.ReadAllBytes(workspace.Source);
        }

        async Task WhenPlanningTheRequestedChange() =>
            error = await Record.ExceptionAsync(() => workspace.PlanRename(workspace.Rename with { Symbol = "M:Demo.Service.ToString", NewName = "Describe" }));

        void ThenRefuseAndKeepAuthoredFiles()
        {
            var failure = Assert.IsType<RefactorFailure>(error);
            Assert.Equal("uneditable_symbol", failure.Code);
            Assert.Equal(before, File.ReadAllBytes(workspace.Source));
        }
    }

    [Fact]
    public void BaselineDiagnosticsRemainVisibleIncludingMappedOffsets()
    {
        using var workspace = new SemanticWorkspace("class Broken { MissingType field; }");
        Plan plan = null!;

        this.Given(GivenExistingErrorsInBothProjects, "existing errors in both projects")
            .When(WhenPlanningAFieldRename, "planning a field rename")
            .Then(ThenReportTheBaselineErrorsSeparately, "report the baseline errors separately")
            .BDDfy();

        void GivenExistingErrorsInBothProjects() => workspace.Add("A/Service.cs", SemanticWorkspace.Service.Replace("Field = 1;", "Field = 1; MissingType broken;"));

        async Task WhenPlanningAFieldRename()
        {
            plan = await workspace.PlanRename(workspace.Rename with { Symbol = "F:Demo.Service.Field", NewName = "LongerFieldName" });
        }

        void ThenReportTheBaselineErrorsSeparately()
        {
            Assert.Equal(2, plan.BaselineErrors.Length);
            Assert.All(plan.BaselineErrors, error => Assert.Equal("CS0246", error.Id));
            Assert.Empty(plan.NewErrors);
        }
    }

    [Fact]
    public void BaselineErrorDoesNotHideNewLocalCollision()
    {
        using var workspace = new SemanticWorkspace("class Broken { MissingType field; }");
        RefactorFailure failure = null!;

        this.Given(GivenAnExistingErrorAndALocalNameCollision, "an existing error and a local name collision")
            .When(WhenPlanningTheConflictingRename, "planning the conflicting rename")
            .Then(ThenReportTheNewCollision, "report the new collision")
            .BDDfy();

        void GivenAnExistingErrorAndALocalNameCollision() => workspace.Add("A/Service.cs", SemanticWorkspace.Service);

        async Task WhenPlanningTheConflictingRename()
        {
            failure = await Refused(workspace, At(workspace.Rename, workspace.Source, SemanticWorkspace.Service, 6, "local", "value"));
        }

        void ThenReportTheNewCollision() => Assert.Contains(failure.Code, new[] { "rename_conflict", "new_compilation_errors" });
    }

    [Theory]
    [InlineData("T:Demo.Plain", "Renamed", "nameof(global::Demo.Renamed)", null)]
    [InlineData("T:Demo.Generic`1", "RenamedGeneric", "nameof(RenamedGeneric<T>)", "nameof(RenamedGeneric<>)")]
    public void AliasAndGenericNameofPreserveSyntax(string symbol, string name, string expected, string? second)
    {
        using var workspace = new SemanticWorkspace();
        Plan plan = null!;

        this.Given(GivenAliasAndGenericNameofReferences, "alias and generic nameof references")
            .When(WhenPlanningTheSymbolRename, "planning the symbol rename")
            .Then(ThenUpdateTheReferencesWithoutNewErrors, "update the references without new errors")
            .BDDfy();

        void GivenAliasAndGenericNameofReferences() => workspace.Add("A/Service.cs", """
            namespace Demo;
            public class Plain { public string Name => nameof(global::Demo.Plain); }
            public class Generic<T> { public string Name => nameof(Generic<T>); public string Open => nameof(Generic<>); }
            """);

        async Task WhenPlanningTheSymbolRename()
        {
            plan = await workspace.PlanRename(workspace.Rename with { Symbol = symbol, NewName = name });
        }

        void ThenUpdateTheReferencesWithoutNewErrors()
        {
            var after = SemanticWorkspace.After(plan, workspace.Source);
            Assert.Contains(expected, after);
            if (second is not null) Assert.Contains(second, after);
            Assert.Empty(plan.NewErrors);
        }
    }

    [Fact]
    public void PreservesBomAndNoFinalNewline()
    {
        using var workspace = new SemanticWorkspace();
        Plan plan = null!;

        this.Given(GivenSourceWithBomAndWithoutFinalNewline, "source with bom and without final newline")
            .When(WhenPlanningRename, "planning rename")
            .Then(ThenPreserveTheBomAndFinalNewlineState, "preserve the bom and final newline state")
            .BDDfy();

        void GivenSourceWithBomAndWithoutFinalNewline() => workspace.Add("A/Service.cs", SemanticWorkspace.Service, bom: true);

        async Task WhenPlanningRename()
        {
            plan = await workspace.PlanRename(workspace.Rename);
        }

        void ThenPreserveTheBomAndFinalNewlineState()
        {
            var after = Convert.FromBase64String(Assert.Single(plan.Edits).After);
            Assert.True(after.AsSpan().StartsWith(new byte[] { 0xef, 0xbb, 0xbf }));
            Assert.NotEqual((byte)'\n', after[^1]);
            Assert.Contains("\\ No newline at end of file", plan.Patch);
        }
    }

    [Fact]
    public void CompactPatchOmitsDistantUnchangedContext()
    {
        using var workspace = new SemanticWorkspace();
        string source = null!;
        Plan plan = null!;

        this.Given(GivenDistantReferencesToTheSameField, "distant references to the same field")
            .When(WhenPlanningTheFieldRename, "planning the field rename")
            .Then(ThenProduceSeparateHunksAndPreserveOriginalBytes, "produce separate hunks and preserve original bytes")
            .BDDfy();

        void GivenDistantReferencesToTheSameField()
        {
            var padding = string.Concat(Enumerable.Range(0, 100).Select(i => $"// unchanged {i}\n"));
            source = $"namespace Demo;\nclass Service {{ int field;\n{padding}int Use() => field;\n}}\n";
            workspace.Add("A/Service.cs", source);
        }

        async Task WhenPlanningTheFieldRename()
        {
            plan = await workspace.PlanRename(workspace.Rename with { Symbol = "F:Demo.Service.field", NewName = "data" });
        }

        void ThenProduceSeparateHunksAndPreserveOriginalBytes()
        {
            Assert.Equal(2, plan.Patch.Split("\n@@ -").Length - 1);
            Assert.Contains("-class Service { int field;\n+class Service { int data;\n", plan.Patch);
            Assert.Contains("-int Use() => field;\n+int Use() => data;\n", plan.Patch);
            Assert.DoesNotContain("// unchanged 50", plan.Patch);
            Assert.Equal(Encoding.UTF8.GetBytes(source), Convert.FromBase64String(Assert.Single(plan.Edits).Before));
        }
    }

    [Fact]
    public void CrOnlySourceAndPatchAreByteExact()
    {
        using var workspace = new SemanticWorkspace();
        const string before = "namespace Demo;\rclass Service {\r int value;\r int Use() => value;\r}\r";
        const string after = "namespace Demo;\rclass Service {\r int data;\r int Use() => data;\r}\r";
        const string marker = "\n\\ No newline at end of file\n";
        Plan plan = null!;

        this.Given(GivenSourceWithCarriageReturnLineEndings, "source with carriage return line endings")
            .When(WhenPlanningTheFieldRename, "planning the field rename")
            .Then(ThenPreserveTheExactEditedBytesAndPatch, "preserve the exact edited bytes and patch")
            .BDDfy();

        void GivenSourceWithCarriageReturnLineEndings() => workspace.Add("A/Service.cs", before);

        async Task WhenPlanningTheFieldRename()
        {
            plan = await workspace.PlanRename(workspace.Rename with { Symbol = "F:Demo.Service.value", NewName = "data" });
        }

        void ThenPreserveTheExactEditedBytesAndPatch()
        {
            var edit = Assert.Single(plan.Edits);
            Assert.Equal(before, File.ReadAllText(workspace.Source));
            Assert.Equal(Encoding.UTF8.GetBytes(before), Convert.FromBase64String(edit.Before));
            Assert.Equal(Encoding.UTF8.GetBytes(after), Convert.FromBase64String(edit.After));
            Assert.Equal($"--- a/A/Service.cs\n+++ b/A/Service.cs\n@@ -1,1 +1,1 @@\n-{before}{marker}+{after}{marker}", plan.Patch);
        }
    }

    private static void AssertSourceTokens(string expected, string source)
    {
        static string[] Tokens(string text) => SyntaxFactory.ParseTokens(text)
            .Where(token => token.RawKind != (int)SyntaxKind.EndOfFileToken)
            .Select(token => token.Text).ToArray();

        var expectedTokens = Tokens(expected);
        var sourceTokens = Tokens(source);
        Assert.True(Enumerable.Range(0, Math.Max(0, sourceTokens.Length - expectedTokens.Length + 1))
            .Any(index => sourceTokens.AsSpan(index, expectedTokens.Length).SequenceEqual(expectedTokens)),
            $"Expected C# tokens for '{expected}' in:{Environment.NewLine}{source}");
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
