using Generation.TestSupport;

namespace Generation.Templates.IntegrationTests;

internal sealed class TemplateSdkFactAttribute : FactAttribute
{
    internal static string? Package => Environment.GetEnvironmentVariable("AICF_TEMPLATE_PACKAGE");

    public TemplateSdkFactAttribute()
    {
        if (!GenerationFixture.RunSdkTests && Package is null)
            Skip = "Set AICF_GENERATION_SDK_TESTS=1 for real SDK/template integration.";
    }
}
