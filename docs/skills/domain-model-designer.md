# domain-model-designer 使用說明

[回 Skill 目錄](README.md) · [安裝](../installation.md) · [知識選配](../knowledge-packages.md) ·
[舊 architect 遷移](domain-architecture-migration.md)

來源套件版本：`0.1.1`。實際可用性以已安裝 metadata 與 runtime entry 為準。
這是指令型 skill，沒有同名 CLI、record store 或強制技術依賴。

## 用途、輸入與輸出

| 操作 | 提供的輸入 | 取得的成果 |
| --- | --- | --- |
| explore | 有界領域疑問、可讀來源、已有語言／規則／例子及接受狀態 | 來源化語言、規則、反例、歧義、模型假設與最小下一步 |
| design | 建模目標、行為與限制、既有模型、已接受決策、來源 ID | context／aggregate 等責任、不變條件、狀態與事件、例子映射、替代方案與未定決策 |
| review | 固定模型身份、來源需求、接受決策、指定覆蓋與允許證據 | 唯讀 findings、位置／準則／觸發／影響／證據、有效選項與限制 |

不用先建立完整 PRD 或 Context Map，也不必先執行 explore 才能 design。
以 DDD 理解業務概念與一致性責任，以 BDD 例子挑戰模型；不強制每個戰術模式。
預設回覆於對話，指定可寫目的地時才保存；模型提案不等於 owner 已接受。

## 責任界線

本 skill 說明哪些業務事實必須一致成立；[software-architect](software-architect.md)
決定資料、交易、整合等實現機制。機制做不到時回傳衝突，不默改業務規則。
Bounded context 不等於微服務、部署單位或資料庫。

需求／模型／規格都能使用 GWT 例子。測試層級、資料、fixtures、隔離、oracle 與
覆蓋由 test-designer 設計；本 skill 不實作程式、不核准業務政策或選部署方案。
Review 綁定固定 artifact，作者自檢與具有證據的獨立審核分開。

## 範例請求

```text
使用 domain-model-designer explore，釐清訂單取消與付款競爭的語言和規則。
已接受規則是出貨後不可取消；退款政策尚未決定。請用具體例子與反例指出
需要 owner 決策的問題，不選資料庫或 broker，先回覆於對話。
```

```text
使用 domain-model-designer design，依我提供的已接受規則比較 aggregate 責任。
保留規則 ID、接受狀態與必須原子成立的業務事實；技術實現交由後續架構判斷。
```

## 知識選配

- `engineering-common@0.4.0`：explore 使用 DDD／BDD discovery 與 collaborative discovery；
  design/review 可選 DDD 各主題、domain-language、Context Map、BDD discovery/formulation。
- `dotnet-backend@0.1.6`：只供 design/review 使用 rule catalog、DbC 與 aggregate standards；
  需要搭配其 required common dependency。Explore 不消費 .NET 規則。

兩者使用既有 `architecture` capability，以不同 operation／allowlist 控制資源。
這不是舊 skill 的 alias。每次只讀所需資源；選取不等於採納規則，缺少選配仍可依
caller sources 進行通用工作，但不能宣稱該專業覆蓋已具備。依 installed protocol
驗證 lock、hash、authority 與 selectors，不回讀 framework source 代替安裝。

## 權威參考

- [來源入口](../../src/skills/domain-model-designer/SKILL.md)
- [完整 operations／knowledge allowlist](../../src/skills/domain-model-designer/skill-package.yaml)
- [Explore](../../src/skills/domain-model-designer/references/explore.md)、[Design](../../src/skills/domain-model-designer/references/design.md)、[Review](../../src/skills/domain-model-designer/references/review.md)
- [Installed resource protocol](../../src/skills/domain-model-designer/references/knowledge.md)

以上供來源核對；實際使用讀取已安裝版本。Prefixed 模式的 entry 可能叫
`aicf-domain-model-designer`，canonical ID 不變。安裝、呼叫與驗收是不同證據。
