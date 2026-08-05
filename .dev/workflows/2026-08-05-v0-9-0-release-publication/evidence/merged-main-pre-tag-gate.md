# v0.9.0 Merged-Main Pre-Tag Gate

- `status`: `passed`
- `executed_at`: `2026-08-06T00:43:00+08:00`
- `branch`: `main`
- `commit`: `c14a3260cba7d0a9e2b67b73df9e221280d2d2ef`
- `pull_request`: `https://github.com/YuChia-Wei/ai-collaboration-prompts-dotnet-backend/pull/130`
- `merge_topology`: `merge-commit`
- `runtime`: Windows host Python with Git for Windows Bash; WSL was not used
- `duration_seconds`: `910.2`

## Command

```powershell
python .ai/scripts/prepare-ai-context-release.py --version v0.9.0 --commit c14a3260cba7d0a9e2b67b73df9e221280d2d2ef --branch main --ai-model "Codex / gpt-5.6-sol / reasoning xhigh (active release supervisor)"
```

## Result

The sanctioned read-only pre-tag command passed on merged `main` and printed
the following owner-only command. The command was not executed by Codex:

```powershell
git tag -a v0.9.0 c14a3260cba7d0a9e2b67b73df9e221280d2d2ef -m "REL-v0.9.0 - Governed AI Context Release" -m "Compatibility: pre-1.0 breaking release; automatic sources v0.8.0." -m "AI-Model: Codex / gpt-5.6-sol / reasoning xhigh (active release supervisor)"
```

This gate ran the repository critical matrix once. It did not rerun the clean
install or exact-v0.8.0 upgrade fixtures covered by the explicit owner
equivalence waiver, and it did not create, move, or push a tag.

## CTX-004 Provider Read-Back

After merged-main verification, GitHub Issue #98 was synchronized and closed
as completed. Project #3 read back the following independent lifecycle fields:

- `Status`: `Done`
- `Target release`: `v0.9.0`
- `Owner review`: `Approved`
- `Priority`: `P3 Low`
- `Published in`: `Not yet published`

The publication field intentionally remains pending until the hosted v0.9.0
release is verified. No local backlog or provider mapping was created for
online-only Issue #128.
