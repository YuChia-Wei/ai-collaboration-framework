> Historical assessment evidence at `41e4ebb8e716355ac86c4b39a8846e7b6711c1aa`. Proposals and execution exclusions below describe the analysis stage, before the subsequent implementation decision. This is not a current test inventory or execution instruction.

# Current follow-up correction

The detailed evidence below is retained from the earlier analysis. Current disposition is in component-test-plan.zh-TW.md and the complete corrected readable list is test-inventory.zh-TW.md. Fixed 7-normal/4-artifact retention is no longer recommended. Correct total is 117 methods / 197 logical cases; Format has 20 methods, and CompilePolicy's 1 method / 7 cases is included in Refactor integration. New owner per-case latency targets and daily-vs-delivery separation govern the current plan. No new test execution is claimed.

---

# Issue #594 測試分類工作筆記

固定 source：`41e4ebb8e716355ac86c4b39a8846e7b6711c1aa`；branch `codex/2026-11-08-dotnet-test-boundaries`。本文件屬指定新 workflow 的分析工作筆記。所有「改」、「移」、「合併」都是待選定的改善提案，沒有在本次執行。完整 Git-tracked bounded inventory 由兩個 Sol/medium 唯讀 worker 完成，TRX／Rider 紀錄由 Luna/medium 以確定性解析完成；parent 綜合取捨，不把委派設定當成後端 model／billing 身分證明。

## 來源、oracle 與分類讀法

- **R** = `tests/dotnet-refactoring`；行為來源 `src/tools/dotnet/refactoring/README.md`，資料列的 source／JSON／bytes 為明確 fixture。文件未承諾的精確錯誤順序、表示法及內部階段標成實作觀察，不能據此新增產品要求。
- **F** = `tests/dotnet-formatting`；來源 `src/tools/dotnet/formatting/README.md` 的輸入、選取、模式、支援環境與可觀察結果。
- **S** = `tests/dotnet-generation/snippet-tool`；來源 `src/knowledge/dotnet-backend/tooling/generation/snippet-tool/README.md` 與明確 shipped catalog／renderer 契約。
- **T** = `tests/dotnet-generation/templates`；來源 `src/knowledge/dotnet-backend/tooling/generation/README.md`、`DELIVERY.md` 及所述範例輸出。HTTP 的部分邊界值為現行範例的 characterization，並非下游產品規格。
- **K** = `src/knowledge/dotnet-backend/templates/domain-contracts`；來源該 README 與 `src/knowledge/dotnet-backend/standards/contract-cases.md`。範例 expected values 是範例契約；CT-005 固定外部原文在此回合未重新取得，原始契約精確對齊仍有限制。
- **SDK**：完整真實 SDK／workspace／程序；**Eval**：真實 SDK MSBuild 評估，可沒有 restore／workspace；**IP**：程序內真實 Roslyn／MSBuild，可能仍有局部 FS；**FS**：真實 filesystem／命令／wire；**U**：受控的單元邊界；**A**：選定發佈成品。這些是分析欄位，不新增七套專案或 runner。
- 「拒絕」須檢查所需的 stable code/status、exit 與 no-write，而非只有沒有例外。「snapshot」現有 R fixture 只看排除 obj/bin/artifacts 的 `.cs`；它不能單獨宣稱 project/import/plan 或所有磁碟 bytes 未變。
- 成本欄描述實際呼叫與已知量測。除成本表列出的數字外，未對每個候選另跑 timing；「低成本」只表示無 restore／SDK 子程序等已知工作，不是新 benchmark。

## 完整 Refactor 方法／資料列群組

R 共 72 方法、130 展開案例：integration 64／122，unit 3／3，artifact 5／5。integration 實際分成 SDK 37、IP 58、FS 25、受控 Stream unit 候選 2。

### R/integration/CompileInclusionTests.cs：3 方法／7 列

| 行／方法與資料列 | 主張與獨立 oracle | 邊界／成本、處置及損失 |
| --- | --- | --- |
| 13 `RejectsRulesThatCanExcludeOrImportTheNewFile`：`Compile Remove="ISelected.cs"` | authored Remove XML 應拒絕；無 output／plan，來源 bytes 保留 | 現為 SDK restore＋preview。建議 Eval Register→Require；保留完整 preview witness 對應 CLI mapping。若仍都是完整 preview，與 84 的 Remove 重複可合併。 |
| 同方法：`Import Project="Fake.nuget.g.targets"` | 真實匯入檔內 BeforeTargets=CoreCompile 要移除檔案，預期拒絕 | Eval 仍需真實 import graph／來源。這個 fixture 無假造 Exists package Import，不能宣稱已專門測完整 generated-NuGet origin 豁免。 |
| 同方法：`CustomBeforeMicrosoftCommonTargets` | 指向 Contracts/ISelected.cs 的 SDK hook，拒絕、bytes 保留 | 保留真實 SDK XML hook 發現／展開；不以測試硬填 importProperties 取代。 |
| 同方法：`DirectoryBuildTargetsPath` | Directory.Build.targets 路徑 hook 指向待產檔，拒絕 | 可 Eval；同一拒絕碼不證明具體走 hook override 或 import-match 哪一分支。 |
| 同方法：`_DirectoryBuildTargetsFile` | 間接 filename/search hook 指向 ISelected.cs，拒絕 | 可 Eval；間接搜尋語意與其他 hook 不同，保留資料列。 |
| 49 `OtherProjectLowercaseCompileGlobCanAlsoIncludeTheOutput`，1 | B 的小寫 compile glob 包含 A 待產檔，必須拒絕，無 plan/output、snapshot | 保留完整 SDK，手工 project graph 會失去 workspace 發現第二專案的證據。 |
| 84 `StableImportAllowsPreviewButExplicitCompileExclusionRefuses`，1／2 journeys | Bound.props 穩定匯入成功，明確 Remove 失敗；來源不寫入 | 保留完整 SDK witness。成功分支增 Plan.Inputs 中已知 Bound.props 路徑觀察，否則忽略匯入也可通過。可同一 restored project 分別選 allowed／Excluded.cs，但若主張需沒有 Remove 的正向組態，保留兩 fixture。 |

