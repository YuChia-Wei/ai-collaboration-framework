# Downstream v0.4.0 Upgrade Findings

## Evidence Identity

- Source repository: `C:\Github\YuChia\dotnet-mq-arch-lab`
- Final merged commit: `2eeddf392ca79deb4407c47d13ad53178015ba90`
- Upgrade workflow: `2026-07-18-ai-context-v0-4-upgrade`
- Workflow closeout commit: `b0039492ce9b517ef4e9f38383e062b5736f216f`
- Upgrade implementation commit: `21c6b61`
- Assessment: `ASM-20260718-001`
- Assessment commit: `65fe3f2`
- Published framework subject: annotated `v0.4.0` tag peeled to `5af1db672928f9d51f55fee04183ad27b79fb9f8`
- Intake date: `2026-07-18T21:39:19+08:00`

This file is a provenance-bound summary of external implementation evidence. It
is not a copied assessment, does not modify the downstream repository, and does
not replace source-side reproduction or independent verification.

## Finding PKG-001

The published migration guide declares governed `v0.3.0` as the supported
source and instructs the operator to supply its `files.yaml`. The tagged package
builder instead emits:

```yaml
from:
  version: null
  manifest_sha256: null
operations:
  - id: clean-install-0001
    kind: add
```

The apply library treats that identity as clean install and rejects a supplied
previous manifest with:

```text
clean install must not supply a previous files manifest
```

The downstream workflow therefore created a workflow-local deterministic
metadata adapter. It derived 166 operations from the governed inventories:

- 82 replacements
- 41 additions
- 28 removals
- 15 target reconciliation items

The official planner applied 151 byte-safe operations. The remaining 15 were
explicitly reconciled so target truth and local governance remained protected.
This workaround proved that the inventories are sufficient, but it is not part
of the published package and cannot be required of every downstream maintainer.

## Finding PKG-002

The profile packages `.ai/scripts/**`, and the packaged README lists these
commands as directly runnable:

```text
python .ai/scripts/tests/test_ai_context_version_governance.py -v
python .ai/scripts/tests/test_ai_context_packaging.py -v
```

The packaged `check-all.sh` also selects version-governance and package-builder
tests as required. The package intentionally excludes source release records
and history, while the relevant builder module is not available in the form
expected by the test. Direct downstream execution produced missing Git
refs/release records and `ModuleNotFoundError`.

The downstream target retained applicable manifest validation and safe-apply
tests while overriding the invalid source-only selections. Its full target gate
then passed 19/19. `ASM-20260718-001#AIC-001` classified the target residual as
MEDIUM because the override prevented a broken target gate; at the source
release boundary this is HIGH/P0 because every package inherits the mismatch.

## Downstream Completion Evidence

- Progressive upgrade: v0.1.0 to governed v0.3.0 to v0.4.0
- Package accounting: 568 paths, 503 exact framework matches, 65 explicit
  target overrides, zero missing package paths
- Target validation: 19/19 required checks
- Analyzer tests: 49/49
- Configuration validation: 2/2
- BuildingBlocks tests: 5/5
- Solution build: zero errors; six pre-existing nullable warnings

## Source-Side Reproduction Anchors

- `releases/v0.4.0/migration-guide.md`
- `releases/v0.4.0/release.yaml`
- `.ai/scripts/ai_context_package.py`
- `.ai/scripts/ai_context_package_apply.py`
- `.ai/distribution/profiles/dotnet-backend.yaml`
- `.ai/scripts/check-all.sh`
- `.ai/scripts/README.md`

The implementation session must reproduce both findings from immutable source
refs before editing, then use disposable repositories and extracted package
assets for acceptance.
