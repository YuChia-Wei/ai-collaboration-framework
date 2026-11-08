using Aicf.Dotnet.TestSupport;

namespace FormatTool.IntegrationTests;

internal sealed class FormatArtifactFactAttribute : FactAttribute
{
    public FormatArtifactFactAttribute(bool caseSensitive = false)
    {
        if (FormatFixture.SdkVersion is null)
            Skip = "The formatter artifact requires Windows x64 or macOS arm64.";
        else if (caseSensitive && !FormatFixture.MacArm64)
            Skip = "The case-sensitive volume scenario requires macOS arm64.";
        else if (caseSensitive)
            Skip = FormatArtifactProfile.CaseRootSkip;
    }
}

internal static class FormatArtifactProfile
{
    private const string ExecutableInput = "AICF_FORMAT_ARTIFACT";
    private const string CaseRootInput = "AICF_FORMAT_CASE_ROOT";
    private sealed record CaseRoot(string? Path, string? Failure = null);
    private static readonly Lazy<CaseRoot> Case = new(ProbeCaseRoot);

    internal static string RequireExecutable() =>
        PublishedExecutable.Require(Environment.GetEnvironmentVariable(ExecutableInput), "FormatTool", ExecutableInput);

    internal static string? CaseRootSkip => Case.Value is { Path: null, Failure: null }
        ? "The formatter scratch volume does not distinguish case aliases." : null;

    internal static string RequireCaseRoot()
    {
        var result = Case.Value;
        if (result.Failure is not null) throw new InvalidOperationException(result.Failure);
        return result.Path ?? throw new InvalidOperationException("The formatter scratch volume does not distinguish case aliases.");
    }

    private static CaseRoot ProbeCaseRoot()
    {
        var selected = Environment.GetEnvironmentVariable(CaseRootInput);
        try
        {
            var root = selected ?? Environment.GetEnvironmentVariable("AICF_TEST_WORK") ?? Path.GetTempPath();
            if (selected is not null && (!Path.IsPathFullyQualified(selected) || !Directory.Exists(selected)))
                return new(null, $"Supply an existing absolute scratch directory with {CaseRootInput}.");

            root = Directory.CreateDirectory(root).FullName;
            var name = $"format-case-probe-{Guid.NewGuid():N}";
            var sentinel = Path.Combine(root, name);
            var ownsSentinel = false;
            try
            {
                using (File.Open(sentinel, FileMode.CreateNew)) ownsSentinel = true;
                if (!File.Exists(Path.Combine(root, name.ToUpperInvariant())))
                    return new(root);
                return selected is null ? new(null) : new(null, $"{CaseRootInput} must distinguish case aliases.");
            }
            finally
            {
                if (ownsSentinel) File.Delete(sentinel);
            }
        }
        catch (Exception exception)
        {
            return new(null, $"Cannot probe the formatter scratch volume: {exception.Message}");
        }
    }
}
