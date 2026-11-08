# FormatTool tests

Run the typed cleanup rule cases and in-process request cases with the .NET 10
SDK. Unit tests call the product rules directly. Integration cases exercise the
request file and JSON result and use actual file identities for path checks.

```text
dotnet test tests/dotnet-formatting/unit/FormatTool.UnitTests.csproj
dotnet test tests/dotnet-formatting/FormatTool.IntegrationTests.csproj
```

SDK integration runs automatically on Windows x64 when SDK 10.0.403 is
discoverable, or on macOS arm64 when SDK 10.0.400 is discoverable. Each fixture pins the
supported SDK without roll-forward and restores from a local source. The
tests exercise the wrapper's actual MSBuild command and evaluated Compile
results, formatter include matching, nested EditorConfig, diagnostic reports,
source bytes, and generator consent in compiler and design-time contexts.

Publish Native AOT with the [FormatTool manual](../../src/tools/dotnet/formatting/README.md),
then set `AICF_FORMAT_ARTIFACT` to the absolute path of the executable and run
the artifact project.

```text
dotnet test tests/dotnet-formatting/artifact/FormatTool.ArtifactIntegrationTests.csproj -c Release
```

The case-alias test on macOS arm64 probes the scratch volume for case-sensitive
names. Set `AICF_FORMAT_CASE_ROOT` to an existing absolute directory on a
case-sensitive volume to select that location. The Formatting acceptance
workflow supplies a mounted case-sensitive APFS directory. The case checks
both real Compile identities before the formatter.
The POSIX literal filename cases require macOS. Missing-file and directory
selections have independent theory rows, as do the three POSIX filenames.
The CI profiles require the intended case counts in the native test reports.

Set `AICF_TEST_WORK` to a directory for disposable fixtures when needed. The
tests otherwise use the OS temporary directory and clean up their own
per-case subdirectories. A process or permission failure leaves that
integration case failed.
