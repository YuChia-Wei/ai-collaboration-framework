namespace RefactorTool.IntegrationTests;

[Trait("Boundary", "Sdk")]
[Collection(SdkCollection.Name)]
public sealed class CompileInclusionTests
{
    /// <summary>Rejects compile exclusions and unstable imports that invalidate the proposed output.</summary>
    [RefactorSdkTheory]
    [InlineData("""<ItemGroup><Compile Remove="ISelected.cs" /></ItemGroup><Import Project="Bound.props" />""", "ISelected.cs")]
    [InlineData("""<Import Project="Fake.nuget.g.targets" />""", "ISelected.cs")]
    [InlineData("""<PropertyGroup><CustomBeforeMicrosoftCommonTargets>$(MSBuildProjectDirectory)/Contracts/ISelected.cs</CustomBeforeMicrosoftCommonTargets></PropertyGroup>""", "Contracts/ISelected.cs")]
    [InlineData("""<PropertyGroup><DirectoryBuildTargetsPath>$(MSBuildProjectDirectory)/Contracts/ISelected.cs</DirectoryBuildTargetsPath></PropertyGroup>""", "Contracts/ISelected.cs")]
    [InlineData("""<PropertyGroup><_DirectoryBuildTargetsFile>ISelected.cs</_DirectoryBuildTargetsFile></PropertyGroup>""", "ISelected.cs")]
    public void RejectsRulesThatCanExcludeOrImportTheNewFile(string xml, string destination)
    {
        using var fixture = new SdkFixture();
        string output = null!;
        Dictionary<string, byte[]> original = null!;
        CommandResult? result = null;
        Exception? failure = null;
        bool direct = false;

        this.Given(GivenAPotentiallyUnstableCompileRule, "a potentially unstable compile rule")
            .When(WhenCheckingWhetherTheNewFileWouldCompile, "checking whether the new file would compile")
            .Then(ThenRefuseWithoutCreatingTheFile, "refuse without creating the file")
            .BDDfy();

        async Task GivenAPotentiallyUnstableCompileRule()
        {
            fixture.Write("A/Fake.nuget.g.targets", """<Project><Target Name="RemoveInterface" BeforeTargets="CoreCompile"><ItemGroup><Compile Remove="ISelected.cs" /></ItemGroup></Target></Project>""");
            fixture.Write("A/Bound.props", "<Project><PropertyGroup><Nullable>enable</Nullable></PropertyGroup></Project>");
            fixture.AppendProject(xml);
            output = fixture.PathFor("A/" + destination);
            Directory.CreateDirectory(Path.GetDirectoryName(output)!);
            direct = CompilePolicyTests.MsBuildParser.CanEvaluate(fixture.SdkPath);
            if (!direct)
                await fixture.Restore();
            original = fixture.Snapshot();
        }

        async Task WhenCheckingWhetherTheNewFileWouldCompile()
        {
            var request = fixture.Extract with { OutputFile = output };
            if (!direct)
            {
                result = await fixture.Preview(request);
                return;
            }

            await CompileInclusion.Register(request);
            using var loaded = new LoadedWorkspace(new Microsoft.CodeAnalysis.AdhocWorkspace(), SdkFixture.Version);
            loaded.Projects.Add(new ProjectInfo(fixture.Project, "net10.0", request.Configuration, "Enable", "14.0", [], []));
            failure = await Record.ExceptionAsync(
                () => CompileInclusion.Require(loaded, fixture.Project, output, request));
        }

        void ThenRefuseWithoutCreatingTheFile()
        {
            if (direct)
                Assert.Equal("unsupported_compile_inclusion", Assert.IsType<RefactorFailure>(failure).Code);
            else
                fixture.RefusedPreview(result!, "unsupported_compile_inclusion");
            Assert.False(File.Exists(output));
            fixture.AssertSnapshot(original);
        }
    }

    /// <summary>Rejects an output that a second project's lowercase compile glob could include.</summary>
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

    /// <summary>Captures a stable import and allows a nonmatching literal Compile exclusion without changing source.</summary>
    [RefactorSdkFact]
    public void StableImportAllowsPreviewAndIsCaptured()
    {
        using var fixture = new SdkFixture();
        Dictionary<string, byte[]> original = null!;
        CommandResult result = null!;

        this.Given(GivenAStableImport, "a stable import and a nonmatching literal Compile exclusion")
            .When(WhenPreviewingExtraction, "previewing extraction")
            .Then(ThenPreviewAndCaptureTheImportWithoutWritingSource, "preview and capture the import without writing source")
            .BDDfy();

        async Task GivenAStableImport()
        {
            fixture.Write("A/Bound.props", "<Project><PropertyGroup><Nullable>enable</Nullable></PropertyGroup></Project>");
            fixture.AppendProject("""<Import Project="Bound.props" /><ItemGroup><Compile Remove="Excluded.cs" /></ItemGroup>""");
            await fixture.Restore();
            original = fixture.Snapshot();
        }

        async Task WhenPreviewingExtraction() => result = await fixture.Preview(fixture.Extract);

        void ThenPreviewAndCaptureTheImportWithoutWritingSource()
        {
            result.Previewed();
            Assert.Contains(fixture.Plan().Inputs, input =>
                string.Equals(input.Path, fixture.PathFor("A/Bound.props"), StringComparison.OrdinalIgnoreCase));
            fixture.AssertSnapshot(original);
        }
    }
}
