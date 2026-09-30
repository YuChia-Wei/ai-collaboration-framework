# Use Case 與 Command Handler 邊界 Workflow

## Metadata

- Plan ID: `workflow-plan-2026-07-usecase-command-handler-boundary`
- Workflow ID: `2026-07-usecase-command-handler-boundary`
- Owner skill: `dev-workflow`
- Status: `completed`
- Created: `2026-07-06`
- Branch: `codex/usecase-command-handler-alignment`
- Base: `main` at merge commit `343ab29`
- Issue: not provided
- Translation note: 本檔案是供人員閱讀的台灣繁體中文翻譯版本；英文版 [workflow-plan.md](./workflow-plan.md) 仍是 canonical planning file。

## 問題說明

目前的有效規範定義了兩種彼此不相容的同步 Application 入口模型：

1. `Controller -> Command/Query -> Handler`，其中 Handler 通常是 Use Case 的實作。
2. `Controller -> IUseCase -> Use Case implementation`，其中 Handler 是獨立的傳遞／派送物件。

使用者在 repository-pattern workflow 核准的目標是第二種模型：

- Use Case 與 Handler 是分開的物件；
- API Controller 注入 Use Case 介面；
- 一般同步 API 行為不會透過 bus 發布 Command；
- message/event Handler 的責任要和 Use Case 的流程編排維持分離。

目前的指引、範例、提示詞、專案結構、測試與 analyzer 並未一致地落實這個目標。

證據基準記錄在 [review-report.md](./review-report.md)。

使用者的 D1-D12 決策已和附帶的討論資料進行比較，結果記錄在
[decision-difference-analysis.md](./decision-difference-analysis.md)。實質差異已於
`2026-07-07` 重新決策，並記錄如下。

## 範圍

### 納入範圍

- 定義 `Use Case`、`Input`、`Command`、`Query`、`Handler`、`Application Service`、
  `Controller`、`Consumer` 與 `Reactor` 的責任；
- 定義同步 API 的預設呼叫鏈；
- 定義 command/query/message handler 何時存在，以及它們可以委派什麼；
- 定義 query 流程是否使用相同的明確 Use Case 邊界；
- 對齊 DI、命名、專案結構、提示詞、範例、測試與 analyzer；
- 讓 Wolverine 與其他 dispatch 套件維持條件式使用，依目標 repository 的證據決定。

### 不納入範圍

- 不實作 production application；
- 不重新設計 message broker 或 transport；
- 不重新設計 repository pattern；
- 不做大範圍的規範翻譯；
- 不做目標專案專屬的 Wolverine API 設定；
- 除非之後明確要求，不進行 sub-agent 作業。

## 統御限制

- DDD + Clean Architecture + CQRS 仍是基礎架構。
- Use Case 是 Application 的流程編排邊界。
- Presentation adapter 不直接依賴 repository 或 Domain object。
- 跨 bounded context 的溝通仍然只走 MQ。
- in-process 的同步 API 行為不需要發布 message。
- Aggregate 之間預設維持最終一致性。
- 例外的強一致性需求，由 Use Case 明確依賴 `IUnitOfWork` 表達，不隱藏在 Handler 中。
- Wolverine 這類 runtime 套件是依目標 repository 決定的條件式選項。

## 已核准的目標方向

```text
HTTP Request
  -> Controller
  -> I<CreateOperation>UseCase
  -> <CreateOperation>UseCase
  -> Aggregate / Domain Service / outbound ports
  -> Use Case Output
  -> HTTP Response
```

當確實需要 dispatch 或 message 入口時：

```text
Command / Message / Scheduled Trigger
  -> Handler (inbound adapter)
  -> I<CreateOperation>UseCase
  -> Use Case implementation
```

規劃的責任切分如下：

- `Use Case interface`：穩定的 inbound Application port；
- `Use Case implementation`：Application 流程編排、交易需求、Aggregate/query 協作與輸出合約；
- `Input` / `Output`：與 transport 無關的 Use Case 合約；
- `Command`：只有在刻意選用 command dispatch 時才使用的意圖訊息；
- `Handler`：所選傳遞機制的 adapter，負責對應其輸入並呼叫 Use Case，不會成為預設的 Use Case 實作；
- `Controller`：HTTP adapter，負責將 HTTP DTO 對應成 Use Case input，且只注入 Use Case 介面；
- `Consumer` / event Handler / Reactor：message adapter 或最終一致性的 worker，與同步 API Use Case 維持分離。

## 已核准的決策

### D1 — Use Case 介面形狀

`ExecuteAsync` 是強制的 operation 名稱。每個非同步 Use Case 都必須宣告一個不可省略的
`CancellationToken` 參數。

預設使用專屬且與 transport 無關的 input 物件：

```csharp
public interface ICreateProductUseCase
{
    Task<CreateProductOutput> ExecuteAsync(
        CreateProductInput input,
        CancellationToken cancellationToken);
}
```

允許以下兩項例外：

