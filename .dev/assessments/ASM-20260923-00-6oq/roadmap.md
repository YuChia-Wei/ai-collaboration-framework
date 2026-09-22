# 採納與實作路線草案

本文件是 assessment 的工作分解，不是已建立的 backlog、已採納的 roadmap 或執行 workflow。`Wxx` 是本文穩定工作包 ID；可在未來 Issue 引用 `ASM-20260923-00-6oq#Wxx` 並指明本文件。尚未排 release、工時或承諾日期。

## 執行順序

```text
方向採納：D01–D07
     ├─ W01 縮減測試／支援範圍與 I/O 邊界
     └─ W02 可攜技能與設定的最小契約
             ├─ W03 src／core／custom + dogfood 的小型垂直試作
             ├─ W04 組織型 workflow 與 storage
             └─ W05 ADR／Lesson／promotion
                    ├─ W06 PR 與 local backlog
                    ├─ W07 schema family 工具與 migration
                    └─ W08 整理／壓縮／移除
             W09 更新與一次性舊架構轉移
             W10 真實專案試用及停止／擴大決策
             W11 CLI／更多平台的再評估（條件式）
```

圖表示主要節奏，不要求所有工作等全部前置完成。W03 先搬一個 skill，不搬全 repo；W04 與 W05 可在 W02 後平行試作；W06 的 local provider 可先於線上 provider；W07 只處理正在改的 family。精確相依見下表。

## 工作包

| ID／階段 | 工作與交付 | 主要前置 | 可觀察完成條件 | 刻意不包含 |
| --- | --- | --- | --- | --- |
| W01／先止血 | 列出仍承諾的 install/update 行為，將測試分為保留、縮小、退役；設定 scratch/durable 路徑 | D03、D07；可先盤點再採納刪除 | routine 路線不再隱含歷史／多跳矩陣；每個留下的 I/O test 有產品風險；指定 scratch 的可丟棄寫入可觀察且 cleanup contained | 不先把所有舊測試改造成 RAM-disk 測試；不新造 benchmark 平台 |
| W02／最小契約 | 定義 skill package、依賴、設定解析、artifact role／ID 與錯誤輸出；做一個 resolver | D02、D04、D06 | 一個 skill 在乾淨專案、預設與非預設路徑完成任務；缺 optional dependency 可降級；缺 required dependency 明確失敗；沒有隱藏 source repo 引用 | 通用 plugin market、動態下載 solver、所有 skill 一次改完 |
| W03／產品邊界 | 建立 `src` canonical root、單一 manifest、生成成品、core/custom 安裝界線及 stable/dev dogfood | W02、D01 | 一個 skill 的 source → package → 根目錄消費可追溯；專案 custom 的已知 bytes 保持不變；重建不引入第二份手工 source | 首次就大搬全 repo、移植所有 provider、下游批次升級 |
| W04／編排 | 用一個組織型 skill 擁有 workflow schema、工具、模板、resume、retrospective；支援 Git 與 ignored local 兩種 store | W02；W03 可同步 | 同一簡短流程可從兩種 store 接續；不用固定 `.dev` locator；專家 skill 可直接執行；無新知時不產生假 Lesson | 通用 BPMN／排程服務／無限 agent orchestration |
| W05／知識閉環 | ADR 與 Lesson 的 create/find/update/supersede；一個 promotion 例子 | W02；回顧整合待 W04 | 依範圍讀出有效記錄；可標未知根因；避免重複記錄；採納後只有一個有效規範 owner；舊證據仍可定位 | 自動採納所有回顧、每次工作必寫 ADR、全文知識庫預載 |
| W06／工作與 PR | local-backlog skill、PR skill；先一個有需求的線上 adapter | W02；流程整合用 W04/W05 | local record 的 stable ID 與並行衝突可檢查；PR 摘要綁定當前 diff，驗證狀態真實；建立 PR 不自動 merge/close issue | 一次支援 GitHub/Azure DevOps/Jira/Gitea 全部寫入／雙向同步 |
| W07／資料工具 | 盤點仍在使用的 schema family，將可重用 #320 primitives 歸位；實作一條必要 migration | W02；按 W04/W05 的真實格式選擇 | reader/writer/validator/disposition 有 owner；一條 edge 可 preview、拒絕 drift、保留原資料並恢復；receipt 不被偽造或改寫 | 95 kinds 全面重寫、完整通用 YAML editor、所有歷史版本轉換 |
| W08／保存成本 | record compact/archive/purge preview；Git 摘要與外部原始證據 mapping | W04、W05；provider export 可用 W06 | 未完工作不被 TTL 刪除；摘要能續讀；referencers 可解析；外存先 read-back；不可恢復證據有明確 disposition | 自動 history rewrite、單看天數刪資料、每個 provider 的完整 archive 能力 |
| W09／更新策略 | core digest delta、必要 runtime projections、custom migration；一次性舊架構轉移說明 | W03、W07、D03 | 未變動 bytes 不重寫；只寫安裝擁有範圍；custom 不丟；不支援版本明確拒絕；中斷後可保留／恢復舊可用狀態 | 任意舊版多跳 upgrade、隱含採納新規範、承諾任意 downgrade |
| W10／實際驗證 | 本 repo + 一個明確選定的下游專案進行少量真實工作，記錄便利／干擾與成本 | W03；依待驗能力選 W04–W09 | 能用同一套成品適應不同目錄和規範；有真實輸出與使用回饋；人工補救次數、載入量／可得 token、I/O 和耗時範圍說明清楚 | 大規模 benchmark、無證據跨平台支援、直接推廣所有下游 |
| W11／條件式 | 重評 CLI、runtime、獨立發版及其他 providers | W10 顯示需求，或已有明確部署約束 | 說明現有小工具解不了什麼、最小 CLI 價值與預期成本；選一個 slice 再決定是否擴大 | 為了工具而重寫全部 Python、先建自有 issue 平台 |

