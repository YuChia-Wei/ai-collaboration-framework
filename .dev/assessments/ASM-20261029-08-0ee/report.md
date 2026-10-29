# Skills and knowledge baseline assessment — #516

Assessment: `ASM-20261029-08-0ee`. Subject: Framework
`0ee07d8314c55a95c99428fa8d4fd12c4673c04c`, clean `main` at intake on
2026-10-29 (Asia/Taipei). Conclusions below concern that immutable source,
before #518 edits. This is an author assessment, not independent review.

## Result and evidence boundary

The #516 analysis is complete. Existing domain/architecture separation is retained.
The remaining work is bounded policy/source explanation (#518), reconstruction
semantics (#519), selected resource access and adoption decisions (#515), delivery
methods (#443), and explicit ArchPrecept integration (#179). No conclusion here
claims these repairs, downstream adoption, model behavior or publication completed.

Sources: current tracked files; live Issues #515/#516/#518/#179/#443/#460;
the historical `.dev/design/skill-evolution-2026-10-22/review-follow-up.md`;
the caller-selected `.ai/project/installation.json`; and official publications
listed below. `evidence/skill-inventory.json` records source skill versions,
operations and exact knowledge consumption rows. The inventory includes source-only
experiments; directory presence is not distribution or installation selection.

Source knowledge: `engineering-common@0.4.0` (34 members),
`dotnet-backend@0.1.6` (246 members). Installed selection: 17 skills, Codex/Claude
adapters, no knowledge and no bindings. The retired combined architect is absent;
`domain-model-designer@0.1.1` and `software-architect@0.1.1` exist as separate
source and installed entries. The installed catalog identifies source `7e79f29b`;
this is separate from the assessed source HEAD. No installation mutation occurred.

Code discovery for the narrow R26-3 comparison used freshly indexed
`issue516-distribution` (`src/distribution`, 690 nodes, 4564 edges, no skips),
then the `derive_subset` source snippet. Non-code evidence used tracked YAML/Markdown.
No negative graph search is an absence proof.

## Historical observations reconciled

| Prior observation | Current evidence and disposition | Remaining scope |
|---|---|---|
| R26-1 empty installed directories | Migration concern remains distinct from managed file identity; no directory cleanup is necessary for this request. | Preserve custom files; no installer change. |
| R26-2 installed combined architect | Changed/resolved for this checkout: installation selection and generated entries now select both separate skills. | Do not repeat the split or infer another target upgraded. |
| R26-3 missing `unavailable` on public derive | Resolved in source: `src/distribution/catalog.py:603` copies resolver output into the public result; CLI emits that result. | No reimplementation; source inspection is not a fresh consumer trial. |
| S1 exact pins | Current metadata still uses exact knowledge versions. | Compare exact pins versus compatible ranges only if separately selected; retain exact pins for #518. |
| S2 behavior fixtures | Instruction structure and historical unit/install reports do not establish current model operation. | Four bounded cases below; no blanket model/CI matrix. |
| S3/S5 role split | Domain explores language/invariants; architect owns mechanisms; orchestrator selects stages. Source role/instruction boundaries exist. | No new system/DevOps skill justified by the observed gaps. |
| S4 capability/authority | `references/knowledge.md` separates installed reader, allowlist, bindings and target authority. | Make missing resources explicit; readable does not mean adopted. |
| F1/F2 accepted decisions and self-install | Current domain and architecture design instructions preserve accepted sources and return unresolved choices to owners. Installed selection is explicit. | Reuse accepted input; source edit does not authorize self-update. |
| F3/F6 delivery/workflow | SQLite workflow work has a separate current source policy and completed native records. Generic delivery methods remain #443. | Do not treat workflow storage or source release procedures as portable deployment delivery. |
| F4/F5 historical navigation/old Issues | Historical references remain provenance; #179 now explicitly names ArchPrecept and optional integration. | No historical rewrite or broad Issue cleanup. |

## Findings and exact owner mapping

Paths below are under `src/knowledge/` unless marked otherwise. Heading anchors
identify owner sections at the subject SHA, independently of later line movement.

| ID / confidence | Owner and observation | Impact and disposition |
|---|---|---|
| K01 / high | `dotnet-backend/standards/coding-standards/repository-standards.md`, Aggregate Repository / Canonical Contract: only identity load/save; Query Repository separates criteria/DTO; batch/UoW are already separate. | Preserve contract; add reasons, costs and methodology boundary in #518. Criteria finder is not accepted merely because DDD permits richer repositories. |
| K02 / high | `dotnet-backend/standards/USECASE-COMMAND-HANDLER-RELATIONSHIP.MD`, Core Conclusions / Use Case Contract; `coding-standards/usecase-standards.md`, Input / MUST Rules; `controller-standards.md`, Overview. | Existing direct UseCase and thin Handler shape is selected policy. Universal Command-as-transport wording overstates role identity. Correct attribution without allowing AppCommand as canonical Input or allowing UseCase chaining (#518). |
| K03 / high | `coding-standards/mapper-standards.md`, Pattern Markers / Use Static Methods: required marker and SHOULD conflict; markers claim actual scripts. | Align static-only pure object Mapper policy and qualify mechanical claims. Static does not prove purity, determinism or round-trip completeness (#518). |
| K04 / high | Same Mapper owner, Domain Events and Metadata / Reconstruction / Error Handling, especially lines 255–256 and 299–339. Clear is required when cleanliness is unknown; catch/continue protects identity but not all invariants. | Confirmed separate #519 defect scope. Repair must bind constructor/replay/pending semantics and reject incomplete invariant state. #518 does not claim this repair. |
| K05 / high | `coding-standards/aggregate-standards.md`, Automated Check Boundaries / constructor example / Value Object Immutability. DBA1009 uses a name-based description with no product revision; static factory is universally marked incorrect; record comment overstates immutability. | Version the observation; qualify constructor policy and source gap, fix record guarantee, preserve VO value/immutability intent (#518). |
| K06 / high | `USECASE-COMMAND-HANDLER-RELATIONSHIP.MD`, Cross-BC Flow: MQ required. `design/architecture-playbook.md`, Primary Style / Repo Constraints: MQ-first plus RabbitMQ/Kafka-only. Common `ddd/strategic-design.md`, Keep exchange semantics separate from transport, leaves transport to target. | Separate common principle from selected .NET restriction and expose broker-only scope mismatch. Reasons sufficient for a blanket mandate are missing. #518 must not adopt HTTP/RPC or a new universal ban. |
| K07 / high | `coding-standards/projection-standards.md`, Core Rules / Candidate IDs; Repository role table already separates query and capability writer. | Preserve read-only reader and reload/revalidate. Clarify read-store projector versus reader without claiming all projection text is wrong (#518 overview; #519 reconstruction/failure detail). |
| K08 / high | Common `ddd/README.md`, Conceptual sources cites Evans without explicit license/adaptation notice; .NET owner policies lack a source/interpretation/predicate comparison. | Supply official-source register, CC attribution, policy reasons and representative counterexamples (#518); reject unverified mirrors. |
| K09 / high | `src/skills/software-architect/skill-package.yaml`, dotnet-software-architecture: allows UseCase standards, but not its relationship owner, Controller or Repository owners. Reviewer/implementer allow Controller and Repository but not the relationship document. | Missing semantic inputs for selected .NET design/review. Recommend these three exact resources for architect; relationship resource for direct consumers that already rely on it. No full playbook permission; final allowlist adoption belongs to #515. |
| K10 / high | .NET catalog `unpacketized_documents` preserves Controller/Mapper/Repository identity-allocation-required; installed selection has no knowledge/bindings. | An instruction read, catalog hash or zero diagnostic cannot grant normative coverage. Keep existing Rule IDs; promotion is an owner decision (#515). |

## Minimum resources and unresolved decisions

For a .NET architecture operation judging ingress and persistence boundaries,
the relationship owner, Controller owner and Repository owner are directly necessary:
the first supplies the shape and exceptions, the second transport constraints,
the third write/query/batch semantics. Existing UseCase standards are insufficient
because their link does not extend the allowed resource set. The complete
architecture playbook contains unrelated testing, DI and broker choices and is
not a minimum dependency. Review/implementation consumers need the relationship
owner when interpreting UseCase standards. Source authors may inspect these files
as their task subject; this does not bypass an installed consumer's protocol.

Keep these questions open, with owner #515: allocate stable identities for any
currently unregistered guidance, or retain guidance with explicit adoption?
Expand only the identified consumer resources, or deliver a smaller bounded
resource preserving the same owner? Retain exact pins or later implement compatible
ranges with reproducibility rules? No analysis result chooses an engine change.
For #518, use existing exact pins and keep rule strength/adoption unchanged.

Factory and cross-BC questions remain open under #518: which creation lifecycle
requires a public constructor; how invariant completion, rehydration and alternate
named creation compare; which availability/latency/ordering requirements justify
MQ-only and which justify named brokers. Compare HTTP/RPC/module ports only as
unselected alternatives. Missing rationale does not accept them or make them DDD violations.

## Bounded case plan (not executed model acceptance)

| Case | Input / expected result / limitation |
|---|---|
| B1 ingress and policy | Selected .NET policy, HTTP command, pure AppCommand and a message entry. Expect direct UseCase, dedicated Input, thin message adapter; pure AppCommand is not inherently transport but still fails Input shape. Prohibit UseCase chaining. One author walkthrough tests document interpretability, not all models. |
| B2 resource/authority | Run the same design request with knowledge absent, wrong version, inaccessible relationship resource, then conflicting target binding. Expect unavailable/blocked scope and unaffected common reasoning; never silently source-read or override authority. Reader/unit checks are structural, separate from actor behavior. |
| B3 modeling and persistence | Accepted invariant, candidate IDs, concurrent changes, dual narrow adapter versus wide mixed consumer. Expect reload/revalidate, no criteria finder in Aggregate port, narrow consumer dependencies, explicit consistency decision. No runtime concurrency proof. |
| B4 method handoff | Existing accepted order-cancellation model, shared GWT example and asynchronous external refund. Expect architecture to preserve domain decisions and separate local acceptance from external completion; test design specifies oracle only when requested. No forced skill pipeline or fabricated business acceptance. |

Recommend a concise adoption example naming selected package/version/resource,
target authority and unavailable coverage rather than copying a full playbook.
Actual multi-model evaluation is not required to finish this analysis and remains
unexecuted; packaging checks alone must not later be reported as B1–B4 actor acceptance.

## ArchPrecept and adjacent delivery

Framework supplies optional knowledge, policy and binding semantics. ArchPrecept
owns Contracts, rule implementation, severity/profile/role evidence and Diagnostics;
the inspected application owns invariants, runtime behavior and adoption. #179
owns package/feed/source provenance, compatibility fixtures and package-free/custom
paths. Installing either product does not establish the other product's contract.

Read-only reference: ArchPrecept clean local source
`60330242f7f690a01cfa2332b578aac35584f067`, described by Git as
`v0.0.3-preview-8-g6033024`; build version still `0.0.3-preview`. Its current
DBA1009 document describes canonical When override identity, unlike the old
Framework name-only summary. DBA1018/1019 describe bounded declared-state checks
and unknown/not-evaluated paths. These are source documentation observations,
not proof this revision is the published 0.0.3-preview package. #518 should link
this immutable revision and avoid copying a second predicate catalog. #179 must
select and validate the actual published package independently. ArchPrecept preview
renumbering policy does not supersede Framework's released identities.

#443 remains necessary: the complete common member inventory contains runbook and
boundary guidance, not the requested delivery/deployment model and paired examples.
`src/distribution/templates/release-readme.md`, `docs/installation.md` and
`docs/recovery.md` cover Framework artifact/install identity, not generic multi-environment
deployment and rollback history. Deliver its manifest and synthetic Framework/Board
examples as an independent slice; no actual Board deployment is prerequisite.
#460 remains an unaccepted proposal: `problem-frame-author` offers bounded CBF
draft/snapshot operations, not a general Problem Frames topic. Common package has
no selected Problem Frames topic. Do not add a skill, migrate CBF or allocate a
version from this observation. #443 required scope and #460 proposal status differ.

## Official-source qualification

Use author/publisher/official organization resources; no third-party PDF mirror
or unidentified manuscript was used as authority. Preserve the requested source,
version and printed page context. The directly checked Domain Language DDD Reference
2015-03 page/PDF specifies CC BY 4.0; Pattern Summaries has a separate license.
Attribution must name Eric Evans, work, original URL, license, and adaptation.
Other author articles are linked with original short summaries; no diagrams,
code, full text or translated chapters are redistributed. Public access is not
an open reproduction license. Source silence proves neither a ban nor unrestricted legality.

Official inputs checked: [DDD Reference](https://www.domainlanguage.com/ddd/reference/)
and [2015-03 PDF](https://www.domainlanguage.com/wp-content/uploads/2016/05/DDD_Reference_2015-03.pdf)
(printed pp.12,16–18); [Clean Architecture, 2012-08-13](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html);
[Hexagonal Architecture, 2005 report](https://alistair.cockburn.us/hexagonal-architecture);
[Solid Relevance, 2020-10-18](https://blog.cleancoder.com/uncle-bob/2020/10/18/Solid-Relevance.html);
[Data Mapper, 2003-03-05](https://martinfowler.com/eaaCatalog/dataMapper.html).

## Acceptance and delivery slices

| #516 criterion | Analysis outcome / evidence |
|---|---|
| AC01 | Covered: fixed source, inventory, installed selection and historical disposition table. |
| AC02 | Covered: K09 and minimum-resource analysis; no full playbook permission. |
| AC03 | Covered: B1–B4 plan and compact adoption example recommendation, expected outcomes and limits. |
| AC04 | Covered: explicit unresolved identity/pin/resource/skill questions; no preselected new mechanism. |
| AC05 | Covered: three-owner ArchPrecept mapping and #179 integration boundary. |
| AC06 | Covered: #443 required method scope versus #460 unaccepted candidate. |
| AC07 | Covered: K01–K10 mapped to independent slices #518/#519/#515/#443/#179. |
| AC08 | Covered: official sources and reproduction boundaries above. |
| AC09 | Covered: fixed owner paths/headings, current observation, impact and owning Issue per finding. |
| AC10 | Covered: selected form policy, invariants, bounded predicates and unregistered guidance distinguished. |

Preserve already correct invariant ownership, explicit consistency, single-Aggregate
default and documented strong-consistency exception, Domain Event versus async/ES,
query candidate revalidation, optional knowledge and target authority. No product
tests were necessary for this read-only semantic assessment. A scoped locator/link
check is required for the new report; subsequent #518 metadata changes need their
direct distribution checks. Analysis complete is not Issue closure or remediation.
