namespace RefactorTool.IntegrationTests;

[Trait("Boundary", "Sdk")]
[Collection(SdkCollection.Name)]
public sealed class ApplyIntegrationTests
{
    /// <summary>Rejects a rename plan when a captured input, source membership, or proposed edit changes.</summary>
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

    /// <summary>Rejects extraction if the output appears or the create edit is forged after preview.</summary>
    [RefactorSdkTheory]
    [InlineData("output-race", "invalid_output")]
    [InlineData("forged-create", "plan_drift")]
    public void ExtractApplyRefusesOutputRaceOrForgedPlan(string change, string expectedCode)
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

    /// <summary>Rejects a retargeted input until a fresh plan captures its new physical path.</summary>
    [RefactorSdkFact(requiresJunction: true)]
    public void CanonicalReadOnlyInputDetectsRetargetAndAcceptsFreshPreview()
    {
        using var fixture = new SdkFixture();
        var aliasPath = fixture.PathFor("input-alias/Config.props");
        Dictionary<string, byte[]> original = null!;
        CommandResult refused = null!, preview = null!, applied = null!;

        this.Given(GivenAnSdkCapturedInputRetargetedToIdenticalBytes, "an SDK-captured input retargeted to identical bytes")
            .When(WhenApplyingTheStalePreview, "applying the stale preview")
            .Then(ThenRefuseBeforeWritesAndReportNoRecovery, "refuse before writes and report no recovery")
            .When(WhenPreviewingTheRetargetedWorkspace, "previewing the retargeted workspace")
            .Then(ThenCaptureTheNewPhysicalInputWithoutWriting, "capture the new physical input without writing")
            .When(WhenApplyingTheFreshPreview, "applying the fresh preview")
            .Then(ThenApplyTheFreshPlan, "apply the fresh plan")
            .BDDfy();

        async Task GivenAnSdkCapturedInputRetargetedToIdenticalBytes()
        {
            var originalConfig = fixture.Write("original-input/Config.props", "<Project />");
            var replacementConfig = fixture.Write("replacement-input/Config.props", "<Project />");
            await fixture.Junction("input-alias", Path.GetDirectoryName(originalConfig)!);
            fixture.AppendProject("""<ItemGroup><AdditionalFiles Include="../input-alias/Config.props" /></ItemGroup>""");
            await fixture.Restore();
            (await fixture.Preview()).Previewed();
            AssertCanonicalInput(Assert.Single(fixture.Plan().Inputs, input => input.Path == aliasPath), "original-input");
            fixture.RemoveJunction("input-alias");
            await fixture.Junction("input-alias", Path.GetDirectoryName(replacementConfig)!);
            original = fixture.Snapshot();
        }

        async Task WhenApplyingTheStalePreview() => refused = await fixture.Apply();

        void ThenRefuseBeforeWritesAndReportNoRecovery()
        {
            refused.Refused("input_drift");
            Assert.False(refused.Json.TryGetProperty("recovery", out _));
            fixture.AssertSnapshot(original);
        }

        async Task WhenPreviewingTheRetargetedWorkspace() => preview = await fixture.Preview();

        void ThenCaptureTheNewPhysicalInputWithoutWriting()
        {
            preview.Previewed();
            AssertCanonicalInput(Assert.Single(fixture.Plan().Inputs, input => input.Path == aliasPath), "replacement-input");
            fixture.AssertSnapshot(original);
        }

        async Task WhenApplyingTheFreshPreview() => applied = await fixture.Apply();

        void ThenApplyTheFreshPlan() => applied.Applied();
    }

    /// <summary>Rejects an evaluated editable Compile item that reaches its source through a junction.</summary>
    [RefactorSdkFact(requiresJunction: true)]
    public void EditableCompileSourceJunctionIsRefused()
    {
        using var fixture = new SdkFixture();
        Dictionary<string, byte[]> original = null!;
        CommandResult preview = null!;

        this.Given(GivenAnEditableSourceThroughAJunction, "an evaluated Compile source through a junction")
            .When(WhenPreviewingTheLinkedSource, "previewing the linked source")
            .Then(ThenRefuseWithoutChangingSource, "refuse without changing source")
            .BDDfy();

        async Task GivenAnEditableSourceThroughAJunction()
        {
            var outside = fixture.Write("linked-source/Extra.cs", "public class Extra {}");
            await fixture.Junction("A/alias", Path.GetDirectoryName(outside)!);
            fixture.AppendProject("""<ItemGroup><Compile Remove="alias/**/*.cs" /><Compile Include="alias/Extra.cs" /></ItemGroup>""");
            await fixture.Restore();
            original = fixture.Snapshot();
        }

        async Task WhenPreviewingTheLinkedSource() => preview = await fixture.Preview();

        void ThenRefuseWithoutChangingSource()
        {
            fixture.RefusedPreview(preview, "linked_path");
            fixture.AssertSnapshot(original);
        }
    }

    /// <summary>Refuses a plan destination inside any loaded project directory.</summary>
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
