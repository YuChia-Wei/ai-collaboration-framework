# 領域建模、軟體架構與相鄰 skill 職責與行為契約

基準與 owner 授權見 [設計入口](README.md)，精確來源修改與知識映射見
[實作設計](implementation-design.md)。本文定義此次實作的責任與接受條件。`design` 產出提案；接受狀態必須來自
實際 owner 證據，不能由 skill 自行宣告。

## 共同原則

- 依所需判斷與產出選 skill；檔名、GWT 格式、DDD 或 CA 關鍵字不單獨決定路由。
- 共通知識提供方法；skill 承擔操作判斷；專案擁有業務、規則採用、工具、儲存位置與授權。
- 既有來源、模型、例子與決策可以共用；不因切換 skill 就重新探索或建立一份副本。
- 單一 skill 可獨立工作；可選 knowledge 或其他 skill 缺少時，列明覆蓋限制，繼續有依據的部分。
- `review` 綁定固定 artifact，維持唯讀；self-check、review 與有證據的 independent review 分開。
- 預設對話輸出；只有指定目的地且有寫入授權才落地。沒有強制的新 schema、record store、文件數或工具依賴。

## 1. `domain-model-designer`

### 主要責任

回答「這個領域的概念、規則、行為與一致性責任應如何建模」。以 DDD 為主要方法，
以 BDD 的具體例子／反例檢查理解；能探索既有模型，也能設計與審查修改。

負責：

- 業務語言與歧義、subdomain 與 bounded-context 候選、context 關係及責任。
- 模型中的 entities、value objects、aggregates、domain services/events，僅在需要時使用。
- 不變條件、狀態轉換、行為歸屬，以及何種業務事實必須共同保持一致。
- 模型替代方案與演進影響；用例子挑戰邊界，保留來源與未定業務政策。
- 從需求推導模型，但不把推導結果冒充已接受需求。

不負責：產品優先序核准、需求文件的唯一 author、transport／ORM／broker／部署選型、
實際交易機制與重試實作、完整測試設計、程式修改或 provider 操作。

### Operations、輸入與輸出

| Operation | 最低輸入 | 輸出 | 結束條件 |
| --- | --- | --- | --- |
| `explore` | 有界領域問題／受阻的模型判斷、可讀來源、已有語言與例子、已知決策及限制 | 來源化的語言、規則與反例、歧義、模型假設、owner 問題與最小下一步；允許沒有模型圖 | 指定疑問已有足夠依據、或留下影響範圍明確的待決策；不為了湊模型持續提問 |
| `design` | 有界建模目標、需求／行為與接受狀態、既有模型／約束、需要保持的契約；品質條件只取影響模型者 | 模型提案、責任與不變條件分配、狀態／事件、例子映射、替代方案及後果、未定選項、可選 architecture/spec/implementation 交接 | 模型可由具體例子檢查，重要不變條件有 owner，待決定項不被當成已接受 |
| `review` | 固定模型 artifact 與身份、來源需求、接受決策、指定覆蓋與允許證據 | 有位置／準則／觸發／影響／依據的 findings、有效替代方案、未知與排除、review 身份 | 完成指定覆蓋並交代限制；不修模型、不產生 compliance 或 runtime 通過宣稱 |

共同輸入只需要與當前操作相關的內容；不要求 PRD、完整 Context Map 或全部 DDD
文件先存在。未知可保留為 proposal／question，不允許為填滿範本虛構規則。

### 與架構的接點

領域建模可提出「某項不變條件需原子成立」及 aggregate 的模型責任。
`software-architect` 決定實際交易、資料儲存與跨邊界協調如何滿足它。
架構若認為無法滿足，回傳可行性衝突與選項，由相關 owner 修訂需求或模型；
不能自行把強一致性改成最終一致性，也不能把每個 bounded context 直接部署成微服務。

### 知識分配

優先使用既有 `engineering-common` 的 `ddd/domain-discovery.md`、`strategic-design.md`、
`tactical-design.md`、`model-evolution.md`、必要的 domain-language 與 Context Map 資源。
可選 BDD discovery/formulation，用於模型例子；不因此取得 test automation 責任。
DDD 的模型知識保持共用，architecture 可讀與其判斷相關的部分，不以物理移除知識來製造隔離。

