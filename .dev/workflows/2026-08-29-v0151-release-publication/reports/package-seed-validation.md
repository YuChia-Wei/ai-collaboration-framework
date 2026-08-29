# v0.15.1 Package Seed Validation

## Subject

- Source commit: `f741765e457a3dcd7f65175db9f3f9d1bf9586ae`.
- Release record state: `planned`.
- Automatic migration input: v0.15.0 governed `metadata/files.yaml`.
- Output class: ignored local diagnostic package; not a publication asset.

## Observed Result

- The deterministic builder produced the v0.15.1 ZIP and tar.gz archives.
- Independent archive validation passed for both archives, including sidecars
  and ZIP/tar payload parity.
- The first build invocation did not execute because its asserted full commit
  was typed incorrectly; the unchanged build command passed after binding the
  exact `git rev-parse HEAD` value shown above.

## Evidence Boundary

This proves that the planned immutable Git tree is package-buildable and that
the resulting diagnostic archives are structurally valid. It does not prove
the final release package because `release.yaml` is still planned, and it does
not satisfy actual clean-install, v0.15.0 upgrade, retained-route, fresh audit,
candidate, hosted, tag, or publication acceptance.

The ignored raw archives remain under
`.dev/ai-context/local/release/v0.15.1/seed-build/` and are not Git history or
public release artifacts.
