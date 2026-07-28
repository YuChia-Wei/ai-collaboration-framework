# AI 協作知識庫與 .NET Backend Context Framework

[English](README.en.md)

本專案是一個可攜式的 AI 協作框架來源庫，將軟體開發實務、可重用的 Agent context、skills、sub-agent prompts 與協作流程集中管理。它目前保留並發展 .NET / C# 後端的專門能力，同時把可跨技術棧使用的協作規則抽離為通用內容。

這不是特定產品的應用程式或範例系統。它的目的，是讓團隊能把經過整理與驗證的 AI 協作能力帶入新舊專案，並由目標專案本身的程式碼、設定與文件建立該專案的真實脈絡。

> `README.md` 是此來源庫的人類導覽文件，不是可攜式發佈封包的一部分。封包由明確 allowlist 建立，並刻意排除根目錄 README，避免來源庫介紹被帶入目標專案。

## 專案定位

| 這個專案是 | 這個專案不是 |
| --- | --- |
| 可重複採用的 AI 協作知識庫與框架來源 | 單一產品、微服務或 Web API 的完整實作 |
| 通用軟體開發協作規則與 .NET 後端專門能力的集合 | 把來源庫的 requirement、spec、workflow 或決策直接複製成目標專案事實的工具 |
| 產出可攜式 AI context 發佈封包的受治理來源庫 | 要安裝到目標專案的原始碼快照 |

## 它協助解決的問題

- 讓 AI Agents 在開始工作前取得一致的協作規則、文件位置與驗證方式。
- 將需求、規格、架構、實作、測試、審查與交接的工作方法整理成可路由的 skills 與流程。
- 區分「可跨專案重用的知識」與「只能由目標專案決定的事實」，避免舊專案脈絡污染新專案。
- 保留 .NET 後端開發的實作、設計與審查經驗，讓 DDD、Clean Architecture、CQRS 與 message-driven backend 的討論有一致起點。

## 適用情境

本專案特別適合希望建立一致 AI 協作方式的團隊或個人，例如：

- 要在新專案或既有專案導入可維護的 AI Agent context。
- 需要把 .NET / C# 後端架構與實作慣例提供給多個 Agent 使用。
- 希望讓需求、規格、實作、測試與程式碼審查有清楚的責任邊界與交接方式。
- 想保留可攜式框架規則，同時避免覆寫目標專案既有的業務、架構與營運事實。

## 快速導覽

| 你的目的 | 從哪裡開始 |
| --- | --- |
| 了解此來源庫的架構與範圍 | [`.dev/ARCHITECTURE.md`](.dev/ARCHITECTURE.md) |
| 尋找可用的 AI skills | [`.ai/assets/skills/README.MD`](.ai/assets/skills/README.MD) |
| 了解人類可閱讀的協作指南 | [`.dev/guides/ai-collaboration-guides/INDEX.MD`](.dev/guides/ai-collaboration-guides/INDEX.MD) |
| 讓 Agent 在此來源庫中正確協作 | [`AGENTS.md`](AGENTS.md) |
| 取得或升級可攜式框架版本 | [`.dev/releases/INDEX.MD`](.dev/releases/INDEX.MD) |

## 核心內容

### 通用 AI 協作內容

通用內容可跨語言、框架與產品型態重複使用，涵蓋：

- AI 協作流程、workflow gate 與交接規則。
- Git commit、驗證、需求、規格、ADR 與 review 的工作方式。
- Skill routing、sub-agent 協作與可追溯的執行邊界。
- 系統與軟體架構，以及 DDD、Clean Architecture、CQRS 等概念層指引。

### .NET Backend 專門能力

目前保留的技術棧 profile 聚焦於 .NET / C# 後端，包括：

- Web API、worker 與 consumer 類型的後端專案結構。
- DDD、Clean Architecture、CQRS、Hexagonal Architecture 與 message-driven backend 的實務。
- WolverineFx、Dapper、EF Core、PostgreSQL、RabbitMQ 與 Kafka 等常見後端組合。
- .NET 後端的架構設計、實作切片與 code review 指引。

## 主要目錄

| 路徑 | 用途 |
| --- | --- |
| `.ai/` | Agent-facing 的可重用 AI context、canonical assets、scripts 與 skill specs。 |
| `.ai/assets/shared/` | 跨技術棧的 prompt fragments、規則與可重用材料。 |
| `.ai/assets/tech-stacks/dotnet-backend/` | .NET C# backend Web API 專用 context。 |
| `.ai/assets/skills/` | Canonical skill specs 與 skill registry。 |
| `.ai/assets/sub-agent-role-prompts/` | Sub-agent role prompts 的 canonical source。 |
| `.agents/skills/` | Codex 與目前 runtime 的 skill wrappers。 |
| `.claude/skills/` | Claude-compatible skill wrappers。 |
| `.dev/` | 人類可閱讀的 standards、guides、requirements、specs、release 與 workflow records。 |
| `.dev/releases/` | 發佈版本、相容性宣告與遷移說明。 |
| `AGENTS.md` | Codex 與通用 Agent 的 canonical root collaboration guide。 |
| `CLAUDE.md` | 匯入 `AGENTS.md` 的 Claude Code project-memory 薄入口。 |

## 在其他專案採用

1. 從已發佈版本取得對應的可攜式 AI context 封包，而非直接複製此來源庫的全部內容。
2. 依該版本的 release 與 migration guide 安裝或升級。
3. 在目標專案先使用 `ai-context-init` 盤點真實檔案、設定與既有文件，建立 target-specific truth。
4. 保留目標專案自己的需求、規格、架構、營運文件與決策；它們不應由此來源庫覆寫。
5. 依工作類型選擇對應 skill，例如需求、規格、架構、實作、測試設計或 code review。

詳細的遷移與邊界規則，請見 [`migration-boundaries.md`](.ai/assets/skills/ai-context-init/references/migration-boundaries.md)。

## 發佈邊界

本 repository 同時是框架的維護來源與發佈封包的建置來源，但兩者包含的內容不同：

- 根目錄 README、來源庫的 Agent entry files、歷史 workflow、assessment、release records 與產品 placeholder 均屬於來源庫資訊，不會放進下游封包。
- 可攜式封包只收錄 distribution profile 明確列出的可重用內容，並以排除規則作為第二道保護。
- 因此，更新本 README 只會改善此來源庫的可讀性，不會改變已發佈版本，也不會讓 README 被誤納入未來封包。

## 語言

- `README.md` 是人類導覽用途的繁體中文（台灣）版本。
- `README.en.md` 是對應的英文版本。
- Agent-facing context 優先使用英文；人類導覽與協作文件可使用繁體中文（台灣）。完整原則請見 [`.dev/standards/AI-CONTEXT-LANGUAGE-POLICY.md`](.dev/standards/AI-CONTEXT-LANGUAGE-POLICY.md)。
