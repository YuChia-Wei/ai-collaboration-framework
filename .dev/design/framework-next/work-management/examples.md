# Synthetic examples only

These are hypothetical inputs and narratives, not live records, execution receipts, authorization or schema-validation results. Placeholder digests/OIDs are deliberately invalid and must be replaced by actual observations.

## Local-only work

A project with an existing planning parent selects:

```json
{
  "config_version": 1,
  "skills": {
    "local-backlog": {"store": {"kind": "filesystem", "root": "planning/items", "tracking": "tracked"}},
    "pr": {"store": {"kind": "filesystem", "root": "planning/pull-requests", "tracking": "tracked"}}
  },
  "constraints": {
    "local-backlog": {"write_roots": ["planning/items"]},
    "pr": {"write_roots": ["planning/pull-requests"]}
  }
}
```

This uses the proposed WM-C1 envelope, not current P2 compatibility. An ignored collection changes tracking to ignored; the project establishes ignore rules separately. No source repository setting is changed.

Illustrative local create content:

```json
{
  "title": "Document timeout behavior",
  "summary": "Describe the response when the selected operation times out.",
  "acceptance": ["The documented timeout result matches the implementation."],
  "references": [{
    "kind": "github-issue",
    "target": "https://github.com/example/demo/issues/7",
    "relationship": "reference-only"
  }]
}
```

A real create returns its own UUID/digest. Draft -> planned -> in_progress -> completed requires actual authorized transitions, current digest/state and completion evidence. Issue 7 is a separate reference; its status is never imported or changed.

## PR without backlog/workflow/Lesson

The caller supplies actual full Git base/head OIDs to prepare, initially with no validation entries if the diff digest is not yet known. After reading the actual subject, it may revise with:

```json
{
  "id": "focused-example",
  "command": "project-selected focused check",
  "disposition": "deferred",
  "subject_head": "<actual selected head>",
  "subject_diff_sha256": "<actual computed diff digest>",
  "evidence": [],
  "reason": "Project owner schedules execution at its next verification checkpoint."
}
```

A selected provider_target could be github/github.com/example/demo with base_ref main and head_ref topic/timeout-docs. That target is not permission to publish. Render keeps deferred visible and returns real record/template/body hashes. A later authorized provider-create rechecks actual remote branches and matching PR absence; only actual execution/read-back can return a created PR identity. No successful checks, merge, Issue closure or Project update are implied.