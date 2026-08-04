# AI Context Rule Architecture Issue Draft

- `status`: `ready-for-owner-review`
- `target_repository`: `YuChia-Wei/ai-collaboration-prompts-dotnet-backend`
- `source_workflow`: `2026-07-30-ai-context-architecture-kit-standards-discussion`
- `prepared_at`: `2026-08-02T17:09:26+08:00`
- `updated_at`: `2026-08-02T17:26:31+08:00`
- `github_action`: no issue created

## Suggested Title

`[Proposal] Define Layered Engineering Rule Ownership, Target Policy, and .NET Analyzer Bindings`

## Suggested Labels

- `kind:proposal`
- `scope:framework`
- `triage:needed`

## Copy-Ready Issue Body

### 問題或機會

AI Context 已經擁有軟體工程標準、.NET backend profile、skill routing、target customization lifecycle，以及隨 framework source 發布的 Roslyn Analyzer／validation tools；另一方面，獨立的 `dotnet-architecture-kit` 正在評估承接 .NET 機械式驗證並發布為 NuGet。

目前缺少一份完整契約，明確區分：

1. AI Context core 所擁有的跨語言軟體工程概念與設計意圖；
2. Technology Profile 所擁有的生態慣例、具體限制、範例與工具綁定；
3. Target repository 所擁有的有效規則狀態、ADR、customization、`.editorconfig` 與 tooling waiver；
4. Architecture Kit 所擁有的 .NET Analyzer 實作、Diagnostic 行為與 NuGet 版本。

如果只有高階文字規範，而沒有在 AI 產生程式碼前提供 Analyzer 真正檢查的具體 observable constraints，AI 可能先產生「概念上看似正確」但會被 Analyzer 拒絕的程式碼，再使用昂貴的文字推理反覆修正。反過來，如果直接讓 Diagnostic ID 或 `.editorconfig` 成為規則語意的來源，AI Context 又會被 .NET／Roslyn 實作細節綁定，無法支援 Java、TypeScript、Rust 或未來 frontend profiles。

團隊也需要保留不同工程判斷的空間。相同的 Diagnostic suppression 可能代表：

- 不認同工程規則的 semantic deviation；
- 接受規則但調整嚴格度的 enforcement tuning；
- 接受規則但避開 false positive 的 tooling waiver。

這三者不應被同一個 `.editorconfig` 結果或同一種 customization 紀錄取代。

### 目前證據（2026-08-02）

- `.dev/standards/AI-CONTEXT-OWNERSHIP.yaml` 已有 stable `rule_id`、scope、strength 與 override policy，但仍是 flat rule registry，尚未分離 concept、rule、constraint、abstract enforcement capability 與 technology binding。
- `.ai/assets/skills/ai-context-governance/templates/customizations.schema.yaml` 的 semantic subject 目前為 `capability | rule | contract`，尚無 constraint identity 與完整 effective target rule profile 契約。
- `.ai/distribution/profiles/dotnet-backend.yaml` 仍將 `tools/**` 當成 framework-managed .NET component 發布。
- `tools/DotnetBackendAnalyzers` 與 `tools/DotnetBackendValidation` 仍為 `IsPackable=false`；Analyzer README 仍要求在規則與 skill integration 穩定前維持 source-included，而不是發布 NuGet。
- 目前 AI Context source 尚未宣告 Architecture Kit package identity、compatible version range 或 rule／constraint-to-Diagnostic mapping。
- GitHub open/closed issue 查重未找到直接涵蓋這份完整設計的既有 issue。#61 負責 standards simplification deliberation；本提案是該類討論產生的具體架構與 lifecycle 候選。

### 期望成果

建立一個版本化、可驗證、可逐步遷移的三層規則模型：

| 層級 | 擁有內容 | 不應擁有 |
| --- | --- | --- |
| AI Context core | 跨語言 concept、normative rule、observable constraint、abstract enforcement capability、協作與判斷流程 | Roslyn、Diagnostic ID、NuGet 或 `.editorconfig` 實作細節 |
| Technology Profile | 語言／framework 慣例、profile-owned rules、具體範例、tool bindings、package compatibility、configuration surfaces | Target 團隊的最終採用理由 |
| Target Repository | 完整 effective rule state、ADR、semantic deltas、enforcement tuning、tooling waivers、實際 package/configuration | 重寫 framework 或工具的 canonical semantics |

Architecture Kit 是 .NET Profile 背後的一個獨立 mechanical-validation provider；它不成為 AI Context 規則語意的反向來源。

### 提議契約

#### 1. 正規化規則模型

分離並給予 stable identity：

