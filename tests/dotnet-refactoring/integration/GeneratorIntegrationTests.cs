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

    [RefactorSdkTheory]
    [InlineData("emit-after")]
    [InlineData("throw-after")]
    [InlineData("throw-before")]
    [InlineData("newer-api")]
    public void ExtractionRefusesActivatedFailingOrIncompatibleAnalyzer(string scenario)
    {
        using var fixture = new SdkFixture();
        Dictionary<string, byte[]> original = null!;
        CommandResult result = null!;

        this.Given(GivenTheSelectedFailingOrIncompatibleGenerator, "the selected failing or incompatible generator")
            .When(WhenPreviewingExtraction, "previewing extraction")
            .Then(ThenRefuseTheUnsupportedGeneratorWithoutWrites, "refuse the unsupported generator without writes")
            .BDDfy();

        async Task GivenTheSelectedFailingOrIncompatibleGenerator()
        {
            var name = "Generator" + scenario.Replace("-", "");
            var condition = scenario == "throw-before" ? "true" : """context.Compilation.GetTypeByMetadataName("Contracts.ISelected") != null""";
            var body = scenario.StartsWith("throw-", StringComparison.Ordinal)
                ? """throw new System.InvalidOperationException("conditional generator failure");"""
                : """context.AddSource("Activated.cs", "namespace Generated { internal class Activated {} }");""";
            var currentRoslyn = typeof(Compilation).Assembly;
            var reference = scenario == "newer-api"
                ? "$(MSBuildToolsPath)/Roslyn/bincore/Microsoft.CodeAnalysis.dll"
                : currentRoslyn.Location;
            if (scenario == "newer-api")
            {
                var info = await fixture.Dotnet("--info");
                var sdk = info.Split('\n').Single(line => line.TrimStart().StartsWith("Base Path:", StringComparison.Ordinal)).Split(':', 2)[1].Trim();
                var sdkRoslyn = AssemblyName.GetAssemblyName(Path.Combine(sdk, "Roslyn/bincore/Microsoft.CodeAnalysis.dll"));
                Assert.True(sdkRoslyn.Version > currentRoslyn.GetName().Version);
            }
            var project = fixture.Write($"Generator/{name}.csproj", $"""
                <Project Sdk="Microsoft.NET.Sdk"><PropertyGroup><TargetFramework>net10.0</TargetFramework></PropertyGroup>
                <ItemGroup><Reference Include="Microsoft.CodeAnalysis" HintPath="{SecurityElement.Escape(reference)}" Private="false" /></ItemGroup></Project>
                """);
            fixture.Write("Generator/Generator.cs", $$"""
                using Microsoft.CodeAnalysis;
                [Generator] public class ConditionalGenerator : ISourceGenerator
                {
                    public void Initialize(GeneratorInitializationContext context) {}
                    public void Execute(GeneratorExecutionContext context)
                    {
                        if ({{condition}}) { {{body}} }
                    }
                }
                """);
            await fixture.Dotnet("build", project, "--source", fixture.Root, "-p:NuGetAudit=false", "--nologo");
            var assembly = fixture.PathFor($"Generator/bin/Debug/net10.0/{name}.dll");
            Assert.True(File.Exists(assembly));
            fixture.AppendProject($"""<ItemGroup><Analyzer Include="{SecurityElement.Escape(assembly)}" /></ItemGroup>""");
            await fixture.Restore();
            original = fixture.Snapshot();
        }

        async Task WhenPreviewingExtraction()
        {
            result = await fixture.Preview(fixture.Extract);
        }

        void ThenRefuseTheUnsupportedGeneratorWithoutWrites()
        {
            fixture.RefusedPreview(result, "unsupported_generated_source");
            if (scenario == "newer-api") Assert.Contains("newer Roslyn API", result.Text("message"));
            fixture.AssertSnapshot(original);
        }
    }
}
