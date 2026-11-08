# SnippetTool tests

The ordinary [tools solution](../../../src/tools/dotnet/AICF.Dotnet.Tools.slnx)
includes both source test projects. Run either project with the .NET 10 SDK.

| Project | Coverage |
| --- | --- |
| [Unit](unit/SnippetTool.UnitTests.csproj) | Placeholder syntax, parameter validation, and exact expansion text. |
| [Source integration](SnippetTool.IntegrationTests.csproj) | Requests, catalog and body files, JSON results, and a compiled Roslyn consumer of the rendered C# fragments. The FIFO case runs the ordinary build in a bounded child process on Linux x64. |
| [Artifact integration](artifact/SnippetTool.ArtifactIntegrationTests.csproj) | Starts the staged Native AOT executable from another directory and reads the shipped adjacent catalog. |

The FIFO case runs automatically on Linux x64 with `mkfifo` on PATH. The case
reports a skip on other platforms or when `mkfifo` is absent. A probe fault
or a failed child process fails the case. Set `AICF_TEST_WORK` to choose the
parent directory for disposable fixtures.

For artifact verification, supply `AICF_SNIPPET_ARTIFACT` as the absolute path
to the prepared executable. See the [artifact preparation commands](../../../src/tools/dotnet/README.md#published-artifact-acceptance).
Run the artifact project directly. A missing or invalid staged executable fails
the test on a supported host.
