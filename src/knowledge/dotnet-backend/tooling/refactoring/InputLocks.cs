namespace RefactorTool;

internal sealed class InputLocks
{
    public List<(string Path, Stream Stream)> All { get; } = [];
    public List<(FileEdit Edit, Stream Stream)> Writes { get; } = [];

    public static InputLocks Open(Plan plan)
    {
        var locks = new InputLocks();
        try
        {
            var edits = plan.Edits.ToDictionary(e => e.Path, Paths.Comparer);
            foreach (var input in plan.Inputs)
            {
                Paths.RegularFile(input.Path);
                var writing = edits.TryGetValue(input.Path, out var edit);
                if (writing)
                    Data.Require(edit!.Kind == "modify" && (File.GetAttributes(input.Path) & FileAttributes.ReadOnly) == 0,
                        "unwritable_source", $"Cannot modify: {input.Path}");
                // Unchanged inputs stay locked against ordinary write/delete
                // access as well; a transient hash check would leave a race.
                var stream = new FileStream(input.Path, FileMode.Open, writing ? FileAccess.ReadWrite : FileAccess.Read,
                    writing ? FileShare.None : FileShare.Read, bufferSize: 1);
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
            Data.Require(locks.Writes.Count == edits.Count, "invalid_plan", "Every edit must have a captured input.");
            return locks;
        }
        catch (Exception error)
        {
            var closeFailures = FileApply.Close(locks.All);
            if (error is RefactorFailure && closeFailures.Length == 0) throw;
            throw new RefactorFailure("apply_preflight_failed", "No source writes began: " + error.Message, closeFailures);
        }
    }
}
