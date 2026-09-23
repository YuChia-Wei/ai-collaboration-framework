# P5 能力收斂與格式處置設計

這是 [Issue #342](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/342) 的設計交付，屬於 program #322 / U001。**處置與 metadata v3 都是待協調者選擇的提案**，並未改變現行規則、啟用技能、實作工具或執行 migration。

## 對使用者的改變

一般使用者只選所需能力，例如 review、需求撰寫或 ADR。review 可直接讀取使用者提供的程式與規則，回傳有依據的文字結果；不應先建立 AI-context 維護 workflow、effective-rule packet、角色登錄或 95 類記錄。必要的權限、真實證據與目標專案規則仍然存在。

有保存、查詢、狀態轉換需求的 ADR／Lesson 等資料，由該能力的 schema 和實際工具負責。定性推理與機械操作分開表達：寫出建議不是執行工具、存成檔案不是通過驗證、套件存在也不是已安裝。安裝／更新由 P6 負責；低頻的 context audit 與語意調整是選配；source 發版、歷史結案與 provider reconciliation 不下放。

## 已盤點的範圍

- **16 個 legacy canonical skills**：10 個 specialist 能力建議可選攜帶，2 個 context audit/governance 路由建議選配，init/upgrader 的安裝更新責任交 P6，1 個 orchestrator 交 P4 #341，1 個 release-closeout 留 source-only。保留方法，逐項拆開隱藏路徑與來源治理相依。
- **95 個 artifact kind**：原分類 portable 60、source 34、dotnet 1；authoring 標籤 executable 61、semantic-owner 20、manual-gap 9、external 4、creation-template 1。標籤不是執行證據，也不是 95 個 schema。
- 保留每筆 kind ID、原 registry row、model 路徑與 Git blob。17 個責任群提出 33 source-only、21 preserve-unsupported、16 replaced-preserve、14 retired-preserve、6 optional-deferred、4 portable-selectable、1 external-preserve。`retired` 僅建議退出新產品 active use，**不授權刪除、停止舊 transaction recovery 或重寫歷史**。
- **5 個真實 src 套件、6 個 record schema resource**：ADR 8 members、Lesson 9、local-backlog 8、PR 10、standards-promotion 9。另列 config、metadata、manifest/profile、生成輸出、request/result 與外部 evidence 的格式責任。

起始證據固定在 `94741016bd7baae9936bb77dd6c4f56d37036e97`。該版本已有五個套件原始碼，但 shared manifest/profile 仍指向 Lesson 0.1.0 / 8 members；Lesson 實際為 0.2.0 / 9 members。這是 #337 已分工的 mapping 工作，本設計不改寫，也不宣稱可 build/install。之後整合不追溯改變此快照。

## 閱讀順序

1. [能力處置與方法](capability-disposition.md)：每個 skill 的保留方法、輸出與具體相依。
2. [95 筆精確處置](legacy-artifact-dispositions.json)與[格式責任](format-ownership.md)：原始 row 與提案分開；群組不消失 ID。
3. [操作模型](operation-model.md)：最小 metadata v3、純推理例、現有 ADR schema authoring 對照。
4. [後續切片與決策](implementation-slices.md)：共享檔單一 writer、前置條件、M01 版本轉換候選、Issues 重疊。
5. [workflow 交接](../../../workflows/2026-09-23-capability-consolidation/reports/handoff.md)：實際檢查、限制與 Git 續作定位。

詳細資料：[16 skills](legacy-skills.json)、[src members/schemas](current-src-formats.json)、[證據](../../../workflows/2026-09-23-capability-consolidation/evidence/source-observation.json)。path occurrences 包含條件相依、範本、角色與舉例；不把每條文字連結視為必載 runtime dependency。模式路徑及未解析路徑保留原文，不偽造完整 semantic closure。

## 交給協調者的選擇

建議先選 D342-01（metadata v3 指令操作與無 store 能力），再安排第一個 code-reviewer 純推理套件。其後依需求選 specialist、prose authoring、可選 maintenance。結構化 problem frame 與 optional assessment 先決定最小格式與 writer 邊界，不一次搬動 legacy machinery。來源 code/profile/root cutover 均由後續 owner 執行。

本次只做 UTF-8／JSON／YAML 直接讀取、無 import 的 Python AST、特定來源／Git 核對、diff 及指定 commit-message 格式檢查。產品 CLI（含 help）、schema validators、測試、build/install/migration/compatibility、獨立 audit／lease 及 CI 均為 **deferred-by-owner：U001，program #322 coordinator / P7**。沒有 runtime coverage、相容性或效能提升主張。

Subsequent dependency state: [P3 integrated mapping and P4 selected contract](dependency-update.md). Baseline inventory remains pinned; P4 source is not yet delivered.
