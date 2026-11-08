using System.Text;

namespace RefactorTool.IntegrationTests;

public sealed class FileApplyTests
{
    [WindowsFact]
    public void UnchangedInputDeniesOrdinaryWriterUntilHandlesClose()
    {
        using var directory = new TestDirectory();
        string unchanged = null!, changed = null!;
        Plan plan = null!;
        Exception? competingError = null;
        ApplyResult applied = null!;
        CloseFailure[] closed = null!;

        this.Given(GivenAPlanWithOneUnchangedCanonicalInput, "a plan with one unchanged canonical input")
            .When(WhenApplyingWithTheInputHeldAgainstWriters, "applying with the input held against writers")
            .Then(ThenDenyTheCompetingWriterAndApplyTheEdit, "deny the competing writer and apply the edit")
            .When(WhenWritingAfterTheInputHandleCloses, "writing after the input handle closes")
            .Then(ThenAllowTheWriterAfterRelease, "allow the writer after release")
            .BDDfy();

        void GivenAPlanWithOneUnchangedCanonicalInput()
        {
            unchanged = directory.Write("unchanged.cs", "caller");
            changed = directory.Write("changed.cs", "before");
            using var stream = File.OpenRead(unchanged);
            plan = new Plan
            {
                Inputs = [new(unchanged, Data.Hash("caller"u8.ToArray()), Paths.CanonicalFile(stream)), Before(changed)],
                Edits = [Edit(changed)]
            };
        }

        void WhenApplyingWithTheInputHeldAgainstWriters()
        {
            var locks = InputLocks.Open(plan);
            try
            {
                competingError = Record.Exception(() =>
                {
                    using var competing = new FileStream(unchanged, FileMode.Open, FileAccess.Write, FileShare.ReadWrite);
                });
                applied = FileApply.Write(locks.Writes);
            }
            finally { closed = FileApply.Close(locks.All); }
        }

        void ThenDenyTheCompetingWriterAndApplyTheEdit()
        {
            Assert.IsAssignableFrom<IOException>(competingError);
            Assert.Equal("applied", applied.Status);
            Assert.Empty(closed);
            Assert.Equal("AFTER!", File.ReadAllText(changed));
        }

        void WhenWritingAfterTheInputHandleCloses() => File.WriteAllText(unchanged, "released");

        void ThenAllowTheWriterAfterRelease() => Assert.Equal("released", File.ReadAllText(unchanged));
    }

    [Fact]
    public void CompetingCreatorOwnsOutputAndExistingSourceStaysOriginal()
    {
        using var directory = new TestDirectory();
        string changed = null!, created = null!;
        ApplyResult result = null!;
        CloseFailure[] closed = null!;

        this.Given(GivenAnExistingSourceAndAnAbsentOutput, "an existing source and an absent output")
            .When(WhenApplyingAfterACompetingWriterCreatesTheOutput, "applying after a competing writer creates the output")
            .Then(ThenPreserveTheCompetingOutputAndExistingSource, "preserve the competing output and existing source")
            .BDDfy();

        void GivenAnExistingSourceAndAnAbsentOutput()
        {
            changed = directory.Write("changed.cs", "before");
            created = directory.PathFor("created.cs");
        }

        void WhenApplyingAfterACompetingWriterCreatesTheOutput()
        {
            var locks = InputLocks.Open(new Plan { Inputs = [Before(changed)], Edits = [Edit(changed), Create(created)] });
            try
            {
                File.WriteAllText(created, "other writer");
                result = FileApply.Write(locks.Writes, locks.Creates, locks.All);
            }
            finally { closed = FileApply.Close(locks.All); }
        }

        void ThenPreserveTheCompetingOutputAndExistingSource()
        {
            Assert.Empty(closed);
            Assert.Equal("partial_failure", result.Status);
            Assert.Equal("original", Assert.Single(result.Files, f => f.Path == changed).State);
            Assert.Equal("unknown", Assert.Single(result.Files, f => f.Path == created).State);
            Assert.Equal("other writer", File.ReadAllText(created));
            Assert.Equal("before", File.ReadAllText(changed));
        }
    }

    [Fact]
    public void CreateAcquisitionFailureDistinguishesEmptyAndUnattemptedOutputs()
    {
        using var directory = new TestDirectory();
        using var original = Original();
        using var empty = new MemoryStream();
        string first = directory.PathFor("first.cs");
        FileEdit[] creates = null!;
        ApplyResult result = null!;
        CloseFailure[] closed = null!;

        this.Given(GivenThreeNewOutputsAndAnExistingSource, "three new outputs and an existing source")
            .When(WhenTheSecondCreateFailsDuringApply, "the second create fails during apply")
            .Then(ThenDistinguishEmptyUnknownAndUnattemptedOutputs, "distinguish empty, unknown and unattempted outputs")
            .BDDfy();

        void GivenThreeNewOutputsAndAnExistingSource() =>
            creates = [Create(first), Create(directory.PathFor("second.cs")), Create(directory.PathFor("third.cs"))];

        void WhenTheSecondCreateFailsDuringApply()
        {
            var handles = new List<(string Path, Stream Stream)>();
            try
            {
                result = FileApply.Write([(Edit("existing"), original)], creates, handles,
                    edit => edit.Path == first ? empty : throw new IOException("injected create failure"));
            }
            finally { closed = FileApply.Close(handles); }
        }

        void ThenDistinguishEmptyUnknownAndUnattemptedOutputs()
        {
            Assert.Empty(closed);
            Assert.Equal(new[] { "original", "created_empty", "unknown", "not_created" }, result.Files.Select(f => f.State));
            Assert.Empty(empty.ToArray());
        }
    }

    [Fact]
    public void PartialNewFileRequiresRecoveryForCreatedFile()
    {
        using var directory = new TestDirectory();
        using var original = Original();
        using var partial = new FailingCreatedStream();
        FileEdit created = null!;
        ApplyResult result = null!;
        CloseFailure[] closed = null!;

        this.Given(GivenAnExistingSourceAndANewOutput, "an existing source and a new output")
            .When(WhenTheNewOutputWriteFailsPartway, "the new output write fails partway")
            .Then(ThenReportRecoveryAndKeepTheObservedPartialBytes, "report recovery and keep the observed partial bytes")
            .BDDfy();

        void GivenAnExistingSourceAndANewOutput() => created = Create(directory.PathFor("created.cs"));

        void WhenTheNewOutputWriteFailsPartway()
        {
            var handles = new List<(string Path, Stream Stream)>();
            try { result = FileApply.Write([(Edit("existing"), original)], [created], handles, _ => partial); }
            finally { closed = FileApply.Close(handles); }
        }

        void ThenReportRecoveryAndKeepTheObservedPartialBytes()
        {
            Assert.Empty(closed);
            Assert.Equal(new[] { "applied", "partial" }, result.Files.Select(f => f.State));
            Assert.Contains("no original file", result.Recovery);
            Assert.Contains("never replace it with an empty", result.Recovery);
            Assert.Equal("in", Encoding.UTF8.GetString(partial.ToArray()));
        }
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
