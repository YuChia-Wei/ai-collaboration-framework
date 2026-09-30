# RC3 知識文件處置與原始需求對照

本文件是 T2 已完成工作的外部整理，由 parent 納入 workflow。報告所列目前路徑固定於 source `5fcc4b5a484476af0c72b43d09a4c2b3693baf95`；不是目前未固定工作樹的宣告。T2 原始執行提交為 `8940ae9eae1fcb1464f82c7ad4564380af59a5ae`，原 worktree `F:/framework-next/rc3-knowledge`、branch `codex/rc3-knowledge`。父代理持有整合、完整 candidate build、實際試裝、驗收、GitHub／release 與主要專案採用。

## 結果與證據邊界

原 34 份搬移文件中 **32 份納入、2 份退休**。32 份分布為 **8 份移到 engineering-common、17 份 .NET 選用知識、3 份 common contracts、4 份 skill references**。表中的 consolidate 仍納入套件：共 29 include、3 consolidate、2 retire；沒有把 consolidate 誤算為未交付。

- E-T2：原 T2 在提交前實際執行 metadata loaders、skill 文件/schema/frontmatter 參照、typed dependency closure、knowledge file/resource/anchor closure、manifest schema/order／members／destination、既有 metadata 物件保持、變更 Markdown 檔案連結與 `git diff --check`，最終均通過。當時 optional unavailable resources 為 0。來源為本 agent 執行 log 與該提交 Validation 區塊，不是另造的驗收 receipt。
- E-READBACK：本次僅讀固定 `5fcc4b5a484476af0c72b43d09a4c2b3693baf95` 的 Git blobs，擷取目前 metadata／manifest／入口對應及大小；逐份確認 retained member、resource/reference、manifest destination 與 README／SKILL 直接入口，用於生成下表。這是固定 source 結構 read-back，沒有重跑 full matrix／CI，也不等於 product/runtime acceptance。
- K-dotnet-backend：`src/knowledge/dotnet-backend/content-package.yaml` 的 member/resource/reference + `src/distribution/manifest.yaml` 的 knowledge component + 同 package README。K-engineering-common 同理。
- S-*：目前 owning skill 的 `skill-package.yaml` resources.references + distribution manifest skill member + 同 skill SKILL.md。ADR author rename／record family 保留是父整合範圍；T2 原始 skill 名為 adr。
- R：退休檔案不在目前固定 tree，也不在出貨 metadata／manifest；原文仍可從 Git 歷史恢復。

T2 保留的失敗紀錄：一次路徑準備錯誤，以及兩次參照準備錯誤（未宣告六個頁內錨點、補充物件缺少 on_missing）均先修正，再取得最終 focused pass；失敗嘗試不記為 passed。完整 catalog assembly、行為矩陣、hosted CI 與 target behavioral acceptance 不是 T2 的完成宣告。Source U001/P7 deferrals 不移植為 target policy。

## 34 份文件逐一處置

Original path 指兩個搬移提交前的位置；目前路徑固定於上述 source HEAD。兩個搬移提交為 `526150aa6e966a8924bce07b2a9c89a71b7370f4` 與 `d9ddbc64370970b6275ce59b42508d05e0225dff`。搬移後但 T2 前的中介路徑保存在下一節，避免混淆第一次搬移和 T2 重新分類。

