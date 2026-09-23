# Dormant source gates: local checkpoint

[#369](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/369), program
#322 / [selected P7 scope](../p7-execution-selection.md). **Partial; directly
authorized dormant policy delivered, contracts/public CLI bound; actual product
acceptance and native implementation outstanding. No adoption or restoration claim.**
Read the [current dormant-policy handoff](../../../workflows/2026-09-23-source-gates-implementation/reports/dormant-policy-handoff.md)
and [initial handoff](../../../workflows/2026-09-23-source-gates-implementation/reports/blocked-handoff.md)
and [contracts binding](../../../workflows/2026-09-23-source-gates-implementation/reports/runner-binding-handoff.md),
and [current public binding](../../../workflows/2026-09-23-source-gates-implementation/reports/public-binding-handoff.md).

## Delivered selector contract

```text
python -I -B .github/scripts/check-source-change.py --base FULL_BASE_SHA --head FULL_HEAD_SHA
python -I -B .github/tests/test_source_gates.py --output-root EXPLICIT_DISPOSABLE_PARENT
python -I -B .github/scripts/run-source-native.py --subject FULL_SUBJECT_SHA
```

The selector requires the current checkout to equal the full pinned head, reads
regular blobs from both commits, uses a NUL-delimited rename-aware finite diff,
checks both sides of changes and rejects unknown ownership. It never imports
product code to discover ownership or runs a legacy aggregate as fallback.
Each changed blob is bounded to 1 MiB, the diff to 256 entries, captured subprocess
output to 64 KiB (Git blob reads to 1 MiB) and each selected command to 120 seconds.
The future hosted source job has a 10-minute limit; native has 15 minutes.

| Ownership/purpose | Actual selected binding in this checkpoint |
| --- | --- |
| Known source prose / declared package entry or reference | UTF-8/conflict checks, new/changed Markdown local file references, `git diff --check BASE HEAD`. File existence only; heading/semantic meaning remains review. Renames re-resolve unchanged relative links. |
| Source selector/workflows/policies/root | `.github/tests/test_source_gates.py --json`; nonzero, absent, timed-out, failed, skipped or malformed result fails. Report review requirement separately. |
| Package schema/template/tool/metadata | `contracts` binds #368 and the owning `public:<family>` binds fixed #373; actual product acceptance is still incomplete and must fail truthfully. |
| Shared distribution/profile/adapter | `contracts` and actual declared tool-family consumers; only declared members/profiles/adapters are recognized. Nonempty/unknown dependency impact fails for coordinator mapping. Separate affected-selection trials remain required; C1/C5 Lesson smoke is not blanket actual assembly coverage. |
| Installation/maintenance | `contracts`, separate Windows native requirement and independent scoped review. No native command is launched by source gate. |
| Legacy support/recovery, frozen backlog or unknown member | Narrow failure requiring its named owner/check selection, never a green placeholder or historical matrix. |

Source context: **Source change gate**. One unconditional job for PRs to main,
opened/synchronize/reopened/edited/ready_for_review; no draft or paths skip. Exact
event head checkout and full event base shallow fetch; `permissions: {}` globally,
job `contents: read`, no environment/secrets, no persisted checkout credentials.
The dormant workflow explicitly declares PyYAML >=6,<7, jsonschema >=4.18,<5
and referencing, matching #368's inspected runtime checks. No local dependency
installation occurred. Missing selected runner files/dependencies remain failures. Bounded diagnostics stay in the run
log and an always-run step records outcomes/identities. No artifact upload or
worktree copying is introduced.

Official pins verified by read-only GitHub API at their exact revisions:
`actions/checkout@d23441a48e516b6c34aea4fa41551a30e30af803` and
`actions/setup-python@ece7cb06caefa5fff74198d8649806c4678c61a1`, both v6/node24.
Source workflow uses hosted Ubuntu/Python 3.12; selected native route is Windows
only. These definitions are not hosted execution/compatibility evidence.

## Native continuation

**Source native trial** is workflow_dispatch on the main workflow revision only.
Its `subject_sha` is validated before use. The runner checkout uses `github.sha`;
the subject is not fetched while no actual V3 binding exists. The current script
returns blocked/exit 1 and explicitly reports `native_executed:false`.

Coordinator must supply the fixed V3 native-windows command, delivered cases,
explicit separate native/recovery roots, subject/runner verification, output and
process-termination result contract. Add and exercise that actual binding before
proposing enablement. Do not invent illustrative installation-paths/managed-recovery
cases or a Linux native route. No installation, power-loss or physical-media
claim follows from synthetic tests.

## Seven old workflow dispositions

All seven files remain byte-identical to starting HEAD; observed provider states
were all `disabled_manually` with repository Actions disabled. Dispositions below
are retained prospective decisions, **not settings changes**.

| Existing ID / file | Prospective disposition and owner |
| --- | --- |
| 316930531 / governance.yml | Replace ordinary invocation with `source-checks.yml` / Source change gate; retain old runner only for explicitly selected legacy support. |
| 316885236 / portable-gates.yml | Replace ordinary prerequisite/PR matrix with affected source checks plus selected Windows manual native trial. No automatic OS pair. |
| 334993163 / nightly-full-readiness.yml | Retire from proposed restoration set; no scheduled/full-matrix successor. Preserve historical/selected legacy investigation commands. |
| 313373704 / package-candidate.yml | Replace ordinary PR role with affected distribution checks; preserve disabled legacy-only candidate duty. Dispatch-only conversion requires later scoped work before separate enablement. |
| 313373707 / publish-release.yml | Retain disabled, source-release-only exact admitted-byte/publication duties; no new-format release engine or enablement. |
| 363100663 / release-provider-preflight.yml | Retain disabled, legacy release/provider-only. #309 owns unresolved hosted capability; no credential change or claim from local REST. |
| 341690089 / test-fixture-acceleration.yml | Retire from proposed set without a self-hosted/nightly replacement. Preserve #274/#275 history and separately selected measurement obligations. |

The precise mandatory-gate replacements are now recorded in the
[dormant canonical source policy](../../../standards/SOURCE-DEVELOPMENT-POLICY.md),
following the selected [#365 source-rule table](../pipeline-redesign/source-rules.md).
Direct user confirmation resolved the earlier policy-write authorization block.
Only prospective text and applicability pointers were added: five legacy contexts,
audit receipt/declaration machinery, aggregate validators, handoff/lease/acceptance
requirements and effective-rule YAML retain their existing fields and applicable
U001 deferrals. Both roots retain their effective text and routes, and the PR form
has only a dormant preview comment. No hybrid schema or active replacement exists.

## Verification and adoption boundaries

The second focused test run passed 24/24 with no skips in 1.733 s after an explicitly
permitted fixture-only repair. The first failed run (F: strict final-path resolution,
WinError 1) is retained. Tiny two-commit real Git fixture: rename/deletion identity,
selection and whitespace; synthetic responses cover non-passing commands/events.
Selector ownership read-back recognized all 113 declared members at starting HEAD.
This is no product/public/native/hosted acceptance or independent review.

One small per-run child under the exact supplied disposable parent is preflighted
using absolute lexical paths and no-reparse directory ancestry. Cleanup removes
only that created child; the parent remains. No global TEMP/TMP or legacy fixture
setting is changed. This fixture behavior is not product filesystem validation.

Dormant policy writing is directly authorized and complete. Coordinator still owns
#368/#373 integration and failed product acceptance, V3 binding, first push/PR/merge,
scoped review, actual selected trials, root adoption and the user's exact policy
adoption/restoration decision. Keep #369 open; keep all
seven old workflows disabled. Legacy matrices/packet machinery and CI remain
`deferred-by-owner` under U001 until selected P7 adoption, never passed.

## Historical #368-only binding follow-up

Runner interface source: `070a47335ffce99d31bd83e487447942539e4a9f`.
`contracts` selects `python -I -B tests/framework_next/run.py --layer contracts`.
Exit 0 plus the real unittest summary/runtime/cleanup observations is required;
there is no invented success JSON. Nonzero, skipped, malformed, absent or retained
cleanup output fails. Seven public family names are known but reserved/non-passing;
native is unchanged and blocked. The upstream runner is not copied into this worktree.

The updated source tests passed 28/28, no skips, harness 2.441 s. New command/result
responses are explicitly synthetic and do not execute product code. Upstream's
retained actual result remains 14 methods / 11 successful / 3 affected with 7
errors, **zero successful candidate builds**. These failures and the original
#369 failure/24-pass checkpoint remain visible. See the current handoff above
for exact interfaces, scope and remaining owners. CI remains disabled.

## Current fixed #373 public binding

Interface: `7996b32d3d4f70553b203299e25dc69d9413ff9d`.
The seven public families now select `--layer public --family ID`; no read-only
mode or aggregate is used. Their separate JSONL/stdout and unittest/stderr must
agree with the requested family and pinned subject, complete declared phases,
zero skips, actual process exit/outcome and cleanup/accounting. Calls are checked
only for basic structure/count; original tests retain operation semantics.

Final source-only tests passed 37/37, no skips, harness 1.541 s. Complete success
responses are synthetic because no #373 family fully passed. The seven phase
lists matched fixed source; retained ADR partial and PR failed output were
correctly rejected. No product/public/native command ran. See the current public
handoff above. Native and all reported #368/#373 product/backend failures remain
unresolved. The later direct authorization permits dormant policy writes only;
policy adoption and CI restoration remain outstanding. No provider setting changed.

## Dormant policy follow-up

The direct owner confirmation is retained in the current handoff. Sixteen policy,
root and template files now carry the dormant rules/pointers; all 15 existing
bodies were preserved, and both parsed YAML values matched with exact types.
Fifteen added local links, UTF-8/newlines/whitespace and the additive diff passed
direct checks. English/Traditional Chinese additions have matching meaning.
Source code, tests, workflows and commit-policy YAML are unchanged in this follow-up.
The earlier source tests are historical evidence, not newly executed policy tests.
