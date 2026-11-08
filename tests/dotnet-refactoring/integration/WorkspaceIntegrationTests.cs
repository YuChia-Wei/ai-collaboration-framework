namespace RefactorTool.IntegrationTests;

[Trait("Boundary", "Sdk")]
[Collection(SdkCollection.Name)]
public sealed class WorkspaceIntegrationTests
{
    [RefactorSdkFact]
    public void ExplicitFrameworkDoesNotAdmitMultiTargetProject()
    {
        using var fixture = new SdkFixture();
        CommandResult previewingTheSelectedFrameworkResult = null!;

        this.Given(GivenAMultiTargetProjectAndAnExplicitFramework, "a multi target project and an explicit framework")
            .When(WhenPreviewingTheSelectedFramework, "previewing the selected framework")
            .Then(ThenRefuseTheMultiTargetWorkspace, "refuse the multi target workspace")
            .BDDfy();

        void GivenAMultiTargetProjectAndAnExplicitFramework() => fixture.Write("A/A.csproj", File.ReadAllText(fixture.Project).Replace(
            "<TargetFramework>net10.0</TargetFramework>", "<TargetFrameworks>net10.0;net9.0</TargetFrameworks>"));

        async Task WhenPreviewingTheSelectedFramework() => previewingTheSelectedFrameworkResult = await fixture.Preview(fixture.Rename with { Framework = "net10.0" });

        void ThenRefuseTheMultiTargetWorkspace() => fixture.RefusedPreview(previewingTheSelectedFrameworkResult, "multiple_frameworks");
    }

    [RefactorSdkFact]
    public void ExplicitLinkedCompileItemIsRejected()
    {
        using var fixture = new SdkFixture();
        Dictionary<string, byte[]> original = null!;
        CommandResult previewingRenameResult = null!;

        this.Given(GivenARestoredProjectWithALinkedCompileItem, "a restored project with a linked compile item")
            .When(WhenPreviewingRename, "previewing rename")
            .Then(ThenRefuseTheLinkedFileWithoutWrites, "refuse the linked file without writes")
            .BDDfy();

        async Task GivenARestoredProjectWithALinkedCompileItem()
        {
            fixture.Write("Linked.cs", "class Linked {}");
            fixture.AppendProject("""<ItemGroup><Compile Include="../Linked.cs" Link="Linked.cs" /></ItemGroup>""");
            await fixture.Restore();
            original = fixture.Snapshot();
        }

        async Task WhenPreviewingRename() => previewingRenameResult = await fixture.Preview();

        void ThenRefuseTheLinkedFileWithoutWrites()
        {
            fixture.RefusedPreview(previewingRenameResult, "linked_file");
            fixture.AssertSnapshot(original);
        }
    }

    [RefactorSdkTheory]
    [InlineData(false)]
    [InlineData(true)]
    public void MissingProjectIsIdentifiedWhetherInSolutionOrReference(bool reference)
    {
        using var fixture = new SdkFixture();
        Request request = null!;
        Dictionary<string, byte[]> original = null!;
        CommandResult result = null!;

        this.Given(GivenAMissingSolutionOrReferencedProject, "a missing solution or referenced project")
            .When(WhenPreviewingRename, "previewing rename")
            .Then(ThenReportTheMissingProjectWithoutWrites, "report the missing project without writes")
            .BDDfy();

        async Task GivenAMissingSolutionOrReferencedProject()
        {
            request = fixture.Rename;
            if (reference)
            {
                fixture.AppendProject("""<ItemGroup><ProjectReference Include="Missing.csproj" /></ItemGroup>""");
                await fixture.Restore();
            }
            else
            {
                var solution = fixture.Write("Missing.slnx", """<Solution><Project Path="Missing.csproj" /></Solution>""");
                request = request with { Workspace = solution };
            }
            original = fixture.Snapshot();
        }

        async Task WhenPreviewingRename()
        {
            result = await fixture.Preview(request);
        }

        void ThenReportTheMissingProjectWithoutWrites()
        {
            fixture.RefusedPreview(result, "missing_file");
            Assert.Contains("Missing.csproj", result.Text("message"));
            fixture.AssertSnapshot(original);
        }
    }

