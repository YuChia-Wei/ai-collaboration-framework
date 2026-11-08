# .NET generation tests

Run the native generation and SnippetTool tests with the .NET 10 SDK. Run each
project directly or use
[`AICF.Dotnet.Tools.slnx`](../../src/tools/dotnet/AICF.Dotnet.Tools.slnx).

| Former `Generation.Tests` cases | Project |
| --- | --- |
| SnippetTool placeholder, parameter and text expansion rules | `snippet-tool/unit/SnippetTool.UnitTests.csproj` |
| `SnippetTests`, including the executable cases, and `GeneratedFragmentTests` | `snippet-tool/SnippetTool.IntegrationTests.csproj` |
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

Set `AICF_GENERATION_SDK_TESTS=1` to exercise the real template engine,
generated builds and HTTP behavior. The template
case uses an isolated `dotnet new` hive. Select an absolute
`AICF_TEMPLATE_PACKAGE` path to exercise package installation and extracted
template content. This package selection enables the template case by itself.
An explicitly supplied package must exist.

Set `AICF_SNIPPET_ARTIFACT` to the absolute path of a separately published
SnippetTool executable for the artifact-relative catalog and process contract.
The FIFO case requires Linux and `mkfifo`. Set `AICF_TEST_WORK` to select a
disposable fixture root. Each case creates and removes its own subdirectory.

The PR native-tools workflow runs the three generation projects on Windows,
with the published executable and template package. Its Linux job runs the
FIFO case. CI requires the selected test counts in the native test reports.
The [domain contract test templates](../../src/knowledge/dotnet-backend/templates/domain-contracts/README.md)
generate illustrative projects separately. The knowledge template workflow
generates and tests the package-free example.
