# software-development-orchestrator 使用說明

[回 Skill 目錄](README.md) · [安裝](../installation.md) · [知識選配](../knowledge-packages.md)

套件版本：`0.4.1`。操作名稱以實際安裝的 metadata 為準。

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

編排 task 時先規劃驗證目的、項目、觸發條件與執行時機，區分必要 gate／已接受驗收與依影響選用的檢查。
實作期間依實際差異校正，執行測試前確認必要性；完成修改後確認驗收證據齊備。
跨 task 的共同驗證安排在適當整合點，避免每個 task 重複執行；必要 gate 仍須遵守。
重現 bug、TDD 或分段檢查可在修改前或修改中進行，不要求所有測試等到最後。
無語意影響的說明或空白不自動觸發測試；會影響解析、schema 或輸出的空白仍需檢查。
高成本驗證須有受影響行為／邊界或明確要求，且不自動展開全矩陣。
專案必要的 PR、安全及發版義務仍有效；未執行不代表通過。

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

按阻礙成果的未知選 owner：需求意圖交 requirement-author；語言、規則與模型歧義交 domain-model-designer；依賴、軟體結構與技術機制交 software-architect。混合問題可先做有界探索，逐段形成可供下一步使用的結果，不強制完整流水線。spec-author 依接受的需求與設計形成系統規格；test-designer 負責測試層級、資料與預期結果來源。技術限制無法滿足業務一致性時，回饋模型 owner，不自行改寫規則。BDD／DDD metadata 可用不代表每次全讀。

獨立 Story 規劃、撰寫、正規化或整份／指定 AC 需求審查，可在可用時選 user-story-author；PRD／Feature／一般需求仍由 requirement-author 處理，不構成必經管線。
