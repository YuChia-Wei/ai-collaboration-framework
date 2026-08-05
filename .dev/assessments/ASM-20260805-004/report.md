# v0.9.0 Candidate Package And Release Contract Verification

## Template Metadata

- `template_id`: `ai-context-auditor-report`
- `template_version`: `2.1.0`

## Metadata

- `assessment_id`: `ASM-20260805-004`
- `assessment_type`: `ai-context-verification`
- `owner_skill`: `ai-context-auditor`
- `status`: `final`
- `audit_date`: `2026-08-06`
- `created_at`: `2026-08-05T23:59:00+08:00`
- `updated_at`: `2026-08-06T00:16:57+08:00`
- `repository`: `C:/Github/YuChia/ai-collaboration-prompts-dotnet-backend`
- `subject_branch`: `codex/2026-08-05-v0-9-0-release-publication`
- `subject_commit`: `773b96cb742f09fd2744ae63b85d982ee3d61822`
- `base`: `main@5d9af93b35b299377194f98709ecfbaec7fb0222`
- `workflow_ref`: `.dev/workflows/2026-08-05-v0-9-0-release-publication/workflow.yaml`

## Executive Summary

- Overall assessment: the candidate consistently binds the exact eight-item
  release scope, CTX-004's intentionally source-only analyzer-test boundary,
  deterministic rewritten archives, the v0.8.0-only migration source, and the
  post-filemode critical gate.
- Decision: `healthy-with-followups`; the source-local `planned -> validated`
  transition is permitted.
- Active findings: none. The two provisional HIGH concerns found before
  evidence remediation are resolved by the immutable-tree, archive, and
  critical-gate read-back below.
- Remaining lifecycle gates: candidate-state validation after the record is
  advanced, reviewed hosted integration, merged-main pre-tag validation,
  user-owned tag creation, hosted publication, and final provider read-back.

## Scope

### Included AI Context Surfaces

- v0.9.0 release record, notes, migration contract, exact backlog membership,
  and the specialized release-publication workflow/task.
- Package profiles, archive metadata, sidecars, package validation, package
  apply behavior, and clean-install / exact-v0.8.0 upgrade receipts.
- Candidate critical-gate evidence, commit/rewrite equivalence, and release
  contract validators.
- CTX-004's bilingual root navigation and the exclusion of
  `tools/DotnetBackendAnalyzers.Tests` and
  `tools/DotnetBackendValidation.Tests` from downstream payloads.

### Exclusions

- Product source and product-test implementation trees; no code review was
  requested or performed.
- Live GitHub Issue, Project, pull-request, hosted-check, tag, Release, and
  publication state. In particular, this assessment does not create or read
  back a local backlog item for Issue #128.
- WSL runtime discovery, installation, and execution. All observed local
  validation used the Windows host Python runtime; no WSL Python or .NET
  prerequisite was inferred.

## Methodology And Evidence

### Pass A: Independent Baseline

The auditor recomputed both rewritten archive pairs and their sidecars, ran the
package validator over both pairs, read the archive metadata, and compared the
old and rewritten package subjects. The results establish that only the
envelope source commit and archive hashes changed after the commit-message
rewrite:

| Subject | Git tree / source | Payload paths | `files.yaml` | `migration.yaml` |
| --- | --- | ---: | --- | --- |
| Original package subject | `25ae56647a93668c800409f4306a9485b78cce3c` / `863f50ae4679b3d908299435168d118414284262` | 652 | `c293247612eb2f01ef42e4d7c55be4ff36201cdf034157c518de871ec2acb5c7` | `ca0ec6f7d8694549a3cf6cfa6ef22bcfe7da88f7d7900b2c24e9f58c8f00d27a` |
| Rewritten package subject | `d3236e6dfe54c56a5b9d040e95071569ccc493a3` / `863f50ae4679b3d908299435168d118414284262` | 652 | `c293247612eb2f01ef42e4d7c55be4ff36201cdf034157c518de871ec2acb5c7` | `ca0ec6f7d8694549a3cf6cfa6ef22bcfe7da88f7d7900b2c24e9f58c8f00d27a` |

