# Repository Rename Compatibility Notice

本 repository 的 canonical GitHub 座標已由
`YuChia-Wei/ai-collaboration-prompts-dotnet-backend` 更名為
`YuChia-Wei/ai-collaboration-framework`。新作業、自動化、security report、
原始碼連結與 release download coordinate 應一律使用新座標。

GitHub 在 2026-08-09 對舊 repository URL 回傳 HTTP 301 並導向新座標；
這是 GitHub provider 當下的相容行為，不是本 framework 保證的永久 alias。
保留舊座標只適用於明確分類的歷史 evidence、provider receipt、相容性測試或本 notice。

## 遷移檢查

| Surface | 風險 | 必要處理 |
| --- | --- | --- |
| Local Git remote | GitHub 目前可能接受舊 URL，但 redirect 會隱藏 stale local configuration。 | 用 `git remote get-url origin` 讀回；若仍是舊座標，改用 `git remote set-url origin https://github.com/YuChia-Wei/ai-collaboration-framework.git`。 |
| SSH remote | 舊 repository path 可能暫時由 provider 轉送，但不應成為新 clone 的預設。 | 使用 `git@github.com:YuChia-Wei/ai-collaboration-framework.git`，並以 `git ls-remote` 或 clone 驗證實際權限。 |
| Enterprise mirror、fork 或同步 job | GitHub.com rename 不會自動更新外部 mirror、allowlist、credential scope 或企業內部 repository。 | 由該 mirror／automation owner 更新 upstream、webhook、deploy key、allowlist 與同步設定；不要把 GitHub.com redirect 當作 mirror receipt。 |
| Hard-coded GitHub／raw URL | 網頁 redirect 不代表 `raw.githubusercontent.com`、API、download、cache 或第三方 crawler 都有相同相容保證。 | 將 current operational URL 改成新座標；歷史 evidence 保留原值並由 retired-name classification 標記。 |
| Security report URL | 舊 advisory URL 目前導向新路徑，但未登入的 HTTP probe只能確認 routing，不能證明已登入表單可提交。 | 使用 `https://github.com/YuChia-Wei/ai-collaboration-framework/security/advisories/new`，並由 repository owner 在登入狀態完成 read-back。 |
| Release download URL | 已發布 asset 與檔名不可重建或改寫；舊 repository URL 的 redirect 不是未來 automation contract。 | 新文件與 automation 使用 `https://github.com/YuChia-Wei/ai-collaboration-framework/releases/download/<tag>/<asset>`；保留既有 tag、Release、asset bytes 與 checksum。 |

## 不隨 Repository Rename 自動變更的 Identity

Repository identity 與 public product、framework release、archive／package base
name、technology profile、namespace 及 CLI identity 是不同決策面。這次 rename
不會自動更名 `dotnet-backend`、`ai-context-dotnet-backend-v<version>` 或其他
產品與執行介面；相關盤點與決策由 GitHub Issue #166 管理。

## 歷史與相容性邊界

- 不重寫 Git history、既有 tag、Release、asset、final assessment 或 completed workflow。
- Time-pinned provider mapping receipt 保留建立／read-back 當時的 repository URL。
- 新增 current operational surface 時不得再引入 retired repository name；source-only validator 會 fail closed。
- 若第三方仍依賴舊 URL，先記錄 owner、用途、預期 redirect behavior 與移除條件，再新增明確的 compatibility classification。
