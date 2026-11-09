# .NET 知識精簡、更名與舊版遷移評估

Assessment: `ASM-20261109-23-dnr`
Owning skill: `ai-context-auditor@0.1.0`
Subject: `main@c641602a50ee17016ea1729897625aefe708af2a`
Assessment artifacts: `codex/assessment/asm-20261109-23-dnr`

## 結論與待確認方案

建議將 `src/knowledge/dotnet-backend` 整理為 `src/knowledge/dotnet`，用同一知識包的按需資源區分 .NET 共通知識、Web API、選用 DDD/CQRS、persistence、messaging 與 testing。現有 122 個檔案可收斂為 **55 個具體目的檔案**：18 個保留／更新、33 個搬移、52 個合併或拆分合併、19 個刪除候選。這是逐檔清單的靜態計數，不是已完成的精簡，也未量測 token／閱讀成本。

建議 package ID 同步改為 `dotnet`，提議 knowledge version `0.3.0` 承接現行 0.2.1，採明確的一次性 selection／resource 遷移。既有規則 ID、規則 profile token、target authority 及原政策限制維持原意，不用全域字串取代所有 `dotnet-backend`。此 package version 提議與 Framework Release `0.23.0-rc.1` 的候選名稱是兩個不同身分，均不是此評估已發布的成品。

- [122 列逐檔處置清單](file-disposition.md)：每個來源、動作、目的地及必須保留的內容。
- [相容性與升級方案](compatibility.md)：package/resource/catalog/skill/selection/lock、外部引用、v0.21.0／v0.22.0、F 槽執行安排及獨立驗證。
- [256 列公開成員對照](evidence/published-member-map.csv)：兩個公開包和目前來源的每個成員，分清更名前已移除的內容與本次提案。
- [發布物證據](evidence/release-comparison.json)／[目前識別與 binding 清單](evidence/identity-inventory.json)：固定 SHA、驗證範圍、精確版本與 resource IDs。

這次授權限調查、提案與保存成果。來源、installed projections、F 槽 preview、tag/release 均未改動，沒有建立 implementation workflow、提交或外部發布。使用者確認這份具體方案後，才進入來源實作。

## 範圍與來源

核實的目前來源共有 122 個 Git 追蹤檔案：legacy-guidance 37、standards 22、guides 21、tooling 15、references 9、shared 5、design 4、templates 3、review 2、requirements 1、根目錄 3。Package metadata 同樣列 122 members；resource 是 **121**，排除 metadata 自身。

讀取範圍涵蓋所有 122 個檔案的處置用途、37 個 legacy 檔案與 67 個主要內容檔的正文、root/tooling 契約及直接引用、六個 consuming skills、distribution selection/resource/lock/delta 的相關函式、明確的 package 外 active references，以及兩個公開 release ZIP。未審查每個工具／schema 的完整行為，未以搜尋無結果推定所有下游引用不存在。

程式探索先使用 codebase-memory graph；四個主要 distribution 檔案回報 best-effort metadata match，未從 graph 推定整庫 SHA 或完整覆蓋。重要結論回到 c641602a 的 tracked source／實際 ZIP；source HEAD 始終固定，未變更 assessed bytes。知識文字、metadata、設定與路徑引用使用有界 Git inventory／literal search。

F 槽既有 `F:\AICF-Preview-Notes\596-c641602a\verification.md` 只作已歸屬的歷史證據：記載 snapshot `0.0.0-rc.217984088559855` 在先前 preview 上的更新。它沒有證明本次規劃的更名升級，也沒有證明正式 RC tag／成品存在。另個 dotnet-mq-arch-lab 對話的執行結果未作為本評估已觀察的證據。

## 目標分類與載入方式

| 提案區域 | 目的檔數 | 內容與觸發 |
| --- | ---: | --- |
| 根目錄 | 3 | README、content-package、rule catalog；入口只選下一個相關資源。 |
| `core` | 4 | C# conventions、technology selection、host configuration、DbC；保留各自的 target adoption 條件。 |
| `tooling` | 17 | 現有 generation 三文件、reference-only validation 十二文件、development tools、Docker restore cache。 |
| `application-types/web-api` | 2 | setup 與 controller/HTTP boundary；只在實際 HTTP/API 工作載入。 |
| `architecture/ddd-cqrs` | 6 | overview、aggregate、usecase、project structure、reconstruction、reactor；只在目標採用該架構／角色時載入。 |
| `integration/persistence` | 6 | configuration、migrations、repository、mapper、projection、archive；依實際 persistence/read/write contract 載入。 |
| `integration/messaging` | 2 | transactional messaging、persistence/messaging 組合；不預設 transport 或完整 consumer。 |
| `testing` | 7 | canonical tests、profile testing、Gherkin storage、test spec、scenario review、reconstruction cases、domain contract examples。 |
| `references` | 8 | rationale、troubleshooting、identity bindings、design/review routes，以及三份明選 legacy compliance 參考。 |

