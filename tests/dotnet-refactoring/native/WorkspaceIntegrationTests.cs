namespace RefactorTool.Tests;

[Trait("Boundary", "Sdk")]
[Collection(SdkCollection.Name)]
public sealed class WorkspaceIntegrationTests
{
    [Fact]
    public async Task ExplicitFrameworkDoesNotAdmitMultiTargetProject()
    {
        using var fixture = new SdkFixture();
        fixture.Write("A/A.csproj", File.ReadAllText(fixture.Project).Replace(
            "<TargetFramework>net10.0</TargetFramework>", "<TargetFrameworks>net10.0;net9.0</TargetFrameworks>"));
        fixture.RefusedPreview(await fixture.Preview(fixture.Rename with { Framework = "net10.0" }), "multiple_frameworks");
    }

    [Fact]
    public async Task ExplicitLinkedCompileItemIsRejected()
    {
        using var fixture = new SdkFixture();
        fixture.Write("Linked.cs", "class Linked {}");
        fixture.AppendProject("""<ItemGroup><Compile Include="../Linked.cs" Link="Linked.cs" /></ItemGroup>""");
        await fixture.Restore();
        var original = fixture.Snapshot();
        fixture.RefusedPreview(await fixture.Preview(), "linked_file");
        fixture.AssertSnapshot(original);
    }

    [Theory]
    [InlineData(false)]
    [InlineData(true)]
    public async Task MissingProjectIsIdentifiedWhetherInSolutionOrReference(bool reference)
    {
        using var fixture = new SdkFixture();
        var request = fixture.Rename;
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
        var original = fixture.Snapshot();
        var result = await fixture.Preview(request);
        fixture.RefusedPreview(result, "missing_file");
        Assert.Contains("Missing.csproj", result.Text("message"));
        fixture.AssertSnapshot(original);
    }

    [Fact]
    public async Task MissingCompileInputIsIdentifiedBeforePlan()
    {
        using var fixture = new SdkFixture();
        fixture.AppendProject("""<ItemGroup><Compile Include="Missing.cs" /></ItemGroup>""");
        await fixture.Restore();
        var original = fixture.Snapshot();
        var result = await fixture.Preview();
        fixture.RefusedPreview(result, "missing_file");
        Assert.Contains("Missing.cs", result.Text("message"));
        fixture.AssertSnapshot(original);
    }

    [Fact]
    public async Task AuthoredGeneratedSuffixCannotBeEditedThroughRelatedRename()
    {
        using var fixture = new SdkFixture();
        fixture.Write("A/Generated.g.cs", "namespace Demo; class Generated : Service { public override int Get(int value) => base.Get(value); }");
        await fixture.Restore();
        var original = fixture.Snapshot();
        var result = await fixture.Preview();
        Assert.Contains(result.Text("code"), new[] { "uneditable_symbol", "uneditable_reference", "uneditable_source" });
        fixture.RefusedPreview(result, result.Text("code"));
        Assert.Contains(".g.cs suffix", result.Text("message"));
        Assert.Contains("Generated.g.cs", result.Text("message"));
        fixture.AssertSnapshot(original);
    }

    [Fact]
    public async Task ConditionalConfigurationAndImportedFrameworkAreReported()
    {
        using var fixture = new SdkFixture();
        fixture.Write("Directory.Build.props", """
            <Project><PropertyGroup><TargetFramework>net10.0</TargetFramework><DefineConstants>$(DefineConstants);CUSTOM</DefineConstants></PropertyGroup></Project>
            """);
        fixture.Write("A/A.csproj", File.ReadAllText(fixture.Project).Replace("<TargetFramework>net10.0</TargetFramework>", ""));
        fixture.Write("A/Conditional.cs", "#if DEBUG\nclass Active {}\n#else\nclass Inactive {}\n#endif\n");
        await fixture.Restore();
        (await fixture.Preview()).Previewed();
        var debug = fixture.Plan();
        Assert.Contains("DEBUG", Assert.Single(debug.Projects).Defines);
        Assert.Contains(debug.Limits, limit => limit.Contains("Inactive conditional"));
        (await fixture.Preview(fixture.Rename with { Configuration = "Release" })).Previewed();
        var release = Assert.Single(fixture.Plan().Projects);
        Assert.Equal("net10.0", release.Framework);
        Assert.Equal("Release", release.Configuration);
        Assert.Contains("CUSTOM", release.Defines);
        Assert.DoesNotContain("DEBUG", release.Defines);
    }

