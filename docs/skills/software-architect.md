# software-architect 使用說明

[回 Skill 目錄](README.md) · [安裝](../installation.md) · [知識選配](../knowledge-packages.md) ·
[舊 architect 遷移](domain-architecture-migration.md)

來源套件版本：`0.1.2`。實際可用性依已安裝 metadata 與 runtime entry。
本套件提供指令方法，沒有同名 CLI、配置或 managed store。

## 用途、輸入與輸出

| 操作 | 提供的輸入 | 取得的成果 |
| --- | --- | --- |
| design | 有界技術目標、行為／契約與接受狀態、已知模型／依賴、品質／相容性及技術事實 | 元件、依賴、ports/adapters、交易與失敗機制、替代方案、品質論據、演進影響與驗證需要 |
| review | 固定架構 artifact、來源需求／模型、已接受決策、指定覆蓋 | 有位置／準則／觸發／影響／證據的唯讀 findings、有效選項、未定事項與限制 |

已有需求或模型足夠時可直接使用，不要求先執行領域 skill。CA／Hexagonal 是按
需要使用的方法，不預選 CQRS、event sourcing、broker、ORM、DI 或實體專案拆分。
預設對話輸出；保存須有目的地與寫入範圍。Design 是提案，不代替 owner 採納。

## 責任與範圍

[Domain model designer](domain-model-designer.md) 擁有語言、不變條件與業務一致性責任；
software architect 擁有實現機制。若只有最終一致性卻要求原子成立，必須明列衝突、
時間窗及可行選項，回到相關 owner，不自行弱化模型。

處理相關的 retry、duplicates、ordering、commit/publish、恢復與 observability，
不假設 exactly-once，也不把未量測的效能數字寫成保證。相容、rollout、migration 與
rollback 僅在需要時設計，設計不授權執行。

可使用與軟體正確性相關的部署／網路失敗假設；網路拓樸、DNS／防火牆、跨機房基建、
IaC、平台營運與部署流水線建置不在本 skill 範圍。未來 system architect／DevOps
能力尚未由此套件提供。測試設計與程式實作各有 owner。

## 範例請求

```text
使用 software-architect design。訂單模型與取消規則已接受；這次只替換第三方付款 API。
請提出 port/adapter 與錯誤映射，說明 retry/idempotency、依賴方向及相容性取捨。
不要重跑完整 DDD 流程；若發現機制與既有規則衝突，列出影響和待決策選項。
```

Review 請另外提供固定檔案／版本與需求來源；reviewer 維持唯讀並表明作者關係，
沒有 findings 不代表 runtime 或全系統 compliance 通過。

## 知識選配

- `engineering-common@0.4.1`：rule catalog、technology selection、authoring boundaries、artifact review。
- `dotnet-backend@0.1.7`：rule catalog、building-block reconstruction、DbC、transactional messaging、usecase、project structure 與政策理由 guidance；required common dependency 一起選。

Capability 為 `architecture`，operations 為 design/review；只載入匹配 allowlist 與
目標 bindings 的資源。模型是 caller input，不為架構問題預載全部 DDD。
未安裝選配可做通用分析並揭露缺口，不能從 source 補讀、假稱 .NET coverage 或
將 knowledge selection 當作 target rule adoption。

## 權威參考

- [來源入口](../../src/skills/software-architect/SKILL.md)
- [完整 operations／knowledge allowlist](../../src/skills/software-architect/skill-package.yaml)
- [Design](../../src/skills/software-architect/references/design.md)、[Review](../../src/skills/software-architect/references/review.md)
- [Installed resource protocol](../../src/skills/software-architect/references/knowledge.md)

以上供來源核對，實際使用讀取安裝副本。Prefixed entry 可能為
`aicf-software-architect`，canonical ID 不變。
