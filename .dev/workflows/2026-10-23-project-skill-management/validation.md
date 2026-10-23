# Project skill management validation

## Subject, authority and evidence boundaries

The implementation starts from main
`1f473ecdb5a7544233299dd69bc6376a43a6c912` on
`codex/2026-10-23-project-skill-management`. Feature #482 and Story #484 were
updated online before implementation, following the owner's ordered instruction.
The implementation sub-agent was explicitly invoked as `gpt-6.1-sol / medium`
with fresh bounded context through the registered project bounded-general-worker
profile. The parent remained read-only in the worktree until the worker returned
ownership. The parent integrated documentation and the remaining compatibility
fixture correction afterward.

This is source implementation evidence. The local package version will be a
commit-derived `0.0.0-rc.*` snapshot, not a published release. No source-project
self-installation, account login, paid model test, transport or administrative
closure is implied. The separate `F:/AICF-Release-Preview` manual-review snapshot
from #487 is unchanged.

## Validation selection

The changed registry and CLI require behavior checks for multi-file projection,
hash/path boundaries, optional framework metadata, adoption, managed collision,
precise detachment, baseline retention, three-way comparison, explicit routes,
interruption and completed replay. The current engine closure changes from 27 to
29 files, so the directly affected catalog, adapter, maintenance, historical
artifact/lock, layout and loader checks are selected. The new module is included
in the existing hosted distribution suite.

Tests ran with existing `F:/aicf482/tmp` as process-local TEMP/TMP and asserted
`tempfile.gettempdir()` resolves to that exact path. F: was verified as an NTFS
RAMDRIVE with sufficient free space. Fixture roots are canonical resolved paths.
No machine-wide environment setting changed. The parent normalized only changed
source/test files to canonical LF for Git-bound packaging; this did not change
Python semantics or select another behavioral run.

## Actual focused checks and retained failures

| Check | Actual outcome | Disposition / evidence |
| --- | --- | --- |
| Initial new skill tests | 15 executed; 1 CLI fixture failure | Fixture used a fictional source commit and correctly failed engine verification. Repaired to actual HEAD; targeted CLI rerun passed. |
| Skills, sub-agent registry, layout, naming, distribution contracts and loader | 99 executed in 30.486 s; 1 failure | Old layout test expected current closure count 27. Added historical 27 and current 29 expectations; `skill-focused-1.log`. |
| Affected layout and naming after repair | 18 passed | Also added the old27/current29 identical wrapper/inventory regression after author inspection found the generator-convention boundary; `skill-compat-repair.log`. |
| Skills plus test-runner checks at that revision | 20 passed | Confirms runner registration; `skill-focused-final.log`. |
| Framework binding/resource-budget and collision boundaries | 2 passed | Dotted canonical IDs and installer-sized managed resources retain their actual contracts; `skill-route-boundaries.log`. |
| Final skill module, including record retention | 18 passed in 6.001 s | No failures, errors or skips; `skill-retention-final.log`. |
| Remaining distribution modules | 54 executed in 8.147 s; 1 failure | The old installed-lock fixture's allowed tuple omitted historical27. Product readers already accepted it; `remaining-distribution.log`. |
| Corrected old installed-lock case | 1 passed in 0.691 s | Added `LAYOUT_ENGINE_FILES` to that fixture's historical tuple; arbitrary closures remain rejected; `previous-lock-repair.log`. |
| Author syntax / whitespace inspection | Passed for the worker's nine changed files | Parent also runs changed-file `git diff --check` after documentation integration. |

Logs above are bounded transient evidence under `F:/aicf482/`; durable outcomes
and limitations are recorded here. Failed attempts remain failures and are not
relabeled by subsequent success. No full default suite or provider CI was run
for this local implementation stage. The PR hosted gate remains required if
transport is separately selected.

The actual harness form was `python -I -B -` from the repository root, with
`tests` explicitly inserted in `sys.path`, `unittest.defaultTestLoader` and
`unittest.TextTestRunner(verbosity=2)`, and a nonzero exit on unsuccessful result.
The final 18-test selection was `framework_next.test_skill_registry`. The
99-test selection was:

