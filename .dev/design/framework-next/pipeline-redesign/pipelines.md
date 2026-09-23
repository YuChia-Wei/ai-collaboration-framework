# Pipeline disposition and execution design

Every path and command below is a **future proposal**, except explicitly described
existing legacy commands. No YAML implementation, dispatch or execution occurs here.

## Seven legacy workflows

All seven were read at source `171f33474f88888fbe853600de04bfe9c5716b25`;
all are live-disabled. Preserve their disabled files during the first dormant
implementation. Later removal of retired files can be a small source cleanup after
successor admission; it never deletes Git history, version records or support code.

| ID / existing file under .github/workflows | Disposition and concrete successor or retained duty |
| --- | --- |
| 316930531 / governance.yml | **Replace ordinary invocation** with `source-checks.yml` / `Source change gate`. Its global `check-all.sh --profile fast` is not the new route. Retain old runner for selected legacy support only. |
| 316885236 / portable-gates.yml | **Replace ordinary invocation** with the same source gate and `source-native.yml` for specifically selected native cases. Retire automatic Ubuntu/Windows prerequisite pair and `--profile pr`; new entrypoints get their own actual producer/reader checks, not every old entrypoint suite. |
| 334993163 / nightly-full-readiness.yml | **Retire from the prospective pipeline set**, with no scheduled successor. The existing nightly-full job is already `if: false`; its schedule is not evidence of execution. Keep full legacy profile available only to a specifically authorized legacy investigation/release. |
| 313373704 / package-candidate.yml | **Replace general PR responsibility** with affected distribution checks in the source gate; **preserve legacy-only candidate qualification**. Before any separate enablement, change this file to dispatch-only, retaining exact version/source inputs, `Build and validate candidate`, permissions and required version-specific commands. No automatic legacy archive extraction or origin matrix for ordinary skills/docs. |
| 313373707 / publish-release.yml | **Retain, disabled and source-release-only**, including annotated `v*` tag trigger, admitted exact bytes, draft ownership, public byte read-back and provider reconciliation. No replacement release engine is designed here. A new-format release needs its own approved contract before this workflow can consume it. |
| 363100663 / release-provider-preflight.yml | **Retain, disabled and legacy release/provider-only**. Main-only dispatch, exact version and preflight/verify choice; preserve `Read-only release provider check`, environment and existing credential reference. #309 must establish actual hosted capability; local REST success is insufficient. |
| 341690089 / test-fixture-acceleration.yml | **Retire from the prospective pipeline set**, no self-hosted benchmark successor. Preserve script/history and #274/#275 evaluation obligations. Any later benchmark is separately selected, comparable and explicitly rooted; no required RAM disk or three-run benchmark on every change. |

Existing release specifics stay scoped: v0.15.1 clean install / v0.15.0 upgrade,
v0.16.0 direct origins, and v0.17.0 retained seven-plus-two evidence are not generic
new product tests. v0.18.0's own admitted assets, source gates and failed hosted
history remain version-owned. No matrix is moved wholesale to manual or nightly
as a purported cost reduction: selecting a legacy command requires a named version,
incident or active recovery operation and the smallest relevant case set. If its
existing acceptance truly requires a full matrix, report that cost and obtain that
work's execution authority; do not weaken acceptance.

## Exact proposed future files and hosted contexts

| File / jobs | Events / identity | Permissions, concurrency and bounds |
| --- | --- | --- |
| `.github/workflows/source-checks.yml`, workflow `Source checks`, job ID `source-change`, job name/context **Source change gate** | `pull_request` to main, types opened/synchronize/reopened/edited/ready_for_review; no paths filter, no draft skip, no tag/push/schedule/dispatch. Check out exact event head; use exact event base for diff. | Workflow `permissions: {}`; job `contents: read`; no secrets/environment, `persist-credentials: false`. Group `source-pr-${{ github.event.pull_request.number }}`, cancel-in-progress true. Ubuntu, Python 3.12, 10-minute initial limit, no OS matrix. |
| `.github/scripts/check-source-change.py` | Small source-only diff selector/runner and readable summary. Proposed interface `python .github/scripts/check-source-change.py --base BASE_SHA --head HEAD_SHA`. Full 40-character event SHAs supplied via environment, not shell interpolation of PR prose. | No provider writes, credential reads, product installation or implicit storage discovery. Uses #364's reconciled exact commands; no new persistent schema/registry/receipt service. |
| `.github/workflows/source-native.yml`, workflow `Source native checks`, job ID `native`, context **Source native trial** | `workflow_dispatch` only on main workflow revision. Required inputs: `subject_sha` (full source SHA), `case` (installation-paths or managed-recovery), `platform` (ubuntu or windows). Pin both runner revision and checked-out subject. | `permissions: {}`; job `contents: read`; no secrets, environment or self-hosted runner. Group `source-native-${{ inputs.subject_sha }}-${{ inputs.case }}-${{ inputs.platform }}`, cancel false; one selected hosted OS, 15-minute initial limit. |
| `.github/scripts/run-source-native.py` | Proposed interface `python .github/scripts/run-source-native.py --subject SUBJECT_SHA --case CASE --scratch-root SCRATCH --recovery-root RECOVERY`. Cases and exact argv await #364 binding. | Explicit preflighted fresh roots, fail on unknown case/backend; no full repository copies/history matrix. Trusted main runner selects cases; no arbitrary input command. |

