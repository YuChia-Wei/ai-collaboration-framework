# Artifact Capability Matrix

Assessed source: `8830cdfc252b8845efcbe6cce539041c17cf8e7a`.
This is assessment evidence, not a new production registry or adopted policy.
Exact schema paths, source blob identities, byte hashes, nested version literals,
template paths and selected test-method names are in [source-inventory.json](source-inventory.json).
Reproduce with [collect-inventory.py](collect-inventory.py). A declared schema
version, a nested artifact version and a template version are separate identities.

Capability notation:

- `producer`: an evidenced program emits the artifact; this does not imply general CRUD or arbitrary historical migration.
- `authoring`: a skill/template supplies the creation route; a dedicated executable writer was not established in the bounded sources.
- `reader`: compatibility is evidenced; no transformation capability is implied.
- `unknown`: not established, rather than proof of absence.
- Proposed lifecycle categories describe the recommended next design, not changes made here.

## Explicit schema files: 33 YAML definitions

Paths below are repository-relative. Each row identifies one schema file; nested
record families make the number of artifact kinds larger than 33.

| ID | Schema path | Observed model / versions | Current capability and enforcement | Proposed lifecycle handling |
| --- | --- | --- | --- | --- |
| E01 | `.ai/assets/shared/agent-execution-guardrails.schema.yaml` | Definition 1.0; packet 1.0/1.1 models; lease, evidence ledger, retry, graph, classification, review-input contracts | `execution-artifacts.py prepare` writes selected current packet; `validate-agent-execution-guardrails.py` checks structure and live/authority semantics. No general writer for all nested kinds established. | Adapt existing packet producer; dedicated operations for leases/retries/evidence; do not auto-convert authority records. |
| E02 | `.ai/assets/shared/cli-execution-routing.schema.yaml` | 1.0 local routing | `ai_context_cli_routing.py` reads/validates; a programmatic writer was not established. Missing file is valid unconfigured state. | Explicit opt-in authoring only; preserve ignored, secret-free local ownership. |
| E03 | `.ai/assets/shared/provider-neutral-capability-registry.schema.yaml` | 1.0 registry | `validate-ai-context.py` validates capability registry relationships; current standalone producer unknown. | Authoring adapter with cross-reference validation. |
| E04 | `.ai/assets/shared/provider-projection-registry.schema.yaml` | 1.0 registry/projections | Context validator and registered profile gates; standalone producer unknown. | Authoring adapter; preserve provider-neutral versus provider projection ownership. |
| E05 | `.ai/assets/shared/validation-dependency-observation.schema.yaml` | Definition 1.0; versioned request/report | `observe-validation-dependencies.py` produces observations; partial/unsupported coverage remains explicit. | Author requests; produce reports from observation, never from desired coverage. |
| E06 | `.ai/assets/shared/validation-evidence-lifecycle.schema.yaml` | Definition 1.0; classification, subject manifest, rebind, audit, reuse receipt, freeze | `validation_subject.py`, `validation-evidence.py`, `validate-validation-lifecycle.py` | Preserve existing producers; content rebind/proven reuse is a semantic operation, not format migration. |
| E07 | `.ai/assets/skills/ai-context-governance/templates/customizations.schema.yaml` | 1.0 customization ledger | Init/upgrade/effective-rule lifecycle and target validation; ledger decisions require source evidence. | Author/reconcile with owner decisions; legacy overrides become unresolved reconciliation inputs where required. |
| E08 | `.ai/assets/skills/ai-context-governance/templates/effective-rule-packet.schema.yaml` | 1.0 packet; route/layout contracts | `resolve-effective-rule-packet.py` and effective-rule implementation produce candidate projections; complete legacy layout is readable. | Regenerate from adopted authority; a candidate output does not adopt new target truth. |
| E09 | `.ai/assets/skills/ai-context-governance/templates/effective-rule-state.schema.yaml` | 1.0 state; current compact and legacy layout rules | Effective-rule/provenance implementation; legacy layout reading has explicit constraints. | Rebuild/adopt through owning lifecycle; preserve target semantic customizations. |
| E10 | `.ai/assets/skills/ai-context-init/templates/technology-selection.schema.yaml` | 1.0 target selection | Init template and `validate-ai-context.py`; no independent general CRUD writer established. | Author explicit selection; unresolved values remain unresolved. |
| E11 | `.ai/assets/skills/ai-context-init/templates/work-item-binding.schema.yaml` | 1.0 binding selection | Init configuration and context validation | Author explicit target choice; do not infer authorization from provider state. |
| E12 | `.ai/assets/skills/ai-context-upgrader/references/delegation-run-contract.schema.yaml` | 1.0 run record | Upgrader skill contract and context validation | Bind observed invocation; no fabricated role execution on generation. |
| E13 | `.ai/assets/skills/ai-context-upgrader/references/role-execution-bindings.schema.yaml` | 1.0 binding manifest | Upgrader role binding manifest / context gates | Author bindings under owning skill; static availability never means invocation. |
| E14 | `.ai/assets/skills/ai-context-upgrader/templates/multi-hop-upgrade-transaction.schema.yaml` | 1.0 outer transaction; prepared-hop, preparation-failure, resolver records | `ai_context_multi_hop_upgrade.py`, package-apply implementation | Existing transaction producer/recovery owner; preserve child plan and journal semantics. |
| E15 | `.ai/assets/skills/ai-context-upgrader/templates/upgrade-remediation-decision.schema.yaml` | Definition 1.0; `upgrade-remediation-decision/v1` JSON document | Package-apply/provenance operations consume sealed decisions | Explicit decision creation; no format-only conversion to new approval. |
| E16 | `.ai/assets/skills/ai-context-upgrader/templates/upgrade-remediation-packet.schema.yaml` | Definition 1.0; `upgrade-remediation-packet/v1` | Package-apply producer and validation | Reprepare from bound inputs; invalidate old decision binding when subject changes. |
| E17 | `.ai/assets/skills/ai-context-upgrader/templates/upgrade-route-matrix.schema.yaml` | Definition 1.1; readers for 1.0/1.1; nested edge evidence | `ai_context_upgrade_routes.py` | Author route with supported reader boundary; edge proof is not synthesized by migration. |
| E18 | `.ai/assets/skills/software-development-orchestrator/templates/external-task-delegation.schema.yaml` | 1.3; dispatch/completion/receipt 1.2/1.3; request/observations 1.0 | `execution-artifacts.py prepare/finalize/check/migrate/templates`; owner validator | Existing dispatch/completion 1.2→1.3 route; receipts never migrated; historical readability is not admission. |
| E19 | `.ai/assets/tech-stacks/dotnet-backend/examples/evidence-schema.yaml` | 1.0 example evidence manifest | `validate-ai-context.py` checks example evidence | Author example provenance; examples do not become real acceptance evidence. |
| E20 | `.ai/assets/tech-stacks/dotnet-backend/tooling/on-demand-mechanical-validation/provider-contract.schema.yaml` | 1.0 provider contract | Contract/template and engineering-guardrail checks; exact production schema-loading path not established | Provider-owned adapter; keep real provider availability/execution separate. |
| E21 | `.ai/distribution/schemas/files.schema.yaml` | 2.0.0; legacy reader 1.0.0 | `ai_context_package.py` / apply parser; package builder generates inventory | Regenerate package inventory; preserve published bytes and provenance. |
| E22 | `.ai/distribution/schemas/identity-registry.schema.yaml` | Source registry 1.1; packaged identity metadata uses separate 1.0.0/1.1.0 versions | `.ai/distribution/validators/product_identity_registry.py`; package identity resolver/build/parser | Update registry through canonical owner; regenerate selected package identity. Do not conflate registry and package metadata versions. |
| E23 | `.ai/distribution/schemas/migration.schema.yaml` | 3.0.0; readers 1.0.0/2.0.0/3.0.0 | Package builder/parser/apply | Existing package migration semantics; not a universal document migration engine. |
| E24 | `.ai/distribution/schemas/package.schema.yaml` | 2.4.0; declared older package readers | `build-ai-context-package.py`, `ai_context_package.py`, apply and package validators | Regenerate candidate packages; published package identities remain immutable. |
| E25 | `.ai/distribution/schemas/selected-inputs.schema.yaml` | Definition 1.0; `package-selected-input/v1` and `/v2`; nested `release-package-input/v1` | Package input projection builder/parser | Regenerate content identity from source; preserve unknown release fields required by the projection contract. |
| E26 | `.ai/distribution/schemas/source-dispositions.schema.yaml` | 1.0 source disposition registry | `validate-source-dispositions.py`; registry authoring | Author explicit dispositions, validate all referenced ownership paths. |
| E27 | `.ai/distribution/schemas/v015-package-validation-terminal.schema.yaml` | JSON Schema 2020-12; terminal `/v1` | `ai_context_v015_validation.py` execution lane | Execution-derived report, retain prior outcome and retry identity. |
| E28 | `.ai/evaluation/schemas/corpus-manifest.schema.yaml` | 1.0 mapping contract | Evaluation corpus authoring and `validate-ai-behavior-evaluation.py` | Author corpus metadata; exact generic schema loader not established. |
| E29 | `.ai/evaluation/schemas/evaluation-result.schema.yaml` | 1.0 mapping contract | Evaluation result validation | Produce from actual evaluated cases; migration cannot create a missing observation. |
| E30 | `.ai/evaluation/schemas/incident-fault-injection-result.schema.yaml` | 1.0 definition; result `/v1` | Evaluation validator emits fault-injection result | Run or preserve evidence; do not relabel synthetic evidence as real acceptance. |
| E31 | `.ai/evaluation/schemas/incident-mutant-manifest.schema.yaml` | 1.0 mapping contract | Mutant manifest and evaluation validator | Author defined mutations; preserve independent expected outcomes. |
| E32 | `.dev/backlog/provider-mappings/github-issues.schema.yaml` | JSON Schema 2020-12; receipt schema 1.0 | `github_backlog_provider.py` receipt producer/reader | Preserve historical migration receipts; current provider truth needs live read-back. |
| E33 | `.dev/standards/AI-CONTEXT-SOURCE-EFFECTIVE-RULE-EVIDENCE.schema.yaml` | 1.0 source rule evidence | Effective-rule resolver and source rule validation | Generate source projections; target adoption remains a separate operation. |

