# 重構執行計畫與使用者授權補充

本文件補充 2026-09-23 的原始 assessment，不覆寫原分析。原 [report.md](report.md)、[architecture.md](architecture.md)、[roadmap.md](roadmap.md) 保留其當時提案性質；正式實作依本補充與後續 workflow 追蹤。

## U001：本次明確授權與優先規則

使用者在本 assessment 完成後明確授權：

1. 由統籌對話安排工作次序，建立線上 Issues 並開工；正式工作依 repo 適用規範及 owning skill 執行。
2. **全部線上 CI／PR 自動驗證停止**。開發期間不執行舊框架 validators、package/upgrade/migration 或高 I/O 測試來阻擋重構；驗證工具與測試在開發完成後重新設計、試行。未跑／延後不是 passed。
3. 繼續走遠端 branch → GitHub PR → 線上 merge。CI 停止期間以範圍核對、內容檢視、Git 身分與必要檔案讀回作為整合依據；不以舊 required contexts 或完整 audit packet 工具阻擋。不得把無 CI 稱為已通過 CI。
4. 允許 commit 整理、壓縮後再 push／PR；未分享的細碎 implementation commits 可壓成有意義的工作批次。已明確保留的分析 checkpoint、已分享／被引用的提交不任意改寫。
5. 清理本機與線上已合併到 main 的分支；保留尚未合併工作、dirty worktree 與無法證明可刪的內容。
6. **每個實作 Issue 使用獨立 GPT-6 Astra、ultra 對話**。本對話負責計畫、依賴、狀態、整合與協調。禁止 sub-agents、巢狀 agents；子對話也不得自行建立更多對話。
7. worktree 放到目前指定的 RAM disk。已讀回 F: 容量 17,179,865,088 bytes；保留既有 `F:/ai-context-tests` 及全部內容。其他 F: 內容可在確認身分與無未保存工作後管理。
8. 完整計畫與報告先 commit 留存，再建立正式工作項與執行安排。

以上是本次重構的明確 user override，優先於與其衝突的 repo 規範。其餘規範繼續適用：專用 branch、owning skill、Issue scope、workflow/tasks、可續作交接、真實狀態、最小變更及 PR-only main 整合。舊驗證器不適用時記錄 deferred-by-owner，不修改證據使其看似 passed，也不為了滿足它額外建立大量表單。

這不是所有未來工作永久取消驗證。新架構完成後需有單獨工作項負責重新設計驗證與 pipeline；CI 恢復應依該階段的具體檢視結果與 owner 採納執行，本階段不自動恢復。

## 具體選擇

沿用原分析的 D01–D07，由 owner 委任統籌後採下列工作基線；如實作揭露新的實質權衡再提出修正：

| 決策 | 本次執行基線 |
| --- | --- |
| D01 | 單 repo；產品 canonical source 在 `src/`；根目錄是使用成品的專案，不能成為第二份手工 product source。 |
| D02 | skill 是可選能力包；必要共通層精簡。ai-context 維護系列改選配，source-only 發版／歷史工作不下放。 |
| D03 | 不先重建舊版本多跳與全量 migration engine。開發新成品的 core/custom 界線；一次性轉移與必要資料轉換放後段。 |
| D04 | skill 的輸入／輸出位置可設定；初期以 filesystem store 為實作基線。workflow 可 tracked 或 ignored；跨人持久化需選共享位置。本 repo 正式工作仍用 GitHub Issues。 |
| D05 | 先做 retention/compaction preview 與清楚規則；不自動刪重要紀錄或重寫 Git history。 |
| D06 | 一個來源 manifest 可生成所選技能／bundle／runtime projection；先完成一種可用路徑，再擴充。 |
| D07 | **原 W01 的測試分類、benchmark 與重寫移到最後**。初期只做必要語法／格式讀回（含既有 commit message 格式檢查）、差異核對與人工內容檢視，不執行舊驗證工具試行。 |

## 工作階段與對應

| 階段 | 有界工作項 | 與原 Wxx 的關係 | 主要完成物 |
| --- | --- | --- | --- |
| P0 | 報告 checkpoint；已合併分支清理；停用 CI；建立統籌與特殊執行規則 | 新增 prerequisite | 可追溯 baseline、停用前後 read-back、cleanup disposition、正式 workflow |
| P1-A | 可攜 skill／設定／artifact 所有權契約 | W02 | 小型明確契約、第一個 schema family、無隱性 `.dev` 路徑 |
| P1-B | source 與消費者邊界、src/package/dogfood 具體設計 | W03 的設計部分 | 與 P1-A 協調的目錄／manifest／runtime projection 契約；不在設計期搬全 repo |
| P2 | 建立 src 與共通基礎，移入一個 Lesson 垂直案例 | W03 + W05 起點 | 可讀寫專案指定位置的產品 source；根目錄消費方式；可選依賴 |
| P3-A | ADR、Lesson、規範 promotion | W05 | 自訂模板、查詢／寫入／supersede、有效規範 ownership |
| P3-B | PR、local backlog 與單一 provider 邊界 | W06 | 獨立 skill、明確操作與 scope、真實驗證狀態 |
| P4 | workflow 編排、回顧、續作、儲存與知識整合 | W04 + W08 | owning workflow schema/tools；可配置 tracking／retention；不硬綁 `.dev` |
| P5 | 其餘能力／ai-context 選配收斂；schema 工具 ownership 與必要 edges | W07 + W03 剩餘 | src 成品完整、舊混合界線退出 active use；schema producer/reader/disposition 清楚 |
| P6 | package 更新／migration notes／custom preservation；本 repo dogfood 收尾 | W09 + W10 開發部分 | 可重建成品、差異更新與一次性轉移方案；不宣稱舊升級矩陣相容 |
| P7 | 重新設計 validators、focused tests、必要 I/O 路線及 CI | W01 延後部分 + W10 驗證部分 | 依新契約選取的檢查、tiny fixtures、必要 RAM-disk 路徑、pipeline 重新檢視與恢復提案 |
| P8 | CLI/runtime、更多 provider 與發布方式重評 | W11 | 依實際結果決定是否需要，不作為本次重構的預設擴張 |

