# AI Collaboration Framework

這是可重用 AI collaboration framework 的來源庫。本庫維護產品套件，也安裝選定版本供 Codex 與 Claude 使用。

## 從這裡開始

| 目的 | 路徑 |
| --- | --- |
| Agent 協作規則與目前 routes | [`AGENTS.md`](AGENTS.md) |
| 人類導覽與操作說明 | [`.dev/guides/`](.dev/guides/README.MD) |
| 可編輯的 reusable framework source | [`src/`](src/) |
| 本庫已安裝的 generated package | [`.ai/core/`](.ai/core/) |
| Codex skill entries | [`.agents/skills/README.md`](.agents/skills/README.md) |
| Claude skill entries | [`.claude/skills/README.md`](.claude/skills/README.md) |
| Source policy、工作紀錄與發布治理 | [`.dev/INDEX.md`](.dev/INDEX.md) |

## 本庫的安裝選擇

RC3 source selection 包含 17 個 portable skills、Codex 與 Claude adapters，不安裝 engineering knowledge packages。Authoring package IDs 為 `adr-author`、`lesson-author` 與 `pr-author`；portable workflow orchestration 已退休。Generated installation identity 仍由其 lock 記錄，與 source selection 分開更新。`.ai/custom/installation.json` 保存 project-owned selection；managed installer 產生 `.ai/framework.lock`、`.ai/core/` 與兩種 runtime entries。Generated content 不可直接編輯；要改產品請編輯 `src/`，再依 source workflow 更新安裝。

Installation selection 與 skill operation settings 分開管理。`.ai/custom/framework.json` 為 Lesson、ADR、PR、CBF 與 standards-promotion skills 設定了五個 project-owned filesystem roots 及精確 write_roots，採用套件模板與 tracked-intent；目前沒有建立記錄或 evidence，也沒有配置 ADR decision、promotion target/source adapters 或 local-backlog provider。這是 path selection，不是執行權限、store availability 或 runtime capability 證明。

## Source 與相容性邊界

- `src/skills/` 與 `src/knowledge/` 是 reusable product 的可編輯來源；本庫不選取 engineering knowledge package。
- `.ai/core/`、`.ai/framework.lock` 與 runtime entries 是安裝產物。
- `.ai/assets/` 只保留仍有 active source tooling caller 的 compatibility 與工具輸入，不是日常 skill registry，也不是一般執行的第二條路由。
- `.dev/standards/` 擁有 source policy、Issue authority、U001 與 P7 deferrals；`releases/` 擁有發布記錄與版本支援邊界。
- 舊 published-format 初始化、upgrade、transaction recovery 及歷史／exception release closeout 是 source-owned compatibility duties，不是 portable installed skills。

遵循 [`AGENTS.md`](AGENTS.md) 與其指出的 `.dev/standards/`。RC2 安裝不代表 runtime discovery、behavioral acceptance、upgrade/recovery trials 或下游 admission 已驗收；這些項目由 owner 指定的 S6/P7 work 負責。穩定版發布與 GitHub Release 是另外的 owner 決策。
