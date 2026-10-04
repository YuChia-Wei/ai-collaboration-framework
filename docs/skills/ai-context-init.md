# ai-context-init 使用說明

[回 Skill 目錄](README.md) · [安裝](../installation.md) · [知識選配](../knowledge-packages.md)

本頁對應 `ai-context-init@0.2.0`；實際操作仍以已安裝 metadata 為準。
RC4 的舊資源不會因來源手冊更新就取得這次入門擴充。

## 目的與完成點

這個 skill 協助團隊建立最小可用的 AI 協作起點：知道專案在做什麼、
可以修改什麼、依據在哪裡、如何驗證，以及如何開始下一個有限任務。

入口、必要背景與規則、實際指令狀態及下一步指引可理解後，初始化就結束。
未知事實可以明確保留；不會接著執行第一個開發任務或持續管理專案。

| 操作 | 用途 | 界線 |
| --- | --- | --- |
| `initialize` | 辨識既有內容，補齊缺少的協作入口、基線、背景引用及起步指引 | 不制定產品策略、不設計完整團隊制度、不覆寫既有規則 |
| `refresh` | 更新指定文件中的事實、指令、連結與導覽 | 不因新版範本而重設政策、產品範圍、文件責任或 precedence |

這是指令型 skill，沒有同名 CLI，也不是 framework 安裝器。Agent 使用
已授權的一般檔案工具完成文件工作；不需要工程知識包或其他 skill。

## 安裝與開始

可只選 `ai-context-init`，或選 `project-initialization@0.1.0` preset。
這個 preset 選取 init 與 Codex／Claude adapters，knowledge 為空。
Preset 版本與其中 skill 的版本是不同欄位，請查實際 catalog。
使用 prefixed 命名時，runtime 名稱為 `aicf-ai-context-init`。

安裝只放入方法與範本，不自動建立根目錄文件。先完成
[安裝與 inspect](../installation.md)，再向 agent 指定初始化。

```text
請用已安裝的 ai-context-init initialize，為 <專案絕對路徑> 建立最小協作起點。
可修改根目錄 AGENTS.md、必要的 runtime 入口與專案文件；不得改應用程式碼、
CI、Git 歷史、安裝選擇或 managed framework 檔案。
先沿用現有產品說明、CONTRIBUTING、架構與規則，不建立重複權威。
在缺少時補上協作基線與第一次任務指南；產品目的只能取自我提供的資料或
已有文件，未知處明確標示。完成後回報檔案、引入的起始條款與實際檢查。
這次不執行第一次開發任務，也不提交或推送 Git。
```

已有明確初始化授權時，不需要每份文件再確認一次；真正無法由證據解決的
產品或權威決策才交回適合的 owner。只要求 root entry 時，也不會強迫建立
整組 `.dev` 文件。

## 提供的入門資源

| 資源 | 如何使用 |
| --- | --- |
| 產品背景範本 | 整理目的、使用者、範圍／非目標、系統邊界、限制與目前階段；已有等效 README／PRD 就引用它 |
| 協作基線範本 | 提供可改寫採用的工作意圖、授權、完成證據、適度審查／紀錄、委派／成本與反思條款 |
| 第一次任務指南 | 依真實檔案改寫「只讀理解功能」及「完成已指定的小修改」兩個例子；不自動啟動任務 |
| 根目錄與導覽範本 | 保留必要的工作邊界，指出何時讀取哪些實際文件；連結存在不代表 runtime 已載入 |
| 可選技術盤點 | `project-config.template.yaml` 記錄技術事實、命令與文件位置；不重複整份產品背景，也不是 framework 設定契約 |

沒有既有慣例時，可以選擇以下布局；不會為了符合範例建立空資料夾：

```text
AGENTS.md
.dev/
  README.MD
  project-context.md
  project-config.yaml                 # 有需要才建立
  standards/ai-collaboration.md
  guides/first-task.md
```

已有 `CONTRIBUTING.md`、`docs/product-overview.md` 或其他布局時，沿用原位置。
沒有 .NET 或工程知識選擇，不會加入其特定規範。沒有安裝 specialist 時，
指南不能假裝它存在，也不會為了範例自動安裝。

## 責任分工與維護

- init 可以寫下已有證據的產品背景；需要制定產品方向、範圍或驗收時，
  交給產品 owner 與選定的需求／規格工作。
- init 可以補上缺少的協作起始條款；改變既有制度或解決政策衝突時，
  交給專案維護 owner，`ai-context-governance` 是已安裝時可選的路由。
- init 提供第一次任務指引；實作、審查與開發階段協調由後續另行選定的
  任務負責。這些責任分工不會增加必裝 skill 或強制工作流程。
- 重複 initialize 會檢查缺口；不會重新套版。refresh 保留客製規則、
  註解、語言與既有決策。新版模板值得採納的差異可另提維護建議。
- 初始化產出的文件由目標專案擁有。Framework 更新或移除 init 不會自動
  覆寫或刪除它們；不要把它們加入 managed package inventory。

```text
請用 ai-context-init refresh，只更新 AGENTS.md 的專案事實區及
<既有導覽文件> 的指令與連結。以目前 repository 的檔案為證據，
保留產品範圍、協作規則、客製區段與歷史。不要套用新版範本重寫文件。
```

文件中的授權與成本條款是行為指引，不是 sandbox 或計費限制器。
初始化完成、套件安裝成功、runtime 載入及 agent 實際遵守規則，仍是不同證據。

## 權威參考

- [Skill 入口](../../src/skills/ai-context-init/SKILL.md)
- [版本、操作與資源宣告](../../src/skills/ai-context-init/skill-package.yaml)
- [初始化與 refresh 方法](../../src/skills/ai-context-init/references/initialize.md)
- [專案結構與文件分工](../../src/skills/ai-context-init/references/project-structure.md)
- [產品背景範本](../../src/skills/ai-context-init/templates/project-context.md)
- [協作基線範本](../../src/skills/ai-context-init/templates/ai-collaboration.md)
- [第一次任務指南範本](../../src/skills/ai-context-init/templates/first-task.md)
- [AGENTS 範本](../../src/skills/ai-context-init/templates/public-root/AGENTS.md)
- [技術盤點範本](../../src/skills/ai-context-init/templates/project-config.template.yaml)

來源連結供核對；實際執行應讀取所安裝套件中的對應資源。
