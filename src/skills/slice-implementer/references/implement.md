# Implement one bounded slice

## Selected installed knowledge for implement

For requested knowledge coverage, take the caller's explicit installed lock and
selection, `project_root`, capability `implementation`, operation `implement`,
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

## Intake and source layers

Record the following proportionally in conversation or the target's selected
artifact. No framework workflow/store/role record is mandatory:

- Intent: feature, bug-fix, behavior-correction, refactor, cleanup or selected
  review/validation remediation.
- One bounded goal, observable acceptance, explicit non-goals, authorized paths
  and behavior/contracts that must remain stable.
- Authorization source defining allowed work and checks.
- Normative sources: applicable requirements, specifications, target standards
  and accepted architecture/decisions defining correct behavior.
- Optional finding evidence and the reviewed revision, separately from those
  sources. A recommendation does not redefine requirements or grant permission.
- Exactly one execution mode and any applicable overlay.
- Selected technology guidance, actual target commands, working directory,
  prerequisites, environment and permitted validation outputs.

Do not invent a formal finding for an ordinary bug fix, refactor or cleanup.
Quote bounded conversational evidence when no durable finding exists. Preserve
unrelated edits and current target constraints. Missing authority or conflicting
normative sources stops the dependent action; do not copy defaults from the
framework's source repository or infer a technology from a filename.

## Select one mode

| Mode | Read | Purpose |
| --- | --- | --- |
| command | [Command](modes/command.md) | One state-changing application behavior. |
| query | [Query](modes/query.md) | One read behavior without domain-state mutation. |
| reactor | [Reactor](modes/reactor.md) | One event-driven reaction/projection/integration behavior. |
| generic | [Generic](modes/generic.md) | Other bounded behavior, refactor or concrete test implementation. |

Read only the selected mode. Apply [remediation](remediation.md) when selected
findings/failures are being repaired; it augments that mode. For concrete GWT
tests in any mode, use [test handoff](test-handoff.md). Complete supplied
scenarios do not require another design stage.

No role registry, extra installed skill, language, broker, ORM, test package or
DI model is a prerequisite for generic implementation. This package supplies
common methods; selected specialist rules must come from explicit target
sources. Missing required coverage is reported and blocks the affected judgment,
not erased by a common-method result.

## Implement and check

1. Inspect only the paths, contracts and immediate dependencies needed for the
   accepted goal. Trace acceptance to the relevant implementation boundary.
2. Check that responsibility, domain language, module/aggregate boundaries,
   dependency direction, compatibility, lifetimes and transactions are settled.
   An accepted design may introduce a public type or interface without repeating
   architecture approval. A new unresolved decision stops dependent edits.
3. Plan the smallest coherent change across that slice and implement it. Keep
   internal local edits under the slice owner; optional local collaboration is
   for a separable useful subtask, not every method or file.
4. Implement necessary regression protection within authority. Preserve supplied
   scenarios and assertion intent. Test design, concrete code and actual test
   execution remain separate results, even when all are already authorized.
5. Run the narrowest meaningful authorized target checks using actual supported
   commands. Do not invent a runner, acquire credentials or weaken a guard to
   make validation pass. Preserve failures, interruptions and missing evidence.
6. Inspect the resulting diff, acceptance coverage and touched radius. Record
   adjacent unrelated issues without silently broadening the slice.

An unavailable editor prevents implementation. Missing validation tools or
environment leaves checks blocked/not-run; keep the implementation result and
remaining acceptance distinct. Continue unaffected authorized work only when
the missing item is not its prerequisite. Zero discovered tests, successful
compilation or a synthetic example alone does not prove the required behavior.
Proposed commands and source instructions are not executed evidence.

## Ownership and output

One handler/use-case flow, adapter extraction, outbound port isolation,
single-module repository cleanup or targeted cross-file correction can form a
slice. File count alone does not determine scope. Several independent goals
need sequencing; a concrete missing architecture or compatibility decision
goes directly to its owner without inventing an entire new planning stage.

If the whole request is one technical target/operation and direct-call-site
radius, a local implementer is sufficient. Within this selected slice, retain
ownership and avoid bouncing accepted work between skills. A private helper
may remain local when it preserves responsibility, dependencies, lifetime,
transactions and behavior; public/semantic changes stay inside the accepted
slice design or require an actual missing decision.

Return intent, mode, overlays, source/authorization bindings, changed files,
bounded outcome and compatibility notes. Include actual check command/context,
results and remaining gaps; selected GWT and findings mappings belong in the
same compact result when useful. Persistence requires an authorized caller
destination, not a prescribed folder.

Optional handoffs identify the concrete missing decision or separable work,
source references, original permission and current evidence. Existing permission
travels unchanged; a handoff grants none. Return the semantic handoff if another
skill is unavailable. Do not rewrite the originating review or claim independent
review/compliance from implementation. Push, PR, merge, publication, adoption
and external tracker changes require their own applicable authority.