Both fresh builds produced the same current envelope artifacts:

- ZIP: `db314ef5f1f0428f6e0907a7877c0050575c9f58f2f3a54528528ff6f0d4195f`
- tar.gz: `d1c7e2dd1349fa8c62573ef62da01c1a196a2d2dbf8c34c1e8cfc6a779db3208`

Each digest matched its adjacent sidecar and both ZIP/tar archive-validator
runs passed. Archive metadata pins `d3236e6dfe54c56a5b9d040e95071569ccc493a3`
and contains no analyzer-test project payload path.

The owner explicitly waived a duplicate clean-install and exact-v0.8.0 upgrade
fixture execution after the message-only rewrite. That waiver is limited to
these byte-identical payload, inventory, and migration surfaces; it does not
waive the rebuilt archive, checksum, sidecar, or package-validator checks.
The inherited fixture evidence remains: clean install 649 applied plus one
intentional reconciliation, and exact v0.8.0 upgrade 360 applied plus the sole
`migration-0345` reconciliation, both with 636 required paths, zero missing
paths, and zero SHA mismatches.

### Pass B: Repository-Aware Skill Review

- `validate_backlog_refs` accepted exactly `GOV-004`, `PKG-005`, `GOV-006`,
  `CTX-004`, `CTX-005`, `PKG-006`, `VAL-003`, and `SAG-002`, each with the
  required resolved/completed release state.
- The workflow is a `release-publication` workflow using the specialized
  `release-workflow-locator.yaml`, and its sole task is the specialized
  `REL090-001` release-publication task. Its authorization explicitly excludes
  a local #128 record, source-only test movement, WSL installation/use, and
  tag mutation.
- `CTX-004` is resolved for v0.9.0. The bilingual README navigation links the
  stable bundled mechanical-validation landing page and consistently identifies
  the two provider test projects as source-only.
- The critical gate started at
  `cc832b4ec0264743854e99a7d3d7f3bf03c915ac`, after the filemode remediation,
  and passed all 49 selected checks in 951 seconds. Its tree
  `fe817e8807b8bb54b796c07441c28a0646925942` equals rewritten evidence commit
  `bb16471c04ca7fa93db699112a5742dbe7020052`. The only later changes through
  this assessment subject are candidate evidence and workflow-plan wording;
  no `.ai`, `.agents`, or `tools` path changed after the package subject.
- The focused `core.filemode=false` safe-replace GWT passed. It proves the
  narrow allowance for byte-identical `0755` versus `0644` executable-mode
  loss while retaining reconciliation for every other hash or mode drift.

### Lifecycle Interpretation

`release.status` remains `planned` by design while the independent assessment
is made. Consequently, the candidate-phase validator currently exits nonzero
with `release.status must be 'validated' in candidate phase`. This is the
expected pre-transition condition, not a release-candidate finding. This final
assessment is the evidence that permits the release owner to make that
source-local transition; it does not make the transition itself.

## Strengths

1. The release scope is exact, fail-closed, and excludes the owner-designated
   online-only Issue #128 from canonical backlog accounting.
2. A commit-message rewrite no longer leaves stale archive identities: the
   new archive source, two-build hashes, sidecars, and deterministic metadata
   all point to the rewritten candidate.
3. The v0.8.0 package is the sole declared automatic and reconciliation source;
   the one upgrade reconciliation remains explicit and target-preserving.
4. CTX-004 improves navigation without relocating source-only tests or
   broadening into analyzer behavior, Architecture Kit cutover, or payload
   scope.
5. The critical gate and focused filemode regression stay outside WSL and do
   not misrepresent unavailable runtime prerequisites as a passing check.

## Findings

No CRITICAL, HIGH, MEDIUM, LOW, recurring, or regressed AI-context finding was
identified in this bounded candidate verification.

The provisional evidence-binding concerns raised before commit `773b96c` are
closed, not suppressed: the current archive source and hashes were rebuilt and
independently rechecked, while the critical run is explicitly tied to an
identical post-filemode tree. The accepted owner waiver is recorded as a
bounded validation choice rather than a claim that the duplicate fixtures ran.

