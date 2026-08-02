# Python 進入點先決條件完整盤點

> 翻譯說明：本文件是 `entrypoint-inventory.md` 的完整繁體中文（臺灣）翻譯，供 repository owner 查閱與進行設計決策。英文原文仍是 agent-facing 執行與交接的優先來源；若兩者出現差異，應以英文原文為準並同步修正本翻譯。所有指令、路徑與識別碼均維持原樣。

## 證據中繼資料

- `translation_status`: `complete`
- `translated_by`: `OpenAI Codex`
- `translated_at`: `2026-08-02T11:01:14+08:00`
- `source_document`: `.dev/workflows/2026-08-02-python-prerequisite-diagnostics/evidence/entrypoint-inventory.md`
- `source_updated_at`: `2026-08-02T10:53:29+08:00`
- `generated_by`: `OpenAI Codex repository-native inventory`
- `generated_at`: `2026-08-02T10:39:48+08:00`
- `updated_at`: `2026-08-02T10:53:29+08:00`
- `source_revision`: `2263744bb2dc876f8077547e961fc68be28b0074`
- `source_branch`: `codex/2026-08-02-python-prerequisite-diagnostics`
- `issue`: `https://github.com/YuChia-Wei/ai-collaboration-prompts-dotnet-backend/issues/69`
- `baseline_finding`: `ASM-20260730-001#AIC-004`

## 範圍與方法

- 納入 `.ai/scripts/**` 與 `.ai/assets/skills/*/scripts/**` 下已由 Git 追蹤的 Python 檔案。
- 先使用 repository-native 的 `git ls-files` 建立盤點，再直接檢查每個檔案是否具有 `__main__` 執行路徑，以分類能否直接執行。
- 依據 `.ai/distribution/profiles/dotnet-backend.yaml` 及其 source-only 排除規則分類可攜性。
- 依據直接 import 敘述與本機模組的直接 import 鏈分類目前的先決條件。
- 檢查根目錄入口文件、`.ai/scripts/README.md`、`.ai/distribution/templates/INSTALL.md`、skill 規格與參考資料、`.dev/standards/**`、`.dev/guides/**`、`.dev/releases/**`、`.github/workflows/**`、`.ai/scripts/check-all.sh` 及 `.ai/scripts/shell-assets.yaml` 中目前有效的指令與說明介面。
- 支援範圍分類不採用歷史 workflow 與 assessment 參照，但本次選定的 baseline finding 除外。
- 排除產品的 `src/**` 與 `tests/**` 目錄；本 repository 在本次範圍內沒有相關的產品實作。

盤點時先檢查 Codebase Memory MCP 索引。當時的索引在隱藏的 `.ai/**` 路徑下沒有回報任何 Python 相符項目，因此僅將其視為一次未取得結果的 discovery probe。以下數量與結論已依 `AICTX-EVIDENCE-001`，透過 Git 追蹤路徑、直接讀取檔案、manifest 與測試加以驗證。

## 重現方式

在 repository 根目錄使用 PowerShell 執行：

```powershell
$Tracked = git ls-files -- '*.py' |
  Where-Object { $_ -match '^\.ai/(scripts|assets/skills)/' }

$Entrypoints = foreach ($Path in $Tracked) {
  if ((Get-Content -Raw -LiteralPath $Path) -match '__name__\s*==\s*["'']__main__["'']') {
    $Path
  }
}

$Tracked.Count
$Entrypoints.Count
($Entrypoints | Where-Object { $_ -notmatch '/tests/' }).Count
($Entrypoints | Where-Object { $_ -match '/tests/' }).Count
```

使用下列檔案重新核對分類：

```powershell
Get-Content -Raw .ai/distribution/profiles/dotnet-backend.yaml
Get-Content -Raw .ai/scripts/shell-assets.yaml
Get-Content -Raw .ai/scripts/README.md
```

## 盤點摘要

| 類別 | 數量 | 與契約的關聯 |
| --- | ---: | --- |
| 範圍內已追蹤的 Python 檔案 | 74 | 所選根目錄下的完整 Git 追蹤盤點。 |
| 直接 `__main__` 進入點 | 70 | 每個檔案都可以當成指令執行。 |
| Production CLI 進入點 | 25 | user-facing 先決條件契約的主要候選範圍。 |
| 可直接執行的 test CLI 進入點 | 45 | 可由開發人員明確執行的指令，且經常由 aggregate runner 呼叫。 |
| 僅供 import 的支援模組 | 4 | 不應只因 shared bootstrap 會 import 這些模組，就將其變成獨立的 user-facing 指令。 |
| Portable production CLI | 12 | 會投射至下游套件，或保留為已發布的相容進入點。 |
| Source-only production CLI | 13 | 供維護、release、evaluation、migration 或 source-governance 作業使用。 |
| 直接或間接需要 PyYAML 的 production CLI | 23 | 目前可能在共用診斷執行前，就於 import 階段失敗。 |
| 僅使用標準函式庫的 production CLI | 2 | 若契約涵蓋所有 production CLI，仍需檢查 Python 最低版本。 |
| import `tomllib` 的 production CLI | 1 | 在 Python 3.10 或更舊版本中，會在進入 `main` 前失敗。 |

