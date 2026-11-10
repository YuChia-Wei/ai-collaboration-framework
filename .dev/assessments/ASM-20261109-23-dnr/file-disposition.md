# dotnet 知識套件逐檔處置提案

Assessment: `ASM-20261109-23-dnr`。唯讀基準：`c641602a50ee17016ea1729897625aefe708af2a`。

以下 122 列完整對應目前 122 個追蹤檔案；這是待確認方案，尚未執行搬移、合併或刪除。
目前位置相對於 `src/knowledge/dotnet-backend/`，提案位置相對於 `src/knowledge/dotnet/`。

- **保留／搬移**：保留正文契約及明示適用條件，必要時修正導覽與相對路徑。
- **合併／拆分合併**：先保留表內列出的有用內容，與現行 canonical owner 對照，再撤除原檔；不是整檔無條件刪除。
- **刪除**：無需保留獨立正文的 wrapper 或過時示例，須先完成宣告、路由與使用者引用的處置。歷史仍可用固定 Git SHA 取得。
- 文件進入 `core` 或 `testing` 不代表目標已採用所有規範；現行有條件的規則不因分類而升格為通用規則。
- Worker／Console 此次不建空目錄，不把 reactor/outbox 等同 Worker 入口，不新增完整 consumer 知識。

舊 resource ID 對應規則及無等價替代的處置見 [相容性方案](compatibility.md)。舊規則衝突以 [評估報告](report.md) 的裁決界線處理，不藉合併選擇新的業務或架構政策。

