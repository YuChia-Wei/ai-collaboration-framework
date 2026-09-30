# v0.4.2 Current Candidate Inventory

## Evidence Identity

- Workflow: `2026-07-19-v0-4-2-remediation`
- Immutable base: `main@9b03668f14af7e69e283b4caf30d25fe41d2b460`
- Refreshed at: `2026-07-19T12:48:48+08:00`
- Historical finding source: `ASM-20260717-004`
- Independent planning source: `.dev/backlog/plans/post-v0.4.0-improvement-plan.md`
- Evidence method: direct file inspection, current repository scans, Git mode
  inspection, and local tool-version execution. Historical findings are not
  accepted as current without reproduction.

## Patch Impact Result

Every selected v0.4.2 blocker has a patch-compatible correction path. The
following recommendations from the historical inputs are explicitly excluded
because they would add or remove a published contract:

- semantic cross-runtime wrapper validation and governance PR CI -> `ENF-001`;
- deletion or relocation of auditor templates -> `ENF-001`;
- runtime-adapter metadata, promotion, and parity validation -> `SAG-001`;
- runner redesign or SDK-absence FAIL-to-SKIP semantics -> `TOOL-001`.

No new schema, required validation or CI route, published-path removal, or
intentional required-gate semantic change is authorized by this inventory.

## R042-001 — Runtime Wrapper And Routing Correctness

| Observation | Current Evidence | Disposition | Exact Candidate Surface |
| --- | --- | --- | --- |
| `AIC-001` five Claude wrapper descriptions say Codex | Reproduced in `bdd-gwt-test-designer`, `ddd-ca-hex-architect`, `problem-frame-author`, `requirement-author`, and `spec-author` at frontmatter line 3. | Patch: use runtime-neutral `the agent`; do not add the proposed semantic validator. | `.claude/skills/{bdd-gwt-test-designer,ddd-ca-hex-architect,problem-frame-author,requirement-author,spec-author}/SKILL.md` |
| `AIC-010` root skill routing omits `spec-compliance-validator` | Reproduced in both `AGENTS.md` and `AGENTS.zh-TW.md`; the canonical registry and both runtime wrapper roots contain the skill. | Patch: add the existing skill to both derived routing tables. | `AGENTS.md`, `AGENTS.zh-TW.md` |
| `AIC-010` / `SAG-F-002` active role routing omits `context-translator` | Reproduced: `.ai/SUB-AGENT-SYSTEM.MD` lists 17 roles while the canonical role exists and has three retained runtime adapters. | Patch: add the existing role and its `repo-structure-sync` use; do not change adapter metadata or behavior. | `.ai/SUB-AGENT-SYSTEM.MD` and the human taxonomy guide if its active routing inventory is incomplete |

Validation: wrapper quick validation, direct canonical-to-table inventory,
`validate-ai-context.py`, exact-case/reference checks, and independent audit.

## R042-002 — Doctrine And Standards Consistency

| Observation | Current Evidence | Disposition | Exact Candidate Surface |
| --- | --- | --- | --- |
| `AIC-002` positive Handler examples own business orchestration/repository access | Reproduced in `best-practices.md`, the recommended block in `anti-patterns.md`, `LEARNING-PATH.md`, and the SPEC guide phrase “application executor in code.” | Patch: express Use Case as executor and optional dispatch Handler as thin mapping adapter; add explicit canonical precedence. | `.dev/standards/best-practices.md`, `.dev/standards/anti-patterns.md`, `src/knowledge/dotnet-backend/guides/LEARNING-PATH.md`, `src/skills/spec-author/references/spec-guide.md` |
| `AIC-008` positive examples use bare wall clock | Reproduced in three positive aggregate snippets, `TaskDto.cs`, and `EfTasksDueTodayProjection.cs`; `DateProvider.Now()` is already the retained repository example abstraction. | Patch: use the existing DateProvider convention or explicit time input; do not select a new universal time technology. | `.dev/standards/coding-standards/aggregate-standards.md`, `.dev/standards/examples/dto/TaskDto.cs`, `.dev/standards/examples/projection/EfTasksDueTodayProjection.cs` |
| `AIC-008` method naming fact says camelCase | Reproduced in `CODE-REVIEW-CHECKLIST.md`. | Patch: methods use PascalCase. | `.dev/standards/CODE-REVIEW-CHECKLIST.md` |
| `AIC-008` wrong/correct connection examples are identical | Reproduced in `ASPNET-CORE-CONFIGURATION-CHECKLIST.md`. | Patch: make the incorrect example an explicit hardcoded wrong-port example and retain environment-driven correct configuration. | `.dev/standards/ASPNET-CORE-CONFIGURATION-CHECKLIST.md` |
| `AIC-008` `Lab.MessageSchemas` contradiction | Not reproduced; current active contract paths use `<Company>.BoundedContextContracts.<Domain>`. | Stale/already resolved; no edit. | none |
| `AIC-011` foreign `ezSpec`, missing L2, and source-shaped layout | Reproduced in the canonical spec-compliance rules. | Patch: use GWT-neutral wording, restore consecutive levels, and mark mappings target-relative. No executable validator behavior changes. | `.ai/assets/skills/spec-compliance-validator/references/spec-compliance-rules.md` |

