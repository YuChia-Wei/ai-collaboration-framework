# diagnostic-analyst 使用說明

[回 Skill 目錄](README.md) · [安裝](../installation.md) · [知識選配](../knowledge-packages.md)

套件版本：`0.1.0`。操作名稱以實際安裝的 metadata 為準。

## 用途與操作

`diagnose` 對觀察到的預期/實際落差進行可否證假設、有限重現與因果隔離。

## 輸入與輸出

提供症狀、期望、subject、環境、權威、證據與限制、被授權的實驗範圍/指令；輸出假設、falsifier、重現/隔離結果、確認/未確認/阻塞結論與修復 proposal。

## 何時用／界線

需要解釋症狀才用；固定 artifact 的 defect review 是 code review，已決定且授權的修復交給實作 route。診斷不授予修復權限。

## 範例請求

使用 `diagnostic-analyst diagnose`，分析生產匯入偶發重複事件的原因；只執行已授權的讀取與重現指令，提出可否證假設和最小修復建議。

## 知識

無套件綁定。

## 開始使用

先確認此 skill 已在專案的 runtime entries 中。向 agent 提供上面的操作、
實際範圍與輸入；範例 prompt 是自然語言請求，不是 shell 指令。
明確指定輸出位置及可寫範圍。使用 prefixed 安裝時，選單中的名稱可能是
`aicf-diagnostic-analyst`；canonical package ID 仍為 `diagnostic-analyst`。

此套件提供指令方法，不提供同名 CLI。Agent 依已安裝的 operation
reference 執行；若本次任務需要編輯或測試，使用專案已有且被授權的工具。

## 權威參考

- [Skill 入口](../../src/skills/diagnostic-analyst/SKILL.md)
- [版本、操作、依賴與 runtime metadata](../../src/skills/diagnostic-analyst/skill-package.yaml)
- [references/diagnose.md](../../src/skills/diagnostic-analyst/references/diagnose.md)

上述連結方便在來源庫核對；實際使用時應讀取已安裝套件中的相同資源。
