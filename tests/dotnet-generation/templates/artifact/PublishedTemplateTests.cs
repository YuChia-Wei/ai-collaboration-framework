using System.IO.Compression;
using Generation.TestSupport;

namespace Generation.Templates.IntegrationTests;

public sealed class PublishedTemplateTests
{
    /// <summary>Registers the actual package and its extracted content in separate hives and generates named outputs.</summary>
    [Fact]
    [Trait("Boundary", "PublishedArtifact")]
    public async Task PackedTemplatesRegisterAndGenerateFromPackageAndExtractedContent()
    {
        const string input = "AICF_TEMPLATE_PACKAGE";
        var package = GenerationFixture.ExistingArtifact(Environment.GetEnvironmentVariable(input), input);
        Assert.Equal(".nupkg", Path.GetExtension(package), ignoreCase: true);
        using var packed = new TemplateRegistration();
        await packed.Install(package);
        await packed.AssertShortNames();
        var projectOutput = Path.Combine(packed.Fixture.Root, "project");
        await packed.Generate("aicf-domain-contract-tests", "Package.DomainContracts", projectOutput);
        Assert.True(File.Exists(Path.Combine(projectOutput, "Package.DomainContracts.csproj")));
        Assert.True(File.Exists(Path.Combine(projectOutput, "fixtures", "Plan.cs")));

        using var extracted = new TemplateRegistration();
        var extraction = Path.Combine(extracted.Fixture.Root, "extraction");
        using var archive = ZipFile.OpenRead(package);
        Assert.DoesNotContain(archive.Entries, entry =>
            entry.FullName.Contains("/bin/", StringComparison.Ordinal) ||
            entry.FullName.Contains("/obj/", StringComparison.Ordinal));
        archive.ExtractToDirectory(extraction);
        await extracted.Install(Path.Combine(extraction, "content"));
        await extracted.AssertShortNames();
        var classOutput = Path.Combine(extracted.Fixture.Root, "class");
        await extracted.Generate("aicf-class", "PackageNote", classOutput, "--namespace", "Sample.Package");
        var generated = File.ReadAllText(Path.Combine(classOutput, "PackageNote.cs"));
        Assert.Contains("namespace Sample.Package", generated);
        Assert.Contains("class PackageNote", generated);
    }
}
