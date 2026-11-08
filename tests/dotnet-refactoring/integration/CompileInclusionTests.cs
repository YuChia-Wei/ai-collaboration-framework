using Microsoft.CodeAnalysis;

namespace RefactorTool.IntegrationTests;

[Trait("Boundary", "Sdk")]
[Collection(SdkCollection.Name)]
public sealed class CompileInclusionTests
{
    [RefactorSdkTheory]
    [InlineData("""<ItemGroup><Compile Remove="ISelected.cs" /></ItemGroup>""", "ISelected.cs")]
    [InlineData("""<PropertyGroup Condition="Exists('ISelected.cs')"><EnableDefaultCompileItems>false</EnableDefaultCompileItems></PropertyGroup>""", "ISelected.cs")]
    [InlineData("""<Import Project="ExcludeInterface.targets" Condition="Exists('ISelected.cs')" />""", "ISelected.cs")]
    [InlineData("""<ItemGroup><IgnoredFiles Include="ISelected*.cs"/><Compile Remove="@(IgnoredFiles)" /></ItemGroup>""", "ISelected.cs")]
    [InlineData("""<ItemGroup><Compile Remove="ISelected.cs" Condition="'@(Compile)' != ''" /></ItemGroup>""", "ISelected.cs")]
    [InlineData("""<Target Name="RemoveInterface" BeforeTargets="CoreCompile"><ItemGroup><Compile Remove="ISelected.cs" /></ItemGroup></Target>""", "ISelected.cs")]
    [InlineData("""<Import Project="Fake.nuget.g.targets" />""", "ISelected.cs")]
    [InlineData("""<Import Project="Contracts/*" />""", "Contracts/ISelected.cs")]
    [InlineData("""<PropertyGroup><ImportSpec>Contracts/*</ImportSpec></PropertyGroup><Import Project="$(ImportSpec)" />""", "Contracts/ISelected.cs")]
    [InlineData("""<PropertyGroup><CustomBeforeMicrosoftCommonTargets>$(MSBuildProjectDirectory)/Contracts/ISelected.cs</CustomBeforeMicrosoftCommonTargets></PropertyGroup>""", "Contracts/ISelected.cs")]
    [InlineData("""<PropertyGroup><DirectoryBuildTargetsPath>$(MSBuildProjectDirectory)/Contracts/ISelected.cs</DirectoryBuildTargetsPath></PropertyGroup>""", "Contracts/ISelected.cs")]
    [InlineData("""<PropertyGroup><_DirectoryBuildTargetsFile>ISelected.cs</_DirectoryBuildTargetsFile></PropertyGroup>""", "ISelected.cs")]
    public void RejectsRulesThatCanExcludeOrImportTheNewFile(string xml, string destination)
    {
        using var fixture = new SdkFixture();
        string output = null!;
        Dictionary<string, byte[]> original = null!;
        RefactorFailure failure = null!;

        this.Given(GivenAPotentiallyUnstableCompileRule, "a potentially unstable compile rule")
            .When(WhenCheckingWhetherTheNewFileWouldCompile, "checking whether the new file would compile")
            .Then(ThenRefuseWithoutCreatingTheFile, "refuse without creating the file")
            .BDDfy();

        void GivenAPotentiallyUnstableCompileRule()
        {
            fixture.Write("A/ExcludeInterface.targets", """<Project><ItemGroup><Compile Remove="ISelected.cs" /></ItemGroup></Project>""");
            fixture.Write("A/Fake.nuget.g.targets", """<Project><Target Name="RemoveInterface" BeforeTargets="CoreCompile"><ItemGroup><Compile Remove="ISelected.cs" /></ItemGroup></Target></Project>""");
            fixture.AppendProject(xml);
            output = fixture.PathFor("A/" + destination);
            Directory.CreateDirectory(Path.GetDirectoryName(output)!);
            original = fixture.Snapshot();
        }

        async Task WhenCheckingWhetherTheNewFileWouldCompile()
        {
            failure = await Assert.ThrowsAsync<RefactorFailure>(() => Require(fixture, output));
        }

        void ThenRefuseWithoutCreatingTheFile()
        {
            Assert.Equal("unsupported_compile_inclusion", failure.Code);
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

    private static async Task Require(SdkFixture fixture, string output)
    {
        var request = fixture.Extract with { OutputFile = output };
        await CompileInclusion.Register(request);
        using var loaded = new LoadedWorkspace(new AdhocWorkspace(), SdkFixture.Version);
        loaded.Projects.Add(new ProjectInfo(fixture.Project, "net10.0", "Debug", "Enable", "14.0", [], []));
        await CompileInclusion.Require(loaded, fixture.Project, output, request);
    }
}
