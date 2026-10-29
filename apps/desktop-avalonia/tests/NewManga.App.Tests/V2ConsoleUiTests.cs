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

        console.SelectSectionById(ConsoleSectionId.Storage);
        Dispatcher.UIThread.RunJobs();
        Assert.True(console.IsNotWiredSection);
        Assert.True(console.ShowClearCacheDanger);
        Capture(window, "04-console-storage-not-wired");
        console.RequestClearCacheCommand.Execute(null);
        Assert.True(shell.ViewModel.IsConfirmOpen);
        Assert.False(shell.ViewModel.ConfirmCanConfirm);
        Assert.Contains("能力待接入", shell.ViewModel.ConfirmBlockedReason, StringComparison.Ordinal);
        Capture(window, "08-console-danger-confirm-blocked");
        shell.ViewModel.CancelConfirmCommand.Execute(null);
        Assert.False(shell.ViewModel.IsConfirmOpen);

        console.SelectSectionById(ConsoleSectionId.Backup);
        Dispatcher.UIThread.RunJobs();
        Assert.True(console.ShowBackupDanger);
        console.RequestDeleteBackupCommand.Execute(null);
        Assert.True(shell.ViewModel.IsConfirmOpen);
        Assert.False(shell.ViewModel.ConfirmCanConfirm);
        Assert.Contains("永久移除", shell.ViewModel.ConfirmBody, StringComparison.Ordinal);
        shell.ViewModel.CancelConfirmCommand.Execute(null);

        // Clicking confirm on a blocked action must not call anything, only surface the reason.
        console.RequestCreateBackupCommand.Execute(null);
        shell.ViewModel.ConfirmCommand.Execute(null);
        Dispatcher.UIThread.RunJobs();
        Assert.Contains("能力待接入", shell.ViewModel.NoticeText, StringComparison.Ordinal);
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
            @"C:\Users\someone\secret-config.json sk-live-should-not-leak"));
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
}
