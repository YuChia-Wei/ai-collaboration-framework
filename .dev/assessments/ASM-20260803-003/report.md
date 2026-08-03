# v0.8.0 Release Workflow Time And Context-Cost Incident Assessment

## Template Metadata

- `template_id`: `ai-context-auditor-report`
- `template_version`: `2.1.0`
- `template_created_at`: `2026-07-10T18:22:49+08:00`
- `template_updated_at`: `2026-07-15T08:39:00+08:00`

## Metadata

- `assessment_id`: `ASM-20260803-003`
- `assessment_type`: `ai-context-audit`
- `owner_skill`: `ai-context-auditor`
- `status`: `final`
- `audit_date`: `2026-08-03`
- `created_at`: `2026-08-03T19:46:19+08:00`
- `updated_at`: `2026-08-04T01:09:50+08:00`
- `template_source`: `.ai/assets/skills/ai-context-auditor/templates/ai-context-audit-report-template.md`
- `template_version`: `2.1.0`
- `repository`: `C:/Github/YuChia/ai-collaboration-prompts-dotnet-backend`
- `subject_branch`: `main`
- `subject_commit`: `2d7917c43452668bb129ae14392781c13c9040fd`
- `previous_assessment`: [`ASM-20260803-002`](../ASM-20260803-002/report.md)
- `workflow_refs`: [`2026-08-03-v0-8-0-release-publication`](../../workflows/2026-08-03-v0-8-0-release-publication/workflow.yaml), [`2026-07-29-v0-7-0-public-release-body-correction`](../../workflows/2026-07-29-v0-7-0-public-release-body-correction/workflow.yaml)
- `backlog_ref`: [`REL-004`](../../backlog/items/REL-004.yaml)
- `machine_readable_evidence`: [`incident-record.json`](evidence/incident-record.json), [`session-019fc7dc-observation.json`](evidence/session-019fc7dc-observation.json)

## Executive Summary

- Overall assessment: **the release result is strongly governed and correctly
  evidenced, but the execution path is not cost-governed or sufficiently
  observable**.
- Overall score: **5.5/10**
- Decision: **remediation-recommended**
- Primary strengths: exact immutable Release/tag/asset boundaries, fail-closed
  result classification, deterministic package evidence, PR-only integration,
  and a pre-existing open backlog item that already recognizes source-only
  closeout as a distinct problem.
- Primary risks: hours of wall time cannot be attributed to active work,
  waiting, tool queueing, approval, or sleep; broad context and repeated
  validation are manually reinterpreted; and an equivalently broad route could
  impose avoidable token and time costs if exported to downstream adopters.

The direct GitHub Release body edit was not a five-hour operation. Current-task
tool timing observed the command at 1.8 seconds and its immediate read-backs at
seconds-scale; these timings were not persisted before this assessment and are
therefore classified as conversation observations, not independently
reproducible repository facts.
The incident is the surrounding orchestration: a 10:47:46 end-to-end release
workflow, a 5:42:29 unattributed post-publication interval before the published
source checkpoint merged, repeated broad gates, Windows runtime retries,
provider reconciliation, three PR boundaries, and no hook capable of separating
active execution from waiting or machine sleep.

The evidence does **not** support claiming that the model actively computed for
five hours or that all elapsed time was waste. It also cannot prove how many
tokens were wasted because no token telemetry was captured. That inability to
answer the owner's accountability question is itself the highest-severity
finding.

## Scope

### Included AI Context Surfaces

- The complete v0.8.0 release-publication workflow, release record, finalization
  report, and immutable hosted evidence.
- PR #81, #82, and #83 metadata and synchronized Git commit facts.
- Open backlog item `REL-004`, its discussion attachment, and its GitHub Issue
  #57 projection.
- Root routing, workflow, Git, governance-skill, and release-runbook context
  that a closeout executor can be routed through.
- Current-task command timings when explicitly labeled as conversation
  observations rather than repository facts.

### Default Exclusions

- `src/**`
- `tests/**`, `test/**` except already-recorded AI-context validation outcomes
- product implementation trees
- generated and dependency trees

### Additional Exclusions

- Raw prompts, conversation bodies, secrets, credentials, and private machine
  telemetry.
- Remediation changes to context, scripts, hooks, skills, provider state, or
  release records.
- Reinterpretation of owner-controlled tag timing as model delay.

### Code Review Handoff

- Requested: `no`
- Paths not scanned: product implementation and product tests
- Recommended skill: not applicable

## Methodology And Evidence

### Pass A: Independent Baseline

- Reconstructed the incident only from persisted timestamps, Git commit facts,
  and current read-only GitHub metadata.
- Classified every value as repository record, Git fact, GitHub read-back,
  current-conversation observation, or derived interval.
- Refused to convert wall-clock gaps into active-execution or token claims.
- Compared the seconds-scale body mutation with the broader workflow route and
  explicitly recorded aggregate-gate durations.

### Pass B: Repository-Aware Skill Review

- Applied assessment, workflow, Git, AI-context governance, release, and
  package-isolation boundaries.
- Compared the incident with `REL-004`, the v0.7.0 body-correction precedent,
  and the source release runbook.
- Evaluated a low-freedom source-only closeout skill without treating the
  assessment as design or implementation authorization.
