using Aicf.Dotnet.TestSupport;
using Generation.TestSupport;
using System.Text.Json;
using static SnippetTool.IntegrationTests.SnippetTestSupport;

namespace SnippetTool.IntegrationTests;

public sealed class PublishedSnippetTests
{
    [SnippetArtifactFact]
    [Trait("Boundary", "PublishedArtifact")]
    public void PublishedExecutableFindsItsBundledCatalogFromAnotherDirectory()
    {
        using var fixture = new GenerationFixture();
        string executable = null!;
        string request = null!;
        (int Exit, string Output, string Error) result = (0, "", "");
        (int Exit, string Output, string Error) failure = (0, "", "");
        (int Exit, string Output, string Error) version = (0, "", "");

        this.Given(GivenThePublishedSnippetToolAndARequestOutsideItsDirectory, "the published snippet tool and a request outside its directory")
            .When(WhenListingSnippetsFromTheOtherDirectory, "listing snippets from the other directory")
            .Then(ThenFindTheBundledCatalog, "find the bundled catalog")
            .Given(GivenAnUnsupportedRequestSchema, "an unsupported request schema")
            .When(WhenInvokingThePublishedToolWithThatSchema, "invoking the published tool with that schema")
            .Then(ThenReturnTheStableSchemaError, "return the stable schema error")
            .When(WhenRequestingTheExecutableVersion, "requesting the executable version")
            .Then(ThenPrintTheVersionWithoutErrors, "print the version without errors")
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

        void GivenAnUnsupportedRequestSchema() => File.WriteAllText(request, """{"schemaVersion":2,"operation":"list"}""");

        async Task WhenInvokingThePublishedToolWithThatSchema()
        {
            failure = await fixture.Execute(executable, TimeSpan.FromSeconds(15), "--request", Path.GetFileName(request));
        }

        void ThenReturnTheStableSchemaError() => ReadResult(failure, "unsupported-request-schema");

        async Task WhenRequestingTheExecutableVersion()
        {
            version = await fixture.Execute(executable, TimeSpan.FromSeconds(15), "--version");
        }

        void ThenPrintTheVersionWithoutErrors()
        {
            Assert.Equal(0, version.Exit);
            Assert.Empty(version.Error);
            Assert.False(string.IsNullOrWhiteSpace(version.Output));
        }
    }

    [SnippetArtifactFact(linuxOnly: true)]
    [Trait("Boundary", "LinuxArtifact")]
    public void PublishedExecutableRejectsFifoWithoutOpeningIt()
    {
        using var fixture = new GenerationFixture();
        string executable = null!, request = null!;
        (int Exit, string Output, string Error) run = (0, "", "");

        this.Given(GivenAStagedExecutableAndAFifoBody, "a staged executable and a FIFO body")
            .When(WhenInspectingTheFifoBody, "inspecting the FIFO body")
            .Then(ThenRejectTheNonRegularFile, "reject the non-regular file without blocking")
            .BDDfy();

        async Task GivenAStagedExecutableAndAFifoBody()
        {
            executable = PublishedExecutable.Require(SnippetArtifactFactAttribute.Artifact, "SnippetTool", "AICF_SNIPPET_ARTIFACT");
            WriteCatalog(fixture);
            var fifo = await fixture.Execute(SnippetArtifactFactAttribute.RequireMkfifo(), TimeSpan.FromSeconds(15), "--", Path.Combine(fixture.Root, "custom-probe.snippet"));
            Assert.True(fifo.Exit == 0, fifo.Error);
            request = fixture.Write("request.json", JsonSerializer.Serialize(Inspect("custom-probe")));
        }

        async Task WhenInspectingTheFifoBody() =>
            run = await fixture.Execute(executable, TimeSpan.FromSeconds(15), "--request", request);

        void ThenRejectTheNonRegularFile() => ReadResult(run, "invalid-body");
    }
}
