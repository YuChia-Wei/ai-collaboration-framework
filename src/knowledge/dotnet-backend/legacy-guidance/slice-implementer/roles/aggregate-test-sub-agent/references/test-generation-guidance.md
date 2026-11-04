# Aggregate Test Generation Prompt (Dotnet)

Reference-only technical guidance. Apply the target-selected architecture and technology;
this projection neither activates a runtime role nor creates an additional normative owner.

Generate aggregate-level tests (not use case tests).

## Mandatory References
- `../sub-agent.yaml`
- `../assets/skills/bdd-gwt-test-designer/skill.yaml`
- `../../../../../shared/testing-strategy.md`
- `../../../../../shared/common-rules.md`

## Rules
- Use GWT structure and naming for every test. BDDfy is the default profile; if the target team explicitly opted out, preserve GWT in plain xUnit rather than using 3A.
- `.feature` files are optional; support an explicitly supplied/requested feature or a selected target feature-runner profile without choosing the runner/package.
- No BaseTestClass
- Resolve the target `testing.mocking` selection; use NSubstitute by default
- Verify event serialization/deserialization
- Consume `../../../../../../engineering-common/references/GWT-TEST-HANDOFF-CONTRACT.md` and return concrete
  scenario/data-row-to-test/step/assertion mappings with honest execution status.
- Follow the [.NET step-method responsibilities](../../../../../standards/coding-standards/test-standards.md#step-methods-and-scenario-readability).
  Keep scenario data visible and result state isolated. Use Case fixtures belong
  in Use Case tests.

## Output Location
`src/tests/Domain/<Aggregate>/`
