namespace RefactorTool.IntegrationTests;

[Trait("Boundary", "Sdk")]
[Collection(SdkCollection.Name)]
public sealed class CompileInclusionTests
{
    [RefactorSdkTheory]
    [InlineData("""<ItemGroup><Compile Remove="ISelected.cs" /></ItemGroup>""", "ISelected.cs")]
    [InlineData("""<Import Project="Fake.nuget.g.targets" />""", "ISelected.cs")]
    [InlineData("""<PropertyGroup><CustomBeforeMicrosoftCommonTargets>$(MSBuildProjectDirectory)/Contracts/ISelected.cs</CustomBeforeMicrosoftCommonTargets></PropertyGroup>""", "Contracts/ISelected.cs")]
    [InlineData("""<PropertyGroup><DirectoryBuildTargetsPath>$(MSBuildProjectDirectory)/Contracts/ISelected.cs</DirectoryBuildTargetsPath></PropertyGroup>""", "Contracts/ISelected.cs")]
    [InlineData("""<PropertyGroup><_DirectoryBuildTargetsFile>ISelected.cs</_DirectoryBuildTargetsFile></PropertyGroup>""", "ISelected.cs")]
    public void RejectsRulesThatCanExcludeOrImportTheNewFile(string xml, string destination)
    {
        using var fixture = new SdkFixture();
        string output = null!;
        Dictionary<string, byte[]> original = null!;
        CommandResult result = null!;

        this.Given(GivenAPotentiallyUnstableCompileRule, "a potentially unstable compile rule")
            .When(WhenCheckingWhetherTheNewFileWouldCompile, "checking whether the new file would compile")
            .Then(ThenRefuseWithoutCreatingTheFile, "refuse without creating the file")
            .BDDfy();

        async Task GivenAPotentiallyUnstableCompileRule()
        {
            fixture.Write("A/Fake.nuget.g.targets", """<Project><Target Name="RemoveInterface" BeforeTargets="CoreCompile"><ItemGroup><Compile Remove="ISelected.cs" /></ItemGroup></Target></Project>""");
            fixture.AppendProject(xml);
            output = fixture.PathFor("A/" + destination);
            Directory.CreateDirectory(Path.GetDirectoryName(output)!);
            await fixture.Restore();
            original = fixture.Snapshot();
        }

        async Task WhenCheckingWhetherTheNewFileWouldCompile()
        {
            result = await fixture.Preview(fixture.Extract with { OutputFile = output });
        }

        void ThenRefuseWithoutCreatingTheFile()
        {
            fixture.RefusedPreview(result, "unsupported_compile_inclusion");
            Assert.False(File.Exists(output));
            fixture.AssertSnapshot(original);
        }
    }

    [RefactorSdkFact]
    public void OtherProjectLowercaseCompileGlobCanAlsoIncludeTheOutput()
    {
        using var fixture = new SdkFixture(twoProjects: true);
        string output = null!;
        Dictionary<string, byte[]> original = null!;
        CommandResult result = null!;

        this.Given(GivenASecondProjectThatCanCompileTheNewFile, "a second project that can compile the new file")
            .When(WhenPreviewingExtraction, "previewing extraction")
            .Then(ThenRefuseWithoutWrites, "refuse without writes")
            .BDDfy();

        async Task GivenASecondProjectThatCanCompileTheNewFile()
        {
            fixture.AppendProject("""<ItemGroup><compile Include="../A/Contracts/**/*.cs" /></ItemGroup>""", "B/B.csproj");
            output = fixture.PathFor("A/Contracts/ISelected.cs");
            Directory.CreateDirectory(Path.GetDirectoryName(output)!);
            await fixture.Restore();
            original = fixture.Snapshot();
        }

        async Task WhenPreviewingExtraction()
        {
            result = await fixture.Preview(fixture.Extract with { OutputFile = output });
        }

        void ThenRefuseWithoutWrites()
        {
            fixture.RefusedPreview(result, "unsupported_compile_inclusion");
            Assert.False(File.Exists(output));
            fixture.AssertSnapshot(original);
        }
    }

    [RefactorSdkFact]
    public void StableImportAllowsPreviewButExplicitCompileExclusionRefuses()
    {
        using var stable = new SdkFixture();
        using var excluded = new SdkFixture();
        Dictionary<string, byte[]> original = null!;
        CommandResult previewingExtractionWithTheStableImportResult = null!;
        Dictionary<string, byte[]> excludedOriginal = null!;
        CommandResult previewingExtractionWithTheExclusionResult = null!;

        this.Given(GivenAProjectWithAStableImport, "a project with a stable import")
            .When(WhenPreviewingExtractionWithTheStableImport, "previewing extraction with the stable import")
            .Then(ThenPreviewWithoutChangingAuthoredSource, "preview without changing authored source")
            .Given(GivenAProjectThatExplicitlyExcludesTheOutput, "a project that explicitly excludes the output")
            .When(WhenPreviewingExtractionWithTheExclusion, "previewing extraction with the exclusion")
            .Then(ThenRefuseWithoutChangingAuthoredSource, "refuse without changing authored source")
            .BDDfy();

        async Task GivenAProjectWithAStableImport()
        {
            stable.Write("A/Bound.props", "<Project><PropertyGroup><Nullable>enable</Nullable></PropertyGroup></Project>");
            stable.AppendProject("""<Import Project="Bound.props" />""");
            await stable.Restore();
            original = stable.Snapshot();
        }

        async Task WhenPreviewingExtractionWithTheStableImport() => previewingExtractionWithTheStableImportResult = await stable.Preview(stable.Extract);

        void ThenPreviewWithoutChangingAuthoredSource()
        {
            previewingExtractionWithTheStableImportResult.Previewed();
            stable.AssertSnapshot(original);
        }

        async Task GivenAProjectThatExplicitlyExcludesTheOutput()
        {
            excluded.AppendProject("""<ItemGroup><Compile Remove="ISelected.cs" /></ItemGroup>""");
            await excluded.Restore();
            excludedOriginal = excluded.Snapshot();
        }

        async Task WhenPreviewingExtractionWithTheExclusion() => previewingExtractionWithTheExclusionResult = await excluded.Preview(excluded.Extract);

        void ThenRefuseWithoutChangingAuthoredSource()
        {
            excluded.RefusedPreview(previewingExtractionWithTheExclusionResult, "unsupported_compile_inclusion");
            excluded.AssertSnapshot(excludedOriginal);
        }
    }
}
