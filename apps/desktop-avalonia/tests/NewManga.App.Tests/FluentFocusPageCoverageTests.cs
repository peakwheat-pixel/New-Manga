using System;
using System.IO;
using System.Linq;
using Avalonia.Automation;
using Avalonia.Controls;
using Avalonia.Headless.XUnit;
using Avalonia.Input;
using Avalonia.Threading;
using Avalonia.VisualTree;
using NewManga.App.Services;
using NewManga.App.ViewModels.Fluent;
using NewManga.App.Views.Fluent;
using NewManga.Appearance;
using NewManga.DesignSystem.Theming;
using Xunit;

namespace NewManga.App.Tests;

/// <summary>
/// FEA-06-RESIDUAL-1 I-11: every one of the four Fluent pages has at least one keyboard focus scenario
/// that paints the shared 2px focus ring (design 03 §3).
/// </summary>
public sealed class FluentFocusPageCoverageTests : IDisposable
{
    private readonly string _root = Path.Combine(Path.GetTempPath(), $"nm-fea06-residual-focus-{Guid.NewGuid():N}");

    public FluentFocusPageCoverageTests() => Directory.CreateDirectory(_root);

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

    [AvaloniaFact]
    public void EachFluentPage_PaintsTheKeyboardFocusRing()
    {
        using var themeManager = new DesignSystemThemeManager(Avalonia.Application.Current!);
        themeManager.Initialize();
        var appearance = new AppearanceCoordinator(new AppearanceStore(Path.Combine(_root, AppearanceStore.FileName)));
        appearance.Reload();
        var shell = FluentShell.CreateRoot(
            selection: FrontendSelector.Select("builtin.fluent", null),
            host: new FakeHostController(FakeHostController.ReadySnapshot("Sample Manga")),
            appearance: appearance);
        shell.Show();
        Dispatcher.UIThread.RunJobs();

        var pages = new[] { FluentPage.Library, FluentPage.Workbench, FluentPage.Reader, FluentPage.Settings };
        foreach (var page in pages)
        {
            shell.Navigate(page);
            Dispatcher.UIThread.RunJobs();

            var candidates = shell.GetVisualDescendants()
                .OfType<Control>()
                .Where(control => control.Focusable
                    && control.IsEffectivelyVisible
                    && control.IsEffectivelyEnabled
                    && control.Bounds.Width > 0
                    && control.Bounds.Height > 0)
                .Take(8)
                .ToList();
            Assert.NotEmpty(candidates);

            var ringFound = false;
            foreach (var candidate in candidates)
            {
                candidate.Focus(NavigationMethod.Tab);
                Dispatcher.UIThread.RunJobs();
                if (VisibleRingOf(shell) is not null)
                {
                    ringFound = true;
                    break;
                }
            }

            Assert.True(ringFound, $"no focus ring was painted on page '{page}'");
        }

        shell.Close();
    }

    private static Border? VisibleRingOf(Window window) =>
        window.GetVisualDescendants()
            .OfType<Border>()
            .FirstOrDefault(border => border.Classes.Contains("nm-focus-ring") && border.IsVisible);
}
