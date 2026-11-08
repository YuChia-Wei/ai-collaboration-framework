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

- **Unit.** Three `FileApplyTests` cases use injected streams to check the
  written prefix, unreadable state and closing failures.
- **Integration.** The remaining former `RefactorTool.Tests` cases run in
  their own assembly. The Roslyn planners use an in-memory project graph but
  capture real source bytes. Request validation and file races use real files.
  Windows path canonicalization and file sharing are gated at discovery.
  The classic solution and project entry are independent theory rows.
- **SDK.** The SDK-backed integration cases use the build's RefactorTool in
  bounded child processes and check actual project inclusion, workspace inputs,
  generators and apply. `pwsh` creates real junction fixtures, and xUnit
  verifies the resulting behavior.
- **Artifact.** The published integration cases launch the extracted tool to
  exercise cross-project operations and SDK selection. The archive inventory
  checks notices, the build host and test dependency exclusion.

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
| 04 Extract output race, changed input, forged plan | `ApplyIntegrationTests.ExtractApplyRefusesChangedOutputInputOrPlan` |
| 05 Unsupported members and visibility collision | `ExtractInterfaceTests.UnsupportedMemberShapesAreRefused` and `DuplicateTypeWouldIntroduceCompilationErrors` |
| 06 File-dependent inclusion and invalid Windows paths | `CompileInclusionTests.RejectsRulesThatCanExcludeOrImportTheNewFile` and `ExtractInterfaceTests.InvalidOutputPathIsRefused` |
| 07 Inactive import, item expressions, target rules, lower-case Compile glob | `CompileInclusionTests.RejectsRulesThatCanExcludeOrImportTheNewFile` and `OtherProjectLowercaseCompileGlobCanAlsoIncludeTheOutput` |
| 08 Type and namespace rebinding | `ExtractInterfaceTests.ExistingTypeAndNamespaceBindingsCannotChange` |
| 09 Future imports, SDK hooks, stable positive | `CompileInclusionTests.RejectsRulesThatCanExcludeOrImportTheNewFile` and `StableImportAllowsPreviewButExplicitCompileExclusionRefuses` |
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
| 38 Activated, failing, and ABI-incompatible generators | `GeneratorIntegrationTests.ExtractionRefusesActivatedFailingOrIncompatibleAnalyzer` |
| 39 Generated reference and declaration | `GeneratorIntegrationTests.GeneratorReferenceAndDeclarationCannotBeEdited` |
| 40–41 External intermediates and bin ancestor | `WorkspaceIntegrationTests.ExternalSdkIntermediatesAreCapturedWithoutBeingEdited` and `BinAncestorOutsideProjectDoesNotMarkAuthoredSourceGenerated` |
| 42, 44 Canonical input retarget and removal | `ApplyIntegrationTests.CanonicalReadOnlyInputDetectsRetargetOrRemoval` |
| 43 Editable and plan junctions | `ApplyIntegrationTests.PlanAndEditableSourceJunctionsAreRefused` |
| 45 Exclusive edited or unedited input handle | `ApplyIntegrationTests.ExclusiveSourceOrProjectHandleRefusesBeforeWrites` |
| 46 Non-C# solution member | `WorkspaceIntegrationTests.VisualBasicSolutionMemberIsRejected` |
| 47 Read-only reference | `ApplyIntegrationTests.ReadOnlyConsumerRefusesBeforeAnySourceChange` |
| 49, 57 Classic solution folder and project entry graph | `WorkspaceIntegrationTests.ClassicSolutionFolderAndProjectEntryKeepCompilationGraph` |
| 50–52 BOM, missing final newline, compact hunks, CR-only patch | `RenameTests.PreservesBomAndNoFinalNewline`, `CompactPatchOmitsDistantUnchangedContext`, and `CrOnlySourceAndPatchAreByteExact` |
| 53 Ambiguous overload position | `RenameTests.PositionOutsideIdentifierAndOverloadGroupAreRefused` |
| 54 Inherited name collision | `RenameTests.InvalidNamesSelectionsAndCollisionsProduceNoEdits` |
| 55 Configuration injection | `WorkspaceIntegrationTests.ConfigurationCannotInjectAnMsbuildProperty` |
| 56 Caller directory with incompatible SDK | `PublishedArtifactTests.CallerSdkConfigurationDoesNotOverrideWorkspaceSdk` |
| 58–59 Design-time linked or unexpected sources | `WorkspaceIntegrationTests.DesignTimeOnlySourceCannotSilentlyChangeTheEditableGraph` |
| 60–61 Design-time missing edge and build-only reference | `WorkspaceIntegrationTests.DesignTimeAndBuildOnlyReferencesHaveDifferentMeaning` |
| 62 Malformed source encoding | `WorkspaceIntegrationTests.MalformedSourceEncodingIsRefusedWithoutWrites` |
| 63 Alias and generic nameof syntax | `RenameTests.AliasAndGenericNameofPreserveSyntax` |
| 64 Unsafe source, project-local and SDK configuration plan paths | `CommandInputTests.SourceAndSdkConfigurationNamesAreRefusedBeforePreview` and `ApplyIntegrationTests.PreviewPlanCannotEnterLoadedProjectDirectory` |
| I/O runner | `FileApplyTests` covers partial and unknown states, all close attempts and prior observations, unchanged-input sharing, exclusive create race, empty and unattempted outputs, and recovery for a partial new file. |
