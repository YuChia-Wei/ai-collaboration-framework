# FormatTool tests

Run the component cases with the .NET 10 SDK.

```text
dotnet test tests/dotnet-formatting/FormatTool.Tests.csproj
```

Set `AICF_FORMAT_SDK_TESTS=1` for SDK integration on Windows x64 with
SDK 10.0.403 or macOS arm64 with SDK 10.0.400. Each project fixture pins the
supported SDK without roll-forward and restores from a local source. The
tests exercise Compile selection, nested EditorConfig, real fixes and
unchanged source, load failures, solution and linked paths, semantic
failures, and the generator consent boundary.

Set `AICF_FORMAT_ARTIFACT` to the absolute path of a separately published
FormatTool executable to include the public process and JSON contract. The
Formatting acceptance workflow builds Native AOT and supplies the executable
for each supported platform. It separately sets `AICF_FORMAT_CASE_ROOT` to a
mounted case-sensitive APFS directory and selects
`--filter Boundary=CaseSensitiveArtifact`. That case verifies the volume is
case-sensitive and checks both real Compile identities before the formatter.
The POSIX literal filename cases require macOS.

Set `AICF_TEST_WORK` to a directory for disposable fixtures when needed. The
tests otherwise use the OS temporary directory and clean up their own
per-case subdirectories. A process or permission failure leaves that
integration case failed.
