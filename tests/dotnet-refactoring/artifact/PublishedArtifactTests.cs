using Aicf.Dotnet.TestSupport;
using System.Text.Json;

namespace RefactorTool.IntegrationTests;

[Trait("Boundary", "Artifact")]
[Collection(SdkCollection.Name)]
public sealed class PublishedArtifactTests
{
    /// <summary>Loads a real project and writes an extraction plan without changing source.</summary>
    [RefactorArtifactFact]
    public void SingleFilePreviewsAndAppliesInterfaceForRestoredProject()
    {
        using var fixture = new SdkFixture();
        string executable = null!;
        Dictionary<string, byte[]> original = null!;
        CommandResult result = null!;

        this.Given(GivenTheExtractedToolAndRestoredProject, "the extracted tool and a restored project")
            .When(WhenPreviewingExtractionWithTheExtractedExecutable, "previewing extraction with the extracted executable")
            .Then(ThenProduceAnExtractionPlanWithoutChangingSource, "produce an extraction plan without changing source")
            .And(ThenApplyTheExtraction, "apply the selected interface extraction")
            .BDDfy();

        async Task GivenTheExtractedToolAndRestoredProject()
        {
            executable = fixture.Write("published/RefactorTool.exe", File.ReadAllBytes(Artifact()));
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

        async Task ThenApplyTheExtraction()
        {
            (await fixture.Apply(executable)).Applied();
            Assert.Contains("interface ISelected", File.ReadAllText(fixture.Output));
        }
    }

    /// <summary>Preserves cross-project Rename through the standalone executable.</summary>
    [RefactorArtifactFact]
    public void SingleFileRenamesDeclarationAndConsumerAcrossProjects()
    {
        using var fixture = new SdkFixture(twoProjects: true);
        string executable = null!;

        this.Given(GivenTheStandaloneToolAndSolution, "a standalone executable and a restored solution")
            .When(WhenPreviewingAndApplyingRename, "previewing and applying Rename")
            .Then(ThenRenameTheDeclarationAndItsConsumer, "rename the declaration and its cross-project reference")
            .BDDfy();

        async Task GivenTheStandaloneToolAndSolution()
        {
            executable = fixture.Write("published/RefactorTool.exe", File.ReadAllBytes(Artifact()));
            await fixture.Restore();
        }

        async Task WhenPreviewingAndApplyingRename()
        {
            (await fixture.Preview(artifact: executable)).Previewed();
            (await fixture.Apply(executable)).Applied();
        }

        void ThenRenameTheDeclarationAndItsConsumer()
        {
            Assert.Contains("Fetch(int", File.ReadAllText(fixture.Source));
            Assert.Contains(".Fetch(", File.ReadAllText(fixture.Consumer));
        }
    }

    /// <summary>Publishes one executable and notices, and extracts no CoreCLR or test components.</summary>
    [RefactorArtifactFact]
    public void SingleFileIncludesBuildHostWithoutCoreClrOrTestDependencies()
    {
        using var directory = new TestDirectory();
        var executable = Artifact();
        var root = Path.GetDirectoryName(executable)!;
        var extraction = directory.PathFor("extract");
        string[] extractedFiles = null!;

        this.Given(GivenThePublishedInventory, "one executable with its notices")
            .When(WhenStartingWithAFreshExtractionCache, "starting with a fresh extraction cache")
            .Then(ThenExtractBuildHostWithoutCoreClr, "extract BuildHost without CoreCLR or test components")
            .BDDfy();

        void GivenThePublishedInventory()
        {
            Assert.Equal(new[] { "README.md", "RefactorTool.exe", "THIRD-PARTY-NOTICES.txt", "licenses" },
                Directory.GetFileSystemEntries(root).Select(Path.GetFileName).Order(StringComparer.Ordinal));
            Assert.NotEmpty(Directory.EnumerateDirectories(Path.Combine(root, "licenses")));
        }

        async Task WhenStartingWithAFreshExtractionCache()
        {
            var result = await TestDirectory.RunProcess(executable, directory.Root, ["--version"], TimeSpan.FromSeconds(30),
                new() { ["DOTNET_BUNDLE_EXTRACT_BASE_DIR"] = extraction });
            Assert.Equal(0, result.ExitCode);
            Assert.Empty(result.Error);
            extractedFiles = Directory.GetFiles(extraction, "*", SearchOption.AllDirectories);
        }

        void ThenExtractBuildHostWithoutCoreClr()
        {
            var dependenciesFile = Assert.Single(extractedFiles, path => Path.GetFileName(path) == "RefactorTool.deps.json");
            using var dependencies = JsonDocument.Parse(File.ReadAllText(dependenciesFile));
            var libraries = dependencies.RootElement.GetProperty("libraries").EnumerateObject().Select(library => library.Name);
            Assert.Contains(extractedFiles, path => Path.GetFileName(path) == "Microsoft.CodeAnalysis.Workspaces.MSBuild.BuildHost.dll");
            Assert.DoesNotContain(extractedFiles, path => Path.GetFileName(path).ToLowerInvariant() is
                "coreclr.dll" or "hostfxr.dll" or "hostpolicy.dll" or "system.private.corelib.dll");
            Assert.DoesNotContain(libraries, IsTestDependency);
            Assert.DoesNotContain(extractedFiles, path => IsTestDependency(Path.GetFileName(path)));
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
        Assert.True(RefactorTestProfile.WindowsX64, "The selected executable requires Windows x64.");
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