## Portable production 進入點

1. `.ai/assets/skills/software-development-orchestrator/scripts/validate-software-development-orchestrator-acceptance.py`
2. `.ai/scripts/plan-ai-context-package-apply.py`
3. `.ai/scripts/validate-ai-context-target.py`
4. `.ai/scripts/validate-ai-context.py`
5. `.ai/scripts/validate-assessment-artifacts.py`
6. `.ai/scripts/validate-dependency-versions.py`
7. `.ai/scripts/validate-file-disposition-manifest.py`
8. `.ai/scripts/validate-git-commits.py`
9. `.ai/scripts/validate-shell-assets.py`
10. `.ai/scripts/validate-software-development-orchestrator-acceptance.py`
11. `.ai/scripts/validate-workflow-artifacts.py`
12. `.ai/scripts/validate-workflow-handoff.py`

相容進入點會委派給 skill 所擁有的 acceptance validator；因此，除非在委派前先執行先決條件檢查，否則它也會承襲該 validator 的 PyYAML import 失敗。

## Source-only production 進入點

1. `.ai/assets/skills/ai-context-upgrader/scripts/compare-ai-context-versions.py`
2. `.ai/scripts/build-ai-context-package.py`
3. `.ai/scripts/measure-ai-context-load.py`
4. `.ai/scripts/plan-github-backlog-migration.py`
5. `.ai/scripts/prepare-ai-context-release.py`
6. `.ai/scripts/render-ai-context-release-notes.py`
7. `.ai/scripts/validate-ai-behavior-evaluation.py`
8. `.ai/scripts/validate-ai-context-package.py`
9. `.ai/scripts/validate-ai-context-release-state.py`
10. `.ai/scripts/validate-ai-context-versions.py`
11. `.ai/scripts/validate-repository-config-contract.py`
12. `.ai/scripts/validate-skill-transition.py`
13. `.ai/scripts/validate-source-governance.py`

這些進入點會從下游 payload 排除，但確實是維護者或 CI 會執行的操作。其中數個會寫入輸出或 release/package artifacts，因此排除它們會保留來源端診斷行為不一致的問題。

## 目前行為與風險

### 主機沒有 interpreter

在目前的 Windows 主機上，`python` 與 `python3` 會解析至 Windows App Execution Alias 可執行檔，但主機並未安裝 Python runtime。因此，直接執行 `python <entrypoint>.py` 時，會在作業系統 launcher 階段失敗，repository 還來不及執行 Python bootstrap 或印出自己的訊息。

這形成兩個不同的診斷層次：

1. 非 Python 的 shell 或 PowerShell launcher 可以偵測沒有可用 interpreter 的情況、列出曾嘗試的指令、說明需要 Python 3.11+，並在呼叫任何 Python 進入點前停止。
2. Python interpreter 一旦啟動，shared Python bootstrap 就可以在 import PyYAML、`tomllib`、本機模組或可寫入程式碼前，拒絕不支援的版本或缺少 dependency 的環境。

因此，僅標準化 Python preamble，無法讓缺少 interpreter 的直接指令改由 repository 提供診斷。若要完整涵蓋這台電腦實際出現的狀態，核准後的呼叫契約必須包含非 Python launcher 或 aggregate runner；當沒有 Python 可執行檔時，直接呼叫 `.py` 的原始方式仍受作業系統行為控制。

### Aggregate runner

`.ai/scripts/check-all.sh` 依序解析 `AI_CONTEXT_PYTHON`、`python`、`python3`，且只接受 Python 3.11 或更新版本。其失敗訊息會說明最低版本並指向 `requirements.txt`，但目前不會回報選定的可執行檔、偵測到但不支援的版本、缺少的 dependency 名稱，或結構化的 mutation 前結果。

### Package planner

`.ai/scripts/plan-ai-context-package-apply.py` 已能捕捉缺少 `yaml` import 的情況、指出 `PyYAML==6.0.3`、印出 `python -m pip install -r requirements.txt`、以狀態碼 2 結束，並在 import 本機 apply 模組前停用 bytecode；它也具有使用 `python -S` 的解壓後套件測試覆蓋。

這是目前最完整的直接診斷，但仍屬於一次性的獨立契約。它不會在 dependency import 前檢查或回報不支援的 interpreter，也不會回報選定的可執行檔／版本，或明確輸出尚未 mutation 的狀態。

