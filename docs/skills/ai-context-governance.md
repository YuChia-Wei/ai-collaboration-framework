# ai-context-governance 使用說明

[回 Skill 目錄](README.md) · [安裝](../installation.md) · [知識選配](../knowledge-packages.md)

套件版本：`0.1.0`。操作名稱以實際安裝的 metadata 為準。

## 用途與操作

`propose` 產生既有專案 AI context 的可審查變更；`apply` 對已授權的專案自有內容進行有界調整。

## 輸入與輸出

指定問題、檔案、擁有者、權威與目標行為；輸出 before/after 或實際修改、來源/決策綁定、讀回、檢查與未解事項。

## 何時用／界線

適用規則、職責、導覽或衝突調和；不可改 managed core、生成 projection、安裝 lock 或 framework 安裝設定。未授權的語意決定應停下來交還 owner。

## 範例請求

使用 `ai-context-governance propose`，針對 `AGENTS.md` 與專案規則的重複職責提出最小改寫，保留自訂段落，先不要寫入。

## 知識

無套件綁定。

## 開始使用

先確認此 skill 已在專案的 runtime entries 中。向 agent 提供上面的操作、
實際範圍與輸入；範例 prompt 是自然語言請求，不是 shell 指令。
明確指定輸出位置及可寫範圍。使用 prefixed 安裝時，選單中的名稱可能是
`aicf-ai-context-governance`；canonical package ID 仍為 `ai-context-governance`。

此套件提供指令方法，不提供同名 CLI。Agent 依已安裝的 operation
reference 執行；若本次任務需要編輯或測試，使用專案已有且被授權的工具。

## 權威參考

- [Skill 入口](../../src/skills/ai-context-governance/SKILL.md)
- [版本、操作、依賴與 runtime metadata](../../src/skills/ai-context-governance/skill-package.yaml)
- [references/maintenance.md](../../src/skills/ai-context-governance/references/maintenance.md)

上述連結方便在來源庫核對；實際使用時應讀取已安裝套件中的相同資源。
