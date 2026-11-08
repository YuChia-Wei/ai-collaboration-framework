# .NET 測試策略、工具邊界與格式化 hook 評估

固定分析對象為 `41e4ebb8e716355ac86c4b39a8846e7b6711c1aa`。本報告保留 #594 分析階段的推理、原始案例清單與既有執行證據，並說明後續選定方向。它不宣稱後續實作、Run All、交付或安裝已通過。現行執行進度由 SQLite workflow 持有；現行測試說明應查測試專案 README 與案例旁的 XML summary。

## 範圍與方法

涵蓋 Refactor、原 FormatTool、Snippet、原生範本及 domain-contracts 範例。以 Git 固定來源、既有 TRX／Rider 記錄、Microsoft 與產品官方資料為依據。唯讀盤點由 task-selected Sol/medium workers 分擔，耗時整理使用 Luna/medium；主代理綜合分析。這是設計自我檢查，並非獨立驗收；指定模型不等於後端計費或執行身分遙測。

完整證據：

- [依元件用途的改善計畫與官方例子](evidence/component-test-plan.zh-TW.md)
- [逐方法來源、oracle、實際邊界與處置理由](evidence/analysis-notes.md)
- [供閱讀的歷史測試清單](evidence/test-inventory.zh-TW.md)

三份文件保留分析當時的措辭與修訂，不作為要繼續維護的現行清單。其中固定保留七個一般／四個成品專案的早期方案已被後續元件用途分析取代；FormatTool 的舊 JSON、consent 與 snapshot 合約也不再是原生格式化腳本的需求。

## 結論與對應處置

| ID | 固定來源觀察 | 採用的方向與限制 |
| --- | --- | --- |
| T01 | 五個 Compile rules 從直接 SDK 評估加入 restore／完整 preview，已有較小的真實評估入口 | 回到必要的 SDK 評估；須核對實際 MSBuild／SDK 身分，保留完整 preview 見證。不能只用手寫 XML 替代 evaluated imports／glob。 |
| T02 | 一個 Template Fact 混合七類操作，且成品路徑重跑長旅程 | 按 items、兩種 API、contract templates 的獨立主張呈現；保留生成後 build／代表性 HTTP，交付包只做必要安裝／生成證據。 |
| T03 | 範本來源分散，普通可建置專案未全納入日常 solution | 七個範本統一入口；可獨立建置的專案納入主 solution。CT-005 的選定外部 DLL 與 .NET 8 執行前提保持明示。 |
| T04 | 原 FormatTool 包裝 SDK 並維護大量選檔、JSON、consent、bytes 觀察與成品測試 | 使用原生 dotnet format 與薄腳本，接受原生輸出／結束碼；移除被替代產品責任及其專屬測試，不重建另一套框架。 |
| T05 | 部分唯讀、Stream 和 SDK 查詢案例走過與主張無關的完整路徑 | Stream 移 unit；真實 ReadOnly 留 preflight；configuration 用 inspect。保留實際 OS／SDK 邊界及 no-write oracle。 |
| T06 | 成品案例含來源語意，來源測試又不能證明封裝完整 | 先對照來源 coverage，必要時移回真正缺漏的行為；交付流程保留少量解壓／AOT／nupkg smoke。無成品不是日常 Run All 的 skip 原因。 |
| T07 | 測試用途需另行整理大清單才容易閱讀 | 專案 README 寫責任、依賴、邊界、命令；案例 summary 寫可觀察承諾。與測試一起維護，不新增生成清單、manifest 或檢查平台。 |

一般案例以 10 秒內為目標；確有必要的整合案例最多 30 秒。不能透過漏跑、缺旗標 skip、加 timeout、削弱結果或切斷有意義的連續主張達標。SDK／環境具備時 Run All 應自動執行。

## 已有耗時證據的正確範圍

保存的 Windows 正常結果為 175 passed、1 POSIX-only skip。47 個 SDK 案例占案例耗時加總的 96.1%；五個相同 Compile 輸入合計為 6.025 → 38.339 → 38.593 秒。逐案例分類與超時清單見上述證據。

這些執行和跨專案／成品工作有重疊，並非乾淨效能基準；第一版已執行 Refactor SDK，不能把變慢全部歸因於新增 SDK 執行。Rider 有兩組重疊序列，原因未明，且使用者取消後沒有完整完成耗時。CLI 和 Rider 不能互相代替實際驗收證據。後續需在單一 runner、無其他重工作下，分開記錄 build、discovery、case durations 和總耗時。

## AI 回合完成後自動格式化：可行，但本次只評估

截至 2026-11-08 的官方文件，Codex 與 Claude Code 均提供 `Stop` command hook。它代表回合停止，不代表整段對話結束。Codex 的 Stop stdout 應是合法 JSON，阻擋決定或 exit 2 會要求模型繼續。因此不能直接把 formatter 的一般 stdout／exit code 當作 Stop 協定。這仍須單獨的短 adapter；正常完成不回傳繼續指令。[Codex Hooks](https://learn.chatgpt.com/docs/hooks)

Claude 的 PostToolUse Edit／Write 不能涵蓋所有 shell 寫檔；Stop 可在回合末集中處理。阻擋 Stop 會繼續代理工作，`stop_hook_active` 可防止反覆繼續。command hook 與呼叫模型的 prompt／agent hook 是不同選擇。[Claude Code hooks guide](https://code.claude.com/docs/en/hooks-guide)

設計建議為 repository opt-in、同步 command hook、明確 solution、僅 whitespace，先取得這個回合的檔案集合。`git status` 包含回合前的使用者改動，不能直接當 AI 修改清單；新增、刪除、生成檔與其他 writer 也要有明確處理。找不到可信範圍就只報告，不自動擴成全 solution。以 worktree 為範圍防止重疊 formatter，限定執行時間，捕捉 formatter 輸出並回報錯誤，保留重跑冪等性。這些是尚未實作的建議，不是已提供的安全保證。

格式化若發生在最後一次測試之後，最終檔案與測試輸入會不同；應優先在驗證前格式化，末端 hook 作補充，並清楚回報後續改動。hook 可省去模型為啟動 formatter 所需的額外選擇／工具呼叫，官方文件未證明整個 host lifecycle 為零 token 或零費用。本機版本、設定、信任及 hook 實際觸發未驗證；本次沒有啟用 hook。

## 官方慣例與非結論

原生 Fact／Theory、可讀的 AAA、獨立 expected values 及最小足夠邊界是合適做法；Microsoft 並未要求 BDDfy。既有具名 GWT 可保留，表達方式不是已證實的耗時瓶頸。[Microsoft 單元測試建議](https://learn.microsoft.com/en-us/dotnet/core/testing/unit-testing-best-practices)

原生 `dotnet format` 可選 whitespace／style／analyzers、指定 include、驗證變更或實際套用，規則來自 EditorConfig。薄腳本應保留這些原生責任；它不具備舊工具的 no-write／回復／consent 保證。[dotnet format](https://learn.microsoft.com/en-us/dotnet/core/tools/dotnet-format)

本報告沒有驗證下游業務、CT-005 外部原始規格、其他 OS、hosted CI、下載後 Gatekeeper、發佈或安裝。規劃結果不等於產品執行結果。
