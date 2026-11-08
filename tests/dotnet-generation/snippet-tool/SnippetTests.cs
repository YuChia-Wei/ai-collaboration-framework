using static SnippetTool.IntegrationTests.SnippetTestSupport;
using System.Text.Json;
using SnippetTool;
using Generation.TestSupport;

namespace SnippetTool.IntegrationTests;

public sealed class SnippetTests
{
    internal const string CustomBody = """
        // ${comment}

        if (true) {
            var ${variable} = "$${顯示}";
            return ${variable};
        }
        """;

    [Fact]
    public void BuiltInCatalogListsSearchesAndInspectsWithoutAChildProcess()
    {
        using var fixture = GivenAnIsolatedRequestDirectory();
        JsonElement listed = default, searched = default, inspected = default;

        this.Given("the bundled catalog and an isolated request directory")
            .When(WhenListingTheCatalog, "listing the catalog")
            .Then(ThenListEveryBuiltInId, "list every built-in ID")
            .When(WhenSearchingForGuards, "searching for guards without matching case")
            .Then(ThenFindTheGuardIds, "find the guard IDs")
            .When(WhenInspectingTheInterfaceMethod, "inspecting the interface method")
            .Then(ThenDescribeItsContextUsingsDefaultsAndBody, "describe its context, usings, defaults and body")
            .BDDfy();

        void WhenListingTheCatalog() => listed = Invoke(fixture, new { schemaVersion = 1, operation = "list" });
        void ThenListEveryBuiltInId() => Assert.Equal(BuiltInIds, Ids(listed));

        void WhenSearchingForGuards() => searched = Invoke(fixture, new { schemaVersion = 1, operation = "search", query = "GUARD" });
        void ThenFindTheGuardIds() => Assert.Equal(new[] { "cancellation-guard", "null-guard", "string-guard" }, Ids(searched));

        void WhenInspectingTheInterfaceMethod() =>
            inspected = Invoke(fixture, new { schemaVersion = 1, operation = "inspect", id = "interface-method" });

        void ThenDescribeItsContextUsingsDefaultsAndBody()
        {
            var snippet = inspected.GetProperty("snippet");
            Assert.Equal("interface-member", Text(snippet, "context"));
            Assert.Equal("System.Threading.Tasks", Assert.Single(snippet.GetProperty("requiredUsings").EnumerateArray()).GetString());
            Assert.Equal("value", Text(snippet.GetProperty("parameters").GetProperty("parameterName"), "default"));
            Assert.Equal("framework-dotnet", Text(inspected.GetProperty("source"), "id"));
            Assert.Equal("${returnType} ${methodName}(${parameterType} ${parameterName});\n",
                Text(inspected, "body").ReplaceLineEndings("\n"));
        }

        GenerationFixture GivenAnIsolatedRequestDirectory() => new GenerationFixture();
    }

    [Fact]
    public void BuiltInFragmentsUseTypedParametersAndDefaults()
    {
        using var fixture = GivenABundledInterfaceMethod();
        string method = null!;

        this.Given("the bundled interface method fragment")
            .When(WhenRenderingTheInterfaceMethod, "rendering with a typed return and omitted default parameter")
            .Then(ThenRenderTheTypedReturnAndDefaultParameter, "render the typed return and default parameter")
            .BDDfy();

        GenerationFixture GivenABundledInterfaceMethod() => new();

        void WhenRenderingTheInterfaceMethod() =>
            method = Render(fixture, "interface-method", new { methodName = "ReadAsync", returnType = "Task<string>" }, indent: 4);

        void ThenRenderTheTypedReturnAndDefaultParameter() => Assert.Equal("    Task<string> ReadAsync(string value);\n", method);
    }

    [Fact]
    public void BuiltInStringGuardUsesTheNamedParameter()
    {
        using var fixture = GivenABundledStringGuard();
        string guard = null!;

        this.Given("the bundled string guard fragment")
            .When(WhenRenderingTheStringGuard, "rendering the string guard with the label parameter")
            .Then(ThenRenderTheNamedGuardParameter, "render the named guard parameter")
            .BDDfy();

        GenerationFixture GivenABundledStringGuard() => new();
        void WhenRenderingTheStringGuard() => guard = Render(fixture, "string-guard", new { parameterName = "label" }, indent: 4);

        void ThenRenderTheNamedGuardParameter() => Assert.Equal("    ArgumentException.ThrowIfNullOrWhiteSpace(label);\n", guard);
    }

