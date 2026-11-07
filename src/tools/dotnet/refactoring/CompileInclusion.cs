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
        var sdkPath = await SelectedSdkPath(directory);
        if (!MSBuildLocator.IsRegistered) MSBuildLocator.RegisterMSBuildPath(sdkPath);
        registeredSdkPath = sdkPath;
    }

    private static async Task<string> SelectedSdkPath(string directory)
    {
        // --list-sdks is an inventory, not selection: sdk.paths may list the
        // same version from multiple roots. --info identifies the selected SDK.
        var info = await WorkspaceLoader.Run(directory, "--info");
        var matches = Regex.Matches(info, @"(?m)^\s*Base Path:\s*([^\r\n]+)\r?$");
        Data.Require(matches.Count == 1, "sdk_unavailable", "Cannot read the CLI-selected SDK base path.");
        var path = Path.GetFullPath(matches[0].Groups[1].Value.Trim()).TrimEnd(Path.DirectorySeparatorChar, Path.AltDirectorySeparatorChar);
        Data.Require(File.Exists(Path.Combine(path, "Microsoft.Build.dll")), "sdk_unavailable", "The CLI-selected SDK does not contain MSBuild.");
        return path;
    }

    public static async Task Require(LoadedWorkspace loaded, string projectPath, string output, Request request)
    {
        Data.Require(registeredSdkPath is not null && Path.GetFileName(registeredSdkPath) == loaded.Sdk,
            "sdk_mismatch", "Compile inclusion must use the workspace-selected SDK.");
        foreach (var project in loaded.Projects)
            Data.Require(Paths.Comparer.Equals(await SelectedSdkPath(Path.GetDirectoryName(project.Path)!), registeredSdkPath),
                "sdk_mismatch", "Extract Interface requires the same selected SDK directory in every loaded project.");
        Evaluate(loaded, projectPath, output, request, registeredSdkPath!);
    }

    // Keep MSBuild types behind the Locator registration boundary.
    [MethodImpl(MethodImplOptions.NoInlining)]
    private static void Evaluate(LoadedWorkspace loaded, string selected, string output, Request request, string sdkPath)
    {
        using var collection = new Microsoft.Build.Evaluation.ProjectCollection();
        loaded.Capture(Path.Combine(sdkPath, "Microsoft.Build.dll"));
        using var sdkFile = File.OpenRead(Path.Combine(sdkPath, "Microsoft.Build.dll"));
        var physicalSdk = Path.GetDirectoryName(Paths.CanonicalFile(sdkFile))!;
        var physicalHost = Path.GetDirectoryName(Path.GetDirectoryName(physicalSdk))!;
        bool SdkResource(string path)
        {
            using var stream = File.OpenRead(path);
            var physical = Paths.CanonicalFile(stream);
            return Paths.IsWithin(physical, physicalSdk) ||
                Paths.IsWithin(physical, Path.Combine(physicalHost, "sdk-manifests")) ||
                Paths.IsWithin(physical, Path.Combine(physicalHost, "packs"));
        }
        foreach (var info in loaded.Projects)
        {
            var properties = new Dictionary<string, string> { ["Configuration"] = request.Configuration };
            if (request.Framework is not null) properties["TargetFramework"] = request.Framework;
            var project = collection.LoadProject(info.Path, properties, null);
            foreach (var import in project.Imports) loaded.Capture(import.ImportedProject.FullPath);
            var extensions = Path.GetFullPath(project.GetPropertyValue("MSBuildProjectExtensionsPath"), project.DirectoryPath);
            var generatedProps = Path.Combine(extensions, Path.GetFileName(info.Path) + ".nuget.g.props");
            var generatedTargets = Path.Combine(extensions, Path.GetFileName(info.Path) + ".nuget.g.targets");
            var roots = project.Imports.Select(i => i.ImportedProject).Prepend(project.Xml)
                .DistinctBy(r => r.FullPath, Paths.Comparer).ToArray();
            var sdkRoots = roots.Where(r => SdkResource(r.FullPath)).ToArray();
            var sdkImports = sdkRoots.SelectMany(r => r.AllChildren).OfType<Microsoft.Build.Construction.ProjectImportElement>().ToArray();
            // SDK extension hooks can import a file only after it appears. Find
            // hook properties, including indirect filename/search properties,
            // from the selected SDK's actual XML rather than a hard-coded list.
            var importProperties = sdkImports.Where(i => !ImportSuffix(i.Project))
                .SelectMany(i => PropertyNames(i.Project)).ToHashSet(StringComparer.OrdinalIgnoreCase);
            var propertiesInRoots = roots.SelectMany(r => r.AllChildren).OfType<Microsoft.Build.Construction.ProjectPropertyElement>().ToArray();
            var expanded = true;
            while (expanded)
            {
                expanded = false;
                foreach (var property in propertiesInRoots.Where(p => importProperties.Contains(p.Name) && !ImportSuffix(p.Value)))
                    foreach (var name in PropertyNames(property.Value)) expanded |= importProperties.Add(name);
            }
            foreach (var import in sdkImports)
            {
                var specification = project.ExpandString(import.Project.Replace("$(MSBuildThisFileDirectory)",
                    Path.GetDirectoryName(import.ContainingProject.FullPath)! + Path.DirectorySeparatorChar, StringComparison.OrdinalIgnoreCase));
                foreach (var pattern in specification.Split(';', StringSplitOptions.RemoveEmptyEntries | StringSplitOptions.TrimEntries))
                    Data.Require(!Microsoft.Build.Globbing.MSBuildGlob.Parse(project.DirectoryPath, pattern).IsMatch(output),
                        "unsupported_compile_inclusion", "An SDK import hook or pattern can include the proposed C# output as an MSBuild project.");
            }
            // File-dependent custom evaluation or build-time Compile mutations
            // cannot be proven by an absent-path glob query. Reject them rather
            // than promise that an in-memory Roslyn document will be built.
            // Inspect raw roots as well as resolved imports. The logical
            // project omits inactive Import nodes, which can activate later.
            foreach (var element in roots.Where(r => !SdkResource(r.FullPath)).SelectMany(r => r.AllChildren))
            {
                // SDK-generated NuGet import guards check whether package props
                // exist; custom file-dependent conditions can instead change
                // evaluation when the proposed source file appears.
                var origin = element.ContainingProject.FullPath;
                var nugetImport = element is Microsoft.Build.Construction.ProjectImportElement packageImport &&
                    (Paths.Comparer.Equals(origin, generatedProps) || Paths.Comparer.Equals(origin, generatedTargets)) &&
                    (packageImport.Project.EndsWith(".props", StringComparison.OrdinalIgnoreCase) || packageImport.Project.EndsWith(".targets", StringComparison.OrdinalIgnoreCase)) &&
                    Stable(packageImport.Project) && string.Equals(packageImport.Condition, $"Exists('{packageImport.Project}')", StringComparison.OrdinalIgnoreCase);
                Data.Require(nugetImport || (Stable(element.Condition) &&
                    (element is not Microsoft.Build.Construction.ProjectPropertyElement property || Stable(property.Value))),
                    "unsupported_compile_inclusion", $"Custom file/item-dependent evaluation cannot prove absent-file compile inclusion: {origin}");
                if (element is Microsoft.Build.Construction.ProjectImportElement customImport)
                    Data.Require(nugetImport || (customImport.Project.Split(';').All(ImportSuffix) &&
                        customImport.Project.IndexOfAny(['*', '?']) < 0 && !customImport.Project.Contains("$(", StringComparison.Ordinal) && Stable(customImport.Project)),
                        "unsupported_compile_inclusion", $"Custom imports require literal non-wildcard .props/.targets paths: {origin}");
                if (element is Microsoft.Build.Construction.ProjectPropertyElement customProperty)
                    Data.Require(!importProperties.Contains(customProperty.Name), "unsupported_compile_inclusion",
                        $"Custom override of an SDK import hook is outside the supported subset: {customProperty.Name} in {origin}");
                Data.Require(nugetImport || element is not Microsoft.Build.Construction.ProjectTargetElement,
                    "unsupported_compile_inclusion", $"Custom build targets are outside Extract Interface's compile-inclusion subset: {origin}");
                if (element is Microsoft.Build.Construction.ProjectItemElement item && item.ItemType.Equals("Compile", StringComparison.OrdinalIgnoreCase))
                {
                    Data.Require(string.IsNullOrEmpty(item.Condition) && item.AllParents.All(p => string.IsNullOrEmpty(p.Condition)) &&
                        new[] { item.Include, item.Exclude, item.Remove, item.Update }.Select(s => s ?? "").All(s => !s.Contains("$(", StringComparison.Ordinal) &&
                            !s.Contains("@(", StringComparison.Ordinal) && !s.Contains("%(", StringComparison.Ordinal)),
                        "unsupported_compile_inclusion", $"Custom Compile rules must be unconditional literal patterns without item/property/metadata expressions: {origin}");
                }
            }
            var relative = Path.GetRelativePath(project.DirectoryPath, output);
            var matching = project.GetAllGlobs().Count(g => g.ItemElement.ItemType.Equals("Compile", StringComparison.OrdinalIgnoreCase) && g.MsBuildGlob.IsMatch(relative));
            Data.Require(Paths.Comparer.Equals(info.Path, selected) ? matching == 1 : matching == 0,
                "unsupported_compile_inclusion", $"New file must match exactly one evaluated Compile glob in its project and none in other loaded projects: {output}");
        }
    }

    private static bool ImportSuffix(string value) => value.EndsWith(".props", StringComparison.OrdinalIgnoreCase) || value.EndsWith(".targets", StringComparison.OrdinalIgnoreCase);
    private static IEnumerable<string> PropertyNames(string value) => Regex.Matches(value, @"\$\(([A-Za-z_][A-Za-z0-9_.-]*)\)")
        .Select(m => m.Groups[1].Value);

    private static bool Stable(string? value) => string.IsNullOrEmpty(value) || (!value.Contains("Exists", StringComparison.OrdinalIgnoreCase) &&
        !value.Contains("@(", StringComparison.Ordinal) && !value.Contains("%(", StringComparison.Ordinal) &&
        !value.Contains("$([", StringComparison.Ordinal));
}
