namespace RefactorTool.IntegrationTests;

[Trait("Boundary", "Sdk")]
[Collection(SdkCollection.Name)]
public sealed class ApplyIntegrationTests
{
    [RefactorSdkTheory]
    [InlineData("unmodified", "input_drift")]
    [InlineData("glob-member", "plan_drift")]
    [InlineData("forged-edit", "plan_drift")]
    public void RenameApplyRefusesChangesSincePreview(string change, string expectedCode)
    {
        using var fixture = new SdkFixture(twoProjects: change == "unmodified");
        Dictionary<string, byte[]> original = null!;
        CommandResult applyingTheStaleRenamePlanResult = null!;

        this.Given(GivenARenamePlanAndDriftSincePreview, "a rename plan and drift since preview")
            .When(WhenApplyingTheStaleRenamePlan, "applying the stale rename plan")
            .Then(ThenRefuseWithoutSourceWrites, "refuse without source writes")
            .BDDfy();

        async Task GivenARenamePlanAndDriftSincePreview()
        {
            await fixture.Restore();
            var request = change == "unmodified" ? fixture.Rename with { Symbol = "F:Demo.Service.Field", NewName = "Data" } : fixture.Rename;
            (await fixture.Preview(request)).Previewed();
            if (change == "unmodified") File.AppendAllText(fixture.Consumer, "// user edit\n");
            if (change == "glob-member") fixture.Write("A/Added.cs", "class Added {}\n");
            if (change == "forged-edit") Tamper(fixture, "modify");
            original = fixture.Snapshot();
        }

        async Task WhenApplyingTheStaleRenamePlan() => applyingTheStaleRenamePlanResult = await fixture.Apply();

        void ThenRefuseWithoutSourceWrites()
        {
            applyingTheStaleRenamePlanResult.Refused(expectedCode);
            fixture.AssertSnapshot(original);
        }
    }

    [RefactorSdkTheory]
    [InlineData("output-race", "invalid_output")]
    [InlineData("source-drift", "input_drift")]
    [InlineData("forged-create", "plan_drift")]
    public void ExtractApplyRefusesChangedOutputInputOrPlan(string change, string expectedCode)
    {
        using var fixture = new SdkFixture();
        Dictionary<string, byte[]> original = null!;
        CommandResult applyingTheStaleExtractionPlanResult = null!;

        this.Given(GivenAnExtractionPlanAndDriftSincePreview, "an extraction plan and drift since preview")
            .When(WhenApplyingTheStaleExtractionPlan, "applying the stale extraction plan")
            .Then(ThenRefuseAndPreserveTheCurrentSources, "refuse and preserve the current sources")
            .BDDfy();

        async Task GivenAnExtractionPlanAndDriftSincePreview()
        {
            await fixture.Restore();
            (await fixture.Preview(fixture.Extract)).Previewed();
            if (change == "output-race") File.WriteAllText(fixture.Output, "// belongs to another writer");
            if (change == "source-drift") File.AppendAllText(fixture.Source, "// drift");
            if (change == "forged-create") Tamper(fixture, "create");
            original = fixture.Snapshot();
        }

        async Task WhenApplyingTheStaleExtractionPlan() => applyingTheStaleExtractionPlanResult = await fixture.Apply();

        void ThenRefuseAndPreserveTheCurrentSources()
        {
            applyingTheStaleExtractionPlanResult.Refused(expectedCode);
            fixture.AssertSnapshot(original);
            if (change == "output-race") Assert.Equal("// belongs to another writer", File.ReadAllText(fixture.Output));
            else Assert.False(File.Exists(fixture.Output));
        }
    }

