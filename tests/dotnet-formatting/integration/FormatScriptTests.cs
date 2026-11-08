using System.Diagnostics;
using Aicf.Dotnet.TestSupport;

namespace Formatting.ScriptIntegrationTests;

/// <summary>Exercises the source script with a real SDK and a disposable project.</summary>
public sealed class FormatScriptTests : IDisposable
{
    private const string Chosen = "A & B.cs";
    private const string Unselected = "Unselected.cs";
    private const string Original = "class Chosen{int value=1;}\n";
    private const string Other = "class Unselected{int value=1;}\n";
    private static readonly string Script = Path.Combine(AppContext.BaseDirectory, "Format-Dotnet.ps1");
    private readonly string root = Directory.CreateDirectory(Path.Combine(
        Environment.GetEnvironmentVariable("AICF_TEST_WORK") ?? Path.GetTempPath(),
        $"format-{Guid.NewGuid():N}")).FullName;

    private string Workspace => Path.Combine(root, "Workspace With Spaces");
    private string Project => Path.Combine(Workspace, "Example.csproj");
    private string Dotnet => DotnetTestHost.RequireExecutable();

    /// <summary>Checks explicit selection, refuses redirected paths or extra include values, and applies only the chosen file.</summary>
    [PowerShellFact]
    public async Task CheckAndApplyFromOutsideWorkspace()
    {
        Directory.CreateDirectory(Workspace);
        File.WriteAllText(Project, """
            <Project Sdk="Microsoft.NET.Sdk">
              <PropertyGroup><TargetFramework>net10.0</TargetFramework></PropertyGroup>
            </Project>
            """);
        File.WriteAllText(Path.Combine(Workspace, "global.json"),
            """{"sdk":{"version":"10.0.100","rollForward":"latestFeature"}}""");
        File.WriteAllText(Path.Combine(Workspace, ".editorconfig"), """
            root = true
            [*.cs]
            indent_style = space
            indent_size = 4
            csharp_preserve_single_line_blocks = false
            """);
        var chosenPath = Path.Combine(Workspace, Chosen);
        var otherPath = Path.Combine(Workspace, Unselected);
        File.WriteAllText(chosenPath, Original);
        File.WriteAllText(otherPath, Other);
        var restore = await Run(Dotnet, Workspace, "restore", Project, "--source", Workspace);
        Assert.True(restore.Exit == 0, restore.Output);

        var check = await Format(Project, "-Files", Chosen);
        Assert.True(check.Exit != 0, check.Output);
        Assert.Equal(Original, File.ReadAllText(chosenPath));
        Assert.Equal(Other, File.ReadAllText(otherPath));

        var solution = Path.Combine(Directory.CreateDirectory(Path.Combine(Workspace, "solution")).FullName, "Example.slnx");
        File.WriteAllText(solution, """<Solution><Project Path="../Example.csproj" /></Solution>""");
        var refused = await Format(solution, "-Files", "../" + Chosen, "-Apply");
        Assert.True(refused.Exit != 0, refused.Output);
        Assert.Contains("Selected file must be under the workspace directory", refused.Output);
        Assert.Equal(Original, File.ReadAllText(chosenPath));
        Assert.Equal(Other, File.ReadAllText(otherPath));

        var caseAlias = Path.Combine(Directory.CreateDirectory(Path.Combine(root, "workspace with spaces")).FullName, Chosen);
        File.WriteAllText(caseAlias, Original);
        var redirected = await Format(Project, "-Files", caseAlias, "-Apply");
        Assert.True(redirected.Exit != 0, redirected.Output);
        Assert.Contains("Selected file must be under the workspace directory", redirected.Output);
        Assert.Equal(Original, File.ReadAllText(chosenPath));
        Assert.Equal(Original, File.ReadAllText(caseAlias));

        var extraSelection = await Format(Project, "-Files", Chosen, "-Apply", "-SdkOptions", "./" + Unselected);
        Assert.True(extraSelection.Exit != 0, extraSelection.Output);
        Assert.Equal(Original, File.ReadAllText(chosenPath));
        Assert.Equal(Other, File.ReadAllText(otherPath));

        var apply = await Format(Project, "-Files", chosenPath, "-Apply");
        Assert.True(apply.Exit == 0, apply.Output);
        Assert.Contains("    int value = 1;", File.ReadAllText(chosenPath));
        Assert.Equal(Other, File.ReadAllText(otherPath));
    }