Worker／Console 是之後可用的分類方向，目前不建空資料夾，不把 reactor、outbox 或 MQ handler 當作完整 Worker/Console 知識。跨 BC 的既有 broker 限制只保留在已採 profile；此提案沒有擴充完整 MQ consumer。

「放到 core」只表示主題可跨應用入口，不表示要求所有 .NET 專案採用該規約。已有的 GWT/BDDfy opt-out、NSubstitute 預設／target mocking、DbC、style、ES、dual persistence profile、Linux portability 與 UoW 等條件不因分類而變為新的普遍規則。

## 發現與處置

### F01 — 路徑是公開資源身分，單純搬目錄會破壞精確消費

**觀察，信心高。** `content-package.yaml` 的 121 個 resources 中，120 個 ID 為 `member:<path>`；六個 skills 以 `dotnet-backend@0.2.1` 精確列出允許資源。Distribution 在 `src/distribution/content.py:300-319` 驗證 package/resource/profile 與所需 rule；`catalog.py:192-215` 要求 selected ID 存在於新 catalog。沒有可由 directory rename 推定的 package alias。

**觸發／影響。** 舊 selection 或 binding 原樣送入新 ID 的 catalog，會失去 selected package 或 resource；手改 lock 又破壞其 candidate/catalog identity。相容機制不是把所有路徑搬好就算完成。

**提案。** 同一交付更新來源宣告、六個 skill pins、current resource references 與 build/CI 讀取點；target 選擇用副本逐項遷移，lock 由引擎產生。合併／拆分／retired resources 不做無條件 alias。完整處置在相容性文件。

### F02 — 通用路由和特定架構內容混在一起，allowlist 亦需一起核對

**觀察，信心高。** `review/review-routing.yaml:287-296` 的 general-csharp 指向 `standards/coding-standards.md`，後者標題及內容同時涵蓋 DDD/CQRS/ES、Wolverine、testing 與 style。`src/skills/code-reviewer/skill-package.yaml:46-61` 明定 links 不擴大 allowlist，但 YAML 其他 routes 還列到清單未涵蓋的資源，例如 `review/test-scenario-review.md`。

**影響。** 對一般 C# 工作可能載入過多不相關假設；若嚴守 allowlist，部分 route 的額外 reference 應維持 unavailable。這是靜態導覽與消費邊界的問題，尚無本次模型 runtime 行為驗收。

**提案。** general-csharp 改指 core 的共同語言內容；DDD、Web API、persistence、messaging、testing 由目標事實選路。每條可提供的 route 明列直接所需 resource；不把整包或每個相對 link 默認允許。

### F03 — Legacy 外殼可刪，技術差異與 compatibility duty 不能整批刪

**觀察，信心高。** 37 個 legacy 檔案中有 13 個 role YAML、4 個 review prompt、20 個其他技術 Markdown。YAML 明示 activation none／reference-only，例如 `legacy-guidance/code-reviewer/roles/aggregate-code-review-sub-agent/sub-agent.yaml:1-5`。它們仍在 manifest、metadata 與 `design/source-map.md:16-74` 中可達；四個 guides 另有明確 wrapper 引用。

**影響。** inactive 不等於沒有內容或沒有 downstream 引用。直接移除會同時失去 access-boundary/retry/event/HTTP test 等有用 checklist，並可能破壞既有 resource binding。

**提案。** 刪 13 個 YAML、4 個 prompt，以及已由 common reviewer 完整持有的一份 generic review playbook；其餘技術內容先併回對應 owner。另將三份 spec compliance 文件一對一搬到 explicit legacy references，完整保留 target-selected legacy gate、L1–L4、CBF/SWF、helper/report 語義。AGENTS 的 retained duty 與 `src/skills/spec-compliance-validator/references/legacy-intake.md` 不允許以現代 scoped assessment 假裝等價取代。

