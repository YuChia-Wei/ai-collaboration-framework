# Python Entrypoint Prerequisite Inventory

## Evidence Metadata

- `generated_by`: `OpenAI Codex repository-native inventory`
- `generated_at`: `2026-08-02T10:39:48+08:00`
- `updated_at`: `2026-08-02T10:53:29+08:00`
- `source_revision`: `2263744bb2dc876f8077547e961fc68be28b0074`
- `source_branch`: `codex/2026-08-02-python-prerequisite-diagnostics`
- `issue`: `https://github.com/YuChia-Wei/ai-collaboration-prompts-dotnet-backend/issues/69`
- `baseline_finding`: `ASM-20260730-001#AIC-004`

## Scope And Method

- Included tracked Python files under `.ai/scripts/**` and `.ai/assets/skills/*/scripts/**`.
- Classified direct execution by a repository-native `git ls-files` inventory plus a direct check for each file's `__main__` path.
- Classified portability from `.ai/distribution/profiles/dotnet-backend.yaml`, including its source-only exclusions.
- Classified current prerequisites from direct import lines and direct local-module import chains.
- Checked active command and explanation surfaces in root entry documents, `.ai/scripts/README.md`, `.ai/distribution/templates/INSTALL.md`, skill specs/references, `.dev/standards/**`, `.dev/guides/**`, `.dev/releases/**`, `.github/workflows/**`, `.ai/scripts/check-all.sh`, and `.ai/scripts/shell-assets.yaml`.
- Excluded historical workflow and assessment references from support classification, except for the selected baseline finding.
- Excluded product `src/**` and `tests/**` trees; this repository has no relevant product implementation in scope.

The Codebase Memory MCP index was checked first. Its current index reported no Python matches below hidden `.ai/**` paths, so it was used only as a failed discovery probe. Counts and conclusions below were verified with tracked paths, direct file reads, manifests, and tests under `AICTX-EVIDENCE-001`.

## Reproduction

From the repository root in PowerShell:

```powershell
$Tracked = git ls-files -- '*.py' |
  Where-Object { $_ -match '^\.ai/(scripts|assets/skills)/' }

$Entrypoints = foreach ($Path in $Tracked) {
  if ((Get-Content -Raw -LiteralPath $Path) -match '__name__\s*==\s*["'']__main__["'']') {
    $Path
  }
}

$Tracked.Count
$Entrypoints.Count
($Entrypoints | Where-Object { $_ -notmatch '/tests/' }).Count
($Entrypoints | Where-Object { $_ -match '/tests/' }).Count
```

Recheck classification against:

```powershell
Get-Content -Raw .ai/distribution/profiles/dotnet-backend.yaml
Get-Content -Raw .ai/scripts/shell-assets.yaml
Get-Content -Raw .ai/scripts/README.md
```

## Inventory Summary

| Category | Count | Contract relevance |
| --- | ---: | --- |
| Tracked Python files in scope | 74 | Complete tracked inventory for the selected roots. |
| Direct `__main__` entrypoints | 70 | Every file can be invoked as a command. |
| Production CLI entrypoints | 25 | Primary candidates for a user-facing prerequisite contract. |
| Direct test CLI entrypoints | 45 | Explicitly runnable developer commands, often called by the aggregate runner. |
| Import-only support modules | 4 | Must not become independent user-facing commands merely because a shared bootstrap imports them. |
| Portable production CLIs | 12 | Projected into downstream packages or retained as published compatibility paths. |
| Source-only production CLIs | 13 | Maintainer, release, evaluation, migration, or source-governance operations. |
| Production CLIs requiring PyYAML directly or indirectly | 23 | Can currently fail at import before a common diagnostic. |
| Standard-library-only production CLIs | 2 | Still need a Python floor check if the contract covers all production CLIs. |
| Production CLIs importing `tomllib` | 1 | Fails on Python 3.10 or older before `main`. |

## Portable Production Entrypoints

1. `.ai/assets/skills/software-development-orchestrator/scripts/validate-software-development-orchestrator-acceptance.py`
2. `.ai/scripts/plan-ai-context-package-apply.py`
3. `.ai/scripts/validate-ai-context-target.py`
4. `.ai/scripts/validate-ai-context.py`
5. `.ai/scripts/validate-assessment-artifacts.py`
6. `.ai/scripts/validate-dependency-versions.py`
7. `.ai/scripts/validate-file-disposition-manifest.py`
8. `.ai/scripts/validate-git-commits.py`
9. `.ai/scripts/validate-shell-assets.py`
10. `.ai/scripts/validate-software-development-orchestrator-acceptance.py`
11. `.ai/scripts/validate-workflow-artifacts.py`
12. `.ai/scripts/validate-workflow-handoff.py`

The compatibility entrypoint delegates to the skill-owned acceptance validator and therefore inherits its PyYAML import failure unless the prerequisite check runs before delegation.

## Source-Only Production Entrypoints

1. `.ai/assets/skills/ai-context-upgrader/scripts/compare-ai-context-versions.py`
2. `.ai/scripts/build-ai-context-package.py`
3. `.ai/scripts/measure-ai-context-load.py`
4. `.ai/scripts/plan-github-backlog-migration.py`
5. `.ai/scripts/prepare-ai-context-release.py`
6. `.ai/scripts/render-ai-context-release-notes.py`
7. `.ai/scripts/validate-ai-behavior-evaluation.py`
8. `.ai/scripts/validate-ai-context-package.py`
9. `.ai/scripts/validate-ai-context-release-state.py`
10. `.ai/scripts/validate-ai-context-versions.py`
11. `.ai/scripts/validate-repository-config-contract.py`
12. `.ai/scripts/validate-skill-transition.py`
13. `.ai/scripts/validate-source-governance.py`