原 baseline `97ce2c6c4ef4e87e1866cd053d99d74d67578684:tests/dotnet-refactoring/native/CompileInclusionTests.cs` 已使用 `Register`、authored `LoadedWorkspace(new AdhocWorkspace(), sdkVersion)`／ProjectInfo 與 `Require`。現有入口不必產品新增 seam。它仍會真正 `ProjectCollection.LoadProject`、檢查 resolved imports、SDK XML hook、屬性展開、MSBuildGlob／GetAllGlobs；省略的是 restore／WorkspaceLoader／planner／apphost。

前置限制：CompilePolicy bootstrap 已在程序內註冊 build-time MSBuild；產品靜態 registeredSdkPath 與已載入 MSBuild assemblies 不能只靠版本字串視為一致。需在可執行指定 SDK 的 host 證明實際 physical assembly／resolver 路徑一致；其餘 host 的 raw XML 案例仍應可用原 build SDK。無法保證時保留 apphost，只做同完整路徑的重複合併。

### R/integration/CompilePolicyTests.cs：1 方法／7 列

| 行／方法與資料列 | 主張與 oracle | 邊界／處置 |
| --- | --- | --- |
| 21 `RejectsFileDependentCustomProjectXml`：Exists PropertyGroup、inactive Exists Import、Compile `@(IgnoredFiles)` Remove、Compile `@(Compile)` Condition、literal wildcard Import、property wildcard Import、custom BeforeTargets Target | 手寫 XML，穩定 `unsupported_compile_inclusion`，inactive XML 也應受檢查 | IP 真實 ProjectRootElement＋ValidateCustomProjectXml。保留 7 列；它們不證明 SDK hook discovery。與上面五列輸入不同，不能把其毫秒結果當相同案例的 before。 |

### R/integration/WorkspaceIntegrationTests.cs：13 方法／17 列

| 行／方法（列數） | 主張與獨立 oracle | 邊界／成本、處置 |
| --- | --- | --- |
| 8 `ExplicitFrameworkDoesNotAdmitMultiTargetProject` (1) | net10.0;net9.0 即使 request 指定 net10.0，仍 multiple_frameworks／無 plan | SDK evaluation，已無 restore；保留先評估完整 frameworks 的次序。 |
| 27 `ExplicitLinkedCompileItemIsRejected` (1) | 真實 Compile Link metadata 拒絕／無 plan／snapshot | SDK；不同於 design-time-only additions，保留。 |
| 58 `MissingProjectIsIdentifiedWhetherInSolutionOrReference` (2) | .slnx member／ProjectReference 兩來源，missing_file 並指向已知 Missing.csproj | reference 需 SDK item；solution 分支已無 restore。保留各自 discovery 與 CLI mapping。 |
| 100 `MissingCompileInputIsIdentifiedBeforePlan` (1) | 真實 Compile item Missing.cs 不存在，missing_file／無 plan | SDK 評估→檔案擷取；fake list 失去前者。 |
| 132 `AuthoredGeneratedSuffixCannotBeEditedThroughRelatedRename` (1) | Generated.g.cs override 不可改；接受明定拒絕碼集合／檔名、無 plan／snapshot | SDK loader→planner generated 分類，保留。將以 actual code 當 Refused(expected) 改為共同 refusal fields＋明確 allowlist；不強制未承諾的單一碼。 |
| 165 `ConditionalConfigurationAndImportedFrameworkAreReported` (1／2 journeys) | Directory.Build.props：Debug define 與 inactive limit；Release net10.0／CUSTOM、無 DEBUG | 保留一次 restore、兩次真實評估；改用既有 inspect 可省額外 Rename planning。limits 的精確字串表示屬現行觀察。 |
| 213 `ExternalSdkIntermediatesAreCapturedWithoutBeingEdited` (1) | 外部 AssemblyAttributes.cs 在 inputs，唯一 edit 是 authored source；Apply 成功 | SDK artifacts graph，保留。若宣稱 Apply 後 intermediate bytes 不變，需觀察它；SDK 可能再產生 intermediate，不能僅靠 source snapshot 擴大 no-write。 |
| 252 `BinAncestorOutsideProjectDoesNotMarkAuthoredSourceGenerated` (1) | 專案外 bin ancestor 不使 Service.cs 變 generated，唯一 edit 正確 | SDK loader 傳遞相對路徑；不為下移公開私有 GeneratedReason。 |
| 281 `VisualBasicSolutionMemberIsRejected` (1) | .vbproj solution member → unsupported_project／無 plan | 小型 FS solution discovery，已無 restore；保留現有邊界。 |
| 306 `ClassicSolutionFolderAndProjectEntryKeepCompilationGraph` (2) | B.csproj dependency 與 .sln solution-folder 兩入口均得 A/B 與 consumer 更新 | SDK；保留兩種 discovery。可用已知 A/B 路徑集合取代只有 Count=2。 |
| 348 `DesignTimeOnlySourceCannotSilentlyChangeTheEditableGraph` (2) | ../Shared.cs→linked_file；Extra.cs→unexpected_source；無 plan／snapshot | 真實 normal/design-time 差異，保留；不是 explicit Link 重複。 |
| 381 `DesignTimeAndBuildOnlyReferencesHaveDifferentMeaning` (2) | normal-only reference→incomplete_references；ReferenceOutputAssembly=false→成功且無 compilation reference | SDK graph，保留相反預期。 |
| 420 `PreviewJsonReportsBaselineErrorsSeparatelyFromNewErrors` (1) | Broken.cs 的 CS0246 與已知路徑在 baseline，無 new errors | 保留代表性 CLI JSON＋SDK；較小 Rename diagnostic 案例不證明 wire mapping。縮成單專案會失去跨專案傳遞，尚未選定。 |

### R/integration/ApplyIntegrationTests.cs：6 方法／9 列

