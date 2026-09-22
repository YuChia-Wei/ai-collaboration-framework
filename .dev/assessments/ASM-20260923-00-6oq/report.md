# Framework 未來方向評估

Assessment：`ASM-20260923-00-6oq`。觀察基線：`c2e7071335d02d9b8d40ab4dcaf437e690791741`。日期：2026-09-23，Asia/Taipei。

這份報告的完成代表分析交付；下面的選擇仍是提案，不是已採納的 framework 規範或實作授權。使用者授權本次跳脫 repo 強制流程；沒有使用 repo 現有 SKILL。沿用 assessment 的保存與追蹤形式，方法與報告結構自行設計。使用者的「ARD」依上下文解讀為 ADR。

後續正式開工的授權、CI 暫停、驗證延後與獨立對話安排，見 [execution-plan.md](execution-plan.md)。以下保留原始分析。

## 建議方向

建議採用「可獨立選用的 skill 套件 + 小型共通協定 + 專案自有設定與知識」，把目前較緊密的整套框架拆出清楚的所有權。workflow 成為組織型 skill 的能力；一般能力型 skill 可以單獨使用，不因產生一份文件就必須啟動完整 workflow。

產品原始碼放在 `src/`，本 repo 以安裝成品的方式使用自己的 framework。這兩件事可以同時成立。根目錄的 `.ai`、`.dev` 是這個開發專案的協作環境，`src/` 才是出貨來源；不能讓兩邊都變成人工維護的 framework 真相。

測試方向應先刪減不再需要的產品承諾與重複驗證，再優化留下的測試。若縮減目前明列的歷史版本升級路線與自動連跳承諾，就不應繼續付出對應完整矩陣的維護成本。仍會改寫專案資料的安裝／migration 工具，保留少量直接驗證不破壞資料的測試即可；不把「安全」擴張為每次改文件都重新測歷史。

## 閱讀順序

| 文件 | 用途 |
| --- | --- |
| [architecture.md](architecture.md) | 套件、依賴、目錄、設定、workflow、知識落地、schema 與更新設計 |
| [roadmap.md](roadmap.md) | 分階段工作包、相依關係、驗收、刪減順序及既有 Issue 對照 |
| [evidence.md](evidence.md) | 基線證據、外部參考、靜態測試盤點、限制與查證狀態 |
| [assessment.yaml](assessment.yaml) | 身分、範圍、例外及續作入口 |

## 基線觀察與推論

### F-01：skill 的包裝邊界尚未等於它的獨立使用邊界

