# spec-author 使用說明

[回 Skill 目錄](README.md) · [安裝](../installation.md) · [知識選配](../knowledge-packages.md)

套件版本：`0.1.0`。操作名稱以實際安裝的 metadata 為準。

## 用途與操作

`draft` 或 `normalize` 已選類型的 production/use-case、entity/value-object、adapter/interface 或 formal-test specification。

## 輸入與輸出

提供規格類型、有界 subject、來源需求/觀察、已採納決策與格式/目的地；輸出保留來源的規格、選型理由、覆蓋/開放決策與交付位置。

## 何時用／界線

模板是普通 authoring guidance，不是 schema；含 GWT 的正式 test spec 仍可屬本 skill，情境矩陣本身屬 BDD route。它不實作、不跑測試、不中途核准架構。

## 範例請求

使用 `spec-author draft`，撰寫『取消訂單』production specification，包含輸入、輸出、失敗條件和來源，但保留尚未決定的退款策略。

## 知識

無套件綁定。

## 開始使用

先確認此 skill 已在專案的 runtime entries 中。向 agent 提供上面的操作、
實際範圍與輸入；範例 prompt 是自然語言請求，不是 shell 指令。
明確指定輸出位置及可寫範圍。使用 prefixed 安裝時，選單中的名稱可能是
`aicf-spec-author`；canonical package ID 仍為 `spec-author`。

此套件提供指令方法，不提供同名 CLI。Agent 依已安裝的 operation
reference 執行；若本次任務需要編輯或測試，使用專案已有且被授權的工具。

## 權威參考

- [Skill 入口](../../src/skills/spec-author/SKILL.md)
- [版本、操作、依賴與 runtime metadata](../../src/skills/spec-author/skill-package.yaml)
- [references/authoring.md](../../src/skills/spec-author/references/authoring.md)
- [references/production-template.md](../../src/skills/spec-author/references/production-template.md)
- [references/entity-template.md](../../src/skills/spec-author/references/entity-template.md)
- [references/adapter-template.md](../../src/skills/spec-author/references/adapter-template.md)
- [references/formal-test-template.md](../../src/skills/spec-author/references/formal-test-template.md)
- [references/spec-guide.md](../../src/skills/spec-author/references/spec-guide.md)
- [references/spec-organization-guide.md](../../src/skills/spec-author/references/spec-organization-guide.md)

上述連結方便在來源庫核對；實際使用時應讀取已安裝套件中的相同資源。
