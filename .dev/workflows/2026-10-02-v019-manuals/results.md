# 0.19.0 文件與選配驗證結果

本次工作對應 [#322](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/322)
及 owner 要求的 `docs/` 安裝／各 skill 說明書。產品盤點固定於
`dd1453e8cf23bf62a5b28c70ed08f475856dda41`；RC4 發行來源另為
`158b8438f61a60eb621e3a5b43ed1a0479634f6f`。此記錄保留文件工作的來源、
驗證與交接，不授予正式版發布、目標升級或 provider 寫入權限。

## 原始主要目標的重新核對

原始 18 項的追溯來源為
[RC3 原意與處置表](../2026-09-30-rc3-reinstall/knowledge-disposition.md)
及 [#322](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/322)。
以下將現有產品、實際選定試裝、後續採納的範圍變更與未驗證事項分開，
不以檔案數或 Issue 關閉數換算達成百分比。

| 原 ID | 原目標 | 現況與證據限制 |
| --- | --- | --- |
| 1-1 | 可攜低相依 skills；workflow 組織工具 | 18 個 skills 可獨立選取；portable workflow-v2 工具已退休。orchestrator 0.2.0 恢復階段協調，workflow 儲存／保留政策由專案擁有；原完整工具承諾已縮減。 |
| 1-2 | `.dev` 交還專案；來源／輸出位置可選 | 指令型 skills 接受 caller-selected 來源、模板、目的地；record 工具使用明確 roots/config。不是固定複製來源庫的 `.dev`。 |
| 1-3 | `.ai/core` 與 `.ai/custom` 分離 | 已實作；source/MQ 選定重裝有 protected-byte 保留證據，不推論所有未知客製 layout。 |
| 1-4 | ADR／Lesson 標準 skills | `adr-author`、`lesson-author` 已分發，保有 schema／工具／歷史身分邊界；採用與實作不是 record 寫入的同義詞。 |
| 1-5 | PR 標準 skill | `pr-author` 已分發；本機 record 及另行授權的 GitHub draft 操作存在，不含 push／merge／Issue 管理。 |
| 1-6 | 開發回顧以 ADR／Lesson 落地 | orchestrator 可協調專案選定記錄與交接；未交付自動回顧或 portable workflow record 工具。部分達成。 |
| 1-7 | ADR／Lesson 轉為專案規範 | `standards-promotion` 刻意留在未發佈實驗；不在 catalog／preset／payload。正式能力未完成，不能算入 stable 已交付清單。 |
| 1-8 | AI-context 能力可選 | auditor／governance 可選，RC4 另有 initialization preset；安裝不自動生成根文件，也不代表 context 已初始化。 |
| 1-9 | 維護 schema 有工具／migration | 已分發 record families 有其 schema／工具；部分版本只讀或 unsupported migration 保留原件。沒有「所有 schema 都具完整 migration」的驗收。 |
| 1-10 | 全刪全加及差異更新、降低衝突／I/O | managed plan/apply 與 RC3 明確 Git-backed breaking reinstall 已實作並有選定 source/MQ 實測。未量測 I/O 改善；不能泛稱原子重裝或通用 rollback。 |
| 1-11 | 本機 backlog skill | `local-backlog` 已分發；專案可選本機 store，不強迫取代線上 tracker。 |
| 1-12 | 後續 CLI／工具可行性 | 現有 JSON API 與 CLI 可組裝／維護；互動式 installer、所有 provider 等仍不是已交付範圍。 |
| 1-13 | workflow／assessment 壓縮、保留、刪除或線上化 | 完整通用能力未完成；線上 workflow 另由 v0.20 [#416](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/416) 規劃。手動 cleanup 不算產品保留系統。 |
| 2-1 | 來源庫自行採用並驗證 | source 實際選定安裝為 17 skills、雙 adapter、無 knowledge；有 plan/apply/inspect 紀錄。安裝事實不等於 18 skills 的 agent 行為品質驗收。 |
| 2-2 | 可編輯來源移至 `src` | 已完成 source／managed projection 分離；目前 `src/skills`、`src/knowledge` 與 installation owner 明確。 |
| 2-3 | 參考外部 skills 打包結構 | 已採可攜套件與 metadata/manifest 方向；參考不是必須照抄的獨立驗收。 |
| 2-4 | 捨棄高 I/O／歷史升級自我測試 | #425 與 2026-10-02 source policy 已縮減為 affected checks；Source checks 恢復。退休與 deferred checks 均不記為 passed。 |
| 2-5 | RAM-disk fixture 路徑／降低 SSD 消耗 | 舊加速路由已移除，#274/#275 為 NOT_PLANNED；本次不復活，也沒有 SSD/RAM 效能量測。 |
| R8（後加） | skill／工程知識可選配 | 現行 selection 明確分開 skills、knowledge、adapters；九個 presets 都不自帶 knowledge。實際 RC4 選配驗證另列下節。 |

對照材料：

- [RC3 實測與保留邊界](../2026-09-30-rc3-reinstall/results.md)
- [orchestrator 恢復與 source/MQ 安裝](../2026-10-01-orchestrator-restore/results.md)
- [promotion 未發佈處置](../2026-10-01-standards-promotion-hold/results.md)
- [source adoption 與 recovery 範圍](../../design/framework-next/source-adoption/adoption-and-recovery.md)
- [source development policy](../../standards/SOURCE-DEVELOPMENT-POLICY.md)

## RC4 與正式版的實際狀態

Provider 讀回：

- [v0.19.0-rc.4](https://github.com/YuChia-Wei/ai-collaboration-framework/releases/tag/v0.19.0-rc.4)
  已公開，`isPrerelease=true`，有 ZIP、checksum 及 release manifest。
- [draft build 37000062722](https://github.com/YuChia-Wei/ai-collaboration-framework/actions/runs/37000062722)
  succeeded；ZIP SHA-256 為
  `db505854a2f355632e71a356ae8c4b85778880be4caee409e6557eca07ed5c4c`。
- [Source checks 37027470904](https://github.com/YuChia-Wei/ai-collaboration-framework/actions/runs/37027470904)
  在 `f6e5c7966772ede02f0d408e2ca1336c3cb913bd` 成功，其 tree
  `594c1d28688176c13d647fac0c98d397e47fa87e` 等於本次基線 `dd1453e8`。
  這不是本次新增文件的 hosted pass。
- [main snapshot 37027874017](https://github.com/YuChia-Wei/ai-collaboration-framework/actions/runs/37027874017)
  succeeded；snapshot 不等於 Release。
- 本次讀回沒有 `v0.19.0` stable tag/release；#322 仍 OPEN。

固定 `git diff v0.19.0-rc.4 dd1453e8cf23bf62a5b28c70ed08f475856dda41 --`
為 58 files、851 additions、114 deletions，其中 14 個 distributed skills
的 19 個 instruction/reference Markdown 有修改。Product metadata、operation、
dependency、version、manifest、profile 與安裝工具未變。故正式版需要以新的
candidate 重建，不應把 RC4 舊 ZIP 改名當成新的內容。

## 文件與知識盤點

入口為 [docs/README.md](../../../docs/README.md)，包含安裝、知識選配、
工具型 skills 設定及 18 份個別手冊。

三個 bounded read-only agents 分別調查 release inventory、skill/knowledge
metadata、RC4 installer。Root 是唯一 tracked writer。前兩個 authoring
research 使用 `evidence-report-synthesizer`（gpt-5.6-terra/high）及
`bounded-general-worker`（gpt-5.6-terra/xhigh）；installer 為後者。
這是實際 dispatch profile，沒有額外聲稱 provider runtime attestation。

Metadata 盤點：18 skills、2 knowledge packages、5 consumers、10 optional
consumption blocks、34 resource references、13 unbound skills。
`dotnet-backend@0.1.0` 必要相依 `engineering-common@0.1.0`；沒有名為
`engineering-practices` 的套件。Consumption 宣告與 target bindings 不同。

## 選配與文件命令驗證

初始 RC4 實體 subset 組裝（僅一個 `code-reviewer`，Codex adapter）：

| knowledge 選擇 | payload files | payload bytes | 組裝結果 |
| --- | ---: | ---: | --- |
| 無 | 4 | 16,400 | passed |
| engineering-common | 21 | 77,932 | passed |
| dotnet-backend + engineering-common | 267 | 1,050,749 | passed |

各 build completion 誠實保留 `installation: not-performed` 與
`behavioral_validation: not-performed`。它們不是 apply 的結果。
另外驗證：`.NET` 未選 common 時以 `dependency-closure` 拒絕；YAML selection
以 `invalid-json` 拒絕；隔離空目錄 inspect 為 uninstalled；短路徑 plan 為
planned。

其後 root 明確選定三個全新 task-owned 空專案的教學命令驗證。使用下載的
RC4 engine，JSON stdin API 執行 `inspect → plan → apply → inspect`；
三者 apply 都回傳 `applied`、post-inspect 為 `managed-bytes-consistent`，
逐檔 raw SHA-256 全相符，兩種 maintenance markers 都不存在。

| case | managed files | plan SHA-256 | installed lock SHA-256 |
| --- | ---: | --- | --- |
| zero | 4 | `a1b3ba10ab257ad9f4985f5ffbba9d820abd747c26d05b8279266359d5877dbd` | `ddf6429c1a29f764acbdcd9cf05d40d8d82adc804deacc8eff3755d4b9a53be4` |
| common | 21 | `e431f5a2195a049410c9146954772ab867ba585fd2954be8a6d50548f05f1058` | `913a78f1964701b19e874ad93ca5f9ae74230a38db2cf868f8ff63163b4ac9eb` |
| both | 267 | `d8b639edf41bc456f3330c47f103b07bc4ea11cf6ec8a8b32a33ab22d62981f2` | `851511481cf67f70ed3da1f030bbc3ea50bddcde17e6846ba7a261351f735304` |

Local evidence retained under `C:/aicf-rc4-audit-01a0/tutorial-apply-logs/`:
40 files、644,996 bytes，摘要 `summary.json` 由 root 讀回核對。
未量測個別 operation duration。這是明確教學情境的本機安裝結果，不是
重新啟用退休的 full/native matrices；未執行 restore/recover、breaking reinstall、
Linux、Claude discovery、真實 agent 任務、語意規則採用、產品 runtime 或 hosted acceptance。

保留限制與失敗：

- 過深臨時根路徑觸發 `path-budget`；改用明確短路徑後同選擇成功，最大
  full path 為 220／240 UTF-16。這是 material input change，沒有改產品限制。
- Release agent 一次混入工作樹 diff；root 指出後以兩個固定 endpoints
  重查，撤回原說法。上方固定 delta 不含本次未提交的 docs selector 變更。
- Source graph 沒有可信當前 identity/coverage 且仍有移除路徑，採 tracked-file
  fallback；graph search absence 不作不存在證明。
- Draft 的 `local-backlog create planned` 範例已更正為 create draft 後再
  transition；未執行不正確 request。文件抽取漏掉 prompt 的問題在 author
  read-back 發現後補回 18 份，沒有以初稿當交付。
- Installer agent 曾把工具 yield 誤判為 30 秒中斷，root 當時沿用於 progress
  update。保留輸出與 fresh inspect 證明程序仍在完成，三例皆成功；已明確
  更正使用者更新。這是觀察判讀錯誤，不是失敗 apply；沒有執行 recovery。

## 本機檢查與審查

- 初次 `python -I -B tests/run.py --suite source`：47 tests passed，
  zero errors/failures/skips，runner duration 2.399087 seconds。
- 新增 selector contract 僅讓 `docs/` Markdown 取得文件 owner；安裝與知識
  指南保留 independent-scoped-review，rename/delete 維持舊側條件，
  非 Markdown／相鄰未知路徑仍拒絕。修改 selector 本身仍要求獨立審查。
- Author content check：23 Markdown files、18 unique skill manuals，版本與所有
  operation IDs、34 declared resource references 符合 manifest/metadata；
  214 個本機連結 exact-case 可解析，11 個 JSON 範例可解析。
- PowerShell Parser 對 9 個教學 code blocks 語法檢查成功。實際安裝 API
  如上另行執行；語法檢查不宣稱逐字執行了整份 shell 教學。
- `git diff --check` passed。
- Immutable author subject `c2337d44811371db19215c629c67e15a3bc4c1ac` 的
  `python -I -B .github/scripts/check-source-change.py --base dd1453e8cf23bf62a5b28c70ed08f475856dda41 --head c2337d44811371db19215c629c67e15a3bc4c1ac`
  passed：content／whitespace 與 source suite 47 tests，zero failures/errors/skips；
  全命令 26.437 seconds，suite 2.271635 seconds。Admission 未由此本機檢查評估。

### 獨立審查與處置

Reviewer `/root/manuals_review` 以 `bounded-general-worker`
（gpt-5.6-terra/xhigh）及 `code-reviewer` 對
`dd1453e8cf23bf62a5b28c70ed08f475856dda41..c2337d44811371db19215c629c67e15a3bc4c1ac`
執行獨立唯讀審查。核對安裝 archive、18 skills metadata、知識宣告、
maintenance API、三例 apply 證據、release packaging 與 selector；未評估
runtime／hosted／recovery／agent 行為。操作、preset、maintenance、recovery
限制及 selector 行為與所檢來源相符。

初次結果為 `needs-parent-decision`：RC4 ZIP 沒有 `docs/`，generic README
也沒有手冊入口；另外提示相對 source links 可能隨分支漂移。Root 核對後：

- ZIP 缺少手冊入口的事實成立，列入下一版 release handoff。原文沒有要求
  讀者從 archive 取得手冊；owner 的本次交付位置為來源庫 `docs/`，未選定
  自包含 ZIP 文件產品。因此這不是缺少本次要求的文件，亦不擴大到修改
  release builder、payload closure 或已發布 RC4。
- 補明手冊是線上來源文件、RC4 ZIP 不含手冊及連結，而命令不需 checkout。
- 安裝 schema、binding schema、breaking reinstall 契約改連 RC4 固定 tag；
  相對 skill source links 明示為查閱用，實際指令以 installed bytes 為準。
- 文件修正後需以新的 immutable subject 再審受影響段落；原審查沒有直接
  延伸為新內容已通過。

## 建議的下一版收斂方式

優先準備 `0.19.0` stable 的單一新 candidate；只有教學／實際使用情境
揭露產品缺陷或修正需要再觀察時，才使用最後一個 RC5。這是建議，尚未
選定或建立 tag、Release、CI dispatch 或下游升級。

正式版前的具體驗收：

1. 整合本次文件及必要修正，固定 candidate；實際 current-head Source change
   gate、必要 independent review、manifest／ZIP／digest 都綁同一內容。
2. 用選定的空白專案驗證無知識、common、common+.NET 的安裝／讀回；
   驗證新增／移除的正式承諾若列為支援，另選最小代表情境。
3. 對兩個 adapters 的實際 discovery／代表任務取得對應結果；例如無知識
   review 誠實揭露缺口，以及已採用 .NET binding 的 review／slice 使用
   選定資源。Static metadata／本機檔案不能替代 agent 行為。
4. 明列 stable 支援範圍：若只發來源套件，不宣稱 target rc-to-stable
   update/rollback、跨電腦 recovery、未選 target adapters 或完整 P7 已完成。
   若要宣稱上述任一能力，必須補該能力的真實驗收，不能自行改成 waived。
5. 在下一版 Release／archive README 提供可從發行入口找到的版本固定手冊
   連結；若改選內附文件，另明確修改 payload closure 並驗證。現有 RC4
   archive 不含這次手冊，不能把本次來源文件完成當作 archive 入口已完成。
6. 按 release owner 決策建立新 stable tag/build、讀回 hashes 和 provider，
   審閱 release notes 後發布。文件完工不等於發布完成。

R3/R4 是原 pilot 的 stable update／cross-computer 義務，不是所有來源套件
使用者的自動前置條件；R5 的普通 source CI 已恢復，native/P7 仍分開；
R6 的 target decision adapters 屬可選專案邊界；R7 的最終版本證據仍必須新綁。
Retired full/history/high-I/O suites 不因準備 stable 就自動復活。
