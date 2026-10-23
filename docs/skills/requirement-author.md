# requirement-author 使用說明

[回 Skill 目錄](README.md) · [安裝](../installation.md) · [知識選配](../knowledge-packages.md)

套件版本：`0.2.3`。操作名稱以實際安裝的 metadata 為準。

## 用途與操作

`explore` 先釐清有界問題、證據、已決事項、例子與未知；已有接受輸入可直接 `draft` 或 `normalize` 一份需求文件，維持利害關係人意圖、商業規則、來源與可觀察驗收。

## 輸入與輸出

提供需求範圍/來源、目標規則及可選模板/目的地；輸出需求草稿或保留語意/身分/核准狀態的 normalised document，並列假設、未解決事項與實際交付位置。

## 何時用／界線

需求可包含 GWT 驗收例子；領域模型的 aggregate／不變條件設計由 domain-model-designer 負責，軟體機制由 software-architect 負責。不自動加規格、測試設計或 problem-frame 階段；文件作者不能宣稱 stakeholder 已核准、已實作或已跑驗收。

## 範例請求

使用 `requirement-author draft`，依訪談紀錄與既有商業規則撰寫退款需求，為每條驗收條件附來源與可觀察結果，未知決策獨立列出。

## 知識

metadata 4 宣告 optional `engineering-common@0.4.0`。`explore` 可選 collaborative-discovery、BDD discovery、DDD domain-discovery；`draft`／`normalize` 可選 BDD discovery/formulation 與 DDD domain-discovery。只讀任務需要的資源，依 references/knowledge.md 驗證 lock、hash、allowlist 與 authority。缺少時揭露 unavailable，不偷讀 source，也不強制先 explore。

## 開始使用

先確認此 skill 已在專案的 runtime entries 中。向 agent 提供上面的操作、
實際範圍與輸入；範例 prompt 是自然語言請求，不是 shell 指令。
明確指定輸出位置及可寫範圍。使用 prefixed 安裝時，選單中的名稱可能是
`aicf-requirement-author`；canonical package ID 仍為 `requirement-author`。

此套件提供指令方法，不提供同名 CLI。Agent 依已安裝的 operation
reference 執行；若本次任務需要編輯或測試，使用專案已有且被授權的工具。

## 權威參考

- [Skill 入口](../../src/skills/requirement-author/SKILL.md)
- [版本、操作、依賴與 runtime metadata](../../src/skills/requirement-author/skill-package.yaml)
- [references/authoring.md](../../src/skills/requirement-author/references/authoring.md)
- [references/requirement-template.md](../../src/skills/requirement-author/references/requirement-template.md)
- [references/requirement-guide.md](../../src/skills/requirement-author/references/requirement-guide.md)

上述連結方便在來源庫核對；實際使用時應讀取已安裝套件中的相同資源。

已決事項不應重問；只有新的衝突證據影響本次產出時才重新釐清。探索完成不是需求核准或實作授權。

PRD／Feature／一般需求可繼續使用本技能；獨立 Story 的 plan／draft／normalize 或整份／指定 AC 審查，可在已安裝時選 [user-story-author](user-story-author.md)，不要求先經本技能。測試設計仍由 test-designer 負責。

## 公開需求內容的強制界線

公開 Epic／Feature／User Story／Issue 必須能獨立說明需求與驗收；授權與
交接必須使用 workflow 機制，不得存入線上 Issue 系統或留言。功能盤點、
設計討論、相依及已完成／待完成／延後的功能摘要可以保留；產品本身的
權限或審核行為仍可作為需求。依內容用途判斷，不使用關鍵字黑名單。
workflow 不可用時如實回報，不能改存 Issue 或宣稱已轉移紀錄。這是來源
指令契約；不代表現有安裝已升級、模型行為已驗收或已發布套件。
