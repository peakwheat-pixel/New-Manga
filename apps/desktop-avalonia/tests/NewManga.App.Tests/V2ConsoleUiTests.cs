using System.Reflection;
using Avalonia;
using Avalonia.Controls;
using Avalonia.Headless;
using Avalonia.Headless.XUnit;
using Avalonia.Input;
using Avalonia.Media;
using Avalonia.Threading;
using Avalonia.VisualTree;
using NewManga.App.Services;
using NewManga.CoreClient;
using NewManga.App.Shell.V2;
using NewManga.App.ViewModels.V2.Console;
using NewManga.App.Views.V2.Console;

namespace NewManga.App.Tests;

/// <summary>
/// V11R-B-2 L1 evidence: Console space with real headless rendering. Covers the nine sections,
/// credential masking (secret never echoed/retained), destructive confirmations (cancel-first, no
/// writes when blocked), network/provider real IPC calls and the honest 能力待接入 sections.
/// </summary>
public sealed class V2ConsoleUiTests
{
    private static FakeHostController Fixture()
    {
        var fake = V2Fixture.Create();
        V2Fixture.AddConsoleData(fake);
        return fake;
    }

    private static (Window Window, AppShellV2 Shell) Host(IHostController controller, double width = 1600, double height = 1000)
    {
        TestTheme.ResetToDefaults();
        var shell = new AppShellV2(controller);
        var window = new Window
        {
            Width = width,
            Height = height,
            Content = shell,
            Background = Brushes.Black,
        };
        window.Show();
        Dispatcher.UIThread.RunJobs();
        return (window, shell);
    }

    private static async Task<(Window Window, AppShellV2 Shell, ConsoleViewModel Console)> HostInConsoleAsync(
        IHostController controller,
        double width = 1600,
        double height = 1000)
    {
        var (window, shell) = Host(controller, width, height);
        await shell.Initialization;
        Assert.True(shell.HandleKeyForTest(Key.D3, KeyModifiers.Control));
        await shell.ViewModel.Console.InitializeAsync();
        Dispatcher.UIThread.RunJobs();
        return (window, shell, shell.ViewModel.Console);
    }

    /// <summary>R-19: temp-first capture (unique name incl. test method); repo sync only when curated.</summary>
    private static void Capture(Window window, string name, [System.Runtime.CompilerServices.CallerMemberName] string? testName = null)
    {
        Dispatcher.UIThread.RunJobs();
        var frame = window.CaptureRenderedFrame()
            ?? throw new InvalidOperationException($"{name}: CaptureRenderedFrame() returned null");
        var bytes = EvidenceFiles.SaveFrame(frame, "V11R-B-2", name, testName);
        Assert.True(bytes is null or > 4096, $"{name}: {bytes} bytes — blank/placeholder screenshot");
    }

    private static Color ResourceColor(string key) =>
        Application.Current!.TryGetResource(key, null, out var value) && value is ISolidColorBrush brush
            ? brush.Color
            : default;

    [AvaloniaFact]
    public async Task Console_HasNineSections_FiveRealAndFourHonestlyNotWired()
    {
        var (window, shell, console) = await HostInConsoleAsync(Fixture());
        Assert.Equal(9, console.Sections.Count);
        Assert.Equal(
            new[] { "01", "02", "03", "04", "05", "06", "07", "08", "09" },
            console.Sections.Select(section => section.Index).ToArray());

        var wired = console.Sections.Where(section => section.IsWired).Select(section => section.Id).ToArray();
        Assert.Equal(
            new[]
            {
                ConsoleSectionId.Tasks,
                ConsoleSectionId.Providers,
                ConsoleSectionId.Network,
                // REALUSE-DATA-SAFETY-4 AC1: ⑤ 缓存与版本清理 已接真实 cleanup.preview / cleanup.run。
                ConsoleSectionId.Storage,
                // REALUSE-DATA-SAFETY-1 AC2: ⑥ 备份与恢复 已接真实 Host 面。
                ConsoleSectionId.Backup,
                // REALUSE-DATA-SAFETY-4 AC1: ⑦ 插件与 Hooks 已接真实 plugins.* 面。
                ConsoleSectionId.Plugins,
                ConsoleSectionId.Diagnostics,
                ConsoleSectionId.Appearance,
            },
            wired);

        foreach (var section in console.Sections)
        {
            console.SelectSectionById(section.Id);
            Dispatcher.UIThread.RunJobs();
            if (section.IsWired)
            {
                Assert.False(console.IsNotWiredSection);
            }
            else
            {
                Assert.True(console.IsNotWiredSection);
                Assert.False(string.IsNullOrWhiteSpace(console.NotWiredBody));
                Assert.Contains("能力待接入", console.NotWiredBody, StringComparison.Ordinal);
                Assert.False(string.IsNullOrWhiteSpace(console.NotWiredRequirement));
            }
        }

        Assert.NotNull(shell.GetVisualDescendants().OfType<ConsoleView>().SingleOrDefault());
        window.Close();
    }

