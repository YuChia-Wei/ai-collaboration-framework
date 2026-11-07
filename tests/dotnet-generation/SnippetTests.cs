using System.Text.Json;
using SnippetTool;

namespace Generation.Tests;

public sealed class SnippetTests
{
    private static readonly string[] BuiltInIds =
    [
        "cancellation-guard", "constructor-assignment", "domain-contracts", "es-aggregate", "guid-id",
        "interface-method", "null-guard", "readonly-property", "string-guard"
    ];

    internal const string CustomBody = """
        // ${comment}

        if (true) {
            var ${variable} = "$${顯示}";
            return ${variable};
        }
        """;
    private const string CustomText = "    // first\r\n    // second ${verbatim}\r\n\r\n    if (true) {\r\n" +
        "        var result = \"${顯示}\";\r\n        return result;\r\n    }";

    [Fact]
    public void BuiltInCatalogListsSearchesAndInspectsWithoutAChildProcess()
    {
        using var fixture = new GenerationFixture();
        Assert.Equal(BuiltInIds, Ids(Invoke(fixture, new { schemaVersion = 1, operation = "list" })));
        Assert.Equal(new[] { "cancellation-guard", "null-guard", "string-guard" },
            Ids(Invoke(fixture, new { schemaVersion = 1, operation = "search", query = "GUARD" })));
        var inspected = Invoke(fixture, new { schemaVersion = 1, operation = "inspect", id = "interface-method" });
        var snippet = inspected.GetProperty("snippet");
        Assert.Equal("interface-member", Text(snippet, "context"));
        Assert.Equal("System.Threading.Tasks", Assert.Single(snippet.GetProperty("requiredUsings").EnumerateArray()).GetString());
        Assert.Equal("value", Text(snippet.GetProperty("parameters").GetProperty("parameterName"), "default"));
        Assert.Equal("framework-dotnet", Text(inspected.GetProperty("source"), "id"));
        Assert.Equal("${returnType} ${methodName}(${parameterType} ${parameterName});\n",
            Text(inspected, "body").ReplaceLineEndings("\n"));
    }

    [Fact]
    public void BuiltInFragmentsUseTypedParametersAndDefaults()
    {
        using var fixture = new GenerationFixture();
        Assert.Equal("    Task<string> ReadAsync(string value);\n",
            Render(fixture, "interface-method", new { methodName = "ReadAsync", returnType = "Task<string>" }, indent: 4));
        Assert.Equal("    ArgumentException.ThrowIfNullOrWhiteSpace(label);\n",
            Render(fixture, "string-guard", new { parameterName = "label" }, indent: 4));
    }

    [Theory]
    [InlineData("""{"schemaVersion":1,"operation":"render","id":"string-guard"}""", "missing-parameter")]
    [InlineData("""{"schemaVersion":1,"operation":"render","id":"string-guard","parameters":{"parameterName":"label","extra":"value"}}""", "unknown-parameter")]
    [InlineData("""{"schemaVersion":1,"operation":"render","id":"string-guard","parameters":{"parameterName":"class"}}""", "invalid-parameter")]
    [InlineData("""{"schemaVersion":1,"operation":"render","id":"interface-method","parameters":{"methodName":"Read","returnType":"List<int>"}}""", "invalid-parameter")]
    [InlineData("""{"schemaVersion":1,"operation":"list","extra":0}""", "invalid-request")]
    [InlineData("""{"schemaVersion":1,"operation":"list","operation":"render"}""", "invalid-request")]
    [InlineData("""{"schemaVersion":2,"operation":"list"}""", "unsupported-request-schema")]
    [InlineData("""{"schemaVersion":1,"operation":"list","source":"missing.json"}""", "unreadable-catalog")]
    public void InvalidRequestPreservesFailureEnvelope(string request, string expectedCode)
    {
        using var fixture = new GenerationFixture();
        Invoke(fixture, request, expectedCode);
    }

    [Fact]
    public void CustomMetadataIsLazyAndMissingOrEmptyBodiesHaveDistinctErrors()
    {
        using var fixture = new GenerationFixture();
        WriteCatalog(fixture);
        Assert.Equal(new[] { "custom-probe", "unreadable" },
            Ids(Invoke(fixture, new { schemaVersion = 1, operation = "list", source = "custom.json" })));
        Assert.Equal("unreadable", Assert.Single(Ids(Invoke(fixture,
            new { schemaVersion = 1, operation = "search", source = "custom.json", query = "Unreadable" }))));
        Invoke(fixture, Inspect("unreadable"), "unreadable-body");
        Invoke(fixture, Inspect("string-guard"), "snippet-not-found");

        fixture.Write("custom-probe.snippet", "");
        Invoke(fixture, Inspect("custom-probe"), "invalid-body");
    }

    [Fact]
    public void CustomRenderPreservesUnicodeLiteralPlaceholdersIndentAndNewlines()
    {
        using var fixture = new GenerationFixture();
        var rendered = RenderCustom(fixture);
        Assert.Equal("2.0.0", Text(rendered.GetProperty("source"), "version"));
        Assert.Equal(CustomText, Text(rendered, "text"));

        fixture.Write("custom-probe.snippet", "return ${unknown};");
        Invoke(fixture, CustomRequest, "unknown-placeholder");
        fixture.Write("custom-probe.snippet", "return ${variable;");
        Invoke(fixture, Inspect("custom-probe"), "invalid-placeholder");
    }

