# dotnet 更名與公開版升級相容性方案

Assessment: `ASM-20261109-23-dnr`。本文件是待確認的遷移方案；尚未實作更名、生成新 catalog、安裝或執行升級。

## 已查證的發布物

直接下載 GitHub 公開 Release 的 ZIP、checksum、release-manifest；比對 GitHub asset digest、ZIP checksum、manifest archive hash、內含 content-hashes 的每個列出成員，以及 engine.json／engine-pin.json。只讀取封存內容，未執行封包內安裝器。

| 對象 | 固定來源 | 發布 manifest | Catalog／Engine | dotnet-backend／engineering-common | knowledge 成員／resources |
| --- | --- | --- | --- | --- | --- |
| [v0.21.0](https://github.com/YuChia-Wei/ai-collaboration-framework/releases/tag/v0.21.0) | `5fe8d307ce8c337463088f2abb4f2a945262a56d` | `framework-release-assets/2` | 1／2.0.0 | 0.1.6／0.4.0 | 246／245 |
| [v0.22.0](https://github.com/YuChia-Wei/ai-collaboration-framework/releases/tag/v0.22.0) | `5aa7346e3d99cf4c7ad72ba91f1d81af5251f515` | `framework-release-assets/3` | 1／2.0.0 | 0.1.9／0.4.1 | 251／247 |
| 本次來源基準 | `c641602a50ee17016ea1729897625aefe708af2a` | 不以來源 checkout 代替發布物 | current Engine 2 source | 0.2.1／0.4.2 | 122／121 |

兩個公開 ZIP 都有 `catalog/`、`engine/`、`engine-pin.json`、`content-hashes.json`、`README.md`，沒有 `generation/`。其 packaged `project_layout.py:14-15` 明定 canonical `.ai/project` 與 legacy `.ai/custom`；`catalog.lock_document` 寫入 lock 2，installed resource reader 接受 lock 2。這支持「v0.21.0 已採目前這一代結構／安裝契約」的判斷，不支持「所有舊專案都已遷移 .ai/project」或「現在改名可直接成功」。

兩版各 29 個 engine members；ZIP 分別有 497／527 個成員。content-hashes 列出 496／526 個成員，全部 hash/size 相符；唯一不列於自身清單的是 `content-hashes.json`。完整來源、SHA-256、catalog identity、觀察範圍見 [發布物證據](evidence/release-comparison.json)。

另外比較兩版封包與目前來源的 8 個相關函式 AST：`load_content_package`、`desired_shape`、`resource_bindings`、`resolve_selection`、`lock_bytes`、`lock_document`、`_lock_bytes`、`member_delta` 均相同。這是有限的靜態相容證據；未比較或執行完整引擎，不能替代實際 upgrade。

現有 F 槽筆記描述的是 `c641602a...`／`0.0.0-rc.217984088559855` snapshot 預覽。候選名稱 `0.23.0-rc.1` 尚不是本評估已查證的 tag 或成品。此次沒有改動 F 槽，沒有重新主張筆記中的 CI／安裝結果是本次執行。

## 建議的識別策略

建議一次建立明確的新 package identity，配合可審閱的一次性遷移清單。利用現有 derive／inspect／plan／apply／inspect 契約，不新增 alias resolver、常態 migration service 或另一套安裝器。

| 層次 | 建議處置 | 相容性含義 |
| --- | --- | --- |
| Source root | `src/knowledge/dotnet-backend` → `src/knowledge/dotnet` | 逐檔目的地見 [122 列清單](file-disposition.md)，不是單純字串替換。 |
| Package ID／version | canonical ID 改為 `dotnet`；提議 knowledge 版本 `0.3.0` 承接 0.2.1，此版本仍待確認 | 新 ID 是明確 breaking selection change；此處不是 Framework Release 版本配置。 |
| Installed root | `.ai/core/knowledge/dotnet/` | 讓既有 Engine 依舊 lock 的 ownership 刪除舊 managed members、增加新 members；不直接 rename managed 目錄。 |
| Rule IDs | 保留既有 11 個 ID | 移動 owner path 不創造新規則；不把未 packetize 的指導假造為已採規則。 |
| Catalog resource ID | 保留 `engineering-rule-catalog` | binding 的 package 改為 dotnet，但 rule ID／selected authority 仍需逐項維持原意。 |
| 其他 resource IDs | 新包繼續採 `member:<新相對路徑>` | 每個舊 ID 先依逐檔清單分類為一對一、合併／拆分、retired；不留指向不存在路徑的假 alias。 |
| Catalog identity | distribution catalog identity、hashes、source SHA 由正常 build 重新產生 | 不手改 release catalog／lock 的摘要。 |
| Knowledge catalog `catalog_id`／既有 `technology_profile` | 此階段保留 `engineering-rule-catalog-dotnet-backend` 與原 `dotnet-backend` 規則 profile token | 這些標示原規則採用範圍，與新 package ID 不同；不因套件改名把 DDD、GWT/BDDfy、mock 或 broker 預設普遍化。 |
| 新 common reference 的 metadata | 只對已分離且確實沒有固定 profile 的普通 guidance 使用 `technology_profile: null`；其餘保持原條件 | `null` 只是可供不同 target 選用，不等於 normative adoption。每個 reference 仍按任務、app type、architecture/integration 決策載入。 |
| Tool／capability identities | 保留 `dotnet.mechanical-validation`、DBA labels、7 個 template IDs、SnippetTool 與工具安裝位置 | 知識改名不改工具 API、不將 reference-only 變成 analyzer、不重註冊使用者範本。 |
| 歷史 provenance | 保留原 source_identity path、commit、舊 release notes／assessment／workflow 引用 | 只改 active current-owner paths；歷史不全域 replace。 |

保留原 profile token 是保守的相容決定：新版 README 用人可讀的「選用 DDD/CQRS 與既有 .NET 規則 profile」說明其界線。若要把原規則重新分配為多個新的 profile ID，必須另列語意差異與每項 adopted binding 的處置；不能從本次分類推定已核准改規則適用範圍。

不建議同時再發一份完整 `dotnet-backend` 相容 package：它會增加第二份知識、釘版與維護面，且目前沒有確定的 downstream 舊 ID 支援要求。舊 release 的實際位元組維持可取回。若後續證據顯示某個支援中的使用者無法遷移，再針對該目標決定延後更名或 bounded bridge，不現在先做一套 alias 平台。

## Resource 與 skill 連動

目前資源共有 121 個，其中一個是 `engineering-rule-catalog`，其餘 120 個是 `member:<path>`；`content-package.yaml` 本身不是 resource。這些 source resource ID／path 與六個 binding 的精確原值保存在 [identity inventory](evidence/identity-inventory.json)。

對照規則：

1. 單一搬移或保留：`member:舊路徑` → `member:新路徑`。普通引用可機械化產生候選替換；採規則的權威仍要人確認。
2. 多檔合併：只有確認原來所需內容完整保留時，才改選目的 resource；合併後檔案包含較多知識，不代表允許載入整個原目錄。
3. 一檔拆分：依該 binding 的 operation／purpose 選擇目的 resource 子集，不把全部目的地自動加入 allowlist。逐檔清單列出所有可能目的地，這不是每位使用者的選擇。
4. 退役的 role YAML／prompt：沒有 executable alias。若 target 仍以該 resource 或路徑呼叫角色，應回報 unavailable 並改選現行 skill／明確的技術 reference；保留原資料直到 owner 核對。
5. 三份 legacy compliance 文件一對一搬到 `references/legacy-dotnet-compliance/`，保留其語意及 explicit legacy 選用。缺少原 helper 仍 unavailable，不以 modern validator 取代舊 100% gate 證據。

六個 source skills 都精確消費 `dotnet-backend@0.2.1`，皆 optional／missing=unavailable。它們需在同一 coherent change 中改 package/version/resource allowlist、提升自身 package version，並更新 distribution component pins；不是改 metadata schema 版號。

| Skill | Binding ID 保留 | Operations 保留 | 新 resource 內容集合（每列仍需 explicit allowlist） |
| --- | --- | --- | --- |
| code-reviewer | `dotnet-review` | review | catalog、review-routing、core C#/DbC、rationale、對應 Aggregate/Use Case/API/repository/test；對 YAML 實際可選 route 補足其直接 owner，不能靠 link 自動擴權。 |
| domain-model-designer | `dotnet-domain-model` | design, review | catalog、DbC、rationale、aggregate。 |
| local-change-implementer | `dotnet-local-change` | implement | catalog、rationale、usecase/controller/aggregate/repository/test、generation；移除已合併 relationship 舊 ID。 |
| slice-implementer | `dotnet-implementation` | implement | 前述內容加 DbC／transactional messaging，維持所選 slice 模式。 |
| software-architect | `dotnet-software-architecture` | design, review | catalog、reconstruction／DbC／rationale／usecase／controller／repository／messaging／project structure。 |
| test-designer | `dotnet-test-design` | design, review | catalog、rationale、test standards；需要 semantic probe 時明列，不由導覽默認加入。 |

目前 code-reviewer allowlist 沒有涵蓋 review-routing 所列的全部 reference（例如 `review/test-scenario-review.md`），而 metadata 明寫 links 不擴大允許清單。實作時逐 route 核對所需資源，保留 unavailable 行為；不直接選整包。Source presets 目前沒有預設選用 dotnet-backend，這次也不新增預設採用。

本專案安裝的 `.ai/core/skills` 使用較舊 0.1.6 knowledge pins，而 `.ai/project/installation.json` 的 knowledge/bindings 為空；這是另一個 installed subject，不是本次來源的錯誤副本，不手改 generated projections。Self-installation 要使用另外選定的新 catalog／engine。

## Package 外必須同步處理的引用

| 位置 | 具體工作 |
| --- | --- |
| `src/distribution/manifest.yaml` | component ID／version／source、全部 destinations、skill dependency pins；generated catalogs 由 build 產生。 |
| `src/skills/{code-reviewer,domain-model-designer,local-change-implementer,slice-implementer,software-architect,test-designer}/skill-package.yaml` | 以上六個 exact bindings、resource closure 與 skill package version 同步。 |
| `src/knowledge/engineering-common/references/TECHNOLOGY-SELECTION-POLICY.md` | 分清新 dotnet package 與保留的 dotnet-backend 規則 profile；若正文有變，依正常 package version/pins 連動，不重寫歷史。 |
| `.github/scripts/build-generation.py:23` | guides root 改新來源；保留 DELIVERY.md 作 bundle README、snippet README 作交付說明的雙使用情境。 |
| `src/tools/dotnet/generation/snippet-tool/SnippetTool.csproj:24` | 更新 Include 指向新 README；保留 build/publish 輸出位置。 |
| `.github/workflows/dotnet-knowledge-templates.yml:7` | 將舊 domain-contracts 文檔 filter 對應到新 testing/domain-contract-examples.md；不可讓搬移後漏觸發必要 job。 |
| `.github/workflows/native-tools.yml:7` | 改新 tooling filter，維持原 native tooling 觸發語義。 |
| `src/tools/dotnet/check-coding-standards.sh` | 它明示 source-checkout structural checker，且假設單一 standards dir 及舊 headings。更新既有路徑表與必要結構檢查；移除只為舊佈局存在的硬編碼，不建立新文件品質 gate、行數標準或為過測試保留重複正文。 |
| `src/tools/dotnet/README.md` | 更新生成知識位置；工具安裝路徑/API 不變。 |
| `docs/README.md`、`docs/installation.md`、`docs/knowledge-packages.md`、`docs/maintaining-documentation.md` | 更新 current links／selection 示例／相容界線，明列一次性遷移；舊版本示例只在明示版本情境保留。 |
| 六個 `docs/skills/<skill>.md` 與 `docs/skills/domain-architecture-migration.md` | 更新 current package/version/resource 路徑，保留 retired architect 的歷史意義。 |
| `tests/framework_next/test_contracts.py`、`tests/schemas/schema_support.py`、`tests/tools/test_retired_asset_routes.py`、`tests/dotnet-generation/templates/README.md` | 更新受影響 fixture／schema root／route assertions／參考連結；檢查其真實意義，不能一概把 retired-route 反例也換新字串。 |
| `docs/installation-rc4.md` 與固定 .dev／release 歷史 | 保留原版路徑與命令；其目的就是描述舊版，不應全域改名。 |
| 目標自有 `AGENTS.md`／README／docs／自建 skill/sub-agent／tool config／scripts | 先列出文字命中與分類，再由目標 owner 核對採用與替換；不可由 installer 自動改寫。 |

這份清單由目前 tracked active paths 的有界 literal search 得出，未宣稱已發現所有下游引用。發版主對話和 dotnet-mq-arch-lab 的實際測試仍各自持有其觀察。

## 從兩個公開版本遷移

兩條路徑都以真實已安裝目標的 lock／managed bytes／project state 為起點。不要求先升到 v0.22.0 或目前 snapshot；預設評估直接升到最終被選定的新包，只有實測顯示必要時才增加中繼步驟。

1. **保存起點。** 記錄已安裝版本、raw lock hash、catalog identity、adapters／skills／knowledge／sub_agents／bindings、project-owned 與未知內容。保留原封包及其 engine pin，供既有 recovery 程序使用。檢查有無 incomplete maintenance、managed drift、新舊 project roots 衝突；不以刪檔解除。
2. **選定新產物。** 使用實際存在的候選或發布包，同包 catalog／engine／pin。發版版本相同、Engine version 同為 2.0.0 都不允許混用其他 SHA 的 engine files。
3. **準備新 selection 副本。** 以新 catalog identity 為父身分；將 knowledge ID 改為 dotnet，保留其他已選能力。六個 source skill 的精確 pins 由新包提供。按上述規則翻譯舊 bindings 的 package/resources；保留 rule IDs、authorities、path selector、execution modes 及原 profile 意義。不是直接改 lock。
4. **檢視 0.1.x 已移除內容。** v0.21.0 有 130 個、v0.22.0 有 134 個成員在本次基準已不存在；這是本次更名前已發生的 examples/source-includes 退出。每個舊成員見 [公開成員對照](evidence/published-member-map.csv)。其中既有 copied source 已屬目標，不會自動升級；不存在完整等價 relay/projector/consumer 的項目明列無等價成品。
5. **derive 與 preview。** 用新 engine derive subset，inspect 舊目標，再 plan。確認舊 .ai/core/knowledge/dotnet-backend managed members 的 remove、新 dotnet members 的 add、runtime skill 投影變更、project edit intent 與 preserved_unknown。找出未轉換 ID 時接受 selection-unavailable／binding-unresolved 的拒絕，不放寬 schema。
6. **處理自有引用與 drift。** 普通 docs link 一對一可批次提出 diff；normative bindings／一對多合併／自建 role／copied code 需人工核對。不覆蓋改過的 managed 文件或未知同名檔案；先抽取保留必要客製。新舊包同時存在不表示可以繼續執行舊角色。
7. **核准並 apply。** 依實際授權執行既有 plan/apply 與既有恢復程序。若使用支援的 project_edits，指定精確內容與 preimage；不能假設 installer 會搜尋或決定自有引用。完成後 inspect，確認 managed consistency、選擇及保護內容。Lock 由引擎生成。
8. **讀取與行為驗證。** 在實際 selected skills 的 resource allowlist 內讀得到新 owner；對目標正在做的工作核對選擇正確，不自動載入 DDD/ES/MQ。若另選 generation 或 RefactorTool，使用其獨立成品及安裝契約，不能由 knowledge 升級推定已安裝或已驗收。

## 獨立升級驗證與機械化界線

本次只規劃，沒有執行兩條升級。後續獨立試驗限兩個公開基準及一個明確新候選，不加入標準化 suite 或常態大矩陣：

**大量 I/O 的執行安排。** 後續驗證取得實際授權，且 preview 管理對話完成其清理工作後，執行前讀回 `F:` RAMDRIVE 的剩餘容量及所選路徑狀態。優先在 F 槽建立這次驗證專用的新暫存根，放置 ZIP 完整解包、一次性舊版安裝／升級目標，以及必要的 scratch、staging、recovery 與測試／建置中間產物。各角色根依安裝器契約保持分離，不巢狀互覆；預先檢查實體路徑與 reparse-point，不把先前 F 槽的個別預檢處理泛化成繞過路徑保護。保留既有 preview，由其管理對話負責清理。若容量或路徑預檢不足，先回報具體缺口，評估逐案執行或明確記錄替代位置，不擅自清掉 preview。下載來源、hash、命令結果、失敗／恢復狀態與結論保存到持久儲存；F 槽不作唯一證據來源。此安排只補充方案的執行條件，沒有提前授權升級、搬移或清理預覽。

- 用 v0.21.0 真實 asset 建一個可回復的代表安裝，再直接升新候選。
- 用 v0.22.0 真實 asset 建一個代表安裝，再直接升同一候選。
- 選能涵蓋此差異的 knowledge、六個受影響 skill、兩個 adapter 與少量 bindings；同一安裝能覆蓋兩個 adapter 時不拆出排列矩陣。
- 讓其中一條包含 project-owned 普通引用與 normative authority，另一條包含 managed drift／未知同名檔／舊 resource ID 的拒絕情境。只測此遷移觸及的拒絕；不是全面復原或平台驗收。
- 一次記錄真實 plan/apply/inspect、old/new identity、資料保留、失敗與限制。只因失敗修正或 relevant artifact 改變才重跑受影響部分。dotnet-mq-arch-lab 若測的是目前未更名 snapshot，其結果只能覆蓋 rename 前路徑。

可機械化：ZIP/hash/inventory 比對、exact package/version/resource ID 是否存在、old/new destination delta、六個 allowlist closure、文字引用候選、受管／自有檔案 pre/post hash、plan/readback 結構。使用現有 CLI，加這次一次性的資料整理即可。

保留人工判讀：合併後的規範是否等價、target 是否採用 DDD/ES/DbC/BDDfy、factory/broker 舊限制、例外／交易語義、哪一個 split resource 才符合 binding、使用者 copied code 的真實契約、完整業務驗收。無法可靠機械化者不新增 heuristic gate。

未取得 final renamed artifact、真實舊版安裝、實際 apply／readback 前，不宣稱升級相容、無資料遺失或 release-ready。
