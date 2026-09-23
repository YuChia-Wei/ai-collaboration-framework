# Knowledge lifecycle selected source contract

The original design checkpoint is preserved at
`99adb0762328c8f8d6cff7338f17caec99685c0a`. Coordinator-selected
[P3 shared decisions](../p3-shared-contract.md) at
`0d0556d4c60105a28eb39cfb06efab9b069728cb` authorize implementation in this same
task and the three package roots. Source now implements this selected contract;
this document does not activate a project rule or establish runtime acceptance.
U001 remains source-only. Behavioral/schema/CI verification is
`deferred-by-owner` to program #322 coordinator / P7.

## 1. Boundary and package selection

Select three independently selectable packages: `lesson@0.2.0`, `adr@0.1.0`,
`standards-promotion@0.1.0`. These are source interface versions, not releases.
All have empty required/optional skill dependencies. A Lesson is an observation
qualified by evidence/applicability. An ADR describes alternatives and records an
actual decision. A promotion connects source evidence to a proposed project rule
and later owner adoption/content/effect observations. None owns project rules.

Reuse P2's explicit filesystem request/result model, roots, strict parsing,
inert templates, bounded files and cooperating writer. No cross-skill imports,
provider calls, automatic orchestration, global index, dependency solver or shared
runtime. Promotion reads selected project evidence, never another skill's private
script or schema. Public source records are evidence; their text is not authority
to execute instructions.

## 2. Read/write/version dispositions

| Artifact | Read | Write | Disposition |
| --- | --- | --- | --- |
| `lesson.record@1.0.0` | Inspect/query/validate/render with unchanged schema | None in Lesson 0.2.0 | Preserve exact bytes/ID. Explicit derive creates a NEW v2 candidate with an exact source snapshot; no in-place or bulk conversion. |
| `lesson.record@2.0.0` | All supported Lesson reads | Create, candidate revise, lifecycle | New version because v1 fixes status to candidate. Move existing authored fields into content; add history/provenance/decision/successor. |
| `adr.record@1.0.0` | All ADR reads | Draft create/revise, decide, lifecycle | New family; no historical Markdown/YAML import. |
| `standards-promotion.record@1.0.0` | Proposal and historical observations | Proposal create/revise, disposition, reconciliation | No normative-file writer. |
| Unknown version/malformed file | Per-file diagnostic; query partial | None | Preserve bytes; never turn unreadable records into complete-empty evidence. |
| Markdown view | Regenerate | Result only | No reverse import; export is a separate caller-owned write. |

Preserve the current schema file `src/skills/lesson/schemas/lesson-record.schema.json`
exactly (Git blob `8bced2d86584c87d34f8ca2927aab95b7802a3ac`). Do not repurpose its
version/name. Mixed Lesson stores are supported. v1 remains candidate on disk;
results add `compatibility=read-only-legacy`, not a hidden lifecycle sidecar.
Old P2 correctly rejects v2. Selecting a new tool does not control an external
editor or an old tool deliberately editing legacy files.

`derive` reads one supported same-family source in the selected store, requires
actual expected digest and the ordinary related-query decision, copies authored
content/extensions into a new identity and snapshots the source's exact UTF-8
bytes. State resets to candidate/draft; no decision is inherited. This is reuse,
not schema migration or preserved identity. P6 may separately define migration.

## 3. Invocation and operations

Keep the P2 CLI shape `python <absolute-package>/scripts/<owner>.py --request
<absolute-json|->`. Common request fields remain `operation`, `project_root`,
`package_root`, optional explicit `project_config`, `local_config`, own settings
`overrides`, caller `write_roots`. This description does not authorize a trial.

Retain P2 outcomes and `mutation_state=none|committed|unknown`. `succeeded` on a
read-back operation means an observation was recorded, not that adoption/effect
succeeded. Failure outcomes are `invalid-input`, `unsupported`, `unavailable`,
`blocked`, `conflict`, `failed`; a dispatcher may report `not-executed`.
All writes need real task authority, independently of request fields. Updates
require a reference plus raw-byte `expected_sha256`; lifecycle reasons are
nonblank. Tools generate identity, timestamps, history and observations. Content
is the complete owned content object, never a general patch.

