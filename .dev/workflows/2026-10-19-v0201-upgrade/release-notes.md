<!-- aicf-draft-delivery-v1:{"manifest_sha256":"59fd719b2e8b8f87ed98ab0d35a5b6ec1bce63eff56ce8881ac0dc23b9b154ba","source":{"commit":"fba2f031f1c969cd5788af924e307ffebf553422","tag":"v0.20.1","tag_object":"62559e0196db7275067755fc07e4a4b85c75f3eb"},"workflow":".github/workflows/publish-release.yml"} -->

## 修正
- 修復 v0.19.1 安裝升級時的 `unsupported-adapter`：新版引擎以 adapter 專屬、精確 digest 相符的歷史模板驗證舊安裝，保留未知與竄改模板的拒絕條件。
- Breaking reinstall 納入 `.codex/agents` 與 `.claude/agents`；受管 sub-agent 可明確清理，自訂 profile 必須明確保留或選定處置，runtime 設定不會因此納入清理。
- 保留重裝 preview 與 cleanup 後 installation plan 的原始診斷，並維持部分失敗的 `changed`／`removed` 與復原資訊。
- 更新安裝、重裝與復原文件的版本、範例及已知限制。

## 升級方式
使用同一份 v0.20.1 封存檔中的 catalog、engine 與 engine pin，依安裝手冊執行 derive → inspect → plan → 經授權 apply → inspect。v0.19.1 與 v0.20.0 都可直接升級至 v0.20.1。不要改寫舊 lock/hash、混用模板或刪除 lock 來繞過驗證。

v0.19.1 → v0.20.0 的已發布封存檔仍保留原有問題；本次不替換舊版資產。平台保證與既有 macOS 暫時後端契約維持不變。

## 驗證
- Windows／Python 3.13／PyYAML 6.0.3：本 Draft 精確 ZIP 的四個真實升級案例通過：v0.19.1 Codex-only、Claude-only、兩 adapter 完整安裝，以及 v0.20.0 兩 adapter 完整安裝。
- 完整案例包含全部選定 skills、兩個知識包與六種 sub-agent；最終 502 個受管檔案逐一核對。README、runtime 設定與自訂 agent 均保留。
- 同一 Draft 的真實 Git-backed reinstall 移除 12 個受管 agent profile、保留兩個自訂 profile 及範圍外設定；未分類與 untracked cleanup 均在寫入前拒絕，最終 inspect 一致。
- 本機 distribution 回歸 76 項通過；[PR head hosted CI](https://github.com/YuChia-Wei/ai-collaboration-framework/actions/runs/39254819912) 246 項通過、無失敗或跳過；固定 diff 獨立審查無可支持的 P0–P3 缺陷。
- [精確 main commit snapshot](https://github.com/YuChia-Wei/ai-collaboration-framework/actions/runs/39255268520) 與 [正式 Draft 流水線](https://github.com/YuChia-Wei/ai-collaboration-framework/actions/runs/39255304812) 成功。Actions 與 Draft 位元組相同，catalog/engine/README 對應原始 Git 來源。

來源 commit：`fba2f031f1c969cd5788af924e307ffebf553422`。
ZIP SHA-256：`e60b53e83e89ee3742e5ff4b20b5a28037ffef3cf8b12817dcb40c869b89be80`。

修正 PR：#468；工作與驗收：#467。