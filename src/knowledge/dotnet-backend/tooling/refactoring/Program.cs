using System.Text;

namespace RefactorTool;

internal static class Program
{
    public static async Task<int> Main(string[] args)
    {
        var applyStarted = false;
        try
        {
            if (args is ["--version"])
            {
                Console.WriteLine("RefactorTool 0.1.0-dev.1 (Roslyn 5.0.0; managed .NET 10)");
                return 0;
            }
            if (args.Length == 0 || args is ["--help"])
            {
                Console.WriteLine("RefactorTool preview --request request.json --plan NEW-plan.json\nRefactorTool apply --plan plan.json\nRefactorTool inspect --request request.json\nAll paths in requests are explicit; file positions are 1-based UTF-16. Restore trusted target projects before use. See README.md.");
                return 0;
            }
            var options = new Dictionary<string, string>(StringComparer.Ordinal);
            for (var i = 1; i < args.Length; i += 2)
            {
                Data.Require(i + 1 < args.Length && args[i].StartsWith("--", StringComparison.Ordinal) && options.TryAdd(args[i], args[i + 1]), "invalid_arguments", "Expected unique --option value pairs.");
            }
            if (args[0] == "inspect")
            {
                Data.Require(options.Count == 1 && options.ContainsKey("--request"), "invalid_arguments", "inspect requires --request.");
                using var loaded = await WorkspaceLoader.Load(Data.Read<Request>(options["--request"]));
                Console.WriteLine(Data.Serialize(new { status = "loaded", sdk = loaded.Sdk, roslyn = typeof(Microsoft.CodeAnalysis.Compilation).Assembly.GetName().Version!.ToString(), projects = loaded.Projects, limits = loaded.Limits }));
                return 0;
            }
            if (args[0] == "preview")
            {
                Data.Require(options.Count == 2 && options.ContainsKey("--request") && options.ContainsKey("--plan"), "invalid_arguments", "preview requires --request and --plan.");
                var destination = Path.GetFullPath(options["--plan"]);
                Data.Require(Path.GetExtension(destination).Equals(".json", StringComparison.OrdinalIgnoreCase) &&
                    !Path.GetFileName(destination).Equals("global.json", StringComparison.OrdinalIgnoreCase),
                    "unsafe_plan_path", "Use a JSON plan filename that is not global.json, outside all loaded project directories.");
                Paths.RegularDirectory(Path.GetDirectoryName(destination)!);
                Data.Require(!File.Exists(destination), "plan_exists", "Choose a new plan path; existing files are never overwritten.");
                var plan = await RenamePlanner.Preview(Data.Read<Request>(options["--request"]));
                Data.Require(!plan.Inputs.Any(i => Paths.Comparer.Equals(i.Path, destination)) &&
                    !plan.Projects.Any(p => Paths.IsWithin(destination, Path.GetDirectoryName(p.Path)!)),
                    "unsafe_plan_path", "Store the plan outside all loaded project directories and existing inputs.");
                using (var stream = new FileStream(destination, FileMode.CreateNew, FileAccess.Write, FileShare.None))
                {
                    var bytes = Encoding.UTF8.GetBytes(Data.Serialize(plan));
                    stream.Write(bytes); stream.Flush(true);
                }
                Console.WriteLine(Data.Serialize(new { status = "previewed", plan = destination, symbol = plan.Symbol, relatedSymbols = plan.RelatedSymbols,
                    files = plan.Edits.Select(e => new { e.Path, e.Kind }), baselineErrors = plan.BaselineErrors, newErrors = plan.NewErrors,
                    patch = "Complete unified patch is in the plan's patch field; before/after base64 preserve exact bytes.", limits = plan.Limits }));
                return 0;
            }
            Data.Require(args[0] == "apply" && options.Count == 1 && options.ContainsKey("--plan"), "invalid_arguments", "apply requires --plan.");
            var selectedPlan = Data.Read<Plan>(options["--plan"]);
            applyStarted = true;
            return await Apply(selectedPlan);
        }
        catch (RefactorFailure error)
        {
            Console.WriteLine(Data.Serialize(new { status = "refused", code = error.Code, message = error.Message, detail = error.Detail, sourceWrites = false }));
            return 2;
        }
        catch (Exception error)
        {
            Console.WriteLine(Data.Serialize(new { status = "failed", code = error.GetType().Name, message = error.Message,
                sourceWrites = applyStarted ? "unknown" : "none", recovery = applyStarted ? FileApply.Recovery : null }));
            return 2;
        }
    }

    internal static async Task<int> Apply(Plan plan)
    {
        Data.Require(plan.Contract == "refactor-plan/1", "unsupported_plan", "Unsupported plan version.");
        foreach (var input in plan.Inputs)
        {
            Paths.RegularFile(input.Path);
            Data.Require(Data.Hash(File.ReadAllBytes(input.Path)) == input.Hash, "input_drift", $"Preview input changed: {input.Path}");
        }
        // Recompute with the public semantic operation: a changed or forged plan
        // cannot introduce arbitrary filesystem edits, omit inputs or skip checks.
        var actual = await RenamePlanner.Preview(plan.Request);
        Data.Require(Data.Serialize(actual) == Data.Serialize(plan), "plan_drift", "Workspace or plan changed; create and review a new preview.");
        var handles = new List<(FileEdit Edit, Stream Stream)>();
        var writesBegun = false;
        try
        {
            foreach (var edit in plan.Edits)
            {
                Paths.RegularFile(edit.Path);
                Data.Require(edit.Kind == "modify" && (File.GetAttributes(edit.Path) & FileAttributes.ReadOnly) == 0, "unwritable_source", $"Cannot modify: {edit.Path}");
                var stream = new FileStream(edit.Path, FileMode.Open, FileAccess.ReadWrite, FileShare.None);
                handles.Add((edit, stream));
                using var content = new MemoryStream();
                stream.CopyTo(content);
                Data.Require(content.ToArray().SequenceEqual(Convert.FromBase64String(edit.Before)), "input_drift", $"File changed before apply: {edit.Path}");
            }
            var edited = new HashSet<string>(plan.Edits.Select(e => e.Path), Paths.Comparer);
            foreach (var input in plan.Inputs.Where(i => !edited.Contains(i.Path)))
            {
                Paths.RegularFile(input.Path);
                Data.Require(Data.Hash(File.ReadAllBytes(input.Path)) == input.Hash, "input_drift", $"Input changed before writes: {input.Path}");
            }
            writesBegun = true;
            var result = FileApply.Write(handles);
            Console.WriteLine(Data.Serialize(result));
            return result.Status == "applied" ? 0 : 3;
        }
        catch (Exception error) when (!writesBegun && error is not RefactorFailure)
        {
            throw new RefactorFailure("apply_preflight_failed", "No source writes began: " + error.Message);
        }
        finally { foreach (var (_, stream) in handles) stream.Dispose(); }
    }
}
