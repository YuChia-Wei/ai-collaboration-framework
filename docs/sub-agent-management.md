# Sub-agent 模型政策、客製資源與升級分流

角色描述工作邊界；模型政策決定每次任務的模型與推理深度。兩者分開維護，
讓模型改版、成本偏好與下游客製不必跟著 framework 發布，也不必修改 managed core。

## 所有權與交付

| 內容 | Owner／更新方式 |
| --- | --- |
| `.ai/core/sub-agents` 與由 lock 管理的 runtime entries | framework 套件，使用原安裝 plan/apply |
| `.ai/project/sub-agent-policy.json` | 專案自有，管理工具只在明確 apply 時更新 |
| `.ai/project/sub-agent-registry.json` | 專案自有的來源、資源閉包、整合證據引用與用途路由 |
| `.ai/project/sub-agents/<project-id>/` | 自建／明確衍生的原稿與必要參考資源，不放進 managed core |
| registry 明確登記的 runtime entries | 專案投影；與原稿相同 bytes，由資源管理 plan/apply 更新 |
| `.codex/config.toml`、`.claude/settings.json` | 專案／runtime 自有，明確檢視與合併必要設定 |
| 未登記、自建或既有本地 agent entries | 保留原 owner，不自動接管、覆蓋或刪除 |

管理工具是 pinned engine 的 `src/tools/manage-sub-agents.py`，不是新 installer
或必裝 skill。只安裝角色不代表外部 engine 已存在。使用與該 engine 完全一致的
pin；更新 framework 不更新 policy、不把它加入 lock，也不擅自採納新版預設。
舊 engine closure 僅可作歷史 catalog/lock 的讀取資料；實際執行仍須驗證現行完整 pin。
Policy 與 registry 是兩個獨立 version 1 格式；調整模型不必改角色內容，調整角色
也不必重新分類所有模型。Registry 不加入 framework lock，不改 installer 的所有權。

## 初始政策與任務選擇

`defaults` 只提出初始政策，不在檔案缺失時偷偷啟用。

| 任務 | Codex | Claude Code |
| --- | --- | --- |
| inventory、translation、synthesis | Luna / medium | Haiku / 不指定不支援的 effort |
| implementation、semantic-review、independent-review | Sol / medium | Sonnet / medium |
| 明確選取 premium 且另行授權 | Astra / low | Opus / medium |

優先用確定性工具完成可機械化工作。分類根據實際任務，role 的 default_task
只是提示。任務／tier mapping、模型 ID、effort 在專案 policy 中可獨立調整。
提高 effort 或採用新模型仍受已接受範圍約束；不能藉改 policy 隱藏新的成本決定。
已知 Astra/Opus 不得配置在普通 tier；未來未知模型的能力／成本分類由 owner 決定。
premium 的 `authority_ref` 只是傳入的授權依據，工具不驗證人的同意、不執行模型。

## Provider 差異

Codex 解析順序為 custom profile > explicit spawn > `[agents]` default > parent。
因此 task 型 Codex profiles 不寫死 model/effort。每次傳入選型值，並明確合併：

```toml
[agents]
default_subagent_model = "gpt-6-luna"
default_subagent_reasoning_effort = "medium"
```

若完整歷史 fork 不接受模型覆寫，使用 fresh bounded context，交代必要來源、
授權與輸出；不能藉由省略 override 回到 Astra。

Claude Code 2.1.251+ 的順序是 invocation model > frontmatter model >
`CLAUDE_CODE_SUBAGENT_MODEL` > main model。角色預設 `model: haiku`，需要時呼叫
明確選 Sonnet。2.1.292+ 才能在呼叫時覆寫 effort，還須模型支援；Haiku 不強套
Sonnet 的 effort。專案環境預設可明確合併為：

```json
{"env":{"CLAUDE_CODE_SUBAGENT_MODEL":"haiku"}}
```

`CLAUDE_CODE_SUBAGENT_MODEL_FORCE=1` 會破壞上述任務選型，
`CLAUDE_CODE_EFFORT_LEVEL` 也可能覆寫 effort。不要強制全域 model/effort；
檢查 managed、local、user、shell 與 provider 限制。內建 Explore/Plan 不受單一
env default 全面保證，須明確選型或使用已檢視的自有角色。alias 隨 provider 演進，
可改用確切 ID；不得把名稱、版本或靜態設定當成帳號可用性／實際扣款證據。

