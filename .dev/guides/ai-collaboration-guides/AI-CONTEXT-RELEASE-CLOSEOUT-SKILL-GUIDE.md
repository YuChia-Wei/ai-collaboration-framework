# AI Context Release Closeout Skill Guide

本指南說明 source repository 專用的 `ai-context-release-closeout` exception capability。其 canonical 規則以 `.ai/assets/skills/ai-context-release-closeout/skill.yaml` 為準；它不會進入任何 downstream package，也不是正常發布或 `ai-context-governance` 的 runtime dependency。

## 適用時機

只在 immutable annotated tag 已存在、GitHub Release 已發布，而且需要驗證歷史 record，或 tag automation 因明確例外無法完成時使用。從 `v0.12.0` 起，正常發布由 tag workflow 自動完成 hosted finalization、Issue／Project read-back 與 reconciliation；不應再呼叫本 skill 建立 source closeout PR。

## 執行邊界

- 預設只執行 post-tag verification、hosted Release／asset／checksum／archive parity 與 provider reconciliation read-back。
- 不建立 candidate，不選擇、建立、移動、重建或刪除 tag。
- 不執行 full Packaging GWT migration matrix 或 .NET product tests。
- retryable credential、Issue 或 Project 問題應重跑 hosted reconciliation，不得轉成 source patch。
- repository write 前檢查 sanctioned Python 與 offline uv discovery；環境不成立時回報 `blocked-by-environment`。
- 只有 historical compatibility 或明確核准的 source exception 才可產生 patch。Windows 必須先驗證短 temporary root，避免 nested worktree 長路徑；primary worktree 保持不變，直到 patch 已驗證並交由獨立 records-only PR。
- 不自動改寫 shared 或 published history；provider mutation 失敗時先 read-back 再決定下一步。

## Commands

驗證已完成 records 的 closeout：

```text
python .ai/scripts/ai_context_release_closeout.py verify --version <vX.Y.Z> --repository <owner/repo> --workflow-run-id <run-id>
```

僅在明確核准的 historical／source exception 中，從 validated registry 產生 records-only patch：

```text
python .ai/scripts/ai_context_release_closeout.py plan-patch --version <vX.Y.Z> --repository <owner/repo> --workflow-run-id <run-id> --output <path-outside-primary-worktree>
```

第二個命令不是正常發布步驟。它只在 hosted publication read-back 成功、且 exception justification 已記錄後進行，並在短路徑 isolated copy 內更新 registry copy、執行 finalization gate 與 `git diff --check`。它不會 commit、push 或建立 PR；已驗證 patch 必須經 records-only branch／PR handoff。
