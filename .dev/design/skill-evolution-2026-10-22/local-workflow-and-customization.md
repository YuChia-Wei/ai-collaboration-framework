# 本機 workflow 與客製 skill 升級評估

參見 [設計入口](README.md) 的 owner 意圖與授權。owner 已明確將本文件兩個主題列為另案，
本次只建立中文 Feature／設計 Story，不實作下列提案。本文只評估現有公開契約與提出
產品選項，沒有執行 CLI、建立 store、安裝、遷移或驗證 runtime。基準為
`f96fffe0af6e9e4f79d5f2f4be05bb3665553123`。

## 1. 本機工作管理目前具備什麼

| 面向 | `local-backlog` | `workflow-records` |
| --- | --- | --- |
| 主要責任 | work item、AC、狀態與完成證據 | workflow 文件、checkpoint、接續與恢復 |
| 權威資料 | `<id>.work-item.json`；Markdown 是 render view | 既有 Git 文字紀錄或明確選定 SQLite store |
| 公開操作 | explain/create/inspect/query/revise/transition/render | capabilities/find/context/read/checkpoint/resume/validate/operation；SQLite 另有 init/create/write-document/export/preflight/restore/deactivate/activate |
| 工作狀態 | draft/planned/in_progress/blocked/completed/cancelled；終態唯讀 | 可讀已有 tasks/status，但沒有公開 task／metadata editing |
| 純文件方式 | filesystem records；非任意 Markdown | Git provider 讀 `workflow.yaml`、plan 與 tasks，持久寫入限 checkpoint journal |
| SQLite | 無 | 有；DB 目前必須在 repo 與 Git common dir 外 |
| Git 前提 | 僅選用 local config 的 ignore 檢查等條件用途 | Git 與 SQLite provider 都要求既有 Git repo 提供來源身份 |
| 線上服務 | GitHub 連結僅 reference，不同步 | 無遠端 provider；不更新線上 tracker |
| 開發編排 | 無完整開發編排責任 | 不選階段；由 `software-development-orchestrator` 決定 |

直接來源：
[local operations](../../../src/skills/local-backlog/references/operations.md)（操作與生命週期）、
[local configuration](../../../src/skills/local-backlog/references/configuration.md)（store 與條件 Git 要求）、
[workflow operations](../../../src/skills/workflow-records/references/operations.md)（操作矩陣、task editing 限制、SQLite path 與 Git 要求）、
[Git format](../../../src/skills/workflow-records/references/git-format.md)（checkpoint-only writer）。

因此不能直接移除 local-backlog 並宣稱 workflow-records 已完整取代。
現有 Git provider 也不能描述成「任意純 Markdown 的無 Git 工作管理器」。

## 2. 整合選項與建議

| 選項 | 做法 | 主要取捨 |
| --- | --- | --- |
| C-A 保留分離 | local-backlog 管 work item；workflow-records 管執行，兩者以引用連接 | 改動較小；使用者仍需理解兩個 store／生命週期 |
| C-B 整合記錄，保留編排 owner（推薦） | work-item/task 記錄能力整合至 workflow-records；orchestrator 繼續決定下一項工作 | 符合簡易本機體驗；需完整語意與 provider writers，並安排相容／遷移 |
| C-C 資料與開發編排全部合一 | 改為單一 workflow manager，兼管 state 與開發判斷 | 與現有 orchestrator 重疊；讀取資料容易混入執行，技能過大；本輪不推薦 |

推薦 C-B 對外提供簡單的本機使用模式：選定 record provider、以本機 work item 為
工作來源，使用既有 orchestrator 編排，再選需要的專業能力。這可以是可選組合與
指南，不必創造另一個 orchestrator，也不要求使用者安裝所有 framework skills。
是否新增 preset 是後續選擇，不在本輪默改既有 presets。

### 資料責任與判斷責任

- `workflow-records`：建立／查詢／更新記錄、允許的狀態轉換、依賴引用、版本衝突、
  operation replay、checkpoint 與 recovery。可以機械回報相依／阻擋資訊，不能自行改優先順序或接受成果。
- `software-development-orchestrator`：依使用者目標與接受條件選下一個工作、依賴排序、
  skill 路由、驗證安排與結果交接；判斷須遵守既有授權。
- 狀態欄位、record schema validity、checkpoint 或 `resume` 不構成新的執行授權，
  也不單憑 `completed` 文字證明行為已完成。
- 下游可選本機 work item 作為工作權威；不需要線上帳號或 GitHub Issue。
  framework 來源庫目前選用的 GitHub 治理仍保留，不因此改成本機 backlog。

