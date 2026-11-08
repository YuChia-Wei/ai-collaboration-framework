using System.Text;
using System.Text.Json;

namespace RefactorTool.IntegrationTests;

[Trait("Boundary", "InProcess")]
public sealed class EngineBoundaryTests
{
    [WindowsFact]
    public void ConfigurationCannotInjectAnMsbuildProperty()
    {
        using var directory = new TestDirectory();
        const string projectXml = """<Project Sdk="Microsoft.NET.Sdk" />""";
        Request request = null!;
        Exception? error = null;

        this.Given(GivenARegularProjectAndAnInjectedConfiguration, "a regular project and an injected configuration")
            .When(WhenLoadingTheWorkspace, "loading the workspace")
            .Then(ThenRefuseTheConfigurationWithoutChangingTheProject, "refuse the configuration without changing the project")
            .BDDfy();

        void GivenARegularProjectAndAnInjectedConfiguration() =>
            request = new Request { Workspace = directory.Write("A.csproj", projectXml), Configuration = "Debug,DefineConstants=OTHER" };

        async Task WhenLoadingTheWorkspace() =>
            error = await Record.ExceptionAsync(async () => { using var loaded = await WorkspaceLoader.Load(request); });

        void ThenRefuseTheConfigurationWithoutChangingTheProject()
        {
            Assert.Equal("invalid_configuration", Assert.IsType<RefactorFailure>(error).Code);
            Assert.Equal(projectXml, File.ReadAllText(request.Workspace));
        }
    }

    [Fact]
    public void MalformedSourceEncodingIsRefusedWithoutWrites()
    {
        using var workspace = new SemanticWorkspace();
        byte[] original = [0xef, 0xbb, 0xbf, .. Encoding.UTF8.GetBytes(SemanticWorkspace.Service), .. "\n// malformed "u8, 0xff, 0x0a];
        Exception? error = null;

        this.Given(GivenMalformedSourceBytes, "malformed UTF-8 source bytes")
            .When(WhenPlanningRename, "planning rename")
            .Then(ThenRefuseLossyEncodingAndPreserveSourceBytes, "refuse lossy encoding and preserve the original source bytes")
            .BDDfy();

        void GivenMalformedSourceBytes() => workspace.Add("A/Service.cs", original);

        async Task WhenPlanningRename() => error = await Record.ExceptionAsync(() => workspace.PlanRename(workspace.Rename));

        void ThenRefuseLossyEncodingAndPreserveSourceBytes()
        {
            Assert.Equal("lossy_encoding", Assert.IsType<RefactorFailure>(error).Code);
            Assert.Equal(original, File.ReadAllBytes(workspace.Source));
        }
    }

    [Theory]
    [InlineData("emit-after")]
    [InlineData("throw-after")]
    [InlineData("throw-before")]
    public void ExtractionRefusesCompatibleGeneratorOutputOrFailure(string scenario)
    {
        using var workspace = new SemanticWorkspace();
        byte[] original = Encoding.UTF8.GetBytes(SemanticWorkspace.Service);
        var request = InterfacePlanner.Normalize(workspace.Extract);
        InterfacePlanner.ExtractionTarget? target = null;
        Exception? error = null;

        this.Given(GivenACompatibleGeneratorWithTheSelectedTrigger, "a compatible generator with the selected trigger")
            .When(WhenPlanningExtractionWithTheGenerator, "planning extraction with the generator")
            .Then(ThenRefuseTheGeneratedOutputOrFailureWithoutWrites, "refuse generated output or failure without writes")
            .BDDfy();

        async Task GivenACompatibleGeneratorWithTheSelectedTrigger()
        {
            workspace.Add("A/Service.cs", original);
            workspace.AddGenerator(GeneratorSource(scenario));
            if (scenario != "throw-before")
                target = await InterfacePlanner.SelectTarget(request, workspace.Loaded);
        }

        async Task WhenPlanningExtractionWithTheGenerator()
        {
            error = target is null
                ? await Record.ExceptionAsync(() => InterfacePlanner.SelectTarget(request, workspace.Loaded))
                : await Record.ExceptionAsync(() => InterfacePlanner.BuildPlan(request, workspace.Loaded, target));
        }

        void ThenRefuseTheGeneratedOutputOrFailureWithoutWrites()
        {
            var refusal = Assert.IsType<RefactorFailure>(error);
            Assert.Equal("unsupported_generated_source", refusal.Code);
            if (scenario == "emit-after")
                Assert.Contains("generated consumer documents", refusal.Message);
            else
            {
                var diagnostics = JsonSerializer.SerializeToElement(refusal.Detail);
                Assert.Contains(diagnostics.EnumerateArray(), item =>
                    item.GetProperty("Id").GetString() == "CS8785" &&
                    item.GetProperty("Message").GetString()!.Contains("conditional generator failure", StringComparison.Ordinal));
            }
            Assert.Equal(original, File.ReadAllBytes(workspace.Source));
            Assert.False(File.Exists(workspace.Output));
        }
    }

    internal static string GeneratorSource(string scenario)
    {
        var condition = scenario == "throw-before" ? "true" : """context.Compilation.GetTypeByMetadataName("Contracts.ISelected") != null""";
        var body = scenario.StartsWith("throw-", StringComparison.Ordinal)
            ? """throw new System.InvalidOperationException("conditional generator failure");"""
            : """context.AddSource("Activated.cs", "namespace Generated { internal class Activated {} }");""";
        return $$"""
            using Microsoft.CodeAnalysis;
            [Generator] public class ConditionalGenerator : ISourceGenerator
            {
                public void Initialize(GeneratorInitializationContext context) {}
                public void Execute(GeneratorExecutionContext context)
                {
                    if ({{condition}}) { {{body}} }
                }
            }
            """;
    }
}
