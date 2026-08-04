# .NET Engineering Identity Bindings

Applies framework identity contract: `ENG-IDENTITY-001`.

This is the canonical .NET profile binding contract. The source-governance
[AI Context Rule Ownership](../../../../../.dev/standards/AI-CONTEXT-OWNERSHIP.md)
registry classifies it as the owner of selected .NET bindings; it does not
duplicate the contract. This file does not own the concept, rule, or constraint
that a binding enforces.

## Binding Boundary

A .NET technology binding references an existing `constraint_id` and
`capability_id`, then records the selected profile, provider identity, and any
Diagnostic, package, command, or configuration details needed to enforce that
constraint. A Roslyn analyzer and a runtime/configuration validator are
separate capabilities even when distributed by the same bundled provider.

The binding does not replace the referenced concept, rule, or constraint. A
Diagnostic ID, analyzer project, provider path, package version, `.slnx`,
`Directory.Build.props`, `.editorconfig`, or target package reference is not a
normative semantic owner. Those target files remain target-owned and can only
be selected, tuned, or changed through explicit target evidence and activation
records.

## Consumption Boundary

Routine action work loads only the task-scoped effective rule packet. It adds
binding details only for implementation, validation, upgrade, or diagnostic
handling that requires them. Missing, stale, ambiguous, or type-invalid
identity/binding resolution fails closed; it does not silently select a
framework default or activate a delivered provider.
