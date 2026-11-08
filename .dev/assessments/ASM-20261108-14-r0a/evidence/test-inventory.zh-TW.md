> Historical assessment evidence at `41e4ebb8e716355ac86c4b39a8846e7b6711c1aa`. Proposals and execution exclusions below describe the analysis stage, before the subsequent implementation decision. This is not a current test inventory or execution instruction.

# .NET 測試清單：每個案例實際驗證什麼

清單依固定版本 `41e4ebb8e716355ac86c4b39a8846e7b6711c1aa` 的既有分析筆記整理，沒有重新掃描來源或執行測試。**117 個測試方法展開為 197 個邏輯案例**：一般測試 178 個、發佈成品測試 10 個、知識範本案例 9 個。這些是目前分類的邏輯數；Windows RunAll 的 TRX 記錄為 **175 通過、1 略過、0 失敗**。略過項是格式工具中只適用 POSIX 的檔名測試；macOS 上的三個 POSIX 資料列在 Windows TRX 中合併呈現為一個略過結果，因此不能直接把 TRX 列數當跨平台邏輯案例數。

表內的「測試邊界」描述測試實際走過哪一段程式與環境，方便理解它有沒有真的碰到 SDK、檔案、命令或發佈成品。它不是建議把所有測試改成同一種邊界。

## Refactor 工具

**3 個測試專案，72 個方法、130 個案例**：整合測試 64 方法／122 案例、單元測試 3／3、發佈成品測試 5／5。整合測試有 SDK 整合、程序內 Roslyn/MSBuild 與檔案系統測試；只有標示 SDK 的部分會啟動 SDK 子程序。

來源檔案根目錄：`tests/dotnet-refactoring/`。

### 整合測試：SDK 工作區與編譯項目

