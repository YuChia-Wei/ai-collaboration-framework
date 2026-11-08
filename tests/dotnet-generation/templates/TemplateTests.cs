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
        string? suppliedPackage = null, packageClass = null;
        string delivered = null!;
        string list = null!, help = null!;
        string mini = null!;
        string[] miniArgs = null!;
        string web = null!;
        string solution = null!;
        string application = null!;
        string domain = null!;
        string custom = null!;
        string packingNote = null!;
        byte[] before = null!;
        (int Exit, string Output, string Error) collision = default;
        string installed = null!;
        WorkItemApiResult miniApi = null!, webApi = null!;

        this.Given(GivenAnIsolatedTemplateHiveAndSelectedDelivery, "an isolated template hive and selected delivery")
            .When(WhenInstallingAndInstantiatingTheSuppliedPackage, "installing and instantiating the supplied package")
            .Then(ThenGenerateTheExpectedClassFromTheSuppliedPackage, "generate the expected class from the supplied package")
            .Given(GivenTheSelectedTemplateContent, "the selected template content")
            .When(WhenInstallingAndDiscoveringTheDeliveredTemplates, "installing and discovering the delivered templates")
            .Then(ThenExposeTheExpectedTemplateNamesAndOptions, "expose the expected template names and options")
            .Given(GivenAMinimalApiOutputLocation, "a minimal api output location")
            .When(WhenDryRunningMinimalApiGeneration, "dry running minimal api generation")
            .Then(ThenLeaveTheOutputAbsent, "leave the output absent")
            .When(WhenGeneratingTheMinimalApi, "generating the minimal api")
            .Given(GivenItemTemplateDestinationsAndANamespace, "item template destinations and a namespace")
            .When(WhenGeneratingTheThreeNativeItemKinds, "generating the three native item kinds")
            .Given(GivenAConsumerOfThoseItemsAndACustomizedTemplate, "a consumer of those items and a customized template")
            .When(WhenInstallingAndInstantiatingTheCustomizedTemplate, "installing and instantiating the customized template")
            .Then(ThenPreserveTheCustomMarkerAndNamespace, "preserve the custom marker and namespace")
            .When(WhenBuildingAndRequestingTheMinimalApi, "building and requesting the minimal api")
            .Then(ThenServeTheMinimalApiContract, "serve the minimal api contract")
            .Given(GivenAWebApiOutputLocation, "a web api output location")
            .When(WhenGeneratingTheLayeredWebApi, "generating the layered web api")
            .Then(ThenPreserveTheLayeredProjectGraph, "preserve the layered project graph")
            .When(WhenBuildingAndRequestingTheLayeredApi, "building and requesting the layered api")
            .Then(ThenServeTheLayeredApiContract, "serve the layered api contract")
            .Given(GivenAUserEditInTheGeneratedClass, "a user edit in the generated class")
            .When(WhenRegeneratingAtTheEditedDestination, "regenerating at the edited destination")
            .Then(ThenRefuseTheCollisionAndPreserveTheUserEdit, "refuse the collision and preserve the user edit")
            .When(WhenUninstallingBothTemplateDeliveries, "uninstalling both template deliveries")
            .Then(ThenRemoveBothShortNames, "remove both short names")
            .BDDfy();

        void GivenAnIsolatedTemplateHiveAndSelectedDelivery()
        {
            if (TemplateSdkFactAttribute.Package is { } supplied)
                suppliedPackage = GenerationFixture.ExistingArtifact(supplied, "AICF_TEMPLATE_PACKAGE");
        }

        async Task WhenInstallingAndInstantiatingTheSuppliedPackage()
        {
            if (suppliedPackage is null)
                return;

            await Template("install", suppliedPackage);
            var smoke = Path.Combine(fixture.Root, "package-smoke");
            await Template("aicf-class", "--name", "PackageNote", "--namespace", "Sample.Package", "--output", smoke);
            packageClass = File.ReadAllText(Path.Combine(smoke, "PackageNote.cs"));
            await Template("uninstall", "AICF.DotNet.Templates");
        }

        void ThenGenerateTheExpectedClassFromTheSuppliedPackage()
        {
            if (suppliedPackage is not null)
                Assert.Contains("namespace Sample.Package", Assert.IsType<string>(packageClass));
        }

        void GivenTheSelectedTemplateContent()
        {
            if (suppliedPackage is not null)
            {
                var extraction = Path.Combine(fixture.Root, "package");
                ZipFile.ExtractToDirectory(suppliedPackage, extraction);
                delivered = Path.Combine(extraction, "content");
            }
            else
            {
                delivered = Path.Combine(fixture.Root, "delivered");
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

        async Task WhenGeneratingTheMinimalApi() => await Template(miniArgs);

        async Task WhenBuildingAndRequestingTheMinimalApi()
        {
            await fixture.Build(Path.Combine(mini, "Sample.Warehouse.csproj"));
            miniApi = await RequestWorkItemApi(fixture, mini, "Sample.Warehouse", "/work-items");
        }

        void ThenServeTheMinimalApiContract() => AssertWorkItemApi(miniApi, "/work-items");

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

        async Task WhenBuildingAndRequestingTheLayeredApi()
        {
            await fixture.Build(solution);
            webApi = await RequestWorkItemApi(fixture, Path.Combine(web, "WebApi"), "Sample.WarehouseApi.WebApi", "/api/work-items");
        }

        void ThenServeTheLayeredApiContract() => AssertWorkItemApi(webApi, "/api/work-items");

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

    private static async Task<WorkItemApiResult> RequestWorkItemApi(GenerationFixture fixture, string root, string name, string route)
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
            if (!Uri.TryCreate(origin, UriKind.Absolute, out var address) ||
                address.Scheme != Uri.UriSchemeHttp || address.Host != "127.0.0.1")
                throw new InvalidOperationException("Backend did not report an IPv4 loopback HTTP address.");
            output = server.StandardOutput.ReadToEndAsync();
            using var client = new HttpClient(new HttpClientHandler { AllowAutoRedirect = false, UseProxy = false })
            {
                BaseAddress = address,
                Timeout = TimeSpan.FromSeconds(10)
            };

            using var created = await client.PostAsJsonAsync(route, new { title = "  Count cartons  " });
            var body = created.IsSuccessStatusCode ? await created.Content.ReadFromJsonAsync<JsonElement>() : default;
            var location = created.Headers.Location;
            Guid? createdId = created.StatusCode == HttpStatusCode.Created &&
                body.ValueKind == JsonValueKind.Object && body.TryGetProperty("id", out var id) &&
                id.ValueKind == JsonValueKind.String && id.TryGetGuid(out var parsedId) ? parsedId : null;
            using var saved = createdId is { } itemId ? await client.GetAsync($"{route}/{itemId:D}") : null;
            var savedBody = saved is { IsSuccessStatusCode: true }
                ? await saved.Content.ReadFromJsonAsync<JsonElement>() : default;
            using var invalid = await client.PostAsJsonAsync(route, new { title = "   " });
            using var missing = await client.GetAsync($"{route}/{Guid.Empty:D}");
            using var home = await client.GetAsync("/");
            return new(address.OriginalString, created.StatusCode, body, location, saved?.StatusCode, savedBody,
                invalid.StatusCode, missing.StatusCode, home.StatusCode);
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

    private static void AssertWorkItemApi(WorkItemApiResult result, string route)
    {
        Assert.Matches(@"\Ahttp://127\.0\.0\.1:[1-9][0-9]*\z", result.Origin);
        Assert.Equal(HttpStatusCode.Created, result.CreatedStatus);
        Assert.Equal("Count cartons", result.CreatedBody.GetProperty("title").GetString());
        var id = result.CreatedBody.GetProperty("id").GetGuid();
        Assert.NotEqual(Guid.Empty, id);
        Assert.NotNull(result.Location);
        var origin = new Uri(result.Origin);
        Assert.Equal(new Uri(origin, $"{route}/{id:D}").AbsoluteUri, new Uri(origin, result.Location).AbsoluteUri);
        Assert.Equal(HttpStatusCode.OK, result.SavedStatus);
        Assert.Equal(id, result.SavedBody.GetProperty("id").GetGuid());
        Assert.Equal("Count cartons", result.SavedBody.GetProperty("title").GetString());
        Assert.Equal(HttpStatusCode.BadRequest, result.InvalidStatus);
        Assert.Equal(HttpStatusCode.NotFound, result.MissingStatus);
        Assert.Equal(HttpStatusCode.NotFound, result.HomeStatus);
    }

    private sealed record WorkItemApiResult(string Origin, HttpStatusCode CreatedStatus, JsonElement CreatedBody,
        Uri? Location, HttpStatusCode? SavedStatus, JsonElement SavedBody,
        HttpStatusCode InvalidStatus, HttpStatusCode MissingStatus, HttpStatusCode HomeStatus);

    private static void CopyTree(string source, string target)
    {
        Directory.CreateDirectory(target);
        foreach (var file in Directory.EnumerateFiles(source))
            File.Copy(file, Path.Combine(target, Path.GetFileName(file)));
        foreach (var directory in Directory.EnumerateDirectories(source))
            CopyTree(directory, Path.Combine(target, Path.GetFileName(directory)));
    }
}
