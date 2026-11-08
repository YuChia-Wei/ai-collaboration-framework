using System.Reflection;
using System.Reflection.Metadata;
using System.Reflection.PortableExecutable;
using System.Security;
using Microsoft.CodeAnalysis;

namespace RefactorTool.IntegrationTests;

[Trait("Boundary", "Sdk")]
[Collection(SdkCollection.Name)]
public sealed class GeneratorIntegrationTests
{
    /// <summary>Rejects extraction with SDK generator output while allowing an unrelated cross-project rename to build.</summary>
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

        void ThenPreviewingAnUnrelatedRenameSucceeds()
        {
            previewingAnUnrelatedRenameResult.Previewed();
            fixture.AssertSnapshot(original);
            var plan = fixture.Plan();
            Assert.Equal(2, plan.Projects.Length);
            Assert.Equal("Enable", Assert.Single(plan.Projects, project => project.Path == fixture.Project).Nullable);
            Assert.NotEmpty(plan.Patch);
            Assert.Contains("M:Demo.IService.Get(System.Int32)", plan.RelatedSymbols);
            Assert.Contains("M:Demo.Derived.Get(System.Int32)", plan.RelatedSymbols);
        }

        async Task WhenApplyingTheUnrelatedRename() => applyingTheUnrelatedRenameResult = await fixture.Apply();

        void ThenChangeTheAuthoredReferences()
        {
            applyingTheUnrelatedRenameResult.Applied();
            var source = File.ReadAllText(fixture.Source);
            var consumer = File.ReadAllText(fixture.Consumer);
            Assert.Contains("interface IService { int Fetch(int value); }", source);
            Assert.Contains("override int Fetch(int value) => base.Fetch(value)", source);
            Assert.Contains("public int Get(string value)", source);
            Assert.Contains("class Other { public int Get(int value)", source);
            Assert.Contains("service.Fetch(2)", consumer);
            Assert.Contains("new Other().Get(4)", consumer);
            Assert.Contains("cref=\"Service.Fetch(int)\"", consumer);
            Assert.Contains("nameof(IService.Fetch)", consumer);
            Assert.Contains("\"Get Service\"", consumer);
            Assert.Contains("// Get Service", consumer);
            Assert.Equal(source.Count(c => c == '\n'), source.Split("\r\n").Length - 1);
        }

        async Task WhenBuildingTheEditedWorkspace() => await fixture.Dotnet("build", fixture.Workspace, "--no-restore", "--nologo");

        void ThenTheEditedWorkspaceBuilds() => Assert.True(File.Exists(fixture.PathFor("B/bin/Debug/net10.0/B.dll")));
    }

    /// <summary>Rejects a rename that would edit a source-generated reference or declaration.</summary>
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

    /// <summary>Refuses extraction when an evaluated analyzer requires a newer Roslyn API.</summary>
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
            var sdkRoslynPath = Path.Combine(fixture.SdkPath, "Roslyn/bincore/Microsoft.CodeAnalysis.dll");
            var sdkRoslyn = AssemblyName.GetAssemblyName(sdkRoslynPath);
            Assert.True(sdkRoslyn.Version > typeof(Compilation).Assembly.GetName().Version);
            assembly = fixture.Write("Generator/Generator.dll",
                SemanticWorkspace.EmitGenerator(EngineBoundaryTests.GeneratorSource("emit-after"), sdkRoslynPath));
            using (var stream = File.OpenRead(assembly))
            using (var pe = new PEReader(stream))
            {
                var metadata = pe.GetMetadataReader();
                var reference = Assert.Single(metadata.AssemblyReferences.Select(metadata.GetAssemblyReference),
                    reference => metadata.GetString(reference.Name) == "Microsoft.CodeAnalysis");
                Assert.Equal(sdkRoslyn.Version, reference.Version);
            }
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
