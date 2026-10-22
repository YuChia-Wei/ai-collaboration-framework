# 專案 skill 的原稿、升級比較與明確路由

專案 skill 可以保留自己的原稿、資源與客製意圖，再明確選擇保留、共存或轉用
framework skill。Registry 保存這些決策的引用；檔案相符、owner 採納與 runtime
已探索各自需要對應證據。

本頁描述目前來源的 skill 管理能力。使用前核對實際取得的 engine 是否含有
`src/tools/manage-skills.py`，以及獨立取得的完整 pin；來源實作不表示已公開發布、
已升級既有專案或已在目前 AI session 載入。

## 所有權

| 內容 | Owner 與操作 |
| --- | --- |
| `.ai/core/skills/` 與 framework lock 登記的 native entries | 原 installer 維護；本工具不覆寫 |
| `.ai/project/skill-registry.json` | 專案所有的 version 1 registry，透過明確 plan/apply 更新 |
| `.ai/project/skills/<project-id>/` | 自建或明確衍生的原稿、參考資料與程式資源 |
| `.agents/skills/<runtime-id>/`、`.claude/skills/<runtime-id>/` | 依 registry 明列 mapping 建立的專案投影 |
| 未登記 entry、同目錄中的 unknown 檔案 | 保留原 owner；相同內容也不自動接管 |

新專案使用 `.ai/project/`；只有 legacy `.ai/custom/` 時，reader/writer 一致沿用
舊根並回報實際位置。兩根同時存在會停止，須先釐清來源。Registry 不加入
framework lock，也不是所有 custom 資源受到保護的先決條件。

## 多檔 skill 與資源閉包

`skills` 以 project ID 索引。每筆保存 `origin`、`source_ref`、`intent`、`acceptance`、
`capabilities`、完整 `members` hashes、可用的 `baseline`、`projections` 與
`integration`。來源及決策引用是 caller 提供的紀錄；工具不獨立驗證作者身分、
人的同意或語意涵蓋結論。

`members` 的 key 是相對原稿目錄的路徑。每個 adapter 的 projection 明列
`runtime_id` 及 `files` mapping；mapping 的 key 是相對 native skill 目錄的
目的路徑，value 是原稿 member。例如：

```json
{
  "codex": {
    "runtime_id": "team-review",
    "files": {
      "SKILL.md": "entries/codex.md",
      "references/checklist.md": "references/checklist.md",
      "scripts/check.py": "scripts/check.py",
      "scripts/support.py": "scripts/support.py"
    }
  }
}
```

必須有 `SKILL.md`，且 YAML frontmatter 的 `name` 必須等於 `runtime_id`。
Codex 與 Claude 可選不同 entry 原稿並共享其他資源。`SKILL.md` 中的相對連結
與 script 的 sibling imports 需符合投影後的結構；工具不猜測或改寫這些參照。

首版接受有界 UTF-8 資源，不支援 opaque/binary assets。錯 hash、漏掉 declared
member、不安全或大小寫別名路徑、不合法 mapping 與不支援內容會在寫入前或
resolve 時拒絕。一般 native skill 不需要 framework metadata；若宣告支援的
`skill-package.yaml`，才使用既有 package/reference reader 檢查其契約。

## 公開管理介面

從與 pin 完全相符的 engine 執行，使用 stdin 傳入 JSON：

```text
python -I -B <engine-root>/src/tools/manage-skills.py < request.json
```

每個 request 都需要 `engine_root` 與獨立取得的完整 `engine` pin。歷史
23、25、26、27-file closure 保留為讀取資料，不是新入口的 execution fallback。
以下省略共同 pin 欄位：

| operation | 主要輸入 | 證據／結果 |
| --- | --- | --- |
| `registry-inspect` | `project_root` | 實際 registry、來源、local delta、資源／投影觀察與 managed/unknown 狀態 |
| `registry-plan` | `project_root`、`proposed`、`files`；可選 `adopt`、`detach` | 完整 preimages 與 plan hash；無寫入 |
| `registry-apply` | `project_root`、原 `plan`、`plan_sha256` | 寫入原稿／投影，最後發布 registry；支援精確續作 |
| `skill-compare` | `project_root`、`candidates` | baseline/local/candidate 三方差異及待比較的重疊線索 |
| `route-resolve` | `project_root`、`purpose`、`adapter` | 驗證明確路由的完整資源；不選模型、不執行 skill |

`files` 使用完整專案相對路徑作 key，value 是 UTF-8 原稿文字；只接受所選
project skill 的 declared members。未提供的 member 讀取既有原稿並核對 hash。
先 inspect、編輯 proposed、取得 plan，再檢視與 apply；不要從空白範例覆蓋
現有 registry。

