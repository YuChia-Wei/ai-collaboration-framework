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
- `updated_at`: `2026-08-02T20:01:06+08:00`
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
- The owner also authorized external tracking for the generalized host/Agent capability idea. GitHub Proposal [#76](https://github.com/YuChia-Wei/ai-collaboration-prompts-dotnet-backend/issues/76), `[Proposal] Add Environment Readiness Profiles for Host and Agent Capabilities`, now owns the proposed readiness skill, ignored local result, target execution/permission policy, consuming-skill prerequisite declarations, and policy-governed workspace-edit fallback. Issue #69 does not add a general readiness profile or make it a Python prerequisite.
- A discussion-completeness review found six resolved atomic decisions, two decomposed umbrella decisions, and thirteen pending atomic decisions. Issue #69 is therefore not ready for accumulated-design approval or implementation yet.
- The owner approved the `CP-1`/`CP-2`/`CP-75A` split on 2026-08-02. Issue #69 remains on the current workflow and branch through design freeze and its two implementation batches; Issue #75 will receive a separate workflow and branch after `CP-1`, beginning with architecture and benchmark evidence rather than a v0.8.0 behavior change.
- Detailed inventory and fallback/ownership evidence are retained in the English evidence files with complete owner-review translations in their `.zh-TW.md` companions.

## Discussion Contract And Decision Log

- Ask exactly one owner-decision question at a time.
- Before each question, explain the affected entrypoints, compatibility boundary, implementation/test cost, and failure-mode impact.
- Record each answer here before moving to the next decision.
- When only three atomic decisions remain, preview all three and their impacts together, then continue requesting only one owner decision at a time.
- Keep the workflow active after design approval and transition directly to bounded implementation.

| Decision | Topic | Status | Owner Decision | Impact Summary |
| --- | --- | --- | --- | --- |
| `D-001` | Supported user-facing entrypoint boundary | resolved | Option A: cover all 25 production CLIs, exclude 45 direct test CLIs and four import-only modules; implement and validate the 12 portable/downstream CLIs before the 13 source-only CLIs. | Establishes complete production coverage while creating two ordered, separately reviewable implementation batches. |
| `D-002` | Diagnostic fallback and delivery architecture umbrella | decomposed | Evaluate fail-closed behavior, automatic installation, host/versioned/provider-runtime discovery, and OS-native launchers one subdecision at a time. | Prevents unlike trust, mutation, portability, and launcher questions from being collapsed into one approval. |
| `D-002A` | Default action when no fully ready environment is found | resolved | Perform read-only discovery only; if no fully ready environment exists, do not execute the target CLI, install anything, create an environment, or modify the host/repository. Fail closed with diagnostics and explicit recovery guidance. | Establishes a no-work/no-mutation terminal state while leaving separately invoked, explicitly authorized bootstrap options open for D-004. |
| `D-002B` | Trusted interpreter discovery sources and order | resolved | Use deterministic read-only discovery in this order: explicit `AI_CONTEXT_PYTHON`; active environment and stable generic PATH commands; versioned PATH commands; one optional installed-uv managed-Python fallback using `uv python find --managed-python --no-python-downloads --offline --no-config --no-project ">=3.11"`; then fail closed. Validate and deduplicate every resolved executable before selection. Do not automatically scan Agent-tool private runtime paths; an owner may still select one explicitly through `AI_CONTEXT_PYTHON`. | Finds uv-managed Python that lacks a PATH shim without making uv or an Agent product a prerequisite, downloading Python, mutating an environment, or depending on provider-private layouts. |
| `D-002C` | OS-native launcher coverage and delegation boundary | resolved | Provide POSIX-sh and Windows-PowerShell thin launchers as stable compatibility entrypoints. They implement only the approved read-only interpreter/dependency preflight and diagnostics, then delegate validator semantics to the canonical Python implementation; do not create a parallel `check-all.ps1` or duplicate validator behavior. The launchers and their fallback must work without Proposal #76. Treat embedded discovery as a replaceable transitional fallback: a future approved readiness result may be consumed additively, but removing fallback logic or either launcher requires separate evidence, migration, compatibility, and release approval. | Gives Windows and POSIX users a native bootstrap even when no Agent/readiness profile is available, while keeping validation truth in one implementation. Python and required dependencies remain necessary for actual validation; two small adapters and their platform tests become maintained compatibility surfaces. |
| `D-003` | Diagnostic output and exit contract umbrella | resolved | Resolve human/machine fields and channels through `D-003A` and compatibility-first numeric behavior through `D-003B`. | Adds stable semantic diagnostics without silently changing existing shell/CI control flow. |
| `D-003A` | Human and machine diagnostic fields and channels | resolved | For known prerequisite failures, default to one compact human diagnostic on `stderr`, suppress expected Python tracebacks, and leave every successful command's existing `stdout` unchanged. Support an explicit common `--diagnostic-format=json` mode that emits exactly one compact, schema-versioned JSON object on `stdout` with no duplicate human message. Both projections carry outcome `blocked-by-environment`, stable reason code, entrypoint, required Python floor, bounded/deduplicated candidate results, resolved executable/version when known, missing governed requirements and requirements path, `mutation_started=false`, and non-executing recovery guidance. | Gives humans actionable output and lets CI/Agents parse one stable object without scraping tracebacks or consuming duplicate diagnostics. Adds shared schema plus Python/POSIX/PowerShell projection tests, but does not decide numeric exit status. |
| `D-003B` | Numeric exit-code compatibility | resolved | Keep `0` success-only and preserve each existing entrypoint's current or closest existing prerequisite-failure code for v0.8.0. Store that compatibility mapping with the entrypoint contract. A new POSIX-sh or Windows-PowerShell launcher uses the target entrypoint's mapped code when preflight blocks delegation and propagates the validator's code unchanged after delegation. Do not introduce one new global prerequisite exit code in v0.8.0; `outcome` and `reason_code` from `D-003A` are authoritative for precise automation semantics. Any later numeric normalization requires downstream observation and a separate breaking-change decision. | Avoids breaking scripts that currently observe exit `1` from `check-all.sh` or exit `2` from the package planner while giving new launchers deterministic parity. Numeric inconsistency remains temporarily, so detailed consumers must use the JSON contract rather than infer cause from the number. |
| `D-004` | Dependency prerequisite inventory and sanctioned recovery/install operation umbrella | resolved | Resolve exact per-entrypoint dependency profiles through `D-004A` and documentation-only recovery through `D-004B`. | Separates read-only readiness and actionable documentation from any network, installation, or environment mutation; no executable bootstrap is part of Issue #69. |
| `D-004A` | Per-entrypoint dependency readiness profile | resolved | Check the Python 3.11+ floor for all 25 production CLIs. Check governed `PyYAML==6.0.3` readiness only for the 23 CLIs that require it directly or indirectly; do not block the two standard-library-only CLIs on PyYAML. Treat `tomllib` as covered by the Python version floor. Maintain a machine-readable entrypoint-to-dependency profile and verify it against imports, the governed requirements declaration, and package projection so future runtime dependencies cannot be silently omitted. | Avoids adding PyYAML as a false prerequisite to `.ai/scripts/validate-dependency-versions.py` and `.ai/assets/skills/ai-context-upgrader/scripts/compare-ai-context-versions.py`, while making dependency drift a contract failure instead of a raw import error. This decision remains read-only and does not authorize installation. |
| `D-004B` | Recovery guidance and explicit isolated bootstrap boundary | resolved | Provide human-facing installation documentation and deterministic, non-executing recovery guidance. Identify the selected interpreter/version, exact missing governed dependency, resolved requirements path, and a copyable command bound to the selected interpreter. Launcher and validator paths must not run `pip` or `uv`, create an environment, access the network, write recovery state, or retry after unchanged failure. The guide may describe owner-executed existing-environment or isolated-environment steps, but Issue #69 provides no executable bootstrap. Enterprise package-source, certificate, proxy, permission, and approval rules remain target/team authority. | Gives developers and CI an actionable next step without hidden mutation or supply-chain assumptions. Environment preparation remains a deliberate human, target, or CI responsibility; future policy-aware assistance belongs to separately approved Proposal #76 rather than this validator path. |
| `D-005` | Pre-mutation guarantee and proof boundary | resolved | Run prerequisite preflight before domain code, local modules, or PyYAML imports on all 25 production CLIs, and disable Python bytecode writing before local imports. On missing Python, an unsupported version, or a missing governed dependency, leave repository-controlled worktree/index, target/package, and output surfaces unchanged; create no `__pycache__` or `.pyc`; start no write-capable domain subprocess; and emit `mutation_started=false` in JSON mode. Require negative-path no-write evidence for every write-capable CLI and no-false-success/no-bytecode evidence for read-only CLIs across direct Python, POSIX-sh, Windows-PowerShell, and portable-package paths. Limit the guarantee to repository-controlled filesystem state, declared target/output paths, and observable subprocesses. | Converts “stop before mutation” into a testable boundary while avoiding unverifiable claims about OS access times, security telemetry, or third-party internal logs. It requires bootstrap-before-import refactoring and focused negative-path coverage but does not authorize implementation yet. |
| `D-006` | Canonical script ownership, shared prerequisite placement, package projection, and compatibility | resolved | Preserve the current two canonical skill-owned production scripts, one repo-level thin compatibility path, and 22 repo-common scripts; move or remove none in v0.8.0. Add repo-common `.ai/scripts/python_prerequisites.py`, `.ai/scripts/python-entrypoints.json`, `.ai/scripts/run-python-entrypoint.sh`, and `.ai/scripts/run-python-entrypoint.ps1`. Keep domain behavior/tests with their owning skills, project the shared component and both generic launchers with the 12 portable CLIs, retain the 13 source-only classifications, and preserve every existing direct Python command. Let `check-all.sh` reuse one POSIX discovery result. Keep only the unavoidable no-Python discovery/projection logic native in sh and PowerShell and enforce parity with the canonical registry. Missing or mismatched shared assets fail closed. | Centralizes the cross-skill prerequisite contract without creating a new skill, moving domain behavior, multiplying per-CLI OS wrappers, or breaking published paths. Downstream packages gain four managed shared files but no automatic invocation or installation; skill-owned CLIs acquire a declared framework dependency on the shared component. |
| `D-006A` | Workflow artifact authoring ownership | resolved | Keep only the minimum shared workflow contract at repository level. Each workflow-owning skill owns its domain-specific plan, task, report templates, and workflow semantics; do not introduce a universal workflow-author skill. | Avoids a god skill that must understand every domain template while retaining shared discovery, identity, lifecycle, and minimum task compatibility. Common validators may validate only the shared envelope and must not author domain semantics. |
| `D-006B` | Framework self-test distribution and activation boundary | resolved | Keep skill-owned acceptance validators, fixtures, and contract tests colocated with and packaged inside their owning skill. Treat them as unselected during routine downstream product development; require or explicitly select them only for source framework CI/release, framework-owned path changes, or explicit downstream framework verification/customization. | Preserves portable, auditable skill acceptance evidence without making file presence a Python runtime prerequisite. This decision does not classify `check-all.sh` or narrow target-runtime workflow/handoff validators. |
| `D-007` | Deterministic test matrix | resolved | Use a layered, non-Cartesian matrix. Exhaustively simulate prerequisite states once at the shared bootstrap layer; validate registry, dependency profile, exit mapping, and one representative blocked smoke for all 25 CLIs; require full no-write evidence for every write-capable CLI; and preserve ready-path domain tests. Gate the 12 portable CLIs on extracted-package, clean-install, and supported v0.7-to-v0.8 upgrade compatibility at CP-2, then test the 13 source-only CLIs in the second batch. Require focused native Windows/PowerShell and Ubuntu/POSIX-sh contract jobs; macOS is not a v0.8.0 required gate. Test cases use deterministic stubs, fixtures, and temporary directories without installing, downloading, or accessing the network. Keep `check-all --full` outside the #69 acceptance gate; retain the existing quick regression plus focused prerequisite suites. | Proves discovery, diagnostics, compatibility, and D-005 no-mutation behavior without multiplying every CLI by every failure state and OS. It adds one focused Windows source-CI surface and portable-package gates, but does not impose CI or validation defaults on downstream product repositories. |
| `D-008` | Documentation and migration communication | pending |  | Determines whether this is behavior clarification only or a documented command/contract migration. |
| `D-009` | Canonical validator runtime disposition | resolved | Retain Python 3.11 or newer as the canonical validator implementation for Issue #69 and v0.8.0. Keep the POSIX-sh and Windows-PowerShell launchers as prerequisite/diagnostic adapters rather than validator rewrites. Do not migrate runtime in this workflow and do not automatically create a replacement issue now. This is a bounded release decision, not a permanent prohibition: any later runtime replacement requires a separate governed proposal, evidence-backed technology/distribution comparison, compatibility migration, and explicit owner approval. | Keeps #69 additive and reviewable across the 25 current Python CLIs without expanding v0.8.0 into a multi-platform rewrite. Python/PyYAML remain prerequisites where selected, mitigated by manual routine defaults, target CI provisioning, native launchers, and documentation-only recovery. |
| `D-TR-001` | Corrective handling for the two primary-agent zh-TW translations | resolved | Keep the two existing translations; do not regenerate them. Require every later finalized-English-to-zh-TW derivation to use the promoted low-cost `context-translator` route and main-agent parity review. | Avoids unnecessary churn while making the future cost/routing precondition explicit and non-optional. |
| `D-010` | Downstream validation activation policy umbrella | resolved | Resolve through `D-010A` routine-only scope, `D-010B` tracked-manual/local-opt-in selection, `D-010C` target-owned CI enforcement, `D-010D` compatibility-safe truthful outcomes, and `D-010E` bounded attempts and CI observation. | Completes one coherent control chain that limits local token cost without weakening explicit lifecycle or selected CI contracts. |
| `D-010A` | Scope of the downstream activation switch | resolved | Control only automatic routine validation in the software-development flow. Do not affect a user's explicit CLI invocation or lifecycle-owned install, apply, init, upgrade, provenance, and release safety commands. | Prevents environment-sensitive routine automation from wasting tokens without turning an opt-out into a bypass for explicitly selected safety operations. |
| `D-010B` | Target-owned local default and developer override umbrella | resolved | Resolve through `D-010B1` tracked `manual` default and `D-010B2` ignored strict `.dev/validation.local.conf` personal opt-in. | Establishes one cross-Agent local policy with a visible, pre-Python personal strengthening path and no hidden Git-config requirement. |
| `D-010B1` | Target-owned routine local default | resolved | Use tracked target mode `manual`: routine local validation is applicable but unselected by default; explicit CLI and lifecycle commands remain unaffected. | Heterogeneous developer hosts perform zero automatic prerequisite probes or routine validator executions until target policy or an allowed developer opt-in selects them. |
| `D-010B2` | Developer-local opt-in storage and transport | resolved | Use ignored `.dev/validation.local.conf` as the only persistent personal opt-in. Require the exact `/.dev/validation.local.conf` ignore rule, a strict one-line `validation.routine.local=<approved-mode>` data parser, monotonic strengthening only, no implicit Agent writes, and no environment-variable override in v0.8.0. | Keeps the preference visible and cross-Agent without reintroducing Python/YAML bootstrap, while adding explicit init, upgrade, ignore, package, native-reader, and negative-path test obligations. |
| `D-010C` | Target-owned CI enforcement | resolved | Use framework default `unconfigured`; allow a target to explicitly select `advisory` or `required` in tracked `.dev/project-config.yaml#validation.routine.ci.mode`. Treat `required` as valid only with a real tracked CI workflow, exact command/profile, provisioned prerequisites, durable check evidence, and separately verified provider merge-gate settings when merge blocking is claimed. Developer-local settings cannot weaken CI; absent, misconfigured, blocked, or failed required CI is never passed. | Avoids inventing CI for downstream targets while allowing teams to centralize Python/PyYAML provisioning and mandatory validation. Issue #75 retains command/profile selection, so this decision does not prescribe `check-all`. |
| `D-010D` | Disabled, unavailable, and executed result semantics | resolved | Preserve the v0.8.0 top-level outcome enum. Project an applicable-but-unselected check as legacy `outcome: not-applicable` plus optional `selection_reason: not-run-by-policy`; human output must say “not run by policy”, and required gates may never treat it as passed. Require schema, package, and v0.7-to-v0.8 compatibility tests, observe downstream consumers, and make any later promotion to a top-level outcome a separate change. | Retains semantic truth for new consumers while minimizing breakage for strict existing consumers that only know the current outcome enum. |
| `D-010E` | Agent prerequisite probe and retry budget | resolved | Scope the budget per selected command, task/checkpoint, and stable material state: unselected means zero probes/executions/retries; selected local validation gets one read-only preflight and at most one initial execution; unchanged state gets no automatic retry; one material change permits at most one automatic retry; CI gets one initial read and one bounded follow-up. Further attempts require explicit owner instruction, and evidence records the policy source, command fingerprint, prerequisite result, outcome, attempt count, and retry reason. | Prevents repeated prerequisite and CI polling loops from wasting tokens while retaining an explicit, auditable recovery path after real state changes. |

## Translation Routing Deviation

- Active repository routing assigns finalized derived Traditional Chinese translations to `context-translator`; the Codex adapter selects `gpt-5.6-terra` with low reasoning.
- The primary agent instead translated `entrypoint-inventory.zh-TW.md` and `runtime-fallback-and-ownership-assessment.zh-TW.md` using `gpt-5.6-sol` with high reasoning.
- Cause: the primary agent consulted the language/governance policies but failed to discover and apply `.ai/SUB-AGENT-SYSTEM.MD` before translation. No runtime limitation required this bypass.
- Impact: structural and semantic parity checks passed, so the content is not automatically invalid, but the requested low-cost delegation contract was violated.
- `D-TR-001` is resolved without regeneration. No translation is being represented as low-cost-sub-agent output retroactively.
- For every future derived translation, the main agent must finalize the English source first, delegate exactly one source/output pair to `context-translator`, record the resolved `gpt-5.6-terra` low-reasoning route, review parity, and own the commit. If that route is unavailable, translation pauses instead of falling back to the primary model.

## D-002B Trusted Interpreter Discovery

The owner approved this deterministic candidate order:

1. An explicit owner-provided `AI_CONTEXT_PYTHON` executable.
2. The active environment and stable generic Python commands already exposed through `PATH`.
3. Versioned Python commands exposed through `PATH`; exact Windows and POSIX command names remain owned by `D-002C`.
4. One optional installed-uv probe for an already installed managed Python:

   ```text
   uv python find --managed-python --no-python-downloads --offline --no-config --no-project ">=3.11"
   ```

5. The fail-closed diagnostic approved by `D-002A` when no fully ready candidate remains.

Every returned executable must start, satisfy the Python 3.11-or-newer constraint retained by `D-009`, and pass the required-import probe before selection. Resolve and deduplicate physical executable identities so a PATH shim and uv-managed installation do not trigger duplicate prerequisite work.

The uv probe is optional, read-only, and non-fatal as an individual source. If uv is missing, blocked, or returns no installed candidate, record that source once and continue without retry under `D-010E`. The adapter must not invoke `uv run`, `uvx`, `uv sync`, `uv python install`, or any download/install behavior. Official uv documentation confirms that Python download is otherwise automatic in some discovery flows, which is why `--no-python-downloads` and `--offline` are mandatory here: [Python versions](https://docs.astral.sh/uv/concepts/python-versions/) and [CLI reference](https://docs.astral.sh/uv/reference/cli/).

No automatic Codex, Claude Code, ChatGPT Desktop, or other Agent-product private-runtime scan is approved for v0.8.0. An owner may still point `AI_CONTEXT_PYTHON` at such an executable explicitly; that preserves owner trust without making provider-private paths part of the portable repository contract.

Local read-only evidence on 2026-08-02 used uv 0.11.29 with the approved safety flags and resolved its installed managed CPython 3.14.1. The same installation is also exposed as `python3.14` on PATH, and both identities lack PyYAML, proving that interpreter discovery and dependency readiness remain separate. The WinGet uv link required sandbox approval in the current Agent environment, reinforcing that uv must remain a bounded fallback rather than a prerequisite or first candidate.

## D-002C OS-Native Launcher And Transition Boundary

The owner approved a POSIX-sh launcher and a Windows-PowerShell launcher as stable compatibility entrypoints. Each launcher may perform only the read-only prerequisite discovery approved by `D-002A` and `D-002B`, produce the diagnostic contract later resolved by `D-003`, and delegate actual validator semantics to the canonical Python implementation retained by `D-009`. They must not duplicate validator rules, become OS-native validator rewrites, or introduce `check-all.ps1` under Issue #69.

The launchers are self-contained bootstrap/fallback paths and cannot require Proposal #76, an Agent runtime, or a pre-existing readiness result. Their embedded discovery is nevertheless a replaceable transitional implementation detail. If Proposal #76 is later approved and implemented, the launchers may first consume a fresh compatible readiness result and retain bounded direct discovery when that result is missing, stale, or unavailable.

Completion of a readiness skill does not itself authorize deleting these entrypoints. Removing duplicated discovery requires evidence that supported local, CI, non-Agent, and downstream package scenarios retain a usable bootstrap plus explicit migration approval. Removing either published launcher is a stronger compatibility change and requires a separate release decision after consumers have migrated; it is not part of the v0.8.0 #69 implementation.

## D-003A Diagnostic Output Projection

The owner approved two mutually exclusive projections for known prerequisite failures:

- Default human mode emits one compact actionable diagnostic on `stderr`, suppresses the expected interpreter/import traceback, and does not add prerequisite text to `stdout`.
- Explicit `--diagnostic-format=json` mode emits exactly one compact schema-versioned JSON object on `stdout` and no duplicate human diagnostic. The shared launcher/bootstrap must consume this option before domain-specific argument parsing and project the same contract from direct Python, POSIX-sh, and Windows-PowerShell paths.

Successful commands retain their existing stdout/stderr behavior. Both failure projections carry the same semantics: `blocked-by-environment`; a stable reason code such as no interpreter, unsupported version, or missing governed dependency; entrypoint; required Python floor; bounded and physically deduplicated candidate results; resolved executable/version when available; exact missing requirement and governed requirements path; `mutation_started=false`; and the documentation-only recovery guidance approved by `D-004B`. Candidate detail must be sufficient to explain the terminal choice but bounded so discovery does not create unbounded logs or Agent token cost.

The JSON object requires an explicit schema version and deterministic field types/order for fixtures, while consumers must use field names rather than textual ordering. Expected prerequisite failures must not include a traceback in either projection. `D-003A` does not select a numeric exit status; current-code compatibility and new launcher behavior remain pending in `D-003B`.

## D-003B Compatibility-First Exit Codes

The owner approved compatibility-first numeric exit behavior for v0.8.0. Exit `0` remains success-only. Existing production entrypoints retain their current or closest existing prerequisite-failure code, including the observed `check-all.sh` missing-interpreter code `1` and package-planner missing-PyYAML code `2`; the complete 25-entrypoint mapping must be recorded with the governed entrypoint contract and locked by compatibility fixtures.

When a new native launcher blocks before Python delegation, it returns the mapped code for the requested target entrypoint. Once delegation begins, the launcher propagates the validator's exit code unchanged. Usage errors, domain validation failures, and prerequisite failures may therefore share a numeric value in an existing CLI; detailed automation must use the schema-versioned `outcome` and `reason_code` approved by `D-003A` rather than infer a cause from the number alone.

Issue #69 and v0.8.0 do not introduce a global prerequisite code. A later normalization may be proposed only after downstream observation identifies consumers, migration impact, and a compatible release path; it is not implied by completing this workflow.

## D-004A Dependency Profile Boundary

The owner approved exact dependency readiness by entrypoint rather than applying the complete repository `requirements.txt` to every command. All 25 production CLIs require the retained Python 3.11-or-newer floor. The 23 CLIs that directly or indirectly import YAML behavior additionally require the governed `PyYAML==6.0.3` package; the following two standard-library-only production CLIs do not:

- `.ai/scripts/validate-dependency-versions.py`
- `.ai/assets/skills/ai-context-upgrader/scripts/compare-ai-context-versions.py`

The Python version gate supplies `tomllib`, so it is a runtime-version capability rather than a separately installable dependency. Implementation must use a machine-readable entrypoint-to-dependency profile and add consistency evidence against the actual direct/indirect import boundary, canonical requirements declaration, portable package projection, and compatibility entrypoints. A future dependency addition that is absent from the profile must fail contract validation before release instead of surfacing later as an unclassified import failure.

`D-004A` authorizes only read-only readiness probes and exact missing-dependency identification. It does not authorize `pip`, `uv`, network access, environment creation, repository writes, or any other recovery mutation; resolved `D-004B` permits documentation-only guidance and explicitly excludes those mutations.

## D-004B Documentation-Only Recovery Boundary

The owner approved installation documentation and deterministic recovery guidance without any executable bootstrap in Issue #69. When a governed dependency is missing, the diagnostic must identify the selected executable and version, the exact missing requirement, the source- or package-relative governed requirements file, and a copyable command equivalent to:

```text
"<resolved-python>" -m pip install -r "<resolved-requirements-file>"
```

The command is guidance only. Neither a direct Python entrypoint nor the POSIX-sh, Windows-PowerShell, or aggregate launcher may execute it, invoke `pip` or `uv`, create or activate a virtual environment, access a package source, write recovery state, or automatically retry after the unchanged prerequisite failure. The human-facing guide may separately explain how an owner can use an existing approved environment or create an isolated environment, but those remain explicit owner actions outside validator execution.

If `pip` is unavailable or an enterprise policy requires an internal index, certificate, proxy, administrator approval, or another provisioning process, the diagnostic must remain fail-closed and point to organization/target instructions without inventing credentials or alternative sources. A future approved Proposal #76 may offer policy-aware preparation assistance, but it cannot retroactively make #69 installation automatic.

## D-005 Verifiable Pre-Mutation Boundary

The owner approved a single pre-mutation contract for all 25 production CLIs. Each Python entrypoint must enter a minimal prerequisite bootstrap before importing domain modules, repository-local modules, or PyYAML. That bootstrap must disable bytecode writing before any repository-local import. When Python itself cannot start, the approved POSIX-sh or Windows-PowerShell launcher owns the equivalent interpreter-discovery failure boundary.

For missing Python, an interpreter below 3.11, or a missing governed dependency, the implementation must prove all of the following:

- The Git worktree and index are unchanged.
- A downstream target repository and an extracted portable package are unchanged.
- Declared output, plan, release, migration, and evaluation paths are neither created nor modified.
- No `__pycache__` directory or `.pyc` file is created.
- No domain subprocess capable of writes is started.
- JSON diagnostics report `mutation_started=false`; this field may not be emitted as false unless the boundary is satisfied.

Every write-capable production CLI requires a negative-path no-write test. Read-only CLIs require evidence that an unsupported or unready environment cannot produce false success and cannot create bytecode. Coverage must include direct Python invocation, the POSIX-sh launcher, the Windows-PowerShell launcher, and execution from an extracted portable package; `D-007` will define the layered matrix and required platform gates without multiplying every state across every CLI.

This guarantee covers repository-controlled filesystem state, declared target/output paths, and observable subprocess creation. It intentionally does not claim control over OS-maintained access timestamps, endpoint-security or audit telemetry, shell history, or opaque internal logging performed by an interpreter or third-party tool. Read-only executable discovery and version/dependency probes are permitted within that bounded exception.

## D-006 Script Ownership And Shared Prerequisite Component

The owner approved the current physical ownership classification without relocation:

- Keep `.ai/assets/skills/software-development-orchestrator/scripts/validate-software-development-orchestrator-acceptance.py` and `.ai/assets/skills/ai-context-upgrader/scripts/compare-ai-context-versions.py` canonical and skill-owned.
- Keep `.ai/scripts/validate-software-development-orchestrator-acceptance.py` as the thin published compatibility path to the orchestrator-owned validator.
- Keep the other 22 production CLIs repo-common because their package, workflow, release, provider, or governance behavior crosses skill boundaries.

The cross-cutting prerequisite contract is repo-common rather than a new skill or a responsibility of either skill-owned CLI. Implementation must add these stable paths:

- `.ai/scripts/python_prerequisites.py`: standard-library-only canonical Python bootstrap and diagnostic behavior after an interpreter can start.
- `.ai/scripts/python-entrypoints.json`: canonical 25-entrypoint dependency, distribution, and compatibility exit-code registry.
- `.ai/scripts/run-python-entrypoint.sh`: generic stable POSIX entrypoint.
- `.ai/scripts/run-python-entrypoint.ps1`: generic stable Windows PowerShell entrypoint.

The two generic launchers avoid 25 per-CLI wrapper pairs. Existing direct `python <script>.py` paths remain supported, and no canonical or compatibility CLI is removed or renamed in v0.8.0. `check-all.sh` must reuse one POSIX discovery result for its selected batch rather than preflight each nested Python command independently.

The Python module and registry own dependency and diagnostic semantics. Because Python absence must be diagnosed before that module can run, the POSIX and PowerShell adapters necessarily retain a small native interpreter-discovery and diagnostic projection. That bounded duplication may not acquire validator semantics and must be checked against the canonical registry for entrypoint identity and prerequisite exit-code parity.

The shared module, registry, and both launchers are managed portable framework assets and must be projected whenever the 12 portable CLIs are projected. The 13 source-only CLI classifications remain unchanged. Skill-owned scripts declare and consume the shared framework dependency while retaining their own domain behavior, fixtures, and acceptance tests under `D-006B`; repo-common bootstrap/registry tests remain under `.ai/scripts/tests/`.

If a dependent CLI is present without the required shared module, registry, or matching registry entry, source and package validation must fail closed before domain import. It may not silently fall back to a raw import traceback, embedded stale profile, automatic install, or unregistered direct execution.

## D-007 Layered Deterministic Test Matrix

The owner approved a layered matrix instead of a 25-entrypoint by prerequisite-state by operating-system Cartesian product:

1. Shared bootstrap contract tests simulate no interpreter, an unusable alias or candidate, Python below 3.11, Python 3.11 or newer with a missing governed dependency, a fully ready interpreter, duplicate PATH/uv identities, and missing, blocked, or empty installed-uv discovery. They verify human and JSON projections, candidate bounding/deduplication, per-entrypoint exit mapping, no unchanged-state retry, and the no-install/no-network boundary.
2. Registry and entrypoint contract tests cover all 25 production CLIs, their 23 PyYAML-bearing and two standard-library-only profiles, portable/source classification, compatibility path, and exit mapping. Every CLI receives at least one representative blocked subprocess smoke so import ordering and no-false-success behavior are executable evidence rather than registry claims alone.
3. Every write-capable CLI receives the full `D-005` filesystem/output/subprocess negative-path proof. Existing or focused ready-path domain tests continue to own validator semantics; prerequisite tests do not duplicate those semantics.
4. The 12 portable CLIs must pass source-tree and extracted-package coverage plus clean-install and supported v0.7.0-to-v0.8.0 upgrade compatibility before CP-2. The 13 source-only CLIs remain the separately reviewable second implementation batch.
5. Source CI requires a focused native Windows job for PowerShell and Windows command/alias behavior and a focused Ubuntu job for POSIX-sh behavior. macOS coverage may be advisory but is not a v0.8.0 closeout gate. A missing required platform result is `blocked-by-environment`, never passed.

Fixtures, stubs, and temporary directories must model failure states; tests must not uninstall host tools or perform installation, downloads, environment creation, or network access. Source CI may continue explicitly provisioning its pinned ready-path dependencies before the suite, but the tested launcher and recovery paths cannot do so.

Issue #69 does not require `check-all.sh --full` as an acceptance gate. The current quick regression remains available, and focused prerequisite/portable suites become the #69 evidence. Aggregate composition, runtime budget, and any later full-gate replacement remain owned by Proposal #75.

## D-009 Canonical Runtime Scope

The owner decided not to replace the validator runtime in Issue #69 or v0.8.0. Python 3.11 or newer remains the canonical implementation for all 25 production CLI paths, with the exact per-entrypoint dependency profile approved by `D-004A`. The POSIX-sh and Windows-PowerShell surfaces approved by `D-002C` remain thin prerequisite and diagnostic adapters; they do not acquire validator semantics.

This decision limits the current release rather than declaring Python permanent. A later move to .NET, a self-contained binary, another language runtime, or another distribution model would need a separate governed proposal covering platform and architecture support, build/restore requirements, artifact integrity and signing, release/update mechanics, CI, source provenance, semantic parity for all affected CLIs, compatibility entrypoints, migration, and rollback. No such follow-up issue is created automatically from this decision.

Proposal #76 may later report runtime availability or policy, but it cannot change the canonical implementation or authorize a migration. Issue #69 may implement only the Python-centered diagnostic architecture already bounded by the approved native launchers, manual routine activation, CI ownership, and documentation-only recovery decisions.

## General Environment Readiness Follow-Up Boundary

The owner approved separating the generalized environment-readiness capability from Issue #69. `FUP-002` is externally tracked as GitHub Proposal [#76](https://github.com/YuChia-Wei/ai-collaboration-prompts-dotnet-backend/issues/76), `[Proposal] Add Environment Readiness Profiles for Host and Agent Capabilities`, with `scope:mixed`, `kind:proposal`, `triage:needed`, and `created-by:codex` labels. Duplicate searches for environment readiness, local profiles, `apply_patch`, PowerShell file editing, and .NET build/test diagnostics found no open issue owning the same boundary.

Proposal #76 owns evaluation of:

- a possible `assess-environment-readiness` skill and ignored machine-local readiness result;
- separate `available`, `allowed`, and `verified` evidence for host tools, Agent-runtime tools, target policy, and actual executions;
- target-owned `.NET` build/test commands, network and permission restrictions, and explicit refresh/configuration assistance;
- a provider-neutral `workspace-text-edit` capability that can record an advertised but unusable `apply_patch` provider;
- an owner- and policy-approved PowerShell-native text-update fallback with repository containment, expected-content/fingerprint checks, encoding/newline preservation, atomic replacement where practical, and post-write diff verification;
- the rule that repository policy cannot bypass a higher-priority system, developer, runtime, sandbox, or enterprise requirement to use another edit mechanism.

Issue #69 retains only Python prerequisite discovery, diagnostic, and native bootstrap behavior. The approved D-002C launchers must work without #76, must not define a general readiness snapshot, and may become future consumers of an approved profile only through additive integration. Creating #76 does not accept, promote, schedule, or authorize its implementation, and completing it would not independently authorize removal of a launcher or fallback.

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
- The owner-approved `D-010E` rule is: zero probes and zero executions when local automatic validation is unselected; when selected, one bounded read-only prerequisite preflight and at most one initial validator execution; retry only after a recorded material state change, with further attempts requiring explicit owner instruction.

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

The owner resolved both D-010B subdecisions. `D-010B1` sets tracked target routine local validation to `manual/unselected`; `D-010B2` uses ignored `.dev/validation.local.conf` as the only persistent personal strengthening path and excludes an environment-variable override from v0.8.0. D-010C separately decides whether and how CI becomes required; resolving D-010B does not claim that CI is configured.

## D-010B Configuration Location And Skill-Stage Impact

No opt-in path or reader is implemented today. The target default and developer-local transport are now resolved design inputs; implementation remains behind the accumulated-design approval gate.

### Proposed Configuration Locations

| Scope | Proposed authority and location | Reason |
| --- | --- | --- |
| Shared team default | Generated, tracked target truth at `.dev/project-config.yaml#validation.routine.local.mode` | All Agent runtimes and humans see the same default; `ai-context-init` creates it and `ai-context-upgrader` preserves it. |
| Persistent developer opt-in | Ignored `.dev/validation.local.conf`, parsed as one strict key/value data line. | Remains per clone, visible, readable before Python discovery, cross-runtime, monotonic, and outside tracked/package truth. |
| CI enforcement | Tracked target CI policy and workflow, governed separately by D-010C | A developer-local Git setting must never weaken hosted enforcement. |

### Why `.git/config` Was Initially Recommended

`.git/config` was recommended for implementation economy, not because Git metadata is the only valid home:

- `git config --get` works before Python, PyYAML, `jq`, Node.js, or an OS-specific parser is available;
- the value is naturally per clone, untracked, excluded from the package, and difficult to commit accidentally;
- all supported Agent runtimes can invoke the same Git command instead of maintaining separate Codex, Claude, and ChatGPT settings;
- repository workflows already depend on Git identity and state.

Its drawbacks are material: it is hidden from normal worktree browsing, depends on a Git checkout, has linked-worktree semantics, is not carried with a copied directory, and makes personal AI behavior less discoverable to the developer. The owner has therefore not approved it.

### D-010B2 Storage Alternatives

| Candidate | Strengths | Costs and risks | Current disposition |
| --- | --- | --- | --- |
| Repository-local `.git/config` key `ai-context.validation.local` | No new file schema or parser; per clone; automatically untracked and un-packaged. | Hidden Git metadata; Git-only; less visible; linked-worktree behavior needs tests. | Not selected. |
| Ignored strict file `.dev/validation.local.conf` | Visible beside project governance; per clone; cross-Agent; can be read without Python when limited to one strict key/value line. | Requires the exact `/.dev/validation.local.conf` ignore rule, safe native readers, init/upgrade/docs/tests, and a documented exception to `.dev`'s durable-truth boundary. | Approved by the owner. |
| One-shot environment variable `AI_CONTEXT_VALIDATION_LOCAL` | No repository or Git metadata write; easy for temporary invocation. | Process/shell scoped, easy to leak across repositories, inconsistent across Agent processes, and poor for durable handoff. | Excluded from v0.8.0 to keep one local precedence path. |
| User-level OS config under XDG/AppData | Outside the repository and reusable across clones. | Cross-OS path logic, repository identity matching, permissions, relocation, and hidden global scope create substantially more implementation and support cost. | Not recommended for v0.8.0. |
| Runtime-specific local files such as Claude or Codex settings | Uses each tool's native convention. | Codex, Claude, ChatGPT Desktop, and other Agents can disagree; violates the single target-policy resolution rule. | Rejected as the shared framework mechanism. |

If the ignored-file option is selected, the proposed content is intentionally not YAML or executable shell:

```text
validation.routine.local=auto-if-ready
```

Readers must parse this as data, accept exactly one known key and approved enum, and never `source` or execute the file. A `.dev/project-config.local.yaml` overlay looks more symmetrical but would require a YAML implementation before Python/PyYAML readiness is known; JSON similarly lacks one OS-native parser across Windows and POSIX. Both would recreate the bootstrap problem or multiply launcher code.

The current source `.gitignore` does not cover the approved validation-local file, and the public initialization seed does not install a `.gitignore`. Implementing `.dev/validation.local.conf` therefore requires the explicit `/.dev/validation.local.conf` target ignore contract and tests proving the file remains untracked, is never packaged, and is preserved by init/upgrade. The current distribution builds from tracked Git blobs and excludes `.git/**`, so an ignored untracked file cannot enter a release package accidentally once that contract exists.

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

The owner resolved the tracked target authority and default as future `.dev/project-config.yaml#validation.routine.local.mode: manual`, and the personal transport as ignored `.dev/validation.local.conf`. It may only strengthen the target decision to an approved mode such as `auto-if-ready` or `required`; an Agent may read but never write it implicitly. D-010B is complete.

### D-010C — CI Enforcement

The owner approved CI modes `unconfigured`, `advisory`, and `required`. The framework default is `unconfigured` because a downstream target cannot be assumed to have a CI provider. A target team that wants the validation standard records `required` only after a real tracked CI workflow, exact command/profile, provisioned prerequisites, and durable check evidence exist.

- The proposed authority is `.dev/project-config.yaml#validation.routine.ci.mode` plus the target-owned CI workflow. A configuration value by itself does not create or prove a hosted gate.
- A required CI path may explicitly provision pinned Python and dependencies as part of the CI environment. That is planned CI provisioning, not implicit self-installation by a validator and does not weaken `D-002A`.
- No developer-local transport can weaken CI. Required CI that is absent, misconfigured, blocked, or failed cannot be reported as passed or allow a required closeout.
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

The current orchestrator contract already accepts `passed`, `failed`, `blocked-by-environment`, `not-applicable`, and `deferred-with-owner`, and currently uses `not-applicable` for some unselected capabilities. Adding `not-run-by-policy` directly to the required outcome enum could break strict v0.8.0 consumers. The owner approved the compatibility-first projection: preserve the current outcome enum and add an optional machine-readable selection reason, so an applicable but unselected routine check projects as legacy `outcome: not-applicable` plus `selection_reason: not-run-by-policy`, while human output always says it was not run by policy. A required gate may not use this projection as success. Schema, package, and supported v0.7.0-to-v0.8.0 upgrade compatibility tests must cover both new and legacy readers. Downstream consumer behavior will be observed after release; promoting `not-run-by-policy` to a required top-level outcome remains a separate future change with its own compatibility evidence.

### D-010E — Agent Attempt, Retry, And CI-Observation Budget

The owner-approved budget is scoped per selected validation command, task/checkpoint, and stable material state:

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
| Resolved atomic decisions (21) | `D-001`, `D-002A`, `D-002B`, `D-002C`, `D-003A`, `D-003B`, `D-004A`, `D-004B`, `D-005`, `D-006`, `D-006A`, `D-006B`, `D-007`, `D-009`, `D-TR-001`, `D-010A`, `D-010B1`, `D-010B2`, `D-010C`, `D-010D`, `D-010E` | Production-entrypoint coverage, no-mutation failure, deterministic interpreter trust/discovery, stable native launchers with replaceable discovery, human/JSON diagnostic projections, compatibility-first exit codes, exact per-entrypoint dependency profiles, documentation-only recovery, a verifiable pre-mutation boundary, unchanged CLI ownership plus a repo-common prerequisite component, workflow ownership, packaged-but-unselected skill self-tests, a layered Windows/Ubuntu/portable test matrix, retained v0.8.0 Python runtime, future translation routing, routine-switch scope, local and CI policy, compatibility-safe result truth, and bounded Agent attempts are approved. |
| Decomposed umbrella (1) | `D-002` | This organizes its now-resolved runtime subdecisions and does not independently authorize implementation. `D-003`, `D-004`, and `D-010` are fully resolved through their control chains. |
| Pending atomic decisions (1) | `D-008` | Documentation and migration communication remains open. |

The requested final-three preview was provided before resolving `D-007`. One question now remains under the one-question-at-a-time decision contract:

1. `D-008` freezes installation, troubleshooting, command/contract migration, upgrade, and release communication.

### Approved Intermediate Checkpoints

The owner approved the following sequence on 2026-08-02. Approval establishes workflow and release boundaries only; it does not approve remaining #69 design decisions or authorize implementation.

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

- Last completed action: resolved `D-006` by preserving two canonical skill-owned scripts, one thin compatibility path, and 22 repo-common scripts while approving four stable repo-common prerequisite/launcher assets and package parity obligations.
- Current task: `AIC-004-diagnostic-design`.
- Exact next action: explain and obtain only the owner decision on `D-008` human documentation, command migration, upgrade, troubleshooting, and release communication.
- Validation already completed: confirmed clean `main@2263744bb2dc876f8077547e961fc68be28b0074` before branching; verified the final baseline assessment; verified the inventory against `git ls-files`, direct file reads, distribution profile, shell registry, active documentation, and existing tests; parsed all then-existing task JSON files; `git diff --check`, `validate-workflow-artifacts.py`, and `validate-ai-context.py` passed.
- Current discussion-checkpoint validation: Git-history probes established the adoption timeline; the active sub-agent manifest and Codex adapter established the missed low-cost route; local uv 0.11.29 help and an offline/no-download managed-Python lookup were inspected read-only; the changed task JSON parsed with PowerShell; locator/index state was checked directly; and `git diff --check` passed. Full Python-backed repository validators were not rerun because every discovered interpreter lacks PyYAML and D-002A now forbids implicit installation; this checkpoint records that result as `blocked-by-environment`, not passed.
- Validation environment note: generic `python` and `python3` resolve to unusable Windows aliases. A versioned uv-managed Python 3.14.1 and the Codex bundled Python 3.12.13 can start, but neither currently imports PyYAML. Prior artifact validation used Codex Python with isolated temporary `PyYAML==6.0.3`; no repository dependency files were changed.
- Git state: active branch `codex/2026-08-02-python-prerequisite-diagnostics`, created from `main@2263744bb2dc876f8077547e961fc68be28b0074`; the latest durable design checkpoint entering this discussion is `e2b46db`.
- Branch history and checkpoint handoffs: bootstrap commits `88a01be` and `4e93c0f`; absent-interpreter boundary `cd58c2b`; inventory translation `d27fb8a`; D-001/fallback assessment `d5ae808`; runtime rationale and D-002A `9937fb4`; downstream switch gap `7fa102c`; activation/retry scope `74bb024`; D-010B team scenarios `c2b35ad`; opt-in location and skill-stage map `32ede97`; workflow ownership and self-test terminology `22e6883`; self-test boundary and FUP scope `ac2d9d7`; staged #69/#75 scope boundary `1a66897`; checkpoint split and integrated D-010 framing `8c3fb8d`; manual-default and local-store comparison `4703943`; persistent local opt-in `5c6b9e5`; target CI enforcement `8ba7ed9`; outcome/retry controls `59a8add`; interpreter discovery order `8cef8fc`; environment-readiness follow-up split `3769584`; native-launcher boundary `779df84`; dependency-profile boundary `3f4d75d`; recovery-guidance boundary `52593be`; canonical-runtime boundary `170d7c8`; diagnostic-output projection `8d00140`; exit-code compatibility `51d274e`; pre-mutation guarantee `44e28fd`; deterministic test matrix `e2b46db`; no push or merge handoff has occurred.
- Blockers or unresolved decisions: one atomic #69 decision remains unresolved: `D-008`. Script ownership/package compatibility, the deterministic test matrix, and all earlier listed decisions are resolved. Implementation edits remain paused pending explicit accumulated-design approval. Proposals #75 and #76 are externally tracked but not accepted, promoted, scheduled, or authorized for implementation.

## Branch Lifecycle

| Segment | Branch | Base | Checkpoint Type | Commit | Remote / Target | Recorded At | Reason | Resume Branch / Action |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `codex/2026-08-02-python-prerequisite-diagnostics` | `main@2263744bb2dc876f8077547e961fc68be28b0074` | bootstrap | `88a01bebfe95f696763c1b310c363f354949f205` | local | `2026-08-02T10:45:48+08:00` | Preserve the authorized workflow and initial impact inventory before owner decisions. | Ask `D-001`; keep implementation pending until the accumulated design is explicitly approved. |
| 1 | `codex/2026-08-02-python-prerequisite-diagnostics` | `main@2263744bb2dc876f8077547e961fc68be28b0074` | design evidence | `cd58c2b0391dccb4a8487f33938b8a3c5d060500` | local | `2026-08-02T10:57:23+08:00` | Preserve the observed absent-interpreter boundary without resolving D-001 or D-002. | Provide the requested complete zh-TW inventory, then ask only `D-001`. |
| 1 | `codex/2026-08-02-python-prerequisite-diagnostics` | `main@2263744bb2dc876f8077547e961fc68be28b0074` | owner-review translation | `d27fb8adbaf890f9f926c2de6bf66aa6917a83d0` | local | `2026-08-02T11:05:29+08:00` | Preserve the complete Traditional Chinese Taiwan inventory used for the D-001 owner decision. | Record D-001 and evaluate fallback/ownership before asking D-002A. |