目前發行元件以 software core、lifecycle core、技術 profile 等為單位；許多工具與可攜規則仍在全域 scripts 或 `.dev`。不能只把 skill 目錄搬到另一個 repo，就宣稱依賴閉包完整。應區分必要依賴、可選能力、runtime 要求與專案設定；產物只攜帶實際需要的內容。[E01、E02](evidence.md#repo-evidence)

### F-02：`.dev` 的所有權問題具有實際的發行耦合

目前 `.dev` 同時包含 framework 管理的標準、模板與專案輸出，而且其中多項被選入下游 package。只改文件描述不夠，還須改 package selection、工具路徑、模板來源與 wrapper 生成。建議將可重用規格／模板移入 owning skill，`.dev` 只保留專案選擇、專案規範與產出。[E02、E03](evidence.md#repo-evidence)

### F-03：workflow 已有部分 skill 所有權，但保存模式被固定

現有 policy 已承認 skill 擁有其流程與模板；限制主要在固定 `.dev/workflows/.../workflow.yaml` locator、Git-trackable 根目錄與禁止外部／ignored 儲存。因此這次不是完全推翻 workflow，而是把 discovery、位置、追蹤與保存期限變成明確設定。[E04](evidence.md#repo-evidence)

### F-04：知識落地已有概念，欠缺可攜的使用入口與完整閉環

現有 ADR 與 Lesson 文件已區分決策、經驗及有效規範，Lesson 也已有 promotion。值得保留；改進重點是把「查找 → 草擬 → 審查／採納 → 更新有效規範 → 標示取代／失效」做成可以單獨使用的能力，並支援專案自訂位置。[E07](evidence.md#repo-evidence)

### F-05：schema 工具化應沿用近期成果，但停止擴張成龐大通用編輯器

live read-back 顯示 #319、#320 已完成。現有 lifecycle registry 對應 33 個 explicit schemas 與 19 個 implicit contracts，細分為 95 個 artifact kinds，且區分 authorable、generated、historical、re-execute 等路線。下一步應把它們歸還 owning component，讓「有 schema 就有操作入口或明確不支援的處置」成為交付原則。schema 可以描述合法結構，不能自行產生使用者同意、執行事實或分析判斷。[E08](evidence.md#repo-evidence)、[Issue 證據](evidence.md#issue-snapshot)

### F-06：測試負擔存在結構性原因，但本次未量測實際成本

靜態 registry 有 85 個 checks，`fast` membership 56，其中 8 個標為 I/O；multi-hop upgrade 也在 fast 裡。這是快速路線仍包含複雜工具驗證的直接證據；不是「已測得執行多久／寫多少 SSD」的證據。建議先縮減功能承諾與測試選取，再針對留下的少量路線設定成本預算。[E09](evidence.md#repo-evidence)

### F-07：`src/` 與 dogfooding 不衝突，問題是來源及消費者未完全分開

現有 product-source contract 已預留未來 canonical product root。將原始碼與自己安裝的 framework 分離，反而可以真實觀察下游會遇到的設定、更新與紀錄維護問題。日常使用鎖定穩定成品；需要驗證候選技能時才明確切換到 development build。[E05](evidence.md#repo-evidence)

### F-08：整包替換、少寫檔與少衝突是三個不同目標

core/custom 物理分離能減少所有權衝突。整包重新複製通常增加寫入量；減少 I/O 要靠相同 digest 不重寫、按元件更新或 staging 後切換。migration note 說明語意差異，機器 manifest 決定檔案差異，migration script 轉換可識別的資料版本。三者不應互相代替。

## 對使用者 18 個方向的逐項回應

| 需求 | 評估及建議 | 設計／後續工作 |
| --- | --- | --- |
| 1-1 skill 可攜、低相依、workflow 歸組織型 skill | 支持。採宣告式依賴與選配 composition；workflow schema、模板及工具由 owning skill 維護；小型共通協定處理設定與定位。避免每個 skill 自造另一套框架。 | architecture A1、A3；W02、W04 |
| 1-2 `.dev` 交還專案，spec／requirement 路徑可改 | 支持。預設路徑僅為 seed；預設讀取與輸出位置都要能改，工具不可偷退回 `.dev`。 | A2、A3；W02、W03 |
| 1-3 `.ai` core／custom 分離 | 支持。`core` 表示 framework 所有權，不等於所有內容必裝；`custom` 由專案掌握，另分離可再生的 runtime state。 | A2；W03 |
| 1-4 ADR、Lesson 撰寫與讀取標準化成 skill | 支持。兩者各有語意與生命週期，查找／適用性篩選和撰寫同等重要；不要求每次工作必產生文件。 | A4；W05 |
| 1-5 PR 標準化成 skill | 支持。內容摘要、scope、驗證結果及更新流程共通，平台差異放 adapter；草稿、建立 PR、push、merge 保留不同操作。 | A5；W06 |
| 1-6 workflow 回顧並保留好做法 | 支持。workflow 結尾安排有界回顧；可回報沒有可保留的新知，不強迫產出 ADR／Lesson。 | A4；W04、W05 |
| 1-7 ADR／Lesson 轉成專案規範 | 支持，但需要明確採納與適用範圍。輸出具體規範 diff、影響與必要檢查；不能把單次經驗自動升為全域 MUST。 | A4；W05 |
| 1-8 ai-context 系列改選配 | 建議採用。消費型專案只需最小設定／安裝識別；審計、治理、修復、維護型升級協助做成 add-on；source 發版維護不下放。 | A1；W03 |
| 1-9 schema 配 scripts／shell tools 與 migration | 支持，以每個實際維護的 schema family 為界；可支援建立、讀取、驗證、受控更新、migration 或明確保留／重建路線。避免把所有 Markdown 也 schema 化。 | A6；W07 |
| 1-10 全刪全加／按差異更新與客製資料調整 | 支持可替換 core；I/O 目標採 digest delta。core 更新與 custom migration 分開，不刪客製資料；文字 migration note 不能當執行程式。 | A7；W09 |
| 1-11 local file backlog 收斂為 skill | 支持。它是 work-item provider 的一種，由 local-backlog skill 提供 CRUD／查詢／關聯；不重新啟用本 repo 已凍結的歷史 backlog。 | A5；W06 |
| 1-12 CLI 等工具依發展重評 | 支持延後 runtime 選型。先讓小工具介面穩定，再考慮整合為 CLI；不先完整重寫現有 validators。 | A6；W11 |
| 1-13 workflows／assessments 清理、壓縮、刪除與線上存取 | 支持。以知識提煉和證據保留需求判定可刪，保存期限可配置；線上 provider 為單一權威，local cache 不競爭寫入。 | A8；W08 |
| 2-1 repo 本身驗證技能與組織編排 | 支持。根目錄是 framework 的真實消費者，累積可用性資料；產品 source 與測試資料不能混入日常知識。 | A9；W03、W10 |
| 2-2 產品是否放 `src/`，是否與前項矛盾 | 建議放 `src/`，透過 build/install dogfood；不是在 `src/` 之外手修另一份 framework。初期維持單 repo 即可。 | A9；W03 |
| 2-3 參考 Matt Pocock 專案 | 借鏡產品技能、維護文件、dev/release 集合分離及小工具；不照搬 runtime 專用呼叫或 symlink installer。 | A10；W03 |
| 2-4 捨棄大量 I/O／升級測試 | 支持移除常態全矩陣、歷史 replay 與重複包裝驗證；是否移除全部 upgrade 測試取決於是否保留自動 upgrade 功能。留下的資料改寫功能只測有限邊界。 | roadmap 測試取捨；W01、W09 |
| 2-5 I/O 路徑可指向 RAM disk | 支持。設專用 disposable workspace；不更動全域 TEMP／TMP。需真實儲存語意的少量測試另設明確路徑並選跑，不以 RAM disk 結果宣稱 SSD durability。 | A3；W01 |

## 建議優先順序與待決事項

第一階段先完成兩件事：確認哪些舊升級／驗證承諾可以退休；用一個可攜 skill 走通「自訂路徑、專案設定、最小 workflow」的垂直範例。不要先全面搬檔、造通用 CLI 或把所有測試再優化一次。

| 決策 | 建議預設 | 採納前需確定的內容 |
| --- | --- | --- |
| D01 產品 source 與自用 | 單 repo，`src/` 出貨，根目錄消費鎖定成品 | 是否接受根目錄 core 為生成／安裝結果 |
| D02 下游最小內容 | 少量共通設定與識別；能力按需選配 | 第一批必選技能與可選套件清單 |
| D03 支援的更新範圍 | 新架構只承諾明列相鄰 schema edges；舊架構一次性轉換 | 舊版自動 upgrade 要退休到哪個範圍 |
| D04 工作紀錄預設 | 個人流程 ignored local；團隊續作改用共享持久 store 或 Git | 本 repo 選 Git 摘要 + provider 工作項，還是全 Git |
| D05 清理政策 | 先提供 preview/manual sweep；TTL 只是候選條件 | 要保留哪些證據、期間與誰可執行刪除 |
| D06 出貨形態 | 一份 manifest，產生單 skill、選配 bundle 與 runtime projection | 第一個正式支援的安裝方式；不一次支援所有平台 |
| D07 成本預算 | 快速檢查不含歷史／升級矩陣；大型 I/O 顯式選跑 | 實際可接受的本機／CI 時間及寫入量預算 |

這些決策不阻礙本次分析交付；它們是下一次採納與實作前的選擇。詳細工作順序、拆分與可觀察完成條件見 [roadmap.md](roadmap.md)。

## 完成與限制

本次只新增 assessment 成品與索引。沒有修改 framework、刪測試、建立正式 ADR／Lesson、建立或更新線上工作項，也沒有 commit、push、PR、merge 或發布。未執行大矩陣、升級測試或 benchmark。

對目前結構的事實以固定 Git 基線與 live Issue read-back 為準；外部參考保留 URL 與研究快照。測試 registry 的 counts 是靜態 membership，不是實際執行時間、token、SSD 寫入量或效能收益。方案的預期收益仍待小型垂直試作驗證。
