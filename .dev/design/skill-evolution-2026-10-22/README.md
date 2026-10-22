# DDD 與軟體架構 skill 拆分設計

- 日期：2026-10-22（Asia/Taipei）
- 設計狀態：已先完成獨立審核及修正，再進行本機產品實作；[設計審核紀錄](../../workflows/2026-10-22-domain-architecture-split/design-review.md)保存固定版本與 findings。
- 執行狀態：見[本次 workflow](../../workflows/2026-10-22-domain-architecture-split/workflow-plan.md)與[實作／驗證紀錄](../../workflows/2026-10-22-domain-architecture-split/implementation-results.md)，不由設計文件推定發布或安裝。
- 來源盤點基準：`f96fffe0af6e9e4f79d5f2f4be05bb3665553123`
- 工作分支：`codex/plan/skill-evolution-20261022`
- 本文件是設計入口；設計、審核、實作、驗證與發布各有獨立狀態。

## 問題與預期成果

既有 `ddd-ca-hex-architect` 在同一操作中處理領域語言、不變條件、aggregate，
以及 ports/adapters、交易機制、失敗恢復。單純領域探索因此必須經過過大的入口。
另一方面，BDD/DDD 是可以跨需求、模型、規格與測試使用的方法，不能因拆 skill
而將方法知識限制在唯一作者。此次設計把「做哪種判斷」與「讀哪種方法」分開。

交付兩個可獨立選用的 instruction packages：`domain-model-designer` 負責領域
分析與模型，`software-architect` 負責軟體結構與技術機制。舊
`ddd-ca-hex-architect` 直接退役，不保留 alias、router 或可選 catalog 項目。

## 文件與讀取順序

| 文件 | 必須能獨立回答的問題 |
| --- | --- |
| [本文件](README.md) | 為何做、已接受什麼、此次做多少、工作如何銜接 |
| [職責與行為契約](skill-contracts.md) | 兩個 skill 的操作、輸入輸出、責任邊界、回饋與可觀察判準 |
| [實作與驗證設計](implementation-design.md) | 要改哪些來源、版本、知識 selector、退役／升級語意與驗證方法 |
| [討論脈絡與參考資料](context-and-references.md) | 原始需求、盤點發現、替代方案及外部研究如何支持本設計 |
| [本機 workflow 與客製升級評估](local-workflow-and-customization.md) | 另案問題、現況、候選方案、尚未接受的決策 |
| [外部審核處置與後續設計](review-follow-up.md) | Claude 報告的逐項核對、文件修正、引擎缺口提案與原 Issues 接續 |
| [現行 skill 選讀表](../../../docs/skills/README.md) | 當前來源提供的能力；安裝是否更新另由 installed state 證明 |

本組設計不能以「採納前述建議」或私人對話作為缺省內容。新接手者須從這些文件、
其固定來源與對應 Issue 得到完整工作範圍。不能保證任何 AI 永遠正確理解；本次以
固定版本、明確決策、具體例子及未參與撰寫的 agent 審核，檢查可獨立理解程度。

## Owner 決策與授權沿革

以下是 2026-10-22 owner 直接指示的持久摘要，不是 agent 自行接受的產品需求。

| ID | 決策／要求 | 現行處置 |
| --- | --- | --- |
| O-01 | 分離 DDD 領域建模與 CA／Hexagonal 軟體架構 | 本次實作 |
| O-02 | 具體定義兩個新 skill 及 requirement/spec/test/orchestrator 配套 | 本次實作，含 user-story-author 的直接相鄰邊界 |
| O-03 | 最初要求先不改 src，先保存規劃 | 已完成規劃階段；後續 O-11 明確授權設計審核後實作，替代該階段限制 |
| O-04 | 保留人類 skill 彙整表並隨演進更新 | 沿用 docs/skills/README.md 與維護說明 |
| O-05 | software architecture 優先，system architecture／網路／DevOps 是中長期 | 本次不新增其 package、操作或依賴 |
| O-06 | 評估 local-backlog 退役或整合 workflow-records，支援純文件／SQLite 本機工作 | 獨立 Feature；本次只保存評估與建立 Issue |
| O-07 | 本機工作須有紀錄與編排，無需線上 Issue 系統 | 區分記錄 owner 與 orchestrator；provider parity 尚未實作 |
| O-08 | 考慮 author/designer/orchestrator 命名慣例 | 新 ID 已由 O-12 定案；不全面改名其他 skills |
| O-09 | 評估自建、客製、整合新版、上游涵蓋等狀態，降低升級衝突 | 獨立 Feature；未採納新 metadata schema |
| O-10 | 自建資源避免放 managed .ai/core | 保留既有保護；候選 custom 位置另案決定 |
| O-11 | 完整設計先完成；實作前請其他 agent 審核；保存對話脈絡；完成後建立中文 Feature/User Story | 本次交付順序，審核與 Issue 必須先於 src 修改 |
| O-12 | 名稱為 domain-model-designer 與 software-architect；舊 ID 直接退役，不保留 alias | 已定案；不再把名稱／過渡 router 留待實作者決定 |
| O-13 | 依計畫實作拆分與相鄰調整；本機 workflow／客製升級另案 | 僅主 Feature 實作；另案不得藉相依更新混入 |
| O-14 | 將目前版本更新至既有 Windows Preview，使用 Antigravity CLI / Gemini 4 Argon 審核 | 已對 438b15eb 完成；來源專案的 17-skill 安裝未更新 |
| O-15 | 修正審核建議，接續原 Issue，推既有分支供 macOS / Claude 審核 | O1/O2 修正及分支推送已完成；實際收到報告的 reviewer 為 Claude Fable 5.1 |
| O-16 | 讀取 Slack 的 Claude 分析，安排修正與設計／既有線上 User Story 調整 | 本輪文件與 Issue 修正；其餘產品選項依 review-follow-up.md 保留待決策／未實作 |

