# AI Context Audit Report

## Template Metadata

- `template_id`: `ai-context-auditor-report`
- `template_version`: `2.1.0`
- `created_at`: `2026-07-10T18:22:49+08:00`
- `updated_at`: `2026-07-15T08:39:00+08:00`

## Metadata

- `assessment_id`: `ASM-20260717-004`
- `assessment_type`: `ai-context-audit`
- `owner_skill`: `ai-context-auditor`
- `status`: `final`
- `audit_date`: 2026-07-16
- `created_at`: `2026-07-17T13:02:24+08:00`
- `updated_at`: `2026-07-17T13:02:24+08:00`
- `template_source`: `.ai/assets/skills/ai-context-auditor/templates/ai-context-audit-report-template.md`
- `template_version`: `2.1.0`
- `repository`: `https://github.com/YuChia-Wei/ai-collaboration-prompts-dotnet-backend`
- `subject_branch`: `main`
- `subject_commit`: `82b88b7287deb7a64e0311fde6b1b53ea0d194b1`
- `previous_assessment`: none durable; an informal conversation-mode review dated 2026-07-07 (subject `a4f46e2`, retained untracked under `docs/review-report/`) is used as the comparison input
- `workflow_refs`: none (standalone assessment; a v0.4.0 remediation planning workflow exists unmerged on `origin/codex/2026-07-16-v0-4-0-ai-context-remediation` and overlaps several findings)

## Executive Summary

- Overall assessment: v0.3.0 is a substantial and genuine quality upgrade over the 2026-07-07 baseline. The previously missing consistency machinery now exists and passes (wrapper-metadata validation, exact-case reference lint, index validation, language and bilingual parity checks, workflow/assessment/commit validators, 107 GWT tests, byte-deterministic release packaging with a hardened publish pipeline). Of the 20 informal 2026-07-07 findings, 5 are fixed, 7 partially fixed, and 8 still open. The remaining risk concentrates in three places: (1) legacy standards and learning content still teach the Handler anti-pattern the canonical standard forbids; (2) the Claude wrapper routing surface still carries "Codex" wording on 5 skills; (3) the repository's own required quick gate is not runnable on a stock environment (bare `python`, undeclared PyYAML/Python-version floor, unsatisfiable SDK pin), while release evidence cites that gate as passing.
- Overall score: `7.5/10` (2026-07-07 informal baseline: 6.5/10)
- Decision: `remediation-recommended`
- Primary strengths: validation tooling now real and passing at HEAD; deterministic packaging and defense-grade release pipeline; coherent assessment/backlog/workflow governance model; exceptional workflow closure and decision traceability; rebuilt `.dev/INDEX.md` with zero dead links; unified skill spec schema (14/14).
- Primary risks: contradictory legacy content mistrains agents on the Use Case/Handler boundary; routing-surface wording drift is invisible to the new validators; enforcement remains local-and-voluntary (packaging-only CI) and the local gate fails on stock machines, making "checks passed" claims irreproducible.

## Scope

### Included AI Context Surfaces

- Root entries: `AGENTS.md`, `AGENTS.zh-TW.md`, `CLAUDE.md`, `README.md`, `README.en.md`
- `.ai/**` (assets, skills, sub-agent prompts, scripts, distribution)
- `.dev/**` (standards, guides, adr, specs, requirement, workflows, assessments, backlog, releases)
- Runtime wrappers: `.agents/**`, `.claude/**` (plus `.codex/`, `.github/agents/` inventory)
- `.github/workflows/**`
- `tools/DotnetBackendAnalyzers/**` (inventory and doc-consistency only)

### Default Exclusions

- `src/**`
- `tests/**`, `test/**`
- product implementation trees
- generated and dependency trees

### Additional Exclusions

- `docs/review-report/**` — untracked 2026-07-07 conversation-mode review output; used only as the comparison input, not audited.
- `origin/codex/2026-07-16-v0-4-0-ai-context-remediation` branch content — evaluated separately as a planning review returned in conversation; not part of this subject revision.

### Code Review Handoff

- Requested: `no`
- Paths not scanned: `src/**`, `tests/**` (both now contain only a readme.md each)
- Recommended skill: `code-reviewer` if product code returns

## Methodology And Evidence

### Pass A: Independent Baseline

