using System.Text.Json;
using static FormatTool.IntegrationTests.FormatFixture;

namespace FormatTool.IntegrationTests;

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
    public void InvalidJsonFailsWithoutSdkOrSourceChanges(string raw)
    {
        using var fixture = new FormatFixture();
        byte[] before = null!;
        (int Exit, JsonElement Result) run = default;

        this.Given(GivenOriginalSourceBytes, "original source bytes")
            .When(WhenSubmittingInvalidJson, "submitting invalid json")
            .Then(ThenRefuseWithoutSdkOrSourceChanges, "refuse without sdk or source changes")
            .BDDfy();

        void GivenOriginalSourceBytes()
        {
            before = File.ReadAllBytes(fixture.Chosen);
        }

        async Task WhenSubmittingInvalidJson()
        {
            run = await fixture.Invoke(raw: raw);
        }

        void ThenRefuseWithoutSdkOrSourceChanges()
        {
            Failure(run, "invalid-request");
            Assert.Empty(Items(run.Result, "commands"));
            Assert.Equal(before, File.ReadAllBytes(fixture.Chosen));
        }
    }

    [Theory]
    [InlineData("style", null, null, "invalid-request")]
    [InlineData("style", "IDE0008", null, "invalid-request")]
    [InlineData("style", "IDE9999", "warn", "unsupported-diagnostic")]
    [InlineData("analyzers", "IDE0008", "warn", "unsupported-diagnostic")]
    [InlineData("analyzers", "CA1040", "warn", "no-fixer")]
    [InlineData("whitespace", "IDE0008", "warn", "invalid-request")]
    public void UnsupportedCleanupRequestFailsBeforeSdk(string mode, string? diagnostic, string? severity, string expected)
    {
        using var fixture = GivenAFormattingProject();
        (int Exit, JsonElement Result) run = default;

        this.Given("a formatting project")
            .When(WhenSubmittingUnsupportedCleanup, "submitting unsupported cleanup")
            .Then(ThenRefuseBeforeSdk, "refuse before sdk")
            .BDDfy();

        FormatFixture GivenAFormattingProject() => new FormatFixture();

        async Task WhenSubmittingUnsupportedCleanup()
        {
            run = await fixture.Invoke(mode: mode, diagnostics: diagnostic is null ? [] : [diagnostic], severity: severity);
        }

        void ThenRefuseBeforeSdk()
        {
            Failure(run, expected);
            Assert.Empty(Items(run.Result, "commands"));
        }
    }

    [Fact]
    public void EmptySelectionFailsBeforeSdk()
    {
        using var fixture = GivenAFormattingProject();
        (int Exit, JsonElement Result) run = default;

        this.Given("a formatting project")
            .When(WhenSubmittingAnEmptySelection, "submitting an empty selection")
            .Then(ThenRefuseWithoutCommandsOrWrites, "refuse without commands or writes")
            .BDDfy();

        FormatFixture GivenAFormattingProject() => new FormatFixture();

        async Task WhenSubmittingAnEmptySelection()
        {
            run = await fixture.Invoke(files: []);
        }

        void ThenRefuseWithoutCommandsOrWrites()
        {
            Failure(run, "invalid-request");
            Assert.Empty(Items(run.Result, "commands"));
            Assert.Empty(Items(run.Result, "changedFiles"));
        }
    }

    [FormatHostTheory]
    [InlineData("Missing.cs")]
    [InlineData("Nested")]
    public void MissingFileAndDirectorySelectionsFailBeforeSdk(string file)
    {
        using var fixture = GivenTheProjectWithNoMatchingSourceFile();
        (int Exit, JsonElement Result) result = default;

        this.Given("a project and a selection that is not a source file")
            .When(WhenCheckingTheSelection, "checking the selection")
            .Then(ThenRefuseBeforeSdkOrSourceWrites, "refuse before SDK calls or source writes")
            .BDDfy();

        async Task WhenCheckingTheSelection() => result = await fixture.Invoke(files: [file]);

        void ThenRefuseBeforeSdkOrSourceWrites()
        {
            Failure(result, "invalid-selection");
            Assert.Empty(Items(result.Result, "commands"));
            Assert.Empty(Items(result.Result, "changedFiles"));
        }

        FormatFixture GivenTheProjectWithNoMatchingSourceFile() => new FormatFixture();
    }

    [FormatHostFact]
    public void MissingWorkspaceFailsBeforeSdk()
    {
        using var fixture = GivenAFormattingProject();
        (int Exit, JsonElement Result) run = default;

        this.Given("a formatting project")
            .When(WhenCheckingAMissingWorkspace, "checking a missing workspace")
            .Then(ThenRefuseBeforeSdk, "refuse before sdk")
            .BDDfy();

        FormatFixture GivenAFormattingProject() => new FormatFixture();

        async Task WhenCheckingAMissingWorkspace()
        {
            run = await fixture.Invoke(workspace: "App/Missing.csproj");
        }

        void ThenRefuseBeforeSdk()
        {
            Failure(run, "load-failed");
            Assert.Empty(Items(run.Result, "commands"));
        }
    }

    [FormatHostTheory(posixOnly: true)]
    [Trait("Platform", "MacOS")]
    [InlineData("Wildcard*.cs")]
    [InlineData("Wildcard?.cs")]
    [InlineData(@"Wildcard\Other.cs")]
    public void PosixLiteralGlobAndSeparatorNamesFailBeforeSdk(string name)
    {
        using var fixture = new FormatFixture();
        string sibling = null!, literal = null!;
        byte[] siblingBefore = null!, literalBefore = null!;
        (int Exit, JsonElement Result) result = default;

        this.Given(GivenAFileWithALiteralGlobOrSeparator, "a file with a literal glob or separator")
            .When(WhenApplyingToThatFilename, "applying to that filename")
            .Then(ThenRefuseAndPreserveBothFiles, "refuse before SDK calls and preserve both files")
            .BDDfy();

        void GivenAFileWithALiteralGlobOrSeparator()
        {
            sibling = fixture.Write("App/WildcardOther.cs", Original);
            siblingBefore = File.ReadAllBytes(sibling);
            literal = fixture.Write("App/" + name, Original);
            literalBefore = File.ReadAllBytes(literal);
        }

        async Task WhenApplyingToThatFilename() => result = await fixture.Invoke(files: [name], action: "apply");

        void ThenRefuseAndPreserveBothFiles()
        {
            Failure(result, "unsupported-selection");
            Assert.Empty(Items(result.Result, "commands"));
            Assert.Equal(literalBefore, File.ReadAllBytes(literal));
            Assert.Equal(siblingBefore, File.ReadAllBytes(sibling));
        }
    }
}
