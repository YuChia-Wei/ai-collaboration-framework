# workflow-records

[回 Skill 目錄](README.md) · [模組與資料流](../workflow-module-map.md)

來源版 `workflow-records@0.2.0` 提供離線 workflow 紀錄、同步意圖、讀取來源選擇、
檔案匯出與完整備份恢復。它是獨立選配套件，所有現有 presets 都不會自動安裝。
來源實作與已發布 ZIP、專案安裝、實際 provider 驗收分別判定。

## 選擇適合的紀錄契約

| 契約／入口 | 權威與用途 |
| --- | --- |
| `local-group/1`，`tools/local-group.py` | 新 group 預設使用普通 JSON 檔；可加入檔案或 SQLite 成員。選定的一個成員同時擁有讀取和接受寫入，其他成員接收固定修訂的同步資料 |
| `workflow-records/1`，`tools/workflow-records.py` | 既有 Git provider 讀取／checkpoint；原生 SQLite provider 提供建立、修訂、文件、完整歷史及備份 |
| `source-store/2`，`tools/source-store.py` | 原生 SQLite schema 3 的多 carrier 配置與唯一讀取來源；writer 固定為 SQLite，讀取來源選擇不轉移 writer |
| `provider-control/1`，`tools/local-group.py` | group 的 project-owned 實驗性 provider 註冊與設定；準備固定命令、記錄 host 回傳結果，不自行連線 |

新 local group 的 SQLite 格式為 `workflow-local-group-sqlite/1`，與原生 SQLite
schemas 1／2／2.1／3 不相容；不能把既有 DB 直接附加成 group 成員或自動升級。
Git provider 和 local-group 的普通 JSON 檔也不是相同格式。先選契約，再依它的
完整 reference 操作；缺少選定權威時明確失敗，不切換來源、不建立替代 store。

安裝使用 metadata 5 相容的 catalog／engine。一般本機操作需 Python 3.11+、
PyYAML 6.x；Git provider 另需 Git，SQLite 使用 Python 標準模組。明確選用的
schema／既有 replica 嚴格驗證還需要其契約指定的 jsonschema。工具不下載依賴。
安裝副本的入口位於 `.ai/core/skills/workflow-records/`，不依賴 framework checkout。

## 多目標同步與唯一來源

一次接受的修改保存固定 revision、operation ID、payload 和目標 generation。
本機接受不代表所有目標已同步。呼叫 `group-sync-status` 檢查本機成員，再對
固定 intent 執行 `group-sync`；遠端 provider 使用 prepare／host dispatch／observe。
沒有背景排程或自動網路傳送。失敗重試沿用原 intent，達上限後須明確 resume。

`select-authority` 只接受已完整追上的本機成員，更新 authority epoch；舊 epoch
不能繼續寫入。provider 設定改動只影響未來目標，既有待送 payload 保持不變。
原生 source-store 的讀取來源則以其 read-prepare／proof 契約處理，不混用 group
的 authority transfer。實際跨廠商、多 Agents 與線上服務驗收仍是另外的工作。

## 可讀檔案、schema 範本與恢復

| 操作 | 成果與限制 |
| --- | --- |
| `export-files`／`group-export-files` | 使用明確 revision 匯出目前完整 `workflow.yaml`、task YAML、文件及附件原 bytes，另保存 manifest 和完整 current-record sidecar |
| `preflight-files`／`group-preflight-files` | 驗證原 manifest digest、檔案集合、hash、原 revision 和 YAML／sidecar 一致性；不把後續變更誤判為匯出當時的狀態 |
| `export`／`group-export` | 包含完整歷史及恢復控制資料的 archive；與可讀檔案匯出分開 |
| `preflight`／`restore` 及 group 對應操作 | 檢查完整備份並還原為 inactive；只有原 store retirement 和唯一 successor claim 完成後才能啟用寫入 |

可讀匯出使用全新目錄，保留 metadata／task 未知欄位，不套入範本預設值。
文件位於 `documents/`、附件位於 `attachments/`；manifest 保存原 logical name
與實體路徑對照。它不是完整 recovery archive，也不宣稱可直接送入 Git provider。
原始 YAML 的註解與排版若未存入結構化紀錄，無法從該紀錄重建。

套件提供 workflow／task schema 與範本，可明確複製到 project-owned
`.ai/project/workflow-records/`。以 selection JSON 的路徑、profile version 及
各檔案 hash 選用；升級不覆寫專案副本。預檢拒絕不存在、漂移或不相容的資源，
不抓取遠端 `$ref`、不轉換資料。0.6.0／0.9.0 及團隊自訂格式須有實際樣本另行
驗收，不能只憑版本名稱宣稱相容。完整步驟見[檔案匯出契約](../../src/skills/workflow-records/references/file-export.md)。

原生 schema 2 的既有 replica binding 可透過 `binding-disable` 以 CAS 停用。
它保留舊資料、以固定 cutoff 停止未來 intent，並拒絕 command preparation；
此明確操作將 store／backup 標記為 2.1，舊 runtime 會拒絕。歷史 lookup／observe
仍可使用，但不是發送授權。group provider disable 與此原生 binding 控制分屬不同契約。

目前不提供原 store 遺失後的可寫災難提升、任意歷史格式轉換或 PostgreSQL／MSSQL。
原資料、備份、project 設定與 lifecycle 都由專案擁有。Workflow 可重開；工具支援
原子修訂並保留歷史，專案仍須同時調和 workflow／task status、phase、結果及時間。
Checkpoint 摘要不會自動改進度，也不等於完成驗收或關閉 Issue。

## 操作與線上擴充

- [原生與 Git 操作](../../src/skills/workflow-records/references/operations.md)
- [local-group、同步及 provider controls](../../src/skills/workflow-records/references/local-group.md)
- [source-store、binding 與備份](../../src/skills/workflow-records/references/source-store.md)
- [Git 逐步範例](../workflow-records-walkthrough.md)
- [workflow-board-experimental](workflow-board-experimental.md)：另行選取且明確啟用的 Board V2 bridges，required-depend on 核心；SourceReplica 不經過 V2 bridge

移除 Board bridges 不刪除核心保存的配置、pending commands、receipts 或歷史。
純資料 validator 缺少時，依賴它的操作會 unavailable。安裝、prepared request、
本機成功與真實線上接受各有證據；工具不自動 commit、更新 Issue／Project 或發布。
