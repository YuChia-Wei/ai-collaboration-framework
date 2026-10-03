# Local validation and handoff

Created/updated: `2026-10-03T08:39:51+08:00`.
Source: `89815900f7d0aa05a53eb9902f8883fdc87649de` on
`codex/2026-10-03-sub-agents`; diff base
`37a588c8c0b6f5e760079c563e71d742af8f962d`.
All commands below ran locally on Windows. No hosted result is claimed.

## Focused checks

`python -I -B .github/scripts/check-source-change.py --base 37a588c8c0b6f5e760079c563e71d742af8f962d --head 89815900f7d0aa05a53eb9902f8883fdc87649de`
passed in 47.28 seconds: content/whitespace plus schemas 43, distribution 44,
source 49 and platform 26 tests; 162 total, zero errors, failures or skips.
Raw result: `artifacts/sub-agents-source-gate-1.json`.

`python -I -B tests/run.py --suite release` with host permission passed 26 tests,
zero errors, failures or skips. Raw log:
`artifacts/sub-agents-release-host-final.log`. The immediately preceding
default-sandbox run failed due to temporary-root access; its separate log
`artifacts/sub-agents-release-final.log` remains retained. Earlier sandbox,
incomplete-fixture and alias-guard failures are preserved in the plan and are
not counted as passes.

The final record commit selects the same fresh Source change gate with its
actual full HEAD. The implementation evidence below remains bound to the
implementation commit; no catalog source identity is rewritten after building.

The initial record-head gate on `cf407f6b22293559fdcf99e816107b1b46370339`
failed in 31.322 seconds with two completed-task metadata errors and no test
dispatch. It is retained as
`artifacts/sub-agents-source-gate-record-failed.json`. Correct the records to
the selector's `result_summary` / `finding_status: addressed` contract and run
fresh checks on the subsequent immutable record commit. The independent
reviewer also blocked the initial final-head binding for this defect.

## Physical assembly and isolated installation

Parent executed `python -I -B artifacts/verify-sub-agent-delivery.py` and
`python -I -B artifacts/verify-sub-agent-install.py`, with host permission.
These ignored scenario drivers use the real committed CLI/API, not mock
assembly/installers. They construct an independent Engine 2 pin from all 24
declared engine files, compare each committed file's exact bytes and SHA-256,
then invoke `tools/build-catalog.py` with `--commit` equal to the source above,
`--engine-pin` that independent pin, and explicit output/scratch roots.

Assembly's `--release-version 0.19.0-rc.5` is a **verification-only artifact
label**, not a release allocation, tag or publication decision. Catalog identity:
`catalog:1:0.19.0-rc.5:89815900f7d0aa05a53eb9902f8883fdc87649de:4cc96857eb5f0eefb25ca63bc0489a09cffcac5e8c1e38fe7662472a5ac211fb`.

The standalone built engine executes `tools/derive-subset.py` with that catalog
identity, `--preset sub-agents --preset-version 0.1.0` and the independent pin;
source-free derivation passed. Subset identity:
`subset:3:0.19.0-rc.5:89815900f7d0aa05a53eb9902f8883fdc87649de:acfadac60c576ca29deee1439a287104445f8b2f4e11dcc2cf7228d4fd8c6c13`.
All 31 subset-member hashes were checked: 25 canonical package files and six
Codex projections. Claude projection is covered by focused contract tests,
not this Codex-only physical preset scenario.

Owned scenario root: `C:\Windows\Temp\a434-8nlopsnq`, using short standard
temporary storage within the existing Windows path budget. No global TEMP/TMP
or fixture acceleration setting changed. Catalog/engine/subset directories,
project `p`, collision project and raw evidence remain retained; cleanup was
not selected.

The actual built `src/tools/maintain_framework.py` API planned 31 additions and
applied them to the new isolated project. Apply passed (6.907428 seconds), and
inspect reported `managed-bytes-consistent`; all 31 installed hashes matched.
Existing `.codex/config.toml` and `.codex/agents/custom.toml` stayed byte-identical.
Changing a managed profile caused inspect to detect drift; restoring its bytes
returned a consistent result. A same-byte unowned profile at the exact managed
destination refused planning with `unowned-collision`, without creating a lock
or changing that profile.

Raw results: `artifacts/sub-agents-physical-result.json`,
`artifacts/sub-agents-installation-result.json`, and requests/stdout/stderr in
`artifacts/sub-agents-physical/` (including the independent engine pin).
These logs are ignored local evidence; this tracked report preserves outcomes
and identities for handoff without declaring them published artifacts.

## Residual boundaries

Independent review disposition is in `review.md`. Local configuration delivery
is complete. Main integration, online Issue closure/Project mutation, push,
PR, hosted CI, tag/release/publication and real downstream adoption were not
performed. Existing earlier local manual/removal commits remain preserved.
No runtime agent invocation, model access or role behavior acceptance is claimed.
Recovery, breaking reinstall and the full retained native/P7 obligations are
outside this newly selected isolated scenario. Source-gate admission remains
`not-evaluated`, including its owner-selected native-acceptance requirement.

The human maintainer owns the next integration/publication decision. Use
`Refs #434` because that online work remains open pending separately selected
provider checks and acceptance; local workflow completion does not close it.
