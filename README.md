# AI Collaboration Framework

AI 協作知識庫與 .NET Backend Context Framework

[English](README.en.md)

本檔案是 `README.md` 所代表的來源庫人類導覽身分之繁體中文（台灣）canonical 版本；README.en.md 是對應的英文翻譯。

本專案是一個可攜式的 AI 協作框架來源庫，將軟體開發實務、可重用的 Agent context、skills、sub-agent prompts 與協作流程集中管理。它目前保留並發展 .NET / C# 後端的專門能力，同時把可跨技術棧使用的協作規則抽離為通用內容。

來源庫、公開產品、framework release、technology profile 與 archive/package 是不同識別類別；目前的 machine-readable 權威與相容 alias 定義在 [identity registry](.ai/distribution/identity-registry.yaml)。這份 registry 不決定 CLI command、binary、installer 或外部 toolchain repository 名稱。

這不是特定產品的應用程式或範例系統。它的目的，是讓團隊能把經過整理與驗證的 AI 協作能力帶入新舊專案，並由目標專案本身的程式碼、設定與文件建立該專案的真實脈絡。

> 根目錄 README 是此來源庫的人類導覽文件，不是可攜式發佈封包的一部分。封包由明確 allowlist 建立，並刻意排除根目錄 README，因此此來源庫介紹不會被帶入目標專案。

## 專案定位

| 這個專案是 | 這個專案不是 |
| --- | --- |
| 可重複採用的 AI 協作知識庫與框架來源 | 單一產品、微服務或 Web API 的完整實作 |
| 通用軟體開發協作規則與 .NET 後端專門能力的集合 | 把來源庫的 requirement、spec、workflow 或決策直接複製成目標專案事實的工具 |
| 產出可攜式 AI context 發佈封包的受治理來源庫 | 要安裝到目標專案的原始碼快照 |

## 它協助解決的問題

- 讓 AI Agents 在開始工作前取得一致的協作規則、文件位置與驗證方式。
- 將需求、規格、架構、實作、測試、審查與交接的工作方法整理成可路由的 skills 與流程。
- 區分「可跨專案重用的知識」與「只能由目標專案決定的事實」，避免舊專案脈絡污染新專案。
- 保留 .NET 後端開發的實作、設計與審查經驗，讓 DDD、Clean Architecture、CQRS 與 message-driven backend 的討論有一致起點。

## 適用情境

本專案特別適合希望建立一致 AI 協作方式的團隊或個人，例如：

- 要在新專案或既有專案導入可維護的 AI Agent context。
- 需要把 .NET / C# 後端架構與實作慣例提供給多個 Agent 使用。
- 希望讓需求、規格、實作、測試與程式碼審查有清楚的責任邊界與交接方式。
- 想保留可攜式框架規則，同時避免覆寫目標專案既有的業務、架構與營運事實。

## 快速導覽

| 你的目的 | 從哪裡開始 |
| --- | --- |
| 了解此來源庫的架構與範圍 | [`.dev/ARCHITECTURE.md`](.dev/ARCHITECTURE.md) |
| 尋找可用的 AI skills | [`.ai/assets/skills/README.MD`](.ai/assets/skills/README.MD) |
| 了解人類可閱讀的協作指南 | [`.dev/guides/ai-collaboration-guides/INDEX.MD`](.dev/guides/ai-collaboration-guides/INDEX.MD) |
| 讓 Agent 在此來源庫中正確協作 | [`AGENTS.md`](AGENTS.md) |
| 探索 target-selected 的 .NET 機械式驗證 recipe | [`.ai/assets/tech-stacks/dotnet-backend/tooling/on-demand-mechanical-validation/`](.ai/assets/tech-stacks/dotnet-backend/tooling/on-demand-mechanical-validation/) |
| 取得或升級可攜式框架版本 | [`.dev/releases/INDEX.MD`](.dev/releases/INDEX.MD) |

## 核心內容

### 通用 AI 協作內容

通用內容可跨語言、框架與產品型態重複使用，涵蓋：

- AI 協作流程、workflow gate 與交接規則。
- Git commit、驗證、需求、規格、ADR 與 review 的工作方式。
- Skill routing、sub-agent 協作與可追溯的執行邊界。
- 系統與軟體架構，以及 DDD、Clean Architecture、CQRS 等概念層指引。

### .NET Backend 專門能力

目前保留的技術棧 profile 聚焦於 .NET / C# 後端，包括：

- Web API、worker 與 consumer 類型的後端專案結構。
- DDD、Clean Architecture、CQRS、Hexagonal Architecture 與 message-driven backend 的實務。
- WolverineFx、Dapper、EF Core、PostgreSQL、RabbitMQ 與 Kafka 等常見後端組合。
- .NET 後端的架構設計、實作切片與 code review 指引。