The historical JSON schema is
`.dev/workflows/2026-08-14-environment-execution-routing/tasks/ENVROUTE-001-contract-schema.json`.
It is retained evidence, not automatically an active family or a required migration target.

## Implicit and embedded contracts

The 47 paths selected by the inventory's template-root selector include historical
compatibility templates, public-root files and templates without schemas. They
are **not** 47 active schema families. Guides below additionally embed templates
outside those path selectors.

| ID | Kind / authoritative location | Existing producer or authoring route | Required boundary for future tooling |
| --- | --- | --- | --- |
| I01 | Active `skill.yaml` / `sub-agent.yaml`; `.ai/assets/CANONICAL-SCHEMA.MD` | Skill/role authoring; `validate-ai-context.py`; runtime entry generator | Common metadata permits owned extension fields. Versioned sub-agent 1.1 differs from common 1.0. |
| I02 | Command / prompt-package creation templates; `.ai/assets/templates/` | Creation templates only | No active manifest family/discovery coverage is established merely by template presence. |
| I03 | Workflow locator/task/plan/report; workflow policy + owning skill templates | Skill-directed authoring; shared workflow validator; orchestrator-specific validation | Operate on the linked locator, tasks, controlled plan metadata and exact index row; retain skill-specific prose/semantics. |
| I04 | Assessment locator/report; assessment policy + report-owning skill | Skill-directed authoring; assessment validator | Create locator/report/index together; immutable IDs/created_at; final report conclusions frozen; workflow relations use IDs. |
| I05 | Workflow handoff checkpoint; `.dev/standards/WORKFLOW-HANDOFF-POLICY.yaml` | Governance handoff template and validator | Bind receiving environment, authority and resume state; a valid shape does not execute a handoff. |
| I06 | Requirement Markdown; `.dev/requirement/REQUIREMENT-GUIDE.MD` | `requirement-author`, embedded copy/fill template | Preserve stakeholder meaning, source references and acceptance IDs; schema cannot author missing requirements. |
| I07 | Production/entity/adapter specs; `.dev/specs/SPEC-GUIDE.MD` | `spec-author`, embedded field shapes/examples | Semantic revision; no supported document version is inferred from a guide's date. |
| I08 | Formal test specs; `.dev/specs/tests/TEST-SPEC-GUIDE.MD` | `spec-author` | Preserve scenario/source linkage; don't derive the expected result from the implementation being checked. |
| I09 | CBF/SWF problem frames; problem-frame author playbook and CBF template set | `problem-frame-author`; separate compliance capability | CBF has five tracked YAML templates; SWF layout is described, not proved to have a template directory. |
| I10 | Init project configuration; `project-config.template.yaml` | Init skill and repository-config contract checks | File contains JSON-compatible content despite .yaml suffix; `schemaVersion` and artifact semantics need explicit binding. |
| I11 | Target provenance / source template; upgrader provenance contract | `ai_context_target_provenance.py` initialize/finalize APIs, target validator | Provenance schema 2.0 versus template 2.1.0; never synthesize trusted source history. |
| I12 | Apply plan / journal / progress / pending receipt | `ai_context_package_apply.py`, planner CLI | Plan 2.2.0, journal v5, progress v1, pending receipt 2.0.0; explicit refusal of v4 recovery/conversion. |
| I13 | Incoming/target/terminal upgrade receipts | Apply runner, `run-target-validation.py`, provenance finalization | Actual execution and immutable authority binding; regenerate only through required execution. |
| I14 | Validation evidence / cache / sidecars | `validation-evidence.py`, process supervisor, validation subject APIs | Evidence/cache 2.0.0 differ from their independent sidecar versions; old cache discard is not historical evidence migration. |
| I15 | Release record / phase checks / notes / migration guide | Governance release templates, version and release-state validators, notes renderer | `prepare-ai-context-release.py` is read-only. Release template top-level version is a placeholder; phase checks 1.0 and provider reconciliation 1.0/1.1 are separate contracts. |
| I16 | Canonical routing, rule and ownership catalogs | Shared/profile rule catalogs, routing YAML, `.dev/standards/AI-CONTEXT-OWNERSHIP.yaml` | Primarily authoring plus cross-file validators; no uniform executable writer established. Preserve one semantic owner. |
| I17 | Tooling registries | `.ai/scripts/python-entrypoints.json`, `shell-assets.yaml`, `test-fixture-classifications.json` and profile registry | Maintainer-authored plus dedicated contract checks; adding a CLI changes dependency/profile registration too. |
| I18 | Source policy configuration | Git commit, source work-management and GitHub policy YAML | Schema-bearing executable policy; tool construction cannot supply owner authorization to weaken policy. |
| I19 | Provider/runtime-native configuration | `.github/workflows/*.yml`, issue forms, runtime TOML, public-root editor/git configuration | Register external ownership/delegated validation where relevant; do not build competing schemas for standards owned by those tools. Personal local values excluded. |