    [Theory]
    [InlineData(2, false, "text", "unsupported-catalog-schema")]
    [InlineData(1, true, "text", "duplicate-snippet-id")]
    [InlineData(1, false, "script", "invalid-catalog")]
    public void InvalidCatalogDoesNotList(int schema, bool duplicate, string kind, string expected)
    {
        using var fixture = new GenerationFixture();
        WriteCatalog(fixture, schema, duplicate, kind);
        Invoke(fixture, new { schemaVersion = 1, operation = "list", source = "custom.json" }, expected);
    }

    [SnippetArtifactFact]
    [Trait("Boundary", "PublishedArtifact")]
    public async Task PublishedExecutableFindsItsBundledCatalogFromAnotherDirectory()
    {
        using var fixture = new GenerationFixture();
        var executable = GenerationFixture.ExistingArtifact(GenerationFixture.SnippetArtifact, "AICF_SNIPPET_ARTIFACT");
        var request = fixture.Write("request.json", """{"schemaVersion":1,"operation":"list"}""");
        var result = await fixture.Execute(executable, TimeSpan.FromSeconds(15), "--request", Path.GetFileName(request));
        Assert.Equal(BuiltInIds, Ids(ReadResult(result, null)));

        File.WriteAllText(request, """{"schemaVersion":2,"operation":"list"}""");
        var failure = await fixture.Execute(executable, TimeSpan.FromSeconds(15), "--request", Path.GetFileName(request));
        ReadResult(failure, "unsupported-request-schema");

        var version = await fixture.Execute(executable, TimeSpan.FromSeconds(15), "--version");
        Assert.Equal(0, version.Exit);
        Assert.Empty(version.Error);
        Assert.False(string.IsNullOrWhiteSpace(version.Output));
    }

    [SnippetArtifactFact(linuxOnly: true)]
    [Trait("Boundary", "LinuxArtifact")]
    public async Task PublishedExecutableRejectsFifoWithoutOpeningIt()
    {
        using var fixture = new GenerationFixture();
        var executable = GenerationFixture.ExistingArtifact(GenerationFixture.SnippetArtifact, "AICF_SNIPPET_ARTIFACT");
        WriteCatalog(fixture);
        var fifo = await fixture.Execute("mkfifo", TimeSpan.FromSeconds(15), "--", Path.Combine(fixture.Root, "custom-probe.snippet"));
        Assert.True(fifo.Exit == 0, fifo.Error);
        var request = fixture.Write("request.json", JsonSerializer.Serialize(Inspect("custom-probe")));
        ReadResult(await fixture.Execute(executable, TimeSpan.FromSeconds(15), "--request", request), "invalid-body");
    }

    internal static JsonElement RenderCustom(GenerationFixture fixture)
    {
        WriteCatalog(fixture);
        fixture.Write("custom-probe.snippet", CustomBody);
        return Invoke(fixture, CustomRequest);
    }

    internal static string Render(GenerationFixture fixture, string id, object? parameters = null, int indent = 0) =>
        Text(Invoke(fixture, new { schemaVersion = 1, operation = "render", id, parameters, indent }), "text");

    internal static string Text(JsonElement json, string key) => json.GetProperty(key).GetString()!;

    private static object CustomRequest => new
    {
        schemaVersion = 1, operation = "render", source = "custom.json", id = "custom-probe", indent = 4,
        newline = "crlf", parameters = new { variable = "result", comment = "first\r\n// second ${verbatim}" }
    };

    private static object Inspect(string id) => new { schemaVersion = 1, operation = "inspect", source = "custom.json", id };

    private static string[] Ids(JsonElement result) => result.GetProperty("snippets").EnumerateArray()
        .Select(row => Text(row, "id")).ToArray();

    private static JsonElement Invoke(GenerationFixture fixture, object request, string? failure = null)
    {
        var path = fixture.Write("request.json", request is string raw ? raw : JsonSerializer.Serialize(request));
        using var output = new StringWriter();
        using var error = new StringWriter();
        var exit = Program.Run(["--request", path], output, error);
        return ReadResult((exit, output.ToString(), error.ToString()), failure);
    }

    private static JsonElement ReadResult((int Exit, string Output, string Error) result, string? failure)
    {
        Assert.True(result.Exit == (failure is null ? 0 : 1),
            $"Unexpected exit {result.Exit}\n{result.Output}\n{result.Error}");
        Assert.Empty(failure is null ? result.Error : result.Output);
        using var response = JsonDocument.Parse(failure is null ? result.Output : result.Error);
        var json = response.RootElement;
        Assert.Equal(1, json.GetProperty("schemaVersion").GetInt32());
        if (failure is not null)
            Assert.Equal(failure, Text(json.GetProperty("error"), "code"));
        return json.Clone();
    }

    private static void WriteCatalog(GenerationFixture fixture, int schemaVersion = 1, bool duplicate = false, string kind = "text")
    {
        object Row(string id, string title, string bodyFile, object parameters) => new
        {
            id, title, description = "Custom method body", context = "method-body", bodyFile,
            tags = Array.Empty<string>(), requiredUsings = Array.Empty<string>(), preconditions = Array.Empty<string>(), parameters
        };
        var custom = Row("custom-probe", "Probe", "custom-probe.snippet", new
        {
            variable = new { kind = "identifier" },
            comment = new { kind }
        });
        var lazy = Row("unreadable", "Unreadable", "missing.snippet", new { });
        fixture.Write("custom.json", JsonSerializer.Serialize(new
        {
            schemaVersion, source = new { id = "custom", version = "2.0.0" },
            snippets = new[] { custom, duplicate ? custom : lazy }
        }));
    }
}
