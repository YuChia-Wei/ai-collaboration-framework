# 來源實作、分發與驗證設計

本文件將 [職責契約](skill-contracts.md) 轉成確定的修改範圍。
基準與授權以 [入口](README.md) 為準。版本號是此次來源 package 的身份，
不代表 release 已配置、來源已安裝或下游已升級。

## 1. Package 與版本

| Package／preset | 來源版本變更 | 實際原因 |
| --- | --- | --- |
| domain-model-designer | 新增 0.1.0，metadata 4 | explore/design/review 領域責任 |
| software-architect | 新增 0.1.0，metadata 4 | design/review 軟體架構責任 |
| ddd-ca-hex-architect | 移除來源 package 與 catalog 項目 | owner 明確退役，沒有 alias/router |
| engineering-common | 0.3.0 → 0.4.0 | 共通責任 routing 與 BDD/Story selector 擴充 |
| dotnet-backend | 0.1.4 → 0.1.5 | required common dependency 同步 0.4.0；技術知識內容不變 |
| requirement-author | 0.2.1 → 0.2.2 | 明確需求探索／模型邊界，同步知識 pin |
| user-story-author | 0.1.0 → 0.2.0，metadata 3 → 4 | optional BDD/DDD knowledge protocol |
| spec-author | 0.2.0 → 0.3.0，metadata 3 → 4 | optional methods、observable examples 與 test spec 邊界 |
| test-designer | 0.4.1 → 0.4.2 | 行為例子與測試設計責任、回饋 owner、知識 pin |
| software-development-orchestrator | 0.3.2 → 0.4.0 | 分開兩個 owner，按未知問題及回饋選工作 |
| code-reviewer | 0.2.4 → 0.2.5 | 僅同步 exact common／dotnet dependencies；不擴大 allowlist |
| local-change-implementer、slice-implementer | 各 0.2.5 → 0.2.6 | 僅同步 exact common／dotnet dependencies；不改其操作 |
| collaboration、complete、engineering、source-repository presets | 各 0.1.0 → 0.2.0 | 一個舊 skill 改為兩個明確選項，既有組合能力保持完整 |

其他未列 skills/presets、adapters、engine API、selection/lock schema 版本保持原身份。此次新來源 catalog 為 21 個 distributed skills；實驗中的
standards-promotion 不計入。來源專案現有 17-skill installation 不因 catalog 改變而改名。

## 2. 新 package 的檔案與操作

兩者均為 instruction package，`configuration: null`、`artifact_roles: []`，沒有
executable、record store 或強制 framework 目錄。只有 skill-instruction-reader runtime。
所有必需 downstream 資源由 `src` 宣告，不引用 `.dev`、`docs` 或 root tools 執行。

| Package | Members | 內容責任 |
| --- | --- | --- |
| domain-model-designer | SKILL.md、skill-package.yaml、references/explore.md、design.md、review.md、knowledge.md | 入口按 operation 漸進載入；knowledge.md 保存一次完整 installed reader protocol，三個 operation 引用 |
| software-architect | SKILL.md、skill-package.yaml、references/design.md、review.md、knowledge.md | 沿用既有架構正確性、相容性與失敗分析；移出領域模型決策；共同 protocol 單一 reference |

Domain explore 產出來源化語言、規則、例子、歧義及最小下一步；design 產出模型提案、
invariant owner、狀態／事件、替代方案；review 固定 subject，只回 findings。
Software design 產出模組、依賴、ports/adapters、交易／失敗機制與品質取捨；review
依 accepted requirements/model 判斷。兩者都保留 proposed/accepted/observed/unknown，
預設對話輸出，只有選定目的地與寫入授權才保存。完整輸入輸出與判準見職責契約。

CA／Hexagonal 的操作指引留在 software-architect；本次不為抽象重用新增 knowledge
package。原 review 的固定身份、作者關係、read-only、有效替代方案及 coverage 限制
分配給兩個 review，不遺失獨立性判斷。原 .NET 可選覆蓋依第 4 節完整分配。

