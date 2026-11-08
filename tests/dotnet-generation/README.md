# .NET generation tests

Run the native generation and SnippetTool tests with the .NET 10 SDK. Run each
project directly or use
[`AICF.Dotnet.Tools.slnx`](../../src/tools/dotnet/AICF.Dotnet.Tools.slnx).

| Source test cases | Project |
| --- | --- |
| SnippetTool placeholder, parameter and text expansion rules | `snippet-tool/unit/SnippetTool.UnitTests.csproj` |
| Catalog, requests, filesystem and generated fragments | [Snippet test projects](snippet-tool/README.md) |
| SDK template discovery, generation and use | [Template test project](templates/README.md) |

SnippetTool unit tests pass text and parameter definitions directly to the
product expansion methods. Integration cases exercise the real catalog,
request and filesystem, including the bundled interface method and string
guard. One invalid parameter kind verifies that catalog loading applies the
definition validator before listing. The generated fragment case compiles the actual rendered source against
.NET 10 reference assemblies with Roslyn and executes it in the test process.

```text
dotnet test tests/dotnet-generation/snippet-tool/unit/SnippetTool.UnitTests.csproj
dotnet test tests/dotnet-generation/snippet-tool/SnippetTool.IntegrationTests.csproj
dotnet test tests/dotnet-generation/templates/Generation.Templates.IntegrationTests.csproj
```

Use the [artifact preparation commands](../../src/tools/dotnet/README.md#published-artifact-acceptance)
to supply `AICF_TEMPLATE_PACKAGE` as the absolute path of a packed template
`.nupkg` and `AICF_SNIPPET_ARTIFACT` as the absolute path of the published
SnippetTool executable.

```text
dotnet test tests/dotnet-generation/snippet-tool/artifact/SnippetTool.ArtifactIntegrationTests.csproj -c Release
dotnet test tests/dotnet-generation/templates/artifact/Generation.Templates.ArtifactIntegrationTests.csproj -c Release
```

The source FIFO case requires Linux x64 and `mkfifo` on PATH. Set `AICF_TEST_WORK` to
select a disposable fixture root. Each case creates and removes its own
subdirectory. The PR native-tools workflow runs source generation cases on
Windows and the FIFO case on Linux. Actual Windows and Linux native executables
are smoke-tested before upload; candidate and release builds test the template
package extracted from the delivery ZIP. CI requires the selected test counts
in native test reports.