### 最小資料概念（提案，不是新 schema）

| 概念 | 內容 | 避免的重複 |
| --- | --- | --- |
| Work item | 目標、AC、優先序、依賴、狀態與完成依據 | 可以只有候選工作，尚無 workflow；不把草案當執行中 |
| Workflow | 被選定的一次執行脈絡、work item refs、計畫、授權來源、結果與接續 | 可涵蓋數個有凝聚性的 items；同一 item 可有後續執行，不強制 1:1 |
| Task | workflow 內可追蹤的工作、阻礙、依賴與驗證結果 | 不為每次 skill 呼叫建立 task；避免和 work item AC 複製成兩套業務真相 |
| Checkpoint | 某一時間已知進度、下一步與限制 | 引用權威 task/item state，不另成一份可衝突的狀態 owner |

### 儲存選擇必須明說

「repo 內自有」可能指專案擁有資料，或要求 DB 實體在 repo 裡，兩者不同。
先以專案擁有、不需線上服務作為目標；DB 位置尚待 owner 決定，不能默默延伸授權搬動它。

| 選項 | 建議與限制 |
| --- | --- |
| Files/Git | 優先沿用 YAML/JSON 結構與 Markdown plan/body，補正式公開 writers；人類可讀與 diff，不把所有 Markdown 都當可解析狀態 |
| SQLite | 相同核心 work 語意；現行 repo 外位置、完整備份與單一 successor 啟用語意保留，除非另行改契約 |
| DB 放 repo 內 | 若 owner 要求，需另外定義忽略／備份／外洩與共用 writer 邊界；不能直接 Git 追蹤活 DB 並宣稱等同文件協作 |
| 完全不用 Git | 目前 workflow-records 不支援；若需要，另定 source identity 與衝突策略，不把「不在線上」推論為「不能用 Git」 |
| Markdown 為權威狀態 | 另需讀寫保真與衝突語意；本輪優先建議結構化記錄搭配 Markdown 正文，不引入任意 Markdown parser |

兩 provider 要列清楚可用操作。推薦核心建立／讀取／更新、transition／resume 語意一致，
provider-specific 備份與恢復維持明確差異；不承諾每一個底層操作完全相同。
本提案不新增刪除記錄能力；刪除及歷史保留若有需要，應另定操作與授權。

### 相容與遷移

1. 先保留舊 local-backlog reader 與生命週期，完成新入口與等效核心能力，再考慮退役。
2. 預覽舊 store/ID → 新 reference 的映射；保留 ID、created_at、AC、狀態、完成證據、引用與可保留 extensions。
3. 無法映射的版本／欄位／權威衝突保留為未完成，不能丟棄或自行改意義；終態不自動重開。
4. 遷移須明確授權與讀回，原資料保留；採納後只有一個 writable authority，避免雙寫分歧。
5. provider 切換不等於資料遷移；目前 export/restore 不能被當成 Git ↔ SQLite 轉換工具。
6. 新記錄類型納入 SQLite 的備份、歷史、operation receipts 與恢復閉包；不繞過 inactive restore／唯一 successor 保護。
7. local-backlog 的退役版本、過渡期限及使用者 selection 改法須獨立決定，不自動刪除舊 store。
8. 本機與線上同步、雲端服務及多人協作平台不在這個簡易本機方案的必要範圍。

### 待採納的完成判準

| ID | 條件／預期 |
| --- | --- |
| C-AC-01 | 沒有線上帳號、credentials 或網路時，可在已初始化本機 Git repo 建立 item/AC/依賴與 workflow |
| C-AC-02 | Files/Git 與 SQLite 均有公開 work-item/task 建立／讀取／更新及有效狀態轉換；讀回核心語意一致 |
| C-AC-03 | orchestrator 能從已授權本機 item 完成有界切片並 checkpoint；新 session 可接續而不重做已完成工作 |
| C-AC-04 | stale revision、重複 operation ID、同 ID 不同 payload 有明確結果，不產生重複 transition |
| C-AC-05 | item 完成有 AC 對應證據；schema validity 或 checkpoint 不能替代 acceptance |
| C-AC-06 | 舊資料映射完整保留身份／語意；未知版本與衝突留下原始資料，不假稱遷移成功 |
| C-AC-07 | provider default 改變不搬動資料或改寫舊 refs；遷移後 writer authority 明確 |
| C-AC-08 | 人工修改／Git merge conflict、SQLite recovery 與所有新記錄的保護契約可被驗證 |
| C-AC-09 | 已安裝 consumer 無 framework checkout 仍可使用；所有 runtime resources 均來自 `src` 的宣告閉包 |
| C-AC-10 | 人類指南提供兩種模式最短流程與能力矩陣，明示安裝不等於 store 初始化 |

