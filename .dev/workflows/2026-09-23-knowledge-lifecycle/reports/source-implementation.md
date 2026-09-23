# Source implementation completion

## Identity and authority

Issue [#334](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/334),
program [#322](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/322).
Assigned worktree `F:/framework-next/334`, branch
`codex/2026-09-23-knowledge-lifecycle`. Original design checkpoint
`99adb0762328c8f8d6cff7338f17caec99685c0a` is preserved; this same task fast-forwarded
to selected shared contract `0d0556d4c60105a28eb39cfb06efab9b069728cb` before source
implementation. The containing local commit identifies final source; exact HEAD
is returned externally without a self-referential tracked update.

Coordinator continuation selected Lesson 0.2.0, ADR 0.1.0 and standards-promotion
0.1.0, metadata/config v2, empty skill dependencies and the three exclusive source
roots. Governance owns workflow records; slice-implementer owns this generic source
slice. U001 displaces legacy validation/audit ceremony. Explicit model/effort dispatch
is gpt-6-astra / ultra, not independent runtime attestation. No sub-agents, new tasks,
new worktrees, push, PR, provider writes or publication were performed by this source
continuation. Shared distribution/manifest/profiles and coordinator indexes are untouched.

## Implemented source and compatibility

| Package | Exact members | Public operations | Record versions |
| --- | --- | --- | --- |
| lesson@0.2.0 | 9 | 11 | v1 read only, v2 read/write |
| adr@0.1.0 | 8 | 11 | v1 read/write |
| standards-promotion@0.1.0 | 9 | 10 | v1 read/write |

Exact lists are in [interface inventory](../../../design/framework-next/knowledge-lifecycle/interface-proposal.yaml).
All packages carry standalone entry, metadata, configuration/operation/example
references, owned schema/template and script; promotion adds an authority reference.
No private cross-package imports, shared runtime or undeclared helper/member fields.
Local strict filesystem/parsing/publication primitives are deliberately duplicated.

Lesson retains v1 schema Git blob `8bced2d86584c87d34f8ca2927aab95b7802a3ac` and the
closed v1 configuration interpretation. New lifecycle records are v2. Legacy records
are read-only; explicit derive captures source bytes into a NEW candidate, retaining
original identity/bytes and resetting decision. ADR records alternatives and actual
mapped owner evidence; corrections derive a new draft. Histories retain prior state,
raw digests and timestamps; successor changes affect only the predecessor.

Promotion persists one-file replacement proposals with exact source/baseline/config
snapshots and separate raw-record/proposal-subject digests. It independently reads
adoption, actual rule bytes and declared effect. It never writes rules/approvals/effect
files or infers authenticated identity. Once adoption was EVER observed, revise is
blocked even after revocation; conflicts require a new proposal identity and new
adoption. Missing/malformed mapped evidence does not hide other known dimensions;
unsafe/unreadable/oversized/non-UTF-8/drifted input fails the new observation.

Config v2 validates the full strict JSON envelope then only owned namespace contents;
foreign object names may be explained, never their values or permissions. Metadata v2
uses exact schema pairs/read_schemas. New schema references are bounded local-only.
All packages retain explicit roots, narrow write authority, raw digest concurrency,
inert one-pass rendering, partial query disclosure and bounded single-record writes.
Shared distribution support/mappings remain #337/coordinator-owned.

## Actual permitted checks

These are executor source inspections, NOT independent review, schema acceptance or
behavioral execution. Narrow direct checks used `python -B -` with standard file,
AST/JSON parsing and PyYAML data reading; no product module was imported or invoked.

- Direct UTF-8/read inspection of the then-current 39 owned files, AST parsing of
  all 3 scripts, JSON parsing of 10 files and YAML parsing of 5 files completed.
- Direct Markdown destination inspection found no missing targets in 49 local
  links; inspection of 96 same-document schema references found no missing target.
  This checked reference existence, not schema validity or record compliance.
- Direct metadata/file inventory found exact 9/8/9 members with no extras/missing
  files; literal AST operation/version declarations match 11/11/10 metadata rows.
- Metadata source inspection confirmed no aliases/anchors/tags after expanding the
  initially generated YAML aliases. No product loader was run to obtain that finding.
- `git diff --check` completed without whitespace errors; branch/HEAD/status and
  changed-path scope were read directly. `git hash-object -- src/skills/lesson/schemas/lesson-record.schema.json`
  reproduced the exact required legacy blob above.
- Final retained report/metadata/status reinspection completed at
  `2026-09-23T08:54:07+08:00`: 40 readable files, 3 ASTs, 10 JSON files, 5 YAML
  files and 51 local Markdown links, with no reported syntax/reference issue.
  The exact planned message command
  `python -B .ai/scripts/validate-git-commits.py --message-file F:/framework-next/334/.dev/ai-context/local/commit-messages/334-implementation.txt --workflow-id 2026-09-23-knowledge-lifecycle`
  exited 0 with `Git commit validation passed for planned message.`

Source inspection also corrected snapshot-capture digest races, input alias checks,
captured binding shapes, retained observation chronology, type-aware history/state
rules and publication read-back mutation state. These are source changes; they do
not constitute evidence of passing their runtime behavior. The earlier checkpoint
report retains its prior approval-review limitation and narrow design observations.
Discovery continues the documented known-source fallback because the graph excluded
the package script path; no graph absence or stale index establishes implementation facts.

## Deferred execution and residual limits

Disposition: **deferred-by-owner**. Authority: U001. Owner: program #322 coordinator /
P7. Next action: select redesigned focused checks and record actual outcomes.
Do not run product CLI (including help), schema validation, tests, build/install,
package/migration/compatibility/benchmark trials, independent audits/leases,
legacy framework validators or CI to admit this development checkpoint.

P7 should select mixed Lesson v1/v2 preservation/derive, config namespace/type/lock
and local-config cases, metadata/local-reference handling, history/decision/successor
transitions, inert/legacy templates, source/query/input drift and malformed data,
write/cleanup/publication uncertainty, and independently varied promotion adoption/
content/effect/conflict cases. Platform and filesystem semantics, concurrency,
privacy-safe diagnostics and declared local-evidence trust remain unexecuted limits.
No synthetic example, local parse or commit substitutes for actual behavior.

## Return and remaining ownership

KL-001/KL-002 and this bounded source workflow are completed under U001. Issue/Project
closure, actual package integration, shared mapping, independent/runtime acceptance,
CI restoration, release and publication are separate and not claimed. No unresolved
shared-contract decision remains in this slice. The coordinator receives exact
local HEAD/branch/worktree and inventory before first push, integrates the delivery
and supplies concrete package mappings to #337. P7 owns the deferred verification.
