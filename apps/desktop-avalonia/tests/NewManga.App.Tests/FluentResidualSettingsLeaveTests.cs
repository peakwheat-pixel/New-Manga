using System.IO;
using Avalonia.Automation;
using Avalonia.Controls;
using Avalonia.Headless.XUnit;
using Avalonia.Input;
using Avalonia.Interactivity;
using Avalonia.Threading;
using Avalonia.VisualTree;
using NewManga.App.Services;
using NewManga.App.ViewModels.Fluent;
using NewManga.App.Views.Fluent;
using NewManga.Appearance;
using Xunit;

namespace NewManga.App.Tests;

/// <summary>
/// FEA-06-RESIDUAL-1 I-3：设置页离开未保存确认三分支（保存并离开 / 丢弃并离开 / 取消）+
/// 保存失败保护 + Esc 优先级（浮层内=取消、页面内=触发离开流）+ FEA-07 退出保护不退化。
/// </summary>
public sealed class FluentResidualSettingsLeaveTests : IDisposable
{
    private readonly string _root = Path.Combine(Path.GetTempPath(), $"nm-fea06-residual-i3-{Guid.NewGuid():N}");

    public FluentResidualSettingsLeaveTests() => Directory.CreateDirectory(_root);

    public void Dispose()
    {
        try
        {
            Directory.Delete(_root, recursive: true);
        }
        catch (IOException)
        {
            // best-effort cleanup
        }
    }

    private AppearanceCoordinator CreateAppearance()
    {
        var appearance = new AppearanceCoordinator(new AppearanceStore(Path.Combine(_root, AppearanceStore.FileName)));
        appearance.Reload();
        return appearance;
    }

    private FluentShell CreateDirtySettingsShell(AppearanceCoordinator appearance, out SettingsViewModel settings)
    {
        var shell = FluentShell.CreateRoot(host: new FakeHostController(FakeHostController.ReadySnapshot()), appearance: appearance);
        shell.Show();
        Dispatcher.UIThread.RunJobs();
        shell.Navigate(FluentPage.Settings);
        Dispatcher.UIThread.RunJobs();
        settings = shell.SettingsViewModel;
        settings.UpdateDraft(settings.Draft with { MotionMode = MotionMode.Reduce });
        Dispatcher.UIThread.RunJobs();
        Assert.True(settings.IsDirty);
        return shell;
    }


    [AvaloniaFact]
    public void I11_LeaveOverlay_MovesFocusIn_AndRestoresItOnCancel()
    {
        var appearance = CreateAppearance();
        var shell = CreateDirtySettingsShell(appearance, out _);
        var trigger = shell.SettingsView.GetVisualDescendants().OfType<Button>()
            .First(button => AutomationProperties.GetName(button) == "保存外观设置");
        trigger.Focus(NavigationMethod.Tab);
        Dispatcher.UIThread.RunJobs();
        Assert.True(trigger.IsFocused);

        Assert.True(shell.HandleKeyForTest(Key.Escape, KeyModifiers.None));
        Dispatcher.UIThread.RunJobs();
        Assert.True(shell.SettingsView.LeaveConfirmationVisible);
        var cancel = shell.SettingsView.GetVisualDescendants().OfType<Button>()
            .First(button => AutomationProperties.GetName(button) == "取消离开设置页");
        Assert.True(cancel.IsFocused, "focus must move into the leave overlay");

        Assert.True(shell.HandleKeyForTest(Key.Escape, KeyModifiers.None));
        Dispatcher.UIThread.RunJobs();
        Assert.False(shell.SettingsView.LeaveConfirmationVisible);
        Assert.True(trigger.IsFocused, "closing the overlay must return focus to the trigger");
        shell.Close();
    }
    private static Button LeaveButton(FluentShell shell, string accessibleName) =>
        shell.SettingsView.GetVisualDescendants().OfType<Button>()
            .First(button => Avalonia.Automation.AutomationProperties.GetName(button) == accessibleName &&
                button.IsVisible);

    private static void PumpUntil(Func<bool> condition, int timeoutMs = 5000)
    {
        var deadline = DateTime.UtcNow.AddMilliseconds(timeoutMs);
        while (!condition() && DateTime.UtcNow < deadline)
        {
            Dispatcher.UIThread.RunJobs();
            Thread.Sleep(5);
        }

        Dispatcher.UIThread.RunJobs();
    }

