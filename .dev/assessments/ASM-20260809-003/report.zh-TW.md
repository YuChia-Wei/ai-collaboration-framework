# .ai 產品來源、所有權與可攜性盤點

## Metadata

- `assessment_id`: `ASM-20260809-003`
- `assessment_type`: `ai-context-audit`
- `owner_skill`: `ai-context-auditor`
- `status`: `final`
- `audit_date`: `2026-08-09`
- `created_at`: `2026-08-09T22:06:38+08:00`
- `updated_at`: `2026-08-09T22:06:38+08:00`
- `template_source`: `.ai/assets/skills/ai-context-auditor/templates/ai-context-audit-report-template.md`
- `template_version`: `2.1.0`
- `repository`: `YuChia-Wei/ai-collaboration-framework`
- `subject_branch`: `main`
- `subject_commit`: `3a60570d0e290f337f2a212d092c6797670528b4`
- `issue_ref`: `#170`
- `related_assessments`: `ASM-20260809-001`, `ASM-20260809-002`
- `translation_status`: `derived-human-review`
- `canonical_source`: `.dev/assessments/ASM-20260809-003/report.md`
- `derived_from`: `.dev/assessments/ASM-20260809-003/report.md`
- `translation_created_at`: `2026-08-10T00:13:54+08:00`
- `translation_updated_at`: `2026-08-10T00:13:54+08:00`
- `translation_role`: `context-translator`

英文報告是 canonical source；本檔案是供人工審查的衍生翻譯。

## 執行摘要

- 整體評估：目前的 `.ai` 產品／來源邊界明確且內部一致。所有 595 個要求盤點的 `.ai` 與 adapter blobs 均已分類；其中 522 個是有效的套件來源，73 個符合具名的僅限來源排除項目。
- 產品結論：可攜式 canonical assets、選定的 runtime scripts/tests，以及精簡的 runtime wrappers/adapters 是 framework product。Distribution build controls、local evaluation、release/provider operations、release-closeout 與 generic Codex worker profiles 僅屬於 source governance。
- 投影結論：目前的 source contract 將 643 個唯一 repository sources 解析為 659 個 target paths，包含 16 個刻意的 projections，沒有 collisions，payload digest 為 `9d559d...`。
- 決策：`handoff-required`，而非廣泛 remediation。#166 負責 product/package/profile/alias identity；#172 負責 archive read-back，以及任何 disposition-schema 決策。
- 主要耦合：已封裝的 v0.6.0 skill-transition manifest 在可攜式相容性 alias map 旁保留 source activation evidence，以及對排除 `.ai/evaluation/**` 路徑的具體 references。

## 範圍

### 納入的 AI Context 表面

- `.ai/assets/skills/**`、`sub-agent-role-prompts/**`、`shared/**`、`tech-stacks/**`，以及 templates/schema entries。
- `.ai/distribution/**`、`.ai/scripts/**`、`.ai/evaluation/**`，以及 `.ai` entry/index documents。
- `.agents/**`、`.claude/**` 與 `.codex/**` 的 projection/adapter relationships。
- 目前針對 #166 與 #172 的 profile resolution 與 identity/package inputs。

### 預設排除項目

- `src/**` 與 product implementation trees。
- 明確納入的 `.ai/scripts/tests/**` AI-context surface 以外的 product tests。

### 其他排除項目

- Material moves、deletions、semantic changes、package-byte changes、CLI runtime selection，以及 full archive read-back。
- Existing tag、Release、asset、historical evidence，或 downstream target-owned truth mutation。

### Code Review 交接

- Requested：`no`。
- Recommended skill：`not-applicable`；未來的 boundary remediation 應在專用 Issue 之後交由 `ai-context-governance`。

## 方法與證據

### Pass A：獨立基線

- 統計 pinned Git blobs 與 bytes，而非 checkout bytes。
- 分類 canonical assets、runtime scripts/tests、source controls、evaluation evidence、wrappers、aliases 與 runtime adapters。
- 驗證每個排除的 scoped path 恰好符合一個具名 profile exclusion。

