using Avalonia;
using Avalonia.Controls;
using Avalonia.Headless;
using Avalonia.Headless.XUnit;
using Avalonia.Input;
using Avalonia.Threading;
using Avalonia.VisualTree;
using NewManga.App.Services;
using NewManga.App.Shell.V2;
using NewManga.App.ViewModels.V2.Console;
using Xunit;

namespace NewManga.App.Tests;

/// <summary>
/// ADJ-B-RESTART-HINT-1: external adjudication B decided to keep the "changing a model config needs an
/// app restart" limitation, and explicitly required that it be KEPT AND CLEARLY SHOWN ("保留并清楚展示"),
/// and it forbids claiming the change takes effect immediately.
///
/// The sentence already existed (TranslateErrorText.RestartHint) but was only reachable through a
/// translation-failure message. The Provider configuration section -- the place where the user actually
/// edits model settings -- never showed it, so a user could change a model and only learn about the
/// restart much later, from an unrelated error. That is exactly the "prompt not visible" precondition
/// adjudication B said to file a defect against.
///
/// These tests pin the corrected behaviour at both levels: the view model exposes the text, and the real
/// view tree paints it inside the Provider section.
/// </summary>
public sealed class RestartHintVisibilityTests
{
    private static (Window Window, AppShellV2 Shell) Host()
    {
        TestTheme.ResetToDefaults();
        var shell = new AppShellV2(V2Fixture.Create());
        var window = new Window
        {
            Width = 1600,
            Height = 1000,
            Content = shell,
        };
        window.Show();
        Dispatcher.UIThread.RunJobs();
        return (window, shell);
    }

    private static async Task<(Window Window, AppShellV2 Shell)> HostInProvidersAsync()
    {
        var (window, shell) = Host();
        await shell.Initialization;
        Assert.True(shell.HandleKeyForTest(Key.D3, KeyModifiers.Control), "Ctrl+D3 should enter the Console space");
        await shell.ViewModel.Console.InitializeAsync();
        Dispatcher.UIThread.RunJobs();
        shell.ViewModel.Console.SelectSectionById(ConsoleSectionId.Providers);
        Dispatcher.UIThread.RunJobs();
        return (window, shell);
    }

    [AvaloniaFact]
    public async Task ViewModel_ExposesTheSameSentenceAsTheErrorMapper()
    {
        // Guard against the sentence drifting into a second copy.
        var (window, shell) = await HostInProvidersAsync();
        try
        {
            Assert.Equal(TranslateErrorText.RestartHint, shell.ViewModel.Console.RestartHintText);
            Assert.Contains("重启", shell.ViewModel.Console.RestartHintText, StringComparison.Ordinal);
        }
        finally
        {
            window.Close();
        }
    }

    [AvaloniaFact]
    public async Task ProviderSection_PaintsTheRestartHint()
    {
        var (window, shell) = await HostInProvidersAsync();
        try
        {
            var painted = window.GetVisualDescendants()
                .OfType<TextBlock>()
                .Where(block => block.IsVisible)
                .Select(block => block.Text)
                .Where(text => !string.IsNullOrEmpty(text))
                .ToList();

            Assert.Contains(
                TranslateErrorText.RestartHint,
                painted,
                StringComparer.Ordinal);
        }
        finally
        {
            window.Close();
        }
    }
}
