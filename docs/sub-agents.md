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
python -I -B <engine-root>/tools/derive-subset.py `
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
Profile 的 model 由 canonical role 的 `model_policy` 管理；effort 保留角色原設定。
這份設定不保證帳號可使用該 model。
安裝器不改 `.codex/config.toml`、個人設定、concurrency 或 credentials。

六個角色為 `context-translator`、`evidence-report-synthesizer`、
`fixed-head-independent-auditor`、`mechanical-evidence-worker`、
`reconciliation-worker`、`semantic-governance-analyst`。五個分析角色的
Codex profile 為 read-only；translator 依角色規約只寫指定譯文。
Claude profiles 依 [Anthropic 官方文件](https://code.claude.com/docs/en/sub-agents)
使用 YAML frontmatter 與明確 tools allowlist。五個分析角色只允許
`Read, Grep, Glob`，不提供 shell、MCP、寫入或再委派工具；需要執行命令或
preflight 時，必須由 parent 選取具授權的執行方式，缺少工具就停止。
三個原 Terra 分析角色使用 Opus 5.5，兩個原 Sol 深度分析角色使用 Fable 5.1。
Translator 使用固定 Haiku 4.5 ID 與 `Read, Write, Edit`，
寫入仍限於 caller 指定的譯文。
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

## 安裝時程式化選模

以下是本專案採用的角色分工，並非官方跨廠牌等效能力保證：

| 原 Codex model | Codex 候選順序 | Claude 固定候選 |
| --- | --- | --- |
| GPT-5.6 Luna | `gpt-6-luna` | `claude-haiku-4-5-20251001` |
| GPT-5.6 Terra | `gpt-6.1-sol` → `gpt-6-sol` | `claude-opus-5-5` |
| GPT-5.6 Sol | `gpt-6-astra` | `claude-fable-5-1` |

[OpenAI](https://learn.chatgpt.com/docs/models) 將 Luna 定位於明確、可重複、
高量任務；[Claude](https://code.claude.com/docs/en/model-config) 將 Haiku
定位於快速簡單任務、Sonnet 定位於日常 coding。因此 Luna 的低成本任務
分工對應 Haiku；Sonnet 5.5 可作為品質優先的另行選擇，不是自動同級替代。
這次候選名單不包含尚未確認發布的 Fable 5.5／5.6。

在前面的 `derive-subset.py` 指令加上 `--discover-codex-models`，
即可透過安裝當下的 Codex CLI `app-server` 查詢 `model/list`，包含分頁與
supported reasoning efforts，選取名單內第一個符合角色 effort 的候選。
查詢只使用 initialize／initialized／model/list，不建立 thread 或執行推論。
安裝器不降低 effort，也不自動跨 provider、跨角色層級或退回 5.6。
CLI 不存在、查詢失敗、沒有合格候選時拒絕 derivation。

Claude 的直接 Anthropic API 使用 `--discover-claude-api-models`，
明確使用 caller 已設定的 `ANTHROPIC_API_KEY` 查詢
[Models API](https://platform.claude.com/docs/en/api/models/list)。
這不是 Claude Code 訂閱帳號查詢，也不能證明訂閱／workspace 可用。
設定 gateway、Bedrock、Vertex 或 Foundry 時，此直接 API 路徑拒絕執行；
由 caller 在實際 provider／Claude Code 環境查詢後，提供明確 observation。
兩個 discovery flags 同時使用只適用於明確選取兩個 adapters 的 selection。
API key 不寫入 metadata、輸出或 lock；查詢不使用 message API。

離線、Claude 訂閱或外部 runtime 查詢可傳入
`--model-availability <absolute-observations.json>`，格式為僅包含
`observations` 的物件；其值為已排序的陣列：

```json
{"observations": [
  {
    "adapter": "codex",
    "source": "codex-app-server",
    "observed_at": "2026-10-03T00:00:00+00:00",
    "models": [
      {"id": "gpt-6-astra", "reasoning_efforts": ["max", "xhigh"]},
      {"id": "gpt-6-luna", "reasoning_efforts": ["max"]},
      {"id": "gpt-6-sol", "reasoning_efforts": ["high", "medium"]}
    ]
  }
]}
```

上例為格式示例，不是帳號實測。Models 與 efforts 都需排序且不重複。
Claude observation 的 source 使用 `anthropic-api` 或 `caller-claude-code`，
`reasoning_efforts` 可為空；本次不將 Codex effort 映射成 Claude effort。
Observation 必須與 selection adapters 完全對應，候選模型必須涵蓋所有
選取角色需求。外部 observation 是 caller 提供的資料，安裝器驗證格式與
選模一致性，不認證它的提供者或帳號存取權。

Resolver 把 observation、時間、policy version 與每個 role 的 model／effort
存入回傳的 `desired.model_resolution` 和 subset metadata，plan／lock 沿用
同一份 selection。Runtime profile 只改 model 欄位，canonical profile、
instructions、tools 和 sandbox 邊界保持原樣。驗證重新計算選模與 profile
bytes，避免套用時重新查詢導致 plan 漂移。保存 installation.json 仍需 caller
明確 project edit；不會自動保存。未傳 discovery／observation 時使用上表首選
固定設定，這種模式沒有「已偵測可用」的宣告。

目前 model/list 可能是 client catalog；API 目錄也不等於實際 runtime entitlement。
Profile 設定不能禁止 Claude runtime 自己的 policy fallback；執行後仍需確認
實際模型。新模型需由 owner 更新 canonical `model_policy` 並重建 catalog，
不依版本號排序或發布傳聞自動接納。