### Pass B：具 repository 感知的 Skill Review

- 套用 `PRODUCT-SOURCE-001`、distribution profile/schema、AI-context boundary/ownership rules、wrapper metadata、role execution contract 與 source-governance validation。
- 使用 repository package code 解析目前 payload：659 個 target paths / 2,889,104 bytes、643 個 unique source paths、16 個 intentional projections、零 target collisions，且沒有 payload reference-integrity error。

### 委派

- 使用的 Sub-agents：`yes`。
- `.ai` content/ownership inventory：`ai-context-auditor` 下的 bounded general worker，read-only，沒有 nested delegation。
- Package/projection cross-check：`ai-context-auditor` 下的 bounded routine worker，read-only，沒有 nested delegation。
- Main-agent reconciliation：從 Git blobs 驗證 scope totals、確認 exclusion lists 與 wrapper parity，並獨立審查 transition/evaluation coupling。

### 探索加速器

| Tool / generated view | Source revision | Use | Unsupported relationships | File-backed fallback |
| --- | --- | --- | --- | --- |
| Codebase Memory MCP | current indexed repository | 定位 package 與 validation entrypoints | 無法證明完整 path coverage、package bytes 或 provider state | Git tree、profile resolver、direct files |
| Distribution resolver | `3a60570d...` | 精確的 source/target/exclusion/component mapping | 無法證明已發布的 v0.11.0 archive bytes | #172 archive read-back |

## Repository Context Inventory

| Surface | Tracked | Effective package source | Classification |
| :--- | ---: | ---: | --- |
| `.ai` entry documents | 4 / 20,320 bytes | 4 / 20,320 bytes | 可攜式產品入口 |
| `.ai/assets/**` | 408 / 1,328,710 bytes | 400 / 1,313,815 bytes | 可攜式 canonical product，含八個僅限來源例外 |
| `.ai/scripts/**` | 110 / 1,552,061 bytes | 79 / 1,068,329 bytes | 可攜式 runtime，加上明確的來源自動化／測試 |
| `.ai/distribution/**` | 11 / 45,137 bytes | 0 | 來源套件控制權威 |
| `.ai/evaluation/**` | 19 / 14,708 bytes | 0 | 來源評估證據 |
| `.agents/**` | 20 / 27,870 bytes | 19 / 26,947 bytes | 精簡的 Codex 相容 wrapper 投影 |
| `.claude/**` | 20 / 28,438 bytes | 19 / 27,517 bytes | 精簡的 Claude wrapper/adapter 投影 |
| `.codex/**` | 3 / 9,425 bytes | 1 / 770 bytes | 一個可攜式 role adapter；兩個僅限來源 worker profiles |

完整的機器可讀矩陣位於 [`evidence/ai-inventory.yaml`](evidence/ai-inventory.yaml)。

## Product 與 Source-Governance 邊界

### Framework Product

- 四個 `.ai` entry documents。
- 可攜式 shared assets、14 個 active packaged skills、兩個 deprecated compatibility aliases、18 個 canonical roles、`dotnet-backend` profile、可重用 templates，以及選定的 scripts/tests。
- 移除僅限來源的 closeout wrapper 後，每個 packaged runtime 有 16 個 Codex/Claude skill wrapper identities。
- `context-translator` runtime-native role adapters；adapters 仍是單一 canonical role 的 projections。

### Source Governance Only

- Distribution profile/schemas/build controls 與 Source Maintainer CLI contracts。
- Evaluation corpus、fixtures、baselines，以及 model-in-loop/source evidence。
- Package/release/provider/repository validators 及其 source-only tests。
- `ai-context-release-closeout` 及其 wrappers/guide。
- `bounded-general-worker` 與 `bounded-routine-worker`；它們是 runtime execution profiles，而不是 canonical roles。

### Generated Or Target-Owned Projections

- Package metadata、archives、files inventories 與 staging trees 都是 generated projections，絕不是第二個來源。
- 三份可攜式治理文件對應至 `.dev` target policies。
- 十三個 `ai-context-init` template sources 也會植入 target-owned root/catalog paths。

