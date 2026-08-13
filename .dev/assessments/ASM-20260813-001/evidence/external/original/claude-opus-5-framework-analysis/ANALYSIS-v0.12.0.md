# AI 協作框架分析報告（完整重跑）

- **分析基準**：`a4fd14f0f08ad53859df1c860db0eb9643cdb2de`（2026-08-11 01:52 +0800，tag `v0.12.0`）
- **repo**：`YuChia-Wei/ai-collaboration-framework`
- **分析日期**：2026-08-11
- **分析者**：Claude Opus 5（未使用本 repo 的 skill，未套用其工作流程規範）
- **前次分析**：`archive/01`~`07`（基準 `481c84c` / `079b517`），**本文完整取代，衝突處以本文為準**

---

## 0. 方法：證據等級與防誤報機制

前兩次分析各出現一次實質誤報。為避免重演，本文每個關鍵陳述都標註證據等級：

| 標記 | 意義 |
|---|---|
| 【實測】 | 我在本機執行或從 GitHub API 取得的原始數據 |
| 【repo 記錄】 | repo 內由維護者記錄的量測結果，我只做引用與交叉比對 |
| 【靜態】 | 從程式碼／設定檔解析得出，不涉及執行 |
| 【推論】 | 我的判斷，**非事實**，已標明推理鏈 |
| 【未量測】 | 沒有資料。不估算、不換算 |

### 0.1 前兩次的誤報與根因

| 誤報 | 根因 | 本次防範 |
|---|---|---|
| 「必讀政策鏈 121 KB ≈ 30k tokens，每條分支付一次」 | 把檔案位元組加總當成 prompt token。**repo 的量測契約明文寫 `repository_corpus_is_prompt: false`** | §7 只陳述載入條件，不給 token 總量 |
| 「upgrader 從未端到端執行」 | 只看 open issue 清單就下結論，未搜 repo，且混淆了兩個不同層級 | §6 拆成兩層，各自附證據 |
| 「`release` profile = 190 秒」 | 引用了一筆 `executed=1 reused=51` 的**快取命中**紀錄，當成冷啟動成本 | §3 明確區分冷跑與快取命中 |

三次錯誤的共同模式：**拿一個容易取得的數字去代表一個我沒實際量到的東西。** 本次凡遇此情況一律標【未量測】。

### 0.2 本次的能力邊界

- 本機 Python 為 3.9.6，框架要求 ≥3.11 且 fail-closed，**我無法在本機執行任何 gate**。所有本機耗時數據皆為【repo 記錄】。
- 無 `gh` CLI，GitHub 資料透過未驗證的公開 REST API 取得（僅公開資訊）。
- 無法取得 Actions 原始 log（需 admin 權限），故 CI 只有 job/step 層級秒數。

---

## 1. 基準事實【實測】

```
HEAD          a4fd14f  2026-08-11 01:52:01 +0800
工作區        乾淨（僅未追蹤的 .DS_Store 與 docs/）
```

### 1.1 發布節奏

| 版本 | 標記時間 | 距前版 commit 數 |
|---|---|---:|
| v0.9.0 | 08-06 00:27 | — |
| v0.10.0 | 08-08 13:30 | 24 |
| v0.11.0 | 08-09 00:52 | 8 |
| v0.12.0 | 08-11 01:52 | 55 |

**五天內三個 minor 版本，87 個 commit。**

### 1.2 累積量

| | v0.9.0 | v0.12.0 |
|---|---:|---:|
| workflow 目錄 | 86 | **95** |
| assessment | 40 | **49** |

---

## 2. 驗證系統的現況【靜態】

### 2.1 profile 註冊表

`validation-profile-registry.sh` 註冊 **61 個檢查**（58 required + 3 advisory），分屬五個 profile：

| profile | 檢查數 | 時間預算 | enforcement | 誰在跑 |
|---|---:|---:|---|---|
| `fast` | 30 | 30 s | report-and-warn | CI `AI Context Governance` job；本機開發 |
| `pr` | 42 | 90 s | report-and-warn | CI `Portable AI Context Gates` job |
| `release` | 57 | 無 | measure-first | **只在維護者本機**（`--critical` 別名） |
| `closeout` | 1 | 120 s | report-and-warn | 發布後 |
| `nightly-full` | 60 | 無 | measure-first | **預設值**（不帶參數時） |