| # | Original path | Current path | Disposition | 精確註冊／入口證據與處置理由 |
| --- | --- | --- | --- | --- |
| 1 | `.dev/ARCHITECTURE.md` | `src/knowledge/dotnet-backend/design/architecture-overview.md` | include | K-dotnet-backend; resource `member:design/architecture-overview.md`; README 直接入口；選用架構概覽；修正套件連結，ES／持久化依目標選擇。E-T2 + E-READBACK。 |
| 2 | `.dev/domain-language/README.MD` | `src/knowledge/engineering-common/domain-language/README.MD` | include | K-engineering-common; resource `member:domain-language/README.MD`; README 直接入口；移至跨技術 common，重新撰寫實際語言來源與 owner 邊界。E-T2 + E-READBACK。 |
| 3 | `.dev/domain-language/templates/aggregate-vocabulary-template.md` | `src/knowledge/engineering-common/domain-language/templates/aggregate-vocabulary-template.md` | include | K-engineering-common; resource `member:domain-language/templates/aggregate-vocabulary-template.md`; README 直接入口；移至 common；原模板內容保持。E-T2 + E-READBACK。 |
| 4 | `.dev/domain-language/templates/bounded-context-language-template.md` | `src/knowledge/engineering-common/domain-language/templates/bounded-context-language-template.md` | include | K-engineering-common; resource `member:domain-language/templates/bounded-context-language-template.md`; README 直接入口；移至 common；原模板內容保持。E-T2 + E-READBACK。 |
| 5 | `.dev/domain-language/templates/domain-event-language-template.md` | `src/knowledge/engineering-common/domain-language/templates/domain-event-language-template.md` | include | K-engineering-common; resource `member:domain-language/templates/domain-event-language-template.md`; README 直接入口；移至 common；原模板內容保持。E-T2 + E-READBACK。 |
| 6 | `.dev/guides/implementation-guides/COMMON-MISTAKES-GUIDE.md` | `src/knowledge/dotnet-backend/guides/COMMON-MISTAKES-GUIDE.md` | include | K-dotnet-backend; resource `member:guides/COMMON-MISTAKES-GUIDE.md`; README 直接入口；條件化 ES／Wolverine；修路徑，註冊六個頁內錨點。E-T2 + E-READBACK。 |
| 7 | `.dev/guides/implementation-guides/COMPLETE-ASPNET-CORE-SETUP-GUIDE.md` | `src/knowledge/dotnet-backend/guides/COMPLETE-ASPNET-CORE-SETUP-GUIDE.md` | include | K-dotnet-backend; resource `member:guides/COMPLETE-ASPNET-CORE-SETUP-GUIDE.md`; README 直接入口；重寫為選用設定清單；不宣稱已建立 working app。E-T2 + E-READBACK。 |
| 8 | `.dev/guides/implementation-guides/CORS-SETUP.md` | `src/knowledge/dotnet-backend/guides/CORS-SETUP.md` | include | K-dotnet-backend; resource `member:guides/CORS-SETUP.md`; README 直接入口；修正套件內相對連結。E-T2 + E-READBACK。 |
| 9 | `.dev/guides/design-guides/DATA-CLASS-STANDARDS.md` | `src/knowledge/dotnet-backend/guides/DATA-CLASS-STANDARDS.md` | include | K-dotnet-backend; resource `member:guides/DATA-CLASS-STANDARDS.md`; README 直接入口；補目標適用範圍並修路徑。E-T2 + E-READBACK。 |
| 10 | `.dev/guides/implementation-guides/DATABASE-MIGRATION-GUIDE.md` | `src/knowledge/dotnet-backend/guides/DATABASE-MIGRATION-GUIDE.md` | include | K-dotnet-backend; resource `member:guides/DATABASE-MIGRATION-GUIDE.md`; README 直接入口；移除來源政策依賴；保留 migration owner 與目標選擇。E-T2 + E-READBACK。 |
| 11 | `.dev/guides/implementation-guides/DEVELOPMENT-TOOLS-GUIDE.md` | `src/knowledge/dotnet-backend/guides/DEVELOPMENT-TOOLS-GUIDE.md` | include | K-dotnet-backend; resource `member:guides/DEVELOPMENT-TOOLS-GUIDE.md`; README 直接入口；移除來源 Git topology／直接 main push；工具選擇由目標持有。E-T2 + E-READBACK。 |
| 12 | `.dev/guides/implementation-guides/DUAL-PROFILE-CONFIGURATION-GUIDE.md` | `src/knowledge/dotnet-backend/guides/DUAL-PROFILE-CONFIGURATION-GUIDE.md` | include | K-dotnet-backend; resource `member:guides/DUAL-PROFILE-CONFIGURATION-GUIDE.md`; README 直接入口；限定已選用 profile 模式。E-T2 + E-READBACK。 |
| 13 | `.dev/guides/implementation-guides/FAQ.md` | `src/knowledge/dotnet-backend/guides/FAQ.md` | include | K-dotnet-backend; resource `member:guides/FAQ.md`; README 直接入口；消除 ES、固定方法數與空白 spec 的普遍強制假設。E-T2 + E-READBACK。 |
| 14 | `.dev/guides/learning-guides/LEARNING-PATH.md` | `src/knowledge/dotnet-backend/guides/LEARNING-PATH.md` | include | K-dotnet-backend; resource `member:guides/LEARNING-PATH.md`; README 直接入口；重寫選用學習路徑；移除退休初始化與來源文件依賴。E-T2 + E-READBACK。 |
| 15 | `.dev/guides/learning-guides/NEW-PROJECT-GUIDE.md` | — | retire | R; 固定 tree 不存在；未列入 metadata／manifest；Git 歷史保留；舊初始化流程、ExampleApp 與 ai-context-init 假設不再適用。E-T2 + E-READBACK。 |
| 16 | `.dev/guides/implementation-guides/NEW-PROJECT-TEST-SETUP-GUIDE.md` | `src/knowledge/dotnet-backend/guides/NEW-PROJECT-TEST-SETUP-GUIDE.md` | include | K-dotnet-backend; resource `member:guides/NEW-PROJECT-TEST-SETUP-GUIDE.md`; README 直接入口；目標選用測試套件與 GWT；修正路徑。E-T2 + E-READBACK。 |
| 17 | `.dev/guides/implementation-guides/PERSISTENCE-CONFIGURATION-GUIDE.md` | `src/knowledge/dotnet-backend/guides/PERSISTENCE-CONFIGURATION-GUIDE.md` | include | K-dotnet-backend; resource `member:guides/PERSISTENCE-CONFIGURATION-GUIDE.md`; README 直接入口；保留各領域持久化決策，不全域統一 ORM。E-T2 + E-READBACK。 |
| 18 | `.dev/guides/implementation-guides/PREVENT-SERVICE-REGISTRATION-MISSING.md` | `src/knowledge/dotnet-backend/guides/PREVENT-SERVICE-REGISTRATION-MISSING.md` | include | K-dotnet-backend; resource `member:guides/PREVENT-SERVICE-REGISTRATION-MISSING.md`; README 直接入口；條件化工具與架構假設，修正相關路徑。E-T2 + E-READBACK。 |
| 19 | `.dev/guides/design-guides/PROFILE-BASED-TESTING-GUIDE.md` | `src/knowledge/dotnet-backend/guides/PROFILE-BASED-TESTING-GUIDE.md` | include | K-dotnet-backend; resource `member:guides/PROFILE-BASED-TESTING-GUIDE.md`; README 直接入口；修正 legacy guidance 路徑，保留目標採用條件。E-T2 + E-READBACK。 |
| 20 | `.dev/guides/design-guides/TEST-DATA-PREPARATION-GUIDE.md` | `src/knowledge/dotnet-backend/guides/TEST-DATA-PREPARATION-GUIDE.md` | include | K-dotnet-backend; resource `member:guides/TEST-DATA-PREPARATION-GUIDE.md`; README 直接入口；目標選用測試規則與資料來源；修正路徑。E-T2 + E-READBACK。 |
| 21 | `.dev/specs/tests/TEST-SPEC-GUIDE.MD` | `src/knowledge/dotnet-backend/guides/TEST-SPEC-GUIDE.MD` | include | K-dotnet-backend; resource `member:guides/TEST-SPEC-GUIDE.MD`; README 直接入口；GWT 依採用狀態適用；BDDfy／文件位置可選，不強制流水線。E-T2 + E-READBACK。 |
| 22 | `.dev/operations/CONTEXT-MAP-GUIDE.MD` | `src/knowledge/engineering-common/operations/CONTEXT-MAP-GUIDE.MD` | include | K-engineering-common; resource `member:operations/CONTEXT-MAP-GUIDE.MD`; README 直接入口；移至 common；具體 paths、template、provider、驗證契約依目標選擇。E-T2 + E-READBACK。 |
| 23 | `.dev/operations/EVENT-CATALOG-GUIDE.MD` | `src/knowledge/engineering-common/operations/EVENT-CATALOG-GUIDE.MD` | include | K-engineering-common; resource `member:operations/EVENT-CATALOG-GUIDE.MD`; README 直接入口；移至 common；具體 paths、template、provider、驗證契約依目標選擇。E-T2 + E-READBACK。 |
| 24 | `.dev/operations/MQ-TOPOLOGY-GUIDE.MD` | `src/knowledge/engineering-common/operations/MQ-TOPOLOGY-GUIDE.MD` | include | K-engineering-common; resource `member:operations/MQ-TOPOLOGY-GUIDE.MD`; README 直接入口；移至 common；具體 paths、template、provider、驗證契約依目標選擇。E-T2 + E-READBACK。 |
| 25 | `.dev/operations/RUNBOOK-GUIDE.MD` | `src/knowledge/engineering-common/operations/RUNBOOK-GUIDE.MD` | include | K-engineering-common; resource `member:operations/RUNBOOK-GUIDE.MD`; README 直接入口；移至 common；具體 paths、template、provider、驗證契約依目標選擇。E-T2 + E-READBACK。 |
| 26 | `.dev/requirement/DOMAIN-UBIQUITOUS-LANGUAGE-REQUIREMENTS.MD` | — | retire | R; 固定 tree 不存在；未列入 metadata／manifest；Git 歷史保留；來源專案歷史／狀態與 repo-structure-sync 命令；不作可攜領域語言規範。E-T2 + E-READBACK。 |
| 27 | `.dev/requirement/TECH-STACK-REQUIREMENTS.MD` | `src/knowledge/dotnet-backend/requirements/TECH-STACK-REQUIREMENTS.MD` | include | K-dotnet-backend; resource `member:requirements/TECH-STACK-REQUIREMENTS.MD`; README 直接入口；技術、配置 owner、messaging 與測試工具由目標證據選擇。E-T2 + E-READBACK。 |
| 28 | `.ai/assets/shared/ARTIFACT-DESIGN-REVIEW-CONTRACT.md` | `src/knowledge/engineering-common/references/ARTIFACT-DESIGN-REVIEW-CONTRACT.md` | include | K-engineering-common; resource `member:references/ARTIFACT-DESIGN-REVIEW-CONTRACT.md`; README 直接入口；移除強制新 packet／resolver gate；依目標 authority／contract。E-T2 + E-READBACK。 |
| 29 | `.ai/assets/shared/AUTHORING-BOUNDARY-CONTRACT.md` | `src/knowledge/engineering-common/references/AUTHORING-BOUNDARY-CONTRACT.md` | include | K-engineering-common; resource `member:references/AUTHORING-BOUNDARY-CONTRACT.md`; README 直接入口；保留既有 skill schema／role／採用規則 authority，不新增 packet gate。E-T2 + E-READBACK。 |
| 30 | `.ai/assets/shared/IMPLEMENTATION-SCOPE-ROUTING-CONTRACT.md` | `src/knowledge/engineering-common/references/IMPLEMENTATION-SCOPE-ROUTING-CONTRACT.md` | include | K-engineering-common; resource `member:references/IMPLEMENTATION-SCOPE-ROUTING-CONTRACT.md`; README 直接入口；改採目標選用協調路由，不依賴已退休 portable orchestrator。E-T2 + E-READBACK。 |
| 31 | `.dev/adr/WHEN-TO-CREATE-ADR.MD` | `src/skills/adr-author/references/WHEN-TO-CREATE-ADR.MD` | include | S-adr-author; references `references/WHEN-TO-CREATE-ADR.MD`; SKILL 直接入口；author ID 經父整合改名；檔案數不產生 ADR 強制要求，依 caller／目標流程。E-T2 + E-READBACK。 |
| 32 | `.dev/requirement/REQUIREMENT-GUIDE.MD` | `src/skills/requirement-author/references/requirement-guide.md` | consolidate | S-requirement-author; references `references/requirement-guide.md`; SKILL 直接入口；保留 guide 入口，重用既有 requirement-template，移除重複內嵌模板。E-T2 + E-READBACK。 |
| 33 | `.dev/specs/SPEC-GUIDE.MD` | `src/skills/spec-author/references/spec-guide.md` | consolidate | S-spec-author; references `references/spec-guide.md`; SKILL 直接入口；保留 guide，整併為既有 authoring/template 入口；移除固定來源 layout／欄位要求。E-T2 + E-READBACK。 |
| 34 | `.dev/specs/SPEC-ORGANIZATION-GUIDE.MD` | `src/skills/spec-author/references/spec-organization-guide.md` | consolidate | S-spec-author; references `references/spec-organization-guide.md`; SKILL 直接入口；保留組織指引；合併通用 placement 建議，依實際 responsibility，不複製來源 layout。E-T2 + E-READBACK。 |