These are excluded from the downstream payload but are real maintainer or CI operations. Several write output or release/package artifacts, so excluding them preserves a source-side diagnostic inconsistency.

## Current Behavior And Risk

### Interpreter absent on the host

On the current Windows host, `python` and `python3` resolve to Windows App Execution Alias executables, but no host Python runtime is installed. A direct `python <entrypoint>.py` command therefore fails in the operating-system launcher before the repository can execute a Python bootstrap or print its own message.

This creates two distinct diagnostic layers:

1. A non-Python shell or PowerShell launcher can detect that no usable interpreter exists, name the attempted commands, state the Python 3.11+ requirement, and stop before invoking any Python entrypoint.
2. Once a Python interpreter starts, a shared Python bootstrap can reject an unsupported version or missing dependency before importing PyYAML, `tomllib`, local modules, or write-capable code.

Consequently, standardizing Python preambles alone cannot make a missing-interpreter direct command repository-owned. Full coverage of the observed machine state requires the approved invocation contract to include a non-Python launcher or aggregate runner; raw direct `.py` invocation remains subject to the operating system when no Python executable exists.

### Aggregate runner

`.ai/scripts/check-all.sh` resolves `AI_CONTEXT_PYTHON`, then `python`, then `python3`, and accepts only Python 3.11 or newer. Its failure message states the version floor and points to `requirements.txt`, but it does not currently report the selected executable, detected unsupported version, missing dependency identity, or a structured pre-mutation result.

### Package planner

`.ai/scripts/plan-ai-context-package-apply.py` already catches a missing `yaml` import, names `PyYAML==6.0.3`, prints `python -m pip install -r requirements.txt`, exits with status 2, disables bytecode before importing its local apply module, and has extracted-package coverage using `python -S`.

This is the strongest existing direct diagnostic, but it remains a one-off contract. It does not check/report an unsupported interpreter before dependency imports, report the selected executable/version, or emit an explicit pre-mutation status.

### Other direct production CLIs

- Most PyYAML-bearing scripts import `yaml` at module load and expose the interpreter's raw `ModuleNotFoundError` when the dependency is absent.
- `validate-ai-context.py` imports `tomllib` before `main`, yielding the interpreter's raw missing-module failure on Python 3.10 and older.
- Indirect entrypoints such as `validate-ai-context-target.py`, the package builder/validator, the backlog migration planner, and the compatibility acceptance validator can fail while importing a local module that imports PyYAML.
- Standard-library-only CLIs can currently run and report success below the documented Python floor unless they happen to use an unavailable language/runtime feature later.

### Mutation boundary

- The downstream-critical write path is `plan-ai-context-package-apply.py --apply`; `--plan-output` also writes a plan file.
- Source-only build, measurement, backlog migration, release-note rendering, and deterministic evaluation commands can write outputs.
- Importing local Python modules may create `__pycache__` unless bytecode is disabled early enough. The existing package planner explicitly guards this because an extracted envelope is checksum-governed.
- Read-only validators do not mutate their subject by design, but they can still make an unsupported validation-success claim unless the Python floor is checked first.

## Work Families Implied By The Finding

1. Define and register the supported Python entrypoint boundary.
2. Define a standard diagnostic schema: executable, detected version, required floor, dependency/import package, sanctioned recovery command, exit status, and pre-mutation state.
3. Choose a delivery architecture that separates non-Python absent-interpreter detection from Python-level version/dependency checks and works for root shared scripts, skill-owned scripts, compatibility entrypoints, extracted packages, and installed targets.
4. Reorder imports and bytecode behavior so the diagnostic executes before `tomllib`, PyYAML, local dependency modules, or target writes.
5. Preserve package projection and checksum behavior for the extracted envelope.
6. Add deterministic unsupported-version and missing-dependency tests, plus no-write assertions for write-capable paths.
7. Synchronize aggregate-runner parity, active command registries, package tests, documentation, and any compatibility contract affected by the selected boundary.
8. Run focused validation, package/apply regression checks, aggregate gates, and an independent post-remediation AI-context assessment.

## Boundary Options For D-001

### Option A — all production CLIs (recommended)

Cover all 25 non-test `__main__` entrypoints across portable and source-only surfaces. Keep the 45 direct test CLIs and four import-only modules outside the user-facing contract.

- Benefit: one understandable boundary for every maintained operation; closes both halves of the Issue's mixed scope.
- Cost: the largest production-code integration surface and the need to distinguish source versus extracted-package recovery text.
- Residual boundary: direct test commands may still show raw environment import errors, which would be documented as developer-test behavior rather than a supported runtime diagnostic.

### Option B — all executable Python files

Cover all 70 direct `__main__` paths, including 45 tests.

- Benefit: the literal strongest interpretation of every directly runnable Python command.
- Cost: substantially larger and noisier changes, or a mandatory test launcher; prerequisite behavior becomes coupled to each test module and compatibility test wrapper.
- Residual boundary: import-only modules remain outside the command contract.

### Option C — portable production CLIs only

Cover the 12 production entrypoints projected into downstream payloads or retained as portable compatibility paths.

- Benefit: smallest bounded change and strongest focus on downstream first-run experience.
- Cost: 13 source-only maintainer/CI operations remain inconsistent, including several write-capable commands; this only partially addresses the Issue's `scope:mixed` label and source-runner comparison.

## Current Conclusion Boundary

This inventory establishes candidates and impact only. No D-001 option has been selected, no implementation architecture has been approved, and no production file has been modified. The observed host state proves that an absent interpreter cannot be diagnosed by repository Python code; whether a supported non-Python launcher is added remains a D-002 owner decision.
