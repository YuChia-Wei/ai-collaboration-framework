# 來源布局與自用安裝設計（#326）

這份 P1-B 設計將產品原始內容收斂到 `src/`，根目錄則像一般專案使用已安裝成品。本次只交付設計與範例，沒有搬移產品、建立套件或變更目前根目錄規範。

- [英文設計](design.md)：所有權、明列分發清單、stable/development、runtime 生成、差異更新與回復。
- [來源對應與分階段清單](mapping-inventory.md)：已讀取的舊路徑、初期 Lesson 範圍與後續分類。
- [manifest](examples/distribution-manifest.example.yaml)、[目錄](examples/layout.txt)、[安裝／回復規劃](examples/installation-plan.example.yaml)：可檢視的設計資料，不是可執行設定或成功紀錄。
- [工作計畫](../../../workflows/2026-09-23-source-layout/workflow-plan.md)：有限檢查、U001 延後事項及統籌交接。

## 開發者使用方式

目標日常使用方式是選用明確版本與 digest 的 stable 成品；P2 僅建立 development candidate，不宣稱已發布 stable。開發 Lesson 時，只改 `src/skills/lesson`，對已提交快照選擇 development，產生並安裝該 skill 與必要 runtime 入口。發現問題仍回 `src` 修正；`.ai/core`、`.agents/skills` 不形成第二份手工來源。這是 P2/P6 待實作的路徑，目前沒有假造可用 CLI。

`.ai/core` 是 framework 管理的選配內容；`.ai/custom`、根目錄指示與真實 Lesson/ADR/workflow 資料由專案擁有。資料可以放在指定位置，不必集中到 `.dev`。#325 擁有 metadata/config/schema 契約；本設計只決定安裝布局與映射，不複製 schema。

已對照 #325 提交 `c3891615` 的 metadata 與設定契約：skill ID 為 `lesson`，schema 為 `lesson.record` 的 `1.0.0`，檔案為 `schemas/lesson-record.schema.json`；工具 `lesson.fs` 仍是 `planned`、`entrypoint=null`，不建立假的腳本。required 與 optional dependencies 都是空集合。分發清單共有六個成員，包含 `references/configuration.md` 與 `references/operations.md`。設定僅支援 JSON，本 repo 選定路徑為 `.ai/custom/framework.json`，其欄位語意仍由 #325 擁有。

統籌已採納 stable core、lock 與精確 runtime 產物一起 tracked，以及首個 copied Codex 入口 `.agents/skills/framework-lesson/SKILL.md`。這是後續實作選擇，不代表目前已有可用或已發布的 stable 成品。

## 替換與回復

「可整體替換」表示 core 可從套件重建，不表示每次都重寫全部檔案。一般 apply 比較舊清單與實際 digest，未改的不寫；新增、變更、刪除只作用於確定由 installer 管理的檔案。手改 core、未登錄 runtime 檔案與 custom 同名衝突需先釐清。

回復須配對 core、lock、runtime，以及這次轉換的設定、record、索引版本。只回復工具，留下舊工具無法讀的新資料，不是回復成功。沒有反向轉換就使用對應持久備份；未知客製欄位、遺失註解或資料的轉換須明示不支援或交由 owner 決定。RAM disk 可放 staging，不能是唯一回復備份。

## 本次界線

初期規劃一個 Lesson、filesystem store、一種 runtime、一份 manifest。後續逐項移出舊 skill/shared/tool 的可攜內容，保留 source governance 與歷史；不搬整份 repository，不承諾舊版任意升級。

依 [U001](../../../assessments/ASM-20260923-00-6oq/execution-plan.md)，CI、舊 validators、critical/check-all、suites、package/upgrade/migration 試跑及 validation-only audit machinery 都是 `deferred-by-owner`，由 P7 承接。內容與格式檢查不代表安裝、更新或回復行為已驗證。
