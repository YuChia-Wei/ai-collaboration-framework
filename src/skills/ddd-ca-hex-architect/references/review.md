# Review a fixed architecture artifact

## Selected installed knowledge for review

For requested knowledge coverage, take the caller's explicit installed lock and
selection, `project_root`, capability `architecture`, operation `review`,
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

Bind the path/version and digest, or quote bounded inline input, before review.
Record requirements, decisions, quality constraints and coverage separately:
artifact claims cannot validate themselves. Leave the subject unchanged. If
revision is also requested, finish this result before [design](design.md)
revises it; a later review must bind the revised subject.

Apply relevant common criteria and selected target rules. Missing authority
blocks the affected judgment. This package has no technology extension; report
missing selected specialist coverage and do not substitute common reasoning for
a required specialist gate. A different valid style, unadopted CQRS or absence
of a speculative abstraction is not a defect.

| Criterion | Evidence and questions |
| --- | --- |
| Requirements and quality | Bind decisions to requirements/ACs and measurable constraints. Which workload/availability claims remain assumptions? |
| Responsibility and language | Does each context/module have an owner, coherent vocabulary and purpose? Are disputed terms or shared responsibilities explicit? |
| Dependencies and ports | Does dependency direction protect business decisions? Are external adapters isolated where needed? Does each abstraction have a purpose? |
| Data and consistency | Who owns state/invariants? Do aggregate/transaction boundaries and intermediate states meet the consistency requirement? |
| Alternatives | Are credible options and simpler valid designs considered with costs/consequences? Is preference masquerading as a requirement? |
| Failure and recovery | Are relevant retry, duplicates, ordering, durability, compensation, observability and operational ownership explicit? Are guarantees supported? |
| Evolution | Where needed, are compatibility, rollout, migration, recovery and rollback limits coherent for existing consumers? |
| Testability | Are outcomes observable and dependency/time/data seams controllable? Is real integration evidence distinguished from mocks? |

Each supported finding needs location, criterion/source requirement, evidence,
triggering condition, impact, severity rationale, uncertainty and bounded
correction. Distinguish defects, questions and optional improvements; retain
valid alternatives and their tradeoffs. Review artifacts here; executable-code
review is a separate responsibility. Do not invent a requirement/vendor choice
to make a proposal pass.

Return subject, sources, findings, criterion coverage, unavailable/excluded
coverage, assumptions and exact unresolved decisions. State actual inspections,
commands and limits. No findings means none supported in the inspected scope,
not compliance or acceptance. A digest proves identity, not execution or
independent authorship.

Select one classification with supporting author relationship:

- `self-check` if the reviewer authored or repaired the subject.
- `review; independence not established` when author relationship or required
  independence evidence is unknown.
- `independent-review` only when a different author, fixed subject, read-only
  reviewer and applicable target independence requirements are evidenced.

A different prompt/model alone establishes no independence. This method creates
no mandatory audit packet; required target acceptance remains separate.
Optional handoff names affected artifact, source IDs, proposed correction,
decision owner and existing revision/implementation permission. Return that
semantic handoff when another skill is unavailable. It cannot enlarge scope
or turn proposed architecture into accepted truth.
