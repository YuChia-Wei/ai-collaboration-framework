# Source package build and Draft Release pipeline

This connected #418 slice is authorized by the owner's 2026-10-01 instruction
under #322/R2 and the coordinator assignment. Intent: implement source release
delivery. Owning skill: `slice-implementer`, `implement`, generic mode; no
specialist package or remediation overlay selected. The assignment chooses
Python standard-library transport plus the existing public Catalog 1 / Engine 2
builders, two GitHub workflows and the bounded current-format release policy.

Worktree `F:/framework-next/418`, branch
`codex/2026-10-01-release-draft-pipeline`, base
`269ab4e1b3d6a0af1e5c738689459f9879c655d1`. One tracked writer; no edits to
other worktrees, installed projections, product parsers, other workflows,
shared indexes or historical release records. Actual executor:
`OpenAI Codex Sub-Agent (gpt-6-astra, ultra)`, coordinator-dispatched.
The graph call lacked an indexed project identity and no project-list tool was
available; exact tracked files and direct call sites were the explicit fallback.

This workflow has two substantive tasks because release-byte custody and the
immutable build boundary need durable execution state. It follows the
source-owned `WORKFLOW-ARTIFACT-POLICY.md` format directly under U001. No active
workflow/task template exists in the selected source inventory; no retired
portable template or validator is claimed.

| Task | Acceptance | State |
| --- | --- | --- |
| S1/T1 | Exact-source full catalog/24-file engine, independent pre-execution pin, safe complete ZIP and manifest; separate read-only build and owned draft writer; owner notes/publication handoff | completed |
| S2/T2 | Focused transport fixtures, direct syntax/YAML/link/diff/message checks, actual clean immutable source build and raw/extracted ZIP verification | in_progress |

## Selected behavior and acceptance

- Main push/manual produces a SHA-named snapshot artifact, without a Release.
- Existing annotated stable/rc.N tags produce a generic draft package. Old-tag
  manual dispatch uses current workflow/tooling bytes and exact old product bytes.
  Original tags are never created/moved.
- Product `distribution_version` accepts only stable/rc.N. Coordinator accepted
  that scope explicitly; arbitrary SemVer prereleases fail before draft writes.
  Snapshots use a positive SHA-derived rc.N label and explicit snapshot naming.
- Raw independent pin hashes both matching literal `ENGINE_FILES` declarations'
  24 files before executing the selected public builder. No new release tool is
  part of the engine pin or downstream archive.
- ZIP entries include full catalog metadata and standalone engine descriptor
  `{engine: PIN, engine_package_version: 1}`. An external manifest binds exact
  archive bytes plus tag/source/catalog/engine/workflow/run identities. Actual
  timestamp-bearing metadata makes byte-identical rebuilds unpromised.
- Authenticated paginated release discovery, ownership/admission marker, no
  public-release writes, preservation of human notes/title, all-existing-assets
  preflight, raw provider download verification and clear partial-failure receipt.
  Exact original artifacts support rerunning failed writer jobs.
- No AI runtime/token, Issue/Project mutation, final publication, source tag
  metadata commit or per-version tracked notes/admission prerequisite.

The source-only release exception is scoped to these operations. Seven other
workflows, test CI, legacy/native/product/history/full suites, ordinary dormant
source policy and full P7 restoration remain `deferred-by-owner` to #322/P7.
Package assembly and fixtures do not establish those acceptance layers.

## Local evidence

- 19 new release transport fixtures: passed, unittest 0.469 s / command 0.863 s.
- Four changed Python AST parses and two workflow YAML/trigger/action-pin
  inspections: passed with PyYAML 6.0.3.
- Official read-only Action tag verification:
  upload-artifact v4.6.2 `ea165f8d65b6e75b540449e92b4886f43607fa02`;
  download-artifact v4.3.0 `d3f86a106a0bac45b974a628896c90dbdf5c8093`.
  Checkout/setup-python pins retain the source-selected verified v6 commits.
- Actual immutable package build: pending the clean implementation commit.
- Selected spec compliance: not-applicable; this slice uses explicit assignment
  acceptance and authentic local build/transport evidence, no formal spec gate.
- No product test suite, native test, legacy gate or full P7 outcome is claimed.

Tool-writing attempts with malformed JavaScript quoting failed before any
filesystem mutation and were corrected. A graph request without project identity
returned a missing-argument error; direct tracked fallback was then used. These
are preparation failures, not package or product failures.

## Handoff and lifecycle

The coordinator owns push/PR/merge, activation of only the two workflows,
actual hosted run and provider/Issue reconciliation. They are separate from
local implementation completion and are recorded by that owner in GitHub/Actions
or ignored provider receipts, with no pending provider task or post-tag tracked
status commit required here. Public publication remains a later explicit owner
action. Proposed integration topology: merge commit, because the delivery and
local immutable-build checkpoint form a reviewable release-transport boundary.

Read the [release guide](../../guides/implementation-guides/FRAMEWORK-RELEASE-DRAFT-GUIDE.md)
for exact CLI commands, retry custody and AI-session capability requirements.
The executor returns local commits and explicitly releases writer ownership
before independent fixed-head review. No provider mutation is authorized for
the executor.
