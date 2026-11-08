using System.Reflection;
using System.Security;
using Microsoft.CodeAnalysis;

namespace RefactorTool.IntegrationTests;

[Trait("Boundary", "Sdk")]
[Collection(SdkCollection.Name)]
public sealed class GeneratorIntegrationTests
{
    [RefactorSdkFact]
    public void SdkGeneratorOutputBlocksExtractionButUnrelatedOutputAllowsRename()
    {
        using var fixture = new SdkFixture(twoProjects: true);
        Dictionary<string, byte[]> original = null!;
        CommandResult previewingExtractionResult = null!;
        CommandResult previewingAnUnrelatedRenameResult = null!;
        CommandResult applyingTheUnrelatedRenameResult = null!;

        this.Given(GivenARestoredWorkspaceWithGeneratedOutput, "a restored workspace with generated output")
            .When(WhenPreviewingExtraction, "previewing extraction")
            .Then(ThenRefuseWithoutSourceChanges, "refuse without source changes")
            .When(WhenPreviewingAnUnrelatedRename, "previewing an unrelated rename")
            .Then(ThenPreviewingAnUnrelatedRenameSucceeds, "previewing an unrelated rename succeeds")
            .When(WhenApplyingTheUnrelatedRename, "applying the unrelated rename")
            .Then(ThenChangeTheAuthoredReferences, "change the authored references")
            .When(WhenBuildingTheEditedWorkspace, "building the edited workspace")
            .Then(ThenTheEditedWorkspaceBuilds, "the edited workspace builds")
            .BDDfy();

        async Task GivenARestoredWorkspaceWithGeneratedOutput()
        {
            fixture.Write("A/Json.cs", """
                using System.Text.Json.Serialization;
                [JsonSerializable(typeof(string))]
                internal partial class Context : JsonSerializerContext {}
                """);
            await fixture.Restore();
            original = fixture.Snapshot();
        }

        async Task WhenPreviewingExtraction() => previewingExtractionResult = await fixture.Preview(fixture.Extract);

        void ThenRefuseWithoutSourceChanges()
        {
            fixture.RefusedPreview(previewingExtractionResult, "unsupported_generated_source");
            fixture.AssertSnapshot(original);
        }

        async Task WhenPreviewingAnUnrelatedRename() => previewingAnUnrelatedRenameResult = await fixture.Preview();

        void ThenPreviewingAnUnrelatedRenameSucceeds() => previewingAnUnrelatedRenameResult.Previewed();

        async Task WhenApplyingTheUnrelatedRename() => applyingTheUnrelatedRenameResult = await fixture.Apply();

        void ThenChangeTheAuthoredReferences()
        {
            applyingTheUnrelatedRenameResult.Applied();
            Assert.Contains("override int Fetch(int value) => base.Fetch(value)", File.ReadAllText(fixture.Source));
            Assert.Contains("service.Fetch(2)", File.ReadAllText(fixture.Consumer));
        }

        async Task WhenBuildingTheEditedWorkspace() => await fixture.Dotnet("build", fixture.Workspace, "--no-restore", "--nologo");

        void ThenTheEditedWorkspaceBuilds() => Assert.True(File.Exists(fixture.PathFor("B/bin/Debug/net10.0/B.dll")));
    }

    [RefactorSdkTheory]
    [InlineData("P:Demo.Service.Property", "Value", "uneditable_reference")]
    [InlineData("P:Context.Service", "ServiceInfo", "uneditable_symbol")]
    public void GeneratorReferenceAndDeclarationCannotBeEdited(string symbol, string name, string code)
    {
        using var fixture = new SdkFixture();
        Dictionary<string, byte[]> original = null!;
        CommandResult result = null!;

        this.Given(GivenASourceGeneratorAndARenameTouchingItsOutput, "a source generator and a rename touching its output")
            .When(WhenPreviewingRename, "previewing rename")
            .Then(ThenRefuseTheGeneratedEditWithoutWrites, "refuse the generated edit without writes")
            .BDDfy();

        async Task GivenASourceGeneratorAndARenameTouchingItsOutput()
        {
            fixture.Write("A/Json.cs", """
                using System.Text.Json.Serialization;
                [JsonSerializable(typeof(Demo.Service))]
                internal partial class Context : JsonSerializerContext {}
                """);
            await fixture.Restore();
            original = fixture.Snapshot();
        }

        async Task WhenPreviewingRename()
        {
            result = await fixture.Preview(fixture.Rename with { Symbol = symbol, NewName = name });
        }

        void ThenRefuseTheGeneratedEditWithoutWrites()
        {
            fixture.RefusedPreview(result, code);
            Assert.Contains("source-generator output", result.Text("message"));
            fixture.AssertSnapshot(original);
        }
    }

    [RefactorSdkFact]
    public void ExtractionRefusesAnalyzerBuiltAgainstNewerSdkRoslyn()
    {
        using var fixture = new SdkFixture();
        string assembly = null!;
        Dictionary<string, byte[]> original = null!;
        CommandResult result = null!;

        this.Given(GivenAnAnalyzerBuiltAgainstTheNewerSdkRoslyn, "an analyzer built against the newer SDK Roslyn")
            .When(WhenPreviewingExtraction, "previewing extraction")
            .Then(ThenRefuseTheIncompatibleAnalyzerWithoutWrites, "refuse the incompatible analyzer without writes")
            .BDDfy();

        async Task GivenAnAnalyzerBuiltAgainstTheNewerSdkRoslyn()
        {
            var info = await fixture.Dotnet("--info");
            var sdk = info.Split('\n').Single(line => line.TrimStart().StartsWith("Base Path:", StringComparison.Ordinal)).Split(':', 2)[1].Trim();
            var sdkRoslyn = AssemblyName.GetAssemblyName(Path.Combine(sdk, "Roslyn/bincore/Microsoft.CodeAnalysis.dll"));
            Assert.True(sdkRoslyn.Version > typeof(Compilation).Assembly.GetName().Version);
            var project = fixture.Write("Generator/Generator.csproj", """
                <Project Sdk="Microsoft.NET.Sdk"><PropertyGroup><TargetFramework>net10.0</TargetFramework></PropertyGroup>
                <ItemGroup><Reference Include="Microsoft.CodeAnalysis" HintPath="$(MSBuildToolsPath)/Roslyn/bincore/Microsoft.CodeAnalysis.dll" Private="false" /></ItemGroup></Project>
                """);
            fixture.Write("Generator/Generator.cs", EngineBoundaryTests.GeneratorSource("emit-after"));
            await fixture.Dotnet("build", project, "--source", fixture.Root, "-p:NuGetAudit=false", "--nologo");
            assembly = fixture.PathFor("Generator/bin/Debug/net10.0/Generator.dll");
            Assert.True(File.Exists(assembly));
            fixture.AppendProject($"""<ItemGroup><Analyzer Include="{SecurityElement.Escape(assembly)}" /></ItemGroup>""");
            await fixture.Restore();
            original = fixture.Snapshot();
        }

        async Task WhenPreviewingExtraction() => result = await fixture.Preview(fixture.Extract);

        void ThenRefuseTheIncompatibleAnalyzerWithoutWrites()
        {
            fixture.RefusedPreview(result, "unsupported_generated_source");
            Assert.Contains("newer Roslyn API", result.Text("message"));
            Assert.Contains(assembly, result.Text("message"), StringComparison.OrdinalIgnoreCase);
            fixture.AssertSnapshot(original);
        }
    }
}
