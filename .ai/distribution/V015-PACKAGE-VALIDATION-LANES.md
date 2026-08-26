# v0.15 Package Validation Lanes

The machine-readable contract is
`.ai/distribution/validation/v015-package-validation-lanes.yaml`; terminal
records follow
`.ai/distribution/schemas/v015-package-validation-terminal.schema.yaml`.

The three source-only commands are intentionally independent:

- `fast` proves identity, sidecar, and ZIP/tar parity without creating a target.
- `medium` applies a synthetic v0.15 candidate to a synthetic clean target.
- `long` upgrades an extracted, published v0.14 payload to the synthetic v0.15
  candidate on real storage and records build, extract, snapshot, plan,
  decision, apply, receipt, and cleanup phases.

All output must be under the ignored `.dev/ai-context/local/validation/` root.
The runner never creates a tracked v0.15 release record; its release metadata
exists only in the ignored synthetic source used to build a candidate.

`fast` and `medium` can never prove an actual upgrade. Aggregation requires
independent trusted Windows and Linux `long` terminals and keeps missing,
failed, blocked, not-applicable, and owner-deferred results non-passing.
Issue #254 remains the owner of later integrated-main release readiness.

If `medium` or any other lane is expected or observed to reach 120 seconds, it
uses the same clean immutable commit, validated packet, exclusive writer lease,
read-only delegation, ignored output, and one-wait boundary as `long`. An
interrupted parent execution is retained as non-passing evidence.