    [AvaloniaFact]
    public async Task Providers_CreateAndEdit_UseTheRealIpcDraft()
    {
        var controller = Fixture();
        var (window, shell, console) = await HostInConsoleAsync(controller);
        Assert.Equal(2, console.ProviderProfiles.Count);
        Assert.Equal("OpenAI · GPT", console.ProviderProfiles[0].DisplayName);
        Assert.True(console.ProviderProfiles[0].IsSelected);

        console.SelectSectionById(ConsoleSectionId.Providers);
        console.NewProviderCommand.Execute(null);
        Assert.True(console.IsProviderFormOpen);
        console.FormProviderId = "deepseek";
        console.FormDisplayName = "DeepSeek 翻译";
        console.FormEndpoint = "https://api.example.invalid";
        console.FormModel = "deepseek-chat";
        console.FormCapOcr = false;
        console.FormCapTranslation = true;
        console.FormCapInpaint = false;
        console.FormCapDetection = false;
        console.FormCapRendering = false;
        console.SaveProviderCommand.Execute(null);
        Dispatcher.UIThread.RunJobs();

        Assert.Single(controller.ProviderSaves);
        var (savedProfileId, draft) = controller.ProviderSaves[0];
        Assert.Null(savedProfileId);
        Assert.Equal("deepseek", draft.ProviderId);
        Assert.Equal(new[] { SettingsCapabilities.Translation }, draft.Capabilities.ToArray());
        Assert.Equal("deepseek-chat", draft.Model);
        Assert.Equal(3, console.ProviderProfiles.Count);
        Assert.False(console.IsProviderFormOpen);
        Assert.False(controller.ProviderSaves[0].Draft.Enabled == false);

        Capture(window, "01-console-providers");
        window.Close();
    }

    [AvaloniaFact]
    public async Task Credentials_DisplayStateOnly_AndTheSecretIsClearedAndNeverExposed()
    {
        var controller = Fixture();
        var (window, shell, console) = await HostInConsoleAsync(controller);
        console.SelectSectionById(ConsoleSectionId.Providers);

        var row = console.CredentialTargets.First(item => item.Kind == CredentialKinds.ProviderApi && item.OwnerId == "provider-1");
        Assert.Equal("未保存", row.StateLabel);
        Assert.Contains(console.CredentialTargets, item => item.Kind == CredentialKinds.ProviderApi
                                                          && item.OwnerId == "provider-2"
                                                          && item.StateLabel == "已保存");

        const string secret = "sk-ui-test-super-secret-value";
        row.SecretInput = secret;
        Assert.True(row.CanPut);
        row.PutCommand.Execute(null);
        Dispatcher.UIThread.RunJobs();

        // The secret WAS sent once through the credential command seam ...
        Assert.Single(controller.PutCredentialCalls);
        Assert.Equal(secret, controller.PutCredentialCalls[0].Secret);
        // ... and is gone from the UI afterwards, with the state refreshed to real Core state.
        Assert.Equal(string.Empty, row.SecretInput);
        Assert.False(row.HasSecretInput);
        Assert.Equal("已保存", row.StateLabel);

        // No public string property of the row/VM may still expose the secret.
        foreach (var target in new object[] { row, console })
        {
            foreach (var property in target.GetType().GetProperties(BindingFlags.Instance | BindingFlags.Public))
            {
                if (property.PropertyType != typeof(string))
                {
                    continue;
                }

                var value = property.GetValue(target) as string;
                Assert.DoesNotContain(secret, value ?? string.Empty, StringComparison.Ordinal);
            }
        }

        Capture(window, "02-console-credentials-state-only");
        window.Close();
    }

    [AvaloniaFact]
    public async Task DeleteProvider_RequiresConfirmation_AndCancelWritesNothing()
    {
        var controller = Fixture();
        var (window, shell, console) = await HostInConsoleAsync(controller);
        console.SelectSectionById(ConsoleSectionId.Providers);
        var provider = console.ProviderProfiles[1];
        provider.SelectCommand.Execute(null);
        Assert.Equal("provider-2", console.SelectedProvider?.ProfileId);

        console.DeleteSelectedProviderCommand.Execute(null);
        Assert.True(shell.ViewModel.IsConfirmOpen);
        Assert.Contains("不可撤销", shell.ViewModel.ConfirmBody, StringComparison.Ordinal);
        Assert.Contains("能力绑定会立即失效", shell.ViewModel.ConfirmBody, StringComparison.Ordinal);
        Assert.True(shell.ViewModel.ConfirmIsDanger);
        Assert.True(shell.ViewModel.ConfirmCanConfirm);

        // Cancel → nothing was deleted.
        shell.ViewModel.CancelConfirmCommand.Execute(null);
        Assert.Empty(controller.ProviderDeletes);

        // Esc closes the modal too (cancel-first keyboard path).
        console.DeleteSelectedProviderCommand.Execute(null);
        Assert.True(shell.HandleKeyForTest(Key.Escape, KeyModifiers.None));
        Assert.False(shell.ViewModel.IsConfirmOpen);
        Assert.Empty(controller.ProviderDeletes);

        // Confirming deletes through the real Host method.
        console.DeleteSelectedProviderCommand.Execute(null);
        shell.ViewModel.ConfirmCommand.Execute(null);
        Dispatcher.UIThread.RunJobs();
        Assert.Equal(new[] { "provider-2" }, controller.ProviderDeletes.ToArray());
        window.Close();
    }

