# Artifact 共用核心 P2 說明報告

## Report Metadata

- `report_id`: `remediation-report-2026-09-21-artifact-shared-core`
- `workflow_id`: `2026-09-21-artifact-shared-core`
- `owner_skill`: `ai-context-governance`
- `status`: `final`
- `created_at`: `2026-09-21T22:46:54+08:00`
- `updated_at`: `2026-09-21T23:14:33+08:00`
- `template_source`: `.ai/assets/skills/ai-context-governance/templates/ai-context-remediation-report-template.md`
- `template_version`: `2.0.1`
- `baseline_assessment`: `ASM-20260921-18-gav`
- `verification_assessment`: `ASM-20260921-23-qsn`

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

放寬的是 P1 對**合法 scalar 內 `#` 字元**的過度拒絕。P1 實際遇到的 `Issue #316` 可以由 writer 建立後再次更新／定稿，不需人工修正 metadata。本次含 `Issue #317` 的 verification assessment 也已由 writer 建立與定稿，並確認 reviewer 正文完整保留。

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
| 完整 producer 與獨立驗證 | 固定實作版本 `b808533b` 上執行完整 execution-artifact 與 package-smoke command：{"errors": 0, "failures": 0, "skipped": 0, "successful_test_cases": 27, "tests_run": 27}，exit 0，實測 96.499 秒；獨立審查未提出需修復的發現。 |

保留準備失敗：第一次新增 malformed-YAML fixture 把合法 block scalar 內容誤當語法錯誤；修正 fixture 縮排後，五項相容性測試通過。沒有為了該案例放寬 parser。最初 sandbox 的遠端 main 讀取遇到 proxy 連線失敗，改用已授權的讀取權限後通過；這不是 CI 失敗。外部驗證首次準備因治理 skill 未綁定 mechanical role 而拒絕，尚未派發行為；改由正式 auditor 綁定執行原已規劃的獨立驗證。派發文字另有一個 authority hash 抄寫錯誤，在行為前更正，正式產生的 dispatch／packet 未改動。兩者不計為測試失敗或重跑。其後第一次實際命令因預設暫存目錄 WinError 5 受阻：11 cases 中 9 成功、2 case errors，另有 1 class setup error，16 methods 未執行；記錄為 blocked-by-environment。確認較高權限的暫存目錄建立／讀寫／清理 probe 通過後，才在相同 commit 與命令執行第二次，沒有改程式或測試。失敗紀錄與成功結果分開保存。

## Finding Resolution Matrix

| Baseline finding | Status | 本階段與剩餘範圍 |
| --- | --- | --- |
| ASM-20260921-18-gav#AIC-001 | partially-resolved | 兩套 producer 共用核心與綁定；全庫 coverage registry 與其他 family 尚未納入。 |
| ASM-20260921-18-gav#AIC-002 | partially-resolved | P1 多檔工具維持，並改善合法 hash 字串的更新；所有正文與完整文件種類仍不是自動撰寫。 |
| ASM-20260921-18-gav#AIC-003 | deferred | 新 migration edges 屬 P3；既有 migration 行為仍須相容。 |
| ASM-20260921-18-gav#AIC-004 | partially-resolved | 明確保留兩套 parser 的不同規則，沒有強制全庫採同一 unknown-field／serialization 政策。 |
| ASM-20260921-18-gav#AIC-005 | deferred | 本階段沒有刪除測試或 validator，也沒有宣稱 token／耗時節省比例。 |

## Verification Assessment Reconciliation

獨立審查見 [ASM-20260921-23-qsn](../../../assessments/ASM-20260921-23-qsn/report.md)。審查者在固定版本 `b808533b71cb257fdfdd741b0dafe5c3b703178e` 執行限定測試與兩階段唯讀分析，沒有修復實作；root 接受其結果，原始 candidate、receipt、dispatch、report 與釋放的 lease 分別保留並校驗 hash。本文仍是實作者說明，獨立結論保留在該 assessment。

[七項 acceptance 對照](../evidence/acceptance-report.md) 與 machine ledger 分項記錄結果和 digest。AC6 的 actual-execution 指真實執行 unittest 命令；測試內部 disposable fixtures 仍為 synthetic，不代表實際 release／upgrade。測試數量有重疊，沒有把先前五項 subset 再累加成額外完整測試。

## Deferred Work

Maintainer 下一階段可依 P3 逐一選取其他 editable metadata／catalog 與明確 migration edge，逐 family 證明 unknown-field 與 reader 行為。P4 必須建立替代 coverage 對照才刪減測試或驗證。效能、token 節省及全庫資料遷移尚未量測／執行。

## Closure Evidence

P2 本機實作與選定驗證已完成，workflow-owned tasks 均已完成。本機整合採 `--no-ff`，保留固定實作與獨立驗證／證據交付兩個有意義的階段；合併身份由 Git 歷史與本次交付 read-back 記錄。Issue 317 保持 open；本機合併授權不包含 remote push、Issue／Project closure、release 或下游採用。

完整測試和第一次獨立審查的執行主體仍是 `b808533b`；交付紀錄新增後會在乾淨的交付 commit 重查其內容與目前 review binding，不把先前測試改稱在後續 commit 重跑。Hosted CI、完整 release/history matrix、token 與整體效能量測未執行。
