# Evidence and scope disposition

Inspected base: `758a7f51c745ee61625cc089b593367fd1a45533`, branch `codex/2026-09-23-installation-update-design`, worktree `F:/framework-next/345`. Initial porcelain empty; persistent common Git directory `C:/Github/YuChia/ai-collaboration-prompts-dotnet-backend/.git`. No C: checkout writes or product execution.

Owning skill: [canonical ai-context-governance](../../../../.ai/assets/skills/ai-context-governance/skill.yaml) via [wrapper](../../../../.agents/skills/ai-context-governance/SKILL.md). Authority: [U001](../../../standards/FRAMEWORK-REDESIGN-EXECUTION-OVERRIDE.md), [execution plan](../../../assessments/ASM-20260923-00-6oq/execution-plan.md), [P6 scope](../../../workflows/2026-09-23-framework-redesign-control/reports/p6-installation-design-scope.md), [coordinator task](../../../workflows/2026-09-23-framework-redesign-control/tasks/ISSUE-345.json).

## Actual source, not a generated candidate

Graph get_architecture on project ai-collaboration-prompts-dotnet-backend, path src/distribution returned root nodes but zero scoped nodes/edges and no exact current SHA. It cannot establish discovery/completeness here. Fallback: scoped git ls-files/ls-tree, direct tracked content and ast.parse only. No product imports, build, fixture or CLI invocation. These are source-reading observations, not verified behavior.

| Path | Exact blob at base | Evidence |
| --- | --- | --- |
| src/distribution/assembly.py | 6a0f9f0581959efada77d1a1336cf21b67b619fe | Document shapes, content identity, completion-last, Windows mode limitation; no installer. |
| src/distribution/selection.py | 5773973a457fdb7c8f8c013f9c325c13fd9121dc | Member identity, exact mapping/closure and generated output fields. |
| src/distribution/codex.py | 55c4bf0394b0d753c6749b09deccab3ff4c4d0d5 | Exact framework-prefixed Codex entry and installed-relative links. |
| src/adapters/codex/skill-entry.md.template | 43cdbf2fbc94fdcf38f04be63467e960a9537131 | Project/config/operation guidance, no executable install guard. |
| src/distribution/data.py | 2d971b3d95ee66f7604719046f13cdc90c394305 | Canonical JSON and closed data/path helpers. |
| src/distribution/git_source.py | f6b041d068fe553047f6bd615b7b13b8d2d6e122 | Regular raw Git blobs/modes/OIDs, exact commit/no fetch. |
| src/distribution/package.py | ffb0d580021d2c8bd33bd4aa0dbb804b5f81b135 | Shared metadata loader owner, v1/v2 source at base. |
| src/distribution/manifest.yaml | 7bbc4d27f12079ce3574dc5265146c959018bfed | Five package mappings/four profiles. |
| src/profiles/collaboration.yaml | 656d62ec54291f6d133c2b3b768dcf36567967eb | Five-package exact selection. |
| src/profiles/knowledge.yaml | 8061bd801cc6065f9997b912694859979a1715b5 | Knowledge subset. |
| src/profiles/lesson-minimal.yaml | 540645382e5b40ae79e0069bf2ee5f36cd816761 | Lesson 0.2.0. |
| src/profiles/work-management.yaml | 2f6c6c3ed372fdd47fe0c368699960b4749ca815 | Work-management subset. |
| source-layout/design.md under framework-next | 7e64a71dd7eeb73cd894708649f05398b105bb25 | P1 ownership/delta/recovery/dogfood intent. |
| p4-selected-contract.md under framework-next | 6f6eca4632227fae2b5babb2bb0fb7e51fdf68c8 | P4 selection, source/mapping still independent. |

