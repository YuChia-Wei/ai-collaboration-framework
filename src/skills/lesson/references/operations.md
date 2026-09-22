# Lesson Filesystem Operations, Version 0.1.0

`lesson.fs` is implemented at `scripts/lesson.py`. This describes the source
interface, not evidence of execution or platform acceptance. Runtime requirements
are in `skill-package.yaml`. The tool rejects duplicate keys, non-JSON YAML types,
explicit tags, anchors, aliases and merge keys. JSON rejects BOMs, invalid UTF-8,
unpaired surrogates and non-finite values, including overflow such as `1e999`.
Metadata version and config version require exact integer types; other versions
are explicit supported strings. Unknown keys fail at each owned object boundary.

## Invocation and result protocol

Run with Python >=3.11,<4 and declared PyYAML/jsonschema versions:

```text
python /absolute/package/scripts/lesson.py --request /absolute/request.json
python /absolute/package/scripts/lesson.py --request -
```

The second form reads one request from standard input. Request filenames must be
absolute. Neither form infers a project/package/config path from cwd. `--help`
only prints usage; it does not execute an operation or establish availability.
Requests/files/serialized records are limited to 4 MiB each. Query selects at most
10,000 direct record filenames; exceeding this bound is `unsupported`, never a
truncated complete result. Limits are fixed in this version.

Every request is an object with required `operation`, absolute `project_root` and
absolute `package_root`. The running script must belong to that package root.
Optional common fields are explicit `project_config`, `local_config`, `overrides`
(the Lesson settings object only), and caller `write_roots` (nonempty path array,
which additionally restricts project permission). There is no implicit config
search. Omitted optional fields inherit; explicit null is invalid.

| Operation | Additional request fields |
| --- | --- |
| `explain` | None |
| `query` | Optional `text` string; default empty |
| `create` | Required `content`, `text`, `decision` |
| `inspect`, `validate`, `render` | Required `reference` |
| `revise` | Required `reference`, `expected_sha256`, `content` |

`content` is the complete authored object below, not a partial patch. Create may
include `extensions`; revise cannot supply that key. `reference` is exactly
`{"role":"lesson.record","id":"lesson-<32 lowercase hex digits>"}`.

Standard output is one UTF-8 JSON object with `operation`, `outcome`, and
`mutation_state`. An unrecognized operation reports `operation: null` and
`unsupported`. A successful invocation exits 0; an unsuccessful operation exits
1. CLI usage errors return JSON too. Help is the ordinary argparse usage surface.
Diagnostics contain stable `code` and plain `message`; input payloads, exception
text and config values are not echoed in errors. `explain` deliberately returns
selected settings and normalized paths; do not put secrets in configuration.

| Operation | Success fields in addition to the common envelope |
| --- | --- |
| `explain` | `settings`, leaf `sources`, normalized `project_root`, `package_root`, `store_root`, `template_path`, `locked_fields`, `write_roots`, `caller_write_roots`, `runtime_capability: not-probed`, `tracking: intent-only`, `unsupported_reasons` |
| `query` | `store_root`, exact `text`, `matches` of `{reference,title,sha256}`, `partial`, per-file `diagnostics`, `query_sha256`, `selected_count` |
| `create` | `reference`, exact persisted-byte `sha256`, `store_root`, `changed: true`, `related_query`, `directories_created` |
| `revise` | `reference`, exact persisted-byte `sha256`, `store_root`, `changed`, `directories_created` |
| `inspect` | `reference`, `sha256`, `store_root`, `record` |
| `validate` | `reference`, `sha256`, `store_root`, `valid: true`, `diagnostics: []` |
| `render` | `reference`, `sha256`, `store_root`, `view: {role: lesson.view, source: reference, schema_version, markdown}` |

An invalid record returns an unsuccessful result with diagnostics, never
`valid: true`. Write results include `directories_created`, even on failure:
newly created empty directories are retained, not recursively rolled back.
Cleanup failure can override an otherwise committed result to `failed` while
retaining the reference/digest. Inspect those results before any retry.

### Related-record decision

