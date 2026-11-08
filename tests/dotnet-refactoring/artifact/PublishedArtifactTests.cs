using Aicf.Dotnet.TestSupport;
using System.Text.Json;

namespace RefactorTool.IntegrationTests;

[Trait("Boundary", "Artifact")]
[Collection(SdkCollection.Name)]
public sealed class PublishedArtifactTests
{
    /// <summary>Loads a real project and writes an extraction plan without changing source.</summary>
    [RefactorArtifactFact]
    public void ExtractedExecutablePreviewsInterfaceForRestoredProject()
    {
        using var fixture = new SdkFixture();
        string executable = null!;
        Dictionary<string, byte[]> original = null!;
        CommandResult result = null!;

        this.Given(GivenTheExtractedToolAndRestoredProject, "the extracted tool and a restored project")
            .When(WhenPreviewingExtractionWithTheExtractedExecutable, "previewing extraction with the extracted executable")
            .Then(ThenProduceAnExtractionPlanWithoutChangingSource, "produce an extraction plan without changing source")
            .BDDfy();

        async Task GivenTheExtractedToolAndRestoredProject()
        {
            executable = Artifact();
            await fixture.Restore();
            original = fixture.Snapshot();
        }

        async Task WhenPreviewingExtractionWithTheExtractedExecutable() =>
            result = await fixture.Preview(fixture.Extract, artifact: executable);

        void ThenProduceAnExtractionPlanWithoutChangingSource()
        {
            result.Previewed();
            var plan = fixture.Plan();
            Assert.Equal("refactor-plan/1", plan.Contract);
            Assert.Equal(fixture.Output, Assert.Single(plan.Edits, edit => edit.Kind == "create").Path);
            Assert.Equal(fixture.Source, Assert.Single(plan.Edits, edit => edit.Kind == "modify").Path);
            Assert.False(File.Exists(fixture.Output));
            fixture.AssertSnapshot(original);
        }
    }

    /// <summary>Ships BuildHost, notices, and licenses without test dependencies in the extracted package.</summary>
    [RefactorArtifactFact]
    public void ExtractedPackageIncludesRuntimeNoticesAndNoTestDependencies()
    {
        string root = null!;
        string[] libraries = null!;
        string[] files = null!;

        this.Given(GivenTheExtractedArchiveRoot, "the extracted archive root")
            .When(WhenReadingTheArchiveInventory, "reading the archive inventory")
            .Then(ThenIncludeTheRuntimeAndNoticesWithoutTestDependencies, "include the runtime and notices without test dependencies")
            .BDDfy();

        void GivenTheExtractedArchiveRoot() => root = Path.GetDirectoryName(Artifact())!;

        void WhenReadingTheArchiveInventory()
        {
            using var dependencies = JsonDocument.Parse(File.ReadAllText(Path.Combine(root, "RefactorTool.deps.json")));
            libraries = dependencies.RootElement.GetProperty("libraries").EnumerateObject().Select(library => library.Name).ToArray();
            files = Directory.GetFiles(root, "*", SearchOption.AllDirectories);
        }

        void ThenIncludeTheRuntimeAndNoticesWithoutTestDependencies()
        {
            Assert.True(File.Exists(Path.Combine(root, "README.md")));
            Assert.True(File.Exists(Path.Combine(root, "THIRD-PARTY-NOTICES.txt")));
            Assert.True(File.Exists(Path.Combine(root, "BuildHost-netcore/Microsoft.CodeAnalysis.Workspaces.MSBuild.BuildHost.dll")));
            Assert.NotEmpty(Directory.EnumerateDirectories(Path.Combine(root, "licenses")));
            Assert.DoesNotContain(libraries, IsTestDependency);
            Assert.DoesNotContain(files, path => IsTestDependency(Path.GetFileName(path)));
        }
    }

    private static bool IsTestDependency(string name) =>
        name.Contains("BDDfy", StringComparison.OrdinalIgnoreCase) ||
        name.Contains("xunit", StringComparison.OrdinalIgnoreCase) ||
        name.Contains("TestPlatform", StringComparison.OrdinalIgnoreCase) ||
        name.Contains("Microsoft.NET.Test.Sdk", StringComparison.OrdinalIgnoreCase) ||
        name.StartsWith("testhost", StringComparison.OrdinalIgnoreCase) ||
        name.StartsWith("RefactorTool.IntegrationTests", StringComparison.OrdinalIgnoreCase) ||
        name.StartsWith("RefactorTool.ArtifactIntegrationTests", StringComparison.OrdinalIgnoreCase) ||
        name.StartsWith("RefactorTool.UnitTests", StringComparison.OrdinalIgnoreCase);

    private static string Artifact()
    {
        Assert.True(RefactorTestProfile.WindowsX64, "The selected archive requires Windows x64.");
        return PublishedExecutable.Require(Environment.GetEnvironmentVariable("AICF_REFACTOR_TEST_ARTIFACT"), "RefactorTool", "AICF_REFACTOR_TEST_ARTIFACT");
    }
}

internal sealed class RefactorArtifactFactAttribute : FactAttribute
{
    public RefactorArtifactFactAttribute()
    {
        if (!RefactorTestProfile.WindowsX64)
            Skip = RefactorTestProfile.WindowsSkip;
    }
}
