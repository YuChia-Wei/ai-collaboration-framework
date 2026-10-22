# 討論脈絡、盤點結果與設計依據

本文件與 [設計入口](README.md)、[職責契約](skill-contracts.md)、
[實作設計](implementation-design.md) 一起構成跨對話可讀的設計。
來源盤點基準為 `f96fffe0af6e9e4f79d5f2f4be05bb3665553123`。
以下區分 owner 意圖、來源觀察、研究解讀及設計選擇，不把其中一種當成另一種證據。

## 1. 問題如何形成

Owner 最初指出 DDD 與 CA/Hexagonal 應屬不同範疇；BDD 已獨立成共通知識，DDD/BDD
也應可在需求與 spec 分析／設計使用，因此要求盤點現有 skills，評估是否需新增分析／
系統設計責任。同時要求從敏捷與 AI 輔助 SDLC 的討論檢查開發編排流程。

盤點後的建議是依「判斷與產出」拆分領域模型與軟體架構，避免建立一個同時包辦需求、
模型、架構、規格與測試的大入口。Owner 同意方向，先授權規劃存檔與選讀表維護，
另提出本機 workflow 與客製升級的評估。後續 owner 指出原規劃的「採納建議」等表述
不足以供新 AI／其他人理解，要求保存完整設計與參考脈絡、實作前由其他 agent 審核、
建立中文 Feature/User Stories，並明定兩個名稱與舊 ID 無 alias 退役。

最後的實作授權只包含領域／架構拆分與直接相鄰配套。本機 workflow 與客製升級列為
另案；system architect（含網路／大型系統）與 DevOps 為中長期方向，未設計其 package。

## 2. 盤點發現及其意義

| 基準來源事實 | 證據定位 | 對此次設計的影響 |
| --- | --- | --- |
| 原 architect 把語言／invariant／aggregate 與 port／transaction／retry／recovery 放在同一 design | 舊 src/skills/ddd-ca-hex-architect/references/design.md 的 Inputs、Design sequence；review.md 的 criteria | 拆 owner，完整分配責任，避免僅改名或遺失 failure 語意 |
| requirement-author 已有 BDD/DDD discovery 與 formulation | skill-package.yaml 的兩個 knowledge_consumption rows；references/explore.md、authoring.md | 不把已有能力說成全新缺口；補明模型設計分界 |
| test-designer 已把 BDD 視為可選方法，負責 level/data/oracle/coverage | references/design.md 與 skill-package.yaml | 維持 test design owner，但不壟斷行為例子 |
| spec-author 沒有 knowledge consumption，scenario notes 排除用語容易混同測試規格與行為例子 | metadata 3；references/authoring.md | 加 optional methods，精確允許契約例子，仍不接管 test spec |
| user-story-author 沒有 knowledge consumption，但有 plan/draft/normalize/review | metadata 3、story-contract.md | 支援可選 discovery/formulation，不增加 upstream skill 前置 |
| orchestrator 已允許跳過不必要階段、重用 accepted artifacts 與條件驗證 | references/orchestrate.md | 不能稱其現況為瀑布流程；增加未知分類與回饋，而非重寫固定 SDLC |
| common capability/operation 是合法 ID 字串，不是固定 enum；binding 是每個 resource 的子集檢查 | src/distribution/schemas/contracts.schema.json；content.py/resource_bindings | capability 可保留 architecture；兩 skill 用 allowlist 分離，無需改 schema |
| knowledge_consumption 被轉為 exact optional dependency | src/distribution/content.py/descriptor、closure | common 升版須同步所有存活 consumers及dotnet的required dependency，不能只改新 skills |
| installed resources reader 依完整 lock closure 與 authority raw hash | src/distribution/catalog.py/read_installed_resources 與原 skill installed protocol | 新 package 保留完整安全／身份與覆蓋界線，不另造 parser |
| 選擇舊 ID 的拒絕來自 catalog resolver，schema 只驗格式 | src/distribution/catalog.py/resolve_selection | 無需歷史 ID blacklist；不破壞舊 lock 可讀性 |

本輪先檢查 code graph；index status 未能證明獨立 extraction SHA，部分 current code
查詢無結果。因此程式部分明確使用 Git-tracked 檔案核對；不以 graph absence 推論
功能不存在。Markdown／metadata／schema 的查詢是文件盤點。以上不構成 runtime 測試。

現有 20 個 distributed skills 的個別職責由 docs/skills/README.md 承載，另有未發行
standards-promotion。來源可用性、17-skill source-project installation、實際 invocation
與驗證結果是四種不同事實。拆分後現行選讀表更新，這份固定基準紀錄不回寫成新數量。

## 3. 為何不採其他拆法

