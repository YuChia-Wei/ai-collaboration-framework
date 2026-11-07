using System.Text.Json;
using Microsoft.CodeAnalysis.CSharp;
using Microsoft.CodeAnalysis.CSharp.Syntax;

namespace RefactorTool.Tests;

[Trait("Boundary", "Artifact")]
[Collection(SdkCollection.Name)]
public sealed class PublishedArtifactTests
{
    [Fact]
    public async Task PublishedRenamePreservesCrossProjectSemanticsAndUnrelatedBytes()
    {
        var artifact = Artifact();
        using var fixture = new SdkFixture(twoProjects: true);
        await fixture.Restore();
        var original = fixture.Snapshot();
        (await fixture.Preview(artifact: artifact)).Previewed();
        fixture.AssertSnapshot(original);
        var plan = fixture.Plan();
        Assert.Equal(2, plan.Projects.Length);
        Assert.Equal("Enable", Assert.Single(plan.Projects, project => project.Path == fixture.Project).Nullable);
        Assert.NotEmpty(plan.Patch);
        Assert.Contains("M:Demo.IService.Get(System.Int32)", plan.RelatedSymbols);
        Assert.Contains("M:Demo.Derived.Get(System.Int32)", plan.RelatedSymbols);
        (await fixture.Apply(artifact)).Applied();
        var source = File.ReadAllText(fixture.Source);
        var consumer = File.ReadAllText(fixture.Consumer);
        Assert.Contains("interface IService { int Fetch(int value); }", source);
        Assert.Contains("override int Fetch(int value) => base.Fetch(value)", source);
        Assert.Contains("public int Get(string value)", source);
        Assert.Contains("class Other { public int Get(int value)", source);
        Assert.Contains("service.Fetch(2)", consumer);
        Assert.Contains("new Other().Get(4)", consumer);
        Assert.Contains("cref=\"Service.Fetch(int)\"", consumer);
        Assert.Contains("nameof(IService.Fetch)", consumer);
        Assert.Contains("\"Get Service\"", consumer);
        Assert.Contains("// Get Service", consumer);
        Assert.Equal(source.Count(c => c == '\n'), source.Split("\r\n").Length - 1);
        await fixture.Dotnet("build", fixture.Workspace, "--no-restore", "--nologo");
    }

    [Fact]
    public async Task PublishedExtractionAppliesSelectedContractAndConsumerDispatches()
    {
        var artifact = Artifact();
        using var fixture = new SdkFixture(twoProjects: true);
        await fixture.Restore();
        var original = fixture.Snapshot();
        var originalProject = File.ReadAllBytes(fixture.Project);
        (await fixture.Preview(fixture.Extract, artifact: artifact)).Previewed();
        fixture.AssertSnapshot(original);
        var plan = fixture.Plan();
        Assert.Equal(new[] { "create", "modify" }, plan.Edits.Select(e => e.Kind).Order().ToArray());
        Assert.Contains("--- /dev/null", plan.Patch);
        Assert.Equal("", Assert.Single(plan.Edits, e => e.Kind == "create").Before);
        using var wirePlan = JsonDocument.Parse(File.ReadAllText(fixture.PlanPath));
        Assert.Equal("refactor-plan/1", wirePlan.RootElement.GetProperty("contract").GetString());
        var create = Assert.Single(wirePlan.RootElement.GetProperty("edits").EnumerateArray(),
            edit => edit.GetProperty("kind").GetString() == "create");
        Assert.Equal("", create.GetProperty("before").GetString());
        (await fixture.Apply(artifact)).Applied();
        Assert.Equal(originalProject, File.ReadAllBytes(fixture.Project));
        Assert.Equal(original[fixture.Consumer], File.ReadAllBytes(fixture.Consumer));
        var edited = File.ReadAllText(fixture.Source);
        Assert.Equal(1, edited.Split(", global::Contracts.ISelected").Length - 1);
        Assert.Equal(original[fixture.Source], System.Text.Encoding.UTF8.GetBytes(edited.Replace(", global::Contracts.ISelected", "")));
        var contract = CSharpSyntaxTree.ParseText(File.ReadAllText(fixture.Output)).GetRoot();
        var declaration = Assert.Single(contract.DescendantNodes().OfType<InterfaceDeclarationSyntax>());
        Assert.Equal("ISelected", declaration.Identifier.ValueText);
        Assert.Equal(2, declaration.Members.Count);
        Assert.Equal("Property", Assert.Single(declaration.Members.OfType<PropertyDeclarationSyntax>()).Identifier.ValueText);
        var method = Assert.Single(declaration.Members.OfType<MethodDeclarationSyntax>());
        Assert.Equal("Get", method.Identifier.ValueText);
        Assert.Contains(Assert.Single(method.ParameterList.Parameters).Type!.ToString(), new[] { "int", "System.Int32", "global::System.Int32" });
        await fixture.Dotnet("build", fixture.Workspace, "--no-restore", "--nologo");
        var consumer = fixture.AddExecutableConsumer("""
            using Demo;
            using Contracts;
            ISelected s = new Service();
            s.Property = 7;
            System.Console.Write($"{s.Get(2)}|{s.Property}|{new Service().Get("abcd")}");
            """);
        var result = await fixture.Dotnet("run", "--project", consumer, "--no-restore", "-v:q");
        Assert.Equal("3|7|4", result.Trim().Split('\n')[^1]);
    }