- Measured a plausible closeout routing corpus by bytes, lines, and
  whitespace-delimited chunks; this is not represented as actual model tokens.

### Delegation

- Sub-agents used: `yes`, three low-cost read-only explorers.
- Assigned surfaces: incident timeline and attribution gaps; assessment schema
  and lifecycle compliance; `REL-004` skill, package-isolation, and context-cost
  options.
- Duplication control: each explorer received disjoint named files and no write
  authority; the primary agent reconciled the final evidence.

### Discovery Accelerators

| Tool / generated view | Source revision or input digest | Freshness / dirty state | Scope and exclusions | Unsupported relationships | File-backed fallback |
| --- | --- | --- | --- | --- | --- |
| GitHub connector PR and Issue read-back | PRs #81-#83; Issue #57 | live read-only capture on 2026-08-03; local assessment branch initially clean | metadata and lifecycle only; no mutation | cannot reconstruct Codex active/wait/token timing | persisted workflow evidence and local Git objects |
| PowerShell context-corpus inventory | `main@2d7917c43452668bb129ae14392781c13c9040fd` | clean subject revision | 14 specifically selected routing and closeout files | does not prove which files entered the model context | exact path list in `incident-record.json` categories and command appendix |

## Repository Context Inventory

| Surface | Files / Size | Audience | Scope | State | Notes |
| --- | ---: | --- | --- | --- | --- |
| Root, workflow, and Git rules | 5 files / 1,036 lines | agents and maintainers | routing, lifecycle, branch, commit, merge | healthy but broad | repeatedly relevant to governed execution |
| Governance skill route | 6 files / 352 lines | agents | wrapper, canonical contract, four references | healthy but not closeout-specific | requires interpretation before the narrow operation |
| Release runbook | 1 file / 157 lines | agents and maintainers | candidate through finalization | healthy | spans more phases than body-only closeout |
| `REL-004` item and plan | 2 files / 218 lines | owner and future implementer | source-only closeout decision | open / unassigned | already anticipates runtime, isolation, and effort risks |
| Potential closeout route corpus | 14 files / 1,763 lines / 89,633 UTF-8 bytes / 11,558 whitespace chunks | agents | plausible required or rediscovered context | unbudgeted | not a token measurement and not proof all content was loaded |
| v0.8.0 workflow evidence | locator, task, report, 6 evidence files | maintainers and agents | release outcome and invariants | completed | outcome-rich but execution-timing-poor |

## Incident Timeline

| Milestone | Timestamp (+08:00) | Direct source | Interval from prior selected milestone | Interpretation limit |
| --- | --- | --- | ---: | --- |
| Workflow created | `2026-08-03 08:33:26` | workflow locator | — | start of durable workflow, not first model token |
| PR #81 created | `10:16:16` | GitHub read-back | `1:42:50` | mixed candidate work and validation |
| PR #81 merged | `10:18:39` | GitHub + commit `97ccc9e9` | `0:02:23` | hosted PR elapsed, not all active local work |
| Owner-created tag | `13:12:55` | hosted evidence | `2:54:16` | owner-controlled handoff; active/wait split unknown |
| Release published | `13:13:55` | hosted evidence | `0:01:00` | hosted publication |
| Publication evidence observed | `13:38:00` | validation evidence | `0:24:05` | observation time, not validation duration |
| PR #82 created | `18:54:02` | GitHub read-back | `5:16:02` | large unattributed wall gap |
| PR #82 merged | `18:56:24` | GitHub + commit `5ad3f60` | `0:02:22` | source-registry integration |
| Body/provider exact read-back | `19:04:13` | hosted evidence | `0:07:49` | includes render, mutation, read-back, and provider updates |
| Closure commit | `19:17:49` | Git commit `7916fa7` | `0:13:36` | artifact update and validation; split unknown |
| PR #83 merged | `19:21:12` | GitHub + commit `2d7917c` | `0:03:23` | terminal integration |

End-to-end wall time from durable workflow creation through terminal main merge
was **10:47:46**. The most important unattributed interval was **5:42:29**
from hosted publication to PR #82 merge. Existing records do not establish how
much of that interval was active reasoning, tool execution, user wait, task
pause, or machine sleep.

The workflow and release `updated_at` value is `19:05:12`, sixteen minutes
before terminal merge. It therefore records a local artifact update and cannot
be used as the end-to-end completion timestamp.

## Cost Attribution

### Repository-Recorded And Current-Task Observed Operations

| Operation | Elapsed | Outcome | Assessment |
| --- | ---: | --- | --- |
| First aggregate critical gate through unintended WSL launcher | `573.5s` | `blocked-by-environment` | nearly ten minutes spent before the runtime mismatch failed at .NET commands |
| Authoritative candidate critical gate through Git for Windows Bash | `438.6s` | passed | required recovery, but reran the broad gate |
| Source-checkpoint Git Bash quick gate | `483.4s` | passed | another broad eight-minute validation before closeout |
| Hosted publication run | `43s` | passed | normal hosted release work |
| Release body edit | `1.8s` | passed | current-task observation, not independently reproducible; requires future hook persistence |
| Immediate Release read-backs | `2.6s`, `2.4s` | passed | current-task observations, not independently reproducible |
| Hosted finalization validator | about `2.4s` | passed | current-task observation, not independently reproducible |

