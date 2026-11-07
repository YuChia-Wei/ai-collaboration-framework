# .NET generation tests

Run the SnippetTool and package-free contract cases with the .NET 10 SDK.

```text
dotnet test tests/dotnet-generation/Generation.Tests.csproj
```

Set `AICF_GENERATION_SDK_TESTS=1` to also compile the rendered fragments and
exercise the real template engine, generated project builds, and HTTP
behavior of the two API templates. The template cases use an isolated
`dotnet new` hive. Set `AICF_TEMPLATE_PACKAGE` to an absolute path to a
separately built template package to exercise its installation and the
extracted template content. An explicitly selected package must exist.

Set `AICF_SNIPPET_ARTIFACT` to the absolute path of a separately published
SnippetTool executable to exercise artifact-relative catalog resolution and
the public process contract. The FIFO case also requires Linux. Set
`AICF_TEST_WORK` to a directory for disposable fixtures when needed. Each
case creates and removes its own subdirectory.

The pull request native-tools workflow runs generation cases once on Windows
with the published executable and a template package. Its Linux job selects
only the FIFO case. The existing three-runtime artifact build stays in place,
and the generation test steps apply only to pull requests.

The [published CT-005 cases](domain-contract/README.md) run through their
separate test project with the verified DLLs supplied explicitly.
