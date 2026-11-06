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
Console.WriteLine("Passed: partial write, remaining original file, recovery guidance, unreadable state.");

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
