# AGENTS.md

[English](AGENTS.md)

本文件是 canonical English root collaboration guide 的繁體中文翻譯；`AGENTS.md` 是 canonical English root collaboration guide。

## Source 開發規則

一般 source 工作讀取 [source 開發政策](.dev/standards/SOURCE-DEVELOPMENT-POLICY.md)，
確認驗證必要性、PR 檢查、條件式獨立審查與規範維護。該政策擁有這些規則；本入口提供導覽。
Owner 於 2026-10-18 的 #461 決策僅簡化本專案規範；#463 的 framework 產品變更
需要另行取得實作授權。Release、支援、credentials、protection 與 downstream adoption
維持原有 owner。Merge 或日期都不能證明 CI 成功。

## 適用範圍與 Authority

- 這是可重用 AI collaboration framework 的 source repository，並非 product application。
- 較深層的 `AGENTS.*` 檔案，在其 subtree 內優先於本文件。
- 優先順序為：使用者與核准、較深層的 `AGENTS.*`、本文件、其他一般文件。
- 使用目前的 Git-tracked files、validated records 與即時 provider read-back。Historical workflows、assessments、releases、examples 與 migrated records 是 evidence，不是 current state。
- Source-framework、target、provider 與 runtime truth 必須分開。
- 不得捏造 facts、authorization、availability、execution、validation、Issue state 或 release state。遇到未決 owner-sensitive decisions 時停止。

- 公開 Epic／Feature／Story、Issue 與 PR 內容（含留言與 review 討論）必須遵守[公開需求內容規則](.dev/standards/PUBLIC-REQUIREMENT-CONTENT-POLICY.md)。執行授權與交接必須使用 workflow 機制，不得存入 Issue 或 PR 管道；保留功能討論、相依、驗證／審查證據與功能完成摘要。

## 執行規則

- 實作符合 accepted scope 與 completion criteria 的最小 coherent change。
- 只修改必要檔案；保留無關的 user changes。
- Implementation、push、PR、merge、Issue／Project mutation、tag、release、publication 與 credential use 是不同動作，除非已一起授權。
- Inventory、paths、hashes、schemas、Git identity、build、test 與 receipts 優先使用 deterministic tools。
- `failed`、`blocked-by-environment`、`not-applicable` 與 `deferred-with-owner` 都不是 `passed`。
- 適用且已允許時，優先使用 IDE MCP refactoring operation。
- 依任務從 `.ai/project/sub-agent-policy.json` 選擇 sub-agent 模型與推理深度，不得直接繼承本對話。優先使用確定性工具；Codex 預設 Luna，實質推理使用 Sol；Claude 預設 Haiku，依任務使用 Sonnet。Astra／Opus 必須另行取得明確授權。確認 runtime 覆寫與實際呼叫身分；缺少政策或選定模型不可用時，停止該次委派。專案模型偏好與受管理角色套件分開維護，見[子代理管理](docs/sub-agent-management.md)。
- 透過 `.ai/project/sub-agent-registry.json` 解析已登記的 sub-agent 用途，委派前確認選定套件與 runtime entry。專案原稿放在 `.ai/project/sub-agents/`。保留未知 entry，分開判讀上游涵蓋、owner 採納、檔案讀回與 runtime 啟用。登記資料不授予 framework 所有權，也不授權自動切換路由。

## 漸進式 Context 載入

1. 從 request、目前 Git/worktree state、本文件，以及明確指定的 Issues 或 artifacts 開始。
2. 先選定一個 owning skill 或 policy，再載入其 canonical entry。可直接使用產生的 runtime entry；只有查閱 metadata、維護或釐清不一致時，才重新載入完整來源。
3. 只有適用的 phase、finding、file type、provider、decision 或 execution boundary 才擴大 context。
4. 不得預先載入 `README.md`、所有 indexes、所有 standards、每個 skill reference、historical workflows 或 assessment archives。
5. 除非 scope 需要，不要 broad-scan `src/`、`tests/`、`.dev/workflows/` 或 `.dev/assessments/`。
6. 重要結論以 Git-tracked evidence、provider read-back 或 repository-owned validators 驗證；沒有搜尋結果不代表不存在。

## 任務路由

Codex 使用 `.agents/skills/<skill-id>/SKILL.md`，Claude 使用 `.claude/skills/<skill-id>/SKILL.md`，兩者皆以原始 skill ID 命名。這些 generated entries 與 `.ai/core/skills/` 是可編輯產品來源 `src/skills/` 的安裝投影；透過 `.ai/project/installation.json` 選取。不得編輯 generated installed files。目前來源 distribution catalog 有 22 個 skills；版本與責任見 [skill 目錄](docs/skills/README.md)。來源以 `domain-model-designer` 與 `software-architect` 取代 `ddd-ca-hex-architect`，不保留 alias。原本選取舊 ID 的四個來源 presets 現在改選兩個新 ID。本來源專案安裝 AICF 0.21.0，共 18 個 skills，包含 `domain-model-designer` 與 `software-architect`；已移除退役的合併架構 entry。呼叫前須核對實際 runtime entry。可選的 `ai-context-init`、`workflow-records` 與 `user-story-author` 仍是可獨立選取的來源套件。`project-initialization` preset 獨立選取初始化。安裝此套件只提供文件撰寫資源，不代表根目錄文件已初始化。`standards-promotion@0.1.1-alpha.1` 保留於 `src/skills/`，供獨立複製試驗；在 owner 選定的驗證完成前，排除於 catalogs、presets 與發布成品，且不是本來源專案已安裝的路由。Generated installation state 分開更新。已移除的 compatibility roots 不提供目前可執行路由。

