# Record shapes and invariants

These Draft 2020-12 schemas originated in the preserved design checkpoint and are
selected for the three package-owned source implementations. Package schemas own
runtime loading; these design copies document the shapes and synthetic examples.
No schema validator or product tool has run against them in this source task.

- [Lesson v2](schemas/lesson-record-v2.schema.json)
- [ADR v1](schemas/adr-record.schema.json)
- [Promotion v1](schemas/promotion-record.schema.json)

All objects are closed except explicitly named extension/config-snapshot objects.
The tool validates their owned config structure before capturing it. JSON parsing
must additionally reject duplicate keys, nonfinite numbers and invalid Unicode;
JSON Schema does not replace those rules. Integers require exact integer runtime
types, excluding booleans/floats. All semantic text is nonblank, not merely length
one. Timestamp format checks and chronological checks are required at execution.
Refs are restricted to same-document #/$defs entries; never fetch resources.

## Common controlled fields

Records have schema_version, kind, owner=project, id, status, revision, created_at,
updated_at, content, provenance, history, successor, and optional immutable
namespaced extensions. New records use revision=1, equal actual creation/update
times, history=[], successor=null. UUID4 IDs are lesson-/adr-/promotion- plus 32
lowercase hex digits; filenames must match IDs and the family suffix. No synthetic
example time or ID is used by an actual create.

A snapshot contains explicit path, exact UTF-8 text in utf8, sha256 over its raw
bytes, and actual observed_at. The bytes are evidence, never executable text.
Source format must be supported strict UTF-8; raw source bytes are not normalized
before hashing. Absolute paths are intentional retained project provenance, not
portable package locations. Exporting these records needs the project's privacy
review; diagnostic errors must not echo file contents or arbitrary paths.

Provenance records derive-from identity/store/schema plus exact snapshot. Preserve
it across updates. A successor similarly pins role/ID/schema/store and exact
snapshot. Re-read it during transition; validate same family/store and acyclic
links. Sources at later different bytes are stale references, not rewritten facts.

Every material update increments revision once and appends a history entry with
from_revision, operation, recorded_at, reason, previous_sha256, previous_status,
and previous_state. previous_state contains content, successor and the family's
other mutable facts (Lesson/ADR decision; promotion observation). Its typed shape
is that family state, not arbitrary data. Entries retain former content/evidence,
including removed assertions; no append-free rewrite or history compaction.
History revisions must be contiguous from 1 through current revision-1; times
cannot regress. previous_sha256 is the actual prior record byte digest, not a
claim that the original serialization can be reconstructed from the snapshot.
Extension/provenance changes are unsupported. Compare authored content, source/target digests and binding identity before refreshing snapshot times. An unchanged proposal retains its subject and snapshots. Equal content revision writes
nothing and creates no history entry. Enforce the 4 MiB whole-record bound before
publication; retention does not justify unbounded storage.

## Lesson v2

The v1 authored fields move together into content: title, observation, evidence,
conclusion, applies_when, does_not_apply_when, confidence, follow_up. This is an
explicit v2 format change, not reinterpretation of v1. Evidence remains ordered
{source,note} observations; references are inert, not automatically fetched.
Empty evidence requires tentative confidence; supported requires at least one
item and still is only an authored content claim. applies_when is nonempty.

Decision is null until accept, then contains mapped actor, accept, decided_at,
subject_sha256, option_id=null, exact evidence snapshot and binding snapshot.
Accepted records require such a decision; candidate cannot have one. Retired and
superseded records preserve whatever decision existed, and the history must show
the allowed transition. They never acquire an effective-rule field.

create request content is the authored object; optional extensions belongs to
creation only. revise cannot replace extensions. derive copies supported source
content/extensions into a new candidate and retains source raw bytes.

## ADR v1

