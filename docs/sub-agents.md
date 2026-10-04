# Sub-agents 發布與安裝

`src/sub-agents/` 是六個可重用角色的 editable source。每個角色都有
`sub-agent-package.yaml`，明確列出 canonical `sub-agent.yaml`、playbook 與
runtime profile。發布沿用 `src/distribution/manifest.yaml` 的 catalog
與既有 Engine 2；沒有另外一套複製或安裝工具。

這份設定需要包含 sub-agents 的新 catalog 及其配對 engine。已發布的 RC4
沒有這些角色，不能用新設定要求舊 catalog 安裝。舊 engine 遇到新的
`sub-agent` component kind 或 selection version 3 會拒絕處理。

## 選取方式

只安裝這六個角色時，Codex 使用 `sub-agents@0.1.0` preset；Claude 使用
`sub-agents-claude@0.1.0`。現有 presets 的
skills、knowledge 與 adapters 選取保持原樣。角色也可與 skills 一起逐項
選取；使用 `selection_version: 3`，並明確提供 `sub_agents`：

```json
{
  "selection_version": 3,
  "catalog": {
    "identity": "<verified catalog identity>",
    "catalog_sha256": "<verified catalog.json SHA-256>",
    "files_sha256": "<verified catalog-files.json SHA-256>"
  },
  "skills": [],
  "knowledge": [],
  "sub_agents": ["context-translator", "mechanical-evidence-worker"],
  "adapters": ["codex"],
  "bindings": [],
  "skill_naming": "original"
}
```

上例的 catalog 欄位是佔位值；請換成實際驗證的 catalog pin。
`sub_agents` 必須排序且不可重複。空陣列代表不安裝角色，不能以未列出的
角色或未知 adapter 自動替代。Version 1、2 的既有 selection 仍可使用，
不會隱含安裝 sub-agents。

使用與該 catalog 配對、已驗證的 engine 和 pin：

```powershell
python -I -B <engine-root>/src/tools/derive-subset.py `
  --catalog-root <catalog-root> --catalog-identity <catalog-identity> `
  --preset sub-agents --preset-version 0.1.0 `
  --engine-pin <engine-pin.json> `
  --output-root <new-subset-root> --scratch-root <scratch-root>
```

逐項選取時以 `--selection <selection.json>` 取代 preset 參數。後續沿用
[安裝指南](installation.md) 的 inspect、plan、apply、驗證及 recovery
流程；selection 的保存仍是明確的 project edit。

Claude 安裝將上方指令的 preset 改為
`--preset sub-agents-claude --preset-version 0.1.0`。手動 selection 使用
`"adapters": ["claude"]`；同時安裝兩種 profiles 則使用已排序的
`"adapters": ["claude", "codex"]`。兩種模式都明確選取同一組角色。

## 安裝位置

| 內容 | 目的地 |
| --- | --- |
| Canonical role、package metadata、playbook 與 profile source | `.ai/core/sub-agents/<role-id>/` |
| 六個 Codex profiles | `.codex/agents/<role-id>.toml` |
| 六個 Claude profiles | `.claude/agents/<role-id>.md` |

