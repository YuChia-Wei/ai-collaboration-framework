# AGENTS.md

[English](AGENTS.md)

本文件是 canonical English agent-facing root collaboration guide 的繁體中文（台灣）翻譯；`AGENTS.md` 是 canonical English agent-facing root collaboration guide。

## 適用範圍與優先順序

- 本文件是 AI agents 與人類在此 repository 中協作時的根目錄指南。
- 這個 repository 是 AI 協作知識庫與可重用 context framework，不是產品應用程式 repository。
- 如果子目錄有其他 `AGENTS.*` 檔案，較深層的檔案優先。
- 指令優先順序：User/Approval > Subfolder AGENTS > This file > Other general documents。
- 若有設定 IDE 的 MCP Server，且該 MCP Server 提供重構功能，優先使用 IDE MCP Server 的重構能力。

## 預設執行原則

- 不得捏造專案事實。明確說明會影響結果的假設、不確定性與取捨。只有在尚未決定的方向會實質影響成果時，才詢問使用者。
- 實作符合既定驗收條件的最小且完整一致的變更。避免推測性的功能、抽象設計與 context。
- 僅修改任務所需的檔案。避免無關的清理，並移除自身變更所引入的 artifacts。
- 執行前先建立可驗證的完成條件。反覆修正直到條件通過；否則應回報具體阻礙與任何略過的 validation。

## Repository 定位

這個 repository 的用途是：

- 萃取軟體工程、架構、.NET backend 與 AI 協作知識；
- 維護可重用的 AI Agent context、skills、sub-agent prompts 與 workflow rules；
- 區分通用 AI context 與技術棧專用 context；
- 保留目前的非通用能力：.NET C# backend Web API 開發；
- 移除、隔離或 template 化歷史來源專案資訊。

除非檔案明確標示為 template、migration artifact 或 dotnet-backend reference，否則不要把歷史 sample backend 資訊視為目前產品真相。

## AI Agents 快速開始

1. 閱讀 `README.md` 或 `README.en.md` 以理解本 repo 的用途。
2. 在移動或重寫 AI context 前，先閱讀 `.dev/standards/AI-CONTEXT-BOUNDARY.md` 與 `.dev/standards/AI-CONTEXT-LANGUAGE-POLICY.md`。
3. 使用 `.ai/assets/skills/README.MD` 作為 canonical skill registry。
4. 使用 `.dev/guides/ai-collaboration-guides/INDEX.MD` 查閱 human-facing skill 與 workflow guides。
5. 使用 `.ai/INDEX.MD` 與 `.ai/README.MD` 瀏覽 agent-facing AI assets。

## 必要工作流程

### Workflow Gate

1. 當工作可能影響 source-of-truth、AI context、skill routing、wrapper sync，或跨越多個階段時，閱讀 `.dev/standards/WORKFLOW-GATE-POLICY.md`。
2. 當 gate 要求 workflow mode 時，主動建立 workflow artifacts。
3. 小型、局部、單次可完成的變更可維持 direct mode。
4. 為多個已核准 work items 建立不同 workflows 前，先評估 delivery cohesion；outcome、branch、validation、reviewers、release gate 與 rollback 相同時，通常使用同一個 delivery。
5. 少於三個實質 tasks 是 proportionality review signal；不要為了合理化 workflow mode 而捏造 validation 或 closeout tasks。

Workflow artifact 規則：

- 遵循 `.dev/standards/WORKFLOW-ARTIFACT-POLICY.md`。
- Branch 命名、checkpoint continuation、push 與 merge strategy 遵循 `.dev/TEAM-GIT-FLOW-RULES.MD`。
- 建立 workflow artifact 或進行實質修改前，先建立或切換到獨立 workflow branch。Codex 預設命名為 `codex/<workflow-id>`。
- 建立 `.dev/workflows/<workflow-id>/workflow.yaml` 作為 discovery locator。
- 新 workflow 使用完整日期 `YYYY-MM-DD-<topic>` ID。
- plan、task、report template、task ID 與 artifact root 由 workflow-owning skill 定義。
- artifact 預設位於 `.dev/workflows/<workflow-id>/`；若 skill 使用其他 repository-relative root，仍須在 `.dev/workflows/` 保留 locator。
- 新 workflow 與 task artifact 記錄 ISO 8601 `created_at` 與 `updated_at`。
- 2026-07-11 起建立的 workflow 必須記錄 `branch` 與 `base_branch`。
- 不要把 runtime workflow 紀錄放進 canonical skill 或 runtime wrapper 目錄。
- Workflow 尚未完成時若使用者要求 merge/push，視為 checkpoint handoff 並維持 workflow active。只有 push 時從已推送的 branch 接續；checkpoint merge 後則從更新後的 target 建立新的獨立 continuation branch。
- 在跨 model、runtime、host、machine 或 fresh session 轉交 active workflow 前，遵循 `.dev/standards/WORKFLOW-HANDOFF-POLICY.md`；receiving checkpoint 必須能在不依賴 hidden session context 的情況下執行。
- 依 `.dev/TEAM-GIT-FLOW-RULES.MD` 明確選擇線性或 merge-commit 整合；workflow mode 本身不決定 topology。

