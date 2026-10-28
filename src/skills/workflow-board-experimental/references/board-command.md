# Board V2 command bridge

`workflow-records/board-command/1` supplies `board-command-prepare`,
`board-command-accept` and `board-command-reconcile` through
`python -I -B <package>/tools/board-command.py --activate --request <file-or->`.
It validates data and prepares explicit host actions. It does not dispatch,
retry, persist a journal/binding, find credentials, change identity or fall back.
The caller must already have authority for the selected domain write. This
single-carrier primitive does not choose the project's daily record authority
or implement SQLite-to-Board synchronization.

## Native schema and runtime prerequisites

Python 3.11+ and `jsonschema >=4.26,<5` (with its dependencies) are explicitly
required for these command operations only. Nothing is installed automatically.
The existing query bridge remains standard-library-only. The command CLI loads
only its declared local command/query modules and schema, without a Board
checkout, ambient provider-package import or network schema retrieval.

`schemas/board-collaboration-v2.schema.json` is the complete native schema from
`YuChia-Wei/ai-collaboration-workflow-board`, commit
`b100c9f9bd09b2a1c125c8b511f06defeb29c556`, source path
`src/Contracts/CollaborationV2/schema.json`. The observed source-checkout bytes
have SHA256 `93fc02c563ee6e05951afa4329a2d48d9f7ffa9a013cb24df1ac0c9364a91023`.
Only CRLF line endings were normalized to repository-owned LF; the packaged
115582 bytes have SHA256
`f9c40d058019a408097ddbf3fd414f5d638fc7a0678853cd2a0d75df55c5c1a4`.
The runtime verifies that packaged hash before using Draft 2020-12 validation
with format checking for the `command`, `capabilities`, `receipt`,
`operation_result` and `error` selectors. Schema presence does not advertise
unsupported commands. External schema resolution is disabled.

## Prepare and host dispatch

All envelopes require `contract_version`, `operation` and the same exact
nonsecret `binding` used by the [query profile](board-query.md): `adapter_id`,
`binding_id`, positive `binding_revision`, complete `project_ref`. Unknown
envelope/binding fields fail. Native profile is fixed to
`workflow-board/collaboration/2`, schema `2.0`.

Prepare additionally requires `capabilities` (the actual native object obtained
from the selected connection) and `command` (the complete original native
command). Its complete WorkflowRef must match the binding. The command must be
advertised by those capabilities, as must the recovery `operation.get` query.
The 18 selected workflow commands are:

- `workflow.create`, `workflow.start`, `workflow.pause`, `workflow.resume`,
  `workflow.cancel`, `workflow.complete`
- `plan.revise`, `document.append`
- `task.claim`, `task.progress`, `task.release`, `task.block`, `task.unblock`,
  `task.complete`, `task.cancel`
- `decision.open`, `handoff.record`, `checkpoint.append`

`decision.resolve` and project administration are excluded, even if advertised
by the service. Client actor/owner injection and unknown nested fields are
rejected by the frozen native schema. Workflow creation requires expected
revision zero; other commands require a positive original expected revision.

The strict UTF-8 JSON reader refuses duplicate keys, invalid Unicode, negative
zero, decimal/exponent/nonfinite number syntax and integers outside the native
safe range. In-process calls also reject floating-point objects. Booleans do not
become revisions. Exact canonical command UTF-8 bytes are bounded by the native
300000-byte limit; document content is bounded by 256000 exact UTF-8 bytes.
Native schema character/count constraints are also applied. Aggregate task,
record/header size, lifecycle, authorization and fencing checks still belong to
Board because preparation has no current aggregate state.

Successful prepare response has `result` with exactly:
`contract_version`, `binding`, `capabilities`, `command`, `tool_name`,
`local_command_fingerprint`, `recovery_query`. It preserves the command and
operation ID without normalization, clipping or expected-revision replacement.
`tool_name` is `v2_` plus the command name with dots replaced by underscores.
`recovery_query` is the native `operation.get` query for the same complete
WorkflowRef and operation ID. The local fingerprint is SHA-256 of compact,
UTF-8, sorted-key JSON of the complete command, without a trailing newline.
It is **not** Board's authority-bound `request_digest`.

The host must persist the entire prepared object before dispatch, then pass
`prepareResponse.result.command` directly to the selected mapped tool as code.
Preserve the connection, project, operation ID, expected revision, payload and
identity after an interruption. A bridge binding is a caller assertion, not a
signature or authentication proof.

