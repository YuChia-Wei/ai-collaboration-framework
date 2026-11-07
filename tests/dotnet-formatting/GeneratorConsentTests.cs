using System.Text.Json;
using System.Xml.Linq;
using static FormatTool.Tests.FormatFixture;

namespace FormatTool.Tests;

[Collection("FormatTool SDK")]
public sealed class GeneratorConsentTests
{
    [FormatSdkFact]
    public async Task GeneratorExecutesOnlyAfterConsentInBothDesignTimeContexts()
    {
        using var fixture = new FormatFixture();
        var marker = Path.Combine(fixture.Root, "generator-executed.txt");
        var generator = fixture.Write("Generator/Generator.csproj", """
            <Project Sdk="Microsoft.NET.Sdk">
              <PropertyGroup><TargetFramework>net10.0</TargetFramework></PropertyGroup>
              <ItemGroup>
                <Reference Include="Microsoft.CodeAnalysis">
                  <HintPath>$(MSBuildToolsPath)/Roslyn/bincore/Microsoft.CodeAnalysis.dll</HintPath>
                </Reference>
              </ItemGroup>
            </Project>
            """);
        fixture.Write("Generator/Probe.cs", $$"""
            using System.IO;
            using Microsoft.CodeAnalysis;
            [Generator]
            public sealed class Probe : ISourceGenerator
            {
                public void Initialize(GeneratorInitializationContext context) {}
                public void Execute(GeneratorExecutionContext context) =>
                    File.WriteAllText({{JsonSerializer.Serialize(marker)}}, "executed");
            }
            """);
        File.WriteAllText(fixture.Chosen, "class Chosen { public int Read() { var value = 1; return value; } }\n");
        await fixture.Restore();
        await fixture.Dotnet("build", generator, "--source", fixture.Root, "-p:UseSharedCompilation=false");
        var analyzer = Path.Combine(fixture.Root, "Generator", "bin", "Debug", "net10.0", "Generator.dll");
        var analyzerItem = new XElement("Analyzer", new XAttribute("Include", analyzer));

        var ordinary = new XElement("ItemGroup", analyzerItem);
        var formatterOnly = new XElement("ItemGroup",
            new XAttribute("Condition", """
                '$(DesignTimeBuild)' == 'true' and
                '$(AlwaysCompileMarkupFilesInSeparateDomain)' == 'false' and
                '$(BuildingProject)' == 'false' and '$(ContinueOnError)' == 'ErrorAndContinue'
                """), analyzerItem);
        foreach (var item in new[] { ordinary, formatterOnly })
        {
            fixture.WriteProject(item.ToString());
            await AssertRefusedBeforeExecution(fixture, analyzer, marker);
            var allowed = await fixture.Invoke(mode: "style", diagnostics: ["IDE0008"], severity: "warn", allowed: [analyzer]);
            Outcome(allowed, 2, "changes-required");
            Assert.Equal("executed", File.ReadAllText(marker));
            File.Delete(marker);
        }

        fixture.WriteProject(new XElement("Target", new XAttribute("Name", "DesignTimeMarkupCompilation"),
            new XElement("ItemGroup", analyzerItem)).ToString());
        await AssertRefusedBeforeExecution(fixture, analyzer, marker);

        var releaseOnly = new XElement("ItemGroup",
            new XAttribute("Condition", "'$(Configuration)' == 'Release'"), analyzerItem);
        fixture.WriteProject(releaseOnly.ToString());
        fixture.Write("Mapped.sln", """
            Microsoft Visual Studio Solution File, Format Version 12.00
            Project("{FAE04EC0-301F-11D3-BF4B-00C04F79EFBC}") = "App", "App\App.csproj", "{A168DF84-CAED-473D-ADAA-96901A33BB02}"
            EndProject
            Global
              GlobalSection(SolutionConfigurationPlatforms) = preSolution
                Debug|Any CPU = Debug|Any CPU
              EndGlobalSection
              GlobalSection(ProjectConfigurationPlatforms) = postSolution
                {A168DF84-CAED-473D-ADAA-96901A33BB02}.Debug|Any CPU.ActiveCfg = Release|Any CPU
                {A168DF84-CAED-473D-ADAA-96901A33BB02}.Debug|Any CPU.Build.0 = Release|Any CPU
              EndGlobalSection
            EndGlobal
            """);
        var solution = await fixture.Invoke(workspace: "Mapped.sln", files: ["App/Nested/Chosen.cs"],
            mode: "style", diagnostics: ["IDE0008"], severity: "warn");
        Failure(solution, "unsupported-cleanup-workspace");
        Assert.False(File.Exists(marker), "Mapped solution generator ran without consent.");

        fixture.Write("Dependency/Dependency.csproj", $"""
            <Project Sdk="Microsoft.NET.Sdk">
              <PropertyGroup><TargetFramework>net10.0</TargetFramework></PropertyGroup>
              {releaseOnly}
            </Project>
            """);
        fixture.Write("Dependency/Dependency.cs", "public class Dependency {}");
        fixture.WriteProject("""
            <ItemGroup>
              <ProjectReference Include="../Dependency/Dependency.csproj" SetConfiguration="Configuration=Release" />
            </ItemGroup>
            """);
        await fixture.Restore();
        var reference = await fixture.Invoke(mode: "style", diagnostics: ["IDE0008"], severity: "warn");
        Failure(reference, "unsupported-cleanup-workspace");
        Assert.False(File.Exists(marker), "Mapped dependency generator ran without consent.");
    }

    private static async Task AssertRefusedBeforeExecution(FormatFixture fixture, string analyzer, string marker)
    {
        var run = await fixture.Invoke(mode: "style", diagnostics: ["IDE0008"], severity: "warn");
        Failure(run, "analyzer-consent-required");
        Assert.Contains(analyzer, Items(run.Result, "projectAnalyzers").Select(row => row.GetString()));
        Assert.False(File.Exists(marker), "Generator ran before explicit consent.");
    }
}
