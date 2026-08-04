# Bundled Mechanical Validation Provider

Provider ID: `ai-context-dotnet-bundled-mechanical-validation`.

This profile-owned provider distributes source only. Its default delivery and
activation state is `source-available`: it does not activate validation, copy
production source, or change any target file.

## Capabilities

| Capability | Source root | Separate target plan must record |
| --- | --- | --- |
| `analyzers` | `analyzers/` | selection, analyzer wiring, build invocation, configuration ownership, evidence |
| `runtime-validation` | `runtime-validation/` | selection, runtime-test wiring, test invocation, configuration ownership, evidence |

Selecting either capability never selects the other. Their source projects are
kept separate to preserve that boundary.

## Activation Contract

The only implemented activation mode is `reference-in-place`. First record an
authorized target-owned plan. The target owner may then apply the selected
wiring and configuration. Only a later target invocation with verified,
file-backed evidence can support `active-reference-in-place`.

A record based on
[`templates/reference-in-place-activation-record.yaml`](templates/reference-in-place-activation-record.yaml)
pins this provider ID, framework version and commit, this canonical root, and
the raw SHA-256 of `provider-manifest.yaml`. It also pins the SHA-256 of the
canonical JSON representation of its `target_plan`; neither digest is a
self-asserted freshness enum.

Each selected capability names three distinct evidence IDs: `wiring`,
`configuration`, and `invocation`. The record registry resolves each ID under
an explicit `evidence.root` (or the defined default). For an active claim, the
evaluator reads only that registry and those named files: it does not scan or
mutate the target. Every file must be a regular, non-symlink,
repository-relative file beneath the evidence root; its recorded raw SHA-256
must match its bytes. Its closed metadata binds the provider ID, framework
commit, capability, evidence kind, status, and target-plan digest.

For an active evaluation, `provider_root` must resolve to exactly
`<repository_root>/.ai/assets/tech-stacks/dotnet-backend/tooling/bundled-mechanical-validation`.
The evaluator rejects symlinks along that canonical path and requires the
canonical manifest, analyzer, and runtime-validation project files there to be
regular, non-symlink files. It reads the canonical manifest bytes again and
rejects a mismatch with the supplied raw manifest. An arbitrary
`--provider-root` can therefore never provide the manifest bytes or project
presence used to certify activation.

[`schemas/activation-record.schema.yaml`](schemas/activation-record.schema.yaml)
defines the record shape. The deterministic evaluator requires an explicit
repository root and raw provider-manifest bytes for an active result. Missing
verification context, an unsafe path, a missing ID, a mismatched digest, or a
kind/status mismatch fails closed. Freshness therefore comes from current
manifest and target-plan checks plus verified evidence, not merely from
declaring `fresh`.

The controlled fixture has real in-place project references, plan, wiring, and
configuration evidence but remains `unresolved`: its invocation evidence is
`not-run-owner-directed`. It is deliberately not passing activation proof.

The contract distinguishes these states:

- `source-available` — delivered but inactive default.
- `active-reference-in-place` — every selected capability has complete plan,
  wiring, invocation, configuration, evidence, and fresh outcome.
- `active-materialized` — reserved but unsupported; always fail closed here.
- `stale` and `unresolved` — incomplete, outdated, or contradictory setup;
  neither is active.

`materialize-to-tools` is not implemented. A future request must first record
a target limitation and separate authorization, but still fails in this
workflow because materialization implementation is unavailable.

Architecture Kit is `unavailable` and `pre-cutover`; it is not selectable from
this provider. Its implementation, publication, proof, and cutover need a
separate authorized readiness workflow.

This provider never mutates a target `.slnx`, `Directory.Build.props`,
`.editorconfig`, project/package references, analyzer severity, or
warnings-as-errors policy. Those files remain target-owned, separately
authorized work.

`provider_evaluator_automation_mutation: not-performed` means this evaluator
and provider automation made no target-owned configuration mutation. It does
not negate separately authorized target-owned wiring or configuration evidence.
Analyzer severity and warnings-as-errors remain optional, target-owned
decisions.

## Controlled Fixture And Test Source

- `fixtures/controlled-reference-in-place/target/ControlledReferenceInPlace.csproj`
  references both canonical provider projects in place. It contains no copied
  production source and does not alter a real target repository.
- `fixtures/controlled-reference-in-place/activation-record.yaml` names six
  typed evidence files. The two invocation files are explicitly
  `not-run-owner-directed`, not fabricated passing results.
- `scripts/evaluate-provider-activation.py` reads only the manifest, record,
  and active record's declared evidence files; it never mutates a target.
- `tests/test_provider_activation_evaluator.py` covers missing verification
  context, plan-only rejection, digest/reference/kind mismatch, unsafe paths,
  materialization rejection, and the unresolved fixture. Root `tools/*Tests`
  projects remain source-only framework tests.
