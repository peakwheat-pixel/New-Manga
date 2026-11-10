using Avalonia;
using Avalonia.Controls;
using Avalonia.Headless.XUnit;
using Avalonia.Media;
using Avalonia.VisualTree;
using NewManga.App.Services;
using NewManga.App.ViewModels.Fluent;
using NewManga.App.Views.Fluent;
using NewManga.CoreClient;
using NewManga.DesignSystem.Controls;
using NewManga.DesignSystem.Theming;

namespace NewManga.App.Tests;

/// <summary>
/// FEA-14-SET-1 (AC1/AC3/AC4/AC5): the 字体 panel is a READ-ONLY projection.
///
/// The view model is constructed without an Avalonia <c>Application</c> (a fake
/// <see cref="ITypographySource"/> is injected), so the group enumeration/search and the
/// projection rows are testable in isolation. The panel must never write resources,
/// styles or AppData.
/// </summary>
public sealed class SettingsTypographyPanelTests
{
    private sealed class FakeSource : ITypographySource
    {
        private readonly TypographySnapshot _snapshot;

        public FakeSource(TypographySnapshot snapshot) => _snapshot = snapshot;

        public TypographySnapshot Read() => _snapshot;
    }

    private static TypographySnapshot InstalledSnapshot() => new(
        [
            TypographyResolver.Resolve("Nm.FontFamily.Ui", "Installed B, sans-serif", _ => true),
            TypographyResolver.Resolve("Nm.FontFamily.Data", "Installed B, serif", _ => true),
            TypographyResolver.Resolve(
                "Nm.FontFamily.Display", "Missing A, Installed B", family => family == "Installed B"),
        ],
        Available: true,
        UnavailableReason: null);

    private static SettingsViewModel NewViewModel(TypographySnapshot snapshot) =>
        new SettingsViewModel(null, null, null, new FakeSource(snapshot));

    [Fact]
    public void ThePanelProjectsThreeRowsWithoutAnAvaloniaApplication()
    {
        var viewModel = NewViewModel(InstalledSnapshot());

        Assert.True(viewModel.TypographyAvailable);
        Assert.Equal(3, viewModel.TypographyLines.Count);
        Assert.Equal("Nm.FontFamily.Ui", viewModel.TypographyLines[0].TokenKey);
        Assert.Equal("Installed B", viewModel.TypographyLines[0].ResolvedFamily);
        Assert.Contains("视觉主题", viewModel.TypographySourceNotice);
    }

    [Fact]
    public void AThemeWithMissingFontTokensIsUnavailableWithAnExplicitReason()
    {
        // R-010: a theme that only exposes two of the three font tokens must not be projected
        // as if it were complete (the old code silently dropped the row).
        var values = new Dictionary<string, string?>
        {
            ["Nm.FontFamily.Ui"] = "Installed B, sans-serif",
            ["Nm.FontFamily.Data"] = "Installed B, serif",
            ["Nm.FontFamily.Display"] = null,
            ["Nm.FontSize.Md"] = "14",
            ["Nm.FontSize.Xl"] = "24",
            ["Nm.LineHeight.Body"] = "1.6",
            ["Nm.LineHeight.Data"] = "1.5",
            ["Nm.LineHeight.Display"] = "1.4",
        };
        var source = new AvaloniaTypographySource(key => values.GetValueOrDefault(key));

        var snapshot = source.Read();

        Assert.False(snapshot.Available);
        Assert.Equal(2, snapshot.Lines.Count);
        Assert.Contains("Nm.FontFamily.Display", snapshot.UnavailableReason);
        Assert.Contains("不完整", snapshot.UnavailableReason);
    }

    [Fact]
    public void AnUnavailableThemeShowsAStablePlaceholder()
    {
        var viewModel = NewViewModel(new TypographySnapshot(
            Array.Empty<TypographyLine>(), false, "当前主题未初始化（缺少 Nm.FontFamily.* 资源）。"));

        Assert.False(viewModel.TypographyAvailable);
        Assert.Empty(viewModel.TypographyLines);
        Assert.Contains("未初始化", viewModel.TypographyUnavailableReason);
    }

    [Fact]
    public void TheTypographyGroupIsSearchableByChineseAndToken()
    {
        var viewModel = NewViewModel(InstalledSnapshot());

        viewModel.Search = "字体";
        Assert.Contains(SettingsGroupId.Typography, viewModel.VisibleGroups);

        viewModel.Search = "typography.ui";
        Assert.Contains(SettingsGroupId.Typography, viewModel.VisibleGroups);

        viewModel.Search = "zzz-no-match";
        Assert.DoesNotContain(SettingsGroupId.Typography, viewModel.VisibleGroups);
    }