    [Theory]
    [InlineData("""{"schemaVersion":1,"operation":"render","id":"string-guard"}""", "missing-parameter")]
    [InlineData("""{"schemaVersion":1,"operation":"list","extra":0}""", "invalid-request")]
    [InlineData("""{"schemaVersion":1,"operation":"list","operation":"render"}""", "invalid-request")]
    [InlineData("""{"schemaVersion":2,"operation":"list"}""", "unsupported-request-schema")]
    [InlineData("""{"schemaVersion":1,"operation":"list","source":"missing.json"}""", "unreadable-catalog")]
    public void InvalidRequestPreservesFailureEnvelope(string request, string expectedCode)
    {
        using var fixture = GivenAnIsolatedRequestDirectory();
        (int Exit, string Output, string Error) run = (0, "", "");

        this.Given("the selected malformed request")
            .When(WhenExecutingTheMalformedRequest, "executing the malformed request")
            .Then(ThenReturnTheExpectedFailureEnvelope, "return the expected failure envelope")
            .BDDfy();

        void WhenExecutingTheMalformedRequest() => run = Call(fixture, request);

        void ThenReturnTheExpectedFailureEnvelope() => ReadResult(run, expectedCode);

        GenerationFixture GivenAnIsolatedRequestDirectory() => new GenerationFixture();
    }

    [Fact]
    public void CustomMetadataIsLazyAndMissingOrEmptyBodiesHaveDistinctErrors()
    {
        using var fixture = new GenerationFixture();
        JsonElement listed = default, searched = default;
        (int Exit, string Output, string Error) missing = (0, "", ""), hidden = (0, "", ""), empty = (0, "", "");

        this.Given(GivenCustomCatalogWithoutBodies, "a custom catalog without bodies")
            .When(WhenListingMetadata, "listing metadata")
            .Then(ThenListBothCustomIdsWithoutReadingBodies, "list both custom IDs without reading bodies")
            .When(WhenSearchingForUnreadableMetadata, "searching for unreadable metadata")
            .Then(ThenFindTheUnreadableEntry, "find the unreadable entry")
            .When(WhenInspectingTheMissingBody, "inspecting the missing body")
            .Then(ThenReportAnUnreadableBody, "report an unreadable body")
            .When(WhenInspectingABuiltInIdInTheCustomCatalog, "inspecting a built-in ID in the custom catalog")
            .Then(ThenReportAnUnknownSnippet, "report an unknown snippet")
            .Given(GivenAnEmptyCustomBody, "an empty custom body")
            .When(WhenInspectingTheEmptyBody, "inspecting the empty body")
            .Then(ThenReportAnInvalidBody, "report an invalid body")
            .BDDfy();

        void GivenCustomCatalogWithoutBodies() => WriteCatalog(fixture);
        void WhenListingMetadata() => listed = Invoke(fixture, new { schemaVersion = 1, operation = "list", source = "custom.json" });
        void ThenListBothCustomIdsWithoutReadingBodies() => Assert.Equal(new[] { "custom-probe", "unreadable" }, Ids(listed));

        void WhenSearchingForUnreadableMetadata() =>
            searched = Invoke(fixture, new { schemaVersion = 1, operation = "search", source = "custom.json", query = "Unreadable" });

        void ThenFindTheUnreadableEntry() => Assert.Equal("unreadable", Assert.Single(Ids(searched)));
        void WhenInspectingTheMissingBody() => missing = Call(fixture, Inspect("unreadable"));
        void ThenReportAnUnreadableBody() => ReadResult(missing, "unreadable-body");
        void WhenInspectingABuiltInIdInTheCustomCatalog() => hidden = Call(fixture, Inspect("string-guard"));
        void ThenReportAnUnknownSnippet() => ReadResult(hidden, "snippet-not-found");
        void GivenAnEmptyCustomBody() => fixture.Write("custom-probe.snippet", "");
        void WhenInspectingTheEmptyBody() => empty = Call(fixture, Inspect("custom-probe"));
        void ThenReportAnInvalidBody() => ReadResult(empty, "invalid-body");
    }

