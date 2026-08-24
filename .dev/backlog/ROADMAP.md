# AI Context Release Roadmap

## Roadmap Metadata

- `roadmap_id`: `post-v0.4.0`
- `status`: `frozen-historical`
- `last_recorded_target`: `v0.12.0`
- `created_at`: `2026-07-18T14:19:06+08:00`
- `updated_at`: `2026-08-24T20:18:17+08:00`
- `frozen_by`: `.dev/standards/SOURCE-WORK-MANAGEMENT-AUTHORITY.md`
- `source_assessment`: `.dev/assessments/ASM-20260717-004/assessment.yaml`
- `source_plan`: `.dev/backlog/plans/post-v0.4.0-improvement-plan.md`
- `planning_workflow`: `.dev/workflows/2026-07-18-post-v0-4-roadmap-planning/workflow.yaml`
- `gate_revision_workflow`: `.dev/workflows/2026-07-19-roadmap-gate-revision/workflow.yaml`
- `product_contract_workflow`: `.dev/workflows/2026-07-23-v0-6-product-contract-planning/workflow.yaml`

## Historical Usage Contract

Do not use this file to plan or resume current work or a release. It preserves
the post-v0.4 planning state recorded before 2026-08-24 for link and release
compatibility only.

- Live GitHub Issues and Project #3 own current source work and release views.
- The horizons, gates, local item metadata, and handoffs below are historical
  records, not current authorization or planning evidence.
- Execution workflows own task progress, validation evidence, commits, and publication checkpoints.
- The retained [`github-project-current.yaml`](provider-mappings/github-project-current.yaml)
  is a frozen 2026-08-10 point-in-time receipt, not current provider authority.
- Open an execution workflow only after execution is authorized or durable
  cross-session execution tracking is required. A candidate issue or planning
  discussion alone is not a workflow trigger.

## Release Horizons