    [AvaloniaFact]
    public async Task Network_TestAndDefault_UseTheRealHostSeams()
    {
        var controller = Fixture();
        controller.ScriptedNetworkTestResults.Enqueue(new NetworkTestInfo(
            "ok",
            null,
            false,
            new[] { new NetworkTestStageInfo("dns", "ok", null, 12) }));
        var (window, shell, console) = await HostInConsoleAsync(controller);
        console.SelectSectionById(ConsoleSectionId.Network);
        Assert.Equal(2, console.NetworkProfiles.Count);
        Assert.Contains("默认网络", console.DefaultNetworkText, StringComparison.Ordinal);

        console.TestSelectedNetworkCommand.Execute(null);
        Dispatcher.UIThread.RunJobs();
        Assert.Single(controller.NetworkTests);
        Assert.Equal("network-1", controller.NetworkTests[0].NetworkProfileId);
        Assert.Equal("provider-1", controller.NetworkTests[0].ProviderProfileId);
        Assert.Contains("status=ok", console.NetworkTestText, StringComparison.Ordinal);

        console.SetDefaultSelectedNetworkCommand.Execute(null);
        Dispatcher.UIThread.RunJobs();
        Assert.Equal(new[] { "network-1" }, controller.NetworkDefaults.ToArray());

        // Network form validates the TLS-confirmation safety rule before touching the Host.
        console.NewNetworkCommand.Execute(null);
        console.FormNetworkName = "不安全代理";
        console.FormProxyEndpoint = "127.0.0.1:1080";
        console.FormVerifyTls = false;
        console.FormConfirmDisableTls = false;
        console.SaveNetworkCommand.Execute(null);
        Dispatcher.UIThread.RunJobs();
        Assert.Empty(controller.NetworkSaves);
        Assert.Contains("TLS", shell.ViewModel.NoticeText, StringComparison.Ordinal);

        Capture(window, "03-console-network");
        window.Close();
    }

    [AvaloniaFact]
    public async Task NotWiredSections_ShowHonestBanner_AndBlockedDangerActionsAreCancelable()
    {
        var controller = Fixture();
        var (window, shell, console) = await HostInConsoleAsync(controller);

        // REALUSE-DATA-SAFETY-4 AC1: ⑤ Storage is a real pre-flight now, so the honest-placeholder
        // example moves to ④ Devices (still needs a Host device/weights command).
        console.SelectSectionById(ConsoleSectionId.Devices);
        Dispatcher.UIThread.RunJobs();
        Assert.True(console.IsNotWiredSection);
        Assert.Contains("能力待接入", console.NotWiredBody, StringComparison.Ordinal);
        Assert.Contains("依赖", console.NotWiredRequirement, StringComparison.Ordinal);
        Capture(window, "04-console-devices-not-wired");

        // ⑤ Storage: the destructive action is real and therefore still gated by the shared confirm.
        console.SelectSectionById(ConsoleSectionId.Storage);
        Dispatcher.UIThread.RunJobs();
        Assert.False(console.IsNotWiredSection);
        console.RequestClearCacheCommand.Execute(null);
        Dispatcher.UIThread.RunJobs();
        Assert.True(shell.ViewModel.IsConfirmOpen);
        Assert.True(shell.ViewModel.ConfirmCanConfirm, "a real cleanup must be confirmable");
        Capture(window, "08-console-danger-confirm");
        shell.ViewModel.CancelConfirmCommand.Execute(null);
        Assert.False(shell.ViewModel.IsConfirmOpen);

        // REALUSE-DATA-SAFETY-1 AC2: ⑥ 备份与恢复 is now a real section, so it no longer opens a
        // blocked "能力待接入" modal; without a selection the actions refuse up front instead.
        console.SelectSectionById(ConsoleSectionId.Backup);
        Dispatcher.UIThread.RunJobs();
        Assert.False(console.IsNotWiredSection);
        Assert.True(console.ShowBackupDanger);
        console.RequestDeleteBackupCommand.Execute(null);
        Assert.False(shell.ViewModel.IsConfirmOpen);
        Assert.Contains("请先选择一个备份包", shell.ViewModel.NoticeText, StringComparison.Ordinal);
        window.Close();
    }

    [AvaloniaFact]
    public async Task Appearance_TogglesRealDesignTokens_AndOpensThemeStudioSurface()
    {
        var (window, shell, console) = await HostInConsoleAsync(Fixture());
        var dark = ResourceColor("Nm.Color.Bg.Canvas");
        console.SelectSectionById(ConsoleSectionId.Appearance);
        Assert.Equal("深色（Dark）", console.AppearanceText);

        console.ToggleAppearanceCommand.Execute(null);
        Dispatcher.UIThread.RunJobs();
        Assert.Equal("浅色（Light）", console.AppearanceText);
        Assert.NotEqual(dark, ResourceColor("Nm.Color.Bg.Canvas"));
        Capture(window, "05-console-appearance-light");

        console.OpenThemeStudioCommand.Execute(null);
        Dispatcher.UIThread.RunJobs();
        Assert.True(shell.ViewModel.State.IsThemeStudioOpen);
        // The theme studio surface keeps the TopBand back semantics (Esc closes the surface).
        Assert.True(shell.HandleKeyForTest(Key.Escape, KeyModifiers.None));
        Assert.False(shell.ViewModel.State.IsThemeStudioOpen);
        window.Close();
    }

    [AvaloniaFact]
    public async Task Diagnostics_ShowsHostFacts_AndExportHistoryWithoutPaths()
    {
        var controller = Fixture();
        var (window, shell, console) = await HostInConsoleAsync(controller);
        console.SelectSectionById(ConsoleSectionId.Diagnostics);
        Dispatcher.UIThread.RunJobs();

        Assert.Equal("就绪", console.HostStateText);
        Assert.Equal("无", console.HostErrorCodeText);
        Assert.Equal(2, console.ExportHistory.Count);
        Assert.Contains("zip", console.ExportHistory[0].Format, StringComparison.OrdinalIgnoreCase);
        // No OS path is rendered from the export history (the Core path is never shown).
        Assert.DoesNotContain(":\\", console.ExportHistory[0].MetaText, StringComparison.Ordinal);

        console.ExportHistory[0].RevealCommand.Execute(null);
        Dispatcher.UIThread.RunJobs();
        Assert.Equal(new[] { "exp-1" }, controller.RevealCalls.ToArray());
        Assert.Contains("已请求", console.ExportHistory[0].RevealText, StringComparison.Ordinal);

        Capture(window, "06-console-diagnostics");
        window.Close();
    }

