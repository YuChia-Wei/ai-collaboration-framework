# RefactorTool tests

Run the two test projects directly or through
[`AICF.Dotnet.Tools.slnx`](../../src/tools/dotnet/AICF.Dotnet.Tools.slnx).

```powershell
dotnet test tests/dotnet-refactoring/unit/RefactorTool.UnitTests.csproj -c Release
dotnet test tests/dotnet-refactoring/integration/RefactorTool.IntegrationTests.csproj -c Release
```

Set `AICF_REFACTOR_SDK_TESTS=1` on Windows x64 with SDK 10.0.403 to
exercise real MSBuild and SDK-backed preview and apply. The junction cases
also require `pwsh`. The SDK fixture uses local SDK reference packs and an
empty package source. Set `AICF_TEST_WORK` for a disposable fixture root.

To exercise an extracted publication artifact, publish with
[`Publish-RefactorTool.ps1`](../../src/tools/dotnet/refactoring/Publish-RefactorTool.ps1)
and extract the ZIP outside the checkout. Set `AICF_REFACTOR_TEST_ARTIFACT` to
the absolute path to the extracted `RefactorTool.exe`.

```powershell
$env:AICF_REFACTOR_SDK_TESTS = '1'
$env:AICF_REFACTOR_TEST_ARTIFACT = 'F:/scratch/refactor-extracted/RefactorTool.exe'
dotnet test tests/dotnet-refactoring/integration/RefactorTool.IntegrationTests.csproj -c Release
```

Use `Boundary=Sdk` or `Boundary=Artifact` for a selected integration subset.
An unset artifact selection skips those cases during discovery. An explicit
artifact selection requires the real win-x64 executable. CI sets both profiles
and checks the required case counts in the native test reports.

## Test boundaries

| Behavior | Smallest selected boundary | Additional evidence in selected profiles |
| --- | --- | --- |
| Write and close failure observations | Three unit cases use injected streams | The file integration cases exercise real directory checks, exclusive create and Windows sharing |
| Apply preflight and plan destination | Windows integration calls the real command entry with authored plan inputs, independent hashes and real handles or junctions | SDK cases prove that preview captures unedited inputs, retargeted AdditionalFiles can be captured by a new preview, and recomputation rejects stale or forged plans |
| Rename and Extract Interface semantics | Real Roslyn workspace and planner with authored source bytes. A compiled analyzer PE drives the real generator checks for compatible generators. | SDK cases prove actual Analyzer and generated document discovery, generated references and declarations, and rejection of a newer SDK Roslyn ABI |
| Workspace and Compile rules | Direct workspace validation rejects configuration injection before SDK selection. The real MSBuild XML parser and custom policy handle raw rule text. | SDK cases evaluate actual Compile globs and imported roots, preserve stable imports, and resolve SDK extension hooks and origin |
| Extracted executable | Windows artifact integration exercises archive inventory and product CLI execution | Cross-project preview and apply, caller and workspace SDK selection, and SDK roots with the same version |

`Boundary=Preflight` selects Windows apply and destination validation without
an SDK restore or RefactorTool child process. Its junction fixtures require
`pwsh`. `Boundary=InProcess` selects the focused planner and MSBuild XML
cases. The XML cases use the MSBuild installation that built the test
assembly. They parse actual project elements from strings. The retained
SDK cases run the tool's apphost so its own SDK selection remains isolated.

## Previous acceptance scenario mapping

The numbers are the order of the 64 test methods in the previous
`accept_refactoring.py` at commit `f5f4b4311f9eb47356a10b12e4db5422c22f4ed4`.
Theory rows retain independent expected outcomes. At the semantic boundary,
refusal is a typed failure with authored bytes preserved. Command-backed
refusals also assert the JSON status, code, source-write flag, and absent
preview plan where applicable.

