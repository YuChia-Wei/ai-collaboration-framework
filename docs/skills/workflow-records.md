# workflow-records

[回 Skill 目錄](README.md)

`workflow-records@0.1.0` 是可選的 workflow 紀錄工具。Git provider 沿用專案
工作目錄中的檔案；SQLite provider 將 workflow、文件、checkpoint 與完整歷史
存於明確選定的 repo 外本機資料庫。既有 presets 不會自動選入它。

使用支援 metadata 5 的 catalog／engine，在安裝選取加入此 skill，並選取所需
Codex 或 Claude adapter。可用能力以所選公開套件與實際安裝版本為準。
需預先準備 Python 3.11+、PyYAML 6.x、Git；SQLite 使用 Python 標準模組，
無額外服務，也不會自動下載 prerequisites。

安裝後的入口是 `.ai/core/skills/workflow-records/tools/workflow-records.py`。
先以 `capabilities` 讀取能力，再依明確 reference 執行 find、context、read、
checkpoint、operation 或 resume。SQLite 額外提供 init、create、write-document、
完整 export／preflight／inactive restore，以及受控 deactivate／activate。

[完整操作契約](../../src/skills/workflow-records/references/operations.md)包含
精確欄位、設定範例、重播與衝突語意、容量及恢復限制；該契約也隨套件安裝。
[Git 格式](../../src/skills/workflow-records/references/git-format.md)說明既有
workflow.yaml／tasks 與 checkpoint 行為。產品執行不依賴來源 checkout。

套件安裝不建立 caller 設定、workflow 或資料庫。原始 Git records、SQLite
資料庫及 caller 附件由目標專案擁有；重裝不代表資料遷移。還原先保持唯讀，
只有完成原 store 的 retirement 與唯一 successor claim 才可啟用新寫入。
此版不提供原 store 遺失時的 disaster promotion，也不自動提交 Git、更新
GitHub Issue／Project、同步遠端 board 或將舊 Git 紀錄搬到 SQLite。

資料權威、備份與同步需分開理解：

| 項目 | 本版語意 |
| --- | --- |
| SQLite store | 所選 local workflow 的權威資料，含文件、修訂、事件、附件與去重 receipts；不是刪除後可從原始 Git workflows 重建的索引 |
| 完整 export | 同一讀取快照的可攜備份；preflight 核對完整性後，可還原為 inactive store。備份不能取代唯一 writer 的啟用程序 |
| Git 備份 | 使用者可自行選擇保存 export 檔案並提交 Git；工具不自動提交，也不把活躍 DB 納入 Git |
| 多人／跨機同步 | 未提供；Git 保存備份不會讓不同 clone 或兩份 SQLite 自動合併成一致的可寫權威 |

既有共通入口的 [逐步範例](../workflow-records-walkthrough.md)與隨包操作契約
提供 request 格式；本次來源候選的實際安裝與限制見
[交付驗收紀錄](../../.dev/workflows/2026-10-11-workflow-sqlite-package/acceptance.md)。