- `concept`: 跨多個規則共享的工程概念；
- `rule`: 規範性的工程決策；
- `constraint`: 可由實作、review 或工具觀察的具體限制；
- `enforcement-capability`: technology-neutral 的驗證能力，例如 static analysis、executable test、AI assessment 或 human review；
- `technology-binding`: profile 將 constraint／capability 綁定到 tool、package version、Diagnostic ID、command 或 configuration surface 的實作資料。

關係必須使用 stable identity 明確連結，允許一個 concept 對應多個 rules、一個 rule 對應多個 constraints，以及一個 constraint 對應多個 capabilities／technology bindings。

正規化 canonical model 不代表每次對話都載入完整 graph。Routine AI work 只投影當前 task、target policy 與 selected profiles 所需的最小 concept／rule／constraint；package、command、Diagnostic 等 binding 資料只在 implementation、validation、upgrade 或 diagnostic handling 時載入。

#### 2. Core 與 Technology Profile 的語意邊界

- 有實質跨語言意義的工程意圖由 core 擁有。
- 精確 syntax、naming、types、framework conventions、examples 與 tool bindings 由 Technology Profile 擁有。
- 沒有可信跨語言抽象的慣例可以直接成為 profile-owned rule，不需要為了形式統一而創造空洞 core concept。
- Profile-owned rule 只有在出現可信的跨技術證據並經過 semantic review 與 versioned migration 後，才能提升到 core。

範例：core 可以要求 public asynchronous contract 清楚表達非同步完成與使用語意；`.NET` 的 `Async` suffix 是 TAP 生態慣例，應留在 .NET Profile，不應成為 TypeScript、Java 或 Rust 的通用命名規則。

#### 3. Target Rule Profile 與 customization

- 每個 target repository 擁有精簡但完整的 target rule profile，記錄當前 effective rule／constraint state。
- 已安裝的 AI Context baseline rules 預設是有效的 AI guidance，除非 target-owned evidence 明確調整；不把每條 baseline guidance 都變成 pending approval。
- ADR 保存 material alternatives、semantic deviations 與架構理由。
- `.dev/ai-context/customizations.yaml` 只記錄相對於 installed baseline 的 semantic delta，不複製所有未修改 defaults。
- Semantic customization 應引用 concept／rule／constraint identity 與 ADR 或其他 owner-approved evidence，不得用 Diagnostic ID 取代工程語意。
- Install、upgrade、reinstall 必須 reconcile target-owned effective state，不得以 incoming defaults 靜默覆蓋已確認決策。

#### 4. Architecture Kit adoption 與 .NET binding

- AI Context 的 .NET Profile 優先建議 Architecture Kit，但不強制安裝。
- 安裝／升級 AI Context 時，由適用的 .NET 開發者或 owner 決定是否安裝 Architecture Kit；未核准前不得加入 NuGet reference。
- Deferred package decision 以 `pending-review` continuation checkpoint 保存，且不影響既有 AI guidance 與一般 `.editorconfig` formatting／code-style defaults。
- 核准某個 Architecture Kit 版本代表採用該 package version 的完整 Diagnostic ruleset 與 package defaults，而不是在安裝前逐條挑選。
- `.editorconfig` 是 target-owned .NET enforcement configuration，可調整 severity 或停用 Diagnostic。
- .NET Profile 單向維護 AI Context constraint／capability identity 到 Architecture Kit package version range、Diagnostic ID 與 configuration surface 的 mapping。
- Architecture Kit 不需要引用 AI Context IDs、解析 AI Context schema，或提供反向 compatibility manifest。
- AI Context 與 Architecture Kit 獨立版本化，不需要 lockstep release。

#### 5. Diagnostic override 分類

`.editorconfig` 的結果不能單獨決定 governance 類型，必須根據意圖分類：

| 類型 | 工程語意 | 必要紀錄 |
| --- | --- | --- |
| Semantic deviation | 拒絕、取代或縮小 AI Context rule／constraint | target rule profile + ADR + `customizations.yaml` semantic delta |
| Enforcement tuning | 接受語意，只改變 severity、visibility 或執行時機 | target-owned enforcement configuration；預設不建立 semantic customization |
| Tooling waiver | 接受語意，但因 false positive、Analyzer defect 或 unsupported code shape 暫時避開 | Diagnostic／binding + linked constraint + local rationale + reconsideration trigger |

Tooling waiver 預設在 Architecture Kit upgrade 或 affected-code design material change 時重新檢視；不要求固定日曆到期。建立 upstream Architecture Kit issue 有幫助但不是 target waiver 的前置條件。

#### 6. Evidence-first diagnostic handling

AI 收到 Diagnostic 時應先：

1. 找到對應 engineering rule／constraint；
2. 確認 applicability 與 effective target policy；
3. 檢查 ADR、customization、enforcement tuning 或 tooling waiver；
4. 判斷問題屬於 code、configuration、mapping drift 或 Analyzer behavior；
5. 確認差異後才修改程式碼。