| Public operation | Owner / additional request input | Result and write boundary |
| --- | --- | --- |
| explain | All | Own settings/sources, locks, config version, authority bindings and ignored namespace names; no store creation. |
| inspect / validate | All; reference | Supported record/digest or structural/owned semantic diagnostics; never approves or authenticates content. |
| query | All; optional literal text, optional statuses | Direct store children, stable ordering, partial diagnostics and actual query digest. |
| render | All; reference | Inert configured template -> result-only Markdown with lifecycle/evidence limits. |
| create | Lesson/ADR; content, text, optional statuses, P2-shaped decision | Rerun identical query under lock; require real digest/partial acknowledgment; initial state only. |
| revise | All; reference/digest, content, reason | Allowed editable state only; retain prior content in history; equal content is a byte/time-preserving no-op. |
| derive | Lesson/ADR; reference/digest, reason, query inputs/decision | New candidate/draft; preserve original; exact source snapshot. |
| accept | Lesson; reference/digest/reason, decision_source | Record candidate acceptance only after mapped owner evidence read-back. |
| decide | ADR; reference/digest/reason, decision_source | Record accept/reject decision and selected option from mapped actual evidence. |
| retire | Lesson/ADR; reference/digest/reason | Archive applicable record; preserve content/evidence. |
| supersede | All; reference/digest/reason, successor reference/digest | Update only predecessor; pin and snapshot successor; no multi-file transaction. |
| propose | Promotion; content, text, optional statuses, decision | Capture source/target bytes and persist one complete replacement proposal. |
| withdraw | Promotion; reference/digest/reason | Withdraw proposal only; no rule rollback. |
| reconcile | Promotion; reference/digest, optional adoption_source, effect_source | Independently read decision, actual target bytes and effect declaration; append historical observation. |

Each `decision_source`, `adoption_source`, `effect_source` is a selection of
`binding_id`, `path`, `expected_sha256`. For promotion, binding_id equals the
proposal's target ID and the request field selects that binding's adapter.
Files must be within project-configured evidence read roots. Paths are neither
executables nor write destinations. A matching flag or caller's file selection
alone is not a decision predicate. Missing adapters produce blocked decisions
or unresolved promotion observations; they do not prevent saved-record reads.

Query version 2 hashes P2's sorted-key/indent-2/LF JSON encoding of query_version,
normalized store_root, exact text, normalized sorted statuses (or all), supported
schema identities and filename-sorted complete inventory with raw digests/errors.
Include nonmatches/unsupported files. P2 query digests cannot be reused. Default
query includes all statuses. Search fields: Lesson title/observation/conclusion;
ADR title/context/decision_drivers/options; promotion title/rationale/replacement.
Read limits/partial semantics remain P2's. De-duplication remains caller judgment.

## 4. Lifecycle and authority

| Family / from | Operation -> to | Required evidence and meaning |
| --- | --- | --- |
| Lesson / absent | create or derive -> candidate | Authorized store write plus actual related-query decision; no approval/rule claim. |
| Lesson / candidate | revise -> candidate | Expected bytes + edit authority; old content/evidence preserved in history. |
| Lesson / candidate | accept -> accepted | Configured allowed owner decision binds current raw record digest and accept; observation acceptance only. |
| Lesson / candidate, accepted | retire -> retired | Authorized reason; no evidence deletion or rule change. |
| Lesson / candidate, accepted | supersede -> superseded | Accepted same-family successor, exact digest and authorized reason. |
| ADR / absent | create or derive -> draft | Authorized write + related query; decision remains null. |
| ADR / draft | revise -> draft | Expected bytes + edit authority; previous alternatives/evidence retained. |
| ADR / draft | decide -> accepted or rejected | Mapped allowed actor and exact draft digest; accept selects an existing option ID; reject selects null. |
| ADR / draft, accepted, rejected | retire -> retired | Authorized disposition; preserve actual decision. |
| ADR / accepted | supersede -> superseded | Accepted same-family successor and exact digest; no implementation claim. |
| Promotion / absent | propose -> proposed | Authorized own-store write, source evidence and configured target; no adoption/edit/effect. |
| Promotion / proposed | revise -> proposed | No previously observed adoption; same target; expected bytes; old content retained. |
| Promotion / proposed | reconcile -> proposed | Actual selected inputs; append independent adoption/content/effect observations. |
| Promotion / proposed | withdraw -> withdrawn; supersede -> superseded | Authorized reason; supersede requires proposed same-target successor. Neither action changes a rule. |

