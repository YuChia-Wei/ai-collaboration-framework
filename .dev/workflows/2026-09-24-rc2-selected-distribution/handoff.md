# S3 local source delivery for Issue #406

Bounded implementation is complete. Source checkpoint: `f5f64d1bcdf4b777c9ee9cb53a734f09dc9052de`.
Worktree: `F:/framework-next/406`; branch: `codex/2026-09-24-rc2-selected-distribution`.
This handoff grants no behavioral admission, target adoption, publication or CI pass.

## Receiving and source identity

The clean core checkpoint `9c3270d4c0e00524345231936fb2c7a66f3ac6a9` preceded the
assigned no-fast-forward S5 receiving merge `0f573325a123419a27ddea2f17385b7d55de8139`
from coordinator commit `2ea6884701b92760266a610c1caede0ebf13201e`. Incoming accepted
skill/coordinator bytes were received unchanged. The final source correction is
`f5f64d1bcdf4b777c9ee9cb53a734f09dc9052de`; later handoff commits contain workflow data only.

[Source inputs](source-inputs.json) records 379 Git/raw-byte identities (2,318,140 bytes).
[Engine source](engine-source.json) records the complete 22-file closure, including
16 distribution modules, bootstrap, two artifact CLIs and all three templates.
[Direct checks](direct-checks.json) records 20 components, 350 catalog payload members,
235 S2 member matches, 17 S5 matches, five S4 renderer/template matches and all eight
preserved preset choices. These are source inventories, not built catalogs or bundles.
The .NET metadata stays exactly 247347 bytes within the unchanged 262144-byte cap.

The source-owned delta is enumerated in [task.json](task.json). Accepted `src/skills`,
`src/knowledge`, `src/adapters`, Codex and Claude renderer bytes are unchanged against
the coordinator input. The exact final HEAD/clean state is reported at terminal handoff;
no self-referential commit identifier is fabricated in tracked evidence.

## Acceptance and remaining execution

| Acceptance | Delivered source responsibility | Direct evidence / limit |
| --- | --- | --- |
| S3-A1 | Closed format parsing | Exact embedded S1 definitions, UTF-8/AST and direct source YAML/JSON; unknown/bool/duplicate cases authored. |
| S3-A2 | Immutable parent catalog | 379 raw Git input identities; 235 S2, 17 S5 and 5 S4 member/renderer/template matches. |
| S3-A3 | Explicit selection and presets | Eight exact prior skill/adapter lists preserved; knowledge empty; complete remains 18; no implicit save path. |
| S3-A4 | Source-free selected subset | Direct identity/owner/renderer dispatch inspection; synthetic empty/missing-selection cases authored; source-free execution not performed. |
| S3-A5 | Legacy read and unsupported write boundaries | Historical pins/constants and legacy renderer preserved; current legacy generator declares added bounded-data dependencies; no legacy execution. |
| S3-A6 | Independent verified engine 2/API 2 | 22-file closure agreement, direct global-symbol inspection and source inventory; isolated loading tests authored only. |
| S3-A7 | Bounded plan/apply/deselection | Direct ownership, old/new prefix, unknown sibling, protected and native boundary inspection; no actual plan/apply/deselect. |
| S3-A8 | Paired journal and recovery | Exact API/journal/phase contract; raw preimages/objects and distinct before/after sides; authored project-intent cases, no interruption/recovery execution. |
| S3-A9 | Project-owned intent boundary | No implicit save CLI; project_data_action none; exact staged object intents only; no target writes. |
| S3-A10 | Focused cases and truthful handoff | Direct AST/Git/hash/link/message checks performed; all tests, builders, native/runtime/formal/hosted/CI remain deferred-by-owner. |

Actual checks: direct UTF-8, 24 Python ASTs, production global-symbol inspection,
JSON/YAML parsing, exact S1 schema literal comparison, full source/raw SHA-256/mode
comparison, 154 active content links/seven heading anchors, Git scope/diff and complete
planned-message validation. No product module was imported or executed for acceptance.

All tests and parser, catalog/subset/engine building, installation, recovery, consumer,
Codex/Claude, target, native, legacy/formal/hosted/CI validation remain
`deferred-by-owner` under U001 to the program #322 coordinator / selected S6 / P7.
No full matrix, native expansion or target-gate waiver is implied. R1-R8 and all
stable/publication/portability obligations remain with their existing owners.

## Concrete S5/S6 entry points

