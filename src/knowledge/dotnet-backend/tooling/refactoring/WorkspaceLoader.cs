using System.Diagnostics;
using System.Text.Json;
using System.Text.RegularExpressions;
using System.Xml.Linq;
using Microsoft.CodeAnalysis;
using Microsoft.CodeAnalysis.CSharp;
using Microsoft.CodeAnalysis.MSBuild;

namespace RefactorTool;

internal sealed class LoadedWorkspace(MSBuildWorkspace workspace, string sdk) : IDisposable
{
    public MSBuildWorkspace Workspace { get; } = workspace;
    public string Sdk { get; } = sdk;
    public List<ProjectInfo> Projects { get; } = [];
    public SortedDictionary<string, string> Inputs { get; } = new(StringComparer.Ordinal);
    public List<string> Limits { get; } = [];
    public void Capture(string path)
    {
        path = Path.GetFullPath(path);
        Paths.RegularFile(path);
        var hash = Data.Hash(File.ReadAllBytes(path));
        if (Inputs.TryGetValue(path, out var previous))
            Data.Require(previous == hash, "input_drift", $"Input changed while loading: {path}");
        Inputs[path] = hash;
    }
    public void VerifyInputs()
    {
        foreach (var (path, hash) in Inputs)
        {
            Paths.RegularFile(path);
            Data.Require(Data.Hash(File.ReadAllBytes(path)) == hash, "input_drift", $"Input changed: {path}");
        }
    }
    public void Dispose() => Workspace.Dispose();
}

