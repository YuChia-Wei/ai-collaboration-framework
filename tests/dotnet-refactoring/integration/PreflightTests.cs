using System.Security.Cryptography;
using System.Text;

namespace RefactorTool.IntegrationTests;

[Trait("Boundary", "Preflight")]
public sealed class PreflightTests
{
    /// <summary>Rejects changed extraction input before recomputing or creating output.</summary>
    [WindowsFact]
    public void ExtractionApplyRefusesSourceDriftBeforeRecomputing()
    {
        using var fixture = new PreflightFixture();
        const string drifted = "namespace Demo; public class Service { public int Get() => 2; }";
        CommandResult result = null!;

        this.Given(GivenACapturedExtractionSourceWithLaterDrift, "a captured extraction source with later drift")
            .When(WhenApplyingTheStalePlan, "applying the stale plan")
            .Then(ThenRefuseWithoutOverwritingOrCreatingSource, "refuse without overwriting or creating source")
            .BDDfy();

        void GivenACapturedExtractionSourceWithLaterDrift()
        {
            fixture.WritePlan(fixture.Rename with
            {
                Operation = "extract-interface",
                Symbol = "T:Demo.Service",
                NewName = "ISelected",
                Namespace = "Contracts",
                OutputFile = fixture.Output,
                Members = ["M:Demo.Service.Get"]
            });
            File.WriteAllText(fixture.Source, drifted);
        }

        async Task WhenApplyingTheStalePlan() => result = await fixture.Apply();

        void ThenRefuseWithoutOverwritingOrCreatingSource()
        {
            fixture.AssertApplyRefused(result, "input_drift", drifted);
            Assert.False(File.Exists(fixture.Output));
        }
    }

    /// <summary>Rejects apply while a captured source or project input is held exclusively.</summary>
    [WindowsTheory]
    [InlineData(false)]
    [InlineData(true)]
    public void ExclusiveSourceOrProjectHandleRefusesBeforeWrites(bool project)
    {
        using var fixture = new PreflightFixture();
        CommandResult result = null!;

        this.Given(GivenCapturedProjectAndSourceInputs, "captured project and source inputs")
            .When(WhenApplyingWithTheSelectedInputHeldExclusively, "applying with the selected input held exclusively")
            .Then(ThenRefuseBeforeWritesOrRecovery, "refuse before writes or recovery")
            .BDDfy();

        void GivenCapturedProjectAndSourceInputs() => fixture.WritePlan(fixture.Rename);

        async Task WhenApplyingWithTheSelectedInputHeldExclusively()
        {
            using var held = File.Open(project ? fixture.Project : fixture.Source, FileMode.Open, FileAccess.Read, FileShare.None);
            result = await fixture.Apply();
        }

        void ThenRefuseBeforeWritesOrRecovery() => fixture.AssertApplyRefused(result, "apply_preflight_failed");
    }

    /// <summary>Rejects a missing canonical additional input without recreating or editing files.</summary>
    [WindowsJunctionFact]
    public void MissingCanonicalAdditionalFileRefusesBeforeWrites()
    {
        using var fixture = new PreflightFixture(additionalFile: true);
        string aliasPath = null!, original = null!;
        CommandResult result = null!;

        this.Given(GivenACanonicalAdditionalFileRemovedAfterCapture, "a canonical AdditionalFiles input removed after capture")
            .When(WhenApplyingThePlanWithTheMissingInput, "applying the plan with the missing input")
            .Then(ThenRefuseWithoutRecoveryOrRecreatingTheInput, "refuse without recovery or recreating the input")
            .BDDfy();

        async Task GivenACanonicalAdditionalFileRemovedAfterCapture()
        {
            original = fixture.Write("original-input/Config.props", "<Project />");
            await fixture.Junction("input-alias", Path.GetDirectoryName(original)!);
            aliasPath = fixture.PathFor("input-alias/Config.props");
            string canonical;
            using (var input = File.OpenRead(aliasPath)) canonical = Paths.CanonicalFile(input);
            Assert.Equal("original-input", Path.GetFileName(Path.GetDirectoryName(canonical)), ignoreCase: true);
            fixture.WritePlan(fixture.Rename, new InputFile(aliasPath, Hash("<Project />"u8), canonical));
            File.Delete(original);
        }

        async Task WhenApplyingThePlanWithTheMissingInput() => result = await fixture.Apply();

        void ThenRefuseWithoutRecoveryOrRecreatingTheInput()
        {
            fixture.AssertApplyRefused(result, "apply_preflight_failed");
            Assert.False(File.Exists(aliasPath));
            Assert.False(File.Exists(original));
        }
    }

