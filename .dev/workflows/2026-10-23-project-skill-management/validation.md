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

## Remaining acceptance at this checkpoint

- Build the current pinned catalog/engine from one clean fixed commit and use
  its public manager for registration, explicit same-byte adoption, multi-file
  readback, original/prefixed framework routing, protected upgrade/deselection,
  legacy migration and precise detachment.
- Observe Codex native `skills/list` and native filesystem reads in that
  consumer without a model turn. This proves discovery/readability only.
  Claude native discovery and actual skill behavior remain separately unverified.
  The protocol is documented in the official
  [Codex app-server reference](https://developers.openai.com/codex/app-server#skills);
  local CLI 0.163.0 generated the actual request schema used by the probe.
- Complete independent scoped read-only review of the clean fixed implementation
  under code-reviewer, covering ownership, path, installation and recovery.
  Record findings and affected re-review without repeating unchanged conclusions.

No pending item in this section is a passed acceptance criterion.
