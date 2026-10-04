# 工具型 skills 共通設定

[回手冊首頁](README.md) · [Skill 目錄](skills/README.md)


以下五個 skill 不是只靠自然語言說明；它們有套件自有 Python 公開工具：`adr-author`、`lesson-author`、`local-backlog`、`pr-author`、`problem-frame-author`。每次執行都要傳入**絕對** `project_root` 與指向已選安裝副本的**絕對** `package_root`；不能由目前工作目錄、上層目錄或環境變數推測。`project_config`、`local_config`、`overrides`、`write_roots` 都是可選且必須明確傳入的 request 欄位。沒有指定設定檔時才使用 package default；明確指定但不存在的設定檔是不可用，而不是空設定。

project config 的頂層是 `config_version: 2`，以 `skills.<skill-id>` 放設定，以 `constraints.<skill-id>` 放 project-only 約束；local config 只有 `config_version` 和 `skills`。例如 ADR 的設定 namespace 是 `skills.adr-author`，寫入範圍是 `constraints.adr-author.write_roots`。設定選項本身不構成實際寫入授權；request 的 `write_roots` 只能縮小、不能擴大 project 允許範圍。若在 Git 專案選用 local config，它必須已忽略且未追蹤；工具只用唯讀 Git 證明此事，絕不修改 ignore 或 Git 狀態。

| Skill | 設定 namespace / 預設 store | 公開工具 | 基本 runtime 與寫入限制 |
| --- | --- | --- | --- |
| `adr-author` | `skills.adr-author` / `notes/adrs`；`constraints.adr-author` | `python <package_root>/scripts/adr.py --request <absolute-request.json>` | Python >=3.11,<4、PyYAML >=6,<7、jsonschema >=4.18,<5、明確 filesystem roots；更新用實際 `expected_sha256`，單一 record 原子寫入。 |
| `lesson-author` | `skills.lesson-author` / `notes/lessons`；`constraints.lesson-author` | `python <package_root>/scripts/lesson.py --request <absolute-request.json>` | 同 ADR；v1/v2 config 不會自動轉換，`accept` 額外需要 project 設定的決策證據來源。 |
| `local-backlog` | `skills.local-backlog` / `notes/work-items`；`constraints.local-backlog` | `python <package_root>/scripts/local_backlog.py --request <absolute-request.json>` | Python/PyYAML/jsonschema、filesystem；建立與更新需要同目錄原子寫入和可用本機 backend。 |
| `pr-author` | `skills.pr-author` / `notes/pull-requests`；`constraints.pr-author` | 本機 record：`python <package_root>/scripts/pr.py --request <absolute-request.json>`；GitHub：`python <package_root>/scripts/github.py --request <absolute-request.json>` | 本機操作需 Python/PyYAML/jsonschema/filesystem/Git。provider 操作另需現有 Git、`gh`、已授權的 GitHub 認證和精確 grant；不會登入、存 token 或補發 credential。 |
| `problem-frame-author` | `skills.problem-frame-author` / `specs/problem-frames`；`constraints.problem-frame-author` | `python <package_root>/scripts/problem_frame.py --request <absolute-request.json>` | Python/PyYAML/jsonschema/referencing、明確既有本機 roots；CBF create 需要已存在的 destination ancestors 與支援 hard link 的本機 NTFS 或 Linux ext4/xfs/btrfs/tmpfs。 |

所有工具 request 都是單一嚴格 UTF-8 JSON object，且以 `operation` 選定公開操作；未知欄位和憑證欄位會失敗。先執行 `explain` 是安全的方式，可讀出實際生效設定、來源、鎖定欄位及可寫根目錄，但它不建立 store，也不證明 runtime 或寫入權可用。對既有 record 的寫入必須先 `inspect`，再使用工具回傳的 digest；失敗或不確定寫入必須先讀回，不能盲目重試。

`adr-author`、`lesson-author` 的預設 store 缺少父目錄時，只能在 project 和 `write_roots` 都允許的範圍建立；`local-backlog`、`pr-author` 同樣限制建立 parent，並保留失敗時已建立的空目錄。`problem-frame-author` 不建立任何 ancestor。五者皆拒絕預設 volume root、路徑走訪、UNC/device/drive-relative path、symlink/junction/reparse point 與 package/config/template 重疊；外部絕對 store 另需明確 project `write_roots` 和實際任務授權。

`pr-author` 的 `provider-create` 與 `provider-update` 僅支援 GitHub.com 同 repository 的 draft PR。建立/更新前要以 `render` 搭配 `repository_root` 取得 `subject_verified=true`，提供 record/template/body SHA-256、`coordinated-single-writer` mode 和覆蓋同一 target/body digest 的 grant。它只會建立或更新 PR 的 title/body；不支援 push、merge、close、auto-merge、review、labels、Issue/Project、release、branch 或 credential 動作。

### 五個工具型 skill 的操作意義

| Skill | 唯讀操作 | 寫入/狀態操作 | 特有語意與限制 |
| --- | --- | --- | --- |
| `adr-author` | `explain`、`query`、`inspect`、`validate`、`render` | `create`、`revise`、`derive`、`decide`、`retire`、`supersede` | `create`/`derive` 前先以實際 query 選新身分；`revise` 只改 draft；`decide` 讀設定的 decision source 並接受既有 option 或拒絕；accepted 才能 supersede。 |
| `lesson-author` | `explain`、`query`、`inspect`、`validate`、`render` | `create`、`revise`、`derive`、`accept`、`retire`、`supersede` | `accept` 讀設定的 decision source；v1 是只讀相容資料，修正/提升要以 `derive` 建新 v2 identity。 |
| `local-backlog` | `explain`、`query`、`inspect`、`render` | `create`、`revise`、`transition` | `transition` 是明確 state 變更；必須先讀現有 record 並使用回傳 digest，不能假設失敗會回滾。 |
| `pr-author` | `explain`、`query`、`inspect`、`render`、`provider-read` | `prepare`、`revise`、`provider-create`、`provider-update` | `prepare` 固定真實 base/head Git comparison；source 改了必須重新 prepare。provider write 是另一個明確授權動作，且不更新本機 record。 |
| `problem-frame-author` | `explain`、`inspect`、`validate`、`render` | `create` | `draft`/`review-draft` 是另行的 instruction 操作，可依請求輸出草稿或審查結果；CBF tool 不提供 query/revise/delete/migration，`create` 只接受呼叫者給的新 identity，絕不覆寫。 |