    /// <summary>Rejects a plan path through a junction before reading the request.</summary>
    [WindowsJunctionFact]
    public void PlanDestinationJunctionIsRefusedBeforeLoadingTheRequest()
    {
        using var fixture = new PreflightFixture();
        string request = null!, plan = null!, physicalPlan = null!;
        CommandResult result = null!;

        this.Given(GivenAPlanDestinationThroughAJunction, "a plan destination through a junction")
            .When(WhenPreviewingToTheLinkedDestination, "previewing to the linked destination")
            .Then(ThenRefuseWithoutWritingToTheJunction, "refuse without writing to the junction")
            .BDDfy();

        async Task GivenAPlanDestinationThroughAJunction()
        {
            request = fixture.PathFor("missing-request.json");
            var target = Directory.CreateDirectory(fixture.PathFor("plan-output"));
            await fixture.Junction("plan-alias", target.FullName);
            plan = fixture.PathFor("plan-alias/plan.json");
            physicalPlan = Path.Combine(target.FullName, "plan.json");
        }

        async Task WhenPreviewingToTheLinkedDestination() => result = await CommandResult.Run("preview", "--request", request, "--plan", plan);

        void ThenRefuseWithoutWritingToTheJunction()
        {
            result.Refused("linked_path");
            Assert.False(File.Exists(plan));
            Assert.False(File.Exists(physicalPlan));
            fixture.AssertAuthoredFilesUnchanged();
        }
    }

    /// <summary>Rejects preflight for a read-only consumer before either planned file changes.</summary>
    [WindowsFact]
    public void ReadOnlyConsumerRefusesBeforeAnySourceChange()
    {
        using var directory = new TestDirectory();
        const string originalSource = "class Service {}";
        const string originalConsumer = "class Consumer { Service value = new(); }";
        string source = null!, consumer = null!;
        Plan plan = null!;
        Exception? failure = null;
        FileAttributes? originalAttributes = null;

        try
        {
            this.Given(GivenTwoPlannedChangesAndAReadOnlyConsumer, "two planned changes and a read-only consumer")
                .When(WhenOpeningThePlanInputs, "opening the plan inputs for apply")
                .Then(ThenRefuseBeforeChangingEitherFile, "refuse before changing either file")
                .BDDfy();
        }
        finally
        {
            if (originalAttributes is { } attributes)
                File.SetAttributes(consumer, attributes);
        }

        void GivenTwoPlannedChangesAndAReadOnlyConsumer()
        {
            source = directory.Write("A/Service.cs", originalSource);
            consumer = directory.Write("B/Consumer.cs", originalConsumer);
            var attributes = File.GetAttributes(consumer);
            originalAttributes = attributes;
            File.SetAttributes(consumer, attributes | FileAttributes.ReadOnly);
            plan = new Plan
            {
                Inputs = [new(source, Hash(Encoding.UTF8.GetBytes(originalSource))),
                    new(consumer, Hash(Encoding.UTF8.GetBytes(originalConsumer)))],
                Edits = [Modify(source, originalSource), Modify(consumer, originalConsumer)]
            };
        }

        void WhenOpeningThePlanInputs() => failure = Record.Exception(() =>
        {
            var locks = InputLocks.Open(plan);
            FileApply.Close(locks.All);
        });

        void ThenRefuseBeforeChangingEitherFile()
        {
            Assert.Equal("unwritable_source", Assert.IsType<RefactorFailure>(failure).Code);
            Assert.Equal(Encoding.UTF8.GetBytes(originalSource), File.ReadAllBytes(source));
            Assert.Equal(Encoding.UTF8.GetBytes(originalConsumer), File.ReadAllBytes(consumer));
        }

        static FileEdit Modify(string path, string text) =>
            new(path, "modify", Convert.ToBase64String(Encoding.UTF8.GetBytes(text)),
                Convert.ToBase64String(Encoding.UTF8.GetBytes(text.Replace("Service", "RenamedService"))));
    }