    [RefactorSdkFact]
    public void MissingCompileInputIsIdentifiedBeforePlan()
    {
        using var fixture = new SdkFixture();
        Dictionary<string, byte[]> original = null!;
        CommandResult result = null!;

        this.Given(GivenAMissingCompileItem, "a missing compile item")
            .When(WhenPreviewingRename, "previewing rename")
            .Then(ThenReportTheMissingSourceWithoutWrites, "report the missing source without writes")
            .BDDfy();

        async Task GivenAMissingCompileItem()
        {
            fixture.AppendProject("""<ItemGroup><Compile Include="Missing.cs" /></ItemGroup>""");
            await fixture.Restore();
            original = fixture.Snapshot();
        }

        async Task WhenPreviewingRename()
        {
            result = await fixture.Preview();
        }

        void ThenReportTheMissingSourceWithoutWrites()
        {
            fixture.RefusedPreview(result, "missing_file");
            Assert.Contains("Missing.cs", result.Text("message"));
            fixture.AssertSnapshot(original);
        }
    }

    [RefactorSdkFact]
    public void AuthoredGeneratedSuffixCannotBeEditedThroughRelatedRename()
    {
        using var fixture = new SdkFixture();
        Dictionary<string, byte[]> original = null!;
        CommandResult result = null!;

        this.Given(GivenAnAuthoredRelatedMemberInAGeneratedSuffixFile, "an authored related member in a generated suffix file")
            .When(WhenPreviewingTheRelatedRename, "previewing the related rename")
            .Then(ThenRefuseGeneratedSourceEdits, "refuse generated source edits")
            .BDDfy();

        async Task GivenAnAuthoredRelatedMemberInAGeneratedSuffixFile()
        {
            fixture.Write("A/Generated.g.cs", "namespace Demo; class Generated : Service { public override int Get(int value) => base.Get(value); }");
            await fixture.Restore();
            original = fixture.Snapshot();
        }

        async Task WhenPreviewingTheRelatedRename()
        {
            result = await fixture.Preview();
        }

        void ThenRefuseGeneratedSourceEdits()
        {
            Assert.Contains(result.Text("code"), new[] { "uneditable_symbol", "uneditable_reference", "uneditable_source" });
            fixture.RefusedPreview(result, result.Text("code"));
            Assert.Contains("Generated.g.cs", result.Text("message"));
            fixture.AssertSnapshot(original);
        }
    }

    [RefactorSdkFact]
    public void ConditionalConfigurationAndImportedFrameworkAreReported()
    {
        using var fixture = new SdkFixture();
        CommandResult previewingDebugConfigurationResult = null!;
        CommandResult previewingReleaseConfigurationResult = null!;

        this.Given(GivenAnImportedFrameworkAndConditionalDefines, "an imported framework and conditional defines")
            .When(WhenPreviewingDebugConfiguration, "previewing debug configuration")
            .Then(ThenReportDebugDefinesAndInactiveCode, "report debug defines and inactive code")
            .When(WhenPreviewingReleaseConfiguration, "previewing release configuration")
            .Then(ThenReportTheReleaseFrameworkAndDefines, "report the release framework and defines")
            .BDDfy();

        async Task GivenAnImportedFrameworkAndConditionalDefines()
        {
            fixture.Write("Directory.Build.props", """
                <Project><PropertyGroup><TargetFramework>net10.0</TargetFramework><DefineConstants>$(DefineConstants);CUSTOM</DefineConstants></PropertyGroup></Project>
                """);
            fixture.Write("A/A.csproj", File.ReadAllText(fixture.Project).Replace("<TargetFramework>net10.0</TargetFramework>", ""));
            fixture.Write("A/Conditional.cs", "#if DEBUG\nclass Active {}\n#else\nclass Inactive {}\n#endif\n");
            await fixture.Restore();
        }

        async Task WhenPreviewingDebugConfiguration() => previewingDebugConfigurationResult = await fixture.Preview();

        void ThenReportDebugDefinesAndInactiveCode()
        {
            previewingDebugConfigurationResult.Previewed();
            var debug = fixture.Plan();
            Assert.Contains("DEBUG", Assert.Single(debug.Projects).Defines);
            Assert.Contains(debug.Limits, limit => limit.Contains(fixture.PathFor("A/Conditional.cs"), StringComparison.OrdinalIgnoreCase));
        }

        async Task WhenPreviewingReleaseConfiguration() => previewingReleaseConfigurationResult = await fixture.Preview(fixture.Rename with { Configuration = "Release" });

        void ThenReportTheReleaseFrameworkAndDefines()
        {
            previewingReleaseConfigurationResult.Previewed();
            var release = Assert.Single(fixture.Plan().Projects);
            Assert.Equal("net10.0", release.Framework);
            Assert.Equal("Release", release.Configuration);
            Assert.Contains("CUSTOM", release.Defines);
            Assert.DoesNotContain("DEBUG", release.Defines);
        }
    }

