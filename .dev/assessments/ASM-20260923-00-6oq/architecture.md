# 目標設計與取捨

本文件屬於 `ASM-20260923-00-6oq` 的提案。目錄、能力名稱、設定欄位、版本與命令都是設計草案；不表示目前產品已支援。證據與外部來源見 [evidence.md](evidence.md)。

以下是可逐步採用的能力設計，不是第一版必做清單。**第一個 slice 僅做一個 skill、一種 filesystem store、直接設定的路徑與一個小型 schema family。** 有第二個實際消費者才抽共通 registry／resolver primitives；跨 provider、全域 artifact registry 和一般化 dependency solver 都不在第一步。完整設計用來避免未來互相衝突，而非增加當下前置工程。

## A1. 可攜 skill 與小型共通協定

### 分離三種責任

| 類型 | 擁有的內容 | 相依原則 |
| --- | --- | --- |
| 能力型 skill | 一項操作的說明、領域輸入／輸出、模板、schema、專用工具 | 可單獨呼叫；不強制依賴組織型 skill 或 workflow store |
| 組織型 skill | 多階段安排、任務／狀態、續作、能力組合、回顧、交付條件 | 透過公開能力契約呼叫選定技能；擁有自己的 workflow 格式 |
| 小型共通協定／函式庫 | 設定解析、logical artifact reference、型別／版本錯誤、最小結果 envelope | 不放團隊流程、PR 規則、ADR 寫法或技術架構政策 |

workflow 不是每項作業的預設儀式。單次補一份規格、查一則 Lesson 或準備 PR 可以直接完成；多階段、需要續作或多角色協調時，由組織型 skill 決定持久化程度。

Agent Skills 標準提供 `SKILL.md` 與 scripts/references/assets 的封裝起點，但沒有替本 framework 定義依賴解析或 workflow storage。建議在標準之上加薄薄的 package metadata，而不是發明另一個 skill 標準。先用一份 bundle lock 保證發布組合相容；暫不建立會自動下載套件的完整 package manager。

### 建議的 skill 套件

```text
adr-manager/
  SKILL.md                  # 任務入口與漸進載入
  skill-package.yaml        # framework 擴充 metadata，名稱待定
  schemas/                  # 此技能的機器資料格式
  scripts/                  # 具體操作；無操作需要可省略
  templates/
  references/               # 此能力真正擁有的說明
```

metadata 最少描述：穩定 skill ID、skill version、公開能力及輸入／輸出版本、必要 runtime、required/optional dependencies、設定 namespace、可寫的 artifact roles。不要每個文件都再建立另一份 metadata。

依賴必須區分：

1. **必要內容／工具依賴**：缺席時明確不支援該操作；由 packaging closure 帶齊。例：需要 YAML writer 的工具依賴。
2. **可選協作能力**：缺席時保留待辦或回傳候選內容。例：workflow 發現決策但 ADR skill 未安裝，不因此讓原工作失敗。
3. **專案規範輸入**：透過設定取得有效規範，不能直接依賴別的 skill 私有模板或此 source repo 的 `.dev/standards`。
4. **runtime/provider 能力**：shell、Git、特定 tracker API 是否可用，由 adapter 回報；沒有工具時不能假裝已呼叫或已發布。

required dependencies 應形成無循環圖；optional composition 也需由執行者限制遞迴。相同 reusable 規則有一個 owner，打包可以帶入必要內容，但不可出現兩份人工維護的規則真相。兩三個檔案的通用小函式不值得另外做一個可獨立發布的子產品。

「獨立可攜」的驗收是：把選定套件及明列依賴安裝到沒有本 framework repo 的空白專案，能完成其聲稱的操作，沒有隱藏 `.dev`、絕對路徑或其他 skill 的深層相對引用。

### 下游元件建議

