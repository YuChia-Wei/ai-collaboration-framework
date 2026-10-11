# #441／#448 本機交付與 v0.20.0 readiness

更新時間：2026-10-11T18:46:52+08:00。此紀錄交付本次授權的實作、可選套件、
合成消費端安裝及驗證；不代表 GitHub 整合、Issue 關閉、發布或正式資料採用。

## 固定來源與成果

- 驗證來源：`4ec4114dbcdffaacfada5b05a4e8d750f5304deb`。
- 來源 tree：`a76a26c62924f0e43dc8e5de0a42a86477386601`。
- 實作起點：`6a615e8ac19df9343835ab74a0e2436cdc974976`。
- 交付單位：可選 `workflow-records@0.1.0`，metadata 5，以 `support_files`
  明確宣告七個 runtime 模組；保留既有 presets 與 source-project 安裝。
- 執行前置：Python `>=3.11,<4`、PyYAML `6.x`、Git、Python 標準 SQLite。
  本次實際執行使用 Windows Python 3.13.14；不內附或自動安裝前置依賴。
- 全部可發布產品程式、資源與 release README 模板來自 `src`。根目錄
  `tools` 僅保留來源維護與驗證入口，未成為安裝後依賴。caller-owned
  configuration／workflow 路徑保留各自權威，不受產品 source pin 的 `src` 限制。
- Owner 採納 Git files＋SQLite，Dolt 保留後續候選；未加入 remote／Board
  adapter、自動同步或真實歷史資料遷移。

## 實際證據

| 類型 | 固定來源的實際結果 | 證據與限制 |
| --- | --- | --- |
| Source suite | `python -I -B tests/run.py`：243 tests，0 failures/errors/skips；68.19431 s | `F:/fw441-448/source-test-4ec4114d.json`；包含 19 個 SQLite 情境與真實 CLI／競爭程序／未提交程序中止 |
| Assembled payload | 真正 catalog、workflow subset 與不選 workflow 的 subset 均完成 | 選入時完整 closure；未選入時不存在 workflow runtime |
| Installed runtime | 外部 validator `contract_advice` 執行 51 次呼叫、69 checks 全部 passed；114.539 s | `F:/fw441-448/e-af7291441785/terminal.json`；Git／SQLite 皆由 installed CLI 執行 |
| Source access | 每個受監測的 consumer Python process 阻擋兩個 source roots；核對載入模組位置 | Python file-access audit；不是 native child 的 OS sandbox |
| Installation maintenance | initial apply、同 candidate no-op、completed-operation finish read-back 與 restore refusal | 安裝中斷與 power loss 未測；拒絕結果沒有算成 restore 成功 |
| Preservation | 前後 preservation JSON 完全一致，SQLite bytes 一致，caller tracked diff 為空 | 保留安裝前 caller config、locator、plan、task、sentinels，以及重裝前全部 installed／caller 檔案 |
| Test storage | 51 份 command records 的 cwd、TEMP、TMP、TMPDIR 全為 F | 全部後續 test artifacts 位於 Owner 選定的 F RAM disk；不宣稱持久媒體耐久性 |
| Hosted／release／adoption | 未執行 | 未 push、PR、merge、建立 tag、發布、更新真實下游或修改 GitHub Issue／Project |

Source log SHA-256：
`34fff0750281215e59b5d94055983820e7319f97a08555b5d0efd9406adfee9d`。
Source result JSON SHA-256：
`5259bd84338a01bedb862f96779a5d35856fdf9410637e5f3c59d50544c1050d`。
Installed terminal SHA-256：
`0532b8d0caf71772c15000c7c6db90a3e4e2d6ae537daac60342ad2f5b3022f8`。
Runner SHA-256：
`5884b18141b3d1f1abea0b431fb41e9346d556d55b428fb4609456aedbb7cc31`。

實際 runner 命令（cwd `F:/fw441-448`）：

```text
python -I -B F:/fw441-448/runner-4ec4114d.py --repository C:/Github/YuChia/ai-collaboration-prompts-dotnet-backend --commit 4ec4114dbcdffaacfada5b05a4e8d750f5304deb --workspace F:/fw441-448 --evidence-root F:/fw441-448
```

`--repository` 是唯讀來源；執行腳本、來源副本、工作目錄、暫存、組裝、安裝、
SQLite 與證據全部在 F。主來源及獨立來源副本在執行後均保持 tracked clean。

## #441 驗收對照

