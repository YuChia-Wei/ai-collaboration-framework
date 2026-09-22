# 證據、來源與限制

基線 commit：`c2e7071335d02d9b8d40ab4dcaf437e690791741`；初始 branch `main`、worktree clean。remote URL 為 `https://github.com/YuChia-Wei/ai-collaboration-framework.git`。分析寫入 branch：`codex/assessment/asm-20260923-00-6oq`。

本次採 bounded tracked-file inventory、設定／文件／scripts 的靜態讀取、GitHub connector Issue read-back、外部 primary-source 閱讀。未做程式函式／呼叫圖的全面分析；沒有使用 code graph 的缺席結果判斷功能不存在。未呼叫 repo 現有 SKILL；少數 skill metadata／模板／registry 作為被評估的產品資料，不作為本次執行規範。

先前記憶僅提供 RAM-disk 分類與所有權的查找線索；以下 repo 結論已用當前 tracked evidence 重新查閱，沒有把舊 Issue 狀態或效能觀察當成現況。

<a id="repo-evidence"></a>
## Repo 證據

下列行號綁定上述 commit，不是未來搬移後的行號；非 Markdown 檔案的連結也只供定位，不要求自動執行。

| ID | 來源與行號 | 可以支持的結論 | 不能據此推論 |
| --- | --- | --- | --- |
| E01 | [distribution profile](../../../.ai/distribution/profiles/dotnet-backend.yaml) 18–43；[skill registry](../../../.ai/assets/skills/README.MD) 11–16 | 現有元件選取較粗；lifecycle core 為 mandatory；有 skill-private/global automation 分工 | 每個 skill 的實際 dependency closure 已完整追蹤 |
| E02 | 同 profile 223–335；[portable-policy-manifest](../../../.ai/assets/shared/governance/portable-policy-manifest.yaml) 3–11 | 下游 package 選入 `.dev` 的標準、guide、scaffold；不能只移 source 路徑便認為所有權混合已解決 | 全部 `.dev` 都是 framework-managed |
| E03 | [distribution README](../../../.ai/distribution/README.md) 88–100；[boundary](../../../.dev/standards/AI-CONTEXT-BOUNDARY.md) 9–17 | 已有 framework-managed、target-template、target-owned 語意，但物理目錄仍混合 | 現有 ownership 語意完全不可用 |
| E04 | [workflow policy](../../../.dev/standards/WORKFLOW-ARTIFACT-POLICY.md) 3–18、65–74 | skill 已擁有部分 workflow 規格；固定 locator、Git-trackable root，禁止 ignored/external | workflow 現在完全不支援任何替代 artifact root |
| E05 | [product source contract](../../../.ai/assets/shared/PRODUCT-SOURCE-PROJECTION-CONTRACT.md) 14–32、48–52；[ADR-001](../../../.dev/adr/ADR-001-separate-source-config-from-downstream-templates.md) 13–21、39–47 | source/projection/target 已區別，未來 canonical root 有概念基礎；source 與 downstream config 分離有既有原因 | `src` 搬移本身已實作或已採納 |
| E06 | [project-config template](../../../.ai/assets/skills/ai-context-init/templates/project-config.template.yaml) 1–77；[migration schema](../../../.ai/distribution/schemas/migration.schema.yaml) 30–33、49–94 | 該設定模板沒有一般 artifact roots/retention；migration 已有檔案操作與 ownership/hash preconditions | 全 repo 沒有任何其他位置設定；檔案 migration 等於所有 record schema migration |
| E07 | [Lesson lifecycle](../../../.dev/lessons/README.MD) 25–42、84–104；[ADR boundary](../../../.dev/adr/README.md) 3–18；[ADR creation](../../../.dev/adr/WHEN-TO-CREATE-ADR.MD) 3–40 | Lesson 非規範，已能 promotion；ADR 與有效 standard 分工已有基礎 | 本次已採納任何新 ADR／Lesson skill |
| E08 | [artifact lifecycle registry](../../../.ai/assets/shared/artifact-lifecycle-registry.json) 2–60、1105–1155、1745–1767、1895–1915、2332–2377 | 95 artifact kinds 對應 33 explicit schemas + 19 implicit contracts；只有明列 conversion edges | registry 宣告即代表所有工具 runtime 能力經本次驗證 |
| E09 | [validation registry](../../../.ai/scripts/validation-profile-registry.sh) 8–11、132–161、273–277 | fast/PR budget 為 warn/report；fast 含 multi-hop，package checks 有高 timeout／相依 | timeout 是實際耗時，或每次都跑全部 85 checks |
| E10 | [fixture classifications](../../../.ai/scripts/test-fixture-classifications.json) 3–32；[fixture guide](../../../.dev/guides/implementation-guides/PORTABLE-TEST-FIXTURE-ACCELERATION-GUIDE.md) 7–23、75 | RAM-disk opt-in 只有部分 suites；real-storage 語意與 disposable I/O 分開；有 containment 和唯一子目錄 | 已經量測 SSD 寫入或證明所有 temporary fixtures 可搬 RAM disk |
| E11 | [package-candidate CI](../../../.github/workflows/package-candidate.yml) 130–161、185–214；[v015 lanes](../../../.ai/distribution/validation/v015-package-validation-lanes.yaml) 6–9、30–48 | 有特定歷史版本、舊包下載與 published-upgrade 路線 | 每次 release 或每次 task 都執行所有歷史 lanes |
| E12 | [nightly readiness](../../../.github/workflows/nightly-full-readiness.yml) 18–21；[immutable-history policy](../../../.ai/distribution/validation/immutable-history-validation.yaml) 8–29、56–90 | nightly job hard-disabled；history 檢查有 routine/full，source history receipt 不下放 | nightly 現在每天耗費完整矩陣成本 |
| E13 | [historical backlog](../../../.dev/backlog/README.MD) 3–30 | `.dev/backlog` 為歷史凍結；本 repo 工作來源已轉線上 | 下游也不得採 local backlog |
| E14 | [assessment policy](../../../.dev/standards/ASSESSMENT-ARTIFACT-POLICY.md) 與 [locator template](../templates/assessment-locator-template.yaml) | 可借用 ID、locator、report、index 的保存 pattern | 本次有使用 owning skill 或通過其完整 schema／validator |

