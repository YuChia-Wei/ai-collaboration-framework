# adr-author 使用說明

[回 Skill 目錄](README.md) · [安裝](../installation.md) · [知識選配](../knowledge-packages.md)

套件版本：`0.1.0`。操作名稱以實際安裝的 metadata 為準。

## 用途與操作

保存架構替代方案、取捨與有證據的 owner 決策。操作：`explain`、`create`、`inspect`、`query`、`validate`、`revise`、`render`、`derive`、`decide`、`retire`、`supersede`。

## 輸入與輸出

指定 `project_root`、`package_root`、設定；建立時提供完整內容、文字、決策與新身分選擇。回傳 record reference、實際 SHA-256、變更狀態、查詢或診斷；`render` 只產生結果 Markdown。

## 何時用／界線

要留存可追溯架構決策才用；不是設計評估、Lesson、實作、測試或規則採用的替代品。決策被接受不代表架構已實作。

## 範例請求

使用 `adr-author`，先查詢既有 ADR，為『訊息去重策略』建立兩個以上替代方案；保存 owner 已接受的選項與證據，勿修改任何產品程式。

## 知識

無套件綁定。

## 開始使用

先確認此 skill 已在專案的 runtime entries 中。向 agent 提供上面的操作、
實際範圍與輸入；範例 prompt 是自然語言請求，不是 shell 指令。
明確指定輸出位置及可寫範圍。使用 prefixed 安裝時，選單中的名稱可能是
`aicf-adr-author`；canonical package ID 仍為 `adr-author`。

此套件含可執行工具。先依[工具型 skills 共通設定](../tool-skills.md)
確認 Python 依賴、絕對 roots、設定及寫入限制，再執行 `explain`。
建立／變更 record 要按 operation reference 提供欄位；更新必須使用
實際讀回的 digest，不能自行填一個 hash。

## 權威參考

- [Skill 入口](../../src/skills/adr-author/SKILL.md)
- [版本、操作、依賴與 runtime metadata](../../src/skills/adr-author/skill-package.yaml)
- [references/configuration.md](../../src/skills/adr-author/references/configuration.md)
- [references/operations.md](../../src/skills/adr-author/references/operations.md)
- [references/example.md](../../src/skills/adr-author/references/example.md)
- [references/WHEN-TO-CREATE-ADR.MD](../../src/skills/adr-author/references/WHEN-TO-CREATE-ADR.MD)
- [adr.record schema](../../src/skills/adr-author/schemas/adr-record.schema.json)

上述連結方便在來源庫核對；實際使用時應讀取已安裝套件中的相同資源。
