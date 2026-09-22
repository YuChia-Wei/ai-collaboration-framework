# P3／P4：文件生命週期工具與驗證整理

## Report Metadata

- `report_id`: `remediation-report-2026-09-22-artifact-lifecycle-completion`
- `workflow_id`: `2026-09-22-artifact-lifecycle-completion`
- `owner_skill`: `ai-context-governance`
- `status`: `draft`
- `created_at`: `2026-09-22T09:29:30+08:00`
- `updated_at`: `2026-09-22T09:36:32+08:00`
- `template_source`: `.ai/assets/skills/ai-context-governance/templates/ai-context-remediation-report-template.md`
- `template_version`: `2.0.1`
- `baseline_assessment`: `ASM-20260921-18-gav`
- `verification_assessment`: `pending independent verification`

## Remediation Summary

本次接續已合併的 P1 workflow／assessment 撰寫器、P2 共用機制及第一批 P3 動態角色操作，完成核准範圍內其餘 P3 選定目錄介面與 P4 驗證整理評估。[Issue #319](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/319) 記錄此次工作。原始盤點的 33 份具名 schema 與 19 組隱含契約，現在分成 91 種記錄並有可檢查的生命週期路由（52 executable、18 semantic-owner、16 manual-gap、4 external、1 creation-template）；一份 schema 內的 packet、lease、request、receipt 等不同記錄分開列出。

結論仍是：每種記錄應有明確的撰寫與遷移處置，但不是每種都能自動生成或轉換。此次增加實際可用的限定編修操作，登錄既有 package／transaction／evidence producers，並留下仍需專屬工具的缺口。路由登錄不代表已完成所有文件的自動撰寫器。

## Changes And Evidence

### 專用操作與改善

所有新操作共用 `artifact-authoring.py` 的 `catalog`、`preview`、`apply`、`recover`。呼叫者選 artifact ID 與語意欄位；工具決定路徑、產生候選內容，先交給該家族的既有檢查，再綁定 preview digest。apply 重算全部讀取依據，攔截來源、schema、runtime、目錄成員、Git 或 request 漂移。原始 bytes 留在 ignored journal；中斷後只允許精確復原未被外部更動的 candidate。多檔寫入仍是可復原 bundle，沒有宣稱跨檔原子交易。

| 操作 | 本次可編修範圍 | 保留的界線 |
| --- | --- | --- |
| `catalog.update` provider 三目錄 | capability tags、deferred reason、stop/escalation | 不改 role identity、owner binding、native profile、availability 或 invocation facts。 |
| `catalog.update` evaluation 兩目錄 | 既有 case 的 input／expected 參照；mutant follow_up | 保留獨立預期資料；靜態檢查不執行 corpus，也不產生 evaluation result。 |
| `catalog.update` source 三 selector | 身分 display_name；既有 YAML／text consumer 路徑／selector；分發處置 patterns／reason | identity schema 1.1 與 disposition 1.0 分開；不改 canonical identity、compatibility、classification、ownership、retention。 |
| `catalog.update` governance terms | qualified term、owner anchor、contextual shorthand | 保留 term ID、namespace、owner path 與 machine literals；檢查不能代替語意審查。 |
| `catalog.update` shell assets | 既有 script lifecycle／replacement | Git executable mode、runner exact coverage、required entrypoint 可執行狀態不放寬；不執行腳本。 |
| `skill.update` | 既有 skill 的 inputs／outputs／constraints／triggers／handoff_rules／runtime_notes | 一般 thin wrapper 保留原 bytes；兩個既有 generated pilot 同步重產 Codex／Claude wrapper，可額外更新 title／purpose。identity、routing、references 與 runtime authority 受保護。 |
| `target.technology`／`target.work-binding` | 既有 project-config 的 explicit selection 與 binding 選擇 | 不初始化或推定 target facts；required owner input 不等於已證明 approval。保留 target extensions 與其他 bounded contexts 的選擇。 |
| `lifecycle.update` | 既有 kind 的路由、版本說明與處置 | kind、baseline identity 與 coverage 受保護；callable 存在不代表實際執行或語意正確。 |

分發處置的 coverage 使用 preview 開始時固定的 **committed source**（包含其 profile 與檔案清單）；候選處置是記憶體 overlay。這不是未提交工作樹的完整 package 驗證。計畫另綁定該 source commit/tree，完成 preview 時 HEAD 不一致即拒絕。

生命週期清單以 `models`、`owner`、`producers`、`validators`、`readable`、`writable`、`migration`、`admissible` 明列責任。具名 schema 新增而未登錄會使 source 檢查失敗；隱含契約則仍需維護明示 inventory。producer 必須指向存在的 Python callable 宣告。這只是路由完整性，不能證明函式的語意覆蓋；`manual-gap` 不會被算成 executable。

### 遷移與未知欄位

目前有證據的自動版本轉換仍只有既有 dynamic role 1.0 → 1.1，以及 external dispatch／completion 1.2 → 1.3。其他家族逐項標明 regenerate、re-execute、preserve、unsupported、owner-recovery 或 owner-reconciliation。receipt 不轉換；journal v4 不改成 v5；歷史 final assessment 不覆寫；外部 provider 格式不建立第二份本地 authority。

各家族維持原 unknown-field policy：允許 extension 的 target、skill 等保留巢狀值；closed catalog 拒絕未知欄位，不默默刪除。YAML comments、alias、tag、重複 key 仍拒絕，以免 serializer 遺失原意。格式正規化與值保留是不同保證；原始 bytes 由 recovery journal 保存。

### P4 規範與檢查調整

唯一放寬的是 **單次編修的檢查範圍**：role／catalog／target／skill／lifecycle 操作不再附帶驗證完全無關的 workflow／assessment 全目錄。這些操作只寫固定且不相交的路徑，仍執行各自的 owner checks。workflow／assessment 操作照舊檢查 linked locator／index 關係。另有負向測試證明，不合法的無關 workflow 不阻擋 catalog preview，但 workflow.create 仍會拒絕。

完整 repository validators、公開 CLI、required gate 與行為測試全部保留。本次沒有刪除既有測試；新增測試是工具邊界，不是再複製每個 schema enum。不能以「writer 和 checker 共用程式」證明兩者獨立正確，因此手寫 oracle、非法輸入、跨檔參照、authority drift、恢復、package import 與實際執行證據仍保留。各項 P4 處置列於 [對照表](../evidence/p4-dispositions.md)。

另外增強既有規範執行：target instance 會先驗證 schema/template authority，再驗證實際選項；Python boolean 不可冒充 project-config integer version。路徑在 resolve 前檢查 symlink/junction；generated wrappers 依既有 LF-normalized source digest 重產。生命週期更新也綁定 model／owner 原始 bytes，不能只靠檔案存在性。

## Validation

已完成的選定檢查如下；原始 log 與執行前輸入 hash 均保留，所有列的 tracked input drift 為空。各列不是同一次全量 suite，也不把重疊案例累加。

| 檢查 | 範圍 | 結果 | 實測時間 | 原始 attempt |
| --- | --- | --- | --- | --- |
| 新 catalog／skill／target／lifecycle operations | 21 cases | passed | 72.099 s | `catalog-03` |
| 最終 optional-profile 與 lifecycle 受影響 subset | 7 cases；其中 6 與前列重疊 | passed | 24.788 s | `routing-01` |
| 既有 workflow／assessment／role authoring | 36 cases | passed | 73.134 s | `authoring-02` |
| validation profile registry | 11 cases | passed | 6.490 s | `contracts-01` |
| 既有 AI behavior evaluation | 18 cases | passed | 3.696 s | `evaluation-01` |
| shell assets CLI | 16 tracked assets | passed | 0.262 s | `shell-01` |
| 完整 canonical context CLI | 39 manifests；91 lifecycle routes | passed | 39.527 s | `canonical-02` |

新 test file 最終有 22 項測試；21-case 執行後只新增 optional profile applicability，最終 7-case subset 驗證受影響路由。21-case 與 7-case 的適用性／輸入差異需要獨立審查核對，不能改稱同一次 22-case 執行。

保留的失敗：`extended-01` 執行 10 cases，9 passed、1 error（首次 apply 建立 ignored recovery 目錄，被過度廣泛的 glob directory observation 判成 stale preview）。修正 literal path traversal 後，`catalog-03` 通過原失敗案例；沒有刪除或改寫失敗記錄。較早 `catalog-01`／`catalog-02`／`authoring-01`／`canonical-01` 是中間版本證據，不作最終新執行宣稱。

固定版本 package smoke 與獨立審查尚待執行。Portable CLI 在隔離 fixture 執行；路由 closure fixture 另覆蓋 mandatory portable sources 與 optional profile 存在／缺檔。Package smoke 只證明 archive bytes／metadata 與 helper inclusion，不代表真實 downstream adoption。未執行的 hosted CI 不列為通過；未量測 token 或整體工時效益。

## Finding Resolution Matrix

| Assessment Finding | Status | 本次處置 |
| --- | --- | --- |
| ASM-20260921-18-gav#AIC-001 | resolved | 明列原 baseline schema／implicit contracts，拆分 nested record kinds，並檢查來源及 callable 路由；不宣稱自動發現所有隱含契約。 |
| ASM-20260921-18-gav#AIC-002 | partially-resolved | P1–P3 已增加高頻 linked documents、roles、skills、selected catalogs／target selections；其餘缺口保留明示 `manual-gap`。 |
| ASM-20260921-18-gav#AIC-003 | resolved | 每種記錄分開宣告 readable／writable／migration／admissible，不以版本欄位替換冒充遷移。 |
| ASM-20260921-18-gav#AIC-004 | resolved | 保留 owner 的不同欄位政策，工具只在符合各自政策時寫入；仍不建立通用寬鬆 schema。 |
| ASM-20260921-18-gav#AIC-005 | resolved | 完成 P4 處置：只移除非相關 family 的重複檢查呼叫，保留 validators／existing tests；沒有足夠等價證據者明示不刪除。 |

以上為實作者處置，獨立 verification 尚待固定版本審查。

## Verification Assessment Reconciliation

待固定實作 commit 的獨立 read-only review、package smoke 與證據驗證。新的 verification assessment 保留 reviewer 原文及 exact-byte archive；不修改原 baseline 的 final 結論。

## Deferred Work

`manual-gap` 並非忘記處理：CLI local binding 需要明示 opt-in；lease／review input／ledger 包含當次實際觀測與 custody；release、upgrade-route、rule ownership 涉及 owner reconciliation。現有工具不足時，必須保留人工建構加 validator，不能填入 fabricated approval 或 passed。

Python entrypoint、fixture classification 與 executable shell profile registry 也不能靠任意 YAML/JSON 欄位 writer 解決：有的欄位全部是 identity／安全 partition，有的需同步 test call site，有的本身是可執行 shell。後續若要新增操作，應按具體語意建立 candidate-validation seam。一般 skill creation、promoted role adapters、完整 rule-consumer 變更仍需協調多份 authority。這些是清單中可查詢的後續能力缺口，owner 為 repository owner；此次核准的 selected-adapter 與 P4 評估不以假能力填滿它們。

## Closure Evidence

尚未進行本機整合。owner 已允許本機 main merge，本次採 implementation freeze 與 evidence intake 分開的 checkpoint，審查完成後保留 merge boundary。不包含 remote push、PR、Issue／Project closure、tag、release 或 target upgrade。
