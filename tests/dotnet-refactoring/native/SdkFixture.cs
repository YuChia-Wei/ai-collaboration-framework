using System.Diagnostics;
using System.Text;
using System.Text.Json;
using System.Xml.Linq;

namespace RefactorTool.Tests;

[CollectionDefinition(Name)]
public sealed class SdkCollection
{
    public const string Name = "Windows SDK integration";
}

internal sealed class SdkFixture : IDisposable
{
    internal const string Version = "10.0.403";
    private readonly TestDirectory directory = new();
    private readonly List<string> junctions = [];
    private readonly string restoreEntry;
    private int sequence;

    internal SdkFixture(bool twoProjects = false)
    {
        directory.Write("global.json", Data.Serialize(new { sdk = new { version = Version, rollForward = "disable" } }));
        directory.Write("A/A.csproj", """<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup><TargetFramework>net10.0</TargetFramework><Nullable>enable</Nullable><GenerateDocumentationFile>true</GenerateDocumentationFile></PropertyGroup></Project>""");
        directory.Write("A/Service.cs", SemanticWorkspace.Service.ReplaceLineEndings("\r\n") + "\r\n");
        if (twoProjects)
        {
            directory.Write("B/B.csproj", """<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup><TargetFramework>net10.0</TargetFramework><GenerateDocumentationFile>true</GenerateDocumentationFile></PropertyGroup><ItemGroup><ProjectReference Include="../A/A.csproj" /></ItemGroup></Project>""");
            directory.Write("B/Use.cs", SemanticWorkspace.Consumer);
            directory.Write("Demo.slnx", """<Solution><Project Path="A/A.csproj" /><Project Path="B/B.csproj" /></Solution>""");
        }
        Workspace = twoProjects ? PathFor("Demo.slnx") : Project;
        restoreEntry = twoProjects ? PathFor("B/B.csproj") : Project;
    }

    internal string Root => directory.Root;
    internal string Workspace { get; }
    internal string Project => PathFor("A/A.csproj");
    internal string Source => PathFor("A/Service.cs");
    internal string Consumer => PathFor("B/Use.cs");
    internal string Output => PathFor("A/ISelected.cs");
    internal string PlanPath { get; private set; } = "";
    internal Request Rename => new() { Workspace = Workspace, Project = Project, Symbol = SemanticWorkspace.GetInt, NewName = "Fetch" };
    internal Request Extract => Rename with
    {
        Operation = "extract-interface", Symbol = "T:Demo.Service", NewName = "ISelected", Namespace = "Contracts",
        OutputFile = Output, Members = [SemanticWorkspace.GetInt, SemanticWorkspace.Property]
    };

    internal string PathFor(string relative) => directory.PathFor(relative);
    internal string Write(string relative, string source) => directory.Write(relative, source);
    internal string Write(string relative, byte[] bytes) => directory.Write(relative, bytes);
    internal void AppendProject(string xml, string relative = "A/A.csproj") =>
        Write(relative, File.ReadAllText(PathFor(relative)).Replace("</Project>", xml + "</Project>"));

    internal async Task Restore(string? entry = null) =>
        await Dotnet("restore", entry ?? restoreEntry, "--source", Root, "-p:NuGetAudit=false");

    internal async Task<string> Dotnet(params string[] args)
    {
        var result = await RunProcess("dotnet", Root, args, TimeSpan.FromSeconds(120));
        Assert.True(result.ExitCode == 0, $"dotnet {string.Join(' ', args)}: {result.Output}{result.Error}");
        return result.Output;
    }

    internal async Task<CommandResult> Preview(Request? request = null, string? planPath = null, string? artifact = null, string? workingDirectory = null)
    {
        sequence++;
        var requestPath = Write($"request{sequence}.json", Data.Serialize(request ?? Rename));
        PlanPath = planPath ?? PathFor($"plan{sequence}.json");
        return await Invoke(["preview", "--request", requestPath, "--plan", PlanPath], artifact, workingDirectory);
    }

    internal async Task<CommandResult> Apply(string? artifact = null) =>
        await Invoke(["apply", "--plan", PlanPath], artifact, null);

    internal Plan Plan() => Data.Read<Plan>(PlanPath);

    internal void RefusedPreview(CommandResult result, string expectedCode)
    {
        result.Refused(expectedCode);
        Assert.False(File.Exists(PlanPath));
    }

    private async Task<CommandResult> Invoke(string[] args, string? artifact, string? workingDirectory)
    {
        if (artifact is not null)
        {
            var run = await RunProcess(artifact, workingDirectory ?? Root, args, TimeSpan.FromSeconds(180));
            Assert.Equal("", run.Error);
            return CommandResult.Parse(run.ExitCode, run.Output);
        }
        using var output = new StringWriter();
        return CommandResult.Parse(await Program.Run(args, output), output.ToString());
    }

