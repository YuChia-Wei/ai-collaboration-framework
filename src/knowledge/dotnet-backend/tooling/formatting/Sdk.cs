using System.Diagnostics;

namespace FormatTool;

internal sealed class Sdk(Result result, string workingDirectory)
{
    public async Task<CommandResult> Run(params string[] arguments)
    {
        var start = new ProcessStartInfo("dotnet")
        {
            WorkingDirectory = workingDirectory,
            UseShellExecute = false,
            RedirectStandardOutput = true,
            RedirectStandardError = true,
            CreateNoWindow = true
        };
        foreach (var argument in arguments) start.ArgumentList.Add(argument);
        using var process = new Process { StartInfo = start };
        try
        {
            process.Start();
        }
        catch (System.ComponentModel.Win32Exception error)
        {
            throw new ToolFailure("sdk-unavailable", error.Message);
        }
        var output = process.StandardOutput.ReadToEndAsync();
        var errorOutput = process.StandardError.ReadToEndAsync();
        using var timeout = new CancellationTokenSource(TimeSpan.FromMinutes(2));
        try
        {
            await process.WaitForExitAsync(timeout.Token);
        }
        catch (OperationCanceledException)
        {
            process.Kill(entireProcessTree: true);
            await process.WaitForExitAsync();
            result.Commands.Add(new(arguments, workingDirectory, -1, await output, await errorOutput));
            throw new ToolFailure("tool-timeout", "SDK command exceeded two minutes; inspect changedFiles before retrying.");
        }
        var command = new CommandResult(arguments, workingDirectory, process.ExitCode, await output, await errorOutput);
        result.Commands.Add(command);
        return command;
    }

    public async Task<CommandResult> Require(string code, params string[] arguments)
    {
        var command = await Run(arguments);
        if (command.ExitCode != 0) throw new ToolFailure(code, "SDK command failed; see commands for its exact output.");
        return command;
    }
}
