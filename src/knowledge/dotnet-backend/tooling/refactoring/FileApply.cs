namespace RefactorTool;

internal sealed record FileState(string Path, string State, string? Hash);
internal sealed record ApplyResult(string Status, FileState[] Files, string? Error, string? Recovery, string Atomicity);

internal static class FileApply
{
    public const string Recovery = "Stop editing. Preserve this result and plan. Inspect every file against plan before/after bytes; restore only affected files from the plan's before base64 after checking for subsequent user edits. Unknown/partial states require manual inspection. Create a new preview before retrying.";

    // Handles are opened and all predictable validation is completed by the
    // caller. This phase reports observations even when a write or read fails.
    public static ApplyResult Write(IReadOnlyList<(FileEdit Edit, Stream Stream)> handles)
    {
        string? failure = null;
        try
        {
            foreach (var (edit, stream) in handles)
            {
                var bytes = Convert.FromBase64String(edit.After);
                stream.Position = 0; stream.Write(bytes, 0, bytes.Length); stream.SetLength(bytes.Length);
                if (stream is FileStream file) file.Flush(true); else stream.Flush();
            }
        }
        catch (Exception error) { failure = error.Message; }
        var states = new List<FileState>();
        var complete = failure is null;
        foreach (var (edit, stream) in handles)
        {
            var state = "unknown";
            string? hash = null;
            try
            {
                stream.Position = 0;
                using var content = new MemoryStream(); stream.CopyTo(content);
                hash = Data.Hash(content.ToArray());
                state = hash == Data.Hash(Convert.FromBase64String(edit.After)) ? "applied" :
                    hash == Data.Hash(Convert.FromBase64String(edit.Before)) ? "original" : "partial";
            }
            catch (Exception error) { failure ??= error.Message; }
            complete &= state == "applied";
            states.Add(new(edit.Path, state, hash));
        }
        return new(complete ? "applied" : "partial_failure", states.ToArray(), failure, complete ? null : Recovery,
            "Per-file observed results only; no cross-file atomicity or protection against noncooperating writers/process termination.");
    }
}