## Validation

| Check | Result | Evidence / Notes |
| --- | --- | --- |
| Candidate commit range | passed | `validate-git-commits.py --range main..HEAD --workflow-id 2026-08-05-v0-9-0-release-publication`: 7 commits |
| Workflow artifacts | passed | 63 post-adoption workflows, 83 indexed directories, 55 backlog items |
| Diff hygiene | passed | `git diff --check main..HEAD`; clean worktree at subject |
| Exact release scope | passed | Structured release/backlog read-back: the eight expected IDs only; no local `*128*` backlog item |
| Specialized release workflow | passed | `release-publication` locator and `REL090-001` specialized task with correct exclusions |
| Rewritten archives and sidecars | passed | Two identical ZIP/tar pairs at the current SHA-256 values above |
| Archive integrity | passed | `validate-ai-context-package.py` passed for both ZIP/tar pairs |
| Rewrite payload/migration equivalence | passed | Equal `25ae566` / `d3236e6` tree, 652 payload paths, and equal metadata digests |
| Clean install and v0.8.0 upgrade | passed by bounded equivalence | Equal-tree fixture evidence; 649/360 applied, one acknowledged reconciliation in each case, 0 missing, 0 SHA mismatch |
| Critical gate | passed by identical-tree evidence | 49/49, 951 seconds; `cc832b4` tree equals rewritten `bb16471` tree |
| Filemode regression | passed | `AiContextPackageApplyGwtTests.test_gwt_012a...`: 1 test in 1.031 seconds |
| Release state tests | passed | 24 tests in 0.499 seconds |
| Backlog release contract tests | passed | 6 tests |
| Release-notes renderer tests | passed | 8 tests |
| Candidate-phase validator before transition | expected precondition | exit 1 solely because the record is still `planned`; not counted as a failed candidate gate |
| Local tag | absent as required | no local `refs/tags/v0.9.0` |

## Skipped Or Deferred Validation

- A duplicate clean-install and upgrade execution after the commit-message-only
  rewrite was not run under the explicit owner waiver. Its exact boundary and
  independently checked equivalence are recorded above.
- The full 49-check critical gate was not repeated after the message-only
  rewrite because its post-filemode execution tree equals the rewritten
  evidence tree and subsequent changes are documentation/evidence only.
- Hosted pull-request checks, merged-main validation, GitHub Project read-back,
  owner-created tag, hosted publication, and terminal release finalization are
  future lifecycle gates, not local candidate passes.

## Recommended Action Order

1. `ai-context-governance` records this assessment and advances the v0.9.0
   source-local record from `planned` to `validated`, updating the candidate
   evidence summary consistently.
2. Run the sanctioned candidate-phase validator on that validated record.
3. Commit, push, open a ready pull request, and require its hosted checks;
   merge only through the repository's pull-request policy.
4. From a continuation branch at current `main`, run the sanctioned pre-tag
   validation and stop before tag mutation.
5. The repository owner creates the immutable tag. Only then may hosted
   publication and final provider/Project read-back proceed.

## Residual Risk

- The owner-approved fixture-equivalence waiver reduces duplicated execution
  but leaves the normal environmental diversity of a fresh post-rewrite run
  unobserved. The identical tree and metadata make this bounded and explicit,
  not invisible.
- WSL runtime prerequisites were intentionally not tested. This says nothing
  about whether WSL has Python or .NET installed.
- No hosted state was queried in this assessment; hosted checks, tag, release,
  and Project publication fields must be independently read back in their own
  authorized lifecycle stages.

## Lifecycle Handoff

- Assessment path: `.dev/assessments/ASM-20260805-004/report.md`
- Stable finding references: none.
- Remediation owner: not applicable; no active remediation is authorized by
  this assessment.
- Release-transition owner: `ai-context-governance`.
- Related workflow: `2026-08-05-v0-9-0-release-publication`.
- This assessment authorizes neither a merge, tag, publication, nor a local
  #128 backlog record.
