# local-change-implementer 使用說明

[回 Skill 目錄](README.md) · [安裝](../installation.md) · [知識選配](../knowledge-packages.md)

套件版本：`0.2.0`。操作名稱以實際安裝的 metadata 為準。

## 用途與操作

`implement` 一個 class/object/method/local symbol/query 上的單一技術操作，以及直接呼叫點或即時測試。

## 輸入與輸出

提供一個主要技術目標、行為、授權、規則、允許相依半徑、技術、可寫檔案及驗證命令；輸出有界程式變更、實際 touched radius、相容性、檢查結果與手交決策。

## 何時用／界線

公開合約或協調行為變更應選 slice；檔案數不是判斷標準。需要授權 target editor，沒有它不可實作。

## 範例請求

使用 `local-change-implementer implement`，只修正 `ParseDate` 對 ISO offset 的處理及其直接單元測試；不變更公開合約或其他解析器，執行我指定的測試。

## 知識

可選 `engineering-common@0.1.0`（1 項）與 `dotnet-backend@0.1.0`（5 項）實作 binding；未裝時通用局部修復可做，不能宣稱特定 .NET 標準已覆蓋。

## 開始使用

先確認此 skill 已在專案的 runtime entries 中。向 agent 提供上面的操作、
實際範圍與輸入；範例 prompt 是自然語言請求，不是 shell 指令。
明確指定輸出位置及可寫範圍。使用 prefixed 安裝時，選單中的名稱可能是
`aicf-local-change-implementer`；canonical package ID 仍為 `local-change-implementer`。

此套件提供指令方法，不提供同名 CLI。Agent 依已安裝的 operation
reference 執行；若本次任務需要編輯或測試，使用專案已有且被授權的工具。

## 宣告的知識資源

以下全部為 optional；未選、缺少或無法驗證時，不可宣稱具備對應專業覆蓋。

### common-local-change

`engineering-common@0.1.0`；操作：`implement`。

- `engineering-rule-catalog`

### dotnet-local-change

`dotnet-backend@0.1.0`；操作：`implement`。

- `engineering-rule-catalog`
- `member:standards/coding-standards/aggregate-standards.md`
- `member:standards/coding-standards/repository-standards.md`
- `member:standards/coding-standards/test-standards.md`
- `member:standards/coding-standards/usecase-standards.md`

## 權威參考

- [Skill 入口](../../src/skills/local-change-implementer/SKILL.md)
- [版本、操作、依賴與 runtime metadata](../../src/skills/local-change-implementer/skill-package.yaml)
- [references/implement.md](../../src/skills/local-change-implementer/references/implement.md)

上述連結方便在來源庫核對；實際使用時應讀取已安裝套件中的相同資源。
