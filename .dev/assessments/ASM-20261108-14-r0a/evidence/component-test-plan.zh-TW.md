> Historical assessment evidence at `41e4ebb8e716355ac86c4b39a8846e7b6711c1aa`. Proposals and execution exclusions below describe the analysis stage, before the subsequent implementation decision. This is not a current test inventory or execution instruction.

# Issue #594：依元件用途重新規劃 .NET 測試

分析對象：`41e4ebb8e716355ac86c4b39a8846e7b6711c1aa`，`codex/2026-11-08-dotnet-test-boundaries`。本文件是 `local/framework-workflows/2026-11-08-issue-594-test-strategy` 的修訂規劃，取代前版「固定保留 7 個一般／4 個成品測試專案、知識範本另行分離」的建議。所有安排仍是提案；未實作、建置或執行測試。

使用者已明確選定：完整 solution 應涵蓋一般 .NET 開發所需的單元與整合測試；發佈成品的端到端驗證另行安排。一般案例目標在 10 秒內，只有確有必要的整合情境才接受 20～30 秒。未指定整套總秒數，不以漏跑案例、缺少 opt-in 旗標、提高 timeout 或刻意拆散連續主張來達標。

## 1. 先確定產品責任

| 元件 | 核心用途與軟體性質 | 自己需要證明的能力 | 不應承擔的測試責任 |
|---|---|---|---|
| RefactorTool | 具 C# 語意的命令列工作區修改工具；使用 Roslyn／MSBuild，提供 inspect、preview、apply | 載入正確工作區；Rename／Extract Interface 只改正確符號；計畫可檢查；輸入漂移、檔案鎖與部分寫入有正確結果 | 重測 Roslyn 所有語法／重構；把每個名稱或 JSON 錯誤都送進完整 SDK restore／publish |
| FormatTool | 包裝既有 SDK `dotnet format` 的選檔與結果控制工具；自己不實作 formatter | 指定路徑／工作目錄／SDK 正確；只處理支援範圍；check 不要求格式器寫入；apply／失敗反映真實 bytes；清理 consent 和錯誤不被誤報 clean | 重測所有 C# 排版、所有 EditorConfig 組合或全部 analyzer fixes |
| SnippetTool | 讀取目錄與參數，輸出供人或代理插入的 C# 文字片段 | 清單、搜尋、inspect、參數與 placeholder、文字與編碼、錯誤 envelope；shipped fragments 在宣稱的 C# 使用情境可編譯及運作 | IDE 插入、整個下游應用驗收、每片段各一次 dotnet restore／publish |
| dotnet new 範本 | 可安裝的內容：API 起始專案／方案、C# items、領域契約測試範例 | 範本可發現；命名／參數替換正確；產物結構、參考與編譯正確；宣稱可運作的 API 有代表性啟動／路由證據 | SDK 通用安裝器、解除安裝、help 文案、所有通用 collision 規則；把 WorkItem 範例當成下游正式業務規格 |
| Generation.Templates | 將上述內容包為 `AICF.Dotnet.Templates.nupkg` 的 SDK 打包專案 | 範本內容、metadata 與排除規則正確，實際包可安裝／生成 | 沒有獨立執行期業務邏輯；不因存在 csproj 就需要一套單元測試 |
| domain-contracts | 可生成的教學型測試專案；package-free 不依賴外部領域套件，CT-005 依賴指定外部 DLL | 示範的 replay／pending／confirmation／重建錯誤行為符合所述範例；範本可生成 | 不代表框架自帶一套生產 domain，也不代表驗證使用者的真實業務 |

