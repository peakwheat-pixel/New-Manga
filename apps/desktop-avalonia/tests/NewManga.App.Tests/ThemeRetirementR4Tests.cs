using System.Diagnostics;
using Avalonia;
using Avalonia.Controls;
using Avalonia.Headless.XUnit;
using Avalonia.LogicalTree;
using Avalonia.Threading;
using NewManga.App.Shell;
using NewManga.App.ViewModels;
using NewManga.App.Views;

namespace NewManga.App.Tests;

/// <summary>
/// V11R-C-3 R4: the five replacement assertions that must exist before the five legacy theme/layout
/// test files are deleted (DELETION_BATCHES §2 hard gate). Each test replaces one old assertion:
/// font-binary audit, window-chrome behaviour, window-material fallback, non-blocking first frame and
/// the retired legacy theme centre pointing at Theme Studio.
/// </summary>
public sealed class ThemeRetirementR4Tests
{
    [AvaloniaFact]
    public void No_font_binaries_ship_with_the_application()
    {
        var root = FindRepositoryRoot();
        // The app ships no font binaries. Only TRACKED files count as shipped: local training data
        // (training_data/** in .gitignore, e.g. TanukiMagic.ttf) lives in the worktree but is not packaged.
        // Any font that exists locally must be either git-ignored or outside the worktree enumeration;
        // an untracked-but-not-ignored font would fail the second assertion below.
        var tracked = GitFileList(root).Select(path => Path.GetFullPath(Path.Combine(root, path))).ToHashSet(StringComparer.OrdinalIgnoreCase);
        var existingFonts = new[] { "*.ttf", "*.otf", "*.woff", "*.woff2" }
            .SelectMany(pattern => Directory.EnumerateFiles(root, pattern, SearchOption.AllDirectories))
            .Where(path => !IsBuildOutput(path))
            .ToArray();

        var trackedFonts = existingFonts.Where(tracked.Contains).ToArray();
        Assert.Empty(trackedFonts.Select(path => Path.GetRelativePath(root, path)));

        foreach (var font in existingFonts)
        {
            var relative = Path.GetRelativePath(root, font);
            Assert.True(
                IsGitIgnored(root, relative),
                $"font '{relative}' exists in the worktree but is neither tracked nor git-ignored; it could leak into the package");
        }
    }

    [AvaloniaFact]
    public void Window_chrome_is_visual_only_and_keeps_real_window_behaviour()
    {
        var controller = new FakeHostController(FakeHostController.ReadySnapshot());
        var window = new MainWindow(controller, new AppOptions());
        var decorations = window.SystemDecorations;
        var canResize = window.CanResize;

        window.Show();
        Dispatcher.UIThread.RunJobs();
        window.ApplyTheme();
        Dispatcher.UIThread.RunJobs();

        Assert.Equal(SystemDecorations.Full, decorations);
        Assert.Equal(decorations, window.SystemDecorations);
        Assert.Equal(canResize, window.CanResize);
        Assert.True(window.IsVisible);
        window.Close();
        Assert.False(window.IsVisible);
    }

    [AvaloniaFact]
    public void Window_material_falls_back_to_opaque_on_unsupported_os()
    {
        Assert.Equal(WindowMaterialKind.Mica, WindowMaterial.Choose(10, 22631).Kind);
        Assert.Equal(WindowMaterialKind.OpaqueFallback, WindowMaterial.Choose(10, 19045).Kind);
        Assert.Equal(WindowMaterialKind.OpaqueFallback, WindowMaterial.Choose(6, 7601).Kind);
        Assert.Equal(new[] { "None" }, WindowMaterial.Choose(10, 19045).Hints);
    }

    [AvaloniaFact]
    public void Startup_does_not_block_first_frame()
    {
        var gate = new TaskCompletionSource();
        var controller = new FakeHostController(FakeHostController.ReadySnapshot()) { StartGate = gate.Task };
        var window = new MainWindow(controller, new AppOptions());

        window.Show();
        Dispatcher.UIThread.RunJobs();

        Assert.True(window.IsVisible);
        Assert.NotNull(window.PageHostControl.Content);
        Assert.False(gate.Task.IsCompleted);
        gate.SetResult();
        Dispatcher.UIThread.RunJobs();
        window.Close();
    }

    [AvaloniaFact]
    public void Legacy_settings_page_retires_theme_center_and_points_to_theme_studio()
    {
        var page = new SettingsPage(new SettingsViewModel(), () => { });
        var themeCardChildren = Assert.IsType<StackPanel>(page.ThemeCard.Child).Children.OfType<TextBlock>().Select(text => text.Text ?? string.Empty).ToArray();

        Assert.Contains(themeCardChildren, text => text.Contains("已退役", StringComparison.Ordinal));
        Assert.Contains(themeCardChildren, text => text.Contains("Theme Studio", StringComparison.Ordinal));
        Assert.True(page.AppearanceRow.IsVisible);
        Assert.DoesNotContain(Descendants(page).OfType<Button>(), button => button.Name?.StartsWith("ThemePack_", StringComparison.Ordinal) == true);
    }

    private static IEnumerable<Control> Descendants(Control root)
    {
        foreach (var child in root.GetLogicalChildren().OfType<Control>())
        {
            yield return child;
            foreach (var descendant in Descendants(child))
            {
                yield return descendant;
            }
        }
    }

    private static string[] GitFileList(string root) =>
        RunGit(root, "ls-files -z").Output.Split('\0', StringSplitOptions.RemoveEmptyEntries);

    private static bool IsGitIgnored(string root, string relativePath) =>
        RunGit(root, $"check-ignore --quiet -- \"{relativePath}\"").ExitCode == 0;

    private static (int ExitCode, string Output) RunGit(string root, string arguments)
    {
        using var process = new Process
        {
            StartInfo = new ProcessStartInfo("git", arguments)
            {
                WorkingDirectory = root,
                RedirectStandardOutput = true,
                RedirectStandardError = true,
                UseShellExecute = false,
            },
        };
        process.Start();
        var output = process.StandardOutput.ReadToEnd();
        _ = process.StandardError.ReadToEnd();
        process.WaitForExit();
        return (process.ExitCode, output);
    }

    private static bool IsBuildOutput(string path)
    {
        var normalized = path.Replace('\\', '/');
        return normalized.Contains("/bin/", StringComparison.OrdinalIgnoreCase) ||
               normalized.Contains("/obj/", StringComparison.OrdinalIgnoreCase) ||
               normalized.Contains("/node_modules/", StringComparison.OrdinalIgnoreCase) ||
               normalized.Contains("/archive/", StringComparison.OrdinalIgnoreCase);
    }

    private static string FindRepositoryRoot()
    {
        var directory = new DirectoryInfo(AppContext.BaseDirectory);
        while (directory is not null)
        {
            if (File.Exists(Path.Combine(directory.FullName, "doc", "design", "redesign-v1", "40-fusion", "tokens.json")))
            {
                return directory.FullName;
            }

            directory = directory.Parent;
        }

        throw new InvalidOperationException("could not locate repository root");
    }
}

