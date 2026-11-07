using System.Text;
using System.Text.Json;

namespace RefactorTool.Tests;

public sealed class FileApplyTests
{
    [Fact]
    public void ReportsWrittenPrefixAndUntouchedFilesAfterFailure()
    {
        using var first = Original();
        using var failing = new FailingStream(failRead: false);
        using var last = Original();
        var result = FileApply.Write([(Edit("first"), first), (Edit("second"), failing), (Edit("last"), last)]);
        Assert.Equal("partial_failure", result.Status);
        Assert.Equal(new[] { "applied", "partial", "original" }, result.Files.Select(f => f.State));
        Assert.NotNull(result.Recovery);
        Assert.Equal("injected I/O failure", result.Error);
        Assert.Equal("AFfore", Encoding.UTF8.GetString(failing.ToArray()));
        Assert.Equal("before", Encoding.UTF8.GetString(last.ToArray()));
    }

    [Fact]
    public void UnreadableStateIsUnknown()
    {
        using var stream = new FailingStream(failRead: true);
        var result = FileApply.Write([(Edit("unknown"), stream)]);
        var file = Assert.Single(result.Files);
        Assert.Equal("unknown", file.State);
        Assert.Null(file.Hash);
    }

    [Fact]
    public void CloseFailurePreservesObservationsAndAttemptsEveryClose()
    {
        var first = new ClosingStream(true);
        var last = new ClosingStream(false);
        var observed = FileApply.Write([(Edit("first"), first), (Edit("last"), last)]);
        var closed = FileApply.AfterClose(observed, FileApply.Close([("first", first), ("last", last)]));
        Assert.True(first.CloseAttempted);
        Assert.True(last.CloseAttempted);
        Assert.Equal("partial_failure", closed.Status);
        Assert.Single(closed.CloseFailures);
        Assert.Equal("unknown", closed.Files[0].State);
        Assert.Null(closed.Files[0].Hash);
        Assert.Equal("applied", closed.Files[0].BeforeCloseState);
        Assert.NotNull(closed.Files[0].BeforeCloseHash);
        Assert.Equal("applied", closed.Files[1].State);
        using var json = JsonDocument.Parse(Data.Serialize(closed));
        Assert.Equal("partial_failure", json.RootElement.GetProperty("status").GetString());
    }

    [Fact]
    public void UnchangedInputDeniesOrdinaryWriterUntilHandlesClose()
    {
        using var directory = new TestDirectory();
        var unchanged = directory.Write("unchanged.cs", "caller");
        var changed = directory.Write("changed.cs", "before");
        string canonical;
        using (var stream = File.OpenRead(unchanged)) canonical = Paths.CanonicalFile(stream);
        var locks = InputLocks.Open(new Plan
        {
            Inputs = [new(unchanged, Data.Hash("caller"u8.ToArray()), canonical), Before(changed)],
            Edits = [Edit(changed)]
        });
        try
        {
            Assert.ThrowsAny<IOException>(() =>
            {
                using var competing = new FileStream(unchanged, FileMode.Open, FileAccess.Write, FileShare.ReadWrite);
            });
            Assert.Equal("applied", FileApply.Write(locks.Writes).Status);
        }
        finally { Assert.Empty(FileApply.Close(locks.All)); }
        File.WriteAllText(unchanged, "released");
        Assert.Equal("AFTER!", File.ReadAllText(changed));
        Assert.Equal("released", File.ReadAllText(unchanged));
    }

    [Fact]
    public void CompetingCreatorOwnsOutputAndExistingSourceStaysOriginal()
    {
        using var directory = new TestDirectory();
        var changed = directory.Write("changed.cs", "before");
        var created = directory.PathFor("created.cs");
        var locks = InputLocks.Open(new Plan { Inputs = [Before(changed)], Edits = [Edit(changed), Create(created)] });
        File.WriteAllText(created, "other writer");
        try
        {
            var result = FileApply.Write(locks.Writes, locks.Creates, locks.All);
            Assert.Equal("partial_failure", result.Status);
            Assert.Equal("original", Assert.Single(result.Files, f => f.Path == changed).State);
            Assert.Equal("unknown", Assert.Single(result.Files, f => f.Path == created).State);
        }
        finally { Assert.Empty(FileApply.Close(locks.All)); }
        Assert.Equal("other writer", File.ReadAllText(created));
        Assert.Equal("before", File.ReadAllText(changed));
    }

    [Fact]
    public void CreateAcquisitionFailureDistinguishesEmptyAndUnattemptedOutputs()
    {
        using var directory = new TestDirectory();
        using var original = Original();
        var empty = new MemoryStream();
        var handles = new List<(string Path, Stream Stream)>();
        var first = directory.PathFor("first.cs");
        try
        {
            var result = FileApply.Write([(Edit("existing"), original)], [Create(first), Create(directory.PathFor("second.cs")), Create(directory.PathFor("third.cs"))], handles,
                edit => edit.Path == first ? empty : throw new IOException("injected create failure"));
            Assert.Equal(new[] { "original", "created_empty", "unknown", "not_created" }, result.Files.Select(f => f.State));
            Assert.Empty(empty.ToArray());
        }
        finally { Assert.Empty(FileApply.Close(handles)); }
    }

    [Fact]
    public void PartialNewFileRequiresRecoveryForCreatedFile()
    {
        using var directory = new TestDirectory();
        using var original = Original();
        var partial = new FailingCreatedStream();
        var handles = new List<(string Path, Stream Stream)>();
        try
        {
            var result = FileApply.Write([(Edit("existing"), original)], [Create(directory.PathFor("created.cs"))], handles, _ => partial);
            Assert.Equal(new[] { "applied", "partial" }, result.Files.Select(f => f.State));
            Assert.Contains("had no original file", result.Recovery);
            Assert.Contains("never replace it with an empty", result.Recovery);
            Assert.Equal("in", Encoding.UTF8.GetString(partial.ToArray()));
        }
        finally { Assert.Empty(FileApply.Close(handles)); }
    }

    private static FileEdit Edit(string path) => new(path, "modify", Convert.ToBase64String("before"u8), Convert.ToBase64String("AFTER!"u8));
    private static FileEdit Create(string path) => new(path, "create", "", Convert.ToBase64String("interface I {}"u8));
    private static InputFile Before(string path) => new(path, Data.Hash("before"u8.ToArray()));

    private static MemoryStream Original()
    {
        var stream = new MemoryStream();
        stream.Write("before"u8);
        stream.Position = 0;
        return stream;
    }
}

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
