# .NET formatting tests

`integration/Formatting.ScriptIntegrationTests.csproj` exercises the PowerShell entry point
against the installed SDK. It checks a workspace-relative path with spaces and
shell metacharacters, refuses parent-relative selection through a nested solution,
and applies formatting to the chosen file by absolute path within the project.
The cases also cover preservation of unselected source, workspace-relative SDK
selection and native failure propagation. They refuse glob-like literal names,
case-distinct workspace prefixes and extra include values passed as SDK options.

```text
dotnet test tests/dotnet-formatting/integration/Formatting.ScriptIntegrationTests.csproj -c Release
```

The source solution includes these cases. They use .NET 10 and PowerShell 7.3+
and create disposable projects under `AICF_TEST_WORK` or the system temporary
directory. The formatting acceptance workflow runs them on Windows and macOS.
PowerShell version discovery runs once; an absent or older host is skipped, while
an unexpected probe failure remains a test failure.
The script and its manual ship as generation-bundle content.