| 行／方法（列數） | 主張與獨立 oracle | 邊界／成本、處置 |
| --- | --- | --- |
| 11 `RenameApplyRefusesChangesSincePreview` (3) | 未編輯 consumer bytes drift→input_drift；新增 glob member→plan_drift；forged-edit→plan_drift；保留已漂移後 snapshot | preview→mutate→fresh Apply 的 SDK journeys。前兩列各證明真實 input capture／重新評估；不能用人工 plan 完全代替。 |
| 45 `ExtractApplyRefusesOutputRaceOrForgedPlan` (2) | output-race→invalid_output，競爭內容保留；forged-create→plan_drift、仍無 output | SDK；preview 後新檔被 workspace 看見，與晚期 CreateNew race 不同。forged-edit/create 雖共用 recompute 比較，保守先留兩種 edit-kind。 |
| 77 `ReadOnlyConsumerRefusesBeforeAnySourceChange` (1) | 真正 Windows ReadOnly；全來源不變；現有只查 exit/sourceWrites 可能因錯誤原因拒絕而過 | 可改真實 FS InputLocks.Open＋獨立雙檔 plan、明確 unwritable_source／bytes；失去「preview／recompute 後遇 readonly」的單案例見證，需完整 Apply 留 wiring。 |
| 116 `CanonicalReadOnlyInputDetectsRetargetAndAcceptsFreshPreview` (1) | junction 同 bytes 換 physical root，舊 plan input_drift；新 plan 正確擷取另一 root，Apply 成功 | 保留 SDK AdditionalFiles＋junction＋fresh capture。若主張 Rename 完成，補 authored source 的 Fetch 觀察；目前 Applied() 是 JSON evidence。 |
| 170 `EditableCompileSourceJunctionIsRefused` (1) | SDK 真正把 junction 列為 editable Compile，linked_path／無 plan／snapshot | 保留 SDK→editable wiring；direct Capture 僅證明 guard。 |
| 200 `PreviewPlanCannotEnterLoadedProjectDirectory` (1) | plan 寫到 B/plan.json→unsafe_plan_path，無 plan／snapshot | 保留 workspace 發現 B 並保護全部 Projects 的接線。 |

### R/integration/PreflightTests.cs：4 方法／5 列

| 行／方法（列數） | 主張與 oracle | 邊界／處置 |
| --- | --- | --- |
| 10 `ExtractionApplyRefusesSourceDriftBeforeRecomputing` (1) | authored plan、BCL SHA-256，source drift→input_drift；無 recovery，plan/project/current source 不變，無 output | FS＋Program.Run；保留，已無 SDK／restore。 |
| 43 `ExclusiveSourceOrProjectHandleRefusesBeforeWrites` (2) | 真實鎖 source／project → apply_preflight_failed；資料／plan 保留 | Windows sharing 為實際主張，不能用 MemoryStream 取代。 |
| 65 `MissingCanonicalAdditionalFileRefusesBeforeWrites` (1) | 已記錄 physical input 被刪→apply_preflight_failed；不重建 alias／physical file | 真實 FS junction；保留。產品 canonical helper 是有效 setup，physical parent 另核對；SDK 發現由 Apply:116 負責。 |
| 99 `PlanDestinationJunctionIsRefusedBeforeLoadingTheRequest` (1) | plan alias/target 均未建立；linked_path 優先於刻意 missing request | FS＋命令 ordering；保留。精確優先順序是現行觀察，不擴張為未承諾全域順序。 |

### R/integration/CommandInputTests.cs：4 方法／17 列

| 行／方法（列數） | 主張與 oracle | 邊界／處置 |
| --- | --- | --- |
| 16 `InvalidRequestDoesNotWritePlan` (10) | missing、malformed、null、empty、workspace:null、unknown、duplicate、only-workspace、Extract empty-members、Extract renameOverloads；invalid_input／無 plan／來源不變 | 真實 JSON＋FS＋Program.Run，保留便宜獨立 partitions；現有 Data.Read(path) 無字串入口，不為移動新增產品 parser seam。 |
| 49 `RequestDirectoryIsNotAJsonFile` (2) | inspect／preview 讀真目錄→invalid_input，無 plan | 保留 FS 類型與兩個入口 mapping。 |
| 80 `InvalidPlanIsRefused` (3) | missing plan、inputs:[null]、inputs:[{path:x}]→invalid_input／no-write | Apply wire；missing 可和 Windows 內容列拆開，只在有實際分類價值時做。 |
| 106 `SourceAndSdkConfigurationNamesAreRefusedBeforePreview` (2) | .cs／既存 global.json 當目的地，unsafe_plan_path；source/config bytes 保留 | FS／命令早拒絕；保留。 |

### R/integration/EngineBoundaryTests.cs：3 方法／5 列

| 行／方法（列數） | 主張與 oracle | 邊界／處置 |
| --- | --- | --- |
| 10 `ConfigurationCannotInjectAnMsbuildProperty` (1) | Debug,DefineConstants=OTHER→typed invalid_configuration；project 文字不變 | SDK discovery 前的 FS guard，維持低成本現狀。 |
| 36 `MalformedSourceEncodingIsRefusedWithoutWrites` (1) | BOM＋0xff→lossy_encoding；原始 bytes 不變 | IP Roslyn＋真實 bytes；保留。 |
| 62 `ExtractionRefusesCompatibleGeneratorOutputOrFailure` (3) | emit-after、throw-after、throw-before→unsupported_generated_source；output原因或 CS8785/token，來源與 absence | 真實編譯 PE、AnalyzerFileReference／GeneratorDriver；保留 IP。before 的 SelectTarget 與 after 的 BuildPlan 階段各有意義。 |

### R/integration/RenameTests.cs：14 方法／24 列

下列均為真實 Roslyn planner／AdhocWorkspace 與局部 FS，沒有 SDK restore；成本優先級低。手寫 source／預期語意、byte 或 patch 是 oracle，不能用 planner 本身生成 expected。

