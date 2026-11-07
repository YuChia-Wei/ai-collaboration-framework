using static FormatTool.Tests.FormatFixture;

namespace FormatTool.Tests;

public sealed class RequestTests
{
    private const string Valid = """{"schemaVersion":1,"workspace":"App/App.csproj","files":["Nested/Chosen.cs"],"mode":"whitespace","action":"check"}""";

    public static TheoryData<string> InvalidRequests => new()
    {
        Valid[..^1] + ""","surprise":true}""",
        Valid.Replace("""["Nested/Chosen.cs"]""", "12"),
        Valid[..^1] + ""","action":"apply"}""",
        "{",
        "null"
    };

    [Theory]
    [MemberData(nameof(InvalidRequests))]
    public async Task InvalidJsonFailsWithoutSdkOrSourceChanges(string raw)
    {
        using var fixture = new FormatFixture();
        var run = await fixture.Invoke(raw: raw);
        Failure(run, "invalid-request");
        Assert.Empty(Items(run.Result, "commands"));
        Assert.Equal(Original, File.ReadAllText(fixture.Chosen));
    }

    [Theory]
    [InlineData("style", null, null, "invalid-request")]
    [InlineData("style", "IDE0008", null, "invalid-request")]
    [InlineData("style", "IDE9999", "warn", "unsupported-diagnostic")]
    [InlineData("analyzers", "IDE0008", "warn", "unsupported-diagnostic")]
    [InlineData("analyzers", "CA1040", "warn", "no-fixer")]
    [InlineData("whitespace", "IDE0008", "warn", "invalid-request")]
    public async Task UnsupportedCleanupRequestFailsBeforeSdk(string mode, string? diagnostic, string? severity, string expected)
    {
        using var fixture = new FormatFixture();
        var run = await fixture.Invoke(mode: mode, diagnostics: diagnostic is null ? [] : [diagnostic], severity: severity);
        Failure(run, expected);
        Assert.Empty(Items(run.Result, "commands"));
    }

    [Fact]
    public async Task EmptySelectionFailsBeforeSdk()
    {
        using var fixture = new FormatFixture();
        var run = await fixture.Invoke(files: []);
        Failure(run, "invalid-request");
        Assert.Empty(Items(run.Result, "commands"));
        Assert.Empty(Items(run.Result, "changedFiles"));
    }

    [FormatHostFact]
    public async Task MissingFileAndDirectorySelectionsFailBeforeSdk()
    {
        using var fixture = new FormatFixture();
        foreach (var file in new[] { "Missing.cs", "Nested" })
        {
            var run = await fixture.Invoke(files: [file]);
            Failure(run, "invalid-selection");
            Assert.Empty(Items(run.Result, "commands"));
            Assert.Empty(Items(run.Result, "changedFiles"));
        }
    }

    [FormatHostFact]
    public async Task MissingWorkspaceFailsBeforeSdk()
    {
        using var fixture = new FormatFixture();
        var run = await fixture.Invoke(workspace: "App/Missing.csproj");
        Failure(run, "load-failed");
        Assert.Empty(Items(run.Result, "commands"));
    }

    [FormatHostFact(posixOnly: true)]
    [Trait("Platform", "MacOS")]
    public async Task PosixLiteralGlobAndSeparatorNamesFailBeforeSdk()
    {
        using var fixture = new FormatFixture();
        var sibling = fixture.Write("App/WildcardOther.cs", Original);
        foreach (var name in new[] { "Wildcard*.cs", "Wildcard?.cs", @"Wildcard\Other.cs" })
        {
            var literal = fixture.Write("App/" + name, Original);
            var run = await fixture.Invoke(files: [name], action: "apply");
            Failure(run, "unsupported-selection");
            Assert.Empty(Items(run.Result, "commands"));
            Assert.Equal(Original, File.ReadAllText(literal));
            Assert.Equal(Original, File.ReadAllText(sibling));
        }
    }
}