| 分組 | 建議 |
| --- | --- |
| 必需 bootstrap | installed identity／lock、設定解析、所選技能的最小共通依賴 |
| 協作能力 | requirement、spec、設計、實作、review 等按需選用 |
| 組織能力 | software workflow 等選配；不默認所有能力都要用它 |
| 知識與工作管理 | ADR、Lesson、PR、local backlog 依團隊需要安裝 |
| 維護 add-on | ai-context audit、governance、init／upgrade assistance 選配或臨時安裝 |
| source 專用 | 本 repo 的 release、發布、source 歷史、維護者管理工具，不下放 |

自動安裝／更新若仍是產品功能，執行它的機械工具可在外部 installer，不必要求每個下游永久保有完整的治理 skills。把維護技能選配化，也要移除核心對這些技能的強制引用，否則只是名義上的選配。

## A2. 所有權與目錄

### 下游安裝示意

```text
project/
  .ai/
    core/                   # framework 擁有的所選成品；可替換
      skills/
      shared/               # 僅必要共通內容
    custom/                 # 專案擁有，可進 Git
      framework.yaml        # 團隊設定與 artifact mappings
      rules/                # 或引用專案既有 docs 規範
      skills/               # 專案自訂技能
    framework.lock          # 精確版本、digest、所選元件；可進 Git
    local/                  # 機器限定設定／cache，ignored
  .agents/skills/            # runtime 安裝面；依 adapter 生成
  .dev/                     # 專案自有資料，位置不是 framework 約束
  docs/                     # 亦可放 specs、ADR、guides
```

`core` 代表誰可以改，不代表裡面全部必裝。`custom` 不必容納所有專案文件；它可以只提供 mappings 與小型 override，真實規範仍在 `docs/engineering/` 等既有位置。

`.ai/local` 是可變執行資料，不混進 replaceable core；它也不是可隨意清除的所有 durable workflow。需要跨人／跨機器續作的 workflow 應在共享持久 store。lock 由工具生成，但由專案選擇並審查版本。

框架更新只能覆換 framework 管理的路徑。自訂技能使用 namespace 或明確 binding；同名衝突不得靜默遮蔽。core 出現本地修改時，先提示差異並提供移到 custom／patch 的選擇，不能把「理論上可替換」當作刪除現有手改內容的授權。

根 `AGENTS.md` 由專案擁有，只引用選定入口。第一次 seed 可生成建議內容，更新不能覆寫整份專案指示。runtime adapter 若必須產生 `.agents/skills` 或其他 provider 檔案，需知道自己的檔案集合並保護使用者自訂檔案；不要求所有平台支援 symlink。

### `.dev` 的轉移原則

現有 framework-owned policy/template 應移到 skill 或 shared 最小組件；專案採納後的規範留在專案。複製的初始模板一旦成為專案文件，就不能在每次更新時當成 core 覆蓋。

第一次遷移依現有 ownership manifest 與差異逐項分類：未修改 framework 檔案可以替換；專案修改、ownership 不明或混合內容產生候選分拆，不由文字相似度自動決定。只遷移當前有效內容；歷史工作紀錄先保留或封存，不全量重寫。

## A3. 設定、位置與 workflow store

### 設定解析

建議順序：明確的單次參數 > ignored 機器設定 > 專案設定 > skill 預設。這只適用可覆寫欄位；團隊鎖定的權限、外部寫入範圍或必要證據不得被一般路徑參數繞過。解析結果應可用 `config explain` 類型的唯讀操作檢視：值、來源、解析後位置和不支援原因，不顯示 secrets。

下列為**未實作的範例**；不直接建立這份設定：

```yaml
config_version: 1
artifacts:
  requirements: { store: repo, root: docs/requirements }
  specifications: { store: repo, root: docs/specifications }
  decisions: { store: repo, root: docs/adr }
  lessons: { store: repo, root: docs/lessons }
  standards: { store: repo, root: docs/engineering }
  assessments:
    store: repo
    root: .dev/assessments
    tracking: summary
  workflows:
    store: local
    root: .ai/local/workflows
    tracking: ignored
    retention:
      compact_after_days: 30
      archive_after_days: 90
      purge_after_days: null
work_items:
  provider: github
  binding: project-selected-binding
skills:
  software-workflow:
    retrospective: on-completion
io:
  scratch_root: os-temp
  durable_test_root: null
```

