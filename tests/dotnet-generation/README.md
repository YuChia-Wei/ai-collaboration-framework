# .NET generation tests

Run the native generation and SnippetTool tests with the .NET 10 SDK. Run each
project directly or use
[`AICF.Dotnet.Tools.slnx`](../../src/tools/dotnet/AICF.Dotnet.Tools.slnx).

| Source test cases | Project |
| --- | --- |
| SnippetTool placeholder, parameter and text expansion rules | `snippet-tool/unit/SnippetTool.UnitTests.csproj` |
| `SnippetTests` and `GeneratedFragmentTests` | `snippet-tool/SnippetTool.IntegrationTests.csproj` |
| `TemplateTests` and the copied `dotnet new` fixtures | `templates/Generation.Templates.IntegrationTests.csproj` |

SnippetTool unit tests pass text and parameter definitions directly to the
product expansion methods. Integration cases exercise the real catalog,
request and filesystem, including the bundled interface method and string
guard. One invalid parameter kind verifies that catalog loading applies the
definition validator before listing. The generated fragment case compiles the actual rendered source against
.NET 10 reference assemblies with Roslyn and executes it in the test process.
Template tests exercise the installed SDK command, the generated project builds
and both HTTP applications. The two integration projects link the disposable
fixture helper as source and have independent test assemblies.

```text
dotnet test tests/dotnet-generation/snippet-tool/unit/SnippetTool.UnitTests.csproj
dotnet test tests/dotnet-generation/snippet-tool/SnippetTool.IntegrationTests.csproj
dotnet test tests/dotnet-generation/templates/Generation.Templates.IntegrationTests.csproj
```

The source-template case runs automatically when a .NET 10 SDK and an
ASP.NET Core 10.0 runtime are discoverable. It uses an isolated `dotnet new`
hive to exercise generation, builds and HTTP behavior.

Use the [artifact preparation commands](../../src/tools/dotnet/README.md#published-artifact-acceptance)
to supply `AICF_TEMPLATE_PACKAGE` as the absolute path of a packed template
`.nupkg` and `AICF_SNIPPET_ARTIFACT` as the absolute path of the published
SnippetTool executable.

```text
dotnet test tests/dotnet-generation/snippet-tool/artifact/SnippetTool.ArtifactIntegrationTests.csproj -c Release
dotnet test tests/dotnet-generation/templates/artifact/Generation.Templates.ArtifactIntegrationTests.csproj -c Release
```

The FIFO case requires Linux x64 and `mkfifo` on PATH. Set `AICF_TEST_WORK` to
select a disposable fixture root. Each case creates and removes its own
subdirectory. The PR native-tools workflow runs the source generation projects
and both artifact projects on Windows. Its Linux job runs the
FIFO case. CI requires the selected test counts in the native test reports.
The [domain contract test templates](../../src/knowledge/dotnet-backend/templates/domain-contracts/README.md)
generate illustrative projects separately. The knowledge template workflow
generates and tests the package-free example.
