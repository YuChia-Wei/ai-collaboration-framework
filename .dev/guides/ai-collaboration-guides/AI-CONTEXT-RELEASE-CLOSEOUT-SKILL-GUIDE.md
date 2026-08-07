# AI Context Release Closeout Skill Guide

本指南說明 source repository 專用的 `ai-context-release-closeout` capability。其 canonical 規則以 `.ai/assets/skills/ai-context-release-closeout/skill.yaml` 為準；它不會進入任何 downstream package，也不是 `ai-context-governance` 的 runtime dependency。

## 適用時機

只在 immutable annotated tag 已存在、GitHub Release 已發布、且需要完成 release registry、Issue／Project read-back 與 records-only Git handoff 時使用。

## 執行邊界

- 只執行 post-tag verification、hosted Release／asset／checksum／archive parity read-back 與 records-only validation。
- 不建立 candidate，不選擇、建立、移動、重建或刪除 tag。
- 不執行 full Packaging GWT migration matrix 或 .NET product tests。
- repository write 前檢查 sanctioned Python 與 offline uv discovery；環境不成立時回報 `blocked-by-environment`。
- patch 只可在 temporary isolated worktree 產生；primary worktree 保持不變，直到 patch 已驗證並交由獨立 records-only PR。
- 不自動改寫 shared 或 published history；provider mutation 失敗時先 read-back 再決定下一步。

## Commands

驗證已完成 records 的 closeout：

```text
python .ai/scripts/ai_context_release_closeout.py verify --version <vX.Y.Z> --repository <owner/repo> --workflow-run-id <run-id>
```

從 validated registry 產生 records-only patch：

```text
python .ai/scripts/ai_context_release_closeout.py plan-patch --version <vX.Y.Z> --repository <owner/repo> --workflow-run-id <run-id> --output <path-outside-primary-worktree>
```

第二個命令只在 hosted publication read-back 成功後進行，並在 temporary worktree 內更新 registry copy、執行 finalization gate 與 `git diff --check`。它不會 commit、push 或建立 PR；已驗證 patch 必須經 records-only branch／PR handoff。