    [AvaloniaFact]
    public void I3_CleanSettings_NavigatesAwayWithoutConfirmation()
    {
        var appearance = CreateAppearance();
        var shell = FluentShell.CreateRoot(host: new FakeHostController(FakeHostController.ReadySnapshot()), appearance: appearance);
        shell.Show();
        Dispatcher.UIThread.RunJobs();
        shell.Navigate(FluentPage.Settings);
        Dispatcher.UIThread.RunJobs();
        Assert.False(shell.SettingsViewModel.IsDirty);

        shell.Navigate(FluentPage.Library);
        Dispatcher.UIThread.RunJobs();

        Assert.Equal(FluentPage.Library, shell.CurrentPage);
        Assert.False(shell.SettingsView.LeaveConfirmationVisible);
        shell.Close();
    }

    [AvaloniaFact]
    public void I3_DirtySettings_NavigationIsSuspendedUntilSaveAndLeave()
    {
        var appearance = CreateAppearance();
        var shell = CreateDirtySettingsShell(appearance, out var settings);
        shell.Navigate(FluentPage.Library);
        Dispatcher.UIThread.RunJobs();

        // 导航被挂起：确认浮层打开、页面未切换。
        Assert.Equal(FluentPage.Settings, shell.CurrentPage);
        Assert.True(shell.SettingsView.LeaveConfirmationVisible);

        LeaveButton(shell, "保存设置后离开").RaiseEvent(new RoutedEventArgs(Button.ClickEvent));
        // SaveAsync 的 continuation 可能晚于一次 RunJobs 入队（文件 IO 线程 post 回 UI），泵到离开完成。
        PumpUntil(() => shell.CurrentPage == FluentPage.Library);

        Assert.Equal(FluentPage.Library, shell.CurrentPage);
        Assert.False(shell.SettingsView.LeaveConfirmationVisible);
        Assert.False(settings.IsDirty);
        // 「保存调用 / host 写入发生」：canonical 已持久化为 draft 值。
        Assert.Equal(MotionMode.Reduce, appearance.Settings.MotionMode);
        Assert.True(File.Exists(Path.Combine(_root, AppearanceStore.FileName)));
        shell.Close();
    }

    [AvaloniaFact]
    public void I3_DirtySettings_DiscardAndLeave_RestoresCanonicalAndNavigates()
    {
        var appearance = CreateAppearance();
        var shell = CreateDirtySettingsShell(appearance, out var settings);
        shell.Navigate(FluentPage.Workbench);
        Dispatcher.UIThread.RunJobs();
        Assert.True(shell.SettingsView.LeaveConfirmationVisible);

        LeaveButton(shell, "丢弃未保存修改后离开").RaiseEvent(new RoutedEventArgs(Button.ClickEvent));
        Dispatcher.UIThread.RunJobs();

        Assert.Equal(FluentPage.Workbench, shell.CurrentPage);
        Assert.False(settings.IsDirty);
        Assert.Equal(appearance.Settings, settings.Draft); // draft 已丢弃（回到 canonical）
        shell.Close();
    }

    [AvaloniaFact]
    public void I3_DirtySettings_Cancel_StaysOnPageAndKeepsDraft()
    {
        var appearance = CreateAppearance();
        var shell = CreateDirtySettingsShell(appearance, out var settings);
        var draftBefore = settings.Draft;
        shell.Navigate(FluentPage.Library);
        Dispatcher.UIThread.RunJobs();
        Assert.True(shell.SettingsView.LeaveConfirmationVisible);

        LeaveButton(shell, "取消离开设置页").RaiseEvent(new RoutedEventArgs(Button.ClickEvent));
        Dispatcher.UIThread.RunJobs();

        Assert.Equal(FluentPage.Settings, shell.CurrentPage);
        Assert.False(shell.SettingsView.LeaveConfirmationVisible);
        Assert.True(settings.IsDirty);
        Assert.Equal(draftBefore, settings.Draft); // 草稿保留
        shell.Close();
    }