    [Fact]
    public void Should_use_the_selected_source_when_rendering_and_reject_invalid_inspection()
    {
        using var fixture = new GenerationFixture();
        JsonElement rendered = default;
        (int Exit, string Output, string Error) malformed = (0, "", "");

        this.Given(GivenTheCustomCatalogAndUnicodeBody, "the custom catalog and Unicode body")
            .When(WhenRenderingWithIndentationAndCrlf, "rendering with indentation and CRLF")
            .Then(ThenReportTheSelectedSourceAndRenderedText, "report the selected source and rendered text")
            .Given(GivenAMalformedPlaceholder, "a body with a malformed placeholder")
            .When(WhenInspectingTheMalformedPlaceholder, "inspecting the malformed placeholder")
            .Then(ThenReportAnInvalidPlaceholder, "report an invalid placeholder")
            .BDDfy();

        void GivenTheCustomCatalogAndUnicodeBody() => WriteCustomBody(fixture);
        void WhenRenderingWithIndentationAndCrlf() => rendered = Invoke(fixture, CustomRequest);

        void ThenReportTheSelectedSourceAndRenderedText()
        {
            Assert.Equal("2.0.0", Text(rendered.GetProperty("source"), "version"));
            Assert.StartsWith("    // first\r\n", Text(rendered, "text"), StringComparison.Ordinal);
        }

        void GivenAMalformedPlaceholder() => fixture.Write("custom-probe.snippet", "return ${variable;");
        void WhenInspectingTheMalformedPlaceholder() => malformed = Call(fixture, Inspect("custom-probe"));
        void ThenReportAnInvalidPlaceholder() => ReadResult(malformed, "invalid-placeholder");
    }

    [Theory]
    [InlineData(2, false, "text", "unsupported-catalog-schema")]
    [InlineData(1, true, "text", "duplicate-snippet-id")]
    [InlineData(1, false, "script", "invalid-catalog")]
    public void InvalidCatalogDoesNotList(int schema, bool duplicate, string kind, string expected)
    {
        using var fixture = new GenerationFixture();
        (int Exit, string Output, string Error) run = (0, "", "");

        this.Given(GivenTheInvalidCatalog, "the invalid catalog")
            .When(WhenListingThatCatalog, "listing that catalog")
            .Then(ThenRefuseWithTheExpectedFailure, "refuse with the expected failure")
            .BDDfy();

        void GivenTheInvalidCatalog() => WriteCatalog(fixture, schema, duplicate, kind);

        void WhenListingThatCatalog() =>
            run = Call(fixture, new { schemaVersion = 1, operation = "list", source = "custom.json" });

        void ThenRefuseWithTheExpectedFailure() => ReadResult(run, expected);
    }

    internal static JsonElement RenderCustom(GenerationFixture fixture)
    {
        WriteCustomBody(fixture);
        return Invoke(fixture, CustomRequest);
    }

    private static void WriteCustomBody(GenerationFixture fixture)
    {
        WriteCatalog(fixture);
        fixture.Write("custom-probe.snippet", CustomBody);
    }

    internal static string Render(GenerationFixture fixture, string id, object? parameters = null, int indent = 0) =>
        Text(Invoke(fixture, new { schemaVersion = 1, operation = "render", id, parameters, indent }), "text");

    private static object CustomRequest => new
    {
        schemaVersion = 1, operation = "render", source = "custom.json", id = "custom-probe", indent = 4,
        newline = "crlf", parameters = new { variable = "result", comment = "first\r\n// second ${verbatim}" }
    };

    private static JsonElement Invoke(GenerationFixture fixture, object request) => ReadResult(Call(fixture, request), null);

    private static (int Exit, string Output, string Error) Call(GenerationFixture fixture, object request)
    {
        var path = fixture.Write("request.json", request is string raw ? raw : JsonSerializer.Serialize(request));
        using var output = new StringWriter();
        using var error = new StringWriter();
        var exit = Program.Run(["--request", path], output, error);
        return (exit, output.ToString(), error.ToString());
    }
}