Direct YAML declared counts: lesson@0.2.0 9, adr@0.1.0 8, standards-promotion@0.1.0 9, pr@0.1.0 10, local-backlog@0.1.0 8; total 44. Profiles: lesson-minimal 9 + 1 runtime entry; knowledge 26 + 3; work-management 18 + 2; collaboration 44 + 5. Runtime counts derive from adapter loop, not a build. All four select Codex. No P4/P5 package is inferred from a future assignment.

Selected references: [P1](../source-layout/design.md), [P2 interface](../distribution-implementation/README.md), [P3 metadata/mapping](../distribution-implementation/metadata-v2.md), [P4 selection](../p4-selected-contract.md), [initial P5 scope](../../../workflows/2026-09-23-framework-redesign-control/reports/p5-capability-consolidation-scope.md), actual Lesson metadata/config. Lesson reads record 1.0.0/2.0.0, writes 2.0.0, mutation migration unsupported; derive creates new identity.

## Subsequent P5 input without base mutation

Coordinator supplied commit `842b73ca09d701d1561109255193d80439dc996b`. Read only with git show/ls-tree; no merge/cherry-pick/source write. [p5-selected-contract.md](https://github.com/YuChia-Wei/ai-collaboration-framework/blob/842b73ca09d701d1561109255193d80439dc996b/.dev/design/framework-next/p5-selected-contract.md) blob `0427cec4ab0c4158677695fb5ba6235434322b57`; [implementation-slices.md M01](https://github.com/YuChia-Wei/ai-collaboration-framework/blob/842b73ca09d701d1561109255193d80439dc996b/.dev/design/framework-next/capability-consolidation/implementation-slices.md) blob `2b64a933a86c1fd260ffcaf191394cc376f7fd7a`.

M01 now selected for design: only actual-needed closed P2 project/local JSON exact integer 1->2, all other semantic values/absence unchanged, no defaults/permissions/namespaces added, conditional durable pair recovery. No migration implementation/execution. D342-01 selects metadata v3 instruction/tool union and restricted null configuration; #346 owns shared loader/adapter, #347/#348 own future packages. None is counted as delivered at this base. Contract explicitly preserves this distinction and remaining activation-interface selection.

## Live Issue overlap

Read-only gh issue view for five Issues on 2026-09-23 approximately 09:31 +08:00 returned all OPEN. Initial sandbox request failed because proxy 127.0.0.1:9 refused connection; authorized read-only network escalation succeeded. No credential diagnosis, Issue/Project/settings mutation.

| Issue | Scope | #345 disposition |
| --- | --- | --- |
| [#345](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/345) | P6 design only | Local design checkpoint; implementation/online closeout separate. |
| [#43](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/43) | Existing AI repository intake/collision taxonomy | Preserve intent; refuse unowned collisions. No semantic merge/provider intake/provenance/fixtures/pilot. Open/unfulfilled. |
| [#305](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/305) | Windows path/staging exposure and real evidence | Budget actual paths/short staging proposal. No old 677-file metrics reused as new result, no proven fix. Open/unfulfilled. |
| [#149](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/149) | Runtime comparison/CLI-validator strategy | No Go/Rust/.NET prototype, runtime ADR, binary/service or validator engine. Open/unfulfilled. |
| [#168](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/168) | Installable read-only CLI preview | Product API proposal does not enable preview mutation commands or satisfy preview acceptance. Open/unfulfilled. |

## Limited checks

Actual: Git identity/scope/content, seven distribution modules ast.parse, direct YAML profile/member extraction, live Issue reads. Design UTF-8/JSON/YAML/reference/diff and planned-message outcomes are recorded in [workflow](../../../workflows/2026-09-23-installation-update-design/workflow.yaml).

Product CLI/help, schema validation, tests/fixtures, package/build/install/migration/compatibility, I/O/performance, independent audit/lease/effective-rule/receipt/handoff tooling, hosted checks and CI: deferred-by-owner, authority U001, owner program #322 coordinator / P7, next action select redesigned checks after implementation. Syntax is not schema/runtime/durability/platform/independent-review evidence.
