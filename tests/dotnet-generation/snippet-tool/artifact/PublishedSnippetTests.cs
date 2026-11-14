using System.Text.Json;
using Aicf.Dotnet.TestSupport;
using Generation.TestSupport;
using static SnippetTool.IntegrationTests.SnippetTestSupport;

namespace SnippetTool.IntegrationTests;

public sealed class PublishedSnippetTests
{
    /// <summary>
    /// Starts the staged Native AOT executable from another directory and lists the adjacent catalog.
    /// </summary>
    [SnippetArtifactFact]
    [Trait("Boundary", "PublishedArtifact")]
    public void PublishedExecutableFindsItsBundledCatalogFromAnotherDirectory()
    {
        using var fixture = new GenerationFixture();
        string executable = null!;
        string request = null!;
        (int Exit, string Output, string Error) result = (0, "", "");

        this.Given(GivenThePublishedSnippetToolAndARequestOutsideItsDirectory, "the published snippet tool and a request outside its directory")
            .When(WhenListingSnippetsFromTheOtherDirectory, "listing snippets from the other directory")
            .Then(ThenFindTheBundledCatalog, "find the bundled catalog")
            .BDDfy();

        void GivenThePublishedSnippetToolAndARequestOutsideItsDirectory()
        {
            executable = PublishedExecutable.Require(SnippetArtifactFactAttribute.Artifact, "SnippetTool", "AICF_SNIPPET_ARTIFACT");
            request = fixture.Write("request.json", """{"schemaVersion":1,"operation":"list"}""");
        }

        async Task WhenListingSnippetsFromTheOtherDirectory()
        {
            result = await fixture.Execute(executable, TimeSpan.FromSeconds(15), "--request", Path.GetFileName(request));
        }

        void ThenFindTheBundledCatalog() => Assert.Equal(BuiltInIds, Ids(ReadResult(result, null)));
    }

    [SnippetArtifactFact]
    [Trait("Boundary", "MacOSTrialArtifact")]
    public async Task TrialExecutableUsesExternalCatalogAndProducesCompilableCode()
    {
        using var fixture = new GenerationFixture();
        var executable = PublishedExecutable.Require(SnippetArtifactFactAttribute.Artifact, "SnippetTool", "AICF_SNIPPET_ARTIFACT");
        var searched = await Run("""{"schemaVersion":1,"operation":"search","query":"interface-method"}""");
        Assert.Equal(["interface-method"], Ids(searched));

        var inspected = await Run("""{"schemaVersion":1,"operation":"inspect","id":"interface-method"}""");
        Assert.Equal("interface-method", Text(inspected.GetProperty("snippet"), "id"));

        var rendered = await Run("""
            {"schemaVersion":1,"operation":"render","id":"interface-method","parameters":{"methodName":"ReadAsync","returnType":"Task<string>"},"indent":4}
            """);
        var declaration = Text(rendered, "text");
        Assert.Equal("    Task<string> ReadAsync(string value);\n", declaration);
        await Run("""{"schemaVersion":1,"operation":"render","id":"interface-method"}""", "missing-parameter");

        WriteCatalog(fixture);
        fixture.Write("custom-probe.snippet", "var ${variable} = 1; // ${comment}\n");
        var custom = await Run("""
            {"schemaVersion":1,"operation":"render","id":"custom-probe","source":"custom.json","parameters":{"variable":"count","comment":"trial"}}
            """);
        Assert.Equal("custom", Text(custom.GetProperty("source"), "id"));
        Assert.Equal("var count = 1; // trial\n", Text(custom, "text"));

        var project = fixture.Write("Consumer.csproj", """
            <Project Sdk="Microsoft.NET.Sdk">
              <PropertyGroup><TargetFramework>net10.0</TargetFramework></PropertyGroup>
            </Project>
            """);
        fixture.Write("IReader.cs", "using System.Threading.Tasks;\npublic interface IReader\n{\n" + declaration + "}\n");
        await fixture.Build(project);

        async Task<JsonElement> Run(string request, string? failure = null)
        {
            var requestPath = fixture.Write("trial.json", request);
            var result = await fixture.Execute(executable, TimeSpan.FromSeconds(15), "--request", Path.GetFileName(requestPath));
            return ReadResult(result, failure);
        }
    }
}
