using System.Text.Json;
using Aicf.Dotnet.TestSupport;
using Generation.TestSupport;

namespace Generation.Templates.IntegrationTests;

internal sealed class TemplateRegistration : IDisposable
{
    private static readonly string[] ShortNames =
    [
        "aicf-class", "aicf-ct005-contract-tests", "aicf-domain-contract-tests",
        "aicf-interface", "aicf-miniapi", "aicf-usecase", "aicf-webapi"
    ];

    internal GenerationFixture Fixture { get; } = new();

    internal TemplateRegistration()
    {
        try
        {
            var sdk = DotnetTestHost.RequireTemplateSdk();
            Fixture.DotnetExecutable = DotnetTestHost.RequireExecutable();
            Fixture.Write("global.json", JsonSerializer.Serialize(new
            {
                sdk = new { version = sdk.Version, rollForward = "disable", paths = new[] { sdk.Root } }
            }));
        }
        catch
        {
            Fixture.Dispose();
            throw;
        }
    }

    internal Task<string> Install(string source) => New("install", source);

    internal async Task AssertShortNames()
    {
        var list = await New("list", "aicf");
        var actual = list.Split((char[]?)null, StringSplitOptions.RemoveEmptyEntries)
            .Where(word => word.StartsWith("aicf-", StringComparison.Ordinal))
            .Order(StringComparer.Ordinal);
        Assert.Equal(ShortNames, actual);
    }

    internal Task<string> Generate(string shortName, string name, string output, params string[] options) =>
        New([shortName, "--name", name, "--output", output, .. options]);

    private Task<string> New(params string[] arguments) =>
        Fixture.Dotnet(["new", .. arguments, "--debug:custom-hive", Path.Combine(Fixture.Root, "hive")]);

    public void Dispose() => Fixture.Dispose();
}