相容別名：`--quick`→`pr`、`--critical`→`release`、`--full`→`nightly-full`。

**這是 v0.9.0 時「三個模式實質相同」問題的完整解決**：現在有真實分層、時間預算、changed-path 選擇（`--base`/`--head`，或自動用 `git merge-base HEAD @{upstream}`）、以及 input fingerprint 快取重用。

### 2.2 輸出處理

```bash
emit_retained_output() {
    if [ "$VERBOSE" = true ]; then cat "$log_path"
    elif [ "$outcome" != passed ]; then sed -n '1,20p' "$log_path"; fi
}
```

預設不輸出通過項目的內容；失敗時只印前 20 行；`--verbose` 才全展開。61 個檢查中仍有 41 個帶 `-v`，但其輸出進入 log 檔而非終端。

**v0.9.0 時我判定的最大 token 消耗源（gate 無條件全印）已解決。**

---

## 3. 實際耗時：冷跑與快取命中必須分開看

> **這是本次最重要的修正。** 前次報告寫「`release` profile 190 秒」，那筆數據來自 `executed=1 reused=51` 的快取命中run。冷跑的實際數字差了 7 倍，而且是失敗的。

### 3.1 已知的量測數據

| 情境 | 秒數 | 檢查數 | 結果 | 來源 |
|---|---:|---:|---|---|
| Windows Git Bash `fast` | **24** | 27 選中 | passed | 【repo 記錄】v0.10.0 `V010-VAL.json` |
| Windows `fast` 未變更重跑 | **3** | 27 全部 reuse | passed | 【repo 記錄】同上 |
| Windows `pr` | **49** | 36 選中 | passed | 【repo 記錄】同上 |
| WSL `fast` | **192** | 27 選中 | passed（超預算告警） | 【repo 記錄】同上 |
| Windows `release`（快取命中） | **190~197** | 52，`executed=1 reused=51` | passed | 【repo 記錄】v0.10.0 handoff checkpoint |
| **Windows `release`（冷跑）** | **1,344.651** | **54** | **exit 1，兩項逾時** | 【repo 記錄】`LESSON-VAL-001` |
| CI `pr`（Ubuntu） | **49**（中位數，n=7） | — | 7 成功／2 失敗 | 【實測】GitHub API |
| CI `fast`（Ubuntu governance） | **22**（中位數，n=8） | — | 8 成功／1 失敗 | 【實測】GitHub API |

**注意**：`fast`/`pr` 的 Windows 數據量測於 v0.10.0，當時 `fast`=27、`pr`=36；現在是 30 與 42。**v0.12.0 的 Windows `fast`/`pr` 實際耗時為【未量測】。**

### 3.2 `release` 冷跑 1,344 秒的組成【repo 記錄】

`ASM-20260810-005` 拆解得很清楚：

| 檢查 | 預算 | 實際 | 佔比 |
|---|---:|---:|---:|
| `package-full-matrix`（`test_ai_context_packaging.py -v`） | 900 s | **860.4 s** | **64%** |
| `aggregate-runner-contract` | 300 s | 379.975 s（**逾時**） | — |
| `immutable-history-validation-contract` | 60 s | 67.767 s（**逾時**） | — |
| 其餘 51 項 | — | 約 480 s | 36% |

**單一檢查佔了整個 release gate 的六成四。**

### 3.3 我的評價

正面：`fast` 24 秒、未變更 3 秒、CI 49 秒——**日常開發迴圈已經是健康的**，v0.9.0 那個 847 秒的問題確實解決了。

但有一個結構性風險：**成本最高、目前會失敗的 `release`/`nightly-full` profile，只在維護者的 Windows 機器上跑，CI 完全不跑。** 【靜態】：CI 只有 `fast` 與 `pr` 兩個 job。

【推論】這代表 22 分鐘的冷跑失敗要靠人在發版前才發現，而不是 CI 每晚告訴你。`nightly-full` 這個名字暗示了原本的設計意圖是排程執行，但目前沒有對應的 scheduled workflow。

---

## 4. 已知但未追蹤的驗證缺陷【repo 記錄 + 實測】

`ASM-20260810-005`（2026-08-10）記錄了四項 finding：

