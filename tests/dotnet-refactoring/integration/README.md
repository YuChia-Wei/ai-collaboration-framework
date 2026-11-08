# RefactorTool integration tests

Verify Rename and Extract Interface with real Roslyn compilations, command
input and apply preflight with local files, and project loading and compile
inclusion with MSBuild. Windows x64 SDK cases run automatically when SDK
10.0.403 is available. Junction cases also need PowerShell on PATH.

Run from the repository root.

```powershell
dotnet test tests/dotnet-refactoring/integration/RefactorTool.IntegrationTests.csproj
```

See the [test overview](../README.md) for fixtures and scenario mapping.