Content: title, context, decision_drivers (nonempty), options (at least two),
consequences, evidence, applies_when (nonempty), does_not_apply_when. An option is
{id, summary, benefits, costs}; option IDs are nonblank and unique. A status-quo
alternative is a real option, not an empty second row. No compulsory Lesson link.

Decision is null in draft. decide reads actual owner evidence bound to the current
draft byte digest. An accept decision must select an existing option ID; reject
must select null. Decision evidence/actor/time/subject and captured project binding
remain part of the record. Decision time must be at or after draft creation and no later than actual observation; Lesson acceptance uses the same chronology. Evidence cannot be synthesized by the tool. The actual
decision rationale is retained in the transition reason and decision source;
consequences remain the alternatives' authored analysis, not observed execution.
Accept/reject record evidence does not prove implementation or rule adoption.

## Promotion v1

Record content contains title, target_id, baseline (snapshot), replacement (full
UTF-8 text), rationale, applicability, conflicts, sources, target_binding,
after_sha256, subject_sha256. A source contains kind, id, schema_version, reason
and an exact snapshot. These descriptor strings are attributed source metadata,
not foreign-schema validation. At least one source is required. Conflicts are
{subject, disposition, reason}, using preserve/replace/supersede/unresolved.

propose/revise request content instead supplies title, target_id,
expected_target_sha256, replacement, rationale, applicability, conflicts and
sources of {path, expected_sha256, kind, id, schema_version, reason}. The tool
captures baseline/source snapshots and accepted target binding; computes
SHA256(UTF8(replacement)) and the subject digest. It rejects caller-supplied
snapshots, digests computed on their behalf, observations or permission fields.
The source descriptors must match identity fields when present in a JSON source;
unsupported/non-JSON source descriptors remain explicitly caller-attributed.
No schema or semantic validation of a foreign owner is inferred from that match.

The subject hash input is {target_binding, source_snapshots, content}. Here
source_snapshots is the exact sources array; content is ONLY title, target_id,
baseline, replacement, rationale, applicability and conflicts. Exclude computed
digests and duplicate stored sources/binding. Hash P2 sorted-key/indent-2 UTF-8
JSON plus LF. Observation and record lifecycle never change that subject;
a permitted unadopted revision changes the subject and needs a new decision.
Once adoption was observed, conflict correction requires a NEW proposal identity
and new matching adoption; revision of the adopted identity remains blocked.
Only proposed/unadopted proposals can revise. A material proposal revision clears the current observation to null while retaining it in history. Same target and unchanged captured
baseline/config are required; drift requires a new proposal. A prior observed
adoption stays visible through history and prevents revision even after revocation.

Observation is null until reconcile. It records observed_at; adoption
(adopted/rejected/revoked/unresolved); rule_content
(matches-proposal/drifted/missing/unresolved); effect
(effective/inactive/unresolved); authority_basis=project-owned-local-evidence;
nullable adoption/rule/effect snapshots; and diagnostics of {code,message}.
There is no caller-set approved boolean. Unresolved conflicts prevent effective conclusions; a matching actual adoption remains independently visible with an unresolved-conflicts diagnostic. Unresolved adoption/effect does not hide other known dimensions. The schema reserves
rule_content=unresolved; this filesystem implementation fails unsafe/unreadable
target input rather than publishing an invented completed observation.

Inactive is reported only when a matching effect declaration says inactive;
effective additionally requires matched actual adoption and target bytes. A
missing/invalid effect declaration is unresolved. Require current captured target
binding to equal the accepted config before reconcile; otherwise conflict. Inspect
reports historical observations without making them fresh. A new reconcile on
unchanged evidence is still a real observation with its actual time.

## Synthetic examples

examples.json is wrapped with example_status=synthetic-design-only and explicitly
says execution_evidence=false. It includes initial candidate/draft/proposed records
and a config v2 example. Any example snapshot/hash describes only included
invented text. No acceptance, owner adoption, effective rule or tool execution is
claimed. No files named inside example paths were created.
