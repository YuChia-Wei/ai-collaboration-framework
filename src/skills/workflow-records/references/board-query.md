# Board V2 query bridge

The additive profile `workflow-records/board-query/1` supports reads through an
explicitly selected host MCP connection. It does not send network requests,
discover credentials, save bindings or write domain records. The separate CLI
requires Python 3.11+ and the declared sibling `workflow_records/board_query.py`;
its runtime uses only the standard library and needs no repository checkout.

## Exact public envelopes

Both operations require `contract_version`, `operation` and `binding`. Unknown
envelope/binding/native-query fields fail. The binding has exactly `adapter_id`
(`workflow-board-v2`), stable transport `binding_id`, positive `binding_revision`
and `project_ref` (`store_id`, `namespace: personal`, `project_id`). It contains no
credential. The host owns authentication, connection selection and mapping the
symbolic tool name to the selected MCP tool. A binding is a caller assertion,
not cryptographic proof of the connection's identity.

`board-query-prepare` additionally requires `query`: the complete exact native
envelope (`service_contract_version: workflow-board/collaboration/2`,
`schema_version: 2.0`, `query`, `payload`). Only `context.page` additionally
requires positive `expected_snapshot_revision`; it stays outside the native
payload and is compared with the returned snapshot. All other queries omit it.
Native task/decision reads require `at_revision` and their definition/decision
revision; document reads require `document_id`, positive `revision`, and
`content_hash` in `document_ref`. Opaque cursors are passed unchanged.

```json
{
  "contract_version": "workflow-records/board-query/1",
  "operation": "board-query-prepare",
  "binding": {
    "adapter_id": "workflow-board-v2",
    "binding_id": "selected-work-records-connection",
    "binding_revision": 1,
    "project_ref": {
      "store_id": "workflow-records-private-collaboration",
      "namespace": "personal",
      "project_id": "ai-collaboration-framework"
    }
  },
  "query": {
    "service_contract_version": "workflow-board/collaboration/2",
    "schema_version": "2.0",
    "query": "project.read",
    "payload": {
      "project_ref": {
        "store_id": "workflow-records-private-collaboration",
        "namespace": "personal",
        "project_id": "ai-collaboration-framework"
      }
    }
  }
}
```

Run `python -I -B <package>/tools/board-query.py --request prepare.json`.
`--request -` reads UTF-8 JSON from stdin. No project-root argument is needed.
The successful response is `{contract_version, operation, status: "ok",
mutation_state: "none", result: prepared}`. `prepared` has exactly
`contract_version`, `binding`, `query`, `tool_name`, `expected_snapshot_revision`
(null for queries other than `context.page`). For the example, `tool_name` is
`v2_project_read`; `prepared.query` is the unchanged native query above.

The host passes `prepared.query` directly as the selected tool's arguments.
It must then construct, as code, the following accept envelope and pass the
actual returned MCP CallToolResult object without AI rewriting either hop:

```javascript
const prepared = prepareResponse.result;
const mcpResult = await selectedTool(prepared.query);
const acceptRequest = {
  contract_version: "workflow-records/board-query/1",
  operation: "board-query-accept",
  binding: prepared.binding,
  prepared,
  mcp_result: mcpResult
};
// Serialize acceptRequest directly to accept.json or the CLI's stdin.
```

Run `python -I -B <package>/tools/board-query.py --request accept.json`.
Acceptance revalidates the prepared query and exact binding, revision and tool
mapping. A successful response's `result` is the native data, with unknown
extensions, missing inputs, cursors and receipt outcomes preserved.
`mutation_state` is always `none`: a successful receipt lookup does not mean
this adapter applied a mutation. Prepared objects are not signatures or durable
execution records; callers must retain the exact prepared object and selected
connection, rather than replace both the binding and query after dispatch.

## Supported query and result boundaries

| Native query | Symbolic tool | Critical acceptance checks |
| --- | --- | --- |
| `project.list` | `v2_project_list` | Store/namespace of every project; page limit/cursor; project contract |
| `project.read` | `v2_project_read` | Complete ProjectRef, positive revision, workflow contract |
| `project.operation.get` | `v2_project_operation_get` | Project receipt target, operation ID, outcome and revisions |
| `capabilities` | `v2_capabilities` | Native versions and complete ProjectRef; native commands are data, not adapter write capabilities |
| `workflow.find` | `v2_workflow_find` | Complete project scope for every workflow, positive revisions and paging |
| `workflow.context` | `v2_workflow_context` | Exact WorkflowRef, native versions/revision, sections, missing inputs, plan reference |
| `context.page` | `v2_context_page` | Exact WorkflowRef, expected snapshot revision, section and paging |
| `task.read` | `v2_task_read` | Exact WorkflowRef, snapshot, task ID and definition revision |
| `decision.read` | `v2_decision_read` | Exact WorkflowRef, snapshot, decision ID and revision |
| `document.read` | `v2_document_read` | Exact WorkflowRef and document reference; SHA-256 of exact UTF-8 content |
| `operation.get` | `v2_operation_get` | Workflow receipt target, operation ID, native versions, outcome and revisions |

Project listing intentionally enumerates the selected store, including projects
other than the bound project. Other project results must match the binding.
`legacy-personal` may be discovered/read in the registry as V1; workflow reads
for that scope are refused. There is no implicit V1/local-provider fallback.
IDs follow native 1–160 ASCII syntax with reserved names rejected. Revisions
are safe integers; booleans are not integers. Project and workflow receipts stay
distinct. `accepted`, `rejected`, and `unknown` outcomes are returned unchanged;
unknown does not prove that a prior write failed or authorize a replacement.

MCP results require a `content` array. Use native object `structuredContent`,
or exactly one text block containing native JSON. If both are present, their
parsed JSON must agree. Mixed/ambiguous content, malformed JSON, invalid Unicode
and non-boolean `isError` fail. `isError: true` with a valid native fault returns
`status: error`, adapter code `remote_error`, and the unchanged fault under
`native_result`; it does not enter the successful result path.

Input JSON is limited to 2 MiB. Both operations accept optional
`max_output_bytes` (2048–2097152, default 65536) bounding the complete serialized
response. Larger documents require an explicit budget. Oversized results fail
with `limit_exceeded`; content is never clipped. File/stdin errors and malformed
inputs return bounded JSON without host paths or tracebacks. Exit status is 0
for `status: ok` (including rejected/unknown receipt lookup) and 1 otherwise.

These checks cover critical identities, revisions, hashes, outcome and paging
invariants, not every field of the full native JSON Schema. Unknown native data
is retained, not executed. Host authentication/authorization, hosted behavior,
cross-session persistence, full export/recovery, writes, claims, retry/fanout,
publication, installation and migration need their separately selected evidence.
