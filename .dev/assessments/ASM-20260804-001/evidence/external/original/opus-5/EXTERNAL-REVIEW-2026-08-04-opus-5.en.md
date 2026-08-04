# External Review: AI Collaboration Framework Source Repository

> Agent-facing version. The human-facing Traditional Chinese counterpart is
> `EXTERNAL-REVIEW-2026-08-04-opus-5.zh-TW.md`. Finding IDs, evidence values, and
> conclusions are identical across both files; only narrative density differs.

## Intake Contract For The Receiving Agent

This document is **external opinion**, not repository truth. Before any claim in
this file becomes a backlog item, workflow, policy, or release input:

1. Normalize it through the repository's own external-review intake path.
2. Require the owner to select which findings enter remediation.
3. Do **not** convert the numeric scores in §5 into a repository health oracle or
   a gate condition. Retain them as attributed external opinion.
4. Treat every quantitative claim as reproducible-but-commit-bound; re-measure
   before acting if `HEAD` has moved from the subject commit.

This intake contract deliberately mirrors the disposition that
`ASM-20260730-001` applied to the previous external review. That disposition was
correct and should be reused.

---

## Metadata

```yaml
review_type: external-independent
review_date: "2026-08-04"
reviewer: "Claude Opus 5"
reviewer_class: external-model
subject_repository: "YuChia-Wei/ai-collaboration-prompts-dotnet-backend"
subject_commit: "4e7b5e0"
subject_branch: "main"
previous_external_review:
  date: "2026-07-30"
  normalized_as: "ASM-20260730-001"
  finding_ids: ["AIC-001", "AIC-002", "AIC-003", "AIC-004", "AIC-005", "AIC-006", "AIC-007", "AIC-008", "AIC-009"]
method:
  used_repository_skills: false
  used_repository_gate_policy: false
  used_repository_scoring_template: false
  used_repository_report_template: false
  evidence_sources:
    - "filesystem measurement (find + wc -l)"
    - "git history (git log, git diff --stat, git tag)"
    - "GitHub REST API /repos/{owner}/{repo}/issues"
    - "direct execution of .ai/scripts entrypoints"
execution_environment:
  platform: "macOS (Darwin 25.5.0)"
  python: "3.9.6"
  python_note: "deliberately below the repository-required 3.11+, used to retest prerequisite diagnostics"
exclusions:
  - "token cost inference"
  - "model compute time inference"
  - "untracked files"
overall_score: 7.2
previous_overall_score: 7.1
decision: "improvement-confirmed-with-resource-allocation-concern"
```

---

## 1. Measured Baseline

### 1.1 Scale

1,462 tracked files, approximately 145,000 lines excluding `.git`.

