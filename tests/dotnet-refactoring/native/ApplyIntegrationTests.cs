namespace RefactorTool.Tests;

[Trait("Boundary", "Sdk")]
[Collection(SdkCollection.Name)]
public sealed class ApplyIntegrationTests
{
    [Theory]
    [InlineData("unmodified", "input_drift")]
    [InlineData("glob-member", "plan_drift")]
    [InlineData("forged-edit", "plan_drift")]
    public async Task RenameApplyRefusesChangesSincePreview(string change, string expectedCode)
    {
        using var fixture = new SdkFixture(twoProjects: change == "unmodified");
        await fixture.Restore();
        var request = change == "unmodified" ? fixture.Rename with { Symbol = "F:Demo.Service.Field", NewName = "Data" } : fixture.Rename;
        (await fixture.Preview(request)).Previewed();
        if (change == "unmodified") File.AppendAllText(fixture.Consumer, "// user edit\n");
        if (change == "glob-member") fixture.Write("A/Added.cs", "class Added {}\n");
        if (change == "forged-edit") Tamper(fixture, "modify");
        var original = fixture.Snapshot();
        (await fixture.Apply()).Refused(expectedCode);
        fixture.AssertSnapshot(original);
    }

    [Theory]
    [InlineData("output-race", "invalid_output")]
    [InlineData("source-drift", "input_drift")]
    [InlineData("forged-create", "plan_drift")]
    public async Task ExtractApplyRefusesChangedOutputInputOrPlan(string change, string expectedCode)
    {
        using var fixture = new SdkFixture();
        await fixture.Restore();
        (await fixture.Preview(fixture.Extract)).Previewed();
        if (change == "output-race") File.WriteAllText(fixture.Output, "// belongs to another writer");
        if (change == "source-drift") File.AppendAllText(fixture.Source, "// drift");
        if (change == "forged-create") Tamper(fixture, "create");
        var original = fixture.Snapshot();
        (await fixture.Apply()).Refused(expectedCode);
        fixture.AssertSnapshot(original);
        if (change == "output-race") Assert.Equal("// belongs to another writer", File.ReadAllText(fixture.Output));
        else Assert.False(File.Exists(fixture.Output));
    }

    [Theory]
    [InlineData(false)]
    [InlineData(true)]
    public async Task ExclusiveSourceOrProjectHandleRefusesBeforeWrites(bool project)
    {
        using var fixture = new SdkFixture();
        await fixture.Restore();
        (await fixture.Preview()).Previewed();
        var original = fixture.Snapshot();
        using (var held = new FileStream(project ? fixture.Project : fixture.Source, FileMode.Open, FileAccess.Read, FileShare.None))
        {
            var result = await fixture.Apply();
            result.Refused("apply_preflight_failed");
            Assert.False(result.Json.TryGetProperty("recovery", out _));
        }
        fixture.AssertSnapshot(original);
    }

    [Fact]
    public async Task ReadOnlyConsumerRefusesBeforeAnySourceChange()
    {
        using var fixture = new SdkFixture(twoProjects: true);
        await fixture.Restore();
        (await fixture.Preview()).Previewed();
        var original = fixture.Snapshot();
        var attributes = File.GetAttributes(fixture.Consumer);
        try
        {
            File.SetAttributes(fixture.Consumer, attributes | FileAttributes.ReadOnly);
            var result = await fixture.Apply();
            Assert.Equal(2, result.ExitCode);
            Assert.False(result.Json.GetProperty("sourceWrites").GetBoolean());
            fixture.AssertSnapshot(original);
        }
        finally { File.SetAttributes(fixture.Consumer, attributes); }
    }

    [Theory]
    [InlineData(false, "input_drift")]
    [InlineData(true, "apply_preflight_failed")]
    public async Task CanonicalReadOnlyInputDetectsRetargetOrRemoval(bool remove, string expectedCode)
    {
        using var fixture = new SdkFixture();
        var originalConfig = fixture.Write("original-input/Config.props", "<Project />");
        var replacementConfig = fixture.Write("replacement-input/Config.props", "<Project />");
        await fixture.Junction("input-alias", Path.GetDirectoryName(originalConfig)!);
        fixture.AppendProject("""<ItemGroup><AdditionalFiles Include="../input-alias/Config.props" /></ItemGroup>""");
        await fixture.Restore();
        (await fixture.Preview()).Previewed();
        var aliasPath = fixture.PathFor("input-alias/Config.props");
        var input = Assert.Single(fixture.Plan().Inputs, input => input.Path == aliasPath);
        AssertCanonicalInput(input, "original-input");
        if (remove) File.Delete(originalConfig);
        else
        {
            fixture.RemoveJunction("input-alias");
            await fixture.Junction("input-alias", Path.GetDirectoryName(replacementConfig)!);
        }
        var original = fixture.Snapshot();
        var result = await fixture.Apply();
        result.Refused(expectedCode);
        Assert.False(result.Json.TryGetProperty("recovery", out _));
        fixture.AssertSnapshot(original);
        if (!remove)
        {
            (await fixture.Preview()).Previewed();
            AssertCanonicalInput(Assert.Single(fixture.Plan().Inputs, i => i.Path == aliasPath), "replacement-input");
            (await fixture.Apply()).Applied();
        }
    }

    [Fact]
    public async Task PlanAndEditableSourceJunctionsAreRefused()
    {
        using var fixture = new SdkFixture();
        var outside = fixture.Write("linked-source/Extra.cs", "public class Extra {}");
        await fixture.Junction("plan-alias", Path.GetDirectoryName(outside)!);
        var original = fixture.Snapshot();
        fixture.RefusedPreview(await fixture.Preview(planPath: fixture.PathFor("plan-alias/plan.json")), "linked_path");
        fixture.AssertSnapshot(original);
        await fixture.Junction("A/alias", Path.GetDirectoryName(outside)!);
        fixture.AppendProject("""<ItemGroup><Compile Remove="alias/**/*.cs" /><Compile Include="alias/Extra.cs" /></ItemGroup>""");
        await fixture.Restore();
        original = fixture.Snapshot();
        fixture.RefusedPreview(await fixture.Preview(), "linked_path");
        fixture.AssertSnapshot(original);
    }

    [Fact]
    public async Task PreviewPlanCannotEnterLoadedProjectDirectory()
    {
        using var fixture = new SdkFixture(twoProjects: true);
        await fixture.Restore();
        var original = fixture.Snapshot();
        fixture.RefusedPreview(await fixture.Preview(planPath: fixture.PathFor("B/plan.json")), "unsafe_plan_path");
        fixture.AssertSnapshot(original);
    }

    private static void Tamper(SdkFixture fixture, string kind)
    {
        var plan = fixture.Plan();
        var edit = Assert.Single(plan.Edits, edit => edit.Kind == kind);
        var forged = edit with { After = Convert.ToBase64String("forged bytes"u8) };
        File.WriteAllText(fixture.PlanPath, Data.Serialize(plan with { Edits = plan.Edits.Select(e => e == edit ? forged : e).ToArray() }));
    }

    private static void AssertCanonicalInput(InputFile input, string physicalParent)
    {
        Assert.NotNull(input.CanonicalPath);
        Assert.Equal("Config.props", Path.GetFileName(input.CanonicalPath), ignoreCase: true);
        Assert.Equal(physicalParent, Path.GetFileName(Path.GetDirectoryName(input.CanonicalPath)), ignoreCase: true);
    }
}