    [AvaloniaFact]
    public async Task Console_FailedSave_RendersTypedCodeOnly_NoPathOrSecretInNotice()
    {
        var controller = Fixture();
        var (window, shell, console) = await HostInConsoleAsync(controller);
        console.SelectSectionById(ConsoleSectionId.Providers);
        controller.ScriptedProviderSaveResults.Enqueue(new SettingsProfileResult(
            SettingsProfileStatus.Failed,
            "INVALID_REQUEST",
            @"C:\Users\someone\secret-config.json sk-live-should-not-leak")); // ci-allow-fixture-path: negative-test payload, asserts the notice redacts paths/secrets; not a real machine path
        console.NewProviderCommand.Execute(null);
        console.FormProviderId = "x";
        console.FormDisplayName = "X";
        console.SaveProviderCommand.Execute(null);
        Dispatcher.UIThread.RunJobs();

        Assert.Contains("INVALID_REQUEST", shell.ViewModel.NoticeText, StringComparison.Ordinal);
        Assert.DoesNotContain("C:\\", shell.ViewModel.NoticeText, StringComparison.Ordinal);
        Assert.DoesNotContain("sk-live", shell.ViewModel.NoticeText, StringComparison.Ordinal);
        window.Close();
    }

    [AvaloniaFact]
    public async Task Tasks_LoadsRealRunSnapshotAndProjection_AndHonorsRunControlRules()
    {
        var controller = Fixture();
        controller.ScriptedControlRuns.Enqueue(new RunControlInfo("run-1", "paused"));
        controller.ScriptedControlRuns.Enqueue(new RunControlInfo("run-1", "cancelled"));
        var (window, shell, console) = await HostInConsoleAsync(controller);
        console.SelectSectionById(ConsoleSectionId.Tasks);
        console.IsRunPollingEnabled = false; // deterministic: no 1s polling in the test
        console.RunIdInput = "run-1";
        console.LoadRunCommand.Execute(null);
        Dispatcher.UIThread.RunJobs();

        // Data comes from real IRunController calls, not UI-invented numbers.
        Assert.Equal(new[] { "run-1" }, controller.RunSnapshotRequests.ToArray());
        Assert.Equal(new[] { "run-1" }, controller.TaskProjectionRequests.ToArray());
        Assert.Equal("进行中", console.RunStatusText);
        Assert.Equal("translate", console.RunCommandText);
        Assert.Contains("chapter", console.RunScopeText, StringComparison.Ordinal);
        Assert.Equal("50%", console.RunProgressText);
        Assert.Contains("总 2", console.RunCountsText, StringComparison.Ordinal);
        Assert.Contains("完成 1", console.RunCountsText, StringComparison.Ordinal);
        Assert.Equal("inpaint", console.RunCurrentStepText);
        Assert.Equal(2, console.RunStages.Count);
        Assert.Equal(2, console.RunRows.Count);
        Assert.Equal("002.jpg", console.RunRows[1].Filename);
        Assert.True(console.RunCanPause);
        Assert.True(console.RunCanRestart);
        Assert.True(console.RunCanStop);

        // R-08: restart/retry need a caller-supplied idempotency key — the UI must not invent one.
        console.RestartRunCommand.Execute(null);
        Dispatcher.UIThread.RunJobs();
        Assert.Empty(controller.ControlRunRequests);
        Assert.Contains("幂等键", shell.ViewModel.NoticeText, StringComparison.Ordinal);

        console.RunIdempotencyKey = "idem-restart-1";
        console.RestartRunCommand.Execute(null);
        Dispatcher.UIThread.RunJobs();
        Assert.Single(controller.ControlRunRequests);
        Assert.Equal(("run-1", RunControlAction.Restart, "idem-restart-1"), controller.ControlRunRequests[0]);

        // Stop is destructive → confirmation first, cancel writes nothing.
        console.StopRunCommand.Execute(null);
        Assert.True(shell.ViewModel.IsConfirmOpen);
        Assert.Contains("进行中的步骤会终止", shell.ViewModel.ConfirmBody, StringComparison.Ordinal);
        shell.ViewModel.CancelConfirmCommand.Execute(null);
        Assert.Single(controller.ControlRunRequests);

        console.StopRunCommand.Execute(null);
        shell.ViewModel.ConfirmCommand.Execute(null);
        Dispatcher.UIThread.RunJobs();
        Assert.Equal(2, controller.ControlRunRequests.Count);
        Assert.Equal(RunControlAction.Stop, controller.ControlRunRequests[1].Action);

        Capture(window, "07-console-tasks-run");
        console.StopRunPolling();
        window.Close();
    }

    [AvaloniaFact]
    public async Task Tasks_WithoutRunId_DoesNotFabricateAnything()
    {
        var controller = Fixture();
        // Drain the fixture's scripted run so the section has no data until a real load happens.
        controller.ScriptedRunSnapshots.Clear();
        controller.ScriptedTaskProjections.Clear();
        var (window, shell, console) = await HostInConsoleAsync(controller);
        console.SelectSectionById(ConsoleSectionId.Tasks);
        console.IsRunPollingEnabled = false;
        console.RunIdInput = string.Empty;
        console.LoadRunCommand.Execute(null);
        Dispatcher.UIThread.RunJobs();
        Assert.Empty(controller.RunSnapshotRequests);
        Assert.False(console.HasRunLoaded);
        Assert.Empty(console.RunRows);
        Assert.Contains("run_id", shell.ViewModel.NoticeText, StringComparison.Ordinal);
        window.Close();
    }