授權包括原本的本機設計、來源實作、必要驗證及中文 Issues，以及後續 O-14–O-16
明列的 Preview、審核、既有分支推送與文件／Issue 整理。依來源政策保存階段 commit。
PR、merge、Issue closure、Project 狀態、來源專案 self-installation 與 release/tag/
publication 仍不是這些動作的自動後續。

## 明確決策與取捨

1. 不新增包辦需求／模型／架構／測試的「通用系統設計者」。兩個新 skill 的判斷 owner
   各自唯一；需要混合工作時共用來源與交接，不複製需求或強制完整流水線。
2. DDD/BDD 保持共通知識。skill 可在無 optional knowledge 時依 caller sources 做
   common work，並揭露專業覆蓋缺口；不得回讀 framework source checkout 補裝。
3. 模型決定業務一致性需求，架構決定實現機制。機制做不到時回饋衝突，不默改規則。
4. GWT 可表達需求、模型或契約例子；test-designer 擁有測試層級、資料、隔離、oracle
   與覆蓋設計，並不壟斷 GWT。
5. Orchestrator 以未解問題選工作，沿用 accepted artifacts 與已有授權；有回饋才回到
   對應 owner。保留現有可跳階段的能力，不增加固定階段、文件數或驗證平台。
6. 新來源 catalog 直接拒絕舊 ID；既有安裝保持真實狀態。下一次升級先顯式選擇兩者之一
   或兩者，再規劃 managed 變更與知識 bindings，不自動改 selection 或 lock。
7. 命名以對象與責任為主；architect 本身是職責詞，不為統一字尾進行純外觀改名。

## 交付順序與工作切片

| 次序 | 工作 | 產出與完成條件 |
| --- | --- | --- |
| 1 | 完整設計與另一 agent 審核 | 固定設計版本、具體 findings 與處置；重大責任／授權歧義解決才動 src |
| 2 | 中文 Feature／User Stories | 主 Feature 與可驗收 Stories；另案 workflow/customization 只排設計工作，雙向引用 |
| 3 | Domain modeling | 新 package 的 explore/design/review、獨立知識 allowlist、行為例子 |
| 4 | Software architecture | 新 package 的 design/review；舊能力責任完整分配；移除舊 package |
| 5 | 相鄰與分發一致性 | requirement/story/spec/test/orchestrator、共通契約、catalog、四個 presets、版本與文件 |
| 6 | 驗證與本機交付 | 直接受影響分發／schema 測試、選擇與退役語意、固定來源審核、真實結果與接續點 |

第 3–5 項構成一致的產品變更，不能發布中間的殘缺 catalog。工作排序以 DDD 為先，
但不把內部每個檔案變更製造成可獨立發布成果。主 Feature 的四個 Stories 分別承載
領域建模、架構設計、相鄰協作、可選分發與遷移；整合時保留其依賴與判準。

## 範圍外與另案待決策

本機 workflow 的記錄整合方式、Git 必要性、SQLite 位置、狀態寫入與資料遷移，
以及客製 manifest、baseline、語意涵蓋、整合／採納／啟用狀態，均由另案設計決定。
本次沒有授權移除 local-backlog、搬動 DB、建立客製 schema 或修改 installer recovery。
大型 system architect／DevOps 只保留需求方向，不建立偽裝成已排定實作的 Stories。

## 接續與證據

以對應 workflow 的執行紀錄保存審核、Issue、commit 與驗證結果；本文件不預填 passed。
實作者先讀此入口與兩份核心設計，再看必要的固定來源。版本或規則已漂移時只核對
受影響處；不能因新 session 重建所有文件或重新索取既有授權。

保留原有未追蹤的 `.dev/workflows/2026-10-19-v020-draft/` 與
`.dev/workflows/2026-10-20-self-install-v0201/`；它們不屬於本次修改。
