using System.Text.Json;
using Avalonia;
using Avalonia.Controls;
using Avalonia.Headless.XUnit;
using Avalonia.Threading;
using NewManga.App.Views;
using NewManga.Theme;
using Xunit;

namespace NewManga.App.Tests;

/// <summary>
/// THEME-MACOS-2 (independent redo): the two audits the task card asks for beyond the restored
/// THEME-MACOS-1 behavior tests — (1) font licensing: the macOS pack uses a system/OFL fallback
/// stack and ships no font binaries, and (2) the Sonoma traffic lights are visual only: applying
/// the pack must not change window decorations, resizing, or the client-area chrome behaviour.
/// </summary>
public sealed class ThemeMacosAuditTests
{
    private static readonly string[] FontExtensions = { ".ttf", ".otf", ".ttc", ".woff", ".woff2" };

    private static string RepositoryRoot()
    {
        var directory = new DirectoryInfo(AppContext.BaseDirectory);
        while (directory is not null)
        {
            if (Directory.Exists(Path.Combine(directory.FullName, "apps", "desktop-avalonia", "src", "NewManga.Theme")))
            {
                return directory.FullName;
            }

            directory = directory.Parent;
        }

        throw new InvalidOperationException("repository root (apps/desktop-avalonia/src/NewManga.Theme) not found above test binaries");
    }

    private static IReadOnlyList<string> BundledFontFiles(string repositoryRoot)
    {
        var appRoot = Path.Combine(repositoryRoot, "apps", "desktop-avalonia");
        var found = new List<string>();
        foreach (var file in Directory.EnumerateFiles(appRoot, "*", SearchOption.AllDirectories))
        {
            var relative = Path.GetRelativePath(appRoot, file).Replace('\\', '/');
            var segments = relative.Split('/');
            if (segments.Any(segment => segment is "bin" or "obj"))
            {
                continue;
            }

            if (FontExtensions.Any(extension => relative.EndsWith(extension, StringComparison.OrdinalIgnoreCase)))
            {
                found.Add(relative);
            }
        }

        return found;
    }

    [Fact]
    public void MacosFontStack_ShipsNoFontBinary_AndIsSystemOrOflFallbackOnly()
    {
        var repositoryRoot = RepositoryRoot();
        var bundled = BundledFontFiles(repositoryRoot);
        Assert.Empty(bundled);

        var stacks = new[] { ThemePacks.MacOsFontFamily, ThemePacks.DefaultFontFamily };
        foreach (var stack in stacks)
        {
            Assert.False(string.IsNullOrWhiteSpace(stack));
            Assert.DoesNotContain("avares://", stack, StringComparison.OrdinalIgnoreCase);
            Assert.DoesNotContain("#", stack, StringComparison.Ordinal);
            Assert.DoesNotContain(".ttf", stack, StringComparison.OrdinalIgnoreCase);
            Assert.DoesNotContain(".otf", stack, StringComparison.OrdinalIgnoreCase);
            Assert.Contains("sans-serif", stack, StringComparison.OrdinalIgnoreCase);
        }

        // The only non-system family named by the macOS stack is Inter, an SIL OFL 1.1 font; it is
        // referenced as an install-time fallback and never bundled (asserted above by the empty scan).
        Assert.Contains("Inter", ThemePacks.MacOsFontFamily, StringComparison.Ordinal);
        Assert.Contains("PingFang SC", ThemePacks.MacOsFontFamily, StringComparison.Ordinal);
        Assert.Contains("Microsoft YaHei UI", ThemePacks.MacOsFontFamily, StringComparison.Ordinal);

        Evidence.Write("theme/font-audit.json", writer =>
        {
            writer.WriteStartObject();
            writer.WriteString("ac", "AC5");
            writer.WriteString("generated_by", "ThemeMacosAuditTests.MacosFontStack_ShipsNoFontBinary_AndIsSystemOrOflFallbackOnly");
            writer.WriteNumber("bundled_font_files", bundled.Count);
            writer.WriteStartArray("font_files");
            foreach (var file in bundled)
            {
                writer.WriteStringValue(file);
            }

            writer.WriteEndArray();
            writer.WriteString("macos_font_stack", ThemePacks.MacOsFontFamily);
            writer.WriteString("default_font_stack", ThemePacks.DefaultFontFamily);
            writer.WriteString(
                "license_note",
                "No font binary is shipped. Both stacks name system-installed families (Segoe UI / Microsoft YaHei UI / PingFang SC / Noto Sans CJK SC) plus Inter (SIL OFL 1.1) as an optional fallback; sans-serif is the final fallback. Redistribution therefore adds no commercial or system font payload.");
            writer.WriteBoolean("no_embedded_font_uri", true);
            writer.WriteEndObject();
        });
    }

    [AvaloniaFact]
    public void MacosTrafficLights_AreVisualOnly_AndDoNotChangeWindowBehaviour()
    {
        var application = Application.Current!;
        ThemePackService.Apply(application, ThemePacks.Default);
        var window = new MainWindow(new FakeHostController(FakeHostController.ReadySnapshot("雾港来信")), new AppOptions())
        {
            Width = 1280,
            Height = 820,
        };
        window.Show();
        Dispatcher.UIThread.RunJobs();

        try
        {
            var decorations = window.SystemDecorations;
            var canResize = window.CanResize;
            var extendChrome = window.ExtendClientAreaToDecorationsHint;
            var chromeHints = window.ExtendClientAreaChromeHints;
            var width = window.Width;
            var height = window.Height;

            Assert.False(window.AreTrafficLightsVisible);

            window.Settings.SelectTheme(ThemePacks.ById("macos-sonoma"));
            Dispatcher.UIThread.RunJobs();

            Assert.True(window.AreTrafficLightsVisible);
            Assert.Equal(decorations, window.SystemDecorations);
            Assert.Equal(canResize, window.CanResize);
            Assert.Equal(extendChrome, window.ExtendClientAreaToDecorationsHint);
            Assert.Equal(chromeHints, window.ExtendClientAreaChromeHints);
            Assert.Equal(width, window.Width);
            Assert.Equal(height, window.Height);

            window.Settings.SelectTheme(ThemePacks.Default);
            Dispatcher.UIThread.RunJobs();
            Assert.False(window.AreTrafficLightsVisible);

            Evidence.Write("theme/traffic-lights-visual-only.json", writer =>
            {
                writer.WriteStartObject();
                writer.WriteString("ac", "AC1");
                writer.WriteString("generated_by", "ThemeMacosAuditTests.MacosTrafficLights_AreVisualOnly_AndDoNotChangeWindowBehaviour");
                writer.WriteString("system_decorations", decorations.ToString());
                writer.WriteBoolean("can_resize_unchanged", canResize == window.CanResize);
                writer.WriteBoolean("extend_client_area_hint_unchanged", extendChrome == window.ExtendClientAreaToDecorationsHint);
                writer.WriteBoolean("extend_client_area_chrome_hints_unchanged", chromeHints == window.ExtendClientAreaChromeHints);
                writer.WriteBoolean("size_unchanged", width == window.Width && height == window.Height);
                writer.WriteBoolean("visible_only_for_macos", true);
                writer.WriteEndObject();
            });
        }
        finally
        {
            window.Close();
        }
    }
}
