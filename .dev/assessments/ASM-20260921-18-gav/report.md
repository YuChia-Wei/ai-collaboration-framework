# 結構化文件撰寫、遷移與驗證整併深度分析

## Metadata

- `assessment_id`: `ASM-20260921-18-gav`
- `assessment_type`: `ai-context-audit`
- `owner_skill`: `ai-context-auditor`
- `status`: `final`
- `created_at`: `2026-09-21T18:46:34+08:00`
- `updated_at`: `2026-09-21T19:03:58+08:00`
- `template_source`: `.ai/assets/skills/ai-context-auditor/templates/ai-context-audit-report-template.md`
- `template_version`: `2.2.0`
- `subject_commit`: `8830cdfc252b8845efcbe6cce539041c17cf8e7a`
- `workflow_refs`: `.dev/workflows/2026-09-21-schema-artifact-lifecycle/workflow.yaml`
- `repository`: `YuChia-Wei/ai-collaboration-framework`
- `subject_branch`: `main`
- `artifact_branch`: `codex/2026-09-21-schema-artifact-lifecycle`
- `previous_assessment`: 前一輪對話中的暫態分析，不追認為正式 assessment。

## Executive Summary

**建議推進，先以 workflow／assessment 撰寫器作為第一個擴充範圍，再逐類納入其他文件。** 共用結構模型、版本路由及診斷可以集中維護；文件語意、實際執行證據、交易恢復及授權仍由各家族擁有者負責。

目標是讓 AI 或維護者只提供必要內容，工具可靠地建立與更新一組相關文件，在寫入前攔截格式與關聯錯誤，並明確處理版本演進。只新增空白模板產生器，不能完整解決這個問題。

本次選擇**先交付報告，不直接實作全庫工具或刪除驗證器**。使用者已允許在總時間與 token 成本較低時直接實作；目前發現 schema 方言與權威來源不一致、文件可變性與遷移策略不同，且尚未建立可刪除個別測試的同契約證明。此時廣泛重構較容易重工。這是工程取捨，不是已量測到的效能結論，也不是缺少分析授權。

- Overall assessment：可行，有既有基礎，適合漸進導入。
- Overall score：N/A，沒有足以量化全庫成熟度的統一分母。
- Decision：`remediation-recommended`，指改善機會，不宣告現行整體系統失效。
- 本次實際變更：分析報告、證據、workflow 與索引。
- 本次放寬規範、移除 validator／測試、改變執行或發布行為：**均為零**。
- 下列設計與規則處置都是提案，尚未成為新的執行規範。

## Scope

包含固定來源中的 `.ai` schema、模板、framework 工具與契約測試，以及 `.dev` 現行標準、需求／規格／problem-frame 指南和選定近期 Issue 證據。完整列出明確 path selector 選中的 schema，再追查 Markdown、模板與程式中的隱含契約。

排除產品 `src/**`、`tests/**`、`test/**`，不相關歷史 workflow／assessment，秘密與個人 local routing 值，以及真實升級、release／provider mutation。`.ai/scripts/tests` 僅作靜態契約盤點。未要求產品程式碼審查；本報告不提供所有程式分支正確性或安全稽核結論。

## Methodology And Evidence

### Pass A: Independent Baseline

先依一般工程原則區分結構、語意、事實、授權與副作用，再評估單一來源、作者負擔、更新完整性、相容性及恢復。Writer 可以保證它建立的表示法，無法單憑表示法證明外部事件已發生。

### Pass B: Repository-Aware Review

對照 workflow／assessment／版本／provenance／execution custody 契約。補充了 receipt 不可轉換、journal v4 不可復原轉換、canonical metadata 允許延伸欄位，以及 aggregate gate／provider admission 的獨立責任。

