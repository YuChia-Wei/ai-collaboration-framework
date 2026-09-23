# CBF snapshot contract proposal

This is the D351-01/D351-02 recommendation; not runtime availability.
The [schema draft](cbf-record-v1.schema.json) describes structural shape.
The [example](cbf-example.json) is fictional, proposed intent with no target
implementation, authority approval or execution evidence.

## Ownership and exact version

| Duty | Sole accountable implementation owner |
| --- | --- |
| Semantic producer | problem-frame-author instruction operation draft; consumes caller-selected intent/observations and marks uncertainty |
| Machine producer | problem-frame-author scripts/problem_frame.py:create; materializes supplied content without inventing approval, sources, IDs, time or pass results |
| Reader | Same script read_record used by inspect, validate, render and create read-back |
| Structural validator | Same package schema plus validate_structure for duplicate IDs, typed local references and exact versions; create calls this same implementation |
| Version authority | problem-frame-author maintainer; exact family + exact string schema_version + package-declared schema pair |
| Migration authority | Same maintainer; first release has no migration input or converter; preserve unknown/legacy bytes |
| Meaning/target compliance | spec-compliance-validator consumes the owner's actual structural result when required; target owns intent, implementation, runtime and gate authority |

No consumer copies the schema/parser or privately broadens version acceptance.
The structure result is evidence about selected bytes, not a requirement approval.
The compliance package may be used independently with an explicit external
format/reader; for this machine family, absence of its owner reader leaves the
structural stage unavailable. It never silently substitutes text inspection.

Record version `1.0.0` is an exact JSON string. Unknown family/version or
wrong types fail before the rest of the record is interpreted. Package version
`0.1.0`, metadata integer `3`, config integer `2` and record string
`1.0.0` are distinct. No version ranges, nearest-version coercion or permissive
additional fields. A required or semantic field change requires a new record
version and selected reader/writer/migration dispositions; historical v1
semantics stay unchanged.

## Minimal record

All object shapes are closed; every listed field is required. Empty arrays are
allowed only where stated in the schema. Strings are nonblank; exact IDs use
ASCII letters/digits/hyphens/underscores and are case-sensitive. The first reader caps raw record/request input at 4 MiB, decoded nesting at 32,
each array at 1024 entries, each text field at 16384 characters and IDs at 96
characters (snapshot id has its own exact pattern). Over-limit input is
invalid-input, not truncated. These are format/tool limits requiring an explicit
version decision to change, not claims that all targets fit. The tool rejects
JSON duplicate keys, nonfinite numbers, invalid Unicode and unsupported numeric
coercions before schema checks. It rejects BOM rather than guessing encoding.

| Root field | Meaning |
| --- | --- |
| family / schema_version | problem-frame.cbf / 1.0.0 |
| id | cbf- followed by 32 lowercase hex digits; caller supplies a fresh snapshot identity |
| frame_key / title | Caller-owned logical use-case label and display title; frame_key need not be globally unique |
| derived_from | null or a source ID in sources identifying the exact predecessor snapshot or legacy input; a link, not conversion or global supersession |
| sources | Nonempty list of source bindings |
| statements | Nonempty list of individually identified claims |
| scenarios | Nonempty list of GWT scenarios with individually identified observable assertions |
| open_questions | Zero or more identified unresolved questions, optional related claim IDs |

A source binding is `{id, kind, reference, revision, locator, sha256,
authority, authority_reference}`. kind is requirement, specification, decision,
code, test, legacy-frame or other. reference is an inert caller-supplied
repository/project-relative path or URI; it is never fetched or executed.
revision, sha256 and authority_reference are explicitly nullable when unknown.
locator is a supplied section/ID/symbol, not inferred line truth.
authority is normative, proposed, observation or unknown. A normative label
requires a non-null authority_reference structurally; it remains a caller claim
whose real provenance must be checked semantically. Code/test observation alone
does not establish intended behavior. URI credentials/tokens must not be stored.

A statement is `{id, category, text, basis, source_ids}`. Categories:
actor, command, controlled-domain, input, behavior, precondition, postcondition,
invariant, outcome, error, event, constraint, concern, external-boundary, fact.
Typed category carries meaning, while text stays language-neutral. Signatures,
event attributes, field types and retry/timeout decisions are separate statements
when independently testable; text is not parsed as executable expressions.

basis is stated, observed, inferred or unresolved. stated/observed/inferred
must cite at least one source; an inferred statement can cite observed code
without becoming normative. unresolved may have no source and must be linked
from at least one open question. The structural validator checks these relations,
not whether the text is true. At least one actor, command and controlled-domain
statement is required. Other categories are selected from actual scope; absence
is visible to the semantic review, not filled with invented defaults.

