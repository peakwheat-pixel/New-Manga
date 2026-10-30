using Avalonia;
using Avalonia.Automation;
using Avalonia.Controls;
using Avalonia.Headless.XUnit;
using Avalonia.Interactivity;
using Avalonia.Threading;
using Avalonia.VisualTree;
using NewManga.App.Services;
using NewManga.App.Shell.V2;
using NewManga.App.Shell.V2.Studio;
using NewManga.App.ViewModels.V2.ThemeStudio;
using NewManga.App.Views.V2.ThemeStudio;
using NewManga.DesignSystem.Controls;
using AppKbd = NewManga.App.Views.V2.Shell.Controls.Kbd;
using DsKbd = NewManga.DesignSystem.Controls.Kbd;

namespace NewManga.App.Tests;

/// <summary>
/// V11R-A11Y-1 regression wall: every interactive control in <c>Views/V2/**</c> must expose a readable
/// automation name, never a CLR type name (`Avalonia.Controls.StackPanel`,
/// `NewManga.App.Views.V2.Shell.Controls.Kbd`, …) — the real-machine UIA audit found 7 such buttons.
///
/// The effective-name rule mirrors UIA: an explicit <see cref="AutomationProperties.Name"/> wins; a
/// string Button.Content is its natural name; local/DS Kbd expose their gesture. Anything else is the
/// defect this test is designed to catch.
/// </summary>
public sealed class V2AccessibilityTests : IDisposable
{
    private readonly string _themeSandbox = Path.Combine(
        Path.GetTempPath(),
        "nm-a11y-tests",
        Guid.NewGuid().ToString("N")[..10]);

    public V2AccessibilityTests() => Directory.CreateDirectory(_themeSandbox);

    public void Dispose()
    {
        try
        {
            if (Directory.Exists(_themeSandbox))
            {
                Directory.Delete(_themeSandbox, recursive: true);
            }
        }
        catch (Exception exception) when (exception is IOException or UnauthorizedAccessException)
        {
            // best effort temp cleanup
        }
    }

    [AvaloniaFact]
    public async Task V2_ButtonsAndKbd_ExposeReadableAutomationNames()
    {
        var findings = new List<string>();
        var counts = new Dictionary<string, int>(StringComparer.Ordinal);

        // ── Shell + Library + overlays ────────────────────────────────────────────────────
        var fake = V2Fixture.Create();
        var shell = new AppShellV2(fake);
        var shellWindow = new Window { Content = shell, Width = 1600, Height = 1000 };
        shellWindow.Show();
        await shell.Initialization;
        RunJobs();

        AddView(findings, counts, "Shell/Library", shellWindow);

        shell.ViewModel.OpenPalette();
        RunJobs();
        AddView(findings, counts, "Shell/CommandPalette", shellWindow);
        shell.ViewModel.ClosePalette();

        shell.ViewModel.OpenJump();
        RunJobs();
        AddView(findings, counts, "Shell/Jump", shellWindow);
        shell.ViewModel.CloseJump();

        shell.ViewModel.OpenHelp();
        RunJobs();
        AddView(findings, counts, "Shell/Help", shellWindow);
        shell.ViewModel.CloseHelp();

        shell.ViewModel.RequestConfirm(new ConfirmRequest(
            "删除作品", "将删除《夜光列车》及其章节记录（可恢复）。", "删除", IsDanger: true, OnConfirm: () => { }));
        RunJobs();
        AddView(findings, counts, "Shell/Confirm", shellWindow);
        shell.ViewModel.CancelConfirmCommand.Execute(null);

        // ── Console ─────────────────────────────────────────────────────────────────────
        shell.ViewModel.ConsoleSpaceCommand.Execute(null);
        RunJobs();
        await shell.ViewModel.Console.InitializeAsync();
        RunJobs();
        AddView(findings, counts, "Console", shellWindow);

        // ── Studio page + batch ─────────────────────────────────────────────────────────
        shell.ViewModel.StudioSpaceCommand.Execute(null);
        RunJobs();
        AddView(findings, counts, "Studio/Page", shellWindow);
        var studio = shellWindow.GetVisualDescendants().OfType<StudioWorkspaceView>().FirstOrDefault();
        if (studio is not null)
        {
            studio.BatchModeButton.RaiseEvent(new RoutedEventArgs(Button.ClickEvent));
            RunJobs();
            AddView(findings, counts, "Studio/Batch", shellWindow);
        }

        shellWindow.Close();

        // ── Theme Studio (sandbox service, all seven sections) ─────────────────────────
        var service = StubThemeStudioService.Create(Path.Combine(_themeSandbox, "themes"), seedFixtures: true);
        await service.InitializeAsync();
        using var themeViewModel = new ThemeStudioViewModel(service);
        var themeView = new ThemeStudioView(themeViewModel);
        var themeWindow = new Window { Content = themeView, Width = 1600, Height = 1000 };
        themeWindow.Show();
        await Dispatcher.UIThread.InvokeAsync(async () =>
        {
            await themeView.OpenAsync(ThemeStudioSection.Library);
        });
        RunJobs();

        foreach (var section in themeViewModel.Sections.Select(item => item.Section).Distinct())
        {
            themeViewModel.SelectSection(section);
            RunJobs();
            AddView(findings, counts, $"ThemeStudio/{section}", themeWindow);
        }

        themeWindow.Close();

        var total = counts.Values.Sum();
        Assert.True(total > 0, "accessibility sweep collected no buttons/Kbd controls");
        Assert.True(
            findings.Count == 0,
            $"V2 accessibility names incomplete: {findings.Count} unnamed/type-named control(s) across "
            + $"{counts.Count} views. Fix with AutomationProperties.Name (action semantics) or Kbd naming:\n"
            + string.Join("\n", findings.Distinct(StringComparer.Ordinal).Take(80)));
    }