    [RefactorSdkTheory]
    [InlineData(false)]
    [InlineData(true)]
    public void ExclusiveSourceOrProjectHandleRefusesBeforeWrites(bool project)
    {
        using var fixture = new SdkFixture();
        Dictionary<string, byte[]> original = null!;
        CommandResult result = null!;

        this.Given(GivenAPreviewAndAnExclusiveInputHandle, "a preview and an exclusive input handle")
            .When(WhenApplyingWithTheHandleHeld, "applying with the handle held")
            .Then(ThenRefuseWithoutWritesOrRecovery, "refuse without writes or recovery")
            .BDDfy();

        async Task GivenAPreviewAndAnExclusiveInputHandle()
        {
            await fixture.Restore();
            (await fixture.Preview()).Previewed();
            original = fixture.Snapshot();
        }

        async Task WhenApplyingWithTheHandleHeld()
        {
            using (var held = new FileStream(project ? fixture.Project : fixture.Source, FileMode.Open, FileAccess.Read, FileShare.None))
                result = await fixture.Apply();
        }

        void ThenRefuseWithoutWritesOrRecovery()
        {
            result.Refused("apply_preflight_failed");
            Assert.False(result.Json.TryGetProperty("recovery", out _));
            fixture.AssertSnapshot(original);
        }
    }

    [RefactorSdkFact]
    public void ReadOnlyConsumerRefusesBeforeAnySourceChange()
    {
        using var fixture = new SdkFixture(twoProjects: true);
        Dictionary<string, byte[]> original = null!;
        FileAttributes attributes = default;
        CommandResult result = null!;

        this.Given(GivenAPreviewAndAReadOnlyConsumer, "a preview and a read only consumer")
            .When(WhenApplyingWithTheConsumerReadOnly, "applying with the consumer read only")
            .Then(ThenRefuseBeforeAnySourceWrite, "refuse before any source write")
            .BDDfy();

        async Task GivenAPreviewAndAReadOnlyConsumer()
        {
            await fixture.Restore();
            (await fixture.Preview()).Previewed();
            original = fixture.Snapshot();
            attributes = File.GetAttributes(fixture.Consumer);
        }

        async Task WhenApplyingWithTheConsumerReadOnly()
        {
            try
            {
                File.SetAttributes(fixture.Consumer, attributes | FileAttributes.ReadOnly);
                result = await fixture.Apply();
            }
            finally { File.SetAttributes(fixture.Consumer, attributes); }
        }

        void ThenRefuseBeforeAnySourceWrite()
        {
            Assert.Equal(2, result.ExitCode);
            Assert.False(result.Json.GetProperty("sourceWrites").GetBoolean());
            fixture.AssertSnapshot(original);
        }
    }

