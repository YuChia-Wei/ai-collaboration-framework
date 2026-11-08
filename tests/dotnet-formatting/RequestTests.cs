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
        using var fixture = new FormatFixture(requestOnly: true);
        byte[] before = null!;
        (int Exit, JsonElement Result) run = default;

        this.Given(GivenOriginalSourceBytes, "original source bytes")
            .When(WhenSubmittingInvalidJson, "submitting invalid json")
            .Then(ThenRefuseWithoutSdkOrSourceChanges, "refuse without sdk or source changes")
            .BDDfy();

        void GivenOriginalSourceBytes()
        {
            fixture.Write("App/Nested/Chosen.cs", Original);
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

    [Fact]
    public void Should_report_no_fixer_without_sdk_commands_when_submitting_ca1040()
    {
        using var fixture = new FormatFixture(requestOnly: true);
        string request = null!;
        (int Exit, JsonElement Result) run = default;

        this.Given(GivenACa1040AnalyzerCleanupRequest, "an analyzer cleanup request for CA1040")
            .When(WhenSubmittingTheCleanupRequest, "submitting the cleanup request")
            .Then(ThenReportTheFailureEnvelopeWithoutSdkCommands, "report the failure envelope without sdk commands")
            .BDDfy();

        void GivenACa1040AnalyzerCleanupRequest() => request = """
            {"schemaVersion":1,"workspace":"App/App.csproj","files":["Nested/Chosen.cs"],"mode":"analyzers","action":"check","diagnostics":["CA1040"],"severity":"warn"}
            """;

        async Task WhenSubmittingTheCleanupRequest() => run = await fixture.Invoke(raw: request);

        void ThenReportTheFailureEnvelopeWithoutSdkCommands()
        {
            Failure(run, "no-fixer");
            Assert.Empty(Items(run.Result, "commands"));
        }
    }

    [Fact]
    public void EmptySelectionFailsBeforeSdk()
    {
        using var fixture = new FormatFixture(requestOnly: true);
        string[] selectedFiles = null!;
        (int Exit, JsonElement Result) run = default;

        this.Given(GivenNoSelectedFiles, "no selected files")
            .When(WhenSubmittingAnEmptySelection, "submitting an empty selection")
            .Then(ThenRefuseWithoutCommandsOrWrites, "refuse without commands or writes")
            .BDDfy();

        void GivenNoSelectedFiles() => selectedFiles = [];

        async Task WhenSubmittingAnEmptySelection() => run = await fixture.Invoke(files: selectedFiles);

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
        using var fixture = new FormatFixture(requestOnly: true);
        (int Exit, JsonElement Result) result = default;

        this.Given(GivenAProjectAndDirectory, "a project and directory")
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

        void GivenAProjectAndDirectory()
        {
            fixture.WriteProject();
            Directory.CreateDirectory(Path.GetDirectoryName(fixture.Chosen)!);
        }
    }

    [FormatHostFact]
    public void MissingWorkspaceFailsBeforeSdk()
    {
        using var fixture = new FormatFixture(requestOnly: true);
        string workspace = null!;
        (int Exit, JsonElement Result) run = default;

        this.Given(GivenAnAbsentWorkspacePath, "an absent workspace path")
            .When(WhenCheckingAMissingWorkspace, "checking a missing workspace")
            .Then(ThenRefuseBeforeSdk, "refuse before sdk")
            .BDDfy();

        void GivenAnAbsentWorkspacePath() => workspace = "App/Missing.csproj";

        async Task WhenCheckingAMissingWorkspace() => run = await fixture.Invoke(workspace: workspace);

        void ThenRefuseBeforeSdk()
        {
            Failure(run, "load-failed");
            Assert.Empty(Items(run.Result, "commands"));
        }
    }

    [FormatHostFact]
    public void Should_refuse_cleanup_when_the_solution_maps_debug_to_release()
    {
        using var fixture = new FormatFixture(requestOnly: true);
        (int Exit, JsonElement Result) run = default;

        this.Given(GivenASolutionMappingDebugToRelease, "a solution mapping debug to release")
            .When(WhenCheckingTheMappedSolution, "checking the mapped solution")
            .Then(ThenRefuseBeforeSdkCommands, "refuse before sdk commands")
            .BDDfy();

        void GivenASolutionMappingDebugToRelease()
        {
            fixture.WriteProject();
            fixture.Write("App/Nested/Chosen.cs", Original);
            fixture.Write("Mapped.sln", """
                Microsoft Visual Studio Solution File, Format Version 12.00
                Project("{FAE04EC0-301F-11D3-BF4B-00C04F79EFBC}") = "App", "App\App.csproj", "{A168DF84-CAED-473D-ADAA-96901A33BB02}"
                EndProject
                Global
                  GlobalSection(SolutionConfigurationPlatforms) = preSolution
                    Debug|Any CPU = Debug|Any CPU
                  EndGlobalSection
                  GlobalSection(ProjectConfigurationPlatforms) = postSolution
                    {A168DF84-CAED-473D-ADAA-96901A33BB02}.Debug|Any CPU.ActiveCfg = Release|Any CPU
                    {A168DF84-CAED-473D-ADAA-96901A33BB02}.Debug|Any CPU.Build.0 = Release|Any CPU
                  EndGlobalSection
                EndGlobal
                """);
        }

        async Task WhenCheckingTheMappedSolution() =>
            run = await fixture.Invoke(workspace: "Mapped.sln", files: ["App/Nested/Chosen.cs"],
                mode: "style", diagnostics: ["IDE0008"], severity: "warn");

        void ThenRefuseBeforeSdkCommands()
        {
            Failure(run, "unsupported-cleanup-workspace");
            Assert.Empty(Items(run.Result, "commands"));
        }
    }

    [FormatHostFact]
    public void Should_preserve_the_linked_source_when_it_is_outside_the_workspace()
    {
        using var fixture = new FormatFixture(requestOnly: true);
        string linked = null!;
        byte[] before = null!;
        (int Exit, JsonElement Result) run = default;

        this.Given(GivenALinkedSourceOutsideTheProject, "a linked source outside the project")
            .When(WhenApplyingThroughTheProject, "applying through the project")
            .Then(ThenRefuseBeforeSdkCommandsAndPreserveTheLinkedSource, "refuse before sdk commands and preserve the linked source")
            .BDDfy();

        void GivenALinkedSourceOutsideTheProject()
        {
            linked = fixture.Write("@Linked.cs", Original);
            fixture.WriteProject("""<ItemGroup><Compile Include="../@Linked.cs" Link="Linked.cs" /></ItemGroup>""");
            before = File.ReadAllBytes(linked);
        }

        async Task WhenApplyingThroughTheProject() =>
            run = await fixture.Invoke(files: ["../@Linked.cs"], action: "apply");

        void ThenRefuseBeforeSdkCommandsAndPreserveTheLinkedSource()
        {
            Failure(run, "unsupported-selection");
            Assert.Empty(Items(run.Result, "commands"));
            Assert.Equal(before, File.ReadAllBytes(linked));
        }
    }

    [FormatHostTheory(posixOnly: true)]
    [Trait("Platform", "MacOS")]
    [InlineData("Wildcard*.cs")]
    [InlineData("Wildcard?.cs")]
    [InlineData(@"Wildcard\Other.cs")]
    public void PosixLiteralGlobAndSeparatorNamesFailBeforeSdk(string name)
    {
        using var fixture = new FormatFixture(requestOnly: true);
        string sibling = null!, literal = null!;
        byte[] siblingBefore = null!, literalBefore = null!;
        (int Exit, JsonElement Result) result = default;

        this.Given(GivenAFileWithALiteralGlobOrSeparator, "a file with a literal glob or separator")
            .When(WhenApplyingToThatFilename, "applying to that filename")
            .Then(ThenRefuseAndPreserveBothFiles, "refuse before SDK calls and preserve both files")
            .BDDfy();

        void GivenAFileWithALiteralGlobOrSeparator()
        {
            fixture.WriteProject();
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
