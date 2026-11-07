namespace RefactorTool;

internal sealed record FileState(string Path, string State, string? Hash)
{
    public string? BeforeCloseState { get; init; }
    public string? BeforeCloseHash { get; init; }
}
internal sealed record CloseFailure(string Path, string Message);
internal sealed record ApplyResult(string Status, FileState[] Files, string? Error, string? Recovery, string Atomicity)
{
    public CloseFailure[] CloseFailures { get; init; } = [];
}

internal static class FileApply
{
    public const string Recovery = "Stop editing. Preserve this result and plan. Inspect every file against plan before/after bytes; restore modified files from before base64 only after checking for subsequent user edits. A create entry had no original file: remove a created file only after verifying its identity, contents and absence of subsequent user edits; never replace it with an empty before payload. Unknown/partial/not-created states require manual inspection; an output conflict may belong to another writer. Create a new preview before retrying.";

    // Handles are opened and all predictable validation is completed by the
    // caller. This phase reports observations even when a write or read fails.
    public static ApplyResult Write(IReadOnlyList<(FileEdit Edit, Stream Stream)> handles,
        IReadOnlyList<FileEdit>? creates = null, List<(string Path, Stream Stream)>? all = null,
        Func<FileEdit, Stream>? create = null)
    {
        creates ??= [];
        var opened = handles.ToList();
        var attempted = new HashSet<string>(Paths.Comparer);
        string? failure = null;
        try
        {
            // CreateNew is the absence check at the write boundary. Acquire all
            // output handles before modifying any existing source. Empty new
            // files are still writes and are reported if acquisition fails.
            foreach (var edit in creates)
            {
                Paths.RegularDirectory(Path.GetDirectoryName(edit.Path)!);
                attempted.Add(edit.Path);
                var stream = create is null
                    ? new FileStream(edit.Path, FileMode.CreateNew, FileAccess.ReadWrite, FileShare.None, bufferSize: 1)
                    : create(edit);
                opened.Add((edit, stream));
                all?.Add((edit.Path, stream));
            }
            foreach (var (edit, stream) in opened)
            {
                var bytes = Convert.FromBase64String(edit.After);
                stream.Position = 0; stream.Write(bytes, 0, bytes.Length); stream.SetLength(bytes.Length);
                if (stream is FileStream file) file.Flush(true); else stream.Flush();
            }
        }
        catch (Exception error) { failure = error.Message; }
        var states = new List<FileState>();
        var complete = failure is null;
        foreach (var (edit, stream) in opened)
        {
            var state = "unknown";
            string? hash = null;
            try
            {
                stream.Position = 0;
                using var content = new MemoryStream(); stream.CopyTo(content);
                hash = Data.Hash(content.ToArray());
                state = hash == Data.Hash(Convert.FromBase64String(edit.After)) ? "applied" : edit.Kind == "create"
                    ? (content.Length == 0 ? "created_empty" : "partial")
                    : hash == Data.Hash(Convert.FromBase64String(edit.Before)) ? "original" : "partial";
            }
            catch (Exception error) { failure ??= error.Message; }
            complete &= state == "applied";
            states.Add(new(edit.Path, state, hash));
        }
        foreach (var edit in creates.Where(e => !opened.Any(h => Paths.Comparer.Equals(h.Edit.Path, e.Path))))
        {
            complete = false;
            states.Add(new(edit.Path, attempted.Contains(edit.Path) ? "unknown" : "not_created", null));
        }
        return new(complete ? "applied" : "partial_failure", states.ToArray(), failure, complete ? null : Recovery,
            "Per-file observed results only; no cross-file atomicity or protection against noncooperating writers/process termination.");
    }

    public static CloseFailure[] Close(IEnumerable<(string Path, Stream Stream)> handles)
    {
        var failures = new List<CloseFailure>();
        foreach (var (path, stream) in handles)
            try { stream.Dispose(); }
            catch (Exception error) { failures.Add(new(path, error.Message)); }
        return failures.ToArray();
    }

    public static ApplyResult AfterClose(ApplyResult result, CloseFailure[] failures)
    {
        if (failures.Length == 0) return result;
        var uncertain = new HashSet<string>(failures.Select(f => f.Path), Paths.Comparer);
        return result with
        {
            Status = "partial_failure", Recovery = Recovery, CloseFailures = failures,
            Error = result.Error ?? "Closing one or more input files failed.",
            Files = result.Files.Select(f => uncertain.Contains(f.Path)
                ? f with { State = "unknown", Hash = null, BeforeCloseState = f.State, BeforeCloseHash = f.Hash } : f).ToArray()
        };
    }
}
