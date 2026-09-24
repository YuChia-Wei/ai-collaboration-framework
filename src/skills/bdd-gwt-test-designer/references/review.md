# Review a fixed scenario artifact

## Selected installed knowledge for review

For requested knowledge coverage, take the caller's explicit installed lock and
selection, `project_root`, capability `test-design`, operation `review`,
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

Bind the artifact path/version and digest, or quote bounded inline scenarios.
Record requirements/ACs, source revision/status, coverage and target conventions
separately. Leave the artifact unchanged. For authorized revision, finish this
review before [designing the revision](design.md); later review binds that new
subject.

| Criterion | Inspect for |
| --- | --- |
| Traceability | Each scenario has a source requirement or labeled assumption; each in-scope AC has coverage or a gap. Preserve scenario/data-row IDs and source status. |
| Observable assertions | Every important Then names an assertable value, relation, state, event or error with an independent expected-value source. |
| Controlled setup | Given supplies data, permissions, time, state, dependency outcomes and isolation; nondeterminism/unknowns are visible. |
| Behavior focus | One main When, or a justified sequence, tests a contract rather than copying private algorithm steps. |
| Boundaries/failures | Meaningful edge values and specified failure/recovery are covered; speculative cases are not invented requirements. |
| Evidence level | The selected boundary can prove the behavior; a mock is not real integration evidence. |
| Handoff | Stable IDs, concrete data, expected outcomes and unresolved inputs survive into implementation; future locations/results are not invented. |
| Cost/conventions | Fixtures are proportionate; conventions are explicitly target-selected without imposing a runner/package. |

Missing requirement authority or selected specialist guidance limits the affected
judgment. This package has no technology extension. Keep required specialist
acceptance unresolved instead of presenting common-method coverage as a pass.
Valid alternative wording or test levels may prove the same acceptance.

For each finding give artifact location, criterion/source, evidence, triggering
condition, impact, severity rationale, uncertainty and a bounded correction.
Distinguish defects, questions and optional improvements. Suggested scenarios
cite their source or remain provisional. Return subject, sources, findings,
criterion/AC coverage, exclusions and missing inputs. No findings means none
supported within inspected coverage, not compliance.

Choose and justify the classification:

- `self-check` when the reviewer authored or repaired the artifact.
- `review; independence not established` when authorship or required evidence
  is unknown.
- `independent-review` only with evidenced distinct author, fixed subject,
  read-only reviewer and applicable target independence requirements.

Different prompts/models and a hash alone do not prove independence. This
package mandates no review packet. Preserve separate target acceptance and
state actual inspections and limits.

This operation reviews scenario artifacts. Executable-test review must follow
actual step/helper calls, check that the real action runs and assertions inspect
every designed outcome. GWT comments, names, compilation and a green run alone
cannot establish fidelity. Do not claim such code review or execution from
scenario text.

Return optional handoffs for requirement decisions, architecture, formal-spec
authoring or bounded test implementation with source, exact question/correction
and existing permission. Other skills are not required to finish this review.
A handoff grants no new authority, creates no test results and rewrites no
source requirement.