### 靜態 registry 摘要

| 盤點 | 結果 | 限定 |
| --- | --- | --- |
| Registered validation checks | 85 | 靜態 registry 條目 |
| `fast` membership | 56，其中 8 個 `io` | 不是單次實際執行數 |
| `pr` membership | 64 | 與 fast 可能重疊，不相加成不同 checks |
| `io` checks 全部 | 12 | 分類標籤，不代表已量測 I/O |
| fast / PR budget | 30 / 90 秒 | report-and-warn，不是實測 |
| multi-hop upgrade timeout | 360 秒 | 包含 fast，`io`、`no-reuse` |
| package-apply timeout | 600 秒 | PR membership |
| package-smoke timeout | 120 秒 | 有 package-apply 依賴 |
| full package matrix timeout | 900 秒 | release/nightly membership；不是 routine default |
| 可使用 fixture root 的 suites | 3 | release-state、version-governance、release-notes-renderer |
| package-apply / packaging | 前者 durability/platform 排除；後者 unclassified | 不自行宣告兩者已支援 RAM disk |
| Artifact authoring dispositions | executable 61、semantic-owner 20、manual-gap 9、external 4、creation-template 1 | 共 95；這是 registry claims |
| Artifact migration dispositions | convert 3、unsupported 32、regenerate 16、preserve 14、re-execute 13、owner-recovery 9、owner-reconciliation 8 | 共 95；不能把 preserve/re-execute 算成 schema conversion |

這些數字足以找出縮减切入點，不足以估算 token savings、SSD 壽命或改善百分比。沒有在此時新增 benchmark 工作作為分析前置。

<a id="issue-snapshot"></a>
## Live Issue 快照

透過 GitHub connector 讀取 exact issue，而非只依搜尋摘要判斷 state。查閱日為 2026-09-23（Asia/Taipei）。