產品來源：Refactor 的 [README](https://github.com/YuChia-Wei/ai-collaboration-framework/blob/41e4ebb8e716355ac86c4b39a8846e7b6711c1aa/src/tools/dotnet/refactoring/README.md)、Format 的 [README](https://github.com/YuChia-Wei/ai-collaboration-framework/blob/41e4ebb8e716355ac86c4b39a8846e7b6711c1aa/src/tools/dotnet/formatting/README.md)、Snippet 的 [README](https://github.com/YuChia-Wei/ai-collaboration-framework/blob/41e4ebb8e716355ac86c4b39a8846e7b6711c1aa/src/knowledge/dotnet-backend/tooling/generation/snippet-tool/README.md)、[generation 說明](https://github.com/YuChia-Wei/ai-collaboration-framework/blob/41e4ebb8e716355ac86c4b39a8846e7b6711c1aa/src/knowledge/dotnet-backend/tooling/generation/README.md)、[domain-contracts 說明](https://github.com/YuChia-Wei/ai-collaboration-framework/blob/41e4ebb8e716355ac86c4b39a8846e7b6711c1aa/src/knowledge/dotnet-backend/templates/domain-contracts/README.md)。

## 2. Generation.Templates 為什麼是單一專案

目前 csproj 的 `PackageType=Template`、`IncludeBuildOutput=false`、`IncludeContentInPack=true` 與 `Content Include="dotnet-new/**/*" PackagePath="content"` 表示：它是集合多個範本的打包入口，不是生成後的應用程式。`dotnet pack` 把範本來源及 `.template.config` 放入 NuGet 包。Microsoft 官方教學直接採用這種 csproj，並提供 `Microsoft.TemplateEngine.Authoring.Templates` 的 `templatepack` 產生打包專案。[官方打包教學](https://learn.microsoft.com/en-us/dotnet/core/tutorials/cli-templates-create-template-package)

使用者記得的 Visual Studio「Export Template」也正確：精靈把既有專案與 `.vstemplate` metadata 打成 ZIP。那是 Visual Studio 範本格式；SDK 範本以 `.template.config/template.json` 配置，可從目錄或 `.nupkg` 註冊。Visual Studio 的 Create a new project 也支援 SDK 的專案／方案範本；SDK item 範本仍由 CLI 使用。[Visual Studio Export Template](https://learn.microsoft.com/en-us/visualstudio/ide/how-to-create-project-templates) · [SDK 範本作者文件](https://learn.microsoft.com/en-us/dotnet/core/tools/templates)

兩種說法可以同時成立：**範本內容可以是可直接建置的普通專案，另外用一個 csproj 將多個範本打包。** 官方明確說明，來源可以保持一般可建置／執行／除錯的專案，只加 template.json；若作者自行插入不合法程式 token 才會失去直接建置能力。[官方範本來源結構](https://learn.microsoft.com/en-us/dotnet/core/tools/custom-templates#template-structure)

因此保留一個打包專案合理；目前 solution 只顯示它、沒有列入 miniapi 與 web-api 的五個普通專案，則是可改善的開發入口安排，不是 SDK 必然限制。

## 3. domain-contracts 應納入統一 dotnet new 內容

package-free 與 published-ct005 現在已各有 template.json，短名稱分別為 `aicf-domain-contract-tests`、`aicf-ct005-contract-tests`。它們不是尚待轉換的純文件；目前差異是交付來源：兩個範本在 knowledge content-package 的清單內，卻在 `Generation.Templates.csproj` 的 glob 外，所以安裝既有 generation nupkg 只得到五個範本。

建議以一份 canonical 範本來源提供七個 short names，讓兩個契約範本進入 generation 的打包／安裝入口；知識文件保留概念、使用與契約說明，並指向該入口。遷移須同時調整知識套件 member 清單、文件路徑、生成 CI 和交付說明，不能只移資料夾而留下失效依賴，也不複製兩份範本各自維護。

package-free 的 csproj.template 內容本身是普通 .NET 10 xUnit 專案，可以評估改為可直接載入的 csproj，以 sourceName 做生成後命名；加入主 solution 後六項示範測試能正常 Run All。它仍使用 xUnit／BDDfy 套件，package-free 指無外部 domain 套件，不是完全免 NuGet。

CT-005 是選用 .NET 8 範本，須呼叫者提供指定版本 DLL。納入範本套件不代表框架取得外部 DLL 或能在任何環境執行那三個範例；它可在 solution 的範本內容中完整呈現，但不能把未具備的依賴當成日常可建置測試專案。是否進一步讓外部範例加入日常可執行集合，需先有明確依賴供應方式。本案不新增自動下載或另造跳過機制。

## 4. Generation.Templates.IntegrationTests 現在測什麼，哪些必要

目前只有一個 Fact：`NativeTemplatesGenerateBuildAndServeBothApiShapesAndPreserveEdits`。它透過共同的 TemplateScenario 完成長串操作，並非只測範本 metadata：

| 目前操作 | 它能證明什麼 | 修訂建議 |
|---|---|---|
| 隔離 hive 註冊，檢查五個 IDs | 自家 template.json 可被引擎發現 | 保留必要 discovery；未來按統一內容改為七個 |
| help、namespace、dry-run | 參數呈現、命名替換、引擎預覽行為 | 保留自己的命名／參數；通用 help/dry-run 沒有特定回歸時移除 |
| 生成 class、interface、usecase，放進 consumer | 自家 item 產物不是只看起來像 C#，能共同編譯並使用 | 共用一次 consumer 編譯，保留代表性參數與使用 |
| miniapi 與四專案 webapi 生成、建置 | 不同起始型態的檔案、namespace、project references 能工作 | 各型態保留生成後 build；避免把同一來源 build 與產物 build 的目的混淆 |
| 兩個 Kestrel 程序與多次 HTTP 請求 | API 啟動、路由、DI 與示範 POST/GET 真正可用 | 每種型態保留一次必要的啟動與代表性 POST→Location GET；刪去沒有獨立產品承諾的邊界值矩陣 |
| customization marker、碰撞與解除安裝 | 修改後產物能用、重疊寫入時保留內容、引擎卸載 | 若只是 SDK 保證則移除通用旅程；有自家 rename/source modifier 的回歸才留下針對性案例 |

**官方確實有範本測試，但不是要求本專案保留這整條長旅程。** 一手證據如下：

| 官方來源 | 可核實的實作 | 對本案的判斷 |
|---|---|---|
| [.NET SDK TemplateVerifier 文件](https://github.com/dotnet/sdk/blob/f344df8e9372871a10f4e146cf802b520895801b/documentation/TemplateEngine/authoring-tools/Templates-Testing-Tooling.md) | 生成範本後比較檔案樹／內容，提供自訂檢查與選用命令結果驗證 | 應測自己的生成結果。現有少量明確斷言足夠時，無需另加 snapshot 套件 |
| [官方 templatepack 測試](https://github.com/dotnet/sdk/blob/f344df8e9372871a10f4e146cf802b520895801b/test/TemplateEngine/Microsoft.TemplateEngine.Authoring.Templates.IntegrationTests/AuthoringTemplatesTests.cs#L117-L165) | 預設與改名的 templatepack 產物快照 | 證實打包範本本身也測產物；不是只信 template.json 存在 |
| [SDK 安裝後生成 MSTest 專案](https://github.com/dotnet/sdk/blob/f344df8e9372871a10f4e146cf802b520895801b/test/dotnet-new.IntegrationTests/DotnetNewInstantiateTests.cs#L16-L102) | 隔離 hive、安裝套件、生成並查 TFM／套件參考 | 支持短的 installation→generation 證據；不要求每條路徑都啟動 API |
| [ASP.NET Core WebApiTemplateTest](https://github.com/dotnet/aspnetcore/blob/6394b4fd2454c365064a4132b9857e03e5564184/src/ProjectTemplates/test/Templates.Mvc.Tests/WebApiTemplateTest.cs#L214-L319) | 一部分案例生成、publish、build、啟動、HTTP；另一部分只檢查生成 .http 檔 | API starter 的可運作主張有實際上游 precedent；簡單產物主張可以只檢查產物 |

因此應保留**縮短後的範本整合測試能力**；是否仍使用獨立的 Generation.Templates.IntegrationTests 專案，取決於組織與測試相依，不是官方強制。沒有理由為範本增加另一套測試框架。

## 5. 其他工具的官方與社群做法

| 工具／主張 | 正式文件與真實上游測試 | 本專案的最小合理邊界 |
|---|---|---|
| Refactor 語意轉換 | [Microsoft Workspace API](https://learn.microsoft.com/en-us/dotnet/csharp/roslyn-sdk/work-with-workspace)；[Roslyn RenameEngineTests](https://github.com/dotnet/roslyn/blob/main/src/EditorFeatures/Test2/Rename/RenameEngineTests.vb#L9-L44) 以 inline projects/documents 呼叫真正 Renamer；[ExtractInterfaceTestState](https://github.com/dotnet/roslyn/blob/main/src/EditorFeatures/TestUtilities/ExtractInterface/ExtractInterfaceTestState.cs#L31-L53) 建立 EditorTestWorkspace；社群 [Roslynator RR0075](https://github.com/dotnet/roslynator/blob/main/src/Tests/Refactorings.Tests/RR0075MergeIfStatementsTests.cs) 以 before／after 驗證重構 | 真 Roslyn workspace、手寫預期語意／來源、必要的 consumer 編譯；不用每列 SDK restore 或 published exe |
| Refactor 的真實專案載入 | [Roslyn NetCoreTests](https://github.com/dotnet/roslyn/blob/main/src/Workspaces/MSBuild/Test/NetCoreTests.cs#L75-L145) 建專案、restore、OpenProjectAsync、查 compilation；[project references](https://github.com/dotnet/roslyn/blob/main/src/Workspaces/MSBuild/Test/NetCoreTests.cs#L278-L309) | imports、Compile graph、reference graph、design-time 差異仍需真 SDK。只查配置的情境走 inspect，不必再規劃 Rename |
| Format 命令參數與結果 | [官方 ProgramTests](https://github.com/dotnet/sdk/blob/main/test/dotnet-format.UnitTests/ProgramTests.cs#L14-L73) 直接驗證 parser 與 exit code | 既有 Rules／JSON／Program.Run 小測試；不必啟動 formatter |
| Format 工作區與外部 SDK | [官方 CodeFormatterTests](https://github.com/dotnet/sdk/blob/main/test/dotnet-format.UnitTests/CodeFormatterTests.cs#L711-L776) 用真 project/solution fixture 呼叫 FormatWorkspaceAsync；[CLI 整合基底](https://github.com/dotnet/sdk/blob/main/test/dotnet-format.IntegrationTests/FormatIntegrationTestBase.cs) 另外對實際 repo 執行 dotnet format，查 exit 與真正處理的 file count | 我們是 wrapper，必須有少量真 SDK 選檔／check/apply／consent 證據；無需照搬上游大型 repo 測試。上游專案名 UnitTests 也含工作區互動，不能用名字判定測試類型 |
| Snippet 文字生成與 C# 可用性 | [Microsoft 單元測試建議](https://learn.microsoft.com/en-us/dotnet/core/testing/unit-testing-best-practices) 的小輸入、獨立期望、Fact/Theory；[Microsoft analyzer/code-fix 教程](https://learn.microsoft.com/en-us/dotnet/csharp/roslyn-sdk/tutorials/how-to-write-csharp-analyzer-code-fix#build-unit-tests) 示範受控 C# 輸入與預期來源 | renderer 以精確文字驗證；catalog 用小型真檔案；所有 shipped fragments 共用一次 Roslyn consumer 編譯／執行。此為依產品特性推導，沒有查到一項「所有 snippet 工具必須如此」的官方規範 |

這些是可查證的建議與產品實作，不是適用所有 .NET 軟體的統一強制矩陣。上游 main 連結記錄本次讀到的做法，不代表它和本案 Roslyn 5.0.0 或指定 SDK 的相容性已測過。AAA／原生 Fact、Theory 是常見表達，沒有官方規範要求 BDDfy。現有 GWT／BDDfy 是本專案選擇；本分析不因此全面改寫它，也沒有把它當成已證實的效能瓶頸。

## 6. 成品驗證：保留交付證據，不固定保留四個測試專案

單元／一般整合測試通過不能證明 NuGet 收進正確檔案、AOT 入口能啟動，或 ZIP 解壓後仍有 BuildHost。這些是具體交付失敗模式；但只需要針對這些模式的少量自動檢查，不必把整套功能重跑。交付流程可以執行既有 script 或少量 E2E checks；獨立 xUnit 專案是安排方式，不是必要成果。

| 本案交付物 | 建議保留的短驗證 | 從成品測試移回日常或合併的部分 |
|---|---|---|
| Refactor Windows ZIP | 實際解壓；檢查 runtime notices／BuildHost；一個最小 Extract preview 證明 MSBuild、Roslyn、BuildHost 真能載入；需要交付寫入證據時在同 fixture apply，查 create／modify bytes | 完整 Rename／Extract 語意與 consumer dispatch 由現有語意／source apphost 案例承接；caller global.json、同版本不同 SDK root 屬 source SDK integration |
| Format Native AOT | 真正發佈 exe 完成代表性 JSON request 及選檔操作，證明 native 入口與外部 SDK 接線 | compact/verbose envelope、完整 whitespace 行為應進日常；APFS case alias 屬真平台整合，在支援 host 執行，不必只綁成品 |
| Snippet Native AOT＋catalog | 從另一 cwd 啟動成品並完成一項 catalog／render 操作，查正確結果 | FIFO 拒絕屬真 Linux 檔案類型整合；參數／catalog／render／consumer 無需在成品重跑 |
| Templates nupkg | 裝真正 nupkg，確認預期 short names 與一項代表性命名生成；既然仍承諾 extracted-directory 安裝，再保留短的目錄註冊／生成 | 完整 build／HTTP／碰撞不在兩個安裝途徑各跑一遍；詳細產物主張由 source template 測試承接 |

以下是實際產品的 publish／package 自動測試，已讀取固定版本原始碼：

| 產品 | 實際操作與斷言 | 證據的範圍 |
|---|---|---|
| Chocolatey CLI 2.5.1 | `Invoke-Tests.ps1` 解開建置產生的 chocolatey nupkg，載入包內模組、初始化測試安裝，再以 Invoke-Choco／Pester 執行；`Add single unauthenticated source` 真正新增 source，核對 exit、stdout 與 chocolatey.config | 工具自己的交付包。[測試入口](https://github.com/chocolatey/choco/blob/2.5.1/Invoke-Tests.ps1#L107-L177) · [實際命令與效果](https://github.com/chocolatey/choco/blob/2.5.1/tests/pester-tests/commands/choco-source.Tests.ps1#L11-L67) |
| .NET SDK v10.0.100 | `It_publishes_self_contained_apps_to_the_publish_folder_and_the_app_should_run` 執行指定 RID 的 self-contained publish，查 runtime/dependency 檔，再以 RunExeCommand 直接執行 publish folder 的 HelloWorld apphost，查 exit 與 Hello World 輸出 | SDK 所產生的應用輸出，並非 SDK 自己的安裝包。[固定版本測試](https://github.com/dotnet/sdk/blob/v10.0.100/test/Microsoft.NET.Publish.Tests/GivenThatWeWantToPublishAHelloWorldProject.cs#L67-L127) |

對本案最直接的推論是保留少量 post-extract／post-publish 操作：例如 Refactor preview 真正啟動 BuildHost，Snippet 從別的 cwd 找到相鄰 catalog。這些失敗在來源測試中不一定出現。兩個外部實例不建立「每個產品都必須成品測試」的普遍規則，也不決定我們的專案數、runner、測試矩陣或時間門檻。

## 7. 完整 solution 與速度要求

建議使用一個主要 `.slnx` 作日常入口，含全部內部生產工具、範本打包專案、一般測試，以及可以直接建置的範本來源專案。現有主方案已包含 3 個工具、1 個打包專案和 7 個測試專案；miniapi／webapi 的 5 個普通專案尚未列入。package-free 可在統一範本安排時改為普通測試專案並加入。CT-005 的外部依賴限制應明示，而不是透過空白專案或假成功填滿 solution。

完成成品案例的逐項轉移／縮減後，純交付 checks 由打包／發佈流程承擔，便沒有維持另一個日常 artifact solution 的必要。若實作時某些 checks 仍最適合用測試專案承載，必須清楚呈現它的 delivery 範圍，不把缺成品輸入造成的 failure／skip 混入一般 Run All。當前四個 artifact project 缺輸入即失敗的契約，在完成替代交付檢查之前不可先刪掉。

測試引擎會排程，但並不保證所有專案或同一 collection 全部平行。xUnit 的跨 collection 與跨 assembly 執行由不同設定／runner 控制；共享 Console／環境／MSBuild process-global registration 也可能需要序列。[xUnit parallelism](https://xunit.net/docs/running-tests-in-parallel) · [shared context](https://xunit.net/docs/shared-context)

因此效能改善順序是：

1. 刪除與主張無關的 restore、完整 preview、formatter 重複呼叫和通用 SDK 旅程。五個 Compile rows 保留真 SDK 評估，優先回到既有 Register→Require 路徑；先驗證實際 MSBuild assembly 與選定 SDK 一致，否則保留程序隔離。
2. 以獨立主張拆解過長 scenario，而不是只把大 Fact 拆成更多 Fact 來美化時長。Template 的 items／兩種 API 可分開呈現，共用不變的註冊準備；generator consent 的各 context 有獨立結果，可共用不可變 DLL，保留各自 workspace／marker。
3. 只共享真正不變的昂貴準備，避免每列重新建 generator 或 restore 相同依賴。來源、obj、plan、已 apply 檔案與可變範本 hive 不跨並行案例共用。
4. 確認隔離後才選有限並行；不新增通用測試排程器、不預設全面提高平行度。新增 source coverage 若來自既有 artifact 主張，先和普通案例對照合併，避免日常重複。
5. 同一 SDK／同一 build／單一 runner、無並行成品工作時量測。一般案例以 10 秒內為目標，必要整合 20～30 秒需寫出實際工作及不可再縮小的理由；超過 30 秒先調整或呈報瓶頸，不默認增加等待容忍。

保存 TRX 的 176 個結果列中：≤10 秒為 158 通過＋1 略過，>10～20 秒為 11 通過，>20～30 秒為 4 通過，>30 秒為 2 通過。這與 175 通過、1 略過一致；不把略過當快速通過。

| 秒數 | 現有案例 | 優先檢討的工作 |
|---:|---|---|
| 44.3953 | Format `StyleHonorsSeverityAndRecheckIsClean` | 四次 wrapper 呼叫；區分 severity 正反例、check/apply 的契約與多餘 fresh recheck |
| 38.2622 | Format `GeneratorExecutesOnlyAfterConsentInBothDesignTimeContexts` | 六次呼叫的獨立 context，共用不可變 generator 準備，拆清主張並保留 marker |
| 28.7150 | Refactor `SdkGeneratorOutputBlocksExtractionButUnrelatedOutputAllowsRename` | generator discovery、Extract 拒絕、Rename、build；保留接線並去掉重複準備 |
| 28.3306 | Format `AnalyzerAppliesRequestedFixWithoutStyleChanges` | check 與 apply 的不同來源寫入契約；真 SDK 保留，先減少額外 preparation |
| 26.0625 | Template `NativeTemplatesGenerateBuildAndServeBothApiShapesAndPreserveEdits` | 多型態生成、build、HTTP、通用 SDK 旅程；依前表縮短 |
| 23.0997 | Refactor `CanonicalReadOnlyInputDetectsRetargetAndAcceptsFreshPreview` | 舊計畫拒絕與新計畫捕捉是有意義序列，維持真實 retarget，減少不必要工作 |
| 18.0577 | Refactor `ExtractApplyRefusesOutputRaceOrForgedPlan`：forged-create | 保留 Apply 重新規劃與 create-kind，和既有語意案例合併準備而非刪除結果 |
| 17.1367 | Format `ResponsePrefixAndLinkedPathsRemainLiteral` | response prefix 與 linked selection 為不同輸入行為，縮小各 fixture |
| 17.0685 | Refactor `ReadOnlyConsumerRefusesBeforeAnySourceChange` | 可下移真 InputLocks／ReadOnly 前置檢查，保留 Apply wiring 見證 |
| 16.0326 | Refactor `StableImportAllowsPreviewButExplicitCompileExclusionRefuses` | 正向 import 與 exclusion witness；移除與五 policy rows 完全重複的完整路徑 |
| 15.1887 | Refactor `ExtractApplyRefusesOutputRaceOrForgedPlan`：output-race | preview 後出現檔案的獨特情境，不能用晚期 CreateNew race 取代 |
| 15.1413 | Refactor `ConditionalConfigurationAndImportedFrameworkAreReported` | 改為既有 inspect，省 Rename planning |
| 14.9643 | Refactor `ExternalSdkIntermediatesAreCapturedWithoutBeingEdited` | 保留真實 SDK 中介檔捕捉；no-write 主張需直接觀察相應 bytes |
| 14.9030 | Refactor `RenameApplyRefusesChangesSincePreview`：glob-member | 真實 fresh workspace membership；手寫 plan 不能取代 |
| 14.9016 | Format `SlnxAndEditorConfigGeneratedSelectionsAreUnreportedAndUnchanged` | 兩入口的選檔與 generated 語意，分清各自必要 loading |
| 14.3145 | Refactor `RenameApplyRefusesChangesSincePreview`：forged-edit | 保留 recompute 比較與 edit-kind，減少重複 setup |
| 10.2485 | Refactor `OtherProjectLowercaseCompileGlobCanAlsoIncludeTheOutput` | 真實發現第二個 project 的證據，保留完整 workspace |

來源：`F:/tmp/dotnet-test-boundaries-20261108/runall-capability/default-results/*.trx` 的唯讀重算。五個 Compile rules 每列約 7.5～8.1 秒雖未超過 10 秒，仍做了不必要工作；不能只因低於門檻就保留浪費。這些 run 與 artifact 工作重疊，且屬原 build，不是本輪穩定效能基準；以上僅供排定優先順序，不是本輪速度驗收或未來時間保證。第一版本來就執行 Refactor SDK；不可將變慢一概歸因於新增 SDK 測試。

## 8. 下一個實作計畫與完成條件

| 順序 | 具體工作 | 完成時須看見的結果 |
|---|---|---|
| 1 | 以本表取代固定 7／4 專案方案；逐項標定日常／交付／範例，整合七個範本與完整主 solution | 所有內部可建置專案有一個日常入口；無效佔位／外部依賴有真實說明；來源只有一份；不得以旗標藏起可執行測試 |
| 2 | 縮小 Compile、Workspace inspect、ReadOnly／preflight、Format 重複呼叫；修正 directory、glob、import input 等既知 oracle 問題 | 每個保留主張仍有正確拒絕碼／內容／no-write 觀察；真 SDK／OS 部分仍真實 |
| 3 | 縮短 Template 與 generator 長旅程，按獨立行為呈現結果；把必要 source 行為由 artifact 移入一般測試 | API 生成可用、不同 consent context 正確；完整 Run All 不需先 publish；不複製重複驗證 |
| 4 | 在既有交付流程保留上述最小成品 checks，移除被替代的冗長 artifact 測試承載 | 實際 ZIP／AOT／nupkg 的特有失敗仍可被抓到；不每次 Run All 重建成品 |
| 5 | 比例適當的變更測試後，做一次無其他重工作重疊的 solution Run All，分開 build／discovery／case durations | 一般案例目標≤10秒；例外整合20～30秒有明確理由；CLI 與 Rider 各自依實際觀察說明，不能互相冒稱 |

這是分析與規劃的交付，沒有藉此取得 source implementation、push、PR、merge、Issue closure 或 release 權限。後續驗證依實際 diff 選擇，不因換對話重跑歷史矩陣。已取消的 Rider 執行未重啟。

完整繁體中文清單在同 workflow 的 `test-inventory.zh-TW.md`，涵蓋 **117 方法／197 邏輯案例**；每個方法有真實路徑、案例數、實際行為與邊界。已用固定 HEAD 的測試宣告核對 117 列無漏項，並重新加總 130＋32＋24＋2＋9＝197；這修正先前 Format 方法數與漏列 CompilePolicy 的摘要錯誤。
