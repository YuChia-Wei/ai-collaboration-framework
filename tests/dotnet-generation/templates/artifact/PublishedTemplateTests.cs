using Generation.TestSupport;

namespace Generation.Templates.IntegrationTests;

public sealed class PublishedTemplateTests
{
    [Fact]
    [Trait("Boundary", "PublishedArtifact")]
    public void PackedTemplatesGenerateBuildAndServeBothApiShapesAndPreserveEdits()
    {
        const string input = "AICF_TEMPLATE_PACKAGE";
        var package = GenerationFixture.ExistingArtifact(Environment.GetEnvironmentVariable(input), input);
        Assert.Equal(".nupkg", Path.GetExtension(package), ignoreCase: true);
        new TemplateScenario().Run(package);
    }
}
