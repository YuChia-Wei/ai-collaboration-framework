using System.Diagnostics;
using System.Net;
using System.Net.Http.Json;
using System.Text.Json;
using System.Xml.Linq;
using Generation.TestSupport;

namespace Generation.Templates.IntegrationTests;

public sealed class TemplateSourceFixture : IAsyncLifetime
{
    private TemplateRegistration? registration;
    internal TemplateRegistration Registration => registration!;

    public async Task InitializeAsync()
    {
        registration = new TemplateRegistration();
        await registration.Install(Path.Combine(AppContext.BaseDirectory, "native-templates"));
    }

    public Task DisposeAsync()
    {
        registration?.Dispose();
        return Task.CompletedTask;
    }
}

public sealed class TemplateTests(TemplateSourceFixture source) : IClassFixture<TemplateSourceFixture>
{
    private TemplateRegistration Registration => source.Registration;
    private GenerationFixture Fixture => Registration.Fixture;

    /// <summary>Discovers all seven short names from the canonical source directory.</summary>
    [TemplateSdkFact]
    [Trait("Boundary", "Sdk")]
    public void DiscoversAllSevenTemplates()
    {
        string hive = null!;
        string listing = null!;

        this.Given(GivenCanonicalTemplatesRegisteredInTheIsolatedHive, "canonical templates registered in the isolated hive")
            .When(WhenListingTheRegisteredTemplates, "listing the registered templates")
            .Then(ThenListExactlyTheSevenTemplateShortNames, "list exactly the seven template short names")
            .BDDfy();

        void GivenCanonicalTemplatesRegisteredInTheIsolatedHive() => hive = Path.Combine(Fixture.Root, "hive");

        async Task WhenListingTheRegisteredTemplates() =>
            listing = await Fixture.Dotnet("new", "list", "aicf", "--debug:custom-hive", hive);

        void ThenListExactlyTheSevenTemplateShortNames()
        {
            string[] expected =
            [
                "aicf-class", "aicf-ct005-contract-tests", "aicf-domain-contract-tests",
                "aicf-interface", "aicf-miniapi", "aicf-usecase", "aicf-webapi"
            ];
            var actual = listing.Split((char[]?)null, StringSplitOptions.RemoveEmptyEntries)
                .Where(word => word.StartsWith("aicf-", StringComparison.Ordinal))
                .Order(StringComparer.Ordinal);
            Assert.Equal(expected, actual);
        }
    }

    /// <summary>Generates named C# items and runs a typed consumer of all three item shapes.</summary>
    [TemplateSdkFact]
    [Trait("Boundary", "Sdk")]
    public void GeneratedItemsCompileAndExecuteTogether()
    {
        const string itemNamespace = "Sample.Generated";
        var output = Path.Combine(Fixture.Root, "items");
        string project = null!;
        string result = null!;

        this.Given(GivenAnExecutableConsumerProject, "an executable consumer project")
            .When(WhenGeneratingTheThreeNamedItems, "generating the three named items")
            .Given(GivenAConsumerOfTheGeneratedItems, "a consumer of the generated items")
            .When(WhenBuildingAndRunningTheConsumer, "building and running the consumer")
            .Then(ThenUseAllThreeItemsAndReturnTheTrimmedLabel, "use all three items and return the trimmed label")
            .BDDfy();

        void GivenAnExecutableConsumerProject() => project = Fixture.Write("items/Consumer.csproj", """
            <Project Sdk="Microsoft.NET.Sdk">
              <PropertyGroup>
                <TargetFramework>net10.0</TargetFramework>
                <OutputType>Exe</OutputType>
              </PropertyGroup>
            </Project>
            """);

        async Task WhenGeneratingTheThreeNamedItems()
        {
            await Registration.Generate("aicf-class", "PackingNote", output, "--namespace", itemNamespace);
            await Registration.Generate("aicf-interface", "ILabelReader", output, "--namespace", itemNamespace);
            await Registration.Generate("aicf-usecase", "DescribeLabel", output, "--namespace", itemNamespace);
        }

        void GivenAConsumerOfTheGeneratedItems() => Fixture.Write("items/Program.cs", """
            using System;
            using System.Threading;
            using Sample.Generated;

            PackingNote note = new();
            ILabelReader reader = new LabelReader();
            IDescribeLabelUseCase useCase = new DescribeLabelUseCase();
            var result = await useCase.ExecuteAsync(new DescribeLabelInput("  Fragile  "), CancellationToken.None);
            Console.WriteLine($"{note.GetType().Name}|{reader.GetType().Name}|{result.Text}|{result.Length}");

            sealed class LabelReader : ILabelReader;
            """);

        async Task WhenBuildingAndRunningTheConsumer()
        {
            await Fixture.Build(project);
            result = await Fixture.Dotnet(Path.Combine(output, "bin", "Debug", "net10.0", "Consumer.dll"));
        }

        void ThenUseAllThreeItemsAndReturnTheTrimmedLabel() => Assert.Equal("PackingNote|LabelReader|Fragile|7", result.Trim());
    }