Validation: focused content assertions, coding-standards structural gate,
documentation projection tests, AI-context validation, and independent audit.

## R042-003 — Navigation And Lifecycle Hygiene

| Observation | Current Evidence | Disposition | Exact Candidate Surface |
| --- | --- | --- | --- |
| `AIC-004` three auditor templates encode the retired workflow-persistence model | Reproduced; the canonical skill no longer routes to the workflow locator/plan/task templates. | Patch: retain published files but mark them historical/deprecated with current assessment routing. Physical removal remains `ENF-001`. | `.ai/assets/skills/ai-context-auditor/templates/{workflow-locator-template.yaml,ai-context-audit-workflow-plan-template.md,ai-context-audit-task-template.json}` |
| `AIC-006` workflow index advertises missing `templates/` | Reproduced: `.dev/workflows/templates/` does not exist. | Patch: remove the dead discovery row and route new workflows to owner-skill templates. | `.dev/workflows/INDEX.MD` |
| `AIC-006` completed workflows appear under Active | Reproduced for the four pre-existing rows under `Active Workflows`. | Patch: move completed rows to the completed discovery table; retain the active v0.4.2 row only. | `.dev/workflows/INDEX.MD` |
| `AIC-014` two prompt guides deny current skill status | Reproduced. | Patch: identify the guides as human-facing usage surfaces for the existing skills. | `.dev/guides/ai-collaboration-guides/{REQUIREMENT-DESIGNER-PROMPT-GUIDE.md,SPEC-DESIGNER-PROMPT-GUIDE.md}` |
| `AIC-015` obsolete `/path/to/ai-plan` copy install | Reproduced. | Patch: use the governed release package and `repo-structure-sync` path already published by the repository. | `.dev/guides/implementation-guides/quick-setup.md` |
| `AIC-015` source-specific example/stub wording | `ScrumTeam`, ezDDD/ezapp TODO wording, and the short EZDDD reference remain. Exact `ezapp-2.0.0` and `Lab.MessageSchemas` observations are no longer present. | Patch only where wording falsely presents source-project or future package truth; retain explicitly historical mapping content. No new capability design. | focused current matches under `.dev/standards/` and `.dev/guides/design-guides/EZDDD-FRAMEWORK-REFERENCE.md` |
| `AIC-018` two completed requirements lack outcomes | Reproduced for `DOTNET-VALIDATOR-PHASE-2-REQUIREMENTS.MD` and `HISTORICAL-CONTEXT-NORMALIZATION-REQUIREMENTS.MD`. | Patch: add evidence-backed implementation outcomes and preserve original requirement wording below. | the two named requirement files |

Validation: workflow/index/reference validation, exact-case tests, explicit
outcome evidence, AI-context validation, and independent audit.

## R042-004 — Patch-Safe Tooling Portability

| Observation | Current Evidence | Disposition | Exact Candidate Surface |
| --- | --- | --- | --- |
| `AIC-003` required runner uses bare `python` | Reproduced in all Python-backed `check-all.sh` command strings and the shell manifest parity list. | Patch: add in-runner interpreter discovery while preserving the existing command inventory and required failure semantics; update manifest only if the retained exact parity contract requires it. | `.ai/scripts/check-all.sh`, `.ai/scripts/shell-assets.yaml`, focused GWT fixtures |
| `AIC-003` source dependency bootstrap is undeclared | Reproduced: source validators import PyYAML; only extracted-package metadata declares `PyYAML==6.0.3`. | Patch: add a source-side checksum-stable requirement and documented virtual-environment/bootstrap command. | root source dependency declaration and `.ai/scripts/README.md` |
| `AIC-003` SDK pin is currently unsatisfied | Not reproduced locally: `global.json` requests `10.0.300` with `latestMajor`; installed `dotnet --version` is `10.0.302` and the quick gate passes. | No speculative local edit. Re-evaluate in hosted Ubuntu after the declared setup. Do not change SDK absence to SKIP. | `global.json` only if hosted evidence proves a current patch defect |
| `AIC-005` advisory script scans repository parent | Reproduced: `check-test-compliance.sh` uses `../../..`; neighboring retained scripts use `../..`. | Patch: correct to `../..`; do not delete the published retirement-candidate path. | `src/tools/dotnet/check-test-compliance.sh`, focused path fixture |
| `AIC-013` repo-side Python floor is undeclared | Reproduced; current local Python is 3.13.14 and PyYAML 6.0.3. The published target tooling already requires Python 3.11+. | Patch: declare Python 3.11+ for source-side tooling and provide actionable bootstrap instructions. | `.ai/scripts/README.md`, source dependency/bootstrap entry |

Environment evidence:

- Windows Git Bash: required; baseline quick gate passed before remediation.
- Hosted Ubuntu: required after the candidate commit.
- macOS: explicitly deferred/unverified by repository-owner decision.

## Frozen Execution Order

1. `V042-002` wrapper and routing.
2. `V042-003` doctrine and standards.
3. `V042-004` navigation and lifecycle.
4. `V042-005` portability and platform evidence.
5. `V042-006` complete gates and independent verification.

Any implementation-time discovery that crosses the patch-impact gate returns to
this inventory, records the named v0.5.0 owner, and stops that candidate.