| Need | Owning route |
| --- | --- |
| AI-context audit 或 comparison | `ai-context-auditor` |
| AI-context governance 與 reusable context maintenance | `ai-context-governance` |
| 領域探索／建模或軟體架構 | 領域探索／建模使用 [domain-model-designer](.agents/skills/domain-model-designer/SKILL.md)，軟體架構使用 [software-architect](.agents/skills/software-architect/SKILL.md)（Claude：對應的 `.claude/skills/<skill-id>/SKILL.md` entries）。依各自安裝契約操作；兩者都不是退役合併 skill 的 alias。 |
| Test design、code review、diagnosis 或 implementation | `test-designer` / `code-reviewer` / `diagnostic-analyst` / `slice-implementer` / `local-change-implementer` |
| Requirements、specifications、problem frames 或 selected compliance | `requirement-author` / `spec-author` / `problem-frame-author` / `spec-compliance-validator` |
| Decisions、lessons、local backlog 或 pull requests | `adr-author` / `lesson-author` / `local-backlog` / `pr-author` |
| 多階段軟體開發 | `software-development-orchestrator` 負責階段選擇與專業 skill 交接；source `.dev/` policy 與 Issue authority 擁有 workflow records 與整合權限 |
| 初始化或升級先前發布的 legacy package format | 保留 source compatibility duty，目前沒有 portable 或可執行路由；執行前須恢復已驗證的 source-owned procedure。 |
| Historical 或 exceptional source release closeout | `releases/` 與 source release policy；沒有 portable installed skill route。 |

Source work 仍由 `.dev/standards/` 擁有 source policy、GitHub work authority、release governance、U001 與 P7 deferrals。明確保留以下 source duties：source assessment persistence 與 terminal records；source customization 與 policy reconciliation；legacy CBF/SWF intake 與 active records；target-selected legacy .NET 100% gate 與 rule resolver（僅維護該舊版下游格式或 target 時適用，不適用於本 framework source 或其自身安裝）；舊 published-format initialization、upgrade 與 recovery。保留 duty 不代表工具可用。已移除的 legacy roots 與仍依賴它們的 validators，在恢復已驗證的 source-owned route 前不可用；它們不會恢復已移除的 runtime discovery entries。

- AI-context placement 或 language changes 只有適用時才載入 `.dev/standards/AI-CONTEXT-BOUNDARY.md` 與 `.dev/standards/AI-CONTEXT-LANGUAGE-POLICY.md`。
- Code review 載入 installed `code-reviewer` entry，並只載入其適用的 route 與 finding references。
- `test-execution` 沒有 required skill；先解析 target-owned commands。
- Direct execution 仍然有效。依 `.dev/contracts/AGENT-EXECUTION-GUARDRAILS-CONTRACT.md` 界定 delegation 範圍；只有適用時才載入所選角色的現行指示。`.dev/contracts/ROLE-EXECUTION-CONTRACT.md` 說明來源專案的執行證據；其中的歷史格式不會選定一般來源作業程序。Static profile presence 不是 invocation evidence。

## Workflow 與變更控制

- 小型、局部、單次可完成的工作可以維持 direct mode。
- Source-of-truth、AI-context、routing、wrapper、multi-stage 或 durable cross-session work，載入 `.dev/standards/WORKFLOW-GATE-POLICY.md`。
- Workflow mode 時，遵循 `.dev/standards/WORKFLOW-ARTIFACT-POLICY.md` 與 `.dev/TEAM-GIT-FLOW-RULES.MD`；material edits 前切換 dedicated branch。
- 日常執行紀錄儲存與明確的 native continuation 遵循[工作流程儲存政策](.dev/standards/WORKFLOW-STORE-POLICY.md)。使用其中明確指定的 configuration 與 source CLI；可選的 `workflow-records` package 未安裝於此專案。正式產物仍由 Git 管理，歷史 workflow files 保留為 provenance；不選用自動探索或 Git fallback。
- 需留存的唯讀報告使用 `.dev/standards/ASSESSMENT-ARTIFACT-POLICY.md`；報告本身不必然需要 workflow。
- Cross-session transfer 遵循 `.dev/standards/WORKFLOW-HANDOFF-POLICY.md`；checkpoint 不得依賴 hidden conversation state。
- Commit 前遵循 `.dev/standards/GIT-COMMIT-POLICY.md`，並在執行 `git commit` 前以 message file 驗證完整 planned message。
- Merge、workflow completion、Issue closure、Project status、release allocation、publication 與 target upgrade 是不同 state。