    /// <summary>Builds the renamed Minimal API and follows its create response to the saved work item.</summary>
    [TemplateSdkFact]
    [Trait("Boundary", "Sdk")]
    public async Task GeneratedMinimalApiServesWorkItems()
    {
        const string name = "Sample.Warehouse";
        string output = null!;
        await using var api = new WorkItemApiProbe(Fixture, "/work-items");

        this.Given(GivenADestinationForTheNamedMinimalApi, "a destination for the named Minimal API")
            .When(WhenGeneratingTheMinimalApi, "generating the Minimal API")
            .When(WhenBuildingAndStartingTheMinimalApi, "building and starting the Minimal API")
            .Then(api.ThenListenOnIpv4Loopback, "listen on IPv4 loopback")
            .When(api.WhenPostingTheWorkItem, "posting the work item")
            .Then(api.ThenReturnTheCreatedWorkItemAndItsLocation, "return the created work item and its location")
            .When(api.WhenFollowingTheCreatedLocation, "following the created location")
            .Then(api.ThenReturnTheSavedWorkItem, "return the saved work item")
            .BDDfy();

        void GivenADestinationForTheNamedMinimalApi() => output = Path.Combine(Fixture.Root, "miniapi");

        Task WhenGeneratingTheMinimalApi() => Registration.Generate("aicf-miniapi", name, output);

        async Task WhenBuildingAndStartingTheMinimalApi()
        {
            await Fixture.Build(Path.Combine(output, name + ".csproj"));
            await api.Start(output, name);
        }
    }

    /// <summary>Builds the renamed layered solution and follows the controller's create response to the saved work item.</summary>
    [TemplateSdkFact]
    [Trait("Boundary", "Sdk")]
    public async Task GeneratedLayeredWebApiServesWorkItems()
    {
        const string name = "Sample.WarehouseApi";
        string output = null!;
        string solution = null!;
        await using var api = new WorkItemApiProbe(Fixture, "/api/work-items");

        this.Given(GivenADestinationForTheNamedLayeredApi, "a destination for the named layered API")
            .When(WhenGeneratingTheLayeredApi, "generating the layered API")
            .Then(ThenPreserveTheLayeredSolutionAndProjectReferences, "preserve the layered solution and project references")
            .When(WhenBuildingAndStartingTheLayeredApi, "building and starting the layered API")
            .Then(api.ThenListenOnIpv4Loopback, "listen on IPv4 loopback")
            .When(api.WhenPostingTheWorkItem, "posting the work item")
            .Then(api.ThenReturnTheCreatedWorkItemAndItsLocation, "return the created work item and its location")
            .When(api.WhenFollowingTheCreatedLocation, "following the created location")
            .Then(api.ThenReturnTheSavedWorkItem, "return the saved work item")
            .BDDfy();

        void GivenADestinationForTheNamedLayeredApi()
        {
            output = Path.Combine(Fixture.Root, "webapi");
            solution = Path.Combine(output, name + ".slnx");
        }

        Task WhenGeneratingTheLayeredApi() => Registration.Generate("aicf-webapi", name, output);

        void ThenPreserveTheLayeredSolutionAndProjectReferences() => AssertSolutionStructure(output, solution);

        async Task WhenBuildingAndStartingTheLayeredApi()
        {
            await Fixture.Build(solution);
            await api.Start(Path.Combine(output, "WebApi"), name + ".WebApi");
        }
    }

