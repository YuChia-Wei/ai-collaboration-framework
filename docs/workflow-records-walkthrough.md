# Git workflow 共通入口的完整操作範例

這個範例使用 [source checkout CLI](workflow-records.md)，串起同一筆紀錄的
建立、接手、checkpoint、指定文件讀取與操作結果查詢。Git 情境已在隔離的
真實 Git repository 執行；local／remote 的對照僅是設計要求。

先由專案原有 writer 建立 `workflow.yaml`、至少一個 `tasks/*.json|yaml|yml`
及 locator 指定的 entrypoint。目標目錄須有 Git commit；共通入口不替代這個
writer，也不修改 task 或 workflow 的生命週期狀態。範例驗證使用現有
`2026-10-02-skill-routing` 紀錄的隔離複本，沒有改動原紀錄。

將各請求存成 UTF-8 JSON，再以同一個 `--root` 執行：

```powershell
python -I -B tools/workflow-records.py --root C:/path/to/project --request C:/path/to/request.json
```

每次同時檢查 exit code、`status`、`mutation_state` 和結果／錯誤。
以下回覆片段只顯示相關欄位；實際回覆還有版本、operation 與部分 limitation。

## 1. 確認能力，查找並讀取 context

```json
{"contract_version":"workflow-records/1","operation":"capabilities"}
```

Git provider 會列出可用 operations，且 `create` 為 `false`。送出
`{"contract_version":"workflow-records/1","operation":"create"}` 會以 exit 1
回傳 `status: error`、`mutation_state: none`、`unsupported_capability`；不會
假裝建立空紀錄。既有 writer 建立好紀錄後，查找它：

```json
{"contract_version":"workflow-records/1","operation":"find","provider_id":"git","limit":10}
```

從 `result.items` 保存完整 `workflow_ref`。此範例使用：

```json
{"provider_id":"git","store_id":"project-workflows","workflow_id":"2026-10-02-skill-routing"}
```

後續請求使用這份 ref；若你選的是其他紀錄，請一致替換所有範例中的 ref。

```json
{
  "contract_version":"workflow-records/1",
  "operation":"context",
  "workflow_ref":{"provider_id":"git","store_id":"project-workflows","workflow_id":"2026-10-02-skill-routing"}
}
```

保存以下值，並檢查 `missing`、`tasks_truncated` 與各摘要的 `truncated`：

| 本文符號 | 取值來源 | 用途 |
| --- | --- | --- |
| `R0` | `result.revision` | 這次 checkpoint 依據的核心紀錄版本 |
| `H0` | `result.source_head` | 這次 checkpoint 依據的 Git HEAD |
| `D0` | `result.entrypoint.revision` | 指定文件的原始 bytes 版本 |
| entrypoint | `result.entrypoint.document` | 此例為 `workflow-plan.md` |

`R0`、`H0`、`D0` 是範例符號，不是有效值。送出下列 JSON 前，須以剛讀到的
完整字串替換 `<R0>`、`<H0>`、`<D0>`；不要使用別次範例的雜湊值。

## 2. 條件寫入 checkpoint，保留可重試的原始請求

```json
{
  "contract_version":"workflow-records/1",
  "operation":"checkpoint",
  "workflow_ref":{"provider_id":"git","store_id":"project-workflows","workflow_id":"2026-10-02-skill-routing"},
  "expected_revision":"<R0>",
  "expected_source_head":"<H0>",
  "operation_id":"checkpoint-001",
  "checkpoint":{
    "summary":"完成來源盤點，準備審核設計",
    "authority":"隔離 fixture 示範，不代表正式採用",
    "completed":["盤點目前讀取與寫入路徑"],
    "pending":["審核設計"],
    "blockers":[],
    "evidence":["inventory.md"],
    "next_action":"核對設計與驗收案例"
  }
}
```

`evidence` 等文字是呼叫者提供的觀察／引用，工具不會因此驗證檔案存在、
批准範圍或執行結果。此示範只用來核對傳輸與儲存行為。

首次成功是 exit 0，主要欄位為：

```json
{"status":"ok","mutation_state":"applied","result":{"state":"applied","operation_id":"checkpoint-001","replayed":false}}
```

完整結果另含 `checkpoint_revision` 與 `source_head`。保存原始請求與操作 ID。
原封不動再送一次會得到 `replayed: true` 及相同 receipt，journal bytes 不變。
此時 `mutation_state: applied` 表示該操作已有套用結果，不表示又寫入一次。
若重用 ID 卻改了 checkpoint 或原條件，會得到 `operation_id_conflict`。

## 3. 分辨過期寫入與安全重試

成功寫入後，若把同一份請求的 ID 改成 `checkpoint-002`，卻保留舊的 `R0`，
這是另一個依據過期版本的寫入；它以 exit 1 回傳：

```json
{
  "contract_version":"workflow-records/1",
  "operation":"checkpoint",
  "status":"error",
  "mutation_state":"none",
  "error":{"code":"revision_conflict","message":"Workflow inputs changed; read context again."}
}
```

