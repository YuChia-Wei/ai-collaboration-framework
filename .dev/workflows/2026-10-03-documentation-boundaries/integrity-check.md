# Integrity capture from the initial local cleanup

This is the initial pre-commit capture; later review is recorded separately.

```json
{
  "source_commit": "b52c68d64373bb54688109b9174bd4a9cea2b577",
  "identity_semantics": "Raw Git blob comparison distinguishes existing checkout line endings; git diff confirms canonical content unchanged. No pre-edit raw byte snapshot was recorded.",
  "protected": {
    "installed": {
      "files": 142,
      "raw_equal": 142,
      "line_ending_only": 0,
      "unexpected_changes": []
    },
    "excluded_history": {
      "files": 2248,
      "raw_equal": 2051,
      "line_ending_only": 197,
      "unexpected_changes": []
    }
  },
  "git_canonical_content_unchanged": true,
  "changed_markdown": {
    "files": 26,
    "missing": [],
    "source_external": []
  }
}
```
