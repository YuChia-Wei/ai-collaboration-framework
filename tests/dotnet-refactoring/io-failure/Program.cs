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
    var plan = new Plan { Inputs = [new(unchanged, Data.Hash("caller"u8.ToArray())), new(changed, Data.Hash("before"u8.ToArray()))], Edits = [Edit(changed)] };
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
}
finally { Directory.Delete(directory, recursive: true); }
Console.WriteLine("Passed: partial write, original/unknown state, recovery, close failure/all handles closed, unchanged-input lock and release.");

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
