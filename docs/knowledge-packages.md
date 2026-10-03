# 知識套件選配與 skill 效果

[回手冊首頁](README.md) · [安裝步驟](installation.md) · [Skill 目錄](skills/README.md)

## 先說結論

18 個發行 skills 都可以在不安裝這兩個知識套件的選擇中使用，前提是各自
作業需要的專案規則、輸入、工具、設定與授權齊備。**不安裝知識不會讓
skill 自動失效，但會減少 5 個 skills 的套件專業覆蓋。** 如果任務明確要求
該覆蓋，就要補齊依賴或把該部分列為 unavailable／blocked，不能說完整完成。

目前九個 presets 都明確設定 `knowledge: []`。包含 `complete`、
`engineering`，甚至名為 `knowledge` 的 preset，都不會自動安裝工程知識。
`knowledge` preset 選的是 ADR／Lesson 撰寫能力。要知識套件，請另外編輯
安裝 selection 的 `knowledge` 清單，依[安裝說明](installation.md)重新產生 subset。

## 兩個套件分別提供什麼

| 套件 | 內容與適用範圍 | 相依與限制 |
| --- | --- | --- |
| `engineering-common@0.1.0` | 共通工程規則 catalog、GWT 交接、領域語言、context map、event catalog、runbook 等參考與模板 | 不預選技術、不自動採用規則；可以單獨選取 |
| `dotnet-backend@0.1.0` | DDD／Clean／Hexagonal／CQRS、ASP.NET Core、aggregate、repository、command/query/reactor、交易訊息、.NET 測試慣例與範例 | 必要相依為 `engineering-common@0.1.0`；不是 UI、Razor、Blazor、MAUI 或完整 full-stack 模板 |

`.NET` 套件包含 EF Core、Dapper、PostgreSQL、Wolverine、RabbitMQ、Kafka、
Outbox、Event Sourcing 等參考，不會因此替專案選定所有技術。
Event Sourcing 等條件規則仍需條件成立；BDDfy／mocking 選擇仍由目標專案決定。
範例與 source includes 不會自動複製進產品，也不是已通過你的產品測試的程式。

## 哪些 skills 會失去完整的配套效果

以下是 metadata 明確宣告的 optional consumption；兩個 package 的版本都是
`0.1.0`。共 **10 個 consumption 宣告、34 次 resource ID 引用**。
這不是實際已採用的 target binding 數，也不是執行過的檢查數。

| Skill／操作 | 缺少 `engineering-common` | 缺少 `dotnet-backend` | 仍可做的工作 |
| --- | --- | --- | --- |
| [bdd-gwt-test-designer](skills/bdd-gwt-test-designer.md) `design`／`review` | 共通工程 catalog 與 GWT 交接準則不可用 | .NET catalog 與測試規範覆蓋不可用 | 依提供的需求與專案慣例設計、審查情境 |
| [code-reviewer](skills/code-reviewer.md) `review` | 共通工程 catalog 覆蓋不可用 | .NET catalog、DbC、aggregate／repository／test／use-case 規範覆蓋不可用 | 對照預期行為與目標規則找程式缺陷 |
| [ddd-ca-hex-architect](skills/ddd-ca-hex-architect.md) `design`／`review` | 共通工程 catalog 覆蓋不可用 | .NET catalog、building blocks、DbC、aggregate、交易訊息、use-case、project structure 覆蓋不可用 | 領域／依賴／不變量與架構替代方案分析 |
| [local-change-implementer](skills/local-change-implementer.md) `implement` | 共通工程 catalog 覆蓋不可用 | .NET catalog、aggregate／repository／test／use-case 規範覆蓋不可用 | 依接受的行為與技術，完成局部修改及直接檢查 |
| [slice-implementer](skills/slice-implementer.md) `implement` | 共通工程 catalog 與 GWT 交接準則不可用 | .NET catalog、DbC、aggregate／repository／test／交易訊息／use-case 規範覆蓋不可用 | 依已接受架構與情境，實作一個行為 slice |

其餘 13 個沒有宣告 `knowledge_consumption`：`adr-author`、
`ai-context-auditor`、`ai-context-governance`、`ai-context-init`、
`diagnostic-analyst`、`lesson-author`、`local-backlog`、`pr-author`、
`problem-frame-author`、`requirement-author`、`software-development-orchestrator`、
`spec-author`、`spec-compliance-validator`。

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
此專案沒有安裝 engineering-common 或 dotnet-backend。
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
- [.NET 知識說明](../src/knowledge/dotnet-backend/README.md)及
  [metadata](../src/knowledge/dotnet-backend/content-package.yaml)
- 各 skill 手冊連到實際 `skill-package.yaml`；安裝後應核對安裝副本，
  不以 source HEAD 取代已安裝版本。

此表是宣告與使用契約盤點，沒有量測模型輸出品質或推論出各 skill 的效能百分比。

## 尚未發佈的來源整理

目前來源分支在 `engineering-common` 增加資源所有權、技術選擇、
skill／sub-agent 分類與外部 AI 回饋方法。入口是
[來源知識目錄](../src/knowledge/engineering-common/README.md)。
這些變更尚未回填 RC4 ZIP，也尚未自我安裝；本節不更動上述 RC4 的
skill consumption 數量或既有版本的能力宣告。