整體另外刪除一份明示過時的 `standards/coding-guide.md`，形成清單中的 19 個刪除候選；Git 來源歷史保留。

### F04 — 重複投影含有與現行 owner 不同的條件，合併必須保留裁決界線

**觀察，信心高。** `shared/common-rules.md`、`shared/testing-strategy.md` 與部分 legacy implementation 指導帶有較廣的 ES、Wolverine、PostgreSQL、exception／fixture 假設。現行 `aggregate-standards.md:14-21` 明確允許普通 Aggregate，ES 須明選；`transactional-messaging-standards.md` 把 provider／adapter 留給目標。Profile guides 也混有小寫環境例，與 `profile-configuration-standards.md:11-75` 的 casing/selector 契約不一致。

`guides/PERSISTENCE-CONFIGURATION-GUIDE.md:104-105` 有兩個 inline relative references，`../../standards/...` 會指到 package 外的不存在位置；它們不是可當作驗證成功的有效 owner 導覽。

**提案。** 用既有 canonical owner 消除過時重複投影；不是另造較寬鬆的新政策。原 profile 的 factory、MQ-only 與 named-broker restriction 仍保留，因 `standards/POLICY-RATIONALE.md:175-207` 明示它們的通用理由／範圍未解。此次只把未決問題放在單一可見處，不採用 static factory 或 HTTP/RPC 等替代方案。Controller 的 `Task<ActionResult<T>>` 與特定例外名稱保留為有界示例，不從舊 wrapper 推定新的唯一 API 契約。

### F05 — 機械驗證資料是 reference-only；工具交付與知識安裝分開

**觀察，信心高。** `tooling/on-demand-mechanical-validation/README.md:3-14` 明示無 executable provider／project／activation；provider identity 未知，capability `dotnet.mechanical-validation` 不是 NuGet 身分。其 12 個文件／schema／模板有各自契約，不應因「只是 reference」整批刪除或宣稱已交付 analyzer。

Generation 的三份說明由 build-generation 與 SnippetTool.csproj 使用；generation bundle 安裝到 `.ai/tools/dotnet-generation`，不受 framework.lock 的 knowledge consistency 結論涵蓋。

**提案。** 保留這 15 個 tooling 文件，只做需要的路徑／引用一致性更新；generation 既有 7 個 templates 與執行來源在 `src/tools/dotnet/generation`，不在知識整理中重複產生 executable code。F 槽預覽及工具發版由原負責對話持有。

## 規則與未決政策的保留

| 穩定 Rule ID | 新 owner 提案 |
| --- | --- |
| AGGREGATE-ES-001 | architecture/ddd-cqrs/building-blocks-reconstruction.md |
| ARCH-UOW-001 | architecture/ddd-cqrs/usecase-standards.md |
| CONTRACT-SEMANTICS-001 | core/design-by-contract.md |
| DELETE-PURGE-001 | integration/persistence/archive-standards.md |
| DELETE-SOFT-001 | architecture/ddd-cqrs/aggregate-standards.md |
| MAP-EVENTS-001 | integration/persistence/mapper-standards.md |
| MESSAGING-TX-001 | integration/messaging/transactional-messaging-standards.md |
| PROJECT-GRAMMAR-001 | architecture/ddd-cqrs/project-structure.md |
| TEST-BDDFY-001、TEST-GWT-001、TEST-MOCK-001 | testing/test-standards.md |

移動時保留適用條件、strength、scope、target adoption、anchor、normative text 的完整語義。相對連結若改變正文 bytes，依實際新 owner 重建 embedded text／source_file hash／catalog digest；原 source_identity 的 revision/digest 與歷史路徑保持 provenance。Unpacketized documents 也要同步 owner 路徑，不因不存在 rule ID 而忽略它們。

本方案不要求使用者現在解決 factory/broker 等既有未決政策：以保留現行採用與明示歧義為預設處置。只有後續要改這些政策，才另提精確選擇，不借更名順帶採用。

## 升級結論與證據分層

使用者所述「v0.21.0 已採目前檔案結構」經實際公開 ZIP 核對，在 Catalog 1／Engine 2／project-root 契約層次成立；v0.22.0 也是同一代。兩者不是 RC4 格式，沒有理由單憑版本較舊就要求走 RC4 recovery 或先破壞式重裝。

