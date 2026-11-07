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
                var request = RequireRequest(Data.Read<Request>(options["--request"]), preview: false);
                await CompileInclusion.Register(request);
                using var loaded = await WorkspaceLoader.Load(request);
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
                var plan = await Preview(RequireRequest(Data.Read<Request>(options["--request"]), preview: true));
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
                    patch = "Unified patch is in the plan's patch field; before/after base64 preserve exact bytes.", limits = plan.Limits }));
                return 0;
            }
            Data.Require(args[0] == "apply" && options.Count == 1 && options.ContainsKey("--plan"), "invalid_arguments", "apply requires --plan.");
            var selectedPlan = Data.Read<Plan>(options["--plan"], strictPath: true);
            WorkspaceLoader.RequireSupportedHost();
            RequireRequest(selectedPlan.Request, preview: true);
            Data.Require(selectedPlan.Inputs.All(input => input is not null) && selectedPlan.Edits.All(edit => edit is not null),
                "invalid_input", "Plan inputs and edits must be objects.");
            var locks = await PrepareApply(selectedPlan);
            applyStarted = true;
            return Apply(locks);
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

    private static Request RequireRequest(Request request, bool preview)
    {
        Data.Require(!string.IsNullOrWhiteSpace(request.Workspace), "invalid_input", "workspace is required.");
        if (preview)
        {
            Data.Require(request.Operation is "rename" or "extract-interface", "unsupported_operation", "Use rename or extract-interface.");
            Data.Require(!string.IsNullOrWhiteSpace(request.NewName), "invalid_input", "newName is required.");
            Data.Require(request.File is not null || request.Symbol is not null, "invalid_input", "A file or symbol selector is required.");
            if (request.Operation == "extract-interface")
                Data.Require(request.Namespace is not null && !string.IsNullOrWhiteSpace(request.OutputFile) && request.Members.Length > 0 &&
                    request.Members.All(m => !string.IsNullOrWhiteSpace(m)) && !request.RenameOverloads,
                    "invalid_input", "Extract Interface requires namespace (empty for global), outputFile and exact member declaration IDs; renameOverloads is not applicable.");
            else
                Data.Require(request.Namespace is null && request.OutputFile is null && request.Members.Length == 0,
                    "invalid_input", "Interface options require operation extract-interface.");
        }
        return request;
    }

    private static async Task<Plan> Preview(Request request)
    {
        await CompileInclusion.Register(request);
        if (request.Operation != "extract-interface") return await RenamePlanner.Preview(request);
        return await InterfacePlanner.Preview(request);
    }

    private static async Task<InputLocks> PrepareApply(Plan plan)
    {
        try
        {
            Data.Require(plan.Contract == "refactor-plan/1", "unsupported_plan", "Unsupported plan version.");
            foreach (var input in plan.Inputs)
            {
                using var stream = InputLocks.OpenInput(input);
                Data.Require(Data.Hash(stream) == input.Hash, "input_drift", $"Preview input changed: {input.Path}");
            }
            // Recompute with the public semantic operation: a changed or forged plan
            // cannot introduce arbitrary filesystem edits, omit inputs or skip checks.
            var actual = await Preview(plan.Request);
            Data.Require(Data.Serialize(actual) == Data.Serialize(plan), "plan_drift", "Workspace or plan changed; create and review a new preview.");
            return InputLocks.Open(plan);
        }
        catch (Exception error) when (error is IOException or UnauthorizedAccessException)
        {
            throw new RefactorFailure("apply_preflight_failed", "No source writes began: " + error.Message);
        }
    }

    private static int Apply(InputLocks locks)
    {
        ApplyResult? result = null;
        try
        {
            result = FileApply.Write(locks.Writes, locks.Creates, locks.All);
        }
        finally
        {
            var closeFailures = FileApply.Close(locks.All);
            if (result is not null) result = FileApply.AfterClose(result, closeFailures);
        }
        // Closing/flushing is part of the operation, not cleanup after its
        // response. Emit exactly one result only after every close was attempted.
        Console.WriteLine(Data.Serialize(result));
        return result!.Status == "applied" ? 0 : 3;
    }
}