| ID | 嚴重度 | 內容 |
|---|---|---|
| `VALSNAP-001` | **HIGH** | 終端驗證未綁定不可變 checkout。獨立 worktree 對「workdir 指向另一個共用 checkout」的指令毫無隔離作用。該次 22 分鐘的驗證期間，來源 checkout 提交了 merge、切到 `main`、又切分支、又提交——結果只能當診斷證據 |
| `VALTIME-001` | **HIGH** | 逾時取消只針對 wrapper 或直接子 PID。`timeout --foreground` 的 fallback 只對 `$!` 送 TERM/KILL，**孤兒行程在逾時後仍繼續寫 log 並最終印出 `OK`** |
| `VALTEST-001` | MEDIUM | 慢速套件重複建立 fixture：aggregate 套件 40 個測試裡有 29 次 `SyntheticRunnerRepo` + 10 次 `SyntheticShellAssetRepo` 建構；immutable-history 套件為 19 個測試各初始化一個 Git repo。相關 `subprocess.run` 無 timeout |
| `VALCOST-001` | MEDIUM | 昂貴套件覆蓋與預算未先對帳：`package-full-matrix` 已在 aggregate 內跑完 860 秒，之後又獨立重跑 1,177 秒，**重複約 20 分鐘** |

### 4.1 這四項目前沒有被追蹤【實測】

四條獨立查證，結果一致：

| 查證方式 | 結果 |
|---|---|
| assessment 自述的 Lifecycle Handoff | `Related remediation workflow: not-created`、`Verification assessment: not-created` |
| `grep` 全 `.dev/` | 四個 finding ID 在 `ASM-20260810-005` 以外**零次出現** |
| GitHub Search API（四個 finding ID + `ASM-20260810-005`，共五組） | **全部 `total_count: 0`** |
| 抓取全部 56 個 issue（#90~#187，open + closed）在本地比對 title 與 body | 四個 ID 與該 assessment ID **零命中**。`timeout` 關鍵字只命中 #96、#134、#146、#149、#168，**全部建立於事故之前**，內容是 profile 設計的一般性討論 |

更能說明問題的是時間軸：事故發生於 **2026-08-10T14:11Z**（run `20260810T141148Z-1549`），而其後兩小時內確實有建立 issue——

```
#184  2026-08-10T14:32  [PKG-010] 建立 machine-readable source disposition contract
#187  2026-08-10T16:17  [CTX-009] 移除 framework 的直接 .NET SDK 倚賴
```

**兩件都與事故無關。** 事故當下工作佇列是活躍的，只是這四個 finding 沒被放進去。

**兩個 HIGH finding 有完整證據、有具名 owner（`ai-context-governance`）、有建議的補救順序，但沒有進入任何工作佇列。**

> **殘餘不確定性【未量測】：** 我比對的是 issue 的 title 與 body。**GitHub Projects 的自訂欄位、issue 留言的完整內容，未驗證的公開 API 無法可靠取得**（Search API 宣稱涵蓋留言，但索引可能延遲）。若這四項其實記在 Project 欄位或留言裡，本節結論需要修正——請以你手上的實際狀態為準。

### 4.2 為什麼這件事重要

【推論】`VALTIME-001` 的具體後果是：**逾時的檢查最後會印出 `OK`**。對一個把「fail-closed、絕不讓未驗證被記成通過」當作核心價值的框架來說，這是價值主張本身的漏洞——不是效能問題。lesson 裡那句話寫得很準：

> A timeout remains a failed orchestration outcome even when an unobserved or surviving process later logs successful assertions.

規則寫對了，但執行層還沒做到。

---

## 5. 程式碼結構趨勢【實測】

以互斥分類逐檔統計行數（`git ls-tree` + `git show`，排除重複計算）：

| 類別（互斥） | v0.9.0 | v0.11.0 | v0.12.0 | 增量 |
|---|---:|---:|---:|---:|
| 驗證器 production (py) | 17,351 | 20,156 | **22,455** | +5,104 |
| 驗證器 test (py) | 15,264 | 17,351 | **18,399** | +3,135 |
| 驗證器 shell | 3,233 | 4,376 | **4,376** | +1,143 |
| **驗證器合計** | **35,848** | **41,883** | **45,230** | **+9,382 (+26%)** |
| 產品內容（`.ai/assets` 非程式） | 29,434 | 29,576 | **29,464** | **+30 (+0.1%)** |
| 治理歷史（`.dev/workflows`+`assessments`） | 84,249 | 89,921 | **92,830** | +8,581 |
| 治理規範（`.dev` 其他） | 20,431 | 21,395 | 21,845 | +1,414 |