```text
framework_next.test_skill_registry
framework_next.test_subagent_registry
framework_next.test_project_layout
framework_next.test_skill_naming
framework_next.test_distribution_contracts
framework_next.test_engine_source
```

The remaining 54-test selection was:

```text
framework_next.test_contracts
framework_next.test_adapters
framework_next.test_maintenance_contracts
framework_next.test_distribution_versions
framework_next.test_subagent_policy
```

Only the affected test was rerun after the parent's fixture correction:
`framework_next.test_subagent_policy.CompatibilityTests.test_real_previous_installed_lock_remains_readable_but_arbitrary_closure_is_rejected`.

## Isolated old consumer starting point

The actual packaged 27-file engine at source
`546c1041959ae7209d7afe758012bd34afc72838` was verified by its independent pin.
Its public `derive-subset.py` and `maintain_framework.py` plan/apply installed
`adr-author` and `test-designer`, both adapters, original naming, into the new
`F:/aicf482/consumer`. Each subprocess exited successfully and apply returned
`applied`. The resulting old lock SHA-256 is
`4b2d434d7dc532c34a58cc8b8108de743eca71623dbf20d87d1aa4f2b560c708`.

This consumer includes a legacy-only `.ai/custom` root, an unknown binary file,
and a protected project AGENTS.md. It is the actual upgrade starting point,
not a mock or a claim that the new manager passed. Driver and results:
`F:/aicf482/seed-old-consumer.py`, `old-consumer-result.json`.

## Independent review and actual consumer correction

The independent read-only reviewer examined clean commit
`ff7c86b8e831fb98b4def274b9b3d84c93cea14b` against the selected main base under
the installed code-reviewer route and registered fixed-head-independent-auditor
profile, explicitly invoked as Sol/medium. It reported two actionable P2 findings:
completed same-registry repairs could reacquire a subsequently restored foreign
preimage, and comparison rejected valid dotted framework IDs/native entry names.

The same fixed commit produced an actual 29-file pinned catalog/engine. Its public
CLI passed explicit same-byte adoption, seven-member projection per adapter,
original/prefixed framework routing, managed collision rejection, upgrade and
optional deselection protection. The subsequent legacy migration failed before
renaming: its lock before/after hashes were identical, and apply incorrectly
inferred completion from equality with the after hash. This is a retained failed
attempt (`F:/aicf482/layout-apply.json`), not a passed migration.

The bounded repair adds a fresh UUIDv4 operation ID to each skill plan and a
canonical completion marker for each exact completed plan under `.ai/local`.
Fresh explicit repairs remain possible; completed-plan replay requires after
states even after other plans finish. Invalid markers and publication failure
remain visible. Comparison uses the existing framework ID grammar. Layout apply
infers completion from a lock hash only when that lock actually transitions.

The implementation worker was the sole tracked writer for these four source/test
files and returned ownership before parent integration. Its final focused run
passed all 39 tests (24 skill, 15 layout) in 38.009 s, with zero failures, errors
or skips. Log: `F:/aicf482/skill-layout-review-repairs-final.log`. The harness and
TEMP/TMP contract are the same as above. Targeted 5-test and intermediate 23-test
runs also passed; the 39-test run includes subsequent UUID/layout additions.

## Fixed repaired source and independent re-review

Clean commit `87b85018b32e43db1e705c33e7e54972cc1426eb` contains the repaired
implementation. The same independent reviewer examined only the two findings,
the equal-lock migration correction and directly affected ownership/recovery
paths against `ff7c86b8e831fb98b4def274b9b3d84c93cea14b`. It found R1 and R2
resolved, found the migration correction sound, and reported no new actionable
defect in that scope. HEAD and the clean worktree were unchanged before/after.
The reviewer inspected tests but did not execute them or access providers.

