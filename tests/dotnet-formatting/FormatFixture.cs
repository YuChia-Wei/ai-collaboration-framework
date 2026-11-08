using Aicf.Dotnet.TestSupport;
using System.Diagnostics;
using System.Runtime.InteropServices;
using System.Text.Json;
using FormatTool;

namespace FormatTool.IntegrationTests;

internal sealed class FormatFixture : IDisposable
{
    public const string Original = "class Chosen{\nvoid Run(){\nint value=1;\n}\n}\n";
    public const string UserEdit = "class UserEdit{int Value=  0; int Read(){var n=1; return Value+n;}} // preserve my edit\n";
    private const string EditorConfig = """
        root = true
        [*.cs]
        indent_style = space
        indent_size = 4
        end_of_line = lf
        csharp_preserve_single_line_blocks = false
        csharp_preserve_single_line_statements = false
        csharp_style_var_for_built_in_types = false:warning
        dotnet_diagnostic.IDE0008.severity = warning
        dotnet_diagnostic.CA1805.severity = warning
        """;
    private const string ProjectBody = """
        <PropertyGroup><TargetFramework>net10.0</TargetFramework></PropertyGroup>
        <ItemGroup><Compile Remove="Excluded.cs" /></ItemGroup>
        """;
    internal static string? SdkVersion =>
        OperatingSystem.IsWindows() && RuntimeInformation.ProcessArchitecture == Architecture.X64 ? "10.0.403" :
        MacArm64 ? "10.0.400" : null;
    internal static bool MacArm64 => OperatingSystem.IsMacOS() && RuntimeInformation.ProcessArchitecture == Architecture.Arm64;
    private bool sdkPinned;

    public string Root { get; }
    public string Chosen { get; }
    public string Unselected { get; }
    public string Project => Path.Combine(Root, "App", "App.csproj");

    public FormatFixture(string? scratchRoot = null, bool requestOnly = false)
    {
        Root = Directory.CreateDirectory(Path.Combine(
            Path.GetFullPath(scratchRoot ?? Environment.GetEnvironmentVariable("AICF_TEST_WORK") ?? Path.GetTempPath()),
            $"format-{Guid.NewGuid():N}")).FullName;
        Chosen = Path.Combine(Root, "App", "Nested", "Chosen.cs");
        Unselected = Path.Combine(Root, "App", "Unselected.cs");
        if (requestOnly) return;

        Write("App/Nested/Chosen.cs", Original);
        Write("App/Unselected.cs", UserEdit);
        Write("App/.editorconfig", EditorConfig + "\n");
        Write("App/Nested/.editorconfig", "[*.cs]\nindent_size = 2\n");
        Write("App/Excluded.cs", "class Excluded{}\n");
        WriteProject();
    }

    public string Write(string relativePath, string contents)
    {
        var path = Path.GetFullPath(Path.Combine(Root, relativePath));
        Directory.CreateDirectory(Path.GetDirectoryName(path)!);
        File.WriteAllText(path, contents);
        return path;
    }

    public void WriteProject(string extra = "", bool explicitCompile = false)
    {
        var property = explicitCompile ? "<EnableDefaultCompileItems>false</EnableDefaultCompileItems>" : "";
        Write("App/App.csproj", "<Project Sdk=\"Microsoft.NET.Sdk\">" +
            ProjectBody.Replace("</PropertyGroup>", property + "</PropertyGroup>") + extra + "</Project>");
    }

    public void PinSdk()
    {
        var selected = DotnetTestHost.RequireSdk(SdkVersion ?? throw new InvalidOperationException("Unsupported formatter SDK host."));
        Write("global.json", JsonSerializer.Serialize(new
        {
            sdk = new { version = selected.Version, rollForward = "disable", paths = new[] { selected.Root } }
        }));
        sdkPinned = true;
    }

    public Task Restore()
    {
        PinSdk();
        return Dotnet("restore", Project, "--source", Root);
    }

    public async Task Dotnet(params string[] arguments)
    {
        var (exit, output, error) = await Execute(DotnetTestHost.RequireExecutable(), arguments, TimeSpan.FromSeconds(120));
        Assert.True(exit == 0, $"dotnet {string.Join(' ', arguments)} exited {exit}\n{output}\n{error}");
    }