    private static void AddView(List<string> findings, Dictionary<string, int> counts, string view, Window window)
    {
        RunJobs();
        // Match the real UIA surface: only controls the current view renders as interactive buttons
        // are exposed. Kbd is named in every state (decorative key caps are still announced).
        var controls = window.GetVisualDescendants()
            .OfType<Control>()
            .Where(control => control is AppKbd || control is DsKbd
                || (control.GetType() == typeof(Button)
                    && control.IsEffectivelyVisible
                    && control.Bounds.Width > 1
                    && control.Bounds.Height > 1))
            .ToList();
        counts[view] = counts.TryGetValue(view, out var existing) ? existing + controls.Count : controls.Count;
        foreach (var control in controls)
        {
            var name = EffectiveName(control);
            if (IsReadable(control, name))
            {
                continue;
            }

            findings.Add(
                $"{view}: {control.GetType().FullName} (x:Name='{control.Name}', name='{name ?? "<null>"}', "
                + $"content={DescribeContent(control)}, classes='{string.Join(",", control.Classes)}')");
        }
    }

    private static string DescribeContent(Control control)
    {
        if (control is Button button)
        {
            return button.Content switch
            {
                null => "<null>",
                string text => $"str:{text}",
                Control content => $"{content.GetType().Name}[{string.Join("|", content.GetVisualDescendants().OfType<TextBlock>().Select(t => t.Text).Where(t => !string.IsNullOrWhiteSpace(t)).Take(2))}]",
                _ => button.Content.GetType().Name,
            };
        }

        return control is AppKbd kbd ? $"kbd:{kbd.Text}" : control is DsKbd ds ? $"kbd:{ds.Gesture}" : "-";
    }

    private static bool IsReadable(Control control, string? name)
    {
        if (string.IsNullOrWhiteSpace(name))
        {
            return false;
        }

        return !name.StartsWith("Avalonia.", StringComparison.Ordinal)
            && !name.StartsWith("NewManga.", StringComparison.Ordinal)
            && !name.StartsWith("System.Windows.", StringComparison.Ordinal)
            && !string.Equals(name, control.GetType().Name, StringComparison.Ordinal)
            && !string.Equals(name, control.GetType().FullName, StringComparison.Ordinal);
    }

    private static string? EffectiveName(Control control)
    {
        var explicitName = AutomationProperties.GetName(control);
        if (!string.IsNullOrWhiteSpace(explicitName))
        {
            return explicitName;
        }

        return control switch
        {
            Button { Content: string content } => content,
            AppKbd kbd when !string.IsNullOrWhiteSpace(kbd.Text) => $"快捷键 {kbd.Text}",
            DsKbd kbd when !string.IsNullOrWhiteSpace(kbd.Gesture) => $"快捷键 {kbd.Gesture}",
            _ => null,
        };
    }

    private static void RunJobs()
    {
        Dispatcher.UIThread.RunJobs(DispatcherPriority.Render);
        Dispatcher.UIThread.RunJobs(DispatcherPriority.Loaded);
        Dispatcher.UIThread.RunJobs();
    }
}
