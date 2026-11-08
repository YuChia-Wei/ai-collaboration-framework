using System.Reflection;
using System.Runtime.CompilerServices;
using System.Xml;
using Microsoft.Build.Construction;
using Microsoft.Build.Evaluation;
using Microsoft.Build.Locator;

namespace RefactorTool.IntegrationTests;

[Trait("Boundary", "InProcess")]
public sealed class CompilePolicyTests
{
    [Theory]
    [InlineData("""<PropertyGroup Condition="Exists('ISelected.cs')"><EnableDefaultCompileItems>false</EnableDefaultCompileItems></PropertyGroup>""")]
    [InlineData("""<Import Project="ExcludeInterface.targets" Condition="Exists('ISelected.cs')" />""")]
    [InlineData("""<ItemGroup><IgnoredFiles Include="ISelected*.cs"/><Compile Remove="@(IgnoredFiles)" /></ItemGroup>""")]
    [InlineData("""<ItemGroup><Compile Remove="ISelected.cs" Condition="'@(Compile)' != ''" /></ItemGroup>""")]
    [InlineData("""<Import Project="Contracts/*" />""")]
    [InlineData("""<PropertyGroup><ImportSpec>Contracts/*</ImportSpec></PropertyGroup><Import Project="$(ImportSpec)" />""")]
    [InlineData("""<Target Name="RemoveInterface" BeforeTargets="CoreCompile"><ItemGroup><Compile Remove="ISelected.cs" /></ItemGroup></Target>""")]
    public void RejectsFileDependentCustomProjectXml(string xml)
    {
        string projectXml = null!;
        Exception? error = null;

        this.Given(GivenACustomProjectRule, "a custom project rule")
            .When(WhenValidatingTheParsedProjectXml, "validating the parsed project XML")
            .Then(ThenRefuseUnsupportedCompileInclusion, "refuse unsupported compile inclusion")
            .BDDfy();

        void GivenACustomProjectRule() => projectXml = "<Project>" + xml + "</Project>";

        void WhenValidatingTheParsedProjectXml()
        {
            MsBuildParser.EnsureRegistered();
            error = Record.Exception(() => MsBuildParser.Validate(projectXml));
        }

        void ThenRefuseUnsupportedCompileInclusion() =>
            Assert.Equal("unsupported_compile_inclusion", Assert.IsType<RefactorFailure>(error).Code);
    }

    private static class MsBuildParser
    {
        static MsBuildParser()
        {
            var path = typeof(CompilePolicyTests).Assembly.GetCustomAttributes<AssemblyMetadataAttribute>()
                .Single(attribute => attribute.Key == "RefactorTestSdkPath").Value!;
            MSBuildLocator.RegisterMSBuildPath(path);
        }

        internal static void EnsureRegistered() { }

        // Delay binding the real SDK assembly until its resolver is registered.
        [MethodImpl(MethodImplOptions.NoInlining)]
        internal static void Validate(string projectXml)
        {
            using var collection = new ProjectCollection();
            using var reader = XmlReader.Create(new StringReader(projectXml));
            var project = ProjectRootElement.Create(reader, collection);
            project.FullPath = Path.Combine(AppContext.BaseDirectory, "Probe.csproj");
            CompileInclusion.ValidateCustomProjectXml([project],
                Path.Combine(AppContext.BaseDirectory, "obj", "Probe.csproj.nuget.g.props"),
                Path.Combine(AppContext.BaseDirectory, "obj", "Probe.csproj.nuget.g.targets"),
                new HashSet<string>(StringComparer.OrdinalIgnoreCase));
        }
    }
}
