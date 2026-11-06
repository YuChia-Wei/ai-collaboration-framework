# RefactorTool: workspace and C# Rename

RefactorTool is an independent command-line application using public Roslyn
`MSBuildWorkspace`, `SymbolFinder` and `Renamer` APIs. It loads a specific project
or solution, produces a reviewable plan, and applies that plan only after
revalidating the workspace and original contents. It requires no IDE. Its NuGet
dependencies belong to the tool, never to the target application.

This is the bounded first implementation for #573 and #574. Extract Interface,
namespace moves, Extract Class and generic refactoring providers are outside it.

## Support and coverage

| Input or behavior | First-release contract |
| --- | --- |
| Host | Windows x64 and .NET 10 SDK; the acceptance fixture selects SDK 10.0.403. Other hosts have not been accepted for this tool. |
| Workspace | Explicit SDK-style C# `.csproj`, `.sln`, or `.slnx`; all active project references are loaded as source, including cross-project consumers in the selected solution. |
| Project selection | A project entry loads that project and its dependencies, not unknown reverse consumers. Select the complete solution to include consumers. |
| Target framework | Exactly one evaluated TFM per project; multi-TFM projects are refused even when `framework` is specified. An optional framework must match every loaded project. |
| Configuration | One explicit configuration (`Debug` by default), preserving MSBuild compilation options, nullable context, language version and preprocessor symbols. |
| Conditional code | Only active code in that configuration is analyzed. Files containing inactive code are listed. Other configurations are not claimed covered; review them separately before applying a shared-source rename. |
| Linked source | Explicit links, source outside a project's directory, files shared by projects, and symbolic/reparse paths are refused. |
| Generated source | Source-generator output is refused. SDK-generated `obj` inputs may participate in compilation but cannot be renamed. `.g.cs`, `.generated.cs`, and an early `auto-generated` marker make declarations/references uneditable. |
| Other languages | Non-C# projects and incomplete loads are refused. Razor, XAML, reflection strings, binary consumers, serialization and database contracts are not tracked. |
| Restore | Restore the target explicitly first. RefactorTool does not request restore or install packages into the target. MSBuild design-time loading may create/update SDK intermediates under `obj`; preview does not edit authored source. |
| Execution boundary | Use trusted projects. Evaluating MSBuild imports/targets and loading analyzer assemblies executes target-provided build tooling. |
| Supported symbols | Editable source classes/interfaces, ordinary methods, properties, fields, parameters and local variables. Constructor/accessor/event/operator/type-parameter renames are not included. |
| File operations | Rename produces `modify` entries only. Added/deleted/moved documents or project-graph changes are refused, never omitted from a successful plan. |

Missing metadata, workspace failures, ambiguous selections, collisions and
uneditable related symbols are refusals. A successfully loaded `Solution` alone
is not acceptance. Results report the SDK/Roslyn versions, evaluated projects,
TFMs, configuration, compiler settings, source references and coverage limits.

## Select and preview

Create a request using absolute paths. A declaration ID includes its signature,
so overload selection is explicit:

```json
{
  "workspace": "C:/work/Example/Example.slnx",
  "configuration": "Debug",
  "project": "C:/work/Example/Library/Library.csproj",
  "symbol": "M:Example.Service.Get(System.Int32)",
  "newName": "Fetch",
  "renameOverloads": false
}
```

Alternatively replace `project` and `symbol` with `file`, `line` and `column`.
Line and column are 1-based; the column counts UTF-16 code units and must be
inside the identifier. File selection also supports parameters and locals,
which do not have documentation declaration IDs. Whitespace, unresolved or
ambiguous targets are refused; the tool never selects by a bare name search.

```powershell
RefactorTool.exe inspect --request request.json
RefactorTool.exe preview --request request.json --plan rename-plan.json
```

The plan path must be a new `.json` file outside every loaded project directory,
with an existing parent directory and no symbolic/reparse path components.
The reserved SDK configuration filename `global.json` is rejected. For a
single-project workspace, select a plan directory outside that project's root.
These restrictions keep preview output from becoming a source/configuration
input. Stdout contains a concise JSON summary; the plan
contains evaluated scope, related symbol IDs, every changed file, exact original
and proposed bytes (base64), input hashes, compilation diagnostics and the entire
unified patch. To read the patch in PowerShell:

```powershell
(Get-Content rename-plan.json -Raw | ConvertFrom-Json).patch
```

The patch is a complete-file review projection; the exact before/after bytes
are authoritative for encoding, BOM and newline preservation. Unchanged files
are not rewritten. Keep the plan until the operation has been reviewed and any
recovery need has ended; it contains copies of your source code.

## Rename policy

`renameOverloads: false` selects one method signature. Source interface
implementations, interface declarations and overrides related by Roslyn are
renamed together. `renameOverloads: true` also renames the ordinary overloads.
The summary lists discovered related declarations. An ambiguous `nameof`
overload group is refused for a single-overload rename; explicitly review the
whole-group option to change it. Relations to metadata-only declarations are
refused instead of breaking the contract.

Resolvable `nameof` and XML `cref` references participate in semantic rename.
Unrelated same-name symbols are preserved. Ordinary strings/comments, filenames,
folders, project names and assembly names are unchanged. New names must be
unescaped C# identifiers; keywords and existing member-name collisions are
conservatively refused. Public API renames can break external consumers.

Compilation errors are compared before and after the proposed operation with
source-position mapping. Existing errors remain visible and cannot compensate
for new errors elsewhere. New errors or Roslyn conflict annotations prevent a
plan. This check is separate from scenario tests: neither a clean compilation
nor a returned Roslyn solution proves behavioral equivalence.

## Apply and recovery

```powershell
RefactorTool.exe apply --plan rename-plan.json
```

Apply checks recorded inputs and recomputes the semantic plan. Changes to source,
project/configuration inputs, referenced metadata, discovered source files or
the plan itself require a fresh preview. It opens every destination for exclusive
read/write access and checks its bytes before beginning writes. Read-only/locked
files and other predictable errors therefore refuse the operation before any
source write.

Each file result reports `applied`, `original`, `partial` or `unknown`, with its
observed hash when available. An I/O failure after writing begins reports
`partial_failure`; there is no cross-file atomicity claim. Keep the result and
plan, stop edits, compare every file with the stored before/after bytes, and
restore only the affected files from their `before` bytes after checking for
subsequent user changes. Inspect `partial`/`unknown` files manually. Always create
a new preview before retrying. Process termination, hardware failure and writers
that bypass OS sharing rules remain outside the observed-result guarantee; the
preserved plan is the recovery source in those cases.

Exit codes: `0` successful inspect/preview/apply; `2` refused or failed before
normal completion; `3` observed partial apply. Stdout is one JSON result except
for `--help` and `--version`.

## Build, distribute and install

This tool uses managed .NET and out-of-process Roslyn MSBuild build hosts.
Native AOT, trimming and single-file publishing are disabled; do not copy only
the executable. A published directory must retain its dependency assemblies,
`BuildHost-netcore`, notices and runtime files. The .NET SDK is still required
on the target machine for workspace evaluation.

Maintainers build the standalone artifact from this source directory:

```powershell
./Publish-RefactorTool.ps1 -Destination C:/staging/refactor-win-x64 -Archive C:/staging/RefactorTool-win-x64.zip
```

The script keeps dependency metadata and notices, checks required build-host
files, and emits the archive SHA-256. Both destination paths must be new; failed
staging remains available for diagnosis. This artifact is installed separately
from the existing generation/formatting bundle and does not change that bundle's
installer or Native AOT policy.

Install a prepared standalone archive by extracting its entire directory to a
user-selected location and invoking `RefactorTool.exe` there, or adding that
directory to PATH yourself. No target `.csproj` change, IDE extension, source
checkout, global tool installation or machine-wide registration is required to
run the prepared artifact. Updating means extracting a new complete directory;
keep the previous one to roll back. Do not overlay a newer executable onto older
dependencies. This source implementation does not allocate a Framework release
version or publish a downloadable release.

See `THIRD-PARTY-NOTICES.txt` and `licenses/` in the archive. Public API
reference: [Roslyn Renamer](https://learn.microsoft.com/en-us/dotnet/api/microsoft.codeanalysis.rename.renamer.renamesymbolasync?view=roslyn-dotnet-5.0.0).