The three recorded local aggregate executions alone consumed **1,495.5
seconds (24:55.5)**, including the environment-blocked attempt. This is a
material and explainable cost, but it still explains only a minority of the
10:47:46 wall time. The remaining attribution is unavailable.

### Currently Unmeasured

- Input, cached-input, reasoning, and output tokens per turn and sub-agent.
- Which context files were loaded and their individual token contribution.
- Tool process time versus queue or orchestration wait.
- Approval wait, user handoff wait, and host sleep/resume intervals.
- Duplicate validation keyed by an identical input fingerprint.
- Silent no-output periods and whether an executor was running, blocked, idle,
  disconnected, or asleep.

No token total or five-hour active-runtime claim is inferred.

## Strengths

1. The Release body correction preserved the Release identity, annotated tag,
   peeled commit, timestamps, publication run, and all four asset tuples.
2. Exact rendered/live body equality was proven by SHA-256 and immediate
   read-back.
3. Blocked and skipped validations were not relabeled as passed.
4. Main integration remained PR-only, and shared history was not rewritten
   after a commit-policy error.
5. `REL-004` already separates a repository-only closeout capability from the
   portable product and demands negative package-leakage tests.
6. The repository has enough durable outcome evidence to reproduce release
   correctness; the missing layer is execution-efficiency evidence.

## Findings

| ID | Severity | Finding | Evidence | Impact | Recommendation | Owner / Next Skill |
| --- | --- | --- | --- | --- | --- | --- |
| AIC-001 | HIGH | There is no end-to-end execution telemetry or budget. | The 5:42:29 post-publication gap and 10:47:46 workflow can be reconstructed, but token use, active/wait time, tool queueing, sleep/resume, and no-output periods cannot. | Owners cannot distinguish necessary rigor from executor waste or diagnose a sleeping/stalled task. | Add privacy-preserving hook events, active/wait classification, stage budgets, heartbeat/no-output limits, and checkpoint/resume records before benchmarking optimizations. | `ai-context-governance`; future observability owner |
| AIC-002 | HIGH | A seconds-scale body mutation is embedded in a broad manually interpreted closeout route. | The plausible route is 14 files, 1,763 lines, and 89,633 bytes across root, workflow, Git, governance, runbook, and backlog context; the final operation also reconciled registry, provider, roadmap, task, workflow, and two post-tag PRs. | Context and reasoning cost scale with policy surface instead of the allowed mutation. An equivalent exported route would risk imposing the same interpretation tax downstream. | Define a deterministic source-only closeout manifest and minimal progressive-disclosure context profile with exact source mutation boundaries; keep hosted body correction separately authorized. | `ai-context-governance` under `REL-004` |
| AIC-003 | HIGH | Validation is fail-closed but not fingerprinted or reuse-aware. | A blocked 573.5s broad gate was followed by a 438.6s broad gate and a later 483.4s quick gate; terminal validators were also repeated after unchanged facts. | Correctness is preserved at avoidable time and token cost, and a runtime mismatch is discovered too late. | Preflight runtimes first; assign each validation tier an input fingerprint and run once per unchanged fingerprint, with a narrow terminal read-back after merge. | `ai-context-governance` plus release tooling |
| AIC-004 | MEDIUM | Sub-agent use has no declared token, time, overlap, or stopping budget. | The release used multiple independent audits and follow-up reconciliation, while durable records preserve results but not per-agent cost or duplicated context. | Delegation can multiply broad context loading and repeat already-proven checks. | Cap closeout delegation at two non-overlapping bounded audits by default, export per-agent usage, and require explicit overlap rationale. | orchestration/context governance |
| AIC-005 | MEDIUM | Windows runtime, temporary-directory, and power/resume preflight is incomplete. | Bare `bash` selected WSL and failed after 573.5s; system Temp ACL attempts failed before workspace-scoped Temp/TMP succeeded; the task later survived machine sleep without a durable resume event. | Failures arrive after expensive work, and a resumed task cannot know which evidence remains reusable. | Preflight shell, Python/uv, .NET, writable temp root, credentials, network, and expected wall duration before writes; checkpoint before long waits and record sleep/resume. | source-only closeout tooling under `REL-004` |
| AIC-006 | MEDIUM | Commit-policy validation occurred after a shared checkpoint was pushed. | The first continuation checkpoint omitted the required `|scope` segment; shared history was preserved by recreating the finalization branch and replaying reviewed content. | Safe recovery added branch, context, validation, and PR overhead. | Validate the intended commit subject/body before commit and before push; retain fix-forward behavior after sharing. | Git/release tooling |
| AIC-007 | HIGH | Source-only closeout isolation is recognized but not mechanically established. | `REL-004` is open/unassigned and warns that broad package profiles include canonical skill, script, and wrapper roots; placement alone would leak a new skill downstream. | A naive optimization could reduce local cost by shipping repository-specific machinery and references to every consumer. | If approved, use a dedicated source-only canonical root or exact exclusions plus negative ZIP/tar path, identifier, and broken-reference tests; portable governance must not route to the skill. | owner decision, then `ai-context-governance` |

## Baseline And Skill Comparison

### Confirmed

- Independent timeline reconstruction and repository-aware review agree that
  release correctness is high while execution attribution is inadequate.
