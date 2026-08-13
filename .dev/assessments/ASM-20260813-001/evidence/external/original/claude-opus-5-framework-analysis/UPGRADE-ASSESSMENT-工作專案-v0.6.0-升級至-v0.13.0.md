# 工作專案升級評估：v0.6.0 → v0.13.0（七跳 governed upgrade 路徑）

- 框架基準：`5c93e81`（tag `v0.13.0` 於 2026-08-12 18:10 發布，距 v0.12.0 共 48 commits）
- 目標現況：**v0.6.0**（擁有者告知，2026-08-11 已正式升級完成）
- 參考樣本：本機留存的舊副本（**v0.5.0**，非目標現況）
- 評估日期：2026-08-11 初版，**2026-08-13 依 v0.13.0 更新**

---

## 0. 證據邊界（先講清楚我看得到什麼）

| 項目 | 來源 | 可信度 |
|---|---|---|
| 目標在 v0.6.0 | 擁有者告知 | 事實 |
| 9 個 `local_overrides` + 6 個 `unresolved` 的內容 | **本機 v0.5.0 副本**的 `.dev/AI-CONTEXT-SOURCE.yaml` | **參考值**。v0.6.0 升級時應已轉制並可能增刪 |
| 客製項目的具體衝突面 | 同上 | 參考值 |
| 框架各版的遷移要求 | 框架 repo `.dev/releases/*/migration-guide.md` | 事實 |
| v0.12.0 / v0.13.0 破壞面 | 各版 `release-notes.md` / `migration-guide.md` | 事實 |
| 目標實際的 `customizations.yaml` 內容 | **無法取得** | 【未量測】 |

**最重要的未知**：目標升 v0.6.0 時，那 9 個 override 有沒有完整轉成 `.dev/ai-context/customizations.yaml` 的正規記錄？本機副本仍是舊制 `.dev/AI-CONTEXT-SOURCE.yaml`（無 `.dev/ai-context/` 目錄）。這一題的答案直接決定後面能不能走自動路徑——見 §7。

---

## 1. 路徑：v0.6.0 → v0.13.0 是七跳，不能跳號

逐版讀過 migration guide，**每一版都只接受「恰好前一版」**：

| 目標版本 | Supported Sources 原文要求 |
|---|---|
| v0.7.0 | 「only the exact published **v0.6.0** package inventory… use `--previous-version v0.6.0`」 |
| v0.8.0 | 「from the exact published **v0.7.0** package inventory」 |
| v0.9.0 | 「only from the exact published **v0.8.0** package inventory」 |
| v0.10.0 | 「supported from **v0.9.0**」 |
| v0.11.0 | 「from exactly **v0.10.0**」 |
| v0.12.0 | 「from exactly **v0.11.0**」 |
| **v0.13.0** | 「僅支援從 **v0.12.0** 升級。**v0.13.0 是 breaking migration checkpoint，不得自動跨越**」 |

所以是 **7 次連續的 governed upgrade**，每次都要那一版已發布 archive 的 `metadata/files.yaml`。

v0.13.0 的 migration guide 用了 **breaking migration checkpoint** 這個措辭，並明講「更早版本需要 owner-reviewed reconciliation，或先按各版本 checkpoint 逐步升級」——**不存在把 v0.6.0 一步帶到 v0.13.0 的自動路徑**。

### 好消息：你站在最好的起點

v0.7.0 的遷移要求是「恰好 v0.6.0」——**你正好在 v0.6.0**。這是整條鏈唯一「起點完全對得上」的位置。如果目標當初停在 v0.5.0，第一跳就得走人工 reconciliation。

### 壞消息：這條鏈很長，而且每跳都要處理客製

粗估工作量（【推論】，非量測）：

```
7 跳 × (下載並驗證 archive → dry-run plan → 逐項審查 collision
        → acknowledge → apply → target validation → 保留 receipt)
     + 每跳重新處理 9 個 override
```

不是 6 × 一小時，因為衝突集中在少數幾跳（見 §3）。但也不會是一個下午。

---

## 2. 目標的客製化盤點（依 v0.5.0 副本，需以實際 `customizations.yaml` 校正）

