# R2R3 自动化与像素审计（实施者自测）

本报告不提供独立视觉签署。PNG 原文件不做调色、重绘或尺寸修改。

## 无过滤全量（TRX 实读）

| assembly | passed | failed | skipped | total |
|---|---|---|---|---|
| NewManga.Appearance.Tests.dll | 21 | 0 | 0 | 21 |
| NewManga.Presentation.Avalonia.Tests.dll | 38 | 0 | 0 | 38 |
| NewManga.ApplicationCore.Tests.dll | 31 | 0 | 0 | 31 |
| NewManga.CoreClient.Tests.dll | 128 | 0 | 22 | 150 |
| NewManga.Host.Tests.dll | 51 | 0 | 28 | 79 |
| NewManga.ThemeEngine.Tests.dll | 253 | 0 | 0 | 253 |
| NewManga.App.Tests.dll | 653 | 0 | 7 | 660 |
| NewManga.DesignSystem.Tests.dll | 114 | 0 | 0 | 114 |
| TOTAL | 1289 | 0 | 57 | 1346 |

相对1281/0/57：+8/+0/+0。

## 新增生命周期回归

| test | outcome |
|---|---|
| `NewManga.App.Tests.FluentResidual2DecorativeTests.PageTurnParticles_InactiveNavigationAndNewTurn_StayPausedUntilActivation` | Passed |
| `NewManga.App.Tests.FluentResidual2DecorativeTests.PageTurnParticles_DisablingPolicy_CancelsExistingRunAndCannotRevive(mode: Full, categories: None, paused: False)` | Passed |
| `NewManga.App.Tests.FluentResidual2DecorativeTests.PageTurnParticles_DisablingPolicy_CancelsExistingRunAndCannotRevive(mode: Full, categories: None, paused: True)` | Passed |
| `NewManga.App.Tests.FluentResidual2DecorativeTests.PageTurnParticles_DisablingPolicy_CancelsExistingRunAndCannotRevive(mode: Auto, categories: Decorative, paused: False)` | Passed |
| `NewManga.App.Tests.FluentResidual2DecorativeTests.PageTurnParticles_DisablingPolicy_CancelsExistingRunAndCannotRevive(mode: Reduce, categories: Decorative, paused: True)` | Passed |
| `NewManga.App.Tests.FluentResidual2DecorativeTests.PageTurnParticles_DisablingPolicy_CancelsExistingRunAndCannotRevive(mode: Auto, categories: Decorative, paused: True)` | Passed |
| `NewManga.App.Tests.FluentResidual2DecorativeTests.PageTurnParticles_DisablingPolicy_CancelsExistingRunAndCannotRevive(mode: Reduce, categories: Decorative, paused: False)` | Passed |
| `NewManga.App.Tests.FluentResidual2DecorativeTests.ShelfGradient_InactiveNavigationReturn_RemainsPausedUntilActivation` | Passed |

## 逐条 skip 原因

