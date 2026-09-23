# Proposed slices and coordinator decisions

Future assignments only; no new execution authority or Issue creation. Coordinator selects immutable base, dedicated worktree and one writer. Source/tools/tests/migrations are unchanged by #342. P7 owns redesigned verification under U001. [Subsequent P3/P4 state](dependency-update.md) supplements the original inventory without merging it.

## Decisions

| ID | Recommendation | Consequence / pending choice |
| --- | --- | --- |
| D342-01 | Select exact metadata-v3 union and null configuration in operation-model.md | Shared owner implements; v1/v2 unchanged. |
| D342-02 | First package common-only code-reviewer, three members, prose output | No fake tool. Dotnet extension separately selected later. |
| D342-03 | Ten specialists selectable; context maintenance optional; release/history source-only | Proposed selection, not current unregistration. |
| D342-04 | Preserve unsupported history; P4/P6/P7 own replacements | No 95-schema port. Active old transactions recover with original owner. |
| D342-05 | Keep real P3 record packages unchanged; select M01 only for a real v1-config project needing v2 | No unnecessary Lesson record migration or invented decision state. |
| D342-06 | New problem-frame/optional-assessment persistence needs bounded format design first | Owners identified, no promise of a safe writer before exact semantics are selected. P4 workflow contract is already selected separately. |

None blocks retaining this design checkpoint. All are future coordinator selection points; without selection no dependent source edit or availability claim follows.

## Small single-writer implementation units

| Slice | Exclusive intended scope | Prerequisite and complete outcome |
| --- | --- | --- |
| P5-S0 | Shared owner: src/distribution/package.py, necessary direct distribution consumers, src/adapters/codex/skill-entry.md.template | D342-01; integrated #337 mappings. Version-3 parsing/reference source support and operation-neutral adapter, without rewriting P3 metadata/config. Return source plus future P7 cases. |
| P5-R1 | src/skills/code-reviewer/ | Selected v3; three complete members, honest common coverage. No dotnet/assessment machinery. Shared owner maps only after real source return. |
| P5-R2 | src/skills/diagnostic-analyst/ | v3; preserve causal method and uncertainty. Optional diagnostic-1.0 validate port is separately selected useful mechanical operation; no synthetic facts or required JSON. |
| P5-R3a / R3b | Separate assignments: src/skills/ddd-ca-hex-architect/ and src/skills/bdd-gwt-test-designer/ | v3; contained method, explicit target inputs/destinations. ADR optional, GWT creates no runner. |
| P5-R4a / R4b | Separate assignments: src/skills/local-change-implementer/ and src/skills/slice-implementer/ | v3; scope radius, target architecture/commands. Start generic slice, conditional technology, no all-role migration. |
| P5-A1a / A1b | Separate requirement-author/ and spec-author/ under src/skills/ | v3; useful default writing guidance and caller templates/paths. No artificial record schema/store. Formal-test spec remains spec-author. |
| P5-A2a | Future src/skills/problem-frame-author/ owner; design first | Select one CBF or SWF family and exact version, source bindings, real reader/validator and useful deterministic create/write boundary. Preserve other formats unsupported; no compliance claim. |
| P5-A2b | Future src/skills/spec-compliance-validator/ owner | Selected frame contract and explicit target .NET prerequisites; criteria/evidence mapping. Target runtime/P7 proves execution, source textual helper does not. |
| P5-M1a | Future src/skills/ai-context-auditor/ | v3; optional bounded audit method, prose default, no source policy dependency. |
| P5-M1b | Optional assessment format owner/path selected before implementation | Reconcile #316; choose exact format/operations, stable identity and finalized conclusion protection. Automate useful mechanics only, no phantom verification or mandatory .dev location. |
| P5-M2 | Future src/skills/ai-context-governance/ after narrow design | Select minimal semantic reconciliation and which ledger/state still needed. No universal effective-rule engine, source release/catalog duties excluded. |
| P5-T1 | Separately assigned technology owner and exact product path | Only after actual consumer; extract selected rules/checks with missing coverage explicit. No global dotnet baseline. |
| P4 | #341 owns workflow package/schema/config | Selected software-development-orchestrator@0.1.0, metadata/config 2, record 1.0.0. Source not yet returned. Candidate-only composition and retention preview; no P5 rewrite. |
| P6 | Install/update, managed inventory, custom preservation, recovery, root adoption, M01 if selected | Actual mappings and selected update/data contract. Shared root/config/runtime paths remain one writer. No history/release payload. |
| P7 | Validators/tests/trials/CI restoration proposal | Source contracts first, actual versus synthetic evidence distinct; reconcile #274/#275 separately. |

