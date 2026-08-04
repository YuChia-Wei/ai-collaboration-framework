# Dotnet Backend Validation

This is the runtime-validation capability of the profile-owned bundled
mechanical validation provider. It is separate from the Roslyn analyzers,
delivered as source only, and inactive until a target records an explicit
`reference-in-place` activation. It is not copied into a target repository by
this pre-cutover provider.

See the provider [activation contract](../README.md#activation-contract) before
planning target use.

## Projection Model Registration

`ProjectionModelRegistrationValidator.FindUnregistered` discovers concrete types that implement the target repository's projection read-model marker interface and reports those absent from the assembled EF Core model.

The production marker interface belongs in the target repository's shared query/read-model building blocks, not in this validation project. The recommended name is `IProjectionReadModel`.

Example target-owned test plan:

```csharp
var missing = ProjectionModelRegistrationValidator.FindUnregistered(
    typeof(IProjectionReadModel).Assembly.GetTypes(),
    typeof(IProjectionReadModel),
    type => dbContext.Model.FindEntityType(type) is not null);

Assert.Empty(missing);
```

Dapper-only DTOs and query services should not implement the marker interface.

## Source Repository Verification

```bash
dotnet test tools/DotnetBackendValidation.Tests/DotnetBackendValidation.Tests.csproj
```

The root test project is source-repository verification only. It references the
canonical provider source in place and is excluded from target delivery.

## Activation Direction

An activation record selects this capability independently from `analyzers` and
must record its target plan, runtime-test invocation, configuration ownership,
evidence, outcome, and freshness. The provider does not modify target `.slnx`,
`Directory.Build.props`, `.editorconfig`, project/package references, severity,
or warnings-as-errors settings.
