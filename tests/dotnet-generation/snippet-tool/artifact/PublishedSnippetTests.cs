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
}
