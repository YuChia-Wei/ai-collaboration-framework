# Portable Test Fixture Acceleration Guide

本指南說明如何在不改變測試語意的前提下，對已分類、可拋棄的高 I/O test fixtures 使用明確 opt-in 的較快儲存空間。

## Portable baseline

不設定 `AI_CONTEXT_TEST_TMP_ROOT` 時，測試維持既有作業系統 temporary directory 行為。Repository 不會偵測 RAM disk、tmpfs、磁碟代號、容量、產品或工具，也不會修改全域 `TEMP`／`TMP`。

只有 `.ai/scripts/test-fixture-classifications.json` 中列為 `ephemeral-fixture-io` 的 tracked tests 會使用加速路由。未分類測試，以及 `durability-storage-semantics`、`platform-filesystem-semantics` 測試，維持既有 storage semantics；不得為了速度重新導向。

## Root contract 與 preflight

使用者或 runner 必須提供一個已存在的絕對 directory。Runner parameter 的優先順序高於 repository-scoped environment variable；兩者都未提供時使用 portable baseline。

每次實際執行都會重新驗證 root：

- 必須存在、為 directory，且不是 filesystem／volume root；
- 不得為 symlink 或 Windows reparse point；
- 必須可建立、寫入、讀回及移除 probe；
- 會記錄 filesystem type、capacity、free space、writable 與 path category，但不記錄實際 path；
- 每個 process 建立唯一的 `ai-context-tests-run-*` direct child；cleanup 只接受該已驗證 child。

任何 preflight、containment 或 cleanup failure 都是 failure，不得降級成 pass，也不得改用猜測的替代 root。

## Local usage

先建立你控制、可完全拋棄且不含其他資料的 directory，再明確傳入：

```powershell
python .ai/scripts/run-test-fixture-profile.py run `
  --mode accelerated `
  --fixture-root <absolute-disposable-root> `
  --condition warm `
  --storage-kind ram-backed
```

環境變數路由適合直接執行已分類的單一測試：

```powershell
$env:AI_CONTEXT_TEST_TMP_ROOT = '<absolute-disposable-root>'
python .ai/scripts/tests/test_ai_context_release_state.py -v
Remove-Item Env:AI_CONTEXT_TEST_TMP_ROOT
```

Default mode 不接受 `--fixture-root`，因此測試集合相同但 route 明確分離：

```powershell
python .ai/scripts/run-test-fixture-profile.py run --mode default --condition warm
```

## WSL guidance

在 WSL 中，workspace 或 fixtures 位於 `/mnt/*` 時可能因 metadata I/O 變慢。Runner 只提供不阻斷的 privacy-safe warning；它不會搬移 repository 或選擇另一個 root。若 owner 已提供 WSL-native disposable root，可明確傳給 runner，並在當次執行重新 preflight。

## Reproducible benchmark

Baseline 與 accelerated 結果必須使用同一 host、commit、tracked profile 與 condition。每種 mode 至少三次，使用 median；cold 與 warm 不得混合。若沒有安全且可重現的 cache-reset 程序，應把 cold evidence 記為 `deferred-with-owner`，不可把 warm 結果標成 cold。

```powershell
python .ai/scripts/run-test-fixture-profile.py benchmark `
  --mode default `
  --condition warm `
  --runs 3 `
  --output artifacts/fixture-benchmark-default.json

python .ai/scripts/run-test-fixture-profile.py benchmark `
  --mode accelerated `
  --fixture-root <absolute-disposable-root> `
  --storage-kind ram-backed `
  --condition warm `
  --runs 3 `
  --output artifacts/fixture-benchmark-accelerated.json
```

Evidence JSON 只記錄 route、root type、filesystem type、path category、容量、可用空間、test list、commit、condition、每次 duration 與 median；不包含 absolute path、使用者名稱、hostname、drive letter 或 storage 產品名稱。Nested subprocess phase 未被可靠 instrumentation 時會明確記為 `unavailable`。

## Manual CI profile

`.github/workflows/test-fixture-acceleration.yml` 僅能以 `workflow_dispatch` 在 owner-controlled self-hosted runner 上啟動。Caller 必須提供 explicit fixture root、storage kind 與 condition；workflow 不讀取 repository variables 來猜測 host storage。每次執行仍會 preflight，且 default 與 accelerated outcome semantics 不變。
