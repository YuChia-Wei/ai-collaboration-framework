# 03 — Current State Findings (main@71c41db, 2026-07-20)

Each finding lists a reproduction command. main may have advanced; re-run
before acting. Findings are ordered by severity.

## F1 (CRITICAL) — Critical gate is red on main

`validate-workflow-artifacts.py` is a critical-tier check (runs in both
`--quick` and `--critical` modes of `check-all.sh`) and currently fails.

Reproduce:
```
python .ai/scripts/validate-workflow-artifacts.py
```
Observed failures:
- `2026-07-19-v0-4-2-release-publication/workflow.yaml`: `workflow_id` must
  match directory name (recorded as `2026-07-18-...`).
- same file: `artifact_root` does not exist (points at `2026-07-18-...`).
- `.dev/workflows/INDEX.MD`: row `updated_at` differs from the workflow file.

Implication: any finalize commits that reached main were pushed without a
green critical gate, or the gate was ignored. This is both a concrete defect
to fix and evidence for RC-3.

## F2 (CRITICAL) — v0.4.2 release.yaml stuck at `validated`

Reproduce:
```
grep -E '^status|^commit|^tag|^created_at' releases/v0.4.2/release.yaml
grep '^status' releases/v0.4.1/release.yaml   # compare: published
```
Observed: `status: validated`, no `tag`/`commit` fields, `created_at` copied
from v0.4.1. v0.4.1 by contrast is `published` with the commit recorded.

Implication: `discover_candidate()` in `render-ai-context-release-notes.py`
requires exactly one governed `planned|validated` release. With v0.4.2 left
as `validated`, the next release (v0.5.0) will discover two candidates and
fail. Fail-closed works, but v0.5.0 is effectively blocked until v0.4.2 is
finalized — and the roadmap does not record this as the reason.

## F3 (HIGH) — release-notes.md polluted and duplicated

Reproduce:
```
grep -c 'ai-context-release-automation' releases/v0.4.2/release-notes.md
grep -c 'Release provenance' releases/v0.4.2/release-notes.md
grep '1c13d7966b937004f12be6dd70d58c8ecb5afbe7' releases/v0.4.2/release-notes.md
```
Observed: two automation markers, two provenance sections. The file contains
render *output*, not authored content; v0.4.1-style Status/Highlights/
Compatibility sections were never written.

Escalation (public-facing): one provenance block records
`Commit: 1c13d7966b937004f12be6dd70d58c8ecb5afbe7`, which
`git cat-file -t 1c13d7966b937004f12be6dd70d58c8ecb5afbe7` reports as **not a
real object** — a garbled SHA. This same block is visible on the published
GitHub Release page (owner-supplied, 2026-07-20), so the public release
provenance points at a non-existent commit. The real tagged commit is
`f474c3b058cb9f89f93929e0732fc1f276422dd9`.

Fix direction: rewrite as an authored source (mirror v0.4.1 structure);
never store render output here. Regenerating the GitHub Release body from the
corrected source is also needed to clear the public invalid provenance.

## F4 (HIGH) — migration-guide.md is empty

Reproduce:
```
wc -c releases/v0.4.2/migration-guide.md   # 0
wc -l releases/v0.4.1/migration-guide.md    # 84
```
Implication: the published GitHub Release body's Migration guide section was
empty. Author real content (even if it is "no migration required; v0.3.0 is
the only automatic source; v0.4.0 targets wait for PKG-003").

## F5 (HIGH) — fabricated / copied evidence in workflow artifacts

Reproduce:
```
grep 29650583394 .dev/workflows/2026-07-19-v0-4-2-release-publication/tasks/REL042-002.json \
                 releases/v0.4.1/release.yaml
git show 71c41db --stat   # body claims release.yaml updated; only notes changed
```
Observed: REL042-002 records v0.4.1's run ID as v0.4.2 evidence; `71c41db`'s
message misstates its own diff.

Ground truth (confirmed from hosted runs, owner-supplied 2026-07-20):
- Failed run: **#4 `29678934006`** — failure at "Validate tag and build
  release", tag at commit `1c13d799a8cd0c897304e6f21c14a1874ea76b81`,
  2026-07-19 07:55 UTC.
- Published run: **#5 `29679273269`** — success, tag at commit
  `f474c3b058cb9f89f93929e0732fc1f276422dd9`, 2026-07-19 08:07 UTC.
These are the correct values for the R042-005 hotfix; the in-repo
`29650583394` must be replaced with `29679273269` and the published commit
recorded as `f474c3b`.

## F6 (MEDIUM) — ROADMAP and backlog not reconciled to published state

Reproduce:
```
grep -E 'current_target|v0.4.2. \| .(ready_for_publication|published)' .dev/backlog/ROADMAP.md
grep published_in .dev/backlog/items/R042-00*.yaml
```
Observed: ROADMAP still shows v0.4.2 `ready_for_publication` and "Next
Action: Execute V042-001"; `R042-001..004` have `published_in: null` (index
shows `—`). REL042-003 claims registry/backlog finalization completed; it did
not.

## F7 (LOW) — publication workflow.yaml self-inconsistent metadata

Reproduce:
```
grep -E 'workflow_id|artifact_root|branch|backlog_refs' \
  .dev/workflows/2026-07-19-v0-4-2-release-publication/workflow.yaml
```
Observed: `2026-07-18` ids and `PKG-00x` backlog_refs in a `2026-07-19`
R042 workflow. Root cause of F1; fixing F1 requires fixing this.

## Validators that currently PASS (do not regress)

```
python .ai/scripts/validate-ai-context.py              # passes
python -m pytest .ai/scripts/tests/test_backlog_release_contract.py   # 6 passed
```
Note: local runs require `pyyaml` (and `pytest`); the interpreter default
lacks them. This is expected — `R042-004` addressed script portability, not
host provisioning.