## Reconciled discovery limitations

- The mechanical-worker projection initially called the CLI routing module a
  potential reader/writer. Parent inspection established a reader/validator;
  no writer is claimed in E02.
- The selected-inputs schema explicitly declares both package-selected-input
  v1/v2 and a nested release projection v1. Reading only the top-level 1.0 or
  the nested release projection would undercount supported document versions.
- The source identity registry's 1.1 and package identity metadata's 1.1.0 are
  different records, not evidence of an inconsistency.
- The auditor's static role bindings do not select mechanical-evidence-worker.
  The attempted binding was retained as a preparation problem; returned material
  is supporting discovery, not an accepted canonical-role or independent-review
  receipt. Parent file-backed reconciliation owns this matrix.
- No repository-wide absence of additional helpers is claimed. A production
  registry must prove each adapter binding and coverage rather than promote this
  assessment table into executable authority by copying it.

## Evidence anchors

- `.ai/scripts/README.md:18`, `:49`, `:63`, `:215`, `:248`, `:312`.
- `.ai/scripts/execution-artifacts.py:91`, `:174`, `:227`, `:283`, `:316`.
- `.ai/scripts/execution_artifact_contract.py:44`, `:88`, `:126`, `:172`.
- `.ai/assets/CANONICAL-SCHEMA.MD:8`, `:24`.
- `.ai/distribution/schemas/selected-inputs.schema.yaml:1` and `:9`.
- `.ai/assets/skills/ai-context-upgrader/references/provenance-contract.md:60` and `:89`.
- `.ai/scripts/ai_context_package_apply.py:80`.
- `.ai/scripts/validate-workflow-artifacts.py:362` and `:393`.
- `.ai/scripts/validate-assessment-artifacts.py:259` and `:304`.
- `.ai/scripts/validate-ai-context-versions.py:278`.
- `.dev/requirement/REQUIREMENT-GUIDE.MD:51`.
- `.dev/specs/SPEC-GUIDE.MD:74`.
- `.ai/assets/skills/problem-frame-author/references/authoring-playbook.md:35`.
