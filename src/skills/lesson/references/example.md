# Custom-path Lesson example (not executed)

This is an illustrative input sequence. No command below has been run as part of
this package delivery; no ID, timestamp, digest, successful persistence or
platform support is claimed. Replace the example roots with actual absolute
paths on the invoking host. The package has no dependency on the source checkout.

Assume the caller separately prepares a project at `C:/work/acme` and places the
entire declared package at `C:/packages/lesson`. Python and the declared library
versions must be installed by the caller; the tool never installs dependencies.

## Project configuration and custom template

The caller selects `C:/work/acme/.ai/custom/framework.json` explicitly:

```json
{
  "config_version": 1,
  "skills": {
    "lesson": {
      "store": {"root": "knowledge/lessons", "tracking": "tracked"},
      "template": {"origin": "project", "path": "team/templates/learning.md"}
    }
  },
  "constraints": {
    "lesson": {
      "write_roots": ["knowledge"],
      "locked_fields": ["store.tracking", "template"]
    }
  }
}
```

The explicit `knowledge` constraint permits provisioning `knowledge/lessons`.
All relative settings resolve against `C:/work/acme`, regardless of the config
directory or invoking cwd. There is no automatic `.ai/custom` discovery. The
config and template are project-owned files, not package members.

Place this inert text at `C:/work/acme/team/templates/learning.md`:

```markdown
# Team learning: {{title}}

Record {{id}} / schema {{schema_version}} / {{status}}

## What we observed
{{observation}}

## Evidence and confidence
{{evidence}}
Confidence: {{confidence}}

## Conclusion and limits
{{conclusion}}
Applies when:
{{applies_when}}
Does not apply when:
{{does_not_apply_when}}

## Follow-up candidates
{{follow_up}}
```

## Explain, then query

Save this illustrative request to an explicitly chosen absolute filename such as
`C:/work/lesson-request.json` and invoke the script as documented in
[operations](operations.md#invocation-and-result-protocol):

```json
{
  "operation": "explain",
  "project_root": "C:/work/acme",
  "package_root": "C:/packages/lesson",
  "project_config": ".ai/custom/framework.json"
}
```

Expected configuration interpretation (not observed execution): store
`C:/work/acme/knowledge/lessons`, project template under `team/templates`,
`store.root`, `store.tracking` and `template` sourced from project configuration,
and `store.kind` from package defaults. Explain creates nothing.

Use the same roots/config with `"operation": "query"` and
`"text": "output locations"`. A query over a missing store may be complete and
empty. An unreadable/unknown-version selected file must instead appear in partial
diagnostics. Review `matches`, `partial`, diagnostics and actual `query_sha256`.
Changing text or collection requires a new decision even when matches look equal.

## Decide to create or revise

If an existing record covers the observation, use its returned reference to
`inspect` and then `revise` with that response's raw-byte `sha256`. Otherwise,
the following create request shows all fields. The digest placeholder is
deliberately invalid; replace it with the actual query result:

```json
{
  "operation": "create",
  "project_root": "C:/work/acme",
  "package_root": "C:/packages/lesson",
  "project_config": ".ai/custom/framework.json",
  "text": "output locations",
  "decision": {
    "action": "new",
    "query_sha256": "REPLACE_WITH_ACTUAL_QUERY_SHA256",
    "acknowledge_partial": false,
    "reason": "The reviewed candidates do not cover this location-binding observation."
  },
  "content": {
    "title": "Bind output locations to an explicit project root",
    "observation": "Illustrative observation: changing cwd can change an unbound relative path.",
    "evidence": [],
    "conclusion": "Explicit project binding may prevent accidental destination changes.",
    "applies_when": ["The caller works with multiple project roots."],
    "does_not_apply_when": ["The operation intentionally targets an explicit absolute external store."],
    "confidence": "tentative",
    "follow_up": ["Gather evidence from an authorized real operation."],
    "extensions": {"acme.learning": {"audience": "maintainers"}}
  }
}
```

`acknowledge_partial: false` is appropriate only when the actual query is complete.
A partial query requires a conscious decision about the reported limitations and
true acknowledgment. Create still reruns it under lock; changed digest yields
conflict with a new `related_query`. Reassess that output, do not retry blindly.

Successful execution would return the actual generated reference/digest, which
must be read from the result rather than copied from a sample. Use the returned
reference for `inspect`, `validate` or `render` with the same store binding.
Render returns Markdown in `view.markdown`; it does not write a second file.

For revision, send the same common roots/config, `operation: revise`, the actual
`reference`, actual `expected_sha256` from inspect, and all eight authored fields
in `content`. Omit `extensions`: the existing extension map is preserved. Equal
authored content keeps the exact original bytes and update time. A stale digest
is conflict even when the requested content appears equal.

## Boundaries to preserve

- An invocation override `{"store":{"root":"knowledge/drafts"}}` is permitted
  by the project root bound and changes the collection; it moves no records.
- An override outside `knowledge`, a changed locked template/tracking setting,
  explicit null, partial template, unknown namespace or config version fails.
- Optional local config must be explicitly named and ignored/untracked in a Git
  project. It cannot supply constraints or expand project write authority.
- Read operations never require the write backend to be writable. A requested
  write on an unrecognized/shared backend is unsupported rather than redirected.
- `failed` with `mutation_state: committed` or `unknown` requires a fresh read
  and inspection of reported transient cleanup. Existing locks are preserved.
- Promotion, adoption, deletion, import and migration are not operations of this
  candidate-only version. Evidence strings are neither fetched nor executed.
