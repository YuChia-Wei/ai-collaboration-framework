using System.Text.Json;
using System.Xml.Linq;
using static FormatTool.IntegrationTests.FormatFixture;

namespace FormatTool.IntegrationTests;

[Collection("FormatTool SDK")]
public sealed class GeneratorConsentTests
{
    [FormatSdkFact]
    public void GeneratorExecutesOnlyAfterConsentInBothDesignTimeContexts()
    {
        using var fixture = new FormatFixture();
        string marker = null!;
        string analyzer = null!;
        XElement analyzerItem = null!;
        XElement ordinary = null!;
        XElement formatterOnly = null!;
        List<((int Exit, JsonElement Result) Refused, bool RanWithoutConsent, (int Exit, JsonElement Result) Allowed, string? Marker)> consentRuns = null!;
        (int Exit, JsonElement Result) markup = default;
        XElement releaseOnly = null!;
        (int Exit, JsonElement Result) solution = default;
        (int Exit, JsonElement Result) reference = default;

        this.Given(GivenAnAnalyzerWithAnObservableExecutionMarker, "an analyzer with an observable execution marker")
            .When(WhenCheckingOrdinaryAndFormatterOnlyAnalyzerInputsWithAndWithoutConsent, "checking ordinary and formatter only analyzer inputs with and without consent")
            .Then(ThenRunTheGeneratorOnlyAfterConsent, "run the generator only after consent")
            .Given(GivenAnAnalyzerIntroducedByTheMarkupTarget, "an analyzer introduced by the markup target")
            .When(WhenCheckingTheMarkupTargetWithoutConsent, "checking the markup target without consent")
            .Then(ThenRefuseBeforeExecutingTheMarkupGenerator, "refuse before executing the markup generator")
            .Given(GivenASolutionMappingDebugToRelease, "a solution mapping debug to release")
            .When(WhenCheckingTheMappedSolution, "checking the mapped solution")
            .Then(ThenRefuseTheMappedSolutionWithoutExecutingTheGenerator, "refuse the mapped solution without executing the generator")
            .Given(GivenADependencyWithItsOwnReleaseConfiguration, "a dependency with its own release configuration")
            .When(WhenCheckingTheMappedDependency, "checking the mapped dependency")
            .Then(ThenRefuseTheMappedDependencyWithoutExecutingTheGenerator, "refuse the mapped dependency without executing the generator")
            .BDDfy();

        async Task GivenAnAnalyzerWithAnObservableExecutionMarker()
        {
            marker = Path.Combine(fixture.Root, "generator-executed.txt");
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
            analyzer = Path.Combine(fixture.Root, "Generator", "bin", "Debug", "net10.0", "Generator.dll");
            analyzerItem = new XElement("Analyzer", new XAttribute("Include", analyzer));

            ordinary = new XElement("ItemGroup", analyzerItem);
            formatterOnly = new XElement("ItemGroup",
                new XAttribute("Condition", """
                    '$(DesignTimeBuild)' == 'true' and
                    '$(AlwaysCompileMarkupFilesInSeparateDomain)' == 'false' and
                    '$(BuildingProject)' == 'false' and '$(ContinueOnError)' == 'ErrorAndContinue'
                    """), analyzerItem);
            consentRuns = new List<((int Exit, JsonElement Result) Refused, bool RanWithoutConsent, (int Exit, JsonElement Result) Allowed, string? Marker)>();
        }

        async Task WhenCheckingOrdinaryAndFormatterOnlyAnalyzerInputsWithAndWithoutConsent()
        {
            foreach (var item in new[] { ordinary, formatterOnly })
            {
                fixture.WriteProject(item.ToString());
                var refused = await fixture.Invoke(mode: "style", diagnostics: ["IDE0008"], severity: "warn");
                var ranWithoutConsent = File.Exists(marker);
                var allowed = await fixture.Invoke(mode: "style", diagnostics: ["IDE0008"], severity: "warn", allowed: [analyzer]);
                var markerText = File.Exists(marker) ? File.ReadAllText(marker) : null;
                consentRuns.Add((refused, ranWithoutConsent, allowed, markerText));
                File.Delete(marker);
            }
        }

        void ThenRunTheGeneratorOnlyAfterConsent()
        {
            foreach (var (refused, ranWithoutConsent, allowed, markerText) in consentRuns)
            {
                AssertConsentRefused(refused, analyzer, ranWithoutConsent);
                Outcome(allowed, 2, "changes-required");
                Assert.Equal("executed", markerText);
            }
        }

        void GivenAnAnalyzerIntroducedByTheMarkupTarget() => fixture.WriteProject(new XElement("Target", new XAttribute("Name", "DesignTimeMarkupCompilation"),
            new XElement("ItemGroup", analyzerItem)).ToString());

        async Task WhenCheckingTheMarkupTargetWithoutConsent()
        {
            markup = await fixture.Invoke(mode: "style", diagnostics: ["IDE0008"], severity: "warn");
        }

        void ThenRefuseBeforeExecutingTheMarkupGenerator() => AssertConsentRefused(markup, analyzer, File.Exists(marker));

        void GivenASolutionMappingDebugToRelease()
        {
            releaseOnly = new XElement("ItemGroup",
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
        }

        async Task WhenCheckingTheMappedSolution()
        {
            solution = await fixture.Invoke(workspace: "Mapped.sln", files: ["App/Nested/Chosen.cs"],
                mode: "style", diagnostics: ["IDE0008"], severity: "warn");
        }

        void ThenRefuseTheMappedSolutionWithoutExecutingTheGenerator()
        {
            Failure(solution, "unsupported-cleanup-workspace");
            Assert.False(File.Exists(marker), "Mapped solution generator ran without consent.");
        }

        async Task GivenADependencyWithItsOwnReleaseConfiguration()
        {
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
        }

        async Task WhenCheckingTheMappedDependency()
        {
            reference = await fixture.Invoke(mode: "style", diagnostics: ["IDE0008"], severity: "warn");
        }

        void ThenRefuseTheMappedDependencyWithoutExecutingTheGenerator()
        {
            Failure(reference, "unsupported-cleanup-workspace");
            Assert.False(File.Exists(marker), "Mapped dependency generator ran without consent.");
        }
    }

    private static void AssertConsentRefused((int Exit, JsonElement Result) run, string analyzer, bool ranWithoutConsent)
    {
        Failure(run, "analyzer-consent-required");
        Assert.Contains(analyzer, Items(run.Result, "projectAnalyzers").Select(row => row.GetString()));
        Assert.False(ranWithoutConsent, "Generator ran before explicit consent.");
    }
}
