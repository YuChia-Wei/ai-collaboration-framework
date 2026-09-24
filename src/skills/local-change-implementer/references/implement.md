# Implement one local change

## Selected installed knowledge for implement

For requested knowledge coverage, take the caller's explicit installed lock and
selection, `project_root`, capability `local-change`, operation `implement`,
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

## Confirm the semantic radius

Identify one primary class/object/method/local symbol/query, one operation,
expected behavior and its source, permitted files/module, direct dependencies,
direct call sites and immediate tests. Authorization and target requirements
serve different purposes: permission to edit does not define correct behavior.
Preserve unrelated work and the target's accepted architecture.

Suitable operations include extracting a method, renaming a local symbol,
fixing bounded logic, simplifying an object interaction or adjusting a local
SQL/ORM implementation. A behavioral fix needs its intended behavior stated;
otherwise preserve behavior. Do not combine independent goals.

Several direct call-site files do not force a slice. A private implementation
helper type can remain local only if it preserves accepted target, radius,
behavior, responsibility, dependency direction, lifetime and transaction
boundary. A new type's existence or line count alone decides nothing.

A public/domain type, interface or responsibility/dependency/lifetime/transaction
change belongs to a bounded slice under an accepted design. Missing or changed
architecture, compatibility, module/aggregate or business-language decisions
need their owner's decision before dependent edits. Public DTO/API/event or
ubiquitous-language renames are not local symbol renames. Broad namespace
restructuring, cross-module behavior and multi-aggregate cleanup exceed this
local method. Return a concrete handoff rather than executing beyond scope.

When the target, operation or radius is unknown, resolve that bounded question
first. An unexplained runtime failure may need diagnosis before choosing a
repair; a diagnostic finding does not grant implementation authority.

## Execute the smallest coherent edit

1. Inspect the target, direct uses and relevant tests. Use applicable
   target-owned rules and only explicitly selected technology guidance. This
   package provides no ambient language, ORM, DI or test framework baseline.
2. State what changes and what behavior/contracts must remain stable. Identify
   hidden side effects, lifetime, transaction or data-semantics risks before
   treating a seemingly small edit as local.
3. Apply the single operation and required direct call-site changes. Prefer an
   applicable IDE refactoring if available and permitted; review its actual
   edits. Do not treat a tool's success as proof the radius stayed bounded.
4. Update immediate tests when needed to protect the changed contract and
   within authority. Avoid unrelated cleanup or implementation-mirroring tests.
5. Run the narrowest meaningful authorized target checks. Obtain the actual
   command, working directory, prerequisites and allowed output scope from
   target evidence. No default product command or package is supplied here.
6. Inspect the diff and actual touched radius. Stop dependent edits if an
   unaccepted semantic/architecture decision or wider operation emerges.

An unavailable editor blocks implementation. Missing selected specialist rules
block the corresponding decision. Missing test tools, environment or command
authority means those checks are blocked or not run; it is not permission to
invent a command, broaden credentials or call the implementation verified.
Continue other authorized work only if the missing item is not its prerequisite.
Existing permission remains valid; do not ask again just because an optional
handoff is used.

## Return the result

Report target/operation, expected behavior source, actual files/direct call
sites/tests touched and why they fit the radius. State compatibility and any
prevented expansion or unresolved decision. For each relevant check include
actual command/context and result, or precise not-run/blocked/deferred reason.
Preserve failures beside later results. A proposed regression, compilation or
zero discovered tests is not proof of changed-behavior coverage.

Keep output in the conversation or a caller-selected authorized destination.
No workflow, rule packet, record store or other installed skill is required
by this method. Optional review or slice/architecture collaboration receives
scope, sources, current evidence and existing permission. A local implementation
result is not independent review or specification compliance, and it grants no
push, PR, merge, publication or target decision authority.
