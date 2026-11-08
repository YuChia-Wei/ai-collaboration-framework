# RefactorTool delivery acceptance

Check the actual extracted win-x64 ZIP. The inventory case verifies the
BuildHost, notices, licenses, and absence of test dependencies. The preview
smoke starts the extracted executable and loads a real restored project.

Follow the [test overview](../README.md) to publish, extract, and select the
executable. Run from the repository root.

```powershell
dotnet test tests/dotnet-refactoring/artifact/RefactorTool.ArtifactIntegrationTests.csproj -c Release
```
