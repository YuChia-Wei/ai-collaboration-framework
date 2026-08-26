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

Trusted Linux execution from a Windows host must use the repository-owned
WSL-native launcher instead of opening the checkout or a wrapper through a
shared `/mnt/*` path:

```powershell
python .ai/scripts/run-v015-package-validation-wsl.py long `
  --distribution Ubuntu-24.04 `
  --expected-commit SHA `
  --output-dir .dev/ai-context/local/validation/issue-250-252/SHA/long-linux `
  --trusted-reference
```

The launcher verifies a clean exact head, creates a Git bundle with Windows
Git, streams the bundle and any prior terminal over stdin, and performs clone,
execution, and cleanup in one unique WSL-native `/tmp` directory. The
repository-owned inline command receives only bounded scalar arguments; it
does not receive a Windows path. Evidence is
returned over stdout and persisted by the Windows process under the requested
ignored output directory. The WSL process rejects `9p`/`drvfs`, never receives
a Windows checkout or script path, and explicitly removes
`AI_CONTEXT_TEST_TMP_ROOT` from the durability-lane environment.

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
