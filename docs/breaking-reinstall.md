# Git-backed breaking reinstall

[回手冊首頁](README.md) · [一般安裝與更新](installation.md) · [操作復原](recovery.md)

本頁描述 v0.20.2 修正後的 Catalog 1／Engine 2 契約；版本是否已發布須另行確認。入口為
`engine/src/tools/reinstall-framework.py`，以 JSON stdin 接受 `plan`／`apply`。
這是先清除明確選定的舊 framework 檔案，再安裝新 candidate 的**非原子重裝**。
一般更新、取消選配仍使用 `maintain_framework.py`；不要為了避開 drift 或衝突
就改走重裝。此頁不提供自動 cleanup 分類，也不宣稱舊版內容可無損遷移。

v0.20.0 的 macOS 路徑使用同一暫時後端，保證較弱；其 plan／apply
也會回報 `macos-reduced-guarantees`。需使用相應的新 engine 與 pin，
已發布的 v0.19.0 不會因文件修訂而取得支援，見[平台說明](installation.md#8-平台與常見問題)。

## 選定 baseline 與檔案處置

專案必須是精確 Git worktree root，具有固定的完整 HEAD SHA 和乾淨的 tracked
內容；原有編輯先由 owner 決定保存方式。不能由重裝流程代替決定 commit、丟棄
或覆蓋使用者變動。從 plan 到 apply 完成前，所有新舊 framework 活動都須停止。

工具從可驗證的既有 lock inventory 與實際 managed bytes 判定所有權，再觀察新
candidate 的目的路徑、明列的 preservation 與 project edits。它不再遞迴盤點
整棵 `.dev`／`.ai`，也不要求為大量歷史紀錄逐檔分類、複製、移走或補登記。
`scoped_inventory` 是這次操作的受影響檔案，不是專案全部資源清冊。

未受管或未知內容預設留在原處，包括團隊新增 skill、參考文件、設定與 runtime
entry；放在 framework 鄰近目錄、已 commit 或內容恰好相同，都不移轉所有權。
受管檔案若缺失或有本機修改，即使刪除／修改已 commit，也會先回報 drift。新目的路徑與自訂
內容衝突時停止。缺少或無法驗證歷史 ownership 時，不得用 caller cleanup 清單
代替證據；保留內容並交回 owner。這不新增 RC3 直接升級／歷史 lock 支援。

以下明列處置的路徑不得重疊，hash 必須取自實際 raw bytes，pin 清單按 path 排序：

| 處置 | 輸入與限制 |
| --- | --- |
| 清除 `cleanup` | `{path, sha256}`；必須屬於已驗證 installed inventory（或該 lock 本身），且 baseline 具有相同內容、普通 tracked 狀態；Git 是復原證據，不是 ownership |
| 保留 `preserved_inputs` | `{path, sha256}`；可額外 pin 少量重要檔案作讀回，不須列出全部歷史；未知／自訂檔案未列入仍預設保留。不能與 candidate 目的檔案衝突 |
| 明確修改 `installation.project_edits` | 指定 before／after raw hashes 與 staging object；只接受[明列的安裝設定與導覽路徑](installation.md#安裝寫入邊界)，內容仍須 owner 審閱 |

**已驗證的舊受管檔案不適用「漏列即保留」。** 不在新 candidate 的舊受管檔案，
每個都必須明列於 `cleanup` 或 `preserved_inputs`；漏列會在建立 preview 與清理前
回報 `reinstall-unclassified` 及精確路徑。新 candidate 仍使用的既有目的檔案，
則依原規則必須明列 cleanup，才能重新安裝。這只檢查已驗證的舊 inventory，
不要求分類未知內容或盤點整個專案歷史，也不會自動替 owner 增加刪除項目。

明確保留舊受管檔案表示：檔案 bytes 留下，但**不再由新安裝的 lock 管理**。
若保留 runtime entry，它可能繼續被發現，或引用已清除的支援資源；必須先確認
保留用途與必要相依，不能把這個結果說成「skill 已停用／退役」或「仍由 framework
管理」。後續若選回同一路徑，會是 unowned collision，需由 owner 另行協調。
`preserved_unknown` 只涵蓋工具觀察到的範圍，不是完整自訂資源清冊。

舊 `.ai/framework.lock` 若存在，必須驗證後明確選入 cleanup。spec、requirement、
lesson、ADR、workflow、design、assessment 與其他專案紀錄都不是安裝 payload；
不能經 cleanup 或 project edits 刪除、重寫或搬移。`.ai/local/` 不得作為一般
cleanup 資源。既有 `.ai/local/installation.guard` 必須明確列入 preservation，
工具會先驗證它是 inert coordination file，再依宣告的完整 quiescence 重設。
任何未完成 operation marker 必須先走原操作復原，不能重裝繞過。

root `AGENTS.md`／`CLAUDE.md` 只有被明列時才成為操作輸入。Fable 回報的舊入口連結
殘留應由 owner 審閱後，透過 `project_edits` 與重裝配對修改，或另外做 project-owned
文件變更；installer 不會自行理解並重寫團隊規則。也須人工檢查其他 runtime
config 是否仍引用退役資源；必要的導覽修正不得順便重設團隊規則或自訂設定。

## 準備新安裝與 project edits

依[安裝手冊](installation.md)驗證 archive、選配並 derive 新 candidate。建立完整
API 2 **plan request** 作為 `installation`：包含完整 engine pin、candidate identity、
各個 root、mode policy、durability、protected inputs、`project_data_action: "none"`
及 project edits。此處 `expected_lock_sha256` 必須是 `null`，表示在所選 cleanup
移除舊 lock 後建立新安裝；不是忽略舊 lock，舊 bytes 仍由 cleanup pin 保護。
這份 nested request 不可加入 apply 專用的 `maintenance`／`expected_plan_sha256`。

根目錄及所有外部工作目錄必須已存在、互不重疊；scratch／staging 可共用。
`preview_root` 必須在專案之外，初次使用空目錄，並符合[平台限制](installation.md#8-平台與常見問題)。
重裝 plan 不修改目標專案，但**會在外部 preview 寫入選定操作輸入的副本**；它不是
完全不寫磁碟的操作。內容改變後若 preview 不符，選另一個空 preview，不覆蓋舊證據。

每個 project edit 的 closed object 為以下四個欄位；這是欄位說明，不是可直接
執行的虛構 JSON：

| 欄位 | 值 |
| --- | --- |
| `path` | 專案相對路徑，例如 `AGENTS.md` |
| `before_sha256` | 原始檔案 raw hash；原本不存在才填 `null` |
| `after_sha256` | 已審閱新內容的 raw hash；明確刪除才填 `null` |
| `after_content_ref` | `objects/<after_sha256>`，實際 bytes 放在 `staging_root` 下該位置；刪除時填 `null` |

不要把同一路徑再列入 cleanup、preservation 或 protected inputs。工具會保存
配對 before／after 供新安裝 operation 復原；不接受只有 hash 而沒有 after object。

## 組合重裝請求

下例使用 PowerShell 7。先準備四個外部檔案：`new-install-plan.json` 是上一節的
完整 API 2 plan request；`cleanup.json` 與 `preserved-inputs.json` 是已逐檔審閱的
pin 陣列。`affected-capabilities.json` 是新 candidate 選定的所有 component IDs
排序後的陣列，包含 skills 及所選 knowledge，不能用 runtime 前綴名稱代替。
這些是輸入檔名，工具不會自動分類產生它們。

```powershell
$PackageRoot = 'C:\aicf\v019\package'
$InputsRoot = 'C:\aicf\reinstall-inputs'
$ProjectRoot = 'C:\work\selected-project'
$PreviewRoot = 'C:\aicf\reinstall-preview' # 已存在的外部空目錄
$RequestPath = Join-Path $InputsRoot 'reinstall-plan-request.json'
$NewInstallation = Get-Content -LiteralPath (Join-Path $InputsRoot 'new-install-plan.json') -Raw |
  ConvertFrom-Json -AsHashtable -Depth 100
if ($NewInstallation.operation -ne 'plan' -or $NewInstallation.project_root -ne $ProjectRoot -or
    $null -ne $NewInstallation.expected_lock_sha256) { throw 'Review the nested API 2 plan request.' }
if (Test-Path -LiteralPath $RequestPath) { throw 'Choose a new request output file.' }
$SelectedHead = & git -C $ProjectRoot rev-parse HEAD
if ($LASTEXITCODE -ne 0) { throw 'Cannot read the selected Git baseline.' }
# 在執行前核對 SelectedHead 就是 owner 選定且可用於 cleanup recovery 的 baseline。
$Maintenance = [ordered]@{
  declared_by = 'project-owner' # 實際宣告者
  declaration_reference = 'selected breaking reinstall decision' # 實際決策位置
  affected_capabilities = @(Get-Content -LiteralPath (Join-Path $InputsRoot 'affected-capabilities.json') -Raw | ConvertFrom-Json)
  sessions_stopped = $true
  tools_stopped = $true
  external_writers_stopped = $true
}
$ReinstallRequest = [ordered]@{
  reinstall_version = 1
  operation = 'plan'
  project_root = $ProjectRoot
  expected_head = [string] $SelectedHead
  cleanup = @(Get-Content -LiteralPath (Join-Path $InputsRoot 'cleanup.json') -Raw | ConvertFrom-Json)
  preserved_inputs = @(Get-Content -LiteralPath (Join-Path $InputsRoot 'preserved-inputs.json') -Raw | ConvertFrom-Json)
  preview_root = $PreviewRoot
  installation = $NewInstallation
  maintenance = $Maintenance
  all_framework_activity_stopped = $true
}
[IO.File]::WriteAllText($RequestPath, ($ReinstallRequest | ConvertTo-Json -Depth 100),
  [Text.UTF8Encoding]::new($false))
```

`true` 欄位只有在活動實際停止後才能填寫；plan 也要求完整 quiescence。
使用支援平台的 Python 呼叫，保存 request、stdout、stderr 與 exit code：

```powershell
$PythonExe = 'C:\aicf\venv\Scripts\python.exe'
$ReinstallTool = Join-Path $PackageRoot 'engine/src/tools/reinstall-framework.py'
$PlanResponsePath = Join-Path $InputsRoot 'reinstall-plan-response.json'
$PlanErrorPath = Join-Path $InputsRoot 'reinstall-plan-stderr.txt'
if ((Test-Path -LiteralPath $PlanResponsePath) -or (Test-Path -LiteralPath $PlanErrorPath)) {
  throw 'Choose new response and error output paths.'
}
$PlanText = Get-Content -LiteralPath $RequestPath -Raw |
  & $PythonExe -I -B $ReinstallTool 2> $PlanErrorPath
$ReinstallExitCode = $LASTEXITCODE
[IO.File]::WriteAllText($PlanResponsePath, ($PlanText -join "`n"), [Text.UTF8Encoding]::new($false))
if ($ReinstallExitCode -ne 0) { throw "Reinstall planning failed: $ReinstallExitCode" }
$ReinstallPlan = $PlanText | ConvertFrom-Json -Depth 100
if ($ReinstallPlan.outcome -ne 'planned') { throw 'No accepted reinstall plan.' }
$ReinstallPlan.plan.scoped_inventory
$ReinstallPlan.plan.installation_preview.delta
$ReinstallPlan.plan.installation_preview.project_edits
```

逐項審閱 inventory、cleanup／preservation、project edits、installation preview
及 Git recovery baseline。既有回應欄位的分類讀法如下；不另增 request／plan 格式：

| 審閱項目 | 既有回應證據 |
| --- | --- |
| 舊受管清理及新 payload | `plan.cleanup`、`plan.installation_preview.delta` |
| 明確保留 | `plan.preserved_inputs`；若是舊受管檔案，需確認退出新安裝管理的後果 |
| 必要設定／導覽修改 | `plan.installation_preview.project_edits`，審閱 before／after |
| 衝突、漏列或無法驗證 ownership | 最外層 `diagnostics`，以及有執行 preview 時的 `installation_preview_result.diagnostics` |
| 操作觀察範圍 | `plan.scoped_inventory`；不代表全部未知內容或歷史均被盤點 |

若核准 destructive apply，從保存的原 request 建立
**新檔案**，只把最外層 `operation` 改成 `apply`，並加入最外層
`expected_plan_sha256`，值取自這次重裝回應的 `plan_sha256`，不是內部安裝 plan
的 hash。以同一 CLI 執行，保留另一組完整回應。任何輸入、宣告或 preview 變更
都須重新 plan；apply 會重新計算並拒絕不符的 hash。

## 成功與部分失敗的判讀

成功結果應為 `outcome: reinstalled`、`preserved: hashes-match`（只指明列的
preservation pins，不能當作全部專案檔案已逐一核對），但
`project_readiness` 仍是 `not-assessed`。再以新 engine `inspect`、檢查 root 文件
連結、runtime discovery、工具與知識採用；這些是分開的驗收項目。

舊受管檔案若被清除後成為新 candidate 檔案的父目錄，屬於合法的檔案轉目錄；
成功檢查會接受該普通目錄。原檔案重新出現、link 或無關目錄仍不能當作清理成功。

`cleanup-incomplete` 表示可能已有檔案被移除；保留 `removed`、diagnostics、
`installation_result` 及原請求。v0.20.1 另保留 `installation_preview_result`
與 `installation_plan_result`（執行至該階段時），可從其原始 `diagnostics`
判讀預覽或清理後規劃的失敗原因。預覽失敗仍是 `changed: false`，不能與
清理後的部分失敗混淆。舊 tracked cleanup 的還原依選定 Git baseline
逐檔規劃；新的 installer 若已建立 operation，則依其精確 journal 走
[API 2 復原](recovery.md)。不要直接整棵 `reset --hard`／刪目錄，也不要以
新安裝的 `restore` 推論舊 cleanup 會自動回來。此流程沒有整體原子 rollback。