- Both identify runtime preflight, narrow deterministic closeout, package
  isolation, and duplicate-validation control as necessary.
- Both keep `REL-004` open and treat this assessment as corroborating evidence,
  not implementation authorization.

### Added By Repository-Aware Review

- `REL-004` already contains runtime and forward-effort requirements, but it
  does not yet specify hook telemetry, stage budgets, no-output limits,
  validation fingerprints, or sleep/resume evidence.
- Portable improvements should be principles—progressive disclosure,
  budgeted orchestration, validation reuse, explicit wait states, and
  resume-safe checkpoints—not this repository's source-only closeout machinery.
- The package profile is broad enough that source-only placement requires
  proof; directory naming alone is insufficient.

### Downgraded Or Deferred

- The statement “the body correction ran for more than five hours” is
  downgraded to “more than five hours elapsed around the post-publication
  source checkpoint.” The mutation itself was seconds-scale, and active time
  within the gap is unmeasured.
- A hard token-reduction percentage is deferred until hooks produce a baseline
  across at least three comparable runs.

### Overturned

- None. The owner's observed wall-time and sleep impact are valid operational
  symptoms; only their attribution remains unmeasured.

## Skill Option Evaluation

| Option | Benefit | Cost / Risk | Assessment |
| --- | --- | --- | --- |
| Keep only the broad governance skill and runbook | no new skill identity | preserves repeated interpretation and context loading | not recommended as the sole response |
| Add only a deterministic source script | smallest runtime surface | weak discoverability and routing; still needs policy/context boundary | viable implementation core, insufficient entry contract |
| Add source-only `ai-context-release-closeout` as a thin low-freedom entry over a deterministic script and manifest | compact routing, exact scope, preflight, checkpoint/resume, reusable evidence | requires owner decisions and strict package isolation | **recommended for owner evaluation under REL-004** |
| Make closeout a portable framework skill | downstream discoverability | exports repository-specific release registry/provider assumptions | reject unless future evidence establishes a portable contract |

The recommended skill would trigger only after an owner-created immutable tag
and successful hosted publication. It would have zero runtime skill
dependencies and would consume file-backed contracts directly.

### Proposed Deterministic REL-004 Path

1. Preflight the exact shell, supported Python or `uv`, .NET if declared,
   workspace temp root, GitHub authentication, clean Git state, and base SHA.
2. Freeze Release ID, annotated tag object, peeled commit, timestamps, run, and
   asset ID/name/size/digest set.
3. Load one source-only manifest naming the allowed source input files, mutable
   repository paths, commands, validation tiers, and evidence outputs.
4. Verify the stable hosted Release, immutable tag/asset facts, and existing
   body digest. If the body needs correction, stop with a distinct
   `needs-owner-authorized-hosted-repair` outcome; REL-004 does not authorize or
   perform the hosted mutation.
5. Reconcile only the declared release, backlog, roadmap, and workflow source
   records.
6. Reconcile optional provider projection as a separately declared tier; do
   not make provider state an authorization source.
7. Generate one evidence bundle in an isolated temporary worktree, validate
   once per fingerprint, and apply only if base SHA and patch digest still
   match.
8. Validate the commit message before commit, push one continuation branch,
   open one ready PR, and after merge perform a narrow synchronized-main
   read-back. Shared history is fix-forward only.

A future automation that mutates a hosted Release body would require its own
explicit owner-approved scope or an approved expansion of `REL-004`; this
assessment does not place that behavior inside the proposed closeout skill.

## Context And Execution Reduction Proposal

| Area | Current cost pattern | Proposed boundary | Initial measurable gate |
| --- | --- | --- | --- |
| Routing | broad governance and repository policies rediscovered | an excluded source-only root entry or explicitly source-only registry routes post-publication administrative closeout directly to one source-only entry | zero broad governance/audit reference reads on the normal path |
| Context | plausible 89,633-byte route corpus | manifest summary plus progressive disclosure to phase-specific references | provisional closeout pack at or below 1,500 measured input tokens; recalibrate after 3–5 runs |
| Commands | runtime errors discovered inside long aggregate gates | one preflight resolver and at most six declared normal-path commands | runtime or temp failure before repository writes |
| Validation | broad gates repeated without reusable identity | fingerprint `{release_id, tag_object, peeled_commit, release_database_id, asset_digest_set, rendered_body_sha256, source_tree_sha}` | each validator at most once per unchanged fingerprint |
| Delegation | multiple audits without cost records | at most two disjoint read-only agents for exceptional ambiguity; normal path uses none | 100% per-agent duration/token capture when available |
| Time | no active/wall/no-output budget | stage and end-to-end budgets with approval/hosted queue classified separately | body-only active <=10 min; full local closeout <=20 min; no silent no-output interval >60s |
| Git | policy error found after push | pre-commit message validation and resume-safe checkpoint | zero preventable post-push commit-policy recovery |
| Distribution | broad roots can leak source-only assets | dedicated source-only root or exact exclusions plus reference-integrity checks | 100% negative assertions across ZIP and tar payloads |

These thresholds are proposals for the future owner decision, not current
policy. Token thresholds must be calibrated against hook data rather than
claimed as achieved now.

## Proposed Conversation Hook Evidence