| 替代方案 | 不採原因／保留價值 |
| --- | --- |
| DDD、CA、Hexagonal 各一個 skill | 把方法當工作 owner，容易讓同一架構決策反覆交接；方法仍可分 topic 按需讀 |
| 新增通用 system-analysis skill 包辦所有上游工作 | 重疊 requirement/spec/test，且本輪只需要領域模型與軟體結構兩種判斷 |
| 保留舊 architect 作 alias/router | Owner 明確要求直接退役；alias 到單一新 skill 也會隱藏另一半責任 |
| 每個任務強制 domain → software → spec → test → implement | 已接受輸入可直接使用；小改動不應因 framework 增加交接與文件 |
| 用新 domain-modeling capability 表達新 identity | 技術上可做，但會擴大現有 knowledge/target binding 遷移；既有 architecture 分類加精確 allowlist 已足夠 |
| 為所有 GWT 強制 test-designer | GWT 可用於澄清需求與契約；只有設計系統邊界、資料、oracle、隔離及測試層級時才需 test owner |
| 順便整合 local workflow 或客製 installer | 涉及不同資料／recovery 契約，owner 已明確另案；不是此次拆分的必要前提 |

## 4. 一個完整的跨責任例子

情境：使用者要釐清訂單取消與付款競爭；現有 stakeholder 規則只有「出貨後不能取消」。

1. Requirement owner 釐清什麼叫出貨、取消成功的可觀察結果、付款與退款政策；沒有
   來源的「付款成功一律可退款」不能由 AI 補成 accepted rule。
2. Domain model designer 以取消前／後、同時付款、重複取消等例子探索語言；提出
   狀態、invariant 與責任。如果要求「取消成功就不能再出貨」，說明哪項業務事實必須
   共同成立，而不先選資料庫、broker 或 microservices。
3. Software architect 在已接受模型下設計資料／交易邊界與付款 port；若跨系統只能
   最終一致，明列無法維持原子要求的時間窗與替代方案，回饋 owner，不能自行降級規則。
4. Spec author 精確記錄已接受的輸入、狀態／結果、錯誤、外部契約與可觀察例子；
   沒有接受的補償政策保持未定，不從技術建議推定業務同意。
5. Test designer 選併發／重複請求的測試層級、資料、可控制的時間與依賴，以及
   獨立預期結果來源。新反例若暴露業務歧義，回到 requirement/model owner。
6. Orchestrator 只安排當下有阻礙的工作。若只有替換付款 API 且模型不變，可直接
   進 software architecture；若契約充分且已授權小改動，可直接實作與必要驗證。

每項輸出保留相同的 source IDs／接受狀態，不要求另造一份 PRD、模型或 Spec。
這個例子說明責任與回饋，並非某個真實訂單系統的已接受需求或已驗證實作。

## 5. 外部一手與作者資料

以下網頁於本次最初唯讀研究（2026-10-22，Asia/Taipei）讀取。它們是設計背景，
不會因被引用就成為 target adopted rule，也不證明本 framework 的 runtime 效果。
不將研究解讀表述成社群已有唯一最佳 AI SDLC。

| 來源 | 參考內容 | 本設計的解讀與限制 |
| --- | --- | --- |
| [Cucumber：BDD](https://cucumber.io/docs/bdd/) | discovery、formulation、automation 與協作例子 | 方法跨工作使用；不等於固定 skill/agent 呼叫順序 |
| [Eric Evans：DDD Reference](https://www.domainlanguage.com/wp-content/uploads/2016/05/DDD_Reference_2015-03.pdf) | 語言、模型、bounded context 與責任 | 支持領域建模 owner；不要求每個 context 成為微服務 |
| [Alistair Cockburn：Hexagonal Architecture](https://alistair.cockburn.us/hexagonal-architecture) | 應用內外分離、ports/adapters | 技術邊界由 software architect 判斷，非全專案強制 folder layout |
| [Robert C. Martin：Clean Architecture](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html) | 政策／機制與依賴方向 | 按目標限制使用，不以框架名稱替代品質論據 |
| [Agile Manifesto：Principles](https://agilemanifesto.org/principles.html) | 持續交付、回饋、簡單與調整 | 採有凝聚性的增量與最小必要工作，不取消來源與驗證要求 |
| [DORA：Balancing AI tensions](https://dora.dev/insights/balancing-ai-tensions/)（2026-03-10） | AI 帶來的產出速度與交付／驗證張力 | 生成量不等於交付效果；本設計不從研究推算本專案效能數字 |
| [Birgitta Böckeler：SDD tools analysis](https://www.martinfowler.com/articles/exploring-gen-ai/sdd-3-tools.html) | spec-first、spec-anchored、spec-as-source 等差異 | 保留可追溯規格但不強制把所有文件變成產生程式的唯一真相 |

## 6. 另案脈絡如何保留

[本機 workflow 與客製升級評估](local-workflow-and-customization.md) 已包含現況矩陣、
替代方案、推薦理由、來源與 C-AC/D-AC。這些是未採納產品設計候選：本機資料整合
建議記錄歸 workflow-records、判斷歸 orchestrator；客製狀態建議分離 origin、delta、
upstream coverage、reconciliation 與 activation。後續 Feature 先完成 owner 決策，
不能直接把候選欄位塞進 lock、將 live DB 放 repo，或刪除 local-backlog/store。

設計保存目的不是把本對話逐字複製，而是保存能改變工作判斷的意圖、證據、取捨、
已接受事項、未接受事項與下一步。其審核結果另附固定 subject 與處置，不能只寫
「另一 agent 看過」。
