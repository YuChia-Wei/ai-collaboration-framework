# Current-record file export and project schema selection

Use native `export-files` with `workflow-records/1`, or `group-export-files`
with `workflow-records/local-group/1`. Both export **one current record** to a
fresh caller-selected absolute local directory. Existing `export` and
`group-export` still produce complete recovery archives, with their existing
preflight, inactive restore and activation rules. File export does not migrate,
restore, activate, change authority or send pending commands.

## Requests

Native export requires an explicitly configured native SQLite provider (schemas
1/2/2.1/3), complete `workflow_ref`, `destination` and exact `expected_revision` from
context. Git/remote export is unavailable.

```json
{"contract_version":"workflow-records/1","operation":"export-files","workflow_ref":{"provider_id":"local","store_id":"project-workflows","workflow_id":"example"},"destination":"C:/Exports/example","expected_revision":"sha256:<observed-revision>"}
```

Group export requires configured `group_ref`, `destination` and all three
observed `expected_configuration_revision`, `expected_authority_epoch` and
`expected_revision` values. It reads the selected authority under the group lock.
Missing selected storage fails without fallback; an unreadable replica does not
prevent current-record export. Complete group recovery export still requires
every retained member.

```json
{"contract_version":"workflow-records/local-group/1","operation":"group-export-files","group_ref":{"group_id":"project","project_id":"project","workflow_id":"example"},"destination":"C:/Exports/example","expected_configuration_revision":0,"expected_authority_epoch":1,"expected_revision":"sha256:<observed-cut>"}
```

Neither export takes an operation ID or writes a store receipt. Existing
destinations fail instead of merging or replacing. Success returns `format`,
`scope: current-record`, exact source identity/revision, destination,
`manifest_digest`, file count and unsupported restore/Git-import status.

Native `preflight-files` takes `workflow_ref`, `directory`, `manifest_digest`
and optional `schema_selection`. Group `group-preflight-files` takes configured
`group_ref` and those same directory/digest/selection fields. Neither takes CAS
or an operation ID. Use the original CLI/root/config. Preflight validates the
directory independently of subsequent source progress; it does not prove the
source is still at that cut or authorize importing the exported record.

## Directory contract

Manifest format is `workflow-records/files/1`:

```text
<destination>/
  workflow.yaml
  tasks/<task_id>.yaml
  documents/<original-relative-name>
  attachments/<original-relative-name>
  .workflow-records/manifest.json
  .workflow-records/current-record.json
  .workflow-records/checkpoint.json     # when currently retained
```

`workflow.yaml` is the complete metadata mapping. Task YAML preserves entire
objects; manifest order preserves task order. Extension fields, including
project `schema_version`, retain their meanings. No export-version, entrypoint
or template defaults are inserted. Deterministic YAML must parse to the same
structured values. Original YAML comments/formatting cannot be recovered from
records originally accepted as structured objects.

Documents/attachments preserve exact bytes, including empty, CRLF and binary
content. Manifest maps retain logical names; physical paths add `documents/`
or `attachments/`. Logical `documents/notes.md` thus becomes physical
`documents/documents/notes.md`. Entrypoint remains its original logical name.
Consumers use these maps; export does not rewrite links or infer an old layout.

The current-record sidecar retains the exact structured native revision state,
including event/checkpoint wrapper, or the complete current group event body,
including providers, request and fixed targets. Source revision/cut is recomputed
with its original canonicalization. This current cut omits retained history,
delivery reconciliation and control state; it is not a restorable authority.

Preflight checks explicit identity, observed manifest digest, hashes/sizes,
source revision/cut, blob closure, YAML/current-record equality, selected resource
identity and a rebuilt complete export plan. Missing/extra/altered files and
unused extra directories fail. Rehashed YAML disagreeing with raw state fails.
The manifest digest comes from the caller's observed export; internally
consistent replacement data does not authenticate itself or prove ownership.

## Project-owned schemas and templates

Without selection, export uses `current-record` profile version `1`. Explicit
project validation uses this optional field on export and preflight:

```json
{"schema_selection":{"path":".ai/project/workflow-records/selection.json","sha256":"sha256:<observed-selection-digest>"}}
```

The strict JSON selection contains `contract_version:
workflow-records/file-schema-selection/1`, `profile_id`, `profile_version`,
`schemas: {workflow,task}` and optional `templates: {workflow,task}`. Each schema
or template reference is exactly `{path,sha256}`, with a safe project-relative
path and observed raw-byte hash. Template keys are individually optional.
`.ai/project` is permitted; managed `.ai/core`, `.agents`, `.claude` and `.codex`
resources are rejected. There is no implicit selection discovery or resource
write, dependency installation, download, code execution or missing-file fallback.

Selected validation needs jsonschema 4.26–4.x. Schemas use Draft 2020-12 and only
document-local `#` references. Each selected template is a YAML mapping validated
against its corresponding selected schema. Templates supply validation and
identity only: no expressions, rendering, data transformation or default insertion.

Explicitly copy the supplied defaults byte-for-byte to the chosen project's
`.ai/project/workflow-records/` directory:

| Package member | Project filename |
| --- | --- |
| `schemas/file-workflow-v1.schema.json` | `workflow.schema.json` |
| `schemas/file-task-v1.schema.json` | `task.schema.json` |
| `templates/file-workflow.yaml` | `workflow-template.yaml` |
| `templates/file-task.yaml` | `task-template.yaml` |
| `templates/file-schema-selection.json` | `selection.json` |

The supplied selection contains exact default resource hashes and these project
paths. Compute the copied selection digest for requests. After deliberate project
customization, update resource hashes/profile version and request digest. Upgrade
does not discover/overwrite project copies. Custom-profile preflight requires the
same explicit selection and matching resources; it never silently trusts a profile
embedded in an export or falls back after resources change.

Old 0.6/0.9 values remain opaque metadata or selected project schema identities.
Naming a version supplies no historical parser/migration/restore adapter. Such an
adapter requires authentic selected samples and separate authority. GitStore's
schema/lifecycle 1.0 reader has additional mandatory fields; export does not
invent them or establish Git-import compatibility.

## Safety, bounds and failures

Export captures one SQLite transaction or selected group lock. Source records,
provider configuration, receipts and synchronization state remain unchanged.
Paths reject traversal, drive/UNC/ADS escapes, reserved names, case-aliased
components, file/directory prefix collisions and links/reparse components.
Destination cannot overlap live native storage or group control/member paths.
Preflight rejects hard-linked members. Hostile simultaneous direct filesystem
mutation remains outside the cooperating-writer model.

All paths/data/schemas are planned before reserving the fresh directory with
`mkdir`. Payload files are written exclusively and flushed; manifest is written
last as completion marker. A partial directory cannot pass preflight. Ordinary
failure removes only invocation-created files/directories, never another writer's
files. Process termination may leave an incomplete directory requiring explicit
inspection/cleanup before retry. This is not an atomic filesystem snapshot or
physical power-loss guarantee. After ambiguous output failure, inspect and
preflight using the observed manifest digest; no export receipt exists.

Bounds refuse without truncation: 400 payload/manifest paths, 32 MiB per member,
64 MiB total payload, 1 MiB manifest. Existing source collection limits apply.
No extension data, history or files are silently removed to fit limits.