| Version | State | Required | Objective | Activation Gate | Workflow |
| --- | --- | --- | --- | --- | --- |
| `v0.4.1` | `published` | yes | Restore only the published package upgrade and downstream-validation contracts through `PKG-001` and `PKG-002`. | Completed at immutable tag `v0.4.1`; hosted run `29650583394` and downloaded assets passed validation. | [`2026-07-18-v0-4-1-release-publication`](../workflows/2026-07-18-v0-4-1-release-publication/workflow.yaml) |
| `v0.4.2` | `published` | yes | The immutable package, local release registry, workflow evidence, roadmap state, migration guidance, and authorized public Release body correction are complete. | Completed without moving `v0.4.2` or changing the four published assets. | [`2026-07-20-v0-4-2-release-finalization-hotfix`](../workflows/2026-07-20-v0-4-2-release-finalization-hotfix/workflow.yaml) |
| `v0.5.0` | `published` | yes | The four-source release, including exact automatic v0.4.2 upgrades, passed independent review, Windows, hosted Ubuntu, and owner-arranged macOS gates. | Completed at immutable tag `v0.5.0`, peeled commit `1477181f0b43fa7ee82fcd482141758ac9e22eb6`, successful hosted publication run `29922585651`, and a stable GitHub Release with four governed assets. | [`2026-07-22-v0-5-0-macos-portability`](../workflows/2026-07-22-v0-5-0-macos-portability/workflow.yaml) |
| `v0.6.0` | `published` | yes | The componentized downstream product, semantic customization lifecycle, software-development orchestration acceptance, coordinated CI/configuration/skill transitions, Terra evaluation, and measured simplification disposition are complete. | Completed at immutable annotated tag `v0.6.0`, peeled commit `8b98b5f917513f2d143f42a322050a1162bb63f9`, successful hosted publication run `30074558122`, and a stable GitHub Release with four governed assets. | [`2026-07-24-v0-6-0-release-publication`](../workflows/2026-07-24-v0-6-0-release-publication/workflow.yaml) |
| `v0.7.0` | `published` | yes | The provenance, portable work-management, downstream package-safety, and fail-closed release-traceability outcomes are published. Legacy identifier retirement and historical archive migration remain separately conditional. | Completed at immutable annotated tag `v0.7.0`, peeled commit `49723a943f744820f4bdb2c22de7930693a7106d`, successful hosted publication run `30363397794`, and a stable GitHub Release with four governed assets. | [`2026-07-28-v0-7-0-release-preparation`](../workflows/2026-07-28-v0-7-0-release-preparation/workflow.yaml) |
| `v0.8.0` | `published` | yes | Canonical skill-owned Python automation, fail-closed prerequisite diagnostics, and provider-neutral target-selected work-item binding and merge-gate policy are published. | Completed at immutable annotated tag `v0.8.0`, peeled commit `97ccc9e9f218ec681bb726d2e1b4edbb3e14fb25`, successful hosted run `30786537723`, exact governed public body, four unchanged assets, and Project #3 publication-field read-back. | [`2026-07-30-skill-script-colocation`](../workflows/2026-07-30-skill-script-colocation/workflow.yaml), [`2026-07-31-work-item-binding-policy`](../workflows/2026-07-31-work-item-binding-policy/workflow.yaml), [`2026-08-02-python-prerequisite-diagnostics`](../workflows/2026-08-02-python-prerequisite-diagnostics/workflow.yaml), [`2026-08-03-v0-8-0-release-publication`](../workflows/2026-08-03-v0-8-0-release-publication/workflow.yaml) |
| `v0.9.0` | `published` | yes | Published the eight completed outcomes owned by `GOV-004`, `PKG-005`, `GOV-006`, `CTX-004`, `CTX-005`, `PKG-006`, `VAL-003`, and `SAG-002`: proportional delivery governance, ignored-path package safety, layered engineering-rule ownership, bilingual bundled-provider navigation, target-effective rule packets, the bundled .NET validation provider contract, the unavailable Architecture Kit cutover gate, and canonical owning-skill reachability plus provider-neutral role execution. | Published from immutable annotated tag `v0.9.0` at `c14a326` through successful run `31027306074`. All eight canonical items read back `Done`, target `v0.9.0`, and published in `v0.9.0`. Proposals, umbrellas, leaves, #119, and online-only #128 remain traceability rather than additional Included Work. The accepted pre-tag sequence deviation is preserved in the release workflow without moving the tag. | [`2026-08-05-v0-9-0-release-publication`](../workflows/2026-08-05-v0-9-0-release-publication/workflow.yaml) |
| `v0.10.0` | `published` | yes | Published profile-driven validation selection, package content identity, and source-only release closeout contracts. | Immutable tag `v0.10.0` at `5878f213b50bdbb4b3123a60525cdc206fd5be04`, successful hosted run `31242089985`, and governed Release `REL-v0.10.0`. Its included online work is release/workflow evidence, not a retroactively inferred local backlog-item set. | [`2026-08-08-v0-10-release-publication`](../workflows/2026-08-08-v0-10-release-publication/workflow.yaml) |
| `v0.11.0` | `published` | yes | Published the product-boundary, delivery-contract, environment-readiness, and source-only closeout outcomes. | Immutable tag `v0.11.0` at `05199ed0a9ed509ef1696df014fce244f8e7cffa` and stable Release `REL-v0.11.0`; the original tagged-tree publication run remains recorded as failed, while later source-only closeout validation passed without moving the tag or assets. | [`2026-08-09-v0-11-product-boundary-delivery-evidence`](../workflows/2026-08-09-v0-11-product-boundary-delivery-evidence/workflow.yaml) |
| `v0.12.0` | `planned` | no | The current Project read-back records #150, #170, and #171 as Done/P1/target `v0.12.0`, each `Not yet published`. | A release candidate requires the owner to select an exact included-work set and authorize a release workflow. The authorized #175/#178 Phase A and #176 delivery work remain separately unallocated until that decision. | — |

## Release Gate Semantics

- A `release-blocker` is required implementation and evidence. The release
  cannot enter publication while the item is unresolved.
- A `disposition-gate` requires an explicit retained decision before release
  closure. The result may be implement, retain, defer to a named horizon, or
  reject; an unreviewed or silently dropped item fails the gate.
- An `activation-gate` must be satisfied before the named implementation work
  begins.
- These gates control completeness and decision visibility. They do not impose
  a deadline, force a version split, or create artificial time pressure.

