namespace SnippetTool.IntegrationTests;

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