    /// <summary>Generates both renamed contract projects and verifies the explicit CT-005 DLL inputs.</summary>
    [TemplateSdkFact]
    [Trait("Boundary", "Sdk")]
    public void GeneratesBothContractProjectShapes()
    {
        string packageFree = null!;
        string ct005 = null!;

        this.Given(GivenADestinationForThePackageFreeProject, "a destination for the package-free project")
            .When(WhenGeneratingThePackageFreeProject, "generating the package-free project")
            .Then(ThenTargetNet10WithoutExternalReferences, "target .NET 10 without external references")
            .Given(GivenADestinationForTheCt005Project, "a destination for the CT-005 project")
            .When(WhenGeneratingTheCt005Project, "generating the CT-005 project")
            .Then(ThenTargetNet8AndRequireBothPublishedDlls, "target .NET 8 and require both published DLLs")
            .BDDfy();

        void GivenADestinationForThePackageFreeProject() => packageFree = Path.Combine(Fixture.Root, "package-free");

        Task WhenGeneratingThePackageFreeProject() =>
            Registration.Generate("aicf-domain-contract-tests", "Sample.DomainContracts", packageFree);

        void ThenTargetNet10WithoutExternalReferences()
        {
            var packageFreeProject = ReadGeneratedProject(packageFree, "Sample.DomainContracts.csproj");
            Assert.Equal("net10.0", packageFreeProject.Descendants("TargetFramework").Single().Value);
            Assert.Empty(packageFreeProject.Descendants("Reference"));
            Assert.True(File.Exists(Path.Combine(packageFree, "PackageFreeContractTests.cs")));
            Assert.True(File.Exists(Path.Combine(packageFree, "fixtures", "Plan.cs")));
        }

        void GivenADestinationForTheCt005Project() => ct005 = Path.Combine(Fixture.Root, "published-ct005");

        Task WhenGeneratingTheCt005Project() =>
            Registration.Generate("aicf-ct005-contract-tests", "Sample.Ct005Contracts", ct005);

        void ThenTargetNet8AndRequireBothPublishedDlls()
        {
            var ct005Project = ReadGeneratedProject(ct005, "Sample.Ct005Contracts.csproj");
            Assert.Equal("net8.0", ct005Project.Descendants("TargetFramework").Single().Value);
            Assert.Equal(new[]
                {
                    "$(PublishedContractsDir)/domain/lib/net8.0/ArchPrecept.Contracts.Domain.dll",
                    "$(PublishedContractsDir)/eventsourcing/lib/net8.0/ArchPrecept.Contracts.Domain.EventSourcing.dll"
                },
                ct005Project.Descendants("HintPath").Select(path => path.Value).Order(StringComparer.Ordinal));
            Assert.Contains(ct005Project.Descendants("Error"),
                error => (string?)error.Attribute("Condition") == "'$(PublishedContractsDir)' == ''");
            Assert.True(File.Exists(Path.Combine(ct005, "PublishedContractTests.cs")));
        }
    }

    private static XDocument ReadGeneratedProject(string output, string name)
    {
        Assert.Equal(name, Path.GetFileName(Assert.Single(Directory.GetFiles(output, "*.csproj"))));
        Assert.Empty(Directory.GetFiles(output, "*.csproj.template", SearchOption.AllDirectories));
        return XDocument.Load(Path.Combine(output, name));
    }

