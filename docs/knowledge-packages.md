# 知識套件選配與 skill 效果

[回手冊首頁](README.md) · [安裝步驟](installation.md) · [Skill 目錄](skills/README.md)

## 先說結論

目前來源 catalog 的 [skills](skills/README.md) 都可以在不安裝這兩個知識套件的選擇中使用，前提是各自
作業需要的專案規則、輸入、工具、設定與授權齊備。**不安裝知識不會讓
skill 自動失效，但會減少下列 skills 的套件專業覆蓋。** 如果任務明確要求
該覆蓋，就要補齊依賴或把該部分列為 unavailable／blocked，不能說完整完成。

目前十一個 presets 都明確設定 `knowledge: []`。包含 `complete`、
`engineering`，甚至名為 `knowledge` 的 preset，都不會自動安裝工程知識。
`knowledge` preset 選的是 ADR／Lesson 撰寫能力。要知識套件，請另外編輯
安裝 selection 的 `knowledge` 清單，依[安裝說明](installation.md)重新產生 subset。

基本協作入門資源由 `ai-context-init` 提供；只選此 skill 也能建立入口、
缺少的協作基線與第一個任務指引。這不會自動採用工程知識中的專業規範。

## 兩個套件分別提供什麼

下表是目前來源版本；下載成品與已安裝專案仍以各自 catalog／lock 為準。
來源版本更新不代表已發布或自動升級。

| 套件 | 內容與適用範圍 | 相依與限制 |
| --- | --- | --- |
| `engineering-common@0.4.2` | 共通工程規則 catalog、按主題選讀的 BDD／DDD、協作探索、一般與 GWT 測試交接、領域語言、context map、event catalog、runbook 等參考與模板 | 不預選技術、不自動採用規則；可以單獨選取 |
| `dotnet@0.3.0` | 共通 C#／.NET、Web API、選用 DDD/CQRS、persistence、messaging、testing 與工具指引，共 55 個檔案 | 必要相依為 `engineering-common@0.4.2`；依目標已採用的技術選讀，沒有完整 Worker／Console／MQ consumer 實作 |

`.NET` 套件包含 EF Core、Dapper、PostgreSQL、Wolverine、RabbitMQ、Kafka、
Outbox、Event Sourcing 等參考，不會因此替專案選定所有技術。
Event Sourcing 等條件規則仍需條件成立；BDDfy／mocking 選擇仍由目標專案決定。
知識套件提供規範、情境示範與產生工具指引。C# snippets 與 `dotnet new` 範本
由獨立的 generation 發行成品提供。請依目標專案的需求選用與驗證。

`dotnet-backend` 自 `0.1.8` 起修正既有 `MAP-EVENTS-001` 的重建事件生命週期，
移除通用強制 Clear 與必要業務狀態反序列化失敗後繼續成功的指引，並補明
query reader／read-model projector 的責任與恢復條件。若舊目標專案已接受不同
失敗政策或依賴 Clear，採用前須列出受影響重建、dispatcher／repository 呼叫及
遷移方式，由目標所有者處理衝突；安裝或 pin 更新不會替它作決定。
套件的合約案例摘要引用 ArchPrecept `0.0.3-preview` 的固定 CT-005 合約，並說明
無套件 ES snippet 的失敗處理責任。實際外部整合由 #179 獨立選版。

## 從 dotnet-backend 遷移到 dotnet

`dotnet@0.3.0` 是新的 package 身分，沒有 `dotnet-backend` 自動 alias。
`knowledge` 選擇、binding 的 `package` 及 `member:<path>` resource IDs 必須明確遷移。
`engineering-rule-catalog` resource ID、11 個 rule IDs、catalog 的
`engineering-rule-catalog-dotnet-backend` 身分與既有 `dotnet-backend` 規則 profile
保持不變。不可把 binding selector 的 `technology_profile` 一併改為 `dotnet`。

先保存現有 lock、managed bytes、專案自有內容與舊成品，再以選定新成品的
catalog identity 準備 selection 副本。將 package 改為 `dotnet`，保留其他選擇、
authority、rule IDs、path selectors 與 execution modes。依本次所需內容選擇新
resource；合併或拆分不是自動擴大 allowlist 的理由。

常用路徑對照如下；兩欄均為 package 內相對路徑，對應的 resource ID 加上 `member:`。

