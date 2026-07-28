# REL-004 AI Context Release Closeout Discussion Context

## Document Status

This file preserves the discussion context that led to `REL-004`. It is a
planning reference, not an approved skill design, implementation workflow,
portable product contract, or release assignment.

## Triggering Observation

After the owner created and pushed the immutable `v0.7.0` tag, the remaining
behavior was conceptually narrow: verify the tag and hosted Release, reconcile
repository registries, close the existing workflow, and integrate one PR.

The release was published shortly after the tag, but the complete closeout took
about nineteen minutes. The elapsed time came primarily from execution overhead
rather than the release-state checks themselves:

- the broad `ai-context-governance` surface and multiple repository policies
  were rediscovered before the narrow post-tag action was identified;
- local execution retried unavailable Windows Python, a bundled Python without
  PyYAML, denied WSL startup, `uv`, and a Windows encoding failure before a
  working UTF-8 command was established;
- thirteen registry, backlog, roadmap, release, and workflow files were updated
  manually, including one failed patch-context attempt;
- one incorrect test-discovery command was replaced and the validation suite
  was repeated before commit, after commit, and after merge;
- the ready pull request then waited about two minutes for its Ubuntu hosted
  check before merge.

This evidence suggests a repeatable source-repository closeout operation, but
it does not by itself prove that a new skill is the correct product boundary.

## Problem To Preserve

Two concerns are intentionally kept together for later deliberation:

1. simplify this repository's post-tag release closeout so an agent executes a
   small deterministic path instead of reinterpreting broad AI-context
   governance; and
2. prove whether the capability is source-only, how its canonical and runtime
   files are isolated, and whether any part belongs in the published framework.

The second concern must be resolved before implementation because the current
distribution profile broadly selects `.ai/assets/**`, `.ai/scripts/**`,
`.agents/skills/**`, and `.claude/skills/**`. Placement alone cannot be assumed
to prevent product leakage.

## Naming Discussion

The owner requested the `ai-context-` namespace for consistency.

| Candidate | Current assessment |
| --- | --- |
| `ai-context-release-closeout` | Preferred discussion candidate. `Closeout` naturally means the administrative completion after the main release action. |
| `ai-context-release-finalizer` | Grammatically correct and consistent with actor-style names such as `auditor` and `upgrader`, but it emphasizes an executing role. |
| `ai-context-release-finalization` | Grammatically correct but longer and more process-oriented. |
| `ai-context-release-finalize` | Understandable as an identifier but less idiomatic English. |
| `finalize-ai-context-release` | Natural verb-led English but does not preserve the requested namespace-first pattern. |

No name is approved by this attachment. The working recommendation is
`ai-context-release-closeout` with display name `AI Context Release Closeout`.

## Proposed Responsibility Boundary

The candidate capability would trigger only after the owner has created and
pushed an annotated tag and hosted publication has succeeded. Its narrow
responsibility would be:

1. verify immutable tag, peeled commit, hosted run, Release state, and governed
   asset set;
2. reconcile the existing release, backlog, roadmap, and workflow records;
3. execute one declared finalization validation bundle; and
4. create the repository closeout commit and follow the existing PR-only Git
   policy.

The candidate would not prepare a release, build a candidate, create or move a
tag, republish a Release, start a successor version, run a general AI-context
audit, or remediate unrelated findings.

## Skill Dependency Boundary

The preferred design has no runtime dependency on another skill.

- Packaged `ai-context-governance` must not mention, require, invoke, or route
  to a source-only closeout skill.
- Source-repository routing may select the closeout skill directly from an
  excluded root entry or another explicitly source-only registry.
- The closeout skill may consume repository release records, validators, and
  Git policy as file-backed contracts without invoking governance, GitHub,
  workflow-orchestration, review, or audit skills.
- Portable registries and guides must not retain a skill name or path that is
  absent from the package.

This is a parallel responsibility boundary, not a skill chain.

## Product-Isolation Alternatives

The discussion identified two alternatives that still require a decision:

### A. Existing Canonical Roots Plus Exact Exclusions

Store the canonical spec and runtime wrappers beside portable skills, then add
exact source-only distribution exclusions and regression tests.

This minimizes repository-structure change but risks ambiguity because local
registries and portable registries share the same roots.

### B. Dedicated Source-Only AI Root

Introduce a source-only canonical location such as `.ai/source/skills/` and a
source-only script/test location, while keeping only the runtime wrappers in
their discoverable roots with exact package exclusions.

This makes the boundary visible by placement but requires deliberate updates
to repository indexes, wrapper parity validation, and source-context policy.

Neither alternative is selected. Any adopted design must prove absence from
all package components and prevent packaged text from linking to excluded
files.

## Runtime And Failure-Containment Discussion

The smallest proposed runtime policy is:

1. use a supported Python environment when available;
2. otherwise use `uv` to provide a temporary supported environment; and
3. when neither route is available, return `blocked-by-environment` before any
   repository write.

The skill must not silently install tools, fall back to manual multi-file
editing, or count hosted checks as missing local validation.

The preferred failure-containment model avoids broad rollback:

- perform evidence collection and runtime preflight without writes;
- create and validate all proposed changes in an exact temporary Git worktree;
- leave the primary worktree unchanged when generation or validation fails;
- apply only the validated patch when the base commit and patch digest still
  match;
- before push, preserve a failed continuation branch for inspection rather
  than using a broad destructive reset; and
- after push, PR, merge, tag, or publication, use fix-forward behavior and
  never rewrite shared history or mutate the immutable tag and Release.

## Decisions Required Before Implementation

1. Approve the skill identifier and display name.
2. Decide whether the capability is permanently source-only or potentially a
   future portable capability.
3. Select the canonical source-only placement and local registry strategy.
4. Define exact package exclusions and negative package regression evidence.
5. Confirm the zero-skill-dependency rule and portable governance independence.
6. Confirm Python, `uv`, and blocked-by-environment behavior.
7. Confirm temporary-worktree transaction and post-push fix-forward boundaries.
8. Define whether successful completion stops at a ready PR or includes hosted
   checks, merge, and local `main` synchronization.
9. Decide whether existing source release templates and runbook responsibilities
   remain under governance or move into the source-only capability.

## Explicit Non-Decisions

- No new skill is approved or implemented.
- No portable `ai-context-governance` contract is changed.
- No distribution path is included or excluded by this discussion alone.
- No source-only root is established.
- No Python, `uv`, hosted-only, rollback, or merge mode is selected.
- No successor release is activated.

## Suggested Handoff

When the owner is ready to decide the open questions, start one dedicated
AI-context governance workflow sourced from `REL-004`. The workflow should
record the owner decisions before creating canonical skill files, runtime
wrappers, scripts, or package rules.