框架預設不提供可編譯的 .NET provider、專案或 SDK pin。若目標專案需要 Roslyn analyzer 或 projection registration test，必須由 target owner 明確選取後，依 [on-demand recipe](.ai/assets/tech-stacks/dotnet-backend/tooling/on-demand-mechanical-validation/) 在目標庫建立並驗證。DBA1001–DBA1017 對應、severity 範例與 bounded snippets 僅為 `reference-only`；canonical standards 仍是語意 owner。

目標庫自行負責 SDK、target framework、Roslyn／測試套件版本、專案 wiring、severity、CI、相容性與新鮮 evidence。Recipe 檔案存在不代表 capability 已啟用，也不建立 framework release 的 .NET SDK 依賴。

## 主要目錄

| 路徑 | 用途 |
| --- | --- |
| `.ai/` | Agent-facing 的可重用 AI context、canonical assets、scripts 與 skill specs。 |
| `.ai/assets/shared/` | 跨技術棧的 prompt fragments、規則與可重用材料。 |
| `.ai/assets/tech-stacks/dotnet-backend/` | .NET C# backend Web API 專用 context。 |
| `.ai/assets/skills/` | Canonical skill specs 與 skill registry。 |
| `.ai/assets/sub-agent-role-prompts/` | Sub-agent role prompts 的 canonical source。 |
| `.agents/skills/` | Codex 與目前 runtime 的 skill wrappers。 |
| `.claude/skills/` | Claude-compatible skill wrappers。 |
| `.dev/` | 人類可閱讀的 standards、guides、requirements、specs、release 與 workflow records。 |
| `.dev/releases/` | 發佈版本、相容性宣告與遷移說明。 |
| `AGENTS.md` | Codex 與通用 Agent 的 canonical root collaboration guide。 |
| `CLAUDE.md` | 匯入 `AGENTS.md` 的 Claude Code project-memory 薄入口。 |

## 安裝與升級

請從已發佈版本取得對應的可攜式 AI context 封包，而非直接複製此來源庫。封包是 versioned framework payload，不是整個 repository 的覆蓋式快照。

| 目標狀態 | 正確流程 |
| --- | --- |
| 第一次在空白或既有專案導入 framework | 依下方「乾淨安裝」用 package planner 套用，再使用 `ai-context-init`。 |
| 已初始化且有可信的 provenance，並且 release guide 支援該升級路徑 | 依下方「版本升級」先用 package planner，再使用 `ai-context-upgrader`。 |
| 沒有可信的來源版本、provenance 不完整，或版本跨度不受支援 | 停止自動升級；採人工 baseline reconciliation 或乾淨安裝式導入，不能猜測舊版。 |

### 乾淨安裝

#### 0. 先準備正確的目錄與證據

將下載的 ZIP / tar.gz **解壓縮在目標專案之外**。`PACKAGE_ROOT` 指的是解壓後、包含 `requirements.txt`、`metadata/` 與 `payload/` 的 envelope root，不是 ZIP 檔所在目錄。

```text
~/gitproj/
├── ai-context-package-0.7.0/
│   └── ai-context-dotnet-backend-v0.7.0/  # PACKAGE_ROOT
└── my-project/                            # TARGET_ROOT
```

不要將封包直接解壓縮到 `my-project`，也不要手動逐檔複製 `payload/` 內容。這會略過 checksum、套件選擇、reconciliation 與套用收據，並可能把 envelope metadata 誤放進目標專案。

開始前請確認：

1. 目標專案是 Git repository，worktree 乾淨，並已記錄目前 commit，方便回復。
2. 已下載發布包及相鄰的 `.sha256` sidecar；先比對 archive 的 SHA-256 與 sidecar 中的值。
3. 可使用 Python 3.11 或更新版本。
4. 已閱讀目標版本的 `migration-guide.md`。即使是乾淨安裝，也要確認 optional provider 與 profile 的預設選擇。

可攜式 package CLI 會在執行前驗證 Python 與其受治理的相依套件。被阻擋的 direct command 會在 stderr 輸出一行可採取行動的訊息；POSIX 與 PowerShell launcher 也支援 `--diagnostic-format=json`，以輸出一個 machine-readable stdout object。診斷不會安裝套件或變更 target。請手動依照回報的 recovery command 處理，或使用 `AI_CONTEXT_PYTHON` 選取已準備好的 interpreter。關於 discovery order 與 local routine-validation policy，請見 [Python prerequisite diagnostics guide](.dev/guides/ai-collaboration-guides/PYTHON-PREREQUISITE-DIAGNOSTICS-GUIDE.zh-TW.md)。