`30/90` 只是待試用的候選預設，並非已量測最佳值；`purge_after_days: null` 表示不自動刪除。機器設定可以把 scratch root 改到 `F:/ai-context-tests` 之類的使用者指定 RAM disk 路徑；這不是本次新設定，也未確認該磁碟目前存在。

設定中的路徑相對明確 project root，而不是目前 shell cwd。absolute／external root 需顯式設定；解析與清理工具檢查 canonical containment，禁止將 volume root 當作可刪除 run directory。invalid／unwritable root 明確失敗；不靜默改寫全域 TEMP/TMP 或換到另一個磁碟。

### 儲存與追蹤分開

| 選項 | 使用情境 | 必要語意 |
| --- | --- | --- |
| repo + tracked | 團隊需要審查完整紀錄 | 正常 Git review；不自動 stage／commit |
| repo + summary | Git 保留摘要、有效決策與穩定索引 | raw evidence 放獨立 store；摘要可自行解讀 |
| local + ignored | 個人暫存／單機續作 | 標示不可保證跨機器接續；重要輸出另存持久位置 |
| external filesystem | 團隊共享儲存或指定工作盤 | 明確可用性、可寫權限與備份責任 |
| provider | GitHub、Azure DevOps、Jira、Gitea 等 | adapter 宣告實際支援的資料／附件能力；本地副本僅作 cache |

改 `tracking` 不會自動讓已 tracked 檔案消失；工具應產生 `.gitignore`／搬移／取消追蹤的具體計畫，需專案採納。workflow 開始時保存有效 store binding 與格式版本，避免途中因改設定失去狀態；active workflow 搬家是獨立操作。

不再強制 `.dev/workflows` 留固定 locator。改用穩定 artifact ID 與已設定 store 的索引解析；索引可小型生成。每個 record 最小保留 ID、kind、owner、schema version、status、時間、關聯、entrypoint。組織型 skill 自行擁有細部 task/state schema，common core 不管理每一種 task 欄位。

### I/O 分類

`scratch_root` 容納可丟棄 build、解包、logical fixture；RAM disk 可用於此類資料。`durable_test_root` 只供需要真實檔案系統／持久性的選跑測試。續作 checkpoint、migration backup、已完成工作報告不可放到易失 scratch。

每次 I/O 工作只建立唯一子目錄，cleanup 僅刪除該子目錄；工具不得探索磁碟並自動選 RAM disk。保留極少數測試分類與 containment 工具即可，不以擴建大型分類治理系統作為使用 RAM disk 的前置工程。

## A4. ADR、Lesson 與規範落地

### 兩個可獨立使用的能力

| 能力 | 最小資料 | 讀取行為 | 寫入／生命週期 |
| --- | --- | --- | --- |
| ADR management | 決策問題、範圍、選項、取捨、決定、狀態、決策者／依據、後果、關聯 | 依作用範圍與狀態查詢；返回當前決策及必要 rationale；呈現互相矛盾的有效決策 | proposed → accepted/rejected；accepted 可被後續 ADR supersede；不覆寫舊決策的歷史理由 |
| Lesson management | 觀察情境、證據、可重用結論、適用／不適用條件、可信度、後續處置 | 依症狀／條件查找；區分觀察與已確認原因；不把相似案例當作當前根因 | candidate → active；可 promoted／superseded／retired；不自動建立規範權威 |

既有專案可能使用 MADR、自己的 Markdown 或線上 ADR。skill 接受模板 binding 與欄位 mapping；機械工具驗證最小 metadata，主要論證仍由人／agent 判斷，不為了格式重寫所有歷史 ADR。

寫入前先查詢相似 active record；有相同結論就更新 evidence 或建立關聯，不每次 workflow 再複製一則 Lesson。讀取先看相關領域與當前狀態，按需展開來源；不在每次 task 預載所有 ADR、Lessons 和工作歷史。機械索引可重建，讀者需能定位實際權威文件。

