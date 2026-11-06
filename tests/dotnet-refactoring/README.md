# RefactorTool acceptance

These tests execute the actual CLI, .NET SDK and Roslyn against temporary
two-project C# solutions. They require Python 3.11+, Windows x64, SDK 10.0.403,
and a built or published RefactorTool. Fixture restore uses only the local SDK
reference packs and an empty local package source.

```powershell
python -I -B tests/dotnet-refactoring/accept_refactoring.py --tool C:/staging/refactor-win-x64/RefactorTool.exe --work C:/scratch/refactor-acceptance -v
```

The selected SDK version can be supplied with `--sdk-version`; that records a
different environment, not an automatic expansion of the published support
matrix. Tests use actual expected source expressions and a post-apply build for
the representative cross-project scenario. They distinguish source preservation
from SDK-generated `obj` intermediates and exercise original-error reporting,
new conflicts, unsupported workspace forms and plan/input drift.

This suite is separately selected for refactoring changes. It does not rerun
formatting acceptance or imply all-platform/runtime acceptance.

The small I/O harness compiles the production `FileApply` and contract sources
directly. It supplies streams that fail after writing a prefix and while reading
the observed result. This validates the production state-reporting algorithm;
it does not claim a real disk-full, power-loss or process-crash experiment.

```powershell
dotnet run --project tests/dotnet-refactoring/io-failure/IoFailure.csproj -c Release
```