## 中介路徑與整合改名

以下路徑在 T2 輸入 d9ddbc64 時仍位於 dotnet-backend，T2 重新分類到 common：

- `src/knowledge/dotnet-backend/domain-language/README.MD` → `src/knowledge/engineering-common/domain-language/README.MD`。
- `src/knowledge/dotnet-backend/domain-language/templates/aggregate-vocabulary-template.md` → `src/knowledge/engineering-common/domain-language/templates/aggregate-vocabulary-template.md`。
- `src/knowledge/dotnet-backend/domain-language/templates/bounded-context-language-template.md` → `src/knowledge/engineering-common/domain-language/templates/bounded-context-language-template.md`。
- `src/knowledge/dotnet-backend/domain-language/templates/domain-event-language-template.md` → `src/knowledge/engineering-common/domain-language/templates/domain-event-language-template.md`。
- `src/knowledge/dotnet-backend/operations/CONTEXT-MAP-GUIDE.MD` → `src/knowledge/engineering-common/operations/CONTEXT-MAP-GUIDE.MD`。
- `src/knowledge/dotnet-backend/operations/EVENT-CATALOG-GUIDE.MD` → `src/knowledge/engineering-common/operations/EVENT-CATALOG-GUIDE.MD`。
- `src/knowledge/dotnet-backend/operations/MQ-TOPOLOGY-GUIDE.MD` → `src/knowledge/engineering-common/operations/MQ-TOPOLOGY-GUIDE.MD`。
- `src/knowledge/dotnet-backend/operations/RUNBOOK-GUIDE.MD` → `src/knowledge/engineering-common/operations/RUNBOOK-GUIDE.MD`。
- `src/skills/adr/references/WHEN-TO-CREATE-ADR.MD` → `src/skills/adr-author/references/WHEN-TO-CREATE-ADR.MD`。

