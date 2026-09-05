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
| 已觀察的故障、效能症狀或根因診斷 | `diagnostic-analyst` |
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
- Commit 前遵循 `.dev/standards/GIT-COMMIT-POLICY.md`，並在執行 `git commit` 前以 message file 驗證完整 planned message。
- Merge、workflow completion、Issue closure、Project status、release allocation、publication 與 target upgrade 是不同 state。

## 驗證與檢閱

- 定義 observable acceptance criteria，並先執行最小但有意義的 validation。
- 不得只為了讓 test 通過而弱化 fail-closed behavior。
- Independent review 在一個 immutable commit 上執行、綁定 exact content subject、維持 read-only，且不能把自己的 repair 當成 verification。
- Review 後若 content、criteria 或 authority drift，該 review 即失效。只有 commit SHA drift 時只需執行 deterministic current-subject rebind，不必重做 independent review。
- 保留 failure、timeout、interruption 與 blocked evidence；後來的 pass 不會抹除它們。

### Validation Freeze 與 Evidence Reuse

- Reuse 前將 validation evidence 分類為 identity-sensitive、input-sensitive、environment-sensitive 或 provider-sensitive。只有 tracked bytes、transitive dependencies、command、profile、environment、runner、manifest、resolver、policy 與 configuration authority 全部相容時才可 reuse。
- 只有完成 tracked mutation 與 focused validation 後才可 freeze。Freeze 後若 tracked content 或 governing authority drift，subject 即失效；只有 history-only identity drift 時則執行 rebind。Terminal metadata 只能寫入已宣告的 ignored artifacts，且不會使 frozen snapshot 失效。
- Unknown dependency 或 authority state 必須 fail closed。Current-head review-subject binding、required hosted contexts 與 live admission gates 一律 fresh；content digest 相等時可 reuse independent review，無須重做。
- 每個 admitted head 都必須保留 required hosted contexts。內部可以 execution 或 proven reuse，但 path filtering 不得讓 required context 消失。
- Content-addressed independent audit 對每個 gate 回報 `re-executed`、`reused-with-proof`、`blocked`、`deferred` 或 `not-applicable`；commit SHA 只保留為 provenance，不作為 validity key。

### Agent Execution Guardrails

- Delegated、external 或 fixed-head execution 前，驗證 agent execution packet；其中包含 owning skill、canonical role path 與 applicability、exact SHA/argv/cwd、permissions、ignored artifact roots、terminal schema 與 callback、integration owner、stop conditions 與 retry budget。SHA 用來固定 execution checkout；evidence validity 依適用的 content-subject contract 判定。
- 持有 machine-readable worktree snapshot lease。一個 active tracked-writer holder 排除其他所有 tracked writer；read-only work 與已宣告的 ignored validation output 仍可進行，terminal release 必須明確記錄。
- 維護 acceptance-to-evidence ledger 並驗證其 human-report projection。Synthetic、mock、fixture 與 unit evidence 不得滿足要求 actual execution 的 acceptance。
- 只有具備 privacy-safe failure fingerprint 與 material state change 才可 retry。Attempt 三次以上需要新的 owner 或 workflow authorization。
- Discovery conclusion 前驗證 code-graph index SHA 與 coverage。Stale 或 missing graph 必須 reindex 或使用明確 tracked-file fallback；search absence 本身不是 proof。
- PowerShell automatic 或 reserved variables 一律不得被賦值，且不分大小寫；使用用途明確的 variable names。

### 長時間驗證 Gate

- `release`、`nightly-full`、full matrix，或預期／已觀測 wall time 至少 120 秒時，視為 long-running。
- 先完成 tracked mutations 與 focused validation，再把 exact command 綁定到 clean immutable commit。
- 派送一個 read-only external task，使用足以完成工作的最低成本 profile；只寫入 ignored validation artifacts，且不得修復 subject。
- 使用 callback 或一次 event wait。不得輪詢。
- 只接受一份 schema-valid terminal report，綁定 exact task、commit provenance、content subject、command、duration、outcome 與 evidence。
- Timeout、interruption、drift、缺少 evidence、cleanup failure 或 blocked execution 絕不會成為 `passed`。

### 可攜式 Test Fixture 加速

- Portable baseline 為零設定。只有在 `.ai/scripts/test-fixture-classifications.json` 中明確分類為 disposable fixture I/O 的測試，才可使用 `AI_CONTEXT_TEST_TMP_ROOT`。
- 此設定只接受單一、明確 opt-in 的 fixture root。不得自動探索 storage、修改全域 `TEMP` 或 `TMP`，也不得將 durability-storage 或 platform-filesystem semantics 導向該 root。
- 實際執行時重新 preflight、建立唯一且受 containment 驗證的 run directory，cleanup 只可刪除該 verified directory。Invalid、unsafe 或 unwritable root 必須在 material fixtures 前失敗。
- Diagnostics 不得包含 path。WSL `/mnt/*` performance warning 只是 advisory；不得改變 test outcome，也不得靜默選擇其他 root。
- Default 與 accelerated mode 必須在同一 commit、同一 host 使用相同 tracked test profile 比較。Median 至少使用三次執行，並明確標示 cold 或 warm condition。
- Local 與 manual CI 用法請見 `.dev/guides/implementation-guides/PORTABLE-TEST-FIXTURE-ACCELERATION-GUIDE.md`。

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