驗收採用 Owner 的 SQLite 設計決定及
[#441](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/441)
AC01–AC06；狀態限定於本次合成本機資料。

| AC | 處置 | 證據 |
| --- | --- | --- |
| AC01：更新不造成 workflow tracked diff | 已驗證 | 真實 SQLite CLI 測試與 installed consumer 最終 `consumer-diff` 為空；DB 在 repo 外 |
| AC02：跨程序接手與文件／限制／下一步 | 已驗證 | 新程序 resume、revision-bound 文件；installed `sqlite-resume` 讀回相同 checkpoint |
| AC03：去重、不同內容拒絕、過期 revision | 已驗證 | Source 及 installed 同 ID replay、不同內容 `operation_id_conflict`、過期 `revision_conflict`；source HEAD 變更無寫入 |
| AC04：並行及不支援模式 | 已驗證（宣告的本機範圍） | 兩個真實 client 同 revision 僅一個成功；同 ID 一次效果；外部鎖 busy timeout；網路／repo 內 DB 拒絕；linked worktree 與 clone binding 區分 |
| AC05：完整 export／乾淨 restore | 已驗證 | Source 真實 SQLite 測試保留全部修訂、事件、receipts、未知欄位與 binary attachment；比對 hashes／relationships；inactive restore、唯一 successor、競爭 export 與程序中止情境 |
| AC06：備份、索引與同步界線 | 已驗證（文件與 capability） | [使用指南](../../../docs/skills/workflow-records.md)明確區分權威 store、完整 export、Git 備份、可重建索引與多人同步；隨包操作契約保留手動 export／inactive restore 與啟用限制 |

AC05 的 activation 第二階段中斷使用故障注入；另一個 workflow transaction
測試實際中止子程序，驗證 revision／receipt 一同 rollback。兩者不能替代
斷電或磁碟故障測試。完整來源 suite 在最後固定版本重新執行，不沿用修復前結果。

## #448 驗收對照

本次將 #441 的 local provider 與
[#448](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/448)
套件交付合併驗證；#448 原本單獨列為範圍外的 local provider，由 Owner 本次
明確指定與 #441 一起交付，沒有據此擴張 remote／Board 範圍。

| AC | 處置 | 證據 |
| --- | --- | --- |
| AC01：可選宣告／closure 一致 | 已驗證 | Metadata 5、manifest、operations、runtime members 與 schema tests；實際 optional subset 未含 workflow runtime |
| AC02：成品安裝與 source 獨立性 | 已驗證（Python source-access 隔離） | 真正 catalog/subset initial apply；無 source PYTHONPATH；source 讀取探針拒絕且模組均位於 installed root；下列 artifact identities 與每次 raw output 可查 |
| AC03：完整 Git 操作鏈與資料保留 | 已驗證 | Installed find → context → read → checkpoint → operation → resume；另同樣執行 SQLite；caller 原始 bytes 保留 |
| AC04：衝突、replay、unavailable 不 fallback | 已驗證 | Git／SQLite 各自真實推進 HEAD、檢查無寫入；同 ID replay、不同內容與過期 revision 拒絕；remote unavailable 前後兩個 store hash 相同 |
| AC05：initial／repeat／selected recovery | 已驗證（選定情境） | 初次 applied、第二次 unchanged/no-op；以原始 operation.json SHA 執行 finish 得 already-matching；對 completed operation 的 restore 得 conflict；caller config／workflow／DB 保留 |
| AC06：文件入口與缺少前置／member | 已驗證（選定缺少情境） | Installed path 實際執行；`-S` 排除 PyYAML 與移走已宣告 backup.py 均 structured unavailable；原 bytes 隨後恢復，未安裝依賴或改 binding |
| AC07：證據層級分離 | 已驗證（紀錄） | 上表分開 source／static／assembled／installed／Windows native API／hosted／release；macOS/Linux、IDE discovery、installer interruption 與 power loss 未執行 |
| AC08：v0.20.0 引用實際 payload／runtime | 已完成本機 readiness 對照 | 下列精確 artifact identity、installed evidence、限制與後續整合責任；不以版本字串或 source tests 代替 |

## v0.20.0 交付對照與接手

這是供 [#446](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/446)
引用的 #448 必要交付證據；不是整個 v0.20.0 release acceptance，也不解除
#437 或其他既有發布條件。

- Catalog identity：
  `catalog:1:0.20.0:4ec4114dbcdffaacfada5b05a4e8d750f5304deb:cbe36a01869f3cc28a0a207f999b34910e9625256c6a3d2177772d4c7d43f3a5`。
- Workflow subset identity：
  `subset:3:0.20.0:4ec4114dbcdffaacfada5b05a4e8d750f5304deb:5ccd958637cb36b8919dd0fec4f352c3c36ab7e702afa2413d5964b3e011e0ed`。
- Candidate：`F:/fw441-448/w-af7291441785/workflowo/subset-d13a0b6b936045c590449f37dad3afea`。
- Consumer：`F:/fw441-448/w-af7291441785/p`；入口為
  `.ai/core/skills/workflow-records/tools/workflow-records.py`。
- Engine pin SHA-256：`1973137c4ce27473defd5d2d0d420d361edea3f2bb94fea9414eb78120fb3371`。
- Installed lock SHA-256：`85483c69130843a8c9da8fdb3468147dcef2ac209795d48f092a788aa885038d`。
- Original installation operation SHA-256：`8218c61103c491887d4c457b86f54847a18768a46941ef5bd020cbe51a0f36c1`。

支援限制：本機合作 writers、明確 repository binding、有限且不驅逐的歷史容量；
原 DB 遺失時不支援 disaster promotion。64 MiB backup、60 MiB 一般 portable data、
4096 workflow operations／128 administrative receipts 的上限，不宣稱無限歷史。
RAM disk 僅用於本次測試，產品文件仍要求真實 workflow 使用持久儲存。

下一位整合者使用分支 `codex/2026-10-11-workflow-sqlite-package`，先核對本紀錄
與最後 commit。此次本機授權交付已完成；#441／#448 維持 open，未修改線上 AC
勾選或 Project。後續 push／PR／merge 另依明確授權，並要求實際當前 PR head 的
`Source change gate` 成功，再分別處理 Issue／Project 與 release 決策。若另行
組裝新來源身份，需保留新 artifact identity，不能冒用以上產物的安裝結果。

第一次安裝失敗、schema 修復、獨立審查與 Owner 指定清除 C 測試目錄的紀錄，
保留於 [validation.md](validation.md)。本機 suite 與安裝成功不抹除該次失敗。