不要把所有 Diagnostic 都當成無條件重寫命令，也不要在已有可信 mechanical validation 時退回 grep 或大量 prose 猜測。

#### 7. Native development 與 CI consistency 分離

- `.editorconfig` 修改照 .NET／Roslyn／IDE／build 原生行為立即生效。
- 不因每次 `.editorconfig` 編輯就自動啟動 semantic reconciliation 或額外消耗 AI token。
- Cross-artifact consistency 由 AI Context／target CI 根據 profile 的單向 mapping，在明確的 final CI stage 比對 target rule profile、package、Diagnostic defaults、`.editorconfig` overrides 與 evidence references。
- Framework default 是 non-blocking warning／reminder；target team 可以自行提高嚴格度。
- Architecture Kit 提供 Diagnostic 的 mechanical behavior，不負責解析 AI Context 或判斷團隊理由是否正確。

#### 8. Mechanical validation 的跨技術原則

- Rule 沒有 mechanical binding 時仍是有效 AI guidance。
- Profile 應先調查 compiler、analyzer、linter、formatter、test framework 或 architecture-test tool 等 language-native 機制。
- 只有 credible、maintained、versionable、deterministic 的機制才能成為正式 binding。
- 沒有可信 binding 時記錄為 AI-assessed／unbound，不假裝 generic `.sh` 或文字搜尋已完成機械式驗證。
- 其他語言不因 .NET 使用 Roslyn Analyzer 就被迫採用相同工具模型。

#### 9. Technology references、skills 與 external skills

- Technology Profile 擁有 concrete rules、examples、pitfalls 與 tool-binding references。
- Architecture、implementation、review 等 action skills 只載入當前 task 所需的最小 profile references；skill 擁有 workflow，不複製 profile semantics。
- 不為了容納 .NET 知識而新增籠統的 `dotnet-engineering` skill。
- External skills 分為三層：unregistered coexistence、target-approved registry／allowlist、少數 AI Context-maintained thin adapters。
- External skill 永遠受 repository truth、effective target profile、approval gate 與 completion contract 約束。

### Provider transition

#### Current state

- 在 Architecture Kit 尚未符合 cutover gate 前，`tools/**` 是 .NET custom mechanical validation 的唯一 supported provider。
- 不提供 framework-level Architecture Kit preview binding，也不讓兩個 providers routine 執行同一組 Diagnostics。

#### Cutover gate

至少需要：

- 已發布且 immutable 的 Architecture Kit NuGet package identity/version；
- Diagnostic-to-constraint crosswalk；
- Analyzer behavior／parity evidence；
- consumer installation、upgrade 與 configuration guidance；
- .NET Profile 宣告 compatible version range；
- target consumer proof；
- owner approval。

#### Cutover behavior

- Provider 切換由一個明確的 breaking AI Context release 完成。
- 該 release 移除 bundled source tools，不保留 framework-level legacy provider。
- Existing target 可完成 AI Context upgrade 但暫不安裝 Architecture Kit；此時必須明確回報 custom mechanical-validation gap，不能宣稱仍已驗證。
- Migration output 要求 responsible people 選擇現在安裝 package 或 deferred-with-continuation；不得靜默安裝、升級或重設 package/configuration。

### 建議交付項目

1. Versioned normalized rule schema 與 validator。
2. Core concept／rule／constraint／capability registry，以及 profile-owned rule 支援。
3. .NET Profile technology-binding schema，預留 Architecture Kit package range、Diagnostic mapping 與 binding evidence。
4. Compact target rule profile template 與 effective-projection contract。
5. `customizations.yaml` schema migration，使 semantic subjects 可引用適當 normalized identities。
6. Enforcement-tuning 與 tooling-waiver 的 target-owned record contracts。
7. Install／init／upgrade／reinstall reconciliation 與 pending continuation behavior。
8. Final CI consistency validator，預設 warning 並與 Analyzer 原生 build behavior 分離。
9. AI diagnostic-handling guidance與 action-skill reference routing。
10. Bundled-tools-to-Architecture-Kit cutover readiness checklist、breaking migration guide 與 downstream acceptance fixtures。

### 建議實作階段

1. **Additive schema stage**：新增 normalized identities、target profile 與 projections，不改變目前 bundled provider。
2. **Target lifecycle stage**：讓 init／upgrade／reinstall 能保存 effective state、semantic deltas、waivers 與 pending decisions。
3. **Bundled-provider mapping stage**：先用現有 `tools/**` 驗證一方向 mapping、Diagnostic handling 與 CI consistency contract。
4. **Architecture Kit readiness stage**：在獨立 repository 完成 NuGet、Diagnostic contract、parity 與 consumer proof；AI Context 仍不提供 preview provider。
5. **Breaking cutover release**：核准 gate 後一次移除 bundled tools、加入正式 .NET Profile binding 與 migration behavior。