| 目前檔案 | 提案動作 | 提案目的地 | 必須保留或完成的處置 |
| --- | --- | --- | --- |
| `content-package.yaml` | 保留／重建宣告 | `content-package.yaml` | 提案 package=dotnet；精確 members/resources/dependencies/references 隨核准清單重建，舊 ID 不暗中別名。 |
| `design/architecture-overview.md` | 搬移 | `architecture/ddd-cqrs/overview.md` | 保留 DDD/CA/CQRS、port/adapter 與持久化選擇；明示選用 profile。 |
| `design/architecture-playbook.md` | 合併 | `architecture/ddd-cqrs/overview.md`<br>`references/policy-rationale.md` | 保留 BC／invariant 設計檢核；MQ 與 named-broker 限制保留在原 profile，既有歧義仍列 unresolved。 |
| `design/design-routing.yaml` | 搬移 | `references/design-routing.yaml` | 保留可選 structured route，更新 architecture/test/messaging 目的地；不建立新 resolver。 |
| `design/source-map.md` | 合併 | `README.md` | 保留主題導航及 target-authority 說明；移除把 inert role YAML 當操作入口的導覽。 |
| `engineering-rule-catalog.yaml` | 保留／更新定位 | `engineering-rule-catalog.yaml` | 保留 11 個 rule ID、適用條件、錨點與來源歷史；只更新目前 owner path／抽取文字／digest；既有 profile ID 不全域替換。 |
| `guides/COMMON-MISTAKES-GUIDE.md` | 合併 | `references/troubleshooting.md` | 保留有辨識力的 namespace／DI／BDDfy／事件與時間診斷；重複規則改連到 owner。 |
| `guides/COMPLETE-ASPNET-CORE-SETUP-GUIDE.md` | 搬移 | `application-types/web-api/setup.md` | 保留實際 startup、HTTP 與所選 integration 驗證；不是完整 scaffold，設定插值需明確機制。 |
| `guides/CORS-SETUP.md` | 合併 | `application-types/web-api/setup.md` | 保留瀏覽器邊界、origin/headers/credentials、middleware 次序與正反 preflight 情境。 |
| `guides/DATA-CLASS-STANDARDS.md` | 合併 | `integration/persistence/mapper-standards.md` | 保留 schema coverage、version、metadata、必要狀態失敗；EF／Outbox／序列化形狀屬所選政策。 |
| `guides/DATABASE-MIGRATION-GUIDE.md` | 搬移 | `integration/persistence/database-migrations.md` | 保留所選 migration owner、SQL 審閱、驗證與 rollback；EF CLI 為選用範例。 |
| `guides/DEVELOPMENT-TOOLS-GUIDE.md` | 搬移 | `tooling/development-tools.md` | 保留 CLI／IDE／debug／diagnostics；Git、CI、套件與資料庫工具依目標選擇。 |
| `guides/DOCKER-RESTORE-CACHE-GUIDE.md` | 搬移 | `tooling/docker-restore-cache.md` | 保留容器 restore layer、遞迴 project/metadata closure 與後續 source copy。 |
| `guides/DOTNET-DI-TEST-GUIDE.md` | 合併 | `testing/profile-based-testing.md` | 保留 host/DI/fixture 與所選 port 替換；單元測試仍可直接建構，無強制框架 adapter。 |
| `guides/DUAL-PROFILE-CONFIGURATION-GUIDE.md` | 合併 | `core/host-configuration.md`<br>`integration/persistence/configuration.md`<br>`testing/profile-based-testing.md` | 保留 host selector、registration 與所選雙 profile smoke；大小寫及優先序依 canonical owner。 |
| `guides/FAQ.md` | 合併 | `architecture/ddd-cqrs/overview.md`<br>`testing/test-standards.md` | 保留 CQRS 與 ES 的區分、實際 adapter、repository 角色、controlled clock；刪除重複問答外殼。 |
| `guides/FRAMEWORK-API-INTEGRATION-GUIDE.md` | 搬移 | `integration/messaging/persistence-and-messaging.md` | 保留 in-memory/durable 組合、outbound port 與診斷；API 範例須依所選版本，TX／mapping owner 優先。 |
| `guides/GHERKIN-FEATURE-STORAGE-GUIDE.MD` | 搬移 | `testing/gherkin-feature-storage.md` | 保留學習範例、選用正式 spec、維護 feature 與 executable bindings 的區分。 |
| `guides/LEARNING-PATH.md` | 合併 | `README.md` | 縮為主題導覽與按需載入，移除 legacy 角色連結與重複規則。 |
| `guides/NEW-PROJECT-TEST-SETUP-GUIDE.md` | 合併 | `testing/profile-based-testing.md` | 保留 fixture／trait／filter／environment／事件擷取的有效內容；不預設 EF/Wolverine。 |
| `guides/PERSISTENCE-CONFIGURATION-GUIDE.md` | 搬移 | `integration/persistence/configuration.md` | 保留 infrastructure 持有 ORM/connection/migration、host composition；修正既有兩處失效相對連結。 |
| `guides/PREVENT-SERVICE-REGISTRATION-MISSING.md` | 合併 | `integration/persistence/configuration.md`<br>`references/troubleshooting.md` | 保留缺少 port/provider 的診斷鏈；排除與現行純 mapper 或 profile casing 衝突的範例。 |
| `guides/PROFILE-BASED-TESTING-GUIDE.md` | 搬移 | `testing/profile-based-testing.md` | 保留選用 provider 的隔離與證據；不由名稱推定實際資料庫。 |
| `guides/PROFILE-CONFIGURATION-COMPLEXITY-SOLUTION.md` | 合併 | `core/host-configuration.md`<br>`integration/persistence/configuration.md` | 保留 explicit modules、設定與註冊分工；合併衝突 selector/大小寫範例，無新增腳本。 |
| `guides/TEMPLATE-USAGE-GUIDE.md` | 合併 | `tooling/generation/README.md` | 以現行 template/snippet selector 為入口，保留設計前提、產碼歸目標及驗證責任。 |
| `guides/TEST-DATA-PREPARATION-GUIDE.md` | 合併 | `testing/profile-based-testing.md`<br>`testing/test-standards.md` | 保留區分情境的資料、獨立狀態與 setup events/reset；產品專屬路徑改明示示例。 |
| `guides/TEST-SPEC-GUIDE.MD` | 搬移 | `testing/test-spec-guide.md` | 保留選用正式 test spec、AC/GWT/assertion 對應與測試層級；不新增強制文件階段。 |
| `legacy-guidance/code-reviewer/roles/aggregate-code-review-sub-agent/references/review-playbook.md` | 合併 | `architecture/ddd-cqrs/aggregate-standards.md` | 保留 construction/transition/failure/replay 檢核；ES 僅明選，接受等價 target contract。 |
| `legacy-guidance/code-reviewer/roles/aggregate-code-review-sub-agent/references/review-prompt.md` | 刪除 | — | 重複 scoped/read-only/finding envelope；由 src/skills/code-reviewer/references/review.md 持有，無 knowledge alias。 |
| `legacy-guidance/code-reviewer/roles/aggregate-code-review-sub-agent/sub-agent.yaml` | 刪除 | — | 已停用的角色外殼；先保留對應技術 checklist，再撤除 member/resource/導航，不新增角色。 |
| `legacy-guidance/code-reviewer/roles/code-review-sub-agent/references/review-playbook.md` | 刪除 | — | 一般 authority/evidence/finding/read-only 方法已有 code-reviewer owner，沒有獨立 .NET 技術正文。 改由 src/skills/code-reviewer/references/review.md 承擔。 |
| `legacy-guidance/code-reviewer/roles/code-review-sub-agent/references/review-prompt.md` | 刪除 | — | 重複 scoped/read-only/finding envelope；由 src/skills/code-reviewer/references/review.md 持有，無 knowledge alias。 |
| `legacy-guidance/code-reviewer/roles/code-review-sub-agent/sub-agent.yaml` | 刪除 | — | 已停用的角色外殼；先保留對應技術 checklist，再撤除 member/resource/導航，不新增角色。 |
| `legacy-guidance/code-reviewer/roles/controller-code-review-sub-agent/references/review-playbook.md` | 合併 | `application-types/web-api/controller-standards.md` | 保留 access boundary、status/shape/errors、input/mapping 與已採架構 delegation。 |
| `legacy-guidance/code-reviewer/roles/controller-code-review-sub-agent/references/review-prompt.md` | 刪除 | — | 重複 scoped/read-only/finding envelope；由 src/skills/code-reviewer/references/review.md 持有，無 knowledge alias。 |
| `legacy-guidance/code-reviewer/roles/controller-code-review-sub-agent/sub-agent.yaml` | 刪除 | — | 已停用的角色外殼；先保留對應技術 checklist，再撤除 member/resource/導航，不新增角色。 |
| `legacy-guidance/code-reviewer/roles/reactor-code-review-sub-agent/references/review-playbook.md` | 合併 | `architecture/ddd-cqrs/reactor-standards.md` | 保留 event identity/registration、選用 ordering/retry、刻意傳播錯誤與 read-port 邊界。 |
| `legacy-guidance/code-reviewer/roles/reactor-code-review-sub-agent/references/review-prompt.md` | 刪除 | — | 重複 scoped/read-only/finding envelope；由 src/skills/code-reviewer/references/review.md 持有，無 knowledge alias。 |
| `legacy-guidance/code-reviewer/roles/reactor-code-review-sub-agent/sub-agent.yaml` | 刪除 | — | 已停用的角色外殼；先保留對應技術 checklist，再撤除 member/resource/導航，不新增角色。 |
| `legacy-guidance/slice-implementer/roles/aggregate-sub-agent/references/implementation-playbook.md` | 合併 | `architecture/ddd-cqrs/aggregate-standards.md`<br>`architecture/ddd-cqrs/building-blocks-reconstruction.md`<br>`core/design-by-contract.md` | 保留 immutable event/metadata/contract/VO；事件驅動狀態只限選用 ES，現行 ordinary aggregate/rehydration owner 優先。 |
| `legacy-guidance/slice-implementer/roles/aggregate-sub-agent/sub-agent.yaml` | 刪除 | — | 移除 inert role 外殼；技術差異先整合至對應 owner，歷史路徑不再當操作入口。 |
| `legacy-guidance/slice-implementer/roles/aggregate-test-sub-agent/references/test-generation-guidance.md` | 合併 | `testing/test-standards.md`<br>`architecture/ddd-cqrs/aggregate-standards.md` | 保留 aggregate fixture、invariants/postconditions、適用 event/serialization 與 scenario/row/assertion；移除歷史 bdd-gwt-test-designer 路徑。 |
| `legacy-guidance/slice-implementer/roles/aggregate-test-sub-agent/references/test-playbook.md` | 合併 | `testing/test-standards.md`<br>`architecture/ddd-cqrs/aggregate-standards.md` | 保留有區別的測試情境與前項契約；設計/實作交接由 test-designer 及 slice-implementer 擁有，不保留角色提示外殼。 |
| `legacy-guidance/slice-implementer/roles/aggregate-test-sub-agent/sub-agent.yaml` | 刪除 | — | 移除 inert role 外殼，條件式測試義務已併入對應技術 owner；不變更現行 test handoff。 |
| `legacy-guidance/slice-implementer/roles/command-sub-agent/references/implementation-playbook.md` | 合併 | `architecture/ddd-cqrs/usecase-standards.md` | 保留 transport-neutral I/O、scalar/no-input 例外、非 optional token、Task、真實 dispatch、所選 repository 邊界。 |
| `legacy-guidance/slice-implementer/roles/command-sub-agent/sub-agent.yaml` | 刪除 | — | 移除 inert role 外殼；技術差異先整合至對應 owner，歷史路徑不再當操作入口。 |
| `legacy-guidance/slice-implementer/roles/controller-sub-agent/references/implementation-guidance.md` | 合併 | `application-types/web-api/controller-standards.md` | 保留 thin HTTP/Use Case injection/DTO/token/status/pure-query；Task<ActionResult<T>> 保留為示例，不暗中取代現行其他合法簽名。 |
| `legacy-guidance/slice-implementer/roles/controller-test-sub-agent/references/test-generation-guidance.md` | 合併 | `testing/test-standards.md`<br>`application-types/web-api/controller-standards.md` | 保留 HTTP route/status/body/error、已選 WebApplicationFactory 整合層與 mock 選擇；DTO 與 source layout 留目標所有。 |
| `legacy-guidance/slice-implementer/roles/controller-test-sub-agent/references/test-playbook.md` | 合併 | `testing/test-standards.md`<br>`application-types/web-api/controller-standards.md` | 保留有區別的測試情境與前項契約；設計/實作交接由 test-designer 及 slice-implementer 擁有，不保留角色提示外殼。 |
| `legacy-guidance/slice-implementer/roles/controller-test-sub-agent/sub-agent.yaml` | 刪除 | — | 移除 inert role 外殼，條件式測試義務已併入對應技術 owner；不變更現行 test handoff。 |
| `legacy-guidance/slice-implementer/roles/outbox-sub-agent/references/implementation-playbook.md` | 合併 | `integration/messaging/transactional-messaging-standards.md`<br>`integration/persistence/configuration.md` | 保留 durable intent、audit metadata、所選 adapter/DI；不得弱化新版單一 completion-owner/atomicity 契約。 |
| `legacy-guidance/slice-implementer/roles/outbox-sub-agent/sub-agent.yaml` | 刪除 | — | 移除 inert role 外殼；技術差異先整合至對應 owner，歷史路徑不再當操作入口。 |
| `legacy-guidance/slice-implementer/roles/profile-config-sub-agent/references/implementation-playbook.md` | 合併 | `core/host-configuration.md`<br>`integration/persistence/configuration.md` | 保留 environment/appsettings/DI 與 fixture selection；禁測試類別修改全域環境，雙 profile 明選。 |
| `legacy-guidance/slice-implementer/roles/profile-config-sub-agent/sub-agent.yaml` | 刪除 | — | 移除 inert role 外殼；技術差異先整合至對應 owner，歷史路徑不再當操作入口。 |
| `legacy-guidance/slice-implementer/roles/query-sub-agent/references/implementation-playbook.md` | 合併 | `architecture/ddd-cqrs/usecase-standards.md`<br>`integration/persistence/projection-standards.md`<br>`integration/persistence/archive-standards.md`<br>`application-types/web-api/controller-standards.md` | 保留唯讀/transport-neutral/real dispatch/pure-query；Archive 依現行 lookup/save 契約；sentinel normalization 與 client navigation 僅為條件示例。 |
| `legacy-guidance/slice-implementer/roles/query-sub-agent/sub-agent.yaml` | 刪除 | — | 移除 inert role 外殼；技術差異先整合至對應 owner，歷史路徑不再當操作入口。 |
| `legacy-guidance/slice-implementer/roles/reactor-sub-agent/references/implementation-playbook.md` | 合併 | `architecture/ddd-cqrs/reactor-standards.md` | 保留 event-data 與 accepted read-port；依現行 owner 將 Wolverine 限於已選 adapter，分清別人 write store 與 read port。 |
| `legacy-guidance/slice-implementer/roles/reactor-sub-agent/sub-agent.yaml` | 刪除 | — | 移除 inert role 外殼；技術差異先整合至對應 owner，歷史路徑不再當操作入口。 |
| `legacy-guidance/slice-implementer/roles/usecase-test-sub-agent/references/test-generation-guidance.md` | 合併 | `testing/test-standards.md` | 保留 async event、單一主要動作、資料列/assertion mapping、獨立期待值與隔離；依現行 handoff 允許等價 Then 共用證據。 |
| `legacy-guidance/slice-implementer/roles/usecase-test-sub-agent/references/test-playbook.md` | 合併 | `testing/test-standards.md` | 保留有區別的測試情境與前項契約；設計/實作交接由 test-designer 及 slice-implementer 擁有，不保留角色提示外殼。 |
| `legacy-guidance/slice-implementer/roles/usecase-test-sub-agent/sub-agent.yaml` | 刪除 | — | 移除 inert role 外殼，條件式測試義務已併入對應技術 owner；不變更現行 test handoff。 |
| `legacy-guidance/spec-compliance-validator/references/spec-compliance-rules.md` | 保留／搬移 | `references/legacy-dotnet-compliance/spec-compliance-rules.md` | 保留 target-selected legacy 100% gate、CBF/SWF/FC/AC/Then、L1–L4 與 failure/remediation；不宣稱等價 modern validator。 |
| `legacy-guidance/spec-compliance-validator/references/test-validation-steps.md` | 保留／搬移 | `references/legacy-dotnet-compliance/test-validation-steps.md` | 保留 legacy checklist/例外/fixture 意義及 scenario/await mapping；只對已證明採用的相容舊目標載入。 |
| `legacy-guidance/spec-compliance-validator/references/validation-command-templates.md` | 保留／搬移 | `references/legacy-dotnet-compliance/validation-command-templates.md` | 保留 native .NET command 與 target-authority helper/report 範例；未恢復 helper 仍 unavailable，不自動選 route。 |
| `README.md` | 保留／重寫導覽 | `README.md` | 單一 progressive entry；區分共通、Web API、選用 DDD/CQRS 與 integration；保留 0.1.9 examples 遷移說明。 |
| `references/BUILDING-BLOCKS-CLASS-INDEX.MD` | 合併 | `architecture/ddd-cqrs/building-blocks-reconstruction.md` | 保留 portable interface、選用 ES base、target adapter lookup、snippet 導覽與產碼所有權。 |
| `references/CODE-TEMPLATES.MD` | 合併 | `tooling/generation/README.md` | 保留語意 owner 連結與產碼驗證界線，採唯一生成入口。 |
| `references/COMMON-PITFALLS.MD` | 合併 | `references/troubleshooting.md` | 保留 DI／mapping／BDDfy／同步與非同步 API 症狀；既有 factory 政策不藉此放寬。 |
| `references/ENGINEERING-IDENTITY-BINDINGS.MD` | 搬移 | `references/engineering-identity-bindings.md` | 保留穩定 identity、target binding 與 unresolved fail-closed；diagnostic/provider/config 不成規則 owner。 |
| `references/FAILURE-CASES.MD` | 合併 | `references/troubleshooting.md` | 保留有效失敗情境；不讓歷史 nested mapper、mutable metadata、必選 ES 範例覆蓋現行 owner。 |
| `references/rationale/generic-repository-only-rationale.MD` | 合併 | `references/policy-rationale.md` | 保留 compatibility、opt-in batch、purge 隔離理由；不複製規範正文。 |
| `references/rationale/profile-based-testing-rationale.MD` | 合併 | `testing/profile-based-testing.md` | 保留 profile/process 可見性、fixture ownership 與共用可變狀態風險理由。 |
| `references/rationale/query-side-layering-rationale.MD` | 合併 | `references/policy-rationale.md` | 保留無意義 pass-through、immutable read results、command reload/revalidation 理由。 |
| `references/rationale/rest-api-resource-path-rationale.MD` | 合併 | `application-types/web-api/controller-standards.md` | 保留 nested-create/flat-identity 的 ownership/lifecycle 理由，仍為可選慣例。 |
| `requirements/TECH-STACK-REQUIREMENTS.MD` | 拆分合併 | `core/technology-selection.md`<br>`architecture/ddd-cqrs/overview.md`<br>`integration/persistence/configuration.md`<br>`integration/messaging/persistence-and-messaging.md`<br>`testing/test-standards.md` | 共同層只持有實際 SDK/TFM/package/deployment 選擇；DDD、provider、test 及 Linux 預設留在原適用範圍。 |
| `review/review-routing.yaml` | 搬移 | `references/review-routing.yaml` | 保留 priority、finding gates 與 inert provenance；general-csharp 僅載 core；同步 skill 明確 allowlist。 |
| `review/test-scenario-review.md` | 搬移 | `testing/test-scenario-review.md` | 保留 GWT semantic probes、runner/row/result evidence、允許的精簡契約測試形式。 |
| `shared/architecture-config.md` | 合併 | `architecture/ddd-cqrs/overview.md`<br>`core/host-configuration.md`<br>`integration/messaging/persistence-and-messaging.md` | 消除第二規範 owner；.slnx、environment、persistence、Wolverine 連到其選用契約。 |
| `shared/common-rules.md` | 合併 | `README.md`<br>`core/csharp-conventions.md`<br>`integration/persistence/mapper-standards.md`<br>`application-types/web-api/controller-standards.md` | 只保留未重複且有現行 owner 支持的規約；不將 Java/ES/DTO 位置或 doc-comment 限制普遍化。 |
| `shared/domain-rules.md` | 合併 | `architecture/ddd-cqrs/aggregate-standards.md` | 保留 invariant/transition、VO equality、event intent/traceability；例外型別依目標契約。 |
| `shared/dto-conventions.md` | 合併 | `application-types/web-api/controller-standards.md` | 保留 request/response 分離、命名、validation 與 domain type 不外洩；固定資料夾是示例。 |
| `shared/testing-strategy.md` | 合併 | `testing/test-standards.md`<br>`testing/profile-based-testing.md`<br>`integration/messaging/transactional-messaging-standards.md` | 保留 GWT handoff、scenario/row/assertion、fixture 與 TX 證據；legacy 100% 義務移入明選參考。 |
| `standards/anti-patterns.md` | 合併 | `references/troubleshooting.md` | 保留有辨識力的 invariant/ES/N+1/use-case/scenario 失敗示例，規則正文回單一 owner。 |
| `standards/ASPNET-CORE-CONFIGURATION-CHECKLIST.md` | 合併 | `application-types/web-api/setup.md`<br>`integration/persistence/configuration.md` | 保留所選 API 啟動、設定、連線/schema/migration 檢核；messaging 分支須明選。 |
| `standards/best-practices.md` | 合併 | `references/troubleshooting.md`<br>`architecture/ddd-cqrs/overview.md`<br>`testing/test-standards.md` | 保留 controlled time、必要行為測試、cache/measurement 權衡；不成第二規範集。 |
| `standards/BUILDING-BLOCKS-RECONSTRUCTION-CONTRACT.md` | 搬移 | `architecture/ddd-cqrs/building-blocks-reconstruction.md` | 完整保留 AGGREGATE-ES-001、失敗 replay disposal、committed/pending version、confirm/failure 與 package-free/CT-005 界線。 |
| `standards/coding-guide.md` | 刪除 | — | 明示 legacy Todo/Wolverine 範例；有價值的規則已由現行 owner 持有，Git 固定來源保留歷史。 |
| `standards/coding-standards.md` | 拆分合併 | `core/csharp-conventions.md`<br>`README.md`<br>`architecture/ddd-cqrs/project-structure.md`<br>`testing/test-standards.md`<br>`integration/messaging/transactional-messaging-standards.md` | 分出共同 C# 與 profile 導覽；保留已採規約，先更新 route、metadata、shell checker 再移除原檔。 |
| `standards/coding-standards/aggregate-standards.md` | 搬移 | `architecture/ddd-cqrs/aggregate-standards.md` | 保留 DELETE-SOFT-001、invariants、Entity/VO/events、constructor、可選 ES、rehydration 與 UoW。 |
| `standards/coding-standards/archive-standards.md` | 搬移 | `integration/persistence/archive-standards.md` | 保留 DELETE-PURGE-001、lookup/save writer 與另行選定 purge/retention/audit；EF 條件不變。 |
| `standards/coding-standards/controller-standards.md` | 搬移 | `application-types/web-api/controller-standards.md` | 保留資源 URL、狀態/ProblemDetails、DTO/validation；Use Case 與 pure-query 條件仍依原 profile。 |
| `standards/coding-standards/mapper-standards.md` | 搬移 | `integration/persistence/mapper-standards.md` | 保留 MAP-EVENTS-001、static pure mapping、必要狀態 round-trip/visible failure、歷史相容及 version。 |
| `standards/coding-standards/profile-configuration-standards.md` | 拆分合併 | `core/host-configuration.md`<br>`integration/persistence/configuration.md`<br>`testing/profile-based-testing.md` | 完整保留 single host selector、override/case、composition 與 fixture ownership；雙 provider 僅在選用時載入。 |
| `standards/coding-standards/projection-standards.md` | 搬移 | `integration/persistence/projection-standards.md` | 保留 read port、ordered paging、command reload、projector writer/checkpoint/recovery 與非 exactly-once 界線。 |
| `standards/coding-standards/reactor-standards.md` | 搬移 | `architecture/ddd-cqrs/reactor-standards.md` | 保留 domain event/conversion/read-port/eventual consistency；TX/retry 連到 messaging；不新增 consumer scaffold。 |
| `standards/coding-standards/repository-standards.md` | 搬移 | `integration/persistence/repository-standards.md` | 保留 Aggregate identity/load/save、alias、read/batch/purge/writer 分工、atomic enrollment/pending ack/recovery。 |
| `standards/coding-standards/test-standards.md` | 搬移 | `testing/test-standards.md` | 完整保留 TEST-GWT/BDDFY/MOCK 三個 ID 與錨點、row/async、BDDfy opt-out、mock/profile 與測試層級。 |
| `standards/coding-standards/transactional-messaging-standards.md` | 搬移 | `integration/messaging/transactional-messaging-standards.md` | 完整保留 MESSAGING-TX-001、單一 physical commit/completion owner、receipt、idempotency/retry 與真實證據。 |
| `standards/coding-standards/usecase-standards.md` | 搬移 | `architecture/ddd-cqrs/usecase-standards.md` | 完整保留 ARCH-UOW-001、同 context/all-or-nothing 例外、typed I/O、token、actual dispatch 與 pending ack。 |
| `standards/contract-cases.md` | 搬移 | `testing/reconstruction-and-projector-cases.md` | 保留 required state／歷史相容／fallback／replay/ack 反例與 CT-005 版本邊界。 |
| `standards/DESIGN-BY-CONTRACT.md` | 搬移 | `core/design-by-contract.md` | 保留 CONTRACT-SEMANTICS-001、pre/post/invariant、選用 API 與證據；放 core 不代表自動採用契約政策。 |
| `standards/POLICY-RATIONALE.md` | 搬移 | `references/policy-rationale.md` | 保留來源版本/授權/commit URLs、interpretation、factory/broker unresolved 與 ArchPrecept 比較界線。 |
| `standards/project-structure.md` | 搬移 | `architecture/ddd-cqrs/project-structure.md` | 保留 PROJECT-GRAMMAR-001、條件式 .slnx/BC、logical/physical、Shared/BuildingBlocks；cross-BC 歧義明留。 |
| `standards/USECASE-COMMAND-HANDLER-RELATIONSHIP.MD` | 合併 | `architecture/ddd-cqrs/usecase-standards.md`<br>`application-types/web-api/controller-standards.md`<br>`references/policy-rationale.md` | 保留 call chain、輸入例外、async/token、thin dispatch、pure-query 例外與既有 cross-BC 限制，不偷偷改政策。 |
| `templates/application-properties-templates.md` | 合併 | `core/host-configuration.md`<br>`application-types/web-api/setup.md` | 保留最小 settings/override 例；固定 API path/ports/outbox key/插值皆不可成普遍假設。 |
| `templates/domain-contracts/README.md` | 搬移 | `testing/domain-contract-examples.md` | 保留兩個 template ID、TFM/版本、disposable hive、可選 CT-005 DLL/checksum 與行為界線。 |
| `templates/profile-isolated-configurations.md` | 合併 | `integration/persistence/configuration.md`<br>`core/host-configuration.md` | 保留選用 dual-profile 的明確 composition/fail-fast 範例；不用 dormant TODO 冒充 provider 能力。 |
| `tooling/generation/DELIVERY.md` | 保留 | `tooling/generation/DELIVERY.md` | 保留 Native AOT／formatting／安裝拒絕與恢復／獨立 generation bundle 契約；供 build-generation 複製，更新 source path。 |
| `tooling/generation/README.md` | 保留 | `tooling/generation/README.md` | 保留現行 generator/snippet selector；吸收重複 guide 的導覽與產碼所有權，不改 7 個 template IDs。 |
| `tooling/generation/snippet-tool/README.md` | 保留 | `tooling/generation/snippet-tool/README.md` | 保留 JSON 契約、catalog/parameters/render 與平台說明；供 csproj/bundle 引入，更新該引用。 |
| `tooling/on-demand-mechanical-validation/diagnostic-mapping.yaml` | 保留 | `tooling/on-demand-mechanical-validation/diagnostic-mapping.yaml` | 保留 DBA1001–DBA1017 labels/severity/binding-only；更新 semantic_sources，不宣稱 analyzer 已交付。 |
| `tooling/on-demand-mechanical-validation/provider-contract.schema.yaml` | 保留 | `tooling/on-demand-mechanical-validation/provider-contract.schema.yaml` | 保留 provider state/receipt schema；本次只查必要引用，沒有理由重做契約。 |
| `tooling/on-demand-mechanical-validation/provider-contract.yaml` | 保留 | `tooling/on-demand-mechanical-validation/provider-contract.yaml` | 保留 capability dotnet.mechanical-validation、unknown identity、recommendation 與 selection 分離；既有 profile token 不自動改。 |
| `tooling/on-demand-mechanical-validation/README.md` | 保留 | `tooling/on-demand-mechanical-validation/README.md` | 保留 reference-only/default-not-selected/無可執行 provider 與 target 選用責任。 |
| `tooling/on-demand-mechanical-validation/recipe-manifest.yaml` | 保留 | `tooling/on-demand-mechanical-validation/recipe-manifest.yaml` | 保留 recipe/material/source owner 與 unavailable 語義，更新受影響連結。 |
| `tooling/on-demand-mechanical-validation/recipes/analyzer-project.md` | 保留 | `tooling/on-demand-mechanical-validation/recipes/analyzer-project.md` | 保留 target-owned 起點與 SDK/Roslyn/version 自選，不擴充可編譯 analyzer。 |
| `tooling/on-demand-mechanical-validation/recipes/analyzer-severity.editorconfig.snippet` | 保留 | `tooling/on-demand-mechanical-validation/recipes/analyzer-severity.editorconfig.snippet` | 保留可編輯 severity baseline；不自動 wiring 或 warnings-as-errors。 |
| `tooling/on-demand-mechanical-validation/recipes/projection-registration-test.md` | 保留 | `tooling/on-demand-mechanical-validation/recipes/projection-registration-test.md` | 保留已選 EF/marker registration 的測試思路；無 framework runtime library。 |
| `tooling/on-demand-mechanical-validation/templates/code-fix-decision.md` | 保留 | `tooling/on-demand-mechanical-validation/templates/code-fix-decision.md` | 保留 decline/defer/implement 的 target 決定；不交付或啟用 fix。 |
| `tooling/on-demand-mechanical-validation/templates/minimal-diagnostic-analyzer-test.cs.template` | 保留 | `tooling/on-demand-mechanical-validation/templates/minimal-diagnostic-analyzer-test.cs.template` | 保留 unresolved harness 的 GWT 起點；不冒充已通過測試。 |
| `tooling/on-demand-mechanical-validation/templates/minimal-diagnostic-analyzer.cs.template` | 保留 | `tooling/on-demand-mechanical-validation/templates/minimal-diagnostic-analyzer.cs.template` | 保留無選定診斷行為的起點；無新 runtime/project。 |
| `tooling/on-demand-mechanical-validation/templates/provider-selection.template.yaml` | 保留 | `tooling/on-demand-mechanical-validation/templates/provider-selection.template.yaml` | 保留 not-selected、target-owned copy 及 evidence 狀態；不把更名當採用。 |
