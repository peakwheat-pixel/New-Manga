using Avalonia.Controls;
using Avalonia.Headless.XUnit;
using Avalonia.Threading;
using Avalonia.VisualTree;
using NewManga.App.Services;
using NewManga.App.ViewModels.Fluent;
using NewManga.App.Views.Fluent;
using NewManga.CoreClient;
using Xunit;

namespace NewManga.App.Tests;

/// <summary>
/// SETTINGS-ERROR-STATE-1: closes the only "no coverage at all" cell in the Gate 3 matrix
/// (`doc/reviews/MAINT-1-GATE-CONDITION-3-MATRIX-2026-11-15.md` §3, "错误态 / 设置").
///
/// The implementation already existed — `SettingsViewModel.LoadAsync` catches and sets
/// `State = Error` with a retryable message (`SettingsViewModel.cs:139-171`), and
/// `SettingsPageView` renders a "设置错误" banner with a 重试 action on that state
/// (`SettingsPageView.cs:670-701`). What was missing was a test that would go RED if either
/// half of that behaviour were reverted.
/// </summary>
public sealed class SettingsErrorStateTests
{
    private static FakeHostController HostWithBook()
    {
        var host = new FakeHostController(FakeHostController.ReadySnapshot("Sample Manga"));
        // Unlike the read-only case, this is a genuine load failure: the settings list throws.
        host.SettingsLoadFailure = new InvalidOperationException("settings backend exploded");
        return host;
    }

    /// <summary>AC1: the ViewModel must land in Error with a retryable message.</summary>
    [Fact]
    public async Task LoadFailure_PutsTheViewModelInErrorState_WithRetryableMessage()
    {
        var host = HostWithBook();
        var viewModel = new SettingsViewModel(host, appearance: null, themeManager: null);

        await viewModel.LoadAsync();

        Assert.Equal(FluentPageState.Error, viewModel.State);
        Assert.Contains("设置读取失败", viewModel.Error, StringComparison.Ordinal);
        Assert.Contains("可以重试", viewModel.Error, StringComparison.Ordinal);
        Assert.Contains("InvalidOperationException", viewModel.Error, StringComparison.Ordinal);
    }

    /// <summary>
    /// AC2: the failure must be VISIBLE in the real view tree, not just as a VM field.
    /// A revert that leaves the page blank (or stuck in Loading/ReadOnly) fails here.
    /// </summary>
    [AvaloniaFact]
    public async Task LoadFailure_ShowsTheErrorBannerWithRetryAction()
    {
        var host = HostWithBook();
        var shell = FluentShell.CreateRoot(host: host);
        try
        {
            shell.Show();
            await shell.SettingsViewModel.LoadAsync();
            shell.Navigate(FluentPage.Settings);
            Dispatcher.UIThread.RunJobs();

            var page = shell.GetVisualDescendants().OfType<SettingsPageView>().FirstOrDefault();
            Assert.NotNull(page);

            var texts = page!.GetVisualDescendants()
                .OfType<TextBlock>()
                .Select(block => block.Text ?? string.Empty)
                .ToArray();

            Assert.Contains(texts, text => text.Contains("设置错误", StringComparison.Ordinal));
            Assert.Contains(texts, text => text.Contains("设置读取失败", StringComparison.Ordinal));

            // The banner carries a retry action that the user can actually reach and hit.
            var buttons = page.GetVisualDescendants().OfType<Button>().ToArray();
            var retry = Assert.Single(buttons, button => (button.Content as string) == "重试");
            Assert.True(retry.IsEffectivelyVisible, "the retry action must be visible, not just present");
            Assert.True(retry.IsEffectivelyEnabled, "the retry action must be clickable");
        }
        finally
        {
            shell.Close();
        }
    }

    /// <summary>
    /// AC5 (regression guard for the neighbouring state): a healthy load must NOT show the error
    /// banner — otherwise the AC2 assertion could pass for the wrong reason.
    /// </summary>
    [AvaloniaFact]
    public async Task HealthyLoad_DoesNotShowTheErrorBanner()
    {
        var host = new FakeHostController(FakeHostController.ReadySnapshot("Sample Manga"));
        var shell = FluentShell.CreateRoot(host: host);
        try
        {
            shell.Show();
            await shell.SettingsViewModel.LoadAsync();
            shell.Navigate(FluentPage.Settings);
            Dispatcher.UIThread.RunJobs();

            Assert.NotEqual(FluentPageState.Error, shell.SettingsViewModel.State);

            var page = shell.GetVisualDescendants().OfType<SettingsPageView>().First();
            var texts = page.GetVisualDescendants()
                .OfType<TextBlock>()
                .Select(block => block.Text ?? string.Empty)
                .ToArray();
            Assert.DoesNotContain(texts, text => text.Contains("设置错误", StringComparison.Ordinal));
        }
        finally
        {
            shell.Close();
        }
    }
}