| Previous scenario | Native test or theory |
| --- | --- |
| 01 Selected extraction and consumers | `PublishedArtifactTests.PublishedExtractionAppliesSelectedContractAndConsumerDispatches` |
| 02 Nullable generics, ref/out and private setter | `ExtractInterfaceTests.NullableGenericContractPreservesRefOutAndPrivateSetterBehavior` |
| 03 Invalid members, output, compile exclusion | `ExtractInterfaceTests.ExactDeclaredMethodOrPropertyIsRequired`, `DuplicateMemberIdsAreRefused`, `InvalidInterfaceOrNamespaceIdentifierIsRefused`, `InvalidOutputPathIsRefused`, extraction rows in `CommandInputTests.InvalidRequestDoesNotWritePlan`, and `CompileInclusionTests.StableImportAllowsPreviewButExplicitCompileExclusionRefuses` |
| 04 Extract output race, changed input, forged plan | `ApplyIntegrationTests.ExtractApplyRefusesOutputRaceOrForgedPlan` and `PreflightTests.ExtractionApplyRefusesSourceDriftBeforeRecomputing` |
| 05 Unsupported members and visibility collision | `ExtractInterfaceTests.UnsupportedMemberShapesAreRefused` and `DuplicateTypeWouldIntroduceCompilationErrors` |
| 06 File-dependent inclusion and invalid Windows paths | `CompilePolicyTests.RejectsFileDependentCustomProjectXml`, `CompileInclusionTests.RejectsRulesThatCanExcludeOrImportTheNewFile` and `ExtractInterfaceTests.InvalidOutputPathIsRefused` |
| 07 Inactive import, item expressions, target rules, lower-case Compile glob | `CompilePolicyTests.RejectsFileDependentCustomProjectXml` and `CompileInclusionTests.OtherProjectLowercaseCompileGlobCanAlsoIncludeTheOutput` |
| 08 Type and namespace rebinding | `ExtractInterfaceTests.ExistingTypeAndNamespaceBindingsCannotChange` |
| 09 Future imports, SDK hooks, stable positive | `CompilePolicyTests.RejectsFileDependentCustomProjectXml`, `CompileInclusionTests.RejectsRulesThatCanExcludeOrImportTheNewFile` and `StableImportAllowsPreviewButExplicitCompileExclusionRefuses` |
| 10 Primary constructor and setter parameter attribute | `ExtractInterfaceTests.PrimaryConstructorAndMethodBodyArePreserved` and `UnsupportedMemberShapesAreRefused` |
| 11 Duplicate SDK version under two roots | `PublishedArtifactTests.SdkPathsCanSelectLocalSdkWhenSameVersionExistsInHost` |
| 12 Cross-project rename with related members, cref, nameof, build | `PublishedArtifactTests.PublishedRenamePreservesCrossProjectSemanticsAndUnrelatedBytes` |
| 13–14 Selected overload group and related-type exclusions | `RenameTests.OverloadGroupRequiresOptInAndUpdatesNameof` and `OptInDoesNotPullInOverloadsFromRelatedTypes` |
| 15–16 Type, interface, property, field, parameter and local | `RenameTests.TypeRenameUpdatesDeclarationAndConsumer`, `RenamesSelectedPropertyOrField`, and `PositionRenamesParameterOrLocal` |
| 17 Invalid name, documentation ID and position | `RenameTests.InvalidNamesSelectionsAndCollisionsProduceNoEdits` and `PositionOutsideIdentifierAndOverloadGroupAreRefused` |
| 18 Invalid requests | `CommandInputTests.InvalidRequestDoesNotWritePlan` |
| 19 Contextual keyword | `RenameTests.PositionRenamesParameterOrLocal` |
| 20–21 Request directory, invalid plan | `CommandInputTests.RequestDirectoryIsNotAJsonFile` and `InvalidPlanIsRefused` |
| 22 Existing name collision | `RenameTests.InvalidNamesSelectionsAndCollisionsProduceNoEdits` |
| 23–25 Unmodified-input drift, new glob member, tampered edit | `ApplyIntegrationTests.RenameApplyRefusesChangesSincePreview` |
| 26–27 Multi-target and linked source | `WorkspaceIntegrationTests.ExplicitFrameworkDoesNotAdmitMultiTargetProject` and `ExplicitLinkedCompileItemIsRejected` |
| 28–30 Missing reference, project, and compile input | `WorkspaceIntegrationTests.MissingProjectIsIdentifiedWhetherInSolutionOrReference` and `MissingCompileInputIsIdentifiedBeforePlan` |
| 31 Related generated suffix source | `WorkspaceIntegrationTests.AuthoredGeneratedSuffixCannotBeEditedThroughRelatedRename` |
| 32 External override | `RenameTests.RefusesOverrideOfFrameworkMember` |
| 33, 36 Existing and offset-mapped diagnostics | `WorkspaceIntegrationTests.PreviewJsonReportsBaselineErrorsSeparatelyFromNewErrors` and `RenameTests.BaselineDiagnosticsRemainVisibleIncludingMappedOffsets` |
| 34, 48 Explicit conditional configuration and imported framework | `WorkspaceIntegrationTests.ConditionalConfigurationAndImportedFrameworkAreReported` |
| 35 Existing diagnostic versus new collision | `RenameTests.BaselineErrorDoesNotHideNewLocalCollision` |
| 37 Unrelated SDK-generated output | `GeneratorIntegrationTests.SdkGeneratorOutputBlocksExtractionButUnrelatedOutputAllowsRename` |
| 38 Activated, failing, and ABI-incompatible generators | `EngineBoundaryTests.ExtractionRefusesCompatibleGeneratorOutputOrFailure` and `GeneratorIntegrationTests.ExtractionRefusesAnalyzerBuiltAgainstNewerSdkRoslyn` |
| 39 Generated reference and declaration | `GeneratorIntegrationTests.GeneratorReferenceAndDeclarationCannotBeEdited` |
| 40–41 External intermediates and bin ancestor | `WorkspaceIntegrationTests.ExternalSdkIntermediatesAreCapturedWithoutBeingEdited` and `BinAncestorOutsideProjectDoesNotMarkAuthoredSourceGenerated` |
| 42, 44 Canonical input retarget and removal | `ApplyIntegrationTests.CanonicalReadOnlyInputDetectsRetargetAndAcceptsFreshPreview` and `PreflightTests.MissingCanonicalAdditionalFileRefusesBeforeWrites` |
| 43 Editable and plan junctions | `PreflightTests.PlanDestinationJunctionIsRefusedBeforeLoadingTheRequest` and `ApplyIntegrationTests.EditableCompileSourceJunctionIsRefused` |
| 45 Exclusive edited or unedited input handle | `PreflightTests.ExclusiveSourceOrProjectHandleRefusesBeforeWrites` |
| 46 Non-C# solution member | `WorkspaceIntegrationTests.VisualBasicSolutionMemberIsRejected` |
| 47 Read-only reference | `ApplyIntegrationTests.ReadOnlyConsumerRefusesBeforeAnySourceChange` |
| 49, 57 Classic solution folder and project entry graph | `WorkspaceIntegrationTests.ClassicSolutionFolderAndProjectEntryKeepCompilationGraph` |
| 50–52 BOM, missing final newline, compact hunks, CR-only patch | `RenameTests.PreservesBomAndNoFinalNewline`, `CompactPatchOmitsDistantUnchangedContext`, and `CrOnlySourceAndPatchAreByteExact` |
| 53 Ambiguous overload position | `RenameTests.PositionOutsideIdentifierAndOverloadGroupAreRefused` |
| 54 Inherited name collision | `RenameTests.InvalidNamesSelectionsAndCollisionsProduceNoEdits` |
| 55 Configuration injection | `EngineBoundaryTests.ConfigurationCannotInjectAnMsbuildProperty` |
| 56 Caller directory with incompatible SDK | `PublishedArtifactTests.CallerSdkConfigurationDoesNotOverrideWorkspaceSdk` |
| 58–59 Design-time linked or unexpected sources | `WorkspaceIntegrationTests.DesignTimeOnlySourceCannotSilentlyChangeTheEditableGraph` |
| 60–61 Design-time missing edge and build-only reference | `WorkspaceIntegrationTests.DesignTimeAndBuildOnlyReferencesHaveDifferentMeaning` |
| 62 Malformed source encoding | `EngineBoundaryTests.MalformedSourceEncodingIsRefusedWithoutWrites` |
| 63 Alias and generic nameof syntax | `RenameTests.AliasAndGenericNameofPreserveSyntax` |
| 64 Unsafe source, project-local and SDK configuration plan paths | `CommandInputTests.SourceAndSdkConfigurationNamesAreRefusedBeforePreview` and `ApplyIntegrationTests.PreviewPlanCannotEnterLoadedProjectDirectory` |
| I/O runner | `FileApplyTests` covers partial and unknown states, all close attempts and prior observations, unchanged-input sharing, exclusive create race, empty and unattempted outputs, and recovery for a partial new file. |