| ID | disposition | 內容 | 升級時的處理 |
|---|---|---|---|
| OVR-001 | `keep` | 自訂 skill 的 zh-TW 內容（language policy 例外） | 每跳都要讓 language validator 接受這些路徑 |
| OVR-002 | `re-apply-on-upgrade` | tech-stack 真相區塊（MSSQL/Kafka 等）覆寫 7 個框架檔 | **每跳重新套用** |
| OVR-003 | `reconcile-on-upgrade` | `dev-workflow` 模板 port（timeline 欄位、review 模板、local profile id） | 見 §3.3 |
| OVR-004 | `reconcile-on-upgrade` | commit policy 文法委派給自有 `COMMIT-CONVENTIONS.md`、zh-TW title、subject_pattern 放寬 | **高風險，見 §3.1** |
| OVR-005 | `keep` | `TEAM-GIT-FLOW-RULES.MD` 整檔保留（ut→uat→prd、master、sprint/issue 分支） | **持續發散，見 §3.4** |
| OVR-006 | `reconcile-on-upgrade` | 保留自有的 use-case 命名 doctrine、project-structure、coding-guide | 見 §3.2 |
| OVR-007 | `re-apply-on-upgrade` | `.dev/standards/` 與 `.dev/guides/` **整棵樹**的 in-place override 段落 | **最高風險，見 §3.2** |
| OVR-008 | `re-apply-on-upgrade` | registry 與 wrapper index 額外列出 2 個自訂 skill | 每跳重套 |
| OVR-009 | `drop-when-upstream-fixed` | 移除 package 排除但 index 仍列出的 source-only 參照 | **可能已可 drop，見 §5.4** |

另有 6 項 `unresolved`（UNR-001~006），其中 `UNR-001-tools-analyzers-deferred` 對後續判斷很關鍵——見 §5.1。

---

## 3. 四個高風險衝突面

### 3.1 🔴 OVR-004：commit policy —— v0.11.0/v0.12.0 剛好動過

框架在 v0.11.0 修改了 commit 標題文法定義（`AGENTS.md` diff 可見）：