在 PowerShell 可用下列方式先設定路徑與檢視 checksum（兩個值必須相同）：

```powershell
$Archive = 'C:\Downloads\ai-context-dotnet-backend-v0.7.0.zip'
$Checksum = 'C:\Downloads\ai-context-dotnet-backend-v0.7.0.zip.sha256'
$PackageRoot = 'C:\gitproj\ai-context-package-0.7.0\ai-context-dotnet-backend-v0.7.0'
$TargetRoot = 'C:\gitproj\my-project'

Get-Content $Checksum
(Get-FileHash $Archive -Algorithm SHA256).Hash
```

在 macOS 或 Linux，將上例路徑換成目錄後，可使用 `shasum -a 256 <archive>` 與 sidecar 的第一欄比較。

#### 1. 先執行 dry-run，絕不直接覆蓋

在 `PACKAGE_ROOT` 執行。`--plan-output` 是選用但建議的審查檔，且必須放在 package 與 target 以外的位置。

```powershell
Set-Location $PackageRoot
python --version
python -m pip install -r requirements.txt

python .\payload\.ai\scripts\plan-ai-context-package-apply.py `
  --package-root . `
  --target-root $TargetRoot `
  --plan-output "$env:TEMP\ai-context-v0.7.0-clean-install-plan.yaml"
```

在 Bash 或 zsh，可使用下列等效命令：

```bash
PACKAGE_ROOT="$HOME/gitproj/ai-context-package-0.7.0/ai-context-dotnet-backend-v0.7.0"
TARGET_ROOT="$HOME/gitproj/my-project"
PLAN_OUTPUT="/tmp/ai-context-v0.7.0-clean-install-plan.yaml"

cd "$PACKAGE_ROOT"
python3.11 --version
python3.11 -m pip install -r requirements.txt
python3.11 payload/.ai/scripts/plan-ai-context-package-apply.py \
  --package-root . \
  --target-root "$TARGET_ROOT" \
  --plan-output "$PLAN_OUTPUT"
```

預設會選取 `dotnet-backend` profile；`repo-backlog` 是預設停用的 optional provider。只有目標 owner 明確需要它時，才在 **乾淨安裝** 的 dry-run 與 apply 同時加上 `--enable-provider repo-backlog`。不要因為升級遇到問題而臨時啟用它。

仔細審查 plan 中的 selection、`add`、`replace`、`remove`、`rename` 與 `reconcile` 項目。此步驟只產生計畫，不會寫入目標專案。

#### 2. 確認計畫後才套用

只有在 dry-run 已確認、目標 worktree 仍是同一個乾淨起點時，才執行 apply。對每個 reconciliation 項目加入 `--acknowledge`；確認某個 ID 只會略過該項目，**不代表**授權覆寫或刪除 target-owned 檔案。

```powershell
Set-Location $PackageRoot

python .\payload\.ai\scripts\plan-ai-context-package-apply.py `
  --package-root . `
  --target-root $TargetRoot `
  --apply `
  --acknowledge 'OP-001' `
  --acknowledge 'OP-002'
```

在 Bash 或 zsh：

```bash
cd "$PACKAGE_ROOT"
python3.11 payload/.ai/scripts/plan-ai-context-package-apply.py \
  --package-root . \
  --target-root "$TARGET_ROOT" \
  --apply \
  --acknowledge 'OP-001' \
  --acknowledge 'OP-002'
```

將範例中的 `OP-001`、`OP-002` 換成剛才 plan 實際列出的 operation ID；沒有需要 acknowledgement 的項目時，移除這兩行。套用後先閱讀：

Plan 的 `plan_sha256` 同時是 durable transaction ID。若程序在 journal 持久化後中斷，請以相同 package 執行 `--resume <transaction-id>`，或不依賴 package 執行 `--rollback <transaction-id>`。復原不接受新的 selection 或 acknowledgement；不相關的 worktree 變更、package/proof 漂移、損壞的 prestate 與模糊的部分寫入都會 fail closed。交易 journal 與 exact recovery bytes 位於目標 Git administrative directory，不會冒充 target repository 內容。

```powershell
Get-Content "$TargetRoot\.dev\AI-CONTEXT-APPLY-PENDING.yaml"
```

這份 schema-2 receipt 說明 transaction／plan、selected-input proof、每個 applied artifact 的 raw SHA-256 與 Git mode、完整 selected managed state、套用的 component、略過的 reconciliation 與來源證據；它尚未完成 target provenance 的最終初始化。