## 2. `software-architect`

### 主要責任

回答「在已知行為、領域責任與品質限制下，如何安排軟體結構、依賴及整合契約」。
CA 與 Hexagonal 是按需使用的架構方法，不是每個專案的預設採用規則。

負責：

- 軟體模組／元件邊界、依賴方向、application responsibility、inbound/outbound ports 及 adapters。
- 外部介面、持久化／訊息／vendor 依賴隔離、相容性與演進方案。
- 在來源支持範圍內，設計實際 transaction、併發、retry、idempotency、失敗與恢復機制。
- 可測試性、可觀察性、相關 security／performance／availability 要求的軟體設計取捨。
- 比較較簡單的有效方案；保留技術選擇、成本與實際環境能力的未知。

不負責：自行核准業務政策、重定義已接受領域不變條件、以未量測數字聲稱容量或效能、
程式實作、部署、環境變更、完整測試規格或大型基礎設施架構。

### Operations、輸入與輸出

| Operation | 最低輸入 | 輸出 | 結束條件 |
| --- | --- | --- | --- |
| `design` | 有界軟體設計目標、行為／契約與接受狀態、既有責任與依賴、品質／相容性限制、已選技術與環境事實 | 元件與依賴提案、ports／adapters、關鍵交互與失敗語意、替代方案、品質論據／假設、演進影響、所需驗證與未定決策 | 每個重要結構選擇有目的與來源；可測試但未驗證之處明示；沒有多餘 speculative abstraction |
| `review` | 固定架構 artifact、來源行為／模型／品質要求、已接受決策與指定 coverage | 依賴、介面、失敗／恢復、相容性與品質的 evidence-backed findings、有效選項與限制 | 固定 scope 完成；不以另一種偏好當缺陷，不宣稱實際系統符合 |

不要求必先呼叫 domain-model-designer；既有需求／模型或明確技術問題已足夠時可直接
處理。技術設計暴露的新領域問題則回到該問題的 owner，而非自動補完業務規則。

### Software 與未來 system architect／DevOps 的界線

本輪保留與軟體正確性直接相關的 deployment／rollout 假設、依賴網路失敗條件和
運作約束，但不擴展為網路分區、路由／DNS／防火牆拓樸、跨機房基礎設施、硬體容量、
平台營運、IaC 或部署流水線建置。這些輸入不足時可列為限制／未來專業能力需求。

未來 `system-architect` 可承接大型系統與跨軟硬體／網路的結構設計；DevOps 能力可
承接交付與運作工程。其操作、職責與命名尚未設計，不能從此段推定已存在或已授權。

### 知識分配

保留與 dependency、ports/adapters、技術選擇、failure/recovery 直接相關的共通指引。
此次 CA／Hexagonal 操作指引由新 software-architect 的 design/review 唯一承接，
不另建重複知識 package；通用跨 skill 邊界仍由 engineering-common 的既有 references 擁有。
既有 .NET 的 aggregate、DbC、transactional messaging、use-case、project structure
需依具體判斷分配 allowlist；名稱拆分不等於技術規則自動採納。

## 3. 相鄰 skill 的必要調整

| Owner | 保留責任 | 要修改的部分 | 輸出／交接邊界 |
| --- | --- | --- | --- |
| `requirement-author` | stakeholder need、business rule、可觀察 AC，既有 `explore/draft/normalize` | 保留 BDD/DDD discovery；說明語言探索與模型設計的分界；對純需求例子不強迫 test handoff | 規則／例子／未知及接受狀態；aggregate 或機制只是另需設計的問題，不能當需求既成事實 |
| `user-story-author` | 價值或技術學習切片、Story／AC authoring 與 review | 提供可選 BDD discovery/formulation、必要的 DDD vocabulary 指引及 metadata allowlist；維持無 upstream skill 前置 | Title/Description/AC 與來源；可表達例子，不決定 fixture、runner 或測試層級 |
| `spec-author` | production/entity/adapter 契約的 draft/normalize | 允許方法知識幫助表達／檢查契約；修清楚「scenario notes」與正式 test design 的界線，避免 GWT 全被導走 | 已接受模型與架構的契約、observable examples、未定設計；不自行選 aggregate、persistence 或 failure policy |
| `test-designer` | 測試設計／review、case/level/data/oracle/coverage、formal test specification | 保留 BDD 作可選方法；明確區分需求例子、模型驗證例子與測試設計；發現語意矛盾時回饋 owner | 測試邊界、獨立預期結果來源、資料及案例映射；不為方便測試重寫需求或把 observed behavior 當 approved |
| `software-development-orchestrator` | 選必要工作、依賴／授權、驗證與接續 | architecture candidate 拆成 domain modeling/software architecture；新增問題分類、有界探索、增量與回饋路由 | 同一成果的最小必要工作與真實結果；不重寫 specialist 證據，不強制每步換 agent 或建立文件 |

