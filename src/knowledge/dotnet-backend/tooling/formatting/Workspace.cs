using System.Text.Json;
using System.Text.RegularExpressions;
using System.Xml.Linq;

namespace FormatTool;

internal static partial class Workspace
{
    internal static readonly StringComparer Paths = OperatingSystem.IsWindows() ? StringComparer.OrdinalIgnoreCase : StringComparer.Ordinal;

    public static string FullPath(string path, string root) => Path.GetFullPath(path.Replace(Path.AltDirectorySeparatorChar, Path.DirectorySeparatorChar), root);

    public static string[] Projects(string workspace)
    {
        var root = Path.GetDirectoryName(workspace)!;
        if (Path.GetExtension(workspace).Equals(".csproj", StringComparison.OrdinalIgnoreCase)) return [workspace];
        IEnumerable<string> projects = Path.GetExtension(workspace).ToLowerInvariant() switch
        {
            ".slnx" => XDocument.Load(workspace).Descendants("Project").Select(node => (string?)node.Attribute("Path") ?? ""),
            ".sln" => SolutionProject().Matches(File.ReadAllText(workspace))
                .Where(match => !match.Groups[1].Value.Equals("{66A26720-8FB5-11D2-AA7E-00C04F688DDE}", StringComparison.OrdinalIgnoreCase))
                .Select(match => match.Groups[2].Value),
            _ => throw new ToolFailure("unsupported-workspace", "Select an explicit .csproj, .sln, or .slnx file.")
        };
        var paths = projects.Select(path => FullPath(path.Replace('\\', Path.DirectorySeparatorChar), root)).Distinct(Paths).ToArray();
        if (paths.Length == 0 || paths.Any(path => !Path.GetExtension(path).Equals(".csproj", StringComparison.OrdinalIgnoreCase) || !File.Exists(path)))
            throw new ToolFailure("unsupported-workspace", "The solution must contain existing C# projects only.");
        return paths;
    }

    public static async Task<WorkspaceData> Load(Sdk sdk, string[] projects, bool cleanup)
    {
        var files = new Dictionary<string, string>(Paths);
        var observedFiles = new HashSet<string>(Paths);
        var externalAnalyzers = new HashSet<string>(Paths);
        foreach (var project in projects)
        {
            if (!Path.GetExtension(project).Equals(".csproj", StringComparison.OrdinalIgnoreCase) || !File.Exists(project))
                throw new ToolFailure("unsupported-project", "Select existing C# projects.");
            var command = await LoadDesignTime(sdk, project);
            using var metadata = JsonDocument.Parse(command.StandardOutput);
            var properties = metadata.RootElement.GetProperty("Properties");
            if (properties.GetProperty("UsingMicrosoftNETSdk").GetString() != "true" ||
                !string.IsNullOrEmpty(properties.GetProperty("TargetFrameworks").GetString()) ||
                string.IsNullOrEmpty(properties.GetProperty("TargetFramework").GetString()))
                throw new ToolFailure("unsupported-project", "This version requires single-target SDK-style C# projects.");
            var assets = properties.GetProperty("ProjectAssetsFile").GetString();
            if (string.IsNullOrEmpty(assets) || !File.Exists(assets))
                throw new ToolFailure("restore-required", "Assets are missing. Restore explicitly or select allowRestore.");
            foreach (var item in metadata.RootElement.GetProperty("Items").GetProperty("Compile").EnumerateArray())
            {
                var path = FullPath(item.GetProperty("FullPath").GetString()!, Path.GetDirectoryName(project)!);
                files.TryAdd(path, path);
                observedFiles.Add(path);
            }
            if (!cleanup) continue;
            RejectProjectReferences(metadata.RootElement);
            CollectAnalyzers(metadata.RootElement, externalAnalyzers);
            // Actual compilation and design-time loading can select different Analyzer items.
            // Query both without running the compiler before permitting either execution.
            var buildMetadata = await sdk.Require("load-failed", "msbuild", project, "-nologo",
                "-target:Compile", "-property:SkipCompilerExecution=true", "-property:BuildProjectReferences=false",
                "-property:RunAnalyzers=false", "-property:UseSharedCompilation=false",
                "-getItem:Analyzer,ProjectReference", "-getProperty:MSBuildToolsPath");
            using var buildDocument = JsonDocument.Parse(buildMetadata.StandardOutput);
            RejectProjectReferences(buildDocument.RootElement);
            CollectAnalyzers(buildDocument.RootElement, externalAnalyzers);
        }
        return new(files, observedFiles.ToArray(), externalAnalyzers.Order(Paths).ToArray());
    }

