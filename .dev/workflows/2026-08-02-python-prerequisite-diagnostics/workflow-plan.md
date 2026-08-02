# Standardize Python Prerequisite Diagnostics Across Validator Entrypoints

## Template Metadata

- `template_id`: `ai-context-governance-maintenance-workflow-plan`
- `template_version`: `1.2.0`
- `created_at`: `2026-07-10T18:22:49+08:00`
- `updated_at`: `2026-07-13T23:11:56+08:00`

## Workflow Metadata

- `workflow_id`: `2026-08-02-python-prerequisite-diagnostics`
- `workflow_kind`: `ai-context-maintenance`
- `owner_skill`: `ai-context-governance`
- `branch`: `codex/2026-08-02-python-prerequisite-diagnostics`
- `base_branch`: `main`
- `branch_segment`: `1`
- `status`: `in_progress`
- `current_phase`: `remediation-planning`
- `artifact_root`: `.dev/workflows/2026-08-02-python-prerequisite-diagnostics`
- `created_at`: `2026-08-02T10:32:53+08:00`
- `updated_at`: `2026-08-02T16:53:39+08:00`
- `template_source`: `.ai/assets/skills/ai-context-governance/templates/ai-context-maintenance-workflow-plan-template.md`
- `template_version`: `1.2.0`

## Authorization And Decision Boundary

