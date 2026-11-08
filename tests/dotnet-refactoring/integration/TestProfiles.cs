using Aicf.Dotnet.TestSupport;
using System.Runtime.InteropServices;

namespace RefactorTool.IntegrationTests;

internal static class RefactorTestProfile
{
    internal static bool WindowsX64 =>
        OperatingSystem.IsWindows() && RuntimeInformation.OSArchitecture == Architecture.X64;

    internal static string? SdkSkip => !WindowsX64 ? WindowsSkip : DotnetTestHost.SdkSkip(SdkFixture.Version);

    private static readonly Lazy<DotnetTestHost.Command> Pwsh = new(() => DotnetTestHost.DiscoverCommand("pwsh.exe"));

    internal static string? JunctionSkip => Pwsh.Value.Skip(JunctionPrerequisite);
    internal static string RequirePwsh() => Pwsh.Value.Require(JunctionPrerequisite);

    internal const string WindowsSkip = "This case exercises a Windows x64 RefactorTool boundary.";
    internal const string JunctionPrerequisite = "Windows junction fixtures require pwsh.exe on PATH.";
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

internal sealed class WindowsJunctionFactAttribute : FactAttribute
{
    public WindowsJunctionFactAttribute()
    {
        if (!RefactorTestProfile.WindowsX64)
            Skip = RefactorTestProfile.WindowsSkip;
        else
            Skip = RefactorTestProfile.JunctionSkip;
    }
}

internal sealed class RefactorSdkFactAttribute : FactAttribute
{
    public RefactorSdkFactAttribute(bool requiresJunction = false)
    {
        Skip = RefactorTestProfile.SdkSkip;
        if (Skip is null && requiresJunction && !DotnetTestHost.SdkProbeFaulted)
            Skip = RefactorTestProfile.JunctionSkip;
    }
}

internal sealed class RefactorSdkTheoryAttribute : TheoryAttribute
{
    public RefactorSdkTheoryAttribute() => Skip = RefactorTestProfile.SdkSkip;
}
