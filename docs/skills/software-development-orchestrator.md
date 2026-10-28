# software-development-orchestrator 使用說明

[回 Skill 目錄](README.md) · [安裝](../installation.md) · [知識選配](../knowledge-packages.md)

來源套件版本：`0.5.0`。操作名稱以實際安裝的 metadata 為準。

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

## Issue 操作設定

在專案明確選定的 `config_version: 2` 設定檔，以
`skills.software-development-orchestrator.issue_control` 選擇方式；本來源 repo
使用 `.ai/project/framework.json`。Installer 不自動建立或改寫這項 project 設定。
這項來源能力使用新的 `instruction-settings` metadata 分支，須搭配支援它的 engine；
舊 loader 會拒絕新欄位，不會把它當作 filesystem store 設定。精確規則見
[issue-operation 設定契約](../../src/skills/software-development-orchestrator/references/issue-control.md)。

| 值 | 行為 |
| --- | --- |
| 缺省或 `""` | 不指定 framework route；agent 依當前工具與專案權限操作，仍須核對實際 provider 和命令 |
| `{"mode":"experimental","route":"issue-control"}` | 明確選擇未來實驗性 skill；目前尚未提供，因此所需操作 unavailable，不退回其他工具 |
| `{"mode":"project","route":"team-issue-skill"}` | 使用專案指定的實際 skill 或 MCP entry；可指向團隊自有 Azure DevOps 等工具，名稱須換成真實 route |

每次 operation 重新讀設定並依套件 schema 驗證。缺少明確選定的設定檔、格式錯誤
或 route 不可用都會停止依賴它的操作。設定不授權外部寫入、不安裝工具，也不提供
自動 provider fallback。Resume 保留已存在 work item 的完整 provider references；
改設定不會搬移資料或重新建立既有 Issue。

獨立 `local-backlog` 已從來源 catalog 與 presets 移除；既有 project records 保留。
新的 issue-control skill 尚在規劃，預計以 GitHub Issue／Project 及明確選用的本機
backlog 為初始範圍，並保留團隊流程差異；本版不宣稱已具備這些 provider。

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

## 公開需求內容的強制界線

公開 Epic／Feature／User Story／Issue 必須能獨立說明需求與驗收；授權與
交接必須使用 workflow 機制，不得存入線上 Issue 系統或留言。功能盤點、
設計討論、相依及已完成／待完成／延後的功能摘要可以保留；產品本身的
權限或審核行為仍可作為需求。依內容用途判斷，不使用關鍵字黑名單。
workflow 不可用時如實回報，不能改存 Issue 或宣稱已轉移紀錄。這是來源
指令契約；不代表現有安裝已升級、模型行為已驗收或已發布套件。