The hook should write append-only, machine-readable events and avoid raw prompt
or secret capture by default. Minimum fields:

- conversation/task, workflow, assessment, release, turn, and event IDs;
- UTC and local timestamp, stage, event type, skill, model, and reasoning mode;
- repository, branch, HEAD, dirty-state digest, and checkpoint/PR/run IDs;
- context file identifiers and bytes; input, cached-input, reasoning, and output
  tokens when the client exposes them;
- tool/sub-agent name, start/end, process time, queue/wait time, exit status,
  output-byte count, and retry lineage;
- validation command, input fingerprint, outcome, cache reuse, and invalidation
  reason;
- external mutation target, exact allowlist, authorization source, and read-back;
- state transitions for active, awaiting-owner, awaiting-hosted-check,
  blocked-by-environment, paused, sleep, resume, disconnected, and completed;
- heartbeat/no-output events and the last durable checkpoint.

Retention should hash or path-identify context rather than copy its contents,
redact credentials and environment secrets, allow owner-configured retention,
and make unavailable provider metrics explicit `null` rather than estimated.

## Validation

| Check | Result | Evidence / Notes |
| --- | --- | --- |
| Git state | pass | assessment branch started from clean synchronized `main@2d7917c43452668bb129ae14392781c13c9040fd` |
| Registry and wrapper parity | not-applicable | audited but did not modify canonical skills, wrappers, registries, or distribution profiles |
| Path and reference checks | pass | all report and locator references resolve in the assessment subject |
| Schema / structured file parse | pass | locator YAML and `incident-record.json` parsed successfully |
| Assessment structural validator | pass | `.ai/scripts/validate-assessment-artifacts.py` |
| Repository context checks | pass | focused line/byte inventory and release/backlog evidence read-back completed |
| Remote lifecycle read-back | pass | PRs #81-#83 are merged; Issue #57 / REL-004 is open with zero pre-link comments |

### Skipped Validation

- Product source and tests were excluded by the audit boundary.
- The full repository critical gate was not repeated for an assessment-only
  documentation change; the release workflow already records its executions.
- Token totals, per-turn context inclusion, sleep/resume, and active/wait split
  were unavailable and are findings, not silently passed checks.
- No hosted Release, Issue lifecycle, Project field, backlog item, context, or
  skill mutation was performed by this assessment.

## Recommended Action Order

1. Merge this standalone assessment and add one reference-only comment to open
   Issue #57 / `REL-004`.
2. Instrument the proposed hook schema before optimizing so future changes have
   an active/wall/token baseline and regression evidence.
3. Obtain owner decisions required by `REL-004`: name, source-only placement,
   package isolation, Python/`uv` policy, temporary-worktree transaction,
   terminal boundary, and proposed budgets.
4. If authorized, open a dedicated `ai-context-governance` workflow and
   implement the deterministic script/manifest first, then the thin skill and
   routing through an excluded source-only root entry or explicitly source-only
   registry.
5. Add fingerprinted validation reuse, Windows preflight, commit-message
   preflight, heartbeat, and resume-safe checkpoints.
6. Prove zero leakage across every package component and run forward benchmarks
   over at least three comparable closeouts before changing the provisional
   token/time budgets.
7. Publish only the portable principles downstream; retain the repository-
   specific closeout implementation in source-only roots.

## Deferred Items

- All remediation and skill implementation pending explicit owner authorization.
- Selection of the source-only canonical/runtime root and exact distribution
  exclusions.
- Hook storage location, schema versioning, redaction, retention, and client
  integration.
- Final token budget pending measured baselines.
- Any target-release, priority, closure, or publication assignment for
  `REL-004`.

## Appendix

### Commands Run

```text
git status --short --branch
git log -5 --oneline --decorate
git show -s --format="%H%n%aI%n%cI%n%s" <release-commit-shas>
Get-Content <bounded assessment, workflow, release, backlog, and skill files>
rg -n <timestamp-and-validation-patterns> <bounded release paths>
PowerShell line/whitespace-chunk/UTF-8-byte inventory over 14 named context files
GitHub connector read-back for PR #81, PR #82, PR #83, Issue #57, and Issue #57 comments
python .ai/scripts/validate-assessment-artifacts.py
python -m json.tool .dev/assessments/ASM-20260803-003/evidence/incident-record.json
python -c <parse assessment locator with PyYAML>
git diff --check
```

### Notes

- The machine-readable record preserves evidence classification and limitations
  so a future hook can add precision without rewriting this assessment.
- Current-conversation command durations are retained because the owner asked
  for detailed historical evidence, but their evidence class prevents them
  from being confused with independently reproducible repository facts.
- The assessment intentionally does not edit `REL-004`; the merged report and a
  reference comment are enough to connect the evidence while preserving
  backlog authority.

## Lifecycle Handoff

- Assessment path: `.dev/assessments/ASM-20260803-003/report.md`
- Stable finding references: `ASM-20260803-003#AIC-001` through `ASM-20260803-003#AIC-007`
- Remediation owner: `ai-context-governance`
- Related remediation workflow: not created; requires explicit owner authorization under open `REL-004`
- Verification assessment: pending any future remediation
- Remediation intentionally not performed by this skill: `yes`

## Addendum — 2026-08-03 Runtime, Sleep, And Distribution Follow-Up

