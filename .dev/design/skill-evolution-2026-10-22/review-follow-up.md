# 外部審核處置與後續設計

2026-10-22 owner 要求讀取 Claude 分析、安排修正並調整設計及既有線上 Issues。
本文件延續 #476–#484；不新建替代工作項目。已授權文件修正與 Issue 整理，
未決產品選項仍保留為提案；不據外部建議自動升級本來源專案、改 pin、搬資料或分配版本。

## 審核來源與證據層次

[Slack 原訊息]([私人連結已移除])
附有「26-技能拆分分支審核-domain-model-designer與software-architect.md」與
「27-設計文件與發展方向評估-skill-evolution分支.md」。報告記錄的實際 reviewer
是 macOS 27 / Claude Code / Claude Fable 5.1（`claude-fable-5-1`），不是原交接預期的 Opus。
固定 subject 為 `6694b8b099c8fcc3063f498f008df698756e0a92`，比較基準為
`f96fffe0af6e9e4f79d5f2f4be05bb3665553123`。

報告 26 未列 P1/P2，列三項 P3；它回報 130 項 distribution/schema 測試、來源 metadata/
allowlist/文件檢查與 macOS 安裝／升級 trial。原始執行檔案在 reviewer 環境，
本次取得的是報告內容，不能表述成本機重跑或 hosted CI。13 項 AC 的審核是
instruction／結構層級；沒有證明所有 skills 的實際模型行為或所有 runtime discovery。

本次另由 tracked source、現有安裝 entry、Windows Preview 空目錄與 live Issues
核對可直接驗證的主張。圖譜僅以重新建立的 `src/distribution` 索引協助定位，
CLI 腳本採 tracked-file 讀取；空搜尋結果未用作缺陷證據。

## 報告 26：三項 P3

| ID | 核對與處置 | Owner／下一步 |
| --- | --- | --- |
| R26-1 | 舊 managed 檔案移除後可留空目錄。遷移指南補上 lock/inventory/entry 的判讀與避免遞迴刪除 custom 的說明；不改 installer 清理行為 | #480；文件修正 |
| R26-2 | 本來源專案仍有 17-skill 安裝，含舊 architect。雙語 AGENTS 明列實際已安裝入口及其原契約，與新 source owners 分開；不建立 alias | #480；文件修正，來源專案升級仍需另行選定 |
| R26-3 | `src/distribution/catalog.py` 的 `resolve_selection` 計算 `unavailable`，但 `derive_subset`／`src/tools/derive-subset.py` 公開結果未傳出該欄位 | #480；以下最小變更設計，尚未實作 |

### R26-3 最小變更與驗收候選

目的：使用者 derive 成功時仍能看見缺少的 optional knowledge 覆蓋，不把成功組裝
等同完整專業能力。沿用 resolver 的缺口資料，不建立第二套 allowlist 判定器。

- 僅在公開 derive 結果增加具固定形狀的 `unavailable`，沒有缺口時為空集合；
  最終欄位結構應對齊既有 resolver，保留 package/resource/consumer 的可定位資訊。
- 不將診斷寫成 desired selection、lock 或新的採納狀態，不藉此修改 artifact identity。
- Given 選 domain skill 而未選 common，When derive，Then 組裝依原選配契約成功，
  結果顯示對應缺口；不自動安裝或讀 framework checkout。
- Given 選足相容知識且 bindings 有效，Then 回報空缺口；Given required dependency 缺失，
  Then 保留原失敗結果，不能降級成成功 warning。
- 同時檢查 library result 與 CLI JSON，及既有 selection/lock 契約；測試限這個可觀察
  輸出與相容性，無需新增全面安裝或模型矩陣。

## 報告 27：設計建議的處置

| ID | 處置與理由 | 既有工作入口 |
| --- | --- | --- |
| S1 exact pins | 保留目前 exact pins。比較「維持精確版本，清楚分類 metadata-only/行為差異」與「支援相容範圍版本」；後者會改 resolver/identity/可重現性，不是文字最佳化 | #480；未決選項，不是本次引擎修正 |
| S2 行為 fixtures | 提議從兩新 skills 及四類既有 walkthrough 選 2–4 個有輸入、預期責任與反例的案例；記錄所選模型、實際輸出與限制。此為可選評估設計，未執行、不自動成為每次 CI 或每個模型 gate | #479 |
| S3 拆分界線 | 新 skill 應有不同的決策責任、獨立使用價值及必要回饋；跨角色可重用的方法優先作 knowledge。這是後續設計判準候選，不新增硬性 skill 數量／模板門檻 | #476；system/DevOps 仍中長期 |
| S4 capability | 人類知識指南補明 capability/operation/resource selector/allowlist/binding/installed closure 與 adopted authority 的共同限制；不改 enum 或授權 | #479/#480 |
| S5 roles | sub-agents 指南說明六個角色的證據、分析、審核、翻譯責任；開發方法仍由選定 skills 提供 | #480 |
| F1 決策分散 | 本設計入口增加本文件與既有 O-01–O-16；沿用既有決策位置，不為每項建議強制另建 ADR／批准 ledger | #476 |
| F2 自我安裝 | 修正可用入口說明即可解除路由歧義。catalog 變動不自動授權來源專案升級；既有 Windows Preview 與來源專案安裝保持獨立 | #480 |
| F3 版本規劃 | #443 可用 framework 下一次交付作方法範例；候選範圍、正式版本、milestone 及發佈依 owner 後續選定，不憑報告建立 0.21 | #443 |
| F4 歷史導航 | 新增 framework-next 歷史入口、更新 src/readme 與 .dev 索引，保留 U001 等未解除責任；不搬移／刪除舊 JSON 或改寫歷史 | #480 |
| F5 舊 Issues | #149/#168 移除 Portable Validator Engine 的現行前提，改以現行分發引擎與 CLI 需求再評估；#153 改為第三 adapter 的設計前提。#43 仍有初次導入用途，不合併或關閉；#179 已有可選整合邊界，保留 | 原 Issue 各自接續 |
| F6 #416 | 更新現有入口的剩餘工作與 #481 關係，保留既有歷史和來源權威，不關閉、不重開已完成子項 | #416/#443/#445 |

