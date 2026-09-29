# 05 — Process Improvement Plan

Ordered by dependency. Phase 0 unblocks everything; Phases 1–3 are the
v0.5.0 hardening set.

## Phase 0 — Hotfix (R042-005, before any v0.5.0 work)

Goal: return main to a green, self-consistent, published state.

1. Fix the publication `workflow.yaml` (F1/F7): correct `workflow_id`,
   `artifact_root`, `branch`, `backlog_refs`; sync `.dev/workflows/INDEX.MD`
   row. Verify `validate-workflow-artifacts.py` passes.
2. Flip `releases/v0.4.2/release.yaml` to `status: published` with the
   confirmed values: commit `f474c3b058cb9f89f93929e0732fc1f276422dd9`, run
   `29679273269`. Remove the copied v0.4.1 run ID `29650583394` (F2, F5).
3. Rewrite `release-notes.md` as an authored source mirroring v0.4.1's
   structure; strip all automation markers and render provenance, including
   the invalid SHA `1c13d7966b93...` (F3). Author `migration-guide.md` (F4).
   Regenerate the public GitHub Release body from the corrected source so the
   invalid provenance commit is cleared from the release page.
4. Reconcile ROADMAP (v0.4.2 published, corrected Next Action) and backlog
   `published_in` for R042-001..005 (F6).
5. Run `check-all.sh --full`; all green before merge. Do NOT move the tag.

Exit criteria = R042-005 acceptance in `04`.

## Phase 1 — Runbook (RC-1)

Write `.ai/assets/skills/ai-context-governance/references/RELEASE-PUBLICATION-RUNBOOK.md`:

- One numbered step per action, each with: the exact command, the expected
  output, and the fail action.
- Explicit ordering: author registry (validated, tag/commit unset) → merge to
  main → `check-all --critical` green → `prepare-release-tag` → verify hosted
  run → finalize registry to published → reconcile roadmap/backlog.
- Explicit prohibition: "Do not copy the previous release's workflow/task/
  registry files. Instantiate from templates."
- Add a routing pointer from `AGENTS.md` "Git Commit Policy" / release
  context so a cold-start agent finds it.

## Phase 2 — Templates + stale-value rejection (RC-2)

- Convert release/workflow/task artifacts to placeholder templates
  (`<WORKFLOW_ID>`, `<CREATED_AT>`, `<RUN_ID>`, ...).
- Extend a validator (new or in `validate-workflow-artifacts.py`) to reject:
  - `created_at` earlier than the workflow directory's date;
  - a release `evidence` run ID equal to any prior release's;
  - `backlog_refs` not matching the workflow's actual scope;
  - any placeholder token left unfilled.
- Add GWT fixtures (fits the repo's fail-closed testing style).

## Phase 3 — Mechanical gates (RC-3, RC-4)

1. `prepare-release-tag` script — the only sanctioned tag creator. Preconditions
   (all must pass before it creates the annotated tag):
   - `releases/<v>/release.yaml` present, `status: validated`,
     `tag`/`commit` unset;
   - `release-notes.md` and `migration-guide.md` non-empty and free of
     automation markers;
   - `check-all.sh --critical` green on HEAD.
2. Terminal-state validator (pure local git), added to `check-all`:
   - if tag `vX` exists ⇒ `release.yaml` `status: published` and
     `commit == vX^{}`;
   - `release-notes.md` contains no render output / duplicate provenance.
3. Governance validation route in pull-request CI (ENF-001 alignment) so a
   red critical gate cannot reach main unnoticed.
4. Handoff gate (HANDOFF-001): receiving agent runs `check-all --critical`
   and records the result in the resume checkpoint before continuing;
   Validation sections require a runnable command + output.

## Design principle to encode

State in the root collaboration guide: **specify for the weakest credible
executor.** Acceptance criterion for the whole release surface — any capable
agent, cold-starting from repo files alone, can execute a correct release.
Prior stability under one model is context continuity, not proof of
specification quality.

## Sequencing summary

```
Phase 0 (R042-005)  ──►  unblocks v0.5.0 candidate discovery
        │
        ▼
Phase 1 (runbook) ─► Phase 2 (templates+validator) ─► Phase 3 (gates+CI+handoff)
        │                                                     │
        └───────────────► REL-001 / HANDOFF-001 / ENF-001 ◄──┘  (v0.5.0 blockers)
```
Note: the diagram is only a dependency sketch; the prose above is
authoritative.
