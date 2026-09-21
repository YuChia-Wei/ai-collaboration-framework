# Workflow／Assessment 撰寫工具 P1 說明報告

## Report Metadata

- `report_id`: `remediation-report-2026-09-21-schema-artifact-lifecycle`
- `workflow_id`: `2026-09-21-schema-artifact-lifecycle`
- `owner_skill`: `ai-context-governance`
- `status`: `draft`
- `created_at`: `2026-09-21T21:46:40+08:00`
- `updated_at`: `2026-09-21T21:46:40+08:00`
- `template_source`: `.ai/assets/skills/ai-context-governance/templates/ai-context-remediation-report-template.md`
- `template_version`: `2.0.1`
- `baseline_assessment`: `ASM-20260921-18-gav`
- `verification_assessment`: `pending independent verification`

## Remediation Summary

依你閱讀分析報告後的授權，已實作 P1：提供共用 CLI 與 workflow／assessment 專用操作，讓工具維護 locator、task、Markdown metadata 和 index。正式工作項目是 [Issue #316](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/316)。本報告目前保留為 draft，等待獨立驗證與發現調和。

這次先處理分析時實際遇到的索引標題不一致、workflow 關聯格式錯誤，以及多檔更新容易漏改的問題。沒有移除驗證器、刪除既有測試，或放寬現行治理規則。P2–P4 的其他 producer 接入、遷移與測試整併仍保留為後續階段。

## Changes And Evidence

入口是 [artifact-authoring.py](../../../../.ai/scripts/artifact-authoring.py)，共用實作為 [artifact_authoring.py](../../../../.ai/scripts/artifact_authoring.py)，完整輸入與命令見 [使用說明](../../../../.ai/scripts/README.md#workflow-and-assessment-authoring)。

| 能力 | 本次實作 | 實際意義 |
| --- | --- | --- |
| Workflow 建立 | 一次產出 locator、plan、初始任務與索引列 | 作者提供意圖與實際執行身分，不需手寫整個 envelope。 |
| 任務管理 | 新增 pending 任務、有限狀態切換、同次交接下一任務 | 維持適用的單一 active task；完成狀態必須附作者觀測。 |
| Assessment 建立／更新／定稿 | Auditor 的 audit／verification profile；受控 draft 更新 | 自動同步 metadata 與索引區段，受評 subject 與建立時間不變。 |
| 寫入前驗證 | 既有兩個 validator 讀取記憶體中的完整預計狀態 | 不另複製同一套跨文件、索引與生命周期規則。 |
| 預覽與變動偵測 | Unified diff、摘要綁定輸入／執行程式／Git；套用時重新推導 | 過期預覽、碰撞、未知版本或非法關聯在寫入前拒絕。 |
| 部分寫入復原 | 本地 ignored journal、合作式鎖、明確 rollback | 保留原始與候選位元組證據；外部修改不覆蓋。 |
| 相容性 | 舊 validator CLI 不變；新增 portable entrypoint、profile gate 與套件 import 測試 | 新工具加入現有執行方式，沒有建立另一套測試入口權威。 |

共用驗證只抽出 workflow 的 `validate_workflows(repo)` 函式；CLI 執行方式與語意不變。Assessment validator 無需改寫。Writer 額外比較前後狀態，補上既有「單一文件快照」驗證無法證明的不可變性。

## Rules Retained And Authoring Restrictions

**沒有放寬現行規範。** 被工具接手的是人工維護模板版本、衍生路徑、metadata 時間與索引列的工作。你仍需提供 scope、正文、真正觀測和授權；工具成功不代表文件裡提到的測試或事件已發生。

保留必要欄位、精確型別、duplicate-key 拒絕、未知版本拒絕、ID／created_at／subject 不可變、final conclusions 凍結、失敗與未執行結果的真實性，以及原有 provider／merge／release 邊界。這次沒有提出可立即刪除的等價測試案例。

Writer 的可寫範圍比 reader 更窄：只支援兩個已選定 profile、目前模板版本與有限操作。已完成 workflow 或已定稿 assessment 不能由此工具重新開啟。這是 P1 的能力限制，不是改寫 repository 的歷史修訂政策。

JSON／YAML extension 值會保留；Markdown metadata 以局部方式更新，其餘正文保留，只有明確的 draft-body replacement 會換正文。YAML 重序列化可能改變空白／呈現，diff 會顯示；含 comment-like 文字的 YAML 會先拒絕更新，避免悄悄丟失註解。報告內容與領域章節仍由作者負責，工具不代寫結論。

## Validation

| 檢查 | 結果與範圍 |
| --- | --- |
| Authoring regression | 20 tests passed，42.820 秒；包含真實 Windows junction、hard link、外部修改、程序 abrupt exit、部分寫入 rollback、定稿不可變、關聯批次診斷及型別／版本。 |
| 獨立 oracle | 手寫語意輸入、固定預期值及失敗注入；相容 optional extension 保留，新增必填 placeholder 拒絕，沒有只用生成器自驗。 |
| Portable CLI | 隔離 package/payload 僅含必要 portable module／模板，catalog 與完整 preview 通過；不是完整發佈矩陣。 |
| 既有 regression | Workflow lifecycle 與 assessment suites 通過；7 個 entrypoint contract tests、11 個 profile registry tests 通過。 |
| Repository checks | Shell assets、validation lifecycle、AI context、6 個 deterministic AI-behavior evaluation cases 通過。 |
| 獨立驗證 | pending；完成後記錄另立 assessment 與固定 subject。 |

保留的失敗紀錄：初次 live preview 因 CRLF 模板版本讀取失敗，修正後同輸入兩次 preview 摘要一致；sandbox 的 Windows Temp 權限使 fixture setup／cleanup 未能完成，Git Bash signal-pipe 權限使 registry checks 無法執行，經工具權限流程在相同主機正常執行後通過。另一次 evaluation 呼叫缺少 `validate` 子命令，正確命令已通過。早期環境失敗與準備失敗都不是 behavioral pass。

## Cost And Limitations

一個 workflow 請求推導 4 份變更（locator、plan、task、index）；assessment 請求推導 3 份變更（locator、report、index）。作者仍需撰寫語意內容，但不需人工同步這些檔案的衍生欄位。預覽與套用需要 2 次 CLI 呼叫；這是可核對的機械工作差異，並非已量測的 token 或時間節省比例。

沒有做人工流程的對照計時或 token 統計。完整投影驗證會讀取現有 workflow／assessment，因此大型資料庫的預覽成本仍存在；未對此宣稱加速。套用是逐檔寫入，**不是跨檔 atomic transaction**，也不保證斷電耐久性或排除惡意並行程序。遇到程序中斷的 stale lock，須先確認 writer 已停止，再移除該鎖並復原。若復原依賴已變更或檔案已被他人修改，保留 journal 交由人工調和。

## Finding Resolution Matrix

| Assessment Finding | Status | 本次對應與剩餘範圍 |
| --- | --- | --- |
| ASM-20260921-18-gav#AIC-001 | partially-resolved | CLI catalog 明列兩個 profile 的 template owner、可寫範圍與 unsupported migration；全庫 coverage registry 留待後續。 |
| ASM-20260921-18-gav#AIC-002 | partially-resolved | 多檔、關聯、索引與機械 metadata 由工具維護；領域正文仍由作者提供。 |
| ASM-20260921-18-gav#AIC-003 | deferred | 更廣的 migration disposition 與版本轉換未納入 P1。 |
| ASM-20260921-18-gav#AIC-004 | deferred | P1 已保留兩個 profile 的 extension 值；其他 family 的 unknown-field／serialization 規則尚未納入。 |
| ASM-20260921-18-gav#AIC-005 | deferred | 測試刪減與成本量測需要後續等價性證據。 |

## Verification Assessment Reconciliation

尚待獨立 auditor 對固定 commit 檢查 Issue #316 的驗收條件、工具限制、資料保存與測試證據。此 remediation report 由實作者維護，不作為獨立審查結論。

## Deferred Work

P2 先評估與既有 producer 共用 parsing／diagnostics 的真正重複部分，再挑選下一個 editable family。P3 的遷移必須逐版本宣告 convert／regenerate／re-execute／historical／unsupported。P4 只有在指出替代 coverage 後才移除重複 checks/tests。責任人為 maintainer，依原分析順序選擇下一階段。

## Closure Evidence

目前 P1 實作與 focused checks 已完成，workflow 轉入獨立驗證。尚未 push、建立 PR、merge、關閉 Issue、分配 release 或修改任何下游 repository。
