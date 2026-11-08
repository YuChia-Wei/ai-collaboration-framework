using System.Diagnostics;

namespace Generation.TestSupport;

internal sealed class GenerationFixture : IDisposable
{
    public static bool RunSdkTests => Environment.GetEnvironmentVariable("AICF_GENERATION_SDK_TESTS") == "1";

    public string Root { get; } = Directory.CreateDirectory(Path.Combine(
        Path.GetFullPath(Environment.GetEnvironmentVariable("AICF_TEST_WORK") ?? Path.GetTempPath()),
        $"generation-{Guid.NewGuid():N}")).FullName;

    public string Write(string relativePath, string contents)
    {
        var path = Path.GetFullPath(relativePath, Root);
        Directory.CreateDirectory(Path.GetDirectoryName(path)!);
        File.WriteAllText(path, contents);
        return path;
    }

    public async Task<string> Dotnet(params string[] arguments)
    {
        var result = await Execute("dotnet", TimeSpan.FromMinutes(2), arguments);
        Assert.True(result.Exit == 0, $"dotnet {string.Join(' ', arguments)} exited {result.Exit}\n{result.Output}\n{result.Error}");
        return result.Output;
    }

    // Dedicated test processes must close their redirected output when the build returns.
    public Task<string> Build(string project, string configuration = "Debug") =>
        Dotnet("build", project, "-c", configuration, "--source", Root, "--disable-build-servers");

    public Process Start(string executable, string[] arguments, string? workingDirectory = null)
    {
        var start = new ProcessStartInfo(executable)
        {
            WorkingDirectory = workingDirectory ?? Root,
            UseShellExecute = false,
            CreateNoWindow = true,
            RedirectStandardOutput = true,
            RedirectStandardError = true
        };
        foreach (var argument in arguments)
            start.ArgumentList.Add(argument);
        return Process.Start(start)!;
    }

    public async Task<(int Exit, string Output, string Error)> Execute(
        string executable, TimeSpan limit, params string[] arguments)
    {
        using var process = Start(executable, arguments);
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
            var stopped = process.HasExited;
            if (!stopped)
                process.Kill(entireProcessTree: true);
            await process.WaitForExitAsync();
            var phase = stopped ? "reading redirected output after exit" : "waiting for process exit";
            throw new TimeoutException($"{executable} {string.Join(' ', arguments)} exceeded {limit} while {phase}.");
        }
    }

    public static string ExistingArtifact(string? path, string variable)
    {
        Assert.False(string.IsNullOrWhiteSpace(path), $"Supply an absolute artifact path with {variable}.");
        Assert.True(Path.IsPathFullyQualified(path) && File.Exists(path), $"Selected artifact is missing: {path}");
        return path;
    }

    public void Dispose() => Directory.Delete(Root, recursive: true);
}
