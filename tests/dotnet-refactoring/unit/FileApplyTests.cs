using System.Text;
using System.Text.Json;

namespace RefactorTool.UnitTests;

public sealed class FileApplyTests
{
    [Fact]
    public void ReportsWrittenPrefixAndUntouchedFilesAfterFailure()
    {
        using var first = Original();
        using var failing = new FailingStream(failRead: false);
        using var last = Original();
        ApplyResult result = null!;
        (FileEdit Edit, Stream Stream)[] writes = null!;

        this.Given(GivenTwoWritableStreamsAndOneFailingStream, "two writable streams and one failing stream")
            .When(WhenApplyingTheThreeEdits, "applying the three edits")
            .Then(ThenReportTheWrittenPrefixAndPreserveTheUntouchedStream, "report the written prefix and preserve the untouched stream")
            .BDDfy();

        void GivenTwoWritableStreamsAndOneFailingStream() =>
            writes = [(Edit("first"), first), (Edit("second"), failing), (Edit("last"), last)];

        void WhenApplyingTheThreeEdits() => result = FileApply.Write(writes);

        void ThenReportTheWrittenPrefixAndPreserveTheUntouchedStream()
        {
            Assert.Equal("partial_failure", result.Status);
            Assert.Equal(new[] { "applied", "partial", "original" }, result.Files.Select(f => f.State));
            Assert.NotNull(result.Recovery);
            Assert.Equal("injected I/O failure", result.Error);
            Assert.Equal("AFfore", Encoding.UTF8.GetString(failing.ToArray()));
            Assert.Equal("before", Encoding.UTF8.GetString(last.ToArray()));
        }
    }

    [Fact]
    public void UnreadableStateIsUnknown()
    {
        using var stream = new FailingStream(failRead: true);
        ApplyResult result = null!;
        FileEdit edit = null!;

        this.Given(GivenAnEditWithAnUnreadableStream, "an edit whose stream cannot be read after failure")
            .When(WhenApplyingTheEdit, "applying the edit")
            .Then(ThenReportUnknownWithoutAHash, "report unknown without a hash")
            .BDDfy();

        void GivenAnEditWithAnUnreadableStream() => edit = Edit("unknown");

        void WhenApplyingTheEdit() => result = FileApply.Write([(edit, stream)]);

        void ThenReportUnknownWithoutAHash()
        {
            var file = Assert.Single(result.Files);
            Assert.Equal("unknown", file.State);
            Assert.Null(file.Hash);
        }
    }

    [Fact]
    public void CloseFailurePreservesObservationsAndAttemptsEveryClose()
    {
        UnitTests.ClosingStream first = null!;
        UnitTests.ClosingStream last = null!;
        ApplyResult observed = null!;
        ApplyResult closed = null!;

        this.Given(GivenWrittenStreamsAndOneFailingClose, "written streams and one failing close")
            .When(WhenClosingTheWrittenStreams, "closing the written streams")
            .Then(ThenKeepThePreCloseObservationAndAttemptEveryClose, "keep the pre close observation and attempt every close")
            .BDDfy();

        void GivenWrittenStreamsAndOneFailingClose()
        {
            first = new ClosingStream(true);
            last = new ClosingStream(false);
            observed = FileApply.Write([(Edit("first"), first), (Edit("last"), last)]);
        }

        void WhenClosingTheWrittenStreams()
        {
            closed = FileApply.AfterClose(observed, FileApply.Close([("first", first), ("last", last)]));
        }

        void ThenKeepThePreCloseObservationAndAttemptEveryClose()
        {
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
    }

    private static FileEdit Edit(string path) => new(path, "modify", Convert.ToBase64String("before"u8), Convert.ToBase64String("AFTER!"u8));

    private static MemoryStream Original()
    {
        var stream = new MemoryStream();
        stream.Write("before"u8);
        stream.Position = 0;
        return stream;
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