| 行／方法（列數） | 主張與 oracle | 處置 |
| --- | --- | --- |
| 9 `OverloadGroupRequiresOptInAndUpdatesNameof` (1) | 未 opt-in ambiguous_nameof／bytes；opt-in 變更 overload 與 nameof | 保留真正 method-group binding 與政策正負對照。 |
| 55 `OptInDoesNotPullInOverloadsFromRelatedTypes` (2) | interface／derived selector 仍 ambiguous_nameof、consumer 訊息、bytes | 保留 declaring-type 關聯邊界。 |
| 91 `TypeRenameUpdatesDeclarationAndConsumer` (2) | class／interface declaration 和 consumer 的 authored token sequences | 保留不同 symbol kinds；必要時用 syntax/symbol 改善語意斷言。 |
| 118 `RenamesSelectedPropertyOrField` (2) | property→Value、field→Data，宣告與使用一致 | 保留。 |
| 142 `PositionRenamesParameterOrLocal` (3) | parameter／local／contextual keyword record；scope 正確、無 new errors | 保留；ValueText＋binding 比排版 regex 更適當。 |
| 183 `InvalidNamesSelectionsAndCollisionsProduceNoEdits` (5) | ambiguous ID、class、bad-name、Property、ToString 的指定拒絕與 bytes | 保留既有便宜 planner cases；不抽純 predicate 造成重複。 |
| 212 `PositionOutsideIdentifierAndOverloadGroupAreRefused` (1／2位置) | whitespace 拒絕允許碼集合、overload 群 ambiguous_symbol、bytes | 保留；沒有來源時不為一致性強制某一拒絕碼。 |
| 266 `RefusesOverrideOfFrameworkMember` (1) | metadata override→uneditable_symbol／bytes | 保留真實 metadata/override relation。 |
| 295 `BaselineDiagnosticsRemainVisibleIncludingMappedOffsets` (1) | 手寫兩個 missing type，仍兩個 CS0246、無 new errors | 保留；若名稱承諾 mapped offsets，需對具體 fixture 位置觀察，而非僅 ID＋count。 |
| 321 `BaselineErrorDoesNotHideNewLocalCollision` (1) | baseline error 不掩蓋新 collision；兩個允許 refusal code／bytes | 保留真實 compilation/scope。 |
| 344 `AliasAndGenericNameofPreserveSyntax` (2) | alias/global-qualified、open/closed generic nameof 語法、無 new errors | 保留語法形狀契約。 |
| 375 `PreservesBomAndNoFinalNewline` (1) | EF BB BF、無末 LF、patch marker | 保留 planner→bytes；可用完整 fixture 預期 bytes 加強最後一字元判定。 |
| 402 `CompactPatchOmitsDistantUnchangedContext` (1) | 手寫兩 hunk／added/removed、中間省略、Before bytes | 可用既有 internal Patch＋authored changes 降為純排版規則，但成本低且現有 planner wiring 有價值，後排。 |
| 436 `CrOnlySourceAndPatchAreByteExact` (1) | 完整 CR-only Before/After bytes 與 patch header/hunk/marker | 保留精確契約；僅 direct Patch 會失去 Rename 對 CR-only 規劃。 |

### R/integration/ExtractInterfaceTests.cs：9 方法／23 列

| 行／方法（列數） | 主張與 oracle | 邊界／處置 |
| --- | --- | --- |
| 9 `NullableGenericContractPreservesRefOutAndPrivateSetterBehavior` (1) | T:class／T?／getter-only／unmanaged／ref/out，獨立 consumer 得 True\|0\|abc\|3\|abc | IP planner＋另一 compilation/assembly consumer；保留語意與 no-write。 |
| 85 `ExactDeclaredMethodOrPropertyIsRequired` (3) | field、other owner、模糊 method ID 拒絕／bytes/absence | 保留 Roslyn selection。 |
| 115 `DuplicateMemberIdsAreRefused` (1) | duplicate property ID→invalid_members／bytes/absence | 保留，已便宜。 |
| 147 `InvalidInterfaceOrNamespaceIdentifierIsRefused` (2) | class／bad-name→invalid_name／bytes/absence | 可 direct Normalize，但會失去同列 no-write，無優先需要。 |
| 183 `InvalidOutputPathIsRefused` (6) | existing Service.cs、../Outside.cs、ADS-like payload.cs:stream.cs、CON.cs、COM¹.cs、obj/ISelected.cs→invalid_output | 保留存在／越界／路徑主張。冒號依 Path.GetInvalidFileNameChars 為 host-dependent，拆明 Windows 前提；CON/COM¹ 是產品顯式規則。未實跑 POSIX，不宣稱已觀察失敗。 |
| 222 `UnsupportedMemberShapesAreRefused` (6) | static、optional param、attribute、indexer、init、setter param attribute 拒絕 | 保留真實 syntax/symbol shape。 |
| 252 `DuplicateTypeWouldIntroduceCompilationErrors` (1) | 既有同名 type→new_compilation_errors，bytes/absence | 保留 compiler interaction。 |
| 284 `ExistingTypeAndNamespaceBindingsCannotChange` (2) | 新 interface/type 改變既有 imported/qualified lookup→name_collision | 保留跨 project reference 的 semantic binding／bytes。 |
| 316 `PrimaryConstructorAndMethodBodyArePreserved` (1) | exact短source只加 interface、consumer得7 | 保留 exact preservation＋真實 dispatch。 |

### R/integration/GeneratorIntegrationTests.cs：3 方法／4 列

| 行／方法（列數） | 主張與 oracle | 邊界／成本、處置 |
| --- | --- | --- |
| 12 `SdkGeneratorOutputBlocksExtractionButUnrelatedOutputAllowsRename` (1) | SDK generator 拒絕 Extract、允許 unrelated Rename；authored refs→Fetch，build B.dll | 保留真實 SDK generator discovery/build；同 restored fixture 的連續操作為有意義 journey。 |
| 71 `GeneratorReferenceAndDeclarationCannotBeEdited` (2) | generated reference→uneditable_reference；declaration→uneditable_symbol；無 plan／snapshot | 保留兩種來源。只在不可變 fixture 隔離成立時共用 setup，仍保留兩列結果。 |
| 107 `ExtractionRefusesAnalyzerBuiltAgainstNewerSdkRoslyn` (1) | 真實較新 SDK Roslyn built analyzer→unsupported_generated_source，DLL與ABI原因 | 保留真實 build／PE ABI／Analyzer discovery；compatible PE 不能替代。 |

### R FileApply：integration 4 方法／4 列，unit 3 方法／3 列

