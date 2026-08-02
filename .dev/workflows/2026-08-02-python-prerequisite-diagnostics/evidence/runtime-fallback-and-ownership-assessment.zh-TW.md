# Python runtime 備案與進入點 ownership 評估

> 翻譯說明：本文件是 `runtime-fallback-and-ownership-assessment.md` 的完整繁體中文（臺灣）翻譯，供 repository owner 查閱與進行設計決策。英文原文仍是 agent-facing 執行與交接的優先來源；若兩者出現差異，應以英文原文為準並同步修正本翻譯。所有指令、路徑與識別碼均維持原樣。

## 證據中繼資料

- `translation_status`: `complete`
- `translated_by`: `OpenAI Codex`
- `translated_at`: `2026-08-02T12:03:33+08:00`
- `source_document`: `.dev/workflows/2026-08-02-python-prerequisite-diagnostics/evidence/runtime-fallback-and-ownership-assessment.md`
- `generated_by`: `OpenAI Codex repository-native and host-local assessment`
- `generated_at`: `2026-08-02T12:03:33+08:00`
- `source_revision`: `d27fb8adbaf890f9f926c2de6bf66aa6917a83d0`
- `source_branch`: `codex/2026-08-02-python-prerequisite-diagnostics`
- `issue`: `https://github.com/YuChia-Wei/ai-collaboration-prompts-dotnet-backend/issues/69`
- `baseline_finding`: `ASM-20260730-001#AIC-004`
- `decision_state`: `D-001 已核准選項 A 與 portable-first 順序；所有 fallback 與 ownership 建議均尚未核准`

## 使用的證據

