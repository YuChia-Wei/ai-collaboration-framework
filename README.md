# AI Collaboration Framework

這是可重用 AI collaboration framework 的來源庫。本庫維護產品套件，也安裝選定版本供 Codex 與 Claude 使用。

## 從這裡開始

| 目的 | 路徑 |
| --- | --- |
| 安裝說明、知識選配與各 skill 使用手冊 | [`docs/`](docs/README.md) |
| Agent 協作規則與目前 routes | [`AGENTS.md`](AGENTS.md) |
| Source 操作政策 | [`.dev/standards/`](.dev/standards/INDEX.MD) |
| 可編輯的 reusable framework source | [`src/`](src/) |
| 本庫已安裝的 generated package | [`.ai/core/`](.ai/core/) |
| Codex skill entries | [`.agents/skills/README.md`](.agents/skills/README.md) |
| Claude skill entries | [`.claude/skills/README.md`](.claude/skills/README.md) |
| Source policy、工作紀錄與發布治理 | [`.dev/INDEX.md`](.dev/INDEX.md) |

## 本庫的安裝選擇

目前 distribution catalog 包含 18 個 portable skills 與 Codex、Claude adapters。可選的 [`ai-context-init@0.1.0`](src/skills/ai-context-init/SKILL.md) 透過獨立 `project-initialization` preset，提供依據專案證據建立協作文件與專案結構的指引。既有 presets 與本來源專案的 17-skill installation 維持原狀；安裝套件不會自動建立根目錄文件。`standards-promotion@0.1.1-alpha.1` 保留於 `src/skills/` 供獨立試驗，在用途與行為另行驗證前不隨 framework 成品發布或安裝。`software-development-orchestrator` 已恢復跨階段開發編排；workflow 紀錄格式與存放位置仍由專案選擇。Authoring package IDs 為 `adr-author`、`lesson-author` 與 `pr-author`。本來源專案的安裝選擇不包含 engineering knowledge packages。Generated installation identity 由 lock 記錄，與 source catalog 分開更新。`.ai/custom/installation.json` 保存 project-owned selection；managed installer 產生 `.ai/framework.lock`、`.ai/core/` 與兩種 runtime entries。Generated content 不可直接編輯；要改產品請編輯 `src/`，再依 source workflow 更新安裝。

完整的增減、改名與職責變化見 [Skill 職責變遷](.dev/guides/ai-collaboration-guides/SKILL-RESPONSIBILITY-CHANGES.md)。

Installation selection 與 skill operation settings 分開管理。`.ai/custom/framework.json` 為 Lesson、ADR、PR、CBF 與 standards-promotion skills 設定了五個 project-owned filesystem roots 及精確 write_roots，採用套件模板與 tracked-intent；目前沒有建立記錄或 evidence，也沒有配置 ADR decision、promotion target/source adapters 或 local-backlog provider。standards-promotion namespace 設定保留，但目前不安裝該 skill。這是 path selection，不是執行權限、store availability 或 runtime capability 證明。

RC3 透過固定 engine 的 `tools/reinstall-framework.py` 提供明確選用的 Git-backed 破壞性重裝。呼叫者指定精確清理與保留清單，工具先在外部 preview 預檢新安裝，並在安裝後核對保留內容。清理不是原子操作：已提交的 Git baseline 負責過時檔案還原，固定 API 2 journal 負責新安裝。請參閱[重裝契約](.dev/workflows/2026-09-30-rc3-reinstall/breaking-reinstall.md)與[來源／MQ 實測結果](.dev/workflows/2026-09-30-rc3-reinstall/results.md)。

## Source 與相容性邊界

- `src/skills/` 與 `src/knowledge/` 是 reusable product 的可編輯來源；本庫不選取 engineering knowledge package。
- `.ai/core/`、`.ai/framework.lock` 與 runtime entries 是安裝產物。
- Legacy compatibility roots 已從目前 source layout 移除；歷史 references 不代表目前有可執行 tooling。
- `.dev/standards/` 擁有 source policy、Issue authority、U001 與 P7 deferrals；`releases/` 擁有發布記錄與版本支援邊界。
- 舊 published-format 初始化、upgrade 與 transaction recovery 保留為 source-owned compatibility duties，目前沒有 portable 或可執行的 legacy 路由。歷史／exception release closeout 仍受 source release policy 管理。

遵循 [`AGENTS.md`](AGENTS.md) 與其指出的 `.dev/standards/`。RC3 報告保存實際打包、重裝與讀回的驗證範圍。Runtime discovery、應用程式行為、失敗還原與 hosted admission 保留各自的 S6/P7 驗證狀態。穩定版發布與 GitHub Release 是另外的 owner 決策。
