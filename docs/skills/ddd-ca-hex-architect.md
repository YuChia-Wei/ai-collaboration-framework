# ddd-ca-hex-architect 使用說明

[回 Skill 目錄](README.md) · [安裝](../installation.md) · [知識選配](../knowledge-packages.md)

套件版本：`0.3.1`。操作名稱以實際安裝的 metadata 為準。

## 用途與操作

`design` 提出 DDD/Clean/Hexagonal 架構方案；`review` 只讀比較固定架構 artifact 與需求/決策。

## 輸入與輸出

提供有界目標、需求、驗收、品質/相容限制、已採納決策與選定技術；輸出領域語言、不變量、邊界、替代方案、風險和 handoff。

## 何時用／界線

不實作、不採納決策；其他 skill 非完成設計或審查的必要條件，目標未選的慣例不能自動生效。

## 範例請求

使用 `ddd-ca-hex-architect design`，為庫存保留流程提出 bounded-context、port/adapter 與交易邊界的兩個方案，說明不變量和取捨；不要修改產品。

## 知識

可選 `engineering-common@0.3.0`（依當前 allowlist 按主題選讀）及 `dotnet-backend@0.1.4`（7 項）架構 binding；未裝時不具那些 .NET 專門架構規則覆蓋。

## 開始使用

先確認此 skill 已在專案的 runtime entries 中。向 agent 提供上面的操作、
實際範圍與輸入；範例 prompt 是自然語言請求，不是 shell 指令。
明確指定輸出位置及可寫範圍。使用 prefixed 安裝時，選單中的名稱可能是
`aicf-ddd-ca-hex-architect`；canonical package ID 仍為 `ddd-ca-hex-architect`。

此套件提供指令方法，不提供同名 CLI。Agent 依已安裝的 operation
reference 執行；若本次任務需要編輯或測試，使用專案已有且被授權的工具。

## 宣告的知識資源

以下宣告皆為 optional allowlist；不是每次必讀清單。未選、缺少或無法驗證時，揭露 coverage unavailable。

### common-architecture

`engineering-common@0.3.0`；操作：`design`、`review`。

- `engineering-rule-catalog`
- `member:ddd/README.md`
- `member:ddd/domain-discovery.md`
- `member:ddd/strategic-design.md`
- `member:ddd/tactical-design.md`
- `member:ddd/model-evolution.md`
- `member:ddd/examples/order-cancellation.md`
- `member:domain-language/README.MD`
- `member:domain-language/templates/aggregate-vocabulary-template.md`
- `member:domain-language/templates/bounded-context-language-template.md`
- `member:domain-language/templates/domain-event-language-template.md`
- `member:operations/CONTEXT-MAP-GUIDE.MD`

### dotnet-architecture

`dotnet-backend@0.1.4`；操作：`design`、`review`。

- `engineering-rule-catalog`
- `member:standards/BUILDING-BLOCKS-RECONSTRUCTION-CONTRACT.md`
- `member:standards/DESIGN-BY-CONTRACT.md`
- `member:standards/coding-standards/aggregate-standards.md`
- `member:standards/coding-standards/transactional-messaging-standards.md`
- `member:standards/coding-standards/usecase-standards.md`
- `member:standards/project-structure.md`

## 權威參考

- [Skill 入口](../../src/skills/ddd-ca-hex-architect/SKILL.md)
- [版本、操作、依賴與 runtime metadata](../../src/skills/ddd-ca-hex-architect/skill-package.yaml)
- [references/design.md](../../src/skills/ddd-ca-hex-architect/references/design.md)
- [references/review.md](../../src/skills/ddd-ca-hex-architect/references/review.md)

上述連結方便在來源庫核對；實際使用時應讀取已安裝套件中的相同資源。

## DDD 主題選讀

| 當前問題 | 選讀資源 |
| --- | --- |
| 語言或業務意義不清 | ddd/domain-discovery.md |
| 比較 contexts 與合作邊界 | ddd/strategic-design.md |
| 不變量及模型責任 | ddd/tactical-design.md |
| 修訂既有模型 | ddd/model-evolution.md |

README 只在需要選路時讀取；domain-language 模板與 Context Map 僅在相關成果需要時選讀。不預載全包，不強制 MQ 或分散式部署；缺少知識仍可依 caller 來源進行通用架構工作並揭露 coverage 限制。
