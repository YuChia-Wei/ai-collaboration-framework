# Framework .NET tools

Open `AICF.Dotnet.Tools.slnx` in Rider, Visual Studio or another .NET IDE.
The .NET 10 SDK also builds it directly:

```text
dotnet build src/tools/dotnet/AICF.Dotnet.Tools.slnx -c Release
```

These are Framework product tools. Their execution does not require an IDE or
MCP server, and their dependencies are not added to generated or refactored
applications.

| Source | Responsibility |
| --- | --- |
| `generation/Generation.Templates.csproj` | Package the native `dotnet new` project and item templates. |
| `generation/snippet-tool/SnippetTool.csproj` | Render deterministic C# fragments from the bundled catalog. |
| `formatting/FormatTool.csproj` | Run bounded SDK formatting and cleanup operations. |
| `refactoring/RefactorTool.csproj` | Load a C# workspace, preview semantic changes and apply a reviewed plan. |

Run All in the tools solution exercises the unit and integration cases
that the host supports. SDK-backed cases discover their SDK and platform
prerequisites automatically and report specific skip reasons when unavailable.

```text
dotnet test src/tools/dotnet/AICF.Dotnet.Tools.slnx -c Release
```

The Web API template keeps its own solution. The
[domain contract test templates](../../knowledge/dotnet-backend/templates/domain-contracts/README.md)
generate illustrative projects in a separate directory.

## Published artifact acceptance

Open [AICF.Dotnet.Artifacts.slnx](AICF.Dotnet.Artifacts.slnx) for acceptance
against prepared artifacts. Supply absolute artifact paths on supported
hosts. Missing or invalid required artifact inputs fail the selected cases.
The normal tools solution uses its build outputs and source templates.

For a full Windows x64 run, use SDK 10.0.403, the Native AOT toolchain and
PowerShell 7. From the repository root, prepare the four inputs under a fresh
disposable directory:

```powershell
$work = (New-Item -ItemType Directory -Path (Join-Path ([IO.Path]::GetTempPath()) "aicf-artifacts-$([Guid]::NewGuid().ToString('N'))")).FullName
dotnet publish src/tools/dotnet/formatting/FormatTool.csproj -c Release -r win-x64 --self-contained true -p:PublishAot=true -p:PublishSingleFile=false -p:CopyOutputSymbolsToPublishDirectory=false --artifacts-path "$work/format-build" -o "$work/format"
if ($LASTEXITCODE -ne 0) { throw 'FormatTool publish failed.' }
$env:AICF_FORMAT_ARTIFACT = "$work/format/FormatTool.exe"

$snippetVersion = '0.1.0-dev.1'
& src/tools/dotnet/generation/Publish-Snippets.ps1 -Version $snippetVersion -OutputRoot "$work/snippets" -RuntimeIdentifier win-x64 -NativeAot
$env:AICF_SNIPPET_ARTIFACT = "$work/snippets/SnippetTool-$snippetVersion-win-x64-aot/publish/SnippetTool.exe"

& src/tools/dotnet/refactoring/Publish-RefactorTool.ps1 -Destination "$work/refactor-publish" -Archive "$work/RefactorTool-win-x64.zip"
Expand-Archive -LiteralPath "$work/RefactorTool-win-x64.zip" -DestinationPath "$work/refactor"
$env:AICF_REFACTOR_TEST_ARTIFACT = "$work/refactor/RefactorTool.exe"

dotnet pack src/tools/dotnet/generation/Generation.Templates.csproj -c Release --artifacts-path "$work/template-build" -o "$work/templates"
if ($LASTEXITCODE -ne 0) { throw 'Template package build failed.' }
$env:AICF_TEMPLATE_PACKAGE = (Get-ChildItem -LiteralPath "$work/templates" -File -Filter '*.nupkg').FullName
dotnet test src/tools/dotnet/AICF.Dotnet.Artifacts.slnx -c Release --artifacts-path "$work/artifact-tests"
```

For a selected artifact, run its project directly with the path shown in the
corresponding [formatter](../../../tests/dotnet-formatting/README.md),
[generation](../../../tests/dotnet-generation/README.md) or
[refactoring](../../../tests/dotnet-refactoring/README.md) test guide.

The three generation guides remain canonical knowledge-package members under
`src/knowledge/dotnet-backend/tooling/generation`. The snippet project explicitly
includes its manual from that source as `README.md` in its build/publish output;
the bundle builder likewise includes the delivery guide. Installed tools read
their own artifact files and never require the source checkout or an installed
knowledge package.

Use the [generation delivery guide](../../knowledge/dotnet-backend/tooling/generation/DELIVERY.md),
[FormatTool manual](formatting/README.md) and
[RefactorTool manual](refactoring/README.md) for their separate packaging,
installation and supported-host contracts. The relative guide link is resolved
from this source directory; generated release artifacts include their manuals.

The existing `check-*.sh`, `code-review.sh` and other legacy scripts in this
directory retain their previous status. Their presence does not register them
as current tool capabilities or add them to this solution.
