namespace Generation.Templates.IntegrationTests;

public sealed class TemplateTests
{
    [TemplateSdkFact]
    [Trait("Boundary", "Sdk")]
    public void NativeTemplatesGenerateBuildAndServeBothApiShapesAndPreserveEdits() =>
        new TemplateScenario().Run(package: null);
}