退休的兩份文件原本先搬到 `src/knowledge/dotnet-backend/guides/NEW-PROJECT-GUIDE.md`、`src/knowledge/dotnet-backend/requirements/DOMAIN-UBIQUITOUS-LANGUAGE-REQUIREMENTS.MD`，再由 T2 移除。這是 reviewed tracked history 的退休，不代表任何未 commit／untracked 資料可以靠 Git 還原。

## Compact metadata 與精確固定 bytes

- `src/knowledge/dotnet-backend/content-package.yaml`：**250,457 / 262,144 bytes**；246 members、245 resources、407 references；SHA-256 `816b4797bfdf9f23610f8234b4e5801f3ecc35ddd71dbde4edbe4820e079a0c8`。
- `src/knowledge/engineering-common/content-package.yaml`：**12,200 / 262,144 bytes**；17 members、16 resources、20 references；SHA-256 `63b74b16794affe7fd3f4a5bf4a96760d38411c6fcbbc17ce9c95e0cef3bc094`。

上限未修改。Compact YAML serialization 調整表示方式，T2 原有 member/resource/reference 物件及其他 metadata 值已做語意保持比較。增加 resources、member-kind（含 templates）、排序 reference edges 和頁內錨點宣告後，.NET 仍有 11,687 bytes 餘裕。大量 line churn 主要來自序列化；不是大量新規則或套件執行證據。