    [RefactorSdkFact]
    public void ExternalSdkIntermediatesAreCapturedWithoutBeingEdited()
    {
        using var fixture = new SdkFixture();
        CommandResult previewingRenameResult = null!;
        CommandResult applyingRenameResult = null!;

        this.Given(GivenSdkIntermediatesOutsideTheProject, "sdk intermediates outside the project")
            .When(WhenPreviewingRename, "previewing rename")
            .Then(ThenCaptureIntermediatesAsInputsOnly, "capture intermediates as inputs only")
            .When(WhenApplyingRename, "applying rename")
            .Then(ThenApplyTheAuthoredEdit, "apply the authored edit")
            .BDDfy();

        async Task GivenSdkIntermediatesOutsideTheProject()
        {
            fixture.Write("Directory.Build.props", """
                <Project><PropertyGroup><UseArtifactsOutput>true</UseArtifactsOutput><ArtifactsPath>$(MSBuildThisFileDirectory)artifacts</ArtifactsPath></PropertyGroup></Project>
                """);
            await fixture.Restore();
        }

        async Task WhenPreviewingRename() => previewingRenameResult = await fixture.Preview();

        void ThenCaptureIntermediatesAsInputsOnly()
        {
            previewingRenameResult.Previewed();
            var plan = fixture.Plan();
            Assert.Contains(plan.Inputs, input =>
                Path.GetRelativePath(fixture.PathFor("artifacts"), input.Path) is var relative &&
                !relative.StartsWith("..", StringComparison.Ordinal) && relative.EndsWith("AssemblyAttributes.cs", StringComparison.Ordinal));
            Assert.Equal(fixture.Source, Assert.Single(plan.Edits).Path);
        }

        async Task WhenApplyingRename() => applyingRenameResult = await fixture.Apply();

        void ThenApplyTheAuthoredEdit() => applyingRenameResult.Applied();
    }

    [RefactorSdkFact]
    public void BinAncestorOutsideProjectDoesNotMarkAuthoredSourceGenerated()
    {
        using var fixture = new SdkFixture();
        string project = null!;
        string source = null!;
        CommandResult previewingRenameResult = null!;

        this.Given(GivenAnAuthoredProjectUnderABinAncestor, "an authored project under a bin ancestor")
            .When(WhenPreviewingRename, "previewing rename")
            .Then(ThenIncludeTheAuthoredSourceEdit, "include the authored source edit")
            .BDDfy();

        async Task GivenAnAuthoredProjectUnderABinAncestor()
        {
            project = fixture.Write("bin/A/A.csproj", File.ReadAllText(fixture.Project));
            source = fixture.Write("bin/A/Service.cs", File.ReadAllBytes(fixture.Source));
            await fixture.Restore(project);
        }

        async Task WhenPreviewingRename() => previewingRenameResult = await fixture.Preview(fixture.Rename with { Workspace = project, Project = project, Symbol = "F:Demo.Service.Field", NewName = "Data" });

        void ThenIncludeTheAuthoredSourceEdit()
        {
            previewingRenameResult.Previewed();
            Assert.Equal(source, Assert.Single(fixture.Plan().Edits).Path);
        }
    }

    [RefactorSdkFact]
    public void VisualBasicSolutionMemberIsRejected()
    {
        using var fixture = new SdkFixture();
        string solution = null!;
        CommandResult previewingTheMixedSolutionResult = null!;

        this.Given(GivenASolutionWithAVisualBasicProject, "a solution with a visual basic project")
            .When(WhenPreviewingTheMixedSolution, "previewing the mixed solution")
            .Then(ThenRefuseTheUnsupportedWorkspace, "refuse the unsupported workspace")
            .BDDfy();

        void GivenASolutionWithAVisualBasicProject()
        {
            fixture.Write("VisualBasic.vbproj", """<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup><TargetFramework>net10.0</TargetFramework></PropertyGroup></Project>""");
            solution = fixture.Write("Mixed.slnx", """<Solution><Project Path="VisualBasic.vbproj" /><Project Path="A/A.csproj" /></Solution>""");
        }

        async Task WhenPreviewingTheMixedSolution() => previewingTheMixedSolutionResult = await fixture.Preview(fixture.Rename with { Workspace = solution });

        void ThenRefuseTheUnsupportedWorkspace() => fixture.RefusedPreview(previewingTheMixedSolutionResult, "unsupported_project");
    }

