# Reconstruction contract tests

The package-free Replay and Plan cases run with the [generation tests](../README.md).
The published CT-005 cases require the two verified 0.0.3-preview net8.0
assemblies described in [BASELINE.md](BASELINE.md).

```text
dotnet test tests/dotnet-generation/domain-contract/published/PublishedDomainContract.Tests.csproj -p:PublishedContractsDir=<verified-extracted-directory>
```

The explicit project reports a build error when either supplied assembly
is missing. Test-runner dependencies restore through the usual NuGet
configuration. The ArchPrecept assemblies are resolved from the supplied
directory.
