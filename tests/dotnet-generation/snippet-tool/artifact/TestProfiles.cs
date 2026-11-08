using Aicf.Dotnet.TestSupport;
using System.Runtime.InteropServices;

namespace SnippetTool.IntegrationTests;

internal sealed class SnippetArtifactFactAttribute : FactAttribute
{
    internal static string? Artifact => Environment.GetEnvironmentVariable("AICF_SNIPPET_ARTIFACT");
    private const string FifoPrerequisite = "The FIFO regression requires mkfifo on PATH.";
    private static readonly Lazy<DotnetTestHost.Command> FifoCommand = new(() => DotnetTestHost.DiscoverCommand("mkfifo"));

    internal static string RequireMkfifo() => FifoCommand.Value.Require(FifoPrerequisite);

    public SnippetArtifactFactAttribute(bool linuxOnly = false)
    {
        var supported = RuntimeInformation.ProcessArchitecture switch
        {
            Architecture.X64 => OperatingSystem.IsWindows() || OperatingSystem.IsLinux(),
            Architecture.Arm64 => OperatingSystem.IsMacOS(),
            _ => false
        };
        if (!supported)
            Skip = "The SnippetTool artifact requires Windows x64, Linux x64 or macOS arm64.";
        else if (linuxOnly && !OperatingSystem.IsLinux())
            Skip = "The FIFO regression requires Linux x64.";
        else if (linuxOnly)
            Skip = FifoCommand.Value.Skip(FifoPrerequisite);
    }
}
