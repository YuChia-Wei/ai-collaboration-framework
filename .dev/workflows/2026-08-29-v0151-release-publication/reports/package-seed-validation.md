# v0.15.1 Package Candidate Validation

## Subject

- Package source commit: `cbd36d41be44e12fbc6031ec5c87b23ee5fccbc3`.
- Release record state: `validated`.
- Automatic migration input: v0.15.0 governed `metadata/files.yaml`.
- Output class: source-retained route candidate plus ignored tar diagnostic;
  not a public Release asset.

## Observed Result

- The deterministic builder produced the v0.15.1 ZIP and tar.gz archives.
- Independent archive validation passed for both archives, including sidecars
  and ZIP/tar payload parity.
- The ZIP SHA-256 is
  `3b5c0483cbf7d8076d3bf9cdd2cfd6f1bac290726e5904a7fa3b29bbc4424c3e`.
- The payload fingerprint is
  `ef8f900a840e8869189b50b28a7735dcf279046665ebed3f89b18637f43b8017`.
- Incoming-candidate validation passed from the retained release-local ZIP.
- The evidence-bound v0.15.0-to-v0.15.1 direct route passed, and v0.9.0 plus
  v0.6.0 resolve canonically through the retained v0.14.0 and v0.15.0 edges.

## Evidence Boundary

This proves that the package-source Git tree is package-buildable, that the
archives are structurally valid, and that retained upgrade routing resolves.
Release metadata and route artifacts are source-only, so their later commit
does not change the selected public payload. It does not replace a fresh build
or hosted actual admission for the final PR head, and it does not authorize
merge, tag, or publication.

The route ZIP and canonical receipts are under
`.dev/releases/v0.15.1/route-assets/`; the ignored tar diagnostic remains under
`.dev/ai-context/local/release/v0.15.1/cbd36d41-package/`.
