# Sub-agents 發布與安裝

`src/sub-agents/` 是六個可重用角色的 editable source。每個角色都有
`sub-agent-package.yaml`，明確列出 canonical `sub-agent.yaml`、playbook 與
runtime profile。發布沿用 `src/distribution/manifest.yaml` 的 catalog
與既有 Engine 2；沒有另外一套複製或安裝工具。

目前六個角色涵蓋證據整理、調和、語意治理分析、報告彙整、固定版本獨立審核
與上下文翻譯。它們提供有界的委派責任；需求、領域建模、軟體架構與實作方法
仍由選定 skills 提供。角色存在不代表已啟動 agent，也不代表自動取得另一模型、
額外工具權限或執行授權；使用哪個角色與 skill 應由當次工作範圍決定。

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

使用與該 catalog 配對、已驗證的 engine 和 pin。下列變數沿用
[安裝說明](installation.md) 第 3、5 節的實際絕對路徑、identity 與空輸出根：

```powershell
python -I -B "$EngineRoot/src/tools/derive-subset.py" `
  --catalog-root $CatalogRoot --catalog-identity $CatalogIdentity `
  --preset sub-agents --preset-version 0.1.0 `
  --engine-pin "$PackageRoot/engine-pin.json" `
  --output-root $OutputRoot --scratch-root $ScratchRoot
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
Canonical role 的 `model_policy` version 3 要求依任務選型，從專案自有的
`.ai/custom/sub-agent-policy.json` 讀取偏好，不直接繼承主對話。Codex profile
不固定模型，以免覆蓋每次委派參數；由 parent 明確傳入模型與 effort，另設
Luna 專案預設防止漏填。設定與實際呼叫仍須分別確認。
安裝器不改 `.codex/config.toml`、個人設定、concurrency 或 credentials。

六個角色為 `context-translator`、`evidence-report-synthesizer`、
`fixed-head-independent-auditor`、`mechanical-evidence-worker`、
`reconciliation-worker`、`semantic-governance-analyst`。五個分析角色的
Codex profile 為 read-only；translator 依角色規約只寫指定譯文。
Claude profiles 依 [Anthropic 官方文件](https://code.claude.com/docs/en/sub-agents)
使用 YAML frontmatter 與明確 tools allowlist。五個分析角色只允許
`Read, Grep, Glob`，不提供 shell、MCP、寫入或再委派工具；需要執行命令或
preflight 時，必須由 parent 選取具授權的執行方式，缺少工具就停止。
Claude profiles 使用 `model: haiku` 作低成本保護，parent 依專案政策在呼叫時
選 Haiku／Sonnet；Opus 需另行授權。版本與覆寫順序見[管理指南](sub-agent-management.md)。
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
parent 的 integration 決策。Fixed-head auditor 由 parent 明確提供固定 commit、
比較基準、範圍、判準、實際權限與停止條件；不依賴來源庫的 classifier、
packet tier、lease 或 preflight 腳本。若 target 另有必要檢查，仍須確認
工具可用且執行方式已授權；無法執行時回報 blocked。套件不提供 source repository 的 `.dev/`
治理檔案。六個角色套件升至 `0.2.0`，不改角色的檔案與工具責任邊界。
檔案發布、安裝驗證、runtime discovery 與角色實際執行是
不同證據。

## 模型選型與成本邊界

使用[獨立管理指南](sub-agent-management.md)設定 project-owned policy。模型偏好、
角色內容與 runtime entries 各有 owner；framework 升級不重建這份 policy。
Codex 預設 Luna，實質推理用 Sol，Astra 另行授權；Claude 對應 Haiku、Sonnet、Opus。
任務分類、effort、可用性與實際呼叫身分須確認，不以 role 名稱、主對話模型或
「沒有升級」推導已節省成本。確定性工作優先直接使用工具。

`src/tools/manage-sub-agents.py` 隨 pinned engine 分發，提供 defaults、inspect、
plan、apply、resolve、compare。角色套件本身不代表已安裝外部 engine 工具。
只有 apply 可改 project policy；native settings 是明確選取的 project edit。
不要手改 managed profile；unknown/custom entries 即使未登記也受原安裝保護。

## 可選模型查詢

`src/tools/derive-subset.py` 保留 `--discover-codex-models`、
`--discover-claude-api-models` 與 `--model-availability`。查詢不啟動模型推論；
Claude API credentials 與訂閱授權仍為不同邊界，不因本管理政策取得存取權。
v2/v3 查詢只回傳 observations，不寫入 install-time model_resolution，亦不
自動替代 task policy。正常安裝不依賴模型帳號；委派前須另核對可用性。
舊 policy v1/v2 保持可讀，新角色採 v3。模型查詢不是成本同意或實際呼叫證據。
