# v0.15.1 Release Package Impact

## Decision

`confirmed-material`: the Issue #261 patch changes the distributed package payload and envelope. If package consumers are to receive these fixes, a new immutable package version is required. Because v0.15.0 is already published and immutable, the appropriate candidate is v0.15.1.

This is a release-allocation recommendation, not release readiness, tag, Release, or publication authorization.

## Comparison Method

- Builder: `.ai/scripts/build-ai-context-package.py`.
- Baseline source: `v0.15.0` / `5fedaceef7e18b4cdcde3cb665adcc97070db2df`.
- Candidate source: `303eee678ee2848d92b7007b0fe8a7a170ca8fe2`.
- Diagnostic version identity: `0.15.0` for both builds so the existing release contract could be evaluated; the candidate archive is not publishable under that identity.
- Migration source: published v0.14.0 `metadata/files.yaml`.
- Both ZIP packages built successfully with 647 members and were compared by repository-relative member path and SHA-256.
- Live GitHub Release read-back reported the published ZIP digest as `efd2509f6c869dcadfea7f58fcb942efa9f2c46ab7ae181f4160d47fd4112a92` and the published tar.gz digest as `ef849caefd085c77a3c6cef416c912b1dec7b18c839543757888afa4378472d7`; both exactly match the deterministic baseline build.
- `validate-ai-context-package.py` passed separately for the baseline ZIP/tar.gz pair and the candidate ZIP/tar.gz pair.

## Direct Consumer Changes

| Package member | v0.15.0 SHA-256 | Candidate SHA-256 |
| --- | --- | --- |
| `INSTALL.md` | `c7f12212f0dbc5be1f0b6e9aee4984d52959c4d625ffc3bbc55d1c2b4a9c7403` | `439fce297a8a875ee065e6080cfca15004b1c2466de5587bd4d5a9a24ba714d7` |
| `payload/.ai/scripts/check-all.sh` | `84c536ded79b5a4bbfc5ef02255ff98c22bce5f7afd1529f9a0f23f17e33871d` | `5733f1048829198a23c58d64c81ddf2265000d39347b79a9685cc3adac1f988f` |
| `payload/.ai/scripts/validation-evidence.py` | `2999d9b919b15666bccee4c4d44f0250e093709ca68eb97fc969054e0b71f198` | `58be9ef73e2646b413605b35e567b75e673df2ed8e22db90a86fe0113e40d290` |
| `payload/.ai/scripts/validation-profile-registry.sh` | `ff63036e3498c20384244bfbf1bc174404cf1051ae414821c617a2b8d157f9d0` | `e1b934dd12389811ab566137e886dcf92fdb1eeaea28b1e1aa09d90d4b319409` |

The package payload fingerprint changed from `6c2bd24ef993c4ac122bce0c6bdd528c39e559fd47b0ec8b76ead80e4d8dc0e3` to `34242a7f7cbf9a7d7ff3cacae38bd55db1e28a742bb1acd10ee9d852699b9d71`.

## Derived Package Changes

Six derived members also changed: `metadata/package.yaml`, `metadata/files.yaml`, `metadata/migration.yaml`, `metadata/selected-inputs.json`, `metadata/validation.json`, and `metadata/SHA256SUMS.txt`.

The ZIP digest changed from `efd2509f6c869dcadfea7f58fcb942efa9f2c46ab7ae181f4160d47fd4112a92` to `61aa39da4bae7b5a07e38edac8e264cc04f7ac09df80ed4cc7f447c2a39cdbfa`. The tar.gz digest changed from `ef849caefd085c77a3c6cef416c912b1dec7b18c839543757888afa4378472d7` to `a0a1b11c73dc09993e30fe460e494f750f74f33f59e9449a1370af9b304e5725`.

## Excluded Source-Only Changes

Focused test files and `.dev/workflows/**` evidence are excluded by the distribution profile. They do not account for the changed payload fingerprint. The material package change comes from the three distributed runtime scripts; the INSTALL change additionally changes the package envelope and selected-input identity.

## Release Boundary

The comparison proves package impact, not release admission. A v0.15.1 release still requires separately authorized version/release records, candidate construction under the v0.15.1 identity, applicable package and upgrade validation, exact-head review/admission evidence, tag authorization, and publication authorization.