| 檔案／行／方法 | 主張與 oracle | 邊界／處置 |
| --- | --- | --- |
| integration/FileApplyTests.cs:8 `UnchangedInputDeniesOrdinaryWriterUntilHandlesClose` | 真實 sharing 拒普通 writer，AFTER! bytes，釋放後 released | FS 保留。Data.Hash/CanonicalFile 為建立有效 plan 的 setup，外部 writer／bytes 是獨立 oracle，不需另測 hash。 |
| 同檔:64 `CompetingCreatorOwnsOutputAndExistingSourceStaysOriginal` | CreateNew race，partial_failure；original與other-writer bytes保留 | FS 保留；與 preview 前 race 不同。 |
| 同檔:105 `CreateAcquisitionFailureDistinguishesEmptyAndUnattemptedOutputs` | original/created_empty/unknown/not_created、空 stream與handles關閉 | 已是 U 受控 stream／delegate；移到既有 unit，真實 CreateNew 由上一列保留。 |
| 同檔:143 `PartialNewFileRequiresRecoveryForCreatedFile` | applied/partial、partial bytes in、recovery說明無原檔不能還原空檔 | 已是 U，移 unit；斷言承諾的操作限制，不需要完整文案逐字相同。 |
| unit/FileApplyTests.cs:9 `ReportsWrittenPrefixAndUntouchedFilesAfterFailure` | applied/partial/original、AFfore／before bytes、recovery | U faulting stream，保留。 |
| 同檔:39 `UnreadableStateIsUnknown` | unknown且hash null | U，保留；不需模擬磁碟硬體故障。 |
| 同檔:63 `CloseFailurePreservesObservationsAndAttemptsEveryClose` | 全部close attempted、失敗檔unknown/null、保留prior applied/hash與其他檔 | U，保留。若主張保留原hash，與既有 observed hash 或BCL fixture hash比，NotNull只證明存在。 |

### R/artifact/PublishedArtifactTests.cs：5 方法／5 列

| 行／方法 | 主張與獨立 oracle | 邊界／處置 |
| --- | --- | --- |
| 13 `PublishedRenamePreservesCrossProjectSemanticsAndUnrelatedBytes` | 真實解壓apphost；interface/override/cref/nameof更新、overload/comment/string保留、CRLF、build | A＋SDK；保留。若宣稱 unrelated bytes，以對應fixture bytes觀察，不能只有泛稱成功。 |
| 77 `PublishedExtractionAppliesSelectedContractAndConsumerDispatches` | refactor-plan/1、create/modify、absence、preview no-write、project/consumer bytes；consumer 3\|7\|4 | A＋SDK＋跨assembly執行；保留wire／bytes與語意各自oracle。 |
| 165 `CallerSdkConfigurationDoesNotOverrideWorkspaceSdk` | caller99.0.100、workspace有效SDK，preview/plan取workspace | A＋CWD/global.json/SDK；保留。 |
| 191 `SdkPathsCanSelectLocalSdkWhenSameVersionExistsInHost` | 同version兩roots，實際CLI base path為local，Extract捕捉local Microsoft.Build.dll | A＋SDK＋junction；保留physical identity，不只version字串。 |
| 256 `ExtractedPackageIncludesRuntimeNoticesAndNoTestDependencies` | deps／實體必要檔案、README/notices/BuildHost/license與已知test families排除 | A inventory；保留但不宣稱涵蓋所有潛在封裝內容。 |

R helper coverage：SdkFixture/SdkCollection/CommandResult.Run、TestWorkspace/TestDirectory/SemanticWorkspace、TestProfiles、linked DotnetTestHost/PublishedExecutable、三 csproj、兩 slnx、refactoring-checks.yml 均已盤點。沒有把 helper 自動各配一份測試；只有被改動／確認缺陷才選驗證。

## 完整 Format 方法／資料列群組

F 有 unit6、request15（Windows12、macOS15）、SDK9、artifact2。Windows正常TRX為21P＋1個collapsed POSIX theory skip；macOS要求的24P與APFS成品案例屬另一host驗收，這次未執行。

