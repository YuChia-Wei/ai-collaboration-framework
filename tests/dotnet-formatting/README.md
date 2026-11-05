# FormatTool acceptance

These selected real-SDK cases exercise the public JSON/process contract of a
built or published FormatTool. They use Python's standard library and synthetic
single-target projects with an offline restore source. They require Windows x64
and SDK 10.0.403, or macOS arm64 and SDK 10.0.400, including working MSBuild
subprocess support. A sandbox
pipe denial is an environment failure, not formatter acceptance.

```powershell
python -I -B tests/dotnet-formatting/accept_formatting.py --tool C:/artifacts/format-tool/FormatTool.exe --work C:/scratch/format-acceptance
```

On macOS use the native `FormatTool` executable and physical directories you own:

```sh
python3 -I -B tests/dotnet-formatting/accept_formatting.py --tool /path/to/format-tool/FormatTool --work /path/to/scratch/format-acceptance --sdk-version 10.0.400
```

The fixture writes an exact-version `global.json` with roll-forward disabled;
all setup and tool SDK calls resolve from that fixture. `--sdk-version` defaults
to the supported version for the host OS. The `Formatting acceptance` workflow
publishes Native AOT and runs this same suite on Windows and macOS using the selected SDK;
the existing Python `Source change gate` remains separate.
The Mac job also runs the case-alias refusal on a small disposable case-sensitive
APFS disk image, so a case-insensitive runner cannot silently skip that check.
Literal glob/separator filename cases run on macOS; Windows skips them because
those filenames are not valid there.

`--tool` also accepts a built DLL, but that is build-output evidence, not
framework-dependent single-file publish acceptance. Use the actual detached publish directory
for the latter. The tests create and remove their own temporary projects below
`--work`; they do not format this repository. One synthetic source generator
writes a marker only inside that temporary test area, proving the explicit
analyzer-execution opt-in rather than merely checking command text.

Coverage: nested EditorConfig, preserved unselected user edits, no check writes,
actual apply/recheck, `.sln`/`.slnx`, generated conventions and EditorConfig,
invalid/unmatched files, load and partial-side-effect failures, explicit cleanup
diagnostics/severity, unsupported/no-fixer results, semantic prerequisites,
mode separation, external generator consent, rejection of solution/reference
configuration mappings, and literal `@`-prefixed/linked file paths. These are focused tool checks,
plus compact/verbose output, strict request parsing, and honest unreported
selection messages. These are focused tool checks, not the #541 generation
matrix, Linux or Intel macOS acceptance, download/Gatekeeper acceptance, or
business tests.
