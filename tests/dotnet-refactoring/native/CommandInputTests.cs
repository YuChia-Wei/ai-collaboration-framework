using System.Text.Json;

namespace RefactorTool.Tests;

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
    public async Task InvalidRequestDoesNotWritePlan(string? content)
    {
        using var directory = new TestDirectory();
        var source = directory.Write("A/Source.cs", "class C {}");
        var request = content is null ? directory.PathFor("invalid.json") : directory.Write("invalid.json", content);
        var plan = directory.PathFor("plan.json");
        await Refused("invalid_input", "preview", "--request", request, "--plan", plan);
        Assert.False(File.Exists(plan));
        Assert.Equal("class C {}", File.ReadAllText(source));
    }

    [Theory]
    [InlineData("inspect")]
    [InlineData("preview")]
    public async Task RequestDirectoryIsNotAJsonFile(string command)
    {
        using var directory = new TestDirectory();
        var plan = directory.PathFor("plan.json");
        string[] args = [command, "--request", directory.Root, .. command == "preview" ? new[] { "--plan", plan } : []];
        await Refused("invalid_input", args);
        Assert.False(File.Exists(plan));
    }

    [Theory]
    [InlineData(null)]
    [InlineData("[null]")]
    [InlineData("""[{"path":"x"}]""")]
    public async Task InvalidPlanIsRefused(string? inputs)
    {
        using var directory = new TestDirectory();
        var path = directory.PathFor("plan.json");
        if (inputs is not null)
            directory.Write("plan.json", $$"""{"contract":"refactor-plan/1","edits":[],"request":{"workspace":"a","symbol":"T:C","newName":"Renamed"},"inputs":{{inputs}}}""");
        await Refused("invalid_input", "apply", "--plan", path);
    }

    [Theory]
    [InlineData("A/Injected.cs")]
    [InlineData("global.json")]
    public async Task SourceAndSdkConfigurationNamesAreRefusedBeforePreview(string destination)
    {
        using var directory = new TestDirectory();
        var source = directory.Write("A/Source.cs", "class C {}");
        var sdk = directory.Write("global.json", "unchanged");
        var plan = directory.PathFor(destination);
        await Refused("unsafe_plan_path", "preview", "--request", directory.PathFor("unused.json"), "--plan", plan);
        Assert.Equal("class C {}", File.ReadAllText(source));
        Assert.Equal("unchanged", File.ReadAllText(sdk));
        if (destination != "global.json") Assert.False(File.Exists(plan));
    }

    private static async Task Refused(string code, params string[] args)
    {
        using var output = new StringWriter();
        Assert.Equal(2, await Program.Run(args, output));
        using var json = JsonDocument.Parse(output.ToString());
        Assert.Equal("refused", json.RootElement.GetProperty("status").GetString());
        Assert.Equal(code, json.RootElement.GetProperty("code").GetString());
        Assert.False(json.RootElement.GetProperty("sourceWrites").GetBoolean());
    }
}