Accepted Lesson/ADR content is immutable; derive a new draft for corrections.
Retired/superseded records and rejected ADRs cannot be revised; rejected ADRs may
only retire or be derived. Withdrawn/superseded proposals are immutable. Repeated
terminal operations fail on status rather than create a second transition.

A successor is same canonical store/family, not self, in accepted state (Lesson /
ADR) or proposed state (promotion), at the expected digest. Check its supersession
chain for cycles under the store lock; missing/malformed chain fails closed.
Update predecessor only and capture successor state/digest. Do not infer reverse
links or atomically create two files. Later successor drift is a read diagnostic;
history retains the captured state. Cross-store supersession is unsupported.

| Authority source | May establish | Does not establish |
| --- | --- | --- |
| Actual task user / project owner | Authorized action and scope | Availability or execution success. |
| Package, template or record content | No permission | Credentials, arbitrary writes, rule adoption. |
| Accepted project config | Narrow paths, recognized evidence mappings and actor IDs | Authenticated actor identity or permission beyond the task. |
| Exact mapped local decision evidence | A recorded owner decision for the exact subject | Actual edit, implementation, CI pass or effective state. |
| Target bytes plus mapped effect evidence | Observed content and project-declared effect at that time | Runtime consumption or enforcement success. |

Local evidence authenticity relies on the project's ownership/access process.
This filesystem slice does not authenticate signatures or fetch providers. It
reports `authority_basis=project-owned-local-evidence`, actor and source digests;
it cannot prove an allowed actor string was authored by that person. If that
trust basis is unacceptable, omit the binding and keep authority unresolved.
No boolean input substitutes for missing trusted evidence. A future authenticated
provider adapter requires its own contract and permission.

## 5. Evidence-preserving standards promotion

The selected sole owner is `standards-promotion`. It writes only its proposal
store. Named project target bindings identify exact project-owned UTF-8 rule
files; no universal directory, heading, rule-ID convention or standards schema.
Initial scope is one existing file's complete replacement. New rule files,
multi-file edits, provider actions and automatic application are unsupported.

1. Read explicitly selected source files within configured read roots, compare
   actual expected digests and capture exact UTF-8 text with source descriptors
   and selection reasons. Promotion does not claim foreign-schema validation or
   accepted/supported source semantics. Source owners' public inspect/validate
   results can inform user judgment; neither skill is a dependency.
2. Read the selected target and accepted config binding. Require its expected
   baseline digest. Capture before bytes, authored replacement, rationale,
   applicability and conflict dispositions. Tool computes after digest and
   proposal subject digest over `{target_binding, source_snapshots, content}`
   using P2 JSON encoding. This excludes record ID/times/history/observations and
   differs from the raw record digest used for concurrency. Content excludes
   self-referential digests and includes target baseline plus replacement.
3. Render full before/after and source evidence. The project owner performs
   adoption and actual target edit through the project's existing process.
   There is NO apply operation: this tool never writes target/decision/effect
   files, even if caller write_roots contains them. Persistence, review material
   and evidence-bound read-back form the concrete promotion mechanism.
4. Reconcile adoption by reading the configured JSON source and mapping exact
   subject digest, target ID, replacement digest, allowed actor, decision and
   decision time. Match every binding. Return adopted/rejected/revoked/unresolved
   independently. A generated approval file/flag is not an observation.