    public async Task<(int Exit, JsonElement Result)> Invoke(
        string? raw = null, string workspace = "App/App.csproj", string[]? files = null,
        string mode = "whitespace", string action = "check", string[]? diagnostics = null,
        string? severity = null, bool verbose = false, string[]? allowed = null, string? artifact = null)
    {
        var request = Write("request.json", raw ?? JsonSerializer.Serialize(new
        {
            schemaVersion = 1, workspace, files = files ?? ["Nested/Chosen.cs"], mode, action,
            diagnostics = diagnostics ?? [], severity, verbose, allowedProjectAnalyzers = allowed ?? []
        }));
        if (artifact is not null || sdkPinned)
        {
            var arguments = artifact is null
                ? new[] { Path.Combine(AppContext.BaseDirectory, "FormatTool.dll"), "--request", request }
                : ["--request", request];
            var (exit, output, error) = await Execute(artifact ?? DotnetTestHost.RequireExecutable(), arguments, TimeSpan.FromSeconds(180));
            Assert.Empty(error);
            using var processJson = JsonDocument.Parse(output);
            return (exit, processJson.RootElement.Clone());
        }
        using var writer = new StringWriter();
        var code = await Program.Run(["--request", request], writer);
        using var json = JsonDocument.Parse(writer.ToString());
        return (code, json.RootElement.Clone());
    }

    private async Task<(int Exit, string Output, string Error)> Execute(
        string executable, string[] arguments, TimeSpan limit)
    {
        var start = new ProcessStartInfo(executable)
        {
            WorkingDirectory = Root,
            UseShellExecute = false,
            CreateNoWindow = true,
            RedirectStandardOutput = true,
            RedirectStandardError = true
        };
        start.Environment.Remove("MSBuildSDKsPath");
        foreach (var argument in arguments)
            start.ArgumentList.Add(argument);
        using var process = Process.Start(start)!;
        using var deadline = new CancellationTokenSource(limit);
        var output = process.StandardOutput.ReadToEndAsync(deadline.Token);
        var error = process.StandardError.ReadToEndAsync(deadline.Token);
        try
        {
            await process.WaitForExitAsync(deadline.Token);
            return (process.ExitCode, await output, await error);
        }
        catch (OperationCanceledException)
        {
            if (!process.HasExited)
                process.Kill(entireProcessTree: true);
            await process.WaitForExitAsync();
            throw new TimeoutException($"{executable} {string.Join(' ', arguments)} exceeded {limit}.");
        }
    }

    public static string? Text(JsonElement result, string name) => result.GetProperty(name).GetString();

    public static JsonElement[] Items(JsonElement result, string name) => result.GetProperty(name).EnumerateArray().ToArray();

    public static void Outcome((int Exit, JsonElement Result) run, int exit, string status)
    {
        Assert.True((run.Exit, Text(run.Result, "status")) == (exit, status), run.Result.ToString());
    }

    public static void Failure((int Exit, JsonElement Result) run, string code)
    {
        Outcome(run, 1, "failed");
        Assert.Equal(code, Text(run.Result, "errorCode"));
    }

    public void Dispose() => Directory.Delete(Root, recursive: true);
}

internal sealed class FormatHostFactAttribute : FactAttribute
{
    public FormatHostFactAttribute() => Skip = HostSkip();

    internal static string? HostSkip(bool posixOnly = false) => FormatFixture.SdkVersion is null ?
        "FormatTool path handling requires Windows x64 or macOS arm64." :
        posixOnly && OperatingSystem.IsWindows() ? "Windows does not permit these literal filename characters." : null;
}

internal sealed class FormatHostTheoryAttribute : TheoryAttribute
{
    public FormatHostTheoryAttribute(bool posixOnly = false) => Skip = FormatHostFactAttribute.HostSkip(posixOnly);
}

internal sealed class FormatSdkFactAttribute : FactAttribute
{
    public FormatSdkFactAttribute() => Skip = FormatFixture.SdkVersion is { } version
        ? DotnetTestHost.SdkSkip(version)
        : "Formatter SDK integration requires Windows x64 or macOS arm64.";
}
