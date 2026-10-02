# ai-context-init 使用說明

[回 Skill 目錄](README.md) · [安裝](../installation.md) · [知識選配](../knowledge-packages.md)

套件版本：`0.1.0`。操作名稱以實際安裝的 metadata 為準。

## 用途與操作

`initialize` 建立缺少的協作入口與文件骨架；`refresh` 僅更新已初始化 context 中的可驗證事實、指令與導覽。

## 輸入與輸出

提供目標 repository、所求 context、可寫範圍、目前規則與可用證據；輸出 project-owned 文件或 proposal、變更摘要、來源、未解事實與實際驗證狀態。

## 何時用／界線

不是 framework 安裝器；refresh 不重設規則、文件責任或 precedence，這些屬治理工作。不得把模板不加判斷地複製進目標。

## 範例請求

使用 `ai-context-init initialize`，為此既有 repository 建立最小 AGENTS 與 `.dev` 導覽，只寫入我列出的文件；根據現有檔案填入事實，未知處明確標示。

## 知識

無套件綁定。

## 開始使用

先確認此 skill 已在專案的 runtime entries 中。向 agent 提供上面的操作、
實際範圍與輸入；範例 prompt 是自然語言請求，不是 shell 指令。
明確指定輸出位置及可寫範圍。使用 prefixed 安裝時，選單中的名稱可能是
`aicf-ai-context-init`；canonical package ID 仍為 `ai-context-init`。

此套件提供指令方法，不提供同名 CLI。Agent 依已安裝的 operation
reference 執行；若本次任務需要編輯或測試，使用專案已有且被授權的工具。

## 權威參考

- [Skill 入口](../../src/skills/ai-context-init/SKILL.md)
- [版本、操作、依賴與 runtime metadata](../../src/skills/ai-context-init/skill-package.yaml)
- [references/initialize.md](../../src/skills/ai-context-init/references/initialize.md)
- [references/project-structure.md](../../src/skills/ai-context-init/references/project-structure.md)
- [templates/public-root/AGENTS.md](../../src/skills/ai-context-init/templates/public-root/AGENTS.md)
- [templates/public-root/CLAUDE.md](../../src/skills/ai-context-init/templates/public-root/CLAUDE.md)
- [templates/public-root/README.md](../../src/skills/ai-context-init/templates/public-root/README.md)
- [templates/public-catalogs/dev/README.MD](../../src/skills/ai-context-init/templates/public-catalogs/dev/README.MD)
- [templates/public-catalogs/dev/INDEX.md](../../src/skills/ai-context-init/templates/public-catalogs/dev/INDEX.md)
- [templates/project-config.template.yaml](../../src/skills/ai-context-init/templates/project-config.template.yaml)
- [templates/architecture.md](../../src/skills/ai-context-init/templates/architecture.md)
- [templates/technology-requirements.md](../../src/skills/ai-context-init/templates/technology-requirements.md)

上述連結方便在來源庫核對；實際使用時應讀取已安裝套件中的相同資源。
