# slice-implementer 使用說明

[回 Skill 目錄](README.md) · [安裝](../installation.md) · [知識選配](../knowledge-packages.md)

套件版本：`0.2.0`。操作名稱以實際安裝的 metadata 為準。

## 用途與操作

`implement` 一個已授權行為、協調重構或具體測試 slice；主模式必須剛好選 `command`、`query`、`reactor`、`generic` 之一，`remediation` 只是 overlay。

## 輸入與輸出

提供目標、意圖/驗收/非目標、既有授權、架構、技術、可寫路徑、驗證命令，測試時附情境；輸出實作、實際 touched files、驗證、延後工作、情境到斷言 mapping 和 finding disposition。

## 何時用／界線

適合協調行為或公開合約改動；單一局部技術操作可留給 local-change。需要授權 editor，不能自行選技術或把 finding 當權限。

## 範例請求

使用 `slice-implementer implement`，以 command mode 實作『建立預約』行為和已選 GWT 情境測試；範圍限於 application、domain、immediate tests，沿用已接受的 outbox 決策；如發現尚未決定的交易邊界，先回報該阻塞。

## 知識

可選 `engineering-common@0.1.0`（2 項）與 `dotnet-backend@0.1.0`（7 項）binding；未裝時 generic/common slice 仍能執行，但不能自稱 .NET 專門設計/交易/測試涵蓋。

## 開始使用

先確認此 skill 已在專案的 runtime entries 中。向 agent 提供上面的操作、
實際範圍與輸入；範例 prompt 是自然語言請求，不是 shell 指令。
明確指定輸出位置及可寫範圍。使用 prefixed 安裝時，選單中的名稱可能是
`aicf-slice-implementer`；canonical package ID 仍為 `slice-implementer`。

此套件提供指令方法，不提供同名 CLI。Agent 依已安裝的 operation
reference 執行；若本次任務需要編輯或測試，使用專案已有且被授權的工具。

## 宣告的知識資源

以下全部為 optional；未選、缺少或無法驗證時，不可宣稱具備對應專業覆蓋。

### common-implementation

`engineering-common@0.1.0`；操作：`implement`。

- `engineering-rule-catalog`
- `member:references/GWT-TEST-HANDOFF-CONTRACT.md`

### dotnet-implementation

`dotnet-backend@0.1.0`；操作：`implement`。

- `engineering-rule-catalog`
- `member:standards/DESIGN-BY-CONTRACT.md`
- `member:standards/coding-standards/aggregate-standards.md`
- `member:standards/coding-standards/repository-standards.md`
- `member:standards/coding-standards/test-standards.md`
- `member:standards/coding-standards/transactional-messaging-standards.md`
- `member:standards/coding-standards/usecase-standards.md`

## 權威參考

- [Skill 入口](../../src/skills/slice-implementer/SKILL.md)
- [版本、操作、依賴與 runtime metadata](../../src/skills/slice-implementer/skill-package.yaml)
- [references/implement.md](../../src/skills/slice-implementer/references/implement.md)
- [references/modes/command.md](../../src/skills/slice-implementer/references/modes/command.md)
- [references/modes/query.md](../../src/skills/slice-implementer/references/modes/query.md)
- [references/modes/reactor.md](../../src/skills/slice-implementer/references/modes/reactor.md)
- [references/modes/generic.md](../../src/skills/slice-implementer/references/modes/generic.md)
- [references/test-handoff.md](../../src/skills/slice-implementer/references/test-handoff.md)
- [references/remediation.md](../../src/skills/slice-implementer/references/remediation.md)

上述連結方便在來源庫核對；實際使用時應讀取已安裝套件中的相同資源。
