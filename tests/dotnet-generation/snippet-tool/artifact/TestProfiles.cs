using System.Runtime.InteropServices;

namespace SnippetTool.IntegrationTests;

internal sealed class SnippetArtifactFactAttribute : FactAttribute
{
    internal static string? Artifact => Environment.GetEnvironmentVariable("AICF_SNIPPET_ARTIFACT");

    public SnippetArtifactFactAttribute()
    {
        var supported = RuntimeInformation.ProcessArchitecture switch
        {
            Architecture.X64 => OperatingSystem.IsWindows() || OperatingSystem.IsLinux(),
            Architecture.Arm64 => OperatingSystem.IsMacOS(),
            _ => false
        };
        if (!supported)
            Skip = "The SnippetTool artifact requires Windows x64, Linux x64 or macOS arm64.";
    }
}
