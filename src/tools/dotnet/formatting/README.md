# Format .NET source with the SDK

`Format-Dotnet.ps1` runs the installed SDK's `dotnet format` from the directory
that contains the supplied project or solution. Use it from PowerShell 7.3+
with `dotnet` on PATH. The workspace's normal SDK selection (including
`global.json`) and `.editorconfig` apply. Use a trusted workspace. MSBuild can
evaluate project code and load analyzers or source generators.

## Check or apply selected files

From PowerShell, with the script installed by the generation bundle:

```powershell
$formatter = './.ai/tools/dotnet-generation/formatting/Format-Dotnet.ps1'
& $formatter -Workspace './src/App/App.csproj' -Files @('Services/Order Handler.cs', 'Program.cs')
$checkExit = $LASTEXITCODE

& $formatter -Workspace './src/App/App.csproj' -Files @('Services/Order Handler.cs') -Apply
```

`-Workspace` is relative to the caller or absolute. The script resolves
`-Files` from the workspace directory and requires existing files beneath it.
Choose the owning project or an enclosing solution to select files outside a
nested solution's directory. Absolute file paths must use the same workspace-root
casing as the supplied workspace. Literal paths containing `*`, `?`, or POSIX
backslashes are rejected because the SDK interprets them as patterns or separators.
`-WholeWorkspace` explicitly selects the entire project or solution.
The SDK matches the selected paths against the loaded workspace. An existing
file outside the loaded sources can match nothing and still yield exit 0.
Native include matching is case-insensitive, even on case-sensitive volumes;
case-distinct source names can therefore both match. Use detailed output or a
report to inspect SDK activity when selection is in doubt.

The script defaults to `-Mode Whitespace`, check and no restore. Restore the
workspace separately when needed, including for whitespace mode. `-Restore`
omits `--no-restore` and permits the selected SDK mode's normal restore behavior;
it does not force a restore in whitespace mode.
Workspace loading can still create build artifacts. Choose `-Mode Style`,
`-Mode Analyzers` or `-Mode All` for additional SDK formatting rules. Supply
native option tokens individually through `-SdkOptions`:

```powershell
& $formatter -Workspace './src/App/App.csproj' -Files @('Program.cs') -Mode Style `
    -SdkOptions @('--diagnostics', 'IDE0005', '--severity', 'info', '--report', './format-report')
```

Relative paths in native options also start at the workspace directory.
Workspace mode, inclusion, check/apply and restore are controlled by the
script's parameters. Use the SDK directly for other invocation shapes.
[Microsoft's dotnet format reference](https://learn.microsoft.com/en-us/dotnet/core/tools/dotnet-format)

## Native output and migration

The SDK writes its usual console output and supplies the exit code. In check
mode (`--verify-no-changes`), a nonzero exit can mean formatting is required or
the SDK encountered an error. Inspect the console output and any requested SDK
report. `--report` requests the SDK's JSON report in the supplied directory.
Use `-Apply` to let the SDK edit source files. A failure can leave partial
edits. Review changes and use version control for recovery.

For macOS, Linux or another shell without PowerShell, the equivalent check is:

```sh
cd /path/to/project
dotnet format whitespace ./App.csproj --no-restore --verify-no-changes --include './Services/Order Handler.cs'
```

The script replaces the former FormatTool executable and its request,
capability and response JSON contracts, custom analyzer consent, byte-diff
verification and formatter-specific exit codes. Migrate callers to native
arguments and SDK output. An update of an unchanged generation installation
replaces the old executable layout with this script and manual.
