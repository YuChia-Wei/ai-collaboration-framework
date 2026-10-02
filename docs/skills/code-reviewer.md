# code-reviewer 使用說明

[回 Skill 目錄](README.md) · [安裝](../installation.md) · [知識選配](../knowledge-packages.md)

套件版本：`0.2.0`。操作名稱以實際安裝的 metadata 為準。

## 用途與操作

`review` 對指定程式、diff 或具體實作指引產生可行動缺陷 findings。

## 輸入與輸出

提供 subject、範圍、預期行為、目標規則和可讀證據；輸出位置、觸發條件、影響、證據、不確定性，以及覆蓋/未執行檢查。

## 何時用／界線

只讀且不修復；觀察到的症狀需要因果調查時用診斷；架構或情境 artifact 審查仍走其專用 route。它不自行提供 .NET 專門檢查。

## 範例請求

使用 `code-reviewer review`，審查此 commit 的付款重試路徑，依提供的冪等契約找可重現 defect；不要改碼，不要把靜態閱讀稱為執行驗證。

## 知識

可選 `engineering-common@0.1.0`（1 項）與 `dotnet-backend@0.1.0`（6 項）審查 binding；未裝時不可宣稱有那些專門覆蓋。

## 開始使用

先確認此 skill 已在專案的 runtime entries 中。向 agent 提供上面的操作、
實際範圍與輸入；範例 prompt 是自然語言請求，不是 shell 指令。
明確指定輸出位置及可寫範圍。使用 prefixed 安裝時，選單中的名稱可能是
`aicf-code-reviewer`；canonical package ID 仍為 `code-reviewer`。

此套件提供指令方法，不提供同名 CLI。Agent 依已安裝的 operation
reference 執行；若本次任務需要編輯或測試，使用專案已有且被授權的工具。

## 宣告的知識資源

以下全部為 optional；未選、缺少或無法驗證時，不可宣稱具備對應專業覆蓋。

### common-review

`engineering-common@0.1.0`；操作：`review`。

- `engineering-rule-catalog`

### dotnet-review

`dotnet-backend@0.1.0`；操作：`review`。

- `engineering-rule-catalog`
- `member:standards/DESIGN-BY-CONTRACT.md`
- `member:standards/coding-standards/aggregate-standards.md`
- `member:standards/coding-standards/repository-standards.md`
- `member:standards/coding-standards/test-standards.md`
- `member:standards/coding-standards/usecase-standards.md`

## 權威參考

- [Skill 入口](../../src/skills/code-reviewer/SKILL.md)
- [版本、操作、依賴與 runtime metadata](../../src/skills/code-reviewer/skill-package.yaml)
- [references/review.md](../../src/skills/code-reviewer/references/review.md)

上述連結方便在來源庫核對；實際使用時應讀取已安裝套件中的相同資源。