Coordinator-designated distribution integrator owns manifest/profiles (P3 mapping from #337 is now integrated). Package workers return exact members and never race shared mappings. Loader, config envelopes, adapter, root entries, install state and indexes are not co-owned by these slices. New shared methods require a separately selected owner. Complete bounded capabilities may span files; this is not one PR per file or mass migration.

Legacy init/upgrader and root routes stay active until explicit P6 cutover. No portable release-closeout successor is needed.

## M01: exact necessary conversion candidate

Conditional need: a project with existing P2 JSON config_version 1 (closed to Lesson) selects ADR/PR/backlog/promotion with the same explicit config file. Those consumers require version 2. That is the precise necessary edge for this case; projects using defaults/already v2 need none. No actual target need is asserted.

- Input: project JSON exact integer config_version **1**, optional skills.lesson and constraints.lesson as accepted by Lesson's v1 branch; optional selected local JSON exact integer **1**, only skills.lesson. Reject unknown roots/namespaces, duplicates, null/invalid settings, nonfinite values and bool/float version. Legacy YAML project-config/provenance is excluded.
- Output: corresponding project/local JSON exact integer config_version **2**, otherwise identical semantic values, namespaces and absence. Preserve write_roots, locked fields and store/template values; add no decision_sources, permissions, new namespace or defaults. New namespace authoring is separate.
- Future owner: P6 config-transition implementer, coordinated with Lesson config owner and all v2 consumers. Own one edge plus necessary recovery; no general engine.
- Plan: caller chooses exact existing files/digests; preview before/after fields; disclose old P2 tools reject v2; capture durable before bytes outside volatile worktree; recheck inputs and perform bounded writes. No automatic invocation/install migration.
- Pair limits: selected project/local files must match. A single changed member leaves an invalid pair; do not claim atomic multi-file replace. Suspend selected readers during operation, retain progress and backups, withhold activation until both agree. External edits block overwrite recovery.
- Recovery: restore matching captured files only when current digests belong to the partial operation. No automatic reverse conversion after v2 namespaces/constraints are added. If restoration loses meaning, preserve backup and report unsupported.
- Later validation: owning parsers and P7-selected exact-type, mixed-version, unknown-key, stale-input, containment, partial-write and external-edit recovery cases. None run here. No tool, receipt, conversion or adoption is delivered.

Lesson record 1.0.0 -> 2.0.0 is not necessary now: current tool reads v1 and can explicitly derive a new identity. Legacy journals/release history, final assessments and external approvals remain preserve/unsupported.

## Related Issues: scope only

Read-only GitHub observations on 2026-09-23; exact title/state/updatedAt in [evidence](../../../workflows/2026-09-23-capability-consolidation/evidence/related-issues.json). No provider mutations performed.

| Issue | State | Overlap and retained boundary |
| --- | --- | --- |
| [#316](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/316) | OPEN | Legacy workflow/assessment authoring, stale-input/identity/recovery requirements. P4 owns new workflows; optional assessment needs explicit reconciliation. Not absorbed/closed. |
| [#320](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/320) | CLOSED | Prior 16-gap reduction informs current labels (9 manual-gap plus semantic/external). Preserve history; do not reopen or infer runtime coverage. |
| [#149](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/149) | OPEN | Runtime/repository strategy comparison; P5 selects no Go/Rust/.NET rewrite or benchmark. P8 later selection. |
| [#168](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/168) | OPEN | Installable read-only CLI preview remains distinct from P6 bounded mechanics/publication/parity. No mutation-command authority. |
| [#274](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/274) | OPEN | Fixture I/O classification evaluation, not automatic RAM routing. P7 must reconcile, not mark done. |
| [#275](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/275) | OPEN | Durability/logical cost baseline required. No measurement, speed claim or assertion removal here. |

Coordinator update: P6 design Issue #345 is assigned to its separate task/worktree and consumes M01 only after coordinator selection. #345 owns installation-update design; the later conversion implementation owner remains to be assigned. No source, test or extra migration work is added to #342.