| Version | Release Blockers | Disposition Gates | Activation Dependencies |
| --- | --- | --- | --- |
| `v0.4.2` | `R042-001`, `R042-002`, `R042-003`, `R042-004`, `R042-005` | Any selected correction that would add a schema, required validation or CI route, remove a published path, or intentionally change pass/fail semantics must stop and move to an explicit v0.5.0 item. | v0.4.1 publication and registry closeout are complete. |
| `v0.5.0` | `PKG-003`, `SAG-001`, `ENF-001`, `TOOL-001`, `LANG-001`, `REL-001`, `REL-002`, `HANDOFF-001` | `GOV-001`, `CAP-001`, `VAL-001` | R042-005 is closed; v0.4.2 workflow, independent verification, local release evidence, public Release body, and final version state are reconciled. |
| `v0.6.0` | `DIST-001`, `CUST-001`, `DEVWF-002`, `CI-001`, `CI-002`, `CFG-001`, `SKILL-001` | `SIMPL-001`; any legacy identifier retirement remains conditional and cannot be silently included. | `EVAL-001`, v0.5.0 completion, `.dev/ai-context/provenance.yaml`, `.dev/ai-context/customizations.yaml`, and the approved `software-development-orchestrator` plus `ai-context-init` compatibility transitions. |
| `v0.7.0` | `GOV-002`, `GOV-003`, `PKG-004`, `REL-003` | A historical archive migration and legacy identifier retirement each require explicit successor work rather than silent inclusion. | All four blockers are resolved and published at immutable tag `v0.7.0`; no conditional successor work was silently included. |
| `v0.8.0` | `SKILL-002`, `TOOL-002`, `WIBIND-001` (all resolved and published) | No additional scope was selected. Any fourth item still requires an explicit owner roadmap decision rather than silent inclusion. | The exact three-item set is terminally complete at immutable tag `v0.8.0`; the governed hosted body and Project #3 `Published in` read-back pass. |
| `v0.9.0` | `GOV-004`, `PKG-005`, `GOV-006`, `CTX-004`, `CTX-005`, `PKG-006`, `VAL-003`, `SAG-002` (all resolved and published in v0.9.0) | Proposal #93 remains provenance for `PKG-005`; Proposal #92 is represented by four umbrella-level canonical items; Proposal #94 remains provenance for the single aggregated `SAG-002` item represented by #118 with dependent slice #119. Proposal, umbrella, and leaf Issues must not be counted together. Issue #128 is an online-only packaged correction disclosed in release notes, not a ninth canonical item. | Immutable tag `v0.9.0` peels to `c14a326`; hosted run `31027306074`, the public Release, all four assets, adjacent checksums, and package parity passed. Project #3 records all eight items as published in v0.9.0. CTX-004 keeps source-only tests outside the payload, and Architecture Kit remains unavailable/non-selectable. |
| `v0.10.0` | Selected and published through its governed release workflow; its exact online Issue scope is owned by `REL-v0.10.0` and the linked workflow. | Do not infer missing local backlog item YAML from the published Release. | Immutable tag, hosted publication run, and Release evidence are recorded in `.dev/releases/v0.10.0/`. |
| `v0.11.0` | Selected and published through its governed release workflow; its exact online Issue scope is owned by `REL-v0.11.0` and the linked workflow. | The failed tagged-tree publication run remains immutable evidence; it was not relabeled as passed by later closeout. | Immutable tag and assets are preserved; source-only closeout evidence is recorded in `.dev/releases/v0.11.0/`. |
| `v0.12.0` | No canonical local included-work set is selected. Current Project planning records #150, #170, and #171 as Done/P1/target `v0.12.0`, all `Not yet published`. | #175, #176, and #178 are authorized delivery work but have no selected Project target-release value; do not add them to a v0.12.0 candidate without an owner decision. | A release workflow, candidate record, and publication authority remain required before any release claim. |

The 2026-08-02 owner decision promotes Proposal #69 into required v0.8.0
scope as `TOOL-002`. That decision authorizes the bounded Story delivery and
merge workflow only. The separate 2026-08-03 owner decision adds the already
integrated work-item binding policy as `WIBIND-001`, freezes the exact three-item
release set, and authorizes release preparation. It does not delegate creation,
movement, deletion, replacement, or push of the immutable release tag.

