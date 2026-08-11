# v0.13 Framework-Owned .NET SDK Dependency Baseline

## Template Metadata

- `template_id`: `ai-context-auditor-report`
- `template_version`: `2.1.0`
- `created_at`: `2026-07-10T18:22:49+08:00`
- `updated_at`: `2026-07-15T08:39:00+08:00`

## Metadata

- `assessment_id`: `ASM-20260811-001`
- `assessment_type`: `ai-context-audit`
- `owner_skill`: `ai-context-auditor`
- `status`: `final`
- `audit_date`: `2026-08-11`
- `created_at`: `2026-08-11T08:33:55+08:00`
- `updated_at`: `2026-08-11T08:33:55+08:00`
- `template_source`: `.ai/assets/skills/ai-context-auditor/templates/ai-context-audit-report-template.md`
- `template_version`: `2.1.0`
- `repository`: `YuChia-Wei/ai-collaboration-framework`
- `subject_branch`: `codex/2026-08-11-ctx-009-sdk-free-baseline`
- `subject_commit`: `7652e5f1d11054878699046856fce12f0c19e587`
- `previous_assessment`: `ASM-20260805-002`
- `workflow_refs`: `2026-08-11-ctx-009-sdk-free-baseline`

## Executive Summary

- Overall assessment: The source framework is not SDK-free. Its required PR profile installs .NET from a root `global.json`, runs three framework-owned `dotnet test` projects, packages two compilable provider projects, and seeds the SDK pin into downstream targets. Active tests, manifests, and guidance make those selections contractual even though the provider is described as inactive by default.
- Overall score: `N/A`
- Decision: `remediation-required`
- Primary strengths: canonical engineering rules are already separate from provider code; target ownership is already stated in several provider contracts; the evidence schema supports `reference-only`; hosted package and publication workflows are Python-only.
- Primary risks: a missing SDK blocks required source validation; default payload bytes contain compilable .NET implementation; unresolved provider fixtures can be mistaken for activation proof; active documentation and Python contracts preserve direct SDK coupling.

The bounded v0.13 disposition is to remove framework-owned compilable projects and required `dotnet` execution, retain semantic rules and diagnostic mappings as non-executable references, and make any analyzer or configuration-test project an explicit target-owned, on-demand choice. This assessment does not perform that remediation.

## Scope

### Included AI Context Surfaces

- aggregate validation entrypoints, profile selection, environment handling, and fail-closed tests
- portable hosted workflow setup and human pull-request guidance
- tracked `.csproj` and root SDK configuration
- bundled mechanical-validation implementation, activation records, schemas, templates, fixtures, and tests
- source-include evidence claims and BuildingBlocks test coupling
- distribution payload mapping and target-template seeding
- active root, script, skill, standards, persistence, and dotnet-backend guidance

### Default Exclusions

- `src/**`
- product implementation and target-repository tests
- generated and dependency trees

### Additional Exclusions

- GitHub Issue #179 and `EngineeringGuardrails.Contracts.*`
- creation of a replacement NuGet package, `dotnet tool`, or compiled CLI
- immutable dated workflows, assessments, and releases
- implementation, transport, integration, Issue closure, tag, and publication

### Code Review Handoff

- Requested: `no`
- Paths not scanned: product source and product tests
- Recommended skill: `not-applicable`; the inspected scripts and .NET artifacts are framework validation/provider surfaces owned by AI-context governance

## Methodology And Evidence

### Pass A: Independent Baseline

- Enumerated every tracked `.csproj`, `.sln`, `.slnx`, and root SDK pin with Git-backed file inventory.
- Traced the hosted PR workflow through `check-all.sh`, the validation registry, exact project commands, missing-SDK classification, and Python tests that assert the coupling.
- Traced distribution selectors from the dotnet-backend profile to packaged provider projects and the downstream `global.json` seed.
- Classified current provider activation evidence, fixture state, source-include evidence tiers, and historical-only paths.

