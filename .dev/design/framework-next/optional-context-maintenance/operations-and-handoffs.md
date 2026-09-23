# Operations, persistence and knowledge handoffs

The [auditor](drafts/ai-context-auditor/SKILL.md) and
[governance](drafts/ai-context-governance/SKILL.md) are design specimens.
Future metadata-v3 uses configuration null, empty artifact_roles/schemas/templates/
tools, and empty required/optional dependencies. Prose guidance is a reference,
not a machine artifact role. No Python, provider, store or common runtime is needed.

## Operation contract

| Package / operation | Inputs | Useful output | Mutation boundary |
| --- | --- | --- | --- |
| auditor / audit | Explicit context scope, relevant authority, question/intended behavior, available subject evidence; optional presentation/export | Prioritized findings with location, trigger, impact, evidence, uncertainty and coverage | Audited context read-only; requested export only to its selected destination. |
| auditor / compare | Two identified subjects, or a prior report plus current subject; selected findings and comparison question | Confirmed/changed/resolved/unresolved observations mapped to prior identities and evidence | No baseline rewrite or automatic independent-verification/closure claim. |
| governance / propose | Selected finding/problem or direct request, named files, ownership and intended behavior | Reviewable before/after text, authority/source binding, consequences and unresolved decisions | Chat by default; proposal export only if requested. No rule/tracking mutation. |
| governance / apply | Concrete authorized proposal or bounded direct edit, project-owned files, applicable authority and current bytes | Actual changes, source/decision references, direct checks and remaining limits | Accepted radius only; no protected core, install/update, source release or provider writes. |

A direct edit request need not create a proposal artifact. Neither skill requires
the other. Compare can read the caller's report without owning its storage.
Missing requested tool, format, coverage or independent review is explicitly
unavailable/unresolved, not silently replaced with another engine.

## Caller paths, templates and tracking

1. Resolve named scope and relevant authority. Read concrete dependencies when a
   finding/edit needs them; do not scan all documents to calculate effective rules.
2. Use a caller template as inert presentation. Preserve source/status/identity
   distinctions; report conflicts instead of filling approval/evidence placeholders.
3. No destination means conversation. Requested export uses a project-owned path.
   If project conventions cannot resolve a missing destination, prepare the content
   and seek that destination; do not universally choose .dev/assessments.
4. Inspect ownership, containment, links, existing contents and relevant current
   bytes before writing. Preserve unrelated work and final records. Collisions or
   stale content require reconciliation. New exports do not replace final reports.
   Instruction editing claims no lock/CAS or multi-file transaction.
5. Follow caller-selected tracking (none, existing Issue/workflow or project
   surface) within authorization. Export alone does not require a branch, workflow,
   index, Issue, audit or receipt. Actual project policy may require them.
6. Run only task-authorized checks selected by project contract. Record actual
   command/result/limits; failed, unavailable, deferred and not-run are not passed.
   A read-only audit does not implicitly execute a mutating check.

Prose states subject/revision or observed file identity, freshness time when
material, scope/exclusions, source locations, findings/uncertainty, actual checks
and next action. Dirty subjects are identified: HEAD alone does not bind dirty
bytes. Retained finding labels stay stable within their report and are cited
with project identity/path plus immutable revision or digest where available.
No invented global ASM ID or schema version. Editorial final is not mechanical
immutability enforcement.

### Reusing a project format

The caller names format/version, owner, destination, public operation and lifecycle
intent. Map observations into supported fields, exposing unrepresentable facts.
Use the owner-supported operation under actual authority. No generic parser,
query scanner, finalizer, schema upgrade or arbitrary JSON patch is supplied.

The existing format owner owns producer/writer, reader/query, validator,
finalization, version and migration; the project owns semantic acceptance.
Preserve IDs, creation times, assessed subjects, final conclusions and supported
revision/successor relationships. If that contract cannot be established, return
prose/mapping and leave records intact. Structural validity proves no execution.

## Optional P3 knowledge handoffs

These are semantic candidates, not executable JSON with invented hashes. They
follow the selected P4 handoff boundary and actual P3 contracts (E07-E10).

| Destination | Candidate | Public sequence after caller selection | Limit |
| --- | --- | --- | --- |
| ADR 0.1.0 | Context, drivers, at least two real alternatives, benefits/costs, consequences, evidence, applicability/exclusions | Read selected config/operations, actual query and new-identity decision, create draft or revise a draft using its real digest. decide later reads actual configured decision evidence. | Acceptance is not implementation, rule adoption or runtime effect. |
| Lesson 0.2.0 | Observation, evidence, conclusion, applicability/exclusions, honest confidence and follow-up | Actual query/identity decision; create/revise candidate or explicitly derive a new candidate. accept reads real project decision evidence. | Accepted Lesson is not a rule; v1 remains read-only history. |
| standards-promotion 0.1.0 | Existing target rule/baseline, full replacement, rationale, applicability, sources and conflicts | Actual query/identity decision; propose captures selected config, target and source bytes. reconcile later reads adoption source, rule bytes and effect source. | Proposal cannot edit a rule, author its own adoption/effect evidence or prove enforcement. |

Before any invocation, read the installed version's public interface, requirements,
explicit project/package/config/write roots and actual query/expected digests.
Maintenance never imports private functions, fabricates query decisions or
configures another package. Absent capability/runtime leaves a useful candidate
and handoff not executed; installation remains a separate choice.

Do not create all three records automatically. Lesson captures learning; ADR
records a decision with alternatives; promotion proposes an existing rule change.
Current promotion requires an existing target: new-rule creation belongs to the
project's explicit process. Never create a dummy rule to satisfy the tool.

Conversation-only content is not a file snapshot for promotion. A caller-authorized
export into selected evidence roots may supply bytes; otherwise retain the
semantic handoff. ADR/Lesson evidence references are inert and do not verify the
cited source automatically.

Record only real receiving-operation references/outcomes after invocation.
Uncertain/failed writes require read-back before retry, not a completed handoff.
Keep proposal, owner adoption, actual rule bytes and declared effect separate.
Governance may perform an authorized project rule edit through the project process
but cannot invent adoption/effect evidence. P3 effective means observed
project-declared effect, not runtime consumption/enforcement proof.

## Concrete absence examples

- Conflicting instructions: auditor reads selected files and authority, returns
  evidence and uncertainty in chat; no ledger or workflow.
- Authorized project link repair: governance checks named ownership/files, repairs
  the link and reports read-back; no package-mandated audit or ADR.
- Rule replacement: governance prepares before/after and tradeoffs. Optional
  promotion captures real existing target/source evidence; adoption/edit/effect
  remain separate.
- Pending old upgrade: identify its owner without resuming/converting/deleting it.
  Preserve original recovery and hand the affected transition to P6.