The repaired commit was built through the source catalog builder with a complete
independently constructed pin: all 29 engine members matched that commit's Git
bytes before execution. Actual output was `assembled`:

```text
catalog:1:0.0.0-rc.149225687528238:87b85018b32e43db1e705c33e7e54972cc1426eb:67350212628f5fa7cdd9495a1bb5c1e01dc448cf3eadb5f32bbd177154953b5a
```

The build is a local candidate, with no invented hosted-build provenance or
public release. Later record-only commits do not relabel this artifact's source.

## Actual public-CLI consumer results

The original RAM-disk consumer was continued through the repaired pinned
`derive-subset.py`, `maintain_framework.py`, `manage-sub-agents.py` and
`manage-skills.py`; it was not reset after its failed attempt. Process-local
TEMP/TMP remained `F:/aicf482b/tmp`. Commands from the repository root were:

```text
python -I -B F:/aicf482b/build-current.py 87b85018b32e43db1e705c33e7e54972cc1426eb
python -I -B F:/aicf482b/consumer-resume.py
python -I -B F:/aicf482b/consumer-detach.py
python -I -B F:/aicf482b/ntfs-native-setup.py
python -I -B F:/aicf482b/native-codex-probe.py F:/aicf482b/ntfs-native-spec.json
python -I -B F:/aicf482b/consumer-rename.py
```

Each completed successfully. The first consumer's lock after the repaired engine
upgrade was `f317efbc946e9bb8038a7aa198cc4f6ae5622ef1412fd22cef6567e76263298b`.
The actual legacy migration plan again had identical before/after lock hashes:
first apply now succeeded, changed registered references and hashes coherently,
preserved baseline history and opaque unknown bytes, and returned unchanged on
completed replay. Both project adapter routes and strict installed-resource
reading passed.

Same-registry repair succeeded with explicit foreign preimages; replay after
restoring those preimages was blocked without overwriting them. A fresh plan had
a distinct operation ID/hash and repaired the current state. Earlier completed
plans remained blocked after later plans completed. Dotted canonical candidate
IDs with original/prefixed native paths passed public comparison.

Precise detachment removed exactly 14 registered native files across both
adapters, retaining eight authoring members, the skill record, provenance,
baseline and unknown sibling. Recreating an old entry and replaying the completed
plan was blocked; the recreated entry survived. The framework lock stayed
unchanged, protected project input hashes matched, and strict installed-resource
reading still passed. The fixture intentionally retains that unowned entry.

A second small consumer was created by the same actual pinned manager in the
verified ignored `.dev/ai-context/local/native-skill-482` directory for native
discovery, following the filesystem limitation below. All seven projected Codex
member hashes matched the RAM-disk consumer. A later public-CLI rename moved the
Codex entry to `team-resource-demo-renamed` while retaining the Claude entry as
`team-resource-demo`; both explicit routes resolved. Exactly seven old registered
Codex members were detached; unknown siblings and baseline were preserved. The
synthetic script's sibling import printed `resource-closure-ok` through local
Python. This is a local resource execution check, not AI behavior evidence.

Bounded transient results are `F:/aicf482b/build.json`, `consumer-result.json`,
`detach-result.json`, `ntfs-native-setup-result.json`, `native-codex-result.json`
and `rename-result.json`. Durable outcomes are retained here; RAM-disk files are
not the sole continuation record.

## Native evidence and retained environment limit

The first native Codex attempt on the RAM-disk consumer returned no matching
entry. Its stderr reported `failed to walk skills root file:///F:/aicf482/consumer/.agents/skills`
with Windows `os error 1`. A diagnostic-only repeat confirmed no per-entry parse
errors and retained the same traversal failure. This is failed native discovery
on that fixture, not a successful RAM-disk runtime acceptance. It is preserved
in `F:/aicf482/native-codex-ramdisk-failure.json` and the matching stderr log.