A scenario has `{id, title, source_ids, given, when, then, tests_anchor}`.
given/when are nonempty arrays of prose, not runnable steps. then is a nonempty
array of `{id, text, basis, source_ids, statement_ids}`; each assertion links at
least one statement. tests_anchor is an array of `{reference, locator}`, empty
when no test is known. Anchors are discovery hints, never execution proof.
The scenario's given/when are provisional scenario context traced by source_ids;
semantic review must check their authority, feasibility and alignment.

An open question has `{id, text, related_ids}`; an empty related_ids array permits
a missing requirement not yet represented by a claim. Statement, scenario,
assertion and question IDs are unique across their combined namespace. Source
IDs occupy a separate namespace. source_ids resolve only sources;
statement_ids only statements; related_ids only statements/scenarios/assertions.
No glob, recursive include, embedded code or external JSON Schema reference is
allowed. These checks belong to the same package's structural validator.

## Source and criteria binding

The raw SHA-256 of the exact record is the snapshot subject. inspect returns
that digest, exact family/version and criterion pointers (statement IDs and
each scenario/then ID). It does not drop inferred or unresolved claims from the
inventory. Source reference, revision, locator and bytes, when supplied, bind
what the author actually used. Unavailable originals remain explicit; a hash
alone neither authenticates an author nor approves intent.

The compliance reviewer expands independently observable conjuncts, input fields,
event attributes and scenario conditions into a complete criterion list with
stable `statement-id/component-label` or `assertion-id/component-label`
references where needed. No favorable denominator is selected by keyword count.
Each selected criterion is mapped to authority and evidence; exclusions require
target-owned rationale. A record edit changes the subject even if id is reused
manually; prior structural or compliance results must not follow it automatically.

## State and safe creation

There is no persisted draft/approved/compliant state machine. Every saved record
is a proposed snapshot whose semantic status is assessed outside the format.
Package writers provide only `absent -> complete new snapshot`. Existing path
or identity collision blocks creation; there is no overwrite/revise/finalize
operation. A semantic revision uses a new id and destination, with a preserved
predecessor source binding and derived_from. This is new authoring, not automated
migration, and does not retire the predecessor.

The writer validates the entire supplied payload, schema/config identities and
explicit destination before touching the store. Stage canonical bytes in an
exclusive temporary file in the selected destination directory, flush the file,
then publish through a no-clobber single-file primitive (for example a hard link
to the staged file) and read back exact bytes. Never use replacing rename or
open/truncate on the public destination. If safe publication is unavailable,
report unavailable before creating a final record. Probe only the selected
directory, not drives; no fallback filesystem.

A collision is conflict even if the existing bytes match. A crash may leave a
complete final file and/or an identified temporary file; no directory-wide
cleanup or automatic overwrite recovery is allowed. Return changed/mutation
state as none, published, or uncertain plus known contained residue. If final
publication happened but read-back/cleanup fails, return an error with published
or uncertain state, never a false unchanged success. Callers inspect the exact
destination before retrying with a new identity. No transaction journal or
power-loss/multi-file atomicity claim is made. P7 must observe Windows/Linux
publication and failure behavior before support is claimed.

## Paths, configuration and external templates

All tool requests supply absolute project_root and package_root. Require the
selected executable, metadata and schema to belong to that package. No ambient
cwd/upward discovery, source-checkout fallback, global index or common runtime.

Metadata 3 cannot use configuration:null with an owned schema. Use the existing
non-null P3 shape, namespace problem-frame-author, default store
`specs/problem-frames` (filesystem, tracked intent), default template
`templates/cbf.md`. Configuration files are optional, selected explicitly;
their absence creates no config file. Record operations also require an explicit
store-relative `reference`; create requires the exact basename
`<id>.cbf.json`. Nothing forces .dev. Destination ancestors must already exist
for the first release; no directory provisioning, implicit layout or global temp
change is needed.

Use config_version exact integer 2. Project roots config_version/skills/constraints;
local config_version/skills only. Validate the closed envelope and only the
selected namespace deeply. Foreign namespace objects remain inert. Precedence:
invocation > local > project > package defaults. Merge store leaves; replace
template object. Same-version selected config pair; no conversion. Adopt the
existing write_roots and locked_fields semantics described by the pinned
ADR configuration evidence: overrides cannot broaden project/default authority;
caller roots only narrow. Missing/invalid explicit config, path escape, lock
conflict or unproven ignored/untracked selected local Git config blocks the
affected operation. Do not create a shared parser for this new package.

