using Aicf.Dotnet.TestSupport;

namespace Generation.Templates.IntegrationTests;

internal sealed class TemplateSdkFactAttribute : FactAttribute
{
    public TemplateSdkFactAttribute() => Skip = DotnetTestHost.TemplateSkip;
}
