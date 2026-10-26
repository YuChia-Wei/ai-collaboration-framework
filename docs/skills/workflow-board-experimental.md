# workflow-board-experimental

實驗性選用套件，版本 `0.1.0`，需要明確選取 `workflow-records@0.2.0`。
預設 presets 不安裝；安裝後仍不啟用。每次 CLI 呼叫須明確加上 `--activate`，
沒有此選項時回傳 `experimental_not_activated`，在讀取 request 或載入橋接模組前停止。

```powershell
python -I -B <installed-package>/tools/board-query.py --activate --request <request.json>
python -I -B <installed-package>/tools/board-command.py --activate --request <request.json>
```

[query contract](../../src/skills/workflow-board-experimental/references/board-query.md) 與
[command contract](../../src/skills/workflow-board-experimental/references/board-command.md)
保留原有 Board V2 envelope 與版本。模組只準備及驗證資料，不執行網路、尋找憑證
或重試；host transport 的選擇與外部操作效果仍需明確授權。核心的本機 replica
配置與 prepare／observe 也不執行網路，不能把它們當作已完成線上同步。

真實 Board 登入、ACL、分享、撤銷、跨 client 與恢復驗收另行安排。
本機與模擬結果不代表線上已通過。[責任與資料流](../workflow-module-map.md)
說明 Issue、workflow 與遠端複本各自的責任。

升級舊合併套件應審閱 installer plan 並明確保留所需實驗性選項。核心不依賴
本套件；移除它不刪既有 replica 資料，不重寫待補送命令，也不改變 SQLite authority。
