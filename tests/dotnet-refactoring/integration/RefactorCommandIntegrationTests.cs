using System.Text.Json;
using Microsoft.CodeAnalysis.CSharp;
using Microsoft.CodeAnalysis.CSharp.Syntax;

namespace RefactorTool.IntegrationTests;

[Trait("Boundary", "Sdk")]
[Collection(SdkCollection.Name)]
public sealed class RefactorCommandIntegrationTests
{
    /// <summary>Applies exactly the selected interface and verifies that a consumer dispatches through it.</summary>
    [RefactorSdkFact]
    public void ExtractionAppliesSelectedContractAndConsumerDispatches()
    {
        using var fixture = new SdkFixture(twoProjects: true);
        Dictionary<string, byte[]> original = null!;
        byte[] originalProject = null!;
        CommandResult previewingTheExtractionResult = null!;
        CommandResult applyingTheExtractionResult = null!;
        string consumer = null!;
        string result = null!;

        this.Given(GivenARestoredConsumer, "a restored consumer")
            .When(WhenPreviewingTheExtraction, "previewing the extraction")
            .Then(ThenRecordCreateAndModifyWithoutWriting, "record create and modify without writing")
            .When(WhenApplyingTheExtraction, "applying the extraction")
            .Then(ThenChangeOnlyTheSelectedContractAndBaseList, "change only the selected contract and base list")
            .Given(GivenAnExecutableConsumer, "an executable consumer")
            .When(WhenRunningTheContractConsumer, "running the contract consumer")
            .Then(ThenDispatchOnlyTheSelectedMembers, "dispatch only the selected members")
            .BDDfy();

        async Task GivenARestoredConsumer()
        {
            await fixture.Restore();
            original = fixture.Snapshot();
            originalProject = File.ReadAllBytes(fixture.Project);
        }

        async Task WhenPreviewingTheExtraction() => previewingTheExtractionResult = await fixture.Preview(fixture.Extract);

        void ThenRecordCreateAndModifyWithoutWriting()
        {
            previewingTheExtractionResult.Previewed();
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

        async Task WhenApplyingTheExtraction() => applyingTheExtractionResult = await fixture.Apply();

        void ThenChangeOnlyTheSelectedContractAndBaseList()
        {
            applyingTheExtractionResult.Applied();
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

        void GivenAnExecutableConsumer()
        {
            consumer = fixture.AddExecutableConsumer("""
                using Demo;
                using Contracts;
                ISelected s = new Service();
                s.Property = 7;
                System.Console.Write($"{s.Get(2)}|{s.Property}|{new Service().Get("abcd")}");
                """);
        }

        async Task WhenRunningTheContractConsumer()
        {
            result = await fixture.Dotnet("run", "--project", consumer, "--no-restore", "-v:q");
        }

        void ThenDispatchOnlyTheSelectedMembers() => Assert.Equal("3|7|4", result.Trim().Split('\n')[^1]);
    }

    /// <summary>Loads the workspace SDK even when the caller directory selects a different version.</summary>
    [RefactorSdkFact]
    public void CallerSdkConfigurationDoesNotOverrideWorkspaceSdk()
    {
        using var fixture = new SdkFixture();
        CommandResult result = null!;

        this.Given(GivenADifferentSdkInTheCallerDirectory, "a different sdk in the caller directory")
            .When(WhenInspectingFromTheCallerDirectory, "inspecting from the caller directory")
            .Then(ThenSelectTheWorkspaceSdk, "select the workspace sdk")
            .BDDfy();

        async Task GivenADifferentSdkInTheCallerDirectory()
        {
            await fixture.Restore();
            fixture.Write("caller/global.json", """{"sdk":{"version":"99.0.100","rollForward":"disable"}}""");
        }

        async Task WhenInspectingFromTheCallerDirectory() => result = await fixture.Inspect(workingDirectory: fixture.PathFor("caller"));

        void ThenSelectTheWorkspaceSdk()
        {
            result.Loaded();
            Assert.Equal(SdkFixture.Version, result.Text("sdk"));
        }
    }

    /// <summary>Previews and applies extraction with the selected local SDK when two roots contain the same version.</summary>
    [RefactorSdkFact(requiresJunction: true)]
    public void SdkPathsCanSelectLocalSdkWhenSameVersionExistsInHost()
    {
        using var fixture = new SdkFixture();
        string localSdk = null!;
        CommandResult preview = null!, applied = null!;

        this.Given(GivenTheSameSdkVersionInLocalAndHostRoots, "the same sdk version in local and host roots")
            .When(WhenPreviewingExtractionWithTheLocalSdk, "previewing extraction with the local sdk")
            .Then(ThenCaptureBuildInputsFromTheLocalRoot, "capture build inputs from the local root")
            .When(WhenApplyingTheExtraction, "applying the extraction")
            .Then(ThenCreateTheInterfaceAndUpdateTheSource, "create the interface and update the source")
            .BDDfy();

        async Task GivenTheSameSdkVersionInLocalAndHostRoots()
        {
            var sdkPath = fixture.SdkPath;
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

        async Task WhenPreviewingExtractionWithTheLocalSdk() => preview = await fixture.Preview(fixture.Extract);

        void ThenCaptureBuildInputsFromTheLocalRoot()
        {
            preview.Previewed();
            Assert.Contains(fixture.Plan().Inputs, input => Paths.Comparer.Equals(input.Path, fixture.PathFor(localSdk + "/Microsoft.Build.dll")));
        }

        async Task WhenApplyingTheExtraction() => applied = await fixture.Apply();

        void ThenCreateTheInterfaceAndUpdateTheSource()
        {
            applied.Applied();
            var created = CSharpSyntaxTree.ParseText(File.ReadAllText(fixture.Output)).GetRoot();
            var declaration = Assert.Single(created.DescendantNodes().OfType<InterfaceDeclarationSyntax>());
            Assert.Equal("ISelected", declaration.Identifier.ValueText);
            Assert.Contains("global::Contracts.ISelected", File.ReadAllText(fixture.Source));
        }
    }

    private static string BasePath(string info) => Path.TrimEndingDirectorySeparator(info.Split('\n')
        .Single(line => line.TrimStart().StartsWith("Base Path:", StringComparison.Ordinal)).Split(':', 2)[1].Trim());
}