    [AvaloniaFact]
    public void I3_SaveFailure_StaysOnPageKeepsDraftAndShowsError()
    {
        var appearance = CreateAppearance();
        var shell = CreateDirtySettingsShell(appearance, out var settings);
        // 注入校验失败：MaterialAcrylicStrength 越界 → SaveAppearanceAsync 返回 false 并设置 Error。
        settings.UpdateDraft(settings.Draft with { MaterialAcrylicStrength = 5 });
        Dispatcher.UIThread.RunJobs();
        Assert.True(settings.IsDirty);

        shell.Navigate(FluentPage.Library);
        Dispatcher.UIThread.RunJobs();
        Assert.True(shell.SettingsView.LeaveConfirmationVisible);

        LeaveButton(shell, "保存设置后离开").RaiseEvent(new RoutedEventArgs(Button.ClickEvent));
        Dispatcher.UIThread.RunJobs();

        Assert.Equal(FluentPage.Settings, shell.CurrentPage); // 留页
        Assert.False(shell.SettingsView.LeaveConfirmationVisible);
        Assert.True(settings.IsDirty); // 留稿（dirty 保持）
        Assert.Equal(5, settings.Draft.MaterialAcrylicStrength);
        Assert.False(string.IsNullOrWhiteSpace(settings.Error)); // 错误可见
        Assert.Contains("Acrylic", settings.Error, StringComparison.Ordinal); // RenderNotice 优先显示 Error
        shell.Close();
    }

    [AvaloniaFact]
    public void I3_Esc_InsideLeaveConfirmation_CancelsWithoutNavigating()
    {
        var appearance = CreateAppearance();
        var shell = CreateDirtySettingsShell(appearance, out _);
        // 页面内 Esc 触发离开流。
        Assert.True(shell.HandleKeyForTest(Key.Escape, KeyModifiers.None));
        Dispatcher.UIThread.RunJobs();
        Assert.True(shell.SettingsView.LeaveConfirmationVisible);
        Assert.Equal(FluentPage.Settings, shell.CurrentPage);

        // 浮层内 Esc = 取消：浮层关闭、页面未变、草稿保留。
        Assert.True(shell.HandleKeyForTest(Key.Escape, KeyModifiers.None));
        Dispatcher.UIThread.RunJobs();
        Assert.False(shell.SettingsView.LeaveConfirmationVisible);
        Assert.Equal(FluentPage.Settings, shell.CurrentPage);
        Assert.True(shell.SettingsViewModel.IsDirty);
        shell.Close();
    }

    [AvaloniaFact]
    public void I3_Esc_OnDirtySettingsPage_OpensLeaveConfirmation_ThenSaveAndLeaveProceeds()
    {
        var appearance = CreateAppearance();
        var shell = CreateDirtySettingsShell(appearance, out _);
        Assert.False(shell.SettingsView.LeaveConfirmationVisible);

        Assert.True(shell.HandleKeyForTest(Key.Escape, KeyModifiers.None));
        Dispatcher.UIThread.RunJobs();
        Assert.True(shell.SettingsView.LeaveConfirmationVisible);
        Assert.Equal(FluentPage.Settings, shell.CurrentPage);

        LeaveButton(shell, "保存设置后离开").RaiseEvent(new RoutedEventArgs(Button.ClickEvent));
        PumpUntil(() => shell.CurrentPage == FluentPage.Library);
        Assert.Equal(FluentPage.Library, shell.CurrentPage); // 离开流默认目标=一级页（书架）
        Assert.False(shell.SettingsViewModel.IsDirty);
        shell.Close();
    }

    [AvaloniaFact]
    public void I3_Esc_InsidePlainConfirmationDialog_ClosesDialogFirst()
    {
        var appearance = CreateAppearance();
        var shell = CreateDirtySettingsShell(appearance, out _);
        // 打开一个普通确认浮层（Provider 编辑器）——dirty 仍在，但 Esc 必须先关浮层。
        shell.SettingsView.ViewModel.SelectedGroup = SettingsGroupId.Providers;
        Dispatcher.UIThread.RunJobs();
        shell.SettingsView.GetVisualDescendants().OfType<Button>()
            .First(button => button.Content?.ToString() == "添加 Provider")
            .RaiseEvent(new RoutedEventArgs(Button.ClickEvent));
        Dispatcher.UIThread.RunJobs();
        Assert.True(shell.SettingsView.HasOpenConfirmation);

        Assert.True(shell.HandleKeyForTest(Key.Escape, KeyModifiers.None));
        Dispatcher.UIThread.RunJobs();
        Assert.False(shell.SettingsView.HasOpenConfirmation);
        // 离开流未触发（浮层优先）。
        Assert.False(shell.SettingsView.LeaveConfirmationVisible);
        Assert.True(shell.SettingsViewModel.IsDirty);
        Assert.Equal(FluentPage.Settings, shell.CurrentPage);
        shell.Close();
    }