#### 3. 在目標專案使用 `ai-context-init`

接著以 `TARGET_ROOT` 開啟慣用的 AI Agent，讓 Agent 使用已安裝的 `ai-context-init` skill。它應依目標專案的真實檔案、solution、套件、設定與既有文件，整理 target-specific truth；不能把 framework source 的專案資訊當成目標事實，也不能在空專案中捏造產品架構。

第一次可直接使用下列 prompt。先要求唯讀盤點；確認後再讓 Agent 寫入，會比「交給 AI 自行處理」更安全且可審查。

```text
請在目前的 target repository 完成 AI context 的乾淨安裝初始化。

Package envelope root：<PACKAGE_ROOT>
Target repository：<TARGET_ROOT>
Requested release：<VERSION>

第一階段只做唯讀檢查：
1. 確認 target Git worktree 是否乾淨，並回報目前 commit。
2. 確認 package root 包含 requirements.txt、metadata/ 與 payload/，並驗證 archive checksum 的證據。
3. 執行 package planner 的 dry-run；plan output 必須放在 package 與 target 之外。
4. 回報 component/profile/provider selection、所有 add/replace/remove/rename/reconcile 項目與 operation ID。
5. 不得直接解壓縮或複製 payload 到 target，不得套用變更，不得建立或 finalize provenance。

等待我確認 plan 後再繼續。
```

確認 plan 後，使用下列 follow-up prompt：

```text
我已確認套用計畫。只可從相同的乾淨 target commit 套用已審查的 package plan；
只 acknowledgement 我明確列出的 operation ID，不能把 acknowledgement 當成覆寫或刪除授權。

套用後請閱讀 .dev/AI-CONTEXT-APPLY-PENDING.yaml，接著使用 ai-context-init：
- 根據 target repository 的檔案、solution、專案、套件、設定與既有文件建立 target-specific truth；
- 保留 reusable framework rules；
- 更新必要的 README、AGENTS、架構入口與 project config；
- 不得在空專案捏造產品、endpoint、資料庫、broker、queue 或部署事實；
- 只有在 repository、release、tag、full commit、component selection 與 import-time 都有可信證據時，
  才原子建立 .dev/ai-context/provenance.yaml 與 .dev/ai-context/customizations.yaml。

回報已修改檔案、未確認的事實、驗證結果與下一步建議。
```

在實務上，建議將「framework package 套用」與「target-specific 文件同步」分開提交，讓回復與審查界線清楚。

### 版本升級

`ai-context-upgrader` 不是一鍵覆蓋工具，也不是第一次安裝的入口。它只適用於已初始化的 target，且必須先由新發布包的 planner 進行 version-aware 套用。

開始前必須同時具備：

1. 乾淨 target worktree 與可回復的目前 commit。
2. 有效的 `.dev/ai-context/provenance.yaml` 與 `.dev/ai-context/customizations.yaml`；legacy `.dev/AI-CONTEXT-SOURCE.yaml` 只能作 read compatibility，不能與新 authority 並存。
3. 舊版本發布包中對應的 `metadata/files.yaml`，以及新版本的完整發布包與 checksum。
4. 新版本 migration guide 明確支援的來源版本與升級路徑。

例如，v0.7.0 只直接支援「已發布 v0.6.0 inventory」作為 automatic / reviewed 升級來源；v0.5.0 或更舊的 target 必須先依各自發布版本的 migration guide 走到 v0.6.0。是否已經有 `ai-context-upgrader` skill 不是充分條件。

#### 1. 以新 package 建立升級 dry-run

下例假設 target 已從 v0.6.0 升級到 v0.7.0。從 **新** package root 執行，並傳入完全相符的 **舊** package inventory：

```powershell
$PackageRoot = 'C:\gitproj\ai-context-package-0.7.0\ai-context-dotnet-backend-v0.7.0'
$TargetRoot = 'C:\gitproj\my-project'
$PreviousFiles = 'C:\gitproj\ai-context-package-0.6.0\ai-context-dotnet-backend-v0.6.0\metadata\files.yaml'

Set-Location $PackageRoot
python -m pip install -r requirements.txt

python .\payload\.ai\scripts\plan-ai-context-package-apply.py `
  --package-root . `
  --target-root $TargetRoot `
  --previous-version 'v0.6.0' `
  --previous-files $PreviousFiles `
  --plan-output "$env:TEMP\ai-context-v0.6.0-to-v0.7.0-plan.yaml"
