using System.Text.Json;
using Generation.TestSupport;

namespace SnippetTool.IntegrationTests;

internal static class SnippetTestSupport
{
    internal static readonly string[] BuiltInIds =
    [
        "cancellation-guard", "constructor-assignment", "domain-contracts", "es-aggregate", "guid-id",
        "interface-method", "null-guard", "readonly-property", "string-guard"
    ];

    internal static string Text(JsonElement json, string key) => json.GetProperty(key).GetString()!;

    internal static object Inspect(string id) => new { schemaVersion = 1, operation = "inspect", source = "custom.json", id };

    internal static string[] Ids(JsonElement result) => result.GetProperty("snippets").EnumerateArray()
        .Select(row => Text(row, "id")).ToArray();

    internal static JsonElement ReadResult((int Exit, string Output, string Error) result, string? failure)
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

    internal static void WriteCatalog(GenerationFixture fixture, int schemaVersion = 1, bool duplicate = false, string kind = "text")
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
