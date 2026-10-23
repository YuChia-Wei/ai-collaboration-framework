# user-story-author 使用說明

[回 Skill 目錄](README.md) · [安裝](../installation.md)

套件版本：`0.2.1`。這是來源 catalog 的獨立選配能力；可用性依實際安裝
版本與 runtime entry，不代表本來源專案已自行安裝。

## 用途與操作

`plan` 依獨立價值／技術成果或學習成果提出 Story 切分、依賴及理由。
`draft` 從一個明確需求撰寫 Story；`normalize` 保留既有意義、ID、狀態與
格式並記錄實際調整。`review` 可只審查整份 Story 或指定一個／多個 AC，
僅回報選定範圍的問題、依據、影響與有界建議。

## 範本與輸出

caller／目標專案範本優先，否則依成果選 user-value、business-rules 或
technical 三套 Description 範本；研究可調整 technical 範本，保留學習問題、
證據輸出、時間／範圍界線、停止條件與決策 owner，缺少的條件保持未知。
輸出分開的 Title、Description、Acceptance Criteria，可分別貼入 Azure
DevOps 等系統，不強制 provider 或自訂欄位。另附必要來源／版本／狀態、
真實依賴或明標的本機提案代號，以及需求未知事項的影響。執行授權、
下一位 Agent 的操作與交接必須另存 workflow 機制，不得附加到 Issue 正文或留言。支援 caller 語言，包括臺灣繁體中文。

既有 GWT、非 Gherkin 技術 AC 與自訂範本均可保留，不會自動轉寫或改變
驗收意義。缺少資料只阻擋相關主張，不必先建立 PRD 或完整技能管線。

## 責任界線

requirement-author 保留 PRD／Feature／一般需求；此技能負責獨立 Story
規劃、撰寫及需求／AC 審查。test-designer 負責測試案例、層級、資料、oracle
機制與覆蓋。Story review 不修改受審內容或 provider 狀態，僅在要求時匯出
報告；無發現不代表產品驗收通過。撰寫也不授予實作、核准或外部寫入權限。

## 範例請求

```text
使用 user-story-author review，只審查以下 Story 的 AC-2。
保留既有 GWT；可讀 Description 和相鄰 AC 作為解讀脈絡。
只回報 AC-2 的問題、來源、影響與建議；不修改 Story。
```

沒有 configuration、工具或必要 skill 相依。Metadata 4 宣告 optional
engineering-common@0.4.0：plan 可選 BDD/DDD discovery 與 collaborative discovery；
draft/normalize/review 可選 BDD discovery/formulation 與 DDD discovery。依
[knowledge protocol](../../src/skills/user-story-author/references/knowledge.md) 驗證
lock／hash／authority 與 allowlist，缺少時揭露 unavailable，不讀 source 補缺。
方法不授權模型／技術選型，GWT AC 不等於測試層級／資料／oracle 設計。
這是指令技能，沒有同名 CLI。選配時在 skills 清單明確加入
`user-story-author`；既有 presets 不因此新增它。prefixed 安裝的 runtime
名稱可為 `aicf-user-story-author`，canonical ID 不變。

## 權威參考

- [Skill 入口](../../src/skills/user-story-author/SKILL.md)
- [套件 metadata](../../src/skills/user-story-author/skill-package.yaml)
- [共同 Story／AC／交接契約](../../src/skills/user-story-author/references/story-contract.md)
- [範例](../../src/skills/user-story-author/references/examples.md)

以上來源連結供核對；實際執行讀取已安裝套件資源。

## 公開需求內容的強制界線

公開 Epic／Feature／User Story／Issue 必須能獨立說明需求與驗收；授權與
交接必須使用 workflow 機制，不得存入線上 Issue 系統或留言。功能盤點、
設計討論、相依及已完成／待完成／延後的功能摘要可以保留；產品本身的
權限或審核行為仍可作為需求。依內容用途判斷，不使用關鍵字黑名單。
workflow 不可用時如實回報，不能改存 Issue 或宣稱已轉移紀錄。這是來源
指令契約；不代表現有安裝已升級、模型行為已驗收或已發布套件。
