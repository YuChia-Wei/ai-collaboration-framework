# 安裝操作復原

[回手冊首頁](README.md) · [安裝與平台限制](installation.md) ·
[Breaking reinstall](breaking-reinstall.md)

本頁適用於 v0.19.0 Catalog 1／Engine 2，入口為
`engine/src/tools/maintain_framework.py` 的 JSON stdin `recover` operation。
它只處理一份精確保留的安裝操作，不能當作一般 rollback、跨電腦搬移或清理工具。
本頁提供來源契約與請求範例，沒有宣稱已完成你的目標環境復原驗收。

## 先確定操作與復原方向

1. 確認原工具已終止；介面回傳執行中或 yield 不表示操作失敗。
   停止該操作 scope 的 session、tool 與外部 writer，保留原 request／response。
2. 以原來已驗證的 engine 與完整 pin 執行 `inspect`。保留目前 lock、
   `.ai/framework.operation` 及可能存在的 `.ai/config-transition.operation`。
   不要手動刪除 marker、修改 lock、移動 operation 目錄或先做另一輪 apply。
3. 從原回應的 `details.operation_root` 或已保留的操作紀錄定位目錄，核對
   `operation.json`、`objects/` 與 journal。錯誤回應不保證已建好完整 operation；
   缺少紀錄時交由復原 owner 判定，不以新建 JSON 補齊。
4. 選 `finish` 完成這次操作的 after state，或選 `restore` 回到這次操作的
   before state。已完成操作的重播只能確認相符狀態，不會替後續新變動任意降版。

| 請求欄位 | 值的來源 |
| --- | --- |
| `api_version`／`operation` | `2`／`recover` |
| `project_root` | 原 operation 記錄的專案絕對路徑 |
| `engine_root`／`engine` | 原來已驗證的 engine 目錄與完整 `engine-pin.json` 物件 |
| `operation_root` | 原操作目錄的原始絕對路徑 |
| `operation_sha256` | **該目錄 `operation.json` 的原始 bytes SHA-256**，不是 plan hash |
| `direction` | 復原 owner 選定的 `finish` 或 `restore` |
| `expected_lock_sha256` | 當前 `.ai/framework.lock` 的 raw hash；不存在才填 `null` |
| `expected_marker_sha256` | 當前 `.ai/framework.operation` 的 raw hash；不存在才填 `null` |
| `maintenance` | 原 scope，加上本次重新確認的停止活動宣告 |

這是 closed request，不加入 `candidate_root`、`expected_plan_sha256` 或舊版
欄位。paired config marker 由引擎核對；不能因 request 沒有第二個 marker hash
就刪掉它。`operation_sha256` 是 byte pin，仍須核對它確實來自所選的原操作。

## 產生完整請求：PowerShell 7

以下只寫出供審閱的 request，不執行復原。先把路徑及宣告改成這次原始操作的
實際值；相同 engine 版本號不足以取代完整 pin 與 engine bytes 驗證。

