using System.IO.Compression;
using System.Net;
using System.Net.Http.Json;
using System.Text.Json;
using System.Text.Json.Nodes;
using System.Xml.Linq;

namespace Generation.Tests;

[CollectionDefinition("Generation SDK", DisableParallelization = true)]
public sealed class GenerationSdkCollection;

[Collection("Generation SDK")]
public sealed class TemplateTests
{
    [GenerationSdkFact]
    [Trait("Boundary", "Sdk")]
    public async Task NativeTemplatesGenerateBuildAndServeBothApiShapesAndPreserveEdits()
    {
        using var fixture = new GenerationFixture();
        var hive = Path.Combine(fixture.Root, "hive");
        string[] NewCommand(params string[] command) => ["new", .. command, "--debug:custom-hive", hive];
        Task<string> Template(params string[] command) => fixture.Dotnet(NewCommand(command));
        var delivered = Path.Combine(fixture.Root, "delivered");
        if (GenerationFixture.TemplatePackage is { } supplied)
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

        await Template("install", delivered);
        var list = await Template("list", "aicf");
        foreach (var name in new[] { "aicf-miniapi", "aicf-webapi", "aicf-usecase", "aicf-class", "aicf-interface" })
            Assert.Contains(name, list);
        Assert.Contains("--namespace", await Template("aicf-usecase", "--help"));

        var mini = Path.Combine(fixture.Root, "Sample.Warehouse");
        string[] miniArgs = ["aicf-miniapi", "--name", "Sample.Warehouse", "--output", mini];
        await Template([.. miniArgs, "--dry-run"]);
        Assert.False(Directory.Exists(mini));
        await Template(miniArgs);
        var miniProject = Path.Combine(mini, "Sample.Warehouse.csproj");
        await fixture.Build(miniProject);
        await AssertWorkItemApi(fixture, mini, "Sample.Warehouse", "/work-items");

        var web = Path.Combine(fixture.Root, "Sample.WarehouseApi");
        await Template("aicf-webapi", "--name", "Sample.WarehouseApi", "--output", web);
        var solution = Path.Combine(web, "Sample.WarehouseApi.slnx");
        AssertSolutionStructure(web, solution);
        await fixture.Build(solution);
        await AssertWorkItemApi(fixture, Path.Combine(web, "WebApi"), "Sample.WarehouseApi.WebApi", "/api/work-items");

        var application = Path.Combine(mini, "Application");
        var domain = Path.Combine(mini, "Domain");
        const string itemNamespace = "Sample.Warehouse.Labels";
        await Template("aicf-usecase", "--name", "DescribeLabel", "--namespace", itemNamespace, "--output", application);
        await Template("aicf-class", "--name", "PackingNote", "--namespace", itemNamespace, "--output", domain);
        await Template("aicf-interface", "--name", "ILabelReader", "--namespace", itemNamespace, "--output", application);
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

        var custom = Path.Combine(fixture.Root, "custom-class");
        CopyTree(Path.Combine(delivered, "class"), custom);
        var config = Path.Combine(custom, ".template.config", "template.json");
        var metadata = JsonNode.Parse(File.ReadAllText(config))!.AsObject();
        metadata["identity"] = "Example.Warehouse.CustomClass.1";
        metadata["name"] = "Warehouse custom class";
        metadata["shortName"] = "warehouse-class";
        File.WriteAllText(config, metadata.ToJsonString());
        File.AppendAllText(Path.Combine(custom, "AicfClass.cs"), "\n// Warehouse custom marker\n");
        await Template("install", custom);
        await Template("warehouse-class", "--name", "DeliveryNote", "--namespace", itemNamespace, "--output", domain);
        var generated = File.ReadAllText(Path.Combine(domain, "DeliveryNote.cs"));
        Assert.Contains("// Warehouse custom marker", generated);
        Assert.Contains("namespace Sample.Warehouse.Labels", generated);
        await fixture.Build(miniProject);

        var packingNote = Path.Combine(domain, "PackingNote.cs");
        File.AppendAllText(packingNote, "\n// Target-owned edit\n");
        var before = File.ReadAllBytes(packingNote);
        var collision = await fixture.Execute("dotnet", TimeSpan.FromMinutes(2),
            NewCommand("aicf-class", "--name", "PackingNote", "--namespace", itemNamespace, "--output", domain));
        Assert.NotEqual(0, collision.Exit);
        Assert.Equal(before, File.ReadAllBytes(packingNote));

        await Template("uninstall", delivered, custom);
        var installed = await Template("uninstall");
        Assert.DoesNotContain("warehouse-class", installed);
        Assert.DoesNotContain("aicf-class", installed);
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