## 3. Common knowledge 精確映射

Knowledge capability 是適用分類，不是 skill identity。兩個新 skill 保留既有
`architecture` capability，透過 operation 與各自 allowlist 分離責任。這不是舊 ID
的 alias。每個 consumption row 都為 `requirement: optional`、`on_missing: unavailable`，
引用 `engineering-common@0.4.0`。以下路徑一律是完整 `member:` resource ID；
`engineering-rule-catalog` 是例外的具名 ID。

| Consumer／operation | capability | Allowlist |
| --- | --- | --- |
| domain-model-designer / explore | architecture | ddd/README.md、ddd/domain-discovery.md、ddd/examples/order-cancellation.md、bdd/discovery.md、discovery/collaborative-discovery.md |
| domain-model-designer / design, review | architecture | engineering-rule-catalog；ddd/README.md、ddd/domain-discovery.md、ddd/strategic-design.md、ddd/tactical-design.md、ddd/model-evolution.md、ddd/examples/order-cancellation.md；domain-language/README.MD；domain-language/templates/aggregate-vocabulary-template.md、bounded-context-language-template.md、domain-event-language-template.md；operations/CONTEXT-MAP-GUIDE.MD；bdd/discovery.md、bdd/formulation.md |
| software-architect / design, review | architecture | engineering-rule-catalog；references/TECHNOLOGY-SELECTION-POLICY.md、references/ARTIFACT-DESIGN-REVIEW-CONTRACT.md、references/AUTHORING-BOUNDARY-CONTRACT.md |
| user-story-author / plan | requirements | bdd/discovery.md、ddd/domain-discovery.md、discovery/collaborative-discovery.md |
| user-story-author / draft, normalize, review | requirements | bdd/discovery.md、bdd/formulation.md、ddd/domain-discovery.md |
| spec-author / draft, normalize | specification | bdd/formulation.md、ddd/domain-discovery.md、ddd/tactical-design.md、references/AUTHORING-BOUNDARY-CONTRACT.md |
| requirement-author | requirements | 保留原兩組 allowlist 與 operations，只改 pin 與相鄰邊界 |
| test-designer | test-design | 保留原 allowlist 與 operations，只改 pin 與相鄰邊界 |

上表 domain-language 的三個 template 都在 `domain-language/templates/` 下。
Spec 讀 tactical guidance 是為精確表達已接受的 invariant／模型，不能藉此自行選
aggregate、業務政策或 transaction owner。Orchestrator 不新增 knowledge consumption。

`engineering-common/content-package.yaml` 只追加必要 selector，保留既有值：

| Resource | 追加 capability | 追加 operation |
| --- | --- | --- |
| member:bdd/discovery.md | architecture | plan |
| member:bdd/formulation.md | architecture、specification | 無 |
| member:ddd/domain-discovery.md | 無 | plan |
| member:discovery/collaborative-discovery.md | 無 | plan |

不從未宣告的 bdd/README.md 偷讀導航。Domain explore 不含 rule catalog 或 domain-language
templates，因為它們沒有 explore operation。Story plan 與 authoring consumption 分組；
不要建立把 plan 與 formulation 混在一起的 binding，否則現有 selector 子集檢查會拒絕。

`src/distribution/content.py::descriptor`（基準第 209 行）將 consumption 轉為 dependencies，
`closure`（第 249 行）使用 exact version；因此五個
存活舊 consumers（code-reviewer、local-change-implementer、requirement-author、
slice-implementer、test-designer）的 common pin 全部同步。這些 metadata 變更須同步
manifest version；不因此改不相關的行為或知識範圍。

此外 dotnet-backend/content-package.yaml 的 required dependency 精確固定 common@0.3.0；
它也必須升為 dotnet-backend@0.1.5 並依賴 common@0.4.0。其四個存活舊 consumers
（code-reviewer、local-change-implementer、slice-implementer、test-designer）以及兩個
新 skill 的 dotnet pins 同步 0.1.5；前述 skill bumps 已涵蓋這次 metadata 調整。
測試須包含 common + dotnet 同選的 closure，不能只測 common-only。

