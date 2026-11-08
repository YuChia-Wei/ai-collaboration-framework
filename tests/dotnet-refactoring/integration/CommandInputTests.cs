namespace RefactorTool.IntegrationTests;

public sealed class CommandInputTests
{
    [Theory]
    [InlineData(null)]
    [InlineData("{")]
    [InlineData("null")]
    [InlineData("{}")]
    [InlineData("""{"workspace":null}""")]
    [InlineData("""{"workspace":"a","unknown":true}""")]
    [InlineData("""{"workspace":"a","workspace":"b"}""")]
    [InlineData("""{"workspace":"a"}""")]
    [InlineData("""{"workspace":"a","operation":"extract-interface","newName":"I","symbol":"T:C","namespace":"","outputFile":"I.cs","members":[]}""")]
    [InlineData("""{"workspace":"a","operation":"extract-interface","newName":"I","symbol":"T:C","namespace":"","outputFile":"I.cs","members":["P:C.P"],"renameOverloads":true}""")]
    public void InvalidRequestDoesNotWritePlan(string? content)
    {
        using var directory = new TestDirectory();
        CommandResult result = null!;
        string source = null!;
        string request = null!;
        string plan = null!;

        this.Given(GivenInvalidRequestInputAndAnAuthoredSource, "invalid request input and an authored source")
            .When(WhenPreviewingTheInvalidRequest, "previewing the invalid request")
            .Then(ThenRefuseWithoutWritingPlanOrSource, "refuse without writing plan or source")
            .BDDfy();

        void GivenInvalidRequestInputAndAnAuthoredSource()
        {
            source = directory.Write("A/Source.cs", "class C {}");
            request = content is null ? directory.PathFor("invalid.json") : directory.Write("invalid.json", content);
            plan = directory.PathFor("plan.json");
        }

        async Task WhenPreviewingTheInvalidRequest() => result = await CommandResult.Run("preview", "--request", request, "--plan", plan);

        void ThenRefuseWithoutWritingPlanOrSource()
        {
            result.Refused("invalid_input");
            Assert.False(File.Exists(plan));
            Assert.Equal("class C {}", File.ReadAllText(source));
        }
    }

    [Theory]
    [InlineData("inspect")]
    [InlineData("preview")]
    public void RequestDirectoryIsNotAJsonFile(string command)
    {
        using var directory = new TestDirectory();
        CommandResult result = null!;
        string plan = null!;
        string[] args = null!;

        this.Given(GivenADirectoryAsTheRequest, "a directory as the request")
            .When(WhenRunningTheCommand, "running the command")
            .Then(ThenRefuseWithoutWritingAPlan, "refuse without writing a plan")
            .BDDfy();

        void GivenADirectoryAsTheRequest()
        {
            plan = directory.PathFor("plan.json");
            args = [command, "--request", directory.Root, .. command == "preview" ? new[] { "--plan", plan } : []];
        }

        async Task WhenRunningTheCommand() => result = await CommandResult.Run(args);

        void ThenRefuseWithoutWritingAPlan()
        {
            result.Refused("invalid_input");
            Assert.False(File.Exists(plan));
        }
    }

    [WindowsTheory]
    [InlineData(null)]
    [InlineData("[null]")]
    [InlineData("""[{"path":"x"}]""")]
    public void InvalidPlanIsRefused(string? inputs)
    {
        using var directory = new TestDirectory();
        CommandResult result = null!;
        string path = null!;

        this.Given(GivenAMissingOrInvalidPlan, "a missing or invalid plan")
            .When(WhenApplyingThePlan, "applying the plan")
            .Then(ThenRefuseTheInvalidPlan, "refuse the invalid plan")
            .BDDfy();

        void GivenAMissingOrInvalidPlan()
        {
            path = directory.PathFor("plan.json");
            if (inputs is not null)
                directory.Write("plan.json", $$"""{"contract":"refactor-plan/1","edits":[],"request":{"workspace":"a","symbol":"T:C","newName":"Renamed"},"inputs":{{inputs}}}""");
        }

        async Task WhenApplyingThePlan() => result = await CommandResult.Run("apply", "--plan", path);

        void ThenRefuseTheInvalidPlan() => result.Refused("invalid_input");
    }

    [Theory]
    [InlineData("A/Injected.cs")]
    [InlineData("global.json")]
    public void SourceAndSdkConfigurationNamesAreRefusedBeforePreview(string destination)
    {
        using var directory = new TestDirectory();
        CommandResult result = null!;
        string source = null!;
        string sdk = null!;
        string plan = null!;

        this.Given(GivenAProtectedPlanDestination, "a protected plan destination")
            .When(WhenPreviewingToThatDestination, "previewing to that destination")
            .Then(ThenRefuseAndPreserveSourceAndSdkConfig, "refuse and preserve source and sdk config")
            .BDDfy();

        void GivenAProtectedPlanDestination()
        {
            source = directory.Write("A/Source.cs", "class C {}");
            sdk = directory.Write("global.json", "unchanged");
            plan = directory.PathFor(destination);
        }

        async Task WhenPreviewingToThatDestination() => result = await CommandResult.Run("preview", "--request", directory.PathFor("unused.json"), "--plan", plan);

        void ThenRefuseAndPreserveSourceAndSdkConfig()
        {
            result.Refused("unsafe_plan_path");
            Assert.Equal("class C {}", File.ReadAllText(source));
            Assert.Equal("unchanged", File.ReadAllText(sdk));
            if (destination != "global.json") Assert.False(File.Exists(plan));
        }
    }
}
