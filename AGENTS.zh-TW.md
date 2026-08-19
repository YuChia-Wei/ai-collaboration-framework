# AGENTS.md

[English](AGENTS.md)

本文件是 canonical English root collaboration guide 的繁體中文翻譯；`AGENTS.md` 是 canonical English root collaboration guide。

## 適用範圍與 Authority

- 這是可重用 AI collaboration framework 的 source repository，並非 product application。
- 較深層的 `AGENTS.*` 檔案，在其 subtree 內優先於本文件。
- 優先順序為：使用者與核准、較深層的 `AGENTS.*`、本文件、其他一般文件。
- 使用 Git-tracked files、validated records 與 provider read-back。Historical records 是 evidence，不是 current state。
- Source-framework、target、provider 與 runtime truth 必須分開。
- 不得捏造 facts、authorization、availability、execution、validation、Issue state 或 release state。遇到未決 owner-sensitive decisions 時停止。

## 執行規則

- 實作符合 accepted scope 與 completion criteria 的最小 coherent change。
- 只修改必要檔案；保留無關的 user changes。
- Implementation、push、PR、merge、Issue／Project mutation、tag、release、publication 與 credential use 是不同動作，除非已一起授權。
- Inventory、paths、hashes、schemas、Git identity、build、test 與 receipts 優先使用 deterministic tools。
- `failed`、`blocked-by-environment`、`not-applicable` 與 `deferred-with-owner` 都不是 `passed`。
- 適用且已允許時，優先使用 IDE MCP refactoring operation。

## 漸進式 Context 載入

1. 從 request、目前 Git/worktree state、本文件，以及明確指定的 Issues 或 artifacts 開始。
2. 先選定一個 owning skill 或 policy，再載入其 canonical entry。
3. 只有適用的 phase、finding、file type、provider、decision 或 execution boundary 才擴大 context。
4. 不得預先載入 `README.md`、所有 indexes、所有 standards、每個 skill reference、historical workflows 或 assessment archives。
5. 除非 scope 需要，不要 broad-scan `src/`、`tests/`、`.dev/workflows/` 或 `.dev/assessments/`。
6. 重要結論以 Git-tracked evidence、provider read-back 或 repository-owned validators 驗證；沒有搜尋結果不代表不存在。

## 任務路由

使用 `.ai/assets/skills/README.MD` 作為 canonical skill registry。Runtime wrappers 保持 thin，不得成為第二個 authority。

| Need | Owning route |
| --- | --- |
| AI-context audit | `ai-context-auditor` |
| AI-context governance、routing、translation、remediation 或 source-release governance | `ai-context-governance` |
| 第一次 target adoption 或 initialized-target upgrade | `ai-context-init` / `ai-context-upgrader` |
| Historical 或 exceptional release verification | `ai-context-release-closeout` |
| 多階段 software development | `software-development-orchestrator` |
| Architecture、GWT design、review 或 implementation | `ddd-ca-hex-architect` / `bdd-gwt-test-designer` / `code-reviewer` / `slice-implementer` / `local-change-implementer` |
| Requirements、specifications、problem frames 或 selected compliance | `requirement-author` / `spec-author` / `problem-frame-author` / `spec-compliance-validator` |

- AI-context placement 或 language changes 只有適用時才載入 `.dev/standards/AI-CONTEXT-BOUNDARY.md` 與 `.dev/standards/AI-CONTEXT-LANGUAGE-POLICY.md`。
- Code review 先載入 `.ai/assets/skills/code-reviewer/references/review-routing.yaml`，且只載入 selected route 與 finding references。
- `test-execution` 沒有 required skill；先解析 target-owned commands。
- Direct execution 仍然有效。Delegation 時載入 `.ai/assets/shared/ROLE-EXECUTION-CONTRACT.md`；static profile presence 不是 invocation evidence。

## Workflow 與變更控制

- 小型、局部、單次可完成的工作可以維持 direct mode。
- Source-of-truth、AI-context、routing、wrapper、multi-stage 或 durable cross-session work，載入 `.dev/standards/WORKFLOW-GATE-POLICY.md`。
- Workflow mode 時，遵循 `.dev/standards/WORKFLOW-ARTIFACT-POLICY.md` 與 `.dev/TEAM-GIT-FLOW-RULES.MD`；material edits 前切換 dedicated branch。
- 唯讀報告使用 `.dev/standards/ASSESSMENT-ARTIFACT-POLICY.md`；報告本身不必然需要 workflow。
- Cross-session transfer 遵循 `.dev/standards/WORKFLOW-HANDOFF-POLICY.md`；checkpoint 不得依賴 hidden conversation state。
- Commit 前遵循 `.dev/standards/GIT-COMMIT-POLICY.md`。
- Merge、workflow completion、Issue closure、Project status、release allocation、publication 與 target upgrade 是不同 state。

## 驗證與檢閱

- 定義 observable acceptance criteria，並先執行最小但有意義的 validation。
- 不得只為了讓 test 通過而弱化 fail-closed behavior。
- Independent review 綁定 exact subject、維持 read-only，且不能把自己的 repair 當成 verification。
- Fixed-head audit 後的 mutation 會使該 audit 對新 head 失效。
- 保留 failure、timeout、interruption 與 blocked evidence；後來的 pass 不會抹除它們。

### 長時間驗證 Gate

- `release`、`nightly-full`、full matrix，或預期／已觀測 wall time 至少 120 秒時，視為 long-running。
- 先完成 tracked mutations 與 focused validation，再把 exact command 綁定到 clean immutable commit。
- 派送一個 read-only external task，使用足以完成工作的最低成本 profile；只寫入 ignored validation artifacts，且不得修復 subject。
- 使用 callback 或一次 event wait。不得輪詢。
- 只接受一份 schema-valid terminal report，綁定 exact task、commit、command、duration、outcome 與 evidence。
- Timeout、interruption、drift、缺少 evidence、cleanup failure 或 blocked execution 絕不會成為 `passed`。

## CLI 與 Runtime 邊界

- Higher-priority policy 選定 cross-boundary CLI execution 後，載入 `.ai/assets/shared/CLI-EXECUTION-ROUTING-CONTRACT.md`。
- Optional binding 只能位於 `.dev/ai-context/local/cli-execution-routing.yaml`；它必須保持 ignored、untracked、unstaged、secret-free，且不得進入 package 或 provenance truth。
- 不得隱含建立或更新。先驗證 recovery，再揭露 exact path、fields、`create/merge/replace` action 與 secret exclusion；拒絕或未回覆時不寫入。
- 不得靜默替換 model、provider、execution surface、credential boundary 或 permission。Static configuration 不代表 current-session execution。

## 停止條件

Authorization 缺失或矛盾、authority 無法解析、write 超出 scope、target-owned truth 未 reconciliation、required evidence 無法證明、fixed subject 已 drift，或需要新的 owner-sensitive decision 時，停止 mutation。

已授權範圍內可修復的 implementation、test 或 CI failures 不是 owner checkpoints。

## 導覽與語言

需要時才使用 indexes：

- `.ai/INDEX.MD`：可重用 agent-facing assets。
- `.dev/INDEX.md`：project knowledge 與 current records。
- `.dev/standards/INDEX.MD`：standards navigation。
- `.dev/guides/ai-collaboration-guides/INDEX.MD`：human-facing explanations，不是 default execution context。
- `.agents/skills/README.md` 與 `.claude/skills/README.md`：wrapper inventories。

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
