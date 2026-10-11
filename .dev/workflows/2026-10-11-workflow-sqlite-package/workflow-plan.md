# Git＋SQLite workflow 套件交付

本工作承接 [#441](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/441) 與 [#448](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/448)。Owner 於 2026-10-11 授權依先前建議完成實作、套件安裝與驗證；SQLite、repo 外持久儲存、明確 repository/worktree binding、序列化本機 writers、手動完整 export／inactive restore 為本次採納方向。

## 交付邊界

- 共用 Git／SQLite 的 workflow reference、查找、context、revision-bound read、checkpoint、operation receipt、resume 契約。
- 使用預先準備的 Python／PyYAML；不內附 runtime、不移植語言、不導入 Dolt。
- 下游成品的所有程式及資源只從 `src` 組裝；不得復用 `tools` 或其他 source-project 路徑。來源入口可向 `src` 委派，反向依賴禁止。
- 真正 catalog/subset 安裝至一次性 consumer；驗證 Git 與 SQLite，重新安裝／恢復與 caller-owned 資料保留。
- 不自動提交 Git、不搬遷真實紀錄、不啟用雙向同步、不發布 release。#448 的 v0.20.0 必要交付不等於版本已發布。

## 階段

| Task | 工作 | 狀態 |
| --- | --- | --- |
| T1 | SQLite adapter、初始化、受控寫入與完整備份／還原 | completed (source) |
| T2 | src-only optional package、完整模組閉包及安裝入口 | completed (source) |
| T3 | 真正成品安裝／恢復與雙 provider 驗證 | completed（69 checks，F 合成 consumer） |
| T4 | 固定來源獨立審查、必要修正及逐項驗收紀錄 | completed（含實際失敗修正及 evidence read-back） |

## 檢查與證據

先執行受影響行為的 focused checks，再執行固定 `python -I -B tests/run.py`。實際 consumer 操作另外保存產物 identity、命令與結果；不以 static 或 mocks 代替 installed／concurrent-client 證據。長時間命令依 source policy 固定來源、隔離 writer 及保留終端報告。

Package 需證明所有 payload source 位於 `src`，傳遞 import 不回指 repo `tools`，隔離執行不讀 source checkout；惡意或錯誤非 `src` 成員須在組裝前拒絕。

本機 focused 結果與失敗修復見 [validation.md](validation.md)。固定來源 `4ec4114dbcdffaacfada5b05a4e8d750f5304deb` 已完成 243 項 source tests、真正 installed runtime 的 69 項 checks，以及獨立 source／修復／證據審查。[逐項驗收與 v0.20.0 readiness](acceptance.md)保留 artifact identity、命令、限制與接手責任。起點為 `6a615e8ac19df9343835ab74a0e2436cdc974976`。圖索引對 workflow classes 無充分 coverage，使用已知 Git-tracked `src/workflow_records`／distribution 與直接 tests 的明確 fallback；不以搜尋無結果證明不存在。

## 本次完成與下一個權限邊界

本次本機實作、合成消費端安裝與驗證已完成。Owner 後續指定所有 test paths
使用 F RAM disk，並清除 C 測試資料；已依指示保留精簡經驗紀錄，移除 C trial
與 raw logs。F 結果不宣稱持久磁碟或斷電耐久性。

來源分支尚未 push／建立 PR／merge；#441、#448 仍為 open，線上 AC 與 Project
未改動。後續整合需要其明確授權與實際 PR head 的 Source change gate。
本工作不處理 tag／release、真實 downstream 更新、正式資料搬遷或 #437 發布條件。

任務 model／effort 取自 2026-10-11 讀回 host configured defaults `gpt-6-astra`／`ultra`；不宣稱獨立觀測 runtime 執行身分。