## 3. 客製 skill 與升級目前已有的保護

依 [安裝說明](../../../docs/installation.md) 的「安裝後的檔案／客製」與調整段落：

- Unknown/custom skill、資源、設定與 runtime entries 預設保留，不必登記才受到保護。
- Managed 修改／刪除會造成 drift；unowned destination 即使 bytes 一樣也不能據此取得 ownership。
- `.ai/core` 是 managed output，不是自訂 authoring 位置。現行文件已要求沿用專案慣例或請 owner 選位置。
- 自訂 ID 不能任意塞入 catalog selection，也不能手改 lock。
- `skill_naming: original/prefixed` 是 runtime entry 名稱模式；不是 author/designer 等語意命名慣例。
- 已有 derive → inspect → plan → authorized apply 與 recovery 邊界；本次沒有執行證據證明其 runtime 結果。

[Governance 方法](../../../src/skills/ai-context-governance/references/maintenance.md) 目前也禁止
以複製 core 到 custom 來繞過 managed 規則，並避免建立第二套 customization ledger。
因此新增 metadata 若被接受，必須在原 owner 修訂相應契約與明確讀寫用途，不能在旁邊
多放一份無人消費的標籤表，更不能將它作為覆寫／刪除的授權。

[Lock schema](../../../src/distribution/schemas/lock.schema.json)及其
[直接契約](../../../src/distribution/schemas/contracts.schema.json)是封閉格式。
以下欄位都只是設計草案，不得直接加進現有 lock 或 installed metadata。

## 4. 用獨立狀態軸產生人類標籤

使用者列出的情境包含來源、修改、上游能力與整合進度，可能同時成立。
推薦先記錄這些事實，再產生人類標籤；不設一個互斥 enum 企圖涵蓋全部狀態。

| 面向 | 提議內容／值 | 足夠的判斷依據 |
| --- | --- | --- |
| Origin／ownership | framework-managed、project-authored、project-derived、unknown | canonical ID、來源版本／revision、baseline bytes、實際 writer 與來源鏈 |
| Local delta | none、present、unknown；另記 managed bytes 是否被直接改動 | 舊 baseline 與 local 的實際差異，不能由自填標籤替代 |
| Upstream coverage | not-assessed、not-covered、partial、covered-with-evidence | 客製意圖與 AC 對新版本契約／行為的逐項證據；不是文字相似度 |
| Reconciliation | pending、proposed、validated、adopted、superseded | 三方結果、衝突、必要驗證與 owner 接受；狀態不表示已 apply |
| Apply／activation observations | 未執行、已寫入／已安裝、已觀察 discovery、已觀察行為及各自限制 | 實際操作與讀回；metadata 宣告、hash 相等、文件導航各只能證明其本身 |

例如：「project-derived／local delta present／upstream covered／reconciliation proposed」
表示新版可能已涵蓋需求，但本機還沒採納或移除客製。「AI 已整合新版」若只有生成
結果，最多是 proposed；缺少 runtime 證據時不顯示為已生效。

每項 customization 除 patch 外，應保留簡短意圖與 AC。例如「review 時保留既有
GWT Then outcomes」可用不同文字實現；只有原始 diff 無法判斷 upstream 是否已滿足。
優先引用既有決策／記錄，不再複製一份權威批准狀態。

### Metadata 的放置與採用選項

| 選項 | 取捨 |
| --- | --- |
| 僅說明文件／現有決策引用 | 最少機械能力，適合少量客製；無法穩定自動比較與呈現 |
| 可選 project-owned customization manifest（推薦起點） | 明確版本與讀寫 owner，引用 baseline／意圖／狀態證據；不可成為自訂資源保護的必要前提 |
| 直接把所有標籤塞入 lock | 混合機械 inventory 與語意採納，且現行 schema 不支援；不推薦 |

推薦先採有界 manifest／既有紀錄的引用整合，並定義真正使用它的 compare/read-back
流程；確切名稱、schema、存放位置與是否納入 installer 下一版仍待選擇。不創建通用
全產品 provenance 平台，不要求既有使用者先把所有 custom 資源補登記才能升級。

## 5. 三方比較與語意整合流程提案

1. 綁定真實舊 framework baseline、現行 local/custom 版本與新 candidate；缺少 base
   時標明 unavailable-base，無法聲稱完成三方比較。