- Evidence used: full-tree file reads, `git diff --stat a4f46e2..82b88b7`, `git log a4f46e2..82b88b7`, deterministic path/reference scans, direct execution of validators and gates, double-build determinism check of the release package.
- Checks performed: navigation and canonical-ownership review against general AI-context engineering principles; instruction actionability; active-vs-historical separation; wrapper/registry relationships; schema consistency; validation integrity and fail-open behavior.

### Pass B: Repository-Aware Skill Review

- Policies and skills used: `ai-context-auditor` skill contract, `ASSESSMENT-ARTIFACT-POLICY.md`, `WORKFLOW-GATE-POLICY.md`, `AI-CONTEXT-LANGUAGE-POLICY.md`, `AI-CONTEXT-BOUNDARY.md`, `GIT-COMMIT-POLICY.md`, `AI-CONTEXT-VERSION-POLICY.md`, canonical skill registry.
- Checks performed: does the repository follow its own declared contracts; per-finding verification of all 20 findings from the 2026-07-07 informal review; audit of every surface added or rewritten in v0.3.0.

### Delegation

- Sub-agents used: 3 bounded read-only workers.
- Assigned surfaces: (1) re-verification of the 20 prior findings; (2) v0.3.0 new surfaces (skills, assessment/backlog infra, packaging, validators, workflow records); (3) v0.4.0 planning branch review (reported separately in conversation). All high-severity verdicts re-verified by the main agent (wrapper description lines, gate execution, validator runs).

### Discovery Accelerators

| Tool / generated view | Source revision or input digest | Freshness / dirty state | Scope and exclusions | Unsupported relationships | File-backed fallback |
| --- | --- | --- | --- | --- | --- |
| None / not applicable |  |  |  |  |  |

## Repository Context Inventory

| Surface | Files / Size | Audience | Scope | State | Notes |
| --- | ---: | --- | --- | --- | --- |
| Root entries | 5 files | mixed | universal | active | `CLAUDE.md` thin `@AGENTS.md` pointer, validator-enforced |
| `.ai/**` | ~200 files | agent-facing | universal + dotnet-backend | active | 14 canonical skills, 18 sub-agent role prompts, scripts, distribution profiles |
| `.dev/**` | ~250 files | mixed | governance + knowledge | active + historical | 36 workflow dirs (16 post-adoption validated), 9 backlog items, 0 durable assessments before this one |
| Runtime wrappers | `.agents/` + `.claude/` (+ `.codex/`, `.github/agents/`) | agent-facing | runtime | active | 14 wrappers per runtime root; parity validator passes |

## Strengths

1. The consistency tooling missing in the 2026-07-07 review now exists and passes at HEAD: `validate-ai-context.py` (wrapper metadata, exact-case references, index integrity, language policy over 286 files, bilingual root parity, rule ownership, 32 canonical manifests, 10 capability mappings), plus workflow/assessment/version/commit/shell-asset validators, backed by 107 GWT tests under `.ai/scripts/tests/`.
2. Release packaging is deterministic (two builds of `v0.3.0` byte-identical: tar.gz `fc9e3b11…`, zip `7d29a86c…`) and `publish-release.yml` is defense-grade: `permissions: {}`, annotated-tag-only, tag re-verification between jobs, draft-ownership marker, byte-level asset comparison after upload.
3. The assessment/backlog/workflow governance model (`ASSESSMENT-ARTIFACT-POLICY.md`, `WORKFLOW-GATE-POLICY.md`, `.dev/backlog/`) is internally coherent with full bidirectional traceability; all 74 v0.3.0-era workflow task JSONs are completed and every declared deferral maps to a backlog item.
4. `.dev/INDEX.md` was rebuilt: every cataloged path now resolves with exact case (previously ~20% dead or case-broken).
5. Skill spec schema unified: 14/14 `skill.yaml` use `wrapper_path`, declare `status` and `portability`; one template family remains; 11 specs declare `capability_slots`.
6. Broken automation genuinely retired: `generate-check-scripts-from-md.sh`, `parse-md-rules.py`, `generated/`, `check-archive-compliance.sh` removed; survivors carry explicit legacy/advisory disclaimers; shell exec bits fixed (14/14) and `check-all.sh` now fails loudly instead of silently skipping non-executable scripts.
7. Language migration executed for agent-facing Markdown: `.ai` core docs and the canonical skill registry are now pure English; `.dev/standards/**` Markdown is 101/102 CJK-free.
8. New skills (`ai-context-auditor`, `ai-context-upgrader`) are well-specified, wrapper-synced byte-identically modulo runtime labels, with all referenced paths resolving exact-case.