`DEVWF-001`, `INIT-001`, `EVAL-002`, `VAL-002`, and `GOV-005`
remain independent unassigned decisions. Proposal #92 is now represented in
v0.9.0 only by `GOV-006`, `CTX-005`, `PKG-006`, and `VAL-003`; its nine leaf
implementation Issues are not additional release items. Proposal #93 remains
represented only by `PKG-005`. Proposal #94 is represented only by `SAG-002`,
with #118 as its representative provider projection and #119 as its dependent
slice; neither provider record is an additional Included Work item. #98/`CTX-004`
is the eighth resolved v0.9.0 outcome. `STD-001` is planned at P1 and explicitly related to `OBS-001`,
which remains P2 and unassigned. The owner selected round one for implementation
through `GOV-004`; rounds two and three remain deliberation-only. `STD-001`,
`DEVWF-001`, and `OBS-001` are not hidden release blockers. The eight items in the
v0.9.0 release-gate row are the exact currently selected blockers. `OBS-001` may collect
architecture evidence independently, while canonical standards structure,
placement, and publication wait for the remaining applicable `STD-001`
decisions unless the owner grants an exception. Standards or dev-workflow
schema changes may receive a dedicated release after deliberation instead of
being forced into an existing horizon. Actual WorkService upgrade execution
belongs to its target repository rather than this source roadmap.

`UPG-001` was declined by owner decision on 2026-07-27 because no credible
legacy customized target or feedback capacity is expected to be available.
`INIT-001` is a distinct low-priority exploration of collision-safe
`ai-context-init` adoption for repositories that already use AI agents. It is
unassigned, independent, and not a v0.7.0 blocker.

## v0.6.0 Product And Distribution Definition

`DIST-001` is a v0.6.0 release blocker by owner decision on 2026-07-23. It
defines what the release delivers before package bytes, CI gates, or
simplification are treated as complete.

The current approved product direction has four layers:

1. a mandatory software-development core covering requirements, specifications,
   problem framing, DDD and architecture, test design, implementation, review,
   target-aware unit/integration test execution, selectable compliance
   validation, and `.dev/workflows/` lifecycle records;
2. a mandatory AI-context lifecycle core covering initialization, audit,
   target-facing governance, upgrade, provenance, customization reconciliation,
   and post-upgrade verification;
3. optional providers, beginning with repository backlog storage while allowing
   Azure DevOps, Jira, GitHub Issues/Projects, another tracker, or no repository
   backlog provider; and
4. source-only package build, publication, finalization, registry, test, and
   historical instance surfaces.

The approved model is one versioned componentized release. New installations
do not enable the repository-backlog provider unless selected; existing targets
preserve it and record the selection. Installed component identity belongs in
`.dev/ai-context/provenance.yaml`; semantic customization identity belongs in
the referenced `.dev/ai-context/customizations.yaml` ledger. Exact schemas,
migrations, and downstream fixtures remain implementation design work. Future
publication as a Python CLI
or package-registry tool is retained as deferred exploration and is not a
v0.6.0 gate.

## Repository Configuration Release Classification

`CFG-001` is assigned to v0.6.0 and will execute with `SKILL-001`. It records
Proposed `ADR-001`: source-root `.editorconfig` and
`.gitattributes` should be owned separately from downstream public-root seed
templates, and only explicitly classified immutable external originals should
receive byte-preserving Git treatment. The current per-evidence attribute is a
tactical fix, not the proposed canonical placement.

ADR acceptance, revision, or rejection remains an explicit implementation gate.
The release assignment does not pre-approve the Proposed ADR, but it closes the
former v0.5.1-versus-v0.6.0 decision.

## GitHub Workflow Review Boundary

`CI-002` records the comprehensive review of GitHub workflow triggers,
responsibilities, lifecycle ownership, duplication, concurrency, and runner
cost. PR #6 applies only the immediate correction: general Governance retains
release-tooling unit tests but no longer executes a hardcoded candidate or
finalization phase when governed documentation such as `.dev/backlog/**`
changes.

