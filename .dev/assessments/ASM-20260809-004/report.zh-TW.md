# .dev 治理內容與生命週期盤點

## 中繼資料

- `assessment_id`: `ASM-20260809-004`
- `assessment_type`: `ai-context-audit`
- `owner_skill`: `ai-context-auditor`
- `status`: `final`
- `audit_date`: `2026-08-09`
- `created_at`: `2026-08-09T22:06:38+08:00`
- `updated_at`: `2026-08-09T22:17:10+08:00`
- `template_source`: `.ai/assets/skills/ai-context-auditor/templates/ai-context-audit-report-template.md`
- `template_version`: `2.1.0`
- `repository`: `YuChia-Wei/ai-collaboration-framework`
- `subject_branch`: `main`
- `subject_commit`: `3a60570d0e290f337f2a212d092c6797670528b4`
- `issue_ref`: `#171`
- `related_assessments`: `ASM-20260809-001`, `ASM-20260809-002`
- `translation_status`: `derived-human-review`
- `canonical_source`: `.dev/assessments/ASM-20260809-004/report.md`
- `derived_from`: `.dev/assessments/ASM-20260809-004/report.md`
- `translation_created_at`: `2026-08-10T00:13:54+08:00`
- `translation_updated_at`: `2026-08-10T00:13:54+08:00`
- `translation_role`: `context-translator`

英文報告是 canonical，本檔案是供人工審閱的 derived human-review translation。

## 執行摘要

- 整體評估：`.dev` 具備一致的 ownership model，但目前 navigation 與 work-management projections 已落後於 immutable item/release evidence 與 live GitHub Project state。
- 盤點結果：1,011 個 tracked Git blobs / 5,810,865 bytes。current profile 選取 118 個 source files / 400,870 bytes，排除或省略 893 個，並在 portable mappings 後衍生 129 個 `.dev` target paths。
- 歷史結果：採用後的 68 個 workflow 均已 completed，39 項 assessments 中有 38 項為 final，且全部 14 筆 release records 已 published。這些是 source-only evidence，不是 target truth。
- 決策：`follow-up-required`。分別修復 current projections 與 active references，immutable history 保持不變；在各自 work items 中決定 validation-cadence 與 package-disposition schema。
- 主要風險：`ROADMAP.md`、backlog `INDEX.MD` 與 source GitHub provider contract 描述較舊的 release horizon，儘管 item records、release records 與 online Project 均已前進。

## 範圍

### 納入的 AI Context Surfaces

- 固定 source revision 中所有 Git-tracked `.dev/**` blobs。
- 標準、指南、作業文件、ADR、需求、規格、problem frames、domain language、workflows、assessments、releases、lessons、backlog、roadmap、indexes 與 lifecycle projections。
- 目前 distribution-profile 的 inclusion、exclusion、omission、mapping 與 ownership 行為。
- Issue #171 與 Project #3 的目前欄位；#166 的 identity inputs 與 #172 的 package inputs。

### 預設排除

- `src/**`、product implementation 與 product-test review。
- 明確納入範圍的 source governance records 之外的 generated/dependency/local state。

### 額外排除

- Bulk cleanup、historical rewrite、lifecycle-policy mutation 與 package-byte changes。
- 完整的 v0.11.0 archive 與 published-asset read-back，由 #172 負責。

### Code Review 交接

- 要求：`no`。
- 未掃描 product source 與 tests。
- 建議 skill：`not-applicable`；後續 remediation 屬於 `ai-context-governance`。

## 方法與證據

### Pass A：獨立基線

- 使用 pinned Git tree 計算 path 與 blob-size totals，接著按最上層 `.dev` group 對每個 path 分類。
- 直接讀取 current locators、item/release records、roadmap/index projections、provider contract 與 active document references。
- 在 sandbox 外 read back Project #3：#171 為 `In progress`，target 為 `v0.12.0`，狀態為 `Not yet published`，且沒有 owner-selected Priority 或 Owner review value。