## Findings

| ID | Severity | Finding | Evidence | Impact | Recommendation | Owner / Next Skill |
| --- | --- | --- | --- | --- | --- | --- |
| AIC-001 | HIGH | Five Claude wrappers still route on "Use when **Codex** needs" (open since 2026-07-07; the new wrapper validator checks path parity, not runtime-appropriate wording) | `.claude/skills/{spec-author,requirement-author,bdd-gwt-test-designer,problem-frame-author,ddd-ca-hex-architect}/SKILL.md:3` | Claude skill routing degraded on 5 of 14 skills | Reword to runtime-neutral or "Claude" phrasing; extend `validate-ai-context.py` wrapper check to reject cross-runtime tokens in `description` | `ai-context-governance` |
| AIC-002 | HIGH | Legacy standards and learning content still teach the forbidden Handler shape: ✅ examples inject a repository into a Handler / teach static Wolverine `Handle()` as the use case, contradicting the canonical boundary | `best-practices.md:66-77`; `anti-patterns.md:~125-138`; `LEARNING-PATH.md:120-124` vs `USECASE-COMMAND-HANDLER-RELATIONSHIP.MD:161-174`; also `SPEC-GUIDE.MD:~22` defines handler as "the application executor in code" | Agents and newcomers loading these surfaces reproduce the anti-pattern the newest standard forbids | Rewrite the three ✅ examples and the SPEC-GUIDE handler definition; add precedence banners pointing to the canonical standard (overlaps v0.4.0 plan AIC-010 scope) | `ai-context-governance` |
| AIC-003 | HIGH | The required quick gate is unrunnable on a stock environment: `check-all.sh` invokes bare `python` (13/14 required checks fail on macOS/Ubuntu defaults); with `python3`, 13/15 fail on missing PyYAML (no dependency bootstrap or declaration); `global.json` pins SDK `10.0.300` (`rollForward: latestMajor` cannot satisfy from 10.0.203); `shell-assets.yaml:24-37` bakes the bare-`python` form into the parity contract; `release.yaml:55` cites "15/15 required post-merge quick checks" as evidence | executed: `bash .ai/scripts/check-all.sh --quick` → `line 160: python: command not found`; `python3 …validate-ai-context.py` → `ModuleNotFoundError: No module named 'yaml'` | Governance enforcement is de facto author-machine-only; passing-gate claims are irreproducible; fail-closed but misleading as release evidence | Use `python3` (and update `shell-assets.yaml` in the same change), add a documented bootstrap (venv/requirements or vendored fallback), relax or gate the SDK pin, declare the Python ≥3.10 floor for repo-side scripts | `ai-context-governance` |
| AIC-004 | HIGH | `ai-context-auditor` ships three orphaned templates encoding the superseded workflow-persistence model, contradicting its own contract and the assessment policy | `.ai/assets/skills/ai-context-auditor/templates/{workflow-locator-template.yaml:12,17, ai-context-audit-workflow-plan-template.md:35, ai-context-audit-task-template.json:26}` vs `skill.yaml:29` and `references/output-contract.md:31` | An agent browsing templates can be misdirected into the forbidden pre-v0.3.0 persistence shape | Delete the three templates or move them to a clearly-labeled historical area; none are referenced by `skill.yaml` | `ai-context-governance` |
| AIC-005 | HIGH | `check-test-compliance.sh` still resolves `BASE_DIR` to the repository's parent directory and scans outside the repo, passing vacuously | `check-test-compliance.sh:25` `BASE_DIR="$(cd "$SCRIPT_DIR/../../.." && pwd)"` | A registered (advisory) check reports success without checking anything in-repo | Fix path depth (`../..`) or retire the script (backlog TOOL-001 territory) | `ai-context-governance` |
| AIC-006 | MEDIUM | `.dev/workflows/INDEX.MD` advertises the deleted `templates/` directory and lists a completed workflow under "Active Workflows" | `.dev/workflows/INDEX.MD:7-11,61-65` vs `.dev/workflows/README.MD:46-51` and `2026-07-15-v0-1-downstream-feedback-adoption/workflow.yaml` (`completed`) | Primary workflow navigation surface disagrees with reality on two rows | Regenerate the index; add index rows to the workflow-artifact validator's checks | `ai-context-governance` |
| AIC-007 | MEDIUM | No CI runs the governance validators; the only CI is packaging-scoped | `.github/workflows/{package-candidate.yml:4-10,publish-release.yml}`; no workflow invokes `validate-ai-context.py` or the GWT suite on doc/skill PRs | Combined with AIC-003, all context governance enforcement is local-and-voluntary | Add a validation workflow running the Python validators + GWT tests on PRs touching `.ai/**`, `.dev/**`, wrappers | `ai-context-governance` |
| AIC-008 | MEDIUM | Intra-standards contradictions persist: `DateTime.UtcNow` in ✅ aggregate templates vs its prohibition; "camelCase for methods"; first wrong/correct connection-string pair identical; `Lab.MessageSchemas` vs `<Company>.BoundedContextContracts` | `aggregate-standards.md:120,193,222` vs `anti-patterns.md:276`; `CODE-REVIEW-CHECKLIST.md:24`; `ASPNET-CORE-CONFIGURATION-CHECKLIST.md:10-16`; `coding-standards.md:122` vs `project-structure.md:21,64,224` | Agents generating from these standards violate sibling standards | Mechanical fixes; several overlap v0.4.0 plan findings (AIC-012 there) | `ai-context-governance` |
| AIC-009 | MEDIUM | Examples verification story remains vestigial: `.versions.json` tracks 1/136 files and its `source` path died when `src/` was emptied; three overlapping indexes; `TEMPLATE-INDEX.md` still claims to mirror the source template index ("Last update: 2026-02-01"); three near-duplicate BDD example folders | `.dev/standards/examples/{.versions.json,README.md,INDEX.md,TEMPLATE-INDEX.md}`; `bdd-gherkin-example/`, `bdd-given-when-then-example/`, `bdd-gherkin-test/` | "Verified templates" claims exceed evidence (matches unmerged ASM-20260715-002#AIC-003) | Adopt the v0.4.0 evidence-tier contract; delete `.versions.json`; collapse indexes | `ai-context-governance` (v0.4.0 workflow) |
| AIC-010 | MEDIUM | Registry-adjacent tables undercount: `AGENTS.md` Skill Routing lists 13 of 14 skills (missing `spec-compliance-validator`; mirrored in `AGENTS.zh-TW.md`); `SUB-AGENT-SYSTEM.MD` routing table lists 17 of 18 role prompts (missing `context-translator`, which has live wrappers in 3 runtime roots) | `AGENTS.md:171-186`; `AGENTS.zh-TW.md:167-181`; `.ai/SUB-AGENT-SYSTEM.MD:17-35` vs `.dev/agents/` (18 dirs) | Routing tables are the discovery surface; omissions hide capabilities | Add the missing rows; consider registry-vs-table parity in the validator | `ai-context-governance` |
| AIC-011 | MEDIUM | `spec-compliance-validator` rules retain foreign/stale contract details: "ezSpec GWT semantic alignment" (Java ecosystem term; declared stack is xUnit+BDDfy), validation levels jump L1→L3, and the hardcoded `src/…`+`src/tests/…` layout no longer exists in-repo and is not marked target-relative except one hedge | `.ai/assets/skills/spec-compliance-validator/references/spec-compliance-rules.md:39,46-47,51-58` | Validator guidance misleads in any repo not shaped like the retired source project | Replace ezSpec wording, renumber levels, parameterize layout via target-repo evidence | `ai-context-governance` |
| AIC-012 | MEDIUM | `.dev/standards/guides/` still violates the standards-vs-guides boundary (3 how-to guides; README says "translated from the source stack") and contradicts `implementation-guides` on Migrations layout (2-way now) | `.dev/standards/guides/README.md:3`, `DATABASE-MIGRATION-GUIDE.md:29-30` vs `src/knowledge/dotnet-backend/guides/PERSISTENCE-CONFIGURATION-GUIDE.md:29-33` | Placement rules the repo itself declares are broken by its own tree | Move the three guides; reconcile the layout story in `project-structure.md` | `ai-context-governance` |
| AIC-013 | MEDIUM | Repo-side tooling has an undeclared Python ≥3.10 floor: `Path.write_text(newline=)` in `ai_context_package.py:507` and test fixtures — 44/107 GWT tests fail and the package builder crashes on Python 3.9; only the target-side planner declares 3.11+ | `ai_context_package.py:507`; `.ai/distribution/README.md:19`; `.ai/scripts/README.md` (no version floor) | Local reproduction of gates and packaging silently assumes a newer Python than declared | Declare the floor in `.ai/scripts/README.md` and guard scripts with a version check | `ai-context-governance` |
| AIC-014 | LOW | Two prompt guides still claim "目前它不是正式 skill" while `requirement-author`/`spec-author` skills exist on all runtimes | `REQUIREMENT-DESIGNER-PROMPT-GUIDE.md:5`; `SPEC-DESIGNER-PROMPT-GUIDE.md:5`; contradicted by `REQUIREMENT-AND-SPEC-DESIGNER-STRATEGY.md:114` in the same folder | Same-folder dual truth | Update the two status lines | `ai-context-governance` |
| AIC-015 | LOW | Source-project residue persists: `/path/to/ai-plan` copy command, `ezapp-2.0.0` intent wording (3 files), `ScrumTeam` examples, `EZDDD-FRAMEWORK-REFERENCE.md` 30-line zh-TW TODO stub, examples TODO "until ezDDD/ezapp ports exist" | `quick-setup.md:31-32`; `DUAL-PROFILE-CONFIGURATION-GUIDE.md:15,80`; `PROFILE-CONFIGURATION-COMPLEXITY-SOLUTION.md:160,169`; `standards/templates/profile-isolated-configurations.md:6-7`; `aggregate-standards.md:46,57`; `examples/usecase/README.md:18` | Erodes the templatization claim; harmless individually | Sweep with neutral placeholders (overlaps v0.4.0 profile work) | `ai-context-governance` |
| AIC-016 | LOW | `skill-discovery-playbook.md` still maps refactor-type work to a `refactoring` capability slot that no longer exists anywhere else (model otherwise aligned at 10 slots) | `skill-discovery-playbook.md:58` vs `routing-playbook.md:18-27`, `capability-profile.md:20-31` | Discovery can resolve to a ghost slot | Remap to `local-change` | `ai-context-governance` |
| AIC-017 | LOW | No filename-case naming convention exists; mixed `.MD`/`.md` persists within single directories (mitigated: exact-case *reference* lint now exists) | `src/skills/adr/references/WHEN-TO-CREATE-ADR.MD` beside `README.md`; `.dev/README.MD` beside `.dev/INDEX.md`; no policy hit in `.dev/standards/` | Authoring friction; portability annoyance | Adopt a convention prospectively; enforcement already half-built | `ai-context-governance` |
| AIC-018 | LOW | Two implemented requirements still read "Approved for implementation" without the Implementation Outcome section the repo's own convention requires | `DOTNET-VALIDATOR-PHASE-2-REQUIREMENTS.MD:8`; `HISTORICAL-CONTEXT-NORMALIZATION-REQUIREMENTS.MD:8` | Requirement status is not trustworthy at a glance | Backfill the two sections | `ai-context-governance` |
| AIC-019 | LOW | Post-rename and post-migration crumbs: dead lowercase `agents.zh-tw.md` exclude pattern and requirement references; language-policy example casing (`agents.en.md`/`README.zh-tw.md`) contradicts the enforced convention; auditor `skill.yaml:41` residual "workflow metadata" wording; assessment infra was production-unexercised before this assessment (validator passed vacuously on 0 assessments) | `.ai/distribution/profiles/dotnet-backend.yaml:200`; `DOMAIN-UBIQUITOUS-LANGUAGE-REQUIREMENTS.MD:205,213`; `AI-CONTEXT-LANGUAGE-POLICY.md:32-37`; `.ai/assets/skills/ai-context-auditor/skill.yaml:41` | Hygiene | Sweep in one pass | `ai-context-governance` |

## Baseline And Skill Comparison

### Confirmed

- Both passes agree on all HIGH findings. Pass A (general principles) flagged AIC-001/002/003/004/005 independently; Pass B confirmed each also violates a specific repository contract (wrapper thinness+routing, canonical precedence, shell-asset parity registry, `ASSESSMENT-ARTIFACT-001`, validation integrity).

### Added By Repository-Aware Review

- AIC-010 (routing-table parity), AIC-012 (standards-vs-guides boundary), AIC-018 (Implementation Outcome convention), AIC-019 casing-policy internals — these exist only relative to the repo's own declared contracts.

### Downgraded Or Deferred

- Language policy violations: previously HIGH (2026-07-07), now LOW residue — the Markdown migration executed; remaining CJK sits in shell/py comments, two zh trigger lines in `ai-context-auditor/skill.yaml:18-19`, and one quoted-term line in `WORKFLOW-GATE-POLICY.md:27` (defensible as quoted triggers).
- ADR emptiness: downgraded to accepted-by-design; `adr/INDEX.md` now states the governance-only catalog rule, and decisions landed into standards. Retroactive pointer entries remain a nice-to-have.
- `check-test-compliance.sh` (AIC-005) severity is tempered by its explicit legacy/advisory labeling; kept HIGH because a registered check that scans the wrong tree is misleading validation.

### Overturned

- 2026-07-07 claim "no sync tooling; drift is structurally inevitable" is overturned for path/wrapper/index/language surfaces — `validate-ai-context.py` covers them and passes. It remains true only for semantic wording (AIC-001 proves the residual gap).
- 2026-07-07 claim "zero CI" is overturned for packaging; narrowed to "no CI for governance validators" (AIC-007).

### Prior-Finding Disposition (2026-07-07 informal review, 20 findings)

- FIXED (5): copilot-instructions dangling references removed; `.dev/INDEX.md` rebuilt clean; skill spec schema unified; guides index rot removed by redesign; Gherkin storage guide rewritten as target-conditional.
- PARTIALLY-FIXED (7): learning-path dead refs fixed but anti-pattern teaching remains; language migration done for Markdown, residue in scripts; automation pipeline retired but gate unrunnable on stock env (new: AIC-003) and one path bug survives (AIC-005); SPEC-GUIDE domains claim fixed but handler definition remains; ADR index honest but empty; slot model aligned except one ghost reference; slice-implementer modes complete, spec-compliance rules not.
- STILL-OPEN (8): Codex wrappers (AIC-001); best-practices/anti-patterns contradictions (AIC-002); DateTime.UtcNow/camelCase/connection-string/MessageSchemas cluster (AIC-008); examples versioning (AIC-009); prompt-guide status lines (AIC-014); source residue (AIC-015); standards/guides boundary (AIC-012); case convention (AIC-017); requirement outcomes (AIC-018).

## Validation

| Check | Result | Evidence / Notes |
| --- | --- | --- |
| Git state | pass | subject `main@82b88b7` clean at audit start; artifact branch `claude/assessment/asm-20260717-004` created before artifacts |
| Registry and wrapper parity | pass (structural) | `validate-ai-context.py`: 14 canonical skills, 2 runtime roots, 32 canonical manifests — pass; semantic wording gap evidenced by AIC-001 |
| Path and reference checks | pass | `validate-ai-context.py` exact-case reference lint pass; `.dev/INDEX.md` catalog re-verified programmatically |
| Schema / structured file parse | pass | `validate-workflow-artifacts.py` (16 workflows, 9 backlog items) pass; `validate-assessment-artifacts.py` pass; `validate-ai-context-versions.py` (4 releases) pass; `validate-shell-assets.py` pass; `validate-git-commits.py` pass — all under venv Python with PyYAML |
| Repository context checks | fail (environmental, reproducible) | `bash .ai/scripts/check-all.sh --quick` → 13/14 required checks fail (`python: command not found`); with `python3`: 13/15 fail (`No module named 'yaml'`); `dotnet test` unrunnable (SDK pin). See AIC-003 |
| Packaging determinism | pass | double-build of `v0.3.0` byte-identical (tar.gz `fc9e3b11…`, zip `7d29a86c…`); `validate-ai-context-package.py` pass |

### Skipped Validation

- `dotnet test` for `tools/DotnetBackendAnalyzers.Tests` and `tools/DotnetBackendValidation.Tests` — blocked by the `global.json` SDK pin (10.0.300 unavailable locally); recorded as part of AIC-003 rather than asserted as pass or fail.
- Semantic parity of `AGENTS.md` vs `AGENTS.zh-TW.md` beyond structural checks (the validator itself disclaims semantic parity); structural mirror confirmed.

## Recommended Action Order

1. AIC-001 — reword the 5 Claude wrapper descriptions and extend the wrapper validator to reject cross-runtime tokens (small, unblocks routing today; decision-free).
2. AIC-003 + AIC-013 — make the quick gate runnable on a stock machine (`python3`, dependency bootstrap, declared Python floor, SDK-pin gate) and update `shell-assets.yaml` in the same change; then stop citing gate results that a fresh clone cannot reproduce.
3. AIC-004 + AIC-006 — delete the three orphaned auditor templates; regenerate `.dev/workflows/INDEX.MD` (both are one-commit fixes to active discovery/contract surfaces).
4. AIC-002 — rewrite the legacy Handler examples and the SPEC-GUIDE handler definition, or land precedence banners as an interim guard (coordinate with the v0.4.0 workflow, which owns the adjacent AIC-010 finding there).
5. AIC-007 — add a governance-validation CI workflow.
6. Remaining MEDIUM (AIC-008/009/010/011/012) — fold into the v0.4.0 remediation workflow where scopes overlap (examples evidence tiers, namespace leak, standards placement); execute the rest as small governance slices.
7. LOW sweep (AIC-014..019) — one hygiene pass.

## Deferred Items

- Retroactive ADR pointer entries for the D1-D12 decision sets — improved by the honest `adr/INDEX.md` rule; optional.
- Filename-case convention adoption (AIC-017) — propose prospectively; retrofitting all filenames is not worth churn before v0.4.0 restructuring lands.
- v0.4.0 planning-branch amendments — reported separately in conversation (release/migration task, ARCH-001 scope split, unblocking decision-free fixes, V040-DEC-002 strength pinning); owned by that workflow, not this assessment.

## Appendix

### Commands Run

```text
git fetch --all --prune; git rev-parse origin/main
git diff --stat a4f46e2..82b88b7; git log --oneline a4f46e2..82b88b7
grep -rl 'Codex' .claude/skills/*/SKILL.md
ls .github/workflows/; find .ai/scripts -name '*.sh' -perm +111 | wc -l
bash .ai/scripts/check-all.sh --quick                      # 13/14 required FAIL: python not found
python3 .ai/scripts/validate-ai-context.py                 # ModuleNotFoundError: yaml (stock)
<venv>/bin/python .ai/scripts/validate-ai-context.py       # PASS: 16 indexes, 14 skills, 286 files
<venv>/bin/python .ai/scripts/validate-workflow-artifacts.py    # PASS: 16 workflows, 9 backlog
<venv>/bin/python tools/maintenance/validate-assessment-artifacts.py  # PASS: 0 assessments (pre-existing)
python3 .ai/scripts/build-ai-context-package.py --version v0.3.0 (x2, checksum compare)  # deterministic
```

### Notes

- Identity provenance: this assessment was originally allocated as `ASM-20260716-001` on 2026-07-16; that ID was independently published on main by the v0.4.0 remediation verification, so this unpublished artifact was reallocated to `ASM-20260717-004` per the assessment policy collision rule. Audit content and subject revision are unchanged.
- The 2026-07-07 informal review (subject `a4f46e2`) was conversation-mode output retained untracked under `docs/review-report/`; this assessment is the first durable one and adopts its findings as the comparison baseline.
- The unmerged assessments ASM-20260715-001/002 on the v0.4.0 planning branch were produced against the same subject commit (`82b88b7`) with a standards-focused scope; where scopes overlap (examples evidence, profile drift, namespace leak) their findings and this report agree. Finding IDs here are namespaced by this assessment ID and do not collide.

## Lifecycle Handoff

- Assessment path: `.dev/assessments/ASM-20260717-004/report.md`
- Stable finding references: `ASM-20260717-004#AIC-001` … `ASM-20260717-004#AIC-019`
- Remediation owner: `ai-context-governance`
- Related remediation workflow: `2026-07-16-v0-4-0-ai-context-remediation` (unmerged planning branch; overlapping scope noted per finding)
- Verification assessment: to be created after remediation as a new assessment
- Remediation intentionally not performed by this skill: `yes`
