using Avalonia;
using Avalonia.Controls;
using Avalonia.Headless;
using Avalonia.Headless.XUnit;
using Avalonia.Input;
using Avalonia.Layout;
using Avalonia.Media;
using Avalonia.Media.Imaging;
using Avalonia.Threading;
using NewManga.DesignSystem.Controls;
using NewManga.DesignSystem.Icons;
using NewManga.DesignSystem.Theming;
using SkiaSharp;

namespace NewManga.DesignSystem.Tests;

/// <summary>
/// AC10 visual evidence: renders the design-system gallery with headless Skia and captures real PNG
/// frames for dark, light and high-contrast mode. The dark/light pair is captured from the same window
/// instance to prove that an appearance switch replaces resources on a live visual tree.
/// Set <c>NM_DS_EVIDENCE_DIR</c> to write the PNGs into the task evidence directory.
/// </summary>
public sealed class VisualEvidenceTests
{
    private const int GalleryWidth = 1280;
    private const int GalleryHeight = 820;

    [AvaloniaFact]
    public void Gallery_renders_dark_light_and_high_contrast_from_the_same_window()
    {
        using var manager = ThemeTestHarness.CreateInitialized();
        var evidenceDirectory = ResolveEvidenceDirectory();
        Directory.CreateDirectory(evidenceDirectory);

        var window = new Window
        {
            Width = GalleryWidth,
            Height = GalleryHeight,
            Content = BuildGallery(),
        };
        window.Show();
        Dispatcher.UIThread.RunJobs();

        var darkFrame = Capture(window, Path.Combine(evidenceDirectory, "gallery-dark.png"));
        Assert.Equal(GalleryWidth, darkFrame.PixelSize.Width);
        Assert.Equal(GalleryHeight, darkFrame.PixelSize.Height);
        AssertPixels(darkFrame, Path.Combine(evidenceDirectory, "gallery-dark.png"), Color.Parse("#FF1A1C1F"), "dark panel surface");
        Assert.True(CountDistinctColors(darkFrame) > 40, "dark gallery looks blank");

        Assert.True(manager.SetAppearance(AppearanceMode.Light), manager.LastError);
        Dispatcher.UIThread.RunJobs();
        Assert.Same(window.Content, window.Content);
        var lightFrame = Capture(window, Path.Combine(evidenceDirectory, "gallery-light.png"));
        AssertPixels(lightFrame, Path.Combine(evidenceDirectory, "gallery-light.png"), Color.Parse("#FFFFFFFF"), "light panel surface");
        Assert.True(CountDistinctColors(lightFrame) > 40, "light gallery looks blank");
        Assert.NotEqual(EdgePixel(darkFrame), EdgePixel(lightFrame));

        Assert.True(manager.SetContrast(ContrastMode.High), manager.LastError);
        Dispatcher.UIThread.RunJobs();
        var highContrastFrame = Capture(window, Path.Combine(evidenceDirectory, "gallery-highcontrast.png"));
        Assert.True(CountDistinctColors(highContrastFrame) > 40, "high-contrast gallery looks blank");
        // High contrast keeps the background ladder and re-curates every foreground: the frames must
        // differ in a meaningful number of sampled pixels (labels, status hues, borders).
        Assert.True(
            CountDifferentPixels(lightFrame, highContrastFrame) > 50,
            "high-contrast frame is pixel-identical to the standard light frame");

        Assert.True(manager.SetContrast(ContrastMode.Standard), manager.LastError);
        Assert.True(manager.SetAppearance(AppearanceMode.Dark), manager.LastError);
        Assert.True(window.IsVisible);
        window.Close();
    }

    [AvaloniaFact]
    public void Keyboard_focus_ring_is_rendered_in_dark_and_light()
    {
        using var manager = ThemeTestHarness.CreateInitialized();
        var evidenceDirectory = ResolveEvidenceDirectory();
        Directory.CreateDirectory(evidenceDirectory);

        var textBox = new TextBox { Watermark = "键盘焦点", Width = 220 };
        var primary = new Button { Content = "主操作", Classes = { "primary" } };
        var window = new Window
        {
            Width = 520,
            Height = 180,
            Content = new Border
            {
                Classes = { "panel" },
                Padding = new Thickness(24),
                Child = new StackPanel { Spacing = 16, Children = { primary, textBox } },
            },
        };
        window.Show();
        Dispatcher.UIThread.RunJobs();

        var unfocused = CaptureFrame(window);
        textBox.Focus(NavigationMethod.Tab);
        Dispatcher.UIThread.RunJobs();
        var focusedDark = CaptureFrame(window);
        var darkPath = Path.Combine(evidenceDirectory, "focus-ring-dark.png");
        Save(focusedDark, darkPath);
        Assert.True(CountDifferentPixels(unfocused, focusedDark) > 20, "keyboard focus did not change the rendered frame");

        Assert.True(manager.SetAppearance(AppearanceMode.Light), manager.LastError);
        textBox.Focus(NavigationMethod.Tab);
        Dispatcher.UIThread.RunJobs();
        var focusedLight = CaptureFrame(window);
        Save(focusedLight, Path.Combine(evidenceDirectory, "focus-ring-light.png"));
        Assert.True(CountDifferentPixels(focusedDark, focusedLight) > 100, "focus frame did not follow the light palette");

        manager.ResetToDefaults();
        window.Close();
    }