| test | actual reason |
|---|---|
| `NewManga.App.Tests.CreateChapterHostIntegrationTests.HostController_CreateChapter_SucceedsThenMapsCoreFailures` | reason: needs sidecar fixture - set NEWMANGA_CORECLIENT_SIDECAR_DIR or run apps/desktop-avalonia/scripts/test.ps1 (AC11 unlabelled copy) |
| `NewManga.App.Tests.CreateChapterHostIntegrationTests.HostController_CreateChapter_WhenReadOnly_PublishesHostReadOnly` | reason: needs sidecar fixture - set NEWMANGA_CORECLIENT_SIDECAR_DIR or run apps/desktop-avalonia/scripts/test.ps1 (AC11 unlabelled copy) |
| `NewManga.App.Tests.RunControllerHostIntegrationTests.RunCommands_MapCoreErrors_AndReuseIdempotencyKeys` | reason: needs sidecar fixture - set NEWMANGA_CORECLIENT_SIDECAR_DIR or run apps/desktop-avalonia/scripts/test.ps1 (AC11 unlabelled copy) |
| `NewManga.App.Tests.RunControllerHostIntegrationTests.RunCommands_StartSuccessfulRun_ProjectRealPerPageState_AndReuseKey` | reason: needs sidecar fixture - set NEWMANGA_CORECLIENT_SIDECAR_DIR or run apps/desktop-avalonia/scripts/test.ps1 (AC11 unlabelled copy) |
| `NewManga.App.Tests.RunControllerHostIntegrationTests.RunCommands_WhenReadOnly_PublishHostReadOnly` | reason: needs sidecar fixture - set NEWMANGA_CORECLIENT_SIDECAR_DIR or run apps/desktop-avalonia/scripts/test.ps1 (AC11 unlabelled copy) |
| `NewManga.App.Tests.StartupSelfCheckUiTests.SelfCheckFailure_IsVisibleInTheSnapshot` | reason: needs sidecar fixture - set NEWMANGA_CORECLIENT_SIDECAR_DIR or run apps/desktop-avalonia/scripts/test.ps1 (AC11 unlabelled copy) |
| `NewManga.App.Tests.WritePolicyUiIntegrationTests.DefaultController_IsWritable_AndParityFalse_IsReadOnlyWithReason` | reason: needs sidecar fixture - set NEWMANGA_CORECLIENT_SIDECAR_DIR or run apps/desktop-avalonia/scripts/test.ps1 (AC11 unlabelled copy) |
| `NewManga.CoreClient.Tests.Commands.CommandIntegrationTests.ChineseTitle_ThroughCommandDispatcher_RoundTripsWithoutMojibake` | reason: needs sidecar fixture - set NEWMANGA_CORECLIENT_SIDECAR_DIR or run apps/desktop-avalonia/scripts/test.ps1 (AC11 unlabelled copy) |
| `NewManga.CoreClient.Tests.Commands.CommandIntegrationTests.DomainServices_CoverEveryCommandExactlyOnce` | reason: needs sidecar fixture - set NEWMANGA_CORECLIENT_SIDECAR_DIR or run apps/desktop-avalonia/scripts/test.ps1 (AC11 unlabelled copy) |
| `NewManga.CoreClient.Tests.Commands.CommandIntegrationTests.NotSupportedSurface_ReturnsTypedErrorsWithReasons` | reason: needs sidecar fixture - set NEWMANGA_CORECLIENT_SIDECAR_DIR or run apps/desktop-avalonia/scripts/test.ps1 (AC11 unlabelled copy) |
| `NewManga.CoreClient.Tests.Commands.CommandIntegrationTests.TwelveImplementedCommands_ExecuteAgainstFrozenSidecars` | reason: needs sidecar fixture - set NEWMANGA_CORECLIENT_SIDECAR_DIR or run apps/desktop-avalonia/scripts/test.ps1 (AC11 unlabelled copy) |
| `NewManga.CoreClient.Tests.Commands.CommandWiringB1Tests.B1Commands_ExecuteAgainstFrozenCore` | reason: needs sidecar fixture - set NEWMANGA_CORECLIENT_SIDECAR_DIR or run apps/desktop-avalonia/scripts/test.ps1 (AC11 unlabelled copy) |
| `NewManga.CoreClient.Tests.Commands.CommandWiringB1Tests.B1Commands_RejectInvalidArgumentsBeforeAnyCoreFrame` | reason: needs sidecar fixture - set NEWMANGA_CORECLIENT_SIDECAR_DIR or run apps/desktop-avalonia/scripts/test.ps1 (AC11 unlabelled copy) |
| `NewManga.CoreClient.Tests.Commands.CommandWiringB2Tests.B2Commands_ExecuteAgainstFrozenCore` | reason: needs sidecar fixture - set NEWMANGA_CORECLIENT_SIDECAR_DIR or run apps/desktop-avalonia/scripts/test.ps1 (AC11 unlabelled copy) |
| `NewManga.CoreClient.Tests.Commands.CommandWiringB2Tests.B2Commands_RejectInvalidArgumentsBeforeAnyCoreFrame` | reason: needs sidecar fixture - set NEWMANGA_CORECLIENT_SIDECAR_DIR or run apps/desktop-avalonia/scripts/test.ps1 (AC11 unlabelled copy) |
| `NewManga.CoreClient.Tests.Commands.CommandWiringB2Tests.ListRegionRevisions_ExecutesAgainstRegionFixture` | reason: needs sidecar fixture - set NEWMANGA_CORECLIENT_SIDECAR_DIR or run apps/desktop-avalonia/scripts/test.ps1 (AC11 unlabelled copy) |
| `NewManga.CoreClient.Tests.Commands.RunBindingFixTests.StartRun_DefaultDisabled_OmitsProviderBindings` | reason: needs sidecar fixture - set NEWMANGA_CORECLIENT_SIDECAR_DIR or run apps/desktop-avalonia/scripts/test.ps1 (AC11 unlabelled copy) |
| `NewManga.CoreClient.Tests.Commands.RunBindingFixTests.StartRun_InjectsDefaultBindings_WhenOverridesAbsentOrEmpty` | reason: needs sidecar fixture - set NEWMANGA_CORECLIENT_SIDECAR_DIR or run apps/desktop-avalonia/scripts/test.ps1 (AC11 unlabelled copy) |
| `NewManga.CoreClient.Tests.Commands.RunBindingFixTests.StartRun_InvalidOverrides_AreRejectedBeforeAnyCoreFrame` | reason: needs sidecar fixture - set NEWMANGA_CORECLIENT_SIDECAR_DIR or run apps/desktop-avalonia/scripts/test.ps1 (AC11 unlabelled copy) |
| `NewManga.CoreClient.Tests.Commands.RunBindingFixTests.StartRun_KeepsExplicitUserBindings_AndOtherOverrides` | reason: needs sidecar fixture - set NEWMANGA_CORECLIENT_SIDECAR_DIR or run apps/desktop-avalonia/scripts/test.ps1 (AC11 unlabelled copy) |
| `NewManga.CoreClient.Tests.Commands.S4RegionReaderCommandTests.RegionWriteFace_AndReaderProgressFace_ExecuteAgainstFrozenCore` | reason: needs sidecar fixture - set NEWMANGA_CORECLIENT_SIDECAR_DIR or run apps/desktop-avalonia/scripts/test.ps1 (AC11 unlabelled copy) |
| `NewManga.CoreClient.Tests.CoreServiceIntegrationTests.ChineseTitle_CreateThenList_RoundTripsExactly_AndWireIsAsciiEscaped` | reason: needs sidecar fixture - set NEWMANGA_CORECLIENT_SIDECAR_DIR or run apps/desktop-avalonia/scripts/test.ps1 (AC11 unlabelled copy) |
| `NewManga.CoreClient.Tests.CoreServiceIntegrationTests.Ping_ReturnsReady_WithProtocol23` | reason: needs sidecar fixture - set NEWMANGA_CORECLIENT_SIDECAR_DIR or run apps/desktop-avalonia/scripts/test.ps1 (AC11 unlabelled copy) |
| `NewManga.CoreClient.Tests.CoreServiceIntegrationTests.RawUtf8Request_ReplicatesUnknownError` | reason: needs sidecar fixture - set NEWMANGA_CORECLIENT_SIDECAR_DIR or run apps/desktop-avalonia/scripts/test.ps1 (AC11 unlabelled copy) |
| `NewManga.CoreClient.Tests.CoreServiceIntegrationTests.WireFrames_AreSingleLineUtf8AndAsciiForEveryEscapedRequest` | reason: needs sidecar fixture - set NEWMANGA_CORECLIENT_SIDECAR_DIR or run apps/desktop-avalonia/scripts/test.ps1 (AC11 unlabelled copy) |
| `NewManga.CoreClient.Tests.HostBridgeIntegrationTests.Ping_IssueResolveRevoke_FullLifecycle` | reason: needs sidecar fixture - set NEWMANGA_CORECLIENT_SIDECAR_DIR or run apps/desktop-avalonia/scripts/test.ps1 (AC11 unlabelled copy) |
| `NewManga.CoreClient.Tests.HostBridgeIntegrationTests.TypedErrors_UnknownResource_AndCoreOwnedPathSmuggling` | reason: needs sidecar fixture - set NEWMANGA_CORECLIENT_SIDECAR_DIR or run apps/desktop-avalonia/scripts/test.ps1 (AC11 unlabelled copy) |
| `NewManga.CoreClient.Tests.HostBridgeIntegrationTests.WireFrames_AreSingleLineJson_AsciiOnly` | reason: needs sidecar fixture - set NEWMANGA_CORECLIENT_SIDECAR_DIR or run apps/desktop-avalonia/scripts/test.ps1 (AC11 unlabelled copy) |
| `NewManga.CoreClient.Tests.SidecarFailureTests.StartupTimeout_IsTyped_NotAHang` | reason: needs sidecar fixture - set NEWMANGA_CORECLIENT_SIDECAR_DIR or run apps/desktop-avalonia/scripts/test.ps1 (AC11 unlabelled copy) |
| `NewManga.Host.Tests.CredentialPortTests.CredentialPutAndClear_AgainstFrozenSidecar_FullChain` | reason: needs sidecar fixture - set NEWMANGA_CORECLIENT_SIDECAR_DIR or run apps/desktop-avalonia/scripts/test.ps1 (AC11 unlabelled copy) |
| `NewManga.Host.Tests.ExportE2ETests.Export_Cancel_LeavesNoArtifact` | reason: needs sidecar fixture - set NEWMANGA_CORECLIENT_SIDECAR_DIR or run apps/desktop-avalonia/scripts/test.ps1 (AC11 unlabelled copy) |
| `NewManga.Host.Tests.ExportE2ETests.Export_Zip_Produces_RealArtifact_AndSnapshotHistory` | reason: needs sidecar fixture - set NEWMANGA_CORECLIENT_SIDECAR_DIR or run apps/desktop-avalonia/scripts/test.ps1 (AC11 unlabelled copy) |
| `NewManga.Host.Tests.ExportStalePolicyWireTests.BothPolicies_AreSentToTheCore_AsStartExportFrames` | reason: needs sidecar fixture - set NEWMANGA_CORECLIENT_SIDECAR_DIR or run apps/desktop-avalonia/scripts/test.ps1 (AC11 unlabelled copy) |
| `NewManga.Host.Tests.GrantIssuerTests.Export_GrantRegisters_ThenCoreFailsTyped_OnMissingTranslatedPages` | reason: needs sidecar fixture - set NEWMANGA_CORECLIENT_SIDECAR_DIR or run apps/desktop-avalonia/scripts/test.ps1 (AC11 unlabelled copy) |
| `NewManga.Host.Tests.GrantIssuerTests.Import_IntoNewChapter_Executes_AndRegistersGrant` | reason: needs sidecar fixture - set NEWMANGA_CORECLIENT_SIDECAR_DIR or run apps/desktop-avalonia/scripts/test.ps1 (AC11 unlabelled copy) |
| `NewManga.Host.Tests.GrantIssuerTests.ShellActions_Open_Whitelisted_Directories_And_Refuse_Outside_Paths` | reason: needs sidecar fixture - set NEWMANGA_CORECLIENT_SIDECAR_DIR or run apps/desktop-avalonia/scripts/test.ps1 (AC11 unlabelled copy) |
| `NewManga.Host.Tests.GrantIssuerTests.ShellActions_RealOpener_OpensExplorer_WhenEnabled` | reason: needs sidecar fixture - set NEWMANGA_CORECLIENT_SIDECAR_DIR or run apps/desktop-avalonia/scripts/test.ps1 (AC11 unlabelled copy) |
| `NewManga.Host.Tests.HostReaderChaptersIntegrationTests.ConcurrentChapterAndProjectionReads_AreSerialized` | reason: needs sidecar fixture - set NEWMANGA_CORECLIENT_SIDECAR_DIR or run apps/desktop-avalonia/scripts/test.ps1 (AC11 unlabelled copy) |
| `NewManga.Host.Tests.HostReaderChaptersIntegrationTests.ListChapters_MatchesReaderProjection` | reason: needs sidecar fixture - set NEWMANGA_CORECLIENT_SIDECAR_DIR or run apps/desktop-avalonia/scripts/test.ps1 (AC11 unlabelled copy) |
| `NewManga.Host.Tests.HostReaderProgressIntegrationTests.SaveReadingProgress_PersistsAcrossHostRestart_AndResumes` | reason: needs sidecar fixture - set NEWMANGA_CORECLIENT_SIDECAR_DIR or run apps/desktop-avalonia/scripts/test.ps1 (AC11 unlabelled copy) |
| `NewManga.Host.Tests.HostReaderProgressIntegrationTests.SaveReadingProgress_ReadOnlyHost_IsTypedRefusal_NoCoreCall` | reason: needs sidecar fixture - set NEWMANGA_CORECLIENT_SIDECAR_DIR or run apps/desktop-avalonia/scripts/test.ps1 (AC11 unlabelled copy) |
| `NewManga.Host.Tests.HostReaderProgressIntegrationTests.SaveReadingProgress_UnknownPage_IsTypedCoreRejection` | reason: needs sidecar fixture - set NEWMANGA_CORECLIENT_SIDECAR_DIR or run apps/desktop-avalonia/scripts/test.ps1 (AC11 unlabelled copy) |
| `NewManga.Host.Tests.HostRegionWorkbenchIntegrationTests.RegionReadWriteFace_ExecutesAgainstFrozenCore_AndProjectsOverlayGeometry` | reason: needs sidecar fixture - set NEWMANGA_CORECLIENT_SIDECAR_DIR or run apps/desktop-avalonia/scripts/test.ps1 (AC11 unlabelled copy) |
| `NewManga.Host.Tests.HostRegionWorkbenchIntegrationTests.RegionReads_SerializeOnTheCorePipe` | reason: needs sidecar fixture - set NEWMANGA_CORECLIENT_SIDECAR_DIR or run apps/desktop-avalonia/scripts/test.ps1 (AC11 unlabelled copy) |
| `NewManga.Host.Tests.HostRegionWorkbenchIntegrationTests.RegionWrite_StaleExpectedRevision_IsTypedInputRevisionChanged` | reason: needs sidecar fixture - set NEWMANGA_CORECLIENT_SIDECAR_DIR or run apps/desktop-avalonia/scripts/test.ps1 (AC11 unlabelled copy) |
| `NewManga.Host.Tests.HostRegionWorkbenchIntegrationTests.RegionWrites_ReadOnlyHost_AreTypedRefusals_WithZeroCoreFrames` | reason: needs sidecar fixture - set NEWMANGA_CORECLIENT_SIDECAR_DIR or run apps/desktop-avalonia/scripts/test.ps1 (AC11 unlabelled copy) |
| `NewManga.Host.Tests.HostRuntimeIntegrationTests.ParityReached_ChineseRoundTrip_IsExact_ThroughHost` | reason: needs sidecar fixture - set NEWMANGA_CORECLIENT_SIDECAR_DIR or run apps/desktop-avalonia/scripts/test.ps1 (AC11 unlabelled copy) |
| `NewManga.Host.Tests.HostRuntimeIntegrationTests.ReadOnlyUntilParity_Ready_WithBothSidecars_AndWriteBlocked` | reason: needs sidecar fixture - set NEWMANGA_CORECLIENT_SIDECAR_DIR or run apps/desktop-avalonia/scripts/test.ps1 (AC11 unlabelled copy) |
| `NewManga.Host.Tests.HostRuntimeIntegrationTests.SecondInstance_IsAlreadyRunning_WithoutSpawningSidecars` | reason: needs sidecar fixture - set NEWMANGA_CORECLIENT_SIDECAR_DIR or run apps/desktop-avalonia/scripts/test.ps1 (AC11 unlabelled copy) |
| `NewManga.Host.Tests.LegacyShellRealTests.LegacyShellRunning_ForcesReadOnlyMode_AndBlocksWrites` | reason: needs sidecar fixture - set NEWMANGA_CORECLIENT_SIDECAR_DIR or run apps/desktop-avalonia/scripts/test.ps1 (AC11 unlabelled copy) |
| `NewManga.Host.Tests.RealTranslateProviderTests.RealOpenCodeProvider_HostConfiguration` | reason: needs sidecar fixture - set NEWMANGA_CORECLIENT_SIDECAR_DIR or run apps/desktop-avalonia/scripts/test.ps1 (AC11 unlabelled copy) |
| `NewManga.Host.Tests.StartupSelfCheckTests.MajorMismatch_DowngradesToReadOnly_AndRefusesWrites` | reason: needs sidecar fixture - set NEWMANGA_CORECLIENT_SIDECAR_DIR or run apps/desktop-avalonia/scripts/test.ps1 (AC11 unlabelled copy) |
| `NewManga.Host.Tests.StartupSelfCheckTests.MissingCapability_DowngradesToReadOnly_AndRefusesWrites` | reason: needs sidecar fixture - set NEWMANGA_CORECLIENT_SIDECAR_DIR or run apps/desktop-avalonia/scripts/test.ps1 (AC11 unlabelled copy) |
| `NewManga.Host.Tests.StartupSelfCheckTests.RealHost_PassesCheapChecks_AndStaysWritable` | reason: needs sidecar fixture - set NEWMANGA_CORECLIENT_SIDECAR_DIR or run apps/desktop-avalonia/scripts/test.ps1 (AC11 unlabelled copy) |
| `NewManga.Host.Tests.WritePolicyTests.DefaultStart_IsReadWrite_AndCanCreateBook` | reason: needs sidecar fixture - set NEWMANGA_CORECLIENT_SIDECAR_DIR or run apps/desktop-avalonia/scripts/test.ps1 (AC11 unlabelled copy) |
| `NewManga.Host.Tests.WritePolicyTests.ExplicitParityFalse_RefusesWrites_WithTypedReadOnlyError` | reason: needs sidecar fixture - set NEWMANGA_CORECLIENT_SIDECAR_DIR or run apps/desktop-avalonia/scripts/test.ps1 (AC11 unlabelled copy) |
| `NewManga.Host.Tests.WritePolicyTests.FirstRunBackup_CreatesRealBackupFile_OnFirstWritableStartWithCatalog` | reason: needs sidecar fixture - set NEWMANGA_CORECLIENT_SIDECAR_DIR or run apps/desktop-avalonia/scripts/test.ps1 (AC11 unlabelled copy) |