    [AvaloniaFact]
    public async Task R24_ConsoleRunPolling_PausesOnLeave_AndResumesOnReentry()
    {
        var controller = Fixture();
        var (window, shell, console) = await HostInConsoleAsync(controller);
        console.SelectSectionById(ConsoleSectionId.Tasks);
        console.RunIdInput = "run-1";
        console.LoadRunCommand.Execute(null);
        Dispatcher.UIThread.RunJobs();

        Assert.True(console.HasRunLoaded);
        Assert.True(shell.ViewModel.RunMonitor.IsPollingEnabled);
        var snapshotsAfterLoad = controller.RunSnapshotRequests.Count;
        var projectionsAfterLoad = controller.TaskProjectionRequests.Count;
        Assert.True(snapshotsAfterLoad > 0);
        Assert.True(projectionsAfterLoad > 0);

        // Leave the Console: the shared poller must pause (no background Host reads).
        Assert.True(shell.HandleKeyForTest(Key.D1, KeyModifiers.Control));
        Dispatcher.UIThread.RunJobs();
        Assert.False(shell.ViewModel.RunMonitor.IsPollingEnabled);
        var snapshotsWhileAway = controller.RunSnapshotRequests.Count;
        var projectionsWhileAway = controller.TaskProjectionRequests.Count;

        // Re-enter with the same run: subscription resumes and one immediate shared refresh is made.
        Assert.True(shell.HandleKeyForTest(Key.D3, KeyModifiers.Control));
        Dispatcher.UIThread.RunJobs();
        Assert.True(shell.ViewModel.RunMonitor.IsPollingEnabled);
        Assert.True(controller.RunSnapshotRequests.Count > snapshotsWhileAway,
            "re-entry must resume the shared snapshot subscription without waiting for the timer");
        Assert.True(controller.TaskProjectionRequests.Count > projectionsWhileAway,
            "re-entry must resume the shared projection subscription without waiting for the timer");
        Assert.Equal("run-1", console.RunIdInput);
        window.Close();
    }

    [AvaloniaFact]
    public async Task R23_WiringAndSavedStates_UseNeutralVocabulary_NotSevenStateStatus()
    {
        var controller = Fixture();
        var (window, shell, console) = await HostInConsoleAsync(controller);
        console.SelectSectionById(ConsoleSectionId.Providers);
        Dispatcher.UIThread.RunJobs();

        // The NmStatus projections that expressed "wired / saved / bound" are gone at the API level.
        Assert.Null(typeof(ConsoleSectionItem).GetProperty("Status", BindingFlags.Public | BindingFlags.Instance));
        Assert.Null(typeof(CredentialTargetRowViewModel).GetProperty("StateStatus", BindingFlags.Public | BindingFlags.Instance));
        Assert.Null(typeof(CapabilityBindingRowViewModel).GetProperty("BindingStatus", BindingFlags.Public | BindingFlags.Instance));

        var sevenStateWords = Enum.GetValues<NmStatus>()
            .SelectMany(status => new[] { NmStatusInfo.Label(status), NmStatusInfo.Symbol(status) })
            .Where(text => !string.IsNullOrWhiteSpace(text))
            .ToHashSet(StringComparer.Ordinal);

        Assert.NotEmpty(console.Sections);
        Assert.All(console.Sections, section =>
        {
            Assert.Contains(section.WiringText, new[] { "已接入", "待接入" });
            Assert.False(sevenStateWords.Contains(section.WiringText),
                $"section wiring must not use the seven-state vocabulary: {section.WiringText}");
        });

        Assert.NotEmpty(console.CredentialTargets);
        Assert.All(console.CredentialTargets, row =>
        {
            Assert.Contains(row.StateLabel, new[] { "已保存", "未保存" });
            Assert.False(sevenStateWords.Contains(row.StateLabel),
                $"credential state must not use the seven-state vocabulary: {row.StateLabel}");
        });

        Assert.NotEmpty(console.CapabilityBindings);
        Assert.All(console.CapabilityBindings, row =>
        {
            Assert.False(sevenStateWords.Contains(row.BindingText),
                $"binding state must not use the seven-state vocabulary: {row.BindingText}");
        });

        window.Close();
    }

    // ---------------------------------------------------------------------------------------
    // REALUSE-DATA-SAFETY-1 AC2: ⑥ 备份与恢复接到真实 Host 面（列表 / 创建 / 删除 / 恢复确认）
    // ---------------------------------------------------------------------------------------

    private static async Task WaitUntilAsync(Func<bool> predicate, int timeoutMs = 5000)
    {
        var deadline = DateTime.UtcNow.AddMilliseconds(timeoutMs);
        while (DateTime.UtcNow < deadline)
        {
            if (predicate())
            {
                return;
            }

            await Task.Delay(20);
            Dispatcher.UIThread.RunJobs();
        }

        Assert.True(predicate(), "condition not reached before timeout");
    }