`problem-frame-author` 不因新設計 skill 而被強制前置；`spec-compliance-validator`
仍只在指定完整判準／證據評估時使用。實作與 code review 保留原責任，僅更新實際
受影響的 route／引用及交接描述，不利用本次拆分重構無關操作。

### 行為例子與測試設計的判斷

「Given/When/Then」是表達方式。若目的是澄清「預期如何行為」，需求、模型與 spec
均可使用。當輸出開始決定要測的系統邊界、資料分割、隔離、控制依賴、獨立 oracle、
assertions 或 execution level 時，才由 test-designer 擁有該設計。

一個來源例子可被測試設計引用，不需再建立一份不同 ID 的需求或 spec。模型／架構
author 可以對自己的設計做例子 walkthrough，但不能標示 independent review 或測試已通過。

## 4. 交接最小內容

這是一組語意欄位，不新增強制 JSON schema 或記錄格式。使用已有文件／Issue／對話
即可；需要跨 session 時用目標專案選定的持久紀錄。

| 內容 | 必須保留的事實 |
| --- | --- |
| 目標與範圍 | 要解決的問題、此次成果、non-goals、所需下一個判斷 |
| 來源與身份 | 需求／例子／模型／設計的既有 ID、可得版本與位置；無文件時清楚標示對話來源 |
| 決策與語意 | accepted、proposed、observed、unknown 分開；不變條件與 owner 不丟失 |
| 約束與授權 | 相容性、品質、可讀寫邊界、已有授權；artifact 不額外賦予批准 |
| 未定事項 | 哪項疑問阻擋哪個判斷／操作；獨立工作可繼續 |
| 證據與下一步 | 實際做過什麼、限制、需要誰做何種輸出；不列虛構 passing tests |

## 5. Orchestrator 的工作選擇與回饋

### 先找阻礙，再決定操作

| 目前問題 | 優先 route | 何時不需呼叫 |
| --- | --- | --- |
| 價值、需求、AC 或業務政策尚不清楚 | requirement-author／user-story-author 與實際 owner | 已有足夠 accepted behavior |
| 語言、狀態、一致性或模型 owner 衝突 | domain-model-designer | 模型不受本次變更影響 |
| 依賴／整合／品質取捨未定 | software-architect | 已有可沿用設計且未出現新衝突 |
| 契約需要精確表達或更新 | spec-author | 既有契約已能支撐工作，不需另製 spec |
| 技術可行性未知 | 有界探索／實驗；依問題選適當能力與實際授權 | 有直接可靠證據，不需用 prototype 再證明 |
| 驗證邊界或 oracle 不清楚 | test-designer；業務預期回到 requirement owner | 既有設計可直接執行 |
| 已觀察到故障但原因未知 | diagnostic-analyst | 修復原因與設計已確定 |
| 已接受、已授權的行為切片 | slice-implementer | 只有單一不改契約的技術操作時可選 local-change |

有界實驗應有問題、來源、允許作用範圍、成功／否定訊號、停止條件與觀察結果。
沒有要求統一的 spike skill，也不把 prototype 自動升為 production。對業務未知，
AI 自己生成另一個假設不是取得 stakeholder 共識。

### 增量流程

1. 選一個可觀察成果，確認已有接受內容及執行權限。
2. 只解決阻礙該成果的需求、模型、技術與驗證問題；可重用的輸入直接使用。
3. 完成一個有凝聚性的行為／技術／學習切片；不依 folder 或每次 skill 呼叫強制拆 task。
4. 以獨立行為來源驗證，適用時做指定 review。實作與測試失敗依原因回到正確 owner。
5. 依授權整合／交付，保留尚未完成與環境限制。
6. 有實際回饋時調整下一個增量；沒有部署／使用資料就不宣稱產生產品效果。

