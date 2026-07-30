# Repo 分析與評分報告

- `assessed_at`: `2026-07-30`
- `subject_head`: `98e90bb`（`main`）
- `method`: 直接讀檔與統計，未使用任何 skill、未執行 workflow
- `nature`: 對話式分析的存檔，非 `.dev/assessments/` 治理資產

> 本報告是應要求存放於根目錄的一次性分析輸出。它不進入發布封包（封包由 `.ai/distribution/profiles/` 的明確 allowlist 建立），也不宣稱等同於 `ASSESSMENT-ARTIFACT-POLICY.md` 定義的正式評估。

---

## 一、這個 repo 是什麼

它不是 .NET 專案，而是一個 **AI 協作 context 的發行框架來源庫**。`src/` 與 `tests/` 內只有 `readme.md`；實際的 .NET 產物散在 `.dev/standards/examples/`（約 70 個 `.cs` 範例）與 `tools/`（Roslyn analyzers，19 個 `.cs`）。

### 實測規模

| 項目 | 數字 |
| --- | --- |
| 全 repo 文字行數 | 137,620 |
| `.ai/`（可攜交付物） | 35,957 行 / 334 檔 |
| `.dev/`（治理與紀錄） | 99,935 行 / 937 檔 |
| └ `.dev/workflows/` | **60,524 行 / 510 檔** |
| └ `.dev/assessments/` | 8,036 行 / 60 檔 |
| Canonical skills | 15 個（另有 2 個 deprecated alias） |
| Python 自動化 / 契約測試 | 73 檔 / 44 個 test 檔 |
| CI gates | 4 條 workflow |
| 已發布版本 | v0.0.1 → v0.7.0（7 個），v0.8.0 planning |
| Commits / 作者 | 516 / 1 人（2026-04-08 起約 4 個月） |

**關鍵事實：整個 repo 約 50%（68,560 行）是「它自己治理自己」的過程紀錄**，而非可交付給下游的能力。這個比例本身不必然是缺陷，但決定了它的成本結構。

---

## 二、評分

| 面向 | 分數 | 依據 |
| --- | --- | --- |
| 工程紀律 / 治理嚴謹度 | **9.0** | 版本、provenance、release gate、fail-closed 驗證、handoff policy 齊備，且有 CI 實際執行 |
| 自動化與可驗證性 | **8.5** | 40+ validator、44 個 contract test、4 條 CI gate；規則不只寫在文件裡 |
| Skill 設計品質 | **7.5** | `skill.yaml` 的 constraints 克制精準，wrapper 維持薄層並明確指向 canonical |
| 文件與導覽 | **7.0** | 中英雙語、INDEX 完整；但入口層級深，`.dev/guides/` 就有 28 份 |
| 可攜性 / 導入成本 | **6.0** | package / apply / upgrade 三段機制完整，但需 Python 3.11+、PyYAML 6.0.3、.NET SDK 10.0.300+，升級要求 provenance |
| 交付價值密度 | **6.0** | .NET 可攜資產目前僅十餘份文件；相對治理機制比例偏低（見第五節：屬已排程的階段性選擇） |
| Context 效率 / 認知負擔 | **5.0** | `AGENTS.md` 常駐 242 行 / 1,801 字；一次 code review 需先讀 5 份、745 行參考鏈 |
| 自我維持性 / bus factor | **4.0** | 單一作者 516 commits，規則複雜度已超過一般團隊可直接接手的門檻 |

### 綜合：**6.9 / 10**

一句話總結：**治理工程的水準遠高於業界平均，但治理成本與當期交付價值的比例仍待收斂。**

---

## 三、對軟體開發的實際幫助

以下皆為讀檔可驗證、非紙上規則：

1. **消除 AI agent 的開場漂移**
   `AGENTS.md` + skill routing 表讓不同 runtime（Claude / Codex）在同一 repo 得到一致的規則、檔案位置與驗證方式。這解決的是多 agent 協作最昂貴的問題。

2. **fail-closed 的完成定義**
   `blocked-by-environment ≠ passed`、spec compliance 未選取即記 `not-applicable`、coverage 未達 100% 直接 fail。這直接堵住 LLM 最常見的「宣稱完成」失真。

3. **可跨 session 續作的 handoff**
   `workflow-plan.md` 的 Resume Checkpoint 記錄「上一個完成動作 / 下一個確切動作 / 已完成驗證 / git state」。換模型、換機器、開新對話都能接手，不依賴對話記憶。這是本次檢視中最有價值的單一設計。

4. **規則有機械驗證撐腰**
   `validate-workflow-artifacts.py`、`validate-git-commits.py`、`validate-source-governance.py` 等，讓規範不會腐爛成沒人遵守的文件。

5. **skill 邊界以負面清單劃定**
   例如 `code-reviewer` 明訂「只審查、評分、標記問題，不規劃重構、不實作修復、不定義目標架構」。負面清單比正面描述更能防止 agent 越界。

---

## 四、會造成開發人員困擾的地方

### 1. 流程開銷可以壓過工作本身（最嚴重）

以 PR #66 為例，實際工作是**把 4 個 Python 檔搬進 skill 資料夾**，伴隨產出：

```
workflow-plan.md                    88 行
tasks/SKILL-002-*.json              81 行
reports/remediation-report.md       64 行
workflow.yaml                       22 行
backlog/items/SKILL-002.yaml        38 行
provider-mappings/*.yaml            30 行
+ ROADMAP / INDEX 更新
─────────────────────────────────────────
≈ 330 行流程文件 / 一次檔案搬移
```