internal static class WorkspaceLoader
{
    public static async Task<LoadedWorkspace> Load(Request request)
    {
        var path = Path.GetFullPath(request.Workspace);
        Data.Require(OperatingSystem.IsWindows() && System.Runtime.InteropServices.RuntimeInformation.OSArchitecture == System.Runtime.InteropServices.Architecture.X64,
            "unsupported_host", "This release supports Windows x64. Other hosts require separate acceptance.");
        Paths.RegularFile(path);
        Data.Require(!string.IsNullOrWhiteSpace(request.Configuration) &&
            !request.Configuration.Any(c => c is ';' or ',' or '\r' or '\n' or '\0'), "invalid_configuration", "Specify one configuration.");
        var sdk = (await Run(Path.GetDirectoryName(path)!, "--version")).Trim();
        Data.Require(sdk.StartsWith("10.", StringComparison.Ordinal), "unsupported_sdk", "The first release requires .NET 10 SDK.", sdk);
        var properties = new Dictionary<string, string> { ["Configuration"] = request.Configuration };
        if (request.Framework is not null) properties["TargetFramework"] = request.Framework;
        var workspace = MSBuildWorkspace.Create(properties);
        workspace.SkipUnrecognizedProjects = false;
        workspace.LoadMetadataForReferencedProjects = false;
        var loaded = new LoadedWorkspace(workspace, sdk);
        try
        {
            loaded.Capture(path);
            var expected = new HashSet<string>(Paths.Comparer);
            var evaluatedFrameworks = new Dictionary<string, string>(Paths.Comparer);
            var evaluatedSources = new Dictionary<string, HashSet<string>>(Paths.Comparer);
            var pending = new Queue<string>(SolutionProjects(path));
            while (pending.TryDequeue(out var projectPath))
            {
                projectPath = Path.GetFullPath(projectPath);
                if (!expected.Add(projectPath)) continue;
                Data.Require(Path.GetExtension(projectPath) == ".csproj", "unsupported_project", $"Only C# projects are supported: {projectPath}");
                loaded.Capture(projectPath);
                var args = new List<string> { "msbuild", projectPath, "-nologo", $"-property:Configuration={request.Configuration}",
                    "-getProperty:UsingMicrosoftNETSdk,TargetFramework,TargetFrameworks,MSBuildAllProjects,ProjectAssetsFile",
                    "-getItem:ProjectReference,Compile,AdditionalFiles,EditorConfigFiles" };
                // Inspect the unselected framework list before supplying an override.
                using var evaluation = JsonDocument.Parse(await Run(Path.GetDirectoryName(projectPath)!, args.ToArray()));
                var props = evaluation.RootElement.GetProperty("Properties");
                string Property(string name) => props.GetProperty(name).GetString() ?? "";
                Data.Require(Property("UsingMicrosoftNETSdk").Equals("true", StringComparison.OrdinalIgnoreCase), "unsupported_project", $"SDK-style C# required: {projectPath}");
                var frameworks = Property("TargetFrameworks").Split(';', StringSplitOptions.RemoveEmptyEntries);
                Data.Require(frameworks.Length <= 1, "multiple_frameworks", $"Multiple target frameworks are not covered: {projectPath}", frameworks);
                var framework = frameworks.SingleOrDefault() ?? Property("TargetFramework");
                evaluatedFrameworks[projectPath] = framework;
                Data.Require(framework.Length > 0 && (request.Framework is null || request.Framework == framework), "framework_mismatch", $"Requested framework does not match {projectPath}: {framework}");
                foreach (var import in Property("MSBuildAllProjects").Split(';', StringSplitOptions.RemoveEmptyEntries))
                    loaded.Capture(import);
                var assets = Property("ProjectAssetsFile");
                Data.Require(File.Exists(assets), "restore_required", $"Restore the target explicitly before using this tool: {projectPath}");
                loaded.Capture(assets);
                var items = evaluation.RootElement.GetProperty("Items");
                var sourceFiles = new HashSet<string>(Paths.Comparer);
                evaluatedSources[projectPath] = sourceFiles;
                foreach (var reference in items.GetProperty("ProjectReference").EnumerateArray())
                    pending.Enqueue(reference.GetProperty("FullPath").GetString()!);
                foreach (var item in items.GetProperty("Compile").EnumerateArray())
                {
                    var file = item.GetProperty("FullPath").GetString()!;
                    Data.Require(!item.TryGetProperty("Link", out var link) || string.IsNullOrEmpty(link.GetString()), "linked_file", $"Linked source is unsupported: {file}");
                    Data.Require(Paths.IsWithin(file, Path.GetDirectoryName(projectPath)!), "linked_file", $"Source outside its project directory is unsupported: {file}");
                    loaded.Capture(file);
                    sourceFiles.Add(file);
                }
                CaptureAncestorConfiguration(loaded, Path.GetDirectoryName(projectPath)!);
            }
            if (Path.GetExtension(path) == ".csproj") await workspace.OpenProjectAsync(path);
            else await workspace.OpenSolutionAsync(path);
            var failures = workspace.Diagnostics.Where(d => d.Kind == WorkspaceDiagnosticKind.Failure).Select(d => d.Message).ToArray();
            Data.Require(failures.Length == 0, "workspace_load_failed", "Workspace did not load completely.", failures);
            loaded.Limits.AddRange(workspace.Diagnostics.Select(d => d.Message));
            var solution = workspace.CurrentSolution;
            Data.Require(expected.SetEquals(solution.Projects.Select(p => p.FilePath!)) && solution.ProjectIds.Count > 0,
                "incomplete_workspace", "Loaded project set differs from the explicit project/reference graph.");
            var seen = new HashSet<string>(Paths.Comparer);
            foreach (var project in solution.Projects.OrderBy(p => p.FilePath, StringComparer.Ordinal))
            {
                Data.Require(project.Language == LanguageNames.CSharp, "unsupported_project", "Non-C# project encountered.");
                foreach (var document in project.Documents)
                {
                    Data.Require(document.FilePath is not null && seen.Add(document.FilePath), "linked_file", "A source file belongs to more than one project or has no physical path.");
                    loaded.Capture(document.FilePath!);
                    var text = await document.GetTextAsync();
                    using var stream = File.OpenRead(document.FilePath!);
                    var disk = Microsoft.CodeAnalysis.Text.SourceText.From(stream, text.Encoding);
                    Data.Require(text.ContentEquals(disk), "input_drift", $"Workspace text differs from disk: {document.FilePath}");
                    var root = await document.GetSyntaxRootAsync();
                    if (root!.DescendantTrivia(descendIntoTrivia: true).Any(t => t.IsKind(SyntaxKind.DisabledTextTrivia)))
                        loaded.Limits.Add($"Inactive conditional code is not analyzed or renamed: {document.FilePath}");
                }
                foreach (var document in project.AdditionalDocuments.Concat(project.AnalyzerConfigDocuments))
                    if (document.FilePath is not null) loaded.Capture(document.FilePath);
                Data.Require(evaluatedSources[project.FilePath!].IsSubsetOf(project.Documents.Select(d => d.FilePath!)),
                    "incomplete_documents", $"Workspace omitted evaluated Compile items in {project.FilePath}.");
                foreach (var reference in project.MetadataReferences.OfType<PortableExecutableReference>())
                    if (reference.FilePath is not null) loaded.Capture(reference.FilePath);
                foreach (var analyzer in project.AnalyzerReferences)
                    if (analyzer.FullPath is not null) loaded.Capture(analyzer.FullPath);
                var generated = await project.GetSourceGeneratedDocumentsAsync();
                Data.Require(!generated.Any(), "source_generators", $"Source-generator output is not covered by this release: {project.FilePath}");
                var options = (CSharpParseOptions)project.ParseOptions!;
                var compilationOptions = (CSharpCompilationOptions)project.CompilationOptions!;
                loaded.Projects.Add(new(project.FilePath!, evaluatedFrameworks[project.FilePath!], request.Configuration,
                    compilationOptions.NullableContextOptions.ToString(), options.LanguageVersion.ToString(), options.PreprocessorSymbolNames.Order().ToArray(),
                    project.ProjectReferences.Select(r => solution.GetProject(r.ProjectId)!.FilePath!).Order().ToArray()));
            }
            loaded.VerifyInputs();
            return loaded;
        }
        catch { loaded.Dispose(); throw; }
    }