| 舊路徑 | 新路徑或處置 |
| --- | --- |
| `standards/DESIGN-BY-CONTRACT.md` | `core/design-by-contract.md` |
| `standards/POLICY-RATIONALE.md` | `references/policy-rationale.md` |
| `standards/coding-standards.md` | 一般 C# 選 `core/csharp-conventions.md`；架構、測試與訊息內容分別選其 owner |
| `standards/USECASE-COMMAND-HANDLER-RELATIONSHIP.MD` | Use Case 契約併入 `architecture/ddd-cqrs/usecase-standards.md`；HTTP 邊界與理由分別在 controller 與 rationale |
| `standards/coding-standards/aggregate-standards.md`、`usecase-standards.md`、`reactor-standards.md` | 同檔名移到 `architecture/ddd-cqrs/` |
| `standards/BUILDING-BLOCKS-RECONSTRUCTION-CONTRACT.md` | `architecture/ddd-cqrs/building-blocks-reconstruction.md` |
| `standards/project-structure.md` | `architecture/ddd-cqrs/project-structure.md` |
| `standards/coding-standards/controller-standards.md` | `application-types/web-api/controller-standards.md` |
| `standards/coding-standards/` 中 repository、mapper、projection、archive standards | 同檔名移到 `integration/persistence/` |
| `standards/coding-standards/transactional-messaging-standards.md` | `integration/messaging/transactional-messaging-standards.md` |
| `standards/coding-standards/test-standards.md`、`review/test-scenario-review.md` | 同檔名移到 `testing/` |
| `review/review-routing.yaml`、`design/design-routing.yaml` | 同檔名移到 `references/` |
| `legacy-guidance/spec-compliance-validator/references/` 三份文件 | 同檔名移到 `references/legacy-dotnet-compliance/`，仍需明確 legacy 選用 |
| 歷史 role YAML／prompt | 已退役，沒有 executable alias；改選現行 skill 與所需技術 reference |
| `tooling/generation/`、`tooling/on-demand-mechanical-validation/` | package 內路徑保留；後者仍為 reference-only |

完整來源處置及公開版本差異見
[122 檔處置清單](../.dev/assessments/ASM-20261109-23-dnr/file-disposition.md)與
[公開成員對照](../.dev/assessments/ASM-20261109-23-dnr/evidence/published-member-map.csv)。
它們保留更名前的評估基準；目前可用 resource 以新包 metadata 為準。

使用同一成品內的 engine／catalog／pin 執行 derive、inspect、plan，審閱舊 managed
members 的移除與新 members 的增加。遇到未轉換 ID、managed drift、未知同名檔案或
未完成維護狀態時保留拒絕結果，依原恢復程序處理；不刪檔繞過檢查、不手改 lock。
目標自有 AGENTS、文件、skill/sub-agent、腳本及已複製的程式碼需另行核對，installer
不會自動決定或改寫這些引用。核准的 apply 完成後，再 inspect 並讀回實際選用資源。

公開 v0.21.0（knowledge 0.1.6）及 v0.22.0（0.1.9）都採 Catalog 1／Engine 2，
但這不是更名後升級通過的證明。兩條直接升級試驗維持獨立工作，不加入常態測試矩陣；
本次來源整理不宣稱它們已通過。舊 `examples/`、`source-includes/` 在更名前已退役，
已複製的程式碼不會隨 managed knowledge 更新，替代能力也不保證完整等價。

## 哪些 skills 會失去完整的配套效果

`capability` 是較粗的消費分類，例如兩個新 skills 都使用 `architecture`。
實際可讀覆蓋還須同時符合 operation、resource selectors、skill allowlist、
選定 binding 與已安裝版本／成員；目標專案的 adopted authority 決定規則是否適用。
allowlist 不能單獨授權採用規則，套件存在也不代表資源適用於所有操作。

以下是 metadata 明確宣告的 optional consumption；版本分別是
`engineering-common@0.4.2` 與 `dotnet@0.3.0`。宣告與 resource allowlist 以當前各 skill metadata 核對，不另維護易漂移的引用總數。
這不是實際已採用的 target binding 數，也不是執行過的檢查數。

| Skill／操作 | 缺少 `engineering-common` | 缺少 `dotnet` | 仍可做的工作 |
| --- | --- | --- | --- |
| [requirement-author](skills/requirement-author.md) `explore`／`draft`／`normalize` | 所選探索、BDD 與 DDD 方法覆蓋不可用 | 無直接 .NET binding | 依 caller 來源探索與整理需求；保留已決事項 |
| [test-designer](skills/test-designer.md) `design`／`review` | 共通工程 catalog、BDD 方法、Gherkin 表述與 GWT 交接準則不可用 | .NET catalog 與測試規範覆蓋不可用 | 依提供的需求與專案慣例設計、審查情境 |
| [code-reviewer](skills/code-reviewer.md) `review` | 共通工程 catalog 覆蓋不可用 | .NET catalog、DbC、aggregate／repository／test／use-case 規範覆蓋不可用 | 對照預期行為與目標規則找程式缺陷 |
| [domain-model-designer](skills/domain-model-designer.md) explore/design/review | DDD、語言、Context Map、BDD 方法覆蓋不可用 | design/review 的 aggregate／DbC 覆蓋不可用 | 依 caller sources 探索／設計／審查領域模型 |
| [software-architect](skills/software-architect.md) design/review | 技術選擇與邊界／review 方法覆蓋不可用 | building blocks、DbC、messaging、usecase、project structure 覆蓋不可用 | 依接受模型與限制設計軟體機制 |
| [user-story-author](skills/user-story-author.md) plan/draft/normalize/review | 所選 discovery/formulation 覆蓋不可用 | 無直接 .NET binding | Story 與 AC authoring/review |
| [spec-author](skills/spec-author.md) draft/normalize | BDD formulation、DDD discovery/tactical 與 authoring boundary 不可用 | 無直接 .NET binding | 依 accepted design 表達系統契約與例子 |
| [local-change-implementer](skills/local-change-implementer.md) `implement` | 共通工程 catalog 覆蓋不可用 | .NET catalog、aggregate／repository／test／use-case 規範覆蓋不可用 | 依接受的行為與技術，完成局部修改及直接檢查 |
| [slice-implementer](skills/slice-implementer.md) `implement` | 共通工程 catalog、一般與 GWT 測試交接準則不可用 | .NET catalog、DbC、aggregate／repository／test／交易訊息／use-case 規範覆蓋不可用 | 依已接受架構與情境，實作一個行為 slice |

