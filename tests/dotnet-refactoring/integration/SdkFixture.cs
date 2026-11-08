using System.Text.Json;
using System.Xml.Linq;

namespace RefactorTool.IntegrationTests;

[CollectionDefinition(Name)]
public sealed class SdkCollection
{
    public const string Name = "Windows SDK integration";
}

internal sealed class SdkFixture : IDisposable
{
    internal const string Version = "10.0.403";
    private readonly TestDirectory directory = new();
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
        var result = await TestDirectory.RunProcess("dotnet", Root, args, TimeSpan.FromSeconds(120));
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
        // SDK-backed commands can block inside Roslyn or MSBuild. A child
        // process gives each command its own deadline and a stoppable writer.
        var tool = artifact ?? Path.Combine(AppContext.BaseDirectory, "RefactorTool.exe");
        Assert.True(File.Exists(tool), $"Missing RefactorTool executable: {tool}");
        var run = await TestDirectory.RunProcess(tool, workingDirectory ?? Root, args, TimeSpan.FromSeconds(180));
        Assert.Equal("", run.Error);
        return CommandResult.Parse(run.ExitCode, run.Output);
    }

    internal Task Junction(string relative, string target) => directory.Junction(relative, target);

    internal void RemoveJunction(string relative) => directory.RemoveJunction(relative);

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

    public void Dispose() => directory.Dispose();
}

internal sealed record CommandResult(int ExitCode, JsonElement Json)
{
    internal static async Task<CommandResult> Run(params string[] args)
    {
        using var output = new StringWriter();
        var exit = await Program.Run(args, output);
        return Parse(exit, output.ToString());
    }

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