### Acceptance criteria

- [ ] Core schema 能分別驗證 concept、rule、constraint、abstract enforcement capability 與 technology binding identity/reference integrity。
- [ ] Profile-owned rule 可以存在，且不需要虛構 universal concept。
- [ ] AI routine projection 只載入 task-relevant semantics；token／context 成本不因 canonical normalization 而無條件增加。
- [ ] .NET concrete constraints 在 code generation 前可被 action skill 取得，不需要等 Analyzer 報錯後才發現。
- [ ] Target rule profile 保存完整 effective state，`customizations.yaml` 只保存 semantic deltas。
- [ ] Semantic deviation、enforcement tuning 與 tooling waiver 有不同、可驗證的 evidence contract。
- [ ] `.editorconfig` 保持 target-owned native configuration；framework 不在每次 edit 自動啟動 semantic review。
- [ ] Final CI consistency check 預設為 non-blocking warning，且不把 Analyzer severity 或 target warnings-as-errors 誤認為 framework governance severity。
- [ ] .NET Profile 的 Architecture Kit compatibility 與 Diagnostic mapping 是單向關係；Architecture Kit 不依賴 AI Context schema。
- [ ] AI Context／Architecture Kit 可獨立版本化，並有 package/profile upgrade compatibility fixtures。
- [ ] 未安裝 Architecture Kit 時不宣稱其 Diagnostics 可用；deferred decision 有明確 continuation checkpoint。
- [ ] Cutover 前只支援 bundled provider；cutover release 不 routine dual-run 或保留 legacy provider。
- [ ] Existing target deferred package adoption 時，upgrade 可完成但明確回報 mechanical-validation gap。
- [ ] Cross-language fixture 證明 universal intent 不會強迫其他語言採用 .NET `Async` suffix 或 Roslyn configuration。
- [ ] External skill 不得繞過 target policy、approval、test、review 或 completion gates。
- [ ] Migration、rollback boundary、downstream validation 與 owner approval checkpoints 都有 retained evidence。

### 範圍外

- 在本 issue 內實作或發布 Architecture Kit NuGet。
- 立即移除目前 `tools/**`。
- 提供 Architecture Kit preview 或 routine dual-provider execution。
- 要求 Architecture Kit 解析或引用 AI Context IDs。
- 讓所有語言採用 .NET Analyzer、`.editorconfig` 或 naming conventions。
- 以 generic shell／grep checks 取代可信的 language-native validation。
- 重新設計 sub-agent runtime routing；該議題獨立追蹤。
- 重構任一 downstream product codebase。
- 將 framework rename 為 AI Collaboration Framework；命名遷移另案處理。

### Related work

本提案應作為這次討論結果的單一完整載體。相關 issue 只保存完成狀態、責任邊界與反向連結，不複製整份規則架構，避免同一結論在多個 issue 形成可漂移的副本。

- #61 — standards simplification deliberation：本提案是其中一輪 bounded discussion 的具體候選成果。建立本提案並取得 issue 編號後，應在 `STD-001` 的 canonical backlog 紀錄中標示該輪討論已完成、結果已正規化到本提案、仍待 owner 審查，之後再同步 GitHub 歷史投影；不得只修改 GitHub issue 而讓它與 canonical backlog 分歧。
- #75 — source-framework aggregate gate 與 downstream validation profile 分離：建立本提案後只需增加雙向 Related Work 連結，並明確保留「本提案定義驗證什麼，#75 定義 validation profile 在何時與何處執行」的責任邊界；本提案不重做 `check-all` composition。
- #43 — existing AI-agent repository compatibility intake：建立本提案後可在其 canonical backlog 紀錄增加 Related Work 連結，指出 target rule profile、customization reconciliation 與 pending package decision 可能成為 init compatibility 的輸入；在本提案尚未核准前，不修改 #43 的 acceptance criteria，也不讓 #43 取代本提案的 rule semantics。
- #58 — completed sub-agent runtime adapter promotion：不重開，也不加入本提案的實作範圍。未來獨立的 sub-agent reachability issue 應引用 #58 作為已完成的前置契約，並只處理 owning-skill reachability 與 downstream adapter installation drift。

建議同步順序：先建立本提案取得 `#NN`，再更新 #61 的 canonical deliberation evidence，最後為 #75 與 #43 增加精簡的 reciprocal links；sub-agent 後續議題另案處理。這些關聯更新不代表本提案已成為 canonical standard，也不授權 implementation、Architecture Kit publication 或 provider cutover。

### Submission check

- [x] 未包含秘密、private credentials 或 private session content。
- [x] 尚未授權 canonical implementation、NuGet publication、GitHub issue creation、push 或 merge。