## 图数与旧签署的字节对应

旧图 164；本轮 172 PNG / 172 清单行 / 172 唯一 SHA。
同名同字节 136；同名改字节 24；新增文件名 12；移除旧误标签文件名 4。
原 impl-r3 的158 PASS/6 REJECT只签其旧SHA；本轮清单全部NOT_RUN，不将实施者自测充作复审。

| file | byte change | old SHA256 | new SHA256 |
|---|---|---|---|
| `components--alert-banner--blocked--full--dark.png` | UNCHANGED | 889624c7872462760cc7545756717001ea63349fd747c19b4b39b22bc77a5b24 | 889624c7872462760cc7545756717001ea63349fd747c19b4b39b22bc77a5b24 |
| `components--alert-banner--blocked--full--light.png` | UNCHANGED | 5d540e07adc5dcda6252092cb9e7b01708fbb2079d4755bddc412378f623154a | 5d540e07adc5dcda6252092cb9e7b01708fbb2079d4755bddc412378f623154a |
| `components--alert-banner--done--full--dark.png` | UNCHANGED | 7a4d26627e72ace2020ff5ea0e51adc970e4b03184e30a8acbd5fa1386c8474e | 7a4d26627e72ace2020ff5ea0e51adc970e4b03184e30a8acbd5fa1386c8474e |
| `components--alert-banner--done--full--light.png` | UNCHANGED | 163a6a8d34bc3115045d0ca15df288d686880733d038319321a454bdef346cf8 | 163a6a8d34bc3115045d0ca15df288d686880733d038319321a454bdef346cf8 |
| `components--alert-banner--failed--full--dark.png` | UNCHANGED | 4e795504d6985ae9096333d8fb4eef07d5619a75dc5c8456669ac7b0871da9b0 | 4e795504d6985ae9096333d8fb4eef07d5619a75dc5c8456669ac7b0871da9b0 |
| `components--alert-banner--failed--full--light.png` | UNCHANGED | c0c0ff3836fba3fceb4f8a4bc58423f3d8fb0e77d10c94e7b53abbdf4376c719 | c0c0ff3836fba3fceb4f8a4bc58423f3d8fb0e77d10c94e7b53abbdf4376c719 |
| `components--alert-banner--locked--full--dark.png` | UNCHANGED | dd5a7ffc3450eeeb9dbb85065152f8f1c5a3714caba00d585420077e5f71a78a | dd5a7ffc3450eeeb9dbb85065152f8f1c5a3714caba00d585420077e5f71a78a |
| `components--alert-banner--locked--full--light.png` | UNCHANGED | bc5b80643145d8192e36d9b3f1a81ad4d3db0c1212559f9aaaa0343b57e446e7 | bc5b80643145d8192e36d9b3f1a81ad4d3db0c1212559f9aaaa0343b57e446e7 |
| `components--alert-banner--notstarted--full--dark.png` | UNCHANGED | bbaa2d452fc25923a23d2ad06a4c4f75fbe5a04a8d650fb4cb51b267db021eef | bbaa2d452fc25923a23d2ad06a4c4f75fbe5a04a8d650fb4cb51b267db021eef |
| `components--alert-banner--notstarted--full--light.png` | UNCHANGED | e2154725e7c1eae2a64f9e84a8b8cba298bdaa5fe74cb08b04a793e1f1d61f3a | e2154725e7c1eae2a64f9e84a8b8cba298bdaa5fe74cb08b04a793e1f1d61f3a |
| `components--alert-banner--queued--full--dark.png` | UNCHANGED | 41f70aa437e62c3463760aab8ded163ee5bcc76b12f609c13370eebae3d6b0c5 | 41f70aa437e62c3463760aab8ded163ee5bcc76b12f609c13370eebae3d6b0c5 |
| `components--alert-banner--queued--full--light.png` | UNCHANGED | 0f10612d149089d0d9aed4ee66177f239f1fa9b67f704bd96f2b0381c42b53fb | 0f10612d149089d0d9aed4ee66177f239f1fa9b67f704bd96f2b0381c42b53fb |
| `components--alert-banner--running--full--dark.png` | UNCHANGED | 99c5e3c53622e072898c86ea2aae0d2029d9d4e0b7fd8b83c35f0719f7356ce2 | 99c5e3c53622e072898c86ea2aae0d2029d9d4e0b7fd8b83c35f0719f7356ce2 |
| `components--alert-banner--running--full--light.png` | UNCHANGED | 4b694feb9fd9888e13eec5e5fe60bc49b2c82469c5486bbb123d61db9e232e11 | 4b694feb9fd9888e13eec5e5fe60bc49b2c82469c5486bbb123d61db9e232e11 |
| `components--alert-banner--skipped--full--dark.png` | UNCHANGED | a0ffe5811f77b4772115d3455cc443e94f938f6cf57c4f7a3eae992b073da157 | a0ffe5811f77b4772115d3455cc443e94f938f6cf57c4f7a3eae992b073da157 |
| `components--alert-banner--skipped--full--light.png` | UNCHANGED | c8bb612c824489e5a896f5e3aa2138c32550a2f30df26f390fbdd43c689331e1 | c8bb612c824489e5a896f5e3aa2138c32550a2f30df26f390fbdd43c689331e1 |
| `components--alert-banner--stale--full--dark.png` | UNCHANGED | c3bc9b631b8eb5b51282a81e0c7fcfebf274fda9bb3effaecb3a105b3145afca | c3bc9b631b8eb5b51282a81e0c7fcfebf274fda9bb3effaecb3a105b3145afca |
| `components--alert-banner--stale--full--light.png` | UNCHANGED | a87e56fd424452afbec7746b1fb573ce28f317f00d5d075dc65c0fba8baeb64b | a87e56fd424452afbec7746b1fb573ce28f317f00d5d075dc65c0fba8baeb64b |
| `components--book-card--default--full--dark.png` | UNCHANGED | 2b49270515c35d9d25a4ed2af95627d95ec92ec6df94e2abdfa8f43fca7567b7 | 2b49270515c35d9d25a4ed2af95627d95ec92ec6df94e2abdfa8f43fca7567b7 |
| `components--book-card--default--full--light.png` | UNCHANGED | 4155acd86a1b6a0fe18a8ca2adbd0eda43dc88665f52811e56531d94c23458d8 | 4155acd86a1b6a0fe18a8ca2adbd0eda43dc88665f52811e56531d94c23458d8 |
| `components--book-card--disabled--full--dark.png` | UNCHANGED | a379dba17d8109c2da45f7bddf371ae47dd8bd9db5d3f7e22baa7169f88594bc | a379dba17d8109c2da45f7bddf371ae47dd8bd9db5d3f7e22baa7169f88594bc |
| `components--book-card--disabled--full--light.png` | UNCHANGED | 611bd5b99caf77161b02dabc5a81d92113e924141b54e036423060453286005e | 611bd5b99caf77161b02dabc5a81d92113e924141b54e036423060453286005e |
| `components--book-row--default--full--dark.png` | UNCHANGED | d4be22a5228aa3f8930cd8e2ae25789cdcd843780146a68d1d5f61228a89afdf | d4be22a5228aa3f8930cd8e2ae25789cdcd843780146a68d1d5f61228a89afdf |
| `components--book-row--default--full--light.png` | UNCHANGED | f3e1043e9fca4fe3bedc316a8b6d9e16a1d3e810e3456da80eaeec343df48324 | f3e1043e9fca4fe3bedc316a8b6d9e16a1d3e810e3456da80eaeec343df48324 |
| `components--book-row--disabled--full--dark.png` | UNCHANGED | 661615cb6d3be9fd287c54c36ba03082bcc02d78a0c686110fc0369d9c9167e6 | 661615cb6d3be9fd287c54c36ba03082bcc02d78a0c686110fc0369d9c9167e6 |
| `components--book-row--disabled--full--light.png` | UNCHANGED | 17d95b8b06885f6bc4a6e676169a50885a30b011701f29bcad0a8e89c662f32c | 17d95b8b06885f6bc4a6e676169a50885a30b011701f29bcad0a8e89c662f32c |
| `components--chapter-list--default--full--dark.png` | UNCHANGED | 54d5facd816f38d120a9fc5adcfcdd8a31b3258c182b8949a077dfefeaa33386 | 54d5facd816f38d120a9fc5adcfcdd8a31b3258c182b8949a077dfefeaa33386 |
| `components--chapter-list--default--full--light.png` | UNCHANGED | f4bc1e72aa58d8bfb6f4045028e95badfc02bb6255f0535ade7252bdd32159d5 | f4bc1e72aa58d8bfb6f4045028e95badfc02bb6255f0535ade7252bdd32159d5 |
| `components--command-palette--empty--full--dark.png` | CHANGED | 90ac667c6329844e3d9ca99b8a181530f019a920b491bb1394a333bfc941ddb4 | f02341d594f487b3f5096ca5b7ec025af56766e80dc755393680de28533427eb |
| `components--command-palette--empty--full--light.png` | CHANGED | fdbe84a4793048856a47e34c134a73e201e0c64a2ac845843e79970e47975d48 | a43cba142d61fc4f45e96056b124a1e97854122c5d8ceb268959cadcafceb669 |
| `components--command-palette--result--full--dark.png` | CHANGED | 3e3117b108988ca8ea69eb623237ac5fcb72b02755ddf7c24ff7b72312010dbb | 3fb1b7368fb3127acab2ab5793d48128e7d94b9f8aaf068119ae0281be65e954 |
| `components--command-palette--result--full--light.png` | CHANGED | bc29b1dead005a23b2b1728ae0cd7e7c656acecf2b83992bf93cd6b8e2220085 | 0c164442056950b2671e6ba4dcaee6da26a0a6b74efe65245739e3d1a47945df |
| `components--context-menu--disabled-item--full--dark.png` | UNCHANGED | 8a58e962dd4219c04b2daaa5914999a34acf64f073b4039e970cab33ab8191bc | 8a58e962dd4219c04b2daaa5914999a34acf64f073b4039e970cab33ab8191bc |
| `components--context-menu--disabled-item--full--light.png` | UNCHANGED | 66d6d2856d808299064b6c7e5986856f335185c2510d438607fbab9862ce49ac | 66d6d2856d808299064b6c7e5986856f335185c2510d438607fbab9862ce49ac |
| `components--danger-button--default--full--dark.png` | UNCHANGED | 6a41f040ec40ba869973b2cb31e89b16a71380e79693f2a06956b33bcd0281d2 | 6a41f040ec40ba869973b2cb31e89b16a71380e79693f2a06956b33bcd0281d2 |
| `components--danger-button--default--full--light.png` | UNCHANGED | 1d8455eaf665cdd6b7571a30a955bb5a67b886c80dc1ec1c9865e2ca780adcc7 | 1d8455eaf665cdd6b7571a30a955bb5a67b886c80dc1ec1c9865e2ca780adcc7 |
| `components--danger-button--disabled--full--dark.png` | UNCHANGED | 860f0a294d694add33ba817e43cc852d2e8e823ccba920e3603cef19aab4d0ed | 860f0a294d694add33ba817e43cc852d2e8e823ccba920e3603cef19aab4d0ed |
| `components--danger-button--disabled--full--light.png` | UNCHANGED | 9149c20ee24a91492f1add37dcc719686595390af0869a50973bc497ebedcf42 | 9149c20ee24a91492f1add37dcc719686595390af0869a50973bc497ebedcf42 |
| `components--danger-button--hover--full--dark.png` | UNCHANGED | be969a6bb952c675bda2e1172da9dfe5d50fac5fd55cef03e324495b24359d4a | be969a6bb952c675bda2e1172da9dfe5d50fac5fd55cef03e324495b24359d4a |
| `components--danger-button--hover--full--light.png` | UNCHANGED | 9dc59d68f89479997baecd320880b65cd967d841753286d0a4f1d71452a926df | 9dc59d68f89479997baecd320880b65cd967d841753286d0a4f1d71452a926df |
| `components--danger-button--pressed--full--dark.png` | CHANGED | a19ca3dda2c87b7078d994ff559baefdc32d9cd2e2a2baebe5ad536c5f8a2f77 | c9ed4f8e9f47cb250fd569df180730a98f198a3a78fd4e077c855cf46379d6a9 |
| `components--danger-button--pressed--full--light.png` | CHANGED | 5bc2d9c8bfec5f98c805bd28f2a1154399077306355a35de47aac6e12aabb24b | 8d37c109c38e96fc73fa5f7d1ddd08c3de02c9631ea54fe19b27470a980bed35 |
| `components--dialog--closed--full--dark.png` | UNCHANGED | 8ac09c4e2df3f412b5a45695aadf0bddc7035b3faf45d4dd063405bc0e3de48a | 8ac09c4e2df3f412b5a45695aadf0bddc7035b3faf45d4dd063405bc0e3de48a |
| `components--dialog--closed--full--light.png` | UNCHANGED | 12417c1281d9511903ddfe5d90ec27972402b28cbfd53d27a81704e9d0128659 | 12417c1281d9511903ddfe5d90ec27972402b28cbfd53d27a81704e9d0128659 |
| `components--dialog--open--full--dark.png` | UNCHANGED | 658516ddfb910a804a2a1c903f79d86b637918c312e4ad0cefdefb7bba306651 | 658516ddfb910a804a2a1c903f79d86b637918c312e4ad0cefdefb7bba306651 |
| `components--dialog--open--full--light.png` | UNCHANGED | d0802f517cce8b3ffb55e3a210536bcf1eee78dc8ce173c2a8b06987e6b41dfd | d0802f517cce8b3ffb55e3a210536bcf1eee78dc8ce173c2a8b06987e6b41dfd |
| `components--drawer--closed--full--dark.png` | UNCHANGED | 3a23880327ee14fa9bb2129e23db725f4a0fa7b602295ba53331d7fe92dd95e5 | 3a23880327ee14fa9bb2129e23db725f4a0fa7b602295ba53331d7fe92dd95e5 |
| `components--drawer--closed--full--light.png` | UNCHANGED | 87da9a58f004be601d18b043b2eddb80a881d96a35e9a295c0a2851855c9b08b | 87da9a58f004be601d18b043b2eddb80a881d96a35e9a295c0a2851855c9b08b |
| `components--drawer--open--full--dark.png` | UNCHANGED | 89177c7a4d87f7c6d47ba499e2dd8def32ac4ad6d53793efa20a1d650b22b301 | 89177c7a4d87f7c6d47ba499e2dd8def32ac4ad6d53793efa20a1d650b22b301 |
| `components--drawer--open--full--light.png` | UNCHANGED | f2af162bb59466d6d3af98961b858c52c9966d80f32814f3ee1a0ac667abe2be | f2af162bb59466d6d3af98961b858c52c9966d80f32814f3ee1a0ac667abe2be |
| `components--empty-state--default--full--dark.png` | UNCHANGED | 00ebe5a1fb4d8f0bcae9cad3b1a8a1ad705e828c67ba93649fa61eeabf94ca2c | 00ebe5a1fb4d8f0bcae9cad3b1a8a1ad705e828c67ba93649fa61eeabf94ca2c |
| `components--empty-state--default--full--light.png` | UNCHANGED | fc608c250bd153f58ba53625b92ec5aeefba30f188c89c6b451811b0b066d36a | fc608c250bd153f58ba53625b92ec5aeefba30f188c89c6b451811b0b066d36a |
| `components--error-state--retryable--full--dark.png` | UNCHANGED | 95e877efe79f19166792bef6df47f17f376e677aba7bccc1870d996447fd6275 | 95e877efe79f19166792bef6df47f17f376e677aba7bccc1870d996447fd6275 |
| `components--error-state--retryable--full--light.png` | UNCHANGED | d14df0c76fddc633c968a984575d190192e80840a876734bfbd8083e5984cf65 | d14df0c76fddc633c968a984575d190192e80840a876734bfbd8083e5984cf65 |
| `components--error-state--unrecoverable--full--dark.png` | UNCHANGED | 5433294d678ee91518da15555b8b3630d74a04e8d83475f1b50da405e9433af5 | 5433294d678ee91518da15555b8b3630d74a04e8d83475f1b50da405e9433af5 |
| `components--error-state--unrecoverable--full--light.png` | UNCHANGED | 403d1287e9e6e0e5fc7b7a634362bfab9bde3b624a6bd31f1fd69a46b7aba622 | 403d1287e9e6e0e5fc7b7a634362bfab9bde3b624a6bd31f1fd69a46b7aba622 |
| `components--icon-button--checked--full--dark.png` | UNCHANGED | 92fd3d87c790490f7abef0ff92f0b47e0af790063bb71f01123d9df360a165a3 | 92fd3d87c790490f7abef0ff92f0b47e0af790063bb71f01123d9df360a165a3 |
| `components--icon-button--checked--full--light.png` | UNCHANGED | d009b3061519b65f92451ea1c08ba9c8f88fc8e00a56bf3e31204bbb5a4db589 | d009b3061519b65f92451ea1c08ba9c8f88fc8e00a56bf3e31204bbb5a4db589 |
| `components--icon-button--default--full--dark.png` | UNCHANGED | a76694f35f67dc4fc002b0d0bf7f331f93fe77d86b8c5d5921a7cbb782e87cbe | a76694f35f67dc4fc002b0d0bf7f331f93fe77d86b8c5d5921a7cbb782e87cbe |
| `components--icon-button--default--full--light.png` | UNCHANGED | dbe9ead20b6ee7668251604d59e9eac257327fd84f1f64927b9331d027ff06b6 | dbe9ead20b6ee7668251604d59e9eac257327fd84f1f64927b9331d027ff06b6 |
| `components--icon-button--hover--full--dark.png` | UNCHANGED | 36739cad328ce06cd45e1e060651668ceeff5b1b13d0154c9a51018034d554b2 | 36739cad328ce06cd45e1e060651668ceeff5b1b13d0154c9a51018034d554b2 |
| `components--icon-button--hover--full--light.png` | UNCHANGED | 0ee78de15661439f7382201ba67dab8d7123a1803cb9451ce5665d338fd1e74c | 0ee78de15661439f7382201ba67dab8d7123a1803cb9451ce5665d338fd1e74c |
| `components--page-thumb-strip--default--full--dark.png` | UNCHANGED | c0a1b356140f095b360aa0e13525b2577cc506a432020068441f36b95fea6626 | c0a1b356140f095b360aa0e13525b2577cc506a432020068441f36b95fea6626 |
| `components--page-thumb-strip--default--full--light.png` | UNCHANGED | 232e323c050233cde9ef3a2be0cdeded6948a3e6812cd49c7062c6b23597db7b | 232e323c050233cde9ef3a2be0cdeded6948a3e6812cd49c7062c6b23597db7b |
| `components--primary-button--default--full--dark.png` | UNCHANGED | 11fa85f9e7a5f03e6a32b8ef79bd2f944556310d4a506e888c03db45f7de794e | 11fa85f9e7a5f03e6a32b8ef79bd2f944556310d4a506e888c03db45f7de794e |
| `components--primary-button--default--full--light.png` | UNCHANGED | ccaf77f6cfc0095e4f14951805384f820a4895fba409900d0718ef165f112849 | ccaf77f6cfc0095e4f14951805384f820a4895fba409900d0718ef165f112849 |
| `components--primary-button--disabled--full--dark.png` | UNCHANGED | 19096cdb5df881d61ad3ae2f43f8ff6ac34aadbed4e5e501bc0a163790e65c3d | 19096cdb5df881d61ad3ae2f43f8ff6ac34aadbed4e5e501bc0a163790e65c3d |
| `components--primary-button--disabled--full--light.png` | UNCHANGED | 1ea6a98c677b17d93fb066256cac6a0894ac05bd0d2ef59b4ec527ab67f42834 | 1ea6a98c677b17d93fb066256cac6a0894ac05bd0d2ef59b4ec527ab67f42834 |
| `components--primary-button--hover--full--dark.png` | UNCHANGED | 058ccb1d999c4e4f39f51328c51faaebbf7d0d10425e2493bb9569546405c27a | 058ccb1d999c4e4f39f51328c51faaebbf7d0d10425e2493bb9569546405c27a |
| `components--primary-button--hover--full--light.png` | UNCHANGED | a221df936ec221b8a3e4abfc2c64ef1e4f0e0389fb52cdcadd5a7d5c0483e34f | a221df936ec221b8a3e4abfc2c64ef1e4f0e0389fb52cdcadd5a7d5c0483e34f |
| `components--primary-button--pressed--full--dark.png` | UNCHANGED | 7bd2d5cf594bcbe8527a3e59a3b7706b3b63b67ed2285de07f1550c0c1c2a955 | 7bd2d5cf594bcbe8527a3e59a3b7706b3b63b67ed2285de07f1550c0c1c2a955 |
| `components--primary-button--pressed--full--light.png` | UNCHANGED | 966913b84077ce64a6cd571bb7b158b78b3d0b859d7e4663355ec4d662301f01 | 966913b84077ce64a6cd571bb7b158b78b3d0b859d7e4663355ec4d662301f01 |
| `components--reader-page--single--full--dark.png` | UNCHANGED | bcc7af72ece3d9b5e125c63a71c403d5c33be00bbab7ceda1532bb4efab95182 | bcc7af72ece3d9b5e125c63a71c403d5c33be00bbab7ceda1532bb4efab95182 |
| `components--reader-page--single--full--light.png` | UNCHANGED | e3f00ce494d670cf1e68710b0fb1c7a82491ef1a401a23ecba369bc103cccd55 | e3f00ce494d670cf1e68710b0fb1c7a82491ef1a401a23ecba369bc103cccd55 |
| `components--reader-progress--default--full--dark.png` | UNCHANGED | 58c8d0d619c7e0bd14466c858781cb6124ced8c676744020b9309b97f7bf690a | 58c8d0d619c7e0bd14466c858781cb6124ced8c676744020b9309b97f7bf690a |
| `components--reader-progress--default--full--light.png` | UNCHANGED | 0beab56ff843af1299a11b62a6eecf27871645195cd620dab18f689d3a045a31 | 0beab56ff843af1299a11b62a6eecf27871645195cd620dab18f689d3a045a31 |
| `components--region-box--default--full--dark.png` | UNCHANGED | f3b894536c2572c74ec509e12d62a10c47cb8108c1f275ccf2af1e602d3e4426 | f3b894536c2572c74ec509e12d62a10c47cb8108c1f275ccf2af1e602d3e4426 |
| `components--region-box--default--full--light.png` | UNCHANGED | c9d3be1cc6e7142e8f8beb303619091a6644123948e672f920da4acd21bc0051 | c9d3be1cc6e7142e8f8beb303619091a6644123948e672f920da4acd21bc0051 |
| `components--region-box--hover--full--dark.png` | UNCHANGED | f62a1758ab3074ac07b2434cbf4e9dce6f55640331522edb2e706b4554d6d42d | f62a1758ab3074ac07b2434cbf4e9dce6f55640331522edb2e706b4554d6d42d |
| `components--region-box--hover--full--light.png` | UNCHANGED | 17f44ae5eb9b98aa30a1e446bdd0809522d3f376ecdf578addd59d3bf11ac600 | 17f44ae5eb9b98aa30a1e446bdd0809522d3f376ecdf578addd59d3bf11ac600 |
| `components--search-field--default--full--dark.png` | UNCHANGED | dbc55aaef36076c30c35a6bc0f18da5f79ce9299fa457ebfe5251836b0290bae | dbc55aaef36076c30c35a6bc0f18da5f79ce9299fa457ebfe5251836b0290bae |
| `components--search-field--default--full--light.png` | UNCHANGED | 27a98ef1deb62665126467e998639b74f366c4f8d76ac89abce5ad383c05cc5d | 27a98ef1deb62665126467e998639b74f366c4f8d76ac89abce5ad383c05cc5d |
| `components--search-field--focus--full--dark.png` | UNCHANGED | ca1645c4d6675445eb86d444829d8419e5256471524f8e462fab4b20f143a747 | ca1645c4d6675445eb86d444829d8419e5256471524f8e462fab4b20f143a747 |
| `components--search-field--focus--full--light.png` | UNCHANGED | b9d104868ae380e64b973d609c369f0a7a1883c886f5583edb8633d2204c089c | b9d104868ae380e64b973d609c369f0a7a1883c886f5583edb8633d2204c089c |
| `components--search-field--value--full--dark.png` | UNCHANGED | eff1c117102189d659c3c4d224d121ba36388b96ba74a8f5f4c1518f012acce1 | eff1c117102189d659c3c4d224d121ba36388b96ba74a8f5f4c1518f012acce1 |
| `components--search-field--value--full--light.png` | UNCHANGED | 9357d1f26a74a6bd8b6cfda1f20f515ea1698208b56aa62690cd8104152d3267 | 9357d1f26a74a6bd8b6cfda1f20f515ea1698208b56aa62690cd8104152d3267 |
| `components--secondary-button--default--full--dark.png` | UNCHANGED | 6225650c0f4293b861aa2eccc06c726ca717c977c935a68598443d2aa19f9220 | 6225650c0f4293b861aa2eccc06c726ca717c977c935a68598443d2aa19f9220 |
| `components--secondary-button--default--full--light.png` | UNCHANGED | e3bfe1fbe83bb94888ee20dd3818dd5bc8b6d80f85beb6aa945e1eab3b4c2a14 | e3bfe1fbe83bb94888ee20dd3818dd5bc8b6d80f85beb6aa945e1eab3b4c2a14 |
| `components--secondary-button--disabled--full--dark.png` | UNCHANGED | 36721b2c032c5db03e353bfdd3d3f44677c27b6cce80a6ac4620a8cac133c131 | 36721b2c032c5db03e353bfdd3d3f44677c27b6cce80a6ac4620a8cac133c131 |
| `components--secondary-button--disabled--full--light.png` | UNCHANGED | 2884f66463b69191dcefff138ed22551c1957cdce4f79620ca6b02b3b6e4ae98 | 2884f66463b69191dcefff138ed22551c1957cdce4f79620ca6b02b3b6e4ae98 |
| `components--secondary-button--hover--full--dark.png` | UNCHANGED | bb96910170e0fbdf3a921f6b58c89ce7b6da7fb79b0842da46b6763cf71b2615 | bb96910170e0fbdf3a921f6b58c89ce7b6da7fb79b0842da46b6763cf71b2615 |
| `components--secondary-button--hover--full--light.png` | UNCHANGED | e57ed5263bca2e360471898acbf01495f5115fda904c3101a6dea021837e3a8f | e57ed5263bca2e360471898acbf01495f5115fda904c3101a6dea021837e3a8f |
| `components--secondary-button--pressed--full--dark.png` | UNCHANGED | 61222ad0c8aaf2811461c14e78bd344af3294bad1c3452f9066823699169e4ed | 61222ad0c8aaf2811461c14e78bd344af3294bad1c3452f9066823699169e4ed |
| `components--secondary-button--pressed--full--light.png` | UNCHANGED | b0be52d745db064b268341b035a824771300f4f6e039616fe66322818e43c516 | b0be52d745db064b268341b035a824771300f4f6e039616fe66322818e43c516 |
| `components--segmented-control--hover--full--dark.png` | UNCHANGED | 28a542455894ce62b044bab1e8aac9497c5ea143f9dc0eaa1571f7d6bfb14122 | 28a542455894ce62b044bab1e8aac9497c5ea143f9dc0eaa1571f7d6bfb14122 |
| `components--segmented-control--hover--full--light.png` | UNCHANGED | 465c95af1b22d85ebf8abc205b3109b524e48e79c8b8a851c5c6df7169f6f18b | 465c95af1b22d85ebf8abc205b3109b524e48e79c8b8a851c5c6df7169f6f18b |
| `components--segmented-control--pressed--full--dark.png` | UNCHANGED | a3943901f5d06267c9ce416b44a73f1eb2543c1bd39263c5393095f497fcde47 | a3943901f5d06267c9ce416b44a73f1eb2543c1bd39263c5393095f497fcde47 |
| `components--segmented-control--pressed--full--light.png` | UNCHANGED | 29ce0fbc6992550f8d840354daa1370e7d45fc735433aac023cda548284f1336 | 29ce0fbc6992550f8d840354daa1370e7d45fc735433aac023cda548284f1336 |
| `components--segmented-control--selected--full--dark.png` | UNCHANGED | e3009ea3f427ce92841d2c2288b8cc847dc1fab4ab44c2c2ac9c467608520500 | e3009ea3f427ce92841d2c2288b8cc847dc1fab4ab44c2c2ac9c467608520500 |
| `components--segmented-control--selected--full--light.png` | UNCHANGED | b0eb26a82c36024b2007657eeee301567c888526e077f24eb0f89e64f8f8794d | b0eb26a82c36024b2007657eeee301567c888526e077f24eb0f89e64f8f8794d |
| `components--segmented-control--unselected--full--dark.png` | UNCHANGED | 5cb43a0b3307144d3fbb88636825b62638cb7462658cc9b70d8b017326ae7e40 | 5cb43a0b3307144d3fbb88636825b62638cb7462658cc9b70d8b017326ae7e40 |
| `components--segmented-control--unselected--full--light.png` | UNCHANGED | 8488e5063a86e0fd17beeafa260569714e3491cfbf0b902152e45248da22676d | 8488e5063a86e0fd17beeafa260569714e3491cfbf0b902152e45248da22676d |
| `components--settings-field--disabled--full--dark.png` | UNCHANGED | 6860034d4c29c33658afcbc3752a3c187516d6dd411c167562eed1aea058ddc0 | 6860034d4c29c33658afcbc3752a3c187516d6dd411c167562eed1aea058ddc0 |
| `components--settings-field--disabled--full--light.png` | UNCHANGED | 0e5f8d1d74f77f6aecb4bfc5a6f372c81165953393ac537b5bf0ceb202f625d3 | 0e5f8d1d74f77f6aecb4bfc5a6f372c81165953393ac537b5bf0ceb202f625d3 |
| `components--settings-field--error--full--dark.png` | UNCHANGED | 8bc7233b0d73cf6f53de6b975933f9215075ede8b1f7030a136af4f3a20dcb86 | 8bc7233b0d73cf6f53de6b975933f9215075ede8b1f7030a136af4f3a20dcb86 |
| `components--settings-field--error--full--light.png` | UNCHANGED | d7550f543ac0d743f328a2f832b3b667bb1942e58d703864a16094ab3dabf19b | d7550f543ac0d743f328a2f832b3b667bb1942e58d703864a16094ab3dabf19b |
| `components--skeleton--bookcard--full--dark.png` | UNCHANGED | b4c23048c005e5586c44d05f505205fe395f0115de5f7ebc4e9f28ce3808c274 | b4c23048c005e5586c44d05f505205fe395f0115de5f7ebc4e9f28ce3808c274 |
| `components--skeleton--bookcard--full--light.png` | UNCHANGED | 851e1f1010efe1f3f8f0b47e4e1bb615a23120d5c8bca9d8e9fd06d11704a3d3 | 851e1f1010efe1f3f8f0b47e4e1bb615a23120d5c8bca9d8e9fd06d11704a3d3 |
| `components--skeleton--panel--full--dark.png` | UNCHANGED | 80b35caafbc126f921557f83f286d8181faf3ab4da629d3bdf28026605c10623 | 80b35caafbc126f921557f83f286d8181faf3ab4da629d3bdf28026605c10623 |
| `components--skeleton--panel--full--light.png` | UNCHANGED | 51e7b0bae6c7e7a3d756ed912156ae74bc4f0d549b8145b75097cc3a2532f22c | 51e7b0bae6c7e7a3d756ed912156ae74bc4f0d549b8145b75097cc3a2532f22c |
| `components--skeleton--row--full--dark.png` | UNCHANGED | c467ecc7edf60eb05436ff3b6ce28dced2b37ada5ed218177ac7542a3bbd22e3 | c467ecc7edf60eb05436ff3b6ce28dced2b37ada5ed218177ac7542a3bbd22e3 |
| `components--skeleton--row--full--light.png` | UNCHANGED | f0d55c31d58648991c094e2010dd09034075d7c5986d077652b846cb02c40deb | f0d55c31d58648991c094e2010dd09034075d7c5986d077652b846cb02c40deb |
| `components--slider--default--full--dark.png` | UNCHANGED | ce971a4da37eb85f49984872bd59047eae23a6b1ddfc6de7dace352492d97768 | ce971a4da37eb85f49984872bd59047eae23a6b1ddfc6de7dace352492d97768 |
| `components--slider--default--full--light.png` | UNCHANGED | a9c0e297603c3bcfb861df94a0e2abdd483bee21ed5de80f88968174e453ee4d | a9c0e297603c3bcfb861df94a0e2abdd483bee21ed5de80f88968174e453ee4d |
| `components--slider--disabled--full--dark.png` | UNCHANGED | afc956e90e3da7f0ea600c29adf7bf3ca1b506a61f269d11d9dbfc48efe571ea | afc956e90e3da7f0ea600c29adf7bf3ca1b506a61f269d11d9dbfc48efe571ea |
| `components--slider--disabled--full--light.png` | UNCHANGED | be751e7678927cc6a76d8f135538293e418f1f497d3d7c2a5b4d266dfc295dbc | be751e7678927cc6a76d8f135538293e418f1f497d3d7c2a5b4d266dfc295dbc |
| `components--slider--hover--full--dark.png` | UNCHANGED | 006731cca2a8e34b29dd5c5742d6c19c4e5e210cc59174b862cb0837e1e6a037 | 006731cca2a8e34b29dd5c5742d6c19c4e5e210cc59174b862cb0837e1e6a037 |
| `components--slider--hover--full--light.png` | UNCHANGED | 7632eb4ee7f4f58f7897dd72fc78986b68b7ae5d33472ed8b13d8bff176ed6e4 | 7632eb4ee7f4f58f7897dd72fc78986b68b7ae5d33472ed8b13d8bff176ed6e4 |
| `components--streaming-thumb--lazy--full--dark.png` | UNCHANGED | 70da80c565c842c894ff3ad7ca3d8be6ba6c903de1b0bf5f9b7146f02d0e5231 | 70da80c565c842c894ff3ad7ca3d8be6ba6c903de1b0bf5f9b7146f02d0e5231 |
| `components--streaming-thumb--lazy--full--light.png` | UNCHANGED | 9fe5f380156f6c1efe36f680e43b27820ad8858a9f1a5ab1127a3cd0c9f79938 | 9fe5f380156f6c1efe36f680e43b27820ad8858a9f1a5ab1127a3cd0c9f79938 |
| `components--surface-card--default--full--dark.png` | UNCHANGED | a1b460f11e58a8d929ae23da500b4c5a0b81773b12fc590b722cd87de9df721a | a1b460f11e58a8d929ae23da500b4c5a0b81773b12fc590b722cd87de9df721a |
| `components--surface-card--default--full--light.png` | UNCHANGED | 4749378885e3e70debe7fe35002fd1e3c9289e8963dd5a1e3c889a8be74b89e6 | 4749378885e3e70debe7fe35002fd1e3c9289e8963dd5a1e3c889a8be74b89e6 |
| `components--surface-card--disabled--full--dark.png` | UNCHANGED | 165d3b8bdcab65efa970b623293d1fa78a602396ba2e60570d9f62fd2669200c | 165d3b8bdcab65efa970b623293d1fa78a602396ba2e60570d9f62fd2669200c |
| `components--surface-card--disabled--full--light.png` | UNCHANGED | ac7ae33a835b6de04820ee3424d4a0b3a18b273d25da71390368aa4c3fe39849 | ac7ae33a835b6de04820ee3424d4a0b3a18b273d25da71390368aa4c3fe39849 |
| `components--surface-card--hover--full--dark.png` | UNCHANGED | 0015cb721aad1d66d06b48185a24ea331401e92df1804c573b843f0ea1178830 | 0015cb721aad1d66d06b48185a24ea331401e92df1804c573b843f0ea1178830 |
| `components--surface-card--hover--full--light.png` | UNCHANGED | be6d587c1a2ba68e7d46e2d42e83fd953e37e527f9ba28f0762d4b8c5133f8c5 | be6d587c1a2ba68e7d46e2d42e83fd953e37e527f9ba28f0762d4b8c5133f8c5 |
| `components--surface-card--selected--full--dark.png` | UNCHANGED | 4efa48c6452907a3a924900bdf81891da0c67e5f664a082ec071923d74d3bf36 | 4efa48c6452907a3a924900bdf81891da0c67e5f664a082ec071923d74d3bf36 |
| `components--surface-card--selected--full--light.png` | UNCHANGED | 2039281e84b426718778c598d8a4d5dff5dee7a69c10e4fd78acdde9783051a7 | 2039281e84b426718778c598d8a4d5dff5dee7a69c10e4fd78acdde9783051a7 |
| `components--tab-strip--hover--full--dark.png` | UNCHANGED | 623b8ea1a98828ec37d781355254ebfab850ed923783c579a40fc573739d3665 | 623b8ea1a98828ec37d781355254ebfab850ed923783c579a40fc573739d3665 |
| `components--tab-strip--hover--full--light.png` | UNCHANGED | 658d18952dcbbea6904f41678644cd738d7419745ac8c2f658f6c5fb5a8ae21d | 658d18952dcbbea6904f41678644cd738d7419745ac8c2f658f6c5fb5a8ae21d |
| `components--tab-strip--selected--full--dark.png` | UNCHANGED | 19f32c0ca252617b9f73971d3069ae7cd22b59551ca65aa7c34275d8552ad84e | 19f32c0ca252617b9f73971d3069ae7cd22b59551ca65aa7c34275d8552ad84e |
| `components--tab-strip--selected--full--light.png` | UNCHANGED | 1490841169568214e09db6778d3e2a35c1fdf2534223768d444b661281637f7a | 1490841169568214e09db6778d3e2a35c1fdf2534223768d444b661281637f7a |
| `components--tab-strip--unselected--full--dark.png` | UNCHANGED | f297bca8d40097d2d4745750baa7bf59fc59bccadbcf2185547838fca6b9febd | f297bca8d40097d2d4745750baa7bf59fc59bccadbcf2185547838fca6b9febd |
| `components--tab-strip--unselected--full--light.png` | UNCHANGED | f5925ef1b3727fb1b3e2c452630c8e19535d8c2845b02002163e42b9377f5820 | f5925ef1b3727fb1b3e2c452630c8e19535d8c2845b02002163e42b9377f5820 |
| `components--toggle-switch--disabled--full--dark.png` | UNCHANGED | 7e34408cb5a2f821aace06faa7c44062dd6117b00dbf9159072d221f986f9f7b | 7e34408cb5a2f821aace06faa7c44062dd6117b00dbf9159072d221f986f9f7b |
| `components--toggle-switch--disabled--full--light.png` | UNCHANGED | d68de31cc8842ba81d9e7fad06218af91878e9d85b79de09636acd9d4847dd68 | d68de31cc8842ba81d9e7fad06218af91878e9d85b79de09636acd9d4847dd68 |
| `components--toggle-switch--off--full--dark.png` | UNCHANGED | 0c2923ce72c87666b9118d66bf5055fd07a2ef9fd691f0e2df2967230651c721 | 0c2923ce72c87666b9118d66bf5055fd07a2ef9fd691f0e2df2967230651c721 |
| `components--toggle-switch--off--full--light.png` | UNCHANGED | 5c480ea9f571df916d0bdac7f24fee7d0f3ab57dbf50c872e77bea2d34938177 | 5c480ea9f571df916d0bdac7f24fee7d0f3ab57dbf50c872e77bea2d34938177 |
| `components--toggle-switch--on--full--dark.png` | UNCHANGED | 3f7443f2bd2d5bc4b56026a0e7de252ae45bf3510b2b8b58c0290ca63f56fe85 | 3f7443f2bd2d5bc4b56026a0e7de252ae45bf3510b2b8b58c0290ca63f56fe85 |
| `components--toggle-switch--on--full--light.png` | UNCHANGED | e170cbc574001e2be3156434f5260f3858522dc03cdeb2983cadea70be186668 | e170cbc574001e2be3156434f5260f3858522dc03cdeb2983cadea70be186668 |
| `components--tooltip--opened--full--dark.png` | UNCHANGED | 0e289319b382638cb22078db49434dab763d5c8ef05b8220d4c34affc4bd262b | 0e289319b382638cb22078db49434dab763d5c8ef05b8220d4c34affc4bd262b |
| `components--tooltip--opened--full--light.png` | UNCHANGED | ef8d97e3980922b0e47039f8af4037011ff2afcdaeb9851165028bb2e22ef5cd | ef8d97e3980922b0e47039f8af4037011ff2afcdaeb9851165028bb2e22ef5cd |
| `decor--page-turn-particles--mid--full--dark.png` | CHANGED | 14c1dcc32f450c4ba1846d05783736fe7dc9cae91f2e03b96cb205b404040a86 | 60ef983fbc08f8f20dd5ccde540e1ee1cf5421786878979b4c49e5aca4551e7d |
| `decor--page-turn-particles--mid--full--light.png` | CHANGED | 0864dfc650398625f8769ea671149575682407407fa3e866100fd9e6becf9cdc | 76af16f65b6cc8391085c94be470526dd6335632ecd33eb5aa29a6d90bcd0156 |
| `decor--page-turn-particles--none--reduce--dark.png` | CHANGED | bab63c8cc33bd41a4928e72d14416f50017f9d038f5bd3923054957a17ad4dfe | 147d8e823c74bdfcb7e4657eb6d170bd91c70c9b3055c54ce318fbfca6f7bc15 |
| `decor--page-turn-particles--none--reduce--light.png` | CHANGED | 8c9eab59f3ac10634cbe1ea4e5f90421ea994d3da420dd6b42dcd2cf81a76fe2 | 70ca25c5f96fccf2388ba8f4867914215b05983c3c8d7da81683284af75258d7 |
| `decor--shelf-gradient--first--full--dark.png` | CHANGED | 020dcad839edbbaf4436759d324be37a9f6e3231e3a483617fa5ecc6acb97e9d | 21cce1e1d2a0242eab3dab1de2e4ad55c06b749a344c77894bc973e2d37d13cc |
| `decor--shelf-gradient--first--full--light.png` | CHANGED | cbd2002b9a9d35685d0e65be3f785cfd4b73df73c95d1f0a53943823ef916b04 | 82110d66080079d45685eaeb4822cb832de5ae8953ac4dbf170e9faac26f3c0b |
| `decor--shelf-gradient--mid--full--dark.png` | CHANGED | dd83438a906d69d37ca6b6604edeb332851bc9bf28ba99ab056278fa09ee0608 | e177a608a9b584750367b64690050f1de1020267fe8245eede77ac370c0db013 |
| `decor--shelf-gradient--mid--full--light.png` | CHANGED | 47a27ce65e02c437c58bf96337b15c0d50ee8aef6ccdb98a1f3006a0fbb9efd8 | f97267f34dff055666d4a8c05b929a63223dff160ec911053809d093c4b2f41e |
| `decor--shelf-gradient--static--reduce--dark.png` | CHANGED | b28c71ef98e10e9acd4d9fb20eb88faabd538455b90e91dbb5d02d00d48099ce | f034f7a4d703a484a90655bcb2e9eb45430e03dbf4c351cf9c3ea7d40e86806c |
| `decor--shelf-gradient--static--reduce--light.png` | CHANGED | 802d443320310f55eb8bd7cad0164b2a11edffa58f3c1a055ae0a58ea4e7cf85 | 845e4b631962087ef6c2b584759e7f696711b2d9416c17fa6acf6aeb26aed211 |
| `pages--reader--default--full--dark.png` | CHANGED | 45ee45c0a7a58f034e8fbd8a5336feac3bb06b1df1c7e23ffa0e158bac6cc7bd | b583c6c40127f0771011c5a58095bd5b995a3151a95d12013c23b0df2a630381 |
| `pages--reader--default--full--light.png` | CHANGED | 75d9fb3ebee3fff8b5b7a05210271dd8706b818fac59976457f6d9b9e6d494a7 | a86b165e8a6baa39d39a89438a5bd1573926748e138a3d2f9fc16f4dd7101d83 |
| `pages--settings--default--full--dark.png` | CHANGED | 1d6c9ac14cfc37923a2999c8ea9b3248dd13813ce41d575f3439f56e7c08df2b | 76e680dafdbb7fc831de461b21e6d4541817a53e7f3955d2931d6e7ff77de190 |
| `pages--settings--default--full--light.png` | CHANGED | 2baf4e65dcb70bc36751c4f9d3757e4374d12413b4215488c2d29a37ff565402 | f56b3e2b5b3d8bd8e3c602018bab5e8b27c8057543ac31a76bde3aa63a69b50a |
| `pages--shelf--default--full--dark.png` | CHANGED | b61390e148a05d50e574c0174022ab493609436a32d7f6fafd03496f02a8fa19 | 75be3b1294b7f61b48e67c237428bf5f7f9d6d441e208e661814dbaac4824426 |
| `pages--shelf--default--full--light.png` | CHANGED | 70f3633d1c88d3708f0452cc2692cdc4b2bd4b3557ab928d0916eac032065df1 | d82d005aa2743fd02022fb68078c722b99fdc7bae2db5fb57f5de42ed0e5901a |
| `pages--workbench--default--full--dark.png` | CHANGED | d035f48dc31f550f23f37e702d5df838b860b6de6c822ea5331ef97d25f18862 | 47bd41ff7ee547758f7c2f26a211c8db4a77f3bf8d7affed62f764901d2902d3 |
| `pages--workbench--default--full--light.png` | CHANGED | 4ed18c299cd6bec1e994542288abc0c1b819f2a91c2b66c36c15090a52c5c2e4 | 9a44fcc96f7f2709f00124f9ed5f98eeb5d31caa4793b5c0f85fbca1b9440b22 |
| `shell--nav-rail--collapsed-1280--full--dark.png` | ADDED | — | 10f78d37500a627d0eb3d47f53ddd329663e549746ac35746fc2647406888734 |
| `shell--nav-rail--collapsed-1280--full--light.png` | ADDED | — | c18af4d233c6af1a1bd077209b5f2163c800316e0e3891ef39dd75dbb055b5e4 |
| `shell--status-band--error-1280--full--dark.png` | ADDED | — | d4fd91d3ea864f01f506ecd1aba63054204972a904800f950ff6345b756da8aa |
| `shell--status-band--error-1280--full--light.png` | ADDED | — | 81b253677264b7460de1ada972263a86ac70393f32446a4c94aa713a39f52932 |
| `shell--status-band--running-1280--full--dark.png` | ADDED | — | 5fbfd830ca67ce57878fd733a925e40c40779cdfed63ad205f4b2a5f43b931d7 |
| `shell--status-band--running-1280--full--light.png` | ADDED | — | 9ee323e81ba1e8e89c9f22a9c05412f213d5cc37b86e066986170dd8a4ee6a29 |
| `shell--top-nav-status--compact--full--dark.png` | REMOVED | 8992866848b4e6885b0e8305e1d6bacd9b3ab5221c5683c9fa4b81aff12ee0f9 | — |
| `shell--top-nav-status--compact--full--light.png` | REMOVED | fd72cd595af889868e52bfa06b33e1851e5b9fe930244515cece16444988d0c9 | — |
| `shell--top-nav-status--compact-1280--full--dark.png` | ADDED | — | f9d3ed353477b975da0ce5d6ebda2375782f6bcdf2dfb10bd7d2c469c1065ded |
| `shell--top-nav-status--compact-1280--full--light.png` | ADDED | — | f0bcdfb7da48e91641c584928a8c0e97dbd206dc1fc06ec49e98817fc225f1ef |
| `shell--top-nav-status--default--full--dark.png` | REMOVED | 3ae8b01c0ebaa6bf96ca7ed9e85b885209f049854e0b14e07282207849163c07 | — |
| `shell--top-nav-status--default--full--light.png` | REMOVED | ab66fb2897e977bb0c91063cc048b6ed350581b00c7995875db6ec7e42efb0b3 | — |
| `shell--top-nav-status--full-1600--full--dark.png` | ADDED | — | d21658e04e8f2d44e8c0c233bda16698ddab30b5fd663de24ed4fc62528e41df |
| `shell--top-nav-status--full-1600--full--light.png` | ADDED | — | 2c8b52d03865d651e97f9ed7eba55d72a84f25fe3055081676cc9a535a9b431f |
| `shell--top-nav-status--medium-1024--full--dark.png` | ADDED | — | d6a24a680fa4ab59537ceaf43d5286f2b83a7118a01cae0b0ce1172cfa02a60e |
| `shell--top-nav-status--medium-1024--full--light.png` | ADDED | — | d0914b0e52fe0fa9b691856cfc947b0487f2dfe5e9724ecde368e26fe407fe63 |

## 纯背景渐变像素（RGB 最大通道差）

crop相对窗口(216,95,1048,720)；纯背景横带窗口(250,740,1000,60)，换成crop坐标(34,645,1000,60)。

| theme | pair | max RGB delta (whole crop) | pixels >8 (whole crop) | pixels >8 (plain strip/60000) | mean abs RGB (strip) |
|---|---|---|---|---|---|
| light | first→mid(3000ms) | 15 | 142193 | 25114 | 6.5342 |
| light | first→reduce | 17 | 216473 | 31699 | 8.0049 |
| dark | first→mid(3000ms) | 23 | 307877 | 10475 | 4.6181 |
| dark | first→reduce | 27 | 377121 | 16219 | 5.4985 |

## Danger pressed 原图实色像素

中心按钮内部区域(195,155,130,30)统计：背景为最多的实色；文字为前景侧亮度极值（抗锯齿边缘不可能比其本色更极端）。属性断言另读实际PART_Root/ContentPresenter。

| theme | background RGB/count | foreground RGB/count | contrast |
|---|---|---|---|
| light | (161, 67, 45)/3457 | (250, 249, 247)/75 | 5.9467:1 |
| dark | (219, 148, 135)/3457 | (20, 21, 24)/75 | 7.4751:1 |
