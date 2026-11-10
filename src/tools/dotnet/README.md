# Framework .NET tools

Open `AICF.Dotnet.Tools.slnx` in Rider, Visual Studio or another .NET IDE for
the tools, source templates and regular tests. The .NET 10 SDK also builds it
directly:

```text
dotnet build src/tools/dotnet/AICF.Dotnet.Tools.slnx -c Release
```

These are Framework product tools. Their execution does not require an IDE or
MCP server, and their dependencies are not added to generated or refactored
applications.

| Source | Responsibility |
| --- | --- |
| `generation/Generation.Templates.csproj` | Package the seven native `dotnet new` templates from `generation/dotnet-new`. |
| `generation/snippet-tool/SnippetTool.csproj` | Render deterministic C# fragments from the bundled catalog. |
| `formatting/Format-Dotnet.ps1` | Check or apply formatting through the workspace's SDK. |
| `refactoring/RefactorTool.csproj` | Load a C# workspace, preview semantic changes and apply a reviewed plan. |

Run All in the tools solution exercises the unit and integration cases
that the host supports. SDK-backed cases discover their SDK and platform
prerequisites automatically and report specific skip reasons when unavailable.

```text
dotnet test src/tools/dotnet/AICF.Dotnet.Tools.slnx -c Release
```

The API starter projects and the package-free domain contract example can
build directly in the solution. Generated Web API projects have their own
solution. The [optional CT-005 example](../../knowledge/dotnet/testing/domain-contract-examples.md)
is visible as template content and requires verified contract assemblies and
the .NET 8 runtime.

Use the repository's [.NET formatting standard](../../../.dev/standards/DOTNET-FORMATTING.md)
for source formatting.

## Published artifact acceptance

Run the delivery test project for each prepared artifact. Supply absolute
artifact paths on supported hosts. Missing or invalid required artifact
inputs fail the selected cases.

For a full Windows x64 run, use SDK 10.0.403, the Native AOT toolchain and
PowerShell 7. From the repository root, prepare the three inputs under a fresh
disposable directory:

```powershell
$work = (New-Item -ItemType Directory -Path (Join-Path ([IO.Path]::GetTempPath()) "aicf-artifacts-$([Guid]::NewGuid().ToString('N'))")).FullName
$snippetVersion = '0.1.0-dev.1'
& src/tools/dotnet/generation/Publish-Snippets.ps1 -Version $snippetVersion -OutputRoot "$work/snippets" -RuntimeIdentifier win-x64 -NativeAot
$env:AICF_SNIPPET_ARTIFACT = "$work/snippets/SnippetTool-$snippetVersion-win-x64-aot/publish/SnippetTool.exe"

& src/tools/dotnet/refactoring/Publish-RefactorTool.ps1 -Destination "$work/refactor-publish" -Archive "$work/RefactorTool-win-x64.zip"
Expand-Archive -LiteralPath "$work/RefactorTool-win-x64.zip" -DestinationPath "$work/refactor"
$env:AICF_REFACTOR_TEST_ARTIFACT = "$work/refactor/RefactorTool.exe"

dotnet pack src/tools/dotnet/generation/Generation.Templates.csproj -c Release --artifacts-path "$work/template-build" -o "$work/templates"
if ($LASTEXITCODE -ne 0) { throw 'Template package build failed.' }
$env:AICF_TEMPLATE_PACKAGE = (Get-ChildItem -LiteralPath "$work/templates" -File -Filter '*.nupkg').FullName
dotnet test tests/dotnet-generation/snippet-tool/artifact/SnippetTool.ArtifactIntegrationTests.csproj -c Release --filter 'Boundary=PublishedArtifact' --artifacts-path "$work/artifact-tests"
dotnet test tests/dotnet-generation/templates/artifact/Generation.Templates.ArtifactIntegrationTests.csproj -c Release --artifacts-path "$work/artifact-tests"
dotnet test tests/dotnet-refactoring/artifact/RefactorTool.ArtifactIntegrationTests.csproj -c Release --artifacts-path "$work/artifact-tests"
```

For a selected artifact, run its project directly with the path shown in the
corresponding [generation](../../../tests/dotnet-generation/README.md) or
[refactoring](../../../tests/dotnet-refactoring/README.md) test guide.

The three generation guides remain canonical knowledge-package members under
`src/knowledge/dotnet/tooling/generation`. The snippet project explicitly
includes its manual from that source as `README.md` in its build/publish output;
the bundle builder likewise includes the delivery guide. Installed tools read
their own artifact files and never require the source checkout or an installed
knowledge package.

Use the [generation delivery guide](../../knowledge/dotnet/tooling/generation/DELIVERY.md),
[formatting script manual](formatting/README.md) and
[RefactorTool manual](refactoring/README.md) for their separate packaging,
installation and supported-host contracts. The relative guide link is resolved
from this source directory; generated release artifacts include their manuals.

The existing `check-*.sh`, `code-review.sh` and other legacy scripts in this
directory retain their previous status. Their presence does not register them
as current tool capabilities or add them to this solution.
