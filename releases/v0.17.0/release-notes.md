# REL-v0.17.0 — Precise Roles And Task-Led Context

v0.17.0 improves everyday development collaboration: choose skills by the required output, load technology rules for the target project, and trace behavior scenarios through implementation and observable test results. Initialization guidance and assessment identifiers are shorter and easier to maintain.

## Highlights

- **Target-aware design and review.** The code-reviewer core is technology-neutral and selects optional technology extensions. Architecture and BDD skills support bounded design-artifact reviews with explicit criteria and evidence.
- **Clearer authoring and implementation boundaries.** Requirements, specifications and problem frames are selected by artifact type. Local-change and slice implementation are selected by the operation and dependency boundary, with handoffs only for a concrete missing decision or separable output.
- **Executable Given-When-Then handoffs.** Scenario identifiers, acceptance criteria and data rows map to setup, action, assertions and actual results. Optional BDDfy and plain xUnit examples demonstrate the same behavior. A green test or a step name alone does not prove that every required assertion executed.
- **Smaller daily context.** The initialization AGENTS seed loads context progressively, preserves existing authorization and target-owned facts, and links to the canonical CLI contract. New assessment identifiers use `ASM-YYYYMMDD-HH-xxx`, with exactly three lowercase letters or digits; historical identifiers remain valid.

## Compatibility

This pre-1.0 minor release declares migration-sensitive contract changes. Existing skill identifiers and runtime wrapper entry paths remain available, but direct consumers of the old .NET review route list must follow the selected technology extension. Review/design output and handoff expectations have also changed. Preserve target rules, customized wrappers and repository-specific AGENTS content through the normal provenance and customization reconciliation.

The retained direct sources are v0.6.0, v0.9.0 and v0.16.0. Each upgrades directly to this version using its own original manifest and the same incoming archive. See the migration guide for source-specific entry points and recovery boundaries.

## Release Validation

The framework source gate remains independent of the .NET SDK. The included .NET projects are optional teaching examples; target owners select their own SDK, test commands and technical rules. Framework checks and representative upgrade evidence do not establish that every downstream project's custom validation has passed.

<!--
The renderer appends canonical Included Work and release provenance. Keep this
authored content phase-neutral and omit generated automation details.
-->