### workflow 的回顧步驟

組織型 skill 在完成或重要失敗後，回答四個有界問題：這次觀察到什麼、哪些結論有證據、什麼值得跨任務保留、哪個 owner 應承接。先沿用 workflow 內的簡短步驟，只有當回顧本身需要獨立重用時才另拆 retrospective skill。

| 回顧結果 | 合適去處 |
| --- | --- |
| 一次性進度、未確認猜測 | 工作摘要，或明確標為待確認 |
| 可重用經驗／環境條件 | Lesson 候選 |
| 架構／權衡選擇 | ADR 候選 |
| 已知缺陷與待做改善 | backlog／線上 Issue 候選 |
| 已成熟、需持續執行的規則 | 專案 standard／runbook／自動檢查候選 |
| 沒有新知 | 簡短記錄 none，不製造文件 |

發現候選不等於修改其他系統。已授權的本地草稿可以完成；若要採納新規範、改產品或發布到線上，需要在當次授權範圍內執行，不能因為 workflow 要結束而自動擴權。

### 從知識到有效規範

```text
觀察／工作證據
   → Lesson 或 ADR 候選
   → 檢查適用範圍、反例與現行規範衝突
   → 產出具體規範／runbook／tool 的變更提案
   → 專案採納
   → 更新唯一有效規範、必要工具與導航
   → 回填來源與 supersession，檢視舊紀錄能否壓縮
```

ADR 的 accepted 表示特定決策已採納；團隊可規定其決定本身就是權威。對日常 agent 行為而言，仍應把需反覆載入的有效規則放在一個精簡入口，並引用 ADR。Lesson 不因出現頻率高就自動成為規範。promotion 是一組一致的變更，不是把舊文件狀態改成 promoted 就結束。

每個 promotion 最少交付：目標規範路徑、具體 diff、適用範圍、來源、取代的規則、採納依據，以及必要時的驗證。若只是人類判斷型準則，不強迫新增程式測試；若能機械判定且錯誤成本足夠，再將其放進現有工具。

## A5. PR、backlog 與 provider

### PR skill

PR skill 擁有的是「把已存在的變更整理成可審查提案」的能力：讀取 base/head 與 diff，說明問題及最終行為、scope、相關工作項、實際驗證結果、必要風險及後續事項。依專案的 PR 模板與語言生成，避免每個組織型 skill 各寫一份 PR 規則。

操作可分 `prepare`、`create/update`、`inspect`、`merge-readiness`；實際 merge 為明確選定操作。工具記錄內容綁定的 head；變更後更新摘要與驗證，不沿用過時的「通過」文字。沒有驗證就說未執行；PR 建立不代表已 merge，也不代表 issue 必然應關閉。

第一版只實作一個有實際需求的平台，並宣告其他平台未支援。共同結果可包含 PR URL、平台、head、狀態；平台 approval/status 欄位由 adapter 保留，不把 GitHub、Azure DevOps、Gitea 的語意硬壓成同一套。Jira 主要承接 work items，不預設其提供 PR hosting。

### Local file backlog skill

提供穩定 ID、去重查找、create/read/update/list、狀態轉換、來源及 workflow 關聯。用一個 record 一個檔案降低合併衝突；索引生成，狀態欄位不再和人工總表競爭。工作流以 ID／URI 關聯，不把實作日誌全部塞進 backlog。

可採最小 open → active → done/cancelled，團隊可提供有驗證的狀態 mapping。done 只表示此工作項完成，不自動表示 merged、released 或 adopted。需要多人同時寫同一 record 時，使用版本／內容摘要進行樂觀衝突檢查。

本 repo 的 `.dev/backlog` 現為凍結歷史。新能力是供專案選用的 provider；不為了 dogfooding 而取消現有歷史凍結或自行改掉本 repo 的 GitHub authority。

### Provider 邊界

共通介面先只包含實際用得到的 get/list/create/update/link 與 optional attachments/export。每個 provider 宣告支援的動作、讀寫一致性、revision/etag 與 rate-limit 行為；權限不足是明確結果。用 stable internal ID + provider ID mapping，不依標題或可變 URL 當身分。

