using RefactorTool;
using System.Text;

static FileEdit Edit(string path) => new(path, "modify", Convert.ToBase64String("before"u8), Convert.ToBase64String("AFTER!"u8));
static MemoryStream Original()
{
    var stream = new MemoryStream(); stream.Write("before"u8); stream.Position = 0; return stream;
}
static void Check(bool condition, string message)
{
    if (!condition) throw new Exception(message);
}

using var first = Original();
using var failing = new FailingStream(failRead: false);
using var last = Original();
var result = FileApply.Write([(Edit("first"), first), (Edit("second"), failing), (Edit("last"), last)]);
Check(result.Status == "partial_failure", "Partial writes must not report success.");
Check(result.Files.Select(f => f.State).SequenceEqual(["applied", "partial", "original"]), "Actual file states must survive an intermediate failure.");
Check(result.Recovery is not null && result.Error == "injected I/O failure", "Failure and recovery must remain visible.");
Check(Encoding.UTF8.GetString(failing.ToArray()) == "AFfore", "Test must actually write a prefix before failing.");
using var unknown = new FailingStream(failRead: true);
result = FileApply.Write([(Edit("unknown"), unknown)]);
Check(result.Files.Single().State == "unknown" && result.Files.Single().Hash is null, "Unreadable post-failure state must remain unknown.");
var closeFirst = new ClosingStream(true);
var closeLast = new ClosingStream(false);
var observed = FileApply.Write([(Edit("close-first"), closeFirst), (Edit("close-last"), closeLast)]);
var failures = FileApply.Close([("close-first", closeFirst), ("close-last", closeLast)]);
var closed = FileApply.AfterClose(observed, failures);
Check(closeFirst.CloseAttempted && closeLast.CloseAttempted, "All closes must be attempted after a close failure.");
Check(closed.Status == "partial_failure" && closed.CloseFailures.Length == 1, "Close failure must not report success.");
Check(closed.Files[0].State == "unknown" && closed.Files[0].Hash is null && closed.Files[0].BeforeCloseState == "applied" && closed.Files[0].BeforeCloseHash is not null,
    "Close failure must preserve prior observations without claiming final bytes.");
Check(closed.Files[1].State == "applied", "Successful closes keep their observations.");
using var response = System.Text.Json.JsonDocument.Parse(Data.Serialize(closed));
Check(response.RootElement.GetProperty("status").GetString() == "partial_failure", "Close result must be a single parseable response.");