### Pass B: Repository-Aware Skill Review

- Applied AI-context boundary, assessment, workflow, distribution, language, evidence, and target-ownership contracts.
- Compared provider-specific diagnostic identifiers with the canonical engineering-rule catalog and confirmed that rule semantics can survive implementation retirement.
- Distinguished hosted release workflows from latent/manual `release` profile membership: candidate and publication workflows are currently Python-only, but the registry still selects three .NET tests whenever `check-all --profile release` is invoked.

### Delegation

- Sub-agents used: `3` bounded read-only inventory workers
- Assigned surfaces: validation gates and workflows; provider projects and distribution; active guidance and indexes
- Mutation authority: none; all findings were independently integrated against tracked-file evidence by the assessment owner

### Discovery Accelerators

| Tool / generated view | Source revision or input digest | Freshness / dirty state | Scope and exclusions | Unsupported relationships | File-backed fallback |
| --- | --- | --- | --- | --- | --- |
| codebase-memory graph | indexed project `ai-collaboration-prompts-dotnet-backend`; exact indexed commit not exposed | usable for discovery, not accepted as subject-revision proof | code and script symbol discovery; non-code manifests remained outside graph authority | exact Git completeness, payload selection, active/historical state | `git ls-files`, direct tracked-file reads, registry and repository-native validators |

## Repository Context Inventory

| Surface | Files / Size | Audience | Scope | State | Notes |
| --- | ---: | --- | --- | --- | --- |
| Compilable .NET projects | 6 tracked `.csproj`; no `.sln` or `.slnx` | maintainers and provider adopters | source plus default dotnet-backend payload | active | 2 provider projects, 1 controlled fixture, 3 root source-test projects |
| SDK selection | 1 root `global.json` | CI, source maintainers, downstream seed consumers | source and target template | active | selects SDK `10.0.300`; hosted PR workflow installs it |
| Required source checks | 3 `dotnet test` entries plus 1 provider evaluator | maintainers | `pr`, `release`, `nightly-full` | active | missing SDK is `blocked-by-environment`, not pass |
| Provider activation contract | manifest, schemas, evaluator, templates, fixtures, evidence | target adopters | default dotnet-backend payload | active/source-available | only reference-in-place is implemented; controlled fixture is unresolved |
| Source-include evidence | 1 evidence manifest plus Python contract | target adopters and release validation | default dotnet-backend payload | active | claims BuildingBlocks are executable-tested through a framework-owned test project |
| Historical former provider paths | dated workflow and release evidence | maintainers | source history only | historical | distribution excludes dated execution history; no current tracked production project at former `tools/DotnetBackend*` paths |

## Strengths

1. The engineering-rule catalog owns stable semantic rule text independently from Roslyn diagnostic IDs or a concrete provider implementation.
2. The current provider documentation already states that target repositories own selection, wiring, SDK, severity, invocation, and evidence, providing a sound basis for on-demand guidance.
3. The example evidence schema already distinguishes `reference-only`, `structure-validated`, `executable-tested`, and `historical`, so retained snippets can be classified without inventing a new evidence vocabulary.
4. Hosted package-candidate and publication workflows use Python-only release commands; removing the PR SDK setup and manual registry selections does not require redesigning release publication.
5. The dependency validator already skips managed-project and `global.json` checks when no managed projects are present, allowing the portable Python dependency contract to remain active.

## Findings

