namespace RefactorTool;

internal sealed class InputLocks
{
    public List<(string Path, Stream Stream)> All { get; } = [];
    public List<(FileEdit Edit, Stream Stream)> Writes { get; } = [];
    public List<FileEdit> Creates { get; } = [];

    public static InputLocks Open(Plan plan)
    {
        var locks = new InputLocks();
        try
        {
            var edits = plan.Edits.ToDictionary(e => e.Path, Paths.Comparer);
            foreach (var input in plan.Inputs)
            {
                var writing = edits.TryGetValue(input.Path, out var edit);
                if (writing)
                    Data.Require(input.CanonicalPath is null && edit!.Kind == "modify" && (File.GetAttributes(input.Path) & FileAttributes.ReadOnly) == 0,
                        "unwritable_source", $"Cannot modify: {input.Path}");
                // Unchanged inputs stay locked against ordinary write/delete
                // access as well; a transient hash check would leave a race.
                var stream = OpenInput(input, writing);
                locks.All.Add((input.Path, stream));
                using var content = new MemoryStream();
                stream.CopyTo(content);
                var bytes = content.ToArray();
                Data.Require(Data.Hash(bytes) == input.Hash, "input_drift", $"Input changed before writes: {input.Path}");
                if (writing)
                {
                    Data.Require(bytes.SequenceEqual(Convert.FromBase64String(edit!.Before)), "input_drift", $"File changed before apply: {input.Path}");
                    locks.Writes.Add((edit, stream));
                }
            }
            foreach (var edit in plan.Edits.Where(e => e.Kind == "create"))
            {
                Data.Require(edit.Before == "" && !plan.Inputs.Any(i => Paths.Comparer.Equals(i.Path, edit.Path)),
                    "invalid_plan", "A create edit must have an absent original.");
                Paths.AbsentFile(edit.Path);
                locks.Creates.Add(edit);
            }
            Data.Require(locks.Writes.Count + locks.Creates.Count == edits.Count, "invalid_plan", "Every modification must have a captured input; only create may have none.");
            return locks;
        }
        catch (Exception error)
        {
            var closeFailures = FileApply.Close(locks.All);
            if (error is RefactorFailure && closeFailures.Length == 0) throw;
            throw new RefactorFailure("apply_preflight_failed", "No source writes began: " + error.Message, closeFailures);
        }
    }

    internal static FileStream OpenInput(InputFile input, bool writing = false)
    {
        if (input.CanonicalPath is null) Paths.RegularFile(input.Path);
        var stream = new FileStream(input.Path, FileMode.Open, writing ? FileAccess.ReadWrite : FileAccess.Read,
            writing ? FileShare.None : FileShare.Read, bufferSize: 1);
        try
        {
            if (input.CanonicalPath is not null)
                Data.Require(Paths.Comparer.Equals(input.CanonicalPath, Paths.CanonicalFile(stream)),
                    "input_drift", $"Input resolves to a different file path: {input.Path}");
            else
                Paths.RegularFile(input.Path);
            return stream;
        }
        catch { stream.Dispose(); throw; }
    }
}