Codex custom agents 使用 `.codex/agents/*.toml`，名稱、說明及
`developer_instructions` 為必要欄位，見
[OpenAI 官方 sub-agents 文件](https://learn.chatgpt.com/docs/agent-configuration/subagents)。
Canonical role 的 `model_policy` version 2 選擇 runtime 繼承模式。
Codex profile 不寫 `model`、`model_reasoning_effort` 或 `model_provider`；
沒有其他委派／runtime 預設覆寫時，沿用主對話的模型與推理深度。
實際 precedence 仍由 runtime 決定，不能把省略欄位當成計費上限。
安裝器不改 `.codex/config.toml`、個人設定、concurrency 或 credentials。

六個角色為 `context-translator`、`evidence-report-synthesizer`、
`fixed-head-independent-auditor`、`mechanical-evidence-worker`、
`reconciliation-worker`、`semantic-governance-analyst`。五個分析角色的
Codex profile 為 read-only；translator 依角色規約只寫指定譯文。
Claude profiles 依 [Anthropic 官方文件](https://code.claude.com/docs/en/sub-agents)
使用 YAML frontmatter 與明確 tools allowlist。五個分析角色只允許
`Read, Grep, Glob`，不提供 shell、MCP、寫入或再委派工具；需要執行命令或
preflight 時，必須由 parent 選取具授權的執行方式，缺少工具就停止。
所有 Claude profiles 使用 `model: inherit`，不固定模型世代或 effort。
Translator 使用 `Read, Write, Edit`，寫入仍限於 caller 指定的譯文。
Claude 的 invocation override／provider policy 仍可能影響實際模型；
parent 必須確認使用者選定的執行與成本邊界。
安裝器不改 `.claude/settings.json`、全域 model、MCP 或 permission 設定。
首次建立 `.claude/agents/` 後，依官方文件重新啟動 Claude Code 才能載入。
Copilot 仍是本專案的手動 translator 設定，沒有新增
Copilot 安裝 adapter。

安裝後的檔案由 lock/inventory 管理。已有的同名、未受此 lock 管理的
profile，即使內容相同，也會造成 collision；安裝器不會自動接管或
覆寫。Managed bytes 被修改時沿用 drift 拒絕規則。角色撤回只移除
lock 所擁有的檔案，其他 project profiles 保留。

角色只提供執行邊界，不代替 target-owned policy、授權、驗證工具或
parent 的 integration 決策。Fixed-head auditor 的 preflight/tooling
前提仍須由 caller 證明；套件不提供 source repository 的 `.dev/`
治理檔案。檔案發布、安裝驗證、runtime discovery 與角色實際執行是
不同證據。

## 模型選型與成本邊界

六個角色都不包含固定模型候選名單。官方新增模型、使用者更換主對話模型，
不需要為此修改或重新發布 framework，也不需手改受 lock 管理的 profile。
角色只定義任務、輸入、輸出、工具與權限，不能因 audit、governance 等名稱
推導「必須用更昂貴模型」。

預設沿用使用者的 runtime 選擇。需要提高模型成本、推理深度或改 provider
時，parent 應先說明原因，取得明確授權後使用可見的獨立工作對話；不得
在 sub-agent 裡默默升級。可用性、角色設定與計費同意是不同事項。
這是選型規則，並非 runtime 強制計費控制；需確認實際 invocation 的模型。

使用者可在工具自己的模型選單／專案或個人 runtime 設定中維護模型。
framework 不寫入 `.codex/config.toml`、`.claude/settings.json` 或 credentials。
對特定角色另外固定模型的能力，仍須由 target 自行選定設定方式；不應直接
修改 managed profile 來繞過安裝漂移檢查。

## 可選模型查詢

`src/tools/derive-subset.py` 保留明確選取的模型查詢參數：

- `--discover-codex-models`：透過 Codex CLI `app-server` 的 `model/list`
  取得 catalog，不建立對話或執行模型推論。
- `--discover-claude-api-models`：使用 caller 明確提供的
  `ANTHROPIC_API_KEY` 查詢直接 Anthropic Models API；不代表 Claude 訂閱權限，
  不自動跨 gateway、Bedrock、Vertex 或 Foundry。
- `--model-availability <absolute-observations.json>`：使用 caller 提供的
  normalized observations；與 live discovery 二擇一。

對本版的繼承型角色，查詢結果只回傳為 `model_observations`，不寫入
`desired.model_resolution`，不改 profile，不凍結主對話模型；空的可用模型
清單也不阻擋純安裝。來源／adapter／資料格式仍會驗證。查詢失敗不會偽裝成功，
但未要求查詢的正常安裝不依賴 CLI、API 或模型帳號。

舊 policy 1 的固定設定仍有相容讀取與驗證；它不代表本版六個角色仍採用
固定候選。模型觀察不是帳號存取證明，也不授權執行或成本升級。

目前沒有獨立的 sub-agent 模型維護 skill。一般 runtime 設定調整可以由
`ai-context-governance` 依明確授權維護專案自有設定；安裝、解除安裝、版本更新
仍沿用既有 selection → plan → apply。跨 runtime 的逐角色覆寫、差異預覽及
更新保留若成為需要，再擴充既有維護工具，無須另建一套安裝系統。
