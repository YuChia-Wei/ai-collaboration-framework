# P5 selected capability and format contract

Coordinator selection under #322/U001, based on #342 design checkpoint `66f353393b3f7ef59265d6c38b119a832e8113a9`. The inventory is complete for its bounded design scope; product capability implementation, root cutover and P7 verification are separate. Original proposals remain historical inputs. This source coordination document is not an installed package dependency.

## Decisions D342-01 through D342-06

| Decision | Selected result |
| --- | --- |
| D342-01 | Adopt exact integer metadata version 3 with the closed instruction/tool operation union and restricted null configuration from [operation-model.md](capability-consolidation/operation-model.md). Preserve v1/v2 shapes and meanings unchanged. |
| D342-02 | Deliver `code-reviewer@0.1.0` first as a common-only, three-member instruction package, with no fake executable, owned record or required Python runtime. Explicitly report missing selected technology coverage. |
| D342-03 | Preserve ten specialist responsibilities as independently selectable capabilities. AI-context auditing/governance are optional maintenance; installation/update mechanics belong to P6; release/history duties stay source-only. Group implementation work where methods share a coherent boundary; do not merge skill identities. |
| D342-04 | Adopt the 95-kind, 17-group future responsibility dispositions. Preserve exact historical bytes and models; retired means excluded from the future active product, not deleted or permission to abandon an active recovery. Current source owners remain until their explicit replacement. |
| D342-05 | Keep the five P3 packages on current metadata/config/record versions. Select M01 as the sole candidate conversion edge for P6 design: JSON config integer 1 to 2, only when an actual selected project needs it. No automatic migration and no required Lesson record conversion. |
| D342-06 | Structured problem-frame/compliance and optional assessment/governance persistence require a bounded format decision before mechanical implementation. They remain queued responsibilities, not fabricated implemented tools or permission for broad legacy conversion. |

Source observations are pinned to their original subject; [dependency-update.md](capability-consolidation/dependency-update.md) records actual P3 integration and P4 selection. P4 source remains owned by #341 and P6 design by #345. Neither is counted as a delivered package by this inventory.

## Exact metadata-v3 boundary

Common operation fields remain id, inputs, outputs and implementation_status. Required execution is exactly instruction or tool. The instruction arm requires instructions pointing to a declared, existing package-relative reference and forbids tool. The tool arm requires tool pointing to an implemented declared executable and forbids instructions. Compare tool-operation equality only across tool arms. No both/neither arm, null placeholder tool, silent fallback, executable instruction string or builder execution.

Null configuration is allowed only when artifact_roles, schemas and templates are empty; it causes no config resolution/creation or store provisioning. Non-null configuration keeps the v2 contract. Resources may be empty, but exact membership, contained paths, cross-platform collisions, runtime requirements and v2 schema-pair/read_schemas rules remain. Package and instruction implementation statuses describe delivered source, never invocation or verification. Optional prose templates may be ordinary instruction references; they are not machine artifact roles.

The Codex adapter must say operation interface and distinguish instruction from tool execution. A null-config package must not render instructions requiring config or a Python runtime. Generated entries remain exact owned projections, not another editable source. Existing tool packages retain correct public-tool guidance. Only actual source may enter manifest/profiles; no speculative package rows.

## First implementation batches

These are selected source assignments: #346, #347 and #348. Each Issue has one independent Astra Ultra conversation/worktree, no sub-agents, and a coherent local source return before push.

| Batch | Exclusive implementation responsibility | Complete bounded result |
| --- | --- | --- |
| P5-A / #346 shared vertical slice | `src/distribution/package.py`, necessary direct `src/distribution/` consumers, `src/adapters/codex/skill-entry.md.template`, `src/skills/code-reviewer/`, own design/workflow | Metadata-v3 source support plus the real three-member common reviewer and operation-neutral adapter. Exact reviewer-only manifest/profile mapping may be assigned to this same shared writer after the source checkpoint; no other skill mapping before actual delivery. |
| P5-B / #347 engineering methods | `src/skills/diagnostic-analyst/`, `ddd-ca-hex-architect/`, `bdd-gwt-test-designer/`, `local-change-implementer/`, `slice-implementer/`, own design/workflow | Five distinct instruction packages with empty skill dependencies and target-owned rules/commands/destinations supplied explicitly. Preserve diagnostic uncertainty/falsification, architecture invariants/alternatives, GWT observability and implementation scope. No diagnostic JSON 1.0 port in this batch. |
| P5-C / #348 artifact authoring | `src/skills/requirement-author/`, `src/skills/spec-author/`, own design/workflow | Two distinct instruction packages with useful packaged default guidance and caller-selected templates/paths. Keep stakeholder intent/source bindings/assumptions; formal-test specification remains a spec-author choice. No compulsory prose schema/store. |

P5-B/P5-C can author against this selected contract while P5-A implements its loader. They never edit shared loader, manifest, profiles, adapter, root entries or indexes. The coordinator reconciles actual members and assigns one shared mapping writer afterward. P4 and all existing P3 package source are outside these batches. Expected source statuses never count as tested compatibility.

Structured frame/compliance design and optional context-maintenance design follow as separately bounded work. Generic implementation remains useful without every technology role. No unselected .NET rules activate globally. The old root routes remain current until P6 cutover; missing new capabilities must remain visible rather than being silently dropped.

## M01 handoff to P6

Read [M01 details](capability-consolidation/implementation-slices.md). Input is only existing closed P2 project/local JSON config version 1, not legacy YAML/provenance. Output changes the exact integer version to 2 while preserving semantic values, absence, namespaces, write roots and locks. Add no permission, default, decision source or other skill namespace. Preserve original raw bytes for recovery.

The pair cannot be claimed atomic: selected project/local versions must agree, readers are withheld during partial conversion, durable before-bytes and expected digests control recovery, and newer external edits block restoration. Old P2 tools reject v2. Adding v2 namespaces later makes naive reverse conversion invalid. P6 #345 designs the installation/conversion boundary; later source ownership and actual need are selected explicitly. No migration tool or conversion is executed by this decision.

## Verification and source transition

Only direct content/UTF-8/JSON/YAML/AST syntax without product imports or pycache, reference/Git/diff and exact planned commit-message checks are permitted now. Product CLI/help, schema validation, tests/fixtures, build/package/install/migration, audit/lease machinery and CI remain deferred-by-owner under U001 to program #322 coordinator / P7. Later checks cover actual instruction/tool union behavior, unchanged v1/v2 behavior, null config, owned paths, exact mapping and useful target use.

Source completion does not activate a root skill, close unrelated #316/#318/#317 work, publish a release or certify downstream use. The coordinator owns integration and future explicit disposition of overlapping old Issues.
