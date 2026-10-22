# Sub-agent 模型政策與獨立管理

角色描述工作邊界；模型政策決定每次任務的模型與推理深度。兩者分開維護，
讓模型改版、成本偏好與下游客製不必跟著 framework 發布，也不必修改 managed core。

## 所有權與交付

| 內容 | Owner／更新方式 |
| --- | --- |
| `.ai/core/sub-agents` 與由 lock 管理的 runtime entries | framework 套件，使用原安裝 plan/apply |
| `.ai/custom/sub-agent-policy.json` | 專案自有，管理工具只在明確 apply 時更新 |
| `.codex/config.toml`、`.claude/settings.json` | 專案／runtime 自有，明確檢視與合併必要設定 |
| 未登記、自建或既有本地 agent entries | 保留原 owner，不自動接管、覆蓋或刪除 |

管理工具是 pinned engine 的 `src/tools/manage-sub-agents.py`，不是新 installer
或必裝 skill。只安裝角色不代表外部 engine 已存在。使用與該 engine 完全一致的
pin；更新 framework 不更新 policy、不把它加入 lock，也不擅自採納新版預設。
舊 engine closure 僅可作歷史 catalog/lock 的讀取資料；實際執行仍須驗證現行完整 pin。

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

1. 保留原 policy 與 custom entries；未登記仍受安裝器原有保護。
2. 明確提供舊 baseline、local policy 與新 candidate；無 base 不推論差異來源。
3. compare 只分類 local-only、candidate-only、same-change、conflict；語意涵蓋、
   採納與啟用都是 unknown，不因文字相同或可合併而宣稱已採納。
4. Owner 接受後以選定 proposed 做 plan/apply；native settings proposal 另行檢視
   並合併，保留 hooks、permissions、plugins、MCP 與其他 env。
5. 檢查實際 runtime discovery 與呼叫身分；既有 session 可能須重新載入設定。

這是 #482/#484 原則的模型政策切片，不實作完整 skill 客製來源平台。Managed
角色的語意客製仍使用 project-owned entry 與明確資源引用，不能改 core 來繞過
drift，也不能自動刪除被 upstream 涵蓋的 local 內容。
