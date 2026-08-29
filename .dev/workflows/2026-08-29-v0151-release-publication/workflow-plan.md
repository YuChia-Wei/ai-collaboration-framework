# v0.15.1 Release Publication

## Objective

Prepare a governed v0.15.1 patch candidate containing the Issue #261 validation
contract repairs, prove that the deterministic package can be installed and
upgraded from v0.15.0, obtain fresh AI-context verification, and hand each
provider mutation to its separately authorized gate.

## Scope And Authority

- Included implementation: Issue #261.
- Release coordination and acceptance: Issue #262.
- Owner skill: `ai-context-governance`.
- Current branch: `codex/2026-08-29-v0151-validation-contract-fixes`.
- Authorized now: local release records, deterministic artifacts, focused
  validation, clean-install and v0.15.0 upgrade evidence, workflow artifacts,
  and local commits.
- Separate gates: push, pull request, merge, Issue or Project terminal mutation,
  annotated tag creation or push, GitHub Release creation, and publication.

## Acceptance-To-Evidence Projection

The machine-readable authority is `acceptance-ledger.yaml`.

| Acceptance | Required evidence | Current disposition |
| --- | --- | --- |
| REL0151-A1 | Fresh read-only AI-context audit against an immutable candidate | pending |
| REL0151-A2 | Version-correct notes, migration guidance, phase contract, release record, and provider reconciliation | in progress |
| REL0151-A3 | Deterministic v0.15.1 ZIP/tar packages and independent archive validation | pending |
| REL0151-A4 | Actual clean install and v0.15.0-to-v0.15.1 upgrade, plus retained-origin route resolution | pending |
| REL0151-A5 | Candidate release-state validation on one clean exact commit | pending |
| REL0151-A6 | Push, PR, merge, tag, hosted publication, and terminal provider changes only after their explicit gates | deferred to owner gates |

## Execution Order

1. Instantiate the release workflow and planned phase contract without copying
   historical run identities or claiming candidate validation.
2. Build and validate the deterministic v0.15.1 package from the current source.
3. Execute clean-install and v0.15.0 automatic-upgrade validation and construct
   canonical retained-origin route evidence from observed results.
4. Complete the governed release record only after the package evidence exists.
5. Commit the source candidate, obtain fresh read-only AI-context verification,
   and run the candidate release gate on that exact clean commit.
6. Ask the owner separately before each remote transport, integration, tag, and
   publication boundary.

## Release Classification

- Version: `v0.15.1`.
- Compatibility: non-breaking patch within the v0.15 public package identity.
- Automatic upgrade source: `v0.15.0` only.
- Retained governed origins: `v0.15.0`, `v0.9.0`, and `v0.6.0` through the
  source-only support matrix.
- Public package base: `ai-collaboration-framework-v0.15.1`.

## Stop Conditions

Stop before claiming release readiness if the fresh audit, actual package
execution, route evidence, provider state, or exact-head candidate gate cannot
be proved. Stop before any remote mutation whose separate authorization has not
been obtained.

## Continuation

The planned seed tree at
`f741765e457a3dcd7f65175db9f3f9d1bf9586ae` produced deterministic diagnostic
ZIP and tar.gz archives, and independent archive validation passed. Final
package acceptance remains pending because the terminal release record,
actual clean install and v0.15.0 upgrade, retained-route evidence, and fresh
audit are not yet complete.

The actual package execution is expected to exceed the repository's
long-running threshold. The current owning skill has no canonical delegated
validator role binding, so an agent execution packet cannot pass the mandatory
pre-dispatch guardrail. Do not bypass that boundary. Continue through an
authorized hosted validation path or a separately governed fresh execution
surface. No remote branch, pull request, tag, or hosted Release exists for
v0.15.1 at this checkpoint.