The broad backlog trigger remains intentional because a backlog change may
also alter its index, roadmap assignment, workflow references, or release
governance contract. Narrowing it to selected filenames would make valid new
items easy to omit and would not correct the lifecycle-ownership defect that
caused the failure.

The full review is assigned to v0.6.0 and combines with `CI-001` as one
release-engineering workstream by owner decision. It must reuse the short-term
regression boundary, avoid duplicating the Node.js 24 action migration, and
enforce the `DIST-001` component and release lifecycle matrix.

## Historical Release Evidence At Freeze

The first governed downstream v0.4.0 upgrade supplied newer and more direct
release evidence than the earlier planning source:

1. `dotnet-mq-arch-lab@2eeddf392ca79deb4407c47d13ad53178015ba90`
   completed the progressive v0.1.0 to v0.3.0 to v0.4.0 upgrade and retained
   workflow plus assessment evidence.
2. `PKG-001` proves that the published guide requires the v0.3.0 manifest while
   the tagged builder emits a clean-install-only `migration.yaml`; this blocks
   the advertised upgrade path.
3. `PKG-002` proves that the package includes and selects source-release tests
   whose Git history, release registry, or builder module is excluded
   downstream.
4. Both are patch-compatible defect corrections unless implementation requires
   a new schema, new required validation contract, or published-path removal.
   Such expansion must stop for v0.5.0 reclassification.
5. The historical assessment and independent Fable 5 plan remain valid planning
   inputs, but their general content corrections no longer precede these
   observed release failures.
6. By user decision, every correction originally targeted to v0.4.1 moves to
   required v0.4.2 work; the independently authored source plan is retained
   unchanged as historical planning input.
7. Migration schema 1.0.0 remains single-source in v0.4.1. `PKG-003` owns the
   v0.5.0 multi-source contract, including direct v0.4.0-to-v0.5.0 validation
   against the retained `dotnet-mq-arch-lab` consumer.
8. v0.4.2 is genuinely published from
   `f474c3b058cb9f89f93929e0732fc1f276422dd9`. `R042-005` repaired the
   post-publication finalization and, after explicit authorization, replaced
   and verified the public Release body without moving the final tag or
   changing the four published assets.
9. `ASM-20260720-001` preserves the independent Fable 5 review and confirms
   its release-finalization findings with repository-native evidence.

## Approved 2026-07-19 Gate Revision

1. v0.5.0 may not start before v0.4.2 is complete.
2. v0.4.2 contains only patch-compatible corrections. Its release workflow must
   stop and reclassify work when the smallest coherent change needs a new
   schema, required validator or CI route, published-path removal, or intentional
   pass/fail semantic change.
3. The minimum portability evidence for v0.4.2 is Windows Git Bash plus hosted
   Ubuntu. macOS requires a separately arranged environment and remains
   explicitly unverified; no artifact may imply macOS execution.
4. `TOOL-001` and `LANG-001` are v0.5.0 release blockers, not optional cleanup
   or disposition-only work.
5. Model-in-the-loop evaluation is a v0.6.0 release-side activation gate.
   Routine downstream installs and upgrades remain deterministic and model-free
   by default.
6. Cold-start release execution and cross-model or fresh-session state
   alignment are v0.5.0 release blockers under `REL-001` and `HANDOFF-001`.
   Form-compliant prose is not sufficient evidence of a validation run.
7. On 2026-07-22 the owner-arranged Fable 5 host completed the previously
   deferred macOS evidence at `main@9ac40bee`: native bash 3.2.57 quick and
   critical gates both passed 33/33. `ASM-20260722-003` preserves the raw
   report and separately reproduces its `AI_CONTEXT_PYTHON` fixture leak; the
   receiving host must not recast the attributed run as a universal platform
   or provider-runtime guarantee.

## Historical Backlog Release Targets

The backlog index is the quick catalog for target, completion, and publication
versions. Current assignments:

- `v0.4.1`: `PKG-001` and `PKG-002` were completed and published in
  `REL-v0.4.1`.
- `v0.4.2`: corrections `R042-001` through `R042-004` are published;
  `R042-005` owns post-tag finalization and keeps `published_in` unset because
  the hotfix is not part of the immutable v0.4.2 tree.