一份工作紀錄只有一個可寫權威來源。離線 cache 清楚標示 stale；同步衝突以 expected revision 偵測，不能自動雙向覆蓋。跨 local／provider 遷移先匯出、驗證關聯、建立新 mapping，讀回成功後才切換 authority。這比一開始做全平台雙向同步小得多。

## A6. Schema、工具與 migration

借用資料庫 migration 的「版本、明確轉換 edge、checksum、已執行記錄」，不照搬全域 DB migration engine。framework package version、skill version、record schema version、已安裝 configuration version 是不同軸；一個文件加了欄位，不代表所有 skills 都需要升 major。

### 每個 schema family 的交付條件

| 資料類型 | 合理工具能力 |
| --- | --- |
| 人工／agent 維護的 record | create/inspect/validate，具明確欄位／狀態操作的 update |
| 可推導的 index／catalog | regenerate/check；避免開放任意編輯衍生欄位 |
| execution observation／receipt | 由實際 producer 產生；reader/validate；不可任意補成成功 |
| 不可變歷史證據 | 按原版本讀取或投影；保留原件，不要求 mass migration |
| provider-native record | adapter 負責 API／版本映射；本地 schema 描述 projection |
| schema 改版 | convert、regenerate、re-execute、preserve 或明確 unsupported 的其中一條路線 |

有 schema 不等於每種操作都合法；例如不可變 receipt 沒有 update 是正確設計，但仍需要 reader／validator 與版本策略。所有常見可寫機械欄位應由工具處理，避免 agent 手填 ID、時間、hash、相對路徑與索引；人／agent 負責內容與判斷。既有 #320 成果可用於這個分工，不必重新做另一套 authoring core。

首次實作按需求選一個 family。共用 primitives 只處理 strict parsing、序列化、containment 與錯誤，family owner 保留語意。拒絕「通用 JSON/YAML 任意 set field」成為主要寫入面，也不為所有自然語言文件建立複雜 schema。

### 一次轉換的必要行為

1. 讀 source version、checksum 與 scope；未知版本回報未支援，不猜欄位。
2. `plan` 計算純結構轉換、預覽 diff、標示資料丟失／語意待決項。
3. `apply` 重新確認輸入未漂移，先備份將變動的專案資料，再完成輸出驗證與受限寫入。
4. 保存簡短 migration record：edge ID/version、input/output digest、工具版本、結果及備份位置。
5. 重跑可判斷已套用；失敗回復或留下可恢復狀態。不可逆轉換提供 restore 備份，不能假稱任意 downgrade 都可行。

可識別的專案 extension namespace 需原樣保留；未知客製結構、註解無法保存或可能丟失的欄位，輸出具體 reconciliation 計畫，不靜默丟棄。保留 extension 不等於相信未知欄位能改變工具權限或執行行為。

不在原件補寫從未存在的使用者核准或執行紀錄。需要重新執行的結果就產生新紀錄並引用舊件。初期只維護明列的當前 edges；一條 edge 改了才跑它的 tiny positive/negative fixtures，避免版本乘積矩陣重新長回來。

工具可以先是 `python ...` 或現有 shell entrypoint，命令的輸入／輸出與錯誤穩定比先選 Rust／Go／.NET 更重要。CLI 若只是統一入口，可重用既有工具；只有量測或部署需求證明需要時才更換 runtime。

## A7. 更新、可替換 core 與低 I/O

### 三類變更分別管理

| 類型 | 權威與行為 |
| --- | --- |
| Package delta | 機器 manifest：所選檔案、digest、依賴、增加／替換／刪除；只操作 installer 擁有範圍 |
| Project-data migration | owning skill 的已支援轉換；配置／自訂 record 有獨立 plan 和 recovery |
| Migration note | 人類可讀的差異、原因、breaking change、需要採納的行為；不直接執行其散文指令 |