2. 機械比較 paths／bytes／references／runtime ID collisions；另比對客製意圖及 AC。
3. 對每項差異提出保留、重套、調整後保留、由 upstream 取代或待 owner 決定的 disposition。
4. 依客製要求做必要驗證，保留 partial coverage、語意衝突與未執行項；沒有文字 conflict
   不等於行為等效，AI 自評也不是 owner 接受。
5. 依已存在的明確授權套用選定結果；授權未涵蓋刪除／切換／安裝時再取得所需決策。
   不增加每個步驟重問批准的流程。
6. 用受支持的 authoring／installation route 寫入並讀回，分開記錄 mechanical merge、
   semantic validation、owner adoption、apply、runtime discovery／行為。
7. Upstream 已涵蓋不自動刪掉 custom、停用 entry、改歷史或改用另一模型／provider。

現有直接修改 `.ai/core` 的情境維持 managed drift；要先保留其意圖與差異，再依
支持的遷移／安裝流程處理。新增標籤不能令 drift 自動成為合法 managed baseline。
這項工作觸及 installation/recovery，後續實作需要來源政策規定的獨立 scoped review。

## 6. 自建 skill／資源位置提案

| 資源 | 建議 owner 與位置 |
| --- | --- |
| Framework 已安裝 canonical resources | `.ai/core/skills/<id>/`，維持 installer ownership |
| 專案自建或明確衍生的 authoring package | 可選慣例 `.ai/custom/skills/<project-skill-id>/`，SKILL/references/scripts/assets 共置；保留已有專案布局 |
| Codex／Claude runtime entry | 使用實際 adapter 支援的位置，明確引用 project package；先檢查名稱與 managed entry 碰撞 |
| 客製 provenance／整合 metadata | project-owned，位置另選；不是手改 lock，也不是第二個批准來源 |

`.ai/custom/skills/...` 是未採納的候選慣例，不是目前已保證可由所有 runtime 自動
發現的路徑。不重用已有特殊安裝／恢復用途的 `.ai/local`，也不將 source 直接塞進 core。

Project-derived skill 需要 owner 選定的 fork 或實際支援的 extension binding。
不能藉「複製到 custom」掩飾 managed drift，或猜測同名 entry 會覆寫 framework entry。
名稱可使用專案 namespace，canonical source identity 則另行保留。所有必要資源都
必須能從明確的 package root 或已宣告知識依賴解析，不依賴 framework 原始 checkout。

### 待採納的完成判準

| ID | 條件／預期 |
| --- | --- |
| D-AC-01 | 可分辨 framework 原版、自建、明確衍生與 unknown；標籤依來源證據，不能創造 ownership |
| D-AC-02 | 可同時表達 upstream 已涵蓋與 local 尚未遷移；不把 covered 當 adopted/active |
| D-AC-03 | base 缺失、local drift、candidate 變動均可見，不偽稱 merge 成功 |
| D-AC-04 | 同 bytes unowned path、ID/entry collision、缺 reference 都不自動覆寫或刪除 |
| D-AC-05 | 未登記 custom 在升級／取消選配／重裝仍預設保留 |
| D-AC-06 | 檢查未改 framework、直接 drift、自建、衍生、機械可合併、語意衝突、上游部分／完整涵蓋的代表情境 |
| D-AC-07 | metadata／navigation／安裝／discovery／行為結果分開；缺少 required evidence 顯示未完成 |
| D-AC-08 | metadata 有一個明確 owner/version，引用既有決策；不修改封閉 lock 或建立兩份權威批准 |
| D-AC-09 | 安裝中斷時可依受支持 recovery 處理，不因新增客製 metadata 失去原保護 |
| D-AC-10 | 自建 package 在所選 runtime 的 discovery 與資源解析有實際證據；未知 adapter 不概括宣稱支援 |

## 7. 評估限制與後續

本文件的現況結論來自具體 Markdown/schema 契約與來源入口；沒有執行 provider writers、
installer 或 runtime discovery，也沒有把 graph 查詢結果當作行為證明。兩個有界唯讀
子任務分別核對了 workflow 與 customization 證據；它們沒有修改檔案，且這不等於
產品變更的 immutable independent review。

後續先決定 C-B 是否採用、Git／DB 位置／文件權威格式，以及 D 的 metadata owner
與最小使用方式。實作前再查看直接程式路徑與受影響測試，不以本次文件盤點取代
真實 code discovery 或 consumer acceptance。這些獨立範圍不阻擋 A 的責任拆分。
