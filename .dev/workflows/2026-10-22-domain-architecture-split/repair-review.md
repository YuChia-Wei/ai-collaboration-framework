# 剩餘缺陷修正與合併交接

日期：2026-10-22。Owner 授權修正剩餘缺陷，確認內容後安排合併；
本次整合僅關閉已交付工作項目，後續調整完成後才另行安排新版發布。

產品修正 commit：`01eabd7f4399ff1fe31edd30e49119372f7484b7`。
修正比較基準：`329571b583cc6290f4c0950a232675bd3edbb45f`。
整個分支比較基準：`f96fffe0af6e9e4f79d5f2f4be05bb3665553123`（當次遠端 main）。
分支：`codex/plan/skill-evolution-20261022`。

## 已修正缺陷

| 缺陷 | 修正 | 證據 |
| --- | --- | --- |
| #480 R26-3：derive 未回傳 resolver 已知的 optional knowledge 缺口 | 成功結果帶出 `unavailable`，無缺口為 `[]`；不加入 selection、metadata、lock 或 identity | 三個 regression cases；實際 pinned library／CLI 三情境一致 |
| 既有 P2：fixed auditor 依賴未分發的 source preflight | 改由 parent 提供固定 subject/base/範圍/criteria/authority/permissions/stop conditions；移除 classifier、packet tier、lease、digest admission 的可攜前提 | manifest、playbook、兩種 runtime projection 及文件一致；固定 diff 獨立審核 |
| 既有 P3：四角色八個 projections 引用未定義 `role_bindings` | 採 canonical role、parent-selected owning skill/operation、bounded assignment、target rules；四 package 與 manifest 同步 0.1.1 | 四組共用指令 parity、metadata 與分發測試；模型與工具權限未變 |

角色仍保留獨立唯讀、固定 clean subject、漂移停止、失敗證據與 parent integration
owner。Target 必要檢查缺工具或權限時回報 blocked，不擴權、不假稱通過。
Package 版本只識別來源修正；未指定 framework 發行版本。

## 驗證與失敗保留

- `python -I -B tests/run.py --suite distribution --suite schemas`：133 tests，
  0 failures、0 errors、0 skipped。初次 fixture／CRLF 失敗與修正經過保留在
  [工作計畫](workflow-plan.md#repair-implementation-checks)，未放寬產品驗證。
- 三個新增 in-memory tests 使用真實 resolver、projection 與 metadata/identity；
  只替換 execution-source admission 與 disk emission，不當作安裝驗收。
- 對固定產品 SHA 建立 synthetic 0.0.0 catalog 與相符 engine pin，使用交付的
  `src/tools/derive-subset.py`，在 `python -I -B` 執行三情境：
  1. 單選 Domain、不選 optional knowledge：exit 0，三組缺口，沒有自動補裝。
  2. 選 common + dotnet 並提供有效 Domain explore binding：exit 0，缺口 `[]`。
  3. 選 dotnet 卻缺其 required common：exit 1，`dependency-closure`，輸出根維持空。
  Library resolver 與 CLI JSON 的診斷逐項相同，desired selection 原樣保留。
- 四組 Codex／Claude 共用指令語意與文字 parity 已核對；Codex 保持 read-only，
  Claude 保持 `Read, Grep, Glob` 與 `model: inherit`。
- 產品修正階段 26 個相對文件連結有效，`git diff --check` 通過。
  整個分支至產品 SHA 的 11 個 commits 通過既有 commit validator。

本機原始 CLI、build、維護及 Gemini 紀錄保存於 `F:/AICF-r/480/`。
這些是本次執行 evidence 的本機位置，不是可攜產品依賴或發布資產。

## 獨立審核與 Gemini 處置

`repair480_review` 是未繼承父聊天內容的獨立 sub-agent，使用 installed
`code-reviewer/review` common method；繼承 session 設定，未 override 模型或 effort，
執行端未另暴露模型身分。它對上述固定修正 diff 審核前後 HEAD 相同、tracked
worktree/index 無修改，沒有發現可支持的 actionable findings。它沒有跑測試、
CLI、安裝或 provider 操作；133 項測試是 parent 執行證據。

Gemini 透過 Antigravity CLI，實際模型 `gemini-4-argon-medium`，權限模式
`request-review`。第一次嘗試偏離指定範圍，猜測不存在的角色路徑，parent 中止
其已確認身分的 process；該次記為 interrupted，不能當作通過。
第二次提供十份精確編號檔案的完整內容，禁止工具使用、限制三分鐘；
實際 21.4119 秒、exit 0、SUCCESS、零工具呼叫，完成三個角色契約情境推演。

Gemini 提出「Claude `stop and return needs-parent-routing` 與回傳 evidence／limitations
衝突」候選。原獨立 reviewer 再做有界裁決：不成立。停止受阻執行沒有要求丟棄
既有證據；同檔仍要求回傳 findings/evidence/limitations。`needs-parent-routing`
表達受阻狀況，沒有被定義為 advisory `parent action` 的欄位值；回報 blocked
並附證據、`parent action: reroute` 可以同時遵守所有要求。因此未因該候選改動產品。

Gemini 推演不是 native role invocation 或模型行為驗收。其初次中止與候選駁回
均保留；沒有把成功返回結果等同產品全部通過。

## 預覽與跨 reviewer 交接

F 槽既有 Preview 已經由支援的 plan/apply 更新到產品 SHA `01eabd7f`：
513 managed files、22 changed、491 unchanged，沒有新增或移除 managed 檔案。
Apply 後獨立 inspect 為 `managed-bytes-consistent`、drift 0；六個原有非管理檔案
hash 不變，沒有重做初始化。Source 專案的 installed 17 skills 未升級。
維護證據宣告的 failure domain 是 process termination，未宣稱斷電 durability。

Owner 明確授權 ROBO Agents 私訊交接；已傳送固定產品 SHA、三項修正、驗證與
不發布邊界，請 owner 轉交 Claude 做唯讀交叉核對。
[Slack 訊息](https://cathayrobo.slack.com/archives/D0B1S83TFEK/p1792653027633689)。
尚未收到該次 Claude 回覆；未當作已完成 reviewer acceptance。

## 工作項目與下一步

| 工作項目 | 本次交付與整合意圖 |
| --- | --- |
| #476 | 分離 Domain／Software 能力與相鄰協作 Feature；隨四張 Story 一致整合 |
| #477 | Domain explore/design/review 與獨立選配 |
| #478 | Software architecture design/review 與模型衝突回饋 |
| #479 | Requirements／Story／Spec／test／orchestrator 責任及共通知識 |
| #480 | 分發、退役、遷移、知識診斷與本次三項缺陷修正 |
| #481–#484 | 後續 local workflow／customization 設計，保留 open，不在本次關閉範圍 |

已更新 #476–#480 的 body，另次 provider fetch 確認內容相符，title/state/labels/
assignees/milestone 未變，五項仍 open。R3 與 ROLE 的已驗證細項有結果；原來源能力
AC 保留供 owner 確認內容，不將 instruction review 勾成所有模型的真實行為通過。

本次交付可供 owner 檢查來源與 Preview。後續在 owner 確認後建立／處理實際 PR，
取得 current-head `Source change gate`、所需 review 與整合授權，再合併並讀回
Issue／Project 狀態。尚未建立 PR、取得 hosted gate、merge、關閉 Issue 或修改
Project。No tag/release/publication；不把整合與新版發布綁在一起。