    [Fact]
    public void ReadingTheProjectionDoesNotTouchApplicationResourcesOrStyles()
    {
        // AC3: there is no Application in this test; reading the projection must not
        // create one or mutate global state.
        var beforeApplication = Avalonia.Application.Current;
        var viewModel = NewViewModel(InstalledSnapshot());

        _ = viewModel.TypographyLines;
        _ = viewModel.TypographySourceNotice;

        Assert.Same(beforeApplication, Avalonia.Application.Current);
    }

    [Fact]
    public void ReadingTheProjectionLeavesTheRealAppDataDirectoryUntouched()
    {
        // AC4: the real %APPDATA%\NewManga must not receive writes from a read-only panel.
        var appData = Path.Combine(
            Environment.GetFolderPath(Environment.SpecialFolder.ApplicationData), "NewManga");
        var before = Fingerprint(appData);
        var viewModel = NewViewModel(InstalledSnapshot());
        _ = viewModel.TypographyLines;
        var after = Fingerprint(appData);
        Assert.Equal(before, after);
    }

    [AvaloniaFact]
    public void TheSourceProjectsTheRealThemeResources()
    {
        // R2-001: the production source path (real ResourceDictionary values: FontFamily +
        // double) must project three lines with the full stack and the scale/line-height values.
        var application = Application.Current!;
        using var theme = new DesignSystemThemeManager(application);
        Assert.True(theme.Initialize(AppearanceMode.Dark), theme.LastError);

        var snapshot = new AvaloniaTypographySource().Read();

        Assert.True(snapshot.Available);
        Assert.Equal(3, snapshot.Lines.Count);
        // Full stack, not just FontFamily.Name (the first family).
        Assert.Contains(",", snapshot.Lines[0].StackRaw);
        Assert.All(snapshot.Lines, line =>
        {
            Assert.NotNull(line.Scale);
            Assert.NotNull(line.LineHeight);
        });
        // R2-003: the face→size pairing follows ThemeTokenBaseline.LineHeightTiers:
        // Data ↔ Nm.FontSize.Sm (12), Display ↔ Nm.FontSize.Xxl (24).
        Assert.Equal(12, snapshot.Lines[1].Scale);
        Assert.Equal(24, snapshot.Lines[2].Scale);
    }

    [AvaloniaFact]
    public void TheSourceIsIndependentOfTheCurrentCulture()
    {
        // R2-002: numeric token values are formatted invariantly, so a comma-decimal locale
        // (de-DE) must not turn the line-height/scale projection into nulls.
        var application = Application.Current!;
        using var theme = new DesignSystemThemeManager(application);
        Assert.True(theme.Initialize(AppearanceMode.Dark), theme.LastError);
        var previous = System.Globalization.CultureInfo.CurrentCulture;
        try
        {
            System.Globalization.CultureInfo.CurrentCulture =
                new System.Globalization.CultureInfo("de-DE");

            var snapshot = new AvaloniaTypographySource().Read();

            Assert.True(snapshot.Available);
            Assert.All(snapshot.Lines, line =>
            {
                Assert.NotNull(line.Scale);
                Assert.NotNull(line.LineHeight);
            });
        }
        finally
        {
            System.Globalization.CultureInfo.CurrentCulture = previous;
        }
    }

    private static string Fingerprint(string directory)
    {
        if (!Directory.Exists(directory)) return "<absent>";
        var entries = Directory
            .EnumerateFileSystemEntries(directory, "*", SearchOption.AllDirectories)
            .OrderBy(item => item, StringComparer.Ordinal)
            .Select(item =>
            {
                var info = new FileInfo(item);
                if (!info.Exists) return $"{item}|<dir>";
                var hash = Convert.ToHexString(
                    System.Security.Cryptography.SHA256.HashData(File.ReadAllBytes(item)));
                return $"{item}|{info.Length}|{info.LastWriteTimeUtc.Ticks}|{hash}";
            });
        return string.Join("\n", entries);
    }
}

/// <summary>
/// FEA-14-SET-1 (AC1/AC3/AC5): the view-level render tests. They live in the same
/// frozen test file (the card's allowed_paths list one panel test file) so the
/// projection, the read-once contract and the zero-global-side-effect claim are all
/// exercised against a real <see cref="SettingsPageView"/> under the Avalonia headless harness.
/// </summary>
public sealed class SettingsTypographyRenderTests
{
    private sealed class FakeSource : ITypographySource
    {
        private readonly TypographySnapshot _snapshot;

        public FakeSource(TypographySnapshot snapshot) => _snapshot = snapshot;

        public int Reads { get; private set; }

        public TypographySnapshot Read()
        {
            Reads++;
            return _snapshot;
        }
    }