    [AvaloniaFact]
    public async Task BackupSection_listsRealPackages_andCreatesThroughHost()
    {
        var fake = Fixture();
        fake.Backups.Add(new NewManga.CoreClient.BackupPackageInfo(
            "0123456789abcdef0123456789abcdef",
            "automatic",
            "2026-10-30T00:00:00+00:00",
            90L * 1024 * 1024,
            6,
            true));

        var (window, _shell, console) = await HostInConsoleAsync(fake);
        window.Close();

        console.SelectSectionById(ConsoleSectionId.Backup);
        await WaitUntilAsync(() => fake.BackupCalls.Contains("list") && !console.IsBackupBusy);

        Assert.True(console.IsBackupSection);
        Assert.False(console.IsNotWiredSection);
        Assert.Single(console.BackupEntries);
        Assert.Contains("90.0 MiB", console.BackupEntries[0].SizeText, StringComparison.Ordinal);
        Assert.Contains("已验证", console.BackupEntries[0].VerifiedText, StringComparison.Ordinal);
        Assert.Contains("共 1 个包", console.BackupStatusText, StringComparison.Ordinal);

        console.RequestCreateBackupCommand.Execute(null);
        await WaitUntilAsync(() => fake.BackupCalls.Contains("create") && console.BackupEntries.Count == 2);

        Assert.Equal(2, console.BackupEntries.Count);
        Assert.True(console.HasBackupResult);
        Assert.Contains("已创建", console.BackupLastResult, StringComparison.Ordinal);
    }

    [AvaloniaFact]
    public async Task BackupDelete_requiresSelectionAndConfirmation()
    {
        var fake = Fixture();
        fake.Backups.Add(new NewManga.CoreClient.BackupPackageInfo(
            "fedcba9876543210fedcba9876543210",
            "manual",
            "2026-10-30T01:00:00+00:00",
            2048,
            6,
            true));

        var (window, shell, console) = await HostInConsoleAsync(fake);
        window.Close();

        console.SelectSectionById(ConsoleSectionId.Backup);
        await WaitUntilAsync(() => fake.BackupCalls.Contains("list") && !console.IsBackupBusy);
        Assert.Single(console.BackupEntries);

        // No selection: refused up front, no modal, no Host call.
        console.RequestDeleteBackupCommand.Execute(null);
        Assert.False(shell.ViewModel.IsConfirmOpen);
        Assert.DoesNotContain(fake.BackupCalls, call => call.StartsWith("delete:", StringComparison.Ordinal));

        console.SelectedBackup = console.BackupEntries[0];
        console.RequestDeleteBackupCommand.Execute(null);
        Assert.True(shell.ViewModel.IsConfirmOpen);
        Assert.True(shell.ViewModel.ConfirmIsDanger);

        shell.ViewModel.ConfirmCommand.Execute(null);
        await WaitUntilAsync(() => fake.BackupCalls.Any(call => call.StartsWith("delete:", StringComparison.Ordinal))
                                   && !console.IsBackupBusy);

        Assert.Contains("delete:fedcba9876543210fedcba9876543210", fake.BackupCalls);
        Assert.Empty(console.BackupEntries);
        Assert.Contains("已删除", console.BackupLastResult, StringComparison.Ordinal);
    }

    [AvaloniaFact]
    public async Task BackupRestore_requiresSelectionAndExplainsOverwrite()
    {
        var fake = Fixture();
        fake.Backups.Add(new NewManga.CoreClient.BackupPackageInfo(
            "aaaabbbbccccddddeeeeffff00001111",
            "pre_migration",
            "2026-10-30T02:00:00+00:00",
            1024,
            6,
            true));

        var (window, shell, console) = await HostInConsoleAsync(fake);
        window.Close();

        console.SelectSectionById(ConsoleSectionId.Backup);
        await WaitUntilAsync(() => fake.BackupCalls.Contains("list") && !console.IsBackupBusy);

        console.SelectedBackup = console.BackupEntries[0];
        console.RequestRestoreBackupCommand.Execute(null);
        Assert.True(shell.ViewModel.IsConfirmOpen);
        Assert.Contains("pre_restore", shell.ViewModel.ConfirmBody, StringComparison.Ordinal);

        shell.ViewModel.ConfirmCommand.Execute(null);
        await WaitUntilAsync(() => fake.BackupCalls.Any(call => call.StartsWith("restore:", StringComparison.Ordinal)));

        Assert.Contains("restore:aaaabbbbccccddddeeeeffff00001111", fake.BackupCalls);
        Assert.Contains("回滚点", console.BackupLastResult, StringComparison.Ordinal);
    }

    // ── REALUSE-DATA-SAFETY-3 AC2 (audit MA-07) ─────────────────────────────────────────────

    /// <summary>
    /// A Run the session saw must be clickable in "任务与队列" instead of asking the user to copy a
    /// run_id from another window. The list is a memory aid over real ids; clicking one still loads
    /// through the normal Host read.
    /// </summary>
    [AvaloniaFact]
    public async Task TasksSection_ListsRunsThisSessionSaw_AndClickFillsTheInput()
    {
        var (window, shell, console) = await HostInConsoleAsync(Fixture());
        console.SelectSectionById(ConsoleSectionId.Tasks);
        Dispatcher.UIThread.RunJobs();

        // Nothing invented: a fresh session shows the honest empty hint, not a fake list.
        Assert.False(console.HasKnownRuns);
        Assert.Contains("本会话还没有出现过 Run", console.KnownRunsHint, StringComparison.Ordinal);

        // The shell records a Run the session actually obtained (Studio Batch does this on start).
        shell.ViewModel.RememberCreatedRun("run-session-7");
        Dispatcher.UIThread.RunJobs();

        Assert.True(console.HasKnownRuns);
        var row = Assert.Single(console.KnownRuns);
        Assert.Equal("run-session-7", row.RunId);
        Assert.True(row.IsMostRecent);

        row.SelectCommand.Execute(null);
        Dispatcher.UIThread.RunJobs();

        Assert.Equal("run-session-7", console.RunIdInput);

        window.Close();
    }

