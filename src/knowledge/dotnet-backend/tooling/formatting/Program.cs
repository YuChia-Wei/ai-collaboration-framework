using System.Security.Cryptography;
using System.Text;
using System.Text.Json;

namespace FormatTool;

internal static class Program
{
    private static readonly WireJson RequestJson = new(new JsonSerializerOptions(WireJson.Default.Options)
    {
        AllowDuplicateProperties = false
    });

    private static async Task<int> Main(string[] args)
    {
        Console.OutputEncoding = new UTF8Encoding(false);
        if (args is ["--help"])
        {
            Console.WriteLine("FormatTool --request <request.json> | --capabilities | --version | --help");
            return 0;
        }
        if (args is ["--version"])
        {
            Console.WriteLine(new Result().ToolVersion);
            return 0;
        }
        if (args is ["--capabilities"])
        {
            var capabilities = new Result { Status = "capabilities",
                Message = "Declared OS/architecture/SDK combinations and their shared rule list; no installed environment was probed." };
            capabilities.IncludeGuidance();
            Console.WriteLine(JsonSerializer.Serialize(capabilities, WireJson.Default.Result));
            return 0;
        }
        var result = new Result();
        var snapshots = new Dictionary<string, string>(Workspace.Paths);
        var verbose = false;
        try
        {
            if (args is not ["--request", var requestPath])
                throw new ToolFailure("invalid-arguments", "Use --request <request.json>.");
            requestPath = Path.GetFullPath(requestPath);
            // Only request parsing is invalid-request; malformed SDK JSON retains its tool-output error.
            var requestText = File.ReadAllText(requestPath);
            Request request;
            try
            {
                request = JsonSerializer.Deserialize(requestText, RequestJson.Request)
                    ?? throw new ToolFailure("invalid-request", "Request must be a JSON object.");
            }
            catch (JsonException error) { throw new ToolFailure("invalid-request", error.Message); }
            verbose = request.Verbose;
            Validate(request);
            var environment = Rules.Environment();
            var workspace = Workspace.FullPath(request.Workspace, Path.GetDirectoryName(requestPath)!);
            result.Workspace = workspace;
            result.PathBase = Path.GetDirectoryName(workspace)!;
            result.Mode = request.Mode;
            result.Action = request.Action;
            result.Diagnostics = request.Diagnostics.Distinct(StringComparer.Ordinal).ToArray();
            result.Severity = request.Severity;
            if (!File.Exists(workspace)) throw new ToolFailure("load-failed", "Workspace does not exist.");
            if (request.Mode != "whitespace" && !Path.GetExtension(workspace).Equals(".csproj", StringComparison.OrdinalIgnoreCase))
                throw new ToolFailure("unsupported-cleanup-workspace", "Cleanup requires a direct .csproj without ProjectReference items. Solution selection is supported for whitespace only.");
            var selected = request.Files.Select(path => Workspace.FullPath(path, result.PathBase)).Distinct(Workspace.Paths).ToArray();
            if (selected.Any(path => !Path.GetExtension(path).Equals(".cs", StringComparison.OrdinalIgnoreCase) || !File.Exists(path)))
                throw new ToolFailure("invalid-selection", "Every selection must be an existing .cs file; folders and globs are not accepted.");
            if (selected.Any(path =>
                Path.IsPathRooted(Path.GetRelativePath(result.PathBase, path)) ||
                Path.GetRelativePath(result.PathBase, path).StartsWith(".." + Path.DirectorySeparatorChar, StringComparison.Ordinal)))
                throw new ToolFailure("unsupported-selection", "SDK include matching requires files inside the workspace directory. For linked files, choose an enclosing solution for whitespace; external/cross-drive selections are unsupported.");
            result.SelectedFiles = selected;
            Snapshot(selected, snapshots);
            var sdk = new Sdk(result, result.PathBase);
            result.SdkVersion = (await sdk.Require("sdk-unavailable", "--version")).StandardOutput!.Trim();
            if (result.SdkVersion != environment.SdkVersion)
                throw new ToolFailure("unsupported-sdk", $"{environment.RuntimeIdentifier} requires SDK {environment.SdkVersion}; actual SDK is {result.SdkVersion}. See --capabilities.");
            result.FormatterVersion = (await sdk.Require("formatter-unavailable", "format", "--version")).StandardOutput!.Trim();
            result.LoadedProjects = Workspace.Projects(workspace);
            if (request.AllowRestore) await sdk.Require("restore-failed", "restore", workspace);
            var loaded = await Workspace.Load(sdk, result.LoadedProjects, request.Mode != "whitespace");
            if (selected.Any(path => !loaded.CompileFiles.ContainsKey(path)))
                throw new ToolFailure("unmatched-selection", "Every selected file must be an evaluated Compile item in the selected workspace.");
            result.SelectedFiles = selected.Select(path => loaded.CompileFiles[path]).ToArray();
            result.ConfigurationFiles = Workspace.Configurations(result.SelectedFiles);
            result.ProjectAnalyzers = loaded.ProjectAnalyzers;
            Snapshot(loaded.ObservedFiles.Where(File.Exists), snapshots);
            if (request.Mode != "whitespace")
            {
                var allowed = request.AllowedProjectAnalyzers.Select(path => Workspace.FullPath(path, result.PathBase)).ToHashSet(Workspace.Paths);
                if (loaded.ProjectAnalyzers.Any(path => !allowed.Contains(path)))
                    throw new ToolFailure("analyzer-consent-required", "External analyzer/source-generator paths require exact allowedProjectAnalyzers opt-in; see projectAnalyzers. No compiler or formatter was run.");
                await CheckSemantics(sdk, workspace);
            }
            var findings = await Format(sdk, result, request.Action == "check");
            result.Findings = findings;
            if (request.Action == "apply")
            {
                if (request.Mode != "whitespace") await CheckSemantics(sdk, workspace);
                result.RemainingFindings = await Format(sdk, result, check: true);
            }
            Observe(result, snapshots);
            if (result.UnexpectedChangedFiles.Length > 0 || (request.Action == "check" && result.ChangedFiles.Length > 0))
                throw new ToolFailure("unexpected-source-change", "Source changed outside the requested write scope; inspect changedFiles. No rollback was attempted.");
            if (result.RemainingFindings.Length > 0)
                throw new ToolFailure("incomplete-apply", "Selected diagnostics remain after apply; inspect actual changes and remainingFindings.");
            result.Status = request.Action == "check" ? (findings.Length > 0 ? "changes-required" : "clean")
                : (result.ChangedFiles.Length > 0 ? "applied" : "clean");
            result.UnreportedSelections = result.SelectedFiles.Except(findings.Select(finding => finding.File), Workspace.Paths).ToArray();
            if (result.UnreportedSelections.Length > 0)
                result.Message = "unreportedSelections have no SDK-reported changes: they may be clean or excluded (including generated code). The SDK report does not distinguish these cases; clean does not prove every selected file was processed.";
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
        if (verbose) result.IncludeGuidance();
        if (!verbose && result.Status != "failed")
            for (var index = 0; index < result.Commands.Count; index++)
                result.Commands[index] = result.Commands[index] with { StandardOutput = null, StandardError = null };
        Console.WriteLine(JsonSerializer.Serialize(result, WireJson.Default.Result));
        return result.Status == "failed" ? 1 : result.Status == "changes-required" ? 2 : 0;
    }

    private static void Validate(Request request)
    {
        if (request.SchemaVersion != 1 || string.IsNullOrWhiteSpace(request.Workspace) || request.Files == null ||
            request.Files.Length == 0 || request.Files.Any(string.IsNullOrWhiteSpace) ||
            request.Mode is not ("whitespace" or "style" or "analyzers") || request.Action is not ("check" or "apply"))
            throw new ToolFailure("invalid-request", "Require schemaVersion 1, workspace, nonempty files, mode whitespace/style/analyzers, and action check/apply.");
        Rules.Validate(request);
    }

    private static async Task<Finding[]> Format(Sdk sdk, Result result, bool check)
    {
        var report = Path.Combine(Path.GetTempPath(), $"aicf-format-{Guid.NewGuid():N}.json");
        try
        {
            var arguments = new List<string> { "format", result.Mode!, result.Workspace!, "--no-restore", "--include" };
            arguments.AddRange(result.SelectedFiles.Select(path =>
            {
                var relative = Path.GetRelativePath(result.PathBase!, path);
                // System.CommandLine expands @response files before interpreting --include.
                // An explicit relative prefix also keeps leading '-' filenames literal.
                // Selection validation keeps paths inside the workspace: SDK glob matching
                // can silently ignore parent-relative and cross-drive files.
                return "." + Path.DirectorySeparatorChar + relative;
            }));
            arguments.AddRange(["--report", report, "--verbosity", "diagnostic"]);
            if (result.Mode != "whitespace")
            {
                arguments.AddRange(["--severity", result.Severity!, "--diagnostics"]);
                arguments.AddRange(result.Diagnostics);
            }
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

    private static Task<CommandResult> CheckSemantics(Sdk sdk, string workspace) =>
        sdk.Require("semantic-prerequisite-failed", "msbuild", workspace, "-nologo", "-target:Compile",
            "-property:BuildProjectReferences=false", "-property:RunAnalyzers=false", "-property:UseSharedCompilation=false");

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