## 最前期的 18 項人類需求

最早已定位的直接 user 原文是 **2026-09-23 00:00:58.044 Asia/Taipei**（`2026-09-22T16:00:58.044Z`），session `01a0c9d9-3b00-7b70-ad85-daff590e7ecd`，檔案 `C:/Users/h4227/.codex/archived_sessions/rollout-2026-09-23T00-00-52-01a0c9d9-3b00-7b70-ad85-daff590e7ecd.jsonl`，**line 10**，role=user。本次只重新讀該精確已知行，沒有歷史廣掃。當時要求使用 workflow 或 assessment 保存分析，並明確授權該次分析跳脫來源 repo 強制規範；那是分析授權，不能推為所有後續寫入／發布授權。

`.dev/assessments/ASM-20260923-00-6oq/report.md` 的「對使用者 18 個方向的逐項回應」忠實對應該訊息。`0.19.0` 版本名在同 session 後來 line 7500、2026-09-23 21:24:45 Taiwan 才明確出現，因此「最初大重構需求」應引用這 18 項，而非把後續 RC2/RC3 加項當作最初承諾。

| 原 ID | 最初需求忠實摘要 | 與本次 RC3／T2 的關係及完成度限制 |
| --- | --- | --- |
| 1-1 | Skill 可攜、降低相依；workflow 是組織型 skill 核心，擁有規格工具及可設定位置、Git、壓縮期限 | 可攜 skill／閉包屬架構主軸；RC3 明確退休 portable workflow，故不能宣稱原 workflow 組織能力全數完成；這是後續採納的 scope 收斂。 |
| 1-2 | .dev 控制權交還專案；spec/requirement 等來源與輸出位置可改 | T2 把可重用內容放進 owning package 並消除固定來源 layout；target 自有政策與資料仍須保留。source/MQ 實際替換證據由 parent 納入。 |
| 1-3 | .ai 明確區分 framework 管理 core 與專案管理 custom | 與 current package／project ownership 分離直接相關；不能由文件存在推定實際 installation 完成。 |
| 1-4 | ADR、Lesson 撰寫與讀取標準化成 skill | RC3 author ID 命名保留 record family；T2 註冊 ADR 指引。不代表每次作業都必產生紀錄。 |
| 1-5 | PR 標準化並建立 skill | RC3 pr-author 改名與原 PR family 保留相關；provider 建立／push／merge 是另外的操作。 |
| 1-6 | Workflow 回顧問題與好做法，用 ADR/Lesson 落地 | 仍可由 project workflow 與各 record skill 配合；移除 portable orchestrator 後，不能稱完整 portable 自動回顧能力已交付。 |
| 1-7 | ADR/Lesson 能轉換成專案規範 | 與 standards-promotion／owner adoption 邊界相關；單次經驗不能直接變成全域 MUST。T2 不驗收其 runtime。 |
| 1-8 | Ai-context 系列重新評估必要性，應可選配 | 選配 catalog／subset 與 generic knowledge availability 是相關方向；source/MQ 全選試裝不等於所有下游必選。 |
| 1-9 | 每個維護的 schema 有 scripts/shell tools；換版有 migration，降低 token／錯誤 | 須按實際 schema family、操作契約與工具證據衡量；T2 metadata/links pass 不足以證明所有 schemas 都有完整工具／migration。 |
| 1-10 | 支持全刪全加、降低更新衝突／I/O；也可按文件差異更新並調整客製資料 | 本次 Git-backed breaking reinstall 直接處理此方向；保護／還原只限明確 tracked scope，實際 source/MQ 試裝與結果由 parent 證據決定。沒有 I/O 收益量測。 |
| 1-11 | Local file backlog 標準化並收攏成 skill | local-backlog 仍是選用能力；不重新啟動 owner 已刪的 target backlog scaffolds 或改變 Issue authority。 |
| 1-12 | 未來 CLI／相關工具依發展重評可行性 | 屬後續方向；API plan/apply 工具不是全部未來 CLI 目標的完成證明。 |
| 1-13 | Workflows/assessments 整理、壓縮、刪除；知識落地後減少紀錄成本，可用線上工作工具 | #416 移至 v0.20 online-workflow 規劃；RC3 不交付這一整體能力。手動保留／清理與完整 online provider 必須分開。 |
| 2-1 | 本 repo 自身套用設計，驗證 skill／組織能力並改善專案資料維護 | Source 隔離 dogfood trial 與此相關；T2 只有 source/static evidence，實際試裝不等於 target behavioral acceptance。 |
| 2-2 | 考慮 source 放 src，避免外部專案資料干擾；釐清與 dogfooding 衝突 | 現固定 source 的產品根目錄採 src；已安裝根目錄是 consumer，不能維持第二份人工 source。 |
| 2-3 | 參考 Matt Pocock skills 專案的維護／打包結構 | 是參考方向，沒有要求完整照抄；不能把參考網站或目錄相似性當驗收。 |
| 2-4 | 捨棄大量 I/O、歷史升級與干擾產品改進的自我測試 | Source U001/P7 的 retired／deferred checks 應如實列示；本次未跑全矩陣，亦沒有證明所有保留資料改寫邊界已通過。 |
| 2-5 | 大量 I/O 可設定路徑到 RAM disk，降低 SSD 消耗 | 本次 source/MQ trials 與外部輸出使用明確 F 路徑；未改全域 TEMP/TMP，也不能用 RAM-disk 結果宣稱真實 SSD durability 或效能收益。 |

