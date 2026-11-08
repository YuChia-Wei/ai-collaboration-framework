# Native template tests

The source integration project registers the canonical source copied at build
time in an isolated `dotnet new` hive. Five cases cover discovery of the seven
short names, a typed consumer of the three C# items, both generated API starters
and the two generated domain contract project shapes. Each case uses its own
output directory. The API cases build and start a generated app and follow the
created work item's HTTP Location. The tests discover the .NET 10 SDK and
ASP.NET Core 10.0 runtime automatically.

These short asynchronous SDK cases use direct xUnit Arrange/Act/Assert instead
of the former BDDfy journey wrapper. Their fixtures, action and independent
observations remain explicit. The generated domain contract examples retain
their own Given/When/Then expression.

```text
dotnet test tests/dotnet-generation/templates/Generation.Templates.IntegrationTests.csproj -c Release
```

The daily tools solution also runs the six package-free example tests directly
from their source project. The knowledge template workflow generates that
example and runs the same cases from the generated project. The
[optional CT-005 example](../../../src/knowledge/dotnet-backend/templates/domain-contracts/README.md)
requires verified external DLLs and a .NET 8 runtime.

The artifact project tests registration and named generation from the actual
nupkg and its extracted content. Use the
[artifact preparation commands](../../../src/tools/dotnet/README.md#published-artifact-acceptance)
to set the absolute `AICF_TEMPLATE_PACKAGE` path before running:

```text
dotnet test tests/dotnet-generation/templates/artifact/Generation.Templates.ArtifactIntegrationTests.csproj -c Release
```
