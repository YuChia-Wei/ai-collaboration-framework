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
    public Task DiscoversAllSevenTemplates() => Registration.AssertShortNames();

    /// <summary>Generates named C# items and runs a typed consumer of all three item shapes.</summary>
    [TemplateSdkFact]
    [Trait("Boundary", "Sdk")]
    public async Task GeneratedItemsCompileAndExecuteTogether()
    {
        const string itemNamespace = "Sample.Generated";
        var output = Path.Combine(Fixture.Root, "items");
        var project = Fixture.Write("items/Consumer.csproj", """
            <Project Sdk="Microsoft.NET.Sdk">
              <PropertyGroup>
                <TargetFramework>net10.0</TargetFramework>
                <OutputType>Exe</OutputType>
              </PropertyGroup>
            </Project>
            """);
        await Registration.Generate("aicf-class", "PackingNote", output, "--namespace", itemNamespace);
        await Registration.Generate("aicf-interface", "ILabelReader", output, "--namespace", itemNamespace);
        await Registration.Generate("aicf-usecase", "DescribeLabel", output, "--namespace", itemNamespace);
        Fixture.Write("items/Program.cs", """
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
        await Fixture.Build(project);
        var result = await Fixture.Dotnet(Path.Combine(output, "bin", "Debug", "net10.0", "Consumer.dll"));
        Assert.Equal("PackingNote|LabelReader|Fragile|7", result.Trim());
    }

    /// <summary>Builds the renamed Minimal API and follows its create response to the saved work item.</summary>
    [TemplateSdkFact]
    [Trait("Boundary", "Sdk")]
    public async Task GeneratedMinimalApiServesWorkItems()
    {
        const string name = "Sample.Warehouse";
        var output = Path.Combine(Fixture.Root, "miniapi");
        await Registration.Generate("aicf-miniapi", name, output);
        await Fixture.Build(Path.Combine(output, name + ".csproj"));
        await AssertWorkItemApi(output, name, "/work-items");
    }

    /// <summary>Builds the renamed layered solution and follows the controller's create response to the saved work item.</summary>
    [TemplateSdkFact]
    [Trait("Boundary", "Sdk")]
    public async Task GeneratedLayeredWebApiServesWorkItems()
    {
        const string name = "Sample.WarehouseApi";
        var output = Path.Combine(Fixture.Root, "webapi");
        await Registration.Generate("aicf-webapi", name, output);
        var solution = Path.Combine(output, name + ".slnx");
        AssertSolutionStructure(output, solution);
        await Fixture.Build(solution);
        await AssertWorkItemApi(Path.Combine(output, "WebApi"), name + ".WebApi", "/api/work-items");
    }

    /// <summary>Generates both renamed contract projects and verifies the explicit CT-005 DLL inputs.</summary>
    [TemplateSdkFact]
    [Trait("Boundary", "Sdk")]
    public async Task GeneratesBothContractProjectShapes()
    {
        var packageFree = Path.Combine(Fixture.Root, "package-free");
        await Registration.Generate("aicf-domain-contract-tests", "Sample.DomainContracts", packageFree);
        var packageFreeProject = ReadGeneratedProject(packageFree, "Sample.DomainContracts.csproj");
        Assert.Equal("net10.0", packageFreeProject.Descendants("TargetFramework").Single().Value);
        Assert.Empty(packageFreeProject.Descendants("Reference"));
        Assert.True(File.Exists(Path.Combine(packageFree, "PackageFreeContractTests.cs")));
        Assert.True(File.Exists(Path.Combine(packageFree, "fixtures", "Plan.cs")));

        var ct005 = Path.Combine(Fixture.Root, "published-ct005");
        await Registration.Generate("aicf-ct005-contract-tests", "Sample.Ct005Contracts", ct005);
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

    private async Task AssertWorkItemApi(string root, string name, string route)
    {
        var dll = Path.Combine(root, "bin", "Debug", "net10.0", name + ".dll");
        using var server = Fixture.Start(Fixture.DotnetExecutable, [dll, "--urls", "http://127.0.0.1:0"], root);
        var error = server.StandardError.ReadToEndAsync();
        Task<string>? output = null;
        try
        {
            using var startup = new CancellationTokenSource(TimeSpan.FromSeconds(20));
            const string listening = "Now listening on: ";
            string? origin = null;
            while (await server.StandardOutput.ReadLineAsync(startup.Token) is { } line)
            {
                var position = line.IndexOf(listening, StringComparison.Ordinal);
                if (position < 0)
                    continue;
                origin = line[(position + listening.Length)..].Trim();
                break;
            }
            output = server.StandardOutput.ReadToEndAsync();
            Assert.Matches(@"\Ahttp://127\.0\.0\.1:[1-9][0-9]*\z", origin ?? "");
            var address = new Uri(origin!);
            using var client = new HttpClient(new HttpClientHandler { AllowAutoRedirect = false, UseProxy = false })
            {
                BaseAddress = address,
                Timeout = TimeSpan.FromSeconds(10)
            };

            using var created = await client.PostAsJsonAsync(route, new { title = "  Count cartons  " });
            Assert.Equal(HttpStatusCode.Created, created.StatusCode);
            var body = await created.Content.ReadFromJsonAsync<JsonElement>();
            var id = body.GetProperty("id").GetGuid();
            Assert.NotEqual(Guid.Empty, id);
            Assert.Equal("Count cartons", body.GetProperty("title").GetString());
            var location = created.Headers.Location;
            Assert.NotNull(location);
            Assert.Equal(new Uri(address, $"{route}/{id:D}"), new Uri(address, location));

            using var saved = await client.GetAsync(location);
            Assert.Equal(HttpStatusCode.OK, saved.StatusCode);
            var savedBody = await saved.Content.ReadFromJsonAsync<JsonElement>();
            Assert.Equal(id, savedBody.GetProperty("id").GetGuid());
            Assert.Equal("Count cartons", savedBody.GetProperty("title").GetString());
        }
        finally
        {
            if (!server.HasExited)
                server.Kill(entireProcessTree: true);
            await server.WaitForExitAsync();
            await error;
            if (output is not null)
                await output;
        }
    }
}
