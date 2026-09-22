# 手動缺口分流與限定撰寫工具

## Report Metadata

- `report_id`: `remediation-report-2026-09-22-artifact-gap-reduction`
- `workflow_id`: `2026-09-22-artifact-gap-reduction`
- `owner_skill`: `ai-context-governance`
- `status`: `draft`
- `created_at`: `2026-09-22T14:12:58+08:00`
- `updated_at`: `2026-09-22T15:53:53.643677+08:00`
- `template_source`: `.ai/assets/skills/ai-context-governance/templates/ai-context-remediation-report-template.md`
- `template_version`: `2.0.1`
- `baseline_assessment`: `ASM-20260921-18-gav`
- `verification_assessment`: `pending`

## Remediation Summary

[Issue #320](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/320) 接續 #319 的 16 個手動缺口。Owner 已授權必要實作與 skill／規範要求的線上操作；公開紀錄僅包含不涉及機敏資訊的技術內容。前次完成範圍維持封存，這份報告記錄新增工作。

不是每個手動項目都適合通用 writer。此次優先補上機械性、反覆出錯的輸入準備，並將涉及 owner 決策或真實執行狀態的項目逐一交代。原 91 列先拆成 94 列，本輪另登錄 remediation report 專用撰寫器，合計 95 列：61 executable、20 semantic-owner、9 manual-gap、4 external、1 creation-template。這是實際 producer 路由的拆分與補登，不代表新增相同數量的 schema。

## Changes And Evidence

- `execution-artifacts.py input` 新增 review-input、prepare-request、dependency-request、evidence-ledger 四種輸入操作；canonical review subject 由同一演算法產生。工具推導 Git tree、byte digest、record constants 與報告對照，避免重複手填。
- Preview 不寫檔。寫入需要相同 digest，只能建立新的 ignored、untracked、contained 檔案；拒絕 symlink／junction、碰撞、輸入與 Git 漂移。失敗只移除本次建立且 bytes 未變的輸出。
- Ledger 讀取既有 output／receipt，保留原 outcome；不製造、修復或重新簽發執行 receipt。自動產生的 human_report 是一致性投影，不是獨立審查結論。
- `catalog.update` 新增兩個 gate 說明 selector，只能改 reason；另有 rule-consumers selector，只能改既有 rule 的 derived_consumers。仍交由既有 owner validator 檢查候選內容。
- 共用 module loader 在執行模組前註冊 module identity，讓具有 dataclass 的 owner validator 正常載入；載入失敗恢復先前 module binding。
- 保留既有 CLI、validators 與測試，補上新相依路徑；不新增自動歷史遷移。

## Boundary Decisions

此次未放寬 required gates、reuse eligibility、實際執行證據、owner 選擇或 review admission。新增的是受限制的撰寫能力。完整 [16 項處置表](../evidence/manual-gap-dispositions.md) 記錄每一項的工具能力、保留理由與下一個條件。

Engineering Guardrails 的 accepted baseline、Git/provider 政策改由 semantic-owner 明確描述；這不代表已有自動 writer。lease、freeze、reuse、handoff、route matrix、local routing 以及三個與程式呼叫緊密相依的 registry 保留 manual-gap。它們需要具體的生命週期操作或 owner 決定，不能用欄位序列化冒充完成。

## Validation

下表保留各時點的 focused 支持證據與該次執行範圍；目前的固定提交驗證結果另外記錄於表格後方，兩者不混用：

| 範圍 | 結果 | 實測時間 | 限制 |
| --- | --- | --- | --- |
| 新 input 首輪 | 7 cases，6 passed／1 error | 23.983 s | dependency owner 的 dataclass 載入失敗；保留原 log。 |
| 修復後受影響 input | 1 passed | 2.168 s | 僅重跑原失敗案例；workflow 明示第三次嘗試授權。 |
| 額外 input／CLI／receipt／requirements 邊界 | 4 passed | 13.451 s | 包含 synthetic receipt fixture；不是實際執行驗收證據。 |
| 最終 input 邊界與 CLI | 11 passed | 51.877 s | 同時包含全部新增案例；仍屬局部單元／fixture 證據。 |
| 舊 execution／custody／migration／package import | 8 passed | 105.361 s | 選定相容性案例，非整包 matrix。 |
| 新 gate／consumer catalog | 8 passed | 22.841 s | 子代理唯讀外部狀態、單一 writer 實作；link 拒絕測試使用模擬邊界，未宣稱建立真實 junction。 |
| Lifecycle registry | 3 passed | 13.729 s | 確認登錄結構與 producer 路由。 |
| Validation profile registry | 11 passed | 19.394 s | 包含新增相依路徑；沒有移除 gate。 |
| Canonical AI context、workflow artifacts、diff whitespace | passed | 未保存獨立時間 | 結構／路由檢查；不等同所有行為或 hosted CI。 |
| CI 修復後相鄰 fixture class | 2 passed | 16.178 s | 此列只證明同一程序中舊、新 class 的隔離；完整 37-case hosted 結果見表格後的固定提交紀錄。 |

Input 與 catalog 各有一次 sandbox 暫存 fixture 存取失敗，均在行為 assertion 前發生；以 blocked-before-behavior 保存，不列 passed。改用正常可寫暫存 fixture 的執行邊界後才取得上述結果。完整輸出留在 ignored local artifacts，公開紀錄僅保留不含機敏路徑的摘要。

修復提交 `63b95af148b574a6dc5f2bc8149010975a8c4a93` 的五個必要 hosted contexts 已全部成功。Governance run `35696222621` 的 execution artifact suite 為 37/37（21.732 s），routing contract 為 9/9（5.197 s）；Portable run `35696222616` 亦成功。這些結果綁定該提交；最終 provider admission 仍需當前 PR head 的新鮮證據。

## Finding Resolution Matrix

| Finding | Status | Evidence |
| --- | --- | --- |
| ASM-20260921-18-gav#AIC-002 | partially-resolved | 已補具體 bounded producers，逐列保留其餘手動／語意責任；不宣稱所有 schema 可自動撰寫。 |

## Verification Assessment Reconciliation

第一次獨立審查已針對 `8d00452d14bd1b6aa3e4cc9f74ffdbee084f14c8` 執行，結果為 failed，保留 F-001／F-002／F-003：合併測試程序的 fixture module 快取污染、精簡套件不可用的文件命令、以及續作狀態過時。審查同時確認 16 項分流、限定 catalog 欄位與不製造執行結果的邊界；這些局部結論不抵銷失敗。

對應修正：每個 fixture class 擁有自己的 module/import path 與 cleanup；輸入範例使用明示 placeholder，source-only 測試以來源倉庫說明呈現；workflow、task 與本報告改為指向修復後固定版本審查。原始 failed review 與 CI 輸出保留，新的驗證不能覆寫它們。第二次審查確認 F-001／F-002 修復，保留 F-003 時間戳問題；第三次確認時間戳已補正，但指出歷次測試表格仍以現在式描述完整測試待執行，與後續 hosted 結果矛盾。8d31fc7d checkpoint 已將表格標示為歷次執行範圍；該修正不會改寫先前失敗的審查結果。

第三次審查已交回 failed 結果並釋放 lease。自動核准審查拒絕建立第四次重試授權，理由是連續審查失敗後，缺少使用者對這項新增重試決策的明確授權。該 checkpoint 未執行第四次審查；本輪新增工具依後續 owner 指示實作，不作為自身實作的獨立通過證明。

初次 hosted runs `35694811987`／`35694812154` 失敗；其中 execution-artifacts suite 執行 26 個既有案例後在新 class setup 出錯，並非 37 個全部通過。精簡套件引用案例亦失敗。PR 首次取得編號後缺少綁定宣告，是另一項尚待補齊的 admission 條件。套件建置與兩個平台前置契約通過，不構成整體 CI 通過。

## Deferred Work

保留的 owner 邊界與專用生命週期需求見處置表。此次沒有修改個人 CLI binding、provider baseline、release allocation、tag、publication、credential 或 downstream target。後續具體變更應由相應 owner 在具備所需輸入時執行。

## 文件欄位自動化補強

Owner 指出本次工具應直接避免漏更新欄位，因此新增 GAP-003。先前手動修改報告時間的做法由以下正式操作取代：

| 文件 | 工具維護方式 |
| --- | --- |
| workflow.yaml、workflow-plan.md、INDEX.MD 選定列 | workflow 操作同步時間、狀態與階段；workflow.update 同時接收正文變更。 |
| task JSON | workflow.progress 記錄實際完成步驟、下一步與選定 observations；workflow.transition 處理明示狀態轉換。 |
| remediation-report.md | workflow.report 建立或明確接管目前 draft；保留 report_id、created_at、baseline 與 template identity，自動更新 updated_at。 |
| plan／report 的 Current Workflow State | 從 workflow.yaml 與全部 task 產生，後續 workflow 操作自動同步；不另手填目前狀態。 |
| terminal Issue closure 宣告 | 保留其專用 admission owner；未從報告或 CI 敘述自動推定 provider 結果。 |

Request 省略 timestamp 時，工具在 preview 自動取得實際時間；JSON preview 保存已解析的 request，apply 使用原 preview 與 digest，不再次取時，也不需人工填日期。既有明示 timestamp API 保持相容；時間倒退或未知版本仍拒絕。建立 assessment 的身分日期仍必須與實際建立時間一致。

報告維持 draft，直到 workflow 完成且有已存在、連結同一 workflow／baseline 的 final verification assessment，才產生 editorial final。這不等於審查通過或 GitHub 結案。歷史測試與失敗證據保留為作者敘述，既有 final report 不會被悄悄改寫。工具不掃描或改寫未明確接管的歷史報告。

使用既有 workflow validator 檢查機械性欄位與投影一致性，沒有新增 required gate、移除測試或放寬驗證／授權規範。任意自然語言中的矛盾仍需作者核對；本輪將易漂移的目前狀態集中為自動產生區塊。

## 本輪驗證紀錄

新增自動化首批案例 8/8 passed（68.565 s）；相鄰時間、handoff、assessment finality、原樣恢復與原失敗 fixture 共 6/6 passed（33.086 s）。案例涵蓋 CLI 無 timestamp、preview 漂移、工具欄位注入、錯誤參照、重複 metadata、狀態同步、final 不可改寫及跨檔中斷恢復。這些是本機 fixture 支持證據，不是 hosted CI 或獨立審查結論。

首次 sandbox 執行在建立／清理暫存 fixture 時被環境拒絕，未到行為 assertions；放到可寫執行邊界後，首輪為 7 passed／1 fixture error。該 error 是測試固定 assessment ID 與自動目前時間不一致，已修正 fixture，保留失敗紀錄；後續通過不抹除先前失敗。

另有 lifecycle registry 3/3（5.988 s）、validation profile registry 11/11（6.980 s）、精簡套件 CLI/import 相容案例 1/1（3.304 s）通過。實際 CLI 使用發現生成區塊更新在檔尾多留空白行，修正後新增格式回歸案例，並連同投影同步與跨檔恢復共 3/3 passed（18.767 s）。新增自動化案例共九個；這三項包含兩項受影響案例的重驗，沒有宣稱重新執行未受影響的完整矩陣。Canonical AI context 檢查亦已通過。

## Closure Evidence

交付分支對應 [PR #321](https://github.com/YuChia-Wei/ai-collaboration-framework/pull/321) 與 [Issue #320](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/320)。上方 CI 證據僅適用其明確列出的 commit。GitHub admission、integration 與 Issue 結案由各自實際回讀證據決定；下方自動區塊只描述本地 workflow/task 記錄。

## Current Workflow State

<!-- artifact-authoring: workflow-state/v1; generated from workflow.yaml and tasks -->
- Workflow status: `blocked`
- Current phase: verification

| Task | Status | Last completed step | Next action |
| --- | --- | --- | --- |
| GAP-001 | completed | Implemented four input preparers. Attempt 1 was blocked before tests by sandbox fixture permissions; attempt 2 ran 7 tests, 6 passed and dependency-request failed because the shared loader did not register dataclass modules. | Runtime input implementation and selected checks complete; continue GAP-002 integration and fixed-subject verification. |
| GAP-002 | blocked | Third independent review retained F-003 historical wording; corrected in 8d31fc7d. Prior failed evidence remains preserved. | Await explicit authorization for further independent review, including the owner-requested report automation changes; do not dispatch a new retry implicitly. |
| GAP-003 | completed | Implemented automatic preview timestamps, report/progress operations and generated current-state checks; 8 automation cases and 6 focused compatibility cases passed. |  |

Recorded workflow state is not independent verification, current-head CI admission, or provider closure.
