# AI Collaboration Framework 使用手冊

本手冊以 `v0.19.0-rc.4` 的套件格式及來源版本
`dd1453e8cf23bf62a5b28c70ed08f475856dda41` 為基準。RC4 已發佈；
`0.19.0` 正式版尚未發佈。來源後續的 skill 路由文字修正不會自動回填到
RC4 ZIP，請以實際下載的版本、catalog 與安裝 lock 判定可用能力。

手冊位於來源庫的 `docs/`，供使用者閱讀，不屬於下游發佈資源。
RC4 ZIP 沒有內附這組文件。安裝命令只需要已下載的 archive，
不需要 clone 本來源庫。手冊中的相對 `src/` 連結是來源參考，可能隨分支更新；
RC4 安裝契約請使用安裝說明中的固定版本連結，實際 skill 指令則以已安裝副本為準。

## 閱讀順序

1. [安裝說明](installation.md)：下載、選取 skills／知識／adapter、預檢、
   安裝、驗證，以及日後調整與復原。
2. [知識套件與缺少知識的影響](knowledge-packages.md)：哪些能力會減少、
   如何分開安裝與採用規則，以及不安裝知識時可做什麼。
3. [各 skill 使用說明](skills/README.md)：18 個發行 skill 的操作、輸入、
   產出、範例與限制。
4. [工具型 skills 共通設定](tool-skills.md)：五個 record／CBF 工具的設定、
   `explain` request、生命週期與 provider 邊界。

這些是使用者文件。可重用 skill 的權威指令仍是所安裝套件的 `SKILL.md`、
operation reference 與 `skill-package.yaml`。本來源庫的 `.dev/` 政策、
GitHub Issue 流程及執行紀錄，不會因為使用此 framework 就變成使用者專案的規則。

## 先決定要安裝什麼

| 使用情境 | 選擇方式 |
| --- | --- |
| 只要一項能力 | 明確列出該 skill；必要相依項由 selection contract 檢查 |
| 一般需求、設計、實作、審查 | 選需要的 skills；可不安裝工程或 .NET 知識 |
| 要共通工程方法、命名／測試／審查等參考 | 另外選 `engineering-common` |
| 要配套 .NET 後端架構、實作、範例與規範 | 選 `dotnet-backend`，並滿足它對 `engineering-common` 的必要相依 |
| 新專案需要協作文件與結構 | 另選 `ai-context-init` 或 `project-initialization` preset，再執行初始化操作 |
| 只使用 Codex 或 Claude | 只選對應 adapter；兩者也可同時選 |

Preset 是選擇的起點，名稱不保證包含所有你需要的項目。
例如 `complete` 與 `project-initialization` 分開；新增初始化 skill
沒有偷偷更動既有 preset。完整清單與可直接修改的 selection 範例見安裝說明。

## 使用前的共同觀念

- **安裝與操作分開。** 安裝讓 runtime 找得到 skill；不會自動建立根目錄
  `AGENTS.md`、需求文件、ADR 或 workflow，也不表示已執行測試。
- **設定與授權分開。** 選定檔案路徑、寫入根目錄或 provider，不等於授權
  寫入、發 PR、合併或發布。已給出的明確授權應沿用，不必逐步重問。
- **知識與規則採用分開。** 知識檔存在可以提供參考；要宣稱套用規範，還需要
  專案選定的 binding、適用條件與 authority。未安裝的專業覆蓋應明確標示。
- **查自己的安裝。** 此來源庫自己只安裝 17 個 skills、沒有知識套件，
  不代表發行 catalog 只有 17 個，也不代表你的專案應採相同選擇。
- **保留專案資料。** `.ai/core/` 與 runtime entries 由 installer 管理；
  `.ai/custom/` 與專案工作紀錄由專案擁有。更新前先閱讀 plan 中的增刪內容。

## 已知版本邊界

`software-development-orchestrator` 已恢復開發階段協調；舊的 portable
workflow-v2 紀錄操作已退場，workflow 儲存方式由專案決定。
`standards-promotion` 是未發佈的實驗，不在本手冊的 18 個可安裝 skills 中。
舊版 published-format 升級／復原不能套用新的安裝命令便宣稱相容。
實際 runtime discovery、跨電腦復原與穩定版升級，仍須各自取得對應驗收。

職責沿革可參考[來源庫的變遷說明](../.dev/guides/ai-collaboration-guides/SKILL-RESPONSIBILITY-CHANGES.md)；
它提供歷史對照，不取代下載版本的實際 metadata。