    /// <summary>Rejects ambiguous literal paths before SDK execution and propagates the workspace's native SDK failure.</summary>
    [PowerShellFact]
    public async Task PropagatesNativeSdkResolutionFailure()
    {
        Directory.CreateDirectory(Workspace);
        File.WriteAllText(Project, "<Project />");
        File.WriteAllText(Path.Combine(Workspace, "global.json"),
            """{"sdk":{"version":"999.0.100","rollForward":"disable"}}""");

        var ambiguousNames = OperatingSystem.IsWindows() ? new[] { "A*.cs", "A?.cs" } : new[] { "A*.cs", "A?.cs", @"A\B.cs" };
        foreach (var name in ambiguousNames)
        {
            if (!OperatingSystem.IsWindows()) File.WriteAllText(Path.Combine(Workspace, name), Original);
            var refused = await Format(Project, "-Files", name, "-Apply");
            Assert.True(refused.Exit != 0, refused.Output);
            Assert.Contains("Selected file cannot contain SDK glob characters or a POSIX backslash", refused.Output);
            if (!OperatingSystem.IsWindows()) Assert.Equal(Original, File.ReadAllText(Path.Combine(Workspace, name)));
        }

        var native = await Run(Dotnet, Workspace, "format", "whitespace", Project,
            "--no-restore", "--verify-no-changes");
        var result = await Format(Project, "-WholeWorkspace");

        Assert.True(native.Exit != 0, native.Output);
        Assert.Equal(native.Exit, result.Exit);
        Assert.Contains("999.0.100", result.Output);
    }

    private Task<(int Exit, string Output)> Format(string workspace, params string[] options) =>
        Run(PowerShellFactAttribute.Host.Require("PowerShell 7 is missing from PATH."), root,
            ["-NoProfile", "-NonInteractive", "-File", Script, "-Workspace",
             Path.GetRelativePath(root, workspace), .. options]);

    private static async Task<(int Exit, string Output)> Run(
        string command, string directory, params string[] args)
    {
        var start = new ProcessStartInfo(command)
        {
            WorkingDirectory = directory,
            UseShellExecute = false,
            RedirectStandardOutput = true,
            RedirectStandardError = true
        };
        start.Environment.Remove("MSBuildSDKsPath");
        foreach (var argument in args)
            start.ArgumentList.Add(argument);

        using var process = Process.Start(start)!;
        using var deadline = new CancellationTokenSource(TimeSpan.FromSeconds(60));
        var stdout = process.StandardOutput.ReadToEndAsync(deadline.Token);
        var stderr = process.StandardError.ReadToEndAsync(deadline.Token);
        try
        {
            await process.WaitForExitAsync(deadline.Token);
            return (process.ExitCode, (await stdout) + (await stderr));
        }
        catch (OperationCanceledException)
        {
            if (!process.HasExited)
                process.Kill(entireProcessTree: true);
            await process.WaitForExitAsync();
            throw new TimeoutException($"{command} did not exit within one minute.");
        }
    }

    /// <summary>Removes the disposable project after its processes finish.</summary>
    public void Dispose() => Directory.Delete(root, recursive: true);
}

internal sealed class PowerShellFactAttribute : FactAttribute
{
    internal static readonly DotnetTestHost.Command Host = DiscoverHost();

    public PowerShellFactAttribute() => Skip = Host.Skip("PowerShell 7.3 or later is required.");

    private static DotnetTestHost.Command DiscoverHost()
    {
        var command = DotnetTestHost.DiscoverCommand(OperatingSystem.IsWindows() ? "pwsh.exe" : "pwsh");
        if (command.Path is null) return command;
        try
        {
            var start = new ProcessStartInfo(command.Path) { UseShellExecute = false, CreateNoWindow = true };
            foreach (var argument in new[] { "-NoProfile", "-NonInteractive", "-Command",
                "if ($PSVersionTable.PSVersion -ge [version]'7.3') { exit 0 }; exit 42" })
                start.ArgumentList.Add(argument);
            using var process = Process.Start(start)!;
            if (!process.WaitForExit(10_000))
            {
                process.Kill(entireProcessTree: true);
                process.WaitForExit();
                return new(null, "PowerShell version probe exceeded ten seconds.");
            }
            return process.ExitCode switch
            {
                0 => command,
                42 => new(null),
                _ => new(null, $"PowerShell version probe failed with exit {process.ExitCode}.")
            };
        }
        catch (Exception exception) { return new(null, $"PowerShell version probe failed: {exception.Message}"); }
    }
}
