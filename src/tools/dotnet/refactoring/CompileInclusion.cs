using System.Runtime.CompilerServices;
using System.Text.RegularExpressions;
using Microsoft.Build.Locator;

namespace RefactorTool;

internal static class CompileInclusion
{
    private static string? registeredSdkPath;

    public static async Task Register(Request request)
    {
        if (registeredSdkPath is not null) return;
        WorkspaceLoader.RequireSupportedHost();
        Data.Require(File.Exists(request.Workspace), "missing_file", $"Required file is missing: {request.Workspace}");
        var directory = Path.GetDirectoryName(Path.GetFullPath(request.Workspace))!;
        var sdk = (await WorkspaceLoader.Run(directory, "--version")).Trim();
        var sdks = await WorkspaceLoader.Run(directory, "--list-sdks");
        var matches = Regex.Matches(sdks, @"(?m)^([^\s]+) \[([^\r\n]+)\]\r?$")
            .Where(m => m.Groups[1].Value == sdk).ToArray();
        Data.Require(matches.Length == 1, "sdk_unavailable", "Cannot locate the exact target-selected SDK for compile inclusion.");
        var sdkPath = Path.Combine(matches[0].Groups[2].Value, sdk);
        if (!MSBuildLocator.IsRegistered) MSBuildLocator.RegisterMSBuildPath(sdkPath);
        registeredSdkPath = sdkPath;
    }

    public static async Task Require(LoadedWorkspace loaded, string projectPath, string output, Request request)
    {
        Data.Require(registeredSdkPath is not null && Path.GetFileName(registeredSdkPath) == loaded.Sdk,
            "sdk_mismatch", "Compile inclusion must use the workspace-selected SDK.");
        foreach (var project in loaded.Projects)
            Data.Require((await WorkspaceLoader.Run(Path.GetDirectoryName(project.Path)!, "--version")).Trim() == loaded.Sdk,
                "sdk_mismatch", "Extract Interface requires the same selected SDK in every loaded project directory.");
        Evaluate(loaded, projectPath, output, request, registeredSdkPath!);
    }

    // Keep MSBuild types behind the Locator registration boundary.
    [MethodImpl(MethodImplOptions.NoInlining)]
    private static void Evaluate(LoadedWorkspace loaded, string selected, string output, Request request, string sdkPath)
    {
        using var collection = new Microsoft.Build.Evaluation.ProjectCollection();
        loaded.Capture(Path.Combine(sdkPath, "Microsoft.Build.dll"));
        foreach (var info in loaded.Projects)
        {
            var properties = new Dictionary<string, string> { ["Configuration"] = request.Configuration };
            if (request.Framework is not null) properties["TargetFramework"] = request.Framework;
            var project = collection.LoadProject(info.Path, properties, null);
            foreach (var import in project.Imports) loaded.Capture(import.ImportedProject.FullPath);
            var logical = project.GetLogicalProject().ToArray();
            // File-dependent custom evaluation or build-time Compile mutations
            // cannot be proven by an absent-path glob query. Reject them rather
            // than promise that an in-memory Roslyn document will be built.
            foreach (var element in logical.Where(e => !Paths.IsWithin(e.ContainingProject.FullPath, sdkPath)))
            {
                // SDK-generated NuGet import guards check whether package props
                // exist; custom file-dependent conditions can instead change
                // evaluation when the proposed source file appears.
                var origin = element.ContainingProject.FullPath;
                var nugetImport = origin.EndsWith(".nuget.g.props", StringComparison.OrdinalIgnoreCase) || origin.EndsWith(".nuget.g.targets", StringComparison.OrdinalIgnoreCase);
                Data.Require(nugetImport || (!element.Condition.Contains("Exists", StringComparison.OrdinalIgnoreCase) &&
                    (element is not Microsoft.Build.Construction.ProjectPropertyElement property || !property.Value.Contains("Exists", StringComparison.OrdinalIgnoreCase))),
                    "unsupported_compile_inclusion", "Custom file-dependent evaluation cannot prove absent-file compile inclusion.");
                if (element is Microsoft.Build.Construction.ProjectItemElement { ItemType: "Compile" } item)
                {
                    Data.Require(item.Parent?.Parent is not Microsoft.Build.Construction.ProjectTargetElement &&
                        !item.Condition.Contains("Exists", StringComparison.OrdinalIgnoreCase) &&
                        !(item.Parent?.Condition.Contains("Exists", StringComparison.OrdinalIgnoreCase) ?? false),
                        "unsupported_compile_inclusion", "Custom file-dependent or build-time Compile rules require a separate implementation.");
                }
            }
            var relative = Path.GetRelativePath(project.DirectoryPath, output);
            var matching = project.GetAllGlobs().Count(g => g.ItemElement.ItemType == "Compile" && g.MsBuildGlob.IsMatch(relative));
            Data.Require(Paths.Comparer.Equals(info.Path, selected) ? matching == 1 : matching == 0,
                "unsupported_compile_inclusion", $"New file must match exactly one evaluated Compile glob in its project and none in other loaded projects: {output}");
        }
    }
}