5. Independently read actual target bytes: matches-proposal/drifted/missing/
   unresolved. Separately read effect JSON: it must bind proposal subject,
   target ID, replacement digest, raw adoption-source digest, configured
   applicability and active/inactive state. Only adopted + matching actual bytes
   + matched active declaration yields effect=effective. This means observed
   project-declared effect, never verified implementation or enforcement.
6. Persist the three dispositions and input snapshots as a historical observation.
   Inspect labels observations historical. Only fresh reconcile reports current
   evidence. Missing/malformed inputs stay unresolved with diagnostics; config or
   identity drift before publication is conflict. Never reuse an old effective
   result after drift. Superseding a proposal does not supersede the actual rule.

Conflicts are authored entries `{subject, disposition, reason}` where disposition
is preserve/replace/supersede/unresolved. A proposal may retain unresolved conflicts
for review. Matching actual adoption is still reported independently, but effect stays unresolved until a NEW proposal
identity explicitly resolves them and receives new matching owner adoption. Existing
rules are not scanned globally or assumed conflict-free. Scope of review remains
visible. Proposal revision after any observed adoption is blocked; create a new
proposal instead. Retain source evidence even when its live file later changes.

Recheck captured config/evidence/target identities before one-record publication.
This is not a cross-file transaction or protection against external writers
ignoring coordination. Capture actual observation times; require decision time
not in the future and effect time >= adoption time, <= observation time. Snapshot
size/history growth stays within the whole-record limit; exceed -> unsupported
before writing, never trim evidence silently. Missing evidence yields a missing snapshot plus a diagnostic. Malformed JSON or
mapped evidence retains exact UTF-8 bytes and unresolved diagnostics. Unsafe,
unreadable, oversized, non-UTF-8 or changed-digest inputs fail without a new
observation; never invent bytes/digests to claim a completed read.

## 6. Project config coexistence

Select config_version 2 for the second actual consumer. v1 explicitly supports
only Lesson; do not silently reinterpret its closed namespace semantics. v2 has
required exact integer config_version, optional skills and (project only)
constraints. Namespace keys follow the package ID grammar; values must be JSON
objects. Validate full JSON syntax/envelope then ONLY the selected namespace.
Foreign objects are ignored/preserved, never treated as permissions or loaded via
private skill schemas. Unknown selected-namespace fields fail. Explain reports
ignored namespace names, not their values or validity. Local constraints remain
forbidden in every namespace. Duplicate keys/nonfinite values/bool versions fail.

Keep invocation > local > project > defaults, store-leaf merge, atomic template,
project locks and caller narrowing. Never union permissions across namespaces.
Defaults: notes/lessons, notes/adrs, notes/promotions. Parent provisioning remains
P2-bounded. No upward search, config edit, implicit converter or disk fallback.
No selected config means package defaults with no decision/promotion authority.
Lesson 0.2.0 can read v1 with unchanged closed semantics; ADR/promotion require v2
for selected config files. Selected project/local versions must match. An owner
may explicitly author a v2 copy/edit preserving v1 namespace content; no migration
is performed by package installation or invocation.

Project-only constraints extend write_roots/locked_fields as follows:

| Namespace | Additional fields |
| --- | --- |
| lesson, adr | decision_sources: array of `{id, root, allowed_actors, pointers}`. Missing -> accept/decide blocked. |
| standards-promotion | source_read_roots: nonempty path array when proposing; targets: array of named target bindings. Missing -> propose blocked; no effect adapter -> unresolved. |

Decision pointers map subject_sha256, actor, decision, decided_at, plus ADR
option_id to JSON Pointers. Decisions are Lesson accept; ADR accept/reject.
Reject missing/root pointers, invalid escapes, duplicate pointer targets and
wrong-type selected values (ADR reject option_id must be null). Resolve JSON
objects/arrays deterministically, no wildcard, remote fetch or expressions.

Promotion target shape is `{id, path, applicability, allowed_actors,
adoption_source, effect_source}`; each source is `{root, pointers}` or null for
an explicitly unavailable adapter. Targets are project-contained existing files;
no external normative target. Adoption pointers map subject_sha256, target_id,
after_sha256, actor, decision, decided_at; decisions adopt/reject/revoke. Effect
pointers map subject_sha256, target_id, after_sha256, adoption_sha256,
applicability, state, effective_at; states active/inactive. Applicability is a
nonempty configured string matched exactly. Source files are selected per request
with actual digest; absent selections produce unresolved observations.