- `v0.5.0`: `PKG-003`, `SAG-001`, `ENF-001`, `TOOL-001`, `LANG-001`,
  `REL-001`, `REL-002`, `HANDOFF-001`, `GOV-001`, `CAP-001`, and `VAL-001`
  were completed and published in `REL-v0.5.0`.
- `v0.6.0`: `DIST-001` owns the release product and component definition;
  `CUST-001` owns the semantic customization ledger and four-skill lifecycle;
  `DEVWF-002` owns high-level orchestrator activation, approval pauses,
  stage-batched commit evidence, target-aware test execution, selectable spec
  compliance, conditional specialized tests, and end-to-end closeout;
  `EVAL-001` is the activation gate for `SKILL-001`, which owns coordinated
  compatible transitions from `repo-structure-sync` to `ai-context-init` and
  from `dev-workflow` to `software-development-orchestrator`;
  `CFG-001` executes with that taxonomy/configuration workstream; `SIMPL-001`
  owns measured simplification disposition; and `CI-001` plus `CI-002` own the
  complete release-automation migration and lifecycle review.
- `v0.7.0`: `GOV-003` records the completed AI execution provenance policy;
  `GOV-002` records the independently verified portable/source-only/target-
  customization/deferred-provider disposition; `PKG-004` records the
  deterministic payload, clean-install, and initialized-upgrade proof; and
  `REL-003` records the fail-closed canonical backlog and Included Work
  contract. All four are resolved and published in `v0.7.0`. Historical archive
  migration and legacy identifier retirement remain conditional and require
  separately approved successor work.
- `v0.8.0`: `SKILL-002` owns compatibility-safe colocation of single-owner
  Python automation and contract tests under canonical skill directories and
  is merged and complete. `TOOL-002` owns the fail-closed Python runtime and
  dependency diagnostics for all governed validator entrypoints and is merged,
  resolved, and published. `WIBIND-001` owns provider-neutral work-
  item binding plus independently selected merge-gate policy and is merged,
  resolved, and published. The exact three-item release is immutable at tag
  `v0.8.0`; governed public-body equality, provider reconciliation, and
  terminal finalization are complete.
- `v0.9.0`: `GOV-004` owns proportional workflow and delivery topology;
  `PKG-005` owns fail-closed ignored framework-managed paths; `GOV-006` owns
  normalized engineering-rule identity, ownership, and file-level migration;
  `CTX-005` owns target-effective rule state, deterministic packets, and shared
  action-skill consumption; `PKG-006` owns the stable bundled .NET validation
  provider and reference-in-place activation contract; `CTX-004` owns stable
  bilingual root navigation to that provider; and `VAL-003` owns the
  unavailable-by-default Architecture Kit readiness gate. Together with
  `GOV-004`, `PKG-005`, and `SAG-002`, these form the exact eight-item Included
  Work set. Proposal #92, umbrellas'
  child Issues #109–#117, and actual Architecture Kit cutover are not additional
  Included Work.
- `unassigned`: `DEVWF-001` owns optional issue/timeline schema deliberation;
  `INIT-001` owns existing-AI-agent initialization compatibility, collision
  inventory, dry-run, and synthetic fixtures; `EVAL-002` owns comparable
  execution evidence; `VAL-002` owns validation profile separation;
  `GOV-005` owns one Proposal-queue convergence decision; planned `STD-001` owns three
  bounded standards deliberation rounds and release allocation; and `OBS-001`
  remains a related but separately owned architecture workflow. None is a
  mandatory closeout gate for an assigned release.
- `declined`: `UPG-001` retains its historical assessment and intake evidence
  but no longer represents planned execution.
- Resolved `AIC-007` and `CTX-001` through `CTX-003` were first completed and
  published in `v0.1.0`, verified by Git tag ancestry.

## Sub-Agent Runtime Integration Timing

- `v0.4.2`: correct only the existing `context-translator` routing/catalog
  omission. This is a contract-preserving documentation patch and does not
  authorize new adapter semantics or bulk wrapper generation.
- `v0.5.0`: execute `SAG-001` to define dynamic versus runtime-native role
  integration, add exact adapter metadata and parity validation, verify package
  coverage, and record explicit role-by-role promotion decisions. This contract
  is complete: 17 roles remain dynamic and only `context-translator` maps
  exact Codex, Claude, and Copilot adapters.
