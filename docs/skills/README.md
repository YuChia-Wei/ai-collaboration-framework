# Skill 使用說明目錄

[回手冊首頁](../README.md) · [安裝說明](../installation.md) ·
[知識選配](../knowledge-packages.md) · [工具型 skills 設定](../tool-skills.md) ·
[自建／客製 skill 管理](../skill-management.md)

本來源 catalog 有 21 個 skills；實際可用版本依下載的 catalog 與安裝 lock。
先依要交付的成果選擇；不必為了使用其中
一個就跑完整開發流程。明確指定的 skill 若在其契約範圍內，應沿用你的選擇。

| Skill | 版本 | 主要責任／何時使用 | 職責邊界 | 操作形式 |
| --- | --- | --- | --- | --- |
| [adr-author](adr-author.md) | 0.1.0 | 記錄架構替代方案與 owner 決策 | 記錄決策，不取代架構設計或證明已實作 | Python record 工具 |
| [ai-context-auditor](ai-context-auditor.md) | 0.1.0 | 只讀稽核或比較 AI context | 回傳 findings；不修正受評對象 | 指令 |
| [ai-context-governance](ai-context-governance.md) | 0.1.2 | 提案或維護已有的專案 context | 維護 project-owned 規則；不手改 managed core | 指令 |
| [ai-context-init](ai-context-init.md) | 0.2.3 | 建立最小協作起點，或更新事實／指令／導覽 | 不安裝 framework、不決定產品策略或執行第一次開發工作 | 指令 |
| [test-designer](test-designer.md) | 0.4.3 | 設計或審查一般測試與正式測試規格 | 擁有案例、層級、資料與預期結果來源；不實作或執行測試 | 指令；可選知識 |
| [code-reviewer](code-reviewer.md) | 0.2.6 | 審查程式或實作指引中的缺陷 | 維持唯讀；故障因果調查、架構／情境文件審查各有 owner | 指令；可選知識 |
| [domain-model-designer](domain-model-designer.md) | 0.1.1 | 探索、設計或審查領域語言與模型 | 擁有不變條件與業務一致性需求；不選軟體機制 | 指令；可選知識 |
| [software-architect](software-architect.md) | 0.1.1 | 設計或審查軟體結構、依賴與整合機制 | 遵循已接受模型；不自行改業務政策或執行部署 | 指令；可選知識 |
| [diagnostic-analyst](diagnostic-analyst.md) | 0.1.0 | 解釋已觀察到的故障或效能症狀 | 診斷與修復建議不額外授權修復 | 指令 |
| [lesson-author](lesson-author.md) | 0.2.0 | 保存有證據的經驗與接受決定 | 經驗接受不自動變成專案規則 | Python record 工具 |
| [local-backlog](local-backlog.md) | 0.1.0 | 管理專案選定的本機 work items | 管理記錄與狀態，不同步線上 tracker 或決定開發流程 | Python record 工具 |
| [local-change-implementer](local-change-implementer.md) | 0.2.7 | 一個局部技術操作與直接影響範圍 | 保持接受的公開契約；協調性行為變更由 slice 承接 | 指令；可選知識 |
| [pr-author](pr-author.md) | 0.1.0 | 準備 PR record，或執行另行授權的 GitHub draft 操作 | 不取代 defect review，也不包含 push、merge 或 Issue／Project 更新 | Python record／provider 工具 |
| [problem-frame-author](problem-frame-author.md) | 0.1.0 | 撰寫／審查 problem frame；選定 CBF 時保存版本化 snapshot | 特定問題框架，不是所有需求的必經格式；結構有效不等於行為接受 | 指令＋選用 Python CBF 工具 |
| [requirement-author](requirement-author.md) | 0.2.2 | 探索、撰寫或正規化需求與可觀察驗收條件 | 釐清需要與規則；不把推測模型／機制當作接受的需求 | 指令；可選知識 |
| [slice-implementer](slice-implementer.md) | 0.2.7 | 實作一個 command／query／reactor／generic slice | 擁有切片內部修改與直接驗證，不需逐方法交接 | 指令；可選知識 |
| [software-development-orchestrator](software-development-orchestrator.md) | 0.4.1 | 協調跨階段開發，或從 checkpoint 繼續 | 選必要工作並重用已接受輸入；記錄儲存與專業判斷各有 owner | 指令 |
| [spec-author](spec-author.md) | 0.3.0 | 依需求與設計撰寫 production／entity／adapter 規格 | 表達已接受契約；不填補未定設計，正式測試規格由 test-designer 擁有 | 指令；可選知識 |
| [spec-compliance-validator](spec-compliance-validator.md) | 0.1.0 | 規劃證據、審查規格語意、評估真實執行證據 | 限指定判準與範圍，不代替實際測試執行或全系統認證 | 指令 |
| [user-story-author](user-story-author.md) | 0.2.0 | 獨立 Story 切分、撰寫、正規化與整份／指定 AC 審查 | 擁有 Story／AC；一般需求與測試設計保留原 owner | 指令；可選 |
| [workflow-records](workflow-records.md) | 0.1.0 | 查找、checkpoint、接續 Git 或本機 SQLite workflow 紀錄 | 不決定開發階段；Git 目前只追加 checkpoint，兩 provider 均未提供 task editing | Python record 工具；可選 |

本表是人類選讀入口；操作細節與可用能力以各頁連結的來源契約及實際安裝版本為準。
新增、拆分、改名、退役或責任改變時，與產品變更一起更新本表及受影響的單項說明，
依[文件維護方式](../maintaining-documentation.md)核對。規劃中的能力不列為已可用項目；
[職責變遷](../../.dev/guides/ai-collaboration-guides/SKILL-RESPONSIBILITY-CHANGES.md)
另保留固定歷史比較。

## 常見選擇

| 你要的成果 | 優先選擇 |
| --- | --- |
| 「這個專案還沒有協作入口文件」 | `ai-context-init initialize` |
| 「既有 AGENTS 的規則、責任或 precedence 要調整」 | `ai-context-governance propose/apply` |
| 「只確認 context 哪裡有問題」 | `ai-context-auditor audit` |
| 「撰寫一份 Story，或只審查 AC-2」 | `user-story-author draft/review`（已安裝時） |
| 「把需求變成正式測試規格」 | `test-designer design` |
| 「設計／審查 GWT 測試情境矩陣」 | `test-designer` |
| 「實作情境的測試程式」 | 已授權的 `slice-implementer` 或符合局部範圍的實作 route |
| 「探索／審查領域模型」 | `domain-model-designer explore/review` |
| 「審查軟體架構文件」 | `software-architect review` |
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

`user-story-author` 為來源 catalog 的獨立選配套件，不自動加入 presets。本來源專案既有 17-skill 安裝尚未升級；四個來源 presets 的領域／軟體架構拆分見[遷移指南](domain-architecture-migration.md)。

原 combined skill 已退役且無 alias，選取新能力與既有 binding 的處理見
[領域／架構遷移說明](domain-architecture-migration.md)。需求、Story、模型與 Spec 都可使用
行為例子；只有測試邊界、資料、oracle 或覆蓋設計才由 test-designer 擁有。
