# 維護產品文件

`docs` 說明 framework 成品的安裝、選擇、使用方式、輸出與限制。
`src` 擁有產品會提供的 skill、知識、role、template、schema 及工具；
`.dev` 保留此來源專案的規範、紀錄與協作流程。

本專案同時開發及使用 framework，來源與安裝副本重複出現是正常情況。
先修改 `src` 與套件宣告，成品準備好後才依另行選定的安裝／升級流程
更新 `.ai/core` 和 runtime entries。直接修改安裝副本會產生漂移。

## 專案格式設定

根目錄 `.editorconfig` 由各專案團隊維護，包含縮排、換行、行長、命名與
程式碼風格等選擇。本來源庫的 `.editorconfig` 只供本專案開發使用，
不作為 framework 預設配送或升級覆寫的檔案；使用端沿用自己的設定。

若某項能力需要特定設定，framework 可在 `src` 提供最小參考片段與用途說明，
由使用端審閱後自行採用。例如 .NET 知識包的
[Analyzer severity 片段](../src/knowledge/dotnet-backend/tooling/on-demand-mechanical-validation/recipes/analyzer-severity.editorconfig.snippet)
只提供診斷嚴重度參考，不代表已採用或啟用，也不取代團隊的完整 `.editorconfig`。
使用端採用後的設定由使用端維護，安裝知識包本身不會寫入其根目錄設定。

## 撰寫使用說明

從使用者的任務開始，說明用途、適用情境、所需輸入、操作、輸出與限制。
提供可直接改寫的 prompt 範例；依情境選擇數量，不強制每份文件套用相同模板。
指南引用產品來源或固定發行版本，避免完整複製 agent 的執行契約。
人類指南是說明；實際 skill 指令與 metadata 仍由產品來源及安裝版本擁有。

保留文件的版本基準。尚未發布的來源能力應標明來源分支範圍，不得當成
已下載 ZIP 的內容。安裝、規則採用、執行、測試、合併及發布各有自己的證據。

## 整理與引用

可重用方法應放入 `src` 的所屬 component，宣告成員及跨套件相依，
再由文件提供導航。產品資源可以要求 caller-selected 的專案事實，
但不應要求 framework 作者專案的特定 `.dev` 政策或私有紀錄。
Git revision 與舊路徑可作為歷史來源證據，不是安裝時必須存在的資源。

移除過時且無獨立經驗價值的操作說明；保留有用的決策理由及相容性責任。
此輪整理保留 `.dev/design`、`.dev/assessments`、`.dev/requirement`、
`.dev/adr`、`.dev/workflows` 的既有內容。它們的舊引用代表歷史狀態，
不應批次改寫成目前操作說明。

修改後檢查 current 文件引用、套件 closure 與受影響的 source checks。
內容檢查不能代替 runtime、native、hosted 或發布驗收。