### Pass B：Repository-Aware Skill Review

- 套用 `AI-CONTEXT-BOUNDARY`、`AI-CONTEXT-OWNERSHIP`、assessment/workflow artifact policy、product-source projection contract 與 current distribution profile。
- 使用 repository package code 解析實際 profile：659 個 target paths、643 個 unique source paths，沒有 target collisions 或 exclusion overlap，且 payload reference integrity passed。

### 委派

- 使用 sub-agents：`yes`。
- `.dev` structure/content/lifecycle inventory：`ai-context-auditor` 下的 bounded general worker，read-only，無 nested delegation。
- Package/projection cross-check：`ai-context-auditor` 下的 bounded routine worker，read-only，無 nested delegation。
- Main-agent reconciliation：以 Git-blob counts 取代 checkout-byte counts，獨立驗證 high-severity evidence 與 live provider state，並將 active broken-link total 修正為四個 canonical targets 中的七次 occurrences。

### 探索加速器

| Tool / generated view | Source revision | Use | Unsupported relationships | File-backed fallback |
| --- | --- | --- | --- | --- |
| Codebase Memory MCP | current indexed repository | 找到 validation entrypoints 與 traversal behavior | 無法建立 package completeness、current provider state 或 document truth | Git tree、direct files、native validators |
| Distribution resolver | `3a60570d...` | 解析 source/target paths、exclusions、components 與 mappings | 無法證明 published v0.11.0 archive contents | #172 archive read-back |
| GitHub Project projection | provider read-back on 2026-08-09 | 目前的 #171 lifecycle 與 field options | 不會授權 implementation 或 integration | Issue body、Git、assessment evidence |

## 內容類型矩陣

| Type | Tracked facts | Authority | Package disposition |
| --- | --- | --- | --- |
| Reusable governance/guidance | 118 current profile source paths | Canonical `.ai` semantics 加上 selected `.dev` governance 與 human guides | Framework-managed 或 seed projection |
| Target-effective state | `.dev/ai-context/environment-policy.yaml` | Current repository evidence；下游 target 擁有其自身 state | Not packaged |
| Current source projections | Root/backlog/workflow/assessment/release indexes 與 provider config | Derived from locators、item records、release records 與 provider read-back | Source-only |
| Immutable execution history | 68 completed workflows；39 assessments | Each locator/report/task/evidence set | Never packaged；byte-stably retain |
| Immutable release history | 14 published release records | Each version's `release.yaml` | Never packaged；byte-stably retain |
| Compatibility/source operations | Rename notice、publication runbook、lessons | Source repository governance | Not packaged |

完整的 machine-readable matrix 位於 [`evidence/dev-inventory.yaml`](evidence/dev-inventory.yaml)。

## Authority 與生命週期結論

1. Online Issues/Projects 是目前的 work-management authority。Provider state 本身不會授權 implementation，但 local backlog/index projections 也不能覆寫 online queue。
2. 對 55 個 migrated/local items 而言，backlog item YAML 仍是 historical decision/release evidence。它不是 111 個目前 Project items 的完整 inventory。
3. Workflow locators 擁有 execution lifecycle；assessment locators 擁有 observations；release manifests 擁有 version lifecycle。它們的 indexes 是 discovery projections，不是 competing truth。
4. Completed/published history 必須保持 immutable 且可驗證，但 routine critical validation 不必無界地與 history 成比例。changed-path routine gate 加上 scheduled/release full-history gate 是建議設計，仍須 owner approval。

## 優勢

1. 此 profile 將所有有日期的 workflow、assessment、backlog-item 與 release-instance history 排除於 downstream payloads。
2. 所有 68 個採用後 workflow、39 項 assessments 與 14 筆 release records 均通過其 native structural validators。
3. Portable governance mappings 刻意使用 `.ai/assets/shared/governance/**` bytes，而非三項 source-local work-management/Git policies。
4. v0.11.0 annotated tag 與 peeled commit 符合 release record，且是 audit subject 的 ancestors。

