using Aicf.Dotnet.TestSupport;
using System.Text.Json;
using Microsoft.CodeAnalysis.CSharp;
using Microsoft.CodeAnalysis.CSharp.Syntax;

namespace RefactorTool.IntegrationTests;

[Trait("Boundary", "Artifact")]
[Collection(SdkCollection.Name)]
public sealed class PublishedArtifactTests
{
    [RefactorArtifactFact]
    public void PublishedRenamePreservesCrossProjectSemanticsAndUnrelatedBytes()
    {
        using var fixture = new SdkFixture(twoProjects: true);
        string artifact = null!;
        Dictionary<string, byte[]> original = null!;
        CommandResult preview = null!, applyingThePublishedRenameResult = null!;

        this.Given(GivenAnExtractedToolAndRestoredCrossProjectReferences, "an extracted tool and restored cross project references")
            .When(WhenPreviewingThePublishedRename, "previewing the published rename")
            .Then(ThenDescribeRelatedSymbolsWithoutWriting, "describe related symbols without writing")
            .When(WhenApplyingThePublishedRename, "applying the published rename")
            .Then(ThenUpdateRelatedSymbolsAndPreserveUnrelatedSource, "update related symbols and preserve unrelated source")
            .When(WhenBuildingTheRenamedWorkspace, "building the renamed workspace")
            .Then(ThenTheRenamedWorkspaceBuilds, "the renamed workspace builds")
            .BDDfy();

        async Task GivenAnExtractedToolAndRestoredCrossProjectReferences()
        {
            artifact = Artifact();

            await fixture.Restore();
            original = fixture.Snapshot();
        }

        async Task WhenPreviewingThePublishedRename() => preview = await fixture.Preview(artifact: artifact);

        void ThenDescribeRelatedSymbolsWithoutWriting()
        {
            preview.Previewed();
            fixture.AssertSnapshot(original);
            var plan = fixture.Plan();
            Assert.Equal(2, plan.Projects.Length);
            Assert.Equal("Enable", Assert.Single(plan.Projects, project => project.Path == fixture.Project).Nullable);
            Assert.NotEmpty(plan.Patch);
            Assert.Contains("M:Demo.IService.Get(System.Int32)", plan.RelatedSymbols);
            Assert.Contains("M:Demo.Derived.Get(System.Int32)", plan.RelatedSymbols);
        }

        async Task WhenApplyingThePublishedRename() => applyingThePublishedRenameResult = await fixture.Apply(artifact);

        void ThenUpdateRelatedSymbolsAndPreserveUnrelatedSource()
        {
            applyingThePublishedRenameResult.Applied();
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
        }

        async Task WhenBuildingTheRenamedWorkspace() => await fixture.Dotnet("build", fixture.Workspace, "--no-restore", "--nologo");

        void ThenTheRenamedWorkspaceBuilds() => Assert.True(File.Exists(fixture.PathFor("B/bin/Debug/net10.0/B.dll")));
    }

    [RefactorArtifactFact]
    public void PublishedExtractionAppliesSelectedContractAndConsumerDispatches()
    {
        using var fixture = new SdkFixture(twoProjects: true);
        string artifact = null!;
        Dictionary<string, byte[]> original = null!;
        byte[] originalProject = null!;
        CommandResult previewingThePublishedExtractionResult = null!;
        CommandResult applyingThePublishedExtractionResult = null!;
        string consumer = null!;
        string result = null!;

        this.Given(GivenAnExtractedToolAndRestoredConsumer, "an extracted tool and restored consumer")
            .When(WhenPreviewingThePublishedExtraction, "previewing the published extraction")
            .Then(ThenRecordCreateAndModifyWithoutWriting, "record create and modify without writing")
            .When(WhenApplyingThePublishedExtraction, "applying the published extraction")
            .Then(ThenChangeOnlyTheSelectedContractAndBaseList, "change only the selected contract and base list")
            .Given(GivenABuiltWorkspaceAndExecutableConsumer, "a built workspace and executable consumer")
            .When(WhenRunningTheExtractedContractConsumer, "running the extracted contract consumer")
            .Then(ThenDispatchOnlyTheSelectedMembers, "dispatch only the selected members")
            .BDDfy();

        async Task GivenAnExtractedToolAndRestoredConsumer()
        {
            artifact = Artifact();

            await fixture.Restore();
            original = fixture.Snapshot();
            originalProject = File.ReadAllBytes(fixture.Project);
        }

        async Task WhenPreviewingThePublishedExtraction() => previewingThePublishedExtractionResult = await fixture.Preview(fixture.Extract, artifact: artifact);

        void ThenRecordCreateAndModifyWithoutWriting()
        {
            previewingThePublishedExtractionResult.Previewed();
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
        }

        async Task WhenApplyingThePublishedExtraction() => applyingThePublishedExtractionResult = await fixture.Apply(artifact);

        void ThenChangeOnlyTheSelectedContractAndBaseList()
        {
            applyingThePublishedExtractionResult.Applied();
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
        }

        async Task GivenABuiltWorkspaceAndExecutableConsumer()
        {
            await fixture.Dotnet("build", fixture.Workspace, "--no-restore", "--nologo");
            consumer = fixture.AddExecutableConsumer("""
                using Demo;
                using Contracts;
                ISelected s = new Service();
                s.Property = 7;
                System.Console.Write($"{s.Get(2)}|{s.Property}|{new Service().Get("abcd")}");
                """);
        }

        async Task WhenRunningTheExtractedContractConsumer()
        {
            result = await fixture.Dotnet("run", "--project", consumer, "--no-restore", "-v:q");
        }

        void ThenDispatchOnlyTheSelectedMembers() => Assert.Equal("3|7|4", result.Trim().Split('\n')[^1]);
    }