| 位置與方法 | 案例 | 測試實際驗證的行為 | 測試邊界 |
|---|---:|---|---|
| [CompileInclusionTests.cs:13](https://github.com/YuChia-Wei/ai-collaboration-framework/blob/41e4ebb8e716355ac86c4b39a8846e7b6711c1aa/tests/dotnet-refactoring/integration/CompileInclusionTests.cs#L13) `RejectsRulesThatCanExcludeOrImportTheNewFile` | 5 | 專案含有 `Compile Remove`、指向 `Fake.nuget.g.targets` 的匯入、`CustomBeforeMicrosoftCommonTargets` hook、`DirectoryBuildTargetsPath` hook，或 `_DirectoryBuildTargetsFile` 間接 hook 時，工具應拒絕預覽且不產生計畫或輸出。五種設定分別驗證不同 MSBuild 宣告方式。 | 真實 SDK 評估與完整預覽路徑；需確認新增檔案是否會被排除或移除。 |
| [CompileInclusionTests.cs:49](https://github.com/YuChia-Wei/ai-collaboration-framework/blob/41e4ebb8e716355ac86c4b39a8846e7b6711c1aa/tests/dotnet-refactoring/integration/CompileInclusionTests.cs#L49) `OtherProjectLowercaseCompileGlobCanAlsoIncludeTheOutput` | 1 | A 專案要新增的檔案若會被 B 專案的小寫 compile glob 納入，工具應拒絕，且不產生計畫或輸出。 | 真實 SDK 與多專案工作區；需由工作區找出第二個專案。 |
| [CompileInclusionTests.cs:84](https://github.com/YuChia-Wei/ai-collaboration-framework/blob/41e4ebb8e716355ac86c4b39a8846e7b6711c1aa/tests/dotnet-refactoring/integration/CompileInclusionTests.cs#L84) `StableImportAllowsPreviewButExplicitCompileExclusionRefuses` | 1 個方法、2 段操作 | 穩定的 `Bound.props` 匯入可成功預覽；明確排除目標檔的設定則應拒絕。成功分支還要確認匯入檔被列入計畫輸入，否則忽略該匯入也可能讓測試通過。 | 同一個已 restore 的專案執行真實 SDK 評估與預覽。 |

### 整合測試：原始 MSBuild XML 規則

| 位置與方法 | 案例 | 測試實際驗證的行為 | 測試邊界 |
|---|---:|---|---|
| [CompilePolicyTests.cs:21](https://github.com/YuChia-Wei/ai-collaboration-framework/blob/41e4ebb8e716355ac86c4b39a8846e7b6711c1aa/tests/dotnet-refactoring/integration/CompilePolicyTests.cs#L21) `RejectsFileDependentCustomProjectXml` | 7 | 手寫 XML 分別包含 Exists PropertyGroup、inactive Exists Import、Compile Remove 的 item expression、Compile condition 的 item expression、literal wildcard Import、property wildcard Import、custom BeforeTargets target 時，均回報 unsupported_compile_inclusion。 | 真實程序內 MSBuild ProjectRootElement 與 XML policy；沒有 SDK restore 或 hook discovery。 |

### 整合測試：專案發現與工作區

| 位置與方法 | 案例 | 測試實際驗證的行為 | 測試邊界 |
|---|---:|---|---|
| [WorkspaceIntegrationTests.cs:8](https://github.com/YuChia-Wei/ai-collaboration-framework/blob/41e4ebb8e716355ac86c4b39a8846e7b6711c1aa/tests/dotnet-refactoring/integration/WorkspaceIntegrationTests.cs#L8) `ExplicitFrameworkDoesNotAdmitMultiTargetProject` | 1 | 專案同時宣告 `net10.0` 與 `net9.0` 時，即使請求指定 `net10.0`，仍須拒絕多目標專案，不產生計畫。 | 真實 SDK 評估完整 target frameworks。 |
| [WorkspaceIntegrationTests.cs:27](https://github.com/YuChia-Wei/ai-collaboration-framework/blob/41e4ebb8e716355ac86c4b39a8846e7b6711c1aa/tests/dotnet-refactoring/integration/WorkspaceIntegrationTests.cs#L27) `ExplicitLinkedCompileItemIsRejected` | 1 | 以 MSBuild `Link` 將外部來源連入 Compile 項目的檔案應被拒絕，不產生計畫，來源檔維持原狀。 | 真實 SDK 工作區；驗證 Compile Link metadata。 |
| [WorkspaceIntegrationTests.cs:58](https://github.com/YuChia-Wei/ai-collaboration-framework/blob/41e4ebb8e716355ac86c4b39a8846e7b6711c1aa/tests/dotnet-refactoring/integration/WorkspaceIntegrationTests.cs#L58) `MissingProjectIsIdentifiedWhetherInSolutionOrReference` | 2 | 缺少專案分別是 `.slnx` 成員或 `ProjectReference` 時，都應指出 `Missing.csproj`。兩種入口各自驗證。 | 真實解決方案／專案參考發現；專案參考分支需 SDK item。 |
| [WorkspaceIntegrationTests.cs:100](https://github.com/YuChia-Wei/ai-collaboration-framework/blob/41e4ebb8e716355ac86c4b39a8846e7b6711c1aa/tests/dotnet-refactoring/integration/WorkspaceIntegrationTests.cs#L100) `MissingCompileInputIsIdentifiedBeforePlan` | 1 | Compile 清單包含不存在的 `Missing.cs` 時，應回報缺少輸入，且不產生計畫。 | 真實 SDK 評估後檢查檔案。 |
| [WorkspaceIntegrationTests.cs:132](https://github.com/YuChia-Wei/ai-collaboration-framework/blob/41e4ebb8e716355ac86c4b39a8846e7b6711c1aa/tests/dotnet-refactoring/integration/WorkspaceIntegrationTests.cs#L132) `AuthoredGeneratedSuffixCannotBeEditedThroughRelatedRename` | 1 | 使用者自行維護的 `Generated.g.cs` 不能透過相關重新命名操作被改寫；應回報拒絕並保持來源不變。 | SDK loader 到 planner 的完整生成檔判定路徑。 |
| [WorkspaceIntegrationTests.cs:165](https://github.com/YuChia-Wei/ai-collaboration-framework/blob/41e4ebb8e716355ac86c4b39a8846e7b6711c1aa/tests/dotnet-refactoring/integration/WorkspaceIntegrationTests.cs#L165) `ConditionalConfigurationAndImportedFrameworkAreReported` | 1 個方法、2 段評估 | `Directory.Build.props` 的 Debug 設定應包含 Debug define；Release 設定應呈現 net10.0 與 CUSTOM，且不含 DEBUG。 | 一次 restore、兩次真實 MSBuild 評估。 |
| [WorkspaceIntegrationTests.cs:213](https://github.com/YuChia-Wei/ai-collaboration-framework/blob/41e4ebb8e716355ac86c4b39a8846e7b6711c1aa/tests/dotnet-refactoring/integration/WorkspaceIntegrationTests.cs#L213) `ExternalSdkIntermediatesAreCapturedWithoutBeingEdited` | 1 | 外部 `AssemblyAttributes.cs` 應列為輸入，重新命名後唯一 edit 是使用者來源，Apply 成功。若要主張中介檔在 Apply 後仍未改變，必須直接觀察其 bytes。 | SDK 產生的中介檔與工作區；單靠來源檔 snapshot 不能證明中介檔未被改寫。 |
| [WorkspaceIntegrationTests.cs:252](https://github.com/YuChia-Wei/ai-collaboration-framework/blob/41e4ebb8e716355ac86c4b39a8846e7b6711c1aa/tests/dotnet-refactoring/integration/WorkspaceIntegrationTests.cs#L252) `BinAncestorOutsideProjectDoesNotMarkAuthoredSourceGenerated` | 1 | 專案外的 `bin` 路徑祖先不能讓使用者維護的 `Service.cs` 被誤判成 generated；應只修改正確檔案。 | SDK loader 的相對路徑判定。 |
| [WorkspaceIntegrationTests.cs:281](https://github.com/YuChia-Wei/ai-collaboration-framework/blob/41e4ebb8e716355ac86c4b39a8846e7b6711c1aa/tests/dotnet-refactoring/integration/WorkspaceIntegrationTests.cs#L281) `VisualBasicSolutionMemberIsRejected` | 1 | 解決方案包含 `.vbproj` 成員時，應回報不支援的專案且不產生計畫。 | 檔案系統與解決方案發現；不需 SDK restore。 |
| [WorkspaceIntegrationTests.cs:306](https://github.com/YuChia-Wei/ai-collaboration-framework/blob/41e4ebb8e716355ac86c4b39a8846e7b6711c1aa/tests/dotnet-refactoring/integration/WorkspaceIntegrationTests.cs#L306) `ClassicSolutionFolderAndProjectEntryKeepCompilationGraph` | 2 | 經由 `.sln` 專案入口及 solution-folder 入口發現 A/B 專案時，都應建立預期的 A/B 編譯關係並更新 consumer。 | 真實 SDK 工作區；兩種解決方案入口分開驗證。 |
| [WorkspaceIntegrationTests.cs:348](https://github.com/YuChia-Wei/ai-collaboration-framework/blob/41e4ebb8e716355ac86c4b39a8846e7b6711c1aa/tests/dotnet-refactoring/integration/WorkspaceIntegrationTests.cs#L348) `DesignTimeOnlySourceCannotSilentlyChangeTheEditableGraph` | 2 | 設計階段才出現的 `../Shared.cs` 應判為 linked file；額外的 `Extra.cs` 應判為非預期來源。兩者都不得產生計畫。 | 真實 SDK 對照一般建置與 design-time 編譯來源。 |
| [WorkspaceIntegrationTests.cs:381](https://github.com/YuChia-Wei/ai-collaboration-framework/blob/41e4ebb8e716355ac86c4b39a8846e7b6711c1aa/tests/dotnet-refactoring/integration/WorkspaceIntegrationTests.cs#L381) `DesignTimeAndBuildOnlyReferencesHaveDifferentMeaning` | 2 | 僅在一般建置出現的參考應回報 references 不完整；`ReferenceOutputAssembly=false` 的參考則可成功，但不應出現在編譯參考中。 | 真實 SDK 編譯圖；兩個相反結果都要成立。 |
| [WorkspaceIntegrationTests.cs:420](https://github.com/YuChia-Wei/ai-collaboration-framework/blob/41e4ebb8e716355ac86c4b39a8846e7b6711c1aa/tests/dotnet-refactoring/integration/WorkspaceIntegrationTests.cs#L420) `PreviewJsonReportsBaselineErrorsSeparatelyFromNewErrors` | 1 | `Broken.cs` 已有的 CS0246 與已知路徑應歸在 baseline error；預覽不可將它算成新錯誤。 | SDK 工作區與跨專案 CLI JSON；同時確認 wire 格式。 |

### 整合測試：Apply、前置檢查與輸入

| 位置與方法 | 案例 | 測試實際驗證的行為 | 測試邊界 |
|---|---:|---|---|
| [ApplyIntegrationTests.cs:11](https://github.com/YuChia-Wei/ai-collaboration-framework/blob/41e4ebb8e716355ac86c4b39a8846e7b6711c1aa/tests/dotnet-refactoring/integration/ApplyIntegrationTests.cs#L11) `RenameApplyRefusesChangesSincePreview` | 3 | 預覽後 consumer bytes 改變時回報輸入漂移；新增 glob 成員時回報計畫漂移；偽造 edit 也回報計畫漂移。各列驗證不同漂移來源，並確認檔案保留漂移後狀態。 | SDK 預覽、修改工作區、重新 Apply 的完整流程。 |
| [ApplyIntegrationTests.cs:45](https://github.com/YuChia-Wei/ai-collaboration-framework/blob/41e4ebb8e716355ac86c4b39a8846e7b6711c1aa/tests/dotnet-refactoring/integration/ApplyIntegrationTests.cs#L45) `ExtractApplyRefusesOutputRaceOrForgedPlan` | 2 | 預覽後輸出路徑被搶先建立時回報無效輸出並保留競爭者內容；偽造 create 則回報計畫漂移且不建立輸出。 | 真實工作區與 Apply；預覽後的新檔由工作區重新發現。 |
| [ApplyIntegrationTests.cs:77](https://github.com/YuChia-Wei/ai-collaboration-framework/blob/41e4ebb8e716355ac86c4b39a8846e7b6711c1aa/tests/dotnet-refactoring/integration/ApplyIntegrationTests.cs#L77) `ReadOnlyConsumerRefusesBeforeAnySourceChange` | 1 | consumer 設為 Windows ReadOnly 後，Apply 應拒絕且來源不變。單看 exit code 或「沒有寫入」不足以證明拒絕原因正確。 | Windows ReadOnly 檔案系統與完整 Apply 路徑。 |
| [ApplyIntegrationTests.cs:116](https://github.com/YuChia-Wei/ai-collaboration-framework/blob/41e4ebb8e716355ac86c4b39a8846e7b6711c1aa/tests/dotnet-refactoring/integration/ApplyIntegrationTests.cs#L116) `CanonicalReadOnlyInputDetectsRetargetAndAcceptsFreshPreview` | 1 | junction 內容相同但 physical root 改變時，舊計畫應回報輸入漂移；新預覽應擷取新 root 並可 Apply。 | SDK AdditionalFiles、junction 與新舊輸入擷取。 |
| [ApplyIntegrationTests.cs:170](https://github.com/YuChia-Wei/ai-collaboration-framework/blob/41e4ebb8e716355ac86c4b39a8846e7b6711c1aa/tests/dotnet-refactoring/integration/ApplyIntegrationTests.cs#L170) `EditableCompileSourceJunctionIsRefused` | 1 | SDK 確實把 junction 列為 editable Compile 時，應回報 linked path 並拒絕，不產生計畫。 | SDK 到 editable source 的完整接線。 |
| [ApplyIntegrationTests.cs:200](https://github.com/YuChia-Wei/ai-collaboration-framework/blob/41e4ebb8e716355ac86c4b39a8846e7b6711c1aa/tests/dotnet-refactoring/integration/ApplyIntegrationTests.cs#L200) `PreviewPlanCannotEnterLoadedProjectDirectory` | 1 | 計畫目標放在 B 專案目錄內時，應回報不安全路徑且不寫入計畫。 | 多專案工作區與計畫路徑保護。 |
| [PreflightTests.cs:10](https://github.com/YuChia-Wei/ai-collaboration-framework/blob/41e4ebb8e716355ac86c4b39a8846e7b6711c1aa/tests/dotnet-refactoring/integration/PreflightTests.cs#L10) `ExtractionApplyRefusesSourceDriftBeforeRecomputing` | 1 | 依手寫計畫與 SHA-256 驗證 source drift；回報輸入漂移，不建立 recovery 或輸出，並保持計畫、專案與來源不變。 | 真實檔案系統與命令入口；不需 SDK。 |
| [PreflightTests.cs:43](https://github.com/YuChia-Wei/ai-collaboration-framework/blob/41e4ebb8e716355ac86c4b39a8846e7b6711c1aa/tests/dotnet-refactoring/integration/PreflightTests.cs#L43) `ExclusiveSourceOrProjectHandleRefusesBeforeWrites` | 2 | 真正鎖住 source 或 project 時都應在寫入前回報 Apply 前置檢查失敗，並保留資料與計畫。 | Windows 檔案分享鎖；兩個鎖定目標分別驗證。 |
| [PreflightTests.cs:65](https://github.com/YuChia-Wei/ai-collaboration-framework/blob/41e4ebb8e716355ac86c4b39a8846e7b6711c1aa/tests/dotnet-refactoring/integration/PreflightTests.cs#L65) `MissingCanonicalAdditionalFileRefusesBeforeWrites` | 1 | 已記錄的 physical input 被刪除後，Apply 應失敗，不應重建 alias 或 physical file。 | 真實檔案與 junction；SDK 發現由另一測試覆蓋。 |
| [PreflightTests.cs:99](https://github.com/YuChia-Wei/ai-collaboration-framework/blob/41e4ebb8e716355ac86c4b39a8846e7b6711c1aa/tests/dotnet-refactoring/integration/PreflightTests.cs#L99) `PlanDestinationJunctionIsRefusedBeforeLoadingTheRequest` | 1 | 計畫目的地是 junction 時，應先回報 linked path；alias 與目標都不應建立，即使 request 本身故意不存在。 | 真實檔案系統與命令檢查順序。 |
| [CommandInputTests.cs:16](https://github.com/YuChia-Wei/ai-collaboration-framework/blob/41e4ebb8e716355ac86c4b39a8846e7b6711c1aa/tests/dotnet-refactoring/integration/CommandInputTests.cs#L16) `InvalidRequestDoesNotWritePlan` | 10 | 分別輸入缺欄位、格式錯誤、null、空物件、workspace 為 null、未知欄位、重複欄位、只有 workspace、Extract 空 members、Extract renameOverloads 等無效 JSON；都應回報無效輸入、不寫計畫且不改來源。 | 真實 JSON、檔案系統與命令入口。 |
| [CommandInputTests.cs:49](https://github.com/YuChia-Wei/ai-collaboration-framework/blob/41e4ebb8e716355ac86c4b39a8846e7b6711c1aa/tests/dotnet-refactoring/integration/CommandInputTests.cs#L49) `RequestDirectoryIsNotAJsonFile` | 2 | inspect 或 preview 把目錄當 request JSON 讀取時，都應回報無效輸入且不寫計畫。 | 真實檔案類型與兩個命令入口。 |
| [CommandInputTests.cs:80](https://github.com/YuChia-Wei/ai-collaboration-framework/blob/41e4ebb8e716355ac86c4b39a8846e7b6711c1aa/tests/dotnet-refactoring/integration/CommandInputTests.cs#L80) `InvalidPlanIsRefused` | 3 | 缺少計畫、`inputs:[null]`、`inputs:[{path:x}]` 三種格式錯誤都應回報無效輸入且不寫檔。 | Apply 命令與真實 JSON。 |
| [CommandInputTests.cs:106](https://github.com/YuChia-Wei/ai-collaboration-framework/blob/41e4ebb8e716355ac86c4b39a8846e7b6711c1aa/tests/dotnet-refactoring/integration/CommandInputTests.cs#L106) `SourceAndSdkConfigurationNamesAreRefusedBeforePreview` | 2 | `.cs` 來源檔或既有 `global.json` 被指定為計畫目的地時，應回報不安全路徑並保留原 bytes。 | 命令入口與檔案系統；兩種受保護檔案分開驗證。 |
| [EngineBoundaryTests.cs:10](https://github.com/YuChia-Wei/ai-collaboration-framework/blob/41e4ebb8e716355ac86c4b39a8846e7b6711c1aa/tests/dotnet-refactoring/integration/EngineBoundaryTests.cs#L10) `ConfigurationCannotInjectAnMsbuildProperty` | 1 | `Debug,DefineConstants=OTHER` 不能注入 MSBuild 屬性；應回報無效設定且 project 文字不變。 | SDK discovery 之前的檔案系統檢查。 |
| [EngineBoundaryTests.cs:36](https://github.com/YuChia-Wei/ai-collaboration-framework/blob/41e4ebb8e716355ac86c4b39a8846e7b6711c1aa/tests/dotnet-refactoring/integration/EngineBoundaryTests.cs#L36) `MalformedSourceEncodingIsRefusedWithoutWrites` | 1 | 含 BOM 與非法位元組 `0xff` 的來源應回報 lossy encoding，且保留原始 bytes。 | Roslyn 與真實來源 bytes。 |
| [EngineBoundaryTests.cs:62](https://github.com/YuChia-Wei/ai-collaboration-framework/blob/41e4ebb8e716355ac86c4b39a8846e7b6711c1aa/tests/dotnet-refactoring/integration/EngineBoundaryTests.cs#L62) `ExtractionRefusesCompatibleGeneratorOutputOrFailure` | 3 | generator 在 emit 後產生輸出、emit 後拋錯、emit 前拋錯三種情形都應拒絕 Extract；確認相應生成來源／編譯診斷，且來源不變、沒有輸出。 | 真實 analyzer DLL、Roslyn `GeneratorDriver` 與編譯流程。三個列分別檢查不同發生階段。 |

### 整合測試：重新命名與 Extract Interface

| 位置與方法 | 案例 | 測試實際驗證的行為 | 測試邊界 |
|---|---:|---|---|
| [RenameTests.cs:9](https://github.com/YuChia-Wei/ai-collaboration-framework/blob/41e4ebb8e716355ac86c4b39a8846e7b6711c1aa/tests/dotnet-refactoring/integration/RenameTests.cs#L9) `OverloadGroupRequiresOptInAndUpdatesNameof` | 1 | 未啟用 opt-in 時，模糊 `nameof` 應拒絕且 bytes 不變；啟用後應更新 overload 名稱與 `nameof`。 | Roslyn 工作區與局部檔案系統；不用 SDK restore。 |
| [RenameTests.cs:55](https://github.com/YuChia-Wei/ai-collaboration-framework/blob/41e4ebb8e716355ac86c4b39a8846e7b6711c1aa/tests/dotnet-refactoring/integration/RenameTests.cs#L55) `OptInDoesNotPullInOverloadsFromRelatedTypes` | 2 | interface 與 derived type 的 selector 不應把相關型別 overload 一併帶入；兩列確認拒絕訊息與來源 bytes。 | Roslyn 符號與宣告型別關係。 |
| [RenameTests.cs:91](https://github.com/YuChia-Wei/ai-collaboration-framework/blob/41e4ebb8e716355ac86c4b39a8846e7b6711c1aa/tests/dotnet-refactoring/integration/RenameTests.cs#L91) `TypeRenameUpdatesDeclarationAndConsumer` | 2 | class 與 interface 的重新命名都應同步更新宣告和 consumer 中手寫指定的 token。 | Roslyn 工作區；兩種 symbol kind 分列驗證。 |
| [RenameTests.cs:118](https://github.com/YuChia-Wei/ai-collaboration-framework/blob/41e4ebb8e716355ac86c4b39a8846e7b6711c1aa/tests/dotnet-refactoring/integration/RenameTests.cs#L118) `RenamesSelectedPropertyOrField` | 2 | 選中的 property 改為 `Value`、field 改為 `Data`；宣告和使用處要一致更新。 | Roslyn 工作區與來源內容。 |
| [RenameTests.cs:142](https://github.com/YuChia-Wei/ai-collaboration-framework/blob/41e4ebb8e716355ac86c4b39a8846e7b6711c1aa/tests/dotnet-refactoring/integration/RenameTests.cs#L142) `PositionRenamesParameterOrLocal` | 3 | 由游標位置選取 parameter、local 或 contextual keyword `record`，並只改正確作用域；不得增加新錯誤。 | Roslyn 符號綁定與語法位置。 |
| [RenameTests.cs:183](https://github.com/YuChia-Wei/ai-collaboration-framework/blob/41e4ebb8e716355ac86c4b39a8846e7b6711c1aa/tests/dotnet-refactoring/integration/RenameTests.cs#L183) `InvalidNamesSelectionsAndCollisionsProduceNoEdits` | 5 | 五種輸入：模糊 ID、class、非法名稱、`Property`、`ToString` 衝突；確認各自拒絕且沒有 edit。 | Roslyn planner 與手寫來源／預期結果。 |
| [RenameTests.cs:212](https://github.com/YuChia-Wei/ai-collaboration-framework/blob/41e4ebb8e716355ac86c4b39a8846e7b6711c1aa/tests/dotnet-refactoring/integration/RenameTests.cs#L212) `PositionOutsideIdentifierAndOverloadGroupAreRefused` | 1 個方法、2 個位置 | 游標在空白處應拒絕；選到 overload group 應回報符號模糊；兩者皆不得修改來源。 | Roslyn selection 與符號分析。 |
| [RenameTests.cs:266](https://github.com/YuChia-Wei/ai-collaboration-framework/blob/41e4ebb8e716355ac86c4b39a8846e7b6711c1aa/tests/dotnet-refactoring/integration/RenameTests.cs#L266) `RefusesOverrideOfFrameworkMember` | 1 | metadata 中的 framework member override 不可重新命名；確認拒絕且 bytes 不變。 | Roslyn metadata 與 override 關係。 |
| [RenameTests.cs:295](https://github.com/YuChia-Wei/ai-collaboration-framework/blob/41e4ebb8e716355ac86c4b39a8846e7b6711c1aa/tests/dotnet-refactoring/integration/RenameTests.cs#L295) `BaselineDiagnosticsRemainVisibleIncludingMappedOffsets` | 1 | 兩個手寫缺少型別錯誤應仍顯示兩個 CS0246，且不產生新錯誤。 | Roslyn 編譯診斷。 |
| [RenameTests.cs:321](https://github.com/YuChia-Wei/ai-collaboration-framework/blob/41e4ebb8e716355ac86c4b39a8846e7b6711c1aa/tests/dotnet-refactoring/integration/RenameTests.cs#L321) `BaselineErrorDoesNotHideNewLocalCollision` | 1 | 原有編譯錯誤不能遮蔽重新命名造成的新本地衝突；確認允許的拒絕結果且 bytes 不變。 | Roslyn 編譯與作用域衝突。 |
| [RenameTests.cs:344](https://github.com/YuChia-Wei/ai-collaboration-framework/blob/41e4ebb8e716355ac86c4b39a8846e7b6711c1aa/tests/dotnet-refactoring/integration/RenameTests.cs#L344) `AliasAndGenericNameofPreserveSyntax` | 2 | alias/global-qualified 與 open/closed generic `nameof` 情境下，重新命名後語法形狀仍正確，且沒有新錯誤。 | Roslyn 語法與符號分析。 |
| [RenameTests.cs:375](https://github.com/YuChia-Wei/ai-collaboration-framework/blob/41e4ebb8e716355ac86c4b39a8846e7b6711c1aa/tests/dotnet-refactoring/integration/RenameTests.cs#L375) `PreservesBomAndNoFinalNewline` | 1 | 重新命名後保留 UTF-8 BOM、不增加檔尾換行，patch 標記正確。 | Planner 到檔案 bytes／patch 的整合。 |
| [RenameTests.cs:402](https://github.com/YuChia-Wei/ai-collaboration-framework/blob/41e4ebb8e716355ac86c4b39a8846e7b6711c1aa/tests/dotnet-refactoring/integration/RenameTests.cs#L402) `CompactPatchOmitsDistantUnchangedContext` | 1 | 兩個相距很遠的修改應形成兩個 hunk，中間未改內容不應被塞進 patch，Before bytes 仍正確。 | Planner 與 patch 輸出。 |
| [RenameTests.cs:436](https://github.com/YuChia-Wei/ai-collaboration-framework/blob/41e4ebb8e716355ac86c4b39a8846e7b6711c1aa/tests/dotnet-refactoring/integration/RenameTests.cs#L436) `CrOnlySourceAndPatchAreByteExact` | 1 | CR-only 檔案在 Before、After 與 patch header/hunk/marker 中都保持精確位元組內容。 | 重新命名規劃到 byte-level patch。 |
| [ExtractInterfaceTests.cs:9](https://github.com/YuChia-Wei/ai-collaboration-framework/blob/41e4ebb8e716355ac86c4b39a8846e7b6711c1aa/tests/dotnet-refactoring/integration/ExtractInterfaceTests.cs#L9) `NullableGenericContractPreservesRefOutAndPrivateSetterBehavior` | 1 | 抽出的介面保留 `T:class`、`T?`、getter-only、`unmanaged`、`ref/out` 等契約；獨立 consumer 執行結果為 `True\|0\|abc\|3\|abc`。 | Roslyn planner 加另一 compilation/assembly consumer。 |
| [ExtractInterfaceTests.cs:85](https://github.com/YuChia-Wei/ai-collaboration-framework/blob/41e4ebb8e716355ac86c4b39a8846e7b6711c1aa/tests/dotnet-refactoring/integration/ExtractInterfaceTests.cs#L85) `ExactDeclaredMethodOrPropertyIsRequired` | 3 | 對 field、其他 owner 的成員、模糊 method ID 進行選取時都要拒絕，且不建立檔案、不改來源。 | Roslyn 成員選取與符號 owner 判定。 |
| [ExtractInterfaceTests.cs:115](https://github.com/YuChia-Wei/ai-collaboration-framework/blob/41e4ebb8e716355ac86c4b39a8846e7b6711c1aa/tests/dotnet-refactoring/integration/ExtractInterfaceTests.cs#L115) `DuplicateMemberIdsAreRefused` | 1 | property ID 重複時回報無效 members，不產生輸出，來源 bytes 不變。 | Roslyn selection 與檔案系統。 |
| [ExtractInterfaceTests.cs:147](https://github.com/YuChia-Wei/ai-collaboration-framework/blob/41e4ebb8e716355ac86c4b39a8846e7b6711c1aa/tests/dotnet-refactoring/integration/ExtractInterfaceTests.cs#L147) `InvalidInterfaceOrNamespaceIdentifierIsRefused` | 2 | 介面名稱是 class 或非法識別字時，回報無效名稱且不產生檔案、不改來源。 | Roslyn 語法／名稱驗證。 |
| [ExtractInterfaceTests.cs:183](https://github.com/YuChia-Wei/ai-collaboration-framework/blob/41e4ebb8e716355ac86c4b39a8846e7b6711c1aa/tests/dotnet-refactoring/integration/ExtractInterfaceTests.cs#L183) `InvalidOutputPathIsRefused` | 6 | 輸出路徑為既有 `Service.cs`、`../Outside.cs`、ADS 樣式 `payload.cs:stream.cs`、`CON.cs`、`COM¹.cs` 或 `obj/ISelected.cs` 時，應拒絕輸出。 | 真實路徑與檔案系統；冒號案例受作業系統路徑規則影響。 |
| [ExtractInterfaceTests.cs:222](https://github.com/YuChia-Wei/ai-collaboration-framework/blob/41e4ebb8e716355ac86c4b39a8846e7b6711c1aa/tests/dotnet-refactoring/integration/ExtractInterfaceTests.cs#L222) `UnsupportedMemberShapesAreRefused` | 6 | static、optional parameter、attribute、indexer、init、setter parameter attribute 等成員形狀都應被拒絕。 | Roslyn syntax/symbol 結構。 |
| [ExtractInterfaceTests.cs:252](https://github.com/YuChia-Wei/ai-collaboration-framework/blob/41e4ebb8e716355ac86c4b39a8846e7b6711c1aa/tests/dotnet-refactoring/integration/ExtractInterfaceTests.cs#L252) `DuplicateTypeWouldIntroduceCompilationErrors` | 1 | 已存在同名型別時，抽取會造成編譯錯誤，因此應拒絕且不改來源、不建立輸出。 | Roslyn compiler interaction。 |
| [ExtractInterfaceTests.cs:284](https://github.com/YuChia-Wei/ai-collaboration-framework/blob/41e4ebb8e716355ac86c4b39a8846e7b6711c1aa/tests/dotnet-refactoring/integration/ExtractInterfaceTests.cs#L284) `ExistingTypeAndNamespaceBindingsCannotChange` | 2 | 新介面或型別不得改變既有 imported／qualified lookup 的解析結果；應回報名稱衝突且 bytes 不變。 | 跨專案參考的 Roslyn semantic binding。 |
| [ExtractInterfaceTests.cs:316](https://github.com/YuChia-Wei/ai-collaboration-framework/blob/41e4ebb8e716355ac86c4b39a8846e7b6711c1aa/tests/dotnet-refactoring/integration/ExtractInterfaceTests.cs#L316) `PrimaryConstructorAndMethodBodyArePreserved` | 1 | 抽取介面後保留指定原始程式與 method body，獨立 consumer 執行結果為 7。 | Roslyn planner 加真實 consumer dispatch。 |
| [GeneratorIntegrationTests.cs:12](https://github.com/YuChia-Wei/ai-collaboration-framework/blob/41e4ebb8e716355ac86c4b39a8846e7b6711c1aa/tests/dotnet-refactoring/integration/GeneratorIntegrationTests.cs#L12) `SdkGeneratorOutputBlocksExtractionButUnrelatedOutputAllowsRename` | 1 個方法、2 段操作 | SDK generator 輸出應阻止 Extract，但不相關的 Rename 可成功；authored references 更新後建立 B.dll。 | 真實 SDK generator 發現與建置；同一 restored fixture 的連續操作。 |
| [GeneratorIntegrationTests.cs:71](https://github.com/YuChia-Wei/ai-collaboration-framework/blob/41e4ebb8e716355ac86c4b39a8846e7b6711c1aa/tests/dotnet-refactoring/integration/GeneratorIntegrationTests.cs#L71) `GeneratorReferenceAndDeclarationCannotBeEdited` | 2 | generated reference 與 generated declaration 分別應回報不可編輯的 reference／symbol；皆不產生計畫。 | Roslyn generated symbol/reference 判定。 |
| [GeneratorIntegrationTests.cs:107](https://github.com/YuChia-Wei/ai-collaboration-framework/blob/41e4ebb8e716355ac86c4b39a8846e7b6711c1aa/tests/dotnet-refactoring/integration/GeneratorIntegrationTests.cs#L107) `ExtractionRefusesAnalyzerBuiltAgainstNewerSdkRoslyn` | 1 | 以較新 SDK Roslyn 建置的 analyzer DLL，應因 generator 相容性拒絕 Extract，並辨認 DLL／ABI 原因。 | 真實較新 SDK build、PE 與 analyzer discovery。 |

### 整合與單元測試：檔案套用

| 位置與方法 | 案例 | 測試實際驗證的行為 | 測試邊界 |
|---|---:|---|---|
| [FileApplyTests.cs:8](https://github.com/YuChia-Wei/ai-collaboration-framework/blob/41e4ebb8e716355ac86c4b39a8846e7b6711c1aa/tests/dotnet-refactoring/integration/FileApplyTests.cs#L8) `UnchangedInputDeniesOrdinaryWriterUntilHandlesClose` | 1 | 真正檔案分享鎖住輸入時，一般 writer 應被拒絕；確認 `AFTER!` bytes，解除鎖後可寫入 `released`。 | 真實檔案系統與 Windows sharing。 |
| [FileApplyTests.cs:64](https://github.com/YuChia-Wei/ai-collaboration-framework/blob/41e4ebb8e716355ac86c4b39a8846e7b6711c1aa/tests/dotnet-refactoring/integration/FileApplyTests.cs#L64) `CompetingCreatorOwnsOutputAndExistingSourceStaysOriginal` | 1 | CreateNew 競爭者先建立輸出時，Apply 回報部分失敗，保留原始來源與競爭者寫入的 bytes。 | 真實 CreateNew race。 |
| [FileApplyTests.cs:105](https://github.com/YuChia-Wei/ai-collaboration-framework/blob/41e4ebb8e716355ac86c4b39a8846e7b6711c1aa/tests/dotnet-refactoring/integration/FileApplyTests.cs#L105) `CreateAcquisitionFailureDistinguishesEmptyAndUnattemptedOutputs` | 1 | 取得輸出 stream 失敗時，區分原檔、已建立空檔、狀態未知與尚未建立；確認 handles 關閉。 | 受控 stream/delegate；可歸為單元測試。 |
| [FileApplyTests.cs:143](https://github.com/YuChia-Wei/ai-collaboration-framework/blob/41e4ebb8e716355ac86c4b39a8846e7b6711c1aa/tests/dotnet-refactoring/integration/FileApplyTests.cs#L143) `PartialNewFileRequiresRecoveryForCreatedFile` | 1 | 新檔只寫入部分內容後失敗時，回報 partial 並說明沒有原檔可還原空檔。 | 受控 stream；可歸為單元測試。 |
| [FileApplyTests.cs:9](https://github.com/YuChia-Wei/ai-collaboration-framework/blob/41e4ebb8e716355ac86c4b39a8846e7b6711c1aa/tests/dotnet-refactoring/unit/FileApplyTests.cs#L9) `ReportsWrittenPrefixAndUntouchedFilesAfterFailure` | 1 | 寫入故障後辨認已寫入的前綴、部分套用狀態與未變更檔案，並提供 recovery 資訊。 | 故障注入 stream。 |
| [FileApplyTests.cs:39](https://github.com/YuChia-Wei/ai-collaboration-framework/blob/41e4ebb8e716355ac86c4b39a8846e7b6711c1aa/tests/dotnet-refactoring/unit/FileApplyTests.cs#L39) `UnreadableStateIsUnknown` | 1 | 無法讀取的狀態必須標成 unknown，hash 為 null。 | 受控單元邊界。 |
| [FileApplyTests.cs:63](https://github.com/YuChia-Wei/ai-collaboration-framework/blob/41e4ebb8e716355ac86c4b39a8846e7b6711c1aa/tests/dotnet-refactoring/unit/FileApplyTests.cs#L63) `CloseFailurePreservesObservationsAndAttemptsEveryClose` | 1 | 即使某個 close 失敗，也嘗試關閉所有 handle；保留已知套用狀態，將失敗檔案標成 unknown/null。 | 受控 stream 與 close fault。 |

### 發佈成品測試

| 位置與方法 | 案例 | 測試實際驗證的行為 | 測試邊界 |
|---|---:|---|---|
| [PublishedArtifactTests.cs:13](https://github.com/YuChia-Wei/ai-collaboration-framework/blob/41e4ebb8e716355ac86c4b39a8846e7b6711c1aa/tests/dotnet-refactoring/artifact/PublishedArtifactTests.cs#L13) `PublishedRenamePreservesCrossProjectSemanticsAndUnrelatedBytes` | 1 | 解壓後的真實 apphost 能重新命名跨專案 interface/override/cref/nameof；overload、comment、string 與 CRLF 保留，並能建置。 | 發佈成品加 SDK。 |
| [PublishedArtifactTests.cs:77](https://github.com/YuChia-Wei/ai-collaboration-framework/blob/41e4ebb8e716355ac86c4b39a8846e7b6711c1aa/tests/dotnet-refactoring/artifact/PublishedArtifactTests.cs#L77) `PublishedExtractionAppliesSelectedContractAndConsumerDispatches` | 1 | 真實成品完成 plan、create/modify；preview 不寫檔；project/consumer bytes 正確，consumer 結果為 `3\|7\|4`。 | 發佈成品、SDK 與跨 assembly 執行。 |
| [PublishedArtifactTests.cs:165](https://github.com/YuChia-Wei/ai-collaboration-framework/blob/41e4ebb8e716355ac86c4b39a8846e7b6711c1aa/tests/dotnet-refactoring/artifact/PublishedArtifactTests.cs#L165) `CallerSdkConfigurationDoesNotOverrideWorkspaceSdk` | 1 | caller 端 `global.json` 指向 99.0.100 時，workspace 有效 SDK 仍應主導 preview/plan。 | 真實 apphost、CWD、`global.json` 與 SDK。 |
| [PublishedArtifactTests.cs:191](https://github.com/YuChia-Wei/ai-collaboration-framework/blob/41e4ebb8e716355ac86c4b39a8846e7b6711c1aa/tests/dotnet-refactoring/artifact/PublishedArtifactTests.cs#L191) `SdkPathsCanSelectLocalSdkWhenSameVersionExistsInHost` | 1 | host 和 local root 有相同版本 SDK 時，CLI 應實際載入 local root 的 Microsoft.Build.dll，Extract 也應捕捉其實體身分。 | 發佈成品、SDK path 與 junction。 |
| [PublishedArtifactTests.cs:256](https://github.com/YuChia-Wei/ai-collaboration-framework/blob/41e4ebb8e716355ac86c4b39a8846e7b6711c1aa/tests/dotnet-refactoring/artifact/PublishedArtifactTests.cs#L256) `ExtractedPackageIncludesRuntimeNoticesAndNoTestDependencies` | 1 | 封裝包含必要執行檔、README、notice、BuildHost、license，且已知 test family 不被帶入。 | 封裝檔案盤點；不是對所有可能封裝內容的完整證明。 |

## Format 工具

**3 個測試專案，20 個方法、32 個邏輯案例**：單元 6、一般命令與 SDK 整合 24、發佈成品 2。一般 Windows TRX 為 21 通過、1 略過。macOS 的三列 POSIX 檔名案例在 Windows 只記錄為一個略過項。

來源檔案根目錄：`tests/dotnet-formatting/`。

| 位置與方法 | 案例 | 測試實際驗證的行為 | 測試邊界 |
|---|---:|---|---|
| [CleanupRulesTests.cs:14](https://github.com/YuChia-Wei/ai-collaboration-framework/blob/41e4ebb8e716355ac86c4b39a8846e7b6711c1aa/tests/dotnet-formatting/unit/CleanupRulesTests.cs#L14) `Should_reject_unsupported_cleanup_when_validating_the_request` | 6 | 缺少 diagnostics/severity、未知 style、錯誤 mode/ID、CA1040 無 fixer、禁止 whitespace 各自回報指定拒絕碼。 | typed Request 與 Rules.Validate；不啟動 SDK。 |
| [RequestTests.cs:21](https://github.com/YuChia-Wei/ai-collaboration-framework/blob/41e4ebb8e716355ac86c4b39a8846e7b6711c1aa/tests/dotnet-formatting/RequestTests.cs#L21) `InvalidJsonFailsWithoutSdkOrSourceChanges` | 5 | 未知欄位、錯誤型別、重複欄位、格式錯誤、null 五種 JSON 都回報 invalid-request、不執行命令且來源不變。 | 真實 JSON parser、檔案系統與 wire response。 |
| [RequestTests.cs:52](https://github.com/YuChia-Wei/ai-collaboration-framework/blob/41e4ebb8e716355ac86c4b39a8846e7b6711c1aa/tests/dotnet-formatting/RequestTests.cs#L52) `Should_report_no_fixer_without_sdk_commands_when_submitting_ca1040` | 1 | CA1040 沒有 fixer 時回報 no-fixer failure envelope，且沒有 SDK 命令。 | 命令入口與 formatter 規則。 |
| [RequestTests.cs:77](https://github.com/YuChia-Wei/ai-collaboration-framework/blob/41e4ebb8e716355ac86c4b39a8846e7b6711c1aa/tests/dotnet-formatting/RequestTests.cs#L77) `EmptySelectionFailsBeforeSdk` | 1 | 空選取應在 SDK 啟動前回報 invalid-request、不執行命令或寫檔。 | 命令入口前置檢查。 |
| [RequestTests.cs:103](https://github.com/YuChia-Wei/ai-collaboration-framework/blob/41e4ebb8e716355ac86c4b39a8846e7b6711c1aa/tests/dotnet-formatting/RequestTests.cs#L103) `MissingFileAndDirectorySelectionsFailBeforeSdk` | 2 | 選取不存在的檔案，或選取目錄時，回報 invalid-selection、不執行命令、不寫檔。 | 真實路徑／檔案系統；現有目錄名稱可能先撞到副檔名檢查。 |
| [RequestTests.cs:130](https://github.com/YuChia-Wei/ai-collaboration-framework/blob/41e4ebb8e716355ac86c4b39a8846e7b6711c1aa/tests/dotnet-formatting/RequestTests.cs#L130) `MissingWorkspaceFailsBeforeSdk` | 1 | workspace 不存在時回報 load-failed、不執行 SDK 命令。 | 真實檔案系統與命令前置檢查。 |
| [RequestTests.cs:153](https://github.com/YuChia-Wei/ai-collaboration-framework/blob/41e4ebb8e716355ac86c4b39a8846e7b6711c1aa/tests/dotnet-formatting/RequestTests.cs#L153) `Should_refuse_cleanup_when_the_solution_maps_debug_to_release` | 1 | 指定的 `.sln` cleanup workspace 不支援時，回報 unsupported-cleanup-workspace、不執行命令。 | 檔案系統與副檔名拒絕；不是對 Debug/Release mapping 的完整評估測試。 |
| [RequestTests.cs:195](https://github.com/YuChia-Wei/ai-collaboration-framework/blob/41e4ebb8e716355ac86c4b39a8846e7b6711c1aa/tests/dotnet-formatting/RequestTests.cs#L195) `Should_preserve_the_linked_source_when_it_is_outside_the_workspace` | 1 | workspace 外的 parent-relative linked source 應被拒絕，來源 bytes 保持不變。 | 真實檔案系統；此列不執行 MSBuild 評估。 |
| [RequestTests.cs:230](https://github.com/YuChia-Wei/ai-collaboration-framework/blob/41e4ebb8e716355ac86c4b39a8846e7b6711c1aa/tests/dotnet-formatting/RequestTests.cs#L230) `PosixLiteralGlobAndSeparatorNamesFailBeforeSdk` | 3 | 真實 POSIX 檔名含 `*`、`?` 或反斜線時，在 SDK 啟動前拒絕，並保留選取檔與可能匹配的鄰檔。 | POSIX/macOS 真實檔名；Windows TRX 將三列收成一個略過結果。 |
| [SdkTests.cs:24](https://github.com/YuChia-Wei/ai-collaboration-framework/blob/41e4ebb8e716355ac86c4b39a8846e7b6711c1aa/tests/dotnet-formatting/SdkTests.cs#L24) `ExistingFileOutsideCompileItemsIsRefused` | 1 | 真實 Compile `Remove` 排除的既有檔案不得被 formatter 選取；回報 unmatched-selection 且不寫檔。 | SDK restore 與 evaluated Compile items。 |
| [SdkTests.cs:49](https://github.com/YuChia-Wei/ai-collaboration-framework/blob/41e4ebb8e716355ac86c4b39a8846e7b6711c1aa/tests/dotnet-formatting/SdkTests.cs#L49) `MalformedProjectCannotLoad` | 1 | 無效 XML 專案應回報 load-failed。 | SDK 子程序載入；此版本已無 restore。 |
| [SdkTests.cs:71](https://github.com/YuChia-Wei/ai-collaboration-framework/blob/41e4ebb8e716355ac86c4b39a8846e7b6711c1aa/tests/dotnet-formatting/SdkTests.cs#L71) `DesignTimeFailureReportsObservedSourceChanges` | 1 個方法、2 次呼叫 | 目標失敗且有／沒有來源副作用時，都回報 load-failed；結果需反映實際 bytes、變更檔案與診斷。 | 一次 SDK restore、兩次真實載入。 |
| [SdkTests.cs:132](https://github.com/YuChia-Wei/ai-collaboration-framework/blob/41e4ebb8e716355ac86c4b39a8846e7b6711c1aa/tests/dotnet-formatting/SdkTests.cs#L132) `SlnxAndEditorConfigGeneratedSelectionsAreUnreportedAndUnchanged` | 1 個方法、2 次呼叫 | `.slnx` 中的 generated 檔與 editorconfig 保持不變；classic `.sln` 含 solution folder 時仍找到 authored source 修改。 | SDK restore 與兩種解決方案入口。 |
| [SdkTests.cs:185](https://github.com/YuChia-Wei/ai-collaboration-framework/blob/41e4ebb8e716355ac86c4b39a8846e7b6711c1aa/tests/dotnet-formatting/SdkTests.cs#L185) `ResponsePrefixAndLinkedPathsRemainLiteral` | 1 個方法、2 段操作 | `@file` 字串不被展開成 response file；`.slnx` 的 linked file 可選取且只改所選檔。 | SDK 工作區、命令與 linked paths。 |
| [SdkTests.cs:244](https://github.com/YuChia-Wei/ai-collaboration-framework/blob/41e4ebb8e716355ac86c4b39a8846e7b6711c1aa/tests/dotnet-formatting/SdkTests.cs#L244) `StyleHonorsSeverityAndRecheckIsClean` | 1 個方法、4 次 wrapper 呼叫 | IDE0008 在 error 設定下忽略、warning 設定下回報；check 不寫檔、apply 修正、未選檔不變。 | SDK formatter；四次呼叫共用同一個方法情境。 |
| [SdkTests.cs:316](https://github.com/YuChia-Wei/ai-collaboration-framework/blob/41e4ebb8e716355ac86c4b39a8846e7b6711c1aa/tests/dotnet-formatting/SdkTests.cs#L316) `AnalyzerAppliesRequestedFixWithoutStyleChanges` | 1 個方法、2 段操作 | CA1805 移除 initializer 但保留 `var`；check 不寫檔，修正後沒有 remaining issue，未選檔不變。 | SDK analyzer/fixer 與真實檔案。 |
| [SdkTests.cs:369](https://github.com/YuChia-Wei/ai-collaboration-framework/blob/41e4ebb8e716355ac86c4b39a8846e7b6711c1aa/tests/dotnet-formatting/SdkTests.cs#L369) `SemanticFailureDoesNotReportClean` | 1 | 缺少型別時應回報 semantic-prerequisite-failed，不可錯報 clean，來源 bytes 不變。 | SDK compiler 與真實診斷。 |
| [GeneratorConsentTests.cs:11](https://github.com/YuChia-Wei/ai-collaboration-framework/blob/41e4ebb8e716355ac86c4b39a8846e7b6711c1aa/tests/dotnet-formatting/GeneratorConsentTests.cs#L11) `GeneratorExecutesOnlyAfterConsentInBothDesignTimeContexts` | 1 個方法、6 次呼叫 | 一般與 formatter-only 情境需 consent；markup/mapped-reference 情境應拒絕且 marker 不得產生。 | 真實 generator DLL、SDK 專案與 marker oracle。 |
| [PublishedFormatTests.cs:11](https://github.com/YuChia-Wei/ai-collaboration-framework/blob/41e4ebb8e716355ac86c4b39a8846e7b6711c1aa/tests/dotnet-formatting/artifact/PublishedFormatTests.cs#L11) `PublishedExecutableChecksAndAppliesNestedEditorConfigToSelectedBytesOnly` | 1 | 真實成品的 compact/verbose schema、SDK、nested editorconfig 縮排、check/apply/clean 都正確，且未選檔 bytes 不變。 | 發佈成品加 SDK；一個方法內四次呼叫。 |
| [PublishedFormatTests.cs:108](https://github.com/YuChia-Wei/ai-collaboration-framework/blob/41e4ebb8e716355ac86c4b39a8846e7b6711c1aa/tests/dotnet-formatting/artifact/PublishedFormatTests.cs#L108) `CaseAliasOnCaseSensitiveVolumeIsRejectedBeforeFormatter` | 1 | 大小寫敏感磁碟上兩個 Compile identity 只差大小寫時，formatter 應回報 unsupported-selection 並保留兩個檔案。 | macOS arm64/APFS 與發佈成品。 |

## Snippet 工具

**3 個測試專案，14 個方法、24 個案例**：單元 4 方法／8 案例、一般整合 8／14、發佈成品 2／2。

來源檔案根目錄：`tests/dotnet-generation/snippet-tool/`。

| 位置與方法 | 案例 | 測試實際驗證的行為 | 測試邊界 |
|---|---:|---|---|
| [ExpansionTests.cs:12](https://github.com/YuChia-Wei/ai-collaboration-framework/blob/41e4ebb8e716355ac86c4b39a8846e7b6711c1aa/tests/dotnet-generation/snippet-tool/unit/ExpansionTests.cs#L12) `Should_reject_invalid_parameter_inputs_when_rendering` | 4 | 缺少／未知參數、保留字識別字、未列出的 enum 值分別回報固定拒絕碼。 | 渲染參數驗證單元測試。 |
| [ExpansionTests.cs:42](https://github.com/YuChia-Wei/ai-collaboration-framework/blob/41e4ebb8e716355ac86c4b39a8846e7b6711c1aa/tests/dotnet-generation/snippet-tool/unit/ExpansionTests.cs#L42) `Should_reject_unknown_or_malformed_placeholders_when_parsing_the_body` | 2 | 未宣告 placeholder 與格式錯誤 placeholder 各回報不同拒絕碼。 | placeholder parser 單元測試。 |
| [ExpansionTests.cs:58](https://github.com/YuChia-Wei/ai-collaboration-framework/blob/41e4ebb8e716355ac86c4b39a8846e7b6711c1aa/tests/dotnet-generation/snippet-tool/unit/ExpansionTests.cs#L58) `Should_reject_an_unknown_kind_when_validating_a_parameter_definition` | 1 | 未知 script kind 在 catalog validation 時回報 invalid-catalog。 | catalog 欄位驗證。 |
| [ExpansionTests.cs:69](https://github.com/YuChia-Wei/ai-collaboration-framework/blob/41e4ebb8e716355ac86c4b39a8846e7b6711c1aa/tests/dotnet-generation/snippet-tool/unit/ExpansionTests.cs#L69) `Should_preserve_unicode_and_literal_placeholders_when_expanding_with_indent_and_crlf` | 1 | 精確保留手寫 CRLF、縮排、空行、Unicode 與 escaped literal text。 | 純文字 renderer 單元測試；輸出 bytes 是 oracle。 |
| [SnippetTests.cs:20](https://github.com/YuChia-Wei/ai-collaboration-framework/blob/41e4ebb8e716355ac86c4b39a8846e7b6711c1aa/tests/dotnet-generation/snippet-tool/SnippetTests.cs#L20) `BuiltInCatalogListsSearchesAndInspectsWithoutAChildProcess` | 1 個方法、list/search/inspect 三個操作 | shipped catalog 排序、GUARD 搜尋，以及 interface fragment 的 context/usings/default/source/body 都正確。 | 真實 catalog、命令入口；不啟動 child process。預期 catalog 清單獨立於實際 catalog。 |
| [SnippetTests.cs:58](https://github.com/YuChia-Wei/ai-collaboration-framework/blob/41e4ebb8e716355ac86c4b39a8846e7b6711c1aa/tests/dotnet-generation/snippet-tool/SnippetTests.cs#L58) `BuiltInFragmentsUseTypedParametersAndDefaults` | 1 | built-in fragment 的 enum、return/default、縮排與 LF 輸出符合手寫預期文字。 | 真實資產與 renderer。 |
| [SnippetTests.cs:77](https://github.com/YuChia-Wei/ai-collaboration-framework/blob/41e4ebb8e716355ac86c4b39a8846e7b6711c1aa/tests/dotnet-generation/snippet-tool/SnippetTests.cs#L77) `BuiltInStringGuardUsesTheNamedParameter` | 1 | string guard fragment 的 label、縮排、LF 與指定參數一致。 | 真實資產 renderer；固定文字契約不等同編譯語意測試。 |
| [SnippetTests.cs:99](https://github.com/YuChia-Wei/ai-collaboration-framework/blob/41e4ebb8e716355ac86c4b39a8846e7b6711c1aa/tests/dotnet-generation/snippet-tool/SnippetTests.cs#L99) `InvalidRequestPreservesFailureEnvelope` | 5 | 缺參數、未知參數、重複欄位、schema 錯誤、catalog 缺失各自回報 exit 1、正確 stderr code，stdout 為空。 | 真實 JSON/wire 命令入口。 |
| [SnippetTests.cs:117](https://github.com/YuChia-Wei/ai-collaboration-framework/blob/41e4ebb8e716355ac86c4b39a8846e7b6711c1aa/tests/dotnet-generation/snippet-tool/SnippetTests.cs#L117) `CustomMetadataIsLazyAndMissingOrEmptyBodiesHaveDistinctErrors` | 1 個方法、多個操作 | 只讀 metadata 不需 body；inspect 區分 body 缺失與空字串；custom source 不可 fallback 到 built-in。 | 真實 catalog 與 body 檔案。 |
| [SnippetTests.cs:155](https://github.com/YuChia-Wei/ai-collaboration-framework/blob/41e4ebb8e716355ac86c4b39a8846e7b6711c1aa/tests/dotnet-generation/snippet-tool/SnippetTests.cs#L155) `Should_use_the_selected_source_when_rendering_and_reject_invalid_inspection` | 1 | 指定 custom source 後以 CRLF/prefix 正確渲染；malformed inspection 應拒絕。 | 真實 source selection 與命令接線。 |
| [SnippetTests.cs:187](https://github.com/YuChia-Wei/ai-collaboration-framework/blob/41e4ebb8e716355ac86c4b39a8846e7b6711c1aa/tests/dotnet-generation/snippet-tool/SnippetTests.cs#L187) `InvalidCatalogDoesNotList` | 3 | schema 錯誤、重複 ID、無效 kind 三種 catalog 分別回報指定錯誤，不應列出內容。 | 真實 JSON catalog 讀取與 validation。 |
| [GeneratedFragmentTests.cs:14](https://github.com/YuChia-Wei/ai-collaboration-framework/blob/41e4ebb8e716355ac86c4b39a8846e7b6711c1aa/tests/dotnet-generation/snippet-tool/GeneratedFragmentTests.cs#L14) `Should_retain_the_rendered_fragment_contracts_when_compiled_in_a_consumer` | 1 | 真實渲染結果能以 C# 14、warnings-as-errors 編譯；consumer 驗證 guard exception/參數、取消、constructor identity、GUID、Unicode、replay/commit 行為。 | Roslyn 編譯、emit 與 collectible AssemblyLoadContext；不啟動 dotnet child process。 |
| [PublishedSnippetTests.cs:12](https://github.com/YuChia-Wei/ai-collaboration-framework/blob/41e4ebb8e716355ac86c4b39a8846e7b6711c1aa/tests/dotnet-generation/snippet-tool/artifact/PublishedSnippetTests.cs#L12) `PublishedExecutableFindsItsBundledCatalogFromAnotherDirectory` | 1 | 真實 native executable 從不同工作目錄啟動，仍找到相鄰 catalog 並回傳 IDs/schema envelope/version。 | 發佈成品與另一個 CWD。 |
| [PublishedSnippetTests.cs:68](https://github.com/YuChia-Wei/ai-collaboration-framework/blob/41e4ebb8e716355ac86c4b39a8846e7b6711c1aa/tests/dotnet-generation/snippet-tool/artifact/PublishedSnippetTests.cs#L68) `PublishedExecutableRejectsFifoWithoutOpeningIt` | 1 | 真實 Linux FIFO 作為 body 輸入時，成品限時回報 invalid-body。 | Linux x64 native 成品與 FIFO；驗證及時拒絕，不主張 syscall trace。 |

## 原生 templates

**2 個測試專案，2 個方法／2 個案例**。source template 測試包含在一般 RunAll；packed template 是發佈成品測試。

來源檔案根目錄：`tests/dotnet-generation/templates/`。

| 位置與方法 | 案例 | 測試實際驗證的行為 | 測試邊界 |
|---|---:|---|---|
| [TemplateTests.cs:7](https://github.com/YuChia-Wei/ai-collaboration-framework/blob/41e4ebb8e716355ac86c4b39a8846e7b6711c1aa/tests/dotnet-generation/templates/TemplateTests.cs#L7) `NativeTemplatesGenerateBuildAndServeBothApiShapesAndPreserveEdits` | 1 | 五個 template IDs、namespace、dry-run 不建目錄；產生的 typed items 可由 consumer 使用；保留 customization marker 和四專案圖；兩種 API app 可經 HTTP 回應；發生 collision 時保留使用者 bytes，且可 uninstall。 | 原生 `dotnet new` 註冊、隔離 hive、兩次建置、兩個 loopback Kestrel app。 |
| [PublishedTemplateTests.cs:9](https://github.com/YuChia-Wei/ai-collaboration-framework/blob/41e4ebb8e716355ac86c4b39a8846e7b6711c1aa/tests/dotnet-generation/templates/artifact/PublishedTemplateTests.cs#L9) `PackedTemplatesGenerateBuildAndServeBothApiShapesAndPreserveEdits` | 1 | 從實際 nupkg 安裝／產生／解除安裝；另一路徑從 extracted content 註冊後，產生的內容可供 consumer 使用。 | 發佈套件加 SDK。直接套件路徑目前驗證 class/custom namespace；完整 consumer/build/HTTP 行程由 extracted-content 路徑驗證。 |

`.csproj.template` 是原生 template 生成的內容檔，不是獨立測試，也不是額外的 test project。

## 知識範本範例

這 **9 個案例不是工具測試**。它們驗證知識文件中的 C# 範例契約。兩個對應的測試專案尚屬後續選用項目，不在目前 11 個 framework test projects 或一般 RunAll 內。CT-005 需外部 DLL；本次筆記未重新取得其原始外部契約，故不能宣稱已驗證語意完全對齊。

來源檔案根目錄：`src/knowledge/dotnet-backend/templates/domain-contracts/`。

| 位置與方法 | 案例 | 測試實際驗證的行為 | 測試邊界 |
|---|---:|---|---|
| [PackageFreeContractTests.cs:11](https://github.com/YuChia-Wei/ai-collaboration-framework/blob/41e4ebb8e716355ac86c4b39a8846e7b6711c1aa/src/knowledge/dotnet-backend/templates/domain-contracts/package-free/PackageFreeContractTests.cs#L11) `ReplayRestoresCommittedStateAndOnlyNewFactsRemainPendingUntilConfirmation` | 1 | 範例中已有 2+3 的歷史時 replay 得到 5、revision 2、沒有 pending；新增事實後，要等確認到 version 3 才清除 pending。 | 生成的純範例 contract case；無 domain dependency。 |
| [PackageFreeContractTests.cs:53](https://github.com/YuChia-Wei/ai-collaboration-framework/blob/41e4ebb8e716355ac86c4b39a8846e7b6711c1aa/src/knowledge/dotnet-backend/templates/domain-contracts/package-free/PackageFreeContractTests.cs#L53) `CompletePlanHistoryRestoresRequiredNestedState` | 1 | Plan/Project/Task 歷史恢復成 nested task，version 為 3 且沒有 pending。 | 生成範例的巢狀狀態恢復。 |
| [PackageFreeContractTests.cs:82](https://github.com/YuChia-Wei/ai-collaboration-framework/blob/41e4ebb8e716355ac86c4b39a8846e7b6711c1aa/src/knowledge/dotnet-backend/templates/domain-contracts/package-free/PackageFreeContractTests.cs#L82) `EmptyPlanHistoryCannotReturnAnAggregate` | 1 | 空 history 建立 aggregate 時應拋出指定例外。 | 生成範例錯誤情境。 |
| [PackageFreeContractTests.cs:86](https://github.com/YuChia-Wei/ai-collaboration-framework/blob/41e4ebb8e716355ac86c4b39a8846e7b6711c1aa/src/knowledge/dotnet-backend/templates/domain-contracts/package-free/PackageFreeContractTests.cs#L86) `TaskCreationWithoutItsProjectCannotReturnAnAggregate` | 1 | 沒有 parent project 時不能建立 task aggregate。 | 生成範例 parent invariant。 |
| [PackageFreeContractTests.cs:93](https://github.com/YuChia-Wei/ai-collaboration-framework/blob/41e4ebb8e716355ac86c4b39a8846e7b6711c1aa/src/knowledge/dotnet-backend/templates/domain-contracts/package-free/PackageFreeContractTests.cs#L93) `TaskUpdateWithoutItsTaskCannotReturnAnAggregate` | 1 | 沒有對應 task 時不能更新 task aggregate。 | 生成範例 task invariant。 |
| [PackageFreeContractTests.cs:100](https://github.com/YuChia-Wei/ai-collaboration-framework/blob/41e4ebb8e716355ac86c4b39a8846e7b6711c1aa/src/knowledge/dotnet-backend/templates/domain-contracts/package-free/PackageFreeContractTests.cs#L100) `UnsupportedPlanFactCannotBeSilentlyIgnored` | 1 | 未知 plan fact 應拋出 `NotSupportedException`，不能靜默忽略。 | 生成範例對未知 fact 的處理。 |
| [PublishedContractTests.cs:9](https://github.com/YuChia-Wei/ai-collaboration-framework/blob/41e4ebb8e716355ac86c4b39a8846e7b6711c1aa/src/knowledge/dotnet-backend/templates/domain-contracts/published-ct005/PublishedContractTests.cs#L9) `LoadingHistoryRestoresStateWithoutPendingEventsAndCannotRepeat` | 1 | 外部 DLL 的 typed contract 範例可由 committed history 恢復 arithmetic 狀態且無 pending；不能重複 clear/reload。 | 選定外部 DLL 的 integration；外部原始契約尚未重新核對。 |
| [PublishedContractTests.cs:46](https://github.com/YuChia-Wei/ai-collaboration-framework/blob/41e4ebb8e716355ac86c4b39a8846e7b6711c1aa/src/knowledge/dotnet-backend/templates/domain-contracts/published-ct005/PublishedContractTests.cs#L46) `PendingBatchSurvivesRejectedOrUnconfirmedAppendAndClearsOnConfirmation` | 1 | 錯誤確認或尚未確認的 append 不應丟掉 pending batch；正確確認後 revision 前進並清除 pending。 | 真實外部物件與確認前後的狀態變化。 |
| [PublishedContractTests.cs:103](https://github.com/YuChia-Wei/ai-collaboration-framework/blob/41e4ebb8e716355ac86c4b39a8846e7b6711c1aa/src/knowledge/dotnet-backend/templates/domain-contracts/published-ct005/PublishedContractTests.cs#L103) `FailedReplayRejectsFurtherOperationsOnTheSameInstance` | 1 | replay 失敗後，同一個 instance 必須拒絕後續 change、commit 與 reload。 | 外部物件的失敗 replay lifecycle。 |

## 數量核對

| 範圍 | 方法數 | 邏輯案例數 |
|---|---:|---:|
| Refactor 一般整合 | 64 | 122 |
| Refactor 單元 | 3 | 3 |
| Format 一般整合 | 17 | 24 |
| Format 單元 | 1 | 6 |
| Snippet 一般整合 | 8 | 14 |
| Snippet 單元 | 4 | 8 |
| 原生 source template | 1 | 1 |
| **日常測試小計** | **98** | **178** |
| Refactor 成品 | 5 | 5 |
| Format 成品 | 2 | 2 |
| Snippet 成品 | 2 | 2 |
| Packed template 成品 | 1 | 1 |
| **成品小計** | **10** | **10** |
| Package-free 知識範本案例 | 6 | 6 |
| CT-005 知識範本案例 | 3 | 3 |
| **總計** | **117** | **197** |

方法數以固定 HEAD 的 Git-tracked C# 測試宣告做確定性核對。此表修正早先摘要對 Format 方法數（實為20）及完整清單漏列 CompilePolicy 的錯誤；案例總數未變。Theory 以資料列計案例，方法中的多次操作仍只算一個案例。因此方法數、邏輯案例數、SDK 呼叫次數、特定平台的 TRX 結果列數是不同數字。

這份清單描述目前內容，不等於全部保留的建議。必要性及後續安排見同一 workflow 的 component-test-plan.zh-TW.md；較細的既有 oracle、成本與調整理由保存在 analysis-notes.md。所有執行結果沿用其原 build 歸屬，本輪沒有重跑測試。
