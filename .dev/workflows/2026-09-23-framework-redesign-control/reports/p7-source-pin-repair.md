# P7 source-pin repair and affected review

[Issue #371](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/371)
returned local commit `0d29b9abf36804cb2587732232d807a1b754c3a0` from
`fe6c63f87cb54e166fc796fd315f11e3c2212823`, in the assigned independent Astra
Ultra task and F:/framework-next/371. The task is idle and worktree clean at
handoff. No executor push or provider mutation occurred.

## Exact scope and evidence

Six files changed: the maintenance bootstrap, one focused test entry and four
Issue-owned workflow/evidence files. Only `src/tools/maintain_framework.py`
changes product bytes. It compiles verified retained source bytes for the
allowlisted distribution package/modules, including delayed imports; no cache
deletion, path fallback, new engine member or recovery change is included.
The nine distribution files remain byte-identical to the earlier reviewed
product. This is the worker's source repair, not yet independent acceptance.

The coordinator inspected all six fixed files, direct AST/JSON/YAML/UTF-8,
scope/whitespace and six local links. No product imports or runtime rerun were
performed. The product-path delta is exactly the one authorized bootstrap.

Actual worker evidence from the [handoff](../../2026-09-23-engine-source-pin/report.md):

- Nine focused loader tests passed, zero skips, 1.279 s. Bootstrap unit cases
  explicitly substitute the path predicate; they do not prove native path
  admission. Actual source-loader controls admit deliberately different valid
  caches while the repaired loader executes retained source.
- The single unmodified public-entry attempt refused before dispatch with
  `source-bootstrap` / `unsupported`, child exit 1, `changed=false`. The generic
  response does not isolate a particular bootstrap predicate. No public-entry
  success, project mutation or native acceptance is claimed; no retry occurred.
- The failed public fixture remains at the exact F: child named in the worker
  report. Logical file/byte/process observations, first helper-check failure and
  CRLF/staged-byte preparation failure are retained. Product/test bytes were not
  changed by the record/message LF correction. No physical-I/O claim is made.

The required public-entry N1 positive/cache behavior and later native N2-N5
remain coordinator/P7 obligations. They cannot be filled by loader unit evidence
or by changing to another drive. The stopped #368 path/metadata and #369 policy
batches remain exclusively owned by those original tasks, pending direct owner
confirmation. #371 takes over neither.

## Independent affected review

The original #370 task was idle and its worktree clean at
`6de20bfeb059d74f1ba0ede96c28d312db04235f`. The coordinator fast-forwarded that
same worktree/branch to `0d29b9abf36804cb2587732232d807a1b754c3a0` and assigned
read-only inspection of the loader delta and actual test/evidence limits. The
original report remains preserved. Allowed writes are only its existing review
workflow; no tests/product/native execution or repairs are assigned. Its result
has not returned at this checkpoint. CR-001 remains pending that disposition.

No CI restoration, source-policy activation, root adoption, release or downstream
acceptance is part of this repair/review checkpoint. Referenced implementation
and review commits must be preserved by the coordinator's online integration.

## Independent return

The original #370 task returned `066a964efe95062179bb1eff1376fc4b73aecb17`,
with clean worktree and three review-only changed files. Its conclusion for
product `0d29b9abf36804cb2587732232d807a1b754c3a0` is **CR-001 resolved in source;
no substantiated new defect in the affected delta**. The original report and
product bytes remain unchanged. Coordinator inspection of three fixed records,
direct JSON/YAML/UTF-8/scope/whitespace and local references passed.

The reviewer executed no product tests. Nine worker-run unit cases do not
establish a successful allowed delayed import, and the one public-entry request
lacks complete operation fields. Its observed bootstrap refusal remains valid
negative evidence, but even passing bootstrap would not make that request a
successful public operation. A later positive N1 case must use a complete valid
request after path applicability is resolved. Public/native obligations remain
with program #322 / selected V3; the source review does not close them.

The coordinator assigned the existing #371 executor a test-only follow-up for
successful delayed import of an allowed module with a deliberately different
valid cache. It cannot change product/helper/runner bytes or retry the public
attempt. The current source-review conclusion remains bound to the same product
bytes; additional test results are reported separately when actually returned.

## Test-only return and bounded disposition

The original #371 executor returned `dc0f5c65d6dbfdd0954886340b149f99453c6705`:
five test/record files, with product/helper/runner raw bytes unchanged from the
reviewed source. The focused suite ran once with the new positive delayed-import
case: **10 passed**, zero skips/errors, 1.629 s. Original 9-pass and public refusal
observations remain. Coordinator inspection confirms only one test method was
added, unchanged prior test methods, direct syntax/scope/whitespace and no
product/helper/runner delta. This new worker-run evidence is not reviewer execution.

The coordinator accepts bounded #370 source review and #371 source repair as
locally complete, selected for online closure. The resolved finding is source-
level CR-001 only. Full EnginePin operation admission, a complete valid positive
N1 request, native N2-N5 and root adoption remain open under program #322 / V3,
with existing path applicability unresolved. Closing these two bounded work items
must not close those program obligations or the stopped #368/#369 tasks.

Issue #373 now owns the independent V2 public-skill layer using the published
helper and direct committed package-resource fixtures. Its tests do not depend
on real candidate assembly or installer activation and must not claim either.
It owns only new public-family test files and the public dispatch arm of run.py;
contracts/helper/native/product semantics remain unchanged. Actual failures go
back to owning repair assignments, with no substitution for stopped writes.