**驗證器 : 產品內容 = 1.22 → 1.42 → 1.54**

### 5.1 讀法

五天內：**驗證框架自己的程式碼 +9,382 行（+26%），要交付給使用者的內容 +30 行（+0.1%）。**

這不是說新增的東西沒價值——identity registry、source dispositions、immutable-history validation 都是 #166/#172 盤點後的正當產出，而且 v0.12.0 確實交付了實質的 brand-neutral 清理。但趨勢很清楚：**框架正在快速長出「驗證自己」的能力，而「交付給下游的內容」幾乎靜止。**

### 5.2 與 §3、§4 的因果連結【推論，但推理鏈明確】

1. v0.11.0 新增 `validate-immutable-history.py`（846 行）與其 19 個測試
2. 該套件為每個測試初始化一個 Git repo（`VALTEST-001` 實證）
3. `immutable-history-validation-contract` 在 60 秒預算下實際跑 67.8 秒 → 逾時
4. 這是 `release` 冷跑失敗的兩個原因之一

**驗證器增長 → gate 變慢 → 逾時 → 終端驗證失敗**，這條鏈在 v0.12.0 的證據裡是完整的。這也是為什麼我把它列為現況第一順位問題。

---

## 6. 升級路徑：兩層必須分開講

前次我寫「upgrader 從未端到端執行」，太粗。實際查證後：

### 6.1 機械套用層 —— 驗證紮實【實測】

`test_ai_context_package_apply.py` 有完整的 GWT fixture，涵蓋：

- `test_gwt_003_given_unchanged_managed_base_when_upgraded_then_replace_remove_and_rename_apply`
- `test_gwt_010_given_wrong_previous_manifest_when_upgrade_plans_then_identity_fails_closed`
- `test_gwt_000b_given_component_upgrade_without_provenance_when_planned_then_it_fails_closed`
- `test_gwt_000c/000d`：provider 過濾與 legacy inventory 保留

且每次發布都跑 clean-install 與 exact vN-1 upgrade fixture。**plan / dry-run / replace-add-rename-remove / receipt / hash 驗證這一層，覆蓋良好。**

### 6.2 語意調解層 —— 無真實執行紀錄【實測】

`ai-context-upgrader` 在 `.dev/workflows/` 與 `.dev/assessments/` 命中 45 個檔案，逐條檢視後**全部是設計、路由、契約、保存規則的引用**（例：「upgrader 必須保留 target 的 `validation.local.conf`」「其 step-5/6 驗證屬 lifecycle-owned」）。

**沒有一筆是對真實 target 執行「讀 provenance → 三方比對 → 語意客製化逐項 owner 調解 → 升級後獨立稽核 → provenance finalization」的紀錄。**

這與擁有者提供的事實一致：低版本 → v0.6.0 那一輪的客製整理與回套是**人工**完成的，而那正是這一層。

### 6.3 v0.12.0 把門檻收緊了【實測】

```yaml
compatibility:
  breaking_changes: true
  minimum_source_version: "v0.11.0"
  automatic_upgrade_sources: ["v0.11.0"]
```

`migration-guide.md`：「Automatic governed upgrade is supported from exactly v0.11.0；更早的版本需要 reviewed reconciliation。」

【推論】內部工作專案在 v0.6.0，已落在自動升級範圍外。要嘛逐版升到 v0.11.0（6 次），要嘛又是一次人工 reconciliation。**「upgrader 是正規路線」這個定位，目前對實際持有的目標並不適用**——這不是設計意圖的問題，是版本差距累積的結果。

---

## 7. Context 載入【實測，且刻意不估算】

只陳述可查證的載入條件：

- `CLAUDE.md` 全文為一行 `@AGENTS.md`。**永遠載入的只有 `AGENTS.md`**（16,294 bytes）。
- 其餘政策皆為條件式，條件寫在 `AGENTS.md` 內：`WORKFLOW-GATE-POLICY` = 影響 source-of-truth／AI context／跨階段時；`ROADMAP.md` = 規劃或恢復 post-v0.4.0 發布時；`WORKFLOW-HANDOFF-POLICY` = 跨模型／runtime／主機／機器／新 session 交接時。
- `ROADMAP.md` 從 27,731 增至 **30,670** bytes。

**實際的 per-session 載入量：【未量測】。**

