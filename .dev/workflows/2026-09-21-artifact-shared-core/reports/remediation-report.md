# Artifact 共用核心 P2 說明報告

## Report Metadata

- `report_id`: `remediation-report-2026-09-21-artifact-shared-core`
- `workflow_id`: `2026-09-21-artifact-shared-core`
- `owner_skill`: `ai-context-governance`
- `status`: `draft`
- `created_at`: `2026-09-21T22:46:54+08:00`
- `updated_at`: `2026-09-21T22:49:47+08:00`
- `template_source`: `.ai/assets/skills/ai-context-governance/templates/ai-context-remediation-report-template.md`
- `template_version`: `2.0.1`
- `baseline_assessment`: `ASM-20260921-18-gav`
- `verification_assessment`: `pending independent verification`

## Remediation Summary

本階段依你接受 P1 後的授權，執行 [Issue 317](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/317) 的 P2：共用機械處理核心，接入既有 workflow／assessment authoring 與 execution-artifact producer。原 P1 已在本機合併為 `9b07d22f`，合併後 tree 與交付版本相同。本次依明確授權採本機分支合併；未執行 hosted CI，也沒有將預期的 CI 問題寫成已發生的失敗。

兩套 parser 的既有行為不同：authoring 先解析 JSON 且限制 JSON-compatible 值；execution 維持 YAML 解析、schema anchor／merge 與既有 scalar 規則。直接換成同一 parser 會改變日期、科學記號、alias／tag 等行為。因此只抽出已確認重複的機械處理，保留各自的語意邊界。

## Changes And Evidence

| 項目 | 改變與效果 |
| --- | --- |
| 共用核心 | 新增 `artifact_core.py`，集中字串 key／duplicate-key mapping 建構、canonical JSON、SHA-256 與 YAML token／註解辨識。 |
| 既有 producer 接入 | 兩個原有模組保留 public API，內部委派給共用核心；`execution-artifacts.py` 及 `artifact-authoring.py` 的 CLI 介面不變。 |
| YAML 可用性 | 以 token 範圍區分內容與註解，合法 quoted／plain／block scalar 裡的 `#` 可以更新，真正註解仍拒絕；block scalar 標頭註解另外檢查。 |
| 變更偵測 | 新模組加入 authoring preview 的輸入與 runtime 綁定，以及 execution authority manifest；核心變更使舊證據失效。 |
| 套件與測試 | 沿用既有 package script 包含規則與 gate 身分；補上來源及隔離 payload 匯入、固定 bytes、兩套 parser 差異與變更失效的證據。 |

另外補齊既有 synthetic packaging fixture 遺漏的三個 helper，並讓 package smoke 明確確認它們進入兩種 archive；不把既有 fixture 缺口宣稱為實際發佈包缺陷。

Execution 原有有限 schema walker 沒有與 authoring 重複，因此保留在既有 owner；版本處理、不可變性、狀態轉移、receipt/custody 與復原規則也維持原處。此階段沒有建立全庫通用 JSON Schema 引擎。

## Rules Retained And Relaxed

放寬的是 P1 對**合法 scalar 內 `#` 字元**的過度拒絕。P1 實際遇到的 `Issue #316` 可以由 writer 建立後再次更新／定稿，不需人工修正 metadata。

沒有放寬真正 YAML 註解的保護、duplicate／non-string key 拒絕、authoring alias／anchor／explicit-tag 限制、未知版本拒絕、時間遞增、ID／subject／final conclusions 不可變、execution 失敗結果保存或 receipt 驗證。每個 family 仍保留原本接受的語法；沒有更動全域 PyYAML loader。

既有 validator、測試及 required gate 均保留。YAML 仍會重新排版，資料值保留不代表原始格式無損；有真正註解時仍需既有受審查的手動編輯流程。

## Validation

| 檢查 | 目前結果 |
| --- | --- |
| Authoring regression | 24 tests passed，40.528 秒，無 skip；含兩種文件的 quoted-hash 更新／定稿、真正註解拒絕、preview dependency drift 與 P1 原有案例。 |
| 共用核心相容性 | 5 tests passed；涵蓋手寫 canonical bytes oracle、parser 差異、錯誤邊界、LF／CRLF、Unicode、block／flow 與實際註解。 |
| Execution structure／package | 5 tests passed；隔離 Python payload 可執行既有 CLI，移除核心後確實無法匯入，避免借用來源目錄。 |
| Generated templates | `execution-artifacts.py templates --check` passed；沒有重寫 generated template。 |
| 相依 contract／註冊 | Guardrails 46 tests、external-task 35 tests、entrypoint 7 tests、profile registry 11 tests 通過；AI context、guardrail contract、shell assets 通過。 |
| 完整 producer 與獨立驗證 | 尚待固定 commit 後的外部測試與獨立審查。 |

保留準備失敗：第一次新增 malformed-YAML fixture 把合法 block scalar 內容誤當語法錯誤；修正 fixture 縮排後，五項相容性測試通過。沒有為了該案例放寬 parser。最初 sandbox 的遠端 main 讀取遇到 proxy 連線失敗，改用已授權的讀取權限後通過；這不是 CI 失敗。

## Finding Resolution Matrix

| Baseline finding | Status | 本階段與剩餘範圍 |
| --- | --- | --- |
| ASM-20260921-18-gav#AIC-001 | partially-resolved | 兩個 producer family 共用核心與綁定；全庫 coverage registry 與其他 family 尚未納入。 |
| ASM-20260921-18-gav#AIC-002 | partially-resolved | P1 多檔工具維持，並改善合法 hash 字串的更新；所有正文與完整文件種類仍不是自動撰寫。 |
| ASM-20260921-18-gav#AIC-003 | deferred | 新 migration edges 屬 P3；既有 migration 行為仍須相容。 |
| ASM-20260921-18-gav#AIC-004 | partially-resolved | 明確保留兩套 parser 的不同規則，沒有強制全庫採同一 unknown-field／serialization 政策。 |
| ASM-20260921-18-gav#AIC-005 | deferred | 本階段沒有刪除測試或 validator，也沒有宣稱 token／耗時節省比例。 |

## Verification Assessment Reconciliation

待獨立 auditor 檢查固定版本。本報告是實作者紀錄，不代替獨立結論。

## Deferred Work

Maintainer 下一階段可依 P3 逐一選取其他 editable metadata／catalog 與明確 migration edge，逐 family 證明 unknown-field 與 reader 行為。P4 必須建立替代 coverage 對照才刪減測試或驗證。效能、token 節省及全庫資料遷移尚未量測／執行。

## Closure Evidence

目前仍為 P2 執行中。Issue 317 保持 open；本機合併授權不包含 remote push、Issue／Project closure、release 或下游採用。