## 優勢

1. 所有 73 個 scoped non-product paths 均符合明確的 exclusions；沒有未分類的 `.ai`/adapter 遺漏。
2. 17 個 source canonical skills 在兩個 runtime roots 皆具 wrapper parity；product projection 刻意移除一個僅限來源 skill 並保留兩個 compatibility aliases。
3. 全部 18 個 canonical roles 都可攜式，但 generic runtime worker profiles 明確維持在 role taxonomy 與 package 之外。
4. 實際 resolver 找不到 target collision、component ambiguity、exclusion overlap 或 forbidden source-lifecycle reference。

## Findings

| ID | Severity | Finding | Evidence | Impact | Recommendation | Owner / Next Skill |
| --- | --- | --- | --- | --- | --- | --- |
| AIA-001 | MEDIUM | 已封裝的 `transitions/v0.6.0.yaml` 將目前的 compatibility alias map 與僅限來源的 activation/model evidence，以及對排除 `.ai/evaluation/**` 路徑的具體 references 結合在一起。 | `.ai/assets/skills/transitions/v0.6.0.yaml:7,33-73`；profile exclusion for `.ai/evaluation/**`。 | alias contract 可攜式，但其 evidence 無法從 package 重現，且仍與單一來源 release/history boundary 耦合。 | 保留 historical manifest。由 #166 選擇 versioned alias identity model；若需要 portable alias registry，開立 bounded governance Issue 以衍生它，但不要重寫 v0.6 evidence。 | #166，然後在選定時交由 `ai-context-governance`。 |
| AIA-002 | LOW | Canonical asset 的 `portability` 與 distribution inclusion 是不同的分類；`ai-context-release-closeout` 是有效的 `repo-portable` metadata，但在 distribution profile 中刻意僅限來源。 | `ai-context-release-closeout/skill.yaml:1-9`；profile lines 441-448；asset schema enum。 | 若人員或 generic inventory tools 未同時解析 profile，可能會將 `repo-portable` 誤讀為 downstream product inclusion。Package resolver 本身沒有歧義。 | 以 profile 作為目前 authority。由 #172 決定是否需要跨表面的 disposition field/registry；不要在本次 audit 中變更 metadata。 | #172 / `ai-context-governance`。 |

## Identity 與 Drift 交接給 #166

| Identity class | Current value | Disposition |
| --- | --- | --- |
| Repository | `YuChia-Wei/ai-collaboration-framework` | 目前的 operational coordinate；不是 product identity |
| Product description | AI collaboration context framework with retained .NET backend capability | #166 正式化 versioned product identity |
| Release model | `single-versioned-componentized-release` | 目前的 profile contract |
| Distribution profile | `dotnet-backend` | Technology profile，不是 repository name |
| Package/archive template | `ai-context-dotnet-backend-v{version}` | #166 owner decision；不要推斷 rename |
| Mandatory components | `software-development-core`、`ai-context-lifecycle-core` | 目前的 product contract |
| Optional components | `dotnet-backend`、`repo-backlog` | 保留明確的 selection/default rules |
| Deprecated aliases | `dev-workflow` → `software-development-orchestrator`；`repo-structure-sync` → `ai-context-init` | 保留至 #166／versioned compatibility decision 為止 |
| Source-only skill | `ai-context-release-closeout` | 依目前 contract 絕不作為 downstream product |
| CLI identities | Distribution CLI、Portable Validator Engine、Source Maintainer CLI | 分開的 Feature／runtime decisions |

## Package 交接給 #172

- 精確的 scoped sources：522 included、73 explicitly excluded。
- 整個目前的 contract：643 unique sources → 659 targets，digest `9d559dec5d36975305e53bb7ee71403a1e711f76e59a8bf1c63352f86edfd6c1`。
- 此 digest 是位於 `3a60570d...` 的 current-contract projection，不是已發布 v0.11.0 archive verdict。
- #172 必須將實際 ZIP/tar.gz members、modes、checksums、metadata 與 profile/archive identities 與 v0.11.0 artifacts 比對。