但目前來源已把 0.1.x 的 examples/source-includes 轉為另一個 generation/knowledge 分工：v0.21.0 的 130 個、v0.22.0 的 134 個 member 在 c641602a 已不存在。這是本次改名之前的差異。對照 CSV 將其逐檔列出並指出示例替代／無完整等價成品；copied code 不隨 managed upgrade 自動遷移。

8 個相關函式在兩版成品與本次來源的 AST 相同，只支持有界靜態相容性。兩條真實 upgrade、拒絕情境、資料保留、selected resource readback 與行為仍須使用最後選定的 renamed artifact 驗證，沒有被本次下載核對代替。

本次沒有啟動 source test suite。依 source policy 的 necessity decision，此差異只有 assessment artifacts；所需檢查是逐檔覆蓋、metadata/exact IDs、發布物 hash、引用與 assessment 結構。後續實作才按實際 diff 執行受影響現有測試、source hosted gate 及安裝／升級相關的固定 diff 獨立審查。獨立 upgrade 試驗保持一次性工作，不加入常態全版本／全 profile／全平台矩陣。

F 槽的後續大量 I/O 安排已納入相容性方案：先取得驗證授權與 preview 管理對話清理完成的實際狀態，再讀回 RAMDRIVE 容量，在獨立、分離的暫存根執行；持久儲存保留結果。這裡沒有授權預先清理 preview 或開始升級。

## 分工與主對話驗證

| 分工 | 選定角色／模型 | 產出及主對話處置 |
| --- | --- | --- |
| 67 檔主要內容 | project-semantic-governance-analyst；Sol medium | 完整逐檔提案、profile/route/衝突證據；主對話整合命名與保留界線。 |
| 37 檔 legacy | project-semantic-governance-analyst；Sol medium | wrapper/unique technical/legacy duty 分離；主對話選擇保留三個 legacy 文件而非先合一。 |
| identity/tooling/reference inventory | project-bounded-routine-worker；Luna medium | 六個 bindings、tooling tier 與引用盤點；主對話重做直接 YAML extraction，採用 122 members／121 resources 的確定值。 |
| 發布物、升級機制、整合 | 主對話 | 公開 ZIP 與 hash、8 函式比較、256 列舊成員表、122/122 覆蓋、package 外 build/CI 引用及最終方案。 |

子代理均為唯讀，主對話為 assessment 唯一 tracked writer；模型／effort 依 project policy 明確指定，沒有繼承主對話作 fallback。Runtime tool 接受上述 invocation，未取得獨立模型／計費遙測。主對話驗證不宣稱為 fixed-commit independent review；這次未改安裝行為。

## 本次檢查與限制

- 逐檔清單與 Git inventory 完整對應：122／122，無重複、漏列或額外來源；目的地去重為 55。
- YAML 直接抽取核對：122 members、121 resources、6 個 consuming skill bindings；公開成員 CSV 為 256 個唯一位置，舊版數量與差異均相符。
- 公開 ZIP、checksum、manifest、engine pin 與全部列出的 content hashes 核對完成；相對於目前來源的 8 個函式 AST 比較有界完成，未執行安裝器。
- 新 assessment 內部相對連結均可達；索引及 locator 已與實際標題／狀態對齊。`git diff --check` 無問題，assessed source 未變更。
- Repository 原有 assessment validator 在全庫執行仍失敗：154 個診斷來自既有歷史模板／backlog 路徑消失及其他 assessment 未提供 workflow-store-config。本次 assessment 沒有被列入其錯誤。保留此失敗，未修改歷史紀錄或 validator。
- 使用同一個未修改的 repository validator，透過支援的 `--root` 對本 assessment 的 byte copies、原始索引列及實際引用模板進行有界檢查，通過 1 個 assessment；這不是全庫通過。詳細命令與範圍見 [驗證紀錄](evidence/validation.json)。
- 沒有執行產品測試、兩條 upgrade、native discovery 或 target 語意驗收。這些尚未執行的工作沒有被列為 passed。

## 實作前的確認範圍

請使用者確認是否採用以下整體方案：55 個目的檔案與逐檔保留界線、canonical package `dotnet`／建議 0.3.0、保留原規則 profile identities、無自動 alias、三份 legacy compliance 保留，以及兩個公開版本的獨立驗證安排。

本次完成的是評估與可審閱方案。後續來源實作需以核准結果建立適用的 Issue／workflow 與 dedicated implementation branch；再更新來源、連動引用及驗證。Assessment 自身的 final 狀態只固定本報告結論，不代表方案被採納、升級通過或發版完成。