    private static Control BuildGallery()
    {
        var buttons = new StackPanel
        {
            Orientation = Orientation.Horizontal,
            Spacing = 8,
            Children =
            {
                new Button { Content = "主要操作", Classes = { "primary" } },
                new Button { Content = "次要操作", Classes = { "secondary" } },
                new Button { Content = "跳过", Classes = { "ghost" } },
                new Button { Content = "删除", Classes = { "danger" } },
                new Button { Content = "更多", Classes = { "icon" } },
                new Button { Content = "小按钮", Classes = { "primary", "sm" } },
            },
        };

        var badges = new StackPanel
        {
            Orientation = Orientation.Horizontal,
            Spacing = 8,
        };
        foreach (var kind in Enum.GetValues<StatusKind>())
        {
            badges.Children.Add(new StatusBadge { Status = kind });
        }

        var typography = new StackPanel
        {
            Spacing = 2,
            Children =
            {
                new TextBlock { Text = "Display 空间标题", Classes = { "display" } },
                new TextBlock { Text = "Title 面板标题", Classes = { "title" } },
                new TextBlock { Text = "Body 正文示例文本：页面翻译流程说明。", Classes = { "body" } },
                new TextBlock { Text = "Label 字段名", Classes = { "label" } },
                new TextBlock { Text = "Meta 次要信息 · 12:03", Classes = { "meta" } },
                new TextBlock { Text = "023-017 / 1,204ms / 86%", Classes = { "data" } },
            },
        };

        var inputs = new StackPanel
        {
            Orientation = Orientation.Horizontal,
            Spacing = 8,
            Children =
            {
                new TextBox { Watermark = "搜索作品", Classes = { "search" }, Width = 160 },
                new TextBox { Text = "mono value", Classes = { "mono" }, Width = 140 },
                new TextBox { Text = "invalid", Classes = { "invalid" }, Width = 120 },
                new CheckBox { Content = "启用", IsChecked = true },
                new RadioButton { Content = "选中", IsChecked = true },
                new ToggleSwitch { IsChecked = true, OnContent = "开", OffContent = "关" },
            },
        };

        var last = new StackPanel
        {
            Orientation = Orientation.Horizontal,
            Spacing = 8,
            Children =
            {
                new SegmentedControl { Items = new[] { "页面", "成品", "分屏" }, SelectedIndex = 0 },
                new Chip { Text = "仅失败", Status = StatusKind.Failed, IsActive = true },
                new Kbd { Gesture = "Ctrl+K" },
                new ProgressBar { Value = 62, Maximum = 100, Width = 160 },
                new ComboBox { ItemsSource = new[] { "全部章节", "本章" }, SelectedIndex = 0, Classes = { "compact" } },
            },
        };

        var counts = new CountChips
        {
            Counts = new[]
            {
                new CountChipItem("总页数", 120),
                new CountChipItem("完成", 96, StatusKind.Done),
                new CountChipItem("失败", 3, StatusKind.Failed),
                new CountChipItem("过期", 2, StatusKind.Stale),
                new CountChipItem("待确认", 5, StatusKind.Blocked),
            },
        };

        var alerts = new StackPanel
        {
            Spacing = 8,
            Children =
            {
                new AlertBanner
                {
                    Severity = StatusKind.Blocked,
                    Title = "需要解除阻塞",
                    Message = "3 个页面等待人工确认后才能继续。",
                    ActionText = "查看",
                },
                new AlertBanner
                {
                    Severity = StatusKind.Stale,
                    Title = "上游内容已变更",
                    Message = "曾成功的译文因原图更新而过期，需重跑对应阶段。",
                    ActionText = "重跑",
                },
            },
        };

        var icons = new StackPanel
        {
            Orientation = Orientation.Horizontal,
            Spacing = 10,
        };
        foreach (var kind in new[]
                 {
                     NmIconKind.Add,
                     NmIconKind.Search,
                     NmIconKind.Settings,
                     NmIconKind.Check,
                     NmIconKind.Warning,
                     NmIconKind.Folder,
                     NmIconKind.Page,
                     NmIconKind.Play,
                     NmIconKind.Lock,
                     NmIconKind.Refresh,
                     NmIconKind.Export,
                     NmIconKind.Grid,
                 })
        {
            icons.Children.Add(new NmIcon { Kind = kind });
        }

        icons.Children.Add(new NmIcon { Kind = NmIconKind.Settings, Classes = { "active" } });
        icons.Children.Add(new NmIcon { Kind = NmIconKind.Grid, Classes = { "sm" } });

        var skeletons = new StackPanel
        {
            Orientation = Orientation.Horizontal,
            Spacing = 12,
            Children =
            {
                new Skeleton { Variant = SkeletonVariant.BookCard, Width = 120 },
                new Skeleton { Variant = SkeletonVariant.Row, Width = 140 },
                new Skeleton { Variant = SkeletonVariant.Panel, Width = 160 },
            },
        };

        var topBand = new TopBand
        {
            LeftContent = new TextBlock { Text = "Library   Studio   Console", Classes = { "label" } },
            CenterContent = new TextBlock { Text = "作品 › 第 3 章 › 第 23 页", Classes = { "meta" } },
            RightContent = new Kbd { Gesture = "Ctrl+K" },
        };

        var content = new Grid
        {
            RowDefinitions = new RowDefinitions("Auto,Auto,Auto,Auto,Auto,Auto,Auto,Auto,*,Auto"),
            Children =
            {
                topBand,
                Widget(buttons, 1),
                Widget(badges, 2),
                Widget(typography, 3),
                Widget(inputs, 4),
                Widget(last, 5),
                Widget(counts, 6),
                Widget(alerts, 7),
                Widget(skeletons, 8),
                Widget(icons, 9),
            },
        };

        return new Border
        {
            Classes = { "panel" },
            Padding = new Thickness(24),
            Child = content,
        };
    }