重新取得 context 並核對差異，再決定新的 checkpoint 內容與唯一操作 ID。
不要單純換上新 revision 以強行重送舊決策。若問題是 Git HEAD 改變，另有
`source_conflict`；先確認 source 再形成新的請求。

## 4. 指定文件版本、查操作結果與接手

再次取得 context 後，使用當次回傳的 entrypoint `document` 與文件 revision。
只新增 checkpoint 時，核心 revision 會改變，但未修改的 plan 仍保有 `D0`。

```json
{
  "contract_version":"workflow-records/1",
  "operation":"read",
  "workflow_ref":{"provider_id":"git","store_id":"project-workflows","workflow_id":"2026-10-02-skill-routing"},
  "document":"workflow-plan.md",
  "revision":"<D0>",
  "offset":0,
  "limit":256
}
```

結果有 `content`、`revision`、`truncated`、`next_offset`。若要續讀，以相同文件
revision 和回傳的 `next_offset` 當下一次 `offset`；文件變了會明確衝突。
此處 offset／limit 是字元數，輸出另外受 `max_output_bytes` 上限約束。

查詢原操作：

```json
{"contract_version":"workflow-records/1","operation":"operation","workflow_ref":{"provider_id":"git","store_id":"project-workflows","workflow_id":"2026-10-02-skill-routing"},"operation_id":"checkpoint-001"}
```

成功查詢是 `status: ok`、`mutation_state: none`，`result.state: applied`，
`checkpoint_revision` 與首次 receipt 一致。查不到 `not-recorded` 這個 ID 時，
結果則為 `state: unknown`；查詢成功不等於原寫入成功或失敗。

```json
{"contract_version":"workflow-records/1","operation":"resume","workflow_ref":{"provider_id":"git","store_id":"project-workflows","workflow_id":"2026-10-02-skill-routing"},"limit":256}
```

Resume 整合 context、checkpoint 摘要及 plan，仍須保留截斷／缺漏標記。
Receipt 查詢與重試都要求核心紀錄可解析；若原紀錄損壞，依
[復原指引](workflow-records.md)先保留 journal 並核對，不把查詢失敗當成未寫入。

## 5. 更換預設值不會替既有紀錄改綁 provider

把下列 JSON 存為另行指定的設定檔，呼叫時加上 `--config C:/path/to/config.json`。
工具不會儲存或自動採用這份設定：

```json
{
  "contract_version":"workflow-records/1",
  "default_provider":"board",
  "stores":{
    "git":{"kind":"git","store_id":"project-workflows","root":".dev/workflows"},
    "board":{"kind":"remote","store_id":"board-records"}
  }
}
```

此時不指定 provider 的 `find` 選到尚未實作的 remote，exit 1 回覆：

```json
{
  "contract_version":"workflow-records/1",
  "operation":"find",
  "status":"unavailable",
  "mutation_state":"none",
  "error":{"code":"provider_unavailable","message":"Selected provider is not implemented; no fallback was attempted."}
}
```

前面保存的完整 Git ref 仍可讀取同一筆 Git 紀錄，不受這個 default 影響。
若另送一個明確使用 `board`／`board-records` ref 的 checkpoint，亦回報
`provider_unavailable`、`mutation_state: none`，既有 Git journal 不變。
這是現行入口拒絕未實作 provider 的實際結果，沒有執行網路連線或遠端故障測試。
不要為了消除 unavailable 而另建一份可寫副本。

## 同一情境對照三種模式

| 步驟 | Git：現行可執行範圍 | Local：設計要求 | Remote：設計要求 |
| --- | --- | --- | --- |
| 建立 | 原 project writer 建立；共通 create 明確不支援 | 若宣告 create，選定資料庫並回完整 ref | 若宣告 create，由 adapter 映射建立結果及完整 ref |
| 接手 | context／resume，有界且標示缺漏 | 讀一致的資料庫 snapshot | 讀服務宣告的版本與 snapshot |
| 修改 | 同 clone 內 cooperating lock＋條件檢查＋單文件 replace | 同一交易內檢查 revision 並保存 outcome | 使用服務提供的條件命令與 outcome |
| 指定文件 | 以原始 bytes digest 綁定 read | 以保存的文件 revision 讀取 | 以 server revision／ETag 映射讀取 |
| 查結果 | 查保留 journal；缺 receipt 是 unknown | 查已提交的 operation row | 查服務 operation；非終態可回 pending |
| 不可用 | 不切換到其他 store 寫入 | unavailable，沒有 Git fallback | unavailable／pending，沒有 Git／local fallback |

後兩欄尚無 runtime，也沒有通過 provider 驗收。`pending` 是未來 remote 的結果
契約要求，並非目前 Git CLI 已觀察到的回覆。Git 跨 branch／clone 沒有中央交易，
RAM disk／本機測試亦不證明斷電持久性。
