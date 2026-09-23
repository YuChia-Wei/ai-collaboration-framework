# Issue #370 fixed-source installation review

- Review ID: `ISSUE-370#CR-001`; status: final source review, **remediation recommended**.
- Issue: [#370](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/370), read live as OPEN with no comments on 2026-09-23.
- Reviewed product commit: `38e6458f8d3e81dc2568daf1fa467571fb529fee`.
- Review checkout/start: `F:/framework-next/370`, `codex/2026-09-23-installation-source-review`, `ea627ad8bb9251b31035b494c8d1d6c235461c2f`.
- Artifact commit: the containing commit of this report; resolve with `git log -1 --format=%H -- .dev/workflows/2026-09-23-installation-source-review/report.md`.
- Authoring provenance: coordinator-selected independent OpenAI Codex / gpt-6-astra / ultra conversation; declared selection, not separate runtime attestation. No sub-agents or cross-task callbacks.
- Template: `.ai/assets/skills/code-reviewer/templates/code-review-assessment-report-template.md`, version 1.1.0, proportionately adapted under U001 and #370 to this workflow only.
- Created: 2026-09-23T15:17:15+08:00; updated: 2026-09-23T15:18:09+08:00.

## Criteria and method

Authority is the live [#359 assignment](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/359), the actual [managed-installation handoff](../../design/framework-next/managed-installation/handoff.md), [selected P6 contract](../../design/framework-next/p6-selected-contract.md) and its selected [contract](../../design/framework-next/installation-update/contract.md)/[formats](../../design/framework-next/installation-update/formats.md), plus #364's [selected checks](../../design/framework-next/verification-design/selected-checks.md), [Windows cases](../../design/framework-next/verification-design/windows-pilot.md) and the coordinator [P7 addendum](../../design/framework-next/p7-execution-selection.md). The latter selects an explicit F: native root and process-termination only; it supersedes the earlier proposed C: native root.

Applied the code-reviewer common reasoning route and primary review role inline. No .NET, aggregate, controller or reactor extension applies. ai-context-governance supplies proportional workflow/handoff recording. This is contract-based source reasoning, with no effective-rule catalog certification. U001/#370 explicitly defer legacy subject validators, effective-rule packets, audit/lease/receipt and acceptance-ledger machinery; no separate assessment/index was created.

Fresh graph `issue370-distribution` was indexed from this worktree's `src/distribution` with `mode=fast,persistence=false`: 221 nodes, 1486 edges, 0 skipped. File-node read-back covered 13 direct files, including all nine selected distribution files. The tool exposed no commit attestation, so freshness was externally bound by the stable HEAD and the Git/raw-byte checks below; graph edges were discovery hints, not proof. Used search_graph, get_code_snippet and a bounded apply call trace, then exact numbered content reads. The one explicitly named entry outside that bounded index, imports/constants and source gaps used tracked-file reads. No broad source/test/history scan or graph absence claim.

## Reviewed file identity

For every row, fixed-subject blob = starting HEAD blob = checkout blob. A separate direct byte comparison against `git cat-file blob <subject>:<path>` also matched (no checkout normalization). All ten decoded as UTF-8 and passed `ast.parse`, without importing product modules.

| Path | Git blob |
| --- | --- |
| `src/tools/maintain_framework.py` | `94741f16abaf17e221472f9b03f9cfa0953e4c66` |
| `src/distribution/__init__.py` | `fca5683977f2046233795428cc0c16feece19ce6` |
| `src/distribution/data.py` | `2d971b3d95ee66f7604719046f13cdc90c394305` |
| `src/distribution/git_source.py` | `f6b041d068fe553047f6bd615b7b13b8d2d6e122` |
| `src/distribution/package.py` | `0dc910ca76f4835a5cbf172abbda7595088861a9` |
| `src/distribution/installation.py` | `958c8b6ae64168b14889187fb431db1736fe4dae` |
| `src/distribution/installation_io.py` | `93ba125f1d613c6afc7bc0b9a7b5b1321d74e82c` |
| `src/distribution/installation_plan.py` | `745d028a9e3736af7a4f5382b0123fec99754a29` |
| `src/distribution/installation_state.py` | `9f74ec2e5645fdf261918eba3fc304382b5b8d56` |
| `src/distribution/maintenance_coordination.py` | `d6bdb5147678d62580cdbb392c2c9cae53877298` |

Read scope was these ten files and selected contract/policy records. GitSource's subprocess builder path is not invoked by maintenance; its Blob type is the relevant consumer dependency. No candidate-producer or product-test execution was used.

## Finding CR-001 — MUST FIX / P1: cached local bytecode can bypass the source pin

**Location:** [maintain_framework.py lines 117-126](../../../src/tools/maintain_framework.py#L117), especially `package_spec.loader.exec_module(package)` and the subsequent normal `distribution.installation` import. Supporting checks: [installation_state.py lines 821-837](../../../src/distribution/installation_state.py#L821).

**Trigger:** a provisioned engine checkout already contains an interpreter-compatible stale `src/distribution/__pycache__/installation_io.*.pyc` (or another pinned local module's cache), with either an unchecked-hash header or timestamp/size metadata that still validates against the selected source. This needs no concurrent writer, changed pinned .py bytes, malicious host library or loaded-memory modification.

**Actual path:** bootstrap hashes the ten .py files (lines 95-107), then uses standard source loaders. Those loaders can read an existing cache even under `-I -B`/`sys.dont_write_bytecode=True`. A cached module still has the expected .py `__file__` and module name. The later `_engine` hash/origin/module-set checks therefore all can match while the local implementation executing, for example, publication logic is older than the verified source. The cache is not an EnginePin member.

**Evidence:** Python documents [-B](https://docs.python.org/3/using/cmdline.html#cmdoption-B) as disabling cache writes. In [CPython 3.11.9 SourceLoader.get_code](https://github.com/python/cpython/blob/v3.11.9/Lib/importlib/_bootstrap_external.py#L934-L1014), cache read/validation and return precede the separate dont_write_bytecode write guard. [Cached bytecode rules](https://docs.python.org/3.11/reference/import.html#cached-bytecode-invalidation) describe timestamp/size and unchecked-hash admission. These explain the source path; no cache fixture or public entry was executed here.

**Expected/consequence:** #359 requires the complete actual local executing closure bound to the fixed pin. Two starts with identical accepted EnginePin/source bytes can instead execute different maintenance or recovery behavior because of an unpinned local cache. The handoff's exclusion of host authenticity and loaded-memory attestation does not exclude ordinary local loader input from that closure.

**Smallest repair/test:** make every allowlisted local distribution module load by compiling the exact verified source bytes through a source-only loader, including package initialization and transitive imports; do not rely on -B or delete user caches. Retain current host dependency boundaries. Extend selected N1 with one bounded public-entry regression using a deliberately different valid cache for a local engine module and unchanged source pin: it must execute pinned source or refuse before product code dispatch. No project mutation is needed for that regression. Coordinator assigns repair and affected changed-source review.

Confidence: high in this source-level defect; runtime reproduction unexecuted. This is a defect in the inspected subject, with no claim about when it was introduced.

## Other examined behavior and limits

No additional substantiated defect was found in the following traced paths; these observations are not native acceptance:

- Strict integer versions/sizes, bounded closed JSON/YAML, raw candidate/member hashes, available Git blob bindings, metadata 1/2/3 owner/reference reuse, and exact candidate closure.
- Plan/apply binding includes roots, engine, candidate identity, old raw lock, all-old member drift, protected inputs, exact maintenance scope and under-lock recomputation. Guard creation is excluded from the unknown-package observation and stable prerequisites, avoiding plan-hash churn.
- Native writer coordination uses held handles, never guard replacement/unlink. No-op requires an existing guard and skips ID/allocation/capture/marker/lock/mode writes.
- Durable before/after objects, both locks and three metadata documents are read back before marker admission. Changes use exact siblings; complete target/protected read-back precedes lock publication; marker removal is last.
- Recovery checks exact operation/engine/root/control bindings, before/after/defined-absence states and unknown sibling preservation. Marker-free completed operations cannot authorize rollback. Caller-protected data remains separately owned.
- Path containment, aliases, links/reparse points, hardlinks, native volume boundaries and 240/255 UTF-16 budgets were inspected, together with partial-write counts and failure results. Native syscall behavior was not established.

Documented conservative refusals remain limitations: incomplete capture residue, unknown/partial siblings, the retained guard after clean-install restore, and ambiguous partial whole-loss reconstruction. They do not justify force cleanup, overwrite or a new journal here. Power loss, hostile concurrent writers, whole-project readiness and broad platform coverage are not promised.

## Actual checks, retained interruptions and handoff

Executed read-only checks: explicit workdir/root/branch/full HEAD/common-dir/status; live `gh issue view 370` and `359 --json ...`; ten per-file `git rev-parse`/`git hash-object` comparisons; direct raw-byte `git cat-file` comparison and AST/UTF-8 parsing via an isolated stdlib-only review script; selected source/reference reads; bounded graph discovery; official Python loader/documentation reads. Initial and pre-report status were clean, and the selected product diff from the fixed source was empty.

The first sandboxed GitHub read failed at the restricted local proxy. The explicitly authorized normal read-only escalation succeeded. There was no automatic approval rejection. An attempted read of a guessed `verification-design/native-cases.md` path found no file; bounded tracked-file inventory located the actual `windows-pilot.md`. Neither event is a validation pass or a product failure.

Coordinator supplied an external #368 observation during this review: F: output-root `Path.resolve(strict=True)` returned Windows “Incorrect function” before its product tests began. This reviewer did not reproduce or probe it. Here, bootstrap `_direct` and state `_root` also use strict resolve, and their public boundaries catch OSError as refusal; applicability to this exact engine/backend remains unresolved. Preserve that external evidence and let its owner isolate it; do not call it native acceptance or bypass it with another root.

Product CLI/help/imports, schemas, fixtures, tests, build/install/recover/native probes, CI and legacy verification: **deferred-by-owner**, U001 / program #322 coordinator / P7, except this explicitly selected source review. Next action is the separately assigned CR-001 repair, N1 regression and affected fixed-source re-review, followed by selected N2-N5 evidence and explicit residual disposition. No product-wide/security certification, provider acceptance or native execution is claimed.

Direct review-record UTF-8/JSON/YAML syntax, local reference, selected-scope and unchanged raw-subject checks passed. The complete planned-message validator passed (exit 0) using commit-message.tmp and this workflow ID. Only report.md, workflow.yaml and task.json are intended tracked changes; staged diff/scope checks precede local commit; the ignored commit-message.tmp stays inside this workflow. Report transport commit is separate from the reviewed product SHA. Coordinator owns repair assignment, transport, PR/merge and Issue/Project lifecycle; this executor does not push or change providers.