    private static Control Widget(Control control, int row)
    {
        Grid.SetRow(control, row);
        return control;
    }

    private static WriteableBitmap CaptureFrame(Window window)
    {
        Dispatcher.UIThread.RunJobs();
        return window.CaptureRenderedFrame() ?? throw new InvalidOperationException("CaptureRenderedFrame returned null");
    }

    private static void Save(WriteableBitmap frame, string path)
    {
        frame.Save(path);
        Assert.True(new FileInfo(path).Length > 2_000, $"{path} is suspiciously small");
    }

    private static WriteableBitmap Capture(Window window, string path)
    {
        Dispatcher.UIThread.RunJobs();
        var frame = window.CaptureRenderedFrame() ?? throw new InvalidOperationException("CaptureRenderedFrame returned null");
        frame.Save(path);
        Assert.True(new FileInfo(path).Length > 15_000, $"{path}: {new FileInfo(path).Length} bytes - blank/placeholder screenshot");
        return frame;
    }

    private static void AssertPixels(WriteableBitmap frame, string path, Color expected, string label)
    {
        using var bitmap = SKBitmap.Decode(path) ?? throw new InvalidOperationException($"{path}: PNG decode failed");
        Assert.Equal(frame.PixelSize.Width, bitmap.Width);
        Assert.Equal(frame.PixelSize.Height, bitmap.Height);
        var pixel = bitmap.GetPixel(3, 3);
        Assert.True(
            Math.Abs(pixel.Red - expected.R) <= 3 &&
            Math.Abs(pixel.Green - expected.G) <= 3 &&
            Math.Abs(pixel.Blue - expected.B) <= 3,
            $"{path}: corner pixel {pixel} is not the {label} ({expected})");
    }

    private static Color EdgePixel(WriteableBitmap frame)
    {
        using var bitmap = SKBitmap.Decode(SaveBytes(frame)) ?? throw new InvalidOperationException("PNG decode failed");
        var pixel = bitmap.GetPixel(3, 3);
        return Color.FromArgb(pixel.Alpha, pixel.Red, pixel.Green, pixel.Blue);
    }

    private static byte[] SaveBytes(WriteableBitmap frame)
    {
        using var stream = new MemoryStream();
        frame.Save(stream);
        return stream.ToArray();
    }

    private static int CountDistinctColors(WriteableBitmap frame)
    {
        using var bitmap = SKBitmap.Decode(SaveBytes(frame)) ?? throw new InvalidOperationException("PNG decode failed");
        var distinct = new HashSet<uint>();
        for (var y = 0; y < bitmap.Height; y += 7)
        {
            for (var x = 0; x < bitmap.Width; x += 7)
            {
                var pixel = bitmap.GetPixel(x, y);
                distinct.Add((uint)((pixel.Red << 16) | (pixel.Green << 8) | pixel.Blue));
            }
        }

        return distinct.Count;
    }

    private static int CountDifferentPixels(WriteableBitmap left, WriteableBitmap right)
    {
        using var leftBitmap = SKBitmap.Decode(SaveBytes(left)) ?? throw new InvalidOperationException("PNG decode failed");
        using var rightBitmap = SKBitmap.Decode(SaveBytes(right)) ?? throw new InvalidOperationException("PNG decode failed");
        Assert.Equal(leftBitmap.Width, rightBitmap.Width);
        Assert.Equal(leftBitmap.Height, rightBitmap.Height);
        var differing = 0;
        for (var y = 0; y < leftBitmap.Height; y += 5)
        {
            for (var x = 0; x < leftBitmap.Width; x += 5)
            {
                if (leftBitmap.GetPixel(x, y) != rightBitmap.GetPixel(x, y))
                {
                    differing++;
                }
            }
        }

        return differing;
    }

    private static string ResolveEvidenceDirectory()
    {
        var configured = Environment.GetEnvironmentVariable("NM_DS_EVIDENCE_DIR");
        return string.IsNullOrWhiteSpace(configured)
            ? Path.Combine(Path.GetTempPath(), "nm-designsystem-evidence")
            : configured;
    }
}



