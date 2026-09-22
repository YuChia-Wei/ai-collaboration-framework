# Issue #330 source delivery

Implementation is present for the standalone candidate-only Lesson package.
Runtime behavior, platform compatibility, installation and CI are
**deferred-by-owner** under U001 to program #322 coordinator / P7. No product CLI,
including help, has been executed. No independent audit or passing behavioral
acceptance is claimed.

Owning Issue: [#330](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/330).
Owning task: `LESSON-001`. This report adapts
`.ai/assets/skills/ai-context-governance/templates/ai-context-remediation-report-template.md`
under U001. Starting HEAD:
`a1d8b750b8c81fd17697a39e04b55c35c4f3c4dc`.
Report template version: `2.0.1`; status: final source-delivery report.
Created/updated: `2026-09-23T01:58:20+08:00`.

## Delivered content and public boundary

`src/skills/lesson/` is self-contained: the original six P1 members retain their
roles, the executable is `scripts/lesson.py`, and `references/example.md` is a
declared reference. Metadata v1 uses existing fields only. There are no private
helpers, source-repository imports, copied metadata schemas, extra dependencies,
shared configuration changes or generated runtime entries.

Exact package-relative member list (eight):

```text
SKILL.md
skill-package.yaml
references/configuration.md
references/operations.md
references/example.md
schemas/lesson-record.schema.json
templates/lesson.md
scripts/lesson.py
```

Public executable interface is one JSON request:
`python <absolute-package>/scripts/lesson.py --request <absolute-file|->`.
Python internals are private, not an import API. Operations are `explain`,
`query`, `create`, `inspect`, `validate`, `revise`, `render`. Required common
inputs are `operation`, absolute `project_root`, absolute `package_root`;
optional inputs are explicitly selected `project_config`, `local_config`,
settings `overrides` and caller `write_roots`. Exact operation-specific fields,
output envelope and error dispositions are in `references/operations.md`.

Configuration is JSON only, project/default constraints precede local/invocation
overrides, locks are enforced after each override layer, and caller roots only
narrow permission. Metadata uses JSON-compatible YAML with strict duplicates,
types, tags/aliases/anchors/merge rejection. Record parsing preserves extension
values and rejects unknown versions/fields. JSON Schema is package-owned with
format checks; timestamp/evidence/identity semantics remain tool-owned.

Query's decision digest binds normalized store path, exact query text, schema
version and sorted selected filenames/raw-byte digests/errors, including
nonmatches. Create always reruns that query under its writer lock and compares
the actual digest before publishing. Partial reads require an explicit decision
acknowledgment and remain partial. A digest is not an authorization or dedup
receipt. Revision uses expected raw-byte hashes, preserves identity/time and
extensions, and retains exact bytes/time on equal authored content.

Writes use one token-owned lock, exclusive create from a complete same-directory
temporary file, same-directory replace for revision, actual flush/readback and
owned transient cleanup. Outcomes retain `none`, `committed` or `unknown` record
publication state on failure. There is no rollback claim, stale-lock deletion,
adoption/promotion, export write, delete or migration operation.

## Limits requiring P7 attention

- One cooperating writer per store; arbitrary external editors are not a
  transaction or compare-and-swap participant. Content/path checks narrow races
  without claiming adversarial filesystem isolation or crash recovery.
- Selected symlinks/reparse paths are rejected even when contained. Windows
  write support is scoped to local fixed/RAM NTFS; Linux to identified local
  ext2/ext3/ext4/xfs/btrfs/tmpfs/ramfs mounts. Other backends are unsupported for
  writes. These are code paths, not tested-platform acceptance.
- Missing store parents must themselves be within allowed roots. Default
  `notes/lessons` requires `notes` to be provisioned or separately authorized.
  Created empty directories are disclosed and retained after failures.
- Per-file/request/record limit is 4 MiB; query maximum is 10,000 direct record
  names. Unknown/unreadable records produce partial diagnostics. A read-only
  query does not freeze concurrent external edits; create reruns under lock.
- Local config in a Git project requires read-only Git ownership/ignore checks;
  Git is otherwise unnecessary. No ambient GIT_* repository override is used.
- Template replacement is single-pass inert text, with authored Markdown/HTML
  escaped. Rendering returns a view only.

P7 should select focused strict-parser/config/path, stale-query/hash/lock,
extension/no-op, partial-read/template and publication/cleanup failure cases,
plus real supported filesystem trials. These are future work suggestions, not
new tests, test commands or acceptance evidence in this delivery.

## Actual inspection and allowed checks

All repository commands ran with explicit `workdir: F:/framework-next/330`.
All edits used absolute paths under the two assigned roots. The live Issue was
read through the GitHub connector; no provider mutations were made. Initial
Git branch/HEAD/status and persistent common database were read back.

At `2026-09-23T01:55:19+08:00`, an inline `python -` readability command read the
two owned trees as UTF-8, parsed Python with `ast.parse(text, filename=...)`,
parsed JSON with `json.loads`, and parsed YAML with `yaml.safe_load`. Actual
counts were 11 UTF-8 files, one Python syntax tree, two JSON files and two YAML
files. This did not import/execute product source and is not schema or behavior
validation. A later content change requires the final syntax readback below.

At `2026-09-23T01:56:29+08:00`, an inline `python -` read the metadata with
`yaml.safe_load`, collected its entrypoint/resources, compared exact actual file
paths and inspected Markdown relative link destinations. Actual result was
eight exact members and six existing local file targets. The same command
parsed `scripts/lesson.py` via `ast.parse` without import. The query/operations
anchor was also reviewed directly in the Markdown source.

Content inspection found and corrected missing-parent permission expansion,
store identity drift, potential nonregular-file blocking, and unnecessary store
creation by revise. These are author inspection corrections, not findings from
executed tests or independent review. An initial documentation patch did not
match its expected paragraph and changed nothing; the corrected additive patch
was applied. No failed behavior trial was rerun or erased.

Final parsing, staged scope/diff and exact planned-message check results are
retained in `../handoff.yaml` and the commit's `Validation` section. Earlier
`git diff --check` against an untracked tree did not establish staged whitespace
coverage; the final staged check is the relevant result.

## Coordinator integration

The coordinator accepted the eight-member metadata-v1 plan and passed it to
#331. Do not widen the assembly manifest to a glob. No unresolved substantive
cross-contract decision is known. The exact source closure and public protocol
are ready for that owner's integration; no builder/tool execution has occurred.

After the local commit, read exact HEAD/message and clean worktree, then send
the coordinator the immutable identity, actual/deferred checks, eight members,
limitations and the proposed shared-index row. Coordinator owns first push,
remote branch/PR/merge and Issue/Project disposition.
