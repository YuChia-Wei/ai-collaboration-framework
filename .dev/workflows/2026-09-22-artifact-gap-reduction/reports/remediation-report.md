# 手動缺口分流與限定撰寫工具

## Report Metadata

- `report_id`: `remediation-report-2026-09-22-artifact-gap-reduction`
- `workflow_id`: `2026-09-22-artifact-gap-reduction`
- `owner_skill`: `ai-context-governance`
- `status`: `draft`
- `created_at`: `2026-09-22T14:12:58+08:00`
- `updated_at`: `2026-09-22T14:20:17+08:00`
- `template_source`: `.ai/assets/skills/ai-context-governance/templates/ai-context-remediation-report-template.md`
- `template_version`: `2.0.1`
- `baseline_assessment`: `ASM-20260921-18-gav`
- `verification_assessment`: `pending`

## Remediation Summary

[Issue #320](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/320) 接續 #319 的 16 個手動缺口。Owner 已授權必要實作與 skill／規範要求的線上操作；公開紀錄僅包含不涉及機敏資訊的技術內容。前次完成範圍維持封存，這份報告記錄新增工作。

不是每個手動項目都適合通用 writer。此次優先補上機械性、反覆出錯的輸入準備，並將涉及 owner 決策或真實執行狀態的項目逐一交代。原 91 列拆成 94 列：60 executable、20 semantic-owner、9 manual-gap、4 external、1 creation-template。增列來自將混合的 tooling registries 拆成四類；並非宣稱新增三種 schema。

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

目前的 focused 支持證據（尚非最終固定 subject 的全面通過）：

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
| CI 修復後相鄰 fixture class | 2 passed | 16.178 s | 同一程序依序執行舊、新 class，驗證快取隔離；完整 required suite 仍待固定提交的 hosted 結果。 |

Input 與 catalog 各有一次 sandbox 暫存 fixture 存取失敗，均在行為 assertion 前發生；以 blocked-before-behavior 保存，不列 passed。改用正常可寫暫存 fixture 的執行邊界後才取得上述結果。完整輸出留在 ignored local artifacts，公開紀錄僅保留不含機敏路徑的摘要。

## Finding Resolution Matrix

| Finding | Status | Evidence |
| --- | --- | --- |
| ASM-20260921-18-gav#AIC-002 | partially-resolved | 已補具體 bounded producers，逐列保留其餘手動／語意責任；不宣稱所有 schema 可自動撰寫。 |

## Verification Assessment Reconciliation

第一次獨立審查已針對 `8d00452d14bd1b6aa3e4cc9f74ffdbee084f14c8` 執行，結果為 failed，保留 F-001／F-002／F-003：合併測試程序的 fixture module 快取污染、精簡套件不可用的文件命令、以及續作狀態過時。審查同時確認 16 項分流、限定 catalog 欄位與不製造執行結果的邊界；這些局部結論不抵銷失敗。

對應修正：每個 fixture class 擁有自己的 module/import path 與 cleanup；輸入範例使用明示 placeholder，source-only 測試以來源倉庫說明呈現；workflow、task 與本報告改為指向修復後固定版本審查。原始 failed review 與 CI 輸出保留，新的驗證不能覆寫它們。第二次固定版本審查仍待完成，本報告不作為自身實作的獨立通過證明。

初次 hosted runs `35694811987`／`35694812154` 失敗；其中 execution-artifacts suite 執行 26 個既有案例後在新 class setup 出錯，並非 37 個全部通過。精簡套件引用案例亦失敗。PR 首次取得編號後缺少綁定宣告，是另一項尚待補齊的 admission 條件。套件建置與兩個平台前置契約通過，不構成整體 CI 通過。

## Deferred Work

保留的 owner 邊界與專用生命週期需求見處置表。此次沒有修改個人 CLI binding、provider baseline、release allocation、tag、publication、credential 或 downstream target。後續具體變更應由相應 owner 在具備所需輸入時執行。

## Closure Evidence

實作 checkpoint `8d00452d14bd1b6aa3e4cc9f74ffdbee084f14c8` 已推送，並建立 [draft PR #321](https://github.com/YuChia-Wei/ai-collaboration-framework/pull/321)。本次修正接續該 checkpoint；下一個 gate 是針對包含修正的固定提交重驗受影響行為與進度記錄。PR 宣告維持 deferred，Issue #320 開啟中；hosted admission、integration 與結案尚未完成。最終線上結果由 provider read-back 記錄，不能先寫成 passed。