### Addendum Status And Evidence Boundary

This dated addendum records follow-up evidence obtained after the original
assessment cutoff. It does not rewrite the original timeline, overall score,
decision, finding IDs, or subject revision. The original statement that
sleep/resume and the active/wait split were unavailable was accurate at that
cutoff; the sleep interval is now partly attributable from host and task logs,
while active execution, power-request ownership, and complete token attribution
remain unavailable.

Evidence in this addendum is classified as current-machine or current-task
observation unless a repository or hosted source is named. Raw conversation
content, secrets, credentials, private host identifiers, and complete host logs
are not committed. The original `incident-record.json` remains the immutable
machine-readable snapshot for the initial cutoff. The bounded
`session-019fc7dc-observation.json` file separately records derived metrics and
correction events from a later Codex Desktop thread summary without preserving
the raw conversation.

### Sleep And Resume Reconstruction

| Event | Timestamp (+08:00) | Evidence class | Interpretation |
| --- | --- | --- | --- |
| Last recorded pre-sleep command activity | `2026-08-03 14:07:13.335` | current-task log observation | A command completing shortly before sleep disproves a claim that no Agent work occurred for the entire configured idle interval. |
| Child turn ended with `model_needs_follow_up=false` | `14:07:36.227` | current-task log observation | The child turn was locally complete, but the parent task still owed lifecycle reconciliation and user-facing completion. |
| Kernel-Power session transition, event `566` | `14:07:40.254` | Windows System event log | The host entered the low-power transition about four seconds after the child-turn boundary. |
| Kernel-Power sleep, event `42` | `14:07:44.030` | Windows System event log | Windows explicitly recorded `Sleep Reason: System Idle`; sleep-to-wake was about `4:42:45.765`. |
| Power-Troubleshooter wake | `18:50:29.795` | Windows System event log | The earlier event `566` low-power transition-to-wake span was about `4:42:49.541`. |
| Next recorded task command | `18:50:46.621` | current-task log observation | The app resumed and reconciled the still-active parent task instead of starting a new release operation from zero. |

Windows idle time is driven primarily by user-input idleness; Agent subprocess
activity does not necessarily reset that timer. Therefore a two-hour configured
idle timeout does not prove that the Agent was inactive for two hours before
sleep. The confirmed conclusion is that sleep was not effectively prevented at
the decisive parent/child lifecycle boundary even though the owner had enabled
**Keep this computer awake**. The evidence does not identify whether an app
power request was absent, released, ignored, or scoped differently.

The evidence is consistent with a keep-awake lifetime that ended when the child
turn reported local completion while the parent task still required follow-up.
It is not proof of that exact implementation defect because no contemporaneous
`powercfg /requests` snapshot or app-owned power-request event was captured.
Classify it as a high-priority lifecycle-defect candidate, not as a proven
Release-body or repository-script defect. This strengthens `AIC-001` and
narrows the previously unattributed post-publication gap; it does not change
the assessment decision.

### Approval Policy, Auto-Review, And Execpolicy Rules

The owner reports that this repository did contain an
`approval_policy = "never"` override during the incident period and that the
override was later removed manually. This is owner-supplied historical evidence;
the removed file was not available at follow-up, so its exact path, lifetime,
and effective actor coverage cannot be independently reconstructed.

Follow-up inspection found no *current* file-backed override:

- the user config records `approval_policy = "on-request"` and
  `sandbox_mode = "workspace-write"`;
- the project entry for this repository records only `trust_level = "trusted"`;
- no repository-local `.codex/config.toml` exists at the follow-up revision,
  and that local path is intentionally ignored;
- the current task context records `on-request` with automatic approval review.

Some release-rollout records belong to the separate `codex-auto-review`
reviewer and carry their own `never` plus `read-only` context. Those child
reviewer records do not prove which historical repository override applied to
the parent executor. The earlier absence-of-current-file observation must not
be used to contradict the owner's report about removed historical config.
Future telemetry must record the effective policy source and actor role at turn
start so parent execution is not confused with an approval-review turn.

If an actual executor uses `approval_policy = "never"`, it suppresses approval
prompts; it does not bypass the filesystem, network, service, or sandbox
boundary. An operation that needs escalation can therefore fail closed instead
of being offered to the user or auto-reviewer. That can add retry and rerouting
cost, but it does not explain the confirmed sleep interval.

`.codex/rules` has a separate role: an execpolicy prefix rule controls whether
a matching command may run outside the sandbox with `allow`, `prompt`, or
`forbidden`. It does not install tools, select a Python interpreter, populate
environment variables, make WSL services visible, or replace a readiness
profile. The inspected user rules contain no `gh`, Python, or WSL route. Any
future exception should use the narrowest safe executable/subcommand prefix,
remain machine- or source-repository-specific, and never be exported as a
portable downstream requirement without a separate product decision.

### Python And WSL Routing Clarification

Issue #69 / `TOOL-002` introduced two controls that must not be conflated:

1. `AI_CONTEXT_PYTHON` selects an owner-prepared Python executable. The
   launchers then consider an active environment, generic and versioned PATH
   commands, and an installed offline `uv` managed-Python result before failing
   closed.
2. ignored `.dev/validation.local.conf` selects the local routine-validation
   mode through one strict data line. It does not store a Python path.