The bounded workspace-filesystem consumer was then registered through the real
manager, not copied into native discovery by an untracked file shortcut.
Codex CLI 0.163.0 app-server returned one matching `team-resource-demo` entry with
`enabled: true` and `scope: repo`. Its native `fs/readFile` returned all seven
projected members with exact expected SHA-256 values, including nested references,
schema, template, script and sibling module. The probe used only initialize,
skills/list and fs/readFile; no thread/model turn, login or paid test was started.
The second consumer has its own Git root and is ignored by the source repository.
Test drivers and other temporary files remained on F:; the source project's
installed skill tree and global runtime configuration were unchanged.

The protocol was taken from the official
[Codex app-server reference](https://developers.openai.com/codex/app-server#skills)
and the installed CLI's generated schema. This establishes that selected native
entry's discovery and file readability at that observation. It does not establish
model selection of the skill, semantic correctness of its method, or the later
renamed entry's native discovery. Claude projections/routes were mechanically
verified; Claude native discovery and actual AI behavior remain unverified.

## Criterion coverage and delivery state

| Feature criterion | Observed coverage / limit |
| --- | --- |
| F-AC01 | Inspect exposes registry facts, deltas and resource observations; unknown/baseline cases covered by focused tests and actual consumer readback. References remain caller-supplied, not independently accepted semantic facts. |
| F-AC02 | Actual pinned inspect/plan/apply/compare/resolve executed. Skill operations retained framework lock bytes and respected installer ownership. |
| F-AC03 | Eight source members and seven resources per native adapter retained. Focused checks cover missing declared resources, metadata, hash, path/case aliases and unsupported content. Native reads and a local sibling import cover the representative resource closure. |
| F-AC04 | Same-byte unowned rejection then explicit adoption, managed collision rejection, unknown retention, actual rename/coexist and precise detachment observed. |
| F-AC05 | Focused tests cover union additions/deletions, conflicts and missing baseline; public comparison left routes unchanged. No coverage label performs owner acceptance or retirement. |
| F-AC06 | Complete project routes, original and prefixed installed framework bindings, required resource drift and deselected-framework rejection covered. |
| F-AC07 | Focused interruption/recovery tests plus actual completed repair/detach replay, fresh repair and retained history observed; R1 resolved by independent re-review. |
| F-AC08 | Historical readers/wrapper tests passed after retained fixture repairs. Actual legacy migration on the equal-lock boundary passed after the retained first failure. |
| F-AC09 | Real pinned public CLI performed registration, multi-file readback, upgrade, original/prefixed conversion, deselection, migration, rename and detachment in isolated consumers. |
| F-AC10 | Selected Codex native discovery and seven native file reads passed on the workspace filesystem. F: native walk failed; Claude native discovery and AI behavior remain unverified. |
| F-AC11 | Immutable initial review plus affected repair review completed with both P2 findings resolved and no new actionable finding in the repair scope. |

The authorized local implementation and selected validation are complete. This
does not close either online Issue or accept every future runtime/platform.
Feature #482 has no push, PR, merge, hosted CI, public publication or real-project
self-installation from this work. A separately authorized transport must use its
own current PR hosted gate; no existing local result substitutes for it.

## Online progress readback and publication limit

After the interrupted progress update, the owner explicitly requested fresh
readback of #482/#484, missing progress updates where needed, then completion of
local records and commit. Both Issues were read back as OPEN without the new
local-delivery progress section. Their previously revised implementation plans
remain present.

Automatic approval review rejected the #482 full-body progress update, citing
the local paths, branch/commit and internal validation/design details in the
payload. A safer concise progress-only addition removed those local identifiers
and retained the existing body, but review also rejected that action because
the API still replaces the complete Issue body and sends validation progress.
No alternate tool or indirect write was used to bypass the rejection. The same
progress has not been published to #484. Neither Issue's pending progress is
reported as updated successfully.

Local records and the authorized local commit can complete independently.
Publishing the prepared concise progress to both Issues now awaits explicit
owner approval of that exact external update; no state, labels or Project fields
are included. This provider-only limitation does not reopen implementation work
or erase the previously authorized and completed Issue-plan reconciliation.