    [RefactorSdkTheory]
    [InlineData(false)]
    [InlineData(true)]
    public void ClassicSolutionFolderAndProjectEntryKeepCompilationGraph(bool classic)
    {
        using var fixture = new SdkFixture(twoProjects: true);
        string entry = null!;
        CommandResult previewingFromTheSelectedEntryResult = null!;

        this.Given(GivenTwoReferencedProjectsAndAClassicSolutionFolder, "two referenced projects and a classic solution folder")
            .When(WhenPreviewingFromTheSelectedEntry, "previewing from the selected entry")
            .Then(ThenKeepBothProjectsAndUpdateTheConsumer, "keep both projects and update the consumer")
            .BDDfy();

        async Task GivenTwoReferencedProjectsAndAClassicSolutionFolder()
        {
            await fixture.Restore();
            var solution = fixture.Write("Classic.sln", """
                Microsoft Visual Studio Solution File, Format Version 12.00
                Project("{2150E333-8FDC-42A3-9474-1A3956D46DE8}") = "src.Core", "src.Core", "{F0000000-0000-0000-0000-000000000000}"
                EndProject
                Project("{FAE04EC0-301F-11D3-BF4B-00C04F79EFBC}") = "A", "A\A.csproj", "{A0000000-0000-0000-0000-000000000000}"
                EndProject
                Project("{FAE04EC0-301F-11D3-BF4B-00C04F79EFBC}") = "B", "B\B.csproj", "{B0000000-0000-0000-0000-000000000000}"
                EndProject
                Global
                EndGlobal
                """);
            entry = classic ? solution : fixture.PathFor("B/B.csproj");
        }

        async Task WhenPreviewingFromTheSelectedEntry() => previewingFromTheSelectedEntryResult = await fixture.Preview(fixture.Rename with { Workspace = entry });

        void ThenKeepBothProjectsAndUpdateTheConsumer()
        {
            previewingFromTheSelectedEntryResult.Previewed();
            var plan = fixture.Plan();
            Assert.Equal(2, plan.Projects.Length);
            Assert.Contains("service.Fetch(2)", SemanticWorkspace.After(plan, fixture.Consumer));
        }
    }

    [RefactorSdkTheory]
    [InlineData("../Shared.cs", "linked_file")]
    [InlineData("Extra.cs", "unexpected_source")]
    public void DesignTimeOnlySourceCannotSilentlyChangeTheEditableGraph(string compileItem, string expectedCode)
    {
        using var fixture = new SdkFixture();
        Dictionary<string, byte[]> original = null!;
        CommandResult previewingRenameResult = null!;

        this.Given(GivenAnExtraDesignTimeCompileItem, "an extra design time compile item")
            .When(WhenPreviewingRename, "previewing rename")
            .Then(ThenRefuseTheChangedEditableGraphWithoutWrites, "refuse the changed editable graph without writes")
            .BDDfy();

        async Task GivenAnExtraDesignTimeCompileItem()
        {
            fixture.Write(compileItem == "Extra.cs" ? "A/Extra.cs" : "Shared.cs", "public class Extra { public Demo.Service Value = new(); }");
            fixture.AppendProject($"""
                <ItemGroup><Compile Remove="{compileItem}" /><Compile Include="{compileItem}" Condition="'$(DesignTimeBuild)' == 'true'" /></ItemGroup>
                """);
            await fixture.Restore();
            original = fixture.Snapshot();
        }

        async Task WhenPreviewingRename() => previewingRenameResult = await fixture.Preview(fixture.Rename with { Symbol = "T:Demo.Service", NewName = "Renamed" });

        void ThenRefuseTheChangedEditableGraphWithoutWrites()
        {
            fixture.RefusedPreview(previewingRenameResult, expectedCode);
            fixture.AssertSnapshot(original);
        }
    }