以下 JSON 是每個工具 envelope 的最小 `explain` request。把檔案存成 UTF-8，
將範例磁碟根目錄換成實際存在、已選安裝的路徑。CLI 的 `--request` 請提供
**絕對檔案路徑**；上表的 request 路徑是需替換的參數，不是相對檔名。
它們只讀設定，沒有建立 store 或 record。

`adr-author` 的 `request.json`：

```json
{"operation":"explain","project_root":"C:\\work\\my-project","package_root":"C:\\work\\my-project\\.ai\\core\\skills\\adr-author"}
```

`lesson-author` 的 `request.json`：

```json
{"operation":"explain","project_root":"C:\\work\\my-project","package_root":"C:\\work\\my-project\\.ai\\core\\skills\\lesson-author"}
```

`local-backlog` 的 `request.json`：

```json
{"operation":"explain","project_root":"C:\\work\\my-project","package_root":"C:\\work\\my-project\\.ai\\core\\skills\\local-backlog"}
```

`pr-author` 的 `request.json`：

```json
{"operation":"explain","project_root":"C:\\work\\my-project","package_root":"C:\\work\\my-project\\.ai\\core\\skills\\pr-author"}
```

`problem-frame-author` 的 `request.json`：

```json
{"operation":"explain","project_root":"C:\\work\\my-project","package_root":"C:\\work\\my-project\\.ai\\core\\skills\\problem-frame-author"}
```

實際讀寫 operation 按各自 `references/operations.md` 所列欄位加上 `reference`、實際 `expected_sha256`、完整 `content`/`record` 等資料；不要以範例 placeholder 或自造 hash 取代工具讀回的值。

例如已安裝 ADR 後，可使用[安裝手冊](installation.md)建立的 Python venv：

```powershell
$SkillPython = 'C:\aicf\venv\Scripts\python.exe'
$SkillPackage = 'C:\work\my-project\.ai\core\skills\adr-author'
$RequestPath = 'C:\aicf\adr-explain.json'
$ExplainRequest = @{
  operation = 'explain'
  project_root = 'C:\work\my-project'
  package_root = $SkillPackage
}
[IO.File]::WriteAllText($RequestPath, ($ExplainRequest | ConvertTo-Json -Depth 20), [Text.UTF8Encoding]::new($false))
& $SkillPython (Join-Path $SkillPackage 'scripts/adr.py') --request $RequestPath
```

記錄驗證／寫入等操作另需要 `jsonschema>=4.18,<5`；CBF tool 的 runtime
另列 `referencing`。使用相同 interpreter 依實際 metadata 安裝依賴，
例如 `& $SkillPython -m pip install 'jsonschema>=4.18,<5'`。
`explain` 成功不等於 `create` 或 provider 操作的所有相依已備齊。


## 共通操作怎麼選

| 操作 | 目的 |
| --- | --- |
| `explain` | 讀取有效設定及其來源，先找出 roots、constraints 與尚缺設定 |
| `query` | 在已選 store 查詢既有資料，避免未查就新增；CBF tool 沒有此操作 |
| `inspect` | 讀取精確 record 與 digest，作為後續操作的輸入 |
| `validate` | 檢查選定 record 的結構；只在該 skill 宣告此操作時使用 |
| `render` | 依指定 record／模板產生 Markdown 結果；不是發布或自動保存成果 |
| `create`／`prepare` | 建立新的本機 record；PR 使用 `prepare`，其他按 metadata 選擇 |
| `revise` | 在可修改的 lifecycle 狀態更新內容，保留 identity，使用先前 digest |
| `derive` | 從既有資料建立新 identity，保留來源關係；不就地覆蓋舊版本 |
| `retire`／`supersede` | 記錄停止使用或替代關係；不是刪除原始歷史 |

若 `explain` 回報選定目錄不存在，先依專案授權建立實際需要的目錄，再重新讀取。
特別是 CBF 的 store、write roots 與所有 ancestors 必須已存在；不要假設工具會補齊。
以上五份 JSON 是最小設定讀取範例，沒有包含建立 record 所需的完整業務內容。

## 自訂設定範例

以下內容可儲存到專案選定的 JSON 檔；路徑不是框架強制標準。
先確定 `notes/adrs` 是你要管理的目錄，再將設定檔絕對路徑傳入 request 的
`project_config`。`installation.json` 管安裝選擇，這份設定管 skill 作業，兩者勿混用。

```json
{
  "config_version": 2,
  "skills": {
    "adr-author": {
      "store": {"kind": "filesystem", "root": "notes/adrs", "tracking": "tracked"}
    }
  },
  "constraints": {
    "adr-author": {"write_roots": ["notes/adrs"]}
  }
}
```

其餘 namespace 請按各 skill 的 configuration reference 設定；不要將 ADR 的
欄位整份複製給其他工具。變更 store 選擇不會搬移、升級或合併既有資料。
工具回傳非成功時，保留 outcome、mutation state 與 diagnostics；
`unknown` mutation 需要先讀回實際狀態，再決定復原方式。