| 證據 | 用途與限制 |
| --- | --- |
| [來源盤點 JSON](evidence/source-inventory.json) | 33 份 YAML schema、1 份歷史 JSON schema、47 個選定模板路徑、4 個測試檔的 AST 方法清單；包含來源 SHA／blob／hash。 |
| [能力矩陣](evidence/capability-matrix.md) | 33 個顯式 schema 與 19 組隱含／外部契約的能力、未知項目及建議處理方式。 |
| [盤點重現程式](evidence/collect-inventory.py) | Assessment 專用唯讀證據工具；從固定 Git commit 讀取，不是正式文件 writer。 |
| [近期 Issue 快照](evidence/recent-issues.json) | 有查詢時間的 GitHub read-back；日後現況需重新確認。 |
| [Workflow](../../workflows/2026-09-21-schema-artifact-lifecycle/workflow-plan.md) | 授權、進度、失敗修正及接續動作。 |

### Delegation And Discovery Accelerators

三個 bounded-routine-worker invocation 蒐集支援證據，另由一個普通 explorer 有界補查。Parent 為唯一 tracked writer 與整合者。初始 mechanical role routing 缺精確路徑，補正後又發現 auditor 沒有該靜態 role binding；準備問題保留在 workflow，未宣稱有效 canonical-role invocation 或 independent review。普通 explorer 依 skill-owned bounded analysis 補足缺口，重要結論由固定來源盤點與 parent 檔案調和支援。

Codebase graph 的 project 存在，但 indexed_at／commit_sha／coverage 無可用值，部分已存在工具搜尋不到。因此以固定 SHA 的 `git ls-tree`／`git show`、明確路徑查詢及直接檔案作 fallback。不存在搜尋命中不作為不存在功能的證據。來源盤點 JSON 明列生成時間、selector 與排除項目；完整性僅對這些 selector 成立。

## Repository Context Inventory

| 顯式 schema 家族 | YAML 檔數 | 特性 |
| --- | ---: | --- |
| Shared 執行／驗證／provider registry | 6 | 同檔可能有 packet、lease、ledger、retry、review-input 等記錄。 |
| Skill-owned init／governance／upgrade／delegation | 12 | 設定、有效規則、交易、決策與執行產物權威不同。 |
| .NET example／provider contract | 2 | Example、provider contract 與實際執行證據需分開。 |
| Distribution | 7 | 已有 builder／planner／parser，含舊版 reader 與發布不可變性。 |
| Evaluation | 4 | Manifest 可以撰寫；結果需來自觀測或明確標示的 fixture。 |
| Development governance | 2 | 歷史 provider receipt 與 source rule evidence。 |
| 合計 | 33 | 2 份明示 JSON Schema 2020-12；其餘使用專案描述格式，部分內嵌受限結構模型。 |

另有 1 份歷史 workflow JSON schema，不因此新增維護或遷移義務。完整逐檔表見矩陣 E01–E33。

Workflow／assessment 的重要限制在政策與 Python validator；skill／sub-agent 欄位在 `CANONICAL-SCHEMA.MD`；requirement／spec 模板嵌在指南；plan／journal／receipt 版本在 producer 與契約。另有 routing、ownership、tooling registry 及 GitHub Actions 等外部格式。矩陣 I01–I19 將這些另行列出。

47 個選定模板路徑含歷史 audit workflow 模板與 public-root 檔案，**不代表 47 種現行 schema**。`command-spec`／`prompt-package` 有建立模板，但 canonical schema 明確表示尚未成為 active manifest families。正式 registry 要記錄狀態與覆蓋證據，不能只列檔名。

版本身分也不能混用：

- `selected-inputs.schema.yaml` 的定義欄位是 1.0，內含 `package-selected-input/v1`／`v2`，另有 `release-package-input/v1`。
- Source identity registry 1.1 與 package identity metadata 1.1.0 是不同記錄，不是版本衝突。
- Provenance artifact 2.0、template 2.1.0、plan 2.2.0、journal v5 是不同契約。
- Release 模板頂層 schema_version 是 placeholder，所檢查的 release validation 函式未建立可推導全部支援版本的 discriminator；phase checks 1.0、provider reconciliation 1.0／1.1 須分別辨識。