建議第一個垂直範例是 **Lesson skill**：讀取現有記錄 → 在自訂路徑寫入一則候選 → 去重查找 → 由 workflow 回顧引用 → 產出規範變更提案。它能同時驗證可攜、設定、讀寫、知識轉移與可選 composition，且不必先打通複雜外部平台。正式採納或線上發布仍是另外的操作。

## 測試與功能的具體取捨

本表是退役提案，不是本次已刪除的項目。不要只把所有舊檢查搬到 nightly 便宣稱維護成本已改善。

| 現行負擔 | 建議處置 | 可以刪／縮的前提 | 留下的最小證據 |
| --- | --- | --- | --- |
| multi-hop upgrade transaction 在 fast | 移出 routine；若退出多跳能力就連功能、fixtures 和 runner 一起退役 | D03 明確不再支援該能力 | 選定當前更新路徑或一次性遷移的 tiny fixtures |
| 舊版本專屬 package lanes／candidate branches | 支援窗口關閉後刪除 active branches；舊 Git tag 保留歷史 | 有清楚支援政策與舊使用者轉移說明 | 當前發行物 smoke；不對每次改稿重新 replay |
| 大型 package/full/history 矩陣 | 取消常態全矩陣；必要處改為選定 package/component 與一個實際安裝 smoke | 對外相容性承諾縮小 | 真的出貨 bytes、核心邊界、自訂資料保存 |
| 反覆完整 repo copy／git worktree fixtures | 刪除只靠巨大背景資料才能跑的測試設計；logical case 改小模型 | assertion 不依真實 repo 規模 | 小型內容＋少量代表性檔案 |
| 多個 validators 重複驗同一格式 | 合併真正相同的解析與約束，保留不同失敗語意 | 比對同一輸入／規則／錯誤承諾 | 單一 owner check，清楚 negative cases |
| spec 或說明的純文字調整 | 只檢查影響的引用與格式，必要時生成一個預覽 | 未改機械行為／package boundary | 針對變更的讀回，而非全 Python suite |
| 真正資料改寫／刪除／migration | 保留窄範圍功能測試 | 功能仍存在 | unsafe path、custom overwrite、drift、unsupported version、中斷恢復 |
| real-storage／platform semantic tests | 顯式選跑，依功能變更觸發；無相應功能就刪 | 不能用 RAM disk 取代要驗證的語意 | 真實目標平台的小 fixture；不用全歷史包 |