First execute `query` with a meaningful literal `text` (or empty text to examine
all). Review matches and partial diagnostics. Choosing an existing candidate
means `inspect`, then `revise` with its raw-byte digest. Choosing a new candidate
means `create` with the same text/binding and this exact decision shape:

```json
{
  "action": "new",
  "query_sha256": "<actual query result, not an example digest>",
  "acknowledge_partial": false,
  "reason": "The observed cause and applicability differ from the listed candidates."
}
```

The placeholder above is not a valid hash. Use the actual returned 64 lowercase
hex characters. `reason` must be nonblank. `acknowledge_partial` must be a boolean;
set true only after a caller decision that acknowledges the listed limitations.
The tool itself always reruns the query under its exclusive writer lock. It
compares the resulting digest and refuses record publication on drift. A partial
query additionally requires explicit acknowledgment; false returns `blocked`.
The rerun is returned as `related_query` on success, query conflict or partial
rejection, so the next decision has concrete evidence. The caller's decision is
not a signed authorization receipt, dedup proof or content-uniqueness guarantee.

The query SHA-256 hashes sorted-key, indented UTF-8 JSON with one newline over:
`query_version: 1`, normalized absolute `store_root`, exact case-sensitive request
`text`, `record_schema: 1.0.0`, and filename-sorted `inventory`. Each entry has
`filename` and actual raw-byte `sha256` if readable, plus a diagnostic `error`
code if invalid. All selected records participate, including nonmatches and
malformed records. Unreadable/link/oversized entries bind filename/error only;
`partial: true` makes that limitation visible. Text search itself is
case-insensitive, but changing the exact text changes the decision digest.
Changing the store binding also changes it. No guessed digest or prior-query
flag can suppress the tool's actual query. Read-only queries are not atomic
snapshots against external editors; the under-lock rerun checks cooperating
writer changes. Unknown concurrent editors remain outside the supported model.

## Record and authoring boundary

One JSON file stores the complete Lesson. Schema: `schemas/lesson-record.schema.json` relative to package root. `schema_version`, `kind`, `owner`, `id`, `status`, `created_at` and `updated_at` are tool-controlled. Invocation supplies authored `title`, `observation`, `evidence`, `conclusion`, `applies_when`, `does_not_apply_when`, `confidence`, `follow_up` and optional `extensions`.

IDs are `lesson-` plus UUID4's 32 lowercase hexadecimal digits. Initial status is always `candidate`; owner is `project`. Times are actual timezone-aware ISO 8601 execution times, never template values. `created_at` stays fixed. `updated_at` changes only for a material revision and cannot precede `created_at`.

Evidence items contain `source` and `note`. Sources are opaque references, not instructions or automatically fetched paths/URLs. Empty evidence requires `tentative` confidence; `supported` needs at least one item. Supported remains a content claim, not proof of causality or approval. No adopted/active state exists yet.

Namespaced `extensions` preserve JSON values semantically. Initial revision cannot replace/remove extension data; creation may supply it. Unknown top-level fields or unsupported schema versions fail before mutation. Structural validation uses the supplied schema with date-time format checks enabled; the tool owns the additional semantics below.

## Operation contracts

| Operation | Inputs beyond frozen configuration | Behavior/output | Writes |
| --- | --- | --- | --- |
| `explain` | None | Effective values, field sources, constraints and path diagnostics; does not infer actual availability. | None |
| `create` | Complete authored content, optional extensions | Query related candidates first; caller chooses revise or new. Generate identity/times, validate, exclusively create, return real reference/digest. | New candidate only |
| `inspect` | `{role: lesson.record, id}` | Read direct filename, parse/validate, return record and SHA-256 of exact UTF-8 bytes. | None |
| `query` | Optional literal text | Case-insensitive substring over title/observation/conclusion; empty selects all. Sort by ID; return references/titles, per-file errors and `partial` flag. | None |
| `validate` | Reference | Check structure, filename/ID equality, versions, timestamp ordering, evidence/confidence. Never approves content. | None |
| `revise` | Reference, lowercase 64-hex expected SHA-256, complete replacement authored content excluding extensions | Candidate-only; reread under lock, reject changed digest, preserve identity/creation time/extensions, update content/time, validate then replace. Equal content is a byte/time-preserving no-op. | Existing candidate only |
| `render` | Reference and resolved template | Validate both; return Markdown with source ID/schema. Never imports view edits. | None; exporting requires caller-owned destination authority |