    private static void AssertSolutionStructure(string root, string solution)
    {
        var expected = new Dictionary<string, string[]>
        {
            ["Domain/Sample.WarehouseApi.Domain.csproj"] = [],
            ["Application/Sample.WarehouseApi.Application.csproj"] = ["../Domain/Sample.WarehouseApi.Domain.csproj"],
            ["Infrastructure/Sample.WarehouseApi.Infrastructure.csproj"] = ["../Application/Sample.WarehouseApi.Application.csproj"],
            ["WebApi/Sample.WarehouseApi.WebApi.csproj"] =
                ["../Application/Sample.WarehouseApi.Application.csproj", "../Infrastructure/Sample.WarehouseApi.Infrastructure.csproj"]
        };
        var members = XDocument.Load(solution).Root!.Elements("Project").Select(p => (string)p.Attribute("Path")!);
        Assert.Equal(expected.Keys.Order(StringComparer.Ordinal), members.Order(StringComparer.Ordinal));
        foreach (var (path, references) in expected)
        {
            var actual = XDocument.Load(Path.Combine(root, path)).Descendants("ProjectReference")
                .Select(p => (string)p.Attribute("Include")!);
            Assert.Equal(references.Order(StringComparer.Ordinal), actual.Order(StringComparer.Ordinal));
        }
        Assert.Equal(Path.Combine(root, "WebApi", "Program.cs"),
            Assert.Single(Directory.GetFiles(root, "Program.cs", SearchOption.AllDirectories)));
    }

    private sealed class WorkItemApiProbe(GenerationFixture fixture, string route) : IAsyncDisposable
    {
        private Process? server;
        private Task<string>? error;
        private Task<string>? output;
        private HttpClient client = null!;
        private HttpResponseMessage created = null!, saved = null!;
        private string? origin;
        private Uri? validatedLocation;
        private Guid id;

        public async Task Start(string root, string name)
        {
            var dll = Path.Combine(root, "bin", "Debug", "net10.0", name + ".dll");
            server = fixture.Start(fixture.DotnetExecutable, [dll, "--urls", "http://127.0.0.1:0"], root);
            error = server.StandardError.ReadToEndAsync();
            using var startup = new CancellationTokenSource(TimeSpan.FromSeconds(20));
            const string listening = "Now listening on: ";
            while (await server.StandardOutput.ReadLineAsync(startup.Token) is { } line)
            {
                var position = line.IndexOf(listening, StringComparison.Ordinal);
                if (position < 0)
                    continue;
                origin = line[(position + listening.Length)..].Trim();
                break;
            }
            output = server.StandardOutput.ReadToEndAsync();
        }

        public void ThenListenOnIpv4Loopback() => Assert.Matches(@"\Ahttp://127\.0\.0\.1:[1-9][0-9]*\z", origin ?? "");

        public async Task WhenPostingTheWorkItem()
        {
            client = new HttpClient(new HttpClientHandler { AllowAutoRedirect = false, UseProxy = false })
            {
                BaseAddress = new Uri(origin!),
                Timeout = TimeSpan.FromSeconds(10)
            };
            created = await client.PostAsJsonAsync(route, new { title = "  Count cartons  " });
        }

        public async Task ThenReturnTheCreatedWorkItemAndItsLocation()
        {
            Assert.Equal(HttpStatusCode.Created, created.StatusCode);
            var body = await created.Content.ReadFromJsonAsync<JsonElement>();
            id = body.GetProperty("id").GetGuid();
            Assert.NotEqual(Guid.Empty, id);
            Assert.Equal("Count cartons", body.GetProperty("title").GetString());
            var location = created.Headers.Location;
            Assert.NotNull(location);
            var address = client.BaseAddress!;
            Assert.Equal(new Uri(address, $"{route}/{id:D}"), new Uri(address, location));
            validatedLocation = location;
        }

        public async Task WhenFollowingTheCreatedLocation() =>
            saved = await client.GetAsync(validatedLocation ?? throw new InvalidOperationException("The create response did not provide a validated location."));

        public async Task ThenReturnTheSavedWorkItem()
        {
            Assert.Equal(HttpStatusCode.OK, saved.StatusCode);
            var savedBody = await saved.Content.ReadFromJsonAsync<JsonElement>();
            Assert.Equal(id, savedBody.GetProperty("id").GetGuid());
            Assert.Equal("Count cartons", savedBody.GetProperty("title").GetString());
        }

        public async ValueTask DisposeAsync()
        {
            saved?.Dispose();
            created?.Dispose();
            client?.Dispose();
            using var runningServer = server;
            if (runningServer is null)
                return;
            if (!runningServer.HasExited)
                runningServer.Kill(entireProcessTree: true);
            await runningServer.WaitForExitAsync();
            if (error is not null)
                await error;
            if (output is not null)
                await output;
        }
    }
}
