# spec-compliance-validator 使用說明

[回 Skill 目錄](README.md) · [安裝](../installation.md) · [知識選配](../knowledge-packages.md)

套件版本：`0.1.0`。操作名稱以實際安裝的 metadata 為準。

## 用途與操作

`plan-validation` 建完整 criteria/evidence plan；`review-semantics` 對固定 subject 做語意/完整性審查；`assess-runtime` 對每條 criterion 的真實證據做 scoped conclusion。

## 輸入與輸出

輸入版本化 artifact/規則、subject、authority、必要證據，runtime 時另要固定 code/tests/config/dependencies、profile、真實 runs 或授權執行；輸出 criterion inventory、findings 或 evidence matrix、排除項與 `not-compliant`/`unavailable`/`compliant-within-scope` 結論。

## 何時用／界線

不自動修復、建測試、安裝/restore、build、provider 操作或全域 gate。criteria 規劃、結構、語意與 runtime 結論必須分開；僅在明確選 `problem-frame.cbf@1.0.0` 時，結構層需要實際 `problem-frame-author` reader result。

## 範例請求

使用 `spec-compliance-validator plan-validation`，對此固定規格列出每個驗收條件所需的語意與 runtime 證據，標示尚缺 owner、環境或指令；不要聲稱已合規。

## 知識

無套件綁定；另有顯式 opt-in `dotnet@0.1.0` instruction profile，非 SDK、非自動由 `.csproj` 啟用。

## 開始使用

先確認此 skill 已在專案的 runtime entries 中。向 agent 提供上面的操作、
實際範圍與輸入；範例 prompt 是自然語言請求，不是 shell 指令。
明確指定輸出位置及可寫範圍。使用 prefixed 安裝時，選單中的名稱可能是
`aicf-spec-compliance-validator`；canonical package ID 仍為 `spec-compliance-validator`。

此套件提供指令方法，不提供同名 CLI。Agent 依已安裝的 operation
reference 執行；若本次任務需要編輯或測試，使用專案已有且被授權的工具。

## 權威參考

- [Skill 入口](../../src/skills/spec-compliance-validator/SKILL.md)
- [版本、操作、依賴與 runtime metadata](../../src/skills/spec-compliance-validator/skill-package.yaml)
- [references/compliance.md](../../src/skills/spec-compliance-validator/references/compliance.md)
- [references/report-template.md](../../src/skills/spec-compliance-validator/references/report-template.md)
- [references/legacy-intake.md](../../src/skills/spec-compliance-validator/references/legacy-intake.md)
- [profiles/dotnet.md](../../src/skills/spec-compliance-validator/profiles/dotnet.md)

上述連結方便在來源庫核對；實際使用時應讀取已安裝套件中的相同資源。