    private static TypographySnapshot Snapshot() => new(
        [
            TypographyResolver.Resolve(
                "Nm.FontFamily.Ui", "Missing A, Installed B", family => family == "Installed B",
                scale: 14, lineHeight: 1.6),
            TypographyResolver.Resolve(
                "Nm.FontFamily.Data", "Installed B", _ => true, scale: 14, lineHeight: 1.5),
            TypographyResolver.Resolve(
                "Nm.FontFamily.Display", "Installed B", _ => true, scale: 24, lineHeight: 1.4),
        ],
        Available: true,
        UnavailableReason: null);

    private static SettingsViewModel NewViewModel(TypographySnapshot snapshot) =>
        new SettingsViewModel(null, null, null, new FakeSource(snapshot));

    [AvaloniaFact]
    public void TheTypographyGroupRendersItsProjectionRows()
    {
        var viewModel = NewViewModel(Snapshot());
        viewModel.SelectedGroup = SettingsGroupId.Typography;
        var view = new SettingsPageView(viewModel);
        var window = new Window { Content = view, Width = 960, Height = 720 };
        window.Show();

        var texts = window.GetVisualDescendants()
            .OfType<TextBlock>()
            .Select(block => block.Text ?? string.Empty)
            .ToList();

        Assert.Contains(texts, text => text.Contains("Nm.FontFamily.Ui"));
        Assert.Contains(texts, text => text.Contains("Nm.FontFamily.Data"));
        Assert.Contains(texts, text => text.Contains("Nm.FontFamily.Display"));
        // The resolved family and the missing segment are explained in the row text.
        Assert.Contains(texts, text => text.Contains("Installed B"));
        Assert.Contains(texts, text => text.Contains("Missing A"));
        // AC1: scale/line-height are rendered, not swallowed by the projection.
        Assert.Contains(texts, text => text.Contains("缩放 14"));
        Assert.Contains(texts, text => text.Contains("行高 1.6"));
        // The panel states that family selection belongs to the visual theme.
        Assert.Contains(texts, text => text.Contains("视觉主题"));
        // R-015: the sample block says which face it previews.
        Assert.Contains(texts, text => text.Contains("样例预览（使用 Nm.FontFamily.Ui 的实际字体）"));
        // The three Chinese/Latin/number samples render, in the resolved family.
        Assert.Contains(texts, text => text == "永字体样式预览");
        Assert.Contains(texts, text => text == "The quick brown fox jumps over the lazy dog.");
        Assert.Contains(texts, text => text == "0123456789 1.25 × 1.6");
        var sample = window.GetVisualDescendants()
            .OfType<TextBlock>()
            .First(block => block.Text == "永字体样式预览");
        Assert.Equal("Installed B", sample.FontFamily?.Name);

        // R2-007: exactly three projection rows (each labelled with its token key).
        var projectionFields = window.GetVisualDescendants()
            .OfType<SettingsField>()
            .Where(field => ProjectionLabel(field) is not null)
            .ToList();
        Assert.Equal(3, projectionFields.Count);
        // R-006: every row is announced with its resolved family and is a Tab stop.
        Assert.All(projectionFields, field =>
        {
            var name = Avalonia.Automation.AutomationProperties.GetName(field);
            Assert.Contains("实际使用", name);
            Assert.True(field.Focusable, "the read-only projection row must participate in Tab navigation");
        });
    }

    [AvaloniaFact]
    public void RenderingTheTypographyGroupReadsTheSourceOncePerRender()
    {
        // R-012: one group render must probe the projection exactly once (the Avalonia source
        // walks the installed-font set) and the rows must stay consistent within that render.
        var source = new FakeSource(Snapshot());
        var viewModel = new SettingsViewModel(null, null, null, source);
        viewModel.SelectedGroup = SettingsGroupId.Typography;
        var view = new SettingsPageView(viewModel);
        var window = new Window { Content = view, Width = 960, Height = 720 };
        window.Show();
        // Page construction also renders on state transitions; the contract under test is
        // that ONE group switch/render probes once, not that page startup never renders.
        var baseline = source.Reads;
        Assert.True(baseline is >= 1 and <= 4, $"page startup read the projection {baseline} times (expected one read per render)");

        viewModel.SelectedGroup = SettingsGroupId.Appearance;
        viewModel.SelectedGroup = SettingsGroupId.Typography;

        Assert.Equal(baseline + 1, source.Reads);
    }