```

在 Bash 或 zsh：

```bash
PACKAGE_ROOT="$HOME/gitproj/ai-context-package-0.7.0/ai-context-dotnet-backend-v0.7.0"
TARGET_ROOT="$HOME/gitproj/my-project"
PREVIOUS_FILES="$HOME/gitproj/ai-context-package-0.6.0/ai-context-dotnet-backend-v0.6.0/metadata/files.yaml"
PLAN_OUTPUT="/tmp/ai-context-v0.6.0-to-v0.7.0-plan.yaml"

cd "$PACKAGE_ROOT"
python3.11 -m pip install -r requirements.txt
python3.11 payload/.ai/scripts/plan-ai-context-package-apply.py \
  --package-root . \
  --target-root "$TARGET_ROOT" \
  --previous-version 'v0.6.0' \
  --previous-files "$PREVIOUS_FILES" \
  --plan-output "$PLAN_OUTPUT"
```

審查所有 `automatic-candidate`、`reconcile` 與 `exclude` 項目。planner 無法確認的內容必須保留給 owner decision；不要用猜測的版本或任意一份 `files.yaml` 讓流程繼續。

#### 2. 套用 planner 後，再使用 `ai-context-upgrader`

確認計畫後，以相同的 `--previous-version`、`--previous-files` 與已核准的 acknowledgement ID 重新執行帶有 `--apply` 的指令。閱讀 `.dev/AI-CONTEXT-APPLY-PENDING.yaml` 後，在 target repository 執行 `ai-context-upgrader` 的唯讀規劃。

```powershell
Set-Location $PackageRoot

python .\payload\.ai\scripts\plan-ai-context-package-apply.py `
  --package-root . `
  --target-root $TargetRoot `
  --previous-version 'v0.6.0' `
  --previous-files $PreviousFiles `
  --apply `
  --acknowledge 'OP-001' `
  --acknowledge 'OP-002'
```

```bash
cd "$PACKAGE_ROOT"
python3.11 payload/.ai/scripts/plan-ai-context-package-apply.py \
  --package-root . \
  --target-root "$TARGET_ROOT" \
  --previous-version 'v0.6.0' \
  --previous-files "$PREVIOUS_FILES" \
  --apply \
  --acknowledge 'OP-001' \
  --acknowledge 'OP-002'
```

將範例 operation ID 換成 plan 中已核准的項目；沒有 reconciliation 時移除所有 `--acknowledge` 行。

```text
請使用 ai-context-upgrader，先以唯讀方式規劃此 target repository 從 <FROM_VERSION>
升級到 <TO_VERSION>。新 package 已由 package planner 套用，套用收據位於
.dev/AI-CONTEXT-APPLY-PENDING.yaml。

請先：
1. 驗證 .dev/ai-context/provenance.yaml、customizations ledger、發布版本、tag、full commit、
   package metadata 與 migration guide；
2. 以 base、incoming、target 做三方比較；
3. 列出 automatic-candidate、reconcile、exclude，以及每項的理由；
4. 產出依 customization ID 分組的 semantic reconciliation table、validation 與 rollback boundaries。

在我明確核准前，不得修改 target 檔案、不得覆寫 target-owned truth，
也不得 finalize provenance 或 customizations ledger。
```

只有在 owner 已決定所有 reconciliation、必要驗證已成功，且獨立 post-upgrade audit 沒有阻擋問題後，才授權 Agent 套用接受的變更。若 target 缺少可信 baseline，請要求 Agent 停在 unresolved-provenance inventory，改提出人工 reconciliation 或乾淨安裝式 baseline 計畫；不得強制執行自動升級。

詳細的目標真相邊界，請見 [`migration-boundaries.md`](.ai/assets/skills/ai-context-init/references/migration-boundaries.md)；每個版本的支援來源以其 [release migration guide](.dev/releases/INDEX.MD) 為準。

## 發佈邊界

本 repository 同時是框架的維護來源與發佈封包的建置來源，但兩者包含的內容不同：

- 根目錄 README、來源庫的 Agent entry files、歷史 workflow、assessment、release records 與產品 placeholder 均屬於來源庫資訊，不會放進下游封包。
- 可攜式封包只收錄 distribution profile 明確列出的可重用內容，並以排除規則作為第二道保護。
- 因此，更新本 README 只會改善此來源庫的可讀性，不會改變已發佈版本，也不會讓 README 被誤納入未來封包。

## 語言

- `README.md` 是人類導覽用途的繁體中文（台灣）版本。
- `README.en.md` 是對應的英文版本。
- Agent-facing context 優先使用英文；人類導覽與協作文件可使用繁體中文（台灣）。完整原則請見 [`.dev/standards/AI-CONTEXT-LANGUAGE-POLICY.md`](.dev/standards/AI-CONTEXT-LANGUAGE-POLICY.md)。
