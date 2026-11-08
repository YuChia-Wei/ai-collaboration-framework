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
    /// <summary>Rejects raw MSBuild rules whose evaluation or build can change when the source appears.</summary>
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

    internal static class MsBuildParser
    {
        private static readonly string BuildSdkPath = typeof(CompilePolicyTests).Assembly
            .GetCustomAttributes<AssemblyMetadataAttribute>()
            .Single(attribute => attribute.Key == "RefactorTestSdkPath").Value!;

        private static readonly Lazy<bool> Registration = new(() =>
        {
            MSBuildLocator.RegisterMSBuildPath(BuildSdkPath);
            return true;
        });

        internal static void EnsureRegistered() => _ = Registration.Value;

        internal static bool CanEvaluate(string selectedSdkPath)
        {
            if (!SamePath(BuildSdkPath, selectedSdkPath))
                return false;

            var sdksPath = Environment.GetEnvironmentVariable("MSBuildSDKsPath");
            if (!string.IsNullOrEmpty(sdksPath) && !SamePath(sdksPath, Path.Combine(selectedSdkPath, "Sdks")))
                return false;

            EnsureRegistered();
            return UsesMsBuild(selectedSdkPath);
        }

        private static bool SamePath(string left, string right) =>
            Path.IsPathFullyQualified(left) && Path.IsPathFullyQualified(right) &&
            Paths.Comparer.Equals(Path.TrimEndingDirectorySeparator(Path.GetFullPath(left)),
                Path.TrimEndingDirectorySeparator(Path.GetFullPath(right)));

        [MethodImpl(MethodImplOptions.NoInlining)]
        private static bool UsesMsBuild(string sdkPath) =>
            SamePath(typeof(ProjectRootElement).Assembly.Location, Path.Combine(sdkPath, "Microsoft.Build.dll"));

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
