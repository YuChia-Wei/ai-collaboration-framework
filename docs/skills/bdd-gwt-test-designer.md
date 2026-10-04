# bdd-gwt-test-designer 使用說明

[回 Skill 目錄](README.md) · [安裝](../installation.md) · [知識選配](../knowledge-packages.md)

套件版本：`0.2.0`。操作名稱以實際安裝的 metadata 為準。

## 用途與操作

`design` 設計或明確修訂 Given-When-Then 情境、矩陣或 `.feature`；`review` 只讀審查固定情境 artifact。

## 輸入與輸出

提供需求/規格/驗收或標記的觀察行為、範圍、慣例與格式；輸出可追溯情境、具體資料、可觀察斷言、測試層級、設定與缺口/交接。

## 何時用／界線

正式測試規格仍是 `spec-author`；本 skill 不實作或執行測試，也不因產生 `.feature` 而選擇 runner。

## 範例請求

使用 `bdd-gwt-test-designer design`，根據『取消訂單』驗收條件寫 GWT 情境矩陣，逐條標註可觀察斷言與適當測試層級，不要寫測試程式。

## 知識

可選兩個 binding：`engineering-common@0.1.0`（`design`,`review`，2 項資源）與 `dotnet-backend@0.1.0`（同操作，2 項資源）。缺失只會使這些專門準則不可用，通用情境設計仍可完成。

## 開始使用

先確認此 skill 已在專案的 runtime entries 中。向 agent 提供上面的操作、
實際範圍與輸入；範例 prompt 是自然語言請求，不是 shell 指令。
明確指定輸出位置及可寫範圍。使用 prefixed 安裝時，選單中的名稱可能是
`aicf-bdd-gwt-test-designer`；canonical package ID 仍為 `bdd-gwt-test-designer`。

此套件提供指令方法，不提供同名 CLI。Agent 依已安裝的 operation
reference 執行；若本次任務需要編輯或測試，使用專案已有且被授權的工具。

## 宣告的知識資源

以下全部為 optional；未選、缺少或無法驗證時，不可宣稱具備對應專業覆蓋。

### common-test-design

`engineering-common@0.1.0`；操作：`design`、`review`。

- `engineering-rule-catalog`
- `member:references/GWT-TEST-HANDOFF-CONTRACT.md`

### dotnet-test-design

`dotnet-backend@0.1.0`；操作：`design`、`review`。

- `engineering-rule-catalog`
- `member:standards/coding-standards/test-standards.md`

## 權威參考

- [Skill 入口](../../src/skills/bdd-gwt-test-designer/SKILL.md)
- [版本、操作、依賴與 runtime metadata](../../src/skills/bdd-gwt-test-designer/skill-package.yaml)
- [references/design.md](../../src/skills/bdd-gwt-test-designer/references/design.md)
- [references/review.md](../../src/skills/bdd-gwt-test-designer/references/review.md)

上述連結方便在來源庫核對；實際使用時應讀取已安裝套件中的相同資源。