## 比較、採納與路由

候選提供 `id`、`ref`、`capabilities`、`files` 與 `runtime_paths`。三方比較使用
baseline/local/candidate 的 member 聯集，包含新增與刪除；區分 local-only、
candidate-only、same-change、conflict，缺 baseline 明示 unknown。名稱、能力
或 native path 重疊只產生比較或碰撞線索，不代表語意等效。

`integration` 的 coverage、status、candidate/evidence/decision references
和實際 route 分開；即使記錄 framework 已涵蓋需求，也可保留 local route。
工具不因文字相等或 coverage 標籤，自動刪除客製、改 route 或宣稱 owner 採納。

`routes` 以 purpose/adapter 選擇 project 或 framework：

- Project route 使用 registry project ID，驗證完整原稿和該 adapter 的全部投影。
- Framework route 使用 canonical skill ID 及預期 entry hash，從已驗證安裝的
  binding/owner 找出真正的 original 或 prefixed native entry，並驗證必要資源。

缺 route、未安裝、錯 owner、錯 hash 或資源漂移均停止。框架 ID 不一定等於
native 目錄名；不能靠同名或檔案順序猜測優先權。選擇 route 也不會自動影響
provider 的自動探索或既有 session cache。

## 明確接管、共存與解除投影

`adopt` 明列 `{ "<native-member-path>": "<current-sha256>" }`。既有 unowned
檔案即使 bytes 完全相同，也需這個明確 preimage；已登記投影被外部修改後，
重新接受也需明確處理。真正 lock-owned 路徑永遠由 installer 維護。

換名共存時，同時更新 entry 的 frontmatter name、runtime ID 與 projection
mapping，並用 `detach` 列出退出新 projection 的舊 member 路徑。工具只移除
已登記且仍符合原 hash 的選定檔案，不遞迴刪除 native skill 目錄。未列出的
unknown siblings、原稿與 baseline 保留。解除投影／路由時保留既有 skill record、
provenance 與 baseline；`registry-plan`／`registry-apply` 拒絕刪除既有 record。
這個操作不提供原稿或歷史紀錄刪除。

採用 framework skill 時，先保留客製原稿及 owner 決策，再明確處理會碰撞的
project projection，交給原 installer 安裝 framework entry。安裝成功後讀回
framework route；尚未安裝的 metadata 不能證明已切換。

## 寫入、恢復與目錄遷移

管理器與 installer/project-layout 共用 writer 排他。Apply 完整核對 lock、
registry 與檔案 preimages，先寫資源與精確 detach，最後發布 registry。這是
可續作的多檔操作，不是跨檔 atomic transaction。

中斷後保留原 plan 與 hash，明確重試。每個檔案只能處於已接受的 before 或
已寫入的 after 狀態；外部變更會阻擋。完成後重播要求 after-state 仍相符，
已 detach 的舊檔案重新出現時，即使 bytes 與以前相同也不能再刪一次。
外部編輯器仍需由 caller 停止；遺留 writer guard 須確認原程序已停止後由 owner
處置，不自動清除。

Legacy layout 的明確遷移沿用 pinned `manage-sub-agents.py` 的
`layout-inspect`、`layout-plan`、`layout-apply`。新 engine 同時處理已登記 skill
原稿與其相符投影內的舊根參照，更新 member hashes；保留 provenance、baseline、
意圖與決策引用。未知檔案和空目錄隨 rename 保留，未登記 native entry 不改寫。
遷移不安裝新版 skill，也不把既有 managed drift 重新接受為正常。

## 驗收時分開回報

| 證據 | 可支持的結論 |
| --- | --- |
| Registry schema 與 references 有效 | 輸入結構與選定資源契約有效 |
| 實際 plan/apply 及 hash 讀回 | 所選原稿／projection 已寫入並相符 |
| 原 installer 的實際碰撞／選配移除結果 | 被測 consumer 的保護與安裝邊界成立 |
| Native skill list | 該 runtime 在該次探索找到 entry |
| Native 檔案讀取及相對資源定位 | 所選資源在該 runtime 檔案介面可讀 |
| 實際執行符合原 AC | 只支持該行為情境，不擴大成所有模型／平台保證 |

Codex 與 Claude 各自取得原生證據。沒有 runtime 介面或帳號時保留未驗證；
目錄、registry 或另一 runtime 的結果不能代替。這個管理器不登入帳號、呼叫
付費模型或讓 skill 綁定 sub-agent 模型政策。