Reject duplicate binding IDs, canonical path aliases and overlap with installed
packages, config, templates or this owner's writable record store. Evidence roots and target
bindings are never local/invocation overrides. Configured read scope is not write
authority. Existing path/reparse/caller restrictions continue to apply.

## 7. Templates, storage and actual P2 reuse

Retain literal {{token}} grammar, one substitution pass, escaped text, no execution
or includes. Required Lesson tokens retain all authored fields and add status,
history, provenance for v2. ADR requires all authored fields plus id/schema_version/
status/decision/history/provenance. Promotion requires the proposal token (complete before/after, rationale, conflicts, binding and source snapshots),
observation/history/status/id/schema_version. Custom templates change presentation
only. v1 reads accept the old token set; v2 template lifecycle fields render an
explicit legacy explanation for v1 without changing data. v2 reads reject a
custom v1 template missing required lifecycle tokens.

Retain P2 4 MiB file/request/serialized-record and 10,000 direct-file bounds,
strict UTF-8/JSON/YAML, safe paths, frozen binding, local filesystem allowlist,
exact comparison, owner-specific exclusive store lock, atomic single-record
publication and truthful cleanup/mutation_state. Suffixes: .lesson.json,
.adr.json, .promotion.json. Lock names: .lesson-write.lock, .adr-write.lock,
.standards-promotion-write.lock. No stale-lock deletion, implicit recovery,
network filesystem support, cache, generic journal or power-loss guarantee.

| Inspected P2 source | Selected reuse/change |
| --- | --- |
| lesson.py parse_json/parse_yaml/safe_path/read_bytes/exact_equal | Reuse semantics and bounded code locally; no other skill imports Lesson. |
| config/settings/Binding | P2 was Lesson-only with one schema/template. Owner-local implementations of v2 envelope/own settings and evidence adapters. |
| load_package | Exact lesson@0.1.0, one resource family. Replace with explicit supported package/schema identities, not heuristic compatibility. |
| Writer/write_operation/query | Reuse single-record publication and strict failures; add owner lifecycle/history and query v2. |
| distribution.package.load_package | Named packages already supported, but schemas keyed only by ID and artifact role has one closed schema field. Shared distribution metadata-v2 implementation belongs to #337. |
| distribution.data | Similar strict primitives, but distribution-specific errors, blob inputs/path semantics; do not import build-time modules into installed skills. |
| distribution manifest/selection/projection | Exact members remain coordinator-owned; no glob or undeclared helper. |

Bounded duplication is preferable here to extracting the entire 950-line Lesson
script into a shared runtime. Pure primitive parity becomes focused P7 work;
project authority text is never copied as policy. No new helper/member field.
Extraction needs demonstrated stable consumers and an explicit distribution
contract; this source slice introduces neither. New schemas are package-owned and
self-contained; only local #/$defs references may resolve, never remote/file refs.
The P2 no-reference guard must be narrowed deliberately for these new schemas.

## 8. Selected implementation and return

C334-01 through C334-04 are selected by the shared contract: config v2 isolation,
metadata v2 with explicit readable/writable schemas, independent standards-promotion
and exclusive package ownership. The shared loader/manifest/profile implementation
belongs to #337/coordinator, not these installed packages. See
[interface inventory](interface-proposal.yaml) for 9/8/9 exact members and 11/11/10
operations. The original design commit remains unchanged historical evidence.

This executor returns a coherent local source commit before first push. Bounded
implementation/workflow completion is separate from Issue/Project closure, provider
integration, release and runtime acceptance. The coordinator owns those later states.
P7 selects actual checks for mixed-version preservation/derive, namespace isolation,
local schema resolution, histories/decisions/successor cycles, template compatibility,
path/lock/cleanup failures and adoption/content/effect drift. No synthetic example,
AST parse, local inventory inspection or Git checkpoint satisfies those behaviors.