這張表是原意與本次 scope 的分流，不是完整 18 項 acceptance ledger。尤其 1-1/1-6 的 portable workflow 承諾已改變、1-13 線上化另開版本、1-9 完整 schema tooling 與 2-4 成本／行為證據尚須獨立核對，不能以 32/34 文件數或「四項工作完成」換算原 18 項的百分之百。

後續採納的收斂：D01/D02 選擇 src source＋安裝自用＋選配；D03 停止歷史 multi-hop 承諾；D04 先 filesystem；D05 先 retention/compaction preview；D07/P7 tests、benchmark、CI 延後；P8 CLI/providers 依發展條件再定。這些不是最初 user 原文的新增義務，也不是都已實作完成。

## 本次人類已批准的四項具體 scope

以下按 coordinator accepted scope 整理；前一輪提出這四項後，人類以「好，進行這四項工作」批准。這是後續 execution scope，不改寫最早 18 項需求。

1. 移除 portable software-development-orchestrator/workflow v2；source 與 target 自有普通 workflows、歷史輸出及已採用政策保留。
2. adr/lesson/pr 改為 adr-author/lesson-author/pr-author，保留各自 record family。
3. 逐份處置 34 搬移文件，完成 include/consolidate/retire、metadata／manifest／links 閉合；本報告的 32 納入／2 退休就是這一項的 T2 證據。
4. 實作 Git-backed breaking reinstall，並在 source／MQ 的明確 F worktrees 實測。T2 不宣稱該實測 passed；parent 以實際 plan/apply/read-back、protected-byte preservation 與 failure outcomes 完成此項判定。