    // ── REALUSE-DATA-SAFETY-4 AC1 (audit MA-06): cache cleanup is real, not a placeholder ────

    /// <summary>
    /// The section used to be a permanent 待接入 placeholder because the Host never exposed
    /// cleanup.preview / cleanup.run. It now shows the Core's own pre-flight and only deletes after
    /// the shared confirmation gate.
    /// </summary>
    [AvaloniaFact]
    public async Task StorageSection_PreviewsThenDeletesOnlyAfterConfirmation()
    {
        var fake = Fixture();
        var (window, shell, console) = await HostInConsoleAsync(fake);
        console.SelectSectionById(ConsoleSectionId.Storage);
        Dispatcher.UIThread.RunJobs();

        Assert.True(fake.CleanupPreviewCalls >= 1, "opening the section must read the pre-flight");
        Assert.True(console.HasCleanupTargets);
        Assert.Contains("将清理 1 个", console.CleanupSummaryText, StringComparison.Ordinal);

        console.RequestClearCacheCommand.Execute(null);
        Dispatcher.UIThread.RunJobs();
        Assert.True(shell.ViewModel.IsConfirmOpen, "deleting cache must go through the confirm gate");
        Assert.Equal(0, fake.CleanupRunCalls);

        shell.ViewModel.ConfirmCommand.Execute(null);
        await WaitUntilAsync(() => fake.CleanupRunCalls == 1);
        Dispatcher.UIThread.RunJobs();

        Assert.Contains("已清理 1 个", console.CleanupLastResult ?? string.Empty, StringComparison.Ordinal);
        window.Close();
    }

    [AvaloniaFact]
    public async Task StorageSection_WithEmptyPreview_RefusesWithoutConfirming()
    {
        var fake = Fixture();
        fake.CleanupPreview = new CleanupPreviewInfo(Array.Empty<CleanupTargetInfo>(), 0, 0);
        var (window, shell, console) = await HostInConsoleAsync(fake);
        console.SelectSectionById(ConsoleSectionId.Storage);
        Dispatcher.UIThread.RunJobs();

        Assert.False(console.HasCleanupTargets);
        Assert.Contains("没有可安全清理", console.CleanupSummaryText, StringComparison.Ordinal);

        console.RequestClearCacheCommand.Execute(null);
        Dispatcher.UIThread.RunJobs();

        Assert.False(shell.ViewModel.IsConfirmOpen, "an empty preview must not open a destructive confirm");
        Assert.Equal(0, fake.CleanupRunCalls);
        window.Close();
    }

    [AvaloniaFact]
    public async Task StorageSection_SurfacesPendingFailuresFromTheCoreLedger()
    {
        var fake = Fixture();
        fake.CleanupPreview = new CleanupPreviewInfo(
            new[] { new CleanupTargetInfo("cache/tiles/abc.webp", 2048) }, 2048, 3);
        var (window, _, console) = await HostInConsoleAsync(fake);
        console.SelectSectionById(ConsoleSectionId.Storage);
        Dispatcher.UIThread.RunJobs();

        Assert.Contains("3 处上次删除失败", console.CleanupPendingText, StringComparison.Ordinal);
        window.Close();
    }

    // ── REALUSE-DATA-SAFETY-4 AC1: plugins are a real inventory, not a placeholder ───────────

    [AvaloniaFact]
    public async Task PluginsSection_ReadsInventory_TogglesOnlyAfterConfirmation()
    {
        var fake = Fixture();
        var (window, shell, console) = await HostInConsoleAsync(fake);
        console.SelectSectionById(ConsoleSectionId.Plugins);
        Dispatcher.UIThread.RunJobs();

        Assert.True(fake.PluginListCalls >= 1, "opening the section must read plugins.list");
        Assert.True(console.HasPlugins);
        Assert.True(console.PluginsGlobalEnabled);
        var row = Assert.Single(console.Plugins);
        Assert.Equal("sample.plugin", row.PluginId);
        Assert.True(row.CanToggle);

        // A plugin switch is a real write: it must pass the confirm gate first.
        row.ToggleCommand.Execute(null);
        Dispatcher.UIThread.RunJobs();
        Assert.True(shell.ViewModel.IsConfirmOpen);
        Assert.Equal(0, fake.PluginToggleCalls);

        shell.ViewModel.ConfirmCommand.Execute(null);
        await WaitUntilAsync(() => fake.PluginToggleCalls == 1);
        Dispatcher.UIThread.RunJobs();
        Assert.Contains("已停用", console.PluginsLastResult ?? string.Empty, StringComparison.Ordinal);
        window.Close();
    }

    [AvaloniaFact]
    public async Task PluginsSection_PerPluginSwitchIsDisabledWhileTheGlobalSwitchIsOff()
    {
        var fake = Fixture();
        fake.PluginList = fake.PluginList with { GlobalEnabled = false };
        var (window, shell, console) = await HostInConsoleAsync(fake);
        console.SelectSectionById(ConsoleSectionId.Plugins);
        Dispatcher.UIThread.RunJobs();

        Assert.False(console.PluginsGlobalEnabled);
        Assert.Contains("已停用", console.PluginsGlobalText, StringComparison.Ordinal);
        var row = Assert.Single(console.Plugins);
        Assert.False(row.CanToggle, "a per-plugin switch cannot take effect while the master is off");

        // Pressing it anyway must explain instead of silently writing.
        row.ToggleCommand.Execute(null);
        Dispatcher.UIThread.RunJobs();
        Assert.False(shell.ViewModel.IsConfirmOpen);
        Assert.Contains("全局插件已停用", shell.ViewModel.NoticeText, StringComparison.Ordinal);
        Assert.Equal(0, fake.PluginToggleCalls);
        window.Close();
    }

