# Selected-file formatting

`FormatTool` is a standalone .NET 10 console program that invokes the installed
SDK's `dotnet format`. It needs no IDE and adds no dependency to the application
being edited. This initial delivery supports **Windows with SDK 10.0.403** and
single-target SDK-style C# projects. A `.sln` or `.slnx` must contain only C#
projects. Multi-targeting, solution filters, legacy projects, Linux acceptance
and macOS support are outside this initial contract.

## Build a local deliverable

From this directory, publish to a fresh directory outside the source tree:

```powershell
dotnet publish FormatTool.csproj -c Release -r win-x64 --self-contained true -o C:/artifacts/format-tool
```

Copy the **entire publish directory** to a machine with the supported SDK. Run
`FormatTool.exe --version` or `FormatTool.exe --request C:/work/format.json`.
The publish directory, including this guide, is independently runnable without
the framework checkout. It is not an installed framework component or a formal
release. No installer, global tool registration or automatic SDK download occurs.

## Request and paths

```json
{
  "schemaVersion": 1,
  "workspace": "app/App.csproj",
  "files": ["Nested/Chosen.cs"],
  "mode": "whitespace",
  "action": "check",
  "allowRestore": false
}
```

`workspace` is absolute or relative to the **request file's directory**. Every
`files` entry is absolute or relative to the **workspace file's directory**, also
returned as `pathBase`. The caller's working directory does not select files or
SDK policy. The tool runs the SDK from `pathBase`, respecting its `global.json`.
Supply exact files, never folders or globs. Empty, missing, non-C# and unmatched
selections fail. Every file must be an evaluated `Compile` item in that workspace;
an existing but excluded source file does not count. Linked Compile items can be
selected explicitly. Project references do not implicitly expand a `.csproj`
selection to their source files; select the containing solution when needed.

Use `action: "apply"` to write. `whitespace` invokes only the SDK whitespace
formatter. Generated files remain excluded by the SDK; there is no
`include-generated` option. `selectedFiles` describes valid source membership,
not a claim that SDK generated-code exclusions were bypassed.

## Results and failure recovery

One JSON object is written to stdout, including on failure:

| Exit | `status` | Meaning |
| --- | --- | --- |
| 0 | `clean` | No selected formatting changes were reported. |
| 0 | `applied` | Observed file changes, followed by a clean check. |
| 2 | `changes-required` | Check found selected formatting diagnostics; no formatter write requested. |
| 1 | `failed` | Invalid input, unsupported capability, load/tool failure or incomplete apply. |

`sdkVersion`, `formatterVersion`, `loadedProjects`, `selectedFiles`,
`configurationFiles` and `commands` expose the actual version, scope and SDK
output. `findings` holds reported diagnostic locations. A formatter report is
**not** evidence of writes: `changedFiles` is calculated from file bytes,
including on failure. `unexpectedChangedFiles` names observed changes outside
the selection. `remainingFindings` holds the check after apply. A failure never
claims transactional rollback. Inspect the diff and preserve your existing edits
before selectively recovering changed files; do not blindly reset the workspace.

Check uses `--verify-no-changes`. Apply is followed by that same check and cannot
claim success while selected diagnostics remain. A load failure cannot become a
clean result merely because no diagnostic was found. Do not edit source
concurrently with this command. Source comparisons cover existing evaluated
Compile items and initially selected files, not every possible custom-build
side effect or file on disk.

## Configuration and execution requirements

The SDK owns EditorConfig hierarchy, section matching and C# settings. This tool
does not translate options or impose its own style. `configurationFiles` lists
ancestor configuration candidates; the captured diagnostic SDK log also lists
configuration consumed during project loading, including generated/global
configuration. Missing options use **SDK 10.0.403 defaults**, including C#'s
four-space indentation unless overridden. Ancestor files above `root = true`
may appear in the candidate list but do not override the SDK's hierarchy.
Unknown and vendor-specific properties are not claimed as applied. See the
[SDK command documentation](https://learn.microsoft.com/en-us/dotnet/core/tools/dotnet-format)
and [C# formatting settings](https://learn.microsoft.com/en-us/dotnet/fundamentals/code-analysis/style-rules/csharp-formatting-options).

Restore is off by default and assets must already exist. Restore explicitly with
your project's configured feeds, or set `allowRestore: true` to permit one
`dotnet restore` before loading. Formatter commands always pass `--no-restore`.
Offline operation requires the SDK, assets and all referenced packages already
available locally. SDK commands have a two-minute timeout each; timeout/failure
does not undo completed operations.

Use trusted workspaces. MSBuild evaluation, imported targets and explicit restore
can execute code and write intermediate files even in check mode. Check is a
formatter source-write contract, not an OS sandbox. A clean format result is not
compilation, tests, business validation or complete ReSharper cleanup.
