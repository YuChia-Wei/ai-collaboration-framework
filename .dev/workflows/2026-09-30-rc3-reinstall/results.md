# RC3 四項工作與打包／重裝評估

本次批准的四項工作均完成本地實作與選定驗證。RC3 catalog、獨立 engine、
source/MQ subsets，以及兩個 F: Git worktree 的實際破壞性重裝均通過。
這份結果覆蓋打包、安裝檔案與設定讀回；原始 18 項需求的其餘行為驗收、
CI 與發布各自保留原有狀態。

## 四項成果

| 工作 | 結果 | 證據 |
| --- | --- | --- |
| S1/T1：退休 portable workflow v2 | 產品、manifest、profiles、source selection 與實際安裝均移除 software-development-orchestrator；保留 source／target 工作紀錄 | 17 個 skill IDs；兩套 adapters 各 17 entries；舊入口 absent |
| S2/T2：三個 author IDs 與搬移文件 | adr-author、lesson-author、pr-author；ADR/Lesson/PR record family、schemas、IDs、writer locks 保持。34 份文件逐份處置：29 include、3 consolidate、2 retire | [逐份處置與最初 18 項要求](knowledge-disposition.md)；metadata／manifest／reference／anchor 閉合與實際 catalog/subsets |
| S3/T3：Git-backed breaking reinstall | 新增 pinned engine 內的 tools/reinstall-framework.py；完整分類、Git HEAD／preimage、保留 pins、外部 preview、清理後 API 2 安裝與讀回 | [操作契約](breaking-reinstall.md)；邊界 suite 15 passed／1 host symlink fixture skip；native/dense 限定檢視 |
| S4/T4：F: 實測 | source 與 mq lab 的 public plan/apply/inspect，以及六次 installed author explain 均成功 | 下表與保存的 request/result/invocation/readback-summary |

原 task table 的 S1/T1 同時包含退休與三個 ID 改名；S2/T2 是 34 份文件整理。
上述成果依內容合併說明，task IDs 與 ownership 保持不變。