    [AvaloniaFact]
    public void RenderingTheTypographyGroupDoesNotMutateGlobalResourcesOrStyles()
    {
        // AC3: the real test Application's tokens live in MergedDictionaries, so counting
        // direct Resources entries (0 == 0) would be vacuous. Save the actual font-family
        // resource objects and the Styles sequence, render the group, then compare identity.
        var application = Application.Current!;
        using var theme = new DesignSystemThemeManager(application);
        Assert.True(theme.Initialize(AppearanceMode.Dark), theme.LastError);

        Assert.True(application.Resources.TryGetResource("Nm.FontFamily.Ui", null, out var uiBefore));
        Assert.True(application.Resources.TryGetResource("Nm.FontFamily.Data", null, out var dataBefore));
        Assert.True(application.Resources.TryGetResource("Nm.FontFamily.Display", null, out var displayBefore));
        var stylesBefore = application.Styles.ToList();

        var viewModel = NewViewModel(Snapshot());
        viewModel.SelectedGroup = SettingsGroupId.Typography;
        var view = new SettingsPageView(viewModel);
        var window = new Window { Content = view };
        window.Show();
        window.Measure(new Size(960, 720));

        Assert.Same(application, Application.Current);
        Assert.True(application.Resources.TryGetResource("Nm.FontFamily.Ui", null, out var uiAfter));
        Assert.True(application.Resources.TryGetResource("Nm.FontFamily.Data", null, out var dataAfter));
        Assert.True(application.Resources.TryGetResource("Nm.FontFamily.Display", null, out var displayAfter));
        Assert.Same(uiBefore, uiAfter);
        Assert.Same(dataBefore, dataAfter);
        Assert.Same(displayBefore, displayAfter);
        Assert.Equal(stylesBefore, application.Styles.ToList());

        // The sample font is local to the sample control: it carries the resolved family while
        // the global Nm.FontFamily.Ui resource still holds the theme's original object.
        var sample = window.GetVisualDescendants()
            .OfType<TextBlock>()
            .First(block => block.Text == "永字体样式预览");
        Assert.Equal("Installed B", sample.FontFamily?.Name);
        Assert.NotSame(uiBefore, sample.FontFamily);
    }

    [AvaloniaFact]
    public void AnUnavailableThemeRendersTheStablePlaceholderWithoutRows()
    {
        var viewModel = NewViewModel(new TypographySnapshot(
            Array.Empty<TypographyLine>(), false, "当前主题未初始化（缺少 Nm.FontFamily.* 资源）。"));
        viewModel.SelectedGroup = SettingsGroupId.Typography;
        var view = new SettingsPageView(viewModel);
        var window = new Window { Content = view, Width = 960, Height = 720 };
        window.Show();

        var texts = window.GetVisualDescendants().OfType<TextBlock>()
            .Select(block => block.Text ?? string.Empty)
            .ToList();
        Assert.Contains(texts, text => text.Contains("未初始化"));
        Assert.Equal(0, window.GetVisualDescendants()
            .OfType<SettingsField>()
            .Count(field => ProjectionLabel(field) is not null));
    }

    private static string? ProjectionLabel(SettingsField field) =>
        field.Children.OfType<TextBlock>()
            .FirstOrDefault()?.Text is { } label && label.StartsWith("Nm.FontFamily.", StringComparison.Ordinal)
            ? label
            : null;

    [AvaloniaFact]
    public void SearchingForTheTopicStillShowsTheProjectionRows()
    {
        var viewModel = NewViewModel(Snapshot());
        viewModel.Search = "字体";
        Assert.Contains(SettingsGroupId.Typography, viewModel.VisibleGroups);
        viewModel.SelectedGroup = SettingsGroupId.Typography;
        var view = new SettingsPageView(viewModel);
        var window = new Window { Content = view };
        window.Show();

        var visibleRows = window.GetVisualDescendants()
            .OfType<SettingsField>()
            .Where(field => field.IsVisible)
            .Count();
        // R-008: the group-level match must not hide every row inside the group.
        Assert.True(visibleRows > 0, "the typography rows must stay visible after a group match");
    }

    [AvaloniaFact]
    public void OpeningTheTypographyGroupIssuesNoHostCommands()
    {
        // L2-3 IPC replay: switching to / rendering the 字体 group must not call the host at all.
        // Page construction itself loads the settings lists, so those calls are recorded first and
        // the assertion only covers the group switch + render that follows.
        var host = new FakeHostController(new HostViewSnapshot(
            HostViewState.Ready, "ready", "fake", null, null,
            Array.Empty<BookSummary>(), 0, true, null));
        var viewModel = new SettingsViewModel(host, null, null, new FakeSource(Snapshot()));
        var view = new SettingsPageView(viewModel);
        var window = new Window { Content = view, Width = 960, Height = 720 };
        window.Show();
        var before = CommandCounts(host);

        viewModel.SelectedGroup = SettingsGroupId.Typography;
        window.Measure(new Size(960, 720));

        var after = CommandCounts(host);
        Assert.Equal(before.Count, after.Count);
        foreach (var (name, value) in before)
        {
            Assert.Equal(value, after[name]);
        }
    }

    private static Dictionary<string, int> CommandCounts(FakeHostController host) =>
        typeof(FakeHostController)
            .GetProperties()
            .Where(property => property.PropertyType == typeof(int) &&
                property.Name.EndsWith("Calls", StringComparison.Ordinal))
            .ToDictionary(property => property.Name, property => (int)property.GetValue(host)!);
}
