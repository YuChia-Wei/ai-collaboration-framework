# Selected-file formatting

`FormatTool` is a standalone .NET 10 console program that invokes the installed
SDK's `dotnet format`. It needs no IDE and adds no dependency to the application
being edited. Supported combinations are **Windows x64 with SDK 10.0.403** and
**macOS Apple silicon (arm64) with SDK 10.0.400**, using single-target SDK-style
C# projects. Other SDK versions, including other servicing versions, are not
implicitly accepted. A `.sln` or `.slnx` must contain only C# projects.
Multi-targeting, solution filters, legacy projects, Linux and Intel macOS
formatting are outside this contract.
Solution selection is available for whitespace. Cleanup supports a direct
`.csproj` with **no ProjectReference items**; solution configuration mappings
and referenced-project execution contexts are not part of this initial subset.

## Install or build

Releases containing `generation/formatting` install this tool through
`python generation/install-generation.py --project <existing-project>` from the
extracted release. Choose the executable for your environment:

| Environment | Installed executable | Required SDK |
| --- | --- | --- |
| Windows x64 | `.ai/tools/dotnet-generation/formatting/win-x64/FormatTool.exe` | `10.0.403` |
| macOS arm64 | `.ai/tools/dotnet-generation/formatting/osx-arm64/FormatTool` | `10.0.400` |

The existing `generation.json` inventory owns its version, files and recovery;
Framework's knowledge lock does not track this separately installed tool bundle.
Older bundles without `formatting` do not supply this capability.

From this source directory, publish to a fresh directory outside the source tree:

```powershell
dotnet publish FormatTool.csproj -c Release -r win-x64 --self-contained false -o C:/artifacts/format-tool
```

Copy the **entire publish directory** to a machine with the supported SDK. Run
`FormatTool.exe --version` or `FormatTool.exe --request C:/work/format.json`.
The project defaults to framework-dependent single-file publishing with the command
above: one executable and this guide, without an embedded runtime or loose DLLs/PDBs.
Install the matching .NET 10 SDK on the host before running it; its runtime must
be discoverable by the .NET apphost, and `dotnet` must be on PATH for SDK commands.
For a custom installation, configure the .NET host lookup (for example,
`DOTNET_ROOT_X64` on Windows x64 or `DOTNET_ROOT_ARM64` on macOS arm64) as well as PATH.
The release builder uses the same single-file settings for snippets and formatting
and rejects unexpected runtime files. No global tool registration or automatic
SDK download occurs. A local publish alone is not a formal release.
For macOS, use `-r osx-arm64` and a destination you own, then run `./FormatTool`.
The macOS executable uses .NET's ad-hoc signature; it is not Developer ID signed
or notarized. Download quarantine/Gatekeeper acceptance is separate from SDK
behavioral compatibility. Preserve those platform protections when evaluating a
downloaded artifact.

The macOS compatibility basis is a native Apple silicon / SDK 10.0.400 run of
the 12 original acceptance cases against a copy with only the former OS/SDK
gates removed. That evidence is accepted for this exact combination. The
`Formatting acceptance` workflow now exercises the unmodified published source
on Windows and macOS with the respective exact SDKs. Each run's outcome remains
its own evidence; compatibility does not certify every macOS release or every
workspace. A general compatibility registry is not required by this delivery.

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
an existing but excluded source file does not count. Files must be inside the
workspace directory: SDK include matching can silently ignore parent-relative
or cross-drive files, so those selections return `unsupported-selection` before
formatting. Linked Compile items inside that boundary can be selected explicitly;
for whitespace, select an enclosing solution to cover links outside a project's
own directory. Project references do not implicitly expand a `.csproj`
selection to their source files; select the containing solution when needed.
SDK includes are glob patterns with case-insensitive matching. Literal `*`, `?`
and POSIX backslash characters anywhere in the selected relative path are
rejected before SDK execution. On macOS, a selected path that differs from another
evaluated Compile item only by case is rejected before formatter execution,
including on case-sensitive APFS. Windows uses case-insensitive Compile identity;
this alias check does not cover Windows directories explicitly configured as
case-sensitive. The macOS guard prevents apply from broadening the write scope
before post-operation checks can detect it.

Use `action: "apply"` to write. `whitespace` invokes only the SDK whitespace
formatter. Generated files remain excluded by the SDK; there is no
`include-generated` option. `selectedFiles` describes valid source membership,
not a claim that SDK generated-code exclusions were bypassed.
`unreportedSelections` lists selected files with no entry in the SDK's change
report. They may already be clean or excluded by the SDK, including generated
files. The SDK does not report which of these reasons applies. The result
message makes this uncertainty explicit; no filename heuristic overrides
EditorConfig or claims an exclusion that the SDK did not report.

Optional `verbose: true` includes the full SDK command output, capability list
and explanatory notes. By default, successful `clean`, `applied` and
`changes-required` results include command arguments, working directories and
exit codes without command stdout/stderr. Failures retain full command output
for diagnosis even without verbose. Unknown properties, duplicate properties,
malformed JSON and wrong JSON types return `invalid-request` before SDK execution.

## Bounded cleanup

