# Candidate assembly delivery

- Report: `remediation-report-2026-09-23-candidate-assembly`; workflow `2026-09-23-candidate-assembly`; owner `ai-context-governance`; status `final` for local implementation delivery.
- Created/updated: `2026-09-23T01:59:15+08:00`.
- Template: `.ai/assets/skills/ai-context-governance/templates/ai-context-remediation-report-template.md`, version `2.0.1`, adapted under U001.
- Baseline: `ASM-20260923-00-6oq`; bounded work item [#331](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/331). No whole-assessment finding closure or independent verification assessment is claimed.
- Delivery identity: containing commit; exact HEAD and actual commit message are read back after the commit and returned to the coordinator.

## Completed scope

`src/distribution/` owns strict JSON-model YAML parsing, version 1 package consumption, Git blob selection, metadata/manifest closure comparison, explicit required/optional dependencies, path/ownership collisions, supported document/schema resource references, Codex projection and new candidate assembly. `src/profiles/lesson-minimal.yaml` selects `lesson@0.1.0` and Codex. The adapter template lives in `src/adapters/codex/`. `tools/build-development.py` is only maintainer invocation. The [interface guide](../../../design/framework-next/distribution-implementation/README.md) documents commands, generated identities, support limits and the exact member list.

Source selection reads one full commit OID with replace refs disabled, rejects partial/promisor clones, preserves regular Git blob bytes and modes, and never reads root installation/config/history as build input. Payload, runtime and metadata are distinct. Output/scratch roots are explicit, may be RAM disk, and receive unique exclusively created directories. No old destination is reused; no cleanup/apply/delete/migration/recovery engine exists. Completion metadata is generated only during a real future invocation after emitted content read-back; this task generated no candidate, installation lock or execution receipt.

The initial default selection has eight Lesson members: `SKILL.md`, `skill-package.yaml`, `references/configuration.md`, `references/operations.md`, `references/example.md`, `schemas/lesson-record.schema.json`, `templates/lesson.md`, `scripts/lesson.py`. The coordinator supplied and adopted this final initial interface in the current conversation. `lesson.fs` uses `scripts/lesson.py`; no helper or metadata version change is needed. General selection derives members from metadata, not this fixed list. #330 exact source bytes remain an integration input outside this branch.

## Actual checks and limits

- Verified assigned clean start at `a1d8b750b8c81fd17697a39e04b55c35c4f3c4dc`, branch `codex/2026-09-23-candidate-assembly`, worktree `F:/framework-next/331`, persistent C: Git common database; fetched the live Issue read-only.
- Inspected all owned source and the eight manifest destinations against P1 and the coordinator interface. `python -B -` used only standard-library source/text inspection plus PyYAML reading: strict UTF-8 decode, `ast.parse`, `json.loads`, `yaml.safe_load`, and changed Markdown link resolution. No product module was imported, compiled to bytecode or executed. The 01:56 static pass read 15 files, parsed 8 Python / 3 YAML / 1 JSON, and resolved 7 local Markdown links; final workflow/handoff additions receive the same readability pass before commit.
- Git scope/status and `git diff --check` / staged diff are the content-delivery checks. The full planned message is written under this workflow's ignored `.tmp/` and checked with the existing `validate-git-commits.py --message-file ... --workflow-id 2026-09-23-candidate-assembly` exception before those exact bytes are committed. Final command results and exact HEAD/message are retained in the task conversation; no prospective product-validation pass is asserted here.
- An initial `apply_patch` could not create the absent F: source parent directories. No source files were created by that failed call. Explicitly scoped directory creation using normal sandbox escalation succeeded, then the edits continued in the same assigned worktree. This was a filesystem preparation failure, not a product trial.

All behavioral execution, builder help/trials, builds, tests, schema/semantic verification trials, legacy validators other than message format, independent audit machinery, hosted checks and CI remain **`deferred-by-owner`**, authority U001, owner program #322 coordinator / P7. Source parsing is syntax/readability evidence only. The baseline assessment is `partially-resolved` by this bounded implementation, with no invented resolved finding IDs.

Windows preserves executable Git mode in the inventory; POSIX applies/reads filesystem permissions. Markdown checks cover standard inline/reference file links and schema reference file targets, not every HTML/dynamic-code/fragment semantic. Roots must be caller-controlled. No adversarial filesystem sandbox, cross-volume transaction or crash-durability guarantee is claimed. A failed/interrupted build is not admitted by a completion file's presence; P6 must re-read candidate identity/content and installation ownership before any application. These are explicit support limits for P7 selection, not passing evidence.

## Handoff and deferred owners

| Work | State | Owner and next action |
| --- | --- | --- |
| #331 local code/doc slice | Completed with verification deferred | Coordinator reads exact local HEAD and this owned diff. |
| #330 integration | Pending exact-byte reconciliation | Coordinator integrates its coherent local delivery and compares actual metadata to the eight manifest members before first push; do not run builder as reconciliation. |
| Product trials / focused checks / CI | deferred-by-owner | P7 selects redesigned cases and records actual outcomes. |
| Installation planning/apply/migration/recovery/cutover | Outside #331 | P6 owns implementation and P7 owns trials; existing root runtime stays active. |
| Push / PR / merge / Issue / Project / release | Not performed by executor | Coordinator owns authorized integration; publication/adoption remain separate. |

No unresolved field/member decision remains for this slice. Actual runtime execution has no evidence yet. No sub-agents or executor-created conversations were used. The bounded early callback delivered the metadata helper boundary; coordinator resolved it with one script plus a declared example reference.

Proposed shared workflow index row (coordinator-owned insertion only):

```text
| 2026-09-23-candidate-assembly | Exact Git selection and development candidate assembly (#331) | ai-context-governance | completed (local code; U001/P7 verification deferred) | .dev/workflows/2026-09-23-candidate-assembly/workflow-plan.md |
```

Read [the bounded handoff](../handoff.yaml). No shared index or coordinator record was edited.