[API 2 and journal 2](api2-maintenance.md) defines closed requests, transaction objects,
retained operation fields and all eight paired phases. [Request examples](request-examples.json)
contains complete request shapes and the 22 engine file rows. They are intentionally
non-admissible templates: replace roots, pins, current hashes and declarations using
actual selected inputs. False quiescence booleans must never be changed without a
fresh exact-scope caller declaration. No example was executed.

The ignored `.dev/ai-context/local/rc2-406/engine-pin-final.json` is produced only after
final commit/read-back; it binds that exact checkout HEAD and the tracked file hashes.
Recompute/reselect the pin after coordinator integration changes HEAD. A copied pin
is not approval, and the engine bundle branch must carry its exact engine.json/files.
The tracked inventories let the receiver reconstruct those pins without volatile-only evidence.

Commands after explicit S6 selection (absolute roots; no inferred directories):

```text
python -I -B ENGINE/tools/build-catalog.py --repository ENGINE --commit SOURCE_COMMIT --engine-pin PIN_JSON --release-version 0.19.0-rc.2 --output-root OUTPUT --scratch-root SCRATCH --engine-output-root ENGINE_OUTPUT
python -I -B ENGINE/tools/derive-subset.py --engine-pin PIN_JSON --catalog-root CATALOG --catalog-identity EXACT_CATALOG_ID --preset complete --preset-version 0.1.0 --output-root OUTPUT --scratch-root SCRATCH
python -I -B ENGINE/tools/derive-subset.py --engine-pin PIN_JSON --catalog-root CATALOG --catalog-identity EXACT_CATALOG_ID --selection SELECTION_JSON --output-root OUTPUT --scratch-root SCRATCH
```

The new artifact tools never save project configuration. A selected installation.json,
framework.json or root edit travels through the separately authorized paired intent.
PowerShell stdin invocation after request preparation:

```powershell
Get-Content -Raw -Encoding UTF8 REQUEST_JSON | python -I -B ENGINE/src/tools/maintain_framework.py
```

[The S5 seam](s5-interface.md) gives the isolated host recipe and exact
`read_installed_resources(project_root, expected_lock_sha256, authorities)` arguments
and result. It verifies installed raw identity/project-input pins and returns resource
metadata plus exact bindings; S5 owns task-scoped loading, selector interpretation,
coverage and target adoption. It is not another public maintenance operation.

Selected S6 may begin with the two narrow authored files and the directly affected
engine-source suite, without widening unchanged helper caps:

```text
python -I -B tests/framework_next/test_rc2_distribution.py
python -I -B tests/framework_next/test_rc2_maintenance.py --output-root EXPLICIT_DISPOSABLE_FIXTURE_ROOT
python -I -B tests/framework_next/test_engine_source.py --output-root EXPLICIT_DISPOSABLE_FIXTURE_ROOT
```

No `--public-entry`, actual native trial or full runner is selected here. The tests
include synthetic descriptors/objects; they cannot establish real artifact, install,
interruption or runtime acceptance. Coordinator must select actual source-free subset,
legacy read, paired finish/restore and marker interruption observations separately.
Use short explicit artifact/operation roots within the existing 240-unit path budget.

## Retained failures, limits and ownership

Automatic approval review rejected the initial outgoing callback; no message was sent
and none is retried. It also rejected the first engine/maintenance edit batch until
the user's direct bounded approval; that approved batch was then applied. A proposed
CLI --save-selection capability was rejected and omitted entirely. No approval block
remains for this local implementation.

Static findings and repairs are retained in [workflow-plan.md](workflow-plan.md),
including the missing engine constant, identical-lock project-side ambiguity, exact
saved-selection typing and six inert C# example false links. No behavioral failure
was hidden behind the later direct checks. Native path/filesystem feasibility,
interruption behavior and old/new runtime discovery remain unexecuted risks.

Recovery preserves the existing guard and preparation residue; it is not cleanup or
whole-project reconstruction. Exact restored project preimages may retain an earlier
project-input mismatch; consumers report that drift and readiness remains not-assessed.
Target selector/admission adapters and source/target adoption are separate owner work.

No source/target self-adoption, remote push, PR, online merge, Issue/Project mutation,
new tag/Release or CI restoration occurred. No shared coordinator record was authored
by S3; the accepted incoming records only arrived through the assigned merge. No shared
index row is written. Receiver may link this handoff from its own tracking record.
Exclusive writer ownership is released with the final clean-HEAD handoff in this task.