```diff
-2. Use `<type>(#<issue-number>|<scope>): <summary>` when an issue number exists.
-3. Use `<type>(<scope>): <summary>` when no issue number exists.
+2. Use exactly one of `<type>(#<issue-number>): <summary>` or `<type>(<scope>): <summary>`; they are alternatives.
+3. Treat `|` in historical examples as meta-notation for "or", never as a literal character in a new commit title.
```

目標的 OVR-004 把標題文法**委派給自有的 `COMMIT-CONVENTIONS.md`**（`type(#issue): zh-TW title`），並放寬了 `GIT-COMMIT-POLICY.yaml` 的 `subject_pattern`。

**風險**：框架有 `validate-git-commits.py` 會實際驗證 commit message。若 v0.11.0 的新文法定義覆蓋了目標放寬過的 `subject_pattern`，**目標既有的 zh-TW commit 歷史可能開始驗證失敗**。

**建議**：這一項在 v0.10→v0.11 那一跳要特別停下來，先確認目標的 `subject_pattern` 覆寫在新版 schema 下仍然合法。

### 3.2 🔴 OVR-006 + OVR-007：`.dev/standards/` 與 `.dev/guides/` 的樹狀 override

這是最麻煩的一項，原因是**框架在 v0.9.0 對這兩棵樹做過大搬遷**（GOV-006 / Issue #111「migrate portable .NET rule assets」）：.NET 規則資產從 `.dev/standards/` 移到 `.ai/assets/tech-stacks/dotnet-backend/`。

而 OVR-007 的做法是「在框架文件內就地插入或附加 `Service Local Override` 段落」，涵蓋 `.dev/standards/`、`.dev/guides/`、`.dev/operations/README.MD`、`.dev/workflows/README.MD`、`.dev/adr/README.md`。

**風險**：
- 檔案被 rename/move 時，就地插入的 override 段落會跟著走，但**搬到新位置後語意可能不再正確**（例如原本針對 `.dev/standards/` 的 dotnet 規則，搬去 tech-stack 目錄後脈絡變了）
- 有些檔案是 `remove`（如 v0.12.0 刪掉 `UCONTRACT-GUIDE.md`、`ezddd-import-mapping.md`），**override 段落會連同宿主檔案一起消失**

【實測】v0.12.0 的 distribution profile 確認 `.dev/standards/**` 與 `.dev/guides/**` **仍然會安裝到目標**，所以這個衝突面在每一跳都是活的。

**建議**：把 OVR-007 從「就地插入」改成「獨立檔案 + 引用」。例如建立 `.dev/standards/LOCAL-OVERRIDES.md` 集中所有本地覆寫，框架檔案只留一行指向它。這樣 rename/remove 不會吃掉你的內容。**這個重構值得在第一跳之前就做**，會讓後面 6 跳都變簡單。

### 3.3 🟠 OVR-003：`dev-workflow` 模板 port

`dev-workflow` 在 v0.6.0 已更名為 `software-development-orchestrator`（SKILL-001）。若目標真的在 v0.6.0，這個 override 的路徑應該已轉移過一次。

但要注意兩件事：
1. 目標當初 port 的是 **task timeline 欄位**（`started_at`/`completed_at`/`last_validated_at`/timezone）——【觀察】這正好是框架 Issue **#21 DEVWF-001** 的題目，而 #21 **至今未排程**。也就是說目標在這一點上領先框架，且沒有收斂跡象，每跳都要重新 reconcile。
2. v0.12.0 的 task template 又演化了（新增 `model`、`reasoning_effort`、`finding_ids` 欄位）。目標的 1.2.0 自訂版與框架現行版本已分歧多輪。

**建議**：考慮把 OVR-003 的通用部分（timeline 欄位）正式提報上游成為 #21 的輸入。你有真實使用經驗，而框架至今沒有動力做——這是少數「回饋上游能實際降低自己維護成本」的項目。

### 3.4 🟠 OVR-005：分支模型持續發散

目標用 `ut→uat→prd` promotion + `master` + `sprint`/`issue` 分支，整檔 `keep`，與框架的 single-trunk 模型不同。

而框架在 v0.10.0~v0.12.0 期間：
- 把 work-item binding 從 `optional` 改成 **`required`**（每個 material 變更都要先有 online Issue）
- 改成 terminal release lifecycle（tag 觸發發布，不再有 post-tag closeout PR）

【推論】這兩項都預設了 GitHub Issues 作為 work-management authority。若目標用的是內部 tracker（Azure DevOps？根目錄有 `azure-pipelines.yml`），`required` binding 的語意需要重新對映，否則框架的 workflow gate 會要求一個不存在的東西。

**建議**：在 `.dev/backlog/providers/` 明確記錄目標選用的 provider 與 binding mode，不要讓它繼續靠 OVR-005 的散文承載。

---

## 4. v0.12.0 特有的注意事項（第七跳前的最後一跳）

### 4.1 `ez*` / UContract 命名移除，但**框架不會幫你改**

v0.12.0 migration guide 第 3 步寫得很明確：

> Review target-owned references to the former repository name or deleted example paths. **The framework migration must not silently rewrite target-owned documentation or customizations.**

【實測】本機 v0.5.0 副本裡有 **8 個檔案**引用 `ezspec`/`ezddd`/`UContract`，**全部在 `.dev/` 下**：

```
.dev/guides/learning-guides/LEARNING-PATH.md
.dev/guides/implementation-guides/COMMON-MISTAKES-GUIDE.md
.dev/guides/design-guides/INDEX.MD
.dev/standards/examples/outbox/README.md
.dev/standards/examples/contract/README.md
.dev/standards/examples/reference/README.md
（另有 2 個在該副本自己的升級 workflow evidence 內，屬歷史紀錄，不需改）
```

實際專案的數量需要自己 grep 一次。這些是**人工工作**，不在 upgrader 的職責內。

### 4.2 repo 已更名

框架 repo 已從 `ai-collaboration-prompts-dotnet-backend` 更名為 `ai-collaboration-framework`。目標的 `.dev/AI-CONTEXT-SOURCE.yaml`（或 `provenance.yaml`）記錄的 `source.repository` 是舊 URL。

框架的 `.dev/REPOSITORY-RENAME-COMPATIBILITY.md` 明講：GitHub 目前回 301，但那是 provider 當下行為、**不是框架保證的永久 alias**，且 `raw.githubusercontent.com` / API / download 不保證有同樣相容性。

**建議**：升級過程中把 provenance 的 repository URL 更新為新座標；舊值只保留在歷史 evidence。

### 4.3 identity registry 與 source dispositions 是新的驗證面

v0.12.0 引入 `identity-registry.yaml`（324 行）與 `source-dispositions.yaml`，並有 fail-closed 驗證。這些是**來源側**治理，理論上不是下游政策輸入（migration guide 明講「The source-disposition registry explains package omissions but is not itself a downstream policy input」）。

【推論】但這代表 v0.12.0 的 target validation 可能對「哪些路徑該存在」更嚴格。目標若有 OVR-009 那種「移除了 index 裡的 source-only 參照」的覆寫，需要確認新版是否仍需要。

---

## 5. v0.13.0（已發布）的影響

> 本節於 2026-08-13 依實際發布內容改寫。原本是對未發布版本的預測，現在是查證。

v0.13.0 於 **2026-08-12 18:10** 發布，距 v0.12.0 共 48 commits。Included Work：**#187、#191、#192、#193、#194、#197**。

### 5.1 🟢 #187 CTX-009 已完成：框架不再直接依賴 .NET SDK

【實測】`tools/` 目錄**已從 repo 移除**（`DotnetBackendAnalyzers.Tests`、`DotnetBackendValidation.Tests`、`DotnetBackendBuildingBlocks.Tests` 全數刪除）。

owner 的決策已落地：

> 1. framework 的預設發布基線應脫離 .NET SDK 的直接倚賴；
> 2. framework 不再把內建可編譯 analyzer project 及其 unit-test project 當作必要發布元件或 required release gate；
> 4. 只有在使用者明確要求／選擇時，才於目標 repository 建立 target-owned 專屬 analyzer project。

**這正好對應目標的 `UNR-001-tools-analyzers-deferred`。** 目標當初就沒安裝框架的 analyzer 專案（本機副本無 `tools/`），一直掛著 unresolved。v0.13.0 把「不裝」變成官方預設，**那個 unresolved 自動消解**。

同時：目標的 gate 不再需要 .NET SDK 才能跑框架 required checks——對一個本來就有自己 .NET 建置流程（`azure-pipelines.yml`）的專案來說，這是實質減負。**這是七跳裡唯一一項純減負的變更。**

### 5.2 🟢 #61 STD-001 **沒有**進 v0.13.0（我先前標的風險未發生）

我原本擔心「STD-001 Standards Simplification Round 2/3 若動到 `.dev/standards/` 結構，OVR-006/OVR-007 會大衝突」。**查證結果：v0.13.0 的 Included Work 不含 #61**，release notes 也未提及。該風險**遞延**，仍會在某個未來版本出現。

### 5.3 🟠 但 `.dev/standards/` 與 `.dev/guides/` 仍動了 14 個檔案

【實測】`git diff --stat v0.12.0..v0.13.0 -- .dev/standards/ .dev/guides/`：**14 個檔案、+647／−151 行**。主要變動：

| 檔案 | 變動 |
|---|---|
| `AI-CONTEXT-OWNERSHIP.yaml` | **+296 行** |
| `AI-CONTEXT-SOURCE-RELEASE-POLICY.md` | **新增，160 行** |
| `AI-CONTEXT-VERSION-POLICY.md` | 大幅重寫（−120 行） |
| `WORKFLOW-GATE-POLICY.md` | +74 行 |
| `AI-CONTEXT-OWNERSHIP.md` | +40 行 |
| `DEPENDENCY-VERSION-CONSISTENCY-POLICY.md`、`WORKFLOW-HANDOFF-POLICY.*`、`WORKFLOW-ARTIFACT-POLICY.md`、`ASSESSMENT-ARTIFACT-POLICY.md`、`INDEX.MD` | 小幅 |
| `.dev/guides/implementation-guides/`（3 檔） | `COMMON-MISTAKES-GUIDE.md`、`PERSISTENCE-CONFIGURATION-GUIDE.md`、`TEMPLATE-USAGE-GUIDE.md` |

**結論：即使沒有 STD-001，OVR-006 與 OVR-007 的衝突面在 v0.12→v0.13 這一跳依然是活的**，而且 `.dev/guides/implementation-guides/COMMON-MISTAKES-GUIDE.md` 正好也是 §4.1 列出的 `ez*` 引用檔案之一——同一個檔案會同時遇到框架改寫與目標自有引用需要清理。

### 5.4 OVR-009 可能已可 drop

OVR-009 的原因是「published package 排除了某些 source-only 資產，但打包的 registry/index 仍列出它們」——這正是 v0.12.0 `PKG-010` source-disposition 工作要解的問題（「every source-only `.dev/**` omission is covered by a machine-readable exclusion or disposition instead of an unexplained gap」）。v0.13.0 又新增了 `AI-CONTEXT-SOURCE-RELEASE-POLICY.md` 與大幅擴充的 `AI-CONTEXT-OWNERSHIP.yaml`，方向一致。

**建議**：升到 v0.12.0 後驗證一次，若上游已修好就依 disposition `drop-when-upstream-fixed` 移除這個 override。

---

## 6. 我的建議：先做 v0.6.0 → v0.7.0 一跳，然後停下來評估

不要一次規劃七跳，理由有四：

1. **這是唯一 provenance 完全對得上的一跳。** v0.7.0 要求「恰好 v0.6.0」，你正好在。爆炸半徑最小。
2. **它會給你真實的成本數據。** 做完一跳，你就知道 9 個 override 實際要花多少時間處理、dry-run 的 collision 數量級、target validation 會不會過。之後 6 跳可以據此排程，而不是猜。
3. **它同時是 `ai-context-upgrader` 的第一次端到端真實驗證。** 依我的分析（`ANALYSIS-v0.12.0.md` §6.2），這條路徑至今沒有一筆真實執行紀錄——機械套用層測試紮實，但「讀 provenance → 三方比對 → 語意客製化逐項調解 → 升級後稽核 → provenance finalization」這整條沒被走過。**你這一跳會是第一次。**
4. **失敗的資訊價值很高。** 如果第一跳就卡住，那答案是「這條鏈目前不可行，需要先修 upgrader 或改走人工 reconciliation」——這個結論值得現在知道，而不是走到第四跳才發現。

### 6.1 在第一跳之前，先做 §3.2 的重構

把 OVR-007 從「在框架檔案內就地插入 override 段落」改成「集中在 `.dev/standards/LOCAL-OVERRIDES.md` 等獨立檔案，框架檔案只留指標」。

這件事現在做的成本是一次，之後 6 跳都受益；等到第三跳才發現 override 段落被 rename 帶走或被 remove 吃掉，成本會高得多。

### 6.2 終點該設在哪（2026-08-13 更新）

v0.13.0 已發布，原本「要不要等」的問題現在有答案了：

- **終點設 v0.13.0**，不要停在 v0.12.0。理由是 #187 讓框架脫離 .NET SDK 依賴，**這是七跳裡唯一一項純減負的變更**，也直接消解目標掛了很久的 `UNR-001`。停在 v0.12.0 等於放棄這個收益卻還要承擔前六跳的成本。
- **#61 STD-001 沒有進 v0.13.0**（§5.2 已查證），所以它不構成「再等一版」的理由。但它遲早會來，屆時 OVR-006/OVR-007 會再痛一次——**這反而是盡早把 §6.1 的 override 重構做掉的理由**。
- 框架目前約每 1~2 天一個 minor 版本（v0.9.0→v0.13.0 五天四版）。**追版本追不完，設一個終點做完，之後再定期追。** 不要把「保持最新」當目標。
- #187 的好處（免 .NET SDK）要到 v0.13.0 才有，但它不影響前幾跳

---

## 7. 前置檢查清單（第一跳之前）

| # | 檢查 | 為什麼 |
|---|---|---|
| 1 | **確認 `.dev/ai-context/provenance.yaml` 與 `customizations.yaml` 存在且內容完整** | 本機副本仍是舊制 `AI-CONTEXT-SOURCE.yaml`。框架把舊制列為「legacy read compatibility」且**不可兩者並存**。若 v0.6.0 升級時沒轉制，第一跳會失敗 |
| 2 | 確認 9 個 override 都已轉成 `customizations.yaml` 條目且 disposition 正確 | upgrader 依 disposition 決定調解方式；漏一個就會被靜默覆蓋 |
| 3 | 下載 v0.6.0 published archive，驗證 checksum，取出 `metadata/files.yaml` | v0.7.0 migration 明確要求 `--previous-version v0.6.0` 搭配該 inventory |
| 4 | 目標 worktree 乾淨、在預期起始 commit | 所有 migration guide 的共同前提 |
| 5 | Python 3.11+ 與 `PyYAML==6.0.3` | 框架 fail-closed，版本不符會直接擋 |
| 6 | `grep -rl "ezspec\|ezddd\|EZDDD\|UContract\|ucontract" .dev/ .ai/` 記錄基準數量 | v0.12.0 才需要處理，但先知道規模 |
| 7 | 決定 work-item binding provider 與 mode | v0.10.0+ 框架預設 GitHub Issues 為 authority；目標若用別的要明確記錄 |
| 8 | 先做 §3.2 的 override 重構 | 讓後續每一跳都變簡單 |

---

## 8. 需要你確認的三件事

我無法從本機驗證，但它們會改變上面的結論：

1. **目標的 provenance 是新制還是舊制？** 若仍是 `.dev/AI-CONTEXT-SOURCE.yaml`，第一步不是升級，是先轉制。
2. **9 個 override 在 v0.6.0 升級後還剩幾個？** 有些可能已在升級過程中被上游吸收或放棄。實際數量決定工作量。
3. **目標的 work-item tracker 是什麼？** 根目錄有 `azure-pipelines.yml`，若 tracker 是 Azure DevOps 而非 GitHub Issues，v0.10.0+ 的 `required` binding 語意要先對映好。

把 `.dev/ai-context/customizations.yaml`（或現行的 provenance 檔）貼給我，我可以把 §2 的表換成實際內容，並逐項標出七跳中哪一跳會碰到它。