`.ai/evaluation/context-load/` 定義了完整量測契約（要求 `runtime`、`skill-routing`、`release`、`handoff`、`development` 五個 family 各一筆 trace），**目前有 0 筆實測紀錄**【實測：`find` 結果為 0】。

> 框架蓋好了量測儀器，五個版本過去，從未讀過刻度。

在那五筆 trace 出現之前，任何關於 context 成本的排序都是猜測——包括我前兩次寫的。

---

## 8. Issue 與 roadmap【實測】

open issue 從 15 降到 **9**：

| # | 標題 | 我的觀察 |
|---|---|---|
| 187 | [CTX-009] 移除 framework 的直接 .NET SDK 倚賴並改採按需分析器 | **v0.13.0**。owner 已決策：不再把內建 analyzer 專案與其測試當必要發布元件。這比我原本建議的「build 一次 test 三次」更徹底——直接移除 |
| 179 | [CTX-008] 導入 EngineeringGuardrails.Contracts prerelease | 與 #187 分開處理 |
| 168 | [CLI-002] 可安裝的唯讀 Distribution CLI 預覽 | 六個唯讀指令，mutation 明確禁用 |
| 153 | [COP-001] Copilot first-class | 維持延後 |
| 149 | [TOOL-004] Distribution CLI 與驗證器 Runtime 受控比較 | 見 §9 |
| 61 | [STD-001] Standards Simplification — v0.13 Round 2/3 | 已排入 v0.13 |
| 45 / 43 / 21 | OBS-001 / INIT-001 / DEVWF-001 | **仍未排程** |

【觀察】前次報告建議「#61/#45/#43/#21 不排程」——五天後 #61 進了 v0.13，其餘三個仍未動。

---

## 9. 對 #149（runtime 受控比較）的意見

#149 要求 Go 與 Rust 各完成同一個 bounded vertical slice，.NET 與最佳化 Python 只做架構／供應鏈評估。**這個設計是對的。** 我補三點：

### 9.1 要移植的是 orchestration，不是規則

#149 明文寫 Python 在比較期間仍是 authoritative baseline、.NET/Roslyn 繼續負責 .NET semantic validation。所以 Portable Validator Engine 要取代的是 **4,376 行 shell 的選擇／排程／逾時／取消／fingerprint／evidence 層**。

【推論】這一層的本質是**行程樹管理與可靠取消**——正是 `VALTIME-001` 失敗的地方。Go 的 `context` + process group、Rust 的 tokio + process group 都能做，.NET 也能。但這是選型的主軸，不是啟動時間或 binary size。

### 9.2 判準不該是速度

`fast` 已經 24 秒、未變更 3 秒、CI 49 秒。**新 runtime 在速度上沒有可贏的空間。** 建議把驗收條件明確定為：

| 判準 | 可量測的驗收條件 |
|---|---|
| 行程樹可靠終止 | 逾時後**證明**無後代行程、log 已封存、不再有輸出（直接對應 `VALTIME-001`） |
| 跨平台一致性 | WSL 與 Git Bash 的同 profile 耗時差距從目前的 8 倍（192 s vs 24 s）收斂 |
| 快照完整性 | 執行前後的 repo identity 比對內建於 runner（對應 `VALSNAP-001`） |
| 可測試性 | orchestration 層有真正的單元測試，不再有「巢狀 bash 函式隔離」這類問題 |
| 維護面積 | 4,376 行 shell 換成多少行？ |

### 9.3 建議加入第三個對照組

除了 Go 與 Rust，加上**「現況 bash + 已修好 `VALTIME-001`/`VALSNAP-001` 的版本」**。理由：若這兩個 HIGH 修好之後 bash 版就夠用，那 bake-off 的結論可能是「不換」——而那是完全正當的結論，值得被證明而不是被跳過。

【推論】目前的風險是：bake-off 沒開始，而要移植的 shell 層每週在長。v0.9.0→v0.12.0 五天內 shell +1,143 行（+35%）。

---

## 10. 框架評價（v0.12.0）

### 10.1 強項（維持前次判斷，且有新證據）