| ID | Severity | Finding | Evidence | Impact | Recommendation | Owner / Next Skill |
| --- | --- | --- | --- | --- | --- | --- |
| SDKGATE-001 | HIGH | Required source validation directly depends on a .NET SDK and three framework-owned test projects. | `.github/workflows/portable-gates.yml:82-115` installs .NET from `global.json` before `check-all --profile pr`. `.ai/scripts/validation-profile-registry.sh:207-221` registers analyzer, runtime-validation, and BuildingBlocks `dotnet test` commands for `pr`, `release`, and `nightly-full`. `.ai/scripts/check-all.sh:1090-1123` executes them whenever source-release context is present; missing SDK is recorded as blocked at lines 823-836 and 1029-1035. | The framework's required PR baseline cannot pass when `dotnet` is absent, contradicting the v0.13 portability goal. | Remove these checks from required profiles and the aggregate runner, remove hosted SDK setup, and add a Python contract proving required framework checks contain no SDK selection. Target-owned .NET tests remain optional outside the framework gate. | `ai-context-governance` / `CTX009-002` |
| SDKPAYLOAD-001 | HIGH | The default dotnet-backend payload contains compilable provider projects and seeds a framework SDK pin downstream. | Two canonical provider projects and one controlled target fixture are tracked under `.ai/assets/tech-stacks/dotnet-backend/tooling/bundled-mechanical-validation/**`. `.ai/distribution/profiles/dotnet-backend.yaml:97-117` maps that tree into the managed payload, while lines 308-325 seed root `global.json`. Packaging assertions at `.ai/scripts/tests/test_ai_context_packaging.py:489-510` require the analyzer project to be packaged. | Downstream installation carries framework-owned implementation and SDK policy even when no target explicitly selects an analyzer. | Retire all packaged compilable projects, remove the `global.json` seed and root pin, and change packaging assertions to require a project-free default payload plus retained recipe-only guidance. | `ai-context-governance` / `CTX009-002` |
| SDKEVID-001 | HIGH | Source-include evidence claims executable validation through a framework-owned BuildingBlocks project and active Python tests enforce that command. | `.ai/assets/tech-stacks/dotnet-backend/source-includes/evidence-manifest.yaml:5-13` marks domain includes executable-tested through `tools/DotnetBackendBuildingBlocks.Tests`. `.ai/scripts/tests/test_ai_context_source_include_evidence.py:71-84` requires the command in both runner and shell registry, and the registry selects that Python contract for every profile. | Removing only the project or registry entry would leave active evidence overstated or fail closed; downstream consumers could treat bounded source examples as framework-compiled guarantees. | Reclassify the source include as `reference-only` or `structure-validated`, state target compatibility responsibility, remove command coupling, and keep a Python structural evidence contract. | `ai-context-governance` / `CTX009-002` |
| SDKPROV-001 | HIGH | Active provider and activation contracts model a bundled reference-in-place implementation, but the only fixture is unresolved and no invocation was run. | `provider-manifest.yaml` declares a source-only provider and two capabilities. The controlled activation record remains `unresolved`; build and test evidence are `not-run-owner-directed`. The Architecture Kit readiness record reports unavailable while its action text says to keep the bundled provider selected. | Active guidance can be read as supported executable adoption without target proof, and it conflicts with the v0.13 target-selected on-demand creation model. | Replace the bundled provider/activation surface with recipe-only target creation guidance. Preserve diagnostic mappings, semantic constraints, and bounded snippets with explicit evidence tier and compatibility ownership; remove activation claims that require a framework implementation. | `ai-context-governance` / `CTX009-002` |
| SDKDOC-001 | MEDIUM | Active documentation and contract tests disagree about the number and ownership of .NET gates and hard-code the bundled provider path. | `.ai/scripts/README.md:480-493` describes future commands and only one current analyzer test, while `check-all.sh:1109-1119` runs three. Root READMEs, dotnet-backend README, spec-compliance templates, persistence guide, shell registry, fail-closed tests, source evidence tests, PR template, and provider templates select concrete framework projects or paths. | Partial remediation would leave discovery, tests, and user guidance inconsistent, causing reintroduction or false expectations. | Rewrite all active guidance and Python assertions in the same delivery; retain immutable dated history unchanged and validate active link/index reachability. | `ai-context-governance` / `CTX009-002` |

## Baseline And Skill Comparison

### Confirmed

