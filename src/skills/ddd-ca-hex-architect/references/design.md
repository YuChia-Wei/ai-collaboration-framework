# Design a bounded architecture

## Selected installed knowledge for design

For requested knowledge coverage, take the caller's explicit installed lock and
selection, `project_root`, capability `architecture`, operation `design`,
execution-mode, affected paths/file types, requested coverage and permitted
target authority inputs. Use the distribution reader's verified installed resource index and
binding observations. Without a verified selected installation or reader observation,
continue only common work and report requested specialist coverage unavailable;
do not fall back to source-tree package links or infer technology from a suffix.

Treat metadata-4 `knowledge_consumption` resources as an allowed set, not an
instruction to load it all. Intersect that set with selected packages, matching capability/operation/execution-mode,
path-prefix, technology-profile and file-type selectors, and this task; load only the resource IDs
needed for this subject. Verify each selected member's raw identity and the
binding's raw target-authority identity through that verified reader. Interpret
knowledge as guidance and examples as illustrations. A normative rule requires
an adopted binding and the existing target-owned resolver/gate; the source
catalog alone cannot adopt it. Preserve conditional applicability as conditional.
Stale, ambiguous or conflicting authority blocks the affected normative
coverage; do not create a replacement rule parser or ask again for unchanged
saved adoption.

Return a transient result with `status` (available, unavailable or blocked),
`loaded_resources` (package, version, resource ID, member, SHA-256, use_as),
`applicable_rule_ids`, `conditional_rule_ids`, `authorities` (path, SHA-256,
selector), `coverage` (capability, operation, technology profile, status,
missing) and bounded `diagnostics` (code, relative path or null, reason, next
action). Name each missing package, resource, authority, rule or target predicate
needed for requested coverage. Optional absence is unavailable; required
specialist gaps cannot be reported as covered. Continue unaffected common work
with the limit disclosed. Keep this result in the conversation unless the
actual task authorizes persistence; never save installation/configuration
implicitly.

## Inputs and authority

Confirm business capability/module, requested new design or revision, source
requirements/AC IDs, known workload, quality constraints, adopted architecture,
existing decisions and compatibility obligations. Separate source facts,
observed behavior, assumptions and proposed decisions. Existing code does not
override an accepted requirement by existing.

Use explicit target sources for this scope; no directory or registry is
mandatory. Conflicting or missing authority stops the dependent decision:
present bounded options and identify the decision owner. Reuse accepted choices
rather than reopening them merely because a class is added.

Use DDD for language, responsibility and invariant ownership; Clean Architecture
for dependency direction; Hexagonal Architecture for ports and external
adapters. These lenses do not make every pattern mandatory. CQRS, event
sourcing, a broker, physical project splits, ORM and DI API need target
selection. This package has no technology supplement. Apply selected supplied
guidance only within scope; report missing specialist coverage and leave the
affected required acceptance unresolved.

## Design sequence

1. Describe capability, actors, trigger, result and measurable acceptance.
   Preserve business vocabulary and label unconfirmed terms. Name ownership of
   data and decisions rather than treating a folder as the boundary.
2. Identify invariants and constrained state. Propose aggregate/module
   boundaries where responsibility or consistency warrants them. Explain what
   must be atomic and which intermediate states are acceptable.
3. Place inbound application ports and outbound dependency ports. Keep business
   decisions independent of transport, persistence and vendor APIs. Give each
   abstraction a purpose such as a stable dependency boundary or controllable
   failure/time/data seam; avoid speculative interfaces.
4. Describe commands, queries or reactions only when needed by the chosen
   model. Specify input/output, errors, transitions, transaction owner, external
   effects and dependency lifetimes relevant to correctness.
5. Compare credible alternatives, including the simpler valid option. State
   benefits, costs, operational burden, rejected choices and the evidence or
   assumption driving the recommendation.
6. Walk relevant failure windows: commit versus publish, retry, duplicates,
   ordering, partial failure, cancellation, recovery and observability. Record
   actual guarantees; do not assume exactly-once delivery. Compare coordination
   or compensation against invariants for cross-owner effects.
7. For existing consumers, explain compatibility, versioning, rollout order,
   migration/recovery and rollback limits when relevant. A proposal authorizes
   none of these actions.
8. Define observable acceptance and evidence needs. Distinguish controlled
   tests from required real storage/messaging/integration evidence and record
   feasibility limits.

## Scale the deliverable

| Requested subject | Include when relevant |
| --- | --- |
| Bounded context/module | Purpose, owner, vocabulary, aggregates/invariants, ports, adapters, integrations and target-selected placement. |
| Aggregate or major refactor | Responsibility, entities/value objects, behavior/events, consistency, persistence decision and regression risks. |
| Command/query/reaction | Trigger/input, application responsibility, domain/projection logic, outbound effects, result/error and acceptance. |
| Messaging integration | Producer/consumer ownership, payload, guarantees, duplicate/order policy, transaction/publish boundary, retry and recovery. |

Return a coherent proposal with source bindings, alternatives, assumptions,
recommendation, unresolved owner decisions and validation needs. Label choices
proposed until accepted by the target owner. Use a diagram when it clarifies
dependencies or effects. Default to conversation; persist only at a selected
authorized destination with an available editor.

Use [review criteria](review.md) as an author self-check when useful and label
it self-check. It is not independent review, implementation or specification
compliance. Optional ADR/knowledge persistence is a separate selected handoff:
return decision context, options, consequences, status and sources when no
persistence capability is available. Accepted designs can pass to an
implementation owner with existing permission and open questions; proposals
never silently become accepted target truth.