未列於上表的 skills 沒有直接宣告這兩包的 knowledge consumption；這不表示任務無需
目標專案的領域、規則、事實或其他所選能力。

例如 `spec-compliance-validator` 仍須有明確 criteria 和 authentic evidence；
`pr-author` 的 provider 操作仍需正確設定與授權；orchestrator 若選到
`code-reviewer` 的 .NET 專業審查階段，仍會受到該階段的知識缺口影響。
「沒有直接宣告依賴」不等於所有任務都不需要外部資訊或其他能力。

## 安裝、讀取與採用是三件事

1. **安裝內容：** selection 選到套件，subset 包含內容，installer 寫入
   `.ai/core/knowledge/<id>/`，lock 保存實際 identity 與成員。
2. **讀取參考：** skill 只讀與本次操作有關、已驗證的 installed resource。
   Metadata allowlist 不要求每次載入整包知識；缺少 lock、檔案 drift 或不明
   authority 時，不能偷偷改讀來源庫檔案補足。
3. **採用規範：** selection 的 `bindings` 與專案 authority 決定某條規則在什麼
   capability、operation、execution mode、path、technology、file type 下適用。
   安裝檔案或在 prompt 寫「遵守 .NET 規範」不會自動完成所有規範採用。

若只是需要參考範例，可以明確要求「作為 guidance，保留專案既有決策」。
若要宣稱符合配套規範，先選定採用規則、authority 的路徑／digest／selector
與實際範圍，再儲存對應 binding；**不要複製另一個專案的雜湊或採用清單**。
Binding 欄位與設定方式見[安裝說明](installation.md)。

典型使用要求：

```text
使用 code-reviewer 審查指定 commit 的訂單取消流程。
此專案沒有安裝 engineering-common 或 dotnet。
請依我提供的契約與專案規則審查，列出實際覆蓋；不要宣稱完成套件的 .NET 專業覆蓋。
```

```text
使用 slice-implementer 實作已接受的庫存保留 slice。
請確認安裝 lock 與此操作的已採用知識 bindings，
只載入符合目前路徑與技術條件的資源；列出缺少或無法驗證的專業覆蓋。
沿用專案選定的 persistence、transaction 與測試工具。
```

## 選配建議

- 一般文件、需求、ADR／Lesson、backlog、context 維護：先只選 skills。
- 想使用共通工程方法：加 `engineering-common`，按任務選讀，按專案決策採用規範。
- .NET 後端希望取得 framework 配套架構／實作／審查效果：兩包一起選，
  再配置適用 bindings；不要只以套件已安裝作為驗收。
- 非 .NET 專案：不必因為選了架構、BDD、review 或 implementer 就安裝 .NET 套件。
  請提供該專案自己的技術規則。

## 核對來源

- [共通知識說明](../src/knowledge/engineering-common/README.md)及
  [metadata](../src/knowledge/engineering-common/content-package.yaml)
- [.NET 知識說明](../src/knowledge/dotnet/README.md)及
  [metadata](../src/knowledge/dotnet/content-package.yaml)
- 各 skill 手冊連到實際 `skill-package.yaml`；安裝後應核對安裝副本，
  不以 source HEAD 取代已安裝版本。

此表是宣告與使用契約盤點，沒有量測模型輸出品質或推論出各 skill 的效能百分比。

## v0.19.0 的共通方法與版本邊界

v0.19.0 的 `engineering-common` 已包含資源所有權、技術選擇、
skill／sub-agent 分類與外部 AI 回饋方法。入口是
[來源知識目錄](../src/knowledge/engineering-common/README.md)。
這些資源已列入 v0.19.0 的 Release manifest；沒有回填 RC4 ZIP。
本來源專案沒有自我安裝知識包，來源可讀、成品可用與專案採用是三件事。
新增的共通方法不會自動改變各 skill 的 consumption 宣告或目標專案的規則採用；
仍以所選版本的 metadata、installation lock 與專案 bindings 為準。
