using System;
using System.IO;
using System.Linq;
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
/// FEA-06-RESIDUAL-1 I-11 / I-4 overlay open-close cells: the shell command palette moves keyboard focus
/// into its search box when opened, and Escape closes it while returning focus to the trigger button.
/// </summary>
public sealed class FluentCommandPaletteFocusTests : IDisposable
{
    private readonly string _root = Path.Combine(Path.GetTempPath(), $"nm-fea06-residual-palette-{Guid.NewGuid():N}");

    public FluentCommandPaletteFocusTests() => Directory.CreateDirectory(_root);

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
    public void CommandPalette_MovesFocusIn_AndEscapeRestoresTheTrigger()
    {
        var appearance = new AppearanceCoordinator(new AppearanceStore(Path.Combine(_root, AppearanceStore.FileName)));
        appearance.Reload();
        var shell = FluentShell.CreateRoot(
            selection: FrontendSelector.Select("builtin.fluent", null),
            host: new FakeHostController(FakeHostController.ReadySnapshot("Sample Manga")),
            appearance: appearance);
        shell.Show();
        Dispatcher.UIThread.RunJobs();

        var trigger = shell.GetVisualDescendants().OfType<Button>()
            .First(button => AutomationProperties.GetName(button) == "打开命令面板");
        trigger.Focus(NavigationMethod.Tab);
        Dispatcher.UIThread.RunJobs();
        Assert.True(trigger.IsFocused);

        trigger.RaiseEvent(new RoutedEventArgs(Button.ClickEvent));
        Dispatcher.UIThread.RunJobs();

        var modal = shell.GetVisualDescendants().OfType<Border>()
            .First(border => border.Name == "FluentModalHost");
        Assert.True(modal.IsVisible);
        var search = Assert.IsType<TextBox>(shell.FocusManager?.GetFocusedElement());

        // Result/empty cells (inventory §3): the palette renders real commands, filters them by the query,
        // and shows an honest empty result instead of fake data.
        int RowCount() => shell.GetVisualDescendants().OfType<Button>()
            .Count(button => button.Classes.Contains("fluent-command-row"));
        Assert.True(RowCount() > 0);
        search.Text = "不存在的命令-zzz";
        Dispatcher.UIThread.RunJobs();
        Assert.Equal(0, RowCount());
        search.Text = string.Empty;
        Dispatcher.UIThread.RunJobs();
        Assert.True(RowCount() > 0);

        Assert.True(shell.HandleKeyForTest(Key.Escape, KeyModifiers.None));
        Dispatcher.UIThread.RunJobs();

        Assert.False(modal.IsVisible);
        Assert.True(trigger.IsFocused, "closing the command palette must return focus to the trigger");
        shell.Close();
    }
}
