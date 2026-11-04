using System.Security.Cryptography;
using System.Text;
using System.Text.Json;

namespace FormatTool;

internal static class Program
{
    private const string SupportedSdk = "10.0.403";

    private static async Task<int> Main(string[] args)
    {
        Console.OutputEncoding = new UTF8Encoding(false);
        if (args is ["--help"])
        {
            Console.WriteLine("FormatTool --request <request.json> | --version | --help");
            return 0;
        }
        if (args is ["--version"])
        {
            Console.WriteLine(typeof(Program).Assembly.GetName().Version);
            return 0;
        }
        var result = new Result();
        var snapshots = new Dictionary<string, string>(Workspace.Paths);
        try
        {
            if (args is not ["--request", var requestPath])
                throw new ToolFailure("invalid-arguments", "Use --request <request.json>.");
            requestPath = Path.GetFullPath(requestPath);
            var request = JsonSerializer.Deserialize(File.ReadAllText(requestPath), WireJson.Default.Request)
                ?? throw new ToolFailure("invalid-request", "Request must be a JSON object.");
            Validate(request);
            var workspace = Workspace.FullPath(request.Workspace, Path.GetDirectoryName(requestPath)!);
            result.Workspace = workspace;
            result.PathBase = Path.GetDirectoryName(workspace)!;
            result.Mode = request.Mode;
            result.Action = request.Action;
            if (!File.Exists(workspace)) throw new ToolFailure("load-failed", "Workspace does not exist.");
            var selected = request.Files.Select(path => Workspace.FullPath(path, result.PathBase)).Distinct(Workspace.Paths).ToArray();
            if (selected.Any(path => Path.GetExtension(path) != ".cs" || !File.Exists(path)))
                throw new ToolFailure("invalid-selection", "Every selection must be an existing .cs file; folders and globs are not accepted.");
            result.SelectedFiles = selected;
            Snapshot(selected, snapshots);
            var sdk = new Sdk(result, result.PathBase);
            result.SdkVersion = (await sdk.Require("sdk-unavailable", "--version")).StandardOutput.Trim();
            if (result.SdkVersion != SupportedSdk)
                throw new ToolFailure("unsupported-sdk", $"This initial support contract requires SDK {SupportedSdk}; actual SDK is {result.SdkVersion}.");
            result.FormatterVersion = (await sdk.Require("formatter-unavailable", "format", "--version")).StandardOutput.Trim();
            result.LoadedProjects = Workspace.Projects(workspace);
            if (request.AllowRestore) await sdk.Require("restore-failed", "restore", workspace);
            var compile = await Workspace.CompileFiles(sdk, result.LoadedProjects);
            if (selected.Any(path => !compile.ContainsKey(path)))
                throw new ToolFailure("unmatched-selection", "Every selected file must be an evaluated Compile item in the selected workspace.");
            result.SelectedFiles = selected.Select(path => compile[path]).ToArray();
            result.ConfigurationFiles = Workspace.Configurations(result.SelectedFiles);
            Snapshot(compile.Keys.Where(File.Exists), snapshots);
            var findings = await Format(sdk, result, request.Action == "check");
            result.Findings = findings;
            if (request.Action == "apply")
                result.RemainingFindings = await Format(sdk, result, check: true);
            Observe(result, snapshots);
            if (result.UnexpectedChangedFiles.Length > 0 || (request.Action == "check" && result.ChangedFiles.Length > 0))
                throw new ToolFailure("unexpected-source-change", "Source changed outside the requested write scope; inspect changedFiles. No rollback was attempted.");
            if (result.RemainingFindings.Length > 0)
                throw new ToolFailure("incomplete-apply", "Selected diagnostics remain after apply; inspect actual changes and remainingFindings.");
            result.Status = request.Action == "check" ? (findings.Length > 0 ? "changes-required" : "clean")
                : (result.ChangedFiles.Length > 0 ? "applied" : "clean");
        }
        catch (ToolFailure error)
        {
            result.ErrorCode = error.Code;
            result.Message = error.Message;
        }
        catch (Exception error) when (error is IOException or UnauthorizedAccessException or JsonException or ArgumentException or System.Xml.XmlException or InvalidOperationException or KeyNotFoundException)
        {
            result.ErrorCode = "invalid-input-or-tool-output";
            result.Message = error.Message;
        }
        Observe(result, snapshots);
        Console.WriteLine(JsonSerializer.Serialize(result, WireJson.Default.Result));
        return result.Status == "failed" ? 1 : result.Status == "changes-required" ? 2 : 0;
    }