| 路徑／行／方法（列數） | 行為與獨立 oracle | 邊界／成本、處置 |
| --- | --- | --- |
| unit/CleanupRulesTests.cs:14 `Should_reject_unsupported_cleanup_when_validating_the_request` (6) | missing diagnostics/severity、unknown style、wrong mode/ID、CA1040無fixer、forbidden whitespace→specified codes | U typed Request/Rules.Validate；保留partitions，compact typed assertion僅依選定GWT形式。 |
| RequestTests.cs:21 `InvalidJsonFailsWithoutSdkOrSourceChanges` (5) | unknown/type/duplicate/malformed/null→invalid-request、無commands、bytes不變 | FS＋wire parser；保留，typed Request不能證明wire。 |
| 同檔:52 `Should_report_no_fixer_without_sdk_commands_when_submitting_ca1040` (1) | no-fixer failure envelope、無SDK command | FS／in-process command；保留unit規則到CLI的代表性mapping。 |
| 同檔:77 `EmptySelectionFailsBeforeSdk` (1) | invalid-request、無commands/writes | 保留便宜獨立partition；若一致setup可合成Theory但不掉身份。 |
| 同檔:103 `MissingFileAndDirectorySelectionsFailBeforeSdk` (2) | missing file／existing directory→invalid-selection、無commands/writes | FS；directory現名無.cs，可能只撞extension guard。改.cs結尾真目錄以測所稱行為。 |
| 同檔:130 `MissingWorkspaceFailsBeforeSdk` (1) | 已知不存在workspace→load-failed、無commands | FS；保留。 |
| 同檔:153 `Should_refuse_cleanup_when_the_solution_maps_debug_to_release` (1) | mapped .sln→unsupported-cleanup-workspace、無commands | FS；產品在extension拒絕而非評估mapping，名稱應說明它是unsupported solution例子。 |
| 同檔:195 `Should_preserve_the_linked_source_when_it_is_outside_the_workspace` (1) | parent-relative file→unsupported-selection、bytes不變 | FS，無evaluated MSBuild；保留，正向enclosing solution另有SDK witness。 |
| 同檔:230 `PosixLiteralGlobAndSeparatorNamesFailBeforeSdk` (3) | literal *,?及backslash拒絕；selected／可能匹配siblings保留 | 真實macOS filename；保留。WildcardOther.cs不匹配Wildcard?.cs，?row旁檔改成實際單字元匹配者。 |
| SdkTests.cs:24 `ExistingFileOutsideCompileItemsIsRefused` (1) | 真正Compile Remove→unmatched-selection、無writes | SDK restore＋evaluated items；保留，raw XML不能證明接線。 |
| 同檔:49 `MalformedProjectCannotLoad` (1) | invalid XML→load-failed | SDK child load，已無restore；可合併唯需明認放棄該specific child witness，不新增parser只為省這列。 |
| 同檔:71 `DesignTimeFailureReportsObservedSourceChanges` (1／2calls) | failing target有／無source side effect，load-failed、bytes/changed-file/diagnostics | SDK一次restore兩次load，保留兩情形；增fixture-authored changed bytes與report一致性。 |
| 同檔:132 `SlnxAndEditorConfigGeneratedSelectionsAreUnreportedAndUnchanged` (1／2calls) | slnx generated/g.cs/config保留；classic sln含folder仍find authored change | SDK，一restore兩wrapper；保留兩入口與真正formatter acceptance。 |
| 同檔:185 `ResponsePrefixAndLinkedPathsRemainLiteral` (1／2journeys) | @file非response expansion；enclosing slnx可選linked file，selected-only writes | SDK；保留。@Linked組合不取代@Excluded crafted response trap；強化對所稱selected/sibling bytes的觀察。 |
| 同檔:244 `StyleHonorsSeverityAndRecheckIsClean` (1／4wrapper calls) | IDE0008 warning在error忽略、warn報告且check不寫、applyfix、unselected保留 | SDK，保存約44s。若無fresh-invocation idempotence要求，可移除apply內recheck之後額外check；需先承認少掉該獨立主張。型別用C#結構而非偶然spacing。 |
| 同檔:316 `AnalyzerAppliesRequestedFixWithoutStyleChanges` (1／2journeys) | CA1805去initializer但var保留、check bytes不寫、無remaining/unselected writes | SDK，保存約28s。與IDE0008不同mode不可合併；語法結構適合。 |
| 同檔:369 `SemanticFailureDoesNotReportClean` (1) | missing type→semantic-prerequisite-failed、bytes不變 | SDK compiler；保留，與XML/loadfailure不同。 |
| GeneratorConsentTests.cs:11 `GeneratorExecutesOnlyAfterConsentInBothDesignTimeContexts` (1／6calls) | ordinary／formatter-only需consent；markup/mapped-reference拒絕且marker未產生 | SDK真實generator DLL與project，保存約38s；marker是獨立執行oracle。保留各context，共用一次DLL建置在同scenario內。 |
| artifact/PublishedFormatTests.cs:11 `PublishedExecutableChecksAndAppliesNestedEditorConfigToSelectedBytesOnly` (1) | 真成品、compact/verbose schema、SDK、nested indent、check/apply/clean、nonselected bytes | A＋SDK一restore四calls；保留代表性，精確只比契約欄位／設定indent。 |
| 同檔:108 `CaseAliasOnCaseSensitiveVolumeIsRejectedBeforeFormatter` (1) | real case-sensitive volume雙Compile identity→unsupported-selection、兩檔bytes保留 | A macOS arm64/APFS＋SDK；保留實際OS互動。fake comparer不能代替。 |

F helpers：FormatFixture unpinned為Program.Run、pinned為child dotnet FormatTool.dll；case-local trees；child-only MSBuildSDKsPath清除；FormatArtifactProfile missing能力／錯選root／probe fault分開；SDK collection序列。未證明可共享mutable restored project。

## 完整 Snippet 方法／資料列群組

S 有 unit8、IP/FS integration14、artifact2。來源精確renderer bytes／機器ID應保留，不因「字串」一概改弱。

| 路徑／行／方法（列數） | 行為與獨立 oracle | 邊界／處置 |
| --- | --- | --- |
| unit/ExpansionTests.cs:12 `Should_reject_invalid_parameter_inputs_when_rendering` (4) | missing/unknown、reserved identifier、unlisted enum→fixed codes | U，保留Theory。 |
| 同檔:42 `Should_reject_unknown_or_malformed_placeholders_when_parsing_the_body` (2) | undeclared/malformed placeholders的不同codes | U，保留。 |
| 同檔:58 `Should_reject_an_unknown_kind_when_validating_a_parameter_definition` (1) | script kind→invalid-catalog | U compact exception可表達；catalog integration另測呼叫接線。 |
| 同檔:69 `Should_preserve_unicode_and_literal_placeholders_when_expanding_with_indent_and_crlf` (1) | authored exact CRLF/indent/blank/Unicode/escaped literal text | U，保留精確比對，文字本身即結果。 |
| SnippetTests.cs:20 `BuiltInCatalogListsSearchesAndInspectsWithoutAChildProcess` (1／list/search/inspect) | shipped sorted IDs、GUARD search、interface context/usings/default/source/body | FS realcatalog＋command；各action oracle保留，若讀性需要可分便宜案例。不能從同catalog反算expected inventory。 |
| 同檔:58 `BuiltInFragmentsUseTypedParametersAndDefaults` (1) | authored enum return/default/indent/LF text | FS asset＋renderer；保留文本/default mapping，compile witness不同。 |
| 同檔:77 `BuiltInStringGuardUsesTheNamedParameter` (1) | label／indent／LF正確 | FS realasset；整fragment目前固定API拼法。如允許equivalent guard，交由compiled consumer證明例外/參數，renderer精確契約仍留。 |
| 同檔:99 `InvalidRequestPreservesFailureEnvelope` (5) | missing param/unknown/duplicate/schema/missingcatalog→exit1 stderr code、stdout empty | FS＋wire；保留便宜partitions。 |
| 同檔:117 `CustomMetadataIsLazyAndMissingOrEmptyBodiesHaveDistinctErrors` (1／多action) | metadata操作不需body，inspect分missing/empty，custom不fallbackbuilt-in | FS realcatalog/body；保留所有主張，觸碰時才為可讀性拆分。 |
| 同檔:155 `Should_use_the_selected_source_when_rendering_and_reject_invalid_inspection` (1) | custom source/rendered CRLF prefix與malformed inspection拒絕 | FS＋command，保留source selection與inspect wiring；低層expand已有U。 |
| 同檔:187 `InvalidCatalogDoesNotList` (3) | schema、duplicate ID、invalid kind→specified codes | FS JSON；保留，kind列證明載入有呼叫validation。 |
| GeneratedFragmentTests.cs:14 `Should_retain_the_rendered_fragment_contracts_when_compiled_in_a_consumer` (1) | 真render＋C#14 warnings-as-errors compile；guard exception/param、cancellation、constructor identity、GUID、Unicode、replay/commit | IP realRoslyn emit＋collectible ALC／typed probes；保留一次compile多個明確結果。Reflection只綁consumer method，非產品shape oracle。 |
| artifact/PublishedSnippetTests.cs:12 `PublishedExecutableFindsItsBundledCatalogFromAnotherDirectory` (1) | 真nativeexe在異CWD找adjacentcatalog；IDs／schema envelope／launch/version | A；保留。nonblank version只算smoke。 |
| 同檔:68 `PublishedExecutableRejectsFifoWithoutOpeningIt` (1) | realFIFO→invalid-body且限時返回 | A Linux x64＋mkfifo；保留，觀察是timely refusal，不聲稱syscall trace。local missing能力可skip，requiredCI必須執行。 |