核心替換流程：驗證取得的 artifact 與預期來源 → 比較 installed lock／本地 drift → 生成變更計畫 → 在 staging 準備變動元件 → 執行已採納的資料轉換 → 更新 activation 與 runtime projection → 驗證最小可用狀態 → 更新 lock，保留可回復前版。

不能把多目錄 rename 說成跨平台原子交易。Windows 開檔、跨磁碟移動或部分 runtime projection 失敗時，installer 必須保持舊版可用或提供明確恢復步驟。回復單位包含相互匹配的 core、lock、runtime projection 與本次轉換的專案資料版本；只還原 core 可能無法讀取新版資料。無法逆轉時，明確要求還原對應備份，而非聲稱 rollback 成功。可先以小型備份與 operation-specific recovery record 處理實際寫入，避免無需求地複製既有完整 transaction engine。

### 全量與差異策略

建議「全量 package 可重建，預設 apply 只寫差異」。未變動檔案的 bytes/digest 相同就不寫；一個可獨立元件變更就只替換該元件。乾淨重裝仍可選全量。staging 使用 scratch，持久備份不可放 RAM disk。

一開始可維持一個 release version + components manifest，而不是每個小 skill 都獨立發版。真的出現不同更新節奏再拆版本；否則獨立版本解析會重新引入大量相容性維護。

歷史到新架構的首度轉移，建議一次性 export／分類／seed／驗證，不承諾所有舊版自動連跳。已修改 core 與專案資料需人工 reconciliation。新架構之後只測和支援明列的 schema／installer 邊界。若 owner 選擇完全不提供自動 upgrade，就可以取消 upgrade engine 與其測試，改成取得新 core + 明確 custom 轉移指引；代價是使用者自己處理不相容配置。

## A8. 工作紀錄整理、壓縮與移除

保留價值依「是否仍有續作、決策、證據或團隊需要」判斷，不依文件是不是 YAML。壓縮有兩種：語意壓縮產生可續讀摘要；二進位 archive 減少熱工作集。把 zip 放進 Git 不等於降低 Git 歷史成本。

| 資料 | 建議生命週期 | 刪除條件 |
| --- | --- | --- |
| active workflow／未結案 assessment | 可做階段摘要；保留當前 scope、進度、待決與 evidence refs | 不因 TTL 自動刪除 |
| completed workflow 原始中間紀錄 | completion → extraction → compacted → archived → eligible-for-purge | 有完整摘要、未決項已轉交、關鍵證據另保留且可讀；再依專案 retention |
| assessment | 保留結論、基線、限制與 disposition；大原始證據外存 | 已無待處理 finding／audit hold；刪除前保留定位與必要證據 |
| ADR／有效規範 | 持續維護或標示 superseded | 不以 workflow TTL 刪除有效權威 |
| Lesson | 去重、整合、promote 或 retire | 無現行依賴，已保留必要結論與來源，依專案政策 |
| build scratch／重建型 cache | 完成後清理 | 確認為本次建立的可丟棄目錄 |

「已寫 ADR／Lesson」不足以證明原始證據全可刪。先區分可重建操作紀錄與不可替代事實。只有結論、未解除的引用或專案義務仍需要證據時，才保留 bounded evidence packet 或可存取外部來源；一般可丟棄流程可能只需可自行解讀的完成摘要。清理工具列出每件預計動作、理由、referencers、目標與可恢復性，提供 preview；有未決工作、不可解關聯、保留義務或必要來源不可用時保留。

摘要最少有：目的、subject/version、結果與失敗、目前有效決策、未完事項及承接 ID、必要證據位置、archive 位置及完整性資料。以 stable ID 解析搬移，留下小型 tombstone／redirect，而不是讓現有連結斷掉。已壓縮摘要不假裝與原始證據同等完整。

移至外部 provider 後須 read-back／試讀才可清理本地權威副本；平台附件大小、保留期限、export 與權限須先確認。初期選一個 provider 或 filesystem archive 即可，不把支援 Jira／Azure DevOps／GitHub／Gitea 當作同時完成的前置條件。

