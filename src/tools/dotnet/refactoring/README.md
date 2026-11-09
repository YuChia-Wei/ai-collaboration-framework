# RefactorTool: workspace, C# Rename and Extract Interface

RefactorTool is an independent command-line application using public Roslyn
`MSBuildWorkspace`, `SymbolFinder` and `Renamer` APIs. It loads a specific project
or solution, produces a reviewable plan, and applies that plan only after
revalidating the workspace and original contents. It requires no IDE. Its NuGet
dependencies belong to the tool, never to the target application.

This implements the bounded workspace/Rename slice (#573/#574) and the selected
Extract Interface subset (#575). Namespace moves, Extract Class and generic
refactoring providers are outside it.

## Support and coverage

| Input or behavior | First-release contract |
| --- | --- |
| Host | Windows x64 and .NET 10 SDK; the acceptance fixture selects SDK 10.0.403. Other hosts have not been accepted for this tool. |
| Workspace | Explicit SDK-style C# `.csproj`, `.sln`, or `.slnx`; all active project references are loaded as source, including cross-project consumers in the selected solution. |
| Project selection | A project entry loads that project and its dependencies, not unknown reverse consumers. Select the complete solution to include consumers. |
| Target framework | Exactly one evaluated TFM per project; multi-TFM projects are refused even when `framework` is specified. An optional framework must match every loaded project. |
| Configuration | One explicit configuration (`Debug` by default), preserving MSBuild compilation options, nullable context, language version and preprocessor symbols. |
| Conditional code | Only active code in that configuration is analyzed. Files containing inactive code are listed. Other configurations are not claimed covered; review them separately before applying a shared-source rename. |
| Linked source | Explicit links in normal evaluation and files shared by projects are refused. Editable source must be inside its project directory with no symbolic/reparse path components. Read-only inputs are tracked by their supplied paths, resolved file paths and content hashes. |
| Generated source | Source-generator output and physical generated files participate in compilation. Physical source outside the project directory is admitted only under its evaluated `IntermediateOutputPath`. Source-generator output, files under evaluated `IntermediateOutputPath` or `OutDir`, project-relative `obj` and `bin`, `.g.cs` and `.generated.cs` suffixes, and early `auto-generated` markers identify uneditable source. A rename requiring an edit in those files is refused. |
| Other languages | Non-C# projects and incomplete loads are refused. Razor, XAML, reflection strings, binary consumers, serialization and database contracts are not tracked. |
| Restore | Restore the target explicitly first. RefactorTool does not request restore or install packages into the target. MSBuild design-time loading may create/update SDK intermediates under `obj`; preview does not edit authored source. |
| Execution boundary | Use trusted projects. Evaluating MSBuild imports/targets and loading analyzer assemblies executes target-provided build tooling. |
| Supported symbols | Editable source classes/interfaces, ordinary methods, properties, fields, parameters and local variables. Constructor/accessor/event/operator/type-parameter renames are not included. |
| File operations | Rename produces `modify` entries only. Extract Interface produces one `modify` and one `create`; no deleted/moved documents or project-graph changes. |

Missing metadata, workspace failures, ambiguous selections, collisions and
uneditable related symbols are refusals. A successfully loaded `Solution` alone
is not acceptance. Results report the SDK/Roslyn versions, evaluated projects,
TFMs, configuration, compiler settings, source references and coverage limits.
Normal-evaluation source items and compilation reference edges are compared
with the actual design-time workspace. Unexplained authored additions, omissions
or reference-option differences are refused. Build-only project references
(`ReferenceOutputAssembly=false`) are not compilation edges.

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

The patch shows changed lines with nearby context. The exact before/after bytes
are authoritative for encoding, BOM and newline preservation. Unchanged files
are not rewritten. A changed file whose decoded text cannot round-trip to its
exact original bytes, or whose new text cannot use that encoding, is refused.
Keep the plan until the operation has been reviewed and any
recovery need has ended; it contains copies of your source code.

## Extract Interface

Select the source class using the same file/position or project/declaration-ID
selector. Supply exact declaration IDs for every selected member, an interface
name, namespace (empty string for the global namespace), and a new `.cs` path:

```json
{
  "operation": "extract-interface",
  "workspace": "C:/work/Example/Example.slnx",
  "project": "C:/work/Example/Library/Library.csproj",
  "symbol": "T:Example.Service",
  "members": ["M:Example.Service.Get(System.Int32)", "P:Example.Service.Name"],
  "newName": "IService",
  "namespace": "Example.Contracts",
  "outputFile": "C:/work/Example/Library/IService.cs"
}
```

Use the same `preview` and `apply` commands. Omitting `operation` continues to
select `rename`. Interface options are rejected on Rename requests, and
`renameOverloads` is not applicable to extraction. The tool does not guess a
member list. It creates a public/internal interface matching the class's
accessibility and adds the fully qualified interface to that class's base list.
It preserves every byte outside that insertion, including method bodies and
consumer/DI code. New interface files use UTF-8 without BOM and explicit nullable
annotations/warnings directives matching the selected source context.

The subset uses public Roslyn `SyntaxGenerator`, syntax/semantic models and
compilation APIs, with no dependency on IDE-internal ExtractInterfaceService.
The generated interface must compile, and every generated member must resolve
to the explicitly selected original implementation with matching signature and
constraints. Existing references to introduced interface/namespace names must
retain their semantic binding, so adding a type cannot silently shadow an
imported type in consumer code. The loaded workspace must be free of compilation
errors before extraction.

| Shape | Extract Interface support |
| --- | --- |
| Class | Public/internal, top-level, single declaration, no class inheritance; existing interfaces, primary constructors and generic type parameters/constraints are supported. |
| Methods | Explicitly selected ordinary public instance methods; return/parameter type references, nullable annotations, method generic constraints and ordinary `ref`/`out` parameters are preserved. |
| Properties | Non-indexed public instance properties; only public accessors are emitted. A private setter does not become an interface setter. |
| Refused shapes | Partial/file-local/static classes, records, inherited class implementations, fields, events, indexers, static members, overrides, explicit implementations, init accessors, ref returns, optional/explicitly scoped parameters, unsafe pointer/function-pointer types and attributes on selected signatures or type parameters. |
| Nullable context | Selected declarations must share the class declaration's nullable context. |
| Source generators | Extract Interface refuses source-generator output or generator execution failures reported by the public GeneratorDriver API in either the original or proposed workspace, including previously idle generators activated by the new interface. Analyzer references requiring a newer Roslyn API than the tool are also refused, so skipped incompatible generators are not treated as idle. Its binding check covers authored documents. Rename retains the separate generator support described above. |
| New file | Existing parent directory inside the selected project, outside generated/obj/bin paths; existing files, directories and reparse paths are refused. |
| Compile inclusion | The new path must match exactly one evaluated MSBuild `Compile` glob in its project and none in other loaded projects, using case-insensitive MSBuild item types. Excludes/removes are respected. Explicit-list projects need their own supported glob configuration first; the tool does not edit `.csproj`. Custom build targets, file/item-dependent conditions or property functions, and custom conditional or expression-based Compile rules are refused. Only unconditional literal custom Compile patterns are admitted; raw XML inspection includes inactive imports. Custom imports must use literal, non-wildcard `.props`/`.targets` paths. Custom overrides of SDK import-hook properties (including indirect filename/search properties) are refused; SDK import patterns cannot include the proposed output. This covers the selected configuration with stable evaluation, not arbitrary custom build behavior or other configurations. |

The process loads MSBuild from the SDK directory selected by `dotnet --info`
for the workspace; a version inventory is not treated as SDK selection. Extraction
requires that same selected directory in every loaded project. It queries
compile inclusion there. Those tool dependencies are never added to the target
application. See the public [MSBuild glob API](https://learn.microsoft.com/en-us/dotnet/api/microsoft.build.evaluation.project.getallglobs).

## Rename policy

`renameOverloads: false` selects one method signature. Source interface
implementations, interface declarations and overrides related by Roslyn are
renamed together. `renameOverloads: true` also selects ordinary overloads declared
by the selected method's containing type, together with their Roslyn-related
members. It does not recursively add other overloads declared on implementation,
derived or base types. The summary lists discovered related declarations.
An ambiguous `nameof` overload group is refused for a single-overload rename;
explicitly review the whole-group option to change it. Even with that option,
a group containing methods outside the selected rename scope is refused. Select
the appropriate declaring method to cover its overload group; the tool never
silently expands the rename to unrelated overloads. Relations to metadata-only
declarations are refused instead of breaking the contract.

Resolvable `nameof` and XML `cref` references participate in semantic rename.
Unrelated same-name symbols are preserved. Ordinary strings/comments, filenames,
folders, project names and assembly names are unchanged. New names must be
unescaped C# identifiers. Contextual keywords may be used where the rename
resolves without conflicts. Reserved keywords and member-name collisions are
refused. Public API renames can break external consumers.

Compilation errors are compared before and after the proposed operation with
source-position mapping. Existing errors remain visible and cannot compensate
for new errors elsewhere. New errors or Roslyn conflict annotations prevent a
plan. For method renames, preview also rechecks direct calls to the renamed
methods. A call that binds to a different method, such as a hiding method on
a derived receiver, is refused with `rename_binding_changed` even if the
proposed code compiles. A refusal writes neither a plan nor authored source.
These checks do not establish general behavioral equivalence.

## Apply and recovery

```powershell
RefactorTool.exe apply --plan rename-plan.json
```

Apply checks recorded inputs and recomputes the full semantic plan, so budget
for another preview's worth of SDK and Roslyn work. Changes to source,
project/configuration inputs, referenced metadata, discovered source files or
the plan itself require a fresh preview. It opens every destination for exclusive
read/write access and checks its bytes before beginning writes. Read-only/locked
files and other predictable errors therefore refuse the operation before any
source write. On Windows, file-sharing modes on the retained handles deny
ordinary writes and deletion of captured files until the write phase ends.
That guarantee applies to the opened files. Directory membership and path
aliases can still change, and new files may appear after workspace enumeration.

Existing-file results report `applied`, `original`, `partial` or `unknown`, with their
observed hash when available. An I/O failure after writing begins reports
`partial_failure`; there is no cross-file atomicity claim. Every handle is closed
before the single response is emitted. A failed close marks the affected file
`unknown`, retains its `beforeCloseState` and `beforeCloseHash`, and includes
`closeFailures`. Keep the result and
plan, stop edits, compare every file with the stored before/after bytes, and
restore only the affected files from their `before` bytes after checking for
subsequent user changes. Inspect `partial`/`unknown` files manually. Always create
a new preview before retrying.

For extraction, all new outputs are opened with exclusive `CreateNew` before
any existing file is modified. A competing creator is never overwritten.
Opening a new file is itself a write: failure can leave a `created_empty` file,
while an output not attempted is `not_created`. A failed create reports `unknown`
because the path may belong to another writer. Successful and partial new-file
writes report `applied` and `partial`. The plan's `create` entry has an empty
`before` field to represent absence, not an empty original file. Recovery must
inspect identity and subsequent edits before removing a created file; never
restore a create entry as an empty file or delete a conflicting writer's file.

Process termination, hardware failure and writers
that bypass OS sharing rules remain outside the observed-result guarantee; the
preserved plan is the recovery source in those cases.

Exit codes: `0` successful inspect/preview/apply; `2` refused or failed before
normal completion; `3` observed partial apply. Stdout is one JSON result except
for `--help` and `--version`. Missing or malformed request and plan JSON files,
including unknown or duplicate fields, return `refused` with code `invalid_input`.

## Build, distribute and install

Download the versioned Windows x64 `RefactorTool-<version>-win-x64.exe`, its
SHA-256 file and the companion notices ZIP from the Framework release. Check
the executable with `Get-FileHash -Algorithm SHA256` before running it. The
single executable uses the installed .NET 10 runtime and workspace-selected
.NET 10 SDK. It extracts Roslyn dependencies and BuildHost to the .NET bundle
cache at launch. The SDK remains required for workspace evaluation.

Maintainers build the standalone artifact from this source directory:

```powershell
./Publish-RefactorTool.ps1 -Destination C:/staging/refactor-win-x64 -Version 0.1.0-dev.1
```

The destination must be new. The script verifies the single-file layout and
stages the dependency licenses and notices. An optional `-Archive` path creates
a local ZIP and prints its SHA-256.

Successful pull request acceptance runs retain the Windows x64 executable,
checksum and notices for 14 days.

Run the downloaded executable from a user-selected location. To update, put
the new versioned executable beside the previous one, verify its checksum, and
switch your command or PATH entry to it. Keep the previous version for rollback.

See `THIRD-PARTY-NOTICES.txt` and `licenses/` in the notices ZIP. Public API
reference: [Roslyn Renamer](https://learn.microsoft.com/en-us/dotnet/api/microsoft.codeanalysis.rename.renamer.renamesymbolasync?view=roslyn-dotnet-5.0.0).
