# local-backlog 使用說明

[回 Skill 目錄](README.md) · [安裝](../installation.md) · [知識選配](../knowledge-packages.md)

套件版本：`0.1.0`。操作名稱以實際安裝的 metadata 為準。

## 用途與操作

為選定本機檔案型 backlog 建立並維護 project-owned work item。操作：`explain`、`create`、`inspect`、`query`、`revise`、`transition`、`render`。

## 輸入與輸出

以嚴格 JSON 請求指定根目錄/設定和操作欄位；輸出實際 outcome、mutation state、reference、digest 與診斷。

## 何時用／界線

狀態需要可追溯、衝突檢查的本機 work collection 才用；不讀寫 GitHub、不與 tracker 同步、不替代 workflow/ADR/Lesson。

## 範例請求

使用 `local-backlog`，先查詢再於指定 store 建立 draft work item；讀回後以 `transition` 轉為 planned，保留 Issue 連結為 reference-only；先讀取有效設定。

## 知識

無套件綁定。

## 開始使用

先確認此 skill 已在專案的 runtime entries 中。向 agent 提供上面的操作、
實際範圍與輸入；範例 prompt 是自然語言請求，不是 shell 指令。
明確指定輸出位置及可寫範圍。使用 prefixed 安裝時，選單中的名稱可能是
`aicf-local-backlog`；canonical package ID 仍為 `local-backlog`。

此套件含可執行工具。先依[工具型 skills 共通設定](../tool-skills.md)
確認 Python 依賴、絕對 roots、設定及寫入限制，再執行 `explain`。
建立／變更 record 要按 operation reference 提供欄位；更新必須使用
實際讀回的 digest，不能自行填一個 hash。

## 權威參考

- [Skill 入口](../../src/skills/local-backlog/SKILL.md)
- [版本、操作、依賴與 runtime metadata](../../src/skills/local-backlog/skill-package.yaml)
- [references/configuration.md](../../src/skills/local-backlog/references/configuration.md)
- [references/operations.md](../../src/skills/local-backlog/references/operations.md)
- [references/example.md](../../src/skills/local-backlog/references/example.md)
- [local-backlog.record schema](../../src/skills/local-backlog/schemas/local-backlog-record.schema.json)

上述連結方便在來源庫核對；實際使用時應讀取已安裝套件中的相同資源。
