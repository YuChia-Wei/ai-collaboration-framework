# FormatTool acceptance

These selected real-SDK cases exercise the public JSON/process contract of a
built or published FormatTool. They use Python's standard library and synthetic
single-target projects with an offline restore source. They require Windows and
SDK 10.0.403, including working MSBuild subprocess/named-pipe support. A sandbox
pipe denial is an environment failure, not formatter acceptance.

```powershell
python -I -B tests/dotnet-formatting/accept_formatting.py --tool C:/artifacts/format-tool/FormatTool.exe --work C:/scratch/format-acceptance
```

`--tool` also accepts a built DLL, but that is build-output evidence, not
self-contained publish acceptance. Use the actual detached publish directory
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
not the #541 generation matrix, native Linux/macOS acceptance, or business tests.