Action versions may begin with the repository's existing checkout/setup-python v6
and upload-artifact v7 only after dependency compatibility is checked in the later
implementation. Pin immutable action revisions if the owner adopts that setting;
this design does not silently turn SHA-pinning enforcement on. Install only the
dependencies required by reconciled #364 commands; legacy `requirements.txt` is
not an assumed new product environment contract.

Checkout only necessary head/base trees; do not fetch all history by default.
Validate fetched identities and treat unavailable base, unsafe paths or incomplete
diff as unknown impact. Keep the single source job unconditional. Write its
summary even on failure; never use `continue-on-error`, `|| true` or skipped
selected steps to turn failure green. No aggregate dependent job can mask a failed
child. Upload bounded diagnostics on failure, 14-day retention, without copying
worktrees or private records. A rerun preserves run/attempt identity.

## Check selection and #364 reconciliation

This is a finite decision table for one script, not a new cross-product registry.
For additions/deletions/renames, examine both old and new paths and their owners
in both pinned trees. Use current metadata/manifest membership for selected package
closures; directories alone do not prove an instruction-only change.

| Changed ownership | Selected purpose and explicit command status |
| --- | --- |
| Ordinary Markdown, examples, design/Issue-workflow prose, instruction-only SKILL/reference files | UTF-8, changed local references, conflict markers, whitespace; compare explicit constraints/owner meaning in review. Known Git command: `git diff --check BASE_SHA HEAD_SHA`. #364 binds lightweight content checks. No product import, schema validator, build, fake behavior test or all-record scan solely for prose. |
| A structured record/schema/template or its writer/reader | Direct syntax plus only the selected schema and actual producer/consumer/negative-boundary cases. JSON parsing alone is not schema or behavioral evidence. #364 owns exact argv/cases; no schema forced onto instruction packages. |
| Script, shared support or CLI behavior | Focused tests of changed behavior and direct callers; shared dependencies select all affected package consumers, not unrelated legacy suites. #364 binds argv and failure cases, including missing prereqs only for changed entries. |
| Package metadata, profile, manifest, adapter or assembly ownership | Selection/member/destination integrity and affected profile/package tiny build/reader cases. Adapter/shared distribution changes expand across affected declared selections; do not assume one Lesson build covers 18 packages. #364 binds exact cases/commands and fixture limits. |
| Native maintenance/coordination/path/recovery implementation, engine closure or byte-affecting installed/root binding | Portable logical boundaries in source gate plus specifically selected manual native cases on affected platforms. #364/#361 bind real engine, subject and pilot/recovery inputs. Source gate reports `native-trial-required`; it does not claim native success. |
| .github, source policies/root entries, selector, test/dependency configuration | Content/syntax, focused selector/workflow event-and-outcome contracts and consistency of exact context names/permissions; independent scoped review for authority/security changes. #364 binds executable checks. Root bilingual rules must retain normative parity. |
| Legacy release/package/recovery code or preserved records | Select named legacy owner and version/incident. Known phase entry: `python .ai/scripts/validate-ai-context-release-state.py --phase candidate --version VERSION`, only if selected version's phase contract requires it. Other exact argv come from that version's `release-phase-checks.yaml` or approved recovery plan. No new source blanket aggregate. |
| Unknown path/ownership, missing command binding or transitive dependency uncertainty | Fail with the narrow unresolved paths/purpose and next owner. Coordinator resolves mapping and reruns affected checks. Do not default to no-op success or an all-history/full matrix. |

A mixed diff selects the union of genuinely affected purposes. A known unneeded
purpose is `not-applicable` with the path/owner reason; no job is manufactured for
it. A selected failed/cancelled/timed-out/skipped/deferred/missing command is
non-passing. Required context absence is a blocker, including skip annotations,
merge conflicts or disabled workflows. Resolve the trigger/event and rerun; do not
fabricate a context. After final adoption, a newer head requires its own source run.

Native/manual runs are an additional, conditional maintainer admission check:
the portable source context may succeed while a required native trial remains
outstanding. Its summary and PR must make that distinction explicit. Integrator
checks the real run URL, actual subject SHA, runner revision, case/platform, command,
exit/outcome and limitation; a manually dispatched job is never substituted for the
PR context. A deferred native requirement permits only an explicitly authorized
checkpoint with open work, not a terminal readiness/support claim.

GitHub documents [pending path-filtered checks, skipped jobs and dispatch limits](https://docs.github.com/en/pull-requests/how-tos/merge-and-close-pull-requests/troubleshooting-required-status-checks).
The source policy deliberately requires actual `success`, despite GitHub allowing
some skipped/neutral statuses. Grant only [necessary job token permissions](https://docs.github.com/en/actions/tutorials/authenticate-with-github_token).

## Storage and execution limits

Future local disposable runs may use
`F:/framework-next/p7-runs/<issue>-<unique-run>/`; do not touch
`F:/ai-context-tests`. Persistent managed recovery/backup may use distinct ignored
roots under the selected persistent repository's
`.dev/ai-context/local/p7-recovery/<run>/` and `p7-project-backups/<run>/`.
Those are proposed inputs, not created or preflighted by this design. An F: checkout's
relative ignored directory is still volatile; the actual recovery absolute path must
resolve on persistent storage. Managed bytes and project records need separate backups.

Hosted scratch/recovery roots must also be separate within the disposable runner.
Such a run proves only its selected process/filesystem failure domain; an ephemeral
runner cannot establish cross-machine or power-loss recovery. Zero-configuration
local checks use a fresh contained OS temporary directory, never discover RAM drives
or rewrite TEMP/TMP. Record actual logical bytes/files/process counts where #364
can measure them cheaply; make no SSD wear, speed or token-saving claim.