### Assessment Gate

- 唯讀 audit、大型 code review、architecture assessment 或類似報告需要保存時，遵循 `.dev/standards/ASSESSMENT-ARTIFACT-POLICY.md`。
- Durable observations 存放於 `.dev/assessments/<assessment-id>/`；不要只因報告需要落地就建立 workflow。
- Locator、report、commit subject 與 `Assessment-Id` trailer 使用穩定的 `ASM-YYYYMMDD-NNN` ID。
- 被評估的 surfaces 必須維持唯讀。若 remediation 已獲授權，建立或使用對應 workflow，並引用 assessment 與選定的 finding IDs。

### Git Commit Policy

1. 遵循 `.dev/standards/GIT-COMMIT-POLICY.md`。
2. 有 issue number 時使用 `<type>(#<issue-number>|<scope>): <summary>`。
3. 沒有 issue number 時使用 `<type>(<scope>): <summary>`。
4. workflow-stage commits 需包含 `Why`、`What`、`Validation` 與 `Workflow` body sections。
5. 每個 validated durable stage 或 coherent bounded batch 建立一個 commit，
   而不是每次 skill invocation 都 commit。只能改寫尚未 shared、尚未 pushed
   的 history，且須保留 approval、review、evidence、checkpoint 與 handoff 邊界。

### AI Context Governance

以下情境使用 `ai-context-governance`：

- 通用與技術棧專用 context 分類；
- AI 文件整理；
- 語言政策調整；
- skill routing 調整；
- runtime wrapper sync；
- context migration 規劃或執行。

不要將純 AI 文件治理工作交給 `bdd-gwt-test-designer`。

### AI Context Audit

執行唯讀的 AI context 健康度與漂移分析時，使用 `ai-context-auditor`。若結果只回覆於對話，可維持 transient direct mode；若只要求保存而未授權 remediation，則建立 standalone assessment 與 assessment branch，而不是 workflow。

- 預設只檢查 AI context 與治理 surfaces。
- 排除 `src/`、`tests/` 與其他產品 implementation trees。
- 若使用者要求掃描產品 source 或 test code，停止擴大 audit，改為轉介 `code-reviewer`。
- Audit finding 與 remediation 必須分開；只有在使用者授權整改後，才由 `ai-context-governance` 協調 AI context remediation lifecycle。
- 僅因分析有多階段或使用 sub-agent，不代表必須建立 workflow；前提是沒有 repository mutation、remediation 或 durable report。
- Durable report-only audit 對被稽核 surfaces 維持唯讀，commit 只包含 assessment-owned artifacts 與 assessment index updates。

### Development Workflow Orchestration

當軟體開發工作需要多階段規劃、開發 skill routing、sub-agent coordination、approval pause、target-aware test execution、validation checkpoint 或 commit checkpoint 時，使用 `software-development-orchestrator`。即使使用者沒有說出 `software-development-orchestrator` 或 downstream skill 名稱，只要 high-level software-development intent 符合上述範圍就應啟動；依 requested outcome、current artifacts 與 repository policy 推導 stages，不要只從 skill 名稱判斷。

該 skill 可以協調 downstream skills，但不應取代它們各自的專業責任。

Requirement、design 或 specification 尚待核准時，先暫停，不要建立或執行
implementation work；繼續前必須記錄 authorization source。

`test-execution` 是 optional、unmapped capability contract，不是新的 required
skill。依序使用 target-owned commands、經過獨立評估的 external skill、fallback
contract。Unit 與 integration 是預設；E2E、browser、Playwright 與
environment-dependent tests 是 conditional。Outcome 只能記錄為 `passed`、
`failed`、`blocked-by-environment`、`not-applicable` 或
`deferred-with-owner`；blocked 絕不等於 passed。

一般 AI context audit、文件治理或 repository initialization 不交給 `software-development-orchestrator`；改由對應 owner skill 與其自有 workflow template 處理。

### Repo Init / Template Adaptation

當這套 framework 被複製到既有或全新目標 repository 後，第一個 skill 應使用 `ai-context-init`。

該 skill 必須：

1. 依據檔案證據盤點目標 repository；
2. 辨識 copied template 或歷史來源專案真相；
3. 更新目標 repo 專屬的 `AGENTS.md`、`.dev/` 與必要 `.ai/` entry docs；
4. 除非目標 repo 明確推翻，否則保留 framework-level collaboration rules；
5. 移除或重寫來源 repo 專屬的 requirements、specs、operations docs、workflow artifacts 與 ADRs。

以 `.ai/assets/skills/ai-context-init/references/migration-boundaries.md` 作為 authoritative migration boundary。

### AI Context 版本升級

已初始化的目標 repository 要在已發布的 framework 版本之間升級時，使用 `ai-context-upgrader`。

