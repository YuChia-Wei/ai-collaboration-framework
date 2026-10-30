# 路徑預算與拒絕處理

[安裝手冊](installation.md#2-目錄與工作目錄規則) · [精確復原](recovery.md)

這份說明適用目前 Catalog 1／Engine 2 的選取與安裝流程。完整路徑上限為
240 個 UTF-16 code units，單一 segment 上限為 255；非 BMP 字元佔兩個單元。
這是引擎的保守拒絕政策，不是 Windows、Git 或所有檔案系統的通用能力上限。
已發布封存檔使用其內附引擎；來源文件更新不會改變舊版的診斷或支援範圍。

## 各階段的責任

| 階段 | 責任與預檢 | 證據邊界 |
| --- | --- | --- |
| Git checkout | Git／執行客戶端建立工作目錄；來源建置要求精確 commit 與來源一致性 | 安裝引擎尚未執行，不會預防 Git 或客戶端註冊失敗；不能將 access denied 推論為路徑超限 |
| 封存解壓 | 解壓工具與操作者選目的地並核對封存／內容 hashes | 引擎不攔截外部解壓；在很深的目錄解壓可能先失敗，應先選短的明確位置 |
| Catalog 建置 | 來源工具 `tools/build-catalog.py` 使用產品 emitter，於配置輸出與 scratch 目錄前檢查選取 payload、metadata 及實際 run 前綴 | 來源工具不屬於下游 engine；來源 checkout 與外部封存寫入另有責任 |
| Engine bundle | 來源工具選定 `engine-output-root`，檢查 `engine-<32 hex>/` 下的 engine 成員與 `engine.json` | 角色為 `output`、階段為 `engine-package`；不是目標專案安裝 |
| Subset | 公開 `engine/src/tools/derive-subset.py` 於配置目錄前檢查選取 payload、metadata、output 及 scratch | 根目錄須直接、明確、既存且符合互斥條件；不能用未選取內容估算通用上限 |
| Plan | 公開 maintenance API 的 `plan` 計算 project、candidate、engine、scratch、staging、recovery；涵蓋控制檔、project edits、同層短名與 recovery objects | 唯讀預覽，不配置 operation、不取得 writer exclusion，也不是原生寫入驗收 |
| Apply | 以真實 operation ID 重查實際布局、碰撞及 volume；預算檢查在首次 guard 寫入前 | 只有成功回應及後續 readback 支持該次配置完成；短根成功不證明近上限成功 |
| Recover | 以原 operation、engine pin、project／recovery 根目錄重查精確布局，再執行 finish／restore | 不得搬移或改名來繞過拒絕；完成的 operation 只能作匹配狀態的唯讀重播 |
| Cleanup | 復原只處理該 operation 的已驗證同層暫存；一般 apply 的移除受舊 ownership 限制，breaking reinstall 另有 Git baseline 與精確清理契約 | 沒有通用遞迴 cleanup 命令；保留的 scratch／staging／recovery 不是可任意刪除的垃圾 |

來源庫另外保留 `tools/build-development.py`、`tools/build-candidate.py` 與
`assembly.assemble*` 的 schema-1／schema-2 相容入口。它們不等於目前
Catalog／Engine 2 發布與安裝路線，本次近邊界驗收不將它們納入新的支援承諾。
維護舊格式須先選定其相容版本、既有支援義務及可用程序；檔案仍存在或使用
同一個 `OwnedDirectory`，都不能證明它具有目前 emitter 的整體預檢或驗收。

## 依選取布局計算

對每個根角色分別列出實際會讀寫的相對路徑。若根目錄沒有結尾分隔符，
令 `R` 是根目錄的 UTF-16 單元數、`L` 是含生成前綴的相對路徑單元數，
非空 member 的完整長度為 `R + 1 + L`；根本身則為 `R`。每個 segment
也要計量。`R <= 240 - 1 - max(L)` 只是在這份選取布局的必要條件，
仍須通過根目錄、相對名稱、containment、碰撞、檔案系統及復原契約。

計算時至少包含：

- Catalog／subset output：`catalog-<32 hex>/...` 或 `subset-<32 hex>/...`；scratch 則是 `scratch-<32 hex>/...`。payload 與 metadata 都算。
- Project：新舊 managed members、明列 project edits、protected inputs、lock／markers／guard，以及每個受影響父目錄下的 `.fi-<12 hex>`。
- Candidate／engine：實際選取的 payload、metadata 與 pin 所列 engine 成員。
- Scratch：`i-<32 hex>/` 下的候選 metadata、`plan.json` 與 lock。
- Staging：`i-<32 hex>/` 下的 add／change destination 與 lock。
- Recovery：`i-<32 hex>/operation.json` 與 `i-<32 hex>/objects/<64 hex>`；最後一個相對布局為 107 個 ASCII 單元。

`plan.details.path_budget` 回報選定布局的 `checked_paths`、
`maximum_full_path_utf16`、`maximum_segment_utf16` 與上限。它不提供通用
53／80 字元根上限；[安裝手冊](installation.md#2-目錄與工作目錄規則)中的
v0.19.0 例子是歷史選取計量，不能套用到新版或另一份 selection。

## 讀取診斷與下一步

`path-budget` 保留 `unsupported` 拒絕語意。maintenance API 維持原有
`diagnostics[].code/path/reason/next_action`；`reason` 指出穩定階段、根角色、
根長度、完整路徑／最大 segment 的實測單元數與上限，`path` 僅為有界相對路徑。
不輸出主機根目錄或底層例外字串。Catalog／subset CLI 的錯誤 JSON 維持
`outcome/code/reason` 三個欄位，將同一診斷、相對 member 與下一步放入 `reason`；
消費者應依 `code` 分類，不依自然語言文字解析固定 schema。

生成或 plan 超限時，縮短診斷指定的根角色並重新計算全部布局；apply 前須重新
產生並審閱 plan。若已存在 operation，先保留它並走原始路徑上的精確復原。
不修改主機全域 long-path 設定來跳過預檢。

若相對布局即使放在最短根也無法容納，須改選支援的 package／layout，或由來源
擁有者修正再重新產生；不能手動改 managed 檔名。`path-limit` 表示更早的相對
路徑長度／深度限制，縮短根無法解決。權限、非直接根、來源 bootstrap、名稱或
客戶端註冊拒絕保留各自分類，不自動改標成 `path-budget`。

原生驗收需另保留候選身分、選取、根角色計量、公開入口回應與 readback，並確認
超限在受影響寫入前停止。segment／相對路徑案例若已被更早限制拒絕，就記錄
該拒絕；不為了湊滿 255 邊界而宣稱存在不可達的成功組合。
