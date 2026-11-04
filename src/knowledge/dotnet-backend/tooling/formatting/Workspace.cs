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
        if (Path.GetExtension(workspace) == ".csproj") return [workspace];
        IEnumerable<string> projects = Path.GetExtension(workspace) switch
        {
            ".slnx" => XDocument.Load(workspace).Descendants("Project").Select(node => (string?)node.Attribute("Path") ?? ""),
            ".sln" => SolutionProject().Matches(File.ReadAllText(workspace)).Select(match => match.Groups[1].Value)
                .Where(path => !string.IsNullOrEmpty(Path.GetExtension(path))),
            _ => throw new ToolFailure("unsupported-workspace", "Select an explicit .csproj, .sln, or .slnx file.")
        };
        var paths = projects.Select(path => FullPath(path.Replace('\\', Path.DirectorySeparatorChar), root)).Distinct(Paths).ToArray();
        if (paths.Length == 0 || paths.Any(path => Path.GetExtension(path) != ".csproj" || !File.Exists(path)))
            throw new ToolFailure("unsupported-workspace", "The solution must contain existing C# projects only.");
        return paths;
    }

    public static async Task<Dictionary<string, string>> CompileFiles(Sdk sdk, string[] projects)
    {
        var files = new Dictionary<string, string>(Paths);
        foreach (var project in projects)
        {
            var command = await sdk.Require("load-failed", "msbuild", project, "-nologo",
                "-target:Compile", "-property:DesignTimeBuild=true", "-property:SkipCompilerExecution=true",
                "-property:ProvideCommandLineArgs=true", "-property:BuildProjectReferences=false",
                "-getItem:Compile", "-getProperty:UsingMicrosoftNETSdk,TargetFramework,TargetFrameworks,ProjectAssetsFile");
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
            }
        }
        return files;
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

    [GeneratedRegex("^Project\\(\"[^\"]+\"\\)\\s*=\\s*\"[^\"]*\",\\s*\"([^\"]+)\"", RegexOptions.Multiline)]
    private static partial Regex SolutionProject();
}