- 如果操作除了 cancellation 之外沒有其他輸入，則省略 input 物件；
- 如果操作只有一個輸入值，且該值使用標準 platform type，Use Case 可以直接接受該值。

此例外中的標準 platform type，是指一個 scalar built-in 或 BCL 值，例如 `string`、數值型別、
`bool`、`Guid` 或日期／時間型別。collection、tuple、custom record/class 或多個輸入值都必須
使用專屬 input 物件。

```csharp
Task ExecuteAsync(CancellationToken cancellationToken);

Task<FindProductOutput> ExecuteAsync(
    Guid productId,
    CancellationToken cancellationToken);
```

### D2 — Input 與 Command

Use Case 不會接受 HTTP request、broker contract、Wolverine Command 或其他 delivery
contract 作為其 Application input。它接受自己與 transport 無關的 input 物件，唯一例外是
D1 所述的無輸入與單一標準型別情境。

Controller 將 HTTP request 對應成 Use Case input。當確實存在 dispatch 入口時，其 Handler
會將 message Command 對應成相同的 Use Case input。

### D3 — Command Handler 的存在與角色

只有在實際設定 command/message dispatch 入口時，Command Handler 才會存在。它不是每個
command-style Use Case 的必要元件，也不會只為了包裝 Controller 呼叫而加入。

### D4 — Controller 相依規則

Controller 預設依賴一個或多個明確的 Use Case 介面。它不得注入：

- concrete Handler；
- `IMessageBus`；
- mediator/dispatcher abstraction；
- write repository；
- Domain service。

經明確選擇的純查詢 endpoint 可以直接注入 `IQueryRepository` 或 query service。這是允許但
不建議的例外，而不是另一種預設做法。若未針對該 endpoint 明確決策，Controller 就必須使用
query Use Case。

### D5 — Query 端對稱性

預設的同步 query 流程是：

```text
Controller -> I<GetProduct>UseCase -> GetProductUseCase -> IProductQueryRepository
```

只有純查詢情境中，經明確核准的 endpoint 才可以直接呼叫 `IQueryRepository` 或 query
service。開發者必須記錄為何額外的耦合與失去 inbound-port 對稱性仍屬合理。直接
query-handler dispatch 並非已核准的例外。

### D6 — Handler 放置位置

與套件無關、依 convention 運作的 Handler 可以留在 Application。Wolverine、MediatR、
MQ 或其他 framework/transport 專屬的 Handler 應放在 inbound adapter 或 composition
boundary。不論放置位置為何，Handler 都負責對應 delivery input 並呼叫一個 Use Case；
它不擁有 business workflow。

### D7 — 結果與錯誤的擁有權

Use Case 只回傳完成操作後產生、與 transport 無關的 output。如果操作不會產生 output
物件，則回傳 `Task`，而不是人為建立空 result。Controller 將結果對應成 HTTP，message
Handler 則將失敗行為對應成 retry/dead-letter semantics。Use Case 不會回傳
`IActionResult`、broker acknowledgement 或 framework-specific envelope。

### D8 — 交易與事件生命週期的擁有權

Repository 協調、例外且明確的 `IUnitOfWork`、outbox 協調，以及待處理 Domain Event
acknowledgement 的相依性，都屬於 Use Case implementation。Handler 不會引入隱藏的強一致性，
也不會在呼叫 Use Case 之後獨立 commit。

### D9 — 具體實作命名

具體實作使用 `CreateProductUseCase` 與 `*UseCase` 後綴。此 workflow 不會導入、擴充或重新
定義 `Application Service`；該概念不在本次決策範圍內。

### D10 — 相容性與遷移

相容性與具體遷移步驟延後處理。必須在實際重構時，依目標產品進行規劃；屆時應提醒開發者在
變更前先分類 callers、registrations 與真實的 dispatch entries。此 workflow 不會發布通用
遷移作法。

### D11 — Analyzer 強制規則

可確定的邊界違規屬於 analyzer error，包括：

- Controller 相依於 Handler、dispatcher 或 message bus；
- Use Case interface 與 implementation 的形狀；
- Handler 到 Use Case 的相依方向；
- Use Case 中的 transport/package 相依；
- 同時實作 Use Case 與 Handler 入口的 legacy class。

如果目標專案提供可靠證據，證明 endpoint 已選擇 D4/D5 的明確純查詢例外，就不得將該例外
回報為 error。若缺乏可確定的目標證據，僅涉及命名或遷移的建議仍維持 warning。

### D12 — Wolverine 與 dispatcher 政策

Use Case 依賴專案自行擁有的 outbound event publisher port，而不是直接依賴 Wolverine
`IMessageBus`。當目標 repository 選用 Wolverine 時，由 Infrastructure 將這些 port
轉接至 Wolverine。

Wolverine 仍是 messaging、outbox、consumer 與刻意選用 dispatch 的有效條件式指引。它不是
一般同步 API Use Case 的可攜式必要條件，也不會因 command/query implementation prompt 而
自動導入。Use Case 不得發布 Command，也不得注入另一個 Use Case。