- The SDK dependency is selected by active hosted PR validation, not merely by dormant source files.
- The default payload contains provider source projects even though activation is described as target-explicit.
- Canonical engineering semantics do not require retaining the provider implementation.
- Removing all managed projects allows the existing Python dependency validator to skip SDK and NuGet validation without weakening Python dependency consistency.

### Added By Repository-Aware Review

- The `release` profile's .NET membership is latent/manual: current candidate and publication workflows do not call it, but the registry remains an active contract and must be SDK-free.
- The source-include evidence Python test is a required cross-profile coupling and must change together with the BuildingBlocks project.
- The controlled fixture is negative evidence, not a successful target activation example.

### Downgraded Or Deferred

- Deprecated shell helpers and the unregistered Dockerfile project-copy script are compatibility or historical surfaces; they do not independently create a required SDK gate. Active wording may be made target-conditional, but no replacement tooling is required.
- Historical release and workflow references to former project paths remain immutable evidence and are not remediation targets.

### Overturned

- `source-available` plus packaged source is not sufficient justification for a framework-owned compilable payload under the approved v0.13 boundary.
- An unresolved fixture cannot establish provider readiness or implementation compatibility.

## Validation

| Check | Result | Evidence / Notes |
| --- | --- | --- |
| Git and subject state | passed | dedicated branch at `7652e5f1d11054878699046856fce12f0c19e587`; assessed context surfaces unchanged during inventory |
| Tracked project inventory | passed | 6 `.csproj`, 0 `.sln`, 0 `.slnx`, and 1 root `global.json` identified with `git ls-files` |
| AI-context validator | passed | `python .ai/scripts/validate-ai-context.py`; 27 active indexes, 17 skills, 391 language-policy files, 13 rules, 35 manifests, 10 capability mappings, 2 lessons |
| Dependency validator | passed | `python .ai/scripts/validate-dependency-versions.py`; source mode, 1 Python dependency, 5 managed production projects, 7 NuGet dependencies |
| Provider activation evaluator | passed | 14 Python tests passed against the pre-remediation provider contract |
| Validation registry contract | passed | 5 Python tests passed outside the restricted sandbox |
| Source-include evidence contract | passed | 4 Python tests passed outside the restricted sandbox, confirming the current BuildingBlocks command coupling |
| GitHub workflow contract | passed | 8 Python tests passed, including current portable workflow shape |
| Aggregate fail-closed contract | timed-out | baseline run exceeded 124 seconds; timeout is retained as failure, not pass |
| Packaging suite | diagnostic-only | restricted-sandbox run reported 37 tests, 2 current workflow-permission assertion failures, 26 temporary-directory permission errors, and 2 skips; it does not establish package compliance |
| Example-evidence suite | blocked-by-environment | restricted-sandbox temporary-directory permission failures prevented a valid result |

### Skipped Validation

- No `dotnet build` or `dotnet test` was needed to establish the dependency inventory; current command registration and project selection are direct tracked-file evidence.
- No product implementation or target repository was reviewed.
- No long suite was rerun after the baseline timeout because no material remediation existed yet.
- No push, pull request, merge, Issue closure, tag, or publication occurred.

## Recommended Action Order

1. Remove the six tracked `.csproj` surfaces and root `global.json`, including bundled provider implementation, controlled fixture, and three root test projects.
2. Replace the bundled provider contract with a recipe-only, target-selected on-demand guidance surface that has no activation claim or compilable project.
3. Preserve DBA1001-DBA1017 mappings as enforcement labels attached to canonical rule semantics, and retain bounded analyzer/configuration snippets as `reference-only` with target compatibility responsibility.
4. Remove hosted .NET setup and all required `dotnet` entries from registry, aggregate runner, shell registry, and fail-closed contracts.
5. Reclassify source-include evidence and update its structural Python contract.
6. Update distribution/profile/package assertions and active discovery/guidance surfaces; leave dated evidence unchanged.
7. Add a deterministic SDK-free framework contract and run required validation with `dotnet` absent from `PATH`.
8. Obtain independent `ASM-20260811-002` verification and reconcile every finding before local workflow closeout.

