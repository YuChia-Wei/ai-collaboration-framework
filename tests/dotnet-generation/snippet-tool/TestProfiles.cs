using Generation.TestSupport;

namespace SnippetTool.IntegrationTests;

internal sealed class SnippetSdkFactAttribute : FactAttribute
{
    public SnippetSdkFactAttribute()
    {
        if (!GenerationFixture.RunSdkTests)
            Skip = "Set AICF_GENERATION_SDK_TESTS=1 to compile rendered fragments with the SDK.";
    }
}

internal sealed class SnippetArtifactFactAttribute : FactAttribute
{
    internal static string? Artifact => Environment.GetEnvironmentVariable("AICF_SNIPPET_ARTIFACT");

    public SnippetArtifactFactAttribute(bool linuxOnly = false)
    {
        if (linuxOnly && !OperatingSystem.IsLinux())
            Skip = "The FIFO regression requires Linux.";
        else if (Artifact is null)
            Skip = "Set AICF_SNIPPET_ARTIFACT to the staged SnippetTool executable.";
    }
}
