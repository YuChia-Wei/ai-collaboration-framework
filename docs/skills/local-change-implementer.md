# local-change-implementer 使用說明

[回 Skill 目錄](README.md) · [安裝](../installation.md) · [知識選配](../knowledge-packages.md)

套件版本：`0.2.15`。操作名稱以實際安裝的 metadata 為準。

## 用途與操作

`implement` 一個 class/object/method/local symbol/query 上的單一技術操作，以及直接呼叫點或即時測試。

## 輸入與輸出

提供一個主要技術目標、行為、授權、規則、允許相依半徑、技術、可寫檔案及驗證命令；輸出有界程式變更、實際 touched radius、相容性、檢查結果與手交決策。

## 何時用／界線

公開合約或協調行為變更應選 slice；檔案數不是判斷標準。需要授權 target editor，沒有它不可實作。

## 範例請求

使用 `local-change-implementer implement`，只修正 `ParseDate` 對 ISO offset 的處理及其直接單元測試；不變更公開合約或其他解析器，執行我指定的測試。

## 知識

可選 `engineering-common@0.4.2`（1 項）與 `dotnet@0.3.1`（依當前 allowlist 選讀）實作 binding；未裝時通用局部修復可做，不能宣稱特定 .NET 標準已覆蓋。

將既有驗證計畫視為初步安排，實作期間依實際差異校正條件式檢查，執行前確認必要性。
修改完成後確認驗收證據齊備；必要 gate 與已接受驗收不得自行取消。
新增的跨 task 影響交回編排 owner；未選用 orchestrator 時由既有 task owner 協調。
重現 bug、TDD 或分段檢查可在修改前或修改中進行，不要求所有測試等到最後。
無語意影響的說明或空白不自動觸發測試；會影響解析、schema 或輸出的空白仍需檢查。
高成本驗證須有受影響行為／邊界或明確要求，且不自動展開全矩陣。
專案必要的 PR、安全及發版義務仍有效；未執行不代表通過。

## 開始使用

先確認此 skill 已在專案的 runtime entries 中。向 agent 提供上面的操作、
實際範圍與輸入；範例 prompt 是自然語言請求，不是 shell 指令。
明確指定輸出位置及可寫範圍。使用 prefixed 安裝時，選單中的名稱可能是
`aicf-local-change-implementer`；canonical package ID 仍為 `local-change-implementer`。

此套件提供指令方法，不提供同名 CLI。Agent 依已安裝的 operation
reference 執行；若本次任務需要編輯或測試，使用專案已有且被授權的工具。

## 宣告的知識資源

以下宣告皆為 optional allowlist；不是每次必讀清單。未選、缺少或無法驗證時，揭露 coverage unavailable。

### common-local-change

`engineering-common@0.4.2`；操作：`implement`。

- `engineering-rule-catalog`

### dotnet-local-change

`dotnet@0.3.1`；操作：`implement`。

- `engineering-rule-catalog`
- `member:application-types/web-api/controller-standards.md`
- `member:architecture/ddd-cqrs/aggregate-standards.md`
- `member:architecture/ddd-cqrs/usecase-standards.md`
- `member:integration/persistence/repository-standards.md`
- `member:references/policy-rationale.md`
- `member:testing/test-standards.md`
- `member:tooling/development-tools.md`
- `member:tooling/generation/README.md`
- `member:tooling/implementation-guidance.md`

依目標已採用的技術與本次操作選讀；允許讀取不代表採用規則，連結不擴大 allowlist。

通用 skill 入口與操作方法保持技術中立。只有選用 `dotnet` 知識套件時，共用 skill 的 `references/knowledge/dotnet/tooling/` 才放入該套件的 `implementation-guidance.md` 參考檔，引導按需讀取開發及 generation 指引；取消選用並透過既有更新流程套用後，相應參考檔會移除，`SKILL.md` 與 Codex／Claude 入口主文保持相同。選用不等於採用規約或安裝工具，實際讀取仍遵守 installed-resource protocol。

## 權威參考

- [Skill 入口](../../src/skills/local-change-implementer/SKILL.md)
- [版本、操作、依賴與 runtime metadata](../../src/skills/local-change-implementer/skill-package.yaml)
- [references/implement.md](../../src/skills/local-change-implementer/references/implement.md)

上述連結方便在來源庫核對；實際使用時應讀取已安裝套件中的相同資源。

明確選擇程式碼產生時，可按需讀取 generation 指引，使用原生模板或 snippet 工具。先 inspect 適用位置與參數，再將 render 的文字插入已檢查的脈絡；展開不等於語意整合或通過編譯。