workflow／assessment 的整理、壓縮與線上儲存另屬 [v0.20.0 #416](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/416)。
本次保留一般 workflow 與工作產物；可攜 workflow 組織能力已依後續 scope 退休。
因此「本次四項完成」不能換算為最初 18 項全部完成。

## 固定候選與實測

產品候選 source commit：`bdb5bbec012e86f5d9486dadd9872ecbbb5a4e0a`。
Catalog identity：
`catalog:1:0.19.0-rc.3:bdb5bbec012e86f5d9486dadd9872ecbbb5a4e0a:ccc6cc2b8ed71f3440a82f411f32d429a0c7b1ae1cd8c695ac53bb4c622726e5`。
所有 public build/derive commands exit 0；獨立核對 raw hashes、sizes 與完整 file closure。

| 產物／操作 | Source | MQ lab |
| --- | ---: | ---: |
| Skills | 17 | 17 |
| Knowledge packages | 0 | 2 |
| Managed members | 141 | 404 |
| 清理的舊檔案（含後續被新套件取代者） | 150 | 462 |
| 安裝後確認不存在的 obsolete paths | 45 | 122 |
| Scoped 保留檔案 raw hashes 相符 | 2,237 | 568 |
| 額外保留的 scoped 外 role files | — | 8 |
| 明確 project edit 前像／後像 | 4 | 35 |
| Codex／Claude entries，各 | 17 | 17 |
| Source-free subset derive，秒 | 7.276 | 11.842 |
| Real plan，秒 | 60.806 | 35.032 |
| Real apply，秒 | 138.474 | 139.714 |
| Public inspect，秒 | 1.706 | 4.188 |

Catalog assembly 72.192 秒：17 skills、2 knowledge、372 inventory members。
Engine 包含 24 pinned files 與 descriptor；bootstrap/state AST closure、Git raw
與執行 bytes、出貨檔案 hashes 均一致。

Source subset identity：
`subset:3:0.19.0-rc.3:bdb5bbec012e86f5d9486dadd9872ecbbb5a4e0a:ed33214b1d60a67bce077d217309eba46ef1528d20895429477bccc0cee23ae2`。
MQ subset identity：
`subset:3:0.19.0-rc.3:bdb5bbec012e86f5d9486dadd9872ecbbb5a4e0a:65b2fcd6207aabc970773cb61a7aebeb43af78652171c69917bdcb7133a8e9fa`。

兩次 apply 的 outcome 均為 `reinstalled`；public inspect 均為
`managed-bytes-consistent`，無 drift。三個 author 的 installed `explain`
在 source 與 MQ 均為 `succeeded`、無 mutation；這是設定／安裝工具讀回，
不是全部技能在真實專案情境中的執行驗收。

Source baseline 為產品候選 commit；實測後提交
`df0f557487403ba0d48563f36fc6ae291bf20876`，其 generated installation 由
`7f81146f9418bb663b245f51e9083d436cb20f06` 整合至 coordinator branch。
MQ baseline 為 `441009dd550f5ca7f40d94dcbf0c28290cf39ac0`，包含主要 checkout
原已 staged 的五份 owner deletions；實測後 fixture 提交為
`2ed977371e20a1e479248be64652695bce232ef1`。
後續 closeout 文件不改寫已驗證的 candidate／lock bytes。

## 保留與清除邊界

MQ 原 468 份可重寫／移除 framework 資源，六份現行導覽使用精確替換 intent，
其餘 462 份逐檔清理。不是因不確定而保留過時 tracked framework 檔案。
原始 user-staged 五份刪除先複製到隔離 baseline，主要 checkout 的 index 不變。

真正 workflow 目錄的 records／outputs、assessments／work products、產品 specs、
教學文件、自有 guides、role settings 與 adopted target semantics 均有明確分類。
僅 workflow 頂層 README／INDEX 依批准的導覽例外替換；不改工作目錄中的紀錄。
保留 568 份 scoped files 加八份 roles，共 576 份完整 raw hashes。
三個 namespace 的設定映射後，其 store/template/constraints 值維持原意；
其餘三個有效 record stores 原值不變。

MQ 40 個 knowledge bindings 的 canonical hash 維持
`95ce1f6064ac729387d0e28f438900bf7d902e8d9ba85e34ba823e9649c7930e`。
TARGET-ENGINEERING-RULES.md 的 raw hash 維持
`e46c6527b6cb7bf9cd9ef5c3cb19c0f9e36c38dd8ecdeda546c5c273b87d4c08`。
主要 MQ checkout 仍為 `bd9f9da6a4460336c3921686b76d4a2b9ca4547b`，五份
staged deletions 的完整 patch hash 前後皆為
`dad169f1e5d43db193f405ac681db7e08633e0d323d452d43f0286f8cfa94917`。

此模式明確為 breaking、non-atomic；Git 負責 committed cleanup 還原，
普通 API 2 journal 負責新安裝。未追蹤／ignored 資料不會列為 cleanup，
所有 scoped files 都須有保留、清理或 edit disposition。RAM fixture 僅宣告
process-termination failure domain，不宣稱 SSD durability 或效能提升百分比。

## 失敗嘗試與修正

| 嘗試 | 結果與修正 |
| --- | --- |
| 初始 candidate 準備 | 錯誤 Git ref／pin shape 被拒；舊 bundler 漏新 entry，22-file engine 不符合新 24-file closure。未進行 apply |
| b162 catalog | GitSource closed allowlist 漏 tools/reinstall-framework.py；invalid-shape，修正於 5df0 |
| Source 5df0 real plan | 保留歷史中文 assessment filename 被 portable path 拒絕；changed=false、removed=[]。5fcc 加入安全 native preservation；cleanup 仍 portable |
| Source 5fcc real plan | Preview 寫大量 sibling files 導致重複 listing 耗盡 scan bound；changed=false、removed=[]。bdb5 改為寫入前觀察與寫入後完整 bounded snapshot；limits 不變 |
| Lesson focused C4 | 改名後 config namespace 殘留；修正後重新驗證。初次 failed log 保留 |
| Archive measurement | Windows DirEntry.stat 的 identity 欄位零值使 harness 誤判；改用 Path.lstat，四份完整 archive 相符，第一次測量失敗保留 |

15 passed／1 skipped 的邊界 suite 使用 actual Git fixtures，但 installer 由 mocks
控制。另有 actual ADR 32、Lesson 44、PR 24 launches 的 focused checks；PR
provider transport 為 synthetic。這些證據與本節兩次真實 reinstall 分開記錄。
兩個 native tests 與一個 dense test 的限定獨立檢視未找到支持的新缺陷，
不代表完整 release independent admission。

## 證據與交付

持久 evidence root：
`C:/Github/YuChia/ai-collaboration-prompts-dotnet-backend/.dev/ai-context/local/rc3-final-evaluation-20260930/`。

- `candidate/`：catalog、engine、source/MQ subsets、independent pin、selections、public invocation records；共 955 檔與 F: 產物完整 raw bytes／directory sets 相符。
- `attempts/`：每次 real trial 的 request/result/invocation/readback；保留先前失敗。
- `archive-verification.json`、`native-review/`、`dense-review/`、`skill-checks/`、MQ inventories/navigation manifest 與 primary staged patch。
- `final-handoff.json`：closeout commit、固定候選、worktree／branch、primary state 與 current-product byte rebind；於最後本地提交後填入。

Source 成果 branch 為 `codex/2026-09-30-rc3-reinstall`，worktree
`F:/framework-next/rc3-coordinator`。Source／MQ 本地 commits 與 refs 都位於
各自 C: repository 的 shared Git object store；未 push、PR、merge、tag、發布
或關閉 Issues，也未將 MQ primary 切换成 RC3。

U001 保留完整 legacy／history／behavioral matrices、hosted CI、independent
release admission 為 `deferred-by-owner`，owner 為 program #322 coordinator/P7；
下一步是 owner 選定其恢復／驗收範圍。初始 stale graph 僅使用明確 tracked-file
fallback，未以 graph 無搜尋結果宣稱 absence。此 workflow 的四個本地 tasks
完成，Issue #415/#417 與 release/adoption 狀態仍獨立。
