using System.Diagnostics;

namespace Aicf.Dotnet.TestSupport;

internal static class DotnetTestHost
{
    internal sealed record Sdk(string Version, string Root);
    internal sealed record Command(string? Path, string? Fault = null)
    {
        internal string? Skip(string missing) => Fault is null && Path is null ? missing : null;

        internal string Require(string missing) =>
            Fault is not null ? throw new InvalidOperationException(Fault) :
            Path ?? throw new InvalidOperationException(missing);
    }

    private sealed record Inventory(string[] Lines, string? Fault = null);
    private static readonly Lazy<Command> Executable = new(() =>
        DiscoverCommand(OperatingSystem.IsWindows() ? "dotnet.exe" : "dotnet"));
    private static readonly Lazy<Inventory> Sdks = new(() => ReadInventory("--list-sdks"));
    private static readonly Lazy<Inventory> Runtimes = new(() => ReadInventory("--list-runtimes"));

    internal static string? SdkSkip(string version) =>
        Sdks.Value.Fault is null && FindSdk(version) is null
            ? $"The selected dotnet host cannot discover SDK {version}." : null;

    internal static bool SdkProbeFaulted => Sdks.Value.Fault is not null;

    internal static Sdk RequireSdk(string version)
    {
        RequireInventory(Sdks.Value);
        var sdk = FindSdk(version);
        Assert.True(sdk is not null, $"The selected dotnet host cannot discover SDK {version}.");
        return sdk!;
    }

    internal static string RequireExecutable() =>
        Executable.Value.Require("The dotnet executable is missing from PATH.");

    internal static string? TemplateSkip
    {
        get
        {
            if (Sdks.Value.Fault is not null) return null;
            if (TemplateSdk() is null) return "Native templates require a discoverable .NET 10 SDK.";
            if (Runtimes.Value.Fault is not null) return null;
            return HasAspNetRuntime() ? null : "Generated APIs require a discoverable Microsoft.AspNetCore.App 10.0 runtime.";
        }
    }

    internal static Sdk RequireTemplateSdk()
    {
        RequireInventory(Sdks.Value);
        var sdk = TemplateSdk();
        Assert.True(sdk is not null, "Native templates require a discoverable .NET 10 SDK.");
        RequireInventory(Runtimes.Value);
        Assert.True(HasAspNetRuntime(), "Generated APIs require a discoverable Microsoft.AspNetCore.App 10.0 runtime.");
        return sdk!;
    }

    private static Sdk? FindSdk(string version) => InstalledSdks().FirstOrDefault(sdk => sdk.Version == version);

    private static Sdk? TemplateSdk() => InstalledSdks()
        .Where(sdk => Version.TryParse(sdk.Version, out var version) && version.Major == 10)
        .OrderByDescending(sdk => Version.Parse(sdk.Version))
        .FirstOrDefault();

    private static IEnumerable<Sdk> InstalledSdks() => Sdks.Value.Lines.Select(line =>
    {
        var bracket = line.IndexOf(" [", StringComparison.Ordinal);
        return new Sdk(line[..bracket], Path.GetDirectoryName(line[(bracket + 2)..^1])!);
    });

    private static bool HasAspNetRuntime()
    {
        const string prefix = "Microsoft.AspNetCore.App ";
        return Runtimes.Value.Lines
            .Where(line => line.StartsWith(prefix, StringComparison.Ordinal))
            .Select(line => line[prefix.Length..line.IndexOf(" [", StringComparison.Ordinal)])
            .Any(value => Version.TryParse(value, out var version) && version.Major == 10 && version.Minor == 0);
    }

    private static void RequireInventory(Inventory inventory)
    {
        if (inventory.Fault is not null) throw new InvalidOperationException(inventory.Fault);
    }

    private static Inventory ReadInventory(string argument)
    {
        try
        {
            var executable = Executable.Value;
            if (executable.Fault is not null) throw new InvalidOperationException(executable.Fault);
            return executable.Path is null ? new([]) : ReadInventoryAsync(executable.Path, argument).GetAwaiter().GetResult();
        }
        catch (Exception exception)
        {
            return new([], $"dotnet {argument} capability probe failed: {exception.Message}");
        }
    }

    private static async Task<Inventory> ReadInventoryAsync(string executable, string argument)
    {
        var start = new ProcessStartInfo(executable)
        {
            WorkingDirectory = AppContext.BaseDirectory,
            UseShellExecute = false,
            CreateNoWindow = true,
            RedirectStandardOutput = true,
            RedirectStandardError = true
        };
        start.ArgumentList.Add(argument);
        start.Environment.Remove("MSBuildSDKsPath");
        using var process = Process.Start(start) ?? throw new InvalidOperationException("The host did not start.");
        using var deadline = new CancellationTokenSource(TimeSpan.FromSeconds(10));
        var stdout = process.StandardOutput.ReadToEndAsync(deadline.Token);
        var stderr = process.StandardError.ReadToEndAsync(deadline.Token);
        try
        {
            await process.WaitForExitAsync(deadline.Token).ConfigureAwait(false);
            var output = await stdout.ConfigureAwait(false);
            var error = await stderr.ConfigureAwait(false);
            if (process.ExitCode != 0 || !string.IsNullOrWhiteSpace(error))
                throw new InvalidOperationException($"Exit {process.ExitCode}: {error}{output}");

            var lines = output.Split(['\r', '\n'], StringSplitOptions.RemoveEmptyEntries | StringSplitOptions.TrimEntries);
            foreach (var line in lines)
                ValidateLine(line, argument == "--list-runtimes");
            return new(lines);
        }
        catch (OperationCanceledException)
        {
            if (!process.HasExited) process.Kill(entireProcessTree: true);
            await process.WaitForExitAsync().ConfigureAwait(false);
            throw new TimeoutException("The SDK inventory command exceeded ten seconds.");
        }
    }

    private static void ValidateLine(string line, bool runtime)
    {
        var bracket = line.IndexOf(" [", StringComparison.Ordinal);
        if (bracket <= 0 || !line.EndsWith(']'))
            throw new FormatException($"Unrecognized inventory line: {line}");
        var fields = line[..bracket].Split(' ');
        if (fields.Length != (runtime ? 2 : 1) ||
            !Version.TryParse(fields[^1].Split('-', 2)[0], out _))
            throw new FormatException($"Unrecognized inventory line: {line}");
        var directory = line[(bracket + 2)..^1];
        if (!Path.IsPathFullyQualified(directory) || !Directory.Exists(Path.Combine(directory, fields[^1])))
            throw new InvalidOperationException($"Inventory entry does not name an accessible installation: {line}");
    }

    internal static Command DiscoverCommand(string executable)
    {
        try { return new(FindOnPath(executable)); }
        catch (Exception exception) { return new(null, $"Cannot discover {executable} on PATH: {exception.Message}"); }
    }

    private static string? FindOnPath(string executable)
    {
        var path = Environment.GetEnvironmentVariable("PATH") ?? "";
        foreach (var entry in path.Split(Path.PathSeparator, StringSplitOptions.RemoveEmptyEntries))
        {
            var directory = entry.Trim('"');
            if (directory.Length == 0) continue;
            var candidate = Path.Combine(directory, executable);
            try
            {
                if ((File.GetAttributes(candidate) & FileAttributes.Directory) == 0)
                    return Path.GetFullPath(candidate);
            }
            catch (Exception exception) when (exception is FileNotFoundException or DirectoryNotFoundException) { }
        }
        return null;
    }
}
