# Lesson Filesystem Operations, Version 0.1.0 Design

All operations are planned. `lesson.fs` has no executable entrypoint here; these are interfaces for P2, not available commands. Runtime requirements are in `skill-package.yaml`. Strict parsing must explicitly reject duplicate keys, non-JSON YAML types, tags and aliases; permissive library defaults are insufficient.

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

1. Resolve runtime/config/authorization, freeze the store/template and validate authored content before material writes.
2. For create/revise exclusively create `<store>/.lesson-write.lock` with a unique invocation token. Existing lock is conflict; never guess it stale or delete another writer's lock. Reads need no lock.
3. Under lock recheck containment/target identity. Revise compares current raw bytes to expected digest. A create ID collision fails without overwrite.
4. Serialize validated UTF-8 JSON with one trailing newline to a unique same-directory temporary file. Publish new records with an exclusive non-overwriting operation; revise by atomic same-directory replacement. Unsupported filesystem semantics fail explicitly, including unproven shared/network backends.
5. Readers see whole old/new records. Flush/close before publication. No power-loss durability claim, recovery journal or store migration is implied.
6. Clean up only this invocation's verified temp file and matching-token lock. Cleanup failure or uncertain publication is `failed`, with `mutation_state: none | committed | unknown`; reread before retry. Never infer rollback merely from failure.

One cooperating writer per store is supported. External editors ignoring the lock can race; expected digests do not solve arbitrary concurrent writers. A record operation is not a transaction over standards, Issues and workflows. A shared mutation service or general locking framework is unnecessary here.

## Template binding

Default `templates/lesson.md`; project override selects a UTF-8 file within project root. Templates are inert text: no execution, includes, expressions, path interpolation or recursive evaluation.

Tokens: `id`, `schema_version`, `status`, `title`, `observation`, `evidence`, `conclusion`, `applies_when`, `does_not_apply_when`, `confidence`, `follow_up`, written `{{token}}`. Require `id`, `schema_version` and all authored-content tokens except `extensions`; `status` is optional. Unknown/malformed/missing required tokens fail before rendering. Repetition is allowed. Substitute once so token-like input cannot trigger another lookup.

Arrays render in authored order as Markdown bullets; empty arrays as `None supplied`. Evidence is `source: note` escaped text, not executable instructions. Other values are Markdown-escaped plain text preserving line breaks. Do not interpret user HTML. Custom headings/order change presentation, not semantics or schema.

## Version dispositions

Read/write only `lesson.record@1.0.0`. Accept, supersede, retire, promote, delete, import, conversion and store migration are unsupported. Preserve unknown/historical bytes. Future owners select explicit convert/regenerate/re-execute/preserve behavior; no automatic compatibility/downgrade. P3-A owns lifecycle extension; P7 owns behavioral checks.