    [RefactorSdkTheory]
    [InlineData("""Condition="'$(DesignTimeBuild)' != 'true'" """, false)]
    [InlineData("""ReferenceOutputAssembly="false" """, true)]
    public void DesignTimeAndBuildOnlyReferencesHaveDifferentMeaning(string attribute, bool buildOnly)
    {
        using var fixture = new SdkFixture(twoProjects: true);
        string project = null!;
        Dictionary<string, byte[]> original = null!;
        CommandResult result = null!;

        this.Given(GivenAConditionalProjectReference, "a conditional project reference")
            .When(WhenPreviewingRename, "previewing rename")
            .Then(ThenRespectTheReferenceGraphForTheSelectedCondition, "respect the reference graph for the selected condition")
            .BDDfy();

        async Task GivenAConditionalProjectReference()
        {
            if (buildOnly) fixture.Write("B/Use.cs", "public class Use {}");
            project = fixture.PathFor("B/B.csproj");
            fixture.Write("B/B.csproj", File.ReadAllText(project).Replace("<ProjectReference ", $"<ProjectReference {attribute}"));
            await fixture.Restore();
            original = fixture.Snapshot();
        }

        async Task WhenPreviewingRename()
        {
            result = await fixture.Preview();
        }

        void ThenRespectTheReferenceGraphForTheSelectedCondition()
        {
            if (buildOnly)
            {
                result.Previewed();
                Assert.Empty(Assert.Single(fixture.Plan().Projects, p => p.Path == project).References);
            }
            else fixture.RefusedPreview(result, "incomplete_references");
            fixture.AssertSnapshot(original);
        }
    }

    [RefactorSdkFact]
    public void ConfigurationCannotInjectAnMsbuildProperty()
    {
        using var fixture = GivenASdkProjectAndAPropertyInjectionRequest();
        CommandResult previewingWithInjectedConfigurationResult = null!;

        this.Given("a sdk project and a property injection request")
            .When(WhenPreviewingWithInjectedConfiguration, "previewing with injected configuration")
            .Then(ThenRefuseTheConfiguration, "refuse the configuration")
            .BDDfy();

        SdkFixture GivenASdkProjectAndAPropertyInjectionRequest() => new SdkFixture();

        async Task WhenPreviewingWithInjectedConfiguration() => previewingWithInjectedConfigurationResult = await fixture.Preview(fixture.Rename with { Configuration = "Debug,DefineConstants=OTHER" });

        void ThenRefuseTheConfiguration() => fixture.RefusedPreview(previewingWithInjectedConfigurationResult, "invalid_configuration");
    }

    [RefactorSdkFact]
    public void MalformedSourceEncodingIsRefusedWithoutWrites()
    {
        using var fixture = new SdkFixture();
        Dictionary<string, byte[]> original = null!;
        CommandResult previewingRenameResult = null!;

        this.Given(GivenMalformedSourceBytes, "malformed source bytes")
            .When(WhenPreviewingRename, "previewing rename")
            .Then(ThenRefuseTheLossyEncodingWithoutWrites, "refuse the lossy encoding without writes")
            .BDDfy();

        async Task GivenMalformedSourceBytes()
        {
            byte[] bytes = [0xef, 0xbb, 0xbf, .. File.ReadAllBytes(fixture.Source), .. "// malformed "u8, 0xff, 0x0a];
            fixture.Write("A/Service.cs", bytes);
            await fixture.Restore();
            original = fixture.Snapshot();
        }

        async Task WhenPreviewingRename() => previewingRenameResult = await fixture.Preview();

        void ThenRefuseTheLossyEncodingWithoutWrites()
        {
            fixture.RefusedPreview(previewingRenameResult, "lossy_encoding");
            fixture.AssertSnapshot(original);
        }
    }

    [RefactorSdkFact]
    public void PreviewJsonReportsBaselineErrorsSeparatelyFromNewErrors()
    {
        using var fixture = new SdkFixture(twoProjects: true);
        string broken = null!;
        Dictionary<string, byte[]> original = null!;
        CommandResult result = null!;

        this.Given(GivenAConsumerWithABaselineError, "a consumer with a baseline error")
            .When(WhenPreviewingRename, "previewing rename")
            .Then(ThenReportTheExistingErrorWithoutNewErrorsOrWrites, "report the existing error without new errors or writes")
            .BDDfy();

        async Task GivenAConsumerWithABaselineError()
        {
            broken = fixture.Write("B/Broken.cs", "class Broken { MissingType field; }");
            await fixture.Restore();
            original = fixture.Snapshot();
        }

        async Task WhenPreviewingRename()
        {
            result = await fixture.Preview();
        }

        void ThenReportTheExistingErrorWithoutNewErrorsOrWrites()
        {
            result.Previewed();
            var baseline = Assert.Single(result.Json.GetProperty("baselineErrors").EnumerateArray());
            Assert.Equal("CS0246", baseline.GetProperty("id").GetString());
            Assert.Equal(broken, baseline.GetProperty("file").GetString(), ignoreCase: true);
            Assert.Empty(result.Json.GetProperty("newErrors").EnumerateArray());
            fixture.AssertSnapshot(original);
        }
    }
}