    private static async Task<CommandResult> LoadDesignTime(Sdk sdk, string project)
    {
        // Match SDK 10.0.403 dotnet-format's MSBuildWorkspaceLoader and netcore
        // ProjectBuildManager, including optional post-Compile targets. Conditional
        // Analyzer/ProjectReference items must be inspected in that same context.
        string[] arguments = ["msbuild", project, "-nologo",
            "-property:AlwaysCompileMarkupFilesInSeparateDomain=False",
            "-property:DesignTimeBuild=True", "-property:NonExistentFile=__NonExistentSubDir__\\__NonExistentFile__",
            "-property:BuildProjectReferences=False", "-property:BuildingProject=False",
            "-property:ProvideCommandLineArgs=True", "-property:SkipCompilerExecution=True",
            "-property:ContinueOnError=ErrorAndContinue", "-property:ShouldUnsetParentConfigurationAndPlatform=False"];
        var available = await sdk.Require("load-failed", [.. arguments, "-targets"]);
        var hasMarkup = available.StandardOutput.Split(['\r', '\n'], StringSplitOptions.RemoveEmptyEntries)
            .Any(target => target.Trim().Equals("DesignTimeMarkupCompilation", StringComparison.OrdinalIgnoreCase));
        var targets = hasMarkup ? "Compile;CoreCompile;DesignTimeMarkupCompilation" : "Compile;CoreCompile";
        return await sdk.Require("load-failed", [.. arguments, "-target:" + targets,
            "-getItem:Compile,Analyzer,ProjectReference",
            "-getProperty:UsingMicrosoftNETSdk,TargetFramework,TargetFrameworks,ProjectAssetsFile,MSBuildToolsPath"]);
    }

    private static void RejectProjectReferences(JsonElement metadata)
    {
        if (metadata.GetProperty("Items").GetProperty("ProjectReference").GetArrayLength() > 0)
            throw new ToolFailure("unsupported-cleanup-workspace", "Cleanup does not yet support ProjectReference graphs or their configuration/property mappings. No compiler or formatter was run.");
    }

    private static void CollectAnalyzers(JsonElement metadata, HashSet<string> external)
    {
        var sdk = metadata.GetProperty("Properties").GetProperty("MSBuildToolsPath").GetString()!;
        var sdkRoot = Path.GetFullPath(sdk) + Path.DirectorySeparatorChar;
        var packsRoot = Path.GetFullPath(Path.Combine(sdk, "..", "..", "packs")) + Path.DirectorySeparatorChar;
        var comparison = OperatingSystem.IsWindows() ? StringComparison.OrdinalIgnoreCase : StringComparison.Ordinal;
        foreach (var analyzer in metadata.GetProperty("Items").GetProperty("Analyzer").EnumerateArray())
        {
            var path = Path.GetFullPath(analyzer.GetProperty("FullPath").GetString()!);
            if (!File.Exists(path)) throw new ToolFailure("analyzer-unavailable", $"Analyzer file cannot be loaded: {path}");
            if (!path.StartsWith(sdkRoot, comparison) && !path.StartsWith(packsRoot, comparison)) external.Add(path);
        }
    }

    public static string[] Configurations(IEnumerable<string> files)
    {
        var found = new HashSet<string>(Paths);
        foreach (var file in files)
        {
            for (var directory = new DirectoryInfo(Path.GetDirectoryName(file)!); directory != null; directory = directory.Parent)
            {
                var path = Path.Combine(directory.FullName, ".editorconfig");
                if (File.Exists(path)) found.Add(path);
            }
        }
        return found.Order(Paths).ToArray();
    }

    [GeneratedRegex("^Project\\(\"([^\"]+)\"\\)\\s*=\\s*\"[^\"]*\",\\s*\"([^\"]+)\"", RegexOptions.Multiline)]
    private static partial Regex SolutionProject();
}

internal sealed record WorkspaceData(Dictionary<string, string> CompileFiles, string[] ObservedFiles, string[] ProjectAnalyzers);