Actual outcomes: `succeeded`, `invalid-input`, `unsupported`, `unavailable`, `blocked`, `conflict`, `failed`. A dispatcher that never started the tool reports `not-executed`. Query reports `partial: true` when any selected file cannot be interpreted; its partial result cannot prove no similar Lesson exists. Pre-create query output or an explicit caller decision acknowledging query limits must be available; an input flag alone does not prove the query ran. Dedup is a judgment, not a unique-content constraint.

## Bounded write behavior

1. Resolve runtime/config/authorization, freeze the store/template and validate authored content before material writes. The selected record schema is frozen too; this version rejects schema reference edges instead of resolving arbitrary remote resources.
2. For create/revise exclusively create `<store>/.lesson-write.lock` with a unique invocation token. Existing lock is conflict; never guess it stale or delete another writer's lock. Reads need no lock.
3. Under lock recheck containment/target identity. Revise compares current raw bytes to expected digest. A create ID collision fails without overwrite.
4. Serialize validated UTF-8 JSON with one trailing newline to a unique same-directory temporary file. Flush with `fsync`, close, then create via exclusive hard-link publication (`os.link`) or revise via atomic same-directory `os.replace`. Unsupported filesystem semantics fail explicitly, including unproven shared/network backends. Windows writes initially require local fixed/RAM NTFS; Linux writes require a local ext2/ext3/ext4/xfs/btrfs/tmpfs/ramfs mount observed through `/proc/self/mountinfo`. Other platforms/backends return `unsupported` for writes. This allowlist is implementation scope, not tested platform certification. No storage probing creates trial files or chooses another disk.
5. Readers see whole old/new records. Flush/close before publication. No power-loss durability claim, recovery journal or store migration is implied.
6. Clean up only this invocation's verified temp file and matching-token lock. Cleanup failure or uncertain publication is `failed`, with `mutation_state: none | committed | unknown`; reread before retry. Never infer rollback merely from failure.

Existing lock files are never recovered automatically. Temp cleanup checks the
owned inode and, after a complete write, the exact bytes; lock cleanup also
requires the matching token. Partial lock writes remain for explicit recovery
and report cleanup failure. `mutation_state` describes record publication, not
transient lock/directory writes. A publication call with an uncertain error stays
`unknown`; complete write/readback is `committed`; conflict before publication or
an equal-content revision is `none`. Successful create removes its own extra
temporary hard link. External permission and current filesystem failures remain
real results, not inferred from metadata or `os.access`.

One cooperating writer per store is supported. External editors ignoring the lock can race; expected digests do not solve arbitrary concurrent writers. A record operation is not a transaction over standards, Issues and workflows. A shared mutation service or general locking framework is unnecessary here.

## Template binding

Default `templates/lesson.md`; project override selects a UTF-8 file within project root. Templates are inert text: no execution, includes, expressions, path interpolation or recursive evaluation.

Tokens: `id`, `schema_version`, `status`, `title`, `observation`, `evidence`, `conclusion`, `applies_when`, `does_not_apply_when`, `confidence`, `follow_up`, written `{{token}}`. Require `id`, `schema_version` and all authored-content tokens except `extensions`; `status` is optional. Unknown/malformed/missing required tokens fail before rendering. Repetition is allowed. Substitute once so token-like input cannot trigger another lookup.

Arrays render in authored order as Markdown bullets; empty arrays as `None supplied`. Evidence is `source: note` escaped text, not executable instructions. Other values are Markdown-escaped plain text preserving line breaks. Do not interpret user HTML. Custom headings/order change presentation, not semantics or schema.

## Version dispositions

Read/write only `lesson.record@1.0.0`. Accept, supersede, retire, promote, delete, import, conversion and store migration are unsupported. Preserve unknown/historical bytes. Future owners select explicit convert/regenerate/re-execute/preserve behavior; no automatic compatibility/downgrade. P3-A owns lifecycle extension; P7 owns behavioral checks.
