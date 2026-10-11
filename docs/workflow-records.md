# Workflow 紀錄共通入口：第一個 Git 切片

目前提供 **source checkout CLI**，需要 Python 3.11+、PyYAML 6 與 Git。
它尚未納入 framework 安裝包；既有 installed orchestrator 不會自動取得這支工具。
完整英文契約位於 [workflow_records](../src/workflow_records/README.md)。
需要逐步核對 request／response、重試、衝突與 unavailable 時，請依
[完整操作範例](workflow-records-walkthrough.md)使用同一筆 workflow ref。

此切片支援目前 `workflow.yaml`、`tasks/*.json|yaml|yml` 與 UTF-8 文件格式，
可查找、讀取、留下 checkpoint、查操作結果及整理接手資料。未選用的專案繼續
使用原方式。local／remote 只保留契約位置，尚未實作。

## 使用方式

在 framework checkout 執行以下命令；`--root` 指向欲讀取的專案，
`--request` 指向自行建立的 UTF-8 JSON 請求。工具不會自動儲存設定。

```powershell
python -I -B tools/workflow-records.py --root C:/path/to/project --request C:/path/to/request.json
```

先查找紀錄：

```json
{"contract_version":"workflow-records/1","operation":"find","provider_id":"git","limit":10}
```

保存回傳的完整 `workflow_ref`，不要只保留 workflow ID。每個後續操作都使用
相同 reference。以下 ID 僅為範例，請替換成查找結果：

```json
{
  "contract_version":"workflow-records/1",
  "operation":"context",
  "workflow_ref":{"provider_id":"git","store_id":"project-workflows","workflow_id":"2026-10-10-example"}
}
```

Context 含 `revision`、`source_head`、必要摘要、task 摘要、entrypoint 及最新
checkpoint 摘要。`missing`、`tasks_truncated` 和文字欄位的 `truncated` 必須保留。
需要完整內容時以 `read` 指定 `document` 與回傳的文件 `revision`，按 `next_offset`
續讀；`resume` 會使用同一個入口組合 context 與 plan，仍可能是有限長度的內容。

Checkpoint 請求必須帶上剛讀到的 revision／source，以及本次操作唯一且可重試的 ID：

```json
{
  "contract_version":"workflow-records/1",
  "operation":"checkpoint",
  "workflow_ref":{"provider_id":"git","store_id":"project-workflows","workflow_id":"2026-10-10-example"},
  "expected_revision":"sha256:replace-with-context-revision",
  "expected_source_head":"replace-with-context-source-head",
  "operation_id":"checkpoint-001",
  "checkpoint":{
    "summary":"完成依賴盤點，準備審核設計",
    "authority":"本次使用者授權的工作範圍",
    "completed":["盤點目前讀取與寫入路徑"],
    "pending":["審核設計"],
    "blockers":[],
    "evidence":["inventory.md"],
    "next_action":"核對設計與驗收案例"
  }
}
```

成功結果含 `state: applied` 與 `checkpoint_revision`。若回覆遺失或顯示
`mutation_state: unknown`，先用相同 ref、`operation: operation` 及原本的
`operation_id` 查詢。相同 ID／相同原始請求可安全取得保留結果；不同內容重用
同一 ID 會被拒絕。查不到結果是 unknown，不能視為已確認失敗。

查詢 operation 與重試仍要求目前 locator、task、plan 可正常解析。如果核心紀錄
損壞，先保留 checkpoint journal，依專案授權修復紀錄後再核對；查詢失敗不代表
原本的 checkpoint 沒有成功寫入。

## 相容性與寫入範圍

新增內容只寫入該 artifact root 下的 `.workflow-records/checkpoint.json`。
原有 locator、task、plan、未知延伸欄位與證據檔不會被重寫。Checkpoint 不自動
修改 task／workflow status，也不等於批准、完成驗收或關閉 Issue。

工作目錄要先有 Git commit。工具不會自動 stage、commit、push 或切換分支。
Revision 同時檢查核心紀錄內容與指定 source HEAD；其他證據文件有獨立 revision。
鎖定只涵蓋同一工作目錄內使用本工具的 writers，跨 clone／branch 與直接編輯
需要另外協調。這不是跨檔案交易或跨電腦同步服務。

可用 `--config` 指定不同 locator root 與穩定 store identity；範例見英文契約。
更換 `default_provider` 不會更換既有完整 ref。缺少 provider 或 remote 不可用
會回報 unavailable，不會另寫一份 Git 或 local 紀錄。

## Assessment validator 的明確選用

既有 assessment validator 預設保持原本的 workflow locator 存在檢查。
若專案選定此格式，可傳入上述 JSON 設定：

```powershell
python -I -B tools/maintenance/validate-assessment-artifacts.py --root C:/path/to/project --workflow-store-config C:/path/to/workflow-records.json
```

這條路徑會真正呼叫共通 parser／validator。缺檔、格式錯誤與版本不支援會失敗，
不會只因 locator 檔存在而通過。它不取代專案的其他 assessment、workflow
lifecycle、release 或 handoff 規則。

## 回復與後續範圍

停止使用新入口時，恢復呼叫原有 writer；validator 移除選用參數即可回到原本行為。
新增 checkpoint 可保留在原 Git store 作為紀錄，不需要刪除或搬遷既有資料。
不要把不同 clone 的 checkpoint 當成可以自動合併的兩份可寫權威。

發現 `writer_busy` 時先停止相關 writers，確認 journal、operation ID 與 lock
owner 是否仍在執行。只有確認已無存活 writer 後，由專案 owner 決定移除那個
stale lock／temporary file；工具不會自動搶鎖。移除前保留 checkpoint 並核對
操作結果，再重新讀 context。歷史容量滿時工具拒絕新寫入，不會自動清除 receipt。

本輪未接入：舊 handoff／terminal validators、所有歷史格式、installed runtime、
新增 workflow 的共通 create、任意多文件修改、資料庫、board、完整搬遷及發布。
F RAM disk 可用於暫存 fixture；其測試結果不代表斷電後的資料持久性。
