# Skill 使用說明目錄

[回手冊首頁](../README.md) · [安裝說明](../installation.md) ·
[知識選配](../knowledge-packages.md) · [工具型 skills 設定](../tool-skills.md)

本來源 catalog 有 18 個 skills；實際可用版本依下載的 catalog 與安裝 lock。
先依要交付的成果選擇；不必為了使用其中
一個就跑完整開發流程。明確指定的 skill 若在其契約範圍內，應沿用你的選擇。

| Skill | 版本 | 何時使用 | 操作形式 |
| --- | --- | --- | --- |
| [adr-author](adr-author.md) | 0.1.0 | 記錄架構替代方案與 owner 決策 | Python record 工具 |
| [ai-context-auditor](ai-context-auditor.md) | 0.1.0 | 只讀稽核或比較 AI context | 指令 |
| [ai-context-governance](ai-context-governance.md) | 0.1.0 | 提案或維護已有的專案 context | 指令 |
| [ai-context-init](ai-context-init.md) | 0.2.0 | 建立最小協作起點，或更新事實／指令／導覽 | 指令 |
| [bdd-gwt-test-designer](bdd-gwt-test-designer.md) | 0.2.0 | 設計或審查 GWT 情境 | 指令；可選知識 |
| [code-reviewer](code-reviewer.md) | 0.2.0 | 審查程式或實作指引中的缺陷 | 指令；可選知識 |
| [ddd-ca-hex-architect](ddd-ca-hex-architect.md) | 0.2.0 | 設計或審查領域、架構與依賴邊界 | 指令；可選知識 |
| [diagnostic-analyst](diagnostic-analyst.md) | 0.1.0 | 解釋已觀察到的故障或效能症狀 | 指令 |
| [lesson-author](lesson-author.md) | 0.2.0 | 保存有證據的經驗與接受決定 | Python record 工具 |
| [local-backlog](local-backlog.md) | 0.1.0 | 管理專案選定的本機 work items | Python record 工具 |
| [local-change-implementer](local-change-implementer.md) | 0.2.0 | 一個局部技術操作與直接影響範圍 | 指令；可選知識 |
| [pr-author](pr-author.md) | 0.1.0 | 準備 PR record，或執行另行授權的 GitHub draft 操作 | Python record／provider 工具 |
| [problem-frame-author](problem-frame-author.md) | 0.1.0 | 撰寫／審查 problem frame；選定 CBF 時保存版本化 snapshot | 指令＋選用 Python CBF 工具 |
| [requirement-author](requirement-author.md) | 0.1.0 | 撰寫或正規化需求與可觀察驗收條件 | 指令 |
| [slice-implementer](slice-implementer.md) | 0.2.0 | 實作一個 command／query／reactor／generic slice | 指令；可選知識 |
| [software-development-orchestrator](software-development-orchestrator.md) | 0.2.0 | 協調跨階段開發，或從 checkpoint 繼續 | 指令 |
| [spec-author](spec-author.md) | 0.1.0 | 撰寫 production／entity／adapter／formal-test 規格 | 指令 |
| [spec-compliance-validator](spec-compliance-validator.md) | 0.1.0 | 規劃證據、審查規格語意、評估真實執行證據 | 指令 |

## 常見選擇

| 你要的成果 | 優先選擇 |
| --- | --- |
| 「這個專案還沒有協作入口文件」 | `ai-context-init initialize` |
| 「既有 AGENTS 的規則、責任或 precedence 要調整」 | `ai-context-governance propose/apply` |
| 「只確認 context 哪裡有問題」 | `ai-context-auditor audit` |
| 「把需求變成正式測試規格」 | `spec-author` 的 formal-test 類型 |
| 「設計／審查 GWT 情境矩陣」 | `bdd-gwt-test-designer` |
| 「實作情境的測試程式」 | 已授權的 `slice-implementer` 或符合局部範圍的實作 route |
| 「審查架構文件」 | `ddd-ca-hex-architect review` |
| 「審查固定程式 diff」 | `code-reviewer review` |
| 「追查為什麼特定情況會失敗」 | `diagnostic-analyst diagnose` |
| 「改一個方法及其直接呼叫點」 | `local-change-implementer` |
| 「完成一個跨 domain／application／test 的行為」 | `slice-implementer` |
| 「沿用已接受需求，協調設計、實作、驗證與交接」 | `software-development-orchestrator` |

不用專門 skill 也可以依專案命令執行測試；此 catalog 沒有 `test-execution`
skill。`spec-compliance-validator` 的 evidence assessment 不能用來代替
實際測試執行，orchestrator 也不會自動讓各階段變成已完成。

## 一個足夠具體的請求

```text
使用 <skill-id> 的 <operation>。
目標與預期成果：...
來源／版本／已接受的決策：...
可讀與可寫範圍：...
要套用的專案規則或已選知識：...
輸出位置、格式與驗收方式：...
已有授權與需要保留的限制：...
```

不必填與這次作業無關的欄位。只讀審查不需要先授權修正；已授權的修改也
不必為每個檔案重問。缺少會影響正確性或 owner 決策的輸入時，先處理該缺口。

`standards-promotion` 未列入發行 catalog，沒有可從 RC4 安裝的正式使用路由。
ADR／Lesson 被接受也不表示規則已經採用；專案規範調整需走其選定的治理方式。
