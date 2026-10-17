# spec-author 使用說明

[回 Skill 目錄](README.md) · [安裝](../installation.md) · [知識選配](../knowledge-packages.md)

本次來源版本草案：`0.2.0`。實際操作與版本以已安裝 metadata 為準。

## 用途與操作

以 `draft` 或 `normalize` 撰寫 production/use-case、entity/value-object、
adapter/interface 系統規格，依據需求與已接受的 designer 產出表達系統契約。
已有完整設計時直接引用，不要求重新執行 designer。

## 輸入與輸出

提供有界 subject、來源需求與版本、已接受設計及其決策狀態、適用目標規則、
選定 schema／版本、格式與目的地。輸出保留來源 identities、決策、invariants、
可觀察驗收結果、開放問題與實際交付位置的系統規格。

缺少設計決策時，可以依明確請求提供 provisional draft，保留未知及其影響；
不得自行決定 aggregate ownership、技術機制或失敗政策並冒稱已接受。
`normalize` 保留語意、IDs、例外、來源、核准狀態與未決問題，語意變更需另行指出。

## 責任界線

正式 test specification 及所有測試、情境、assertion 設計由 `test-designer` 負責。
系統規格仍須保留可觀察 acceptance，並在有需要時引用已存在的測試設計與 IDs；
責任轉移不代表刪除系統可驗證性。

若使用者明確指定本 skill，卻要求測試設計等不同產物，先釐清這個有界衝突，
不可私自換 route。沒有強制 requirement → designer → spec → test pipeline。
模板是普通文字指引，不是 schema；目標專案選定的格式與存放位置優先。
本 skill 不代替領域或架構決策、不實作、不跑測試，也不宣告驗收或合規通過。

## 範例請求

使用 `spec-author draft`，依需求 R1 與已接受的取消設計 D1 撰寫取消訂單的
production specification，保留其 ownership、invariants、輸入、輸出與可觀察
失敗結果；引用已有測試設計 T1，未決退款政策保持未決，不重新設計 D1。

## 知識與開始使用

本 skill metadata 維持版本 3，沒有直接方法知識消費綁定。
先確認已安裝 runtime entry，提供操作、範圍、來源及可寫目的地。
範例是自然語言請求，不是 shell 指令；prefixed 名稱可能是 `aicf-spec-author`，
canonical package ID 仍為 `spec-author`。本套件提供指令方法，沒有同名 CLI。
需要工具時沿用目標專案已授權的能力。

## 權威參考

- [Skill 入口](../../src/skills/spec-author/SKILL.md)
- [版本、操作及依賴 metadata](../../src/skills/spec-author/skill-package.yaml)
- [Authoring method](../../src/skills/spec-author/references/authoring.md)
- [Production template](../../src/skills/spec-author/references/production-template.md)
- [Entity template](../../src/skills/spec-author/references/entity-template.md)
- [Adapter template](../../src/skills/spec-author/references/adapter-template.md)
- [Presentation guide](../../src/skills/spec-author/references/spec-guide.md)
- [Organization guide](../../src/skills/spec-author/references/spec-organization-guide.md)

連結供來源庫核對；實際操作讀取已安裝資源。正式測試模板的搬移由其工作負責者處理。