## 4. .NET 知識與 installed protocol

| Consumer | dotnet-backend@0.1.5 / design, review allowlist |
| --- | --- |
| domain-model-designer | engineering-rule-catalog、member:standards/DESIGN-BY-CONTRACT.md、member:standards/coding-standards/aggregate-standards.md |
| software-architect | engineering-rule-catalog、member:standards/BUILDING-BLOCKS-RECONSTRUCTION-CONTRACT.md、member:standards/DESIGN-BY-CONTRACT.md、member:standards/coding-standards/transactional-messaging-standards.md、member:standards/coding-standards/usecase-standards.md、member:standards/project-structure.md |

兩者 capability 為 architecture，technology profile 保持 dotnet-backend。Domain explore
不消費 .NET 規則。相同 DbC 資源可供不同操作閱讀，但只能依已採納 target authority
適用，不能因安裝或 package 名稱就要求 .NET／特定模式。

新 knowledge.md 與 Story/Spec 的 knowledge.md 須保留既有完整 protocol：caller 的
canonical project_root、外部觀察的 raw expected_lock_sha256、明確 authority allowlist；
以既有 `read_installed_resources`／engine-2 verified closure 讀取；驗 lock identity、
managed closure、raw hashes、paths、綁定與 selectors；有 drift 不產出部分 verified index。
只讀實際需要且允許的 installed resources，讀前後重驗身份。不能建立另一個 parser，
不能 ambient import framework checkout，不能因缺 knowledge 默寫 config。

輸出保留 available/unavailable/blocked、loaded_resources、applicable/conditional rules、
authorities、coverage 與 diagnostics。Knowledge/example 不等於 adopted normative rule；
缺少 authority 只阻擋相應判斷。既有 binding 未變不重新要求採納。無 optional knowledge
時仍可依 caller sources 做 common work，不能宣稱專業覆蓋已驗證。

## 5. 相鄰 owner 與檔案

| 來源 | 修改內容 |
| --- | --- |
| requirement-author / SKILL、explore、authoring | 需求語言／規則探索與模型責任分開；GWT 是 AC 表達之一 |
| user-story-author / SKILL、plan、authoring、review、story-contract、新 knowledge | 顯式 optional knowledge；保留 Title/Description/AC、無 upstream skill 前置；plan 不先選技術 |
| spec-author / SKILL、authoring、新 knowledge | 允許 observable examples；test spec／oracle 設計交 test-designer；缺設計回 owner |
| test-designer / SKILL、design、review | 不按 GWT 格式搶作者職責；反例造成規則歧義時回饋原 owner |
| software-development-orchestrator / SKILL、orchestrate | 兩 route、阻礙問題分類、有界探索、增量與回饋，保留既有權限／驗證重用 |
| engineering-common / AUTHORING-BOUNDARY-CONTRACT | 需求、模型、軟體機制、spec、test 的唯一責任；例子可共用 |
| engineering-common / IMPLEMENTATION-SCOPE-ROUTING-CONTRACT | 語意／模型未知與技術／依賴未知分流；module count 不強迫編排 |
| engineering-common / ARTIFACT-DESIGN-REVIEW-CONTRACT | 模型、架構、測試設計的共同 artifact review；保留固定身份與獨立性 |

## 6. 分發、退役與 migration

Manifest 移除舊 component/member destinations，加入兩個新 package 的完整 members；
新增 Story/Spec knowledge.md member。四個原本含舊 ID 的 presets 改選兩個新 ID，
維持排序，`knowledge: []` 保持不變。其他 presets 不新增能力。

現有 schema 只檢查合法 ID 形狀；退役由新 catalog 的 `resolve_selection` 回報
`selection-unavailable`，不新增特殊 blacklist，不改舊 lock 或歷史 catalog 的讀取。
舊來源 package 可由固定 Git revision 查回，並非 runtime alias。

