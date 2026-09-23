# ADR / Lesson 生命週期設計 checkpoint

這是 [Issue #334](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/334) 的第一階段設計交付。整體 Issue 與 workflow 仍為 `in_progress`，尚未實作新工具，也沒有執行產品、schema 或 CI 驗證。

- [Contract](contract.md)：操作、狀態、權限、設定與相容策略。
- [Record shapes](record-shapes.md)：draft schema 欄位語意與寫入限制。
- [Interface proposal](interface-proposal.yaml)：版本、成員及 coordinator 待協調項目。
- [Synthetic examples](examples.json)：資料形狀示例，不是採納或執行證據。
- [Workflow](../../../workflows/2026-09-23-knowledge-lifecycle/workflow-plan.md)：實際檢查、延後項目與續作位置。

Lesson 保存觀察與適用條件；ADR 保存選項及實際決策。兩者都不會自動成為專案規則。Promotion 保存來源快照與規則提案，再分別讀回 owner 採納、目標檔案及專案生效宣告。單一 approval flag 或產生的文字不能替代這些事實。

建議新 Lesson 寫入 `lesson.record@2.0.0`，舊 `1.0.0` 原始檔案及 schema 保留。舊紀錄唯讀；需要延續時，明確衍生新 ID 並保存舊 bytes。這不是歷史資料批次轉換。

Coordinator 仍須統一 config / metadata 版本及 promotion owner，才會給這個 task 明確的 source 寫入範圍。這是已授權工作內的介面協調，不是重新要求使用者批准。