保留現有 conditional validation、昂貴驗證必要性、已接受結果重用與授權傳遞。
不新增強制完整 SDLC、test ledger、文件數門檻或每次 stage 的批准。

## 6. 可觀察完成判準

以下是本次產品完成判準，不是執行結果；依實際改動選最小必要驗證，不轉成所有
模型／平台的固定矩陣。預期結果來自上述責任契約，不以新實作內容反推。

| ID | 請求／條件 | 預期結果 |
| --- | --- | --- |
| A-AC-01 | 只釐清取消訂單的規則、語言與 aggregate 責任 | domain skill 能產出例子／模型問題，不強制選資料庫、broker、CA 或測試 runner |
| A-AC-02 | 已有模型，只需隔離第三方付款 API | software architect 可直接設計 port/adapter，不重跑需求／DDD 全流程 |
| A-AC-03 | 模型要求原子成立，但技術方案只有最終一致性 | 明列衝突、影響與 owner 選項；不默改模型或聲稱需求已滿足 |
| A-AC-04 | 使用者請求含 GWT 的 Story 或 production spec | 仍由指定 author 完成；不因格式強制導向 test-designer |
| A-AC-05 | 要決定併發／重複請求如何測、資料與 oracle | test-designer 擁有設計；沒有業務依據的預期結果保留未定 |
| A-AC-06 | 已接受 spec，可直接實作小型切片 | orchestrator 跳過不必要的 author/design stage，不重新索取已有授權 |
| A-AC-07 | 測試反例指出需求歧義 | 回饋 requirement owner，不能只改測試或實作消除失敗 |
| A-AC-08 | 從 checkpoint 接續 | 保留 accepted/proposed/unknown、來源身份、完成項與權限，不重建全部文件 |
| A-AC-09 | 沒有安裝可選 BDD/DDD knowledge | common 操作仍能基於 caller sources 完成，明列缺少 specialist coverage，不讀 framework checkout 補缺 |
| A-AC-10 | 固定模型／架構 review | subject 不變；結果身份與覆蓋限制真實，不把作者自檢當獨立審查 |
| A-AC-11 | 原 skill ID 與舊 binding 的升級 | 新 catalog 的 resolver 拒絕舊 ID；明選兩者之一或兩者後規劃升級；不 alias／自動覆寫 custom |
| A-AC-12 | 新 skill 加入來源 catalog | 選讀表、各頁、路由、knowledge allowlist、分發宣告一致，未自動採用／安裝到來源或下游 |
| A-AC-13 | 請求大型網路／基礎設施設計 | 說明本次 software skill 的範圍與缺少覆蓋，不假稱未來 system/DevOps skill 已可用 |

## 7. 直接來源定位

- [現有 architecture 設計](https://github.com/YuChia-Wei/ai-collaboration-framework/blob/f96fffe0af6e9e4f79d5f2f4be05bb3665553123/src/skills/ddd-ca-hex-architect/references/design.md)與[審查](https://github.com/YuChia-Wei/ai-collaboration-framework/blob/f96fffe0af6e9e4f79d5f2f4be05bb3665553123/src/skills/ddd-ca-hex-architect/references/review.md)：固定基準的原責任；拆分後不作為執行入口。
- [Requirement exploration](../../../src/skills/requirement-author/references/explore.md)與[authoring](../../../src/skills/requirement-author/references/authoring.md)：已支援有界探索與 AC 中的 GWT。
- [Story contract](../../../src/skills/user-story-author/references/story-contract.md)：現有 Title/Description/AC 與來源界線。
- [Spec authoring](../../../src/skills/spec-author/references/authoring.md)：已接受設計、system/test spec 邊界；需精確澄清 scenario notes。
- [Test design](../../../src/skills/test-designer/references/design.md)：oracle、層級、資料與實作交接。
- [Orchestration](../../../src/skills/software-development-orchestrator/references/orchestrate.md)：保留必要階段、重用與有比例的驗證。
- [BDD](../../../src/knowledge/engineering-common/bdd/README.md)與[DDD](../../../src/knowledge/engineering-common/ddd/README.md)：現有共通知識責任。