- Work-item binding: GitHub Issue [#69](https://github.com/YuChia-Wei/ai-collaboration-prompts-dotnet-backend/issues/69).
- Baseline evidence: `.dev/assessments/ASM-20260730-001/assessment.yaml` and `ASM-20260730-001#AIC-004`.
- Authorization source: the repository owner requested on 2026-08-02 that this workflow be opened, that design decisions be discussed one at a time with impact explanations, and that approved design continue into implementation without closing this workflow.
- Authorized now: workflow bootstrap, repository-backed impact inventory, design discussion, and durable decision recording.
- Approval gate: implementation edits remain pending until the owner explicitly approves the accumulated design direction.
- Provider state: Issue #69 remains open with its existing proposal/triage labels. On 2026-08-02 the owner reported manually changing its GitHub Project Status to `In progress`; the connected Issue read confirms the Issue remains open but does not expose Project fields. This owner-reported tracker update aligns work visibility with the active design workflow but does not authorize implementation or replace the workflow approval gate.

## Objective And Scope

- Problem statement: the aggregate shell runner emits a repository-owned Python prerequisite diagnostic, while directly invoked validator and package entrypoints may raise raw `tomllib` or `yaml` import exceptions before they can explain the Python 3.11+ and pinned-dependency prerequisites.
- Authorized remediation scope: inventory supported user-facing Python entrypoints, decide a consistent fail-closed prerequisite contract, implement the approved design, add deterministic unsupported-version and missing-dependency coverage, synchronize user-facing commands and package projections, and verify that diagnostics occur before mutation or success claims.
- Exclusions: weakening validation, package, upgrade, or release gates; claiming support for Python versions below 3.11; silently or implicitly installing Python/dependencies without a later explicit owner decision; broad unrelated validator refactoring; release preparation or publication.
- Completion criteria: every approved supported entrypoint reports the selected executable/version, Python 3.11+ requirement, missing required dependency when applicable, sanctioned installation command, and pre-mutation stop state; deterministic negative-path tests pass; aggregate and direct behavior remain compatible; an independent post-remediation AI-context assessment reconciles `AIC-004`.

## Artifact Contract

- Baseline assessment: `.dev/assessments/ASM-20260730-001/assessment.yaml`
- Remediation report: `.dev/workflows/2026-08-02-python-prerequisite-diagnostics/reports/remediation-report.md` (created during remediation evidence consolidation)
- Verification assessment: `.dev/assessments/<verification-assessment-id>/assessment.yaml` (created after implementation and validation)
- Tasks: `.dev/workflows/2026-08-02-python-prerequisite-diagnostics/tasks/`
- Entrypoint inventory (English agent-facing source): `.dev/workflows/2026-08-02-python-prerequisite-diagnostics/evidence/entrypoint-inventory.md`
- Entrypoint inventory (complete Traditional Chinese Taiwan owner-review translation): `.dev/workflows/2026-08-02-python-prerequisite-diagnostics/evidence/entrypoint-inventory.zh-TW.md`
- Runtime fallback and ownership assessment (English agent-facing source): `.dev/workflows/2026-08-02-python-prerequisite-diagnostics/evidence/runtime-fallback-and-ownership-assessment.md`
- Runtime fallback and ownership assessment (complete Traditional Chinese Taiwan owner-review translation): `.dev/workflows/2026-08-02-python-prerequisite-diagnostics/evidence/runtime-fallback-and-ownership-assessment.zh-TW.md`
- Python runtime selection history, OS-native alternatives, and translation-routing deviation: `.dev/workflows/2026-08-02-python-prerequisite-diagnostics/evidence/python-runtime-selection-history-and-native-options.md`

## Finding Triage

| Finding | Severity | Owner | Disposition | Task | Validation |
| --- | --- | --- | --- | --- | --- |
| `ASM-20260730-001#AIC-004` | MEDIUM | `ai-context-governance` | D-001 approved; remaining design in progress; implementation authorized only after explicit accumulated-design approval | `AIC-004-diagnostic-design`, then portable `AIC-004-diagnostic-implementation`, then `AIC-004-source-diagnostic-implementation` | entrypoint inventory, fallback/ownership assessment, deterministic prerequisite tests, affected validators/package tests, aggregate gates, independent verification assessment |

## Initial Impact Assessment

- Repository-native inventory found 74 tracked Python files on the candidate surfaces. Seventy have a direct `__main__` execution path: 25 production CLIs and 45 test CLIs; four are import-only support modules.
- The 25 production CLIs split into 12 portable payload entrypoints and 13 source-only maintainer/CI entrypoints under the current distribution profile.
- Twenty-three of the 25 production CLIs require PyYAML directly or through a local module. Two are standard-library-only. `validate-ai-context.py` additionally imports Python 3.11's `tomllib` before `main`.
- The package planner already has a one-off PyYAML diagnostic and a bytecode-suppression guard. Other dependency-bearing direct entrypoints generally import before a repository-owned diagnostic, so the current contract is inconsistent rather than wholly absent.
- The current Windows host exposed a separate bootstrap boundary: `python` and `python3` resolve to unprovisioned Windows App Execution Aliases, so a direct `python <script>.py` invocation fails before repository Python code can run. A later probe found a usable uv-managed `python3.14` command that the current resolver misses, but that interpreter and the current Codex bundled Python both lack PyYAML. Candidate discovery and dependency readiness must therefore remain separate checks.
- Write-capable risk is concentrated in package apply and several source-only build/render/evaluation tools. Read-only validators still need the version gate so they cannot report success under an unsupported interpreter.
- The main design cost is not only a helper module: the approved boundary will affect entrypoint registration, import order, bytecode/no-write behavior, package projection, direct-command documentation, deterministic subprocess fixtures, and aggregate validation.
- D-001 is approved as Option A with an ordered portable-first rollout: the 12 downstream/portable CLIs form the first implementation and validation batch; the 13 source-only CLIs form a second batch that cannot start until the first reaches its approved gate.
- Existing ownership policy and deterministic tests currently classify two canonical skill-owned production scripts, one root compatibility entrypoint, and 22 repo-common production scripts. The owner requested a fresh ownership decision before implementation; the preliminary per-entrypoint matrix remains a recommendation, not an approval.
- Git history contains no current comparison-backed ADR that selects Python as the canonical validator runtime. Python entered incrementally, PyYAML spread when nested YAML validation was added, and dependency/bootstrap declarations followed clean-environment failures. Retaining Python is therefore a pending design decision rather than established owner-approved rationale.
- A historical, now-retired `ADR-052` acknowledged that its Markdown parser required Python but treated that prerequisite as a consequence; it did not compare runtime alternatives. Full OS-native validator rewrites would create multiple platform implementations and YAML parsing gaps, while thin OS-native launchers remain a bounded candidate for discovery and diagnostics.
- The two existing zh-TW evidence files were produced by the primary `gpt-5.6-sol` agent even though active routing assigns finalized derived translations to the low-cost `context-translator` (`gpt-5.6-terra`, low reasoning). Their parity checks passed, but the cost-routing process was not followed; corrective handling is pending owner direction.
- The owner accepted the existing translation content without regeneration. Future derived zh-TW work must use the promoted low-cost translator after English finalization, record the resolved model, and stop rather than fall back to the primary agent when that route is unavailable.
- Current downstream validation has selection modes but no target-owned enablement policy. `--quick`, `--critical`, and `--full` select batches; `check-all.sh` resolves Python before any batch can run, and selected Python checks are generally hard-coded as required. `AI_CONTEXT_PYTHON` selects an interpreter rather than enabling or disabling validation.
- Context-driven `not applicable` behavior exists for absent source-release/provenance/spec inputs, but it is not an owner or developer toggle. No pre-commit hook automatically invokes the aggregate runner. Source CI runs `--quick`, while the distribution profile packages scripts under mandatory core components without projecting the source `.github/workflows/portable-gates.yml` workflow.
- A validation activation switch would not remove Python from explicit package apply, initialization, or upgrade lifecycles. Routine local/CI enforcement must be separated from safety-critical lifecycle commands before a switch is designed.
- The owner confirmed that repeated automatic local-check failures during software-development workflows cause Agent retries and material token waste. Token control is therefore a first-class acceptance concern: policy must be resolved before invocation, and an unchanged prerequisite failure must not trigger identical command retries.
- The owner authorized external tracking for the out-of-scope aggregate-runner concerns. GitHub Proposal [#75](https://github.com/YuChia-Wei/ai-collaboration-prompts-dotnet-backend/issues/75), `[Proposal] Separate check-all Aggregate Gates from Downstream Workflow Validation`, now owns aggregate composition, source-versus-downstream profiles, portable-handoff coupling, performance budgets, compatibility, and release sequencing. Issue #69 retains only `check-all.sh` prerequisite discovery and diagnostic behavior.
- A discussion-completeness review found six resolved atomic decisions, two decomposed umbrella decisions, and thirteen pending atomic decisions. Issue #69 is therefore not ready for accumulated-design approval or implementation yet.
- The owner approved the `CP-1`/`CP-2`/`CP-75A` split on 2026-08-02. Issue #69 remains on the current workflow and branch through design freeze and its two implementation batches; Issue #75 will receive a separate workflow and branch after `CP-1`, beginning with architecture and benchmark evidence rather than a v0.8.0 behavior change.
- Detailed inventory and fallback/ownership evidence are retained in the English evidence files with complete owner-review translations in their `.zh-TW.md` companions.

## Discussion Contract And Decision Log

- Ask exactly one owner-decision question at a time.
- Before each question, explain the affected entrypoints, compatibility boundary, implementation/test cost, and failure-mode impact.
- Record each answer here before moving to the next decision.
- Keep the workflow active after design approval and transition directly to bounded implementation.

| Decision | Topic | Status | Owner Decision | Impact Summary |
| --- | --- | --- | --- | --- |
| `D-001` | Supported user-facing entrypoint boundary | resolved | Option A: cover all 25 production CLIs, exclude 45 direct test CLIs and four import-only modules; implement and validate the 12 portable/downstream CLIs before the 13 source-only CLIs. | Establishes complete production coverage while creating two ordered, separately reviewable implementation batches. |
| `D-002` | Diagnostic fallback and delivery architecture umbrella | decomposed | Evaluate fail-closed behavior, automatic installation, host/versioned/provider-runtime discovery, and OS-native launchers one subdecision at a time. | Prevents unlike trust, mutation, portability, and launcher questions from being collapsed into one approval. |
| `D-002A` | Default action when no fully ready environment is found | resolved | Perform read-only discovery only; if no fully ready environment exists, do not execute the target CLI, install anything, create an environment, or modify the host/repository. Fail closed with diagnostics and explicit recovery guidance. | Establishes a no-work/no-mutation terminal state while leaving separately invoked, explicitly authorized bootstrap options open for D-004. |
| `D-002B` | Trusted interpreter discovery sources and order | pending |  | Determines precedence for owner overrides, generic/versioned host commands, uv or other managers, and optional agent-tool adapters. |
| `D-002C` | OS-native launcher coverage and delegation boundary | pending |  | Determines Windows/POSIX support and whether native scripts only resolve/diagnose or duplicate Python validator semantics. |
| `D-003` | Diagnostic output and exit contract | pending |  | Defines stable fields, channel, exit status, and compatibility expectations for humans and automation. |
| `D-004` | Dependency prerequisite inventory and sanctioned recovery/install operation | pending |  | Determines whether only PyYAML or every required runtime dependency is checked, which recovery command is printed, and whether an explicit isolated bootstrap mode is offered. |
| `D-005` | Pre-mutation guarantee and proof boundary | pending |  | Determines where checks must run and which write-capable paths require negative-path evidence. |
| `D-006` | Canonical script ownership, shared prerequisite placement, package projection, and compatibility | pending |  | Determines which CLIs remain skill-owned or repo-common, where shared prerequisite code lives, what is portable, and which thin compatibility entrypoints remain. |
| `D-006A` | Workflow artifact authoring ownership | resolved | Keep only the minimum shared workflow contract at repository level. Each workflow-owning skill owns its domain-specific plan, task, report templates, and workflow semantics; do not introduce a universal workflow-author skill. | Avoids a god skill that must understand every domain template while retaining shared discovery, identity, lifecycle, and minimum task compatibility. Common validators may validate only the shared envelope and must not author domain semantics. |
| `D-006B` | Framework self-test distribution and activation boundary | resolved | Keep skill-owned acceptance validators, fixtures, and contract tests colocated with and packaged inside their owning skill. Treat them as unselected during routine downstream product development; require or explicitly select them only for source framework CI/release, framework-owned path changes, or explicit downstream framework verification/customization. | Preserves portable, auditable skill acceptance evidence without making file presence a Python runtime prerequisite. This decision does not classify `check-all.sh` or narrow target-runtime workflow/handoff validators. |
| `D-007` | Deterministic test matrix | pending |  | Determines interpreter/dependency simulation, platform coverage, and required closeout gates. |
| `D-008` | Documentation and migration communication | pending |  | Determines whether this is behavior clarification only or a documented command/contract migration. |
| `D-009` | Canonical validator runtime disposition | pending |  | Determines whether Python remains the canonical implementation under Issue #69, a runtime migration enters this workflow, or runtime replacement becomes a separate governed proposal. This must be resolved before implementation can entrench the current dependency. |
| `D-TR-001` | Corrective handling for the two primary-agent zh-TW translations | resolved | Keep the two existing translations; do not regenerate them. Require every later finalized-English-to-zh-TW derivation to use the promoted low-cost `context-translator` route and main-agent parity review. | Avoids unnecessary churn while making the future cost/routing precondition explicit and non-optional. |
| `D-010` | Downstream validation activation policy umbrella | decomposed | Separate automatic routine execution, local developer policy, CI enforcement, lifecycle safety gates, and result semantics instead of using one ambiguous Boolean. | Allows host-flexible local use without weakening explicit install, upgrade, apply, or selected CI contracts. |
| `D-010A` | Scope of the downstream activation switch | resolved | Control only automatic routine validation in the software-development flow. Do not affect a user's explicit CLI invocation or lifecycle-owned install, apply, init, upgrade, provenance, and release safety commands. | Prevents environment-sensitive routine automation from wasting tokens without turning an opt-out into a bypass for explicitly selected safety operations. |
| `D-010B` | Target-owned local default and developer override | pending |  | Determines whether local execution is disabled, manual, recommended, or required by default and where a developer-specific override may live without changing repository truth. |
| `D-010C` | Target-owned CI enforcement | pending |  | Determines how a target separately declares CI-required validation and prevents a local preference from bypassing hosted gates. |
| `D-010D` | Disabled, unavailable, and executed result semantics | pending |  | Keeps `not-run-by-policy`, `blocked-by-environment`, `failed`, and `passed` distinct so disabling a check cannot be reported as success. |
| `D-010E` | Agent prerequisite probe and retry budget | pending |  | Determines zero-attempt behavior when local automation is unselected, the maximum bounded preflight/execution attempts when selected, and the material-state-change requirement for any retry. |

## Translation Routing Deviation

- Active repository routing assigns finalized derived Traditional Chinese translations to `context-translator`; the Codex adapter selects `gpt-5.6-terra` with low reasoning.
- The primary agent instead translated `entrypoint-inventory.zh-TW.md` and `runtime-fallback-and-ownership-assessment.zh-TW.md` using `gpt-5.6-sol` with high reasoning.
- Cause: the primary agent consulted the language/governance policies but failed to discover and apply `.ai/SUB-AGENT-SYSTEM.MD` before translation. No runtime limitation required this bypass.
- Impact: structural and semantic parity checks passed, so the content is not automatically invalid, but the requested low-cost delegation contract was violated.
- `D-TR-001` is resolved without regeneration. No translation is being represented as low-cost-sub-agent output retroactively.
- For every future derived translation, the main agent must finalize the English source first, delegate exactly one source/output pair to `context-translator`, record the resolved `gpt-5.6-terra` low-reasoning route, review parity, and own the commit. If that route is unavailable, translation pauses instead of falling back to the primary model.

## Current Downstream Validation Activation State

- `check-all.sh` supports `--quick`, `--critical`, and `--full`, but these are batch-selection modes rather than an enable/disable switch.
- Python 3.11+ discovery runs before check selection. Even a mode intended to omit some checks cannot start without Python under the current implementation.
- Selected checks use repository-coded enforcement classes (`required` or `advisory`). Downstream configuration cannot currently reclassify them.
- `AI_CONTEXT_PYTHON` is only an explicit interpreter selector.
- Applicability detection can report source-only or unconfigured checks as `not applicable`; it does not express owner or developer preference.
- Installing the package does not install a downstream CI workflow or Git hook. The source repository's `portable-gates.yml` explicitly provisions Python/PyYAML and runs `--quick`; downstream teams must create their own CI integration.
- The distribution profile does not expose validators as an optional component. `.ai/scripts/**` is projected through mandatory core components, although shipping a script does not itself execute it.
- Direct Python commands and lifecycle-owned validation references exist in policies and skills. An activation policy must not silently bypass package apply, initialization, upgrade, provenance finalization, or other commands the user explicitly invokes.

## Token-Cost And Retry Finding

- `check-all.sh` contains no validation retry loop. It selects each check and invokes it once.
- The software-development orchestrator already records exact outcomes such as `blocked-by-environment` and forbids treating blocked as passed, but it defines no attempt budget and no identical-retry prohibition.
- Root execution guidance says to iterate until completion criteria pass or report blockers. That permits an Agent to report the first stable prerequisite blocker, but does not currently force it to stop before one or more redundant retries.
- A shell-only switch would be too late if the Agent has already spent tokens discovering and invoking the command. Target-owned activation policy must be read during orchestration, before Python discovery or process launch.
- The design candidate for `D-010E` is: zero probes and zero executions when local automatic validation is unselected; when selected, one bounded read-only prerequisite preflight and at most one validator execution; retry only after a recorded material state change or explicit owner instruction. This is not yet approved.

## D-010B Scenarios And Team Impact

`manual/unselected` describes automatic local orchestration, not removal of the validators. Scripts remain available, a developer may invoke them explicitly, and D-010A keeps explicit lifecycle commands outside this policy.

| Scenario | Agent behavior under the proposed local default | Team consequence |
| --- | --- | --- |
| New developer without Python/PyYAML | Read target policy, perform no interpreter probe, run no routine Python validator, and continue without claiming validation passed. | No onboarding block or repeated Agent retry/token cost; feedback must come from later developer opt-in or CI. |
| Developer with a ready environment but no personal opt-in | Do not auto-run merely because Python happens to be discoverable. | Deterministic behavior across hosts; capable developers do not unexpectedly receive stricter local automation than others. |
| Developer explicitly opts in | Perform the later-approved bounded preflight and run the selected routine validation once when ready. | Earlier local feedback for developers who accept the environment and execution cost. |
| Target repository selects local validation as required | The shared target policy overrides the framework default; missing prerequisites become a recorded local blocker. | A team can intentionally require homogeneous local tooling, but individual preferences must not weaken that tracked team rule. |
| Target CI selects validation as required | Local manual/unselected behavior remains unchanged; CI provisions its governed environment and owns the required result. | Consistent shared enforcement without requiring every workstation to match; CI feedback and branch protection become operational dependencies. |
| No local opt-in and no CI owner | Record that no automated routine validator owns the gate; never imply standards were checked. | Lowest immediate token/setup cost but highest drift risk; unsuitable for a team claiming mandatory standard enforcement. |
| Explicit package apply, init, upgrade, provenance, or release command | Ignore the local routine switch and enforce that command's own prerequisites and fail-closed contract. | Routine flexibility cannot bypass lifecycle safety. |

### Configuration And Precedence Candidate

- Store the shared target default as target-owned, versioned repository truth under a future validation-policy section of generated `.dev/project-config.yaml`; do not model it as a Python package or technology selection.
- Preserve that target decision during `ai-context-upgrader`, consistent with existing project-configuration ownership.
- Keep a developer-specific opt-in outside tracked target truth. Its exact environment-variable or ignored-local-file transport remains an implementation decision.
- Resolve precedence from strongest to weakest: explicit lifecycle invocation; target CI policy; tracked target local policy; developer local preference; framework default.
- Permit a developer preference to strengthen local execution (`manual` to automatic/required) but not weaken a tracked target or CI requirement.
- Require every Agent runtime to read the same tracked target policy before capability/test selection. A Codex-, Claude-, or Copilot-specific default must not silently diverge.

### Team Tradeoffs

- Benefit: local missing-runtime failures consume zero command attempts and avoid repeated diagnostic reasoning when automatic validation is unselected.
- Benefit: Python/PyYAML installation and supply-chain policy can be centralized in CI while motivated developers retain earlier feedback.
- Cost: defects may be discovered later in CI, increasing feedback latency, CI minutes, and pull-request iterations.
- Cost: without CI enforcement or explicit local execution, the team has availability but no effective standard gate.
- Governance requirement: an unexecuted local validator must remain visibly unexecuted; it cannot become `passed` merely because CI is expected later.
- Token requirement: moving enforcement to CI must not replace command retries with unbounded Agent polling of CI status or logs; CI observation also needs a bounded wait/read policy under D-010E.

The current D-010B recommendation is a tracked target default of `manual/unselected`, with developer-local preferences allowed only to opt into stronger local execution. D-010C separately decides whether and how CI becomes required; approval of D-010B alone does not claim that CI is configured.

## D-010B Configuration Location And Skill-Stage Impact

No opt-in path or reader is implemented today. The paths and keys below are design candidates pending D-010B approval.

### Proposed Configuration Locations

| Scope | Proposed authority and location | Reason |
| --- | --- | --- |
| Shared team default | Generated, tracked target truth at `.dev/project-config.yaml#validation.routine.local.mode` | All Agent runtimes and humans see the same default; `ai-context-init` creates it and `ai-context-upgrader` preserves it. |
| Persistent developer opt-in | Repository-local Git configuration in `.git/config`, read as `ai-context.validation.local` | Per clone, untracked, not packaged, not committed accidentally, and readable through Git before Python discovery. |
| CI enforcement | Tracked target CI policy and workflow, governed separately by D-010C | A developer-local Git setting must never weaken hosted enforcement. |

The proposed opt-in command is conceptually `git config --local ai-context.validation.local auto-if-ready`. No Agent may write that preference implicitly. A one-shot environment override is not yet proposed because another precedence source would increase ambiguity and validation cost.

### Skill And Stage Impact

| Skill or surface | Affected stage | Required behavior change |
| --- | --- | --- |
| `ai-context-governance` | This source remediation's design, implementation coordination, wrapper/policy sync, and post-remediation verification | Own the portable policy/schema changes and prove that runtime adapters do not diverge. Its own required governance validation remains outside the downstream routine switch. |
| `ai-context-init` | Step 4, generation/update of `.dev/project-config.yaml` | Materialize the shared target selection or unresolved/default state from explicit owner evidence. It does not create a personal `.git/config` opt-in. |
| `ai-context-upgrader` | Steps 3-5, comparison/reconciliation/application of target configuration | Preserve the target-owned validation policy and reconcile incoming schema additions without overwriting the target decision. Its step-5/6 required upgrade validation remains lifecycle-owned and unswitchable. |
| `software-development-orchestrator` | Step 1 intake | Read tracked target policy and the allowed local opt-in before planning validation; do not probe Python first. |
| `software-development-orchestrator` | Step 5 capability/test/validation coordination | Select or omit automatic routine validation once, enforce the D-010E attempt budget, and pass the resolved policy to implementation work. |
| `software-development-orchestrator` | Step 6 closeout and handoff | Record whether validation passed, failed, was blocked, or was unselected/deferred; never collapse an unexecuted check into success. |
| `slice-implementer` | Step 4 validation/handoff | When orchestrated, consume the resolved decision rather than independently discovering or retrying validators. In direct use, read the same target/local policy before routine automatic validation. |
| `local-change-implementer` | Step 3 narrow validation | Apply the same rule for a direct local change; a “narrowest meaningful validation” instruction cannot override an unselected routine policy or create repeated prerequisite attempts. |
| `ai-context-auditor` | Independent post-remediation assessment only | Verify routing/configuration drift and negative paths; it is not the runtime policy selector. |

### Skills Not Controlled By This Switch

- `spec-compliance-validator` remains unselected by default and fail-closed once explicitly selected by a problem-frame workflow, requirement, target policy, or owner decision.
- `code-reviewer` remains read-only and does not become a routine validator runner.
- `requirement-author`, `spec-author`, `problem-frame-author`, `bdd-gwt-test-designer`, and `ddd-ca-hex-architect` do not gain Python prerequisite execution from this policy.
- Explicit `ai-context-init`, `ai-context-upgrader`, package apply, provenance finalization, governance, release, and publication validation remains governed by each lifecycle contract, not D-010B.

### Contract And Test Radius

- Extend the target project-config template and repository configuration contract for the shared validation-policy shape.
- Update orchestrator capability, workflow-artifact, output, acceptance fixture, and deterministic test contracts.
- Update slice/local implementer validation language only enough to consume the resolved policy; do not duplicate policy parsing in every skill.
- Preserve thin Codex and Claude wrappers and validate canonical-link parity rather than copying the whole policy into wrappers.
- Add negative tests proving that `manual/unselected` causes zero interpreter probes, zero validator executions, and zero identical retries; local opt-in cannot weaken tracked target or CI requirements.

## D-010B Through D-010E Integrated Decision View

These four decisions form one control chain but remain separately approved: `D-010B` selects routine local behavior, `D-010C` assigns hosted enforcement, `D-010D` records what actually happened, and `D-010E` bounds Agent attempts and observation cost. None of them disables an explicit CLI invocation or lifecycle-owned install, apply, init, upgrade, provenance, release, or publication gate under resolved `D-010A`.

### D-010B — Local Selection And Developer Override

| Candidate local mode | Automatic Agent behavior | Team impact |
| --- | --- | --- |
| `manual/unselected` (recommended framework default) | Read policy before tool discovery; perform zero routine interpreter probes and zero routine validator executions. | Avoids onboarding and token-cost failures on heterogeneous hosts, but requires developer opt-in or CI for actual enforcement. |
| `auto-if-ready` | Run one bounded prerequisite preflight and execute once only when ready. | Gives earlier feedback on prepared hosts without requiring every developer to install Python; unavailable checks remain visible and are not passed. |
| `required` | Select the check and block the local checkpoint when it cannot run or fails. | Suitable only when the team intentionally standardizes local tooling; a personal preference cannot weaken it. |

The tracked target authority remains the future `.dev/project-config.yaml#validation.routine.local.mode`. The per-clone `.git/config` key `ai-context.validation.local` may only strengthen the target decision, such as `manual` to `auto-if-ready`; an Agent may read but never write it implicitly. This decision is requested first.

### D-010C — CI Enforcement

The candidate CI modes are `unconfigured`, `advisory`, and `required`. The framework cannot assume that a downstream target has a CI provider, so the recommended framework default is `unconfigured`; a target team that wants the validation standard should record `required` only after a real tracked CI workflow, exact command/profile, provisioned prerequisites, and durable check evidence exist.

- The proposed authority is `.dev/project-config.yaml#validation.routine.ci.mode` plus the target-owned CI workflow. A configuration value by itself does not create or prove a hosted gate.
- A required CI path may explicitly provision pinned Python and dependencies as part of the CI environment. That is planned CI provisioning, not implicit self-installation by a validator and does not weaken `D-002A`.
- Local `.git/config` cannot weaken CI. Required CI that is absent, misconfigured, blocked, or failed cannot be reported as passed or allow a required closeout.
- Issue #75 decides whether the eventual CI command is `check-all`, a source profile, or a narrow downstream profile. `D-010C` can define enforcement semantics without pre-approving that command choice.
- If branch protection or an equivalent provider merge gate is expected, it must be configured and verified separately; repository policy alone cannot enforce the remote provider setting.

### D-010D — Truthful Result Semantics

The semantic model must distinguish these states:

| State | Meaning | May count as passed? |
| --- | --- | --- |
| `not-applicable` | The target has no applicable validation surface. | No; it is an applicability result. |
| `not-run-by-policy` | The check applies but routine policy left it unselected; no prerequisite probe or execution occurred. | No. |
| `blocked-by-environment` | The check was selected but could not run because a required runtime, dependency, service, or host capability was unavailable. | No. |
| `failed` | The validator executed and reported a failing result. | No. |
| `passed` | The selected validator actually executed and produced the required success evidence. | Yes. |
| `deferred-with-owner` | A named owner explicitly accepted later handling with a follow-up. | No; it is an authorized deferral, not success. |

The current orchestrator contract already accepts `passed`, `failed`, `blocked-by-environment`, `not-applicable`, and `deferred-with-owner`, and currently uses `not-applicable` for some unselected capabilities. Adding `not-run-by-policy` directly to the required outcome enum could break strict v0.8.0 consumers. The compatibility-first candidate is to preserve the current outcome enum and add an optional machine-readable selection reason, so an unselected routine check projects as legacy `outcome: not-applicable` plus `selection_reason: not-run-by-policy`, while human output always says it was not run. Promotion to a new required top-level outcome would require separate compatibility evidence.

### D-010E — Agent Attempt, Retry, And CI-Observation Budget

The recommended budget is scoped per selected validation command, task/checkpoint, and stable material state:

- `manual/unselected`: zero interpreter probes, zero validator executions, and zero retries.
- Selected local validation: one read-only prerequisite preflight and at most one initial validator execution.
- Automatic retry: zero while executable, dependency state, policy, relevant inputs, and repository state are unchanged. After a recorded material change, permit at most one automatic retry in the same checkpoint; further attempts require explicit owner instruction.
- Material change includes an owner-installed runtime/dependency, an approved configuration change, relevant source/test correction, changed lock or package input, or a new CI run/commit. Re-reading the same error, changing only wording, or waiting without a state transition is not a material change.
- CI observation: one initial status/log read and one bounded follow-up observation. If state remains pending or unchanged, report it and stop; do not poll or re-download identical logs indefinitely.
- Record policy source, command fingerprint, prerequisite result, execution outcome, attempt count, and retry justification in the workflow/task evidence so another Agent does not repeat the same attempt after handoff.

This budget reduces repeated token and elapsed-time cost but may delay recovery from a genuinely transient failure. Explicit owner instruction remains the escape hatch; silent automatic installation remains prohibited.

## Workflow Ownership And Framework Self-Test Terminology

The owner confirmed the workflow authoring boundary under `D-006A`: the repository owns only the minimum locator, identity, lifecycle, timestamp, relationship, and minimum-task contract. Each workflow-owning skill owns its domain plan, task, report templates, and workflow semantics. A common validator may validate the shared envelope, but no universal workflow-author skill may learn or reproduce every owner's template.

`Framework self-test` is an execution-role classification, not a distribution classification. The design must keep these axes separate:

| Axis | Values requiring an explicit decision |
| --- | --- |
| Ownership | skill-owned, repo-common, or source-operation-owned |
| Distribution | source-only, packaged in a default component, or packaged in an optional development/test component |
| Activation | source CI/release, framework-path change, explicit downstream invocation, routine product development, or lifecycle handoff |
| Enforcement/result | required, explicitly selected, unselected, blocked-by-environment, failed, or passed |

Current behavior is not source-only or truly default-off:

- The distribution profile packages `.ai/assets/**`, so the canonical `software-development-orchestrator` validator, fixtures, and contract tests travel in the default `software-development-core` payload.
- The same profile packages `.ai/scripts/**` except explicit exclusions. The current exclusions do not remove `check-all.sh`, the orchestrator compatibility validator, or its compatibility tests.
- This source repository proactively executes the orchestrator contract tests from `check-all.sh --critical`.
- The portable handoff policy also requires `check-all.sh --critical`, so a downstream product workflow can currently execute those framework tests during handoff even when no framework-owned skill file changed.
- Merely packaging a dormant test would not require Python at normal skill-runtime activation. The present dependency leak comes from invocation policy and package-install/lifecycle commands, not from file presence alone.

The owner resolved `D-006B`: keep skill-owned acceptance evidence colocated with and packaged inside its skill, but leave it unselected during routine downstream product development. Source framework CI/release and framework-owned path changes may require it; downstream execution requires an explicit framework verification or customization selection. Merely packaging these files does not make Python a normal skill-runtime prerequisite.

### `check-all.sh` Follow-Up Scope

Issue #69 includes `check-all.sh` only as an affected Python entrypoint and diagnostic surface. Standardizing how that entrypoint discovers Python, reports a missing runtime/dependency, and stops before false success remains in #69. The following concerns change aggregate selection and downstream lifecycle architecture rather than prerequisite diagnostics, so they must not be implemented silently under #69:

- whether the aggregate runner belongs only to source framework CI/release;
- whether it is included in downstream packages;
- whether portable handoff policy may require it;
- whether its 30 sequential required checks should be split by changed paths, domain, or execution profile;
- performance budgets, caching, parallelism, and token-aware observation;
- replacement of full aggregate reruns with narrow workflow/checkpoint validation plus recorded target-test evidence.

The owner authorized external tracking, and `FUP-001` was created as GitHub Proposal [#75](https://github.com/YuChia-Wei/ai-collaboration-prompts-dotnet-backend/issues/75), `[Proposal] Separate check-all Aggregate Gates from Downstream Workflow Validation`, with `scope:mixed`, `kind:proposal`, `triage:needed`, and `created-by:codex`. Search found related resolved Issues #22 and #42 but no duplicate that owns this source-versus-downstream aggregate boundary. Proposal creation does not accept, promote, schedule, or authorize implementation of #75.

Narrow validators that inspect actual downstream workflow or handoff artifacts remain target-runtime validators, not framework self-tests, and still require a separate runtime/fallback decision within this workflow where they overlap Python prerequisite behavior.

## Discussion Completion Review And Release Boundary

Issue #69 is not fully discussed. The current decision ledger has this state:

| State | Decisions | Meaning |
| --- | --- | --- |
| Resolved atomic decisions (6) | `D-001`, `D-002A`, `D-006A`, `D-006B`, `D-TR-001`, `D-010A` | Production-entrypoint coverage, no-mutation failure, workflow ownership, packaged-but-unselected skill self-tests, future translation routing, and routine-switch scope are approved. |
| Decomposed umbrellas (2) | `D-002`, `D-010` | These organize subdecisions and do not themselves authorize an implementation. |
| Pending atomic decisions (13) | `D-002B`, `D-002C`, `D-003`, `D-004`, `D-005`, `D-006`, `D-007`, `D-008`, `D-009`, `D-010B`, `D-010C`, `D-010D`, `D-010E` | Interpreter trust, launcher boundary, output/exit contract, dependency recovery, pre-mutation proof, script ownership, tests, migration, canonical runtime, local policy, CI policy, result taxonomy, and retry budgets remain open. |

The remaining questions should be completed in four bounded groups while retaining the one-question-at-a-time owner contract:

1. Downstream activation and cost control: `D-010B` through `D-010E`.
2. Runtime discovery and recovery: `D-002B`, `D-002C`, `D-004`, and `D-009`.
3. Observable contract and proof: `D-003`, `D-005`, and `D-007`.
4. Ownership, package compatibility, and communication: `D-006` and `D-008`.

### Approved Intermediate Checkpoints

The owner approved the following sequence on 2026-08-02. Approval establishes workflow and release boundaries only; it does not approve the thirteen pending #69 design decisions or authorize implementation.

- `CP-1 — #69 Design Freeze`: resolve every pending #69 decision or explicitly defer it to a named issue; require `D-009` to be resolved rather than deferred; freeze the 12-entry portable contract, compatibility requirements, migration expectations, and deterministic acceptance matrix; obtain explicit accumulated-design approval; then create a durable design-freeze commit before implementation.
- `CP-2 — #69 Portable Compatibility`: implement only the 12 portable/downstream entrypoints, preserve command paths and approved exit semantics, prove clean-install and supported v0.7.0-to-v0.8.0 upgrade compatibility, and stop for owner review before touching the 13 source-only entrypoints.
- `CP-75A — #75 Architecture And Benchmark`: after `CP-1`, create a separate #75 workflow and dedicated branch. Inventory and benchmark aggregate paths and approve source/downstream profiles without changing `check-all` defaults, portable handoff behavior, or package disposition.

Discussion may continue in the same Codex task for conversational continuity, but #75 artifacts and commits should not share Issue #69's workflow or branch. This keeps acceptance criteria, rollback, PR review, and release inclusion independently controllable.

### v0.8.0 Compatibility Guardrails

- Issue #69 may add approved diagnostics and bounded discovery but must not redesign aggregate selection, package disposition, or handoff policy owned by #75.
- Preserve published command paths and thin compatibility entrypoints; removals or default changes require a separate migration and release decision.
- Do not combine #69 implementation and #75 aggregate behavior changes in one implementation batch or pull request.
- Keep the existing full source aggregate gate available until any replacement profiles have independent parity and rollback evidence.
- Require clean-install package projection and supported v0.7.0-to-v0.8.0 upgrade tests before either proposal changes portable behavior.
- Permit #75 behavior changes to move after v0.8.0 if its approved design cannot stay additive or dual-path; target-version pressure is not authorization for a breaking default change.

## Stages And Checkpoints

1. Bootstrap the governance workflow and freeze Issue #69 plus `AIC-004` as source evidence.
2. Inventory supported Python entrypoints, import timing, write potential, package inclusion, documented invocation, and current test coverage.
3. Resolve the remaining decision log one question at a time and obtain explicit approval for the accumulated design.
4. Reach `CP-1 — #69 Design Freeze`; no implementation starts before that checkpoint is completed and committed.
5. Implement and validate the approved 12-entry portable/downstream batch without broad validator redesign.
6. Reach `CP-2 — #69 Portable Compatibility`, then begin the 13-entry source-only batch only after explicit checkpoint acceptance.
7. Run focused negative-path tests, affected validator/package checks, workflow/AI-context validation, and applicable aggregate gates.
8. Request an independent `ai-context-auditor` verification assessment and reconcile `AIC-004` in the remediation report.
9. Verify commits, task state, residual risks, and close the workflow only after implementation and verification complete.

## Resume Checkpoint

- Last completed action: recorded owner approval of the `CP-1`/`CP-2`/`CP-75A` split, re-confirmed the exact 25-CLI D-001 boundary, and consolidated the pending D-010B through D-010E candidates and impacts for owner review.
- Current task: `AIC-004-diagnostic-design`.
- Exact next action: obtain only the owner decision on `D-010B`; D-010C through D-010E remain pending even though their interactions and recommendations have been presented together.
- Validation already completed: confirmed clean `main@2263744bb2dc876f8077547e961fc68be28b0074` before branching; verified the final baseline assessment; verified the inventory against `git ls-files`, direct file reads, distribution profile, shell registry, active documentation, and existing tests; parsed both task JSON files; `git diff --check`, `validate-workflow-artifacts.py`, and `validate-ai-context.py` passed.
- Current discussion-checkpoint validation: Git-history probes established the adoption timeline; the active sub-agent manifest and Codex adapter established the missed low-cost route; the changed task JSON parsed with PowerShell; locator/index state was checked directly; and `git diff --check` passed. Full Python-backed repository validators were not rerun because every discovered interpreter lacks PyYAML and D-002A now forbids implicit installation; this checkpoint records that result as `blocked-by-environment`, not passed.
- Validation environment note: generic `python` and `python3` resolve to unusable Windows aliases. A versioned uv-managed Python 3.14.1 and the Codex bundled Python 3.12.13 can start, but neither currently imports PyYAML. Prior artifact validation used Codex Python with isolated temporary `PyYAML==6.0.3`; no repository dependency files were changed.
- Git state: active branch `codex/2026-08-02-python-prerequisite-diagnostics`, created from `main@2263744bb2dc876f8077547e961fc68be28b0074`; the latest durable design checkpoint entering this discussion is `1a66897`.
- Branch history and checkpoint handoffs: bootstrap commits `88a01be` and `4e93c0f`; absent-interpreter boundary `cd58c2b`; inventory translation `d27fb8a`; D-001/fallback assessment `d5ae808`; runtime rationale and D-002A `9937fb4`; downstream switch gap `7fa102c`; activation/retry scope `74bb024`; D-010B team scenarios `c2b35ad`; opt-in location and skill-stage map `32ede97`; workflow ownership and self-test terminology `22e6883`; self-test boundary and FUP scope `ac2d9d7`; staged #69/#75 scope boundary `1a66897`; no push or merge handoff has occurred.
- Blockers or unresolved decisions: thirteen atomic #69 decisions remain unresolved; the checkpoint/branch separation is approved. Implementation edits are paused pending explicit accumulated-design approval. Proposal #75 is externally tracked but not accepted, promoted, scheduled, or authorized for implementation.

## Branch Lifecycle

| Segment | Branch | Base | Checkpoint Type | Commit | Remote / Target | Recorded At | Reason | Resume Branch / Action |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `codex/2026-08-02-python-prerequisite-diagnostics` | `main@2263744bb2dc876f8077547e961fc68be28b0074` | bootstrap | `88a01bebfe95f696763c1b310c363f354949f205` | local | `2026-08-02T10:45:48+08:00` | Preserve the authorized workflow and initial impact inventory before owner decisions. | Ask `D-001`; keep implementation pending until the accumulated design is explicitly approved. |
| 1 | `codex/2026-08-02-python-prerequisite-diagnostics` | `main@2263744bb2dc876f8077547e961fc68be28b0074` | design evidence | `cd58c2b0391dccb4a8487f33938b8a3c5d060500` | local | `2026-08-02T10:57:23+08:00` | Preserve the observed absent-interpreter boundary without resolving D-001 or D-002. | Provide the requested complete zh-TW inventory, then ask only `D-001`. |
| 1 | `codex/2026-08-02-python-prerequisite-diagnostics` | `main@2263744bb2dc876f8077547e961fc68be28b0074` | owner-review translation | `d27fb8adbaf890f9f926c2de6bf66aa6917a83d0` | local | `2026-08-02T11:05:29+08:00` | Preserve the complete Traditional Chinese Taiwan inventory used for the D-001 owner decision. | Record D-001 and evaluate fallback/ownership before asking D-002A. |