    [AvaloniaFact]
    public async Task PluginsSection_RejectedPlugin_ShowsReasonAndStaysOff()
    {
        var fake = Fixture();
        fake.PluginList = new PluginListInfo(true, new[]
        {
            new PluginInfo("broken.plugin", "rejected", false, string.Empty, string.Empty, string.Empty,
                Array.Empty<string>(), Array.Empty<string>(), "manifest 缺少 hooks 字段"),
        });
        var (window, _, console) = await HostInConsoleAsync(fake);
        console.SelectSectionById(ConsoleSectionId.Plugins);
        Dispatcher.UIThread.RunJobs();

        var row = Assert.Single(console.Plugins);
        Assert.True(row.IsRejected);
        Assert.Equal("已拒绝（无法加载）", row.StatusText);
        Assert.Contains("manifest", row.ReasonText, StringComparison.Ordinal);
        Assert.False(row.CanToggle);
        window.Close();
    }

    [AvaloniaFact]
    public async Task PluginsSection_RefusedWrite_IsReportedWithTheTypedCode()
    {
        var fake = Fixture();
        fake.PluginWriteRefused = true;
        var (window, shell, console) = await HostInConsoleAsync(fake);
        console.SelectSectionById(ConsoleSectionId.Plugins);
        Dispatcher.UIThread.RunJobs();

        console.ToggleGlobalPluginsCommand.Execute(null);
        Dispatcher.UIThread.RunJobs();
        Assert.True(shell.ViewModel.IsConfirmOpen);
        shell.ViewModel.ConfirmCommand.Execute(null);
        await WaitUntilAsync(() => fake.PluginGlobalToggleCalls == 1);
        Dispatcher.UIThread.RunJobs();

        Assert.Contains("HOST_READ_ONLY", shell.ViewModel.NoticeText, StringComparison.Ordinal);
        window.Close();
    }

    // ── REALUSE-DATA-SAFETY-4 AC2: the devices section answers what it can and says what it cannot ──

    [AvaloniaFact]
    public async Task DevicesSection_StatesWhatIsUnknown_AndJumpsToProvidersWhenUnbound()
    {
        var fake = Fixture();
        var (window, _, console) = await HostInConsoleAsync(fake);
        console.SelectSectionById(ConsoleSectionId.Devices);
        Dispatcher.UIThread.RunJobs();

        // Still honestly marked as not wired: device/weights status genuinely has no Host command.
        Assert.True(console.IsNotWiredSection);
        Assert.False(console.HasDetectionProvider);
        Assert.Contains("PROVIDER_NOT_CONFIGURED", console.DetectionReadinessText, StringComparison.Ordinal);
        Assert.Contains("Core 尚未暴露设备/权重状态命令", console.DeviceStatusText, StringComparison.Ordinal);

        console.GoToProvidersCommand.Execute(null);
        Dispatcher.UIThread.RunJobs();
        Assert.True(console.IsProvidersSection, "the unbound case must offer a way to fix it");
        window.Close();
    }

    [AvaloniaFact]
    public async Task DevicesSection_ReportsDetectionReady_WhenAnEnabledProviderDeclaresIt()
    {
        var fake = Fixture();
        fake.ProviderProfiles.Add(new ProviderProfileInfo(
            "profile-detect", "local.detector", "本地检测器",
            new[] { SettingsCapabilities.Detection }, "http://127.0.0.1:9999", "det-v1",
            null, true, "saved"));
        var (window, _, console) = await HostInConsoleAsync(fake);
        await console.RefreshProvidersAsync();
        console.SelectSectionById(ConsoleSectionId.Devices);
        Dispatcher.UIThread.RunJobs();

        Assert.True(console.HasDetectionProvider);
        Assert.Contains("检测步骤可以提交", console.DetectionReadinessText, StringComparison.Ordinal);
        window.Close();
    }

    [AvaloniaFact]
    public async Task DevicesSection_TreatsDisabledProviderAndOtherCapabilities_AsUnbound()
    {
        var fake = Fixture();
        // detection capability but disabled
        fake.ProviderProfiles.Add(new ProviderProfileInfo(
            "profile-off", "local.detector", "未启用的检测器",
            new[] { SettingsCapabilities.Detection }, "http://127.0.0.1:9999", "det-v1",
            null, false, "saved"));
        // enabled but only translation
        fake.ProviderProfiles.Add(new ProviderProfileInfo(
            "profile-tr", "cloud.translator", "翻译器",
            new[] { SettingsCapabilities.Translation }, "https://example.invalid", "tr-v1",
            null, true, "saved"));
        var (window, _, console) = await HostInConsoleAsync(fake);
        await console.RefreshProvidersAsync();
        console.SelectSectionById(ConsoleSectionId.Devices);
        Dispatcher.UIThread.RunJobs();

        Assert.False(console.HasDetectionProvider, "a disabled detector or a non-detection capability is not a binding");
        Assert.Contains("PROVIDER_NOT_CONFIGURED", console.DetectionReadinessText, StringComparison.Ordinal);
        window.Close();
    }
}
