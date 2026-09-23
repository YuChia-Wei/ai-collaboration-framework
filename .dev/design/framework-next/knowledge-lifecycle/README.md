# ADR / Lesson 生命週期交付

[Issue #334](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/334) 的
三個獨立套件來源已完成：Lesson 0.2.0、ADR 0.1.0、Standards Promotion 0.1.0。
原始設計 commit `99adb0762328c8f8d6cff7338f17caec99685c0a` 保留；目前文件反映
coordinator 選定的 [P3 共同契約](../p3-shared-contract.md)。
這是本機 source 交付；不代表產品執行、schema 驗證、CI、安裝或發布已通過。

- [Contract](contract.md)：操作、狀態、權限、設定與相容策略。
- [Record shapes](record-shapes.md)：結構及執行期語意限制。
- [Interface inventory](interface-proposal.yaml)：9／8／9 個成員與 11／11／10 個操作。
- [Synthetic examples](examples.json)：原始合成資料，不是採納或執行證據。
- [Workflow](../../../workflows/2026-09-23-knowledge-lifecycle/workflow-plan.md)：實際檢查、延後項目與交付位置。

Lesson 保存觀察與適用條件；ADR 保存替代選項及 owner 決策。兩者都不會自動
成為專案規則。Promotion 保存來源快照與單檔替換提案，再分別讀回採納、目標
檔案及專案生效宣告；工具不寫入規則或批准檔案。曾觀察到採納後，不得 revise；
解決衝突必須建立新 proposal 身分並取得新採納。

Lesson v1 schema 原始 bytes 保留，舊紀錄唯讀。明確 derive 才建立新的 v2 candidate，
保留來源快照並重設決策；不進行原地或批次轉換。三個套件不互相匯入 private files，
也不依賴本設計資料夾。Shared distribution／manifest／profiles 由 coordinator 與 #337 負責。

行為、schema、相容性、獨立審查與 CI 均依 U001 保持 `deferred-by-owner`，由
program #322 coordinator／P7 選擇並執行。Issue／Project／整合狀態不由此來源交付推定。
