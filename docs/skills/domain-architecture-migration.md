# 從 ddd-ca-hex-architect 遷移

[回 Skill 目錄](README.md) · [安裝流程](../installation.md)

本版 catalog 將原 combined skill 直接退役，提供
[domain-model-designer](domain-model-designer.md) 與
[software-architect](software-architect.md)。沒有 alias、過渡 router 或新 catalog 的舊 entry。
本頁是遷移說明，不是可呼叫的 compatibility skill。

## 先選要保留的工作

| 你需要的成果 | 新 canonical ID／operation |
| --- | --- |
| 語言／規則歧義、領域探索 | domain-model-designer / explore |
| Context、aggregate、狀態、不變條件與一致性責任的設計／審查 | domain-model-designer / design、review |
| 軟體元件、依賴、ports/adapters、交易／失敗機制的設計／審查 | software-architect / design、review |
| 原先兩類工作都需要 | 明確選取兩個新 ID，按問題分工，不強制串接 |

四個原本含舊 ID 的 presets（collaboration、complete、engineering、source-repository）
改選兩個新 ID，以保留原組合能力；knowledge 仍為空。自訂 selection 可只選其中一個。
新 catalog 的 selection resolver 對舊 ID 回報 `selection-unavailable`。ID 字串本身
仍符合通用 schema；不使用歷史 ID blacklist，也不重寫舊 catalog／lock。

## 規劃升級

1. 核對目前安裝 lock、desired selection、選用的 catalog／版本與實際 runtime entries。
   下載新套件不等於完成安裝。既有未升級專案仍可能有舊 skill snapshot。
2. 在明確選定的 desired selection 移除舊 ID，加入需要的新 ID；保留其餘 components
   與專案設定。先 inspect／plan，不手改 managed lock/core/wrappers。
3. 檢查 knowledge bindings：兩新 skills 沿用 architecture capability。既有 design/review
   bindings 保留 ID、authority、selectors 與 coverage 意圖，逐項核對新 allowlist。
   Domain 的 explore、Story 的 plan 是不同 operations，不能由名稱替換推論已被採納。
4. 本版的 engineering-common 是 0.4.0，dotnet-backend 是 0.1.6，後者精確依賴前者；
   metadata pins 必須和所用 catalog 一致。Story plan 的 discovery 與 formulation
   不可混成含 plan 的同一 binding，因 formulation 不宣告 plan。
5. 依既有 derive/inspect/plan 與現有授權 apply，再讀回 managed inventory、選擇與 entries。
   Plan 中應可看見舊 managed package 移除及新項目加入。發現 drift、unowned 同名路徑
   或 custom collision，保留現況並解決具體衝突，不因 skill 退役默刪客製內容。

可選的 .NET 資源按責任分配：Domain 使用 aggregate／DbC；Software 使用
building blocks、DbC、transactional messaging、usecase、project structure。兩者都可讀
catalog，但規則適用仍由目標 adopted authority 決定。完整資源 ID 見各新 skill metadata。

## 驗證與限制

安裝器在更新完成時回收符合 managed 路徑規則的空目錄，包括舊 skill 的
`.ai/core/skills/ddd-ca-hex-architect/`、`.agents/skills/ddd-ca-hex-architect/`
及 `.claude/skills/ddd-ca-hex-architect/` 空殼。回收採非遞迴刪除，保留 managed roots、
未知檔案與不符合 managed 路徑規則的名稱，也不追蹤連結或跨磁碟掛載。
有殘留時應核對 lock、managed inventory、實際 entry 與操作回報；
不要自行遞迴刪除舊路徑，因其中可能包含未受管理的客製檔案。

升級後舊 entry 不再由新 catalog 提供；直接呼叫不存在的 runtime 名稱如何回應，
由該 runtime 決定，本頁不承諾特定診斷訊息。尚未升級的舊 entry 仍執行其安裝版本，
並不因此成為新 source 的 alias。

分別記錄 plan/apply/read-back、runtime discovery、實際操作與接受結果。檔案存在、
metadata 有效或作者自檢不能代替行為驗收。套件發布不會自動升級任何專案。
客製 skill 的三方比較、資源保存與明確路由見[專案 skill 管理](../skill-management.md)；
比較結果不代表已完成語意整合或 runtime 啟用。本機 workflow 整併不屬於此遷移。