    internal async Task Junction(string relative, string target)
    {
        var path = PathFor(relative);
        Directory.CreateDirectory(Path.GetDirectoryName(path)!);
        // This command creates the real OS fixture. Assertions remain in xUnit.
        var result = await RunProcess("pwsh", Root,
            ["-NoProfile", "-Command", "$ErrorActionPreference='Stop'; New-Item -ItemType Junction -Path $env:REFACTOR_TEST_LINK -Target $env:REFACTOR_TEST_TARGET | Out-Null"],
            TimeSpan.FromSeconds(30), new Dictionary<string, string> { ["REFACTOR_TEST_LINK"] = path, ["REFACTOR_TEST_TARGET"] = target });
        Assert.True(result.ExitCode == 0, result.Output + result.Error);
        junctions.Add(path);
    }

    internal void RemoveJunction(string relative)
    {
        var path = PathFor(relative);
        Assert.True(File.GetAttributes(path).HasFlag(FileAttributes.ReparsePoint));
        Directory.Delete(path);
        Assert.True(junctions.Remove(path));
    }

    internal Dictionary<string, byte[]> Snapshot() => Directory.EnumerateFiles(Root, "*.cs", SearchOption.AllDirectories)
        .Where(path => !Path.GetRelativePath(Root, path).Split(Path.DirectorySeparatorChar).SkipLast(1).Any(p => p is "obj" or "bin" or "artifacts"))
        .ToDictionary(path => path, File.ReadAllBytes, StringComparer.OrdinalIgnoreCase);

    internal void AssertSnapshot(Dictionary<string, byte[]> original)
    {
        var after = Snapshot();
        Assert.Equal(original.Keys.Order(), after.Keys.Order());
        foreach (var (path, bytes) in original) Assert.Equal(bytes, after[path]);
    }

    internal string AddExecutableConsumer(string source)
    {
        var path = PathFor("B/B.csproj");
        var xml = XDocument.Load(path);
        xml.Root!.Element("PropertyGroup")!.Add(new XElement("OutputType", "Exe"));
        xml.Save(path);
        Write("B/Program.cs", source);
        return path;
    }

    public void Dispose()
    {
        foreach (var path in junctions.AsEnumerable().Reverse())
        {
            if (File.GetAttributes(path).HasFlag(FileAttributes.ReparsePoint)) Directory.Delete(path);
        }
        directory.Dispose();
    }

    private static async Task<(int ExitCode, string Output, string Error)> RunProcess(string executable, string cwd,
        string[] args, TimeSpan limit, Dictionary<string, string>? environment = null)
    {
        var start = new ProcessStartInfo(executable)
        {
            WorkingDirectory = cwd, UseShellExecute = false, CreateNoWindow = true, RedirectStandardOutput = true, RedirectStandardError = true,
            StandardOutputEncoding = Encoding.UTF8, StandardErrorEncoding = Encoding.UTF8
        };
        foreach (var arg in args) start.ArgumentList.Add(arg);
        start.Environment["DOTNET_CLI_UI_LANGUAGE"] = "en-US";
        // A reusable build node can retain this process's redirected pipes.
        // Keep test fixture commands isolated and finish their output with the command.
        start.Environment["MSBUILDDISABLENODEREUSE"] = "1";
        start.Environment["DOTNET_CLI_USE_MSBUILD_SERVER"] = "0";
        if (environment is not null)
            foreach (var (key, value) in environment) start.Environment[key] = value;
        using var process = Process.Start(start)!;
        using var timeout = new CancellationTokenSource(limit);
        var output = process.StandardOutput.ReadToEndAsync(timeout.Token);
        var error = process.StandardError.ReadToEndAsync(timeout.Token);
        try
        {
            await process.WaitForExitAsync(timeout.Token);
            return (process.ExitCode, await output, await error);
        }
        catch (OperationCanceledException)
        {
            var exited = process.HasExited;
            if (!exited) process.Kill(entireProcessTree: true);
            await process.WaitForExitAsync();
            throw new TimeoutException($"{executable} {string.Join(' ', args)} exceeded {limit} while {(exited ? "draining output" : "waiting for exit")}.");
        }
    }
}

internal sealed record CommandResult(int ExitCode, JsonElement Json)
{
    internal static CommandResult Parse(int exitCode, string output)
    {
        using var json = JsonDocument.Parse(output);
        return new(exitCode, json.RootElement.Clone());
    }

    internal void Refused(string code)
    {
        Assert.True(ExitCode == 2, Json.GetRawText());
        Assert.Equal("refused", Text("status"));
        Assert.Equal(code, Text("code"));
        Assert.False(Json.GetProperty("sourceWrites").GetBoolean());
    }

    internal string Text(string field) => Json.GetProperty(field).GetString()!;

    internal void Previewed()
    {
        Assert.True(ExitCode == 0, Json.GetRawText());
        Assert.Equal("previewed", Text("status"));
    }

    internal void Applied()
    {
        Assert.True(ExitCode == 0, Json.GetRawText());
        Assert.Equal("applied", Text("status"));
        Assert.NotEmpty(Json.GetProperty("files").EnumerateArray());
        Assert.All(Json.GetProperty("files").EnumerateArray(), f => Assert.Equal("applied", f.GetProperty("state").GetString()));
    }
}
