# problem-frame-author 使用說明

[回 Skill 目錄](README.md) · [安裝](../installation.md) · [知識選配](../knowledge-packages.md)

套件版本：`0.1.0`。操作名稱以實際安裝的 metadata 為準。

## 用途與操作

`draft`/`review-draft` 產生或審查 bounded commanded-behavior problem frame；選定 `problem-frame.cbf@1.0.0` 時另有 `explain`、`create`、`inspect`、`validate`、`render` 工具操作。

## 輸入與輸出

draft 提供 use case、意圖、來源權威、觀察、模板/格式；輸出 family rationale、extraction sheet、draft、來源、問題及遺漏。CBF tool 用明確 roots/JSON、reference/record，回傳嚴格 structural result 與 digest。

## 何時用／界線

正常需求不會因含 command 便自動成 CBF；結構有效、語意審查、意圖核准與 runtime compliance 必須分開。沒有選定 CBF 時不需要 Python tool。

## 範例請求

使用 `problem-frame-author draft`，為『核准付款』寫 problem frame，保留未知 PRE/POST，附上來源定位；不要把草稿稱為已核准或 runtime 合規。

## 知識

無套件綁定。

## 開始使用

先確認此 skill 已在專案的 runtime entries 中。向 agent 提供上面的操作、
實際範圍與輸入；範例 prompt 是自然語言請求，不是 shell 指令。
明確指定輸出位置及可寫範圍。使用 prefixed 安裝時，選單中的名稱可能是
`aicf-problem-frame-author`；canonical package ID 仍為 `problem-frame-author`。

此套件含可執行工具。先依[工具型 skills 共通設定](../tool-skills.md)
確認 Python 依賴、絕對 roots、設定及寫入限制，再執行 `explain`。
建立／變更 record 要按 operation reference 提供欄位；更新必須使用
實際讀回的 digest，不能自行填一個 hash。

## 權威參考

- [Skill 入口](../../src/skills/problem-frame-author/SKILL.md)
- [版本、操作、依賴與 runtime metadata](../../src/skills/problem-frame-author/skill-package.yaml)
- [references/authoring.md](../../src/skills/problem-frame-author/references/authoring.md)
- [references/format.md](../../src/skills/problem-frame-author/references/format.md)
- [references/operations.md](../../src/skills/problem-frame-author/references/operations.md)
- [references/configuration.md](../../src/skills/problem-frame-author/references/configuration.md)
- [references/example.md](../../src/skills/problem-frame-author/references/example.md)
- [problem-frame.cbf schema](../../src/skills/problem-frame-author/schemas/cbf-record-v1.schema.json)

上述連結方便在來源庫核對；實際使用時應讀取已安裝套件中的相同資源。
