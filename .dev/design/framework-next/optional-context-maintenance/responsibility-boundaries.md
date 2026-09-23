# Responsibility boundaries and semantic state

This future portable design does not change current source authority.
Evidence IDs resolve in the pinned evidence linked from the [entry](README.md).
Code descriptions are static observations, not execution results.

## What moves, what stays

| Responsibility | Actual evidence at the subject | Future owner/disposition |
| --- | --- | --- |
| Scoped read-only context analysis | E01 auditor spec and E02 output already support transient analysis, allowlists and product-code exclusions. | Optional auditor retains evidence, uncertainty and coverage. No forced two independent runs for every question. |
| Bounded context proposal/edit | E03 governance currently combines placement, routing, ledger, migration and remediation. | Optional governance keeps project proposals/authorized edits; no implicit global/source authority. |
| Assessment persistence | E04 source policy owns locator/index/ASM identity and frozen conclusions; E02 requires that source format. | Caller-selected project format owner. Source keeps its policy. No universal path/ASM/index requirement. |
| Workflow/assessment authoring | E05/E06 expose preview/apply/recover and assessment.create/update/finalize plus workflow operations. | Retain source/legacy owner. Source existence does not close #316 or prove acceptance. |
| Project rule adoption | E07-E10 P3 distinguish content, decisions, exact rule bytes and effect. | Project rule owner, optionally through selected public knowledge tools. |
| Source catalogs, release/CI policy and wrapper generation | E03, E11 and E12 separate source and target authorities. | Source maintainer under separate authority; no portable release or global cleanup dependency. |
| Managed install/update, lock/projection recovery and M01 | E12 layout and E13 P5 contract delegate these to P6. | P6 product owner; maintenance supplies drift evidence only. |
| Legacy provenance/customizations/effective state/packets | E11 defines initialized-target lifecycle and separate source applicability. | Existing adopted contract/owner until explicit transition. No automatic conversion or deletion. |
| Active old transaction recovery | E06 re-derives outputs, checks journal/digests and refuses external edits; E14 F07 retains original recovery ownership. | Original transaction owner and supported recovery implementation; no new skill clears locks or adopts journals. |

Source release closeout, provider admission, audit custody, catalog management and
framework-wide cleanup do not ship in these packages. Actual project policies may
require review/tracking; optional maintenance neither weakens nor universalizes them.

## Protected core and custom content

P1 layout examples are managed `.ai/core`, installation `.ai/framework.lock`,
project `.ai/custom` and exact generated runtime members. They are not hard-coded
portable paths. Supplied ownership evidence/lock/manifest or explicit owner
declaration determines the boundary; a directory name does not prove writability.

| Surface | Auditor | Governance |
| --- | --- | --- |
| Selected project instructions, standards, custom prompts/templates and links | Read within scope. | Propose/edit named project-owned files under task authority. |
| Managed package core and generated runtime members | Compare supplied current/baseline identities; report drift/uncertainty. | Source/P6 handoff; no generated edit, silent shadowing or automatic core copy into custom. |
| Lock, selection/config version and recovery stores | Read selected non-sensitive evidence where relevant. | P6 handoff; no repair, upgrade, deletion or M01. |
| Root AGENTS/CLAUDE/readme and unowned runtime files | Read relevant project context. | Project-owned unless exact managed ownership is proven. Selected authorized edits are possible; broad replacement/cutover needs separate scope. |
| Credentials, provider settings, unrelated project data and product source/tests | Outside default scope. | Distinct owner/task, outside default edit radius. |

Conflicting ownership blocks only the affected write; continue useful scoped
analysis. Do not invent precedence, bless drift by changing a lock, weaken controls
or bypass protected core through a custom file. An override has meaning only if the
actual project/runtime binding supports it; proposed text proves no consumption.

## Necessary state without a second ledger

E11 currently requires semantic identity, provenance, customization, full effective
statements, reconciliation, audits and packets. Preserve those requirements for
existing adopted installations. New optional maintenance needs much less.

| State | Scope and single owner | New-package treatment |
| --- | --- | --- |
| Installed component/version/digest/owned paths | P6 installation owner | Read when supplied/relevant; never duplicate in a semantic ledger. |
| Effective rule and applicability | Project canonical standard/instruction owner | Keep full adopted statement there; cite it. A delta is not normative truth. |
| Why an extension/override exists and who adopted it | Existing project decision record owner, ADR or other project format | Preserve subject identity, material baseline, intent, scope, decision evidence and expiry if needed; no second CUST entry. |
| Proposal/unresolved conflict | Caller-selected proposal/Issue/conversation owner | Keep distinct from adoption; no persistence unless requested or project-required. |
| Required exception review/expiry | Existing project exception owner | Retain only the real requirement, without a new maintenance schedule. |
| Final assessment/findings | Existing record owner | Keep identity/conclusions; revisions/addenda/successors use its contract. A proposal cannot resolve an old finding. |
| Legacy ledger/pending migration | Existing lifecycle owner | Retain exact state; transfer/retire only by explicit source/P6 decision and credible recovery disposition. |
| Universal catalogs, effective packets, always-on resolver | Existing legacy/source owner until cutover | Do not reproduce: no selected new consumer needs a universal engine; ordinary operations take relevant explicit authority. |

No rule change means no customization event. Ordinary feature work, skill reading,
presentation-template edits or unrelated upgrades do not require maintenance.
For a real rule change, use the existing project rule/decision location. If no
decision store exists, an explicit user/task decision may support a bounded edit;
retention follows project requirements and requested output. Missing semantic
meaning/adoption/precedence cannot be filled by a filename or fabricated ledger row.

## #316 and history remain separately governed

Live #316 was OPEN on 2026-09-23. Its bounded authoring scope requires protected IDs,
created time, assessed subject and final conclusions, selected index updates,
stale-input checks and recoverable multi-file interruption. E05/E06 show source
operations, not a pass against all ten criteria or permission to alter Issue state.

The coordinator reconciles #316 before retiring old producers/readers/validators
or registrations. Preserve current templates, historical bytes and exact recovery
tool/dependencies for active transactions. No automatic ASM import, comment
rewriting, index conversion or journal adoption. Unknown versions stay intact.
No active transaction inventory was requested or obtained; absence of a known
journal is not proof that recovery duties can be removed.

Under U001 these preservation obligations do not authorize recovery execution now.
An encountered interrupted transaction stops the affected transition; preserve its
evidence and return the decision to coordinator/P6/P7 with the original owner.