## Proposed Acceptance Criteria

- `git ls-files` returns no active framework-owned `.csproj`, `.sln`, `.slnx`, or root `global.json`.
- Default distribution payloads contain no compilable .NET project and do not seed a target SDK.
- Required framework profiles and hosted workflows neither install nor invoke `dotnet`.
- `check-all --profile pr` passes under a controlled `PATH` where `dotnet` is unavailable, subject to unrelated platform prerequisites being present.
- Target-selected analyzer guidance explicitly assigns project creation, SDK, Roslyn version, severity, wiring, tests, CI, compatibility, and evidence to the target owner.
- Retained mappings and snippets declare their evidence tier and do not claim provider activation or executable validation.
- Canonical engineering rules and their semantic digest remain valid after concrete provider retirement.
- Independent verification closes or explicitly defers every baseline finding without representing blocked or skipped checks as passed.

## Deferred Items

- Any future packaged analyzer, contract assembly, `dotnet tool`, or compiled CLI requires a separate owner decision and work item.
- Adoption of `EngineeringGuardrails.Contracts.*` remains Issue #179 and is not a prerequisite for this baseline.
- Target repositories may independently select .NET analyzer or configuration projects; their SDK and compatibility matrix are not framework release truth.
- Existing historical evidence keeps its original commands and outcomes.

## Appendix

### Commands Run

```text
git ls-files -- '*.csproj' '*.sln' '*.slnx' global.json
git ls-files -- '.ai/assets/tech-stacks/dotnet-backend/tooling/**'
git grep -n -E 'dotnet test|setup-dotnet|global.json|DotnetBackend|bundled-mechanical-validation' -- <active scoped paths>
python .ai/scripts/validate-ai-context.py
python .ai/scripts/validate-dependency-versions.py
python .ai/assets/tech-stacks/dotnet-backend/tooling/bundled-mechanical-validation/tests/test_provider_activation_evaluator.py -v
python .ai/scripts/tests/test_validation_profile_registry.py -v
python .ai/scripts/tests/test_ai_context_source_include_evidence.py -v
python .ai/scripts/tests/test_github_workflow_contract.py -v
python .ai/scripts/tests/test_fail_closed_validation.py -v
python .ai/scripts/tests/test_ai_context_packaging.py -v
python .ai/scripts/tests/test_ai_context_example_evidence.py -v
```

### Tracked Project Disposition

| Surface | Baseline role | Disposition |
| --- | --- | --- |
| provider analyzer project | packaged source-only implementation | remove; preserve mappings and bounded target recipe |
| provider runtime-validation project | packaged source-only implementation | remove; preserve marker/configuration-test semantics |
| controlled reference-in-place fixture | unresolved negative fixture | remove with retired activation contract |
| analyzer source test project | framework source-only required gate | remove |
| runtime-validation source test project | framework source-only required gate | remove |
| BuildingBlocks source test project | framework source-only required gate and evidence claim | remove; downgrade source-include evidence |
| root `global.json` | source SDK pin and downstream target-template seed | remove |

## Lifecycle Handoff

- Assessment path: `.dev/assessments/ASM-20260811-001/report.md`
- Stable finding references: `ASM-20260811-001#SDKGATE-001`, `ASM-20260811-001#SDKPAYLOAD-001`, `ASM-20260811-001#SDKEVID-001`, `ASM-20260811-001#SDKPROV-001`, `ASM-20260811-001#SDKDOC-001`
- Remediation owner: `ai-context-governance`
- Related remediation workflow: `2026-08-11-ctx-009-sdk-free-baseline`
- Verification assessment: `ASM-20260811-002` (reserved, not created)
- Remediation intentionally not performed by this skill: `yes`