    [AvaloniaFact]
    public void I3_Fea07ExitProtection_StillBlocksWhileDirty()
    {
        var appearance = CreateAppearance();
        var shell = CreateDirtySettingsShell(appearance, out _);

        // FEA-07 AC2：设置未保存时稳定窗口关闭聚合仍阻断（HasUnsavedEdits 与 IsDirty 一致）。
        Assert.True(shell.Surface.HasUnsavedEdits);

        shell.SettingsViewModel.UpdateDraft(appearance.Settings);
        Dispatcher.UIThread.RunJobs();
        Assert.False(shell.Surface.HasUnsavedEdits);
        shell.Close();
    }

    [AvaloniaFact]
    public void I3_DirtySettings_SpaceSwitch_AlsoGoesThroughLeaveConfirmation()
    {
        var appearance = CreateAppearance();
        var shell = CreateDirtySettingsShell(appearance, out _);
        shell.FindControl<Button>("SpaceConsole")!.RaiseEvent(new RoutedEventArgs(Button.ClickEvent));
        Dispatcher.UIThread.RunJobs();

        // 空间切换同样被挂起：确认前不离开设置页。
        Assert.Equal(FluentPage.Settings, shell.CurrentPage);
        Assert.True(shell.SettingsView.LeaveConfirmationVisible);

        LeaveButton(shell, "丢弃未保存修改后离开").RaiseEvent(new RoutedEventArgs(Button.ClickEvent));
        Dispatcher.UIThread.RunJobs();
        // 确认后完成完整空间进入序列：Console 空间 + Console 页签。
        Assert.Equal(FluentPage.Workbench, shell.CurrentPage);
        Assert.Equal(WorkbenchViewTab.Console, shell.WorkbenchView.ActiveTab);
        shell.Close();
    }

    [AvaloniaFact]
    public void ImplR1_R1_004_DirtySettings_ReaderNavigation_GoesThroughLeaveConfirmation()
    {
        var appearance = CreateAppearance();
        var shell = CreateDirtySettingsShell(appearance, out _);

        // Reader 特判曾绕过 dirty 保护；现在必须被挂起并展示离开确认。
        shell.Navigate(FluentPage.Reader);
        Dispatcher.UIThread.RunJobs();

        Assert.Equal(FluentPage.Settings, shell.CurrentPage);
        Assert.True(shell.SettingsView.LeaveConfirmationVisible);
        shell.Close();
    }

    [AvaloniaFact]
    public void ImplR1_R1_005_EscapeClosesShellPaletteBeforeLowerLeaveConfirmation()
    {
        var appearance = CreateAppearance();
        var shell = CreateDirtySettingsShell(appearance, out _);
        var palette = shell.GetVisualDescendants().OfType<Button>()
            .First(button => AutomationProperties.GetName(button) == "打开命令面板");
        palette.RaiseEvent(new RoutedEventArgs(Button.ClickEvent));
        Dispatcher.UIThread.RunJobs();
        var modal = shell.GetVisualDescendants().OfType<Border>()
            .First(border => border.Name == "FluentModalHost");
        Assert.True(modal.IsVisible);

        // 第一次 Esc 只关闭最上层 shell 浮层，不触发下层设置页离开确认。
        Assert.True(shell.HandleKeyForTest(Key.Escape, KeyModifiers.None));
        Dispatcher.UIThread.RunJobs();
        Assert.False(modal.IsVisible);
        Assert.False(shell.SettingsView.LeaveConfirmationVisible);

        // 第二次 Esc（无 shell 浮层）才按页面 dirty 语义打开离开确认。
        Assert.True(shell.HandleKeyForTest(Key.Escape, KeyModifiers.None));
        Dispatcher.UIThread.RunJobs();
        Assert.True(shell.SettingsView.LeaveConfirmationVisible);
        shell.Close();
    }
}
