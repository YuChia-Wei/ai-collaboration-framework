# P3 第一批：動態角色 metadata 撰寫與遷移

## Report Metadata

- `report_id`: `remediation-report-2026-09-22-role-metadata-authoring`
- `workflow_id`: `2026-09-22-role-metadata-authoring`
- `owner_skill`: `ai-context-governance`
- `status`: `final`
- `created_at`: `2026-09-22T07:28:50+08:00`
- `updated_at`: `2026-09-22T07:44:44+08:00`
- `template_source`: `.ai/assets/skills/ai-context-governance/templates/ai-context-remediation-report-template.md`
- `template_version`: `2.0.1`
- `baseline_assessment`: `ASM-20260921-18-gav`
- `verification_assessment`: `ASM-20260922-07-0n1`

## Remediation Summary

本批次實作兩個操作：現有動態角色的 `role.update`，以及明示的 `role.migrate`（schema 1.0 → 1.1）。它們沿用 P1 的 preview／apply／recover，不增加另一套交易引擎。這是 P3 的第一個 artifact family；其他 metadata/catalog 尚未完成。[Issue #318](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/318) 記錄範圍。

選擇這個家族，是因為 canonical schema 明確記載 migration，Git 歷史也有可獨立比對的真實範例。`6aed5786033d404fdfe9eaa8961f51a071321b5f` 對動態角色只改版本並補上空 `adapter_metadata`；有 runtime adapter 的角色則需要人為決定確切路徑，不能套用同一自動轉換。

## Changes And Evidence

### 使用方式與改善

`role.update` 依 asset ID 尋找 shared 或 skill-private 的既有角色，只允許修改 title、purpose、triggers、inputs、outputs、constraints、references、examples。身份、狀態、workflow、runtime disposition 與 owning-skill bindings 都受保護。未知頂層與巢狀 extension 的值會保留；格式可能正規化，實際 YAML 註解則拒絕改寫，以免無聲遺失。

`role.migrate` 必須明示 from_version=1.0、to_version=1.1，且 wrapper_targets 原本已是空清單，adapter_metadata 原本不存在或為空 mapping。只變更這兩個欄位。1.0 只是 migration input，不會因此成為現行 canonical admission；其他版本、promoted adapters、已搬移而失效的參照都需要 owner reconciliation。兩種操作目前均限定動態角色。

候選檔案在記憶體中接受原 canonical 欄位與 owner/projection 檢查。抽出的共用函式直接接收 candidate mapping，避免讀到磁碟上的舊檔而誤判。preview 綁定被讀取的 manifests、目錄成員、參照存在性、schema／template／role contract，以及新增的 validator/runtime 相依。apply 重算 preview，原始完整 bytes 存在 ignored recovery journal；復原拒絕外部修改與偽造輸出。

角色 writer 的檢查不聲稱驗證未修改的 runtime wrappers；完整 canonical validator 仍是 repository admission gate。其他不合法 contextual manifests 也可能阻擋單檔操作，因此這不是跨整個 repository 的歷史格式批次升級工具。

### 規範變動

沒有放寬現行 schema、owner binding、receipt、release 或驗證門檻，也沒有刪除任何 validator／test。便利性上的增加是允許專用工具讀取已知 1.0 動態角色作為遷移輸入；正式寫入／採認仍需符合 1.1。註解、aliases、未知 request 欄位、身份與 runtime 選擇仍拒絕。

另外收緊兩個原有實作缺口，使 executable checks 符合既有 schema：`.ai/assets` manifests 必須宣告 canonical source_of_truth，workflow.step 必須是整數，不能把 boolean true 當成 1。這是增強現有規範的執行，沒有創造新的角色權限。

### 修改範圍

- `.ai/scripts/artifact_authoring.py`：role adapter、catalog、preview 相依。
- `.ai/scripts/validate-ai-context.py`：共用 canonical manifest／角色關係檢查與兩項型別／authority 修正。
- `.ai/scripts/tests/test_artifact_authoring.py` 與 `tests/fixtures/role-migration/`：歷史 oracle、更新、拒絕、延伸欄位、私有角色、stale preview、復原、portable CLI。
- `.ai/scripts/tests/test_ai_context_sub_agent_adapters.py`：修正既有過時診斷文字斷言，保留 dangling-path 與空結果要求。
- `.ai/scripts/tests/test_ai_context_package_smoke.py`：確認新增 runtime 相依存在 archive。
- `.ai/scripts/validation-profile-registry.sh`、`check-all.sh`、`README.md`：相依閉包、顯示名稱同步與使用說明；gate ID 維持不變。

## Validation

已執行完整 authoring 35 cases，35 通過；新增兩項強化後，重跑受影響角色 subset 12 cases，12 通過。這兩組有重疊，不累加成 47 個不同測試。既有 adapter/owner 與 registry 合併命令 42 cases（31+11）通過。最新完整 canonical validator 通過，涵蓋 39 canonical manifests。實際命令、duration、原始輸出 hash 與輸入檔案 hash 已記錄，獨立審查會核對固定版本。

歷史：fixture 目錄第一次建立因 Windows 權限拒絕，首次角色命令 11 cases 中 10 通過、1 因缺少 oracle 檔案而 error；補齊檔案後完成回歸。adapter 首輪 31 cases 中 1 個舊診斷文字斷言失敗；registry 首輪 11 cases 中 runner 顯示名稱未同步而失敗。兩者修正後 42 cases 通過。這些失敗保留，不改稱通過。原始第一次角色命令只有工具回傳，補記摘要會明示非完整 raw log。

固定實作版本 `fb1c310b6629eece95d9d0bb51da8ef23a1f1e20` 已完成獨立審查與 portable package smoke；實際命令 exit 0，counts={"tests_run": 1, "successful_test_cases": 1, "failures": 0, "errors": 0, "skipped": 0}，實測 1.791 秒。另在同一固定版本，對 repository 真實的 semantic-governance-analyst 執行唯讀 role.update preview 成功，只有預期的一個角色路徑；未 apply。測試內使用 disposable fixtures；沒有對現行 repository 的角色資料執行 migration，也不代表實際 runtime invocation、release、downstream adoption 或 hosted CI。未量測 token／總工時節省。

## Finding Resolution Matrix

| Assessment Finding | Status | 本批貢獻與剩餘工作 |
| --- | --- | --- |
| ASM-20260921-18-gav#AIC-001 | partially-resolved | catalog 新增一個 family 的 readable／migration-input／writable／admissible 區分；未完成所有 schema 的 coverage registry。 |
| ASM-20260921-18-gav#AIC-002 | partially-resolved | 現有動態角色可用專用工具更新；creation、promoted adapters、其他文件仍待後續 P3。 |
| ASM-20260921-18-gav#AIC-003 | partially-resolved | 一條有歷史依據的明示 edge 已實作，原始 bytes 保留；其他 family 不推定可自動遷移。 |
| ASM-20260921-18-gav#AIC-004 | partially-resolved | 角色 nested extension 保留並有獨立測試；未知欄位策略仍由各 family 擁有。 |
| ASM-20260921-18-gav#AIC-005 | deferred | P4 才依替代覆蓋證據評估減測；目前沒有刪除依據。 |

所有列沿用 baseline 的 stable IDs；本批沒有聲稱完全解決全體 inventory。實作與驗證 commit 由 workflow Git 歷史記錄。

## Verification Assessment Reconciliation

獨立結論保留於 [ASM-20260922-07-0n1](../../../assessments/ASM-20260922-07-0n1/report.md)。審查者只讀固定版本並執行限定 package smoke，沒有修復實作。root 接受其結果後才釋放 snapshot lease。原始 dispatch、candidate、receipt、terminal message、review body、失敗與成功的 focused logs 都由 archive catalog 逐檔綁定，未改寫原始位元組。本文仍是實作者說明，不代替 reviewer 結論。

[六項驗收對照](../evidence/acceptance-report.md) 記錄各條件的選定證據。較早 focused runner 的 hash 取樣於命令完成時；中途只有輸出摘要格式調整，因此不把該欄位當成早期 pinned runner 身份證明。35-case 結果是先前 dirty-worktree 執行紀錄；最終受影響的 12-case、42-case 與 canonical 檢查有各自輸入 bytes 紀錄。固定 commit 上新執行的命令只有明列的 package smoke。

## Deferred Work

Owner 為 repository owner；後續由 ai-context-governance 執行。下一個 P3 批次可選另一個 editable metadata/catalog family，先確定真正的 owner 與版本 edge。角色 creation／promoted adapter 需協調 owner binding 和 runtime metadata，另行界定。AIC-005 保留至 P4；在 replacement coverage 未成立前保留驗證器與 behavioral tests。

## Closure Evidence

ROLE-001 與 ROLE-002 已完成選定實作、驗證及證據交付。owner 已授權本機合併；採 --no-ff，保留 implementation freeze 與獨立審查／evidence-intake 兩個有意義的 checkpoint，作為一個可回溯的交付單元。最終交付 commit 另做 evidence-intake delta 審查與 current-subject binding；不重跑未變動的 behavioral tests。Issue 318 維持 open；沒有 push、PR、Issue/Project closure 或 release。最終合併與 current-subject binding 必須由完成時的 live read-back 證明。
