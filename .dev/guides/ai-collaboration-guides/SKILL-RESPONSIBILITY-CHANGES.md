# Skill 增減與職責變遷

這份盤點回答「哪些 skill 新增、移除、改名，以及同名職責是否改變」。
2026-10-01 的修復由 [#421](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/421)
與 [本次 workflow](../../workflows/2026-10-01-orchestrator-restore/workflow.yaml) 追蹤。
來源存在、catalog 可選、runtime 已安裝與產品行為驗收是不同狀態。
本次分支的修復不改寫已發布 RC3，也不宣稱已整合 main；實際安裝結果見
[結果紀錄](../../workflows/2026-10-01-orchestrator-restore/results.md)。

## 固定比較基準與數量

| 階段 | 固定 Git subject | Source／catalog | 來源專案 runtime |
| --- | --- | --- | --- |
| 重構前，2026-09-22 | `c2e7071335d02d9b8d40ab4dcaf437e690791741` | 16 個 canonical skills；其中 release-closeout 不發布，所以 portable 是 15 個 | 舊 16 個 |
| RC1，2026-09-23 | `3755b217421a4f1238f740a09de7e034ccf56038` | 新 `src/skills` 有 18 個 packages | 當時尚未採用，仍為舊 16 個 |
| RC2 實際採用，2026-09-29 | `03ffb961d397955c61a6a0b253aa640de99f9f49` | 18 個 | core／Codex／Claude 各 18 個 |
| RC3 退休前 | `973c477bca6ed6fb33c5c6d9d997c5b9ebaa1baa` | 18 個 | 各 18 個 |
| 本次修復前 RC3 | `a2ed2e3ebbba2acaae2f9574b52302379e01fc48` | 17 個 | 各 17 個 |
| 本次修復來源 | 本文件所在的修復分支；精確 commit 與安裝結果見結果紀錄 | 18 個，恢復 orchestrator | 由 installer 結果分開確認 |

計算為 **舊 16 − 退休 3 + 新增 5 = RC2 18；RC3 再移除 1 = 17；本次恢復 1 = 18**。
若只算 portable，起點是 15，退休 portable 2，再新增 5，同樣得到 18。
RC1 同時存在新舊來源目錄，不可相加成 34 個 skills。RC1→RC2 沒有 ID 增減，
主要是安裝採用與知識消費契約改變。`engineering-common`、`dotnet-backend`
是 knowledge packages，不列入 skill 數量；來源專案未選知識，不代表 mq lab 也未選。

## 完整對照

| Skill／歷史名稱 | 增減／命名 | 重構後職責與重要變化 |
| --- | --- | --- |
| `software-development-orchestrator` | 同名契約改變 → RC3 移除 → 本次恢復 | 舊版是高階意圖、階段排序、專業 skill 路由、核准、測試、審查、交接與收尾。RC1/RC2 同名套件主要變成 workflow record tools。本次 `0.2.0` 恢復開發編排，以 instruction operations `orchestrate`／`resume` 執行；紀錄由專案擁有。 |
| `ai-context-init` | RC2 runtime 退休；RC3 清理舊來源 | 舊職責包括 repo inventory、architecture docs、project-config、target provenance/customization 初始化。新 installer 管理 installed components，沒有證明完整承接上述 repo 初始化。舊發布格式目前沒有可用 portable/executable route。 |
| `ai-context-upgrader` | RC2 runtime 退休；RC3 清理舊來源 | 舊職責包括已發布格式三方比較、customization、升級路徑、multi-hop transaction 與 recovery。新 maintenance/reinstall 不等於舊格式升級。保留 source duty，但目前無已驗證執行路由。 |
| `ai-context-release-closeout` | RC2 source runtime 退休；RC3 清理舊來源 | 原本就 source-only、never packaged，處理歷史 post-tag read-back 與例外 records-only recovery。責任留在來源 `releases/` 和 release policy；沒有 portable installed successor。 |
| `ai-context-auditor` | 同 ID；package 責任收斂 | 保留唯讀 audit／compare；預設 prose，匯出或專案格式由 caller 選擇及既有 owner 管理。舊 mandatory independent baseline／repository pass、ASM persistence/lifecycle 不由此 portable package 自動供應；普通 audit 不代表獨立審查。 |
| `ai-context-governance` | 同 ID；責任拆分 | bounded project-owned context `propose`／`apply`，保留 semantic authority/custom content。Managed core、lock、projection、安裝、catalog、release/CI、migration/legacy finalization 留給各自 owner，不補回 init/upgrader。 |
| `problem-frame-author` | 同 ID；格式契約變更 | portable semantic drafting/review，另有新的 `problem-frame.cbf@1.0.0` snapshot 操作。舊 unversioned CBF YAML／SWF machine format 不支援，保留 bytes/IDs，不會自動轉換或接續。 |
| `spec-compliance-validator` | 同 ID；驗證責任重新界定 | 固定範圍的 `plan-validation`／`review-semantics`／`assess-runtime`，區分 structure、semantics、runtime；.NET 是明確選用 profile。舊 target-selected .NET CBF/SWF 100% gate 的 retained duties 不能以 generic compliance 取代。 |
| `requirement-author` | 核心保留；獨立 package 化 | stakeholder intent/business rules、draft/normalize、assumptions、source authority 和 observable acceptance；使用 caller/project template/destination，不強制來源 `.dev` 路徑或全階段 pipeline。 |
| `spec-author` | 核心保留；獨立 package 化 | production/entity/adapter/formal-test spec draft/normalize，保留 artifact-type ownership；prose templates 不等於 machine schema 或已執行驗證。 |
| `diagnostic-analyst` | 核心保留；portable instruction 化 | falsification、reproduction、causal isolation 和 repair proposal；不內建可執行測試/store，診斷不授予修復權限。 |
| `bdd-gwt-test-designer` | 核心保留；技術資源分離 | GWT 情境設計／唯讀 review；不實作、不執行 tests。RC2 增加 optional selected knowledge binding，並不自動採用 runner/tooling。 |
| `ddd-ca-hex-architect` | 核心保留；技術資源分離 | architecture design/review、domain/invariants/dependency/ports；RC2 optional knowledge；ADR/spec/implementation 是按實際需要的 handoff。 |
| `code-reviewer` | 核心保留；專業覆蓋分離 | bounded read-only review；package 不內建 .NET specialist checks。RC2 optional knowledge，不可把 common review 算成 target-required specialist gate 已完成。 |
| `local-change-implementer` | 核心保留；技術資源分離 | 一個 technical target/operation、explicit semantic radius、direct call sites 和 immediate tests；RC2 optional knowledge。跨數個直接 call-site 檔案仍可屬 local work。 |
| `slice-implementer` | 核心保留；技術資源分離 | 一個 authorized command/query/reactor/generic slice；其內部 edits/tests 留在 slice owner，另有 remediation 指引；RC2 optional knowledge，不要求 technology role registry。 |
| `adr` → `adr-author` | RC1 新增；RC3 改名 | alternatives、mapped owner decision 與 history。舊 `.dev/adr` 是文件治理，非原本同名 skill。RC3 保留 record family/schema/IDs/filenames/locks，調整 package/config/tool namespace；decision 不等於 implementation。 |
| `lesson` → `lesson-author` | RC1 新增；RC3 改名 | evidence-qualified observations、mapped owner acceptance 和 lifecycle history。舊 source lessons 是手動專案文件。v1 records 唯讀，derive 才建立新 v2 identity；accepted lesson 不等於 adopted rule。 |
| `pr` → `pr-author` | RC1 新增；RC3 改名 | content-bound actual Git PR preparation 與另外授權的 GitHub read/create/update。保留 record identities/schema/filenames/locks；不授予 merge、Issue/Project mutation、release/publication。 |
| `local-backlog` | RC1 新增 | local-file work items、acceptance、conflict-aware state；GitHub links 只作引用，不做 remote sync，不擁有 remote tracker authority。 |
| `standards-promotion` | RC1 新增 | evidence-bound rule proposal，另行觀察 owner adoption、實際 rule bytes 和 effect。沒有 apply operation；不直接改規則或自行產生採納證據。 |

在這五個新 standalone skills 中，ADR、Lesson 和 PR 的紀錄能力有既有需求與文件前身；
「新增 skill」不等於所有能力從零發明。三個 author 改名是零淨增減，也不是三個新功能。

## Orchestrator 修復範圍

[`software-development-orchestrator@0.2.0`](../../../src/skills/software-development-orchestrator/SKILL.md)
恢復的是 development lifecycle coordination：依目標選階段、解析已安裝能力、
直接套用或實際委派 specialist、保留核准、驗證結果、交接與 closeout。
小型單階段修改仍交給其 owner；不把所有工作變成固定 requirements→release pipeline。
User/project 明確選擇優先，不重複要求已有的核准。

它不恢復 RC2 的十個 workflow record tool operations、JSON store、writer lock、
retention tooling 或紀錄 migration。`configuration: null`，沒有 scripts/schema/store
相依。專案選擇既有 workflow 格式與 writer；新 skill 不覆寫 target authority。
因此「恢復編排」和「恢復／設計儲存工具」是分開的責任與驗收。

舊職責在
[legacy routing](https://github.com/YuChia-Wei/ai-collaboration-framework/blob/5a802e58a1473aae8cd139fcffd45a35587cb26b/.ai/assets/skills/software-development-orchestrator/references/routing-playbook.md#L16-L48)
與
[stage coordination](https://github.com/YuChia-Wei/ai-collaboration-framework/blob/5a802e58a1473aae8cd139fcffd45a35587cb26b/.ai/assets/skills/software-development-orchestrator/references/routing-playbook.md#L111-L134)。
RC2 record-only 契約在
[operations](https://github.com/YuChia-Wei/ai-collaboration-framework/blob/973c477bca6ed6fb33c5c6d9d997c5b9ebaa1baa/src/skills/software-development-orchestrator/references/operations.md)。
RC3 retirement 與 author renames 是
[`ac5e34e`](https://github.com/YuChia-Wei/ai-collaboration-framework/commit/ac5e34e397ca38b2efa1581fed34ca5c4fb23baa)；
legacy 資源另外於 `526150aa6e966a8924bce07b2a9c89a71b7370f4` 清理。
這兩項清理沒有留下完整 portable 開發編排入口；本次追加修復，不改寫舊紀錄。

## 已在更早版本退休的名字

`repo-structure-sync` 與 `dev-workflow` 在 v0.16.0 就已退休，不能算作 RC3 新刪除。
[固定 transition](https://github.com/YuChia-Wei/ai-collaboration-framework/blob/c2e7071335d02d9b8d40ab4dcaf437e690791741/.ai/assets/skills/transitions/v0.16.0.yaml)
分別指定 `ai-context-init` 與 `software-development-orchestrator` 作後續路由。
init 現在沒有可用路由，不代表可復活 retired alias；恢復 orchestrator 也不需要恢復 `dev-workflow` 別名。

## 查核與使用限制

盤點方法是固定 Git registry/skill metadata/entry 與 manifest/profiles 對照，
必要時只讀直接引用的 responsibility contracts。以 `git show <SHA>:<path>`
可重現；新來源以 manifest 中 `kind: skill` 的 component IDs 計數。
Legacy 使用 `.ai/assets/skills/README.MD:25-42`，不能把 retired transition entries
或 source-only release-closeout 算成 portable package。Actual RC2 runtime cutover
見固定 `03ffb961` 的 `.agents/skills/README.md`；新 catalog 存在本身不證明安裝。

五個工程 skills 在 RC2 將 metadata 3→4、package 0.1.0→0.2.0，加入 optional
`knowledge_consumption`：BDD、architect、reviewer、local implementer、slice implementer。
本表依 current package scope 記錄責任，並不驗收每個 runtime 行為。
其他 skill 被保留的檔案或 source duty，不代表對應工具已可用。

本次 readability/metadata/link/diff 與 installer read-back 依 results 逐項列示。
Legacy/full/native/hosted、獨立 release admission 仍為 U001 的
`deferred-by-owner`（#322 coordinator/P7），不是 passed。Skill 加回 catalog、安裝
成功、commit、main 整合、release 和 target rule adoption 仍分開報告。