    [RefactorArtifactFact]
    public void CallerSdkConfigurationDoesNotOverrideWorkspaceSdk()
    {
        using var fixture = new SdkFixture();
        CommandResult previewingFromTheCallerDirectoryResult = null!;

        this.Given(GivenADifferentSdkInTheCallerDirectory, "a different sdk in the caller directory")
            .When(WhenPreviewingFromTheCallerDirectory, "previewing from the caller directory")
            .Then(ThenSelectTheWorkspaceSdk, "select the workspace sdk")
            .BDDfy();

        async Task GivenADifferentSdkInTheCallerDirectory()
        {
            await fixture.Restore();
            fixture.Write("caller/global.json", """{"sdk":{"version":"99.0.100","rollForward":"disable"}}""");
        }

        async Task WhenPreviewingFromTheCallerDirectory() => previewingFromTheCallerDirectoryResult = await fixture.Preview(artifact: Artifact(), workingDirectory: fixture.PathFor("caller"));

        void ThenSelectTheWorkspaceSdk()
        {
            previewingFromTheCallerDirectoryResult.Previewed();
            Assert.Equal(SdkFixture.Version, fixture.Plan().Sdk);
        }
    }

    [RefactorArtifactFact]
    public void SdkPathsCanSelectLocalSdkWhenSameVersionExistsInHost()
    {
        using var fixture = new SdkFixture();
        string artifact = null!;
        string localSdk = null!;
        CommandResult previewingWithTheLocalSdkResult = null!;
        CommandResult applyingWithTheLocalSdkResult = null!;
        Request request = null!;
        CommandResult previewingExtractionWithTheLocalSdkResult = null!;

        this.Given(GivenTheSameSdkVersionInLocalAndHostRoots, "the same sdk version in local and host roots")
            .When(WhenPreviewingWithTheLocalSdk, "previewing with the local sdk")
            .Then(ThenPreviewingWithTheLocalSdkSucceeds, "previewing with the local sdk succeeds")
            .When(WhenApplyingWithTheLocalSdk, "applying with the local sdk")
            .Then(ThenApplyingWithTheLocalSdkSucceeds, "applying with the local sdk succeeds")
            .Given(GivenTheRenamedMembers, "the renamed members")
            .When(WhenPreviewingExtractionWithTheLocalSdk, "previewing extraction with the local sdk")
            .Then(ThenCaptureBuildInputsFromTheLocalRoot, "capture build inputs from the local root")
            .BDDfy();

        async Task GivenTheSameSdkVersionInLocalAndHostRoots()
        {
            artifact = Artifact();

            var info = await fixture.Dotnet("--info");
            var sdkPath = BasePath(info);
            var host = Directory.GetParent(sdkPath)!.Parent!.FullName;
            var local = fixture.PathFor("local-sdk");
            localSdk = $"local-sdk/sdk/{SdkFixture.Version}";
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
        }

        async Task WhenPreviewingWithTheLocalSdk() => previewingWithTheLocalSdkResult = await fixture.Preview(artifact: artifact);

        void ThenPreviewingWithTheLocalSdkSucceeds() => previewingWithTheLocalSdkResult.Previewed();

        async Task WhenApplyingWithTheLocalSdk() => applyingWithTheLocalSdkResult = await fixture.Apply(artifact);

        void ThenApplyingWithTheLocalSdkSucceeds() => applyingWithTheLocalSdkResult.Applied();

        void GivenTheRenamedMembers()
        {
            request = fixture.Extract with { Members = ["M:Demo.Service.Fetch(System.Int32)", SemanticWorkspace.Property] };
        }

        async Task WhenPreviewingExtractionWithTheLocalSdk() => previewingExtractionWithTheLocalSdkResult = await fixture.Preview(request, artifact: artifact);

        void ThenCaptureBuildInputsFromTheLocalRoot()
        {
            previewingExtractionWithTheLocalSdkResult.Previewed();
            Assert.Contains(fixture.Plan().Inputs, input => Paths.Comparer.Equals(input.Path, fixture.PathFor(localSdk + "/Microsoft.Build.dll")));
        }
    }

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

    private static string BasePath(string info) => Path.TrimEndingDirectorySeparator(info.Split('\n')
        .Single(line => line.TrimStart().StartsWith("Base Path:", StringComparison.Ordinal)).Split(':', 2)[1].Trim());

    private static bool IsTestDependency(string name) =>
        name.Contains("BDDfy", StringComparison.OrdinalIgnoreCase) ||
        name.Contains("xunit", StringComparison.OrdinalIgnoreCase) ||
        name.Contains("TestPlatform", StringComparison.OrdinalIgnoreCase) ||
        name.Contains("Microsoft.NET.Test.Sdk", StringComparison.OrdinalIgnoreCase) ||
        name.StartsWith("testhost", StringComparison.OrdinalIgnoreCase) ||
        name.StartsWith("RefactorTool.IntegrationTests", StringComparison.OrdinalIgnoreCase) ||
        name.StartsWith("RefactorTool.UnitTests", StringComparison.OrdinalIgnoreCase);

    private static string Artifact()
    {
        Assert.True(RefactorTestProfile.WindowsX64, "The selected archive requires Windows x64.");
        return PublishedExecutable.Require(RefactorTestProfile.Artifact, "RefactorTool", "AICF_REFACTOR_TEST_ARTIFACT");
    }
}