## 驗證與檢閱

- 測試前依 source policy 對實際 diff、語意與直接相依判斷必要性。修改存在或副檔名本身不會觸發本機測試。
- 保留 PR hosted gate 與適用的獨立審查。本機檢查、review、hosted 結果與 acceptance 各自證明不同事實。
- 已授權的規範變更應在 owner 位置替換失效指令。保留有效保護與無關內容；不得在矛盾操作文字上持續疊加優先聲明。
- 保留失敗與限制。不得聲稱未執行的測試通過，或只為通過檢查而弱化行為。
- 委派工作讀取 [agent guardrails](.dev/contracts/AGENT-EXECUTION-GUARDRAILS-CONTRACT.md)。維持單一 tracked writer、不可變且唯讀的獨立審查，遵循使用者實際選定的 model／effort 與權限。
- 只有解讀先前結果時才讀取 [evidence guidance](.dev/contracts/VALIDATION-EVIDENCE-LIFECYCLE-CONTRACT.md)。一般工作不需另外建立 reuse receipt、hash 清冊或 acceptance ledger。
- Discovery conclusion 前確認 code-graph index SHA 與 coverage。Stale／missing graph 應 reindex 或採明確 tracked-file fallback；search absence 不是 proof。
- PowerShell automatic 或 reserved variables 一律不得賦值，且不分大小寫；使用用途明確的名稱。

### 歷史背景 — 不符合觸發條件，不得據此執行

早期 U001／重構與 fixture acceleration 指令不是一般 source 工作程序。
不得只因歷史紀錄提及便載入或執行。只有另行選定的 legacy／native／release 義務
才使用相容版本與已驗證路由；缺失工具維持 unavailable，保留的 deferred 狀態不等於通過。
Release、支援與 recovery 義務仍由原 owner 負責。
[暫時執行例外](.dev/standards/FRAMEWORK-REDESIGN-EXECUTION-OVERRIDE.md)
僅為上述明確保留義務的歷史背景。

## CLI 與 Runtime 邊界

- Higher-priority policy 選定 cross-boundary CLI execution 後，載入 `.dev/contracts/CLI-EXECUTION-ROUTING-CONTRACT.md`。
- Optional binding 只能位於 `.dev/ai-context/local/cli-execution-routing.yaml`；它必須保持 ignored、untracked、unstaged、secret-free，且不得進入 package 或 provenance truth。
- 不得隱含建立或更新。先驗證 recovery，再揭露 exact path、fields、`create/merge/replace` action 與 secret exclusion；拒絕或未回覆時不寫入。
- 不得靜默替換 model、provider、execution surface、credential boundary 或 permission。Static configuration 不代表 current-session execution。

## 停止條件

Authorization 缺失或矛盾、authority 無法解析、write 超出 scope、target-owned truth 未 reconciliation、required evidence 無法證明、fixed subject 已 drift，或需要新的 owner-sensitive decision 時，停止 mutation。

已授權範圍內可修復的 implementation、test 或 CI failures 不是 owner checkpoints。

## 文件所有權

- 可編輯的共用資源放在 `src`；framework 能力所需的資源必須包含於其中，或宣告為 knowledge dependencies。所有下游套件成員及必要 runtime 資源都必須源自 `src`。根目錄 `tools` 負責來源專案的編排與驗證；產品執行不得復用它或任何 `src` 以外的資源。
- `.dev` 擁有本專案的紀錄、規範與協作；`docs` 擁有產品文件。本 repository 同時開發及使用 framework，來源與安裝副本可以共存。
- 先整理共用資源至來源，再另行選定自我安裝／升級。移除過時且無經驗傳承價值的文件；此次整理保留 `.dev/design`、`.dev/assessments`、`.dev/requirement`、`.dev/adr` 與 `.dev/workflows` 的既有歷史。

## 導覽與語言

需要時才使用 indexes：

- `.ai/INDEX.MD`：generated installed content 與 source-tooling data。
- `.dev/INDEX.md`：project knowledge 與 current records。
- `.dev/standards/INDEX.MD`：standards navigation。
- `docs/`：產品使用手冊；`.dev/guides/` 說明來源專案的工作與經驗。
- `.agents/skills/README.md` 與 `.claude/skills/README.md`：installed skill inventories。

### 根目錄 Entry Files

| Path | Responsibility |
| --- | --- |
| `README.md` | Human-facing Traditional Chinese repository entry |
| `README.en.md` | English repository entry |
| `AGENTS.md` | Canonical English root collaboration guide |
| `AGENTS.zh-TW.md` | Traditional Chinese translation |
| `CLAUDE.md` | Thin Claude project-memory adapter |

- Agent-facing execution contracts 應優先使用 English。
- Human-facing guides 可以使用繁體中文（台灣）或 English。
- `AGENTS.zh-TW.md` 必須與本文件保持 structural 與 normative alignment；不得新增或移除 rules。
