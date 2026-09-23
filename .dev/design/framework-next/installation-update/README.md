# P6 安裝、差異更新與恢復設計

[#345](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/345) design checkpoint，依 [#322 U001](../../../assessments/ASM-20260923-00-6oq/execution-plan.md)。本次追加統籌選定的 **quiescent maintenance v1**：呼叫者先停用受影響能力、停止會話／工具／外部 writer，再做安裝或恢復。工具只能讀取這項聲明，無法證明活動已停止；非參與 writer 同時修改是不支援情境，hash recheck 不解決 TOCTOU。

OS-held lock 只協調 install/recover/M01 等參與的 maintenance writers。技能平常閱讀與執行不接共同 launcher，instruction skills 不新增 runtime。marker 表示維護未完成、owner 不可啟用；它不能強制停止讀者或收回 agent 已載入的文字。

公開安裝操作是 inspect、plan、apply、recover。成功只表示 **managed-bytes-consistent**，project_readiness 為 **not-assessed**。專案另外選定公開 reader 做啟用檢查；未知相容性不是 pass。開發 engine 由專案外固定 source checkout、完整 commit 與必要檔案雜湊執行，不從正被改寫的 core 載入。

保留 exact inventory、raw digest/mode delta、unchanged 不重寫、未知／drift 檔案保護，以及完整 durable managed before/after snapshot。RAM project 消失後只能由該 snapshot 恢復 managed core/lock/runtime；專案資料需要自己的 Git／備份。即使受管 bytes 完整，也不可宣稱 whole-project ready。這能省去人工複製與逐檔同步，但仍需 drift reads 和 durable snapshot I/O；沒有實測速度、寫入或 SSD 壽命宣稱。

Package update 不改專案 config/data。統籌在 `842b73ca09d701d1561109255193d80439dc996b` 選定的 M01 僅在實際需要時，將閉合 P2 project/local JSON exact integer 1→2，其他值、absence、write_roots、locks不變。它另由 config-transition owner 指派，保留 durable before bytes／部分 pair 恢復／外部新資料保護，不擴張成通用 migration 或 compatibility 系統。

- [實作契約](contract.md)、[機器格式](formats.md)、[synthetic exact-shape examples](examples.json)。
- [Dogfood／fallback／implementation slices](cutover-and-slices.md)、[來源證據](source-evidence.md)。

原 checkpoint `51229b63565ce6e836d57a4b107cf6df5554bf7c` 保留為設計歷程；目前文件取代其中每次 invocation 共用 guard 的提案，未 rebase。仍需指派 engine pin/bootstrap、maintenance lock backend、實際 durable roots、首個 profile、必要 M01 及專案啟用檢查；不需新增 adapter 共用 launcher。

狀態：設計修訂，未實作／試跑／安裝／啟用。只做 U001 允許的直接讀取、UTF-8／JSON／YAML 語法、參照／Git／diff 與完整 commit-message 檢查。產品 CLI/help、schema validation、tests/fixtures/build/install/migration/audit/CI 均 deferred-by-owner；authority U001，owner program #322 coordinator / P7，next action P7 在實作後選定 redesigned checks。