未來 registry 應分辨 kind、artifact version、契約來源／方言、template version、writer 版本及 reader／migration 路徑，不強迫所有檔案使用同一版本欄位。

## Recent Work Reconciliation

| Issue | 本次 live read-back | 已完成範圍與本需求關係 |
| --- | --- | --- |
| [#310](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/310) | CLOSED | 分離 completion candidate、validation receipt、交付放行；格式轉換不能授予新驗證事實。 |
| [#312](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/312) | CLOSED | 共用 record_models／walker、生成模板、prepare／finalize／check／migrate；原 Issue 明確排除全庫 schema 改寫。 |
| [#313](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/313) | CLOSED | 依實際風險簡化程序，保留授權、證據及整合檢查。 |
| [#307](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/307) | OPEN | Pre-tag execution reuse 為獨立議題，不因 writer 設計而完成。 |
| [#308](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/308) | OPEN | Validation input planning／unsupported diagnostics 為相鄰範圍，未納入實作。 |

現有 `prepare` 觀測 Git 身分；`finalize` 接受 caller 的實際觀測，但不執行委派命令，也不能獨立證明 caller 陳述的全部事件。Migration 僅支援 dispatch／completion 1.2→1.3；receipt 永不由 migration 產生，lease／retry／ledger 未涵蓋。

前次最終交付記錄：指定四個測試檔刪掉 3 個重複方法，之後補上 4 個缺少的邊界，最終 162→159→163。沒有量測到的時間／token 節省。本次另盤點 20 個 execution-artifact、46 個 guardrail、15 個 assessment、35 個 external-task 方法；這是不同選定集合，**不能與 163 相減或相加推導節省量**。

## Strengths

1. #312 已有共用模型與 writer／validator 分工，可延伸而不另建一套 execution framework。
2. Package、provenance、validation evidence 已有專門 producer 與恢復邊界，可由統一入口路由。
3. 既有測試保留手寫輸入、非法路徑、authority drift、failed／blocked 等獨立預期。
4. 現有 validator 能找到實際跨檔不一致；可把部分檢查前移到 writer，同時保留接收端驗證。

## Findings

以下為改善發現，並非全庫缺陷總清單。

| ID | Severity | Finding / evidence | Impact / recommendation / owner |
| --- | --- | --- | --- |
| AIC-001 | MEDIUM | 可執行模型、描述 schema 與 Markdown 契約並存；E01–E33、I01–I19。 | 沒有單一覆蓋分母。Governance 建立 kind／version／owner／lifecycle 表，語意留在原 owner。 |
| AIC-002 | MEDIUM | Workflow／assessment 需同步多檔，目前主要依模板與後置 validator；本次實際有兩個 authoring failure。 | 單檔正確仍可能關聯失敗。優先做 bundle create／transition／finalize。 |
| AIC-003 | MEDIUM | Reader 相容、重新生成、migration、實際重跑意義不同；receipt 及 journal v4 禁止一般轉換。 | 通用 converter 容易誤改證據。各 kind 宣告 disposition 與 unsupported 下一步。 |
| AIC-004 | MEDIUM | Unknown field 規則不同：canonical metadata 允許延伸；release projection 要保留未知欄位。 | 全域嚴格化／寬鬆化都會破壞相容。每模型保留原有欄位、型別及序列化策略。 |
| AIC-005 | LOW | 可找到重複結構 mechanics，但沒有逐案例 same-contract 證明能刪哪些測試。 | 先建立 rule→implementation→test 對照，再刪真正重複的案例。 |

AIC-002 的實際觀測：第一次 assessment 檢查因 `workflow_refs` 填 locator path、而 reader 要 workflow ID 失敗；第一次 workflow 檢查因 index 用簡稱而非完整 title 失敗。修正後兩者通過。這是一次 ad hoc 建立腳本的觀測，不是公平效能基準；它證明 writer 需要處理多檔關聯，尚未量化收益。

## Proposed Architecture

### 操作與模型

以 CLI／可呼叫 API 為優先，不新增 GUI／服務部署。每個 family 提供語意明確的操作：建立 workflow、加 task、移轉 task 狀態、建立 assessment、finalize draft、預覽指定版本 migration。這些是擬議介面，目前未新增正式命令。

呼叫端提供 title、scope、body、接受準則、已知事實與必要決策；工具負責可推導欄位、序列化、關聯、模板來源、受控 index row 與診斷。缺少語意資料要批次列出，不能預設 `passed`／`approved`／`completed` 或虛構時間。Request 格式應比完整輸出簡單，避免只把 YAML 負擔搬家。

| 層 | 責任 | 所保留的權威 |
| --- | --- | --- |
| 入口／覆蓋註冊 | kind、owner、dialect、版本路由、支援操作、external／historical 狀態 | 不重複 family 欄位與行為規則。 |
| 共用基礎 | 嚴格解析、明確型別、結構診斷、序列化、安全輸出、dry-run diff | 不接管 package／transaction／receipt 語意。 |
| Family model／adapter | 唯一欄位模型、語意操作、遷移步驟、保留區域 | 模板是投影，不能反向成為權威。 |
| 現有 validator／producer | 跨檔、Git、authority、receipt、交易、live provider | 舊 CLI 先保留薄入口及已發布命令／gate 身分。 |

不猜測轉譯 31 份自訂格式。先為選定 family 建精確模型，writer 與 structural checker 共用，domain functions 保留。必要時抽取共用模組，避免 writer 依賴龐大 CLI 的 `main()`。沿用 Python／PyYAML；目前沒有證據支持新增框架或換語言能降低成本。

若後續超過 #312 的受限方言，明確選擇擴充或標準 JSON Schema validator，並證明 exact-type、duplicate-key、未知 keyword 等行為。不能把受限 walker 宣稱為完整 JSON Schema。

### 多檔更新與人類內容

Workflow create 協調 locator、plan、初始 tasks、index；assessment create 協調 locator、report、正確 lifecycle section 的 index row。更新只觸碰受控欄位／區段與對應 row，保留自由文字及其他記錄。

建立前檢查 ID 碰撞；更新保留身分／created_at，確認版本與預期 bytes 未漂移，驗證整組候選關聯後才寫入。多檔案個別 rename 不等於跨檔 crash-atomic；應定義有界復原或半成品拒絕行為，再測失敗後留下的 bytes。不把 package-apply 全套 journal 強加到一般文件編輯。

Markdown schema 可約束 metadata、章節、連結與 ID，不能證明需求完整、設計正確或翻譯等價。第一階段管理 machine-owned metadata／受控投影；正文由 authoring skill／維護者撰寫。Final assessment 不重寫結論，採 addendum／successor 或合法 locator 關係更新。

## Migration Policy Proposal

| 類別 | 例子 | 正確處理與限制 |
| --- | --- | --- |
| Editable source | Draft workflow／assessment、選定設定 | 明確 from→to route、預覽、必要新輸入、保留原件；不推導 owner decision。 |
| Derived output | Wrapper、package inventory、effective-rule candidate | 從權威來源重新生成；candidate 不自動採認，generated output 不成第二個來源。 |
| Sealed evidence | Receipt、validation result、final report | 保留原件；需要新版證據時實際重跑／驗證；migration 不製造成功或授權。 |
| Transaction state | Journal、progress、sealed plan | 僅走原 owner 支援的 resume／recovery；v4 不轉 v5，保留拒絕與 recovery 指引。 |
| Historical／example | 舊 workflow schema、歷史模板、example | 宣告 read-only／historical／example；不全庫 backfill，不提升為 acceptance。 |
| Externally owned | GitHub／runtime 格式 | 登錄 delegated validation／authoring；不建立競爭的本地標準。 |

`readable`、`writable`、`migratable`、`admissible` 分開宣告。Writer 寫 current supported version；reader 按承諾範圍相容；migrator 只走已測試路徑，不承諾任意版本兩兩轉換。刪除舊 CLI／reader 另作相容性與棄用決策。

## Rule Dispositions

以下全部是提案。本次沒有放寬任何執行中的規範。

| ID | 規則／工作方式 | 建議處置 | 改善與保留條件 |
| --- | --- | --- | --- |
| R01 | 人工維護衍生欄位、模板來源、index、可觀測身分 | 工具接手 | 降低修復；觀測失敗不補假值。 |
| R02 | 多 CLI 重複型別／欄位檢查 | 合併實作 | 同模型與結構引擎；保留 domain semantics、diagnostics 及舊入口。 |
| R03 | 各 family 重複相同結構測試 | 條件式合併 | 證明同規則、輸入域與拒絕邊界；不能只看名字／文字。 |
| R04 | 一般人工文件的空白、鍵順序／呈現限制 | 可評估放寬 | 無 consumer／hash／模板依賴時驗語意等價；canonical bytes、sealed evidence、generated drift 保留。 |
| R05 | 每個 schema 配獨立 executable | 共用入口＋adapter | 減少維護面；每類仍有專用操作。這是需求設計選擇，現行無此全庫強制規則。 |
| R06 | 每個版本都能自動遷移 | 每類宣告 disposition | Convert／regenerate／re-execute／historical／unsupported 明確化；不承諾無法證明的轉換。 |
| R07 | 必填、精確型別、duplicate key、未知版本／keyword | 保留 | 避免 parser 悄悄改變語意。 |
| R08 | Unknown fields | 按原 owner 規則 | Extension、release projection preservation、封閉 execution record 分別處理。 |
| R09 | ID、created_at、assessed subject、final conclusions | 保留 | 工具自動維護，不授權改寫歷史。 |
| R10 | 真實 observations、failed／blocked、receipt custody | 保留 | Writer 成功不等於記錄中的執行成功。 |
| R11 | 授權、role applicability、retry、秘密、target ownership | 保留 | 工具與 schema 不提供行動授權。 |
| R12 | Provider freshness、required context、merge／release admission | 保留 | Writer hash 不能替代 live read-back。 |
| R13 | Aggregate runner／profile gate 身分 | 保留 | 共用實作不等於可刪 gate；改報告／選擇語意須另驗證。 |
| R14 | 普通 authoring 新增完整 packet／lease／審查 | 不新增 | 沿用 #313 實際風險分類；高風險契約變更仍依適用 gate。 |

## Validation And Test Consolidation Design

驗證分為：語法／結構、單文件語意、跨檔／儲存狀態、外部事實／授權。可以共用程式並提前檢查，但接收／採用資料時仍要驗證相應邊界。

| 目前能力 | 可共享部分 | Distinct boundary |
| --- | --- | --- |
| execution_artifact_contract | Strict mapping、受限 walker、version dispatch | 不是完整 JSON Schema；authority manifest 也不只是格式。 |
| External-task validator | 結構與 parsing primitive | Cross-record／raw bytes、路徑、single envelope、exclusive receipt。 |
| Guardrails | Packet structure | Lease/live Git、ledger receipt、retry、review input、graph freshness。 |
| Workflow validator | Locator/task 欄位模型 | Skill task contracts、approval/test evidence、生命週期、terminal anchor、index。 |
| Assessment validator | Locator model／時間解析 | ID/hour、report/index/section、successor/workflow 關係、draft resume。 |
| AI-context validator | 選定 metadata 結構 | Canonical owner、wrapper／profile／role routing、語言與跨檔一致性。 |

保留手寫合法／非法資料與獨立 oracle、migration 事實保存、filesystem／關聯／authority 的負向行為。Writer 輸出通過共用 checker 只是一項 integration evidence，兩者可能共享錯誤。

目前沒有足夠證據指定某個現有測試可立即刪除。可先合併 fixture 建構、primitive 重複實作與脆弱錯誤文字斷言；每次移除附接替它的等價 coverage。一般結構案例可參數化，execution／tamper／failed outcome／retry／recovery 留下。

## Proposed Delivery Order And Acceptance

| 階段 | 有界交付 | 完成條件 | 本次狀態 |
| --- | --- | --- | --- |
| P0 | 正式 coverage registry 最小設計 | 每 kind 有 owner、模型來源、reader/writer/migration disposition；不複製語意 | 盤點完成，未建立 production registry。 |
| P1 | Workflow／assessment create 與有限狀態更新 | 解決本次兩個 authoring failure；維持 locator、task、受控 metadata、index | 建議第一個 implementation slice。 |
| P2 | 共用核心與既有 producer 接入 | #312 CLI 相容；source／package import closure 正確 | P1 穩定後逐類接入。 |
| P3 | 其他 editable metadata／catalog、明確 migration edges | 每次一個 family，證明 unknown-field 與 reader 行為 | 分批，不同時全庫重寫。 |
| P4 | 有證據的 checks/tests 整併與 CLI 棄用評估 | Rule→check→test 可追蹤；必要 gate 身分不消失 | 尚未選定刪除案例。 |

P1 建議驗收：

1. 最小輸入建立整組 workflow／assessment，既有 validator 通過，無須手填 index、模板版本、衍生路徑。
2. Workflow ID 關聯正確；非法／缺失關聯一次列出，寫入前拒絕。
3. Title／status／updated_at 只同步對應 index row，不改其他項目。
4. Task transition 維持適用的單一 in-progress 任務及真實 results，不宣告未執行測試通過。
5. ID、created_at、subject、final conclusions 的不可變性有獨立負向測試。
6. 碰撞、未知版本、外部修改、路徑逃逸不覆寫資料，診斷有下一步。
7. 跨檔寫入失敗有明確復原證據，不能只測 happy path。
8. 正文、合法 extension、注釋保留策略明確；無法無損時限制操作範圍並顯示 diff。
9. Dry-run 不變更 tracked 檔；固定輸入的 rendering／projection 可重現。
10. 新 required 欄位、相容 optional 欄位各有一個演進案例與獨立 oracle。
11. 舊 CLI、profile、package import／檔案註冊相容；依實際變更選 package smoke 或長跑檢查。

正式 implementation 前建立／綁定真實 online Issue，記錄 material scope 與 owner 授權／後續選擇；不重新開啟 #312 容納全庫範圍，不預先分配 release。這份 assessment 是已授權分析的結果，不是新的已採納規範。

## Cost And Benefit Measurement

預期收益為較少手動同步、格式修復及重複 checker 維護；沒有宣稱百分比、token 或分鐘節省。用同一來源、主機、固定輸入比較兩組 exercise：建立／更新 workflow，建立 draft assessment／合法 finalize。

記錄人工供給欄位、手動維護檔案、process invocations、format-only failure／repair、elapsed time。要做統計比較時重複相同 exercise 並說明冷／暖條件；token 只用實際 runtime telemetry，未取得就標 unavailable。Migration 另測相容／不相容診斷、原件 hash、狀態保存、unsupported 行為。新工具維護與新增負向測試成本也要計入，測試數／CLI 數不能單獨代表省成本。

## Baseline And Skill Comparison

- Confirmed：共用 model＋family adapter 可行；writer 降低格式負擔，semantics／custody／actual evidence 保留。
- Added：多檔 authoring failure、unknown-field 差異、code-defined journal／receipt、release version 辨識、historical／inactive template 界線。
- Downgraded/deferred：basename 找不到 consumer 不等於無效 schema；YAML 不等於標準 JSON Schema；沒有 migrator 證據不等於不存在。刪測試幅度與效能收益須實作後證明。
- Overturned：CLI routing 只確認 reader／validator，未確認 writer；selected-inputs 支援 v1/v2 及獨立 release projection；command／prompt-package 模板不是已啟用 manifest family。

## Validation

| Check | Result | Evidence / notes |
| --- | --- | --- |
| 初始 Git／live origin main | passed | 皆為 8830cdfc，工作樹乾淨；branch-first。 |
| 固定來源盤點重現 | passed | 33+1 schemas、47 template paths、4 AST test inventories 與 JSON 一致。 |
| Bootstrap assessment validator | failed → passed | Workflow ref 表示法修正後，65 assessments 通過。 |
| Bootstrap workflow validator | failed → passed | Exact title 修正後，123 post-adoption／143 indexed workflows 通過。 |
| Analysis artifact／source-context checks | passed | Workflow、assessment、AI-context、source work-management、盤點與 15 個 local links 通過；[實際結果](evidence/validation-results.json)。 |
| Commit messages | passed | Bootstrap 與 final 的完整 planned message 均先驗證；commit range 於 Git 交付時另行驗證，不充作受評 source 的行為證據。 |
| Independent behavioral review | not-applicable | 本次分析文件不是 implementation 或 merge admission；未宣稱該 gate。 |

Skipped：product unit／integration／E2E、full package／release／history matrix、真實 upgrade／provider mutation。沒有修改這些實作或宣稱其新行為通過；靜態盤點不算 execution evidence。

## Deferred Items

- Owner：repository maintainer。閱讀報告選定 P1 後，建立真實 work-item binding 進入 implementation stage。
- Production registry／writer API 尚未實作；能力矩陣僅為 assessment evidence。
- 未確認的 producer／schema-loading route，於該 family 納入前補完；unknown 不轉成 passed 或不存在。
- #307／#308 保留原 Issue 邊界；不處理 #309 credentials、release／tag、provider closeout 或下游採用。

## Appendix

主要來源：

- [Execution artifact 工具契約](../../../.ai/scripts/README.md#execution-artifacts)
- [Canonical metadata](../../../.ai/assets/CANONICAL-SCHEMA.MD)
- [Workflow policy](../../../.dev/standards/WORKFLOW-ARTIFACT-POLICY.md)
- [Assessment policy](../../../.dev/standards/ASSESSMENT-ARTIFACT-POLICY.md)
- [Provenance／journal 邊界](../../../.ai/assets/skills/ai-context-upgrader/references/provenance-contract.md)
- [前次最終驗收](../../../.dev/workflows/2026-09-20-proportionate-terminal-artifact-tooling/reports/remediation-report.md#final-local-acceptance)

```text
python -B .dev/assessments/ASM-20260921-18-gav/evidence/collect-inventory.py --check .dev/assessments/ASM-20260921-18-gav/evidence/source-inventory.json
python -B .ai/scripts/validate-assessment-artifacts.py
python -B .ai/scripts/validate-workflow-artifacts.py
git diff --check
python -B .ai/scripts/validate-git-commits.py --range main..HEAD --workflow-id 2026-09-21-schema-artifact-lifecycle
```

## Lifecycle Handoff

- Assessment：`.dev/assessments/ASM-20260921-18-gav/report.md`。
- Findings：`ASM-20260921-18-gav#AIC-001` 至 `#AIC-005`。
- Analysis owner：`ai-context-auditor`；workflow／後續 remediation owner：`ai-context-governance`。
- 本次採 analysis-first；assessment 為 final，workflow 僅完成分析範圍。未修改 production schema、validator、tool 或 policy，未移除任何測試。
- 下一步可由 P1 操作與驗收條件直接建立 implementation Issue／workflow，無須重做同一盤點；開始前刷新來源 drift 與 Issue 現況。