Git 中刪除檔案可縮小 checkout 與日後 diff，但通常不移除歷史 blobs。要縮小既有 repo history 需要另行 archive repo、history rewrite 等專案決策；本提案不預設重寫 Git 歷史。先避免繼續把大量 raw artifacts 放入 Git，通常更直接。

## A9. Source repo 與 dogfooding

| 結構選擇 | 優點 | 成本／建議 |
| --- | --- | --- |
| 保持產品 source 在根 `.ai`／`.dev` | 暫時無搬移成本，修改立即影響自用 | 繼續混合產品、source 治理和專案資料；難以直接驗證真正成品，適合作為過渡 |
| 單 repo，產品放 `src`，根目錄安裝成品 | 所有權清楚；同一 PR 可調 source 與必要工具；可真實 dogfood | 需要小型生成／安裝步驟；本案建議選項 |
| 產品與 dogfood 分 repo | 隔離最強，可獨立維護 | 多 repo 版本協調與發版成本提高；目前沒有足夠證據需要先拆 |

發行物也不必只有一種：單 skill 適合獨立能力，選配 bundle 適合組織型流程，runtime plugin 是同一 source 的平台包裝。避免先固定所有技能必裝的單體 bundle，也避免尚未證明需求就讓每個 skill 獨立跑一套發布流程。

```text
repository/
  src/
    skills/                 # 唯一可編輯的產品 skill source
    shared/                 # 少量共通協定／工具 primitives
    profiles/               # capability bundles，不含此 repo 歷史
    adapters/               # 必要的 runtime/provider projections
    distribution/           # 可生成成品的 manifest／build 設定
  tests/                    # 留下的 focused tests 與小 fixtures
  tools/                    # source 開發、build、release 工具
  docs/                     # 對使用者的產品說明
  .ai/core/                 # 安裝的 released 或明確 development 成品
  .ai/custom/               # 本 repo 的設定、規範與補充
  .dev/                     # 本 repo 的 requirements、ADR、work records
  dist/                     # 生成 staging，ignored
```

此樹是方向，搬移清單要另做 bounded implementation。核心原則是打包 allowlist 只取 `src` 選定內容；不把整個 repo 複製再用黑名單刪除。source release/CI maintenance 在 `tools`，下游會用到的 skill 工具在 skill 套件；不要只改資料夾名稱卻延續混合所有權。

日常用 stable dogfood profile，lock 指向已選定成品。開發某個 skill 時在分支上產生 development profile 安裝結果，包含候選技能；驗證其讀寫 custom、artifact roots 與 providers 的行為，再回寫 `src`。不能修生成的 `.ai/core` 卻忘記 source。

若新 framework 壞掉，維護者仍可透過普通 shell、Git 與外部工具修 source；啟動／修復不應強制要求壞掉的 framework 先自我通過全部流程。這也是避免自我治理持續拖慢產品改進的重要界線。

先維持一個 repo、一份 source、一個 manifest。之後可以產出 standalone skill、選配 bundle、runtime plugin；不為了未來的 installer 先拆出多個 Git repositories。生成檔是否 commit 應由各 runtime 的 clone 即可用需求決定，但不得成為第二份手工 source。

## A10. Matt Pocock 參考的可用部分

該專案將技能成品、維護資料及發布工具區分，並以 development/release 選取區分候選與出貨內容；適合作為本案 `src` + dogfood 的方向參考。其 setup 讓專案保存 issue tracker 與 domain 資料，也支持 skill 消費專案設定的思路。[外部來源與快照](evidence.md#external-sources)

但它仍有技能呼叫關係、runtime 特定假設與同步清單工作，不能據此推論技能天然零依賴。其 dev symlink script 也不是跨平台安全 installer 的範本。建議學習「產品邊界與小工具」，把本 framework 特有的 schema、custom preservation 與 workflow storage 做成最小擴充。

本案不因看到 Changesets 或某個 plugin 形式，就直接指定同樣的發布工具。先決定 release unit、supported runtime 與安裝契約，再選能生成那些成品的最小工具。