| Issue | state／reason | provider updated_at (UTC) | 本次用途 |
| --- | --- | --- | --- |
| [#319](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/319) | closed / completed | 2026-09-22T05:51:30Z | 確认 registry／lifecycle 工作範圍與已完成狀態 |
| [#320](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/320) | closed / completed | 2026-09-22T12:24:51Z | 使用者指定的 schema authoring 方向；不當成新待做 Issue |
| [#149](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/149) | open | 2026-08-09T09:21:39Z | CLI runtime 與 validator 策略尚待工作 |
| [#168](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/168) | open | 2026-08-09T09:21:58Z | installable CLI preview 的既有規劃 |
| [#274](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/274) | open | 2026-08-30T15:51:09Z | fixture I/O classification |
| [#275](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/275) | open | 2026-08-30T15:51:10Z | durability/logical costs |

只查閱與本分析直接相關的 Issues。沒有全量 backlog 搜尋、Project read-back、遠端 branch 最新性比較、release read-back 或任何 provider mutation。Issue 狀態不等於本次已獨立驗證其全部實作。

<a id="external-sources"></a>
## 外部 primary sources

研究時 GitHub history 顯示 Matt Pocock repo 的 commit [`3cca18b368ae95cdbdebbff572ccafa662551015`](https://github.com/mattpocock/skills/commit/3cca18b368ae95cdbdebbff572ccafa662551015)。這是網頁取得的研究快照；一次 `git ls-remote` 因本機 proxy 連線失敗，未獨立確認當時 remote HEAD。下表標明固定 snapshot 與 live `main`，避免將兩者混為一個已完整 checkout 的版本。

| 來源 | 本次觀察 | 對本提案的推論 |
| --- | --- | --- |
| [固定版 README](https://raw.githubusercontent.com/mattpocock/skills/3cca18b368ae95cdbdebbff572ccafa662551015/README.md)；[固定版 CLAUDE](https://raw.githubusercontent.com/mattpocock/skills/3cca18b368ae95cdbdebbff572ccafa662551015/CLAUDE.md) | 技能產品、維護資料與說明區分；安裝包含 managed 與可修改副本模式 | 明確產品 ownership；兩種更新契約不能混用 |
| [固定版 invocation](https://raw.githubusercontent.com/mattpocock/skills/3cca18b368ae95cdbdebbff572ccafa662551015/.agents/invocation.md) | 有組織型／能力型區分及 named skill 呼叫、owning references | 可以借鏡明確相依，不能假定各 runtime 都有相同 Skill tool |
| [setup（live main）](https://raw.githubusercontent.com/mattpocock/skills/main/skills/engineering/setup-matt-pocock-skills/SKILL.md)；[domain（live main）](https://raw.githubusercontent.com/mattpocock/skills/main/skills/engineering/setup-matt-pocock-skills/domain.md) | 專案持有 tracker/domain 資料與相關讀取指引 | 支持專案設定思想；不證明已存在一般化 schema resolver |
| [package（live main）](https://raw.githubusercontent.com/mattpocock/skills/main/package.json)；[sync version（live main）](https://raw.githubusercontent.com/mattpocock/skills/main/scripts/sync-plugin-version.mjs)；[固定版 release workflow](https://raw.githubusercontent.com/mattpocock/skills/3cca18b368ae95cdbdebbff572ccafa662551015/.github/workflows/release.yml) | 以小工具處理版本同步與發布機械工作 | 可優先工具化明確重複工作；不推論全 repo 無測試 |
| [dev linking（live main）](https://raw.githubusercontent.com/mattpocock/skills/main/scripts/link-skills.sh)；[plugin ADR（live main）](https://raw.githubusercontent.com/mattpocock/skills/main/.agents/adr/0002-ship-as-a-claude-code-plugin.md) | development 與支持的 installer 分開；紀錄過 packaging/platform 選擇與限制 | source layout 與 runtime projection 分離；不直接照搬刪目錄／symlink 方法 |
| [retro（live main）](https://raw.githubusercontent.com/mattpocock/skills/main/skills/in-progress/retro/SKILL.md) | in-progress retrospective 提出工具／規範改善候選 | 可參考回顧入口；不等於完整採納、保留與清理生命週期 |
| [Agent Skills specification](https://agentskills.io/specification) | 定義技能封裝及 optional scripts/references/assets、compatibility／metadata | 可用標準封裝；本提案的 dependency、storage、migration 是 framework 擴充，不是現成標準保證 |

外部 SKILL.md 是被研究的案例，沒有在本次 session 執行它的工作流程。未安裝外部技能、plugin、套件或執行外部腳本。外部專案當時的 packaging 決策不代表目前所有 runtime 的限制。

## 檢查與尚未驗證事項

本次檢查僅針對分析成品：需求 18 項對照、文件關聯、ID／基線／分支一致性、Markdown 本地連結存在性、locator 語法、Git diff whitespace，以及協作代理對架構的有界編輯檢視。編輯檢視不是 immutable subject 的正式獨立 audit。

實際結果：locator 以 PyYAML 解析成功；ID／branch／subject binding 一致；18 項需求列、11 個 Wxx 工作包、39 個本地連結與 code fences 檢查通過；索引 diff 僅新增一列，`git diff --check` 無輸出。新檔另外檢查 whitespace。沒有將這些文件檢查稱為 framework 行為驗證。

編輯檢視的五項建議均已納入：core 與資料版本一起恢復；避免誤稱現況支援任意歷史升級；限定第一個垂直 slice；保留 custom extensions／拒絕有損改寫；一般可丟棄 workflow 不強制新建 evidence packet。檢視時文件仍在編輯，因此只作分析品質回饋。

沒有使用既有 assessment validator 宣稱合規：`owner_skill: null`、自訂報告與使用者例外都已明示，這是受授權的 assessment pattern 變體。沒有跑現有 framework tests 或 package build；它們不能驗證一份未實作的架構提案。

未確認項目：完整 skill dependency closure、各平台最新 API／plugin 限制、替代 artifact store 的端到端行為、實際 token／SSD 寫入成本、所有歷史支援承諾的退役影響。後續只為被選中的工作包補必要證據，不先全面掃描或建立矩陣。