- 必須有 `.dev/ai-context/provenance.yaml` 與
  `.dev/ai-context/customizations.yaml`，否則先進行明確的 unresolved
  provenance reconciliation。`.dev/AI-CONTEXT-SOURCE.yaml` 僅作 legacy
  read compatibility，兩種 authority 不得並存。
- 遵循 governance-owned semantic customization lifecycle；provenance
  finalization 前必須取得 owner reconciliation 與獨立的升級後 audit。
- 下游 repository 使用 `.ai/scripts/validate-ai-context-target.py`；source
  release registry 與 publication validation 不是下游前置條件。
- 寫入前比對已記錄的 framework 版本、欲升級版本與目標 repo 現況。
- 保留目標 repo 自有的協作規則、requirements、specs、ADRs、architecture、operations 與 project configuration truth。
- `automatic-candidate` 只是可安全提出的候選，不代表已取得寫入授權；只有驗證成功後才能更新 provenance。
- 證據以 Git 與 repository files 為準；外部 graph 或 index 只能加速探索，不能證明完整性。

### Code Review

只有在 review .NET backend code 或 dotnet-backend implementation guidance 時才使用 `code-reviewer`。

適用 code review 時：

1. 閱讀 `.ai/assets/tech-stacks/dotnet-backend/references/CODE-REVIEW-INDEX.MD`。
2. 閱讀 `.ai/assets/skills/code-reviewer/references/checklist-reference.md`。
3. 辨識檔案類型，並閱讀 `.dev/standards/` 下對應 checklist。
4. 建立 checklist comparison table。
5. 將問題分類為 `CRITICAL`、`MUST FIX` 或 `SHOULD FIX`。
6. 若目標 repo 適用測試，執行最窄且有意義的 test command。

### Spec Compliance

Spec compliance 是 selectable gate。若 target profile、problem-frame workflow、
requirement 或 owner decision 都未明確選定，記錄為 `not-applicable`。選定後：

1. 執行 `spec-compliance-validator`。
2. Gate：coverage 必須是 100%。
3. Partial configuration、缺少 execution evidence 或 coverage 低於 100% 時
   fail closed；回到 implementation 或 test generation 後再宣稱完成。

## Skill Routing

- Canonical skill registry：`.ai/assets/skills/README.MD`
- Current runtime wrappers：`.agents/skills/README.md`
- Claude-compatible wrappers：`.claude/skills/README.md`
- Human-facing skill guides：`.dev/guides/ai-collaboration-guides/INDEX.MD`

當 canonical spec 與 runtime wrapper 不一致時，以 `.ai/assets/skills/` 作為 source of truth。

使用下列邊界：

| 需求 | Skill |
| --- | --- |
| 多階段軟體開發 workflow orchestration、development skill routing、validation 與 commit checkpoints | `software-development-orchestrator` |
| 唯讀 AI context 健康度、漂移與結構分析；可選擇對話輸出或保存報告 | `ai-context-auditor` |
| AI context cleanup、prompt boundary、language policy、wrapper sync | `ai-context-governance` |
| 將此 framework 複製到目標 repo 後的第一次同步 | `ai-context-init` |
| 將已初始化的目標 repo 升級到另一個已發布 framework 版本 | `ai-context-upgrader` |
| .NET backend architecture design | `ddd-ca-hex-architect` |
| GWT scenario 與 assertion design | `bdd-gwt-test-designer` |
| .NET backend code review | `code-reviewer` |
| Problem-frame spec compliance validation | `spec-compliance-validator` |
| Requirement authoring | `requirement-author` |
| Spec authoring | `spec-author` |
| Problem frame authoring | `problem-frame-author` |
| Bounded implementation slice | `slice-implementer` |
| 局部技術程式變更 | `local-change-implementer` |

`test-execution` 刻意不建立 required skill mapping。依 target-owned commands、
經過獨立評估的 external provider 或 fallback contract 執行。

## 檔案與目錄索引

### 根目錄入口文件

| Path | 說明 |
| :--- | :--- |
| `README.md` | 人類導向的繁體中文 repository identity |
| `README.en.md` | Repository identity 的英文翻譯 |
| `AGENTS.md` | Canonical English agent-facing root collaboration guide |
| `CLAUDE.md` | 匯入 `AGENTS.md` 的精簡 Claude Code project-memory 入口 |
| `AGENTS.zh-TW.md` | Root collaboration guide 的繁體中文（台灣）翻譯 |

Canonical AI assets 請使用 `.ai/INDEX.MD`，project knowledge 與 governance 請使用 `.dev/INDEX.md`，adapter inventory 則使用 **Skill Routing** 中所列的 runtime wrapper registries。詳細的目錄清單應保留在其各自擁有的 index 中，不要在這份一律載入的指南重複列出。

## 語言規則

- Agent-facing context 應優先使用英文，除非來源材料本質上就是 human-facing 繁體中文。
- Human-facing guides 與 README content 應優先使用繁體中文台灣用語。
- Runtime wrappers 應保持輕量，並指向 canonical specs。
- Context 分類優先使用資料夾位置，而不是每個檔案各自加 metadata。