```javascript
const prepareRequest = {
  contract_version: "workflow-records/board-command/1",
  operation: "board-command-prepare",
  binding: selectedBinding,
  capabilities: actualNativeCapabilities,
  command: {
    service_contract_version: "workflow-board/collaboration/2",
    schema_version: "2.0",
    workflow_ref: {...selectedBinding.project_ref,
      record_kind: "collaboration", workflow_id: "synthetic-command-check"},
    operation_id: "create-synthetic-command-check",
    expected_revision: 0,
    command: "workflow.create",
    payload: {
      title: "Synthetic command bridge check", goal: "Verify selected host bridge",
      scope: {included: "Synthetic records", excluded: "Production changes"},
      skill: {id: "slice-implementer", version: null}, external_work_refs: []
    }
  }
};
// Serialize prepareRequest to prepare.json, then invoke the CLI.
const prepared = prepareResponse.result;
await persistPrepared(prepared); // host-owned durable storage, before dispatch
const mcpResult = await selectedCommandTool(prepared.command);
const acceptRequest = {
  contract_version: "workflow-records/board-command/1",
  operation: "board-command-accept",
  binding: prepared.binding, prepared, mcp_result: mcpResult
};
// Serialize acceptRequest to accept.json, then invoke the same CLI.
```

## Accept and distinguish original-command outcome

Accept requires `prepared` and `mcp_result`, the actual CallToolResult from the
exact dispatched command. Null explicitly means the response was lost. Both
binding and all derived preparation fields are revalidated. MCP normalization
requires a content array, native object structuredContent or one strict JSON
text block, agreeing parsed representations if both are supplied, and boolean
isError. The selected host may add exactly `structuredContent.error_code:
"INVALID_ARGUMENT"` on `isError: true` results while omitting it from the text
JSON. Only this exact top-level annotation is normalized, and only when the
remaining structured object agrees with the parsed native text object. Other
annotations, values, locations or contradictory native data are refused. The
original supplied transport object is not modified. The native receipt is
validated in full, including actor/digest shape,
scope/operation identity, original expected revision, accepted before+1 and
workflow/document effects. Rejected receipts preserve failure details.

Every response separates `bridge_effect: none` from `command_outcome`:

| Situation | status | command_outcome |
| --- | --- | --- |
| Prepared without dispatch | ok | not_dispatched |
| Valid direct accepted receipt | ok | applied |
| Valid direct durable rejected receipt | ok | rejected |
| Lost, malformed, mismatched, native fault or output overflow after dispatch | error, or ok for explicit loss | unknown |
| Unconfirmed lookup observation | ok | unknown |

A direct accepted/rejected result returns the unchanged receipt as
`result.native_result`, correlation `direct_host_request_response`, and
`result.prior_confirmation: {local_command_fingerprint, request_digest}`.
Retain this confirmation with the same prepared command. Native digest is
**not recomputed locally**: Board includes trusted owner_id and actor, and the
host does not expose independently verified owner_id. Direct correlation relies
on the host sending the exact command and Board checking payload conflicts.

An `isError: true` flag may accompany a native durable `accepted: false` receipt.
The accept operation still validates and correlates that receipt in full and
returns `command_outcome: rejected`. An accepted receipt under `isError: true`
is contradictory and remains unknown. True native faults remain errors with
unknown command outcome and preserved fault data, never durable rejected
receipts. Authentication
and permission errors do not authorize another identity. Bounded errors omit
input bodies, host paths and tracebacks.

## Reconcile the original operation

Reconcile requires the same `prepared`. Without `lookup_result`, or with null,
it returns `result.recovery: {tool_name: "v2_operation_get", query}` for the
original operation, with unknown command outcome. It never sends that query.
The host may submit its actual CallToolResult as `lookup_result` in another
reconcile request. Exact scope/operation, receipt family, versions, revisions
and digest shape are checked again. Unknown results remain unknown.

A known lookup result without a previous confirmation is **observed only**:
`result.observed_outcome` retains accepted/rejected, `command_outcome` stays
unknown, `requires_original_replay: true`, and `result.replay` contains the exact
original command and tool. The host must explicitly replay that same command
and pass its direct response to accept before claiming final acceptance. Board
checks request digest before CAS, so an operation ID collision with a different
payload cannot be adopted by replaying it as this command.

Accept/reconcile optionally take `prior_confirmation`, exactly the pair emitted
by a prior direct accept of this same prepared fingerprint. Both fingerprint
and receipt digest must match before a lookup can establish applied/rejected.
A bare digest, confirmation for another payload, fabricated evidence or a
changed original command is not a valid substitute. The pair is host-supplied
evidence, not a cryptographic signature.

## Bounds and completion limits

Input is at most 2 MiB. All operations accept optional `max_output_bytes`,
2048–2097152, default 65536, for the whole serialized response. Nothing is
clipped. A preparation overflow is not dispatched; after possible dispatch an
overflow remains unknown, so retain the original prepared object and reconcile.
CLI exits 0 for status ok (including durable rejection or unknown observations)
and 1 for error/unavailable. A missing dependency/schema/runtime never means an
already dispatched command failed.

This bridge does not prove hosted behavior, downstream installation, persistent
command acceptance, aggregate acceptance, journal recovery, fanout, migration,
historical event equivalence or publication. Those require their selected host,
storage, domain and integration evidence.

This bridge belongs to `workflow-board-experimental`. Installation is not activation;
select `--activate` for each invocation. No bridge performs network dispatch.