### 其他可直接執行的 production CLI

- 大多數使用 PyYAML 的程式會在 module load 時 import `yaml`；dependency 不存在時，會直接顯示 interpreter 原始的 `ModuleNotFoundError`。
- `validate-ai-context.py` 會在 `main` 前 import `tomllib`，因此在 Python 3.10 或更舊版本會直接產生 interpreter 原始的缺少模組錯誤。
- `validate-ai-context-target.py`、package builder/validator、backlog migration planner 與相容 acceptance validator 等間接進入點，可能在 import 另一個會 import PyYAML 的本機模組時失敗。
- 僅使用標準函式庫的 CLI，目前可能在低於文件所載 Python 最低版本的環境中執行並回報成功；除非稍後剛好使用到該版本沒有提供的語言或 runtime 功能，才會失敗。

### Mutation 邊界

- 下游最關鍵的寫入路徑是 `plan-ai-context-package-apply.py --apply`；`--plan-output` 也會寫入 plan 檔案。
- Source-only 的 build、measurement、backlog migration、release-note rendering 與 deterministic evaluation 指令可能寫入輸出。
- 若未及早停用 bytecode，import 本機 Python 模組可能建立 `__pycache__`。現有 package planner 會明確防止這件事，因為解壓後的 envelope 受 checksum 管控。
- Read-only validator 依設計不會修改其驗證對象，但若沒有先檢查 Python 最低版本，仍可能在不支援的 interpreter 下錯誤宣稱驗證成功。

## 此 finding 所隱含的工作類別

1. 定義並登錄受支援的 Python 進入點範圍。
2. 定義標準診斷 schema：可執行檔、偵測到的版本、最低需求版本、dependency/import package、認可的復原指令、結束狀態碼，以及 mutation 前狀態。
3. 選擇能區分「非 Python 的 interpreter 缺失偵測」與「Python 層級的版本／dependency 檢查」的交付架構，並讓它適用於根目錄 shared scripts、skill-owned scripts、相容進入點、解壓後套件及已安裝的目標 repository。
4. 調整 import 順序與 bytecode 行為，讓診斷在 `tomllib`、PyYAML、本機 dependency 模組或目標寫入前執行。
5. 保持解壓後 envelope 的 package projection 與 checksum 行為。
6. 新增可重現且結果固定的不支援版本與缺少 dependency 測試，並為可寫入路徑加入「沒有寫入」的 assertion。
7. 同步 aggregate runner 的一致性、有效指令登錄、package tests、文件，以及所選範圍影響到的所有相容契約。
8. 執行聚焦驗證、package/apply regression checks、aggregate gates，以及獨立的 remediation 後 AI-context assessment。

## D-001 的範圍選項

### 選項 A——所有 production CLI（建議）

涵蓋 portable 與 source-only 介面中的全部 25 個非測試 `__main__` 進入點。45 個可直接執行的 test CLI 與 4 個僅供 import 的模組，不納入 user-facing 契約。

- 優點：每個受維護的操作都有一個容易理解的共同邊界；同時處理 Issue mixed scope 的兩個部分。
- 成本：production code 整合範圍最大，而且必須區分來源端與解壓後套件的復原說明文字。
- 剩餘邊界：直接執行 test 指令時，仍可能出現原始環境 import 錯誤；這會被記錄為開發者測試行為，而不是受支援的 runtime 診斷。

### 選項 B——所有可執行的 Python 檔案

涵蓋全部 70 個直接 `__main__` 路徑，包括 45 個測試。

- 優點：這是對「每個可直接執行 Python 指令」最強、最字面的解讀。
- 成本：變更規模會大幅增加且產生更多干擾，或者必須強制使用 test launcher；先決條件行為也會與每個 test module 及相容 test wrapper 耦合。
- 剩餘邊界：僅供 import 的模組仍在指令契約之外。

### 選項 C——僅 portable production CLI

涵蓋會投射至下游 payload，或保留為 portable 相容路徑的 12 個 production 進入點。

- 優點：變更範圍最小，並最集中改善下游使用者的首次執行體驗。
- 成本：13 個 source-only 維護者／CI 操作仍會維持不一致，其中包含數個可寫入指令；這只能部分處理 Issue 的 `scope:mixed` 標籤與 source runner 比較問題。

## 目前結論邊界

本盤點只建立候選範圍與影響，尚未選定任何 D-001 選項、尚未核准任何實作架構，也沒有修改任何 production 檔案。目前主機狀態證明：repository 的 Python 程式無法診斷 interpreter 完全不存在的情況；是否新增受支援的非 Python launcher，仍屬於 D-002 的 owner decision。