不要把每次 terminal closeout 都變成重跑所有 checks 的觸發點。當前變更、所選成品與相應功能風險應決定測試集合。若無新變更、環境或資料依賴不變，就不為了新的文件時間戳重跑昂貴套件測試。

## 成功指標與停止條件

先用少量實際任務取得 baseline；不在此報告中假定節省百分比。必要指標如下：

| 問題 | 小型可取得指標 | 決策用途 |
| --- | --- | --- |
| skill 真能單獨使用嗎 | 安裝選定能力所需元件數、缺少相依診斷、人工補路徑次數 | 找隱性依賴 |
| agent 是否更少搬運格式 | 人工填機械欄位次數、工具輸入大小、格式修補次數；runtime 能取得時記 token | 評估工具化是否值得 |
| I/O 是否變少 | fixture bytes、檔案數、實際 writer 行為／process 數；硬體寫入無權限就標 unavailable | 分開 logical bytes 與實際 SSD writes，不推算壽命 |
| 是否更容易做產品改進 | 一次技能修改需要碰多少非產品檔案、強制 steps、額外測試維護時間 | 防止治理重新成為主產品 |
| 知識是否可用 | 能否找到當前規則與來源、重複／過期記錄數、跨 task 手動補問數 | 評估 ADR/Lesson 閉環 |
| 記錄是否可清理 | Git 新增工作資料量、摘要可續讀、archive 可讀性 | 避免以壓縮犧牲可接續性 |

任何微型設計若需要先建立全套 plugin manager、跨平台 provider sync 或大量歷史測試，先停止擴張，回到一個 skill／一種 store 的垂直例子。新增工具的驗收應包含它消除了哪些人工或重複維護，不只檢查它新增了多少規範。

## 與既有 Issue 的關係

live 狀態以 2026-09-23 查閱為準；本次沒有更新任何 Issue。以下是重評建議，不改變原 Issue 的 scope 或授權。

| Issue | 查閱狀態 | 本評估建議 |
| --- | --- | --- |
| [#319](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/319) artifact lifecycle coverage | closed/completed | 作為 W07 的 inventory 與工具基礎；不重新開同一問題 |
| [#320](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/320) authoring gaps | closed/completed | 保留已完成的 bounded authoring 方法；提取到 owning skill／小型共用模組 |
| [#274](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/274) fixture I/O classification | open | W01 先退休不再需要的 suites，再分類剩餘者；避免分類全部舊負擔 |
| [#275](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/275) durability/logical fixture costs | open | 只量測留下的代表性路徑，不把精密量測當作刪減所有舊承諾的前置 |
| [#149](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/149) CLI/validator runtime | open | W11 重新界定需要解決的問題；不要先做四種 runtime 的完整比較 |
| [#168](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/168) installable CLI preview | open | 待新 package/config 契約有實際樣本後再定 preview scope |

未窮舉其他歷史 Issues；未宣稱以上是全部重疊項目。未來建立工作項前，只需針對被選中的 Wxx 再查當時活躍 Issue，避免先把整份提案展開成大量待辦。

## 下一次工作入口

先選定 D01–D07 中會影響第一個垂直試作的決策，接受／調整 W01 與 W02 的 scope。其後以 Lesson 範例檢驗設計，成功再擴到其他能力。需要實作時另建立 execution workflow，引用本 assessment 與 Wxx；本 assessment 保留「為什麼這樣拆」的分析來源。

本次並未將這些提案寫成正式 ADR，因為分析還不能代替專案採納。也未自動排定 cleanup、reminder、nightly 或任何背景 automation。
