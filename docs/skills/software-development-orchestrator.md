# software-development-orchestrator 使用說明

[回 Skill 目錄](README.md) · [安裝](../installation.md) · [知識選配](../knowledge-packages.md)

套件版本：`0.2.0`。操作名稱以實際安裝的 metadata 為準。

## 用途與操作

`orchestrate` 將授權開發成果拆成必要階段並協調；`resume` 先將 checkpoint 與當前 project truth 調和後續作業。

## 輸入與輸出

提供開發成果、驗收、授權、已採納 artifact、專案規則、可用 capability、指令或既有 checkpoint；輸出有比例的 stages/owners/dependencies、實際結果、驗證、未解 handoff 和 closeout/checkpoint。

## 何時用／界線

複合、多階段工作才用；小型局部變更不需完整管線。它不規定 record schema、storage、provider 或 installation，也不恢復已退役的 0.1 workflow-record tool。

## 範例請求

使用 `software-development-orchestrator orchestrate`，以既有需求、架構決策與驗收條件規劃並推進這個 API 變更；保留每個外部寫入的授權邊界和未解決 owner 決定。

## 知識

無套件綁定。

## 開始使用

先確認此 skill 已在專案的 runtime entries 中。向 agent 提供上面的操作、
實際範圍與輸入；範例 prompt 是自然語言請求，不是 shell 指令。
明確指定輸出位置及可寫範圍。使用 prefixed 安裝時，選單中的名稱可能是
`aicf-software-development-orchestrator`；canonical package ID 仍為 `software-development-orchestrator`。

此套件提供指令方法，不提供同名 CLI。Agent 依已安裝的 operation
reference 執行；若本次任務需要編輯或測試，使用專案已有且被授權的工具。

## 權威參考

- [Skill 入口](../../src/skills/software-development-orchestrator/SKILL.md)
- [版本、操作、依賴與 runtime metadata](../../src/skills/software-development-orchestrator/skill-package.yaml)
- [references/orchestrate.md](../../src/skills/software-development-orchestrator/references/orchestrate.md)

上述連結方便在來源庫核對；實際使用時應讀取已安裝套件中的相同資源。