P1-A 與 P1-B 可平行，各自只寫自己的設計／workflow 資料，交由統籌整合契約。P2 基礎完成後，P3-A/P3-B 可在分離的 skill 目錄平行。共通 config、manifest、root entry 與索引採單一 owner，統籌依合併順序安排；不讓兩個工作同時重寫相同 framework 根檔。

每個 Issue 的 PR 應交付一個完整、有意義的結果，不以一個檔案一個 commit/PR 的方式切碎。初期 pipeline suspension 與設計工作可合併到 main 作為明確的重構 checkpoint；此時 framework 的完整驗證尚未完成，須顯示 implementation-complete/validation-deferred 的差別。

## 獨立對話與 RAM disk

- 統籌固定為目前對話 `01a0c9d9-3b00-7b70-ad85-daff590e7ecd`。
- 每個執行對話以 `model=gpt-6-astra`、`thinking=ultra` 建立；不依賴全域預設（目前全域 effort 與本對話不同）。
- 工作根目錄使用 `F:/framework-next/<issue-number-or-bounded-task>/`，一個 branch 一個 worktree，一個 writer。
- RAM disk 只放 checkout、可重建產物與 working data；Git common object database 與正式紀錄保留在持久 repository；工作到 coherent checkpoint 就 commit。不得把唯一未保存成果長期留在 RAM disk。
- 建立 task 的 API 若不能指定自訂 worktree root，允許以已登錄專案作 task 啟動入口，但所有 repo 命令均必須顯式使用已準備的 F: worktree；不得默默改用預設 C: worktree 或在主 checkout 修改。
- 子任務 prompt 需含：Issue、exact starting commit、worktree/branch、owning skill、scope/非目標、U001、相依檔案、允許寫入範圍、停止與交付條件、不得 spawn agents／建立子對話。
- 子任務先完成本地 coherent commits，回報統籌；首次 push 前由統籌安排 commit 整理。PR 與 merge 依明確授權的整合順序執行，不讓並行任務各自修改 main。
- worktree 釋放前確認 clean、成果已 commit 並可由持久 refs/remote 找回；所有刪除先驗證絕對路徑只在預定範圍，永久排除 `F:/ai-context-tests`。

## 停用與恢復清單

已完成唯讀 preflight：main 與 origin/main 同為 `c2e7071335d02d9b8d40ab4dcaf437e690791741`；沒有 open PR；GitHub main branch protection 回 404 `Branch not protected`，rulesets 為空；Actions enabled=true，7 個 workflows active。

在任何 push 前：保存必要的 workflow ID/path/state 與 Actions permissions 基線，逐一停用 workflow，停止現有 queued/in-progress 執行，將 repository Actions 設為 disabled，讀回 enabled=false。不得把停用期間缺少 checks 記為成功。

P0 的正式 Issue 應保留 restoration inventory。P7 檢視 `.github/workflows`、repo GitHub gate policy、必要 provider settings、branch protection/rulesets 的一致性；不重設 token、secrets、credential 或授權範圍。恢復只採用新設計中仍有用途的 pipeline，不能直接全量打開舊 7 條便稱完成。

## Commit 與遠端整合

分析 checkpoint 不壓掉。一般實作在首次 push 前按 scope 整理成少量 coherent commits；保留被引用的 checkpoint／交接身分。若內容已 push，除非統籌確認明確必要，不 force-push 重寫。

每次 push 後讀回遠端 SHA；PR 描述列出 U001、目前驗證 deferred、已做的有限檢查及工作項 disposition。GitHub merge 後讀回 main SHA、PR merged 狀態與 Issue/Project 實際狀態。本次源碼整合不代表 release／tag／publication／下游 adoption。

## 後續狀態來源

本文件是正式開工前的完整 plan baseline。第一筆 commit 後，統籌 workflow 擁有當前 Issue/任務/branch/PR 對照與續作狀態；個別 Issue workflow 擁有其實作紀錄。本 assessment 的原始結論不反覆追寫進度。
