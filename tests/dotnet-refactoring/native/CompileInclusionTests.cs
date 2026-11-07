using Microsoft.CodeAnalysis;

namespace RefactorTool.Tests;

[Trait("Boundary", "Sdk")]
[Collection(SdkCollection.Name)]
public sealed class CompileInclusionTests
{
    [Theory]
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
    public async Task RejectsRulesThatCanExcludeOrImportTheNewFile(string xml, string destination)
    {
        using var fixture = new SdkFixture();
        fixture.Write("A/ExcludeInterface.targets", """<Project><ItemGroup><Compile Remove="ISelected.cs" /></ItemGroup></Project>""");
        fixture.Write("A/Fake.nuget.g.targets", """<Project><Target Name="RemoveInterface" BeforeTargets="CoreCompile"><ItemGroup><Compile Remove="ISelected.cs" /></ItemGroup></Target></Project>""");
        fixture.AppendProject(xml);
        var output = fixture.PathFor("A/" + destination);
        Directory.CreateDirectory(Path.GetDirectoryName(output)!);
        var original = fixture.Snapshot();
        var failure = await Assert.ThrowsAsync<RefactorFailure>(() => Require(fixture, output));
        Assert.Equal("unsupported_compile_inclusion", failure.Code);
        Assert.False(File.Exists(output));
        fixture.AssertSnapshot(original);
    }

    [Fact]
    public async Task OtherProjectLowercaseCompileGlobCanAlsoIncludeTheOutput()
    {
        using var fixture = new SdkFixture(twoProjects: true);
        fixture.AppendProject("""<ItemGroup><compile Include="../A/Contracts/**/*.cs" /></ItemGroup>""", "B/B.csproj");
        var output = fixture.PathFor("A/Contracts/ISelected.cs");
        Directory.CreateDirectory(Path.GetDirectoryName(output)!);
        await fixture.Restore();
        var original = fixture.Snapshot();
        var result = await fixture.Preview(fixture.Extract with { OutputFile = output });
        fixture.RefusedPreview(result, "unsupported_compile_inclusion");
        Assert.False(File.Exists(output));
        fixture.AssertSnapshot(original);
    }

    [Fact]
    public async Task StableImportAllowsPreviewButExplicitCompileExclusionRefuses()
    {
        using (var stable = new SdkFixture())
        {
            stable.Write("A/Bound.props", "<Project><PropertyGroup><Nullable>enable</Nullable></PropertyGroup></Project>");
            stable.AppendProject("""<Import Project="Bound.props" />""");
            await stable.Restore();
            var original = stable.Snapshot();
            (await stable.Preview(stable.Extract)).Previewed();
            stable.AssertSnapshot(original);
        }
        using var excluded = new SdkFixture();
        excluded.AppendProject("""<ItemGroup><Compile Remove="ISelected.cs" /></ItemGroup>""");
        await excluded.Restore();
        var excludedOriginal = excluded.Snapshot();
        excluded.RefusedPreview(await excluded.Preview(excluded.Extract), "unsupported_compile_inclusion");
        excluded.AssertSnapshot(excludedOriginal);
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