| 面向 | 評語 |
|---|---|
| **自我批判的誠實度** | `LESSON-VAL-001` 是這次最能說明框架品質的東西。它記錄了一次自己的驗證事故，明確寫「逾時後來印出 `OK` 不會讓逾時變成通過」，並把結果降級為 diagnostic-only。**大多數團隊會直接把那個 `OK` 當通過。** |
| **證據與推測的分離** | `.ai/evaluation/context-load` 的 `repository_corpus_is_prompt: false` 是機器可讀的反推測宣告。我兩次栽在這條上，證明它有效 |
| **驗證分層** | profile + 預算 + changed-path + fingerprint reuse，設計完整且已見效 |
| **可交接性** | 五天三版、多條分支、跨 session，狀態沒有遺失 |

### 10.2 弱項

| 面向 | 評語 |
|---|---|
| **驗證器/產品比 1.54 且持續上升** | 五天 +9,382 行驗證器 vs +30 行產品內容。這是目前最需要 owner 明確表態的趨勢 |
| **已知 HIGH 缺陷未進佇列** | `VALSNAP-001`/`VALTIME-001` 有完整證據卻零追蹤（§4.1） |
| **最貴的 profile 沒有自動化執行** | `release`/`nightly-full` 只在人的機器上跑，CI 不跑，失敗要等到發版前 |
| **量測儀器閒置** | context-load 五個 family、0 筆 trace |
| **語意升級層未經真實驗證** | §6.2，且 v0.12.0 的版本門檻讓實際目標無法直接使用 |

### 10.3 一句話

**這個框架在「知道自己哪裡不對」這件事上做得比絕大多數專案好——`ASM-20260810-005` 和 `LESSON-VAL-001` 就是證明。目前的瓶頸不是發現問題的能力，是把已發現的問題排進佇列的紀律。**

---

## 11. 建議行動順序

| 順序 | 行動 | 理由 | 成本 |
|---|---|---|---|
| 1 | **把 `VALTIME-001` 與 `VALSNAP-001` 開成 Issue** | 兩個 HIGH、有完整證據、有 owner、零追蹤。`VALTIME-001` 直接違反框架的核心價值主張 | 30 分鐘 |
| 2 | **修 `VALTIME-001`**（行程群組／Job Object，逾時後證明無後代） | 「逾時最後印 `OK`」是 fail-closed 的破口 | 1~2 天 |
| 3 | **拆 `package-full-matrix`** | 單一檢查佔 release gate 64%（860 s）。先依 `VALTEST-001` 減少重複 fixture，再談預算 | 1~2 天 |
| 4 | **把 `nightly-full` 接上 scheduled CI** | 最貴的 profile 目前只靠人跑；排程執行能把 22 分鐘的失敗從發版前移到每晚 | 半天 |
| 5 | **補 context-load 的 `release` 與 `development` trace** | 五個版本沒讀過刻度。補完才知道 `ROADMAP.md`（30.6 KB）該不該拆 | 半天 |
| 6 | **#149 bake-off，判準用 §9.2** | 每週延後，要移植的 shell 就多一些 | 依範圍 |
| 7 | **決定驗證器/產品比的目標值** | 這是 owner 的產品決策，不是工程決策。1.54 可以是對的，但應該是選擇而非漂移 | 一次討論 |
| 8 | **upgrader 端到端實證** | 建議用 #168 的 CLI repo 當第一個乾淨目標，從 v0.12.0 初始化 | 依範圍 |

---

## 附錄：本次執行的查證指令

```bash
git log -1 --format="%H%n%ad" --date=iso
git rev-list --count v0.11.0..v0.12.0
python3 <解析 validation-profile-registry.sh 的 register_check 區塊>
sed -n '760,800p' .ai/scripts/check-all.sh                    # 輸出抑制實作
grep -rn "AI_CONTEXT_CHECK_TIMING|seconds" .dev/lessons/ .dev/workflows/2026-08-1*/
grep -rn "VALSNAP-001|VALTIME-001|VALTEST-001|VALCOST-001" .dev/    # 追蹤狀況
grep -rln "ai-context-upgrader" .dev/workflows/ .dev/assessments/   # 45 檔，逐條檢視
find .ai/evaluation/context-load -name "*.yaml" -o -name "*.json"   # 0 筆
python3 <逐檔 git show 統計互斥分類行數，三個基準>
curl -s .../actions/runs?per_page=60                          # CI 秒數
curl -s .../issues?state=open&per_page=100                    # 9 個 open issue
```

*本文所有數字皆可由上列指令在 `a4fd14f` 重現。標【未量測】者表示我沒有資料，不是估算為零。*