    [RefactorSdkTheory]
    [InlineData(false, "input_drift")]
    [InlineData(true, "apply_preflight_failed")]
    public void CanonicalReadOnlyInputDetectsRetargetOrRemoval(bool remove, string expectedCode)
    {
        using var fixture = new SdkFixture();
        string aliasPath = null!;
        Dictionary<string, byte[]> original = null!;
        CommandResult result = null!;

        this.Given(GivenAPreviewWithARetargetedOrRemovedCanonicalInput, "a preview with a retargeted or removed canonical input")
            .When(WhenApplyingThePreview, "applying the preview")
            .Then(ThenRefuseBeforeWritesAndReportNoRecovery, "refuse before writes and report no recovery")
            .BDDfy();

        async Task GivenAPreviewWithARetargetedOrRemovedCanonicalInput()
        {
            var originalConfig = fixture.Write("original-input/Config.props", "<Project />");
            var replacementConfig = fixture.Write("replacement-input/Config.props", "<Project />");
            await fixture.Junction("input-alias", Path.GetDirectoryName(originalConfig)!);
            fixture.AppendProject("""<ItemGroup><AdditionalFiles Include="../input-alias/Config.props" /></ItemGroup>""");
            await fixture.Restore();
            (await fixture.Preview()).Previewed();
            aliasPath = fixture.PathFor("input-alias/Config.props");
            var input = Assert.Single(fixture.Plan().Inputs, input => input.Path == aliasPath);
            AssertCanonicalInput(input, "original-input");
            if (remove) File.Delete(originalConfig);
            else
            {
                fixture.RemoveJunction("input-alias");
                await fixture.Junction("input-alias", Path.GetDirectoryName(replacementConfig)!);
            }
            original = fixture.Snapshot();
        }

        async Task WhenApplyingThePreview()
        {
            result = await fixture.Apply();
        }

        async Task ThenRefuseBeforeWritesAndReportNoRecovery()
        {
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
    }

    [RefactorSdkFact]
    public void PlanAndEditableSourceJunctionsAreRefused()
    {
        using var fixture = new SdkFixture();
        string outside = null!;
        Dictionary<string, byte[]> original = null!;
        CommandResult previewingToTheLinkedDestinationResult = null!;
        CommandResult previewingTheLinkedSourceResult = null!;

        this.Given(GivenAPlanDestinationThroughAJunction, "a plan destination through a junction")
            .When(WhenPreviewingToTheLinkedDestination, "previewing to the linked destination")
            .Then(ThenRefuseWithoutWritingToTheJunction, "refuse without writing to the junction")
            .Given(GivenAnEditableSourceThroughAJunction, "an editable source through a junction")
            .When(WhenPreviewingTheLinkedSource, "previewing the linked source")
            .Then(ThenRefuseWithoutChangingSource, "refuse without changing source")
            .BDDfy();

        async Task GivenAPlanDestinationThroughAJunction()
        {
            outside = fixture.Write("linked-source/Extra.cs", "public class Extra {}");
            await fixture.Junction("plan-alias", Path.GetDirectoryName(outside)!);
            original = fixture.Snapshot();
        }

        async Task WhenPreviewingToTheLinkedDestination() => previewingToTheLinkedDestinationResult = await fixture.Preview(planPath: fixture.PathFor("plan-alias/plan.json"));

        void ThenRefuseWithoutWritingToTheJunction()
        {
            fixture.RefusedPreview(previewingToTheLinkedDestinationResult, "linked_path");
            fixture.AssertSnapshot(original);
        }

        async Task GivenAnEditableSourceThroughAJunction()
        {
            await fixture.Junction("A/alias", Path.GetDirectoryName(outside)!);
            fixture.AppendProject("""<ItemGroup><Compile Remove="alias/**/*.cs" /><Compile Include="alias/Extra.cs" /></ItemGroup>""");
            await fixture.Restore();
            original = fixture.Snapshot();
        }

        async Task WhenPreviewingTheLinkedSource() => previewingTheLinkedSourceResult = await fixture.Preview();

        void ThenRefuseWithoutChangingSource()
        {
            fixture.RefusedPreview(previewingTheLinkedSourceResult, "linked_path");
            fixture.AssertSnapshot(original);
        }
    }

    [RefactorSdkFact]
    public void PreviewPlanCannotEnterLoadedProjectDirectory()
    {
        using var fixture = new SdkFixture(twoProjects: true);
        Dictionary<string, byte[]> original = null!;
        CommandResult previewingToThatDestinationResult = null!;

        this.Given(GivenAPlanDestinationInsideALoadedProject, "a plan destination inside a loaded project")
            .When(WhenPreviewingToThatDestination, "previewing to that destination")
            .Then(ThenRefuseWithoutWritingThePlan, "refuse without writing the plan")
            .BDDfy();

        async Task GivenAPlanDestinationInsideALoadedProject()
        {
            await fixture.Restore();
            original = fixture.Snapshot();
        }

        async Task WhenPreviewingToThatDestination() => previewingToThatDestinationResult = await fixture.Preview(planPath: fixture.PathFor("B/plan.json"));

        void ThenRefuseWithoutWritingThePlan()
        {
            fixture.RefusedPreview(previewingToThatDestinationResult, "unsafe_plan_path");
            fixture.AssertSnapshot(original);
        }
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