    [Fact]
    public async Task CallerSdkConfigurationDoesNotOverrideWorkspaceSdk()
    {
        using var fixture = new SdkFixture();
        await fixture.Restore();
        fixture.Write("caller/global.json", """{"sdk":{"version":"99.0.100","rollForward":"disable"}}""");
        (await fixture.Preview(artifact: Artifact(), workingDirectory: fixture.PathFor("caller"))).Previewed();
        Assert.Equal(SdkFixture.Version, fixture.Plan().Sdk);
    }

    [Fact]
    public async Task SdkPathsCanSelectLocalSdkWhenSameVersionExistsInHost()
    {
        var artifact = Artifact();
        using var fixture = new SdkFixture();
        var info = await fixture.Dotnet("--info");
        var sdkPath = BasePath(info);
        var host = Directory.GetParent(sdkPath)!.Parent!.FullName;
        var local = fixture.PathFor("local-sdk");
        var localSdk = $"local-sdk/sdk/{SdkFixture.Version}";
        await fixture.Junction(localSdk, sdkPath);
        foreach (var dependency in new[] { "shared", "packs", "sdk-manifests" })
            await fixture.Junction($"local-sdk/{dependency}", Path.Combine(host, dependency));
        fixture.Write("global.json", Data.Serialize(new
        {
            sdk = new { version = SdkFixture.Version, rollForward = "disable", paths = new[] { local, "$host$" } }
        }));
        var inventory = await fixture.Dotnet("--list-sdks");
        Assert.True(inventory.Split('\n').Count(line => line.StartsWith(SdkFixture.Version + " ", StringComparison.Ordinal)) >= 2, inventory);
        Assert.Equal(fixture.PathFor(localSdk), BasePath(await fixture.Dotnet("--info")), ignoreCase: true);
        await fixture.Restore();
        (await fixture.Preview(artifact: artifact)).Previewed();
        (await fixture.Apply(artifact)).Applied();
        var request = fixture.Extract with { Members = ["M:Demo.Service.Fetch(System.Int32)", SemanticWorkspace.Property] };
        (await fixture.Preview(request, artifact: artifact)).Previewed();
        Assert.Contains(fixture.Plan().Inputs, input => Paths.Comparer.Equals(input.Path, fixture.PathFor(localSdk + "/Microsoft.Build.dll")));
    }

    [Fact]
    public void ExtractedPackageIncludesRuntimeNoticesAndNoTestDependencies()
    {
        var root = Path.GetDirectoryName(Artifact())!;
        Assert.True(File.Exists(Path.Combine(root, "README.md")));
        Assert.True(File.Exists(Path.Combine(root, "THIRD-PARTY-NOTICES.txt")));
        Assert.True(File.Exists(Path.Combine(root, "BuildHost-netcore/Microsoft.CodeAnalysis.Workspaces.MSBuild.BuildHost.dll")));
        Assert.NotEmpty(Directory.EnumerateDirectories(Path.Combine(root, "licenses")));
        using var dependencies = JsonDocument.Parse(File.ReadAllText(Path.Combine(root, "RefactorTool.deps.json")));
        Assert.DoesNotContain(dependencies.RootElement.GetProperty("libraries").EnumerateObject(), library => IsTestDependency(library.Name));
        Assert.DoesNotContain(Directory.EnumerateFiles(root, "*", SearchOption.AllDirectories), path => IsTestDependency(Path.GetFileName(path)));
    }

    private static string BasePath(string info) => Path.TrimEndingDirectorySeparator(info.Split('\n')
        .Single(line => line.TrimStart().StartsWith("Base Path:", StringComparison.Ordinal)).Split(':', 2)[1].Trim());

    private static bool IsTestDependency(string name) =>
        name.Contains("xunit", StringComparison.OrdinalIgnoreCase) ||
        name.Contains("TestPlatform", StringComparison.OrdinalIgnoreCase) ||
        name.Contains("Microsoft.NET.Test.Sdk", StringComparison.OrdinalIgnoreCase) ||
        name.StartsWith("testhost", StringComparison.OrdinalIgnoreCase) ||
        name.StartsWith("RefactorTool.Tests", StringComparison.OrdinalIgnoreCase);

    private static string Artifact()
    {
        var path = Environment.GetEnvironmentVariable("AICF_REFACTOR_TEST_ARTIFACT");
        Assert.True(path is not null && Path.IsPathFullyQualified(path) &&
            Path.GetFileName(path).Equals("RefactorTool.exe", StringComparison.OrdinalIgnoreCase) && File.Exists(path),
            "Set AICF_REFACTOR_TEST_ARTIFACT to the absolute RefactorTool.exe path in the extracted win-x64 archive.");
        return path;
    }
}
