using System.Reflection;
using System.Security;
using Microsoft.CodeAnalysis;

namespace RefactorTool.Tests;

[Trait("Boundary", "Sdk")]
[Collection(SdkCollection.Name)]
public sealed class GeneratorIntegrationTests
{
    [Fact]
    public async Task SdkGeneratorOutputBlocksExtractionButUnrelatedOutputAllowsRename()
    {
        using var fixture = new SdkFixture();
        fixture.Write("A/Json.cs", """
            using System.Text.Json.Serialization;
            [JsonSerializable(typeof(string))]
            internal partial class Context : JsonSerializerContext {}
            """);
        await fixture.Restore();
        var original = fixture.Snapshot();
        fixture.RefusedPreview(await fixture.Preview(fixture.Extract), "unsupported_generated_source");
        fixture.AssertSnapshot(original);
        (await fixture.Preview()).Previewed();
        (await fixture.Apply()).Applied();
        Assert.Contains("override int Fetch(int value) => base.Fetch(value)", File.ReadAllText(fixture.Source));
        await fixture.Dotnet("build", fixture.Project, "--no-restore", "--nologo");
    }

    [Theory]
    [InlineData("P:Demo.Service.Property", "Value", "uneditable_reference")]
    [InlineData("P:Context.Service", "ServiceInfo", "uneditable_symbol")]
    public async Task GeneratorReferenceAndDeclarationCannotBeEdited(string symbol, string name, string code)
    {
        using var fixture = new SdkFixture();
        fixture.Write("A/Json.cs", """
            using System.Text.Json.Serialization;
            [JsonSerializable(typeof(Demo.Service))]
            internal partial class Context : JsonSerializerContext {}
            """);
        await fixture.Restore();
        var original = fixture.Snapshot();
        var result = await fixture.Preview(fixture.Rename with { Symbol = symbol, NewName = name });
        fixture.RefusedPreview(result, code);
        Assert.Contains("source-generator output", result.Text("message"));
        fixture.AssertSnapshot(original);
    }

    [Theory]
    [InlineData("emit-after")]
    [InlineData("throw-after")]
    [InlineData("throw-before")]
    [InlineData("newer-api")]
    public async Task ExtractionRefusesActivatedFailingOrIncompatibleAnalyzer(string scenario)
    {
        using var fixture = new SdkFixture();
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
        var original = fixture.Snapshot();
        // Roslyn can retain a handle to a physical analyzer until process exit.
        // The project-reference apphost gives each analyzer an isolated lifetime.
        var tool = Path.Combine(AppContext.BaseDirectory, "RefactorTool.exe");
        Assert.True(File.Exists(tool), $"Missing project-reference executable: {tool}");
        var result = await fixture.Preview(fixture.Extract, artifact: tool);
        fixture.RefusedPreview(result, "unsupported_generated_source");
        if (scenario == "newer-api") Assert.Contains("newer Roslyn API", result.Text("message"));
        fixture.AssertSnapshot(original);
    }
}