    private static void Validate(Request request)
    {
        if (request.SchemaVersion != 1 || string.IsNullOrWhiteSpace(request.Workspace) || request.Files == null ||
            request.Files.Length == 0 || request.Files.Any(string.IsNullOrWhiteSpace) ||
            request.Mode != "whitespace" || request.Action is not ("check" or "apply"))
            throw new ToolFailure("invalid-request", "Require schemaVersion 1, workspace, nonempty files, mode whitespace, and action check or apply.");
        if (!OperatingSystem.IsWindows())
            throw new ToolFailure("unsupported-platform", "Initial supported platform is Windows; Linux and macOS acceptance is not established.");
    }

    private static async Task<Finding[]> Format(Sdk sdk, Result result, bool check)
    {
        var report = Path.Combine(Path.GetTempPath(), $"aicf-format-{Guid.NewGuid():N}.json");
        try
        {
            var arguments = new List<string> { "format", result.Mode!, result.Workspace!, "--no-restore", "--include" };
            arguments.AddRange(result.SelectedFiles.Select(path => Path.GetRelativePath(result.PathBase!, path)));
            arguments.AddRange(["--report", report, "--verbosity", "diagnostic"]);
            if (check) arguments.Add("--verify-no-changes");
            var command = await sdk.Run(arguments.ToArray());
            if (command.ExitCode != 0 && !(check && command.ExitCode == 2))
                throw new ToolFailure("format-failed", "Formatter failed; source may be partially changed. Inspect changedFiles and commands before recovery.");
            if (!File.Exists(report)) throw new ToolFailure("invalid-report", "Formatter did not produce its required report.");
            using var document = JsonDocument.Parse(File.ReadAllText(report));
            var findings = new List<Finding>();
            foreach (var item in document.RootElement.EnumerateArray())
            {
                var path = Workspace.FullPath(item.GetProperty("FilePath").GetString()!, result.PathBase!);
                if (!result.SelectedFiles.Contains(path, Workspace.Paths))
                    throw new ToolFailure("unexpected-report-scope", "Formatter reported an unselected file.");
                foreach (var change in item.GetProperty("FileChanges").EnumerateArray())
                    findings.Add(new(path, change.GetProperty("DiagnosticId").GetString()!, change.GetProperty("LineNumber").GetInt32(),
                        change.GetProperty("CharNumber").GetInt32(), change.GetProperty("FormatDescription").GetString()!));
            }
            if (check && ((command.ExitCode == 2) != (findings.Count > 0)))
                throw new ToolFailure("inconsistent-report", "Formatter exit code and report disagree; no clean result is inferred.");
            return findings.ToArray();
        }
        finally
        {
            if (File.Exists(report)) File.Delete(report);
        }
    }

    private static void Snapshot(IEnumerable<string> files, Dictionary<string, string> snapshots)
    {
        foreach (var file in files) snapshots.TryAdd(file, Hash(file));
    }

    private static string Hash(string path) => Convert.ToHexString(SHA256.HashData(File.ReadAllBytes(path)));

    private static void Observe(Result result, Dictionary<string, string> snapshots)
    {
        var changed = new List<string>();
        foreach (var pair in snapshots)
        {
            try { if (!File.Exists(pair.Key) || Hash(pair.Key) != pair.Value) changed.Add(pair.Key); }
            catch (Exception error) when (error is IOException or UnauthorizedAccessException) { changed.Add(pair.Key); }
        }
        result.ChangedFiles = changed.Order(Workspace.Paths).ToArray();
        result.UnexpectedChangedFiles = result.ChangedFiles.Except(result.SelectedFiles, Workspace.Paths).ToArray();
    }
}