## 本機 workflow：歷史、現況與候選取代範圍

報告把 D-P3-04 當成 local-backlog 唯一 writer 決策，引用不正確。
[work-management contract §1](../framework-next/work-management/contract.md)
記錄獨立 packages／資料責任；同文件 WM-C3 / D-P3-04 談的是 optimistic
preflight/post-read 不能保證 server CAS，不能把它廢止成資料 owner 的替換。

| 來源 | 原責任／目前意義 | 若接受 C-B 才需改變的部分 |
| --- | --- | --- |
| P3 work-management §1 | local-backlog 擁有本機 work item 與其操作，project 擁有 records/settings | 將 work-item writer、schema、reader/migration 逐項映射到 workflow-records；等價能力與讀回完成前保留舊入口 |
| [P4 C341-01](../framework-next/p4-selected-contract.md) | 歷史 orchestrator@0.1.0 aggregate record；不是當前 orchestrator 可用 tool 的證據 | 不恢復舊 aggregate。核對現行 workflow-records 的 record owner 與 public operations，再設計 work-item/task 擴充 |
| 現行 workflow-records Git/SQLite | Git checkpoint writer 與 SQLite workflow/document 能力，尚非完整 work-item/task writer | 明確新增操作、revision/replay/生命週期、備份與恢復閉包；orchestrator 保留判斷 |
| WM-C3 / D-P3-04 | 並行寫入／CAS 的歷史限制 | 本次不取代；新 provider 的 concurrency 能力須另有契約與證據 |

目前沒有宣告 C-B 已 supersede 任何現行規則。#483 的設計完成條件包括每個實際
受影響 owner/reader/writer 的 before/after、保留義務、切換條件與明確採納狀態。
若選擇完全無 Git，需獨立列出 source identity、revision/conflict、遷移與 consumer
影響；「無線上帳號」本身不要求移除 Git。

## 客製升級：最小可用設計

#484 保留「未知即保留」及可選 metadata，與 #43 的初次導入相互引用但不互相取代。
最小 reader 應能讀 old base/local/new candidate 與客製意圖，輸出來源、缺 base、
差異與 coverage/proposed/adopted/active 的分離狀態；缺少語意證據時回報 unknown。
writer 只能處理明確選定的 project-owned 記錄，不能藉標籤改 managed ownership。

除了候選 authoring 目錄，設計必須回答 runtime entry 由誰生成、更新、檢查碰撞及
解除連結，如何保留 unknown entries，及哪些 adapter 有實際 discovery 證據。
選位置不等於已有 adapter／installer 支援。新 schema/reader/writer 尚未接受或實作。

## 接續順序

1. 完成三項 P3 的文件處置與既有 Issues 讀回；引擎缺口維持「設計完成、未實作」。
2. 若後續選定 R26-3，依 #480 做最小輸出修正與必要測試。pin 策略不阻擋此修正。
3. #479 的行為案例、#443 的交付方法與 #460 的方法知識各按原範圍另行選定；
   pin 比較是影響評估輸入，不是強制前置 ADR gate。
4. #483/#484 完成未決方案後才啟動產品實作。保留 #445 的線上整合延後決策。

本輪僅檢查修改的文件、連結、雙語對齊與 Issue 寫入結果；沒有產品行為變更，
不因文件位於 src 就重跑 130 項測試。PR hosted gate、merge、Issue closure、
Project 狀態與 release 仍各自獨立。


## 2026-10-22 後續修正授權

Owner 在 Preview／Gemini／獨立 sub-agent 審核後，選定修正剩餘三項缺陷，
準備確認內容後安排合併；本次整合僅關閉已交付工作項目，下一版發布另行安排。
上述「R26-3 尚未實作」是先前 checkpoint；本次執行狀態與證據改由
[REPAIR 工作紀錄](../../workflows/2026-10-22-domain-architecture-split/workflow-plan.md#2026-10-22-remaining-defect-repair-and-merge-preparation)
承接，不重寫原審核歷史。

#480 同時承接這輪確認的既有可攜角色缺陷：fixed auditor 強制要求未分發的
source preflight，以及四角色八個 projections 引用未定義的 role_bindings。
修正以實際可提供的 parent assignment 與 target rules 表達權威，保留唯讀、
獨立、固定 subject、漂移停止、失敗證據與 integration owner；不恢復舊工具或新增 schema。
四個角色 package 以 0.1.1 識別修正內容，不代表 framework 新版發布。

Gemini 的 .NET design 資源缺少候選未採納為缺陷：舊 architect 同樣未消費這四項，
新 skills 符合已接受的 allowlist，不能因 capability 分類相同而自動擴大採納。
#481–#484 保持後續產品設計，未納入這次交付的關閉清單。