    private static string Hash(ReadOnlySpan<byte> bytes) => Convert.ToHexStringLower(SHA256.HashData(bytes));

    private sealed class PreflightFixture : IDisposable
    {
        private const string SourceText = "namespace Demo; public class Service { public int Get() => 1; }";
        private readonly TestDirectory directory = new();
        private readonly string projectText;
        private string planText = "";

        internal PreflightFixture(bool additionalFile = false)
        {
            projectText = additionalFile
                ? """<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup><TargetFramework>net10.0</TargetFramework></PropertyGroup><ItemGroup><AdditionalFiles Include="../input-alias/Config.props" /></ItemGroup></Project>"""
                : """<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup><TargetFramework>net10.0</TargetFramework></PropertyGroup></Project>""";
            Project = directory.Write("A/A.csproj", projectText);
            Source = directory.Write("A/Service.cs", SourceText);
        }

        internal string Project { get; }
        internal string Source { get; }
        internal string Output => directory.PathFor("A/ISelected.cs");
        internal Request Rename => new() { Workspace = Project, Project = Project, Symbol = "M:Demo.Service.Get", NewName = "Fetch" };

        internal string PathFor(string relative) => directory.PathFor(relative);
        internal string Write(string relative, string text) => directory.Write(relative, text);
        internal Task Junction(string relative, string target) => directory.Junction(relative, target);

        internal void WritePlan(Request request, params InputFile[] additional)
        {
            var before = File.ReadAllBytes(Source);
            FileEdit[] edits = request.Operation == "extract-interface"
                ? [new(Output, "create", "", Convert.ToBase64String("namespace Contracts; public interface ISelected { int Get(); }"u8)),
                   new(Source, "modify", Convert.ToBase64String(before), Convert.ToBase64String("namespace Demo; public class Service : Contracts.ISelected { public int Get() => 1; }"u8))]
                : [new(Source, "modify", Convert.ToBase64String(before), Convert.ToBase64String("namespace Demo; public class Service { public int Fetch() => 1; }"u8))];
            planText = Data.Serialize(new Plan
            {
                Request = request,
                Inputs = [new(Source, Hash(before)), new(Project, Hash(File.ReadAllBytes(Project))), .. additional],
                Edits = edits
            });
            directory.Write("plan.json", planText);
        }

        internal Task<CommandResult> Apply() => CommandResult.Run("apply", "--plan", directory.PathFor("plan.json"));

        internal void AssertApplyRefused(CommandResult result, string code, string currentSource = SourceText)
        {
            result.Refused(code);
            Assert.False(result.Json.TryGetProperty("recovery", out _));
            Assert.Equal(Encoding.UTF8.GetBytes(planText), File.ReadAllBytes(directory.PathFor("plan.json")));
            AssertAuthoredFilesUnchanged(currentSource);
        }

        internal void AssertAuthoredFilesUnchanged(string currentSource = SourceText)
        {
            Assert.Equal(Encoding.UTF8.GetBytes(currentSource), File.ReadAllBytes(Source));
            Assert.Equal(Encoding.UTF8.GetBytes(projectText), File.ReadAllBytes(Project));
        }

        public void Dispose() => directory.Dispose();
    }
}