The interpreter selector is intentionally provider-neutral and can name an
absolute executable. Moving it into `.codex/rules` would make a portable runtime
contract Codex-specific and would still not solve version or dependency
readiness. A rule is relevant only when a known-safe Python command must be
permitted outside the Codex sandbox; the resolver and prerequisite diagnostic
remain authoritative. General reusable host/runtime readiness belongs to open
Proposal #76.

The current host also disproves a machine-wide WSL absence:

- inside the Windows sandbox, `wsl.exe` was discoverable at
  `C:\WINDOWS\system32\wsl.exe`, but status, distribution enumeration, and a
  simple distro launch failed with `Wsl/Service/E_ACCESSDENIED`;
- outside the sandbox, WSL reported default distro `Ubuntu-24.04`, version 2;
- `wsl.exe -d Ubuntu-24.04 -- bash -lc <read-only-probe>` succeeded;
- `-d Ubuntu` failed separately with `WSL_E_DISTRO_NOT_FOUND` because that is
  not the installed distro name.

Therefore the observed current-machine failure is sandbox/service access plus
one possible distro-name mismatch, not an uninstalled WSL platform. Historical
release records are insufficient to assign their WSL failure to only one of
those causes. For a Linux-native toolchain, prefer running the Agent itself in
WSL2 and restarting the app; for this repository's Windows/.NET gates, use the
declared Windows or Git Bash route unless a WSL environment has independently
proven the required SDK, line-ending, filesystem, and credential readiness.
This strengthens `AIC-005` without changing its severity.

### Background Process Records

The inspected task history contained `81` unique background cell identifiers
and `376` background output/wait records. A contemporaneous OS process check
found no remaining Git, GitHub CLI, Python, Bash, or .NET workload attributable
to the release. The stopped rows shown by the desktop interface are therefore
best classified as retained terminal/task records, not proof that all those
commands are still consuming CPU.

The volume is nevertheless actionable evidence of orchestration fragmentation:
the UI retains many stopped units, while the durable release evidence does not
map them to one parent stage, retry lineage, or terminal completion decision.
Future hooks should record parent task ID, cell ID, start/end, wait reason,
process ID, retry predecessor, and disposal state, and should cap simultaneous
or retained cells per stage.

### Comparative Session Observation — Workflow Policy Development

Codex Desktop thread `019fc7dc-a64a-7491-8357-0fa60a763cb0` provides a later
comparison case for the newly adopted workflow and linear-integration rules.
The thread is not part of the v0.8.0 release incident and its policy work was
materially broader than a Release-body correction, so its durations must not be
used as a like-for-like benchmark. It is useful because the thread summary
exposes turn durations, item types, connector timings, context compactions, and
explicit self-corrections.

| Turn | Purpose | Turn duration | Observable structure |
| --- | --- | ---: | --- |
| `019fc7de-92b5-7331-9d5d-bfdccf6dac81` | Initial single-commit/PR assessment | `0:08:27.672` | `72` items; `51` connector calls; `302.723 s` of recorded connector duration; two failed lookups used the wrong repository owner before correction. |
| `019fc7f3-dee2-7622-b70c-9c42dc319468` | Refine linear integration and small-workflow criteria | `0:06:29.737` | `10` items; no separately timed connector call in the summary. |
| `019fc83e-0c43-7340-8a9f-a90bc9a41945` | Add issue-control-system considerations | `0:02:02.542` | `6` items; discussion-only refinement. |
| `019fc846-1987-76d0-9564-50d8b243a55a` | Implement governance workflow and integrate PR #88 | `0:55:41.310` | `73` items; `21` file-change events; `2` context compactions; `10` connector calls totaling `13.557 s`; local aggregate validation timed out and was decomposed into focused plus hosted gates. |
| `019fc87d-58b8-7ca0-8b09-ea88aa68bb8d` | Direct-mode v0.9.0 allocation and PR #89 closeout | `0:17:19.416` | `38` items; `5` file-change events; `5` connector calls totaling `9.628 s`; three explicit correction loops. |

The five completed-turn durations sum to **`1:30:00.677`**. The first turn
started at `2026-08-03 21:44:40+08:00` and the last completed at
`2026-08-04 00:55:25+08:00`, a wall span of **`3:10:45`**. The difference is
primarily between completed turns while awaiting additional user messages; it
must not be reported as Agent execution or idle processing. Conversely, the
small recorded connector totals inside the two implementation turns do not
explain the turn durations: file editing, shell commands, reasoning, queues,
validation waits, and possible no-output intervals have no complete duration
breakdown in the thread summary.

Explicitly observable rework was:

1. The initial assessment issued two failed connector queries against
   `YuChia/ai-collaboration-prompts-dotnet-backend` before using the correct
   repository identity.
2. At the start of the implementation turn, the Agent corrected an earlier
   sandbox-internal `gh` authentication diagnosis after the owner clarified that
   `gh` was authenticated outside the sandbox and the GitHub connector was
   available.
3. The 55-minute workflow turn required two context compactions, multiple
   cross-surface edit passes, an aggregate-gate timeout, focused fallback tests,
   and hosted-check waiting. These are real costs, but the summary cannot
   allocate their individual durations.