- 以 `.ai/scripts/check-all.sh`、`.ai/scripts/README.md`、`.ai/scripts/shell-assets.yaml` 與 `requirements.txt` 核對目前的 resolver、安裝、gate 及 shell 契約。
- 以 `.ai/distribution/profiles/dotnet-backend.yaml` 與 `.ai/distribution/templates/INSTALL.md` 核對 portable/source-only 分類及解壓後套件指令。
- 以 `.ai/assets/skills/README.MD` 與 `.ai/scripts/tests/test_skill_script_colocation.py` 核對目前 canonical script ownership 規則及已鎖定的相容路徑。
- 直接在本機探測 `python`、`python3`、`python3.14`、`codex`、`claude`、`chatgpt` 指令，以及目前 Codex bundled runtime 的中繼資料。
- 使用官方產品文件核對公開說明的安裝先決條件：[Codex CLI npm 安裝](https://openai.com/index/introducing-upgrades-to-codex/)、[ChatGPT Windows 應用程式需求](https://help.openai.com/en/articles/9982051-using-the-chatgpt-windows-app)，以及 [Claude Code 設定需求](https://docs.anthropic.com/en/docs/claude-code/getting-started)。

盤點時先探測 Codebase Memory MCP 索引，但目前 graph 仍會略過隱藏 `.ai/**` 路徑下的 Python 程式。因此，依 `AICTX-EVIDENCE-001`，ownership 與行為結論改以直接追蹤檔案、manifest、測試及本機探測結果為準。

## 已核准的 D-001 範圍與順序

Owner 選擇選項 A：全部 25 個 production `__main__` CLI 介面都納入範圍；45 個可直接執行的 test CLI 與 4 個僅供 import 的模組，仍不納入 user-facing 先決條件契約。

實作必須拆成兩個有先後順序的批次：

1. Portable/downstream 批次：會投射至下游套件，或保留為 portable 相容路徑的 12 個 production CLI。
2. Source-only 批次：僅在本 repository 使用的 13 個維護者、CI、release、provider、evaluation 與 source-governance CLI。

Portable 批次必須先完成設計、實作與驗證，才能開始 source-only 批次。這項順序並未核准 fallback 架構、自動安裝、provider runtime discovery、OS-native launcher 或 ownership 移動。

## 修正後的本機觀察

先前「主機沒有安裝 Python runtime」的說法範圍過大。精確觀察結果如下：

| 探測項目 | 觀察結果 | 對設計的影響 |
| --- | --- | --- |
| `python` | 解析至尚未配置的 Windows App Execution Alias，無法啟動 Python。 | 目前的通用指令候選不可用。 |
| `python3` | 解析至尚未配置的 Windows App Execution Alias，無法啟動 Python。 | 目前的 fallback 候選也不可用。 |
| `python3.14` | 解析至 `<user-home>\.local\bin\python3.14.exe`，可啟動 Python 3.14.1，且 `sys.prefix` 顯示由 uv 管理。 | PATH 上已有可發現的版本化 interpreter，但 `check-all.sh` 不會探測版本化指令名稱。 |
| `python3.14 -c "import yaml"` | 以 `ModuleNotFoundError` 失敗。 | Interpreter discovery 與 dependency readiness 是兩道不同的 gate。 |
| 目前 Codex bundled Python | 本機私有路徑回報 Python 3.12.13；在另行安裝前沒有 PyYAML。 | 工具內附 runtime 可能解決 interpreter 啟動，但不保證具備 repository dependency。 |
| `codex`／`claude`／`chatgpt` | 已安裝 Codex 與 Claude 指令；沒有登錄 `chatgpt` 指令。 | Agent 產品是否存在取決於主機，且不能因此證明它提供可重用的 Python runtime 契約。 |

由 uv 管理的 `python3.14.exe` 剛好與其他可執行檔放在 `.local/bin`；目錄相鄰並不是 ownership 證據。Codex bundled runtime 也只能確認這一台電腦與目前 bundle version 的情況。已查閱的官方安裝頁面並未發布穩定、跨產品的 Python 可執行檔路徑，也未承諾預裝 PyYAML。因此，若將 provider 私有路徑當成 repository 預設契約，會是沒有 portability 證據支持的推論。

## Repository 目前的 fallback 契約

1. `check-all.sh` 將 `AI_CONTEXT_PYTHON` 設為最高優先來源。
2. 未提供 override 時，只探測 `python` 與 `python3`，並要求 Python 3.11 或更新版本。
3. 沒有任何候選通過版本探測時，aggregate gate 會在執行 validator 前失敗。
4. Dependency 由 owner 手動安裝至自行選擇的環境，使用 `python -m pip install -r requirements.txt`；repository script 不會自動安裝。
5. 解壓後套件會帶有同樣 pin 住的 `requirements.txt`，並記載直接 Python 指令。
6. 目前沒有 Python 專用的 PowerShell launcher，也沒有 discovery Codex、Claude Code、ChatGPT Desktop、uv 或其他工具私有 runtime 的 repository 契約。
7. `check-all.sh` 是目前唯一非 Python 的先決條件 resolver。直接執行 Python 進入點時不會經過它。

## Fallback 選項評估

| 作法 | 缺少 interpreter | 缺少 PyYAML | Mutation／信任影響 | 評估 |
| --- | --- | --- | --- | --- |
| 不執行並 fail closed | 只能由非 Python launcher 偵測 | Python 啟動後可以偵測 | 不會 mutation；結果固定且可離線 | 所有已核准 recovery 候選都失敗後，必須採用的終止行為。 |
| 明確的 `AI_CONTEXT_PYTHON` override | Owner 提供路徑時可以解決 | 只有選定環境已就緒才可解決 | 不會自動 mutation；信任來源由 owner 控制 | 保留為最高優先且受支援的來源。 |
| 探測通用及版本化指令 | 經常可以；這台電腦會找到 `python3.14` | 無法單獨解決 | Read-only 探測；必須定義結果固定的順序 | 建議作為預設 discovery 擴充。 |
| Discovery agent tool bundled runtime | 有時可以 | 不保證；目前 Codex bundle 沒有 PyYAML | 私有路徑、更新漂移、sandbox／permission 邊界、跨 provider 契約不清楚 | 只考慮明確 opt-in 的 provider adapter 或 owner 提供的路徑；不要 hard-code 成預設值。 |
| 明確且隔離的 dependency bootstrap | 必須先有 interpreter | 可以 | 會使用網路並寫入檔案；可限制在專用環境與明確指令內 | 可作為後續 opt-in recovery mode，但不能是 validator 的隱含副作用。 |
| 靜默安裝 dependency 或 Python | 可能可以 | 可能可以 | 涉及網路、supply chain、權限、環境 ownership、清理、CI 與重現性風險 | 不建議作為預設行為。 |
| OS-native launcher 委派給 Python | 可以 | 可以在委派前探測 | 增加 PowerShell／POSIX 維護成本，但 validator 語意仍留在 Python | 適合作為受支援 human-facing 指令的候選架構。 |
| 用 OS-native script 完整重寫 validator | 可以 | 不再需要 Python | 重複 25 份行為契約，並導致各 OS 間的語意漂移 | 除非專案有意移除 Python dependency，否則不採用。 |
| 要求已安裝的 AI agent 執行 script | Agent 可能找到 runtime | Agent 可能在核准後安裝或配置 | Availability 與 authorization 不固定；CI 與沒有 agent 的使用者無法使用 | 可作為輔助，但不是 validator 的先決條件契約。 |

## 尚未核准的分層架構候選

一個範圍受控的設計候選如下：

1. OS-native launcher 只負責 discovery 與先決條件診斷。
2. Discovery 依固定順序檢查 owner 明確 override、穩定的 host commands，再檢查已核准的 optional adapters。
3. 每個候選都必須先探測可執行檔 identity、Python 3.11+ 與 required imports，才能被選用。
4. 沒有任何就緒候選時，必須在 validator import 或 target mutation 前 fail closed。
5. 建立環境或安裝 dependency 必須是另一個明確操作，而且不得修改 agent 產品管理的 runtime。
6. 選定的 Python interpreter 只執行一份 canonical Python implementation；PowerShell 與 POSIX launcher 不重複 validator 語意。

這個候選只供討論使用。D-002 與 D-004 仍是 pending。

## 目前的 script ownership 規則

Canonical registry 目前規定：只屬於一個 skill 的行為，必須由且僅由一個 owning skill 擁有。Multi-skill、provider、release、package、workflow 及整個來源 repository 使用的 automation，則保留在 `.ai/scripts/`。已發布的舊路徑，只能以 thin compatibility entrypoint 的形式留在該處。

Colocation contract 已經強制兩個 canonical skill-owned production script，以及 orchestrator acceptance validator 的根目錄相容路徑。變更此規則或移動路徑，會影響 skill specs、package projection、相容指令、測試、文件及可能的下游使用者。

## 25 個 CLI 的初步 ownership 分類

| 進入點 | Distribution | 初步 canonical ownership | 理由 |
| --- | --- | --- | --- |
| `.ai/assets/skills/software-development-orchestrator/scripts/validate-software-development-orchestrator-acceptance.py` | portable | 維持 skill-owned | Acceptance 行為只由一個 canonical skill 擁有。 |
| `.ai/scripts/plan-ai-context-package-apply.py` | portable | 維持 repo-common | Package apply 同時供 initialization 與 upgrade lifecycle 使用，跨越單一 skill ownership。 |
| `.ai/scripts/validate-ai-context-target.py` | portable | 維持 repo-common | Target provenance/customization validation 由 init、upgrade、governance 與 audit lifecycle 共用。 |
| `.ai/scripts/validate-ai-context.py` | portable | 維持 repo-common | Repository-wide navigation、wrapper、language、registry 與 routing 契約跨越多個 skill。 |
| `.ai/scripts/validate-assessment-artifacts.py` | portable | 維持 repo-common | Assessment 產出與 remediation／verification coordination 分屬不同 owner。 |
| `.ai/scripts/validate-dependency-versions.py` | portable | 維持 repo-common | 同時執行 repository、CI、package、Python 與 .NET dependency 契約。 |
| `.ai/scripts/validate-file-disposition-manifest.py` | portable | 維持 repo-common | Disposition evidence 由 remediation、release 與 downstream migration 共用。 |
| `.ai/scripts/validate-git-commits.py` | portable | 維持 repo-common | Git policy 適用於所有 workflow 與 skill。 |
| `.ai/scripts/validate-shell-assets.py` | portable | 維持 repo-common | 驗證 repository-wide shell orchestration 與 compatibility assets。 |
| `.ai/scripts/validate-software-development-orchestrator-acceptance.py` | portable | 保留 thin compatibility path | Canonical 行為仍由 skill 擁有；這個已發布的根目錄路徑只負責委派。 |
| `.ai/scripts/validate-workflow-artifacts.py` | portable | 維持 repo-common | Workflow metadata 與 task 契約由多個 workflow-owning skill 共用。 |
| `.ai/scripts/validate-workflow-handoff.py` | portable | 維持 repo-common | Cross-runtime、cross-model 及 cross-skill handoff 屬於 repository-wide 行為。 |
| `.ai/assets/skills/ai-context-upgrader/scripts/compare-ai-context-versions.py` | source-only | 維持 skill-owned | Comparison 是單一 owner 的 upgrader capability，而且已有固定路徑 contract test。 |
| `.ai/scripts/build-ai-context-package.py` | source-only | 維持 repo-common | Source release/package production 跨越 skill 與 distribution ownership。 |
| `.ai/scripts/measure-ai-context-load.py` | source-only | 維持 repo-common | 測量 source-wide runtime、routing、release、handoff 及 development traces。 |
| `.ai/scripts/plan-github-backlog-migration.py` | source-only | 維持 repo-common | Provider migration 跨越 workflow 與 backlog ownership，而非單一 skill。 |
| `.ai/scripts/prepare-ai-context-release.py` | source-only | 維持 repo-common | 協調 release state、gates、Git state 與 owner handoff。 |
| `.ai/scripts/render-ai-context-release-notes.py` | source-only | 維持 repo-common | Release rendering 會使用 repository-wide release/package truth。 |
| `.ai/scripts/validate-ai-behavior-evaluation.py` | source-only | 維持 repo-common | Deterministic evaluation 橫跨 capability 與 release 契約。 |
| `.ai/scripts/validate-ai-context-package.py` | source-only | 維持 repo-common | Package-envelope validation 是整個 distribution 的契約。 |
| `.ai/scripts/validate-ai-context-release-state.py` | source-only | 維持 repo-common | Release-state gate 橫跨 repository、Git、package 與 hosted evidence。 |
| `.ai/scripts/validate-ai-context-versions.py` | source-only | 維持 repo-common | Source release registry validation 會委派 shared target validation，並跨越多個 lifecycle owner。 |
| `.ai/scripts/validate-repository-config-contract.py` | source-only | 維持 repo-common | Repository configuration ownership 屬於 source-wide 行為。 |
| `.ai/scripts/validate-skill-transition.py` | source-only | 維持 repo-common | Transition compatibility 必然跨越多個 skill。 |
| `.ai/scripts/validate-source-governance.py` | source-only | 維持 repo-common | Discovery 並執行 source-wide governance registry 與 checks。 |

依實體進入點計算的初步結果：2 個 canonical skill-owned script、1 個指向 skill-owned script 的 repo-level thin compatibility route，以及 22 個 repo-common script。

## Ownership 熱點

- Shared prerequisite resolver/bootstrap 同時服務 skill-owned 與 repo-common CLI，因此依目前 ownership 規則，應是 `.ai/scripts/` 下的 repo-common component，並在需要時投射至下游套件。
- Skill-owned CLI 應依賴 shared prerequisite component，但不應把自己的 domain behavior 移交給 repository-common 層。
- 現有根目錄 orchestrator acceptance wrapper 應保持 thin；若直接在 wrapper 中加入 prerequisite domain logic，會形成兩個 behavior owner。
- 若要將初步分類為 repo-common 的 22 個 script 移入某一個 skill，必須先證明其他使用 lifecycle 只是 adapter，而不是共同 owner。
- 若要把兩個 canonical skill script 移回 `.ai/scripts/`，必須修改 canonical ownership policy 及其 deterministic colocation test，不能只搬動檔案。

## 等待 Owner 決定的事項

1. `D-002A`：找不到完全就緒的 interpreter/dependency 環境時，預設採取什麼動作。
2. `D-002B`：可信任的 discovery 來源及固定候選順序，包括是否允許 provider-specific adapter。
3. `D-002C`：受支援的 OS-native launcher 範圍與呼叫契約。
4. `D-004`：dependency recovery 指令，以及是否提供明確且隔離的 bootstrap mode。
5. `D-006`：最終 canonical ownership 分類、shared prerequisite component placement、package projection 與 compatibility routes。

本評估中的任何建議，都不代表已授權實作或自動修改環境。