## Baseline 與 Skill 比較

### 已確認

- 兩次 pass 都發現要求的 `.ai` 與 adapter scope 具有完整且明確的 disposition。
- Wrapper 與 adapter parity 完整。
- Source release、provider、evaluation、package-control 與 generic worker surfaces 仍維持排除。

### 由 Repository-Aware Review 新增

- 實際的 profile resolution 建立了 643-to-659 projection 與目前的 payload digest。
- transition manifest 的 portable alias/source-evidence coupling 不是 target collision 或 reference-integrity failure，但它是 #166 的 semantic boundary。

### 已降級或延後

- 重複的 `ai-context-dotnet-backend` 值是單一 profile authority 的 consumers，不是重複的 product authorities。命名仍由 #166 決定。
- Archive-level regression 延後至 #172；focused/source-contract checks 不會被當作 archive verdict。

## Validation

| Check | Result | Evidence / Notes |
| --- | --- | --- |
| Git tree coverage | passed | 595 scoped blobs / 3,026,669 Git-blob bytes；entry sums exact。 |
| Distribution resolution | passed | 659 targets / 2,889,104 bytes；沒有 collisions 或 reference-integrity errors。 |
| AI context static validation | passed | 26 indexes、17 canonical skills、兩個 wrapper roots、35 manifests 與 governed identities。 |
| Wrapper metadata | passed / static and focused | 每個 runtime 有 17 個 source wrappers；exact canonical references。 |
| Source-governance registry | passed | 1,017 retired-name lines / 172 assignments / 9 rules。 |
| File-disposition manifest | passed | 目前已註冊的 historical disposition manifest 通過驗證。 |
| Archive-level package suite | blocked-by-environment / deferred | 一個 worker 遇到 Windows temp ACL errors；另一個長時間執行超過 180 秒。未宣稱任何 archive semantic verdict。 |

### Not Applicable

- `validate-ai-context-target.py`：此 source repository 刻意沒有 downstream `.dev/ai-context/provenance.yaml`。
- AI-context scope 以外的 product source/tests。

## 建議的行動順序

1. 交付此盤點，不移動或重寫 `.ai` 路徑。
2. 將精確的 identity 與 compatibility list 提供給 #166。
3. 將 source/target/exclusion counts 與 archive-level limitation 提供給 #172。
4. 只有在 #166/#172 作出決策後，若選定可攜式 alias registry 或明確的跨表面 disposition schema，才開立 bounded governance Issue。

## 延後項目

- #170 的優先順序：owner decision；建議為 `P1 High`。
- Product/package/archive/profile/alias naming：#166。
- Archive member/checksum/published-asset comparison：#172。
- Package bytes、CLI runtime、path moves、deletions 與 semantic rewrites：此處未授權。

## 附錄

### 執行的命令

```text
git fetch --prune origin
git ls-tree -r -l 3a60570d0e290f337f2a212d092c6797670528b4 -- .ai .agents .claude .codex
python .ai/scripts/validate-ai-context.py
python .ai/scripts/validate-source-governance.py
python .ai/scripts/validate-file-disposition-manifest.py --manifest <v0.5.0 disposition manifest>
python .ai/scripts/tests/test_profile_projection_contract.py -v
python .ai/scripts/tests/test_ai_context_wrapper_metadata.py -v
python .ai/scripts/tests/test_ai_context_sub_agent_adapters.py -v
python .ai/scripts/tests/test_ai_context_source_include_evidence.py -v
```

### 備註

- Counts 與 bytes 使用 pinned Git tree，而非 checkout encoding 或 local caches。
- Temp-writing 與 long package tests 會如實報告為 environment-limited/deferred。

## Lifecycle 交接

- Assessment path：`.dev/assessments/ASM-20260809-003/report.md`
- Machine inventory：`.dev/assessments/ASM-20260809-003/evidence/ai-inventory.yaml`
- Stable findings：`ASM-20260809-003#AIA-001`、`#AIA-002`
- Identity handoff：Issue #166
- Package handoff：Issue #172
- 本 skill 刻意未執行 remediation：`yes`