- `v0.6.0`: consume the stabilized contract during skill-family taxonomy work.
  Taxonomy grouping or renaming does not automatically promote a role to a
  runtime-native adapter.

## AI Behavior Evaluation And Token Cost Boundary

- Deterministic structure and contract checks are the mandatory complete
  baseline and require no model call.
- Model-in-the-loop evaluation runs on release candidates or explicitly
  requested full evaluations. It does not run during a normal downstream
  upgrade.
- The release workflow must approve the model, judge, repetitions, fixture
  sampling, maximum token budget, acceptance threshold, and result retention
  before executing model calls.
- Empty, existing, and copied-template repositories form the minimum fixture
  families. Deterministic coverage applies to the complete declared corpus;
  model evaluation may use an approved representative sample to bound cost.
- Stochastic results are comparative evidence, not a sole oracle. A single
  model pass cannot override deterministic regression failure.

## Simplification, Archive, And Standards Sequencing

`SIMPL-001` distinguishes repository corpus size from context actually loaded
into an agent session. Fable 5's word-count baseline is useful for discovery,
but it does not prove that completed workflows, assessments, or long references
are paid as prompt tokens on every run. v0.6.0 therefore measures representative
runtime, release, handoff, routing, and development sessions before accepting
token-savings claims.

Historical compression is conditional v0.7.0 work for five reasons:

1. completed workflow and assessment records are normally reached through
   indexes or explicit evidence lookup rather than loaded by default;
2. the v0.4.2 incident required historical records to reconstruct tag, run,
   commit, handoff, and finalization truth;
3. stable repository-relative references currently bind backlog, workflow,
   assessment, release, and Git-search evidence;
4. an archive branch or Git history alone is less deterministic for fresh
   agents and external reviewers than file-backed evidence; and
5. indexes or discovery routing may remove most operational noise without
   accepting migration and auditability risk.

v0.6.0 may reduce default discovery while preserving stable files. Moving,
deleting, summarizing, or replacing full historical evidence requires a
separate v0.7.0 item with measured benefit, a retention policy, immutable
manifest/digests, stable summaries and redirects, reference validation,
restore/lookup behavior, and downstream migration evidence.

Standards simplification is not normal token cleanup. Standards are a core
software-development capability of this framework. `STD-001` remains
unassigned for release allocation; workflow proportionality is now implemented
through `GOV-004`, while code-review progressive disclosure and terminology
discovery remain bounded rounds. `OBS-001` may perform read-only architecture
exploration in parallel, but applicable remaining standards-format decisions
precede its canonical standards publication unless the owner grants an
exception. Only after each round's accepted doctrine, validator impact,
examples, compatibility, and migration boundaries are understood may the owner
assign that round's implementation to an existing or dedicated release.

## Historical Last Recorded Next Action

The owner allocated `v0.9.0` on 2026-08-04 with `GOV-004` and `PKG-005`, then
on 2026-08-05 added the completed #92 umbrella outcomes as `GOV-006`, `CTX-005`,
`PKG-006`, and `VAL-003`, confirmed the completed Issue #94 delivery as
`SAG-002`, and then added the completed bilingual provider navigation as
`CTX-004`. The published v0.9.0 release includes `GOV-004`, `PKG-005`,
`GOV-006`, `CTX-004`, `CTX-005`, `PKG-006`, `VAL-003`, and `SAG-002` exactly
once each.
Proposal #92 and #109–#117 implementation slices must not be counted as
additional Included Work; #104–#107 are the one-to-one provider projections
of the four #92 canonical items. Proposal #94 and dependent #119 are not
additional Included Work; #118 is the sole provider projection for `SAG-002`.
The owner created immutable tag `v0.9.0`; hosted publication and registry
closeout completed on 2026-08-06. Actual Architecture Kit cutover and
additional scope remain unauthorized.

Keep `REL-004`, `DEVWF-001`, `INIT-001`, the related but separately owned
`STD-001` and `OBS-001`, historical archive migration, and legacy identifier
retirement independently gated unless a later explicit owner decision assigns
them to v0.9.0 or another release.
