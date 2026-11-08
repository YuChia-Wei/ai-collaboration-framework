using System.Runtime.InteropServices;

namespace RefactorTool.IntegrationTests;

internal static class RefactorTestProfile
{
    internal static bool WindowsX64 =>
        OperatingSystem.IsWindows() && RuntimeInformation.OSArchitecture == Architecture.X64;

    internal static string? SdkSkip => !WindowsX64 ? WindowsSkip :
        Environment.GetEnvironmentVariable("AICF_REFACTOR_SDK_TESTS") == "1" ? null :
        "Set AICF_REFACTOR_SDK_TESTS=1 for .NET SDK 10.0.403 integration. Junction cases also require pwsh.";

    internal static string? Artifact => Environment.GetEnvironmentVariable("AICF_REFACTOR_TEST_ARTIFACT");
    internal const string WindowsSkip = "This case exercises a Windows x64 RefactorTool boundary.";
}

internal sealed class WindowsFactAttribute : FactAttribute
{
    public WindowsFactAttribute()
    {
        if (!RefactorTestProfile.WindowsX64)
            Skip = RefactorTestProfile.WindowsSkip;
    }
}

internal sealed class WindowsTheoryAttribute : TheoryAttribute
{
    public WindowsTheoryAttribute()
    {
        if (!RefactorTestProfile.WindowsX64)
            Skip = RefactorTestProfile.WindowsSkip;
    }
}

internal sealed class RefactorSdkFactAttribute : FactAttribute
{
    public RefactorSdkFactAttribute() => Skip = RefactorTestProfile.SdkSkip;
}

internal sealed class RefactorSdkTheoryAttribute : TheoryAttribute
{
    public RefactorSdkTheoryAttribute() => Skip = RefactorTestProfile.SdkSkip;
}

internal sealed class RefactorArtifactFactAttribute : FactAttribute
{
    public RefactorArtifactFactAttribute()
    {
        if (!RefactorTestProfile.WindowsX64)
            Skip = RefactorTestProfile.WindowsSkip;
        else if (RefactorTestProfile.Artifact is null)
            Skip = "Set AICF_REFACTOR_TEST_ARTIFACT to the extracted win-x64 RefactorTool.exe.";
    }
}
