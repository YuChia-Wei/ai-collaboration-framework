# .NET generation tests

Run the package-free contract cases and in-process SnippetTool tests with the
.NET 10 SDK. Run each project directly or use
[`AICF.Dotnet.Tools.slnx`](../../src/tools/dotnet/AICF.Dotnet.Tools.slnx).

| Former `Generation.Tests` cases | Project |
| --- | --- |
| `PackageFreeContractTests` and reconstruction fixtures | `domain-contract/DomainContract.UnitTests.csproj` |
| `SnippetTests`, including the executable cases, and `GeneratedFragmentTests` | `snippet-tool/SnippetTool.IntegrationTests.csproj` |
| `TemplateTests` and the copied `dotnet new` fixtures | `templates/Generation.Templates.IntegrationTests.csproj` |

SnippetTool cases exercise the real catalog, request and filesystem boundary
even when they call the tool in process. The interface method and string guard
rendering contracts have independent cases. Template tests depend on the real
SDK and source template content. The two integration projects link the
disposable fixture helper as source and have independent test assemblies.

```text
dotnet test tests/dotnet-generation/domain-contract/DomainContract.UnitTests.csproj
dotnet test tests/dotnet-generation/snippet-tool/SnippetTool.IntegrationTests.csproj
dotnet test tests/dotnet-generation/templates/Generation.Templates.IntegrationTests.csproj
```

Set `AICF_GENERATION_SDK_TESTS=1` to compile the rendered snippets and exercise
the real template engine, generated builds and HTTP behavior. The template
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
The [published CT-005 cases](domain-contract/README.md) run in their own
opt-in integration project with the verified DLLs supplied explicitly.