| Area | Lines | Share | Class |
| --- | ---: | ---: | --- |
| `.dev/workflows` | 65,031 | 45% | self-governance-history |
| `.ai/scripts` | 30,094 | 21% | validation-tooling |
| `.dev/standards` | 15,189 | 10% | mixed |
| `.dev/assessments` | 11,267 | 8% | self-governance-history |
| `.ai/assets/skills` | 8,605 | 6% | **portable-product** |
| `.dev/guides` | 7,313 | 5% | human-facing |
| `.dev/backlog` | 4,246 | 3% | self-governance-history |
| `tools/` (C#) | 2,887 | 2% | **portable-product** |
| `.dev/releases` | 2,075 | 1% | self-governance-history |
| `.ai/assets/tech-stacks` | **1,487** | **1.0%** | **portable-product** |
| `.claude/skills` + `.agents/skills` | 1,044 | <1% | runtime-wrappers |
| `.dev/specs` + `.dev/adr` | 1,002 | <1% | mixed |

### 1.2 Derived Ratios

```yaml
governance_history_to_portable_product:
  governance_history: 82619   # workflows 65031 + assessments 11267 + backlog 4246 + releases 2075
  portable_product: 28434     # skills 8605 + tech-stacks 1487 + production-python 13007
                              # + wrappers 1044 + dotnet-standards ~1404 + analyzers 2887
  ratio: 2.91
  previous_ratio: ~1.0
  direction: worsened

validator_to_validated:
  validator_surface: 24440    # production python 13007 (28 files) + python tests 11433 (48 files)
  validated_content: 10092    # skills 8605 + tech-stacks 1487
  ratio: 2.42
  largest_single_validator: ".ai/scripts/validate-ai-context.py (1880 lines)"
```

### 1.3 Output Cadence

```yaml
commits_per_week:
  2026-W27: 23
  2026-W28: 67
  2026-W29: 167
  2026-W30: 106
  2026-W31: 118
  2026-W32: 34   # partial
workflow_directories_by_month:
  2026-04: 3
  2026-05: 4
  2026-06: 4
  2026-07: 64    # 79% of all 81 directories
  2026-08: 3
assessment_records: 30        # 2026-07: 25, 2026-08: 5
backlog_items: 45
release_tags: 10              # v0.1.0 .. v0.8.0
delta_since_previous_review:
  from_commit: "2263744"
  files_changed: 159
  insertions: 8990
  deletions: 184
  releases_published: ["v0.6.0", "v0.7.0", "v0.8.0"]
```

### 1.4 Online Issue State

```yaml
issues_total: 51
issues_closed: 42
issues_open: 9
pull_requests: 40
open_issues:
  - number: 21
    age_days: 6
    labels: ["migration:historical", "kind:story", "scope:framework"]
    comments: 0
    title: "[DEVWF-001] Evaluate Issue Traceability And Rich Task Timeline Metadata"
  - number: 43
    age_days: 6
    labels: ["migration:historical", "kind:story", "scope:framework"]
    comments: 0
    title: "[INIT-001] Existing AI Agent Repository Compatibility Intake"
  - number: 57
    age_days: 6
    labels: ["migration:historical", "kind:enabler", "scope:source-repo"]
    comments: 1
    title: "[REL-004] Evaluate Source-Only AI Context Release Closeout"
  - number: 61
    age_days: 6
    labels: ["migration:historical", "kind:enabler", "scope:framework"]
    comments: 0
    title: "[STD-001] Standards Simplification Deliberation And Release Decision"
  - number: 75
    age_days: 2
    labels: ["triage:needed", "kind:proposal", "scope:mixed"]
    comments: 0
    title: "[Proposal] Separate check-all Aggregate Gates from Downstream Workflow Validation"
  - number: 76
    age_days: 2
    labels: ["triage:needed", "kind:proposal", "scope:mixed"]
    comments: 0
    title: "[Proposal] Add Environment Readiness Profiles for Host and Agent Capabilities"
  - number: 85
    age_days: 1
    labels: ["triage:needed", "kind:proposal", "scope:mixed"]
    comments: 0
    title: "[Proposal] Establish a Canonical Product Artifact Source Tree"
  - number: 87
    age_days: 1
    labels: ["triage:needed", "kind:proposal", "scope:mixed"]
    comments: 0
    title: "[Proposal] Package the AI Context Framework as an Installable CLI"
  - number: 90
    age_days: 1
    labels: ["triage:needed", "kind:proposal", "scope:mixed"]
    comments: 0
    title: "[Proposal] Define First-Class GitHub Copilot Support"
observations:
  - "all 9 open issues were created by created-by:codex"
  - "all 5 triage:needed proposals have zero comments and zero release target"
  - "oldest open issue is 6 days; throughput itself is healthy"
```

---

## 2. Confirmed Improvements

### F-01 — Python prerequisite diagnostics remediated (was `AIC-004`)

```yaml
finding_id: F-01
status: resolved-and-verified
previous_id: "ASM-20260730-001#AIC-004"
severity_before: medium
verification_method: "direct execution under Python 3.9.6 with -S (site-packages isolated)"
```

The only concretely reproducible runtime defect from the previous review is
fixed. Verbatim output observed during this review:

```
$ python3 -S .ai/scripts/validate-ai-context.py --help
Python prerequisite blocked for .ai/scripts/validate-ai-context.py:
unsupported-python; selected=/Library/.../python3 version=3.9.6; missing=none;
requirements=/Users/.../requirements.txt; recovery: install Python >=3.11, then retry
```

`validate-workflow-artifacts.py` behaves identically. A bare
`ModuleNotFoundError: No module named 'yaml'` has been replaced by structured
output carrying selected interpreter path, actual version, missing-dependency
list, absolute requirements path, and an explicit recovery instruction. A real
(non-`--help`) invocation exits 1.

This is a genuine runtime fix, not a documentation patch. It is the single
largest perceived-quality change for a first-time downstream adopter.

Residual issue: see F-09.

### F-02 — `STD-001` bottleneck cleared

```yaml
finding_id: F-02
status: resolved
previous_concern: "AIC-001/002/003 all deferred into a single unexecuted deliberation item two gates away from landing"
elapsed_to_resolution: ~1 day
```

The previous review flagged that all three friction findings were parked on
`STD-001`, whose `handoff_condition` forbade release assignment, canonical
standards edits, and implementation successors until the rounds were normalized
and approved.

Actual disposition: Round 1 ("Workflow Gate Proportionality And Direct-Mode
Decision Contract") was owner-selected on 2026-08-03, produced
`implementation_ref: GOV-004`, and `GOV-004` is now `resolved` and allocated to
`v0.9.0` with `gate: release-blocker`.

### F-03 — `GOV-004` design is superior to the external proposal

```yaml
finding_id: F-03
status: confirmed-strength
```

`GOV-004` separates four decisions that were previously coupled:

1. execution record mode (`direct` / `assessment` / `workflow`)
2. delivery grouping (whether multiple Issues bind to one delivery)
3. integration gate (pull request required or not)
4. Git topology (linear or merge commit)

Acceptance criteria, verbatim:

> "Issue, task, commit, and file counts remain signals rather than sole mode or
> topology rules."
>
> "Linear and merge-commit integration are normal positive topology choices
> independent of pull-request requirements."

This is the correct formulation of what the previous external review got wrong
when it proposed a `<10 files` direct-mode threshold. The repository did not
merely reject the bad proposal; it formalized the correct version.

### F-04 — Self-assessment is more critical than external assessment

```yaml
finding_id: F-04
status: confirmed-strength
severity_class: notable-positive
```

| Assessment | Topic | Self-score | Decision |
| --- | --- | ---: | --- |
| `ASM-20260803-004` | Workflow proportionality, delivery cohesion, merge topology | **6.5/10** | `remediation-recommended` |
| `ASM-20260803-003` | v0.8.0 release time and context-cost incident | **5.5/10** | `remediation-recommended` |

Both scored below this external review's rating of the same repository.

`ASM-20260803-003` demonstrates unusually disciplined epistemics:

- refuses to claim token waste without telemetry
- names **the inability to answer the owner's cost-accountability question** as
  its own highest-severity finding
- self-corrects an overstatement: "The direct GitHub Release body edit was not a
  five-hour operation ... observed the command at 1.8 seconds"
- downgrades its own timing evidence to "conversation observations, not
  independently reproducible repository facts"

A self-assessment that voluntarily downgrades its own evidence class is rare in
AI collaboration frameworks. This is the most positive finding of this review.

---

## 3. Unimproved Areas And New Risks

### F-05 — Governance-history to product ratio has worsened

```yaml
finding_id: F-05
severity: high
category: delivery-value-density
evidence:
  ratio_now: 2.91
  ratio_previous: ~1.0
  workflows_share_of_repo: 0.45
  workflow_dirs_created_2026_07: 64
  workflow_dirs_total: 81
```

Concrete case: the delivery that fixed excess ceremony (`GOV-004`) itself
produced 1 workflow, 2 assessments, 2 tasks, 1 Issue, 1 PR, and consumed a
`v0.9.0` `release-blocker` slot. The policy states that "one task or fewer than
three tasks triggers proportionality review" — and it was delivered by a
workflow with exactly two tasks.

This is not automatically a violation (proportionality review triggers a review,
not a prohibition), but it is the first self-application case for the new
policy, and it is the most easily identified consistency question an external
observer will raise.

**Risk if unaddressed:** every efficiency improvement enlarges the thing it is
trying to shrink. Extrapolating the current rate, governance history exceeds
100k lines before v1.0, and downstream adopters must distinguish portable from
non-portable content inside it.

### F-06 — Validator surface exceeds validated content

```yaml
finding_id: F-06
severity: high
category: unpriced-maintenance-surface
evidence:
  validator_lines: 24440
  validated_lines: 10092
  ratio: 2.42
  largest_file: ".ai/scripts/validate-ai-context.py (1880 lines)"
  production_python_files: 28
  test_python_files: 48
```

Any team that forks, customizes, or upgrades the framework inherits maintenance
responsibility for 24,440 lines of Python. The framework currently publishes no
metric that lets them assess this before adoption.

The repository's own issue #75 identifies related cost problems (see F-07) but
has no release target.

### F-07 — The framework has self-confirmed adoption friction, yet none of it is release-allocated

```yaml
finding_id: F-07
severity: high
category: resource-allocation
```

Issue #75, verbatim:

> "The current aggregate path combines framework self-tests, workflow-governance
> checks, package/release-oriented validation, and .NET template tests. It runs a
> large sequential command set **without changed-path selection, caching,
> parallel execution, or a per-check time budget**. On slower or heterogeneous
> developer hosts, this can delay product work and cause Agents to repeatedly
> diagnose unavailable prerequisites, **increasing token and elapsed-time cost
> for checks unrelated to the target change**."

Combined with the 5.5/10 self-score in `ASM-20260803-003`, execution cost is now
a repository-acknowledged fact rather than external speculation.

Allocation does not match:

| Work item | Domain | Release target |
| --- | --- | --- |
| `GOV-004` | governance rules | `v0.9.0`, `release-blocker` |
| #75 | validation cost | **none** |
| #76 | environment readiness | **none** |
| #85 | product source boundary | **none** |
| #87 | installable CLI | **none** |
| #90 | Copilot support | **none** |

### F-08 — Proposal queue is interlocked with zero triage

```yaml
finding_id: F-08
severity: medium-high
category: intake-convergence
evidence:
  proposals_created_in_3_days: 5
  proposals_with_zero_comments: 5
  proposals_with_release_target: 0
```

The five proposals reference one another as preconditions:

- **#85** (canonical product artifact source tree) establishes which paths are
  product versus source-repository-only.
- **#87** (installable CLI) states in its body that it must account for the #85
  product-source decision.
- **#90** (first-class Copilot support) states that #85 and #87 "must account for
  Copilot as a delivery projection."
- **#75** (check-all gate separation) and **#76** (environment readiness
  profiles) form a second axis; #76 explicitly cites #69's Python discovery
  experience and #75's cost problem.

This is a triangular dependency plus a crossing second axis, with no owner
sequencing decision. It is structurally the same shape as the
`STD-001` / `OBS-001` dependency that took a week to clear.

Positive counterweight: 42 closed versus 9 open, oldest open issue 6 days.
Throughput is healthy. The problem is **generation rate exceeding disposition
rate, with newly generated items depending on each other**.

### F-09 — `--help` returns exit 0 while prerequisites are blocked

```yaml
finding_id: F-09
severity: low
category: tooling-consistency
```

Within the F-01 remediation, `--help` emits the correct diagnostic but returns
exit 0 when prerequisites are unmet; real execution returns exit 1.

Wrapper scripts commonly probe `cmd --help` to determine tool availability. The
current behavior causes such probes to report available, deferring failure to
actual execution. This runs counter to F-01's own purpose of failing earlier and
more clearly.

### F-10 — .NET capability positioning does not match its actual location

```yaml
finding_id: F-10
severity: medium
category: navigation-and-positioning
corrects_previous_review: true
```

**This review corrects an undercount in the previous external review.** `tools/`
contains 9 executable Roslyn analyzers totaling 2,887 lines of C#:

| Analyzer | Enforces |
| --- | --- |
| `AggregateInfrastructureDependencyAnalyzer` | aggregate-to-infrastructure dependency |
| `EventSourcedAggregateMutationAnalyzer` | event-sourced aggregate mutation |
| `ControllerComplianceAnalyzer` | controller compliance |
| `RepositoryQueryMethodAnalyzer` | repository query methods |
| `ProjectionReadOnlyAnalyzer` | projection read-only constraint |
| `UseCaseServiceProviderInjectionAnalyzer` | UseCase ServiceProvider injection |
| `MapperComplianceAnalyzer` | mapper compliance |
| `RuleDescriptors`, `DiagnosticCategories` | rule descriptors and categories |

This is executable capability, not documentation. The previous review's ".NET
content is thin" finding did not account for it.

The remaining problem: `README.md`'s five-row Quick Navigation table contains
**no entry pointing to `tools/`**, and `.ai/assets/tech-stacks` is 1.0% of the
repository. A repository named `...-dotnet-backend` does not surface its actual
.NET entry point at the first navigation layer. Users arriving by repository
name will look in the wrong place.

---

## 4. Previous-Review Corrections Carried Forward

```yaml
correction_1:
  claim_retracted: "PR #66 was a 4-file Python relocation producing ~330 lines of process documentation"
  actual: "36 files, +2140, -1524; a distribution compatibility change including published compatibility entrypoints, wrapper sync, distribution profile, provider projection, and new contract tests"
  dependent_recommendation_retracted: "route changes under 10 files to direct mode"
  reason: "the threshold would route exactly this class of high-risk compatibility work into direct mode"
  repository_disposition: "ASM-20260730-001#AIC-001 overturned it; correct"
  status_in_this_review: "no count-based threshold is proposed anywhere in this report"

correction_2:
  claim_qualified: "code review imposes a fixed 745-line reference load"
  qualification: "ASSESSMENT-ARTIFACT-POLICY.md (241 lines) binds only for persisted reviews; the sum is not a universal fixed cost"

correction_3:
  claim_retracted: "split the approved release into separate .NET and governance package identities"
  reason: "conflicts with resolved DIST-001; the previous reviewer had not read DIST-001"

correction_4:
  claim_corrected_in_this_review: ".NET capability is thin"
  correction: "undercounted; tools/ contains 9 executable Roslyn analyzers (2887 lines C#). See F-10."
```

---

## 5. Scoring

Scoring dimensions are defined independently by this review. The repository's own
scoring templates and gates were not used. **Do not convert these into repository
metrics.**

| Dimension | Prev (07-30) | Now (08-04) | Basis |
| --- | ---: | ---: | --- |
| Engineering discipline / governance rigor | 9.3 | **9.5** | self-scores below external score; voluntary evidence downgrade and self-correction (F-04) |
| Automation and verifiability | 8.8 | **8.5** | ↓ 24,440 lines of validator code is itself unpriced liability (F-06) |
| Skill design quality | 7.8 | **8.0** | GOV-004's four-decision separation is correct and better than the external proposal (F-03) |
| Portability / adoption cost | 6.0 | **6.8** | ↑ prerequisite diagnostics fixed and independently verified (F-01); check-all cost unresolved (F-07) |
| Delivery value density | 6.0 | **5.5** | ↓ ratio worsened to 2.91:1; tech-stacks still 1.0% (F-05) |
| Context efficiency / cognitive load | 5.0 | **5.5** | ↑ GOV-004 reduces future ceremony; corpus still grew by 8,990 lines |
| Documentation and navigation | 7.0 | **7.0** | README 357 → AGENTS 244 → standards 3,336 lines; .NET entry point absent (F-10) |
| Issue management and convergence | — | **6.0** | 42 closed / 9 open is healthy throughput; 5 proposals interlocked with zero response (F-08) |
| Self-sustainability / bus factor | 4.0 | **4.0** | single owner, single agent producer; unchanged |

### Overall: 7.1 → **7.2**

The 0.1 delta is not the signal. **The signal is that after +8,990 lines, 3
releases, and 391 commits, the score barely moved.** Strengths strengthened, the
prior concrete defect was genuinely fixed, and the prior bottleneck was genuinely
cleared — all real. But delivery value density regressed in the same period, and
self-sustainability did not move at all. Current throughput is converting mostly
into marginal governance-quality gains rather than expanded deliverable
capability.

---

## 6. Proposed Work Packages

`WP-n` identifiers are internal to this report and do not presume the
repository's backlog numbering. **These are proposals, not authorization.**

```yaml
sequencing:
  wave_1_independent_parallel:
    - WP-1   # unblocks everything downstream
    - WP-2   # makes efficiency findings measurable for the first time
  wave_2_depends_on_WP2_measurements:
    - WP-4
    - WP-3
  anytime_independent_low_cost:
    - WP-5
    - WP-6
```

### WP-1 — Proposal queue sequencing decision

```yaml
work_package: WP-1
addresses: [F-08]
priority: highest
mode_recommendation: direct
estimated_effort: "one owner decision plus 5 issue comments"
```

**Do not triage case-by-case.** Per-issue triage reproduces the state where each
item waits on another. Make one axis-level sequencing decision instead.

Two axes:

| Axis | Members | Shared undefined question |
| --- | --- | --- |
| A. Packaging and projection | #85 → #87 → #90 | what is product versus source-repository-only |
| B. Environment and execution cost | #75 → #76 | which checks run where, and for how long |

Root selection:

- **Axis A root is #85.** #87 (CLI) and #90 (Copilot) are both delivery
  projections of the product boundary #85 establishes. Designing a CLI or Copilot
  support before the boundary exists yields two conflicting product definitions.
- **Axis B root is #75.** #76 (environment readiness profiles) needs to know
  which validation profiles exist before it can declare profile prerequisites.

Record explicit `waits_for` relationships on #87, #90, and #76 so the queue state
is self-describing and the next agent does not re-derive it.

Axes A and B are independent and may proceed in parallel.

```yaml
acceptance:
  - "each of the 5 proposals carries exactly one status: selected-for-design | waits_for:<issue> | deferred | closed-superseded"
  - "#85 and #75 each have an owner and an explicit decision-question list"
  - "no proposal remains in zero-response-and-zero-status state"
risk_if_skipped: >
  The queue continues growing at roughly 5 proposals per 3 days, and new proposals
  continue citing undecided proposals as premises, turning a triangular dependency
  into a mesh. Sequencing cost then rises by an order of magnitude.
```

### WP-2 — Minimum viable execution telemetry

```yaml
work_package: WP-2
addresses: [F-07, F-06]
also_addresses: "ASM-20260803-003 self-declared highest-severity finding"
priority: highest-roi
blocks: [WP-3, WP-4]
estimated_effort: medium
```

**Design constraint: do not build token telemetry.** Token telemetry requires a
uniform cross-runtime interface, and the framework explicitly targets multiple
runtimes (Claude, Codex, prospective Copilot) — that path collides immediately
with #90. It also answers the wrong question. The real question is not "how many
tokens" but "which steps were necessary."

**Record structure, not cost.** Add to each workflow locator or closeout record:

```yaml
execution_record:
  started_at: "<ISO 8601>"
  ended_at: "<ISO 8601>"
  validators_invoked:
    - name: "check-all.sh --critical"
      invocations: 4
    - name: "validate-workflow-artifacts.py"
      invocations: 7
  pr_boundaries: 3
  retries_due_to_environment: 2
```

All five fields are derivable from existing Git and CI facts. No new runtime
capability and no cross-provider protocol is required.

Questions this answers:

| Question | Source field |
| --- | --- |
| How many times was one validator re-invoked within a single delivery? | `validators_invoked[].invocations` |
| Which workflows have wall time grossly disproportionate to task count? | `started_at`/`ended_at` vs task count |
| What fraction of execution is environment retry? | `retries_due_to_environment` |
| Do PR boundaries match the delivery-cohesion decision? | `pr_boundaries` vs `GOV-004` grouping |

`ASM-20260803-003` already recorded a "10:47:46 end-to-end release workflow" and
a "5:42:29 unattributed post-publication interval" — proving the data is
obtainable and merely unstructured.

```yaml
acceptance:
  - "newly created workflows include an execution_record block"
  - "at least one complete release produces a comparable record"
  - "a query can identify validators invoked more than N times within one delivery"
risk_if_skipped: >
  All efficiency work stays inference-from-volume, and no improvement can be
  verified as effective. This is precisely the highest-severity finding that
  ASM-20260803-003 raised against itself.
```

### WP-3 — Workflow history retention policy

```yaml
work_package: WP-3
addresses: [F-05]
depends_on: WP-2
estimated_effort: medium
precondition_status: "already met — see below"
```

**The existing trigger has already fired.** `SIMPL-001` deliberately decided
*not* to archive history and set
`archive_preconditions.target_horizon: "v0.7.0-conditional"`. Both v0.7.0 and
v0.8.0 have shipped. **The condition has matured; this is fulfilment of an
existing decision, not a new proposal.**

Define three tiers rather than a binary keep/delete:

| Tier | Content | Location |
| --- | --- | --- |
| active | unclosed workflows | `.dev/workflows/` |
| indexed | closed-workflow summary: ID, dates, outcome, linked assessments, final commit SHA | `.dev/workflows/INDEX.MD` |
| archived | full content of closed workflows | orphan branch or release asset |

**Summarization is not deletion.** The indexed tier preserves full traceability
(any entry restorable from its recorded commit SHA) while removing the bulk from
the default clone and default agent scan path.

Archive selection should be driven by WP-2 data: prioritize directories that are
closed, have no downstream references, and predate the last two releases.

```yaml
acceptance:
  - "retention tiers are stated in policy"
  - "any archived workflow is fully restorable from a recorded commit SHA"
  - "active .dev/workflows line count stays under a stated ceiling"
timing_note: >
  Run after WP-2. Setting an archive threshold without measurement replaces
  no-threshold with an arbitrary number.
```

### WP-4 — Validator cost budget and published metric

```yaml
work_package: WP-4
addresses: [F-06, F-07]
depends_on: WP-2
estimated_effort: "metric: small (immediately actionable); profile split: medium"
```

1. **Publish one metric.** Have `check-all.sh` print on completion:

   ```
   validator surface: 24,440 lines / validated content: 10,092 lines (ratio 2.42:1)
   ```

   Print only; do not gate. **A published metric is self-constraining** and
   requires no policy debate to implement.

2. **Split profiles along #75's stated direction.** #75 already proposes the
   correct decomposition:

   | Profile | Consumer | Contents |
   | --- | --- | --- |
   | `source-ci` | source repository CI and release | full fail-closed aggregate gate |
   | `downstream-workflow` | downstream product workflows | target-owned tests plus only the required workflow/checkpoint validators |
   | `framework-selftest` | framework path changes, explicit downstream framework verification | framework self-tests |

3. **Add changed-path selection.** #75 notes it is absent. This is the single
   highest cost-benefit change in the set.

```yaml
acceptance:
  - "the ratio metric is visible on every check-all run"
  - "at least two profiles are independently invocable"
  - "downstream handoff prerequisites no longer require the full aggregate gate"
coordination_note: "merge with the #75 sequencing decision in WP-1 rather than running separately"
```

### WP-5 — .NET capability positioning correction

```yaml
work_package: WP-5
addresses: [F-10]
mode_recommendation: direct
estimated_effort: minimal
```

Add one row to the Quick Navigation table in both `README.md` and
`README.en.md`:

| Goal | Start here |
| --- | --- |
| Get executable .NET architecture rule enforcement | `tools/DotnetBackendAnalyzers/` |

And state the actual capability distribution in the .NET section:

> .NET capability currently lives in three places: `tools/` Roslyn analyzers
> (executable rule enforcement), `.dev/standards/` coding and review standards
> (shared by humans and agents), and `.ai/assets/tech-stacks/dotnet-backend/`
> technology-stack context (portable). The portable portion is currently the
> smallest of the three.

**The value here is honesty.** Stating plainly that portable .NET content is the
smallest slice, and that executable capability lives in the analyzers, is better
than letting repository-name-driven users search `tech-stacks` and come away
disappointed. It also sharpens `OBS-001`'s value proposition: what it fills is
exactly the portable slice.

```yaml
acceptance:
  - "quick navigation in both language READMEs includes a tools/ entry"
  - "the three-location .NET capability distribution is stated explicitly"
```

### WP-6 — Prerequisite exit-code consistency

```yaml
work_package: WP-6
addresses: [F-09]
mode_recommendation: direct
estimated_effort: minimal
```

When a prerequisite check blocks, `--help` should return the same non-zero exit
code as real execution, or a dedicated `--check-prerequisites` probe subcommand
should return a structured result with documented exit-code semantics.

```yaml
acceptance:
  - "cmd --help does not return 0 while prerequisites are blocked, OR"
  - "a dedicated probe subcommand exists with documented exit-code semantics"
```

---

## 7. Reproduction Notes

```yaml
reproducible: true
subject_commit: "4e7b5e0"
caveat: "line counts move with HEAD; re-measure before acting if HEAD has advanced"
commands_used:
  scale: "find <dir> -type f | xargs wc -l"
  history: "git log --oneline; git diff --stat <a>..<b>; git tag"
  cadence: "git log --since='8 weeks ago' --date=format:'%Y-W%V' --pretty=format:'%ad' | sort | uniq -c"
  issues: "curl -s https://api.github.com/repos/YuChia-Wei/ai-collaboration-prompts-dotnet-backend/issues?state=all&per_page=100"
  prerequisite_retest: "python3 -S .ai/scripts/validate-ai-context.py --help"
format_note: >
  This report deliberately does not conform to the repository assessment
  template. It was produced without the repository's skills, gate policy, or
  scoring rubric in order to provide a view unconditioned by existing framework
  assumptions. If it is to be retained, route it through the external-review
  intake path and let that path decide which claims become normalized findings.
```

---

*End of report. Reviewer: Claude Opus 5. Subject commit: `4e7b5e0`. Date: 2026-08-04.*
