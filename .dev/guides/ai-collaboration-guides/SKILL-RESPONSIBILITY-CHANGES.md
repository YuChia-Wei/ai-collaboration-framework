# Skill 增減與職責變遷

這份盤點回答「哪些 skill 新增、移除、改名，以及同名職責、行為與原因是否改變」。
2026-10-01 的修復由 [#421](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/421)
與 [本次 workflow](../../workflows/2026-10-01-orchestrator-restore/workflow.yaml) 追蹤。
來源存在、catalog 可選、runtime 已安裝與產品行為驗收是不同狀態。
本次修復保留既有 RC3 發布歷史。負責人已授權來源與 MQ lab 合併至 main 並推送；
實際安裝與整合是分開的證據，見[結果紀錄](../../workflows/2026-10-01-orchestrator-restore/results.md)
與 live PR／main read-back。下表的原因來自已記錄需求／設計／owner 選擇；
沒有另行記錄的動機會明列未知，推論不寫成當時決定。

## 固定比較基準與數量

2026-10-02 後續來源變更：[#427](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/427)
新增可選的 `ai-context-init@0.1.0` 與獨立 `project-initialization` preset，
把 AGENTS 與專案文件初始化恢復為 authoring 指引。Catalog 因此為 18 個；
既有 presets 與來源專案的 17-skill installation 不變。它不恢復舊版安裝流程，
安裝套件也不會自動產生根目錄文件。詳見[來源交付紀錄](../../workflows/2026-10-02-source-development/initialization.md)。
以下固定比較表保留各歷史時點；舊 `ai-context-init` 的退役不代表本次尚未存在。

| 階段 | 固定 Git subject | Source／catalog | 來源專案 runtime |
| --- | --- | --- | --- |
| 重構前，2026-09-22 | `c2e7071335d02d9b8d40ab4dcaf437e690791741` | 16 個 canonical skills；其中 release-closeout 不發布，所以 portable 是 15 個 | 舊 16 個 |
| RC1，2026-09-23 | `3755b217421a4f1238f740a09de7e034ccf56038` | 新 `src/skills` 有 18 個 packages | 當時尚未採用，仍為舊 16 個 |
| RC2 實際採用，2026-09-29 | `03ffb961d397955c61a6a0b253aa640de99f9f49` | 18 個 | core／Codex／Claude 各 18 個 |
| RC3 退休前 | `973c477bca6ed6fb33c5c6d9d997c5b9ebaa1baa` | 18 個 | 各 18 個 |
| 本次修復前 RC3 | `a2ed2e3ebbba2acaae2f9574b52302379e01fc48` | 17 個 | 各 17 個 |
| 本次修復來源 | package commit `16f3f0c072bd22c3945fce8aca8295bf2b88f330`；後續文件／整合由 Git 與 PR 識別 | 18 個，恢復 orchestrator | core／Codex／Claude 各 18 個；來源與 MQ installer 已實際回讀 |

計算為 **舊 16 − 退休 3 + 新增 5 = RC2 18；RC3 再移除 1 = 17；本次恢復 1 = 18**。
這是恢復當時的歷史計算。本次 owner 另將 standards-promotion 改列未發布試驗：
可編輯 source 仍有 18 個，distribution catalog 與 managed installation 改為 17 個；
MQ lab 另有 1 個獨立 experimental route，不能算成第 18 個 managed skill。
若只算 portable，起點是 15，退休 portable 2，再新增 5，同樣得到 18。
RC1 同時存在新舊來源目錄，不可相加成 34 個 skills。RC1→RC2 沒有 ID 增減，
主要是安裝採用與知識消費契約改變。`engineering-common`、`dotnet-backend`
是 knowledge packages，不列入 skill 數量；來源專案未選知識，不代表 mq lab 也未選。

## 本次恢復（1 個）

| Skill／歷史名稱 | 增減／時點 | 職責／行為：之前 → 現在 | 原因與承接狀態 |
| --- | --- | --- | --- |
| `software-development-orchestrator` | 同名契約改變 → RC3 退役 → 本次恢復 | 舊版高階意圖、階段排序、專業路由、核准、測試、審查、交接／收尾 → RC1/RC2 主要是十個 workflow record tools → 現在 `orchestrate`／`resume` 恢復開發編排，紀錄由專案擁有。 | #415 記錄 owner 覺得 workflow-v2 與預期不符、和既有 workflow 太相似，因此要求移除整個新套件；#417 落實。該選擇仍要求保留 legacy 編排 duty。比對顯示 duty 沒有完整 portable successor；本次依直接 owner 要求補回 stage coordinator。**編排缺口是分析結果，不是 owner 當時要求刪除舊編排。**（O） |

## 退役（3 個，目前仍退役）

| Skill／歷史名稱 | 增減／時點 | 職責／行為：之前 → 現在 | 原因與承接狀態 |
| --- | --- | --- | --- |
| `ai-context-init` | RC2 runtime 退役；RC3 清除舊來源 | repo discovery／architecture docs／project-config／provenance 初始化 → P6 installer 僅管理新格式 components。沒有 current portable init。 | D342-03 選擇把機械 installation/update 交 P6；提案理由是安裝單一 skill 不應被 public-root、project-config、translator 等整套 repo 初始化前置綁住。**沒有證明 installer 等價承接舊 repo 初始化或 published-format duty；舊 duty 保留，但 route 未恢復。**（P5） |
| `ai-context-upgrader` | RC2 runtime 退役；RC3 清除舊來源 | 舊發布格式三方比較／客製化／multi-hop upgrade／recovery → 新格式 maintenance/reinstall；舊格式執行路由目前不可用。 | D342-03 分離 P6 機械更新，舊 upgrade scripts、route matrix、role registry 不預設進入新 package；已記錄需求摘要要求減少大量歷史升級 I/O 與自我測試干擾。**沒有選擇放棄 active legacy recovery；舊 owner/duty 留存。**（P5、N） |
| `ai-context-release-closeout` | RC2 source runtime 退役；RC3 清除舊來源 | source-only post-tag read-back／例外 records-only recovery → source release policy、`releases/` 和治理程序。 | D342-03 明確把 source release/history duties 留在來源 repo；不把 Git/provider/handoff history 出貨為 portable skill。它原本 never packaged，因此這不是 portable skill 的新增缺口；目前沒有 installed successor。（P5） |

## 歷史新增與改名（5 個）

| Skill／歷史名稱 | 增減／時點 | 職責／行為：之前 → 現在 | 原因與承接狀態 |
| --- | --- | --- | --- |
| `adr` → `adr-author` | RC1 新增；RC3 改名 | 舊 `.dev/adr` 文件治理 → standalone alternatives、mapped owner decision、revision/supersession history；RC3 保留 schema/record IDs/filenames/locks。 | 已記錄需求 1-4 要求 ADR 撰寫／讀取標準化為 skill；P3 把 decision/history owner 與 project-rule owner 分開。RC3 owner 明確指定 author 名稱；**未找到更深入的命名動機紀錄**，不能把名稱語意推論寫成決策理由。（N、L、R） |
| `lesson` → `lesson-author` | RC1 新增；P3 lifecycle 擴充；RC3 改名 | 手動 lessons → evidence-qualified observations／mapped acceptance／history；candidate-only v1 唯讀，explicit derive 新 v2 identity。 | 需求 1-4／1-6 要標準化 Lesson 並將回顧轉成 lessons；v1 固定 candidate，不能表達 acceptance/history，所以新增 v2 而不強制 migration。RC3 owner 指定 rename，保留 record family；**未另載命名動機**。Accepted lesson 不等於 adopted rule。（N、L、R） |
| `pr` → `pr-author` | RC1 新增；RC3 改名 | PR 文件需求 → standalone actual Git comparison/content-bound record＋另外授權的 GitHub read/create/update。 | 需求 1-5 要 PR 標準化成 skill；P3 不要求先有 workflow/ADR/Lesson，並拆開 credential、approval、expected state、post-read/result。RC3 owner 指定 rename、保留 identities；**未另載命名動機**，沒有新增 merge／Issue／release 權限。（N、W、R） |
| `local-backlog` | RC1 新增 | project-local work-item 需求 → stable IDs、acceptance、conflict-aware local state；GitHub links reference-only。 | 需求 1-11 要 local-file backlog 標準化；P3 選唯一 local writer，把本地紀錄與 remote tracker authority 分開，避免 implicit sync 或復活 source frozen backlog。（N、W） |
| `standards-promotion` | RC1 新增 | ADR/Lesson 轉規範的需求 → evidence-bound proposal，分別觀察 owner adoption、實際 rule bytes 與 effect；沒有 `apply`。 | 需求 1-7 要從 ADR/Lesson 形成 standards；P3 刻意拆開 proposal、actual adoption、rule bytes、effect，避免工具自行改規則或產生自己的核准證據。規則寫入／採用仍由 project owner 決定。（N、L） |

## 保留 ID 的行為與職責變化（12 個）

| Skill／歷史名稱 | 增減／時點 | 職責／行為：之前 → 現在 | 原因與承接狀態 |
| --- | --- | --- | --- |
| `ai-context-auditor` | 同 ID；audit 範圍與輸出收斂 | 強制 independent baseline＋repository pass、source ASM lifecycle → scoped `audit`／`compare`、prose 預設、caller 選 export/project format。 | D352-01/02 要求維護能力獨立可選，單一 scoped question 不強制兩次獨立執行或 automatic pre-task gate；新 machine assessment family 沒有被選定的 consumer。舊 source ASM owner 保留；普通 audit 不代表獨立審查。（M） |
| `ai-context-governance` | 同 ID；authority 拆分 | boundary/routing/wrapper/migration/customization ledger 與完整 remediation lifecycle → bounded project-owned `propose`／`apply`。 | D352-03/04/05 分離 target edit、source duty、P6 install/recovery，避免第二 customization ledger 或 universal resolver 形成歧義權威。Managed core／lock／projection／catalog／release／active recovery 各自保留 owner；沒有撤銷既有 adopted contract。（M） |
| `problem-frame-author` | 同 ID；machine 格式換約 | legacy 多檔、未獨立版本化的 CBF/SWF YAML → semantic draft/review＋單檔 `problem-frame.cbf@1.0.0` JSON snapshot。 | 設計比較指出 CBF 有 concrete 五檔模板、SWF 在該 scoped subtree 沒有 concrete template；多檔更新／recovery 較複雜。選 bounded typed-ID snapshot，避免沒有 demonstrated need 的 generic CBF+SWF engine。**不是 legacy compatibility；不自動轉換舊 records，也不取消 SWF semantic duty。**（F） |
| `spec-compliance-validator` | 同 ID；結論與證據層重新界定 | legacy CBF/SWF／.NET 100% gate＋source command/path → `plan-validation`／`review-semantics`／`assess-runtime`，.NET 明確 opt-in。 | 舊 references 混 portable criteria 和 xUnit/BDDfy/NSubstitute/path/100% language；舊 shell check 只比名稱／檔名、缺項也可 exit 0，不能證明 C# semantics/runtime。新 package 分開結構、語意、執行，不複製 author-owned parser。**Target-selected legacy 100% gate 仍須另保留／恢復 route。**（F） |
| `requirement-author` | 核心保留；RC1 standalone；RC3 補資源 | stakeholder/business-rule/acceptance 核心 → `draft`／`normalize`、caller-selected template/path，無 destination 可留 conversation；RC3 加回 presentation guide。 | 讓 authoring method 可單獨使用，移除 source `.dev`、mandatory machine schema/store 與固定 pipeline。RC3 查出保留的 reusable guide 不在 package closure，所以正式補回可達資源。（A、N） |
| `spec-author` | 核心保留；RC1 standalone；RC3 補資源 | production/entity/adapter/formal-test spec → caller-selected format/template/path；formal-test artifact ownership 保留，RC3 加回兩份 guides。 | 保留 artifact-type/source binding，解除固定 source layout、aggregate/.NET 預設與 mandatory machine record。RC3 consolidates guides，重用 package template 並去除 duplicate/fixed source conventions。（A、N） |
| `diagnostic-analyst` | 核心保留；instruction 化 | falsifier-first／reproduction／intervention／causal admission → instruction `diagnose`、prose 預設；舊 diagnostic JSON 1.0／validator/store 不移植。 | #347 選擇保留方法、移除 hidden source paths 與未選 prerequisites；machine format 若保留須有真實 accountable operation，prose 不必 JSON。診斷仍只提供 repair proposal，不授予修復權限；**沒有單獨量化刪除 JSON/store 的收益證據。**（E、P5） |
| `bdd-gwt-test-designer` | 核心保留；RC2 optional knowledge | GWT/source-row/expected-value/assertion/setup/test-level 與唯讀 review → common `design`／`review`；runner、實作、執行由 target 選擇。 | 拆開 scenario reasoning 與 target runner/test implementation，避免固定路徑／未選技術阻擋設計。RC2 增加 task-scoped verified knowledge access；選 package/binding 不自動 adopt target rule 或 runner。（E、K） |
| `ddd-ca-hex-architect` | 核心保留；RC2 optional knowledge | domain/invariant/data owner／ports/dependencies／alternatives/design/review → explicit target inputs，ADR/spec/implementation 為按需要 handoff。 | Architecture method 可跨 target 使用，source convention／未選 .NET 不應隱式生效；少量 shared review meaning 放入 consumer 讓 package standalone。RC2 optional knowledge 經已安裝 verified resource/binding 讀取。（E、K） |
| `code-reviewer` | 同 ID；先 common-only，RC2 optional knowledge | common＋optional tech routing、source assessment/role/packet dependencies → common instruction review，.NET specialist 不內建。 | P5 選擇真實三-member common package，避免假 executable/store/Python runtime；tech extension 另行選擇。RC2 reader 只取 verified allowlist resources，required specialist gap 必須明示，不能把 common review 算成 specialist coverage。（P5、K） |
| `local-change-implementer` | 核心保留；RC2 optional knowledge | 一個 target/operation、直接半徑與 immediate tests → explicit target rules/commands，可涵蓋數個 direct-call-site 檔案。 | Semantic impact 比 file count 適合界定 local/slice；standalone local work 不應被 source ceremony 或反覆跳回 orchestrator 阻擋。RC2 optional knowledge 保留 target authority；public-contract 變更仍需要已接受的 scope。（E、K） |
| `slice-implementer` | 核心保留；RC2 optional knowledge | command/query/reactor/generic/remediation、accepted architecture/GWT、internal edits/tests → explicit target inputs，無 mandatory technology role registry。 | Generic slice 要能在沒有 .NET/private-role tree 的 target 使用，移除 hidden/unselected prerequisites，保留 slice 內部 edits/tests owner，避免 per-method handoff。Legacy「no new type」改為 shared private-helper semantic rule，沒有任意新增 public type 的授權。（E、K） |

在這五個新 standalone skills 中，ADR 與 Lesson 有已核實的既有文件治理前身；
「新增 skill」不等於所有能力從零發明。三個 author 改名是零淨增減，也不是三個新功能。

## 預發布暫停出貨（1 個；不是退役）

| Skill | 現況 | 原因與驗證責任 |
| --- | --- | --- |
| `standards-promotion` | `0.1.1-alpha.1`；保留 `src`，移出 distribution manifest 與四個 presets；MQ lab 使用獨立複製的 `standards-promotion-experimental`。 | Owner 要先另外驗證用途與行為，才判斷能否發布。Framework 成品及正常安裝不包含此 package；release readiness 尚未成立。Record schema、config namespace 與歷史仍保留。 |

此選擇由 [#423](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/423)
及[本次 workflow](../../workflows/2026-10-01-standards-promotion-hold/workflow.yaml)追蹤。
新的 framework catalog/engine 成品以 manifest closure 排除它；可編輯 Git source 與
既有 immutable tags/release artifacts 保留各自原始內容。重新發布仍需 owner 另行選擇。

## 原因證據與可重現定位

表內代號指向固定 Git 文件；原因和實際承接狀態分開。需求摘要 N 是當時 workflow
保留的原始需求整理，本次沒有把它冒充已重新逐字核驗 archived chat 原文。

| 代號 | 固定證據 | 對應原因 |
| --- | --- | --- |
| P5 | [P5 selected contract](https://github.com/YuChia-Wei/ai-collaboration-framework/blob/3755b217421a4f1238f740a09de7e034ccf56038/.dev/design/framework-next/p5-selected-contract.md#L3-L12)；[capability disposition](https://github.com/YuChia-Wei/ai-collaboration-framework/blob/3755b217421a4f1238f740a09de7e034ccf56038/.dev/design/framework-next/capability-consolidation/capability-disposition.md#L15-L36) | D342-03/04、P6 mechanics、source-only release/history、common-only reviewer、legacy duty retention。Disposition 文件是設計提案；已選契約列出被選定的分工。 |
| M | [Optional maintenance design](https://github.com/YuChia-Wei/ai-collaboration-framework/blob/3755b217421a4f1238f740a09de7e034ccf56038/.dev/design/framework-next/optional-context-maintenance/README.md#L16-L43)；[responsibility boundaries](https://github.com/YuChia-Wei/ai-collaboration-framework/blob/3755b217421a4f1238f740a09de7e034ccf56038/.dev/design/framework-next/optional-context-maintenance/responsibility-boundaries.md#L11-L60) | D352-01–05、可選 scoped audit、治理／安裝／source authority 拆分與原 owner recovery。 |
| A | [Portable authoring design](https://github.com/YuChia-Wei/ai-collaboration-framework/blob/b6ba669ff465bb6c6429bcc24cdf9b37af0ce964/.dev/design/framework-next/portable-authoring/design.md#L77-L102) | requirements/spec 方法保留、caller format/path、去 source/.NET/mandatory machine conventions。 |
| E | [Engineering method extraction](https://github.com/YuChia-Wei/ai-collaboration-framework/blob/814fd12822bb270f17edbfe91d0864ba07c1aacb/.dev/design/framework-next/engineering-methods/README.md#L49-L83) | 五個工程方法的 retained reasoning 與 removed dependencies，診斷／GWT／架構／local／slice 的 standalone 邊界。 |
| F | [Problem-frame/compliance design](https://github.com/YuChia-Wei/ai-collaboration-framework/blob/3755b217421a4f1238f740a09de7e034ccf56038/.dev/design/framework-next/problem-frame-compliance/README.md#L20-L78)；[final capability contract](https://github.com/YuChia-Wei/ai-collaboration-framework/blob/3755b217421a4f1238f740a09de7e034ccf56038/.dev/design/framework-next/p5-final-capability-contract.md#L7-L15) | CBF snapshot 選擇、避免 premature generic engine、舊 textual checker 的證據限制、compliance 三層。 |
| K | [RC2 knowledge consumers](https://github.com/YuChia-Wei/ai-collaboration-framework/blob/03ffb961d397955c61a6a0b253aa640de99f9f49/.dev/workflows/2026-09-24-rc2-knowledge-consumers/workflow-plan.md#L3-L55) | 五個 generic skills 的 verified selected-resource access、target authority/binding 與 prior correction history。 |
| N | [RC3 knowledge disposition](https://github.com/YuChia-Wei/ai-collaboration-framework/blob/a2ed2e3ebbba2acaae2f9574b52302379e01fc48/.dev/workflows/2026-09-30-rc3-reinstall/knowledge-disposition.md#L44-L105) | presentation-guide closure 修補（54–56）、原始需求摘要（81–105）：ADR/Lesson、PR、standards promotion、local backlog、減少歷史升級 I/O。 |
| L | [Knowledge lifecycle contract](https://github.com/YuChia-Wei/ai-collaboration-framework/blob/3755b217421a4f1238f740a09de7e034ccf56038/.dev/design/framework-next/knowledge-lifecycle/contract.md#L12-L43)；[P3 selected contract](https://github.com/YuChia-Wei/ai-collaboration-framework/blob/3755b217421a4f1238f740a09de7e034ccf56038/.dev/design/framework-next/p3-shared-contract.md#L36-L48) | standalone ADR/Lesson、v1/v2 lifecycle 原因、proposal/adoption/rule bytes/effect 分離。 |
| W | [Work-management contract](https://github.com/YuChia-Wei/ai-collaboration-framework/blob/3755b217421a4f1238f740a09de7e034ccf56038/.dev/design/framework-next/work-management/contract.md#L55-L86) | local backlog 與 remote authority 分離、PR actual content/head/check 綁定。 |
| O | [Issue #415](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/415)；[Issue #417](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/417)；[fixed RC3 plan](https://github.com/YuChia-Wei/ai-collaboration-framework/blob/a2ed2e3ebbba2acaae2f9574b52302379e01fc48/.dev/workflows/2026-09-30-rc3-reinstall/workflow-plan.md#L3-L25) | owner 選擇完整 retirement workflow-v2，仍保留 legacy workflow 模式/duties；開發編排缺口另由 old/new contracts 比對確認。 |
| R | [Fixed RC3 rename results](https://github.com/YuChia-Wei/ai-collaboration-framework/blob/a2ed2e3ebbba2acaae2f9574b52302379e01fc48/.dev/workflows/2026-09-30-rc3-reinstall/results.md#L12-L22) | owner 指定三個 author 改名，保留 record families/identities。未找到額外命名動機，不推論為權限或功能新增。 |

RC3 也把技術無關的 domain-language 與 operations 指引收進 `engineering-common`，
將 retained guidance 條件化並修復可達性（N:7、24–27、44–56）。這是 knowledge
package 的內容／分工變化，不新增 skill 數量；可選資源存在也不等於 target 已採用。

## Orchestrator 修復範圍

[`software-development-orchestrator@0.2.0`](../../../src/skills/software-development-orchestrator/SKILL.md)
恢復的是 development lifecycle coordination：依目標選階段、解析已安裝能力、
直接套用或實際委派 specialist、保留核准、驗證結果、交接與 closeout。
小型單階段修改仍交給其 owner；不把所有工作變成固定 requirements→release pipeline。
User/project 明確選擇優先，不重複要求已有的核准。

它不恢復 RC2 的十個 workflow record tool operations、JSON store、writer lock、
retention tooling 或紀錄 migration。`configuration: null`，沒有 scripts/schema/store
相依。專案選擇既有 workflow 格式與 writer；新 skill 不覆寫 target authority。
因此「恢復編排」和「恢復／設計儲存工具」是分開的責任與驗收。

舊職責在
[legacy routing](https://github.com/YuChia-Wei/ai-collaboration-framework/blob/5a802e58a1473aae8cd139fcffd45a35587cb26b/.ai/assets/skills/software-development-orchestrator/references/routing-playbook.md#L16-L48)
與
[stage coordination](https://github.com/YuChia-Wei/ai-collaboration-framework/blob/5a802e58a1473aae8cd139fcffd45a35587cb26b/.ai/assets/skills/software-development-orchestrator/references/routing-playbook.md#L111-L134)。
RC2 record-only 契約在
[operations](https://github.com/YuChia-Wei/ai-collaboration-framework/blob/973c477bca6ed6fb33c5c6d9d997c5b9ebaa1baa/src/skills/software-development-orchestrator/references/operations.md)。
RC3 retirement 與 author renames 是
[`ac5e34e`](https://github.com/YuChia-Wei/ai-collaboration-framework/commit/ac5e34e397ca38b2efa1581fed34ca5c4fb23baa)；
legacy 資源另外於 `526150aa6e966a8924bce07b2a9c89a71b7370f4` 清理。
這兩項清理沒有留下完整 portable 開發編排入口；本次追加修復，不改寫舊紀錄。

## 已在更早版本退休的名字

`repo-structure-sync` 與 `dev-workflow` 在 v0.16.0 就已退休，不能算作 RC3 新刪除。
[固定 transition](https://github.com/YuChia-Wei/ai-collaboration-framework/blob/c2e7071335d02d9b8d40ab4dcaf437e690791741/.ai/assets/skills/transitions/v0.16.0.yaml)
分別指定 `ai-context-init` 與 `software-development-orchestrator` 作後續路由。
init 現在沒有可用路由，不代表可復活 retired alias；恢復 orchestrator 也不需要恢復 `dev-workflow` 別名。

## 查核與使用限制

盤點方法是固定 Git registry/skill metadata/entry 與 manifest/profiles 對照，
必要時只讀直接引用的 responsibility contracts。以 `git show <SHA>:<path>`
可重現；新來源以 manifest 中 `kind: skill` 的 component IDs 計數。
Legacy 使用 `.ai/assets/skills/README.MD:25-42`，不能把 retired transition entries
或 source-only release-closeout 算成 portable package。Actual RC2 runtime cutover
見固定 `03ffb961` 的 `.agents/skills/README.md`；新 catalog 存在本身不證明安裝。

五個工程 skills 在 RC2 將 metadata 3→4、package 0.1.0→0.2.0，加入 optional
`knowledge_consumption`：BDD、architect、reviewer、local implementer、slice implementer。
本表依 current package scope 記錄責任，並不驗收每個 runtime 行為。
其他 skill 被保留的檔案或 source duty，不代表對應工具已可用。

本次 readability/metadata/link/diff 與 installer read-back 依 results 逐項列示。
Legacy/full/native 與 hosted test/admission gates 仍為 U001 的
`deferred-by-owner`（#322 coordinator/P7），不是 passed。Skill 加回 catalog、安裝
成功、commit、main 整合、release 和 target rule adoption 仍分開報告。