## #416 與 RC3 排除邊界

先前 live read-back 已定位 [#416](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/416)，標題「[v0.20.0] 規劃 workflow 線上化，減少本機狀態檔案與 Git 負擔」，當次 state=OPEN；建立時間 `2026-09-29T23:26:29Z`（Taiwan 2026-09-30 07:26:29）。本次不重新查 provider state，這是同一工作既有 read-back 證據。

Issue 明確排除在 RC3 外。Sites＋DB 是候選方向；state/event/claim/lease/fencing/idempotency/client/export/recovery 是規劃議題，不是已接受的唯一產品選型。該 Issue 沒有授權實作、部署、credentials、搬移或刪除既有狀態資料。Retention／compaction／cleanup／online storage 不應在 RC3 成品完成度中捏造為已交付，也不應把保留歷史資料或手動 cleanup 誤算成 online workflow 系統完成。

## 供 parent 整合的最終界線

這個 external report 只整理已完成 T2 和既有需求定位證據；沒有改 source／target tracked files、重跑 full matrix／CI、provider mutation、commit、tag、發布或主要 target adoption。parent 應把本表與其他三項 implementation、完整 catalog/subset build、source/MQ 實測的各自固定 subject／receipt 一起評估。Static availability、implementation、actual install、runtime/product acceptance 與 adoption 是不同完成維度。