Resolve project-relative paths against project_root. Reject drive-relative,
device/UNC, traversal, volume-root store, symlink/junction/reparse paths and
case/segment aliases; require contained regular files and supported local
filesystem. Store cannot overlap package, configs or selected template.
External absolute stores need explicit project write roots and actual task
authority. Read source reference strings inertly; tools do not follow them.
Recheck selected input/config/schema/template digests and path identities before
publish. Do not expose unrelated configuration or source content in diagnostics.

External authoring templates are caller-selected prose references, not executable
format adapters. Preserve requested external sections/meaning; report omissions
or conflicts against v1 separately. A caller requesting a different closed
format gets prose/external-format drafting, not a v1 label or silently dropped
fields. A missing selected template is unavailable; never fall back silently.
Packaged cbf.md is a render-only template bound to the record/view roles. A
project custom render template uses the same small literal placeholders
`{{id}}`, `{{title}}`, `{{body}}`, requires body exactly once, rejects unknown
placeholders and executes no expressions. Body includes all claims, sources,
assertions and questions with escaped Markdown. render returns text only;
authorized export is a separate caller write, never a second transactional file.

## Legacy and unknown input matrix

| Input | Inspect structurally | Write | Semantic reading / transition |
| --- | --- | --- | --- |
| Selected CBF 1.0.0 | Real owner reader/validator required | New snapshot only | Explicit criteria/authority review |
| Unknown CBF version or unknown family | unsupported-version / unsupported-family; no best-effort parsed record | Refuse | May inspect original bytes as unverified source if requested |
| Legacy unversioned CBF YAML | unsupported-format, report observed filename/digest only | Refuse | Caller explicitly selects the five files; no auto-discovery/import |
| Legacy SWF YAML | unsupported-format; SWF pending separate contract | Refuse | Caller selects frame/machine/use-case/workpiece/requirements files; preserve AC/entity semantics |
| External prose/template | No claimed v1 structural check | Instruction authoring to authorized destination only | Preserve caller format and annotate outside a closed format |
| Malformed/duplicate-key JSON | invalid-input | Refuse | Preserve original; do not repair while validating |

For historical re-authoring, enumerate every supplied legacy file with exact
digest, explain each retained/changed/omitted field, allocate a new snapshot id
and obtain a new target intent decision where meaning changes. This is a bounded
manual draft with a loss/uncertainty report, not a supported conversion edge.
Active legacy workflows and their readers remain with their original owners.

## Legacy field extraction map for the implementer

This maps meaning for authoring instructions, not an executable migration.

| Selected legacy input | New draft destination / preservation |
| --- | --- |
| frame.yaml frame_type, domain, use_case, summary | Explicit new family selection, frame_key and title; original family/domain in source locator; no inferred version |
| frame.yaml commanded_behavior actor/command/desired_outcome and controlled_domain.aggregate_spec | actor/command/outcome/controlled-domain statements, each with original file/field source binding |
| frame.yaml frame_concerns FC1-FC6, problem_world_facts | concern/fact statements only when applicable; preserve original IDs or bind them through exact source locators |
| machine/machine.yaml command_processing.steps, error_handling, constraint_enforcement | behavior/error/constraint statements; split independently observable claims rather than hide them in one text block |
| machine/use-case.yaml input, execution, preconditions, postconditions, output | input/command/precondition/postcondition/outcome/error statements; keep types/requiredness and individual fields explicit in text |
| controlled-domain/aggregate.yaml contracts, shared/local invariants, behavior.signature, domain_events.attributes, semantic_tags | pre/post/invariant/behavior/event statements with individual attribute checks; applicable semantics become explicit target constraints, not imported C# implementation rules |
| acceptance.yaml scenarios, given/when/then, traces_to and tests_anchor | Scenario/assertion IDs, source_ids, statement_ids and inert test anchors; every then gets its own identity |
| SWF workpiece/aggregate.yaml and requirements/*.yaml AC/entity contracts | Preserve selected original bytes and references; machine conversion/writer unsupported; semantic report retains every supplied AC and entity contract |

Legacy PRE1/POST1 may recur in different files. Use distinct new claim IDs such
as USECASE_PRE1 and AGGREGATE_PRE1 and bind each to its original file/ID; do not
silently merge equal-looking IDs or rewrite historical documents. Omitted
legacy fields require an explicit loss/uncertainty note. The mapping does not
prove round-trip fidelity or permission to convert.