來源：[Codex subagents](https://learn.chatgpt.com/docs/agent-configuration/subagents)、
[Claude subagents](https://code.claude.com/docs/en/sub-agents)、
[Claude models](https://code.claude.com/docs/en/model-config)、
[Claude settings](https://code.claude.com/docs/en/settings)。查核日期：2026-10-22。

## 管理介面

使用隔離 Python，從 stdin 傳入 JSON。每個 request 都需要 `engine_root` 與
獨立取得的完整 `engine` pin，不載入 ambient/source checkout 來補缺檔：

```text
python -I -B <engine-root>/src/tools/manage-sub-agents.py < request.json
```

以下只列 operation 欄位；實際 request 加上上述 engine 欄位。

| operation | 其他輸入 | 結果 |
| --- | --- | --- |
| defaults | 無 | version 1 初始政策與 native settings 建議；無寫入 |
| inspect | project_root | policy、raw SHA、ownership，或 missing |
| plan | project_root、proposed | 綁定前後 bytes 的 plan、plan_sha256；唯讀 |
| apply | project_root、plan、plan_sha256 | 只原子更新固定 policy 路徑；拒絕 stale plan |
| resolve | project_root、adapter、task；可選 tier、authority_ref、observations、profile | task-specific dispatch 建議；缺政策時拒絕，不繼承 |
| compare | baseline、local、candidate（各為 policy document；baseline 可 null） | 三方欄位差異；缺 base 明示，不自動合併／採納 |
| registry-inspect | project_root | 登記來源、local delta、資源／投影漂移、managed drift、未知 entry |
| registry-plan | project_root、proposed registry、files；可選 adopt、detach | 明確原稿與投影變更、全部 preimages、lock pin；唯讀 |
| registry-apply | project_root、plan、plan_sha256 | 寫入選定專案原稿／投影，最後發布 registry；可續作 |
| role-compare | project_root、candidates | 完整 declared members 的三方差異、能力候選與 runtime 碰撞 |
| route-resolve | project_root、purpose、adapter、task；可選 tier、authority_ref、observations | 檢查明確路由的資源閉包，再解析模型選擇 |
| layout-inspect | project_root | 實際專案目錄、完整檔案清單與 lock identity；唯讀 |
| layout-plan | project_root | 從舊目錄遷移的完整前後內容、參照修改與 lock transition；唯讀 |
| layout-apply | project_root、plan、plan_sha256 | 套用已接受的遷移；可續作，拒絕漂移與重播覆寫 |

Policy schema version 1 有 `on_unavailable: stop`、`tasks`、`adapters` 與
`extensions`。正式 reader/writer 為 engine 中的 `distribution.subagent_policy`。
未知版本／欄位拒絕，合法 extensions 保留。更新時先 inspect，修改 proposed，
再 plan/apply；不要用 defaults 取代現有客製。單檔 atomic replacement 搭配
exclusive writer guard，配合 raw SHA 檢查；外部編輯器不遵守 guard 的競爭仍須避免。
遇到遺留 `.json.writer`，確認原 writer 已停止後再由 owner 處理，不自動刪除。

`observations` 是 caller 明確提供的 adapter、runtime_version、models
（每筆 model 與 efforts）、forced_model、forced_effort。無 observations 時只回報
configured/availability unknown；有匹配資料時為 selected/caller-observed，兩者
都不是 invocation observed。`profile` 可提供 model/effort，用於拒絕 Codex 固定
profile 與 task 的衝突。caller 須提供實際有效設定，工具不讀私人 credentials。

## 升級與客製協調

### 專案目錄更名與舊版相容

`.ai/project/` 儲存專案維護的 AI 設定、選擇、資源與登錄。它和框架管理的
`.ai/core/` 分開；目錄名稱表達管理歸屬，registry 保留內容來源與整合證據。
共用目錄遷移同時處理已登記的 sub-agents 與 skills；技能的多檔投影與
客製協調規則見[專案 skill 管理](skill-management.md)。

新專案使用 `.ai/project/`。若只有 `.ai/custom/`，新工具繼續從該目錄讀寫，
回報實際路徑；不會將舊 registry 誤認為空白，也不會暗中建立第二份政策。
兩個目錄同時存在時，即使內容相同也停止，須先由專案釐清唯一來源。
舊版 v3 role policy 路徑及既有 23、25、26、27 檔 engine closure 保留讀取相容性；
執行仍須提供目前完整且驗證過的 engine pin。

明確更名時，先停止會修改專案設定、角色與安裝的其他工具：

1. 用 `layout-inspect` 核對舊目錄、lock 與完整清單。
2. 用 `layout-plan` 取得完整前後雜湊及修改清單，保留回傳的 plan 與 plan_sha256。
3. 檢視後將原 plan 原封不動傳入 `layout-apply`；有外部修改時重新評估，不覆寫。
4. 用 `registry-inspect`、`route-resolve` 及安裝檢查讀回實際結果。

遷移以目錄 rename 保留未知檔案、二進位內容與空目錄，只修改已登錄原稿與其
完全相符的 project runtime 投影中的舊路徑，並同步 registry member hashes。
模型選擇、extensions、來源引用、baseline、路由與採納紀錄保留。未登錄的
native entry 不改寫；若它自行引用舊路徑，由該資源的 owner 另行處理。

安裝輸入不能只搬檔案：遷移透過正式 lock reader/serializer 將已驗證的
`project_inputs` 路徑與相關雜湊改成新位置，記錄實際執行 engine，最後發布 lock。
既有 candidate、selection、inventory 與 managed members 保持一致，沒有升級
已安裝 skill 或接管 framework runtime entry。其他原已漂移的 project input
不會被順便重新接受。若 desired binding 的 authority 位於舊目錄，遷移會拒絕；
這需要另行規劃安裝選擇的變更，不能以目錄搬移偷偷改寫已接受的 authority。

遷移是可續作的多檔操作，並非跨檔原子交易。復原資料只放在
`.ai/local/project-layout-plan.json` 與 `project-layout-complete.json`，不作資源所有權
或採納紀錄；保留原 plan，檢查 `interrupted` 回傳後才能明確續作。已完成重播只
接受仍相符的 after-state，不能重新取得使用者後續修改的所有權。參與的新工具
共用安裝 writer lock；舊版 `.writer` guard 也會阻擋搬移。外部編輯器的並行修改
仍須由 caller 停止。舊版程式本身不會因搬移取得新路徑支援，後續操作須使用新 engine。

1. 保留原 policy 與 custom entries；未登記仍受安裝器原有保護。
2. 明確提供舊 baseline、local policy 與新 candidate；無 base 不推論差異來源。
3. compare 只分類 local-only、candidate-only、same-change、conflict；語意涵蓋、
   採納與啟用都是 unknown，不因文字相同或可合併而宣稱已採納。
4. Owner 接受後以選定 proposed 做 plan/apply；native settings proposal 另行檢視
   並合併，保留 hooks、permissions、plugins、MCP 與其他 env。
5. 檢查實際 runtime discovery 與呼叫身分；既有 session 可能須重新載入設定。

## 資源登記與標籤

Sub-agents 與 [skills](skill-management.md) 使用獨立 registry，沿用相同的
來源、比較與明確路由概念；前者投影單一 native entry，後者明列多檔 mapping。
正式 reader/writer 是 pinned engine 的 `distribution.subagent_registry`，不是單純放置
一份沒人使用的標籤文件。未登記 custom 仍受原安裝器保護，不需先補登記才能保留。

Registry 的 `roles` 以專案 ID 索引，每筆包括：

- `origin`：`project-authored`、`project-derived` 或 `unknown`；搭配 `source_ref`。
- `intent`、`acceptance` 與 `capabilities`：客製意圖、既有驗收引用、明確能力標籤。
- `members`：相對 package root 的每個原稿／參考資源及 SHA-256。
- `baseline`：來源 `ref` 與 `files` 的 UTF-8 原始快照；可為 null。缺 base 明示未知。
- `projections`：每個 adapter 的原稿 `source` 與 `runtime_id`。檔案內 `name` 必須相符。
- `integration`：`candidate_ref`、`coverage`、`status`、`evidence_ref`、`decision_ref`。

`routes` 以 `purpose → adapter` 指向 `{kind, id, decision_ref, expected_sha256}`。
Project route 的 ID 是 registry role ID，`expected_sha256` 為 null；framework route
使用 canonical role ID 與已選定 runtime bytes 的 hash。Framework route 必須讀回
真正 lock ownership、runtime entry 與整個角色資源閉包，尚未安裝或漂移就停止。

| 顯示情境 | 來源與判讀 |
| --- | --- |
| 使用者自建 | project-authored 原稿；來源引用是專案聲明，工具不重建作者身分 |
| 使用者修改 | baseline 與實際 local tree 不同；缺 base 時回報 unknown，不猜測 |
| Framework 已整合客製需求 | coverage=covered、status=adopted，且附候選、驗證及 owner 決策引用；顯示帶 evidence reference 的標籤 |
| 已寫入／已安裝 | 實際 bytes 與 project registry／framework lock 相符 |
| Runtime 已發現／已啟用 | 需要另外觀察；以上欄位均不證明這件事 |

工具不驗證引用中的語意結論或人類同意，因此回傳 `evidence_verified: false`。
「已整合」可與「本地仍保留客製路由」同時成立。不要把自行填寫 coverage 當作
驗收；caller 必須用客製意圖與 AC 核對候選，並沿用真實 owner 決策。

## 原稿與 runtime entry 的更新

`files` 是以完整專案相對路徑為 key、UTF-8 原稿文字為 value 的物件，只接受
所選 `.ai/project/sub-agents/<id>/` 內已宣告 members。未提供的 member 從目前
原稿讀取並驗 hash。投影直接複製選定原稿，不自行放寬 tools／sandbox／model。

初次接管既有 runtime entry，即使 bytes 一樣，也要在 `adopt` 明確列出
`{".codex/agents/<id>.toml": "<current-sha256>"}`。已登記檔案被外部修改時，
重新接受它也需相同的明確 preimage。這只取得 project manager 的更新範圍；
任何真正 lock-owned path 都拒絕，不因標籤變成可覆寫。

換 runtime 名稱時，同時修改原稿中的 name 和 binding.runtime_id，並在 `detach`
列出原登記 entry 路徑。工具只移除 bytes 仍完全相符且已退出新投影集合的舊 entry。
未登記檔案不刪除；取消登記／切換路由也保留所有 custom authoring 與 baseline。
若保留 entry、只改 route，native 工具仍可能列出兩者，caller 必須使用明確路由。

Plan 綁定 registry、framework lock、每個檔案的前後 hash。Apply 先完整檢查，
再寫原稿與新 entry、執行明確 detach，最後寫 registry。這是多檔可續作操作，
不宣稱跨檔 atomic transaction。中斷會回報 `interrupted`、`changed: true` 與
已寫路徑；保留 exact plan 後明確重試。每筆只能處於原 preimage 或已接受 after
bytes，其他修改會阻擋。程序強制終止可能留下 `.json.writer`；先確認 writer
已停止，再由 owner 處理 guard。外部 writer 不遵守 guard 的競爭仍須避免。
Registry 已發布完成後，重播只接受所有 after bytes 仍相符；已解除登記的舊 entry
若重新出現，即使與原 bytes 一樣也阻擋，不重新取得所有權或再次刪除。

## 新版 framework 出現重疊角色時

向 `role-compare` 提供每個候選的 `{id, ref, capabilities, files, runtime_paths}`。
`files` 使用與 baseline/local 相同的 package-relative 名稱。相同 ID、能力標籤或
runtime path 只表示要比較的候選；工具不從文字近似推導語意等效。未知 entry 的
名稱碰撞也會回報，即使沒有對應的已登記能力。

1. **保留客製**：維持目前 route，暫不選取會撞名的 framework role。
2. **共存分流**：選定唯一名稱，例如 `team-reviewer`，更新原稿 name／binding，
   以 registry-plan/apply 明確 detach 原 project entry；再交原 installer 安裝
   framework role。以 purpose route 決定每個任務用哪一個。
3. **採用 framework**：保留客製原稿與證據，明確 detach 舊 project entry，設定
   framework route 的精確預期 hash，再執行原安裝流程。安裝尚未完成時 resolver
   回報 pending，不能以 metadata 宣稱已切換成功。

Managed 檔案若已直接改動，inspect 會顯示 managed-drift。可先在 project package
保存客製內容／意圖，但本管理器不改 managed path。必須由原安裝／恢復 owner
取得可驗證的舊 baseline，依支援程序恢復或處置；不能改 lock hash 消除漂移。

本來源 repo 已選用 registry：7 個 project roles、20 份原稿／參考資源、8 個
runtime entries；原有 runtime 名稱保留，避免把本次資源治理當作 native discovery
遷移。未來自我安裝選中同名 framework roles 時，仍須先選上述共存／採用操作。
這保留原本 unowned-collision 保護，並提供可執行的解決路徑。未發布的 0.21.0
不作候選身份；比較及安裝須使用屆時實際取得的固定 artifact。