var directory = Path.Combine(Path.GetTempPath(), "refactor-locks-" + Guid.NewGuid().ToString("N"));
Directory.CreateDirectory(directory);
try
{
    var unchanged = Path.Combine(directory, "unchanged.cs");
    var changed = Path.Combine(directory, "changed.cs");
    File.WriteAllBytes(unchanged, "caller"u8.ToArray()); File.WriteAllBytes(changed, "before"u8.ToArray());
    string canonical;
    using (var stream = File.OpenRead(unchanged)) canonical = Paths.CanonicalFile(stream);
    var plan = new Plan { Inputs = [new(unchanged, Data.Hash("caller"u8.ToArray()), canonical), new(changed, Data.Hash("before"u8.ToArray()))], Edits = [Edit(changed)] };
    var locks = InputLocks.Open(plan);
    try
    {
        var blocked = false;
        try { using var concurrent = new FileStream(unchanged, FileMode.Open, FileAccess.Write, FileShare.ReadWrite); }
        catch (IOException) { blocked = true; }
        Check(blocked, "An unchanged captured input must remain protected from an ordinary writer until apply ends.");
        Check(FileApply.Write(locks.Writes).Status == "applied", "Locked writes must remain functional.");
    }
    finally { Check(FileApply.Close(locks.All).Length == 0, "Input handles must all close."); }
    File.WriteAllText(unchanged, "released");
    Check(File.ReadAllText(changed) == "AFTER!", "Destination write must complete.");

    // A competing creator after preflight owns that path. CreateNew must fail
    // without overwriting it or modifying the class that would use the output.
    File.WriteAllBytes(changed, "before"u8.ToArray());
    var createdPath = Path.Combine(directory, "created.cs");
    var createEdit = new FileEdit(createdPath, "create", "", Convert.ToBase64String("interface I {}"u8));
    plan = new Plan { Inputs = [new(changed, Data.Hash("before"u8.ToArray()))], Edits = [Edit(changed), createEdit] };
    locks = InputLocks.Open(plan);
    File.WriteAllText(createdPath, "other writer");
    try
    {
        result = FileApply.Write(locks.Writes, locks.Creates, locks.All);
        Check(result.Status == "partial_failure", "Output race must fail.");
        Check(result.Files.Single(f => f.Path == changed).State == "original", "Output acquisition must precede all modifications.");
        Check(result.Files.Single(f => f.Path == createdPath).State == "unknown", "Failed create must not claim ownership of an existing file.");
    }
    finally { FileApply.Close(locks.All); }
    Check(File.ReadAllText(createdPath) == "other writer" && File.ReadAllText(changed) == "before", "Racing output and original source must be preserved.");

    using var originalForCreate = Original();
    var emptyCreated = new MemoryStream();
    var secondCreate = createEdit with { Path = Path.Combine(directory, "second.cs") };
    var thirdCreate = createEdit with { Path = Path.Combine(directory, "third.cs") };
    var createHandles = new List<(string Path, Stream Stream)>();
    result = FileApply.Write([(Edit(changed), originalForCreate)], [createEdit, secondCreate, thirdCreate], createHandles,
        e => e.Path == createdPath ? emptyCreated : throw new IOException("injected create failure"));
    Check(result.Files.Select(f => f.State).SequenceEqual(["original", "created_empty", "unknown", "not_created"]),
        "Failed output acquisition must report empty created files and distinguish unattempted outputs.");
    Check(FileApply.Close(createHandles).Length == 0, "Created handles must close after acquisition failure.");

    using var originalForPartial = Original();
    var partialCreated = new FailingCreatedStream();
    createHandles = [];
    result = FileApply.Write([(Edit(changed), originalForPartial)], [createEdit], createHandles, _ => partialCreated);
    Check(result.Files.Select(f => f.State).SequenceEqual(["applied", "partial"]), "A new-file partial write must never report an absent/original file.");
    Check(result.Recovery!.Contains("had no original file") && result.Recovery.Contains("never replace it with an empty"), "Recovery must distinguish create from modify.");
    Check(FileApply.Close(createHandles).Length == 0, "Partial created handle must close.");
}
finally { Directory.Delete(directory, recursive: true); }
Console.WriteLine("Passed: partial write, original/unknown state, recovery, close failure/all handles closed, unchanged-input lock and release; create race, empty/partial output and unattempted create states.");

sealed class FailingCreatedStream : MemoryStream
{
    public override void Write(byte[] buffer, int offset, int count)
    {
        base.Write(buffer, offset, 2);
        throw new IOException("injected new-file write failure");
    }
}

sealed class ClosingStream(bool failClose) : MemoryStream
{
    public bool CloseAttempted { get; private set; }
    protected override void Dispose(bool disposing)
    {
        CloseAttempted = true;
        base.Dispose(disposing);
        if (failClose) throw new IOException("injected close failure");
    }
}

sealed class FailingStream : MemoryStream
{
    private readonly bool failRead;
    public FailingStream(bool failRead)
    {
        this.failRead = failRead;
        base.Write("before"u8.ToArray(), 0, 6); Position = 0;
    }
    public override void Write(byte[] buffer, int offset, int count)
    {
        base.Write(buffer, offset, 2);
        throw new IOException("injected I/O failure");
    }
    public override void CopyTo(Stream destination, int bufferSize)
    {
        if (failRead) throw new IOException("injected unreadable state");
        base.CopyTo(destination, bufferSize);
    }
}
