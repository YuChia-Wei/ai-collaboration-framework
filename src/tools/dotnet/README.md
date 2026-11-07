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

The solution includes the source repository's xUnit test projects for
formatting, generation and refactoring. Run the projects with `dotnet test`
and use their test READMEs to select SDK and artifact cases. The Web API
template keeps its own solution. The CT-005 tests requiring separately supplied
published DLLs have an explicit test project outside this solution.

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