## Skill Routing

| Stage | Capability | Skill | Confidence | Evidence |
| --- | --- | --- | --- | --- |
| S0 | workflow orchestration | `dev-workflow` | High | 必要的 workflow gate 與既有的 deferred task |
| S0-S2 | architecture | `ddd-ca-hex-architect` | High | Use Case/Handler/Controller/adapter 邊界設計 |
| S3 | context governance | `ai-context-governance` | High | 提示詞、可重用 AI 資產、指南與範例 |
| S4 | implementation | `slice-implementer` | High | 有界的 analyzer 與驗證修改 |
| S5 | workflow validation | `dev-workflow` | High | 跨檔案一致性與收尾 |

## 階段

### S0 — Workflow bootstrap 與 pre-analysis

- 狀態：completed
- 產出：
  - `workflow-plan.md`；
  - `review-report.md`；
  - `tasks/bootstrap-usecase-command-handler-workflow.json`。
- 驗證：
  - branch 從已合併的 `main` 開始；
  - workflow 產物可解析，且連結可解析；
  - findings 有引用目前 repository 的有效證據。

### S1 — 釐清 architecture decisions

- 狀態：completed
- Owner：`ddd-ca-hex-architect`
- 產出：
  - 已核准的 D1-D12 決策；
  - `decision-difference-analysis.md`；
  - `tasks/resolve-usecase-command-handler-decisions.json`。
- Gate：
  - 已通過：R1-R4 已重新決策，且 D1-D12 均已記錄。

### S2 — 對齊 canonical standards

- 狀態：completed
- Owner：`ddd-ca-hex-architect`
- 主要範圍：
  - `src/knowledge/dotnet-backend/design/architecture-overview.md`；
  - `.dev/standards/USECASE-COMMAND-HANDLER-RELATIONSHIP.MD`；
  - usecase/controller/test/project-structure standards；
  - DI and technology-profile rules。

### S3 — 同步 context、提示詞、指南與範例

- 狀態：completed
- Owner：`ai-context-governance`
- 主要範圍：
  - command/query/controller sub-agent prompts；
  - slice-implementer modes；
  - .NET backend templates and checklists；
  - controller/usecase/testing/DI examples and guides。

### S4 — 對齊 analyzer 與可執行驗證

- 狀態：completed
- Owner：`slice-implementer`
- 主要範圍：
  - Controller and Use Case analyzer rules；
  - positive, negative, migration, and false-positive tests；
  - analyzer documentation and severity template。

### S5 — 最終驗證與收尾

- 狀態：completed
- Owner：`dev-workflow`
- 驗證：
  - 所有 task JSON 都可解析；
  - analyzer 測試通過；
  - 變更過的 Markdown 連結都可解析；
  - 針對 role 與 invocation 的搜尋結果與已核准決策一致；
  - `git diff --check`；
  - 已記錄延後處理的遷移風險。

## Commit Checkpoints

1. `workflow(workflow): bootstrap use case handler alignment`
2. `workflow(workflow): record use case handler decisions`
3. `docs(architecture): align use case handler boundaries`
4. `docs(ai-context): synchronize use case handler guidance`
5. `feat(dotnet-backend): enforce use case handler boundaries`
6. `workflow(workflow): close use case handler alignment`

每個 workflow 階段的 commit 都要包含 `Why`、`What`、`Validation` 與 `Workflow` 區塊。

## 完成條件

- Controller、Use Case、Input/Output、Command/Query 與 Handler 各自只有一個 canonical role。
- 同步 API 呼叫只有一條預設相依鏈。
- framework-specific dispatch 是條件式選項，不能默默取代 Application port。
- 交易與事件生命週期的擁有權已明確定義。
- 提示詞、範例、測試、DI 指引與 analyzer 均符合已核准模型。
- 遷移指引能區分 legacy 相容性與新的預設行為。

## 完成摘要

- D1-D12 已核准，並同步落實於 canonical standards 與 active reusable
  guidance。
- 同步 Controller 預設依賴明確的 Use Case interface；唯一的直接 data access
  例外，是經明確指定的純查詢 endpoint 使用唯讀 Query Repository/Service。
- Use Case 使用 `ExecuteAsync`、transport-neutral contract、必要的
  `CancellationToken` 與 project-owned outbound event publisher port，且不直接
  依賴 Wolverine 或其他 Use Case。
- Command/Query Handler 只在真實 dispatch entry 存在，並轉接至一個 Use
  Case；合法 Reactor 與 Consumer Handler 維持不同角色。
- Analyzer diagnostics `DBA1014` 到 `DBA1017` 已落實 deterministic
  boundaries，47 個 analyzer tests 全數通過。
- D10 的 product-specific migration sequencing 維持延後處理。
- Target repository 必須提供 evidence，證明純查詢 endpoint 已明確選擇直接
  Query Repository/Service 例外。
