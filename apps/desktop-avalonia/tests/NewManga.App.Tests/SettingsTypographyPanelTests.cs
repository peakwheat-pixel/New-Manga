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
/// FEA-14-SET-1 (AC1/AC3/AC5/AC8): the view-level render tests. They live in the same
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
        // The panel states that family selection belongs to the visual theme.
        Assert.Contains(texts, text => text.Contains("视觉主题"));
        // R-015: the sample block says which face it previews.
        Assert.Contains(texts, text => text.Contains("样例预览（使用 Nm.FontFamily.Ui 的实际字体）"));
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
        var application = Application.Current;
        Assert.NotNull(application);
        var resourcesBefore = application!.Resources.Count;
        var styleKeysBefore = application.Styles
            .Select(style => style.GetHashCode())
            .ToList();

        var viewModel = NewViewModel(Snapshot());
        viewModel.SelectedGroup = SettingsGroupId.Typography;
        var view = new SettingsPageView(viewModel);
        var window = new Window { Content = view };
        window.Show();
        window.Measure(new Size(960, 720));

        Assert.Same(application, Application.Current);
        Assert.Equal(resourcesBefore, application.Resources.Count);
        Assert.Equal(styleKeysBefore, application.Styles.Select(style => style.GetHashCode()).ToList());
    }

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