Choose `mode: "style"` or `mode: "analyzers"`, and supply both a nonempty
`diagnostics` array and `severity` (`info`, `warn`, or `error`). Severity is a
minimum threshold; it does not enable a suppressed rule. Whitespace rejects
these options. Cleanup never silently selects all analyzer fixes.

```json
{
  "schemaVersion": 1,
  "workspace": "app/App.csproj",
  "files": ["Nested/Chosen.cs"],
  "mode": "style",
  "action": "check",
  "diagnostics": ["IDE0008"],
  "severity": "warn"
}
```

`--capabilities` and verbose results expose this deliberately small rule list
and `supportedEnvironments`, which names the exact runtime/SDK pairs above.
The rules apply to both pairs. Capabilities are declared support, not a probe
of an installed SDK; regular results carry the actual `sdkVersion` separately.

| Mode | Diagnostic | Contract |
| --- | --- | --- |
| `style` | `IDE0008` | Use explicit type instead of `var`, according to effective C# style settings. |
| `analyzers` | `CA1805` | Remove unnecessary default-value field initialization. |
| `analyzers` | `CA1040` | Known `no-fixer` response; no cleanup executes. |
| either | other IDs | `unsupported-diagnostic`; no cleanup executes. |

For the style example, set `csharp_style_var_for_built_in_types = false:warning`
and `dotnet_diagnostic.IDE0008.severity = warning` in the applicable EditorConfig
section. For analyzer cleanup select `CA1805` and enable it with
`dotnet_diagnostic.CA1805.severity = warning`. These are different operations;
neither selects the other. Fixes may carry SDK syntax-formatting adjustments.
The list does not promise arbitrary member ordering, all Roslyn fixes, complete
ReSharper profiles or third-party code fixes. See Microsoft's
[var preference rules](https://learn.microsoft.com/en-us/dotnet/fundamentals/code-analysis/style-rules/ide0007-ide0008)
and [CA1805](https://learn.microsoft.com/en-us/dotnet/fundamentals/code-analysis/quality-rules/ca1805).

Cleanup checks design-time loading and rejects solution or ProjectReference
contexts with `unsupported-cleanup-workspace`. Their configuration/property
mappings cannot be inferred safely from standalone project queries. This remains
an explicit unsupported result even if all current files happen to be clean.
No compiler or formatter is run for that rejection. Whitespace retains its
project/solution support.

For a supported project, cleanup requires a successful `dotnet msbuild
-target:Compile` with ordinary analyzer execution and project-reference builds
disabled, so missing types/references or compiler errors cannot
masquerade as a clean style result. Source generators still run during that
compilation. Apply also checks compilation after its changes before the final
format check. The compiler target and properties match the ordinary preflight,
except that preflight skips the compiler. No Build-level targets or implicit
restore are added. Compiler outputs go to the target's ordinary intermediate
locations; target settings such as warnings-as-errors remain effective. These
checks establish compilation prerequisites, not business correctness.

SDK/targeting-pack analyzers and generators are part of the selected SDK.
Other resolved analyzer or source-generator DLLs, including NuGet packages,
produce `analyzer-consent-required` **before
the compiler or formatter executes**. The result lists `projectAnalyzers`.
To permit them, supply their exact paths in `allowedProjectAnalyzers`; relative
paths use `pathBase`. This permits their code to execute, including source
generators, while fixes remain limited to the diagnostic support list above.
No analyzer is downloaded or installed by this option. Design-time and ordinary
Compile item queries run with `SkipCompilerExecution=true` before this decision.
The design-time query uses the supported formatters' BuildHost global properties,
including `AlwaysCompileMarkupFilesInSeparateDomain=False`, and runs
`Compile;CoreCompile` plus `DesignTimeMarkupCompilation` when the project defines
it. This includes analyzer items conditional on formatter-specific properties or
its optional markup target. Changing the supported SDK requires rechecking this
loading contract.
MSBuild evaluation/custom targets remain trusted execution as described below;
the allowlist is not a sandbox for a malicious project that runs arbitrary code.

## Results and failure recovery

Once the .NET host starts the application, one JSON object is written to stdout,
including on application failure. If the required runtime cannot be found, the
.NET host fails before this contract starts; its stderr/exit code is a native
host diagnostic, not a FormatTool JSON result:

| Exit | `status` | Meaning |
| --- | --- | --- |
| 0 | `clean` | No selected formatting changes were reported; selections can be clean or SDK-excluded. |
| 0 | `applied` | Observed file changes, followed by a clean check. |
| 2 | `changes-required` | Check found selected formatting diagnostics; no formatter write requested. |
| 1 | `failed` | Invalid input, unsupported capability, load/tool failure or incomplete apply. |

`sdkVersion`, `formatterVersion`, `loadedProjects`, `selectedFiles`,
`configurationFiles` and `commands` expose the actual version, scope and command
summary (full SDK output with `verbose: true` or on failure). `findings` holds
reported diagnostic locations. `unreportedSelections` concerns the first
formatter pass, not the mandatory check after apply. A formatter report is
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
ancestor configuration candidates; the verbose diagnostic SDK log also lists
configuration consumed during project loading, including generated/global
configuration. Missing options use **the selected SDK's defaults**, including C#'s
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