且 `AGENTS.md` 的 Workflow Gate 條件偏寬（「可能影響 source-of-truth、AI context、skill routing、wrapper sync 或跨多個 stage」），實務上容易被判定為需要 workflow 模式。

### 2. 起手閱讀成本高

- `AGENTS.md` 常駐 1,801 字，每次對話載入
- 一次 code review 的參考鏈：`CODE-REVIEW-INDEX.MD`(171) → `checklist-reference.md`(61) → `CODE-REVIEW-CHECKLIST.md`(215) → `output-contract.md`(57) → `ASSESSMENT-ARTIFACT-POLICY.md`(241) = **745 行**才開始看使用者的程式碼
- 人類要理解全貌，需讀 28 份 guide + 22 份 standards

### 3. 自創詞彙門檻

`disposition-gate`、`activation-gate`、`semantic customization ledger`、`provenance reconciliation`、`branch_segment`、`published_in` vs `completed_in` 等缺乏業界共通語義，新人與新 agent 第一次讀 ROADMAP 易誤解。

> 註：`CAP-001`（Technical Glossary And Terminology Capability Decision）已 resolved，但其決策結果未降低目前 ROADMAP 的閱讀門檻。

### 4. 環境門檻的失敗訊息不友善

Python 3.11+ 與 PyYAML 6.0.3 已在 `README.md:110` 與 `.ai/scripts/README.md` 寫明，但下游若使用 macOS 內建 python3（3.9），validator 直接拋 `ModuleNotFoundError: No module named 'tomllib'` / `'yaml'`，而非可讀的前置檢查訊息。本次分析實測撞到。

### 5. 歷史紀錄無汰除機制

510 個 workflow 檔全部留在活躍路徑。`SIMPL-001` 已正式評估過封存並**決定不封存**，理由紮實（v0.4.2 發布事故需靠歷史證據釐清；移動路徑會破壞可重現性與穩定引用）。此判斷正確，但代價是紀錄單調成長，且 `SIMPL-001` 已為此定義了 `v0.7.0-conditional` 的封存前置條件。

---

## 五、關於「.NET 內容偏薄」的定位修正

初次分析曾將此列為定位失衡。對照 backlog 後修正如下：

**這是已知且已排序的階段性選擇，不是疏漏。**

目前主線是**開發流程與 AI 協作機制**的調整；dotnet 技術管理議題已進入 backlog 排程：

| 項目 | 類別 | 狀態 | 主題 |
| --- | --- | --- | --- |
| `OBS-001` | `dotnet-architecture` | open | CrossCutting Observability Architecture Standard |
| `STD-001` | `standards-governance` | open | Standards Simplification Deliberation And Release Decision |
| `VAL-001` | `dotnet-validation` | resolved | Repository And Dependency Validation Gap Reassessment |

其餘 open 項目（`DEVWF-001`、`INIT-001`、`REL-004`）皆屬開發流程 / AI 協作主線，與當前重心一致。

因此**先把協作骨架與發布治理穩定、再回頭加厚技術棧內容**，是合理的排序。真正需要留意的不是「.NET 太薄」，而是：

- 骨架的固定成本（第四節第 1、2 點）會**乘以**未來每一次 .NET 內容的產出；
- `STD-001` 的 standards 簡化決策，會直接決定 `OBS-001` 這類技術標準加入時，是攤在既有的高開銷結構上，還是攤在收斂後的結構上。

**建議：讓 `STD-001` 的決策先於 `OBS-001` 落地**，避免新技術標準沿用尚未收斂的格式而放大成本。

---

## 六、建議（依投報比排序）

| 優先 | 建議 | 理由 |
| --- | --- | --- |
| 高 | 定義**輕量模式門檻**：例如「單一 PR、< 10 檔、不動 schema / CI / 發布路徑」直接走 direct mode，只留 commit message | `OPTIONAL-MINIMAL-WORKFLOW-MODE.md` 已存在，但未被 `AGENTS.md` 的 Workflow Gate 明確引用 |
| 高 | `STD-001` 決策先於 `OBS-001` 執行 | 避免新 dotnet 標準沿用未收斂格式，放大既有開銷 |
| 中 | 把「.NET 交付能力」與「框架治理機制」拆為兩個 package profile | 下游多半只想要前者，卻被迫承接後者 |
| 中 | 為 code review / implement 建立**單檔 digest**（745 行參考鏈壓成約 150 行入口 + 按需展開） | 直接降低每次任務的固定 context 成本 |
| 中 | validator 加 Python 版本前置檢查與可讀錯誤訊息 | 下游第一次執行的體驗決定採用率 |
| 低 | 為自創術語建立 glossary（延續 `CAP-001` 的決策結果） | 降低新人與新 agent 的誤解率 |

---

## 七、結論

- 若目標是**治理 AI 協作規範本身**：這是水準相當高的實作，約 **8.5 分**。
- 若目標是**讓開發者用 AI 更快交付 .NET 功能**：以目前形態，摩擦成本仍高於節省，約 **5 分**。

兩者差距來自它現階段更接近**流程治理產品**而非**開發加速工具**。就目前主線安排而言這是刻意的順序；風險在於骨架的固定成本會被之後每一份技術內容持續放大，因此收斂 gate 條件與 context 載入成本，投報比高於繼續增加治理機制。
