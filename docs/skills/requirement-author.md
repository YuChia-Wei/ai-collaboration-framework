# requirement-author 使用說明

[回 Skill 目錄](README.md) · [安裝](../installation.md) · [知識選配](../knowledge-packages.md)

套件版本：`0.1.0`。操作名稱以實際安裝的 metadata 為準。

## 用途與操作

`draft` 或 `normalize` 一份需求文件，維持利害關係人意圖、商業規則、來源與可觀察驗收。

## 輸入與輸出

提供需求範圍/來源、目標規則及可選模板/目的地；輸出需求草稿或保留語意/身分/核准狀態的 normalised document，並列假設、未解決事項與實際交付位置。

## 何時用／界線

不自動加規格、情境設計或 problem-frame 階段；文件作者不能宣稱 stakeholder 已核准、已實作或已跑驗收。

## 範例請求

使用 `requirement-author draft`，依訪談紀錄與既有商業規則撰寫退款需求，為每條驗收條件附來源與可觀察結果，未知決策獨立列出。

## 知識

無套件綁定。

## 開始使用

先確認此 skill 已在專案的 runtime entries 中。向 agent 提供上面的操作、
實際範圍與輸入；範例 prompt 是自然語言請求，不是 shell 指令。
明確指定輸出位置及可寫範圍。使用 prefixed 安裝時，選單中的名稱可能是
`aicf-requirement-author`；canonical package ID 仍為 `requirement-author`。

此套件提供指令方法，不提供同名 CLI。Agent 依已安裝的 operation
reference 執行；若本次任務需要編輯或測試，使用專案已有且被授權的工具。

## 權威參考

- [Skill 入口](../../src/skills/requirement-author/SKILL.md)
- [版本、操作、依賴與 runtime metadata](../../src/skills/requirement-author/skill-package.yaml)
- [references/authoring.md](../../src/skills/requirement-author/references/authoring.md)
- [references/requirement-template.md](../../src/skills/requirement-author/references/requirement-template.md)
- [references/requirement-guide.md](../../src/skills/requirement-author/references/requirement-guide.md)

上述連結方便在來源庫核對；實際使用時應讀取已安裝套件中的相同資源。
