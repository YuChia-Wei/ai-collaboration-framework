# ai-context-auditor 使用說明

[回 Skill 目錄](README.md) · [安裝](../installation.md) · [知識選配](../knowledge-packages.md)

套件版本：`0.1.0`。操作名稱以實際安裝的 metadata 為準。

## 用途與操作

`audit` 對指定 AI 協作脈絡找出有證據的問題；`compare` 比較兩個明確 subject 或先前報告與現況。

## 輸入與輸出

提供檔案/根目錄範圍、權威規則、問題或比較問題與可讀證據；輸出具位置、觸發條件、影響、證據、不確定性的 findings，以及實際覆蓋與限制。

## 何時用／界線

只讀；不可修正、初始化或維護 context，也不替代產品程式審查。沒有發現只代表所選範圍，不能當全域健康證明。

## 範例請求

使用 `ai-context-auditor audit`，只檢查根目錄 AGENTS 與 `.dev/standards` 對權限和 precedence 是否矛盾；列出可驗證 finding，勿修改檔案。

## 知識

無套件綁定。

## 開始使用

先確認此 skill 已在專案的 runtime entries 中。向 agent 提供上面的操作、
實際範圍與輸入；範例 prompt 是自然語言請求，不是 shell 指令。
明確指定輸出位置及可寫範圍。使用 prefixed 安裝時，選單中的名稱可能是
`aicf-ai-context-auditor`；canonical package ID 仍為 `ai-context-auditor`。

此套件提供指令方法，不提供同名 CLI。Agent 依已安裝的 operation
reference 執行；若本次任務需要編輯或測試，使用專案已有且被授權的工具。

## 權威參考

- [Skill 入口](../../src/skills/ai-context-auditor/SKILL.md)
- [版本、操作、依賴與 runtime metadata](../../src/skills/ai-context-auditor/skill-package.yaml)
- [references/audit.md](../../src/skills/ai-context-auditor/references/audit.md)

上述連結方便在來源庫核對；實際使用時應讀取已安裝套件中的相同資源。
