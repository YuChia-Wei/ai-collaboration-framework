using System.IO.Compression;
using System.Net;
using System.Net.Http.Json;
using System.Text.Json;
using System.Text.Json.Nodes;
using System.Xml.Linq;

using Generation.TestSupport;

namespace Generation.Templates.IntegrationTests;

[CollectionDefinition("Generation SDK", DisableParallelization = true)]
public sealed class GenerationSdkCollection;

[Collection("Generation SDK")]
public sealed class TemplateTests
{
    [TemplateSdkFact]
    [Trait("Boundary", "Sdk")]
    public void NativeTemplatesGenerateBuildAndServeBothApiShapesAndPreserveEdits()
    {
        using var fixture = new GenerationFixture();
        var hive = Path.Combine(fixture.Root, "hive");
        string[] NewCommand(params string[] command) => ["new", .. command, "--debug:custom-hive", hive];
        Task<string> Template(params string[] command) => fixture.Dotnet(NewCommand(command));
        const string itemNamespace = "Sample.Warehouse.Labels";
        string delivered = null!;
        string list = null!, help = null!;
        string mini = null!;
        string[] miniArgs = null!;
        string miniProject = null!;
        string web = null!;
        string solution = null!;
        string application = null!;
        string domain = null!;
        string custom = null!;
        string packingNote = null!;
        byte[] before = null!;
        (int Exit, string Output, string Error) collision = default;
        string installed = null!;

        this.Given(GivenAnIsolatedTemplateHiveAndSelectedDelivery, "an isolated template hive and selected delivery")
            .When(WhenInstallingAndDiscoveringTheDeliveredTemplates, "installing and discovering the delivered templates")
            .Then(ThenExposeTheExpectedTemplateNamesAndOptions, "expose the expected template names and options")
            .Given(GivenAMinimalApiOutputLocation, "a minimal api output location")
            .When(WhenDryRunningMinimalApiGeneration, "dry running minimal api generation")
            .Then(ThenLeaveTheOutputAbsent, "leave the output absent")
            .When(WhenGeneratingAndBuildingTheMinimalApi, "generating and building the minimal api")
            .Then(ThenServeTheMinimalApiContract, "serve the minimal api contract")
            .Given(GivenAWebApiOutputLocation, "a web api output location")
            .When(WhenGeneratingTheLayeredWebApi, "generating the layered web api")
            .Then(ThenPreserveTheLayeredProjectGraph, "preserve the layered project graph")
            .When(WhenBuildingTheLayeredApi, "building the layered api")
            .Then(ThenServeTheLayeredApiContract, "serve the layered api contract")
            .Given(GivenItemTemplateDestinationsAndANamespace, "item template destinations and a namespace")
            .When(WhenGeneratingTheThreeNativeItemKinds, "generating the three native item kinds")
            .Given(GivenAConsumerOfThoseItemsAndACustomizedTemplate, "a consumer of those items and a customized template")
            .When(WhenInstallingAndInstantiatingTheCustomizedTemplate, "installing and instantiating the customized template")
            .Then(ThenPreserveTheCustomMarkerAndNamespace, "preserve the custom marker and namespace")
            .When(WhenBuildingTheConsumerOfTheGeneratedItems, "building the consumer of the generated items")
            .Given(GivenAUserEditInTheGeneratedClass, "a user edit in the generated class")
            .When(WhenRegeneratingAtTheEditedDestination, "regenerating at the edited destination")
            .Then(ThenRefuseTheCollisionAndPreserveTheUserEdit, "refuse the collision and preserve the user edit")
            .When(WhenUninstallingBothTemplateDeliveries, "uninstalling both template deliveries")
            .Then(ThenRemoveBothShortNames, "remove both short names")
            .BDDfy();

        async Task GivenAnIsolatedTemplateHiveAndSelectedDelivery()
        {
            delivered = Path.Combine(fixture.Root, "delivered");
            if (TemplateSdkFactAttribute.Package is { } supplied)
            {
                var package = GenerationFixture.ExistingArtifact(supplied, "AICF_TEMPLATE_PACKAGE");
                await Template("install", package);
                var smoke = Path.Combine(fixture.Root, "package-smoke");
                await Template("aicf-class", "--name", "PackageNote", "--namespace", "Sample.Package", "--output", smoke);
                Assert.Contains("namespace Sample.Package", File.ReadAllText(Path.Combine(smoke, "PackageNote.cs")));
                await Template("uninstall", "AICF.Dotnet.Templates");
                var extraction = Path.Combine(fixture.Root, "package");
                ZipFile.ExtractToDirectory(package, extraction);
                delivered = Path.Combine(extraction, "content");
            }
            else
            {
                CopyTree(Path.Combine(AppContext.BaseDirectory, "native-templates"), delivered);
            }
        }

        async Task WhenInstallingAndDiscoveringTheDeliveredTemplates()
        {
            await Template("install", delivered);
            list = await Template("list", "aicf");
            help = await Template("aicf-usecase", "--help");
        }

        void ThenExposeTheExpectedTemplateNamesAndOptions()
        {
            foreach (var name in new[] { "aicf-miniapi", "aicf-webapi", "aicf-usecase", "aicf-class", "aicf-interface" })
                Assert.Contains(name, list);
            Assert.Contains("--namespace", help);
        }

        void GivenAMinimalApiOutputLocation()
        {
            mini = Path.Combine(fixture.Root, "Sample.Warehouse");
            miniArgs = ["aicf-miniapi", "--name", "Sample.Warehouse", "--output", mini];
        }

        async Task WhenDryRunningMinimalApiGeneration() => await Template([.. miniArgs, "--dry-run"]);

        void ThenLeaveTheOutputAbsent() => Assert.False(Directory.Exists(mini));

        async Task WhenGeneratingAndBuildingTheMinimalApi()
        {
            await Template(miniArgs);
            miniProject = Path.Combine(mini, "Sample.Warehouse.csproj");
            await fixture.Build(miniProject);
        }

        async Task ThenServeTheMinimalApiContract() => await AssertWorkItemApi(fixture, mini, "Sample.Warehouse", "/work-items");

        void GivenAWebApiOutputLocation()
        {
            web = Path.Combine(fixture.Root, "Sample.WarehouseApi");
        }

        async Task WhenGeneratingTheLayeredWebApi() => await Template("aicf-webapi", "--name", "Sample.WarehouseApi", "--output", web);

        void ThenPreserveTheLayeredProjectGraph()
        {
            solution = Path.Combine(web, "Sample.WarehouseApi.slnx");
            AssertSolutionStructure(web, solution);
        }

        async Task WhenBuildingTheLayeredApi() => await fixture.Build(solution);

        async Task ThenServeTheLayeredApiContract() => await AssertWorkItemApi(fixture, Path.Combine(web, "WebApi"), "Sample.WarehouseApi.WebApi", "/api/work-items");

        void GivenItemTemplateDestinationsAndANamespace()
        {
            application = Path.Combine(mini, "Application");
            domain = Path.Combine(mini, "Domain");
        }

        async Task WhenGeneratingTheThreeNativeItemKinds()
        {
            await Template("aicf-usecase", "--name", "DescribeLabel", "--namespace", itemNamespace, "--output", application);
            await Template("aicf-class", "--name", "PackingNote", "--namespace", itemNamespace, "--output", domain);
            await Template("aicf-interface", "--name", "ILabelReader", "--namespace", itemNamespace, "--output", application);
        }

        void GivenAConsumerOfThoseItemsAndACustomizedTemplate()
        {
            fixture.Write("Sample.Warehouse/GeneratedItemReferences.cs", """
                global using Sample.Warehouse.Labels;

                namespace Sample.Warehouse;

                internal sealed class GeneratedItemReferences(
                    IDescribeLabelUseCase useCase, PackingNote note, ILabelReader reader)
                {
                    public IDescribeLabelUseCase UseCase { get; } = useCase;
                    public PackingNote Note { get; } = note;
                    public ILabelReader Reader { get; } = reader;
                }
                """);

            custom = Path.Combine(fixture.Root, "custom-class");
            CopyTree(Path.Combine(delivered, "class"), custom);
            var config = Path.Combine(custom, ".template.config", "template.json");
            var metadata = JsonNode.Parse(File.ReadAllText(config))!.AsObject();
            metadata["identity"] = "Example.Warehouse.CustomClass.1";
            metadata["name"] = "Warehouse custom class";
            metadata["shortName"] = "warehouse-class";
            File.WriteAllText(config, metadata.ToJsonString());
            File.AppendAllText(Path.Combine(custom, "AicfClass.cs"), "\n// Warehouse custom marker\n");
        }

        async Task WhenInstallingAndInstantiatingTheCustomizedTemplate()
        {
            await Template("install", custom);
            await Template("warehouse-class", "--name", "DeliveryNote", "--namespace", itemNamespace, "--output", domain);
        }

        void ThenPreserveTheCustomMarkerAndNamespace()
        {
            var generated = File.ReadAllText(Path.Combine(domain, "DeliveryNote.cs"));
            Assert.Contains("// Warehouse custom marker", generated);
            Assert.Contains("namespace Sample.Warehouse.Labels", generated);
        }

        async Task WhenBuildingTheConsumerOfTheGeneratedItems() => await fixture.Build(miniProject);

        void GivenAUserEditInTheGeneratedClass()
        {
            packingNote = Path.Combine(domain, "PackingNote.cs");
            File.AppendAllText(packingNote, "\n// Target-owned edit\n");
            before = File.ReadAllBytes(packingNote);
        }

        async Task WhenRegeneratingAtTheEditedDestination()
        {
            collision = await fixture.Execute("dotnet", TimeSpan.FromMinutes(2),
                NewCommand("aicf-class", "--name", "PackingNote", "--namespace", itemNamespace, "--output", domain));
        }

        void ThenRefuseTheCollisionAndPreserveTheUserEdit()
        {
            Assert.NotEqual(0, collision.Exit);
            Assert.Equal(before, File.ReadAllBytes(packingNote));
        }

        async Task WhenUninstallingBothTemplateDeliveries()
        {
            await Template("uninstall", delivered, custom);
            installed = await Template("uninstall");
        }

        void ThenRemoveBothShortNames()
        {
            Assert.DoesNotContain("warehouse-class", installed);
            Assert.DoesNotContain("aicf-class", installed);
        }
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
            var actual = XDocument.Load(Path.Combine(root, path)).Descendants("ProjectReference").Select(p => (string)p.Attribute("Include")!);
            Assert.Equal(references.Order(StringComparer.Ordinal), actual.Order(StringComparer.Ordinal));
        }
        Assert.Equal(Path.Combine(root, "WebApi", "Program.cs"),
            Assert.Single(Directory.GetFiles(root, "Program.cs", SearchOption.AllDirectories)));
    }

    private static async Task AssertWorkItemApi(GenerationFixture fixture, string root, string name, string route)
    {
        var dll = Path.Combine(root, "bin", "Debug", "net10.0", name + ".dll");
        using var server = fixture.Start("dotnet", [dll, "--urls", "http://127.0.0.1:0"], root);
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
            if (origin is null)
                Assert.Fail("Backend did not report a listening address.");
            Assert.Matches(@"\Ahttp://127\.0\.0\.1:[1-9][0-9]*\z", origin);
            output = server.StandardOutput.ReadToEndAsync();
            using var client = new HttpClient { BaseAddress = new Uri(origin), Timeout = TimeSpan.FromSeconds(10) };

            using var created = await client.PostAsJsonAsync(route, new { title = "  Count cartons  " });
            Assert.Equal(HttpStatusCode.Created, created.StatusCode);
            var body = await created.Content.ReadFromJsonAsync<JsonElement>();
            Assert.Equal("Count cartons", body.GetProperty("title").GetString());
            var id = body.GetProperty("id").GetGuid();
            Assert.NotEqual(Guid.Empty, id);
            var location = created.Headers.Location;
            Assert.NotNull(location);
            Assert.EndsWith($"{route}/{id:D}", location.ToString(), StringComparison.Ordinal);

            var saved = await client.GetFromJsonAsync<JsonElement>(location);
            Assert.Equal(id, saved.GetProperty("id").GetGuid());
            Assert.Equal("Count cartons", saved.GetProperty("title").GetString());
            using var invalid = await client.PostAsJsonAsync(route, new { title = "   " });
            Assert.Equal(HttpStatusCode.BadRequest, invalid.StatusCode);
            using var missing = await client.GetAsync($"{route}/{Guid.Empty:D}");
            Assert.Equal(HttpStatusCode.NotFound, missing.StatusCode);
            using var home = await client.GetAsync("/");
            Assert.Equal(HttpStatusCode.NotFound, home.StatusCode);
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

    private static void CopyTree(string source, string target)
    {
        Directory.CreateDirectory(target);
        foreach (var file in Directory.EnumerateFiles(source))
            File.Copy(file, Path.Combine(target, Path.GetFileName(file)));
        foreach (var directory in Directory.EnumerateDirectories(source))
            CopyTree(directory, Path.Combine(target, Path.GetFileName(directory)));
    }
}