S helpers：GenerationFixture/SnippetTestSupport、reference assemblies via PreserveCompilationReferences、artifact TestProfiles／native header input admission。一般renderedconsumer使用真SDKreference assemblies但無dotnet child，不能稱SDK process case。部分Snippet Given僅文字label而distinguishing input在When；後續調整應把inputs綁回具名Given，不用大量包裝衡量品質。

## Native templates 與獨立知識範本

| 路徑／行／方法 | 來源／oracle | 邊界／成本、處置 |
| --- | --- | --- |
| T/TemplateTests.cs:7 `NativeTemplatesGenerateBuildAndServeBothApiShapesAndPreserveEdits` | 五ID/namespace、dry-run無目錄、typed items consumer、customization marker、四project graph、兩種app各HTTP、collision保留user bytes、uninstall | SDK source registration、isolatedhive、兩build與兩loopbackKestrel。保存case26.06s。保留正常capableRunAll。HTTP細節中部分為現行範例characterization。 |
| T/artifact/PublishedTemplateTests.cs:9 `PackedTemplatesGenerateBuildAndServeBothApiShapesAndPreserveEdits` | direct nupkg ID install/generate/uninstall；extracted content為另一documented registration path且實際consumer可用 | A＋SDK。direct branch目前只產生class/customnamespace，完整旅程在extractedcontent。若縮減須保留兩registration與真payload representative build/HTTP；不能拿packglob當產物可用。正常RunAll不包含此project，降低它不改善正常RunAll。 |
| K/package-free/PackageFreeContractTests.cs:11 `ReplayRestoresCommittedStateAndOnlyNewFactsRemainPendingUntilConfirmation` | 範例2+3→5/revision2/no pending，新fact到確認version3才clear | generated純範例；保留。觸碰時可補newtotal/payload使pending主張具體。 |
| 同檔:53 `CompletePlanHistoryRestoresRequiredNestedState` | Plan/Project/Task facts→nestedtask/version3/nopending | 純範例，保留。 |
| 同檔:82 `EmptyPlanHistoryCannotReturnAnAggregate` | 空history exactexception | 純範例compact Assert.Throws，保留。 |
| 同檔:86 `TaskCreationWithoutItsProjectCannotReturnAnAggregate` | 缺parent拒絕 | 純範例，保留distinct state。 |
| 同檔:93 `TaskUpdateWithoutItsTaskCannotReturnAnAggregate` | 缺task拒絕 | 純範例，可清楚Theory表達但不能丟state區別。 |
| 同檔:100 `UnsupportedPlanFactCannotBeSilentlyIgnored` | unknownfact→NotSupportedException | 純範例，保留。 |
| K/published-ct005/PublishedContractTests.cs:9 `LoadingHistoryRestoresStateWithoutPendingEventsAndCannotRepeat` | typed externalDLL：arithmetic committedstate/no pending、clear/reload拒絕 | 選定外部DLL的IP integration；保留，原始外部契約未重新核對，不聲稱已執行／採納。 |
| 同檔:46 `PendingBatchSurvivesRejectedOrUnconfirmedAppendAndClearsOnConfirmation` | payload/identity/revision跨wrong-confirmation保留，correct-confirmation advance/clear | 真external object，保留有action的前後結果；僅copy同reference再讀而中間無action的assert可移除。 |
| 同檔:103 `FailedReplayRejectsFurtherOperationsOnTheSameInstance` | unsupported replay後change/commit/reload拒絕 | 真external lifecycle，保留；與packagefree constructor failure不同。 |

T/TemplateScenario.cs 主要階段：15 entry、76 directpackage、106 directorydiscovery、125 dryrun/build、248 graph、268 HTTP、319 response oracle。HTTP harness限定fixture loopback、不跟任意Location並另驗證Location。改WebApplicationFactory會失去standalone generated build/start主張，非本次推薦。

K 14個C#是inert template inputs；`.csproj.template`由原生dotnet-new命名。6例的生成可用性與3個externalDLL例子的選用執行分開；「package-free」只指無domain dependencies，生成測試仍restore xUnit/BDDfy。現行CT005無reflection/source-text assertions，不能沿用對更舊案例的描述。

## 共用能力、CI、完整性

DotnetTestHost 的 SDK/runtime inventory 每linked assembly/host cached，missing能力與command/parse/access fault分開。child-only清除MSBuildSDKsPath；不是修改全域env。PublishedExecutable校驗輸入filename/nativeheader，真正launch是另一觀察。沒有證據支持新增通用runner、能力registry或所有helper單獨一套測試。

現有 `Assert-ExecutedTests.ps1` gate 看total/executed/passed；搬動或合併時更新受影響的既有counts與host/trait，保留must-run要求。相關來源：`.github/workflows/{refactoring-checks,formatting-checks,native-tools,dotnet-knowledge-templates}.yml`，兩個 `.slnx`。原生工具7一般testprojects、4獨立artifactprojects；K不在其中。

