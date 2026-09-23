# Work management design and implementation

- Workflow: 2026-09-23-work-management; owner: ai-context-governance.
- Branch/worktree: codex/2026-09-23-work-management, F:/framework-next/335.
- Original design base: a34ecd3c9423b17b6bb745f598ef22fd7437dd24.
- Preserved design checkpoint: 446a579d03a25edf1b6e64b5e5c13016740025c0.
- Preserved source checkpoint: 5e632ed50242f13b44bec1884de24c496f5a93ea.
- Source continuation base: 0d0556d4c60105a28eb39cfb06efab9b069728cb, adopted with git merge --ff-only after clean identity read-back.
- State: **completed for bounded local source delivery**. [Issue #335](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/335) remains OPEN in the last live read; provider integration/closure is coordinator-owned.
- Created: 2026-09-23T08:18:00+08:00; updated: 2026-09-23T00:51:28+00:00.
- Template: .ai/assets/skills/ai-context-governance/templates/ai-context-maintenance-workflow-plan-template.md, version 1.2.0, adapted under U001.

## Ownership and completion

The coordinator explicitly resumed this same task and granted src/skills/pr/**, src/skills/local-backlog/** plus own design/workflow. No other source/config/manifest/profile/runtime/history files were edited. No sub-agent or executor-created task/worktree was used. Shared contract decisions supersede the first proposal; their original checkpoint remains unchanged in Git history.

| Task | State | Delivery |
| --- | --- | --- |
| [WM-001](tasks/WM-001.json) | completed | Preserved early contract checkpoint and bounded authority/operations/schema proposals. |
| [WM-002](tasks/WM-002.json) | completed | Complete independent PR/backlog source sets and one package-owned public GitHub adapter. |
| [CR335-001](tasks/CR335-001.json) | completed for local source scope | Inspect repository and worktree Git configuration before the pinned comparison; runtime verification remains deferred-by-owner. |

This workflow retains a real cross-session design/ownership handoff and source continuation, not empty audit tasks. Completion closes its local code/document scope only. Runtime acceptance, distribution mapping, online integration, Issue/Project closure and P7 verification remain separate.

## Selected interfaces

[Integration inventory](../../design/framework-next/work-management/integration-proposal.json) records exact 10 PR / 8 backlog members. Both use metadata_version 2, config_version 2, one writable/readable schema and no skill dependencies. WM-C1/C2/C3 are selected by the coordinator: selected-namespace config isolation, public package-owned pr.github, and coordinated single-writer provider operations without server CAS. Mode/grant strings are not proof of permission/exclusion.

## Evidence and remaining work

[Original contract report](reports/contract-checkpoint.md) remains historical. [Source report](reports/source-checkpoint.md) records actual static checks, limits and deferrals. [Receiving checkpoint](handoff.yaml) identifies the current containing commit without a self-referential SHA.

All behavioral/schema/provider/package/build/install/migration/CI/audit execution remains deferred-by-owner under U001 to program #322 coordinator / P7. Next: coordinator inspects CR335-001 against the preserved source checkpoint, reads the new local commit, supplies the concrete integrated package subject to #337 for exact manifest/profile mapping, arranges first push/integration, then P7 chooses and runs verification. No provider write, first push, runtime activation, release or credential change was performed by this executor.

## P7 actual worktree repair continuation (2026-09-24)

Live Issue 335 reopens this local outcome for the installed target's actual blocked/git-read failure. Current assigned branch is codex/2026-09-24-pr-worktree-repair at clean base ff57a09b8443402caf3508dcee1fe0378753970f in the rebuilt F:/framework-next/335. Earlier delivery and CR335-001 remain historical evidence. Current local state is in_progress, task [CR335-002](tasks/CR335-002.json); coordinator is 01a0ce78-db26-74e1-a615-2bd0599f7d0c.

The [repair report](reports/pr-worktree-repair.md) records the source correction, selected real Git fixture and actual outcomes. Commit the source/test first, then run only tests/framework_next/test_pr_git_worktree.py under the Issue-selected limits. Other U001 deferrals and coordinator-owned first push, candidate rebuild, target update and provider integration remain in force.