Migration 指南須提供以下可執行的人類決策流程，不能只說換名稱：

1. 依需要明選 domain-model-designer、software-architect 或兩者；使用 preset 者閱讀
   新 preset 的兩項 selection，非 preset 使用者不被強制安裝兩項。
2. 從 desired selection 移除舊 ID、加入已選新 ID；先檢查現有 managed drift／custom
   collision；本次來源工作不代使用者實際修改 selection 或 lock。
3. 既有 architecture/design/review bindings 保留 ID、authority、selectors 與 coverage
   意圖；逐 resource 核對新 consumer allowlist。新 explore／Story plan 需要明確 binding，
   不因名稱替換自動擴大。共用 knowledge 版本由新 catalog 的 exact pin 一致解析。
4. 使用既有 derive/inspect/plan，再依已有授權 apply 與 read-back。若移除未修改 managed
   舊 package 是該 plan 的明確效果，由該升級操作處理；drift/custom 不默刪或覆寫。
5. 新 catalog 不提供舊 runtime entry，因此不承諾舊 ID invocation 能回覆退役訊息。
   Selection 的拒絕由既有 resolver 擁有；退役原因與選擇指引由 migration 文件、選讀表
   及知情的呼叫端說明擁有，不保留 router。既有安裝仍有舊 entry 時是 installed snapshot，
   不能假稱本次來源修改已令它消失。

本次更新 docs/skills 選讀表、新兩頁與 migration 說明、docs/installation 的覆蓋與
升級段落、knowledge packages matrix、根 README 中重複數量。舊 current skill guide
移除，歷史 RC4 文件保留。根 AGENTS 與繁中翻譯明示新 source 與現有 installed routes
差異；不得直接宣稱未安裝的新 skill 可由 .agents 呼叫。

## 7. 驗證選擇與結果界線

| 判準 | 方法／入口 | 能證明與不能證明 |
| --- | --- | --- |
| Source metadata、manifest、members、presets、pins、projections | 既有 `python -I -B tests/run.py --suite distribution --suite schemas` | 機械契約與實際測試結果；不是模型行為或下游安裝驗收 |
| 新 IDs 獨立選用、合用、無 knowledge、common + dotnet；舊 ID 拒絕 | 在現有 distribution tests 加少量行為測試 | resolver 與 closure；不建立固定字串守門平台 |
| Domain explore、Story plan、spec formulation selector | 既有 resource binding validator 的代表案例 | 每組 selector 真正可解析；含不合法混合被拒絕 |
| A-AC-01 至 13 的語意 | 固定來源的另一 agent review，對指定四類例子走查 | 審核涵蓋／缺陷與限制；不稱真實 runtime invocation acceptance |
| 文件與根導航 | 相對連結、版本／操作對照、雙語規範 parity、git diff --check | 文件一致性；不證明 installation |

四類語意輸入為純領域取消訂單、已有模型的付款 API 隔離、含 GWT 的 Story/spec、
模型強一致但架構僅最終一致的混合問題。以職責契約的預期結果為 oracle，不能從
新文字反推全部通過。新 findings 依 owner 修正；重大設計修改先更新設計再實作。

設計審核在任何 src 修改前，subject 為完整設計 commit；實作審核則固定來源 commit，
兩者由未撰寫 subject 的唯讀 agent 執行。維持 parent 為唯一 tracked writer。
沒有與實際 diff 相關的理由，不跑全模型、全平台、安裝／E2E 矩陣。
PR hosted source gate 保留，尚未 push/PR 時標示未執行，不能由本機結果代替。

## 8. 失敗與回復

分發／schema 測試失敗先修正本次 package 或相依宣告，不削弱原 validator。
尚未安裝或發布，回復來源變更可由本機 commit 比較完成；不對使用者既有 installation
執行 recovery 或 rollback。若發現需改 engine、鎖檔 schema 或客製 recovery 才能完成，
先確認是否真是拆分必要條件；超過本設計的 owner 選擇保持未定，不混入本輪實作。