    private static void CaptureAncestorConfiguration(LoadedWorkspace loaded, string directory)
    {
        for (var current = new DirectoryInfo(directory); current is not null; current = current.Parent)
            foreach (var name in new[] { "global.json", "Directory.Build.props", "Directory.Build.targets", "Directory.Packages.props", "NuGet.Config", "nuget.config", ".editorconfig" })
            {
                var file = Path.Combine(current.FullName, name);
                if (File.Exists(file)) loaded.Capture(file);
            }
    }

    private static IEnumerable<string> SolutionProjects(string path)
    {
        var folder = Path.GetDirectoryName(path)!;
        if (Path.GetExtension(path) == ".csproj") return [path];
        if (Path.GetExtension(path) == ".slnx")
            return XDocument.Load(path).Descendants("Project").Select(e => Path.GetFullPath(e.Attribute("Path")!.Value, folder)).ToArray();
        Data.Require(Path.GetExtension(path) == ".sln", "unsupported_workspace", "Use an explicit .csproj, .sln or .slnx path.");
        return Regex.Matches(File.ReadAllText(path), "^Project\\(\"([^\"]+)\"\\)\\s*=\\s*\"[^\"]*\",\\s*\"([^\"]+)\"", RegexOptions.Multiline)
            .Where(m => !m.Groups[1].Value.Equals("{2150E333-8FDC-42A3-9474-1A3956D46DE8}", StringComparison.OrdinalIgnoreCase) &&
                !m.Groups[1].Value.Equals("{66A26720-8FB5-11D2-AA7E-00C04F688DDE}", StringComparison.OrdinalIgnoreCase))
            .Select(m => Path.GetFullPath(m.Groups[2].Value.Replace('\\', Path.DirectorySeparatorChar), folder)).ToArray();
    }

    internal static async Task<string> Run(string directory, params string[] arguments)
    {
        var start = new ProcessStartInfo("dotnet") { WorkingDirectory = directory, RedirectStandardOutput = true, RedirectStandardError = true, UseShellExecute = false, CreateNoWindow = true };
        foreach (var argument in arguments) start.ArgumentList.Add(argument);
        using var process = Process.Start(start) ?? throw new RefactorFailure("sdk_unavailable", "Unable to start dotnet.");
        var output = process.StandardOutput.ReadToEndAsync();
        var error = process.StandardError.ReadToEndAsync();
        using var timeout = new CancellationTokenSource(TimeSpan.FromMinutes(2));
        try { await process.WaitForExitAsync(timeout.Token); }
        catch (OperationCanceledException) { process.Kill(entireProcessTree: true); throw new RefactorFailure("sdk_timeout", "SDK command exceeded two minutes."); }
        Data.Require(process.ExitCode == 0, "sdk_failed", "SDK command failed.", new { arguments, exitCode = process.ExitCode, output = await output, error = await error });
        return await output;
    }
}

internal static class Paths
{
    public static StringComparer Comparer => OperatingSystem.IsWindows() ? StringComparer.OrdinalIgnoreCase : StringComparer.Ordinal;
    public static bool IsWithin(string path, string directory) => Path.GetRelativePath(directory, path) is var relative &&
        !Path.IsPathRooted(relative) && relative != ".." && !relative.StartsWith(".." + Path.DirectorySeparatorChar, StringComparison.Ordinal);
    public static void RegularFile(string path)
    {
        Data.Require(File.Exists(path), "missing_file", $"Required file is missing: {path}");
        for (FileSystemInfo? entry = new FileInfo(path); entry is not null; entry = entry is FileInfo file ? file.Directory : ((DirectoryInfo)entry).Parent)
            Data.Require((entry.Attributes & FileAttributes.ReparsePoint) == 0, "linked_path", $"Symbolic/reparse paths are unsupported: {entry.FullName}");
        Data.Require((File.GetAttributes(path) & FileAttributes.Directory) == 0, "not_regular_file", $"Expected a regular file: {path}");
    }
    public static void RegularDirectory(string path)
    {
        Data.Require(Directory.Exists(path), "missing_directory", $"Plan directory must already exist: {path}");
        for (var directory = new DirectoryInfo(path); directory is not null; directory = directory.Parent)
            Data.Require((directory.Attributes & FileAttributes.ReparsePoint) == 0, "linked_path", $"Symbolic/reparse paths are unsupported: {directory.FullName}");
    }
}
