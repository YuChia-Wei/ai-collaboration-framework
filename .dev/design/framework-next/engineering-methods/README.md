# Engineering method package source delivery

Issue [#347](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/347),
P5-B under the [selected P5 contract](../p5-selected-contract.md).
This is source coordination documentation, not an installed package dependency.

## Delivered boundary

Five separately selectable `0.1.0` packages contain 23 files and seven public
instruction operations. All use exact integer metadata 3, explicit null
configuration, empty required/optional skill dependencies and empty artifact
roles/schemas/templates/tools. `implemented` records delivered instructions,
never invocation, testing, installation, compliance or acceptance.

| Package | Public operations | Members | Runtime |
| --- | --- | --- | --- |
| diagnostic-analyst | diagnose | 3 | skill-instruction-reader |
| ddd-ca-hex-architect | design, review | 4 | skill-instruction-reader |
| bdd-gwt-test-designer | design, review | 4 | skill-instruction-reader |
| local-change-implementer | implement | 3 | skill-instruction-reader, authorized-target-editor |
| slice-implementer | implement | 9 | skill-instruction-reader, authorized-target-editor |

Exact member paths, raw-byte SHA-256s, operation references and runtime
requirements are in [delivery.json](delivery.json), derived by direct file/YAML
reading. It is an inventory, not a schema-validation receipt or executed package
result. For any future coordinator mapping, each listed relative member maps
from `src/skills/<id>/<member>` to `.ai/core/skills/<id>/<member>`. This Issue
does not modify manifest/profiles, generate entries or activate root routes.

No required Python runtime exists in these packages. Requested experiments,
checks and artifact writes additionally require the actual selected target
tools/authority, as explained by each method; missing support is reported per
affected action. A blocked experiment can still yield a diagnostic conclusion
of blocked/unconfirmed. Generic slice needs neither the three other modes nor
a technology role registry.

## Actual source extraction

Initial reading was at `842b73ca09d701d1561109255193d80439dc996b`.
The same assigned worktree resumed at
`4cda6689bf469a2273e14e237a0c3bf7ad4b6eed`; direct Git comparison confirmed no
changes in the five legacy skill trees or three shared contracts below between
those subjects. Non-code Markdown/YAML was discovered through scoped tracked
Git paths and read directly. No graph coverage or absence claim is made.

The following are source-only extraction bindings. Every listed reference was
read, not merely copied from an inventory. All legacy paths remain unchanged.

| Read legacy source (relative to repository root) | Meaning retained and destination | Removed dependency or unported surface |
| --- | --- | --- |
| `.ai/assets/skills/diagnostic-analyst/skill.yaml`; `references/diagnostic-contract.md`; `references/output-contract.md` in that skill | Falsifier-first hypotheses, opportunity counts/strength, bounded reproduction, intervention, causal admission, uncertainty and repair/regression boundary -> new `references/diagnose.md`. | JSON schema_version 1.0, validator and compulsory evidence-store format are not ported. No script/fixture reading or execution is claimed. |
| `.ai/assets/skills/ddd-ca-hex-architect/skill.yaml`; its `references/architecture-playbook.md`, `design-deliverables.md`, `review-criteria.md`, `source-map.md`, `prompt-templates.md` | Language, invariant/data ownership, ports/adapters, dependency direction, alternatives, failure/evolution/testability and design/review distinction -> new `references/design.md` and `review.md`. | Human-guide pointer, implicit profile routing, effective-rule machinery and source directory placement are replaced by explicit target inputs. No technology supplement is bundled. |
| `.ai/assets/skills/bdd-gwt-test-designer/skill.yaml`; its `references/scenario-design-playbook.md`, `scope-rules.md`, `output-contract.md`, `review-criteria.md` | Stable scenario/row sources, concrete GWT, expected-value sources, observable assertions, controlled setup, test level and read-only review -> new `references/design.md` and `review.md`. | Fixed test-spec paths, runner defaults and role/workflow records are absent. Formal test specifications remain a distinct selected authoring output. |
| `.ai/assets/skills/local-change-implementer/skill.yaml`; its `references/allowed-operations.md`, `execution-rules.md`, `skill-boundaries.md` | One target/operation, direct radius, private-helper exception, compatibility, necessary tests and semantic escalation -> new `references/implement.md`. | No source resolver, mandatory packet or workflow path. File count is not a scope decision. |
| `.ai/assets/skills/slice-implementer/skill.yaml`; its `references/input-contract.md`, `execution-playbook.md`, `handoff-rules.md`, `role-execution.md` | Separate authorization/normative/finding inputs, one selected mode, retained slice ownership and concrete missing-decision handoffs -> new `references/implement.md`. | No mandatory per-role registry, delegation, model/runtime, audit/lease or per-binding record. The stricter legacy handoff phrase “no new type” is reconciled to the shared private-helper semantic rule. |
| Legacy slice `references/modes/command-use-case.md`, `query-use-case.md`, `reactor.md`, `generic-slice.md`; `references/overlays/remediation.md` | State-changing command, read-only query, event reaction, generic/test-only and evidence-backed remediation -> four new mode references and `references/remediation.md`. | Hardcoded architecture paths, .NET interfaces/method names, Wolverine and globally mandatory concrete-test roles are not portable requirements. |
| Legacy slice `roles/command-sub-agent/references/implementation-playbook.md`, `roles/query-sub-agent/references/implementation-playbook.md`, `roles/reactor-sub-agent/references/implementation-playbook.md` | Transport/domain separation, state/query/event distinctions, accepted persistence/read boundaries and explicit result mapping inform the corresponding modes. | Technology naming, archive/repository types, DI APIs, output folders and test-framework defaults are deliberately not bundled. No other private role tree or technology implementation coverage is claimed. |
| `.ai/assets/shared/ARTIFACT-DESIGN-REVIEW-CONTRACT.md` | Fixed subject, independent source criteria, read-only review, author relationship/classification and revision rebinding -> contained architecture/GWT review references. | No source packet/resolver route or hidden cross-package dependency. |
| `.ai/assets/shared/GWT-TEST-HANDOFF-CONTRACT.md` | Source/row identity, expected outcomes, real subject, concrete step/assertion mapping and separate execution evidence -> GWT design and slice `references/test-handoff.md`. | No compulsory record or second design stage. Target-selected schemas are not silently extended. |
| `.ai/assets/shared/IMPLEMENTATION-SCOPE-ROUTING-CONTRACT.md` | Semantic radius, private-helper exception, accepted public-type slice, decision-driven handoff and existing permission -> local/slice implementation references. | No compulsory orchestrator/local bouncing or installed skill dependency. |

Only useful shared meaning is contained in each consumer. Repeating a small
review/handoff boundary keeps each package standalone; it creates no shared
runtime or second target authority. Optional architecture/diagnostic/BDD/review/
ADR/knowledge collaboration returns semantic context if the other capability
is absent. A named handoff is not evidence of execution or permission expansion.

## Substantive behavior retained

- Diagnosis requires an observed symptom and falsifier before experiment;
  sampling absence never proves nonexistence. Confirmation needs reproduction
  and deterministic causal isolation, with alternatives and limitations.
- Architecture compares valid alternatives and invariants without imposing all
  DDD/CA/HEX patterns or an unselected technology. Review never mutates its fixed
  subject and does not call self-check independent acceptance.
- GWT covers every selected AC or states a gap. Important outcomes carry
  assertable values and independent expected sources. Mocked boundaries do not
  establish real integration. Test implementation/execution are separate.
- Local implementation stays within an accepted semantic radius; private
  helpers may be local, public/semantic changes require a settled slice design.
- Slice implementation retains internal ownership, selected modes and target
  rules; complete GWT can be implemented without a new designer stage.
  Remediation with deferred validation never becomes a resolved finding.

## Delivery and remaining work

[Workflow](../../../workflows/2026-09-23-engineering-methods/workflow-plan.md)
retains authority and permissions history;
[report](../../../workflows/2026-09-23-engineering-methods/reports/remediation-report.md)
retains actual checks and limits. No cross-contract decision remains for this
source batch. Shared mapping, optional technology coverage, root adoption and
runtime acceptance belong to separately assigned work.

All product execution and acceptance remain `deferred-by-owner` under U001,
owner program #322 coordinator / P7, next action P7 selects redesigned checks
after implementation. This source-only exception is not inside any package.
