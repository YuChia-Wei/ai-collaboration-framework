# 安裝與選配說明

[回手冊首頁](README.md) · [Skill 目錄](skills/README.md) ·
[知識效果](knowledge-packages.md) · [工具型 skills 設定](tool-skills.md)

本文件描述已發布的 `v0.19.0-rc.4` 封存檔，不以開發分支或目前 `main` 的檔案代替已發布內容。RC4 的來源提交為 `158b8438f61a60eb621e3a5b43ed1a0479634f6f`，catalog identity 為 `catalog:1:0.19.0-rc.4:158b8438f61a60eb621e3a5b43ed1a0479634f6f:48e492e5d98fb35b7ec7189a3d6124ed90e0817afa1dab1d59b1750b56ee41fc`，內建 engine 是 `framework-managed-installation 2.0.0`。RC4 是 prerelease；封存、子集組裝或安裝都不代表 runtime、agent 行為或下游專案驗收已完成。

本手冊原始基線 `dd1453e8cf23bf62a5b28c70ed08f475856dda41` 位於 RC4 之後，並含 19 個 skill 說明檔的後續修訂。因此，本節每一個 RC4 安裝命令都從已發布 archive 的 `engine/` 與 `catalog/` 執行，不能混用工作樹中的工具或內容。

目前開發版的 subset 與 breaking reinstall 入口已移到
`engine/src/tools/derive-subset.py`、`engine/src/tools/reinstall-framework.py`；
`engine/src/tools/maintain_framework.py` 不變。新 engine 的 23 個成員全部來自
`src/`，不含 build CLI。下文 RC4 範例仍保留該已發布 archive 的舊路徑。
使用新 catalog（例如 [sub-agents](sub-agents.md)）時必須搭配其新 engine、pin
及新入口，不能把兩個版本的指令或檔案混用。

本手冊是來源庫 `docs/` 的使用文件，不屬於下游發佈資源；閱讀手冊與下載
安裝 archive 是兩個步驟。以下命令不依賴來源庫 checkout。本文的安裝
schema／破壞性重裝契約連到 RC4 固定 tag；各 skill 手冊的相對來源連結
供查閱本手冊基線，不能替代 archive 或實際安裝的指令。

流程是 **下載與校驗 → 選 skill／知識／adapter → 組裝 subset → inspect／plan
→ apply → inspect**。目前是明確 JSON 選擇與命令列流程，沒有互動式勾選安裝器。
也可交由 agent 依本手冊執行，但先提供實際目標、選擇與寫入範圍：

```text
請依 docs/installation.md 安裝已公開的 v0.19.0-rc.4。
目標專案是 <絕對路徑>；skills 選 <ID 清單>；adapters 選 <codex/claude>；
knowledge 選 <空清單、engineering-common 或兩包>，名稱用 original。
請先驗證 release bytes 並產生具體 plan，列出新增、修改、移除及衝突。
沿用我已給的安裝授權；需要尚未決定的清理或規則採用時，先提出精確變更。
```

## 1. 先取得並驗證已發布封存檔

需具備 Python 3.10 以上與既有的 PyYAML 6.x。引擎以 `python -I -B` 執行；`-I` 會隔離目前工作目錄、使用者 site 與 `PYTHONPATH`，`-B` 禁止建立 `.pyc`。請先在要使用的 venv 中確認 `import yaml` 可用且主版本為 6。

