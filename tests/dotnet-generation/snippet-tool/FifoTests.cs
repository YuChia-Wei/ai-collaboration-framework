using Aicf.Dotnet.TestSupport;
using Generation.TestSupport;
using System.Runtime.InteropServices;
using System.Text.Json;
using static SnippetTool.IntegrationTests.SnippetTestSupport;

namespace SnippetTool.IntegrationTests;

public sealed class FifoTests
{
    /// <summary>
    /// Rejects a real Linux x64 FIFO used as a snippet body and returns the error without blocking.
    /// </summary>
    [SnippetLinuxFifoFact]
    [Trait("Platform", "Linux")]
    public void RejectsFifoBodyWithoutBlocking()
    {
        using var fixture = new GenerationFixture();
        string host = null!, assembly = null!, request = null!;
        (int Exit, string Output, string Error) run = (0, "", "");

        this.Given(GivenTheSourceBuildAndAFifoBody, "the source build and a FIFO body without a writer")
            .When(WhenInspectingTheFifoBody, "inspecting the FIFO body in a bounded child process")
            .Then(ThenRejectTheBodyWithoutBlocking, "reject the body without blocking")
            .BDDfy();

        async Task GivenTheSourceBuildAndAFifoBody()
        {
            host = DotnetTestHost.RequireExecutable();
            assembly = Path.Combine(AppContext.BaseDirectory, "SnippetTool.dll");
            Assert.True(File.Exists(assembly), $"Source-built SnippetTool is missing: {assembly}");
            WriteCatalog(fixture);
            var path = Path.Combine(fixture.Root, "custom-probe.snippet");
            var fifo = await fixture.Execute(SnippetLinuxFifoFactAttribute.RequireMkfifo(), TimeSpan.FromSeconds(3), "--", path);
            Assert.True(fifo.Exit == 0, $"mkfifo exited {fifo.Exit}: {fifo.Error}");
            request = fixture.Write("request.json", JsonSerializer.Serialize(Inspect("custom-probe")));
        }

        async Task WhenInspectingTheFifoBody() =>
            run = await fixture.Execute(host, TimeSpan.FromSeconds(5), assembly, "--request", request);

        void ThenRejectTheBodyWithoutBlocking() => ReadResult(run, "invalid-body");
    }
}

internal sealed class SnippetLinuxFifoFactAttribute : FactAttribute
{
    private const string MissingMkfifo = "The FIFO regression requires mkfifo on PATH.";
    private static readonly Lazy<DotnetTestHost.Command> Mkfifo = new(() => DotnetTestHost.DiscoverCommand("mkfifo"));

    public SnippetLinuxFifoFactAttribute()
    {
        Skip = OperatingSystem.IsLinux() && RuntimeInformation.ProcessArchitecture == Architecture.X64
            ? Mkfifo.Value.Skip(MissingMkfifo)
            : "The FIFO regression requires Linux x64.";
    }

    internal static string RequireMkfifo() => Mkfifo.Value.Require(MissingMkfifo);
}