```powershell
$PackageRoot = 'C:\aicf\v019\package'   # 原操作使用且已驗證的 package
$OperationRoot = 'C:\aicf\recovery\selected-operation' # 原回應中的精確目錄
$RequestPath = 'C:\aicf\recover-request.json' # 新的外部輸出檔案
$Direction = 'restore' # owner 已選定的 finish 或 restore
$DeclaredBy = 'project-owner' # 改成實際宣告者
$DeclarationReference = 'selected recovery decision' # 改成可定位的本次決策
$EngineRoot = Join-Path $PackageRoot 'engine'
$Engine = Get-Content -LiteralPath (Join-Path $PackageRoot 'engine-pin.json') -Raw |
  ConvertFrom-Json -Depth 100
$OperationPath = Join-Path $OperationRoot 'operation.json'
$Operation = Get-Content -LiteralPath $OperationPath -Raw | ConvertFrom-Json -Depth 100
if ($Operation.operation_root -ne $OperationRoot) { throw 'Use the original operation root.' }
if ($Direction -notin @('finish','restore')) { throw 'Select one recovery direction.' }
if (Test-Path -LiteralPath $RequestPath) { throw 'Choose a new request output file.' }
$ProjectRoot = [string] $Operation.project_root

function Get-OptionalRawSha256([string] $Path) {
  if (Test-Path -LiteralPath $Path) {
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) { throw 'Expected a file.' }
    return (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant()
  }
  return $null
}

# 只有本次實際停止所有受影響活動後才可建立此宣告。
# scope 沿用原紀錄；三個 true 是新的事實宣告，不能由舊紀錄推論。
$Maintenance = [ordered]@{
  declared_by = $DeclaredBy
  declaration_reference = $DeclarationReference
  affected_capabilities = @($Operation.maintenance.affected_capabilities)
  sessions_stopped = $true
  tools_stopped = $true
  external_writers_stopped = $true
}
$RecoverRequest = [ordered]@{
  api_version = 2
  operation = 'recover'
  project_root = $ProjectRoot
  engine_root = $EngineRoot
  engine = $Engine
  operation_root = $OperationRoot
  operation_sha256 = (Get-FileHash -LiteralPath $OperationPath -Algorithm SHA256).Hash.ToLowerInvariant()
  direction = $Direction
  expected_lock_sha256 = Get-OptionalRawSha256 (Join-Path $ProjectRoot '.ai/framework.lock')
  expected_marker_sha256 = Get-OptionalRawSha256 (Join-Path $ProjectRoot '.ai/framework.operation')
  maintenance = $Maintenance
}
[IO.File]::WriteAllText($RequestPath, ($RecoverRequest | ConvertTo-Json -Depth 100),
  [Text.UTF8Encoding]::new($false))
```

審閱完整 request、原操作 identity、engine pin、復原方向及 fresh maintenance
宣告後，才以受支援平台的 Python 執行。保留 stdout、stderr 與 exit code；
失敗時不要丟棄回應或以同一份過期 lock／marker hashes 盲目重試。

```powershell
$PythonExe = 'C:\aicf\venv\Scripts\python.exe'
$RecoveryResponsePath = 'C:\aicf\recover-response.json'
$RecoveryErrorPath = 'C:\aicf\recover-stderr.txt'
if ((Test-Path -LiteralPath $RecoveryResponsePath) -or (Test-Path -LiteralPath $RecoveryErrorPath)) {
  throw 'Choose new response and error output paths.'
}
$RecoveryText = Get-Content -LiteralPath $RequestPath -Raw |
  & $PythonExe -I -B (Join-Path $EngineRoot 'src/tools/maintain_framework.py') 2> $RecoveryErrorPath
$RecoveryExitCode = $LASTEXITCODE
[IO.File]::WriteAllText($RecoveryResponsePath, ($RecoveryText -join "`n"), [Text.UTF8Encoding]::new($false))
$RecoveryText
if ($RecoveryExitCode -ne 0) { throw "Recovery failed; retained exit code: $RecoveryExitCode" }
```

接著重新 `inspect`，核對結果符合選定方向及 marker 狀態。若涉及 project edits，
也須核對 root 文件等內容的 before／after；這與 runtime discovery、工具可執行性
及業務程式驗收分開。v0.19.0 的 macOS recover 不可用；0.20.0 開發中的
暫時後端接受 recover，但只提供盡力復原，仍需相同 engine pin、原路徑與
完整操作紀錄，見[平台矩陣](installation.md#8-平台與常見問題)。

## 需要人工判定的情況

operation／objects／journal 遺失、engine pin 不符、project 或 operation 路徑
改變、未知檔案衝突、檔案漂移、其他 writer 仍存活，都須先保留證據再決定處置。
完成安裝、可讀取 lock 或外部使用者曾經成功復原，不會使這些條件自動通過。
Breaking reinstall 的舊檔 cleanup 由選定 Git baseline 負責回復；API 2 的
`restore` 只負責新安裝 operation，詳見[重裝手冊](breaking-reinstall.md)。