    [Fact]
    public async Task ExternalSdkIntermediatesAreCapturedWithoutBeingEdited()
    {
        using var fixture = new SdkFixture();
        fixture.Write("Directory.Build.props", """
            <Project><PropertyGroup><UseArtifactsOutput>true</UseArtifactsOutput><ArtifactsPath>$(MSBuildThisFileDirectory)artifacts</ArtifactsPath></PropertyGroup></Project>
            """);
        await fixture.Restore();
        (await fixture.Preview()).Previewed();
        var plan = fixture.Plan();
        Assert.Contains(plan.Inputs, input =>
            Path.GetRelativePath(fixture.PathFor("artifacts"), input.Path) is var relative &&
            !relative.StartsWith("..", StringComparison.Ordinal) && relative.EndsWith("AssemblyAttributes.cs", StringComparison.Ordinal));
        Assert.Equal(fixture.Source, Assert.Single(plan.Edits).Path);
        (await fixture.Apply()).Applied();
    }

    [Fact]
    public async Task BinAncestorOutsideProjectDoesNotMarkAuthoredSourceGenerated()
    {
        using var fixture = new SdkFixture();
        var project = fixture.Write("bin/A/A.csproj", File.ReadAllText(fixture.Project));
        var source = fixture.Write("bin/A/Service.cs", File.ReadAllBytes(fixture.Source));
        await fixture.Restore(project);
        (await fixture.Preview(fixture.Rename with { Workspace = project, Project = project, Symbol = "F:Demo.Service.Field", NewName = "Data" })).Previewed();
        Assert.Equal(source, Assert.Single(fixture.Plan().Edits).Path);
    }

    [Fact]
    public async Task VisualBasicSolutionMemberIsRejected()
    {
        using var fixture = new SdkFixture();
        fixture.Write("VisualBasic.vbproj", """<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup><TargetFramework>net10.0</TargetFramework></PropertyGroup></Project>""");
        var solution = fixture.Write("Mixed.slnx", """<Solution><Project Path="VisualBasic.vbproj" /><Project Path="A/A.csproj" /></Solution>""");
        fixture.RefusedPreview(await fixture.Preview(fixture.Rename with { Workspace = solution }), "unsupported_project");
    }

    [Fact]
    public async Task ClassicSolutionFolderAndProjectEntryKeepCompilationGraph()
    {
        using var fixture = new SdkFixture(twoProjects: true);
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
        foreach (var entry in new[] { solution, fixture.PathFor("B/B.csproj") })
        {
            (await fixture.Preview(fixture.Rename with { Workspace = entry })).Previewed();
            var plan = fixture.Plan();
            Assert.Equal(2, plan.Projects.Length);
            Assert.Contains("service.Fetch(2)", SemanticWorkspace.After(plan, fixture.Consumer));
        }
    }

    [Theory]
    [InlineData("../Shared.cs", "linked_file")]
    [InlineData("Extra.cs", "unexpected_source")]
    public async Task DesignTimeOnlySourceCannotSilentlyChangeTheEditableGraph(string compileItem, string expectedCode)
    {
        using var fixture = new SdkFixture();
        fixture.Write(compileItem == "Extra.cs" ? "A/Extra.cs" : "Shared.cs", "public class Extra { public Demo.Service Value = new(); }");
        fixture.AppendProject($"""
            <ItemGroup><Compile Remove="{compileItem}" /><Compile Include="{compileItem}" Condition="'$(DesignTimeBuild)' == 'true'" /></ItemGroup>
            """);
        await fixture.Restore();
        var original = fixture.Snapshot();
        fixture.RefusedPreview(await fixture.Preview(fixture.Rename with { Symbol = "T:Demo.Service", NewName = "Renamed" }), expectedCode);
        fixture.AssertSnapshot(original);
    }

    [Theory]
    [InlineData("""Condition="'$(DesignTimeBuild)' != 'true'" """, false)]
    [InlineData("""ReferenceOutputAssembly="false" """, true)]
    public async Task DesignTimeAndBuildOnlyReferencesHaveDifferentMeaning(string attribute, bool buildOnly)
    {
        using var fixture = new SdkFixture(twoProjects: true);
        if (buildOnly) fixture.Write("B/Use.cs", "public class Use {}");
        var project = fixture.PathFor("B/B.csproj");
        fixture.Write("B/B.csproj", File.ReadAllText(project).Replace("<ProjectReference ", $"<ProjectReference {attribute}"));
        await fixture.Restore();
        var original = fixture.Snapshot();
        var result = await fixture.Preview();
        if (buildOnly)
        {
            result.Previewed();
            Assert.Empty(Assert.Single(fixture.Plan().Projects, p => p.Path == project).References);
        }
        else fixture.RefusedPreview(result, "incomplete_references");
        fixture.AssertSnapshot(original);
    }

    [Fact]
    public async Task ConfigurationCannotInjectAnMsbuildProperty()
    {
        using var fixture = new SdkFixture();
        fixture.RefusedPreview(await fixture.Preview(fixture.Rename with { Configuration = "Debug,DefineConstants=OTHER" }), "invalid_configuration");
    }
}