盤點使用graph-first；graph總metadata沒有可證明的GitSHA，Snippet Program有partial parse，所以完整性依固定HEAD的bounded Git-tracked inventory／source readback，未以搜尋無結果推論缺席。Refactor關鍵CompileInclusion/WorkspaceLoader/Program graph文字與HEAD核對一致；其餘直接以固定tree計數。此為靜態盤點，不宣稱runtime／hosted acceptance。

## 保存 TRX 與效能證據（已重新解析，沒有重新執行）

F-drive根目錄為 `F:/tmp/dotnet-test-boundaries-20261108`。初始sandbox讀取拒絕後，經限定同路徑的read-only escalation成功；沒有移動證據、改TEMP或執行測試。此root是易失性證據，以下有用摘要保存在SQLite，原檔存在不保證日後仍在。

| 相對結果路徑 | P／NotExecuted／F | 案例duration加總 | TRX Times最早start到最晚finish |
| --- | --- | --- | --- |
| default | 107／49／0 | 未以加總作比較 | 11.710s |
| default-final-clean/results | 134／45／0 | 未以加總作比較 | 14.422s |
| runall-capability/default-results | 175／1／0 | 560.66s | 354.734s |
| runall-capability/artifact-results | 8／2／0 | 139.04s | 85.003s |
| runall-capability/artifact-missing-results | 0／2／8 | 1.37s | 2.511s；預期失敗路徑，不算通過 |

default-results 的實際 testcase start→end區間為353.674s，與TRX suite Times區間354.734s不同；兩者都不是duration加總。結果依UnitTestResult，而非容易誤讀的notExecuted counter。七assembly為FormatUnit6P、RefactorUnit3P、SnippetUnit8P、SnippetIntegration14P、FormatIntegration21P1skip、RefactorIntegration122P、Template1P。唯一skip是 **FormatTool.IntegrationTests.RequestTests.PosixLiteralGlobAndSeparatorNamesFailBeforeSdk**；初期worker訊息誤標Refactor，已用TRX UnitTest/codeBase關聯修正，本文件採修正值。

| 47 SDK案例分組 | 列數 | duration加總 |
| --- | --- | --- |
| Refactor Apply | 9 | 124.01s |
| Refactor Workspace | 17 | 112.05s |
| Refactor CompileInclusion | 7 | 64.87s |
| Refactor GeneratorIntegration | 4 | 52.14s |
| Format SdkTests | 8 | 121.45s |
| Format GeneratorConsent | 1 | 38.26s |
| Source Template | 1 | 26.06s |
| SDK合計 | 47 | 538.84s／560.66s＝96.1% |

其餘129個reported rows含1skip，duration合計21.82s。資料可排序調查優先級，不能用它預測並行後耗時或推論各步驟因果。

五列CompileInclusion的 **相同輸入** 在三個TRX存在：historical `windows-refactoring/results/sdk-artifact.trx`；selected `refactor-necessity/results/sdk-selected.trx`；automatic `runall-capability/default-results` 的Refactor TRX。

| 輸入 | historical秒 | selected秒 | automatic秒 |
| --- | --- | --- | --- |
| DirectoryBuildTargetsPath | 1.0146 | 7.4758 | 7.6071 |
| _DirectoryBuildTargetsFile | 1.2778 | 7.5304 | 7.5026 |
| Compile Remove=ISelected.cs | 1.4022 | 7.7995 | 7.8022 |
| CustomBeforeMicrosoftCommonTargets | 1.0617 | 7.5822 | 7.5992 |
| Fake.nuget.g.targets | 1.2683 | 7.9507 | 8.0815 |
| 合計 | 6.0246321 | 38.3387 | 38.5926 |

Source比較證明前者直接SDK評估、後者新增restore/fullpreview邊界；elapsed同時受build/runner/cache/競爭差異影響，仍非控制變因benchmark。`refactor-necessity/results/final-boundaries.trx` 的七個CompilePolicy rawXML輸入不同，不能冒充相同五列的before。

automatic default suite為11:47:10.090–11:53:04.824（+08）；artifact為11:48:54.582–11:50:19.585，明確重疊。過往三組default也執行不同cases，不能以11.7→354.7聲稱同工作突然慢30倍。第一版已預設執行RefactorSDK。

詳細default TRX basename前綴 `YuChia_佑嘉的AMD桌機_2026-11-08_`，11_47_11_net10.0.trx及[1]..[4]依序FormatUnit、RefactorUnit、SnippetUnit、SnippetIntegration、FormatIntegration；11_47_12為Refactor；11_47_37為Template。default舊檔為`default/default_net10.0_20261108082723.trx`至`...082734.trx`；其餘結果依上列明確資料夾保留。

Rider唯讀紀錄 `C:/Users/h4227/AppData/Local/JetBrains/Rider2026.2/log/backend.2026-11-07_2309.18392.log`：first session launch12:02:39.438／run12:02:42.949；second created12:03:09.732／run12:03:12.359，互相重疊。12:05:12.487僅first sub-run完成；second在12:06:09.528開始Refactor。socket abort不是完整suite完成證據，也不拿它推定使用者取消的確切時間。沿用交接觀察Format→Snippet→Template→Refactor序列／build約3s；未獨立重新歸因各project總時間。User已取消，原因與完整完成時間未知，這次沒重啟。

所有保存測試結果延續 predecessor 的原build歸屬；9efca67b/41e4ebb8後續narrow修正不能把早先長run重標成final-head fullsuite。知識生成6pass、closure4pass、CT005 refusal，以及distribution186中2hardlink環境失敗後2targeted pass，也維持原摘要與限制，並非這次新驗收。

## 設計結論與驗證界線

主要方案詳plan.md：既有直接SDK評估seam優先；FileApply兩U候選移動及具體oracle/平台修正；Format額外freshcheck先決定是否承擔idempotence；Workspace inspect與readonly seam作後續獨立選項；artifact與並行不混入正常RunAll效能承諾。

本次可證明的是靜態完整盤點與既有紀錄的確定性重讀。沒有證明新的測試通過、MSBuildLocator切換可行性、POSIX ADS目前實跑失敗、Rider完整時間、CT005外部語意精確對齊或未來節省量。分析已可供選定實作；這些未驗證內容在對應小slice內驗證，不觸發整套矩陣重跑。