## 發現事項

| ID | Severity | Finding | Evidence | Impact | Recommendation | Owner / Next Skill |
| --- | --- | --- | --- | --- | --- | --- |
| DEV-001 | HIGH | Current roadmap、backlog index 與 source GitHub provider contract 落後於 item、release 與 live Project state。 | `.dev/backlog/ROADMAP.md:5-9`；`.dev/backlog/INDEX.MD:8-45`；八個 v0.9 item records；`.dev/releases/INDEX.MD:26-31`；`.dev/backlog/providers/github.yaml:127-153`；live Project fields 包含 v0.11.0/v0.12.0 與 111 items。 | Agents 可能將 v0.9.0 讀作 current target 或 awaiting publication，而 Project 正規劃 v0.12.0，且 v0.11.0 已 published。 | 從 authoritative records/read-back reconcile current projections 與 provider schema。保留所有 immutable receipts 與 history。 | Issue [#175](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/175)；`ai-context-governance`。 |
| DEV-002 | MEDIUM | 目前 `.dev` 文件含有七個指向已移至 `.ai/assets/tech-stacks/dotnet-backend/standards/` 之四項 standards 的 broken references；requirement guide 另列出四個不存在的 examples。 | `.dev/ARCHITECTURE.md:3,18,32`；`EZDDD-FRAMEWORK-REFERENCE.md:24,26-27`；`DATABASE-MIGRATION-GUIDE.md:120`；`REQUIREMENT-GUIDE.MD:78-82`。 | 即使 canonical targets 存在，目前的 source navigation 仍會誤導。 | 僅修復 active documents；讓 historical assessment/workflow/release links 保持 byte-stable。 | 與 DEV-001 相同的 #175 governance remediation。 |
| DEV-003 | MEDIUM | Critical validation profile 每次執行都會重新驗證全部 68 個 completed workflows 及其 task records。 | `.ai/scripts/check-all.sh:1128-1145`；`validate-workflow-artifacts.py` traversal；local timing 5.419 s（workflows）、0.347 s（39 assessments）、1.125 s（14 releases）。 | Routine cost 隨 immutable history 單調成長，而 changed current truth 沒有獲得更高優先級。 | 設計 changed-path routine validation 加上 scheduled/release full-history validation，並採用 fail-closed tamper detection，且不得削弱 coverage。 | Issue [#176](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/176)；implementation 前需要 owner decision。 |
| DEV-004 | MEDIUM | 29 個 `.dev` paths 未被 packaged，且不符合任何明確的 exclusion rule。 | `dev-inventory.yaml`；profile resolution at `3a60570d...`。 | 目前 bytes 已安全省略，但 owner/classification/reason 無法從 profile 重現；#172 無法僅從 profile 證明 exhaustive disposition。 | 由 #172 classify 這 29 個 paths，並決定是否需要明確的 disposition registry/schema。此 assessment 不得變更 package bytes。 | Issue #172；僅在其 inventory 選定 schema change 時才 follow-up。 |

## 基線與 Skill 比較

### 已確認

- 兩次 pass 都將 workflow、assessment、release、provider-receipt 與 backlog-instance history 分類為 source-only evidence。
- 兩次 pass 都指出 current roadmap/backlog projection drift 與 active documentation reference drift。
- 即使 current projection stale，native validators 仍通過，確認這是 coverage gap 而非 malformed artifacts。

### Repository-Aware Review 新增內容

- Live Project #3 已包含 v0.11.0 與 v0.12.0 options，而 source provider contract 僅到 v0.10.0。
- 29 個 `.dev` files 是 implicit allowlist omissions，而非明確的 source-only exclusions。
- Routine critical validation 與 history 成比例；workflow validator 單獨在此 revision 花費 5.419 seconds。

### 已修正

- Git checkout byte counts 被駁回，因為 Windows CRLF expansion 不同於 canonical Git blobs。
- Active link drift 是四個 canonical target documents 中的七次 occurrences，而非源自 historical broken references 的計數。

## 驗證

| Check | Result | Evidence / Notes |
| --- | --- | --- |
| Git tree coverage | passed | 1,011 個 tracked `.dev` blobs / 5,810,865 Git-blob bytes；entry sums exact。 |
| Distribution resolution | passed | 118 個 `.dev` sources、mappings 後 129 個 `.dev` targets；whole payload 為 659 targets / digest `9d559dec5d36975305e53bb7ee71403a1e711f76e59a8bf1c63352f86edfd6c1`；沒有 collisions 或 reference-integrity violations。 |
| Assessment artifacts | passed | 39 項 assessments。 |
| Workflow artifacts | passed | 68 個採用後 workflows、88 個 indexed workflow directories、55 個 backlog items。 |
| AI context versions | passed | 14 筆 release records。 |
| Current document references | failed | 七個 active references 指向四項已移動的 standards；四個具名 requirement examples 不存在。 |
| Provider state | passed for read-back | #171 為 `In progress / v0.12.0 / Not yet published`；Priority 與 Owner review 仍未設定。 |

### 環境限制的檢查

- 暫存寫入的 package/wrapper/adapter tests 在設定的 temporary directory 遇到 Windows `WinError 5`。它們被記錄為 `blocked-by-environment`，在語義上不是 passed 或 failed。
- `validate-ai-context-target.py` 為 `not-applicable`：此 source repository 刻意沒有下游 `.dev/ai-context/provenance.yaml`。

## 建議行動順序

1. 使用 #175 處理 DEV-001 與 DEV-002；其 scope、reviewer、rollback 與 validation 具備 cohesive scope。
2. 使用 #176 處理 DEV-003，因為它變更 validation lifecycle，而非 current content。
3. 將 DEV-004 與完整的 29-path list 交給 #172；在該 inventory 決定 schema need 前，不建立 redundant package Issue。
4. 將 identity/alias/history list 提供給 #166，但不要重新命名 repository history、package IDs、technology profile、namespace 或 CLI identity。

## 延後項目

- #171 的 Priority：owner decision；建議 `P1 High`。
- Routine/full historical validation cadence：#176 中的 owner decision。
- Package-disposition schema 及任何 byte changes：#172。
- Product/package/archive/profile identity：#166。
- 沒有 immutable workflow、assessment、release、tag、asset 或 provider receipt 被變更。

## 附錄

### 執行的命令

```text
git fetch --prune origin
git ls-tree -r -l 3a60570d0e290f337f2a212d092c6797670528b4 -- .dev
gh project field-list 3 --owner YuChia-Wei --format json
gh project item-list 3 --owner YuChia-Wei --format json --limit 200
python .ai/scripts/validate-ai-context.py
python .ai/scripts/validate-assessment-artifacts.py
python .ai/scripts/validate-workflow-artifacts.py
python .ai/scripts/validate-ai-context-versions.py
python .ai/scripts/validate-source-governance.py
python .ai/scripts/validate-file-disposition-manifest.py --manifest <v0.5.0 disposition manifest>
```

### 注意事項

- `gh` 依 owner 要求在 sandbox 外執行。
- Package resolver output 描述 `HEAD` 的 current source contract；它不是 v0.11.0 published-archive read-back。

## Lifecycle 交接

- Assessment path：`.dev/assessments/ASM-20260809-004/report.md`
- Machine inventory：`.dev/assessments/ASM-20260809-004/evidence/dev-inventory.yaml`
- Stable findings：`ASM-20260809-004#DEV-001` 到 `#DEV-004`
- Current projection/reference remediation：Issue [#175](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/175)；`ai-context-governance`
- Immutable-history validation policy：Issue [#176](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/176)；implementation 前需要 owner decision
- Package handoff：Issue #172
- Identity handoff：Issue #166
- 此 skill 刻意未執行 remediation：`yes`
