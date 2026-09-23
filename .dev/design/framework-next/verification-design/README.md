# Focused verification design

Design-only delivery for [#364](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/364),
program #322 / P7-A, from `171f33474f88888fbe853600de04bfe9c5716b25`.
All proposed product execution is **deferred-by-owner**, U001, owner **program
#322 coordinator / P7**; next action is to reconcile this design with #365 and
assign bounded implementation. Nothing here enables CI, activates a project,
changes source rules or closes another Issue.

Read [selected checks](selected-checks.md) for cases/commands and
[Windows pilot](windows-pilot.md) for concrete proposed bindings. Authority:
[U001](../../../standards/FRAMEWORK-REDESIGN-EXECUTION-OVERRIDE.md),
[P7 assignment](../p7-design-handoff.md), actual
[maintenance handoff](../managed-installation/handoff.md) /
[P7 cases](../managed-installation/p7-cases.md), and
[source adoption](../source-adoption/README.md). This design consumes #361's
Lesson selection and separate recovery responsibilities; its historical missing
#359/#346/#347 dependencies and old counts are superseded by current source.

## Current subject and ownership

Direct metadata/manifest/Git reads at the starting commit give 18 implemented
packages, 113 payload members, no required/optional skill dependencies, one Codex
adapter and seven complete profiles. Counts exclude generated entries and the
three candidate metadata documents; they are declarations, not built results.

| Profile | Packages / generated entries | Payload members |
| --- | --- | --- |
| lesson-minimal | 1 | 9 |
| knowledge | 3 | 26 |
| work-management | 3 | 28 |
| engineering | 10 | 53 |
| collaboration | 16 | 107 |
| source-repository | 15 | 99 |
| context-maintenance | 2 | 6 |

Lesson is 0.2.0; the other 17 packages are 0.1.0. Source-repository is
collaboration minus local-backlog. Context-maintenance is an independent complete
selection, not an overlay; applying it must not imply union with ordinary packages.

A format has one owner even where several consumers need it. Tests invoke that
owner's reader, then independently compare observable outputs to inputs; they
must not create a second production parser or a new evidence registry.

| Contract | Producer / sole semantic reader | Verification responsibility |
| --- | --- | --- |
| Metadata 1/2/3 and package member closure | Package author; `src/distribution/package.py::load_package` reads it | Distribution owns metadata union, resource/operation/schema identity and references. Current packages exercise v2/v3; one minimal synthetic v1 input, no historical release matrix. |
| Manifest/profile v1, Git blobs, adapter | `distribution.selection.select`, `git_source.GitSource`, `codex.project_entry` | Exact seven selections, versions, modes, installed links/destinations; no optional auto-selection or config resolution. |
| Candidate selection/files/build v1 | `distribution.assembly.assemble`; installation state's `_candidate_documents` consumes live candidate and captured objects | Actual emitted bytes, content identity and completion last. Recovery reuses this reader and package owner. Never trust outcome alone. |
| Lock/operation/API v1, EnginePin | Installation modules and fixed `src/tools/maintain_framework.py`; `_lock_bytes` is the shared lock reader | Installer owns plan/apply/recover, complete ten-file pin, native coordination/publication, preservation and truthful failure. It never launches a skill. |
| Config 2 envelope/precedence | Project owns JSON; shared contract is [P3](../p3-shared-contract.md), implemented by each package's own binding reader | Common input table against each configured tool; no eighth config tool/shared runtime. Lesson alone also reads closed config 1. |
| Seven record families / views | Respective package schema, producer and public reader below | Producer output round-trips through the same owner's actual interface. Views are result-only; project records are outside installed ownership. |
| CBF structural result | `problem-frame-author` produces `problem-frame.cbf.structural-result@1.0.0`; compliance instructions consume it | Exact digest and complete criterion inventory; not another persisted family or runtime compliance verdict. |
| Instruction methods | Eleven null-config packages plus CBF's instruction arm | Metadata/reference reachability and bounded task observations; no invented stores, schemas, scripts or config. |

| Family | Sole record owner and tool under `src/skills/` |
| --- | --- |
| Lesson | `lesson`: `lesson.record@1.0.0` read-only, `@2.0.0` writable; `lesson/scripts/lesson.py` |
| ADR | `adr`: `adr.record@1.0.0`; `adr/scripts/adr.py` |
| Standards promotion | `standards-promotion`: `standards-promotion.record@1.0.0`; `standards-promotion/scripts/standards_promotion.py` |
| PR | `pr`: `pr.record@1.0.0`; `pr/scripts/pr.py`; `scripts/github.py` is this family's separate provider surface, not an eighth family |
| Local backlog | `local-backlog`: `local-backlog.record@1.0.0`; `local-backlog/scripts/local_backlog.py` |
| Workflow | `software-development-orchestrator`: `software-development-orchestrator.record@1.0.0`; `software-development-orchestrator/scripts/workflow.py` |
| CBF | `problem-frame-author`: `problem-frame.cbf@1.0.0`; `problem-frame-author/scripts/problem_frame.py` |

Package scripts remain self-contained; no cross-package private import in
production or acceptance tests. Distribution is source tooling, not an installed
skill dependency. AST import observations are selection evidence, not proof that
dynamic execution is isolated.

## Layers and what they establish

1. **Contracts:** selected-source/member/reference checks, owner parser/semantic
   tests and tiny synthetic negatives. Seven profiles are read as declarations;
   only Lesson is assembled for the first integration pilot.
2. **Public tools:** subprocess requests with selected package resources, bounded
   records and real read-back. Success establishes only that operation on its
   input/backend. Fixture evidence/actors stay synthetic.
3. **Native installation:** real processes, Windows file operations, exclusion,
   complete capture, bounded interruption/recovery. Instrumented seams are labelled
   separately from an unmodified public invocation.
4. **Lesson pilot:** builder -> candidate -> installed entry -> config -> Lesson
   candidate/readers, with source/Git byte preservation and persistent backup.
   Installer readiness stays `not-assessed`; fresh Codex route observation and
   project activation are separate decisions.
5. **Independent/provider acceptance:** separately assigned review of the selected
   immutable implementation and authentic provider results. Local tests, prose,
   fixture grants or integrated design cannot satisfy this layer.

No universal pass flag. Retain command, selected commit/raw input identities,
host/runtime/backend, case, outcome, stdout/stderr/exit, actual counts and limits
in the existing owning workflow report. Failure, unavailable runtime, not-observed
interruption, partial mutation and deferred work remain visible.

## Bounded implementation sequence

Proposed work units, not created Issues or execution authority. Coordinator
supplies one fixed starting commit and one writer per assigned worktree.

| Slice | Exclusive proposed implementation responsibility | Dependency / exit |
| --- | --- | --- |
| V1 source contracts | `tests/framework_next/run.py`, `support.py`, `test_contracts.py`; distribution fixes only by explicit assignment | First. Own runner/root helper and shared input table; verify 18/113/7, metadata union, candidate closure and null-config projection. Publish helper interface once. |
| V2 public families | `tests/framework_next/test_knowledge.py`, `test_work.py`, `test_cbf.py`, `instruction-observations.md` | After V1 helper, alongside V3. Seven round-trips/negatives; provider simulations clearly labelled. Return defects to package owner; no unrelated refactor. |
| V3 Windows installation | `tests/framework_next/test_installation.py`, `native_windows.py` | After V1; actual #359 engine. Native cases, deterministic fault tests, public interruption observation and residuals. No expanded recovery format. |
| V4 Lesson pilot | Later task-owned workflow plus explicitly selected isolated project, backup and output roots | After V1, Lesson part of V2 and selected V3. Actual reconciled source and fresh Codex entry; root adoption follows a separate window. |

#365 owns pipeline/context/settings and source-policy dispositions. It may bind
V1/V2/V3 by purpose; coordinator reconciles commands/prerequisites before
implementation/restoration. No CI context or setting is adopted here. Broader
profile activation waits for applicable V2 and instruction observations; Lesson
success does not accept all 18 packages.

## Legacy overlap and remaining decisions

Live read-only observations on 2026-09-23: #274, #275 and #308 remain OPEN.

- [#274](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/274): retain zero-config/explicit opt-in and logical/native separation. Keep legacy mixed-suite classification with its owner; do not classify every old fixture before V1 or reuse the old suite wholesale.
- [#275](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/275): retain measurement-first and isolation lessons. New runs report logical bytes/files/processes; old package-apply baselines and three-run performance comparisons are not P7 prerequisites. No speed, SSD-wear or token-saving claim is available.
- [#308](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/308): #365 should disposition legacy resolver/subject-manifest surfaces. New exact member lists reject missing required files and represent optional absence explicitly; do not import old glob/history/evidence-reuse machinery. This design does not implement or close #308.

Coordinator selects final immutable implementation, actual provisioned interpreter,
proposed roots and trial authority, then reconciles #365. Root adoption and CI
restoration need separate concrete owner decisions. M01 remains **unassigned**
without an actual selected config-1 input. Unsupported roots are refused and
reported, never silently rerouted. Broader recovery and provider writes are
separate scope.