下面完整範例使用 PowerShell 7（Windows）、Python 3.13 與短路徑；不需要 .NET SDK、
Docker 或本來源庫 checkout。要執行 record 型 skill 工具時，另依其手冊安裝
`jsonschema` 等 runtime 相依。`gh` 只用來下載公開 asset，也可從
[RC4 Release 頁面](https://github.com/YuChia-Wei/ai-collaboration-framework/releases/tag/v0.19.0-rc.4)
手動下載相同檔案。

可使用現有相容 Python；若另外建立 venv，先選擇尚未存在、可寫的目錄：

```powershell
py -3.13 -m venv C:\aicf\venv
if ($LASTEXITCODE -ne 0) { throw 'venv 建立失敗' }
$PythonExe = 'C:\aicf\venv\Scripts\python.exe'
& $PythonExe -m pip install 'PyYAML>=6,<7'
if ($LASTEXITCODE -ne 0) { throw 'PyYAML 安裝失敗' }
& $PythonExe -I -B -c 'import sys,yaml; print(sys.version); print(yaml.__version__)'
if ($LASTEXITCODE -ne 0) { throw '隔離 Python 無法載入依賴' }
```

以下凡是 `python -I -B`，若使用此 venv，請寫成 `& $PythonExe -I -B`。
不用啟用 venv 或修改 PowerShell execution policy。

以下範例以 GitHub CLI 下載 RC4，並比對同一 release 的 SHA-256 檔。`$PackageRoot` 是解壓縮後目錄；它必須是直接目錄，不能是 symbolic link、junction 或 UNC 路徑。

```powershell
$ReleaseRoot = 'C:\aicf\rc4'
New-Item -ItemType Directory -Path $ReleaseRoot
gh release download v0.19.0-rc.4 --repo YuChia-Wei/ai-collaboration-framework `
  --pattern 'ai-collaboration-framework-v0.19.0-rc.4-158b8438f61a60eb621e3a5b43ed1a0479634f6f.zip' `
  --pattern 'ai-collaboration-framework-v0.19.0-rc.4-158b8438f61a60eb621e3a5b43ed1a0479634f6f.zip.sha256' `
  --dir $ReleaseRoot
if ($LASTEXITCODE -ne 0) { throw '下載失敗，請保留輸出並檢查' }
Get-FileHash -Algorithm SHA256 "$ReleaseRoot\ai-collaboration-framework-v0.19.0-rc.4-158b8438f61a60eb621e3a5b43ed1a0479634f6f.zip"
Get-Content -Raw "$ReleaseRoot\ai-collaboration-framework-v0.19.0-rc.4-158b8438f61a60eb621e3a5b43ed1a0479634f6f.zip.sha256"
$ArchivePath = "$ReleaseRoot\ai-collaboration-framework-v0.19.0-rc.4-158b8438f61a60eb621e3a5b43ed1a0479634f6f.zip"
$ExpectedArchiveHash = ((Get-Content -Raw "$ArchivePath.sha256").Trim() -split '\s+')[0]
if ($ExpectedArchiveHash -notmatch '^[0-9a-fA-F]{64}$' -or
    (Get-FileHash -Algorithm SHA256 $ArchivePath).Hash -ne $ExpectedArchiveHash) {
  throw 'ZIP checksum 不符；停止解壓縮與執行'
}
Expand-Archive "$ReleaseRoot\ai-collaboration-framework-v0.19.0-rc.4-158b8438f61a60eb621e3a5b43ed1a0479634f6f.zip" -DestinationPath "$ReleaseRoot\package"
$PackageRoot = "$ReleaseRoot\package"
```

RC4 實際 archive SHA-256 是 `db505854a2f355632e71a356ae8c4b85778880be4caee409e6557eca07ed5c4c`。解壓縮後應有 `catalog/`、`engine/`、`engine-pin.json`、`content-hashes.json` 與 `README.md`。archive 不含特定專案的 selection、已安裝狀態或 activation 結果。

## 2. 目錄與工作目錄規則

所有 CLI 路徑都必須使用既有的絕對直接目錄，且 `project`、`engine`、`candidate`、`scratch`、`staging`、`recovery` 彼此不能重疊或互為父子。`scratch` 與 `staging` 唯一可共用同一個目錄。不可將 output/scratch 放回來源工作樹或 catalog 下。

Windows 會以保守的 240 UTF-16 字元完整路徑限制拒絕操作。`.NET` 知識包的最長檔名會讓深層暫存根目錄超出此限制；建議把封存、candidate、scratch、staging 與 recovery 放在短根目錄，例如 `C:\aicf\rc4`，而不是使用很深的使用者暫存資料夾。這是輸入路徑預檢，不是內容相依性錯誤。

所有可攜 CLI 都從其檔案位置解析引擎或 bootstrap；以絕對 script 路徑呼叫時，呼叫端的目前工作目錄不影響封存內容選取。`maintain_framework.py` 的 `engine_root` 必須剛好等於該 script 所在封存的 `engine` 根目錄。

## 3. 檢視 catalog 與選擇規格

RC4 沒有一個「列出 catalog」的互動式 CLI。請讀取 `catalog/metadata/catalog.json` 檢視 components 與 presets，並讀取 `catalog/metadata/build.json` 取得 catalog identity 與兩個 digest。catalog 有 18 個 skill、兩個知識包及 Codex/Claude adapters。所有公開 presets 在 RC4 都只選 skill 與 adapter，沒有自動帶入知識包。

```powershell
$Catalog = Get-Content -Raw "$PackageRoot\catalog\metadata\catalog.json" | ConvertFrom-Json
$Catalog.components | Select-Object kind,id,version
$Catalog.presets | Select-Object id,version,skills,knowledge,adapters
Get-Content -Raw "$PackageRoot\catalog\metadata\build.json"
```

手動選擇檔的副檔名可以自行命名，但內容必須是 JSON；YAML 會被 `derive-subset.py` 以 `invalid-json` 拒絕。selection 必須含下列封閉欄位，陣列須依字典序排列：

下列 identity／hash 只屬於 RC4；換版本時應從新 archive 的 `build.json`
讀取，不能只改版本字串。完整結構可核對
[RC4 selection schema](https://github.com/YuChia-Wei/ai-collaboration-framework/blob/v0.19.0-rc.4/src/distribution/schemas/selection.schema.json)。

```json
{
  "selection_version": 2,
  "catalog": {
    "catalog_sha256": "37d14bd869260b3a089bb4e75cefd451f74912e3b23ad0bf966684e0882423a2",
    "files_sha256": "2263735f0aafaa844c075e09f58e153d77d48f10cf76fd3190b900c905b58cda",
    "identity": "catalog:1:0.19.0-rc.4:158b8438f61a60eb621e3a5b43ed1a0479634f6f:48e492e5d98fb35b7ec7189a3d6124ed90e0817afa1dab1d59b1750b56ee41fc"
  },
  "skills": ["code-reviewer"],
  "knowledge": ["dotnet-backend", "engineering-common"],
  "adapters": ["codex"],
  "bindings": [],
  "skill_naming": "original"
}
```

`skill_naming` 是 `original` 或 `prefixed`。`original` 讓 runtime entry 使用原始 skill ID；`prefixed` 會使用 `aicf-` 前綴。使用 `--preset` 時預設 `original`，可用 `--skill-naming` 覆寫；使用已儲存的 `--selection` 時，名稱模式只能由 selection 本身決定。

修改 `skills` 為你要的 canonical IDs；[18 個 skill 目錄](skills/README.md)
可逐一挑選。只用 Claude 時填 `"adapters": ["claude"]`，兩者都用填
`["claude", "codex"]`；這裡是 JSON 欄位內容，不是 YAML selection 範例。
只裝一個 skill 並不需要先裝 orchestrator 或其他 skills。

九個 preset 的目前內容如下；版本皆 `0.1.0`，knowledge 皆為空：

| Preset | Skill 範圍 | Adapter |
| --- | --- | --- |
| `lesson-minimal` | 只有 lesson-author（1） | Codex |
| `knowledge` | adr-author、lesson-author（2）；名稱不代表知識套件 | Codex |
| `work-management` | local-backlog、pr-author、orchestrator（3） | Codex |
| `context-maintenance` | auditor、governance（2） | Codex |
| `project-initialization` | ai-context-init（1） | Claude、Codex |
| `engineering` | 需求、規格、架構、GWT、診斷、實作與驗證（10） | Codex |
| `source-repository` | collaboration 除 local-backlog（14） | Codex |
| `collaboration` | 工程與記錄／編排 skills，無 context 三項（15） | Codex |
| `complete` | collaboration 加 auditor、governance；不含 init（17） | Codex |

Preset 的精確 ID 陣列以下載 catalog 為準；若要基於 preset 增減 skill、
knowledge 或 adapter，改用完整 JSON selection，勿以 preset 名稱猜測內容。

## 4. 選擇 skill 與選擇知識是兩個獨立決定

可選知識包為：

| 知識包 | 版本 | 相依性 |
| --- | --- | --- |
| `engineering-common` | `0.1.0` | 無 |
| `dotnet-backend` | `0.1.0` | 必須同時選 `engineering-common@0.1.0` |

引擎不會自動補上遺漏的相依性。選 `dotnet-backend` 而未選 `engineering-common` 會在組裝前以 `dependency-closure` 拒絕。另一方面，所有 skill 都可以只選自己而不選知識；缺少 optional 知識會以 `unavailable` 表示其知識增強能力不可用，不會使子集組裝失敗。

三種常用選擇只需替換 selection 的 `knowledge`：

```json
"knowledge": []
```

```json
"knowledge": ["engineering-common"]
```

```json
"knowledge": ["dotnet-backend", "engineering-common"]
```

以上是欄位片段，必須放回完整 selection object 才能作為 CLI 輸入。

### 已宣告會受知識缺少影響的 skill

下列五個 skill 的 package metadata 宣告 optional `knowledge_consumption`。若未安裝對應包，該表列出的作業無法使用該包的規則、標準或範例，應在 skill 操作結果中保留為 unavailable，而不要假設有完整技術指引。

| Skill | `engineering-common` 缺少時 | `dotnet-backend` 缺少時 |
| --- | --- | --- |
| `bdd-gwt-test-designer` | `design`、`review` 的 common test design 資源不可用 | `design`、`review` 的 .NET test standards 不可用 |
| `code-reviewer` | `review` 的 engineering rule catalog 不可用 | `review` 的 .NET design-by-contract、aggregate、repository、test、use-case standards 不可用 |
| `ddd-ca-hex-architect` | `design`、`review` 的 common architecture 規則不可用 | `design`、`review` 的 .NET architecture、messaging、project structure 資源不可用 |
| `local-change-implementer` | `implement` 的 common rule catalog 不可用 | `implement` 的 .NET aggregate、repository、test、use-case standards 不可用 |
| `slice-implementer` | `implement` 的 common engineering/GWT handoff 資源不可用 | `implement` 的 .NET design、aggregate、repository、test、messaging、use-case standards 不可用 |

其餘 13 個 RC4 skill 未在 package metadata 宣告任何知識 consumption：`adr-author`、`ai-context-auditor`、`ai-context-governance`、`ai-context-init`、`diagnostic-analyst`、`lesson-author`、`local-backlog`、`pr-author`、`problem-frame-author`、`requirement-author`、`software-development-orchestrator`、`spec-author`、`spec-compliance-validator`。這只表示 RC4 沒有宣告該兩包的必要資源；它不替目標專案補足自己的領域、政策或產品事實。

## 5. 僅組裝候選子集

以下命令只讀取已釘選 catalog、selection 與 engine pin，並把新的 immutable subset 寫入空的 output/scratch 父目錄。它不寫入專案，因此可用來審閱所選 skill、knowledge、runtime entry 與 metadata。`$Selection` 是上一節 JSON；`$OutputRoot` 和 `$ScratchRoot` 須預先建立、絕對且互不重疊。

```powershell
$CatalogRoot = "$PackageRoot\catalog"
$EngineRoot = "$PackageRoot\engine"
$Selection = 'C:\aicf\rc4\selection.json'
$OutputRoot = 'C:\aicf\rc4\candidate-output'
$ScratchRoot = 'C:\aicf\rc4\candidate-scratch'
New-Item -ItemType Directory -Path $OutputRoot, $ScratchRoot -ErrorAction Stop
python -I -B "$EngineRoot\tools\derive-subset.py" `
  --catalog-root $CatalogRoot `
  --catalog-identity 'catalog:1:0.19.0-rc.4:158b8438f61a60eb621e3a5b43ed1a0479634f6f:48e492e5d98fb35b7ec7189a3d6124ed90e0817afa1dab1d59b1750b56ee41fc' `
  --selection $Selection `
  --engine-pin "$PackageRoot\engine-pin.json" `
  --output-root $OutputRoot `
  --scratch-root $ScratchRoot
```

或以 preset 組裝：

兩種命令擇一。每次新組裝使用新的空 output/scratch 根，保留前次結果供比對。

```powershell
python -I -B "$EngineRoot\tools\derive-subset.py" `
  --catalog-root $CatalogRoot --catalog-identity '<catalog identity>' `
  --preset engineering --preset-version 0.1.0 --skill-naming original `
  --engine-pin "$PackageRoot\engine-pin.json" `
  --output-root $OutputRoot --scratch-root $ScratchRoot
```

實體 RC4 測試結果：只選 `code-reviewer` 產生 4 個檔案、16,400 bytes；再加 `engineering-common` 產生 21 個檔案、77,932 bytes；再加 `dotnet-backend` 與其必要的 `engineering-common` 產生 267 個檔案、1,050,749 bytes。三個結果的 completion metadata 都是 `installation: not-performed` 與 `behavioral_validation: not-performed`。這證明選擇是實際 materialization，沒有證明目標專案已安裝或 skill 已被執行。

## 6. 知識的採納與 bindings

組裝選擇後仍須實際 apply，才會把知識 bytes 寫入 `.ai/core/knowledge/<package>/`。
它不會自行建立或覆寫目標專案的根 `AGENTS.md`、專案政策、技術選擇或啟用設定。
要讓技術知識成為目標操作可讀取的受約束輸入，目標擁有者還要做以下採納：

1. 在 selection 的 `bindings` 明確選擇 resource、使用目的與 selector；要作為 `normative-rule` 使用時，必須列出 resource 的 rule IDs 與目標 authority 檔案的 SHA-256。
2. 以包含該 bindings 的 selection 重建 candidate，讓 digest 與 candidate identity 改變。
3. 安裝後以 lock SHA-256 與同一組 authority allowlist 讀取已安裝資源；authority 位元組或 selector 改變就必須重新選擇並審閱。
4. 由目標專案擁有者決定那些資源是否適用。引擎只驗證 identity、resource、authority hash 與未漂移狀態，並不推論語意適用性。

因此，「安裝 knowledge」和「將其當成目標的規範」是兩個獨立動作。沒有 bindings 的 knowledge 仍可作為 package 內容存在，但不會自動成為目標專案規則。

例如，已選 `code-reviewer` 與 `engineering-common`，想把共通 catalog 當作
`src/` 下 C# review 的**參考知識**，可以將以下 object 放進 selection 的
`bindings` 陣列。這個範例沒有採用 normative rules，也沒有宣稱測試覆蓋：

```json
{
  "id": "common-review-reference",
  "package": "engineering-common",
  "resources": ["engineering-rule-catalog"],
  "use_as": "knowledge",
  "selector": {
    "capabilities": ["review"],
    "operations": ["review"],
    "path_prefixes": ["src"],
    "technology_profile": null,
    "file_types": ["cs"],
    "execution_modes": ["direct"]
  },
  "authorities": [],
  "required_rule_ids": [],
  "required_for_coverage": false
}
```

先依自己的目標調整 selector；檔案存在不會自動決定 technology profile。
若改用 `normative-rule`，`required_rule_ids` 必須是所選 resource 的實際
rule IDs，`authorities` 必須提供目標採納文件的相對 `path`、實際 raw
`sha256` 與可定位決策的 `selector`。不能用空清單或虛構 hash 取代。
例如本機檔案的 raw hash 可由 `Get-FileHash -Algorithm SHA256 <實際檔案>`
取得並轉成小寫；這只證明 bytes，仍須由專案 owner 決定語意是否適用。

完整 closed schema 位於
[RC4 Binding／Selector／Authority](https://github.com/YuChia-Wei/ai-collaboration-framework/blob/v0.19.0-rc.4/src/distribution/schemas/contracts.schema.json)。
新增、修改、撤回 binding 都需要新的 selection／candidate 和 plan；
不要直接修改 managed lock 或 knowledge 副本。

## 7. 檢查、計畫、套用與復原

`engine/src/tools/maintain_framework.py` 是固定的 JSON stdin API：沒有命令列選項，只有 `inspect`、`plan`、`apply`、`recover` 四個 operation。呼叫形式如下；request 必須含 `api_version: 2`、`operation`、`project_root`、`engine_root` 與完整 `engine` pin（`engine-pin.json` 的內容）。

```powershell
Get-Content -Raw C:\aicf\rc4\request.json |
  python -I -B "$PackageRoot\engine\src\tools\maintain_framework.py"
```

下列是 PowerShell 7 的完整教學範例。先在**全新且空白**的暫存專案使用它，確認目標擁有者的 selection、candidate 與 maintenance 宣告都正確後，才以相同 `inspect → plan → apply → inspect` 順序處理既有專案。範例從實際 derive 產物的 `metadata/build.json` 讀取 candidate identity，而不是手動抄寫它；`engine-pin.json` 本身就是 `engine` 物件，不能再取 `.engine`。

```powershell
# 此範例故意使用一個新的空目錄；不要把它指向既有 consumer 專案。
$TutorialRoot = "C:\aicf\t-" + [guid]::NewGuid().ToString('N').Substring(0,8)
$PackageRoot = 'C:\aicf\rc4\package'                 # 已驗證 SHA-256 的 RC4 解壓目錄
$EngineRoot = Join-Path $PackageRoot 'engine'
$CandidateOutputRoot = 'C:\aicf\rc4\candidate-output'              # derive-subset 的輸出根目錄
$ProjectRoot = Join-Path $TutorialRoot 'project'
$ScratchRoot = Join-Path $TutorialRoot 'scratch'
$StagingRoot = Join-Path $TutorialRoot 'staging'
$RecoveryRoot = Join-Path $TutorialRoot 'recovery'
$PythonExe = 'C:\aicf\venv\Scripts\python.exe'     # 第 1 節建立的 venv

New-Item -ItemType Directory -Path $ProjectRoot,$ScratchRoot,$StagingRoot,$RecoveryRoot -ErrorAction Stop | Out-Null
if (@($ProjectRoot,$ScratchRoot,$StagingRoot,$RecoveryRoot | ForEach-Object { Get-ChildItem -LiteralPath $_ -Force }).Count -ne 0) {
  throw 'Tutorial roots must be empty and mutually disjoint.'
}

# 使用第 1 節確認可載入 PyYAML 的同一個 Python。
$MaintenanceTool = Join-Path $EngineRoot 'src\tools\maintain_framework.py'
$Engine = Get-Content -LiteralPath (Join-Path $PackageRoot 'engine-pin.json') -Raw | ConvertFrom-Json
$Candidates = @(Get-ChildItem -LiteralPath $CandidateOutputRoot -Directory | Where-Object Name -like 'subset-*')
if ($Candidates.Count -ne 1) { throw 'Select exactly one derive-subset output directory.' }
$CandidateRoot = $Candidates[0].FullName
$CandidateIdentity = (Get-Content -LiteralPath (Join-Path $CandidateRoot 'metadata\build.json') -Raw | ConvertFrom-Json).identity

function Invoke-AicfMaintenance([object] $Request) {
  $Wire = $Request | ConvertTo-Json -Depth 100 -Compress
  $EvidenceId = [guid]::NewGuid().ToString('N')
  [IO.File]::WriteAllText((Join-Path $TutorialRoot "$EvidenceId-request.json"), $Wire, [Text.UTF8Encoding]::new($false))
  $Text = $Wire | & $PythonExe -I -B $MaintenanceTool
  $MaintenanceExitCode = $LASTEXITCODE
  [IO.File]::WriteAllText((Join-Path $TutorialRoot "$EvidenceId-response.json"), ($Text -join "`n"), [Text.UTF8Encoding]::new($false))
  if ($MaintenanceExitCode -ne 0) { throw "Maintenance operation failed: $Text" }
  return $Text | ConvertFrom-Json -Depth 100
}

$InspectRequest = [ordered]@{
  api_version = 2; operation = 'inspect'; project_root = $ProjectRoot; engine_root = $EngineRoot
  engine = $Engine; candidate_root = $CandidateRoot
}
$Before = Invoke-AicfMaintenance $InspectRequest
if ($Before.outcome -ne 'inspected' -or $Before.details.managed_state -ne 'uninstalled') {
  throw 'The tutorial project is not empty/uninstalled; do not apply this plan.'
}

$PlanRequest = [ordered]@{
  api_version = 2; operation = 'plan'; project_root = $ProjectRoot; engine_root = $EngineRoot; engine = $Engine
  candidate_root = $CandidateRoot; candidate_identity = $CandidateIdentity; expected_lock_sha256 = $null
  mode_policy = 'windows-inventory-only'; scratch_root = $ScratchRoot; staging_root = $StagingRoot; recovery_root = $RecoveryRoot
  durability = [ordered]@{ declared_by = 'target-owner'; declaration_reference = 'approved isolated tutorial'; failure_domain = 'process-termination' }
  protected_inputs = @(); project_data_action = 'none'; project_edits = @()
}
$Plan = Invoke-AicfMaintenance $PlanRequest
if ($Plan.outcome -ne 'planned') { throw 'Plan was not produced.' }
$Plan.plan_sha256             # Read this exact value; it binds the following apply.
$Plan.plan.maintenance_scope  # Review the exact sorted affected capabilities.
$Plan.plan.delta              # Review adds/changes/removes before writing.
$Plan.plan.preserved_unknown  # Preserve this result; do not delete unknown files to force an apply.

# The timestamp is evidence of a fresh human maintenance declaration. It is deliberately not an API field:
# the closed maintenance object accepts exactly the six fields below.
$MaintenanceConfirmedUtc = (Get-Date).ToUniversalTime().ToString('o')
Write-Host "Maintenance declared at UTC $MaintenanceConfirmedUtc for: $($Plan.plan.maintenance_scope -join ', ')"
$ApplyRequest = [ordered]@{}
$PlanRequest.GetEnumerator() | ForEach-Object { $ApplyRequest[$_.Key] = $_.Value }
$ApplyRequest.operation = 'apply'
$ApplyRequest.expected_plan_sha256 = [string] $Plan.plan_sha256
$ApplyRequest.maintenance = [ordered]@{
  declared_by = 'target-owner'; declaration_reference = 'approved isolated tutorial'
  affected_capabilities = @($Plan.plan.maintenance_scope)
  sessions_stopped = $true; tools_stopped = $true; external_writers_stopped = $true
}
$Applied = Invoke-AicfMaintenance $ApplyRequest
if ($Applied.outcome -ne 'applied') { throw 'Apply did not reach applied; retain recovery evidence and inspect.' }

$After = Invoke-AicfMaintenance $InspectRequest
if ($After.outcome -ne 'inspected' -or $After.details.managed_state -ne 'managed-bytes-consistent') {
  throw 'Post-apply inspection did not prove managed-byte consistency.'
}
$After.details.owned          # Installed files and hashes.
```

此範例僅宣告 process-termination 的失敗範圍與 Windows inventory 模式，
沒有宣稱斷電 durability、Linux mode bits 或 recovery 驗收。`maintenance` 的三個
停止欄位只能在實際沒有其他 session／tool／writer 使用該 scope 時填 `true`。

這個範例的 `project_data_action: "none"` 與空的 `project_edits` 不會編輯目標業務資料。對既有專案，先以 `inspect` 和 `plan` 讀回 lock、`delta`、`preserved_unknown` 與 protected inputs；任何 marker、drift、未知衝突或未審閱的 removal 都是停止條件，不能以手動遞迴刪除來取得「乾淨」結果。

- `inspect` 是唯讀檢查，回報 `uninstalled`、`managed-bytes-consistent`、`drift` 或 `recovery-needed`，但 `project_readiness` 一律是 `not-assessed`。
- `plan` 是唯讀預覽，不配置 operation directory、不取得 writer lock、不宣告 caller quiescence。它需額外提供 `candidate_root`、`candidate_identity`、`expected_lock_sha256`、`mode_policy`、`scratch_root`、`staging_root`、`recovery_root`、`durability`、`protected_inputs`、`project_data_action: "none"`、`project_edits`。回傳的 `plan_sha256` 必須是後續 apply 的精確輸入。
- `apply` 是實際寫入。它以相同 plan 欄位加上 `expected_plan_sha256` 與新鮮 `maintenance` 宣告，並在 writer lock 下重新計算 plan。maintenance 的 `affected_capabilities` 必須與 plan 的排序 scope 完全相同，且 `sessions_stopped`、`tools_stopped`、`external_writers_stopped` 都必須確實為 `true`。套用前應先由專案擁有者審閱 plan、衝突、protected inputs 與候選來源。
- `recover` 只處理一份精確保留的 operation，需提供原 `operation_root`、`operation_sha256`、`direction`（`finish` 或 `restore`）、當前 lock/marker hashes 及新鮮 maintenance 宣告。它不是一般性修復或 cleanup 工具。

RC4 沒有名為 `validate` 或 `upgrade` 的 operation。候選及安裝完整性分別由 `derive-subset`、`inspect` 與 plan/apply 讀回保證；它們不能代替下游的建置、測試、runtime 或 agent acceptance。升級是「組裝新的 selection/candidate → inspect 既有 lock → plan 差異 → 經授權 apply」的程序，不是單一命令。

取消選擇或卸載某個 skill/knowledge 同樣沒有單獨 `uninstall` 命令：建立不含該 component 的新 selection，再用 plan 審閱 `remove` delta。若要撤除 runtime skill entry，任何未知的 discovery 子樹、未受舊 inventory 擁有的檔案或漂移都會造成 conflict，不應以手動遞迴刪除繞過它。`reinstall-framework.py` 是另一條 Git-backed breaking reinstall 路徑，要求完整 quiescence、乾淨 Git baseline、明確 cleanup/preservation pins 與可恢復的 content；它不是一般 upgrade 或 deselect 的替代方案。

### 既有 managed 安裝的調整

1. 保留舊 selection、下載的 catalog／engine、目前 lock 和 recovery records。
   先 inspect；有 drift 或 recovery marker 就處理該狀態，不進行下一次 apply。
2. 編輯 project-owned selection 中的 skills／knowledge／adapters／bindings，
   由所選新版本重新 derive。專案可以選用 `.ai/custom/installation.json`
   保存 selection，來源庫自己採此位置；它不是必須存在的固定設定檔。
   本教學 `project_edits: []` 不會自動複製該檔，actual desired selection
   仍保存在 managed `.ai/framework.lock`。不要手動改 lock 代替新 candidate。
3. `expected_lock_sha256` 改成**實際現有 lock 的 raw hash**，不能沿用初裝
   範例的 `null`：

   ```powershell
   $ExpectedLockHash = (Get-FileHash -Algorithm SHA256 (Join-Path $ProjectRoot '.ai/framework.lock')).Hash.ToLowerInvariant()
   $PlanRequest.expected_lock_sha256 = $ExpectedLockHash
   ```

4. 若有要明確保護的專案檔案，在 `protected_inputs` 傳入按 path 排序的
   `{path, sha256}`；`path` 為專案相對路徑，hash 必須由該檔案讀取。
   `sha256: null` 意味該路徑必須不存在，並不是忽略雜湊。
   不要把 managed payload 列為 project-owned protected input。
5. 用新的 request 重做 plan，審閱 `delta`／衝突／preserved_unknown；確認
   真實 maintenance scope 已停用後，再用新的 `plan_sha256` apply，最後 inspect。

上面的教學程式刻意在既有安裝時停止；不要只移除其保護判斷就拿去重裝。
Legacy v0.18／早期 RC 的移轉、跨電腦復原、全專案清除都不是這個更新範例
已驗證的行為。破壞性重裝必須另外閱讀
[RC4 契約](https://github.com/YuChia-Wei/ai-collaboration-framework/blob/v0.19.0-rc.4/.dev/workflows/2026-09-30-rc3-reinstall/breaking-reinstall.md)，
選定精確 cleanup／preservation 與 Git baseline 後才執行。

### 發生失敗時

保留 operation/recovery 目錄、原 engine pin、request／response 與目前 lock；
不要刪除 `.ai/framework.operation` 或 `.ai/config-transition.operation` 來繞過狀態。
先 inspect。工具仍執行時應等待其完成；工具介面的 yield 不是安裝逾時或失敗。

確實需要 recover 時，由復原 owner 選 `finish` 或 `restore`，使用相同 API
共同欄位，加上 `operation_root`、原 operation 的 `operation_sha256`、
`direction`、目前 `expected_lock_sha256`、`expected_marker_sha256` 和真實
maintenance 宣告。雜湊必須來自保留輸出或實際 raw bytes，不能猜測。
`restore` 是該次 operation 的回復，不是一般舊版降版命令。
若 operation 資料遺失、內容漂移或仍有其他 writer，先交回復原 owner；
本手冊沒有以成功安裝推論 recovery 測試也成功。

### 安裝後的使用驗收

確認 `.ai/core/skills/<id>/`、所選 knowledge、Codex 的 `.agents/skills/`
或 Claude 的 `.claude/skills/`，以及實際 lock selection 都符合計畫。
開啟使用該專案的 runtime，以一個手冊範例呼叫已裝 skill，核對它使用的
入口、版本、允許路徑與缺少知識的回報。runtime discovery 若尚未更新，
依該 runtime 的專案載入方式重新開啟／載入，不能把檔案存在當作已執行。

安裝 `ai-context-init` 後仍須另行呼叫 `initialize`；工具型 skills 的
project config 依[共通設定](tool-skills.md)準備。此框架不替你的應用程式
執行 build/test，也不自動採納來源庫的 GitHub、workflow 或授權政策。

## 8. 平台與常見問題

| 情況 | 處理方式 |
| --- | --- |
| `invalid-json` | selection/request 使用 UTF-8 JSON；不傳 YAML、重複 key 或未知欄位 |
| `dependency-closure` | 依下載 catalog 補齊必要依賴；`.NET` 要明列 common |
| `path-budget` | 選短的全新外部根路徑；保留原失敗；不放寬 240 UTF-16 限制 |
| managed drift／conflict | 比較原 lock 擁有的 bytes 和目前客製變動，再由 owner 決定保留方式 |
| recovery-needed | 保留 marker 與 operation，走精確復原流程，先停止受影響能力 |
| 已裝知識但沒有專門規範覆蓋 | 核對 resource、bindings、authority hash 與 task selector；存在不等於採用 |
| 找不到 `ai-context-init` | 舊 `complete` 不含它；另選該 skill／initialization preset |
| 工具讀不到 Python 套件 | 確認 `-I` 使用的同一個 interpreter/venv；user site 或 PYTHONPATH 不會補依賴 |

Windows 使用 `mode_policy: windows-inventory-only`。POSIX 引擎要求
`posix-permissions`；需在目標平台重新 derive candidate，使 build 的 mode
materialization 與該平台相符，不能直接把 Windows subset 當成 Linux 安裝驗收。
POSIX 可將同一 JSON request 透過 stdin 交給
`python -I -B /absolute/engine/src/tools/maintain_framework.py < request.json`，
並使用該平台的絕對本機路徑。本次只執行 Windows 教學情境，未驗證 Linux／
macOS 安裝、檔案系統 durability 或跨平台還原。

## 9. RC4 實測範圍與限制

已在 Windows/Python 3.13/PyYAML 6 的隔離目錄完成：下載後 SHA-256 比對、封存解壓、三種 `code-reviewer` 知識組合的實體 subset 組裝、遺漏 `engineering-common` 的 `dependency-closure` 拒絕，以及三個全新空專案的 `inspect → plan → apply → inspect`。它們分別安裝並逐檔 SHA-256 讀回 4（只含 `code-reviewer`）、21（加 `engineering-common`）和 267（加 `dotnet-backend`）個 managed files；每個 post-apply inspect 都回報 `managed-bytes-consistent`，markers 均不存在，lock SHA-256 與保留 operation 的 after-lock binding 相符。過程記錄在 task-owned local evidence，且未量測個別操作 duration。

上述只驗證 RC4 engine 對空白、隔離目錄的安裝流程與 managed bytes。沒有執行 `recover`、breaking reinstall、目標專案 activation、knowledge 的語意採納、agent task、下游 runtime 測試或 hosted acceptance；這些狀態仍須由其各自擁有者選擇與驗證。
