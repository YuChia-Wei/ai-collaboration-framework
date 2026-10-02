# lesson-author 使用說明

[回 Skill 目錄](README.md) · [安裝](../installation.md) · [知識選配](../knowledge-packages.md)

套件版本：`0.2.0`。操作名稱以實際安裝的 metadata 為準。

## 用途與操作

保存有證據的觀察、信心與適用範圍。操作：`explain`、`create`、`inspect`、`query`、`validate`、`revise`、`render`、`derive`、`accept`、`retire`、`supersede`。

## 輸入與輸出

指定 roots/config；建立內容、觀察文字、決策及新身分選擇，更新用實際 SHA-256。輸出 record reference、digest、mutation state、查詢和診斷。

## 何時用／界線

適合保留觀察與後續行動；不是架構決策、專案規則修改或實作驗證。接受 Lesson 不採納規則；v1 僅能讀取，衍生為新 v2 identity。

## 範例請求

使用 `lesson-author`，先查詢重複觀察，再保存『壓測在固定條件下造成佇列延遲』的證據、信心、適用與不適用範圍；不要將其標為已採納規則。

## 知識

無套件綁定。

## 開始使用

先確認此 skill 已在專案的 runtime entries 中。向 agent 提供上面的操作、
實際範圍與輸入；範例 prompt 是自然語言請求，不是 shell 指令。
明確指定輸出位置及可寫範圍。使用 prefixed 安裝時，選單中的名稱可能是
`aicf-lesson-author`；canonical package ID 仍為 `lesson-author`。

此套件含可執行工具。先依[工具型 skills 共通設定](../tool-skills.md)
確認 Python 依賴、絕對 roots、設定及寫入限制，再執行 `explain`。
建立／變更 record 要按 operation reference 提供欄位；更新必須使用
實際讀回的 digest，不能自行填一個 hash。

## 權威參考

- [Skill 入口](../../src/skills/lesson-author/SKILL.md)
- [版本、操作、依賴與 runtime metadata](../../src/skills/lesson-author/skill-package.yaml)
- [references/configuration.md](../../src/skills/lesson-author/references/configuration.md)
- [references/operations.md](../../src/skills/lesson-author/references/operations.md)
- [references/example.md](../../src/skills/lesson-author/references/example.md)
- [lesson.record schema](../../src/skills/lesson-author/schemas/lesson-record.schema.json)
- [lesson.record schema](../../src/skills/lesson-author/schemas/lesson-record-v2.schema.json)

上述連結方便在來源庫核對；實際使用時應讀取已安裝套件中的相同資源。