4. In the direct-mode turn, provider test failures were first classified as an
   unrelated baseline drift, then correctly reclassified as required #86
   fixture synchronization after acceptance-criteria review.
5. The first fixture edit left a second `44` assertion unchanged, requiring a
   second edit; the commit validator later required a metadata-only amend for
   issue/scope syntax and the AI attribution trailer.

This comparison strengthens the case for hooks that record every command and
file-edit duration, wait reason, context-compaction boundary, correction
predecessor, validation fingerprint, and user-wait interval. It also shows why
direct mode reduces workflow artifacts but does not by itself eliminate
misclassification, incomplete edits, validation waits, or commit-policy rework.

### Product-Source Boundary Follow-Up

The broader request for a canonical distributable-product source directory is
not already owned by #75, #76, or `REL-004`:

- #75 owns aggregate-gate composition and its packaging disposition;
- #76 owns environment-readiness profiles and local snapshots;
- `REL-004` discusses a dedicated source-only root only for one possible
  repository-specific release-closeout capability;
- completed `DIST-001` defines component and source-only classification, but
  does not establish a canonical product-source tree.

GitHub Proposal
[#85](https://github.com/YuChia-Wei/ai-collaboration-prompts-dotnet-backend/issues/85)
now records the separate design problem. It leaves unresolved whether the new
surface is the canonical editable product source, a generated staging tree, or
a manifest-only projection; implementation or file movement remains
unauthorized.

The external `mattpocock/skills` repository is a positive reference for
separating development organization, promoted product content, and delivery
projections. It keeps development-facing material and non-promoted buckets
alongside centralized skill sources, while its plugin manifest explicitly
selects what is promoted and its README exposes more than one delivery mode.
Its Codex single-path limitation is a delivery-channel constraint documented by
the project, not a counterexample to the development/product model. The lesson
for this repository is to keep one authoritative product source and make each
plugin, copied installation, archive, or future CLI an explicit validated
projection, without copying the exact external folder topology.

GitHub Proposal
[#87](https://github.com/YuChia-Wei/ai-collaboration-prompts-dotnet-backend/issues/87)
now owns the installable-CLI design that consumes the future product-source
contract. Proposal
[#90](https://github.com/YuChia-Wei/ai-collaboration-prompts-dotnet-backend/issues/90)
separately owns the first-class Copilot surface/support matrix and
provider-native projection decisions. Neither proposal authorizes file movement,
implementation, publication, or release allocation.

This corroborates `AIC-007` and creates a separate proposal intake; it does not
expand `REL-004` or change any release assignment.

### Addendum Effect On Findings And Actions

| Existing finding | Addendum effect |
| --- | --- |
| `AIC-001` | Strengthened and narrowed: about 4:42:46 of the release gap is attributable to host sleep; the later session also proves that completed-turn time, inter-turn user wait, and recorded connector time must be separated. |
| `AIC-002` | Unchanged: Python selection, command permission, environment readiness, and package-source decisions must stay in separate progressive-disclosure layers. |
| `AIC-003` | Unchanged: preflight and fingerprint reuse remain required. |
| `AIC-004` | Strengthened: background-cell counts plus two context compactions and repeated correction loops show fragmentation, but no per-agent/cell/edit/rework cost budget exists. |
| `AIC-005` | Strengthened: WSL exists and runs outside the sandbox, while sandbox service access fails closed. |
| `AIC-006` | Unchanged. |
| `AIC-007` | Corroborated by Proposals #85, #87, and #90; product source, installer CLI, Copilot projection, and REL-004 source-only behavior remain separate ownership boundaries. |

The recommended action order is refined as follows:

1. Instrument parent/child turn lifecycle, effective keep-awake ownership,
   effective approval policy plus actor role, sleep/resume, and background-cell
   disposal before another release benchmark.
2. Keep Python selection in `AI_CONTEXT_PYTHON` and prerequisite launchers;
   use `.codex/rules` only for narrow Codex command exceptions, and use #76 for
   portable readiness design.
3. Preflight the selected shell/runtime in its actual security boundary. Do not
   infer WSL or GitHub availability from host installation alone.
4. Triage Proposal #85 independently and decide canonical-source versus
   generated-projection semantics before moving distributable files; coordinate
   #87 and #90 as consumers without collapsing their CLI and Copilot decisions.
5. Continue `REL-004` only through its existing owner-decision boundary.

No original finding is closed, renumbered, or reduced in severity by this
addendum. Overall score `5.5/10` and decision `remediation-recommended` remain
unchanged.

### Addendum Commands And Read-Backs

```text
Get-WinEvent -FilterHashtable <bounded 2026-08-03 System events 1,42,107,566>
Get-Command wsl.exe
wsl.exe --status
wsl.exe -l -v
wsl.exe -d Ubuntu-24.04 -- bash -lc <read-only probe>
Read current Codex config, project trust entry, user rules, and task turn context
Read Issue #69/TOOL-002 implementation decisions and launchers
GitHub read-back for Issues #36, #42, #43, #58, #75-#77 and Proposals #85, #87, #90
Inspect mattpocock/skills README, package metadata, skill tree, plugin manifest, and plugin-layout ADR
Read Codex Desktop thread 019fc7dc-a64a-7491-8357-0fa60a763cb0 summary and derive bounded per-turn metrics
```
