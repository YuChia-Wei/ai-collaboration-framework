# pr-author 使用說明

[回 Skill 目錄](README.md) · [安裝](../installation.md) · [知識選配](../knowledge-packages.md)

套件版本：`0.1.0`。操作名稱以實際安裝的 metadata 為準。

## 用途與操作

對真實 Git 比較準備 PR 內容/record，或在明確授權下操作一個 GitHub PR。操作：`explain`、`prepare`、`inspect`、`query`、`revise`、`render`、`provider-read`、`provider-create`、`provider-update`。

## 輸入與輸出

本機 operation 用嚴格 JSON、明確 root 及 Git subject；provider operation 另需 `gh`、既有授權認證、digest/subject rebind、精確 grant。輸出 record/view 或 provider projection、URL、觀察 token 與 mutation state。

## 何時用／界線

可建立/更新 draft PR；不推 branch、不 merge/close PR、不改 Issue/Project、release 或 credential。prepare 不等於已發佈。

## 範例請求

使用 `pr-author prepare`，以 base/head full SHA 建立此 diff 的 PR record，列出實際驗證狀態；不要推送或建立遠端 PR。

## 知識

無套件綁定。

## 開始使用

先確認此 skill 已在專案的 runtime entries 中。向 agent 提供上面的操作、
實際範圍與輸入；範例 prompt 是自然語言請求，不是 shell 指令。
明確指定輸出位置及可寫範圍。使用 prefixed 安裝時，選單中的名稱可能是
`aicf-pr-author`；canonical package ID 仍為 `pr-author`。

此套件含可執行工具。先依[工具型 skills 共通設定](../tool-skills.md)
確認 Python 依賴、絕對 roots、設定及寫入限制，再執行 `explain`。
建立／變更 record 要按 operation reference 提供欄位；更新必須使用
實際讀回的 digest，不能自行填一個 hash。

## 權威參考

- [Skill 入口](../../src/skills/pr-author/SKILL.md)
- [版本、操作、依賴與 runtime metadata](../../src/skills/pr-author/skill-package.yaml)
- [references/configuration.md](../../src/skills/pr-author/references/configuration.md)
- [references/operations.md](../../src/skills/pr-author/references/operations.md)
- [references/github.md](../../src/skills/pr-author/references/github.md)
- [references/example.md](../../src/skills/pr-author/references/example.md)
- [pr.record schema](../../src/skills/pr-author/schemas/pr-record.schema.json)

上述連結方便在來源庫核對；實際使用時應讀取已安裝套件中的相同資源。
